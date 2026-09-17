#!/usr/bin/env python3
"""Retroactive Gate #0 legality scrub (batch-6 D1, 2026-07-30, ratified
2026-07-30). Rescans every member list in codebook.json against
foundry_common.gate_passes() (legal or restricted in >=1 Scryfall format)
and removes gated-out members in place, regardless of axis status
(active/killed/merged/renamed/deferred) -- D1: "rescan every member of
every codebook axis (all versions >= current)". Emits a scrub report
alongside the updated codebook so the removal is auditable, and logs a
gate0_scrub history entry on every touched axis.

Under foundry-codebook/2 a gate-0 removal drops the WHOLE member object,
every assertion on it included -- unlike a DET refresh (A8), which replaces
only its own rule-derived assertions. The difference is not a policy choice:
Gate #0 is a card-level fact ("this card is legal nowhere, so it is not a
valid target for this pipeline at all"), which makes every proof of that
card's membership moot at once, whoever made it. There is nothing left to
preserve, so nothing is.

Usage: python3 experiments/foundry_gate0_scrub.py
"""
import sys
import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402
from mtj_foundry import codebook_membership as _membership  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "gate0_scrub_report.json"


def main():
    cards_all, _ = fc.load_corpus()  # raw/unfiltered -- need every historical member, gated or not
    codebook = fcb.load_codebook(CODEBOOK_PATH)
    axes = codebook["axes"]

    # S11: the Gate #0 membership rule -- walk every axis in slug order, drop a
    # gated-out member whole, keep and surface an unknown card, log the history
    # entry -- is `codebook_membership.scrub_gate0_members`. The load, the halt
    # on data drift, the backup, the atomic write, the report file and the
    # printed lines stay here.
    try:
        scrub = _membership.scrub_gate0_members(
            axes, cards_all, lambda card: fc.gate_passes(card))
    except _membership.Gate0ScrubError as error:
        fc.halt(str(error))
    report_entries = scrub["report_entries"]
    total_checked = scrub["total_checked"]
    total_gated = scrub["total_gated"]

    fcb.backup_codebook("pre-gate0-scrub")
    digest = fcb.write_codebook_atomic(CODEBOOK_PATH, codebook, "codebook.json")
    fc.write_json(REPORT_PATH, {
        "ruling": "batch-6 D1 Gate #0",
        "run_on": date.today().isoformat(),
        "total_member_rows_checked": total_checked,
        "total_gated_out": total_gated,
        "axes_touched": len(report_entries),
        "entries": report_entries,
    })
    print(f"gate0 scrub: checked {total_checked} member rows across {len(axes)} axes")
    print(f"gated out: {total_gated} rows across {len(report_entries)} axes")
    print(f"wrote {CODEBOOK_PATH} (sha256={digest}) and {REPORT_PATH}")


if __name__ == "__main__":
    main()
