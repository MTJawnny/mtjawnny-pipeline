# TURNED-FACE-UP TRIGGERS — RULING (2026-08-04)

Fourth item in the 2026-08-04 gap pass. **Zero API calls.**

Gate-3 dossier on `turned-face-up`: **no prior ruling in any status; not in the
codebook.** It appears in three decision packets only as a gap row.

**STATUS: RATIFIED 2026-08-04 (Captain).** `turned-face-up-trigger` entered
`docs/CODEBOOK-NAMING-GRAMMAR.md` §2 as row 8 of the 14-row sheet.

**§4's flagged §2b tension is ALSO ratified, and it was the larger question.**
Captain's answer: **`replacement`, no code change** — the CR *chains* static and
replacement rather than opposing them (CR 113.3d *"Static abilities … create
continuous effects"* → CR 614.1 *"Some continuous effects are replacement
effects"*), so "static ability" and "replacement effect" name the ability and the
effect it creates, not two rival classifications of one object. The ruling
governs **all 16 keywords in that bucket, 282 lines**, not Tribute alone, and is
recorded as grammar **§2e**, which amends §2b.

---

## 1. The CR states the boundary this token needs, twice

Turning face up is **not** entering the battlefield, and the CR says so outright
in both the morph rule and the general face-down rule:

> **CR 702.37e** — *"…then turn the permanent face up. The morph effect on it
> ends, and it regains its normal characteristics. **Any abilities relating to
> the permanent entering the battlefield don't trigger when it's turned face
> up** and don't have any effect, because the permanent has already entered the
> battlefield."*
>
> **CR 708.8** — *"As a face-down permanent is turned face up… **Any abilities
> relating to the permanent entering the battlefield don't trigger** and don't
> have any effect, because the permanent has already entered the battlefield."*

So `etb` and this token are **hard-disjoint by CR**, in the same way
`death-trigger` and `leaves-battlefield-trigger` are. A card cannot be routed to
`etb` on the strength of a turn-face-up trigger, and the reverse holds too.

**The general rule is CR 708, not morph.** CR 708.7 — *"The ability or rules
that allow a permanent to be face down may also allow the permanent's controller
to turn it face up"* — so the family spans morph (702.37), megamorph (702.37b),
disguise (702.168), manifest (701.40), manifest dread (701.62) and cloak
(701.58). **Anchoring on 708 rather than on morph is what keeps the five
mechanics in one token** instead of five near-duplicates.

## 2. RULING — one token

| token | lines | cards | CR |
|---|--:|--:|---|
| **`turned-face-up-trigger`** (+ §2a prefix) | 121 | 121 | 708.7, 708.8, 702.37e |

§2a measured: **source 94 · `any-` 18 · `other-` 9**. Unlike discard and
is-dealt-damage, `other-` is **populated** here — Salt Road Ambushers prints
*"whenever **another** permanent you control is turned face up"*.

Scope uses existing §6 tokens (`you control` is the common form: Trail of
Mystery, *"a permanent **you control**"*). No new scope vocabulary.

## 3. THE LARGER FINDING — 236 replacement effects were invisible

**CR 614.1c names three templates verbatim:**

> *"Effects that read **'[This permanent] enters with . . . ,' 'As [this
> permanent] enters . . . ,'** or **'[This permanent] enters as . . .'** are
> replacement effects."*

The DET pass matched only the **first**. The other two fell through to
`spell-or-static` — and because the gap census **excludes** `spell-or-static`,
the defect was not merely unfixed, it was **unreportable**. Nothing in the census
had ever shown it.

| template | CR | was | now |
|---|---|---|---|
| "[permanent] enters with …" | 614.1c | `replacement` (66) | unchanged |
| **"As [permanent] enters …"** | 614.1c | **`spell-or-static` (236)** | **`replacement`** |
| **"[permanent] enters as …"** | 614.1c | `spell-or-static` | `replacement` |
| **"As [permanent] is turned face up …"** | **708.11** | `spell-or-static` (6) | `replacement` |

CR 708.11 is the anchor for the fourth row — *"If a face-down permanent would
have an 'As [this permanent] is turned face up . . .' ability… that ability is
applied **while** that permanent is being turned face up, not afterward."* That
is a replacement, not a trigger, which is why Hooded Hydra and Bubble Smuggler
are **not** members of the 121 above.

**`replacement` moved 1,963 → 2,178 lines (+215).**

Two clause types are deliberately **excluded** by lookahead, because neither is
a replacement effect: CR 601.2b additional-cost clauses ("As an additional cost
to cast this spell…", 315 lines) and `as long as` static abilities (435 lines).

## 4. §2b TENSION — logged, needs a Captain call

11 lines moved **off the ratified `static` token** onto `replacement`. All 11 are
the **Tribute** keyword, and the two CR rules pull opposite ways:

> **CR 702.104a** — *"Tribute is a **static ability** that functions as the
> creature with tribute is entering the battlefield. 'Tribute N' means '**As
> this creature enters**, choose an opponent…'"*

- §2b says a keyword's **class** picks the slot → `static`.
- §2's own `replacement` row claims *"'enters with/as' shapes"* and cites
  614.1a–c → `replacement`.

**Resolved toward `replacement` here**, on three grounds: CR 614.1c says these
effects *are* replacement effects; §2's `replacement` row names the template
explicitly; and a replacement effect is not *"continuously true"*, which is §2's
gloss on `static` (CR 113.3d). The 66 "enters with" lines were **already**
`replacement`, so leaving Tribute on `static` split one CR template across two
tokens.

**This is a real ambiguity in §2b and is flagged rather than settled.** The
general form of the question — *a static ability that generates a replacement
effect takes which slot?* — governs more keywords than Tribute.

## 5. Verification

| gate | result |
|---|---|
| determinism ×2 | **byte-identical** |
| known-good routings | 9/9 |
| lines changed | 338 (215 replacement recoveries + the damage-descriptor rename from item 3) |
| `static` movement | 11, all Tribute, all inspected |
