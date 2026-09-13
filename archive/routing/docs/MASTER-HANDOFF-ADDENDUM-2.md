# MTJAWNNY T3 ARC — MASTER HANDOFF ADDENDUM 2 (2026-07-18 → 07-20 sessions)

Purpose: paste this + MASTER-HANDOFF.md into a fresh chat (Fable 5 or
Claude Code) and be current immediately. This addendum covers the
SUP-triage arc: batches 1–3, the lean loop, the parent-tree layer.
Everything here was ratified or verified in-session, not recalled.
Where this conflicts with MASTER-HANDOFF.md, this addendum is newer and
governs.

---

## 1. What changed since the original handoff (one paragraph)

The foundry bootstrap is live and three batches deep. Review method
changed by ratified protocol: Captain no longer clicks 1,145 rows —
a SUP-class model performs full-pass triage and Captain ratifies at
proposal level (docs/SUP-TRIAGE-PROTOCOL.md governs). The loop runs
inside Claude Code via three slash commands with per-command model
pinning. Codebook is at v0.2 (134 active axes) with batch-3 review in
progress. A parent-tag layer ("tags within tags") was designed and its
candidates ledger seeded — it is the schema pass, deferred until after
the full-corpus pass. Chat (Fable 5) is reserved for rulings, audits,
step-backs, and idea work; Claude Code does everything that touches
files.

## 2. The lean loop (how work happens now)

Per batch N: `/triage-alpha N` (Haiku, DET: consolidate + enrich + emit
~60KB digest) → `/triage-beta N` (Fable 5, SUP: reads digest, writes
docs/TRIAGE-BATCH-N.md with prefilled verdicts, ≤8 questions, fixed-seed
30-row override sample, seed 20260718+N) → Captain annotates the .md
(edit VERDICT lines, fill RULE blanks; free-prose JAWNNY-VERDICT
annotations are legal but get translated into a §10 "CAPTAIN
RATIFICATION — PARSED DIRECTIVES" section, which is authoritative for
parsing; prose stays as audit trail) → `/triage-emit N` (Haiku, DET:
parse → decisions/batch-N.json → reconcile → codebook vN → assemble
batch N+1 → live-priced cost estimate → STOP for go-ahead).

Standing session rules baked into commands + CLAUDE.md: scope guards
(emit never re-runs alpha's work; state-check printed first), transcript
hygiene (never print raw oracle text/SYNTH blobs to console — tripped an
AUP false-positive once; print counts/slugs/paths only), paper-over-
Alchemy everywhere, halt-loudly, determinism ×2, all-faces scanning,
oracle-text-only evidence quotes.

## 3. Batch history + convergence record

**Batch 1** (500 cards): 105 axes triaged → 69-axis codebook v0.1.
30 kills (14 bare-keyword, 3 keyword-ledger, 7 riders/templating,
4 grab-bags, 2 generic-DF), 12 merges → 4 targets, 10 keyword-grant
axes killed as engine-redundant (granted_keyword dimension — ratified
Q1), 11 OTHER-lane promotions (rhystic-tax, restricts-opponent-search,
cost-reduction, free-cast(+if-commander), mass-graveyard-exile,
graveyard-to-exile-replacement, x-scales, limits-card-draws,
taxes-opponent-spell-cost; P1 cast-timing folded into shipped
turn-scoped derivation, not duplicated). 3 captain-authored
(exile-until-source-leaves, alt-win-empty-library, targets-a-player).
Override spot-check: 0 reversals / 90. Ratified via chat (predates the
annotation convention — decisions/batch-1.json IS the record; the .md
has no annotations by design).

**Batch 2** (1,200 cards, $8.05): 149 axes → codebook v0.2, 134 active.
Two-lane codebook labeling debuted: 512/2,122 instances resolved to
codebook slugs with 0 anomalies. Captain override rate 10/145 (~6.9%) —
reversal cluster ratified into standing SUP standards: **"don't absorb,
expand"** (sibling axes + parent scheme over absorption when mechanics
differ by object class/vector; absorption OK when one vector owns the
rule, e.g. mana), **"Free must be Free"** (cost qualifiers in names are
binding), copy ≠ cast, joke/acorn-only families get no axis. 6
captain-authored axes added (grants-ability-at-threshold-self/-board,
plus1-counters-matter, targeted-player/planeswalker/battle-damage —
last two derivation-filled, no hand examples). Consolidate bug found+
fixed: single-card clusters masquerading as 2-card families (distinct
oracle_id count now enforced). Emit found+patched: reconcile was
silently dropping ALL OTHER-lane promotions.

**Batch 4** (1,200 cards, $12.34 submission; 166 axes triaged, 1,016 cards
review-covered): codebook v0.3 -> v0.4, 203 active axes. Captain ratified
via TRIAGE-BATCH-4.md section 10 (D1-D7). Override rate 4/165 confident
calls (~2.4%) -- continuing the decline (b1 0% -> b2 6.9% -> b3 ~3.2% ->
b4 ~2.4%), spot-check 0/30. Key rulings: activated-tap-target-creature kept
with 9 member removals (activated-vs-triggered / cost-vs-effect conflation,
new failure pattern -- SYNTH prompt patched); 4 merges (energy, hexproof,
two exile-replacement candidates including Q1); M8 mixed-target addition
(Breya -> both damage axes); **D5 introduces a new codebook status,
`deferred`** (two pump-axis merges held pending more evidence, written to
batch-4-deferred-examples.md); **D6 overturns the b2/b3 cost-shape-riders-
are-not-axes precedent** -- cost axes are legitimate wide-net axes now,
additional-cost-sacrifice-permanent/-discard-a-card flip KILL->KEEP.
Zero OTHER-lane promotions, zero keyword-ledger additions (no kills this
batch). Batch 5 assembled (1,200 cards, thin/zero-member axis confirmation
targeting) and Stage 1B prepared: cost estimate $17.90 intro / $26.85
standard -- **the codebook-growth cost trend flagged in section 6/7#3 is
accelerating** ($8.05 b2 -> $12.34 b3 -> $17.90 b4->b5 prep, all at ~1,200
cards, purely from the embedded codebook growing 134 -> 203 active axes).
STOPPED for Captain's go-ahead before submitting batch 5.

**Batch 3** (1,200 cards, $12.34, submitted): review COMPLETE as of a prior
session (codebook v0.3, batches_reconciled [1,2,3] were already the
starting state when the batch-4 session below began) -- this paragraph was
stale ("IN PROGRESS") in earlier revisions of this addendum; corrected
here. Q2/Q3 answered, ratified via TRIAGE-BATCH-3.md's prose annotations
(no section 10 needed -- batch 3 predates that requirement beyond batch
1's seam).
Captain's annotations so far: Q1 answered (stun-counter-lockdown
RENAMED rule:stun-counter, kept separate from
prevents-target-untap-next-step, both under new parent rule:lockdown);
Q2 (energy = archetype vs ledger) and Q3 (perpetual, Alchemy-only)
UNANSWERED. §1 prose contains major parent-scheme rulings (see §5) +
cantrip predicate refinement #3: the draw must occur upon RESOLUTION
(spell effect, ETB, or immediate) — activated {T} abilities excluded
(summoning sickness). Needs the §10 parsed-directives build once Q2/Q3
land. Cost note: $8.05→$12.34 at identical card count = embedded-
codebook prompt growth; punch-listed to condense before full-corpus
pass.

## 4. Ratified rulings registry (this arc, adds to original §3)

| Ruling | Statement |
|---|---|
| SUP-triage protocol | full-pass triage + proposal-level ratification replaces row review |
| Override metric | primary convergence signal = Captain reversals / confident calls |
| §10 directives | parsed-directives section is authoritative over prose annotations |
| Q1 (b1) | pure keyword-grant axes engine-redundant → killed; grants-unblockable exempt (not a keyword) |
| Cantrip | ANY card type, MV≤2, draw upon resolution (spell/ETB/immediate; no {T} abilities) |
| Don't absorb, expand | b2 standing SUP standard (see §3 batch 2) |
| Free must be Free | name cost-qualifiers are binding |
| Damage targets | per-object-class axes; mixed targets = multiple tags, never combo tags (closed system) |
| Parents | children = mechanism, parents = job; parents derived (union of children + direct members); most-specific-node scoring; depth ratified per family (etb = 3); parent names are user-facing vocabulary |
| No midflight renames | naming standardization is a FINAL AUDIT punch item; renames logged, not executed (exceptions only when Captain directs, e.g. stun-counter) |
| Legality display-layer | reaffirmed: joke/Alchemy cards stay in corpus; they just get no axis when a family is joke-only |
| Transcript hygiene | no raw card text to console in any foundry session |
| Cost-shape precedent reversal (b4 D6) | OVERTURNS the b2/b3 "cost-shape riders are not axes" precedent. Cost-side axes (e.g. rule:additional-cost-sacrifice-permanent, rule:additional-cost-discard-a-card) are legitimate wide-net axes, not automatic kills. b2/b3-killed cost-shape axes (rule:sacrifice-creature-as-additional-cost, rule:sacrifice-as-additional-cost, rule:self-sacrifice-divided-damage) are punch-listed for possible resurrection at reconcile/schema pass, not auto-restored. Binds batch-5 beta onward — see docs/SUP-TRIAGE-PROTOCOL.md and .claude/commands/triage-beta.md, updated same commit set. |
| Deferred verdict (b4 D5) | New codebook status alongside active/killed/merged/renamed: `deferred` — axis is recorded with its members but not offered to SYNTH as an active codebook slug and not merged, pending a specific future Captain ruling. First use: the two pump-axis merge candidates held in batch 4 (see experiments/out/foundry/review/batch-4-deferred-examples.md). |

## 5. The parent-tree layer (docs/PARENT-TREE-CANDIDATES.md)

The schema pass made concrete. Ledger seeded with: ratified lockdown
family; five trigger-family parents (etb [depth-3:
etb → etb-create-token → etb-create-token-creature], attack-trigger,
cast-trigger [requires "when you cast" verbiage — never an ETB],
combat-damage-triggers, death-trigger); N-scales-with-N-count scheme;
damage-target family; mass-N-N lattice (mass-<type>-<disposal>) with
the counts-toward implication problem (Ruinous Ultimatum →
mass-nonland-destruction counts toward per-type siblings — structural
ruling S5, needs thought); ~11 backlogged proposed parents from b1–b2;
new standalone tags Captain named: number-of-opponents-matter,
minus1-counters-matter. Structural rulings S1–S7 pending at schema pass
(derived parents, most-specific scoring, per-family depth, multi-parent
edges, implication edges, parent-name audit, family-tree-evidence
validation per candidate). Open tension T1: Company Commander example
reintroduces keyword-grant leaves (grant-deathtouch-board) vs b1-Q1's
engine-redundancy kill — schema pass reconciles; do not silently
resolve. Sequencing: bootstrap converges → full-corpus pass → SCHEMA
PASS → display build.

## 6. Money + scale posture

Captain-approved: ~$100+ for the eventual full-corpus Source B pass
(38,233 cards), gated behind convergence metrics + explicit trigger.
Thoroughness over speed. Watch embedded-codebook prompt growth (now the
dominant cost driver); condense codebook representation (slugs +
one-liners) before the big pass.

## 7. Open punch list (supersedes original §7 where overlapping)

1. DONE (batch 4 session): Batch 3 ratified, §10-equivalent applied via
   prose annotations, /triage-emit 3 run (codebook v0.3). Batch 4 fully
   triaged, ratified via TRIAGE-BATCH-4.md section 10, /triage-emit 4 run
   (codebook v0.4). Batch 5 assembled + Stage 1B prepared, cost estimate
   $17.90 intro -- STOPPED for Captain's go-ahead before submitting.
2. Override rate trend, updated: b1 0% -> b2 6.9% -> b3 ~3.2% -> b4 ~2.4%,
   declining two batches running under "don't absorb, expand." Spec metric
   (OTHER-lane rate) stays flat ~62-66% every batch -- expected/method-
   inflated per protocol, not a signal.
3. **Condense embedded codebook before full-corpus pass -- now urgent, not
   just flagged.** Batch-5 prep priced at $17.90 (intro) at the same
   ~1,200-card size that cost $8.05 (b2) and $12.34 (b3), purely from
   codebook growth (134 -> 203 active axes). At this growth rate the
   per-batch cost will exceed the full-corpus budget's headroom well
   before convergence. Not actioned this session -- next session should
   treat this as blocking, not background.
4. D5 follow-up (NEW, batch 4): Captain rules on
   rule:activated-pump-with-self-damage-cost and
   rule:activated-self-toughness-pump (merge into
   rule:mana-activated-pump-self, or keep standalone) using
   experiments/out/foundry/review/batch-4-deferred-examples.md.
5. D6 follow-up (NEW, batch 4): evaluate resurrecting the b2/b3-killed
   cost-shape axes (rule:sacrifice-creature-as-additional-cost,
   rule:sacrifice-as-additional-cost, rule:self-sacrifice-divided-damage)
   now that the precedent is overturned -- not automatic, Captain must
   call it.
6. DET fix (batch 4): foundry_common.py's build_review_card_record() needed
   an all-faces oracle_text fallback (21/1200 batch-4 cards affected in
   review/batch-4.json). Found already correctly implemented but
   uncommitted at the start of the batch-4 emit session -- committed as
   part of it (benefits batch 5's Stage 1B prompts going forward; does not
   retroactively fix review/batch-4.json itself). Captain flagged a
   possible sanctioned oracle-text injection path for multi-face cards as
   a further product requirement, beyond the DET fix -- still open.
7. Schema pass prep: keep PARENT-TREE-CANDIDATES.md appended by beta/emit
   (directives already in both commands) -- batch 4 added the
   keyword-grant facet scheme, cost-shape facet scheme, and delivery-facet
   note.
8. Final naming audit (parents ruthless, children lenient).
9. Kiki/Helm granted_keyword verification (b1 Q1 carve-out) still open.
10. Original handoff items still live: family tree rulings vs
    FAMILY-TREE-EVIDENCE.md; duplicate-oracle-rows trim; equivalence map;
    GRANT_SIZE_CEILING/F1 at Phase B; playbook Steps 5–9 (viewer JSONs
    still stale until Step 7).

## 8. Quick starts

**Fresh Fable 5 chat (idea work / rulings):** paste MASTER-HANDOFF.md +
this addendum. State the topic. Public repos are clonable into the chat
container for verification (git clone works; gitignored docs/ and
experiments/out/ are NOT in clones — upload those or read via Claude
Code). Demand verified numbers, not recall.

**Claude Code:** the loop commands self-orient (CLAUDE.md + protocol).
For non-loop work: "Read docs/MASTER-HANDOFF.md, MASTER-HANDOFF-ADDENDUM-2.md,
and <task doc>; execute <task>. Continue through all phases — only stop
on genuine ambiguity, a failed gate, or an unspecified decision."
