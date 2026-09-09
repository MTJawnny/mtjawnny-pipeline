"""The static diagnostic pilot — the accepted artifact, made browsable.

## What this is

Path E milestone 3. It takes two ALREADY-EMITTED accepted milestone-2 artifacts
— an `mtj-foundry-evidence-index/1` and the `mtj-foundry-m2-evaluation/1` report
graded from it — and writes a self-contained static bundle that an ordinary
file server can host. It closes the artifact -> browser loop, and that is the
whole of its ambition.

## What it is NOT, stated first because the temptation runs the other way

It is **not a qualification of retrieval quality**. Milestone 2's own accepted
measurement is that named-correct discovery was 12 of 28, that 3 of the 12
discoverable reached the top ten, and that all 12 sat in tie blocks larger than
one. Those numbers are carried INTO the bundle from the evaluation artifact and
shown on the page, because a pilot that hid them would be presenting a coverage
wall as a product.

It is **not a ranking**. Not one ordering decision is made in this file or in
the JavaScript it ships. Every candidate list in the bundle is precomputed by
calling `mtj_foundry.retrieval.query` — the accepted milestone-2 capability,
unmodified — and the browser renders what Python already decided. See "the
browser boundary" below; it is the design's load-bearing choice.

It is **not a semantic input reader**. Once the two artifacts exist this module
opens nothing else: no codebook, no corpus, no authority selector, no input
lock, no repository. That asymmetry is inherited from milestone 2's `query` and
is the property the bundle needs in order to be static at all.

It **invents no evidence**. Every quote, source_ref, corpus_ref, locality and
evidence_status that reaches the browser was copied whole out of the index,
which copied it whole out of the codebook. Where the codebook records nothing,
the bundle says so in those words and stops.

## The browser boundary — why Python precomputes the whole thing

The task allows two designs: reimplement the accepted presentation rule in
JavaScript and differential-test it, or precompute enough accepted Python
retrieval structure that the browser cannot diverge. This module takes the
second, and the reason is that the first has already failed once here in a way
that was invisible: `WIRE-RESULT-2026-08-09.md` records a shipped top-ten that
was an alphabetical slice of a 44-row score tie, and nothing in the product
could see it because the thing that ordered and the thing that displayed were
different code with the same intentions.

So the browser gets no ordering key, no comparator, no feature arithmetic and no
candidate rule. It gets **tie blocks**, already ordered, already grouped, in the
order `retrieval.query` returned them. A JavaScript defect can then misdraw a
block, and a test can catch that; it cannot silently produce a different ranking,
because there is no ranking code to be wrong. Cost: 6,275 accepted queries at
build time, about six seconds, and the exhaustive equivalence check the task asks
for becomes practical rather than aspirational — `verify_retrieval_equivalence`
re-runs every one of them against the emitted bytes.

**The tie block is the transport unit, and that is not a compression trick.**
Two candidates are in the same block exactly when they are equal under ordering
keys 1 and 2 — which means `shared_axis_count` and `shared_axis_cardinalities`
are properties of the BLOCK, not of its members, and storing them per block is
the shape the accepted rule already has. A consumer physically cannot read an
individual rank out of the wire format, because none is written. Key 3
(`oracle_id` ascending) still orders within a block; it is preserved so the
bytes are deterministic, and it is labelled arbitrary everywhere it surfaces.

## Population, again, because this is where it usually gets lost

The bundle carries **every** row of the index — all 38,233 on the selected
pilot inputs, not the eligible 32,557 and not the covered 6,275. Gate #0
eligibility and evidence coverage are FIELDS the browser can display and filter
on at the user's request; they are never applied here, and no emitted file is
built by dropping rows. `verify_population` asserts that from the emitted bytes
rather than from this paragraph.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from mtj_foundry import __version__, evidence_index, retrieval, runtime

__all__ = [
    "EVALUATION_SCHEMA",
    "MANIFEST_NAME",
    "MANIFEST_SCHEMA",
    "PILOT_SCHEMA",
    "PILOT_STATUS",
    "NORMALIZATION_SCHEMA",
    "PilotConservationError",
    "PilotError",
    "PilotInputError",
    "PilotOutputError",
    "build",
    "build_bundle",
    "build_normalization_table",
    "load_evaluation",
    "normalize_with_table",
    "reconcile_selected_inputs",
    "verify_manifest",
    "verify_population",
    "verify_retrieval_equivalence",
    "write_bundle",
]

PILOT_SCHEMA = "mtj-foundry-static-pilot/1"
MANIFEST_SCHEMA = "mtj-foundry-static-pilot-manifest/1"
MANIFEST_NAME = "manifest.json"

# Read from the accepted module rather than restated. A second literal here is a
# second place for the schema string to drift away from the artifact it gates.
EVALUATION_SCHEMA = "mtj-foundry-m2-evaluation/1"

# THE STATUS THE BUNDLE CARRIES ABOUT ITSELF. Not a label this module chose for
# flavour: milestone 2 was accepted as a trustworthy substrate and explicitly NOT
# as a product-quality result, so a bundle that did not say this in its own
# manifest would be the only artifact in the chain that omitted it.
PILOT_STATUS = "DIAGNOSTIC_NOT_PRODUCT_QUALIFIED"

# oracle_ids in this corpus are UUIDs, so the first two hex characters are an
# even, deterministic 256-way split. A shard key that is not two lowercase hex
# characters HALTS rather than falling back to a catch-all bucket: a silent
# fallback would put an unknown number of cards in one file and nothing would
# report it, which is the "halt loudly on an unexpected data shape" house rule.
_SHARD_RE = re.compile(r"^[0-9a-f]{2}")

_ASSET_FILES = ("index.html", "assets/pilot.css", "assets/pilot.js")


class PilotError(runtime.FoundryRuntimeError):
    """Base for this layer's typed refusals.

    Hung under the milestone-1 runtime base so the installed command's accepted
    exit contract — one `STOP — …` line on stderr, exit 1, nothing on stdout —
    covers it without this module knowing anything about process exits.
    """


class PilotInputError(PilotError):
    """A source artifact is missing, unreadable, the wrong schema, or disagrees
    with its sibling about which inputs it was built from."""


class PilotOutputError(PilotError):
    """The output directory is not one this builder may write into."""


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def load_evaluation(path) -> dict:
    """Read an emitted evaluation report. Schema-gated, and nothing else read."""
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PilotInputError(
            f"evaluation report at {path}: {type(error).__name__}: {error}") from error
    if not isinstance(document, dict):
        raise PilotInputError(
            f"{path}: the evaluation is a {type(document).__name__}, expected a "
            f"JSON object")
    schema = document.get("schema")
    if schema != EVALUATION_SCHEMA:
        raise PilotInputError(
            f"{path}: unexpected schema {schema!r}, expected {EVALUATION_SCHEMA!r}")
    return document


def reconcile_selected_inputs(index: dict, evaluation: dict) -> dict:
    """Require the two artifacts to have been built from the SAME selected inputs.

    Both documents independently record which codebook and corpus bytes they were
    derived from, and the evaluation additionally restates the index's population
    arithmetic. Pairing an index with an evaluation graded from a DIFFERENT index
    would produce a bundle whose card data and whose headline metrics described
    two different runs — and every individual number in it would still look
    right, which is exactly the failure that has no other reporter.

    Mismatch is fatal and names both values. There is no reconciliation rule and
    no "take the index's word for it" default; a reviewer decides which artifact
    is the wrong one.
    """
    checks = [
        ("index schema", index.get("schema"), evaluation["index"].get("schema")),
        ("selected codebook sha256",
         index["selected_inputs"]["codebook"]["measured_sha256"],
         evaluation["index"].get("selected_codebook_sha256")),
        ("selected corpus sha256",
         index["selected_inputs"]["corpus"]["measured_sha256"],
         evaluation["index"].get("selected_corpus_sha256")),
        ("corpus_ids_total",
         index["conservation"]["coverage"]["corpus_ids_total"],
         evaluation["index"].get("corpus_ids_total")),
        ("corpus_ids_covered",
         index["conservation"]["coverage"]["corpus_ids_covered"],
         evaluation["index"].get("corpus_ids_covered")),
        ("corpus_ids_uncovered",
         index["conservation"]["coverage"]["corpus_ids_uncovered"],
         evaluation["index"].get("corpus_ids_uncovered")),
    ]
    for field, from_index, from_evaluation in checks:
        if from_index != from_evaluation:
            raise PilotInputError(
                f"{field}: the index says {from_index!r} but the evaluation report "
                f"says {from_evaluation!r} — these two artifacts were not built "
                f"from the same selected inputs, and a bundle pairing them would "
                f"show one run's cards under another run's measurement")
    return {field: from_index for field, from_index, _ in checks}


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def _render(document) -> bytes:
    """The bundle's byte contract: compact separators, `ensure_ascii=False`, one
    trailing newline, UTF-8.

    The index's contract rather than the report's, and for the index's reason:
    these are machine files a browser loads, not pages a person reads, and
    `ensure_ascii=False` keeps the curly apostrophes and non-ASCII card names
    byte-agreeing with the corpus they were copied from. Every mapping below is
    constructed in a fixed order and `json.dumps` preserves insertion order, so
    the same artifacts render to the same bytes.
    """
    return (json.dumps(document, ensure_ascii=False, separators=(",", ":"))
            + "\n").encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _shard_of(oracle_id: str) -> str:
    match = _SHARD_RE.match(oracle_id)
    if not match:
        raise PilotInputError(
            f"oracle_id {oracle_id!r} does not begin with two lowercase hex "
            f"characters, so it cannot be assigned a shard — refusing to guess a "
            f"bucket for it. every oracle_id in the selected corpus is a UUID; a "
            f"corpus where that stops being true needs a shard rule decided, not "
            f"defaulted")
    return match.group(0)


# ---------------------------------------------------------------------------
# Name normalization — the browser's copy of an accepted Python semantic
# ---------------------------------------------------------------------------
#
# M3.R1 repair A, from Manager review `5595913819`.
#
# THE DEFECT. The accepted artifact's name index is keyed by `corpus.
# normalize_name`, which is `str.strip().casefold()`. The first M3 candidate
# normalized the user's QUERY with `trim().toLowerCase()` and said in a comment
# that the two differ — a known contract deviation, not an unknown edge case,
# and the reviewer was right to reject it. Both halves diverge:
#
#   * `casefold()` is FULL Unicode case folding and `toLowerCase()` is not.
#     211 code points fold differently, and some EXPAND: U+017F LATIN SMALL
#     LETTER LONG S folds to `s`, U+00DF folds to `ss`, U+FB01 folds to `fi`.
#     `toLowerCase()` leaves all three unchanged.
#   * `str.strip()` and `String.prototype.trim()` remove DIFFERENT sets.
#     Python strips U+001C-001F and U+0085, which JS keeps; JS trims U+FEFF,
#     which Python keeps. Neither set is a subset of the other, so no amount of
#     care with `toLowerCase` would have fixed the second half.
#
# THE FIX IS DERIVED, NOT ENUMERATED BY HAND. `build_normalization_table()`
# walks every code point in the Unicode space and asks PYTHON what it does,
# recording the two answers. Nothing is transcribed from a standard, nothing is
# special-cased, and no example is hardcoded — the table is a measurement of the
# accepted implementation, and it is regenerated from that implementation every
# time a bundle is built. Cost: ~0.15 s and roughly 27 KB in the bundle.
#
# WHY A TABLE IS SOUND HERE, stated because "reimplement Unicode in the browser"
# would not be. Full case folding is defined per code point with no context
# rules — unlike LOWERCASING, which has them (Greek final sigma). So folding a
# string is exactly concatenating the fold of each of its code points, and a
# per-code-point table composes. That is not assumed: `_verify_normalization`
# re-derives it below and the test suite proves it over the whole Unicode space
# and over random multi-code-point strings.
#
# WHAT THIS IS NOT. It is not a search feature. Normalization is what turns a
# typed query into a KEY; every lookup downstream of it is still exact, prefix
# or substring against the artifact's own key list. No fuzzy matching, no
# similarity, no scoring, no ranking, no threshold, no model, no library.

NORMALIZATION_SCHEMA = "mtj-foundry-name-normalization/1"

#: The exact accepted semantics, in one place, so the guard and the emitter
#: cannot drift apart. This is `corpus.normalize_name` restated as the property
#: being reproduced rather than imported, because what must be reproduced is the
#: BEHAVIOUR and a shared import would make the guard test itself.
def _accepted_normalize(text: str) -> str:
    return text.strip().casefold()


def build_normalization_table() -> dict:
    """Derive Python's strip set and full case-fold map by asking Python.

    One pass over the Unicode scalar space. A code point is in `strip` when
    Python's argument-less `str.strip()` removes it, and in `fold` when its
    case-folded form differs from itself. Both are emitted in code point order,
    so the bytes are deterministic.
    """
    strip = []
    fold = {}
    for code_point in range(0x110000):
        if 0xD800 <= code_point <= 0xDFFF:
            continue  # surrogates are not scalar values and cannot appear here
        char = chr(code_point)
        if char.strip() == "":
            strip.append(char)
        folded = char.casefold()
        if folded != char:
            fold[char] = folded
    return {
        "schema": NORMALIZATION_SCHEMA,
        "reproduces": ("python str.strip().casefold(), which is the accepted "
                       "artifact's corpus.normalize_name"),
        "derived_by": ("walking every Unicode scalar value and recording what "
                       "THIS python does. nothing is transcribed from a standard "
                       "and no character is special-cased"),
        "why_not_tolowercase": (
            "javascript toLowerCase() is not full case folding and trim() is not "
            "str.strip(). the two strip sets are not subsets of one another: "
            "python removes U+001C-001F and U+0085, javascript removes U+FEFF"),
        "algorithm": ("remove leading and trailing characters in `strip`, then "
                      "replace each remaining code point by `fold[c]` if present. "
                      "full case folding is context-free, so per-code-point "
                      "replacement composes exactly"),
        "is_not": ["a search feature", "fuzzy or approximate matching",
                   "similarity, scoring, ranking or any threshold",
                   "a re-derivation of the artifact's name index, which is "
                   "carried verbatim"],
        "strip": strip,
        "fold": fold,
    }


def normalize_with_table(text: str, table: dict) -> str:
    """The REFERENCE implementation of the algorithm the browser runs.

    Deliberately written to mirror the JavaScript step for step rather than to
    be idiomatic Python: its whole job is to be the thing the guard below can
    compare against `_accepted_normalize`, so if it were cleverer than the
    browser's version it would stop being evidence about the browser.
    """
    strip = set(table["strip"])
    fold = table["fold"]
    start, end = 0, len(text)
    while start < end and text[start] in strip:
        start += 1
    while end > start and text[end - 1] in strip:
        end -= 1
    return "".join(fold.get(char, char) for char in text[start:end])


def _verify_normalization(table: dict, index: dict) -> dict:
    """HALT-GUARD: the table must reproduce the accepted semantics exactly.

    Checked against three populations, because each can fail while the others
    pass:

    * **every card name in the source index**, raw and with whitespace padding —
      real data, and the only population whose failure would be visible to a
      user today;
    * **every code point the table itself mentions**, which is where a
      transcription error would live if this were transcribed;
    * **fixed synthetic witnesses**, including a case-fold EXPANSION and both
      directions of the strip disagreement — the cases the corpus does not
      currently contain and therefore cannot test.

    A single disagreement raises. There is no tolerance and no repair path: a
    normalization that is nearly right is a lookup that silently answers about a
    different card.
    """
    checked = 0
    for row in index["cards"]:
        for probe in (row["name"], " " + row["name"] + " "):
            if normalize_with_table(probe, table) != _accepted_normalize(probe):
                raise PilotError(
                    f"normalization table disagrees with python on the card name "
                    f"{probe!r}: table gives "
                    f"{normalize_with_table(probe, table)!r}, "
                    f"str.strip().casefold() gives {_accepted_normalize(probe)!r}")
            checked += 1
    for char in list(table["fold"]) + list(table["strip"]):
        for probe in (char, char + "x", "x" + char, char + "x" + char):
            if normalize_with_table(probe, table) != _accepted_normalize(probe):
                raise PilotError(
                    f"normalization table disagrees with python on "
                    f"{probe!r} (U+{ord(char):04X})")
            checked += 1
    for probe in _NORMALIZATION_WITNESSES:
        if normalize_with_table(probe, table) != _accepted_normalize(probe):
            raise PilotError(
                f"normalization table disagrees with python on the synthetic "
                f"witness {probe!r}")
        checked += 1
    return {"expressions_checked": checked,
            "strip_points": len(table["strip"]),
            "fold_points": len(table["fold"]),
            "fold_points_where_lower_differs": sum(
                1 for char, folded in table["fold"].items()
                if char.lower() != folded)}


#: Cases the selected corpus does not contain, kept as constants so the guard
#: tests them on every build rather than only when a corpus happens to have one.
#: Built with `chr()` rather than pasted, so a control character cannot be
#: silently lost or "helpfully" normalized by an editor on its way into the file.
_NORMALIZATION_WITNESSES = (
    "\u017fol ring",                       # LONG S -> s. toLowerCase leaves it.
    "\u00dfol",                            # SHARP S -> ss. An EXPANSION.
    "\ufb01nal",                           # LATIN SMALL LIGATURE FI -> fi.
    "\u1e9eol",                            # CAPITAL SHARP S -> ss.
    "\u0130",                              # DOTTED CAPITAL I -> i + U+0307.
    "\u03a3\u03c2\u03c3",                  # sigma forms all fold together.
    chr(0x1c) + "sol ring" + chr(0x1c),   # python strips these, JS trim does not.
    chr(0x85) + "sol ring",               # NEXT LINE: python strips, JS does not.
    "\ufeffsol ring",                      # BOM: JS trims this, python does NOT.
    "  \t\n mixed \u00dfpacing \r\n  ",
    "",
    "   ",
)


# ---------------------------------------------------------------------------
# The browser data layers
# ---------------------------------------------------------------------------
#
# Five whole-bundle files plus two sharded families. The split is by ACCESS
# SHAPE, not by size: everything needed to search the corpus, name a card and
# explain a connection is loaded once, and only per-card ORACLE TEXT and the
# precomputed candidate blocks are fetched on demand.
#
# The consequence worth naming: `evidence.json` holds ALL 7,930 active
# memberships for all 6,275 covered cards, because the codebook's evidence layer
# is small even though the corpus is not. So rendering a candidate's stored
# quote and provenance needs no extra fetch — the browser already has every
# assertion, and a connection can never be drawn with half its evidence missing
# because the other half had not arrived.

def _card_directory(index: dict) -> dict:
    """Columnar, one entry per card, in the index's own row order.

    A card's position in these arrays is its CARD INDEX, and that integer is the
    only card reference used inside the bundle's other files. The `oracle_id`
    column is what turns it back into the real key, and nothing in the browser
    may treat the index as an identity — it is a position in a file, and it moves
    when the corpus does.
    """
    rows = index["cards"]
    return {
        "row_order": ("the source index's own card order, which is oracle_id "
                      "ascending. a card's position here is its CARD INDEX and is "
                      "the reference used by every other file in this bundle"),
        "count": len(rows),
        "oracle_id": [row["oracle_id"] for row in rows],
        "name": [row["name"] for row in rows],
        "normalized_name": [row["normalized_name"] for row in rows],
        "gate0_eligible": [1 if row["gate0_eligible"] else 0 for row in rows],
        "assigned": [1 if row["evidence_state"]
                     == evidence_index.EVIDENCE_STATE_ASSIGNED else 0
                     for row in rows],
        "membership_count": [len(row["memberships"]) for row in rows],
        "face_count": [len(row["faces"]) for row in rows],
        "shard": [_shard_of(row["oracle_id"]) for row in rows],
        "evidence_state_codes": {
            "1": evidence_index.EVIDENCE_STATE_ASSIGNED,
            "0": evidence_index.EVIDENCE_STATE_UNASSIGNED,
        },
        "eligibility_and_coverage_are": (
            "FIELDS on a row. no file in this bundle was built by dropping rows "
            "that failed either one, and the browser applies neither unless a "
            "reader asks for it"),
    }


def _name_lookup(index: dict, position: dict) -> dict:
    """The index's own `name_index`, with oracle_ids mapped to card indices.

    Carried from the artifact rather than rebuilt, and the difference is real
    rather than pedantic: the artifact's name index is keyed on
    `corpus.normalize_name` (strip, then CASEFOLD, which is not `toLowerCase`)
    and each list is in FIRST-SEEN CORPUS order, while the card rows are sorted
    by oracle_id. Rebuilding it from the rows would silently reorder every
    ambiguous name's identities. The id -> index substitution is bijective and
    order-preserving, so the semantics are the artifact's, unchanged.

    216 normalized names in the selected corpus are shared by more than one card.
    Every one of them keeps every id.
    """
    return {
        "semantics": ("keys are the SOURCE ARTIFACT's normalized names — strip, "
                      "then casefold — and each list is that artifact's own id "
                      "list in first-seen corpus order, with oracle_ids replaced "
                      "by card indices. no name was collapsed, deduplicated or "
                      "reordered"),
        "ambiguous_names": sum(1 for ids in index["name_index"].values()
                               if len(ids) > 1),
        "names": {name: [position[oracle_id] for oracle_id in ids]
                  for name, ids in index["name_index"].items()},
    }


def _axis_catalogue(index: dict) -> dict:
    """The index's active-axis catalogue, plus a stable AXIS INDEX per axis.

    Same substitution as the card directory and for the same reason: a membership
    row names its axis by position, and the position is resolved here.
    """
    order = list(index["axes"])
    return {
        "order": order,
        "count": len(order),
        "axis_index_is": ("a position in `order`. it is a reference inside this "
                          "bundle and is not an axis identity"),
        "axes": index["axes"],
    }


def _evidence_layer(index: dict, position: dict, axis_position: dict) -> dict:
    """Every active membership of every covered card, member objects VERBATIM.

    The member object is copied whole, exactly as the index copied it whole out
    of the codebook. `class`, `source_ref`, `quote`, `corpus_ref`,
    `evidence_status`, `locality`, a member-level `tier` and any key a later
    codebook schema adds all survive, because no code path here enumerates the
    fields it expects. The browser renders whatever keys arrive.
    """
    rows = []
    for row in index["cards"]:
        if not row["memberships"]:
            continue
        rows.append([
            position[row["oracle_id"]],
            [[axis_position[m["axis_id"]], m["member"]] for m in row["memberships"]],
        ])
    return {
        "row_shape": "[card_index, [[axis_index, member_object_verbatim], ...]]",
        "member_objects_are": ("copied WHOLE from the source index, which copied "
                               "them whole from the selected codebook. no field "
                               "was projected away and none was synthesized"),
        "covered_cards": len(rows),
        "memberships": sum(len(r[1]) for r in rows),
        "rows": rows,
    }


def _text_shards(index: dict, position: dict) -> dict:
    """Per-card faces, split 256 ways by the oracle_id's first two hex characters.

    Faces are the bundle's bulk — 12.8 MB of the 24.4 MB source artifact on the
    selected pilot — and they are the one layer a reader needs only for the cards
    actually on screen. Sharding them is what keeps the initial load to the
    directory, the names, the axes and the evidence.

    The faces list is copied verbatim from the index, which took it from
    `corpus.card_faces` rather than from the raw `card_faces` key — so split,
    flip and adventure layouts read correctly and a two-faced card arrives with
    both texts.
    """
    shards: dict = {}
    for row in index["cards"]:
        shard = _shard_of(row["oracle_id"])
        shards.setdefault(shard, []).append([position[row["oracle_id"]], row["faces"]])
    return {shard: {"row_shape": "[card_index, faces_verbatim]",
                    "count": len(rows), "rows": rows}
            for shard, rows in sorted(shards.items())}


def _tie_blocks(result: dict) -> list:
    """One `retrieval.query` result, regrouped into its own tie blocks.

    Nothing is decided here. `retrieval._rank` already stamped every candidate
    with `tie_block_first_rank`, and a block is exactly the run of candidates
    carrying the same one — they arrive contiguously because the stamp is derived
    from the same sort key the list is ordered by. This function reads that
    stamp; it does not recompute a comparator, and if it disagreed with the
    accepted ranking `verify_retrieval_equivalence` would fail.

    `shared_axis_count` and `shared_axis_cardinalities` are lifted to the BLOCK
    because a tie block is by definition the set of candidates equal under both.
    That is asserted per member rather than assumed: two candidates the accepted
    ordering placed in one block cannot differ on either value, and if they ever
    did the assertion below would stop the build instead of quietly publishing a
    block whose header described only its first row.
    """
    blocks = []
    for candidate in result["candidates"]:
        features = candidate["features"]
        first = candidate["tie_block_first_rank"]
        if not blocks or blocks[-1]["first_rank"] != first:
            blocks.append({
                "first_rank": first,
                "shared_axis_count": features["shared_axis_count"],
                "shared_axis_cardinalities": list(features["shared_axis_cardinalities"]),
                "declared_size": candidate["tie_block_size"],
                "members": [],
            })
        block = blocks[-1]
        if (features["shared_axis_count"] != block["shared_axis_count"]
                or list(features["shared_axis_cardinalities"])
                != block["shared_axis_cardinalities"]):
            raise PilotError(
                f"candidate {candidate['oracle_id']} was placed in the tie block "
                f"beginning at rank {first} but its ordering features differ from "
                f"the block's — the accepted retrieval's tie-block stamp and its "
                f"ordering keys disagree, which is a defect in the artifact chain "
                f"and not an input state")
        block["members"].append(candidate)
    for block in blocks:
        if len(block["members"]) != block["declared_size"]:
            raise PilotError(
                f"tie block at rank {block['first_rank']} holds "
                f"{len(block['members'])} candidates but the accepted retrieval "
                f"stamped its size as {block['declared_size']}")
    return blocks


def _retrieval_shards(index: dict, position: dict, axis_position: dict) -> dict:
    """Precomputed candidate blocks for every assigned anchor, sharded like the text.

    THE ONE PLACE RETRIEVAL HAPPENS, and it happens by calling the accepted
    milestone-2 capability once per covered card. No ordering rule is restated
    here and none is reimplemented in the JavaScript this bundle ships; the
    browser receives blocks in the order `retrieval.query` returned them.

    Individual ranks are deliberately NOT written. A block carries the rank its
    first member occupies, which is what a reader needs to know how deep into the
    list it sits, and the members inside it are unnumbered — key 3 ordered them by
    `oracle_id` and carries no semantics, so a per-row ordinal would be a number
    the artifact does not mean. The bytes are still fully determined, because the
    within-block order is preserved exactly as returned.
    """
    view = retrieval.EvidenceIndexView(index)
    shards: dict = {}
    for row in index["cards"]:
        if not row["memberships"]:
            continue
        oracle_id = row["oracle_id"]
        result = retrieval.query(index, oracle_id=oracle_id, view=view)
        blocks = [
            {
                "first_rank": block["first_rank"],
                "size": len(block["members"]),
                "shared_axis_count": block["shared_axis_count"],
                "shared_axis_cardinalities": block["shared_axis_cardinalities"],
                "members": [
                    [position[candidate["oracle_id"]],
                     [axis_position[axis_id]
                      for axis_id in candidate["features"]["shared_axis_ids"]]]
                    for candidate in block["members"]
                ],
            }
            for block in _tie_blocks(result)
        ]
        shards.setdefault(_shard_of(oracle_id), []).append([
            position[oracle_id],
            {"result_state": result["result_state"],
             "candidate_count": result["candidate_count"],
             "blocks": blocks},
        ])
    return {shard: {"row_shape": "[anchor_card_index, {result_state, "
                                 "candidate_count, blocks}]",
                    "member_shape": "[candidate_card_index, [shared_axis_index, ...]]",
                    "ranks_within_a_block": (
                        "NOT WRITTEN. ordering key 3 is oracle_id ascending and "
                        "carries no semantics, so a per-member ordinal would be a "
                        "number this artifact does not mean. the order is "
                        "preserved; the ranking claim is not made"),
                    "count": len(rows), "rows": rows}
            for shard, rows in sorted(shards.items())}


# ---------------------------------------------------------------------------
# The diagnostic disclosure
# ---------------------------------------------------------------------------

def _disclosure(index: dict, evaluation: dict) -> dict:
    """The persistent panel the page shows, with every FACT read off an artifact.

    Same discipline as `evidence_index._absent_membership_clause`, and for the
    same measured reason: a permanent capability that types a current
    measurement into its own prose ships that measurement forever, and the next
    inputs make it a lie that still reads authoritative. So the counts, the
    shares and the k-values below are interpolated from the two source
    documents, and the QUANTIFIERS are derived too — "a majority" is as much a
    population claim as "31,958" is, and fixing the digits while leaving the
    adjective would move the same defect one word to the right.

    What is fixed prose is the MEANING: that absence of evidence is unknown and
    never dissimilarity, and that connections here are evidence links rather
    than a claim of gameplay similarity. Those are true of every bundle this
    builder will ever write, which is the test for what may be a constant.
    """
    coverage = index["conservation"]["coverage"]
    eligibility = index["conservation"]["eligibility"]
    total = coverage["corpus_ids_total"]
    covered = coverage["corpus_ids_covered"]
    uncovered = coverage["corpus_ids_uncovered"]
    discovery = evaluation["aggregate_candidate_discovery"]
    presentation = evaluation["aggregate_presentation"]

    def share(part: int) -> str:
        if part * 2 > total:
            return "a majority"
        if part * 2 < total:
            return "a minority"
        return "exactly half"

    top_k = sorted(int(key.rsplit("_", 1)[1]) for key in presentation
                   if key.startswith("in_top_"))
    top_clause = ", ".join(
        f"{presentation[f'in_top_{k}']} of {presentation['discoverable_total']} "
        f"reached the top {k}" for k in top_k)
    recall = discovery["recall"]
    return {
        "status": PILOT_STATUS,
        "headline": ("A PATH E DIAGNOSTIC PILOT over a selected historical corpus "
                     "and codebook. It is not a finished thesaurus, not a "
                     "production Searcher B, not a recommendation engine, and not "
                     "a claim about similarity."),
        "points": [
            (f"The index holds the ENTIRE selected corpus — {total:,} cards. "
             f"Gate #0 eligibility and evidence coverage are fields you can see "
             f"on every card, never filters that remove one: "
             f"{eligibility['ineligible_unique_ids']:,} ineligible cards and "
             f"{uncovered:,} cards with no recorded evidence are all here and all "
             f"selectable."),
            (f"Only {covered:,} of {total:,} cards — {share(covered)} — carry any "
             f"active evidence in the selected codebook. The other {uncovered:,} "
             f"carry UNASSIGNED_NO_ACTIVE_EVIDENCE."),
            ("ABSENCE OF EVIDENCE IS UNKNOWN, NOT DISSIMILARITY. "
             "UNASSIGNED_NO_ACTIVE_EVIDENCE means only that the selected codebook "
             "records no active membership for that card. It is not a review that "
             "rejected it, not negative evidence, and NEVER a finding that no "
             "similar cards exist."),
            (f"The frozen milestone-2 panel measured LIMITED DISCOVERY and LARGE "
             f"TIE BLOCKS: {discovery['discoverable']} of "
             f"{discovery['named_correct_total']} named-correct neighbours were "
             f"discoverable at all"
             + (f" ({recall * 100:.1f}%)" if recall is not None else "")
             + f"; of those, {top_clause}; and "
             f"{presentation['in_a_tie_block_larger_than_one']} of "
             f"{presentation['discoverable_total']} sat in a tie block larger than "
             f"one, where the order carries no meaning at all."),
            ("Therefore what you see below are EVIDENCE CONNECTIONS the selected "
             "codebook records — not a ranking by similarity, and not a claim that "
             "the connections shown are complete."),
        ],
        "tie_blocks_are": (
            "candidates the accepted ordering could not separate. Within a block "
            "the order is oracle_id ascending, which is arbitrary and carries no "
            "meaning. Blocks are shown as groups, and no member is given an "
            "individual rank."),
        "ordering": evaluation["ordering"],
        "evidence_state_semantics": index["evidence_state_semantics"],
        "what_this_does_not_prove": evaluation["what_this_does_not_prove"],
    }


def _meta(index: dict, evaluation: dict, identities: dict, reconciled: dict) -> dict:
    """Everything the page needs that is not a card: identities, counts, metrics."""
    return {
        "schema": PILOT_SCHEMA,
        "status": PILOT_STATUS,
        "generator": {"package": "mtj_foundry", "version": __version__,
                      "capability": "static_diagnostic_pilot"},
        "bundle_is": "DERIVED_EVIDENCE_NOT_AUTHORITY",
        "source_artifacts": identities,
        "selected_inputs": index["selected_inputs"],
        "selected_inputs_agree": reconciled,
        "population": {
            "corpus_population": index["conservation"]["corpus_population"],
            "eligibility": index["conservation"]["eligibility"],
            "coverage": index["conservation"]["coverage"],
            "codebook_structure": index["conservation"]["codebook_structure"],
        },
        "frozen_evaluation": {
            "panel": evaluation["panel"],
            "evaluation_is": evaluation["evaluation_is"],
            "aggregate_candidate_discovery": evaluation["aggregate_candidate_discovery"],
            "aggregate_presentation": evaluation["aggregate_presentation"],
            "anchors": [
                {"label": anchor.get("label"), "name": anchor.get("name"),
                 "oracle_id": anchor.get("oracle_id"),
                 "candidate_pool_size": anchor.get("candidate_pool_size"),
                 "candidate_discovery": anchor.get("candidate_discovery")}
                for anchor in evaluation["anchors"]],
            "controls": [
                {"label": control.get("label"), "name": control.get("name"),
                 "oracle_id": control.get("oracle_id"),
                 "result_state": control.get("result_state"),
                 "candidate_count": control.get("candidate_count")}
                for control in evaluation["controls"]],
        },
        "disclosure": _disclosure(index, evaluation),
        "runtime": {
            "reads": "only the files in this bundle, by relative path",
            "does_not_read": ["the codebook", "the corpus", "the repository",
                              "the authority selector", "any application backend",
                              "any network host other than this bundle's origin"],
            "uses_no": ["CDN", "external stylesheet, font, image or script",
                        "analytics", "model or LLM call", "vector or embedding "
                        "search", "text similarity"],
        },
    }


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _assets() -> dict:
    """The three static files, read from package data.

    Package-owned rather than repository-relative on purpose: an installed
    command must find its own template without a repository to look in, which is
    the same reason milestone 1 made the root an explicit parameter. These are
    inert text — markup, style and rendering code — and they are the only files
    this builder reads that are not one of the two source artifacts.
    """
    from importlib import resources

    root = resources.files("mtj_foundry.pilot_assets")
    out = {}
    for name in _ASSET_FILES:
        source = root
        for part in name.split("/"):
            source = source / part
        out[name] = source.read_text(encoding="utf-8").encode("utf-8")
    return out


def build_bundle(index: dict, evaluation: dict, identities: dict) -> dict:
    """`{relative path: bytes}` for the whole bundle. Pure: writes nothing.

    Returned as bytes rather than written incrementally so determinism can be
    checked without a filesystem, and so a build that fails a conservation check
    part-way leaves no half-written directory behind.
    """
    reconciled = reconcile_selected_inputs(index, evaluation)
    position = {row["oracle_id"]: number
                for number, row in enumerate(index["cards"])}
    axis_position = {axis_id: number
                     for number, axis_id in enumerate(index["axes"])}

    files = dict(_assets())
    # Derived from THIS python, then proven against it before anything is
    # emitted. The guard runs here rather than in `write_bundle` so a table that
    # disagrees with `str.strip().casefold()` never reaches a file at all.
    normalization = build_normalization_table()
    _verify_normalization(normalization, index)
    files["data/normalization.json"] = _render(normalization)
    files["data/meta.json"] = _render(_meta(index, evaluation, identities, reconciled))
    files["data/cards.json"] = _render(_card_directory(index))
    files["data/names.json"] = _render(_name_lookup(index, position))
    files["data/axes.json"] = _render(_axis_catalogue(index))
    files["data/evidence.json"] = _render(
        _evidence_layer(index, position, axis_position))
    for shard, payload in _text_shards(index, position).items():
        files[f"data/text/{shard}.json"] = _render(payload)
    for shard, payload in _retrieval_shards(index, position, axis_position).items():
        files[f"data/retrieval/{shard}.json"] = _render(payload)
    files[MANIFEST_NAME] = _render(_manifest(files, index, evaluation, identities))
    return files


def _manifest(files: dict, index: dict, evaluation: dict, identities: dict) -> dict:
    """Every emitted file's path, sha256 and byte size — except this file.

    THE SELF-REFERENCE CONVENTION, stated here and tested rather than left to be
    inferred: `manifest.json` cannot contain its own sha256, because writing the
    digest changes the bytes it is a digest of. So the manifest covers every
    other emitted file and names its own exclusion in `self_excluded`. A
    verifier walks the bundle, removes exactly that one path, and requires the
    remainder to match — which is deterministic and leaves no file unaccounted
    for, as against the alternatives of a placeholder digest (a value that is
    wrong on purpose) or a second manifest (a file with the same problem).
    """
    covered = {path: payload for path, payload in files.items()
               if path != MANIFEST_NAME}
    return {
        "schema": MANIFEST_SCHEMA,
        "pilot_schema": PILOT_SCHEMA,
        "status": PILOT_STATUS,
        "status_means": (
            "this bundle is a DIAGNOSTIC over accepted milestone-2 artifacts. it "
            "is not a qualification of retrieval quality, not a product, not "
            "semantic authority, and not a claim that the evidence it shows is "
            "complete"),
        "generator": {"package": "mtj_foundry", "version": __version__,
                      "capability": "static_diagnostic_pilot"},
        "source_artifacts": identities,
        "selected_inputs": {
            "codebook_sha256": index["selected_inputs"]["codebook"]["measured_sha256"],
            "codebook_byte_size":
                index["selected_inputs"]["codebook"]["measured_byte_size"],
            "corpus_sha256": index["selected_inputs"]["corpus"]["measured_sha256"],
            "corpus_byte_size":
                index["selected_inputs"]["corpus"]["measured_byte_size"],
            "corpus_content_sha256":
                index["selected_inputs"]["corpus"]["measured_content_sha256"],
            "authority_selector": index["selected_inputs"]["authority_selector"],
        },
        "population": {
            "corpus_ids_total":
                index["conservation"]["coverage"]["corpus_ids_total"],
            "corpus_ids_covered":
                index["conservation"]["coverage"]["corpus_ids_covered"],
            "corpus_ids_uncovered":
                index["conservation"]["coverage"]["corpus_ids_uncovered"],
            "eligible_unique_ids":
                index["conservation"]["eligibility"]["eligible_unique_ids"],
            "ineligible_unique_ids":
                index["conservation"]["eligibility"]["ineligible_unique_ids"],
            "active_axes": len(index["axes"]),
        },
        "frozen_evaluation": {
            "aggregate_candidate_discovery":
                evaluation["aggregate_candidate_discovery"],
            "aggregate_presentation": evaluation["aggregate_presentation"],
        },
        "self_excluded": MANIFEST_NAME,
        "self_excluded_because": (
            "a file cannot carry its own sha256: writing the digest changes the "
            "bytes being digested. every other emitted file is below, and a "
            "verifier removes exactly this one path before comparing"),
        "file_count": len(covered),
        "total_bytes": sum(len(payload) for payload in covered.values()),
        "files": [{"path": path,
                   "sha256": _sha256(covered[path]),
                   "byte_size": len(covered[path])}
                  for path in sorted(covered)],
    }


# ---------------------------------------------------------------------------
# Writing — the one place this package touches a filesystem for output
# ---------------------------------------------------------------------------

def _resolved_target(output: Path, relative: str) -> Path:
    """A write path, proven to be under the declared output root before it exists.

    `Path.resolve()` on both sides and an explicit `relative_to`, rather than a
    string prefix test: a prefix test passes for `/tmp/outputs-evil` against
    `/tmp/output`, and it cannot see a `..` component or a symlinked parent at
    all. Every path this builder writes goes through here, so the boundary is one
    function and not a convention.
    """
    target = (output / relative).resolve()
    try:
        target.relative_to(output.resolve())
    except ValueError:
        raise PilotOutputError(
            f"refusing to write {relative!r}: it resolves to {target}, which is "
            f"outside the declared output directory {output.resolve()}") from None
    return target


def _prepare_output(output: Path) -> None:
    """THE OUTPUT RULE, and it never deletes a directory tree.

    * A path that does not exist is created.
    * An EMPTY directory is used as-is.
    * A directory holding a `manifest.json` this builder wrote — recognised by
      its own `schema` — is REPLACED: every file that manifest lists is removed,
      the manifest itself is removed, and the new bundle is written. Nothing
      outside that recorded file list is touched, so a stray file an operator put
      in the directory survives and is reported rather than destroyed.
    * Anything else REFUSES. A non-empty directory this builder does not
      recognise, or a path that is not a directory, is an operator input state
      and stops the run.

    There is deliberately no `shutil.rmtree` anywhere in this module. A recursive
    delete of a caller-supplied path is a foot-gun whose failure mode is
    unbounded, and the recorded file list is a bounded, deterministic alternative
    that does the same job for the case that actually occurs.
    """
    if output.exists() and not output.is_dir():
        raise PilotOutputError(
            f"{output} exists and is not a directory — refusing to write a bundle "
            f"over it")
    if not output.exists():
        output.mkdir(parents=True)
        return
    entries = sorted(entry.name for entry in output.iterdir())
    if not entries:
        return
    manifest_path = output / MANIFEST_NAME
    if not manifest_path.is_file():
        raise PilotOutputError(
            f"{output} is not empty and holds no {MANIFEST_NAME} written by this "
            f"builder (found {', '.join(entries[:8])}"
            f"{', …' if len(entries) > 8 else ''}) — refusing to write into a "
            f"directory whose contents this builder did not create. name an empty "
            f"or new directory")
    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            previous = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PilotOutputError(
            f"{manifest_path}: {type(error).__name__}: {error} — refusing to "
            f"replace a bundle whose manifest cannot be read") from error
    if not isinstance(previous, dict) or previous.get("schema") != MANIFEST_SCHEMA:
        raise PilotOutputError(
            f"{manifest_path} is not a {MANIFEST_SCHEMA!r} — refusing to replace "
            f"the contents of a directory this builder did not write")
    # M3.R1 REPAIR B: VALIDATE THE WHOLE SHAPE BEFORE DELETING ANYTHING.
    #
    # The schema check above proves the document CLAIMS to be one of ours; it
    # proves nothing about the fields the replacement then consumes. The first
    # M3 candidate went straight from that check to `entry["path"]`, so a
    # schema-correct manifest carrying `"files": [{}]` or a non-list `files`
    # raised a raw `KeyError`/`TypeError` — which escapes the CLI's declared
    # contract, because `pilot_cli` catches `FoundryRuntimeError` and nothing
    # else. The operator would have seen a traceback where the contract promises
    # one `STOP — …` line.
    #
    # So every path is resolved and containment-checked in a FIRST pass that
    # unlinks nothing, and deletion only starts once the whole list has been
    # accepted. That ordering is the point: a manifest whose tenth entry is
    # malformed must not have had its first nine files deleted. The alternative
    # — validating lazily inside the delete loop — fails half-done, and a
    # half-deleted bundle is exactly the state whose manifest can no longer be
    # trusted to describe it.
    stale = _validated_replacement_targets(previous, manifest_path, output)
    for target in stale:
        if target.is_file():
            target.unlink()
    manifest_path.unlink()


def _validated_replacement_targets(previous: dict, manifest_path: Path,
                                   output: Path) -> list:
    """Every file a recognised prior manifest says to remove, or a refusal.

    Deletes nothing and is called before anything is deleted. Validates exactly
    the shape the replacement consumes and no more — this is not a schema
    validator for the manifest as a whole, and it deliberately does not check
    `sha256`, `byte_size` or any field the replacement never reads. Validating
    fields nobody consumes would refuse bundles that are fine, which is its own
    kind of wrong answer.

    Every refusal is a `PilotOutputError` naming the offending entry, and every
    path additionally passes `_resolved_target`'s containment check, so a
    manifest cannot direct a delete outside the output directory it lives in.

    NO GENERIC CATCH. Each condition is tested positively rather than by running
    the consumption and catching what falls out: `except (KeyError, TypeError)`
    would also swallow a defect in this module and report it as a malformed
    input, which is the wrong story told confidently.

    ## M3.R2 — two more shapes that reached past this boundary

    Both from Manager review `5596543305`, and both are the same mistake made
    twice: **a value this function CONSUMES was being accepted on a weaker test
    than the one the consumption actually needs.**

    * **`files` had to be a list, and absence is not a list.** The first draft
      opened with `previous.get("files", [])`, so a schema-correct manifest with
      no `files` field at all was read as "this bundle contained no files" — a
      confident empty answer to a question the document never answered. The
      damage is not in this function: `_prepare_output` would then delete the
      manifest, `write_bundle` would write the new bundle over the top, and
      every unrecorded old file in that directory would survive underneath a
      manifest that does not mention it. Without `--verify` the command exits 0.
      **Absent and empty are different facts, and only one of them is safe.**
    * **A listed path may not be the manifest itself.** The convention is that
      `manifest.json` is self-excluded from `files` and removed separately by
      `_prepare_output` AFTER the stale targets. Containment alone accepts
      `manifest.json` — it is inside the output root — so the stale loop would
      unlink it and the unconditional `manifest_path.unlink()` two lines later
      would raise a raw `FileNotFoundError`, straight past the installed
      command's one-line `STOP` contract. The check is on the RESOLVED path, not
      on the string, so `./manifest.json` and `data/../manifest.json` are caught
      by the same test.
    """
    if "files" not in previous:
        raise PilotOutputError(
            f"{manifest_path}: it has no 'files' — refusing to treat an absent "
            f"field as an empty bundle. an absent 'files' does not say this "
            f"directory held no files, it says the manifest does not describe "
            f"its contents, and replacing on that basis would leave unrecorded "
            f"files under a manifest that never mentions them")
    files = previous["files"]
    if not isinstance(files, list):
        raise PilotOutputError(
            f"{manifest_path}: its 'files' is a {type(files).__name__}, not a "
            f"list — refusing to delete anything from a directory whose manifest "
            f"does not describe its contents")
    targets = []
    for position, entry in enumerate(files):
        if not isinstance(entry, dict):
            raise PilotOutputError(
                f"{manifest_path}: files[{position}] is a "
                f"{type(entry).__name__}, not an object — refusing to delete "
                f"anything from a directory whose manifest is malformed")
        if "path" not in entry:
            raise PilotOutputError(
                f"{manifest_path}: files[{position}] has no 'path' — refusing to "
                f"delete anything from a directory whose manifest is malformed")
        path = entry["path"]
        if not isinstance(path, str) or not path:
            raise PilotOutputError(
                f"{manifest_path}: files[{position}]['path'] is "
                f"{path!r}, expected a non-empty string — refusing to delete "
                f"anything from a directory whose manifest is malformed")
        # Raises PilotOutputError itself if the path escapes the output root.
        target = _resolved_target(output, path)
        if target == _resolved_target(output, MANIFEST_NAME):
            raise PilotOutputError(
                f"{manifest_path}: files[{position}]['path'] is {path!r}, which "
                f"resolves to the manifest itself — refusing to delete anything. "
                f"{MANIFEST_NAME} is self-excluded from 'files' by construction "
                f"and is removed separately after the stale files, so a manifest "
                f"listing itself is malformed for this replacement")
        targets.append(target)
    return targets


def write_bundle(files: dict, output) -> dict:
    """Write the bundle under `output` and return its manifest.

    The manifest is written LAST, after every file it describes has landed — the
    house rule that `latest.json` follows on R2, for the same reason: a manifest
    that exists is then a promise the bundle behind it is complete.
    """
    output = Path(output)
    _prepare_output(output)
    for relative in sorted(files):
        if relative == MANIFEST_NAME:
            continue
        target = _resolved_target(output, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[relative])
    _resolved_target(output, MANIFEST_NAME).write_bytes(files[MANIFEST_NAME])
    return json.loads(files[MANIFEST_NAME].decode("utf-8"))


def _identity(path: Path, label: str) -> dict:
    """The measured identity of one source artifact: role, sha256, byte size.

    Measured from the bytes on disk, never taken from a flag. The whole point of
    recording it in the bundle is that a reader can re-measure the source and get
    the same value, and a declared-but-unmeasured number cannot do that.

    THE FILESYSTEM PATH IS DELIBERATELY NOT RECORDED. It is not the artifact's
    identity — the digest is — and writing it would make two bundles built from
    the same bytes in different directories differ, which is a determinism
    property quietly traded away for a debugging convenience the command already
    prints on stdout.
    """
    payload = path.read_bytes()
    return {"role": label, "sha256": _sha256(payload), "byte_size": len(payload)}


def build(index_path, evaluation_path, output) -> dict:
    """THE entry point: read two artifacts, build the bundle, write it, return
    the manifest.

    Nothing else is opened. No repository root is resolved, no codebook is read,
    no corpus is decompressed, no authority selector is consulted — which is the
    milestone property, and it is the reason the emitted bundle can answer every
    browser question without any of them.
    """
    index_path = Path(index_path)
    evaluation_path = Path(evaluation_path)
    index = retrieval.load_index(index_path)
    evaluation = load_evaluation(evaluation_path)
    identities = {
        "index": {**_identity(index_path, "evidence_index"),
                  "schema": index.get("schema")},
        "evaluation": {**_identity(evaluation_path, "m2_evaluation"),
                       "schema": evaluation.get("schema")},
    }
    return write_bundle(build_bundle(index, evaluation, identities), output)


# ---------------------------------------------------------------------------
# Verifiers — assertions about EMITTED BYTES, not about this module's intentions
# ---------------------------------------------------------------------------
#
# Each one re-derives its expectation from the source artifact and compares it
# against what a reader would actually load out of the bundle directory. They
# take the emitted files rather than the in-memory structures on purpose: a check
# that reads the dict this module just built would agree with itself, which is
# the probe defect this repository has recorded more times than any other.

class PilotConservationError(PilotError):
    """The emitted bundle does not reconcile with the artifact it was built from."""


def _load_emitted(output: Path, relative: str) -> dict:
    with open(_resolved_target(output, relative), "r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_manifest(output) -> dict:
    """Every file on disk is in the manifest with its real digest, and vice versa.

    Walks the directory rather than the file map, so a file written by an earlier
    build and left behind would be an EXTRA and would fail here — which is the
    check that makes the replacement rule in `_prepare_output` trustworthy rather
    than merely documented.
    """
    output = Path(output)
    manifest = _load_emitted(output, MANIFEST_NAME)
    on_disk = {str(path.relative_to(output)).replace("\\", "/")
               for path in output.rglob("*") if path.is_file()}
    on_disk.discard(manifest["self_excluded"])
    recorded = {entry["path"] for entry in manifest["files"]}
    if on_disk != recorded:
        raise PilotConservationError(
            f"manifest and bundle disagree: {sorted(on_disk - recorded)[:5]} are on "
            f"disk but unrecorded, {sorted(recorded - on_disk)[:5]} are recorded "
            f"but absent")
    for entry in manifest["files"]:
        payload = _resolved_target(output, entry["path"]).read_bytes()
        if _sha256(payload) != entry["sha256"] or len(payload) != entry["byte_size"]:
            raise PilotConservationError(
                f"{entry['path']}: manifest records {entry['sha256']} / "
                f"{entry['byte_size']} bytes, the file measures "
                f"{_sha256(payload)} / {len(payload)} bytes")
    return manifest


def verify_population(output, index: dict) -> dict:
    """Every corpus row reached the bundle, with its faces and its state.

    The failure this exists for is a FILTER — an eligibility or coverage test
    that quietly became a `continue` somewhere between the artifact and the
    browser. It is checked as a set comparison over oracle_ids rather than a
    count, because a count cannot see a substitution, and the two counts a filter
    changes are exactly the two it is easiest to also change in the manifest.
    """
    output = Path(output)
    cards = _load_emitted(output, "data/cards.json")
    expected_ids = [row["oracle_id"] for row in index["cards"]]
    if cards["oracle_id"] != expected_ids:
        missing = set(expected_ids) - set(cards["oracle_id"])
        extra = set(cards["oracle_id"]) - set(expected_ids)
        raise PilotConservationError(
            f"the card directory holds {len(cards['oracle_id']):,} ids, the source "
            f"index holds {len(expected_ids):,}: {len(missing)} missing "
            f"({sorted(missing)[:3]}), {len(extra)} unexpected "
            f"({sorted(extra)[:3]}), or the order differs")
    seen = {}
    for shard in sorted({_shard_of(oracle_id) for oracle_id in expected_ids}):
        for card_index, faces in _load_emitted(
                output, f"data/text/{shard}.json")["rows"]:
            seen[card_index] = faces
    for position, row in enumerate(index["cards"]):
        if seen.get(position) != row["faces"]:
            raise PilotConservationError(
                f"{row['oracle_id']} ({row['name']!r}): the emitted faces differ "
                f"from the source index's — {len(row['faces'])} face(s) expected")
    return {"cards": len(expected_ids), "faces_verified": len(seen)}


def verify_retrieval_equivalence(output, index: dict, *, anchors=None) -> dict:
    """The emitted blocks equal `retrieval.query` — candidates, features, ties, order.

    THE CHECK THE BROWSER BOUNDARY RESTS ON. It re-runs the accepted milestone-2
    capability and compares, for every anchor, the full ordered candidate list,
    each candidate's shared axis ids, each tie block's boundaries and each
    block's ordering features, against what was written to disk and mapped back
    through the bundle's own index tables. Exhaustive by default — all 6,275
    assigned anchors on the selected pilot, which is practical because the whole
    sweep is one pass of the same queries the build already made.

    `anchors` narrows it to named oracle_ids, for a focused test that does not
    want the full sweep. Narrowing is the caller's explicit choice and is
    reported in the result, so a partial run cannot be read as the full one.
    """
    output = Path(output)
    cards = _load_emitted(output, "data/cards.json")
    axes = _load_emitted(output, "data/axes.json")["order"]
    by_position = cards["oracle_id"]
    position = {oracle_id: number for number, oracle_id in enumerate(by_position)}
    view = retrieval.EvidenceIndexView(index)

    targets = [row["oracle_id"] for row in index["cards"] if row["memberships"]]
    if anchors is not None:
        wanted = set(anchors)
        targets = [oracle_id for oracle_id in targets if oracle_id in wanted]
    loaded: dict = {}
    checked = candidates_checked = blocks_checked = 0
    for oracle_id in targets:
        shard = _shard_of(oracle_id)
        if shard not in loaded:
            loaded[shard] = {row[0]: row[1] for row in
                             _load_emitted(output, f"data/retrieval/{shard}.json")["rows"]}
        emitted = loaded[shard][position[oracle_id]]
        expected = retrieval.query(index, oracle_id=oracle_id, view=view)
        if emitted["candidate_count"] != expected["candidate_count"]:
            raise PilotConservationError(
                f"{oracle_id}: the bundle records {emitted['candidate_count']} "
                f"candidates, the accepted retrieval returns "
                f"{expected['candidate_count']}")
        if emitted["result_state"] != expected["result_state"]:
            raise PilotConservationError(
                f"{oracle_id}: result_state {emitted['result_state']!r} != "
                f"{expected['result_state']!r}")
        flat = [(by_position[member[0]], [axes[a] for a in member[1]],
                 block["first_rank"], block["size"],
                 block["shared_axis_count"], block["shared_axis_cardinalities"])
                for block in emitted["blocks"] for member in block["members"]]
        reference = [(candidate["oracle_id"],
                      candidate["features"]["shared_axis_ids"],
                      candidate["tie_block_first_rank"],
                      candidate["tie_block_size"],
                      candidate["features"]["shared_axis_count"],
                      candidate["features"]["shared_axis_cardinalities"])
                     for candidate in expected["candidates"]]
        if flat != reference:
            first = next((i for i, (a, b) in enumerate(zip(flat, reference))
                          if a != b), min(len(flat), len(reference)))
            raise PilotConservationError(
                f"{oracle_id}: the bundle's candidate sequence diverges from the "
                f"accepted retrieval at position {first} — bundle "
                f"{flat[first] if first < len(flat) else 'END'!r}, retrieval "
                f"{reference[first] if first < len(reference) else 'END'!r}")
        checked += 1
        candidates_checked += len(flat)
        blocks_checked += len(emitted["blocks"])
    return {"anchors_checked": checked, "candidates_checked": candidates_checked,
            "tie_blocks_checked": blocks_checked,
            "exhaustive": anchors is None,
            "scope": ("every assigned anchor in the index" if anchors is None
                      else f"{len(targets)} named anchors, a NARROWED run")}
