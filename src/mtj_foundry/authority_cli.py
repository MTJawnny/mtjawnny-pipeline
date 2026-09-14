"""Codebook authority operator — the CLI and its commands, over the S12 owners.

## What this is

The operator composition S12 deliberately left in the legacy `foundry_authority`
shell for S13: the argument parser, the six commands (`status`, `publish`,
`verify-remote`, `restore`, `verify`, `describe-local`), their printed reports,
remote-nickname selection, and the order in which each command reaches the
authority owners. Every flag, default, help string, printed line and exit code
is the shell's, character for character.

It is NOT an installed script and must not become one: `publish` and `restore`
mutate remote and local state, and discoverability of mutating operators is not
widened by this module.

## What this is NOT

* **Not authority law.** Manifest validation, succession, exact verification,
  the immutable transport, the status states and the restore order are
  `authority`, `authority_transport`, `authority_status` and `authority_restore`.
  This module calls them; it restates none of them.
* **Not a layout, backup or process owner.** Everything repository-specific
  arrives in an `AuthorityOperatorContext` built by the composition boundary:
  the tracked selector path, the operational codebook path, the disposable
  candidate directory, the remote nicknames, a transport factory that already
  declares the forbidden staging destinations, the backup policy, the corpus
  reference, the historic STOP, and the offline selftest. Nothing here derives a
  root, constructs a transport directly, or exits the process itself.
* **Not a translator.** A typed `AuthorityRefusal` raised by an owner propagates
  out of these commands unchanged; the boundary that invoked them turns it into
  the historic `STOP — …`. `RestoreError` is caught in exactly one place, as it
  always was: `restore` reports it and returns 1.
"""

from __future__ import annotations

import argparse
import dataclasses
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mtj_foundry import authority, authority_restore, authority_status, codebook_store

__all__ = [
    "AuthorityOperatorContext",
    "build_parser",
    "cmd_describe_local",
    "cmd_publish",
    "cmd_restore",
    "cmd_status",
    "cmd_verify",
    "cmd_verify_remote",
    "run",
]


@dataclasses.dataclass(frozen=True)
class AuthorityOperatorContext:
    """What the composition boundary supplies. Callables are invoked when a
    command needs them, never captured as values, so the boundary's own
    call-time rebinding stays observable."""

    manifest_path: Path
    codebook_path: Callable[[], Path]
    candidate_dir: Path
    read_remote: Callable[[Any], str]
    write_remote: Callable[[Any], str]
    transport: Callable[..., Any]
    backup_policy: Callable[[], Callable]
    corpus_ref_current: Callable[[], str]
    stop: Callable[[str], None]
    selftest: Callable[[], int]


def cmd_status(args, ctx: AuthorityOperatorContext) -> int:
    transport = None
    if args.check_remote:
        transport = ctx.transport(ctx.read_remote(args.remote), bucket=args.bucket)
    candidate = None
    if getattr(args, "candidate", None):
        candidate, _ = authority.load_manifest(Path(args.candidate))
    st = authority_status.status(ctx.manifest_path, ctx.codebook_path(), transport, candidate)
    if args.json:
        printable = {k: v for k, v in st.items()}
        # `indent=2, ensure_ascii=False` + one newline is the package's single
        # JSON byte policy, owned by `codebook_store.serialize`.
        print(codebook_store.serialize(printable), end="")
        return 0
    print("=" * 78)
    print(f"C6 AUTHORITY STATUS — {st['state']}")
    print("=" * 78)
    print(f"  {st.get('detail', '')}")
    local = st.get("local") or {}
    if local.get("present"):
        print(f"\n  local codebook  {local['path']}")
        print(f"    sha256        {local['sha256']}")
        print(f"    byte_size     {local['byte_size']}")
        print(f"    axes/assert   {local['active_axis_count']} active, "
              f"{local['assertion_count']} assertions "
              f"({local['human_assertion_count']} human, "
              f"{local['rule_derived_assertion_count']} rule-derived)")
    else:
        print(f"\n  local codebook  ABSENT ({local.get('path')})")
    sel = st.get("selected")
    if sel:
        print(f"\n  selected authority")
        print(f"    bucket        {sel['bucket']}")
        print(f"    object_path   {sel['object_path']}")
        print(f"    sha256        {sel['sha256']}")
    else:
        print(f"\n  selected authority  NONE — manifest {ctx.manifest_path} absent")
    cand = st.get("candidate")
    if cand:
        print(f"\n  candidate (REPORTED, never selected)")
        print(f"    classification  {cand['classification']}")
        print(f"    authoritative   {cand['authoritative']}")
        print(f"    object_path     {cand['object_path']}")
        print(f"    sha256          {cand['sha256']}")
        if "remote" in cand:
            print(f"    remote          {cand['remote']}")
        print(f"    why not         {cand['why_not_authority']}")
    for line in st.get("violations") or []:
        print(f"    ! {line}")
    return 0


def cmd_publish(args, ctx: AuthorityOperatorContext) -> int:
    """Build a candidate manifest FROM the codebook bytes and publish them
    immutably. Writes the candidate to disposable output space only — creating
    the tracked selector is a separate, Captain-authorised act (P3 §18)."""
    cb_path = Path(args.codebook) if args.codebook else ctx.codebook_path()
    prior = None
    if args.prior_manifest:
        prior, pv = authority.load_manifest(Path(args.prior_manifest))
        if prior is None or pv:
            ctx.stop(f"--prior-manifest {args.prior_manifest} is missing or invalid: {pv}")

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = authority.build_manifest(
        snapshot_id=args.snapshot_id,
        created_utc=created,
        mutation_review_id=args.mutation_review_id,
        corpus_ref=args.corpus_ref or ctx.corpus_ref_current(),
        previous_snapshot_hash=args.previous_snapshot_hash,
        codebook_path=cb_path,
        prior=prior,
    )
    out_path = Path(args.candidate_out) if args.candidate_out else (
        ctx.candidate_dir / f"candidate-manifest.{manifest['snapshot_id']}.json")
    if ctx.manifest_path.resolve() == out_path.resolve():
        ctx.stop("--candidate-out names the TRACKED selector path. A candidate is not an "
                 "authority; creating that file is a separate authorised act.")

    print(f"candidate manifest for {cb_path}")
    print(authority.serialize_manifest(manifest))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(authority.serialize_manifest(manifest), encoding="utf-8")
    print(f"wrote candidate (disposable, gitignored): {out_path}")

    if args.dry_run:
        print("\nDRY RUN — nothing uploaded.")
        return 0

    t = ctx.transport(ctx.write_remote(args.remote), bucket=manifest["bucket"])
    print(f"\npublishing to {t.remote}:{t.bucket}/{manifest['object_path']}")
    outcome = t.put_immutable(manifest["object_path"], cb_path,
                              manifest["sha256"], manifest["byte_size"])
    print(f"result: {outcome}")
    print("\nNOTE: this object is a CANDIDATE. No tracked manifest selects it, so it is "
          "ORPHAN / NON-AUTHORITATIVE until Captain authorises the selector.")
    return 0


def cmd_verify_remote(args, ctx: AuthorityOperatorContext) -> int:
    """Consumer-side proof, through the READ-ONLY remote: fetch the exact object
    to staging, verify bytes, and validate that they are the codebook the
    manifest describes. Installs nothing."""
    manifest, v = authority.load_manifest(Path(args.manifest))
    if manifest is None or v:
        ctx.stop(f"{args.manifest} is missing or invalid: {v}")
    t = ctx.transport(ctx.read_remote(args.remote), bucket=manifest["bucket"])
    with tempfile.TemporaryDirectory() as td:
        staged = Path(td) / "codebook.staged.json"
        t.get_verified(manifest["object_path"], staged, manifest["sha256"],
                       manifest["byte_size"])
        print(f"reader remote      : {t.remote}:{t.bucket}")
        print(f"object             : {manifest['object_path']}")
        print(f"sha256 (recomputed): {authority.sha256_of_file(staged)}")
        print(f"byte_size          : {staged.stat().st_size}")
        payload = authority_restore.validate_codebook_payload(staged, manifest)
        print(f"codebook validation: OK — {payload['lint']}")
        local = authority.describe_local(staged)
        for f in ("active_axis_count", "assertion_count", "human_assertion_count",
                  "rule_derived_assertion_count"):
            print(f"  {f:32} {local[f]}")
    return 0


def cmd_restore(args, ctx: AuthorityOperatorContext) -> int:
    """remote -> staging -> verify -> validate -> atomic install. In that order,
    and the order is asserted rather than described."""
    manifest, v = authority.load_manifest(Path(args.manifest))
    if manifest is None or v:
        ctx.stop(f"{args.manifest} is missing or invalid: {v}")
    t = ctx.transport(ctx.read_remote(args.remote), bucket=manifest["bucket"])
    install_to = Path(args.install_to)
    staging = Path(args.staging) if args.staging else install_to.parent / ".restore-staging"
    try:
        result = authority_restore.restore_snapshot(
            manifest, t, staging, install_to, args.replace_existing,
            backup=ctx.backup_policy())
    except authority_restore.RestoreError as e:
        print(f"RESTORE HALTED — {e}")
        return 1
    print(f"restore steps      : {' -> '.join(result['trace'])}")
    print(f"staged at          : {result['staged']}")
    print(f"installed          : {result['installed']}")
    print(f"sha256             : {result['sha256']}")
    print(f"byte_size          : {result['byte_size']}")
    return 0


def cmd_verify(args, ctx: AuthorityOperatorContext) -> int:
    ok, reason = authority.verify_exact(args.sha, args.size, Path(args.path))
    print(("VERIFIED — " if ok else "FAILED — ") + reason)
    return 0 if ok else 1


def cmd_describe_local(args, ctx: AuthorityOperatorContext) -> int:
    print(codebook_store.serialize(authority.describe_local(ctx.codebook_path())), end="")
    return 0


def build_parser(ctx: AuthorityOperatorContext) -> argparse.ArgumentParser:
    """The historic parser. Each subcommand's `func` takes the parsed args."""
    ap = argparse.ArgumentParser(
        description="C6 authority machinery — manifest, verifier, transport, status.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def bind(command):
        return lambda a: command(a, ctx)

    p = sub.add_parser("status", help="read-only authority/candidate state")
    p.add_argument("--check-remote", action="store_true",
                   help="also confirm the SELECTED object exists (never lists)")
    p.add_argument("--remote", default=None, help="rclone remote NAME (local config)")
    p.add_argument("--bucket", default=authority.AUTHORITY_BUCKET)
    p.add_argument("--json", action="store_true")
    p.add_argument("--candidate", default=None,
                   help="report an UNSELECTED candidate manifest; cannot make it authority")
    p.set_defaults(func=bind(cmd_status))

    p = sub.add_parser("publish", help="build a candidate manifest and publish immutably")
    p.add_argument("--snapshot-id", required=True)
    p.add_argument("--mutation-review-id", required=True,
                   help="the ratified mutation these bytes came from")
    p.add_argument("--previous-snapshot-hash", default=None,
                   help="omit for genesis (null); otherwise the prior snapshot's sha256")
    p.add_argument("--prior-manifest", default=None,
                   help="the previously SELECTED manifest, for succession validation")
    p.add_argument("--corpus-ref", default=None)
    p.add_argument("--codebook", default=None)
    p.add_argument("--candidate-out", default=None)
    p.add_argument("--remote", default=None, help="rclone WRITE remote NAME")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=bind(cmd_publish))

    p = sub.add_parser("verify-remote",
                       help="read-only proof that the published object is exact and valid")
    p.add_argument("--manifest", required=True)
    p.add_argument("--remote", default=None, help="rclone READ remote NAME")
    p.set_defaults(func=bind(cmd_verify_remote))

    p = sub.add_parser("restore",
                       help="remote -> staging -> verify -> validate -> atomic install")
    p.add_argument("--manifest", required=True)
    p.add_argument("--install-to", required=True,
                   help="explicit destination; there is no default that resolves to the "
                        "operational codebook")
    p.add_argument("--staging", default=None)
    p.add_argument("--remote", default=None, help="rclone READ remote NAME")
    p.add_argument("--replace-existing", action="store_true")
    p.set_defaults(func=bind(cmd_restore))

    p = sub.add_parser("verify", help="exact-byte verification of a local file")
    p.add_argument("path")
    p.add_argument("--sha", required=True)
    p.add_argument("--size", required=True, type=int)
    p.set_defaults(func=bind(cmd_verify))

    p = sub.add_parser("describe-local", help="facts about the local codebook")
    p.set_defaults(func=bind(cmd_describe_local))

    p = sub.add_parser("selftest", help="every negative control, offline")
    p.set_defaults(func=lambda a: ctx.selftest())
    return ap


def run(argv, ctx: AuthorityOperatorContext) -> int:
    """Parse `argv` (None means the process arguments) and run the command."""
    args = build_parser(ctx).parse_args(argv)
    return args.func(args)
