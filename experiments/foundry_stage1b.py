#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- Stage 1B: SYNTH open coding via the Anthropic
Message Batches API. Batch 1 was pure free-form (no codebook existed yet):
1-5 axes per card as {label, definition, actor_scope, evidence_quote},
evidence-quote-or-discard enforced by a closed JSON schema (structured
outputs) so every axis the model emits is grounded in a verbatim quote or
the field is simply absent.

Batch 2+ is TWO-LANE: codebook v0.1+ (experiments/out/foundry/codebook.json)
is embedded in the system prompt and the model must first check whether the
card's pattern matches an existing active axis (lane="codebook", label = the
exact existing slug) before free-labeling a novel one (lane="free") -- per
TRIAGE-BATCH-1.md's batch-2 feedback and SUP-TRIAGE-PROTOCOL's standing
"two-lane labeling... free-labeling of novel patterns explicitly encouraged."

Three subcommands:
  prepare       -- builds the per-card requests from batch<N>_assembled.json,
                   samples real token counts via the (free) count_tokens
                   endpoint, prints a full cost estimate against LIVE
                   pricing, writes the request bodies to disk, and HALTS
                   for Captain's go-ahead. Makes no batch-creating call.
  submit        -- reads the prepared requests, submits the batch, records
                   the batch ID under experiments/out/foundry/, writes a
                   completion note. Only run after Captain's explicit
                   go-ahead.
  fetch-results -- polls the recorded batch ID for processing_status, and
                   once ended, streams the raw per-card JSONL results to
                   disk (stage1b_raw_results[_batch<N>].jsonl) verbatim --
                   the exact shape foundry_consolidate.py's
                   load_raw_instances() reads. HALTS (not an error) if the
                   batch hasn't ended yet.

API key: read from env var MTJAWNNY_BATCH_KEY ONLY (never ANTHROPIC_API_KEY,
which must stay unset so Claude Code stays on the subscription plan). The
variable name is the only place the key appears -- never printed, never
written to any file, never logged.

Run (from repo root):
  python3 experiments/foundry_stage1b.py prepare --batch 2
  python3 experiments/foundry_stage1b.py submit --batch 2       # only after go-ahead
  python3 experiments/foundry_stage1b.py fetch-results --batch 2
"""
import sys
import os
import json
import random
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

API_BASE = "https://api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"
API_KEY_ENV_VAR = "MTJAWNNY_BATCH_KEY"

MODEL = "claude-sonnet-5"  # SYNTH = "mid model" (worker-class vocabulary, MASTER-HANDOFF.md §6)
MAX_TOKENS = 1536  # raised from 1024: two-lane responses carry an extra `lane` token plus
                    # occasional codebook-slug labels longer than free-form kebab guesses
SAMPLE_SEED = 20260717
COUNT_TOKENS_SAMPLE_N = 25
CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"


batch_paths = fc.batch_paths  # canonical per-batch filenames now live in foundry_common.py


def load_codebook_reference() -> str:
    """Active axes as a slug+definition reference block for the two-lane
    prompt. Read at runtime (not hardcoded) so every future batch's prompt
    automatically reflects the codebook's current state."""
    if not CODEBOOK_PATH.exists():
        return "(no codebook yet -- this is batch 1, free-form only)"
    cb = json.loads(CODEBOOK_PATH.read_text())
    active = sorted(
        (slug, a["definition"]) for slug, a in cb["axes"].items() if a.get("status") == "active"
    )
    lines = [f"- {slug}: {definition}" for slug, definition in active]
    return "\n".join(lines)


SYSTEM_PROMPT_TEMPLATE = """You are doing functional decomposition for a Magic: The Gathering card-similarity engine's Tier 3 layer -- the "same job, different words" signal.

For the given card, identify 1 to 5 distinct FUNCTIONAL axes its oracle text expresses -- reusable mechanical patterns that OTHER cards, phrased completely differently, could also share (e.g. "restricts when opponents may cast spells", "doubles a triggered ability", "taxes an opponent's action unless they pay", "grants an ability to another permanent").

TWO-LANE LABELING (check codebook fit FIRST, every time):
Below is the current codebook of ratified functional axes. For each pattern you find on this card:
1. Check whether it genuinely matches one of these existing axes' DEFINITION (not just a superficial word overlap). Before assigning lane="codebook", re-read the axis's definition and confirm the quote's effect runs in the SAME DIRECTION as that definition -- a card that does the OPPOSITE of an axis (untaps instead of taps, is countered instead of counters, sets a maximum instead of removing one, destroys a different object class than the one named) is NOT a match even when it shares surface vocabulary with the axis name or definition (batch 3 found 12 exactly this-shaped mismatches: Counterbore filed under "can't be countered" because its own quote is "Counter target spell."; Mishra's Helix filed under "untaps target land" because it taps lands). Also confirm the ABILITY TYPE and OBJECT CLASS match, not just the verb: before assigning an axis whose definition says "activated ability," confirm the card's ability actually has a player-chosen activation cost (a "{{cost}}:" template) -- "Whenever X happens" and "When this enters" are triggered abilities, never activated ones, even when their effect taps or costs a resource. Confirm WHAT gets tapped/targeted/damaged matches the definition's object class (creature vs. artifact vs. land vs. any permanent), and don't confuse an activation cost's own effect on the SOURCE (e.g. "{{T}}:") with the ability's EFFECT on a TARGET (batch 4 found this pattern in 9 of `rule:activated-tap-target-creature`'s 16 members: ETB/attack/Saga triggers mistaken for activated abilities, a source-tap cost mistaken for a target-tap effect, and non-creature objects tapped). If the quote genuinely matches: lane="codebook", label=that axis's EXACT slug (copy it verbatim, including the "rule:" prefix).
2. If it does not genuinely fit any existing axis: lane="free", label=your own new short kebab-case slug candidate (e.g. "restricts-opponent-cast"). Free-labeling novel patterns is explicitly encouraged -- do not force a card into a codebook slug that's a loose or partial match.

=== CURRENT CODEBOOK (active axes) ===
{codebook_reference}
=== END CODEBOOK ===

Evidence and quoting rules (do not violate these -- batch 1 measured real waste from violations):
- Every axis MUST be grounded in a verbatim quote copied EXACTLY from the card's ORACLE TEXT ONLY -- never from the type line, mana cost, or card name. If the pattern isn't stated in the oracle text itself, do not emit the axis.
- Do not paraphrase or summarize the quote; copy the exact substring. If you cannot quote it verbatim from oracle text, do not emit the axis.

What is NOT an axis (kills the patterns batch 1 had to prune by hand):
- A bare printed keyword (Flying, Trample, Haste, Menace, Deathtouch, Lifelink, Vigilance, Ward, Convoke, Exploit, Delve, Affinity, Cascade, etc.) or its parenthetical reminder text is NEVER an axis on its own -- that signal is already owned by the engine's keyword/Tagger layer. Only emit an axis for a keyword-shaped effect when it is GRANTED to something else by a non-keyword mechanism worth its own pattern (e.g. a static ability handing haste to tokens) -- and even then, check the codebook first; several such grants were already ruled engine-redundant and killed (see rule:grants-* absence above -- if you don't see a grants-haste/grants-hexproof/etc axis listed, it's because it was deliberately killed, do not reinvent it).
- Procedural riders and templating boilerplate are not axes: "then shuffle your library", "reveal it", "activate only as a sorcery", generic "any number of targets" phrasing, mana-value threshold restrictions, saga/class chapter counters. These are parameters or riders on some other real axis, not identity of their own.
- Plain mana-production abilities ("{{T}}: Add {{G}}." etc.) -- a different part of the engine already covers that.
- Do NOT propose a "cantrip" axis -- rule:cantrip is a ratified deterministic predicate computed directly from card data, not something SYNTH needs to identify. Definition (refined batch 3): the card must draw a card upon RESOLUTION of the spell -- via the spell's own effect, an ETB, or another immediate means. An activated tap-ability ("{{T}}: Draw a card, then discard a card") does NOT qualify even at low mana value, because summoning sickness can block the ability the turn the permanent enters -- the draw is not guaranteed on resolution.
- Skip trivial or purely flavorful text with no reusable mechanical pattern.

Other fields:
- actor_scope: who or what this axis constrains or benefits -- e.g. "your-stuff", "opponent-stuff", "all-players", "self" (the card's own permanent/spell).
- definition: one plain-English sentence describing the pattern in general terms (not restating this specific card). For lane="codebook" entries this should still describe the pattern in your own words (it is not required to match the codebook's definition text verbatim, though it should agree in substance).
- If the card has zero reusable functional axes (e.g. a vanilla creature, a card that is pure flavor text, a basic land), return an empty axes array. Do not force axes onto a card that doesn't have any.
- Multi-face cards (DFC, split, adventure): consider all faces; quote from whichever face the pattern comes from."""

OUTPUT_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "axes": {
                "type": "array",
                # NOTE: structured-output JSON schemas reject array count
                # constraints ("property 'maxItems' is not supported") --
                # confirmed live, 2026-07-18: this cap caused a 500/500
                # invalid_request_error batch failure before any card was
                # graded (zero cost). The 1-5 axes cap is enforced by the
                # system prompt instruction only; Stage 1B consolidation
                # (Session B) should flag/truncate any response that comes
                # back with more than 5 as a model-compliance check.
                "items": {
                    "type": "object",
                    "properties": {
                        "lane": {"type": "string", "enum": ["codebook", "free"]},
                        "label": {"type": "string"},
                        "definition": {"type": "string"},
                        "actor_scope": {"type": "string"},
                        "evidence_quote": {"type": "string"},
                    },
                    "required": ["lane", "label", "definition", "actor_scope", "evidence_quote"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["axes"],
        "additionalProperties": False,
    },
}


def card_user_content(card: dict) -> str:
    rec = fc.build_review_card_record(card)
    lines = [
        f"Name: {rec['name']}",
        f"Mana cost: {rec['mana_cost'] or '(none)'}",
        f"Type line: {rec['type_line']}",
        f"Layout: {rec['layout']}",
    ]
    if rec["power"] is not None or rec["toughness"] is not None:
        lines.append(f"P/T: {rec['power']}/{rec['toughness']}")
    if rec["loyalty"] is not None:
        lines.append(f"Loyalty: {rec['loyalty']}")
    if rec["keywords"]:
        lines.append(f"Keywords: {', '.join(rec['keywords'])}")
    if rec["faces"]:
        for i, face in enumerate(rec["faces"], 1):
            lines.append(f"\nFace {i}: {face['name']} ({face['mana_cost'] or 'no cost'})")
            lines.append(f"Type: {face['type_line']}")
            lines.append(f"Oracle text:\n{face['oracle_text'] or '(none)'}")
    else:
        lines.append(f"\nOracle text:\n{rec['oracle_text'] or '(none)'}")
    return "\n".join(lines)


def build_request(oracle_id: str, card: dict, system_prompt: str) -> dict:
    return {
        "custom_id": oracle_id,
        "params": {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "thinking": {"type": "disabled"},
            "system": system_prompt,
            "output_config": {"format": OUTPUT_SCHEMA},
            "messages": [{"role": "user", "content": card_user_content(card)}],
        },
    }


def api_key() -> str:
    key = os.environ.get(API_KEY_ENV_VAR)
    if not key:
        fc.halt(f"{API_KEY_ENV_VAR} is not set in the environment. Set it and re-run. "
                 f"(Never use ANTHROPIC_API_KEY here -- that must stay unset so Claude Code stays on the subscription plan.)")
    return key


def api_post(path: str, body: dict, extra_headers: dict = None) -> dict:
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key(),
        "anthropic-version": ANTHROPIC_VERSION,
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(
        API_BASE + path, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        fc.halt(f"POST {path} -> HTTP {e.code}: {detail}")


def api_get(path: str) -> dict:
    headers = {"x-api-key": api_key(), "anthropic-version": ANTHROPIC_VERSION}
    req = urllib.request.Request(API_BASE + path, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        fc.halt(f"GET {path} -> HTTP {e.code}: {detail}")


def api_get_raw_url(url: str) -> bytes:
    """Same auth headers as api_get, but for a full URL (results_url is
    absolute) and returns raw bytes rather than parsing as one JSON object --
    the results endpoint is JSONL (one JSON object per line), not a single
    JSON document."""
    headers = {"x-api-key": api_key(), "anthropic-version": ANTHROPIC_VERSION}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        fc.halt(f"GET {url} -> HTTP {e.code}: {detail}")


# ---------------------------------------------------------------------------
# fetch-results
# ---------------------------------------------------------------------------

def cmd_fetch_results(batch_num: int):
    paths = batch_paths(batch_num)
    batch_record_path, raw_results_path = paths["batch_record"], paths["raw_results"]
    if not batch_record_path.exists():
        fc.halt(f"{batch_record_path} not found -- run `submit --batch {batch_num}` first")
    if raw_results_path.exists():
        fc.halt(f"{raw_results_path} already exists -- refusing to overwrite. Delete it first if you intend to re-fetch.")

    record = json.loads(batch_record_path.read_text())
    batch_id = record["batch_id"]
    print(f"checking status of batch {batch_id} (batch {batch_num})...")
    status = api_get(f"/v1/messages/batches/{batch_id}")
    processing_status = status["processing_status"]
    counts = status.get("request_counts", {})
    print(f"processing_status={processing_status} counts={counts}")

    if processing_status != "ended":
        fc.halt(f"batch {batch_id} has not ended yet (processing_status={processing_status!r}) -- "
                f"try again later, do not poll in a loop from here")

    results_url = status["results_url"]
    print(f"fetching results from {results_url} ...")
    raw = api_get_raw_url(results_url)
    raw_results_path.write_bytes(raw)
    n_lines = raw.decode("utf-8").count("\n")
    print(f"wrote {raw_results_path} ({n_lines} lines, {len(raw):,} bytes)")

    n_errored = counts.get("errored", 0) + counts.get("canceled", 0) + counts.get("expired", 0)
    if n_errored:
        print(f"NOTE: {n_errored} request(s) did not succeed (errored/canceled/expired) -- "
              f"foundry_consolidate.py's load_raw_instances halts loudly if it encounters a "
              f"non-succeeded result type, so this needs Captain's attention before consolidating.")


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def cmd_prepare(batch_num: int):
    paths = batch_paths(batch_num)
    assembled_path, requests_path = paths["assembled"], paths["requests"]
    if not assembled_path.exists():
        fc.halt(f"{assembled_path} not found -- assemble batch {batch_num} first")
    with open(assembled_path, "r", encoding="utf-8") as f:
        assembled = json.load(f)
    oracle_ids = assembled["all_oracle_ids"]
    print(f"Stage 1B prepare: {len(oracle_ids)} cards from {assembled_path.name} (batch {assembled['batch']})")

    cards, _ = fc.load_corpus()
    unknown = [oid for oid in oracle_ids if oid not in cards]
    if unknown:
        fc.halt(f"{len(unknown)} assembled oracle_ids not found in corpus: {unknown[:5]}")

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(codebook_reference=load_codebook_reference())
    print(f"system prompt built ({'two-lane, codebook-aware' if batch_num > 1 else 'free-form (batch 1)'}, "
          f"{len(system_prompt)} chars)")

    requests_out = [build_request(oid, cards[oid], system_prompt) for oid in oracle_ids]
    fc.write_json(requests_path, requests_out)
    print(f"wrote {requests_path} ({len(requests_out)} requests, model={MODEL}, max_tokens={MAX_TOKENS})")

    # Sample real input-token counts via the (free) count_tokens endpoint.
    # No API key needed to get here, but IS needed for this call -- if the
    # key is unset, halt now rather than mid-estimate.
    rng = random.Random(SAMPLE_SEED)
    sample = rng.sample(requests_out, min(COUNT_TOKENS_SAMPLE_N, len(requests_out)))
    print(f"\nsampling real input-token counts for {len(sample)} requests via /v1/messages/count_tokens "
          f"(live measurement, not estimated)...")
    sample_counts = []
    for req in sample:
        p = req["params"]
        result = api_post("/v1/messages/count_tokens", {
            "model": p["model"], "system": p["system"], "messages": p["messages"],
        })
        sample_counts.append(result["input_tokens"])
    avg_input = sum(sample_counts) / len(sample_counts)
    min_input, max_input = min(sample_counts), max(sample_counts)
    print(f"sampled input tokens: min={min_input} max={max_input} avg={avg_input:.0f} "
          f"(n={len(sample_counts)} of {len(requests_out)})")

    total_input_tokens = avg_input * len(requests_out)

    # Output tokens cannot be measured in advance (nothing has been generated
    # yet) -- state the assumption plainly rather than presenting it as measured.
    # Structured-output JSON for 1-5 axes: ~6 tok (lane) + ~15 tok (label) +
    # ~35 tok (definition) + ~6 tok (actor_scope) + ~30 tok (quote, ~20 words)
    # + ~18 tok JSON overhead per axis =~ 110 tok/axis (was 100 pre-two-lane;
    # +10 for the new `lane` field). Assume an average of 2.5 axes/card (many
    # vanilla/simple cards emit 0-1, complex cards emit 3-5) => ~275 output
    # tokens/card average, +50 tok floor for near-empty responses.
    ASSUMED_AVG_AXES_PER_CARD = 2.5
    TOKENS_PER_AXIS_ESTIMATE = 110
    FLOOR_OUTPUT_TOKENS = 50
    avg_output = FLOOR_OUTPUT_TOKENS + ASSUMED_AVG_AXES_PER_CARD * TOKENS_PER_AXIS_ESTIMATE
    total_output_tokens = avg_output * len(requests_out)

    # Live pricing (re-fetched fresh this session, 2026-07-18, from
    # platform.claude.com/docs/en/about-claude/models/overview.md and
    # .../pricing -- unchanged from batch 1's 2026-07-17 fetch, but re-checked
    # rather than reused from memory per house rule): Claude Sonnet 5 =
    # $3/$15 per MTok standard, INTRODUCTORY $2/$10 per MTok through
    # 2026-08-31 (today is within that window). Message Batches API = 50%
    # off whatever the effective per-token price is at billing time
    # (confirmed live from the pricing page's Batch processing table:
    # Sonnet 5 batch = $1/$5 intro, $1.50/$7.50 standard).
    STANDARD_INPUT_PER_MTOK = 3.00
    STANDARD_OUTPUT_PER_MTOK = 15.00
    INTRO_INPUT_PER_MTOK = 2.00
    INTRO_OUTPUT_PER_MTOK = 10.00
    INTRO_EXPIRES = "2026-08-31"
    BATCH_DISCOUNT = 0.5

    def cost(input_tok, output_tok, in_rate, out_rate):
        return (input_tok / 1_000_000) * in_rate + (output_tok / 1_000_000) * out_rate

    intro_batch_cost = cost(total_input_tokens, total_output_tokens,
                             INTRO_INPUT_PER_MTOK * BATCH_DISCOUNT, INTRO_OUTPUT_PER_MTOK * BATCH_DISCOUNT)
    standard_batch_cost = cost(total_input_tokens, total_output_tokens,
                                STANDARD_INPUT_PER_MTOK * BATCH_DISCOUNT, STANDARD_OUTPUT_PER_MTOK * BATCH_DISCOUNT)

    print(f"\n=== Stage 1B batch {batch_num} cost estimate ({MODEL}, Message Batches API, live pricing re-fetched 2026-07-18) ===")
    print(f"requests: {len(requests_out)}")
    print(f"input tokens/request: avg={avg_input:.0f} (measured, n={len(sample_counts)} sample) -> total ~{total_input_tokens:,.0f}")
    print(f"output tokens/request: avg={avg_output:.0f} (ASSUMED: {ASSUMED_AVG_AXES_PER_CARD} axes/card x "
          f"{TOKENS_PER_AXIS_ESTIMATE} tok/axis + {FLOOR_OUTPUT_TOKENS} tok floor -- NOT measured, "
          f"nothing generated yet) -> total ~{total_output_tokens:,.0f}")
    print(f"\npricing: Sonnet 5 standard ${STANDARD_INPUT_PER_MTOK}/${STANDARD_OUTPUT_PER_MTOK} per MTok; "
          f"INTRO ${INTRO_INPUT_PER_MTOK}/${INTRO_OUTPUT_PER_MTOK} per MTok through {INTRO_EXPIRES} (active today); "
          f"Batch API = {int(BATCH_DISCOUNT*100)}% off either")
    print(f"  at INTRO batch rate (${INTRO_INPUT_PER_MTOK*BATCH_DISCOUNT}/${INTRO_OUTPUT_PER_MTOK*BATCH_DISCOUNT} per MTok): ${intro_batch_cost:.3f}")
    print(f"  at STANDARD batch rate (${STANDARD_INPUT_PER_MTOK*BATCH_DISCOUNT}/${STANDARD_OUTPUT_PER_MTOK*BATCH_DISCOUNT} per MTok, if intro pricing has lapsed by submit time): ${standard_batch_cost:.3f}")
    print(f"\nExpect the actual charge close to the INTRO figure (this batch typically completes in under an hour, "
          f"well within the {INTRO_EXPIRES} window).")

    estimate = {
        "schema": "foundry-stage1b-estimate/1",
        "batch": batch_num,
        "model": MODEL,
        "n_requests": len(requests_out),
        "input_tokens_avg_measured": avg_input,
        "input_tokens_total": total_input_tokens,
        "output_tokens_avg_assumed": avg_output,
        "output_tokens_total_assumed": total_output_tokens,
        "cost_usd_intro_batch": round(intro_batch_cost, 4),
        "cost_usd_standard_batch": round(standard_batch_cost, 4),
        "pricing_fetched": "2026-07-18 from platform.claude.com/docs/en/about-claude/models/overview.md and .../pricing",
    }
    fc.write_json(paths["cost_estimate"], estimate)
    print(f"\nwrote {paths['cost_estimate']}")
    print(f"\nHALT: awaiting Captain's go-ahead before submitting the batch. Run "
          f"`python3 experiments/foundry_stage1b.py submit --batch {batch_num}` after approval.")


# ---------------------------------------------------------------------------
# submit
# ---------------------------------------------------------------------------

def cmd_submit(batch_num: int):
    paths = batch_paths(batch_num)
    batch_record_path, requests_path = paths["batch_record"], paths["requests"]
    if batch_record_path.exists():
        fc.halt(f"{batch_record_path} already exists -- a batch was already submitted this session "
                 f"(refusing to double-submit). Delete it first if you intend to resubmit.")
    if not requests_path.exists():
        fc.halt(f"{requests_path} not found -- run `prepare --batch {batch_num}` first")
    with open(requests_path, "r", encoding="utf-8") as f:
        requests_out = json.load(f)

    print(f"submitting batch: {len(requests_out)} requests, model={MODEL}...")
    result = api_post("/v1/messages/batches", {"requests": requests_out})
    batch_id = result["id"]
    print(f"batch created: {batch_id} (processing_status={result.get('processing_status')})")

    record = {
        "schema": "foundry-stage1b-batch/1",
        "batch": batch_num,
        "batch_id": batch_id,
        "model": MODEL,
        "n_requests": len(requests_out),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "processing_status": result.get("processing_status"),
        "raw_response": result,
    }
    fc.write_json(paths["batch_record"], record)
    print(f"wrote {paths['batch_record']}")

    note = f"""# Stage 1B batch {batch_num} completion note ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})

Batch submitted: `{batch_id}`
Model: {MODEL}
Requests: {len(requests_out)}
Status at submission: {result.get('processing_status')}

## What happened
Batch {batch_num} was assembled (hand-picked confirmation/reinforcement
targets + DET stratified random fill) and its Stage 1B SYNTH request set was
prepared with the two-lane (codebook-aware, batch 2+) or free-form (batch 1)
system prompt, then submitted. Session ends here -- no in-context polling.

## What's pending (next session)
1. Poll batch `{batch_id}` for completion (`GET /v1/messages/batches/{{id}}`,
   `processing_status == "ended"`) -- typically under an hour, max 24h.
2. Retrieve results (`GET /v1/messages/batches/{{id}}/results`), parse each
   card's `axes` array (each now carries `lane`: "codebook" or "free").
3. Consolidate (DET + SUP): cluster labels into codebook candidates, compute
   per-axis member counts, attach evidence quotes, SUP spot-checks 30
   fixed-seed assignments against card text.
4. Emit the review batch (`experiments/foundry_emit.py`) into
   `experiments/out/foundry/review/batch-{batch_num}.json` and hand to
   Captain in `experiments/foundry_review.html`.
5. After Captain's decisions come back: reconcile
   (`experiments/foundry_reconcile.py`), diff report, convergence metrics,
   assemble the next batch, repeat per T3-AXIS-FOUNDRY-v3.md's bootstrap loop.

State lives under `experiments/out/foundry/` -- resumable cold, per
MASTER-HANDOFF.md §5.
"""
    paths["completion_note"].write_text(note, encoding="utf-8")
    print(f"wrote {paths['completion_note']}")
    print(f"\nBatch {batch_id} is processing asynchronously -- no polling from here. "
          f"Open a new session once the batch has ended.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_prepare = sub.add_parser("prepare", help="build requests, sample token counts, print cost estimate, HALT")
    p_prepare.add_argument("--batch", type=int, required=True, help="batch number to prepare (reads batch<N>_assembled.json)")
    p_submit = sub.add_parser("submit", help="submit the prepared batch (only after go-ahead)")
    p_submit.add_argument("--batch", type=int, required=True, help="batch number to submit")
    p_fetch = sub.add_parser("fetch-results", help="fetch raw results once the batch has ended")
    p_fetch.add_argument("--batch", type=int, required=True, help="batch number to fetch results for")
    args = parser.parse_args()

    if args.command == "prepare":
        cmd_prepare(args.batch)
    elif args.command == "submit":
        cmd_submit(args.batch)
    elif args.command == "fetch-results":
        cmd_fetch_results(args.batch)


if __name__ == "__main__":
    main()
