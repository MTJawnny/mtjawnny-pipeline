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
  3. HISTORICAL CODE -- the same two source shapes over the ARCHIVED D4 triage
              set. Archiving relocates history; it must not delete the ability
              to discover it. Reported as EVIDENCE of a past build, never as a
              runnable successor.
  4. ORPHANS -- a named artifact that a doc calls RATIFIED but which has no
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
# The boundary above already put `src` on the path; this asks the ratified owner
# of repository layout where the archived triage set lives instead of spelling a
# second root arithmetic here. Same idiom as `foundry_cr_checks` and
# `foundry_object_lattice`.
from mtj_foundry.paths import ProjectPaths  # noqa: E402

DOCS = fc.REPO_ROOT / "docs"
CODE = fc.REPO_ROOT / "experiments"

# S15.D4.R2 -- THE ARCHIVE IS STILL EVIDENCE.
#
# S15.D4 moved thirteen batch triage scripts out of `experiments/` into the
# archive byte-for-byte. Nothing about this reader changed -- its blob is
# identical either side of that commit -- but its code-evidence population is the
# single directory `CODE`, so the move carried seven real `def` sites out of
# scan range and
#     foundry_prior_art.py resolve_removed_members --strict
# went from a refusal (exit 1, seven artifacts) to a silent success (exit 0).
# A hard failure had quietly become a success, which is the one conversion this
# repository's governing principle never permits: the move was plumbing, the
# refusal was truth.
#
# The owner is asked for the destination rather than told it, so re-pointing the
# archive re-points this reader too. ONE archive family is added, deliberately:
# the D4 triage set that regressed. This is not a general fix for every earlier
# or future archive migration and must not be read as one.
_LAYOUT = ProjectPaths.for_root(fc.REPO_ROOT)
ARCHIVE_TRIAGE = _LAYOUT.archive_research_triage

# S15.D5.R1 -- THE SAME LOSS HAD ALREADY HAPPENED TWICE BEFORE D4.
#
# D4.R2 repaired ONE family and said so in the comment above. That was accurate
# and it was also incomplete: S15.D3 archived the three Batch-8 research scripts
# and S15.D6 archived the `/1 -> /2` migration pair, both BEFORE this arm
# existed, so both were already invisible here. Measured at the D4.R2 head, with
# the definitions demonstrably present in the archived files:
#     agreement matrix / tail decay check / score pairs   -> exit 0, no artifact
#     replay attribution / project through renames        -> exit 0, no artifact
# "No prior art" was being reported for code that is sitting in the repository.
# Same conversion, same principle, two families older.
#
# The fix is an EXPLICIT list, not a recursive walk. `archive/research/**` would
# make every future directory prior art by accident -- the opposite of the
# bounded-population discipline `_tracked_archive_sources` exists to enforce --
# and it would let an unrelated family answer a topic query with evidence that
# was never authorized as evidence. Each entry names an owner property (so the
# layout owner still decides where the family lives) and the human-readable
# label its hits are reported under, because a Batch-8 match described as triage
# is a provenance lie even when the path printed beside it is correct.
#
# A later task adds ONE tuple here for its own ratified owner. That is the whole
# extension mechanism; nothing about the scope becomes automatic.
#
# `_LAYOUT` is the SAME `for_root` call `ARCHIVE_TRIAGE` already made, reused
# rather than repeated. A second call would add a real root-delegation site and
# move three values inside the already-failing layout-delegation census, for no
# behavioural gain; the raw-textual arm of that census counts the token itself,
# so this note avoids spelling it too. This repair moves none of those values.
HISTORICAL_FAMILIES = (
    (ARCHIVE_TRIAGE, "archived triage set"),
    (_LAYOUT.archive_research_batch8, "archived Batch-8 research set"),
    (_LAYOUT.archive_research_mutations,
     "archived foundry-codebook/1 -> /2 migration pair"),
)

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


def code_shapes(flexible: str) -> tuple:
    """The two source shapes a topic can ALREADY EXIST as: a definition and a
    constant.

    Spelled once and consumed by both the live search and the historical one.
    Two copies would let the populations drift apart in what they even look
    for, and a historical search that asked a narrower question than the live
    one would report "nothing here" for a reason that has nothing to do with
    the archive."""
    return (rf"^\s*def\s+[a-z_]*{flexible}",
            rf"^[A-Z_]*{flexible.upper()}[A-Z_]*\s*=")


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


def _git(root: Path, *argv: str) -> str:
    """One git query about `root`, with every failure LOUD.

    An enumeration that breaks and returns nothing is indistinguishable, at the
    call site, from a topic that genuinely has no prior art. This repair exists
    precisely because a missing population once read as a clean result, so the
    two are never allowed to share an exit path."""
    try:
        r = subprocess.run(["git", "-C", str(root), *argv],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        fc.halt(f"could not query git about {root}: {e}. This is a broken "
                f"enumeration, not an absence of prior art, and the two must "
                f"never be reported the same way.")
    if r.returncode != 0:
        fc.halt(f"git {argv[0]} exited {r.returncode} under {root}: "
                f"{r.stderr.strip()}. Refusing to report zero historical "
                f"matches on the strength of a failed enumeration.")
    return r.stdout


def _tracked_archive_sources(root: Path) -> tuple:
    """`(repository root, sorted repository-relative tracked paths)` under `root`.

    TRACKED, not globbed, and that is the whole point. The live search greps a
    DIRECTORY, so anything sitting in one counts -- including the multi-gigabyte
    ignored `experiments/out/` tree. Historical evidence has to be the opposite:
    a planted or ignored file must never become prior art, and the same commit
    must always yield the same population. `git ls-files` is the only
    enumeration that gives both.

    The repository is derived FROM `root` rather than assumed to be this
    checkout, so the population and every one of its failure modes can be
    exercised against a disposable fixture repository instead of this one."""
    top = Path(_git(root, "rev-parse", "--show-toplevel").strip())
    listed = _git(root, "ls-files", "-z", "--full-name", "--", ".")
    paths = sorted(p for p in listed.split("\0") if p)
    if not paths:
        fc.halt(f"no tracked historical source found under {root}. That "
                f"population is REQUIRED evidence at this commit, so an empty "
                f"one is a damaged or re-pointed archive -- not a topic miss.")
    return top, paths


def _historical_code(flexible: str, root: Path) -> list:
    """(path, lineno, text) for the two code shapes across the archived set.

    TEXT ONLY. The archived programs are read as bytes and matched with a
    regex; nothing here imports, compiles, evaluates, executes or repairs them.
    They are inert history, and a prior-art probe that ran them in order to find
    out what they contain would be a far worse defect than the one it fixes."""
    shapes = [re.compile(s, re.I) for s in code_shapes(flexible)]
    top, paths = _tracked_archive_sources(root)
    hits = []
    for rel in paths:
        path = top / rel
        if path.is_symlink():
            fc.halt(f"tracked historical source {rel} is a symlink; refusing to "
                    f"follow it out of the archive and into whatever it points "
                    f"at.")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            fc.halt(f"cannot read required tracked historical source {rel}: "
                    f"{e}. Missing or damaged evidence is not the same event as "
                    f"a topic with no prior art.")
        for n, line in enumerate(text.splitlines(), 1):
            if any(s.search(line) for s in shapes):
                hits.append((rel, str(n), line.strip()))
    return hits


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
        definition, constant = code_shapes(flexible)
        code = _grep(definition, CODE)
        code += _grep(constant, CODE)
        if code:
            found_any = True
            print(f"\n  ⚠ {len(code)} EXISTING CODE ARTIFACT(S) — do not rebuild:")
            for p, n, t in code[:args.limit]:
                print(f"     {p.replace(str(REPO_ROOT.parent) + '/', '')}:{n}  {t[:100]}")

        # 3. HISTORICAL CODE -- was it built once, and then archived?
        # One family at a time, each reported under its OWN label. The results
        # are deliberately not concatenated first: a single merged list would
        # have to be printed under one family's name, and every hit from the
        # other families would then carry a false provenance.
        for owner, label in HISTORICAL_FAMILIES:
            historical = _historical_code(flexible, owner)
            if not historical:
                continue
            found_any = True
            print(f"\n  ⚠ {len(historical)} HISTORICAL CODE ARTIFACT(S) in the "
                  f"{label} — this was already built once. Read it "
                  f"as EVIDENCE: it is inert history, not a runnable successor, "
                  f"and this is not an instruction to execute an archived "
                  f"program:")
            for p, n, t in historical[:args.limit]:
                print(f"     {p}:{n}  {t[:100]}")
            if len(historical) > args.limit:
                print(f"     … and {len(historical) - args.limit} more")
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
