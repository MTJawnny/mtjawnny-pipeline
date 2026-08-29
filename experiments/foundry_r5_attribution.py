#!/usr/bin/env python3
"""ATTRIBUTE THE R5 DRIFT — which codebook mutation moved `EXPECTED_R5_ROWS`?

`docs/A15-VOCAB-01-RULING-2026-08-09.md` §8b. Session 2a halts because
`EXPECTED_R5_ROWS = 141` (measured 2026-08-02, CDR-03) no longer reproduces.
Re-derived 2026-08-09: **166** before this session's rename, 163 after. The
drift predates the session and had no attributed cause, and R5 is the lane
CDR-03 routes to DET–SYNTH contradiction and human review — so it is the one
premise that must not be re-derived on faith.

HOW IT WORKS
------------
An R5 row is a distinct `(slug, oracle_id)` where a run-1 FREE-LANE label is
literally equal to an ACTIVE axis slug (`classify_r5`). The run-1 label data is
fixed and committed; the only moving input is **which slugs are active**. So
the count is a pure function of the codebook, and the backup series
(`experiments/out/foundry/backups/`) is a recorded history of that input.

This replays `classify_r5` against every backup, in file order, and reports the
row count and the exact rows that enter or leave at each step. It decides
nothing and mutates nothing.

WHY IT SWAPS THE LIVE FILE
--------------------------
`foundry_consolidate_run1` reads `codebook.json` by module-level constant.
Rather than reach into its internals, this swaps the file, runs, and restores —
verifying the live sha256 before and after, and restoring in a `finally` so an
exception cannot leave a backup in place. The live file is captured to the
scratch dir first and compared byte-for-byte at the end.

    python3 experiments/foundry_r5_attribution.py
    python3 experiments/foundry_r5_attribution.py --verbose   # name every row
"""
import argparse
import contextlib
import datetime
import hashlib
import io
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                       # noqa: E402
import foundry_codebook as fcb                    # noqa: E402

BACKUPS = fc.FOUNDRY_OUT_DIR / "backups"
LIVE = fcb.CODEBOOK_PATH


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# THE BACKUPS DO NOT SORT CHRONOLOGICALLY BY NAME, and the first version of
# this file sorted them with `sorted()`. The timestamp sits in a DIFFERENT
# POSITION in each naming era --
#   codebook.v0.7.pre-b-migration.20260802-010714.json      (trailing, dashed)
#   codebook.pre-any-damage-split.20260802-172906.json      (trailing, dashed)
#   codebook.20260809T182220.pre-…-rename.json              (leading, T-form)
#   codebook.20260809T204918Z.json                          (leading, T+Z)
# -- so an alphabetical sort interleaves 2026-08-02 and 2026-08-09 states and
# every delta is computed between NON-ADJACENT codebooks. The counts stay
# correct; the ATTRIBUTION becomes fiction. Same family as the handoff picked
# by filename sort in SESSION-START-PROCEDURE Gate 1.
#
# AND THE TWO ERAS DISAGREE ABOUT THE TIMEZONE. `foundry_membership_move.py`
# writes UTC with a trailing `Z`; the ad-hoc backups (including this session's)
# use LOCAL time with no marker. Sorting the digits as strings therefore mixes
# UTC and local and reorders 2026-08-09 against itself -- measured: it put a
# 20:49**Z** backup (13:49 local) AFTER an 18:22 local one, producing a
# 166 → 156 → 166 bounce that is not a history at all. mtime cannot rescue it
# either: `shutil.copy2` preserves the SOURCE mtime, so a backup carries the
# mtime of the codebook it copied, not of the moment it was taken.
_TS = re.compile(r"(\d{8})[T-](\d{6})(Z?)")
_LOCAL = datetime.datetime.now().astimezone().tzinfo


def backup_time(p: Path) -> datetime.datetime:
    """Absolute instant a backup was taken, tz-normalized. Sorting key."""
    m = _TS.search(p.name)
    if not m:
        fc.halt(f"backup {p.name!r} carries no parseable timestamp. Sorting it "
                f"by name would place it arbitrarily in the history and the "
                f"deltas either side of it would be attributed to the wrong "
                f"mutation.")
    day, clock, zulu = m.groups()
    naive = datetime.datetime.strptime(day + clock, "%Y%m%d%H%M%S")
    tz = datetime.timezone.utc if zulu else _LOCAL
    return naive.replace(tzinfo=tz).astimezone(datetime.timezone.utc)


def a15_sizes_for_current_codebook():
    """A15 cluster sizes under whatever codebook is live NOW.

    Included because `EXPECTED_A15_ROWS` drifted 213 -> 194 in the same window
    and the two lanes draw from ONE population: `classify_a15` buckets
    `result["free_pool"]`, and `build_discovery_artifact` runs first. So a
    label that becomes an exact match to a newly-active slug can leave a
    cluster. Measuring both lanes on the same axis is what turns two separate
    "unexplained drifts" into one accounted-for re-partition -- or proves they
    are unrelated, which is equally worth knowing.
    """
    import importlib
    import foundry_consolidate_run1 as run1
    import foundry_consolidate_run1_classify as clf
    importlib.reload(run1)
    importlib.reload(clf)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = run1.classify_run1_instances()
        discovery, _exact, _near = run1.build_discovery_artifact(result)
        try:
            out = clf.classify_a15(discovery, result)
            clusters = out[1]   # (rows, cluster_summary, …) — index, never unpack:
                                # the arity changed once already and a strict unpack
                                # turns a shape change into a crash mid-replay.
        except SystemExit:
            return None
    return {c["cluster"]: c["rows"] for c in clusters}


def r5_rows_for_current_codebook():
    """Replay 2a's own R5 derivation against whatever codebook is live NOW.

    Imports are reloaded because both modules cache the codebook at module
    scope; without the reload every backup would score the FIRST one's numbers
    and the whole report would read as 'nothing ever moved'.
    """
    import importlib
    import foundry_consolidate_run1 as run1
    import foundry_consolidate_run1_classify as clf
    importlib.reload(run1)
    importlib.reload(clf)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = run1.classify_run1_instances()
        _discovery, exact_match, _near = run1.build_discovery_artifact(result)
        rows = clf.classify_r5(exact_match, result)
    return {(r["slug"], r["oracle_id"]): r for r in rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="name every row that enters or leaves")
    args = ap.parse_args()

    backups = sorted(BACKUPS.glob("codebook*.json"), key=backup_time)
    if not backups:
        fc.halt(f"no codebook backups under {BACKUPS}. The attribution is a "
                f"replay over recorded history; with no history there is "
                f"nothing to attribute and a clean run would be a lie.")

    live_sha = sha(LIVE)
    stash = Path(tempfile.mkdtemp(prefix="r5attr-")) / "codebook.live.json"
    shutil.copy2(LIVE, stash)

    print("=" * 78)
    print("R5 ATTRIBUTION — replaying classify_r5 over the backup series")
    print("=" * 78)
    print(f"  live codebook sha256 {live_sha[:16]}…  stashed to {stash}")
    print(f"  CDR-03's measured value, 2026-08-02: EXPECTED_R5_ROWS = 141")
    print()

    results = []
    try:
        for b in backups + [stash]:
            shutil.copy2(b, LIVE)
            try:
                rows = r5_rows_for_current_codebook()
                a15 = a15_sizes_for_current_codebook()
            except SystemExit as e:
                print(f"  {b.name:<62} HALTED ({e})")
                results.append((b.name, None, None, None))
                continue
            label = "LIVE (now)" if b == stash else f"{backup_time(b).astimezone().strftime('%m-%d %H:%M')} {b.name[:50]}"
            results.append((label, len(rows), rows, a15))
    finally:
        shutil.copy2(stash, LIVE)
        after = sha(LIVE)
        print()
        print(f"  live codebook restored: "
              f"{'YES' if after == live_sha else 'NO — sha256 MISMATCH'}")
        if after != live_sha:
            fc.halt("the live codebook was not restored byte-for-byte. Restore "
                    f"it from {stash} before doing anything else.")

    print()
    print(f"{'codebook state':<64}{'R5':>5}  {'Δ':>5}")
    print("-" * 78)
    prev_rows, prev_n, prev_a15 = None, None, None
    for name, n, rows, a15 in results:
        if n is None:
            continue
        delta = "" if prev_n is None else f"{n - prev_n:+d}"
        mark = "  <<<" if prev_n is not None and n != prev_n else ""
        print(f"{name:<64}{n:>5}  {delta:>5}{mark}")
        if prev_rows is not None and rows.keys() != prev_rows.keys():
            gained = sorted(rows.keys() - prev_rows.keys())
            lost = sorted(prev_rows.keys() - rows.keys())
            for slug, oid in (gained if args.verbose else gained[:6]):
                print(f"        + {slug:<46} {rows[(slug, oid)]['card_name']}")
            if not args.verbose and len(gained) > 6:
                print(f"        + … {len(gained) - 6} more (use --verbose)")
            for slug, oid in (lost if args.verbose else lost[:6]):
                print(f"        - {slug:<46} {prev_rows[(slug, oid)]['card_name']}")
            if not args.verbose and len(lost) > 6:
                print(f"        - … {len(lost) - 6} more (use --verbose)")
        if a15 is not None and prev_a15 is not None and a15 != prev_a15:
            for k in sorted(set(a15) | set(prev_a15)):
                if a15.get(k) != prev_a15.get(k):
                    print(f"        A15 {k:<40} {prev_a15.get(k)} -> {a15.get(k)}")
        prev_rows, prev_n = rows, n
        if a15 is not None:
            prev_a15 = a15

    print()
    print("=" * 78)
    print("READ THE ROWS, NOT THE DELTA. A row entering R5 means a free-lane")
    print("run-1 label now equals an ACTIVE slug that did not exist before —")
    print("which is the codebook growing into the model's vocabulary, not the")
    print("model changing its mind. A row LEAVING means its axis stopped being")
    print("active under that name (a rename or a kill).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
