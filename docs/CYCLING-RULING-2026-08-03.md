# CYCLING — RULING (Captain-ratified 2026-08-03)

> **Captain:** *"Cycling deserves its own ruling as cycling itself is a card
> ability. An activated ability I think. So it can dodge traditional counter
> spells because counterspells usually target spells, not abilities. So down the
> road for parents cycling will be part of a 'dodges counter spells' parent."*

**Both halves verified against the local CR, not recalled.** Gate-3 dossier run
on `cycling`, `activated-cycling`, `cycling-trigger`, `typecycling` first:
**no prior ruling on any of them, in any status.**

## 1. The CR backs it verbatim

**CR 702.29a** — *"Cycling is an activated ability that functions only while the
card with cycling is in a player's hand. 'Cycling [cost]' means '[Cost], Discard
this card: Draw a card.'"*

**CR 113.9** — *"Activated and triggered abilities on the stack aren't spells,
and therefore **can't be countered by anything that counters only spells**.
Activated and triggered abilities on the stack can be countered by effects that
specifically counter abilities."*

So the chain is exact: cycling is an **activated ability** (702.29a) → an
activated ability on the stack **is not a spell** (113.9) → "counter target
spell" cannot touch it. Captain's reasoning holds end to end, with the one
refinement 113.9 adds: it dodges *spell*-counters specifically, not
ability-counters (Stifle, Disallow).

**This is `activated` DELIVERY vocabulary already** (§2, CR 113.3b). Cycling
needs no new delivery token — it needs an EFFECT token, and that is the
ratification below.

## 2. RATIFIED — `cycling` enters the closed vocabulary

Captain's directive ratifies `cycling` as a slug token, anchored to CR 702.29.
Grammar §10.3 requires exactly this: an unknown token halts, and new vocabulary
is a Captain ratification. Recorded here as its sole home.

Per §6a, `cycling` is a **CR term of art hardcoded to its mechanic** and is
therefore **axis identity, never a facet**.

## 3. The population — 433 cards, measured

| shape | CR | cards |
|---|---|--:|
| **`cycling [cost]`** — the keyword ability | 702.29a | **304** |
| **`[type]cycling [cost]`** — typecycling variant | 702.29e | **91** |
| "When you cycle **this card**" — a *triggered* ability | 702.29c | 54 |
| "Whenever you cycle **a/another card**" | 702.29d | 21 |
| "Whenever you cycle **or discard** a card" | 702.29d | 14 |
| cycling **costs** / "a card with a cycling ability" matters | 702.29f | 9 |

Typecycling variants measured: basic land 31 · plains 12 · mountain 11 ·
swamp 10 · forest 10 · island 10 · wizard 2 · sliver 1 · artifact land 1
(plus 3 cards that *grant* typecycling to cards in hand, which are not
typecycling cards themselves).

## 4. BUILT — 2 axes

### `rule:cycling` — 304 members
The keyword ability itself. Effect is fixed by CR 702.29a (discard this card,
draw a card), so the axis is one shape with one effect; the cost is a parameter.

### `rule:typecycling` — 91 members, parameterized by type
**Ruled a SEPARATE axis from `cycling`, not a parameter of it.** The reasoning,
because this one is genuinely arguable:

- **For merging** — CR 702.29f is emphatic: *"Typecycling abilities **are**
  cycling abilities… Any cards that trigger when a player cycles a card will
  trigger when a card is discarded to pay a typecycling cost… Any effect that
  looks for a card with cycling will find a card with typecycling."* That is
  the §8.4a Role test almost word for word — nothing in the game distinguishes
  them — and §8.4a ruled Role a single umbrella on exactly that evidence.
- **For splitting, and why it wins** — the **printed effects are different
  mechanics.** Cycling draws a card off the top; typecycling **searches your
  library for a specific card and puts it in your hand**. That is card
  selection versus card advantage, and for deck-building they are not
  substitutes — a Plainscycling creature is a land, functionally, and a Cycling
  creature is not. §6b is binding here: *"two axes may be merged only when their
  printed shapes are identical. Similar outcome is never grounds for a merge; it
  is grounds for a shared parent."*

**702.29f is therefore read as a PARENT edge, not a merge argument.** "Typecycling
abilities *are* cycling abilities" is an is-a relationship, which is precisely
what the parent layer encodes. Logged in §6.

The specific type (`plains`, `basic land`, `wizard`…) is a **parameter**, per
batch-5's counter-polarity precedent — no card conditions on *which* type
another card can typecycle for.

## 5. LEDGERED, not authored — the trigger family

CR 702.29c and 702.29d describe *triggered* abilities, which per §2 need
**delivery vocabulary that does not exist**:

| proposed token | CR | cards | why not authored now |
|---|---|--:|---|
| `cycled-trigger` (this card was cycled) | 702.29c | 54 | delivery-only slugs are PARENTS (batch-5 D16 precedent: `rule:etb`, `rule:landfall`). Its children are `cycled-trigger-<effect>` and the 54 members carry ~20 different effects — authoring those is a corpus pass, not this ruling. |
| `cycles-a-card-trigger` | 702.29d | 21 | same |
| `cycle-or-discard-trigger` | 702.29d | 14 | CR names this shape explicitly and it fires **once** per cycle (702.29d) — a real distinction from a naive "cycle OR discard" reading |

**These three are new DELIVERY vocabulary and need Captain ratification** before
any child instantiates (§10.3). They are also three more entries for the
`end-step-trigger` batch in `DELIVERY-GAP-CENSUS-2026-08-03.md` — the same
vocabulary gap, found from a different direction.

Note CR 702.29c's own gloss: *"'When you cycle this card' means 'When you
discard this card to pay an activation cost of a cycling ability.'"* So the
trigger is on **paying the cost**, not on the draw — which is why a cycled
trigger still happens if the draw is replaced or prevented.

## 6. PARENT CANDIDATES — logged, never authored

Parents are DERIVED (union of children + direct members), per
`PARENT-TREE-CANDIDATES.md`. Two entries:

1. **`rule:dodges-counterspells`** — Captain's own naming. The job: *this
   card's effect cannot be answered by "counter target spell."* CR 113.9 is the
   anchor. `cycling` and `typecycling` are members; so is every activated
   ability, which means **the parent's real membership is much larger than
   cycling** and it needs its own derivation pass. Flagged as a genuine parent
   with a large, decidable membership — unusual, and worth doing.

   Worth noting under **S4a (parents are UNRANKED)**: a cycling card is a
   *dodges-counterspells* card **and** a *card-filtering* card at equal weight.
   Neither wins.

2. **`rule:cycling`** as parent of `rule:typecycling` — the is-a edge CR 702.29f
   states outright (§4 above).

## 7. What this opens

`cycling` is the first CR **702** keyword (a keyword *ability*) to get an axis
this arc; everything before it was a CR **701** keyword *action*. The two are
different populations and the coverage packet only counted 701. **CR 702 has not
been censused at all** — `--rank` showed flying (4,452 cards), trample (1,597),
vigilance (1,096), first strike (780), flash (696), lifelink (692) and equip
(632) all with **no axis**. That is a bigger uncovered population than the 40
keyword actions, and it is the natural next census.
