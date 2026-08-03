# Membership ratification packet — 2026-08-02

Three Captain decisions from this session need **axis names** before they can
execute. New vocabulary is a Captain ratification, not a typo fix (grammar §10
rule 3), so nothing below has been written to the codebook.

Executed already (for context): the any-damage split
(`docs/DAMAGE-DELIVERY-RULING-2026-08-02.md`) and the any-damage-to-creature
split. Codebook sha256 `4c72ccc69519f355d25e6513…`, 310 active axes.

---

## 0. A standing rule these three decisions all imply

Captain ratified, on Blizzard Specter, that **a modal card holds membership on
every mode's axis**. The Riptide Entrancer answer asks for the same shape from
a different direction: one card, decomposed onto a delivery axis, an effect
axis, a cost-condition axis, and the compound.

Proposed as a standing rule, since it governs far more than these two cards:

> **A card holds membership on every axis it genuinely satisfies.** Modal
> modes each earn their axis; a single ability decomposes onto its compound
> slug *and* the facet axes it is built from. Membership is not exclusive.

This is consistent with grammar §1 ("Multi-ability cards get multiple tags,
never fused slugs", M8 / batch-6 D3) but extends it: §1 covers multiple
*abilities*, this covers multiple *axes per ability*.

**Needs ratification** — it has a real cost. Member counts stop being a
partition of the corpus, so any consumer that assumes "one card, one home"
must be checked. It also inflates every member count, which interacts with the
`membership-grew-since-probe` alarm.

---

## 1. Riptide Entrancer — 4 axes

> "Whenever this creature deals combat damage to a player, you may sacrifice
> it. If you do, gain control of target creature that player controls. (This
> effect lasts indefinitely.)"

Currently sits on `rule:combat-damage-to-player-discard`, which it contradicts
outright — it never discards.

| # | proposed slug | scope | definition | seeds |
|---|---|---|---|---|
| 1 | `rule:permanent-control-theft` | `opponent-stuff` | Permanently gains control of a permanent an opponent controls; the effect lasts indefinitely rather than expiring at end of turn. | Riptide Entrancer |
| 2 | `rule:combat-damage-to-player-permanent-control-theft` | `opponent-stuff` | Whenever this creature deals combat damage to a player, its controller may permanently gain control of a creature that player controls. | Riptide Entrancer |
| 3 | `rule:optional-self-sacrifice-in-trigger` | `self` | A triggered ability offers its controller the option to sacrifice the source as a condition of the effect ("you may sacrifice it. If you do, …"). Distinct from an activation cost — the sacrifice happens on resolution, not on activation. | Riptide Entrancer |

**Why #3 is not `rule:activated-ability-costs-self-sacrifice`** (44 members):
that axis is an *activation cost* (CR 113.3b, cost left of the colon).
Riptide Entrancer's sacrifice occurs during resolution of a triggered ability
— grammar §9's cost-vs-effect law makes this a hard boundary, and filing it as
a cost would violate the same law that says "life/sacrifice/discard occurring
in resolution text NEVER satisfies a cost slug."

**Why #1 is not `rule:temporary-control-theft`:** Riptide Entrancer's reminder
text says "(This effect lasts indefinitely.)" — the opposite claim. If #1 is
ratified, `temporary-control-theft` should get a definition edit making its
duration explicit, so the pair reads as a deliberate distinction.

Open: does #1 want a `-creature` object slot (`permanent-control-theft-creature`)?
Riptide Entrancer steals a creature specifically, but the axis name says
permanent. §5 says OBJECT is omitted when the effect verb binds it — it does
not here.

## 2. Blizzard Specter — the bounce mode

> "choose one — • That player returns a permanent they control to its owner's
> hand. • That player discards a card."

Stays on `rule:combat-damage-to-player-discard` (ratified). Under the standing
rule in §0 it also earns the bounce mode's axis, which does not exist. Every
existing bounce axis is the wrong shape — `targeted-bounce-creature`,
`etb-bounce-other-creature` etc. are all **you** bouncing a chosen target.
Here the **opponent chooses and returns their own permanent**.

| proposed slug | scope | definition | seeds |
|---|---|---|---|
| `rule:combat-damage-to-player-forced-owner-bounce` | `opponent-stuff` | Whenever this creature deals combat damage to a player, that player returns a permanent they control to its owner's hand — the affected player chooses, not the controller. | Blizzard Specter |

The "affected player chooses" distinction is real for deck-building: a forced
self-bounce cannot be aimed, so it never answers a specific threat.

## 3. `combat-damage-to-player-loot` — 15 members, 3 ways

Classified against full oracle text. Looting is draw-**then**-discard (§4
ratified verb list), so only 7 members qualify.

**STAY on `-loot` (7)** — all genuinely draw then discard, conditional
discards included:
April, Reporter of the Weird · Abomination of Gudul · Moon-Circuit Hacker ·
Assassin Gauntlet · Shoreline Looter · Daring Saboteur · Jace, Cunning Castaway

**MOVE to a draw-only axis (5)** — draw, no discard:

| proposed slug | scope | definition | seeds |
|---|---|---|---|
| `rule:combat-damage-to-player-draw` | `self` | Whenever this creature deals combat damage to a player, its controller draws one or more cards, with no discard attached. | Beast Erudite Aerialist · Ninja of the Deep Hours · Fear of Failed Tests · Willie Lumpkin · Surrakar Spellblade |

**MOVE to their real effects (3)** — these never draw at all:

| card | text | proposed slug |
|---|---|---|
| Prowler, Misguided Mentor | "put a +1/+1 counter on another target creature you control" | `rule:combat-damage-to-player-plus1-counter-on-other-creature` |
| Maelstrom Archangel | "you may cast a spell from your hand without paying its mana cost" | `rule:combat-damage-to-player-free-cast` |
| Sword of Body and Mind | "create a 2/2 green Wolf creature token and that player mills ten cards" | `rule:combat-damage-to-player-mill-opponent` **+** `rule:create-token-creature` (compound → two tags, §1) |

### Two sub-findings inside this axis

1. **Surrakar Spellblade scales.** "you may draw X cards, where X is the number
   of charge counters on it." Under §7 that is
   `-draw-scales-with-charge-counters`, not plain `-draw`. Ratify a scaling
   sibling, or accept it on `-draw` and let §7 normalization catch it later?
2. **Jace, Cunning Castaway's delivery is wrong.** "+1: Whenever one or more
   creatures you control deal combat damage to a player this turn, draw a card,
   then discard a card." The trigger is *created by a loyalty ability* — §2
   ratifies `loyalty` as its own DELIVERY value and says planeswalker abilities
   are "always marked `loyalty`, never `activated`." Its loot is real, but its
   delivery is `loyalty`-created-delayed, not `combat-damage-to-player`. Left
   in place pending ruling; this is the same class as the 39 ETB findings.

**`rule:combat-damage-to-player-free-cast` has a second member waiting.**
Kotis, the Fangkeeper ("Whenever Kotis deals combat damage to a player, exile
the top X cards of their library … You may cast any number of spells … without
paying their mana costs") is **not in the codebook at all** — it would seed
this axis alongside Maelstrom Archangel at the corpus pass.

---

## What executes on ratification

7 new axes, ~11 member moves, 1 standing rule, 2 definition edits. All through
`experiments/foundry_membership_move.py` with a declared spec — member
conservation, determinism ×2, backup with readback, lint and sweep either side.
