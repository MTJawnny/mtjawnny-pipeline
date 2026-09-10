"""The standing RATCHET — the permanent home of the capability that decides
whether a standing audit degraded.

## What this is

Six things: an error type, a read, a write, a direction lookup, a comparison and
a report. Given a baseline document and a section's current metrics, it says
which numbers moved and which of those movements are FATAL.

## Why a ratchet and not a tolerance

"Every scoring constant is a ratified ruling, not a tuning knob", and a
percentage band would be exactly such a knob, picked by an implementer, gating
Captain-ratified work. So there is no band: any movement in the WORSE direction
is fatal, any movement in the better direction is reported and requires an
explicit `--update-baseline` to accept. Same shape as the determinism x2
byte-identical gate — the standard is "nothing changed unless you said so",
which needs no constant.

**Why the floor matters.** Measured 2026-08-07 against the corpus base rate, the
`comma` class needed +4,213 newly-broken lines to trip the ratio flag and +2,662
to trip a z=3 flag, because it sits well BELOW baseline and has that much room to
fall before it looks abnormal. Against its OWN pinned rate the floor is 1 line. A
class compared to the corpus can hide a defect the size of a set release; a class
compared to itself cannot.

## A MISSING BASELINE FILE IS FATAL, and that is half the point

`load()` once returned `None` both when the file was absent and when the section
simply was not pinned yet, and `compare()` reads `None` as "no baseline pinned"
and returns **no regressions**. So a baseline that had never existed and one that
had been deleted were the same green result — the failure mode two other modules
independently worked around, recording that `report()` "returns 0 without
comparing anything" on a fresh clone. The baseline is TRACKED (P0.3D), so its
absence means a broken checkout, not a first run.

An absent SECTION still returns `None` and still prints the pin-it note. That
behaviour is deliberately unchanged, because an unpinned section really is a
first run.

## What this is NOT

It is not a move of `experiments/foundry_audit_baseline.py`. That module is the
ORACLE for these behaviors — every value below is differentially compared against
it — but its BOUNDARY is not the target architecture, and two of its properties
are deliberately not reproduced:

* **No module-level baseline path.** The legacy module derives a repository root
  at import time and keeps the resulting path in a module global. That is a
  repository-relative layout fact stated outside the layout owner, and — because
  a global is writable — it doubled as the seam two negative controls
  monkeypatched to redirect a write. Here the baseline is a PARAMETER of every
  entry point; the caller gets it from `ProjectPaths.foundry_audit_baseline`.
  Redirecting a control to a temporary input is then an ARGUMENT, not a mutation
  of shared process state, so it cannot leak into an unrelated consumer and
  cannot be left behind by an interrupt.
* **No private direction lookup.** `_direction()` was private and imported anyway
  — `foundry_locality.assert_ratchet_directions()` calls it to prove its four
  metrics still resolve the way they are supposed to. A consumer that must reach
  through the underscore is telling you the surface is wrong, so `direction()` is
  public here. That is an architecture repair, not a semantic one: the function
  it exposes is unchanged.

Stdlib only. Nothing here imports the legacy tree, touches `sys.path`, or knows
where the repository is.

## The direction tables are EVIDENCE, carried verbatim

Every marker below, and every comment explaining one, is copied from the legacy
oracle unchanged. Each was added by a named incident, and several record a
collision that was avoided ON PURPOSE — `ambiguous` was deliberately NOT added,
`addressable_missing` is deliberately a full metric name rather than the bare
word `missing`. Regenerating or tidying those memberships would discard the
reasoning that decided them, which is the one thing "PRESERVE TRUTH, NOT
PLUMBING" forbids.
"""

from __future__ import annotations

import json
from pathlib import Path

__all__ = ["BaselineUnavailable", "load", "save", "direction", "compare",
           "report"]


class BaselineUnavailable(RuntimeError):
    """The baseline document could not be read.

    Fatal, never a verdict. The whole purpose of a ratchet is to make an
    unreviewed change loud, so the one thing it may never do is report success
    because it could not find the thing it compares against.
    """


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
_WORSE_IF_UP = ("unrouted", "uncontexted", "dropped", "unscanned", "violations",
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
_WORSE_IF_DOWN = ("lines", "deliveries", "keyword_homes", "expansions",
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


def _document(baseline: Path) -> dict:
    """Every pinned section, or HALT. The single read of the baseline document.

    Absence is fatal here rather than an empty document. The tracked baseline is
    present in any checkout; if it is missing, unreadable or not a JSON object,
    the honest answer is that this run cannot say whether anything degraded — and
    returning an empty document would say that nothing did.
    """
    baseline = Path(baseline)
    if not baseline.exists():
        raise BaselineUnavailable(
            f"the tracked ratchet baseline is missing: {baseline}. It is tracked in "
            "git, so this is a broken checkout, not a first run — and a ratchet that "
            "reported success because it could not find its baseline would be worse "
            f"than no ratchet at all. Restore the file (git checkout -- {baseline}) "
            "rather than re-pinning it."
        )
    try:
        raw = baseline.read_text(encoding="utf-8")
    except OSError as exc:
        raise BaselineUnavailable(
            f"the tracked ratchet baseline at {baseline} could not be read: {exc}"
        ) from None
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BaselineUnavailable(
            f"the tracked ratchet baseline at {baseline} is not valid JSON: {exc}. "
            "Refusing to treat a damaged control input as an empty one."
        ) from None
    if not isinstance(doc, dict):
        raise BaselineUnavailable(
            f"the tracked ratchet baseline at {baseline} is not a JSON object"
        )
    return doc


def load(baseline: Path, section: str) -> dict | None:
    """The pinned numbers for one audit, or None if that SECTION is not pinned yet.

    `None` means one thing only — this section has never been pinned. It used to
    mean that OR "the baseline file is not there", and `compare()` reads the
    value as a green "nothing pinned yet". Halting on the missing FILE is what
    separates the two.
    """
    return _document(baseline).get(section)


def save(baseline: Path, section: str, metrics: dict) -> None:
    """Pin `metrics` for `section` in `baseline`, leaving every other section alone.

    Reads through the same halt: if the baseline is missing, this REFUSES rather
    than creating a fresh one. Writing a new file would silently drop every other
    section's pins and leave each of them reading as "not pinned yet" — a
    one-command way to un-ratchet the whole suite while looking like an update.
    """
    doc = _document(baseline)
    doc[section] = metrics
    Path(baseline).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")


def direction(key: str) -> int:
    """+1 if a RISE is worse, -1 if a FALL is worse, 0 if any change is notable.

    EVERY segment of the key path is tested, not just the leaf. The first version
    read only the leaf, so `class_unrouted.comma` was judged on `comma` -- a name
    in no direction set -- and a negative control that pushed that class 621 lines
    in the wrong direction exited 0. The nested metrics are exactly the ones worth
    ratcheting (a per-class unrouted count, a per-descriptor histogram), so the
    leaf is the one segment that never carries the meaning.

    UP is checked BEFORE DOWN, and the precedence is load-bearing rather than
    incidental: `conservation.unrouted_lines` carries both `unrouted` and `lines`,
    and a rise in unrouted lines is the regression that metric exists to catch.
    """
    if any(m in key for m in _WORSE_IF_UP):
        return 1
    if any(m in key for m in _WORSE_IF_DOWN):
        return -1
    return 0


def _flatten(d: dict, prefix: str = "") -> dict:
    """Dotted keys for the NUMERIC leaves only.

    A str/list/None leaf is not a metric: it cannot move in a direction, so
    admitting one would produce a key that `direction()` can classify and
    `compare()` can only ever call "changed".
    """
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, key + "."))
        elif isinstance(v, (int, float)):
            out[key] = v
    return out


def compare(baseline: Path, section: str, metrics: dict, update: bool = False):
    """(regressions, changes, note) for `metrics` against the pinned baseline.

    `regressions` are fatal; `changes` are movement in the better or neutral
    direction and are reported so a session states them rather than carrying
    them forward as if nothing happened.

    A DISAPPEARED metric is a regression whatever its direction — a number that
    stops being emitted stops being watched. A NEWLY APPEARED one is a change and
    not a regression merely for being new; there is nothing to have moved away
    from yet.
    """
    base = load(baseline, section)
    if update:
        save(baseline, section, metrics)
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
        d = direction(key)
        delta = b - a
        if (d == 1 and delta > 0) or (d == -1 and delta < 0):
            regressions.append((key, a, b, f"{delta:+g} in the WORSE direction"))
        else:
            changes.append((key, a, b, f"{delta:+g}"))
    return regressions, changes, None


def report(baseline: Path, section: str, metrics: dict,
           update: bool = False) -> int:
    """Print the comparison and return the number of regressions."""
    regressions, changes, note = compare(baseline, section, metrics, update)
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
