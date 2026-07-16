# mtjawnny-pipeline — Claude Code Instructions

## What this is
The data pipeline for mtjawnny.com's corpus tools (Magic Thesaurus, Similar
Cards, Deck Finisher). Fetches Scryfall bulk data, merges a custom tag
layer, builds SQLite/embedding/shard artifacts, uploads them to R2. Runs
weekly via GitHub Actions (public repo = unlimited free Actions minutes).

This is a separate repo from mtjawnny.github.io — that repo's CLAUDE.md
contract does not travel here. This file is this repo's own contract.

## Locked rules (do not drift)

- **JSONL only.** All Scryfall bulk consumption goes through
  `jsonl_download_uri`, streamed line-by-line, never loading the whole file
  into memory. The legacy bulk format is dead; never write a code path for
  it, even temporarily.
- **No card data in git, ever.** This repo holds code + `tags/` + `recipes/`
  only. `.gitignore` enforces it (`data/`, `*.jsonl`, `*.jsonl.gz`,
  `*.parquet`, `*.sqlite`) — never weaken it.
- **`oracle_id` is the only card key.** Slug does not exist in this repo.
- **DFC rule:** a card is two-image if and only if `card_faces[0].image_uris`
  exists. Never judge by `card_faces` presence — split/flip/adventure cards
  have faces but carry one root-level image. Meld parts are separate
  single-image records, each with its own oracle_id.
- **rclone/R2 upload flag:** always
  `-M --metadata-set "cache-control=public, max-age=31536000, immutable"`
  for versioned/immutable objects, or
  `-M --metadata-set "cache-control=public, max-age=300"` for
  `latest.json` ONLY. Never `--header-upload` — it silently fails to stick
  the header on R2.
- **Versioning:** artifacts land under `/data/v/<date>/`; `/data/latest.json`
  is the only mutable object and is always written LAST, after everything
  else lands. Never overwrite a versioned path.
- **Scryfall etiquette:** real `User-Agent: MTJawnnyPipeline/1.0
  (mtjawnny.com)` + `Accept` header on `api.scryfall.com` calls. Rate
  limits apply to `api.scryfall.com` only, not `*.scryfall.io` file
  origins — throttle to ~8 req/s on the API anyway as courtesy.
- **Card data comes from bulk files, never per-card API calls.**
- **The resolver (3.11, future) exact-matches names and HALTS LOUDLY** on
  any ambiguity — zero matches, multiple matches, missing image, taken
  slug. It never guesses. Nothing in this repo ever fuzzy-matches a card
  name.
- **Halt-loudly is the house style pipeline-wide.** On any unexpected data
  shape, stop with a plain-English message naming the exact problem.
  Never skip silently, never best-guess.

## Reference
Full architecture and phase plan: `~/Projects/mtjawnny.github.io/docs/BACKEND-BUILD-PLAN.md`
(sections 3.1–3.11). As-built notes and corrections from the Phase 2 image
backfill: `~/Projects/mtjawnny.github.io/docs/PHASE-2-COMPLETION.md` —
especially correction #4 (`snapshot.jsonl` is a trimmed upload manifest,
not field-complete card data; use `oracle-cards.jsonl.gz` for real fields).
