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

# 14. DIMENSION SEMANTIC CONTRACTS — SHAPE IS CANDIDATE; ROWS ARE UNWRITTEN

A single exclusive/non-exclusive bit was insufficient (register #13). Each
dimension needs a contract carrying: vocabulary source (CR rule),
single- vs multi-valued, exhaustive or not, hierarchy edges (subtype→type),
whether CARD atoms apply, **applicable entity contexts** (§15), and static
CR anchors.

**CONTRACT SHAPE = CANDIDATE (benchmark subject). ACTUAL ROW VALUES =
UNWRITTEN** — every cell requires implementation-time CR verification, and
the completed sheet is a **Captain ratification** (~10 rows, one-time,
zero growth exposure).

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

- **Every comparison returns `PROVEN / PROVEN-NOT / UNKNOWN`.**
- **Derived relationships are NEVER canonical stored facts.**
  `blue permanent ⊂ permanent` is a consequence of monotonicity, not a
  row. *Store the smallest canonical facts; derive relationships.*
- Ownership of the underlying fact rows remains **the** AQ4 decision —
  nothing in this section pre-commits it.
- Deliberately absent: formula negation, quantifier reasoning, theorem
  proving, "for each" resolution, timing/duration/condition entailment
  beyond equality (v1), any operation without a named consumer question.

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

**Dispositions** (per occurrence × participant × dimension):
`PRESENT(value) · ABSENT-PROVEN · UNRESOLVED · AMBIGUOUS ·
HUMAN-RESOLVED`. Do not invent additional states.

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
  → derived relation {input row ids, per-dimension verdicts}   (recomputed, never stored)
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
- B2. Is A's eligibility broader / narrower / overlapping / disjoint /
  UNKNOWN vs B's — and which per-dimension verdicts produce the answer?
- B3. Actions equivalent while eligibility differs?
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
9. adjudicate the complete holdout answer key independently — in
   projection vocabulary, from the cards and the CR, **without access to
   any candidate output**;
10. freeze and hash the answer key;
11. record procedural PASS **in writing**;
12. only then expose candidate outputs and score.

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
| **9** | candidate freeze + blind evaluation (§22 steps 3–12, incl. blind-cohort key adjudication at steps 9–10) | benchmark dir | 5–8 complete | freeze commits named; procedural audit record THEN scores | procedural audit fails (reserve path only) |
| **10** | evidence-packet generation | benchmark dir | 9 | one packet: matrices, verdicts, kills per §25, tier walk per §26 | — |
| **11** | Captain decision checkpoint | none (document only) | 10 | one decision sheet | **always — this packet ends in Captain's hands** |
| post-ratification | §29 / §30 / §31 tranches | per path | Captain ruling | per path | preamble item missing |

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
  implementing them — it authorizes *reconsideration* (§5).

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
