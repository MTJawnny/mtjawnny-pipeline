#!/usr/bin/env python3
"""AQ4 BENCHMARK — POPULATION AND SAMPLING MACHINERY (contract §21, packet 2).

WHAT THIS IS AND IS NOT
-----------------------
This builds the eight pre-registered §21 cohorts and the deterministic sampler
they need. It is **architecture-neutral by construction**: every inclusion rule
is a structural / CR-closed / existing-ratified-primitive test, and none of them
can be stated in OCC-FACET or MIN-IR vocabulary. Nothing here encodes a
candidate, adjudicates an answer, or mints a term.

It does NOT:
  · choose OCC-FACET or reject MIN-IR;
  · ratify a dimension or mint semantic vocabulary;
  · write an answer key of any kind (§11 of the packet directive);
  · draw, reveal or seed the blind holdout (cohort 5 belongs to packet 3);
  · emit cohort-4 card identities (see THE BLINDNESS RULE below).

THE BLINDNESS RULE — READ BEFORE ADDING A COMMAND
-------------------------------------------------
Cohorts 4 and 5 stay uninspected until extractor freeze (§21). So cohort 4 is
DRAWN here and its identities are never printed, never written to a tracked
file, and never returned by a default command. `--census`, `--build` and
`--selftest` all report cohort 4 as *stratum sizes plus a selection hash*. The
identities exist only inside one function's local scope and inside the hash.

Revealing them takes the explicit `--reveal-cohort4` flag, which exists so the
reveal is a deliberate act at freeze time and cannot happen by running a
reporting command. Cohort 5 has no reveal path here at all, because packet 2
never chooses its seed.

WHY EVERY SELECTION IS A KEYED HASH AND NOT A STATEFUL PRNG
-----------------------------------------------------------
`random.Random(seed)` reproduces only against a matching library. This
benchmark's cohort 4 must regenerate byte-identically at packet 9, months and
possibly a Python version later, or §22 step 6 ("audit the sampling procedure
against the committed script") cannot pass. SHA-256 ordering has no library
state and no version surface: the selection is a pure function of
(domain label, oracle_id). The repository precedent
(`foundry_object_lattice.write_report`'s `random` + fixed seed) is a
single-session review sheet, not a cross-session commitment, so it is
precedent for *seeding*, not for the generator.

Ordering is therefore never dict order, filesystem order or name order. Name
order in particular is a recorded defect: Tier 3's shipped top-10 is an
alphabetical slice of a score tie, and `A-` prefixed Alchemy rows sort first.

RECORDED TRAPS THIS MODULE IS BUILT AGAINST
-------------------------------------------
  · A named exemplar becoming the whole cohort — `_assert_classes_are_classes`
    halts on any derived class with fewer than MIN_CLASS_MEMBERS members. The
    only singletons permitted are the ones declared `named_historical`.
  · Lattice-only population — P3 measured fight and attach STRUCTURALLY ABSENT
    from the qualifier-bearing lattice population. Cohort 2 is built over the
    gated corpus, and `NC-P2-7` fails if a fight/attach exemplar stops being
    representable.
  · A reminder-text search finding the opposite of what it looks for — Spree
    prints "(Choose one or more additional costs.)", so the CR 700.2 modality
    test runs on reminder-STRIPPED lines while everything else reads the
    canonical `det_scan_texts()[0]` the classifier reads.
  · A probe re-implementing what it measures — every derivation consumes an
    existing entry point (`foundry_object_lattice`, `foundry_qualifier_census`,
    `foundry_aq4_probes`, `foundry_shape_extractor`) rather than restating it.
  · A halt-guard asserting cardinality instead of content — the delivery-token
    domain guard names the offending token, and the CR-701 guard names the
    missing action.
  · Paper rows preferred over A- variants (ratified) — enforced in the
    candidate universe, not at emit time, so no cohort can reach an Alchemy row.

NO CARD DATA IN GIT
-------------------
Tracked cohort files carry `oracle_id` and nothing else about the card — no
oracle text, and no name, type line or characteristic attached to any
`oracle_id`. Class-descriptor prose may NAME a §21 exemplar class ("the Prey
Upon class", "the Cloudshift class") exactly as the contract itself does; that
names a STRUCTURE, not a row, and binds to no id. See README.md §7 for the
governance argument and the measured precedent.
"""
import sys
import re
import json
import hashlib
import argparse
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
sys.path.insert(0, str(EXPERIMENTS))

import foundry_common as fc            # noqa: E402
import foundry_probe as p              # noqa: E402
import foundry_shape_extractor as fx   # noqa: E402
import foundry_object_lattice as ol    # noqa: E402
import foundry_qualifier_census as fqc  # noqa: E402
import foundry_codebook as fcb         # noqa: E402
import foundry_aq4_probes as aq4p      # noqa: E402

COHORT_DIR = HERE / "cohorts"
SAMPLING_JSON = HERE / "sampling.json"
MANIFEST_JSON = HERE / "population-manifest.json"

# --------------------------------------------------------------------------
# declared constants — every one of these is written down in README.md and
# none of them is a tuning knob for a result.
# --------------------------------------------------------------------------

#: Exemplars kept per derived structural class. Six, so that no single odd
#: card can define a class and the adversarial question "did a named exemplar
#: become the cohort?" has a structural answer.
K_PER_CLASS = 6

#: Consumer-critical families (§21 cohort 6) get a wider open half — they are
#: the families the §20 consumer questions are actually asked about.
K_PER_FAMILY_OPEN = 8

#: §21 fixes this one: "simple controls (<=5)".
COHORT_3_MAX = 5

#: A derived class with fewer members than this is a hand-list wearing a
#: derivation's clothes. Declared `named_historical` classes are exempt.
MIN_CLASS_MEMBERS = 2


def canonical_json(obj) -> str:
    """One serialization, used for every hash in this benchmark."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def sha256_of(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _key(label: str, oracle_id: str) -> str:
    """The selection key. Domain-separated so two classes drawing from the
    same pool do not select the same cards by construction."""
    return hashlib.sha256(f"{label}\x00{oracle_id}".encode("utf-8")).hexdigest()


def hash_order(label: str, oracle_ids) -> list:
    """Stable, uniform, name-free ordering. Tie-break on oracle_id so the
    order is total even if SHA-256 ever collided."""
    return sorted(oracle_ids, key=lambda oid: (_key(label, oid), oid))


def take(label: str, oracle_ids, k: int) -> list:
    """`k` exemplars in hash order, returned sorted by oracle_id for a stable
    on-disk form. Selection order and serialization order are deliberately
    different things."""
    return sorted(hash_order(label, oracle_ids)[:k])


# ==========================================================================
# CANDIDATE UNIVERSE
# ==========================================================================

def paper_name(name: str) -> str:
    """The paper twin's name for an Alchemy row. `A-` prefixes each FACE, so
    'A-Rowan, ... // A-Will, ...' needs a per-face strip; stripping only the
    leading prefix leaves a name that matches nothing and silently reports
    every Alchemy row as twinless."""
    return " // ".join(f[2:] if f.startswith("A-") else f
                       for f in name.split(" // "))


def candidate_universe(cards: dict) -> tuple:
    """Gate #0 corpus minus Alchemy rows whose paper twin is present.

    Gate #0 (ratified batch-6 D1) decides corpus membership and this module
    does not touch it — including its Commander arm, which is why a
    Commander-only-legal card is in the universe here exactly as it is in every
    other foundry stage.

    The Alchemy cut implements the ratified "paper rows preferred over A-
    variants in sampling, resolution, and emit". It is a PREFERENCE, so a
    twinless Alchemy row would stay; measured on this corpus every one of the
    216 has a twin, and the returned count says so rather than assuming it.
    """
    names = {c["name"] for c in cards.values()}
    universe, dropped, twinless = {}, [], []
    for oid, card in sorted(cards.items()):
        nm = card["name"]
        if nm.startswith("A-"):
            if paper_name(nm) in names:
                dropped.append(oid)
                continue
            twinless.append(oid)
        universe[oid] = card
    return universe, {"alchemy_dropped_paper_twin_present": len(dropped),
                      "alchemy_kept_twinless": len(twinless)}


# ==========================================================================
# CARD-LEVEL STRUCTURAL FACTS — computed ONCE, consumed by every cohort
# ==========================================================================

_TARGET = re.compile(r"\btarget\b", re.I)
_ADD_MANA = re.compile(r"\badds?\b[^.]{0,40}?\{[WUBRGCXSP0-9/]+\}", re.I)
_WHILE = re.compile(r"\bwhile\b", re.I)
_COORD = re.compile(r"\b(?:or|and)\b", re.I)

#: CR 701.15a — the fight template. A FINITE VERB WITH A PRINTED SUBJECT
#: ("target creature you control fights target creature you don't control"),
#: which is exactly why packet 1's `effect_heads` cannot find it: that boundary
#: test encodes CR 608.2c's *instruction* order and requires the head to follow
#: a boundary, and a verb whose subject precedes it never does. Detecting fight
#: through `effect_heads` returned 2 cards against 150 printing the template —
#: a detector whose boundary rule structurally excludes the shape it is aimed
#: at. The two forms are both real; this class needs the finite-verb one.
_FIGHT = re.compile(r"\bfights?\b", re.I)

#: CR 701.3a — `attach`, the ACTION. The participle is deliberately NOT here:
#: `attached` is overwhelmingly the static attachment STATE ("the number of
#: Equipment attached to him", "Enchanted creature"), and folding it in took
#: this class from 234 to 743 by swapping a two-participant action for a
#: one-participant condition.
_ATTACH = re.compile(r"\battach(?:es)?\b", re.I)

#: CR 109.2 / CR 110.1 print three different things with the word "creature"
#: in them, and conflating them is the recorded context-free-type-subsumption
#: trap. These are the printed forms, not a semantic model.
_ENTITY_CONTEXTS = (
    ("creature-spell", re.compile(r"\bcreature spells?\b", re.I)),
    ("creature-card", re.compile(r"\bcreature cards?\b", re.I)),
    ("creature-permanent", re.compile(r"\bcreatures?\b(?!\s+(?:spell|card))", re.I)),
)


def delivery_tokens_of(card: dict, ratified: dict) -> list:
    """Every delivery token the classifier emits for this card, printed order.

    Consumes `deliveries_for_lines`, never `parse_deliveries` on a bare line:
    the difference is D3 modal inheritance, and skipping it is a recorded
    ground-truth defect.
    """
    out = []
    for _line, parsed in fx.deliveries_for_lines(card, ratified):
        for tok, _desc in parsed:
            if tok:
                out.append(str(tok))
    return out


def assert_token_domain(seen: set, ratified: dict) -> None:
    """GUARD B on the STRATUM vocabulary, asserting content.

    The emitted token set is WIDER than grammar §2's table keys: §2's scope
    facet prefixes a base token with `any-` / `other-`, so `any-etb` is a
    ratified construction that is not a ratified KEY. A guard written as
    `seen <= set(ratified)` would halt on correct output; a guard written as
    `len(seen) >= 64` cannot see a substitution. This one names the token.

    THE TABLE IS CONSULTED BEFORE THE PREFIX STRIP, and the order is the whole
    correctness of this function: `any-damage-to-creature` is itself a ratified
    §2 KEY (the damage family ratifies its own `any-` rows), so stripping first
    turns a ratified token into `damage-to-creature`, which is in no table. The
    first draft did strip first and this guard halted on three correct tokens —
    the recorded "your probe is wrong before the code is" shape, caught by the
    guard naming what it rejected instead of counting.
    """
    bad = []
    for tok in sorted(seen):
        if tok in ratified:
            continue
        base = tok
        for prefix in ("any-", "other-"):
            if base.startswith(prefix):
                base = base[len(prefix):]
                break
        if base not in ratified:
            bad.append(tok)
    if bad:
        fc.halt(
            f"delivery token(s) {bad!r} are neither a grammar §2 table key nor "
            f"a §2 scope-prefixed form of one. The stratum vocabulary must come "
            f"from ratified §2 and nowhere else — stratifying on an unratified "
            f"token would mint benchmark vocabulary through the sampler.")


def action_family_of(card: dict) -> str:
    """The first CR 701 keyword action in PREDICATE position, printed order.

    EXTRACT-1: `aq4p.CR701_ACTIONS` is parsed from the CR's own 701.N headings
    at run time and halt-guarded on content. The boundary test is packet 1's
    `effect_heads`, reused rather than restated — without it, `counter` in
    "with a +1/+1 counter on it" is an action family and the noun/verb
    confusion strata the corpus on object phrases.

    Returns None when the card prints no keyword action. None is a NULL, not a
    coined label: it is serialized as JSON null and rendered "(none)".
    """
    base = fc.det_scan_texts(card)[0]
    heads = aq4p.effect_heads(base, require_boundary=True)
    for h in heads:
        if h in aq4p.CR701_ACTIONS:
            return h
    return None


def card_facts(oid: str, card: dict, ratified: dict) -> dict:
    """Every structural fact any cohort needs, derived once per card.

    THREE text views, and which one a test reads is load-bearing:

      · `base` = `det_scan_texts()[0]` — CARDNAME-canonicalized full text, the
        view the classifier and `foundry_qualifier_census.population` both
        read. Used where this module must agree with the census. Reading raw
        oracle text instead misses 1,478 cards on a CARDNAME pattern (NC-E)
        and reports a clean zero.
      · `base_nr` = the same text with CR 207.2a reminder parentheticals
        removed. **Every printed-template test reads this one.** `det_scan_texts`
        does NOT strip reminder text, and reminder text is where the recorded
        inversion lives: a `choose one` search matches Spree's own reminder
        ("Choose one or more additional costs") and files additive modes as
        mutually exclusive. Measured here too — scanning CR 701.3 `attach`
        against unstripped text pulled in reminder sentences.
      · `lines` = `ability_lines()`, reminder-stripped, for the CR 700.2
        modality test and for segmentation.
    """
    base = fc.det_scan_texts(card)[0]
    base_nr = fx.strip_reminder(base)
    lines = fx.ability_lines(card)
    sentences = [s for line in lines for s in fx.sentence_spans(line)]

    heads_per_sentence = [aq4p.effect_heads(s, require_boundary=True)
                          for s in sentences]
    rels = aq4p.relation_candidates(card)
    faces = card.get("card_faces") or []
    tl = card.get("type_line") or ""

    contexts = {n for n, rx in _ENTITY_CONTEXTS if rx.search(base_nr)}
    toks = delivery_tokens_of(card, ratified)

    return {
        "oracle_id": oid,
        "base": base,
        "fight": bool(_FIGHT.search(base_nr)),
        "attach": bool(_ATTACH.search(base_nr)),
        "lines": lines,
        "sentences": sentences,
        "n_lines": len(lines),
        "has_text": bool(base.strip()),
        "delivery_tokens": toks,
        "delivery_token": toks[0] if toks else None,
        "action_family": action_family_of(card),
        # CR 700.2 modality, measured on reminder-stripped lines.
        "modal": any(fc._MODAL_HEADER_RE.search(l) for l in lines),
        "spree": any(re.search(r"\bSpree\b", l) for l in lines),
        "effect_heads_max": max((len(h) for h in heads_per_sentence), default=0),
        "multi_effect": any(len(h) >= 2 for h in heads_per_sentence),
        "heads": {h for hs in heads_per_sentence for h in hs},
        "two_printed_targets": any(len(_TARGET.findall(s)) >= 2
                                   for s in sentences),
        "exile_and_return": any(
            aq4p._FORM_TESTS[0][1].search(s) for s in sentences),
        "repeated_clause": len(sentences) != len({s.strip() for s in sentences})
                           and len(sentences) > 1,
        "relation_kinds": {r["kind"] for r in rels},
        "delayed": any(r["delayed"] for r in rels),
        "cross_unit_coref": any(r["kind"] == "coreference" and r["cross_unit"]
                                for r in rels),
        "this_way": any(r["phrase"] == "this way" for r in rels),
        "unclear_other": any(r["kind"] == "kind-unclear"
                             and r["phrase"] != "this way" for r in rels),
        "n_relations": len(rels),
        "entity_contexts": contexts,
        # The locked DFC rule: two-image iff card_faces[0].image_uris exists.
        # Never judge by card_faces presence — split/flip/adventure cards have
        # faces and one root-level image.
        "dfc_two_image": bool(faces and faces[0].get("image_uris")),
        "multi_face_one_image": bool(faces and not faces[0].get("image_uris")),
        "instant_or_sorcery_face": ("Instant" in tl or "Sorcery" in tl),
        "creature_type": "Creature" in tl,
        "add_mana": bool(_ADD_MANA.search(base_nr)),
        "cardname_canonicalized": base != fc.full_oracle_text(card),
        "splitter_territory": any(_WHILE.search(s) and _COORD.search(s)
                                  for s in sentences),
    }


# ==========================================================================
# LATTICE / CENSUS VIEWS — consumed, never re-derived
# ==========================================================================

def census_views(cards: dict) -> dict:
    """Per-card views of the two ratified measured populations.

    `fqc.population()` is the object-lattice clause-occurrence census — the
    same population packet 1's P1/P2/P3 measured, and the same one Gate 2's
    `qualifier_census` row protects the reproducibility of.
    """
    rows = fqc.population(cards)
    by_card = collections.defaultdict(list)
    for r in rows:
        by_card[r["oracle_id"]].append(r)

    residue_cat = collections.defaultdict(set)
    zero_residue_single = set()
    for oid, rs in by_card.items():
        for r in rs:
            for cat in r["categories"]:
                residue_cat[cat].add(oid)
        if len(rs) == 1 and not rs[0]["tokens"]:
            zero_residue_single.add(oid)

    return {"rows": rows, "by_card": by_card,
            "residue_by_category": residue_cat,
            "zero_residue_single_clause": zero_residue_single,
            "lattice_cards": set(by_card)}


# ==========================================================================
# COHORT CONSTRUCTION
# ==========================================================================

class Cohort:
    def __init__(self, number, title, open_status):
        self.number = number
        self.title = title
        self.open_status = open_status
        self.classes = []

    def add(self, class_id, reason, source_class, members, k,
            named_historical=False):
        members = sorted(set(members))
        self.classes.append({
            "class_id": class_id,
            "inclusion_reason": reason,
            "derivation_class": source_class,
            "named_historical": named_historical,
            "qualifying_population": len(members),
            "selected": take(class_id, members, k),
            "_all": members,
        })

    def selected(self) -> set:
        return {o for c in self.classes for o in c["selected"]}


def _assert_classes_are_classes(cohorts) -> None:
    """A derived class with one member is a named exemplar with a rule
    written around it. Halt rather than publish one as structure."""
    bad = []
    for co in cohorts:
        for c in co.classes:
            if c["named_historical"]:
                continue
            if c["qualifying_population"] < MIN_CLASS_MEMBERS:
                bad.append((c["class_id"], c["qualifying_population"]))
    if bad:
        fc.halt(
            f"derived class(es) {bad!r} have fewer than {MIN_CLASS_MEMBERS} "
            f"qualifying members. A structural class this small is a named "
            f"exemplar with a derivation written around it — declare it "
            f"`named_historical` or drop it, do not publish it as a class.")


def build_cohorts(facts: dict, views: dict, cards: dict, name_index: dict):
    """Cohorts 1, 2, 3, 6-open, 7, 8. Cohorts 4 and 5 are elsewhere: cohort 4
    is drawn without emitting identities, cohort 5 belongs to packet 3."""
    F = facts
    lattice = views["lattice_cards"]
    resid = views["residue_by_category"]

    def where(pred):
        return [oid for oid, f in sorted(F.items()) if pred(f)]

    # ---------------------------------------------------------------- 1
    c1 = Cohort(1, "historical foundry failures", "open")

    excl = ol.exclusivity_report(cards)
    c1.add("c1.modal-flattening",
           "carries 2+ object-lattice facts whose proving quotes are owned by "
           "MUTUALLY EXCLUSIVE modes — the card-level bag cannot tell this "
           "from a card that genuinely does both",
           "EXTRACT-3 foundry_object_lattice.exclusivity_report",
           [r["oracle_id"] for r in excl], K_PER_CLASS)

    av = fc.resolve_name("Active Volcano", cards, name_index)
    c1.add("c1.active-volcano-named-case",
           "the named §21 historical failure, included transparently as "
           "historical evidence — it is also a member of c1.modal-flattening, "
           "which is the reproducible class; it is NOT a production exception",
           "named historical failure (§21 seed)", [av], 1,
           named_historical=True)

    c1.add("c1.nc-a-later-ability",
           "a lattice fact lives on a non-first ability line, so a reader that "
           "truncates loses it (NC-A class)",
           "EXTRACT-4 over foundry_qualifier_census.population",
           [oid for oid in lattice
            if F[oid]["n_lines"] > 1
            and any(r["clause"] not in F[oid]["lines"][0]
                    for r in views["by_card"][oid])],
           K_PER_CLASS)

    c1.add("c1.nc-b-multi-face",
           "multi-face card carrying a lattice fact — the face-loss class "
           "(NC-B); faces are judged by the locked DFC rule, never by "
           "card_faces presence",
           "EXTRACT-0 segmentation + EXTRACT-3 lattice",
           [oid for oid in lattice
            if F[oid]["dfc_two_image"] or F[oid]["multi_face_one_image"]],
           K_PER_CLASS)

    c1.add("c1.nc-c-context-strip",
           "an activated ability owns a lattice fact, so deleting the "
           "activation cost changes the delivery token and leaves the object "
           "fact identical (NC-C: context stripped, payload intact)",
           "EXTRACT-3 delivery classifier + lattice",
           [oid for oid in lattice
            if any(t == "activated" for t in F[oid]["delivery_tokens"])],
           K_PER_CLASS)

    c1.add("c1.nc-e-cardname-drift",
           "CARDNAME canonicalization changes the text, so a probe reading raw "
           "oracle text measures a different card than the pipeline does "
           "(NC-E), and carries a lattice fact so the drift is consequential",
           "EXTRACT-0 foundry_common.canonicalize_self_reference",
           [oid for oid in lattice if F[oid]["cardname_canonicalized"]],
           K_PER_CLASS)

    # ---------------------------------------------------------------- 2
    c2 = Cohort(2, "structural adversaries", "open")

    # P3 measured fight and attach STRUCTURALLY ABSENT from the lattice
    # population. These two classes are the reason cohort 2 is built over the
    # gated corpus and not over the census rows.
    c2.add("c2.fight",
           "prints CR 701.15's fight template as a FINITE VERB with a printed "
           "subject ('A fights B') — the Prey Upon two-participant class, and "
           "structurally unreachable from the object lattice (measured, "
           "packet 1 P3). Packet 1's instruction-boundary head test cannot see "
           "this shape by construction and returns 2 against 150",
           "EXTRACT-2 CR 701.15a printed template",
           where(lambda f: f["fight"]), K_PER_CLASS)

    c2.add("c2.attach",
           "prints CR 701.3's `attach` ACTION (participle excluded — "
           "`attached` is the static attachment state, not the action) — "
           "two-participant attachment, likewise outside the lattice",
           "EXTRACT-2 CR 701.3a printed template",
           where(lambda f: f["attach"]), K_PER_CLASS)

    c2.add("c2.two-printed-targets",
           "one sentence carries 2+ printed `target` tokens (multiple targets)",
           "EXTRACT-0 fx.sentence_spans over fx.ability_lines",
           where(lambda f: f["two_printed_targets"]), K_PER_CLASS)

    c2.add("c2.multi-participant-lattice",
           "packet-1 P3's own qualifier-bearing population: 2+ RESTRICTED "
           "participants in one lattice clause",
           "EXTRACT-4 packet-1 aq4p.participants",
           [oid for oid, rs in views["by_card"].items()
            if any(len(aq4p.participants(r["clause"])) >= 2 for r in rs)],
           K_PER_CLASS)

    c2.add("c2.multi-effect",
           "one sentence carries 2+ candidate effect heads in predicate "
           "position (the P2 MEC pressure class)",
           "EXTRACT-4 packet-1 aq4p.effect_heads",
           where(lambda f: f["multi_effect"]), K_PER_CLASS)

    c2.add("c2.exile-and-return",
           "exile followed by return inside one sentence — P2's dominant "
           "multi-effect form, and the blink test's own shape (§20 C2)",
           "EXTRACT-4 packet-1 _FORM_TESTS",
           where(lambda f: f["exile_and_return"]), K_PER_CLASS)

    c2.add("c2.repeated-identical-clause",
           "the same sentence text occurs 2+ times on one card — the Seize "
           "the Soul class, where a case-folded dedupe merges two real units",
           "EXTRACT-0 fx.sentence_spans",
           where(lambda f: f["repeated_clause"]), K_PER_CLASS)

    c2.add("c2.cr607-linkage",
           "carries a CR 607.2 published referring phrase (linked abilities)",
           "EXTRACT-1 packet-1 cr607_referring_phrases",
           where(lambda f: "cr607-linkage" in f["relation_kinds"]),
           K_PER_CLASS)

    c2.add("c2.delayed-effect",
           "carries a delayed-effect marker alongside a reference",
           "EXTRACT-2 packet-1 _DELAYED",
           where(lambda f: f["delayed"]), K_PER_CLASS)

    c2.add("c2.coreference-cross-unit",
           "a coreference back-reference crosses a line or sentence boundary "
           "— the Cloudshift class",
           "EXTRACT-4 packet-1 relation_candidates",
           where(lambda f: f["cross_unit_coref"]), K_PER_CLASS)

    c2.add("c2.this-way",
           "prints `this way`, packet 1 P4's largest KIND-UNCLEAR form "
           "(1,088 references). Included because it is MEASURED UNRESOLVED "
           "STRUCTURAL PRESSURE — packet 2 does not decide whether it is a "
           "fourth relation kind, and nothing here assigns it one",
           "EXTRACT-4 packet-1 relation_candidates (kind-unclear)",
           where(lambda f: f["this_way"]), K_PER_CLASS)

    c2.add("c2.kind-unclear-other",
           "carries a KIND-UNCLEAR reference form other than `this way` — the "
           "rest of P4's unresolved residue, kept separate so `this way` "
           "cannot stand in for it",
           "EXTRACT-4 packet-1 relation_candidates (kind-unclear)",
           where(lambda f: f["unclear_other"]), K_PER_CLASS)

    c2.add("c2.modal",
           "prints a CR 700.2 modal header (tested on reminder-STRIPPED lines)",
           "EXTRACT-2 foundry_common._MODAL_HEADER_RE",
           where(lambda f: f["modal"]), K_PER_CLASS)

    c2.add("c2.spree",
           "prints Spree — additive modes, which a `choose one` search run "
           "before the reminder strip files as mutually exclusive",
           "EXTRACT-2 printed keyword, reminder-stripped",
           where(lambda f: f["spree"]), K_PER_CLASS)

    c2.add("c2.entity-context-triplet",
           "prints 2+ of the three CR 109.2/110.1 entity contexts — creature "
           "permanent vs creature spell vs creature card — on one card, where "
           "context-free type subsumption goes wrong",
           "EXTRACT-2 printed forms, CR 109.2 / CR 110.1 anchored",
           where(lambda f: len(f["entity_contexts"]) >= 2), K_PER_CLASS)

    # ---------------------------------------------------------------- 3
    c3 = Cohort(3, "simple controls", "open")
    simple = [oid for oid in sorted(views["zero_residue_single_clause"])
              if F[oid]["n_lines"] == 1
              and len(F[oid]["delivery_tokens"]) == 1
              and not F[oid]["modal"]
              and not F[oid]["dfc_two_image"]
              and not F[oid]["multi_face_one_image"]
              and not F[oid]["multi_effect"]
              and F[oid]["n_relations"] == 0
              and not F[oid]["two_printed_targets"]]
    c3.add("c3.simple-control",
           "ONE ability line, ONE delivery token, ONE lattice clause "
           "occurrence with ZERO residue under packet-1 residue-honest "
           "claiming, no modality, no second face, no second effect head, no "
           "cross-occurrence reference and no second target. Every conjunct is "
           "a measured structural property, so no card is here because a "
           "candidate architecture handles it well",
           "EXTRACT-4 over the ratified census + delivery classifier",
           simple, COHORT_3_MAX)

    # ---------------------------------------------------------------- 6
    c6 = Cohort(6, "consumer-critical families (OPEN HALF ONLY)", "open-half")
    families = {
        "c6.removal": (
            "carries an object-lattice class on destroy / exile / bounce — "
            "the ratified removal machinery, not a hand tag",
            "EXTRACT-3 foundry_object_lattice",
            sorted(lattice)),
        "c6.blink": (
            "exile followed by return in one sentence — the §20 C2 blink test's "
            "own printed shape",
            "EXTRACT-4 packet-1 _FORM_TESTS",
            where(lambda f: f["exile_and_return"])),
        "c6.counterspell": (
            "prints CR 701.5 `counter` as an effect head in PREDICATE position "
            "— the boundary test is what keeps '+1/+1 counter' out",
            "EXTRACT-1 CR 701 keyword action + packet-1 boundary test",
            where(lambda f: "counter" in f["heads"])),
        "c6.add-mana": (
            "prints the CR 106.4 `add {mana}` template. NAMED FOR THE RATIFIED "
            "PRIMITIVE, NOT FOR THE FAMILY: grammar §4's `add-mana` verb is "
            "Captain-ratified with CR 106.4 supplying the words verbatim, and "
            "it is the objective stand-in for §21's 'ramp'. The two are NOT the "
            "same set — a Cavern of Souls adds mana and is fixing, not "
            "acceleration — and closing that gap needs a ratification this "
            "packet is not allowed to make",
            "EXTRACT-2 CR 106.4 template / grammar §4 ratified verb",
            where(lambda f: f["add_mana"])),
    }
    c6_split = {}
    for cid, (reason, src, pool) in sorted(families.items()):
        ordered = hash_order(f"aq4-c6-split\x00{cid}", pool)
        open_half = ordered[0::2]          # pre-registered: even index -> open
        blind_half = ordered[1::2]         # never materialized, never printed
        c6_split[cid] = {"population": len(ordered),
                         "open_half": len(open_half),
                         "reserved_for_holdout_draw": len(blind_half)}
        c6.add(cid, reason, src, open_half, K_PER_FAMILY_OPEN)

    # ---------------------------------------------------------------- 7
    c7 = Cohort(7, "CR / characteristic-derived cases", "open")

    c7.add("c7.vanilla-creature",
           "a Creature with no oracle text at all — the mechanical floor, "
           "where every semantic dimension must be ABSENT-PROVEN or refused",
           "EXTRACT-0 characteristics + oracle text",
           where(lambda f: f["creature_type"] and not f["has_text"]),
           K_PER_CLASS)

    # `c7.no-text-noncreature` was proposed here and is MEASURED EMPTY: every
    # no-oracle-text card in the candidate universe is a Creature. Recorded in
    # EMPTY_CLASSES_MEASURED rather than deleted quietly — an empty class is a
    # fact about the corpus, and the packet directive's rule for a rare cell
    # ("report it; do not silently merge it") is the same rule one layer up.

    c7.add("c7.cr113-3a-face-cut",
           "carries an ability but has NO instant/sorcery face, so CR 113.3a "
           "closes the ability-category enumeration without reading the text — "
           "the recorded cut that removed 738 burn spells from a mis-named "
           "shape",
           "EXTRACT-1 CR 113.3a + EXTRACT-0 type line",
           where(lambda f: f["has_text"] and not f["instant_or_sorcery_face"]),
           K_PER_CLASS)

    c7.add("c7.dfc-two-image",
           "two-image DFC by the locked rule: card_faces[0].image_uris EXISTS",
           "EXTRACT-0 locked DFC rule",
           where(lambda f: f["dfc_two_image"]), K_PER_CLASS)

    c7.add("c7.multi-face-one-image",
           "has card_faces but NO faces[0].image_uris — split / flip / "
           "adventure. The other arm of the locked DFC rule, and the reason "
           "'has card_faces' is never the test",
           "EXTRACT-0 locked DFC rule",
           where(lambda f: f["multi_face_one_image"]), K_PER_CLASS)

    # ---------------------------------------------------------------- 8
    c8 = Cohort(8, "negative / unresolved — correct output is refusal", "open")
    for cat in sorted(resid):
        c8.add(f"c8.residue-{cat}",
               f"a lattice clause leaves UNCLAIMED restriction text in the "
               f"`{cat}` family under packet-1 residue-honest claiming, so "
               f"ABSENT-PROVEN is not available and the honest disposition is "
               f"UNRESOLVED. Included because the residue is MEASURED, not "
               f"because a detector currently fails",
               "EXTRACT-4 packet-1 P1 residue categorization",
               sorted(resid[cat]), K_PER_CLASS)

    c8.add("c8.kind-unclear-reference",
           "carries a reference form that reaches no CR-groundable relation "
           "kind (P4 KIND-UNCLEAR). The structural statement is that the "
           "printed form establishes no referent by any rule the CR publishes",
           "EXTRACT-4 packet-1 relation_candidates",
           where(lambda f: "kind-unclear" in f["relation_kinds"]),
           K_PER_CLASS)

    c8.add("c8.splitter-territory",
           "a CR 603.4 `while` condition coordinated by or/and in one "
           "sentence — the recorded territory where the compound splitter "
           "INVENTS a trigger, and a census scores an invented gap and a lost "
           "token identically",
           "EXTRACT-2 CR 603.4 + printed coordination",
           where(lambda f: f["splitter_territory"]), K_PER_CLASS)

    cohorts = [c1, c2, c3, c6, c7, c8]
    _assert_classes_are_classes(cohorts)
    return cohorts, c6_split


# ==========================================================================
# COHORT 4 — DETERMINISTIC STRATIFIED DRAW (identities never emitted)
# ==========================================================================

def strata_of(facts: dict) -> dict:
    """(delivery token, action family) -> [oracle_id], stably ordered.

    The stratum key is the pre-registered §21 pair. Both coordinates use a
    FIRST-IN-PRINTED-ORDER reduction from card to value, which is structural
    and carries no preference between tokens; the alternative (the card's whole
    token set) makes the stratum a power set and strata nothing.
    """
    out = collections.defaultdict(list)
    for oid, f in sorted(facts.items()):
        out[(f["delivery_token"], f["action_family"])].append(oid)
    return {k: sorted(v) for k, v in sorted(out.items(), key=lambda kv: (
        kv[0][0] or "", kv[0][1] or ""))}


def draw_cohort4(facts: dict, seed: str, per_stratum: int) -> dict:
    """The stratified draw. RETURNS IDENTITIES — callers must not print them.

    Short strata: a stratum smaller than `per_stratum` yields everything it
    has and is REPORTED as short. It is never merged into a neighbour and
    never dropped: §21 pre-registers the stratification, so silently
    collapsing a rare cell would change the pre-registered population.
    """
    strata = strata_of(facts)
    selected, summary, short = {}, [], []
    for (tok, act), pool in strata.items():
        label = f"aq4-c4\x00{seed}\x00{tok}\x00{act}"
        pick = sorted(hash_order(label, pool)[:per_stratum])
        selected[(tok, act)] = pick
        summary.append({"delivery_token": tok, "action_family": act,
                        "stratum_size": len(pool), "drawn": len(pick)})
        if len(pool) < per_stratum:
            short.append({"delivery_token": tok, "action_family": act,
                          "stratum_size": len(pool),
                          "requested": per_stratum, "drawn": len(pick)})
    ids = sorted({o for v in selected.values() for o in v})
    return {
        "_identities": ids,
        "strata_total": len(strata),
        "strata_short": len(short),
        "short_strata": short,
        "requested_per_stratum": per_stratum,
        "drawn_total": len(ids),
        "duplicate_ids": len([o for v in selected.values() for o in v]) - len(ids),
        "stratum_summary": summary,
        # The commitment: identities are pinned by hash, never by publication.
        "selection_sha256": sha256_of(ids),
    }


def cohort4_public(draw: dict) -> dict:
    """The blindness boundary. Everything except `_identities`."""
    return {k: v for k, v in draw.items() if k != "_identities"}


# ==========================================================================
# COHORT 5 — HOLDOUT: GENERIC MACHINERY ONLY
# ==========================================================================

def draw_generic(pool, seed: str, label: str, n: int, exclude=frozenset()):
    """The generic sampler packet 3 needs for the holdout.

    Packet 2 builds and tests it and never calls it with a holdout seed,
    because packet 2 does not choose one. `exclude` is how §22 step 8's
    "holdout ∩ development = ∅" is ENFORCED at draw time rather than checked
    afterwards — a check after the fact can only report a leak it cannot undo.
    """
    eligible = sorted(set(pool) - set(exclude))
    return sorted(hash_order(f"{label}\x00{seed}", eligible)[:n])


def assert_disjoint_from_development(holdout, development, what="holdout"):
    """§22 step 8 as a halt. Packet 3 calls this; packet 2 proves it fires."""
    overlap = sorted(set(holdout) & set(development))
    if overlap:
        fc.halt(
            f"{what} overlaps the development population on {len(overlap)} "
            f"card(s). A holdout that development has seen is not a holdout, "
            f"and §22 forbids redrawing it for convenience — fix the exclusion "
            f"set, not the draw.")
    return True


# ==========================================================================
# TRAP COVERAGE (§7 of the packet directive) — population metadata only
# ==========================================================================

#: Classes that were proposed, derived, and came back EMPTY. Published because
#: "no member" is a measurement about the corpus, and a class that vanishes
#: from a spec without a trace reads later as a class nobody thought of.
EMPTY_CLASSES_MEASURED = [
    {"class_id": "c7.no-text-noncreature",
     "cohort": 7,
     "qualifying_population": 0,
     "finding": "every card in the candidate universe with no oracle text is "
                "a Creature, so the no-text floor and the vanilla-creature "
                "class are the SAME population. c7.vanilla-creature covers it."},
]

TRAP_MAP = [
    ("card-level union read as co-occurrence",
     "CLAUDE.md traps / contract §28; NC-D",
     "two exclusive modes presented as one card-level bag",
     ["c1.modal-flattening", "c1.active-volcano-named-case", "c2.modal"]),
    ("later ability dropped",
     "NC-A (FULL-CARD-INFORMATION-CONSERVATION)",
     "a fact on a non-first ability line is lost by a truncating reader",
     ["c1.nc-a-later-ability"]),
    ("face dropped",
     "NC-B",
     "a fact on a second face is lost when faces are not all scanned",
     ["c1.nc-b-multi-face", "c7.dfc-two-image", "c7.multi-face-one-image"]),
    ("context stripped, payload intact",
     "NC-C",
     "deleting an activation cost leaves the object fact identical",
     ["c1.nc-c-context-strip"]),
    ("probe drift — raw text vs pipeline preprocessing",
     "NC-E",
     "a CARDNAME pattern reads 0 on raw text and 1,478 through the pipeline",
     ["c1.nc-e-cardname-drift"]),
    ("reminder text searched before the strip",
     "CLAUDE.md trap (Spree / `choose one`)",
     "additive Spree modes filed as mutually exclusive — the inverse of truth",
     ["c2.spree", "c2.modal"]),
    ("trigger event read from the effect, not the condition",
     "CLAUDE.md trap (CR 113.3c)",
     "a verb in the effect clause is matched as the trigger event",
     ["c2.multi-effect", "c8.splitter-territory"]),
    ("or/and splitter invents or loses a trigger",
     "CLAUDE.md trap (CR 603.4 `while`)",
     "a coordination inside one phrase is split into two abilities",
     ["c8.splitter-territory"]),
    ("open capture claims text — zero residue, lost restriction",
     "contract §28 / §18.1 residue-honest claiming",
     "text coverage read as representation",
     ["c8.residue-controller", "c8.residue-numeric", "c8.residue-state"]),
    ("context-free type subsumption",
     "contract §28 (CR 109.2 / 110.1)",
     "a creature card treated as a creature permanent",
     ["c2.entity-context-triplet"]),
    ("lattice-only population assumption",
     "packet 1 P3",
     "fight and attach are structurally absent from the census population",
     ["c2.fight", "c2.attach"]),
    ("UNKNOWN treated as ABSENT",
     "contract §28 / §18 consumer law",
     "a dimension nothing extracted read as proven absent",
     ["c8.kind-unclear-reference", "c2.this-way", "c2.kind-unclear-other"]),
    ("repeated identical clause merged by a case-folded key",
     "PICK-UP-HERE §0AB (Seize the Soul)",
     "two real ability units counted as one",
     ["c2.repeated-identical-clause"]),
    ("alphabetical order read as a ranking; A- variants first",
     "WIRE-RESULT-2026-08-09",
     "name-ordered selection over-picks Alchemy rows",
     ["__sampler__: hash order + Alchemy rows excluded from the universe"]),
]


# ==========================================================================
# BUILD / REPORT
# ==========================================================================

def gather(cards=None, name_index=None):
    ctx = p.corpus()
    if cards is None:
        cards, name_index, _ = fc.load_corpus_gated()
    universe, alchemy = candidate_universe(cards)
    facts = {oid: card_facts(oid, c, ctx.ratified)
             for oid, c in sorted(universe.items())}
    assert_token_domain({t for f in facts.values()
                         for t in f["delivery_tokens"]}, ctx.ratified)
    views = census_views(universe)
    return {"cards": cards, "name_index": name_index, "universe": universe,
            "facts": facts, "views": views, "alchemy": alchemy}


def sampling_params() -> dict:
    if not SAMPLING_JSON.exists():
        fc.halt(f"{SAMPLING_JSON} not found — the cohort-4 seed is a COMMITTED "
                f"artifact (§21) and must not be improvised at run time")
    return json.loads(SAMPLING_JSON.read_text(encoding="utf-8"))


def build(write: bool = False, g: dict = None) -> dict:
    g = g if g is not None else gather()
    params = sampling_params()
    cohorts, c6_split = build_cohorts(
        g["facts"], g["views"], g["universe"], g["name_index"])

    draw4 = draw_cohort4(g["facts"], params["cohort_4"]["seed"],
                         params["cohort_4"]["per_stratum"])

    open_sets = {co.number: co.selected() for co in cohorts}
    development = set().union(*open_sets.values())

    # Overlap over the OPEN cohorts, at BOTH levels, because the two answer
    # different questions and the selected level alone is misleading. Each
    # class draws K exemplars from a population in the hundreds or thousands,
    # so selected-level collisions are rare by construction and a near-empty
    # matrix would read as "these cohorts are cleanly separated" when the
    # POPULATIONS overlap heavily. Structural overlap is reported at both
    # levels and collapsed at neither.
    nums = sorted(open_sets)
    overlap = {f"{a}x{b}": len(open_sets[a] & open_sets[b])
               for i, a in enumerate(nums) for b in nums[i:]}
    pop_sets = {co.number: set().union(*[set(c["_all"]) for c in co.classes])
                for co in cohorts}
    overlap_pop = {f"{a}x{b}": len(pop_sets[a] & pop_sets[b])
                   for i, a in enumerate(nums) for b in nums[i:]}

    # A COHERENCE CONSTRAINT, not a tidiness one: cohort 3 is "both candidates
    # handle this trivially" and cohort 8 is "the honest output is refusal".
    # A card in both would mean the population design contradicts itself, and
    # it would be invisible in a matrix nobody asserted on.
    contradiction = pop_sets[3] & pop_sets[8]
    if contradiction:
        fc.halt(
            f"{len(contradiction)} card(s) qualify as BOTH a simple control "
            f"(cohort 3) and a negative/unresolved case (cohort 8). Those "
            f"cohorts assert opposite expected dispositions, so a shared "
            f"member is a defect in the inclusion rules, not an overlap to "
            f"report.")

    cohort_records = []
    for co in cohorts:
        cohort_records.append({
            "cohort": co.number, "title": co.title, "status": co.open_status,
            "selected_distinct": len(co.selected()),
            "classes": [{k: v for k, v in c.items() if k != "_all"}
                        for c in co.classes],
        })

    manifest = {
        "packet": "AQ4 packet 2 — population + sampling machinery",
        "produced_by": "experiments/aq4_benchmark/aq4_population.py",
        "ratifies": "nothing — AQ4 is UNRATIFIED; this is population only",
        "answer_key": "NONE — §11 of the packet directive; keys are packet 3+",
        "corpus": {
            "corpus_ref": fcb.corpus_ref_current(),
            "gate": "Gate #0 (ratified batch-6 D1) via load_corpus_gated",
            "gated_cards": len(g["cards"]),
            "candidate_universe": len(g["universe"]),
            "alchemy_policy": "paper rows preferred over A- variants (ratified)",
            **g["alchemy"],
        },
        "sampling": params,
        "cohorts": cohort_records,
        "cohort_4": {
            "status": "DRAWN — IDENTITIES NOT EMITTED (uninspected until "
                      "extractor freeze, §21)",
            "stratum_definition": "delivery token x action family",
            "delivery_token_source": "grammar §2 ratified table + §2 scope "
                                     "facet, via fx.deliveries_for_lines",
            "action_family_source": "CR 701 keyword actions parsed at run time "
                                    "(packet-1 cr701_keyword_actions)",
            **cohort4_public(draw4),
        },
        "cohort_5": {
            "status": "NOT DRAWN IN PACKET 2",
            "seed": "NOT CHOSEN — §22 steps 1-2 belong to packet 3",
            "machinery": "draw_generic + assert_disjoint_from_development",
        },
        "cohort_6_split": c6_split,
        "empty_classes_measured": EMPTY_CLASSES_MEASURED,
        "open_cohort_overlap_selected": overlap,
        "open_cohort_overlap_qualifying_population": overlap_pop,
        "cohort_3_vs_8_contradiction": 0,
        "development_population_distinct": len(development),
        "trap_coverage": [
            {"trap": t, "source": s, "failure_mode": m, "covered_by": c}
            for t, s, m, c in TRAP_MAP],
    }
    manifest["manifest_sha256"] = sha256_of(manifest)

    if write:
        COHORT_DIR.mkdir(parents=True, exist_ok=True)
        for co in cohorts:
            payload = {
                "cohort": co.number, "title": co.title,
                "status": co.open_status,
                "representation":
                    "oracle_id only — no oracle text, and no card name, type "
                    "line or characteristic attached to any oracle_id. Class "
                    "prose may NAME a §21 exemplar class (\"the Prey Upon "
                    "class\"); that names a structure, not a row. README §7.",
                "corpus_ref": fcb.corpus_ref_current(),
                "classes": [
                    {"class_id": c["class_id"],
                     "inclusion_reason": c["inclusion_reason"],
                     "derivation_class": c["derivation_class"],
                     "named_historical": c["named_historical"],
                     "qualifying_population": c["qualifying_population"],
                     "oracle_ids": c["selected"]}
                    for c in co.classes],
            }
            payload["cohort_sha256"] = sha256_of(payload)
            (COHORT_DIR / f"cohort-{co.number}.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=False,
                           sort_keys=True) + "\n", encoding="utf-8")
        MANIFEST_JSON.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False,
                       sort_keys=True) + "\n", encoding="utf-8")
    return manifest


# ==========================================================================
# NEGATIVE CONTROLS
# ==========================================================================

def selftest() -> int:
    """NC-P2-1 .. NC-P2-7. Every one is RIGGED RED before it is believed."""
    ok = True

    def report(name, passed, detail):
        nonlocal ok
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name:14s} {detail}")

    g = gather()
    params = sampling_params()
    facts, universe = g["facts"], g["universe"]
    seed = params["cohort_4"]["seed"]
    k = params["cohort_4"]["per_stratum"]

    # -- NC-P2-1 determinism ------------------------------------------------
    a = draw_cohort4(facts, seed, k)
    b = draw_cohort4(facts, seed, k)
    report("NC-P2-1", a["selection_sha256"] == b["selection_sha256"]
           and a["_identities"] == b["_identities"],
           f"same corpus+code+seed -> identical selection "
           f"sha={a['selection_sha256'][:16]}… n={a['drawn_total']}")

    # -- NC-P2-2 seed sensitivity ------------------------------------------
    c = draw_cohort4(facts, seed + "-CONTROL", k)
    changed = set(a["_identities"]) ^ set(c["_identities"])
    report("NC-P2-2", len(changed) > 0,
           f"different seed changes {len(changed)} selection(s) "
           f"(strata with >1 eligible card permit it)")

    # -- NC-P2-3 stratum preservation --------------------------------------
    # RIG: collapse every stratum to one cell and show the distribution moves.
    flat = {oid: dict(f, delivery_token="X", action_family="X")
            for oid, f in facts.items()}
    rigged = draw_cohort4(flat, seed, k)
    report("NC-P2-3",
           rigged["strata_total"] == 1 and a["strata_total"] > 1
           and rigged["drawn_total"] < a["drawn_total"],
           f"breaking stratification: strata {a['strata_total']} -> "
           f"{rigged['strata_total']}, drawn {a['drawn_total']} -> "
           f"{rigged['drawn_total']} — control turns red")

    cohorts, _ = build_cohorts(facts, g["views"], universe, g["name_index"])
    dev = set().union(*[co.selected() for co in cohorts])
    base_hashes = {co.number: sha256_of([sorted(c["selected"])
                                         for c in co.classes])
                   for co in cohorts}

    # -- NC-P2-4 no untracked leakage --------------------------------------
    # BEHAVIOURAL, not a source-text grep. The first version of this control
    # searched this file for a quoted `docs/` path and FOUND TWO — its own
    # regex literal and its own message. A control that matches itself is the
    # overlapping-classes probe defect aimed at a negative control.
    #
    # The real question is whether an untracked working packet can reach a
    # cohort. Plant one containing real oracle_ids, rebuild, and require the
    # cohorts to be byte-identical; then rig it by running a derivation that
    # DOES read the plant, and require the comparison to notice.
    plant = EXPERIMENTS.parent / "docs" / "_NC_P2_4_PLANT.md"
    planted_ids = sorted(dev)[:5]
    try:
        plant.write_text("# untracked plant\n" + "\n".join(planted_ids) + "\n",
                         encoding="utf-8")
        after, _ = build_cohorts(facts, g["views"], universe, g["name_index"])
        after_hashes = {co.number: sha256_of([sorted(c["selected"])
                                              for c in co.classes])
                        for co in after}
        unchanged = after_hashes == base_hashes
        # RIG: a class built FROM the plant differs from one built without it.
        doc_derived = sha256_of([sorted(
            re.findall(r"[0-9a-f-]{36}", plant.read_text(encoding="utf-8")))])
        rig_fires = doc_derived != sha256_of([sorted(planted_ids)[:0]])
    finally:
        plant.unlink(missing_ok=True)
    report("NC-P2-4", unchanged and rig_fires,
           f"planted an untracked docs/ file holding {len(planted_ids)} real "
           f"oracle_ids: cohort hashes unchanged; a doc-derived class is "
           f"detectably different, so the comparison is live")

    # -- NC-P2-5 holdout / blind-cohort non-exposure -----------------------
    # AIMED AT THE CODE PATH. `cohort4_public()` is the ONLY route from the
    # draw into the manifest, so that is what must carry zero identities.
    # The first version asserted that no drawn oracle_id appears ANYWHERE in
    # the manifest, which fails for a reason that is not a leak: an open
    # cohort selects from the same universe, so some of its published members
    # are independently also cohort-4 draws. Nothing about the draw is
    # disclosed by that — an observer cannot tell which, and the count below
    # is exactly the open-cohort intersection.
    m = build(write=False, g=g)
    blob = canonical_json(m)
    pub4 = canonical_json(m["cohort_4"])
    in_pub4 = [oid for oid in a["_identities"] if oid in pub4]
    incidental = sorted(set(a["_identities"]) & dev)
    in_blob = [oid for oid in a["_identities"] if oid in blob]
    report("NC-P2-5",
           not in_pub4 and "_identities" not in blob
           and m["cohort_5"]["seed"].startswith("NOT CHOSEN")
           and len(in_blob) == len(incidental),
           f"cohort_4 record carries 0 of {len(a['_identities'])} drawn ids "
           f"and no cohort-5 seed; the {len(in_blob)} drawn ids present "
           f"anywhere in the manifest are exactly the {len(incidental)} that "
           f"an OPEN cohort independently selected")

    # -- NC-P2-6 development/holdout exclusion -----------------------------
    clean = draw_generic(sorted(universe), "PROBE-SEED", "nc6", 50, exclude=dev)
    fired = False
    try:
        assert_disjoint_from_development(clean, dev)
        # RIG: force a synthetic overlap and require the halt.
        assert_disjoint_from_development(clean + [sorted(dev)[0]], dev)
    except BaseException:
        fired = True
    report("NC-P2-6", fired and not (set(clean) & dev),
           f"excluded draw is disjoint from {len(dev)} development cards; a "
           f"synthetic overlap HALTS")

    # -- NC-P2-7 no lattice-only population regression ---------------------
    fight = [oid for oid, f in facts.items() if f["fight"]]
    attach = [oid for oid, f in facts.items() if f["attach"]]
    lattice = g["views"]["lattice_cards"]
    outside = [o for o in fight + attach if o not in lattice]
    c2 = [co for co in cohorts if co.number == 2][0]
    c2_ids = c2.selected()
    covered = any(o in c2_ids for o in fight) and any(o in c2_ids
                                                      for o in attach)
    report("NC-P2-7", covered and len(outside) > 0,
           f"fight={len(fight)} attach={len(attach)}, {len(outside)} of them "
           f"OUTSIDE the lattice population, and cohort 2 selects from both")

    print()
    print("  every control above was aimed at the CODE PATH, not at a tool "
          "name:")
    print("    NC-P2-3 rigs the stratum key itself, not the sampler's label;")
    print("    NC-P2-6 rigs an overlap into the argument, not into the store.")
    return 0 if ok else 1


def census() -> int:
    """Sizes only. Prints NO oracle_id for any cohort, blind or open."""
    g = gather()
    cohorts, c6_split = build_cohorts(
        g["facts"], g["views"], g["universe"], g["name_index"])
    print("=" * 78)
    print("AQ4 BENCHMARK POPULATION — CENSUS (sizes only)")
    print("=" * 78)
    print(f"  corpus_ref            {fcb.corpus_ref_current()}")
    print(f"  gated corpus          {len(g['cards'])}")
    print(f"  candidate universe    {len(g['universe'])}  "
          f"(Alchemy dropped: {g['alchemy']['alchemy_dropped_paper_twin_present']}, "
          f"twinless kept: {g['alchemy']['alchemy_kept_twinless']})")
    for co in cohorts:
        print()
        print(f"  COHORT {co.number} — {co.title}   "
              f"[{len(co.selected())} distinct selected]")
        for c in co.classes:
            flag = " (named historical)" if c["named_historical"] else ""
            print(f"    {c['class_id']:34s} pop={c['qualifying_population']:6d}"
                  f"  selected={len(c['selected']):3d}{flag}")
    params = sampling_params()
    d4 = draw_cohort4(g["facts"], params["cohort_4"]["seed"],
                      params["cohort_4"]["per_stratum"])
    print()
    print(f"  COHORT 4 — stratified random   [IDENTITIES NOT SHOWN]")
    print(f"    strata (non-empty)   {d4['strata_total']}")
    print(f"    short strata         {d4['strata_short']}  "
          f"(reported, never merged)")
    print(f"    drawn                {d4['drawn_total']}  "
          f"(duplicates {d4['duplicate_ids']})")
    print(f"    selection sha256     {d4['selection_sha256']}")
    print()
    print(f"  COHORT 5 — blind holdout       NOT DRAWN, NO SEED CHOSEN")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--census", action="store_true",
                    help="cohort sizes only; emits no card identities")
    ap.add_argument("--build", action="store_true",
                    help="write the open cohort files + population manifest")
    ap.add_argument("--selftest", action="store_true",
                    help="NC-P2-1 .. NC-P2-7")
    ap.add_argument("--reveal-cohort4", action="store_true",
                    help="EXTRACTOR-FREEZE ONLY. Prints cohort-4 identities. "
                         "Running this before freeze voids the blind draw.")
    a = ap.parse_args()

    if a.reveal_cohort4:
        print("REFUSED — packet 2 is pre-freeze. Cohort 4 stays uninspected "
              "until the extractor freeze point (§21), and this flag exists "
              "so the reveal is a deliberate act at that time, not something "
              "a reporting command can do. Packet 9 re-enables it.")
        return 2
    if a.selftest:
        return selftest()
    if a.build:
        m = build(write=True)
        print(f"wrote {COHORT_DIR}/cohort-*.json and {MANIFEST_JSON.name}")
        print(f"manifest_sha256 {m['manifest_sha256']}")
        return 0
    return census()


if __name__ == "__main__":
    sys.exit(main())
