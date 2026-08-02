# B-MIGRATION-DIRECTIVE — codebook /1 → /2 schema migration (session 1 of 2)

Captain-triggered (ratified 2026-08-01, B-MIGRATION-DISCOVERY.md §9 —
rulings cited below as R1–R13). ZERO API SPEND: everything here is local
compute. If any step appears to require spend, that is a HALT, not a
judgment call. This session does the SHAPE migration ONLY — the run-1
consolidation write is session 2 (CONSOLIDATION-RUN1-DIRECTIVE-2.md) and
must NOT run here (R12).

## 0. Orientation reads (in order)

1. docs/B-MIGRATION-DISCOVERY.md — §3 (schema), §2 (backfill classes,
   verified counts), §4 (plan this directive enacts), §9 (ratified rulings)
2. docs/MASTER-HANDOFF.md + ADDENDUM-2 + ADDENDUM-3 + ADDENDUM-4
3. docs/CONSOLIDATION-RUN1-DIRECTIVE.md (context only — do not execute)

Print a state-check first: codebook.json schema/version + record count +
membership-row count (expect foundry-codebook/1, v0.7, 455 records, 7,699
rows), git status clean y/n. Then proceed.

## 1. Build the accessor module (R1, R11)

`experiments/foundry_codebook.py`:
- `load_codebook(path)` — halts unless `schema == "foundry-codebook/2"`
  (plain-English message naming the file's actual schema string).
- `member_ids(entry) -> list[str]`, `member_id_set(entry) -> set[str]`.
- `add_member(entry, obj)` — validates the object (field order oracle_id,
  class, tier, runs, batch, quote; class vocab; tier iff llm), halts on
  duplicate oracle_id, inserts keeping the list sorted by oracle_id.
- `lint(codebook)` — invariants: schema string; every member list sorted;
  no intra-axis duplicate oracle_ids; class ∈ {rule-derived, human, llm};
  tier present iff class=llm; runs list-of-str when present; quote str when
  present. Returns violations; callers halt on any. EVERY mutating script
  ends by running lint (R11).
- A small member-add CLI (`python3 -m foundry_codebook add-member <slug>
  <oracle_id> --class human --batch N [--quote ...]`) — the post-freeze
  home for hand-ratified additions (R4).

## 2. Build the migration script (R1–R4)

`experiments/foundry_migrate_codebook_v2.py` — deterministic, re-runnable,
G4-clean (never hand-edit output). Inputs:
- `experiments/out/foundry/codebook.json` (/1, the truth being re-shaped)
- `decisions/batch-{1..7}.foundry-decisions-v1.json` +
  `review/batch-{1..7}.json` — replayed IN MEMORY through
  foundry_reconcile.reconcile() with paths monkeypatched to a temp dir
  (the discovery session's measured method) to build the (slug, oracle_id)
  → {batch, pathway} provenance map, migrating across in-replay renames,
  then following the live codebook's rename chains
- `experiments/out/foundry/batch7_pay_life_scrub_report.json` (the 8)
- `docs/det-patterns-v2.json` + the corpus via foundry_common (read-only)
  — to regenerate each DET-owned axis's matched clause per member for the
  quote backfill (R2). Reuse the det-pass matching machinery; do not
  re-implement patterns.
- review JSONs again for human-row quote backfill (quote of the proposing
  batch where present; captain-seed rows without quotes stay quoteless)

Class assignment (must reproduce B-MIGRATION-DISCOVERY.md §2 exactly):
DET-owned axes' rows → rule-derived, batch="det-pass-1", quote=matched
clause; decisions-traceable rows → human, batch=originating batch, quote
where recoverable; the pay-life 8 → human, batch=7; the 295 shell rows →
human with replay-map batches (R3). Top-level schema → "foundry-codebook/2".
Axis insertion order preserved byte-for-byte; only member lists change
shape. Output via fc.write_json.

HALT conditions: any current member pair absent from the provenance map
(other than the known 8); any DET member without a pattern match for the
quote backfill (that would contradict det_pass_full_hits.json); any count
diverging from §3's gates.

## 3. Backup law, run, gates

1. Timestamped backups of codebook.json AND grammars.json to backups/,
   readback-verified (size + sha256 printed) BEFORE any write.
2. Run the migration.
3. Gates (all must pass, else restore backup and halt):
   - Membership-identity: per record, id-set exactly equals pre-migration
     (455/455; the 13 field-less shells stay field-less only if R3 review
     says so — R3 says uniform for the 442 member-bearing records; the 13
     empty shells gain nothing).
   - Counts: 7,699 rows; statuses 307/75/45/26/2; class totals
     rule-derived 3,697 / human 4,002 (3,707 active+deferred + 295 shells).
   - Quote coverage report: counts by class; missing-quote rows LISTED
     (expected: captain-seed only), not halted.
   - lint() clean.
   - Determinism ×2: second run from the backup, byte-identical.

## 4. Consumer adaptations (same session, R4/R12)

- `foundry_det_pass.py` apply path: emit member objects (rule-derived +
  matched-clause quote); history note trimmed to counts (no embedded
  member lists); write via fc.write_json; end with lint.
- `foundry_gate0_scrub.py`: iterate `m["oracle_id"]`, preserve objects.
- `foundry_consolidate_run1.py`: the two set() reads swap to
  member_id_set. (Its write extension is SESSION 2 — do not build here.)
- `foundry_reconcile.py`: UNTOUCHED except a top-of-file comment marking
  it the frozen /1 legacy producer and pointing at the migrate script for
  the rebuild chain (R4).
- Smoke checks: axis_walk + det_patterns_probe run clean;
  stage1b.load_codebook_reference() output byte-identical pre/post
  (proves the SYNTH prompt is untouched).

## 5. Documentation + report

- CORPUS-PASS-PLAN.md status: note the schema blocker is CLEARED by this
  session (consolidation itself still pending session 2).
- RESUME-NOTE.md: one line (date + commit).
- Report: gate results, class/quote coverage tables, file size before/
  after, commit hashes, spend $0.00 / cumulative $90.51 / headroom $49.49.
- Commit code + docs (codebook.json itself is gitignored — state its new
  sha256 in the report for the record).

## 6. Standing discipline

Halt loudly · verify-or-drop · transcript hygiene (no oracle text to
console; quotes go in files only) · G1 constants untouchable · G4 no
hand-edits · determinism ×2 · pre-mutation backups · one session, this
work item only. Continue through all phases — stop only on genuine
ambiguity, a failed gate, or an unspecified decision.
