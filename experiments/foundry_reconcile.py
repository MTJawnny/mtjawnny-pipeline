#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- reconciler. Consumes a decisions/batch-N.json
export from foundry_review.html (the exported file is "the sole source of
truth", per spec) plus that batch's review JSON (batch-N.json, carrying the
axis definitions/members the decisions refer to), applies Captain's
keep/kill/merge/rename verdicts + member removals + Captain's own new axes
and per-card tags to the running codebook, and writes:
  - experiments/out/foundry/codebook.json (vN+1)
  - experiments/out/foundry/captain_tags_queue.json (appended, provenance-noted)
  - experiments/out/foundry/reports/batch-<N>-diff.md (one-page diff + convergence metrics)

FROZEN /1 LEGACY PRODUCER (B-MIGRATION-DISCOVERY.md sec.9 R4, sec.10 A4).
This script speaks foundry-codebook/1 and nothing else. The live codebook is
foundry-codebook/2 as of the 2026-08-01 migration, so this file can no longer
write it: it exists to replay the batch-1..7 decisions paper trail into a
/1-shaped codebook at a scratch destination, which is how per-membership
provenance is ATTRIBUTED. Per A4, the earlier "permanent rebuild chain"
framing is RETRACTED -- replay alone cannot reproduce post-walk state
(walk-ratification renames, the Black Gate move and the batch-7 surgery are
unscripted history), so there is NO replay-based rebuild chain. The live file
plus its verified backups are the source of truth.

Two hard guards enforce that, rather than a comment asking nicely:
  - loading a codebook whose schema is not foundry-codebook/1 HALTS;
  - writing to the live codebook path HALTS. A destination must be named
    explicitly with --legacy-output, and it must not be the live file.

Codebook schema (this repo's own convention -- the spec fixes batch-N.json/
decisions-N.json, not the codebook's on-disk shape):
{
  "schema": "foundry-codebook/1",
  "version": "0.<N>",  # frozen at "1.0" once Captain calls the convergence gate
  "axes": {
    "<slug>": {"definition","scope","source","parameterized",
               "member_oracle_ids": [...], "status": "active|killed|merged|renamed",
               "merged_into": null, "history": [{"batch","action","note"}]}
  },
  "batches_reconciled": [1, 2, ...]
}

Usage:
  python3 experiments/foundry_reconcile.py --batch-json experiments/out/foundry/review/batch-1.json \\
      --decisions experiments/out/foundry/decisions/batch-1.json \\
      --legacy-output /tmp/replay/codebook.json
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

# The live artifact this script is forbidden to touch. CODEBOOK_PATH below is
# the (re-pointable) destination; LIVE_CODEBOOK_PATH is the fixed thing that
# destination is checked against.
LIVE_CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
CODEBOOK_PATH = LIVE_CODEBOOK_PATH
TAGS_QUEUE_PATH = fc.FOUNDRY_OUT_DIR / "captain_tags_queue.json"
REPORTS_DIR = fc.FOUNDRY_OUT_DIR / "reports"

SCHEMA_V1 = "foundry-codebook/1"

A_HANDFUL = 5  # convergence-gate wording ("no new axis exceeding a handful of members")


def _guard_not_live(path: Path) -> None:
    """Guard 2 (A4): this producer may never write the live codebook. The live
    file is /2 and is maintained by the /2 tooling; a /1 write here would
    silently replace an object-shaped membership list with bare strings."""
    if Path(path).resolve() == LIVE_CODEBOOK_PATH.resolve():
        fc.halt(f"foundry_reconcile.py is the FROZEN /1 legacy producer and refuses to write the live "
                f"codebook at {LIVE_CODEBOOK_PATH}. The live file is {'foundry-codebook/2'} — pass "
                f"--legacy-output with a scratch destination if you meant to replay the decisions "
                f"trail, or use experiments/foundry_codebook.py for /2 writes")


def load_codebook() -> dict:
    if CODEBOOK_PATH.exists():
        with open(CODEBOOK_PATH, "r", encoding="utf-8") as f:
            codebook = json.load(f)
        # Guard 1 (A4): never read a shape this script cannot correctly write.
        if codebook.get("schema") != SCHEMA_V1:
            fc.halt(f"{CODEBOOK_PATH}: schema is {codebook.get('schema')!r}, but this script reads and "
                    f"writes {SCHEMA_V1!r} only. Applying /1 union logic to a /2 file would append bare "
                    f"oracle_id strings into object-shaped member lists")
        return codebook
    return {"schema": SCHEMA_V1, "version": "0.0", "axes": {}, "batches_reconciled": []}


def load_json(path: Path) -> dict:
    if not path.exists():
        fc.halt(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def reconcile(batch_json_path: Path, decisions_path: Path, freeze: bool) -> dict:
    _guard_not_live(CODEBOOK_PATH)
    batch = load_json(batch_json_path)
    decisions = load_json(decisions_path)

    if batch.get("schema") != "foundry-review/1":
        fc.halt(f"{batch_json_path}: unexpected schema {batch.get('schema')!r}, expected foundry-review/1")
    if decisions.get("schema") != "foundry-decisions/1":
        fc.halt(f"{decisions_path}: unexpected schema {decisions.get('schema')!r}, expected foundry-decisions/1")
    if batch["batch"] != decisions["batch"]:
        fc.halt(f"batch number mismatch: batch-json says {batch['batch']}, decisions says {decisions['batch']}")

    n = batch["batch"]
    codebook = load_codebook()
    if n in codebook["batches_reconciled"]:
        fc.halt(f"batch {n} has already been reconciled into the codebook (batches_reconciled={codebook['batches_reconciled']}) — refusing to double-apply")

    axes_by_slug = {a["slug"]: a for a in batch["axes"]}
    decided_axes = decisions.get("axes", {})

    counts = {"kept": 0, "killed": 0, "merged": 0, "renamed": 0, "deferred": 0, "undecided": 0}
    diff_lines = []

    # First pass: apply removed_members and stage each axis's resulting member set.
    staged = {}
    for slug, axis in axes_by_slug.items():
        dec = decided_axes.get(slug)
        removed_ids = {r["oracle_id"] for r in (dec or {}).get("removed_members", [])}
        remaining = [m for m in axis["members"] if m["oracle_id"] not in removed_ids]
        staged[slug] = remaining

    for slug, axis in axes_by_slug.items():
        dec = decided_axes.get(slug)
        if dec is None:
            counts["undecided"] += 1
            diff_lines.append(f"- UNDECIDED: `{slug}` — no verdict in decisions file, codebook left untouched for this axis")
            continue

        verdict = dec.get("verdict")
        note = dec.get("note", "")
        members = staged[slug]

        if verdict == "keep":
            counts["kept"] += 1
            entry = codebook["axes"].get(slug, {
                "definition": axis["definition"], "scope": axis["scope"], "source": axis["source"],
                "parameterized": axis["parameterized"], "member_oracle_ids": [], "status": "active",
                "merged_into": None, "history": [],
            })
            if dec.get("definition_edit"):
                entry["definition"] = dec["definition_edit"]
            if dec.get("scope_edit"):
                entry["scope"] = dec["scope_edit"]
            entry["status"] = "active"
            entry["member_oracle_ids"] = sorted(set(entry["member_oracle_ids"]) | {m["oracle_id"] for m in members})
            entry["history"].append({"batch": n, "action": "kept", "note": note})
            codebook["axes"][slug] = entry
            diff_lines.append(f"- KEEP `{slug}` ({len(members)} members this batch, {len(entry['member_oracle_ids'])} total)"
                               + (f" — definition edited" if dec.get("definition_edit") else "")
                               + (f" — scope edited" if dec.get("scope_edit") else ""))

        elif verdict == "kill":
            counts["killed"] += 1
            entry = codebook["axes"].get(slug, {
                "definition": axis["definition"], "scope": axis["scope"], "source": axis["source"],
                "parameterized": axis["parameterized"], "member_oracle_ids": [], "status": "active",
                "merged_into": None, "history": [],
            })
            entry["status"] = "killed"
            entry["history"].append({"batch": n, "action": "killed", "note": note})
            codebook["axes"][slug] = entry
            diff_lines.append(f"- KILL `{slug}` — {note or '(no reason given)'}")

        elif verdict == "merge":
            target = dec.get("merge_into")
            if not target:
                fc.halt(f"axis {slug!r} has verdict=merge but no merge_into target")
            if target not in axes_by_slug and target not in codebook["axes"]:
                fc.halt(f"axis {slug!r} merge_into target {target!r} does not exist in this batch or the codebook")
            counts["merged"] += 1
            src_entry = codebook["axes"].get(slug, {
                "definition": axis["definition"], "scope": axis["scope"], "source": axis["source"],
                "parameterized": axis["parameterized"], "member_oracle_ids": [], "status": "active",
                "merged_into": None, "history": [],
            })
            src_entry["status"] = "merged"
            src_entry["merged_into"] = target
            src_entry["history"].append({"batch": n, "action": "merged", "note": f"merged into {target}: {note}"})
            codebook["axes"][slug] = src_entry

            tgt_entry = codebook["axes"].get(target, {
                "definition": axes_by_slug.get(target, {}).get("definition", ""),
                "scope": axes_by_slug.get(target, {}).get("scope", ""),
                "source": axes_by_slug.get(target, {}).get("source", "CAPTAIN"),
                "parameterized": axes_by_slug.get(target, {}).get("parameterized", False),
                "member_oracle_ids": [], "status": "active", "merged_into": None, "history": [],
            })
            tgt_entry["member_oracle_ids"] = sorted(set(tgt_entry["member_oracle_ids"]) | {m["oracle_id"] for m in members})
            tgt_entry["history"].append({"batch": n, "action": "received_merge", "note": f"absorbed {slug}"})
            codebook["axes"][target] = tgt_entry
            diff_lines.append(f"- MERGE `{slug}` -> `{target}` ({len(members)} members carried over) — {note}")

        elif verdict == "defer":
            # Batch-4 D5: axis is recorded with its members but not offered to
            # SYNTH as an active codebook slug (stage1b's load_codebook_reference
            # filters status=="active" only) and not merged anywhere, pending a
            # specific future Captain ruling. Distinct from "undecided": deferred
            # axes DO get a codebook entry, so future SYNTH prompts don't
            # re-propose the same free-lane candidate from scratch.
            counts["deferred"] += 1
            entry = codebook["axes"].get(slug, {
                "definition": axis["definition"], "scope": axis["scope"], "source": axis["source"],
                "parameterized": axis["parameterized"], "member_oracle_ids": [], "status": "active",
                "merged_into": None, "history": [],
            })
            entry["status"] = "deferred"
            entry["member_oracle_ids"] = sorted(set(entry["member_oracle_ids"]) | {m["oracle_id"] for m in members})
            entry["history"].append({"batch": n, "action": "deferred", "note": note})
            codebook["axes"][slug] = entry
            diff_lines.append(f"- DEFER `{slug}` ({len(members)} members this batch, {len(entry['member_oracle_ids'])} total) — {note or '(no reason given)'}")

        elif verdict == "rename":
            new_slug = dec.get("new_slug")
            if not new_slug:
                fc.halt(f"axis {slug!r} has verdict=rename but no new_slug")
            if new_slug in codebook["axes"] and codebook["axes"][new_slug].get("status") != "renamed":
                fc.halt(f"axis {slug!r} rename target {new_slug!r} already exists in the codebook — collision")
            counts["renamed"] += 1
            old_entry = codebook["axes"].get(slug, {})
            old_entry_status = {"status": "renamed", "renamed_to": new_slug,
                                 "history": old_entry.get("history", []) + [{"batch": n, "action": "renamed", "note": f"renamed to {new_slug}: {note}"}]}
            codebook["axes"][slug] = {**old_entry, **old_entry_status}

            new_entry = {
                "definition": dec.get("definition_edit") or axis["definition"],
                "scope": dec.get("scope_edit") or axis["scope"],
                "source": axis["source"], "parameterized": axis["parameterized"],
                "member_oracle_ids": sorted(set(old_entry.get("member_oracle_ids", [])) | {m["oracle_id"] for m in members}),
                "status": "active", "merged_into": None,
                "history": [{"batch": n, "action": "created_via_rename", "note": f"renamed from {slug}"}],
            }
            codebook["axes"][new_slug] = new_entry
            diff_lines.append(f"- RENAME `{slug}` -> `{new_slug}` ({len(members)} members)")

        else:
            fc.halt(f"axis {slug!r} has unrecognized verdict {verdict!r}")

    # Captain's own new axes -- HUMAN provenance, full weight, skip model pipeline entirely.
    # A slug that already exists under killed/renamed status (D8, batch-7 slug-continuity
    # revival) is REVIVED, not replaced: this UNIONS seed_members into the existing
    # member_oracle_ids and APPENDS to history, preserving the prior definition/scope/
    # history unless this batch's own definition/scope differ (in which case the batch's
    # values win, same as any other edit). A prior version of this code path silently
    # overwrote the whole entry -- including wiping pre-existing member_oracle_ids --
    # discovered batch-7 (rule:death-trigger-draw-card lost its 7 legacy members before
    # this fix); never repeat that regression.
    captain_axes = decisions.get("captain_axes", [])
    for ca in captain_axes:
        slug = ca["slug"]
        existing = codebook["axes"].get(slug)
        if existing is not None and existing.get("status") not in ("killed", "renamed"):
            fc.halt(f"captain_axes entry {slug!r} collides with an existing active codebook axis")
        if existing is not None:
            entry = existing
            entry["definition"] = ca["definition"]
            entry["scope"] = ca["scope"]
            entry["member_oracle_ids"] = sorted(set(entry.get("member_oracle_ids", [])) | set(ca.get("seed_members", [])))
            entry["status"] = "active"
            entry["merged_into"] = None
            entry.setdefault("history", []).append(
                {"batch": n, "action": "revived", "note": f"captain-review batch-{n} (slug-continuity revival, was {existing.get('status', '?')!r} before this batch)"})
            action_label = "CAPTAIN REVIVED AXIS"
        else:
            entry = {
                "definition": ca["definition"], "scope": ca["scope"], "source": "CAPTAIN",
                "parameterized": False, "member_oracle_ids": sorted(set(ca.get("seed_members", []))),
                "status": "active", "merged_into": None,
                "history": [{"batch": n, "action": "created", "note": f"captain-review batch-{n}"}],
            }
            action_label = "CAPTAIN NEW AXIS"
        codebook["axes"][slug] = entry
        diff_lines.append(f"- {action_label} `{slug}` ({len(ca.get('seed_members', []))} seed members, {len(entry['member_oracle_ids'])} total)")

    # Captain's own per-card tags -- queued for tags/cards.yaml, never auto-written there.
    captain_tags = decisions.get("captain_card_tags", [])
    if captain_tags:
        queue = json.loads(TAGS_QUEUE_PATH.read_text(encoding="utf-8")) if TAGS_QUEUE_PATH.exists() else []
        for ct in captain_tags:
            queue.append({
                "oracle_id": ct["oracle_id"], "tag": ct["tag"], "note": ct.get("note", ""),
                "provenance": f"captain-review batch-{n}",
                "queued_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
        fc.write_json(TAGS_QUEUE_PATH, queue)
        diff_lines.append(f"- queued {len(captain_tags)} captain_card_tags to {TAGS_QUEUE_PATH} (not yet in tags/cards.yaml)")

    # Cross-axis member additions -- a card ratified onto an axis it is NOT
    # a batch-N member of in this batch's own review JSON (e.g. batch-4 D2's
    # reassignment, D3's M8 mixed-target second tag). Distinct from the
    # normal per-axis "keep" path, which only ever unions in a batch's own
    # membership for that slug. Applied after every other pass so the target
    # axis entry already exists with this batch's own members staged in.
    member_additions = decisions.get("member_additions", [])
    for add in member_additions:
        slug = add["slug"]
        oid = add["oracle_id"]
        if slug not in codebook["axes"]:
            fc.halt(f"member_addition targets axis {slug!r}, which does not exist in the codebook after this batch's other passes")
        entry = codebook["axes"][slug]
        if oid in entry["member_oracle_ids"]:
            fc.halt(f"member_addition: oracle_id {oid} is already a member of {slug!r} — redundant addition, check the decisions file")
        entry["member_oracle_ids"] = sorted(entry["member_oracle_ids"] + [oid])
        entry["history"].append({"batch": n, "action": "member_added", "note": add.get("note", "")})
        diff_lines.append(f"- MEMBER ADDED to `{slug}`: {add.get('name', oid)} — {add.get('note', '')}")

    # Convergence metrics.
    total_axis_members_this_batch = sum(len(a["members"]) for a in batch["axes"])
    other_lane_n = len(batch.get("other_lane", []))
    total_assignments = total_axis_members_this_batch + other_lane_n
    other_rate = 100.0 * other_lane_n / total_assignments if total_assignments else 0.0
    decided_n = counts["kept"] + counts["killed"] + counts["merged"] + counts["renamed"]
    kill_merge_rename_rate = 100.0 * (counts["killed"] + counts["merged"] + counts["renamed"]) / decided_n if decided_n else 0.0
    large_new_axes = [
        (slug, len(e["member_oracle_ids"])) for slug, e in codebook["axes"].items()
        if e.get("status") == "active" and any(h["batch"] == n and h["action"] in ("kept", "created", "created_via_rename") for h in e.get("history", []))
        and len(e["member_oracle_ids"]) > A_HANDFUL
    ]

    active_axis_count = sum(1 for e in codebook["axes"].values() if e.get("status") == "active")

    if freeze:
        codebook["version"] = "1.0"
    else:
        codebook["version"] = f"0.{n}"
    codebook["batches_reconciled"] = sorted(set(codebook["batches_reconciled"]) | {n})
    fc.write_json(CODEBOOK_PATH, codebook)

    report_lines = [
        f"# Batch {n} reconciliation diff — codebook v{codebook['version']}",
        "",
        f"Axes reviewed: {len(axes_by_slug)} | kept={counts['kept']} killed={counts['killed']} "
        f"merged={counts['merged']} renamed={counts['renamed']} deferred={counts['deferred']} undecided={counts['undecided']}",
        f"Active axes in codebook after this batch: {active_axis_count}",
        "",
        f"## Convergence metrics (batch {n})",
        f"- OTHER-lane rate: {other_rate:.1f}% ({other_lane_n}/{total_assignments} assignments)",
        f"- kill/merge/rename rate: {kill_merge_rename_rate:.1f}% ({counts['killed'] + counts['merged'] + counts['renamed']}/{decided_n} decided axes)",
        f"- axes exceeding {A_HANDFUL} members touched this batch: {len(large_new_axes)}"
        + (f" ({', '.join(f'{s}={c}' for s, c in large_new_axes)})" if large_new_axes else ""),
        "",
        "Gate passes when: OTHER-lane rate <~5% AND kill/merge/rename rate visibly declining across two "
        "consecutive batches AND no new axis exceeds a handful of members (Captain calls it, not this script).",
        "",
        "## Per-axis diff",
        *diff_lines,
    ]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"batch-{n}-diff.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("\n".join(report_lines))
    print(f"\nwrote {CODEBOOK_PATH} (v{codebook['version']}, {active_axis_count} active axes)")
    print(f"wrote {report_path}")
    return codebook


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch-json", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--legacy-output", required=True,
                        help="where to write the /1 replay codebook. Required, and must not be the "
                             "live codebook — this producer is frozen (A4)")
    parser.add_argument("--freeze", action="store_true", help="Captain has called the convergence gate — freeze codebook at v1.0")
    args = parser.parse_args()

    global CODEBOOK_PATH
    CODEBOOK_PATH = Path(args.legacy_output)
    _guard_not_live(CODEBOOK_PATH)
    reconcile(Path(args.batch_json), Path(args.decisions), args.freeze)


if __name__ == "__main__":
    main()
