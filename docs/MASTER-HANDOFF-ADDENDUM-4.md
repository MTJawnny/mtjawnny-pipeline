# MTJAWNNY T3 ARC — MASTER HANDOFF ADDENDUM 4 (2026-07-30 → 08-01 sessions, rev 2)

Purpose: paste this + MASTER-HANDOFF.md + ADDENDUM-2 + ADDENDUM-3 into a fresh
chat (Fable 5) or point Claude Code at all four and be current immediately.
Covers: batches 5–7 triage, Gate #0 and the legality brand rule, the naming
grammar + validator + DET era, the walk ratification, the packed-request
pricing arc, batch 8's four-arm A/B, and the CONSENSUS PIVOT now in progress.
Where this conflicts with earlier handoffs, this addendum is newer and governs.

---

## 1. What changed (one paragraph)

The bootstrap converged (override rate b1 0% → b7 ~2%; batch 6 had zero
axis-level corrections) and was retired after batch 7 in favor of the
corpus-pass gauntlet. Codebook is v0.7-post-walk: ~281 active axes (306 − 23
renamed-in-place − kicker kill − net surgery), all slugs governed by a
CR-anchored naming grammar with a machine validator. A legality gate (Gate #0)
now excludes nowhere-legal cards corpus- and brand-wide. 44 ratified DET
patterns own the template axes; SYNTH is banned from the activation-restriction
family. Packing collapsed the full-pass price from $707 to ~$42–64, but batch
8's four-arm A/B found (a) packing costs ~9–10pp accuracy beyond baseline and
FAILED the accuracy gate as built, and (b) the bigger discovery: same-harness
same-input repeat agreement is only 77.4% on canonical labels — single-shot
tagging of ANY architecture is below the accuracy bar. The project is now
mid-pivot to a consensus architecture (multiple cheap packed runs,
intersection = corroborated, singletons = provisional/buried), pending a FREE
canonicalization re-score of batch-8 outputs that decomposes wording variance
from judgment variance.

## 2. IMMEDIATE state: RUN 1 OF THE FULL-CORPUS PASS IS TRIGGERED (2026-08-01, overnight)

The canonicalization re-score RAN (free): canonicalize_label() built as
permanent reconcile infra (a stemming-order bug found and fixed:
"mass"→"mas"); recovery was only 0.8–2.4% of free-lane disagreement — the
variance is real judgment divergence + synonym invention, NOT wording noise.
B-D stayed at 77.4% on codebook lane. Per the decision rule, consensus is
mandatory; Captain then ruled:
- **Design 2 (targeted third run) REJECTED** — 64.3% real disputed rate makes
  targeting illusory ($19.63 saved vs full M=3); its outcome split was an
  estimate, Design 1's was measured.
- **Lane-aware consensus RATIFIED:** M-run intersection applies ONLY to
  codebook-lane and grammar-lane tags (agreement = corroborated tier,
  singleton = provisional tier, rank-buries). Free-lane output from all runs
  is UNIONED and routed into standard consolidation as discovery candidates —
  never scored as tag disagreement. (Rationale: the free lane produces
  discovery input, not final tags; label-string mismatch there is a
  clustering job, not a dispute. Batch-8's bleak 29.4% corroborated figure
  was an artifact of scoring the free lane with intersection logic;
  lane-aware recompute was ordered with the trigger.)
- **RUN 1 TRIGGERED** (single M=1 pass now; staged-corroboration path chosen
  over paying for M=2 upfront): N=40, intro batch, full untrimmed schema,
  ~$55 projected. Order of operations in the directive: DET pass first with
  sample-sheet gates (failure = halt, zero spend) → packed-schema pre-flight
  vs the structured-output limit → live-price + cost-stop check → submit.
  Batch ID + RESUME-NOTE.md committed pre-submission for session-expiry
  safety. Corroboration wave 1 is a FUTURE trigger, NOT authorized.

**Resume point for the next session:** check RESUME-NOTE.md / the batch ID.
Expected states: (a) completed → fetch, reconcile, report per standing
format incl. lane-aware corroborated/provisional actuals, DET-SYNTH
contradiction rows, spend vs ceiling; (b) halted pre-submission → read the
stated reason, nothing spent; (c) batch still running → wait/poll (results
persist server-side for weeks, retrievable by ID from any session).
After run 1 reconciles: staged corroboration waves ($15–20 each, tooling
built: foundry_corroboration_pass.py), ordered by site-featured cards first,
each its own Captain trigger — then schema pass, then display build.

## 3. Money + deadlines

- Spent pre-run-1: ~$33 (batch 8; errored requests unbilled; caching CONFIRMED
  applying on Batch API — real Arm-C per-card cost $0.001691 incl. cache).
- Run 1 projected ~$55 → ~$88 cumulative after it lands.
- **EMERGENCY COST STOP (standing rule, logged in CORPUS-PASS-PLAN.md):**
  $140 cumulative arc ceiling. Before ANY Batch API submission: live-priced
  estimate + projected cumulative spend; would-exceed → HALT and report, no
  exceptions. Future sessions inherit this rule.
- **Billing-layer backstop:** Captain sets a Console monthly spend limit
  (~$150) at platform.claude.com/settings/limits — enforced by Anthropic's
  billing; auto-reload will not fire past it. Agent stop = smart layer,
  Console limit = unbreakable layer.
- Post-run-1 headroom: ~$52 for corroboration waves before the ceiling.
- OUTPUT-TRIM proposal REJECTED for the corpus pass (accuracy-first; full
  evidence quotes mandatory on all lanes) — annotated considered-and-declined.
- **Intro pricing lapses Aug 31, 2026** — the only real deadline. Standard is
  1.5× if missed.

## 4. Ratified rulings registry additions (this arc)

| Ruling | Statement |
|---|---|
| Legality gate / brand rule (b6 D1, PARTIAL REVERSAL) | A card must be legal (or restricted) in ≥1 format to be a valid target for the engine, scan, and every MTJawnny tool. Alchemy-only passes; Un/playtest/Unknown Event out. Gate #0 at dataset level; retroactive scrubs done (173 + 53 members). Stated brand-wide fact. |
| M8 generalized (b6 D3) | Multi-class targeted-<action> cards get every applicable per-class tag, all action verbs, never combo tags; removal-for-breadth is wrong. |
| Remove-and-rehome (b6 D5) | Every member_removal must state where the card goes: existing axis, convention-consistent sibling, or explicit ledger flag. Silent stranding = protocol violation. |
| Member roster mandatory (b6 D6) | Structurally required in every triage doc. |
| Lattice grammars (b6 §11.2) | Captain ratifies GRAMMARS (stem + closed facet slots); virtual nodes instantiate on first quote-verified member, no fresh ratification; empty axes never authored; lane=codebook-grammar for grammar-composed slugs. |
| CODEBOOK-NAMING-GRAMMAR v1.1 (RATIFIED) | Slot grammar [DELIVERY]-[EFFECT]-[OBJECT]-[SCOPE]-[QUALIFIER]; CR-anchored closed vocabularies; counter laws (typed nouns, counters- verb, "countered" banned); cost-position law; "defender" banned (defending-player); death-trigger stays family word; bare verb stems; -scales-with- sole connective; validator (validate_slug.py) gates every slug; idiomatic job-leaf exemptions (11 ratified). |
| Activation-restriction family (D-4) | Fully enumerated (8 forms, CR 602.5), DET-OWNED, SYNTH banned from assigning it. |
| 9-bucket keyword taxonomy | From CR 702 first-lines: static/triggered/activated/hybrid/evasion/special-action/characteristic-defining/spell/rules-modifying (+ambiguous-card-dependent, +8 verify-or-drop unclassified). casting-modifier demoted to orthogonal facet flag. Ascend=hybrid (702.131a/b). |
| Unblockable/evasion design (Q8 final) | "unblockable" reserved for absolute "can't be blocked" (no except-by/by-/unless/as-long-as rider; duration ≠ restriction). Riders → cant-be-blocked-<restriction> grammar (by-color, by-power, except-by-count, as-long-as-<state>, by-controller). Granted forms live under grants-<keyword> scheme via the b1-Q1 unblockable carve-out (definitions rewritten, slugs unchanged until schema pass). Keyword evasion gets no rule: axes. Derived `evasion` parent ledgered (CR 113.12 anchor — 509.1h was a walk citation error, corrected). |
| Kicker kill (Q9) | rule:kicker-conditional-bonus-effect killed as bare-keyword duplicate (CR 702.33a; b1/b2 precedent). |
| DET pattern discipline | Patterns versioned like scoring constants (det-patterns-v1.json: 44 ratified + 1 withdrawn); fixed-seed 20-hit sample sheet per pattern at DET-pass time, any failure halts before provenance writes. |
| DET preprocessing standard v1 | One pipeline (foundry_common.det_scan_texts()): CARDNAME canonicalization, modal-bullet splitting, polarity, templating-era, all-faces, per-clause subject checks (G2: imposed-on-others ≠ self). |
| Generated artifacts law (G4) | Never hand-edit generated JSON; fix the producer, re-run, diff. |
| Constants untouchable (G1) | DET-scale membership never triggers agent reinterpretation of ratified engine constants (DERIVED_WEIGHT, DF ceiling 172, MV mults, bands). Bad interactions are report rows for Captain. |
| Backup law | Pre-mutation timestamped backups of codebook.json/grammars.json (the b7 reconcile-revival bug was caught only by backup; revival now UNIONS legacy members, never overwrites). |
| Lane-aware consensus (2026-08-01) | Intersection/corroboration applies to codebook+grammar lanes only; free lane is UNIONED into consolidation as discovery, never scored as disagreement. Corroborated/provisional two-tier provenance, rank-buries. Design 2 (targeted M=3) rejected. Staged corroboration waves replace upfront M=2. |
| Emergency cost stop | $140 cumulative arc ceiling, agent-enforced pre-submission with live pricing, persisted in CORPUS-PASS-PLAN.md; Console monthly limit (~$150) as billing-layer backstop. |
| Canonicalization finding | Deterministic ratified-vocab canonicalization recovers <2.5% of free-lane variance; the rest is judgment/synonym invention. Canonicalizer never guesses synonym equivalence — clustering handles that at consolidation. |
| Packing FAIL (batch 8, scoped) | Packed harness as built rejected for accuracy-first single-shot use (~9-10pp cost beyond the 77.4% same-harness ceiling; N=20 ≈ N=40). Does NOT choose single-card: the ceiling indicts all single-shot runs. Consensus design supersedes the question. |

## 5. Current state (verified numbers, post-walk-execution)

- **Codebook:** v0.7 + walk ratification applied. 305→ active axes after
  kicker kill and Black Gate move; 23 renames executed with bookkeeping; 3
  grant-axis definitions rewritten as facet readings; validator: 170 clean /
  3 warned / 132 flagged (flagged = final-naming-audit backlog by policy).
- **DET:** det-patterns-v1.json 44 ratified (incl. 4 cant-be-blocked and
  imposes-enters-tapped); rule:imposes-enters-tapped authored (24 members,
  rule-derived). DET pass itself (CORPUS-PASS-PLAN step 4) NOT yet run.
- **Wiring:** three-lane prompt + lane=codebook-grammar + D-4 ban in
  foundry_stage1b.py; validator + D-4 rejection in foundry_consolidate.py.
  Smoke-tested only — never exercised on a real batch (the consensus runs
  will be its first live exercise; watch it).
- **Condensation:** SYNTH embedded prompt 23,561 → 19,967 tokens (DET strip
  of 37-39 owned axes + definition condensation). Post-strip axis count for
  SYNTH: 268.
- **Packed harness:** build_packed_request() live; array-of-{oracle_id,axes}
  constant-size schema (the per-id-keyed schema blew the structured-output
  limit — 150 requests errored, fixed, retried clean); position shuffling
  standing (seed 20260731); cache_control on shared prefix.
- **Batch 8 (four arms, same 1,200 cards):** A single-card, B N=20, C N=40,
  D N=20 repeat. Raw exact-set: A-B 18.2/A-C 16.8/A-D 17.2/B-D 34.3%.
  Codebook-lane canonical: A-B 67.2/A-C 68.6/A-D 67.5/B-D 77.4%. Free-lane
  slug self-invention is the dominant raw-noise driver. Tail curves noisy,
  8.0pp worst drop both arms — inconclusive, not clean pass. NO single-card
  repeat control exists (A's own ceiling unknown — known caveat on the FAIL).
- **Corroboration tooling:** foundry_corroboration_pass.py built; projection
  honestly declined pending real full-pass data.
- **Gauntlet status (CORPUS-PASS-PLAN):** 1 Gate#0 DONE · 2 keyword buckets
  DONE+ratified · 3 walk DONE+ratified · 4 DET pass READY (blocked on
  Captain trigger, run it with/just-before the consensus pass) · 5
  condensation DONE · 6 SYNTH full pass = RUN 1 IN FLIGHT (M=1, lane-aware consensus architecture; corroboration waves staged) · 7 schema
  pass · 8 display build.

## 6. Open punch list (supersedes prior lists where overlapping)

**Now / next session:**
0. **BLOCKING (new, 2026-08-01, consolidation-run1 session): member-level
   provenance/tier schema ruling needed before run-1's consolidation can
   write to codebook.json.** `member_oracle_ids` is currently a flat list
   of bare oracle_id strings on every one of the 455 axes (confirmed, 0
   exceptions) — there is no field to carry `source=SYNTH, tier=provisional,
   runs=[run1]` per membership, only axis-level `source`. Per
   CONSOLIDATION-RUN1-DIRECTIVE.md sec.4's own instruction ("HALT and
   propose a shape — do not invent one silently"), this session halted the
   actual codebook.json mutation and instead produced a full dry-run report
   (`experiments/out/foundry/corpus_pass_run1_consolidation_dry_run.json`:
   257 axes would gain >=1 new member, 14,255 new codebook-lane
   confirmations, 21 existing axes would gain 1,127 grammar-lane
   confirmations, 95 new grammar virtual-node axes with 1,297 quote-verified
   members) plus the free-lane discovery artifact (already written,
   doesn't touch codebook.json). Two shape options proposed for Captain's
   ruling: (A) additive `member_provenance: {oracle_id: {source, tier,
   runs}}` dict alongside the untouched flat list (non-breaking, existing
   consumers unaffected); (B) migrate `member_oracle_ids` itself to a list
   of `{oracle_id, source, tier, runs}` objects across all 455 axes
   (breaking — every consumer of the flat-list shape needs updating:
   `foundry_det_pass.py`, `foundry_reconcile.py`'s set-union logic, any
   viewer/emit code). No mutation attempted under either option without
   the ruling.
1. §2 resume point: check run-1 state via RESUME-NOTE.md / batch ID;
   reconcile and report (or read the halt reason). Verify the lane-aware
   batch-8 recompute was reported alongside. **DONE 2026-08-01** — run 1
   completed (32,557/32,557 cards, $57.63 total incl. 2 remediation
   passes for a truncated pack and 30 packs' partial dropout), batch-8
   lane-aware recompute located and confirmed already reported
   (`experiments/out/foundry/batch8_lane_aware_corroboration.json`: 951
   union, 535 corroborated 56.3%, 416 provisional 43.7%). Consolidation
   itself blocked per item 0 above.
2. Unconfirmed from b7 surgery: the Tough Cookie quote-check vs
   rule:etb-create-token-food (ordered with the pay-life amendments; result
   never reported). Verify it happened.
3. b5 D10 leftover: quote-verified token-type classification of the LTB
   parent's direct members (Chittering Dispatcher; Suki, Courageous Rescuer).
4. Contradiction-check heuristic gap: the run-1 DET-SYNTH contradiction
   check shipped two automatable heuristics (structural leak check: 0
   found, confirms the DET-owned strip held; soft det-convergent flag:
   111 found in the initial post-fetch check, 97 in this session's
   independent discovery-artifact pass -- the two runs use slightly
   different canonicalization paths, both counts are informational, not
   reconciled) but true opposite-direction semantic contradiction
   detection needs judgment beyond both — close it during corroboration
   waves (already a ratified wave-targeting category).
5. Site-featured-cards manifest: CONSOLIDATION-RUN1-DIRECTIVE.md sec.6 asks
   for a wave-targeting breakdown of "the 12 built card pages" but no
   manifest of which 12 cards those are could be located in either repo
   (searched docs/*.md both repos, mtjawnny.github.io/cards/, the sec.3.11
   card-authoring resolver spec). Needs Captain to supply the name|slug
   list or point at where it lives.

**At full-pass time:**
4. DET sample sheets (standing condition) gate provenance writes.
5. Corroboration pass on the flagged subset (tooling ready; categories:
   DET-SYNTH contradictions, free-lane-heavy, validator-rejected grammar
   compositions, tail-position if decay shows).
6. First real exercise of the stage1b/consolidate wiring — treat anomalies
   as halt rows.
7. rule:library-dig-to-hand test-case expectation: Plunge into Darkness must
   surface (b5 D16).

**Schema pass agenda (accumulated, one list):**
S1–S7 + T1 (keyword-grant tension, still parked; unblockable carve-out is
the only sanctioned pseudo-keyword) · keyword-bucket integrations (trigger
inheritance; engine projection ruling) · CR-ontology blind-spot audit
(601–616, 700–702) · community-tag convergence check (recall auditor only) ·
facet schemes (keyword-grant, cost-shape, delivery, ownership, spend-target,
restriction-condition) · derived parents incl. `evasion` (CR 113.12) and
create-token/etb families · tap/untap family consolidation · grants-axis
slug/facet consolidation · targeted-destruction/-exile/-discard class facets
(membership check first) · 173-axis unmarked-delivery resolution (mechanical
member-card-type assist suggested) · suffix-family normalization
(-triggers-self-counter vs -self-counter-growth) · death-trigger-draw-card
revival naming · 132-slug validator backlog · etb-create-token's 46
pre-b5 unclassified members · b2/b3 killed cost-shape resurrection
evaluation (D6 follow-up) · imposed-enters-tapped vs enters-tapped scope
family.

**Still live from addendum-2 §7 (unchanged, don't lose):**
Kiki/Helm granted_keyword verification (b1-Q1 carve-out) · duplicate-oracle-
rows trim · equivalence map · GRANT_SIZE_CEILING/F1 at Phase B · playbook
Steps 5–9 (viewer JSONs stale until Step 7) · sanctioned multi-face
oracle-text injection path (product requirement) · pump-axis deferred merges
(b4 D5, batch-4-deferred-examples.md).

## 7. Working discipline reminders (unchanged, load-bearing)

Discuss-before-build · halt-loudly · verify-or-drop (live oracle text, local
CR only — never datadumps, never recall) · §-10-style parsed-directives
sections are authoritative over prose annotations · reversals logged
explicitly, never parsed silently · transcript hygiene (no raw oracle text to
console) · one Code session per distinct work item · determinism ×2 ·
Gate #0 on every corpus probe · pre-mutation backups · Captain's explicit
trigger for every Batch API spend · chat (Fable 5) audits and rules, Code
touches files. The chat-side reviewer role: run the §9 (addendum-3) checklist
on every ratification-bound doc, search live card text for load-bearing
membership claims, and surface contradictions BEFORE parsing — batches 5–8
each caught real errors this way (Captain-side and SUP-side both).

## 8. Quick starts

**Fresh Fable 5 chat:** paste MASTER-HANDOFF.md + ADDENDUM-2 + ADDENDUM-3 +
this. State the topic. Demand verified numbers, not recall. If reviewing any
ratification doc, run the §9 checklist + card searches.

**Claude Code (resume point):** "Read docs/MASTER-HANDOFF.md, ADDENDUM-2,
ADDENDUM-3, ADDENDUM-4, docs/CORPUS-PASS-PLAN.md, and
docs/CODEBOOK-NAMING-GRAMMAR.md. Execute the ADDENDUM-4 §2 canonicalization
re-score directive. Continue through all phases — only stop on genuine
ambiguity, a failed gate, or an unspecified decision. No API spend."
