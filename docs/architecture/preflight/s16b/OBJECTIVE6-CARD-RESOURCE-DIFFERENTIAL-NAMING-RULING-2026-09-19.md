# Objective 6 — Card Resource Delta — Freeze-Candidate Accounting Name

**Date:** 2026-09-19  
**Former working name:** `Card Resource Differential`  
**Status:** **AUDIT-REVISED DERIVED ACCOUNTING FACT / PROPOSED FINAL NAME — NOT FROZEN**

## 1. Naming decision

The global naming audit proposes **Card Resource Delta** as the final name for Foundry's narrower card-origin accounting projection.

Reasons:

- preserves the useful **CRD** acronym;
- shorter than `Card Resource Differential`;
- `delta` accurately describes before/after resource change;
- opponent-relative comparisons can be represented explicitly as pairwise/relative deltas rather than overloading the concept name;
- remains distinct from established Magic theory language `Card Advantage`.

## 2. Structural status

> **Card Resource Delta is a derived accounting fact, not a canonical semantic family/trunk.**

Canonical Foundry preserves underlying card identities, zones, permissions, expenditures, gains/losses, and player-relative changes. CRD is computed from those facts under an explicit comparison context.

## 3. Accounting object

The accounting unit is a **distinct underlying card-origin resource**, not:

- a permission clause;
- a spell/card copy;
- a token or generated non-card object;
- a mana resource;
- an Additional Execution opportunity of the same underlying card.

A card moving from hand to battlefield is still the same underlying card-origin object. Its zone changed; no second card resource was created.

## 4. Required underlying facts

Preserve at minimum:

- underlying card/resource identity where resolvable;
- owner/provenance;
- current zone/position;
- player with access/control/permission;
- resource expended/lost/denied;
- resource gained/recovered/newly made accessible;
- source retained vs consumed;
- `PLAY` / `CAST` / Direct Placement permission;
- Permission Window;
- categorical eligibility restrictions;
- current-action timing/land-play constraints;
- Payment Method / Alternative Cost facts;
- Additional Execution facts;
- copy provenance;
- per-player before/after resource set;
- pairwise opponent-relative result where needed.

## 5. Top-Library Access accounting

Top-Library Access can affect Card Resource Delta when it grants use of an underlying top card that would otherwise be inaccessible.

Working rules:

1. The current top position ordinarily exposes **one underlying card at a time**.
2. Continuous refreshability after that card leaves is access throughput, not an unbounded simultaneous resource count.
3. `CAST` does not make a land eligible through that permission.
4. `PLAY` may cover lands subject to ordinary land-play constraints.
5. Merely revealing/looking at the top card is not resource access.
6. A Tutor that puts a card on top does not by itself grant Top-Library Access.

## 6. Affordability and current actionability

A spell does **not** need to be presently affordable to remain a card-origin resource.

A card in hand does not vanish from the player's resources because they lack enough mana this instant. Apply the same principle to otherwise valid alternate-zone permissions.

Separate:

- **resource/access identity** — the underlying card is available under the relevant permission/window; from
- **current actionability/realization** — current mana, timing, land-play allowance, targets, restrictions, or other state permits immediate use.

This keeps CRD from becoming a volatile `what can I cast this second?` score.

## 7. Graveyard and temporary access

If a permission newly makes an underlying graveyard/exile/top-library card available, the accessible card-resource set may change for the Permission Window.

However:

- moving an already-usable graveyard card to hand does not automatically create another distinct resource;
- expiration of permission can remove access without the card object ceasing to exist;
- shared fuel can constrain realization without changing underlying resource identity.

## 8. Additional Execution and copies

Additional Execution remains separately typed.

Flashback, Retrace, Rebound, Mnemonic Deluge, Isochron Scepter, and similar mechanics may create later or repeated executions. They do not authorize counting each execution/copy as another underlying card-origin resource.

## 9. Generated objects remain separate

Creature tokens, Treasures, Clues, Maps, Powerstones, token copies, and other generated game objects are not silently converted into Card Resource Delta units.

Record their actual resource/object types under the Typed Resources model.

## 10. Multiplayer

Retain per-player and pairwise deltas. A compact projection may report:

- positive;
- parity;
- negative;
- mixed where pairwise results differ.

Do not hide distribution behind an opaque average.

## 11. Relationship to Card Advantage

`Card Advantage` remains established community/theory vocabulary. `Virtual Card Advantage` and `Card Quality` are even more context-sensitive.

Those belong in educational/strategic reasoning over the canonical resource facts, not as replacements for CRD.

## 12. Remaining OPEN item

Whether the UI should separately expose a `currently actionable` view remains open.

If future evidence justifies it, derive it from Card Use Permission, timing, land-play, payment, and state facts. Do not resurrect the rejected `Card Access Differential` under another name.

## 13. Control boundary

`Card Resource Delta` is a freeze-candidate name, not a freeze. No corpus reclassification, implementation acceptance, merge, accepted-head/main movement, AQ4 resumption, Bridge activation, or Step6 is authorized.

> **PRESERVE TRUTH, NOT PLUMBING.**
