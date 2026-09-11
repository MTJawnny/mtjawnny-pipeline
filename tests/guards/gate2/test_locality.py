#!/usr/bin/env python3
"""LOCALITY — the R4 guard surface, at its S9 test owner.

Gate 2 row `locality`.

WHAT THIS FILE OWNS, AND WHAT IT DELIBERATELY DOES NOT
------------------------------------------------------
S7 moved the ratified address law into `mtj_foundry.mtg.shapes.locality`, and
`experiments/foundry_locality.py` remained the shell that supplies it the card
primitives and re-establishes the `STOP — …` process boundary. S9 moves the
GUARD out of that shell and leaves the shell's later-slice halves alone.

Here, and nowhere else now:

  * the six ratified negative-control fixtures;
  * the assertion-SCHEMA fixtures;
  * the WRITE-BOUNDARY fixtures for step 7;
  * the ratchet directions, their baseline read, and the direction assertion;
  * `--gate`, `--fixtures` and `--selftest`.

Still the legacy shell's, because they are later slices' to move:

  * `census()` — codebook-facing measurement;
  * the unaddressed-assertion reporter and `--report`;
  * `--census`.

**THE LAW IS NOT REIMPLEMENTED HERE.** `resolve`, `units`, `owning_header`,
`OWNER`/`SPAN`/`AMBIGUOUS`/`UNRESOLVED` and `_by_name` are bound FROM the shell,
which is the permanent S7 module behind its halt boundary. Binding them by
reference is what lets `--selftest` rig `resolve` exactly as it always did, and
it is why no second copy of the address law exists.

    python3 tests/guards/gate2/test_locality.py --gate
    python3 tests/guards/gate2/test_locality.py --fixtures
    python3 tests/guards/gate2/test_locality.py --selftest
"""
import argparse
import inspect
import sys
from pathlib import Path

# The legacy module directory, exactly as every other guard names it. The shell
# is a bounded later-owner surface this guard is authorized to consume while
# that slice is outstanding; it is NOT a second implementation of anything here.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "experiments"))
import foundry_common as fc                    # noqa: E402
import foundry_codebook as fcb                 # noqa: E402
import foundry_locality as fl                  # noqa: E402

from mtj_foundry.infra import ratchet          # noqa: E402
from mtj_foundry.paths import ProjectPaths     # noqa: E402

# C8.5J's inline form, unchanged. S9 moved the ratchet CALL out of the shell, so
# the baseline is obtained where it is read -- by this guard, from a ProjectPaths
# view built from the compatibility boundary's root, exactly as the six other
# inline consumers state it.
RATCHET_BASELINE = ProjectPaths.for_root(fc.REPO_ROOT).foundry_audit_baseline

# THE ADDRESS LAW, BY REFERENCE. `fl` re-exports the permanent S7 module through
# its halting boundary; these names are that module's, reached through the same
# boundary every legacy caller reaches it through.
#
# `resolve` is bound EXPLICITLY and first, because `--selftest` rebinds this
# module global to rig a first-match-wins resolver and the fixtures must see the
# rigged one.
resolve = fl.resolve

# EVERYTHING ELSE IS BOUND MECHANICALLY, for the reason the shell records in its
# own re-export loop: doing it BY HAND lost `_BULLET`, the fixtures read it as a
# module global, and only the full Gate-2 run saw the `NameError`. S9 reproduced
# that defect exactly once, here, before this loop replaced the hand-written
# list -- which is the second time the same list has cost the same bug.
#
# The NAME LIST comes from the permanent module, so nothing it owns can be
# dropped; the VALUE comes from the shell, so the historic `STOP — …` process
# contract still stands between these fixtures and a raised `LocalityError`.
from mtj_foundry.mtg.shapes import locality as _locality   # noqa: E402

_NOT_REEXPORTED = {"annotations", "Any", "Callable"}
for _name in sorted(vars(_locality)):
    if _name.startswith("__") or _name in _NOT_REEXPORTED or _name in globals():
        continue
    if inspect.ismodule(getattr(_locality, _name)):
        continue
    globals()[_name] = getattr(fl, _name)
del _name

# `census()` stays the shell's — this guard ratchets what it measures.
census = fl.census


# --------------------------------------------------------------------------
# FIXTURES — the six negative controls, inline
#
# `foundry_probe.py`'s guard self-test is the precedent: fixtures live in the
# module they protect, and every one is derived from a failure that really
# happened or that the ratification explicitly promised to prevent. Cards are
# FIXTURES, never a code path -- nothing in `resolve()` reads a card name.
# --------------------------------------------------------------------------

_by_name = fl._by_name


def fixtures(cards) -> list:
    """Returns a list of (label, ok, detail). Empty failures == all pass."""
    by = _by_name(cards)
    out = []

    def check(label, cond, detail=""):
        out.append((label, bool(cond), detail))

    av = by.get("Active Volcano")
    if av is None:
        check("corpus has Active Volcano", False, "fixture card absent")
        return out

    # NC1 -- a BROAD MODAL QUOTE must not become a single owner. This is the
    # failure the whole architecture exists to prevent: a wide quote forcing a
    # wide owner would re-create flattening under another name.
    broad = ("Choose one —\n• Destroy target blue permanent.\n"
             "• Return target Island to its owner's hand.")
    r = resolve(av, broad)
    check("NC1 broad modal quote -> SPAN, not OWNER", r["status"] == SPAN,
          f"got {r['status']}")

    # NC2 -- each fact's own quote resolves to its own bullet, and the two
    # bullets are DIFFERENT owners. That difference is the co-occurrence
    # disproof.
    rd = resolve(av, "Destroy target blue permanent.")
    rb = resolve(av, "Return target Island to its owner's hand.")
    check("NC2a destroy bullet -> OWNER", rd["status"] == OWNER, f"{rd}")
    check("NC2b bounce bullet -> OWNER", rb["status"] == OWNER, f"{rb}")
    check("NC2c the two owners DIFFER", rd["owner"] != rb["owner"],
          f"{rd['owner']} vs {rb['owner']}")
    check("NC2d and they are mutually exclusive (Choose one)",
          mutually_exclusive(av, rd["owner"], rb["owner"]))

    # NC3 -- raw/canonical DISAGREEMENT must yield AMBIGUOUS, never a race.
    # No live case exists (Case F measured 0), so this is constructed: a quote
    # that the union matches in two units must not pick one.
    kw = by.get("Kirtar's Wrath")
    if kw is not None:
        r = resolve(kw, "can't be regenerated")
        check("NC3/NC5 repeated short quote -> AMBIGUOUS",
              r["status"] == AMBIGUOUS,
              f"got {r['status']} candidates={r['candidates']}")

    # NC4 -- CANONICALISATION COLLISION must not silently merge. The union is
    # over COORDINATES, so two paragraphs collapsing to the same canonical
    # STRING still hold distinct coordinates.
    rah = by.get("Rahilda, Wanted Cutthroat // Rahilda, Feral Outlaw")
    if rah is not None:
        us = units(rah)
        canon_dupes = len(us) - len({c for _, _, c in us})
        distinct_coords = len({c for c, _, _ in us}) == len(us)
        check("NC4 collision card: coordinates stay distinct", distinct_coords,
              f"{canon_dupes} canonical text collisions, coords still unique")

    # NC6 -- an UNADDRESSED assertion is still valid card-level evidence and
    # still cannot prove same-unit co-occurrence. Encoded as the API contract:
    # co-occurrence needs two OWNERs, so a missing owner cannot satisfy it.
    unres = resolve(av, "this text is not printed on the card")
    check("NC6a unknown quote -> UNRESOLVED", unres["status"] == UNRESOLVED)
    check("NC6b unaddressed cannot prove co-occurrence",
          unres["owner"] is None)

    # Structural: A1's premise. If a paragraph ever holds two bullets the
    # paragraph coordinate stops separating modes and A1 must be revisited.
    two_bullet = [c["name"] for c in list(cards.values())
                  if any(u[1].count(_BULLET) > 1 for u in units(c))]
    check("A1 premise: no paragraph holds 2+ modal bullets",
          not two_bullet, f"{len(two_bullet)} card(s): {two_bullet[:3]}")
    return out

# --------------------------------------------------------------------------
# SCHEMA FIXTURES — the negative controls for the optional assertion field
#
# The field lives in `foundry_codebook.py`, but its MEANING lives here, and a
# guard is only known to be a guard once it has been shown to fail. These
# exercise `build_assertion` and `lint` against a synthetic one-member
# codebook: no corpus, no live file, nothing written.
#
# SC7 is the one that is easy to skip and expensive to lose. `locality` was
# APPENDED to a closed key tuple that is part of the byte-identity guarantee,
# so the claim that no existing assertion moves is a claim about serialized
# bytes -- and the backfill's conservation invariant rests on it entirely.
# --------------------------------------------------------------------------

_FIXTURE_OID = "00000000-0000-0000-0000-000000000001"


def _synthetic_codebook(assertion: dict) -> dict:
    """The smallest thing `lint` accepts, carrying exactly one assertion."""
    return {
        "schema": fcb.SCHEMA_V2,
        "axes": {"rule:locality-fixture": {
            "status": "active",
            "members": [{"oracle_id": _FIXTURE_OID,
                         "assertions": [assertion]}],
        }},
    }


def _lint_rejects(assertion: dict) -> bool:
    """True iff `lint` raises on a codebook carrying this assertion."""
    try:
        fcb.lint(_synthetic_codebook(assertion), "locality fixture")
    except fcb.LintError:
        return True
    return False


def schema_fixtures() -> list:
    """Returns [(label, ok, detail)] — same contract as `fixtures()`."""
    out = []

    def check(label, cond, detail=""):
        out.append((label, bool(cond), detail))

    base = dict(cls="rule-derived", source_ref="det-patterns-v2:1",
                quote="Destroy target blue permanent.", corpus_ref="2026-08-13")

    # SC7 -- APPENDING THE KEY MOVED NOTHING. An assertion built without an
    # address must serialize to exactly the bytes it did before the tuple
    # changed. Written as a literal, never as a re-derivation from the tuple:
    # a fixture that rebuilds the expectation from the code it is testing
    # agrees with itself by construction.
    plain = fcb.build_assertion(**base)
    expected = ('{"class": "rule-derived", "source_ref": "det-patterns-v2:1", '
                '"quote": "Destroy target blue permanent.", '
                '"corpus_ref": "2026-08-13", "evidence_status": "quoted"}')
    import json as _json
    check("SC7 an unaddressed assertion is byte-identical to pre-change",
          _json.dumps(plain, ensure_ascii=False) == expected,
          _json.dumps(plain, ensure_ascii=False))
    check("SC7b and it carries no locality key", "locality" not in plain)

    # SC1 -- a well-formed address lints clean, in canonical key order.
    good = fcb.build_assertion(**base, locality=(0, 1))
    check("SC1 a valid address lints clean", not _lint_rejects(good))
    check("SC1b locality is emitted LAST", list(good)[-1] == "locality",
          f"{list(good)}")

    # SC6 -- a resolver returns a TUPLE and JSON has none. Normalisation is not
    # cosmetic: an un-normalised address is a tuple in memory and a list after
    # readback, and every equality check downstream would silently disagree.
    check("SC6 a tuple coordinate is normalised to a list",
          good["locality"] == [0, 1] and isinstance(good["locality"], list),
          f"{good['locality']!r}")

    # SC3 -- KEY ORDER IS THE DETERMINISM GUARANTEE. An address in the right
    # shape but the wrong position must still be rejected.
    misordered = {"class": base["cls"], "source_ref": base["source_ref"],
                  "quote": base["quote"], "locality": [0, 1],
                  "corpus_ref": base["corpus_ref"], "evidence_status": "quoted"}
    check("SC3 an out-of-order address is rejected", _lint_rejects(misordered))

    # SC2 -- the tuple is still CLOSED. Adding one key must not turn the lint
    # permissive: the span was ruled derived-never-stored, so a producer
    # inventing `locality_span` has to be caught.
    span_key = dict(good)
    span_key["locality_span"] = [[0, 1], [0, 2]]
    check("SC2 an unknown neighbouring key is still rejected",
          _lint_rejects(span_key))

    # SC4 -- malformed coordinates. `True` is in here because `isinstance(True,
    # int)` is True in Python, so a bare int check accepts a boolean face index.
    for label, bad in (("a string", "0,1"), ("one element", [0]),
                       ("three elements", [0, 1, 2]), ("negative", [0, -1]),
                       ("a bool", [True, 1]), ("a float", [0.0, 1])):
        broken = dict(good)
        broken["locality"] = bad
        check(f"SC4 malformed address rejected: {label}", _lint_rejects(broken))

    # SC5 -- AN ADDRESS IS DERIVED FROM A QUOTE, so a quoteless assertion
    # cannot own one. The A3 legacy-captain-seed exemption is the only way to
    # carry an empty quote, and it must not become a back door to an
    # unfalsifiable address.
    seedless = fcb.build_assertion(
        "human", "captain-seed-batch-1", "", "2026-08-13",
        evidence_status="legacy-captain-seed")
    check("SC5a a quoteless legacy seed lints clean unaddressed",
          not _lint_rejects(seedless))
    seedless_addressed = dict(seedless)
    seedless_addressed["locality"] = [0, 0]
    check("SC5b the same seed WITH an address is rejected",
          _lint_rejects(seedless_addressed))

    # SC8 -- build_assertion halts rather than storing a shape no reader can
    # resolve. The constructor guard and the lint guard are independent, and
    # the backfill goes through the constructor.
    import contextlib
    import io
    try:
        # fc.halt prints to stderr before exiting; swallow it so a PASSING
        # fixture does not print a scary STOP line into a green gate.
        with contextlib.redirect_stderr(io.StringIO()):
            fcb.build_assertion(**base, locality="(0, 1)")
        halted = False
    except SystemExit:
        halted = True
    check("SC8 build_assertion HALTS on a malformed address", halted)
    return out

# --------------------------------------------------------------------------
# WRITE-BOUNDARY FIXTURES — the control for step 7
#
# Step 7's guarantee is the ABSENCE of a gate, and an absence is the one thing
# no ordinary test notices going missing. The ratified rule says an
# unaddressed assertion stays fully valid card-level evidence, so a future
# session that "improves" the write path by refusing unaddressable rows would
# be reverting a ratification while every other check stayed green.
#
# WB3 is therefore the load-bearing one: make the resolver address NOTHING,
# and the assertion must still be built, still lint clean, and still carry its
# evidence. If someone later adds `if locality is None: halt`, WB3 goes red.
# --------------------------------------------------------------------------

def write_boundary_fixtures(cards) -> list:
    """Returns [(label, ok, detail)] — same contract as `fixtures()`."""
    import foundry_det_pass as fdp   # deferred: fdp imports THIS module

    out = []

    def check(label, cond, detail=""):
        out.append((label, bool(cond), detail))

    by = _by_name(cards)
    av = by.get("Active Volcano")
    if av is None:
        check("corpus has Active Volcano", False, "fixture card absent")
        return out

    # WB1 -- a clean DET clause is born ADDRESSED, and the two modes of one
    # card get DIFFERENT addresses. This is the whole product of the arc.
    st = fdp.new_locality_stats()
    o1 = fdp.det_locality_owner(av, "Destroy target blue permanent.", st)
    o2 = fdp.det_locality_owner(av, "Return target Island to its owner's hand.", st)
    check("WB1a a resolvable DET clause is born addressed", o1 is not None, f"{o1}")
    check("WB1b the two modes get different addresses", o1 != o2, f"{o1} vs {o2}")
    check("WB1c both counted as OWNER", st["OWNER"] == 2, f"{st}")

    # WB2 -- an unaddressable clause returns None and is COUNTED, not raised.
    st = fdp.new_locality_stats()
    span = fdp.det_locality_owner(
        av, "Choose one —\n• Destroy target blue permanent.\n"
            "• Return target Island to its owner's hand.", st)
    check("WB2a a span clause yields no address", span is None, f"{span}")
    check("WB2b and is counted as SPAN, not dropped", st["SPAN"] == 1, f"{st}")
    missing = fdp.det_locality_owner(None, "anything", st)
    check("WB2c a card missing from the corpus does not raise",
          missing is None and st["no card"] == 1, f"{st}")

    # WB3 -- THE WRITE IS NOT GATED. With every address withheld, the assertion
    # must still be constructible, lint-clean, and carry its evidence intact.
    st = fdp.new_locality_stats()
    # PATCH THE MODULE `fdp` ACTUALLY CALLS, not this one. When this file runs
    # as `__main__`, `import foundry_det_pass` makes IT import
    # `foundry_locality` afresh -- so there are two live copies of this module
    # and `globals()["resolve"] = ...` patches the copy nobody calls. The first
    # version of this fixture did exactly that and reported a green write
    # boundary it had never exercised. `fdp.fl` is the copy under test in both
    # cases, so it is the only correct target.
    real_resolve = fdp.fl.resolve

    def addresses_nothing(card, quote, strict=True):
        return {"status": UNRESOLVED, "owner": None, "candidates": [],
                "reason": "fixture: resolver disabled"}
    fdp.fl.resolve = addresses_nothing
    try:
        owner = fdp.det_locality_owner(av, "Destroy target blue permanent.", st)
        a = fcb.build_assertion("rule-derived", "det-patterns-v2:1",
                                "Destroy target blue permanent.", "2026-08-13",
                                "quoted", locality=owner)
    finally:
        fdp.fl.resolve = real_resolve
    check("WB3a with the resolver dead, no address is produced", owner is None)
    check("WB3b the assertion is still BUILT", isinstance(a, dict))
    check("WB3c it carries no locality key", "locality" not in a)
    check("WB3d it still carries its evidence quote",
          a["quote"] == "Destroy target blue permanent.")
    check("WB3e and it lints clean", not _lint_rejects(a))

    # WB4 -- a reflowing card cannot kill the write path. `strict=False` is the
    # structural guarantee; this breaks canonicalisation on purpose to prove it,
    # because 0 of 32,557 gated cards reflow today and an untriggered guard is
    # not known to be a guard.
    st = fdp.new_locality_stats()
    real_canon = fc.canonicalize_self_reference
    fc.canonicalize_self_reference = lambda raw, card: (raw or "") + "\nreflowed"
    try:
        import contextlib
        import io
        strict_halts = False
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                resolve(av, "Destroy target blue permanent.", strict=True)
        except SystemExit:
            strict_halts = True
        soft = fdp.det_locality_owner(av, "Destroy target blue permanent.", st)
    finally:
        fc.canonicalize_self_reference = real_canon
    check("WB4a a reflow HALTS the audit path (strict=True)", strict_halts)
    check("WB4b but the write path only loses the address", soft is None,
          f"{soft}")
    check("WB4c and reports it as UNRESOLVED", st["UNRESOLVED"] == 1, f"{st}")
    return out

# Every locality metric that is supposed to ratchet, and the direction it is
# supposed to ratchet in. The ratchet resolves direction by
# SUBSTRING MATCH on the metric name, so renaming a metric silently downgrades
# it to neutral -- reported on movement, never fatal. That is the "ratified
# token with no emitter" shape aimed at the ratchet itself, and it is invisible
# precisely because the gate keeps printing and keeps exiting 0.
#
# `addressable_missing` carries the narrowest marker of the three (its own full
# name, to avoid a future collision with family_sweep's `missing_from_ratified`
# and batch8_diff's `n_missing`), so it is the most rename-fragile and the one
# this check is really for.
RATCHET_DIRECTIONS = {
    "stored_owned": -1,          # a FALL is worse
    "stored_mismatch": 1,        # a RISE is worse
    "addressable_missing": 1,    # a RISE is worse
    "owned": -1,                 # a FALL is worse
}


def load_baseline_locality():
    """The pinned locality numbers, or None if nothing is pinned yet."""
    return ratchet.load(RATCHET_BASELINE, "locality")


def assert_ratchet_directions() -> None:
    """Halts if any locality metric has stopped resolving to its direction.

    C8.5J: this reads the ratchet's PUBLIC `direction()`. It used to reach
    through `foundry_audit_baseline._direction`, and a consumer that has to
    cross an underscore to do its job is the surface telling you it is wrong.
    The function it calls is unchanged.
    """
    wrong = []
    for metric, want in sorted(RATCHET_DIRECTIONS.items()):
        got = ratchet.direction(f"locality.{metric}")
        if got != want:
            wrong.append((metric, want, got))
    if wrong:
        names = {1: "WORSE_IF_UP", -1: "WORSE_IF_DOWN", 0: "NEUTRAL"}
        fc.halt(
            "locality ratchet directions have drifted: "
            + "; ".join(f"{m} should be {names[w]} but resolves {names[g]}"
                        for m, w, g in wrong)
            + ". A metric that resolves NEUTRAL is reported on movement and "
              "never fatal, so this gate would keep passing while the thing it "
              "guards degraded. Fix the marker in mtj_foundry/ratchet.py or "
              "the metric name here — do not delete this check.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", action="store_true",
                    help="fixtures + census ratchet, one exit code")
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="negative control for the GATE: prove the fixtures "
                         "can fail")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()

    if args.selftest:
        # Break the law on purpose: accept the first representation that
        # matches instead of the union. NC1's broad modal quote must then stop
        # reporting SPAN. A guard that has never been shown to fail is not
        # known to be a guard.
        global resolve
        real = resolve

        def racing(card, quote):
            r = real(card, quote)
            if r["status"] == SPAN:
                return {"status": OWNER, "owner": (0, 0),
                        "candidates": [(0, 0)], "reason": "FIRST-MATCH-WINS"}
            return r
        resolve = racing
        try:
            failed = [f for f in fixtures(cards) if not f[1]]
        finally:
            resolve = real
        print(f"selftest (first-match-wins resolver): "
              f"{len(failed)} fixture failure(s)")
        for label, _, detail in failed:
            print(f"    caught: {label}  {detail}")
        if not failed:
            print("  SELFTEST FAILED -- the fixtures cannot detect a racing "
                  "resolver, so they are not a guard.")
            return 1
        print("  selftest OK: the fixtures detect a broken resolver")

        # Second negative control, for the SCHEMA half. Break the lint on
        # purpose -- make it accept everything -- and the schema fixtures must
        # go red. Aimed at the CODE PATH (the raise inside `lint`), not at the
        # tool's name: a control pointed at the wrong layer reads as "this gate
        # is broken", which happened to three of eight controls on 2026-08-09.
        real_lint = fcb.lint

        def permissive(codebook, path_label="codebook"):
            return {"axes": 1, "members": 1, "assertions": 1,
                    "exemptions_applied": []}
        fcb.lint = permissive
        try:
            schema_failed = [f for f in schema_fixtures() if not f[1]]
        finally:
            fcb.lint = real_lint
        print(f"\nselftest (permissive lint): "
              f"{len(schema_failed)} schema fixture failure(s)")
        for label, _, detail in schema_failed:
            print(f"    caught: {label}  {detail}")
        if not schema_failed:
            print("  SELFTEST FAILED -- the schema fixtures cannot detect a "
                  "lint that accepts everything, so they are not a guard.")
            return 1
        print("  selftest OK: the schema fixtures detect a broken lint")

        # Third negative control, for the WRITE BOUNDARY. Add the gate the
        # ratification forbids -- refuse to build an unaddressed assertion --
        # and WB3 must go red. This is the control that matters most, because
        # step 7's guarantee is an ABSENCE, and nothing else in the repo would
        # notice a gate quietly appearing here.
        import foundry_det_pass as fdp
        real_build = fcb.build_assertion

        def gated_build(*a, **kw):
            if kw.get("locality") is None:
                fc.halt("FIXTURE: refusing to write an unaddressed assertion")
            return real_build(*a, **kw)
        fcb.build_assertion = gated_build
        try:
            import contextlib
            import io
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    wb_failed = [f for f in write_boundary_fixtures(cards)
                                 if not f[1]]
            except SystemExit:
                # The gate killed the fixture run outright, which is itself the
                # catch: an unaddressable row became unwritable.
                wb_failed = [("WB3 the write path halted on an unaddressed "
                              "assertion", False, "SystemExit")]
        finally:
            fcb.build_assertion = real_build
        print(f"\nselftest (write path gated on locality): "
              f"{len(wb_failed)} write-boundary fixture failure(s)")
        for label, _, detail in wb_failed:
            print(f"    caught: {label}  {detail}")
        if not wb_failed:
            print("  SELFTEST FAILED -- the write-boundary fixtures cannot "
                  "detect a locality gate on the write path, so the ratified "
                  "unaddressed rule is unguarded.")
            return 1
        print("  selftest OK: the write-boundary fixtures detect a gated write")

        # Fourth negative control, for `addressable_missing`. Take ONE
        # otherwise-unchanged active assertion that the resolver addresses,
        # remove ONLY its stored locality, and the metric must become nonzero
        # while everything else holds still. Runs against a temp copy: the live
        # codebook is never written, and the check asserts that afterwards.
        import json as _json
        import tempfile
        live_sha_before = fcb.sha256_of(fcb.CODEBOOK_PATH)
        cb = _json.loads(fcb.CODEBOOK_PATH.read_text(encoding="utf-8"))

        victim = None
        for slug in sorted(cb["axes"]):
            ax = cb["axes"][slug]
            if ax.get("status") != "active":
                continue
            for mem in ax.get("members") or []:
                for a in mem["assertions"]:
                    if "locality" in a:
                        victim = (slug, mem["oracle_id"], a["class"],
                                  a["source_ref"], list(a["locality"]),
                                  a["quote"])
                        break
                if victim:
                    break
            if victim:
                break
        if victim is None:
            print("\nselftest (addressable_missing): SKIPPED — no stored "
                  "address in the live codebook to remove. Run the backfill "
                  "first; this control has nothing to break.")
            return 0

        slug, oid, cls, sref, coord, quote = victim
        # Step 3 of the control: the resolver must STILL say OWNER. If it did
        # not, a nonzero metric would prove nothing -- the row would be
        # unaddressed for a legitimate reason.
        card = cards.get(oid)
        r = resolve(card, quote)
        still_owner = (r["status"] == OWNER and list(r["owner"]) == coord)

        for mem in cb["axes"][slug]["members"]:
            if mem["oracle_id"] == oid:
                for a in mem["assertions"]:
                    if a["class"] == cls and a["source_ref"] == sref:
                        a.pop("locality")

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as tf:
            _json.dump(cb, tf)
            tmp = tf.name
        try:
            m = census(cards, codebook_path=tmp)
            regressions, _, _ = ratchet.compare(RATCHET_BASELINE, "locality", m)
        finally:
            Path(tmp).unlink()

        base = load_baseline_locality()
        checks = [
            ("the resolver still returns OWNER for the victim", still_owner),
            ("addressable_missing became nonzero",
             m["addressable_missing"] == 1),
            ("stored_owned fell by exactly 1",
             base is None or m["stored_owned"] == base["stored_owned"] - 1),
            ("stored_mismatch stayed 0 — absence is not disagreement",
             m["stored_mismatch"] == 0),
            ("resolvable `owned` did NOT move — the evidence is untouched",
             base is None or m["owned"] == base["owned"]),
            ("the ratchet reports it as a REGRESSION",
             any("addressable_missing" in k for k, *_ in regressions)),
            ("the live codebook was never written",
             fcb.sha256_of(fcb.CODEBOOK_PATH) == live_sha_before),
        ]

        # THE SCENARIO THIS METRIC WAS ADDED FOR, run explicitly rather than
        # argued in a comment. Corpus growth adds addressed rows while one is
        # silently dropped, so `stored_owned` lands back on its pinned value
        # and reads CLEAN. `stored_mismatch` is 0 because nothing incorrect was
        # stored. Both existing guards go green on a real loss; only
        # `addressable_missing` fires. Simulated by masking the baseline, which
        # is exactly what compensating growth does to it.
        if base is not None:
            masked = dict(base)
            masked["stored_owned"] = m["stored_owned"]   # growth hid the loss
            # C8.5J: the mask is an EXPLICIT TEMPORARY BASELINE, not a
            # monkeypatched `load`. Rebinding a shared module attribute made the
            # control depend on a `finally` to un-rig the comparator for every
            # later caller in the process; the ratchet now takes its baseline as
            # an argument, so the rigged document is a file this block owns and
            # deletes. The comparator itself is still the real one -- what is
            # substituted is the INPUT, which is the whole point of the control.
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                             encoding="utf-8") as mf:
                _json.dump({"locality": masked}, mf)
                masked_baseline = Path(mf.name)
            try:
                mask_regs, _, _ = ratchet.compare(masked_baseline, "locality", m)
            finally:
                masked_baseline.unlink(missing_ok=True)
            mask_keys = {k for k, *_ in mask_regs}
            checks += [
                ("MASKED: stored_owned reads clean when growth hides the loss",
                 not any("stored_owned" in k for k in mask_keys)),
                ("MASKED: stored_mismatch still reads clean",
                 not any("stored_mismatch" in k for k in mask_keys)),
                ("MASKED: addressable_missing fires ALONE",
                 mask_keys == {"addressable_missing"}),
            ]
        print(f"\nselftest (addressable_missing) — victim "
              f"{slug}/{oid} ({cls}, {sref}) at {coord}:")
        failed_am = [label for label, ok in checks if not ok]
        for label, ok in checks:
            print(f"    {'caught' if ok else 'NOT CAUGHT'}: {label}")
        if failed_am:
            print("  SELFTEST FAILED -- addressable_missing does not catch a "
                  "removed address on an addressable assertion.")
            return 1
        print("  selftest OK: addressable_missing catches a silently dropped "
              "address")
        return 0

    bad = 0
    if args.gate or args.fixtures:
        rows = fixtures(cards)
        failed = [r for r in rows if not r[1]]
        print(f"locality fixtures: {len(rows) - len(failed)}/{len(rows)} pass")
        for label, _, detail in failed:
            print(f"    FAIL {label}  {detail}")
        bad += len(failed)

        srows = schema_fixtures()
        sfailed = [r for r in srows if not r[1]]
        print(f"locality schema fixtures: "
              f"{len(srows) - len(sfailed)}/{len(srows)} pass")
        for label, _, detail in sfailed:
            print(f"    FAIL {label}  {detail}")
        bad += len(sfailed)

        wrows = write_boundary_fixtures(cards)
        wfailed = [r for r in wrows if not r[1]]
        print(f"locality write-boundary fixtures: "
              f"{len(wrows) - len(wfailed)}/{len(wrows)} pass")
        for label, _, detail in wfailed:
            print(f"    FAIL {label}  {detail}")
        bad += len(wfailed)

        if not args.gate:
            return 1 if bad else 0

    # `--census` stays the legacy shell's door onto `census()`: printing the
    # measurement is a report, and this guard exists to RATCHET it.
    if args.gate:
        m = census(cards)
        q = max(m["quoted"], 1)
        located = m["owned"] + m["span"]
        print(f"\nlocality census — {m['assertions']:,} assertions, "
              f"{m['quoted']:,} quoted, {m['quoteless']:,} quoteless")
        print(f"    semantic OWNER      : {m['owned']:,}  "
              f"({100 * m['owned'] / q:.2f}% of quoted)")
        print(f"    evidence LOCATED    : {located:,}  "
              f"({100 * located / q:.2f}% of quoted)   <- a different question")
        print(f"    span                : {m['span']:,}")
        print(f"    ambiguous           : {m['ambiguous']:,}")
        print(f"    unresolved          : {m['unresolved']:,}")
        print(f"  STORED in the codebook (a different question again)")
        print(f"    addressed           : {m['stored_owned']:,}")
        print(f"    stored_mismatch     : {m['stored_mismatch']:,}   "
              f"<- stored address disagrees with the resolver today")
        print(f"    addressable_missing : {m['addressable_missing']:,}   "
              f"<- resolver says OWNER but nothing is stored (must be 0)")
        if args.gate:
            # Before trusting the ratchet, prove it still points the right way.
            assert_ratchet_directions()
            bad += ratchet.report(RATCHET_BASELINE, "locality", m,
                                  args.update_baseline)

    if args.gate:
        if bad:
            print(f"\n  LOCALITY GATE FAILED ({bad}).")
            return 1
        print("\n  locality gate GREEN")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
