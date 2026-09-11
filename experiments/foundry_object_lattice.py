#!/usr/bin/env python3
"""The `targeted-<action>-<class>` OBJECT LATTICE — class extraction, derived.

THE LAW THIS IMPLEMENTS IS ALREADY RATIFIED, AND WAS NEVER IMPLEMENTED.
`docs/MASTER-HANDOFF-ADDENDUM-4.md` §4, the ratified rulings registry:

    | M8 generalized (b6 D3) | Multi-class targeted-<action> cards get every
    | applicable per-class tag, all action verbs, NEVER COMBO TAGS;
    | removal-for-breadth is wrong. |

restated in `docs/CODEBOOK-NAMING-GRAMMAR.md` §5:

    Per-object-class siblings are the law for every `targeted-<action>` family
    (M8 generalized, b6 D3): OR-shaped multi-class targets get every applicable
    class tag; the class lattice (`targeted-bounce-<class>`,
    `targeted-destruction-<class>`...) is a ratified grammar with virtual nodes.

Measured 2026-08-09, before this module existed: **zero cards in the codebook
carried two class siblings of one action family.** Putrefy — "Destroy target
artifact or creature. It can't be regenerated." — carried exactly one tag,
`rule:prevents-regeneration`, the rider and not the spell.

WHERE THE VOCABULARY COMES FROM, AND WHY NONE OF IT IS TYPED HERE
-----------------------------------------------------------------
* **CR 701.8a** — *"To destroy a permanent, move it from the battlefield to
  its owner's graveyard."* Only a PERMANENT can be destroyed, so the destroy
  lattice's class slot is the permanent-type list and not the card-type list.
* **CR 110.4** — *"There are six permanent types: artifact, battle, creature,
  enchantment, land, and planeswalker."* Closed, and parsed at run time.
* **CR 205.2a** — the fifteen card types, for actions that reach beyond the
  battlefield (exile, bounce and counter can name an instant or sorcery).
* **`validate_slug.OBJECT_VOCAB`** — the ratified grammar §5 OBJECT slot. Every
  class this module emits is asserted to be in it, so a CR term with no ratified
  slug token halts instead of minting vocabulary.

`_assert_vocabulary_agrees()` runs all three against each other at import. A
hand-list is a defect with a delay; three sources that must agree is the
closest thing to a guard against one of them silently moving.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
* **CR 701.8b** names exactly two routes to destruction: *"an effect that uses
  the word 'destroy'"* or the lethal-damage state-based action (704.5g). This
  module reads the WORD. That is not a heuristic boundary, it is one of the
  CR's own two, and the other route is not a targeted destroy at all.
* **AND-shaped targets are not OR-shaped ones.** CR 300.2 — *"Some objects have
  more than one card type (for example, an artifact creature)"* — so
  "destroy target artifact creature" names ONE object that must be both, while
  "artifact or creature" names either. M8 governs the OR case by name and is
  silent on AND. `classify_clause` reports AND separately (`conjunctive=True`)
  and never fuses it into a union; what tag it earns is unruled and is
  reported, not decided.
* It mints nothing and writes nothing. It is the measurement half.
"""
import argparse
import functools
import inspect
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                  # noqa: E402
import foundry_cr as cr                      # noqa: E402
import foundry_cr702_classes as crc          # noqa: E402
import validate_slug as vs                   # noqa: E402

# C8.5J: the standing ratchet now comes from the permanent package. The import
# sits AFTER `foundry_common`, which is what establishes the C8.5A package
# bootstrap -- this module adds no bootstrap and no sys.path mutation of its own.
#
# C8.5R adds the codebook READ beside it, for the same reason and under the same
# constraint. `codebook_store.read` takes an EXPLICIT path, so the path has to
# come from the layout owner -- and it comes from the SAME view bound below.
# Constructing a second view would state the repository root twice and move
# three delegation-census counts while changing nothing.
#
# THIS COMMENT MAY NOT SPELL THE VIEW CONSTRUCTOR OUT. `test_ratchet_capability`
# asserts the bound-view consumers build exactly one view by COUNTING that call
# in the source TEXT, so prose naming it is ingested as a second construction --
# the repository's standing "a document is an API" trap, aimed at a comment.
from mtj_foundry import codebook_store       # noqa: E402
from mtj_foundry.infra import ratchet              # noqa: E402
from mtj_foundry.paths import ProjectPaths   # noqa: E402

PATHS = ProjectPaths.for_root(fc.REPO_ROOT)
RATCHET_BASELINE = PATHS.foundry_audit_baseline


# ---------------------------------------------------------------------------
# S7 — THE PURE TARGET-CLASS CAPABILITY NOW LIVES IN THE PERMANENT SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 7 moved the category-(1) half of this module into
# `mtj_foundry.mtg.shapes.target_classes`: the CR-derived type vocabulary, the
# target noun-phrase boundaries, `classify_clause`, `clauses_for`,
# `classes_for_card`, and the `measure` / `residual_invariant` /
# `anchor_coverage` measurement surfaces. NO SECOND IMPLEMENTATION REMAINS HERE.
#
# What stays is everything the permanent MTG layer may not own: `slug_for` and
# the `rule:targeted-*` identity it builds, the ratified-membership floor and
# its assertion, the live codebook read, `validate_slug` governance, the
# baseline metrics, the audit and exclusivity reports, the locality binding, the
# fixtures, the ratchet wiring, the report writer and the CLI. Those are later
# slices.
#
# The vocabulary used to be derived AT IMPORT TIME by reading this repository's
# CR. That is exactly what an installed library may not do, so the derivation
# now takes the CR text and the CR 205 type vocabulary as ARGUMENTS and this
# boundary supplies them -- at import, in the same place and the same order.
from mtj_foundry.mtg.shapes import target_classes as _tc  # noqa: E402

LatticeError = _tc.LatticeError

# THE RATIFIED DET PREPROCESSING, INJECTED. `det_scan_texts` is
# `foundry_common`'s today and a later slice's tomorrow; the substrate receives
# it from here rather than importing it.
_tc.use_clause_text_rules(
    _tc.ClauseTextRules(fc, {"det_scan_texts": "det_scan_texts"}))


def _halting(fn):
    """Re-establish the historic `STOP — …` process contract at this boundary.

    A library may not exit a process it does not own, so the permanent module
    raises and this converts.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except LatticeError as exc:
            fc.halt(str(exc))
    return wrapper


# Re-export by REFERENCE, mechanically, so a name cannot be silently dropped on
# its way through the shell. The DERIVED vocabulary is excluded here and bound
# BELOW, after the build, because it does not exist yet at this point.
_NOT_REEXPORTED = {"annotations", "Any", "Callable"}
for _name, _obj in sorted(vars(_tc).items()):
    if _name.startswith("__") or _name in _NOT_REEXPORTED:
        continue
    if _name in _tc.DERIVED_STATE or _name in globals():
        continue
    if inspect.ismodule(_obj):
        continue
    globals()[_name] = _halting(_obj) if inspect.isfunction(_obj) else _obj
del _name, _obj


# ---------------------------------------------------------------------------
# The forms the legacy callers use. The CR LOCATION and the CORPUS are the
# boundary's; the permanent functions take text and cards.
# ---------------------------------------------------------------------------
def permanent_types(path: Path = None) -> set:
    """CR 110.4's six, parsed out of this boundary's CR edition."""
    return _halting(_tc.permanent_types)(cr.text(path) if path else cr.text())


def card_types(path: Path = None) -> set:
    """CR 205.2a's card types, parsed out of this boundary's CR edition."""
    return _halting(_tc.card_types)(cr.text(path) if path else cr.text())


def measure(stem: str, domain: set, cards: dict = None) -> dict:
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    return _halting(_tc.measure)(stem, domain, cards)


def residual_invariant(stem: str, domain: set, selftest: bool = False,
                       cards: dict = None) -> dict:
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    return _halting(_tc.residual_invariant)(stem, domain, cards,
                                            selftest=selftest)


def anchor_coverage(anchors=None, cards: dict = None) -> dict:
    if cards is None:
        cards, _, _ = fc.load_corpus_gated()
    return _halting(_tc.anchor_coverage)(
        CLASS_ANCHORS if anchors is None else anchors, cards)


def _assert_vocabulary_agrees() -> None:
    """Three sources, asserted against each other. CR 110.4 must be a subset of
    CR 205.2a (a permanent type is a card type), and every permanent type must
    already be a ratified grammar §5 OBJECT token — otherwise this module would
    be about to emit a slug out of vocabulary the grammar never ratified.

    It stays HERE, not in the substrate: `validate_slug.OBJECT_VOCAB` is
    ratification governance, and a check that an emitted SLUG is in vocabulary
    belongs with the emitter."""
    perms, cards_ = permanent_types(), card_types()
    if not perms <= cards_:
        fc.halt(f"CR 110.4 names permanent type(s) absent from CR 205.2a: "
                f"{sorted(perms - cards_)}")
    missing = sorted(perms - set(vs.OBJECT_VOCAB))
    if missing:
        fc.halt(f"CR 110.4 permanent type(s) {missing} are not in the ratified "
                f"grammar §5 OBJECT vocabulary (validate_slug.OBJECT_VOCAB). "
                f"Emitting a class slug for them would mint vocabulary; that "
                f"is a ratification, not a code change.")


# THE GUARD FIRES IN ITS ORIGINAL ORDER, before the subtype map is built —
# which is why it is called here and not after the derivation below.
_assert_vocabulary_agrees()
_tc.build_vocabulary(cr.text(), crc.type_vocabulary())

# Bound AFTER the build and by value, which is what they always were: the
# derivation runs exactly once, at this module's import, in the same place it
# used to. Nothing rebinds them afterwards, so there is no live-read problem to
# solve here -- unlike the shape substrate, whose state is built by a caller
# long after import.
PERMANENT_TYPES = _tc.PERMANENT_TYPES
CARD_TYPES = _tc.CARD_TYPES
SUBTYPE_TO_TYPE = _tc.SUBTYPE_TO_TYPE
AMBIGUOUS_SUBTYPES = _tc.AMBIGUOUS_SUBTYPES
_CONJUNCTIVE_RE = _tc._CONJUNCTIVE_RE


def slug_for(stem: str, cls: str = None) -> str:
    """`rule:targeted-destroy` / `rule:targeted-destroy-creature`.

    NOTE THE SPELLING. Grammar §5 line 651 still writes the lattice
    `targeted-destruction-<class>`, the PRE-RENAME form: `targeted-destruction`
    became `targeted-destroy` on 2026-08-09 (A15 ruling §6c) and §7 item 2 of
    that doc logs the grammar's stale spelling as open drift. The live axis is
    the authority, so this emits `-destroy-`; the grammar line needs a G4
    generator fix, not this module bending to it.

    Axis IDENTITY is the codebook's, never the MTG substrate's, so this stays
    above L2 whatever else moves."""
    base = f"rule:targeted-{stem}"
    return base if cls is None else f"{base}-{cls}"


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


DET_PATTERNS_PATH = fc.CONFIG_SEMANTIC / "det-patterns-v2.json"


def ratified_total() -> int:
    """The membership total the RATIFIED, TRACKED pattern row asserts.

    **THE LOCAL RATCHET CANNOT BE THE MEMBERSHIP FLOOR, BECAUSE IT IS NOT
    TRACKED.** Measured 2026-08-13: `experiments/out/` is gitignored, so
    `audit-baseline.json` is per-machine; `foundry_audit_baseline.report()`
    returns 0 when a section is unpinned, and `--gate` on a fresh clone printed
    `object lattice gate GREEN` having compared nothing. A guard that is absent
    by default on every new checkout is a local diagnostic, not a standing
    regression gate.

    `docs/det-patterns-v2.json` is tracked, reviewed and ratified, and its
    lattice row already carries the reviewed population as `corpus_hits`. So
    the floor is read from there rather than duplicated: one source of truth,
    already in git, already the thing Captain ratified.

    **`foundry_recorded_numbers.py` is the precedent** — Gate 2 row 11 does
    exactly this for the counts grammar §2 asserts, on the same reasoning:
    *"a wrong count there is not a stale note in a handoff, it is a wrong
    premise inside the document the extractor parses at run time."*
    """
    row = None
    doc = json.loads(DET_PATTERNS_PATH.read_text(encoding="utf-8"))
    for p in doc.get("patterns", []):
        if isinstance(p.get("lattice"), dict):
            row = p
            break
    if row is None:
        fc.halt(f"{DET_PATTERNS_PATH.name} carries no lattice row, so the "
                f"ratified membership total cannot be read. The lattice's "
                f"floor is the RATIFIED number, never a locally pinned one; "
                f"a missing row halts rather than falling back.")
    stems = set(row["lattice"]["stems"])
    if stems != set(ACTION_VERBS):
        fc.halt(f"the ratified lattice row covers {sorted(stems)} but this "
                f"module implements {sorted(ACTION_VERBS)}. The asserted total "
                f"counts a different population than the one measured here.")
    total = row.get("corpus_hits")
    if not isinstance(total, int):
        fc.halt(f"the ratified lattice row's corpus_hits is {total!r}, not an "
                f"integer. It is the membership floor and cannot be absent.")
    return total


def assert_ratified_total() -> tuple:
    """Live memberships vs the ratified total. A FALL is fatal; a RISE reports.

    Returns `(fatal, notes)`.

    **`corpus_hits` IS A MEASUREMENT AT PROBE TIME, NOT AN EQUALITY
    INVARIANT**, and an earlier version of this function got that wrong. Three
    independent pieces of repository evidence, measured 2026-08-13:

      * **three ratified patterns have already drifted from their recorded
        `corpus_hits` and Gate 2 is green** — `grants-unblockable-target` 35→34,
        `innate-unblockable` 183→184, `activated-grants-self-unblockable`
        25→26. Nothing in the repo asserts equality on this field, and never
        has. (`enters-tapped` and `imposes-enters-tapped` look far more drifted
        and are NOT: they are decided by `compute_special_hits`'s G2 subject
        split, so reading their `pattern` field measures the wrong thing.)
      * the sibling field is named **`codebook_n_members_at_probe`** — the
        `_at_probe` suffix is the schema saying point-in-time out loud.
      * the file's own `preprocessing_standard` records these counts BEING
        UPDATED on re-probe: *"Re-probing all patterns under this standard
        changed 5 hit counts … innate-unblockable (161->183)"*.

    So equality would freeze normal corpus growth: measured, a mere **+12 new
    cards** joining `destroy-creature` turned the gate RED on a fresh
    environment, which is a false alarm on the pipeline's ordinary weekly job.

    The direction is what carries the meaning, and that is not invented here —
    it is `foundry_audit_baseline`'s own ratchet semantics (`WORSE_IF_DOWN`
    fatal, better-direction movement reported) applied to a number that lives
    in git instead of in an ignored file. A FALL is the 2026-08-13 incident. A
    RISE is the corpus growing, and it is reported so a session states it
    rather than carrying it forward.

    **THIS TOTAL IS STRUCTURALLY BLIND TO REDISTRIBUTION.** A compensating
    −7/+7 across two classes nets zero and passes here; measured, on a fresh
    environment with no pinned section, the whole gate goes GREEN. That is the
    per-class ratchet's job and it is LOCAL. See §8b of
    docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md — the gap is recorded,
    not silently closed, because per-class tracked counts would be exactly the
    stronger invariant this docstring just disproved.
    """
    want = ratified_total()
    live = sum(measure(stem, PERMANENT_TYPES)["memberships"]
               for stem in sorted(ACTION_VERBS))
    if live == want:
        return [], []
    msg = (f"det-patterns-v2.json lattice row asserts {want:,} memberships; "
           f"the producer now yields {live:,} ({live - want:+,}). ")
    if live < want:
        return [msg + "MEMBERSHIPS WERE LOST. Re-review the sample sheet and "
                      "re-ratify corpus_hits on purpose — never edit the "
                      "number to match the code."], []
    return [], [msg + "Corpus growth or a recall improvement; the ratified row "
                      "is now stale. Re-review and re-pin corpus_hits when the "
                      "growth is accounted for."]


def baseline_metrics() -> dict:
    """Per-class membership counts, residual, and unexplained residual.

    **THE MEMBERSHIP COUNTS ARE PINNED SO THAT A REMOVAL IS FATAL.** They carry
    the `memberships` marker, which `foundry_audit_baseline.WORSE_IF_DOWN`
    reads, so a count that FALLS is a regression and has to be re-pinned on
    purpose. That is the half of the diff nothing watched: `e780842` removed
    170 memberships, verified 83, and the other 87 shipped unread.
    """
    memberships, residual, unexplained = {}, {}, {}
    for stem in sorted(ACTION_VERBS):
        m = measure(stem, PERMANENT_TYPES)
        memberships[stem] = {cls: n for cls, n in sorted(m["per_class"].items())}
        residual[stem] = len(m["residual"])
        unexplained[stem] = len(
            residual_invariant(stem, PERMANENT_TYPES)["unexplained"])
    return {"memberships": memberships, "residual": residual,
            "residual_unexplained": unexplained}


def audit(stem: str, domain: set) -> dict:
    """The negative controls. A guard that has never been shown to fail is not
    known to be a guard, so each of these was run against the live corpus and
    its output READ, card by card, before being written down here.

    NC1  every claimed card prints the word `destroy` — CR 701.8b's first of
         exactly two routes to destruction, and the only one this reads.
    NC2  a card with no targeted clause yields nothing (the extractor cannot
         invent a membership).
    NC3  quoted grants are reported, not silently included. All 16 were read
         2026-08-09: self-grants (Harmonic Sliver IS a Sliver) and Equipment
         grants (Heartseeker). Both genuinely hand the player that removal, so
         they are TAGGED — grammar §2's quoted-grant exclusion governs
         DELIVERY, and the class slot is an EFFECT question. Captain's ratified
         criterion is deck-building relevance.
    NC4  no emitted slug may fall outside the ratified grammar — every one is
         re-validated through `validate_slug`.
    """
    cards, _, _ = fc.load_corpus_gated()
    qspan = re.compile(r"[\"“]([^\"”]*)[\"”]")
    dest = _CLAUSE_RES[stem]
    no_verb, quoted_only, silent, bad_slug = [], [], 0, []
    # NC1 must test the PRINTED verb, not the slug stem. `bounce` is a ratified
    # stem that no card prints -- they print `return` -- so keying this on the
    # stem flagged every bounce card. A probe defect in the negative control
    # itself, which is the default outcome and why this note stays.
    verb_word = ACTION_VERBS[stem]["word"]
    for oid, card in cards.items():
        clauses = list(clauses_for(card, stem))
        if not clauses:
            silent += 1
            continue
        full = fc.full_oracle_text(card)
        if verb_word not in full.lower():
            no_verb.append(card["name"])
        spans = [m.span(1) for m in qspan.finditer(full)]
        hits = [m.start() for m in dest.finditer(full)]
        if hits and all(any(a <= h < b for a, b in spans) for h in hits):
            quoted_only.append(card["name"])

    for cls in sorted(domain | {f for f, _ in PERMANENT_FORMS}):
        slug = slug_for(stem, cls)
        v = vs.validate_slug(slug, definition=None, all_slugs=[])
        if not v["ok"]:
            bad_slug.append((slug, v.get("failures") or v.get("reason")))
    return {"nc1_no_verb": no_verb, "nc2_silent": silent,
            "nc3_quoted_only": quoted_only, "nc4_bad_slug": bad_slug}


def _locality_of(card: dict, quote: str) -> dict:
    """The semantic owner of one proving quote, for the review sheet.

    Consumes `foundry_locality` rather than re-deriving coordinates -- a second
    implementation of the resolution law is exactly the re-implementation
    defect class this repository keeps paying for.
    """
    import foundry_locality as loc
    r = loc.resolve(card, quote)
    out = {"status": r["status"], "owner": list(r["owner"]) if r["owner"] else None}
    if r["owner"]:
        h = loc.owning_header(card, r["owner"])
        if h["modal"]:
            out["modal_header"] = list(h["header"])
    return out


def exclusivity_report(cards: dict) -> list:
    """Cards whose lattice facts come from MUTUALLY EXCLUSIVE modes.

    This is the 41-card flattening population the locality ratification exists
    to fix, now reported with the owners that prove it. Reported, never
    written: what a consumer does with exclusivity is a consumer decision.
    """
    import foundry_locality as loc
    rows = []
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        owned = {}
        for stem in sorted(ACTION_VERBS):
            r = classes_for_card(card, stem, PERMANENT_TYPES)
            for cls in sorted(r["classes"]):
                res = loc.resolve(card, r["quotes"][cls])
                if res["status"] == loc.OWNER:
                    owned[slug_for(stem, cls)] = res["owner"]
        pairs = []
        keys = sorted(owned)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if loc.mutually_exclusive(card, owned[a], owned[b]):
                    pairs.append({"a": a, "b": b,
                                  "owner_a": list(owned[a]),
                                  "owner_b": list(owned[b])})
        if pairs:
            rows.append({"card": card["name"], "oracle_id": oid,
                         "exclusive_pairs": pairs})
    return rows


SAMPLE_REPORT_JSON = fc.FOUNDRY_OUT_DIR / "object_lattice_samples.json"
SAMPLE_REPORT_MD = fc.FOUNDRY_OUT_DIR / "object_lattice_samples.md"


def write_report(seed: int, n: int) -> dict:
    """The ratification packet: `det-patterns-v2.json`'s standing condition is a
    fixed-seed per-pattern sample, and ANY row failing its axis definition halts
    the pass before provenance writes. This writes that sheet for every class of
    every action.

    **Quotes go in the FILE, never to console (A14).** The console gets counts.

    It also emits the `det-patterns-v2.json` entries the lattice would need —
    as a PROPOSAL inside the report, not written into the ratified file. A
    `rule-derived` assertion may only cite `det-patterns-v2:<n>`
    (`SOURCE_REF_FAMILIES`), so those entries are what makes the membership
    legal, and minting them is Captain's."""
    import random
    cards, _, _ = fc.load_corpus_gated()
    cb_axes = None
    try:
        # C8.5R: the permanent read, at the layout owner's explicit path.
        #
        # THE HANDLER IS THE REASON THIS CONSUMER COULD MOVE FIRST, so it is not
        # tidied. `fc.halt` raises `SystemExit`, which `except Exception` does
        # NOT catch; `codebook_store` raises a `RuntimeError`, which it does. So
        # the repoint changes the CLASS of the failure, and whether that is
        # observable depends entirely on the enclosing handler. C8.5Q measured
        # all six seed consumers, and they fall into three groups, not two:
        #
        #   except BaseException  this module                  -> no delta
        #   except Exception      foundry_shape_extractor      -> hard exit becomes
        #                         foundry_system_map              a silent fallback
        #   no handler            foundry_cr_checks            -> exit 1 either way,
        #                         foundry_slug_dossier            but a clean `STOP -- `
        #                         foundry_consolidate_run1        becomes a traceback
        #
        # Only the first row is unobservable, which is why this slice is one file.
        # Here the failure is discarded either way and `cb_axes` stays None, which
        # the `if cb_axes else None` read below is already written for.
        cb_axes = codebook_store.read(PATHS.legacy_codebook_json)["axes"]
    except BaseException:
        pass

    actions = {}
    proposed_patterns = []
    for idx, stem in enumerate(sorted(ACTION_VERBS)):
        m = measure(stem, PERMANENT_TYPES)
        rng = random.Random(seed)
        by_class = defaultdict(list)
        for oid, r in m["hits"].items():
            for c in r["classes"]:
                by_class[c].append((oid, r["quotes"][c]))
        classes = {}
        for cls in sorted(by_class):
            pool = sorted(by_class[cls])
            slug = slug_for(stem, cls)
            exists = cb_axes.get(slug, {}).get("status") if cb_axes else None
            classes[cls] = {
                "slug": slug,
                "members": len(pool),
                "axis_status_today": exists or "ABSENT — self-instantiates per b6 §11.2",
                # SEMANTIC LOCALITY on NEW rule-derived output (roadmap step 3,
                # ratified 2026-08-13). The lattice is the first producer to
                # emit an address, and it emits into the REPORT only -- this
                # sheet is a review artifact, not provenance. Wiring an address
                # into the assertion payload `foundry_det_pass.cmd_apply`
                # WRITES is the backfill migration, which is a codebook
                # mutation under the backup law and is deliberately not done
                # here.
                "sample": [{"card": cards[o]["name"], "oracle_id": o,
                            "quote": q,
                            "locality": _locality_of(cards[o], q)}
                           for o, q in rng.sample(pool, min(n, len(pool)))],
            }
        actions[stem] = {
            "printed_verb": ACTION_VERBS[stem]["word"],
            "cards": m["cards"], "memberships": m["memberships"],
            "multi_class_cards": sum(v for k, v in m["n_classes"].items() if k > 1),
            "residual": [{"card": c, "clause": q} for c, q in m["residual"]],
            "conjunctive_cr300_2": m["conjunctive"],
            "classes": classes,
        }
        proposed_patterns.append({
            "slug": slug_for(stem),
            "lattice": True,
            "class_domain": "CR 110.4 permanent types + permanent/nonland/noncreature forms",
            "pattern": _CLAUSE_RES[stem].pattern,
            "status": "PROPOSED — not ratified, not written to det-patterns-v2.json",
            "cr_anchor": {"destroy": "701.8a/701.8b", "exile": "406.1",
                          "bounce": "zone change to hand"}.get(stem),
            "note": "One matcher -> N axes. det-patterns-v2.json's schema is "
                    "slug + one regex -> one axis; this needs the lattice "
                    "extension before it can be an entry.",
        })

    report = {
        "schema": "foundry-object-lattice-samples/1",
        "generated_by": "experiments/foundry_object_lattice.py",
        "law": "M8 generalized (b6 D3), MASTER-HANDOFF-ADDENDUM-4.md §4; "
               "lattice grammars b6 §11.2 (virtual nodes self-instantiate on "
               "first quote-verified member, no fresh ratification)",
        "record": "docs/OBJECT-LATTICE-2026-08-09.md",
        "seed": seed, "sample_size": n,
        "cr_sources": {
            "permanent_types_110_4": sorted(PERMANENT_TYPES),
            "card_types_205_2a": len(CARD_TYPES),
            "subtype_lists_205_3": "consumed from foundry_cr702_classes.type_vocabulary()",
        },
        "actions": actions,
        "mutually_exclusive_facts": exclusivity_report(cards),
        "proposed_det_patterns": proposed_patterns,
    }
    fc.write_json(SAMPLE_REPORT_JSON, report)

    lines = ["# OBJECT LATTICE — sample sheet for ratification", "",
             f"Seed `{seed}`, {n} rows per class. Record: "
             f"`docs/OBJECT-LATTICE-2026-08-09.md`.", "",
             "Standing condition (`det-patterns-v2.json`): **any sample row "
             "failing its axis definition halts the pass before provenance "
             "writes.**", ""]
    for stem, a in actions.items():
        lines += [f"## `targeted-{stem}` — printed *{a['printed_verb']}*", "",
                  f"{a['cards']:,} cards · **{a['memberships']:,} memberships** · "
                  f"{a['multi_class_cards']} multi-class · "
                  f"{len(a['residual'])} residual", ""]
        for cls, c in a["classes"].items():
            lines += [f"### `{c['slug']}` — {c['members']:,} members "
                      f"({c['axis_status_today']})", ""]
            for row in c["sample"]:
                lines.append(f"- **{row['card']}** — {row['quote']}")
            lines.append("")
        if a["residual"]:
            lines += ["**Residual (no class named):**", ""]
            lines += [f"- {r['card']} — {r['clause']}" for r in a["residual"][:20]]
            lines.append("")
    SAMPLE_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(SAMPLE_REPORT_JSON), "md": str(SAMPLE_REPORT_MD),
            "actions": {k: v["memberships"] for k, v in actions.items()}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--action", default="destroy", choices=sorted(ACTION_VERBS))
    ap.add_argument("--domain", default="permanent",
                    choices=["permanent", "card"],
                    help="permanent = CR 110.4 (destroy); card = CR 205.2a")
    ap.add_argument("--residual", action="store_true",
                    help="print the clauses that matched the action but named "
                         "NO class — where the defects are")
    ap.add_argument("--audit", action="store_true",
                    help="run the negative controls (NC1-NC4) and exit 1 on "
                         "any hard failure")
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
    ap.add_argument("--invariant", action="store_true",
                    help="the residual invariant: HALT if any residual clause "
                         "still carries a target arm resolving to a battlefield "
                         "class. Runs over ALL actions, not just --action.")
    ap.add_argument("--selftest", action="store_true",
                    help="negative control for --invariant: drop the zone "
                         "explanation, so it must report a failure")
    ap.add_argument("--samples", type=int, default=0, metavar="N",
                    help="fixed-seed sample of N cards per class, for the DET "
                         "standing condition's per-pattern verification")
    ap.add_argument("--seed", type=int, default=20260809)
    ap.add_argument("--report", type=int, default=0, metavar="N",
                    help="write the ratification packet (N rows per class) to "
                         "experiments/out/foundry/object_lattice_samples.{json,md}. "
                         "Quotes go in the FILE, never to console (A14).")
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

    if args.invariant:
        bad = 0
        for stem in sorted(ACTION_VERBS):
            r = residual_invariant(stem, PERMANENT_TYPES, selftest=args.selftest)
            print(f"targeted-{stem}: {len(r['explained'])} explained by a "
                  f"printed CR zone origin, {len(r['unexplained'])} UNEXPLAINED")
            for name, arm, cls, quote in r["unexplained"]:
                print(f"    {name}: arm {arm!r} -> {slug_for(stem, cls)}")
                print(f"        {quote}")
            bad += len(r["unexplained"])
        if bad:
            print(f"\n  RESIDUAL INVARIANT FAILED: {bad} live arm(s) in "
                  f"residual. The pass HALTS before provenance writes.")
            return 1
        print("\n  residual invariant holds")
        return 0

    if args.report:
        r = write_report(args.seed, args.report)
        print("wrote the ratification packet (quotes are in the files, not here)")
        print(f"  {r['json']}")
        print(f"  {r['md']}")
        for stem, n in r["actions"].items():
            print(f"  targeted-{stem}: {n:,} memberships")
        return 0

    domain = PERMANENT_TYPES if args.domain == "permanent" else CARD_TYPES
    print(f"CR 110.4 permanent types : {sorted(PERMANENT_TYPES)}")
    print(f"CR 205.2a card types     : {len(CARD_TYPES)}")
    print(f"domain for `{args.action}` : {args.domain} ({len(domain)})\n")

    m = measure(args.action, domain)
    print(f"cards with a targeted `{args.action}` clause and >=1 class: "
          f"{m['cards']:,}")
    print(f"memberships the ratified lattice implies : {m['memberships']:,}")
    print(f"  per class      : {dict(m['per_class'].most_common())}")
    print(f"  by class count : {dict(sorted(m['n_classes'].items()))}")
    print(f"  multi-class    : {sum(v for k, v in m['n_classes'].items() if k > 1):,}"
          f"  <- the population M8 is about")
    for combo, n in m["combos"].most_common(10):
        print(f"      {n:>4}  {' + '.join(combo)}")
    print(f"\n  CR 300.2 conjunctive ('artifact creature', ONE object): "
          f"{len(m['conjunctive'])}  <- UNRULED, reported not decided")
    print(f"  qualified clauses (restriction the class slot cannot hold): "
          f"{len(m['qualified']):,}")
    print(f"  residual (action matched, no class named): {len(m['residual'])}")
    if args.residual:
        for name, clause in m["residual"][:60]:
            print(f"      {name}: {clause}")

    if args.audit:
        a = audit(args.action, domain)
        print("\n--- negative controls " + "-" * 50)
        print(f"  NC1 claimed without the printed verb "
              f"`{ACTION_VERBS[args.action]['word']}` (CR 701.8b): "
              f"{len(a['nc1_no_verb'])}   must be 0")
        print(f"  NC2 cards yielding nothing                   : "
              f"{a['nc2_silent']:,}")
        print(f"  NC3 clause only inside a quoted grant        : "
              f"{len(a['nc3_quoted_only'])}   reported, tagged on purpose")
        for n in a["nc3_quoted_only"]:
            print(f"        {n}")
        print(f"  NC4 emitted slugs failing validate_slug      : "
              f"{len(a['nc4_bad_slug'])}   must be 0")
        for slug, why in a["nc4_bad_slug"]:
            print(f"        {slug}: {why}")
        if a["nc1_no_verb"] or a["nc4_bad_slug"]:
            print("\n  AUDIT FAILED")
            return 1
        print("\n  audit clean")

    if args.samples:
        import random
        rng = random.Random(args.seed)
        by_class = defaultdict(list)
        for oid, r in m["hits"].items():
            for c in r["classes"]:
                by_class[c].append((oid, r["quotes"][c]))
        print(f"\n--- fixed-seed samples (seed {args.seed}) " + "-" * 30)
        cards, _, _ = fc.load_corpus_gated()
        for cls in sorted(by_class):
            pool = sorted(by_class[cls])
            pick = rng.sample(pool, min(args.samples, len(pool)))
            print(f"\n  {slug_for(args.action, cls)}  (n={len(pool)})")
            for oid, q in pick:
                print(f"      {cards[oid]['name']:<34} | {q[:78]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
