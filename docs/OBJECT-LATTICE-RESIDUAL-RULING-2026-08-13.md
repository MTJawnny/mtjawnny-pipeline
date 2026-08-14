# OBJECT LATTICE — the residual false negatives, and the invariant that finds them

**2026-08-13.** Captain reviewed `experiments/out/foundry/object_lattice_samples.md`
card by card and returned: **lattice grammar yes, target-type decomposition yes,
subtype/conjunctive expansion yes, displayed sample quality strong — current
generated membership set NOT ratifiable.** Blocker named:

> *"valid memberships leaking into the residual bucket… I think the parser is
> stopping at the wrong conceptual layer."*

Confirmed, fixed, and guarded.

**RATIFIED 2026-08-13.** Captain reviewed the repaired output and approved the
targeted bounce / destroy / exile object lattice, accepting the seven recovered
memberships. §7 below records where that ratification LIVES in the repository,
§8 what shipped with it, and §9 what it deliberately does **not** decide.

---

## 1. THE SEVEN, AND THEY ARE ALL REGRESSIONS

Captain named seven cards from a hand-check of high-risk constructions. All
seven reproduce: `classes = []`, every one genuinely residual.

They were **not** original defects. They are regressions introduced by
`e780842` (2026-08-12), the noun-phrase fix:

| card | action | before `e780842` | after |
|---|---|---|---|
| Vengeful Pharaoh | destroy | `creature` | — |
| Venser's Diffusion | bounce | `nonland-permanent` | — |
| Illusionist's Stratagem | exile | `creature` | — |
| Displace | exile | `creature` | — |
| Lukka, Coppercoat Outcast | exile | `creature` | — |
| Suspend Aggression | exile | `nonland-permanent` | — |
| Become Anonymous | exile | `creature` | — |

### 1a. The accountability gap, which is the real finding

**`e780842` removed 170 memberships and verified 83.** Its commit message is
accurate about the 83 — they were read, and they were defective. The other
**87 shipped unread**, and the seven are in there. It fully dropped **113
cards** from an action family.

The standing trap says a `--strict` diff *"scores `None → ratified` as pure
profit."* This is that trap **inverted and unrecorded**: a diff that removes
memberships scores every removal as a fix, and nothing in the repo asked
whether a removal was correct. The routing diff corrects the routing; nobody
corrected the direction of the correction.

---

## 2. THE CAUSE — ONE BLAST RADIUS, THREE BOUNDARIES

Every one of the seven dies at the same line: the CR 110.1 phrase-level `card`
refusal in `classify_clause`. And in every one, the refusal was reading a word
that is **not in the target's noun phrase at all**:

| card | what `target_noun_phrase` returned | the intruding word |
|---|---|---|
| Vengeful Pharaoh | `attacking creature, then put this card ` | `, then` |
| Illusionist's Stratagem · Displace | `creatures you control, then return those cards ` | `, then` |
| Lukka | `creature you control, then reveal cards ` | `, then` |
| Suspend Aggression | `nonland permanent and the top card of your library` | `and <determiner>` |
| Become Anonymous | `nontoken creature you own and the top two cards…` | `and <determiner>` |
| Venser's Diffusion | `nonland permanent or suspended card ` | `or <card arm>` |

Captain's diagnosis of the layer is exactly right: the classifier ran
**action → capture everything after `target` → classify the capture**, where it
needs **action → target expression → target alternatives → object-class
resolution**. Three CR-anchored boundaries implement that.

1. **`, then` ends the instruction — CR 608.2c**, *"the spell or ability's
   controller follows the instructions in the order written."* A later
   instruction's objects are not this target's.
2. **`and <determiner>` starts a SECOND object — CR 601.2c**, *"the player
   announces their choice of an appropriate object or player for each target
   the spell requires."* Only what falls under the printed `target` is a
   target. `and/or` is deliberately **not** matched: no determiner follows, and
   those arms share the one `target`.
3. **CR 110.1 applies at ARM level when the arms are independent, at PHRASE
   level when they share a head.**

## 3. THE DISCRIMINATOR FOR RULE 3, AND WHY IT WAS NEEDED

Rule 3 is the dangerous one, and a naive version of it is a worse defect than
the one it fixes. Measured before implementing: an over-broad arm split flags
**50** residual clauses carrying an arm that resolves to a class. Only 7 are
false negatives. The other **43 are correct residual** — `creature or land
card`, `aura or equipment card`, `artifact or enchantment card` — where `card`
distributes across every arm (Pharika's Mender, already the module's own worked
case). Shipping the naive rule would have traded 7 false negatives for 43
**wrong ratified tokens**, which is the standing trap *"improving recall can
hand out a wrong ratified token"*, and no gap census reports that direction.

**A printed zone ORIGIN is what separates them, and it splits 43/7 with no
overlap.** This is the recorded `put into <DESTINATION> from <ORIGIN>` shape one
family over: `from` is what closes the phrase. Graveyard recursion prints its
origin; Venser's Diffusion does not.

**The origin must be read from the target's own instruction, not the whole
tail.** Lukka prints `exile target creature you control, THEN reveal cards FROM
THE TOP OF YOUR LIBRARY` — that origin belongs to the reveal. Reading the whole
tail scored Lukka as recursion, and it is 1 of the 7.

---

## 4. THE RESIDUAL INVARIANT — Captain's, and why it is not a no-op

Captain: *"After classification, inspect every residual clause again. If a
residual still contains a target branch that resolves… to one of your
recognized battlefield-object classes, HALT."*

Built: `foundry_object_lattice.py --invariant`.

**A guard computed with the classifier's own resolver is a no-op by
construction**, so this one is not that. It scans the **raw clause tail** and
never calls `target_noun_phrase` — which makes it independent of the boundary
logic, and the boundary is exactly where all seven came from. A future
re-truncation cannot hide from it.

Being deliberately over-broad, it flags the 43 too. Each flagged row must be
accounted for in exactly one of two ways: the classifier claimed the arm, or
the instruction prints `from <zone>`. Anything else is UNEXPLAINED and halts
the pass before provenance writes — the standing `det-patterns-v2.json`
condition.

```
targeted-bounce : 46 explained by a printed CR zone origin, 0 UNEXPLAINED
targeted-destroy:  0 explained,                             0 UNEXPLAINED
targeted-exile  : 12 explained,                             0 UNEXPLAINED
```

**Negative-controlled.** `--invariant --selftest` drops the zone explanation;
every explained row becomes unexplained, **58 failures, exit 1**. A guard that
has never been shown to fail is not known to be a guard.

---

## 5. VERIFICATION

| check | result |
|---|--:|
| corpus-wide diff vs `HEAD`, all three actions | **+7, −0** |
| the seven, individually | all recovered to their pre-`e780842` class |
| residual invariant | 0 unexplained |
| invariant negative control | 58 failures, exit 1 |
| NC1–NC4 (`--audit`), all three actions | exit 0 |
| `foundry_gate2.py` | 13 run, 12 pass, 1 known-excused, 0 unexpected |
| report determinism ×2 | byte-identical |

Memberships: destroy 1,558 → **1,559** · exile 604 → **609** · bounce 330 →
**331**. Destroy residual 3 → **2**, which is the two `destroy target token`
cards and matches `OBJECT-LATTICE-2026-08-09.md` §3a exactly — independent
confirmation that the record's number was right and the 3 was the regression.

---

## 6. STANDING, AND WHAT IS STILL OPEN

Captain's own read of the remaining residual is recorded and agreed:

* **`Destroy target token`** (The Ruinous Wrecking Crew, Kraul Whipcracker) is
  correct residual. A token is CR 111, not one of CR 110.4's six permanent
  types, and has no ratified §5 OBJECT token. *"I would not smuggle that into
  this permanent-type lattice."* A `targeted-destroy-token` facet is a possible
  future ratification, not this pass.
* **Flicker cards belong in `targeted-exile-*`.** The lattice records an
  objective action fact; it does not assert removal. Downstream similarity must
  not read `targeted-exile-creature` alone as *"creature removal"* — a second
  fact (temporary exile / return-to-battlefield) differentiates them later.

**Open, and NOT resolved here** — grammar §6a rule 2 says an axis scoped `any-`
asserts it can affect an opponent's permanents, and the lattice reads **no
scope at all**. So `targeted-exile-creature` currently holds both
`exile target creature` and `exile target creature you control` (Displace,
Lukka). Three of the seven recovered here are that shape. Captain's flicker
ruling above settles that they are *members*; whether the family needs a
`-you-control` scope sibling is a §1 question ("REQUIRED the moment a
scope-sibling exists") and is **reported, not decided**.

---

## 7. WHERE THE RATIFICATION LIVES

Ratification here is **pattern-registry state**, not a documentation edit. The
authoritative record is the lattice row in **`docs/det-patterns-v2.json`**:

| field | value |
|---|---|
| `status` | `ratified` |
| `corpus_hits` | 2653 → **2499** (2653 predated the 2026-08-12 fix and was stale the day it was written) |
| `lattice.invariant` | names the write-blocking precondition |
| `note` | re-ratification, the deferred scope question, and the token residual |
| `v2_changelog` | the incident, the repair, and why the edit is in place |

**Edited in place rather than minting a v3**, following the precedent set for
this same row on 2026-08-12. The `standing_condition`'s *"a new file, not an
in-place edit"* governs changing a ratified pattern's BEHAVIOUR out from under
a review; here the behaviour is being corrected to what the row's own
`def_anchor` already claimed, and the correction is logged in the changelog the
file keeps for exactly this. Flagged as a judgment call, not a settled one.

The 23 class axes needed **no** ratification and none was performed — grammar
§11.2 / b6 §11.2: *"virtual nodes instantiate on first quote-verified member."*

## 8. WHAT SHIPPED WITH THE RATIFICATION

**A 12-row sample of what WAS produced cannot see a membership that is
MISSING.** The sample gate was green on 2026-08-12 and the seven were already
gone. Three protections close that, each built on an existing mechanism:

| protection | mechanism | precedent |
|---|---|---|
| grammar-shape fixtures (20) | `--fixtures` | `foundry_probe.py`'s 10 inline guard cases |
| independent residual invariant | `--invariant`, and `foundry_det_pass.assert_lattice_invariant` on BOTH phases | the standing condition's own *"halts the pass before provenance writes"* |
| **tracked membership floor** | `assert_ratified_total()` — `det-patterns-v2.json`'s `corpus_hits` re-derived | `foundry_recorded_numbers.py`, Gate 2 row 11 |
| per-class membership ratchet (**local**) | `foundry_audit_baseline`, section `object_lattice` | `foundry_reachability.py`'s `reaching` ratchet |

All four run as one exit code in **Gate 2 row 14**, `object_lattice`.

### 8a. THE RATCHET IS LOCAL, AND THAT IS WHY THERE IS A FOURTH ROW

**Audited 2026-08-13, after ratification.** An earlier draft of this section
claimed the per-class ratchet made a falling membership count fatal, full stop.
**That claim was true only on a machine where the section happens to be
pinned**, and the audit measured all four ways it fails open:

| condition | measured behaviour |
|---|---|
| `audit-baseline.json` absent | `report()` → 0, `--gate` printed **GREEN** having compared nothing |
| file present, `object_lattice` section absent | identical — not distinguished from no file |
| fresh clone | `experiments/out/` is **gitignored** (`.gitignore:6`), `git ls-files` → 0, so *every* clone starts unpinned |
| `foundry_det_pass.py apply` | enforced the residual invariant and the hit-cache reconciliation, and **never** consulted the baseline |

`--update-baseline` on a fresh machine could therefore bless an
already-regressed producer with no historical comparison at all, and the
accepted number would persist nowhere another machine could read it.

**This is shared behaviour, not a lattice defect.** All six pre-existing
consumers (`conservation`, `visibility`, `reachability`, `definition_drift`,
`ruling_registry`, `ground_truth_wide`) call the same `base.report(section,
metrics, update)` and inherit the same bootstrap. Making absence globally fatal
would turn every first run red, so the shared module was **not** changed.

**The fix is one source of truth, and it already existed.**
`docs/det-patterns-v2.json` is tracked, reviewed and ratified, and its lattice
row already carries the reviewed population as `corpus_hits: 2499`. The gate
now re-derives it and fails on drift in **either** direction — a fall is
membership loss, a rise is memberships nobody reviewed, and both mean the row
and the producer have stopped describing each other. Acceptance is durable
because the accepted number lands **in git**, which is what an
`--update-baseline` commit could never do for an ignored file.

The same assertion runs at the authoritative write boundary in
`foundry_det_pass.assert_lattice_invariant`, alongside the hit-cache
reconciliation it structurally resembles.

**Negative control, replaying the actual incident on a fresh clone** (no local
baseline, ratified row asserting 7 more memberships than the producer yields):

```
RATIFIED TOTAL: ...asserts 2,506 memberships; the producer now yields 2,499 (-7).
                MEMBERSHIPS WERE LOST.
--gate exit = 1                     (before this change: 0, "GREEN")
det_pass write boundary: HALTED     (before this change: not consulted)
```

The local ratchet is **kept**: it is per-class where the tracked floor is a
total, so it still localises a loss that a compensating gain would hide. It is
now correctly described as a **local diagnostic**, not the standing floor.

### 8b. `corpus_hits` IS A MEASUREMENT, NOT AN EQUALITY INVARIANT

**Audited 2026-08-13, second pass.** §8a's first implementation asserted
`live == corpus_hits` and failed either way. **That was a stronger invariant
than this repository's architecture intends**, and three independent pieces of
evidence say so:

| evidence | finding |
|---|---|
| live re-measure of all 44 regex patterns | **3 ratified patterns have already drifted** and Gate 2 is green — `grants-unblockable-target` 35→34, `innate-unblockable` 183→184, `activated-grants-self-unblockable` 25→26. Nothing asserts equality on this field, and never has. |
| the schema | the sibling field is named **`codebook_n_members_at_probe`** — `_at_probe` is the schema saying point-in-time out loud |
| the file's own `preprocessing_standard` | records these counts **being updated** on re-probe: *"Re-probing all patterns under this standard changed 5 hit counts … innate-unblockable (161->183)"* |

`enters-tapped` (+23) and `imposes-enters-tapped` (−24) look far more drifted
and are **not**: they are decided by `compute_special_hits`'s G2 subject split,
not by their `pattern` field, so reading that field measures the wrong thing.
A probe defect, caught before it became a finding.

**Consequence, measured:** a mere **+12 new cards** joining `destroy-creature`
turned the gate RED on a fresh environment — a false alarm on the pipeline's
ordinary weekly Scryfall refresh.

**Corrected to directional, which is not a new idea** — it is
`foundry_audit_baseline`'s own ratchet semantics (`WORSE_IF_DOWN` fatal,
better-direction movement reported) applied to a number that lives in git:

| movement | behaviour |
|---|---|
| FALL | **fatal** — the 2026-08-13 incident |
| RISE | **reported, not fatal** — corpus growth; re-pin `corpus_hits` once accounted for |
| equal | silent |

### 8c. THE GAP THIS DOES NOT CLOSE, STATED RATHER THAN PAPERED OVER

**A total is structurally blind to redistribution.** Measured, a compensating
−7 / +7 across two classes of one action:

| environment | tracked floor | per-class ratchet | gate |
|---|---|---|---|
| baseline pinned | silent (net 0) | **FIRES** | RED |
| fresh / unpinned | silent (net 0) | silent (unpinned) | **GREEN** |

So the two guards are exactly complementary and each sits in the other's blind
spot: the floor is durable but total-only; the ratchet is per-class but local.
For comparison, a plain **−7 loss on a fresh environment is RED** — the
incident class that motivated all of this stays caught.

**No per-class number was added to the tracked row**, deliberately. That is
precisely the equality invariant §8b just disproved, one level finer, and it
would freeze growth per class instead of in total.

**Nor does an existing tracked artifact close it.** `experiments/moves/*.json`
(20 files, tracked, replayed by `foundry_ground_truth.py`, Gate 2 row 7) is the
repository's durable, growth-tolerant, per-card accountability mechanism — 534
Captain-ratified seeds with verbatim evidence quotes, where adding cards to the
corpus cannot invalidate an existing seed. But it grades a seed's **grammar §2
DELIVERY token**, and an object CLASS is not a delivery token, so it does not
today assert lattice class membership. The lattice's own 20 fixtures are the
same shape and share the same limit: a fixture covers the cards it names, and
an arbitrary redistribution need not touch one.

**Left open on purpose.** Closing it means either a per-class tracked count
(the disproved invariant) or enrolling lattice class memberships into the
ground-truth seed mechanism — a real design question about what
`experiments/moves` asserts, and Captain's call, not a side effect of a
durability audit.

**`memberships` was added to `WORSE_IF_DOWN`** in `foundry_audit_baseline.py`.
That is the whole membership-delta answer and it needed no new law: the ratchet
already made worse-direction movement fatal and better-direction movement
require an explicit `--update-baseline`. It had simply never been pointed at a
membership count. **A falling count is now a regression**, so a removal must be
re-pinned on purpose with a stated reason — the evidence burden the incident
showed was missing. Verified against all six pre-existing baseline sections:
the new markers `memberships` and `residual` collide with **0** of the 98
already-pinned keys.

**The fixtures are grammatical shapes, not card names.** The seven cards are
kept beside them as corpus fixtures, but nothing in the classifier reads a card
name and each passes only because its SHAPE is handled.

## 9. WHAT THIS RATIFICATION DOES NOT DECIDE

* **Controller/ownership scope — OPEN.** The class slot carries the objective
  object fact only. `exile target creature you control` is
  `targeted-exile-creature` because the targeted object class *is* creature.
  Whether the family needs grammar §6 scope siblings is a §1 question
  ("REQUIRED the moment a scope-sibling exists") and **no scope sibling was
  created**. Ratifying the family did not force one: §1 makes SCOPE omissible
  while no sibling differs only by scope, and none exists.
* **`targeted-destroy-token` — NOT AUTHORED.** A token is CR 111, not one of
  CR 110.4's six, and has no ratified §5 OBJECT token, so §11.2's
  self-instantiation cannot reach it — it would be new vocabulary, which is a
  Captain ratification. The 2 cards stay residual, and **residual is not an
  error**: the invariant requires zero *unexplained* residual, not zero
  residual.
* **Flicker is not removal.** The lattice records an action/object fact. It
  makes no removal claim, and no temporary/permanent taxonomy was invented
  here. Downstream similarity must not read `targeted-exile-creature` alone as
  "creature removal".
