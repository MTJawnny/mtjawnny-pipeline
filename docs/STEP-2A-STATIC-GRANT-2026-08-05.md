# STEP 2, FIRST SLICE — THE STATIC GRANT (2026-08-05)

**294 gap lines closed: 237 `static` + 57 `replacement`. Zero regressions, zero
re-routes.** The first piece of step 2, taken as **two named shapes** rather than
as the blanket sweep `PRE-STEP-2-AUDIT-2026-08-04.md` stopped. **Zero API calls.**

---

## 1. Why this is not "step 2"

`PRE-STEP-2-AUDIT` §6 stopped step 2 because routing `spell-or-static` wholesale
into `static` would take **1,883 wrong answers and make them read as resolved**.
That reasoning is unchanged and this pass does not touch it: **17,367 lines
remain in `spell-or-static`** and 5,153 of those are permanent-side.

This closes two shapes that are individually decidable. Everything else stays
reported.

## 2. Shape A — `enters? as`, the clone family (57 lines)

The replacement branch tested `\benters as\b` — **plural only**. Every clone
prints the subjunctive:

> *"You may have this creature **enter as** a copy of any creature on the
> battlefield."*

Mirror Image, Clever Impersonator, Phyrexian Metamorph, Copy Artifact, Body
Double, Sakashima, Sculpting Steel — **57 lines**, and CR 614.1c names the
template verbatim as one of its three: *"'[This permanent] **enters as** . . .'
are replacement effects."*

**Same class as `MAIN-PHASE-RULING` §3a**, where `\bmain phase\b` missed "main
phase**s**" and lost 10 lines — here it is the mirror, a plural-only test losing
the singular. **An inflection is not a shape.**

## 3. Shape B — the static grant (237 lines)

> **CR 113.3d** — *"Static abilities are written as statements. They're simply
> true."*

A line that **grants a quoted ability to a class of permanents** is such a
statement. §2's created-ability rule then assigns the *quoted* ability to
whatever it is granted to, and the **grant itself** to this card:

```
Cryptolith Rite   Creatures you control have "{T}: Add one mana of any color."
Food Fight        Artifacts you control have "{2}, Sacrifice this artifact: ..."
Magma Sliver      All Slivers have "{T}: Target Sliver creature gets +X/+0 ..."
```

Reached only at the **tail**, so loyalty, activated, trigger and replacement have
all already declined — which is what makes shape A's ordering load-bearing: the
57 clones are claimed by `replacement` *before* they can reach here.

### 3a. It took TWO tightenings, and each was found by reading the output

The first version matched a grant **anywhere in the line** and swept in **97
instants and sorceries** whose *effect* grants an ability — and would have
**undone two of D5's nine created-ability corrections** (Brokers' Safeguard, The
Eighth Doctor).

| | |
|---|---|
| `Creatures you control have "…"` | the line **is** the grant → static |
| `Tap target creature. That creature perpetually gains "…"` | an **instant**; §1, unmarked |

**Fix 1 — no sentence break before the grant** (`^[^.]*?`). Eighth instance of
the whole-line-vs-clause bug class in this file, and the first on the static side.

That still leaked **65** more:

> *"**Until end of turn**, lands you control gain '{T}: Add one mana of any
> color.'"* — Divergent Growth, an **instant**.
> *"**Target** creature card in your graveyard **perpetually** gains …"* — a
> sorcery.

**Fix 2 — a DURATION or a TARGET disqualifies it**, straight from CR 113.3d: a
static is *continuously true*, so `until` / `target` / `perpetually` /
`this turn` appearing **before** the grant means a resolving spell handed the
ability out. The markers are tested only on the pre-grant text, so a granted
ability that itself says "until end of turn" **inside its quote** is unaffected.

### 3b. Residual leakage: ONE line, and it is correct

Face-aware audit of all 237: exactly one is not permanent-side —

> **Torrent of Lava** (Sorcery) — *"**As long as Torrent of Lava is on the
> stack**, each creature has '{T}: Prevent the next 1 damage…'"*

That **is** a static ability. CR 113.3d's own wording covers it: static abilities
are active *"while the permanent … is on the battlefield … **or while the object
with the ability is in the appropriate zone**."* §1's unmarked default governs a
spell's **resolution effect**, not a static that functions on the stack.
**Zero real leakage.**

## 4. RESULT

| | |
|---|--:|
| gap lines closed | **294** (237 static + 57 replacement) |
| regressions (ratified → None) | **0** |
| re-routes | **0** |
| lines appeared / vanished | 0 / 0 |
| `static` | 12,231 → **12,468** |
| `replacement` | 2,298 → **2,355** |
| unrouted | 18,456 → **18,162** |
| `routed_lines` · `keyword_homes` | 61,907 · 148 **UNCHANGED** |

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| name-invariance | **1** — the known harness artifact, unchanged |
| Clue/investigate ground truth | **byte-identical** |
| lint | clean — 565 axes · 359 active · 8,740 members |
| family sweep | 6 blocking, the same 6 |
| definition drift | 35, unchanged |

## 6. What remains of step 2

**17,367 lines in `spell-or-static`, 5,153 of them permanent-side.** The method
that worked here is the one to continue with: **name a shape, measure it, read
its output, tighten until the leakage is zero or explained — then take the next
shape.** Two tightenings were needed on a shape that looked obvious, and both
were visible only in the output, never in the idea.
