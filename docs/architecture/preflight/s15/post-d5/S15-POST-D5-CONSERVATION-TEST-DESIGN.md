# S15 post-D5 — conservation test design

Measured at accepted head `9b7203d337c6685563ff45a76ef51432dd8c2f0c`.
Baseline for comparison only: `adbe6197a92711cfab5bb5e98fdd6e98c330f006`.

**Nothing here is authorized to run as an implementation.** This records the
conservation surfaces that already exist, the ones a future slice would have to
extend, and the negative controls that proved the audit method can fail.

## 1. What is already conserved by a permanent test

| surface | owner | what it actually pins |
|---|---|---|
| four archive families, byte identity | `tests/refoundation/test_s15_d4_archive_conservation.py`, `tests/refoundation/test_s15_d5_codebook_transforms_archive.py` | blob id, SHA-256, byte count and mode against each slice's own accepted head |
| historical prior-art registry | both modules above | exactly four explicit owners, distinct labels, no recursion, each registered once |
| C8.5V nomination set | `tests/refoundation/test_codebook_store.py` | fifteen nominees, six retargeted addresses, verdict totals unchanged |
| `ProjectPaths` property set | `tests/refoundation/test_paths.py` **and** `tests/refoundation/test_layout_delegation.py` | two independent exhaustive literal pins |
| S10 caller provenance | `tests/refoundation/s10_foundry_common_callers.json` + its tests | live/archive split and each moved row's `foundry_common` symbol set |

## 2. The conservation surface that is NOT yet pinned

**The tracked ruling registry.** `tests/guards/gate2/foundry_ruling_registry.py`
runs in Gate 2 as `--check-only`, which compares pinned *metrics*
(127 distinct / 86 corroborated / 41 sole-home). Those are unchanged, so the row
exits `0`. The *document table* is not compared, and at this head it is stale:

- committed: **142 documents / 684 references**
- regenerated here: **138 documents / 660 references**
- the committed table still lists two AQ4 addenda that now live under
  `benchmarks/aq4/docs/`
- the committed table **omits** `docs/ACTIVATED-REGENERATE-SELF-DET-LAW.md`,
  which is the sole home for `R8.3` and is therefore deletion-BLOCKED

A document that is deletion-blocked is missing from the artifact that records
deletion-blocking. That is a truth gap, not a formatting gap, and no guard fails
on it today.

## 3. Method controls actually exercised

Fourteen controls were rigged and each was observed detecting the defect it was
aimed at; every rig was restored byte-exact and the tree verified clean. Three
rigs (hidden caller, subprocess consumer, synthetic sole-home ruling) initially
reported MISSED; each was an **invalid rig**, not a method failure — the first
two were untracked so `git grep` could not see them, and the third did not match
the registry's `SHORT_ID` grammar. They were rebuilt and re-run rather than
recorded as either a pass or a finding.

## 4. What a future slice would have to prove

Any slice that touches a remaining candidate must show, for that candidate:

1. no static, dynamic, subprocess, path or routing consumer remains;
2. no unique truth/law/provenance/benchmark/fixture/authority/selector/baseline/
   incident/recovery value is lost;
3. a permanent successor exists wherever behaviour existed;
4. no guard is weakened by removing its population;
5. tests and Gate 2 preserve *meaning*, not merely green status;
6. clean-checkout and runtime recovery do not depend on it;
7. no document sole-home or corroboration is lost;
8. negative controls show the method could have detected a hidden dependency.

At this head no candidate satisfies all eight, which is why `DELETE_SAFE` is
**0**.
