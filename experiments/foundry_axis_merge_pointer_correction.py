#!/usr/bin/env python3
"""One-off correction to codebook /2: clear the stale `merged_into` pointer on
rule:etb-with-negative-counters. Captain-ratified 2026-08-01 ("un-merge
rule:etb-with-negative-counters, take it out of merge status") following the
re-audit hardening pass, which added the axis-level lint invariant that
surfaced it.

WHAT WENT WRONG. Batch 5 merged rule:etb-with-negative-counters into
rule:etb-with-counters; the target absorbed its members (its own history
records `received_merge`). Batches 6 and 7 then re-KEPT the source axis, and
foundry_reconcile.py's keep path sets `status = "active"` without ever
clearing `merged_into` -- so the axis came back to life still carrying a
pointer saying it had been absorbed. Nothing downstream had followed that
pointer yet, but session 2 does extensive slug routing and would have.

WHY THE FIX IS HERE AND NOT IN THE PRODUCER. foundry_reconcile.py is FROZEN
as the /1 legacy producer (A4): its replay output is load-bearing for the
migration's byte-reproducibility, so changing its keep path would silently
change the provenance attribution of the whole codebook. The /2-era remedy is
the standing lint invariant (already added) plus this one-field data
correction.

WHAT IS AND IS NOT BEING SAID. This does not undo the batch-5 merge -- that
happened, the target kept the members it absorbed, and both history records
stay. It records that the axis has since been independently re-ratified twice
and is a live axis in its own right (measured: 3 members, zero overlap with
the target's 68; the definitions differ by counter polarity, -1/-1 vs +1/+1).
Only the contradictory pointer goes.

Idempotent and re-runnable (G4): a second run is a no-op that writes nothing.

Usage: python3 experiments/foundry_axis_merge_pointer_correction.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

SLUG = "rule:etb-with-negative-counters"
EXPECTED_STALE_TARGET = "rule:etb-with-counters"
RULING_LABEL = "captain-ruling-2026-08-01"


def main():
    codebook = fcb.load_codebook(fcb.CODEBOOK_PATH)
    entry = codebook["axes"].get(SLUG)
    if entry is None:
        fc.halt(f"{SLUG} is not in the codebook — refusing to guess what was meant")

    if entry.get("merged_into") is None:
        print(f"{SLUG}: merged_into is already null — correction already applied, nothing written")
        return

    # Pre-state assertions: correct exactly the situation that was ruled on,
    # never something that merely resembles it.
    if entry.get("merged_into") != EXPECTED_STALE_TARGET:
        fc.halt(f"{SLUG}: merged_into is {entry.get('merged_into')!r}, expected "
                f"{EXPECTED_STALE_TARGET!r} — this is not the state Captain ruled on")
    if entry.get("status") != "active":
        fc.halt(f"{SLUG}: status is {entry.get('status')!r}, expected 'active'. A genuinely merged "
                f"axis keeps its pointer; only a re-kept one carries it staleley")

    target = codebook["axes"].get(EXPECTED_STALE_TARGET)
    overlap = fcb.member_id_set(entry) & fcb.member_id_set(target)
    if overlap:
        fc.halt(f"{SLUG} shares {len(overlap)} member(s) with {EXPECTED_STALE_TARGET} — un-merging "
                f"would leave the same card on two axes that claim different mechanisms; this needs "
                f"a membership ruling, not a pointer fix")

    fcb.backup_codebook("pre-merge-pointer-correction")
    entry["merged_into"] = None
    entry.setdefault("history", []).append({
        "batch": RULING_LABEL, "action": "merged_into_cleared",
        "note": (f"Captain-ratified 2026-08-01: cleared the stale merged_into={EXPECTED_STALE_TARGET} "
                 f"pointer left behind when this axis was merged at batch 5 and then re-kept at "
                 f"batches 6 and 7 (foundry_reconcile.py's keep path reactivates an axis without "
                 f"clearing the pointer). The batch-5 merge itself stands and the target retains the "
                 f"members it absorbed; this axis is a live axis in its own right, re-ratified twice, "
                 f"{len(fcb.member_ids(entry))} members, zero overlap with the target. Surfaced by the "
                 f"axis-level lint invariant added in the 2026-08-01 re-audit hardening pass."),
    })

    digest = fcb.write_codebook_atomic(fcb.CODEBOOK_PATH, codebook, "codebook.json")
    print(f"{SLUG}: merged_into {EXPECTED_STALE_TARGET!r} -> null "
          f"(status stays 'active', {len(fcb.member_ids(entry))} members unchanged)")
    print(f"codebook.json sha256={digest}")


if __name__ == "__main__":
    main()
