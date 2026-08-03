# CODEBOOK NAMING GRAMMAR v1.0 (RATIFIED 2026-07-30)

Status: RATIFIED by Captain, 2026-07-30 (decisions D-1 through D-5 resolved per
recommendation; see section 13). Law: every axis slug —
authored, grammar-instantiated, or renamed at the audit walk — must validate
against this document. Versioned alongside the codebook. Every vocabulary claim
below is anchored to the local `mtg-comprehensive-rules.md` (June 19, 2026);
CR citations were verified against that file on 2026-07-30, not recalled.

Design goals, in priority order:
1. **No two slugs may describe the same mechanic** (the
   scales-token-count-with-x / token-count-scales-with-x duplication class).
2. **No slug may be readable as two different mechanics** (the
   grants-trample-to-countered-creatures class).
3. **Every closed mechanical family is enumerated in advance** so cards cannot
   fall between siblings (the sorcery-speed vs during-combat class).
4. **Slugs are machine-decomposable** so parents, facets, and DET patterns
   derive from names without human interpretation.

---

## 1. The slot grammar

Every axis slug is a hyphen-joined sequence of slots in this fixed order:

```
[DELIVERY]-[EFFECT]-[OBJECT]-[SCOPE]-[QUALIFIER...]
```

- **DELIVERY** — how the ability happens (ability class / trigger family).
  OMITTED for spell abilities (CR 113.3a): an instant/sorcery's resolution
  effect is the unmarked default. `burst-draw`, `targeted-destruction`,
  `counters-target-spell` are spell-delivery slugs. Everything non-spell is
  MARKED.
- **EFFECT** — the standardized verb phrase (section 4).
- **OBJECT** — what the effect acts on (section 5). Omitted when the effect
  verb already binds it (`loot`, `scry`, `mill-self`).
- **SCOPE** — ownership/breadth (section 6). Omitted when the axis's scope=
  field carries it and no sibling differs only by scope; REQUIRED the moment a
  scope-sibling exists (the Q1/Q2 lesson: scope moved into the name for
  tap-or-untap because siblings differ there).
- **QUALIFIER** — closed modifiers: `-conditional`, `-mass` (see 6),
  `-scales-with-<stat>` (see 7), token/counter types (see 8), cost qualifiers
  ("Free must be Free" — cost words in names are binding, ratified b2).

Compounds remain the only authored thing (addendum-3 §3): one slug asserts one
ability doing one thing. Multi-ability cards get multiple tags, never fused
slugs (M8, generalized batch-6 D3).

**Membership is not exclusive (Captain-ratified 2026-08-02).** A card holds
membership on **every axis it genuinely satisfies**. Modal modes each earn
their axis — Blizzard Specter is a member of both its discard axis and its
bounce axis. A single ability decomposes onto its compound slug *and* the
facet axes it is built from — Riptide Entrancer is a member of
`combat-damage-to-player-permanent-control-theft`, `permanent-control-theft`
and `optional-self-sacrifice-in-trigger`. This extends the rule above: §1
already covered multiple *abilities*, this covers multiple *axes per ability*.

This ratifies existing practice rather than changing it — measured
2026-08-02, **1,236 of 5,844 carded cards (21.1%) already sat on more than
one active axis**, up to 5. Consequence to respect: member counts are NOT a
partition of the corpus, and any consumer assuming one-card-one-home is
wrong. Record: `docs/MEMBERSHIP-RATIFICATION-PACKET-2026-08-02.md`.

Formatting law: lowercase ASCII, hyphens only, no articles ("a", "the"), no
plurals except where the mechanic is inherently plural (`-two-target-creatures`,
mass effects), `plus1`/`minus1` for counter polarity (ratified), `x` for the
variable.

---

## 2. DELIVERY slot — closed vocabulary (CR-anchored)

| Slot value | Means | CR anchor |
|---|---|---|
| *(none)* | spell ability, applies on resolution | 113.3a |
| `activated` | "[Cost]: [Effect]" | 113.3b |
| `static` | written as a statement, continuously true | 113.3d |
| `etb` | triggered, "when ~ enters" | 113.3c |
| `leaves-battlefield-trigger` | triggered, any LTB (superset of death-trigger; a card saying "leaves the battlefield" NEVER takes `death-trigger`) — the `-trigger` suffix is kept to match the live axis family | 700.4 boundary |
| `attack-trigger` | "whenever ~ attacks" | 113.3c |
| `cast-trigger` | "when(ever) [someone] casts" — requires cast verbiage; never an ETB; the trigger EVENT must be the cast itself, not a condition about casting (b6 Village Ironsmith ruling) | 701.5a |
| `combat-damage-to-player` | "deals combat damage to a player" | — |
| `combat-damage-to-creature` | "deals combat damage to a creature" | — |
| `any-damage-to-player` | "deals damage to a player/opponent" with NO combat restriction — fires off pingers, burn, fight effects (Captain-ratified 2026-08-02) | 120.3 |
| `any-damage-to-creature` | "deals damage to a creature" with NO combat restriction (Captain-ratified 2026-08-02) | 120.3 |
| `upkeep-trigger` | "at the beginning of [whose] upkeep" | 113.3c |
| `landfall` | the landfall ability word | 207.2c |
| `loyalty` | planeswalker loyalty ability — is activated but always marked `loyalty`, never `activated` (b7 Ob Nixilis crack) | 606.1 |
| `replacement` | "instead" / "skip" / "enters with/as" shapes | 614.1a–c |
| `delayed` | delayed triggered ability created on resolution | 603.7 |
| `kicker` | kicked-conditional bonus | 601.2b |
| `death-trigger` | triggered, graveyard from battlefield | 700.4 |
| `becomes-targeted-trigger` | triggered, "becomes the target of a spell or ability" (Ward's family; walk-ratification Q2, 2026-07-31) | 702.21a |
| `blocks-or-becomes-blocked-trigger` | triggered, a blocking/being-blocked event (Bushido/Flanking/Rampage/Afflict shape; walk-ratification Q2, 2026-07-31) | 509 |

Rules:
- DELIVERY is determined by ability STRUCTURE, never by effect words (batch-4
  D1 / batch-7 feedback #1 codified). An Attraction's Visit/Prize are
  triggered, not activated (b7 Pick-a-Beeble... b6 finding).
- `dies` vs `leaves-battlefield` is a hard boundary both directions.
- RATIFIED (D-1): `death-trigger` stays the family word for dies-triggers;
  CR 700.4 anchors every definition in the family. No `dies-` slugs.
- `combat-damage-triggers-<effect>` normalizes to
  `combat-damage-to-player-<effect>` / `-to-creature-<effect>` at the walk —
  the b7 Guild Thief definition bug is exactly this slot being unmarked.
- **A card does not deliver an ability it CREATES (Captain-ratified
  2026-08-02).** When a card produces an ability — via an **emblem**, a
  **delayed trigger**, an ability **granted** to another permanent, or a
  **token's** printed text — the delivery belongs to the *creating* ability
  (`loyalty`, `delayed`, …), never to the created one. Garruk, Caller of Beasts
  is not a `cast-trigger-` card because its **−7 emblem** says "whenever you
  cast a creature spell"; Jace, Cunning Castaway is not a
  `combat-damage-to-player-` card because a **+1** made that delayed trigger.
  Membership on the EFFECT axis may still be correct; the DELIVERY axis is not.
  This is the same principle as "DELIVERY is determined by ability STRUCTURE,
  never by effect words", applied one level up: read *whose* ability it is
  before reading what it does. Record:
  `docs/REAUDIT-TIER-1-FINDINGS-2026-08-02.md` §2a.
- **A `{T}` in an activated cost is AXIS IDENTITY (Captain-ratified
  2026-08-02, D3f).** Tapping caps an ability at once per turn; an
  otherwise-identical ability without it goes arbitrarily wide with mana. That
  is a when/whether difference, not a magnitude one, and it separates a combo
  piece from a value creature — so the tapped and untapped forms are siblings,
  never one axis. Worked case: `activated-tap-grants-haste-other-creature-you-control`
  (Paragon of Fierce Defiance) vs `activated-grants-haste-any-creature` (Boros
  Guildmage). Test to apply: does the distinction change WHEN or WHETHER the
  effect can happen (split), or only how much (parameter, per batch-5's
  counter-polarity ruling)? Record:
  `docs/TIER-2-DECISION-PACKET-2026-08-02.md` D3f.
- **`combat-` is a RESTRICTION, not decoration (Captain-ratified 2026-08-02).**
  A card reading "whenever ~ deals damage to an opponent" makes no
  combat claim and takes `any-damage-to-player`. The two are different
  mechanisms for deck-building — an any-damage trigger fires off pingers, burn
  and fight effects — so they never share an axis. Record:
  `docs/DAMAGE-DELIVERY-RULING-2026-08-02.md`.

## 3. Activation-restriction family — fully enumerated, DET-owned

The batch 5–7 failure class (own-upkeep collapse, Kjeldoran during-combat).
This family is CLOSED, exact-phrase, and moves entirely to Lane 1 (DET);
SYNTH never assigns these again. Each row is a ratified DET pattern:

| Printed phrase (anchored, both templating eras) | Slug |
|---|---|
| "Activate only as a sorcery" (CR 602.5d) | `activation-restricted-to-sorcery-speed` |
| "Activate only as an instant" (CR 602.5e) | `activation-restricted-to-instant-speed` |
| "Activate only during your turn" | `activation-restricted-only-during-your-turn` |
| "Activate only during your upkeep" | `activation-restricted-to-own-upkeep` |
| "Activate only during combat" | `activation-restricted-during-combat` |
| "Activate only during an opponent's turn" | `activation-restricted-during-opponents-turn` |
| "Activate only once each turn" (CR 602.5b) | `activation-restricted-once-each-turn` |
| "Activate only if ..." (condition-gated) | `activation-condition-gated` (wide net; condition facet to ledger) |

DET patterns must canonicalize "Activate this ability only ..." (older
templating) to the modern phrase (Lesson-1 both-polarity discipline applied to
templating eras). Compound restrictions ("only during combat and only if...")
get EVERY applicable tag (M8 logic applied to restrictions).

The same enumeration discipline applies at the walk to any other closed CR
family the codebook touches: keyword classes (CR 702 first lines — already the
keyword-bucket job), replacement shapes (614.1a/b/c), casting-timing families.

## 4. EFFECT verbs — standardized forms

One verb per mechanic, chosen once, used everywhere:

- `destroy`, `exile`, `bounce` (return to hand), `tuck` (to library),
  `sacrifice`, `discard`, `mill`, `draw`, `loot` (draw-then-discard),
  `scry`, `surveil`, `proliferate`, `tutor` (search library), `reanimate`
  (graveyard → battlefield), `regrowth` (graveyard → hand, ratified b5 vocab),
  `create-token`, `pump` (+P/+T), `debuff` (−P/−T), `damage`, `gain-life`,
  `lose-life`, `drain` (damage/loss + symmetric gain), `tap`, `untap`,
  `tap-or-untap`, `transform`, `copy`, `counters` (verb — see section 8),
  `grants-<keyword>`, `taxes` (cost increase), `cost-reduction`.
- RATIFIED (D-2): bare verb stem everywhere EXCEPT the `counters-` verb
  (section 8) — the b5 D14 `create-token-<type>` standard generalizes.
  All `creates-` slugs normalize at the walk.
- "scroll" = instant-or-sorcery(+interrupt) card (ratified b5 vocab; glossary
  entry required in the embedded codebook).
- "uncounterable" = adjective, "this spell can't be countered" (ratified Q4,
  walk-ratification 2026-07-31 — `rule:cant-be-countered` renames to
  `rule:spell-uncounterable`, replacing the banned `countered` participle).
- "imposes" = verb, an ability forces a state onto something OTHER than its
  own source (ratified 2026-07-31, B3/B4 follow-on — Captain-authored
  `rule:imposes-enters-tapped`, the Root Maze class sibling of
  `rule:enters-tapped`).

## 5. OBJECT vocabulary

`creature`, `artifact`, `enchantment`, `planeswalker`, `battle`, `land`,
`permanent`, `nonland-permanent`, `spell`, `noncreature-spell`,
`creature-spell`, `player`, `opponent`, `any-target` (damage only, = the CR
"any target" shorthand), `card-in-graveyard` families
(`creature-card-graveyard` etc.), token types (section 8).

Per-object-class siblings are the law for every `targeted-<action>` family
(M8 generalized, b6 D3): OR-shaped multi-class targets get every applicable
class tag; the class lattice (`targeted-bounce-<class>`,
`targeted-destruction-<class>`...) is a ratified grammar with virtual nodes.

## 6. SCOPE vocabulary

`self` (the source), `own` (yours), `opponent`, `any`, `each`/`mass-`
(non-targeted, all-covered), `target` (ONLY when the word "target" appears in
the ability per CR 601.2c — the b7 Unwind ruling: "untap up to three lands"
without "target" may NOT sit in a `-target-` slug), `defending-player`
(CR 506.2; the bare word "defender" is BANNED in slugs — it collides with the
Defender keyword, Captain's b7 ruling generalized), `two-target` (fixed
plurality), `-conditional` (an intervening-if or "unless" gate on the same
ability; the gate must be quoted in evidence).

## 7. Scaling standard

One connective, one order, closed stat list — RATIFIED (D-3):
**`<subject>-scales-with-<stat>`** (matches
`x-scales-with-permanent-count` and the ledger's N-scales-with-N scheme;
`-scaled-by-` is retired at the walk).

Closed stat vocabulary (b6/b7 confusion pairs made explicit): `creature-count`,
`hand-size`, `own-counters` (counters ON the source; the charge-counter class),
`graveyard-count`, `graveyard-creature-count`, `land-count`, `land-type-count`,
`permanent-count`, `attacker-count`, `legendary-creature-count`, `mana-value`,
`life-gained`, `x`, `opponent-count`, `target-count` (the Hinata stat),
`token-count`, `color-count`, `target-color-count` (the colors of the TARGET
 itself, not a board count — Captain-ratified 2026-08-02, D3e), `charge-counters` (alias of own-counters where
the type matters), `opponent-tapped-creature-count` (F3, walk-ratification
2026-07-31 — required by the draw-scales-with-opponent-tapped-creature-count
D-3 rename target).

The two token axes under this standard (answers b7 line-84):
- X scales HOW MANY tokens → `token-count-scales-with-x` (absorbs the
  duplicate `scales-token-count-with-x` at the walk).
- X scales counters ON one created token → `create-token-with-x-counters`.

## 8. The counter/token disambiguation laws

Hard rules, each anchored:
1. **Noun sense (CR 122.1) is always TYPED:** `plus1-counter`, `minus1-counter`,
   `charge-counter`, `stun-counter`, `loyalty-counter`, `<name>-counter`.
   The bare noun "counter" never appears in a slug. Generic axes use
   `-counters` only with a binding word (`etb-with-counters`,
   `counter-removal-as-activation-cost` → walk-renames to typed or
   `-counters-` forms as feasible).
2. **Verb sense (CR 701.6) is always `counters-<object>`** (`counters-target-spell`,
   `counters-noncreature-spell`). The participle "countered" is BANNED
   (b7 grants-trample ruling generalized).
3. **A counter is not a token and a token is not a counter (CR 122.1,
   verbatim).** Any slug naming one must have evidence quoting that one —
   the b7 Lat-Nam/Gnarlid effect-suffix check, now grammar law.
4. Token types are their predefined names: `treasure`, `clue`, `food`,
   `blood`, `gold`, `powerstone`, `mutagen`, `lander`, `creature` (with P/T
   left to evidence), `mana-producing-artifact` (umbrella; excludes treasure,
   which owns its own node — S5 semantics at schema pass).

### 8a. CDR-09 amendment — sense is carried by POSITION and BINDING, not by grammatical number (Captain-ratified 2026-08-02)

Rules 1–2 above disambiguate by number: singular `counter` = noun, plural
`counters` = verb stem. **That is insufficient, because plural is itself
ambiguous** — `counters` is both the verb stem AND the noun plural.
`rule:etb-with-counters` (noun) and `rule:counters-target-spell` (verb)
carry the identical token. This is the root of the `canonicalize_label`
corruption: `counters` sits in EFFECT_VOCAB and `counter` in the qualifier
sets, so the canonicalizer sorts by grammatical number rather than by
sense.

**Ratified replacement test, enforced across the WHOLE slug — not only in
final-token position, closing the `validate_slug` gap that let
`rule:self-counter-growth` and `rule:etb-with-counters` pass clean:**

1. **VERB sense (CR 701.6)** — the token is `counters` (plural) and is
   **immediately followed by what is countered** (`spell`, `ability`, or a
   restriction word binding to one, e.g. `noncreature-spell`). Never bare,
   never slug-final. Singular `counter` in verb sense is BANNED.
2. **NOUN sense (CR 122.1)** — `counter`/`counters` must be **bound on the
   left**, by either:
   - a counter TYPE word (`plus1`, `minus1`, `charge`, `stun`, `oil`,
     `energy`, `loyalty`, `<name>`), or
   - the preposition `with` (`etb-with-counters`), or
   - **`any`** — newly ratified for axes that genuinely span every counter
     type and therefore cannot be typed. `any-counter` / `any-counters`.

**Why `any-` and not a sense-marker like `counter-object`:** a counter is
**not** an object. CR 109.1 defines *object* as a spell, permanent, card,
token, copy, or emblem; CR 122.1 defines a counter as "a marker placed on
an object or player." The CR's own word for the noun sense is **marker**.
Worse, the VERB sense is the one that genuinely acts on objects (a spell or
ability on the stack IS an object), so a `-object` marker would point at
the wrong sense. `any-` adds no new vocabulary and fills the existing type
slot.

**Consequence for the canonicalizer (ADD-08), measured 2026-08-02.**
`CR-VOCABULARY-AUDIT.md` §4 proposes local adjacency — `counters` is EFFECT
iff followed by an OBJECT token, QUALIFIER iff preceded by a type word or a
`with`-binding — and states it becomes decidable once these renames land.
Tested against all 33 counter-bearing active axes, scored against each
axis's definition-confirmed sense:

| names | misfiles |
|---|---:|
| current | **17 of 33 (52%)** |
| after the §12a renames | **4** |

So the dependency is REAL: 13 of the 17 are fixed by nothing except the
renames, because slugs like `rule:self-counter-growth` have no type word
for the rule to bind to. Implementing position-aware bucketing before the
walk would misfile half the counter axes.

But §4's claim is **too strong** — the renames alone do not finish the job.
Three of the four residuals are defects in the rule as specified, not in
the names, and both must be fixed before ADD-08 is implemented:

1. **The rule must look past SCOPE tokens when hunting the object.** In
   `counters-target-spell` the token after `counters` is `target` (SCOPE,
   §6), not `spell`, so a literal "followed by an OBJECT token" test finds
   nothing. Affects `counters-target-spell`,
   `activated-counters-target-spell`, `-unless-pays`.
2. **Left type-binding must take precedence over right object-adjacency.**
   `cast-trigger-self-plus1-counter-noncreature-spell` is noun sense (the
   card gains a +1/+1 counter when its controller casts a noncreature
   spell) but has a type word on the left AND an object on the right.
   Checking the object first returns verb, which is wrong.

With both corrections applied after the walk, the residual is expected to
be zero. ADD-08 stays blocked on §12a either way.

## 9. Cost-vs-effect law

Anchors: CR 113.3b ("[Cost]: [Effect]") and CR 601.2b (additional costs).
- `-cost-` / `-as-activation-cost` / `additional-cost-` slugs require the
  action LEFT of the colon or inside an "as an additional cost" clause.
- Life/sacrifice/discard occurring in resolution text NEVER satisfies a cost
  slug (b6 Fleshless Gladiator, b7 Fountain of Youth/Pick-a-Beeble class).
- "Free must be Free" (ratified b2) is a special case of this law.

## 10. Slug validator (Lane-1 lint, wire into emit + SUP)

A DET check every proposed slug must pass before entering the codebook or the
grammar lane. Pseudo-spec for `validate_slug.py`:
1. Charset: `^[a-z0-9]+(-[a-z0-9]+)*$`.
2. Banned tokens: `defender`, `countered`, bare `counter` as final noun
   without type, `free` unless the axis definition quotes a zero-cost,
   `creates` (post-D-2), `scaled` (post-D-3), `token` immediately adjacent to
   `counter` without the section-8 shapes.
3. Every hyphen-token must appear in the closed vocabularies (sections 2,
   4–8) or in the ratified glossary; unknown tokens → halt loudly (new
   vocabulary is a Captain ratification, not a typo).
4. Slot order check via greedy match against section 1.
5. Synonym collision check: normalized slug (stem verbs, strip connectives,
   sort scaling pairs) must be unique across the codebook — catches the
   token-count duplication class mechanically.
6. Restriction-family, counter-law, and cost-law special checks.
Validator failures are never auto-fixed; they surface for ruling.

## 11. Grammar instantiation mechanics (wiring, per CORPUS-PASS-PLAN §11.2)

- Ratified grammars live in `docs/grammars.json`: stem + ordered facet slots +
  closed per-slot vocab + CR anchor + instantiation examples.
- A virtual node instantiates the moment one quote-verified member arrives —
  no fresh ratification (the grammar was ratified). The b7 Brandywine Farmer
  case is the model: `leaves-battlefield-create-token-food` should have
  self-instantiated. SUP and emit both gain this behavior; SUP ledger-flagging
  a grammar-composable home is now a protocol error.
- SYNTH labeling: `lane=codebook-grammar` for grammar-composed slugs;
  validator runs on every one; anything neither exact-codebook nor
  grammar-valid stays `lane=free`.
- Seeded grammar families (already ratified across b5–b7): create-token-<type>;
  etb-create-token-<type>; leaves-battlefield-trigger-create-token-<type>;
  targeted-<action>-<class>; activated-tap-or-untap-<scope>;
  draw-second/cast-second prefix scheme; activation-restriction family (§3);
  grants-<keyword> facet scheme (T1 tension still parked for schema pass —
  grammar defines the NAMES, the b1-Q1 engine question stays open).

## 12. Migration ledger (the walk's worklist — logged, executed AT the walk)

Known non-conforming axes as of v0.7-pending (worked examples, not
exhaustive; the walk validates all ~300):
- `scales-token-count-with-x` → MERGE into `token-count-scales-with-x` (dup).
- `creates-token-with-x-scaled-counters` → `create-token-with-x-counters`.
- All `-scaled-by-` slugs → `-scales-with-` (D-3).
- `combat-damage-triggers-loot/-discard/-treasure/-proliferate` →
  `combat-damage-to-player-*` or `-to-creature-*` per member evidence.
- `attack-trigger-damage-defender` → three-way split (b7 §12 pending).
- `death-trigger-card-draw` → reuse original slug `death-trigger-draw-card`
  (registry continuity) — then family-normalize per D-1.
- ~~`counter-removal-as-activation-cost` → keep (verb-adjacent but shielded by
  `-removal-`); revisit under section-8 rule 1 at the walk.~~ **SUPERSEDED
  by the CDR-09 walk below.**

### 12a. CDR-09 counter-homograph walk (Captain-ratified 2026-08-02) — **EXECUTED 2026-08-02**

> **EXECUTED.** All 16 renames applied name-only; codebook sha256
> `61af1a1d7f81504f422feb4d…` → `d0b1183fc155f13e7b1ae025…`. 307 active axes
> before and after. The 33/16/17 partition below was re-derived from live state
> and confirmed **set-identical**, not merely equal in count. Counter-bearing
> active axes now measure **0 non-conforming**. Full record, the applied target
> strings, and two residual items the walk does not touch:
> `docs/CDR-09-WALK-DERIVATION-2026-08-02.md`.
>
> Note for anyone re-running the conformance check: §8a is **not** the only
> ratified law governing a counter token. §7's scaling standard
> (`own-counters`, `charge-counters`, and the verbatim
> `create-token-with-x-counters`), batch-5's polarity-is-a-parameter ruling,
> and batch-5 D12 each govern specific slugs. A checker that knows only §8a
> reports all of them as defects — it did, and two of those false positives
> would have destroyed ratified names. `foundry_cdr09_derive.py` encodes each
> with its citation.

Measured live against codebook v0.7 this session, classified against each
axis's own ratified DEFINITION (not by name-guessing). **33 active axes
carry a counter token; 16 are non-conforming.** Members and definitions are
unchanged by every row below — these are name-only.

Correcting `CDR-PROPOSALS.md` rev 2, which stated 34 axes and "~15 renames
(3 verb-side, 9 noun-side)". Live measurement: **33 axes, 16 renames —
3 verb-side, 10 noun-side, 3 `any-`.** The noun count was off by one and
the axis count by one. Third arithmetic drift caught in rev 2; see ADD-06.

**Verb-side (3)** — singular `counter` in verb sense, banned by 8a rule 1:

| from | to |
|---|---|
| `rule:activated-counter-target-spell` | `rule:activated-counters-target-spell` |
| `rule:activated-tax-counter-unless-pays` | `rule:activated-counters-target-spell-unless-pays` |
| `rule:tax-or-counter-spell` | `rule:counters-spell-unless-pays` |

Note: those last two plus `rule:activated-counter-target-spell` are also a
near-duplicate cluster differing only in delivery — resolve together, see
CDR-05.

**Noun-side, gain `plus1-` (10)** — every one of these definitions says
+1/+1 explicitly, verified this session:

`activated-counter-transfer-from-other-creature` ·
`attack-trigger-buff-other-attacker-counters` ·
`attack-trigger-self-counter-growth` ·
`cast-trigger-self-counter-noncreature-spell` ·
`death-trigger-counter-transfer` · `draw-trigger-self-counter-growth` ·
`etb-counter-on-other-creature` · `lifegain-triggered-counter` ·
`mass-counter-distribution` · `self-counter-growth`

**Type-agnostic, gain `any-` (3)** — definitions confirm each genuinely
spans every counter type:

| from | to |
|---|---|
| `rule:doubles-counter-placement` | `rule:doubles-any-counter-placement` |
| `rule:cleanup-counters-on-leaving-battlefield` | `rule:cleanup-any-counters-on-leaving-battlefield` |
| `rule:counter-removal-as-activation-cost` | `rule:any-counter-removal-as-activation-cost` |

**Already conforming, no action (17):** 3 verb (`counters-target-spell`,
`counters-noncreature-spell`, `counters-spell-or-ability-targeting-your-permanent`)
+ 14 noun (typed or `with`-bound).

Execution is a codebook mutation and rides the walk as its own step, under
the backup law with determinism ×2 — **not executed here**, per the
ratified "no midflight renames" standing rule.
- `untaps-target-land`, `activated-untap-target-creature`,
  `activated-untap-another-permanent`, `activated-tap-target-creature`,
  tap-or-untap pair, mass-untap pair → normalize onto
  `activated-(un)tap[-or-untap]-<scope>-<class>` lattice; consolidation flag
  already ledgered (b6 D3).
- `cannot-block-restriction` vs `cant-be-*`: pick `cant` (matches oracle
  "can't") — walk item.
- `compensates-controller-with-token`, `cheat-creature-into-play`,
  `rhystic-tax`, `the-ring-tempts-you`: idiomatic job-names, EXEMPT as leaves
  (jobs are parent/display vocabulary; grammar governs mechanism slugs) —
  exemption list is Captain-ratified per slug at the walk.
- **Q6 (walk-ratification 2026-07-31):** 7 further idiomatic-leaf exemptions
  ratified, joining the 4 above: `burst-draw`, `cantrip`, `modal`,
  `drain-life`, `combat-trick-pump-own-creature`, `tribal-anthem-buff`,
  `alternate-win-condition`.

## 13. Ratification record (2026-07-30)

All five decisions ratified per recommendation, Captain-explicit:
- **D-1:** `death-trigger-` stays the family word (no `dies-` slugs).
- **D-2:** bare verb stems; `counters-` verb form retained (section 8).
- **D-3:** `-scales-with-` is the sole scaling connective; `-scaled-by-`
  retires at the walk.
- **D-4:** the §3 activation-restriction enumeration is DET-owned; SYNTH is
  banned from assigning that family.
- **D-5:** banned-token list (§10.2) and per-slug idiomatic-leaf exemption
  mechanism (§12) ratified.
Registry: log this document as a ratified ruling set; changes require the same
explicit-reversal discipline as scoring constants (D6-style logging).

## 14. Walk-ratification vocabulary batch (2026-07-31)

Applied per `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md` section 2 (Q2, Q3,
F3, Q5, F4, Q6, Q8.5); see that document for the full ruling text.

- **Q5 extended structural/descriptive vocabulary** (the ~40-most-common-token
  proposal from `docs/archive/CORPUS-PASS-WALK-RATIFICATION.md` §2.2.2, ratified as
  EXACTLY the named list — the "and similar" backlog remainder is logged to
  the final naming audit, not silently expanded here):
  `creatures`, `other`, `on`, `from`, `library`, `triggers`, `ability`, `and`,
  `by`, `prevents`, `unblockable`, `buff`, `tapped`, `restriction`, `top`,
  `targets`, `doubles`, `energy`, `forces`, `controller`, `prevent`, `into`,
  `growth`, `tribal`, `effect`, `choose`, `enters`, `cards`, `threshold`,
  `recursion`. Explicitly EXCLUDED despite corpus frequency (each has its own
  open reason, logged to the naming audit rather than silently passed):
  `scaled` (banned, D-3), `a`/`the` (banned articles, §1), `targeted` (the
  `targeted-<action>-<class>` grammar family needs a membership check first,
  §2.5 of the walk doc), `lifegain` (synonym-collision candidate against the
  ratified `gain-life` EFFECT verb, design goal #1), `attackers`, `of`,
  `outlet`.
- **F4 soft-warning tier:** `and` is ratified vocabulary (closed-vocab check
  passes) but slugs containing it get a non-blocking VALIDATOR WARNING
  ("grab-bag smell") rather than a silent clean pass — see
  `validate_slug.py`'s `warnings` field.
- **Q8.5 `cant-be-blocked` compound stem token** ratified into vocabulary
  (tokens `cant`, `be`, `blocked`) for the new `cant-be-blocked-<restriction>`
  grammar family (§2.4 of the execution handoff). The `countered` ban (§10.2)
  is unaffected — `rule:cant-be-countered` renames to `rule:spell-uncounterable`
  (Q4, §4 above) rather than sharing this stem. Closed restriction vocab:
  `by-color`, `by-power`, `except-by-count`, `as-long-as-<state>`, and
  **`by-controller`** (B1 ruling, 2026-07-31, post-execution follow-on —
  names WHO may not block, not what the blocker is like; instantiated by
  `rule:cant-be-blocked-by-controller`, seeded by The Black Gate, moved out
  of `rule:grants-unblockable-target` per the terminology law's restriction-
  rider rule).
