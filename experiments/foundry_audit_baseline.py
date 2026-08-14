#!/usr/bin/env python3
"""A PINNED BASELINE for the standing audits — so DEGRADATION is fatal, not
merely printed.

Both new mechanisms exit 0 on any amount of degradation. The conservation
audit's recall-inversion table has no pinned thresholds, its descriptor
histogram is printed and never asserted, and the visibility audit's UNCONTEXTED
count is explicitly non-fatal and unbounded. A change that took uncontexted
from 33 to 900, or moved 3,000 lines out of a named descriptor into
`spell-or-static`, passed both audits green.

The absolute checks they already make are the right ones and are unchanged.
This adds the relative half.

**Why a RATCHET and not a tolerance.** "Every scoring constant is a ratified
ruling, not a tuning knob", and a percentage band would be exactly such a knob,
picked by me, gating Captain-ratified work. So there is no band: any movement
in the WORSE direction is fatal, any movement in the better direction is
reported and requires an explicit `--update-baseline` to accept. That is the
same shape as the determinism x2 byte-identical gate -- the standard is
"nothing changed unless you said so", which needs no constant.

**Why the floor matters.** Measured 2026-08-07 against the corpus base rate,
the `comma` class needed +4,213 newly-broken lines to trip the ratio flag and
+2,662 to trip a z=3 flag, because it currently sits well BELOW baseline and
has that much room to fall before it looks abnormal. Against its OWN pinned
rate the floor is 1 line. A class compared to the corpus can hide a defect the
size of a set release; a class compared to itself cannot.

    from foundry_audit_baseline import load, compare, save
"""
import json
from pathlib import Path

BASELINE = Path(__file__).resolve().parent / "out" / "foundry" / "audit-baseline.json"

# For each metric family, the direction that means WORSE. A metric absent here
# is compared for equality only -- unexplained movement in either direction is
# reported, because an audit number that moves for no stated reason is the
# thing this file exists to surface.
#
# These are MARKERS matched as substrings of the whole dotted key, checked
# UP-first. The first version listed full metric names and matched them with
# `startswith` on the leaf segment, which silently classified every NESTED
# metric as neutral: `class_unrouted.comma` was judged on `comma`, and a
# negative control that pushed that class 621 lines the wrong way exited 0.
# The nested metrics are the whole point of pinning -- a per-class unrouted
# count, a per-descriptor histogram -- so they are the ones that must resolve.
WORSE_IF_UP = ("unrouted", "uncontexted", "dropped", "unscanned", "violations",
               "span", "crashed", "mismatch",
               # 2026-08-13, foundry_object_lattice.py: a clause the producer
               # matched but could name no class for. Growing residual is the
               # producer losing ground, and `residual_unexplained` carries the
               # same marker on purpose -- both directions of the residual
               # invariant ratchet the same way.
               "residual",
               # 2026-08-09, foundry_reachability.py: a foundry artifact that
               # goes back to being read only by audits has lost its wire to
               # the product. Checked UP-first, and "orphaned" is not a
               # substring of "reaching", so the two arms cannot collide.
               "orphaned",
               # 2026-08-09: the two Gate 2 checks that were measured
               # INCAPABLE OF FAILING now ratchet here. A new drift finding is
               # worse; a lost ruling document is worse.
               "findings", "sole_home", "unanchored",
               # 2026-08-13, foundry_locality.py: an assertion the resolver
               # addresses to exactly one OWNER whose stored `locality` is
               # ABSENT. Correct value 0, and a rise means addressable evidence
               # lost its metadata.
               #
               # THE MARKER IS THE FULL METRIC NAME ON PURPOSE, not the bare
               # word "missing". Markers match as substrings of the whole
               # dotted key, and `foundry_family_sweep` already emits
               # `missing_from_ratified` while `foundry_batch8_diff` emits
               # `n_missing` and `n_excluded_missing`. None is pinned TODAY, so
               # a bare marker would collide with nothing and then flip three
               # other consumers' metrics from neutral to fatal the day someone
               # pins them -- the `ambiguous` collision the locality handoff
               # recorded, except deferred instead of immediate. A narrow
               # marker cannot do that; the rename hole it opens in exchange is
               # closed by `assert_ratchet_directions()` in foundry_locality.py.
               "addressable_missing")
WORSE_IF_DOWN = ("lines", "deliveries", "keyword_homes", "expansions",
                 "options", "content", "passed", "graded",
                 # 2026-08-09: the count of foundry artifacts that reach a
                 # SHIPPED card. It is 0 today, which is the product audit's
                 # central finding; the ratchet exists so that once it is
                 # non-zero, losing the wire again is fatal rather than
                 # printed. Negative-controlled by
                 # `foundry_reachability.py --selftest`.
                 "reaching",
                 # 2026-08-13: A DETERMINISTIC PRODUCER REGRESSES THROUGH
                 # REMOVALS EXACTLY AS EASILY AS THROUGH ADDITIONS, and only
                 # one of those directions was ever watched. `e780842` removed
                 # 170 object-lattice memberships, verified 83 of them, and
                 # shipped the other 87 unread; 7 were correct memberships that
                 # silently vanished. A membership count that FALLS is now a
                 # regression, so a removal has to be re-pinned ON PURPOSE with
                 # a stated reason, exactly as an addition is reviewed against
                 # the sample sheet. Record:
                 # docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md.
                 "memberships",
                 # 2026-08-13, foundry_locality.py: assertions whose evidence
                 # resolves to exactly one semantic owner. Coverage that FALLS
                 # means the resolver, the corpus or the canonicaliser moved
                 # under existing evidence, which is the one thing locality
                 # must never do silently.
                 #
                 # `ambiguous` was DELIBERATELY NOT added as a marker: it
                 # collides with the pre-existing `ground_truth_wide.
                 # head_ambiguous`, and flipping that metric from neutral to
                 # fatal would change another consumer's semantics as a side
                 # effect. `locality.ambiguous` therefore stays neutral --
                 # reported on any movement, which is enough.
                 #
                 # `locality.span` resolves to WORSE_IF_UP through the
                 # pre-existing "span" marker. That is the correct direction
                 # (more quotes crossing unit boundaries is worse) and is
                 # accepted deliberately rather than by accident.
                 "owned",
                 # a ruling that stops being recorded anywhere, or a document
                 # that vanishes, is a SILENT loss -- the exact thing the
                 # registry exists to prevent and could not report.
                 "documents", "ruling_ids", "corroborated", "blocked")


def load(section: str) -> dict:
    """The pinned numbers for one audit, or None if nothing is pinned yet."""
    if not BASELINE.exists():
        return None
    return json.loads(BASELINE.read_text(encoding="utf-8")).get(section)


def save(section: str, metrics: dict) -> None:
    """Pin `metrics` for `section`, leaving every other section untouched."""
    doc = {}
    if BASELINE.exists():
        doc = json.loads(BASELINE.read_text(encoding="utf-8"))
    doc[section] = metrics
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")


def _direction(key: str) -> int:
    """+1 if a RISE is worse, -1 if a FALL is worse, 0 if any change is notable.

    EVERY segment of the key path is tested, not just the leaf. The first
    version read only the leaf, so `class_unrouted.comma` was judged on
    `comma` -- a name in no direction set -- and a negative control that pushed
    that class 621 lines in the wrong direction exited 0. The nested metrics
    are exactly the ones worth ratcheting (a per-class unrouted count, a
    per-descriptor histogram), so the leaf is the one segment that never
    carries the meaning.
    """
    if any(m in key for m in WORSE_IF_UP):
        return 1
    if any(m in key for m in WORSE_IF_DOWN):
        return -1
    return 0


def _flatten(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, key + "."))
        elif isinstance(v, (int, float)):
            out[key] = v
    return out


def compare(section: str, metrics: dict, update: bool = False):
    """(regressions, changes, note) for `metrics` against the pinned baseline.

    `regressions` are fatal; `changes` are movement in the better or neutral
    direction and are reported so a session states them rather than carrying
    them forward as if nothing happened.
    """
    base = load(section)
    if update:
        save(section, metrics)
        return [], [], f"baseline PINNED for {section!r} ({len(_flatten(metrics))} metrics)"
    if base is None:
        return [], [], (f"no baseline pinned for {section!r} — run with "
                        f"--update-baseline to pin the current numbers")

    now, was = _flatten(metrics), _flatten(base)
    regressions, changes = [], []
    for key in sorted(set(now) | set(was)):
        a, b = was.get(key), now.get(key)
        if a == b:
            continue
        if a is None:
            changes.append((key, "—", b, "new metric"))
            continue
        if b is None:
            regressions.append((key, a, "—", "metric DISAPPEARED"))
            continue
        d = _direction(key)
        delta = b - a
        if (d == 1 and delta > 0) or (d == -1 and delta < 0):
            regressions.append((key, a, b, f"{delta:+g} in the WORSE direction"))
        else:
            changes.append((key, a, b, f"{delta:+g}"))
    return regressions, changes, None


def report(section: str, metrics: dict, update: bool = False) -> int:
    """Print the comparison and return the number of regressions."""
    regressions, changes, note = compare(section, metrics, update)
    print("\n" + "=" * 78)
    print(f"BASELINE — {section}")
    print("=" * 78)
    if note:
        print(f"  {note}")
        return 0
    if not regressions and not changes:
        print(f"  ✓ all {len(_flatten(metrics))} pinned metrics unchanged.")
        return 0
    for key, a, b, why in changes:
        print(f"  ◐ {key:52}{a} → {b}   ({why})")
    for key, a, b, why in regressions:
        print(f"  ✗ {key:52}{a} → {b}   {why}")
    if regressions:
        print(f"\n  {len(regressions)} REGRESSION(S). Either the change is wrong, or")
        print("  it is right and the baseline needs re-pinning ON PURPOSE:")
        print("      --update-baseline")
    return len(regressions)
