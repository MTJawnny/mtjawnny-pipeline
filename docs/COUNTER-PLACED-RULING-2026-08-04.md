# COUNTER-PLACED TRIGGERS — RULING (2026-08-04)

Seventh item in the 2026-08-04 gap pass. **Zero API calls.**

Gate-3 dossier on `counter-placed`: no prior ruling, not in the codebook. **But
§8, §8a, §7 and batch-5 all govern counter tokens**, and per the CDR-09 lesson a
checker that knows only one of them manufactures false defects. All four were
read before writing this.

**STATUS: RULED, NOT RATIFIED.** Proposed as a **§11 grammar family**, not as a
list of tokens.

---

## 1. CR 122.6 is the anchor, and it carries a non-obvious boundary

> **CR 122.6** — *"Some spells and abilities refer to **counters being put on an
> object**. This refers to putting counters on that object **while it's on the
> battlefield** and **also to an object that's given counters as it enters the
> battlefield**."*

So a counter-placed trigger **also fires on counters placed as the permanent
enters** — it is not disjoint from `etb` or from the "enters with counters"
replacement (CR 614.1c). §1's multi-axis rule applies: a card can hold both, and
neither subsumes the other. Recorded so a later session does not "fix" the
overlap.

> **CR 122.1** — *"A counter is a **marker** placed on an object or player…
> Notably, **a counter is not a token, and a token is not a counter.**"*

That is §8 rule 3's anchor, restated here because this family's slugs sit one
typo away from the token vocabulary.

## 2. RULING — a §11 grammar family, `<type>-counter-placed-trigger`

§8 rule 1 is binding: **the noun sense is ALWAYS TYPED**, and the bare noun
"counter" never appears in a slug. So this is not one token — it is a **grammar**
whose type slot is filled per §8's closed vocabulary, and per §11 *"a virtual
node instantiates the moment one quote-verified member arrives — no fresh
ratification."*

| instantiated node | lines | cards |
|---|--:|--:|
| `plus1-counter-placed-trigger` | 31 | 31 |
| `plan-counter-placed-trigger` | 9 | 9 |
| **`any-counter-placed-trigger`** | 2 | 2 |
| `loyalty-counter-placed-trigger` | 1 | 1 |
| `hour-counter-placed-trigger` | 1 | 1 |

**`any-` is the §8a form, not a coinage.** §8a ratified `any-` precisely for
*"axes that genuinely span every counter type and therefore cannot be typed"* —
Putrid Hexhag and Stalwart Successor print *"whenever **one or more counters**
are put on"* with no type word to bind to. §8a's binding rule requires a left
binder, and `any-` is the ratified one. Naming these `counter-placed` bare would
violate §8 rule 1 and §8a's own test.

`plan` and `hour` are `<name>-counter` types per §8 rule 1, verified from full
oracle text: Political Triumph and Glorious Purpose both *create* plan counters
on themselves; Midnight Clock accrues hour counters.

## 3. An ORDINAL threshold qualifier, logged not ruled

11 of the 44 lines print an **ordinal**, not a bare event:

- Political Triumph — *"When the **fourth** plan counter is put on this
  enchantment"*
- Midnight Clock — *"When the **twelfth** hour counter is put on this artifact"*

This is a genuine `-conditional`-class distinction: the ability fires **once, at
a threshold**, not on every placement. It is a §1 QUALIFIER and it changes WHEN
the effect happens, which is the ratified split test (§2, D3f). Not folded;
**logged for a Captain call** on whether the ordinal is a parameter (batch-5
polarity precedent) or axis identity.

## 4. DET defect fixed

The type-word capture used `\b` before the type, and **`+` is not a word
character** — so `\b` matched at the "1" and produced the nonsense type
`1/+1-counter-placed`. The polarity tokens are the ratified `plus1` / `minus1`
(§8 rule 1), never the printed glyphs. This is the same class as the CDR-09
homograph failure: a slug built by string-slicing rather than by the ratified
vocabulary.

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | byte-identical |
| known-good routings | 9/9 |
| 44 lines | fully partitioned across 5 instantiated nodes |
