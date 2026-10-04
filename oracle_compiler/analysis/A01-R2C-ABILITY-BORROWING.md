# A01-R2C — ability borrowing / inheritance: V1 P0.6 seam audit (R2-C)

Wave `A01.ORACLE-COMPILER-ROUND2-SEAM-AUDITS`, unit A01-R2C, under Issue #1
checkpoint 5984331292, task 5977804389. Pinned to oracle-compiler-interface/3
(`oracle_compiler/INTERFACES.md` blob 119778a68c0e4e8378f0a117b7c22884ec5eda4b).
This document decides no law and mints nothing: it reads the R2-C population,
states what each member requires, and records which existing structure carries
it. Every gap is handed to the Captain as a question.

## Input

The hand-off rule was followed: the existing artifact was not trusted;
`python3 experiments/oracle_ingest/a01_seams.py --verify` ran first and exited 0
("every embedded hash is current (17 files)"), so it was not regenerated.

seams.json sha256: `43c87c240b8628a28dfe16e71c9c6039e1d5f78724208c363339f8dde106a7ec`

Population: 26 member clauses (has/have/gains/gain + "all activated abilities
of" or "all abilities of" + a noun phrase; CR 613.1f, CR 607.2a). The contrast
set is the 5,022 quoted-ability and CR 702 keyword grants seams.json lists.
All three R2-C recall controls are members. Members are four-coordinate
addresses; no card is named (two members open with an ability label, which is
not quoted here).

## Method

CARDS FIRST, no partition, no sampling: every member was read over its clause
and its paragraph tail as seams.json records them, beside the other paragraphs
of its face (the exiling, choosing or sticker abilities the member refers to),
and its required truth was written before any structure was consulted. Only
then were the cited structures checked against seams.json's evidence
(`evidence[].h_region`, `evidence[].p4`, `evidence[].participants`).

## Required truth per member (written from the readings, before any structure)

C1 the recipient; C2 the source set as a reference (with its CR 607 link where
printed); C3 the granted class ("activated abilities" or "abilities") of the
sources, as opposed to a quoted or keyword grant; C4 the sources are not made
playable, cast, copied as spells or acquired.

- `08826de5-a2d7-4732-a5f7-f580507a7844:0:0:0` — C1 this artifact ("it"); C2 "all land cards in all graveyards" (no link printed); C3 activated abilities; C4 not printed. Condition "as long as" it is on the battlefield.
- `1bb7a942-c4b9-47a2-9782-3ec3efcdaff5:0:1:0` — C1 "creatures you control"; C2 land cards "exiled with this creature" (CR 607.2a link to the enters-trigger exile); C3 activated abilities; C4 not printed.
- `1d8c8c71-d569-450d-adc1-1a1b9aea0123:0:1:0` — C1 this creature; C2 "all legendary creatures you control" (no link); C3 activated abilities; C4 not printed.
- `1ef3b48a-55ef-422e-ac7f-e1c1057eec2c:0:1:0` — C1 ~ ("it"); C2 "all artifact cards in your graveyard"; C3 activated abilities; C4 not printed.
- `1fb02bad-0d1f-437f-a269-f51cc19b280f:0:0:1` — C1 this creature; C2 "that card" = the creature card the preceding clause lets you cast; C3 activated abilities, until end of turn; C4 not printed (the cast permission is the preceding clause's, not the grant's).
- `22f0dbbb-9d8d-42bc-8903-fc0b65e00952:0:0:0` — C1 ~; C2 "creatures you control" without the same name; C3 activated abilities; C4 not printed.
- `2fdeb920-2e48-4308-9517-743eec219c04:0:0:0` — C1 this creature ("it"); C2 "all creature cards in all graveyards"; C3 activated abilities; C4 not printed.
- `69fedfbb-5d88-4fe0-81e1-1e97a56c6aca:0:1:0` — C1 "equipped creature"; C2 "ability stickers on this Equipment" (put there by the enters trigger); C3 all abilities; C4 not printed.
- `74cbe86b-cc8c-4a5f-93c3-f4eaced50393:0:1:0` — C1 this creature; C2 creature cards "exiled with it" (CR 607.2a link to the activated exile); C3 activated abilities; C4 not printed.
- `7abc2a1b-b758-480b-9415-f8f5369ab52f:0:2:0` — C1 ~; C2 "all creatures your opponents control"; C3 activated abilities (whose activation by their own controllers another paragraph forbids); C4 not printed; tail: spend mana as any colour for "those abilities".
- `7ad52f9c-48d8-486f-90b7-73ce5cb3b9db:0:2:0` — C1 ~; C2 cards "in exile with brain counters on them" (the counter, not "exiled with", ties them to the exiling ability); C3 activated abilities; C4 not printed.
- `886e00ab-c694-4839-b3fb-7a72048db4b2:0:1:0` — C1 ~; C2 ability stickers on other permanents you own and cards in your graveyard; C3 all abilities; C4 not printed.
- `93a476c0-c77e-43b0-8695-ada40368a002:0:1:0` — C1 ~; C2 "lands your opponents control"; C3 activated abilities "except mana abilities"; C4 not printed.
- `93cfa771-067f-44ed-9e29-6caf698ee9aa:0:0:0` — C1 ~; C2 "each other creature with a +1/+1 counter on it"; C3 activated abilities; C4 not printed.
- `96e25887-e556-423a-8a69-0cd148216f6a:0:1:0` — C1 this creature; C2 creature cards "exiled with it" (CR 607.2a link); C3 activated abilities; C4 not printed.
- `9e862e4a-254d-4d39-b2cf-4beed6db761f:0:1:0` — C1 this creature; C2 "that card" = the revealed top card of your library, while it is an artifact or creature card; C3 activated abilities; C4 not printed (playing it is not granted).
- `a14d89b6-23eb-4337-8dee-93c39b0efbf1:0:1:0` — C1 this artifact; C2 "the exiled card" (CR 607.3 link to the enters-trigger exile); C3 activated abilities; C4 not printed.
- `ae3517db-bb96-4c29-91dc-5bd68683dced:0:1:0` — C1 this artifact; C2 "all lands on the battlefield"; C3 activated abilities; C4 not printed.
- `c259e16f-2a44-4552-8678-815f757a02e8:0:1:0` — C1 "creatures you control with +1/+1 counters on them"; C2 creature cards "exiled with ~" (CR 607.2a link to the tap-exile ability); C3 activated abilities; C4 not printed.
- `c88e3aff-c539-4e8b-8ee1-a43b3d0962b4:0:0:0` — C1 this creature; C2 "target creature"; C3 activated abilities, until end of turn; C4 not printed.
- `cef87a98-61a0-4a88-950f-867144f685e3:0:2:0` — C1 this creature; C2 "the chosen permanent" (CR 607.2d link to the as-enters choice); C3 activated abilities "except for loyalty abilities"; C4 not printed.
- `d5dc00cb-1510-4ce9-8dd9-0722f65d34b4:0:0:0` — C1 "each Horror you control"; C2 "target artifact an opponent controls"; C3 activated abilities, until end of turn; C4 not printed.
- `e8180024-1979-4677-9a0d-e08d4b7c825a:0:2:0` — C1 "Foods you control"; C2 creature cards "exiled with this creature" (CR 607.2a link to the enters-or-attacks exile); C3 activated abilities; C4 not printed.
- `ea2cbf5a-2def-450b-9db8-40a5b6a604d0:0:1:0` — C1 this creature; C2 cards "exiled with it" (CR 607.2a link to the imprint exile); C3 activated abilities; C4 not printed.
- `ed5fbae0-2dca-44a5-84dc-62674b3a92a6:0:1:0` — C1 ~; C2 cards you own "in exile with cage counters on them" (counter-tied, not "exiled with"); C3 activated abilities; C4 not printed; tail: each of those abilities only once each turn.
- `f5d1bd3c-0e65-4999-a810-881b2389b40e:0:2:0` — C1 this creature; C2 "that card" = the revealed top card, while it is a Goblin card; C3 activated abilities; C4 not printed (casting it comes from a separate printed permission).

No required truth contradicts the CR text.

## Structures consulted, and the cell bases

Only the structures the command lists were credited: the AQ4 contract
(`benchmarks/aq4/docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md`)
§9 rungs 1-5, §12, §13, §16 (rung 1 ratified, §11 law; rungs 2-5, §12, §13 and
§16 CANDIDATE benchmark structure, not ratified production law); the H-REGION
regions and ATTACH-3 role marks of oracle-compiler-interface/3 as `h_region.py`
derives them (a ratified measurement interface, not production law); the
frozen P4 `relation_candidates` and the frozen `participants()` marks.

- **U1 (C1 UNRESOLVED).** §12's participant ordinal is the carrier for the recipient (carried by CANDIDATE benchmark structure §12, not ratified production law), but the frozen `participants()` marks derive no recipient on any member: they mark "target" and second-object slots only, and the recipients here are subjects ("this creature", "~", "it", "creatures you control", "equipped creature"). No member has an H-REGION region either ("has"/"gains" is not a frozen head). Resolution reach, I3's class.
- **E2 (C2 EXPRESSED).** The source is a "target" slot and the frozen `participants()` marks derive it (seams.json `evidence[].participants`, kind target): carried by CANDIDATE benchmark structure §12, not ratified production law. No CR 607 link is printed on these members.
- **U2 (C2 UNRESOLVED).** A carrier is defined — a §12/§13 participant with its constraint atoms (zone, type, counter), a §16 CR 607 linkage edge where the link is printed, a §16 coreference edge for "that card" (carried by CANDIDATE benchmark structure §16, not ratified production law) — but the frozen code does not derive it. Quantified source sets ("all land cards in all graveyards") get no participant mark. Where P4 marks a CR 607 phrase ("exiled with ~", CR 607.2a; "the exiled card", CR 607.3; "the chosen permanent", CR 607.2d) or a coreference ("that card", CR 607.1), it names the phrase and its kind but resolves no endpoint: which ability exiled or chose the sources is not derived (P4 "resolves nothing"; I3 K3's UNRESOLVED arm). On five members whose source prints "exiled with this creature" or "exiled with it", P4 marks no CR 607 phrase at all (detector reach).
- **N3 (C3 NOT-EXPRESSED).** No cited section defines a carrier for "the activated abilities (or abilities) of a referenced object" as what is granted. The contrast set has positive carriers — a keyword grant is a value of §14's `keyword_ability` dimension (§13 atom), and a quoted grant is a created ability that the chain blanks and H-REGION counts (`role_marks_in_created_ability`) — but a member is told apart from them only by having neither, which is an absence and not a carrier (register #37). §13 atoms constrain an object's own characteristics; no atom or predicate takes another object's ability class as its value; no member has a region at "has"/"gains"; no §16 kind relates a recipient to the abilities of a source.
- **U4 (C4 UNRESOLVED).** No member prints that the sources become playable, cast, copied or acquired, nor that they do not; the truth is carried only by absence (register #37).

## Ledger

| clause | C1 | C2 | C3 | C4 | note |
|---|---|---|---|---|---|
| `08826de5-a2d7-4732-a5f7-f580507a7844:0:0:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1 (recipient "it": P4 coreference only). C2 U2: "all land cards in all graveyards", no participant mark. C3 N3. C4 U4. Condition span "as long as" marked, no region. |
| `1bb7a942-c4b9-47a2-9782-3ec3efcdaff5:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "exiled with this creature" printed, but P4 marks no CR 607 phrase (detector reach). C3 N3. C4 U4. |
| `1d8c8c71-d569-450d-adc1-1a1b9aea0123:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: quantified set, no participant mark. C3 N3. C4 U4. |
| `1ef3b48a-55ef-422e-ac7f-e1c1057eec2c:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2. C3 N3. C4 U4. |
| `1fb02bad-0d1f-437f-a269-f51cc19b280f:0:0:1` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "that card" P4 coreference (CR 607.1), antecedent unresolved. C3 N3; the until-end-of-turn duration span is marked but attaches to no region. C4 U4. |
| `22f0dbbb-9d8d-42bc-8903-fc0b65e00952:0:0:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2; P4 marks "the same" as kind-unclear. C3 N3. C4 U4. |
| `2fdeb920-2e48-4308-9517-743eec219c04:0:0:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read; recall control. C1 U1. C2 U2. C3 N3. C4 U4. |
| `69fedfbb-5d88-4fe0-81e1-1e97a56c6aca:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. "all abilities" of stickers. C1 U1. C2 U2. C3 N3. C4 U4. |
| `74cbe86b-cc8c-4a5f-93c3-f4eaced50393:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "exiled with it" printed, no CR 607 phrase marked. C3 N3. C4 U4. |
| `7abc2a1b-b758-480b-9415-f8f5369ab52f:0:2:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2. C3 N3; tail region "activate" is the mana permission, not the grant. C4 U4. |
| `7ad52f9c-48d8-486f-90b7-73ce5cb3b9db:0:2:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: counter-tied exile set ("them" P4 coreference). C3 N3. C4 U4. |
| `886e00ab-c694-4839-b3fb-7a72048db4b2:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. "all abilities" of stickers. C1 U1. C2 U2. C3 N3. C4 U4. |
| `93a476c0-c77e-43b0-8695-ada40368a002:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2. C3 N3 (the "except mana abilities" carve-out has no carrier either). C4 U4. |
| `93cfa771-067f-44ed-9e29-6caf698ee9aa:0:0:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read; recall control. C1 U1. C2 U2. C3 N3. C4 U4. |
| `96e25887-e556-423a-8a69-0cd148216f6a:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "exiled with it" printed, no CR 607 phrase marked. C3 N3. C4 U4. |
| `9e862e4a-254d-4d39-b2cf-4beed6db761f:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "that card" coreference unresolved (which card is on top is runtime binding, out of contract; the static reference is not). C3 N3. C4 U4. |
| `a14d89b6-23eb-4337-8dee-93c39b0efbf1:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: P4 cr607-linkage "the exiled card" (CR 607.3) marked, endpoint unresolved. C3 N3. C4 U4. |
| `ae3517db-bb96-4c29-91dc-5bd68683dced:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2. C3 N3. C4 U4. |
| `c259e16f-2a44-4552-8678-815f757a02e8:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read; recall control. C1 U1. C2 U2: P4 cr607-linkage "exiled with ~" (CR 607.2a) marked, endpoint unresolved. C3 N3. C4 U4. |
| `c88e3aff-c539-4e8b-8ee1-a43b3d0962b4:0:0:0` | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 E2: participants() marks the "target" source (kind target), carried by CANDIDATE benchmark structure §12, not ratified production law. C3 N3. C4 U4. |
| `cef87a98-61a0-4a88-950f-867144f685e3:0:2:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: P4 cr607-linkage "the chosen permanent" (CR 607.2d) marked, endpoint unresolved. C3 N3 (loyalty carve-out uncarried). C4 U4. |
| `d5dc00cb-1510-4ce9-8dd9-0722f65d34b4:0:0:0` | UNRESOLVED | EXPRESSED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1 ("each Horror you control" unmarked). C2 E2: participants() marks the "target" source (kind target, restrictions opponent/controls), carried by CANDIDATE benchmark structure §12, not ratified production law. C3 N3. C4 U4. |
| `e8180024-1979-4677-9a0d-e08d4b7c825a:0:2:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "exiled with this creature" printed, no CR 607 phrase marked. C3 N3. C4 U4. |
| `ea2cbf5a-2def-450b-9db8-40a5b6a604d0:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "exiled with it" printed, no CR 607 phrase marked. C3 N3. C4 U4. |
| `ed5fbae0-2dca-44a5-84dc-62674b3a92a6:0:1:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: counter-tied exile set. C3 N3; tail limits each borrowed ability to once each turn (region "activate"). C4 U4. |
| `f5d1bd3c-0e65-4999-a810-881b2389b40e:0:2:0` | UNRESOLVED | UNRESOLVED | NOT-EXPRESSED | UNRESOLVED | read. C1 U1. C2 U2: "that card" coreference unresolved. C3 N3. C4 U4. |

Every NOT-EXPRESSED cell rests on all 26 read members listed above.

## Verdict

- C1: UNDETERMINED (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 26, OUT-OF-CONTRACT 0); the §12 participant ordinal is the carrier, the frozen participant marks never derive a recipient (U1).
- C2: SUFFICES (EXPRESSED 2, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 24, OUT-OF-CONTRACT 0); carried by CANDIDATE benchmark structure §12 and §16, not ratified production law: target sources are derived as participants; every other source has a defined carrier (participant with atoms, CR 607 linkage edge, coreference edge) that the frozen code marks but does not resolve, or does not mark (U2).
- C3: GENUINELY_MISSING (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 26, UNRESOLVED 0, OUT-OF-CONTRACT 0); no cited structure carries "the (activated) abilities of a referenced object" as what is granted, and the members differ from keyword and quoted grants only by absence (N3). Forced by all 26 members.
- C4: UNDETERMINED (EXPRESSED 0, PARTIAL 0, NOT-EXPRESSED 0, UNRESOLVED 26, OUT-OF-CONTRACT 0); carried only by absence (register #37).

**M03's classification.** M03 classified this seam GENUINELY_MISSING
(`oracle_compiler/analysis/M03-AUTHORITY-CROSSWALK.json`, row
`ability_borrowing_inheritance`, authority GENUINELY_MISSING; compiler rule: do
not equate keyword/quoted-ability grants with borrowing activated abilities from
a referenced object). That classification **still holds, narrowed to C3**: the
gap is what is granted — another object's ability class — and all 26 members
force it. In the reader's view the source references themselves are static
(C2 SUFFICES on candidate structure), so C3 does not obviously need RUNG-6; but
an ability set whose contents are read from a referenced object is close to a
predicate-valued reference, and whether it would force RUNG-6 (adoption trigger
is a holdout card, §9/§22) is left to the Captain (Q1). C1 and C4 are
UNDETERMINED. Nothing is overturned.

## Captain questions

No term, field, relation kind, coordinate, family or primitive is proposed
here; each gap is stated in plain words with the members that force it.

- **Q1 (C3 — what is granted).** All 26 members grant "all activated abilities
  of" (or "all abilities of") a referenced set of objects; no cited structure
  can say that, and M03's rule forbids reading them as keyword or quoted
  grants. Is a carrier for borrowed ability classes a Captain decision for a
  later wave, and does it belong at the static-reference level or under RUNG-6
  (an ability set that changes as the source set changes: graveyard contents,
  the top card of a library, linked exiled cards)?
- **Q2 (C3 carve-outs).** Two members exclude part of the class ("except mana
  abilities", "except for loyalty abilities") and two grant "all abilities" of
  ability stickers. Should a future carrier treat these as the same class with
  exclusions, or as separate cases?
- **Q3 (C2 — CR 607 links).** Eight members print a CR 607 link to the
  ability that exiled or chose the sources. P4 marks three of them and resolves
  none; five ("exiled with this creature", "exiled with it") it does not mark.
  Two more tie the sources by a counter ("in exile with brain counters", "cage
  counters") rather than by "exiled with". Should the CR 607 reach and the
  counter-tied form go to the C04 reference work?
- **Q4 (C1 — the recipient).** No member's recipient is derived as a
  participant (the marks cover target and second-object slots only). Should a
  later probe derive subject recipients before C1 is re-measured?
- **Q5 (C4 — non-acquisition).** No member prints that the sources stay
  unplayable, uncast, uncopied and unacquired; it holds by rule. Is a truth that
  the rules supply and no card prints in scope for this seam?
