# CDR-09 §12a rename walk — EXECUTED, 2026-08-02

**Status: COMPLETE.** 16 renames applied, name-only.

| | before | after |
|---|---|---|
| codebook sha256 | `61af1a1d7f81504f422feb4d…` | `d0b1183fc155f13e7b1ae025…` |
| axes | 455 | 471 (+16 tombstones) |
| **active** | **307** | **307** (unchanged — name-only) |
| members (all statuses) | 7,699 | 7,864 (tombstones retain members) |
| lint | clean | clean |
| sweep blocking | 6 | **6** (same six) |
| counter-bearing active axes | 33 (16 non-conforming) | 33 (**0 non-conforming**) |

Scripts: `experiments/foundry_cdr09_derive.py` (derivation, writes nothing),
`experiments/foundry_cdr09_walk.py` (executor).
Backup: `backups/codebook.v0.7.pre-cdr09-rename-walk.20260802-132352.json`,
verified by readback (hash-identical **and** parsed deep-equal, 455 records).

---

## 1. Precondition 4 initially failed — and the failure was mine

First derivation returned **19** non-conforming axes, not 16, plus one whose
sense could not be derived from its definition. On the handoff's instruction
("if the live set disagrees with §12a, halt") the walk was stopped and the
disagreement written up.

**Captain directed a read of the prior rulings before anything was decided.
That read overturned three of the four findings.** All three were re-raising
questions already ratified, by a derivation that only knew about §8a:

| axis | my claim | the ruling I had missed |
|---|---|---|
| `rule:create-token-with-x-counters` | rename to `-x-plus1-counters` | **grammar §7 names this slug verbatim** as the ratified answer to b7 line-84 ("X scales counters ON one created token"). Renaming it would have broken the ruling that chose it. |
| `rule:cost-reduction-scales-with-own-counters` | rename, `own` isn't a binder | **`own-counters` is §7 closed stat vocabulary.** This exact question was already asked at the walk-ratification pass as the `bare_counter_noun` flag and **RESOLVED AS A PASS** — "already uses the correct connective and needs no rename." I re-raised a settled question. |
| `rule:etb-with-negative-counters` | rename to `etb-with-minus1-counters` | **TRIAGE-BATCH-5 ratified counter polarity (+1/+1 vs -1/-1) as a PARAMETER, not a distinct axis.** Typing the slug `minus1-` would encode precisely the distinction that ruling rejects. |

And the fourth, `rule:draw-second-card-trigger-plus1-counter`, was not
undecidable at all — **batch-5 D12 renamed it FROM `-token` TO `-plus1-counter`
for exactly the reason I flagged**: "the old slug's effect suffix did not match
its only member." The name is Captain-ratified. What misled the classifier is
that the *definition text* was never updated from the token era.

With those four ratifications encoded (`RATIFIED_NAMES` / `RATIFIED_SENSE` /
§7 scaling-stat binding, each carrying its citation in the source), the
derivation returns **16 non-conforming, 17 conforming — set-identical to §12a**.
Verified by set comparison, not by count.

**§12a was right. The arithmetic gate holds: 16 + 17 = 33.**

### The lesson

The derivation was written against §8a alone, so every slug governed by a
*different* ratified law read as a defect. Encoding one law and calling the
result a finding manufactures false positives that look exactly like real ones —
and two of these three would have destroyed ratified names had the walk
proceeded on my recommendation. **A conformance check is only as good as the
set of rulings it knows about.**

## 2. The 16 renames as applied

Verb-side (3) and `any-` (3) targets are stated verbatim in §12a. The 10
noun-side targets are **derived** — §12a names the axes and the transform
("gain `plus1-`") but not the strings — by inserting `plus1-` immediately left
of the counter token. That insertion point is not a guess: grammar §8a
correction 2 cites the post-walk name
`cast-trigger-self-plus1-counter-noncreature-spell` verbatim, and the derived
target matches it exactly.

| from | to | mem |
|---|---|--:|
| `rule:activated-counter-target-spell` | `rule:activated-counters-target-spell` | 2 |
| `rule:activated-tax-counter-unless-pays` | `rule:activated-counters-target-spell-unless-pays` | 2 |
| `rule:tax-or-counter-spell` | `rule:counters-spell-unless-pays` | 2 |
| `rule:activated-counter-transfer-from-other-creature` | `rule:activated-plus1-counter-transfer-from-other-creature` | 2 |
| `rule:attack-trigger-buff-other-attacker-counters` | `rule:attack-trigger-buff-other-attacker-plus1-counters` | 2 |
| `rule:attack-trigger-self-counter-growth` | `rule:attack-trigger-self-plus1-counter-growth` | 7 |
| `rule:cast-trigger-self-counter-noncreature-spell` | `rule:cast-trigger-self-plus1-counter-noncreature-spell` | 2 |
| `rule:death-trigger-counter-transfer` | `rule:death-trigger-plus1-counter-transfer` | 4 |
| `rule:draw-trigger-self-counter-growth` | `rule:draw-trigger-self-plus1-counter-growth` | 5 |
| `rule:etb-counter-on-other-creature` | `rule:etb-plus1-counter-on-other-creature` | 42 |
| `rule:lifegain-triggered-counter` | `rule:lifegain-triggered-plus1-counter` | 8 |
| `rule:mass-counter-distribution` | `rule:mass-plus1-counter-distribution` | 41 |
| `rule:self-counter-growth` | `rule:self-plus1-counter-growth` | 13 |
| `rule:doubles-counter-placement` | `rule:doubles-any-counter-placement` | 11 |
| `rule:cleanup-counters-on-leaving-battlefield` | `rule:cleanup-any-counters-on-leaving-battlefield` | 2 |
| `rule:counter-removal-as-activation-cost` | `rule:any-counter-removal-as-activation-cost` | 20 |

Gates run by the executor before installing anything: live non-conforming set
**set-identical** to §12a's 16; every target itself passes §8a; determinism ×2
byte-identical (3,473,239 bytes). Then `write_codebook_atomic` re-linted the
temp, verified re-serialization reproduced the written bytes, and checked the
post-rename sha.

## 3. Sweep: blocking held at 6, advisory +3 — and the +3 are the point

The same six blockers, none new. Advisory 190 → 193, all `name-subsumption`,
five findings touching walk targets:

- `counters-target-spell` / `counters-spell-unless-pays` /
  `activated-counters-target-spell(-unless-pays)` now share a stem. **This is
  the near-duplicate cluster §12a itself flagged** ("differing only in
  delivery — resolve together, see CDR-05"). The old inconsistent names hid it;
  the walk made it mechanically detectable. CDR-05's business, not a regression.
- `self-plus1-counter-growth` < `attack-trigger-…` / `draw-trigger-…` — the
  correct delivery-prefixed family shape, now visible for the same reason.

## 4. What this unblocks, and what it does not

**Unblocked:** ADD-08 / Tier-0 bug 4 (the adjacency rule misfiled 17 of 33
counter axes on the old names; expected 4 now, dropping to 0 once the two §8a
corrections are implemented). CDR-13's Homograph Form Ledger — its "zero new
churn" claim now rests on renames that exist.

**Not touched by the walk, both pre-existing and already tracked:**

1. **`rule:draw-second-card-trigger-plus1-counter` — stale definition and
   membership drift.** The definition still reads "producing a creature token
   as a reward" from before batch-5 D12 renamed the axis. Worse, it now holds
   4 members that split two ways on delivery **and** two ways on payoff:

   | member evidence (human-class quotes) | delivery | payoff |
   |---|---|---|
   | "Whenever you draw your second card each turn, put a +1/+1 counter on this creature." | draw-second | counter |
   | "When this creature enters, if it was the second spell you cast this turn, put a +1/+1 counter on target creature." | **etb / cast-second** | counter |
   | "Whenever you cast your second spell each turn, draw a card, then create a 0/3 white Wall creature token…" | **cast-second** | **token** |
   | "Whenever you draw your second card each turn, create a 1/1 colorless Thopter artifact creature token with flying." | draw-second | **token** |

   Only one matches the slug. D12 already ledgers the target scheme (the
   `cast-second-spell-trigger` mirror family and the `-token` sibling), and
   `B-CONSOLIDATION-REAUDIT-PACKET.md:169` already carries this as an **R7
   report row** — "the node's payoff sense and the rename target's sense
   differ." A definition fix plus a membership split, neither in walk scope.

2. **`rule:etb-with-negative-counters` — contested existence, not a name.**
   Batch-5 ruled MERGE into `etb-with-counters` (polarity is a parameter);
   batches 6 and 7 both KEPT it; the 2026-08-01 Captain ruling cleared its
   stale `merged_into` and declared it live in its own right. That is a
   question about whether the axis exists, and the walk was right to leave the
   name alone either way.

## 5. Standing-discipline note

The handoff's "measure, never recall" held again, in both directions: §12a's
numbers were correct when measured, and my three "extra findings" evaporated
when measured against the full ruling set rather than one section of it.
