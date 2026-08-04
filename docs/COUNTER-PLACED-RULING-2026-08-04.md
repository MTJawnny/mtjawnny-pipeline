# COUNTER-PLACED TRIGGERS — RULING (2026-08-04)

Seventh item in the 2026-08-04 gap pass. **Zero API calls.**

Gate-3 dossier on `counter-placed`: no prior ruling, not in the codebook. **But
§8, §8a, §7 and batch-5 all govern counter tokens**, and per the CDR-09 lesson a
checker that knows only one of them manufactures false defects. All four were
read before writing this.

**STATUS: RATIFIED 2026-08-04 (Captain) — §2's family, §3a's sibling NOT.**

The **`<type>-counter-placed-trigger` §11 grammar family** (§2 below) was ratified
as row 6 of the 14-row sheet and is recorded in `docs/grammars.json` and in
grammar **§8b**. Its type facet is registered as **OPEN**, because §8 rule 1's
`<name>` arm is unbounded — so the family's siblings are correctly reported as
unenumerable rather than being generated as virtual nodes.

**§3a's `<type>-counter-threshold-trigger` remains RULED-NOT-RATIFIED.** The
sheet carried it as its *own* question — *"whether §3a's name is accepted"* —
separate from the ratification word on the 14 rows, and only the latter was
given. Its reasoning stands unchanged and needs zero new vocabulary; it is
carried to the next decision sheet. It is deliberately **absent** from
`grammars.json`.

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
the effect happens, which is the ratified split test (§2, D3f).

### 3a. RESOLVED — the question was TWO questions (2026-08-04 EVE, RULED-NOT-RATIFIED)

Captain asked for one more CR check to see whether this resolves cleanly. **It
does, and it needs no new vocabulary.**

**The two halves separate:**

| | verdict | why |
|---|---|---|
| threshold **vs** every-placement | **AXIS IDENTITY** | fires once at a threshold vs on every placement — changes WHEN/WHETHER, the ratified D3f test |
| **which** ordinal (3rd/4th/5th/6th/7th/10th/12th) | **PARAMETER** | magnitude only. Batch-5 is a fortiori: +1/+1 vs -1/-1 do *opposite* things and were still a parameter |

**The corpus decides the second half.** Nine of the eleven lines are ONE card
design — the plan-counter scheme cycle — printed with ordinals 3·4·4·4·4·5·6·7.
Treating the number as identity mints **five axes for one mechanic**, which is
the `scales-token-count-with-x` duplication class that design goal #1 forbids.

**CR checks, all three clean:**

- **CR 603.8 rules out a state trigger.** *"Some triggered abilities trigger
  when a game state … is true, **rather than triggering when an event
  occurs**."* A counter being put on IS an event, so this is an ordinary
  CR 113.3c trigger whose condition names which instance.
- **`threshold` is ALREADY RATIFIED vocabulary** — §14 Q5, walk-ratification
  2026-07-31. No new token.
- **No CR homograph.** The CR glossary: *"'Threshold' used to be a keyword
  ability. **It is now an ability word and has no rules meaning.**"* Identical
  disposition to `Inspired` in §2's `becomes-untapped-trigger` row.

**The one real collision is inside the codebook, and §8a's ratified principle
resolves it.** Four live axes use `threshold` in a STATIC sense
(`transforms-on-graveyard-threshold`, `grants-ability-at-threshold-self`,
`-board`, and the killed `grants-ability-at-counter-threshold`, whose definition
reads *"as long as it has at least…"*). Ours fires once. §8a: **sense is carried
by POSITION and BINDING, not by the bare token** — so `-trigger` binding
disambiguates, exactly as it does for the `counters` homograph:

| slug | sense |
|---|---|
| `<type>-counter-threshold-trigger` | fires **once**, on the Nth placement |
| `<type>-counter-placed-trigger` | fires on **every** placement (§2 sheet row 6) |
| `grants-ability-at-threshold` *(no `-trigger`)* | static, continuously true |

**PROPOSED: `<type>-counter-threshold-trigger`, a sibling in row 6's §11
family. N is a parameter. Zero new vocabulary.** RULED-NOT-RATIFIED.

### 3b. Correction to this document's own count — it was RIGHT

A 2026-08-04 EVE re-measurement reported **10**, not 11, and **the
re-measurement was wrong**: its ordinal list omitted `eleventh`/`twelfth`, so
Midnight Clock's *"When the **twelfth** hour counter is put on this artifact"*
fell out. **11 stands.** Fourth Gate 4 firing of the session, and the same root
cause as the landwalk defect — a hand-listed enumeration missing a member.

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
