# Oracle Ingest Compiler — Pre-Execution Checkpoint

**Date:** 2026-09-20  
**Status:** SAVED CANDIDATE / NOT RATIFIED / NO EXECUTION AUTHORIZED  
**Base accepted implementation head:** `fdb66e659d81f4efa373ab8e86329485c0205966`  
**Compiler candidate commit line:** branch `docs/oracle-ingest-compiler-v1-ratification-candidate-2026-09-20`

> **PRESERVE TRUTH, NOT PLUMBING.**

## Saved architecture candidate

Read:

`FOUNDRY-ORACLE-INGEST-COMPILER-V1-FINAL-RATIFICATION-CANDIDATE-2026-09-20.md`

This is the final pre-ratification candidate incorporating the independent Claude review and subsequent live-repository reconciliation.

It does **not** authorize AQ4 Packet 0, AQ4 resumption, S16B freeze, production schema changes, codebook mutation, vocabulary minting, corpus execution, merge, accepted-head movement, or `main` movement.

## Sequencing clarification before compiler execution

### S16A

S16A is **not implementation-complete**. Its durable state includes a completed Objective-3 parser-seam evidence audit, but that audit was non-implementing and explicitly left Objective 4 inactive. The parser-ownership acceptance contract is still a draft / not authorized.

The existing S16A evidence should be treated as acceptance criteria and regression material for the compiler rather than duplicated or prematurely implemented as a separate parser project.

### S16B

The near-finished slice is S16B semantic design, not S16A implementation.

The current PR #70 routing already names bounded pre-freeze validation around:

- Card Resource Delta stateful fixtures;
- Sample Selection retrieval/UI fixtures;
- Keyword Consequence Registry census/design gate;
- Lockdown boundary only if evidence forces it.

The 2026-09-20 Round-2 weird-card research adds a required reconciliation/audit before any semantic freeze for:

- generic event-replacement / modification lineage;
- player decision authority under CR 723;
- ability borrowing / inheritance;
- plus the associated visibility/information-access and action-rate pressure findings where they affect the substrate.

These findings are evidence of possible substrate gaps, not authorization to mint new ontology.

## Recommended checkpoint before P0.0

Before opening the Oracle Ingest Compiler P0.0 governance gate:

1. finish the bounded remaining S16B semantic-design validation;
2. audit/reconcile the Round-2 findings against the existing Foundry/AQ4 substrate;
3. update the S16B current-state routing so the surviving candidate semantics and remaining debt are explicit;
4. decide whether S16B is ready for its formal freeze review, without forcing a freeze if S16A dependency law forbids it;
5. use the existing S16A parser-seam evidence and draft acceptance contract as compiler acceptance inputs rather than starting a separate S16A parser implementation;
6. only then make the separate Captain decision on compiler V1 ratification and P0.0 execution authorization.

This checkpoint is routing/planning only and self-authorizes nothing.
