# WALK-RATIFICATION EXECUTION HANDOFF (2026-07-31, fresh session)

You are a fresh Claude Code session. The prior session expired AFTER producing
the step 2–3 walk artifacts but BEFORE Captain's rulings were applied — and its
own final report said **"Nothing has been committed."** This document is
self-contained: it carries the complete ruling set (nothing here requires the
dead session's context) plus the execution order and guard rails. Read these
first for standing doctrine: `docs/MASTER-HANDOFF.md`, `ADDENDUM-2`,
`ADDENDUM-3`, `docs/CORPUS-PASS-PLAN.md`, `docs/CODEBOOK-NAMING-GRAMMAR.md`,
`docs/archive/CORPUS-PASS-WALK-RATIFICATION.md`. Where anything conflicts, THIS
DOCUMENT is newest and governs. Halt loudly on genuine ambiguity, a failed
gate, or an unspecified decision — never guess, never paper over.

---

## 0. Where the project stands (one paragraph)

Codebook v0.7, 306 active axes, batches 1–7 reconciled; Gate #0 (legality
gate) live with retroactive scrub done; pay-life axis surgery applied (18→8 +
rehomes). CORPUS-PASS-PLAN steps 2–3 were EXECUTED (keyword buckets from CR
702; combined per-axis walk: validate_slug.py, grammars.json, 19 structural
renames, 41 DET pattern proposals with corpus hit-counts, 10 open questions)
and written to `docs/archive/CORPUS-PASS-WALK-RATIFICATION.md` — all PROPOSALS,
codebook untouched. Captain has now ruled on everything (section 2 below).
Your job: verify state, apply the rulings, wire the deferred mechanisms, and
report — leaving the repo one ratified DET pass away from pricing the
full-corpus SYNTH run. Batch 8 is NOT to be assembled (it is the
dress-rehearsal AFTER the DET pass and condensation).

## 1. STATE VERIFICATION (do this before anything else)

1. Inventory the expected walk artifacts on disk (uncommitted work survives
   session expiry in the working tree, but verify, don't assume):
   `experiments/foundry_keyword_buckets.py`,
   `experiments/out/foundry/keyword-buckets.json` (+ `_report.md`),
   `experiments/validate_slug.py`,
   `experiments/out/foundry/validate_slug_report.json`, `docs/grammars.json`,
   `experiments/foundry_axis_walk.py`,
   `experiments/out/foundry/axis_walk_scaffold.json`,
   `experiments/foundry_det_patterns_probe.py`,
   `experiments/out/foundry/det_patterns_probe.json`,
   `docs/archive/CORPUS-PASS-WALK-RATIFICATION.md`.
   ANY missing → HALT and report which; do not regenerate silently.
2. `git status` / `git diff` — commit the walk artifacts AS-IS first
   ("walk artifacts, pre-ratification state") so the proposal state is in
   history before rulings mutate anything.
3. Back up `codebook.json` and `docs/grammars.json` to a timestamped
   `experiments/out/foundry/backups/` copy (the batch-7 reconcile bug was
   caught only because a pre-change backup existed — this is now standing
   practice).
4. Confirm codebook v0.7 axis count (306 active) matches the walk doc's
   stated baseline. Mismatch → HALT (something ran since the walk).

## 2. THE COMPLETE RULING SET (Captain, 2026-07-31 — authoritative)

### 2.1 Corrections to the walk's own output (fixes 1–4)
- **F1 Ascend → hybrid.** CR 702.131a/b assigns TWO classes (spell on
  instant/sorcery, static on permanent). Fix the extraction LOGIC in
  `foundry_keyword_buckets.py` (multi-class statements classify as hybrid),
  re-run, and diff: Ascend must move spell→hybrid and NOTHING else may change
  unless the same logic bug demonstrably affected it (report any such rows).
  Hand-editing the JSON is forbidden — generated artifacts get generator
  fixes.
- **F2 landfall-produces-mana pattern bug.** 0 hits vs n=1 member: the
  pattern requires a literal mana symbol; text like "add one mana of any
  color" has none. Fix, and SWEEP all 41 patterns for the same
  literal-vs-prose bug class (mana, numbers, symbols), re-probe every
  hit-count, and diff against the ratification doc's table — any changed
  count gets re-flagged in your report.
- **F3 stat vocab add:** `opponent-tapped-creature-count` joins the grammar
  §7 closed stat vocabulary (required by one D-3 rename target).
- **F4 "and" is a validator SOFT WARNING**, not a pass and not a failure —
  add a warning tier to validate_slug.py; new `and`-slugs surface for review
  (grab-bag smell) without blocking.

### 2.2 Ratified as proposed (apply mechanically)
- **Q1** 9-bucket keyword taxonomy; "casting-modifier" demoted to the
  orthogonal facet flag; the 8 verify-or-drop unclassified keywords stay
  open. (Subject to F1.)
- **Q2** Closed DELIVERY vocabulary gains `becomes-targeted-trigger` and
  `blocks-or-becomes-blocked-trigger`. Recover/Training stay per-keyword
  exceptions, logged.
- **Q3** Editorial fix to CODEBOOK-NAMING-GRAMMAR.md §2: DELIVERY table value
  `dies` → `death-trigger` (D-1 already settled the winner).
- **Q4** `rule:cant-be-countered` → `rule:spell-uncounterable`;
  "uncounterable" enters the vocabulary; sweep all definitions/notes for
  references to the old slug.
- **Q5** Vocabulary-extension list ratified (per F4's "and" carve-out);
  remainder of the 198-slug backlog logged to the final naming audit.
- **Q6** All 7 idiomatic-leaf exemptions ratified: burst-draw, cantrip,
  modal, drain-life, combat-trick-pump-own-creature, tribal-anthem-buff,
  alternate-win-condition (joining the 4 existing exempt leaves).
- **Q10** All 4 combat-damage renames: `combat-damage-triggers-{discard,
  loot,proliferate,treasure}` → `combat-damage-to-player-{...}`.
- **§2.2.1's 19 structural renames** ratified (15 × D-3 connective, 1 × D-2
  stem, 2 × typed-counter law, 1 × Q4 above). Renames are executed with the
  standard rename bookkeeping (old slug logged on the axis record).

### 2.3 Q9 — KILL rule:kicker-conditional-bonus-effect
Bare-keyword duplicate of the batch-2 keyword-ledger kill (its own DET
pattern ≈ "has kicker," 260 hits; CR 702.33a defines kicker as a cost
mechanism — b1 bare-keyword precedent applies). Kill with annotation
"bare-keyword duplicate, b1/b2 precedent; members redistribute by actual
effect at the full pass." Its DET pattern is withdrawn from the set. Members
simply lose the tag (rank-buries doctrine); no forced rehome.

### 2.4 Q8 — FINAL unblockable/evasion design (supersedes the drafted grammar)
1. **REJECT** the drafted `<delivery>-unblockable-<scope>` grammar — its
   delivery slot conflated delivery with scope (grammar §1/§6 violation).
   Mark it `status: "rejected"` in grammars.json with this reason (keep the
   record; don't delete).
2. **Terminology law (ratified vocabulary):** "unblockable" is reserved for
   the ABSOLUTE form — "can't be blocked" with no restriction rider. Any
   continuation with "except by", "by creatures with", "unless", or
   "as long as" makes it a BLOCKING RESTRICTION, regardless of delivery.
   Duration is NOT a restriction: "can't be blocked this turn" is absolute
   unblockable with eot duration; "can't be blocked as long as defending
   player controls an Island" is a restriction (family 4).
3. `rule:innate-unblockable` stays: the sole absolute-innate leaf (static
   printed "this creature can't be blocked", self).
4. The three grant axes (`activated-grants-self-unblockable`,
   `grants-unblockable`, `grants-unblockable-target`) fall under the
   already-ratified grants-<keyword> facet scheme with "unblockable" as its
   sanctioned pseudo-keyword value (the b1-Q1 carve-out: "grants-unblockable
   exempt (not a keyword)"). **Minimal-churn execution: do NOT author facet
   leaves or rename these three axes now.** Rewrite their DEFINITIONS to
   state facet readings (duration/scope/delivery read from member quotes),
   quote-check every member, and MOVE any member whose quote carries a
   restriction rider to family 5 below. Slug-level facet consolidation is a
   schema-pass item. T1 stays parked: this carve-out covers "unblockable"
   only, no real-keyword facet leaves get authored.
5. **NEW ratified grammar `cant-be-blocked-<restriction>`** in grammars.json
   (status ratified): closed restriction vocab `by-color`, `by-power`,
   `except-by-count`, `as-long-as-<state>` — extensible only by Captain
   ratification. Seeded by existing `rule:cant-be-blocked-by-color`.
   Non-keyword oracle text only. Ratify compound stem token
   `cant-be-blocked` into the vocabulary so the validator passes the family
   ("blocked" has no counter-law ambiguity; the "countered" ban is
   unaffected).
6. Keyword evasion (menace, skulk, fear, intimidate, shadow, horsemanship,
   landwalk, flying) gets NO rule: axes — the keyword layer owns them (b1
   bare-keyword kills).
7. **Ledger** (PARENT-TREE-CANDIDATES.md): derived `evasion` parent for
   schema pass, spanning families 3–6 plus keyword-buckets.json's evasion
   bucket; CR 509.1b–c anchor. Children = mechanism, parents = job.
8. **DET rebuild on the new boundary:** absolute pattern = "can't be
   blocked" NOT followed by a restriction token; conditional = one pattern
   per restriction-vocab value. Re-probe, and note the old
   `grants-unblockable` pattern's "as long as" branch now belongs to the
   restriction family — expect its hit-count to split accordingly.

### 2.5 DET pattern set — final arithmetic and standing condition
Ratified now: the walk's 41, MINUS kicker (withdrawn, §2.3), MINUS the two
old unblockable patterns (replaced by §2.4.8's rebuilt set), with
landfall-produces-mana fixed per F2. Report the final ratified count
explicitly. **Standing condition on every ratified pattern:** at DET-pass
time each pattern emits a fixed-seed 20-hit sample sheet (seed 20260731 +
pattern index); ANY sample row failing its axis definition halts the pass
before provenance writes. Patterns are versioned like scoring constants —
never silently tuned.

## 3. EXECUTION ORDER

1. Section 1 state verification (halt on failure).
2. F1 → re-run keyword buckets → diff-verify.
3. Q3 editorial fix; Q2 + F3 + Q5 + §2.4.5 vocabulary updates; F4 warning
   tier — then re-run validate_slug.py --batch and report the new
   clean/warn/fail counts (expect ~198 unknown-vocab failures to collapse).
4. Apply renames (§2.2: 19 + Q10's 4 + Q4) and the Q9 kill to codebook.json.
5. Q8: grammars.json updates (reject entry, new family), the three grant-axis
   definition rewrites + per-member quote-check migration, ledger entry.
   Member moves are quote-verified writes; list every move in the report.
6. F2 pattern sweep + re-probe; assemble the final ratified DET pattern file
   (versioned, e.g. `docs/det-patterns-v1.json`) with per-pattern source,
   CR/def anchor, hit-count, and status.
7. Wire the deferred batch-7 D7 mechanisms: validate_slug.py +
   lane=codebook-grammar into `foundry_stage1b.py` / `foundry_consolidate.py`
   (grammar-composed slugs validate or fall to lane=free; SYNTH remains
   banned from the activation-restriction family per D-4).
8. Update state docs so no future session reads stale authority:
   CORPUS-PASS-PLAN status table (steps 2–3 → ratified/applied; step 4 →
   unblocked pending Captain trigger), CORPUS-PASS-WALK-RATIFICATION.md gets
   a RESOLUTION header pointing at this document, grammars.json statuses.
9. Commit in logical units with the standard message discipline. Print
   counts/slugs/paths only — never raw oracle text to console (transcript
   hygiene).

## 4. GUARDS (holes found in pre-execution review — treat as law)

- **G1 (constants untouchable):** the DET pass will eventually multiply
  n_members on template axes (enters-tapped 171 → ~709). Ratified engine
  constants (DERIVED_WEIGHT, DERIVED_QUALIFY_DF_CEILING=172, MV multipliers,
  commonality bands) are NOT reinterpreted, rescaled, or "adapted" for
  DET-scale membership by any agent. If DET-scale DF interacts badly with a
  constant, that is a REPORT ROW for Captain, never an edit.
- **G2 (enters-tapped subject check):** the pattern "enters tapped" will
  false-positive on cards imposing tapped entry on OTHERS (Root Maze class:
  "Artifacts and lands enter the battlefield tapped"). The pattern must
  verify the clause's subject is the card itself; imposed-on-others hits are
  excluded and reported as a candidate sibling axis
  (`imposes-enters-tapped`), not silently tagged.
- **G3 (no facet-leaf authoring):** §2.4.4's minimal-churn rule is binding —
  if the migration seems to want a new axis, that's a halt-loudly question,
  not an authoring license.
- **G4 (generated artifacts get generator fixes):** F1's rule generalizes —
  never hand-edit a generated JSON; fix the producer and re-run.
- **G5 (rename sweep completeness):** every rename must sweep slug
  references in definitions, notes, grammars.json, ledger docs, and any
  decisions-file forward references; a dangling old slug anywhere is a
  failed gate.
- **G6 (Gate #0 everywhere):** every corpus probe and future DET pass runs
  on load_corpus_gated() only. A hit-count computed against the ungated
  corpus is invalid.
- **G7 (scope of this session):** no batch-8 assembly, no SYNTH submission,
  no full-corpus DET pass execution, no cost spend. The DET pass itself
  (CORPUS-PASS-PLAN step 4) runs only on Captain's explicit go after this
  session's report.

## 5. REPORT FORMAT (end of session)

State verification result; F1 diff; validator before/after counts; renames
applied (count + list); Q9 kill confirmation; Q8 migration table (every
member move: card, from, to, quote basis — file only if long, summary
counts in chat); final DET pattern count + the re-probe diff table; wiring
confirmation (stage1b/consolidate); doc-state updates; commits; and a
BLOCKERS list of anything halted. End with the single number Captain needs
next: the post-strip embedded-codebook size estimate, so the full-corpus
SYNTH cost can finally be priced.
