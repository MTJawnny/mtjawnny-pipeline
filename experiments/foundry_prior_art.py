#!/usr/bin/env python3
"""PRIOR-ART PROBE -- Gate 3 for everything that is not a slug. Zero tokens.

WHY THIS EXISTS
---------------
Captain, 2026-08-04: *"if we were able to genuinely solve issues with already
built architecture, why did we not reference it in the first place? Maybe we
have some sort of mechanism that demands making calls to the already worked
material."*

Right, and the gap is exact. `foundry_slug_dossier.py` (Gate 3) exists because a
bare grep was PROVEN insufficient for slugs -- 77 of 328 active axes carry their
ruling under a former name. But it keys on a SLUG. Nothing keys on a TOPIC, a
POPULATION, a MEASUREMENT or a CODE HELPER, so on 2026-08-04 a session
rediscovered four things the project had already decided:

  det_scan_texts()          the RATIFIED DET preprocessing standard v1, called
                            by six tools -- and not by the shape extractor
  expand_modal_bullets()    written, ratified 2026-07-31, zero callers in the
                            extractor; its absence cost 504 lines
  "Ward 206 · Cumulative Upkeep 80 · Echo 50"
                            already measured and ranked in
                            DELIVERY-VOCABULARY-BATCH-2026-08-03 §6
  keyword ledger            KEYWORD-LEDGER-CANDIDATES.md already carries the
                            SUP-protocol rule that bare keywords are never axes

Every one was findable. None was findable BY THE PROCEDURE, because the
procedure pushes context (a hand-written READING MANIFEST from the previous
session) instead of letting the current task pull it.

WHAT IT DOES
------------
For a topic, it reports in one pass:
  1. DOCS  -- every mention across docs/ and docs/archive/, ruling lines
              separated from prose, exactly as the slug dossier does
  2. CODE  -- existing helpers whose NAME matches, so a session builds nothing
              that is already built
  3. ORPHANS -- a named artifact that a doc calls RATIFIED but which has no
              caller anywhere. This generalises the family sweep's existing
              BLOCKING check `ratified-pattern-has-no-axis`, whose own message
              names this exact failure: *"demotes it to the prefilter list
              without a halt, so it has never been applied."* The project
              already understood the shape -- it was only ever wired for DET
              patterns.

It judges nothing. `--strict` exits 1 when prior art exists, so a batch pass can
be gated on it.

USAGE
  python3 experiments/foundry_prior_art.py ward "cumulative upkeep"
  python3 experiments/foundry_prior_art.py modal bullet --strict
  python3 experiments/foundry_prior_art.py --orphans
"""
import re
import sys
import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

DOCS = fc.REPO_ROOT / "docs"
CODE = fc.REPO_ROOT / "experiments"

# Same idiom as foundry_slug_dossier.py -- a line that carries a VERDICT is not
# the same kind of evidence as a line that merely mentions the topic.
RULED = re.compile(
    r"\bVERDICT\b|\bRATIFIED\b|\bCaptain[- ]ratified\b|\bCaptain\b.*\bruled\b"
    r"|\bKEEP\b|\bKILL\b|\bMERGE\b|\bstanding rule\b|\bnever\b.*\baxes\b", re.I)

# A doc naming a code artifact as ratified: `foo_bar()`, `foo_bar.py`, or
# `experiments/foo.py`. Used for the orphan check.
ARTIFACT = re.compile(r"`([a-z_][a-z0-9_]{3,}(?:\(\)|\.py|\.json|\.yaml))`")

NOISE = ("docs/mtg-comprehensive-rules.md", "docs/RATIFIED-RULINGS-REGISTRY.md")


def flexible_pattern(topic: str) -> str:
    """A topic matches across the spelling drift the docs actually contain.

    Measured: the modal-bullet decision is written FIVE ways -- `modal-bullet`,
    `modal_bullets`, `modal bullets`, `expand_modal_bullets`, "modal 'choose
    one —'". A literal search finds one of them, which is exactly how a settled
    question gets rediscovered.

    NB: do NOT `re.escape` the whole topic first. re.escape() escapes the space,
    and substituting the separator afterwards then leaves a stray backslash
    welded to the character class (`modal\\[-_ ]bullet`), which silently matches
    a literal `[`. That bug made this tool report "0 mentions" on the very case
    it was built for -- Gate 4, on the gate."""
    words = [w for w in re.split(r"[^A-Za-z0-9]+", topic) if w]
    if not words:
        fc.halt(f"topic {topic!r} contains no searchable words")
    # trailing [a-z]* so `bullet` also finds `bullets`, `splitting` finds `split`
    return r"[-_ ]?".join(re.escape(w) for w in words) + r"[a-z]*"


def _grep(pattern: str, root: Path) -> list:
    """(path, lineno, text) for every match. Uses grep so archive/ is included
    and the cost stays flat as docs/ grows."""
    try:
        r = subprocess.run(["grep", "-rniE", pattern, str(root)],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        fc.halt(f"grep failed on {root}: {e}")
    out = []
    for line in r.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        p = parts[0]
        if any(n in p for n in NOISE) or "/__pycache__/" in p:
            continue
        out.append((p, parts[1], parts[2].strip()))
    return out


def cmd_topic(args) -> None:
    found_any = False
    for topic in args.topic:
        flexible = flexible_pattern(topic)
        hits = _grep(rf"\b{flexible}", DOCS)
        ruling = [h for h in hits if RULED.search(h[2])]
        prose = [h for h in hits if not RULED.search(h[2])]

        print("=" * 78)
        print(f"TOPIC: {topic!r}")
        print("=" * 78)
        print(f"  docs mentions: {len(hits)}   ruling-bearing: {len(ruling)}")

        if ruling:
            found_any = True
            print(f"\n  ⚠ {len(ruling)} RULING-BEARING LINE(S) — read every one "
                  f"before calling this new:")
            for p, n, t in ruling[:args.limit]:
                print(f"     {p.replace(str(DOCS.parent) + '/', '')}:{n}\n        {t[:150]}")
            if len(ruling) > args.limit:
                print(f"     … and {len(ruling) - args.limit} more")

        if prose and args.prose:
            print(f"\n  {len(prose)} prose mention(s):")
            for p, n, t in prose[:args.limit]:
                print(f"     {p.replace(str(DOCS.parent) + '/', '')}:{n}  {t[:110]}")

        # 2. CODE -- is a helper already built?
        code = _grep(rf"^\s*def\s+[a-z_]*{flexible}", CODE)
        code += _grep(rf"^[A-Z_]*{flexible.upper()}[A-Z_]*\s*=", CODE)
        if code:
            found_any = True
            print(f"\n  ⚠ {len(code)} EXISTING CODE ARTIFACT(S) — do not rebuild:")
            for p, n, t in code[:args.limit]:
                print(f"     {p.replace(str(REPO_ROOT.parent) + '/', '')}:{n}  {t[:100]}")
        print()

    if args.strict and found_any:
        fc.halt("Prior art exists for at least one topic. This is not a defect "
                "until you can say which prior decision your finding overturns "
                "and why — the Gate 3 rule, applied to topics.")


# The ratified DET preprocessing standard v1 (2026-07-31): CARDNAME
# canonicalization + modal-mode splitting + all-faces, in ONE pipeline.
RATIFIED_PIPELINE = "det_scan_texts"
# A module that reads a card's printed text is a CONSUMER of that standard.
READS_CARD_TEXT = re.compile(r"\b(full_oracle_text|oracle_text|get_raw_faces)\b")


def cmd_orphans(args) -> None:
    """Which consumers of card text BYPASS the ratified preprocessing pipeline?

    This is the check that would have caught 2026-08-04's root cause.
    `expand_modal_bullets` was not an orphan in the naive sense -- it HAS a
    caller, `det_scan_texts`. The defect was one level up: the shape extractor
    reads card text and never goes through that pipeline, so it re-implemented
    the preprocessing and inherited none of the ratified fixes.

    Generalises the family sweep's `ratified-pattern-has-no-axis`, which already
    encodes "a ratified thing nothing applies" for DET patterns and is already
    BLOCKING. The concept existed; it was only ever wired for one artifact type."""
    print("=" * 78)
    print("CONSUMERS OF CARD TEXT vs THE RATIFIED PREPROCESSING PIPELINE")
    print("=" * 78)
    print(f"standard: foundry_common.{RATIFIED_PIPELINE}()  — DET preprocessing")
    print("standard v1, ratified 2026-07-31 (cardname canonicalisation,")
    print("modal-mode splitting, all-faces).\n")

    users, bypassers = [], []
    for path in sorted(CODE.rglob("*.py")):
        if "__pycache__" in str(path) or path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name == "foundry_common.py" or not READS_CARD_TEXT.search(text):
            continue
        (users if RATIFIED_PIPELINE in text else bypassers).append(path.name)

    print(f"  ✓ USE the pipeline ({len(users)}):")
    for n in users:
        print(f"        {n}")
    print(f"\n  ⚠ BYPASS it while still reading card text ({len(bypassers)}):")
    for n in bypassers:
        print(f"        {n}")
    print("\n  A bypasser is not automatically wrong — a line-anchored parser")
    print("  needs per-line granularity the pipeline does not return. But each")
    print("  one re-implements preprocessing, and every such re-implementation")
    print("  is where 2026-08-04's ABILITY_WORD and modal-mode defects lived.")

    if args.strict and bypassers:
        fc.halt(f"{len(bypassers)} module(s) read card text without going "
                f"through {RATIFIED_PIPELINE}().")
    return

    # One pass over the source, not one grep per candidate -- there are ~200
    # candidates and shelling out per name took minutes.
    sources = {}
    for path in sorted(CODE.rglob("*.py")):
        if "__pycache__" in str(path):
            continue
        sources[path] = path.read_text(encoding="utf-8", errors="replace")
    for path in sorted(DOCS.glob("*.json")):
        sources[path] = path.read_text(encoding="utf-8", errors="replace")

    orphans = []
    for name, where in sorted(candidates.items()):
        bare = name.replace("()", "")
        used = False
        for path, text in sources.items():
            for line in text.splitlines():
                if bare not in line:
                    continue
                # A definition is not a use, and neither is the file naming
                # itself. Anything else counts as a caller.
                if re.match(rf"^\s*(def|class)\s+{re.escape(bare)}\b", line):
                    continue
                if path.name == bare:
                    continue
                used = True
                break
            if used:
                break
        if not used:
            orphans.append((name, where))

    if not orphans:
        print("  none found.")
    for name, where in orphans:
        print(f"  ⚠ {name}   — ratified in:")
        for p, n in where[:3]:
            print(f"        {p.replace(str(DOCS.parent) + '/', '')}:{n}")
    print(f"\n  {len(orphans)} orphan(s) of {len(candidates)} ratified artifacts named in docs/")
    if args.strict and orphans:
        fc.halt(f"{len(orphans)} ratified artifact(s) have no caller.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic", nargs="*", help="topic(s) to probe for prior art")
    ap.add_argument("--orphans", action="store_true",
                    help="list ratified artifacts that nothing calls")
    ap.add_argument("--prose", action="store_true", help="also print prose mentions")
    ap.add_argument("--strict", action="store_true", help="exit 1 when prior art exists")
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()
    if args.orphans:
        cmd_orphans(args)
    elif args.topic:
        cmd_topic(args)
    else:
        ap.error("give a topic, or --orphans")


if __name__ == "__main__":
    main()
