# S16A Parser Ownership Recommendations — Objective 3

Status: **RECOMMENDATIONS ONLY / NOT LAW / NOT IMPLEMENTATION AUTHORITY**  
Accepted implementation head: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Measured Gate #0 corpus: **32,557** cards, decompressed SHA-256 `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`

## Recommendation set

1. **Keep `mtj_foundry.corpus.card_faces` as the canonical full-card/face structural owner.** Its independent legacy peer is value-exact across all 32,557 Gate #0 cards and 33,393 face records. Compatibility callers should eventually delegate or disappear rather than preserve a second structural implementation.
2. **Keep `mtj_foundry.oracle_text` as the neutral printed-text normalization owner, but do not fold DET policy into it.** Neutral self-reference is value-exact with the legacy thesaurus peer; DET differs on 1,818 cards by representation contract and should remain explicitly labeled synthetic matching policy until that policy is separately retired or re-ratified.
3. **Create one neutral modal-structure recognition boundary before S16A implementation consumes modal ownership broadly.** Current locality logic misses 69 genuine mode lines and invents 28 nonmodal lines; DET synthetic expansion misses all three Tiered modes on *Vincent's Limit Break*. The future recognizer should cover CR-700.2, pawprint, Spree and Tiered forms without equating every printed bullet with a mode.
4. **Keep delivery consequence semantics in `mtj_foundry.mtg.shapes.delivery`.** Sentence boundaries, quoted created abilities, cost/effect routing, structural grouping, and linked/reflexive/delayed distinctions are delivery semantics rather than generic text normalization.
5. **Keep locality/provenance in `mtj_foundry.mtg.shapes.locality`, but make it consume canonical modal structure rather than independently re-deriving modality.** A plausible wrong owner is more dangerous than a visible parse refusal.
6. **Keep target semantics in `mtj_foundry.mtg.shapes.target_classes`.** `foundry_object_lattice` is compatibility plumbing; DET scan text remains an upstream representation input, not the target owner.
7. **Treat reminder and quoted regions as ownership boundaries before semantic matching.** Current DET has 167 reminder-only assignments across 13 axes and 77 quote-only assignments across 25 axes / 72 cards after reminder removal. A match inside such a region must not silently authorize an enclosing-card fact without an explicit policy saying why that region is admissible and who owns it.
8. **Do not canonicalize the five S3 cross-layer concepts yet:** payment timing, condition/restriction attachment, source/destination zones, quantity/cardinality, and residual CR-derived/local heuristic islands. Select a typed ownership contract first, then measure implementations against that contract.
9. **Preserve task-specific paragraph/clause representations.** Delivery lines, locality units, target noun-phrases, evidence clauses, and ranking clauses are not automatically the same concept. Consolidation should happen only when the semantic question is the same.
10. **Promote the Objective-3 negative controls into future implementation guards only when S16A is authorized.** All 12 private corruptions were demonstrated detectable; Objective 3 installs none of them.

## Canonicalization order if implementation is later authorized

A low-risk order is: face projection (S1) → neutral self-reference peer cleanup (S1) → explicit representation-boundary documentation (S2) → modal shared recognition and ownership conservation (S5) → reminder/quote ownership gating (S5) → only then the five unresolved S3 cross-layer contracts.

This order is nonbinding. Evidence does not self-authorize repair.
