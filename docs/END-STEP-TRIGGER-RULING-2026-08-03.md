# END-STEP TRIGGER — RULING (2026-08-03)

Third ruling in the 2026-08-03 shape series. Chosen over `mutate` (26 cards) and
`unlock a door` (26) because it is **the largest single-token gap in the corpus**
and the mirror of an already-ratified token — the cheapest ruling with the
largest unblock.

Gate-3 dossier: `end-step-trigger`, `end-of-turn-trigger` — **no prior ruling,
in any status.**

## 1. It corrects my own census number

`DELIVERY-GAP-CENSUS-2026-08-03.md` reported **601 cards** for `end-step`.
Measured properly against CR 603.7, that number was **wrong in both directions**
and the breakdown matters more than the total:

| shape | cards | status |
|---|--:|---|
| "at the beginning of **your** end step" | **405** | **needs vocabulary** |
| "at the beginning of **each** end step" | **81** | **needs vocabulary** |
| "at the beginning of **the** end step" (active player's) | **50** | **needs vocabulary** |
| "at the beginning of the **next** end step" — a **delayed** trigger | **333** | **already buildable** — `delayed` is ratified §2 vocabulary (CR 603.7) |
| the trigger sits inside a **granted/created** ability | 41 | belongs to the creating ability (§2) |
| mentions the end step but is not a trigger ("cast only during your end step") | 17 | not this family |

**1,034 cards touch the end step; 536 need new vocabulary; 333 needed none.**

The census over-counted by folding delayed triggers into the gap, and
under-counted the true end-step-trigger family by splitting it across
descriptors. Gate 4 applies to my own tools: **the measurement wins, and the
census gets corrected.** Third time this arc that a first number was wrong
(§S4 154→90→44; investigate 132→163; end-step 601→536).

## 2. The three are NOT one axis

§1 is explicit: SCOPE is *"REQUIRED the moment a scope-sibling exists."* All
three siblings exist here, with real and different game consequences that §6b
insists are not equitable:

- **your end step** — fires once per turn cycle, on your turn only. The
  value-engine shape (405 cards).
- **each end step** — fires on *every* player's end step. In a 4-player game
  that is four times as often, and it is the symmetric/one-sided distinction
  §6c retired `mass-` over (81 cards).
- **the end step** — the *active player's* end step, used by Auras keyed to
  someone else's turn (50 cards).

Merging them would repeat exactly the `mass-` error: a job-level word papering
over a printed scope difference.

## 3. RULING — vocabulary proposed

| token | cards | CR |
|---|--:|---|
| `end-step-trigger` + §6 scope (`own` / `each` / active-player) | 536 | 113.3c, 500.7 |

§2 already ratifies `upkeep-trigger`. This is its mirror and takes the same
shape. **No axes authored** — delivery-only slugs are parents (cycling ruling §5,
batch-5 D16), and the 536 members carry a very wide effect spread.

**Naming question for Captain, stated rather than assumed:** the active-player
form has no clean §6 scope token. `own` and `each` exist; "the end step" means
*whoever's turn it is*, which is closest to `active-player` — **new scope
vocabulary**, not just a new delivery token. Flagged, not invented.

## 4. Parent candidate

**`rule:end-step-payoff`** — logged, never authored. The job: *"my turn ends and
I get paid."* Under S4a it is unranked against whatever else the card is.

## 5. Standing ask — unchanged, and now larger

The pending delivery-vocabulary batch (see `BECOMES-TAPPED-RULING-2026-08-03.md`
§6), with this ruling's corrected figure:

| pending token | cards |
|---|--:|
| **self-vs-other convention** (5 trigger families at once) | **1,921** |
| `end-step-trigger` (+ scope) | **536** |
| `becomes-tapped-trigger` | 111 |
| `cycled-trigger` | 54 |
| `tapped-for-mana-trigger` | 33 |
| `becomes-untapped-trigger` | 33 |
| `cycles-a-card-trigger` | 21 |
| `cycle-or-discard-trigger` | 14 |

**One batch ruling unblocks ~2,700 cards.** Nothing else on the board comes
close per unit of Captain throughput.
