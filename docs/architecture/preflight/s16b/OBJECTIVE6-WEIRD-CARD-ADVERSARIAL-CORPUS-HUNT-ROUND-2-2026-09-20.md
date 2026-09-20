# Objective 6 — Weird-Card Adversarial Corpus Hunt, Round 2

**Date:** 2026-09-20  
**Status:** **RESEARCH / PRE-AUDIT ADVERSARIAL EVIDENCE — NOT A SEMANTIC RULING OR FREEZE**  
**Repository scope:** S16B Objective 6 semantic design on PR #70 documentation branch.  
**Governing principle:** **PRESERVE TRUTH, NOT PLUMBING.**  
**Research principle:** **THOROUGHNESS OVER THROUGHPUT.**

## 1. Purpose

Run a second outlier-card attack against the **post-audit candidate model**, deliberately avoiding a simple replay of the first weird-card pass.

This round concentrates on mechanics that were underrepresented in Round 1:

- replacement-event chains;
- delayed acquisition and state restoration;
- process-bound permission windows;
- linked face-down exile state;
- bottom-library and cross-zone processing;
- control of another player / transferred decision authority;
- borrowing activated abilities without gaining use permission for the underlying card;
- temporary hand replacement and resource identity turnover;
- action-count restrictions;
- multiplayer copy/control provenance.

The question remains:

> Can the current primitives, coordinates, signatures, dependencies, and derived facts express the card faithfully, or does the evidence expose a real coverage hole?

A weird card does **not** automatically justify another family.

This document records evidence only. The next whole-vocabulary audit decides what, if anything, changes.

---

## 2. Source basis

Primary evidence:

- project Oracle bulk snapshot `data_snapshots_2026-07-03_oracle-cards.jsonl.gz`;
- project Comprehensive Rules effective 2026-08-07;
- current PR #70 post-audit candidate records, especially:
  - `OBJECTIVE6-CARD-ACCESS-ACCEPTED-COMPONENTS-2026-09-19.md`;
  - `OBJECTIVE6-WHOLE-VOCABULARY-ADVERSARIAL-SEMANTIC-AUDIT-2026-09-19.md`;
  - `OBJECTIVE6-POST-AUDIT-CURRENT-STATE-2026-09-19.md`.

No later preview cards were required for this pass. The test stays inside the project Oracle snapshot so every card below is reproducible against the project corpus.

Corpus regex triage was used only to establish that some apparent oddities represent recurring mechanical populations rather than a single famous card. Examples:

- at least **7** cards in the snapshot directly use `control target player/opponent`-style turn control;
- at least **21** cards match broad `has/gains all activated abilities of ...` ability-borrowing language;
- at least **51** cards match broad `would draw ... instead` draw-replacement language;
- **15** cards carry Hideaway in the snapshot;
- Panglacial Wurm remains the notable unique `cast this card while searching your library` stress case.

These counts are triage only, not ontology membership counts.

---

## 3. Rules anchors materially relevant to Round 2

The current Comprehensive Rules impose several distinctions that the semantic representation cannot flatten:

- **CR 406.3–406.3b:** face-down cards in exile normally cannot be examined; specific effects may grant inspection/use rights, and face-down cards have no characteristics while face down.
- **CR 400.7:** an object that changes zones normally becomes a new object, subject to listed exceptions.
- **CR 603.7:** delayed triggered abilities can schedule later actions and preserve specific source/object relationships under defined rules.
- **CR 607.1–607.2:** linked abilities refer only to the objects/actions/information produced by the linked ability, including exiled cards and noted information.
- **CR 614.1 / 614.6:** replacement effects replace a would-be event; if the event is replaced, the original event does not happen.
- **CR 614.11 / 614.11a:** draw replacements apply to draws inside draw sequences and complete their replacement instructions before the sequence resumes.
- **CR 616.1 / 616.1f–g:** multiple replacement/prevention effects are ordered and reapplied to the modified event until none remain; nested events can themselves receive replacement effects.
- **CR 723.3 / 723.5 / 723.5a:** controlling another player changes decision authority, not control of that player’s objects; the controlling player makes the controlled player’s game choices and must use that player’s resources for costs.

These rules are especially important because Round 2 finds two candidate coverage holes that are not equivalent to Card Use Permission or Permission Denial: **event replacement lineage** and **player decision control**.

---

## 4. Result vocabulary

- **HANDLED** — current post-audit structures can express the card if implemented faithfully.
- **PRESSURE** — the current structures appear sufficient in principle, but the card exposes a requirement that must be explicit before freeze.
- **FAIL — COVERAGE** — the current documented candidate vocabulary lacks an explicit mechanical relation needed to preserve the card’s gameplay truth. This does **not** pre-decide whether the audit should add a primitive, coordinate, surfaced facet, or some other representation.

---

## 5. Adversarial card matrix

| Card / cluster | Mechanical stress | Current-model test | Result |
|---|---|---|---|
| **Panglacial Wurm** | May be cast from the library **while its controller is searching that library**. The permission exists inside another procedure rather than for a conventional duration. | `Card Use Permission + source_zone=library + Permission Window` is sufficient **only if** Permission Window supports process/event-bound windows, not merely EOT/next-turn clocks. The current accepted-components document already permits named-event/condition windows. | **HANDLED.** Keep as a mandatory process-bound Permission Window fixture. No new family. |
| **Necropotence** | Pays life to exile the top card face down, then moves that card to hand at the next end step; also skips the draw step. | The face-down exiled card is not ordinary current Card Use Permission. The effect instead creates a future scheduled zone transition. Card Resource Delta must not silently treat `future guaranteed acquisition` as `currently accessible card`. | **PRESSURE.** Preserve delayed-event / scheduled-zone-transition structure separately from current access. Audit should decide whether existing event-chain machinery already covers this cleanly. |
| **Sylvan Library** | Draws extra cards, then identifies cards **drawn this turn** and either keeps them for life or puts them back. | Literal Draw remains correct, but intermediate draw events cannot simply be summed into a final Card Resource Delta. The effect depends on event-history provenance and a later retention/restitution choice. | **PRESSURE.** CRD needs an explicit observation state/horizon and resource identity history; do not derive it by adding local `+1 draw` events. |
| **Abundance** | Replaces a draw with a chosen land/nonland predicate, reveals until the first match, moves that card to hand, bottoms the rest. | Mechanically this is not Draw. It is `replacement-of Draw + Library Traversal + stop predicate + hand destination`. Output-only modeling would incorrectly make it look like ordinary draw or Tutor. | **FAIL — COVERAGE** for the **generic replacement relation** in the current documented vocabulary. No new `Abundance` family is warranted. |
| **Tomorrow, Azami's Familiar** | Replaces each draw with looking at the top three, choosing one to hand, bottoming the rest. | The post-replacement operation is clean Sample Selection, but the fact that it **replaces Draw** is itself mechanically meaningful and currently not an explicit post-audit primitive/coordinate. | **FAIL — COVERAGE** for generic replacement-event lineage; otherwise Sample Selection handles the operation. |
| **Chains of Mephistopheles** | Replaces non-first draws with discard; that replacement may itself instruct a draw, otherwise mill. | Requires preserving the original would-be event, the replacement effect, the resulting nested event, and CR replacement-order/applicability semantics. A flat bag of `discard + draw/mill` loses the functional behavior. | **FAIL — COVERAGE.** Round 2 strongly supports a generic event-replacement/modification relation before freeze. |
| **Uba Mask** | Replaces draws with face-up exile, then grants each player temporary PLAY permission for cards they exiled this way. | Existing Card Use Permission, provenance, Permission Window, and source/link dependency model the resulting access. What is missing is the explicit `Draw -> replacement event` lineage that explains why no draw happened. | **FAIL — COVERAGE** only for generic replacement lineage; the resulting exile permission is otherwise **HANDLED**. |
| **Memory Jar** | Exiles every hand face down, draws seven, then at the next end step discards the current hand and restores the earlier exiled cards. | This is temporary resource-state substitution plus delayed restoration. It proves that a card can create a large temporary hand without a stable final delta and that prior hand identity must survive linkage to the delayed event. | **PRESSURE.** Card Resource Delta must be state/time indexed; linked delayed restoration must preserve card identity without treating face-down exile as ordinary current access. |
| **Doomsday** | Searches library **and graveyard** for five cards, exiles the rest, then stacks the chosen five on top of the library in any order. | Tutor/search plus multi-zone domain, exact quantity, complement action, ordered destination, and massive resource contraction. Existing participant/zone/destination facts are sufficient if search domain can be a zone set. | **HANDLED**, with a required multi-zone Tutor/search-domain fixture. |
| **Proteus Staff** | Bottoms a target creature, then that creature’s controller traverses their library until a creature is found and places it directly onto the battlefield. | The target’s owner, target’s controller, library owner/controller, and resulting permanent controller can differ. Current owner/controller/provenance coordinates can express this only if roles remain bound per event rather than globally flattened. | **PRESSURE**, not a new concept. Add as a participant-role choreography fixture. |
| **Grenzo, Dungeon Warden** | Moves the **bottom** library card to graveyard, then conditionally moves it to battlefield based on its characteristics after the first move. | The current permission model already says source zone/**position** rather than only top. Zone-change identity and a second contingent move must remain explicit. | **HANDLED** if library position is genuinely generic (`top`, `bottom`, etc.) and event chaining obeys CR 400.7. |
| **Goblin Charbelcher** | Traverses/reveals until a land, uses traversal length/type only to calculate damage, then bottoms all revealed cards. | This performs Library Traversal with **no card access/acquisition at all**. | **HANDLED.** Strong negative fixture proving Library Traversal must not imply Card Access, Sample Selection, or resource gain. |
| **Shelldock Isle / Hideaway** | Finite sample -> one face-down exiled card -> linked inspection right -> conditional PLAY permission from exile, sometimes free. | Current Sample Selection includes visibility; Card Use Permission includes source/link dependency; Permission Window and Alternative Cost complete the model. CR 607/406 linkage matters. | **HANDLED.** Strong integrated fixture; no new Hideaway family. |
| **Ice Cauldron** | Exiles a specific card, grants it indefinite cast permission, notes the type/amount of mana spent on one activation, later reproduces that exact mana only for the linked exiled card. | Tests linked abilities, noted information, Typed Resources, Stored Capacity, and card-specific spending restriction. | **HANDLED** if linkage IDs can connect stored typed mana to the exact exiled-card permission. Strong CR 607 fixture. |
| **Mairsil, the Pretender / Necrotic Ooze / Skill Borrower / Experiment Kraj / Quicksilver Elemental** | A permanent gains activated abilities from other referenced cards/objects without casting, playing, copying, or moving those cards as usable resources. | This is **not** Card Use Permission, Additional Execution, Direct Placement, or resource acquisition. The current post-audit vocabulary does not explicitly represent `ability inheritance/borrowing from referenced object(s)`. Corpus triage finds at least 21 broad members of this mechanical population. | **FAIL — COVERAGE.** Audit must determine the smallest faithful primitive/signature. Do not create a public family merely because the gap exists. |
| **Spellweaver Volute** | Copies an instant **card** in a graveyard, may cast the copy free, then exiles the physical card and reattaches to another instant card. | Copy/execution provenance must separate the physical graveyard card from the cast copy. Alternative Cost applies to the copy; the physical card is not itself cast. | **HANDLED** by Additional Execution + copy provenance + zone transition + Alternative Cost. |
| **Eye of the Storm** | Builds a shared exile repertoire of instant/sorcery cards; every qualifying cast causes the caster to copy every stored card and optionally cast those copies free. | Stored Capacity/repertoire, copy provenance, Additional Execution, per-trigger multiplicity, and shared source identity are enough. Copies are not new card-origin resources. | **HANDLED**, but keep as a high-multiplicity stress fixture for CRD and Additional Execution. |
| **Mindslaver / Worst Fears / Emrakul, the Promised End / Sorin Markov** | One player controls another player for a turn, making that player’s game decisions while using the controlled player’s resources; object control does not transfer. | This is not permanent theft, Card Use Permission, or Permission Denial. CR 723 defines a distinct change in **decision authority over a player**. The current post-audit candidate vocabulary has no explicit relation for it. | **FAIL — COVERAGE.** Audit must add the smallest faithful Player Control / Decision Authority representation and decide whether it is primitive, surfaced facet, or another type. |
| **Sen Triplets** | Reveals an opponent’s hand, suppresses that opponent’s spell/ability actions for the turn, and lets the controller play lands/cast spells from that opponent’s hand. | Generic Card Use Permission already allows arbitrary source zone, owner/provenance, holder, PLAY vs CAST, and window. Permission Denial covers the opponent restriction. Hand visibility must remain explicit. | **HANDLED** if visibility is a generic coordinate beyond Sample Selection. Good opponent-hand permission fixture. |
| **Fires of Invention** | Allows free casting under an MV/land-count condition but also restricts casting to the controller’s turn and at most two spells per turn. | Alternative Cost is clear. The important stress is that action legality can be **cardinality capped** rather than binary permitted/denied. | **PRESSURE.** Ensure generic action restrictions can carry quantity/rate caps; do not force this into a binary Permission Denial predicate. |
| **Teferi's Puzzle Box** | Each draw step bottoms the player’s entire hand, then draws the same number. | Card count can remain numerically neutral while the entire underlying card-resource identity set turns over. CRD alone therefore cannot explain similarity to hand-replacement/Wheel effects. | **PRESSURE.** Preserve resource identity turnover separately from net resource quantity. This may remain an event signature rather than a new family. |
| **Maralen of the Mornsong** | Players cannot draw; each draw step instead causes life loss and an unrestricted library search to hand. | Combines Draw denial with a recurring Tutor event. No need for a replacement family because the card uses a prohibition plus separate trigger rather than `instead`. | **HANDLED.** Useful negative anchor for the replacement-lineage proposal: similar gameplay outcome, different mechanism. |
| **Hive Mind** | Every instant/sorcery cast is copied for each other player; each receives/control their copy and may retarget it. | Typed copies, per-player controller provenance, target-choice authority, and execution multiplicity are sufficient. | **HANDLED.** Strong multiplayer copy-provenance fixture. |

---

## 6. Round-2 findings before audit

### R2-F1 — Generic replacement-event lineage is missing from the documented post-audit vocabulary

This is the strongest new result.

Round 1 encountered replacement-like cards such as Shared Fate and Omen Machine, but the post-audit candidate vocabulary did not promote a generic relation that preserves:

- original would-be event;
- replacement/modifying effect;
- resulting event(s) or no-event;
- affected object/player;
- applicability condition/exclusion;
- ordering when multiple replacements compete;
- lineage into nested events created by the replacement.

Abundance, Tomorrow, Chains of Mephistopheles, and Uba Mask make the omission difficult to ignore.

**Pre-audit constraint:** do **not** create `Draw Replacement` as a bespoke family. The evidence points toward a reusable event-replacement/modification primitive/signature grounded in CR 614/616.

### R2-F2 — Player Control / Decision Authority is a genuine mechanical coverage hole

CR 723 defines control of a player as a transfer of decision authority, not control of that player’s cards/permanents.

Mindslaver, Worst Fears, Emrakul, Sorin Markov, and other corpus members demonstrate that this is a recurring mechanic rather than a one-card curiosity.

The current model has owner/controller/provenance for objects and selection authority for selection operations, but neither captures `A controls B's game decisions during window W`.

**Pre-audit constraint:** represent the mechanical truth first. Do not assume `Player Control` must be a top-level family.

### R2-F3 — Ability borrowing/inheritance is distinct from card access and execution

Mairsil, Necrotic Ooze, Skill Borrower, Experiment Kraj, Quicksilver Elemental, and a broader corpus population gain activated abilities from referenced cards/objects.

The underlying referenced card:

- is not necessarily playable;
- is not necessarily cast;
- is not copied as a spell;
- is not necessarily moved;
- may simply serve as an ability template/source set.

The post-audit vocabulary currently has no explicit primitive for this relation.

**Pre-audit constraint:** the audit should determine whether a generic `ability inheritance / ability borrowing` primitive already exists elsewhere in the substrate or must be added. Avoid a new public family unless retrieval evidence independently warrants it.

### R2-F4 — Card Resource Delta must be explicitly state/time indexed

Memory Jar and Sylvan Library reinforce an issue that static accounting obscures:

- temporary resources can appear and later disappear;
- previous resources can be temporarily inaccessible and later restored;
- intermediate Draw events need not equal final retained resources;
- net quantity can be unchanged while resource identities turn over completely.

CRD should therefore always be understood as `delta between defined observation states`, not as a naïve sum of event-local card movements.

This does not resurrect Card Access Differential.

### R2-F5 — Delayed acquisition is not current access

Necropotence demonstrates a useful boundary:

- a face-down exiled card may be destined to enter hand later;
- that future scheduled transition is mechanically real;
- but it is not the same fact as current PLAY/CAST/use permission.

The substrate needs to preserve delayed event/entitlement structure without inflating current card-resource access.

### R2-F6 — Existing Card Access decomposition survives several severe tests

Several cards that initially look ontology-breaking fit the revised post-audit components cleanly:

- Panglacial Wurm -> process-bound Permission Window;
- Hideaway -> Sample Selection + visibility + link dependency + Exile Access/PLAY;
- Ice Cauldron -> linked permission + Stored Capacity + Typed Resources;
- Goblin Charbelcher -> Library Traversal without access;
- Spellweaver Volute / Eye of the Storm / Hive Mind -> copy provenance + Additional Execution;
- Sen Triplets -> opponent-hand Card Use Permission + visibility + Permission Denial.

This is evidence **against** reopening the broad Card Access noun tree.

### R2-F7 — Generic visibility/information access must remain first-class enough for legality

The current Sample Selection coordinates already include visibility, and Card Use Permission already preserves source/link dependency. Round 2 reinforces that visibility cannot remain an incidental annotation:

- face-down exile normally hides characteristics under CR 406.3;
- Hideaway grants a linked inspection right;
- Sen Triplets reveals the opponent’s hand while granting use permission;
- some permissions can exist only because a player is allowed to inspect the relevant hidden object.

The audit should verify that visibility/information access is generic substrate data, not restricted to Sample Selection alone.

### R2-F8 — Action restrictions need cardinality/rate, not only binary denial

Fires of Invention permits casting while capping it at two spells per turn.

A binary `Permission Denial = yes/no` is therefore not enough for all interaction/restriction semantics. Generic action restrictions should support quantities/frequency windows where the Oracle text imposes them.

No new public family is implied.

---

## 7. What Round 2 does **not** authorize

This evidence does not yet:

- revise the current post-audit candidate vocabulary;
- name/freeze a replacement primitive;
- name/freeze a Player Control primitive/facet;
- name/freeze an ability-borrowing primitive;
- alter Card Resource Delta rules;
- alter Searcher B weighting;
- start corpus execution;
- freeze S16B;
- merge PR #70;
- move accepted implementation head or `main`;
- resume AQ4;
- activate Bridge v0;
- authorize Step6.

The next action is the **audit of these Round-2 findings against the whole current vocabulary and existing substrate**, with the standing question:

> Does the evidence force new structure, or can an already-existing primitive/coordinate express the fact faithfully?

Until that audit is complete, the three `FAIL — COVERAGE` findings are evidence of missing documented representation, not approved ontology additions.
