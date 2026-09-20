# Objective 6 — Cantrip and Temporary Exile Access Ruling

**Date:** 2026-09-19  
**Status:** **CAPTAIN-APPROVED CANTRIP REALIGNMENT + CAPTAIN-APPROVED EXILE-ACCESS DURATION STRUCTURE; CARD-ADVANTAGE DERIVATION REMAINS FACT-BASED**  
**Scope:** Card Access semantic refinement only. No S16B freeze or implementation authorization.

## 1. Cantrip — Captain ruling

Foundry should use the established Magic/community meaning of **Cantrip** rather than the prior narrower Foundry-specific predicate.

The earlier requirements that a Cantrip must have mana value 2 or less and must provide an additional independent function are withdrawn.

Working Foundry meaning:

> **Cantrip** — a card whose own normal operation replaces its card expenditure by drawing a card, typically by carrying a `draw a card` rider or equivalent self-replacing draw operation.

Important consequences:

- no universal mana-value ceiling;
- no requirement for a second independent function;
- permanents and nonpermanents may qualify when their own normal operation replaces the spent card with a draw;
- a card may be both Cantrip and Card Advantage when, after replacement, the originating card leaves behind independently useful card-origin material or otherwise produces a positive card-resource differential;
- Cantrip remains distinct from non-draw replacement methods such as graveyard recovery, bounded extraction, or exile access.

Established Magic usage is intentionally preferred here so Foundry does not redefine a familiar public term in a surprising way.

## 2. Temporary exile access — explicit access mode

Foundry should represent **temporary exile access** as a lower-level Card Access mode distinct from literal draw.

Core operation:

> move/reveal card(s) into exile -> grant permission to play/cast those card(s) for a defined duration.

The familiar Wizards/R&D term **Impulsive Draw** may be retained as an alias/pattern, but the semantic substrate should store the actual access facts.

## 3. Duration is load-bearing

At minimum, distinguish these access windows:

### 3.1 Current-turn access

Examples use language such as:

> `You may play that card this turn.`

Properties:

- access expires at the end of the current turn;
- normal timing restrictions still apply unless separately overridden;
- unused cards generally remain exiled after permission expires;
- realization is sensitive to how much playable time and mana remain in the current turn.

### 3.2 Through-end-of-next-turn access

Examples use language such as:

> `You may play cards exiled this way until the end of your next turn.`

Properties:

- access survives through the current turn and the controller's next turn;
- the player ordinarily receives an additional untap/draw/main-phase sequence before permission expires;
- this creates a longer factual access horizon and more ordinary legal opportunities to use the exiled card;
- Wizards design commentary explicitly notes that extending access through the next turn increases the chance that the player has sufficient mana to cast the card.

### 3.3 Other durations

The substrate must not hard-code only the two patterns above. Also preserve:

- until a stated future event;
- while a source remains on the battlefield;
- indefinitely while the card remains exiled;
- once-per-turn or other recurring permissions;
- one-shot permission tied to resolution;
- permissions tied to a linked source/object.

## 4. Required exile-access coordinates

Preserve at least:

- source zone;
- access zone (`exile`);
- number of cards granted access;
- visibility / face-up vs face-down;
- `play` vs `cast` permission;
- whether lands may be played;
- eligible card-type restrictions;
- duration / expiration point;
- whether normal timing restrictions still apply;
- whether normal mana costs are paid;
- any alternate-payment or free-cast permission;
- whether unused cards remain exiled;
- whether permission is source-dependent after creation;
- opportunity window remaining when permission is created.

## 5. Card Advantage boundary — duration alone does not decide membership

No durable prior ruling was found establishing the categorical rule:

- `this turn` = never Card Advantage;
- `until end of next turn` = always Card Advantage.

Do not invent that as historical authority.

The correct factual decomposition is:

1. **Card-access quantity** — how many additional usable card resources are exposed/granted.
2. **Source expenditure / retention** — whether a card resource was spent to obtain that access and whether the source remains independently useful.
3. **Access duration** — how long the permission exists.
4. **Legal opportunity** — whether ordinary timing/play restrictions permit actual use during the window.
5. **Realized use** — whether the card was ultimately played/cast before expiration.

Therefore:

> **A longer exile-access window increases opportunity to realize the granted access, but duration by itself is not the definition of Card Advantage.**

Current-turn temporary access can still constitute usable card-resource access while the permission is live. Next-turn-spanning access is mechanically more persistent and normally offers more opportunities to convert that access into played spells/lands.

The canonical layer should report those facts without judging one duration as `good` or `bad`.

## 6. Interaction with future realization modeling

The later realization/deck-context layer may quantify facts such as:

- remaining mana when current-turn access is created;
- number of remaining main phases / legal cast windows;
- probability the exiled card is castable before expiration;
- probability of reaching the next turn;
- mana available after untap;
- land-play availability;
- expected fraction of exiled cards used before expiration.

This is where the practical difference between `this turn` and `until the end of your next turn` becomes quantitatively important.

## 7. Relationship to other Card Access concepts

Temporary exile access is not automatically:

- literal Draw;
- Card Filtering;
- bounded extraction;
- Tutor;
- Card Advantage.

It may overlap those concepts when the originating effect independently satisfies their predicates.

Examples:

- a bounded sample may place a selected card into exile with temporary play permission: bounded extraction + temporary exile access;
- a retained permanent may repeatedly exile top cards for temporary access: temporary exile access + potentially Card Advantage / Card Engine depending on independent predicates;
- a spell may exile multiple cards for temporary access: Card Advantage depends on the resulting card-resource differential, while access duration remains a separate coordinate.

## 8. Control boundary

This ruling does **not** authorize:

- S16B freeze;
- broad corpus execution;
- implementation acceptance;
- merge;
- accepted-head or `main` movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6.

The governing principle remains:

> **PRESERVE TRUTH, NOT PLUMBING.**