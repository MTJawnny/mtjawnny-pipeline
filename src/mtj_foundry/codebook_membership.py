"""Codebook membership semantics — spec-declared re-homing and Gate #0 scrubbing.

## What this is

S11's permanent owner of what it MEANS to change which cards an axis holds,
separately from how that change is executed.

* `apply_spec` -- the ratified re-homing operations a membership spec may
  declare (new axes, renames, merges, moves, multi-axis adds, seeds, drops,
  quote / definition / scope corrections), applied to a DEEP COPY in a fixed
  order, with every precondition refused loudly. The spec never decides
  anything; every move is declared.
* `total_members` / `member_conservation` -- MEMBER CONSERVATION. The expected
  delta is derived from the DECLARED operations, so any change the spec did not
  ask for is caught: members move, they are not created or lost.
* `scrub_gate0_members` -- the batch-6 D1 Gate #0 rule. A gate-0 removal drops
  the WHOLE member object, every assertion included, unlike a DET refresh (A8):
  Gate #0 is a card-level fact that makes every proof of that card's membership
  moot at once. A member whose card cannot be looked up is KEPT and surfaced,
  never silently dropped.

Members carry their assertions -- and therefore their evidence quotes --
verbatim. Nothing is re-evidenced by a move.

## What this is NOT

* No load, no lint call, no determinism ×2 wrapper, no backup, no atomic write,
  no report file, no printing and no process exit. The legacy executors
  (`foundry_membership_move`, `foundry_gate0_scrub`) keep that workflow, and the
  AG-CLI-01 member-add command is untouched: its merge primitive was already
  `mtj_foundry.codebook`'s.
* Nothing here authorizes mutating the selected codebook. These are in-memory
  operations; acceptance of this module is dry-run conservation.

Refusals raise `MembershipSpecError` / `Gate0ScrubError` carrying the historic
halt text verbatim.

## Layer law

Stdlib only.
"""

from __future__ import annotations

import copy
from typing import Callable

__all__ = [
    "Gate0ScrubError",
    "MembershipError",
    "MembershipSpecError",
    "apply_spec",
    "member_conservation",
    "scrub_gate0_members",
    "total_members",
]


class MembershipError(RuntimeError):
    """Base for membership refusals. Raised, never printed, never exited."""


class MembershipSpecError(MembershipError):
    """A declared operation whose precondition does not hold. Nothing applies."""


class Gate0ScrubError(MembershipError):
    """The scrub met data drift rather than a legality question."""


def apply_spec(codebook: dict, spec: dict) -> dict:
    """Apply `spec` to a deep copy of `codebook` and return the copy.

    Order is fixed and load-bearing: new axes, renames, merges, move
    validation, moves, adds, seeds, drops, quote edits, definition edits,
    scope edits. The input document is never modified.
    """
    cb = copy.deepcopy(codebook)
    axes = cb["axes"]
    batch = spec["batch"]
    ruling = spec.get("ruling", "")

    def refuse(message):
        raise MembershipSpecError(message)

    # --- create declared new axes -------------------------------------------
    for slug, meta in sorted(spec.get("new_axes", {}).items()):
        if slug in axes:
            refuse(f"{slug}: already exists — collision with a declared new axis")
        axes[slug] = {
            "definition": meta["definition"],
            "scope": meta["scope"],
            "source": meta.get("source", "CAPTAIN"),
            "parameterized": bool(meta.get("parameterized", False)),
            "members": [],
            "status": "active",
            "merged_into": None,
            "history": [{"batch": batch, "action": "created",
                         "note": meta.get("note", "") + (f" {ruling}" if ruling else "")}],
        }

    # --- renames -------------------------------------------------------------
    # CDR-09 precedent: the old slug becomes a `renamed` tombstone that RETAINS
    # its members, and the new slug carries them forward. Applied before moves
    # so a move may target a freshly renamed axis.
    for old, meta in sorted(spec.get("renames", {}).items()):
        if old not in axes:
            refuse(f"{old}: rename source not in the codebook")
        new = meta["to"]
        if new in axes:
            refuse(f"{old} -> {new}: rename target already exists — collision")
        entry = axes[old]
        new_entry = copy.deepcopy(entry)
        new_entry["status"] = "active"
        new_entry["merged_into"] = None
        new_entry.pop("renamed_to", None)
        if meta.get("definition"):
            new_entry["definition"] = meta["definition"]
        new_entry["history"] = list(entry.get("history", [])) + [
            {"batch": batch, "action": "created_via_rename",
             "note": f"renamed from {old}: {meta.get('why','')} {ruling}".strip()}]
        axes[new] = new_entry
        entry["status"] = "renamed"
        entry["renamed_to"] = new
        entry["merged_into"] = None
        entry.setdefault("history", []).append(
            {"batch": batch, "action": "renamed",
             "note": f"renamed to {new}: {meta.get('why','')} {ruling}".strip()})

    # --- merges --------------------------------------------------------------
    # Members RELOCATE to the target and the source is emptied, unlike a rename
    # tombstone: a merged axis's members live on the surviving slug, so keeping
    # a copy on the source would double-count them.
    for mg in spec.get("merges", []):
        src, dst = mg["from"], mg["to"]
        for s in (src, dst):
            if s not in axes:
                refuse(f"{s}: merge axis not in the codebook")
        have = {m["oracle_id"] for m in axes[dst]["members"]}
        moving = [m for m in axes[src]["members"] if m["oracle_id"] not in have]
        axes[dst]["members"] = sorted(axes[dst]["members"] + [copy.deepcopy(m) for m in moving],
                                      key=lambda m: m["oracle_id"])
        axes[dst].setdefault("history", []).append(
            {"batch": batch, "action": "absorbed_merge",
             "note": f"absorbed {len(moving)} member(s) from {src}: {mg.get('why','')} {ruling}".strip()})
        axes[src]["members"] = []
        axes[src]["status"] = "merged"
        axes[src]["merged_into"] = dst
        axes[src].setdefault("history", []).append(
            {"batch": batch, "action": "merged",
             "note": f"merged into {dst}: {mg.get('why','')} {ruling}".strip()})

    # --- validate every move before mutating any of them --------------------
    routed = {}
    for mv in spec.get("moves", []):
        src, dst = mv["from"], mv["to"]
        if src not in axes:
            refuse(f"{src}: source axis not in the codebook")
        if axes[src].get("status") != "active":
            refuse(f"{src}: status is {axes[src].get('status')!r}, expected 'active'")
        if dst not in axes:
            refuse(f"{dst}: destination axis does not exist and is not declared in new_axes")
        have = {m["oracle_id"] for m in axes[src].get("members", [])}
        for oid in mv["members"]:
            if oid not in have:
                refuse(f"{oid}: not a member of {src} — the spec and live state disagree")
            key = (src, oid)
            if key in routed:
                refuse(f"{oid}: routed twice out of {src}")
            routed[key] = dst

    # --- apply --------------------------------------------------------------
    for mv in spec.get("moves", []):
        src, dst = mv["from"], mv["to"]
        ids = set(mv["members"])
        by_id = {m["oracle_id"]: m for m in axes[src]["members"]}
        carried = [copy.deepcopy(by_id[o]) for o in sorted(ids)]

        existing = {m["oracle_id"] for m in axes[dst]["members"]}
        for m in carried:
            if m["oracle_id"] in existing:
                refuse(f"{m['oracle_id']}: already a member of destination {dst}")
        axes[dst]["members"] = sorted(axes[dst]["members"] + carried,
                                      key=lambda m: m["oracle_id"])
        axes[dst].setdefault("history", []).append(
            {"batch": batch, "action": "members_received",
             "note": f"received {len(carried)} member(s) from {src}: {mv.get('why', '')} {ruling}".strip()})

        axes[src]["members"] = [m for m in axes[src]["members"] if m["oracle_id"] not in ids]
        axes[src].setdefault("history", []).append(
            {"batch": batch, "action": "members_moved",
             "note": f"moved {len(carried)} member(s) to {dst}: {mv.get('why', '')} {ruling}".strip()})

    # --- multi-axis additions ------------------------------------------------
    # Captain-ratified 2026-08-02: a card holds membership on EVERY axis it
    # genuinely satisfies. An `add` copies a card onto an additional axis
    # without removing it from where it already lives, so it legitimately RAISES
    # the total member count -- the conservation gate accounts for these
    # explicitly rather than treating the increase as corruption.
    for ad in spec.get("adds", []):
        src, dst, oid = ad["from"], ad["to"], ad["member"]
        if src not in axes:
            refuse(f"{src}: add source axis not in the codebook")
        if dst not in axes:
            refuse(f"{dst}: add destination does not exist and is not declared in new_axes")
        by_id = {m["oracle_id"]: m for m in axes[src].get("members", [])}
        if oid not in by_id:
            refuse(f"{oid}: not a member of {src} — cannot copy a membership that is not there")
        if any(m["oracle_id"] == oid for m in axes[dst]["members"]):
            refuse(f"{oid}: already a member of {dst}")
        # Evidence does NOT travel unchanged. The source quote may be a FRAGMENT
        # scoped to the source axis's claim, in which case it does not prove the
        # destination's claim. An add must state the quote that proves ITS axis.
        carried = copy.deepcopy(by_id[oid])
        if "quote" not in ad:
            refuse(f"add {oid} -> {dst}: no `quote` given. The source quote proves the "
                   f"SOURCE axis's claim and may not prove this one; state the evidence "
                   f"for this axis explicitly (evidence-quote-or-discard).")
        # Provenance must name what actually made THIS assignment.
        # `captain-cli-<date>` is the ratified label for a hand-ratified addition.
        for a in carried.get("assertions", []):
            a["quote"] = ad["quote"]
            a["source_ref"] = spec.get("source_ref", "captain-cli-2026-08-02")
        axes[dst]["members"] = sorted(axes[dst]["members"] + [carried],
                                      key=lambda m: m["oracle_id"])
        axes[dst].setdefault("history", []).append(
            {"batch": batch, "action": "member_added_multi_axis",
             "note": f"also a member of {src}; multi-axis membership. "
                     f"{ad.get('why', '')} {ruling}".strip()})

    # --- seeds ---------------------------------------------------------------
    # A member that is not currently on ANY axis. Every seed states its own
    # quote: evidence-quote-or-discard binds harder here, since no prior
    # assertion exists to inherit from.
    for sd in spec.get("seeds", []):
        slug, oid = sd["to"], sd["member"]
        if slug not in axes:
            refuse(f"{slug}: seed destination does not exist and is not declared in new_axes")
        if "quote" not in sd or not sd["quote"].strip():
            refuse(f"seed {oid} -> {slug}: no quote. A seeded member has no prior "
                   f"assertion to inherit, so its evidence must be stated explicitly.")
        if any(m["oracle_id"] == oid for m in axes[slug]["members"]):
            refuse(f"{oid}: already a member of {slug}")
        axes[slug]["members"] = sorted(
            axes[slug]["members"] + [{
                "oracle_id": oid,
                "assertions": [{
                    "class": sd.get("class", "rule-derived"),
                    "source_ref": spec.get("source_ref", "captain-cli-2026-08-02"),
                    "quote": sd["quote"],
                    "corpus_ref": sd.get("corpus_ref", "2026-08-02"),
                    "evidence_status": "quoted",
                }],
            }], key=lambda m: m["oracle_id"])
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "member_seeded",
             "note": f"seeded {oid}: {sd.get('why','')} {ruling}".strip()})

    # --- drops ---------------------------------------------------------------
    # Removing a membership that was never true. Declared explicitly because it
    # LOWERS the member count, and a silent decrease is indistinguishable from
    # corruption.
    for dr in spec.get("drops", []):
        slug, oid = dr["from"], dr["member"]
        if slug not in axes:
            refuse(f"{slug}: drop source not in the codebook")
        before_n = len(axes[slug]["members"])
        axes[slug]["members"] = [m for m in axes[slug]["members"] if m["oracle_id"] != oid]
        if len(axes[slug]["members"]) == before_n:
            refuse(f"{oid}: not a member of {slug} — nothing to drop")
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "member_dropped",
             "note": f"dropped {oid}: {dr.get('why','')} {ruling}".strip()})

    # --- assertion quote corrections ----------------------------------------
    # An assignment whose quote does not prove its axis is unevidenced.
    for slug, per_card in sorted(spec.get("quote_edits", {}).items()):
        if slug not in axes:
            refuse(f"{slug}: quote_edits names an axis not in the codebook")
        by_id = {m["oracle_id"]: m for m in axes[slug].get("members", [])}
        for oid, val in sorted(per_card.items()):
            # A value may be a bare quote string, or {quote, source_ref} when the
            # provenance label needs correcting too.
            new_quote = val if isinstance(val, str) else val["quote"]
            new_ref = None if isinstance(val, str) else val.get("source_ref")
            if oid not in by_id:
                refuse(f"{oid}: quote_edits names a non-member of {slug}")
            if not new_quote.strip():
                refuse(f"{oid} on {slug}: refusing to set an empty quote")
            for a in by_id[oid].get("assertions", []):
                a["quote"] = new_quote
                if new_ref:
                    a["source_ref"] = new_ref
                if a.get("evidence_status") == "legacy-captain-seed":
                    a["evidence_status"] = "quoted"
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "quotes_corrected",
             "note": f"corrected evidence quote(s) for {len(per_card)} member(s). {ruling}".strip()})

    # --- definition corrections ---------------------------------------------
    for slug, new_def in sorted(spec.get("definition_edits", {}).items()):
        if slug not in axes:
            refuse(f"{slug}: definition_edits names an axis not in the codebook")
        axes[slug]["definition"] = new_def
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "definition_corrected",
             "note": f"definition corrected. {ruling}".strip()})

    # --- scope corrections ---------------------------------------------------
    # The scope field is a claim like any other and can drift from the members.
    # No gate reads scope, so it needs its own declared op.
    for slug, new_scope in sorted(spec.get("scope_edits", {}).items()):
        if slug not in axes:
            refuse(f"{slug}: scope_edits names an axis not in the codebook")
        if not str(new_scope).strip():
            refuse(f"{slug}: refusing to set an empty scope")
        old_scope = axes[slug].get("scope")
        if old_scope == new_scope:
            refuse(f"{slug}: scope is already {new_scope!r} — the spec and live state agree, "
                   f"so this edit is a no-op and probably a mistake")
        axes[slug]["scope"] = new_scope
        axes[slug].setdefault("history", []).append(
            {"batch": batch, "action": "scope_corrected",
             "note": f"scope {old_scope!r} -> {new_scope!r}. {ruling}".strip()})

    return cb


def total_members(cb: dict) -> int:
    return sum(len(e.get("members", [])) for e in cb["axes"].values())


def member_conservation(before: dict, after: dict, spec: dict) -> dict:
    """The member-count delta the spec DECLARED, against the one it produced.

    Renames retain members on the tombstone (CDR-09 precedent) and therefore
    add a copy; merges relocate and are neutral except for members the target
    already had. Returns the counts and `ok`; never raises -- the verdict is
    the caller's to act on.
    """
    n_before, n_after = total_members(before), total_members(after)
    n_adds = len(spec.get("adds", [])) + len(spec.get("seeds", []))
    n_drops = len(spec.get("drops", []))
    n_rename_copies = sum(len(before["axes"][old].get("members", []))
                          for old in spec.get("renames", {}) if old in before["axes"])
    n_merge_dupes = 0
    for mg in spec.get("merges", []):
        if mg["from"] in before["axes"] and mg["to"] in before["axes"]:
            have = {m["oracle_id"] for m in before["axes"][mg["to"]]["members"]}
            n_merge_dupes += sum(1 for m in before["axes"][mg["from"]]["members"]
                                 if m["oracle_id"] in have)
    expected = n_before + n_adds - n_drops + n_rename_copies - n_merge_dupes
    return {"before": n_before, "after": n_after, "expected": expected,
            "adds": n_adds, "drops": n_drops, "rename_copies": n_rename_copies,
            "merge_dupes": n_merge_dupes, "ok": n_after == expected}


def scrub_gate0_members(axes: dict, cards_all: dict,
                        is_eligible: Callable[[dict], bool]) -> dict:
    """Remove every Gate-#0-ineligible member from every axis, IN PLACE.

    Visits axes in slug order regardless of status (D1: "rescan every member of
    every codebook axis"). `cards_all` is the RAW, unfiltered corpus -- every
    historical member has to be looked up, gated or not. `is_eligible` is the
    Gate #0 predicate, supplied by the caller and called per member.

    Returns `{"report_entries", "total_checked", "total_gated"}`. A member whose
    card is absent is KEPT; if any is absent, `Gate0ScrubError` is raised AFTER
    the walk, naming the first five, and the caller must not write.
    """
    report_entries = []
    total_checked = 0
    total_gated = 0
    missing = []

    for slug in sorted(axes.keys()):
        entry = axes[slug]
        members = entry.get("members", [])
        if not members:
            continue
        kept, gated = [], []
        for member in members:
            oid = member["oracle_id"]
            total_checked += 1
            c = cards_all.get(oid)
            if c is None:
                missing.append((slug, oid))
                kept.append(member)  # can't gate what we can't look up -- surfaced, not silently dropped
                continue
            if is_eligible(c):
                kept.append(member)
            else:
                gated.append({"oracle_id": oid, "name": c.get("name"), "set": c.get("set"),
                              "assertions_dropped": len(member["assertions"])})
        if gated:
            total_gated += len(gated)
            entry["members"] = kept
            entry.setdefault("history", []).append({
                "batch": 6, "action": "gate0_scrub",
                "note": f"removed {len(gated)} nowhere-legal member(s) per batch-6 D1 Gate #0: "
                        + ", ".join(f"{g['name']!r} [{g['set']}]" for g in gated),
            })
            report_entries.append({"slug": slug, "status": entry.get("status"),
                                   "n_before": len(members), "n_after": len(kept),
                                   "gated_members": gated})

    if missing:
        raise Gate0ScrubError(
            f"gate0 scrub: {len(missing)} member oracle_id(s) not found in raw corpus at all "
            f"(data drift, not a legality question) -- resolve by hand: {missing[:5]}...")
    return {"report_entries": report_entries, "total_checked": total_checked,
            "total_gated": total_gated}
