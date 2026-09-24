"""`python3 -m agent_bus <command>` -- the operator surface for the bus.

Exit codes are part of the contract, because a workflow step and a human read
the same run:

    0  the command answered
    2  a bus rejection (the code is printed, and it is stable)
    3  the durable authority could not be resolved

Nothing here writes to GitHub or invokes Claude unless an explicit flag says so.
"""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path

from agent_bus import SCHEMA
from agent_bus.errors import BusError
from agent_bus.issue import AuthorityError, read_comments, resolve_authority
from agent_bus.machine import fold
from agent_bus.protocol import Envelope, parse, parse_comment
from agent_bus.shell import Runner
from agent_bus.supervisor import Supervisor
from agent_bus.wave import plan_from_command

DEFAULT_REPO = "MTJawnny/mtjawnny-pipeline"


def _read(path: str | None) -> str:
    if path in (None, "-"):
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _envelope(text: str) -> Envelope:
    """Accept either a bare message or a whole comment body containing one."""
    stripped = text.lstrip()
    if stripped.startswith("{"):
        return parse(text)
    envelope = parse_comment(text)
    if envelope is None:
        raise BusError("BUS_NOT_AN_OBJECT", "input carries no mtj-bus block")
    return envelope


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _supervisor(args) -> Supervisor:
    return Supervisor(
        repo_path=args.repo_path,
        repo_slug=args.repo,
        actor=args.actor,
        issue=args.issue,
        transport_pr=args.pr,
        trusted_authors=tuple(a for a in (args.trusted or "").split(",") if a),
        run=Runner(),
    )


def build_parser() -> tuple[argparse.ArgumentParser, tuple[str, ...]]:
    """The parser, plus the command names it actually registered.

    The names are RETURNED rather than listed twice, so a documented command and
    a registered command cannot drift apart without a test noticing.
    """
    parser = argparse.ArgumentParser(prog="agent_bus", description=f"Agent Bus ({SCHEMA})")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/name on GitHub")
    parser.add_argument("--repo-path", default=".", help="local checkout to reason about")
    parser.add_argument("--issue", type=int, default=1, help="the authority issue")
    parser.add_argument("--pr", type=int, default=None, help="transport PR number, if any")
    parser.add_argument("--actor", default="WORKER", choices=("WORKER", "MANAGER", "CAPTAIN"))
    parser.add_argument("--trusted", default=None,
                        help="comma-separated GitHub logins allowed to speak on the bus")
    sub = parser.add_subparsers(dest="command", required=True)
    registered: list[str] = []

    def add(name: str, help: str):
        registered.append(name)
        return sub.add_parser(name, help=help)

    add("authority", help="resolve latest K -> active T and print it")
    add("state", help="fold the live comment stream into bus state")

    p_resume = add("resume", help="what is left of a wave, from durable evidence")
    p_resume.add_argument("--wave", required=True)

    p_validate = add("validate", help="strictly validate one message")
    p_validate.add_argument("path", nargs="?", default="-")

    p_plan = add("plan", help="deterministic unit order for a WAVE_COMMAND")
    p_plan.add_argument("path", nargs="?", default="-")

    p_render = add("render", help="wrap a validated message as a comment body")
    p_render.add_argument("path", nargs="?", default="-")

    p_poll = add("poll", help="one supervisor pass (dry run unless --execute)")
    p_poll.add_argument("--execute", action="store_true", help="actually invoke the transport")
    p_poll.add_argument("--resume", action="store_true",
                        help="continue a wave already claimed by an earlier session")

    add("selftest", help="run the bus test suite")

    return parser, tuple(registered)


def main(argv: list[str] | None = None) -> int:
    parser, _ = build_parser()
    args = parser.parse_args(argv)

    try:
        return _run(args)
    except BusError as exc:
        print(f"{exc.code}: {exc.detail}", file=sys.stderr)
        return 2
    except AuthorityError as exc:
        print(f"AUTHORITY_UNRESOLVED: {exc}", file=sys.stderr)
        return 3


def _run(args) -> int:
    if args.command == "authority":
        comments = read_comments(args.issue, args.repo, Runner())
        _print(resolve_authority(comments, args.issue).as_dict())
        return 0

    if args.command == "state":
        _print(_supervisor(args).observe().state.as_dict())
        return 0

    if args.command == "resume":
        observation = _supervisor(args).observe()
        from agent_bus.git_evidence import completed_units
        from_git = completed_units(args.repo_path, args.wave,
                                   observation.authority.accepted_head)
        _print(observation.state.resume(args.wave, from_git))
        return 0

    if args.command == "validate":
        envelope = _envelope(_read(args.path))
        _print({"valid": True, "message_id": envelope.message_id, "actor": envelope.actor,
                "kind": envelope.kind, "wave": envelope.wave,
                "wakes_worker": envelope.wakes("WORKER"),
                "wakes_manager": envelope.wakes("MANAGER")})
        return 0

    if args.command == "plan":
        envelope = _envelope(_read(args.path))
        if envelope.kind != "WAVE_COMMAND":
            raise BusError("BUS_PARENT_KIND_MISMATCH", f"{envelope.kind} is not a WAVE_COMMAND")
        plan = plan_from_command(envelope.wave, envelope.body)
        _print({"wave": plan.wave, "branch": plan.branch, "order": list(plan.order),
                "review_boundary": plan.review_boundary,
                "mutating": [u.id for u in plan.units if u.mutating]})
        return 0

    if args.command == "render":
        print(_envelope(_read(args.path)).render(), end="")
        return 0

    if args.command == "poll":
        _print(_supervisor(args).poll_once(execute=args.execute, resume=args.resume))
        return 0

    if args.command == "selftest":
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root))
        loader = unittest.TestLoader()
        suite = loader.discover(str(root / "tests" / "refoundation"), top_level_dir=str(root),
                                pattern="test_agent_bus*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        return 0 if runner.run(suite).wasSuccessful() else 1

    raise AssertionError(f"unreachable command {args.command}")


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
