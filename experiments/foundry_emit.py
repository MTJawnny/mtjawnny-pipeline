#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- emits a review batch for foundry_review.html.

Input: a CONSOLIDATED-AXES file (the output of the bootstrap loop's
"Consolidate (DET + SUP)" step -- clustered axis candidates with per-member
evidence quotes, plus the OTHER lane). That step is Session B's job (it
needs Stage 1B's SYNTH/BULK decomposition results, which this repo does not
have yet as of Session A) -- this script is the fixed downstream half of
that pipeline stage: given consolidated axes, resolve every referenced card
against the live corpus and emit the exact batch-N.json schema
T3-AXIS-FOUNDRY-v3.md specifies for foundry_review.html to load.

Consolidated-axes input schema (this repo's own convention, not from the
spec doc -- the spec only fixes the OUTPUT batch-N.json shape):
{
  "batch": <int>, "codebook_version": "<str>",
  "axes": [{"slug","definition","scope","source","parameterized",
            "members": [{"oracle_id","quote"}]}],
  "other_lane": [{"oracle_id","label","definition","quote"}]
}

Usage:
  python3 experiments/foundry_emit.py --in <consolidated.json> --out experiments/out/foundry/review/batch-N.json
"""
import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

REQUIRED_AXIS_FIELDS = {"slug", "definition", "scope", "source", "parameterized", "members"}
REQUIRED_MEMBER_FIELDS = {"oracle_id", "quote"}
VALID_SOURCES = {"A∩B", "B-only", "A-only", "CAPTAIN"}


def validate_consolidated(data: dict) -> None:
    for key in ("batch", "codebook_version", "axes"):
        if key not in data:
            fc.halt(f"consolidated-axes input missing required key {key!r}")
    for axis in data["axes"]:
        missing = REQUIRED_AXIS_FIELDS - axis.keys()
        if missing:
            fc.halt(f"axis {axis.get('slug', '?')!r} missing fields {missing}")
        if axis["source"] not in VALID_SOURCES:
            fc.halt(f"axis {axis['slug']!r} has unknown source {axis['source']!r} — expected one of {VALID_SOURCES}")
        for member in axis["members"]:
            missing = REQUIRED_MEMBER_FIELDS - member.keys()
            if missing:
                fc.halt(f"axis {axis['slug']!r} member missing fields {missing}: {member}")
    for row in data.get("other_lane", []):
        for key in ("oracle_id", "label", "definition", "quote"):
            if key not in row:
                fc.halt(f"other_lane row missing {key!r}: {row}")


def collect_oracle_ids(data: dict) -> set:
    ids = set()
    for axis in data["axes"]:
        for member in axis["members"]:
            ids.add(member["oracle_id"])
    for row in data.get("other_lane", []):
        ids.add(row["oracle_id"])
    return ids


def emit(consolidated_path: Path, out_path: Path) -> dict:
    with open(consolidated_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    validate_consolidated(data)

    oracle_ids = collect_oracle_ids(data)
    print(f"consolidated input: {len(data['axes'])} axes, {len(data.get('other_lane', []))} other_lane rows, "
          f"{len(oracle_ids)} distinct cards referenced")

    cards, _ = fc.load_corpus()
    unknown = oracle_ids - cards.keys()
    if unknown:
        fc.halt(f"{len(unknown)} oracle_id(s) referenced by the consolidated input are not in the corpus: "
                f"{sorted(unknown)[:10]}{'...' if len(unknown) > 10 else ''}")

    cards_out = {oid: fc.build_review_card_record(cards[oid]) for oid in oracle_ids}

    batch_json = {
        "schema": "foundry-review/1",
        "batch": data["batch"],
        "codebook_version": data["codebook_version"],
        "axes": data["axes"],
        "cards": cards_out,
        "other_lane": data.get("other_lane", []),
    }

    fc.write_json(out_path, batch_json)
    print(f"wrote {out_path}: {len(data['axes'])} axes, {len(cards_out)} cards, {len(batch_json['other_lane'])} other_lane rows")
    return batch_json


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="in_path", required=True, help="consolidated-axes JSON path")
    parser.add_argument("--out", dest="out_path", required=True, help="output batch-N.json path for foundry_review.html")
    args = parser.parse_args()
    emit(Path(args.in_path), Path(args.out_path))


if __name__ == "__main__":
    main()
