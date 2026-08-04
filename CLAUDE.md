# mtjawnny-pipeline — Claude Code Instructions

## What this is
The data pipeline for mtjawnny.com's corpus tools (Magic Thesaurus, Similar
Cards, Deck Finisher). Fetches Scryfall bulk data, merges a custom tag
layer, builds SQLite/embedding/shard artifacts, uploads them to R2. Runs
weekly via GitHub Actions (public repo = unlimited free Actions minutes).
Also home of the tier engine and the T3 axis foundry (derived-tag mining).

This is a separate repo from mtjawnny.github.io — that repo's CLAUDE.md
contract does not travel here. This file is this repo's own contract.

## FIRST: load full context before foundry/codebook work

**Captain's finding, 2026-08-02: every drift this project has suffered was a
session acting without enough context.** Not carelessness — partial reading.

Before any work on the codebook, the grammar, the tier engine or the foundry:

**→ Follow `docs/SESSION-START-PROCEDURE.md`. It is five gates and it is
short.** The summary, so this file stands alone if that one is missed:

0. **If no task was given, the handoff's NEXT WORK ITEM is the instruction** —
   work it, do not stop to ask. Only two things need Captain's explicit word:
   **ratifying new vocabulary** and **mutating the codebook**. Ruling, measuring,
   DET fixes and ruling docs proceed unasked; a ruling doc is not load-bearing
   until ratified. Pending ratifications go in ONE decision sheet, not one
   question per token.
1. Read the current session handoff. **`docs/SESSION-START-PROCEDURE.md`
   Gate 1 names which file that is** — do NOT pick it by filename sort, because
   `-EVE`/`-PM` suffixes sort *before* the bare-date file and "newest by name"
   selects the oldest same-day handoff. Superseded handoffs carry a
   forward-pointing banner. Its READING MANIFEST lists what else is mandatory
   for the task at hand.
2. Read **`docs/CODEBOOK-NAMING-GRAMMAR.md` WHOLE.** Not the section that
   looks relevant. Three separate errors on 2026-08-02 came from encoding one
   section's law while §7, §12a or a batch ruling governed the same slug — two
   of them would have destroyed Captain-ratified names.
3. Before calling any axis, slug or member defective — **before writing the
   finding, not after** — run:
   ```
   python3 experiments/foundry_slug_dossier.py <slug>
   ```
   It walks the axis's rename history and greps **every name it has ever
   had** across `docs/` and `docs/archive/`, then separates ruling lines from
   prose. A bare `grep` of the current slug is **not** sufficient: measured
   2026-08-02, **77 of 328 active axes (23%) have their rulings filed under a
   former name**, and 88% carry a ruling somewhere. Batch documents hold
   rulings recorded nowhere else, and **Captain's annotations in them are
   authoritative**.
4. Read **full oracle text, all faces**, never a truncated read. Three
   confident findings on 2026-08-02 were false because only the first ~150
   characters were read.

**When a check you wrote disagrees with a ratified list, suspect the check
first.** A conformance checker is only as good as the set of rulings it
encodes.

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
- **NEVER TRANSCRIBE THE CR — DERIVE FROM IT AT RUN TIME.** Captain,
  2026-08-04: *"every time consulting the CR is the answer."* Measured that
  session: **every** finding traced to a CR rule, and **every** defect traced to
  a hand-written list standing in for a closed list the CR already publishes —
  landwalk (5 variants listed vs CR 702.14a's grammar over CR 205), trigger
  verbs (24 curated vs CR 701), keyword classes (curated vs 702.Na), token types
  (8 of 21 vs CR 111.10), and an ordinal recount that omitted `twelfth`.
  A hand-list is not a shortcut, it is a defect with a delay. If the CR
  enumerates it, parse the CR — with a halt-guard, so a parse failure stops the
  run instead of silently truncating the vocabulary. **The rule is predictive:**
  the two hand-lists still standing in `foundry_shape_extractor.py` (the
  activated cost-head verbs, and the replacement templates vs CR 614.1a-c's
  three) are exactly the two open defects D5 and D6.
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
- **A trigger's EVENT lives in its CONDITION, never in its effect.** CR 113.3c:
  *"Triggered abilities have a trigger condition and an effect. They are written
  as '[Trigger condition], [effect]'."* Matching a verb against the whole
  ability line over-counted **seven** families on 2026-08-03 (sacrifice 181→110,
  end-of-combat 111→17, self-vs-other 1,921→1,558, …). Legion Warboss's "create
  a Goblin **that attacks**" is an effect, not an attack trigger.
- A trigger clause does **not** end at the first comma — "Whenever a Mutant**,**
  Ninja, or Turtle you control enters" has commas inside the object phrase.
- **A ground-truth set only validates the shapes it contains.** The 116
  hand-verified Clue routings stayed byte-identical through every one of those
  seven fixes. Keep the set; keep widening it.
- **A missing trigger verb makes the clause end LATER, not earlier.**
  `trigger_clause` returns the first comma-prefix carrying a *listed* verb, so
  when the real event verb is absent it walks PAST the condition and picks up a
  verb from the EFFECT. The old comment claimed the opposite ("conservative
  direction") and that is what hid the defect for eight fixes. The verb set is
  now DERIVED from the CR keyword-action list — but note `cycle` is filed by the
  CR as a KEYWORD, not a keyword-action, and participles (`tapped`) are
  unreachable by `(es|s)?` inflection. Both are in the halt-guard.
- **The gap census is BLIND to `spell-or-static` by construction.** It excludes
  that bucket, so anything misrouted there is unreportable, not merely unfixed.
  236 replacement effects (CR 614.1c "As [this permanent] enters…") hid there
  indefinitely. When a shape "doesn't exist", check that bucket before believing it.
- **Dossier the name you are about to WRITE, not the name you started from.**
  Running Gate 3 on the census name `main-phase` returned clean while
  `rule:postcombat-main-phase-trigger` was already an active axis with a batch-6
  KEEP ruling.
- **A parent's children having ~zero overlap is the RIGHT answer**, not weak
  evidence — the parent exists to group cards that share no child ("Same Job,
  Different Words"). Same-card co-occurrence remains the wrong test.
- **A ratified token with no EMITTER looks exactly like one with no members.**
  Grammar §2 is parsed at run time, so ratifying a row closes its gap only if a
  `mark()`/`msub()` call already produces that token. On 2026-08-04, 11 of 14
  newly ratified tokens still emitted `None, "<descriptor>"`. Same shape as "a
  ratified standard with no caller"; nothing gates either.
- **A markdown table is an API.** §2's DELIVERY table is machine-parsed from the
  `## 2.` heading to the **first `###`**. Any table placed under it — including
  one listing shapes deliberately left UNratified — is ingested as ratified
  vocabulary. Second instance of this exact trap; §2f now carries the rule.
  Prose and bullet lists are safe, tables are not.
- **`\d` in a `re.sub` REPLACEMENT string is a group escape**, not the character
  class — use a lambda. Cousin of the `re.escape`-before-substitution trap.
- **Set subtraction cannot answer "does X depend only on Y"** — it removes the
  members present in both, so the tokens you are testing vanish from the control.
- **A keyword matcher needs `\s+`, not `\s*`, before a non-cost parameter**
  (`\s*` made "EQUIPPED Warriors…" match CR 702.6c's `Equip [quality]`), must
  try the WHOLE line before splitting on commas (a parameter may contain them —
  `Ward—{2}, Pay 2 life.`), and must REFUSE any form whose parameter is an
  ABILITY (CR 702.178a `Max speed — [Ability]`) — matching the wrapper
  overwrites the inner ability's correct delivery.
- **`instantiated_members` in `grammars.json` asserts codebook AXES.** A
  delivery-only slug is never an axis (`TRIAGE-BATCH-1.md` §1c), so a DELIVERY
  grammar family lists its measured nodes elsewhere and leaves that field empty.
- **A measurement probe must consume the SAME preprocessing as the classifier
  it is measuring**, or it under-reports silently. On 2026-08-05 a probe
  matching `^as long as` on the raw line measured 400; the classifier matches
  after `ABILITY_WORD.sub()` and moved **443**. The 43 were ability-word
  statics (`Threshold — As long as…`, CR 207.2c) and all correct — but they
  arrived as an unexplained surplus in the diff, not as an error. Same shape as
  Gate 3b's `--orphans` finding (4 consumers use `det_scan_texts()`, 19 bypass
  it), one layer down.
- **A new tail branch in `parse_delivery` can only claim lines that already
  reached `spell-or-static`** — which makes zero re-routes a structural
  guarantee, not a lucky result. Prefer the tail when a shape does not need to
  outrank an existing branch.
- **`build_keyword_homes` runs `parse_delivery` over each keyword's CR
  templated text**, so any change to the classifier can silently move
  `keyword_homes`. Diff that count on every extractor change; a keyword whose
  parameter is an ABILITY must stay refused by `build_keyword_forms`.
- **Name a shape by the CR rule that DECIDES it, never by the words that open
  the line.** "The `this creature …` group" named a *subject*, and delivery is
  never decided by the subject: 738 of those 2,185 lines were burn spells
  (`~ deals 3 damage to any target`, CR 113.3a). The cut that works is
  **CR 113.3a itself** — a spell ability exists only on an instant or sorcery,
  so a card with no instant/sorcery face leaves CR 113.3's four-category
  enumeration closed on `static`. Zero `deals` lines survive it.
- **A carried-forward count in a handoff or a closing summary is not a
  measurement.** "931 lines" existed in no artifact; the real number was 2,185
  and the real shape was three shapes. Re-measure before naming the next slice.
- **A DATA SOURCE can be a hand-list wearing better clothes.** The
  self-reference noun set was *derived* from live corpus type lines and was
  still missing **6 of CR 205.2a's 15 card types** — including CR 109.2d's own
  worked case `this scheme` — because the corpus gate excludes those layouts.
  The test is not "did a human type this list" but **"can the source contain
  every member the CR names?"** Card types come from CR 205.2a and **every
  subtype list from CR 205.3g–q** (ten of them, closed by 205.3r). Supertypes
  (CR 205.4a) are adjectives and never self-reference nouns. A corpus scan of
  type lines is kept only as a **TEST** of the CR parse, never as its source.
- **The CR prints a CURLY apostrophe (U+2019); Scryfall prints a straight one.**
  `Urza’s` ≠ `Urza's`, and the same hits `C’tan`, `Shi’ar`, `Serra’s Realm`.
  Any CR-parsed value compared against card data must emit both forms.
- **The local CR is a VENDORED SNAPSHOT and can fall behind the corpus.**
  Measured 2026-08-05: `Chorus` is a printed spell type absent from CR 205.3k's
  five. Refreshing `docs/mtg-comprehensive-rules.md` is a real maintenance item;
  known discrepancies live in a dated CR-LAG register that names its evidence,
  and anything outside it halts.
- **A halt-guard must assert CONTENT, not cardinality.** `type_vocabulary`'s
  Oxford-comma split produced `and vanguard`, `and world`, `and urza's` — so
  the LAST member of every CR 205 list was missing while `len() >= 15` stayed
  green. A count cannot see a substitution. Same family as "a ratified token
  with no emitter" and "a ratified standard with no caller".
- **When a rule names a card type, ask the CR which OTHER types it covers.**
  The attachment branch had Auras (CR 303.4) and Equipment (CR 301.5a) and
  omitted Fortifications, though CR 301.6 states the analogy outright
  (*"Rules 301.5a–f apply to Fortifications in relation to lands just as they
  apply to Equipment in relation to creatures"*). Same audit found the SOURCE
  side of the damage family covering 2 of CR 120.1's 4 recipients while the
  RECIPIENT side was ratified against all four — **one side of a family
  enumerated from a closed CR list, the other not.**

## Reference

- **Current state + READING MANIFEST: `docs/SESSION-HANDOFF-2026-08-05.md`**
  — start here, always. It lists every markdown a session needs, tiered by
  what you are about to touch. (This line goes stale; the authoritative
  pointer is Gate 1 of `docs/SESSION-START-PROCEDURE.md`.)
- **Corpus-wide SHAPE work is a script, not tokens.**
  `experiments/foundry_shape_extractor.py` parses every card's DELIVERY slot
  for free, deriving its vocabulary from grammar §2 at run time. Run it before
  reading cards by hand; audit its output rather than re-deriving it.
  Census: `docs/DELIVERY-GAP-CENSUS-2026-08-03.md`.
- Ratified codebook surgery runs through
  `experiments/foundry_membership_move.py` with a declared spec in
  `experiments/moves/*.json` — it decides nothing, and enforces member
  conservation, determinism ×2 and an atomic write. Never hand-edit
  `codebook.json`.
- Full architecture and phase plan: `docs/BACKEND-BUILD-PLAN.md` (3.1–3.11)
  — the local, git-tracked copy; the site repo's byte-identical duplicate
  was removed 2026-08-02.
  As-built corrections: `~/Projects/mtjawnny.github.io/docs/PHASE-2-COMPLETION.md`
  (deliberately site-resident) — especially
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
`docs/mtg-comprehensive-rules.md` and `docs/PHASE-2-COMPLETION.md`.
