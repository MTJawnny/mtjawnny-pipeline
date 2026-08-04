# CR-LAW AUDIT — WHAT IS READ FROM THE CR, AND WHAT IS STILL INFERRED (2026-08-05)

**Captain's criterion:** *"check for other things that might be being derived
rather than cold fact from the CR. Derived should be reserved for the parent
tags only. I believe. I think everything else is law correct?"*

**The criterion is right, and the codebase did not meet it.** Two lists that the
CR enumerates outright were being reconstructed from data. Both are now parsed.
**Zero lines moved by either fix** — this is completeness and correctness, and
neither would ever have shown up in a routing diff.

A note on the word, because this project uses it in two senses. **DERIVED** is
the good thing when it means *"parsed from the CR at run time"* (CLAUDE.md's
locked rule) and the structural thing when it means *"a parent is the union of
its children"*. Captain's sense here is the third: **inferred, harvested or
guessed**. Under that reading the criterion holds — parents are the only place
inference is legitimate.

---

## 1. FIXED — CR 205.3g–q enumerates every subtype list

**The claim I wrote yesterday was false.** `build_self_noun_rx`'s comment read:

> *"CR 205.3b makes these open and set-specific … and the CR does not enumerate
> them in one place, so the corpus harvest is legitimate here."*

CR 205.3 enumerates **ten** subtype lists, in one uniform sentence shape, and
**CR 205.3r closes the set** by naming the four card types that have none:

| rule | list | n |
|---|---|--:|
| 205.3g | artifact types | 22 |
| 205.3h | enchantment types | 13 |
| 205.3i | land types | 17 |
| 205.3j | planeswalker types | 80 |
| 205.3k | spell types | 5 |
| 205.3m | creature types (+ the one two-word type, `Time Lord`) | 323 + 1 |
| 205.3n | planar types | 82 |
| 205.3p | dungeon types | 1 |
| 205.3q | battle types | 1 |
| **205.3r** | *"Phenomenon, scheme, vanguard and conspiracy cards have no subtypes"* | — |

`type_vocabulary()` now parses all ten. The self-reference noun set went **448 →
568**, and the corpus is no longer a source at all.

**Same error as the card-type gap, one level down.** A harvest can only hold what
the gated corpus holds, and this project's gate drops whole layouts.

### 1a. The corpus is now a TEST, not a source

The scan of printed type lines is kept and inverted: any subtype a card prints
that CR 205.3 does not list **halts the run**. It fired on its first execution
and found three real things.

## 2. FOUND BY THAT GUARD — the CR and Scryfall disagree on the apostrophe

**The CR prints a curly apostrophe (U+2019); Scryfall type lines print a straight
one (U+0027).** So CR 205.3i's `Urza’s` never equals a printed `Urza's`, and the
same mismatch hits `C’tan`, `Shi’ar`, `Serra’s Realm`, `Bolas’s Meditation
Realm`, `Outside Mutter’s Spiral`.

**Consequence beyond this file:** CR 702.14a's landwalk template composes over CR
205.3i's land types, so it has been carrying `urza’s` and could never have
matched a printed `Urza'swalk`. `type_vocabulary` now emits both forms — a
mechanical transformation of a CR-parsed value, not a hand-added member.

## 3. FOUND BY THAT GUARD — the local CR snapshot is BEHIND the corpus

**`Chorus` is a spell type the corpus prints and the local CR does not list.**
CR 205.3k enumerates five spell types (Adventure, Arcane, Lesson, Omen, Trap);
the corpus prints `Instant — Chorus` (Hymn to the Ages) and `Sorcery — Chorus`
(Colossal Chorus).

**This is a Captain item: `docs/mtg-comprehensive-rules.md` needs refreshing.**
Until then it sits in a dated **CR-LAG REGISTER** — not a hand-list of
vocabulary, but a record of a discrepancy between two upstream sources, with its
evidence named. Anything printed that is in neither CR 205.3 nor the register
still halts, so the register cannot quietly absorb a parse regression.

**The wider point: the CR is the only non-mirror this project has** (2026-08-01
handoff §3), and it is a *vendored snapshot*. Nothing until now measured whether
it was current.

## 4. THE REGISTER — every list in the classifier, and its standing

### 4a. Law-correct: parsed from the CR at run time

| what | CR authority |
|---|---|
| §2 DELIVERY vocabulary | grammar §2's table, parsed to the first `###` |
| ability CLASSES | CR 113.3a–d (`CLASS_RULE`) |
| card types · supertypes · **all ten subtype lists** | CR 205.2a · 205.4a · **205.3g–q** |
| landwalk template | CR 702.14a's grammar over CR 205's type lists |
| keyword homes | CR 702.Na's stated class (§2b), amended by §2e |
| keyword printed forms | CR 702 sub-rule text, four sentence shapes (D4) |
| trigger verbs | CR 701 keyword-action list (`build_trigger_verbs`) |
| activated cost head | CR 113.3b's `[Cost]: [Effect]` **structure**, not a verb list (D6) |
| replacement templates | CR 614.1a–**d** (614.1d added 2026-08-05) |
| loyalty cost | CR 606.2's printed symbol |
| token types | CR 111.10 |

### 4b. Ratified vocabulary, complete against its CR enumeration

| family | CR closed list | standing |
|---|---|---|
| `is-dealt-damage-trigger` recipients | CR 120.1 — battles, creatures, planeswalkers, players | **all four**; `battle` reserved at 0 |
| `is-attacked-trigger` objects | CR 506.3 — player, planeswalker, battle | **all three**; `battle` reserved at 0 |
| turn structure | CR 502–513 | closed end to end |
| attachment | CR 301.5a · 301.6 · 303.4 | **all three** as of 2026-08-05 (Fortification) |

### 4c. INCOMPLETE against a CR enumeration — reported, needs Captain

| gap | CR | measured |
|---|---|--:|
| **`combat-damage-to-*` / `any-damage-to-*` cover 2 of CR 120.1's 4 recipients** | 120.1 | planeswalker **2 lines** (Zagras unrouted) · battle **0** |
| **`to-graveyard-from-*` names 6 of CR 400.1's 7 zones** | 400.1 | `command` **0 lines** · `ante` **0 lines** (legacy) |

Both are **new vocabulary**, so both go to the decision sheet rather than being
minted. The damage one is the sharper finding: the **recipient** side of that
family was ratified against CR 120.1's full enumeration on 2026-08-04, and the
**source** side never was. One half of a family enumerated from a closed CR list,
the other half not.

### 4d. HEURISTIC with no closed CR list behind it — declared, not hidden

These are the honest residue. Each is a judgement the CR does not enumerate, and
naming them is the point of this section.

| heuristic | where | why no CR list exists |
|---|---|---|
| duration/target disqualifiers — `until` · `target` · `perpetually` · `this turn` | the static-grant branch | CR 611.2a says only *"such as 'until end of turn'"*; there is no closed list of durations. The **justification** is CR 113.3d ("continuously true"), but the marker words are chosen, not enumerated. `perpetually` is an Alchemy term with no CR entry at all. |
| compound-trigger `PREDICATE` verbs — `enters` · `attacks` · `dies` · `leaves` · `becomes` · `blocks` · `is`/`are`/`deals` | `deliveries_for_lines` clause splitting | these are game EVENTS (CR 506, 603.2, 700.4), and the CR publishes no closed list of trigger events — only of keyword *actions* (CR 701), which `build_trigger_verbs` already parses |
| determiner alternations — `(a \| their \| your \| its owner's)` | zone/graveyard branches | grammar, not vocabulary |

### 4e. CHECKED AND CLEARED

| checked | verdict |
|---|---|
| `\ba creature\b` in the §2a subject test | **not a defect** — exact defect condition measured at 5 lines, all correctly routed; 3 are `cast-trigger`, which uses `mark()` and never consults the subject prefix |
| `attacks a battle` (CR 506.3) | **not a defect** — both lines are the *attacking* side and route to `attack-trigger` correctly |
| Dreadhound, *"dies **or** … put into a graveyard from a library"* | **not a defect** — a compound trigger, reported under `to-graveyard-from-nonbattlefield` rather than guessed; §1 says compounds earn multiple tags |

## 5. VERIFICATION

| gate | result |
|---|---|
| routing diff `--strict` (CR 205.3 subtype parse) | **0 lines moved**, 0 appeared, 0 vanished |
| self-reference noun set | 448 → **568**; all CR 205.2a card types and all CR 205.3 subtypes covered |
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — the known Storm of Memories artifact |
| Clue/investigate ground truth | **byte-identical** |
| `routed_lines` · `keyword_homes` | 61,907 · 150 **UNCHANGED** |
| lint · family sweep · drift | clean · 6 blocking, the same 6 · 35 unchanged |

## 6. THE ANSWER TO THE QUESTION

**"Is everything else law correct?"** — It is now, with three declared
exceptions and two reported gaps:

- **Two lists were not**, and both were CR-enumerated: card types (yesterday) and
  all ten subtype lists (today). Both fixed by parsing.
- **Two families are incomplete against a closed CR enumeration** (CR 120.1
  damage recipients on the source side, CR 400.1 zones) and need vocabulary, so
  they are on the decision sheet, not minted.
- **Three heuristics remain** (§4d) where the CR genuinely publishes no closed
  list. They are declared rather than dressed up as derivations.

**The general lesson is the one Captain's question encodes.** "Derived" is only
safe when the derivation's SOURCE can contain every member the rule needs. A
corpus harvest looks like a derivation and behaves like a hand-list, because the
gate decides its contents. **Ask what the source cannot contain.**
