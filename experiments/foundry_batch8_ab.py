#!/usr/bin/env python3
"""Batch 8 -- accuracy-first A/B dress rehearsal (Captain directive,
2026-08-01, superseding docs/BATCH-8-AB-DRESS-REHEARSAL-SPEC.md's original
2-arm design). Four arms on the SAME 1,200 gate-passing cards (reused
verbatim from experiments/out/foundry/batch7_assembled.json -- real,
already-vetted gate-passing cards; batch 8 tests HARNESS agreement, not
card selection):

  A -- single-card baseline (foundry_stage1b.build_request, 1,200 requests)
  B -- packed N=20 (foundry_stage1b.build_packed_request, shuffled per
       pack_oracle_ids' standing seeded-shuffle behavior, 60 requests)
  C -- packed N=40 (30 requests)
  D -- packed N=20 REPEAT: byte-identical packs to B (pack_oracle_ids is
       deterministic under its fixed seed), submitted a second time as the
       same-harness variance control -- isolates model sampling variance
       from packing effects when B and D disagree despite identical input.

Full untrimmed OUTPUT_SCHEMA on every arm (the output-trim proposal was
rejected 2026-08-01, docs/OUTPUT-TRIM-PROPOSAL.md).

Subcommands:
  prepare       -- builds all 4 arms' requests, counts EXACT input tokens
                   for every request (count_tokens is free), prints the
                   full cost estimate against the $120 ceiling, HALTS.
  submit        -- submits the combined 1,350-request batch. Only after
                   Captain's go-ahead (already given for batch 8 itself,
                   2026-08-01 -- NOT a license for the full corpus pass).
  fetch-results -- polls and streams raw results once the batch has ended.
  diff          -- builds the agreement matrices (all 6 arm pairs) and the
                   tail-position curves (B, C vs A) once results are in.

Run (from repo root):
  python3 experiments/foundry_batch8_ab.py prepare
  python3 experiments/foundry_batch8_ab.py submit        # only after go-ahead
  python3 experiments/foundry_batch8_ab.py fetch-results
  python3 experiments/foundry_batch8_ab.py diff
"""
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_stage1b as s1b  # noqa: E402

OUT_DIR = fc.FOUNDRY_OUT_DIR
REQUESTS_PATH = OUT_DIR / "batch8_ab_requests.json"
COST_ESTIMATE_PATH = OUT_DIR / "batch8_ab_cost_estimate.json"
BATCH_RECORD_PATH = OUT_DIR / "batch8_ab_batch_record.json"
RAW_RESULTS_PATH = OUT_DIR / "batch8_ab_raw_results.jsonl"
DIFF_REPORT_PATH = OUT_DIR / "batch8_ab_diff_report.json"

BUDGET_CEILING_USD = 120.00
PACK_SIZES = {"B": 20, "C": 40}

# Live pricing, re-fetched 2026-07-31 (platform.claude.com/docs/en/about-claude/pricing) --
# unchanged from the 2026-07-30 fetch, re-verified per house rule, not reused from memory.
INTRO_INPUT_PER_MTOK, INTRO_OUTPUT_PER_MTOK = 2.00, 10.00
STANDARD_INPUT_PER_MTOK, STANDARD_OUTPUT_PER_MTOK = 3.00, 15.00
BATCH_DISCOUNT = 0.5
INTRO_EXPIRES = "2026-08-31"

# Real batch-6/7-derived output-token model (docs/OUTPUT-TRIM-PROPOSAL.md sec.1) --
# full untrimmed schema, no trim anywhere in batch 8.
AVG_AXES_PER_CARD = 1.7325
CODEBOOK_LANE_FRACTION = 0.342
CODEBOOK_AXIS_CHARS_FULL = 286.2
NONCODEBOOK_AXIS_CHARS = 356.1
CHARS_PER_TOKEN = 4.0
PACKED_JSON_KEY_WRAPPER_CHARS = 45  # oracle_id key + quotes/colon/braces overhead per card


def _load_batch8_card_set() -> list:
    d = json.loads((OUT_DIR / "batch7_assembled.json").read_text())
    ids = d["all_oracle_ids"]
    if len(ids) != 1200 or len(set(ids)) != 1200:
        fc.halt(f"batch7_assembled.json's all_oracle_ids is not exactly 1,200 unique ids "
                 f"(got {len(ids)} total, {len(set(ids))} unique) -- refusing to guess a card set")
    return ids


def _out_tokens_per_card(packed: bool) -> float:
    codebook_axes = AVG_AXES_PER_CARD * CODEBOOK_LANE_FRACTION
    noncodebook_axes = AVG_AXES_PER_CARD * (1 - CODEBOOK_LANE_FRACTION)
    chars = codebook_axes * CODEBOOK_AXIS_CHARS_FULL + noncodebook_axes * NONCODEBOOK_AXIS_CHARS
    if packed:
        chars += PACKED_JSON_KEY_WRAPPER_CHARS
    return chars / CHARS_PER_TOKEN


def build_all_arms(cards: dict, oracle_ids: list) -> dict:
    """Returns {arm_letter: [request, ...]}."""
    single_prompt = s1b.SYSTEM_PROMPT_TEMPLATE.format(
        codebook_reference=s1b.load_codebook_reference(),
        ratified_grammars_reference=s1b.load_ratified_grammars_reference(),
        recently_killed_reference=s1b.load_recently_killed_reference(),
    )
    packed_prompt_20 = s1b.build_packed_system_prompt(PACK_SIZES["B"])
    packed_prompt_40 = s1b.build_packed_system_prompt(PACK_SIZES["C"])

    arm_a = []
    for oid in oracle_ids:
        req = s1b.build_request(oid, cards[oid], single_prompt)
        req["custom_id"] = f"A-{oid}"
        arm_a.append(req)

    packs_20 = s1b.pack_oracle_ids(oracle_ids, PACK_SIZES["B"])
    arm_b = []
    for i, pack in enumerate(packs_20):
        req = s1b.build_packed_request(f"B-pack{i}", pack, cards, packed_prompt_20)
        arm_b.append(req)

    packs_40 = s1b.pack_oracle_ids(oracle_ids, PACK_SIZES["C"])
    arm_c = []
    for i, pack in enumerate(packs_40):
        req = s1b.build_packed_request(f"C-pack{i}", pack, cards, packed_prompt_40)
        arm_c.append(req)

    # Arm D: byte-identical packs to B (pack_oracle_ids is deterministic
    # under PACK_SHUFFLE_SEED) -- same-harness repeat, different custom_id.
    arm_d = []
    for i, pack in enumerate(packs_20):
        req = s1b.build_packed_request(f"D-pack{i}", pack, cards, packed_prompt_20)
        arm_d.append(req)

    # Sanity: B and D must be byte-identical except custom_id (verifies the
    # "identical inputs" repeat-arm requirement mechanically, not by assertion).
    for rb, rd in zip(arm_b, arm_d):
        b_params, d_params = json.dumps(rb["params"], sort_keys=True), json.dumps(rd["params"], sort_keys=True)
        if b_params != d_params:
            fc.halt("Arm D is not byte-identical to Arm B (excluding custom_id) -- "
                     "the same-harness repeat control is broken, refusing to proceed")

    return {"A": arm_a, "B": arm_b, "C": arm_c, "D": arm_d}


def cmd_prepare():
    cards, _, gated_out = fc.load_corpus_gated()
    oracle_ids = _load_batch8_card_set()
    missing = [oid for oid in oracle_ids if oid not in cards]
    if missing:
        fc.halt(f"{len(missing)} batch-8 oracle_ids not found in the gated corpus "
                 f"(gate criteria may have changed since batch 7 was assembled): {missing[:5]}")

    print(f"batch 8 card set: {len(oracle_ids)} cards (reused from batch7_assembled.json, "
          f"all confirmed still gate-passing)")

    arms = build_all_arms(cards, oracle_ids)
    for letter, reqs in arms.items():
        print(f"arm {letter}: {len(reqs)} requests")

    print("\ncounting EXACT input tokens for all requests (count_tokens is free, no spend) ...")
    per_arm_input_tokens = {}
    per_arm_counts = defaultdict(list)
    total_requests = sum(len(v) for v in arms.values())
    done = 0
    for letter, reqs in arms.items():
        total = 0
        for req in reqs:
            p = req["params"]
            result = s1b.api_post("/v1/messages/count_tokens", {
                "model": p["model"], "system": p["system"], "messages": p["messages"],
            })
            total += result["input_tokens"]
            per_arm_counts[letter].append(result["input_tokens"])
            done += 1
            if done % 100 == 0:
                print(f"  ...{done}/{total_requests} requests counted")
        per_arm_input_tokens[letter] = total
        print(f"arm {letter}: {total:,} total input tokens ({total/len(reqs):,.0f} avg/request)")

    n_cards = len(oracle_ids)
    out_single = _out_tokens_per_card(packed=False)
    out_packed = _out_tokens_per_card(packed=True)
    per_arm_output_tokens = {
        "A": n_cards * out_single,
        "B": n_cards * out_packed,
        "C": n_cards * out_packed,
        "D": n_cards * out_packed,
    }

    def cost(inp, out, in_rate, out_rate):
        return (inp / 1_000_000) * in_rate + (out / 1_000_000) * out_rate

    total_input = sum(per_arm_input_tokens.values())
    total_output = sum(per_arm_output_tokens.values())
    intro_total = cost(total_input, total_output, INTRO_INPUT_PER_MTOK * BATCH_DISCOUNT, INTRO_OUTPUT_PER_MTOK * BATCH_DISCOUNT)
    standard_total = cost(total_input, total_output, STANDARD_INPUT_PER_MTOK * BATCH_DISCOUNT, STANDARD_OUTPUT_PER_MTOK * BATCH_DISCOUNT)

    print(f"\n=== Batch 8 A/B cost estimate (live pricing, intro through {INTRO_EXPIRES}) ===")
    print(f"total requests: {total_requests}")
    print(f"total input tokens (EXACT, measured): {total_input:,}")
    print(f"total output tokens (estimated, real batch-6/7-derived model): {total_output:,.0f}")
    for letter in "ABCD":
        arm_intro = cost(per_arm_input_tokens[letter], per_arm_output_tokens[letter],
                          INTRO_INPUT_PER_MTOK * BATCH_DISCOUNT, INTRO_OUTPUT_PER_MTOK * BATCH_DISCOUNT)
        print(f"  arm {letter}: input={per_arm_input_tokens[letter]:,}  "
              f"output={per_arm_output_tokens[letter]:,.0f}  intro_cost=${arm_intro:.2f}")
    print(f"\nINTRO batch total: ${intro_total:.2f}")
    print(f"STANDARD batch total (if intro has lapsed by submit time): ${standard_total:.2f}")
    print(f"Budget ceiling: ${BUDGET_CEILING_USD:.2f}")

    if intro_total > BUDGET_CEILING_USD:
        fc.halt(f"intro-rate estimate ${intro_total:.2f} EXCEEDS the ${BUDGET_CEILING_USD:.2f} ceiling -- "
                 f"halting, does not write requests, refusing to proceed without a revised plan")
    print(f"\nWithin ceiling (${intro_total:.2f} < ${BUDGET_CEILING_USD:.2f}). Writing requests...")

    combined = arms["A"] + arms["B"] + arms["C"] + arms["D"]
    fc.write_json(REQUESTS_PATH, combined)
    print(f"wrote {REQUESTS_PATH} ({len(combined)} requests)")

    estimate = {
        "schema": "foundry-batch8-ab-estimate/1",
        "n_cards": n_cards,
        "per_arm_requests": {k: len(v) for k, v in arms.items()},
        "per_arm_input_tokens_exact": per_arm_input_tokens,
        "per_arm_output_tokens_estimated": per_arm_output_tokens,
        "total_input_tokens": total_input,
        "total_output_tokens_estimated": total_output,
        "cost_usd_intro_batch": round(intro_total, 4),
        "cost_usd_standard_batch": round(standard_total, 4),
        "budget_ceiling_usd": BUDGET_CEILING_USD,
        "pricing_fetched": "2026-07-31 via WebFetch against platform.claude.com/docs/en/about-claude/pricing",
    }
    fc.write_json(COST_ESTIMATE_PATH, estimate)
    print(f"wrote {COST_ESTIMATE_PATH}")
    print(f"\nHALT: awaiting Captain's go-ahead before submitting. Run "
          f"`python3 experiments/foundry_batch8_ab.py submit` after approval.")


def cmd_submit():
    if BATCH_RECORD_PATH.exists():
        fc.halt(f"{BATCH_RECORD_PATH} already exists -- a batch was already submitted "
                 f"(refusing to double-submit). Delete it first if you intend to resubmit.")
    if not REQUESTS_PATH.exists():
        fc.halt(f"{REQUESTS_PATH} not found -- run `prepare` first")
    if not COST_ESTIMATE_PATH.exists():
        fc.halt(f"{COST_ESTIMATE_PATH} not found -- run `prepare` first (need the ceiling check on record)")
    estimate = json.loads(COST_ESTIMATE_PATH.read_text())
    if estimate["cost_usd_intro_batch"] > BUDGET_CEILING_USD:
        fc.halt(f"recorded estimate ${estimate['cost_usd_intro_batch']:.2f} exceeds the "
                 f"${BUDGET_CEILING_USD:.2f} ceiling -- refusing to submit")

    requests_out = json.loads(REQUESTS_PATH.read_text())
    print(f"submitting batch 8 A/B: {len(requests_out)} requests "
          f"(estimate: ${estimate['cost_usd_intro_batch']:.2f} intro / "
          f"${estimate['cost_usd_standard_batch']:.2f} standard, ceiling ${BUDGET_CEILING_USD:.2f})...")
    result = s1b.api_post("/v1/messages/batches", {"requests": requests_out})
    batch_id = result["id"]
    print(f"batch created: {batch_id} (processing_status={result.get('processing_status')})")

    record = {
        "schema": "foundry-batch8-ab-batch/1",
        "batch_id": batch_id,
        "model": s1b.MODEL,
        "n_requests": len(requests_out),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "processing_status": result.get("processing_status"),
        "cost_estimate": estimate,
    }
    fc.write_json(BATCH_RECORD_PATH, record)
    print(f"wrote {BATCH_RECORD_PATH}")
    print(f"\nBatch {batch_id} is processing asynchronously. Run "
          f"`python3 experiments/foundry_batch8_ab.py fetch-results` once it has ended.")


def cmd_fetch_results():
    if not BATCH_RECORD_PATH.exists():
        fc.halt(f"{BATCH_RECORD_PATH} not found -- run `submit` first")
    if RAW_RESULTS_PATH.exists():
        fc.halt(f"{RAW_RESULTS_PATH} already exists -- refusing to overwrite")

    record = json.loads(BATCH_RECORD_PATH.read_text())
    batch_id = record["batch_id"]
    print(f"checking status of batch {batch_id}...")
    status = s1b.api_get(f"/v1/messages/batches/{batch_id}")
    processing_status = status["processing_status"]
    counts = status.get("request_counts", {})
    print(f"processing_status={processing_status} counts={counts}")

    if processing_status != "ended":
        fc.halt(f"batch {batch_id} has not ended yet (processing_status={processing_status!r}) -- "
                 f"try again later, do not poll in a loop from here")

    results_url = status["results_url"]
    print(f"fetching results from {results_url}...")
    raw = s1b.api_get_raw_url(results_url)
    RAW_RESULTS_PATH.write_bytes(raw)
    n_lines = raw.decode("utf-8").count("\n")
    print(f"wrote {RAW_RESULTS_PATH} ({n_lines} lines, {len(raw):,} bytes)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    sub.add_parser("submit")
    sub.add_parser("fetch-results")
    args = parser.parse_args()

    if args.command == "prepare":
        cmd_prepare()
    elif args.command == "submit":
        cmd_submit()
    elif args.command == "fetch-results":
        cmd_fetch_results()


if __name__ == "__main__":
    main()
