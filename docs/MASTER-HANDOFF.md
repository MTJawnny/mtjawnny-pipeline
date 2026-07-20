# MTJAWNNY T3 ARC — MASTER HANDOFF (2026-07-17 session)

Purpose: drop this file (plus the inventory below) into a fresh chat —
Fable 5 or Claude Code — and be working immediately with zero re-derivation.
This is the single orientation document; the other files carry the detail.
Everything here was verified against the live corpus/engine this session,
not recalled.

---

## 1. Project context (one paragraph)

The Magic Thesaurus (mtjawnny-pipeline) is a deterministic card-similarity
engine: look up a card, find related cards. Tier 0 = same card different
name; Tier 1 = shares an exact ability; Tier 2 = shares wording (plus
kinship mechanisms: keyword, mana, granted-keyword, vanilla-frame);
Tier 3 = same job, different words (Grand Abolisher ↔ Defense Grid).
Engine v2.9-era, ~38,233-card corpus, static-first (batch precompute to
R2, no live backend), every scoring constant a ratified ruling, gates +
determinism ×2 + snapshots on every change, rank-buries-never-excludes
(sole exception: corroboration gate), halt loudly, discuss before build,
nothing committed without Captain's explicit ask. "Tier" is RESERVED
vocabulary for card tiers — worker levels are called worker classes
(see §6).

## 2. What this session established (chronological, with verified findings)

**A. Discovery recall audit** (→ DISCOVERY-RECALL-AUDIT.md). Exhaustive
assign_tier-vs-pool diff over 10 whole-card + 5 face anchors. Whole-card
recall clean; ONE real shipped bug: Phase 3 widened T2 qualification to
the rescue ceiling (DF≤172) but pool seeding still gated n-grams at
DF≤50 — face-mode exports were missing 66–87% of qualifiable T2 rows
(whole-card mode was masked by the Tagger seeding blanket; one latent
miss: Equal Treatment for Bonecrusher). Also: keyword_grant had never
been exercised by the viewer panel (panel composition, not a bug), and
GRANT_SIZE_CEILING=2 leaves Helm of Kaldra with exactly 2 corpus kin
(cost exhibit). Harness trap discovered and documented: card_docs are
NOT complete after build_card_doc() — the granted_keyword_facts
post-processing pass is required before building indexes, or the
keyword_grant dimension silently self-blinds.

**B. Captain's 40-card poke notes reviewed** — verdicts + verified
answers (mill keyword universal in oracle wording, 608 cards / 82 with
printed reminder; Flamescroll's Revel in Silence IS already CI-docked at
1.2 superset; saga/Case headers do NOT block discovery; Death Ward's
matchable surface was EMPTY due to the verb-collision misclassification,
plus a second distinct bug: the card Regenerate's self-name substitution
ate its own keyword verb; Agadeem question answered: Shatterskull
outranks same-CI Fell the Profane because +3.45 of tag score swamps the
2.4 capped CI penalty).

**C. TIER-ENGINE-V3-PROPOSAL.md** — full ruling-proposal set: superset
invariant + gate (D1/D2), normalization fixes (N1 verb-collision, N2
self-name), keyword ledger (single governed per-keyword surface,
supersedes "no keyword curation lists"), shared-subset grants (F1),
carried-keyword-set kinship (F2), instant/sorcery affinity bucket (Q1),
CI attenuation of the tag term (R1), sequencing Phases A/B/C.

**D. Step-back verdict.** Verbatim tiers (T0–T2): near-optimal, audit-
clean, better than the AetherSearch competitor — freeze after Phases A+B.
T3 is the headline promise with the least machinery. Embeddings
empirically FAIL the flagship pair (Abolisher's precomputed vector
neighbors are surface-form creature noise; Defense Grid absent both
directions) — validates the ratified "no text-similarity logic inside
T3." Growth path: engine-DERIVED structural rule: tags (generalizing the
shipped rule:turn-scoped), reusing parsing the engine already does for
penalties. Effort reallocation: T3 buildout over Phase C rank knobs.

**E. DERIVED-TAG-LAYER-SPEC.md** — the rule: namespace design, grounded
in a measured prototype (7 regexes over the full corpus). Three lessons
now load-bearing: **Lesson 1** — every restriction derivation must
canonicalize BOTH polarities ("can't X during Y" ≡ "can X only during
Z"; the Dosan miss). **Lesson 2** — derived tags need their own ADDITIVE
score term (fusion into coverage dilutes and demotes; measured).
**Lesson 3** (ratified during Step 3, see G) — single-member-namespace
flood: the derived term always contributes rank but may be a candidate's
SOLE qualifier only when a shared rule: tag has DF ≤
DERIVED_QUALIFY_DF_CEILING. Provenance classes: tagger / rule-derived /
human (full weight) / llm (future, discounted, never gate-bearing).

**F. T3-BUILDOUT-PLAYBOOK.md** — 9-step Claude Code session guide
(commit sitting work → Phase A → additive T3 term → family-tree evidence
→ land derivations → Batch-API audit harness → derived-layer poke →
Phase B → Phase C parked).

**G. Steps 1–4 EXECUTED in Claude Code (all committed except noted):**
- Steps 1–2: sitting punch-list work committed; Phase A landed (seed
  floor aligned, verb-collision + self-name fixes, superset gate in
  suite, face exports regenerated).
- Step 3: additive T3 term landed. Ratified: **DERIVED_WEIGHT = 0.5**
  and, mid-step after Claude Code correctly halted on a 68→814-row
  flood, **DERIVED_QUALIFY_DF_CEILING = 172** (Lesson 3). Post-fix,
  verified: Abolisher 68→98 rows, zero demotions, Dosan #1 / City of
  Solitude #2 / Defense Grid into displayed top 10; non-turn-scoped
  anchors byte-identical; 94/94 gates; snapshot
  derived-additive-term-v1. **Step 5's gate panel is re-baselined to
  this AFTER state** (Dosan #1 etc. is the new floor). Committed with
  both constants cited.
- Step 4: FAMILY-TREE-EVIDENCE.md produced (5 mandated families + a
  26-card attack-tax bridge the data surfaced; Tagger redundancy table
  added to required outputs). Two harness bugs found/fixed
  (set-iteration nondeterminism in tie-breaks; first-match-only paragraph
  scanning that misclassified Vexing Shusher — ALL-PARAGRAPH SCANNING IS
  MANDATORY everywhere). measure script left untracked (recommend
  committing). Key reading correction from Fable 5: near-zero raw
  co-occurrence is evidence AGAINST complement families but expected and
  meaningless for SUBSTITUTE families (Abolisher/Defense Grid are kin
  BECAUSE cards rarely do both) — read cast-interference and
  resolution-protection through the substitute lens. pay-tax genuinely
  splits into pay-tax-cast vs pay-tax-attack (two derivations).
- Awareness: viewer JSONs are stale relative to the engine until Step
  7's regeneration — do not poke-evaluate against them.

**H. Coverage critique + the Axis Foundry.** Captain's finding, correct:
all 12 existing rule: tags trace to cards HE personally presented
(anchor-driven sampling). Delney measured as proof of the gap:
trigger-doubling DF=39, power-2-or-less DF=122, conditional power
evasion DF=61 — three clean derivations sitting unmined.
→ **T3-AXIS-FOUNDRY-v3.md** (v1/v2 superseded): dual-source mining
(Source A = template mining from clause_df/ngram_df, free; Source B =
per-card functional decomposition of ALL 38,233 cards — the "Delney
treatment" industrialized), reconciled; iterative bootstrap batches
(500 then 1,000–1,500) reviewed by Captain in a purpose-built static
REVIEW TOOL (raw card attributes, no images, evidence quotes
highlighted, own-tag entry, exportable decisions JSON) until a MEASURED
convergence gate passes (OTHER-rate <~5%, kill/merge rate declining ×2
batches); only then the full-corpus pass. Worker classes DET / BULK /
SYNTH / SUP. Evidence-quote-or-discard on every per-card assignment.
Models propose, Captain-ratified deterministic patterns dispose —
nothing model-generated is ever load-bearing.

## 3. Ratified rulings registry (this arc)

| Ruling | Value / statement | Where |
|---|---|---|
| DERIVED_WEIGHT | 0.5 | tier_engine, Step 3 commit |
| DERIVED_QUALIFY_DF_CEILING | 172 | tier_engine, Step 3 commit (Lesson 3) |
| Superset invariant + gate | seeding provably ⊇ qualification, gate-enforced | Phase A |
| N-gram seed floor | := T2_RESCUE_CEILING (named constant) | Phase A |
| Lesson 1 | both-polarity canonicalization mandatory | spec |
| Lesson 2 | derived term is additive, never fused into coverage | spec + Step 3 |
| Worker-class naming | DET/BULK/SYNTH/SUP; "tier" = card tiers only | foundry v3 |
| Step 5 gate baseline | derived-additive-term-v1 AFTER state | Step 3 commit |
| All-paragraph scanning | mandatory in every classifier/derivation | Step 4 |
| Captain-entered tags | human provenance class, full weight, skip model pipeline | foundry v3 |

Pending rulings (open, Captain's): family tree (write against
FAMILY-TREE-EVIDENCE.md's open questions, substitute-lens correction
applied); R1 CI attenuation shape (table vs flat raise — Phase B);
keyword ledger entries (Phase B); Tagger↔rule equivalence map (later,
evidence from Step 4's redundancy table); duplicate-oracle-rows trim
question (see §7).

## 4. File inventory + how to use each

| File | What it is | Use |
|---|---|---|
| MASTER-HANDOFF (this) | orientation | read first in any new chat |
| DISCOVERY-RECALL-AUDIT.md | audit findings + method | reference; harness trap documented here |
| TIER-ENGINE-V3-PROPOSAL.md | Phase A/B/C ruling proposals | Phase B/C change orders draw from it |
| DERIVED-TAG-LAYER-SPEC.md | rule: namespace design, Lessons 1–3, provenance classes | governs all derivation work |
| T3-BUILDOUT-PLAYBOOK.md | 9-step Claude Code session guide | open sessions with "execute Step N" |
| T3-AXIS-FOUNDRY-v3.md | foundry spec: mining, batches, review tool, schemas | Session A entry point (v1/v2 superseded — discard) |
| FAMILY-TREE-EVIDENCE.md | Step 4 output (in repo docs/) | Captain writes the family tree against it |
| foundry_batch1_seed.json | 281 corpus-validated hand-picked cards, 44 buckets | Session A consumes; DET fills to 500 stratified-random |

All .md files live in docs/ (gitignored strategy docs); the seed JSON
goes to experiments/out/foundry/. Claude Code sessions open with:
"Read docs/<file> and execute <step/session>. Continue through all
phases — only stop on genuine ambiguity, a failed gate, or an
unspecified decision."

## 5. The batch-seed method (repeatable — use for every future batch)

Batch 1's seed was built this way; future batches follow the same
procedure with shifted targeting:

1. **Enumerate functional buckets** for the batch's purpose. Batch 1:
   44 buckets spanning the functional gamut (interference, taxes,
   trigger modification, mana shapes, ramp, draw, wheels, tutors,
   removal, wipes, counters(pells), reanimation, gy-hate, aristocrats,
   tokens+doublers, +1/+1 matters, anthems, combat manipulation, blink,
   copy, theft, discard, lifegain, alt-wincons, replacement/restriction,
   cost modification, X-spells, landfall, mill, storm, politics, search
   restriction, modality, vehicles, equipment/auras, typal, alt-casting,
   untap/tap, planeswalkers, enchantress, prevention, weird layouts,
   vanillas).
2. **8–14 cards per bucket, hard cap ~14** (diversity rule: never 50 of
   one mechanic; ~10–15 max even for rich ones).
3. **Deliberately include:** polarity pairs (Panharmonicon AND Torpor
   Orb), multi-axis stress cards (Boros Charm, Esika's Chariot,
   Solitude), layers-hell cards (Humility, Blood Moon), every weird
   layout (split/adventure/transform/meld/saga/class/case/mutate/flip/
   vanilla), and at least one untagged card (Water Elemental).
4. **Corpus-validate EVERY name** against cards.sqlite/name_index before
   emitting — no hallucinated names in seed files; ambiguous matches get
   a disambiguation note (prefer paper over A- Alchemy rows).
5. **DET fills the remainder** (to 500 for batch 1; to 1,000–1,500 for
   later batches) by stratified random sample (type × color ×
   text-length × era, fixed seed, strata printed), deduped against ALL
   previously reviewed cards. The random fill is the bias guard — it
   surfaces axes nobody thought to seed.
6. **Batch 2+ targeting shifts:** hand-picked portion targets (a) axes
   with thin member counts needing confirmation, (b) OTHER-lane clusters
   from the prior batch, (c) strata under-covered so far; random fill
   unchanged. Same validation, same caps.

## 6. Standing vocabulary + traps (fresh-session inoculation)

- "Tier" = card tiers ONLY. Worker classes: DET (deterministic, zero
  tokens) / BULK (small model, Message Batches API, two-pass, structured
  output) / SYNTH (mid model, per-axis) / SUP (supervisor, never bulk).
- Harness trap: granted_keyword_facts must be attached
  (build_granted_keyword_facts + keyword_vocabulary) AFTER
  build_card_doc and BEFORE building granted_keyword_index.
- All-paragraph scanning always (Vexing Shusher first-match bug).
- Determinism: seed everything; Python set-iteration order broke
  Counter.most_common tie-breaks once already.
- Substitute vs complement families: same-card co-occurrence is the
  wrong test for substitute families.
- Corpus has duplicate oracle rows (Llanowar Elves ×2, Ajani's Pridemate
  ×2 — likely Alchemy A- variants): resolver prefers paper; open trim
  question (§7).
- Viewer exports stale until playbook Step 7 regenerates them.
- Live pricing: every Batch API submission requires a cost estimate
  computed from CURRENT pricing docs + Captain go-ahead. Never remembered
  prices.

## 7. Open punch-list items generated this session

1. Family tree: Captain writes rulings against FAMILY-TREE-EVIDENCE.md
   (substitute lens; take the pay-tax split; take the attack-tax bridge).
2. Duplicate oracle rows in corpus → trim-step question (DF double-dip).
3. Commit experiments/measure/family_tree_evidence.py (reproducibility).
4. Playbook Steps 5–9 pending; Step 9 parked behind the §8 poke gate as
   ruled.
5. Foundry Sessions A–E pending; batch-1 seed ready.
6. Equivalence-map ruling deferred until redundancy-table evidence +
   Step 7 poke shows measured double-counting distortion.
7. GRANT_SIZE_CEILING shared-subset replacement (F1) awaits Phase B.
8. **(2026-07-19, foundry cost watch)** The codebook-embedded SYNTH prompt
   is now the dominant Stage 1B cost driver, not card count: batch 2's
   cost estimate rose from batch-2-vs-batch-1's ~$8.05 to batch 3's ~$12.34
   at the *same* 1,200-card size and unchanged pricing, purely because the
   embedded codebook reference grew from 69 to 134 active axes (input
   tokens/request: ~5.1k -> ~8.7k). This will keep growing every batch and
   becomes the limiting cost factor well before the full-corpus pass
   (~38k cards). Before that pass: condense the embedded codebook
   representation (e.g. slug + one-line definition only, drop verbose
   phrasing; or paginate/summarize once the codebook exceeds some size
   threshold). Not actioned yet — flagged for a future session.

## 8. Quick starts

**Fresh Fable 5 chat:** paste this file; state which open item you're
working; Fable 5 has corpus access in-session for verification work —
demand verified numbers, not recall.

**Claude Code, foundry:** drop docs + seed per §4, then: "Read
docs/T3-AXIS-FOUNDRY-v3.md and docs/MASTER-HANDOFF.md §5–6, execute
Session A. Consume experiments/out/foundry/foundry_batch1_seed.json for
the hand-picked portion; DET fills to 500 stratified-random per the
seed's diversity_rule. Continue through all phases — only stop on
genuine ambiguity, a failed gate, or an unspecified decision."

**Claude Code, playbook Step 5+:** "Read docs/T3-BUILDOUT-PLAYBOOK.md
and docs/MASTER-HANDOFF.md §3 (gate baseline ruling), execute Step 5."
