# THE OBJECT LATTICE — M8 was ratified in batch 6 and never implemented

**2026-08-09.** Captain: *"it was weeks ago I said that cards that destroy
multiple things need a one rule instance of each object it destroys. Like the
card Putrefy."*

That is correct, it is ratified, and the measurement is that **it was never
applied to a single card.**

---

## 1. THE LAW, QUOTED FROM THE RATIFIED RECORD

`docs/MASTER-HANDOFF-ADDENDUM-4.md` §4, the ratified rulings registry:

> | **M8 generalized (b6 D3)** | Multi-class `targeted-<action>` cards get
> every applicable per-class tag, all action verbs, **never combo tags**;
> removal-for-breadth is wrong. |

`docs/CODEBOOK-NAMING-GRAMMAR.md` §5:

> Per-object-class siblings are the law for every `targeted-<action>` family
> (M8 generalized, b6 D3): OR-shaped multi-class targets get every applicable
> class tag; the class lattice is a ratified grammar with virtual nodes.

And the one that changes what needs Captain at all —
`MASTER-HANDOFF-ADDENDUM-4.md` §4 again:

> | **Lattice grammars (b6 §11.2)** | Captain ratifies GRAMMARS (stem + closed
> facet slots); **virtual nodes instantiate on first quote-verified member, no
> fresh ratification**; empty axes never authored; `lane=codebook-grammar` for
> grammar-composed slugs. |

**So `rule:targeted-destroy-creature` never needed ratifying.** The decision
sheet I brought on it was asking Captain to re-ratify one arbitrary node of a
grammar already ratified whole. The grammar is the ratification; the node
self-instantiates on its first quote-verified member.

Supporting: `CORPUS-PASS-PLAN.md` §151 lists `targeted-<action>-<class>` among
the seeded grammars, *"(M8, generalized to all targeted-<action> families
batch-6 D3)"*. `TIER-4-DECISION-PACKET-2026-08-02.md` §231 applies it —
*"b6 D3), so under §11 it self-instantiates on this quote-verified member."*

## 2. MEASURED STATE BEFORE THIS WORK

| | |
|---|--:|
| cards carrying 2+ class siblings of one action family | **0** |
| `rule:targeted-destroy` active class children | **0** |
| `rule:targeted-exile` (n=72) active class children | **0** |
| `rule:targeted-bounce` active class children | 1 |
| `rule:targeted-destroy` members, and how they arrived | 172, **100% `human`/`batch-1..7`** |
| DET patterns touching destruction (of 45) | **1** — `rule:prevents-regeneration` |

**Putrefy** — *"Destroy target artifact or creature. It can't be
regenerated."* — carries exactly one tag: `rule:prevents-regeneration`. The
rider is tagged and the spell is not, because the rider is the half with a DET
pattern.

### 2a. Why the consolidation plan does not fix it either

Run 1 emitted the right thing for Putrefy — codebook lane, label
`rule:targeted-destruction`, quote *"Destroy target artifact or creature."*
The 2026-08-09 rename made that slug a `renamed` tombstone, and a codebook-lane
hit on a renamed slug is excluded from `codebook_all_hits` and becomes a
**redirect routing row**, which creates no membership. Putrefy is in the plan's
routing list right now, `target: rule:targeted-destroy`.

**367 cards redirect to `targeted-destroy` alone; 2,923 redirect rows in
total.** That is a separate open item (§6).

---

## 3. THE IMPLEMENTATION — `experiments/foundry_object_lattice.py`

Every piece of vocabulary is derived at run time. Nothing is typed.

| source | what it supplies | why it is the right source |
|---|---|---|
| **CR 701.8a** | *"To destroy a permanent, move it from the battlefield to its owner's graveyard."* | only a PERMANENT can be destroyed, so the class slot is the permanent-type list and **not** the card-type list |
| **CR 110.4** | *"There are six permanent types: artifact, battle, creature, enchantment, land, and planeswalker."* | closed; parsed, with cardinality checked against the rule's **own stated count** ("six") rather than a number typed here |
| **CR 205.2a** | the 15 card types | the wider domain, for actions that leave the battlefield |
| **CR 205.3g–q** | subtype → permanent type | **consumed** from `foundry_cr702_classes.type_vocabulary()`, which already keys the ten lists by parent type. Never re-parsed. |
| **CR 300.2** | *"Some objects have more than one card type (for example, an artifact creature)"* | separates AND-shaped from OR-shaped targets |
| **CR 701.8b** | the only two routes to destruction are the word "destroy" and the lethal-damage SBA | the word-reading boundary is one of the CR's own two, not a heuristic |
| **grammar §5** | `validate_slug.OBJECT_VOCAB` | every emitted class asserted present, so a CR term with no ratified slug token halts instead of minting vocabulary |

### 3a. Result, destroy family, corpus-wide

| | before | after |
|---|--:|--:|
| cards reached | 172 | **1,226** |
| memberships | 172 | **1,579** |
| multi-class cards — *the population M8 is about* | **0** | **313** |

Per class: creature 609 · artifact 371 · enchantment 273 · land 157 ·
planeswalker 60 · permanent 48 · nonland-permanent 47 ·
noncreature-permanent 13 · battle 1.

Top combinations: artifact+enchantment 151 · creature+planeswalker 49 ·
artifact+creature 23 · artifact+creature+enchantment 18 · artifact+land 17.

**Putrefy** → `rule:targeted-destroy-artifact` + `rule:targeted-destroy-creature`.

**Residual: 2 cards**, both *"destroy target token"* (The Ruinous Wrecking
Crew, Kraul Whipcracker). A token is CR 111, not a card type, and has no
ratified OBJECT token. Reported, not guessed at.

### 3b. Verification — read, not sampled

* **All 39 subtype-derived hits read individually: zero defects.** The
  behaviour is exactly right — *"Djinn or Efreet"* resolves to `creature`
  alone, *"Scarecrow or Plains"* to `creature` **and** `land`. The class slot
  is the TYPE; a coordination between two subtypes of one type is one class.
* **NC1** — every claimed card prints the word `destroy`: **0** failures.
* **NC2** — 31,329 cards with no targeted clause yield nothing.
* **NC3** — 16 cards whose clause sits only inside a quoted grant. **All 16
  read.** They are self-grants (Harmonic Sliver *is* a Sliver) and Equipment
  grants (Heartseeker). Both genuinely hand the player that removal, so they
  are **tagged**: grammar §2's quoted-grant exclusion governs DELIVERY, and the
  class slot is an EFFECT question. Captain's ratified criterion is
  deck-building relevance. Listed in `--audit` output so the call stays visible.
* **NC4** — all 9 emitted slugs pass `validate_slug`: **0** failures.

**Both guards were negative-controlled.** NC4 rejects `-widget` and also
`-conspiracy` — a real CR 205.2a card type with no ratified OBJECT token, which
is the correct refusal. And `_split_cr_list` **shipped the Oxford-comma defect
its own docstring warned about** (`and planeswalker`): the **cardinality** guard
passed it (six members, one wrong) and the **content** guard caught it in one
run. A count cannot see a substitution — demonstrated, not asserted.

---

## 4. A FINDING IN THE CONSOLIDATION PLAN — 3 axes M8 forbids

M8 says **"never combo tags"**. The plan instantiates three:

| planned axis | Gate 3 | what M8 requires instead |
|---|---|---|
| `rule:targeted-exile-artifact-or-creature` | no ruling | `-artifact` **and** `-creature` |
| `rule:targeted-exile-artifact-or-enchantment` | no ruling | `-artifact` **and** `-enchantment` |
| `rule:targeted-bounce-artifact-or-enchantment` | no ruling | `-artifact` **and** `-enchantment` |

Dossiered before being called defective: all three are `NOT IN CODEBOOK` and
carry **no ruling on any law-bearing document**.

**The nine `activated-tap-or-untap-*` axes are NOT this.** `tap or untap` is one
action whose choice is the ability (b6 D2 ratified `activated-tap-or-untap-<scope>`
as its own grammar). The OR is between verbs, not object classes. They stand.

---

## 5. WHAT NEEDS CAPTAIN, AND IT IS ONE THING

**Not the axes.** b6 §11.2 self-instantiates virtual nodes on first
quote-verified member, no fresh ratification.

**The DET pattern does.** `det-patterns-v2.json`'s own standing condition: a
fixed-seed sample per pattern is reviewed and *any* sample row failing its axis
definition halts the pass before provenance writes. That gate is unchanged and
is the one remaining approval.

`foundry_object_lattice.py --samples N` emits exactly that sheet.

### 5a. One structural extension the DET machinery needs

Every pattern in `det-patterns-v2.json` is `slug` + one regex → **one** axis. A
lattice pattern is one matcher → **N axes decided at match time**. That is a
schema and `foundry_det_pass.py` change, not a new JSON row. Built and
measured here; not yet wired.

### 5b. Genuinely unruled, reported not decided

1. **CR 300.2 conjunctive targets — 7 cards.** *"Destroy target artifact
   creature"* names ONE object that must be both types. M8 governs the OR case
   by name and is silent on AND. Currently reported and not fused.
2. **Token targets — 2 cards.** CR 111; no ratified OBJECT token.
3. **The umbrella.** `rule:targeted-destroy` keeps its 172 human members; the
   lattice adds the children. Whether the umbrella's membership becomes the
   derived union (Captain: *"we need a grouping strategy that is derived. but
   we also need tags that act as umbrellas"*) is the W9 parent-layer question,
   and `PARENT-TREE-CANDIDATES.md` S1–S7 already ratifies parents as derived.
   **A8 protects the existing rows either way**: a DET refresh replaces only
   its own rule-derived assertions and never touches a human or llm one.

---

## 6. STILL OPEN, LARGER THAN THIS FAMILY

**2,923 redirect rows in the consolidation plan create no membership.** The
lattice recovers the destroy ones by re-deriving them from the corpus, but
`combat-trick-pump-creature-you-control` (375) and
`replacement-enters-with-counters` (318) are not lattice cases and would still
tag nothing. Whether a rename redirect should mint a membership on the target
is a real ruling, and I previously waved it past as correct-by-design.

**The lattice covers five ratified action stems**, not one:
`grammars.json`'s `targeted-<action>` closed vocab is `destruction` (now
`destroy`), `bounce`, `exile`, `discard`, `damage`. Only `destroy` is measured
here. `damage` additionally has its own closed recipient list — **CR 120.1's
four** — which the grammar already tracks separately.

**Grammar §5 line 651 still spells the lattice `targeted-destruction-<class>`**,
the pre-rename form, and `grammars.json`'s action facet `closed_vocab` still
carries `"destruction"` with `"destroy"` absent. That is §7 item 2 of the A15
ruling doc, still open, and it is now load-bearing: the extractor emits
`targeted-destroy-<class>` against the live axis and the grammar disagrees with
it in writing. **Generator fix (G4), not a hand edit.**
