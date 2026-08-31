#!/usr/bin/env python3
"""Harvest every ratified-ruling reference across docs/ into one registry.

Purpose: no document may be deleted until every ruling it carries is
provably recorded somewhere else. Dependency analysis alone proved
insufficient -- 2026-08-02, every deletion candidate turned out to carry
ruling text (44 markers in B-MIGRATION-AUDIT-PACKET alone).

This is a DET job. No mutation of anything but its own outputs, no API
calls, no card data. Deterministic: explicit sort keys everywhere, no
reliance on set/dict iteration order (see CLAUDE.md traps).

THE INPUT POPULATION IS GIT'S TRACKED SET, NOT THE FILESYSTEM.
--------------------------------------------------------------
Captain's ruling, 2026-08-15. `docs/RATIFIED-RULINGS-REGISTRY.md` is a
TRACKED deletion-gate artifact, so its source population must be the
repository's tracked documentation. Raw `DOCS.glob("*.md")` made it a
function of one developer's worktree instead: on 2026-08-14 six untracked
working papers added 38 references and one distinct id, and -- the reason
this is a defect and not a cosmetic count -- an untracked incident paper
mentioning `R8` STRIPPED SOLE-HOME STATUS from `B-MIGRATION-DISCOVERY.md`,
the tracked document that actually carries that ruling. The deletion gate
opened on a genuine ruling because of a file Git had never heard of.

Note what did NOT catch it: the ratchet. `sole_home` held at 37 across that
run, because a genuine sole home was lost and a FAKE one (an AQ4 benchmark
label) was gained in the same pass. A count cannot see a substitution --
the `len() >= 15` halt-guard trap, aimed at this file.

An untracked working paper must never create or corroborate a ruling id,
become a sole home, or move a deletion-gate count. Staging a document is
the act that admits it. `git ls-files` (the index) is therefore the
enumeration, which gives all three properties at once:
  - tracked docs modified in the worktree are read as WORKING-TREE bytes;
  - newly staged docs participate before they are committed;
  - untracked docs are invisible until someone stages them.

Outputs:
  docs/RATIFIED-RULINGS-REGISTRY.md    human-readable registry
  experiments/out/foundry/ruling_registry.json   machine-checkable

Usage:
  python3 experiments/foundry_ruling_registry.py
  python3 experiments/foundry_ruling_registry.py --check <doc.md>
      exit 0 if every ruling in <doc> also appears elsewhere (safe to
      delete), exit 1 otherwise, listing the unique rulings that block it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# C8.5J: the standing ratchet now comes from the permanent package. This module
# is invoked as a loose script, so `mtj_foundry` is reachable only once the
# C8.5A compatibility bootstrap has run -- and `foundry_common` is what runs it.
# Importing the boundary FIRST is therefore load-bearing, and is the reason this
# import sits outside the otherwise alphabetical block above. No sys.path
# mutation and no second bootstrap is added here.
import foundry_common as fc  # noqa: E402,F401
from mtj_foundry import ratchet  # noqa: E402
from mtj_foundry.paths import ProjectPaths  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RATCHET_BASELINE = ProjectPaths.for_root(fc.REPO_ROOT).foundry_audit_baseline
DOCS = REPO_ROOT / "docs"
OUT_JSON = REPO_ROOT / "experiments" / "out" / "foundry" / "ruling_registry.json"
OUT_MD = DOCS / "RATIFIED-RULINGS-REGISTRY.md"

# Generated artifact -- never a harvest source (it would cite every ruling
# and make every doc look redundantly covered).
SELF_EXCLUDE = {"RATIFIED-RULINGS-REGISTRY.md"}

# IDs whose shape is unambiguous: harvested wherever they appear.
UNAMBIGUOUS = re.compile(
    r"\b(?:CDR-\d{1,2}|ADD-\d{1,2}|NEW-\d{1,2}|GRAMMAR-SS\d{1,2}|AG-[A-Z]+-\d{2}|B-\d{2}|H-\d{2}|M-\d{2})\b"
)

# Short IDs (D5, Q8.5, S3, A15...). Ambiguous on their own -- a bare "A1"
# is often prose -- so a hit only counts in one of two contexts:
#   (a) the line carries a ruling word, or
#   (b) the id sits in DEFINITION POSITION.
# (b) was missing in the first cut and it mattered: this codebase writes
# rulings as "- **A8** -- statement", which contains no ruling keyword, so
# A8 was harvested from 1 doc when it actually lives in 6. That produced a
# FALSE deletion-block. Under-harvesting is not "safely conservative"
# here -- it makes the gate untrustworthy in both directions.
SHORT_ID = re.compile(r"\b([ADQSTMRFG])[-\s]?(\d{1,2}(?:\.\d{1,2})?)\b")
RULING_WORD = re.compile(
    r"ratifi|ruled|ruling|captain|verdict|decision|standing|precedent|overturn|amend",
    re.IGNORECASE,
)
# "**A8**", "- **A8 (CDR-07):**", "| A8 |", "1. A8 —", "A8." at line start
DEFINITION_POS = re.compile(
    r"(?:^|[-*|]\s*|^\d+\.\s*)\*{0,2}([ADQSTMRFG])[-\s]?(\d{1,2}(?:\.\d{1,2})?)"
    r"\*{0,2}\s*(?:[(:—–.-]|\*\*)"
)

# Lines that are pure navigation rather than a ruling statement.
NOISE = re.compile(r"^\s*(?:\||#{1,6}\s*$|-{3,}|={3,})")

MAX_STATEMENT = 220


def tracked_docs() -> list[Path]:
    """The ONE canonical enumeration: markdown Git tracks directly under docs/.

    Reads the INDEX (`git ls-files` defaults to `--cached`), so a staged
    document participates before it is committed and an untracked one does
    not participate at all. Content always comes from the working tree, so a
    tracked doc edited but not staged is scanned as it currently reads.

    No filename exclusion list, no mtime, no directory walk order: the
    tracked set decides membership and the sort decides order. Any failure
    to enumerate is fatal -- a registry built from a SILENTLY EMPTY or
    SILENTLY PARTIAL tracked set would report rulings as uncorroborated and
    block deletions that are in fact safe, or worse, report a document as
    carrying nothing.
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", "docs"],
            capture_output=True,
            text=True,
        )
    except OSError as exc:  # git absent, not executable, ...
        raise SystemExit(f"HALT: cannot run git to enumerate tracked docs: {exc}")
    if r.returncode != 0:
        raise SystemExit(
            "HALT: `git ls-files` failed while enumerating tracked docs "
            f"(exit {r.returncode}): {r.stderr.strip() or '(no stderr)'}"
        )

    # `-z` means NUL-separated and never quoted, so no unquoting step can go
    # wrong on a non-ASCII name. The parent test reproduces the previous
    # `DOCS.glob("*.md")` exactly: directly under docs/, never docs/archive/.
    names = [n for n in r.stdout.split("\0") if n]
    docs = sorted(
        (REPO_ROOT / n for n in names
         if Path(n).parent == Path("docs")
         and Path(n).suffix == ".md"
         and Path(n).name not in SELF_EXCLUDE),
        key=lambda p: p.name,
    )

    # A tracked doc that is missing from the worktree means an unstaged
    # deletion. Halting is the house style: skipping it would silently drop
    # every ruling it is the sole home of, which is the exact loss this
    # registry exists to make impossible.
    missing = [p.name for p in docs if not p.is_file()]
    if missing:
        raise SystemExit(
            "HALT: tracked under docs/ but absent from the worktree "
            f"(unstaged deletion?): {', '.join(sorted(missing))}"
        )
    return docs


def normalise_id(kind: str, num: str) -> str:
    return f"{kind}{num}"


def harvest_file(path: Path) -> list[dict]:
    """Return one record per ruling reference found in `path`."""
    hits: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        print(f"HALT: {path.name} is not valid UTF-8", file=sys.stderr)
        raise

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if not line.strip() or NOISE.match(line):
            continue
        statement = re.sub(r"\s+", " ", line.strip().lstrip("-*# ").strip())
        if len(statement) > MAX_STATEMENT:
            statement = statement[: MAX_STATEMENT - 1] + "…"

        found: list[str] = []
        for m in UNAMBIGUOUS.finditer(line):
            found.append(m.group(0))
        if RULING_WORD.search(line):
            for m in SHORT_ID.finditer(line):
                found.append(normalise_id(m.group(1), m.group(2)))
        for m in DEFINITION_POS.finditer(line):
            found.append(normalise_id(m.group(1), m.group(2)))

        # sorted+dedup, so ordering never depends on set iteration
        for rid in sorted(set(found)):
            hits.append(
                {
                    "id": rid,
                    "doc": path.name,
                    "line": lineno,
                    "statement": statement,
                }
            )
    return hits


def build() -> dict:
    docs = tracked_docs()
    if not docs:
        raise SystemExit("HALT: no TRACKED markdown found under docs/")

    all_hits: list[dict] = []
    for p in docs:
        all_hits.extend(harvest_file(p))
    all_hits.sort(key=lambda h: (h["id"], h["doc"], h["line"]))

    by_id: dict[str, list[dict]] = {}
    for h in all_hits:
        by_id.setdefault(h["id"], []).append(h)

    # A ruling is CORROBORATED when it appears in more than one document.
    # A doc is DELETION-BLOCKED while it is the sole home of any ruling.
    sole_home: dict[str, list[str]] = {}
    for rid in sorted(by_id):
        docs_with = sorted({h["doc"] for h in by_id[rid]})
        if len(docs_with) == 1:
            sole_home.setdefault(docs_with[0], []).append(rid)

    per_doc: dict[str, dict] = {}
    for p in docs:
        ids = sorted({h["id"] for h in all_hits if h["doc"] == p.name})
        unique = sorted(sole_home.get(p.name, []))
        per_doc[p.name] = {
            "lines": len(p.read_text(encoding="utf-8").splitlines()),
            "ruling_ids": ids,
            "sole_home_for": unique,
            "deletion_blocked": bool(unique),
        }

    return {
        "schema": "foundry-ruling-registry/1",
        "generated_from": f"{len(docs)} documents under docs/",
        "total_references": len(all_hits),
        "distinct_rulings": len(by_id),
        "corroborated": sum(
            1 for rid in by_id if len({h["doc"] for h in by_id[rid]}) > 1
        ),
        "sole_home": sum(
            1 for rid in by_id if len({h["doc"] for h in by_id[rid]}) == 1
        ),
        "rulings": {rid: by_id[rid] for rid in sorted(by_id)},
        "per_doc": {k: per_doc[k] for k in sorted(per_doc)},
    }


def write_markdown(reg: dict) -> None:
    L: list[str] = []
    A = L.append
    A("# RATIFIED RULINGS REGISTRY — generated, do not hand-edit")
    A("")
    A("Generated by `experiments/foundry_ruling_registry.py`. Re-run after any")
    A("doc change. Per ADD-06 the numbers below are pasted from generator")
    A("output, never restated by hand.")
    A("")
    A("**This registry is the deletion gate.** A document may not be deleted")
    A("while it is the SOLE HOME of any ruling — that ruling must first be")
    A("moved somewhere durable. Check one doc with:")
    A("")
    A("```")
    A("python3 experiments/foundry_ruling_registry.py --check <NAME>.md")
    A("```")
    A("")
    A("## Summary")
    A("")
    A(f"- documents scanned: **{reg['generated_from']}**")
    A(f"- ruling references found: **{reg['total_references']}**")
    A(f"- distinct ruling ids: **{reg['distinct_rulings']}**")
    A(f"- corroborated (appear in >1 doc): **{reg['corroborated']}**")
    A(f"- **sole-home (appear in exactly 1 doc): {reg['sole_home']}**")
    A("")
    A("## Deletion gate — per document")
    A("")
    A("| document | lines | rulings | sole home for | deletable |")
    A("|---|---:|---:|---:|---|")
    for name in sorted(reg["per_doc"]):
        d = reg["per_doc"][name]
        if not d["ruling_ids"]:
            continue
        A(
            f"| `{name}` | {d['lines']} | {len(d['ruling_ids'])} | "
            f"{len(d['sole_home_for'])} | "
            f"{'**NO**' if d['deletion_blocked'] else 'yes'} |"
        )
    A("")
    A("### Documents carrying no ruling reference (deletable on this test alone)")
    A("")
    clean = [n for n in sorted(reg["per_doc"]) if not reg["per_doc"][n]["ruling_ids"]]
    A(", ".join(f"`{n}`" for n in clean) if clean else "_(none)_")
    A("")
    A("## Sole-home rulings — these block their document")
    A("")
    for name in sorted(reg["per_doc"]):
        d = reg["per_doc"][name]
        if not d["sole_home_for"]:
            continue
        A(f"**`{name}`** — sole home for {len(d['sole_home_for'])}:")
        A("")
        for rid in d["sole_home_for"]:
            occ = reg["rulings"][rid][0]
            A(f"- `{rid}` (line {occ['line']}) — {occ['statement']}")
        A("")
    A("## Full registry")
    A("")
    for rid in sorted(reg["rulings"]):
        occ = reg["rulings"][rid]
        homes = sorted({o["doc"] for o in occ})
        A(f"### `{rid}` — {len(occ)} reference(s) across {len(homes)} doc(s)")
        A("")
        for o in occ:
            A(f"- `{o['doc']}:{o['line']}` — {o['statement']}")
        A("")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def emit_outputs(reg: dict, *, emit: bool) -> list:
    """Write the registry's two outputs, or write NOTHING. Returns paths written.

    THE ONLY PLACE THIS TOOL WRITES outside `--update-baseline`, so tracked purity
    is a property of one function rather than of the whole file. Gate 2 calls the
    registry with `--check-only`, which routes here with `emit=False`.

    Why the gate may not emit: `OUT_MD` is `docs/RATIFIED-RULINGS-REGISTRY.md`, a
    TRACKED deletion-gate artifact. Measured 2026-08-29 on a full green Gate 2
    run, this write left the worktree DIRTY — the regenerated file differs from
    the committed one, and `refoundation/BOOTSTRAP-STATE.yaml` warns that the
    regenerated registry carries a KNOWN FALSE-POSITIVE S1 namespace collision
    and must not be accepted merely to clean the tree. So verifying the gate
    produced a diff that nobody may commit, on every run.

    Nothing about the REGISTRY changes with `emit`. `build()` runs first and is
    untouched; the metrics and the ratchet comparison are computed from `reg`,
    not from anything on disk.
    """
    if not emit:
        return []
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(reg, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(reg)
    return [OUT_MD, OUT_JSON]


def _selftest() -> int:
    """Prove the tracked-doc boundary is a BOUNDARY, not a comment.

    Five controls. NC1/NC2/NC4/NC5 run against a THROWAWAY git repository in
    a temp dir -- this tool must never stage, unstage or write anything in
    the real worktree to test itself. NC3 reads the real docs/ and mutates
    nothing.

    The temp repo is reached by rebinding this module's REPO_ROOT/DOCS.
    `build()` and `tracked_docs()` resolve those from the module dict at call
    time, and this function lives IN that module, so there is exactly one
    instance to patch. (CLAUDE.md: patching your own globals is dead when the
    patch has to cross a module boundary -- here it does not, and nothing is
    re-imported.)
    """
    import shutil
    import tempfile

    global REPO_ROOT, DOCS
    failures: list[str] = []

    def check(name: str, ok: bool, detail: str) -> None:
        if not ok:
            failures.append(name)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")

    def soles(reg: dict) -> dict:
        return {n: list(d["sole_home_for"])
                for n, d in reg["per_doc"].items() if d["sole_home_for"]}

    def glob_docs() -> list[Path]:
        """The pre-2026-08-15 enumeration, kept ONLY as the rigged control."""
        return sorted((p for p in DOCS.glob("*.md")
                       if p.name not in SELF_EXCLUDE), key=lambda p: p.name)

    real_root, real_docs = REPO_ROOT, DOCS
    tmp = Path(tempfile.mkdtemp(prefix="ruling-registry-selftest-"))
    print("=" * 70)
    print("SELFTEST — tracked-doc population boundary")
    print("=" * 70)
    try:
        (tmp / "docs").mkdir()
        for argv in (["init", "-q"],
                     ["config", "user.email", "selftest@localhost"],
                     ["config", "user.name", "selftest"]):
            subprocess.run(["git", "-C", str(tmp)] + argv, check=True,
                           capture_output=True, text=True)

        # The fixture IS the 2026-08-14 incident in miniature: one tracked
        # document that is the sole home of a genuine ruling, and one
        # untracked working paper that both (a) restates that ruling, which
        # would corroborate it away, and (b) defines a benchmark label shaped
        # like a ruling id, which would become a sole home of its own.
        home = tmp / "docs" / "T-HOME.md"
        paper = tmp / "docs" / "U-PAPER.md"
        home.write_text("# tracked\n\n- **R8** — genuine ruling, sole home here.\n",
                        encoding="utf-8")
        subprocess.run(["git", "-C", str(tmp), "add", "--", "docs/T-HOME.md"],
                       check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(tmp), "commit", "-qm", "fixture"],
                       check=True, capture_output=True, text=True)

        REPO_ROOT, DOCS = tmp, tmp / "docs"
        base = build()

        paper.write_text(
            "# untracked working paper\n\n"
            "- **R8** — restated here, which would corroborate it away.\n"
            "- **F1** — fake benchmark label that would become a sole home.\n",
            encoding="utf-8")

        # ---- NC-RR1: an untracked doc changes nothing -------------------
        after = build()
        check("NC-RR1 untracked doc cannot move counts",
              (after["distinct_rulings"], after["sole_home"],
               after["total_references"]) ==
              (base["distinct_rulings"], base["sole_home"],
               base["total_references"]),
              f"ids={after['distinct_rulings']} sole={after['sole_home']} "
              f"refs={after['total_references']}")
        check("NC-RR1 untracked doc cannot move homes",
              soles(after) == soles(base), f"{soles(after)}")
        check("NC-RR1 fake id absent", "F1" not in after["rulings"],
              "F1 did not enter the registry")

        # ---- NC-RR1-RIG: remove the boundary, the control must go red ---
        real_enum = globals()["tracked_docs"]
        globals()["tracked_docs"] = glob_docs
        try:
            rigged = build()
        finally:
            globals()["tracked_docs"] = real_enum
        check("NC-RR1-RIG boundary removal is detected",
              "F1" in rigged["rulings"] and soles(rigged) != soles(base),
              f"rigged homes={soles(rigged)}")
        check("NC-RR1-RIG restored", soles(build()) == soles(base),
              "tracked-only enumeration back in force")

        # ---- NC-RR5: aggregate equality hides a SUBSTITUTION ------------
        # This is the control the real ratchet did not have. On 2026-08-14
        # `sole_home` held at 37 while B-MIGRATION-DISCOVERY.md silently lost
        # R8 and an AQ4 benchmark label silently gained F1. A count cannot
        # see a substitution; only the population boundary can.
        check("NC-RR5 aggregate sole_home is EQUAL across the substitution",
              rigged["sole_home"] == base["sole_home"],
              f"{base['sole_home']} == {rigged['sole_home']} — "
              "a ratchet on this number is blind here")
        check("NC-RR5 the substitution really happened",
              soles(base) == {"T-HOME.md": ["R8"]}
              and soles(rigged) == {"U-PAPER.md": ["F1"]},
              f"genuine {soles(base)} -> fake {soles(rigged)}")
        check("NC-RR5 boundary prevents it independently of the count",
              soles(build()) == {"T-HOME.md": ["R8"]},
              "R8 keeps its genuine home while the paper stays untracked")

        # ---- NC-RR2: staging admits a document, pre-commit --------------
        subprocess.run(["git", "-C", str(tmp), "add", "--", "docs/U-PAPER.md"],
                       check=True, capture_output=True, text=True)
        staged = build()
        check("NC-RR2 staged doc participates before commit",
              "F1" in staged["rulings"]
              and len(staged["per_doc"]) == len(base["per_doc"]) + 1,
              f"documents {len(base['per_doc'])} -> {len(staged['per_doc'])}")
        paper.write_text("# edited after staging\n\n- **F2** — worktree bytes.\n",
                         encoding="utf-8")
        edited = build()
        check("NC-RR2 worktree bytes beat index bytes",
              "F2" in edited["rulings"] and "F1" not in edited["rulings"],
              "the scan reads the file as it currently is")

        # ---- NC-RR4: determinism x2 -------------------------------------
        a = json.dumps(build(), indent=2, sort_keys=True, ensure_ascii=False)
        b = json.dumps(build(), indent=2, sort_keys=True, ensure_ascii=False)
        check("NC-RR4 determinism x2", a == b, f"{len(a)} bytes, twice")

        # ---- halt guards ------------------------------------------------
        home.unlink()  # tracked, now absent from the worktree
        try:
            build()
            check("HALT on unstaged deletion", False, "did NOT halt")
        except SystemExit as exc:
            check("HALT on unstaged deletion", "T-HOME.md" in str(exc),
                  str(exc)[:70])
        # A SUBDIRECTORY OF THE REPO IS NOT A NEGATIVE CONTROL FOR "NOT A REPO".
        # The first cut pointed this at `tmp/not-a-git-repo`, which is INSIDE
        # the fixture repo -- `git ls-files` succeeded there and returned
        # nothing, so it exercised the empty-set halt and merely LOOKED like a
        # git-failure control. Aim it at a directory outside every repo.
        (tmp / "empty-but-tracked").mkdir()
        REPO_ROOT, DOCS = tmp / "empty-but-tracked", tmp / "empty-but-tracked"
        try:
            build()
            check("HALT when the tracked set is empty", False, "did NOT halt")
        except SystemExit as exc:
            check("HALT when the tracked set is empty",
                  "no TRACKED markdown" in str(exc), str(exc)[:70])

        outside = Path(tempfile.mkdtemp(prefix="ruling-registry-nonrepo-"))
        try:
            REPO_ROOT, DOCS = outside, outside / "docs"
            try:
                build()
                check("HALT when git enumeration fails", False, "did NOT halt")
            except SystemExit as exc:
                check("HALT when git enumeration fails",
                      "ls-files` failed" in str(exc), str(exc)[:70])
        finally:
            shutil.rmtree(outside, ignore_errors=True)
    finally:
        REPO_ROOT, DOCS = real_root, real_docs
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- NC-RR3: the REAL repo's genuine rulings still resolve ----------
    # Read-only. These are Captain-ratified references that the tracked-only
    # boundary must not disturb: the locality amendments and two short ids
    # that untracked papers were falsely corroborating.
    reg = build()
    for rid, doc in (("A1", "B-MIGRATION-DISCOVERY.md"),
                     ("A2", "B-MIGRATION-DISCOVERY.md"),
                     ("A3", "B-MIGRATION-DISCOVERY.md"),
                     ("A4", "B-MIGRATION-DISCOVERY.md"),
                     ("R5", "B-MIGRATION-DISCOVERY.md"),
                     ("R8", "B-MIGRATION-DISCOVERY.md")):
        occ = [o for o in reg["rulings"].get(rid, []) if o["doc"] == doc]
        check(f"NC-RR3 genuine {rid} resolves in {doc}", bool(occ),
              occ[0]["statement"][:64] if occ else "MISSING")

    print("=" * 70)
    if failures:
        print(f"SELFTEST RED — {len(failures)} control(s) failed: {failures}")
        return 1
    print("SELFTEST GREEN — the boundary is negative-controlled, and NC-RR5")
    print("shows it catches the substitution the aggregate ratchet cannot.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", metavar="DOC", help="is DOC safe to delete?")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the tracked-doc population boundary can fail")
    ap.add_argument("--update-baseline", action="store_true",
                    help="pin the CURRENT registry counts as the baseline")
    ap.add_argument("--check-only", action="store_true",
                    help="read-only: build the registry, derive the same metrics and "
                         "run the same ratchet comparison, but write neither output "
                         "and touch no tracked file. What Gate 2 runs. Distinct from "
                         "--check DOC, which asks about ONE document's deletability.")
    args = ap.parse_args()

    if args.check_only and args.update_baseline:
        # Contradictory rather than redundant: --update-baseline WRITES the ratchet.
        print("HALT: --check-only and --update-baseline contradict each other. "
              "--check-only writes nothing; --update-baseline exists to write the "
              "ratchet.", file=sys.stderr)
        return 2

    if args.selftest:
        return _selftest()

    reg = build()

    if args.check:
        name = Path(args.check).name
        d = reg["per_doc"].get(name)
        if d is None:
            # Exit status unchanged (2). The wording names the real reason:
            # since 2026-08-15 an UNTRACKED docs/*.md is not in the population,
            # so "not found" alone would read as "no such file".
            print(f"HALT: {name} is not a TRACKED document under docs/ "
                  f"(stage it first, or check the name)", file=sys.stderr)
            return 2
        if not d["deletion_blocked"]:
            print(f"SAFE: {name} — {len(d['ruling_ids'])} ruling(s), all "
                  f"recorded elsewhere.")
            return 0
        print(f"BLOCKED: {name} is the sole home of "
              f"{len(d['sole_home_for'])} ruling(s):")
        for rid in d["sole_home_for"]:
            occ = reg["rulings"][rid][0]
            print(f"  {rid:14s} line {occ['line']:5d}  {occ['statement'][:90]}")
        return 1

    written = emit_outputs(reg, emit=not args.check_only)

    # ADD-06: print the exact block a commit message should carry.
    print("=" * 62)
    print("RULING REGISTRY")
    print(f"  documents scanned      {reg['generated_from']}")
    print(f"  ruling references      {reg['total_references']}")
    print(f"  distinct ruling ids    {reg['distinct_rulings']}")
    print(f"  corroborated (>1 doc)  {reg['corroborated']}")
    print(f"  sole-home (1 doc only) {reg['sole_home']}")
    blocked = sorted(
        n for n in reg["per_doc"] if reg["per_doc"][n]["deletion_blocked"]
    )
    clean = sorted(
        n for n in reg["per_doc"]
        if reg["per_doc"][n]["ruling_ids"] and not reg["per_doc"][n]["deletion_blocked"]
    )
    print(f"  docs deletion-BLOCKED  {len(blocked)}")
    print(f"  docs deletable         {len(clean)}")
    print("=" * 62)
    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    if not written:
        print("read-only (--check-only): no output written, nothing mutated")

    # THIS FILE NOTICED AND DID NOT GATE. Negative-controlled 2026-08-09
    # (`docs/SYSTEM-SELF-TEST-2026-08-09.md`): a sole-home ruling document was
    # hidden, the registry's own numbers MOVED (sole-home 43 -> 44), and it
    # exited 0 with no complaint. A ruling document could be deleted and
    # nothing in the repo would say so -- which is precisely the loss this
    # registry exists to make impossible.
    #
    # Ratcheted on the same mechanism as conservation and visibility: a FALL in
    # documents / distinct rulings / corroboration is a silent loss and is
    # fatal; a RISE in sole-home means a ruling lost its corroborating home.
    # `generated_from` is a DESCRIPTIVE STRING ("120 documents under docs/"),
    # not a count. Pinning it made the ratchet compare strings: equal-or-not
    # worked, but any real change would reach `b - a` on two strings and raise
    # instead of reporting. Pin the integer the string is describing.
    metrics = {"documents": len(reg["per_doc"]),
               "ruling_ids": reg["distinct_rulings"],
               "total_references": reg["total_references"],
               "corroborated": reg["corroborated"],
               "sole_home": reg["sole_home"]}
    print("\n" + "=" * 62)
    print("BASELINE — ruling registry")
    print("=" * 62)
    return 1 if ratchet.report(RATCHET_BASELINE, "ruling_registry", metrics,
                               args.update_baseline) else 0


if __name__ == "__main__":
    raise SystemExit(main())
