# T3 Buildout — pick up at Step 5

**Paste this to start the next session** (run from `mtjawnny.github.io`,
same as this session — the pipeline work happens cross-repo in
`~/Projects/mtjawnny-pipeline`):

> Read `docs/T3-BUILDOUT-PLAYBOOK.md` and execute Step 5. Read
> `docs/T3-BUILDOUT-STEP5-HANDOFF.md` first for where Steps 1-4 landed.
> Continue through all phases — only stop on genuine ambiguity, a failed
> gate, or an unspecified decision.

## Where things stand

Playbook: `docs/T3-BUILDOUT-PLAYBOOK.md` (Steps 1-9, one step per fresh
session, per its own header).

- **Steps 1-3 — done, committed.** See `docs/T3-BUILDOUT-STEP4-HANDOFF.md`
  for full detail (Step 1 superseded/committed `c53b30d`; Step 2 Phase A
  committed `b5d5e3a`; Step 3's additive derived-score term + Lesson 3's
  `DERIVED_QUALIFY_DF_CEILING=172` committed `1a310b5`, Captain's
  go-ahead 2026-07-17, not pushed).

- **Step 4 — done, NOT a code change, nothing to commit/push.** Task per
  the playbook: produce `docs/FAMILY-TREE-EVIDENCE.md`, evidence only, no
  ratified tree (Captain writes that himself). Delivered.

  **What landed:**
  - A throwaway measurement script, `experiments/measure/
    family_tree_evidence.py` (mtjawnny-pipeline repo, gitignored output
    under `experiments/out/measurement/`, never wired into
    `tier_engine.py` scoring), implementing all eight v1 derivation
    patterns from `DERIVED-TAG-LAYER-SPEC.md` as regexes over
    `composed_full_text` — corpus DF/idf + fixed-seed sample per pattern,
    same ritual as the shipped `rule:turn-scoped`.
  - Corpus co-occurrence + conditional probability computed pairwise
    across all 12 measured derived tags (the eight concepts, with
    restricts-cast/restricts-opponent-cast and uncounterable-self/grants-
    uncounterable each split into two, per Lesson 1's scope-split and the
    spec's self/granted split).
  - Full Scryfall Tagger cross-reference: which Tagger tags blanket which
    derived populations, plus a dedicated Tagger↔rule: redundancy table
    (13 watched Tagger tags × all 12 derived tags) — the appended Step 3
    requirement.
  - `docs/FAMILY-TREE-EVIDENCE.md` written: 5 required families
    (cast-interference, resolution-protection, activation-interference,
    combat-prohibition, tax-effects) plus one the corpus data surfaced and
    the spec's draft didn't anticipate (a 26-card "attack tax" bridge
    between combat-prohibition and tax-effects — Ghostly Prison/
    Propaganda-class). Every family carries a mandatory counter-argument,
    an 8-12-card exemplar panel, a 3-5-card near-miss panel, and one
    single-ruling open question phrased for Captain. No final tree
    proposed.

  **Two real bugs found and fixed auditing the script itself, before
  shipping any numbers** (both documented in the doc's own "Verification"
  section):
  1. A nondeterminism bug — `Counter.most_common()` tie-breaks depended on
     Python's per-process randomized string-hash set iteration order; two
     runs produced different top-8 Tagger-tag orderings among tied counts.
     Fixed with an explicit `(-count, key)` sort; reran twice more,
     confirmed byte-identical.
  2. A classification bug — the first-match-only paragraph scanner
     silently dropped a card's SECOND qualifying sentence, mis-classifying
     Vexing Shusher (the spec's own named uncounterable-self/granted
     example) as self-only instead of both. Added a dedicated
     all-paragraph scanner for that split; verified Vexing Shusher now
     correctly carries both `rule:uncounterable-self` AND
     `rule:grants-uncounterable`.

  **Headline evidence findings** (full detail + citations in the doc
  itself):
  - Raw corpus co-occurrence between the spec's own draft family members
    is consistently near-zero (e.g. `restricts-opponent-cast` ∩
    `uncounterable-self` = 1 card of 58/117; `cost-increase` ∩
    `restricts-opponent-cast` = 0) — every family's basis is functional
    analogy, not a corpus signal, which the doc flags explicitly per the
    anti-laundering guard.
  - Several derived tags are heavily Tagger-redundant:
    `restricts-activation` 91% covered by Tagger's `prevent-activation`;
    `uncounterable-self` 100% covered by `hate-counterspell`;
    `restricts-opponent-cast` 88% covered by `prevent-cast`. None of these
    are treated as disqualifying on their own (per the guard) but are
    flagged as counter-argument material in each family section.
  - `rule:pay-tax` (DF=331) splits cleanly into two functionally different
    populations by Tagger cross-reference: a soft-counterspell majority
    (97% of a 138-card sub-population shares Tagger's `counterspell-soft`)
    and a 26-card attack-tax minority (the Family 4/5 bridge) — flagged as
    a candidate tag-split question, not resolved.
  - A-Teferi, Time Raveler (the Alchemy digital rebalance) was verified
    via the live corpus to carry genuinely different oracle text from
    paper Teferi, Time Raveler — an exact Grand-Abolisher-template match
    the paper card does not share. Confirmed directly, not assumed from
    the similar names.
  - Trinisphere fires NONE of the eight v1 derivations (a mana *floor*,
    textually distinct from "costs N more") — a real, measured gap in the
    cost-increase pattern, flagged as a future-amendment candidate per the
    spec's own "grow the set only when a poke shows a concrete miss" rule,
    not built this session.

  **Files touched**: `experiments/measure/family_tree_evidence.py` (new,
  mtjawnny-pipeline repo — a measurement script, not a scoring change;
  nothing in `tier_engine.py` was touched this session).
  `docs/FAMILY-TREE-EVIDENCE.md` (new, this repo).

  **Nothing to commit in the pipeline repo's tracked history** — the
  measurement script is new but this step's own standing rule set doesn't
  require committing throwaway `experiments/measure/` scripts (compare
  `df_distributions.py`/`phase3_rebalance_shapes.py`, both already
  precedent for uncommitted-vs-committed measurement scripts in that
  directory — if Captain wants this one kept/committed for future re-runs,
  that's a explicit go-ahead question for next session, not assumed here).

## Step 5 — what's next

Per the playbook: Step 5 is "Land v1 derivations (2-3 per session, repeat
until the set is in)" — the FIRST actual code step since Step 3. Read
first: `docs/DERIVED-TAG-LAYER-SPEC.md` (v1 set + ritual), **Captain's
ratified family tree** (does not exist yet — `docs/FAMILY-TREE-EVIDENCE.md`
is evidence only; Step 5 needs Captain to have actually ruled on at least
the families relevant to whichever derivations land first, or proceed
derivation-by-derivation without family umbrellas until the tree is
ratified — this is exactly the kind of ambiguity to surface, not
assume, at the start of that session), Step 3's BEFORE panel snapshot.

Per derivation: implement pattern + BOTH polarities (Lesson 1), print
regex/corpus DF/idf/fixed-seed 20-card sample, run the before/after gate
panel, present sample + panel diff, WAIT for Captain's yes before the
next derivation. Blocking gate: Grand Abolisher's T3 must hold Defense
Grid/Dosan/City of Solitude/Teferi at or above the Step-3-AFTER floor
recorded in `docs/T3-BUILDOUT-STEP4-HANDOFF.md` (Dosan #1/0.74, City of
Solitude #2/0.74, Defense Grid displayed top 10/#4/0.67, Teferi full-list
position 64 or better/0.17 or better) — NOT the pre-Step-3 baseline.
Determinism ×2. Suggested landing order per the playbook: restricts-
opponent-cast(+restricts-cast), cost-increase/cost-reduction,
uncounterable(self/granted split), pay-tax, restricts-activation,
prohibits-attack/block, grants-<keyword> (zero new parsing).

This session's measurement script's regexes are a MEASUREMENT-ONLY
starting point, not pre-ratified production patterns — Step 5 still owes
each derivation its own full ritual (pattern print, corpus DF, fixed-seed
sample, gate panel) before it touches scoring, even though the
measurement script already validated the basic shape of each pattern.

## Standing rules (same as every step)

Halt loudly on ambiguity, verify claims against live code/corpus not
memory, nothing committed without an explicit go-ahead, full gate suite +
determinism ×2 + a snapshot after any ruling-affecting change, new scoring
constants are proposed-then-ratified before implementation. See
`docs/T3-BUILDOUT-PLAYBOOK.md`'s own "Standing rules" section for the
complete list.
