"""Captain-rooted goal plans: the only source of a successor, a repair budget, or a check.

R4 ended every ACCEPT with `a = 0`, hard-coded the repair budget in Worker code,
and accepted on the bus selftest alone. So routine continuation needed a human
`K`, the budget was policy nobody ratified, and a wave could be accepted without
its own validation. All three are the same gap: the publisher had no durable,
Captain-rooted statement of what the goal is. This module is that statement.

**A goal plan** is an Issue #1 comment by a trusted speaker that OPENS with one
fenced ` ```mtj-goal ` JSON block (`FENCE`). It names the Captain decision it
executes, and binds, explicitly and exactly:

* `repair_budget` -- how many consecutive autonomous repairs one planned wave
  may take before REPAIR is recorded as CAPTAIN;
* `waves` -- each planned wave's task, its exact command (branch, units, review
  boundary, stop conditions), its required `validation` checks, and `next`: the
  ONE wave an ACCEPT of it continues to, or null;
* `terminal` -- the one wave whose `next` is null. ACCEPT of it selects nothing.

**A command binds to a plan** only by naming it -- `body.goal = {plan, digest}`
-- AND by being exactly the planned wave: same wave id, same task, same command.
A command that differs in anything, a plan that was edited (the digest), a plan
whose Captain decision is not an earlier trusted Issue #1 comment, or a plan that
does not parse, binds nothing. Unbound is not an error to guess around: the
transition law records it as CAPTAIN (`transition.PLAN_UNBOUND`).

**No other text can create an edge.** The successor is read from the bound plan
entry's `next` and nothing else: not the model (it has no field for it), not the
Worker (`body.next` must be NONE), not a queued task's prose, not a task id that
some comment mentions. The successor command is rendered here, from the plan.

**Validation evidence** is what an independent runner measured, not what the
Worker claims: `run_checks` executes the bound wave's checks in a checkout of the
result head and records the head git reports and every exit code. The transition
law refuses an ACCEPT unless that evidence is for this plan, this wave and the
result head, names exactly the planned checks in order, and every one exited 0.

    python3 -m agent_bus.goal check-plan FILE     lint a plan before posting it
    python3 -m agent_bus.goal run-checks ...      the evidence runner
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from agent_bus import SCHEMA
from agent_bus import errors as E
from agent_bus.errors import BusError
from agent_bus.protocol import SHA_RE, UNIT_ID_RE, WAVE_RE, Envelope, _validate_body
from agent_bus.wave import plan_from_command

FENCE = "mtj-goal"
PLAN_SCHEMA = "mtj-goal/1"
PLAN_KEYS = ("schema", "goal", "captain_decision", "repair_budget", "terminal", "waves")
WAVE_KEYS = ("wave", "task", "command", "validation", "next")
CHECK_KEYS = ("id", "argv")
# What a planned command fixes. `candidate_base`, `note` and `goal` are how a
# command is ISSUED, not what it authorizes, so they are not part of the plan.
TEMPLATE_REQUIRED = ("branch", "review_boundary", "units")
TEMPLATE_OPTIONAL = ("stop_conditions",)
REF_KEYS = ("plan", "digest")

_OPEN = re.compile(r"\A```" + FENCE + r"[ \t]*\r?\n(?P<payload>.*?)\r?\n```[ \t]*(?:\r?\n|\Z)",
                   re.DOTALL)
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _invalid(detail: str) -> BusError:
    return BusError(E.GOAL_PLAN_INVALID, detail)


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise _invalid(f"key {key!r} appears twice")
        out[key] = value
    return out


def _exact(mapping: Any, keys: Sequence[str], where: str, optional=()) -> dict:
    if not isinstance(mapping, dict):
        raise _invalid(f"{where} must be an object")
    missing = [k for k in keys if k not in mapping]
    extra = sorted(set(mapping) - set(keys) - set(optional))
    if missing or extra:
        raise _invalid(f"{where}: missing {missing}, unknown {extra}")
    return mapping


def _positive(value: Any, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise _invalid(f"{where} must be a positive integer")
    return value


# ------------------------------------------------------------------- the plan

@dataclass(frozen=True)
class Check:
    id: str
    argv: tuple[str, ...]


@dataclass(frozen=True)
class PlannedWave:
    wave: str
    task: int
    command: Mapping[str, Any]  # the exact command template
    checks: tuple[Check, ...]
    next: str | None


@dataclass(frozen=True)
class GoalPlan:
    goal: str
    captain_decision: int
    repair_budget: int
    terminal: str
    waves: tuple[PlannedWave, ...]

    def wave(self, wave_id: str | None) -> PlannedWave | None:
        return next((w for w in self.waves if w.wave == wave_id), None)


def _check(raw: Any, where: str) -> Check:
    raw = _exact(raw, CHECK_KEYS, where)
    if not isinstance(raw["id"], str) or not UNIT_ID_RE.match(raw["id"]):
        raise _invalid(f"{where}.id is not an id")
    argv = raw["argv"]
    if not isinstance(argv, list) or not argv or any(
            not isinstance(a, str) or not a or "\x00" in a for a in argv):
        raise _invalid(f"{where}.argv must be a non-empty list of non-empty strings")
    return Check(raw["id"], tuple(argv))


def _template(raw: Any, wave: str, where: str) -> dict:
    raw = _exact(raw, TEMPLATE_REQUIRED, where, optional=TEMPLATE_OPTIONAL)
    try:
        _validate_body("WAVE_COMMAND", "MANAGER", raw)
        plan_from_command(wave, raw)
    except BusError as exc:
        raise _invalid(f"{where}: {exc}")
    return json.loads(json.dumps(raw))


def _planned(raw: Any, index: int) -> PlannedWave:
    where = f"waves[{index}]"
    raw = _exact(raw, WAVE_KEYS, where)
    wave = raw["wave"]
    if not isinstance(wave, str) or not WAVE_RE.match(wave):
        raise _invalid(f"{where}.wave is not a wave id")
    checks = raw["validation"]
    if not isinstance(checks, list) or not checks:
        raise _invalid(f"{where}.validation must name at least one required check")
    parsed = tuple(_check(c, f"{where}.validation[{i}]") for i, c in enumerate(checks))
    if len({c.id for c in parsed}) != len(parsed):
        raise _invalid(f"{where}.validation repeats a check id")
    nxt = raw["next"]
    if nxt is not None and (not isinstance(nxt, str) or not WAVE_RE.match(nxt)):
        raise _invalid(f"{where}.next must be a wave id or null")
    return PlannedWave(wave=wave, task=_positive(raw["task"], f"{where}.task"),
                       command=_template(raw["command"], wave, f"{where}.command"),
                       checks=parsed, next=nxt)


def plan_from_mapping(raw: Any) -> GoalPlan:
    raw = _exact(raw, PLAN_KEYS, "plan")
    if raw["schema"] != PLAN_SCHEMA:
        raise _invalid(f"schema {raw['schema']!r} is not {PLAN_SCHEMA!r}")
    if not isinstance(raw["goal"], str) or not WAVE_RE.match(raw["goal"]):
        raise _invalid("goal is not an id")
    budget = raw["repair_budget"]
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise _invalid("repair_budget must be an integer >= 0")
    if not isinstance(raw["waves"], list) or not raw["waves"]:
        raise _invalid("waves must be a non-empty list")
    waves = tuple(_planned(w, i) for i, w in enumerate(raw["waves"]))
    by_id = {w.wave: w for w in waves}
    if len(by_id) != len(waves):
        raise _invalid("a wave id appears twice")
    terminal = raw["terminal"]
    ends = [w.wave for w in waves if w.next is None]
    if ends != [terminal]:
        raise _invalid(f"terminal {terminal!r} must be the one wave whose next is null; "
                       f"null next: {ends}")
    for w in waves:  # every edge exists, and every path ends at the terminal
        seen, at = set(), w
        while at.next is not None:
            if at.next not in by_id:
                raise _invalid(f"wave {at.wave} continues to unplanned {at.next}")
            if at.wave in seen:
                raise _invalid(f"the edges from {w.wave} loop")
            seen.add(at.wave)
            at = by_id[at.next]
    return GoalPlan(goal=raw["goal"],
                    captain_decision=_positive(raw["captain_decision"], "captain_decision"),
                    repair_budget=budget, terminal=terminal, waves=waves)


def parse_plan(body: str) -> GoalPlan:
    """The plan a comment OPENS with, or GOAL_PLAN_INVALID. Nothing else is a plan."""
    match = _OPEN.match(body or "")
    if not match:
        raise _invalid(f"the comment does not open with a ```{FENCE} block")
    try:
        raw = json.loads(match.group("payload"), object_pairs_hook=_no_duplicates)
    except json.JSONDecodeError as exc:
        raise _invalid(f"not JSON: {exc.msg}")
    return plan_from_mapping(raw)


# ---------------------------------------------------------------- binding

def validate_ref(value: Any, where: str = "body.goal") -> None:
    """Shape of a command's `goal` reference. Whether it binds is `bind`'s question."""
    if not isinstance(value, dict) or set(value) != set(REF_KEYS):
        raise BusError(E.BAD_VALUE, f"{where} must be exactly {list(REF_KEYS)}")
    plan = value["plan"]
    if not isinstance(plan, int) or isinstance(plan, bool) or plan < 1:
        raise BusError(E.BAD_VALUE, f"{where}.plan must be a comment id")
    if not isinstance(value["digest"], str) or not _DIGEST_RE.match(value["digest"]):
        raise BusError(E.BAD_VALUE, f"{where}.digest must be a sha-256")


@dataclass(frozen=True)
class Binding:
    """A command that is exactly one wave of one live, unedited, Captain-rooted plan."""

    comment_id: int
    digest: str
    plan: GoalPlan
    entry: PlannedWave

    @property
    def successor(self) -> PlannedWave | None:
        return self.plan.wave(self.entry.next)

    def ref(self) -> dict:
        return {"plan": self.comment_id, "digest": self.digest}


def template_of(body: Mapping[str, Any]) -> dict:
    return {k: body[k] for k in TEMPLATE_REQUIRED + TEMPLATE_OPTIONAL if k in body}


def _same_task(entry: PlannedWave, origin: Envelope) -> bool:
    return entry.task == origin.authority["task"]


def bind(origin: Envelope | None, issue_comments: Sequence, trust) -> tuple[Binding | None, str]:
    """(binding, "") or (None, why not). Pure: live comments in, verdict out."""
    if origin is None:
        return None, "no origin command"
    ref = origin.body.get("goal")
    if ref is None:
        return None, f"command {origin.message_id} names no goal plan"
    by_id = {c.comment_id: c for c in issue_comments}
    comment = by_id.get(ref["plan"])
    if comment is None or not trust.trusts(comment.author):
        return None, f"goal plan {ref['plan']} is not a trusted Issue comment"
    if digest(comment.body) != ref["digest"]:
        return None, f"goal plan {ref['plan']} is not the plan the command bound (edited)"
    try:
        plan = parse_plan(comment.body)
    except BusError as exc:
        return None, f"goal plan {ref['plan']}: {exc.detail}"
    decision = by_id.get(plan.captain_decision)
    if decision is None or not trust.trusts(decision.author) \
            or decision.comment_id >= comment.comment_id:
        return None, (f"goal plan {ref['plan']} is not rooted in an earlier trusted Captain "
                      f"decision ({plan.captain_decision})")
    entry = plan.wave(origin.wave)
    if entry is None:
        return None, f"wave {origin.wave} is not in goal plan {ref['plan']}"
    if not _same_task(entry, origin):
        return None, f"wave {origin.wave} is planned for task {entry.task}, " \
                     f"commanded under {origin.authority['task']}"
    if _canon(template_of(origin.body)) != _canon(entry.command):
        return None, f"command {origin.message_id} is not the planned command of {origin.wave}"
    return Binding(comment.comment_id, ref["digest"], plan, entry), ""


def next_command(binding: Binding, *, message_id: str, issue: int, checkpoint: int,
                 head: str, created_at: str) -> Envelope:
    """The ONE command an ACCEPT of a nonterminal planned wave may issue: the plan's."""
    nxt = binding.successor
    if nxt is None:
        raise BusError(E.TRANSITION_REFUSED, f"wave {binding.entry.wave} is terminal")
    body = {**json.loads(json.dumps(nxt.command)), "goal": binding.ref()}
    return Envelope(schema=SCHEMA, message_id=message_id, actor="MANAGER",
                    kind="WAVE_COMMAND", wave=nxt.wave, parent=None,
                    authority={"issue": issue, "checkpoint": checkpoint, "task": nxt.task},
                    base=head, created_at=created_at, body=body)


# ---------------------------------------------------------------- evidence

EVIDENCE_KEYS = ("plan", "digest", "wave", "head", "checks")


@dataclass(frozen=True)
class Evidence:
    """What the independent runner measured: which plan, which head, which exits."""

    plan: int
    digest: str
    wave: str
    head: str
    checks: tuple[tuple[str, int], ...]

    def as_dict(self) -> dict:
        return {"plan": self.plan, "digest": self.digest, "wave": self.wave,
                "head": self.head, "checks": [{"id": i, "exit": x} for i, x in self.checks]}

    @property
    def red(self) -> list[str]:
        return [i for i, x in self.checks if x != 0]


def evidence_from_mapping(raw: Any) -> Evidence:
    def bad(detail: str) -> BusError:
        return BusError(E.BAD_VALUE, f"validation evidence: {detail}")
    if not isinstance(raw, dict) or set(raw) != set(EVIDENCE_KEYS):
        raise bad(f"must be exactly {list(EVIDENCE_KEYS)}")
    if not isinstance(raw["plan"], int) or isinstance(raw["plan"], bool) or raw["plan"] < 1:
        raise bad("plan must be a comment id")
    if not isinstance(raw["digest"], str) or not _DIGEST_RE.match(raw["digest"]):
        raise bad("digest must be a sha-256")
    if not isinstance(raw["wave"], str) or not WAVE_RE.match(raw["wave"]):
        raise bad("wave is not a wave id")
    if not isinstance(raw["head"], str) or not SHA_RE.match(raw["head"]):
        raise bad("head must be a 40-character sha")
    checks = raw["checks"]
    if not isinstance(checks, list):
        raise bad("checks must be a list")
    out = []
    for i, c in enumerate(checks):
        if not isinstance(c, dict) or set(c) != {"id", "exit"} \
                or not isinstance(c["id"], str) or not UNIT_ID_RE.match(c["id"]) \
                or not isinstance(c["exit"], int) or isinstance(c["exit"], bool):
            raise bad(f"checks[{i}] must be exactly an id and an integer exit")
        out.append((c["id"], c["exit"]))
    return Evidence(raw["plan"], raw["digest"], raw["wave"], raw["head"], tuple(out))


def check_evidence(binding: Binding, evidence: Evidence, result_head: str) -> None:
    """The evidence is for THIS plan, THIS wave, THIS head, and exactly its checks."""
    def refuse(detail: str) -> BusError:
        return BusError(E.TRANSITION_REFUSED, f"validation evidence {detail}")
    if (evidence.plan, evidence.digest) != (binding.comment_id, binding.digest):
        raise refuse(f"is for plan {evidence.plan}, the wave is bound to {binding.comment_id}")
    if evidence.wave != binding.entry.wave:
        raise refuse(f"is for wave {evidence.wave}, not {binding.entry.wave}")
    if evidence.head != result_head:
        raise refuse(f"was measured on {evidence.head}, not the result head {result_head}")
    planned = [c.id for c in binding.entry.checks]
    if [i for i, _ in evidence.checks] != planned:
        raise refuse(f"ran {[i for i, _ in evidence.checks]}, the plan requires {planned}")


def _execute(argv: Sequence[str], cwd: str) -> int:
    try:
        return subprocess.run(list(argv), cwd=cwd).returncode
    except OSError:
        return 127  # a check that cannot start is red, never skipped


def _git_head(checkout: str) -> str:
    out = subprocess.run(["git", "-C", checkout, "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def run_checks(binding: Binding, checkout: str,
               execute: Callable[[Sequence[str], str], int] = _execute,
               head_of: Callable[[str], str] = _git_head) -> Evidence:
    """Run every required check of the bound wave in `checkout`; measure its head."""
    head = head_of(checkout)
    if not SHA_RE.match(head):
        raise BusError(E.GIT_FAILED, f"cannot measure the head of {checkout}: {head!r}")
    checks = tuple((c.id, int(execute(c.argv, checkout))) for c in binding.entry.checks)
    return Evidence(binding.comment_id, binding.digest, binding.entry.wave, head, checks)


# ------------------------------------------------------------------- entry

def main(argv: Sequence[str] | None = None, run=None) -> int:
    parser = argparse.ArgumentParser(prog="agent_bus.goal",
                                     description="Captain goal plans and validation evidence")
    sub = parser.add_subparsers(dest="command", required=True)
    p_check = sub.add_parser("check-plan", help="parse a plan comment body from a file")
    p_check.add_argument("file")
    p_run = sub.add_parser("run-checks", help="run the bound wave's checks on a checkout")
    p_run.add_argument("--repo", required=True)
    p_run.add_argument("--issue", type=int, default=1)
    p_run.add_argument("--pr", type=int, required=True)
    p_run.add_argument("--trusted-author", required=True)
    p_run.add_argument("--comment-id", type=int, required=True)
    p_run.add_argument("--checkout", required=True)
    p_run.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "check-plan":
            with open(args.file, encoding="utf-8") as handle:
                plan = parse_plan(handle.read())
            print(json.dumps({"goal": plan.goal, "terminal": plan.terminal,
                              "waves": [w.wave for w in plan.waves]}, sort_keys=True))
            return 0
        from agent_bus import publisher  # the publisher's own reading of the world
        from agent_bus.trust import Trust
        target = publisher.Target(args.repo, args.issue, args.pr,
                                  Trust(frozenset({args.trusted_author.lower()}), "goal"))
        binding, why = publisher.binding_for(target, args.comment_id, run)
        if binding is None:
            # No plan, no checks: nothing is written, so ACCEPT stays impossible.
            print(json.dumps({"bound": False, "reason": why}, sort_keys=True))
            return 0
        evidence = run_checks(binding, args.checkout)
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(evidence.as_dict(), handle, sort_keys=True)
        print(json.dumps({"bound": True, **evidence.as_dict()}, sort_keys=True))
        return 0
    except BusError as exc:
        print(json.dumps({"code": exc.code, "detail": exc.detail}, sort_keys=True))
        return 2


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
