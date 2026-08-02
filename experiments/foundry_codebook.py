#!/usr/bin/env python3
"""The /2 codebook accessor boundary -- the single load/save/validate surface
for experiments/out/foundry/codebook.json under schema foundry-codebook/2
(B-MIGRATION-DISCOVERY.md sec.10 A1/A13, sec.9 R11).

Schema /2 in one paragraph: an axis entry's `members` (renamed from /1's
`member_oracle_ids`, CDR-11) is a list of member objects sorted by
oracle_id, each carrying a STACK of assertions -- one per support event --
sorted by (class, source_ref). Assertions are append-merge only: nothing in
this module ever modifies or removes an existing assertion except
remove_det_assertions(), which is scoped to rule-derived rows (A8). A
member-level `tier` is present IFF every assertion on it is llm-class
(full-weight human/rule-derived evidence makes the consensus tier moot);
its value follows the ratified lane-aware rule (ADDENDUM-4: intersection
across runs = corroborated, singleton = provisional, scored on the
codebook and codebook-grammar lanes only).

Everything here halts loudly rather than guessing (house style). Every
mutating script in the arc ends with lint() and writes through
write_codebook_atomic().

CLI (AG-CLI-01) -- the home for hand-ratified single-member additions:
  python3 experiments/foundry_codebook.py add-member \\
      --slug rule:some-axis --oracle-id <uuid> --class human \\
      --source-ref captain-cli-2026-08-01 --quote "<oracle clause>"
  python3 experiments/foundry_codebook.py lint
"""
import os
import re
import sys
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
BACKUPS_DIR = fc.FOUNDRY_OUT_DIR / "backups"
LATEST_ARTIFACT_PATH = REPO_ROOT / "data" / "artifacts" / "latest.json"

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
ASSERTION_KEY_ORDER = (
    "class", "source_ref", "original_lane", "effective_lane",
    "promotion_reason", "quote", "corpus_ref", "evidence_status",
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


class LintError(Exception):
    """Raised by lint(); callers turn it into a loud halt."""


# --------------------------------------------------------------------------
# corpus reference
# --------------------------------------------------------------------------

def corpus_ref_current() -> str:
    """The corpus snapshot date every quote in this repo is drawn from
    (CDR-09). Read from data/artifacts/latest.json rather than hardcoded so
    it moves with the corpus instead of rotting in a constant."""
    if not LATEST_ARTIFACT_PATH.exists():
        fc.halt(f"{LATEST_ARTIFACT_PATH} not found — cannot establish the corpus snapshot date "
                f"that corpus_ref must record; refusing to guess")
    latest = json.loads(LATEST_ARTIFACT_PATH.read_text(encoding="utf-8"))
    version = latest.get("version")
    if not isinstance(version, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", version):
        fc.halt(f"{LATEST_ARTIFACT_PATH}: 'version' is {version!r}, expected a YYYY-MM-DD snapshot date")
    return version


# --------------------------------------------------------------------------
# load / id views
# --------------------------------------------------------------------------

def load_codebook(path: Path = None) -> dict:
    """Loads a /2 codebook. Halts on /1 (or anything else) in BOTH directions
    per the discovery's sec.3 recommendation -- /1-era tooling meeting a /2
    file already dies on `set()` of dicts, but that is an accident of Python
    semantics, not a designed failure. This is the designed one."""
    path = Path(path) if path is not None else CODEBOOK_PATH
    if not path.exists():
        fc.halt(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        cb = json.load(f)
    schema = cb.get("schema")
    if schema != SCHEMA_V2:
        if schema == SCHEMA_V1:
            fc.halt(f"{path} is schema {SCHEMA_V1!r} (pre-migration). This loader reads {SCHEMA_V2!r} only "
                    f"— run experiments/foundry_migrate_codebook_v2.py, or use the frozen /1 producer "
                    f"(foundry_reconcile.py) if you genuinely meant the legacy shape")
        fc.halt(f"{path}: unexpected schema {schema!r}, expected {SCHEMA_V2!r}")
    return cb


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

def build_assertion(cls: str, source_ref: str, quote: str, corpus_ref: str,
                    evidence_status: str = "quoted", original_lane: str = None,
                    effective_lane: str = None, promotion_reason: str = None) -> dict:
    """Builds one assertion with ASSERTION_KEY_ORDER insertion order. Optional
    keys are omitted entirely rather than emitted as null -- an absent lane is
    not the same statement as an unknown lane."""
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
    (class, source_ref) order, halts on a duplicate (class, source_ref) for
    this member, and recomputes the member's tier per A1. Existing assertions
    are NEVER modified or removed here -- an assertion is a historical claim
    about a support event; a later event adds a row, it does not rewrite one.

    Returns "created" or "merged" so callers can report counts."""
    if not _UUID_RE.match(oracle_id or ""):
        fc.halt(f"merge_assertion: {oracle_id!r} is not a valid oracle_id (uuid) shape")
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
            fc.halt(f"merge_assertion: member {oracle_id} already carries a "
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


def lint_or_halt(codebook: dict, path_label: str = "codebook") -> dict:
    try:
        return lint(codebook, path_label)
    except LintError as e:
        fc.halt(str(e))


# --------------------------------------------------------------------------
# atomic write (A13)
# --------------------------------------------------------------------------

def _serialize(codebook: dict) -> str:
    return json.dumps(codebook, indent=2, ensure_ascii=False) + "\n"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_codebook_atomic(path: Path, codebook: dict, path_label: str = None) -> str:
    """Temp file -> flush+fsync -> re-read and lint the TEMP -> atomic rename
    over the live file (A13). The live file is never in a half-written state,
    and a file that fails lint never becomes the live file: the temp is what
    gets validated, so a crash between validation and rename leaves the good
    old file in place plus an inert .tmp for a human to notice.

    Returns the sha256 of the file now at `path`."""
    path = Path(path)
    label = path_label or str(path)
    lint_or_halt(codebook, f"{label} (pre-write, in memory)")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    payload = _serialize(codebook)
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())

    with open(tmp_path, "r", encoding="utf-8") as f:
        readback = json.load(f)
    lint_or_halt(readback, f"{label} (readback of temp)")
    if _serialize(readback) != payload:
        fc.halt(f"{tmp_path}: re-serializing the readback does not reproduce the written bytes — "
                f"non-deterministic serialization, refusing to install this file")

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    os.replace(tmp_path, path)
    if sha256_of(path) != digest:
        fc.halt(f"{path}: post-rename sha256 does not match the verified temp — filesystem-level "
                f"corruption, do not trust this file")
    return digest


def backup_codebook(tag: str, path: Path = None) -> Path:
    """Timestamped, readback-verified pre-mutation backup. codebook.json is
    gitignored (.gitignore: experiments/out/) -- these backups ARE the rollback
    path, so the readback check is not optional."""
    path = Path(path) if path is not None else CODEBOOK_PATH
    if not path.exists():
        fc.halt(f"{path} not found — nothing to back up")
    cb = json.loads(path.read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUPS_DIR / f"codebook.v{cb.get('version', '?')}.{tag}.{stamp}.json"
    shutil.copy2(path, dest)
    src_sha, dst_sha = sha256_of(path), sha256_of(dest)
    if src_sha != dst_sha or path.stat().st_size != dest.stat().st_size:
        fc.halt(f"backup readback mismatch: {path} sha={src_sha} vs {dest} sha={dst_sha} — "
                f"refusing to proceed without a verified rollback point")
    print(f"backup: {dest.name}  size={dest.stat().st_size}  sha256={dst_sha}")
    return dest


# --------------------------------------------------------------------------
# CLI (AG-CLI-01)
# --------------------------------------------------------------------------

def cmd_add_member(args):
    cb = load_codebook(CODEBOOK_PATH)
    axes = cb["axes"]
    slug = args.slug
    if slug not in axes:
        fc.halt(f"axis {slug!r} does not exist in the codebook")
    entry = axes[slug]
    status = entry.get("status")
    if status not in ("active", "deferred"):
        fc.halt(f"axis {slug!r} has status {status!r} — members are only added to active or deferred "
                f"axes; reviving or renaming an axis is a ratification, not a CLI operation")
    if not _UUID_RE.match(args.oracle_id or ""):
        fc.halt(f"{args.oracle_id!r} is not a valid oracle_id (uuid) shape")
    if args.cls not in CLASSES:
        fc.halt(f"--class {args.cls!r} not in {CLASSES}")
    if entry.get("source") == "DET" and args.cls == "rule-derived":
        fc.halt(f"axis {slug!r} is DET-owned: its rule-derived membership is written by "
                f"foundry_det_pass.py from a ratified pattern, never by hand. A human or llm "
                f"assertion on this axis is allowed (A8) — a rule-derived one is not")
    evidence_status = args.evidence_status
    quote = args.quote or ""
    if not quote.strip() and evidence_status != "legacy-captain-seed":
        fc.halt("--quote is empty and --evidence-status is not 'legacy-captain-seed' — "
                "evidence-quote-or-discard; the A3 exemption is for historical captain-seed rows only")
    if args.cls == "llm" and (args.original_lane is None or args.effective_lane is None):
        fc.halt("llm-class assertions require --original-lane and --effective-lane")

    corpus_ref = args.corpus_ref or corpus_ref_current()
    assertion = build_assertion(
        args.cls, args.source_ref, quote, corpus_ref, evidence_status,
        original_lane=args.original_lane, effective_lane=args.effective_lane,
        promotion_reason=args.promotion_reason,
    )

    backup_codebook("pre-cli-add-member")
    outcome = merge_assertion(entry, args.oracle_id, assertion)
    entry.setdefault("history", []).append({
        "batch": args.source_ref, "action": "member_assertion_merged",
        "note": (f"{outcome} member via foundry_codebook.py add-member: class={args.cls}, "
                 f"source_ref={args.source_ref}, oracle_id={args.oracle_id}"
                 + (f" — {args.note}" if args.note else "")),
    })
    digest = write_codebook_atomic(CODEBOOK_PATH, cb, "codebook.json")
    print(f"{slug}: assertion {outcome} on {args.oracle_id} "
          f"({len(entry['members'])} members on this axis)")
    print(f"codebook.json sha256={digest}")


def cmd_lint(args):
    path = Path(args.path) if args.path else CODEBOOK_PATH
    cb = load_codebook(path)
    stats = lint_or_halt(cb, str(path))
    print(f"lint clean: {stats['axes']} axes, {stats['members']} members, "
          f"{stats['assertions']} assertions — {path}")
    for key in stats["exemptions_applied"]:
        print(f"  DECLARED EXEMPTION APPLIED — {key[0]}: {key[1]}")
        print(f"    {AXIS_INVARIANT_EXEMPTIONS[key]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add-member", help="merge one hand-ratified assertion onto an axis")
    p_add.add_argument("--slug", required=True)
    p_add.add_argument("--oracle-id", required=True)
    p_add.add_argument("--class", dest="cls", required=True, choices=list(CLASSES))
    p_add.add_argument("--source-ref", required=True)
    p_add.add_argument("--quote", default="")
    p_add.add_argument("--corpus-ref", default=None, help="defaults to the current corpus snapshot date")
    p_add.add_argument("--evidence-status", default="quoted", choices=list(EVIDENCE_STATUSES))
    p_add.add_argument("--original-lane", default=None, choices=list(LANES))
    p_add.add_argument("--effective-lane", default=None, choices=list(LANES))
    p_add.add_argument("--promotion-reason", default=None)
    p_add.add_argument("--note", default="")
    p_add.set_defaults(func=cmd_add_member)

    p_lint = sub.add_parser("lint", help="run the standing invariant check")
    p_lint.add_argument("--path", default=None)
    p_lint.set_defaults(func=cmd_lint)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
