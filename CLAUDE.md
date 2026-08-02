# mtjawnny-pipeline — Claude Code Instructions

## What this is
The data pipeline for mtjawnny.com's corpus tools (Magic Thesaurus, Similar
Cards, Deck Finisher). Fetches Scryfall bulk data, merges a custom tag
layer, builds SQLite/embedding/shard artifacts, uploads them to R2. Runs
weekly via GitHub Actions (public repo = unlimited free Actions minutes).
Also home of the tier engine and the T3 axis foundry (derived-tag mining).

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

## Engine + foundry rules (do not drift)

- **Vocabulary:** "Tier" = CARD tiers (T0-T3) ONLY. Worker levels are
  "worker classes": DET (deterministic, zero tokens) / BULK / SYNTH / SUP.
  `rule:` namespace = derived tags. Provenance classes: tagger /
  rule-derived / human (full weight) / llm (discounted, never gate-bearing).
- **Every scoring constant is a ratified ruling, not a tuning knob.**
  Discuss before build. Nothing committed without Captain's explicit ask.
  Nothing model-generated is load-bearing without Captain ratification.
- **Determinism:** fixed seeds, explicit sort keys, x2 byte-identical
  gates on generated artifacts.
- **All-paragraph AND all-faces scanning** in every classifier/derivation.
- **Evidence-quote-or-discard** on every per-card assignment; quotes come
  from oracle text only.
- **Rank buries, never excludes** (sole exception: corroboration gate).
- **Paper rows preferred over A- (Alchemy) variants** in sampling,
  resolution, and emit.
- **Batch API submissions:** cost estimate from CURRENT pricing docs +
  Captain go-ahead first. Never remembered prices.

## Traps (learned the hard way)

- `granted_keyword_facts` must attach AFTER `build_card_doc` and BEFORE
  building `granted_keyword_index`, or the dimension silently self-blinds.
- Python set/dict iteration order breaks tie-break determinism.
- Same-card co-occurrence is the WRONG test for substitute families.
- `cards.sqlite` excludes token/plane layouts; corpus truth for foundry
  work is tier_engine's jsonl loader (38,233 cards).
- The local CR markdown contains NO literal reminder-text strings.

## Reference

- Full architecture and phase plan:
  `~/Projects/mtjawnny.github.io/docs/BACKEND-BUILD-PLAN.md` (3.1–3.11).
  As-built corrections: `.../docs/PHASE-2-COMPLETION.md` — especially
  correction #4 (`snapshot.jsonl` is a trimmed upload manifest, not
  field-complete; use `oracle-cards.jsonl.gz` for real fields).
- T3 arc state + ratified constants: `docs/MASTER-HANDOFF.md`
- Batch review loop: `docs/SUP-TRIAGE-PROTOCOL.md`
  (`/triage-alpha N` -> `/triage-beta N` -> Captain annotates ->
  `/triage-emit N`)
- Derivation law: `docs/DERIVED-TAG-LAYER-SPEC.md` (Lessons 1-3)
- Foundry spec: `docs/T3-AXIS-FOUNDRY-v3.md` — **inherits every standing
  rule in `docs/T3-BUILDOUT-PLAYBOOK.md`**; read both.
- Schema-pass ledger (parents/hierarchy, structural rulings S1-S7, open
  tensions T1-T2): `docs/PARENT-TREE-CANDIDATES.md`. Parents are DERIVED
  (union of children + direct members) — never hand-authored as axes.
- Family evidence + 6 unresolved family rulings:
  `docs/FAMILY-TREE-EVIDENCE.md`
- Batch ratification record: `docs/TRIAGE-BATCH-1.md` .. `-7.md`
  (Captain's annotations are authoritative; batch-4 §10 D1-D7 in
  particular defines the `deferred` status and the D6 cost-shape reversal)

**Docs live in THIS repo.** The site repo's `docs/` is gitignored, so
anything left there has no version history. On 2026-08-02 twelve
load-bearing documents were moved here for that reason. Never author or
leave pipeline/foundry/tier-engine documentation in `mtjawnny.github.io`.
The only deliberate exceptions, both read by absolute path:
`mtg-comprehensive-rules.md` and `PHASE-2-COMPLETION.md`.
