# B-MIGRATION-DIRECTIVE — codebook /1 → /2 schema migration (session 1 of 4, rev 2)

Rev 2 incorporates the external-audit amendments (B-MIGRATION-DISCOVERY.md
§10, A1–A15). Captain-ratified 2026-08-01. ZERO API SPEND — all local
compute; any step appearing to need spend is a HALT. This session does the
schema migration ONLY. Consolidation is sessions 2–3; DET run 2 is
session 4 (A12). Prior rev is in git history.

## 0. Orientation reads (in order)

1. docs/B-MIGRATION-DISCOVERY.md §10 (AMENDMENTS — governs where it
   conflicts with anything below it in the stack), §9, §3, §2
2. docs/MASTER-HANDOFF.md + ADDENDUM-2 + ADDENDUM-3 + ADDENDUM-4
3. B-MIGRATION-EXTERNAL-AUDIT-LLM-HANDOFF.md if present (context; its
   PROPOSALS are advisory — §10 is what was actually ratified)

State-check first: codebook.json schema/version (expect
foundry-codebook/1, v0.7), 455 records, 7,699 membership rows, git clean
y/n. Then proceed.

## 1. Accessor module + lint (A1, A13, R11)

`experiments/foundry_codebook.py`:
- `load_codebook(path)` — halts unless schema == "foundry-codebook/2".
- `member_ids(entry)` / `member_id_set(entry)` — id views over `members`.
- `merge_assertion(entry, oracle_id, assertion)` — creates the member if
  absent (sorted insert by oracle_id); appends the assertion in
  deterministic (class, source_ref) order; HALTS on duplicate
  (class, source_ref) for the same member; recomputes/validates the
  member `tier` per A1 (present iff all-llm; value per the lane-aware
  rule). Existing assertions are NEVER modified or removed here.
- `remove_det_assertions(entry, source_ref_prefix)` — the ONLY removal
  primitive, scoped to rule-derived assertions (A8); a member with zero
  remaining assertions is dropped (logged).
- `lint(codebook)` — schema string; members sorted by oracle_id;
  assertions sorted by (class, source_ref); no duplicate oracle_id per
  axis; no duplicate (class, source_ref) per member; valid UUID shape;
  class/evidence_status/lane vocabularies; llm assertions carry
  original_lane+effective_lane; tier present iff all-llm and value
  consistent with the stack; quote non-empty unless
  evidence_status="legacy-captain-seed"; corpus_ref present on every
  assertion. Every mutating script ends with lint; violations halt.
- Atomic write helper (A13): temp file → flush → lint+verify temp →
  atomic rename over live. ALL mutators in this arc use it.
- Member-add CLI (AG-CLI-01): validates schema/target status/UUID/
  evidence, backs up, MERGES an assertion (never overwrites), appends
  history, lints, writes atomically, prints final sha256, halts on
  DET-axis operations other than assertion-merge of non-DET classes.

## 2. Migration writer (A1, A3, A5, R2, R3)

`experiments/foundry_migrate_codebook_v2.py` — deterministic,
re-runnable, G4-clean. Builds each existing row's SINGLE initial
assertion (existing rows have exactly one known support event each;
multi-assertion stacks grow from session 3 onward):

| Bucket (expected counts, B-MIGRATION-DISCOVERY.md §2) | Assertion |
|---|---|
| DET rows (3,697) | class=rule-derived, source_ref="det-patterns-v2:<pattern_index>", quote=matched clause (regenerated read-only from the det-pass machinery — never re-implemented), corpus_ref=current snapshot date, evidence_status=quoted |
| Decisions-traceable (3,699) | class=human, source_ref="batch-N" (captain-seed rows: "captain-seed-batch-N"), quote from the proposing batch's review JSON where present (corpus_ref=that batch's era snapshot date if recorded, else current, stated in report), else evidence_status="legacy-captain-seed" (A3) |
| Pay-life 8 | class=human, source_ref="pay-life-scrub-2026-07-30", quote from the scrub report/oracle text |
| Shell audit rows (295) | same replay-derived human assertions, under their original slugs (R3) |

Provenance attribution: in-memory replay of batches 1→7 through
foundry_reconcile.reconcile() with ALL paths pointed at a temp dir
(never the live file), rename-chain mapping to current slugs — the
discovery session's measured method. Top-level schema →
"foundry-codebook/2"; `member_oracle_ids` renamed `members` (A1/CDR-11);
axis insertion order preserved.

Also emits `experiments/out/foundry/migration_manifest.json`
(foundry-migration-manifest/1): input hashes + per-(slug, oracle_id)
expected assertion summaries — written by the WRITER for the record; the
verifier does NOT read it as ground truth (see §3).

## 3. Independent verifier (A13 / B-02 — the audit's core demand)

`experiments/foundry_verify_migration.py` — imports NOTHING from the
migration writer's assignment logic (file-level separation; shared code
limited to foundry_common loaders). Re-derives expected metadata
directly from source artifacts and checks EVERY (slug, oracle_id):
1. expected assertion count (exactly 1 post-migration) and class;
2. source_ref confirmed against the source artifact itself (the member
   is genuinely in batch-N's staged decisions / det hit list /
   pay-life report);
3. quote verbatim in the referenced corpus representation (A9 policy:
   validate against corpus_ref snapshot where available; errata'd
   mismatches vs current corpus are REPORT rows, not halts, listed
   card-by-card);
4. DET pattern index resolves in det-patterns-v2.json;
5. tier/lane/evidence_status rules hold.
Any check failing outside the declared report categories = HALT.

Negative tests (run against scratch copies, never live): /1 consumer ×
/2 file; /2 loader × /1 file; duplicate member; duplicate
(class, source_ref); invalid UUID; empty quote without exemption; bad
corpus_ref; tier contradicting stack; interrupted-write simulation
(temp file present, live untouched).

## 4. Reconcile guards (A4)

foundry_reconcile.py gains two hard guards (its only edits):
- load halts if the input file's schema is not foundry-codebook/1;
- writing to the live codebook path halts unless an explicit
  `--legacy-output <path>` names a non-live destination.
Header comment states: frozen /1 legacy producer; replay is provenance
attribution only; there is NO replay-based rebuild chain (A4 retraction).

## 5. Run order and gates

1. Backup law: timestamped codebook.json + grammars.json backups,
   readback-verified (size + sha256 printed) + a restore DRILL to a
   scratch path before any mutation.
2. Run migration writer (atomic write path).
3. Gates — ALL must pass or restore-and-halt:
   - membership-identity: per-record id-set exactly unchanged (455/455);
   - counts: 7,699 members; statuses 307/75/45/26/2; class totals
     rule-derived 3,697 / human 4,002;
   - INDEPENDENT VERIFIER clean (§3), report categories printed;
   - lint clean;
   - determinism ×2: writer twice from backup, byte-identical codebook
     AND manifest.
4. Consumer adaptations: foundry_det_pass.py apply →
   remove_det_assertions + merge_assertion pattern (A8; preserves any
   future non-DET assertions; history note = counts only);
   foundry_gate0_scrub.py → iterate m["oracle_id"], removal drops the
   whole member (gate-0 is a card-level fact, all assertions moot —
   state this in its header); foundry_consolidate_run1.py reads →
   member_id_set. No consolidation writing is built this session.
5. Smoke: axis_walk + det_patterns_probe adapt trivially (len(members));
   stage1b.load_codebook_reference() output byte-identical pre/post.
6. Docs: CORPUS-PASS-PLAN note (blocker cleared, plan session next);
   RESUME-NOTE line; report per standing format + new codebook sha256 +
   file size + quote-coverage table by class + errata report count.
   Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 6. Standing discipline

Halt loudly · verify-or-drop · transcript hygiene (quotes to files ONLY,
never console — A14) · G1 · G4 · determinism ×2 · pre-mutation backups ·
one session, this work item only. Continue through all phases — stop only
on genuine ambiguity, a failed gate, or an unspecified decision.
