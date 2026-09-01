"""The codebook SEMANTIC MODEL — schema vocabulary, membership, assertions, lint.

## What this is

The permanent home of one coherent capability: what a `foundry-codebook/2`
document *means*. Six things and five error types — read a member list, build an
assertion, decide a member's tier, merge a support event, remove a DET pass's own
rows, and check the whole document against its standing invariants.

Schema /2 in one paragraph: an axis entry's `members` (renamed from /1's
`member_oracle_ids`, CDR-11) is a list of member objects sorted by oracle_id,
each carrying a STACK of assertions -- one per support event -- sorted by
(class, source_ref). Assertions are append-merge only: nothing here ever
modifies or removes an existing assertion except `remove_det_assertions()`,
which is scoped to rule-derived rows (A8). A member-level `tier` is present IFF
every assertion on it is llm-class (full-weight human/rule-derived evidence
makes the consensus tier moot); its value follows the ratified lane-aware rule
(ADDENDUM-4: intersection across runs = corroborated, singleton = provisional,
scored on the codebook and codebook-grammar lanes only).

The durable contract is `docs/B-MIGRATION-DISCOVERY.md` sec.10 (A1/A3/A5/A8/A9/
A11/A13/A14) and sec.11 (SEMANTIC LOCALITY, resolving FL-2). sec.9 R11 is the
standing-invariant mandate lint discharges.

## What this is NOT

It is not a move of `experiments/foundry_codebook.py`. That module is the ORACLE
for every behaviour below -- each value here is differentially compared against
it over the whole live codebook -- but its BOUNDARY is not the target
architecture, and four of its properties are deliberately not reproduced:

* **No process exit.** The legacy module calls `fc.halt()`, which prints to
  stderr and calls `sys.exit(1)`. A library may not end the process. Every fatal
  state raises a typed error carrying the legacy message body verbatim, and the
  transitional legacy facade translates it back into the existing `halt()`, so
  legacy callers keep their `STOP — …` line and exit code exactly.
* **Not one error type.** `foundry_verify_migration` distinguishes "lint refused
  it" from "the process died"; collapsing every failure into one class would
  make those controls agree by accident. A malformed locality, an invalid
  oracle_id and a duplicate support event are three different facts about three
  different callers, so they are three types.
* **No filesystem, no paths, no root.** Nothing here opens a file, knows where
  the repository is, or carries a module-level codebook path. Loading, JSON,
  digests and the atomic write stay behind the legacy boundary in this slice;
  this module never learns they exist.
* **No legacy imports, no `sys.path`.** Stdlib only -- `re` and nothing else.

## Standing hardening is EVIDENCE, carried verbatim

Two families below are accepted Worker-era hardening rather than sec.10 Captain
amendments, and moving them here does not promote them:

* `SOURCE_REF_FAMILIES` (F4, re-audit 2026-08-01) -- which source_ref families
  each provenance class may cite;
* the axis-status / `renamed_to` / `merged_into` coherence checks, and the
  `AXIS_INVARIANT_EXEMPTIONS` register that declares debt against them.

Their behaviour and their provenance comments travel unchanged. They are
preserved, not re-ratified, and nothing here may weaken, broaden or reinterpret
them.
"""

from __future__ import annotations

import re

__all__ = [
    "ASSERTION_KEY_ORDER",
    "CodebookError",
    "DET_SOURCE_REF_PREFIX",
    "DuplicateAssertionError",
    "InvalidOracleIdError",
    "LintError",
    "LocalityError",
    "SCHEMA_V1",
    "SCHEMA_V2",
    "build_assertion",
    "expected_tier",
    "lint",
    "member_by_id",
    "member_id_set",
    "member_ids",
    "merge_assertion",
    "normalize_locality",
    "remove_det_assertions",
]

SCHEMA_V2 = "foundry-codebook/2"
SCHEMA_V1 = "foundry-codebook/1"

CLASSES = ("human", "llm", "rule-derived")
# NOTE (F7, re-audit 2026-08-01): "legacy-captain-seed" is also worn by the 11
# member_additions rows, which are Captain-ratified per-card additions rather
# than captain_axes seeds. The label is the ratified vocabulary (A1/A3) and the
# data is correct, but a future gate must not read this field alone to count
# seeds: 47 rows are seeds (source_ref "captain-seed-batch-N") and 11 are
# additions (source_ref "batch-N"). source_ref is what distinguishes them.
EVIDENCE_STATUSES = ("quoted", "legacy-captain-seed")
LANES = ("codebook", "codebook-grammar", "free")
AXIS_STATUSES = ("active", "killed", "merged", "renamed", "deferred")
# ADDENDUM-4's lane-aware consensus ruling: only these lanes are scored for
# corroboration at all; free-lane output is unioned as discovery, never
# treated as agreement or disagreement.
SCOREABLE_LANES = ("codebook", "codebook-grammar")
TIERS = ("provisional", "corroborated")

# Fixed emission order for the keys of an assertion object. Determinism law:
# json.dump preserves insertion order, so producers build dicts in exactly
# this order and lint() re-checks it -- key order is part of the byte-identity
# guarantee, not a cosmetic preference.
#
# `locality` (added 2026-08-13, SEMANTIC LOCALITY, resolving FL-2) is the
# newest member and sits LAST on purpose. It is optional, so appending changes
# the emission order of exactly nothing that already exists: every assertion
# written before this change re-serializes byte-identically, which is what lets
# the backfill assert "the only delta is an added key" rather than eyeball it.
#
# NO SCHEMA BUMP TO /3. `original_lane`, `effective_lane` and
# `promotion_reason` are the precedent -- optional keys omitted entirely when
# absent rather than emitted as null, because an absent lane is not the same
# statement as an unknown lane. An absent ADDRESS is the same shape of claim:
# "nothing here asserts where this fact lives", not "this fact lives nowhere".
# A /2 reader that ignores an unknown key still reads every /2 fact correctly,
# so the format is forward-compatible in the one direction that matters.
ASSERTION_KEY_ORDER = (
    "class", "source_ref", "original_lane", "effective_lane",
    "promotion_reason", "quote", "corpus_ref", "evidence_status",
    "locality",
)
MEMBER_KEY_ORDER = ("oracle_id", "tier", "assertions")

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

# Closed source_ref vocabulary (A1). A source_ref that matches nothing here is
# a halt: an unrecognised provenance label is exactly the kind of silent drift
# the schema exists to prevent.
_SOURCE_REF_RES = (
    re.compile(r"^batch-[1-9][0-9]*$"),                 # triage batch membership
    re.compile(r"^captain-seed-batch-[1-9][0-9]*$"),    # captain_axes seed_members
    re.compile(r"^pay-life-scrub-2026-07-30$"),         # the committed one-off rehome
    re.compile(r"^captain-cli-\d{4}-\d{2}-\d{2}$"),     # hand-ratified CLI additions
    re.compile(r"^run[1-9][0-9]*$"),                    # SYNTH corpus-pass runs
    re.compile(r"^wave[1-9][0-9]*$"),                   # corroboration waves
    re.compile(r"^det-patterns-v2:\d+$"),               # DET pattern by pattern_index
)

DET_SOURCE_REF_PREFIX = "det-patterns-v2:"

# Which source_ref families each class is allowed to cite (F4, re-audit
# 2026-08-01). Without this, `class=human, source_ref=det-patterns-v2:3` and
# `class=rule-derived, source_ref=run1` both lint clean -- which is precisely
# the provenance-mislabelling the schema exists to prevent. The migration
# verifier caught that class of error, but it retires after session 1; this is
# the standing replacement.
SOURCE_REF_FAMILIES = {
    "rule-derived": re.compile(r"^det-patterns-v2:\d+$"),
    "human": re.compile(r"^(batch-[1-9][0-9]*|captain-seed-batch-[1-9][0-9]*"
                        r"|pay-life-scrub-2026-07-30|captain-cli-\d{4}-\d{2}-\d{2})$"),
    "llm": re.compile(r"^(run|wave)[1-9][0-9]*$"),
}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Known axis-level defects carried by the live codebook, each named with its
# cause, so lint can be strict without being permanently red. An entry here is
# a DECLARED debt awaiting a Captain ruling, not a silent pass -- lint prints
# every exemption it applies.
#
# Currently EMPTY, and worth keeping that way. Its one entry
# (rule:etb-with-negative-counters carrying a stale merged_into) was ruled on
# by Captain 2026-08-01 and corrected by
# experiments/foundry_axis_merge_pointer_correction.py, so the invariant now
# holds outright rather than by exception.
AXIS_INVARIANT_EXEMPTIONS = {}


# ---------------------------------------------------------------------------
# errors
#
# One base, four leaves. The leaves are separate because three different
# controls in the legacy tree key on three different failures, and a shared
# type would let two of them agree for the wrong reason. Every message body is
# MESSAGE_EXACT with the legacy `fc.halt()` argument it replaces, so the
# transitional facade reproduces the old stderr byte for byte by passing
# `str(error)` straight through.
# ---------------------------------------------------------------------------

class CodebookError(Exception):
    """Base for every codebook-model failure. Raised, never printed, never exited."""


class LintError(CodebookError):
    """Raised by lint(); callers turn it into a loud halt."""


class LocalityError(CodebookError):
    """A semantic address that is not a `[face_index, paragraph_index]` pair."""


class InvalidOracleIdError(CodebookError):
    """merge_assertion was handed something that is not an oracle_id (uuid) shape."""


class DuplicateAssertionError(CodebookError):
    """A `(class, source_ref)` support event already recorded on this member.

    A provenance bug, not an append (A1): an assertion is a historical claim
    about ONE support event, so a second identical pair means two things are
    being recorded as one.
    """


# --------------------------------------------------------------------------
# id views
# --------------------------------------------------------------------------

def member_ids(entry: dict) -> list:
    """Ordered oracle_id view of an axis entry's membership -- the /1
    `member_oracle_ids` list, reconstructed. Renamed shells with no member
    field return []."""
    return [m["oracle_id"] for m in entry.get("members", [])]


def member_id_set(entry: dict) -> set:
    return set(member_ids(entry))


def member_by_id(entry: dict, oracle_id: str):
    for m in entry.get("members", []):
        if m["oracle_id"] == oracle_id:
            return m
    return None


# --------------------------------------------------------------------------
# assertion construction / merge
# --------------------------------------------------------------------------

def normalize_locality(locality):
    """The stored form of a semantic address: `[face_index, paragraph_index]`.

    `foundry_locality.resolve()` returns its coordinate as a TUPLE, and JSON has
    no tuple -- so an un-normalised address would be a tuple in memory and a
    list on readback. Every determinism check in the write path compares
    serialized bytes and would not notice, but the atomic writer's readback lint
    and any in-memory equality check would, and a producer that stores one shape
    while the reader sees another is the "derived map is not the list it was
    derived from" trap with a JSON round-trip in the middle. So the conversion
    happens ONCE, here, and raises on anything else.
    """
    if isinstance(locality, tuple):
        locality = list(locality)
    if (not isinstance(locality, list) or len(locality) != 2
            or any(isinstance(x, bool) or not isinstance(x, int) or x < 0
                   for x in locality)):
        raise LocalityError(
            f"locality {locality!r} is not a [face_index, paragraph_index] "
            f"pair of non-negative integers. An address is a coordinate "
            f"into the shared face reader's output; refusing to store a "
            f"shape no resolver can read back.")
    return [int(locality[0]), int(locality[1])]


def build_assertion(cls: str, source_ref: str, quote: str, corpus_ref: str,
                    evidence_status: str = "quoted", original_lane: str = None,
                    effective_lane: str = None, promotion_reason: str = None,
                    locality=None) -> dict:
    """Builds one assertion with ASSERTION_KEY_ORDER insertion order. Optional
    keys are omitted entirely rather than emitted as null -- an absent lane is
    not the same statement as an unknown lane, and an absent ADDRESS is not the
    same statement as an address at the origin.

    `locality` is the semantic OWNER only. The evidence SPAN is deliberately
    not stored (B-MIGRATION-DISCOVERY.md sec.11, amendment A2): it is a
    pure function of
    quote + corpus snapshot, and storing it would duplicate something that can
    go stale on its own."""
    a = {"class": cls, "source_ref": source_ref}
    if original_lane is not None:
        a["original_lane"] = original_lane
    if effective_lane is not None:
        a["effective_lane"] = effective_lane
    if promotion_reason is not None:
        a["promotion_reason"] = promotion_reason
    a["quote"] = quote
    a["corpus_ref"] = corpus_ref
    a["evidence_status"] = evidence_status
    if locality is not None:
        a["locality"] = normalize_locality(locality)
    return a


def expected_tier(assertions: list):
    """A1's member-level tier rule, as a function. Returns the tier string an
    assertion stack demands, or None when the member must carry no tier at all
    (any human or rule-derived assertion present = full weight, consensus tier
    moot). Corroboration is the ratified lane-aware rule: agreement across two
    or more DISTINCT runs, counted on scoreable lanes only."""
    if not assertions:
        return None
    if any(a["class"] != "llm" for a in assertions):
        return None
    scoring_runs = {a["source_ref"] for a in assertions
                    if a.get("effective_lane") in SCOREABLE_LANES}
    return "corroborated" if len(scoring_runs) >= 2 else "provisional"


def _reorder_member(member: dict) -> dict:
    """Rebuilds a member dict in MEMBER_KEY_ORDER (tier omitted when absent)."""
    out = {"oracle_id": member["oracle_id"]}
    if member.get("tier") is not None:
        out["tier"] = member["tier"]
    out["assertions"] = member["assertions"]
    return out


def _assertion_sort_key(a: dict) -> tuple:
    return (a["class"], a["source_ref"])


def merge_assertion(entry: dict, oracle_id: str, assertion: dict) -> str:
    """THE membership-growth primitive. Creates the member if absent (sorted
    insert by oracle_id), appends the assertion in deterministic
    (class, source_ref) order, raises on a duplicate (class, source_ref) for
    this member, and recomputes the member's tier per A1. Existing assertions
    are NEVER modified or removed here -- an assertion is a historical claim
    about a support event; a later event adds a row, it does not rewrite one.

    Returns "created" or "merged" so callers can report counts."""
    if not _UUID_RE.match(oracle_id or ""):
        raise InvalidOracleIdError(
            f"merge_assertion: {oracle_id!r} is not a valid oracle_id (uuid) shape")
    members = entry.setdefault("members", [])
    member = member_by_id(entry, oracle_id)
    outcome = "merged"
    if member is None:
        member = {"oracle_id": oracle_id, "assertions": []}
        pos = 0
        while pos < len(members) and members[pos]["oracle_id"] < oracle_id:
            pos += 1
        members.insert(pos, member)
        outcome = "created"

    key = _assertion_sort_key(assertion)
    for existing in member["assertions"]:
        if _assertion_sort_key(existing) == key:
            raise DuplicateAssertionError(
                f"merge_assertion: member {oracle_id} already carries a "
                f"(class={key[0]!r}, source_ref={key[1]!r}) assertion — duplicate support events are "
                f"a provenance bug, not an append; nothing written")
    member["assertions"].append(assertion)
    member["assertions"].sort(key=_assertion_sort_key)

    tier = expected_tier(member["assertions"])
    if tier is None:
        member.pop("tier", None)
    else:
        member["tier"] = tier
    rebuilt = _reorder_member(member)
    member.clear()
    member.update(rebuilt)
    return outcome


def remove_det_assertions(entry: dict, source_ref_prefix: str = DET_SOURCE_REF_PREFIX) -> dict:
    """The ONLY removal primitive in this module, and it is scoped to
    rule-derived assertions (A8): a DET refresh replaces its own assertion set
    on an axis and never touches a human or llm assertion sharing the member.
    A member left with zero assertions is dropped -- membership survives
    exactly as long as some proof of it does.

    BOTH halves of the predicate are load-bearing. A human or llm row wearing a
    DET-looking `source_ref` is a provenance defect for `lint` to refuse, never
    a row for a DET refresh to delete: the class is what says whose row it is.

    Returns {"assertions_removed": n, "members_dropped": [oracle_id, ...]}."""
    members = entry.get("members", [])
    removed = 0
    dropped = []
    kept_members = []
    for m in members:
        before = len(m["assertions"])
        m["assertions"] = [a for a in m["assertions"]
                           if not (a["class"] == "rule-derived"
                                   and a["source_ref"].startswith(source_ref_prefix))]
        removed += before - len(m["assertions"])
        if not m["assertions"]:
            dropped.append(m["oracle_id"])
            continue
        tier = expected_tier(m["assertions"])
        if tier is None:
            m.pop("tier", None)
        else:
            m["tier"] = tier
        kept_members.append(_reorder_member(m))
    entry["members"] = kept_members
    return {"assertions_removed": removed, "members_dropped": dropped}


# --------------------------------------------------------------------------
# lint
# --------------------------------------------------------------------------

def lint(codebook: dict, path_label: str = "codebook") -> dict:
    """Standing invariant check (R11 / A1). Raises LintError listing EVERY
    violation found -- one run tells you the whole story rather than making
    you re-run per problem. Returns a small stats dict on success.

    Deliberately quote-blind in its messages (A14): a violation names the
    axis, oracle_id and field, never the evidence text."""
    v = []

    if codebook.get("schema") != SCHEMA_V2:
        v.append(f"top-level schema is {codebook.get('schema')!r}, expected {SCHEMA_V2!r}")
    axes = codebook.get("axes")
    if not isinstance(axes, dict):
        raise LintError(f"{path_label}: 'axes' is {type(axes).__name__}, expected object")

    n_members = 0
    n_assertions = 0
    exemptions_applied = []
    for slug, entry in axes.items():
        if "member_oracle_ids" in entry:
            v.append(f"{slug}: carries a /1 'member_oracle_ids' field — /2 uses 'members'")

        # --- axis-level invariants (F4). A status typo silently removes an axis
        # from every status-partitioned consumer -- the SYNTH prompt, the
        # consolidation active set -- with no error raised anywhere, so the
        # vocabulary check is doing more work than it looks like.
        status = entry.get("status")
        if status not in AXIS_STATUSES:
            v.append(f"{slug}: status {status!r} not in {AXIS_STATUSES}")
        for field, required_status in (("renamed_to", "renamed"), ("merged_into", "merged")):
            target = entry.get(field)
            if status == required_status and not target:
                v.append(f"{slug}: status is {required_status!r} but {field} is unset")
            if target and status != required_status:
                key = (slug, f"{field}-on-non-{required_status}")
                if key in AXIS_INVARIANT_EXEMPTIONS:
                    exemptions_applied.append(key)
                else:
                    v.append(f"{slug}: carries {field}={target!r} but status is {status!r} — a stale "
                             f"pointer will mis-route this axis's members")
            if target and target not in axes:
                v.append(f"{slug}: {field}={target!r} names an axis that does not exist")

        if "members" not in entry:
            continue
        members = entry["members"]
        if not isinstance(members, list):
            v.append(f"{slug}: 'members' is {type(members).__name__}, expected list")
            continue

        ids = []
        for m in members:
            if not isinstance(m, dict):
                v.append(f"{slug}: a member is {type(m).__name__}, expected object "
                         f"(a bare string here means a /1-era tool wrote to a /2 file)")
                continue
            oid = m.get("oracle_id")
            ids.append(oid)
            if not isinstance(oid, str) or not _UUID_RE.match(oid):
                v.append(f"{slug}: member oracle_id {oid!r} is not a valid uuid shape")
            if list(m.keys()) != [k for k in MEMBER_KEY_ORDER if k in m]:
                v.append(f"{slug}/{oid}: member keys {list(m.keys())} are not in canonical order "
                         f"{[k for k in MEMBER_KEY_ORDER if k in m]}")

            assertions = m.get("assertions")
            if not isinstance(assertions, list) or not assertions:
                v.append(f"{slug}/{oid}: 'assertions' must be a non-empty list "
                         f"(a member with no proof is not a member)")
                continue
            n_members += 1
            n_assertions += len(assertions)

            seen_keys = set()
            for a in assertions:
                if not isinstance(a, dict):
                    v.append(f"{slug}/{oid}: an assertion is {type(a).__name__}, expected object")
                    continue
                cls, sref = a.get("class"), a.get("source_ref")
                if cls not in CLASSES:
                    v.append(f"{slug}/{oid}: assertion class {cls!r} not in {CLASSES}")
                if not isinstance(sref, str) or not any(r.match(sref) for r in _SOURCE_REF_RES):
                    v.append(f"{slug}/{oid}: source_ref {sref!r} is outside the ratified vocabulary")
                elif cls in SOURCE_REF_FAMILIES and not SOURCE_REF_FAMILIES[cls].match(sref):
                    v.append(f"{slug}/{oid}: class {cls!r} may not cite source_ref {sref!r} — that "
                             f"label belongs to a different provenance class")
                if (cls, sref) in seen_keys:
                    v.append(f"{slug}/{oid}: duplicate assertion (class={cls!r}, source_ref={sref!r})")
                seen_keys.add((cls, sref))

                if list(a.keys()) != [k for k in ASSERTION_KEY_ORDER if k in a]:
                    v.append(f"{slug}/{oid}: assertion keys {list(a.keys())} are not in canonical order")
                unknown = [k for k in a if k not in ASSERTION_KEY_ORDER]
                if unknown:
                    v.append(f"{slug}/{oid}: assertion carries unknown key(s) {unknown}")

                ev = a.get("evidence_status")
                if ev not in EVIDENCE_STATUSES:
                    v.append(f"{slug}/{oid}: evidence_status {ev!r} not in {EVIDENCE_STATUSES}")
                corpus_ref = a.get("corpus_ref")
                if not isinstance(corpus_ref, str) or not corpus_ref:
                    v.append(f"{slug}/{oid}: assertion is missing corpus_ref")
                elif not _DATE_RE.match(corpus_ref):
                    v.append(f"{slug}/{oid}: corpus_ref {corpus_ref!r} is not a YYYY-MM-DD snapshot "
                             f"date — an unparseable corpus_ref makes quote validation impossible")
                quote = a.get("quote")
                if not isinstance(quote, str):
                    v.append(f"{slug}/{oid}: quote is {type(quote).__name__}, expected string")
                elif not quote.strip() and ev != "legacy-captain-seed":
                    v.append(f"{slug}/{oid}: empty quote without the legacy-captain-seed exemption (A3)")
                elif quote.strip() and ev == "legacy-captain-seed":
                    v.append(f"{slug}/{oid}: evidence_status is 'legacy-captain-seed' but a quote is "
                             f"present — the exemption means no quote was recorded; use 'quoted'")

                # SEMANTIC LOCALITY (FL-2, ratified 2026-08-13). Shape-checked
                # only: an address is SNAPSHOT-RELATIVE, so whether it still
                # resolves is a question for the corpus-loading reporter
                # (foundry_locality.py), not for a lint that reads one file and
                # no cards. What lint CAN prove is that the coordinate is
                # well-formed and that it is not making a claim its own
                # assertion cannot support.
                if "locality" in a:
                    loc = a["locality"]
                    if (not isinstance(loc, list) or len(loc) != 2
                            or any(isinstance(x, bool) or not isinstance(x, int)
                                   or x < 0 for x in loc)):
                        v.append(f"{slug}/{oid}: locality {loc!r} is not a "
                                 f"[face_index, paragraph_index] pair of non-negative integers")
                    elif not (isinstance(quote, str) and quote.strip()):
                        v.append(f"{slug}/{oid}: carries a locality address but no quote — an "
                                 f"address is DERIVED from the evidence quote, so a quoteless "
                                 f"assertion has nothing to resolve and cannot own one")

                for lane_field in ("original_lane", "effective_lane"):
                    if lane_field in a and a[lane_field] not in LANES:
                        v.append(f"{slug}/{oid}: {lane_field} {a[lane_field]!r} not in {LANES}")
                if cls == "llm":
                    for lane_field in ("original_lane", "effective_lane"):
                        if lane_field not in a:
                            v.append(f"{slug}/{oid}: llm assertion is missing required {lane_field}")
                else:
                    for lane_field in ("original_lane", "effective_lane", "promotion_reason"):
                        if lane_field in a:
                            v.append(f"{slug}/{oid}: {lane_field} is llm-class only, found on {cls!r}")

            if sorted(assertions, key=_assertion_sort_key) != assertions:
                v.append(f"{slug}/{oid}: assertions are not sorted by (class, source_ref)")

            want_tier = expected_tier(assertions)
            got_tier = m.get("tier")
            if got_tier is not None and got_tier not in TIERS:
                v.append(f"{slug}/{oid}: tier {got_tier!r} not in {TIERS}")
            if want_tier != got_tier:
                v.append(f"{slug}/{oid}: tier is {got_tier!r} but the assertion stack supports {want_tier!r}")

        if ids != sorted(x for x in ids if x is not None) and all(x is not None for x in ids):
            v.append(f"{slug}: members are not sorted by oracle_id")
        dupes = {x for x in ids if ids.count(x) > 1}
        if dupes:
            v.append(f"{slug}: duplicate member oracle_id(s) {sorted(dupes)}")

    if v:
        raise LintError(f"{path_label}: {len(v)} lint violation(s):\n  " + "\n  ".join(v[:50])
                        + (f"\n  ... and {len(v) - 50} more" if len(v) > 50 else ""))
    return {"axes": len(axes), "members": n_members, "assertions": n_assertions,
            "exemptions_applied": exemptions_applied}
