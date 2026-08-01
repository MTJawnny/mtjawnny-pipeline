#!/usr/bin/env python3
"""Batch 8 A/B diff -- agreement matrices (all 6 arm pairs) and
tail-position curves (B, C vs. A), per Captain's 2026-08-01 directive.
Reads experiments/out/foundry/batch8_ab_raw_results.jsonl (written by
foundry_batch8_ab.py fetch-results) and the same batch7_assembled.json
card set + foundry_stage1b.pack_oracle_ids() (deterministic, so packs are
recomputed identically here rather than re-read from the request file).

Run: python3 experiments/foundry_batch8_diff.py
"""
import sys
import json
from pathlib import Path
from itertools import combinations
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_stage1b as s1b  # noqa: E402
import foundry_batch8_ab as b8  # noqa: E402

ARMS = ["A", "B", "C", "D"]
PACK_SIZES = {"B": 20, "C": 40}


def load_pack_position_maps(oracle_ids: list) -> dict:
    """{"B": {oid: (pack_idx, position_1_indexed)}, "C": {...}} -- recomputed
    from the same deterministic pack_oracle_ids(), not read from a file."""
    maps = {}
    for letter, size in PACK_SIZES.items():
        packs = s1b.pack_oracle_ids(oracle_ids, size)
        m = {}
        for pack_idx, pack in enumerate(packs):
            for pos, oid in enumerate(pack, 1):
                m[oid] = (pack_idx, pos)
        maps[letter] = m
    return maps


def parse_raw_results(path: Path) -> dict:
    """Returns axes[arm][oid] = frozenset of (lane, label) tuples. Missing/
    failed rows are recorded separately and reported, never silently
    treated as an empty axes set (that would corrupt the agreement math --
    'no data' and 'zero axes found' are different things)."""
    axes = {a: {} for a in ARMS}
    missing = defaultdict(list)

    if not path.exists():
        fc.halt(f"{path} not found -- run `foundry_batch8_ab.py fetch-results` first")

    rows_by_custom_id = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        rows_by_custom_id[row["custom_id"]] = row

    def extract_axes_set(axes_list):
        return frozenset(
            (a.get("lane"), a.get("label"))
            for a in axes_list
            if a.get("lane") and a.get("label")
        )

    # Arm A: one row per card, custom_id = "A-<oid>"
    a_rows = {cid: row for cid, row in rows_by_custom_id.items() if cid.startswith("A-")}
    for cid, row in a_rows.items():
        oid = cid[len("A-"):]
        result = row["result"]
        if result["type"] != "succeeded":
            missing["A"].append((oid, f"result type={result['type']}"))
            continue
        content = result["message"].get("content") or []
        if not content:
            missing["A"].append((oid, "empty content (refusal)"))
            continue
        try:
            data = json.loads(content[0]["text"])
        except json.JSONDecodeError:
            missing["A"].append((oid, "non-JSON output"))
            continue
        axes["A"][oid] = extract_axes_set(data.get("axes", []))

    # Arms B/C/D: one row per pack, custom_id = "<letter>-pack<i>"
    for letter in ("B", "C", "D"):
        pack_rows = {cid: row for cid, row in rows_by_custom_id.items() if cid.startswith(f"{letter}-pack")}
        for cid, row in pack_rows.items():
            result = row["result"]
            if result["type"] != "succeeded":
                missing[letter].append((cid, f"result type={result['type']}"))
                continue
            content = result["message"].get("content") or []
            if not content:
                missing[letter].append((cid, "empty content (refusal)"))
                continue
            try:
                data = json.loads(content[0]["text"])
            except json.JSONDecodeError:
                missing[letter].append((cid, "non-JSON output"))
                continue
            for entry in data.get("results", []):
                oid = entry.get("oracle_id")
                if not oid:
                    continue
                axes[letter][oid] = extract_axes_set(entry.get("axes", []))

    return axes, missing


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def agreement_matrix(axes: dict, oracle_ids: list) -> dict:
    """Per-pair: exact-match rate + mean Jaccard, over cards present in
    BOTH arms of the pair (missing rows on either side are excluded from
    that pair's denominator and counted separately)."""
    matrix = {}
    for arm_x, arm_y in combinations(ARMS, 2):
        exact = 0
        jacc_sum = 0.0
        n = 0
        excluded = 0
        for oid in oracle_ids:
            sx, sy = axes[arm_x].get(oid), axes[arm_y].get(oid)
            if sx is None or sy is None:
                excluded += 1
                continue
            n += 1
            if sx == sy:
                exact += 1
            jacc_sum += jaccard(sx, sy)
        matrix[f"{arm_x}-{arm_y}"] = {
            "n_compared": n, "n_excluded_missing": excluded,
            "exact_match_rate": exact / n if n else None,
            "mean_jaccard": jacc_sum / n if n else None,
        }
    return matrix


def tail_curves(axes: dict, oracle_ids: list, pack_maps: dict) -> dict:
    """For B and C (vs A): exact-match rate bucketed by in-pack position."""
    curves = {}
    for letter in ("B", "C"):
        pos_buckets = defaultdict(lambda: {"n": 0, "exact": 0, "jacc_sum": 0.0})
        for oid in oracle_ids:
            if oid not in pack_maps[letter]:
                continue
            _, pos = pack_maps[letter][oid]
            sa, sx = axes["A"].get(oid), axes[letter].get(oid)
            if sa is None or sx is None:
                continue
            b = pos_buckets[pos]
            b["n"] += 1
            if sa == sx:
                b["exact"] += 1
            b["jacc_sum"] += jaccard(sa, sx)
        curve = []
        for pos in sorted(pos_buckets):
            b = pos_buckets[pos]
            curve.append({
                "position": pos, "n": b["n"],
                "exact_match_rate": b["exact"] / b["n"] if b["n"] else None,
                "mean_jaccard": b["jacc_sum"] / b["n"] if b["n"] else None,
            })
        curves[letter] = curve
    return curves


def tail_decay_check(curves: dict, early_positions=5, max_allowed_drop_pp=10.0) -> dict:
    """Proposed guard from BATCH-8-AB-DRESS-REHEARSAL-SPEC.md sec.5: no
    position bucket's agreement rate may fall more than max_allowed_drop_pp
    percentage points below the average of the first `early_positions`."""
    report = {}
    for letter, curve in curves.items():
        early = [c["exact_match_rate"] for c in curve[:early_positions] if c["exact_match_rate"] is not None]
        if not early:
            report[letter] = {"verdict": "no data"}
            continue
        early_avg = sum(early) / len(early)
        worst = min((c["exact_match_rate"] for c in curve if c["exact_match_rate"] is not None), default=None)
        worst_drop_pp = (early_avg - worst) * 100 if worst is not None else None
        report[letter] = {
            "early_position_avg": early_avg,
            "worst_position_rate": worst,
            "worst_drop_pp": worst_drop_pp,
            "verdict": ("PASS" if worst_drop_pp is not None and worst_drop_pp <= max_allowed_drop_pp
                        else "FAIL" if worst_drop_pp is not None else "no data"),
        }
    return report


def main():
    oracle_ids = b8._load_batch8_card_set()
    axes, missing = parse_raw_results(b8.RAW_RESULTS_PATH)
    pack_maps = load_pack_position_maps(oracle_ids)

    print("=== coverage ===")
    for arm in ARMS:
        n = len(axes[arm])
        n_missing = len(missing.get(arm, []))
        print(f"arm {arm}: {n}/{len(oracle_ids)} cards parsed ({n_missing} missing/failed)")
        for oid_or_cid, reason in missing.get(arm, [])[:5]:
            print(f"    MISSING: {oid_or_cid} -- {reason}")

    print("\n=== agreement matrix (all 6 pairs) ===")
    matrix = agreement_matrix(axes, oracle_ids)
    for pair, m in matrix.items():
        print(f"{pair}: exact={m['exact_match_rate']:.1%}  jaccard={m['mean_jaccard']:.3f}  "
              f"n={m['n_compared']}  excluded={m['n_excluded_missing']}")

    print("\n=== tail-position curves (vs Arm A) ===")
    curves = tail_curves(axes, oracle_ids, pack_maps)
    for letter, curve in curves.items():
        print(f"arm {letter}:")
        for c in curve:
            print(f"    pos {c['position']:>2}: exact={c['exact_match_rate']:.1%}  "
                  f"jaccard={c['mean_jaccard']:.3f}  n={c['n']}")

    print("\n=== tail-decay acceptance check (proposed guard: <=10pp drop from early-position avg) ===")
    decay = tail_decay_check(curves)
    for letter, d in decay.items():
        print(f"arm {letter}: {d}")

    fc.write_json(b8.DIFF_REPORT_PATH, {
        "coverage": {a: {"n_parsed": len(axes[a]), "n_missing": len(missing.get(a, []))} for a in ARMS},
        "missing": {a: missing.get(a, []) for a in ARMS},
        "agreement_matrix": matrix,
        "tail_curves": curves,
        "tail_decay_check": decay,
    })
    print(f"\nwrote {b8.DIFF_REPORT_PATH}")


if __name__ == "__main__":
    main()
