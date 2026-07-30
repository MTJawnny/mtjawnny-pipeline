# MTJAWNNY T3 ARC — MASTER HANDOFF ADDENDUM 3 (2026-07-29 session)

Purpose: paste this + MASTER-HANDOFF.md + MASTER-HANDOFF-ADDENDUM-2.md into
a fresh chat (Fable 5) or point Claude Code at all three and be current
immediately. This addendum covers the schema step-back arc: the
atomics-vs-compounds ruling, the keyword-bucket discovery, the three-source
architecture, the batch-4 ratification translations, and the REVISED
SEQUENCING (keyword buckets now precede the full-corpus pass). Where this
conflicts with earlier handoffs, this addendum is newer and governs.

---

## 1. What changed this session (one paragraph)

Captain proposed decomposing compound axes (etb-loot) into atomic tags
(etb + loot) for browsing variety; resolved instead as DERIVED PARENTS —
compounds stay authored, broad tags computed from suffix unions at schema
pass, most-specific-node scoring unchanged. That discussion surfaced the
keyword-bucket insight: CR 702 classifies every keyword as
static/triggered/activated in its first line, so triggered keywords
(annihilator, firebending) can mechanically inherit trigger-family parents.
That generalized into a CR-ontology blind-spot audit plan and a
three-source architecture (CR skeleton / foundry leaves / community tags as
recall auditor). Batch 4 was annotated and translated into §10 directives
including one PRECEDENT REVERSAL (cost-shape axes are now legitimate).
Captain then ratified a sequencing change: the full-corpus pass runs WITH
keyword buckets built and SYNTH made bucket-aware.

## 2. RATIFIED SEQUENCING (supersedes addendum-2 §5 sequencing)

1. Bootstrap batches continue until override-rate convergence (b1 0%,
   b2 6.9%, b3/b4 per emit reports).
2. **Keyword-bucket extraction (DET job, NEW, gates the full pass):**
   walk CR 702 in the local `mtg-comprehensive-rules.md` (June 19, 2026),
   read each keyword's classification line, emit versioned
   `keyword-buckets.json`: slug → {static | triggered | activated |
   hybrid | casting-modifier}, plus trigger-family for triggered keywords
   (attack-trigger, cast-trigger, death-trigger, etc.) read from the
   template text in the CR entry. Every classification cites its CR rule
   number. Verify-or-drop; no recall.
3. **SYNTH prompt update:** full-corpus SYNTH gets keyword-bucket
   awareness + the batch-4 ability-type check (activated vs triggered vs
   cost-vs-effect). Prompt addition only — touches no ratified scoring
   constants. Rationale: this is the class-check that would have prevented
   batch 4's 9-of-16 wrong members in activated-tap-target-creature.
4. **Codebook condensation** (already punch-listed; cost driver).
5. **Full-corpus pass** (~38,233 cards, ~$100 approved, explicit trigger
   still required).
6. **SCHEMA PASS** (parents, facets, keyword inheritance, S1–S7, T1,
   three-source reconciliation, blind-spot audit).
7. Display build per READY-TO-SHIP contract.

## 3. Core ruling: compounds authored, atomics derived

- **Compound** = trigger + effect glued (`etb-loot`), asserts one ability
  does both. This is the ONLY thing the foundry authors, with oracle-text
  evidence quotes.
- **Atomic/broad tags** (`loot`, `etb`) are NEVER authored. They are
  DERIVED at schema pass: a script unions every `*-loot` compound into a
  `loot` parent. Free, deterministic, cannot drift from the leaves.
- Why not author atomics: (a) double authoring cost on 38k cards,
  (b) drift risk (compound present, atomic missing → silent search
  misses), (c) crossed-wire risk on multi-ability cards (independent
  atomics can't say WHICH ability loots — demonstrated live in-session),
  (d) score double-counting (solved by ratified most-specific-node rule:
  only deepest shared tag counts; broad tags are for browsing, not
  points).
- Browsing UX Captain wants (search `loot` broad → click into
  `combat-damage-triggers-loot` narrow) is exactly what derived parents
  deliver. No architecture change needed.
- **Second parent dimension ratified for the ledger:** effect-family
  parents (`loot`, `create-token`, `lifegain`, ...) derived from compound
  SUFFIXES, cross-cutting the trigger-family parents. Multi-parent edges
  resolved under S4 at schema pass. Interacts with S5's counts-toward
  semantics.
- **Naming directive for beta (forward-looking only, no renames):** new
  axes named `<trigger>-<effect>` with consistent effect suffixes so
  suffix-derivation has clean handles. Suffix consistency is now
  schema-FUNCTIONAL, not cosmetic — final naming audit is load-bearing.

## 4. Keyword buckets (the discovery, verified against project CR)

CR 702 prints each keyword's ability class in its first line. Verified
in-session from the local CR file:

| Keyword | Class | CR |
|---|---|---|
| Deathtouch | static | 702.2a |
| Trample | static | 702.19a |
| Annihilator | triggered | 702.86a |
| Firebending | triggered (attack trigger: "whenever this creature attacks, add N {R}") | 702.189a |
| Level up | activated | 702.87a |
| Station | activated | 702.184a |
| Decayed | hybrid (static + triggered) | 702.147a |

Mobilize NOT yet verified (didn't surface in the session search) — the
extraction job verifies it like everything else. Buckets: static /
triggered / activated / hybrid / casting-modifier (flash, convoke, etc.).
The handful of genuine hybrids get per-keyword rulings, not forced into a
bucket.

**Payoff:** a triggered keyword is not an opaque string. Annihilator
carries `attack-trigger` parentage IN ADDITION TO its keyword identity
(add, don't absorb; most-specific scoring keeps keyword-exact matches
ranked above mere trigger kinship). A card with annihilator becomes
discoverable next to "whenever a creature you control attacks..." cards.

**Two integrations, both SCHEMA PASS (only extraction + SYNTH awareness
run earlier, per §2):**
1. Tag tree: triggered keywords inherit trigger-family parents.
2. Engine: whether keywords project into the trigger axis for T0–T2
   keyword-kinship scoring — separate engine ruling, needs its own
   ratification, mirrors b1-Q1.

## 5. Three-source architecture (ratified framing)

- **CR (top-down):** the mechanism skeleton — ability classes, trigger
  families, replacement effects, cost taxonomy (601.2). Extracted
  mechanically, versioned to CR date. Cannot name JOBS (the CR has no
  concept of "stax"; Grand Abolisher ↔ Defense Grid kinship is invisible
  to it).
- **Foundry (bottom-up):** evidence-anchored leaves with oracle quotes and
  Captain ratification. The only source of authored truth. All v0.x
  codebook axes survive as leaves regardless of schema-pass structure.
- **Community taxonomies (outside-in), Scryfall Oracle Tags already in the
  pipeline bulk data:** RECALL AUDITOR ONLY, never authority. At schema
  pass, diff their taxonomy against ours: any community tag whose members
  the engine scatters across unrelated axes = candidate blind spot (an
  unnamed job). Also usable as a measurable convergence TEST SET ("does
  the engine's Defense Grid neighborhood contain the community's stax
  members?") without any unverified tag entering the codebook. Rationale
  for never-authority: no evidence anchoring, no versioning/determinism,
  uneven coverage; standing "never trust datadumps" ruling applies.
- LLM strategy knowledge (this model or research agents): same lane as
  community tags — generates candidates, audits gaps; limits are recall
  (not verification), staleness, nondeterminism. The foundry lane turns
  candidates into truth. This division is the design, not a workaround.

## 6. CR-ontology blind-spot audit (parked, schema pass)

Named step-back session: walk CR 601–616 and 700–702 against the codebook,
one dimension at a time, emitting candidates into the parent-tree ledger.
Known rows already identified:
1. **Keyword actions (CR 701):** investigate = create a Clue; predefined
   tokens (Treasure/Clue/Food/Blood) are all sac-ability artifact tokens —
   `creates-treasure-token` has unlinked cousins.
2. **Replacement vs triggered:** "would ... instead / as ... enters" vs
   "when/whenever" — same job, different machinery, systematically
   different wording. Pure Tier 3 territory.
3. **Cost-side vs effect-side** actions sharing a verb (sac as cost vs
   forced sac as effect) — now partially ratified via the D6 reversal
   (§7).

## 7. Batch-4 ratification record (as translated into §10 directives)

- D1: activated-tap-target-creature KEEP, remove 9 members, NO SPLIT.
  (Captain initially annotated a split into `activated-ability` +
  `tap-target-creature`; withdrawn as contradicting §3. `rule:activated-
  ability` at corpus scale is a CR-skeleton bucket, derived free, near-zero
  similarity signal.)
- D2: Klothys and Item Crate member removals ratified (Item Crate →
  direct-damage-any-target).
- D3: Breya adds targeted-planeswalker-damage per M8.
- D4: merges ratified incl. STANDING RULE: any grants-temporary-<keyword>
  candidate folds into temporary-keyword-grant.
- D5: two pump merges DEFERRED pending Captain review of
  `review/batch-4-deferred-examples.md` (members + quotes; file only,
  never console).
- **D6: PRECEDENT REVERSAL.** b2/b3 "cost-shape riders are not axes" is
  OVERTURNED by Captain: how a card pays for an effect IS an axis.
  additional-cost-sacrifice-permanent and additional-cost-discard-a-card
  flip KILL → KEEP as wide-net cost axes. Granular facet children
  (object class sacrificed; one-shot vs repeatable outlet) go to the
  ledger for schema pass. Punch item (not executed): evaluate resurrecting
  b2/b3-killed cost axes. Beta's batch-5+ instructions must reflect the
  reversal.
- D7: all other verdicts stand.
- Ledger additions (Captain-attributed): keyword-grant facet scheme
  (which keyword × duration [EOT / next turn / static-anthem / counter] ×
  scope [target / up-to-N / all-yours / all] × delivery trigger). NOTE:
  keyword-identity facets (`gives-hexproof`) collide with b1-Q1's
  keyword-grant kill = open tension T1; schema pass reconciles, never
  silently resolve, do not author now.
- Bug: foundry_common.py build_review_card_record() reads root
  oracle_text, blank for 21 multi-face cards; DET fix = concatenate
  card_faces[*].oracle_text when root empty. Captain note attached:
  consider a sanctioned oracle-text injection path — surfacing back-face
  cards fast is a product requirement for every tool on this engine.
- Beta spec change (batch 5+): TRIAGE doc gains a MEMBER ROSTER section —
  every axis, full member NAMES (names only, no oracle text) — so Captain
  audits membership, not just logic. Pull-based quote lookup via Code
  ("show members + quotes for rule:X") for anything a name makes him
  squint at.

## 8. Captain's verdict-pen guide (standing, batches 5+)

Vocabulary: axis/tag = codebook entry; member = card assigned; compound =
trigger+effect for ONE ability; atomic = single ingredient; parent = broad
derived umbrella (job); leaf = authored specific tag (mechanism); derived
= computed, never authored; most-specific scoring = deepest shared tag
counts, broad tags are browse-only.

CORRECT these (when evidence is in front of you — section-0 callouts, the
override sample, roster names that smell wrong; membership audit is BETA's
full-pass job, yours is spot-fire):
1. Wrong members (quote doesn't match axis definition).
2. Crossed wires (tag pairs wrong trigger with wrong effect).
3. Grab-bags (members don't share the conjunction — "don't absorb,
   expand").
4. Missing multi-tags (mixed object classes get every applicable axis —
   M8).
5. Cost qualifiers ("Free must be Free").

LEAVE ALONE:
1. Accurate compounds — never split into atomics; broad versions arrive
   derived.
2. Proposed atomic-union axes (bare `loot`, `token-creation`) — verdict
   KILL, log as parent candidate.
3. Effect-only names on instants/sorceries (burst-draw) — "on resolution"
   IS the trigger; they become direct members of derived parents.
4. Names you dislike — log renames, don't execute (stun-counter-style
   exceptions only when Captain explicitly directs).
5. Small n — kill for fake, never for rare.

Optional gravy: one-line "parent candidate: X" notes when a suffix family
forms.

## 9. STANDING TASK for the next chat session (batch-5 review check)

When Captain brings batch-5 annotations (or any future TRIAGE doc), the
session MUST check his verdicts against this addendum before translation
into §10, specifically:
1. Any verdict that decomposes an accurate compound into atomics →
   flag against §3, confirm intent before parsing (this happened in
   batch 4 and was withdrawn).
2. Any verdict contradicting a ratified ruling or standing precedent →
   flag as either error or EXPLICIT REVERSAL; reversals get logged in the
   rulings registry, never parsed silently (D6 is the model case).
3. Crossed trigger/effect pairs in Captain-authored tag names.
4. New keyword-related verdicts → check against keyword-buckets.json once
   it exists, and against T1.
5. Anything touching structure/parents/facets → ledger, not mid-flight
   authoring, unless Captain explicitly overrides sequencing.
Translation judgment calls are LEGAL but must be surfaced to Captain in
the reply, never silent (model: the D6/gives-hexproof translations).

## 10. Open punch list delta (adds to addendum-2 §7)

1. DONE: batch 4 emitted (codebook v0.4), batch 5 fully triaged +
   ratified via TRIAGE-BATCH-5.md §10 (D1-D18) + emitted (codebook v0.5,
   241 active axes). Batch 6 assembled + Stage 1B prepared, cost estimate
   $22.55 intro — STOPPED for Captain's go-ahead before submitting.
2. Captain reviewed batch-4-deferred-examples.md → both pump merges
   resolved as part of batch-5's D-series (see TRIAGE-BATCH-5.md §10).
3. **Bug found + fixed this session:** foundry_reconcile.py's RENAME
   branch built the new slug's member_oracle_ids from ONLY the triggering
   batch's own staged members, never unioning the old slug's pre-existing
   member history — silently dropping prior-batch membership on every
   rename. Confirmed live: batch-3's stun-counter rename and all 6 of
   batch-5's D14 renames were affected (e.g. rule:create-token-creature
   showed n=22 pre-fix, the correct historical total is n=163). Fixed and
   the ENTIRE codebook.json was rebuilt from scratch by replaying batches
   1→5 through the fixed reconciler using each batch's already-adapted
   foundry-decisions-v1.json file — this is now the verified-correct,
   fully reproducible state (v0.5, 241 active axes). A residual 1-member
   discrepancy on rule:enters-tapped between the freshly-replayed v0.4
   checkpoint and the codebook.json inherited at this session's start
   was noted but not chased further (unrelated to the rename bug,
   pre-existing drift of unknown origin, immaterial at this scale).
4. Keyword-bucket extraction DET job (§2 step 2) — build BEFORE full
   corpus. Then SYNTH prompt update (§2 step 3). NOT started — batch-6's
   SYNTH prompt update only applied batch-5's own feedback (recently-
   killed appendix, restriction-wording/cost-vs-effect/effect-suffix
   checks), not keyword-bucket awareness, per the ratified sequencing.
5. **Codebook condensation is now urgent, not just flagged** — Stage 1B
   prep cost trend: $8.05 (b2) → $12.34 (b3) → $17.90 (b4→b5 prep) →
   $22.55 (b5→b6 prep), all at ~1,200 cards, purely from codebook growth
   (134 → 241 active axes) plus this batch's new recently-killed-slugs
   block (75 slugs, bare list, no reasons, already minimized for cost).
6. Ledger entries from §7 (batch-4) — done in the batch-4 session per its
   own commit. Batch-5's ledger entries (D10's ratified depth-3 etb/
   leaves-battlefield restructuring, D16's new proposed-parent entries)
   are in mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md.
7. Schema-pass agenda now includes: S1–S7, T1, keyword integrations (§4),
   blind-spot audit (§6), community-tag convergence check (§5), facet
   schemes (§7), derived effect-parents (§3), naming audit
   (suffix-functional), PLUS rule:etb-create-token's 46 pre-existing
   (batches 1-4) unclassified members and
   rule:leaves-battlefield-trigger-create-token's 2 (batch-5's own)
   unclassified direct members — flagged in decisions/batch-5.json's
   punch_list, not executed this session (see TRIAGE-BATCH-5.md §10 D10).
8. Full-corpus test-case expectation (D16): Plunge into Darkness was
   confirmed corpus-valid and not yet reviewed — pulled forward into
   batch 6's hand-picks for rule:library-dig-to-hand rather than left
   waiting for the full pass.
9. Everything still live from addendum-2 §7 (Kiki/Helm verification,
   equivalence map, playbook Steps 5–9, etc.).

## 11. Quick starts

**Fresh Fable 5 chat:** paste MASTER-HANDOFF.md + ADDENDUM-2 + this. State
the topic. Demand verified numbers, not recall. If reviewing a TRIAGE doc,
run the §9 checklist.

**Claude Code:** "Read docs/MASTER-HANDOFF.md, docs/MASTER-HANDOFF-
ADDENDUM-2.md, docs/MASTER-HANDOFF-ADDENDUM-3.md, and <task doc>; execute
<task>. Continue through all phases — only stop on genuine ambiguity, a
failed gate, or an unspecified decision."
