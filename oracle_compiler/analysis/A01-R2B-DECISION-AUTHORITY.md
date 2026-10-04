# A01-R2B — player decision authority: V1 P0.6 seam audit (R2-B)

Wave `A01.ORACLE-COMPILER-ROUND2-SEAM-AUDITS`, unit A01-R2B, under Issue #1
checkpoint 5984331292, task 5977804389. Pinned to oracle-compiler-interface/3
(`oracle_compiler/INTERFACES.md` blob 119778a68c0e4e8378f0a117b7c22884ec5eda4b).
This document decides no law and mints nothing: it reads the R2-B population,
states what each member requires, and records which existing structure carries
it. Every gap is handed to the Captain as a question.

## Input

The hand-off rule was followed: the existing artifact was not trusted;
`python3 experiments/oracle_ingest/a01_seams.py --verify` ran first and exited 0
("every embedded hash is current (17 files)"), so it was not regenerated.

seams.json sha256: `43c87c240b8628a28dfe16e71c9c6039e1d5f78724208c363339f8dde106a7ec`

Population: 10 member clauses (a control verb immediately followed by an
explicit player term, CR 723.1 / 723.2) and 4 pronoun candidates (a control
verb followed by "them" or "him or her"). The 410-clause object-control
contrast set (CR 108.4 / 613.1b) is the comparison for B2. All five R2-B recall
controls, including both cards CR 723.2 names (each resolving to exactly one
corpus card in seams.json `cr.cr723_2_resolved`), are members. Members are
four-coordinate addresses; no card is named.

## Method

CARDS FIRST, no partition, no sampling: every member and every pronoun
candidate was read over its clause and its paragraph tail as seams.json records
them (and the preceding clauses of its paragraph), and the required truth of
each was written before any structure was consulted. Only then were the cited
structures checked against seams.json's evidence (`evidence[].h_region`,
`evidence[].p4`, `evidence[].participants`).

## Required truth per member (written from the readings, before any structure)

The CR read for this seam: CR 723.1 (control of another player during that
player's next turn), 723.2 (limited-duration control), 723.3 ("Only control of
the player changes. All objects are controlled by their normal controllers."),
723.5 (the controller makes the controlled player's choices and decisions),
723.9 (a player may be given control of themselves).

- `1f438b8f-fe23-4f3b-ab2e-f6c33676c462:0:1:0` — B1 you control "your opponents" (a set of players); B2 decision control, not control of objects; B3 the window "while they're searching" (each opponent's own search); B4 not printed (CR 723.3 supplies it).
- `369aa9a6-af8a-432c-adff-ced2bb203dc7:0:1:1` — B1 you and "target opponent"; B2 decision control; B3 "during their next turn"; B4 not printed. A reflexive trigger ("When you do").
- `4e7a8817-1a66-45c3-ade9-eac79b40b89f:0:1:0` — B1 you and "target opponent", printed "gain control of"; B2 decision control even though the verb is the object-control verb; B3 "during that player's next turn"; B4 not printed. The tail gives that player an extra turn after it.
- `743fa824-18cb-4225-ba7b-5b0bbc3c8d41:0:1:0` — B1 you and "target opponent"; B2 decision control; B3 "during their next combat phase" (a phase, not a turn); B4 not printed. The tail widens the window to the next turn when a cost was paid.
- `743fa824-18cb-4225-ba7b-5b0bbc3c8d41:0:1:1` — B1 you and "that player" (back-reference to the preceding clause's target opponent); B2 decision control; B3 "during their next turn", replacing the preceding window ('instead', an R2-A member too); B4 not printed.
- `a806f4ee-f48a-46c3-8772-5aaabebe4c7e:0:0:0` — B1 you and "target player" (the target may be you, CR 723.9: two participants, possibly one player); B2 decision control; B3 "during that player's next turn"; B4 not printed.
- `c017f8ae-9103-4965-a07a-f259f44a157d:0:0:0` — inside a quoted ability granted to an equipped creature: B1 you (the ability's controller) and "target opponent"; B2 decision control; B3 "during their next turn"; B4 not printed.
- `c151e8b7-4b28-4f03-8a81-9bf623f893d7:0:2:0` — a loyalty ability: B1 you and "target player" (possibly you, CR 723.9); B2 decision control; B3 "during that player's next turn"; B4 not printed.
- `e8ad3a77-b293-4d69-b080-27ca9f95d443:0:0:1` — B1 you and "that player" (back-reference to the target opponent of the preceding clause); B2 decision control (the tail spells out decisions: the player plays the chosen card, with restricted mana abilities, CR 723.7); B3 "until ~ finishes resolving" (CR 723.2 limited duration), and a second tail window "while that spell is resolving"; B4 not printed.
- `face0a43-6604-4508-b511-81ab0bef7b18:0:0:0` — B1 you and "target player" (possibly you, CR 723.9); B2 decision control; B3 "during that player's next turn"; B4 not printed. The tail exiles the card.

Pronoun candidates: each "them" was resolved by reading its antecedent. All
four antecedents are objects (permanents), so all four are control of objects
(the contrast set, CR 108.4 / 613.1b), not CR 723 control of a player; each is
ruled NOT-MEMBER (antecedents quoted in the table).

No required truth contradicts the CR text. CR 723.9 is noted: B1 asks for two
distinct participants, which a "target player" member has even when one player
fills both (which player fills them is runtime binding, out of contract).

## Structures consulted, and the cell bases

Only the structures the command lists were credited: the AQ4 contract
(`benchmarks/aq4/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`)
§9 rungs 1-5, §12, §13, §16 (rung 1 ratified, §11 law; rungs 2-5, §12, §13 and
§16 CANDIDATE benchmark structure, not ratified production law); the H-REGION
regions and ATTACH-3 role marks of oracle-compiler-interface/3 as `h_region.py`
derives them (a ratified measurement interface, not production law); the
frozen P4 `relation_candidates` and the frozen `participants()` marks.

- **U1 (B1 UNRESOLVED).** §12 defines a flat participant ordinal per argument of an occurrence, and §14's `sort` row makes `player` a contracted filler value (carried by CANDIDATE benchmark structure §12, not ratified production law). The frozen `participants()` marks derive at most one participant here (the "target" slot, with restriction words) and never the controlling player; on three members ("your opponents", "that player" twice) they derive none. Two distinct participants are therefore not derived on any member. Resolution reach, I3's class; not evidence of a missing structure. On "that player" members the identity of the controlled player rests on a P4 coreference mark (CR 607.1) that resolves nothing.
- **P2 (B2 PARTIAL).** Carried: the controlled participant's filler sort `player` is a contracted §14 value, stated as a §13 constraint atom (carried by CANDIDATE benchmark structure §13, not ratified production law), so a player filler is distinguishable from the object fillers of the contrast set ("target creature", "them" = permanents) — though the frozen code does not derive that atom on any member. Not carried: the control itself. §13's relation atom `controller` constrains an object's controller (CR 108.4; it is exactly the contrast set's meaning), not a player's control of another player's decisions (CR 723.5); "control" is not a frozen H-REGION head (no member has a region at it; seams.json `evidence[].h_region.regions`); and no §16 kind relates a controlling player to a controlled one. No cited atom or predicate says that the control is over decisions, so the decision-versus-object distinction is carried only through the filler, never through the control.
- **U3 (B3 UNRESOLVED).** ATTACH-3 defines the duration category (oracle-compiler-interface/3 §I3a), but the frozen duration marks are only 'until' and 'for as long as' (`h_region.py` `_DURATION_RE`): the "during ..." and "while ..." windows are not derived (detector reach). On the one 'until' member the duration span is derived (seams.json `role_spans`, role duration, span 24-50) but has no region to attach to (outcome `no_region`: "control" starts no region), so it is not attached either — extraction reach (I3 K1/K4's UNRESOLVED arm), not a missing structure.
- **U4 (B4 UNRESOLVED).** No member prints that objects keep their controllers; CR 723.3 supplies it. Nothing in the evidence contradicts it, and §13's controller atoms on objects would carry it, but it is carried only by absence (register #37).

## Ledger

| clause | B1 | B2 | B3 | B4 | note |
|---|---|---|---|---|---|
| `1f438b8f-fe23-4f3b-ab2e-f6c33676c462:0:1:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1: participants() derives none ("your opponents" unmarked). B2 P2: filler sort player carried by CANDIDATE benchmark structure §13, not ratified production law; decision control not carried (no region, no atom). B3 U3: "while" window not a frozen duration mark. B4 U4. P4 marks only "they"/"their" (coreference, CR 607.1). |
| `369aa9a6-af8a-432c-adff-ced2bb203dc7:0:1:1` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1: one target participant derived, controller not. B2 P2. B3 U3: "during their next turn" not derived; the only role mark is the reflexive-trigger condition. B4 U4. |
| `4e7a8817-1a66-45c3-ade9-eac79b40b89f:0:1:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. Printed "gain control of" a player: the object-control verb with a player filler, so only the filler (P2) separates it from the contrast set. B1 U1 (target only). B3 U3 ("during"). B4 U4. |
| `743fa824-18cb-4225-ba7b-5b0bbc3c8d41:0:1:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1 (target only). B2 P2. B3 U3: "during their next combat phase" not derived. B4 U4. |
| `743fa824-18cb-4225-ba7b-5b0bbc3c8d41:0:1:1` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1: no participant derived; "that player" is a P4 coreference mark, unresolved. B2 P2. B3 U3 ("during"); the window replaces the preceding one ('instead'). B4 U4. |
| `a806f4ee-f48a-46c3-8772-5aaabebe4c7e:0:0:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1 (target only; CR 723.9 allows one player in both slots). B2 P2: the only region is the cost's "sacrifice", none at the control. B3 U3 ("during"). B4 U4. |
| `c017f8ae-9103-4965-a07a-f259f44a157d:0:0:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. Inside a quoted granted ability; regions only at "exile" (its cost) and "activate". B1 U1 (target only). B2 P2. B3 U3 ("during"). B4 U4. |
| `c151e8b7-4b28-4f03-8a81-9bf623f893d7:0:2:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. Loyalty ability; cost mark only. B1 U1 (target only). B2 P2. B3 U3 ("during"). B4 U4. |
| `e8ad3a77-b293-4d69-b080-27ca9f95d443:0:0:1` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1: no participant derived ("that player" unresolved). B2 P2; the tail's decisions (play the card, restricted mana abilities) have no carrier for being made by the controller. B3 U3: the "until" duration span is derived but attaches to no region (no_region); the tail window "while that spell is resolving" is not derived. B4 U4. |
| `face0a43-6604-4508-b511-81ab0bef7b18:0:0:0` | UNRESOLVED | PARTIAL | UNRESOLVED | UNRESOLVED | read. B1 U1 (target only; CR 723.9). B2 P2. B3 U3 ("during"). B4 U4. Tail region "exile" is the card's own exile, unrelated to the control. |

Every PARTIAL cell rests on all ten read members listed above.

## Pronoun candidates

| clause | membership | B1 | B2 | B3 | B4 | note |
|---|---|---|---|---|---|---|
| `26a623a1-60c9-47e3-af96-616e29551865:0:0:1` | NOT-MEMBER | — | — | — | — | read. "them" = "~ and a creature" (two attacking permanents you own and control): control of objects, a state, not CR 723. |
| `34c3aebe-a224-426a-ae06-f3145193313e:0:0:0` | NOT-MEMBER | — | — | — | — | read. "them" = "noncreature artifacts you control": object control (other players can't gain control of them). |
| `44412804-aa69-4e62-b118-123741d91914:0:0:1` | NOT-MEMBER | — | — | — | — | read. "them" = "~ and all creatures" named in the clause: an opponent gains control of objects. |
| `7f7c204f-be1a-47e4-91c6-ba6f906d9012:0:0:0` | NOT-MEMBER | — | — | — | — | read. "them" = "all creatures": object control until end of turn. |

## Verdict

- B1: UNDETERMINED (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 10, OUT-OF-CONTRACT 0); the §12 participant ordinal (carried by CANDIDATE benchmark structure §12, not ratified production law) can carry two player participants, but the frozen participants() marks never derive the controlling player (U1).
- B2: GENUINELY_MISSING (EXPRESSED 0, PARTIAL 10, NOT-EXPRESSED 0, UNRESOLVED 0, OUT-OF-CONTRACT 0); only the filler sort separates a controlled player from controlled objects; no cited atom, predicate, region or relation kind carries control over decisions (CR 723.5) as distinct from the object-controller relation (CR 108.4). Forced by all ten members. It would not force RUNG-6.
- B3: UNDETERMINED (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 10, OUT-OF-CONTRACT 0); ATTACH-3 defines the duration category; "during"/"while" windows are detector reach, and the one derived "until" span has no region to attach to (U3).
- B4: UNDETERMINED (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 10, OUT-OF-CONTRACT 0); carried only by absence (register #37); no member prints CR 723.3.

**M03's classification.** M03 classified this seam GENUINELY_MISSING
(`oracle_compiler/analysis/M03-AUTHORITY-CROSSWALK.json`, row
`decision_authority`, authority GENUINELY_MISSING; compiler rule: audit CR 723
decision control separately from object/resource control). That classification
**still holds, narrowed to B2**: the gap is the control relation itself — no
existing structure distinguishes control over a player's decisions from control
of objects except through the filler's sort — and all ten members force it
(none would force RUNG-6). B1, B3 and B4 are UNDETERMINED: each has a cited
carrier that the frozen code does not derive (participants, duration marks) or
is carried only by absence. Nothing is overturned.

## Captain questions

No term, field, relation kind, coordinate, family or primitive is proposed
here; each gap is stated in plain words with the members that force it.

- **Q1 (B2 — decision control).** All ten members require that a player
  controls another player's choices and decisions (CR 723.5), and the cited
  structures can only say "controller" of an object (CR 108.4), the contrast
  set's meaning. One member even prints the object-control verb ("gain control
  of") with a player filler. Is a carrier for player-over-player decision
  control a Captain decision for a later wave (and is a player filler on the
  object-control relation an acceptable interim reading, or a conflation to be
  refused)?
- **Q2 (B1 — the controlling player).** The frozen participant marks never
  derive "you" as a participant, and derive no participant at all for "your
  opponents" or "that player". Should a later probe derive both participants
  before B1 is re-measured?
- **Q3 (B3 — windows).** Eight members print a "during ..." window (a turn, or
  a combat phase), one a "while ..." window, and one an "until ... finishes
  resolving" window whose span is marked but cannot attach because "control"
  starts no region. The frozen duration marks stop at 'until' and 'for as long
  as'. Should the ATTACH-3 reach question (during, while, and attachment to a
  control clause) go to an interface review?
- **Q4 (B4 — objects keep their controllers).** No member prints CR 723.3; it
  holds by rule. Is a truth that the CR supplies and the card never prints in
  scope for an Oracle-text compiler at all, or should it stay a rules-level
  fact outside the seam?
- **Q5 (CR 723.9).** Three "target player" members can target their own
  controller, which CR 723.9 allows. Two participant slots filled by one
  player are still two participants for B1; is that reading acceptable?
