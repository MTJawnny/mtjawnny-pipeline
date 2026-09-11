"""SEMANTIC LOCALITY — which structured part of a card owns a fact. L2.

RATIFIED 2026-08-13, resolving FL-2. CANONICAL RULING:
`docs/B-MIGRATION-DISCOVERY.md` sec.11, and the A1-A4 amendments restated in
full at sec.11.2 of that same tracked document. Cite THAT for the law.

## What this owns

The ratified ADDRESS LAW and nothing else: `units`, `resolve`,
`owning_header`, `mutually_exclusive`, and the `_norm`/`_by_name` helpers they
need. Four statuses, a coordinate, and the reconciliation rule between the two
text representations.

## What an address is, and what it deliberately is not

* **Semantic OWNER** — the one structured location that owns the fact.
* **Evidence SPAN** — the wider contiguous range some quotes cover.

They are different, and A2 exists because 39 quoted assertions legitimately
cover a whole modal block. **The span is DERIVED, never stored**: it is a pure
function of quote + corpus snapshot, and storing it would duplicate something
that can go stale on its own.

**NO MODE IDENTIFIER IS DERIVED (A1).** Measured over the whole corpus: 1,791
paragraphs hold exactly one modal bullet and ZERO hold two or more, so the
paragraph coordinate IS the mode path.

**EXCLUSIVITY IS DERIVED, NEVER STORED (A4).** `owning_header()` walks back to
the nearest preceding non-bullet paragraph on the same face: 1,783 of 1,791
bullets resolve deterministically. The 8 exceptions are Celebr-8000's CR 706.3b
die-roll table, which the repository already rules is not modal.

## The resolution law (A3) — reconciled, never raced

A quote is resolved against EVERY supported text representation, and the owner
is accepted only when the union of matched COORDINATES holds exactly one
element. Not first-match-wins, and it privileges no producer class. Measured
over 7,891 quoted assertions: raw only 98.6%, canonical only 93.7%, either
99.44%; Case F — the two representations resolving to DIFFERENT single units —
is 0. **The union is over COORDINATES, not over strings**, which is what makes
a canonicalization collision return AMBIGUOUS instead of silently merging two
faces.

## What this deliberately does NOT own

The codebook-facing census and binding, the assertion schema, the DET write
path's stored fields, the ratchet directions and their baseline, the fixture
suites, the boundary-fixture writer, the unaddressed report and the CLI. Every
one of those belongs to a later slice and none of them is duplicated here. No
child-effect decomposition, no qualifier vocabulary, no roles.

**Locality does not certify CORRECTNESS.** A perfectly addressed assertion can
still sit on the wrong axis; where locality analysis finds a membership
contradicting its axis, it is routed there, never forced into an address.

## Layer law

Imports `re` and `dataclasses` only. No repository path, no root derivation, no
import-time file read, no `experiments`, no process exit — this module RAISES
`LocalityError` and the legacy shell re-establishes the historic `STOP — …`
contract. The two card-text primitives it needs are INJECTED by that boundary,
because their permanent home is a later slice's decision, not this one's.
"""

from __future__ import annotations

import re


class LocalityError(RuntimeError):
    """A structural locality defect the pipeline refuses to proceed on."""


class CardFaceRules:
    """The two card-text primitives the address law consumes but does not own.

    Every name is resolved ON THE PROVIDER AT CALL TIME, which is exactly how
    the moved code resolved it: `fc.<name>` was an attribute lookup per call,
    not a value captured once. Freezing a snapshot at install time would be a
    quiet behaviour change, and a ratified negative control proves it -- the
    locality write-boundary fixture REPLACES the CARDNAME canonicaliser at run
    time to force a reflow, and a snapshot would have made that control test
    nothing. It did: the first S7 pass captured values and the fixture went red.

    The provider is RECEIVED, never imported and never located. A missing name
    is refused loudly at install, not discovered at the first call.
    """

    REQUIRED = frozenset({"raw_faces", "canonicalize_self_reference"})

    def __init__(self, provider, names):
        missing = sorted(self.REQUIRED - set(names))
        extra = sorted(set(names) - self.REQUIRED)
        if missing or extra:
            raise LocalityError(
                f"card-text rules must name exactly {sorted(self.REQUIRED)}; "
                f"missing={missing} unexpected={extra}")
        for alias, attr in names.items():
            if not hasattr(provider, attr):
                raise LocalityError(
                    f"the supplied provider has no {attr!r} for {alias!r}")
        self._provider = provider
        self._names = dict(names)

    def __getattr__(self, item):
        try:
            attr = self._names[item]
        except KeyError:
            raise AttributeError(item) from None
        return getattr(self._provider, attr)


_CARD_FACE_RULES: CardFaceRules | None = None


def use_card_face_rules(rules: CardFaceRules) -> None:
    """Install the injected card-face rules. Called by the boundary, once."""
    global _CARD_FACE_RULES
    if not isinstance(rules, CardFaceRules):
        raise LocalityError(f"card-face rules must be a CardFaceRules, got "
                            f"{type(rules).__name__}")
    _CARD_FACE_RULES = rules


def _rules() -> CardFaceRules:
    if _CARD_FACE_RULES is None:
        raise LocalityError(
            "card-face rules have not been installed. The address law receives "
            "them from its composition boundary (`use_card_face_rules`); it "
            "does not go looking for a repository to read them out of.")
    return _CARD_FACE_RULES


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

    `coord` is `(face_index, paragraph_index)` — derived from the INJECTED
    face reader, which is the ONE shared reader the all-faces oracle text also
    delegates to. **No parallel indexing is invented here**; this is the
    coordinate `build_card_doc` and `emit_viewer` already use for Searcher A,
    written down where a fact can point at it.

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
    for fi, face in enumerate(_rules().raw_faces(card)):
        raw = face["oracle_text"] or ""
        canon = _rules().canonicalize_self_reference(raw, card)
        raw_lines = [x for x in raw.split("\n") if x.strip()]
        canon_lines = [x for x in canon.split("\n") if x.strip()]
        if len(raw_lines) != len(canon_lines):
            if not strict:
                return None
            raise LocalityError(
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


def _by_name(cards):
    out = {}
    for c in cards.values():
        out.setdefault(c["name"], c)
    return out
