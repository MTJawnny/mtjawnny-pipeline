# Any-damage vs combat-damage — Captain ruling, 2026-08-02

## The ruling (Captain-ratified 2026-08-02)

> **"Any damage deserves its own axis rather than combat damage."**

A trigger that fires on **any** damage is a different mechanism from one that
fires only on **combat** damage, and the two must not share an axis. The
`combat-damage-to-*` prefix is a claim that the trigger is combat-restricted;
a card reading "whenever ~ deals damage to an opponent" does not make that
claim and must not be filed as though it does.

This is a DELIVERY ruling and sits alongside the closed DELIVERY vocabulary in
`CODEBOOK-NAMING-GRAMMAR.md` §1/§2.

**Why it matters mechanically, not just nominally:** an any-damage trigger
fires off pingers, direct-damage spells, fight effects and noncombat sources.
A deck built around `combat-damage-to-player-discard` wants evasive creatures;
one built around any-damage discard wants damage sources of any kind. Merging
them makes the axis useless for exactly the deck-building question it exists to
answer.

## How the ruling was reached

The `combat-damage-to-player-*` family was surfaced by the definition-drift
audit (`docs/DEFINITION-DRIFT-AUDIT-2026-08-02.md`, check C2) as a delivery
mismatch. **Captain corrected the audit on two points:**

1. Keen Sense was reported under the delivery finding, but its real defect is
   the **effect** — it reads "you may draw a card" on an axis suffixed
   `-discard`. The audit had no effect check at all. **Check C3 was added in
   response** and immediately found 10 further axes with the same class of
   defect, including `rule:etb-scry` holding three cards that **surveil**, and
   `rule:combat-damage-to-player-loot` holding a +1/+1-counter payoff, a
   free-spell payoff, and a mill payoff.
2. The remedy is not to broaden `combat-damage-` to cover any damage, but to
   give any-damage its own axis.

## Affected members — `rule:combat-damage-to-player-discard` (9 members)

| card | delivery | effect | verdict |
|---|---|---|---|
| Riptide Pilferer | combat | discard | **stays** |
| Sedraxis Specter | combat | discard | **stays** |
| Larceny | combat | discard | **stays** |
| Rakdos Ringleader | combat | discard (at random) | **stays** |
| Blizzard Specter | combat | modal — bounce **or** discard | stays, modal flag |
| Zhang Liao, Hero of Hefei | **any damage** | discard | → any-damage axis |
| Hypnotic Specter | **any damage** | discard (at random) | → any-damage axis |
| Keen Sense | **any damage** | **draw** | → any-damage **draw** axis |
| Riptide Entrancer | combat | **gain control of a creature** | → neither; wrong effect entirely |

Note Zhang Liao and Hypnotic Specter share both delivery *and* effect, so they
form a clean two-member any-damage discard axis. Keen Sense and Riptide
Entrancer each leave on effect grounds and need separate homes.

## Proposed axes — NOT ratified, awaiting Captain

Proposed, in the ratified DELIVERY-then-EFFECT slot order (§1):

| proposed slug | seed members | definition sketch |
|---|---|---|
| `rule:any-damage-to-player-discard` | Zhang Liao, Hypnotic Specter | Whenever a creature deals damage of any kind to an opponent, that player discards a card. |
| `rule:any-damage-to-player-draw` | Keen Sense | Whenever a creature deals damage of any kind to an opponent, its controller may draw a card. |

Open questions for ratification:

1. **Is `any-damage-` the right prefix word?** It is not currently in the
   closed DELIVERY vocabulary (§2), so adopting it is a vocabulary
   ratification, not a typo fix — per §10 rule 3, new vocabulary halts loudly
   for exactly this reason. Alternatives: `damage-to-player-` (unprefixed,
   letting `combat-` be the marked case) or `noncombat-or-combat-damage-`
   (accurate, unwieldy).
2. **Does the mirrored `-to-creature-` family need the same split?**
   `rule:combat-damage-to-player-triggers-self-plus1-counter` already holds
   Spiritmonger and Strax, both of which deal damage **to a creature** — a
   third distinct delivery, and evidence the split generalizes.
3. **Where does Riptide Entrancer go?** Its effect (sacrifice self, gain
   control of target creature) matches no current axis suffix.
4. **Is Blizzard Specter's modal text enough** to hold membership on a
   `-discard` axis when discard is one of two modes? Bears on the general
   modal-membership question, not just this axis.

## Status — EXECUTED 2026-08-02

Captain ratified the `any-damage-` prefix and ordered the split. Both are done.

| | before | after |
|---|---|---|
| codebook sha256 | `d0b1183fc155f13e7b1ae025…` | `2c766ca2fab3300d836d18fd…` |
| active axes | 307 | 309 |
| members (all) | 7,864 | **7,864** — members move, none created or lost |
| `combat-damage-to-player-discard` | 9 members | 6 |
| `rule:any-damage-to-player-discard` | — | 2 (Zhang Liao, Hypnotic Specter), scope `opponent-stuff` |
| `rule:any-damage-to-player-draw` | — | 1 (Keen Sense), scope `self` |
| lint | clean | clean |
| sweep blocking | 6 | 6 |

Executor: `experiments/foundry_any_damage_split.py`, under the backup law
(`backups/codebook.pre-any-damage-split.20260802-172906.json`, verified by
readback) with determinism ×2. Members moved carrying their assertions — and
therefore their evidence quotes — verbatim; nothing was re-evidenced.

The source definition was corrected in the same pass: it read "deals damage to
an opponent", the any-damage wording this ruling forbids under a `combat-`
prefix.

`any-damage-to-player` is now in the closed DELIVERY vocabulary
(`CODEBOOK-NAMING-GRAMMAR.md` §2, CR 120.3), with the standing rule that
**`combat-` is a restriction, not decoration.**

Re-running the drift audit confirms the fix: the C2 delivery finding on
`combat-damage-to-player-discard` cleared entirely (19 → 18 C2 findings). Its
only remaining finding is Riptide Entrancer, which is open question 3 below —
an effect defect, not a delivery one.
