# D4 — PARAMETERIZED KEYWORD LINES, DERIVED FROM THE CR (2026-08-04)

**528 gap lines closed. Zero lines moved off a ratified token.** Second item of
the 2026-08-04 EVE work order, worked after the 14 §2 rows were ratified.
**Zero API calls.**

Gate 3b prior art (`keyword parameter`, `ward`, `equip`): 20 ruling-bearing
lines, all read. The two that govern are
`DELIVERY-VOCABULARY-BATCH-2026-08-03.md` §6 (*"Ward alone is 206 — and Ward is
already served"*) and the EVE handoff's §2b router record (Equip 567). **Both
are about the BARE forms, which were already routed.** D4 is only the remainder
whose parameter is typed or a clause.

---

## 1. The defect

`keyword_line_tokens` recognised a keyword only after `COST_OR_PARAM` stripped
its parameters — and that pattern strips **mana symbols and bare digits only**.
Every keyword taking a **typed** or **clause** parameter was therefore invisible:

| printed | why it was missed |
|---|---|
| `Ward—Pay 3 life.` | the cost is a clause, not a symbol |
| `Equip Knight {1}` | a type word sits between the name and the cost |
| `Craft with artifact {2}{W}` | ditto |
| `Champion a Kithkin` | the parameter is an object, and there is no cost |
| `Cumulative upkeep {W} or {U}` | the cost is a *choice* of symbol runs |

## 2. The derivation — and why a hand-list would have failed FOUR times

The locked rule (`ed252a6`) applies: **the CR publishes each keyword's printed
form, so parse it.** What made this non-trivial is that the CR states that form
in **four different sentence shapes**, and each one is load-bearing:

| shape | rule | example | cost of missing it |
|---|---|---|---|
| **QUOTED** | 702.6a | `"Equip [cost]" means …` | — |
| **UNQUOTED** | 702.21a | `Ward [cost] means …` | **all 53 Ward lines** — the single biggest keyword in D4 |
| **WRITTEN** | 702.57a · 702.167a | `It's written "Forecast — [Activated ability]."` · `It is written as "Craft with [materials] [cost],"` | **all 24 Craft lines** |
| **IN-FORM** | 702.6c | `restrictions … appear in the form "Equip [quality]" or "Equip [quality] creature."` | **18 of Equip's 33** |

A quote-and-`means` parser — the obvious one, and the one the handoff's own
sketch implies — returns **146** keywords and loses Ward entirely. Parsing all
four shapes returns **159**.

**One composition is derived rather than read.** CR 702.6c states Equip's
restriction form *without* the cost, but 702.6a's cost is still part of the
ability and every printed card carries both. `[quality]` + `[cost]` is the
composition of the two rules, not a guess.

**Safety filter, load-bearing:** a captured form counts only if it **begins with
the keyword's own name**. Without it, 702.29c's `"When you cycle this card"
means …` becomes a printed form of Cycling, which it is not.

## 3. Four measured defects in my own matcher, each caught before it landed

**This is the part worth keeping.** Every one was found by measurement, not review.

| # | defect | how it showed | fix |
|---|---|---|---|
| 1 | `\d` inside a `re.sub` **replacement** string is a group escape | every one of the 159 forms failed to compile — loud, not silent | replace via a lambda. Same family as the recorded `re.escape`-before-substitution trap |
| 2 | `\s*` between a keyword name and a non-cost placeholder | **`Equipped Warriors you control have double strike.`** matched `Equip [quality]` — a static routed to `activated` | `\s+` everywhere except before a `[cost]`, where the long dash may replace the space |
| 3 | splitting on commas **before** matching | `Ward—{2}, Pay 2 life.` and `Craft with a Dinosaur, a Merfolk, a Pirate, and a Vampire {4}` were destroyed before they were tested | **whole line first**, comma-split as the fallback |
| 4 | a cost clause crossing a **sentence** boundary | `Equip—Sacrifice another nonland permanent. Activate only once each turn.` matched while its symbol twin `Equip {0}. Activate only once each turn.` did not — one shape decided two ways by which arm happened to match | a period is allowed only as the clause's final character |

### 3a. The fifth, and the only one that reached a routing diff

`"Max speed — [Ability]"` (**CR 702.178a**) has a **whole ability** as its
parameter, and `[Ability]` swallowed it:

| card | was | became |
|---|---|---|
| Pride of the Road | `begin-combat-trigger` | `static` |
| Vnwxt, Verbose Host | `replacement` | `static` |

**Both were correct before and wrong after.** CR 702.178a reads *"'Max speed —
[Ability]' means 'As long as your speed is 4, this object **has** '[Ability]'.'"*
— the parameter is a real ability with its own delivery, which the classifier
already read correctly. Matching the wrapper **overwrote a correct ratified
routing with the wrapper's class**, which is precisely the failure
`PRE-STEP-2-AUDIT-2026-08-04.md` stopped step 2 for. §2's created-ability rule
says the same thing from the other side: the delivery belongs to the ability,
not to the wrapper that grants it.

**RULED: a keyword form whose parameter is an ABILITY is refused by this path.**
It costs 5 static lines and is worth it. Forecast is unaffected — its 11 lines
were already routed.

## 4. RESULT

| | |
|---|--:|
| gap lines closed | **528** |
| lines moved OFF a ratified token | **0** |
| lines appeared / vanished | 0 / 0 |
| `routed_lines` · `keyword_homes` | **UNCHANGED** |

| home | lines | keywords |
|---|--:|---|
| `static` | 356 | Protection 124 · Affinity 73 · Suspend 66 · Splice 30 · Gift 26 · Kicker 16 · Morph 12 · … |
| `activated` | 73 | Equip 33 · Craft 24 · Reinforce 11 · Cycling 2 · Eternalize 2 · Unearth 1 |
| `becomes-targeted-trigger` | 53 | **Ward 53** |
| `upkeep-trigger` | 26 | Cumulative Upkeep 23 · Echo 3 |
| `etb` | 12 | **Champion 12** |
| `replacement` | 7 | Devour 3 · Bloodthirst 2 · Madness 2 |
| `any-death-trigger` | 1 | Recover 1 |
| **non-`static` total** | **172** | |

**All 172 non-`static` lines were read individually before the change landed.**
No false positive survived. The audit's five known false-positive shapes are
carried as canaries and all five still reject:

```
Equip abilities you activate cost {1} less                     -> rejected
Equipped Warriors you control have double strike.              -> rejected
Equipment spells you cast cost {1} less to cast.               -> rejected
Storm Seeker deals damage to target player equal to ...        -> rejected
Other Warriors you control get +1/+1 and have ward {1}.        -> rejected
```

### 4a. Correcting the audit's numbers

`PRE-STEP-2-AUDIT` §D4 hand-read **194** non-`static` lines. Measured: **172**,
and the difference is fully accounted for, not unexplained:

| | |
|---|--:|
| audit's figure | 194 |
| **Forecast** — already routed by the §2b router since `8a4bb31`; the audit predates it | −11 |
| **Equip** — the audit's 43 counts the cost-reducer false positives it then subtracts, plus 4 keyword-plus-rider compounds | −10 |
| `Max speed` — refused by §3a | −5 |
| residual | ≈ 172 |

Per-keyword the two agree exactly where comparable: **Ward 53 = 53 · Craft
24 = 24 · Cumulative upkeep 23 = 23 · Champion 12 = 12.**

## 5. D9 IS NOT TOUCHED, and the gate that keeps it that way

`_keyword_by_form` matches only keywords **present in `KEYWORD_HOME`**. A
keyword with no §2 home stays unrouted: that is **D9** — 49 keywords, ~951
lines measured here (Flashback 191, Partner 75, Bestow 42, Buyback 38, Warp 36,
Rebound 35, Evoke 35, Mutate 34, Plot 33, Disturb 32 …). `KEYWORD-LEDGER-
CANDIDATES.md` sends them to **Phase B**, and that is a Captain ruling, not a
fix. **The matcher can see all 951 and deliberately declines them.**

## 6. Logged, not ruled

- **Keyword-plus-rider compounds** — `Equip {3}. This ability costs {1} less to
  activate for each other Equipment you control.` (Plate Armor),
  `Equip {0}. Activate only once each turn.` (Leather Armor), ~4 lines. The
  line *is* an equip ability carrying a §3 activation-restriction rider. A real
  shape; deliberately left unrouted rather than handled inconsistently.
- **`Max speed`** — 5 lines, refused per §3a. The right treatment is §1's
  multi-axis rule (the card holds *both* the static wrapper and the inner
  ability's delivery), which is a ruling, not a matcher change.

## 7. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| name-invariance (metamorphic) | **1** — the known harness artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** (no Clue line is a keyword line) |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |
| halt-guard | halts unless forms derive for ward · equip · craft · cumulative upkeep · champion |
