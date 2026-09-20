# Objective 6 — Card Resource Differential — Structural Revision

**Date:** 2026-09-19  
**Status:** **AUDIT-REVISED WORKING ACCOUNTING CONCEPT — NOT A FAMILY; FINAL NAME STILL SUBJECT TO NAMING AUDIT**

## 1. Revised structural status

The earlier naming correction from `Card Advantage` to **Card Resource Differential** was directionally correct because Foundry should not redefine the established Magic theory term `Card Advantage`.

The whole-vocabulary adversarial audit makes a second correction:

> **Card Resource Differential is a derived accounting fact, not a canonical semantic family/trunk.**

Canonical Foundry should preserve the underlying card identities, zones, permissions, expenditures, gains/losses, and player-relative changes. The differential is computed from those facts under an explicit comparison context.

## 2. Accounting object

The accounting unit is a **distinct underlying card-origin resource**, not:

- a permission clause;
- a spell/card copy;
- a token or generated non-card object;
- a mana resource;
- an additional execution opportunity of the same underlying card.

A card moving from hand to battlefield is still the same underlying card-origin object. Its zone changed; Foundry must not count the move itself as creation of another card resource.

## 3. Required underlying facts

Preserve at minimum:

- underlying card/resource identity where resolvable;
- owner/provenance;
- current zone/position;
- player with access/control/permission;
- card resource expended/lost/denied;
- card resource gained/recovered/newly made accessible;
- source retained vs consumed;
- `PLAY` / `CAST` / direct deployment permission;
- permission duration/window;
- categorical eligibility restrictions;
- current-action timing/land-play constraints;
- payment method / alternative cost facts;
- repeat execution facts;
- copy provenance;
- per-player before/after resource set;
- pairwise opponent-relative result where needed.

## 4. Top-library accounting

Top-Library Access can affect the derived resource set when it grants use of an underlying top card that would otherwise be inaccessible.

Working rules:

1. The current top position ordinarily exposes **one underlying card at a time**.
2. Continuous refreshability after that card leaves is a throughput/access fact, not an unbounded simultaneous resource count.
3. `CAST` access does not make a land eligible through that permission.
4. `PLAY` may cover lands, subject to ordinary land-play constraints.
5. Merely revealing/looking at the top card is not resource access.
6. A Tutor that puts a card on top does not by itself make that top card accessible.

## 5. Affordability and present actionability

The audit rejects a rule that a spell must be **presently affordable** to count as a card-origin resource.

A card in hand does not stop being a card resource because its controller lacks enough mana at this instant. The same principle applies to an otherwise valid alternate-zone permission.

Therefore separate:

- **resource/access identity** — the underlying card is available under the relevant permission/horizon; from
- **current actionability/realization** — current mana, timing, land-play allowance, targets, game restrictions, or other state permits immediate use right now.

This prevents Card Resource Differential from turning into a volatile generic `what can I cast this second?` score.

## 6. Graveyard and temporary access

If a permission newly makes an underlying graveyard/exile/top-library card available, the accessible card-resource set may change for the permission window.

However:

- moving an already-usable graveyard card to hand does not automatically create another distinct underlying resource;
- expiration of temporary permission can remove access without the card object ceasing to exist;
- shared fuel such as Underworld Breach escape cards can constrain realization without changing the identity count of the permissions/resources themselves.

## 7. Repeat-use and copies

Additional executions are separately typed.

Examples:

- Flashback can give the same underlying card another execution opportunity;
- Retrace can enable repeated casts of the same underlying card;
- Rebound schedules another cast opportunity;
- Mnemonic Deluge can create three spell copies from one graveyard card;
- Isochron Scepter repeatedly copies an imprinted card.

None of those facts authorizes counting each later execution or copy as another underlying card-origin resource.

## 8. Generated objects remain separate

Creature tokens, Treasures, Clues, Maps, Powerstones, token copies, and other generated game objects are not silently converted into Card Resource Differential units.

Record their actual resource/object types.

This does not dispute broad Magic theory uses of `card advantage`; it preserves a narrower typed Foundry accounting layer.

## 9. Multiplayer

Retain per-player and pairwise facts. Useful reduction states remain:

- positive/nonnegative relative result;
- parity;
- negative/nonpositive relative result;
- mixed vector where some opponent-relative comparisons are positive and others negative.

Do not replace the vector with an average that hides distribution.

## 10. Relationship to Card Advantage

`Card Advantage` remains established community/theory vocabulary. `Virtual Card Advantage` and `Card Quality` are even more context-sensitive.

Those terms belong in educational/strategic reasoning over the canonical resource facts, not as replacements for the typed mechanical accounting.

## 11. Remaining OPEN item

Whether the UI should separately expose a `currently actionable` card-resource view remains open.

If future evidence justifies it, it must be derived from the same permission/timing/payment facts. It must **not** resurrect the rejected `Card Access Differential` concept under a new name.

## 12. Control boundary

No S16B freeze, corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized here.

> **PRESERVE TRUTH, NOT PLUMBING.**
