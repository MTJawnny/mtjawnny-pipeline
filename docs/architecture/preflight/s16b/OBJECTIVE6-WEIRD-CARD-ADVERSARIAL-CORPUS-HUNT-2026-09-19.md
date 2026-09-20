# Objective 6 — Weird-Card Adversarial Corpus Hunt

**Date:** 2026-09-19  
**Status:** RESEARCH / ADVERSARIAL EVIDENCE — NOT A SEMANTIC FREEZE  
**Repository scope:** S16B Objective 6 semantic design on PR #70 documentation branch.  
**Governing principle:** **PRESERVE TRUTH, NOT PLUMBING.**  
**Research principle:** **THOROUGHNESS OVER THROUGHPUT.**

## 1. Purpose

This pass deliberately searches for cards that strain or falsify the current Objective 6 model. It is not a showcase of clean anchors.

The central question for every apparent exception is:

> Can the existing primitives, coordinates, event/output signatures, resource typing, and qualifiers already express the card faithfully, or does the evidence actually force a new semantic concept?

A difficult card is **not** by itself evidence for another noun.

## 2. Source basis and method

Primary mechanical evidence used in this pass:

- project Oracle bulk snapshot `data_snapshots_2026-07-03_oracle-cards.jsonl.gz` — 38,233 Oracle-card rows inspected locally;
- project Comprehensive Rules, effective 2026-08-07;
- current official Wizards card/release material where the July corpus cannot contain newly previewed cards.

Current official supplemental source:

- Wizards, *Reality Fracture Release Notes*, 2026-09-18: <https://magic.wizards.com/en/news/feature/reality-fracture-release-notes>

Reality Fracture prerelease begins 2026-09-25 and tabletop release is 2026-10-02. Its previewed cards are used here only as adversarial design evidence; they are not treated as members of the 2026-07-03 project corpus.

Corpus-wide lexical probes were used only to find adversarial candidates, never as semantic classifications. The July snapshot contains, under deliberately broad regex triage, roughly:

- 165 cards mentioning play/cast access involving the top of a library;
- 49 cards combining opponent-library language with play/cast language;
- 80 cards with `for as long as ... remains exiled`-style permission;
- 612 cards mentioning casting without paying a mana cost;
- 1,129 cards where cast/play language appears near graveyard language;
- 692 cards matching broad top-N look/reveal language;
- 106 cards matching broad `exile cards from the top ... until` traversal language;
- 637 cards where copy language appears near cast/play language.

These are **triage counts only**. They demonstrate that the edge populations are not isolated one-card curiosities; they do not establish ontology membership.

## 3. Rules anchors that materially constrain the audit

The current CR supplies several hard distinctions that the semantic model must respect:

- **CR 121.1:** drawing is the specific operation of moving the top library card to hand. Alternate-zone permission is not draw.
- **CR 601.2:** casting is a defined procedure that moves a spell to the stack and includes cost determination/payment. Directly putting a permanent onto the battlefield is not casting it.
- **CR 701.23:** library searching has explicit hidden-zone/failure-to-find rules. A search with a stated quality can legally find fewer matching cards; a search merely for a quantity must find that quantity if possible.
- **CR 701.57 / 702.85:** Discover and Cascade are ordered library traversals with stopping predicates and privileged post-traversal use.
- **CR 118.9:** an alternative cost is paid instead of the spell's mana cost; `without paying its mana cost` is an alternative cost.
- **CR 702.51b / 702.66b / 702.126b:** Convoke, Delve, and Improvise are explicitly **not** additional or alternative costs. They affect how an already-determined total cost is paid.

Those payment rules are especially important because they falsify any semantic parent that casually treats Convoke/Delve/Improvise as examples of Magic's formal `alternative cost` category.

## 4. Adversarial card matrix

`HANDLED` means the current substrate can represent the card if the implicated facts are kept orthogonal. `PRESSURE` means the card exposes ambiguity or a structural correction that should be resolved in the whole-vocabulary audit. `FAIL` means a current documented concept/rule is contradicted or materially misleading.

| Card / construct | Oracle behavior, paraphrased | Concepts implicated | Why it strains the model | Result / candidate correction | Basis |
|---|---|---|---|---|---|
| **Plunge into Darkness** | One mode pays any amount of life, looks at that many top cards, puts one in hand, exiles the rest. | Filtering; Bounded Extraction; resource-controlled depth | The sample is finite but not fixed or necessarily small. A numeric threshold such as `3+` is arbitrary. | **HANDLED** if sample depth is an expression/coordinate. Strong evidence to keep finite-sample selection independently searchable. | Oracle corpus |
| **Dig Through Time** | Looks at seven, chooses two to hand, bottoms the rest; Delve changes payment method. | Filtering; Bounded Extraction; payment method | Same card combines finite-sample selection and Delve, which CR says is not an alternative cost. | **HANDLED**, but operation kind and payment method must be orthogonal. | Oracle + CR 702.66b |
| **Collected Company** | Looks at six and puts up to two eligible creatures directly onto battlefield; rest bottom. | Bounded Extraction; Direct Placement; eligibility | Demonstrates that finite-sample selection is not synonymous with draw/hand acquisition. | **HANDLED** if selected destination is first-class. | Oracle corpus |
| **Impulse** | Looks at four, chooses one to hand, bottoms rest. | Filtering; Bounded Extraction | Clean finite-sample anchor; useful contrast with turnover and reordering filters. | **HANDLED**. | Oracle corpus |
| **Faithless Looting** | Draw two, then discard two; has Flashback. | Filtering; draw; discard; Additional Execution | Superficially `Card Filtering`, but mechanically unlike finite-sample selection. Broad family membership must not create strong equivalence by itself. | **PRESSURE:** generic Filtering needs an operation-kind signature; finite-sample selection must remain surfaced/searchable. | Oracle corpus |
| **Fact or Fiction** | Reveals top five; opponent partitions; controller chooses one pile to hand, other to graveyard. | Bounded sample; selection authority; destination split | Selection is multi-stage and controlled by different players. `player chooses from sample` is insufficient. | **PRESSURE:** preserve staged selection authority / partition operation. No new family needed. | Oracle corpus |
| **Gifts Ungiven** | Searches broader library for up to four different names; opponent chooses two to graveyard; rest to hand. | Tutor; selection authority; destination split; search failure | Broad-library search and opponent choice make it Tutor-like despite non-hand destinations. | **HANDLED** by Tutor + search domain + chooser + destination vector. | Oracle + CR 701.23 |
| **Ad Nauseam** | Repeatedly reveals one top card, moves it to hand, loses life by mana value; controller chooses when to stop. | Sequential Library Traversal; draw-like acquisition; resource-controlled continuation | Neither fixed finite sample nor `until first qualifying card`. Traversal has a **player-controlled stop rule**. | **PRESSURE:** traversal must have explicit stop-rule type, not a Cascade-only predicate model. | Oracle corpus |
| **Lim-Dûl's Vault** | Repeatedly inspects five-card windows, optionally pays life to move each window away, then reorders the final window; gains no card. | Filtering; repeated inspection; life cost | Repeated bounded windows do not imply Bounded Extraction because no card receives privileged access/destination. | **HANDLED** if acquisition/use is separate from inspection. | Oracle corpus |
| **Genesis Wave** | Reveals top X; any number of eligible permanents go directly to battlefield; remainder to graveyard. | Bounded Extraction; Direct Placement; variable depth; many selection | X can be large and resource-controlled; selection count is `any number`; destination bypasses casting. | **HANDLED** with variable depth + selected cardinality + direct placement. | Oracle corpus |
| **Primal Surge** | Exiles top card; if permanent, may put it battlefield and repeat. | Sequential Library Traversal; Direct Placement; optional continuation | Stop depends on revealed characteristic **and** player choice after each success. | **PRESSURE:** traversal requires compound stop/continue rules. | Oracle corpus |
| **Winota, Joiner of Forces** | Each qualifying attacker independently looks at six, may place an eligible Human battlefield tapped/attacking. | Bounded Extraction; Direct Placement; repeated triggers; Engine debate | One permanent can execute multiple finite-sample selections in one combat, keyed to independent attackers. | **HANDLED** mechanically; evidence that repeatability/throughput should be stored separately from the extraction family. | Oracle corpus |
| **Cascade** | Exiles in library order until first qualifying nonland, then may cast it for an alternative cost of zero; rest bottom. | Sequential Library Traversal; CAST permission; alternative cost | Traversal, stopping predicate, permission, and payment are separable facts. | **HANDLED**; strong event-signature anchor. | Oracle + CR 702.85 / 118.9 |
| **Discover** | Traverses until first qualifying nonland; may cast free, otherwise puts it into hand. | Sequential Library Traversal; CAST permission; destination branch | Same traversal can end in cast **or** hand depending choice/legality. | **HANDLED** only if result branching is explicit. | CR 701.57 |
| **Etali, Primal Conqueror** | Each player independently traverses their library until a nonland; controller may cast any number of found nonlands free. | Multiplayer traversal; opponent-owned access; alternative cost | Multiple libraries, multiple owners, one resulting permission set. | **HANDLED** if traversal instances preserve owner/library identity before aggregation. | Oracle corpus |
| **Dack Fayden, Helping Hand** | Reveals until X creature cards where X = number of opponents, puts those creatures battlefield, then gives each to a different opponent. | Sequential traversal; multiplayer cardinality; Direct Placement; control transfer | Stops at the **Xth qualifying card**, with X derived from player count, then transfers control after deployment. | **PRESSURE:** traversal `stop_after_qualifying_count = expression`; ownership/control cannot be flattened. | WotC 2026-09-18 preview |
| **Enlightened Tutor** | Searches for artifact/enchantment and puts it on top of library. | Tutor; destination = library top | Shares `library_top` location with Future Sight-like effects but grants no permission to use the top card. | **HANDLED** and remains the critical negative anchor for Top-Library Access. | Oracle corpus |
| **Demonic Tutor** | Searches library for any card to hand. | Tutor | Clean broad-search anchor. | **HANDLED**. | Oracle corpus |
| **Praetor's Grasp** | Searches an opponent's library, exiles a card face down, lets controller play it for as long as exiled. | Tutor; opponent provenance; exile access; PLAY | Search target owner differs from access controller; destination is exile; permission is indefinite. | **HANDLED** if Tutor and use permission are composed rather than forced into one family. | Oracle corpus |
| **Gonti, Lord of Luxury** | Looks at opponent's top four, exiles one face down, permits casting it indefinitely with color-fixing. | Bounded Extraction; opponent provenance; hidden info; CAST; payment handling | Combines finite-sample selection with hidden exile and indefinite cast-only permission. | **HANDLED** with orthogonal visibility/provenance/permission/payment facts. | Oracle corpus |
| **Thief of Sanity** | On combat damage, looks at opponent's top three, exiles one face down indefinitely castable; rest graveyard. | Bounded Extraction; opponent provenance; graveyard disposition | Selected and unselected cards go to mechanically different zones controlled by different future permissions. | **HANDLED**. | Oracle corpus |
| **Opposition Agent** | Controller controls opponent during searches; found cards are exiled and become playable by Agent's controller. | Search/Tutor interaction; control another player; exile access | The semantic producer modifies another search rather than performing its own ordinary Tutor. | **PRESSURE:** listener/modifier signatures are required; do not misclassify every Agent event as its own Tutor. | Oracle corpus |
| **Pako + Haldan** | Pako exiles top card of each player's library with markers; Haldan grants PLAY for lands and CAST for marked noncreatures. | Multiplayer provenance; linked permission; PLAY/CAST; source separation | One card creates marked resources; another card supplies the permission. Card-level union would falsely imply either card alone does both. | **PRESSURE:** semantic locality/linked-source dependency must survive composition. | Oracle corpus |
| **Xanathar, Guild Kingpin** | During upkeep window, controller may see/play target opponent's top card and fixes colors; opponent cannot cast spells. | Top-Library Access; opponent provenance; PLAY; Permission Denial; horizon | Top access targets an opponent's library and coexists with interaction denial. | **HANDLED**; proves Top-Library Access cannot assume own library. | Oracle corpus |
| **Shared Fate** | Replaces each draw with face-down exile of an opponent's top card; each player can play cards they exiled this way. | Replacement effect; opponent access; draw denial; PLAY | A would-be draw becomes access to a different owner's card without a hand-zone gain. | **PRESSURE:** resource accounting cannot equate `draw prevented + access granted` with ordinary draw; permission and underlying card identity must be preserved. | Oracle corpus |
| **Knowledge Pool** | Imprints top cards from every library; casting from hand exiles that spell and permits a different imprinted spell to be cast free. | Replacement-like cast interception; shared exile pool; alternative cost; CAST | Source spell is displaced and a different card is used; multiple players share a pool. | **PRESSURE:** access facts need pool/source identity and event replacement/modification, not only source/destination zones. | Oracle corpus |
| **Possibility Storm** | A spell from hand is exiled; library traversal finds first same-type card, which may be cast free; all exiled cards bottomed. | Sequential traversal; cast replacement/modification; alternative cost | Triggered by casting one spell but supplies a different spell through traversal. | **HANDLED** if producer/consumer/event chains are explicit. | Oracle corpus |
| **Omen Machine** | Stops draws; at draw step exiles top card and automatically puts land battlefield or casts nonland free if able. | Draw denial; top-card use; Direct Placement; forced CAST | This is not merely `permission to play top card`; it executes a branch automatically. | **PRESSURE:** Top-Library Access tag should require permission/use access, while forced execution remains a separate event signature. | Oracle corpus |
| **Future Sight** | Reveals top card and grants PLAY for lands plus CAST for spells from top. | Top-Library Access; PLAY/CAST; visibility | Clean continuous unrestricted top-position access. | **HANDLED**. | Oracle corpus |
| **Mystic Forge** | Lets controller look at top and cast artifacts/colorless spells from top; can exile top via activated ability. | Top-Library Access; CAST-only restriction; filtering | A land on top is visible but unusable under CAST permission; activated exile can refresh the slot. | **HANDLED**; eligibility and refresh action must remain distinct. | Oracle corpus |
| **Oracle of Mul Daya** | Reveals top; grants land PLAY from top and an additional land play. | Top-Library Access; PLAY; deployment allowance | Access and land-play capacity are separate constraints. | **PRESSURE:** present usability depends on both permission and remaining land-play allowance. Do not bake all realization state into the tag itself. | Oracle corpus |
| **Bolas's Citadel** | Grants top PLAY/CAST; spells cast this way use life instead of mana cost. | Top-Library Access; alternative cost; PLAY vs CAST | Access, alternative payment, and land play coexist; affordability is game-state dependent. | **PRESSURE:** separate legal permission from current ability to pay. | Oracle + CR 118.9 |
| **Experimental Frenzy** | Grants top PLAY/CAST while forbidding play/cast from hand. | Top-Library Access; Permission Denial | Access rises in one zone while ordinary hand access is suppressed. | **PRESSURE:** any resource differential must support simultaneous gain/loss of access routes to existing cards. | Oracle corpus |
| **One with the Multiverse** | Continuous top PLAY/CAST plus once-per-turn free cast from hand or top. | Top-Library Access; alternative cost; frequency cap | A single source grants both persistent access and a capped payment waiver that can apply to two source zones. | **HANDLED** if permission, payment, and frequency are orthogonal. | Oracle corpus |
| **Galvanoth** | At upkeep, may inspect top card and immediately cast it free if instant/sorcery. | Resolution-only CAST opportunity; top inspection; alternative cost | No ongoing permission window; the use opportunity exists only while the ability resolves. | **HANDLED** if Access Horizon includes resolution-only opportunity. | Oracle corpus |
| **Chandra, Torch of Defiance** | Exiles top; during ability resolution may cast it; a land cannot be played; ordinary type timing is ignored. | Immediate CAST; top-card exile; timing override | Demonstrates `CAST` vs `PLAY` and resolution-only horizon more sharply than Ragavan. | **HANDLED**; strong Access Horizon fixture. | WotC 2026-09-18 notes |
| **Blazing Crescendo** | Exiles top card and permits PLAY through end of controller's next turn. | Temporary exile access; PLAY; next-turn horizon | Same general access family as Ragavan but lands and horizon differ materially. | **HANDLED** only if permission kind and horizon are prominent coordinates. | WotC 2026-09-18 notes |
| **Ragavan, Nimble Pilferer** | Combat damage creates Treasure and exiles opponent's top card; may CAST it until end of turn. | CAST-only exile access; opponent provenance; mana object | One event simultaneously creates mana material and a temporary card-origin permission. | **HANDLED**; Resource-Type Separation is necessary. | Oracle corpus |
| **Emrakul, the Exigent Doom** | Can exile itself from hand, grant a land enhanced mana production until Emrakul is cast from exile, and permits that cast for as long as it remains exiled. | Indefinite exile access; source-linked horizon; mana augmentation; CAST | Permission lifetime is defined by object state/action rather than a turn count; the same activation changes a different resource type. | **HANDLED** with condition-based horizon + typed resource outputs. | WotC 2026-09-18 notes |
| **Underworld Breach** | Gives every nonland card in controller's graveyard Escape until end step; each cast consumes three other grave cards plus escape cost. | Graveyard CAST; alternative cost; shared fuel; horizon | Potentially many distinct cards gain permissions simultaneously, but using one can consume fuel needed for others. | **PRESSURE:** permission set and resource competition are separate; do not infer realized throughput from permission count. | Oracle + CR 702.138 |
| **Yawgmoth's Will** | Until EOT, allows land play and spell casting from graveyard; cards headed to graveyard that turn are exiled instead. | Graveyard PLAY/CAST; replacement effect; horizon | Opens a whole zone while also changing future zone transitions. | **HANDLED** if access and replacement consequences remain separate. | Oracle corpus |
| **Snapcaster Mage** | ETB grants one graveyard instant/sorcery Flashback until EOT. | Targeted additional execution; CAST; horizon | Permission is attached to another card and expires; source body remains unrelated material. | **HANDLED** by use-permission assertion + execution count, no new family required. | Oracle corpus |
| **Deep Analysis / Flashback** | Spell can be cast once normally and again from graveyard for Flashback; Flashback cast is exiled when it leaves stack. | Additional Execution; alternative cost; zone permission | Same underlying card object supplies a later execution opportunity; no second physical card is created. | **PRESSURE:** do not count the later cast as another simultaneous card-origin resource. | Oracle + CR 702.34 |
| **Ephemerate / Rebound** | If cast from hand, resolution can exile the spell and create a delayed upkeep permission to cast it free. | Additional Execution; delayed trigger; exile CAST; alternative cost | The second opportunity is scheduled/automatic-permission hybrid, not simply persistent zone access. | **HANDLED** by event + delayed permission signature. | Oracle + CR 702.88 |
| **Oona's Grace / Retrace** | Can be cast repeatedly from graveyard by paying normal costs plus discarding a land. | Repeat execution; graveyard permission; additional cost | Unlike Flashback, ordinary successful use returns the card to graveyard, so the same object can support multiple later executions. | **PRESSURE:** execution multiplicity may be unbounded by the keyword itself while underlying card count remains one. | Oracle + CR 702.81 |
| **Mizzix's Mastery** | Exiles graveyard spell card, copies it, permits casting copy free; overload scales targets. | Copy; Additional Execution; graveyard; alternative cost | Execution is produced by a **copy**, not by making the original card usable again. | **PRESSURE:** Repeat-Use must distinguish original-card reuse from copied-spell execution. | Oracle corpus |
| **Mnemonic Deluge** | Exiles one instant/sorcery from a graveyard, makes three copies, permits casting all copies free. | Copy multiplicity; Additional Execution | One underlying card creates three spell executions while the original is exiled. | **FAIL** for any model equating execution count with card-resource count. Keep copies/executions typed separately. | Oracle corpus |
| **Isochron Scepter** | Exiles one small instant from hand; activated ability repeatedly copies the exiled card and can cast the copy free. | Imprint; repeatable copies; CAST; stored source | The imprinted card is not repeatedly moved/cast; generated copies are. | **PRESSURE:** `Repeat-Use` is too loose unless object identity/copy provenance is explicit. | Oracle corpus |
| **Arcane Bombardment** | On first instant/sorcery each turn, randomly exiles another grave spell, then copies every card it has exiled and may cast copies free. | Accumulating stored set; copy execution; first-each-turn cap | Stored capacity grows while processor firing is capped; each firing can output many executions. | **PRESSURE:** exposes distinct axes for stored repertoire, firing frequency, and output multiplicity. | Oracle corpus |
| **Wheel of Fortune** | Each player discards hand then draws seven. | Wheel alias; draw; discard; multiplayer differential | Resource outcome depends on each player's starting hand. The card has no fixed intrinsic positive differential. | **PRESSURE:** resource differential is a derived state/context result, not a card family membership. | Oracle corpus |
| **Eternal Witness** | ETB may return target grave card to hand while Witness remains battlefield. | Graveyard Access; retrieval; Card Resource Differential | If the target grave card was already legally usable due to another effect, `recovery` may change zone/persistence without increasing the set of usable underlying card resources. | **PRESSURE:** resource differential must derive from before/after accessible resource identity, not assume `graveyard -> hand = +1`. | Oracle corpus |
| **The One Ring** | Tap adds burden counter then draws cards equal to burdens; normal tap availability limits native firing. | Recurring draw; Engine; stored state; throughput | Community readily calls this a draw engine, but current strict Engine definition may exclude it unless untap support is supplied. | **PRESSURE:** test whether `Engine` should be canonical hard family or a community/strategic label over repeatability/throughput facts. | Oracle corpus |
| **Phyrexian Arena** | Draws one at upkeep and loses life. | Recurring draw; Engine terminology; scheduled output | Current model says recurring card advantage but not Engine because upkeep scheduled. Community usage often says `draw engine`. | **PRESSURE:** strong terminology/retrieval collision. | Oracle corpus |
| **Toski, Bearer of Secrets** | Each controlled creature dealing combat damage to a player independently draws. | Card Engine; event scaling | Preserves input multiplicity within one combat window. | **HANDLED** by throughput coordinates; positive scalable-processing anchor. | Oracle corpus |
| **Chivalric Alliance** | One draw when attacking with two-or-more creatures; additional attackers do not increase that trigger count. | Recurring draw; threshold compression; Engine | Mechanically contrasts with Toski, but both are valuable recurring card sources to players. | **PRESSURE:** throughput fact is real; hard exclusion from player-facing `Engine` may hurt retrieval. | Oracle corpus |
| **Grazilaxx, Illithid Scholar** | One draw per damaged player when one-or-more creatures connect. | Engine; aggregation; multiplayer cardinality | Creature multiplicity is compressed, but multiple opponents can still yield multiple outputs. | **PRESSURE:** shows why structural cardinality and throughput should be coordinates, not semantic worth judgments. | Oracle corpus |
| **Nest of Scarabs** | One-or-more -1/-1 counters event makes `that many` tokens. | Engine; trigger compression; output magnitude | Trigger count is compressed while output magnitude preserves quantity. | **HANDLED** as event/output scaling; supports demoting `engine-ness` to a derived label over harder facts. | Oracle corpus |
| **Well of Lost Dreams** | Each life-gain event can be followed by variable mana payment to draw up to that life amount. | Reusable processor; resource conversion; Card Engine | Repetition is externally fueled and variable-output; no tap/turn cap in text. | **HANDLED** by input/output/payment/throughput facts; good positive processor anchor. | Oracle corpus |
| **Dream Halls** | A spell's controller may discard a same-color card rather than pay mana cost. | Formal alternative cost; resource substitution | Unlike Convoke/Delve/Improvise, this really is an alternative cost under CR 118.9. | **FAIL** for a parent that places all four in the same formal `Alternate Payment` bucket. Split formal alternative cost from payment-substitution methods. | Oracle + CR 118.9 |
| **K'rrik, Son of Yawgmoth** | Black symbols in costs may be paid with life instead of black mana. | Payment substitution; life resource; cost payment | Does not simply reduce the cost to zero; changes how symbols can be paid. | **PRESSURE:** payment method needs a lower-level representation independent from alternative-cost labels. | Oracle corpus |
| **Convoke / Delve / Improvise** | Tap creatures / exile grave cards / tap artifacts to pay portions of an already-determined total cost. | Payment method; cost payment | CR explicitly says these are **not** additional or alternative costs. | **FAIL** for current `Alternate Payment / Payment Substitution` tree name if `Alternate Payment` is read as Magic's alternative-cost category. Preserve a distinct payment-method/substitution operation. | CR 702.51b / 702.66b / 702.126b |
| **Affinity** | Reduces generic cost according to stated affinity quantity. | Cost Reduction | Unlike Delve/Convoke, changes total cost itself. | **HANDLED** by Cost Reduction primitive/signature. | CR 702.41 |
| **Omniscience** | Lets controller cast hand spells without paying mana costs. | CAST; formal alternative cost | Spell is still cast, goes on stack, and can generate cast triggers. | **HANDLED**; critical negative for Direct Placement. | Oracle + CR 118.9 / 601.2 |
| **Elvish Piper** | Activated ability puts creature card from hand directly battlefield. | Direct Placement | No casting event occurs. | **HANDLED**; clean positive anchor. | Oracle corpus |
| **Reanimate** | Puts target grave creature battlefield under controller, with life loss. | Graveyard Access; Direct Placement; life cost | Retrieval and deployment happen without casting. | **HANDLED** compositionally. | Oracle corpus |
| **Show and Tell** | Each player may put eligible permanent card from hand battlefield. | Direct Placement; symmetry; multiplayer | Simultaneous-ish multi-player choices and direct placement; source owners/controllers differ. | **HANDLED** if affected-player scope is explicit. | Oracle corpus |
| **Sneak Attack** | Puts creature from hand battlefield with haste, then delayed sacrifice. | Direct Placement; temporary horizon; delayed consequence | Direct placement has a cleanup horizon; `placement` alone is insufficient. | **HANDLED** with delayed consequence signature. | Oracle corpus |
| **Extrapolate the Impossible** | Reveals exactly two differently named owned cards from outside game; opponent chooses one to hand. | External-zone selection; selection authority; acquisition | Looks Tutor-like but does not search the library at all. | **HANDLED** if Tutor remains library-search-specific and selection primitives are zone-general. | WotC 2026-09-18 preview |
| **Uldaros Theorix** | On cast-ETB, exiles up to one nonland of each card type from graveyard, copies them, then permits casting copies with total MV cap 6 free; permanent spells become tokens. | Graveyard access; copies; cast budget; generated board objects | One effect creates copy executions and potentially permanent tokens while original grave cards remain separately tracked/exiled. | **PRESSURE:** execution copies, underlying cards, cast-budget constraint, and token objects must remain distinct resource types. | WotC 2026-09-18 preview |

## 5. Strongest failures / unresolved questions exposed by Step 1

### F1 — `Card Access Differential` is superseded durable debt

The branch still contains `OBJECTIVE6-CARD-ACCESS-DIFFERENTIAL-RULING-2026-09-19.md`, but the later durable Captain checkpoint explicitly says **do not create a separate Card Access Differential metric**. The current session handoff repeats that correction.

This is a documentation contradiction, not a live semantic choice. Step 2 should retire/supersede that file rather than preserve two metrics.

### F2 — Card Resource Differential cannot be a naïve per-card static label

Shared Fate, Experimental Frenzy, Oracle of Mul Daya, Underworld Breach, Wheel of Fortune, and Eternal Witness show that `usable card-origin resource` depends on before/after permissions, underlying card identity, player-relative state, and sometimes zone-specific constraints.

The current safest direction is:

- store the underlying hard resource/access facts canonically;
- derive resource differential from a defined comparison context;
- count **distinct underlying card-origin resources**, not permission clauses or spell copies;
- keep refreshability/throughput and execution multiplicity separate from simultaneous resource count;
- distinguish legal permission from present affordability/realization.

Whether CRD should be available as a card-level capability summary as well as a state-derived accounting output remains **OPEN**.

### F3 — finite-sample selection is real, but generic `Card Filtering` is too weak by itself

Dig Through Time, Collected Company, Plunge into Darkness, Impulse, Fact or Fiction, Genesis Wave, and Winota share a coherent finite-sample-selection pattern despite radically different destinations and selection authority.

Faithless Looting, Lim-Dûl's Vault, Brainstorm/scry/surveil-style operations, and pure self-mill can all be reasonably called `filtering` in broad player language but do not perform that same operation.

Therefore consolidation survives only if the substrate makes **operation kind** first-class and finite-sample selection remains independently queryable. Generic Filtering membership should not carry heavy similarity weight by itself.

### F4 — Sequential Library Traversal is broader than Cascade/Discover

Ad Nauseam, Primal Surge, Etali, Possibility Storm, Cascade, Discover, and Dack Fayden, Helping Hand expose multiple stop architectures:

- first card satisfying predicate;
- first N qualifying cards;
- repeat while predicate succeeds;
- player chooses when to stop;
- one traversal per player/library.

The pattern is real, but the stable machine fact is an **ordered traversal event with an explicit stop rule**, not a Cascade-shaped family definition.

### F5 — `Repeat-Use` cannot mean “another card resource”

Flashback, Rebound, Retrace, Mizzix's Mastery, Mnemonic Deluge, Isochron Scepter, and Arcane Bombardment show at least three mechanically different cases:

1. the same underlying card later becomes castable again;
2. a delayed permission schedules another cast of that card;
3. a source generates and casts **copies** of a stored/exiled card.

Execution multiplicity and card-origin-resource count must stay separate.

### F6 — Engine has a real hard-fact core but a serious terminology/retrieval collision

Toski, Chivalric Alliance, Grazilaxx, Nest of Scarabs, The One Ring, Phyrexian Arena, and Well of Lost Dreams validate hard coordinates such as:

- input event;
- input aggregation;
- firing frequency/cap;
- output multiplicity;
- variable output magnitude;
- processor retention;
- external fuel requirement.

They do **not** yet prove that `Engine` should remain a canonical family with a strict gate. Community/player use of `draw engine` is materially broader than the current Foundry definition, and a hard exclusion can damage retrieval even when the underlying throughput facts are correct.

Step 2 must decide whether Engine is a canonical family, a derived structural signature, or a strategic/community alias over harder facts.

### F7 — current payment naming conflates formal Magic categories

The CR is decisive:

- Affinity is Cost Reduction;
- `without paying its mana cost` and other `rather than pay` structures are formal alternative costs;
- Convoke, Delve, and Improvise are expressly **not** alternative or additional costs.

The current documented `Alternate Payment / Payment Substitution` parent therefore needs structural/naming correction. The underlying distinction is useful; the present umbrella name is not mechanically safe.

### F8 — Resource-Type Separation is load-bearing but may not deserve ontology membership

Ragavan, Uldaros, Emrakul, Mnemonic Deluge, and token/mana examples strongly validate typed resource accounting. However, the evidence supports it most strongly as a **substrate design law / typed-resource model**, not necessarily a user-facing semantic family.

### F9 — Top-Library Access survives attack as a surfaced query facet

The positive/negative boundary remains unusually clean:

- Future Sight, Mystic Forge, Oracle of Mul Daya, Bolas's Citadel, Experimental Frenzy, Xanathar: positive;
- Enlightened Tutor, reveal/look-only effects: negative.

The surfaced include/exclude value is real. The difficult part is not membership; it is downstream accounting of the currently usable top card.

### F10 — Direct Placement survives mechanically; the old working name does not

Elvish Piper, Reanimate, Show and Tell, Sneak Attack, Genesis Wave, Winota, and Omniscience make the cast-vs-put distinction robust. The mechanic deserves a stable event signature and likely a surfaced retrieval concept. `Deployment Bypass` remains unnecessary architecture jargon.

## 6. Step-1 verdict

The weird-card pass does **not** justify adding another Card Access noun. It instead increases pressure to make the substrate more compositional:

- permission assertions;
- source/destination/owner/controller coordinates;
- selection and selection-authority structure;
- ordered traversal + stop rules;
- typed payment operations;
- typed resource outputs;
- distinct underlying card identity;
- execution/copy multiplicity;
- duration/expiration;
- event producer/consumer signatures;
- derived accounting only after those facts are preserved.

The strongest surviving surfaced concepts at this stage are those with clear retrieval value and clean boundaries, especially Tutor, Top-Library Access, finite-sample selection, Ramp, and major Interaction functions. The whole-vocabulary audit must now determine which of the other working nouns are actually forced by evidence.

## 7. Control boundary

This research artifact does **not** authorize:

- S16B freeze;
- broad corpus reclassification;
- implementation acceptance;
- merge of PR #70;
- accepted implementation head movement;
- AQ4 resumption;
- Bridge v0 activation;
- Step6;
- `main` movement.

It is the required evidence input to the next step: the whole-vocabulary adversarial semantic audit.
