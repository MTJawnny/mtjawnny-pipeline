# B-MIGRATION SESSION 1 — MIGRATE: report (2026-08-01)

Executed `docs/B-MIGRATION-DIRECTIVE.md` (rev 2) end to end. codebook.json is
now `foundry-codebook/2`. Every gate passed; nothing was left partial.
**Spend this session: $0.00. Cumulative arc: $90.51. Headroom vs the $140
ceiling: $49.49.** Zero API calls were made or needed.

Per A12 this was session 1 of 4. **Session 2 (PLAN) is next** and is the
designated external re-audit checkpoint. No consolidation writing was built.

---

## 1. State check (before anything)

`foundry-codebook/1`, v0.7, 455 records, 7,699 membership rows, statuses
307 active / 75 killed / 45 renamed / 26 merged / 2 deferred, git clean
(one untracked doc). Matches the directive's expectation exactly.

## 2. What was built

| File | Role |
|---|---|
| `experiments/foundry_codebook.py` | NEW — the /2 accessor boundary: `load_codebook` (schema-checked both directions), `member_ids`/`member_id_set`, `merge_assertion`, `remove_det_assertions`, `lint`, `write_codebook_atomic`, `backup_codebook`, and the `add-member` CLI (AG-CLI-01) |
| `experiments/foundry_migrate_codebook_v2.py` | NEW — the migration writer; deterministic, re-runnable, halts on a /2 input |
| `experiments/foundry_verify_migration.py` | NEW — the independent verifier (A13/B-02) + the 11-case negative-test suite |
| `experiments/foundry_reconcile.py` | frozen as the /1 legacy producer + two hard guards |
| `experiments/foundry_det_pass.py` | apply path rewritten to the A8 assertion pattern; `quote_pattern_src`/`matched_clause` factored out as the single home for DET clause extraction |
| `experiments/foundry_gate0_scrub.py` | iterates member objects; removal drops the whole member |
| `experiments/foundry_consolidate_run1.py` | reads through `member_id_set`; schema-checked load |
| `experiments/foundry_axis_walk.py`, `foundry_det_patterns_probe.py` | `len(members)` |

## 3. Result

- codebook.json sha256 `21f432817dc7a418ac62846f2bc5ee5edf5ccf28f944b74d4cbafa1059b39d2a`
- size **3,384,958 B** (3.23 MiB), up from 785,747 B (×4.31). Well inside the
  8–9 MB post-consolidation projection A1 accepted. The multiplier is higher
  than the discovery's ×1.76 shape-only figure because that figure excluded
  quotes; R2 projected 6.5–7 MB *with* quotes at this row count, so this
  lands under the accepted budget, not over it.
- `experiments/out/foundry/migration_manifest.json` (`foundry-migration-manifest/1`),
  18 input hashes + per-(slug, oracle_id) expected assertion summaries.
- `experiments/out/foundry/migration_verification_report.json`,
  `migration_negative_tests.json`.

### Class and provenance totals (all measured, all gated)

| | rows |
|---|---|
| class rule-derived | 3,697 |
| class human | 4,002 |
| **total assertions / members** | **7,699 / 7,699** (exactly one assertion each) |

| source_ref family | rows |
|---|---|
| `det-patterns-v2:<index>` | 3,697 |
| `batch-N` | 3,947 |
| `captain-seed-batch-N` | 47 |
| `pay-life-scrub-2026-07-30` | 8 |

Human rows by replay pathway: 3,765 verdict union · 171 rename carry-over ·
47 captain seed · 11 member addition · 8 pay-life. Split across live vs
audit-shell axes, this reproduces the discovery's §2 table exactly:
**3,699 on live axes** (of which 3,641 verdict-union / 47 seed / 11 addition)
+ **295 audit rows on non-active shells** + **8 pay-life** = 4,002.

### Quote coverage by class

| class | evidence_status | rows | % of class |
|---|---|---|---|
| rule-derived | quoted | 3,697 | 100.0% |
| human | quoted | 3,944 | 98.6% |
| human | legacy-captain-seed (A3 exemption) | 58 | 1.4% |

The 58 quoteless rows are exactly the 47 `captain_axes` seed rows and the 11
`member_additions` rows — Captain-ratified per-card judgments recorded in
decisions files that carry no quote field. A3 keeps them and marks them.

## 4. Gates

| Gate | Result |
|---|---|
| Backup law + restore drill | PASS — `codebook.v0.7.pre-b-migration.20260802-010714.json` (785,747 B, sha256 `5e133c24…`) and `grammars.pre-b-migration.20260802-010714.json` (19,155 B, sha256 `9214e67b…`), both readback-verified; restore drill to a scratch path parsed as /1 with 455 records / 7,699 members, live file untouched |
| Membership identity | PASS — 455/455 records, id-set exactly unchanged, zero adds/drops/reorders |
| Counts | PASS — 7,699 members; 307/75/45/26/2; rule-derived 3,697 / human 4,002 |
| Independent verifier | **CLEAN** — every (slug, oracle_id) checked for assertion count, class, source_ref confirmed against the source artifact, quote verbatim, DET index resolution, tier/lane/evidence rules |
| Lint | PASS — 455 axes, 7,699 members, 7,699 assertions |
| Negative tests | PASS — 11/11 |
| Determinism ×2 | PASS — writer run twice from the backup: byte-identical codebook AND manifest, and both equal the live file |

### Verifier report categories (declared, non-halting)

1. **quote-not-verbatim — 1 row.** `rule:create-token-treasure` / *Gluntch,
   the Bestower* (`0222dc7c…`), source_ref `batch-7`. The batch-7 review JSON
   recorded `"Choose a third player to create two Treasure tokens."`; the card
   reads `"Then choose a third player to create two Treasure tokens."` — a
   dropped leading `Then `. Worth naming precisely: this is a **SYNTH
   transcription slip, not corpus drift**, so it is not the "historically true,
   currently stale" case A9 was written for. It is reported rather than
   silently repaired because the assertion records what the proposing batch
   actually claimed; rewriting it would fabricate provenance. Recommend
   Captain either ratify the corrected quote via the `add-member` CLI path at
   consolidation, or leave it as the honest historical record.
2. **pay-life-name-with-earlier-trail — 1 row.** `rule:fixed-lifegain` /
   *Tanglebloom*. The scrub report names 9 additions but the ratified count is
   8: the scrub UNIONS, and Tanglebloom was already a member from batch 3, so
   its earlier and truer provenance stands. This is the arithmetic behind the
   discovery's 8, now mechanically confirmed.
3. **det-pattern-match-exempt — 878 rows across 3 axes**
   (`rule:enters-tapped`, `rule:enters-tapped-conditional`,
   `rule:imposes-enters-tapped`). Their `det-patterns-v2.json` `pattern` field
   is not the standalone matcher that decided membership (two are base regexes
   still needing the probe's G2 subject split; the third's field is prose). The
   verifier confirms these rows against the ratified hit list and validates
   their quotes; only the redundant "does this regex match" re-check is
   exempted, enumerated by name rather than skipped quietly.

## 5. Consumer smoke

- `foundry_stage1b.load_codebook_reference()` — **byte-identical** pre/post
  (sha256 `29b52368…`, 268 slugs). The SYNTH prompt is provably unaffected.
- `foundry_axis_walk.py` — ran clean; all 307 rows' `n_members` match the
  pre-migration counts.
- `foundry_det_patterns_probe.py` — imports clean; 455/455 `len(members)`
  reads match pre-migration counts.
- `foundry_consolidate_run1.py` — ran clean on /2 and reproduced the ratified
  numbers exactly: **1,833** codebook-lane and **170** grammar-lane
  already-member no-ops, 95 virtual nodes, 1,297 grammar pairs. This is the
  strongest single proof that `member_id_set` reads /2 membership correctly —
  a silently-empty read would have reported 0 already-member and inflated the
  new-member count by 2,003. Side effect to note: running it regenerated its
  own two report artifacts (`corpus_pass_run1_discovery.json`,
  `corpus_pass_run1_consolidation_dry_run.json`) from the same deterministic
  producer. Their numbers are unchanged; the dry run's `block_reason` string
  was deliberately updated, since it still claimed a schema blocker that no
  longer exists — leaving a generated report asserting a cleared blocker would
  have been the wrong kind of quiet.

## 6. Findings worth Captain's attention

1. **The rename alone would have failed SILENTLY, not loudly.** The discovery
   (§0 finding 3) held that /1-era tooling meeting a /2 file dies immediately
   on `set()` of dicts. That is true only for the direct-subscript shape.
   `entry.get("member_oracle_ids", [])` — which is what
   `foundry_consolidate_run1.py` actually used — returns `[]` on a /2 entry
   with no error at all, so every axis would have looked empty and every
   run-1 hit like a brand-new member. Renaming the field to `members` (A1 /
   CDR-11) converts every such site from a loud TypeError into a quiet wrong
   answer. What makes it safe is the schema check in `load_codebook()`, which
   is therefore load-bearing rather than belt-and-braces. Captured as a
   negative test so it stays true.
2. **There is only one corpus snapshot in this repo's entire history.**
   `data/raw/oracle-cards.jsonl.gz` has not been refreshed since 2026-07-03/04;
   `data/artifacts/latest.json` reports version `2026-07-04` and 38,233 cards,
   which matches the loaded corpus exactly. So the directive's "that batch's
   era snapshot date if recorded, else current" resolves to `2026-07-04` for
   every assertion — there is no ambiguity to arbitrate. (Batch assembly files
   carry an `assembled_on`, but that is an assembly date, not a corpus
   snapshot date; using it would have recorded a false precision.) `corpus_ref`
   is read from `latest.json` at write time, not hardcoded. A consequence
   worth stating plainly: **the near-total quote fidelity above is not
   evidence of corpus stability over time** — nothing has had the chance to
   drift yet. The first Scryfall refresh is when A9's errata machinery will
   actually earn its keep.
3. **Rename chains have intermediate nodes that legitimately hold members.**
   `rule:combat-damage-to-creature-triggers-self-counter` →
   `…-to-player-triggers-self-counter` → `…-to-player-triggers-self-plus1-counter`:
   the middle slug is a renamed shell still holding 4 audit rows. Any tool that
   maps an old slug to "its current name" by chasing to the END of the chain
   will mis-handle those rows. The verifier now checks every node on the path.
   Flagging it because the session-2 plan will do a great deal of slug routing.
4. **`foundry_reconcile.py` now requires `--legacy-output`.** Any muscle
   memory or doc that invokes it without one will halt. The in-memory replay
   used for provenance attribution is unaffected (it points the module path at
   a temp dir, which the guard permits and the live path forbids).

## 7. Not done, deliberately

- No consolidation writing (session 3, and only from an approved session-2 plan).
- No DET run 2 (session 4).
- No llm-class assertions exist yet; every member carries exactly one
  assertion. The multi-assertion machinery (`merge_assertion`, tier
  recomputation, the lane-aware corroboration rule) is built, linted and
  negative-tested, but is exercised only by tests until session 3.
- `docs/grammars.json` untouched (backed up per the directive; it carries axis
  slugs, not card membership, and §1.3 ruled it out of scope).
