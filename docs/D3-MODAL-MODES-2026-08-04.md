# D3 — MODAL MODES INHERIT THEIR HEADER'S DELIVERY (2026-08-04)

**515 gap lines closed. One line re-routed, and it was a FIX.** Third item of
the 2026-08-04 EVE work order. **Zero API calls.**

Gate 3b prior art (`modal bullets`, `modal modes`): the known art is
`foundry_common.expand_modal_bullets()` / `det_scan_texts()`, **DET
preprocessing standard v1, ratified 2026-07-31** — exactly as the handoff said.
Nothing else.

---

## 1. The defect

A modal ability is printed as a header carrying the delivery, then one `• ` line
per mode. `ability_lines()` splits on newlines, so each bullet became its own
ability line **with no trigger of its own**:

```
When this creature enters, choose one —          <- etb
• Cure Wounds — You gain 2 life.                 <- routed NOWHERE
• Dispel Magic — Destroy target enchantment.     <- routed NOWHERE
• Gentle Repose — Exile target card from a graveyard.
```

Grammar §1 is explicit that this is wrong — *"modal modes each earn their
axis"*, with Blizzard Specter as its worked case (a member of both its discard
axis and its bounce axis).

## 2. Measured population, with the boundary stated

| | |
|---|--:|
| bullet ability lines in the corpus | **1,791** |
| under a **ratified** modal header (`_MODAL_HEADER_RE`) | 1,532 |
| …of those, header carries a ratified delivery | **516** |
| …header is a spell ability (unmarked — §1's correct default) | 1,016 |
| under a header that is **not** a ratified modal header | 259 |

The 1,016 are instants and sorceries: their header has no DELIVERY, so the modes
correctly inherit nothing. **The fix is a no-op for them by construction**, not
by exclusion.

## 3. What was implemented — and what was deliberately NOT

`deliveries_for_lines(card, ratified)` is the single modal-aware entry point;
`foundry_shape_extractor.scan()`, its keyword-action ranking pass, and
`foundry_routing_regression.route_all()` all now go through it, so no consumer
can silently keep the old behaviour.

**The delivery is INHERITED, never re-parsed from a joined string.** The
ratified `expand_modal_bullets()` joins header + bullet because its job is DET
*pattern scanning*, where a same-clause pattern must see both halves at once.
Reusing that join here would hand `trigger_clause` a header condition glued to a
mode's effect text — the CR 113.3c whole-line-vs-clause bug this file has now
been bitten by **six** times. The mode's delivery simply *is* the header's, so
it is copied.

**The modal test is the ratified one**, `foundry_common._MODAL_HEADER_RE`, not a
fresh one. Bullets under a non-modal header are not inherited, and that
exclusion is load-bearing:

> **Celebr-8000** — *"At the beginning of combat on your turn, **roll two
> six-sided dice**… For each other result, it gains the indicated ability"*
> followed by `• 2 — menace`, `• 3 — vigilance`, `• 4 — lifelink`.

Those bullets are a **die-roll result table**, not a set of modes. A looser
"previous line with a delivery" rule would have swept them in.

## 4. The one re-route was a FIX

| card | was | now |
|---|---|---|
| **Pyramids** | `replacement` | **`activated`** |

```
{2}: Choose one —
• Destroy target Aura attached to a land.
• The next time target land would be destroyed this turn, remove all damage
  marked on it instead.
```

The ability is **activated** (`{2}:` — CR 113.3b). The old `replacement` came
from reading the *mode's own effect words* (`would … instead`), which §2 forbids
outright: **"DELIVERY is determined by ability STRUCTURE, never by effect
words"** (batch-4 D1 / batch-7 feedback #1). The mode's effect is still a
replacement effect; its DELIVERY is not.

## 5. RESULT — and it corroborates the audit exactly

| home | lines | audit's hand-read figure |
|---|--:|--:|
| `etb` | **201** | **201** ✓ |
| `activated` | **64** | **64** ✓ |
| `cast-trigger` | **33** | **33** ✓ |
| `begin-combat-trigger` | **26** | **26** ✓ |
| `etb` + `attack-trigger` (compound) | **19** | **19** ✓ |
| `end-step-trigger` · `upkeep-trigger` | 18 · 18 | |
| `death-trigger` 16 · `any-attack-trigger` 15 · `attack-trigger` 14 · `landfall` 14 · … | | |
| **total** | **515** | 504 |

Five of the audit's rows reproduce **to the line**. The total differs because
the audit predates this session's 14 ratified §2 rows and D4, which gave several
headers a delivery they did not have when it was written.

### 5a. `routed_lines` moved 61,868 → 61,900, and the +32 is accounted for

The harness flagged it loudly (*"ROW COUNT CHANGED … the pass altered how lines
are produced"*) and fell back to a key-based diff — correct behaviour, and worth
recording that the pin caught it. Every one of the 32 is a **compound-trigger
header** giving each of its modes both deliveries, which is §1's multi-axis rule
and `parse_deliveries`'s documented purpose:

| extra rows | tokens |
|--:|---|
| 19 | `etb` + `attack-trigger` |
| 4 | `etb` + `death-trigger` |
| 3 | `attack-trigger` + `blocks-or-becomes-blocked-trigger` |
| 2 each | `attack-trigger`+`becomes-targeted` · `etb`+`leaves-battlefield` · `cast-trigger`+`etb` |

## 6. LOGGED, NOT RULED — a gap in the ratified modal regex

`_MODAL_HEADER_RE` requires the header to **end** with a long dash:

```python
r"choose (?:one|two|three|one or more|up to \w+)\b.*—\s*$"
```

**49 lines across 19 cards are genuinely modal and end with a period instead**,
so they are missed:

> **Shadrix Silverquill** — *"At the beginning of combat on your turn, you may
> **choose two. Each mode** must target a different player."*
> **Lita, Little Orphan Amphibian** — *"Alliance — Whenever another creature you
> control enters, choose one that hasn't been chosen this turn."*

Shadrix's own text says *"Each **mode**"*, so the CR-side reading is not in
doubt. **Not fixed here**, deliberately: `_MODAL_HEADER_RE` is part of a
**ratified** standard (DET preprocessing standard v1), it is shared with
`det_scan_texts()`, and widening it changes DET pattern scanning for every
consumer — a separate pass with its own before/after diff, not a rider on this
one.

## 7. Verification

| gate | result |
|---|---|
| lines moved | 516 — **515 gap closures + 1 fix** |
| lines appeared / vanished | 0 / 0 |
| `keyword_homes` | 144 **UNCHANGED** |
| `routed_lines` | 61,868 → 61,900, +32 fully accounted (§5a) |
| determinism ×2 | **byte-identical** |
| name-invariance (metamorphic) | **1** — the known harness artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |
