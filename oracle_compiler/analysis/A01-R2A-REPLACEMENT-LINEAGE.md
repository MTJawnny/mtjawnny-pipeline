# A01-R2A — replacement-event lineage: V1 P0.6 seam audit (R2-A)

Wave `A01.ORACLE-COMPILER-ROUND2-SEAM-AUDITS`, unit A01-R2A, under Issue #1
checkpoint 5984331292, task 5977804389. Pinned to oracle-compiler-interface/3
(`oracle_compiler/INTERFACES.md` blob 119778a68c0e4e8378f0a117b7c22884ec5eda4b at
the wave's base). This document decides no law and mints nothing: it reads the
R2-A population, states what each member requires, and records which existing
structure carries it. Every gap is handed to the Captain as a question.

## Input

The hand-off rule was followed: the existing artifact was not trusted;
`python3 experiments/oracle_ingest/a01_seams.py --verify` ran first and exited 0
("every embedded hash is current (17 files)"), so it was not regenerated.

seams.json sha256: `43c87c240b8628a28dfe16e71c9c6039e1d5f78724208c363339f8dde106a7ec`

Population: 1013 member clauses in 80 classes (561 in 35 would-classes, 452 in
45 no-would classes); scope is CR 614.1a clauses printing the quoted word only
(the 614.1b-e forms and CR 616 ordering are not audited, so nothing here covers
them). Members are written as four-coordinate addresses (oracle_id, face,
paragraph, clause); no card is named.

## Method

CARDS FIRST. Every READ POSITION of every class and all four recall controls
were read first, and the required truth of each class was written from those
readings (next section) before any structure was consulted. Then every
remaining member was read too, so that no cell rests on inference: in every
ledger row `read` equals `members`, every member is listed under `## Reads`,
and no row needs the 'inferred from' rule. Each member was read over its clause
and its paragraph tail as seams.json records them, beside the preceding clauses
of its paragraph (or the preceding paragraph) where the 'instead' modifies
earlier text.

A class whose members do not share one cell per truth item is SPLIT; parts are
member lists under `## Splits`, never averages. Two cells vary inside classes:
A2 (whether every replacing instruction has its H-REGION region), and, inside
no-would classes, A1/A4 (whether the 'instead' modifies an earlier printed
instruction, or replaces an event printed only as an "instead of" phrase or a
rules event). One would-class member is a printed-modification member and is a
part of its own.

The truth items are the five the command defines verbatim (A1-A5). Reader
classifications used below:

- **would-class member** — the 'instead' replaces the would-be event named by
  'would <verb>' (CR 614.1a, 614.6: "If an event is replaced, it never happens").
- **N1 (printed-modification) member** — a member, no-would or not, whose
  'instead' modifies an instruction printed earlier on the card (kicker, gift,
  ability-word, Opus, modal "choose both", "countered this way" forms). The
  reader reads these as CR 608.2c's case ("later text on the card may modify the
  meaning of earlier text"); whether CR 614.1a also makes each a replacement
  effect is a Captain question (Q3). They stay members.
- **N2 (would-less replacement) member** — a no-would member whose 'instead'
  replaces an event that is not a printed instruction of the card: an event
  printed only as an "instead of" phrase, or a rules event (a spell going to the
  graveyard as it resolves, a land producing mana, a discard, entering the
  battlefield, declaring blockers, drafting).

## Required truth per class (written from the readings, before any structure)

Would-classes: A1 is the would-be event; A2 the replacing instruction(s); A4 a
resulting event the replacement produces, notably a nested event of A1's own
kind (CR 614.5); A5 a back-reference to A1's object.

- add (1): A1 a would-be mana addition; A2 add white mana; A4 the new addition is of A1's kind; A5 none to an object ("that much" is A1's amount).
- assemble (1): A1 a would-be assembly; A2 assembles two; A4 nested assembly; A5 "it" = the assembling permanent.
- assign (1): A1 would-be damage assignment, dealing, being dealt or tapping by a face-down creature; A2 turned face up, then the same events; A4 the events after the flip are new events of A1's kind; A5 "it" = that creature.
- be created (16): A1 would-be token creation; A2 doubled, augmented or substituted creation (passive); A4 a nested creation that contains A1's own tokens; A5 "those tokens" = the tokens A1 would create.
- be dealt (58): A1 would-be damage to a recipient; A2 the damage dealt to another recipient, or a substitute (counters, exiled cards, sacrifice, destroy, echo counters); A4 redirected damage is a new damage event; A5 "that damage", "it", "that creature"; one member modifies an earlier printed prevent instruction (N1); one member prints a prohibition, not a replacement.
- be destroyed (3): A1 would-be destruction of a land; A2 sacrifice and indestructible, or remove damage; A4 none of A1's kind; A5 "that land", "it".
- be put (129): A1 a would-be move to a graveyard, or a would-be counter placement; A2 exile, reveal and shuffle, library placement, or the modified placement; A4 counter members produce a nested placement of A1's kind; A5 "it", "that card", "them".
- be reduced (1): A1 a would-be life reduction to 0 or less; A2 transform and set the life total, with a tail loss; A4 none of A1's kind; A5 none.
- begin (6): A1 a would-be beginning of a turn or step; A2 skip it (with tail follow-ups); A4 nothing results; A5 "that turn"/"that step" name A1 itself, "that player" its agent.
- cause (2): A1 a would-be draw caused by cycling, a would-be life gain; A2 exile-until and cast, lose life; A4 none of A1's kind; A5 "that player".
- connive (1): A1 a would-be connive; A2 draw, then the creature connives; A4 a nested connive (CR 614.5); A5 "that creature".
- copy (1): A1 a would-be copying; A2 copy that many plus one; A4 nested copies; A5 "it" = the spell.
- counter (1): A1 a would-be countering; A2 exile that spell, may play it; A4 none of A1's kind; A5 "that spell", "that card".
- create (14): A1 would-be token creation; A2 augmented, doubled or substituted creation; A4 nested creation; A5 "those tokens".
- deal (86): A1 would-be damage by a source; A2 modified damage (double, triple, plus or minus N, redirected), counters, mill; A4 the modified damage is a nested damage event; A5 "it" = the source, "that permanent or player"; one member prints a prohibition, not a replacement.
- die (92): A1 a would-be death; A2 exile, return, shuffle, library; A4 none of A1's kind; A5 "it", "that card", "that creature".
- draw (46): A1 a would-be draw; A2 a substitute (exile, look, reveal, skip, win, counters, tokens, life, damage) or more draws; A4 many produce a nested draw ("draw two", "then draw a card", "they draw a card"), the CR 614.5 case; A5 "that card" = the card that would have been drawn, "that draw" names A1 itself, "they"/"that player".
- enter (15): A1 a would-be entering; A2 sacrifice or discard with a tail put onto the battlefield, exile, or entering under another control; A4 the tail put is a nested entering of A1's kind; A5 "it" = the entering object.
- explore (2): A1 a would-be explore; A2 explores twice, or scry then explores; A4 nested explores; A5 "it", "that creature".
- flip (1): A1 a would-be coin flip; A2 flip two and ignore one; A4 nested flips; A5 none.
- gain (20): A1 a would-be life gain; A2 more life, draws, loss or no gain; A4 a nested gain on most; A5 "that player" ("that much" is A1's amount).
- get (4): A1 would-be energy or counters; A2 more, or one and a prohibition; A4 nested; A5 none (amounts only).
- learn (1): A1 a would-be learn; A2 return this card; A4 none of A1's kind; A5 none.
- leave (15): A1 a would-be leaving of the battlefield; A2 exile "instead of putting it anywhere else"; A4 none of A1's kind; A5 "it", "them".
- lose (9): A1 a would-be loss of mana, life or the game; A2 the mana becomes a colour, twice the loss, draws and a life total, exile and a life total; A4 a nested loss on one; A5 "they", "that mana".
- mill (2): A1 a would-be mill; A2 a larger mill; A4 nested; A5 "they".
- pay (1): A1 a would-be life payment; A2 exile that many cards; A4 none; A5 none (the "it" is inside the condition).
- planeswalk (1): A1 a would-be planeswalk; A2 look, put, then planeswalk; A4 a nested planeswalk; A5 none.
- proliferate (1): A1 a would-be proliferate; A2 proliferate twice; A4 nested; A5 none.
- put (9): A1 a would-be counter placement or land move; A2 the modified placement, or put then sacrifice; A4 nested; A5 "that permanent", "it", "that land".
- reduce (8): A1 damage that would reduce the life total below N; A2 it reduces it to N; A4 the modified reduction; A5 "it" = your life total.
- result (1): A1 damage that would remove every loyalty counter; A2 all but one removed; A4 nested removal; A5 "those counters".
- roll (7): A1 a would-be die roll; A2 more dice and an ignore; A4 nested rolls; A5 "they", "them".
- scry (2): A1 a would-be scry; A2 scry plus one, or draw; A4 nested on one; A5 none.
- search (1): A1 a would-be library search; A2 search the top four; A4 nested; A5 "that player", "that library".
- untap (2): A1 a would-be untap; A2 remove counters (and, quoted, untap); A4 nested untap on one; A5 "it".

No-would classes: A1 is the instruction the 'instead' modifies; A2 the
modifying instruction; A4 the event the modification produces, distinguishable
from A1; A5 a back-reference to A1's object.

- The ability-word and keyword classes (adamant, addendum, corrupted, coven, delirium, descend, fateful, ferocious, hellbent, infusion, landfall, metalcraft, morbid, raid, revolt, spell, threshold, void; 63 members): N1. A1 the preceding paragraph's instruction; A2 the member's own instruction; A4 the member's instruction is the resulting event, mostly of A1's kind ("deals 4 damage" for "deals 2"); A5 "that creature", "that player", "it" = A1's target.
- no-would:counter, create, deals, draw, gain, it, put, return, that, excess, equipped (30 members): N1 with the modified instruction in the preceding clause of the same paragraph (inside one quoted ability for equipped); excess redirects the excess of the earlier damage.
- no-would:if (343): mostly N1 (kicker, gift, bargain, Opus, mana-spent, "choose both", "countered this way", Landfall-type upgrades); 19 are N2 (discard-to-battlefield, land and permanent mana production, enters-instead-of-battlefield).
- no-would:g, t, u, until (6): N2 — a land's mana production replaced (one u member: a spell's move to the graveyard as it resolves).
- no-would:imprint, when, whenever (8): N2 — a spell's move to the graveyard as it resolves replaced ("instead of putting it into"), except one whenever member, N1, which modifies a create in the same clause.
- no-would:instead (1): N2 — a draft action replaced; drafting is outside a game.
- no-would:this (1): N2 — declaring blockers replaced by a pile procedure.

## Structures consulted, and the cell bases

Only the structures the command lists were credited, each by section:

- AQ4 contract (`benchmarks/aq4/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`) §9 rungs 1-5, §12, §13, §16. Rung 1 is ratified (§11 law); rungs 2-5, §12, §13 and §16 are CANDIDATE benchmark structure, not ratified production law; RUNG-6 (predicate-valued references, event patterns, bound choices; §9 consumer column "scaling/replacement wording") is RESERVED.
- H-REGION regions and ATTACH-3 role marks of oracle-compiler-interface/3, as `h_region.py` derives them (a ratified measurement interface, not production law): one region per frozen legacy candidate head, a head occupying a predicate slot only at a CR 608.2c instruction boundary; role marks cost, condition, duration, destination.
- The frozen P4 `relation_candidates` (kinds cr607-linkage, coreference with anchor CR 607.1, conditionality with anchors CR 603.4 / 601.2b / 611.2 / 608.2, kind-unclear) and the frozen `participants()` marks.

The bases the ledger notes cite:

- **B1 (A1 NOT-EXPRESSED, would-class).** The would-be event is a hypothetical event: it never happens (CR 614.6). H-REGION starts a region only at an instruction-boundary head, and seams.json `supports_A1` (a region headed at the would-verb) is false on every one of the 561 would-class members. The ATTACH-3 condition span that covers an 'If ... would ...' prefix marks a qualifier attached to a region, not an event; §13 atoms are eligibility constraints over an object's value sets; §12 participants are argument slots; §16 kinds are CR 607 linkage, coreference and conditionality. No cited section defines a carrier for an event that is described but not instructed. Carrying it would force RUNG-6 (adoption trigger is a holdout card, §9/§22).
- **B1n (A1 NOT-EXPRESSED, N2).** As B1: the replaced event is printed only as an "instead of" phrase, or is a rules event the card does not instruct; no cited section defines a carrier for it; would force RUNG-6 (adoption trigger is a holdout card, §9/§22).
- **U1 (A1 UNRESOLVED, N1).** The modified instruction is printed earlier on the card. A printed instruction has a cited carrier — the H-REGION region of its own occurrence (oracle-compiler-interface/3 §I3a; the occurrence itself is CANDIDATE benchmark structure §9 rung 2, not ratified production law) — but which earlier instruction a bare 'instead' modifies is not derived by the frozen code (seams.json records the member clause and its tail only, and no frozen detector points back). Resolution reach, I3's class; not evidence of a missing structure.
- **A2 EXPRESSED.** Every replacing (or modifying) instruction of the clause and of its tail continuation has an H-REGION region at its head, and no region's head or span sits on A1's own printed text: carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law); evidence seams.json `members[].a2.heads`, `a2_tail` and `evidence[].h_region.regions`.
- **U2 (A2 UNRESOLVED).** H-REGION defines a region for an instruction, but on this member the frozen legacy detector derives none at one or more replacing heads (passive "are created instead", "is dealt to", "reduces it to"; a head printed after 'instead' or after an adverb, not at a boundary word; "look", "put", "gain", "deal", "skip", "choose" and others never heads), or derives one on A1's own text (a "draw" or "discard" inside the condition), or a region's span runs over A1's printed "instead of" phrase (N2). Detector reach, I3's class; not evidence of a missing structure. A tail clause that continues the replacement ("If you do", "If you can't", "Then", "Otherwise") counts as replacing text.
- **B3 (A3 NOT-EXPRESSED, definitional).** A3 is EXPRESSED only by a carrier whose CR anchor is in 614. The §16 kinds are CR 607 linkage, same-card coreference and conditionality; P4's conditionality candidates come from its 'if'/'unless'/'as long as'/'otherwise' arms anchored in CR 603.4, 601.2b, 611.2 and 608.2, and are NOT evidence of a CR 614 replaces/modifies link. No frozen P4 arm has a 614 anchor (seams.json `p4.frozen_arm_anchors_in_cr614` is empty), so `count_614_anchored` is 0 on every member (`count_614_anchored_total` 0, expected 0). The result is definitional, not measured. The same holds for N1 members: a CR 608.2c modification link has no carrier either.
- **B4 / U4 (A4).** Distinguishing a resulting event from A1 needs A1 carried. Where A1 is NOT-EXPRESSED (B1, B1n), A4 is NOT-EXPRESSED: a region may locate the resulting event, but nothing can say it is a new event and not the replaced one; the nested-event cases (draw → draw, create → create, explore, roll, proliferate, scry, deal) are exactly the CR 614.5 lineage this needs; would force RUNG-6 (adoption trigger is a holdout card, §9/§22). Where A1 is UNRESOLVED (U1), A4 is UNRESOLVED: the two printed instructions sit in different occurrences, which the cited structures could tell apart, but the modified one is not derived.
- **U5 (A5 UNRESOLVED).** §16 defines the same-card coreference edge (carried by CANDIDATE benchmark structure §16, not ratified production law), whose endpoints are participants or occurrences; P4 marks the anaphor ("it", "that card", "those tokens", "that player"; kind coreference, anchor CR 607.1; seams.json `a5`, `a5_tail`, `evidence[].p4`) but resolves nothing, so the edge to A1's object is not derived. On a member printing no back-reference to A1's object, the frozen code finds none and the absence is not a proof (register #37). Mechanical `supports_A5` is not A5 evidence by itself: it is true for an "it" inside the condition on one member, and on one recall control the tail "that card" names the revealed card, not A1's object.

## Ledger

| class | members | read | A1 | A2 | A3 | A4 | A5 | note |
|---|---|---|---|---|---|---|---|---|
| `add` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### add). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `assemble` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### assemble). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `assign` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### assign). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `be created` | 16 | 16 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 16 read (listed under ## Reads / ### be created). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 16 read members of this row. |
| `be dealt/part-1` | 55 | 55 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 55 read (listed under ## Reads / ### be dealt/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 55 read members of this row. Prohibition, not a replacement (Q4): 84050a10-e1f1-413e-aa21-5c1f47bb2a64:0:0:1. |
| `be dealt/part-2` | 2 | 2 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### be dealt/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: destroy, sacrifice; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `be dealt/part-3` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### be dealt/part-3). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `be destroyed` | 3 | 3 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 3 read (listed under ## Reads / ### be destroyed). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 3 read members of this row. |
| `be put/part-1` | 103 | 103 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 103 read (listed under ## Reads / ### be put/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: activate, cast, exile, return, reveal, shuffle; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 103 read members of this row. |
| `be put/part-2` | 26 | 26 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 26 read (listed under ## Reads / ### be put/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 26 read members of this row. |
| `be reduced` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### be reduced). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `begin` | 6 | 6 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 6 read (listed under ## Reads / ### begin). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 6 read members of this row. |
| `cause` | 2 | 2 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### cause). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. A legacy head sits on A1 text on 5b67a944-ab0b-4155-8bc0-becb1b38b3bb:0:0:0. |
| `connive` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### connive). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `copy` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### copy). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `counter` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### counter). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `create/part-1` | 12 | 12 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 12 read (listed under ## Reads / ### create/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 12 read members of this row. |
| `create/part-2` | 2 | 2 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### create/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: create; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `deal` | 86 | 86 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 86 read (listed under ## Reads / ### deal). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 86 read members of this row. Prohibition, not a replacement (Q4): f7be3da5-55b2-46f2-a5aa-277dee242b94:0:0:1. |
| `die/part-1` | 84 | 84 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 84 read (listed under ## Reads / ### die/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: activate, create, exile, return, shuffle; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 84 read members of this row. |
| `die/part-2` | 8 | 8 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 8 read (listed under ## Reads / ### die/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 8 read members of this row. |
| `draw/part-1` | 38 | 38 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 38 read (listed under ## Reads / ### draw/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 38 read members of this row. |
| `draw/part-2` | 8 | 8 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 8 read (listed under ## Reads / ### draw/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: create, draw, exile, play; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 8 read members of this row. |
| `enter/part-1` | 11 | 11 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 11 read (listed under ## Reads / ### enter/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 11 read members of this row. |
| `enter/part-2` | 4 | 4 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 4 read (listed under ## Reads / ### enter/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: exile, sacrifice; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 4 read members of this row. |
| `explore` | 2 | 2 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### explore). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `flip` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### flip). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `gain/part-1` | 18 | 18 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 18 read (listed under ## Reads / ### gain/part-1). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 18 read members of this row. |
| `gain/part-2` | 2 | 2 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### gain/part-2). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: draw; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `get` | 4 | 4 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 4 read (listed under ## Reads / ### get). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 4 read members of this row. |
| `learn` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### learn). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `leave` | 15 | 15 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 15 read (listed under ## Reads / ### leave). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: activate, cast, create, exile, return; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 15 read members of this row. |
| `lose` | 9 | 9 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 9 read (listed under ## Reads / ### lose). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 9 read members of this row. |
| `mill` | 2 | 2 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### mill). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:adamant` | 2 | 2 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:adamant). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:addendum` | 2 | 2 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:addendum). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:corrupted` | 2 | 2 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:corrupted). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:counter` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:counter). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: counter; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:coven` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:coven). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:create` | 2 | 2 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:create). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: create; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:deals` | 2 | 2 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:deals). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:delirium` | 6 | 6 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 6 read (listed under ## Reads / ### no-would:delirium). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 6 read members of this row. |
| `no-would:descend` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:descend). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:draw` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:draw). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: draw; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:equipped` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:equipped). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:excess` | 4 | 4 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 4 read (listed under ## Reads / ### no-would:excess). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 4 read members of this row. |
| `no-would:fateful/part-1` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:fateful/part-1). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:fateful/part-2` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:fateful/part-2). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: create; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:ferocious/part-1` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:ferocious/part-1). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: counter; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:ferocious/part-2` | 4 | 4 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 4 read (listed under ## Reads / ### no-would:ferocious/part-2). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 4 read members of this row. |
| `no-would:g` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:g). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:gain` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:gain). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:hellbent` | 4 | 4 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 4 read (listed under ## Reads / ### no-would:hellbent). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 4 read members of this row. |
| `no-would:if/part-1` | 67 | 67 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 67 read (listed under ## Reads / ### no-would:if/part-1). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: cast, counter, create, destroy, double, draw, exile, investigate, play, return, search, shuffle; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 67 read members of this row. |
| `no-would:if/part-2` | 257 | 257 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 257 read (listed under ## Reads / ### no-would:if/part-2). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 257 read members of this row. |
| `no-would:if/part-3` | 19 | 19 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 19 read (listed under ## Reads / ### no-would:if/part-3). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 19 read members of this row. A legacy head sits on A1 text on 18ac2282-83af-4acc-b20b-6a95771da688:0:1:0, 2441696b-a9ba-4813-ba2e-e71f85281d05:0:3:0, 2c189e3b-90d3-49b4-bebe-a4f14c8a275b:0:0:0, 3b7e7a11-bf59-413d-8796-640d17c2c1c6:0:0:0, 5b04a337-3152-481e-973f-a11dbd615f93:0:3:0, 867def48-4be8-4056-bcf1-d6b00450b9a3:0:1:0, ee2ab1ab-be1e-4e56-99f2-7784f7350b41:0:1:0. |
| `no-would:imprint` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:imprint). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:infusion` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:infusion). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: destroy; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:instead` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:instead). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:it` | 11 | 11 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 11 read (listed under ## Reads / ### no-would:it). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 11 read members of this row. |
| `no-would:landfall/part-1` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:landfall/part-1). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: draw; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:landfall/part-2` | 4 | 4 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 4 read (listed under ## Reads / ### no-would:landfall/part-2). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 4 read members of this row. |
| `no-would:metalcraft` | 3 | 3 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 3 read (listed under ## Reads / ### no-would:metalcraft). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 3 read members of this row. |
| `no-would:morbid` | 6 | 6 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 6 read (listed under ## Reads / ### no-would:morbid). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 6 read members of this row. |
| `no-would:put` | 3 | 3 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 3 read (listed under ## Reads / ### no-would:put). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 3 read members of this row. |
| `no-would:raid` | 2 | 2 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:raid). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:return` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:return). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: return; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:revolt` | 1 | 1 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:revolt). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:spell/part-1` | 2 | 2 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:spell/part-1). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:spell/part-2` | 2 | 2 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:spell/part-2). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: cast, search; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:t` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:t). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:that` | 3 | 3 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 3 read (listed under ## Reads / ### no-would:that). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 3 read members of this row. |
| `no-would:this` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:this). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:threshold` | 13 | 13 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 13 read (listed under ## Reads / ### no-would:threshold). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 13 read members of this row. |
| `no-would:u` | 2 | 2 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:u). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:until` | 2 | 2 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### no-would:until). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `no-would:void` | 3 | 3 | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 3 read (listed under ## Reads / ### no-would:void). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 3 read members of this row. |
| `no-would:when` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:when). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `no-would:whenever/part-1` | 5 | 5 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 5 read (listed under ## Reads / ### no-would:whenever/part-1). N2 would-less replacement; A1 NOT-EXPRESSED per B1n and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 5 read members of this row. |
| `no-would:whenever/part-2` | 1 | 1 | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | UNRESOLVED | all 1 read (listed under ## Reads / ### no-would:whenever/part-2). N1 printed modification (CR 608.2c reading, Q3); A1 UNRESOLVED per U1 and A4 per U4. A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: create; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `pay` | 1 | 1 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### pay). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: exile; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `planeswalk` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### planeswalk). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `proliferate` | 1 | 1 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### proliferate). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: proliferate; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `put` | 9 | 9 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 9 read (listed under ## Reads / ### put). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 9 read members of this row. |
| `reduce` | 8 | 8 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 8 read (listed under ## Reads / ### reduce). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 8 read members of this row. |
| `result` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### result). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `roll` | 7 | 7 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 7 read (listed under ## Reads / ### roll). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 7 read members of this row. |
| `scry` | 2 | 2 | NOT-EXPRESSED | EXPRESSED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### scry). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 EXPRESSED: H-REGION region at every replacing head (all heads derived on the row, replacing or not: draw, scry; seams.json members[].a2.heads and a2_tail), carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |
| `search` | 1 | 1 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 1 read (listed under ## Reads / ### search). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 1 read members of this row. |
| `untap` | 2 | 2 | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | all 2 read (listed under ## Reads / ### untap). would-class; A1 NOT-EXPRESSED per B1 and A4 per B4 (would force RUNG-6). A2 UNRESOLVED per U2 (detector reach). A3 NOT-EXPRESSED per B3 (definitional; count_614_anchored 0 on every member). A5 UNRESOLVED per U5. Every NOT-EXPRESSED cell rests on all 2 read members of this row. |

## Splits

Each part is a member list, one address per line.

### be dealt/part-1

- `03c47f1c-02a7-428c-a126-9e85325ebc71:0:0:1`
- `05775dea-d7f0-4e0b-af4d-ba8d320dc4c0:0:0:0`
- `09b9e6fd-7a61-4ed4-a121-61b64fbf03f4:0:0:0`
- `0e69e6c2-fdc5-4c1a-bd96-c4283b82743a:0:0:0`
- `0fe4767b-2023-49fc-bc93-b73b43f70b76:0:1:0`
- `1245b165-e26f-4839-8468-2e95148fc6f6:0:0:0`
- `184fdd23-8235-4500-b2f5-d3b0b93a8f35:0:0:0`
- `1af63a5e-2bec-4f8d-a373-d9ce43a7d242:0:0:1`
- `2c5c8250-1860-42a1-a335-071f54830d37:0:1:0`
- `33e88072-3840-4090-8d0b-7fb38279e150:1:1:2`
- `35844d8b-8f68-4248-b921-e766757a9e26:0:0:0`
- `3a105959-dfce-4202-b37f-ae635dfcb30b:0:2:0`
- `44ae1c25-8622-4a58-92e0-12d76f084718:0:0:0`
- `45f3b9f2-3fce-4f91-bcbd-de069e5f9e4c:0:0:0`
- `4d9d5dbb-25ab-41a5-a277-3ee5f9ef579b:0:0:0`
- `4f5a7b65-b7f4-4bad-acfd-35edfb8f86a7:0:0:0`
- `50ddbea3-7ef4-4f6a-83c9-0c3ea1dfa3c9:0:2:0`
- `5b3f6817-5d7a-4d83-ad1d-df75b4e1970b:0:0:0`
- `644b7aba-a7b8-4861-9e83-73329cf85be2:0:1:0`
- `655ae8e7-372b-4d8d-b33f-4aca46831abb:0:0:0`
- `6e49a5b8-6bc4-4c7b-82c1-957f1fb0ca5f:0:0:0`
- `7ca54a23-f8eb-4982-b4ee-7392e2f2a1b3:0:0:0`
- `7d84e667-2f14-437c-be4f-161b98d59341:0:0:0`
- `8137e765-4df9-469f-a527-dee91d58fb7e:0:0:0`
- `84050a10-e1f1-413e-aa21-5c1f47bb2a64:0:0:1`
- `8429ba6a-6c06-4a83-a6ee-023b64b825f8:0:2:0`
- `86d0ba9d-6972-4cbc-871d-3fb413565c45:0:0:0`
- `8bc5546e-554f-430d-80b1-99578b5ea188:0:2:1`
- `9c058107-b2a1-4300-8d97-c697c248df96:0:1:0`
- `9e60c102-412e-4956-a7bb-a2cd737d6692:0:1:0`
- `a8b93d4d-bb67-4063-ac6d-7775be1b1f10:0:0:0`
- `b7902113-9ddf-4d81-a76a-b54b8a36c154:0:1:0`
- `b8d395a3-0bfe-45c3-bb3a-820d4f235b88:0:0:0`
- `bd5ad7c3-4477-4278-9875-d2ffbb0e8089:0:0:0`
- `d29078c0-1fb8-437a-81d1-bb319f646941:0:0:0`
- `d3088e1d-62c9-4478-9ef7-fc3c9e5cfadb:0:0:0`
- `d748bad4-dd4c-4553-9fcc-e462260f6ff3:0:1:1`
- `d79e8ec4-b44b-4598-991c-7781dab55868:0:0:0`
- `d830a136-6fb9-42e7-81f1-97e1d713ee82:0:1:0`
- `dfedb968-f27c-4117-aff6-da707dd43e82:0:2:0`
- `dff66bcf-e126-49d2-b67e-ea3b0a38d390:0:1:0`
- `e02164ba-34f8-4a5f-a05b-dd3ef3f8ceae:0:1:0`
- `e03b553a-3d0d-453e-ad3e-f7d4b9fb2624:0:0:0`
- `e6873252-653a-47a8-99b7-b2ef70aa1f7f:0:2:0`
- `e85f6251-8801-414b-adc9-5488794e7456:0:0:0`
- `ee7f698d-55c5-4a7a-803d-304febe6a758:0:0:0`
- `ef49dc78-9fd9-4cf8-af10-5a6b8ef7fc57:0:1:0`
- `f066174a-a959-4365-920f-c04506d94a5a:0:1:0`
- `f1052b21-ba96-499f-b9e6-9dba4ed82e1e:0:1:0`
- `f2103ab8-a183-4db8-98dd-4146217b5125:0:0:0`
- `f38fe1e9-8997-4b63-9109-7513034bac88:0:0:0`
- `f4bc6674-8586-4dd9-ad3a-87ba704fda7a:0:0:0`
- `f6a6da20-52c8-4921-9884-29d3a3051b0d:0:0:0`
- `f9269fda-e1e6-4e10-9a64-26e8c0f38b0c:0:0:0`
- `fec51ab9-484f-46a8-b2b0-772a61d89e41:0:0:0`

### be dealt/part-2

- `35ab189a-adc8-48d6-82d2-53eb56a4d5e4:0:0:0`
- `52ddf96d-3d6a-439c-b486-d806cbc32d77:0:1:0`

### be dealt/part-3

- `cc22c210-efd0-494c-8560-448b038b3c5f:0:1:1`

### be put/part-1

- `00ba0c24-a671-493e-ba46-13e45d1818f1:0:1:1`
- `02b6900b-219f-4832-8f93-6ef27ee76c0c:0:0:1`
- `0761a0e7-d443-4bab-bb15-307c83d4a6a1:1:2:0`
- `087f9ad7-e74f-40e2-8102-1ed2925d0418:0:1:0`
- `0a154fb2-9f23-4c22-baee-728492385d6d:1:2:0`
- `11838086-db2f-4588-ae18-4129c9e2b67d:0:1:1`
- `13c90d78-cfb1-4d40-a35e-1fd170450b45:1:2:0`
- `1b09d0cf-403c-4a15-aeee-602a1bdaf0c1:0:2:0`
- `1c248187-0be3-4a03-a817-14f68f638ae7:0:1:2`
- `1e0cf860-6be6-4b4b-9a67-0c19b6018ae1:0:1:2`
- `210d1077-6e60-4f06-a8a4-10b842979ac5:0:1:2`
- `27065d34-b22a-47af-aea2-980f47bafcea:0:1:1`
- `2ad77eb7-9466-432f-87b4-e80e4b66e143:0:0:1`
- `2cef4171-8151-4ee9-83a7-bcb5116451bf:1:2:0`
- `2d7e00b6-12f0-4b03-82a6-50e3d1b5395e:0:1:0`
- `2de138b0-3159-4a0c-a474-a4e5600b2e51:0:1:0`
- `2fa6f1b1-00af-433f-b8e1-36db99cd9bba:0:0:1`
- `2fcd5779-7234-49e3-b3c5-ebc07db74462:1:2:0`
- `322f0459-f394-44f0-977b-55fd0cbe0712:0:1:0`
- `35f53871-203a-41da-930e-76540c62d3da:1:1:0`
- `389bcb9f-4e66-4704-9968-a1c1574ec2c8:1:2:0`
- `3b102ccc-7629-457c-aba6-e9b00fd50c85:1:2:0`
- `3d5c98ff-fcf1-42bd-9533-2648791a4f45:0:1:2`
- `3e155876-6086-4499-9963-6efc97cfa5a6:1:3:0`
- `4380df08-7be4-48ca-9783-d644fd2ea27d:0:1:1`
- `45802eb2-6848-416c-95e0-c1c1ea0620d0:1:2:0`
- `493b2820-c250-48bd-9f3c-e1b5639ee101:1:2:0`
- `4b1da9aa-a30c-44b8-a10e-f9dc3fe70b6f:1:3:1`
- `4c05b382-58ab-4a2d-a81c-408ea273b6b6:0:1:1`
- `4d0a0027-53b3-45a1-8736-f0ac86b19342:1:2:0`
- `4db96d32-b4c2-44e9-a73f-aca7dad279b6:1:2:0`
- `51233ade-70cd-4539-9f41-5ffab761da54:1:2:0`
- `5228730a-cebc-472e-ab9a-f424e0c893fd:1:2:0`
- `52e77cc3-f8e9-4a20-811b-fe1e46a96ad7:1:0:0`
- `55717e47-c1ab-4218-bc1c-10e58e91fa87:1:2:0`
- `56ba8fe5-8693-4783-8406-9ced99de0b2a:0:1:1`
- `5768fe50-a134-492c-a725-5ed02610c39f:1:2:0`
- `594f6881-c059-46f8-aa4e-7151d502de73:1:1:1`
- `5b3f041e-ad4a-47ea-bdc4-1be2353f2e18:0:0:1`
- `5d0b8dc6-f4b6-4650-805d-4240d4a4ab82:1:1:0`
- `5e1bd17d-3825-45c0-9e7c-6887b7e2cb5c:1:2:0`
- `5f1e9098-f554-4505-974b-cef4b4b7b23d:0:1:1`
- `600db821-4210-4996-a3f7-e05a143e50c2:1:1:0`
- `626e8acc-20da-496c-9a79-bfbf7529c01d:0:2:1`
- `634475d9-a1d7-4146-9a37-645d3d162af1:0:1:1`
- `657c5473-f153-4dd2-94a0-d477cbc2451d:0:0:1`
- `67a025eb-6e65-435c-becb-b51085175292:1:2:0`
- `6c1d22d4-f28e-4041-a9b6-1575e8929b61:0:1:0`
- `6df6e834-1917-4bf4-b0b7-09834bf90fb2:0:1:0`
- `6f8ca795-d6fd-4e3e-911c-c621a942acbb:0:1:2`
- `7088a901-0489-41c3-9f2f-633939514de8:0:1:1`
- `72177c93-ed1f-47bd-99a6-ad229a292d46:0:2:0`
- `74c9cc13-c03f-4322-82af-b7bce1f2a0d8:1:1:0`
- `7721e800-fba6-4ae7-855e-631b2ecc8d6b:0:1:1`
- `78dbbc15-9304-4178-b9b2-1db6c64ca11a:0:0:2`
- `7a3e50a5-c163-4c41-b62d-d52c233c55b7:0:1:2`
- `810d3afe-c644-444f-a4d9-88b323f0b581:0:2:0`
- `821e8648-222c-4b33-a8bd-e8bfff7dcd9e:0:0:1`
- `830e3e37-a80c-4b0e-b9af-393ad4ca01d7:1:2:0`
- `839748e7-ccb4-421e-9626-b6d8be9390ab:0:0:1`
- `87efff06-b6cb-4a8f-937b-e50e367fd896:0:2:0`
- `8845ba0d-c2f4-49e4-b06e-54a06a8297e0:1:2:0`
- `8b34b211-985b-4934-bb3b-8e6672685ac2:0:1:0`
- `8c56530b-098a-4afd-9022-76bfaa1f6a7c:0:1:1`
- `8f3e6554-eb8a-4096-81a3-2411186d9cb4:1:2:0`
- `8f5ef838-839a-4eb0-8d65-c8c8def0a233:0:1:2`
- `9059a940-ac28-4322-a11b-af1d107b2edd:0:0:1`
- `9ef53bd8-9999-4ea3-a43a-4084a9f208db:1:2:0`
- `a051dee0-60c8-4f58-84cb-55460c097115:0:1:0`
- `a10b3e35-8cc4-450e-9e30-0fce8df0fea4:0:3:0`
- `a3e10b9b-9349-4b44-a46c-c825293dbd05:0:2:1`
- `a56c5ca5-70eb-4d5f-8116-2acbe5f5a3cb:0:2:0`
- `a6395447-677d-4c39-8eda-2d57e527c94e:0:1:1`
- `a986d83d-22f1-45c3-bc2d-f5b210c539fb:0:1:1`
- `aa1a248d-2f76-4f15-b065-08f299af07b9:0:1:0`
- `aba60536-ffbd-480c-8e8f-9639bdc53d4b:0:1:1`
- `abf4dcd8-5176-4f4a-b7c1-5ce24ff181bf:0:1:2`
- `b0c28b2b-a2dd-4b76-bb1c-cec55a0a6784:1:0:1`
- `b8ca5877-ac9e-4b15-8c23-c70f61b01895:0:1:0`
- `ba790609-7b48-4a96-a21f-5a0cfcf316a3:1:2:0`
- `ba88575a-4b9a-40cd-abbc-4539912c9455:1:1:0`
- `bab0ab8d-74d2-49a3-b258-b93d19925d99:0:1:1`
- `c21d1ca3-3d19-4b4d-bbfa-07b5b7bcea4b:1:2:0`
- `c3a68018-9eff-47e6-a612-182886d28fe3:0:0:2`
- `c6bb4b41-8dae-429a-b928-ae9d39c74711:1:1:0`
- `cae3ec72-436d-4086-9dcb-17b3d92ad5c4:0:2:0`
- `cca15007-2faf-4696-a4c5-2d7b6c1ec5b5:0:0:1`
- `cddccc2a-a76e-48b3-b4dd-dfeab89e1619:0:0:0`
- `d1438681-241b-4d53-9470-4d04a7797ea8:0:0:1`
- `d2d753d4-3bb7-4503-8cc0-8f948b7a461e:1:2:0`
- `d6fafb50-9531-4fbf-bb1e-ebb4dd39281c:0:0:1`
- `e4d52559-7624-48b2-96ba-e52ada6c507a:0:0:1`
- `e80772e2-8623-4094-81a2-70828b2b151c:0:1:0`
- `ebfafabc-5255-4024-be59-7403bdb16ee4:0:1:0`
- `ee049bf3-b31c-4dcc-996f-bb076848432b:1:2:0`
- `ee12e2e0-7eda-4f5e-9373-d4c029995adb:1:2:0`
- `f21ce158-2925-4658-ab7b-b73718d31965:0:1:1`
- `f32c5530-6692-4d47-8789-c73da23fd5b7:0:0:1`
- `f4e32fc1-1b8d-441e-8e76-71f19f98e925:0:1:0`
- `f5092c14-eec4-472c-999c-ba96c36b2fbb:0:1:1`
- `f589e5ee-399c-4613-b7a2-9ab2866cc830:0:1:2`
- `fb5e8b8c-bad2-45bb-abb4-2ed454525749:0:1:1`
- `fd36cc16-d3d9-4c9d-9d28-bbe7e5459d75:0:1:1`

### be put/part-2

- `01dbf1bc-ca62-4fb6-959c-ef7c0dc03bb0:0:1:0`
- `14d3e014-9c4f-4864-8f1e-a45ac27e4dbf:0:0:0`
- `16156274-8dc0-439c-94c4-e8c89bbb5687:0:0:0`
- `170ab932-9d50-4ce7-9a42-08e1edce7e7c:0:1:0`
- `28fe909b-06e0-424c-9f75-c824a25f5865:0:0:0`
- `34ceb733-0329-4c1b-8d75-25c34fd4400f:0:1:0`
- `41fed659-237c-4d8e-ad31-d17fa0d3f764:0:0:0`
- `5e7ef7fe-968b-4ada-9fe4-6fda0541aafc:0:1:0`
- `6b6e4ee2-52e6-452b-af15-c90eab5fc746:0:1:0`
- `7683c2b2-a06f-4691-9cc5-1968dc032885:0:1:0`
- `79770e65-740a-44c7-bea2-a24e6a722c22:0:0:0`
- `8609ed1a-f202-483e-9299-408ef6e84ad6:0:1:0`
- `9966cac0-331f-4627-be5a-5060a6ac5a32:0:1:0`
- `a1f3da21-af6d-450e-bf0b-985d158418e6:0:0:0`
- `a2fe5937-212c-4e71-8d6e-f408b38100aa:0:0:0`
- `a9d60d80-bcef-45e0-8ded-d70bd3c2780f:0:1:0`
- `c3d38129-b955-4fb5-8486-095f918935b9:0:2:2`
- `c665544f-557b-4631-a1dc-39571470ca2e:0:1:0`
- `c9404d7d-a026-4082-9fcb-1ab571a136b5:0:0:0`
- `ca0cc02b-b106-4eca-9388-d4b48dd3be49:0:0:0`
- `d81fc181-ecb0-43a5-88e8-c61aca3428d8:0:0:0`
- `e7b746c8-1b32-42ed-8328-4e16274209d8:0:1:1`
- `f122624f-f30d-444e-a62a-939829241045:0:0:0`
- `f1c2dbe2-fbe0-4058-bdf1-91d1b1832786:0:1:0`
- `f578465d-f3a5-48da-bcab-cffbbdd88be8:0:1:0`
- `fe2afa18-54d0-4595-af27-256398793a42:0:1:0`

### create/part-1

- `01546b7d-a233-4176-8843-d732074dc5b6:0:0:0`
- `11d8fab8-93af-4291-80bd-cf9436e99f4b:0:0:0`
- `353db389-b829-4e66-85d5-6018bc87c3e0:0:0:0`
- `61fbaaf2-4286-4e9a-b9cb-aa31262b596a:0:0:0`
- `6a1bce89-0c11-4d8d-aacb-c0a5a5effffc:0:0:0`
- `7246d45b-2185-4cdd-981b-5419b7d52bce:0:0:0`
- `8215f4a2-7131-426b-ad9c-6427caabd715:0:1:0`
- `84dc94b2-95fb-4d53-aaa2-191cb645639f:0:0:0`
- `9573c85a-e574-4b4e-aae0-2165c45fd27e:0:0:0`
- `9d22960b-babc-4cf3-b228-d32e13bc6014:0:1:0`
- `df702b0c-e011-497f-ae29-9876efac4a4c:0:1:0`
- `f36d1d8b-8303-44a9-ab56-531931641ea2:0:0:0`

### create/part-2

- `44ba2aa5-2bf5-4267-ae82-f0daf8f5e3e8:0:3:0`
- `44ba2aa5-2bf5-4267-ae82-f0daf8f5e3e8:0:5:0`

### die/part-1

- `0462e985-c99e-4404-b212-e9d8baecce72:0:0:1`
- `077885dc-3a88-4ad4-bd5d-bf709aa71e8d:0:1:0`
- `10d33e95-3e5d-447e-ba4a-acd3c33b4045:0:2:0`
- `1128d2ab-0b6e-4912-8735-15521bc314e6:0:0:1`
- `1216900e-93e3-41a4-b354-9c81938639c2:0:1:0`
- `14079f05-fbc1-401c-9008-da678656b4c6:0:0:1`
- `1b9a5170-39c0-4cbf-a041-f3c15f1359ae:0:0:2`
- `247075c5-62f8-41a1-91b3-562ff0aabb30:0:0:2`
- `2c3ed6b9-1a2b-42ad-baa9-ee2a0ad505a7:0:1:0`
- `2d1bbeda-2e81-4aaa-9494-094ec3dd6c3b:0:1:1`
- `314a5c76-1a68-433b-a383-1834400254a8:0:0:1`
- `36ac8fc6-98ad-499b-9adf-046433e2c122:0:1:1`
- `37994591-3494-4314-a7da-49c112b0866f:0:0:2`
- `3a7fe095-8278-4b1d-bec4-19b35bdcdd1b:0:0:1`
- `3bed0b60-5944-44bb-9ddd-c82f323e6d20:0:1:1`
- `3dfeb0c5-85d6-48fb-b924-d7b77f4b89d6:0:0:1`
- `3f404fe4-4335-4dcc-ba90-78246c4b880b:0:0:1`
- `46515251-2172-4b0a-81ac-4c0120b73360:0:1:1`
- `468cfc88-a493-44dc-9d0a-63d9cc89c114:0:0:1`
- `4aa119f7-d411-4188-956e-547f7d14e789:0:0:1`
- `4c095e91-b6ab-417f-94f3-684e64259f97:0:0:0`
- `522a04ff-cbfe-47b0-bd29-ef6fc27a6905:0:0:1`
- `535916f8-b51a-4414-8ab0-fdccdefd9433:1:1:0`
- `57fe941c-a830-4570-afe2-18f93c7a7b84:0:0:1`
- `597d1dce-67e8-4c37-9781-eeaeb7c2d7b7:0:1:1`
- `5beb8d6e-d3c1-46a5-8516-d6bf66413cff:0:0:1`
- `5d65ba1a-3943-4462-9874-62a1afd45bcd:0:1:1`
- `69ae219e-bf97-4626-9b16-7901f51f0343:0:0:1`
- `6a521eed-0965-4fce-8a11-190dc2863da8:0:0:1`
- `6b530534-5c02-4874-9256-501102ef8a5f:0:1:1`
- `6c3faf4f-83c1-4098-98b8-bae15d59b0de:0:0:1`
- `6c87c261-00a8-46f2-92c8-42009a0a2faf:0:2:0`
- `6d776c7b-4ca1-48cd-88c7-dfbbe5a56a0b:0:1:0`
- `6e1aa07a-5d9b-4daf-8dc4-c1717360855f:0:1:0`
- `71d178b3-e5ca-4576-83f7-8dce74758acd:0:3:1`
- `73dad679-1edb-41c9-9d43-56dc93c3e9fe:0:0:0`
- `762f891e-5d88-42b0-8abf-c69f3421011b:0:0:1`
- `7b2a600b-d6c8-45ff-a7fc-06105d27111f:0:3:1`
- `7b89b7d2-c724-4d5d-9f0b-7d3302ad1168:0:1:1`
- `81036c9f-fe0a-45a7-bcd5-0d344f31055a:0:0:1`
- `82e61db8-4625-488f-8a5f-66ace9bbf34a:0:0:1`
- `85d81888-8df7-4826-891e-a14fb8bf6549:0:2:0`
- `8a1ccbdb-3d89-42fb-a731-6db4241acf24:0:0:2`
- `8dc1148f-c6bc-469c-8d1a-7e3efd2de7e2:0:0:1`
- `91b2ffe8-155d-4b9f-82dd-868cc895856b:0:0:1`
- `928c62fe-9c4d-4e89-bd7a-0d3b6a81f393:0:0:0`
- `92d6af2f-728e-4e41-87cb-5c90878a2f2f:0:0:1`
- `964c2003-cef0-4ac7-9f66-4e20893c8e50:0:0:3`
- `9aab4b32-c5b3-4707-b359-9b5e3b63cd11:0:0:1`
- `9fe75f56-c2e4-4c82-8113-039b8c486fae:0:1:1`
- `a30159ae-f6a6-4e29-bca2-769d3657d310:0:0:1`
- `a32795a2-a965-4a85-9944-fd9eed464e65:0:0:1`
- `a42b567d-6bfc-49e7-8f91-917e2bb3046c:0:1:0`
- `ad2a1b07-58f5-44c2-92e0-464ea2d45e7e:0:1:0`
- `b58737a4-180e-4e2f-95ae-afd6d446d608:0:2:0`
- `b5aae42b-3fde-4f10-b85e-882c528badef:0:0:1`
- `b707c131-de13-4d4d-839d-b9f47d62f090:0:1:1`
- `bfb3d862-d92d-4a4f-9a22-671b55d954fd:0:1:1`
- `c638957f-88bf-40c2-834c-2be39d73bf41:0:0:1`
- `c7ecaa1a-fbf7-436b-a1c9-d7810b0dc5dc:0:0:1`
- `c983644d-6741-4aa1-aa68-a6e680c26bb6:0:1:1`
- `cc2d016a-af44-427b-a25a-593274369449:0:1:1`
- `ccdf3399-b836-47ab-802d-af5a9c24d759:0:0:0`
- `ce807ee3-a27c-4f3b-92a4-37faaca42aa1:0:1:0`
- `d09aecc5-4f78-49f8-b503-677e84e36a6d:0:3:0`
- `d14f313c-fea6-49c4-8197-5b74ee584a6b:0:0:1`
- `d2db3f9c-26fe-487b-bbb7-8bc6f33456f1:0:0:1`
- `d4424585-9564-4ec2-8267-3f5438e1f29e:0:0:1`
- `d44f3724-17b7-48f0-885d-75292669f971:0:0:2`
- `d97553bf-6763-4a7b-8d82-1b438a22aa62:0:1:1`
- `dffa7c06-096a-47f8-9645-1ba7306ba5b0:0:2:0`
- `e42fb51e-254a-43ac-ad02-9f0fad0f4c8a:0:1:1`
- `e5d928dc-b465-4cf7-ab11-d5bd3328f8e7:0:1:1`
- `ed3d113d-f2c3-4ef3-8bdd-ed4824a22ab0:0:0:1`
- `efcaadbe-24e3-4dfc-b08c-a910f003d427:0:2:0`
- `f1354b1b-896c-4492-b0c0-3dd07c6d3917:0:0:0`
- `f196ae91-be5c-461b-a69f-aecb538923b4:0:0:0`
- `f474d244-d9be-4580-bf62-f97660e9c1a3:0:0:1`
- `f5dc3dbd-7eab-40f3-afe2-1e88a0c00538:0:0:1`
- `f72558f5-ac5c-4efa-b01b-439bc0bbf18d:0:1:0`
- `f7f8a186-313e-4a29-bf4e-b6a200dfd1ed:0:0:0`
- `f895ec2e-7481-4280-a5c0-38b58c440faf:0:0:0`
- `fa71db44-5181-4c51-8b24-7fbedf36e3ca:0:0:1`
- `fe16f1ab-58b4-4452-abe4-cbd9addd348f:0:0:1`

### die/part-2

- `1822f924-51ba-4f81-92cc-6c5d741a33f9:0:1:0`
- `4696decb-7bff-4c6b-8a7b-9ec324faefde:0:1:0`
- `5653b40f-c566-4a14-b188-a9268ea36218:0:1:0`
- `660f370a-b25b-4ea5-b765-7abf96899c1c:0:1:0`
- `c2f42c67-ff88-4248-bfa5-79a18c6473d5:0:1:0`
- `d04a836b-7e42-424d-9600-42a40d0dfccd:0:0:0`
- `d14c9d2b-41c7-4c9a-a66a-cda34d29c7ba:0:0:0`
- `e1cfd1cb-44a5-429f-a5c1-e6d29bad1c71:0:1:0`

### draw/part-1

- `06d60b71-a9f9-4a7f-ad69-15d760b6e5c3:0:1:0`
- `227ddf6c-d21a-48da-84fb-395c7e096914:0:0:0`
- `278e51fe-3cd9-4c82-bd81-2164771f8611:0:1:0`
- `2aa2f96b-5784-4767-b9ea-b8d9222cb1de:0:0:0`
- `2daee7cb-6736-4aa6-9921-0371c1abe69f:0:1:0`
- `2f533667-e29b-4bec-897a-e7a9eee08314:0:1:0`
- `33345c43-3e77-4d9c-a9b5-5d723e1e5c69:0:0:0`
- `378ae023-04d3-44cc-9248-3d787796ed6c:0:1:0`
- `3fe5cfcd-b25f-49d8-9f60-8b4c388a9c68:0:0:0`
- `3fe61a65-b1c0-4d15-b379-e4ce22c96941:0:2:0`
- `473a7998-669d-4181-83fe-f178a2e781f0:0:1:0`
- `47a080c4-ff04-4f52-aca0-2b8e4f4d931e:0:1:0`
- `51d517c9-2812-44ce-ab4d-e5422b5ecf6c:0:0:0`
- `51f55021-04e0-49bf-8f1f-de2a578c95fc:0:2:0`
- `523d3e3d-8fdf-44f8-868d-7b00995e4577:0:0:0`
- `5277a68e-1ceb-4b40-8e10-3d0564f5d7be:0:0:0`
- `58582fac-4c42-4a1c-9ab1-4a892b500da4:0:2:0`
- `5966c464-5f63-4c71-9317-e2ca79da5aba:0:1:0`
- `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0`
- `76d6d4cc-607f-4a33-a964-a38b5dbfe710:0:0:0`
- `7d1769d0-d942-45b3-a31c-2bbe45e68661:0:0:0`
- `7f5124a4-9ffd-475a-8b77-3ff59a9871a1:0:0:0`
- `8b34b211-985b-4934-bb3b-8e6672685ac2:0:0:0`
- `aa286dd5-aa19-446d-9003-684d81eb57ca:0:0:0`
- `af66da4b-2f36-4dd2-a5c6-18e6023c5aba:0:0:0`
- `ba4f9450-d468-4686-9f48-00fa08c6ac52:0:0:0`
- `c6eaa147-3566-43a9-999a-d58b877496f5:0:1:0`
- `c79b9187-cbfe-43a0-bdc8-4f7e0d215607:0:0:0`
- `c9a9550c-e6bb-4fe3-930f-6266024dbead:0:0:0`
- `d6c008c7-6c87-4677-ba0e-6d95f10d10bc:0:0:0`
- `e1bce9c3-300c-4a9d-abe0-a1f02d3a1105:0:0:0`
- `e23bf5fe-e494-473e-8502-606106ee1820:0:0:0`
- `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0`
- `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0`
- `f1fad5ab-d087-4912-b1b9-42733fa34707:0:0:0`
- `f515c691-07be-47ea-8bc0-46221eab8b46:0:1:0`
- `f8dab16e-1d50-443e-9431-8b6f1cf61c9c:0:1:0`
- `fbfa8b3f-58a7-44ca-8c22-6747b56fdcb9:0:0:0`

### draw/part-2

- `08f17ebc-c0fd-493f-84b3-e9250694543e:0:0:0`
- `1c9e1f75-73f0-4846-b53f-458a0984b1bb:0:0:0`
- `1e4032f6-9741-4845-9325-781c9e489172:0:0:0`
- `6454c457-a278-431a-9e8d-bfd1a966bdde:0:2:0`
- `692a6833-3014-42f6-b1ad-333bb3292c65:0:0:0`
- `888582df-4fe2-4d05-9b62-10c90aaa76f2:0:0:0`
- `a0380b63-58ef-4545-beec-6ad307bbc21b:0:0:0`
- `d5c4d36c-54b3-4149-906b-a57a670260fc:0:1:0`

### enter/part-1

- `01fc5bb3-ebd7-4ab4-8aef-2ece1e1d9b7c:0:0:0`
- `5733c3fb-c533-456c-b30e-5d2b9e206b6b:0:0:0`
- `5baa7abe-5bdf-40ce-9a83-a93b7cae71a3:0:0:0`
- `6c9a854c-0509-4ed4-9d94-c45b823b65e5:0:0:0`
- `6ee68855-c8c5-422b-88da-163c09a96416:0:0:0`
- `7647940e-c99c-401c-ad1d-9ec730f66b6f:0:0:0`
- `8b370db5-dfb9-4ea0-9017-bae3e767b041:0:0:0`
- `bdf476e5-1d57-4b17-b45b-d52fd75aadeb:0:0:0`
- `cd535fa3-6fd8-4227-97fd-3ef07cb0598d:0:0:0`
- `e3b8d70b-17aa-4a31-a4f9-319907d088c2:0:0:0`
- `f3c5978a-70fa-431f-933b-b954bd0db0ea:0:0:0`

### enter/part-2

- `808d5a67-8c38-42f5-9413-8771d8b4ae38:0:0:0`
- `8a76a9b9-3127-45fe-b20f-a8f643276281:0:1:0`
- `a11c6601-7e91-4def-bfea-bb34023ef3c6:0:0:0`
- `e9541db2-2874-4307-b896-c403f6d82e68:0:0:0`

### gain/part-1

- `02be0b99-d40b-4287-989b-12eb2701115c:0:1:0`
- `08f17ebc-c0fd-493f-84b3-e9250694543e:0:1:0`
- `240f0835-36af-4ad8-9336-d6d3d816d293:0:1:0`
- `2abe9303-d498-4aad-b6b2-8b5064bd2ffd:0:1:0`
- `43c31a03-2bbd-49a6-8b78-c5f3cab04a07:0:1:0`
- `4e9df979-c1c2-4de1-944e-c5e2d782e66e:0:0:2`
- `51b114cd-c174-4d74-a854-07c68b41fc9d:0:0:0`
- `5789520c-e4b2-44b2-b756-3f6b468dc55b:0:0:0`
- `635fe908-6f58-4c9e-ac55-0775a7c6f278:0:1:0`
- `7652f328-e142-494b-a869-772ced10c26a:0:1:0`
- `801e55c7-f8a1-4a90-81cb-3ad7022290ba:0:1:0`
- `9552fc97-9e6d-4307-bf58-30bf956356bf:0:1:0`
- `98c059ed-d749-4f66-bda1-6352976198f0:0:1:0`
- `b86d3142-568a-4eea-b1ae-5fcfc1453533:0:0:0`
- `c7ee79c3-a273-45b4-b3a4-548d9b2b883c:0:1:0`
- `d5c4d36c-54b3-4149-906b-a57a670260fc:0:0:0`
- `f0ead7f5-5c82-40fd-8e89-3e3c5d31fbad:0:1:0`
- `f297648b-0dda-4c58-a3eb-fdabdfb42177:0:1:0`

### gain/part-2

- `5b7515f2-7a5a-4e2a-9784-6cbacd768172:0:2:0`
- `d79e8ec4-b44b-4598-991c-7781dab55868:0:1:0`

### no-would:fateful/part-1

- `dd3cc9e5-b99a-429c-baeb-663a7af70081:0:1:0`

### no-would:fateful/part-2

- `ff45677d-977e-4ef5-859c-52393ed71a6c:0:1:0`

### no-would:ferocious/part-1

- `3adc3af3-5086-4d61-b38c-c1dddeaeebe6:0:1:0`

### no-would:ferocious/part-2

- `b0060b32-b856-4ff7-a113-cec2dc8f8dc6:0:1:0`
- `b8cf8614-14f4-4c20-9697-2e5ea34e0039:0:1:0`
- `e7871b4d-a408-4377-beee-6b1d3c7dd57d:0:1:0`
- `f70f1f2e-7277-4bc9-b0bb-b44a1da2c62f:0:1:0`

### no-would:if/part-1

- `0146de73-29bf-415a-b450-11074553f715:0:0:1`
- `0403bfb0-2174-4360-994d-68d8ca96fc55:0:2:1`
- `07159efc-c69f-4164-a8ca-9da641dbf702:0:1:1`
- `085bc7be-bd44-40af-8e8f-a1a8006fe22c:0:1:1`
- `12cc97ec-5d03-4434-a31b-51e77d208466:0:1:1`
- `198fed4c-297e-41c0-a172-e471c7401fbb:0:0:1`
- `1fb3b5a3-ca4b-4cbf-ab58-71c960f3efd0:0:1:1`
- `318f7f70-e374-40ef-8afb-3389c10461d8:0:0:1`
- `334c284e-7bc3-4c18-9f8d-4d846f80008e:0:0:2`
- `3686fd97-49ff-4a92-9cb2-7d8e9438d945:0:0:1`
- `3a0ea41e-b4f5-4aa1-9f7a-158485313c64:0:0:1`
- `3b06b242-caed-4c8f-b5ab-30e86061286e:0:0:1`
- `3ceca713-38de-4428-a4f1-2146f6e98393:0:0:1`
- `3d9f854e-1ee5-4aa1-a33b-d3ae08f15dd0:0:1:1`
- `473da1b6-232b-4428-a66d-30262246b47a:0:1:1`
- `495ebe60-f0e5-4f0f-9d99-b2c64c95dbf4:0:0:1`
- `4b2e9aa9-6f91-41de-84b6-e9a89be06a53:0:0:1`
- `4b803bf2-025a-4bf6-9d3c-a28d714b4781:0:1:1`
- `55c7ce94-3cd3-42f3-9dd8-0c118fa626c8:0:0:1`
- `60fc5eb0-95d6-49b0-a538-945ef599e484:0:1:1`
- `610af0f7-b5e3-43fb-9d02-7c59bd99034c:0:1:1`
- `62f4a2db-6d7c-487b-be37-22f06c1e779e:0:1:1`
- `6d56bd32-f47a-4e54-a88e-b69d16283ea4:0:0:1`
- `70d7d1a7-9d39-44ec-a4ea-a70ffa453d23:1:1:1`
- `71ac4d8c-5b58-4ea8-996b-f0289717c4bb:0:1:1`
- `7687b2a7-816d-4416-979b-675e35e235fc:0:0:1`
- `7a5ff4d4-27b7-47d4-ba88-970c63c4e3fb:0:0:1`
- `7c6e0198-edd8-42b8-ba1b-549e1713d188:0:0:1`
- `7f420633-901d-47f9-ae0f-0f5b0ea8359c:0:1:1`
- `87f82107-eaba-484a-800d-e61a0cc5e1f2:0:2:1`
- `8fa0fe02-2452-4386-8e0c-165757b0f0a3:0:0:1`
- `929117cd-caa6-402b-9d7b-1f684d75695c:0:1:1`
- `93ab7462-ceef-4bc7-a9fe-8af8ceb78e1c:0:1:1`
- `9cac23a1-a0b3-490c-aea2-dc2928f6dc9e:0:1:1`
- `aa854d50-444c-49d9-bfb1-5476b33c1c0b:0:0:1`
- `ac2173f9-f223-440a-9231-fd98762bdc6f:0:1:1`
- `b1c8fddb-d686-4b4a-8aff-d79ea747801c:0:1:1`
- `b665a64b-4772-42dd-9fd2-fd8598e689ba:0:0:1`
- `b981af39-4ee6-4fbc-9a89-618dcad9dfbf:0:0:1`
- `ba5a7ac0-b625-42e9-af05-2680a01a95ed:0:0:1`
- `bb377cf8-29ee-489e-86a9-93f4dc2ae02e:0:1:1`
- `bbbb80bd-76fa-4155-929b-4a3565d1cb35:0:1:1`
- `bbe370ba-412b-4052-89d9-2d0ae4928118:0:0:1`
- `be14d3be-295e-431c-b891-590164b730dd:0:1:1`
- `bfaf376f-90f9-45d9-bfbe-dd84a2a4688b:0:1:1`
- `bfcffe67-7db6-41bb-bfcc-400cbb8c8a9c:0:0:1`
- `c01411e0-77b2-4e65-a369-5dbe13745769:0:1:1`
- `c0dda0d0-1fae-4777-ba86-9fe7990bf3a8:0:1:1`
- `c23aaf6d-151e-481a-a345-ca00c14940d1:0:1:1`
- `c68964df-51ae-43b0-abea-74735016c13f:0:0:1`
- `ce6f3c67-8806-416d-9156-6f5bb63d5f4c:0:1:1`
- `d6cba688-faff-4d9f-8148-37d389fa5fb3:0:1:1`
- `d799a2c4-628a-45da-b9ca-0337c46e3e14:0:0:1`
- `d95f1797-56f9-41be-a5fe-8398961f4b8b:0:1:1`
- `dc9ae094-139f-4f28-9d4e-4d6def765744:0:0:1`
- `dcc59bd6-2c5f-48eb-8008-83ce6eb5a442:0:1:1`
- `dd3a4b64-0987-4e9b-a18d-c54365438857:0:1:1`
- `e22824cf-07a1-4c83-b6c4-9d8fcff3892f:0:1:1`
- `e83a629e-2d74-48e2-ad4d-f390067cc51a:0:2:1`
- `ead1ee6a-e0da-46d5-89e8-31e8c0270bc2:0:0:1`
- `ee2ef1e0-6803-4eb5-8664-605438c67505:0:1:1`
- `ee524e82-35c4-4cae-b65e-3e147eac2927:1:0:2`
- `f58117e4-ba85-41b8-8fd5-4245716a84dc:0:0:1`
- `f63c2438-27d4-449a-828f-f0a2ea86ff16:0:1:1`
- `f73da5d8-fd15-4315-ad3c-c86c28087285:0:1:1`
- `fb60739e-1dc3-481d-a056-ad72e665c680:0:1:1`
- `feb221fb-59bf-4671-a53f-1bbe8e9c2ca9:0:0:1`

### no-would:if/part-2

- `0221330a-3e7a-40aa-9c78-85c88a4c1a53:0:0:3`
- `030b5408-f216-43e4-8593-f78d22821876:0:0:1`
- `04fd8c1f-80e5-4b3d-b63e-7af6ccafbbaa:0:1:1`
- `054c6250-ac96-42f6-931d-925761ab7764:0:0:1`
- `05b6f9e3-9acd-43a6-acff-caa811aaf0a1:0:1:1`
- `0611beb7-a38d-4fbf-af9b-ee2a5b9a2896:0:1:1`
- `07634620-a83a-4ca0-8a60-2a21368a2661:0:1:1`
- `09027657-bc9a-4702-88c1-e5b3534ad188:0:0:1`
- `0b085c90-95df-4823-ba67-9eb398b1ec94:0:0:1`
- `0be4bf5e-1c93-49ea-a568-209638bf738e:0:1:1`
- `0efe1357-bfbb-42c0-9cc9-6a919d686c66:0:1:1`
- `0f35cf85-6783-4d69-b5e6-a81f7c1f21e7:0:1:2`
- `0fd114c4-092b-4e28-b0dc-ef529f3bc73e:0:0:1`
- `10185447-a13f-40d8-a8b6-39ce801f2fc0:0:1:1`
- `10d33e95-3e5d-447e-ba4a-acd3c33b4045:0:1:1`
- `11293f96-3263-45e5-89fc-850df6b25a63:0:0:1`
- `123d002c-0004-4e0e-80f3-f0f9555201ac:0:0:2`
- `128170ed-c86a-4f02-9244-28197be90c10:0:0:1`
- `1322734c-3c3e-4885-a6d2-d6460a16fca2:0:1:1`
- `13ebe447-1f8f-4b12-9e35-9d334a863c19:0:0:1`
- `13f58292-9b78-4cd1-a16e-b1779a170d33:0:1:1`
- `144d0817-348c-4171-aa7e-3468b23cf97d:0:1:1`
- `14d06354-4827-41b4-a9b7-e1cd89dfaf40:0:0:1`
- `1551fe97-437e-4e89-a0d2-c398cb2155e4:0:1:1`
- `15d2176b-ab3d-4738-bcbc-bcebf891d16e:0:0:1`
- `1779af8e-38fc-4043-b5fa-ee16a7ea840c:0:1:1`
- `1954994f-17bf-4ea5-af72-60f9bfcb6569:0:1:1`
- `1ae29791-aa7c-4050-bf72-dd0f739b11b8:0:0:1`
- `1b065a17-14a4-433f-a6c8-2c8212f505c7:0:1:1`
- `1b721ad3-d0f6-4eec-9bf0-f57ea9dfa392:0:0:1`
- `1e21e57e-3bc9-41a8-9746-57b583a5ad63:0:1:1`
- `1e46c709-5278-44f3-9f0e-f71bd9558339:0:0:1`
- `1ee3753c-3b6e-4182-9305-2ab757f485f0:0:0:1`
- `202b275e-e0c4-482d-abe9-c5e6360208f3:0:1:1`
- `2069145f-d8af-4386-a874-52a2efb8c7a9:0:1:1`
- `21989fad-9672-46d4-b7d5-101906e7aed2:0:1:1`
- `224f5f1a-4f31-4935-bf5a-910fd0a666a1:0:0:1`
- `2586a59d-8501-4c22-9d69-f4bf91de7024:0:0:1`
- `277757c6-4c4c-4a4c-84f6-4a64fe3b3bfe:0:1:1`
- `27905301-333e-4cdd-90cf-188159fcf8e9:0:1:1`
- `2ab88c99-aaa0-4a91-9225-0bbfba04b6bc:0:1:1`
- `2b34b361-7b0e-4464-874c-ceb501bc5ecc:0:0:1`
- `2b87bcac-ec64-4012-9e75-f459d3640eb3:0:1:2`
- `2bdb2495-cc67-4750-a300-7881b0346514:0:0:1`
- `2c3c3bec-00f0-4de2-b929-73f1c9276ec4:0:0:1`
- `2c3e6377-d09c-46b6-8a83-ada4a2930b14:0:0:1`
- `2c42983e-f45a-4d10-afe5-d2234dfae1ee:0:1:1`
- `2c6b2f4a-4e0e-4dc1-92a8-c07e5cbba5f4:0:1:1`
- `2e5e0abd-38a6-46ca-b922-556db52f1332:0:2:1`
- `2e80d632-cf84-4562-8c93-5850cceb5bec:0:1:1`
- `2f995678-c315-4afe-845b-8c8ae863de6e:0:1:1`
- `32fbb638-ab14-4e8b-a07a-d4c44e3496f2:0:0:1`
- `33e85a8a-86df-4cdc-a9cc-8cbabe92c3c0:0:0:1`
- `34428f42-03ac-4795-8286-6cbea796df2b:0:0:1`
- `36330947-5ef9-4bff-b541-bfbddd9715a3:0:1:1`
- `363f8c66-fe0c-44b9-987d-1d160e3f9c54:0:2:1`
- `393a5d32-fc8e-422b-a957-59e545a54cb6:0:2:1`
- `39f2a632-30d2-4b35-9e7f-fef27713a4f7:0:1:1`
- `3cbdf37b-7fe3-4791-b33c-8591158b0ce5:0:1:1`
- `3e2034ee-adc5-4a24-9605-c9722bf813c1:0:0:1`
- `416c70ab-f136-43e0-b5d5-9af8d4211c01:0:1:1`
- `4236851b-5366-43a1-bde4-f525b4fbcbce:0:1:1`
- `42b10f0f-19cd-45d2-a2db-d5463ddc5e5b:0:0:1`
- `43b5794a-4ed6-471d-bc45-22fac486895d:0:1:1`
- `45c4e67c-e452-41c5-8baa-050819a1321f:0:0:1`
- `4728e320-d29b-4019-8ab5-e45319c77c40:0:0:1`
- `4ae15bd1-e0ea-4c1a-a311-dae421381ebc:0:1:1`
- `4af2e62f-150e-4fd0-98b0-c6e72f5f9a51:0:1:1`
- `4b0b4d16-1d2b-497e-a1ae-bfb89eece665:0:0:1`
- `4b1befff-48fa-47a3-832e-bdaf43495c02:0:0:1`
- `4c11bda3-903f-4b7c-9e5e-f6c5c91977cf:0:0:1`
- `4de71245-9d9b-44ca-9c13-37dc3dfbbcd5:0:0:1`
- `4f429b99-6aca-409f-9d2e-5743d81f1f22:0:1:1`
- `4f6e2e47-34df-4bf3-a546-e06b42840167:0:1:1`
- `51a0d1c2-ff29-4ac9-84a2-ad4f566fee8d:0:0:1`
- `51f091a7-9b0b-4362-8e9c-c174752f369b:0:1:1`
- `51f17fe1-1cf7-4362-b9a2-8ec225d41b03:0:0:1`
- `54402930-84ea-4c3e-9880-ca631e47485f:0:0:1`
- `55eb9310-f24b-410b-850b-a7d0d5117946:0:0:1`
- `573a3afb-3a2a-41b7-ac1a-9685b90bffa3:0:0:1`
- `5bb38d08-582e-43aa-9507-7c20759978ec:0:0:2`
- `5be6f245-31cf-4294-ace0-ca6ce3463fed:0:0:1`
- `5ea1d89c-8650-4373-9835-e369587020ef:0:1:1`
- `5f2be3c2-060a-43e1-b63b-9cd3c78ffcb0:0:0:1`
- `5f97d49c-d0fa-4776-9455-93c1a172cd83:0:1:1`
- `5ffed544-1656-4753-ac8f-ad8fb4442c7f:0:1:1`
- `616c7f45-5295-4b8c-a828-ff3a5ba4d917:0:0:1`
- `624bdbfb-b611-43b6-a3c5-cc8b11dbfaae:0:0:1`
- `639926c1-c4b4-4a49-b125-0e1b584c5bb8:0:0:1`
- `63a85361-56bc-4209-aea8-b49319bc7b92:0:1:1`
- `645ab3c7-ee1d-4dd0-811f-2dc7f7c7e792:0:1:1`
- `647e5639-6339-48af-af96-e48729e1cad3:0:0:1`
- `652e71a9-e46f-41b3-8695-76b3606b1955:0:1:1`
- `675de007-a71e-4036-8204-140c67871b7f:0:1:1`
- `6798163a-864f-4844-96b1-77585a7e7ab4:0:1:1`
- `67a48e3f-2388-42a9-a8b1-97c08761f807:0:1:1`
- `68979160-b5ce-4787-8a1e-1f40e614c3b0:0:1:1`
- `6897f9e0-f654-4c0a-9fda-2ad4e264bf9a:0:1:1`
- `6a6b19db-cdeb-4922-8642-5d872f90e7a1:0:1:1`
- `6b5d1b0a-544c-41e6-bc32-c2b0c9bb4576:0:0:1`
- `6b73f05a-de8c-4e6f-abc0-e66325613e1f:0:1:1`
- `6bdbe36f-b46d-4746-baf2-04f0977bb532:0:0:1`
- `6c0e22f2-f0f3-43e6-87c5-c543032112d8:0:2:1`
- `6dff1d15-604f-4eea-9b7a-0c0ba6afbbac:0:0:1`
- `6ec54d84-7026-45a3-a7d7-37cd5c9a8463:0:1:1`
- `6fc26faa-94a8-433f-8863-126c2d2e73b0:0:0:1`
- `7237d607-2613-4786-96d6-55792c2e02b9:0:1:1`
- `7246638e-0361-40e3-8019-3c10210a593e:0:1:1`
- `736017e2-bc33-49e8-812d-1639443fdb51:0:0:2`
- `743fa824-18cb-4225-ba7b-5b0bbc3c8d41:0:1:1`
- `755bd5d8-67f1-4f24-a4e8-d98edf2f2e03:0:0:1`
- `75c626fb-9dfc-4a94-b59f-f0e45c7b2f56:0:0:1`
- `75f77d67-6702-4311-870c-0209d3a687b6:0:0:1`
- `760e8561-4ec6-4594-ba5d-f79cb9f25fd0:0:1:1`
- `78301998-fd9b-4cd5-afad-dbcb43cac2a7:0:0:1`
- `7857c7b6-9676-47ac-bb28-d0b4cbda5fa7:0:2:1`
- `7a56bdd4-f70e-4abf-9cb7-1624be3288ce:0:1:1`
- `7bc53740-86e7-4e9d-aab6-b5ae62a42133:0:0:1`
- `7ca9ef3e-e5b2-4eb5-87b3-0d97637428a0:0:1:1`
- `7cc4a635-8730-4018-a8fd-b29fb5479928:0:1:1`
- `7de66ba3-6e97-4e0a-928e-7ce45dee278b:0:1:1`
- `7f527852-bf7d-43a3-be0b-784c73ed88aa:0:0:1`
- `8089c3eb-99a8-40ca-882a-c1d4e30075ee:0:0:1`
- `819a7235-b61a-49d7-a0ad-3d8bbf83091e:0:0:1`
- `845b40b1-dc09-44fa-9910-22544c1424ba:0:1:1`
- `854fd120-9a51-4d37-9922-7e4b0464e0f5:0:1:1`
- `8574f57a-768d-42a0-ac8c-cc0a1de181e0:0:1:1`
- `85ac3efc-5e19-4661-b52f-116f57e39581:0:1:1`
- `867b3923-692c-4444-a071-518a290e43d8:0:0:1`
- `87864421-505c-4bdb-b1e3-3e44e05f2beb:0:0:1`
- `888f58c0-1860-4df4-ad75-53e634150680:0:0:1`
- `8985e545-07c3-45f9-9058-fe3c1f50de04:0:0:1`
- `8a83d284-75a0-4901-b7d9-c4b7586ee327:0:0:1`
- `8bba7c7d-6110-4d7f-8b28-3c5b9d3448df:0:0:1`
- `8ca4ca66-30b1-4074-a2e3-545b7682381b:0:2:1`
- `8cb36a67-9206-4665-a03f-64f52ba559c4:0:1:1`
- `8d4e0866-d8f5-4eb6-a0fd-3fa9d4b9cf4a:0:1:1`
- `8d4ef98d-228e-41ff-9133-53f0987e58d8:0:0:1`
- `902eb71f-62b3-40cb-816b-f6b7e92e91e7:0:1:1`
- `906881da-6bb3-4a0e-9bd1-d1a5bc484144:0:0:1`
- `938c03fc-8adf-4c7a-8ae1-eca8401f7a83:0:1:1`
- `93af8f9d-6877-4cb8-a744-c89186db22e1:0:1:1`
- `951a0e34-e610-477f-b441-6680df55a29b:0:0:1`
- `9588a7fd-bbe5-4a81-9a7e-d8e8f6c0537d:0:1:1`
- `96480e86-70a8-401d-abf8-a7d509311b73:0:1:1`
- `96c65faf-859c-4436-a551-5538409a9792:0:1:1`
- `983caa3f-7089-4e66-825d-4086a5adb9bb:0:0:1`
- `99915b5a-5092-4900-8824-6de2aab1b2c1:0:0:1`
- `9ac62ff0-6d13-4091-ba84-fbfbe742a4f4:0:0:1`
- `9b44c005-6799-47fd-8b0d-7179b5281d78:0:0:1`
- `9c348bc7-e6e1-40a2-9798-6d2c4a2d8e72:0:0:1`
- `9dbc2fc8-ed42-4534-9676-bf0695cd518c:0:0:1`
- `9eff1ce5-41e4-4ae6-9480-2b549c8546bd:0:1:1`
- `a151c45f-0b9e-41af-90b3-fafa12e3bbce:0:1:1`
- `a1fc4269-f3e4-4a59-849d-aa1727eef23a:0:1:1`
- `a2b6faca-3321-45d2-a027-ff3a8ae61f10:0:0:1`
- `a32860dd-e8df-4a3c-bdc2-948dcd07cf9a:0:0:1`
- `a3b8a08b-5409-4d5f-9bab-8a7a6376a5b9:0:0:1`
- `a45762af-4aac-40b3-a983-ea441b04c5ee:0:1:1`
- `a5ca7bd9-0964-405f-adb9-7c27153595e6:0:0:1`
- `a5e28749-18ea-4a2b-b7d9-905cf2913d4e:0:1:1`
- `a6e12be3-4166-4bd7-8254-e28b7c8588c7:0:1:1`
- `a9282f91-638e-414b-8b3d-9a99e30aec96:0:1:1`
- `aa00c18b-8719-4095-940a-8e35a57b46c2:0:1:1`
- `abf8264e-d020-4939-8092-83469b1a2244:0:0:1`
- `ac2086fe-98ee-4280-9c7c-c5c2d6548a8b:0:1:1`
- `ad8b90c0-4c66-4fc6-a749-cd10e6deabdb:0:0:1`
- `adc1f850-9217-4a90-8e6a-02ed226ef8df:0:1:1`
- `b11c250c-f191-4c52-ba02-a9176f163447:0:1:2`
- `b23c1f40-291d-43b3-971d-97ded8b367cb:0:0:2`
- `b50a6db0-16ce-4e98-afbd-ec37e1653e7c:0:0:1`
- `b5208c2c-b839-42f6-8717-ee4bbaf1385b:0:0:1`
- `b5c8e24a-f4d7-42dc-8117-905ad0bad888:0:1:1`
- `b613ab11-e173-4a68-8d0a-ac5f09a4db28:0:1:1`
- `b7d7c131-b628-4b35-b40b-1087589ebdd0:0:1:1`
- `b8647f54-f50b-4bc6-bd44-fda25ef189fa:0:1:1`
- `b9a0977a-6364-4358-bab1-112898a1b942:0:0:1`
- `ba0a815c-1dfe-47c1-890f-496c670124f3:0:1:1`
- `ba9ac0a9-735d-4bca-9d24-586aca963872:0:0:1`
- `bad5b8d4-9089-4ebd-8eaa-07552737c527:0:1:1`
- `bbfb3e4a-b389-4391-8141-13b68c0ef2e0:0:0:1`
- `bd581eb6-1a12-4985-9a41-65c5c322d849:0:0:1`
- `bdf4c82b-b3bd-4d57-8c2c-c99f1270577a:0:1:1`
- `be0c9947-3e7c-4b53-b87c-ff16ffd668ea:0:0:1`
- `bf3a0585-3976-4078-8beb-6afa79f97027:0:1:1`
- `c0adbddc-b070-4c5f-afe0-0474c72a9251:0:1:1`
- `c1c62704-1f20-48cf-8588-47e7fca85f7b:0:1:1`
- `c6901a89-ac7d-4797-a027-97bb1cf42e60:0:0:1`
- `c6adfaa7-d9cf-4501-8e7d-e035369390d2:0:1:1`
- `c70598e1-30c6-4f92-a265-34a7a73bc2b8:0:2:1`
- `c8110200-209e-423a-96b7-81a3ac32447c:0:2:1`
- `c9b1557b-70b1-44f2-9fc2-7aa0b035b187:0:0:2`
- `c9db6b94-a7b1-4b93-b454-4dead8f85e34:0:0:1`
- `ca3cda24-0ecd-4edf-b1b3-54311ad58a51:0:1:1`
- `cf3234f2-09d7-4d8b-b871-3bf0fcb75b6d:0:0:1`
- `cfe4d707-41b3-4897-b13a-dcae8f1f3350:0:0:1`
- `d0d844f2-6cf4-49f2-95db-64e932a15b17:0:0:1`
- `d21994f2-75e1-456c-a25a-729c3269df1a:0:1:1`
- `d2bd182c-532f-4c77-adb8-754f2c2fcd82:0:1:1`
- `d32c9439-4c97-412b-83cc-6d9acb48be3c:0:0:1`
- `d3cec4b5-bc93-44a2-a29d-3478f0a5dac6:0:0:1`
- `d4ab7848-5c37-4c6b-be29-0bb703333e5b:0:0:1`
- `d4e54b48-956f-4467-8485-a5fdb44779fd:0:0:1`
- `d533b356-ffa6-44b5-a501-a06954b9345b:0:0:1`
- `d565cd3d-68d4-4039-9e45-7e69e31d0ffb:0:1:1`
- `d6d236c5-b537-4428-b438-7a60a251297b:0:0:1`
- `d71cd08e-3e84-41ff-b9db-9e343c0af6b4:0:0:1`
- `d7562f89-4808-44ab-8dc9-fc4078e8a47b:0:0:1`
- `d7b49bee-2cb0-48e1-91c1-1e150a0da6ed:0:1:1`
- `d851312f-8b4e-4d8e-bfee-c470853be930:0:1:1`
- `d8df9813-0376-4d30-8cdc-30451fb67726:0:0:1`
- `da522912-1bc2-4d70-b426-94d10edb2afe:0:1:1`
- `daec03b6-e3f8-4e44-9766-c64dc23fa3dc:0:0:1`
- `dbdd93d2-f2c6-43f9-93e6-2185c7df83bc:0:1:2`
- `dc39c52b-9bee-4cec-a970-1867314944ef:0:1:1`
- `dc665ddc-4326-4860-94ba-c40ced8b0af6:0:1:1`
- `dd06c11c-c4fd-414e-ac63-5556f31491f5:0:1:1`
- `dd886509-7455-4c8f-976f-0f5fafcb97be:0:0:1`
- `dd893746-e8bd-49fa-a1ce-755d5bd4f513:0:0:1`
- `ddf461b9-a205-4dc7-a9c3-c047b1ff709f:0:1:1`
- `dec281b4-e6d6-4b78-b755-358e07eb7c06:0:0:1`
- `e0f0f290-c83f-4d97-9f5d-786c7136b0d1:0:1:1`
- `e11966cd-2ee3-4df4-b099-abf42dcdf0db:0:0:1`
- `e3d08582-85ba-48c4-a453-4a5a385a0c3e:0:1:1`
- `e45a1c99-a020-49ab-8971-35c6bcd096c8:0:1:1`
- `e4648fa3-0343-414b-b04d-07fe0d132145:0:1:1`
- `e46d0b57-5eec-4ab6-b9a7-a5c5cc01cc34:0:1:1`
- `e50fecff-8872-42f5-8882-41ad13d9d1ae:0:1:1`
- `e536e0d2-7117-4ca8-bdb4-e7dd380113c6:0:1:1`
- `e55d9377-f89a-41e5-a094-730d6f24caf0:0:1:1`
- `e6521404-8474-4727-b2d0-537d15d8a63f:0:1:1`
- `e7194bca-0cf4-4a86-8b84-d2f9219a08b3:0:0:2`
- `e921839f-9d91-41a9-bc89-016af3c757aa:0:1:2`
- `ea46835c-9dac-4e1e-8338-ad99136f511a:0:0:1`
- `ebd6a3a0-ae8d-44e6-8d0b-048da6dd1f03:0:0:1`
- `ebe1448e-21c5-4b73-8296-03d3e5097c50:0:0:1`
- `ec7d550b-9e13-4249-89c7-6ad43f71ea11:0:1:1`
- `ecd49d85-9c8c-4cc9-9a83-072ecd433677:0:0:1`
- `edbe4fdf-9e55-44fa-b3ec-5b1ac615f3a7:0:1:2`
- `ee3d1f44-e0ca-4ce9-be76-4b675a115156:0:0:1`
- `ee3d21b9-58b4-480c-bae3-26de50f1a5c6:0:1:1`
- `ef2aa67a-9531-495c-85c7-7f745bc19ce1:0:2:1`
- `f034e8a3-82f7-4c70-93ea-0bf2688f66e1:0:1:1`
- `f0d1636e-6f80-44fe-869a-1749ab249815:0:0:1`
- `f0d8bde1-76db-4bd2-ae90-3e3a3418de0b:0:0:1`
- `f1993767-1d07-49c8-b8dc-04ec9840a999:0:1:1`
- `f2b376d2-a2f4-4d23-a1fb-eb7b6ebd0b7a:0:1:1`
- `f2b4f37b-270b-4746-83b3-51ff88ee3491:0:0:1`
- `f2b88031-bfb7-46c4-abdd-3b6b5f5acfa4:0:0:1`
- `f3ae58ed-8ef7-4e0a-945f-1f622157236b:0:1:1`
- `f6abd7e5-8c52-4b36-98c5-a4df8b5b6863:0:0:1`
- `f701ada1-e9e1-42ce-9a62-c11bcec03da7:0:0:2`
- `f7a8066e-f8a4-4202-8825-0327d11e58c3:0:1:1`
- `f87df7d4-99e2-4340-9d0a-b96c397555db:0:0:1`
- `fa4755c2-e573-45c3-bd6a-61b2b35fbd24:0:0:1`
- `fd949f82-fc10-4e37-8aa9-6c7569fe3c55:0:0:1`
- `ff52f955-98de-4f12-9ec7-f1d73e3edae9:0:1:1`

### no-would:if/part-3

- `100218ce-1572-4bce-bb00-d2df5f68705c:0:0:1`
- `18ac2282-83af-4acc-b20b-6a95771da688:0:1:0`
- `2441696b-a9ba-4813-ba2e-e71f85281d05:0:3:0`
- `2c189e3b-90d3-49b4-bebe-a4f14c8a275b:0:0:0`
- `2c6f9fdb-ee27-4cd8-9d4d-1ea8b2830f73:0:1:0`
- `31af78dd-e962-4d9a-b696-f3048be03486:0:0:0`
- `3b7e7a11-bf59-413d-8796-640d17c2c1c6:0:0:0`
- `4013b4c2-c9ed-4d14-90f0-97214ec1fded:0:1:0`
- `5b04a337-3152-481e-973f-a11dbd615f93:0:3:0`
- `728e2960-1d85-4b3f-8b5b-915f9b9ffd2f:0:0:2`
- `867def48-4be8-4056-bcf1-d6b00450b9a3:0:1:0`
- `8b610f8f-c8dd-4eeb-bc6e-3bc706d5f63e:0:1:0`
- `a3a8a044-283d-443e-bc40-c2f826d70c22:0:0:0`
- `dd1ef824-4e61-4dee-a8f0-9cf459008f2c:0:0:0`
- `dd821fca-79a0-48a9-b1cf-5a496bc04f65:0:1:0`
- `e0587218-206e-41ed-af3c-f06b7a668e90:0:1:0`
- `ee2ab1ab-be1e-4e56-99f2-7784f7350b41:0:1:0`
- `fb5ec55d-4a35-432a-be6e-c295f1b2e603:0:1:0`
- `fd50d76c-7654-47b9-a5b6-d075874e4357:0:0:0`

### no-would:landfall/part-1

- `3708eaae-9306-46b2-ae41-7ce6c50be3c7:0:1:0`

### no-would:landfall/part-2

- `4b3bc59c-5439-4ec8-b25e-7493fa1cd3fd:0:1:0`
- `74b08a70-b0bb-4340-98a0-b1d5b7c9d2cc:0:1:0`
- `c7f08962-6c54-4fd5-a55e-7513e758af32:0:1:0`
- `ddbacb74-1f98-4607-a92e-d14973b9d0ef:0:1:0`

### no-would:spell/part-1

- `27c84ad1-1491-459b-bf8a-0146062084dc:0:1:0`
- `8f31d870-872d-4671-80d1-8d2ecd2c38d2:0:1:0`

### no-would:spell/part-2

- `a3a26df4-a9d5-48f5-942f-76862bdcd146:0:1:0`
- `e83236f8-1c45-4d31-8937-1c76db549955:0:1:0`

### no-would:whenever/part-1

- `0757c5a7-e51b-4c39-bb4d-b32657c10cb4:0:1:0`
- `9207facd-fbf9-4faa-ac44-6c0bcac81551:0:0:0`
- `aa219936-661b-4ccb-8741-78b70cff2b1a:0:1:0`
- `cbad35cd-9026-43ea-8333-94f3b34459e3:0:0:0`
- `d32345c1-ed20-4bfc-a5fa-6ac7b99542ec:0:0:0`

### no-would:whenever/part-2

- `e23cd06d-1360-4e5d-aecc-adf902bede69:0:1:0`

## Reads

Every member of every row was read; each list holds the whole row, every READ
POSITION of its class included.

### add

- `efd9cc25-f445-4de0-9a69-adab9f8878f4:0:0:0`

### assemble

- `4d614c79-7934-4662-9ce1-22b57d5137f7:0:1:0`

### assign

- `05ac866d-0405-4d25-986a-c10fcfc097e6:0:0:2`

### be created

- `12a6cad9-eb42-43bd-9e68-aaf862cd83db:0:1:0`
- `188da0ad-8524-4fb2-915e-1876dc9df89f:0:0:0`
- `1ba2f763-5895-4663-b38f-95591ebb2ef4:0:0:0`
- `2acb15bd-6c89-4ff3-ab32-beac67e9c88a:0:0:0`
- `2ef53e18-0baf-4eee-b671-4c19b464cbfb:0:1:0`
- `43febbcd-ecbe-4edb-ad90-7fc6dc381d05:0:1:0`
- `486bb9a5-73f1-4cec-b097-fb07ac80b72e:0:1:0`
- `5917216f-5b42-41fa-8976-401bdbeb782e:0:0:0`
- `5f04d4b0-2c75-4f2d-97d5-96220b624b17:0:1:0`
- `68d3084b-0f4b-44a6-8954-6ebaf1db9269:0:2:0`
- `9070c98b-fd01-4eeb-a4ec-fc464946c7c0:0:1:0`
- `c665544f-557b-4631-a1dc-39571470ca2e:0:0:0`
- `e0edb2fc-2533-407c-85e5-4337f4233f05:0:1:0`
- `f15b3b76-d38a-48db-bb44-3296183c8641:0:1:0`
- `f78af825-023a-42e9-8374-5c52303a1417:0:0:0`
- `fe83087d-c6c1-40be-9295-baaa1c6b2db1:0:0:0`

### be dealt/part-1

- `03c47f1c-02a7-428c-a126-9e85325ebc71:0:0:1`
- `05775dea-d7f0-4e0b-af4d-ba8d320dc4c0:0:0:0`
- `09b9e6fd-7a61-4ed4-a121-61b64fbf03f4:0:0:0`
- `0e69e6c2-fdc5-4c1a-bd96-c4283b82743a:0:0:0`
- `0fe4767b-2023-49fc-bc93-b73b43f70b76:0:1:0`
- `1245b165-e26f-4839-8468-2e95148fc6f6:0:0:0`
- `184fdd23-8235-4500-b2f5-d3b0b93a8f35:0:0:0`
- `1af63a5e-2bec-4f8d-a373-d9ce43a7d242:0:0:1`
- `2c5c8250-1860-42a1-a335-071f54830d37:0:1:0`
- `33e88072-3840-4090-8d0b-7fb38279e150:1:1:2`
- `35844d8b-8f68-4248-b921-e766757a9e26:0:0:0`
- `3a105959-dfce-4202-b37f-ae635dfcb30b:0:2:0`
- `44ae1c25-8622-4a58-92e0-12d76f084718:0:0:0`
- `45f3b9f2-3fce-4f91-bcbd-de069e5f9e4c:0:0:0`
- `4d9d5dbb-25ab-41a5-a277-3ee5f9ef579b:0:0:0`
- `4f5a7b65-b7f4-4bad-acfd-35edfb8f86a7:0:0:0`
- `50ddbea3-7ef4-4f6a-83c9-0c3ea1dfa3c9:0:2:0`
- `5b3f6817-5d7a-4d83-ad1d-df75b4e1970b:0:0:0`
- `644b7aba-a7b8-4861-9e83-73329cf85be2:0:1:0`
- `655ae8e7-372b-4d8d-b33f-4aca46831abb:0:0:0`
- `6e49a5b8-6bc4-4c7b-82c1-957f1fb0ca5f:0:0:0`
- `7ca54a23-f8eb-4982-b4ee-7392e2f2a1b3:0:0:0`
- `7d84e667-2f14-437c-be4f-161b98d59341:0:0:0`
- `8137e765-4df9-469f-a527-dee91d58fb7e:0:0:0`
- `84050a10-e1f1-413e-aa21-5c1f47bb2a64:0:0:1`
- `8429ba6a-6c06-4a83-a6ee-023b64b825f8:0:2:0`
- `86d0ba9d-6972-4cbc-871d-3fb413565c45:0:0:0`
- `8bc5546e-554f-430d-80b1-99578b5ea188:0:2:1`
- `9c058107-b2a1-4300-8d97-c697c248df96:0:1:0`
- `9e60c102-412e-4956-a7bb-a2cd737d6692:0:1:0`
- `a8b93d4d-bb67-4063-ac6d-7775be1b1f10:0:0:0`
- `b7902113-9ddf-4d81-a76a-b54b8a36c154:0:1:0`
- `b8d395a3-0bfe-45c3-bb3a-820d4f235b88:0:0:0`
- `bd5ad7c3-4477-4278-9875-d2ffbb0e8089:0:0:0`
- `d29078c0-1fb8-437a-81d1-bb319f646941:0:0:0`
- `d3088e1d-62c9-4478-9ef7-fc3c9e5cfadb:0:0:0`
- `d748bad4-dd4c-4553-9fcc-e462260f6ff3:0:1:1`
- `d79e8ec4-b44b-4598-991c-7781dab55868:0:0:0`
- `d830a136-6fb9-42e7-81f1-97e1d713ee82:0:1:0`
- `dfedb968-f27c-4117-aff6-da707dd43e82:0:2:0`
- `dff66bcf-e126-49d2-b67e-ea3b0a38d390:0:1:0`
- `e02164ba-34f8-4a5f-a05b-dd3ef3f8ceae:0:1:0`
- `e03b553a-3d0d-453e-ad3e-f7d4b9fb2624:0:0:0`
- `e6873252-653a-47a8-99b7-b2ef70aa1f7f:0:2:0`
- `e85f6251-8801-414b-adc9-5488794e7456:0:0:0`
- `ee7f698d-55c5-4a7a-803d-304febe6a758:0:0:0`
- `ef49dc78-9fd9-4cf8-af10-5a6b8ef7fc57:0:1:0`
- `f066174a-a959-4365-920f-c04506d94a5a:0:1:0`
- `f1052b21-ba96-499f-b9e6-9dba4ed82e1e:0:1:0`
- `f2103ab8-a183-4db8-98dd-4146217b5125:0:0:0`
- `f38fe1e9-8997-4b63-9109-7513034bac88:0:0:0`
- `f4bc6674-8586-4dd9-ad3a-87ba704fda7a:0:0:0`
- `f6a6da20-52c8-4921-9884-29d3a3051b0d:0:0:0`
- `f9269fda-e1e6-4e10-9a64-26e8c0f38b0c:0:0:0`
- `fec51ab9-484f-46a8-b2b0-772a61d89e41:0:0:0`

### be dealt/part-2

- `35ab189a-adc8-48d6-82d2-53eb56a4d5e4:0:0:0`
- `52ddf96d-3d6a-439c-b486-d806cbc32d77:0:1:0`

### be dealt/part-3

- `cc22c210-efd0-494c-8560-448b038b3c5f:0:1:1`

### be destroyed

- `ad8fd4e9-f6ae-4f24-b806-4509c8f4ee47:0:2:0`
- `c984787c-f883-42c9-ae5d-9277c84dba01:0:2:0`
- `da2f0d16-3cb4-492d-8535-52a31dbae95e:0:2:0`

### be put/part-1

- `00ba0c24-a671-493e-ba46-13e45d1818f1:0:1:1`
- `02b6900b-219f-4832-8f93-6ef27ee76c0c:0:0:1`
- `0761a0e7-d443-4bab-bb15-307c83d4a6a1:1:2:0`
- `087f9ad7-e74f-40e2-8102-1ed2925d0418:0:1:0`
- `0a154fb2-9f23-4c22-baee-728492385d6d:1:2:0`
- `11838086-db2f-4588-ae18-4129c9e2b67d:0:1:1`
- `13c90d78-cfb1-4d40-a35e-1fd170450b45:1:2:0`
- `1b09d0cf-403c-4a15-aeee-602a1bdaf0c1:0:2:0`
- `1c248187-0be3-4a03-a817-14f68f638ae7:0:1:2`
- `1e0cf860-6be6-4b4b-9a67-0c19b6018ae1:0:1:2`
- `210d1077-6e60-4f06-a8a4-10b842979ac5:0:1:2`
- `27065d34-b22a-47af-aea2-980f47bafcea:0:1:1`
- `2ad77eb7-9466-432f-87b4-e80e4b66e143:0:0:1`
- `2cef4171-8151-4ee9-83a7-bcb5116451bf:1:2:0`
- `2d7e00b6-12f0-4b03-82a6-50e3d1b5395e:0:1:0`
- `2de138b0-3159-4a0c-a474-a4e5600b2e51:0:1:0`
- `2fa6f1b1-00af-433f-b8e1-36db99cd9bba:0:0:1`
- `2fcd5779-7234-49e3-b3c5-ebc07db74462:1:2:0`
- `322f0459-f394-44f0-977b-55fd0cbe0712:0:1:0`
- `35f53871-203a-41da-930e-76540c62d3da:1:1:0`
- `389bcb9f-4e66-4704-9968-a1c1574ec2c8:1:2:0`
- `3b102ccc-7629-457c-aba6-e9b00fd50c85:1:2:0`
- `3d5c98ff-fcf1-42bd-9533-2648791a4f45:0:1:2`
- `3e155876-6086-4499-9963-6efc97cfa5a6:1:3:0`
- `4380df08-7be4-48ca-9783-d644fd2ea27d:0:1:1`
- `45802eb2-6848-416c-95e0-c1c1ea0620d0:1:2:0`
- `493b2820-c250-48bd-9f3c-e1b5639ee101:1:2:0`
- `4b1da9aa-a30c-44b8-a10e-f9dc3fe70b6f:1:3:1`
- `4c05b382-58ab-4a2d-a81c-408ea273b6b6:0:1:1`
- `4d0a0027-53b3-45a1-8736-f0ac86b19342:1:2:0`
- `4db96d32-b4c2-44e9-a73f-aca7dad279b6:1:2:0`
- `51233ade-70cd-4539-9f41-5ffab761da54:1:2:0`
- `5228730a-cebc-472e-ab9a-f424e0c893fd:1:2:0`
- `52e77cc3-f8e9-4a20-811b-fe1e46a96ad7:1:0:0`
- `55717e47-c1ab-4218-bc1c-10e58e91fa87:1:2:0`
- `56ba8fe5-8693-4783-8406-9ced99de0b2a:0:1:1`
- `5768fe50-a134-492c-a725-5ed02610c39f:1:2:0`
- `594f6881-c059-46f8-aa4e-7151d502de73:1:1:1`
- `5b3f041e-ad4a-47ea-bdc4-1be2353f2e18:0:0:1`
- `5d0b8dc6-f4b6-4650-805d-4240d4a4ab82:1:1:0`
- `5e1bd17d-3825-45c0-9e7c-6887b7e2cb5c:1:2:0`
- `5f1e9098-f554-4505-974b-cef4b4b7b23d:0:1:1`
- `600db821-4210-4996-a3f7-e05a143e50c2:1:1:0`
- `626e8acc-20da-496c-9a79-bfbf7529c01d:0:2:1`
- `634475d9-a1d7-4146-9a37-645d3d162af1:0:1:1`
- `657c5473-f153-4dd2-94a0-d477cbc2451d:0:0:1`
- `67a025eb-6e65-435c-becb-b51085175292:1:2:0`
- `6c1d22d4-f28e-4041-a9b6-1575e8929b61:0:1:0`
- `6df6e834-1917-4bf4-b0b7-09834bf90fb2:0:1:0`
- `6f8ca795-d6fd-4e3e-911c-c621a942acbb:0:1:2`
- `7088a901-0489-41c3-9f2f-633939514de8:0:1:1`
- `72177c93-ed1f-47bd-99a6-ad229a292d46:0:2:0`
- `74c9cc13-c03f-4322-82af-b7bce1f2a0d8:1:1:0`
- `7721e800-fba6-4ae7-855e-631b2ecc8d6b:0:1:1`
- `78dbbc15-9304-4178-b9b2-1db6c64ca11a:0:0:2`
- `7a3e50a5-c163-4c41-b62d-d52c233c55b7:0:1:2`
- `810d3afe-c644-444f-a4d9-88b323f0b581:0:2:0`
- `821e8648-222c-4b33-a8bd-e8bfff7dcd9e:0:0:1`
- `830e3e37-a80c-4b0e-b9af-393ad4ca01d7:1:2:0`
- `839748e7-ccb4-421e-9626-b6d8be9390ab:0:0:1`
- `87efff06-b6cb-4a8f-937b-e50e367fd896:0:2:0`
- `8845ba0d-c2f4-49e4-b06e-54a06a8297e0:1:2:0`
- `8b34b211-985b-4934-bb3b-8e6672685ac2:0:1:0`
- `8c56530b-098a-4afd-9022-76bfaa1f6a7c:0:1:1`
- `8f3e6554-eb8a-4096-81a3-2411186d9cb4:1:2:0`
- `8f5ef838-839a-4eb0-8d65-c8c8def0a233:0:1:2`
- `9059a940-ac28-4322-a11b-af1d107b2edd:0:0:1`
- `9ef53bd8-9999-4ea3-a43a-4084a9f208db:1:2:0`
- `a051dee0-60c8-4f58-84cb-55460c097115:0:1:0`
- `a10b3e35-8cc4-450e-9e30-0fce8df0fea4:0:3:0`
- `a3e10b9b-9349-4b44-a46c-c825293dbd05:0:2:1`
- `a56c5ca5-70eb-4d5f-8116-2acbe5f5a3cb:0:2:0`
- `a6395447-677d-4c39-8eda-2d57e527c94e:0:1:1`
- `a986d83d-22f1-45c3-bc2d-f5b210c539fb:0:1:1`
- `aa1a248d-2f76-4f15-b065-08f299af07b9:0:1:0`
- `aba60536-ffbd-480c-8e8f-9639bdc53d4b:0:1:1`
- `abf4dcd8-5176-4f4a-b7c1-5ce24ff181bf:0:1:2`
- `b0c28b2b-a2dd-4b76-bb1c-cec55a0a6784:1:0:1`
- `b8ca5877-ac9e-4b15-8c23-c70f61b01895:0:1:0`
- `ba790609-7b48-4a96-a21f-5a0cfcf316a3:1:2:0`
- `ba88575a-4b9a-40cd-abbc-4539912c9455:1:1:0`
- `bab0ab8d-74d2-49a3-b258-b93d19925d99:0:1:1`
- `c21d1ca3-3d19-4b4d-bbfa-07b5b7bcea4b:1:2:0`
- `c3a68018-9eff-47e6-a612-182886d28fe3:0:0:2`
- `c6bb4b41-8dae-429a-b928-ae9d39c74711:1:1:0`
- `cae3ec72-436d-4086-9dcb-17b3d92ad5c4:0:2:0`
- `cca15007-2faf-4696-a4c5-2d7b6c1ec5b5:0:0:1`
- `cddccc2a-a76e-48b3-b4dd-dfeab89e1619:0:0:0`
- `d1438681-241b-4d53-9470-4d04a7797ea8:0:0:1`
- `d2d753d4-3bb7-4503-8cc0-8f948b7a461e:1:2:0`
- `d6fafb50-9531-4fbf-bb1e-ebb4dd39281c:0:0:1`
- `e4d52559-7624-48b2-96ba-e52ada6c507a:0:0:1`
- `e80772e2-8623-4094-81a2-70828b2b151c:0:1:0`
- `ebfafabc-5255-4024-be59-7403bdb16ee4:0:1:0`
- `ee049bf3-b31c-4dcc-996f-bb076848432b:1:2:0`
- `ee12e2e0-7eda-4f5e-9373-d4c029995adb:1:2:0`
- `f21ce158-2925-4658-ab7b-b73718d31965:0:1:1`
- `f32c5530-6692-4d47-8789-c73da23fd5b7:0:0:1`
- `f4e32fc1-1b8d-441e-8e76-71f19f98e925:0:1:0`
- `f5092c14-eec4-472c-999c-ba96c36b2fbb:0:1:1`
- `f589e5ee-399c-4613-b7a2-9ab2866cc830:0:1:2`
- `fb5e8b8c-bad2-45bb-abb4-2ed454525749:0:1:1`
- `fd36cc16-d3d9-4c9d-9d28-bbe7e5459d75:0:1:1`

### be put/part-2

- `01dbf1bc-ca62-4fb6-959c-ef7c0dc03bb0:0:1:0`
- `14d3e014-9c4f-4864-8f1e-a45ac27e4dbf:0:0:0`
- `16156274-8dc0-439c-94c4-e8c89bbb5687:0:0:0`
- `170ab932-9d50-4ce7-9a42-08e1edce7e7c:0:1:0`
- `28fe909b-06e0-424c-9f75-c824a25f5865:0:0:0`
- `34ceb733-0329-4c1b-8d75-25c34fd4400f:0:1:0`
- `41fed659-237c-4d8e-ad31-d17fa0d3f764:0:0:0`
- `5e7ef7fe-968b-4ada-9fe4-6fda0541aafc:0:1:0`
- `6b6e4ee2-52e6-452b-af15-c90eab5fc746:0:1:0`
- `7683c2b2-a06f-4691-9cc5-1968dc032885:0:1:0`
- `79770e65-740a-44c7-bea2-a24e6a722c22:0:0:0`
- `8609ed1a-f202-483e-9299-408ef6e84ad6:0:1:0`
- `9966cac0-331f-4627-be5a-5060a6ac5a32:0:1:0`
- `a1f3da21-af6d-450e-bf0b-985d158418e6:0:0:0`
- `a2fe5937-212c-4e71-8d6e-f408b38100aa:0:0:0`
- `a9d60d80-bcef-45e0-8ded-d70bd3c2780f:0:1:0`
- `c3d38129-b955-4fb5-8486-095f918935b9:0:2:2`
- `c665544f-557b-4631-a1dc-39571470ca2e:0:1:0`
- `c9404d7d-a026-4082-9fcb-1ab571a136b5:0:0:0`
- `ca0cc02b-b106-4eca-9388-d4b48dd3be49:0:0:0`
- `d81fc181-ecb0-43a5-88e8-c61aca3428d8:0:0:0`
- `e7b746c8-1b32-42ed-8328-4e16274209d8:0:1:1`
- `f122624f-f30d-444e-a62a-939829241045:0:0:0`
- `f1c2dbe2-fbe0-4058-bdf1-91d1b1832786:0:1:0`
- `f578465d-f3a5-48da-bcab-cffbbdd88be8:0:1:0`
- `fe2afa18-54d0-4595-af27-256398793a42:0:1:0`

### be reduced

- `93d1e21b-7326-4aad-9f6e-e0e391845a18:0:2:0`

### begin

- `01591d42-4ef8-471d-beda-d31186bba6a6:0:1:0`
- `0d787c6b-ab82-42c5-b840-8f3a09af30ac:0:1:0`
- `99d4d99d-cf56-45aa-aa39-a250695612f2:0:2:0`
- `b66c6e3a-daed-43a3-95d6-4f9d6223bbf1:0:1:0`
- `f349f58b-8cc8-45e4-9565-2b46fdf976c9:0:0:0`
- `fe2afa18-54d0-4595-af27-256398793a42:0:0:0`

### cause

- `5b67a944-ab0b-4155-8bc0-becb1b38b3bb:0:0:0`
- `d12b4b66-9453-4494-9547-c737f48277ed:0:0:0`

### connive

- `bec686dd-a9ea-4db5-bc20-8e40420b9a9b:0:0:0`

### copy

- `3ca8113b-f5b8-41a7-aae6-ebb32554dfe3:0:0:0`

### counter

- `591bbf84-259d-4885-8b5f-b29c04222d41:0:1:0`

### create/part-1

- `01546b7d-a233-4176-8843-d732074dc5b6:0:0:0`
- `11d8fab8-93af-4291-80bd-cf9436e99f4b:0:0:0`
- `353db389-b829-4e66-85d5-6018bc87c3e0:0:0:0`
- `61fbaaf2-4286-4e9a-b9cb-aa31262b596a:0:0:0`
- `6a1bce89-0c11-4d8d-aacb-c0a5a5effffc:0:0:0`
- `7246d45b-2185-4cdd-981b-5419b7d52bce:0:0:0`
- `8215f4a2-7131-426b-ad9c-6427caabd715:0:1:0`
- `84dc94b2-95fb-4d53-aaa2-191cb645639f:0:0:0`
- `9573c85a-e574-4b4e-aae0-2165c45fd27e:0:0:0`
- `9d22960b-babc-4cf3-b228-d32e13bc6014:0:1:0`
- `df702b0c-e011-497f-ae29-9876efac4a4c:0:1:0`
- `f36d1d8b-8303-44a9-ab56-531931641ea2:0:0:0`

### create/part-2

- `44ba2aa5-2bf5-4267-ae82-f0daf8f5e3e8:0:3:0`
- `44ba2aa5-2bf5-4267-ae82-f0daf8f5e3e8:0:5:0`

### deal

- `009240f3-b7f8-4cbe-a3e9-974da66fb62c:0:1:0`
- `01c39670-3677-49df-a4f6-e5062e0909d5:0:1:0`
- `0afcc646-cb34-4c0e-b3f5-4115ad4faa8e:0:2:0`
- `0ca9c400-c62a-49d8-8dce-5caca7f92ed9:0:0:0`
- `0edf0988-9ed8-4fe6-aa47-4921870f05a8:0:1:0`
- `10a87c58-2d8b-4658-b7d6-8dcbb44a2d2f:0:0:0`
- `1198d47a-4235-4678-bd2e-20f2a97b5924:0:1:0`
- `131069a6-8f30-4caf-8934-3588837b5f7f:0:1:0`
- `13daa21c-278d-45bd-9a6e-a77d6a558453:0:2:0`
- `17327d50-be12-423d-9d37-d6bae519f50c:0:1:0`
- `1e105ab7-fb10-4cfd-ac2f-5e11488cf1b0:0:0:0`
- `1fa272bf-8759-4750-b40b-8e2f6972d570:0:1:0`
- `21565b0d-f814-49ca-8613-f40040c4ba6c:0:0:0`
- `21971c8b-ff9b-40f8-8c9a-93d26c2615b7:0:2:0`
- `22647b1a-5a7c-41b5-b820-b2e9f49c7aad:0:0:0`
- `26b41c78-c5ee-4c50-93be-e3acc35ab355:0:3:0`
- `2b947703-751a-4d95-b5de-e2d6b1fcb502:0:0:1`
- `2d4976d4-649c-4d42-ac5a-ada4b46a480c:0:0:0`
- `2f9107c5-991a-4c20-9b77-2e2fb4b9dc53:0:1:0`
- `321b5cc6-8df6-4292-97a0-a6a3a22f3b55:0:1:0`
- `3383a72f-fb83-4b9a-aca6-b736ed929c2e:0:1:0`
- `37da03c2-c03e-453c-8fbf-e1039faceb8c:0:1:0`
- `3807e6fe-0555-4b09-aef2-efd58abaf669:0:0:0`
- `3998a60d-9521-4100-8d41-3e612972a3de:1:0:0`
- `39a9323d-dddc-42ac-929d-3f4fa7c87567:0:0:1`
- `3d960d33-623a-4415-ae00-f8cffbc15f5a:0:1:0`
- `40b14aaa-f29e-4e84-9bdc-bc2ac9762ce9:0:0:0`
- `41eec4e8-92d3-4f98-9346-3a3e3cc602ce:0:1:0`
- `44c2fefb-5de3-4406-955a-3fabc46357d0:0:1:0`
- `47543892-4d60-4c6b-a6a4-69b9172af01e:0:0:1`
- `47795817-73e5-4af6-bd1e-d69b193e8e9e:1:1:0`
- `4c34a882-3786-4d3c-9ca4-04fa85d5e51b:0:0:0`
- `4d9d5dbb-25ab-41a5-a277-3ee5f9ef579b:0:1:0`
- `4f0bcfe5-7e52-4249-a26a-482619716f18:1:1:0`
- `52159875-354c-47f9-bb1c-cd65395fcc68:0:0:0`
- `543599e2-8312-43a6-ab26-0be17e690d4f:0:0:0`
- `585eb5bc-5a3d-44d8-b593-1ff0d67f96a7:0:1:0`
- `5cbb70e7-a52c-4b35-bc31-d9a0a7df893c:0:0:0`
- `5dbfd316-a0a9-4caa-99b1-069931d2aaa4:0:0:1`
- `60654004-7d9a-47ac-a70d-b246dd1728d3:0:0:0`
- `66290104-ac65-4eb5-bf00-89b944249e07:0:1:0`
- `66f9f325-5e8e-4ebf-b5b3-c6410d80f2c5:0:1:0`
- `68715465-6cf9-4006-87e9-31f227fe9ed3:0:0:0`
- `6985c8a9-9299-461b-8bef-bd2b2c739c11:0:1:0`
- `71220cc2-5f3d-4c97-ae66-05b1b79adef1:0:1:0`
- `7c340a39-4ee0-4ba1-bb66-6674f8020fda:0:0:0`
- `7e529372-cec7-40d7-a1ac-1dce1764f8b2:0:1:0`
- `80d918b2-3a28-49ad-a485-496658bd7ac3:0:4:0`
- `895f23a2-55b7-4cc0-8939-2efaaf097e6f:0:0:0`
- `8b9734c1-7185-40f6-8582-9f87109e3a09:0:2:0`
- `8c3495bf-02e7-4ad9-949d-92eb3d2b662a:0:0:0`
- `9243bd95-5467-490d-9bd2-4d5ce1ebc589:0:0:0`
- `9369f131-3356-4926-9a9f-88a636305bd0:0:0:1`
- `9931a999-ee1b-465b-a912-9f4697a01014:0:0:0`
- `9937dae8-e639-46ad-849b-7e7be93bbbad:0:1:0`
- `a1ed2274-7774-4c65-a95b-28ae5e225994:0:0:0`
- `a89ae357-b5aa-4256-beb3-a2e5e7f43200:0:0:0`
- `a89ae357-b5aa-4256-beb3-a2e5e7f43200:0:1:0`
- `ab0dfae5-b9d4-417b-8a0d-2525ae3a73b9:0:1:0`
- `aba0f637-2d8d-43df-9002-08541ab42944:0:1:0`
- `aed1f0cd-8df8-415f-afd6-ccfd12234334:0:0:0`
- `b1fbfcf3-6921-4417-a58e-0f5e5d34a105:0:1:1`
- `b3f7c4ac-b788-4307-9bc3-d99ce310e07c:0:0:0`
- `b437c963-def5-40d6-b567-ae9f1d2a0fa5:0:0:0`
- `b44d5457-b4d6-4521-a25a-8ef96adba461:0:1:0`
- `b73661a6-d136-4c65-804c-461e83484f4b:0:0:0`
- `bd655e8b-f192-4635-9e23-357b6f89ef8f:0:1:0`
- `beef71f4-f607-4718-9fde-98e8d7871ce9:0:0:0`
- `c40c823c-5954-457a-81a6-02683da57f7f:0:1:0`
- `c8f8b4ed-8455-45cd-a24c-e2f42cd5e5b1:0:1:0`
- `c912a43b-8994-434e-84c0-f4cf58abbd42:0:0:0`
- `cceba6f3-b1c0-45ee-826c-b871d24c7208:0:0:0`
- `d3b7b541-6f05-46c1-8031-c848c4bd4635:0:1:0`
- `d46a6e0b-d39e-42ad-b95f-6902e1b72e62:0:1:0`
- `d46a6e0b-d39e-42ad-b95f-6902e1b72e62:0:2:0`
- `d8328d27-e27f-4c84-8ab5-cabb80a34f54:0:0:1`
- `db121503-8a34-498a-829c-72c33798369b:0:0:0`
- `dbf64afa-ace6-44b9-b47f-750c7e52cc29:0:0:0`
- `e49b902f-a556-4dab-8928-93caf0a3f609:1:0:0`
- `e4acac65-112b-48fc-bea3-44747c1389a3:0:2:0`
- `e4add901-3f2b-4f92-bb26-7f599e288802:0:1:0`
- `e99b0bf8-054a-4fa6-ad67-58ccb7cba004:0:0:2`
- `ea734863-5793-49d6-b10e-109432aec0a3:0:5:0`
- `ea93acc8-0c1f-42a2-bed3-f385d210d58f:0:0:0`
- `f7be3da5-55b2-46f2-a5aa-277dee242b94:0:0:1`
- `ff9a5529-83bd-46a8-b20b-235a5fd26d93:0:0:0`

### die/part-1

- `0462e985-c99e-4404-b212-e9d8baecce72:0:0:1`
- `077885dc-3a88-4ad4-bd5d-bf709aa71e8d:0:1:0`
- `10d33e95-3e5d-447e-ba4a-acd3c33b4045:0:2:0`
- `1128d2ab-0b6e-4912-8735-15521bc314e6:0:0:1`
- `1216900e-93e3-41a4-b354-9c81938639c2:0:1:0`
- `14079f05-fbc1-401c-9008-da678656b4c6:0:0:1`
- `1b9a5170-39c0-4cbf-a041-f3c15f1359ae:0:0:2`
- `247075c5-62f8-41a1-91b3-562ff0aabb30:0:0:2`
- `2c3ed6b9-1a2b-42ad-baa9-ee2a0ad505a7:0:1:0`
- `2d1bbeda-2e81-4aaa-9494-094ec3dd6c3b:0:1:1`
- `314a5c76-1a68-433b-a383-1834400254a8:0:0:1`
- `36ac8fc6-98ad-499b-9adf-046433e2c122:0:1:1`
- `37994591-3494-4314-a7da-49c112b0866f:0:0:2`
- `3a7fe095-8278-4b1d-bec4-19b35bdcdd1b:0:0:1`
- `3bed0b60-5944-44bb-9ddd-c82f323e6d20:0:1:1`
- `3dfeb0c5-85d6-48fb-b924-d7b77f4b89d6:0:0:1`
- `3f404fe4-4335-4dcc-ba90-78246c4b880b:0:0:1`
- `46515251-2172-4b0a-81ac-4c0120b73360:0:1:1`
- `468cfc88-a493-44dc-9d0a-63d9cc89c114:0:0:1`
- `4aa119f7-d411-4188-956e-547f7d14e789:0:0:1`
- `4c095e91-b6ab-417f-94f3-684e64259f97:0:0:0`
- `522a04ff-cbfe-47b0-bd29-ef6fc27a6905:0:0:1`
- `535916f8-b51a-4414-8ab0-fdccdefd9433:1:1:0`
- `57fe941c-a830-4570-afe2-18f93c7a7b84:0:0:1`
- `597d1dce-67e8-4c37-9781-eeaeb7c2d7b7:0:1:1`
- `5beb8d6e-d3c1-46a5-8516-d6bf66413cff:0:0:1`
- `5d65ba1a-3943-4462-9874-62a1afd45bcd:0:1:1`
- `69ae219e-bf97-4626-9b16-7901f51f0343:0:0:1`
- `6a521eed-0965-4fce-8a11-190dc2863da8:0:0:1`
- `6b530534-5c02-4874-9256-501102ef8a5f:0:1:1`
- `6c3faf4f-83c1-4098-98b8-bae15d59b0de:0:0:1`
- `6c87c261-00a8-46f2-92c8-42009a0a2faf:0:2:0`
- `6d776c7b-4ca1-48cd-88c7-dfbbe5a56a0b:0:1:0`
- `6e1aa07a-5d9b-4daf-8dc4-c1717360855f:0:1:0`
- `71d178b3-e5ca-4576-83f7-8dce74758acd:0:3:1`
- `73dad679-1edb-41c9-9d43-56dc93c3e9fe:0:0:0`
- `762f891e-5d88-42b0-8abf-c69f3421011b:0:0:1`
- `7b2a600b-d6c8-45ff-a7fc-06105d27111f:0:3:1`
- `7b89b7d2-c724-4d5d-9f0b-7d3302ad1168:0:1:1`
- `81036c9f-fe0a-45a7-bcd5-0d344f31055a:0:0:1`
- `82e61db8-4625-488f-8a5f-66ace9bbf34a:0:0:1`
- `85d81888-8df7-4826-891e-a14fb8bf6549:0:2:0`
- `8a1ccbdb-3d89-42fb-a731-6db4241acf24:0:0:2`
- `8dc1148f-c6bc-469c-8d1a-7e3efd2de7e2:0:0:1`
- `91b2ffe8-155d-4b9f-82dd-868cc895856b:0:0:1`
- `928c62fe-9c4d-4e89-bd7a-0d3b6a81f393:0:0:0`
- `92d6af2f-728e-4e41-87cb-5c90878a2f2f:0:0:1`
- `964c2003-cef0-4ac7-9f66-4e20893c8e50:0:0:3`
- `9aab4b32-c5b3-4707-b359-9b5e3b63cd11:0:0:1`
- `9fe75f56-c2e4-4c82-8113-039b8c486fae:0:1:1`
- `a30159ae-f6a6-4e29-bca2-769d3657d310:0:0:1`
- `a32795a2-a965-4a85-9944-fd9eed464e65:0:0:1`
- `a42b567d-6bfc-49e7-8f91-917e2bb3046c:0:1:0`
- `ad2a1b07-58f5-44c2-92e0-464ea2d45e7e:0:1:0`
- `b58737a4-180e-4e2f-95ae-afd6d446d608:0:2:0`
- `b5aae42b-3fde-4f10-b85e-882c528badef:0:0:1`
- `b707c131-de13-4d4d-839d-b9f47d62f090:0:1:1`
- `bfb3d862-d92d-4a4f-9a22-671b55d954fd:0:1:1`
- `c638957f-88bf-40c2-834c-2be39d73bf41:0:0:1`
- `c7ecaa1a-fbf7-436b-a1c9-d7810b0dc5dc:0:0:1`
- `c983644d-6741-4aa1-aa68-a6e680c26bb6:0:1:1`
- `cc2d016a-af44-427b-a25a-593274369449:0:1:1`
- `ccdf3399-b836-47ab-802d-af5a9c24d759:0:0:0`
- `ce807ee3-a27c-4f3b-92a4-37faaca42aa1:0:1:0`
- `d09aecc5-4f78-49f8-b503-677e84e36a6d:0:3:0`
- `d14f313c-fea6-49c4-8197-5b74ee584a6b:0:0:1`
- `d2db3f9c-26fe-487b-bbb7-8bc6f33456f1:0:0:1`
- `d4424585-9564-4ec2-8267-3f5438e1f29e:0:0:1`
- `d44f3724-17b7-48f0-885d-75292669f971:0:0:2`
- `d97553bf-6763-4a7b-8d82-1b438a22aa62:0:1:1`
- `dffa7c06-096a-47f8-9645-1ba7306ba5b0:0:2:0`
- `e42fb51e-254a-43ac-ad02-9f0fad0f4c8a:0:1:1`
- `e5d928dc-b465-4cf7-ab11-d5bd3328f8e7:0:1:1`
- `ed3d113d-f2c3-4ef3-8bdd-ed4824a22ab0:0:0:1`
- `efcaadbe-24e3-4dfc-b08c-a910f003d427:0:2:0`
- `f1354b1b-896c-4492-b0c0-3dd07c6d3917:0:0:0`
- `f196ae91-be5c-461b-a69f-aecb538923b4:0:0:0`
- `f474d244-d9be-4580-bf62-f97660e9c1a3:0:0:1`
- `f5dc3dbd-7eab-40f3-afe2-1e88a0c00538:0:0:1`
- `f72558f5-ac5c-4efa-b01b-439bc0bbf18d:0:1:0`
- `f7f8a186-313e-4a29-bf4e-b6a200dfd1ed:0:0:0`
- `f895ec2e-7481-4280-a5c0-38b58c440faf:0:0:0`
- `fa71db44-5181-4c51-8b24-7fbedf36e3ca:0:0:1`
- `fe16f1ab-58b4-4452-abe4-cbd9addd348f:0:0:1`

### die/part-2

- `1822f924-51ba-4f81-92cc-6c5d741a33f9:0:1:0`
- `4696decb-7bff-4c6b-8a7b-9ec324faefde:0:1:0`
- `5653b40f-c566-4a14-b188-a9268ea36218:0:1:0`
- `660f370a-b25b-4ea5-b765-7abf96899c1c:0:1:0`
- `c2f42c67-ff88-4248-bfa5-79a18c6473d5:0:1:0`
- `d04a836b-7e42-424d-9600-42a40d0dfccd:0:0:0`
- `d14c9d2b-41c7-4c9a-a66a-cda34d29c7ba:0:0:0`
- `e1cfd1cb-44a5-429f-a5c1-e6d29bad1c71:0:1:0`

### draw/part-1

- `06d60b71-a9f9-4a7f-ad69-15d760b6e5c3:0:1:0`
- `227ddf6c-d21a-48da-84fb-395c7e096914:0:0:0`
- `278e51fe-3cd9-4c82-bd81-2164771f8611:0:1:0`
- `2aa2f96b-5784-4767-b9ea-b8d9222cb1de:0:0:0`
- `2daee7cb-6736-4aa6-9921-0371c1abe69f:0:1:0`
- `2f533667-e29b-4bec-897a-e7a9eee08314:0:1:0`
- `33345c43-3e77-4d9c-a9b5-5d723e1e5c69:0:0:0`
- `378ae023-04d3-44cc-9248-3d787796ed6c:0:1:0`
- `3fe5cfcd-b25f-49d8-9f60-8b4c388a9c68:0:0:0`
- `3fe61a65-b1c0-4d15-b379-e4ce22c96941:0:2:0`
- `473a7998-669d-4181-83fe-f178a2e781f0:0:1:0`
- `47a080c4-ff04-4f52-aca0-2b8e4f4d931e:0:1:0`
- `51d517c9-2812-44ce-ab4d-e5422b5ecf6c:0:0:0`
- `51f55021-04e0-49bf-8f1f-de2a578c95fc:0:2:0`
- `523d3e3d-8fdf-44f8-868d-7b00995e4577:0:0:0`
- `5277a68e-1ceb-4b40-8e10-3d0564f5d7be:0:0:0`
- `58582fac-4c42-4a1c-9ab1-4a892b500da4:0:2:0`
- `5966c464-5f63-4c71-9317-e2ca79da5aba:0:1:0`
- `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0`
- `76d6d4cc-607f-4a33-a964-a38b5dbfe710:0:0:0`
- `7d1769d0-d942-45b3-a31c-2bbe45e68661:0:0:0`
- `7f5124a4-9ffd-475a-8b77-3ff59a9871a1:0:0:0`
- `8b34b211-985b-4934-bb3b-8e6672685ac2:0:0:0`
- `aa286dd5-aa19-446d-9003-684d81eb57ca:0:0:0`
- `af66da4b-2f36-4dd2-a5c6-18e6023c5aba:0:0:0`
- `ba4f9450-d468-4686-9f48-00fa08c6ac52:0:0:0`
- `c6eaa147-3566-43a9-999a-d58b877496f5:0:1:0`
- `c79b9187-cbfe-43a0-bdc8-4f7e0d215607:0:0:0`
- `c9a9550c-e6bb-4fe3-930f-6266024dbead:0:0:0`
- `d6c008c7-6c87-4677-ba0e-6d95f10d10bc:0:0:0`
- `e1bce9c3-300c-4a9d-abe0-a1f02d3a1105:0:0:0`
- `e23bf5fe-e494-473e-8502-606106ee1820:0:0:0`
- `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0`
- `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0`
- `f1fad5ab-d087-4912-b1b9-42733fa34707:0:0:0`
- `f515c691-07be-47ea-8bc0-46221eab8b46:0:1:0`
- `f8dab16e-1d50-443e-9431-8b6f1cf61c9c:0:1:0`
- `fbfa8b3f-58a7-44ca-8c22-6747b56fdcb9:0:0:0`

### draw/part-2

- `08f17ebc-c0fd-493f-84b3-e9250694543e:0:0:0`
- `1c9e1f75-73f0-4846-b53f-458a0984b1bb:0:0:0`
- `1e4032f6-9741-4845-9325-781c9e489172:0:0:0`
- `6454c457-a278-431a-9e8d-bfd1a966bdde:0:2:0`
- `692a6833-3014-42f6-b1ad-333bb3292c65:0:0:0`
- `888582df-4fe2-4d05-9b62-10c90aaa76f2:0:0:0`
- `a0380b63-58ef-4545-beec-6ad307bbc21b:0:0:0`
- `d5c4d36c-54b3-4149-906b-a57a670260fc:0:1:0`

### enter/part-1

- `01fc5bb3-ebd7-4ab4-8aef-2ece1e1d9b7c:0:0:0`
- `5733c3fb-c533-456c-b30e-5d2b9e206b6b:0:0:0`
- `5baa7abe-5bdf-40ce-9a83-a93b7cae71a3:0:0:0`
- `6c9a854c-0509-4ed4-9d94-c45b823b65e5:0:0:0`
- `6ee68855-c8c5-422b-88da-163c09a96416:0:0:0`
- `7647940e-c99c-401c-ad1d-9ec730f66b6f:0:0:0`
- `8b370db5-dfb9-4ea0-9017-bae3e767b041:0:0:0`
- `bdf476e5-1d57-4b17-b45b-d52fd75aadeb:0:0:0`
- `cd535fa3-6fd8-4227-97fd-3ef07cb0598d:0:0:0`
- `e3b8d70b-17aa-4a31-a4f9-319907d088c2:0:0:0`
- `f3c5978a-70fa-431f-933b-b954bd0db0ea:0:0:0`

### enter/part-2

- `808d5a67-8c38-42f5-9413-8771d8b4ae38:0:0:0`
- `8a76a9b9-3127-45fe-b20f-a8f643276281:0:1:0`
- `a11c6601-7e91-4def-bfea-bb34023ef3c6:0:0:0`
- `e9541db2-2874-4307-b896-c403f6d82e68:0:0:0`

### explore

- `0171861e-98d5-4e58-834f-899d8ad7acea:0:1:0`
- `740aa9d9-91a9-431e-8bf9-1344e5273e27:0:0:0`

### flip

- `a97c8482-775c-4f11-9872-25b4f9bfcb1a:0:0:0`

### gain/part-1

- `02be0b99-d40b-4287-989b-12eb2701115c:0:1:0`
- `08f17ebc-c0fd-493f-84b3-e9250694543e:0:1:0`
- `240f0835-36af-4ad8-9336-d6d3d816d293:0:1:0`
- `2abe9303-d498-4aad-b6b2-8b5064bd2ffd:0:1:0`
- `43c31a03-2bbd-49a6-8b78-c5f3cab04a07:0:1:0`
- `4e9df979-c1c2-4de1-944e-c5e2d782e66e:0:0:2`
- `51b114cd-c174-4d74-a854-07c68b41fc9d:0:0:0`
- `5789520c-e4b2-44b2-b756-3f6b468dc55b:0:0:0`
- `635fe908-6f58-4c9e-ac55-0775a7c6f278:0:1:0`
- `7652f328-e142-494b-a869-772ced10c26a:0:1:0`
- `801e55c7-f8a1-4a90-81cb-3ad7022290ba:0:1:0`
- `9552fc97-9e6d-4307-bf58-30bf956356bf:0:1:0`
- `98c059ed-d749-4f66-bda1-6352976198f0:0:1:0`
- `b86d3142-568a-4eea-b1ae-5fcfc1453533:0:0:0`
- `c7ee79c3-a273-45b4-b3a4-548d9b2b883c:0:1:0`
- `d5c4d36c-54b3-4149-906b-a57a670260fc:0:0:0`
- `f0ead7f5-5c82-40fd-8e89-3e3c5d31fbad:0:1:0`
- `f297648b-0dda-4c58-a3eb-fdabdfb42177:0:1:0`

### gain/part-2

- `5b7515f2-7a5a-4e2a-9784-6cbacd768172:0:2:0`
- `d79e8ec4-b44b-4598-991c-7781dab55868:0:1:0`

### get

- `6a618c4a-e604-4dce-a078-755fd35ac5d9:0:0:0`
- `6bb8c22c-8b01-45f8-8c9e-f683e6b4f022:0:0:0`
- `9e9cde32-0568-44bc-a00a-9709f15c1350:0:0:0`
- `c9404d7d-a026-4082-9fcb-1ab571a136b5:0:1:0`

### learn

- `279e573d-b7a3-4e62-a708-3ec992d97972:0:2:0`

### leave

- `0956bc16-ff04-4e96-8059-ef62afa2405f:0:1:1`
- `1692602a-0c44-485c-aadc-c9c70ed70ea8:0:1:2`
- `23391456-5dfd-4402-88fa-3b08f5e23864:0:1:1`
- `3b6cf935-3b99-4371-a797-6f40b89adeeb:0:0:1`
- `445ad01c-c899-424d-8666-ee7bb2a6e535:0:1:3`
- `53987a39-c18c-4c13-b1ea-fd1b2a369f9e:0:1:3`
- `77398866-eebb-4091-b566-7726f8194a59:0:0:2`
- `7af0e2da-9163-42d9-bf69-439cc61cd28d:0:1:2`
- `7e4cbfd1-2393-4643-bc05-022d06b30210:0:0:4`
- `83914a83-4de2-4d64-9770-f68a12014167:0:0:2`
- `b868de48-3271-4f33-94a4-3dd9b67dd72c:0:1:1`
- `cc21b29f-2d1a-4769-9b65-f92bd2ca1cc8:0:0:2`
- `dfc45c58-821c-42f3-ab48-05b912748bdf:0:0:1`
- `f6fee76b-5c34-4e95-962d-d2b38fcef540:0:0:1`
- `f87bf51e-6218-4418-ae3e-98055e9601e4:0:0:3`

### lose

- `26445dc7-8363-4205-aee8-1cafeb4ba4c0:0:0:0`
- `3db00947-d568-45d7-82cd-b54b4fcb1312:0:0:0`
- `469956a2-7cd4-4695-b8f4-c841526f160d:0:1:0`
- `472efb69-47c8-4c93-b60a-f6dba4364b8c:0:1:0`
- `7472af8e-2e93-43b2-bc32-a3741f6d7502:0:1:0`
- `a68f41a2-37ee-46e1-bf3c-164c78b003ca:0:0:0`
- `add46292-470e-47fa-a261-4884d02e65fe:0:0:0`
- `b2cefcd6-4b81-479c-86ff-1695b836972c:0:3:0`
- `e81da4a7-4b03-4107-b7d9-4b635faa615d:0:0:0`

### mill

- `274b999f-f193-48fd-9a4a-0fdaf535e6c3:0:0:0`
- `f8d2a94f-7be1-4b17-8556-398dde531360:0:1:0`

### no-would:adamant

- `1e94e647-9150-4b22-aa9f-d195f64fb20a:0:1:0`
- `f666c38d-e601-4aa9-b140-4b6607bb12dd:0:1:0`

### no-would:addendum

- `275d0b90-a8d6-4388-b7db-34615287f532:0:1:0`
- `ae198ce9-097b-4204-b599-12bdb36f5195:0:1:0`

### no-would:corrupted

- `402c3afe-7041-41a3-8fcd-64a060c12d4a:0:1:0`
- `57b37690-0fb6-4e78-9210-4a529a6ade7c:0:1:0`

### no-would:counter

- `1abe8246-d2f9-407b-8c16-83da0a6b7de3:0:1:1`

### no-would:coven

- `8afe3d28-be3e-416c-9457-8a2af85b2eec:0:1:0`

### no-would:create

- `12afe8e6-eaf0-45c9-8086-4c658db7cb7e:0:0:1`
- `afc1c443-93e3-4ef4-a404-1d9fc13e0b02:0:1:1`

### no-would:deals

- `2c22af49-c6ef-4de6-bb84-6b3e99879148:0:0:1`
- `c0cc881c-b63b-44dd-8157-67680c65fc3d:0:0:1`

### no-would:delirium

- `518cf9ce-14aa-4f51-81bf-f8c2692a4244:0:1:0`
- `563a8e37-b90e-4ea1-9366-8502b403e13e:0:1:0`
- `712e3479-722c-40a1-9b61-d5bdde93042b:0:1:0`
- `b23cba46-6ed2-442d-bc39-7c4933f6b083:0:1:0`
- `c9dd2bf5-32e0-47f7-9a49-501c262d745b:0:1:0`
- `cf8bc2e3-2f22-45d3-9810-bc039202f41c:0:1:0`

### no-would:descend

- `b153fc70-0312-4856-befd-bb6b9a04a26e:0:1:0`

### no-would:draw

- `6ac3abba-cf55-4d97-a253-bce45972b050:0:0:1`

### no-would:equipped

- `0edc8ad3-2920-4b25-8a86-98ce216111d1:0:0:0`

### no-would:excess

- `6696d2e4-28ee-4ba7-8710-c1b735745270:0:0:1`
- `89abdf4c-ba9d-4602-ae50-cf79c68ea08d:0:0:1`
- `9cfac390-4638-4654-8b50-65c0f0886b18:0:1:1`
- `de6ebf55-f1df-4c3c-bba5-8655b7daf488:0:0:1`

### no-would:fateful/part-1

- `dd3cc9e5-b99a-429c-baeb-663a7af70081:0:1:0`

### no-would:fateful/part-2

- `ff45677d-977e-4ef5-859c-52393ed71a6c:0:1:0`

### no-would:ferocious/part-1

- `3adc3af3-5086-4d61-b38c-c1dddeaeebe6:0:1:0`

### no-would:ferocious/part-2

- `b0060b32-b856-4ff7-a113-cec2dc8f8dc6:0:1:0`
- `b8cf8614-14f4-4c20-9697-2e5ea34e0039:0:1:0`
- `e7871b4d-a408-4377-beee-6b1d3c7dd57d:0:1:0`
- `f70f1f2e-7277-4bc9-b0bb-b44a1da2c62f:0:1:0`

### no-would:g

- `6f82b01d-8975-42a1-87e2-99782272bbea:0:0:0`

### no-would:gain

- `b1298ce8-b318-4d5b-83f2-e274726dfca5:0:0:1`

### no-would:hellbent

- `1b7e325d-24ee-42e3-b06f-6c91ec5280c3:0:1:0`
- `68a203a3-2283-4e29-b177-b3be43f76899:0:1:0`
- `6d890c2a-2ed7-429d-a2b2-d261397f838d:0:1:0`
- `ab48147c-0bd7-4875-8e11-0e26185453dd:0:1:0`

### no-would:if/part-1

- `0146de73-29bf-415a-b450-11074553f715:0:0:1`
- `0403bfb0-2174-4360-994d-68d8ca96fc55:0:2:1`
- `07159efc-c69f-4164-a8ca-9da641dbf702:0:1:1`
- `085bc7be-bd44-40af-8e8f-a1a8006fe22c:0:1:1`
- `12cc97ec-5d03-4434-a31b-51e77d208466:0:1:1`
- `198fed4c-297e-41c0-a172-e471c7401fbb:0:0:1`
- `1fb3b5a3-ca4b-4cbf-ab58-71c960f3efd0:0:1:1`
- `318f7f70-e374-40ef-8afb-3389c10461d8:0:0:1`
- `334c284e-7bc3-4c18-9f8d-4d846f80008e:0:0:2`
- `3686fd97-49ff-4a92-9cb2-7d8e9438d945:0:0:1`
- `3a0ea41e-b4f5-4aa1-9f7a-158485313c64:0:0:1`
- `3b06b242-caed-4c8f-b5ab-30e86061286e:0:0:1`
- `3ceca713-38de-4428-a4f1-2146f6e98393:0:0:1`
- `3d9f854e-1ee5-4aa1-a33b-d3ae08f15dd0:0:1:1`
- `473da1b6-232b-4428-a66d-30262246b47a:0:1:1`
- `495ebe60-f0e5-4f0f-9d99-b2c64c95dbf4:0:0:1`
- `4b2e9aa9-6f91-41de-84b6-e9a89be06a53:0:0:1`
- `4b803bf2-025a-4bf6-9d3c-a28d714b4781:0:1:1`
- `55c7ce94-3cd3-42f3-9dd8-0c118fa626c8:0:0:1`
- `60fc5eb0-95d6-49b0-a538-945ef599e484:0:1:1`
- `610af0f7-b5e3-43fb-9d02-7c59bd99034c:0:1:1`
- `62f4a2db-6d7c-487b-be37-22f06c1e779e:0:1:1`
- `6d56bd32-f47a-4e54-a88e-b69d16283ea4:0:0:1`
- `70d7d1a7-9d39-44ec-a4ea-a70ffa453d23:1:1:1`
- `71ac4d8c-5b58-4ea8-996b-f0289717c4bb:0:1:1`
- `7687b2a7-816d-4416-979b-675e35e235fc:0:0:1`
- `7a5ff4d4-27b7-47d4-ba88-970c63c4e3fb:0:0:1`
- `7c6e0198-edd8-42b8-ba1b-549e1713d188:0:0:1`
- `7f420633-901d-47f9-ae0f-0f5b0ea8359c:0:1:1`
- `87f82107-eaba-484a-800d-e61a0cc5e1f2:0:2:1`
- `8fa0fe02-2452-4386-8e0c-165757b0f0a3:0:0:1`
- `929117cd-caa6-402b-9d7b-1f684d75695c:0:1:1`
- `93ab7462-ceef-4bc7-a9fe-8af8ceb78e1c:0:1:1`
- `9cac23a1-a0b3-490c-aea2-dc2928f6dc9e:0:1:1`
- `aa854d50-444c-49d9-bfb1-5476b33c1c0b:0:0:1`
- `ac2173f9-f223-440a-9231-fd98762bdc6f:0:1:1`
- `b1c8fddb-d686-4b4a-8aff-d79ea747801c:0:1:1`
- `b665a64b-4772-42dd-9fd2-fd8598e689ba:0:0:1`
- `b981af39-4ee6-4fbc-9a89-618dcad9dfbf:0:0:1`
- `ba5a7ac0-b625-42e9-af05-2680a01a95ed:0:0:1`
- `bb377cf8-29ee-489e-86a9-93f4dc2ae02e:0:1:1`
- `bbbb80bd-76fa-4155-929b-4a3565d1cb35:0:1:1`
- `bbe370ba-412b-4052-89d9-2d0ae4928118:0:0:1`
- `be14d3be-295e-431c-b891-590164b730dd:0:1:1`
- `bfaf376f-90f9-45d9-bfbe-dd84a2a4688b:0:1:1`
- `bfcffe67-7db6-41bb-bfcc-400cbb8c8a9c:0:0:1`
- `c01411e0-77b2-4e65-a369-5dbe13745769:0:1:1`
- `c0dda0d0-1fae-4777-ba86-9fe7990bf3a8:0:1:1`
- `c23aaf6d-151e-481a-a345-ca00c14940d1:0:1:1`
- `c68964df-51ae-43b0-abea-74735016c13f:0:0:1`
- `ce6f3c67-8806-416d-9156-6f5bb63d5f4c:0:1:1`
- `d6cba688-faff-4d9f-8148-37d389fa5fb3:0:1:1`
- `d799a2c4-628a-45da-b9ca-0337c46e3e14:0:0:1`
- `d95f1797-56f9-41be-a5fe-8398961f4b8b:0:1:1`
- `dc9ae094-139f-4f28-9d4e-4d6def765744:0:0:1`
- `dcc59bd6-2c5f-48eb-8008-83ce6eb5a442:0:1:1`
- `dd3a4b64-0987-4e9b-a18d-c54365438857:0:1:1`
- `e22824cf-07a1-4c83-b6c4-9d8fcff3892f:0:1:1`
- `e83a629e-2d74-48e2-ad4d-f390067cc51a:0:2:1`
- `ead1ee6a-e0da-46d5-89e8-31e8c0270bc2:0:0:1`
- `ee2ef1e0-6803-4eb5-8664-605438c67505:0:1:1`
- `ee524e82-35c4-4cae-b65e-3e147eac2927:1:0:2`
- `f58117e4-ba85-41b8-8fd5-4245716a84dc:0:0:1`
- `f63c2438-27d4-449a-828f-f0a2ea86ff16:0:1:1`
- `f73da5d8-fd15-4315-ad3c-c86c28087285:0:1:1`
- `fb60739e-1dc3-481d-a056-ad72e665c680:0:1:1`
- `feb221fb-59bf-4671-a53f-1bbe8e9c2ca9:0:0:1`

### no-would:if/part-2

- `0221330a-3e7a-40aa-9c78-85c88a4c1a53:0:0:3`
- `030b5408-f216-43e4-8593-f78d22821876:0:0:1`
- `04fd8c1f-80e5-4b3d-b63e-7af6ccafbbaa:0:1:1`
- `054c6250-ac96-42f6-931d-925761ab7764:0:0:1`
- `05b6f9e3-9acd-43a6-acff-caa811aaf0a1:0:1:1`
- `0611beb7-a38d-4fbf-af9b-ee2a5b9a2896:0:1:1`
- `07634620-a83a-4ca0-8a60-2a21368a2661:0:1:1`
- `09027657-bc9a-4702-88c1-e5b3534ad188:0:0:1`
- `0b085c90-95df-4823-ba67-9eb398b1ec94:0:0:1`
- `0be4bf5e-1c93-49ea-a568-209638bf738e:0:1:1`
- `0efe1357-bfbb-42c0-9cc9-6a919d686c66:0:1:1`
- `0f35cf85-6783-4d69-b5e6-a81f7c1f21e7:0:1:2`
- `0fd114c4-092b-4e28-b0dc-ef529f3bc73e:0:0:1`
- `10185447-a13f-40d8-a8b6-39ce801f2fc0:0:1:1`
- `10d33e95-3e5d-447e-ba4a-acd3c33b4045:0:1:1`
- `11293f96-3263-45e5-89fc-850df6b25a63:0:0:1`
- `123d002c-0004-4e0e-80f3-f0f9555201ac:0:0:2`
- `128170ed-c86a-4f02-9244-28197be90c10:0:0:1`
- `1322734c-3c3e-4885-a6d2-d6460a16fca2:0:1:1`
- `13ebe447-1f8f-4b12-9e35-9d334a863c19:0:0:1`
- `13f58292-9b78-4cd1-a16e-b1779a170d33:0:1:1`
- `144d0817-348c-4171-aa7e-3468b23cf97d:0:1:1`
- `14d06354-4827-41b4-a9b7-e1cd89dfaf40:0:0:1`
- `1551fe97-437e-4e89-a0d2-c398cb2155e4:0:1:1`
- `15d2176b-ab3d-4738-bcbc-bcebf891d16e:0:0:1`
- `1779af8e-38fc-4043-b5fa-ee16a7ea840c:0:1:1`
- `1954994f-17bf-4ea5-af72-60f9bfcb6569:0:1:1`
- `1ae29791-aa7c-4050-bf72-dd0f739b11b8:0:0:1`
- `1b065a17-14a4-433f-a6c8-2c8212f505c7:0:1:1`
- `1b721ad3-d0f6-4eec-9bf0-f57ea9dfa392:0:0:1`
- `1e21e57e-3bc9-41a8-9746-57b583a5ad63:0:1:1`
- `1e46c709-5278-44f3-9f0e-f71bd9558339:0:0:1`
- `1ee3753c-3b6e-4182-9305-2ab757f485f0:0:0:1`
- `202b275e-e0c4-482d-abe9-c5e6360208f3:0:1:1`
- `2069145f-d8af-4386-a874-52a2efb8c7a9:0:1:1`
- `21989fad-9672-46d4-b7d5-101906e7aed2:0:1:1`
- `224f5f1a-4f31-4935-bf5a-910fd0a666a1:0:0:1`
- `2586a59d-8501-4c22-9d69-f4bf91de7024:0:0:1`
- `277757c6-4c4c-4a4c-84f6-4a64fe3b3bfe:0:1:1`
- `27905301-333e-4cdd-90cf-188159fcf8e9:0:1:1`
- `2ab88c99-aaa0-4a91-9225-0bbfba04b6bc:0:1:1`
- `2b34b361-7b0e-4464-874c-ceb501bc5ecc:0:0:1`
- `2b87bcac-ec64-4012-9e75-f459d3640eb3:0:1:2`
- `2bdb2495-cc67-4750-a300-7881b0346514:0:0:1`
- `2c3c3bec-00f0-4de2-b929-73f1c9276ec4:0:0:1`
- `2c3e6377-d09c-46b6-8a83-ada4a2930b14:0:0:1`
- `2c42983e-f45a-4d10-afe5-d2234dfae1ee:0:1:1`
- `2c6b2f4a-4e0e-4dc1-92a8-c07e5cbba5f4:0:1:1`
- `2e5e0abd-38a6-46ca-b922-556db52f1332:0:2:1`
- `2e80d632-cf84-4562-8c93-5850cceb5bec:0:1:1`
- `2f995678-c315-4afe-845b-8c8ae863de6e:0:1:1`
- `32fbb638-ab14-4e8b-a07a-d4c44e3496f2:0:0:1`
- `33e85a8a-86df-4cdc-a9cc-8cbabe92c3c0:0:0:1`
- `34428f42-03ac-4795-8286-6cbea796df2b:0:0:1`
- `36330947-5ef9-4bff-b541-bfbddd9715a3:0:1:1`
- `363f8c66-fe0c-44b9-987d-1d160e3f9c54:0:2:1`
- `393a5d32-fc8e-422b-a957-59e545a54cb6:0:2:1`
- `39f2a632-30d2-4b35-9e7f-fef27713a4f7:0:1:1`
- `3cbdf37b-7fe3-4791-b33c-8591158b0ce5:0:1:1`
- `3e2034ee-adc5-4a24-9605-c9722bf813c1:0:0:1`
- `416c70ab-f136-43e0-b5d5-9af8d4211c01:0:1:1`
- `4236851b-5366-43a1-bde4-f525b4fbcbce:0:1:1`
- `42b10f0f-19cd-45d2-a2db-d5463ddc5e5b:0:0:1`
- `43b5794a-4ed6-471d-bc45-22fac486895d:0:1:1`
- `45c4e67c-e452-41c5-8baa-050819a1321f:0:0:1`
- `4728e320-d29b-4019-8ab5-e45319c77c40:0:0:1`
- `4ae15bd1-e0ea-4c1a-a311-dae421381ebc:0:1:1`
- `4af2e62f-150e-4fd0-98b0-c6e72f5f9a51:0:1:1`
- `4b0b4d16-1d2b-497e-a1ae-bfb89eece665:0:0:1`
- `4b1befff-48fa-47a3-832e-bdaf43495c02:0:0:1`
- `4c11bda3-903f-4b7c-9e5e-f6c5c91977cf:0:0:1`
- `4de71245-9d9b-44ca-9c13-37dc3dfbbcd5:0:0:1`
- `4f429b99-6aca-409f-9d2e-5743d81f1f22:0:1:1`
- `4f6e2e47-34df-4bf3-a546-e06b42840167:0:1:1`
- `51a0d1c2-ff29-4ac9-84a2-ad4f566fee8d:0:0:1`
- `51f091a7-9b0b-4362-8e9c-c174752f369b:0:1:1`
- `51f17fe1-1cf7-4362-b9a2-8ec225d41b03:0:0:1`
- `54402930-84ea-4c3e-9880-ca631e47485f:0:0:1`
- `55eb9310-f24b-410b-850b-a7d0d5117946:0:0:1`
- `573a3afb-3a2a-41b7-ac1a-9685b90bffa3:0:0:1`
- `5bb38d08-582e-43aa-9507-7c20759978ec:0:0:2`
- `5be6f245-31cf-4294-ace0-ca6ce3463fed:0:0:1`
- `5ea1d89c-8650-4373-9835-e369587020ef:0:1:1`
- `5f2be3c2-060a-43e1-b63b-9cd3c78ffcb0:0:0:1`
- `5f97d49c-d0fa-4776-9455-93c1a172cd83:0:1:1`
- `5ffed544-1656-4753-ac8f-ad8fb4442c7f:0:1:1`
- `616c7f45-5295-4b8c-a828-ff3a5ba4d917:0:0:1`
- `624bdbfb-b611-43b6-a3c5-cc8b11dbfaae:0:0:1`
- `639926c1-c4b4-4a49-b125-0e1b584c5bb8:0:0:1`
- `63a85361-56bc-4209-aea8-b49319bc7b92:0:1:1`
- `645ab3c7-ee1d-4dd0-811f-2dc7f7c7e792:0:1:1`
- `647e5639-6339-48af-af96-e48729e1cad3:0:0:1`
- `652e71a9-e46f-41b3-8695-76b3606b1955:0:1:1`
- `675de007-a71e-4036-8204-140c67871b7f:0:1:1`
- `6798163a-864f-4844-96b1-77585a7e7ab4:0:1:1`
- `67a48e3f-2388-42a9-a8b1-97c08761f807:0:1:1`
- `68979160-b5ce-4787-8a1e-1f40e614c3b0:0:1:1`
- `6897f9e0-f654-4c0a-9fda-2ad4e264bf9a:0:1:1`
- `6a6b19db-cdeb-4922-8642-5d872f90e7a1:0:1:1`
- `6b5d1b0a-544c-41e6-bc32-c2b0c9bb4576:0:0:1`
- `6b73f05a-de8c-4e6f-abc0-e66325613e1f:0:1:1`
- `6bdbe36f-b46d-4746-baf2-04f0977bb532:0:0:1`
- `6c0e22f2-f0f3-43e6-87c5-c543032112d8:0:2:1`
- `6dff1d15-604f-4eea-9b7a-0c0ba6afbbac:0:0:1`
- `6ec54d84-7026-45a3-a7d7-37cd5c9a8463:0:1:1`
- `6fc26faa-94a8-433f-8863-126c2d2e73b0:0:0:1`
- `7237d607-2613-4786-96d6-55792c2e02b9:0:1:1`
- `7246638e-0361-40e3-8019-3c10210a593e:0:1:1`
- `736017e2-bc33-49e8-812d-1639443fdb51:0:0:2`
- `743fa824-18cb-4225-ba7b-5b0bbc3c8d41:0:1:1`
- `755bd5d8-67f1-4f24-a4e8-d98edf2f2e03:0:0:1`
- `75c626fb-9dfc-4a94-b59f-f0e45c7b2f56:0:0:1`
- `75f77d67-6702-4311-870c-0209d3a687b6:0:0:1`
- `760e8561-4ec6-4594-ba5d-f79cb9f25fd0:0:1:1`
- `78301998-fd9b-4cd5-afad-dbcb43cac2a7:0:0:1`
- `7857c7b6-9676-47ac-bb28-d0b4cbda5fa7:0:2:1`
- `7a56bdd4-f70e-4abf-9cb7-1624be3288ce:0:1:1`
- `7bc53740-86e7-4e9d-aab6-b5ae62a42133:0:0:1`
- `7ca9ef3e-e5b2-4eb5-87b3-0d97637428a0:0:1:1`
- `7cc4a635-8730-4018-a8fd-b29fb5479928:0:1:1`
- `7de66ba3-6e97-4e0a-928e-7ce45dee278b:0:1:1`
- `7f527852-bf7d-43a3-be0b-784c73ed88aa:0:0:1`
- `8089c3eb-99a8-40ca-882a-c1d4e30075ee:0:0:1`
- `819a7235-b61a-49d7-a0ad-3d8bbf83091e:0:0:1`
- `845b40b1-dc09-44fa-9910-22544c1424ba:0:1:1`
- `854fd120-9a51-4d37-9922-7e4b0464e0f5:0:1:1`
- `8574f57a-768d-42a0-ac8c-cc0a1de181e0:0:1:1`
- `85ac3efc-5e19-4661-b52f-116f57e39581:0:1:1`
- `867b3923-692c-4444-a071-518a290e43d8:0:0:1`
- `87864421-505c-4bdb-b1e3-3e44e05f2beb:0:0:1`
- `888f58c0-1860-4df4-ad75-53e634150680:0:0:1`
- `8985e545-07c3-45f9-9058-fe3c1f50de04:0:0:1`
- `8a83d284-75a0-4901-b7d9-c4b7586ee327:0:0:1`
- `8bba7c7d-6110-4d7f-8b28-3c5b9d3448df:0:0:1`
- `8ca4ca66-30b1-4074-a2e3-545b7682381b:0:2:1`
- `8cb36a67-9206-4665-a03f-64f52ba559c4:0:1:1`
- `8d4e0866-d8f5-4eb6-a0fd-3fa9d4b9cf4a:0:1:1`
- `8d4ef98d-228e-41ff-9133-53f0987e58d8:0:0:1`
- `902eb71f-62b3-40cb-816b-f6b7e92e91e7:0:1:1`
- `906881da-6bb3-4a0e-9bd1-d1a5bc484144:0:0:1`
- `938c03fc-8adf-4c7a-8ae1-eca8401f7a83:0:1:1`
- `93af8f9d-6877-4cb8-a744-c89186db22e1:0:1:1`
- `951a0e34-e610-477f-b441-6680df55a29b:0:0:1`
- `9588a7fd-bbe5-4a81-9a7e-d8e8f6c0537d:0:1:1`
- `96480e86-70a8-401d-abf8-a7d509311b73:0:1:1`
- `96c65faf-859c-4436-a551-5538409a9792:0:1:1`
- `983caa3f-7089-4e66-825d-4086a5adb9bb:0:0:1`
- `99915b5a-5092-4900-8824-6de2aab1b2c1:0:0:1`
- `9ac62ff0-6d13-4091-ba84-fbfbe742a4f4:0:0:1`
- `9b44c005-6799-47fd-8b0d-7179b5281d78:0:0:1`
- `9c348bc7-e6e1-40a2-9798-6d2c4a2d8e72:0:0:1`
- `9dbc2fc8-ed42-4534-9676-bf0695cd518c:0:0:1`
- `9eff1ce5-41e4-4ae6-9480-2b549c8546bd:0:1:1`
- `a151c45f-0b9e-41af-90b3-fafa12e3bbce:0:1:1`
- `a1fc4269-f3e4-4a59-849d-aa1727eef23a:0:1:1`
- `a2b6faca-3321-45d2-a027-ff3a8ae61f10:0:0:1`
- `a32860dd-e8df-4a3c-bdc2-948dcd07cf9a:0:0:1`
- `a3b8a08b-5409-4d5f-9bab-8a7a6376a5b9:0:0:1`
- `a45762af-4aac-40b3-a983-ea441b04c5ee:0:1:1`
- `a5ca7bd9-0964-405f-adb9-7c27153595e6:0:0:1`
- `a5e28749-18ea-4a2b-b7d9-905cf2913d4e:0:1:1`
- `a6e12be3-4166-4bd7-8254-e28b7c8588c7:0:1:1`
- `a9282f91-638e-414b-8b3d-9a99e30aec96:0:1:1`
- `aa00c18b-8719-4095-940a-8e35a57b46c2:0:1:1`
- `abf8264e-d020-4939-8092-83469b1a2244:0:0:1`
- `ac2086fe-98ee-4280-9c7c-c5c2d6548a8b:0:1:1`
- `ad8b90c0-4c66-4fc6-a749-cd10e6deabdb:0:0:1`
- `adc1f850-9217-4a90-8e6a-02ed226ef8df:0:1:1`
- `b11c250c-f191-4c52-ba02-a9176f163447:0:1:2`
- `b23c1f40-291d-43b3-971d-97ded8b367cb:0:0:2`
- `b50a6db0-16ce-4e98-afbd-ec37e1653e7c:0:0:1`
- `b5208c2c-b839-42f6-8717-ee4bbaf1385b:0:0:1`
- `b5c8e24a-f4d7-42dc-8117-905ad0bad888:0:1:1`
- `b613ab11-e173-4a68-8d0a-ac5f09a4db28:0:1:1`
- `b7d7c131-b628-4b35-b40b-1087589ebdd0:0:1:1`
- `b8647f54-f50b-4bc6-bd44-fda25ef189fa:0:1:1`
- `b9a0977a-6364-4358-bab1-112898a1b942:0:0:1`
- `ba0a815c-1dfe-47c1-890f-496c670124f3:0:1:1`
- `ba9ac0a9-735d-4bca-9d24-586aca963872:0:0:1`
- `bad5b8d4-9089-4ebd-8eaa-07552737c527:0:1:1`
- `bbfb3e4a-b389-4391-8141-13b68c0ef2e0:0:0:1`
- `bd581eb6-1a12-4985-9a41-65c5c322d849:0:0:1`
- `bdf4c82b-b3bd-4d57-8c2c-c99f1270577a:0:1:1`
- `be0c9947-3e7c-4b53-b87c-ff16ffd668ea:0:0:1`
- `bf3a0585-3976-4078-8beb-6afa79f97027:0:1:1`
- `c0adbddc-b070-4c5f-afe0-0474c72a9251:0:1:1`
- `c1c62704-1f20-48cf-8588-47e7fca85f7b:0:1:1`
- `c6901a89-ac7d-4797-a027-97bb1cf42e60:0:0:1`
- `c6adfaa7-d9cf-4501-8e7d-e035369390d2:0:1:1`
- `c70598e1-30c6-4f92-a265-34a7a73bc2b8:0:2:1`
- `c8110200-209e-423a-96b7-81a3ac32447c:0:2:1`
- `c9b1557b-70b1-44f2-9fc2-7aa0b035b187:0:0:2`
- `c9db6b94-a7b1-4b93-b454-4dead8f85e34:0:0:1`
- `ca3cda24-0ecd-4edf-b1b3-54311ad58a51:0:1:1`
- `cf3234f2-09d7-4d8b-b871-3bf0fcb75b6d:0:0:1`
- `cfe4d707-41b3-4897-b13a-dcae8f1f3350:0:0:1`
- `d0d844f2-6cf4-49f2-95db-64e932a15b17:0:0:1`
- `d21994f2-75e1-456c-a25a-729c3269df1a:0:1:1`
- `d2bd182c-532f-4c77-adb8-754f2c2fcd82:0:1:1`
- `d32c9439-4c97-412b-83cc-6d9acb48be3c:0:0:1`
- `d3cec4b5-bc93-44a2-a29d-3478f0a5dac6:0:0:1`
- `d4ab7848-5c37-4c6b-be29-0bb703333e5b:0:0:1`
- `d4e54b48-956f-4467-8485-a5fdb44779fd:0:0:1`
- `d533b356-ffa6-44b5-a501-a06954b9345b:0:0:1`
- `d565cd3d-68d4-4039-9e45-7e69e31d0ffb:0:1:1`
- `d6d236c5-b537-4428-b438-7a60a251297b:0:0:1`
- `d71cd08e-3e84-41ff-b9db-9e343c0af6b4:0:0:1`
- `d7562f89-4808-44ab-8dc9-fc4078e8a47b:0:0:1`
- `d7b49bee-2cb0-48e1-91c1-1e150a0da6ed:0:1:1`
- `d851312f-8b4e-4d8e-bfee-c470853be930:0:1:1`
- `d8df9813-0376-4d30-8cdc-30451fb67726:0:0:1`
- `da522912-1bc2-4d70-b426-94d10edb2afe:0:1:1`
- `daec03b6-e3f8-4e44-9766-c64dc23fa3dc:0:0:1`
- `dbdd93d2-f2c6-43f9-93e6-2185c7df83bc:0:1:2`
- `dc39c52b-9bee-4cec-a970-1867314944ef:0:1:1`
- `dc665ddc-4326-4860-94ba-c40ced8b0af6:0:1:1`
- `dd06c11c-c4fd-414e-ac63-5556f31491f5:0:1:1`
- `dd886509-7455-4c8f-976f-0f5fafcb97be:0:0:1`
- `dd893746-e8bd-49fa-a1ce-755d5bd4f513:0:0:1`
- `ddf461b9-a205-4dc7-a9c3-c047b1ff709f:0:1:1`
- `dec281b4-e6d6-4b78-b755-358e07eb7c06:0:0:1`
- `e0f0f290-c83f-4d97-9f5d-786c7136b0d1:0:1:1`
- `e11966cd-2ee3-4df4-b099-abf42dcdf0db:0:0:1`
- `e3d08582-85ba-48c4-a453-4a5a385a0c3e:0:1:1`
- `e45a1c99-a020-49ab-8971-35c6bcd096c8:0:1:1`
- `e4648fa3-0343-414b-b04d-07fe0d132145:0:1:1`
- `e46d0b57-5eec-4ab6-b9a7-a5c5cc01cc34:0:1:1`
- `e50fecff-8872-42f5-8882-41ad13d9d1ae:0:1:1`
- `e536e0d2-7117-4ca8-bdb4-e7dd380113c6:0:1:1`
- `e55d9377-f89a-41e5-a094-730d6f24caf0:0:1:1`
- `e6521404-8474-4727-b2d0-537d15d8a63f:0:1:1`
- `e7194bca-0cf4-4a86-8b84-d2f9219a08b3:0:0:2`
- `e921839f-9d91-41a9-bc89-016af3c757aa:0:1:2`
- `ea46835c-9dac-4e1e-8338-ad99136f511a:0:0:1`
- `ebd6a3a0-ae8d-44e6-8d0b-048da6dd1f03:0:0:1`
- `ebe1448e-21c5-4b73-8296-03d3e5097c50:0:0:1`
- `ec7d550b-9e13-4249-89c7-6ad43f71ea11:0:1:1`
- `ecd49d85-9c8c-4cc9-9a83-072ecd433677:0:0:1`
- `edbe4fdf-9e55-44fa-b3ec-5b1ac615f3a7:0:1:2`
- `ee3d1f44-e0ca-4ce9-be76-4b675a115156:0:0:1`
- `ee3d21b9-58b4-480c-bae3-26de50f1a5c6:0:1:1`
- `ef2aa67a-9531-495c-85c7-7f745bc19ce1:0:2:1`
- `f034e8a3-82f7-4c70-93ea-0bf2688f66e1:0:1:1`
- `f0d1636e-6f80-44fe-869a-1749ab249815:0:0:1`
- `f0d8bde1-76db-4bd2-ae90-3e3a3418de0b:0:0:1`
- `f1993767-1d07-49c8-b8dc-04ec9840a999:0:1:1`
- `f2b376d2-a2f4-4d23-a1fb-eb7b6ebd0b7a:0:1:1`
- `f2b4f37b-270b-4746-83b3-51ff88ee3491:0:0:1`
- `f2b88031-bfb7-46c4-abdd-3b6b5f5acfa4:0:0:1`
- `f3ae58ed-8ef7-4e0a-945f-1f622157236b:0:1:1`
- `f6abd7e5-8c52-4b36-98c5-a4df8b5b6863:0:0:1`
- `f701ada1-e9e1-42ce-9a62-c11bcec03da7:0:0:2`
- `f7a8066e-f8a4-4202-8825-0327d11e58c3:0:1:1`
- `f87df7d4-99e2-4340-9d0a-b96c397555db:0:0:1`
- `fa4755c2-e573-45c3-bd6a-61b2b35fbd24:0:0:1`
- `fd949f82-fc10-4e37-8aa9-6c7569fe3c55:0:0:1`
- `ff52f955-98de-4f12-9ec7-f1d73e3edae9:0:1:1`

### no-would:if/part-3

- `100218ce-1572-4bce-bb00-d2df5f68705c:0:0:1`
- `18ac2282-83af-4acc-b20b-6a95771da688:0:1:0`
- `2441696b-a9ba-4813-ba2e-e71f85281d05:0:3:0`
- `2c189e3b-90d3-49b4-bebe-a4f14c8a275b:0:0:0`
- `2c6f9fdb-ee27-4cd8-9d4d-1ea8b2830f73:0:1:0`
- `31af78dd-e962-4d9a-b696-f3048be03486:0:0:0`
- `3b7e7a11-bf59-413d-8796-640d17c2c1c6:0:0:0`
- `4013b4c2-c9ed-4d14-90f0-97214ec1fded:0:1:0`
- `5b04a337-3152-481e-973f-a11dbd615f93:0:3:0`
- `728e2960-1d85-4b3f-8b5b-915f9b9ffd2f:0:0:2`
- `867def48-4be8-4056-bcf1-d6b00450b9a3:0:1:0`
- `8b610f8f-c8dd-4eeb-bc6e-3bc706d5f63e:0:1:0`
- `a3a8a044-283d-443e-bc40-c2f826d70c22:0:0:0`
- `dd1ef824-4e61-4dee-a8f0-9cf459008f2c:0:0:0`
- `dd821fca-79a0-48a9-b1cf-5a496bc04f65:0:1:0`
- `e0587218-206e-41ed-af3c-f06b7a668e90:0:1:0`
- `ee2ab1ab-be1e-4e56-99f2-7784f7350b41:0:1:0`
- `fb5ec55d-4a35-432a-be6e-c295f1b2e603:0:1:0`
- `fd50d76c-7654-47b9-a5b6-d075874e4357:0:0:0`

### no-would:imprint

- `60a63eb4-b0f7-4930-9bf6-afd42261d4d0:0:0:0`

### no-would:infusion

- `fddd1c39-bdf8-4aee-897c-666498cc4dd3:0:1:0`

### no-would:instead

- `19047c4b-0106-455d-ab71-68cabfae7404:0:1:0`

### no-would:it

- `196948c7-7386-4b5f-ad2f-ec9e3aef26fe:0:2:1`
- `279f3aa5-5807-4797-8cd1-e009984a3691:0:0:1`
- `377d9245-9a70-4e35-9ed1-308565fc1acc:0:0:1`
- `3d7fcc18-5d5f-449f-a584-45d49121cd9d:0:2:1`
- `4669926b-93f9-4d80-aee3-492fbf8e0a0a:0:0:1`
- `4c376349-1a50-4215-8a40-f702da81eb7b:0:0:1`
- `54421e69-d79e-4c2e-8ce6-96994d168835:0:1:1`
- `5e414dc2-d0ff-43e5-9aa2-cd9d96de6d89:0:1:1`
- `649e7237-b38b-43e9-83f4-763751fb1bea:0:0:1`
- `65d6eae4-4318-4dbe-af7a-9f57bb587605:0:1:1`
- `d60c8cfe-435c-419e-a44b-b47d49d1afef:0:2:1`

### no-would:landfall/part-1

- `3708eaae-9306-46b2-ae41-7ce6c50be3c7:0:1:0`

### no-would:landfall/part-2

- `4b3bc59c-5439-4ec8-b25e-7493fa1cd3fd:0:1:0`
- `74b08a70-b0bb-4340-98a0-b1d5b7c9d2cc:0:1:0`
- `c7f08962-6c54-4fd5-a55e-7513e758af32:0:1:0`
- `ddbacb74-1f98-4607-a92e-d14973b9d0ef:0:1:0`

### no-would:metalcraft

- `35506b6b-6476-4830-9baa-4051c18322f0:0:1:0`
- `a47bf064-b810-43d0-89a5-13c107a317b0:0:1:0`
- `d211c03a-03cd-40c5-b7c8-ada352fd01a6:0:1:0`

### no-would:morbid

- `296dee6b-6ec1-4ea4-8dc3-23080dd37646:0:1:0`
- `925a3ded-b7bc-4384-8684-79c20c59ab12:0:1:0`
- `a1180796-6e26-4b45-9263-130620d702e5:0:1:0`
- `d12e374d-ed09-4d5e-bb7a-6c7d9ea80a1e:0:1:0`
- `ecdae60b-c594-4e70-909b-83483104a42c:0:1:0`
- `fa6e2a47-a8cb-4224-ae3e-f61c90477285:0:1:0`

### no-would:put

- `a63eb744-71c4-447d-9372-c3a734f022c5:0:0:2`
- `d6780d29-0dd7-4f04-95b8-4ca6a55308f2:0:0:1`
- `fc3ee37a-f676-44af-80d0-774ff271ce11:0:0:1`

### no-would:raid

- `97bff952-3bc8-41d0-b03f-5c76f3c7e0a3:0:1:0`
- `a0ce2f5a-9c0b-4801-9105-72f84d8a4a1f:0:1:0`

### no-would:return

- `c0535854-e4e7-43e4-bc5c-7cc95fb17929:0:1:1`

### no-would:revolt

- `16437a83-be52-44cd-a768-a767c9347eb2:0:1:0`

### no-would:spell/part-1

- `27c84ad1-1491-459b-bf8a-0146062084dc:0:1:0`
- `8f31d870-872d-4671-80d1-8d2ecd2c38d2:0:1:0`

### no-would:spell/part-2

- `a3a26df4-a9d5-48f5-942f-76862bdcd146:0:1:0`
- `e83236f8-1c45-4d31-8937-1c76db549955:0:1:0`

### no-would:t

- `ce5e52c9-4cb1-42aa-8403-bcd143d68704:0:0:0`

### no-would:that

- `5887922e-d1fb-44e2-9498-2065ce8ac870:0:0:1`
- `75ffebc4-8db9-4de6-a330-e3f41cdccecc:0:0:2`
- `fab8c985-d7a9-41eb-9884-01128b97af5c:0:0:1`

### no-would:this

- `9cf44db4-627a-4197-9588-6da72e41f03d:0:1:0`

### no-would:threshold

- `08261613-1af3-4bd7-9a4d-a366fd508d5f:0:1:0`
- `264cb7f6-6d36-4e58-87f4-83ccaa998a32:0:1:0`
- `2ef797ef-c05f-4309-85c7-1bd151dac3fa:0:1:0`
- `4f66d82a-492f-4638-9f77-190d4a33ad7f:0:1:0`
- `52ad1a31-3ad8-4ead-ba77-675cad7e4a14:0:1:0`
- `5b5bf1fa-6502-4790-b66b-f0f8504ebc7c:0:1:0`
- `658bccf8-fe73-4d6a-b37b-7a58034e5e5d:0:1:0`
- `9c3be33b-0be9-49ec-8160-898cbcab8814:0:1:0`
- `bc3d5911-3580-4132-9daf-2826495b5739:0:1:0`
- `c1972a20-5308-4ee4-b234-751b805d30e4:0:1:0`
- `dc55e69e-e1b8-4129-902c-c71bcb952418:0:1:0`
- `defa9b92-4b54-4b00-852e-6c5ec4015643:0:1:0`
- `f3073e4f-ca7e-4fde-88a4-bd7b6ebfbc8c:0:1:0`

### no-would:u

- `cf9ef041-5396-4f18-8233-42d667db0888:0:0:0`
- `e65769f4-50ae-482b-933b-ac5cf3843f2a:0:2:0`

### no-would:until

- `3da9fecc-064a-44e6-b88e-4b10194e367e:0:0:1`
- `78e3a3c3-3091-46ab-a47a-86b7db68ced4:0:0:0`

### no-would:void

- `42510758-6167-420b-bb70-65f914b7a259:0:1:0`
- `ac5258c1-5b46-4892-a445-bfd56875f039:0:1:0`
- `e5e19326-3e90-439c-a3b2-749d43a1af0c:0:1:0`

### no-would:when

- `118da256-d1ea-44e8-9026-317e49694d29:0:0:1`

### no-would:whenever/part-1

- `0757c5a7-e51b-4c39-bb4d-b32657c10cb4:0:1:0`
- `9207facd-fbf9-4faa-ac44-6c0bcac81551:0:0:0`
- `aa219936-661b-4ccb-8741-78b70cff2b1a:0:1:0`
- `cbad35cd-9026-43ea-8333-94f3b34459e3:0:0:0`
- `d32345c1-ed20-4bfc-a5fa-6ac7b99542ec:0:0:0`

### no-would:whenever/part-2

- `e23cd06d-1360-4e5d-aecc-adf902bede69:0:1:0`

### pay

- `67d66678-a8e6-4f80-bade-1f1daf4b0610:0:0:0`

### planeswalk

- `0f21f3b1-aee9-4272-ad02-067aa5f6a7c8:0:0:0`

### proliferate

- `4716ab91-30e6-4c63-8389-a9db8f9414d8:0:1:0`

### put

- `01546b7d-a233-4176-8843-d732074dc5b6:0:1:0`
- `549dc9f3-1fda-4ad3-87bc-8a990800380b:0:1:0`
- `5a3fdf5a-bff8-4896-b288-3f43f9a72d9b:0:1:0`
- `5a3fdf5a-bff8-4896-b288-3f43f9a72d9b:0:2:0`
- `699610c9-c991-4faf-b712-d015ef0799ad:0:0:0`
- `70987216-f84d-43b9-8d75-bb21ff37747b:0:2:0`
- `915b75d1-b5e3-4aca-a54c-beaccef0a2e4:0:5:0`
- `a3711453-b17d-4b1c-b726-9b41f36d07ab:0:0:0`
- `c066f921-e349-45d1-8ec3-0955d10bbf19:0:0:0`

### reduce

- `1e81454a-ce30-4e41-9d09-3256ae30efc2:0:2:0`
- `6517edb3-30e2-40ba-b6e4-4554b4bbb342:0:0:0`
- `66ca8a60-e028-4a5f-8177-860b888cb9d1:0:1:1`
- `683c81ae-38cd-4db1-b7e7-a09d34b6431e:0:1:0`
- `860add4f-8fe4-4441-b394-f3a48d610b90:0:0:0`
- `8b0e2382-dd91-42e6-aba3-5e8a15418a49:0:2:0`
- `99f9a4c8-b59f-4a41-8577-6c1e4684b240:0:0:0`
- `fcfcac6b-6d26-4ffe-ae9e-b0ee7fa49787:0:2:0`

### result

- `8c8f93d7-d89a-401b-8764-76be71ad16e3:0:2:0`

### roll

- `4fb254cf-b60c-4a3e-b753-4213cb572837:0:0:0`
- `59faa1b9-17aa-4f2c-a8f8-17ab50392b36:0:1:0`
- `5bd19c93-4b1b-45d7-9764-1327fffe94ca:0:0:0`
- `81b06e8d-ed30-4f90-b729-0aa93b0d870f:0:0:0`
- `af1779f8-790e-4606-a02d-9eb4589d58cf:0:1:0`
- `b6003419-1a2a-46f3-b32c-47b825324f78:0:1:0`
- `b8645fe4-884b-4511-b138-ea4ba2eee943:0:1:0`

### scry

- `45b3a028-5705-4dc8-bfab-04bb5e01eea6:0:0:0`
- `65e15354-4258-411f-a8f1-f64f4ccb873b:0:1:0`

### search

- `d9517c5d-66d0-4178-96fb-a8c04f311ad8:0:2:0`

### untap

- `a5d803bc-7fd4-4570-8cd6-cb138727a66e:0:2:0`
- `ffeb792a-6df0-46c1-badc-4deb857f7d48:0:1:0`

## Recall controls

All four recall controls are members of class `draw` and fall in one part.

| clause | class | A1 | A2 | A3 | A4 | A5 | note |
|---|---|---|---|---|---|---|---|
| `51d517c9-2812-44ce-ab4d-e5422b5ecf6c:0:0:0` | `draw/part-1` | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | read. The replacement continues into the tail ("look at", then "Put one of those cards"); no region at either head (U2). The tail "those cards" refers to the looked-at cards, not to A1's object. |
| `766c644c-04fe-4b01-93dd-09a50d78d01f:0:0:0` | `draw/part-1` | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | read. The A5 paradigm: "that card" = the card that would have been drawn; P4 marks it coreference (CR 607.1) with no antecedent (U5). "exiles" is not a region (U2). |
| `eae87919-6322-4bd2-ae9c-b1ce25d686da:0:0:0` | `draw/part-1` | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | read. The tail draws and mills ("they draw a card") are nested events of A1's kind; telling them from A1 needs A1 carried (B4). "discards" is not a region (U2). |
| `eccc9a54-2b56-4a02-9926-258d5b2e25fb:0:0:0` | `draw/part-1` | NOT-EXPRESSED | UNRESOLVED | NOT-EXPRESSED | NOT-EXPRESSED | UNRESOLVED | read. Region at "reveal" only; "choose" and the tail put are not regions (U2). The tail "that card" names the revealed card, not A1's object: a P4 coreference mark is not A5 evidence by itself (U5). |

## Member notes

- Prohibitions, not replacements, in the reader's judgment (they stay members; Q4): `84050a10-e1f1-413e-aa21-5c1f47bb2a64:0:0:1` and `f7be3da5-55b2-46f2-a5aa-277dee242b94:0:0:1` print that damage "can't be prevented or dealt instead" to another recipient; nothing is replaced.
- `cc22c210-efd0-494c-8560-448b038b3c5f:0:1:1` (class be dealt) is a would-class member whose would sits inside the modifying instruction ("prevent the next 4 damage that would be dealt"): it modifies an earlier printed prevent instruction, so it is N1 and a part of its own.
- `19047c4b-0106-455d-ab71-68cabfae7404:0:1:0` (no-would:instead) replaces a draft action; drafting happens outside a game, so in the reader's judgment it is not a CR 614 replacement of a game event (Q5). It stays a member.
- `9cf44db4-627a-4197-9588-6da72e41f03d:0:1:0` (no-would:this) replaces declaring blockers, a turn-based action, with a pile procedure.
- A legacy head on A1's own printed text (a draw or discard inside the condition, U2): `5b67a944-ab0b-4155-8bc0-becb1b38b3bb:0:0:0`, `18ac2282-83af-4acc-b20b-6a95771da688:0:1:0`, `2441696b-a9ba-4813-ba2e-e71f85281d05:0:3:0`, `2c189e3b-90d3-49b4-bebe-a4f14c8a275b:0:0:0`, `3b7e7a11-bf59-413d-8796-640d17c2c1c6:0:0:0`, `5b04a337-3152-481e-973f-a11dbd615f93:0:3:0`, `867def48-4be8-4056-bcf1-d6b00450b9a3:0:1:0`, `ee2ab1ab-be1e-4e56-99f2-7784f7350b41:0:1:0`. On these the mechanical supports_A2 is true but is not A2 evidence.
- Mechanical flags, for any later inferred audit: supports_A1 is false on every would-class member; supports_A2 was true but A2 is UNRESOLVED on 67 members (a region on A1 text, a missed replacing head, a tail continuation without a region, or a region spanning an N2 instead-of phrase).

## Verdict

- A1: GENUINELY_MISSING (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 53, UNRESOLVED 37, OUT-OF-CONTRACT 0); NOT-EXPRESSED on every would-class and N2 row (B1, B1n): no cited section carries a would-be or rules event; would force RUNG-6 (adoption trigger is a holdout card, §9/§22). UNRESOLVED on every N1 row (U1).
- A2: SUFFICES (EXPRESSED 22, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 68, OUT-OF-CONTRACT 0); carried by oracle-compiler-interface/3 §I3a (ratified measurement interface, not production law): H-REGION regions locate the replacing instructions where the frozen detector reaches them; every other row is detector reach (U2), none lacks a carrier.
- A3: GENUINELY_MISSING (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 90, UNRESOLVED 0, OUT-OF-CONTRACT 0); definitional, not measured: no carrier has a CR 614 anchor (count_614_anchored_total 0, expected 0), and P4 conditionality arms (CR 603.4 ...) are not evidence of a replaces/modifies link.
- A4: GENUINELY_MISSING (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 53, UNRESOLVED 37, OUT-OF-CONTRACT 0); a resulting event cannot be told from A1 while A1 has no carrier (B4); would force RUNG-6 (adoption trigger is a holdout card, §9/§22). UNRESOLVED on N1 rows (U4).
- A5: UNDETERMINED (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 90, OUT-OF-CONTRACT 0); the §16 same-card coreference edge (carried by CANDIDATE benchmark structure §16, not ratified production law) is defined, P4 marks the anaphor but resolves nothing (U5).

**M03's classification.** M03 classified this seam GENUINELY_MISSING
(`oracle_compiler/analysis/M03-AUTHORITY-CROSSWALK.json`, row
`replacement_lineage`, authority GENUINELY_MISSING). Within this audit's scope
(CR 614.1a 'instead' clauses), that classification is **narrowed, not
overturned**: it still holds for A1, A3 and A4; A2 SUFFICES (carried by
oracle-compiler-interface/3 §I3a (ratified measurement interface, not
production law), detector reach recorded as UNRESOLVED); A5 is UNDETERMINED.

- A1 is forced by every would-class row (560 members; the 561st would-class
  member is N1) and every N2 row (34 members); each would force RUNG-6 (event
  patterns; adoption trigger is a holdout card, §9/§22). The 419 N1 members are
  UNRESOLVED, not missing.
- A3 is forced by every row: no relation kind with a CR 614 anchor exists
  (definitional). It would not force RUNG-6; it is a question about a relation
  kind beyond §16's three (Q2).
- A4 is forced by the same rows as A1 and for the same reason; the nested-event
  members (draw, create, explore, roll, deal and the others listed under the
  required truths) are where it bites hardest; would force RUNG-6.
- A2 and A5 force no gap. A2's SUFFICES is a statement about a measurement
  interface, not about production law.

## Captain questions

No term, field, relation kind, coordinate, family or primitive is proposed
here; each gap is stated in plain words with the members that force it.

- **Q1 (A1, A4 — the replaced event).** No cited structure carries an event
  that is described but never happens: the would-be event of every would-class
  row (560 members) and the rules or "instead of" event of every N2 row (34
  members). Lineage needs it twice: to say what was replaced (A1), and to tell
  the replacement's own resulting event from it, the CR 614.5 case, which the
  nested-event members show plainly (a would-be draw replaced by draws, a
  would-be creation by a creation containing the same tokens, explore, roll,
  proliferate, scry, deal). This would force RUNG-6 (event patterns; §9 lists
  "scaling/replacement wording" as its consumer question; adoption trigger is a
  holdout card, §9/§22). Does the Captain send this gap to the RUNG-6 holdout
  process, or keep it as a recorded gap for now?
- **Q2 (A3 — the replaces/modifies link).** No relation kind with a CR 614
  anchor exists; §16 currently needs three kinds (CR 607 linkage, coreference,
  conditionality), and §9's rung-5 row makes a fourth kind conditional on such
  a relation being observed. Every row forces this (definitional). Is a CR 614
  replaces/modifies link (and, for N1, a CR 608.2c modifies link) a candidate
  for the relation-kind set, to be decided by the Captain, or out of scope?
- **Q3 (N1 membership).** 419 members (every no-would row except the N2
  members, and one be dealt member) read, in the reader's judgment, as CR
  608.2c later-text modification of a printed instruction — kicker, gift,
  ability-word upgrades, "choose both", "countered this way" — rather than the
  replacement of an event. CR 614.1a literally makes every 'instead' a
  replacement effect, and CR 608.2c's own example uses 'instead', so the two do
  not contradict. They stay members (the membership rule is not edited in this
  wave). Should a later audit treat them as R2-A members, or as a separate seam?
- **Q4 (not a replacement).** Two members print that damage cannot be
  "dealt instead" to another recipient (see Member notes): the form admits them
  literally, but nothing is replaced. Are prohibitions of redirection in R2-A's
  scope?
- **Q5 (outside a game).** One member replaces a draft action (see Member
  notes). Drafting is not a game event; is such a member in scope?
- **Q6 (A5 — what "named as such" needs).** A5 is UNRESOLVED everywhere: §16's
  edge exists on paper and P4 resolves nothing. Two questions remain. (a) When
  A1's object is bound only by the would-be event ("a card" in a would-be draw,
  "one or more tokens"), is a §16 edge to that noun phrase enough to name the
  back-reference "as such", or does it need the RUNG-6 event pattern of Q1?
  (b) Back-references to A1's amount ("that much", "that many", "twice that")
  and to A1 itself ("that draw", "that turn", "that step") are common, are
  outside A5's literal truth item (A1's object), and have no cited carrier;
  should they be a truth item of their own?
- **Q7 (A2's SUFFICES).** A2 SUFFICES only as a statement about the ratified
  measurement interface (H-REGION), not production law, and 68 of 90 rows are
  detector reach (passive replacing events, heads after 'instead', heads the
  legacy detector never emits, tail continuations, regions on A1's own text,
  and N2 regions spanning the "instead of" phrase, which this audit counted as
  not distinct from A1). Does the Captain accept this narrowing of M03's
  classification for A2?
- **Q8 (mechanical evidence).** The flags seams.json computes are not truth:
  supports_A2 is true on members where the region sits on A1's text or misses a
  replacing head, and supports_A5 is true on an "it" inside a condition. This
  audit read every member and did not rely on them; should a future inferred
  audit be allowed to?
