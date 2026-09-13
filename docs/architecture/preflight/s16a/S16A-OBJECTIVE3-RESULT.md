# Objective 3 — S16A Parser-Seam Audit Result

Status: **COMPLETE EVIDENCE / NON-IMPLEMENTING**  
Objective: **3 of 5**  
Implementation authorization: **NONE**  
Objective 4 activation: **NO**

## Durable anchors

- selected checkpoint: `K-20260912-PREFLIGHT-OBJECTIVE3-ACTIVE`
- active task: `PREFLIGHT.OBJECTIVE3.S16A-PARSER-SEAM-AUDIT`
- accepted implementation head: `9f92039eb9c7132a351576c31472eb30a2957a67`
- Objective-3 planning head: `b01848d63bb40a7025a3ab0cd287c479a13dfd22`
- Objective-2 evidence head: `fc99f3bdf0503bd325f0b644771895c05940ad15`
- evidence branch: `preflight/objective3-parser-seam-audit-2026-09-12`
- controls: `{AQ4:P, BRIDGE0:U, STEP6:N, MERGE:N}`

The earlier Objective-3 STOP was correct for the environment in which it was issued. It is now **superseded**: the project-source corpus became available and its byte identity was verified before measurements resumed.

## Input identity

- project-source gzip SHA-256: `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217`
- archive size: **22,735,516 bytes**
- decompressed SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`
- raw Oracle records: **38,233**
- Gate #0: **32,557**
- excluded nowhere-legal: **5,676**
- Gate #0 face records: **33,393**

This exactly matches the completed Objective-2 evidence identity. No newer Scryfall substitution was used. The Objective-2 holdout remained unlabeled and unused.

## Method

The accepted source tree was mechanically inspected for every live Oracle/Oracle-derived interpreter and caller family. Overlapping same-contract implementations were compared over the full Gate #0 population or a mechanically complete applicable subpopulation. Objective-2 development witnesses were used only after mechanical discovery. Historical documents were treated as discovery evidence and current counts were remeasured. Negative controls were executed privately outside tracked repository paths; no parser/test/runtime mutation occurred.

## Measured results

- **Face projection:** `mtj_foundry.corpus.card_faces` vs `tier_engine.get_raw_faces` — **32,557 equal / 0 divergent**, covering **33,393** face records. This duplicate is S1.
- **Neutral self-reference:** permanent `oracle_text` vs the legacy thesaurus peer — **32,557 equal / 0 divergent**.
- **DET self-reference:** neutral owner vs DET policy — **30,739 equal / 1,818 divergent**. The difference is an explicit synthetic matching-representation boundary, S2, not a safe duplicate cleanup.
- **Depth-aware vs flat reminder stripping on live Gate #0:** **33,393 equal / 0 divergent** face texts because Gate #0 contains zero nested-parenthesis-depth≥2 cases. The synthetic nested-reminder control remains necessary.
- **DET reminder ownership:** **4,205** current card→pattern assignments; **167** are reminder-only across **13 axes**. This is live S5 evidence: plausible facts can be emitted from text that is not admissible as the enclosing card's claim.
- **Quoted/granted ownership:** after reminder text is removed, **77** assignments across **25 axes / 72 cards** remain quote-only. This is live S5 evidence.
- **Modal locality:** against the certified modal structure, the independent locality heuristic misses **69** genuine mode lines and invents **28** nonmodal lines across **14 cards**.
- **DET modal expansion:** covers **1,821 of 1,824** certified mode lines and misses all **3** Tiered modes on *Vincent's Limit Break*.

## Final concept topology

Across the 28 required semantic concepts:

- **S0:** 9
- **S1:** 1
- **S2:** 6
- **S3:** 5
- **S4:** 0
- **S5:** 7

S4 is intentionally zero: observed same-contract risks that can silently preserve plausible wrong semantics are classified S5, while documented representation differences are S2. No historical count was promoted into a current S4 claim.

The remaining S3 concepts are **payment timing**, **conditions/restrictions**, **source/destination zones**, **quantity/cardinality**, and **residual CR-derived/local heuristic islands**. Objective 3 does not guess a canonical owner for them because that would select a new interpretation contract rather than audit an existing one.

## Negative controls

Twelve private corruption probes were executed for all S3–S5 seam families. All twelve corruptions were detected, covering nested reminder parsing, quote/reminder colons, modal continuation, nonstandard modal markers, mode flattening, resolution payment→activation corruption, condition relocation, zone sequence reversal, cardinality change, quoted-owner loss, and CR routing-constant drift. These are evidence that the proposed invariants are falsifiable; no repository guard was installed.

## Historical reconciliation

The historical reminder, modal, face, punctuation, linked-ability, self-reference and quote/grant incidents are crosswalked separately. Most full-card/punctuation/provider defects are closed and guarded; reminder-retention, modal ownership/flattening and quote/granted ownership remain observably live; nested-reminder product failure is superseded by Gate #0 scope while retaining a synthetic guard.

## Decision boundary

Objective 3 is complete as evidence. The future S16A implementation now has a measured parser topology, explicit duplicate/representation boundaries, current divergences, unresolved contracts, and falsifiable negative controls. The nonbinding recommendation is to canonicalize S1 plumbing first, preserve S2 boundaries, then address modal and reminder/quote S5 ownership before selecting any of the five S3 cross-layer contracts.

**This completion self-authorizes nothing.** Objective 4 remains inactive. No accepted implementation ref, parser/runtime source, tests, codebook, authority, AQ4 state, Bridge0 state, Step6 state, merge, deploy, or publication state was changed.
