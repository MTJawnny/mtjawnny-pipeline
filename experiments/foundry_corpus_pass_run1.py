#!/usr/bin/env python3
"""CORPUS-PASS-PLAN.md step 6: full-corpus SYNTH pass, run 1 -- executed per
Captain's 2026-08-01 execution trigger (M=1, this run only; corroboration
wave 2/M=2 consensus is a FUTURE trigger, NOT authorized here). Packed
architecture (foundry_stage1b.py's build_packed_request family), N=40,
intro Batch API rate, full untrimmed schema (the output-trim proposal
stays rejected). Runs against the full Gate #0-filtered corpus (32,557
cards as of the post-DET-pass codebook.json), post-DET-pass (the 39
DET-owned axes are already stripped from the embedded codebook reference
via foundry_stage1b.load_det_owned_slugs(), reading docs/det-patterns-v2.json).

Distinct from foundry_stage1b.py's per-triage-batch prepare/submit (that
workflow is for the OLD single-card hand-picked-batch loop, batch1-8) --
this is the one-time full-corpus packed run, its own paths under
experiments/out/foundry/corpus_pass_run1_*.

Preconditions already satisfied before this script's submit was run
(2026-08-01 session):
  - DET pass applied (foundry_det_pass.py apply), zero-spend, all 39
    patterns passed their sample-sheet gate (docs/det-patterns-v2.json).
  - Packed N=40 schema pre-flighted (one live dry-run call, confirmed no
    "compiled grammar too large" regression, all 40 oracle_ids returned
    correctly) -- experiments/out/foundry/preflight_n40_result.json.
  - Live-priced estimate computed and the $140 emergency-arc-ceiling gate
    passed ($87.93 projected cumulative <= $140) -- logged in
    docs/CORPUS-PASS-PLAN.md's EMERGENCY COST STOP section.

Run:
  python3 experiments/foundry_corpus_pass_run1.py prepare
  python3 experiments/foundry_corpus_pass_run1.py submit    # only after go-ahead
  python3 experiments/foundry_corpus_pass_run1.py fetch-results
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_stage1b as s1b  # noqa: E402

PACK_SIZE = 40

REQUESTS_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_requests.json"
BATCH_RECORD_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_batch.json"
RAW_RESULTS_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_raw_results.jsonl"
COMPLETION_NOTE_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_completion_note.md"


def cmd_prepare():
    cards, _, gated_out = fc.load_corpus_gated()
    oracle_ids = sorted(cards.keys())
    print(f"corpus: {len(cards)} gate-passing cards ({gated_out} gated out)")

    packs = s1b.pack_oracle_ids(oracle_ids, PACK_SIZE)
    print(f"packed into {len(packs)} packs at N={PACK_SIZE} (shuffle seed {s1b.PACK_SHUFFLE_SEED})")

    system_prompt = s1b.build_packed_system_prompt(PACK_SIZE)
    print(f"packed system prompt built ({len(system_prompt)} chars, shared byte-identical across all packs)")

    requests_out = [
        s1b.build_packed_request(f"corpus-pass-1-pack-{i:04d}", pack, cards, system_prompt)
        for i, pack in enumerate(packs)
    ]
    fc.write_json(REQUESTS_PATH, requests_out)
    print(f"wrote {REQUESTS_PATH} ({len(requests_out)} pack-requests, {len(oracle_ids)} total cards)")
    print(f"\nHALT: awaiting Captain's go-ahead before submitting. Run "
          f"`python3 experiments/foundry_corpus_pass_run1.py submit` after approval.")


def cmd_submit():
    if BATCH_RECORD_PATH.exists():
        fc.halt(f"{BATCH_RECORD_PATH} already exists -- a batch was already submitted "
                 f"(refusing to double-submit). Delete it first if you intend to resubmit.")
    if not REQUESTS_PATH.exists():
        fc.halt(f"{REQUESTS_PATH} not found -- run `prepare` first")
    with open(REQUESTS_PATH, "r", encoding="utf-8") as f:
        requests_out = json.load(f)

    n_cards = sum(len(r["params"]["messages"][0]["content"].split("=== Card ")) - 1 for r in requests_out)
    print(f"submitting corpus-pass run 1: {len(requests_out)} pack-requests (~{n_cards} cards), model={s1b.MODEL}...")
    result = s1b.api_post("/v1/messages/batches", {"requests": requests_out})
    batch_id = result["id"]
    print(f"batch created: {batch_id} (processing_status={result.get('processing_status')})")

    record = {
        "schema": "foundry-corpus-pass-run1-batch/1",
        "run": 1,
        "batch_id": batch_id,
        "model": s1b.MODEL,
        "pack_size": PACK_SIZE,
        "n_pack_requests": len(requests_out),
        "n_cards_approx": n_cards,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "processing_status": result.get("processing_status"),
        "live_priced_estimate_usd": 55.05,
        "cost_estimate_note": "docs/CORPUS-PASS-PLAN.md EMERGENCY COST STOP section, "
                               "2026-08-01 full-corpus run-1 gate check",
        "raw_response": result,
    }
    fc.write_json(BATCH_RECORD_PATH, record)
    print(f"wrote {BATCH_RECORD_PATH}")
    return batch_id, result


def cmd_fetch_results():
    if not BATCH_RECORD_PATH.exists():
        fc.halt(f"{BATCH_RECORD_PATH} not found -- run `submit` first")
    if RAW_RESULTS_PATH.exists():
        fc.halt(f"{RAW_RESULTS_PATH} already exists -- refusing to overwrite. Delete it first if you intend to re-fetch.")

    record = json.loads(BATCH_RECORD_PATH.read_text())
    batch_id = record["batch_id"]
    print(f"checking status of batch {batch_id} (corpus-pass run 1)...")
    status = s1b.api_get(f"/v1/messages/batches/{batch_id}")
    processing_status = status["processing_status"]
    counts = status.get("request_counts", {})
    print(f"processing_status={processing_status} counts={counts}")

    if processing_status != "ended":
        fc.halt(f"batch {batch_id} has not ended yet (processing_status={processing_status!r}) -- "
                f"try again later, do not poll in a loop from here")

    results_url = status["results_url"]
    print(f"fetching results from {results_url} ...")
    raw = s1b.api_get_raw_url(results_url)
    RAW_RESULTS_PATH.write_bytes(raw)
    n_lines = raw.decode("utf-8").count("\n")
    print(f"wrote {RAW_RESULTS_PATH} ({n_lines} lines, {len(raw):,} bytes)")

    n_errored = counts.get("errored", 0) + counts.get("canceled", 0) + counts.get("expired", 0)
    if n_errored:
        print(f"NOTE: {n_errored} pack-request(s) did not succeed (errored/canceled/expired) -- "
              f"needs Captain's attention before consolidating.")


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
