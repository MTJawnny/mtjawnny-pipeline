#!/usr/bin/env python3
"""Retroactive Gate #0 legality scrub (batch-6 D1, 2026-07-30, ratified
2026-07-30). Rescans every member_oracle_ids list in codebook.json against
foundry_common.gate_passes() (legal or restricted in >=1 Scryfall format)
and removes gated-out members in place, regardless of axis status
(active/killed/merged/renamed/deferred) -- D1: "rescan every member of
every codebook axis (all versions >= current)". Emits a scrub report
alongside the updated codebook so the removal is auditable, and logs a
gate0_scrub history entry on every touched axis.

Usage: python3 experiments/foundry_gate0_scrub.py
"""
import sys
import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "gate0_scrub_report.json"


def main():
    cards_all, _ = fc.load_corpus()  # raw/unfiltered -- need every historical member, gated or not
    codebook = json.loads(CODEBOOK_PATH.read_text())
    axes = codebook["axes"]

    report_entries = []
    total_checked = 0
    total_gated = 0
    missing = []

    for slug in sorted(axes.keys()):
        entry = axes[slug]
        members = entry.get("member_oracle_ids", [])
        if not members:
            continue
        kept, gated = [], []
        for oid in members:
            total_checked += 1
            c = cards_all.get(oid)
            if c is None:
                missing.append((slug, oid))
                kept.append(oid)  # can't gate what we can't look up -- surfaced, not silently dropped
                continue
            if fc.gate_passes(c):
                kept.append(oid)
            else:
                gated.append({"oracle_id": oid, "name": c.get("name"), "set": c.get("set")})
        if gated:
            total_gated += len(gated)
            entry["member_oracle_ids"] = kept
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

    fc.write_json(CODEBOOK_PATH, codebook)
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
    print(f"wrote {CODEBOOK_PATH} (in place) and {REPORT_PATH}")


if __name__ == "__main__":
    main()
