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

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "gate0_scrub_report.json"


def main():
    cards_all, _ = fc.load_corpus()  # raw/unfiltered -- need every historical member, gated or not
    codebook = fcb.load_codebook(CODEBOOK_PATH)
    axes = codebook["axes"]

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
            if fc.gate_passes(c):
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
        fc.halt(f"gate0 scrub: {len(missing)} member oracle_id(s) not found in raw corpus at all "
                 f"(data drift, not a legality question) -- resolve by hand: {missing[:5]}...")

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
