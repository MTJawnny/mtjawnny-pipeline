# BECOMES-TAPPED / BECOMES-UNTAPPED — RULING (2026-08-03)

Second ruling in the 2026-08-03 shape series, after `CYCLING-RULING-2026-08-03.md`.
Gate-3 dossier run on `becomes-tapped`, `tapped-trigger`, `becomes-untapped`:
**no prior ruling on any, in any status.**

## 1. The CR anchor makes this sharper than it looks

**CR 603.2e** — *"Some trigger events use the word 'becomes'… An ability that
triggers when a permanent 'becomes tapped' or 'becomes untapped' **doesn't
trigger if the permanent enters the battlefield in that state.**"*

With the CR's own example: *"An ability that triggers when a permanent 'becomes
tapped' triggers only when the status of a permanent that's **already on the
battlefield** changes from untapped to tapped."*

So three printed things that look adjacent are mechanically distinct, and §6b
forbids collapsing them:

| printed | what it is | already in the codebook? |
|---|---|---|
| "becomes tapped" | a **trigger event** on a state *change* | **no vocabulary** |
| "is tapped" / "tapped creature" | a **state check** | partly (`tapped` is §14 Q5 vocabulary) |
| "enters tapped" | a **replacement effect** (CR 614) | yes — `rule:enters-tapped`, `rule:imposes-enters-tapped` |

A card entering tapped **never** fires a becomes-tapped trigger. That is exactly
the kind of "adjacent vocabulary is not equivalent vocabulary" case §6b names.

## 2. The population — 179 cards

| shape | cards |
|---|--:|
| **becomes tapped — SELF** ("whenever ~ becomes tapped") | **65** |
| **becomes tapped — OTHER** (enchanted/equipped/another permanent) | **46** |
| **tapped for mana** — a *narrower, different* trigger | **33** |
| **becomes untapped — SELF** (the `Inspired` ability-word family) | **27** |
| becomes untapped — OTHER | 6 |
| granted / not the mechanic | 2 |

### `tapped for mana` is not `becomes tapped`
33 cards print "Whenever enchanted land **is tapped for mana**". Tapping for mana
does make the land become tapped, but the trigger condition is narrower — it
requires a mana ability to have been activated. Manually tapping the land for a
non-mana cost fires `becomes tapped` and **not** `tapped for mana`. Separate
axis, not a synonym.

### `Inspired` is an ability word, not a rule
The becomes-untapped SELF family is almost entirely `Inspired`. **`Inspired` does
not appear in the Comprehensive Rules** — checked, zero hits — so it is an
ability word (CR 207.2c: flavour, no rules meaning). It names the family for
players; the axis takes the printed trigger, not the ability word.

## 3. Two members the naive scan got wrong — recorded because they generalize

- **Ambassador of Evendo** prints "…perpetually gains **"Whenever this land
  becomes tapped, draw a card."**" — the trigger is inside a **granted** ability.
  Per §2's created-ability rule the card does **not** deliver a becomes-tapped
  trigger; it delivers a landfall trigger that creates one. A scan that does not
  check quoted spans puts it in the wrong family, and mine did until it was
  hand-read.
- **Agent Maria Hill** prints "becomes tapped **to pay a teamwork cost**" — a
  *restricted* becomes-tapped. Under §6a the restriction is printed, so it is a
  distinct shape, not decoration.

## 4. RULING — vocabulary ratified, axes NOT authored

Proposed as new DELIVERY vocabulary (§2), each anchored to CR 603.2e:

| token | cards |
|---|--:|
| `becomes-tapped-trigger` | 65 self / 46 other |
| `becomes-untapped-trigger` | 27 self / 6 other |
| `tapped-for-mana-trigger` | 33 |

**No axes were authored, deliberately.** These are delivery-only slugs, and the
cycling ruling §5 established the precedent (itself from batch-5 D16): a
delivery-only slug is a **parent**, and its children are `<delivery>-<effect>`.
The 65 self members carry ~30 different effects — authoring those is a corpus
pass, not this ruling.

**These three tokens need Captain ratification before any child instantiates**
(§10.3: unknown tokens halt; new vocabulary is a ratification). They join
`end-step-trigger` and the cycling trigger family in one pending vocabulary
batch — see §6.

## 5. Parent candidates — logged, never authored

- **`rule:becomes-tapped-trigger`** — parent over its effect children.
- **`rule:untap-matters`** — the `Inspired` family plus vigilance-adjacent and
  untapper payoffs. Genuinely a JOB parent (§6b): "my creatures untapping is my
  engine" is a deck role, not a printed shape.

## 6. THE STANDING ASK — one vocabulary batch, not five rulings

Every ruling this session ends at the same wall. Delivery vocabulary now
pending, with corpus-wide card counts from
`DELIVERY-GAP-CENSUS-2026-08-03.md`:

| pending token | cards |
|---|--:|
| **self-vs-other convention** (5 trigger families at once) | **1,921** |
| `end-step-trigger` | 601 |
| `becomes-tapped-trigger` | 111 |
| `cycled-trigger` (CR 702.29c) | 54 |
| `tapped-for-mana-trigger` | 33 |
| `becomes-untapped-trigger` | 33 |
| `cycles-a-card-trigger` (702.29d) | 21 |
| `cycle-or-discard-trigger` (702.29d) | 14 |

**One batch ruling unblocks ~2,800 cards.** That is a better use of Captain
throughput than any single mechanic, and it is the same argument the CR-coverage
packet made for the 701 action names — ratify the *vocabulary*, and nodes
self-instantiate per §11.
