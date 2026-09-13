# Draft S16A Parser-Ownership Acceptance Contract

Status: **DRAFT / NOT AUTHORIZED**  
Objective-3 evidence branch: `preflight/objective3-parser-seam-audit-2026-09-12`  
Accepted implementation head measured: `9f92039eb9c7132a351576c31472eb30a2957a67`  
Pinned Gate #0 corpus SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`

A future S16A implementation may claim parser-ownership acceptance only if all of the following are explicitly authorized and then demonstrated:

1. **Input identity:** use the pinned 32,557-card Gate #0 corpus or a Captain-ratified successor; report raw/gated counts and decompressed SHA.
2. **Face conservation:** shared structural face projection remains value-exact for all applicable cards; no face, text, mana cost, type line, power or toughness field is silently dropped.
3. **Representation declaration:** every consumer declares whether it needs neutral printed Oracle structure, delivery semantics, locality/provenance structure, target semantics, or synthetic DET/ranking representation. No synthetic representation may silently become neutral structure.
4. **Modal structure:** one canonical modal-structure recognizer covers the full certified modal population, including continuation, pawprint, Spree and Tiered forms, and rejects nonmodal bullet structures. Mode parent/exclusivity must be conserved into locality and delivery.
5. **Reminder ownership:** semantic fact production cannot rely on reminder-only text unless a separately authorized policy explicitly permits that region and assigns its semantic owner.
6. **Quoted/granted ownership:** punctuation, colons, targets, triggers, costs and effects inside quoted/granted abilities remain owned by the quoted/granted ability unless an explicit rule says otherwise.
7. **Cost/payment timing:** casting/additional/alternative costs, activation costs, optional resolution payments and post-payment reflexive triggers remain distinct typed relations.
8. **Conditions/restrictions:** parent/child attachment is preserved; moving a condition between parent and child must fail a guard.
9. **Zones and sequence:** source/destination zone and ordered action sequence are explicit, typed, and conserved.
10. **Cardinality:** exact/up-to/any-number/X/repeat/distinctness semantics are conserved rather than normalized into an untyped number.
11. **CR-derived vocabulary:** truly shared CR-derived constants have one permanent substrate owner; validator-local or pattern-governance vocabularies remain separate when their contract differs.
12. **Negative controls:** each Objective-3 S3–S5 seam has an installed guard whose corruption case demonstrably turns red. The 12 executed Objective-3 private controls are candidate minimums, not automatically sufficient implementation tests.
13. **Development benchmark:** Objective-2 development witnesses satisfy their protected relations or produce an explicit unsupported/refusal result; no card-specific exception is permitted.
14. **Holdout isolation:** the Objective-2 18-card holdout remains unlabeled during implementation and is not used for tuning.
15. **No silent approximation:** unsupported structures fail/refuse visibly rather than coercing into a nearby semantic shape.
16. **Governance:** passing this draft contract would still not authorize codebook mutation, authority succession, AQ4, Bridge0, Step6, merge, deploy, publish, or accepted-head movement without a later durable Captain/Manager action.

This document is a draft acceptance boundary only. It is not ratified law and does not authorize S16A implementation.
