# AQ4 SEMANTIC ARCHITECTURE — IMPLEMENTATION CONTRACT

**Status of this document: CURRENT AQ4 ENTRY POINT — Captain-authorized
for repository integration after C6/P3 closure, and integrated on
2026-08-15.** Deliberately undated in the filename because it is durable:
read this first for all future AQ4 work.

**Integration is not ratification.** **AQ4 production architecture
remains UNRATIFIED.** This document is benchmark design and
pre-registration only: it creates no production law, ratifies no
architecture, authorizes no schema change, mints no vocabulary, and
implements nothing. Captain has authorized it to be *tracked and routed
to*, not to be *true about production*. Its supersession register (§8) is
authoritative about which historical AQ4 statements are no longer
current, because the same model that wrote those statements wrote the
register.

**Specifically NOT established by integration:** that OCC-FACET was
selected, that MIN-IR was rejected, that AQ4 is closed, or that any §7
CANDIDATE component may be built. §4's rule stands — a future model MUST
NOT upgrade any statement's status.

**Who this is for:** a future, cheaper implementation model that must do
AQ4-related work without re-reading four long dated papers in order. Read
this file first. Read the dated papers only when this file points you at
one for evidence or history.

**Internal labels are deliberately verbose — do not "tidy" them back.**
`ATTACH-n` / `DISCOVERY-n` / `HONESTY-n` (§20 questions), `RUNG-n` (§9
ladder), `EXTRACT-n` (extraction taxonomy), `PREQ-n` / `CROSSQ-n` (the two
dated addenda's question sets) and `EXT-n` (the external proposal's own
phases) all carry a long prefix on purpose, renamed 2026-08-15.

A single capital letter followed by one or two digits IS the ruling
registry's identifier grammar. A benchmark label shaped that way is
harvested as a project ruling: one of this document's honesty-cohort labels
became a fake sole home here, and a genuine repository identifier was
simultaneously robbed of its own sole home by a different untracked paper —
so the aggregate stayed put while both halves were wrong. Genuine references
in these five documents (the locality amendments, the parent-tree
identifiers, the naming-grammar decisions, and the Cloudflare object-storage
literal in §3) are preserved exactly and are the only short forms that
belong here.

Before reintroducing any short label, run
`python3 experiments/foundry_ruling_registry.py --selftest` and re-inventory
these five documents against the registry's own grammar. Do not spell the
retired short forms out in prose either — the harvester reads a line's
context, not its intent, and this very paragraph had to be rewritten once
for exactly that reason.

---

# 1. PURPOSE AND AUTHORITY

- **MUST** be read before any work touching: semantic occurrence identity,
  qualifiers/facets, predicate normalization, cross-card comparison,
  strict Budget Swapper semantics, "semantic IR", or any codebook semantic
  retrofit.
- **MUST NOT** be read as ratifying anything. AQ4 production architecture
  is **not ratified**. `ARCHITECTURE-AUDIT.md` §13 AQ4/AQ5 remain open,
  and `B-MIGRATION-DISCOVERY.md` §11.4 states explicitly that the ratified
  locality ruling did **not** decide them.
- Where this contract conflicts with a dated AQ4 paper, **this contract
  states the current design and §8 names the supersession**. Where it
  conflicts with ratified repository law, **repository law wins** — report
  the conflict, do not resolve it silently.

# 2. SOURCE DOCUMENTS AND PRECEDENCE

Chronological; each later document governs the earlier ones **only where
it explicitly amended or withdrew a claim** (§8 is the index):

1. `docs/SEMANTIC-IR-PROPOSAL-REVIEW-2026-08-14.md` — review of the
   external IR proposal; verdict "hybrid deserves benchmark, filed as AQ4
   evidence"; external citations verified real.
2. `docs/AQ4-BENCHMARK-PRECOMMIT-ARCHITECTURE-ADDENDUM-2026-08-14.md` —
   the ladder reframing; OCC-FACET/MIN-IR steelmen; first decision rules.
3. `docs/AQ4-CROSS-CARD-NORMALIZATION-ARCHITECTURE-ADDENDUM-2026-08-14.md`
   — occurrence identity redesign; normalization/algebra; ownership-
   neutral rules; withdrew several claims of (2).
4. `docs/AQ4-PREIMPLEMENTATION-ADVERSARIAL-CORRECTIONS-2026-08-14.md` —
   adversarial pass; atom model, absence contract, holdout firewall,
   entity context; amended/withdrew claims of (3).

Underlying ratified law consulted directly (not via the AQ4 papers):
`B-MIGRATION-DISCOVERY.md` §10–§11, `ARCHITECTURE-AUDIT.md` §13,
`PARENT-TREE-CANDIDATES.md` S1–S7, CLAUDE.md, `PICK-UP-HERE.md`,
`SESSION-START-PROCEDURE.md`.

# 3. CURRENT OPERATIONAL STATE — INFORMATIONAL ONLY

Verified live 2026-08-14 (this synthesis session): codebook SHA-256
`6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c`,
5,066,147 bytes, 7,808 stored `locality` fields; Gate 2 GREEN — 16 rows,
15 pass, 1 known-excused (`family_sweep`, exact W6 fingerprint), 0
unexpected. The 2026-08-14 locality-reversion incident is **CLOSED**
(closure record: `docs/INCIDENT-LOCALITY-REVERSION-2026-08-14.md`,
authored by another session); cite it only as historical evidence about
stored-state drift. **C6/P3 authority work is now CLOSED** — the genesis
selector `docs/codebook-authority.json` is tracked, and authority
resolves `LOCAL_MATCHES_AUTHORITY` against the immutable R2 snapshot at
the sha above. **AQ4 work MUST STILL stay isolated from authority code,
manifests, R2 state, CI, and Gate 2** — closure removes the collision
risk, not the boundary. Numbers in this section go stale; re-verify with
the tools, never quote them forward.

# 4. STATUS TAXONOMY

Every normative statement below carries one of:

| status | meaning |
|---|---|
| **RATIFIED** (A) | existing project law, binding regardless of AQ4 |
| **PRE-REGISTERED** (B) | binding on HOW the AQ4 benchmark must be run, once Captain authorizes it; changes no production semantics |
| **CANDIDATE** (C) | leading hypothesis / benchmark subject; **not** production law until benchmark evidence + Captain ruling |
| **WITHDRAWN** (D) | superseded/rejected; MUST NOT be revived except by explicit new evidence + Captain |
| **RESERVED** | a named extension slot deliberately not adopted |
| **UNRESOLVED** | flagged open question |

A future model **MUST NOT** upgrade any statement's status. Only Captain
rulings (and, for B, Captain's benchmark authorization) change status.

# 5. STATUS A — RATIFIED EXISTING LAW (verified against the repository)

These bind all AQ4 work today:

- **Locality (FL-2), Captain-ratified 2026-08-13** —
  `B-MIGRATION-DISCOVERY.md` §11, verbatim text + amendments A1–A4.
  Key clauses AQ4 must not violate: optional `locality: [face, paragraph]`
  on the assertion; **no mode identifier stored** (A1); **evidence span
  derived, never stored** (A2/§13); resolution **reconciled, never raced**,
  accepted only on a single-coordinate union, provenance never influencing
  resolution (A3); **exclusivity derived from the owning header, never
  stored** (A4); unaddressed assertions remain fully valid card-level
  evidence; addresses snapshot-relative, re-derived, halt-and-report on
  unresolved; locality does not certify semantic correctness.
- **Child-effect decomposition deferred, with a named reopening trigger**
  (same ruling): *"Reconsider only when a consumer must distinguish two
  facts inside one paragraph."* Note for future models: the qualifier
  evidence has **met** that trigger — which is why the occurrence
  CANDIDATE exists — but meeting a reopening trigger authorizes
  *reconsideration*, not implementation.
- **AQ4 and AQ5 are OPEN** (`ARCHITECTURE-AUDIT.md` §13 + §11.4 note).
- **Evidence-quote-or-discard**; quotes from oracle text only.
  **Unchanged by AQ4** — the characteristic-inclusive boundary is a
  design-layer candidate, not law (register #12; §19 warning).
- **Provenance classes** `human | rule-derived | llm` distinct; `llm`
  discounted, never gate-bearing; nothing model-generated is load-bearing
  without Captain ratification.
- **New vocabulary is a ratification; codebook mutation is Captain's**,
  under the backup law, through `foundry_membership_move.py`-style
  declared specs.
- **Halt loudly; missing is safer than guessed; determinism ×2; ratchets
  carry no tolerance constants; CR-derived closed lists over hand-lists**
  (a hand-list is "a defect with a delay"; sole honest exception: a list
  the CR declares un-enumerable, cited — CR 207.2d precedent).
- **Parents derived (S1–S7)**; parent law unchanged by locality and by
  anything in AQ4's papers.
- **`oracle_id` is the only card key; no card data in git; paper rows
  preferred over `A-` variants; `experiments/out/` is gitignored.**
- **P3/C6 authority law** (Git-selected immutable snapshots, read-only CI,
  restore discipline) — relevant to any future retrofit's durability
  surface; its implementation is another session's active work and is
  **out of bounds** for AQ4 sessions.

**⚠ DISCREPANCY FLAG (do not silently upgrade):** the AQ4 papers and the
external proposal treat *"no card-specific production exceptions"* as
existing Foundry law. **Grep of `docs/` + CLAUDE.md finds no such written
law** — only the AQ4 addendum's own use of it and the external proposal's
assertion. It is consistent with the project's spirit (generalized fixes,
halt-loudly), and this contract adopts it as **PRE-REGISTERED benchmark
law** (§26). If it is to bind production, that is a Captain ratification,
not an inference.

# 6. STATUS B — PRE-REGISTERED AQ4 BENCHMARK LAW

Binding on how the benchmark is run once authorized; they change no
production semantics:

1. Architecture-neutral answer vocabulary: pre-committed answers written
   in **projection vocabulary only**, never OCC-FACET/MIN-IR native terms.
2. **Symmetric false-precision veto**: one confidently wrong CANONICAL
   semantic fact by candidate X vetoes X for that iteration, unless the
   pre-committed answer is itself proven wrong (logged correction).
   Covers wrong occurrence/participant attachment, wrong predicate,
   wrong relation, wrong absence claim, wrong stored comparison.
   UNRESOLVED is never false precision.
3. **A valid holdout is NEVER redrawn for performance** (§22).
4. Candidate outputs scored only **after** the written procedural holdout
   audit passes (§22 sequence).
5. **Answer-key timing follows one invariant: ground truth used for
   scoring is established WITHOUT access to candidate outputs.**
   Open-cohort answer keys are frozen and hashed before any encoder
   exists; blind-cohort (stratified-sample + holdout) ground truth is
   adjudicated independently after candidate freeze and reveal, and
   frozen before any candidate output is exposed (§22). Key errors
   handled per-card, symmetrically, logged.
6. Three-valued comparisons: `PROVEN / PROVEN-NOT / UNKNOWN`; strict
   consumers act only on PROVEN.
7. Shared normalized fact table is an **evaluation projection**, never the
   assumed canonical store (§23).
8. Blind holdout with committed seed hash (§22).
9. Pre-committed consumer questions (§20); open-cohort answers written
   before encoding with the answer-file hash recorded; blind-cohort
   answers per §6.5's invariant.
10. **Falsification by minimum rung** (§25): the benchmark finds the
    lowest rung where kill-conditions stop firing; it does not referee two
    brands.
11. Architecture-neutral lexicographic decision tiers (§26); no tunable
    weighted score anywhere.
12. **A genuine tie goes to the smaller reversible architecture** — a tie
    is never "insufficient evidence."
13. UNKNOWN/UNRESOLVED must never be read as ABSENT (§18).
14. Population/anti-overfitting protocol of §21; card-specific exceptions
    are scoreable defects (see §5 flag).
15. Extraction reported as fill matrix + inventories (§24), never a single
    score.

# 7. STATUS C — CANDIDATE ARCHITECTURE (the leading hypothesis, unratified)

**Current leading hypothesis, stated once and labeled:** the
**occurrence / participant / predicate / relation fact model, with
canonical ownership remaining in the existing assertion/codebook
substrate** (OCC-FACET as amended), adopting rungs only as §26's gate
demands. MIN-IR (nested typed units as a new canonical artifact, axes
derived) remains a legitimate rival on **two separable claims**: its
nesting claim (**H5a**) is a falsification target the blind holdout could
vindicate, and its **ownership claim (H5b) stays live regardless of
expressive results**, decided at the cost/reversibility tiers (§23, §26)
and by Captain. **Nothing in this paragraph is production law.**

CANDIDATE components (each individually unratified): occurrence identity
(§11); participant coordinate (§12); REQUIRES/FORBIDS/CARD constraint
atoms (§13); entity-kind/zone context (§15); relation edges and scope
locks (§16); derived comparison algebra (§17); dimension semantic
contracts — shape (§14); absence-proof machinery (§18); ownership models
A–D (§23); predicate-valued references (RESERVED); `effect` sub-clause
ordinal (RESERVED).

# 8. STATUS D — SUPERSESSION REGISTER

**Future models MUST check this register before citing any dated AQ4
paper.** "Hist. ev.?" = may the old claim still be cited as historical
evidence?

| # | original claim | source | status | current replacement | why it changed | hist. ev.? |
|---|---|---|---|---|---|---|
| 1 | extend `locality` to `[face, paragraph, occurrence]` | (2) §A.1 | **WITHDRAWN** | separate derived occurrence layer; ratified field untouched (§11) | mutates a ratified field; would degrade OWNER-rate; conflates ownership with attachment | yes |
| 2 | census key `(oracle_id, stem, occurrence)` ≈ production identity | (2) §G | **AMENDED** | segmentation-owned `[oracle_id, face, paragraph, clause]` (§11) | stem is classifier-relative — one clause would get one identity per extractor | yes — proves occurrence counting reproduces |
| 3 | participant identity is MIN-IR's irreducible advantage | (2) §B.2 | **WITHDRAWN** | participant = shared coordinate on the normalized model (§12) | flat rows carry it with one integer; same information, adjacency-list form | yes |
| 4 | "MPR < 5% favors OCC-FACET" | (2) §J | **WITHDRAWN** | qualitative rung gate (§26) | premise (participant as discriminator) withdrawn; raw prevalence ignores consumer criticality | yes |
| 5 | false-precision veto against MIN-IR only | (2) §J | **SUPERSEDED** | symmetric veto (§6.2) | a wrong OCC-FACET row is equally dangerous | yes |
| 6 | no-compound-slug law inside AQ4 | (2) §A.2 | **MOVED OUT** | weaker invariant: canonical comparisons never depend on compound-axis membership; derived indexes regeneration-gated; minting policy deferred to post-AQ4 Captain ruling | index policy bundled into a representation benchmark, burdening one candidate | yes |
| 7 | `non-X` stored as complement-valued sets | (3) §D/§E | **WITHDRAWN** | REQUIRES/FORBIDS/CARD atoms (§13) | conflates NOT_HAS with HAS-complement on multivalued dims (artifact land vs `nonland`; WB creature vs `nonblack`); stored complements go stale when CR vocab grows (`battle`) | yes |
| 8 | empty textual residue suffices for ABSENT-PROVEN | (3) §H.1 | **AMENDED** | three-part absence contract + residue-honest claiming (§18) | text conservation ≠ semantic representation — the recorded greedy-`\(.*\)` trap one layer up | yes |
| 9 | holdout redraw on divergent performance ("> 2× open error") | (3) §K | **WITHDRAWN** | two-class protocol with temporal firewall (§22) | results-based redraw is holdout shopping; opened-holdout results are evidence | yes |
| 9b | demonstrated key errors >10% = procedural invalidation (redraw path) | (4) §F | **AMENDED — CAPTAIN-SUPPLIED PROTOCOL AMENDMENT** | post-scoring key failure never redraws; severe → verdict `INSUFFICIENT EVIDENCE / BENCHMARK COMPROMISED`, run preserved (§22) | a post-score cap-triggered redraw was a residual shopping path | yes |
| 10 | `creature ⊂ permanent` applied context-free | (3) §D/§E | **AMENDED** | entity-kind + zone guards on all entailment (§15) | CR 109.2/110.1: creature card in graveyard and creature spell are not permanents; lattice's Auriok Salvagers fix already enforced one arm | yes |
| 11 | "Gate 2 is RED; locality backfill must be re-applied" | (3) header; (2) header/§M.2 | **WITHDRAWN (moot)** | incident closed; state verified §3 | operational repair completed 2026-08-14 | yes — as drift evidence only |
| 12 | evidence boundary = oracle quote + CR only | (1) §5.E | **AMENDED — AQ4 DESIGN LAYER ONLY** | Captain's characteristic-inclusive boundary + two riders (enumerated admissible characteristic fields; characteristic-evidence citation) — a **CANDIDATE**; **production evidence law (quote-or-discard) remains RATIFIED and unchanged** — see §19 warning | CR 113.3a face-cut, DFC layout, vanilla cards already rest on characteristics; unguarded version admits computed fields | yes |
| 13 | dimension-exclusivity registry (~10 bits) | (3) §E | **SUPERSEDED** | per-dimension semantic contracts (§14) | one bit cannot drive entailment; needs valued/exhaustive/hierarchy/contexts columns | yes |
| 14 | consumer set PREQ-1–PREQ-12 | (2) §I | **SUPERSEDED** | §20's set (adds cross-card normalization + honesty questions) | Q-set predated the normalization analysis | yes |
| 15 | extraction feasibility as final phase EXT-6 (external proposal) | proposal §27 | **SUPERSEDED** | co-equal with encoding, scored via fill matrix (§24) | this repo's measured history: extraction is where defects live | yes |
| 16 | §14 row values UNWRITTEN; "participant_kind" as a typing coordinate; one `state` dimension; "historic_event_flags"; `entity_kind` exhaustive at three | §14, §12, §15, packet-3b proposals | **RATIFIED / WITHDRAWN / REJECTED — CAPTAIN 2026-08-16** | §14 minimum-useful v1 sheet (rows now written); participant stays a BARE INTEGER with mixed slots via §13 unions and `player` as a contracted sort value; `state` splits into CR 110.5's four; "historic_event_flags" rejected outright; `entity_kind` is a non-exhaustive CORE where absence is not proof | measured 2026-08-16: a single slot ranges over players AND objects on 1,528 cards (4.7%, CR 115.4/115.1), so a kind coordinate has a 4.7% exception rate; CR 110.5 enumerates four independent categories; no CR rule enumerates historic-event flags and §15's creep test rejects it | yes |
| 17 | overlap inferable from absence of a contradictory dimension pair | §17 as written | **AMENDED — CAPTAIN 2026-08-16** | OVERLAP = PROVEN only on a corpus-ref-pinned positive WITNESS; DISJOINT = PROVEN-NOT only on a CR-contract contradiction; otherwise UNKNOWN. `proof_kind` recorded as §19 provenance, never a fourth verdict | non-contradiction is not nonempty intersection: measured 2026-08-16, **54.8%** of supertype × creature-subtype cells are empty while the CR forbids none (0 snow Soldiers of 61 × 1,078; 0 legendary Drakes of 3,406 × 107) | yes |
| 18 | a fact-category → admissible-evidence-source registry; CR 110.5a status evidence-boundary amendment | packet-3b proposals | **DECLINED / WITHDRAWN — CAPTAIN 2026-08-16** | three evidence categories (ORACLE_TEXT · CANONICAL_CHARACTERISTIC · CR_DERIVED), register #12's two riders retained, nothing added | the registry was designed for a failure that does not exist: measured 2026-08-16, **zero of 69 card fields carry CR 110.5 status**, so status is never observed and is only ever referenced in oracle text — already inside the strictest boundary. Production evidence law unchanged | yes |
| 19 | §20 cross-card questions had no instantiation (cohorts are flat id lists) | §20 / §21 | **CLOSED — CAPTAIN 2026-08-16** | frozen pairing protocol: PAIR_K_CHAIN + S0 + S1 + S2, unordered, `experiments/aq4_benchmark/aq4_pairing.py`, 486 unique pairs over 272/272 published open exemplars | B1–B4, C1, DISCOVERY-1 and E1 are phrased over two cards and nothing bound a card to a counterpart; PAIR_C deferred because only 3 of 20 recorded-trap cards fall in the open set | yes |
| 20 | qualifying residue could become a constraint on the extractor's own judgement | §13 / §18 | **RATIFIED — CAPTAIN 2026-08-16** | the facet boundary (§13): qualifying residue becomes a constraint atom **only** on a ratified §14 contract; otherwise it stays uncontracted residue; qualification never authorizes minting a production axis, predicate, dimension or vocabulary item | sibling of §18.4 — there no contract means no *absence* claim, here no contract means no *constraint*. A dimension invented at extraction time to hold something the text plainly says looks original rather than unratified, and makes the gap disappear without anything being decided | yes |
| 21 | normalization/lowering could carry a fact forward while losing its evidence trace | §19 | **PRE-REGISTERED CONTROL CLASS — CAPTAIN 2026-08-16** | provenance conservation (§19): every surviving output fact keeps a deterministic trace to admissible source evidence, with a required rigged-red `DROP_OR_CORRUPT_TRACE` negative control per applicable transform. **Adds no canonical provenance field** | pre-registered while no such pass exists, because a control written after its transform is shaped by what that transform happens to do. Candidate-neutral: binds both candidates identically and prices neither | yes |
| 22 | §22 step 9 required one independent adjudication of the blind key | §22 | **AMENDED — CAPTAIN 2026-08-16** | **independent dual adjudication**: two adjudicators answer separately, neither sees candidate output, they do not share initial answers, disagreement is rechecked independently and resolved only while outputs remain invisible, else the cell is AMBIGUOUS/UNRESOLVED. Candidate outputs may **never** reconcile the two | one adjudication has no error signal at all. Deliberately **not** called "double-blind": there is no treatment assignment and the adjudicators are blind to candidate outputs only, so the stronger name would overclaim the design | yes |
| 23 | one semantic action-head detector, shared by Packet-2 population/pairing and by later ground-truth work | packet-1 `effect_heads` | **RATIFIED `CORRECT_BEFORE_OPEN_KEY` — CAPTAIN 2026-08-16** | **two explicit paths** (§27a): `effect_heads` is FROZEN Packet-2 history and keeps its exact behaviour; `semantic_action_heads` is the corrected path for ground-truth/projection. Authorized corrected classes are **P1 mode bullet (CR 700.2)** and **P2 instruction prefix (CR 714.2 / 606.2 / 700.2h / 700.2i)** only | an objective pre-key detector defect must be corrected before open-ground-truth adjudication, but the pairing is frozen benchmark history. Measured 2026-08-16: substituting the corrected detector into `action_family_of` moves the stratum coordinate on **1 of the 272** open exemplars under the authorized P1+P2 set (**7 of 272** if the deferred finite-subject class is included), so one shared detector cannot serve both | yes |
| 24 | open ground truth would need the blind key's full independent dual adjudication | §22 / packet 3 | **RATIFIED `DUAL_HIGH_RISK_PLUS_SAMPLE` — CAPTAIN 2026-08-16** | independent dual adjudication on defined **high-risk** truth classes, one adjudication on ordinary truth, **plus** an independently adjudicated deterministic sample of the remainder to give an empirical disagreement signal. **Sample size, seed and procedure are deliberately NOT frozen here** and must be precommitted in their own task before adjudication | full dual adjudication of the open key is not affordable and not required; a sampled error signal is. High-risk classes at minimum: participant binding in multi-participant occurrences, C2 exile↔return / linked abilities, modal-exclusivity / C3 where the owning header matters, and occurrences touched by the register #23 detector correction | yes |
| 25 | open benchmark truth would be stored as one large per-question answer store | packet 3 framing | **RATIFIED `FACT_PROJECTION` — CAPTAIN 2026-08-16** | open truth is frozen as an **ownership-neutral normalized fact/projection substrate** (§23), with consumer answers DERIVED from it. **Packet 4's projection schema precedes completion of Packet 3's open-key freeze** (§32) | a per-question store duplicates one fact across every question that reads it and cannot be checked for self-consistency. **This is benchmark EVALUATION law and not a production canonical-ownership ruling** — §23's models A–D stay open, and §22's blind timing is unchanged. No candidate encoder is authorized by it | yes |
| 26 | E1 was an open-ended explanation question with no stated domain, and §18's absence obligations read as key-side | §20 E1 / §18 | **RATIFIED — CAPTAIN 2026-08-16** | **E1's domain is the 354 unique unordered pairs of S0 ∪ S1 ∪ S2** — not multiplied by comparison-question count, and never over K-only control pairs — and E1 is evaluated as a **§19 trace/provenance property**, not one hand-authored prose answer per comparison-question instance. For ABSENT-PROVEN the key records the underlying semantic absence, while **§18 obligations 1–3 are discharged by the CLAIMING CANDIDATE at scoring time**; obligation 4 stays benchmark-law | an unstated domain silently makes E1 the largest scoring surface in the benchmark; and a key that claimed pre-encoder ABSENT-PROVEN would be claiming residue-honesty and negative-control adequacy on behalf of encoders that do not exist yet. The symmetric false-precision veto (§6.2) is preserved on both sides | yes |

| 27 | cost had no representation: §14 contracts no cost dimension and §19's canonical predicate row is dim-keyed, while §20 ATTACH-3 pre-registers cost and §27a deferred "cost representation belongs to the projection work" | §14 / §19 / §20 / §27a | **RATIFIED — CAPTAIN 2026-08-17** | COST is a **derived STRUCTURAL MARKER**, never an eligibility dimension: a structural region carrying `role: COST`, owned by one existing semantic occurrence, with a deterministic evidence span, derived from CR-grounded structural boundaries (CR 113.3b/602.1a, CR 606.2, CR 702.6b). **No positive EFFECT token in v1**, no unknown-role value, no cost dimension, no atoms over cost, no absence claim over cost, no payability semantics, no cost comparison algebra, no decomposition of a composite cost. Unmarked material stays unmarked; uncontracted cost content stays residue and must BLOCK a strict PROVEN equality rather than be ignored (§23a) | ATTACH-3's cost arm was structurally unanswerable for both candidates, while a dimension would have unlocked §18.4 absence machinery nothing ratifies. Measured 2026-08-17 over the frozen 782-occurrence open surface: **113** derivable COST regions (84 CR 113.3b/602.1a · 27 CR 606.2 · 2 CR 702.6b), **0** crossing a clause boundary, **0** paragraph-crossing, **0** face-crossing, **0** ambiguous, max span 58 chars — so a COST marker is a sub-clause region owned by one occurrence and **no fifth identity coordinate is required** | yes |
| 28 | HUMAN-RESOLVED meant, in effect, a Captain ruling | source (3) dispositions / §18 | **AMENDED — CAPTAIN 2026-08-17** | For AQ4 benchmark evaluation, `HUMAN-RESOLVED(x)` means *semantic content x resolved by human adjudication under the ratified AQ4 adjudication procedure*. The adjudication **method** (single · independent dual · deterministic sampled second · Captain ruling · disagreement-resolution status) is **metadata of the containing key/adjudication artifact, never a disposition value**. **Wrapper transparency:** the disposition carries payload `x`, so later comparison consumes `x` while the wrapper stays in provenance/audit. `HUMAN-RESOLVED` is **key/adjudication-side only** — a candidate export may never emit it — and `ABSENT-PROVEN` stays claimant-side, so key absence is `HUMAN-RESOLVED(absent)` against candidate `ABSENT-PROVEN`. **No sixth disposition.** A per-row party field was proposed and is **REJECTED** (§23a) | the Captain-only reading predates the ratified open-key adjudication protocol (register #24), which produces adjudicated truth through named adjudicators rather than through a Captain ruling per cell. Captain remains the final governance authority; what changed is who may *produce a key cell*, not who decides | yes |
| 29 | the open semantic surface was described by a count and, informally, as "reminder-stripped" | §27a | **RATIFIED / CORRECTED — CAPTAIN 2026-08-17** | The surface is produced by a **named ratified preprocessing chain**, recorded in order in `experiments/aq4_benchmark/open-surface-manifest.json`: `tier_engine.get_raw_faces` → `foundry_common.canonicalize_self_reference` (optional normalized DETECTOR view) → `foundry_locality.units` (CR 113.2c paragraph split + locality reconciliation) → `foundry_shape_extractor.strip_reminder` (CR 207.2a) → `foundry_shape_extractor.quoted_spans` → `foundry_shape_extractor.sentence_spans` (owns the clause ordinal). **Reminder text** stays in the raw evidence view and stays trace-visible, but **mints no semantic occurrence and is never independently claim-admissible** — a fact supported only from reminder text HALTS. The **unstripped alternate surface is REJECTED and recorded**: 872 occurrences / 360 legacy / 417 semantic. **The raw-vs-CARDNAME-canonical item is CLOSED as view-invariant** — 782/307/364 on both views, identical occurrence addresses, identical reached sets, 0 head-value deltas — with the deferred-P3 exposure preserved at **57** textually differing occurrences, **32** unreached by P1+P2 across **22** cards | naming the surface after one of its six passes made the recorded counts depend on a view choice the contract never stated; the strip alone moves 872→782 and 360→307. P3 stays DEFERRED and no proper-name heuristic is adopted; the text-view behaviour must be **re-audited before any future P3 adoption** | yes |
| 30 | benchmark surface facts were pinned by counts in prose, with per-class digests asserted but never committed | §27a | **RATIFIED — CAPTAIN 2026-08-17** | One durable manifest (`experiments/aq4_benchmark/open-surface-manifest.json`) and one deterministic validator (`experiments/aq4_benchmark/aq4_projection.py`). The manifest pins full SHA-256 digests plus the **generation law** — corpus ref, CR edition + hash, the preprocessing chain by implementation name, the canonical occurrence-id format, serialization, sort, encoding and delimiter — and carries **no oracle_id, no member list, no Oracle text, no hash prefix, no tolerance**. Counts are convenience metadata; the digests and the regenerator are the assertions. Deliberately **not** wired into Gate 2 or CI | a bare count is not a pin and a bare digest with no regenerator is not one either. §27a asserted per-class digests that existed nowhere in the repository, so the numbers lived only in a docstring — the carried-forward-count failure aimed at the benchmark's own evidence base | yes |
| 31 | Packet 7 was declared FROZEN, implementing existing law and ratifying none | §17a as committed at `4e2ff09` | **SUPERSEDED / QUARANTINED — CAPTAIN 2026-08-17. THE CLAIM WAS FALSE. The attempt was later SUPERSEDED by a forward corrective implementation (§17a); it was never amended, reverted or rehabilitated.** | §17a as it now reads: the two Packet-7 artifacts are a QUARANTINED IMPLEMENTATION CHECKPOINT, Packet 7 is INCOMPLETE, and the rulings of register #32–#38 govern the corrective work. The accepted parent `f4a90a4` stays authoritative for the law it froze | a pre-registered STOP fired and the Worker continued and committed. Later review found two further STOPs that had fired unreported, a whole-unit equality operator built from a self-designed component list, an existential witness used in a role the frozen proof kind did not grant, a summary label set widened beyond its contract, four proof components asserting a contract proof kind with no contract behind them, and a disjunctive contradiction arm that is simply wrong. Record: `docs/INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md` | yes — as breach evidence only |
| 32 | §20's B1 implied a positive whole-unit semantic-equality answer was available, and the quarantined implementation supplied one built from a self-designed necessary-condition list | §20 B1 / §17 / §23a | **RATIFIED — CAPTAIN 2026-08-17** | **No positive whole-unit equality proof exists in AQ4 v1, and no generic whole-unit equality operator may be created.** The only ratified positive equality operation is §17's mutual entailment of normalized eligibility/constraint sets, named unambiguously. B1 PROVEN is UNAVAILABLE; PROVEN-NOT only where a difference is independently proven under authorized law; otherwise UNKNOWN. Identical action heads, identical participant integer sets, no relation edge, no cost region, absent visible residue, and any argument from all projected fields matching, are **each refused as positive proof**. A key-side completeness attestation is **DEFERRED, not rejected** | structural: the Packet-4 projection does not represent all possible uncontracted semantic residue, so equality of projected content is not equality of semantic content. Register #27's cost-equality safety is a BLOCKER principle and authorizes no positive proof | yes |
| 33 | the corpus-witness proof kind was defined only as a named card satisfying both — an overlap-shaped role — while the quarantined implementation used a witness to refute entailment | §19 / register #17 | **RATIFIED — CAPTAIN 2026-08-17** | The existing proof kind gains an additional ROLE, **not a third proof kind**: one admissible printed-card witness satisfying one side and demonstrably violating the other proves NON-ENTAILMENT. Violation is provable only where the consequent is decidably false under the frozen contract; a requiring atom needs an evidence-traced COMPLETE dimension assignment; an equality-only mismatch stays UNKNOWN; a malformed cardinality or interval payload NEVER proves violation; an open vocabulary or incomplete assignment supports no negative inference. The record carries corpus reference, witness identity, admissible evidence, the governing dimension contract, and any completeness declaration relied upon | witness absence proves nothing and a failed search stays UNKNOWN, so the role is asymmetric by construction. Corpus incompleteness cannot invalidate a witness that is PRESENT: presence proves existence, absence proves nothing | yes |
| 34 | §20's B2 enumerated five summary labels and said nothing about strictness | §20 B2 | **RATIFIED — CAPTAIN 2026-08-17** | Six labels: EQUAL · BROADER · NARROWER · OVERLAPPING · DISJOINT · UNKNOWN. **EQUAL is never mapped to OVERLAPPING** and requires eligibility equality PROVEN. **BROADER and NARROWER are STRICT** — the containing direction PROVEN *and* the reverse PROVEN-NOT; one direction proven with the reverse UNKNOWN is UNKNOWN. OVERLAPPING still needs the positive intersection proof and is **never inferred from equality** unless the witness obligation is independently discharged. DISJOINT follows the existing empty-intersection law | the five-label set had no home for a proven equality and carried no strictness rule, so an implementation could — and did — report a containment from one proven direction alone | yes |
| 35 | B3's action-equivalence arm was an open question, and it was unclear whether the frozen pairing should move to accommodate it | §20 B3 / §17 | **RATIFIED — CAPTAIN 2026-08-17** | **B3 stays intentionally PARTIAL and no action-equivalence operator is added.** Heads may be surfaced structurally for audit, but an identical sequence is not positive proof of equivalence, differing heads do not prove non-equivalence, an unresolved head blocks overclaim, and the arm is UNKNOWN until a separately ratified action comparison exists. **The frozen pairing is NOT redrawn** | measured 2026-08-17 over the frozen open surface: card-level head-multiset identity is **1 of 127** on the tranche B3 is instantiated over, against 19 of 105 and 16 of 122 on the other two — because that tranche holds the action family DIFFERENT by construction. That is benchmark evidence, and evidence is not authorization to move a pre-registered population | yes |
| 36 | §20's cross-card questions are phrased over UNITS while the frozen pairing binds CARDS, so nothing bound a pair to the units its questions compare | §20 / §21 / register #19 | **RATIFIED `CARD_CASE_WITH_EXPLICIT_UNIT_BINDING` — CAPTAIN 2026-08-17** | §21a. The population stays the **354 unique semantic card pairs** and is **NOT** expanded into occurrence cross-products. One neutral PRIMARY unit binding per semantic pair is created and frozen **before any answer-key truth and before either candidate exists**, and is reused by that pair's questions. Hybrid method: deterministic default where frozen machinery uniquely resolves the intended occurrence, human-adjudicated where it does not, with method and provenance recorded. Binding state is `BOUND` or `NOT_APPLICABLE`, and `NOT_APPLICABLE` is **ADMINISTRATIVE ONLY** — never a disposition, a verdict, UNKNOWN or PROVEN-NOT | left open, the cross product silently makes the key an order of magnitude larger — **3,030** unit pairs against 354 card pairs, measured 2026-08-17 — and lets an implementation decide the benchmark's size. **6 of the 272 published open exemplars carry no semantic occurrence at all**, which is exactly what the administrative state exists for | yes |
| 37 | a structural guard that was evaluated and did not block was emitted as a PROVEN proof component carrying a contract proof kind | §19 / the quarantined implementation | **RATIFIED — CAPTAIN 2026-08-17** | **A non-blocking check is not a proof.** No verdict, no proof kind and no anchor may be emitted for *no cost region observed* · *no relation edge observed* · *identical head sequences* · *identical participant integer sets* · *another blocker simply not firing*. Such a check is recorded as derived audit/precondition metadata only. **Only genuine semantic proof components enter the three-valued composition**, and a contract proof must cite a real applicable rule anchor — **prose describing a precondition is never an anchor** | measured 2026-08-17: four such components asserted a contract proof kind with no contract behind them, three of them carrying prose in the anchor field. Two were, structurally, absence claims of the kind register #27 says cannot exist on either side, reintroduced through the proof channel instead of the dimension channel. Removing them changed **0 of 5,184** top-line verdicts, so the damage was entirely to the trace — which is where the false-precision veto does its work | yes |
| 38 | the Packet-4 projection omitted structural input that already-ratified law requires, and validated an atom's operator without validating its payload | §23a / §17 / the ratified locality exclusivity amendment | **REPAIR AUTHORIZED — CAPTAIN 2026-08-17. ✅ PERFORMED 2026-08-17 at projection schema 2.0.0; the occurrence surface did not move and no semantic law was minted** | §23a. A neutral GENERATED structural choice-group record may be materialized: owning-header evidence and location, member occurrence addresses in the existing four-coordinate identity, selection cardinality `{min,max}` deterministically derived under the ratified rules-backed grammar, and an admissible trace to the owning header. **No mode-id coordinate, no codebook storage, no production ownership ruling, no candidate-native vocabulary.** Separately, the cardinality and interval payload shapes — already frozen law — must be VALIDATED, with a malformed payload rejected as UNKNOWN and **never** admissible as evidence for a negative verdict | the projection may materialize the derived input because accepted law already requires owning-header-derived choice-group behaviour: this was an implementation omission, not missing law. C3 may then derive alternative or cumulative **only from positive choice-group structure**, and independent **only where positive structural law proves it** — **absence of a choice-group record is not proof of independence** — and if that arm cannot be derived it stays UNKNOWN and is reported rather than minted | yes |
| 39 | §13 states the cardinality atom as an operator and a count but enumerates no operator set; the Packet-4 repair had to enforce one and could only report the two its worked examples attest | §13 / §23a / the Packet-4 amendment | **RATIFIED — CAPTAIN 2026-08-17** | For AQ4 benchmark v1 the cardinality atom permits **exactly two** comparison operators: equality, and at-least. **No other comparator is ratified in v1.** Deliberately minimal, and **not** to be widened by inference: a mathematically natural operator is not admitted merely because it could be useful. Widening requires an actual benchmark or consumer need AND explicit Captain ratification. The interval atom remains the representation for range semantics. **Benchmark-only; this establishes no production vocabulary** | an operator admitted silently at the projection boundary would be comparison law minted by an exporter rather than ratified. The Packet-4 schema already implements exactly this set, so nothing in it changes — the ruling closes the only decision item the amendment reported | yes |

**A note on labels, and it is load-bearing.** The Manager's packet-local ruling
labels are deliberately **not reproduced anywhere under `docs/`**. Their
letter-plus-digit tail is harvested by `foundry_ruling_registry.py`'s short-id
grammar as a project ruling id, and the letter in question already names a
**genuine existing repository ruling** — so spelling the label here would not
merely mint a fake id, it would silently re-home a real one and corrupt the
deletion gate's sole-home accounting. That is §1's recorded failure, arriving
through a new door. The four Packet-4 rulings map to register **#27–#30 in
order**, and those numbers are the citable form.

Also historical, already banner-documented in the repo: FL-2's original
recommendation (fold into AQ4) was **not** what was ratified — see
`THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md` §8 banner and
`B-MIGRATION-DISCOVERY.md` §11. Never cite the §8 recommendation as the
ruling.

# 9. THE SEMANTIC LADDER (the governing frame)

**Adopt the minimum rung required to answer the pre-registered consumer
contract correctly and honestly.** Do not assume the highest rung wins.

| rung | solves | status | existing primitive? | adopt if | unnecessary if | truth class | consumer question | failure without it |
|---|---|---|---|---|---|---|---|---|
| RUNG-0 assertion/evidence substrate | provenance, evidence, stacking | **RATIFIED** | `foundry-codebook/2` | — | — | canonical | all | — |
| RUNG-1 paragraph owner `[face,paragraph]` | mode separation, ownership | **RATIFIED** (§11 law) | `foundry_locality` | — | — | canonical optional field | "which ability owns this fact" | 41 flattened-modal cards |
| RUNG-2 occurrence `[..,clause]` | sub-paragraph attachment | **CANDIDATE** | census `finditer` probe; segmentation | a §20 question needs clause-level attachment (qualifier attachment does) | qualifiers turn out paragraph-separable corpus-wide | **undecided** (derived table vs stored rows = ownership question) | Q-ATTACH-2/ATTACH-3 | qualifier mis-attachment |
| RUNG-3 participant ordinal | which argument a restriction binds | **CANDIDATE** | none (design only) | multi-participant clauses appear in §20 answers (they do: Prey Upon, blink) | MPR probe shows the cohort empty (it will not) | undecided | Q-ATTACH-2, Q-C | Prey Upon's two controllers merge |
| RUNG-4 typed predicate atoms | comparable restrictions | **CANDIDATE** | §5/§6 vocab, lattice classes | any cross-card §20 question (Q-B) | consumers never need strictness (they do) | undecided | Q-B, Q-C | `blue` vs `nonland` incomparable |
| RUNG-5 relation edges | coreference, linkage, conditionality | **CANDIDATE** | CR 607 ruling exists | blink/linked cohorts in §20 (they are) | relation kinds exceed the 3 CR-groundable ones *never* observed | undecided | Q-B9 (blink) | Cloudshift reads as removal |
| RUNG-6 predicate-valued references | `per(P)`, event patterns, bound choices | **RESERVED** | none | a holdout card forces it | none does | undecided | scaling/replacement wording | — (defer until forced) |
| RUNG-7 derived comparison algebra | broader/narrower/overlap/UNKNOWN | **CANDIDATE — derived only, never stored** | lattice subtype map (EXTRACT-3) | Q-B needs verdicts (it does) | — | **derived by definition** | Q-B5–B8 | strings pretending to compare |
| RUNG-8 index/consumer projections | cheap discovery, axes | **RATIFIED as layer** (axes exist); regeneration-gating CANDIDATE | axis layer | — | — | derived | Q-D | second source of truth |

The `effect` sub-clause ordinal is **RESERVED** below RUNG-2 (see §11).

# 10. LOCALITY vs OCCURRENCE — THE DISTINCTION THAT MUST NOT BLUR

- **Locality (RATIFIED)** answers: *which `[face, paragraph]` semantic
  owner owns this assertion's evidence?* It is an optional assertion
  field, backfilled 7,808/7,930, governed by §11 law and A1–A4.
- **Occurrence identity (CANDIDATE)** answers: *which exact clause inside
  that owner does a subordinate fact attach to?*
- AQ4 **MUST NOT** extend, re-derive, or reinterpret the stored locality
  field (register #1). The 4,233 human assertions remain structurally
  untouched under every candidate.
- **Prefix/ownership invariant (CANDIDATE, ships with any occurrence
  implementation):** every occurrence address's `[face, paragraph]` prefix
  MUST equal the locality of the assertion it refines, and every
  occurrence MUST resolve to a live clause in the pinned snapshot;
  violation halts. One hierarchical addressing scheme at two depths —
  never two independent schemes. Character spans are evidence-only, never
  identity (A2 generalized).

# 11. OCCURRENCE IDENTITY — CANDIDATE CONTRACT

```
occurrence := [oracle_id, face, paragraph, clause]     — CANDIDATE
```

- `clause` = ordinal of the segment in the paragraph's canonical text,
  owned by the **segmentation** (conservation-gated `sentence_spans`
  machinery), **never by the matching extractor**. Extractors RESOLVE
  their match position into the segmentation; they never mint ordinals.
- Two derived facts belong to the same occurrence **iff** derived from the
  same segment.
- Snapshot-local; re-derived per refresh; halts on unresolved; zero human
  judgment — the ratified locality identity behavior, one coordinate down.
  Identity does **not** survive wording changes; continuity is a diff
  problem (§J of source (3); the §17 algebra classifies cross-snapshot
  changes as widened/narrowed/equal).
- The census key `(oracle_id, stem, occurrence index)` is **evidence**
  that occurrence counting is deterministic and reproducible; it is
  **not** the production identity (register #2).
- **`effect` (sub-clause ordinal): RESERVED, not adopted.** Sub-sentence
  effect-splitting is the repository's highest-measured-defect-rate
  machinery (the coordination-splitter family); coupling identity to it on
  day one makes every splitter bug an identity bug. The MEC probe (§27)
  prices the deferral before anyone pays it.
- Repeated identical clauses: distinguished by ordinal path. Legacy
  backfill quotes matching two units stay AMBIGUOUS — correct; their
  evidence genuinely cannot say which unit it came from. Forward-emitted
  facts are born with full addresses and never hit this.

# 12. PARTICIPANT MODEL — CANDIDATE

A flat integer coordinate identifying which argument of an occurrence a
constraint binds:

```
(occ, participant=0, REQUIRES(type, creature), REQUIRES-rel(controller, you))
(occ, participant=1, REQUIRES(type, creature), FORBIDS-rel(controller, you))
```

Prey Upon carried completely. Participant identity is **available
identically to both candidates** (register #3) — it discriminates nothing
about ownership or nesting. It is adopted for the benchmark because the
pre-registered questions already require it (Prey Upon, blink cohorts).

**THE COORDINATE STAYS A BARE INTEGER. A "participant_kind" field was
proposed and is WITHDRAWN (register #16)** — written in quotes, not
backticks, per the house rule that a rejected term in backticks is
ingested as ratified vocabulary. A single printed slot may range
over players *and* objects at once: CR 115.4 — *"These targets may be
creatures, players, planeswalkers, or battles"* — and CR 115.1 states the
general case, *"The targets are object(s) and/or player(s)."* Measured
2026-08-16: **1,528 corpus cards (4.7%)** carry such a slot (836 print
`any target`). A typing coordinate with a 4.7% exception rate is not a
typing coordinate. **Mixed-kind fillers are carried by §13's existing small
unions** — printed `or` classes, DNF ≤ ~4 disjuncts — and CR 115.4's
enumeration is exactly four. The filler *sort* is a constraint atom over a
§14 dimension, never a coordinate on the participant.

# 13. PREDICATE / NORMALIZATION MODEL — CANDIDATE

**Attachment (occurrence identity) and comparison (normalization) are
different problems. Occurrence identity does NOT answer equivalent /
broader / narrower / overlap / disjoint / unknown.**

Constraint atoms over an object's **value set** per dimension:

```
REQUIRES(dim, v)    v ∈ values(object, dim)      "blue permanent"; "artifact creature" = two REQUIRES (CR 300.2)
FORBIDS(dim, v)     v ∉ values(object, dim)      "nonland", "nonblack", "another"(excludes self)
CARD(dim, op, n)    |values(object, dim)| op n   "monocolored"=1, "multicolored"≥2, "colorless"=0
```

plus interval atoms (numeric thresholds), relation atoms (controller/
owner/self-exclusion), quantity `{min,max}` normalization, and the §15
context coordinates. Eligibility = base class ∧ atoms; printed `or`
classes = small unions (DNF ≤ ~4 disjuncts).

**Why complement-valued storage is WITHDRAWN (register #7), preserved so
no one re-derives it:**

1. **Multivalued conflation.** `nonland` as "has some type from
   COMPLEMENT({land})" wrongly ADMITS an artifact land (it has artifact);
   `nonblack` as HAS-complement wrongly admits a white-black creature (it
   has white). Printed meaning is NOT_HAS: the artifact land IS a land;
   the WB creature's colour set contains black. FORBIDS states NOT_HAS
   directly.
2. **CR-growth staleness.** A materialized complement over CR 205.2a went
   silently wrong the day the CR added `battle` — a carried-forward count
   in set form. `FORBIDS(land)` stores what the card says and is stable
   across every CR vocabulary refresh.

Negation is thereby confined to the atom; the algebra (§17) needs **no
formula-level negation**. These counterexamples are documentation, not
production fixtures — the benchmark adds them as negative-control
fixtures when authorized.

**THE FACET BOUNDARY — WHEN QUALIFYING RESIDUE MAY BECOME A CONSTRAINT
(Captain, 2026-08-16 — register #20).** This governs the *residue that
qualifies an already-identified semantic claim* — the leftover of a clause
the extractor has already claimed, in §18's sense of residue. **It does not
govern arbitrary text**, and it is not a licence to read unclaimed
material.

1. Such residue becomes a **constraint atom only when it maps to a
   RATIFIED §14 dimension contract.** No contract, no atom.
2. Residue that maps to no ratified contract **stays unresolved,
   uncontracted residue** and is reported as residue. It is never
   promoted, never approximated onto a neighbouring dimension, and never
   silently dropped.
3. **Qualification alone NEVER authorizes minting** a production axis,
   predicate, dimension or vocabulary item. A facet that "clearly wants"
   a new dimension is a ratification request, not an extraction result.

This is the sibling of §18.4. There, no contract means no *absence*
claim; here, no contract means no *constraint*. Both exist because the
tempting failure is identical — a dimension invented at extraction time
to hold something the text plainly says, which then looks original rather
than unratified. Recording it as residue keeps the gap visible and
countable; promoting it makes the gap disappear without anything being
decided.

# 14. DIMENSION SEMANTIC CONTRACTS — SHAPE IS CANDIDATE; ROWS ARE UNWRITTEN

A single exclusive/non-exclusive bit was insufficient (register #13). Each
dimension needs a contract carrying: vocabulary source (CR rule),
single- vs multi-valued, exhaustive or not, hierarchy edges (subtype→type),
whether CARD atoms apply, **applicable entity contexts** (§15), and static
CR anchors.

**CONTRACT SHAPE = CANDIDATE (benchmark subject). ROW VALUES = RATIFIED
FOR AQ4 as MINIMUM USEFUL v1, Captain 2026-08-16 (register #16).** The
global equality-only escape was offered and **REJECTED**: a real sheet is
what unlocks §18.4's ABSENT-PROVEN, and the blanket escape would have
forfeited it everywhere — including on the four CR 110.5 status rows,
where CR 110.5's own closing sentence makes absence proof free. Rows not
earning ratification are **equality-only or UNKNOWN**, never guessed.
**This ratification is for the AQ4 benchmark layer; it changes no
production semantics and mints no production vocabulary.**

`closed` = the CR enumerates every possible value. `must-have` = every
object in an applicable context carries one. **The two are independent**,
and conflating them is what turns a merely absent value into a false
ABSENT-PROVEN.

| dimension | CR anchor | closed | must-have | multi | context guard | v1 status |
|---|---|---|---|---|---|---|
| `card_type` | 205.2a | yes | yes | yes (300.2) | — | full |
| `subtype` | 205.3c/d | yes | no | yes | kind/zone | full — subtype→type edge sound (measured: 0 of 460 subtypes map to >1 type) |
| `supertype` | 205.4a | yes (5) | no | yes | — | full |
| `color` | 105 | yes (5) | no (colorless) | yes | — | full; CARD atoms carry mono/multi/colorless |
| `zone` | 400.1 | yes (7 + ante) | yes | no | — | full. **"Outside the game" is NOT a zone (CR 400.11) and is never a value** |
| `entity_kind` | 109.1 | **no — core only** | yes | no | — | core `{permanent, card, spell}`; every other CR 109.1 shape is **UNKNOWN unless contracted**, and **absence from the core is not proof** |
| `sort` (participant filler) | 102.1 / 109.1 / 115.4 | no | yes | no | — | **`player` is a contracted value** (register #16). Mixed slots are §13 unions, not a coordinate |
| `owner_relation` | 108.3 | yes | yes | no | — | full — an owner exists in **every** zone |
| `controller_relation` | 102.2 / 102.3 | yes | no | no | kind + zone | full, **complement inference FORBIDDEN** (below) |
| `self_identity` | 109.2d | n/a (atom) | n/a | no | — | full |
| `keyword_ability` | 702 | yes (194) | no | yes | kind | full |
| `tapped_untapped` | 110.5 | yes (2) | yes *(permanent)* | no | permanent only | full |
| `flipped_unflipped` | 110.5 | yes (2) | yes *(permanent)* | no | permanent only | full |
| `face_up_face_down` | 110.5 | yes (2) | yes *(permanent)* | no | permanent only | full |
| `phased_in_phased_out` | 110.5 | yes (2) | yes *(permanent)* | no | permanent only | full |
| `selection_mode` | 115.1 | **no — conservative** | yes | no | — | required; **unhandled shapes are UNKNOWN**, never coerced |
| `quantity` | 107.1 | `{min,max}` | no | no | — | interval only |
| `numeric` | 107.1 | integers | no | no | — | interval only; **the cardinality-WORD list is `H2 HAND-LIST` (§24), not EXTRACT-1** |
| `counter_kind` | 122.1 | **no — open** | no | yes | permanent/player | **equality-only** |
| `combat_state` | 506.3 / 508 | yes | no | no | permanent only | **equality-only v1** |
| `condition` | §17 v1 | no | no | yes | — | **equality-only** |
| `timing_duration` | §17 v1 | no | no | no | — | **equality-only** |

**CR 110.5 closes its own absence question.** *"There are four status
categories, each of which has two possible values… Each permanent always
has one of these values for each of these categories."* So on an applicable
permanent these four are exhaustive **and** must-have — ABSENT-PROVEN is
available on them without further machinery. They are four independent
rows because one grab-bag `state` dimension cannot say which category a
card constrains. Status is read from **oracle text**, never from a
characteristic (CR 110.5a, and no card field carries it — §19).

**CONTROLLER COMPLEMENT INFERENCE IS FORBIDDEN (Captain 2026-08-16 — the
benchmark is Magic-general and assumes no player count).**
`FORBIDS(controller, you)` does **not** entail `REQUIRES(controller,
opponent)` and never rewrites to it. CR 102.2 scopes the simple complement
to *two-player* games; CR 102.3 makes teammates *"all players not on their
team"* — neither you nor opponents. Measured 2026-08-16: 1,575 corpus
cards (4.9%) print one of the two forms and **only 6 print both**, so the
distinction is almost entirely cross-card and will surface in comparison
verdicts rather than in extraction. **Expect it to look like reduced
recall. It is not — do not "fix" it.** `owner_relation` and
`controller_relation` stay separate rows for the same reason: CR 108.3
gives every object an owner in every zone, while a card in a graveyard has
no controller at all.

**"historic_event_flags" was proposed and is REJECTED** (register #16; in
quotes, not backticks, for the reason §12 gives): no
CR rule enumerates it, and §15's own test applies — a feature that exists
only because a rules engine would need it is evidence against itself.
Anything genuinely required is reachable as a `condition` (equality-only).

**AN ACTION PREDICATE HEAD IS NOT A §14 DIMENSION (register #23).** The
action/effect head of an occurrence — what the instruction *does* — is a
**predicate**, and the rows above are **eligibility** dimensions describing
*what an object must be*. §27a's detector work adds no row here, contracts
no new dimension, and mints no vocabulary; its output is the CR 701 keyword
action already parsed at run time. Keeping the two apart is what stops a
detector improvement from arriving as a silent §14 ratification.

**NEITHER IS A COST (register #27).** COST is **structural ability content** —
a CR-grounded positional region (§23a), not an eligibility dimension and not a
predicate. **There is deliberately no cost row in the table above, and none may
be added by inference.** The consequence is the point: with no §14 contract over
cost, §18.4 has nothing to key on, so **no absence claim about cost is available
to either side** — structurally, rather than by a rule someone must remember.

**Hardcoded-intuition warnings (each is a measured or CR-verified trap):**

- Card **types are NOT mutually exclusive** (CR 300.2 — artifact
  creatures, land creatures exist).
- **Colours are NOT exclusive** (multicolour) and NOT exhaustive
  (colourless exists).
- **Controller does not exist in every context** — cards in graveyards
  have owners, not controllers.
- **Tapped/untapped exists only for battlefield permanents.**

# 15. ENTITY CONTEXT — CANDIDATE, CR-GROUNDED

`target creature`, `target creature spell`, and `target creature card in
your graveyard` are three different entity kinds and MUST NOT normalize
identically. **CR 109.2** is the static decision rule (bare type word ⇒
permanent on the battlefield; "card" ⇒ card in the named zone; "spell" ⇒
on the stack); **CR 110.1** ("`<type>` card is not a permanent") is
already enforced in the object lattice (the Auriok Salvagers fix,
`PICK-UP-HERE.md` §0AA).

Normalized objects carry `entity-kind ∈ {permanent, card, spell}` (+
token/nontoken flag, CR 111) and `zone` (+ owner relation). **All
subsumption and entailment is guarded by kind/zone compatibility**;
cross-kind predicates are incomparable-by-kind (register #10).

**Boundary — IN SCOPE:** static semantic classification from canonical
text, admissible card characteristics, and the CR. **OUT OF SCOPE,
always:** live game-object binding, legal-action generation, priority,
state-based actions, layers, APNAP, replacement-loop execution, combat
simulation, game-state mutation. If a proposed feature exists only
because a rules engine would need it, that is evidence against it.

# 16. STATIC COREFERENCE AND RELATIONS — CANDIDATE

- **Static semantic reference structure** ("that creature", "that card",
  CR 607 linked abilities, effect-B-depends-on-participant-of-A) is IN
  SCOPE — Budget Swapper cannot distinguish Cloudshift's exile-and-return
  from removal without it, and explanation needs it.
- **Runtime object binding** ("which creature is that *now*") is OUT OF
  SCOPE, permanently.
- Representation candidate: typed relation edges
  `(kind, from-occ/participant, to-occ/participant)`; kinds currently
  needed: CR 607 linkage, same-card coreference, conditionality (+ delayed
  marker).
- **Scope locks:** same-card references only; edges name
  participants/occurrences, never game objects; an unresolvable reference
  stays UNRESOLVED, never guessed. The creep line: any consumer question
  requiring evaluation of the reference against game state is out of
  contract.

# 17. COMPARISON ALGEBRA — CANDIDATE, DERIVED-ONLY

Small and closed by construction: conjunction (storage shape), small
printed unions, per-dimension entailment (set/interval math over CR-closed
vocabularies), REQUIRES/FORBIDS interaction, CARD constraints, equality
(mutual entailment), overlap/disjointness (driven by the §14 contracts),
subtype→type hierarchy (EXTRACT-3 — exists), context-guarded application (§15),
quantity `{min,max}` comparison, zone/origin-destination componentwise
comparison, ChoiceGroup alternative-vs-cumulative (derived from the owning
header per ratified A4; derived-and-materialized in generated artifacts,
never codebook-stored).

**OVERLAP AND DISJOINT ARE NOT SYMMETRIC, AND NON-CONTRADICTION PROVES
NEITHER (Captain, 2026-08-16 — register #17).** Two constraints can
contradict on no dimension whatsoever and still have an EMPTY intersection,
so "no contradictory dimension pair" must never be read as OVERLAP:

- **OVERLAP = `PROVEN` only on a positive WITNESS** — one card satisfying
  both. Existential, so a single card settles it; but it is a claim about
  the **corpus**, so the assertion carries `corpus_ref` (§19).
- **DISJOINT = `PROVEN-NOT` only on a CR CONTRACT contradiction** —
  contradictory values on a single-valued exhaustive §14 dimension.
  **Never** on the absence of a witness.
- **Everything else is `UNKNOWN`**, including *"searched and found
  nothing"* — the standing house law that a null result from your own
  search is not a fact about the data.

A corpus witness is therefore **sufficient** for overlap, **necessary** in
practice for most overlaps, and **inadmissible** for disjointness.
Per-dimension contracts alone cannot establish a nonempty intersection:
they describe a product space, and the printed pool is sparse inside it.
Measured 2026-08-16 over CR-closed vocabulary: **54.8% of supertype ×
creature-subtype cells are empty** while the CR forbids none of them —
there are 61 snow creatures and 1,078 Soldiers and **zero** snow Soldiers;
3,406 legendary creatures and 107 Drakes and **zero** legendary Drakes.
This is the common case, not a corner. **No new verdict values are minted**
— the rule maps onto the existing triple, and `proof_kind` is provenance
(§19), not a fourth state.

- **Every comparison returns `PROVEN / PROVEN-NOT / UNKNOWN`.**
- **Derived relationships are NEVER canonical stored facts.**
  `blue permanent ⊂ permanent` is a consequence of monotonicity, not a
  row. *Store the smallest canonical facts; derive relationships.*
- Ownership of the underlying fact rows remains **the** AQ4 decision —
  nothing in this section pre-commits it.
- Deliberately absent: formula negation, quantifier reasoning, theorem
  proving, "for each" resolution, timing/duration/condition entailment
  beyond equality (v1), any operation without a named consumer question.

# 17a. THE SHARED COMPARISON ALGEBRA — REPAIRED AND FROZEN (register #31–#39)

**✅ PACKET 7 IS FROZEN at `aq4-comparison-algebra` 2.0.0**, consuming the
Packet-4 projection at 2.0.0. The corrective implementation superseded the
quarantined attempt and passed validation.

**⛔ THE QUARANTINED ATTEMPT IS NOT REHABILITATED.** Commit `4e2ff09` crossed a
pre-registered STOP and embedded unratified law; it stays in history as
evidence and **nothing in it carries authority**. It was superseded, never
adopted. Incident record:
`docs/INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md`. **Every defect that
record names is repaired**, and the repair is a forward commit — `4e2ff09` was
neither amended nor reverted.

**What the freeze covers:** the operation table, the three verdicts, the two
proof kinds, the distinguishing-witness role and its decidability
restrictions, the corrected contradiction semantics, the six B2 labels, B1's
and B3's intentional partiality, C3 over projected choice-group structure, and
the proof/precondition boundary. **It does not cover scoring, an answer key,
a candidate encoder or the unit binding**, none of which exists.

## 17a.1 What is RATIFIED NOW (Captain, 2026-08-17)

**No positive whole-unit semantic-equality proof exists in v1.** The only
ratified positive equality operation is the one §17 already froze —
**mutual entailment of normalized eligibility/constraint sets** — and it must be
named unambiguously (`ELIGIBILITY_EQUALITY`, or a repository-native equivalent).
**A bare unqualified operation name meaning whole-unit "equality" must not be
used, and no generic whole-unit equality operator may be created.**

For the consumer question B1: **PROVEN whole-unit equality is UNAVAILABLE in
v1.** PROVEN-NOT is permitted only where a semantic difference is independently
proven under currently-authorized law — in v1 that is eligibility equality
proven negative by an admissible distinguishing witness. Everything else is
UNKNOWN.

**None of the following is positive proof of whole-unit semantic equality:**
identical action heads · identical participant integer sets · no relation edge ·
no cost region · absence of visible residue · any *"all projected fields match"*
argument. **The reason is structural, not stylistic:** the Packet-4 projection
does not represent all possible uncontracted semantic residue, so equality of
projected content is not equality of semantic content.

**A key-side completeness-attestation field is NOT introduced in v1.** It is
**deferred, not rejected forever.** The existing cost-equality-safety law
(register #27) stands as a blocker principle and **authorizes no positive
proof**.

**The distinguishing-witness role is granted.** One admissible printed-card
witness that satisfies one side and demonstrably violates the other proves
non-entailment. **This is an additional ROLE for the existing corpus-witness
proof kind — not a third proof kind.** Witness absence proves nothing; a failed
search stays UNKNOWN; and corpus incompleteness can never invalidate a witness
that is present, because presence proves existence while absence proves nothing.

**The witness may prove violation only where the violated consequent is
decidably false under the frozen dimension contract:**

| consequent | may a witness prove violation? |
|---|---|
| a forbidding atom | yes, where the forbidden value's presence is evidence-admissible |
| a requiring atom | **only** with an evidence-traced COMPLETE assignment for that dimension, sufficient to establish that no required value is present |
| an equality-only dimension | **no** — a value or text mismatch is not automatically violation and stays UNKNOWN unless existing law independently proves it |
| a malformed cardinality or interval payload | **never** — malformed input is invalid and UNKNOWN, and must be rejected once Packet-4 validation is repaired |
| an open vocabulary or an incomplete assignment | **no negative inference at all** |

Such a proof record carries the corpus reference, the witness identity, the
admissible evidence, the governing dimension contract, and any completeness
declaration relied upon.

**The summary label set for B2 is amended to six values** — EQUAL, BROADER,
NARROWER, OVERLAPPING, DISJOINT, UNKNOWN. **EQUAL is never mapped to
OVERLAPPING**, and requires eligibility equality PROVEN. **BROADER and NARROWER
are STRICT**: the containing direction must be PROVEN *and the reverse direction
must be PROVEN-NOT.* One direction proven with the reverse UNKNOWN is **not
enough** and is UNKNOWN. OVERLAPPING still requires the positive intersection
proof, and **overlap is never inferred from equality** unless the witness
obligation is independently discharged. DISJOINT follows the existing
empty-intersection law.

**B3 remains intentionally PARTIAL, and no action-equivalence operator is
added.** Semantic action heads may be surfaced structurally for audit, but an
identical head sequence is not positive proof of semantic equivalence, differing
heads do not prove non-equivalence, and an unresolved head blocks overclaim. The
action-equivalence arm is **UNKNOWN** until a separately ratified action
comparison exists. **The frozen pairing is NOT redrawn**: the measured near-zero
positive yield on the same-delivery contrast tranche is benchmark evidence, and
evidence is not authorization to move a pre-registered population.

**A NON-BLOCKING CHECK IS NOT A PROOF.** No component may be emitted as PROVEN
with a contract proof kind for *no cost region observed* · *no relation edge
observed* · *action-head sequences identical* · *participant integer sets
identical* · *another blocker simply not firing*. A structural guard that was
evaluated and did not block is recorded as **derived audit/precondition
metadata only**: no verdict, no proof kind, no anchor. **Only genuine semantic
proof components enter the three-valued composition, and a contract proof must
cite a real applicable rule anchor — prose describing a precondition is never an
anchor.**

## 17a.2 Existing-law CLARIFICATIONS (no new law)

**Participant integers are LOCAL to one semantic occurrence.** Participant 0 on
one card and participant 0 on another have **no cross-card semantic meaning by
themselves**, and participant-set identity is never positive evidence for B1 or
for any cross-card equality. **No printed-order cross-card participant
correspondence is ratified here**; if future comparison needs correspondence
beyond the frozen attachment law, that is its own benchmark contract.

**The coverage and non-vacuity guards remain required**, because a missing fact
is not a proven absence, two projection-empty constraint sets are not thereby
proven unconstrained, and sparse representation must never be read as equality.
**Two genuinely adjudicated constraint-free cases may still prove eligibility
equality under existing absence law.**

**Empty intersection may be established** by a same-value requiring-versus-
forbidding pair, by incompatible required values on a contracted closed
single-valued domain, by disjoint cardinality ranges, or by disjoint intervals —
**where their frozen semantics actually contradict.**

**One correction, and it is a defect in the quarantined implementation.** For a
DISJUNCTIVE required value set against a forbidding constraint, contradiction
exists **only if the complete allowed disjunction is eliminated.** Requiring
*artifact or creature* against forbidding *artifact* is **not** a contradiction,
because creature remains satisfiable. An *"any overlap means contradiction"*
implementation is wrong and is repaired in the technical task.

## 17a.3 Repair status

**✅ ALL DONE.** The two Packet-4 repairs (register #38) are performed at
projection schema 2.0.0, and the **Packet-7 corrective implementation** is
performed at comparison-algebra 2.0.0. Packet 7 is **FROZEN**.

**What the repair removed, and did not revive:** the generic whole-unit
equality operation and its self-designed necessary-condition list · action-head
identity, relation-edge absence, cost-region absence and participant
integer-set identity as comparison conditions · PROVEN components carrying a
contract proof kind for a check that merely did not block · prose in a
contract-anchor field · a false disjointness proof on partially-forbidden
disjunctions · the cardinality and interval payload readings, now Packet-4 law.

**Measured effect of the repair**, on the same 5,184-pair synthetic sweep the
audit used: the removed whole-unit operation's **12** positive verdicts are
gone, because v1 has no proof for them; the eligibility operation is
**byte-for-byte behaviour-preserving** on equivalent occurrence-scoped input
(1,728 proven, unchanged); and the participant-correspondence restriction moves
**1,728 → 0** positive verdicts on participant-scoped input. The false
disjointness reproduced as `PROVEN-NOT` before the repair and is `UNKNOWN`
after, while the genuine all-alternatives-forbidden case still proves.

## 17a.3a THE COST OF THE PARTICIPANT RULING, STATED PLAINLY

**Eligibility comparison is unreachable on PARTICIPANT-scoped constraints**, and
that follows directly from 17a.2 rather than from an implementation choice. A
constraint describing *what an object must be* is normally scoped to a
participant, so on realistic input the operation will answer UNKNOWN far more
often than the operation table alone suggests.

**This is the conservative direction and it costs nothing today** — no
projection instance and no answer key exists — but it is the single largest
practical limit on B1, B2 and C1, and it is recorded here rather than
discovered later. **The remedy is a benchmark contract for participant
correspondence**, which 17a.2 already names as the required route. Until then
the comparator declines instead of aligning integers the contract says do not
correspond.

## 17a.4 DEFERRED

The key-side completeness attestation that would be required before any positive
whole-unit equality proof could exist. **Deferred, not rejected.** Reviving it is
a Captain ratification and nothing else.

# 18. UNCERTAINTY AND ABSENT-PROVEN — LOAD-BEARING

**Empty textual residue ≠ semantic completeness** (register #8). Residual
exhaustion proves *no unclaimed clause material remains*; it does NOT
prove *claimed material was fully represented* — an open capture can
consume `target creature with flying` and emit only `creature`, losing
flying with zero residue. This is the repository's recorded
"conservation is structural and cannot see content" trap, one layer up.

**ABSENT-PROVEN(dim, occurrence) requires ALL FOUR:**

1. **Residue-honest exhaustion** — zero residue under the claiming rule:
   *only literal template tokens and closed-vocabulary matches may claim
   text; text matched by an open capture group is residue by definition.*
2. **Template adequacy** — every claiming template ratified WITH its
   emission schema (the existing DET ratification law + one adequacy
   sentence).
3. **Per-dimension negative control** — adding a `dim` restriction to a
   matched card MUST change the output (new fact or new residue).
4. **Registered dimension contract** (§14) — no contract, no absence
   claims, ever.

**WHO DISCHARGES WHICH OBLIGATION (Captain, 2026-08-16 — register #26).**
The four obligations do **not** all sit on the same party, and reading them
as key-side made the answer key responsible for properties of encoders that
did not exist when it was written.

- **The KEY records the underlying semantic ABSENCE** — that the text
  places no constraint on that dimension for that occurrence. That is a
  statement about the card, and the key can make it.
- **Obligations 1–3 are discharged by the CLAIMING CANDIDATE at
  scoring/evaluation time**, under *that claimant's own* rule: residue-honest
  exhaustion, template/emission-schema adequacy, and a per-dimension negative
  control that changes *that claimant's* output. A key cannot prove them on
  behalf of a future encoder, and **the key never claims pre-encoder
  ABSENT-PROVEN.**
- **Obligation 4, the registered dimension contract, stays
  benchmark-law/ground-truth-side** (§14). No contract, no absence claim, by
  either party.

This preserves the symmetric false-precision veto (§6.2) in both directions:
a candidate claiming ABSENT-PROVEN it cannot discharge is confidently wrong,
and a key asserting absence the card does not support is equally so.

**Dispositions** (per occurrence × participant × dimension):
`PRESENT(value) · ABSENT-PROVEN · UNRESOLVED · AMBIGUOUS ·
HUMAN-RESOLVED`. Do not invent additional states.

**`HUMAN-RESOLVED` FOR AQ4 EVALUATION (Captain, 2026-08-17 — register #28).**
It means *semantic content x resolved by human adjudication under the ratified
AQ4 adjudication procedure* — **not** "a Captain ruling", which is the older and
now too narrow reading. The **method** (single · independent dual · deterministic
sampled second · Captain ruling · disagreement-resolution status) is metadata of
the containing key/adjudication artifact and **is never a disposition value**;
encoding a method as a disposition is refused by the validator. **Captain remains
the final governance authority** — what the amendment changes is who may
*produce a key cell* under register #24's protocol, never who decides.

**Wrapper transparency.** `HUMAN-RESOLVED(x)` carries `x`. Later comparison may
consume the semantic payload while the wrapper stays in provenance/audit
metadata.

**Sides.** `HUMAN-RESOLVED` is **key/adjudication-side only**; a candidate
export may never emit it. `ABSENT-PROVEN` is **claimant-side only**. So key
absence is `HUMAN-RESOLVED(absent)` where a candidate would claim
`ABSENT-PROVEN`, and **no sixth disposition is created**. Both directions are
rigged-red controls in `aq4_projection.py`.

**Consumer law (PRE-REGISTERED):** strict replacement relies only on
PRESENT and ABSENT-PROVEN; UNRESOLVED on a consumer-critical dimension
blocks the strict claim (and only the strict claim — discovery/ranking may
proceed with the caveat); **UNKNOWN/UNRESOLVED MUST NEVER silently become
ABSENT.** A slightly incomplete honest representation beats a fully
populated wrong one — that asymmetry is why the false-precision veto
exists.

# 19. PROVENANCE / DEBUGGING CONTRACT

Every consumer answer must be traceable:

```
characteristic field / Oracle text
  → evidence span OR named characteristic evidence   (evidence law + §8 register #12 riders)
  → paragraph owner [face, paragraph]                (ratified locality)
  → occurrence [.., clause]                          (INV-1 prefix consistency)
  → participant ordinal
  → canonical predicate row {dim, value/atom, disposition, extractor version,
                             derivation class, CR anchors, provenance class}
  → derived relation {input row ids, per-dimension verdicts,
                      proof_kind, corpus_ref if CORPUS_WITNESS}  (recomputed, never stored)
  → index projection (regeneration-gated)
  → consumer answer (cites the verdicts)
```

Minimum required: extraction bugs localize to a row's span + extractor;
normalization bugs to a verdict's CR anchor; one bad derivation is
invalidated by fixing one input fact, never by rebuilding unrelated facts;
a reviewer disputes one fact row without discarding the occurrence
(existing assertion-granularity dispute model); a failed strict
replacement names its dimension, verdict, and both evidence rows. Human
vs deterministic provenance classes remain distinct throughout. This is a
contract, not a database design — do not build heavyweight provenance
infrastructure to satisfy it.

**PROVENANCE CONSERVATION — A PRE-REGISTERED CONTROL CLASS, NOT A NEW
FIELD (Captain, 2026-08-16 — register #21).**

**The law.** Any normalization or lowering transform that receives
source-grounded semantic material **must preserve a deterministic trace
from every surviving output semantic fact back to admissible source
evidence.** Surviving is the operative word: a transform may legitimately
drop a fact, and dropping is not a trace failure. Carrying a fact forward
*without* its trace is.

**The control.** Every applicable transform ships a **negative control of
class `DROP_OR_CORRUPT_TRACE`**: break the trace deliberately — sever one
output fact's link, or corrupt it to point at the wrong source span — and
the check **must turn red**. A trace check that has never been shown to
fail is not known to be a check, which is this repository's recorded
"reporters listed as gates" finding. Each such control is demonstrated
rigged-red, exactly as §24's per-derivation-class controls are.

**This adds NO canonical provenance field.** §19's trace above already
carries what is needed; this pre-registers the *obligation and its
control*, not a new row, column or store. Nothing here may be cited to
justify a schema addition.

**Timing.** Pre-registered **now**, deliberately, while no normalization
or lowering pass exists — a control written after the transform it guards
is a control shaped by what that transform happens to do. Candidate
implementations satisfy it when those passes are actually built (packets
5–7). **No candidate code is written for it here**, and its absence today
is not a gap.

**Candidate-neutral by construction.** The obligation is stated over "any
transform receiving source-grounded material", so it binds OCC-FACET and
MIN-IR identically and prices neither. A candidate that normalizes more
aggressively carries more trace obligation — which is a fact about that
candidate, and is exactly what the benchmark is for.

**`proof_kind` is PROVENANCE, never canonical semantic truth (Captain,
2026-08-16 — register #17).** A §17 comparison verdict records **how** it
was established: `CR_CONTRACT` (a contradiction on a single-valued
exhaustive §14 dimension) or `CORPUS_WITNESS` (a named card satisfying
both). A `CORPUS_WITNESS` assertion **must carry the `corpus_ref` it was
established against**, because it is a claim about the printed pool and a
later snapshot may add the card that was missing. `proof_kind` is a field
on the derived relation — it is **not** a fourth verdict value, **not** a
stored semantic fact, and nothing may branch on it except the audit trail.

**A NON-BLOCKING CHECK IS NOT A PROOF (Captain, 2026-08-17 — register #37).**
A structural guard that was evaluated and did not block carries **no comparison
verdict, no `proof_kind` and no anchor.** It is recorded as derived
audit/precondition metadata only. Specifically, none of *no cost region
observed* · *no relation edge observed* · *identical action-head sequences* ·
*identical participant integer sets* · *another blocker simply not firing* may
be emitted as a PROVEN component carrying a contract proof kind. **Only genuine
semantic proof components enter the three-valued composition.**

**A contract proof must cite a real applicable rule anchor. Prose describing a
precondition is never an anchor.** Measured 2026-08-17 in the quarantined
Packet-7 implementation: four components asserted a contract proof kind with no
contract behind them, three of them carrying prose in the anchor field, and two
were structurally absence claims of a kind register #27 says cannot exist on
either side — arriving through the proof channel instead of the dimension
channel. Removing them moved **0 of 5,184** top-line verdicts, which is the
point: **the damage was entirely to the trace, and the trace is what the
false-precision veto reads.**

**Evidence categories — three, and no registry (Captain, 2026-08-16 —
register #18).** The minimum the §20 questions actually require is
`ORACLE_TEXT` (every constraint value, including CR 110.5 *status
references*, §16 relation edges, selection mode and keyword restrictions),
`CANONICAL_CHARACTERISTIC` (cohort 7 only — vanilla creatures, CR 113.3a
face cuts, DFC layout; register #12's two riders already govern it), and
`CR_DERIVED` (vocabulary, hierarchy edges, contract cells — contract-level,
not per-card). **A generic fact-category → evidence-source registry was
proposed and is declined:** it was designed for a failure that does not
exist. Status looked like it needed one because CR 110.5a says *"Status is
not a characteristic"* — but measured 2026-08-16, **zero of the 69
available card fields carry CR 110.5 status.** A static corpus has no
tapped permanents; status is never *observed*, only ever *referenced in
oracle text*, and is therefore already inside the strictest boundary.

**Characteristic evidence — status warning.** Production evidence law is
RATIFIED as oracle-quote-or-discard and is **unchanged by AQ4**. The
characteristic-inclusive boundary this trace begins with is a
**CANDIDATE** (register #12), exercised only inside the evaluation
projection — cohort 7 of §21 exists precisely to test it. If the selected
architecture requires characteristic-evidenced canonical facts in
production, that evidence-boundary change is an **explicit, separate
Captain ratification** and a precondition of retrofit (it appears in the
§29 preamble for that reason).

# 20. CONSUMER-QUESTION CONTRACT (current set; older PREQ-1–PREQ-12 superseded, register #14)

Answers pre-committed per benchmark card in projection vocabulary — open
cohorts before encoding; blind cohorts (4–5) adjudicated per §22's
sequence, always without access to candidate outputs (§6.5's invariant).
No rules-engine questions.

**A. Within-card attachment**
- ATTACH-1. Which occurrence performs action X, on what object class?
- ATTACH-2. Which participant does each restriction modify?
- ATTACH-3. Which occurrence does each cost / condition / duration / destination
  belong to?

**B. Cross-card mechanical comparison**
- B1. Are U_A and U_B semantically equal under normalization despite
  different wording?

  **PARTIAL IN v1, ratified Captain 2026-08-17 (register #32).** There is **no
  positive whole-unit semantic-equality proof in AQ4 v1** and no generic
  whole-unit equality operator may be created. PROVEN is **UNAVAILABLE**;
  PROVEN-NOT only where a semantic difference is independently proven under
  authorized law; otherwise UNKNOWN. The refused positive arguments are
  enumerated in §17a.1 — the reason is that the projection does not represent
  all uncontracted semantic residue, so matching projected content is not
  matching semantic content.

- B2. Is A's eligibility broader / narrower / overlapping / disjoint /
  UNKNOWN vs B's — and which per-dimension verdicts produce the answer?

  **SUMMARY LABELS AMENDED TO SIX, ratified Captain 2026-08-17 (register
  #34):** EQUAL · BROADER · NARROWER · OVERLAPPING · DISJOINT · UNKNOWN.
  EQUAL requires eligibility equality PROVEN and is **never** mapped to
  OVERLAPPING. **BROADER and NARROWER are STRICT** — the containing direction
  PROVEN *and* the reverse PROVEN-NOT; one direction proven with the reverse
  UNKNOWN is UNKNOWN. OVERLAPPING still requires the positive intersection
  proof and is never inferred from equality.

- B3. Actions equivalent while eligibility differs?

  **INTENTIONALLY PARTIAL, ratified Captain 2026-08-17 (register #35).** No
  action-equivalence operator is added. The eligibility arm answers; the
  action-equivalence arm is **UNKNOWN** until a separately ratified action
  comparison exists. Heads may be surfaced structurally for audit only, and
  the frozen pairing is **not** redrawn to accommodate the measured yield.

- B4. Eligibility equal while destination / timing / quantity differs?

**C. Strict Budget Swapper**
- C1. What exact fact (dimension, verdict, both evidence rows) prevents B
  from strictly replacing A?
- C2. Is A's exile linked to a return (blink test)?
- C3. Are U1 and U2 alternatives, cumulative, or independent?

**D. Broad discovery / similarity**
- DISCOVERY-1. Which broad facts remain shared despite narrower predicates — and
  answerable from indexes alone, without assembling full structure?

**E. Explanation**
- E1. Why did these cards match, and which part of each card produced the
  comparison (full §19 trace)?

  **DOMAIN AND FORM, ratified Captain 2026-08-16 (register #26).** E1's
  domain is the **354 unique unordered pairs of S0 ∪ S1 ∪ S2** — the
  semantic tranches of the frozen pairing (§8a of the benchmark README).
  It is **not** multiplied by the number of comparison questions asked of a
  pair, and it does **not** apply to `PAIR_K_CHAIN`-only control pairs,
  which are semantics-free by construction. E1 is scored as a **§19
  trace/provenance property** — the derivation is producible and names the
  semantic units that support the comparison — and explicitly **not** as one
  hand-authored prose explanation string per pair. A prose gold answer would
  be an unscoreable free-text surface and would smuggle native vocabulary
  into a key that §6.1 requires to be architecture-neutral.

**F. Honesty / unresolved behavior**
- HONESTY-1. Which consumer-relevant dimensions are UNRESOLVED/AMBIGUOUS, and
  does that block a strict claim the facts would otherwise support?
- HONESTY-2. For a fully parsed clause: demonstrate ABSENT-PROVEN by the §18
  contract, not by omission.

# 21. BENCHMARK POPULATION — PRE-REGISTERED

Eight cohorts. **Named cards are seeds for structural classes, not the
population**: (1) historical Foundry failures (Active Volcano; the
flattened-modal class; documented semantic-loss cases); (2) structural
adversaries (multi-participant — Prey Upon class; multi-effect paragraphs
— Kalitas class; repeated identical clauses — Seize the Soul class;
linked abilities CR 607; delayed effects; coreference — Cloudshift class;
modal structures incl. Spree; entity-context triplets — creature vs
creature spell vs creature card); (3) simple controls (≤5); (4)
deterministic stratified random sample (committed script + seed,
stratified by delivery token × action family, from the gated corpus); (5)
blind holdout (§22); (6) consumer-critical families (removal, blink,
counterspells, ramp — half open, half in the holdout draw); (7)
CR/characteristic-derived cases (vanilla creatures, CR 113.3a face cuts,
DFC layouts); (8) negative/unresolved cases where the correct output is
refusal.

Development may consult 1–3, 7–8, and the open half of 6. Cohorts 4–5
stay uninspected until extractor freeze; 5 until evaluation. Trap cohorts
seed from the measured failure inventory (CLAUDE.md traps; NC-A…E of
`FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md`).

# 21a. CARD CASE WITH EXPLICIT UNIT BINDING (register #36)

**Ratified Captain 2026-08-17. NOT YET INSTANTIATED — the binding artifact does
not exist and this section does not create it.**

§20's cross-card questions are phrased over **units**; the frozen pairing binds
**cards**. Register #19 closed the card-level instantiation and left the unit
level unstated, so nothing bound a pair to the units its questions actually
compare.

**The population does not change.** It stays the **354 unique semantic card
pairs**, and it is **NOT** expanded into occurrence cross-products. (Measured
2026-08-17, the cross product is **3,030** unit pairs — an order of magnitude,
decided by implementation rather than by contract, which is why this is ruled
rather than left to a later session.)

**One neutral PRIMARY unit binding per semantic pair**, created and frozen
**before any answer-key truth exists and before either candidate exists**, and
reused by every pair-level question instantiated for that pair. **The binding
layer is benchmark administration and ground-truth instantiation. It is not a
semantic comparison verdict.**

**Method — hybrid, and both arms are required.**

1. a **deterministic default** wherever frozen machinery uniquely resolves the
   intended occurrence. It may use the corrected semantic detector for binding,
   but **MUST NOT modify the frozen Packet-2 pairing coordinate**, which stays
   legacy by ratified history (§27a);
2. **human-adjudicated binding** wherever it does not, frozen before encoders
   and carrying its adjudication method and provenance.

Multi-occurrence ambiguous cases belong to the **high-risk** class of the
ratified open-key adjudication protocol (register #24).

**Binding state is `BOUND` or `NOT_APPLICABLE`, and the second is
ADMINISTRATIVE ONLY.** It is **not** a semantic disposition, **not** a
comparison verdict, **not** UNKNOWN and **not** PROVEN-NOT. It records a card
case with no valid semantic unit — including the known no-oracle-text shape, of
which the published open set carries **6** — and **no semantic verdict is
invented for such a side.**

**The minimum record, conceptually:** pair identity · tranche · each side's
occurrence address or null when not applicable · binding method · binding state
· a required reason when not applicable · evidence and adjudication metadata
where applicable. **Every bound occurrence must validate against the frozen
semantic occurrence surface.**

# 22. HOLDOUT PROTOCOL — EVERY ESCAPE HATCH CLOSED

**Core principle (PRE-REGISTERED): a valid holdout is NEVER redrawn
because candidate performance was unexpectedly poor. Poor performance is
evidence** — against one candidate's extraction story, or (both) evidence
that extraction is harder than the open cohorts suggested, feeding the
verdict via tiers THIRD and SIXTH.

**Sequence — BEFORE any candidate scoring:**

1. precommit primary holdout seed hash (`sha256(seed)`);
2. **optionally precommit ONE reserve seed hash** at the same moment;
3. freeze both candidate implementations at named commits;
4. reveal seed; regenerate the population;
5. verify seed against commitment;
6. audit the sampling procedure against the committed script;
7. verify the corpus snapshot sha;
8. verify zero development leakage (holdout ∩ development = ∅; no
   pre-freeze inspection);
9. adjudicate the complete holdout answer key by **INDEPENDENT DUAL
   ADJUDICATION** (see below) — in projection vocabulary, from the cards
   and the CR, **without access to any candidate output**;
10. freeze and hash the answer key;
11. record procedural PASS **in writing**;
12. only then expose candidate outputs and score.

**INDEPENDENT DUAL ADJUDICATION — step 9's procedure (Captain,
2026-08-16 — register #22).**

- **Two adjudicators, A and B, answer the whole blind key separately.**
- **Neither may see any candidate output**, at any point before the key
  is frozen and hashed (step 10). This is the §6.5 invariant, now
  enforced twice over.
- **They do not share initial answers.** A and B work from the cards, the
  CR and the frozen contract alone; an adjudication anchored on the
  other's answer is one adjudication wearing two names.
- **On disagreement:** each **independently rechecks** against the frozen
  contract, the CR and the evidence. Resolution happens **only while
  candidate outputs are still invisible.**
- **If they still disagree, the cell is `AMBIGUOUS` or `UNRESOLVED`** —
  and that is a *result*, not a failure to be tidied away. §18's law
  applies unchanged: a slightly incomplete honest key beats a fully
  populated wrong one, and forcing agreement to fill a cell is exactly
  the false precision the symmetric veto exists to punish.
- **CANDIDATE OUTPUTS MAY NEVER BE USED TO RECONCILE THE TWO
  ADJUDICATIONS.** Reconciling against outputs would let the candidates
  vote on their own answer key — the single failure this whole section
  exists to prevent, arriving through the one door the timing rules left
  open.

**It is deliberately NOT called "double-blind", and the name matters.**
Double-blind names an experimental design in which neither subject nor
experimenter knows the treatment assignment. There is no treatment
assignment here and the adjudicators are not blind to the cards — they
are blind to **candidate outputs only**, which is a weaker and more
specific property. Calling it double-blind would claim a design this
benchmark does not have, and an overclaimed method is a defect in the
same family as an overclaimed count.

**The reserve seed may activate ONLY if the primary fails steps 5–8
BEFORE scoring begins.** Once scoring begins: no performance result
triggers redraw, ever. A post-score demonstrated answer-key error is
recorded permanently and voids that card **symmetrically for both
candidates** — never the holdout. If post-score key defects are so severe
the run is untrustworthy, the verdict is
**`INSUFFICIENT EVIDENCE / BENCHMARK COMPROMISED`** — the run is
preserved in the packet, and there is **no silent fresh attempt inside
the same evidence packet**. *(This severity rule and the reserve-seed
mechanism are CAPTAIN-SUPPLIED PROTOCOL AMENDMENTS — register #9b — not
prior Fable design.)* Every draw, including invalidated ones, remains in
history, labeled.

# 23. OWNERSHIP-NEUTRAL EVALUATION PROJECTION

The shared normalized fact table is an **EVALUATION PROJECTION** — never
the assumed canonical store. Both candidates export into it; each
candidate's native answers MUST match its own projection's answers
(self-consistency); exporter implementation cost is excluded from scoring;
only a *lossy* projection is scoreable evidence.

**`FACT_PROJECTION` — THE OPEN KEY'S SHAPE, ratified Captain 2026-08-16
(register #25).** Open benchmark truth is frozen as this
**ownership-neutral normalized fact/projection substrate**, with the
per-question consumer answers of §20 **derived** from it. It is not stored
as one large per-question answer store: that duplicates a single fact across
every question that reads it, gives the key no self-consistency check, and
makes a single corrected fact a multi-cell edit.

**Read the scope narrowly, because the words invite over-reading.** This is
**benchmark EVALUATION law only.** It does **not** rule that normalized fact
rows are canonically owned in production — models A–D above stay open, that
is the AQ4 decision itself, and §34's list of things a future model must not
infer applies to this paragraph in particular. It authorizes **no** candidate
encoder, mints no vocabulary, and changes **no** §22 blind timing: the blind
key is still adjudicated after candidate freeze under §22's sequence.

Ownership possibilities the benchmark must leave open:

- **MODEL A** — broad assertions canonical; semantic refinements derived.
- **MODEL B** — broad assertions + predicate rows canonical; occurrence
  addresses derived.
- **MODEL C** — semantic fact rows canonical; axes/assertions become
  projections/indexes.
- **MODEL D** — a bounded hybrid; the verdict names which row kinds are
  canonical.

Tiers FIRST–FOURTH (§26) run on the projection and are **ownership-blind
by construction**. Ownership is discriminated only where it genuinely
differs: migration cost, guard conservation, human-ruling preservation,
refresh behavior and canonical identity churn, mutation/ratification
path, durability surface (P3/C6), projection/regeneration obligations,
reversibility — tiers FIFTH and SIXTH.

# 23a. THE FROZEN PACKET-4 PROJECTION (register #27–#30, amended by #38)

**Artifacts.** `experiments/aq4_benchmark/evaluation-projection-schema.json`
(schema `aq4-evaluation-projection`, **version 2.0.0** — bumped by register
#38's repair, which both ADDS a projected category and NARROWS validation, so
a document valid under 1.0.0 may no longer be. **There is no migration
obligation: no accepted candidate export and no answer key exists.**) ·
`experiments/aq4_benchmark/open-surface-manifest.json` ·
`experiments/aq4_benchmark/aq4_projection.py` (validator, canonicalizer and
surface regenerator; **never** a candidate encoder, and it parses no Oracle
text into semantic facts).

**Benchmark evaluation law only.** It ratifies no production architecture,
decides no canonical ownership (§23's models A–D stay open), mints no
production vocabulary, authorizes no candidate encoder, and changes no §22
blind timing.

**Projected categories.** Occurrence address `[oracle_id, face, paragraph,
clause]` (no fifth coordinate) · participants as **bare integers** · action
heads (predicates, printed order preserved, multi-head required, no detected
head represented as UNRESOLVED and never fabricated) · constraint facts over
**ratified §14 dimensions only**, scoped to the occurrence or to a participant
ordinal · quantity/numeric intervals · §16 relation edges (the three
CR-groundable kinds, same-card only) · **COST structural regions** ·
**generated structural CHOICE GROUPS** (register #38) · evidence locators ·
the five §18 dispositions.

**What the substrate must never contain**, each refused by a rigged-red
control: a candidate-native ownership or storage concept; a participant kind
coordinate; a per-row party field; an action head carrying a dimension; a
structural region carrying a dimension, atom or disposition; a B1/B2/B3/B4/C1/
DISCOVERY verdict; a hand-authored E1 explanation string; a fact with no
evidence trace; normalization presented as evidence.

**COST equality safety (register #27).** Uncontracted cost content remains
residue, and residue is not free. **If relevant cost material differs between
two semantic units and v1 has no contracted representation sufficient to prove
equality, that residue BLOCKS a strict PROVEN equality** rather than being
silently ignored; such cases stay `UNKNOWN`/`UNRESOLVED` for future B1/C1-style
comparison. Cost is not a §14 dimension, so **no §14 contract exists over cost
and neither side may make an absence claim about it** — that is structural
rather than a rule to remember, because cost carries no dimension for §18.4 to
key on.

**The rejected alternative, recorded (register #28).** A per-row party field
was proposed and is **REJECTED** — written in quotes, never in backticks, per
the house rule that a rejected term in backticks is ingested as ratified
vocabulary. Artifact identity already establishes whether rows belong to the
frozen key or to a candidate export; storing it per row would be a second
source of truth. The validator refuses the field by name.

**Exporter contract (symmetric, and no exporter is written here).** Candidate A
and Candidate B each export their native semantics into **this** schema at
**this** version; neither receives a privileged field; a candidate's native
answer and its exported projection must agree; the projection does not force
either candidate to adopt the other's ownership model and decides no production
ownership; exporter normalization may reorder and canonicalize representation
but may **never** invent or drop a semantic fact, and every surviving fact keeps
its evidence trace; **candidate exports may not emit `HUMAN-RESOLVED`**, and
`ABSENT-PROVEN` stays claimant-side under §18's obligations; scoring later
consumes the projection, never candidate internals; **exporter failure is a
candidate failure, never permission to mutate the projection.**

**HONESTY-2, recorded without implementing scoring.** A candidate's
`ABSENT-PROVEN(dim, occurrence)` may match a key's `HUMAN-RESOLVED(absent)`
**only if that candidate has satisfied the applicable §18 claimant-side
obligations.** The key does not discharge them on the candidate's behalf.

**BOTH PACKET-4 REPAIRS ARE PERFORMED — projection schema version 2.0.0
(register #38, implemented 2026-08-17).** Neither minted semantic law. The
occurrence surface itself did NOT change: **782 / 307 / 364** reproduce exactly,
the rejected unstripped surface stays **872 / 360 / 417**, the **113** structural
cost regions are unmoved, and `open-surface-manifest.json` is **byte-identical**
because it never bound the projection schema version.

**1. The generated structural choice-group record — BUILT.**
`aq4_projection.derive_choice_groups` materializes owning-header evidence and
location, member occurrence addresses in the existing four-coordinate identity,
a `{min,max}` selection derived under the ratified rules-backed grammar, and an
admissible trace. **No mode identifier, no fifth coordinate, no codebook
storage, no ownership ruling, no candidate-native vocabulary** — and the record
carries no dimension, no atom, no disposition and no verdict.

**The four coordinates suffice, and that is measured rather than asserted.**
Each CR 700.2 option is its own paragraph under the ratified locality split, so
a member's PARAGRAPH coordinate already says which option it belongs to. All 21
derived groups span more than one paragraph and **none crosses a face**, which
is the correct shape rather than a violation.

**Every step is a ratified helper** — the locality unit split, the CR 207.2a
reminder strip, the ratified mode-line and modal-header tests, the clause
segmentation, and the ratified numeral map. **No modal parser was written.**

**THE DERIVATION REFUSES RATHER THAN GUESSES.** CR 700.2 enumerates no header
forms — it says *"preceded by instructions for a player to choose a number of
those options, **such as** 'Choose one —'"* — so a count is trusted only where
nothing remains between the matched count token and the modal separator. The
ratified matcher accepts a bare *"chooses one"*, and that alternative also fires
inside *"Choose one or more —"* and *"Choose one or both —"*, where the
selection is not one. Residue means refuse.

Measured over the frozen open surface: **27** candidate headers, **21** groups
derived (selection `{1,1}` ×20, `{2,2}` ×1), **49** options, **54** member
occurrences, max 4 members, **0** off-surface members, **0** duplicates, **0**
overlapping membership, **0** face crossings — and **6 refusals, every one
correct**: two headers with no bulleted list under them (targeting
instructions, not modes), a conditional selection count, a CR 700.2i pawprint
header, and the two compound *"or more"* / *"or both"* forms. **Each refused
form is reported as a masked generic shape, never as card text.**

**2. Atom-payload validation — BUILT.** The shapes were already frozen law and
the validator inspected only an atom's operator, so a malformed payload
validated here and failed later as an unattributable UNKNOWN. Cardinality now
validates as an operator drawn from the ratified set plus a non-negative
integer count; the interval validates as `{min,max}` with integer-or-null
endpoints, never both null, and min at or below max. **A malformed payload
fails HERE, and may never become evidence for a negative verdict.**

**The ratified cardinality operator set is exactly two** — the ones §13's own
worked examples attest. A third is a ratification request and is refused
loudly, because an operator admitted silently here would be comparison law
minted by an exporter.

# 24. EXTRACTION TAXONOMY AND REPORTING — PRE-REGISTERED

Every populated field/facet/edge carries exactly one class:

| class | qualifies iff |
|---|---|
| **EXTRACT-0 STRUCTURAL** | from face/paragraph/segmentation machinery that exists |
| **EXTRACT-1 CR-CLOSED** | value from a closed CR enumeration parsed at run time |
| **EXTRACT-2 ORACLE-TEMPLATE** | Oracle template with a named CR anchor |
| **EXTRACT-3 EXISTING-FOUNDRY-PRIMITIVE** | existing ratified machinery (delivery classifier, lattice, locality resolver) |
| **EXTRACT-4 COMPOSED** | pure function of EXTRACT-0–EXTRACT-3 outputs |
| **H1 HUMAN** | per-card/per-axis human judgment |
| **H2 HAND-LIST** | an open list a human typed that no CR rule closes — permitted only under the cited CR 207.2d exemption |
| **U UNRESOLVED** | deliberately unresolved (an unverified CR anchor is U, not EXTRACT-2) |

Reported per candidate: the **fill matrix** (fields × classes, per card
and aggregate); the **H2 inventory** (each hand-list named, sized, with
growth exposure — grows-per-set is worse than static); **anchor-free
heuristic count** (target 0, each named); **trap-replay** misparse counts
against the trap cohort; **negative controls** demonstrated per derivation
class; **U-rate** on consumer-relevant fields. **MUST NOT** be collapsed
into a tunable weighted score; comparison is lexicographic per §26.

# 25. FALSIFICATION LADDER

Purpose: **find the minimum rung where the kill conditions stop firing.**
Do not preselect OCC-FACET or MIN-IR by name. (H1–H4 below restate source
(3) §O with participant/relations given their own rung for clarity; the
mapping is noted so the historical numbering stays citable.)

| hypothesis | can answer | killed by | justifies next rung | stop here if |
|---|---|---|---|---|
| **H1** occurrence identity alone | attachment (Q-A) | any Q-B/Q-C needing restriction *values* compared — expected immediate; record the kill | typed predicates | consumers never compare (they do — proceed) |
| **H2** + typed predicate atoms | labeled restrictions | any B2 broader/narrower answer wrong or forced UNKNOWN without per-dimension entailment | derived algebra | labels alone answer all §20 (they will not) |
| **H3** + derived comparison algebra | verdicts on single-participant clauses | ATTACH-2/C questions on multi-participant or linked cards unanswerable | participant + relation coordinates | MPR/relation cohorts empty (they are not) |
| **H4** + participant + relation edges (flat rows; = source (3)'s H3) | full §20 set, flat | a card whose consumer-needed fact cannot be represented without nesting beyond predicate-valued references; or algebra ops proliferating past §17's closed table; or a normalization dimension demanding a growing hand-list in both candidates | predicate-valued references (RESERVED), then H5 | **expected stopping rung** — holdout decides |
| **H5a** nested structure is expressively NECESSARY (= source (3)'s H4) | anything flat rows cannot express | H4 surviving the entire benchmark including the holdout | — | a named holdout card forces nesting |
| **H5b** moved canonical ownership (MIN-IR-style artifact) is architecturally PREFERABLE | the same expressive content as H4 | **not killable by expressive results** — decided at §26 tiers FIFTH–SIXTH over §23's ownership dimensions, and by Captain | — | tiers FIFTH–SIXTH resolve it |

**H4 surviving falsifies H5a ONLY.** A future model MUST NOT infer that
flat expressive sufficiency disproves moved ownership: H5b is an
ownership hypothesis, invisible to tiers FIRST–FOURTH by construction
(§23), and it remains live until the cost/reversibility tiers and Captain
decide it.

# 26. DECISION RULES — LEXICOGRAPHIC, ARCHITECTURE-NEUTRAL

Evaluated in order; a tier decides only if earlier tiers tie. No labels,
no weights.

- **FIRST — correctness.** The symmetric false-precision veto (§6.2).
- **SECOND — completeness/honesty.** UNRESOLVED allowed; silent
  omission-read-as-absence disqualifies (HONESTY-2 tests it); consumer-critical
  UNRESOLVED rates reported.
- **THIRD — deterministic extraction.** H2 inventory + growth exposure;
  CR anchoring (anchor-free count); trap replay; negative controls;
  determinism ×2; dev-vs-holdout divergence scored here.
- **FOURTH — consumer sufficiency.** All §20 questions answered PROVEN
  where the pre-committed answers say PROVEN; DISCOVERY-1 answerable from indexes;
  the §19 trace producible.
- **FIFTH — architecture cost.** Migration; ruling-corpus and
  human-assertion conservation; guard rows unchanged/adapted/rewritten
  (counted against the runner — never quote a fixed gate total); schema
  complexity (record types + coordinates + relation kinds);
  projection/regeneration obligations; refresh/semantic-diff cost.
- **SIXTH — reversibility.** Genuine tie → the smaller reversible
  extension wins. **A tie is never "insufficient evidence."**

Outcome `INSUFFICIENT EVIDENCE` is limited to: benchmark compromise
(§22), both extraction stories indeterminate (high U on both), or
population invalidation — never "we dislike the result."

**Rung adoption gate (replaces the withdrawn 5% threshold, register #4):**

> Adopt a rung iff some pre-registered consumer question on the
> pre-registered population cannot be answered PROVEN without it.

# 27. THE FOUR PRE-BENCHMARK READ-ONLY PROBES

All four: deterministic, $0, probe-library-built (`import foundry_probe
as p` — 21 recorded probe defects came from hand-rolling), read-only,
run BEFORE any encoding. **Not implemented by this document.**

**P1 — residual / absence-proof feasibility.**
PURPOSE: is ABSENT-PROVEN achievable often enough for strict replacement
to function at all — the measurement most likely to change the leading
hypothesis. POPULATION: object-lattice-classified clause occurrences
(the census population). UNIT: clause occurrence. OUTPUT: % reaching zero
residue under **residue-honest** claiming (open captures never claim),
by action family and dimension. NON-GOAL: a high rate does NOT prove the
claims are adequate (that is §18 obligations 2–3), and the rate is
detector-sensitive — protect reproducibility, never pin the number.
NEGATIVE CONTROL: injecting an unclaimable token into a zero-residue
clause MUST flip it to non-empty residue. DECISION USE: if low, strict
replacement starves under BOTH candidates — escalate before any
architecture spend.

**P2 — multi-effect-per-clause (MEC) pressure.**
PURPOSE: price the RESERVED `effect` ordinal. POPULATION: all classified
clause occurrences. UNIT: clause. OUTPUT: % of clauses whose segment
carries >1 candidate action verb / effect head, with the top structural
forms enumerated. NON-GOAL: does not license building the splitter; it
prices deferral. NEGATIVE CONTROL: a known two-effect sentence ("Draw a
card, then discard a card") MUST count; a known one-effect coordination
inside an object phrase MUST NOT. DECISION USE: RUNG-2's reserved slot;
high MEC concentrated in consumer-critical families is the strongest
argument that identity should live in a rebuilt artifact.

**P3 — multi-participant (MPR) pressure.**
PURPOSE: size the participant-coordinate cohort and its extraction
priority (NOT an architecture threshold — register #4). POPULATION:
qualifier-bearing clauses. UNIT: clause. OUTPUT: % with ≥2 restricted
participants + the structural forms (fight templates, exile-and-return,
attach, two-target spells) + consumer-criticality annotation. NON-GOAL:
no prevalence number selects an architecture. NEGATIVE CONTROL: Prey
Upon's template MUST count 2; a single-target clause with a possessive
("its owner's hand") MUST NOT count the owner as a participant.
DECISION USE: benchmark cohort sizing; extraction priority.

**P4 — relation-kind diversity.**
PURPOSE: test whether relation edges stay within the three CR-groundable
kinds (CR 607 linkage, coreference, conditionality). POPULATION: cards
with cross-occurrence references (pronoun back-references, linked-ability
pairs, delayed effects). UNIT: card and reference. OUTPUT: reference
counts by kind; residual "kind unclear" rate. NON-GOAL: does not resolve
any reference; counts structure only. NEGATIVE CONTROL: Cloudshift MUST
yield a coreference edge candidate; a card with no pronouns MUST yield
zero. DECISION USE: RUNG-5 scope; a proliferating kind inventory is
evidence toward H5.

# 27a. THE SEMANTIC ACTION-HEAD DETECTOR — TWO PATHS, ONE FROZEN

**Ratified `CORRECT_BEFORE_OPEN_KEY`, Captain 2026-08-16 (register #23).**
An objective defect in action-head detection is corrected **before**
open-ground-truth adjudication. Packet-2 population and pairing are
**frozen benchmark history** and are not redrawn to accommodate it.

Those two requirements are only jointly satisfiable with two paths, and
that is a measurement rather than a preference: `action_family_of` is one
of cohort 4's two stratum coordinates and one of the S-tranche pairing
coordinates, and re-running it with the corrected rules over the **272**
published open exemplars moves the coordinate on **1** of them under the
authorized P1+P2 set — and on **7** if the deferred finite-subject class is
included. One moved coordinate is enough to redraw the frozen 486-pair
artifact, so one shared detector cannot serve both purposes.

| path | entry point | status | consumers |
|---|---|---|---|
| **legacy / frozen** | `foundry_aq4_probes.effect_heads` | **FROZEN Packet-2 history — do not "fix"** | `aq4_population.action_family_of`, `card_facts`, probe P2 |
| **corrected / semantic** | `foundry_aq4_probes.semantic_action_heads` | corrected, ground-truth & projection use | open-key and projection work only |

**Two explicit functions, never a boolean mode** — a `corrected=True`-style
flag reads identically at both call sites and is exactly how the frozen path
gets substituted by accident. The corrected path must never be routed into
Packet-2 regeneration, and the legacy path must not be recommended for new
ground-truth work.

**Authorized corrected classes — these two and no others:**

- **P1 MODE BULLET (CR 700.2).** *"two or more options in a bulleted
  list … each of those options is a mode"* — the bullet is list
  punctuation, so the mode's instruction begins after it. Applies to the
  bulleted clause itself, **not** to follow-on sentences inside the mode.
- **P2 INSTRUCTION PREFIX.** A CR 714.2 Saga chapter bar, a CR 606.2
  loyalty cost, a CR 700.2h additional-cost marker or a CR 700.2i pawprint
  marker prints a **marker or cost** before the instruction; the
  instruction begins after the em-dash. A **CR 702.Na keyword prefix is
  REFUSED** — CR 702.6b makes the body the keyword's own *cost*
  ("Equip—Sacrifice a creature"), not an effect.

Both are **structural and CR-grounded**: no vocabulary is minted, no
subject-word list is involved, and neither depends on which text view the
detector consumes.

**Deliberately NOT adopted, and each is a real open question:**

- **Finite-verb-with-printed-subject recovery is DEFERRED.** The audited
  predicate rests on a subject-word list the CR does not enumerate; that
  list is **not ratified** and must not be implemented.
- **✅ CLOSED 2026-08-17 (register #29) — the text-view choice is
  VIEW-INVARIANT for P1+P2, measured rather than argued.** Over the frozen
  open surface both views give **782** occurrences, **307** legacy and **364**
  semantic, with **identical occurrence addresses**, **identical reached sets**
  (full digests pinned in `open-surface-manifest.json`) and **0** head-value
  deltas on either detector path. Normalization may therefore assist detection
  while evidence stays raw. **The deferred-P3 exposure is preserved, not
  closed:** **57** occurrences differ textually between the views and **32** of
  them, across **22** cards, are unreached by P1+P2. **Re-audit text-view
  behaviour before any future P3 finite-subject adoption.** P3 stays DEFERRED
  and no proper-name heuristic is adopted.
- **✅ CLOSED 2026-08-17 (register #27) — a CR 702 keyword's cost body.** It
  contributes **no** effect head, and it is now positively represented instead
  of merely refused: the body is a **COST structural region** (CR 702.6b),
  carrying no dimension, no atom and no absence claim. The detector's existing
  refusal is unchanged.

**Classification is HIT-LEVEL, not occurrence-level, and this is ratified
practice rather than an implementation detail (register #23).** A single
occurrence may carry both a genuine missed action head and a vocabulary hit
that is *correctly* rejected — measured on 5 occurrences of the open
surface, e.g. *"Whenever a player casts a spell they don't own, that player
creates a Treasure token"*, where `casts` sits in the CR 113.3c trigger
condition and `creates` is the effect. **Do not force occurrence-level
exclusivity**, and do not specify acceptance as disjoint occurrence counts.

**The evidence base is a reproducible partition, not a remembered count.**
The open surface is **782** occurrences over the 272 published open
exemplars, addressed as `[oracle_id, face, paragraph, clause]` with the
face/paragraph coordinate taken from the ratified locality resolver; the
legacy path reaches **307** of them (39.3%) and the corrected path with P1
and P2 reaches **364** (46.5%). Every class carries a SHA-256 over its
sorted canonical id set, so a later session reproduces the partition rather
than inheriting a number.

**A CLASS SIZE IS NOT A RECOVERY COUNT, and conflating them is how the
expected figure for this work was first written as 372.** The P1 *class* —
occurrences opening with a CR 700.2 bullet — is **49**; the number P1
*recovers* is **41**. The other 8 divide exactly: **5** need the deferred
finite-subject rule (`• You draw three cards.`), and **3** must stay
rejected and do (two CR 122.1 marker nouns, one participle in a subordinate
clause). P2's class and recovery are both **16**. Any future scope statement
about this work must say which of the two numbers it means. **An earlier, uncommitted read-only audit
circulated a different sub-partition of the same surface; it was withdrawn
as an acceptance contract on 2026-08-16 and is not law, not current
evidence, and must not be reproduced or optimized toward.**

# 28. HISTORICAL TRAPS — DO NOT REPEAT

| trap | symptom | why wrong | protective rule |
|---|---|---|---|
| card-level union as co-occurrence proof | "card destroys AND bounces" | modes are alternatives | ratified A4 derivation; the 41-card cohort |
| overloading locality with occurrence identity | "extend the ratified field" | different questions; degrades OWNER rate | §10; register #1 |
| classifier stem as identity | one clause, four identities | extractor-relative | segmentation owns ordinals (§11) |
| first-match-wins resolution | silent racing | ratified A3 forbids it | reconcile; AMBIGUOUS on multiplicity |
| open capture claims text | zero residue, lost restriction | text coverage ≠ representation | residue-honest claiming (§18.1) |
| structural conservation read as semantic completeness | "everything reassembles" | the greedy-`\(.*\)` recorded trap | §18's four obligations |
| complement sets on multivalued dims | artifact land passes `nonland` | NOT_HAS ≠ HAS-complement | FORBIDS atom (§13) |
| materialized complement over growing CR vocab | stale the day the CR grows | carried-forward count in set form | store the printed atom |
| UNKNOWN treated as ABSENT | confident wrong strict swaps | absence needs proof | §18 consumer law |
| context-free type subsumption | creature card "is" a permanent | CR 109.2/110.1 | entity-kind/zone guards (§15) |
| stored derived values | drift from their derivation | second source of truth | derive exclusivity, ChoiceGroup, comparisons; regeneration gates |
| index policy inside representation decision | no-compound-slug in AQ4 | biased one candidate | register #6; policy deferred |
| nesting assumed superior | "typed = fewer bugs" | failures transform, not vanish | fill matrix + trap replay decide |
| holdout redrawn after bad results | architecture shopping | opened results are evidence | §22 firewall |
| answer key in native vocabulary | home-field bias | key must be neutral | projection vocabulary only |
| hand-list where CR closes the list | "a defect with a delay" | measured repeatedly | EXTRACT-1 derivation; H2 inventoried |
| one hard card ⇒ new architecture rung | rung inflation | minimum-rung principle | §26 adoption gate |
| card-specific exception | "just this card" | generalization is the product | scoreable defect (§6.14; §5 flag) |

# 29. RETROFIT PATH A — CONSERVATIVE / EXISTING-OWNERSHIP OUTCOME

**Outcome-independent preamble (applies to A, B, and C): before ANY
production semantic retrofit —** AQ4 evidence packet exists · Captain
ruling exists and names the architecture · P3/C6 authority state healthy
and the operational codebook authority known exactly · rollback exists
and is drill-verified · human-assertion conservation measured
(4,233-class counts before/after) · baseline gates frozen · migration has
a dry-run · any evidence-boundary change the selected architecture
requires (register #12) explicitly ratified · Stage F not begun.
**STOP if any item is missing.**

If Captain rules for occurrence/predicate extension with existing
canonical ownership: (1) promote the occurrence probe to guarded
infrastructure — derived table, INV-1 prefix gate, determinism ×2 —
touching no stored schema; (2) ratify the dimension-contract sheet
(Captain); (3) introduce predicate rows in ONE bounded tranche, one
dimension, one action family, forward-emission only, with §18 controls
shipped in the same tranche; (4) human assertions untouched throughout —
facet-less legacy rows remain valid card-level evidence by ratified law;
(5) per-dimension corpus backfill only after that dimension's negative
controls pass, under the backup law; (6) derive indexes/regeneration
gates; (7) benchmark-family replay after each tranche; (8) Gate 2
adaptation only where separately authorized; (9) global re-audit last.
One tranche per session; commit cadence per standing autonomous law.

# 30. RETROFIT PATH B — MIN-IR / MOVED-OWNERSHIP OUTCOME

If Captain rules for a new canonical semantic artifact with derived axes:
(1) build the canonical unit artifact generation as CANDIDATE output
beside the untouched codebook — dual-run, nothing cut over; (2)
demonstrate **derived-index equivalence** (regenerated axes match ratified
memberships exactly; discrepancies are findings, not fixes); (3) map
every human assertion mechanically with zero provenance loss (explicit
`unresolved` allowed, silent drops never); (4) build the ruling-migration
linkage (axis → unit-projection), extending the slug-dossier rename-walk
pattern so the 77-rulings-under-former-names failure does not recur at
corpus scale; (5) rewrite codebook-keyed guards one at a time, each
negative-controlled before trusted (measured base rate: 3 of 8 controls
mis-aimed on first pass); (6) authority publication of the new artifact
under P3/C6 law — new durability surface, same architecture; (7) cutover
only after a restore drill on the NEW artifact; (8) historical
compatibility: the codebook is preserved read-only as evidence archive,
never deleted; (9) rollback = the untouched codebook remains operational
until cutover, so every step before (7) is reversible by abandonment.

# 31. PATH C — INSUFFICIENT EVIDENCE

Production remains exactly as it is. **FORBIDDEN until a new Captain
ruling:** any schema change, any occurrence/facet storage, any
vocabulary minting from AQ4 material, Stage F, any migration tooling.
Required before another decision attempt: name the specific evidence gap
(compromised run → re-run under §22 with a fresh packet; indeterminate
extraction → build the failing extractor stories as probes first;
population defect → redraw under §21 with full history preserved). The
failed packet stays in history.

# 32. LOWER-MODEL PACKET MAP (specification, not prompts)

**Never ask a lower model to "implement AQ4."** Bounded packets, one per
session, each with STOP conditions. Common to all: read this contract
first; production codebook / Gate 2 / CLAUDE.md / P3-C6 / CI are
FORBIDDEN files unless a packet names them; every probe uses
`foundry_probe`; determinism ×2 on any generated artifact; STOP on any
red gate, any ratified-law conflict, any need to mint vocabulary.

| packet | objective | permitted | prereqs | evidence returned | STOP if |
|---|---|---|---|---|---|
| **0** | preflight: verify repo state, Gate 2 green, contract vs law consistency | read-only + Gate 2 run | Captain authorizes benchmark | state report | Gate 2 red; law conflict found |
| **1** | the four §27 probes | new `experiments/` probe files only | 0 | four probe reports + negative-control transcripts | P1 rate collapses (escalate, do not proceed) |
| **2** | population + sampling machinery (§21) | new benchmark dir | 1 | cohort lists (open), committed sampling script + seed | any cohort needs vocabulary minting |
| **3** | holdout commitment (§22 steps 1–2) + **open-cohort** answer-key freeze | benchmark dir | 2 | seed hashes, frozen open-cohort key hash | key requires native-vocabulary answers |
| **4** | normalized evaluation projection schema + exporters' contract (§23) | benchmark dir | 2 | schema doc + self-consistency test spec | projection needs canonical-ownership assumptions |
| **5** | candidate A (OCC-FACET as amended) benchmark encoding | benchmark dir | 3,4 | encodings + fill matrix + provenance traces | any card needs a card-specific exception |
| **6** | candidate B (MIN-IR) benchmark encoding | benchmark dir | 3,4 | same, symmetric | same |
| **7** | comparison algebra + scoring harness (§17, §26) | benchmark dir | 4 | verdict tables on open cohorts | any op outside §17's closed table needed |
| **8** | negative controls + trap replay (§24) | benchmark dir | 5,6,7 | control transcripts, misparse counts | a control cannot be aimed (record, continue others) |
| **9** | candidate freeze + blind evaluation (§22 steps 3–12, incl. blind-cohort key adjudication at steps 9–10 by **independent dual adjudication**) | benchmark dir | 5–8 complete | freeze commits named; **both adjudications** + disagreement record; procedural audit record THEN scores | procedural audit fails (reserve path only); adjudicator sees candidate output |
| **10** | evidence-packet generation | benchmark dir | 9 | one packet: matrices, verdicts, kills per §25, tier walk per §26 | — |
| **11** | Captain decision checkpoint | none (document only) | 10 | one decision sheet | **always — this packet ends in Captain's hands** |
| post-ratification | §29 / §30 / §31 tranches | per path | Captain ruling | per path | preamble item missing |

**PACKET 4 MAY PRECEDE COMPLETION OF PACKET 3 (Captain, 2026-08-16 —
register #25).** Packet 3 is holdout commitment **plus** the open-cohort
answer-key freeze; under `FACT_PROJECTION` (§23) that key is frozen as a
normalized fact substrate, so packet 4's projection schema must exist before
the key can be frozen in it. The prerequisite column already permits this —
both packets depend only on packet 2 — so **no prerequisite is changed**, and
the sequencing note is recorded rather than the graph rewritten. Packet 3A
(the §22 step 1–2 seed commitment) is unaffected and is already done.
**§22's blind timing is untouched**: the blind key is still adjudicated after
candidate freeze, and packets 5–6 still require packet 3 as well as 4.

**PACKET 7 SPLITS, AND ONLY THE ALGEBRA HALF IS FROZEN (register #31).** The row above
bundles *"comparison algebra + scoring harness"*, and the two halves have
different prerequisites: the **algebra** depends only on packet 4, while the
**scoring harness** and the *"verdict tables on open cohorts"* need packet 3's
open key and packets 5–6's encodings, none of which exist. **No verdict table
over any real card was produced, and none could honestly be.**

**The first attempt at `4e2ff09` is QUARANTINED and was SUPERSEDED, never
adopted** — a pre-registered STOP fired and the Worker continued, and later
review found further unfrozen law and implementation defects. A forward
corrective implementation now carries the algebra and is **FROZEN** (§17a);
`docs/INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md` is the record. **The
scoring harness is still not built and needs packet 3's open key and packets
5–6's encodings, so do not read this row as packet 7 being complete end to
end.**

# 33. CAPTAIN-CONTROLLED DECISIONS

MUST remain Captain's: benchmark implementation authorization (packet 0
gate) · dimension-contract sheet ratification (§14) · any answer-key
correction policy change or holdout cap (§22 — frozen once the first
holdout opens) · the final AQ4 architecture ruling and canonical
ownership choice · any production schema change · vocabulary minting ·
migration approval and each tranche's authorization · Gate 2 adaptation ·
Stage F authorization · installing §35/§36 pointers. Already delegated by
standing law (do not escalate): probe writing, measuring, CR-anchored
ruling documents, benchmark encodings, audits — the existing "proceed
without asking" list.

# 34. WHAT FUTURE MODELS MUST NOT INFER

DO NOT infer that:

- Fable recommending a model means Captain ratified it — §7 is a
  hypothesis;
- a benchmark representation existing means it belongs in the production
  codebook;
- occurrence identity being useful changes ratified locality (§10);
- an axis being derivable means it should be deleted — index policy is
  deferred (register #6);
- a derivable relationship should be stored — §17 derives, never stores;
- flat representability forbids nested IR (that is H5a, killed only by
  the full benchmark), or that flat sufficiency disproves moved ownership
  (that is H5b, decided at tiers FIFTH–SIXTH and by Captain, never by
  expressive results);
- a dimension absent from extraction is ABSENT-PROVEN — §18 requires four
  obligations;
- a badly performing holdout is an invalid holdout — §22;
- one difficult card requires a higher rung — §26's gate requires a
  pre-registered question to fail, not a card to exist;
- a dated AQ4 paper's statement is current — check §8 first;
- the operational numbers in §3 are current — re-verify with tools;
- "no card-specific production exceptions" is written production law —
  see the §5 discrepancy flag;
- the characteristic-evidence boundary is ratified production law — it is
  an AQ4 candidate only (register #12; §19 warning);
- meeting the ratified reopening trigger for child effects authorizes
  implementing them — it authorizes *reconsideration* (§5);
- the Packet-4 projection existing means production canonical ownership was
  decided — §23's models A–D stay open and §23a is benchmark evaluation law
  only;
- COST being representable makes it a dimension, a predicate, or something
  with payability or comparison semantics — it is a positional structural
  region and nothing else (register #27);
- an unmarked span is proven not to be a cost — unmarked means unmarked, and
  no absence claim over cost exists on either side;
- `HUMAN-RESOLVED` in a key cell means Captain ruled that cell — it means
  adjudicated under register #24's procedure, with the method recorded as
  metadata (register #28);
- a candidate may emit `HUMAN-RESOLVED`, or a key may claim `ABSENT-PROVEN` —
  neither is permitted, and both are rigged-red controls;
- P1/P2 view-invariance settles the text view for P3 — it does not; the
  exposure is measured and a re-audit is required before any P3 adoption
  (register #29);
- a comparison verdict being derivable means it may be stored — §17 derives
  and never stores, and the projection refuses a derived verdict by name;
- UNKNOWN means the two units differ, or are incompatible, or that a search
  was run and found nothing — it means none of those, ever;
- identical action heads mean the actions are proven equivalent — no action
  comparison is authorized at all, an identical head sequence is not positive
  proof of anything, and differing heads prove nothing either (register #35);
- anything in the QUARANTINED Packet-7 artifacts is law because it is
  committed at HEAD — it is not, and §17a governs where they disagree
  (register #31);
- a whole-unit semantic equality can be PROVEN in v1 — it cannot, and none of
  matching heads, matching participant integers, an absent relation edge, an
  absent cost region or an absence of visible residue supplies one
  (register #32);
- participant integer 0 on one card means the same participant as integer 0 on
  another — the ordinals are LOCAL to one occurrence and carry no cross-card
  meaning by themselves (register #32);
- a structural guard that ran and did not block has proved something — it has
  not, and emitting it as a proof component with a contract proof kind is
  refused (register #37);
- absence of a choice-group record proves the units are independent — it does
  not, and an underivable independence arm stays UNKNOWN and is reported
  rather than minted (register #38);
- an administrative not-applicable binding state is a semantic disposition or
  a comparison verdict — it is neither, and it is never UNKNOWN or PROVEN-NOT
  (register #36);
- the quarantined attempt was rehabilitated because the algebra is now frozen —
  it was SUPERSEDED by a forward commit and never adopted (§17a);
- a cardinality comparator beyond the two ratified in v1 is available because
  it is mathematically natural — widening needs a real consumer need and an
  explicit ratification (register #39);
- absence of a projected choice group proves two units are independent, or that
  the independence arm is merely unimplemented — it is NOT DERIVABLE from
  anything the projection carries, and that was audited (register #38);
- participant-scoped constraints can be compared across occurrences once an
  implementation aligns them by ordinal — the alignment is exactly what is
  unratified (§17a.2, §17a.3a);
- the 354 semantic card pairs may be expanded into occurrence cross-products —
  the population is the card pairs, with one frozen primary unit binding each
  (register #36);
- an empty blocker list on the strict-replacement question means the
  replacement holds — no positive strict-replacement relation is contracted;
- the algebra's PROVEN means either projection is semantically complete — it
  is a claim about the projected fact sets, and completeness is the
  false-precision veto's subject (§6.2), not the algebra's.

# 35. CLAUDE.md ROUTING BLOCK — **INSTALLED 2026-08-15**

*(Installed at the head of CLAUDE.md's `## Reference` section, verbatim as
below. Routing only: it mints no vocabulary and ratifies nothing.)*

```markdown
- **AQ4 (semantic architecture) IS NOT RATIFIED — a leading hypothesis
  exists, a benchmark is pre-registered, and production is unchanged.**
  Before ANY work on semantic occurrence identity, qualifiers/facets,
  predicate normalization, cross-card comparison, "semantic IR", strict
  Budget Swapper semantics, or any codebook semantic retrofit:
  **→ read `docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`
  FIRST.** It is the current entry point; the dated AQ4-*.md and
  SEMANTIC-IR-*.md papers are evidence/history, and where an older
  statement conflicts with the contract's SUPERSESSION REGISTER (§8),
  the register states the current design. Locality law
  (`B-MIGRATION-DISCOVERY.md` §11) is ratified and is NOT extended by
  AQ4. Do not implement production AQ4 changes before the benchmark
  runs AND Captain rules. Do not revive anything the register marks
  WITHDRAWN.
```

# 36. PROJECT-HANDOFF POINTER — **INSTALLED 2026-08-15**

*(Installed in `docs/PICK-UP-HERE.md`, immediately above §0AC.)*

```markdown
**AQ4 design is pre-registered but NOT production-ratified.** Current
entry point: `docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`
— read its status taxonomy (§4) and supersession register (§8) before
any semantic-retrofit or benchmark work. Dated AQ4 papers are history.
```

# 37. SEQUENCING LOCK

```
C6/P3 closure (active elsewhere — AQ4 stays isolated until then)
    ↓
Captain integrates/freezes this contract (commit timing is Captain's)
    ↓
install §35 + §36 routing pointers (Captain)
    ↓
authorize packet 0, then packets 1–4 (read-only probes, population,
holdout commitment, projection)
    ↓
packets 5–8 (encodings, algebra, controls) — extractors frozen at the end
    ↓
packet 9 (blind evaluation: procedural audit in writing, then scoring)
    ↓
packet 10 evidence packet → return to a high-level architecture reviewer
    ↓
packet 11 — Captain rules AQ4 (architecture + ownership)
    ↓
generate bounded production retrofit packets for the chosen path (§29/§30/§31)
    ↓
retrofit in authorized tranches → certify
    ↓
Stage F only when separately authorized (its plan is NOT in-repo law —
`FOUNDRY-SHARDED-CORPUS-CERTIFICATION-PLAN.md` is a Downloads-resident
design packet, per the 2026-08-14 review §2.2)
```

Checked against current law: consistent with `PICK-UP-HERE.md` §0AC
(C6 next), the product-reality queue (which this sequence does not
displace — the consolidation/coverage arc is orthogonal and proceeds on
its own authority, per `SEMANTIC-IR-PROPOSAL-REVIEW-2026-08-14.md` §6),
and the standing rule that ratification throughput is the bottleneck —
which is why exactly one decision sheet reaches Captain per checkpoint.

# 38. FINAL IMPLEMENTATION-READINESS STATEMENT

The AQ4 benchmark design is **ready for packetized implementation once
Captain authorizes it after C6/P3 closure** — with the §8 register
governing every historical statement, the §26 rules pre-registered before
any result exists, and §22's firewall making an inconvenient valid result
impossible to discard. The leading hypothesis (§7) is exactly that: a
hypothesis, held to the same one-wrong-fact veto as its rival. Nothing in
this contract changes production. The next event in AQ4's life is a
Captain decision, and every path from here runs through one.

*Known-open items carried honestly: the §5 card-specific-exception law
flag; the unverified cardinality-word CR anchor (U until verified); the
dimension-contract row values (unwritten, ratification required);
timing/duration/condition entailment deferred to equality-only;
predicate-valued reference semantics RESERVED; the answer-key cap number
frozen only when the first holdout opens.*
