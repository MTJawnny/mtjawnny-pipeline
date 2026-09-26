"""Provider-neutral local Worker execution, with one narrow failover rule.

The bus does not care which model does a unit. It cares that the unit is
authorized, that the checkout is the one the wave named, and that git afterwards
agrees with what was authorized. So a local Worker provider is only three things:

* an `argv` for one non-interactive invocation of an already-authenticated CLI;
* a `classify` of that invocation's result into OK, CAPACITY or FAILED;
* its OWN session namespace, which no other provider may resume.

Two providers are defined: `ClaudeProvider` (`claude -p`) and `CodexProvider`
(`codex exec`, workspace-write sandbox). Neither needs a repository secret.

`ProviderFailoverTransport` tries them in an operator-configured order and moves
to the next provider for the SAME unit only when all of this holds:

1. the provider's result is a classified quota / 429 / capacity failure, read
   from a structured shape in stdout or stderr -- never from prose;
2. an independent git measurement proves the attempt left HEAD, the branch and
   the working tree exactly as they were, clean;
3. a live re-read of the authority proves the command is still the selected one.

Anything else -- a success, an unclassified error, a launch failure, a timeout,
a commit, a dirty tree, moved authority -- ends the dispatch with a stable code
and never reaches another provider. Each provider is invoked at most once per
unit, so "every provider is out of capacity" is one bounded failure, not a loop.

Provider ORDER is operator configuration, resolved from a flag, the environment
or a file outside the checkout, exactly like the speaker set. It is never read
from Issue #1, a transport PR, the repository, or model output.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Mapping, Sequence

from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.issue import AuthorityError
from agent_bus.preflight import Checkout, inspect
from agent_bus.protocol import Envelope
from agent_bus.shell import Completed, Runner
from agent_bus.transport import SESSION_NAMESPACE, Dispatch, LocalClaudeTransport, worker_brief
from agent_bus.wave import WavePlan

# ------------------------------------------------------------------ classification
OK = "OK"
CAPACITY = "CAPACITY"
FAILED = "FAILED"


@dataclass(frozen=True)
class Classification:
    status: str
    evidence: tuple[str, ...] = ()


def _json_object(text: str) -> dict | None:
    """The whole of `text` as ONE JSON object, or None. Never a substring."""
    try:
        value = json.loads(text)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def _json_lines(text: str) -> list[dict]:
    """Every line of `text` that is by itself one JSON object. Prose lines are not evidence."""
    return [obj for obj in (_json_object(line.strip()) for line in text.splitlines()
                            if line.strip().startswith("{")) if obj is not None]


# Claude Code, `--output-format json`: a terminal `result` object. A capacity
# failure is an `is_error` result carrying either the API status, the CLI's own
# machine-shaped usage-limit marker, or the API's typed error object.
_CLAUDE_LIMIT = re.compile(r"^Claude AI usage limit reached\|\d+$")
_CLAUDE_API_ERROR = re.compile(r"^API Error: (?P<status>\d{3}) (?P<body>\{.*\})$")
_CLAUDE_CAPACITY_STATUS = {429: "rate_limit_error", 529: "overloaded_error"}


def _claude_api_error(text: str) -> str | None:
    match = _CLAUDE_API_ERROR.match(text.strip())
    if not match:
        return None
    status = int(match["status"])
    body = _json_object(match["body"])
    error = body.get("error") if body else None
    if (status in _CLAUDE_CAPACITY_STATUS and isinstance(error, dict)
            and error.get("type") == _CLAUDE_CAPACITY_STATUS[status]):
        return f"API Error {status} {error['type']}"
    return None


def classify_claude(result: Completed) -> Classification:
    if result.returncode == 0:
        return Classification(OK)
    evidence: list[str] = []
    payload = _json_object(result.stdout.strip())
    if payload and payload.get("type") == "result" and payload.get("is_error") is True:
        status = payload.get("api_error_status")
        if type(status) is int and status in _CLAUDE_CAPACITY_STATUS:
            evidence.append(f"stdout result api_error_status {status}")
        text = payload.get("result")
        if isinstance(text, str):
            if _CLAUDE_LIMIT.match(text.strip()):
                evidence.append("stdout result usage-limit marker")
            api = _claude_api_error(text)
            if api:
                evidence.append(f"stdout result {api}")
    for line in result.stderr.splitlines():
        if _CLAUDE_LIMIT.match(line.strip()):
            evidence.append("stderr usage-limit marker")
        api = _claude_api_error(line)
        if api:
            evidence.append(f"stderr {api}")
    return Classification(CAPACITY if evidence else FAILED, tuple(evidence))


# Codex, `codex exec --json`: JSONL events. A capacity failure is an `error` or
# `turn.failed` EVENT whose message is one of the CLI's fixed capacity messages,
# anchored at the start. The same words inside an agent message are not an event.
_CODEX_CAPACITY = (
    re.compile(r"^You've hit your usage limit\."),
    re.compile(r"^Quota exceeded\. Check your plan and billing details\.$"),
    re.compile(r"^exceeded retry limit, last status: 429 Too Many Requests\b"),
    re.compile(r"^Selected model is at capacity\."),
)


def _codex_error_message(event: dict) -> str | None:
    if event.get("type") == "error":
        message = event.get("message")
    elif event.get("type") == "turn.failed" and isinstance(event.get("error"), dict):
        message = event["error"].get("message")
    else:
        return None
    return message if isinstance(message, str) else None


def classify_codex(result: Completed) -> Classification:
    if result.returncode == 0:
        return Classification(OK)
    evidence: list[str] = []
    for stream, text in (("stdout", result.stdout), ("stderr", result.stderr)):
        for event in _json_lines(text):
            message = _codex_error_message(event)
            if message and any(p.match(message.strip()) for p in _CODEX_CAPACITY):
                evidence.append(f"{stream} {event['type']} event: {message.strip()[:120]}")
    return Classification(CAPACITY if evidence else FAILED, tuple(evidence))


def codex_thread_id(stdout: str) -> str | None:
    """The session id Codex assigned, from its own `thread.started` event."""
    for event in _json_lines(stdout):
        if event.get("type") == "thread.started" and isinstance(event.get("thread_id"), str):
            return event["thread_id"]
    return None


# ------------------------------------------------------------------------ sessions
@dataclass(frozen=True)
class SessionRef:
    """A session, and the provider that owns it. The owner is part of the identity."""

    provider: str
    id: str | None      # None: a fresh session whose id the provider will assign
    resumed: bool

    @property
    def label(self) -> str:
        return f"{self.provider}:{self.id or 'new'}"


def _own(provider: str, session: SessionRef) -> None:
    if session.provider != provider:
        raise BusError(E.PROVIDER_SESSION_MISMATCH,
                       f"{provider} was handed a {session.provider} session "
                       f"({session.id}); a session is resumed only by the provider "
                       "that opened it")


class ClaudeProvider:
    """The operator's authenticated Claude Code CLI, run headless."""

    name = "claude"
    # The pre-existing namespace, kept, so a Claude-only bus keeps its session ids.
    namespace = SESSION_NAMESPACE

    def __init__(self, repo: str, executable: str = "claude", model: str | None = None,
                 permission_mode: str = "acceptEdits") -> None:
        self.repo = repo
        self.executable = executable
        self._cli = LocalClaudeTransport(repo, executable=executable, model=model,
                                         permission_mode=permission_mode)

    def fresh_session(self, wave: str, ordinal: int) -> SessionRef:
        # A second fresh session for the same wave gets a new id rather than
        # colliding with one an earlier (failed) attempt may have created.
        key = wave if ordinal == 0 else f"{wave}#{ordinal}"
        return SessionRef(self.name, str(uuid.uuid5(self.namespace, key)), False)

    def durable_session(self, wave: str) -> SessionRef | None:
        return SessionRef(self.name, str(uuid.uuid5(self.namespace, wave)), True)

    def argv(self, prompt: str, session: SessionRef) -> tuple[str, ...]:
        _own(self.name, session)
        return self._cli.argv(prompt, session.id, session.resumed)

    def opened(self, session: SessionRef, result: Completed) -> SessionRef | None:
        return SessionRef(self.name, session.id, True)

    classify = staticmethod(classify_claude)


class CodexProvider:
    """The operator's authenticated Codex CLI: `codex exec`, workspace-write only."""

    name = "codex"
    sandbox = "workspace-write"

    def __init__(self, repo: str, executable: str = "codex", model: str | None = None) -> None:
        self.repo = repo
        self.executable = executable
        self.model = model

    def fresh_session(self, wave: str, ordinal: int) -> SessionRef:
        return SessionRef(self.name, None, False)

    def durable_session(self, wave: str) -> SessionRef | None:
        # Codex assigns its own ids; only one recorded from its own output can be
        # resumed. Nothing durable names one, so a new process starts fresh.
        return None

    def argv(self, prompt: str, session: SessionRef) -> tuple[str, ...]:
        _own(self.name, session)
        argv = [self.executable, "exec", "--json", "--sandbox", self.sandbox,
                "--cd", self.repo]
        if self.model:
            argv += ["--model", self.model]
        if session.resumed:
            if not session.id:
                raise BusError(E.PROVIDER_SESSION_MISMATCH,
                               "a codex resume needs the thread id codex assigned")
            argv += ["resume", session.id]
        argv.append(prompt)
        return tuple(argv)

    def opened(self, session: SessionRef, result: Completed) -> SessionRef | None:
        thread = codex_thread_id(result.stdout) or session.id
        return SessionRef(self.name, thread, True) if thread else None

    classify = staticmethod(classify_codex)


PROVIDERS = {"claude": ClaudeProvider, "codex": CodexProvider}
DEFAULT_EXECUTABLES = {"claude": "claude", "codex": "codex"}


@dataclass
class SessionBook:
    """Sessions opened in this process, keyed by (provider, wave). Never shared."""

    opened: dict[tuple[str, str], SessionRef] = field(default_factory=dict)
    fresh_count: dict[tuple[str, str], int] = field(default_factory=dict)

    def resumable(self, provider: str, wave: str) -> SessionRef | None:
        return self.opened.get((provider, wave))

    def any_opened(self, wave: str) -> bool:
        return any(w == wave for _, w in self.opened)

    def next_fresh(self, provider: str, wave: str, commit: bool = True) -> int:
        ordinal = self.fresh_count.get((provider, wave), 0)
        if commit:
            self.fresh_count[(provider, wave)] = ordinal + 1
        return ordinal

    def record(self, wave: str, session: SessionRef) -> None:
        self.opened[(session.provider, wave)] = session


# -------------------------------------------------------------------- provider order
PROVIDER_ENV_VAR = "MTJ_AGENT_BUS_PROVIDERS"
PROVIDER_CONFIG_ENV_VAR = "MTJ_AGENT_BUS_PROVIDER_CONFIG"
DEFAULT_PROVIDER_CONFIG = Path("~/.config/mtj-agent-bus/providers.json")
DEFAULT_ORDER = ("claude", "codex")


@dataclass(frozen=True)
class ProviderOrder:
    order: tuple[str, ...]
    source: str

    def as_dict(self) -> dict:
        return {"order": list(self.order), "source": self.source}


def parse_order(value: str | Sequence[str], source: str) -> ProviderOrder:
    """`claude,codex`, `codex,claude`, `claude` or `codex`. Anything else is refused."""
    items = value.split(",") if isinstance(value, str) else list(value)
    if not all(isinstance(item, str) for item in items):
        raise BusError(E.PROVIDER_CONFIG_INVALID, f"{source}: provider names must be strings")
    names = [item.strip().lower() for item in items]
    if not names or any(not n for n in names):
        raise BusError(E.PROVIDER_CONFIG_INVALID, f"{source}: empty provider name in {value!r}")
    unknown = [n for n in names if n not in PROVIDERS]
    if unknown:
        raise BusError(E.PROVIDER_CONFIG_INVALID,
                       f"{source}: unknown provider(s) {', '.join(unknown)}; "
                       f"known: {', '.join(sorted(PROVIDERS))}")
    if len(set(names)) != len(names):
        raise BusError(E.PROVIDER_CONFIG_INVALID,
                       f"{source}: a provider may appear once in the order, got {value!r}")
    return ProviderOrder(tuple(names), source)


def _inside(path: Path, root: str | None) -> bool:
    if not root:
        return False
    try:
        path.resolve().relative_to(Path(root).expanduser().resolve())
    except ValueError:
        return False
    return True


def resolve_order(flag: str | None = None, environ: Mapping[str, str] | None = None,
                  path: Path | None = None, repo_path: str | None = None) -> ProviderOrder:
    """First configured source wins: flag, environment, operator file, default.

    The file must live OUTSIDE the checkout: a unit can edit the checkout, and a
    unit must never be able to choose which model runs the next unit.
    """
    environ = os.environ if environ is None else environ
    if flag:
        return parse_order(flag, "--providers")
    if environ.get(PROVIDER_ENV_VAR, "").strip():
        return parse_order(environ[PROVIDER_ENV_VAR], PROVIDER_ENV_VAR)
    if path is None:
        configured = environ.get(PROVIDER_CONFIG_ENV_VAR)
        path = Path(configured) if configured else DEFAULT_PROVIDER_CONFIG
    path = path.expanduser()
    if _inside(path, repo_path):
        raise BusError(E.PROVIDER_CONFIG_INVALID,
                       f"{path} is inside the checkout {repo_path}; provider order is "
                       "operator configuration and must live outside the repository")
    if path.is_file():
        payload = _json_object(path.read_text(encoding="utf-8"))
        if payload is None or not isinstance(payload.get("order"), list):
            raise BusError(E.PROVIDER_CONFIG_INVALID,
                           f'{path} must be a JSON object with an "order" list')
        return parse_order(payload["order"], str(path))
    return ProviderOrder(DEFAULT_ORDER, "default")


def build_providers(order: ProviderOrder, repo: str,
                    executables: Mapping[str, str] | None = None) -> list:
    executables = dict(DEFAULT_EXECUTABLES, **(executables or {}))
    return [PROVIDERS[name](repo, executable=executables[name]) for name in order.order]


# ------------------------------------------------------------------ failover proof
AuthorityProbe = Callable[[Envelope], Sequence[str]]


def live_authority_probe(observe: Callable) -> AuthorityProbe:
    """Re-read Issue #1 and the transport; name every way the command went stale.

    `observe` is `Supervisor.observe`: the same reader every other decision uses,
    so the failover gate cannot hold a looser idea of "current" than dispatch did.
    """
    def probe(envelope: Envelope) -> list[str]:
        observation = observe()
        authority = observation.authority
        problems: list[str] = []
        if (authority.checkpoint != envelope.authority["checkpoint"]
                or authority.task != envelope.authority["task"]):
            problems.append(
                f"authority moved: latest checkpoint {authority.checkpoint} selects task "
                f"{authority.task}, the command cites checkpoint "
                f"{envelope.authority['checkpoint']} task {envelope.authority['task']}")
        if authority.accepted_head != envelope.base:
            problems.append(f"accepted head moved to {authority.accepted_head}, "
                            f"the command cites {envelope.base}")
        wave = observation.state.waves.get(envelope.wave)
        if wave is None or wave.aborted:
            problems.append(f"wave {envelope.wave} is aborted or no longer on the bus")
        if envelope.wave in observation.state.superseded():
            problems.append(f"wave {envelope.wave} has been superseded")
        return problems
    return probe


def failover_problems(repo: str, before: Checkout, envelope: Envelope,
                      probe: AuthorityProbe | None, run: Runner) -> list[str]:
    """Everything that forbids handing this checkout to another provider. Empty = safe."""
    problems: list[str] = []
    if before.dirty:
        problems.append(f"the tree was already dirty before dispatch ({len(before.dirty)} path(s))")
    try:
        after = inspect(repo, run)
    except BusError as exc:
        problems.append(f"git could not be re-measured: {exc}")
    else:
        if after.head != before.head:
            problems.append(f"HEAD moved {before.head} -> {after.head}: "
                            "the failed provider left a commit")
        if after.branch != before.branch:
            problems.append(f"branch changed {before.branch} -> {after.branch}")
        if after.dirty:
            problems.append(f"the failed provider left {len(after.dirty)} uncommitted "
                            "path(s): " + "; ".join(after.dirty[:5]))
    if probe is None:
        problems.append("no live authority probe: freshness cannot be proven")
    else:
        try:
            problems.extend(probe(envelope))
        except (BusError, AuthorityError) as exc:
            problems.append(f"authority could not be re-resolved: {exc}")
    return problems


# ----------------------------------------------------------------------- transport
class ProviderFailoverTransport:
    """The provider-neutral local transport. Same `dispatch` as every transport."""

    def __init__(self, repo: str, providers: Sequence, authority_probe: AuthorityProbe | None = None,
                 run: Runner | None = None, book: SessionBook | None = None) -> None:
        if not providers:
            raise BusError(E.PROVIDER_CONFIG_INVALID, "at least one provider is required")
        names = [p.name for p in providers]
        if len(set(names)) != len(names):
            raise BusError(E.PROVIDER_CONFIG_INVALID, f"duplicate provider in {names}")
        self.repo = repo
        self.providers = tuple(providers)
        self.authority_probe = authority_probe
        self.run = run or Runner()
        self.book = book or SessionBook()

    @property
    def name(self) -> str:
        return "local-provider:" + ",".join(p.name for p in self.providers)

    @property
    def order(self) -> tuple[str, ...]:
        return tuple(p.name for p in self.providers)

    def _session(self, provider, wave: str, resumed: bool, first: bool,
                 commit: bool = True) -> SessionRef:
        """This provider's own session for the wave -- never another provider's."""
        own = self.book.resumable(provider.name, wave)
        if own is not None and resumed:
            return own
        if own is None and resumed and first and not self.book.any_opened(wave):
            durable = provider.durable_session(wave)
            if durable is not None:
                return durable
        return provider.fresh_session(wave, self.book.next_fresh(provider.name, wave, commit))

    def dispatch(self, envelope: Envelope, plan: WavePlan, remaining: Sequence[str],
                 resumed: bool = False, dry_run: bool = True,
                 queue: Sequence[str] = ()) -> Dispatch:
        prompt = worker_brief(envelope, plan, remaining, self.repo, queue)
        wave = envelope.wave
        if dry_run:
            provider = self.providers[0]
            session = self._session(provider, wave, resumed, first=True, commit=False)
            return Dispatch(provider.argv(prompt, session), prompt, session.label,
                            session.resumed, executed=False, provider=provider.name)

        before = inspect(self.repo, self.run)
        attempts: list[dict] = []
        for index, provider in enumerate(self.providers):
            if index:
                problems = failover_problems(self.repo, before, envelope,
                                             self.authority_probe, self.run)
                if problems:
                    raise BusError(
                        E.FAILOVER_REFUSED,
                        f"{attempts[-1]['provider']} reported a classified capacity failure "
                        f"but {provider.name} may not take the unit: " + "; ".join(problems))
            session = self._session(provider, wave, resumed, first=index == 0)
            argv = provider.argv(prompt, session)
            # A launch failure or timeout raises here and is NOT a capacity failure:
            # nothing classified it, so nothing fails over.
            result = self.run(argv, timeout=None)
            verdict = provider.classify(result)
            if verdict.status == OK:
                opened = provider.opened(session, result)
                if opened is not None:
                    self.book.record(wave, opened)
                return Dispatch(argv, prompt, session.label, session.resumed, executed=True,
                                result=result, provider=provider.name,
                                attempts=tuple(attempts))
            if verdict.status != CAPACITY:
                raise BusError(E.TRANSPORT_FAILED,
                               f"{provider.executable} exited {result.returncode}: "
                               f"{result.stderr.strip()[:400]}")
            attempts.append({"provider": provider.name, "session": session.label,
                             "returncode": result.returncode,
                             "classified": list(verdict.evidence)})
        raise BusError(
            E.PROVIDERS_EXHAUSTED,
            "every enabled provider reported a classified quota/capacity failure, each "
            "invoked once: " + "; ".join(f"{a['provider']} ({', '.join(a['classified'])})"
                                          for a in attempts))
