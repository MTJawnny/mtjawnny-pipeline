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

**Batch 3** (1,200 cards, $12.34, submitted): review IN PROGRESS.
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

1. Batch 3: Captain answers Q2/Q3 + confirms T1 stance later; build §10
   directives; run /triage-emit 3.
2. Batch 4 assembly targets follow from 3's feedback; override rate
   trend is the needle (b1: 0%, b2: 6.9%, b3: TBD with "don't absorb,
   expand" now binding on beta).
3. Condense embedded codebook before full-corpus pass.
4. Schema pass prep: keep PARENT-TREE-CANDIDATES.md appended by beta/emit
   (directives already in both commands).
5. Final naming audit (parents ruthless, children lenient).
6. Kiki/Helm granted_keyword verification (b1 Q1 carve-out) still open.
7. Original handoff items still live: family tree rulings vs
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
