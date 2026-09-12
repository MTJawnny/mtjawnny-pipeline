# Objective 2 — S16A Adversarial Gold-Suite Preflight Result

Status: **COMPLETE EVIDENCE PACKAGE / NOT IMPLEMENTATION AUTHORITY**  
Date: 2026-09-12  
Accepted implementation head measured: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Planning base: `36655d59860d812bdbd8f352ad9d7176604c7797`  
Evidence branch: `preflight/s16a-gold-suite-2026-09-12`  
Controls: `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`

## Verdict

Objective 2's preflight bar is met for the Captain-approved Gate #0 Foundry population. The package contains a mechanically derived raw-corpus census, a **33-card development gold set** selected without observing current parser output, an **18-card deterministic unlabeled holdout**, **18 falsifiable negative controls**, an implementation-neutral schema, semantic coverage/unsupported registers, provenance, and a draft future acceptance contract.

This result **does not authorize S16A implementation**, migration advancement, S16B, merge, deploy, publication, authority succession, AQ4 work, or codebook mutation.

## Input identity and scope

- Raw pinned source: **38,233** unique Oracle records.
- Captain-approved Gate #0: include a card iff at least one Scryfall legality value is `legal` or `restricted`.
- Benchmark universe: **32,557** cards.
- Excluded nowhere-legal population: **5,676** cards.
- Uploaded R2 archive container SHA-256: `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217` (22,735,516 bytes).
- Decompressed content SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c` (179,284,334 bytes).
- Repository-selected operational container SHA-256 remains `2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872`; the uploaded R2 copy is decompressed-content identical and differs only as a gzip container.
- Comprehensive Rules edition used: effective **2026-08-07**, SHA-256 `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b`.

The Gate #0 correction materially changes one historical parser-seam population. The raw corpus contains **Devoted Mardu**, the historical nested-reminder witness, but it is legal in no Scryfall format and is excluded. The live gated nested-parenthesis-depth≥2 population is therefore **0**, not 1. A synthetic negative control remains appropriate for the parser seam; Devoted Mardu is not benchmark truth for the product population.

## Independence method

1. Load the pinned raw JSONL directly and reproduce Gate #0 from the accepted legality rule.
2. Pass A: enumerate structural populations from Scryfall record structure and raw Oracle text only.
3. Pass B: stratify materially different rules shapes before choosing witnesses: modal cardinality, repeat/state memory, chooser, weighted modes, cost-before-effect, components/layouts, dependencies, target relationships, zones, timing, quoted abilities, and provenance traps.
4. Select development witnesses from those measured populations using Oracle/CR structure only; retain the three required seeds.
5. Precommit an unlabeled holdout using deterministic seed `S16A-GOLD-2026-09-12-v1`.
6. Reconcile historical incidents only after census and selection. Historical counts are not current measurements.

**No current Foundry semantic-parser output was inspected to choose witnesses or labels.**

## Pass A — measured census

The machine census records **66 structural/punctuation families**, discovery rules, status (`certified`, `exhaustive_*`, or `candidate*`), measured card population, and high-overlap populations in `S16A-STRUCTURAL-CENSUS.json`.

High-value measured populations include:

| family | cards | interpretation |
|---|---:|---|
| CR-700.2 certified modal population | **748** | mechanically certified modal cards in Gate #0 |
| modal choose-up-to | 21 | exact phrase inside certified modal population |
| modal choose-any-number | 12 | exact phrase inside certified modal population |
| modal choose-X | 1 | exact phrase inside certified modal population |
| repeat-mode permission | 22 | `same mode more than once` |
| stateful mode restriction | 22 | `hasn't/has not been chosen` family |
| opponent mode chooser | 3 | mode chooser specifically; not choices inside a mode |
| pawprint modal | 5 | CR 107.18 / 700.2i form |
| Spree | 21 | CR 702.172a modal + mode-specific costs |
| Tiered | 7 | CR 702.183a modal + mode-specific costs |
| cost-before-effect modal | 28 | certified Spree/Tiered subset |
| modal header continuation | 81 | certified modal headers whose governing instruction continues beyond a simple em-dash header |
| printed bullet cards | 737 | all product bullet structures |
| printed bullet nonmodal | 15 | proof that bullet ≠ mode |
| activated top-level colon candidate | 8,325 | depth/quote-aware colon census |
| multi-part activated-cost candidate | 3,524 | top-level activation with comma before colon |
| explicit additional cost | 351 | exact phrase family |
| reflexive `when you do` | 370 | high-precision CR 603.12 population |
| linked-ability candidate | 190 | reproducible lexical discovery net; not an exhaustive CR 607 enumerator |
| replacement `instead` | 1,178 | high-precision CR 614 discovery population |
| prevention `prevent` | 493 | high-precision CR 615 discovery population |
| same-paragraph multiple targets | 637 | high-value target graph population |
| explicit `then` sequence | 3,833 | high-precision sequence evidence |
| multi-sentence paragraph | 10,663 | broad composition population |
| multiple zone terms | 6,795 | discovery population, not a source→destination parser |
| quoted text | 1,986 | punctuation/ownership population |
| quoted colon | 1,004 | granted/quoted ability adversarial population |
| repeated identical paragraph | 109 | provenance-ambiguity population |
| multi-face/component cards | 836 | exact structured-layout population |
| Adventure | 146 | exact layout |
| transform | 396 | exact layout |
| Room | 30 | exact layout |
| Saga | 163 | exact layout |
| Class | 38 | exact layout |
| leveler | 25 | exact layout |
| Station | 34 | exact layout |
| legal Prototype mechanic | 21 | retained because these cards pass Gate #0 |
| nested parentheses depth≥2 | **0** | no live Gate #0 witness |

### Modal reconciliation

Earlier provisional broad lexical counts such as a simple `choose one` tally are **not acceptance populations**. The final benchmark uses the 748-card CR-700.2-certified structural population plus narrower semantic strata. This avoids mixing named choices, nonmodal bullet tables, and other English uses of “choose” into modal truth.

## Pass B — development gold witnesses

The machine gold is partitioned across `S16A-GOLD-SUITE-DEV-PART-1.json` through `PART-3.json`, with `S16A-GOLD-SUITE-DEV.json` as the index. It contains **33 witnesses**. Oracle text is not copied into git: each witness pins `oracle_id`, whole Oracle projection SHA-256, face/paragraph coordinates, and paragraph SHA-256. Exact source wording is recovered from the pinned corpus.

The selected witnesses and protected relationship classes are:

- **Cryptic Command** — exactly two distinct modes; mode-local targets; selected modes remain separate.
- **Zuko, Conflicted** — parent trigger/life loss; four statefully restricted modes; fourth-mode exile→return/control sequence. The benchmark intentionally does **not** invent a temporal reset window absent from Oracle text.
- **Monument to Endurance** — discard trigger; per-turn mode memory; official exhausted-choice behavior.
- **Season of Gathering** — weighted pawprint budget; repeat permission; choice during resolution.
- **Three Steps Ahead** — Spree; mode-specific additional costs before effects.
- **Vincent's Limit Break** — Tiered; continuation sentence; quoted delayed/death ability remains quoted structure.
- **Library of Lat-Nam** — opponent, not controller, chooses the mode; delayed draw vs search line.
- **Jeska's Will** — conditional expansion from choose-one to choose-both.
- **Eldrazi Confluence** — exactly three selections with repeat permission; sequence and quoted token ability.
- **Kalitas, Bloodchief of Ghet** — multi-part activation cost; payload; `dies this way` dependency and referent.
- **Heart-Piercer Manticore** — optional resolution action and reflexive `when you do` trigger.
- **Bag of Holding** — linked abilities; `exiled with this artifact`; multi-part activation cost.
- **Rest in Peace** — ETB trigger distinct from static replacement effect.
- **Martyr's Cause** — sacrifice cost distinct from prevention payload and duration.
- **Suffocating Blast** — two cumulative effects and two target roles; deliberately nonmodal.
- **Brazen Borrower // Petty Theft** — Adventure component ownership.
- **History of Benalia** — Saga chapter ownership/timing.
- **Barbarian Class** — level-gated replacement/trigger/static abilities.
- **Coralhelm Commander** — level bands and band-local abilities.
- **Pinnacle Kill-Ship** — Station threshold plus reminder-colon ownership trap.
- **Steel Seraph** — legal Prototype mechanic and nonmodal “your choice of” distinction.
- **Fire // Ice** — split-card component separation and divided/multiple targets.
- **Delver of Secrets // Insectile Aberration** — transforming face boundary.
- **Food Fight** — static grant containing a quoted activated ability with internal colon.
- **Hound Tamer // Untamed Pup** — identical activated paragraph on two faces; provenance cannot rely on quote identity alone.
- **Final Fortune** — extra turn plus delayed end-step loss; temporal dependency.
- **Hylda of the Icy Crown** — optional payment during trigger resolution; reflexive trigger; subsequent modal choice.
- **Eldrazi Displacer** — activation, exile→return sequence, owner/control and zone conservation.
- **Cloud's Limit Break** — Tiered costs with one/any-number/all target cardinalities.
- **Moldering Gym // Weight Room** — Room/door ownership, manifest dependency, repeated reminder provenance.
- **Active Volcano** — classic mutually exclusive cross-action-family modal flattening witness.
- **Requisition Raid** — Spree mode-specific costs and target scope.
- **See Double** — parent restriction, conditional choose-both, spell-target vs creature-target separation.

## Semantic relationship coverage matrix

| relationship | development witnesses |
|---|---|
| ownership / face / component | Brazen Borrower, Hound Tamer, Moldering Gym, Delver |
| delivery / ability type | Heart-Piercer Manticore, Rest in Peace, Food Fight, Barbarian Class |
| costs / payment timing | Three Steps Ahead, Vincent's Limit Break, Kalitas, Hylda, Cloud's Limit Break |
| modal cardinality / exclusivity | Cryptic Command, Active Volcano, Jeska's Will, See Double |
| repeat / state memory | Eldrazi Confluence, Zuko, Monument, Season of Gathering |
| chooser / actor scope | Library of Lat-Nam, Zuko |
| target attachment / sharing | Cryptic Command, Suffocating Blast, Fire // Ice, Cloud's Limit Break |
| conditions / dependency | Kalitas, Heart-Piercer Manticore, Jeska's Will, Hylda |
| sequence / temporal dependency | Eldrazi Displacer, Final Fortune, Library of Lat-Nam, Eldrazi Confluence |
| zones | Bag of Holding, Rest in Peace, Eldrazi Displacer, Brazen Borrower |
| quoted / granted abilities | Food Fight, Vincent's Limit Break, Eldrazi Confluence |
| replacement / prevention | Rest in Peace, Martyr's Cause, Barbarian Class |
| chapters / levels / thresholds | History of Benalia, Barbarian Class, Coralhelm Commander, Pinnacle Kill-Ship, Steel Seraph |
| repeated-text provenance | Hound Tamer, Moldering Gym |

## Holdout precommitment

`S16A-HOLDOUT-PRECOMMIT.json` reserves **18 unlabeled cards** using fixed seed `S16A-GOLD-2026-09-12-v1`. For each fixed source stratum, eligible `oracle_id`s are sorted by `SHA256(seed|stratum|oracle_id)` and the first unused card is reserved.

Only identity, source stratum, and Oracle projection hash are exposed. No expected semantic labels are stored. Membership must not change because a future implementation passes or fails a card.

## Negative controls

`S16A-NEGATIVE-CONTROLS.json` defines **18 corruptions**, each with a named invariant that must go red. The catalog covers cost deletion; choose-two→one; modal distinctness; repeat permission; state memory; target reassignment; modal flattening; linked-effect splitting; component merging; condition relocation; zone changes; payment timing; continuation deletion; face deletion; quoted punctuation; nested-reminder flattening; delayed-trigger collapse; and reminder-colon ownership.

The nested-reminder control is explicitly **synthetic-only** because Gate #0 contains zero live nested-parenthesis-depth≥2 cards.

## Unsupported / unrepresented / census-risk register

- **Nested reminder text:** zero Gate #0 cards. Keep a synthetic parser guard; do not promote nowhere-legal Devoted Mardu into product benchmark truth.
- **Linked abilities:** 190-card candidate population is a discovery net, not an exhaustive CR 607 enumerator. Bag of Holding is a certified gold case; unknown shapes must be separately adjudicated or refused.
- **Resolution payments:** 1,357 lexical candidates are intentionally broad. Hylda is a certified witness; the population count is not a claim that all 1,357 are resolution payments.
- **Target graph:** 637 same-paragraph multiple-target cards are candidates. Token count alone cannot establish shared/separate target identity.
- **Independent vs sequential instructions:** `then` is high-precision sequence evidence, while multi-sentence text is a broad composition net. Punctuation alone does not establish independence.
- **Zone relations:** 6,795 cards mention multiple zones; that is discovery evidence, not a source→destination parse.
- **Quoted text:** 1,986 quoted cards / 1,004 quoted-colon cards are ownership/punctuation populations, not claims that every quote grants an activated ability.
- **Nonmodal bullets:** 15 Gate #0 cards contain bullets but are outside the certified modal population. Bullet structure must never be treated as synonymous with modality.

## Provenance register

- `refoundation/path-e/input-lock.json` — selected corpus byte identity and R2 archive relationship.
- `config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md` — rules authority, especially 107.18, 115, 601.2b, 602.1a, 603.7/603.12, 607, 614, 615, 700.2a–i, 702.172a, 702.183a, and layout rules 709/711/712/714/715/716/718/721/722.
- `docs/architecture/CARD-READING-PRECISION-ACCEPTANCE.md` — acceptance dimensions only; not gold labels.
- preserved `FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md` — historical context/flattening evidence; historical counts not reused.
- `docs/PUNCTUATION-RESCAN-2026-08-06.md` — historical punctuation/modal evidence; current counts remeasured.
- Wizards official Avatar: The Last Airbender release notes — Zuko card-specific/controller-choice evidence.
- Wizards official Aetherdrift release notes — Monument exhausted-mode behavior.
- Wizards official Bloomburrow release notes — Season of Gathering resolution-choice behavior.
- Wizards official FINAL FANTASY release notes — Tiered/Vincent evidence.

## Draft S16A benchmark acceptance contract — NOT AUTHORIZED

A future S16A implementation may claim benchmark acceptance only if:

1. it consumes this pinned Gate #0 corpus identity or an explicitly re-ratified successor and reports corpus drift;
2. every development witness either satisfies every protected relationship and provenance coordinate, or explicitly refuses an unsupported shape; silent approximation fails;
3. all 18 negative controls are demonstrated to fail the corresponding invariant, then restored byte-exact;
4. text, structural ownership, context/cost, modal exclusivity, dependency, target attachment, cardinality, zones, actor/chooser scope, and provenance are conserved;
5. implementation output does not alter gold membership or labels; any gold correction requires a recorded provenance error and review;
6. holdout membership remains byte-identical until the implementation is frozen for evaluation;
7. no witness card name or `oracle_id` may be special-cased;
8. unsupported shapes are surfaced explicitly rather than coerced into a nearby representation; and
9. S16B may not treat a semantic coordinate as trustworthy until S16A acceptance for that coordinate is demonstrated.

This contract is **NOT AUTHORIZED** by completing Objective 2.

## Evidence files

- `S16A-STRUCTURAL-CENSUS.json`
- `S16A-GOLD-SUITE-SCHEMA.json`
- `S16A-GOLD-SUITE-DEV.json`
- `S16A-GOLD-SUITE-DEV-PART-1.json`
- `S16A-GOLD-SUITE-DEV-PART-2.json`
- `S16A-GOLD-SUITE-DEV-PART-3.json`
- `S16A-HOLDOUT-PRECOMMIT.json`
- `S16A-NEGATIVE-CONTROLS.json`
- `S16A-OBJECTIVE2-RESULT.md`

No card-corpus file is committed. No parser/runtime/package/codebook/authority/AQ4 file is changed. No accepted implementation ref is moved and no merge is authorized.
