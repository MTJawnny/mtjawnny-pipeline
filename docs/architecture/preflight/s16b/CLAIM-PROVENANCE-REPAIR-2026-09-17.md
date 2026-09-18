# S16B Claim-Provenance Repair — 2026-09-17

Status: **PREFLIGHT CANDIDATE — NOT SEMANTIC AUTHORITY**

Base: `fdb66e659d81f4efa373ab8e86329485c0205966`

This candidate repairs provenance only. It does not change S16B vocabulary, card sets, relation labels, benchmark judgements, S16A, AQ4, codebook authority, Step6, merge, deployment, or publication.

## Changes

- adds `claims-schema-v1.json` and marks every claim as `mtj-s16b-claim/1`;
- makes source-date status, source lineage and independent-corroboration count explicit on every claim;
- replaces C017's subreddit-root locator with four specific dated r/EDH discussion objects while preserving the original conflict claim and making no majority inference;
- replaces C023's generic Issue locator with the accepted M2 R1 Manager review 5595331993, accepted R1 Worker result 5594358320, and the frozen M2 panel lineage; rejected predecessor review 5593405124 is not acceptance/corroboration evidence;
- adds pinned-corpus Oracle claims C024-C033 and C035 for the six previously claimless benchmark rows;
- adds CR claim C034 (112.1, 113.1c, 701.6a) for Counterspell/Stifle object-class distinction;
- adds community functional-vocabulary claim C036 for board preservation/protection;
- adds claim links to P06, N01, N05, N09, N11 and N12 without changing their labels or card sets.

## Pinned mechanical inputs

- corpus container SHA-256: `b46e0670a8f3fa2d5357ec35ff7f8d58e7c2f9f15db0e27a3b0543672b00c217`
- corpus decompressed-content SHA-256: `5e47e1325a3987db745a941307080830696cbac2f6aa80d8f88f8a6dad90723c`
- Comprehensive Rules effective date: 2026-08-07
- local CR SHA-256: `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b`

## Validation performed before commit construction

- unique claim ids: PASS
- all claims have typed provenance fields: PASS
- all 24 benchmark rows have at least one claim link: PASS
- every benchmark claim id resolves exactly once: PASS
- existing benchmark semantic/card/label fields unchanged: PASS
- existing claim fields unchanged except C017/C023 locator metadata: PASS
- C017/C023 claim text unchanged: PASS
- NC1 remove a benchmark's claims: RED
- NC2 duplicate a claim id: RED
- NC3 revert C017 to subreddit root: RED
- NC4 revert C023 to generic Issue locator: RED

This candidate does **not** make the 24-row benchmark an answer key. Objective 6 remains Captain-owned and S16B remains blocked on accepted S16A plus later vocabulary/benchmark freeze.
