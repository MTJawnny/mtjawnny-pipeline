# CONCEPT AXES — WHERE DO THE 59 ACTUALLY BELONG?

**Measurement + proposed homes. 2026-08-09. Nothing ratified, nothing mutated.**

`foundry_slug_reparse.py` found that **43.8% of codebook membership sits on
axes whose name does not decompose into §1's slot grammar** at all. Captain's
instruction was the right one:

> *"Re-read them and build out either new homes or figure out if they belong in
> a current home."*

Answer: **most of them already have a home.** Only two families genuinely need
a new one, and one of those is large and coherent enough to be obvious in
hindsight.

| | axes | members |
|---|--:|--:|
| tail NOT typed at all (the population) | 59 | 3,472 |
| …**already have a home** | 45 | **2,551** |
| …need a **new** home | 11 | 762 |
| …genuinely idiomatic, keep as-is | 3 | 159 |

---

## GROUP A — 7 axes that ARE compositional and just break §4 (57 members)

These have a valid §2 DELIVERY head. Only the tail is off-standard, and §4
already ratifies the correct verb. **This is design goal #1 — two names for one
mechanic — not a missing home.**

| axis | n | the tail says | §4 already ratifies |
|---|--:|---|---|
| `rule:death-trigger-token-creation` | 21 | `token-creation` | **`create-token`** — and §4 says outright *"All `creates-` slugs normalize at the walk"* |
| `rule:combat-damage-to-player-draws-card` | 5 | `draws-card` | **`draw`** — §4's rule is the bare verb stem |
| `rule:etb-modal-choice` | 22 | `modal-choice` | CR 700.2 `modal` (see Group D) |
| `rule:landfall-produces-mana` | 4 | `produces-mana` | no mana verb in §4 — **real gap** |
| `rule:etb-shuffle-graveyard-cards-into-library` | 2 | phrase | §4 has no shuffle verb — **real gap** |
| `rule:attack-trigger-tribal-anthem-attackers` | 2 | phrase | see Group E |
| `rule:combat-damage-to-player-free-cast` | 1 | `free-cast` | see Group F |

**Home: existing.** Three are pure renames onto ratified §4 verbs. Two expose a
genuine §4 gap (a mana verb, a shuffle verb).

---

## GROUP B — the ENTERS-TAPPED family already has a DELIVERY (1,073 members)

| axis | n |
|---|--:|
| `rule:enters-tapped` | 686 |
| `rule:created-token-enters-tapped` | 195 |
| `rule:enters-tapped-conditional` | 168 |
| `rule:imposes-enters-tapped` | 24 |

Its own definition names the mechanism: *"The permanent enters the battlefield
tapped."* That is **CR 614.1c**, a replacement effect — and §2 **already
ratifies `replacement`** as a DELIVERY token. Measured: `replacement` is the
second-commonest delivery across these member cards (395).

**Home: existing.** `replacement` DELIVERY + an `enters-tapped` EFFECT. The
effect verb is the only thing missing, and `conditional` is already a ratified
§1 QUALIFIER. This is the single largest block in the whole population and it
needs no new slot at all.

> **Do not fold `created-token-enters-tapped` in.** The subject is a *created
> token*, not the source permanent — that is a §2a subject distinction, and
> collapsing it would assert a token-maker and a tapped-land are one mechanism.

---

## GROUP C — 2 axes that are CR keywords (145 members)

| axis | n | rule |
|---|--:|---|
| `rule:typecycling` | 91 | CR 702.29e/f — a *variant family*, not a bare keyword |
| `rule:the-ring-tempts-you` | 54 | CR 701.54 — a keyword **action** |

Neither is in `CR_KEYWORD_NAMES`, which is why the reparse missed them —
`typecycling` is printed per-instance (`plainscycling`, `basic landcycling`)
and `the ring tempts you` is CR 701, not CR 702. **`foundry_ground_truth.py`
already solved exactly this** with its `VARIANT_FAMILIES` predicate map.

**Home: existing.** The CR-keyword home, once membership is tested against the
variant predicate rather than string equality. Same defect, same cure, already
written down once.

---

## GROUP D — NEW HOME #1: **RESTRICTION** (8 axes, 896 members)

The largest genuinely-missing slot, and it is coherent. Every one of these says
*"you may not, or only under condition X"* — a **limit on when or how**, which
is neither a DELIVERY (how it happens) nor an EFFECT (what it does).

| axis | n | CR |
|---|--:|---|
| `rule:activation-restricted-to-sorcery-speed` | 565 | **602.5d** |
| `rule:restricted-purpose-mana` | 217 | 106.6 |
| `rule:activation-restricted-only-during-your-turn` | 77 | 602.5 |
| `rule:cannot-block-restriction` | 21 | 509.1a |
| `rule:activation-restricted-during-combat` | 7 | 602.5 |
| `rule:conditional-attack-restriction` | 5 | 508.1a |
| `rule:restricts-library-search` | 3 | 701.19 |
| `rule:limits-card-draws` | 1 | 121.1 |

**The CR supports the slot directly.** CR 602.5d is the rule *"Activate only as
a sorcery"* is printed from. The three `activation-restricted-*` axes are one
parameterized family (`activation-restricted-<when>`), which is §11's grammar-
slot pattern exactly.

**Why it is not a QUALIFIER:** §1's QUALIFIER slot is a closed list of
modifiers on an effect (`-conditional`, `delayed`, `-mass`). A restriction is
not a modifier on the effect — it is a constraint on the *ability's legality*,
and 896 members is not a modifier-sized population.

**This needs Captain.** A new §1 slot is new vocabulary.

---

## GROUP E — NEW HOME #2: **STATIC COMBAT PROPERTY** (5 axes, 384 members)

| axis | n |
|---|--:|
| `rule:grants-unblockable` | 185 |
| `rule:innate-unblockable` | 183 |
| `rule:conditional-first-strike-your-turn` | 9 |
| `rule:evasion-vs-low-power-blockers` | 4 |
| `rule:evasion-vs-high-power-blockers` | 3 |

`rule:innate-unblockable` delivers `static` on **183 of 183** members — a clean
1:1, which is the positive test that it really is a static property and not a
mis-shelved trigger.

**The `innate-` / `grants-` split is already correct and must be kept.** §2's
created-ability rule says a card does not deliver an ability it grants to
something else; these two axes encode exactly that boundary and are the same
distinction `keyword_line_tokens` draws for printed-vs-granted keywords.

---

## GROUP F — 3 axes that are DECK VERNACULAR, and should stay (159 members)

| axis | n | why it stays |
|---|--:|---|
| `rule:modal` | 111 | CR 700.2 names the concept; it is a property of the ability, not a delivery |
| `rule:cantrip` | 31 | pure player vernacular, no CR term, universally understood |
| `rule:rhystic-tax` | 24 | named after Rhystic Study; no CR term exists |

**These are the honest case for a concept axis.** CLAUDE.md already licenses
exactly one reason a non-CR shape may stand — *"a list the CR declares
un-enumerable"* — and player vernacular for a real deck-building pattern is the
same argument: the CR does not name it, and the players do.

---

## THE RESIDUAL — 34 axes, ~1,800 members, not yet homed

Named honestly rather than forced into a bucket. They cluster, but each cluster
needs its own read before it earns a home:

- **zone-movement recursion** — `graveyard-to-hand-recursion` (46),
  `graveyard-to-library-top-recursion` (8), `graveyard-to-library-shuffle-in`
  (6), `leaves-battlefield-returns-exiled-card` (3).
  > **`graveyard-to-hand-recursion` should be checked against §4's ratified
  > `regrowth`** (*"graveyard → hand, ratified b5 vocab"*). Not caught by the
  > collision checker below — that only catches rearrangements of the SAME
  > words, and this is a different phrase for the same mechanic, which no
  > derivation can see. It needs a read.
- **library access** — `library-top-visibility` (23), `cast-from-top-of-library`
  (14), `library-dig-to-hand` (11), `library-dig-put-onto-battlefield` (10).
- **anthems / stat setting** — `tribal-anthem-buff` (63),
  `sets-base-power-or-toughness` (18), `conditional-buff-by-color` (12).
- **extra turns and phases** — `grants-extra-turn` (55),
  `grants-additional-combat-phase` (44).
- **temporary effects** — `temporary-control-theft` (42),
  `temporary-keyword-grant` (41).
- **singletons** — `prevents-regeneration` (152), `fixed-lifegain` (58),
  `forced-hand-reveal` (23), `alternate-win-condition` (16) + `alt-win-empty-library`
  (3), `life-total-reset` (8), `symmetric-hand-refill` (9), and others.
  > **`fixed-lifegain` (58) is probably §4's `gain-life` plus a `fixed`
  > qualifier**, not a concept — same duplication shape as `regrowth`.

---

## WHAT THIS CHANGES ABOUT THE ARCHITECTURE ANSWER

The earlier read — *"the codebook holds two kinds of axis and §1 only models
one"* — was **half right and overstated the problem.**

- **2,551 of 3,472 members already have a home.** They read as unparseable
  because the slug uses a non-§4 verb form, a CR-variant keyword, or omits a
  DELIVERY that its own definition names. That is *naming drift*, not a second
  ontology.
- **Only 762 members need genuinely new structure**, and they fall into two
  clean families with CR anchors: RESTRICTION (896 incl. overlap) and STATIC
  COMBAT PROPERTY (384).
- **159 members are honest concept axes** and should never be forced into slots.

So the fact-table plan holds, and it is cheaper than it looked: **one new slot
(RESTRICTION), one property table (static combat properties), and a normalization
pass over §4 verb forms.**

---

## WHAT NEEDS CAPTAIN

1. **A RESTRICTION slot in §1** — 896 members, CR 602.5d anchored. New
   vocabulary, so it is a ratification.
2. **An `enters-tapped` EFFECT verb** — unlocks 1,073 members onto the existing
   `replacement` DELIVERY with no new slot.
3. **Two §4 gaps** — a mana verb and a shuffle verb.

## WHAT DOES NOT NEED CAPTAIN (DET work, proceeds unasked)

4. ✅ **DONE — `experiments/foundry_synonym_collision.py`.** Measured, and it
   is bigger than one axis. §4's premise is *"one verb per mechanic, chosen
   once, used everywhere"*, and §14 Q5 already RULED `lifegain` out by name
   against the ratified `gain-life`. **Both rulings existed; nothing enforced
   either.**

   | kind | axes | members | status |
   |---|--:|--:|---|
   | **REORDERED** (`token-creation`, `life-loss`) | 5 | 40 | collision on §4's stated order |
   | **CONCATENATED** (`lifegain`) | 9 | 74 | **§14 Q5 already ruled these out** |
   | **INFLECTED** (`created-token`, `gains-life`) | 3 | 300 | **needs a READ, not a rename** |

   **The 300 are reported separately on purpose.** `rule:created-token-enters-tapped`
   (195) and `rule:grants-haste-to-created-tokens` (102) use `created-token` as
   a **SUBJECT** — *"a token that was created"* — not as §4's verb. Lumping
   them would have produced a headline of 414 that nobody should act on. The
   actionable, already-ruled population is **14 axes / 114 members**.

   The checker DERIVES the collision (a ratified multi-word verb defines a stem
   set; any run carrying those stems rearranged is the same mechanic) rather
   than hand-listing synonyms — and it caught its own first defect via
   `foundry_probe.must_capture`: exact stem equality mapped `creation`→`cre`
   but `create`→`create`, so `token-creation` did **not** collide with
   `create-token`, and the checker returned clean for the exact case §4 names
   in its own text.
5. Teach the reparse the CR-variant keyword predicate so `typecycling` and
   `the-ring-tempts-you` stop reading as unhomed.
6. Normalize the three Group A tails onto their existing §4 verbs.
