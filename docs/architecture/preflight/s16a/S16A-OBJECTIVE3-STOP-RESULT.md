# S16A Objective 3 Parser-Seam Audit — STOP Result

Status: **STOP / INCOMPLETE**  
Objective: **3 of 5**  
Implementation authorization: **NONE**  
Objective 4 activation: **NO**

## Durable anchors verified

The Manager-side session independently reconstructed the durable control plane from GitHub Issue #1 before doing research.

- latest selected checkpoint: `K-20260912-PREFLIGHT-OBJECTIVE3-ACTIVE`
- checkpoint comment: `5647210411`
- active task: `PREFLIGHT.OBJECTIVE3.S16A-PARSER-SEAM-AUDIT`
- task comment: `5647209355`
- accepted implementation head `h`: `9f92039eb9c7132a351576c31472eb30a2957a67`
- Objective-3 planning branch: `preflight/objective3-parser-seam-2026-09-12`
- Objective-3 planning head: `b01848d63bb40a7025a3ab0cd287c479a13dfd22`
- Objective-2 evidence head: `fc99f3bdf0503bd325f0b644771895c05940ad15`

No newer valid `K` superseding Objective 3 was found.

## Required source package read

The session read the required planning/ownership package and the completed Objective-2 evidence package, including:

- root `CLAUDE.md` at accepted `h`;
- `PREFLIGHT-PICK-UP-HERE.md`;
- `PREFLIGHT-OBJECTIVES-1-5-2026-09-11.md`;
- `S16A-PARSER-SEAM-AUDIT-PREFLIGHT-PLAN.md`;
- `OBJECTIVE-3-FRESH-CHATGPT-PREFLIGHT-PROMPT.md`;
- `CARD-READING-PRECISION-ACCEPTANCE.md`;
- `S10-CARD-TEXT-OWNERSHIP-DECISION-2026-09-11.md`;
- Objective-2 result, census, schema, development suite and all three manifest parts, negative controls, and holdout precommit.

The Objective-2 holdout remained unlabeled. No holdout semantics were inferred or used.

## Objective-2 corpus identity expected for present-tense card-level claims

- raw Oracle records: `38,233`
- Gate #0 product/benchmark population: `32,557`
- nowhere-legal excluded records: `5,676`
- decompressed pinned corpus SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`

The Objective-2 structural census itself is accepted evidence and remains usable as an independent mechanically discovered population lattice. Examples include:

- CR-700.2 modal population: `748`
- modal-header continuation: `81`
- top-level activation-colon candidates: `8,325`
- quoted-ability-colon candidates: `1,004`
- quoted-text cards: `1,986`
- repeated-identical-paragraph cards: `109`
- pawprint: `5`
- Spree: `21`
- Tiered: `7`
- nested-parenthesis depth >=2 in Gate #0: `0`

Those are Objective-2 measurements, not newly generated Objective-3 differential results.

## STOP condition fired

The exact pinned corpus bytes were not available in this execution environment.

The corpus is correctly absent from Git. Repository policy does not permit silently substituting a newer Scryfall download. File-library lookup available to this session did not provide the pinned corpus bytes, so the expected decompressed SHA could not be independently reproduced before running card-level comparisons.

The Objective-3 plan requires a STOP when:

> accepted Gate #0 corpus identity cannot be established for card-level differential claims

Therefore this session did **not** run or claim current full-population parser differentials.

Important interpretation:

- `0` new current differential runs were completed because the input precondition failed.
- This does **not** mean `0` divergences.
- No new seam is classified S1 merely because historical tests or examples matched.
- Historical counts remain historical evidence only.

## Static source/caller census completed before STOP

A tracked partial inventory was committed on a separate evidence branch:

`docs/architecture/preflight/s16a/S16A-OBJECTIVE3-STATIC-INTERPRETER-INVENTORY.json`

A tracked partial concept/seam register was also committed:

`docs/architecture/preflight/s16a/S16A-OBJECTIVE3-PARTIAL-SEAM-REGISTER.json`

The static register contains `28` concept rows:

- `9` provisional S0 single-owner rows;
- `3` S2 intentional-representation/task-boundary rows;
- `13` S3 unproven-duplicate/cross-layer rows;
- `3` S5 silent-loss/silent-invention risk rows;
- `0` new S1 rows;
- `0` current-measurement S4 rows.

These classifications are deliberately conservative. S0/S2 are based on direct accepted-source ownership/delegation evidence. S3/S5 indicate where full applicable corpus measurement is still required.

## Most important static findings

### 1. Permanent ownership is real, but compatibility does not mean legacy semantics are dead

Accepted permanent owners are visible:

- face/full-card structure: `src/mtj_foundry/corpus.py`;
- neutral Oracle recognition/normalization capability: `src/mtj_foundry/oracle_text.py`;
- delivery semantics: `src/mtj_foundry/mtg/shapes/delivery.py`;
- semantic owner/evidence locality: `src/mtj_foundry/mtg/shapes/locality.py`;
- target noun/class semantics: `src/mtj_foundry/mtg/shapes/target_classes.py`;
- mechanical regex/evidence matching: `src/mtj_foundry/mtg/text_match.py`.

But `experiments/foundry_common.py` remains a live high-fan-in composition boundary and still owns DET-specific semantic preprocessing policy:

- DET self-reference canonicalization;
- synthetic `det_scan_texts()` modal expansion;
- shared modal/die recognizers injected into permanent delivery;
- an independent review-metadata face extraction helper.

The permanent module existing is not proof that every legacy interpretation is dead.

### 2. Reminder handling is a real S5 seam

Accepted source contains at least three materially different reminder behaviors:

- `oracle_text.paren_spans()` is depth-aware;
- `tier_engine.find_paren_spans()` is depth-aware;
- `shapes.delivery.REMINDER` is a flat parenthesis regex;
- DET scan preprocessing retains printed reminder text while delivery strips reminders.

Objective 2 measured no nested-parenthesis-depth >=2 cards in Gate #0, so Devoted Mardu remains a synthetic robustness case rather than a present product failure.

That does not close the broader reminder seam. A tracked 2026-08-07 historical audit recorded semantic false assignments caused by reminder text remaining visible to DET matching while delivery treated it as non-semantic. Those historical counts were **not** copied forward as current measurements, but the representation mismatch is still present in accepted source.

### 3. Self-reference is intentionally not presumed equivalent

The accepted stack still has:

- permanent `oracle_text.normalize_self_references`;
- legacy DET `foundry_common.canonicalize_self_reference`;
- legacy `tier_engine.normalize_self_references`.

The S10 ownership decision explicitly says architectural consolidation does not establish semantic equivalence. Current Gate #0 differential is still required before any S1 or canonical semantic merge claim.

The S7 runtime-substitution conservation lesson is already guarded: provider lookup must remain late-bound so a runtime rule replacement reaches downstream consumers.

### 4. DET preprocessing is an intentional different representation, not neutral card structure

`det_scan_texts()` creates synthetic modal scan variants. This is an S2 policy boundary, not a parser to promote blindly into the neutral Oracle owner.

Any future parser contract must distinguish:

- printed/structured card text;
- semantic face/paragraph ownership;
- delivery structure;
- DET synthetic matching representation.

Failure to name that boundary recreates historical probe-drift/modal-flattening failures.

### 5. Modal ownership remains duplicated/unproven across layers

Current static paths include:

- shared modal-header/mode recognizers in `foundry_common` injected into delivery;
- delivery header-to-mode consequence inheritance;
- locality's independent preceding-header / exclusivity derivation;
- DET synthetic mode expansion.

Objective 2 provides a mechanically complete stress population, especially the `81` modal-header-continuation cards plus pawprint/Spree/Tiered families, but the current A/B comparison still requires the pinned corpus.

### 6. Delivery and target semantics are much cleaner ownership cases

`foundry_shape_extractor.py` explicitly delegates to permanent delivery; it does not retain a second delivery implementation.

`foundry_object_lattice.py` explicitly delegates target/class interpretation to permanent `target_classes`; its remaining dependency is the injected DET scan representation, not a second target parser.

Those are static S0 ownership cases, while their upstream representation dependencies remain separately classified.

### 7. Quoted/granted ability ownership remains high-risk across representations

Delivery contains quote-aware sentence handling that prevents punctuation inside granted/quoted abilities from being treated as punctuation owned by the enclosing ability.

Generic scan-text/pattern matching does not by itself carry that quoted-region owner. Objective 2 independently identifies `1,986` quoted-text cards and `1,004` quoted-ability-colon candidates. The partial register therefore keeps quoted/granted ownership at S5 risk pending corpus-wide comparison.

### 8. Colon/cost/payment/zone/cardinality cross-layer ownership is not yet certified

The Objective-2 structural populations are large enough that sample reasoning is inadequate:

- top-level colon candidates: `8,325`;
- additional cost: `351`;
- alternative cost: `660`;
- resolution payment: `1,357`;
- multiple zone terms: `6,795`;
- variable-X: `2,021`;
- for-each: `1,992`;
- any-number: `923`;
- up-to-N: `1,483`.

These remain S3 where multiple task-specific consumers exist and the full applicable differential is not yet measured.

## Historical incident reconciliation completed statically

The partial register records the following current statuses without carrying old counts forward:

- partial reads / later abilities / single-face read failures: `CLOSED_AND_GUARDED`;
- face-boundary loss in flattened text: `CLOSED_BUT_DUPLICATE_REMAINS`;
- modal flattening/context stripping: `STILL_OBSERVABLE` as a representation seam;
- DET reminder retention versus delivery reminder stripping: `STILL_OBSERVABLE`;
- flat nested-reminder product failure: `SUPERSEDED_BY_SCOPE` because Gate #0 depth>=2 is zero, while synthetic robustness remains;
- historical hyphen/ability-word punctuation mutilation: `CLOSED_AND_GUARDED`;
- one-line/one-delivery linked-ability miss: `CLOSED_AND_GUARDED`;
- historical modal-continuation count: `NOT_REPRODUCIBLE_FROM_CURRENT_EVIDENCE` until the pinned corpus is available;
- runtime self-reference provider capture-by-value: `CLOSED_AND_GUARDED`;
- quoted/granted punctuation: `CLOSED_BUT_DUPLICATE_REMAINS` across delivery versus generic scan representations.

## Falsifiable negative controls mapped

Every S3-S5 row in the partial register is paired with a negative-control shape, including:

- flat nested reminder;
- capture runtime-replaceable parser rule by value;
- ignore modal continuation;
- flatten pawprint/Spree/Tiered or modal exclusivity;
- move target between modes;
- mistake quoted/reminder colon for activation colon;
- move condition between parent/child;
- swap source/destination zone;
- attach repeated identical text to wrong face/paragraph;
- corrupt quoted-ability punctuation;
- convert resolution payment to cost;
- alter quantity/distinctness;
- feed raw Oracle to a DET-dependent CARDNAME pattern.

A future acceptance guard must be demonstrated capable of turning red under the corresponding deliberate corruption.

## Non-binding ownership recommendation

The evidence supports the existing architecture direction, without authorizing implementation:

1. `mtj_foundry.corpus` remains the structural face/full-card owner.
2. `mtj_foundry.oracle_text` is the natural neutral recognition home, but only after corpus differentials establish semantics for any legacy policy being moved.
3. `mtj_foundry.mtg.shapes.delivery` remains delivery-consequence owner.
4. `mtj_foundry.mtg.shapes.locality` remains semantic-owner/evidence-location owner.
5. `mtj_foundry.mtg.shapes.target_classes` remains target noun/class owner.
6. DET synthetic preprocessing remains explicit policy and must not masquerade as neutral Oracle structure.
7. Late-bound provider lookup is a conservation requirement.
8. Quote/granted regions and top-level colon boundaries need explicit differential certification before consolidation.

These are recommendations only. They do not amend Captain/ratified law.

## What is deliberately NOT produced

Because the required corpus differential precondition failed, this STOP result does **not** claim Objective-3 completion and does not produce a parser-ownership acceptance contract as if the evidence were complete.

In particular:

- no full-population differential result artifact is fabricated;
- no S1 equivalence is inferred from historical tests;
- no holdout evaluation occurs;
- no parser/runtime/package/test code is changed;
- no codebook/authority state is touched;
- AQ4 remains paused;
- Bridge v0 remains unused;
- Step 6 remains not started;
- no merge/deploy/publish occurs;
- accepted `h` does not move;
- Objective 4 is not activated.

## Exact resume condition

Resume Objective 3 from this evidence branch only after the exact pinned corpus is available and its decompressed bytes reproduce:

`5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`

Then run the required current full-population/subpopulation differentials, update the S3/S5 seams with measured equal/divergent counts and signatures, and only then determine whether any duplicate qualifies for S1 or current S4/S5 evidence.

Until that occurs, Objective 3 remains **STOP / INCOMPLETE**.
