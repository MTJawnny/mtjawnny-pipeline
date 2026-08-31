#!/usr/bin/env python3
"""SEMANTIC LOCALITY — which structured part of a card owns a fact.

RATIFIED 2026-08-13, resolving FL-2.

CANONICAL RULING: `docs/B-MIGRATION-DISCOVERY.md` sec.11 -- tracked, and it
sits with sec.10's A1, the section that defines the assertion object this
amends. Cite THAT for the law.

**AMENDMENTS A1-A4 ARE RESTATED IN FULL AT sec.11.2 OF THAT SAME TRACKED
DOCUMENT, AND THAT IS THE CITATION TO USE.** Every `A1`/`A2`/`A3`/`A4` below
means sec.11.2. This was repointed 2026-08-14: the amendments were previously
cited to the architecture-review packet, which is UNTRACKED, so on a fresh
clone a Gate 2 module cited a path that does not exist -- the same fail-open
shape as `SESSION-START-PROCEDURE.md` Gate 3b's missing-manifest corollary,
and as a ratified standard with no caller.

Working packets, historical records rather than authority -- and they differ in
whether a fresh clone even has them:
  * `docs/SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md` (PASS) --
    TRACKED, committed in 35f77b7. Safe to cite for detail.
  * `docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md` (RATIFY WITH
    AMENDMENTS A1-A4) -- **UNTRACKED**. Do not cite it as authority; its
    binding content is sec.11.2.

THE PROBLEM THIS SOLVES, IN ONE CARD
------------------------------------
Active Volcano prints `Choose one — • Destroy target blue permanent. • Return
target Island to its owner's hand.` The codebook knows the card destroys a
permanent AND bounces a land. Both true. It does not know they are two options
you choose BETWEEN. Measured 2026-08-13: **41 cards** carry two object-lattice
facts proven by mutually exclusive modes.

An assertion already carries the quote that proves it. It never carried WHICH
PART of the card that quote came from. This module derives that.

WHAT AN ADDRESS IS, AND WHAT IT DELIBERATELY IS NOT
---------------------------------------------------
* **Semantic OWNER** — the one structured location that owns the fact.
* **Evidence SPAN** — the wider contiguous range some quotes cover.

They are different, and A2 exists because 39 quoted assertions legitimately
cover a whole modal block. **The span is DERIVED, never stored** (§13 of the
pre-implementation check): it is a pure function of quote + corpus snapshot,
and storing it would duplicate something that can go stale on its own.

**NO MODE IDENTIFIER IS DERIVED (amendment A1).** Measured over the whole
corpus: **1,791 paragraphs hold exactly one modal bullet and ZERO hold two or
more.** Scryfall puts every mode on its own line, so the paragraph coordinate
IS the mode path. A separate mode field would be a second source of truth for
a fact the paragraph index already carries.

**EXCLUSIVITY IS DERIVED, NEVER STORED (amendment A4).** `owning_header()`
walks back to the nearest preceding non-bullet paragraph on the same face:
**1,783 of 1,791 bullets** resolve deterministically. The 8 exceptions are
Celebr-8000's CR 706.3b die-roll table, which the repository already rules is
not modal.

THE RESOLUTION LAW (amendment A3) — RECONCILED, NEVER RACED
------------------------------------------------------------
A quote is resolved against EVERY supported text representation, and the owner
is accepted only when the union of matched COORDINATES holds exactly one
element. This is not first-match-wins and it privileges no producer class.

Why both representations are required, measured 2026-08-13 over 7,891 quoted
assertions: human evidence is verbatim, DET evidence is CARDNAME-canonicalized.

    raw only        98.6%          canonical only  93.7%          either  99.44%

Canonical-only would orphan **423 human assertions**; raw-only orphans 26 DET
ones. And the tie the law never has to break: **Case F — the two
representations resolving to DIFFERENT single units — is 0**, as are the cases
where one narrows the other. The union is safe because the corpus contains no
disagreement, and it returns AMBIGUOUS by construction if one ever appears.

**The union is over COORDINATES, not over strings.** That is what makes a
canonicalization collision safe: `Rahilda, Wanted Cutthroat // Rahilda, Feral
Outlaw` has two faces whose distinct raw text collapses to identical
canonical text, and two paragraphs collapsing to the same STRING still hold
different COORDINATES, so the union has 2 elements and the law returns
AMBIGUOUS rather than silently merging them.

WHAT THIS MODULE DOES NOT DO
----------------------------
* It writes nothing. No assertion is modified; the backfill migration is a
  separate, Captain-authorised codebook mutation under the backup law.
* **Locality does not certify CORRECTNESS.** A perfectly addressed assertion
  can still sit on the wrong axis -- `foundry_definition_drift` C4 measured 93
  such memberships. Where locality analysis finds a membership contradicting
  its axis, it is routed there, never forced into an address.
* No child-effect decomposition, no qualifier vocabulary, no roles.

    python3 experiments/foundry_locality.py --gate
    python3 experiments/foundry_locality.py --fixtures
    python3 experiments/foundry_locality.py --census
    python3 experiments/foundry_locality.py --selftest
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                    # noqa: E402
import foundry_codebook as fcb                 # noqa: E402

# C8.5J: the standing ratchet now comes from the permanent package. The import
# sits AFTER `foundry_common`, which is what establishes the C8.5A package
# bootstrap -- this module adds no bootstrap and no sys.path mutation of its own.
from mtj_foundry import ratchet                # noqa: E402
from mtj_foundry.paths import ProjectPaths     # noqa: E402

RATCHET_BASELINE = ProjectPaths.for_root(fc.REPO_ROOT).foundry_audit_baseline


# Resolution statuses. Deliberately four, not two: "we know where the evidence
# is" and "we know what owns the fact" are different answers (§15 of the
# pre-implementation check), and collapsing them is how a broad quote comes to
# force a broad owner.
OWNER = "OWNER"            # exactly one unit -- the semantic owner
SPAN = "SPAN"              # evidence crosses units; owner not established here
AMBIGUOUS = "AMBIGUOUS"    # several candidate units; no deterministic choice
UNRESOLVED = "UNRESOLVED"  # the quote matches nothing in the current snapshot


def _norm(s: str) -> str:
    """Whitespace-and-case normalisation ONLY.

    Deliberately not punctuation-stripping: the evidence-quote discipline is
    verbatim, and a normaliser that erased punctuation could match a quote
    against a paragraph it did not come from.
    """
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def units(card: dict, strict: bool = True):
    """[(coord, raw_paragraph, canonical_paragraph)] for one card.

    `coord` is `(face_index, paragraph_index)` — derived from
    `foundry_common.raw_faces`, the ONE shared face reader that
    `foundry_common.full_oracle_text` also delegates to. **No parallel
    indexing is invented here**; this is the coordinate `build_card_doc` and
    `emit_viewer` already use for Searcher A, written down where a fact can
    point at it.

    HALTS if canonicalisation changes a face's line count. It must be a
    per-line substitution, never a reflow — if that ever stops being true the
    two representations stop being coordinate-comparable and every address
    derived here would be silently wrong.

    **`strict=False` returns None instead of halting**, and exists for exactly
    one caller: the DET write path. The ratified rule is that an unaddressable
    assertion stays writable, so a WRITE must not be able to die on a locality
    concern — a reflow would otherwise block Captain-ratified membership over a
    field that is optional by construction. The AUDIT path keeps `strict=True`,
    so the structural defect is still fatal in Gate 2, where finding it is the
    whole job. Measured 2026-08-13: **0 of 32,557 gated cards** reflow, so this
    is a structural guarantee rather than an observed condition.
    """
    out = []
    for fi, face in enumerate(fc.raw_faces(card)):
        raw = face["oracle_text"] or ""
        canon = fc.canonicalize_self_reference(raw, card)
        raw_lines = [x for x in raw.split("\n") if x.strip()]
        canon_lines = [x for x in canon.split("\n") if x.strip()]
        if len(raw_lines) != len(canon_lines):
            if not strict:
                return None
            fc.halt(
                f"CARDNAME canonicalisation changed the paragraph count on "
                f"face {fi} of {card.get('name')!r}: {len(raw_lines)} raw vs "
                f"{len(canon_lines)} canonical. Locality compares the two "
                f"representations coordinate by coordinate, so a reflow makes "
                f"every address on this card meaningless. Fix the "
                f"canonicaliser; never fall back to one representation.")
        for pi, (r, c) in enumerate(zip(raw_lines, canon_lines)):
            out.append(((fi, pi), r, c))
    return out


def resolve(card: dict, quote: str, strict: bool = True) -> dict:
    """The ratified resolution law. Returns {status, owner, candidates, reason}.

    Union over every supported representation; accept iff exactly one
    coordinate. See the module docstring for why this needs no tiebreak.
    """
    if not quote or not quote.strip():
        return {"status": UNRESOLVED, "owner": None, "candidates": [],
                "reason": "assertion carries no evidence quote"}
    us = units(card, strict=strict)
    if us is None:
        return {"status": UNRESOLVED, "owner": None, "candidates": [],
                "reason": "CARDNAME canonicalisation reflows this card's "
                          "paragraphs; coordinates are not comparable"}
    nq = _norm(quote)
    hits = set()
    for coord, raw, canon in us:
        if nq in _norm(raw) or nq in _norm(canon):
            hits.add(coord)
    if len(hits) == 1:
        return {"status": OWNER, "owner": sorted(hits)[0],
                "candidates": sorted(hits), "reason": ""}
    if len(hits) > 1:
        return {"status": AMBIGUOUS, "owner": None, "candidates": sorted(hits),
                "reason": f"quote appears in {len(hits)} units; no "
                          f"deterministic rule distinguishes them"}
    # No single unit. Does the quote cover a contiguous run of them? Both
    # representations are joined and tested, for the same reason the per-unit
    # test uses both.
    for joined in (_norm("\n".join(r for _, r, _ in us)),
                   _norm("\n".join(c for _, _, c in us))):
        if nq in joined:
            return {"status": SPAN, "owner": None,
                    "candidates": [c for c, _, _ in us],
                    "reason": "evidence crosses unit boundaries"}
    return {"status": UNRESOLVED, "owner": None, "candidates": [],
            "reason": "quote matches no text in the current corpus snapshot"}


_BULLET = "•"
_CHOOSE = re.compile(r"\bchoose|\bchooses\b", re.I)


def owning_header(card: dict, coord) -> dict:
    """The modal header that groups a bullet, and its selection cardinality.

    DERIVED, never stored (A4). The header is the nearest preceding non-bullet
    paragraph on the SAME face. Measured: 1,783 of 1,791 bullets resolve; the
    8 that do not are Celebr-8000's CR 706.3b die-roll table, which is one
    ability and not modal at all -- so a bullet with no CHOOSE header is
    correctly reported as non-modal rather than forced into a group.
    """
    us = units(card)
    idx = {c: i for i, (c, _, _) in enumerate(us)}
    if coord not in idx:
        return {"modal": False, "header": None, "reason": "coord not on card"}
    i = idx[coord]
    if _BULLET not in us[i][1]:
        return {"modal": False, "header": None, "reason": "not a bullet"}
    for j in range(i - 1, -1, -1):
        c, raw, _ = us[j]
        if c[0] != coord[0]:
            break
        if _BULLET in raw:
            continue
        if _CHOOSE.search(raw):
            return {"modal": True, "header": c, "text": raw.strip(),
                    "reason": ""}
        break
    return {"modal": False, "header": None,
            "reason": "no CR 700.2 choose-header governs this bullet"}


def mutually_exclusive(card: dict, coord_a, coord_b) -> bool:
    """Do two owners sit under one `Choose one` header?

    The whole point of the architecture, in one predicate. Only cardinality
    ONE makes two modes exclusive -- under `Choose two` a player may take both,
    so those owners are NOT exclusive.
    """
    if coord_a == coord_b:
        return False
    ha, hb = owning_header(card, coord_a), owning_header(card, coord_b)
    if not (ha["modal"] and hb["modal"] and ha["header"] == hb["header"]):
        return False
    return bool(re.search(r"\bchoose one\b", ha.get("text", ""), re.I))


# --------------------------------------------------------------------------
# FIXTURES — the six negative controls, inline
#
# `foundry_probe.py`'s guard self-test is the precedent: fixtures live in the
# module they protect, and every one is derived from a failure that really
# happened or that the ratification explicitly promised to prevent. Cards are
# FIXTURES, never a code path -- nothing in `resolve()` reads a card name.
# --------------------------------------------------------------------------

def _by_name(cards):
    out = {}
    for c in cards.values():
        out.setdefault(c["name"], c)
    return out


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


def census(cards, codebook_path=None) -> dict:
    """Coverage over every live assertion, with EXACT denominators.

    Reports owner coverage and evidence-location coverage SEPARATELY. They are
    different questions and the pre-implementation check exists because
    substituting one for the other is how a broad quote comes to look owned.
    """
    import json
    path = codebook_path or (fc.FOUNDRY_OUT_DIR / "codebook.json")
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    m = {"assertions": 0, "quoted": 0, "quoteless": 0,
         "owned": 0, "span": 0, "ambiguous": 0, "unresolved": 0,
         # STORED coverage, added with the step-4 backfill. Everything above
         # measures what the resolver CAN address; these two measure what the
         # codebook actually CARRIES, and the difference is not academic:
         # measured 2026-08-13, deleting all 7,808 stored addresses left every
         # one of Gate 2's 15 rows green, because a census computed from quotes
         # reproduces itself perfectly on a file with the field stripped out.
         # The migration's entire product was unguarded by the gate that
         # exists to guard it.
         #
         # Marker choice is deliberate and collision-checked against every
         # pinned section, per the trap the handoff records: `stored_owned`
         # resolves WORSE_IF_DOWN through the pre-existing "owned" marker and
         # `stored_mismatch` resolves WORSE_IF_UP through "mismatch", so
         # neither needs a new marker and neither changes another consumer's
         # semantics as a side effect.
         "stored_owned": 0, "stored_mismatch": 0,
         # THE THIRD QUESTION, AND THE ONE NEITHER OTHER METRIC CAN ANSWER.
         # An assertion the resolver addresses to exactly one OWNER, whose
         # stored `locality` is ABSENT. Correct value: 0.
         #
         # The regression it exists for: someone removes or fails to write
         # locality on an assertion that is still perfectly deterministically
         # addressable. `stored_owned` can stay FLAT through that, because
         # corpus growth adds addressed rows at the same time it loses one --
         # a ratchet on a total cannot see a compensated loss, which is the
         # object lattice's own open -7/+7 gap in a different field.
         # `stored_mismatch` stays 0 because no INCORRECT coordinate was
         # stored; absence is not disagreement. Only a per-assertion join of
         # "is addressable" against "is addressed" catches it.
         #
         # EXCLUSIONS, all four by ratification rather than convenience:
         # AMBIGUOUS, SPAN, UNRESOLVED and quoteless assertions are NOT
         # missing. The resolver declines to address them, so an absent
         # address is the correct and required state -- counting them here
         # would make the ratified unaddressed rule read as 122 permanent
         # defects. Tombstone (non-active) axes stay outside the active-axis
         # locality contract, unchanged.
         "addressable_missing": 0}
    for slug, axis in cb["axes"].items():
        if axis.get("status") != "active":
            continue
        for member in axis.get("members") or []:
            card = cards.get(member["oracle_id"])
            for a in member["assertions"]:
                m["assertions"] += 1
                q = a.get("quote")
                stored = a.get("locality")
                if stored is not None:
                    m["stored_owned"] += 1
                if not q:
                    m["quoteless"] += 1
                    # A stored address with no quote is unfalsifiable; lint
                    # already rejects it, so reaching here is a mismatch.
                    if stored is not None:
                        m["stored_mismatch"] += 1
                    continue
                m["quoted"] += 1
                if card is None:
                    m["unresolved"] += 1
                    if stored is not None:
                        m["stored_mismatch"] += 1
                    continue
                r = resolve(card, q)
                m[{OWNER: "owned", SPAN: "span", AMBIGUOUS: "ambiguous",
                   UNRESOLVED: "unresolved"}[r["status"]] ] += 1
                # An address is SNAPSHOT-RELATIVE. When the corpus moves under
                # stored evidence, the ratified rule is that the change is
                # REPORTED, never silently reattached -- so this counts rather
                # than repairs.
                if stored is not None and (
                        r["status"] != OWNER or list(r["owner"]) != list(stored)):
                    m["stored_mismatch"] += 1
                # Addressable but unaddressed. Deliberately keyed on OWNER
                # only, so the four unaddressed-by-rule statuses can never
                # reach it.
                if r["status"] == OWNER and stored is None:
                    m["addressable_missing"] += 1
    return m


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


# --------------------------------------------------------------------------
# STEP 5 — the unaddressed-assertion reporter
#
# `census()` returns COUNTS. What a human needs in order to work the ambiguous
# rows down over time is the LIST, grouped by reason. Written to
# `experiments/out/foundry/` (gitignored: local, never committed), for the same
# reason the object-lattice sample sheet is.
#
# **The remainder is 122, not 83.** The implementation handoff sec.6 enumerates
# "the other 83 (40 ambiguous + 4 unresolved + 39 quoteless)" and omits the
# **39 SPAN** rows, which are equally unaddressed -- `resolve()` returns no
# owner for them, so the backfill skips them exactly as it skips the rest.
# Almost certainly because span and quoteless are BOTH 39 and read as the same
# number twice. The backfill rule itself ("address only where resolve()
# returns OWNER") is unaffected and correct; only the count of its complement
# was wrong. Re-derived here so the reporter can never inherit it.
# --------------------------------------------------------------------------

UNADDRESSED_JSON = fc.FOUNDRY_OUT_DIR / "locality-unaddressed.json"
UNADDRESSED_MD = fc.FOUNDRY_OUT_DIR / "locality-unaddressed.md"

# Why each reason is unaddressed, and what a human would have to do about it.
# Prose, not vocabulary: none of these strings is a ratified token.
_REASON_NOTES = {
    "AMBIGUOUS": ("the quote appears in more than one paragraph, so no "
                  "deterministic rule picks one. Dominated by short repeated "
                  "riders. FIX: narrow the evidence quote to the paragraph "
                  "that actually proves the axis."),
    "SPAN": ("the quote legitimately covers a contiguous run of paragraphs "
             "(A2). The evidence is LOCATED but the fact has no single owner. "
             "FIX: usually none needed -- a modal block quote is honest "
             "evidence; narrow it only if the axis is about one mode."),
    "UNRESOLVED": ("the quote matches no text in the current corpus snapshot. "
                   "Near-noise today. FIX: re-check the quote against the "
                   "card; addresses are snapshot-relative and re-derived."),
    "QUOTELESS": ("the assertion carries no quote at all (the A3 "
                  "legacy-captain-seed exemption). An address is DERIVED from "
                  "a quote, so there is nothing to resolve. FIX: record the "
                  "evidence quote; this is a provenance gap, not a locality "
                  "one."),
}


def unaddressed_rows(cards, codebook_path=None) -> list:
    """Every live assertion the backfill will NOT address, with its reason.

    Deterministically ordered: (reason, slug, oracle_id, class, source_ref).
    Nothing here reads a card name as a code path -- names are carried for the
    human reading the sheet.
    """
    import json
    path = codebook_path or (fc.FOUNDRY_OUT_DIR / "codebook.json")
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for slug, axis in cb["axes"].items():
        if axis.get("status") != "active":
            continue
        for member in axis.get("members") or []:
            oid = member["oracle_id"]
            card = cards.get(oid)
            for a in member["assertions"]:
                q = a.get("quote")
                if not q:
                    reason, detail, cands = "QUOTELESS", (
                        "assertion carries no evidence quote"), []
                elif card is None:
                    reason, detail, cands = "UNRESOLVED", (
                        "oracle_id is not in the gated corpus"), []
                else:
                    r = resolve(card, q)
                    if r["status"] == OWNER:
                        continue
                    reason = r["status"]
                    detail = r["reason"]
                    cands = [list(c) for c in r["candidates"]]
                rows.append({
                    "reason": reason,
                    "axis": slug,
                    "oracle_id": oid,
                    "card": (card or {}).get("name", "(not in corpus)"),
                    "class": a.get("class"),
                    "source_ref": a.get("source_ref"),
                    "quote": q or "",
                    "candidates": cands,
                    "detail": detail,
                })
    rows.sort(key=lambda r: (r["reason"], r["axis"], r["oracle_id"],
                             r["class"] or "", r["source_ref"] or ""))
    return rows


def render_unaddressed_md(rows: list, totals: dict) -> str:
    """The human-readable sheet. Pure function of `rows` -- determinism ×2."""
    from collections import Counter
    by_reason = Counter(r["reason"] for r in rows)
    out = [
        "# SEMANTIC LOCALITY — the unaddressed assertions",
        "",
        "Generated by `python3 experiments/foundry_locality.py --report`.",
        "**Regenerate rather than edit**; this file is gitignored and local.",
        "",
        "An unaddressed assertion is **fully valid card-level evidence** "
        "(ratified 2026-08-13).",
        "It simply cannot prove that its fact co-occurs in the same semantic "
        "unit with another.",
        "Nothing here is a defect by default — read the FIX note per reason.",
        "",
        f"- assertions on active axes: **{totals['assertions']:,}**",
        f"- addressed (semantic OWNER): **{totals['owned']:,}**",
        f"- **unaddressed: {len(rows):,}**",
        "",
        "| reason | n | what it means |",
        "|---|--:|---|",
    ]
    for reason in sorted(by_reason):
        out.append(f"| `{reason}` | {by_reason[reason]} | "
                   f"{_REASON_NOTES.get(reason, '')} |")
    out.append("")
    for reason in sorted(by_reason):
        out += [f"## {reason} — {by_reason[reason]}", "",
                "| axis | card | class | source_ref | quote |",
                "|---|---|---|---|---|"]
        for r in (x for x in rows if x["reason"] == reason):
            q = r["quote"].replace("\n", " ⏎ ").replace("|", "\\|")
            if len(q) > 160:
                q = q[:157] + "…"
            out.append(f"| `{r['axis']}` | {r['card'].replace('|', '')} | "
                       f"{r['class']} | `{r['source_ref']}` | {q} |")
        out.append("")
    return "\n".join(out) + "\n"


def cmd_report(cards) -> int:
    """Writes the two artifacts, with determinism ×2 byte-identical."""
    import json
    from collections import Counter

    totals = census(cards)
    rows = unaddressed_rows(cards)

    # The reporter's own conservation check. `census` and `unaddressed_rows`
    # walk the codebook independently, so a disagreement means one of them is
    # wrong -- exactly the "second measurement path" rule, wired in rather than
    # done once by hand.
    expected = (totals["assertions"] - totals["owned"])
    if len(rows) != expected:
        fc.halt(f"reporter disagreement: census says {expected} assertions are "
                f"unaddressed ({totals['assertions']} total - "
                f"{totals['owned']} owned) but the row walk found "
                f"{len(rows)}. Two independent walks of the same codebook must "
                f"agree; refusing to write a sheet that contradicts the gate.")
    by_reason = Counter(r["reason"] for r in rows)
    if by_reason["SPAN"] != totals["span"] or by_reason["AMBIGUOUS"] != totals["ambiguous"]:
        fc.halt(f"reporter disagreement per reason: rows {dict(by_reason)} vs "
                f"census {totals}")

    payload = {"generated_by": "experiments/foundry_locality.py --report",
               "totals": totals, "unaddressed": len(rows),
               "by_reason": dict(sorted(by_reason.items())), "rows": rows}
    md = render_unaddressed_md(rows, totals)

    # Determinism ×2 on both artifacts, from a second independent build.
    rows2 = unaddressed_rows(cards)
    payload2 = {"generated_by": payload["generated_by"], "totals": census(cards),
                "unaddressed": len(rows2),
                "by_reason": dict(sorted(Counter(r["reason"] for r in rows2).items())),
                "rows": rows2}
    if json.dumps(payload, sort_keys=False) != json.dumps(payload2, sort_keys=False):
        fc.halt("determinism gate FAILED — two builds of the unaddressed "
                "report differ")
    if render_unaddressed_md(rows2, payload2["totals"]) != md:
        fc.halt("determinism gate FAILED — two renders of the unaddressed "
                "sheet differ")

    fc.write_json(UNADDRESSED_JSON, payload)
    UNADDRESSED_MD.write_text(md, encoding="utf-8")
    print(f"determinism ×2 byte-identical on both artifacts")
    print(f"wrote {UNADDRESSED_JSON}")
    print(f"wrote {UNADDRESSED_MD}")
    print(f"\n{totals['assertions']:,} assertions on active axes · "
          f"{totals['owned']:,} addressed · {len(rows):,} UNADDRESSED")
    for reason in sorted(by_reason):
        print(f"    {reason:12}: {by_reason[reason]:>4}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", action="store_true",
                    help="fixtures + census ratchet, one exit code")
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--report", action="store_true",
                    help="write the unaddressed-assertion sheet to "
                         "experiments/out/foundry/ (gitignored)")
    ap.add_argument("--selftest", action="store_true",
                    help="negative control for the GATE: prove the fixtures "
                         "can fail")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()

    if args.report:
        return cmd_report(cards)

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

    if args.gate or args.census:
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
