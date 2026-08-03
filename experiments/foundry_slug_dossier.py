#!/usr/bin/env python3
"""Slug dossier -- every ratified ruling that governs one axis, in one place.

WHY THIS EXISTS
---------------
Every drift this project has suffered has the same shape: a session writes a
check against ONE law, unaware of a DIFFERENT ratified law governing the same
slug. Measured instances, all 2026-08-02:

  * the CDR-09 derivation knew grammar §8a only. It reported 3 false defects,
    and two of them would have DESTROYED Captain-ratified names
    (`create-token-with-x-counters` is named verbatim in §7;
    `etb-with-negative-counters`' polarity was ruled a parameter in batch-5).
  * the tier-3 re-audit nearly re-raised all three of those again, plus the
    `exiled` participle that CR-VOCABULARY-AUDIT had already cleared.

The standing mitigation is a manual habit -- `grep -rn '<slug>' docs/` -- and a
habit is exactly what failed. `RATIFIED-RULINGS-REGISTRY.md` does not close it
either: that registry is keyed on ruling IDs (D12, CDR-09, A15), not on slugs.

So this tool is the missing index: slug -> every ruling that touches it.

THE PART THAT MATTERS MOST: RENAME CHAINS
-----------------------------------------
A slug's rulings are usually filed under a name it no longer has.
`rule:activated-plus1-counter-transfer-to-other-creature` carries batch-5's
verdict under `activated-counter-transfer-from-other-creature` (pre-CDR-09) and
tier-2 D1's under `-from-other-creature`. Grep the current name and you find
neither. This tool walks the codebook's own rename history and greps EVERY name
the axis has ever had -- which is the step a session cannot be relied on to
remember.

Read-only. Zero tokens. Judges nothing; it assembles what a human must read.

Usage:
  python3 experiments/foundry_slug_dossier.py <slug>          # one axis
  python3 experiments/foundry_slug_dossier.py <slug> --strict # exit 1 if ruled
  python3 experiments/foundry_slug_dossier.py --audit         # coverage report
"""
import re
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_codebook as fcb  # noqa: E402

DOCS = REPO_ROOT.parent / "docs"

# Documents whose word is LAW, in descending authority. A hit in one of these
# is not "context" -- it is a ruling, and re-deciding it is the drift.
AUTHORITY = [
    ("RATIFIED DIRECTIVE", re.compile(
        r"RATIFIED-DIRECTIVES-BATCH|TRIAGE-BATCH-\d+\.md$")),
    ("GRAMMAR LAW", re.compile(r"CODEBOOK-NAMING-GRAMMAR\.md$")),
    ("WALK RATIFICATION", re.compile(
        r"WALK-RATIFICATION-EXECUTION-HANDOFF|CORPUS-PASS-WALK-RATIFICATION")),
    ("DECISION PACKET", re.compile(r"DECISION-PACKET|RATIFICATION-PACKET|-RULING-")),
    ("REGISTRY", re.compile(r"RATIFIED-RULINGS-REGISTRY\.md$")),
]

# Line shapes that mean a decision was MADE, as opposed to discussed.
RULED = re.compile(
    r"\bVERDICT\b|\bRATIFIED\b|\bCaptain[- ]ratified\b|\bCaptain\b.*\bruled\b"
    r"|^\s*###?\s*D-?\d+|\bKEEP\b|\bKILL\b|\bMERGE\b|\bDEFER\b|\bRENAME",
    re.I)


def authority_of(path: Path) -> str:
    rel = str(path)
    for label, rx in AUTHORITY:
        if rx.search(rel):
            return label
    return "working record"


def all_names(cb: dict, slug: str) -> list:
    """Every name this axis has ever had, walking rename edges BOTH ways.

    Forward:  a tombstone's `renamed_to` points at the successor.
    Backward: a successor's history carries 'renamed from <old>'.
    Both directions matter -- a session may hold either end of the chain.
    """
    axes = cb["axes"]
    seen, frontier = set(), [slug]
    back = re.compile(r"renamed from (rule:[a-z0-9-]+)")
    while frontier:
        cur = frontier.pop()
        if cur in seen:
            continue
        seen.add(cur)
        e = axes.get(cur)
        if not e:
            continue
        nxt = e.get("renamed_to") or e.get("merged_into")
        if nxt:
            frontier.append(nxt)
        for h in e.get("history", []):
            for m in back.finditer(h.get("note", "") or ""):
                frontier.append(m.group(1))
        # anyone pointing AT us
        for other, oe in axes.items():
            if oe.get("renamed_to") == cur or oe.get("merged_into") == cur:
                frontier.append(other)
    return sorted(seen)


def scan(names: list) -> list:
    """Grep docs/ and docs/archive/ for every name. Returns hit records."""
    bare = {n.split(":", 1)[-1] for n in names}
    hits = []
    for path in sorted(DOCS.rglob("*.md")):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            for b in bare:
                # word-ish boundary: avoid matching a longer sibling slug
                if re.search(rf"(?<![a-z0-9-]){re.escape(b)}(?![a-z0-9-])", line):
                    hits.append({
                        "path": path.relative_to(DOCS.parent),
                        "line": i,
                        "text": line.strip(),
                        "name": b,
                        "authority": authority_of(path),
                        "ruled": bool(RULED.search(line)),
                    })
                    break
    return hits


ORDER = {lbl: i for i, (lbl, _) in enumerate(AUTHORITY)}


def report(cb, slug, hits, names):
    e = cb["axes"].get(slug)
    print("=" * 72)
    print(f"DOSSIER  {slug}")
    print("=" * 72)
    if e:
        print(f"  status {e.get('status')}  ·  n={len(e.get('members', []))}"
              f"  ·  scope={e.get('scope')}  ·  source={e.get('source')}")
    else:
        print("  NOT IN CODEBOOK (never existed, or the name is misspelled)")
    if len(names) > 1:
        print(f"\n  RENAME CHAIN — rulings may be filed under ANY of these:")
        for n in names:
            st = cb["axes"].get(n, {}).get("status", "—")
            print(f"    · {n}  [{st}]")

    ruled = [h for h in hits if h["ruled"] and h["authority"] != "working record"]
    other_auth = [h for h in hits if not h["ruled"] and h["authority"] != "working record"]
    prose = [h for h in hits if h["authority"] == "working record"]

    print(f"\n  {len(hits)} hits across {len({h['path'] for h in hits})} documents")
    print(f"    {len(ruled)} carry a RULING on a law-bearing document")

    if ruled:
        print("\n" + "-" * 72)
        print("RULINGS — re-deciding any of these is the drift this tool exists to stop")
        print("-" * 72)
        for h in sorted(ruled, key=lambda h: (ORDER.get(h["authority"], 9), str(h["path"]))):
            print(f"\n  [{h['authority']}] {h['path']}:{h['line']}")
            print(f"      {h['text'][:200]}")

    if other_auth:
        print("\n" + "-" * 72)
        print("LAW-BEARING DOCUMENTS, non-verdict lines — read before concluding")
        print("-" * 72)
        for h in sorted(other_auth, key=lambda h: (ORDER.get(h["authority"], 9), str(h["path"]))):
            print(f"  [{h['authority']}] {h['path']}:{h['line']}  {h['text'][:140]}")

    if prose:
        print(f"\n  ({len(prose)} further hits in working records — "
              f"{', '.join(sorted({h['path'].name for h in prose})[:6])}"
              f"{' …' if len({h['path'].name for h in prose}) > 6 else ''})")

    print()
    if ruled:
        print("  ⚠  THIS SLUG IS RULED. Read every line above before calling it")
        print("     defective. When your check disagrees with a ratified list,")
        print("     suspect the check first.")
    else:
        print("  No ruling found on a law-bearing document. Still read the")
        print("  working-record hits — batch documents hold rulings recorded")
        print("  nowhere else.")
    return len(ruled)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if the slug carries any ruling (for pre-flight gating)")
    ap.add_argument("--audit", action="store_true",
                    help="coverage report: how many active axes are ruled vs unruled")
    args = ap.parse_args()

    cb = fcb.load_codebook()

    if args.audit:
        active = [s for s, e in cb["axes"].items() if e.get("status") == "active"]
        ruled_n = renamed_n = 0
        for s in active:
            names = all_names(cb, s)
            if len(names) > 1:
                renamed_n += 1
            if any(h["ruled"] and h["authority"] != "working record"
                   for h in scan(names)):
                ruled_n += 1
        print(f"active axes                     : {len(active)}")
        print(f"  carrying a ruling             : {ruled_n} "
              f"({100*ruled_n//max(len(active),1)}%)")
        print(f"  with a rename chain (>1 name) : {renamed_n} "
              f"— these are the ones a current-name grep MISSES")
        return

    if not args.slug:
        ap.error("give a slug, or --audit")
    slug = args.slug if args.slug.startswith("rule:") else f"rule:{args.slug}"
    names = all_names(cb, slug)
    n_ruled = report(cb, slug, scan(names), names)
    if args.strict and n_ruled:
        sys.exit(1)


if __name__ == "__main__":
    main()
