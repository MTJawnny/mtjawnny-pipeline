# MTJawnny Backend — Phase 2 Implementation Plan

*The build plan. Architecture: Option A from BACKEND-RESEARCH-FINDINGS.md (static artifacts + GitHub Actions pipeline + R2, no server). Locked decisions: PNG print-quality images, one per card (backfilled 2026-07-03: 36,155 files, 50.53GB, ~$0.76/mo — see PHASE-2-COMPLETION.md); no EDHREC scraping for now (pluggable slot reserved; `edhrec_rank` from Scryfall bulk covers popularity); deck finisher runs fully client-side.*

**Naming & handoff decisions (locked this session — read before Phases 1–3):**
- **Image storage is keyed by `oracle_id`, never by slug.** Objects live at `/cards/png/<oracle_id>.png`. Double-faced cards: `/cards/png/<oracle_id>-front.png` and `/cards/png/<oracle_id>-back.png`. Single-faced cards have no suffix. This convention is frozen — never change it.
- **Slug is an HTML filename only.** It names the `.html` card page (`pris.html`) and has nothing to do with image storage. There is no slug→image coupling and no hand-maintained `slug-map.json`.
- **One image format: PNG.** Scryfall's `image_uris.png` (745×1040, print-quality, transparent rounded corners) is the only image we store. No jpg cohort, no mixed extensions.
- **The existing site jpgs are NOT migrated ahead of Phase 2.** The 12 legacy card pages keep their working same-origin `/cardimages/<slug>.jpg` until the Phase 2 backfill produces the full oracle_id PNG corpus, at which point every page (legacy + new) is repointed uniformly. This means the old standalone "Phase 1 media migration" dissolves into Phase 2 — see Phase 1 note.
- **Two-CDN image fallback (no repo weight).** Pages reference primary = R2 `cdn.mtjawnny.com`, fallback = Scryfall's own image CDN. Both offsite. A broken image requires both R2 and Scryfall down at once. No same-origin repo copy is needed for new cards.
- **The resolver (Phase 3 component) is the safety layer.** Captain's entire authoring surface is a two-field list: `name | slug`. A pipeline resolver tool enriches it to `name | slug | oracle_id | image_url | scryfall_fallback_url | is_dfc` by exact-matching names against Scryfall bulk data. Agents build pages from the *resolved* manifest and never fuzzy-match names or guess oracle_ids themselves. The resolver halts loudly on any ambiguity rather than guessing. Activates once Phase 2/3 data exists.
- **Session ops corrections (verified live at end of Phase 0):** rclone uploads must use `-M --metadata-set "cache-control=..."` (the plan's original `--header-upload` silently does NOT stick the header on R2); the remote needs `no_check_bucket = true` because the bucket-scoped token can't run rclone's default CreateBucket precheck.

**Running cost when everything below is live: ~$0.76/month.** (R2 storage for 50.53GB of PNGs, measured post-backfill. Literally everything else — pipeline compute, data artifacts, bandwidth, reads — rides free tiers with zero egress.)

---

## Architecture at a glance

```
Scryfall bulk (JSONL, weekly)          repo: tags/ (your custom layer)
        │                                       │
        └────────────┬──────────────────────────┘
                     ▼
        GitHub Actions pipeline (free, weekly cron + manual)
        fetch → trim → merge tags → embed (incremental) →
        neighbors → build SQLite + shards + finisher artifacts →
        validate → upload versioned → flip latest.json
                     │
                     ▼
        R2 bucket behind cdn.mtjawnny.com  (zero egress)
        /cards/png/<oracle_id>.png   /data/v/<date>/…   /data/latest.json
                     │
                     ▼
        mtjawnny.com static tools (unchanged GitHub Pages)
        thesaurus · similar-cards · deck finisher (client-side)
        image fallback: R2 → Scryfall image CDN (both offsite)

AUTHORING LANE (card-page creation, runs on top of the corpus above):
        Captain writes a list:  name | slug
                     ▼
        Resolver tool (Phase 3): exact-match name → oracle_id,
        detect DFC, verify image in R2, check slug not already taken →
        emits resolved manifest (name|slug|oracle_id|image_url|fallback|is_dfc);
        HALTS LOUDLY on any ambiguity, never guesses
                     ▼
        Agent(s) build card pages from the resolved manifest
        (zero name-matching in the agent = zero creative errors)
                     ▼
        Captain visual-audits the pages → says ship → commit
```

Nothing runs at request time. If R2 is unreachable, corpus tools show a friendly error and every existing tool behaves exactly as it does today.

---

## Phase 0 — Foundation (one evening)

**0.1 — Enable R2.** Cloudflare dashboard → R2. Requires adding a credit card even for free tier; you won't be charged until you exceed free limits (you will — by ~53¢). While in billing, set a **notification/budget alert at $5** so any surprise is loud.

**0.2 — Create one bucket:** `mtjawnny`. One bucket, prefixes instead of multiple buckets — simpler tokens, simpler CORS, one custom domain:
- `/cards/png/` — card images
- `/data/` — pipeline artifacts
- `/art/` — your custom MS Paint art, helper tokens, mana-symbol SVGs

**0.3 — Custom domain.** Bucket → Settings → Custom Domains → `cdn.mtjawnny.com`. Since DNS is already on Cloudflare this is one click; it also puts the bucket behind Cloudflare's edge cache (r2.dev URLs don't get that, and are rate-limited — never ship r2.dev URLs).

**0.4 — CORS policy** on the bucket (Settings → CORS):
```json
[{
  "AllowedOrigins": ["https://mtjawnny.com", "https://www.mtjawnny.com", "http://localhost:8000"],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedHeaders": ["range"],
  "ExposeHeaders": ["content-length", "content-range", "etag"],
  "MaxAgeSeconds": 86400
}]
```
The `range` header allowance matters — it's what lets sql.js-httpvfs work cross-origin later.

**0.5 — Cache rule.** Cloudflare dashboard → your zone → Cache Rules: for hostname `cdn.mtjawnny.com`, set Edge TTL to respect origin headers. The pipeline and sync scripts will set headers per-object: images and versioned artifacts get `public, max-age=31536000, immutable`; `latest.json` gets `public, max-age=300`. Immutable + versioned paths is what makes rollback trivial and cache-busting a non-issue.

**0.6 — API token.** R2 → Manage API Tokens → create token scoped to **object read & write on the `mtjawnny` bucket only**. Save Access Key ID + Secret. Add to the pipeline repo (Phase 3) as GitHub Actions secrets: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`.

**0.7 — Local rclone** on the MacBook (primary dev machine) for the initial backfill and manual ops. rclone is not yet in `setup-mtjawnny-mac.sh` — add `brew install rclone` to the script when installing:
```
brew install rclone
rclone config  →  type: s3, provider: Cloudflare,
endpoint: https://<account-id>.r2.cloudflarestorage.com
```
`rclone config` is interactive — answer prompts one at a time; never paste multi-line blocks into it (known zsh/prompt gotcha from the Mac setup doc). Smoke test: `rclone lsd r2:mtjawnny` (empty output, no error = success — note `rclone lsd r2:` alone will 403, because the bucket-scoped token can't list all buckets; that's correct).

**Then make `no_check_bucket` permanent** so uploads don't 403 on rclone's default CreateBucket precheck (the bucket-scoped token can't create buckets, by design):
```
rclone config update r2 no_check_bucket true
```

**Done when:** `https://cdn.mtjawnny.com/` resolves, a hand-uploaded test file serves with correct headers, and a `fetch()` from a local page succeeds under CORS.

---

## Phase 1 — Superseded: dissolved into Phase 2 (read this — the roadmap changed)

**Why this phase no longer stands alone.** Phase 1 was originally "sync the existing site jpgs to R2 ahead of the pipeline, so the repo stops growing immediately." The one-lane decisions locked this session (PNG only, `oracle_id`-keyed storage, no jpg cohort) remove the thing Phase 1 was migrating. Syncing slug-named jpgs into an oracle_id-named PNG bucket would create exactly the orphan/duplicate mess we chose to avoid. So there is nothing to migrate ahead of Phase 2 — **the migration IS Phase 2's unified cutover.**

**Why this loses nothing.** Phase 1's only independent value was early repo-size relief. But mass card creation depends on the resolver + R2 corpus, which don't exist until Phase 2/3 — so the repo physically cannot balloon before Phase 2. The 12 legacy jpgs are a rounding error until then. Deferring the migration costs zero and buys a clean single cutover.

**What actually happens instead (all inside Phase 2's cutover):**
- The 12 legacy card pages keep working untouched on same-origin `/cardimages/<slug>.jpg` until Phase 2 lands their oracle_id PNGs.
- At Phase 2 cutover, every card page (legacy + new) is repointed to the oracle_id PNG URL via the shared image helper below, one page at a time in Claude Code, merged with the in-flight report-button/Tally rollout (per-page edit + validation ritual + commit; `pris.html` first as the template). The per-page discipline is kept because the repo audit found pages may have drifted.
- **Mana symbols** stay a straightforward prefix concern and can be handled at cutover too: canonical `https://cdn.mtjawnny.com/art/manasymbols/<SYM>.svg`, with repo `/manasymbols/` remaining as-is (they're small UI chrome; no urgency to move them).
- Legacy `/cardimages/` jpgs are pruned ~1 month after cutover; UI chrome (logo SVGs, CSS, fonts) stays in the repo permanently.

**The shared image helper (built at cutover, used by every card page — legacy and agent-authored):**
```js
const CDN = "https://cdn.mtjawnny.com";
// oracle_id-keyed, PNG-only, Scryfall fallback. `face` is "" | "-front" | "-back".
function cardImg(el, oracleId, scryfallUrl, face = "") {
  el.src = `${CDN}/cards/png/${oracleId}${face}.png`;
  el.onerror = () => { el.onerror = null; el.src = scryfallUrl; }; // Scryfall CDN fallback
}
```
Both the oracle_id and the Scryfall fallback URL are supplied by the resolver at page-build time, so the agent hardcodes correct values and the helper stays dumb. A broken image needs R2 **and** Scryfall down simultaneously.

**Update `CLAUDE.md` at cutover** with the image contract (oracle_id-keyed PNG, DFC face suffixes, Scryfall fallback, never r2.dev, `/cardimages/` is legacy-only) — otherwise future Claude Code sessions write stale same-origin paths.

**QR-proxy end-to-end test** still happens at cutover: print a sheet, scan a QR on mobile data, confirm the landing page renders its image from the CDN.

---

## Phase 2 — Full PNG image corpus — BACKFILL DONE 2026-07-03 (36,155 files / 50.53GB; per-page cutover + weekly upkeep still open — see PHASE-2-COMPLETION.md)

**2.1 — The source of truth for "which images":** the Oracle Cards bulk file (Phase 3 fetches it anyway; for the backfill, download it once manually). Each card's `image_uris.png` is the 745×1040 print-quality PNG. **DFC convention (locked):** for double-faced cards use `card_faces[i].image_uris.png`, stored as `<oracle_id>-front.png` (face 0) and `<oracle_id>-back.png` (face 1). Single-faced cards are `<oracle_id>.png`. Two-image detection is by WHERE `image_uris` lives, never by `card_faces` presence: split/flip/adventure cards HAVE `card_faces` but carry ONE root-level image. Rule: `card_faces[0].image_uris` exists → front/back pair; otherwise root `image_uris` → single image. (Verified in the executed backfill.)

**2.2 — Naming: `oracle_id` is the only image key. Slug is HTML-only.** Store objects as `/cards/png/<oracle_id>.png` (+ `-front`/`-back` for DFCs). Oracle IDs are stable across Scryfall renames. **There is no hand-maintained `slug-map.json`** — the slug names the `.html` page and never touches image storage. The resolver (3.x) generates the name↔oracle_id mapping on demand from bulk data, so nothing about images is ever hand-keyed. A page knows its card's oracle_id because the resolver handed it over at build time; that oracle_id is what builds the image URL.

**2.3 — Initial backfill: run it from the MacBook overnight, not from Actions.** ~35K PNGs at ~1MB each doesn't fit a GitHub runner's ~14GB disk without batching gymnastics; locally it's a simple resumable script. Run it under `caffeinate -i` so the Mac doesn't sleep mid-download, and spell out file paths explicitly in the batch/cleanup steps — zsh aborts the entire command line when a wildcard matches nothing. Requirements that keep it polite and compliant with Scryfall's guidance:
- Set a real `User-Agent: MTJawnnyPipeline/1.0 (mtjawnny.com; contact email)` and `Accept` header — Scryfall asks for this and may block anonymous agents.
- **Max ~8 requests/second** (their guidance is ≤10/s; stay under). 35K images ≈ 1.5–2.5 hours of wall time.
- Download in batches of ~500 → `rclone copy` batch to R2 **with the corrected metadata flag** (see below) → delete local → append to a local `synced.txt` checkpoint so it resumes cleanly if interrupted.
- Only images are pulled this way; card *data* always comes from bulk files, never per-card API calls.

**Corrected rclone upload pattern (verified live in Phase 0 — use this everywhere, not `--header-upload`):**
```
rclone copy <batch-dir> r2:mtjawnny/cards/png \
  -M --metadata-set "cache-control=public, max-age=31536000, immutable"
```
`--header-upload "Cache-Control: ..."` silently does NOT persist the header on R2 (object serves with no cache-control → Cloudflare `cf-cache-status: BYPASS` → every read hits R2). `-M --metadata-set "cache-control=..."` is the pattern that actually sticks. Getting this wrong on a 35K-image run turns "free reads forever" into millions of Class B operations, so it matters most exactly here. (The remote also needs `no_check_bucket = true` — set once in Phase 0, see 0.7 — or every upload 403s on the CreateBucket precheck.)

**2.4 — Incremental image sync (the weekly upkeep, runs in Actions).** After the backfill, new/changed images per week are dozens, not thousands — that fits Actions trivially. The pipeline (Phase 3) maintains `/data/image-manifest.json` in R2: `{oracle_id: image_sha_or_updated_at}`. Each run diffs current bulk data (and/or Scryfall's new `/cards/manifest` endpoint, which exists for exactly this) against the manifest, fetches only deltas, updates the manifest. This *is* your manifest-diff plan, promoted to production.

**2.5 — Cost check (measured):** 50.53GB × $0.015 = **~$0.76/mo** storage (avg PNG ≈ 1.4MB, above the 1.1MB estimate). 37.4K Class A writes once (1M/mo free). Reads and egress: free forever. Dashboard verified 2026-07-03.

**Done when:** ✅ every kept card has a PNG in R2 (36,155 objects == worklist, verified), a re-run of the backfill script exits near-immediately, dashboard storage 50.53GB. Still open from this section: `image-manifest.json` + weekly delta sync (2.4) — that belongs to the Phase 3 pipeline build. Snapshot + raw bulk archived at `/data/snapshots/2026-07-03/` (includes Tagger oracle tags with weights/inherited parents); Phase 3's first run can seed from it.

---

## Phase 3 — The data pipeline (jobs 2.2 + 2.3 — the core build; 2–4 evenings)

**3.1 — New public repo: `mtjawnny-pipeline`.** Public = unlimited free Actions minutes. Layout:
```
tags/cards.yaml          ← YOUR custom layer (oracle_id-keyed), the differentiator
pipeline/
  fetch.py  build_db.py  embed.py  neighbors.py
  finisher_artifacts.py  validate.py  upload.py
recipes/embedding.yaml   ← pins model name + input recipe (see 3.4)
.github/workflows/build.yml       (cron: weekly, Mon 06:00 UTC + workflow_dispatch)
.github/workflows/image-sync.yml  (the Phase 2.4 delta job; can be a step in build.yml)
```
No card data is ever committed to git — the repo holds code + your tags only.

**3.2 — Fetch (JSONL from day one — mandatory).**
`GET https://api.scryfall.com/bulk-data` → select `oracle_cards` → follow **`jsonl_download_uri`** → stream-decompress. One card per line; parse line-by-line, never load the whole file. Also fetch the `rulings` bulk file (thesaurus/explainer tools will want rulings eventually; it's small).

**3.3 — Trim + merge.** Keep per card: `oracle_id, name, mana_cost, cmc, type_line, oracle_text, colors, color_identity, keywords, power, toughness, loyalty, produced_mana, legalities (commander at minimum), rarity, set, collector_number, released_at, edhrec_rank, game_changer, prices.usd, scryfall_uri, image status fields`. Two fields to underline: **`edhrec_rank`** (EDHREC popularity, shipped legitimately inside Scryfall bulk — your deck-finisher popularity prior with zero scraping) and **`prices.usd`** (feeds the proxy-deck-cost-calculator from the tool backlog for free). Then merge `tags/cards.yaml` — your roles, archetypes, thesaurus synonyms, anything — as additional columns/JSON. **Reserved slot:** the merge step accepts any extra oracle_id-keyed JSON file; if EDHREC (or anything else) is ever approved, it drops in here with no redesign.

**3.4 — Embeddings (incremental by design).**
- Model: `BAAI/bge-small-en-v1.5` (384-dim, runs fine on the free CPU runner). Pin the exact name in `recipes/embedding.yaml` — switching models later invalidates all vectors (a full re-embed is only ~25 CI minutes, but make it a deliberate act).
- Input recipe (also pinned): `name. type_line. oracle_text (keywords)`. Normalize the card's own name inside oracle text to `~` (standard trick — stops "Lightning Bolt deals 3 damage" matching on the word "Lightning" instead of the effect).
- Cache: `embeddings.parquet` in R2 at `/data/cache/`, keyed `oracle_id → (text_sha256, vector)`. Each run re-embeds only new/changed hashes. First run ≈ 20–30 min; weekly runs ≈ seconds.

**3.5 — Neighbors.** Brute-force cosine over all pairs (35K × 384 is a couple of matrix multiplies in numpy — seconds). Emit top-25 per card with scores. This is the entire "similar cards" backend.

**3.6 — Build `cards.sqlite`:**
- `cards` table (all trimmed+merged fields), indexed on `name COLLATE NOCASE`, `oracle_id`, `(color_identity, cmc)`.
- `neighbors(oracle_id, rank, neighbor_id, score)`, PK `(oracle_id, rank)`.
- `rulings(oracle_id, published_at, comment)`.
- **FTS5** virtual table over `name, type_line, oracle_text` — this powers thesaurus-style text search.
- Finish with `PRAGMA page_size=1024; VACUUM; ANALYZE;` (small pages = small Range requests for httpvfs).

**3.7 — Deck-finisher artifacts (client-side, so the artifacts do the heavy lifting):**
- `finisher/index.json.gz` — for every Commander-legal card: `oracle_id, name, ci` (color identity bitmask), `cmc, type_bucket, role_flags, edhrec_rank, price_usd`. Role flags (ramp / card-draw / spot-removal / board-wipe / counterspell / recursion / tutor / land) derived by oracle-text pattern rules in the pipeline, overridable per-card in `tags/cards.yaml` — your hand-tuning beats regexes wherever you disagree. ~2–4MB gzipped.
- `finisher/vectors.bin` — the same embeddings **int8-quantized** in oracle_id order: ~30K commander-legal × 384 bytes ≈ **11MB**, one-time download, cached (see 4.1). If that feels heavy on mobile, the fallback knob is Matryoshka-style truncation to 192 dims (~5.5MB) — decide after testing, the pipeline flag is one line.
- The scoring algorithm itself ships as site JS, not artifact (Phase 4.4).

**3.8 — Emit + shard.** Alongside the SQLite file, emit plain JSON for the simplest consumers: `shards/names/<a-z>.json` (name → core fields) and `shards/neighbors/<prefix>.json`. Cheap to generate from the same build; gives every tool a zero-dependency option.

**3.9 — Validate (the gate that makes deploys safe).** Fail the build — leaving `latest.json` untouched, i.e., automatic rollback — unless: card count within ±10% of previous build; a fixed panel of known cards (Sol Ring, Pox, Chains of Mephistopheles…) returns correct oracle text via SQL; neighbors of a few anchor cards pass sanity (Counterspell's top-25 contains other counterspells); artifact sizes within expected bounds; FTS query smoke test passes.

**3.10 — Upload versioned, flip pointer last.**
```
/data/v/2026-07-06/cards.sqlite | finisher/* | shards/* | manifest.json
/data/latest.json  → {"version":"2026-07-06","paths":{...},"counts":{...}}
```
Everything under `/v/<date>/` is immutable-cached; `latest.json` is the only mutable object and is written **after** everything else lands. Rollback = rewrite latest.json to point at last week. Keep the trailing 4 versions, prune older in the workflow.

**3.11 — The card-authoring resolver (the piece that makes agent-built card pages safe).** This is the tool that lets Captain hand a dumb two-field list to one or more agents without any manual oracle_id entry and without agents ever guessing which card is meant. It rides on the same bulk data the pipeline already downloads, so it adds no new dependency — it only becomes usable once the Phase 2/3 data exists.

- **Input:** a plain list, one card per line, two fields only: `name | slug`. `name` is what Captain calls the card in plain English; `slug` is the intended `.html` filename. These are the only two things a human decides.
- **Resolution (deterministic, no fuzzy matching):**
  1. Exact-match `name` against the Oracle bulk name index (case-normalized). **Not** a fuzzy/live API search — exact match against the baked corpus, so results are reproducible and can't drift.
  2. On a unique hit → capture `oracle_id`, set `is_dfc` by checking whether `card_faces[0].image_uris` exists (NOT by `card_faces` presence — split/flip/adventure have faces but one image), build the R2 image URL(s) `<oracle_id>[.|-front.|-back.]png`, and build the Scryfall fallback URL(s) from the same bulk record.
  3. **Verify the image object actually exists in R2** (HEAD via rclone/API) so a page never ships pointing at a missing file.
  4. **Check the `slug` is not already a live `.html`** in the repo, so a build can't silently clobber an existing good page.
- **Halt-loudly behavior (the whole safety mechanism):** any of {name matched zero cards, name matched more than one card, image missing in R2, slug already taken} → the resolver **stops and prints a plain-English line naming the exact problem card** and does not emit that row. It never picks a "best guess." Example output: `STOP — "Giant Growth" is fine, but "Bolt" matched 0 cards (did you mean "Lightning Bolt"?) and slug "pris" is already taken.` Captain fixes the two-field list and re-runs; clean rows pass through untouched.
- **Output:** an enriched manifest, one row per card: `name | slug | oracle_id | image_url | scryfall_fallback_url | is_dfc | face_urls`. This manifest — not the raw list — is what goes to the agents.
- **How Captain runs it:** no terminal command. Captain pastes the `name | slug` list into chat; an agent runs the resolver and either returns "N cards resolved, ready to build" or the STOP report. Captain's surface never grows past the two fields + reading plain-English output + visually auditing finished pages + saying ship.
- **Why it's strictly better than pinning oracle_ids by hand:** same deterministic lookup, but zero transcription-error surface, DFCs auto-flagged instead of remembered, ambiguous/misspelled names caught at the gate instead of committed silently wrong.

**Done when:** `workflow_dispatch` produces a green run end-to-end, `latest.json` resolves, `SELECT oracle_text FROM cards WHERE name='Pox'` returns the right text from the artifact via the sqlite3 CLI, and the resolver turns a sample `name | slug` list (including one deliberately ambiguous name and one DFC) into a correct enriched manifest — halting loudly on the ambiguous line.

---

## Phase 4 — Client integration (per-tool; incremental forever)

**4.1 — One shared loader module** (`mtj-data.js`): fetch `latest.json` → resolve artifact URLs → cache artifacts in the browser **Cache API keyed by version string** (new version = new cache entry, old evicted). Every corpus tool imports this; no tool hardcodes an artifact path. On any fetch failure: friendly "corpus tools are napping" message + the tool's live-Scryfall single-card path keeps working. This module *is* the degrade-gracefully constraint, implemented once.

**4.2 — Magic Thesaurus.** Text search over FTS5 via range requests is chatty; better pattern for a search-as-you-type tool: pipeline emits a compact search index (name + type + oracle-text tokens, ~3–5MB gz) that the tool downloads once and searches in-memory (minisearch or hand-rolled). Detail views and rulings then come from the SQLite artifact or shards. Your `tags/cards.yaml` synonym entries surface here — that's the "thesaurus" part nobody else has.

**4.3 — Similar Cards.** Trivial after Phase 3: look up the card's neighbor list (shard fetch or one httpvfs query), render the 25 results with images from `/cards/png/`. Good candidate for the **first shipped corpus tool** — smallest surface, most demoable.

**4.4 — Deck Finisher (the flagship).** All client-side, in a Web Worker so the UI never jitters:
1. User pastes a partial decklist + commander → resolve to oracle_ids via the name index.
2. Load `finisher/index.json.gz` + `finisher/vectors.bin` (cached after first use).
3. Hard filter candidates by commander color identity + format legality.
4. Compute the deck's **centroid embedding** (mean of int8 vectors, upcast).
5. Score every candidate: `w1·cosine(candidate, centroid) + w2·popularity(edhrec_rank, log-scaled) + w3·role_need + w4·curve_need − already_in_deck`, where role_need comes from quota templates (e.g., 10 ramp / 10 draw / 8 removal / 2 wipes / 36 lands, adjustable sliders) minus what the deck already has, and curve_need from a target mana-curve histogram.
6. Fill greedily by highest score against unmet quotas until 100; show picks grouped by role, each with a "why" line (similarity / popularity / fills ramp slot) and a swap button.
7. Optional budget mode: cap by `price_usd` — free, because prices came in the bulk file.
Scoring 30K candidates × 384 dims in a Worker is tens of milliseconds; this genuinely needs no server. The weights `w1..w4` and quota templates live in a config JSON so tuning never touches code. When richer synergy data (EDHREC-later, or your own co-occurrence layer) arrives, it becomes an additional score term — the architecture doesn't move.

**4.5 — sql.js-httpvfs (optional power layer).** Wire it up for tools wanting arbitrary SQL against `cards.sqlite` (advanced explainer pages, a future rules-ceiling tool). Set `requestChunkSize: 1024` to match the DB page size. Treat as enhancement, not foundation — every tool must already work off shards/indexes, so if the library misbehaves nothing user-facing depends on it.

---

## Phase 5 — Automation, ops, guardrails (an evening)

**5.1 — Schedule:** weekly cron (Scryfall: weekly is fine for gameplay data) + `workflow_dispatch` for on-demand (set-release days).

> **⚠ AS-BUILT, 2026-08-13: THE CRON IS UNBUILT.** `build.yml` ships
> `on: workflow_dispatch` only — no `schedule:` block — so 5.1 is a plan, not a
> description. Every run in the repo's history is manual and the last green one
> was **2026-07-05**. 5.2's keepalive guard is unbuilt with it and only becomes
> relevant once a schedule exists. `CLAUDE.md` claimed the weekly run as fact
> until this date; corrected there too.

**5.2 — The 60-day trap:** scheduled workflows in public repos auto-disable after 60 days without repo activity, and **scheduled runs don't count as activity**. Guard: a keepalive step in the weekly workflow (e.g., `gautamkrishnar/keepalive-workflow`, which makes an empty commit only when needed). Set it and forget it.

**5.3 — Failure = loud, stale = safe.** Actions failures already email you; validation failures leave last week's artifacts live. Add one line to the workflow that posts run status to a private channel in the Way of the Proxy Discord via webhook — your ops dashboard is a Discord channel, cost $0.

**5.4 — Budget guardrails:** the $5 Cloudflare billing alert from 0.1, plus a monthly 2-minute ritual: glance at R2 dashboard (storage ≈ 50–55GB, Class B well under 10M) and the Actions tab (green). That's the entire operational burden.

**5.5 — Disaster recovery, already free:** artifacts are regenerable from source (Scryfall bulk + your git-versioned tags) — the only irreplaceable data is `tags/cards.yaml`, which lives in git. Images are re-pullable via the backfill script. There is nothing to back up that isn't already backed up by being source code.

---

## Build order & first wins

| Step | What ships | Effort | Unblocks |
|---|---|---|---|
| Phase 0 | ✅ **DONE** — CDN live at cdn.mtjawnny.com | (complete) | everything |
| ~~Phase 1~~ | ~~Standalone media migration~~ — **dissolved into Phase 2** (one-lane decision) | — | — |
| Phase 2 | ✅ corpus DONE 2026-07-03 (36,155 PNGs in R2) — per-page cutover still open | per-page cutover in Claude Code | every image-using tool; repo growth stops |
| Phase 3 | Data pipeline green end-to-end | 2–4 evenings | all corpus tools |
| 3.11 | **Card-authoring resolver** — safe agent handoff | ~1 evening (on top of 3) | scaled multi-agent card creation |
| 4.3 | **Similar Cards — first public corpus tool** | 1 evening | proof + a video |
| 4.2 | Magic Thesaurus | 2–3 evenings | backlog flagship #1 |
| 4.4 | Deck Finisher | 3–5 evenings | backlog flagship #2 |
| Phase 5 | Full automation | 1 evening | hands-off forever |

Phase 0 is complete. Phase 2's backfill is complete (2026-07-03): the full corpus + a data snapshot with Tagger oracle tags live in R2 (`/cards/png/`, `/data/snapshots/2026-07-03/`). What remains of Phase 2 is the per-page cutover of the 12 legacy pages (+ CLAUDE.md image contract + QR test). Phase 3's first run can seed from the archived snapshot instead of re-downloading bulk data.

**Captain's standing workflow once Phase 2/3 land:** write a `name | slug` list → paste to chat → an agent runs the resolver (get "N ready" or a plain-English STOP) → agents build the pages from the resolved manifest → Captain visually audits → says ship → commit. That is the entire human surface. Everything else — oracle_id resolution, image URLs, DFC faces, fallback wiring — is machine-side and never hand-entered.

One deliberate omission, consistent with the needs doc: none of this touches the verified-and-hardcoded card-explainer pipeline. Explainer pages keep their verify-before-publish model; the corpus DB is substrate for *tools*, not a bypass for editorial verification.
