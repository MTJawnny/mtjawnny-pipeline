New session. Working repo: ~/Projects/mtjawnny-pipeline — all git operations,
snapshots, and code changes happen there ONLY. The site repo
(~/Projects/mtjawnny.github.io) is read-only reference this session.

STEP 0 (before anything else): write the RATIFIED RULING MANIFEST and PHASE
WORK ORDER below, verbatim, to
~/Projects/mtjawnny.github.io/docs/RULING-MANIFEST-2026-07-09.md.
That file is now this session's authority. At the START of every phase, and
immediately after every /compact, re-read that file from disk before writing
any code — never work from remembered context. If anything you are about to
do contradicts the file, the file wins; halt if you can't reconcile.

Then read, in order:
~/Projects/mtjawnny.github.io/docs/TIER-ENGINE-STATE-AND-V2_9-ERRATUM-2-HANDOFF.md
  (engine authority; one correction: erratum 2's affected set is 14 cards,
  not ~147),
~/Projects/mtjawnny.github.io/docs/THESAURUS-REFINEMENT-PASS-1-HANDOFF.md,
~/Projects/mtjawnny.github.io/docs/TRIAGE-BATCH-1-similarity-corrections.md,
~/Projects/mtjawnny-pipeline/experiments/measure/FINDINGS-MEMO.md (+ the two
  measurement scripts beside it).
Report headers in experiments/out/reports/ are authoritative for pre-existing
formulas/constants. NOTE: SNAPSHOT-SYSTEM-CHANGE-ORDER.md referenced in the
handoffs is NOT available — Phase 0's inline spec below replaces it; do not
go looking for it.

Working tree must start clean at or after tag tier-engine-v2.9e2-baseline —
verify and print git status first.

=======================================================================
RATIFIED RULING MANIFEST (Captain, 2026-07-09)
Supersedes DRAFT RULINGS 1 and 2 in the refinement handoff — the Gate-0
measurement disproved DR1's flat-DF-threshold premise (wanted and unwanted
DF ranges interleave; see FINDINGS-MEMO.md).
=======================================================================

R1 — PROVENANCE DISCOUNT. A shared-paragraph/fragment match whose evidence
is Mechanism-2-injected reminder text on BOTH sides is discounted hard in
rank regardless of DF. One-side-native matches (Hero-of-Bladehold class)
keep full standing — that overlap is ratified by-design. No named
keyword/phrase lists anywhere; provenance is engine-known (it did the
injecting).

R2 — TWO METRICS FOR T1, PER PARAGRAPH. Paragraphs of >=5 tokens use
ngram-scale DF (T2's existing scale). Paragraphs of <5 tokens use
para_exact_df with their OWN thresholds. Always per-paragraph, never
per-card (matchable_paragraphs are already split per line — existing
behavior, do not change the splitting).

R3 — COMMONALITY BANDS. Provisional edges pending the Phase 1 re-cut:
  Long (>=5 tok) native paragraphs/fragments: full weight DF<=10;
  discounted 11-50; qualifies-but-buried 51-172 (the rescue zone — this is
  what readmits the Lane 1c six); DEAD >172.
  Short (<5 tok) paragraphs: full weight exact_df<=5; discounted 6-39;
  DEAD >39.
  T1 and T2 get SEPARATE constants (Captain ruling) — Phase 1 produces
  separate tables; identical values are allowed but must be separately
  declared constants, never one shared constant.
  Death zones are ratified qualification law (Captain: "kill them, for
  now") — a second lawful exception, alongside the v2.6 corroboration
  gate, to rank-buries-never-excludes. Print this in report headers.

R4 — MANA KINSHIP RUNS PARALLEL, NEVER REPLACES. Literal-text matching is
untouched. The mana path only ADDS qualification (M1/M2 better-tier-wins
pattern). The measured guild-pair regression (ten "{T}: Add {B} or {G}."
families collapsing into one DF=358 skeleton) must be impossible by
construction. No text-normalization replacement gate anywhere.

R5 — MANA-FACT SYSTEM (ratified). Extractors over mana-producing
abilities: amount produced; colors produced AS A SET (order never
matters); colorless amount; source class; one-shot vs repeatable;
any-color / commander-identity-restricted production; mixed
color+colorless outputs. Equivalences: a {C}-run equals its numeral
({C}{C} = {2}, both directions); a hybrid symbol ({W/U}) is ONE pip
carrying its colors. Cascade for within-tier rank: amount first, then
type; exact color set first, then widening (mono, then hybrid, then
multi-pip); EXTRA colors cost rank; entirely WRONG colors cost more than
extra; for mixed outputs the majority component leads the match and the
minority is the tiebreaker (true 50/50 gets no special rule — the other
weight terms decide); drawback/rider text NEVER blocks qualification, only
rank. Land/nonland separation is DISPLAY-LAYER ONLY (READY-TO-SHIP
toggle) — the engine treats lands as ordinary cards, zero special-casing.

R6 — MANA-PIP KINSHIP TIER RULE. Same mana-ability shape sharing at least
one produced pip (or, for the colorless family, comparable amounts under
the cascade) qualifies Tier 2 — the same shared-slot precedent as keyword
kinship (mobilize 2 vs mobilize X). ZERO pip overlap = no shared wording =
NOT T2 via this path; such cards fall through to T3 tags (Captain: Option
B). Kinship evidence rows carry BOTH sides' facts (see Phase 2c).

R7 — STRUCK / PARKED. Black Market Connections is OFF the F1
expected-fix list (its opener is corpus-unique, exact_df=1 — it cannot
flood; re-diagnosis happens in Batch 2). Modal shared-structure bonus is
PARKED as a CO-F design note pending post-fix Boros Charm / Deflecting
Swat evidence. F7 (Rhythm of the Wild / Surrak) is WITHDRAWN by Captain —
engine verified correct; do not use it as a landmark or counterweight.

=======================================================================
PHASE WORK ORDER — phases are hard gates, in order. /compact between
phases as needed (then re-read the manifest file). Halt loudly rather
than paper over anything. Park cleanly at any phase boundary if context
strains — Phase 0/1 results must never be lost to a mid-phase death.
=======================================================================

PHASE 0 — SNAPSHOT SYSTEM (BLOCKING; ratified precondition for ANY fix
code). The original change-order doc is lost; build to this inline spec,
which preserves its ratified invariants:
  - Git remains the revert mechanism for logic/source. The snapshot layer
    is manifest-based and adds: input pinning (paths + checksums of
    oracle-cards, oracle-tags, cards.sqlite, any *.json.gz consumed),
    constants fingerprinting (hash of every ruling constant the engine
    exposes), gate-result capture (which gates ran, pass/fail), and
    optional frozen output caching (reports/exports by checksum).
  - Safety invariants (all mandatory): refuse to snapshot a dirty
    worktree without an explicit --force; refuse to overwrite an existing
    snapshot without an explicit flag; automatic pre-restore backup
    before any restore; halt loudly on post-restore checksum mismatch;
    provide a determinism-verification command (run twice, byte-for-byte
    diff of outputs).
  - Keep it small and stdlib-only, consistent with the repo's style.
  Take SNAPSHOT ZERO = the current v2.9e2 baseline state. Verify one full
  restore round-trip (snapshot -> mutate something trivial in out/ ->
  restore -> checksums match) before proceeding. If any part of this spec
  is ambiguous, choose the strictest reading and print the choice in the
  session log — do not silently relax an invariant.

PHASE 1 — CLEAN-DATA RE-CUT (read-only). Re-run the DF distribution
measurement with provenance segregation: native-only T1 long-paragraph
table, native-only T1 short-paragraph table, native-only T2 fragment
table — SEPARATE T1 and T2 tables per R3. Locate every FINDINGS-MEMO
landmark on the clean tables (the boilerplate set AND the Lane 1c six).
Print the solo exact_df of "{t}: add {c}{c}." for the record.
DECISION RULE: if the provisional edges (10/50/172 long, 5/39 short)
still produce the ladder's wanted/unwanted verdicts on clean data (Lane
1c six qualify-buried; choose-one / equip / flashback / enters-tapped /
draw-a-card evidence dead or buried), ADOPT them and print them as
ratified constants with the header note "confirmed against native-only
distributions." If ANY landmark verdict flips, HALT and print the clean
tables for Captain — never choose replacement numbers yourself.

PHASE 2 — SMALL INDEPENDENT FIXES (each gets its own snapshot + gate
run before the next begins):
 2a. CO-C punctuation: strip purely sentence-final trailing periods
     before tokenization; never touch apostrophes or symbol tokens
     ({t}:). Corpus-wide re-tokenization — expect DF drift; every gate
     delta must trace under the tightened explained-drift definition.
 2b. CO-G resolver: add a layout column to the cards.sqlite build and
     exclude token/emblem/art-series layouts; cross-check against the
     216-name multi-oracle_id list; Llanowar Elves must resolve cleanly
     in both server search paths. Pipeline-level change, engine
     untouched.
 2c. Kinship row completeness: fix the assign_tier() return (~line 1424)
     dropping anchor_param/candidate_param/keyword — rows carry both
     sides. Phase 4's mana-kinship rows must use the same both-sides
     shape.

PHASE 3 — BANDS + PROVENANCE (implements R1/R2/R3; replaces draft CO-A).
find_shared_paragraph gains the two-metric band qualification; T2
fragment scoring gains its own bands including the rescue zone; both gain
the R1 both-sides-injected discount. All band constants printed in report
headers as rulings.

PHASE 4 — MANA FACTS + PIP KINSHIP (implements R5/R6; expands draft
CO-B). Extractors, cascade rank terms, and the T2 mana-kinship
qualification path (parallel per R4). Kinship evidence carries both
sides' pip facts.

PHASE 5 — GATES, DETERMINISM, PARK. Full v2.5–v2.9 standing gate suite
PLUS these new outcome-form gates (print evidence for each):
 G-A Boros Charm: zero T1 rows evidenced solely by "choose one —"; print
     the new T1 count and every surviving row's evidence.
 G-B Swiftfoot Boots: zero T1 rows on the equip reminder alone;
     both-sides-injected matches buried below display cutoff.
 G-C Faithless Looting: flashback-reminder-only evidence produces no
     qualification (DF 173 > ceiling).
 G-D The Lane 1c six qualify T2 in the rescue zone, ranked bottom half:
     Growth Spiral<->Eureka Moment, Garruk's Uprising<->Elemental Bond,
     Cultivate<->Skyshroud Claim, Rhystic Study<->Reparations, Rampant
     Growth<->Natural Connection, Deadly Dispute<->Village Rites. Print
     ranks.
 G-E Hero of Bladehold stays in Zurgo's T2 (one-side-native preserved).
 G-F Arcane Signet: Manalith + the 8 creatures qualify T2 via the
     restored 7-token fragment post-2a. Print each with fragment DF.
 G-G Sol Ring<->Ancient Tomb T2 via {C}{C} pip kinship; drawback text
     does not block; print the breakdown and where Mind Stone / Mana
     Vault / Thran Dynamo land under the cascade.
 G-H Zero-overlap: Gold Myr does NOT reach Elvish Mystic's T2 via mana
     kinship (and vice versa); T3-via-tags is acceptable.
 G-I Guild-pair regression: two same-pair "{T}: Add {B} or {G}."-shaped
     sources still match exactly as at baseline (literal path untouched).
 G-J Ignoble Hierarch: the 0.29 quartet (Llanowar Elves, Delighted
     Halfling, Urborg Elf, Druid of the Anima) is ordered by the cascade,
     no plateau, and Llanowar Elves resolves without a 404.
 G-K Standing count assertions that legitimately move (e.g.
     ABOLISHER_T2_COUNT=52, whose reminder rows the bands now bury or
     kill) are updated by explicit annotated ruling in headers — never
     silently. Every top-10 movement traces to a named cause (band,
     provenance, kinship, punctuation) or STOP.
Determinism twice, byte-identical. Regenerate all reports + full lists +
viewer cache (wipe experiments/out/viewer/data/, re-export all anchors).
Take a post-fix snapshot. Commit with a body summarizing the ruling
manifest. Print a park-point summary for Captain: new engine version,
adopted band constants, gate results, and anything parked.

=======================================================================
CO-D EVIDENCE (parked, NOT this wave) — logged 2026-07-09, Phase 3
rebalance spot-check
=======================================================================

Craterhoof Behemoth / End-Raze Forerunners share a scrambled-order pump
clause the n-gram matcher structurally cannot see: same slots (amount:
+X/+X vs +2/+2 — a parameterized-vs-fixed param, mobilize-X precedent;
keyword-set granted: {trample} vs {vigilance, trample}; scope: creatures
you control; duration: until end of turn) in different word order.
Word-order scrambling defeats contiguous n-grams by construction; the fix
shape is the same as mana kinship — extract the clause as
order-independent FACTS and match facts, as a parallel qualification
path. This is the third slot-kinship family (keywords, mana pips, effect
clauses) and belongs to CO-D as its own future change order. Log only —
implement nothing this session.
