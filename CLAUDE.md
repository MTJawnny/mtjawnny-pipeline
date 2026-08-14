# mtjawnny-pipeline — Claude Code Instructions

## What this is
The data pipeline for mtjawnny.com's corpus tools (Magic Thesaurus, Similar
Cards, Deck Finisher). Fetches Scryfall bulk data, merges a custom tag
layer, builds SQLite/embedding/shard artifacts, uploads them to R2. Runs
weekly via GitHub Actions (public repo = unlimited free Actions minutes).
Also home of the tier engine and the T3 axis foundry (derived-tag mining).

This is a separate repo from mtjawnny.github.io — that repo's CLAUDE.md
contract does not travel here. This file is this repo's own contract.

## 0. BEFORE ANYTHING ELSE — DOES THIS WORK REACH A CARD?

**→ `docs/PRODUCT-REALITY-AUDIT-2026-08-09.md`. Read it before taking any
foundry work item.** Measured 2026-08-09, and it governs whether the rest of
this page matters:

- **The T3 foundry is NOT CONNECTED to the product.** `tier_engine.py` reads
  **no** foundry output — no `codebook.json`, no `det-patterns-v2.json`, no
  axes — and emits exactly **one** `rule:` tag, which it derives itself. All
  **13** importers of `foundry_shape_extractor` are audits, censuses, probes or
  regression harnesses. The delivery classifier's output is consumed only by
  tools that check the delivery classifier.
- **19.3% of the corpus carries any derived tag** (6,275 of 32,557). The
  full-corpus pass has been `STOPPED_FOR_CAPTAIN` since 2026-08-02 on **one**
  decision, `A15-VOCAB-01`.
- **204 commits since 2026-08-01 touched `pipeline/` ZERO times.**

**THE QUESTION TO ASK OF YOUR OWN WORK ITEM, AND IT IS THE ONLY NEW ONE:**

> *Which shipped artifact changes if I finish this? If none, say so out loud
> before starting, not after.*

**Every gate in this repo answered "did I break anything?" NONE answered "does
this reach a card?"** That is why routing 1,012 lines to `static` on 2026-08-09
passed twelve green gates and moved nothing a user can see — and why it made
the `--gaps` backlog look *smaller* while coverage stayed at 19.3%. **A shape
routed to a ratified token leaves the gap census without tagging one card.**

**ONE GATE NOW ASKS IT — `experiments/foundry_reachability.py`, Gate 2 row 13**
(audit §10, built 2026-08-09). It parses the shipped entry points out of
`.github/workflows/`, walks their import closure, and reports how many foundry
artifacts reach a shipped card: **0 of 5**, while `codebook.json` carries **26**
`experiments/` consumers. Ratcheted on `reaching` and negative-controlled by
`--selftest`, so it is a gate and not a reporter listed as one.

**AND ITEM 1 OF §9 IS ANSWERED — `docs/WIRE-RESULT-2026-08-09.md`. DO NOT
RE-RUN IT.** The codebook→`tier_engine` join was built offline and graded
against predictions committed before the harness existed. **It does not land —
1 of 3 criteria passed.** The join is a re-rank by codebook MEMBERSHIP: across
33 hand-named correct neighbours, **every one on its axis was promoted and
every one not on it was demoted, without exception**, and displacement was
uniform (every non-member fell by exactly the number of members inserted above
it). **The derived term does not rank, it PARTITIONS — into "reviewed" and "not
yet reviewed".** Axis recall against those families: **13/33 = 39%**, and the
one axis at 100% recall moved nothing, because its members already share
verbatim text and the engine reaches them at Tier 2 for free. **The codebook is
complete exactly where the engine did not need help.** So the blocker is
coverage, not plumbing — which makes this the measured argument for §9.2
(`A15-VOCAB-01`), the next item.

**W4 IS PAUSED.** Do not take the remaining 3,358 decidably-static lines; it is
the same trade. The ordered queue is §9 of the audit: **wire the codebook into
`tier_engine` first**, then unblock `A15-VOCAB-01`, then revive
`foundry_review.html` (dark since 2026-07-17 and named "the highest-leverage
unstarted work" the whole time), then get a green pipeline build (last one
2026-07-05).

---

## IF YOU HAVE NO CONTEXT, READ THESE SIX LINES

**These govern HOW to work. §0 above governs WHETHER the work is worth doing —
read it first.** The traps list below is ~70 bullets and a cold session cannot
hold it. It is a reference, not a checklist. These six are the whole of it that
you must act on before writing any code:

1. **`python3 experiments/foundry_gate2.py`** — Gate 2, all of it, one exit
   code. Never run the individual commands to "save time"; ten commands get
   run as nine, which is why the runner exists.
2. **Writing a probe, a script, a one-off measurement? `import foundry_probe as p`.**
   `p.corpus()` · `p.rows()` · `p.domain()` · `p.assert_disjoint()` ·
   `p.must_capture()` · `p.longest_match()`. **21 probe defects across five
   sessions, and every one was somebody hand-rolling something this module
   already does.** It is shorter than doing it by hand — that is the point.
3. **Never guess a field's values.** `p.domain(records, "status", "active")`
   halts if the value is absent. A filter on a value that does not exist
   matches nothing and reads as a clean result.
4. **Read EVERY moved line in a routing diff.** Not a sample. On 2026-08-09 a
   fix moved 137 lines and **1 of them was a regression** (Field of the Dead);
   the diff reports a correct re-route and a wrong one identically.
5. **A count is not a measurement.** Re-derive it. Two counts written into
   ratified §2 law the same day they were measured were both wrong.
6. **Your probe is wrong before the code is.** When your check disagrees with a
   ratified list, suspect the check — measured base rate, and 3 of 8 negative
   controls on 2026-08-09 were mis-aimed and each first read as "this gate is
   broken".
7. **BEFORE PROPOSING A MUTATION, MEASURE WHETHER THE THING IS BROKEN.**
   Twice on 2026-08-09 a "defect" was not one. "Repair the 55 stale quotes"
   would have **rewritten 54 correct Captain-ratified quotes** to make a
   defective test pass — 54 were verbatim correct and the fixture was reading a
   reminder-stripped view. "0 of 89 have a home" was an over-narrow string
   search; 27 already had homes. **A null result from your own search is not a
   fact about the data.**
8. **A NUMBER GOING UP IS NOT AUTOMATICALLY A REGRESSION — READ THE
   DENOMINATOR.** `--wide` mismatches went 3 → 10 and that was 67 seeds moving
   from *ungraded* to *graded* (60 pass, 7 fail). State the reason in the
   `--update-baseline` commit or the next session will read it as rot.

**Everything else on this page is context for WHY.** Read it when you have room;
act on the six above always.

---

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
  Gate 3b's `--orphans` finding (**8** consumers use `det_scan_texts()`, **23**
  bypass it — re-derived 2026-08-13; this line read 4/19 from 2026-08-04 and
  was never re-measured, which is the carried-forward-count trap biting THIS
  FILE for the second recorded time), one layer down.
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
- **The CR and the corpus can each be ahead of the other, and BOTH have been.**
  Measured 2026-08-05: `Chorus` is a printed spell type absent from CR 205.3k's
  five — and still absent after the 2026-08-07 refresh, so that is the CR
  trailing the cards, not a stale snapshot. Measured 2026-08-09: CR 701.70
  Recruit and CR 702.195 Storied have zero corpus lines, the CR leading. Known
  discrepancies live in a dated CR-LAG register that names its evidence, and
  anything outside it halts.
- **A halt-guard must assert CONTENT, not cardinality.** `type_vocabulary`'s
  Oxford-comma split produced `and vanguard`, `and world`, `and urza's` — so
  the LAST member of every CR 205 list was missing while `len() >= 15` stayed
  green. A count cannot see a substitution. Same family as "a ratified token
  with no emitter" and "a ratified standard with no caller".
- **A PERIOD is not an ability boundary; a PARAGRAPH is (CR 113.2c).** But one
  paragraph may hold several abilities: CR 603.11 / 607.2h put a STATIC ability
  and the TRIGGERED abilities linked to it in one paragraph, and CR 701.43d
  names exert as the worked case. **CR 603.12 is the discriminator** — a
  reflexive "when you do" needs a *resolving* ability to create it, and a
  created ability's delivery belongs to its creator (§2d). Measured 2026-08-05:
  516 lines have a later-sentence trigger; only **37** are separate abilities.
  Exclusions are all CR rules: 113.3a (spell abilities), 702.159a (`Visit —` is
  triggered), 706.3b (a die-roll table is one ability), §2 (quoted grants).
- **Strip an ability-word prefix BEFORE splitting sentences.** `No One Dies! —`
  ends in "!", so a sentence splitter cuts the prefix off as its own sentence
  and hides the real trigger. `ABILITY_WORD` accepts only `[A-Za-z'’\- ]`, so
  any prefix with a DIGIT (`Nitro-9 —`) or punctuation is never stripped and
  the line silently misses its own branch.
- **"Reached `spell-or-static`" is NOT "is static."** It is a proxy, and it
  fails exactly when the first ability is a trigger that went unrouted for an
  unrelated reason. Gate on a positive test, never on "nothing else claimed it".
- **A DERIVED MAP IS NOT THE LIST IT WAS DERIVED FROM.** `KEYWORD_HOME` is
  keyed on CR 702 keyword names, so it reads like the keyword list — but
  `build_keyword_homes` SKIPS any keyword whose home cannot be derived, and
  `awaken`/`impending` are absent. Asking it *"is this a keyword?"* answered no,
  and `Awaken 4—{4}{W}` was read as a flavor word. A membership test must use
  the **membership list** (`CR_KEYWORD_NAMES`, parsed from `load_702`), never a
  map that happens to be keyed on it. Same family as "a ratified token with no
  emitter" and "a ratified standard with no caller".
- **The CR enumerates ability words and REFUSES to enumerate flavor words.**
  CR 207.2c publishes all 61 ability words in one sentence (`descend 4`,
  `descend 8` carry DIGITS; `council’s dilemma` a curly apostrophe) — so the
  strip is parsed, not shaped. CR 207.2d then says flavor words *"are not
  listed in the Comprehensive Rules"* and are tailored per card. **A list the
  CR declares un-enumerable is the ONE honest reason a heuristic may stand** —
  declare it and cite the rule; everything else is a hand-list with a delay.
- **An em-dash prefix is one of SIX things and the CR decides which.** Saga
  chapter (714.2), die-roll row (706.3b), modal header (700.2), a cost
  (601.2b), an activated cost (602.1), a keyword parameter (702.Na) — those
  five carry rules meaning and must NOT be stripped; only 207.2c/207.2d words
  may be. But the keyword refusal must stay NARROW: a keyword whose parameter
  is an ABILITY (`Max speed —`, `Visit —`) is strippable **on purpose**, since
  `build_keyword_forms` refuses those forms so the INNER ability reaches its
  own branch.
- **Zero movement can be the CORRECT result and still be a real fix.** 739
  lines stopped being stripped (modal headers, Saga chapters) and routed
  identically — because `CHAPTER` is tested before the strip and
  `_MODAL_HEADER_RE` reads the RAW line. The old behaviour was wrong somewhere
  nothing downstream could observe. Don't read "0 moved" as "no-op"; read it as
  "the guard was elsewhere".
- **A SEPARATOR IS SCAFFOLDING, BUT THE SYMBOL IS AN ABILITY.** CR 711.2,
  716.2 and 721.2 say the same sentence — *"any abilities printed within the
  same text box striation are part of its static ability"* — and 711.3/721.3
  add the striations *"have no game significance other than clearly
  demarcating"*. So STRIP the marker and let the content classify: claiming
  `12+ | {3}{W}, {T}: Create a token…` as `static` overwrites an ACTIVATED
  ability, which is the `Max speed — [Ability]` trap again. Only a marker with
  nothing after it is the ability itself.
- **"UNROUTED" IS NOT "STOPPED".** Pawprint modes read 100% unrouted after
  being correctly fixed: Season of Loss is a sorcery, its header is
  `spell-or-static` by CR 113.3a, and a mode inherits its header's delivery.
  Inheriting "no ratified token" is the right answer. Test whether the delivery
  is REACHABLE, not whether it is ratified — an unrouted rate alone called
  three correct constructs broken.
- **AN OPTION CAN BE LOST AT THREE LAYERS, AND TWO HAVE NO OTHER REPORTER.**
  DROPPED (no delivery row), UNSCANNED (effect text in no `det_scan_texts`
  variant), UNCONTEXTED (readable, but never JOINED to the header that says
  WHEN it happens, so a proximity pattern cannot span it). The routing
  regression compares tokens, the gap census counts vocabulary, and the
  conservation audit proves nothing was deleted — all three are blind to
  layer 3. `foundry_visibility_audit.py` is the reporter. **Run it for the
  number; do not read one here.** The 237 this line used to quote was stale one
  commit after it was written (`3ff3afd` joined the die rows and spree), which
  is the "carried-forward count is not a measurement" trap biting THIS FILE.
- **A PROBE IS CODE AND GETS AUDITED LIKE CODE.** Three probe defects in one
  session, each of which would have been reported as a finding: a `non-ASCII`
  class that re-measured the em-dash, `{TK}` read as a CR 721 station symbol
  when it is Unfinity's ticket, and a visibility audit that called 165 options
  unscannable because it compared un-canonicalized text against
  `det_scan_texts` output. Run the system map's question on your own probe
  before you run it on the code.
- **A SHAPE TEST LOOKS LIKE A MEASUREMENT.** `{TK} — 1/5` is not a CR 721
  station symbol; `{TK}` is Unfinity's TICKET symbol on sticker cards
  (`unf`/`sunf`, type line `Stickers`). 192 lines nearly filed under the wrong
  CR rule on shape alone. Twice in one session (see the `non-ASCII` probe), so
  ask the system map's question of your own probe: *where does this come from,
  and can that source contain what I think it contains?*
- **A MODE IS NOT AN ABILITY (CR 700.2), so CR 113.3's enumeration never
  closes on a bullet.** *"Each of those options is a mode"* — an option inside
  an ability is not one of CR 113.3's four categories, so "this card has no
  instant/sorcery face, therefore `static`" is valid for a printed ability and
  proves nothing about a `• …` line. A mode's delivery is its parent's (§2d /
  D3 inheritance). Hawkeye's `• Explosive — Hawkeye deals 2 damage to target
  player.` is a mode of a CR 603.12 reflexive trigger, not a static.
- **An ABILITY NAME is a CR 207.2d flavor word and is never vocabulary.**
  CR 207.2d: *"an ability word ties together several abilities with similar
  functionality; each flavor word is tailored to the specific ability it
  appears with."* `Landfall` is in CR 207.2c's closed list and on 174 lines;
  `Sell Contraband` is on one card and in no list anywhere. Strip it and
  discard it — never let one become an axis, a token or a tag, or you get a
  1-member axis that can never gain a second. The **bullet** is CR 700.2 list
  punctuation, so a mode name must be stripped through it.
- **IMPROVING RECALL CAN HAND OUT A WRONG RATIFIED TOKEN.** Stripping mode
  names let `~ deals 2 damage to target player` reach a branch that had never
  seen it, and a line that was an *honest gap* became confidently `static`. A
  gap-closing diff scores `None → ratified` as pure profit and **cannot see
  this** — read every closed gap, every time. Same family as "a fallback is a
  wrong answer with a ratified name", one layer up.
- **A PROBE THAT OVERLAPS ANOTHER PROBE reports a correlation as a finding.**
  A `non-ASCII` punctuation class written as `[^\x00-\x7f]` also matches the
  em-dash, the bullet and the curly apostrophe — so it silently re-measured
  three classes already in the same table and scored 6,342 lines at ratio 1.55.
  Restricted to letters: 33 lines, ratio 0.81. Cousin of "a probe must consume
  the same preprocessing as the classifier": there it disagreed with the
  classifier, here it agreed with itself twice.
- **A CENSUS CANNOT ANSWER "did anything get LOST" — conservation can.** Assert
  that what went in came back out: the strip returns a *suffix* of its input
  (nothing deleted mid-line), `sentence_spans` reassembles character-for-
  character, every ability line yields ≥1 delivery. `foundry_punctuation_audit.py`
  runs all three; test A would have caught the 2026-08-04 hyphen disaster
  (`"When Spider-Ham enters"` → `"Ham enters"`) *without knowing what an ability
  word is*.
- **An ability with NO SOURCE is not the keyword's ability.** CR 702.179a says
  *"Start your engines! is a static ability"*, but `effective_classes` returns
  `['static','triggered']` because it swept in 702.179d's inherent trigger —
  which *"has no source"* and exists whether or not any permanent has the
  keyword. The `== ["static"]` fallback then never fires and 46 lines go
  unrouted. When a CR keyword entry describes a game rule alongside the
  keyword, only the ability the keyword GRANTS is its class.
- **A population count is not a yield count is not a routing claim.** AUDIT-5's
  121 unstrippable prefixes were 41 real ability/flavor words, of which 29
  changed delivery — three questions, three numbers. State which one you mean.
- **When a rule names a card type, ask the CR which OTHER types it covers.**
  The attachment branch had Auras (CR 303.4) and Equipment (CR 301.5a) and
  omitted Fortifications, though CR 301.6 states the analogy outright
  (*"Rules 301.5a–f apply to Fortifications in relation to lands just as they
  apply to Equipment in relation to creatures"*). Same audit found the SOURCE
  side of the damage family covering 2 of CR 120.1's 4 recipients while the
  RECIPIENT side was ratified against all four — **one side of a family
  enumerated from a closed CR list, the other not.**
- **AN AUDIT'S BOUNDARY IS UPSTREAM OF SOMETHING.** Conservation test A
  measured from `ability_lines()` OUTPUT — and `ability_lines()` IS the
  reminder strip plus a split, so the biggest text mutation in the pipeline
  (19.2% of every oracle character, CR 207.2a) sat upstream of the boundary and
  test A's own law was never applied to it. Ask what runs BEFORE the first
  thing your audit reads.
- **CONSERVATION IS STRUCTURAL AND CANNOT SEE CONTENT.** Interleave
  conservation passes a GREEDY `\(.*\)` that eats every character between the
  first `(` and the last `)` — kept + removed still reassembles perfectly. Only
  the span's own CR definition catches it. Negative-control every guard against
  a deliberately broken version of what it guards.
- **THE HOUSE STYLE HAS NO POSITIVE-CORRECTNESS TEST — build the fixture from
  ratified artifacts, never by hand.** Conservation asks "did anything get
  lost", invariance "does it depend on the name", diff "did it change".
  Nothing sees a token that was wrong before the first snapshot, and
  `diff --strict` scores `None → ratified` as pure profit.
  `experiments/moves/*.json` already hold **534 `class: human` seeds with
  evidence quotes** — derive expected values from the slug against §2 / CR 702
  at run time. `foundry_ground_truth.py` found 91 unrouted typecycling lines on
  its first run.
- **CR 201.5c's shortened name is LEGENDARY-ONLY, and the qualifier is in the
  rule** (*"used in this manner"*). Ungated, the `" of "` / `" the "` head
  heuristic erased CR 205 TYPE words from oracle text on 26 non-legendary
  cards — `Destroy the Evidence` scanned as `~ target land`, `Knight of the New
  Coalition` created a `~ token`. All 118 legendary hits were correct.
- **EVERY STANDING CHECK SHARES ONE GATE, SO THE GATE IS ONE BLIND SPOT, NOT
  EIGHT.** All of them call `load_corpus_gated()`. 114 CR 205 members are
  attested ONLY outside it, including the six card types that caused the
  self-reference defect. `foundry_gate_audit.py` is the reporter; all 5,676
  gated-out cards parse, so the gate is a POPULATION decision, not a
  capability limit — a CR enumeration can still be tested against all of it.
- **A RATCHET NEEDS NO CONSTANT.** Both new audits exited 0 on any amount of
  degradation, and a tolerance band would be exactly the tuning knob the engine
  rules forbid. `foundry_audit_baseline.py` pins the numbers and makes movement
  in the WORSE direction fatal, better-direction movement reported, and either
  one accepted only by an explicit `--update-baseline`. Same standard as the
  determinism ×2 gate.
- **"UNROUTED" OVERSTATES THE WORK BY ~3×.** 93.7% of it is `spell-or-static`,
  and CR 113.3a splits that bucket with no new vocabulary: **69.9% sits on
  cards WITH an instant/sorcery face**, where grammar §1's unmarked default is
  already correct. Only the decidably-static 30.1% is a queue. `--gaps` now
  reports inside the bucket it excludes.
- **A JOIN IS A CAPABILITY, AND CAPABILITIES CUT BOTH WAYS.** The joins that
  let a mode reach its header could also let a pattern pair the FRONT face of a
  DFC with the BACK — a co-occurrence that never exists in play (CR 712.8,
  CR 709.3b). Currently zero, because house proximity scoping is `[^\n]*`; the
  assertion ships WITH the joins, not after one breaks it.
- **A PROBE DEFECT IS THE DEFAULT OUTCOME, NOT THE EXCEPTION.** Six more this
  session on top of the previous four, every one in the same family — *asking
  the question again instead of consuming what the classifier emitted*:
  `parse_deliveries` instead of `deliveries_for_lines` (lost D3 inheritance);
  `kw in [(tok, desc), …]` against tuples (scored a correct 304-member family
  0/304); grading a family axis by string equality against a printed variant;
  splitting type lines on whitespace (called 28 multiword/curly-apostrophe CR
  subtypes unattested); a band boundary that stopped at any `roll … dice` line
  (Barbarian Class's own level-2 ability); `_direction` reading only a dotted
  key's LEAF, so every nested pinned metric silently resolved to neutral.
- **THE CR STATES THE SAME EVENT IN THE ACTIVE VOICE ONE RULE ABOVE THE
  TRIGGER RULE — LOOK ONE RULE UP.** A branch written from the sub-rule that
  describes the *trigger* inherits that sub-rule's voice and silently loses
  every card printing the other one. Three sites in one session, all the same:
  106.12a prints *"is tapped for mana"* while **106.12** defines the act
  itself (*"to TAP [a permanent] FOR MANA is to activate a mana ability…"*) —
  32 lines; 508 prints the attack while **506.3** prints the defence (*"only a
  player, a planeswalker, or a battle CAN BE ATTACKED"*) — 6 lines, five of
  them the exact Curse cycle §6's `enchanted-player` was ratified for; 708.8
  prints *"is turned face up"* while **708.7** prints *"allow the permanent's
  CONTROLLER TO TURN IT FACE UP"*. **VOICE is a sweep class beside W1's
  INFLECTION class**, and word ORDER is a third: the CR 120.1 recipient side
  also prints noun-first (*"combat damage IS DEALT TO YOU"*) and both arms
  tested `dealt`→`damage` only.
- **A DETERMINER SLOT IS NOT VOCABULARY — DERIVE IT FROM THE TEMPLATE.**
  `put into (a |their |your |its owner's )?graveyard` was a hand-list of four
  English determiners standing where the CR template has an open noun phrase,
  and it lost every *"an opponent's graveyard"* (15 lines, incl. the Bridge
  from Below / Lurking Skirge death family) and *"a player's graveyard"*. The
  CR writes **"put into ‹DESTINATION› from ‹ORIGIN›"**, so `from` is what
  CLOSES the destination — and that constraint is also what keeps Golgari
  Brownscale out (*"put into your HAND from your graveyard"*), which a
  width-only widening would have wrongly claimed.
- **THE `or`/`and` SPLITTER CANNOT TELL A COORDINATION *INSIDE* ONE PHRASE
  FROM ONE *BETWEEN* TWO TRIGGERS — three defects, and they point opposite
  ways.** Inside an OBJECT phrase the event verb is stranded in a fragment the
  PREDICATE filter then DISCARDS (part 0 has a re-join cure; later parts had
  none — 4 lines lost real tokens). Inside a **CR quantity phrase** (`mana
  value 3 or greater`, `one or more`) the same, and invisible to the re-join
  because **`control` is in `_SUPPLEMENT_VERBS`**, so the scope phrase *"you
  control"* satisfies `TRIGGER_VERB` on almost any clause. Inside a **`while`
  condition** (CR 603.4) it INVENTS a trigger — Preacher of the Schism's
  *"attacks WHILE you have the most life OR ARE TIED for most life"* emitted a
  second delivery for an ability that does not exist. **A census scores a lost
  token and an invented gap identically**, and the routing diff only sees the
  first; the invented one needs the delivery-ROW count.
- **A `--strict` DIFF IS BLIND TO A ROW-LEVEL LOSS ON A ROUTED LINE.** Every
  splitter defect above emitted `[etb, unclassified-trigger]` — the line kept
  a ratified token, so the diff scored it a re-route and the gap census saw
  only "missing vocabulary". Watch `deliveries` and
  `descriptor_unrouted.*`, not `unrouted_lines`, when the change touches how
  rows are PRODUCED rather than classified.
- **AN EXACT-PHRASE GREP OF THE CR IS THE INFLECTION TRAP AIMED AT THE CR.**
  `commit a crime` returned **0** and was one step from being filed as a third
  CR-LAG entry; the CR states it as a GERUND — *"Some cards refer to
  COMMITTING a crime"* (CR 700.13). Same for `expend`, which is not a keyword
  action at all but **CR 700.14**, itself a trigger rule. **CR 700.10–700.16
  is a vein of named mechanics that neither closed keyword list reaches.**
- **A `llm` PROPOSAL SET IS STRUCTURALLY BLIND TO A CLASSIFIER DEFECT.** W3
  was scoped as a Batch API job on its own reasoning that it is *"a CR-LOOKUP
  JOB, not a judgement job"* — which is the argument for a script, not a
  batch. Deriving it instead cost $0 and found **ten defects**, six of them
  branches that could not see a printed form of a token they ALREADY HAD.
  A proposal set is shown *shapes* and asked to name them, so it can only ever
  report gaps: **it names gaps; only reading the classifier finds the ones
  that are not gaps.** Record: `docs/W3-TRIGGER-VOCABULARY-2026-08-07.md` §5.

- **A TOKEN-SCOPED AUDIT IS BLIND TO ITS OWN NEIGHBOURS.** Reading all 280
  lines of the six tokens ratified 2026-08-08 found 2 defects; the routing
  diff on the fix found **4**. The other two had the identical cause —
  `trigger_clause` walking past the condition — but had been handed
  `cast-trigger`, a token outside the audit's scope. Meat Locker proves the
  shape on ONE card: its two faces print the SAME condition and got different
  tokens, decided by their EFFECT text (CR 113.3c). **Read the population,
  then run the diff and read that too.** Neither one alone is the check.
- **A SPECIFICATION IS A CARRIED-FORWARD COUNT WITH A CR NUMBER ATTACHED.**
  All five D8a items had a defective spec, and none was wrong in a way a line
  count could show: three wrong counts (43→30, 12→3, and one right by
  accident), **one wrong CR anchor** (the sheet cited 728.1 for day–night;
  CR 728 is Rad Counters and Day and Night is CR 731), and **one hidden second
  CR rule** (Room doors is 709.5h "unlock this door" AND 709.5i "FULLY unlock
  a Room" — a different event on different cards). Every wrong count came from
  counting the PHRASE instead of the EVENT: 103 of 110 `flip` lines and 23 of
  26 `is exiled` lines carry the words in their effect. **Re-measure the
  anchor and the partition, not just the number.**
- **THE SAME RATIFIED TEST GIVES OPPOSITE ANSWERS, AND THAT IS IT WORKING.**
  D3f produced ONE token for day–night — every line prints "day becomes night
  **or** night becomes day" in a single clause, so a split yields two axes with
  identical membership — and TWO for coin flip, because Karplusan Minotaur
  prints win and lose as separate abilities that do different things. CR 705.2
  closing the outcome set at two is also what lets `coin-flip-lost-trigger`
  stand at ONE member without being a one-card token: it is reserved by an
  enumeration, the `noncombat-damage-to-planeswalker` pattern. **Let the corpus
  decide the split; do not carry a preference between rows.**

- **A PROBE DEFECT WAS THE ONLY DEFECT CLASS GUARDED BY PROSE, WHICH IS WHY IT
  WAS THE ONLY ONE STILL RECURRING.** Measured 2026-08-09
  (`docs/SYSTEM-SELF-TEST-2026-08-09.md`): every class that got a TOOL stopped —
  ruled slugs (Gate 3), prior art (Gate 3b), text loss (conservation),
  unreachable options (visibility), wrong-since-forever tokens (ground truth),
  baseline drift (the ratchet). Probe defects got a paragraph, and reached 21.
  **And "the same cure" was a story**: they have at least FOUR causes —
  re-implementation, assumed vocabulary, overlapping classes, over-narrow
  filter — so one slogan could never prevent them. `experiments/foundry_probe.py`
  is the mechanism: `p.corpus()` / `p.rows()` (A), `p.domain()` / `p.vocab()`
  (B), `p.assert_disjoint()` (C), `p.must_capture()` (D). Every guard HALTS.
  **Write probes with it** — it is shorter than hand-rolling, which is the only
  thing that has ever worked here.
- **A GUARD THAT HAS NEVER BEEN SHOWN TO FAIL IS NOT KNOWN TO BE A GUARD.** All
  eight Gate 2 checks were broken on purpose 2026-08-09. Six caught it and
  failed. **`foundry_definition_drift.py` and `foundry_ruling_registry.py`
  DETECT AND EXIT 0** — they are reporters listed as gates, so never read their
  exit code as a verdict. And **three of the eight negative controls were
  mis-aimed**, each first reading as "this gate is broken": `C1a` cannot fire on
  an axis naming neither a counter nor a token, and family sweep only reacts to
  an axis a ratified family actually references. Aim a negative control at the
  code path, not at the tool's name.
- **THE ROUTING DIFF CORRECTS THE ROUTING; NOBODY CORRECTS THE NUMBER.**
  `foundry_recorded_numbers.py` re-derives every count grammar §2 asserts and
  found two wrong on its first run — `player-loses-game-trigger` 5→**7** and
  `coin-flip-won-trigger` 6/5→**6/6** — both written into ratified law the same
  session their probe defect was found and fixed. A stale number in a handoff is
  a note; **a wrong number in §2 is a wrong premise inside the document the
  extractor parses its vocabulary from at run time.** Only 7 of 64 rows carry a
  checkable count, so this is a floor, not a clean bill.

- **A REJECTED TERM IN BACKTICKS IS INGESTED AS RATIFIED VOCABULARY.** Third
  instance of "a markdown document is an API", and the first one outside §2's
  table. Every section parser (`foundry_probe.vocab`, the reparse, the synonym
  checker) harvests backticked identifiers from PROSE, so writing *"NOT
  `produce-mana`"* mints `produce-mana`. Caught within one run on 2026-08-09:
  `foundry_synonym_collision.py` reported 21 members colliding against a
  "ratified verb" that existed only inside its own rejection — **and the
  sentence written to explain the trap re-introduced it the same way.**
  **Rejected alternatives go in "quotes", never in `backticks`.** A regex
  cannot reliably find these after the fact: a detector built for it flagged
  13, of which several were real ratified values (`defending-player`,
  `two-target`) that merely sit near the word BANNED, which applies to a
  different term in the same sentence. The convention is the control; the
  detector is not.

- **SIZING A RATIFICATION BY THE SLUG PREFIX OVER-COUNTS IT, TWICE MEASURED.**
  "38 `etb-` axes need a ruling" was really **5** — only those are
  replacement-dominant, and the tell was printed in the slug all along
  (`-with-`/`-as-` is CR 614.1c, a bare verb is CR 603.6a). "89 membership
  errors" was really 27 prefix-imprecision + 59 needing a home + 3 spells.
  **Measure per item before quoting a population to Captain**; a prefix is a
  hypothesis about a population, not the population.
- **A CODEBOOK MUTATION CAN PROPAGATE A PRE-EXISTING DEFECT INTO A NEW AXIS,
  WHERE IT LOOKS ORIGINAL.** On 2026-08-09 a re-home moved a member whose
  evidence quote was a TOKEN onto a new `-plus1-counter` axis (§8 rule 3).
  The membership was already wrong on its SOURCE axis; the move would have
  given the defect a fresh, innocent-looking home. `definition_drift` caught it
  as `C1b 1 → 2` — **only because it was ratcheted into a real gate that same
  morning; the day before it would have exited 0.** The mutation drill is:
  backup → `--dry-run` and READ the conservation line → execute → **re-run
  `foundry_gate2.py` and expect it to find something** → revert from the
  verified backup if it does. The revert is free; that is what the backup law
  buys.

- **A JOIN CAN BE PLUMBED CORRECTLY AND STILL BE THE WRONG SIGNAL, AND ONLY A
  PRE-COMMITTED PREDICTION SET CAN TELL YOU WHICH.** The codebook wire works on
  the first try — one call site, both controls byte-identical, the DF-ceiling
  prediction exact. It still fails, because `derived_agreement` rewards
  MEMBERSHIP and an absent member means *"nobody has reviewed this card yet"*,
  not *"this card is unlike the anchor"*. Beast Within's three functional twins
  (all printing *"Destroy target nonland permanent. Its controller creates…"*)
  fell #5/#6/#7 → #19/#20/#21, displaced by a 172-member `targeted-destruction`
  bucket that qualified past `DERIVED_QUALIFY_DF_CEILING=172` **by a margin of
  exactly zero**. A broad axis is a WORSE discriminator than the verbatim text
  it outranks. **Write the correct neighbours down before running** — every one
  of those movements would have read as progress against a list written after.
- **A DISPLAYED LIST CAN BE ALPHABETICAL AND LOOK LIKE A RANKING.** Tier 3
  sorts `(-score, name)`, and Rampant Growth's shipped top-10 is a slice of a
  **44-row score tie** — so the product shows the alphabet, `A-` prefixed
  Alchemy variants first. Measure the TIE BLOCK, not just the order: a change
  that "improves the ranking" of a tie block improved nothing that was ranked.
  Cousin trap in the data: **88 Alchemy memberships sit on 51 active axes, 48
  of them duplicate pairs with their own paper twin**, inflating every axis DF —
  which feeds `idf` *and* the 172 ceiling — against the ratified "paper rows
  preferred over A- variants".

- **A DISPLAY STRING READ AS DATA SILENTLY CHANGES THE CONCLUSION.**
  `foundry_object_lattice.measure()["residual"]` **truncates its clause to 90
  characters** — it exists to be printed. Consuming it as data drops the
  trailing `from <zone>` and reclassifies the clause. Same family as "a
  generated artifact is not the CR": ask what a field is FOR before joining on
  it.
- **A REMINDER-TEXT SEARCH FINDS THE OPPOSITE OF WHAT IT LOOKS FOR.** Spree
  prints *"Spree (Choose one or more additional costs.)"*, so a naive
  `choose one` search matches the REMINDER and files Spree cards as
  **mutually exclusive modes** — the exact inverse of the truth, since Spree
  modes are additive. Two cards were classified that way during the locality
  arc. §6a strips reminder text; a modality test must run AFTER the strip, and
  `IN-CARD-SEPARATION-CENSUS-2026-08-06.md` §6a-vs-CR-700.2 is the standing
  tension.
- **A BEFORE/AFTER DIFF CANNOT SEE A WRONG VALUE IN A FIELD THAT DID NOT EXIST
  BEFORE.** The locality backfill's `verify()` checked added / removed /
  **changed** addresses, and `changed` was **structurally dead**: the pre-state
  carried zero addresses, so `set(was) & set(now)` is empty and no coordinate
  can ever differ from a value that was never there. NC3 mutated a stored
  coordinate by +99 and `verify` returned **clean** — added still equalled the
  planned count, because a count cannot see a substitution (the `len() >= 15`
  halt-guard, one layer up). **The cure is to compare against the DECLARATION,
  not against the past**: the applied result must equal the plan
  coordinate-by-coordinate. Generalises past this migration — **any additive
  migration's `changed` arm is dead on arrival, and it is the arm that looks
  most like real diligence.** The `changed` check is kept for the re-address
  operation, which is unbuilt and would have a non-empty `was`.
- **A MODULE RUN AS `__main__` IS A SECOND, SEPARATE COPY OF ITSELF, AND
  MONKEYPATCHING THE WRONG ONE READS AS A PASSING TEST.** `foundry_locality.py`
  run as `__main__` does `import foundry_det_pass`, which imports
  `foundry_locality` **afresh** — so two live copies exist, and
  `globals()["resolve"] = ...` patched the copy nobody calls. The write-boundary
  fixture reported a **green** result it had never exercised. **Patch the module
  the code under test actually reaches** (`fdp.fl.resolve`), never your own
  globals, whenever the patch has to cross a module boundary. Note the asymmetry
  that hides it: patching `fc.canonicalize_self_reference` in the same fixture
  DID work, because `foundry_common` is never `__main__` and therefore has
  exactly one instance — so a fixture file can have one working patch and one
  silently dead patch side by side. Cousin of "a probe is code and gets audited
  like code": here the probe agreed with itself twice.

## Out of scope — check before raising a finding

**`docs/OUT-OF-SCOPE.md` is a DECLINE REGISTER, not a backlog.** Attractions /
`Visit` (22 cards, one set), art tags (outside evidence law — quotes come from
oracle text only) and Prototype (21 cards) were measured and deliberately
declined. If it is in that file, report it as *declined*, never as *open*, and
do not re-derive it. Captain's criterion decides membership: **judge by
deck-building relevance, not textual frequency.**

## Reference

- **✅ THE CR REFRESH IS DONE — `docs/CR-REFRESH-2026-08-09.md`.** The pipeline
  reads the **2026-08-07** edition, tracked in THIS repo, through one
  normalizing loader (`experiments/foundry_cr.py`); the file itself is
  pristine, as ratified. **Never `path.read_text()` a CR — always
  `foundry_cr.text()`**, or the bold rule markers (`**605.1a.**`) make every
  enumeration return empty. **0 of 61,383 ability lines moved**; the only
  movement was CR 702 keyword names 193 → **194** and keyword homes 150 →
  **151**, both from the new CR 702.195 Storied. `MTJ_CR_PATH=<file>` runs
  everything against another edition — that is how a refresh gets verified as
  a comparison, and how the loader was proven a no-op on the June CR before the
  diff was believed. **The 2026-08-07 file is an LLM-reformatted DERIVATIVE and
  it arrived with encoding damage** — 7 mojibake characters in CR 206.3a
  (`Juzám` → `JuzÃ¡m`). Captain ruled 2026-08-09: **repaired at read time**, in
  its own pass, DERIVED (`.encode("latin-1").decode("utf-8")` is the inverse of
  the corruption) rather than typed, and pinned by the repaired rule coming out
  **byte-identical to the 2026-06-19 edition**. A repair is a SUBSTITUTION and
  normalization's law is PURE DELETION, so they cannot share a pass — and the
  undeclared-damage guard must run BEFORE the repair, or it cannot tell "never
  damaged" from "quietly repaired".
- **THE MANA RULE IS CR 605.1a AND IT HAS NO CODE PATH HERE**
  (`docs/CR-REFRESH-MANA-ABILITIES.md`, resolved 2026-08-09). A mana ability now
  also requires that *"its cost and effect don't move any card to or from a
  library"*. Nothing parses 605.1a — grammar §2 cites it to EXPLAIN a §1
  qualifier that is matched as printed card text. CR 106.4 / 106.6 / 106.12 are
  byte-identical across editions, so `tapped-for-mana-trigger` (58), `add-mana`
  (1,746) and `restricted-purpose-mana` (217) did not move. **A prediction that
  a rules change would move a branch's PREMISE was aimed at the right rule; the
  premise just is not encoded anywhere.** Check that before building on it.
- **THE CR-LAG REGISTER SURVIVED THE REFRESH, AND BOTH ENTRIES WERE LYING ABOUT
  WHY.** `chorus` (CR 205.3k) and `N or less` (CR 706.3a) each said *"the real
  fix is to refresh the CR snapshot"*; the refresh happened and both rules are
  byte-identical. **The CR is behind the printed cards — the snapshot was never
  behind the CR.** Both comments are corrected in place, because a register
  entry naming a fix nobody has done reads as unstarted work. And the direction
  now runs both ways: CR 701.70 Recruit and CR 702.195 Storied have **0**
  attested corpus lines, so the corpus is older than the CR.
- **A GENERATED ARTIFACT IS NOT THE CR, AND IT MADE A REFRESH DIFF READ CLEAN.**
  `cr_action_terms()` reads `docs/cr-checks.json`, so the first post-refresh
  routing diff never exercised the CR 701 change and its **0 moved lines** was
  meaningless. Regenerating it moved 262 → 264 terms. **Re-run every generator
  that caches a CR-derived list before believing a CR diff** — and then verify
  the zero positively: `recruit` DID enter `TRIGGER_VERB`, and it moves nothing
  only because all 3 corpus lines printing it carry it inside a CARD NAME.
- **⚠ DEFERRED, CAPTAIN'S CALL: MEMBERSHIP EXCLUSIVITY.** Captain, 2026-08-09:
  *"membership should probably be exclusive… a deck that cares about gaining
  life will not care about losing life most of the time."* **Deferred until the
  tools exist and can be tested card by card**, not dropped. Measured before
  deferring: **78.8% of cards are already on exactly one axis**; the 21.2% on
  2+ are MULTI-ABILITY cards (Kayla's Command is on 5 — modal, fixed-lifegain,
  tutor, create-token), so global exclusivity would force picking one of four
  things a card genuinely does. **The tension is real but narrower than the
  rule**: it is about a COMPOUND-EVENT ability ("gain or lose life") joining
  both single-event axes, which was a suggestion of mine and not the 2026-08-02
  ratification. And the two planned tools want opposite answers — a budget
  swapper wants exclusivity (a compound card is a bad substitute), a
  recommender wants inclusion (it genuinely synergises). **Do not implement
  exclusivity globally; scope it within an effect family and measure the blast
  radius first.**
- **START HERE AFTER A BREAK: `docs/PICK-UP-HERE.md`** — undated, stably
  named, says what to audit FIRST and what not to touch.
- **Current state + READING MANIFEST: `docs/SESSION-HANDOFF-2026-08-09.md`**
  — start here, always. It lists every markdown a session needs, tiered by
  what you are about to touch. (This line goes stale; the authoritative
  pointer is Gate 1 of `docs/SESSION-START-PROCEDURE.md`.)
- **A WITHDRAWN DECISION LEAVES A SHADOW ON EVERY OTHER ITEM ON ITS SHEET.**
  D2/D3 (CR 701/702 keyword events) was sent back to Captain; D8 was then
  scoped as "nine smaller CR classes" and **five of them turned out to BE
  CR 701/702 keyword terms** — monstrosity, level-up, attach, phasing,
  dungeon, 55 of its 134 lines. Working it as written would have minted the
  withdrawn family one token at a time, which is design goal #1's
  duplication or a back-door ratification. **After withdrawing an item,
  re-test every REMAINING item for overlap with it** — the sheet was
  partitioned before the withdrawal, so its partition is stale by
  construction.
- **RANK A WORK QUEUE BY DECK-BUILDING RELEVANCE, NOT BY LINE COUNT.**
  Captain's ratified criterion, and a queue sorted by lines silently
  applies the one the rule names as wrong. Rooms (a build-around set
  mechanic), day–night (werewolves) and coin flip (Krark) are archetypes;
  `player loses the game` is marginal at any count. **And a line count
  UNDER-states the gain**: an unrouted header keeps its MODES unrouted, so
  ratifying D5 routed one header and three bullets inherited for free.
- **A STANDING WARNING'S NUMBER IS STILL A CARRIED-FORWARD COUNT.**
  `PRE-STEP-2-AUDIT`'s *"1,883 wrong answers that READ as resolved"* gates
  W4, and it was measured on 2026-08-04 against six enumerated causes that
  have each since been fixed. Re-measured: **1,883 → 4**, and the 4 are the
  Siege cycle behaving correctly (the CR 614.1c *choice* is the replacement;
  the chosen `• Mode — <static>` must not inherit it).
  `experiments/foundry_blanket_risk.py` is the reporter. **Re-measure the
  warning, not just the work it guards** — but note a low number says the
  ENUMERATED causes are gone, never that the rest is correct.
- **W3's trigger-vocabulary decision sheet + the CR partition of the
  `unclassified-trigger` population: `docs/W3-TRIGGER-VOCABULARY-2026-08-07.md`.**
  Re-measure with `python3 experiments/foundry_w3_census.py` — it partitions
  every unrouted trigger line by the CR rule that decides it (87.9% of 818)
  and mints nothing. D1–D9 are the pending ratifications; **D4 (CR 603.8
  state triggers) is the cleanest and shrinks the residual too.**
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
**One deliberate exception now, read by absolute path:
`docs/PHASE-2-COMPLETION.md`.** The Comprehensive Rules used to be the other
one; as of the 2026-08-07 refresh they are TRACKED HERE
(`docs/MTG_Comprehensive_Rules_2026-08-07_LLM.md`) and reached only through
`experiments/foundry_cr.py`, which owns both the location and the formatting.
The 2026-06-19 edition stays in the site repo as `foundry_cr.PRIOR_CR_PATH`,
never read by the pipeline, so a refresh can be verified as a comparison.
