# Role shapes — built, and the 20 held back

Executed 2026-08-02. First application of §8.4a (`role` umbrella) and §6b
(per-shape axes) to a previously unmodelled mechanic.

Before this, **all 39 Role-creating cards were on no axis at all.**

## Built — 3 axes, 19 members, every one hand-verified

| axis | n | printed shape |
|---|--:|---|
| `create-token-role-attached-to-own-creature` | 8 | spell; "attached to target creature **you control**" |
| `etb-create-token-role-attached-to-own-creature` | 8 | ETB trigger; same attachment |
| `etb-create-token-role-attached-to-self` | 3 | ETB trigger; "attached to **it**" — the creature that just entered |

Provenance is `class: human`, `captain-cli-2026-08-02`. The lint gate rejected
my first attempt at `rule-derived` — correctly, because I read these line by
line rather than deriving them from a ratified pattern. The gate knew the
difference before I did.

## Held — 20 of 39, with reasons

I ran a classifier over all 39 first. **It was wrong on 6.** Rather than mint
axes off it, I read all 39 lines by hand; these are what did not survive.

### Created-ability cases — §2, ratified this morning, catching real cards

| card | why |
|---|---|
| **Not Dead After All** | "target creature you control gains *'When this creature dies, … create a Cursed Role attached to it'*" — the death trigger is **granted to another creature**. The card has no death trigger. |
| **Giant Inheritance** | "Enchanted creature … has *'Whenever this creature attacks, create a Monster Role token'*" — the attack trigger is **granted by an Aura**, not the card's own. |

A classifier reading effect words filed both under the granted trigger's
delivery. §2 says delivery belongs to the *creating* ability.

### Delivery vocabulary that does not exist yet

| card | needs |
|---|---|
| Spellbook Vendor | `begin-combat-trigger` — flagged in tier-4 D2, still unratified |
| Gadwick's First Duel · The Witch's Vanity | a Saga-chapter delivery value; §2 has none |

Three cards blocked on the same §2 gap. Worth ratifying the vocabulary
together rather than piecemeal.

### Shapes needing their own ruling

| card | printed shape | why held |
|---|---|---|
| **Asinine Antics** | "For **each creature your opponents control**, create a Cursed Role token attached to that creature" | mass + opponent-scoped — a one-sided board neutering (every creature becomes 1/1). My classifier called it "self". Genuinely its own shape. |
| **Twisted Sewer-Witch** | creates a Rat token, then a Role "attached to **that Rat**" | attaches to a token it just created — a distinct shape with no sibling |
| **Dunbarrow Revivalist** | Role creation nested inside a one-time boon | nested delayed ability; delivery unclear without a ruling |
| **Gylwain, Casting Director** | modal, "attached to **that creature**" | the referent is set by an earlier mode |

### The ownership sub-split I did not force

`prior-target` — the card targets something, then attaches the Role to that
same thing — turned out **not to be one shape**:

- Monstrous Rage: "**Target creature** gets +2/+0 … attached to it" → any creature
- Royal Treatment: "**Target creature you control** gains hexproof … attached to that creature" → own-restricted

Under C4b ownership is axis identity, so these are two axes, not one. Five
cards (Monstrous Rage, Become Brutes, Return Triumphant, Royal Treatment,
Vantress Transmuter) plus the three `any`-scoped singletons want that split
done deliberately rather than at the end of a long session.

## What this cost, honestly

My shape classifier was **~85% accurate** (33 of 39) on a mechanic with only
39 cards and completely regular templating. That is the argument for
hand-verifying closed sets rather than trusting a first-pass classifier — the
same lesson as §S4 (154→90→44) and C4f (~50 correct axes flagged), now with a
measured rate.

It is also the argument *for* the itemization: every one of the 6 errors was a
real distinct shape that the naive reading would have flattened.
