# TRIAGE OF THE 201 — what opening positive correctness actually found

**2026-08-09. Nothing fixed here; this is the partition and the verdicts.**

`foundry_ground_truth.py --wide` grades 1,276 assignments instead of 488 and
reports **201 mismatches + 55 unanchored**. The headline number was never the
finding — the partition is.

**One confirmed pipeline defect, 136 corpus lines. Everything else is fixture
or naming.**

---

## THE PARTITION

| # | class | cases | what it is | verdict |
|---|---|--:|---|---|
| 1 | **`landfall` claims a land's OWN etb** | 15 seeds → **136 corpus lines** | **REAL EXTRACTOR DEFECT** | **fix** |
| 2 | `etb` axis, `replacement` delivery | 60 | naming: `etb` used colloquially | ruling |
| 3 | quote anchored to the WRONG line | ~50 | fixture defect | fix the fixture |
| 4 | §2a prefix imprecision | 13 | `death-trigger` vs `any-death-trigger` | naming |
| 5 | spell ability on an `activated-` axis | 13 | membership vs §1 | read |

---

## 1. THE ONE REAL DEFECT — `landfall` is eating land ETBs

```python
re.search(r"\bland (you control )?enters\b", clause)
```

*"When **this land enters**"* matches `land enters`. So a land's **own** ETB
trigger is classified as **landfall**.

The CR keeps these apart cleanly:

- **Landfall** (CR 207.2c ability word) — *"Whenever a land you control
  enters"*. Fires on **every** land, repeatedly, including other lands.
- **`When this land enters`** — an ETB trigger of that permanent (CR 603.6a).
  Fires **once**, for itself.

Khalni Garden triggers once when it enters. Lotus Cobra triggers every time any
land enters. They are not the same mechanism, and 136 lines currently say they
are.

| `landfall` population | lines |
|---|--:|
| **SELF etb, misrouted** | **136 (40%)** |
| real landfall | 204 |

Sample misrouted: A.I.M. Labs, Abraded Bluffs, Adventurer's Inn, Aether Hub,
Akoum Refuge, Archway Commons — the entire "gain 1 life when it enters"
dual-land cycle.

**This is the payoff of the whole exercise.** No routing diff could see it (the
lines have carried a ratified token since before the first snapshot), no
conservation or visibility audit could see it, and `--strict` scores it as
settled. Only positive correctness finds a token that has been wrong from the
beginning.

**The fix is DET and small** — exclude the self-reference subject, which the
extractor already canonicalizes to `~`. It needs the full recipe: routing diff
`--strict --lines`, read all 136 moved lines, four audits.

---

## 2. `etb` MEANS TWO THINGS (60 cases) — naming, not routing

`rule:etb-copy-your-permanent`, `rule:etb-plus1-counter-on-target-creature`,
`rule:etb-with-counters`. Their lines read:

> *"You may have this creature **enter as a copy** of an artifact or creature"*
> *"Mikaeus **enters with** X +1/+1 counters on it"*

Those are **CR 614.1c replacement effects**, and the extractor routes them to
`replacement` — **correctly**. The axis name uses `etb` in the colloquial sense
*"on entering"*, while §2's `etb` is a DELIVERY token meaning *an ETB
triggered ability*.

**Same shape as the synonym collisions**: one string, two meanings. It is the
mirror of `lifegain`/`gain-life` — there, two names for one mechanic; here, one
name for two.

Not a defect in either the axis or the extractor. It is a **ratification**:
either the token or the prefix has to give.

---

## 3. THE QUOTE ANCHORED TO THE WRONG LINE (~50) — fixture, not pipeline

The seeds carry a card + an axis + a quote, and `anchor_line` takes the first
ability line containing the quote. On multi-ability cards that is often not the
line the axis is about:

| card | axis claims | quote landed on |
|---|---|---|
| Monk Class | `etb-bounce-target-creature` | *"When this Class becomes level 2…"* |
| Yotia Declares War | `etb-create-token` | a Saga chapter, *"I — Create a 0/2…"* |
| Kavaron, Memorial World | `etb-create-token` | an activated ability |
| Tempt with Bunnies | `etb-create-token-creature` | a modal mode line |

**The pipeline is right in every one.** The fixture picked the wrong line.

**Fix is mechanical:** when several lines contain the quote, prefer the one
whose delivery matches the axis's claim, and report the ambiguity rather than
silently taking the first. That is a fixture change, not a routing change — and
it must be reported, because "prefer the line that agrees with me" is a
grading rule that can hide a real mismatch if applied carelessly.

---

## 4 & 5. TWO SMALL NAMING/MEMBERSHIP CLASSES

**§2a prefix imprecision (13).** *"Whenever **equipped creature** dies"* routes
to `any-death-trigger` — correctly, since the dying creature is not the source
Equipment. The axis says `death-trigger` (unprefixed = the source itself). The
extractor is right; the slug is imprecise.

**Spell on an `activated-` axis (13).** Seismic Spike — *"Destroy target land.
Add {R}{R}"* — is a **sorcery** on `rule:activated-destroy-target-land`. §1
says a spell ability OMITS delivery (CR 113.3a), so either the membership or
the slug head is wrong. Needs a read, not a rule.

---

## WHAT THIS CHANGES ABOUT `--wide`

**It should not be wired into the gate yet, and 201 was never the number.**
After class 3 is fixed (fixture) and class 1 is fixed (extractor), the residual
is naming work that belongs to Captain, not to a gate.

**Order:** fix class 1 (real defect, 136 lines) → fix class 3 (fixture) →
re-run `--wide` → then decide the gate.
