# D8 — KEYWORD LISTS, AND THE SEAM BETWEEN THE TWO KEYWORD PATHS (2026-08-04)

**95 gap lines closed — 34 semicolon-joined, and 61 the item never claimed.**
Sixth item of the work order. **Zero API calls. No CR question.**

---

## 1. D8 as stated: the semicolon

`keyword_line_tokens` split a printed keyword list on the **comma only**, so
every semicolon-joined line fell through — *"Flying; banding"*, *"Defender;
reach"*, *"Trample; rampage 1"*, *"Flying; trample; rampage 4"*. **34 lines.**

There is no CR question: both are ordinary list punctuation and the semicolon
carries no rules meaning the comma does not. `KEYWORD_LIST_SPLIT = [,;]` is
shared by **both** keyword paths, because `keyword_line_tokens` now falls
through to `keyword_form_tokens` (D4) and fixing one would have let them drift.

## 2. The larger half: the two paths could not cooperate on ONE line

Splitting on the semicolon left **2 of the 34 still unrouted**:

```
Knights of Thorn      Protection from red; banding
Tel-Jilad Archers     Protection from artifacts; reach
```

**Neither keyword path could take the line, because each half belonged to the
other path.** `Protection from red` is a §2b **parameterized form**
(CR 702.16b, `Protection from [quality]`); `banding` is a **bare keyword name**.
The bare-name path rejected the line on the left half, the form path rejected it
on the right, and it routed nowhere.

`Protection from black; flanking` routed fine — **but only by accident**, because
Flanking happens to have a CR printed form too, so both halves landed on the same
path.

`_keyword_by_form` now checks **bare name, landwalk variant, then CR form** for
each part, so a mixed list resolves. That closed the 2, and then **61 more that
were the identical defect with a comma instead of a semicolon**:

| | |
|---|--:|
| `Flying, protection from green` (Coast Watcher) | |
| `First strike, protection from black and from red` (Paladin en-Vec) | |
| `Double strike, protection from black and from green` (Mirran Crusader) | |
| `Flying, first strike, vigilance, trample, haste, protection from black…` (Akroma) | |
| **total** | **61** |

Every one is `<bare keywords>, protection from <quality>` — all correctly
`static`. **All 95 newly-routed lines were read.**

## 3. Multi-delivery lines are correct, and they are why the row count moved

7 lines carry **two** deliveries, which is §1's multi-axis rule:

| card | line | tokens |
|---|---|---|
| Varchild's War-Riders · Gorilla Berserkers · Teeka's Dragon | `Trample; rampage N` | `static` + `blocks-or-becomes-blocked-trigger` |
| Bushi Tenderfoot | `Double strike; bushido 2` | same |
| Knight of Sursi · Riftmarked Knight | `Flying; flanking` | same |
| **Emrakul, the Aeons Torn** | `Flying, protection from spells that are one or more colors, annihilator 6` | `static` + **`attack-trigger`** |

Rampage, bushido and flanking are CR 702 blocking triggers; annihilator is an
attack trigger (§2b's derived table). `routed_lines` 61,900 → 61,907, +7,
one per dual-delivery line.

## 4. RESULT

| | |
|---|--:|
| gap lines closed | **95** (34 semicolon + 61 comma) |
| regressions (ratified → None) | **0** |
| re-routes | **0** |
| lines appeared / vanished | 0 / 0 |
| `static` | 12,136 → **12,231** |
| `blocks-or-becomes-blocked-trigger` | 387 → 393 |
| `attack-trigger` | 1,491 → 1,492 |
| unrouted | 18,551 → **18,456** |
| `keyword_homes` | 148 **UNCHANGED** |

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — the known harness artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |

## 6. What this item proves

**A defect stated as "29 semicolon lines" was really a seam between two code
paths, and the punctuation was incidental.** Fixing the stated scope closed 34
lines; fixing the actual cause closed 95. The tell was that 2 lines survived the
stated fix — a residue is worth chasing, because a fix that leaves one is
usually addressing a symptom.

**`Protection from black; flanking` routing correctly was luck, not coverage.**
It is the same shape as `Protection from red; banding`, and it worked only
because both halves happened to fall on one path. A passing case that passes for
the wrong reason is invisible to every census.
