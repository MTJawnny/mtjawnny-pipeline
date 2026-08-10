# W4, SECOND SHAPE — THE KEYWORD GRANT (2026-08-09)

**488 gap lines closed, all `None` → `static`. Zero regressions, zero
re-routes, zero lines appeared or vanished.** The anthem's twin, taken as one
named shape. **Zero API calls. No new vocabulary** — `static` is a ratified §2
token (CR 113.3d) and this is wiring.

Predecessor: `docs/W4-ANTHEM-2026-08-09.md` (524). The method comes from
`STEP-2A-STATIC-GRANT-2026-08-05.md` and `STEP-2B-STATIC-CONDITION-2026-08-05.md`.

---

## 1. The shape

`<subject> have/has <CR 702 keyword list>` — `Creatures you control have
flying.` Same CR 113.3d statement as the anthem, same subject discipline, a
different predicate: it grants **keywords** instead of power and toughness.

**STEP-2A's shape B already claims the QUOTED grant** (`Creatures you control
have "{T}: Add one mana of any color."`), where §2 hands the quoted ability to
whatever it was granted to. **This is the UNQUOTED half** — a bare keyword,
which has no ability text to hand anywhere.

**488 lines · 480 cards · 386 distinct texts · 243 distinct subjects**, all read.

## 2. The subject is deliberately NOT restricted to permanents

`Spells you cast have cascade`, `You have hexproof` (12 lines) and `Creatures
you control have haste` (15) are equally CR 113.3d statements. What closes
CR 113.3's four-category enumeration on `static` is **the card having no
instant or sorcery face** (CR 113.3a), and that is true of all three.

Restricting the shape to "a class of permanents" would have been a claim about
the **subject**, and the recorded lesson is that **delivery is never decided by
the subject** — the `this creature …` group, where 738 of 2,185 lines turned
out to be burn spells.

## 3. "Is this a keyword?" is a MEMBERSHIP question, not a HOME question

`_granted_keywords` tests each part against **`CR_KEYWORD_NAMES`** — the list
parsed from `load_702` — plus CR 702.14a's composed landwalk, CR 702.29e's
typecycling, and each keyword's own **CR printed form** (`Ward [cost]`,
`Protection from [quality]`).

It deliberately does **not** call `_keyword_by_form`, which gates on
`KEYWORD_HOME`. That map **skips any keyword whose home could not be derived**,
so asking it *"is this a keyword?"* answers **no** for `awaken` and
`impending` — the recorded trap, where `Awaken 4—{4}{W}` was read as a flavor
word. Whether a keyword has a §2 home is a different question from whether it
**is** one, and this branch only needs the second: **the delivery of the GRANT
is `static` regardless of where the granted keyword would live on a card that
printed it bare.**

The list splitter is local (`[,;]` **or `and`**) rather than the shared
`KEYWORD_LIST_SPLIT`, because that one feeds both keyword-line paths and
widening it there would move existing routing. Adding `and` is safe *here*
because a parameter containing it — CR 702.11f's `hexproof from [A] and from
[B]` — simply fails the all-parts test and the line is left reported.

### 3a. One measured gap, costing exactly one line

`cr_printed_forms` does not derive **CR 702.11d**'s *"'Hexproof from [quality]'
is a **variant** of the hexproof ability"* — a published form in the same
family as landwalk and typecycling, stated in a sentence shape the form parser
does not read. Cost, measured: **1 line** (Tam, Mindful First-Year, which is
actually CR 702.11g's `hexproof from each of its colors`).

**Left as an honest gap rather than patched around.** Widening
`cr_printed_forms` also moves `keyword_form_tokens`, and that is its own shape
with its own diff. Logged in the code at the point of use.

## 4. Refusals, each owned by a rule

| refused | rule | n |
|---|---|--:|
| `Creatures with islandwalk can be blocked **as though** they didn't have islandwalk` | **CR 609.4** | 16 |
| `Each creature with a gold counter on it **is** a Wall … and has defender` | subject is a predicate | 1 |
| `Each creature spell you cast costs {1} less to cast **if** it has mutate` | CR 601.2f, not a grant | 1 |
| `• …` mode | **CR 700.2** | 1 |

**All 18 are genuine statics.** The token would have been RIGHT and only the
descriptor wrong — which is exactly why they are refused: *"a fallback is a
wrong answer with a ratified name."* §2 requires the descriptor to describe
what was actually printed, and "keyword grant" is false of a line that
**ignores** a keyword (CR 609.4) or **reduces a cost** (CR 601.2f).

They stay reported. CR 609.4 is a real shape and it is now a named candidate.

### 4a. THE CLAUSE GUARD IS A DECLARED HEURISTIC

`CLAUSE_NOT_SUBJECT` = `as though` · `is` · `if`.

The branch's whole claim is that group 1 is a **subject**; this tests that
claim rather than assuming it. A clause has its own finite main verb, and the
CR **anchors only one** of the three markers (609.4's `as though`). The CR
enumerates ability words and keywords; it does not enumerate English clause
markers, so **no source can hold this list** — which is the one honest reason a
heuristic may stand, and it is declared rather than hidden.

It was derived by **reading all 490 captured subjects**, it excludes exactly the
2 that are clauses, and **`are` is deliberately absent**: its only appearance is
the legitimate relative clause `creatures you control that are enchanted or
equipped`. `that's` appears in 4 legitimate subjects and contains no bare `is`.

## 5. Gate 3b — prior art says AXIS, never DELIVERY

`keyword grant` returns **22 ruling-bearing lines**. Every one is about
**codebook axis naming** — `rule:temporary-keyword-grant` (KEEP, batches 4 and
6), `rule:grants-temporary-hexproof` (MERGE). **None rules on the DELIVERY of a
keyword-grant line.** Same finding as the anthem's: this is routing, not
vocabulary.

**`tier_engine.build_granted_keyword_facts` / `extract_granted_keyword_clause`
were checked and deliberately NOT reused.** They are the T2 card-doc layer and
answer *"which keywords does this card grant?"*; this branch answers *"what is
this line's delivery slot?"*. Different layer, different question — and
`granted_keyword_facts` carries an attachment-order trap of its own that
coupling the two would drag into T3.

## 6. RESULT

| | |
|---|--:|
| gap lines closed | **488** |
| regressions (ratified → None) | **0** |
| re-routes (ratified → ratified′) | **0** |
| lines appeared / vanished | 0 / 0 |
| distinct texts · cards · subjects | 386 · 480 · 243 |
| `static` | 14,934 → **15,422** |
| unrouted delivery rows | 14,906 → **14,418** |
| `spell-or-static` bucket | 14,218 → **13,730** |
| decidably-static queue | 3,846 → **3,358** |
| `routed_lines` · `keyword_homes` | 61,960 · 151 **UNCHANGED** |

## 7. Verification

| gate | result |
|---|---|
| routing diff `--strict` | **488 moved, all `None` → `static`** |
| every moved line read | **386 distinct texts** — and reading is what found §4's 2 clause defects |
| determinism ×2 | **byte-identical** |
| Gate 2 (12 checks) | **green** — 11 pass, family_sweep's standing 6 excused |
| conservation · visibility · ground truth · gate audit | pass, baselines unmoved |
| `recorded_numbers --strict` | pass |
| `build_keyword_homes` | **151 → 151** — this branch reads keyword text, so the map was the first thing checked |
| Gate 3b prior art | 22 ruling-bearing lines, **all axis-naming**; 1 code artifact, this branch itself |

## 8. A correction to the anthem record

`W4-ANTHEM-2026-08-09.md` §9 predicted *"Criminal Past lives here."* **It does
not.** Its line is

> `Commander creatures you own have menace and "This creature gets +X/+0, where
> X is the number of creature cards in your graveyard."`

a **mixed** grant — one bare keyword and one quoted ability — so the granted
text is not entirely keywords and this shape correctly declines it. It is a
**STEP-2A shape B miss**: shape B claims the quoted grant and does not claim
this one. That is a real, separate finding and it belongs to shape B, not here.

A prediction about a population is a hypothesis about it, not a measurement of
it — the same lesson as sizing a ratification by a slug prefix.

## 9. What remains of W4

**3,358 decidably-static lines.** Two shapes have now taken 1,012 of them.
Ranked from `--gaps`:

| shape | ~lines | note |
|---|--:|---|
| `<class>/<spell> cost(s) {N} less` | ~498 | **CR 601.2f**. Pollywog Symbiote is already waiting in the refusals. |
| `<class> can't …` | ~336 | CR 113.3d restrictions |
| `you may cast / you may play` | ~160 | CR 118.5 permission statics |
| `<subject> have no …` / `have base P/T` | ~48 | CR 613.4 characteristic-setting; the `have` residual this shape declined |
| CR 609.4 `as though` | ~16+ | named by this pass's refusals |
| `during your turn, …` | ~92 | a comma-subject shape both W4 branches decline by construction |

The method is unchanged: **name a shape, measure it, read its output, tighten
until the leakage is zero or explained — then take the next shape.** This pass
needed two tightenings, both visible only in the output: the CR 609.4 class
(16 lines) and the two-line clause guard.
