# THE ABILITY-WORD STRIP IS A CR ENUMERATION — CR 207.2c / 207.2d (2026-08-06)

**Status: DET fix, no vocabulary, no codebook mutation. Not load-bearing until
ratified, but nothing here proposes a token.**

Closes `AUDIT-5-2026-08-05.md` **FINDING 4**, and closes it differently from the
way the audit proposed.

---

## 1. What the audit proposed, and why it was the wrong shape of fix

AUDIT-5 said: *"widen `ABILITY_WORD` to the printed shape."* That treats the
problem as a character class that is too narrow. It is not. **CR 207.2c
publishes the ability words as a CLOSED LIST**, in one sentence:

> **CR 207.2c** — *"An ability word appears in italics at the beginning of some
> abilities. … The ability words are adamant, addendum, alliance, battalion,
> bloodrush, celebration, channel, chroma, cohort, constellation, converge,
> council's dilemma, coven, delirium, **descend 4, descend 8**, disappear,
> domain, eerie, eminence, enrage, fateful hour, fathomless descent, ferocious,
> flurry, formidable, grandeur, hellbent, heroic, imprint, infusion, inspired,
> join forces, kinship, landfall, lieutenant, magecraft, metalcraft, morbid,
> opus, pack tactics, paradox, parley, radiance, raid, rally, renew, repartee,
> revolt, secret council, spell mastery, strive, survival, sweep, tempting
> offer, threshold, undergrowth, valiant, vivid, void, and will of the
> council."*

**61 members, parsed at run time.** The locked rule applies verbatim — *NEVER
TRANSCRIBE THE CR, DERIVE FROM IT AT RUN TIME* — and it is once again
predictive: the two members a shape test could never express are exactly the two
that were failing. `descend 4` and `descend 8` carry a **digit**;
`council's dilemma` carries the CR's **curly apostrophe**.

A widened character class would have caught `Descend 4` by accident. The CR
list catches it **because the CR says so**, and it catches the next digit-
bearing ability word Wizards prints without another session measuring anything.

## 2. Why a shape still exists — and why that is legitimate

**CR 207.2d** is the other half, and it is the rule that licenses a heuristic:

> *"Similar to ability words, **flavor words** appear in italics at the
> beginning of some abilities. … they have no special rules meaning and **are
> not listed in the Comprehensive Rules**. While an ability word ties together
> several abilities with similar functionality, **each flavor word is tailored
> to the specific ability it appears with**."*

The system map asks one question: *"Where does this list come from, and can that
source contain every member the CR names?"* For flavor words the CR answers it
directly — **no source can hold them, by rule.** That is the only honest reason
a shape may stand where a list would be preferred, and it is now DECLARED as
such rather than sitting in the map as an open defect.

The residual shape rejected every flavor word carrying a digit (`Nitro-9 —`),
terminal punctuation (`No One Dies! —`, `Exterminate! —`, `I. AM. TALKING! —`),
a comma (`In You, All Things Are Possible —`), an ellipsis (`... Catch —`) or a
non-ASCII letter (`Pavitr's Sevā —`). It now accepts them.

## 3. The refusals — six constructs, six rules, no judgement

The old test decided membership with characters. The new one decides it with
rules: an em-dash phrase opening a line is exactly one of **six** things, five
of which carry rules meaning and **must not** be stripped.

| printed | rule | worked case |
|---|---|---|
| Saga chapter bar | **CR 714.2** | `III —`, `II, IV —` |
| die-roll result row | **CR 706.3b** | `5 —`, `4 or 5 —`, `1 \| Trapped! —` |
| modal header | **CR 700.2** | `When Kura dies, choose one —` |
| a cost | **CR 601.2b** | `Prototype {1}{B} —`, `+ {R} —` |
| an activated ability's cost | **CR 602.1** | `Sacrifice another Serpent: Choose one —` |
| a keyword's own parameter | **CR 702.Na** | `Awaken 4—{4}{W}`, `Impending 5—{1}{B}` |
| **ability word** | **CR 207.2c** | `Descend 4 —`, `Landfall —` |
| **flavor word** | **CR 207.2d** | `Nitro-9 —`, `No One Dies! —` |

### 3a. The keyword refusal is deliberately NARROW

A CR 702 keyword whose parameter is an **ability** — `Max speed — [Ability]`
(CR 702.178a), `Visit —` (702.159a), `Forecast —` (702.57a) — stays
**strippable on purpose**. `build_keyword_forms` refuses those forms precisely
so the INNER ability reaches its own branch (the standing trap: *"matching the
wrapper overwrites the inner ability's correct delivery"*), and removing the
wrapper is how it gets there. Only a keyword with a **numeric** parameter is
refused, because there the text after the dash is a cost and there is no inner
ability to reach.

### 3b. `KEYWORD_HOME` is not the keyword list — a new trap

The first cut asked `KEYWORD_HOME` *"is this a keyword?"* and it answered **no**
for `awaken` and `impending`: `build_keyword_homes` **skips** a keyword whose
home cannot be derived, so the home map is a strict subset of CR 702's names.
`Awaken 4—{4}{W}` was consequently read as a flavor word. **A membership test
must use the membership list**, not a map that happens to be keyed on it. Fixed
by parsing `CR_KEYWORD_NAMES` from `load_702` directly, with its own halt-guard.

This is the same shape as *"a ratified token with no emitter"* and *"a ratified
standard with no caller"*: a derived structure standing in for the thing it was
derived from, minus whatever the derivation dropped.

## 4. The halt-guard asserts CONTENT

Per the CR 205 Oxford-comma lesson (*a count cannot see a substitution*), the
guard names members, not a length — and each probe fails a **different** way the
parse can break:

| probe | the failure it catches |
|---|---|
| `landfall`, `threshold` | the ordinary case |
| `will of the council` | the **last** member, which an Oxford split drops |
| `descend 4`, `descend 8` | the **digit** members that motivated this parse |
| `council's dilemma` | the CR's **curly** apostrophe vs Scryfall's straight one |

**Negative-tested, 2026-08-06.** All four halt; the unmodified CR does not:

```
wording changed .................. halted
last member dropped .............. halted   missing=['will of the council']
digit members dropped ............ halted   missing=['descend 4', 'descend 8']
apostrophe member changed ........ halted   missing=["council's dilemma"]
unmodified CR .................... no halt  (61 words)
```

## 5. The local hack is gone

`linked_abilities` carried its **own** looser dash-strip, added 2026-08-05 with
the note *"widening ABILITY_WORD globally would touch every classifier, so the
looser dash-strip is local to this gate."* AUDIT-5 named that for what it was —
*"I fixed the symptom there and left the cause standing"*. There is now **one**
strip, called from all three sites, so the two cannot drift apart.

## 6. Measured result

Baseline `p19-abilityword-before.json` → `p19-abilityword-after.json`.

| | |
|---|--:|
| strip decisions changed | **780** lines / 39 prefixes |
| ...newly **stripped** (was kept) | **41** — every one a CR 207.2c or 207.2d word |
| ...newly **kept** (was stripped) | **739** — 415 modal headers (CR 700.2), 324 Saga chapters (CR 714.2) |
| **routing changes** | **29**, every one `None → ratified` |
| **re-routes** (ratified → different ratified) | **0** |
| lines appeared / vanished | **0 / 0** |
| unrouted | 16,273 → **16,244** |
| deliveries emitted | 61,945 → **61,946** |
| keyword homes | **150 → 150, unchanged** |
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — Storm of Memories, the known harness artifact |
| Clue/investigate ground truth | **unmoved** (no moved line carries `investigate`) |

### 6a. The 739 newly-KEPT lines moved NOTHING, and that was predicted

Both populations were being stripped **wrongly** and both were saved by branch
order, not by the strip:

- **Saga chapters** — `parse_delivery` tests `CHAPTER` *before* the strip, so
  `III —` reached `chapter-trigger` either way.
- **Modal headers** — `Choose one —` stripped to the empty string and landed in
  `spell-or-static`; unstripped it lands there too, and `_MODAL_HEADER_RE` reads
  the **raw** line in `deliveries_for_lines`, so mode inheritance never depended
  on the strip.

Zero movement here is the **correct** result and it is a structural one: the old
behaviour was wrong in a place where nothing downstream could observe it. It is
now right for a stated reason.

### 6b. Why 29 moved and not AUDIT-5's 121

AUDIT-5's **121** counted *lines whose prefix the shape could not strip* — the
population, not the yield. **41** of those are genuine ability/flavor words
(the rest are the six refused constructs above), and of those 41, **29** change
routing. The remaining **12** were already correctly routed: they are activated
abilities (`GOOOOAAAALLL! — {T}, Sacrifice this artifact: Draw two cards.`),
and `parse_delivery`'s `":" in body` test saw the colon whether or not the
prefix was stripped.

**Stating the boundary, per Gate 4:** 121 is the count of unstrippable prefixes;
41 is the count that *should* strip; 29 is the count whose delivery changes.
Three different questions, three different numbers, and only the last is a
routing claim.

### 6c. The moved lines, by family

| n | to | representative |
|--:|---|---|
| 8 | `static` | `Descend 4 — As long as there are four or more permanent cards in your graveyard, …` |
| 6 | `attack-trigger` | `Nitro-9 — Whenever Ace attacks, …` · `10,000 Needles — Whenever this creature attacks, …` |
| 5 | `etb` | `Exterminate! — When this creature enters, …` |
| 2 | `cast-trigger` | `Pavitr's Sevā — Whenever you cast a creature spell, …` |
| 2 | `begin-combat-trigger` | `... Catch — At the beginning of combat on your turn, …` |
| 1 | `upkeep-trigger` | `Descend 8 — At the beginning of your upkeep, …` |
| 1 | `player-attack-trigger` | `Allons-y! — Whenever you attack, …` |
| 1 | `combat-damage-to-player` | `I. AM. TALKING! — Whenever The Eleventh Doctor deals combat damage to a player, …` |
| 1 | `any-etb` | `Avalanche! — Whenever an Equipment you control enters, …` |
| 1 | `any-attack-trigger` | `In You, All Things Are Possible — Whenever one or more artifact creatures you control attack, …` |
| 1 | `etb` + `attack-trigger` | `Do You Like Squirrels? — Whenever … enters or attacks, …` — **the +1 row**, a CR 113.3c compound trigger now reachable, two deliveries by grammar §1 |

All 29 read and confirmed.

## 7. What this leaves open in stage 2

`PREDICATE` — the compound-trigger split's verb list — is now the **last
hand-written list in stage 2**. It is not the same case as this one: the CR
enumerates keyword **actions** (701), and a trigger's event is a game **EVENT**,
which the CR does not publish as a closed list. That makes it a candidate for
the CR 207.2d treatment (declare it un-enumerable and say why) **or** a real
defect — and the honest answer is that **nobody has measured its recall yet**.
That measurement is the next stage-2 item, and it is a recall inversion, not a
census: a missing predicate verb looks exactly like a shape that does not exist.
