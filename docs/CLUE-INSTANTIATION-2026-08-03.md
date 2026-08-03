# CLUE INSTANTIATION — 2026-08-03

The `investigate` / Clue-token population, measured, routed, and instantiated
under **already-ratified** vocabulary. Step 1 of `CR-COVERAGE-PACKET-2026-08-02.md`
§5. **No new ratification was needed to build what §1 below builds** — §4 is the
part that comes back to Captain.

Spec: `experiments/moves/2026-08-03-clue-instantiation.json`
Backup: `codebook.v0.7.pre-clue-instantiation.20260803-073352.json`
(sha256 `999a9021…c726c9ee9e5`, readback-verified)

## 0. Authority — why this needed no ruling

| link | source |
|---|---|
| `clue` is ratified token-type vocabulary | grammar §8 rule 4 (CR 111.10, full 21-token enumeration) |
| `create-token-<type>` is a ratified grammar family | batch-5 **D14** |
| `create-token-clue` is named as a future sibling **by name** | batch-5 D14, `TRIAGE-BATCH-5.md:1010` |
| a virtual node instantiates on first quote-verified member, no fresh ratification | grammar **§11** |
| CR 701.16: *investigate* **is** "create a Clue token" | CR |

Gate-3 dossier run on `create-token-clue` before authoring: **never existed in
any status**, 16 hits across 7 documents, 0 verdicts against it. The node should
have self-instantiated at batch 5; nothing was looking.

## 1. Built — 10 axes, 120 memberships, 116 cards

| axis | n | scope |
|---|--:|---|
| `rule:etb-create-token-clue` | 35 | own |
| `rule:create-token-clue` (spell ability, DELIVERY omitted per §1) | 34 | own |
| `rule:activated-create-token-clue` | 17 | own |
| `rule:cast-trigger-create-token-clue` | 10 | own |
| `rule:attack-trigger-create-token-clue` | 8 | self |
| `rule:combat-damage-to-player-create-token-clue` | 5 | self |
| `rule:death-trigger-create-token-clue` | 5 | self |
| `rule:upkeep-trigger-create-token-clue` | 4 | own |
| `rule:landfall-create-token-clue` | 1 | own |
| `rule:any-damage-to-creature-create-token-clue` | 1 | self |

120 > 116 because four cards print two deliveries and hold both memberships per
§1's multi-axis rule: **Duggan, Private Detective** and **Raven Eagle**
("enters **or** attacks"), **Obsessive Pursuit** ("enters **and** at the
beginning of your upkeep"), **Tivit, Seller of Secrets** ("enters **or** deals
combat damage to a player").

Every delivery token above is on §2's ratified list. Nothing was approximated.

## 2. The boundaries this rests on — STATED, per Gate 4

A finding without its boundary is not reportable, so here are all five.

- **B1 — creator, not referencer.** The keyword must appear as an **effect**.
  `investigate` inside a trigger *condition* is not a creation.
- **B2 — §2's rows are read literally.** `etb` is "when **~** enters";
  `attack-trigger` is "whenever **~** attacks"; `death-trigger` is the source's
  own death. A trigger keyed on *another* permanent is a different printed
  shape (§6b) and was **not** folded into the near neighbour.
- **B3 — created-ability rule (§2).** A card does not deliver an ability it
  creates. Granted abilities and abilities set up by another trigger route to §4.
- **B4 — ownership is axis identity (§6a rule 2).** A card where *another player*
  ends up with the Clue makes a different claim.
- **B5 — no vocabulary, no axis.** A delivery §2 does not define is BLOCKED,
  never approximated onto the nearest token.

## 3. The measurement, and where the handoff's number came from

| boundary | count |
|---|--:|
| handoff / CR-coverage packet | 132 |
| **prints `investigate`**, gate-passing, all faces, reminder text stripped | **137** |
| prints `Clue` but not `investigate` | 37 |
| **Clue CREATORS** (union, after B1) | **163** |
| routed to an axis | 116 |
| routed to §4 for a ruling | 47 |

**The 132 was low because it counted the keyword only.** 26 cards create Clue
tokens without ever printing `investigate` — Messenger Hawk, Tolls of War,
Zuko's Exile, The Third Doctor, Transmutation Font and others. Per §6a the
printed instruction is the claim whether or not the keyword is used, so the
real population is **163**, not 132. Correcting the packet's own number.

Reminder text made no difference to the `investigate` count (137 either way) but
**strips 16 cards** from a naive `Clue` grep, because the investigate reminder
parenthetical names the token. §6a's boundary is doing real work here.

## 4. WAITING ON CAPTAIN — 47 cards, and the questions behind them

### 4a. Delivery vocabulary that does not exist (§2 gap) — 15 cards

Each is a printed shape with no ratified delivery token. **None were
approximated.**

| missing token | cards |
|---|---|
| **`end-step-trigger`** | Lord Jyscal Guado · Syndicate Heavy · Fae Offering · Teysa, Opulent Oligarch |
| Saga/Class **chapter trigger** | Fugitive of the Judoon · Heaven Sent · Tamiyo Meets the Story Circle · Blink |
| `turned-face-up` | Mistway Spy |
| damage **received** ("is dealt N damage") | Innocent Bystander |
| mill / library→graveyard | Unshakable Tail · Dennick, Pious Apprentice |
| triggers on *investigating* | Erdwal Illuminator |
| triggers on *collecting evidence* | Evidence Examiner |
| cards **leaving** your graveyard | Chalk Outline |
| counter **placed on** the source | Lonis, Genetics Expert |
| players **discarding** | Hostile Investigator |
| `begin-combat-trigger` (already carried) | Serene Sleuth's 2nd ability |

**`end-step-trigger` is the notable one.** §2 ratifies `upkeep-trigger` but not
its mirror, and no active axis uses it. It is a common, wholly regular shape.

### 4b. Self vs other — the split B2 forced — 17 cards

§2's rows say "**~** enters / **~** attacks / **~** dies". These cards trigger on
*someone else's* permanent, so under §6b they are distinct shapes needing their
own names. They are the larger half of some families:

| family | other-triggered cards |
|---|---|
| another creature **dies** | Eloise, Nephalia Sleuth · Merchant of Truth · Ulvenwald Mysteries · Madame Vastra · Thijarian Witness · Homicide Investigator · Nick Valentine, Private Eye |
| another permanent **leaves the battlefield** | Angelic Sleuth · Sally Sparrow |
| another creature **enters** | April O'Neil · Lonis, Cryptozoologist · Sharp-Eyed Rookie |
| **you** attack / a creature you control attacks | Agent 13, Sharon Carter · Meddling Youths · Thorough Investigation · The Seventh Doctor |
| creatures **you control** deal combat damage | Excogitator Sphinx · Ongoing Investigation (2nd ability) · Sophia, Dogged Detective |

**Consequence worth naming:** `rule:leaves-battlefield-trigger-create-token-clue`
was **not created** — both its candidates are other-permanent LTB, so it would
have been born empty, and `CORPUS-PASS-PLAN` §2 forbids that ("an axis with zero
members is a hypothesis").

Also here: **Nick Valentine** prints "you **may** investigate". §6b names
`may` vs mandatory as non-equivalent vocabulary, so it is a shape question too.

### 4c. Another player creates the Clue (§6a rule 2) — 7 cards

Declaration in Stone · Fateful Absence · Zuko's Exile · No Witnesses ·
Panther Pounce · Overencumbered · Wernog, Rider's Chaplain

These do **not** share an axis with the you-create population. But they do not
share one with *each other* either: "its controller", "target player", "each
opponent", "enchanted opponent" and "each player who controls the most" are
five different printed scopes, and §6b consequence 3 is explicit that adjacent
scope vocabulary is not equivalent vocabulary. **Question: how many axes?**

Note this also decides whether `rule:create-token-clue` keeps its bare name.
§1 makes the SCOPE slot *required the moment a scope-sibling exists* — so
building 4c renames the axis D14 named.

### 4d. One card that is not a creator at all

**Val, Marooned Surveyor** — "Whenever you discover, **investigate**, scry,
surveil, or seek one or more cards, Val deals 2 damage…". The keyword is in the
trigger condition; the effect is damage and lifegain. It creates no Clue.
Recorded because a keyword-frequency count will keep finding it.

### 4e. Academy Manufactor

"If you would create a Clue, Food, or Treasure token, instead create one of
each" — a token-creation **replacement**, not a Clue-creation shape. Belongs to
a token-replacement family that does not exist yet.

### 4f. The `-conditional` question — RULING NEEDED, and I assumed the answer

§6 ratifies `-conditional` for "an intervening-if or 'unless' gate on the same
ability". **Nine routed members have exactly that gate** and were placed on the
**base** axis anyway:

Drag the Canal · Sold Out · Torch the Witness · Hotshot Investigators ·
Resonance Technician · Raven Eagle · Foreboding Steamboat ·
Fire Nation Raider (Raid) · Funnel-Web Recluse (Morbid)

Read strictly, §6a ("the printed word is the claim") splits each of these off.
I did not split, because that mints 5-plus axes on my own initiative and §6b
warns against false splits as much as false merges. **This is a stated
assumption, not a finding.** If the ruling goes the other way it is one move
spec — the member list above is the whole worklist.

## 5. Provenance note — flagging rather than assuming

The 120 seeds carry `class: human` / `source_ref: captain-cli-2026-08-03`,
following the **2026-08-02 role-shapes precedent** for the identical operation.
The lint gate's `SOURCE_REF_FAMILIES` ties `rule-derived` to a
`det-patterns-v2:<n>` run number, which this is not, so `rule-derived` will not
lint.

**But these assignments are model-derived, not Captain-authored**, and `human`
is the full-weight class. The precedent may deserve a look: a
`rule-derived`-style class for grammar-composed, quote-verified, hand-read
assignments would describe this work more honestly than either existing option.
Not changed here — deviating from an established convention mid-task would be
the same kind of unratified invention this document is trying to avoid.

## 6. What this closes and what it opens

Closes: the lead case of `CR-COVERAGE-PACKET` §2 — the thesis that CR keyword
actions self-instantiate under existing grammar is now **demonstrated**, not
argued. One action, 10 axes, zero new vocabulary.

Opens: 39 CR keyword actions remain. The measured cost of this one is that
**29% of its population (47 of 163) needed a ruling** — mostly for delivery
shapes that are not specific to Clues at all (`end-step-trigger`, chapter
triggers, self-vs-other). **Ruling those once unblocks them across all 40
actions**, which is the argument for taking §4a and §4b as a general vocabulary
batch rather than as Clue business.
