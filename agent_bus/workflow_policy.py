"""Static law for the Manager wake workflow: permissions, secrets, pins. No network.

The workflow is the one place a credential and a write token coexist in a run,
so its shape is checked mechanically rather than by reading it and nodding:

* nothing is granted by default (`permissions: {}` at the top);
* no job may hold ANY write permission except `issues: write`, and only a job
  that references no secret and runs no model;
* no job holds `contents`, `actions`, `pull-requests`, `deployments`,
  `packages`, `id-token`, `checks`, `statuses` or `security-events` write --
  nothing here can push, move a branch, merge or deploy;
* a secret is referenced by exactly one job, only as a `with:` input of the
  pinned Codex action, never in `run:` or `env:`; that job's permissions are
  all read, and its Codex step keeps `drop-sudo` and the read-only profile;
* every `uses:` is pinned to a 40-hex commit, and every checkout sets
  `persist-credentials: false`;
* the triggers are exactly a CREATED `issue_comment` and the COMPLETED
  `workflow_run` of this same workflow (by its own `name`) -- the no-model
  recovery path; nothing else, and never a schedule.

`python3 -m agent_bus.workflow_policy <path>` exits 0 when the file obeys, and
2 with one `BUS_WORKFLOW_POLICY` line per violation otherwise.

The file is read with the small block-YAML reader below -- the stdlib has none,
and a control plane that needs a dependency to check itself is not one. It reads
exactly the subset a workflow uses and halts on anything else.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from agent_bus import errors as E
from agent_bus.errors import BusError

CODEX_ACTION = "openai/codex-action"
PIN_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}$")
SECRET_RE = re.compile(r"\$\{\{\s*secrets\.")
WRITE_ALLOWED = frozenset({"issues"})
WORKFLOW_NAME = "Agent Bus Manager wake"
TRIGGERS = {"issue_comment": {"types": ["created"]},
            "workflow_run": {"workflows": [WORKFLOW_NAME], "types": ["completed"]}}


# ------------------------------------------------------------------ reading

class YamlError(ValueError):
    pass


def _strip_comment(text: str) -> str:
    out, quote = [], None
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "#" and (index == 0 or text[index - 1] in " \t"):
            break
        out.append(char)
    return "".join(out).rstrip()


def _scalar(text: str):
    text = text.strip()
    if text == "{}":
        return {}
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [_scalar(v) for v in inner.split(",")] if inner else []
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    return text


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _content(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#")


def load(text: str):
    if "\t" in text:
        raise YamlError("tabs are not allowed")
    lines = text.splitlines()
    value, index = _block(lines, 0, 0)
    while index < len(lines) and not _content(lines[index]):
        index += 1
    if index != len(lines):
        raise YamlError(f"line {index + 1}: unexpected content")
    return value


def _skip(lines, index):
    while index < len(lines) and not _content(lines[index]):
        index += 1
    return index


def _block(lines, index, indent):
    index = _skip(lines, index)
    if index >= len(lines) or _indent(lines[index]) < indent:
        return None, index
    if lines[index].strip().startswith("- ") or lines[index].strip() == "-":
        return _sequence(lines, index, _indent(lines[index]))
    return _mapping(lines, index, _indent(lines[index]))


def _sequence(lines, index, indent):
    out = []
    while True:
        index = _skip(lines, index)
        if index >= len(lines) or _indent(lines[index]) != indent \
                or not lines[index].strip().startswith("-"):
            return out, index
        rest = lines[index].strip()[1:].lstrip()
        if not rest:
            value, index = _block(lines, index + 1, indent + 1)
            out.append(value)
            continue
        if re.match(r"^[A-Za-z0-9_.-]+:(\s|$)", rest):
            # "- key: value": a mapping whose first key sits after the dash.
            inner = indent + 2
            lines = lines[:index] + [" " * inner + rest] + lines[index + 1:]
            value, index = _mapping(lines, index, inner)
            out.append(value)
            continue
        out.append(_scalar(_strip_comment(rest)))
        index += 1


def _mapping(lines, index, indent):
    out: dict = {}
    while True:
        index = _skip(lines, index)
        if index >= len(lines) or _indent(lines[index]) != indent:
            return out, index
        line = lines[index].strip()
        match = re.match(r"^([A-Za-z0-9_.-]+|'[^']*'|\"[^\"]*\"):(?:\s+(.*))?$", line)
        if not match:
            raise YamlError(f"line {index + 1}: not a mapping entry: {line!r}")
        key = _scalar(match.group(1))
        if key in out:
            raise YamlError(f"line {index + 1}: duplicate key {key!r}")
        rest = _strip_comment(match.group(2) or "")
        if rest in ("|", "|-", ">", ">-"):
            value, index = _block_scalar(lines, index + 1, indent, folded=rest.startswith(">"))
        elif rest:
            value, index = _scalar(rest), index + 1
        else:
            nxt = _skip(lines, index + 1)
            if nxt < len(lines) and _indent(lines[nxt]) == indent \
                    and lines[nxt].strip().startswith("-"):
                value, index = _sequence(lines, nxt, indent)
            else:
                value, index = _block(lines, index + 1, indent + 1)
        out[key] = value


def _block_scalar(lines, index, indent, folded):
    body = []
    while index < len(lines) and (not lines[index].strip() or _indent(lines[index]) > indent):
        body.append(lines[index])
        index += 1
    while body and not body[-1].strip():
        body.pop()
    width = min((_indent(line) for line in body if line.strip()), default=0)
    text = [line[width:] for line in body]
    return (" ".join(t.strip() for t in text) if folded else "\n".join(text)), index


# -------------------------------------------------------------------- law

def _walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def violations(workflow) -> list[str]:
    """Every broken rule, in a stable order. Empty means the file obeys."""
    out: list[str] = []
    if not isinstance(workflow, dict):
        return ["the workflow is not a mapping"]
    on = workflow.get("on")
    if on != TRIGGERS:
        out.append(f"the triggers must be exactly {TRIGGERS!r}, got {on!r}")
    if workflow.get("name") != WORKFLOW_NAME:
        out.append(f"the workflow must be named {WORKFLOW_NAME!r}: its recovery trigger "
                   "names itself and nothing else")
    if workflow.get("permissions") != {}:
        out.append("top-level permissions must be {} (nothing by default)")
    if any(SECRET_RE.search(s) for s in _walk_strings(workflow.get("env", {}))):
        out.append("workflow-level env references a secret")
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        return out + ["the workflow has no jobs"]

    secret_jobs = []
    for name, job in jobs.items():
        if not isinstance(job, dict):
            out.append(f"job {name} is not a mapping")
            continue
        perms = job.get("permissions")
        if not isinstance(perms, dict):
            out.append(f"job {name} must state its permissions explicitly")
            perms = {}
        writes = sorted(k for k, v in perms.items() if v == "write")
        for key, value in perms.items():
            if value not in ("read", "write", "none"):
                out.append(f"job {name} permission {key}={value!r} is not read/write/none")
        for key in writes:
            if key not in WRITE_ALLOWED:
                out.append(f"job {name} holds {key}: write")
        steps = job.get("steps") or []
        if not isinstance(steps, list):
            out.append(f"job {name} steps are not a list")
            steps = []
        job_secret = False
        if any(SECRET_RE.search(s) for s in _walk_strings(job.get("env", {}))):
            out.append(f"job {name} env references a secret")
            job_secret = True
        for index, step in enumerate(steps):
            where = f"job {name} step {index + 1}"
            if not isinstance(step, dict):
                out.append(f"{where} is not a mapping")
                continue
            uses = step.get("uses")
            if uses is not None and not PIN_RE.match(str(uses)):
                out.append(f"{where} uses {uses!r}, not pinned to a 40-hex commit")
            if isinstance(uses, str) and uses.startswith("actions/checkout@"):
                if (step.get("with") or {}).get("persist-credentials") != "false":
                    out.append(f"{where} checkout must set persist-credentials: false")
            for key in ("run", "env"):
                if any(SECRET_RE.search(s) for s in _walk_strings(step.get(key, ""))):
                    out.append(f"{where} references a secret in {key}")
                    job_secret = True
            if any(SECRET_RE.search(s) for s in _walk_strings(step.get("with", {}))):
                job_secret = True
                if not (isinstance(uses, str) and uses.split("@")[0] == CODEX_ACTION):
                    out.append(f"{where} passes a secret to {uses!r}, not the Codex action")
                inputs = step.get("with") or {}
                if inputs.get("safety-strategy") != "drop-sudo":
                    out.append(f"{where} Codex step must keep safety-strategy: drop-sudo")
                if inputs.get("permission-profile") != ":read-only":
                    out.append(f"{where} Codex step must keep the read-only profile")
        if job_secret:
            secret_jobs.append(name)
            if writes:
                out.append(f"job {name} holds a secret AND {', '.join(writes)}: write")
    if len(secret_jobs) > 1:
        out.append(f"secrets are referenced by more than one job: {secret_jobs}")
    return out


def check_text(text: str) -> list[str]:
    try:
        return violations(load(text))
    except YamlError as exc:
        return [f"unreadable workflow: {exc}"]


def require(text: str) -> None:
    problems = check_text(text)
    if problems:
        raise BusError(E.WORKFLOW_POLICY, "; ".join(problems))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python3 -m agent_bus.workflow_policy <workflow.yml>", file=sys.stderr)
        return 2
    problems = check_text(Path(argv[0]).read_text(encoding="utf-8"))
    for problem in problems:
        print(f"{E.WORKFLOW_POLICY}: {problem}")
    return 2 if problems else 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
