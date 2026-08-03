# "WHENEVER YOU ATTACK" — RULING (2026-08-03)

Sixth ruling in the 2026-08-03 shape series, at Captain's direction: *"then take
player-attacks next."* **159 ability lines / 158 cards.**

Gate-3 dossier run on `player-attacks-trigger`, `you-attack-trigger`,
`attacks-trigger`: **no prior ruling on any of them, in any status, and none is
in the codebook.** Clean ground — unlike `end-step-trigger` and
`saga-chapter-progression`, both of which turned out to be killed.

**Zero API calls.**

---

## 1. Attacking is a PLAYER's action, and the CR is unambiguous

> **CR 508.1** — *"First, **the active player declares attackers**. This
> turn-based action doesn't use the stack."*
>
> **CR 508.1a** — *"**The active player chooses** which creatures that they
> control, if any, will attack."*

The creature does not attack of its own accord; **a player attacks with it**.
So "whenever you attack" names the *player's declaration* — a different event
subject from "whenever this creature attacks", even though CR 508.1m fires both
at the same moment:

> **CR 508.1m** — *"Any abilities that trigger on attackers being declared
> trigger."*

**Same timing, different subject.** That is precisely the §6b case: adjacent
vocabulary is not equivalent vocabulary.

---

## 2. The proof that these cannot share a token

`attack-trigger` is §2's *"whenever **~** attacks"* — the source is the
attacking creature. Under §6a that claim is binding, and **it is false for most
of this population's edge**:

| card | type | prints |
|---|---|---|
| **Cosmic Cube** | **Artifact** | "Whenever you attack, look at the top six cards…" |
| **Sparring Regimen** | **Enchantment** | "Whenever you attack, put a +1/+1 counter on target attacking creature" |
| **Undercellar Sweep** | **Enchantment** | "Whenever you attack, if you or a player you're attacking has the…" |
| **Gideon, the Oathsworn** | **Planeswalker** | "Whenever you attack with two or more non-Gideon creatures…" |
| **Leader's Talent** · **Cool but Rude** | **Enchantment — Class** | "Whenever you attack, …" |

**These sources cannot attack.** An artifact, an enchantment and a planeswalker
are not creatures and are never declared as attackers, yet they carry the
trigger. Folding them into `attack-trigger` would make the codebook assert that
each of them attacked.

Two further consequences that matter for deck-building, both printed:

- **It fires ONCE per combat**, on the declaration, no matter how many creatures
  attack. `attack-trigger` is keyed to one specific creature attacking.
- **The source need not attack even when it is a creature.** A creature with
  "whenever you attack" that stays home still triggers, provided something else
  attacked.

---

## 3. RULING — one token proposed

| token | lines | cards | CR |
|---|--:|--:|---|
| **`player-attack-trigger`** | 159 | **158** | 508.1, 508.1a, 508.1m |

Measured shapes, zero unclassified:

| printed | lines |
|---|--:|
| "whenever **you attack**" | 106 |
| "whenever **you attack with** «qualifier»" | 53 |

### 3a. The "with «qualifier»" half is a QUALIFIER, not a second token

The 53 carry wildly different restrictions — "with one or more **Lizards**"
(Hired Claw), "with **two or more** creatures" (Eiganjo Dynastorian), "with a
creature **an opponent owns**" (Nihiloor), "with two or more **non-Gideon**
creatures". These restrict *which declaration counts*, not *what kind of event
it is*. The delivery is identical; §1's QUALIFIER slot is the home. Minting a
token per restriction would be the `targeted-<action>-<class>` lattice all over
again, and that is a grammar family, not delivery vocabulary.

### 3b. Why not `you-attack-trigger`

§6d ratified `you-control` / `you-own` earlier today, making a leading `you-`
read as a **SCOPE** token about the controller. Reusing it as a DELIVERY subject
marker would blur two slots that §1 keeps in fixed order. **`player-`** is
already §5 OBJECT vocabulary and reads unambiguously as *the subject is a
player, not the source*.

### 3c. Why §2a's prefixes do not apply

`other-` / `any-` mark **which permanent** is the trigger subject. Here the
subject is a **player**, which is not in that domain at all. So this is a
genuinely new token rather than a composition — checked, per §2c's standing
instruction to look at §2a before minting.

### 3d. No scope slot yet — and the condition for needing one

Measured: **zero** cards in this population print "whenever **a player**
attacks" or "whenever **an opponent** attacks". Every one is "you". So no §6
scope token is required today. **If an opponent-side form ever prints, §1 makes
SCOPE mandatory the moment a scope-sibling exists** — recorded here so that is
caught rather than rediscovered.

---

## 4. Not authored — delivery-only slugs are parents

Per the cycling ruling §5 / batch-5 D16. The 158 cards carry a wide effect
spread; `player-attack-trigger-<effect>` children are a corpus pass.

**Parent candidate, logged not authored:** `rule:attack-payoff` — *"declaring an
attack is itself the engine."* Note under S4a it sits unranked beside whatever
else the card is.

---

## 5. The defending mirror is still unnamed

`is-attacked` — **38 lines / 37 cards**, "whenever ~ is attacked" and "whenever
a player attacks you". It is the same event from the other side of the table
(CR 508.1b names the defending player, planeswalker or battle), and it has no
token. Logged as the natural sibling; not bundled, because the defending side
carries its own scope question (attacked *player* vs *planeswalker* vs
*battle*) that this ruling does not answer.
