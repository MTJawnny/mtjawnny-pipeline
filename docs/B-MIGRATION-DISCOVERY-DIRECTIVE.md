# B-MIGRATION-DISCOVERY-DIRECTIVE — provenance schema migration, discovery pass (2026-08-01)

DISCOVERY ONLY. This session MUTATES NOTHING: no codebook.json write, no
schema change, no consolidation write, no script modification, no API spend.
The only files this session creates are its own output documents (§7). If any
step appears to require a mutation or a spend, that is a HALT, not a judgment
call.

## 0. Context (read first)

1. docs/MASTER-HANDOFF.md
2. docs/MASTER-HANDOFF-ADDENDUM-2.md
3. docs/MASTER-HANDOFF-ADDENDUM-3.md
4. docs/MASTER-HANDOFF-ADDENDUM-4.md (§4 lane-aware consensus ruling, §6
   item 0 — the schema-gap HALT this session exists to resolve)
5. docs/CORPUS-PASS-PLAN.md
6. docs/CONSOLIDATION-RUN1-DIRECTIVE.md (the halted directive)
7. The blocked dry-run report from commit 5a7340e (locate it in the repo)
8. docs/DERIVED-TAG-LAYER-SPEC.md — specifically the ratified provenance
   classes: tagger / rule-derived / human (full weight) / llm (discounted,
   never gate-bearing)

Situation in one paragraph: the run-1 consolidation HALTED because
codebook.json's `member_oracle_ids` is a flat list of bare oracle_id strings
(455 axes, 0 exceptions) with no field to carry per-membership provenance
(source, consensus tier, run history), which the lane-aware consensus ruling
requires. Captain has ruled OUT the additive-sidecar bridge (Option A) as
wasted tokens. The target is Option B: `member_oracle_ids` becomes a list of
objects (shape to be ratified) everywhere. This session's job is to make
that migration fully known before a single line changes: every consumer,
every backfill question, every hidden roadblock, every simplification the
codebase might be hiding. All questions answered BEFORE execution.

## 1. Consumer census (the core deliverable)

Find EVERY read and write of `member_oracle_ids` — and every code path that
consumes codebook.json at all, since B changes the file's shape — across
BOTH repos: this one (mtjawnny-pipeline) and ../mtjawnny.github.io. Grep is
the start, not the finish: follow indirection (functions that receive the
loaded dict, scripts that shell out, anything deserializing codebook.json or
artifacts derived from it).

For each call site, record in a table:
- File, function/line, repo
- Operation class: reads-as-set / iterates / counts (len) / mutates-appends /
  mutates-removes / serializes-writes / diffs-or-compares / other (describe)
- What breaks under B (list-of-strings → list-of-objects), precisely:
  set-union on dicts fails, `in` membership tests change semantics, len()
  survives, JSON diff tooling, etc.
- Adaptation shape: trivial accessor swap / needs a helper (e.g. a
  members_as_id_set(axis) accessor) / structural rework / unknown-flag-it

Do not forget the quiet consumers — check explicitly, each is a known or
likely reader:
- foundry_reconcile.py (set-union logic; the rename-bug fix and the b7
  revival-UNIONS-legacy-members law both live here)
- The DET pass apply path (foundry_det_pass.py) — it WROTE full-corpus
  membership on 2026-08-01; it will write again on every Scryfall refresh
- foundry_consolidate.py and the new consolidation script from 5a7340e
- Gates / validation suite / determinism-×2 harness — anything that
  byte-compares or structurally diffs codebook.json against backups or
  snapshots (B invalidates byte-comparison against pre-B backups; how do
  the gates handle that?)
- gate0 scrub tooling, foundry_axis_walk.py, validate_slug-adjacent tooling
- Any viewer/export JSON generation, the resolver, anything in the site repo
  that transitively consumes codebook-derived artifacts
- Tests, CI workflows, ad-hoc scripts in experiments/
- Backup/restore conventions (are backups ever machine-restored by code that
  assumes the old shape?)

Also census the ADJACENT membership-bearing structures so B is defined
consistently: do grammars.json, decisions/batch-N.json, keyword-buckets.json,
or any other artifact carry member lists that should (or should not) migrate
to the same shape? Recommend scope: codebook.json only vs. uniform shape
everywhere, with reasons.

## 2. Backfill analysis (what provenance do the existing 7,699 rows get)

B forces an answer for every existing member at migration time. Map what is
mechanically derivable, with verified counts:
- DET-owned axes (39, det-patterns-v2.json): members → source=rule-derived,
  full weight. Count them.
- Triage-era members: can each be traced to its originating batch via
  decisions/batch-N.json files (batches 1–7)? If yes → source=human
  (Captain-ratified), runs/batch recorded. Report the traceable count and,
  critically, the UNTRACEABLE remainder (members in codebook.json with no
  decisions-file paper trail) — list count per axis for the remainder and
  propose disposition options (e.g. source=human-legacy vs. flag for review).
  Recall the addendum-3 §10.3 full-replay: codebook.json was rebuilt by
  replaying batches 1→5 through the fixed reconciler — that replay machinery
  may BE the traceability mechanism; assess.
- Captain-authored axes' members, derivation-filled members (e.g. the
  targeted-player/planeswalker/battle-damage fills), grammar
  virtual-node members: where do they land in the class vocabulary?
- Alignment requirement: the source vocabulary must map onto
  DERIVED-TAG-LAYER-SPEC's ratified classes (tagger / rule-derived / human /
  llm), with the provisional/corroborated consensus tier as a field WITHIN
  llm-class entries — not a parallel vocabulary. Propose the exact field
  spec under this constraint.

## 3. Schema proposal (draft for ratification, not implementation)

Propose the B object shape with exact field names, types, required/optional
status, and 2–3 realistic examples (a DET member, a replayed triage member,
a run-1 provisional SYNTH member). Address explicitly:
- Determinism: canonical sort order for the member list and for keys within
  each object; serialization settings (the determinism-×2 law must keep
  producing byte-identical output post-B)
- Size: measure current codebook.json size; project post-B size with the
  proposed shape at 23,688 membership rows (post-consolidation scale). If
  bloat is material, propose mitigations (short field names, enum codes)
  WITH the readability tradeoff stated — agent-legibility is a ratified
  language standard.
- Versioning: how the file self-identifies as post-B (schema_version field?)
  so old tooling fails loudly instead of misreading.
- Future-proofing against known upcoming needs, so B is done ONCE: multi-run
  histories (runs=[run1, wave1, ...]), corroborated-tier upgrades in place,
  the schema pass's parent/child structure, and the equivalence-map and
  resurrection punch items. Do not design those features — just verify the
  shape doesn't foreclose them.

## 4. Migration mechanics (plan on paper, execute nothing)

Draft the execution plan the follow-up session would run:
- Producer-side: which scripts must be modified, in what order, so that G4
  (never hand-edit generated artifacts — fix the producer, re-run, diff) is
  satisfied end to end. The migration itself must be a script (re-runnable,
  deterministic), not an edit.
- The write sequence: backup law → migrate → integrity checks → determinism
  ×2 → then the run-1 consolidation write lands ON the new shape. Assess:
  should migration and consolidation be one session or two? (Bias per house
  style: one session per distinct work item — but state the dependency
  honestly.)
- Post-migration verification: membership-identity check (the set of
  oracle_ids per axis is EXACTLY unchanged by migration alone), count
  checks, gate-suite pass, and a defined answer for how pre-B backups remain
  usable for audit.
- Rollback story if a post-migration gate fails.

## 5. Roadblock hunt + simplification hunt (open-ended, this is the point)

Beyond the structured sections: actively look for what the machine is hiding
in both directions.
- Roadblocks: assumptions baked anywhere that membership entries are
  strings (hashing, JSON keys, set literals, sort(), string formatting into
  reports/console), snapshot fixtures with the old shape, anything that
  round-trips membership through a format that can't carry objects.
- Simplifications: is there a cleaner path than anticipated? Examples to
  evaluate honestly (adopt none without evidence): a single load/save module
  boundary that already mediates ALL codebook access (making B a one-file
  change + accessor swaps); the possibility that most consumers only ever
  need the id-set view, making a canonical `members_ids()` accessor the
  entire compatibility story; whether the replay machinery means backfill is
  free.
- Anything found that is NEITHER: report it anyway under "observations."

## 6. Also answer while in there (zero-mutation report items)

1. The dry-run report's count gaps from the chat-side audit — explain with
   verified numbers, correcting the record in THIS session's output doc
   (the dry-run report file itself gets corrected at execution time, not
   now): (a) the grammar-lane "1,297 total members across 95 new nodes"
   figure vs. the arithmetic (2,561 − 1,297 − 646 = 618 instances; sanity
   panel implies ~607 rows) — which number is real; (b) codebook lane
   16,149 vs. accounted 16,114 (35 missing — intra-run duplicates?);
   (c) free lane 28,889 = 28,243 + 646 exactly, so where are the 24 folded
   anomalies.
2. The 141 exact-match free-lane reinventions: confirm current disposition
   in the computed dry-run state (promoted to codebook-lane confirmations
   per the halted directive §4, or still sitting in discovery).
3. Token-multiset reorder measurement (report-only, no promotion): sort each
   free-lane canonical cluster's tokens and match against (active slugs +
   ratified grammar compositions) with tokens sorted likewise. Report how
   many clusters / instances are pure reorderings (the
   creature-targeted-destruction ↔ targeted-destruction-creature case).
   This sizes a future ruling; it changes nothing now.

## 7. Output

Write `docs/B-MIGRATION-DISCOVERY.md` containing: the consumer census table
(§1), backfill analysis with verified counts (§2), the draft schema spec
(§3), the migration plan draft (§4), risk register + simplification findings
(§5), the §6 answers, and — mandatory closing section — **OPEN QUESTIONS FOR
CAPTAIN**: every decision the discovery surfaced that requires a ruling,
each stated as a one-line question with the evidence pointer. Nothing in
this document is self-ratifying; it is entirely input to Captain's ruling.

Commit the document (and nothing else). Report per standing format: census
headline numbers (call sites by operation class, trivial vs. structural
adaptation counts), backfill traceability numbers, projected size delta,
top risks, top simplifications, §6 answers, spend $0.00 / cumulative $90.51
/ headroom $49.49, commit hash.

## 8. Standing discipline

Verify-or-drop (measured numbers only, no recall — every census claim points
at a file:line) · transcript hygiene (no raw oracle text to console) ·
Gate #0 irrelevant here (no corpus probes needed; if one becomes needed,
gate it) · G1 constants untouchable · halt loudly on genuine ambiguity ·
one session, this work item only. Continue through all phases — only stop on
genuine ambiguity or an unspecified decision.
