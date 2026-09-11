#!/usr/bin/env python3
"""OBJECT LATTICE — the R4 guard surface, at its S9 test owner.

Gate 2 row `object_lattice`.

Three checks, one exit code: the grammar-shape fixtures, the independent
residual invariant, and the pinned per-class membership ratchet. Never run the
three separately to save time — the ratchet is the one that makes a REMOVAL
fatal, and `e780842` removed 170 memberships, verified 83, and nothing else on
Gate 2's list could see the other 87.

WHAT THIS FILE OWNS, AND WHAT IT DELIBERATELY DOES NOT
------------------------------------------------------
S7 moved the reusable target-class semantics into
`mtj_foundry.mtg.shapes.target_classes`, and
`experiments/foundry_object_lattice.py` remained the shell that supplies the CR
edition and the DET preprocessing and re-establishes the `STOP — …` process
boundary. S9 moves the GUARD out of that shell.

Here, and nowhere else now:

  * `GRAMMAR_FIXTURES`, `REGRESSION_CARDS`, `CLASS_ANCHORS` and `fixtures()`;
  * `--gate` and `--fixtures`.

Still the legacy shell's, because they are later slices' to move: `slug_for`
and the `rule:targeted-*` axis identity it builds, `_assert_vocabulary_agrees`
and `validate_slug` governance, `ratified_total`/`assert_ratified_total`, the
live codebook read, `baseline_metrics`, `audit`, `exclusivity_report`, the
locality binding, `write_report` and the rest of the CLI.

**NO SEMANTIC IS REIMPLEMENTED HERE.** `classify_clause`, `classes_for_card`,
`PERMANENT_TYPES`, `residual_invariant`, `anchor_coverage`,
`assert_ratified_total`, `baseline_metrics` and `slug_for` are bound FROM the
shell, which is the permanent S7 module behind its halt boundary plus the
later-slice measurement this guard ratchets.

    python3 tests/guards/gate2/test_object_lattice.py --gate
    python3 tests/guards/gate2/test_object_lattice.py --fixtures
"""
import argparse
import sys
from pathlib import Path

# The legacy module directory, exactly as every other guard names it. The shell
# is a bounded later-owner surface this guard is authorized to consume while
# that slice is outstanding; it is NOT a second implementation of anything here.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "experiments"))
import foundry_common as fc                     # noqa: E402
import foundry_object_lattice as ol             # noqa: E402

from mtj_foundry.infra import ratchet           # noqa: E402
from mtj_foundry.paths import ProjectPaths      # noqa: E402

# C8.5J's inline form, unchanged. S9 moved the ratchet CALL out of the shell, so
# the baseline is obtained where it is read. The shell keeps its own bound view
# for the codebook path it still owns; this guard builds none, which is why it is
# held to the stricter inline spelling rather than the bound-view one.
RATCHET_BASELINE = ProjectPaths.for_root(fc.REPO_ROOT).foundry_audit_baseline

# THE LATTICE SEMANTICS, BY REFERENCE.
ACTION_VERBS = ol.ACTION_VERBS
PERMANENT_TYPES = ol.PERMANENT_TYPES
classify_clause = ol.classify_clause
classes_for_card = ol.classes_for_card
residual_invariant = ol.residual_invariant


def anchor_coverage(anchors=None, cards: dict = None) -> dict:
    """`CLASS_ANCHORS` lives here now, so the default that names it does too.

    The measurement itself is not reimplemented: this forwards to the shell's
    boundary, which forwards to the permanent S7 surface.
    """
    return ol.anchor_coverage(CLASS_ANCHORS if anchors is None else anchors,
                              cards)

assert_ratified_total = ol.assert_ratified_total
baseline_metrics = ol.baseline_metrics
slug_for = ol.slug_for


# --------------------------------------------------------------------------
# grammar fixtures
# --------------------------------------------------------------------------

# THE FIXTURE IS THE GRAMMATICAL SHAPE, NEVER THE CARD NAME. Seven cards
# regressed on 2026-08-12 and pinning those seven would leave the next card
# printing the same shape unprotected. Each row is a clause TAIL — what
# `classify_clause` actually receives — and the five categories are the five
# ways the target expression's right edge can be got wrong.
#
# `foundry_probe.py`'s guard self-test is the precedent: fixtures inline in the
# module they protect, replayed by a gate, every one derived from a defect that
# really happened.
GRAMMAR_FIXTURES = (
    # A. INSTRUCTION TERMINATION (CR 608.2c) — a later instruction must not
    #    contaminate this target's noun phrase.
    ("A instruction-termination", "destroy",
     "attacking creature, then put this card on top of your library",
     {"creature"}),
    ("A instruction-termination, plural", "exile",
     "creatures you control, then return those cards to the battlefield",
     {"creature"}),

    # B. A SEPARATE LATER OBJECT (CR 601.2c) — the single printed `target` does
    #    not reach a conjunct carrying its own determiner.
    ("B second-object", "exile",
     "nonland permanent and the top card of your library",
     {"nonland-permanent"}),
    ("B second-object, quantified", "exile",
     "nontoken creature you own and the top two cards of your library",
     {"creature"}),

    # C. SHARED-HEAD DISTRIBUTIVE `card` — `card` applies across every arm, so
    #    NO arm is a battlefield object. The dangerous direction: a naive arm
    #    split turns each of these into a wrong ratified token.
    ("C shared-head creature-or-land", "bounce",
     "creature or land card from your graveyard to your hand", set()),
    ("C shared-head aura-or-equipment", "bounce",
     "aura or equipment card from your graveyard to your hand", set()),
    ("C shared-head artifact-or-enchantment", "exile",
     "artifact or enchantment card from your graveyard", set()),
    # `and/or` is a coordination INSIDE one target phrase — no determiner
    # follows, so rule B must not fire and the shared head must still hold.
    ("C shared-head and/or", "bounce",
     "instant and/or sorcery cards from your graveyard to your hand", set()),

    # D. INDEPENDENT ALTERNATIVES — one arm is a battlefield object, the other
    #    is a card in another zone, and no origin is printed for the target.
    ("D independent-arms", "bounce",
     "nonland permanent or suspended card to its owner's hand",
     {"nonland-permanent"}),

    # E. INSTRUCTION-LOCAL ZONE ORIGIN — an origin belonging to a LATER
    #    instruction cannot retroactively make this target a card.
    ("E zone-origin-is-instruction-local", "exile",
     "creature you control, then reveal cards from the top of your library",
     {"creature"}),

    # NEGATIVE CONTROLS — the behaviour the repair must NOT have broken.
    ("neg plain card-form", "bounce",
     "creature card from your graveyard to your hand", set()),
    ("neg plain permanent", "destroy", "creature", {"creature"}),
    ("neg broad outranks per-type", "destroy",
     "nonland permanent", {"nonland-permanent"}),
)

# The seven that regressed, kept as CORPUS fixtures beside the grammar ones.
# They are a fixture, never a code path: nothing in the classifier reads a card
# name, and each of these passes only because its SHAPE is handled.
REGRESSION_CARDS = {
    "Vengeful Pharaoh": ("destroy", {"creature"}),
    "Venser's Diffusion": ("bounce", {"nonland-permanent"}),
    "Illusionist's Stratagem": ("exile", {"creature"}),
    "Displace": ("exile", {"creature"}),
    "Lukka, Coppercoat Outcast": ("exile", {"creature"}),
    "Suspend Aggression": ("exile", {"nonland-permanent"}),
    "Become Anonymous": ("exile", {"creature"}),
}


# ONE ANCHOR PER RATIFIED CLASS — the only guard that sees a ZERO-SUM MOVE.
#
# Measured 2026-08-13: a compensating `exile-creature -7 / exile-artifact +7`
# nets zero, so the tracked family total is silent by construction and the
# per-class ratchet is unpinned on a fresh clone. Both count-based guards go
# GREEN. A count cannot see a substitution either — a correct member leaving
# and a wrong one arriving keeps every number identical.
#
# A per-card anchor sees both, because it names the CARD and the CLASS. It is
# tracked (so it survives a fresh clone), and it is growth-tolerant (a new
# Scryfall card cannot invalidate it), which is exactly the pair of properties
# the count guards each have only one of.
#
# **These are FIXTURES, not a hand-list standing in for a derivation.** Nothing
# in the classifier reads a card name; each anchor passes only because the
# CR-derived grammar handles its shape. Every one was verified against full
# oracle text, all faces, before being written here — classifier output is not
# evidence for its own fixture.
#
# Chosen for stability: each names its type DIRECTLY ("Destroy target
# artifact"), never through a CR 205.3 subtype, so a subtype-list refresh
# cannot move an anchor. Single-class for their stem, so the expectation is
# exact rather than a subset.
CLASS_ANCHORS = (
    ("bounce",  "artifact",              "Into Thin Air"),
    ("bounce",  "creature",              "Flooded Shoreline"),
    ("bounce",  "enchantment",           "Triton Cavalry"),
    ("bounce",  "land",                  "Aven Fogbringer"),
    ("bounce",  "nonland-permanent",     "Wail of the Forgotten"),
    ("bounce",  "permanent",             "Surging Aether"),
    ("destroy", "artifact",              "Goblin Trashmaster"),
    ("destroy", "creature",              "Kalitas, Bloodchief of Ghet"),
    ("destroy", "enchantment",           "Dawnbringer Cleric"),
    ("destroy", "land",                  "Ogre Arsonist"),
    ("destroy", "noncreature-permanent", "Nicol Bolas, Planeswalker"),
    ("destroy", "nonland-permanent",     "Vraska the Unseen"),
    ("destroy", "permanent",             "Angel of Despair"),
    ("destroy", "planeswalker",          "Silumgar's Command"),
    ("exile",   "artifact",              "Suplex"),
    ("exile",   "creature",              "Astarion's Thirst"),
    ("exile",   "enchantment",           "Erase"),
    ("exile",   "land",                  "Sowing Mycospawn"),
    ("exile",   "nonland-permanent",     "Kaya the Inexorable"),
    ("exile",   "permanent",             "Karn Liberated"),
)



def fixtures() -> dict:
    """Replay the grammar shapes, the seven regressions, and the class anchors."""
    failed = []
    for label, stem, tail, want in GRAMMAR_FIXTURES:
        got = classify_clause(tail, PERMANENT_TYPES)["classes"]
        if got != want:
            failed.append((label, tail, sorted(want), sorted(got)))

    cards, _, _ = fc.load_corpus_gated()
    by_name = {}
    for card in cards.values():
        by_name.setdefault(card["name"], card)
    for name, (stem, want) in sorted(REGRESSION_CARDS.items()):
        card = by_name.get(name)
        if card is None:
            failed.append((f"corpus {name}", "absent from the gated corpus",
                           sorted(want), ["CARD NOT FOUND"]))
            continue
        got = classes_for_card(card, stem, PERMANENT_TYPES)["classes"]
        if got != want:
            failed.append((f"corpus {name}", stem, sorted(want), sorted(got)))
    for stem, cls, name in CLASS_ANCHORS:
        card = by_name.get(name)
        if card is None:
            failed.append((f"anchor {stem}-{cls} {name}",
                           "absent from the gated corpus", [cls], ["CARD NOT FOUND"]))
            continue
        got = classes_for_card(card, stem, PERMANENT_TYPES)["classes"]
        if got != {cls}:
            failed.append((f"anchor {stem}-{cls} {name}", stem, [cls], sorted(got)))
    return {"n": len(GRAMMAR_FIXTURES) + len(REGRESSION_CARDS) + len(CLASS_ANCHORS),
            "failed": failed}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", action="store_true",
                    help="the Gate 2 entry: grammar fixtures + residual "
                         "invariant + the pinned membership ratchet, one exit "
                         "code. Never run the three separately to save time.")
    ap.add_argument("--fixtures", action="store_true",
                    help="replay the grammar-shape fixtures and the seven "
                         "recorded regressions")
    ap.add_argument("--update-baseline", action="store_true",
                    help="accept the current membership/residual counts ON "
                         "PURPOSE. A membership count that FELL is a "
                         "regression until it is re-pinned here.")
    args = ap.parse_args()

    if args.gate or args.fixtures:
        f = fixtures()
        print(f"grammar fixtures: {f['n'] - len(f['failed'])}/{f['n']} pass")
        cov = anchor_coverage()
        print(f"class anchors   : {cov['anchored']}/{cov['live']} live classes"
              + (f"  UNCOVERED (blind to zero-sum movement): "
                 f"{', '.join(cov['uncovered'])}" if cov['uncovered'] else ""))
        for label, ctx, want, got in f["failed"]:
            print(f"    FAIL {label}: {ctx!r}")
            print(f"         want {want}, got {got}")
        if f["failed"] and not args.gate:
            return 1
        if not args.gate:
            return 0

    if args.gate:
        bad = len(fixtures()["failed"])
        # THE TRACKED FLOOR RUNS FIRST, because it is the only one of the two
        # membership checks that exists on a fresh clone.
        floor_fatal, floor_notes = assert_ratified_total()
        for note in floor_notes:
            print(f"RATIFIED TOTAL (reported, not fatal): {note}")
        for problem in floor_fatal:
            print(f"RATIFIED TOTAL: {problem}")
            bad += 1
        for stem in sorted(ACTION_VERBS):
            r = residual_invariant(stem, PERMANENT_TYPES)
            if r["unexplained"]:
                print(f"targeted-{stem}: {len(r['unexplained'])} UNEXPLAINED "
                      f"residual arm(s)")
                for name, arm, cls, _q in r["unexplained"]:
                    print(f"    {name}: arm {arm!r} -> {slug_for(stem, cls)}")
                bad += len(r["unexplained"])
        bad += ratchet.report(RATCHET_BASELINE, "object_lattice",
                              baseline_metrics(), args.update_baseline)
        if bad:
            print(f"\n  OBJECT LATTICE GATE FAILED ({bad}). No provenance "
                  f"write may proceed on this producer.")
            return 1
        print("\n  object lattice gate GREEN")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
