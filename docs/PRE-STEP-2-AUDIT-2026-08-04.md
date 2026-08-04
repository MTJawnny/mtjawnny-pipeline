# PRE-STEP-2 AUDIT — the delivery extractor, audited by method (2026-08-04)

> **STATUS, 2026-08-05 — D1–D6 and D8 are ALL CLOSED.** This document remains the
> reference for the partition and the method; its per-defect line counts are
> pre-fix and are superseded by each defect's own record:
> D3 `docs/D3-MODAL-MODES-2026-08-04.md` · D4 `docs/D4-KEYWORD-FORMS-2026-08-04.md` ·
> D5 `docs/D5-REPLACEMENT-WINDOW-2026-08-04.md` · D6 `docs/D6-COST-HEAD-2026-08-04.md` ·
> D8 `docs/D8-KEYWORD-LIST-SPLIT-2026-08-04.md`.
> **D9 is a Captain ruling (Phase B), not a fix. What remains of this audit is
> STEP 2 itself**, which §6 still correctly describes as unsafe as a blanket sweep.

Captain, 2026-08-04: *"before the route let's do an additional audit on all work
done"* — then: *"maybe even taking a step back and contemplating on how to more
thoroughly audit wouldn't be a bad idea."*

**Verdict up front: DO NOT RUN STEP 2 AS SPECIFIED. It would file 1,883 lines —
20% of the population it touches — onto `static`, a token the CR contradicts for
every one of them.** Nine defects below, with the measurement and the fix for
each. Zero API calls. **Nothing was changed by this audit; it is measurement
only.**

---

## 0. THE METHOD, AND WHY THE OLD ONE WAS NOT ENOUGH

The first pass of this audit was *opportunistic*: pick a suspicious population,
measure it, read examples. It found seven defects and **could make no
completeness claim at all** — no way to answer "what else is wrong?"

That is this project's recorded failure shape, stated one level up:

> **Every guard reports on what it classifies. Nothing reports on what it
> silently absorbs.**

The gap census excludes `spell-or-static`. `--rank` counts a `spell-or-static`
line as *resolved*. The Clue ground-truth set holds no Equipment. The
spell-or-static audit's own partition used the root type line. Four independent
guards, four blind spots, all structural.

**Four principles replace it, and the last one is the one that paid.**

| # | principle | why |
|---|---|---|
| 1 | **Audit the PARTITION, not samples** | every line lands in exactly one CR-anchored bucket; the *residual* is a first-class number and must be driven to something nameable |
| 2 | **Invert every classifier** | today's tooling measures PRECISION ("are lines routed here right?"). Every defect below is a RECALL failure ("what belongs here and isn't?"). Equip, loyalty, landwalk, Ward — **not one was visible as a precision failure** |
| 3 | **Audit the TEXT TRANSFORMS before the classifier** | a transform that silently deletes text is worse than a classifier that mislabels, because nothing downstream can see it. `ABILITY_WORD` is upstream of every delivery decision |
| 4 | **METAMORPHIC testing** | change an input in a way that *must not* change the output. Needs **no ground truth and no judgement** — which is exactly what this project keeps running out of |

**Principle 4 is the finding of this session.** A card's delivery cannot legally
depend on its **name**. So: rename every card to a neutral string, re-route all
61,383 lines, and diff.

> **63 lines changed delivery when only the name changed. 62 share one root
> cause. One is a harness artifact** (a card *named* "Storm of Memories" whose
> keyword line is the word "Storm").

That is a **closed** result — the kind the opportunistic method cannot produce.
It also caught my own harness: the first run reported 195, and **Gate 4 applied
to my own check** found the rename was not faithful (it did not use
`_cardname_candidates`, the canonicalizer's own set). 132 of the 195 were my
test's fault, not the code's.

---

## 1. WHAT THE SHIPPED ROUTER FIX ACTUALLY DID — verified exhaustively

`KEYWORD-ROUTER-FIX-2026-08-04.md`, re-verified here rather than trusted:

| check | result |
|---|---|
| all 824 moved lines, normalised | **28 distinct shapes, every one a bare keyword line** |
| moved lines containing a created-ability quote (§2) | **0** |
| moved lines longer than 40 characters | **0** |
| `KEYWORD_HOME` entries changed | **exactly 7** — the 6 added, Unearth corrected |
| landwalk matcher vs the 31 near-miss lines | **all 31 correctly rejected** |
| determinism ×2 | byte-identical |
| Gate 2 | unchanged in every direction |
| name-invariance | the fix introduces **no** name dependence |

**It is sound.** Every defect below pre-dates it.

---

## 2. NINE DEFECTS, BY BLAST RADIUS

### D1 — `ABILITY_WORD` destroys the front of 556 lines *(fix: one regex)*

```
^\s*[A-Z][A-Za-z'’\- ]{2,40}(\s*—|\s*-)\s*
                                    ^^^^^ this alternative
```

The character class contains a hyphen, so the pattern matches across
**hyphenated words** and **minus signs**:

| printed | what the classifier receives |
|---|---|
| `When Spider-Ham enters, create a Food token.` | `Ham enters, create a Food token.` |
| `Whenever a non-Human creature you control attacks, …` | `Human creature you control attacks, …` |
| `Put a -1/-1 counter on target creature.` | `1/-1 counter on target creature.` |
| `Attacking creatures get -1/-0.` | `1/-0.` |

**Exhaustively classified, not sampled: 333 minus signs · 223 hyphenated
words · ZERO legitimate ability words.** All 3,004 real CR 207.2c ability words
use the em-dash and are unaffected.

**90 of the 556 are triggers whose CR 113.3c condition is decapitated**, so they
cannot enter the trigger branch and fall to `spell-or-static`.

**The one piece of luck: it hides, it does not inflate.** The 556 currently
route only to `spell-or-static` (528), `replacement` (18) and `static` (10,
Web-slinging — safe because `keyword_line_tokens` runs before this transform).
**No ratified trigger family's count contains a mutilated line**, so no ratified
number is wrong because of this. The 18 `replacement` routings must be re-read
when the fix lands.

**Fix:** drop the `|\s*-` alternative — em-dash only, per CR 207.2c.
**This must be fixed FIRST. It is upstream of every other decision.**

### D2 — 900 loyalty abilities lost; the 7 that route are all wrong

```python
if ":" in body:
    head = body.split(":")[0]
    if ... re.search(r"[{}]|\bsacrifice\b|\bdiscard\b|\bpay\b|\btap\b|…", head):
        if re.search(r"^[+\-−]?\d|loyalty", head.strip()[:3]) …:   # ← nested INSIDE
            return "loyalty", "loyalty-ability"
```

A loyalty cost is `+1`. It contains no mana symbol and none of the listed verbs,
so **the outer gate rejects it and the loyalty branch is unreachable for exactly
the cards it exists for.** `loyalty` is ratified §2 vocabulary (CR 606.1) with
the b7 Ob Nixilis ruling behind it.

| | |
|---|--:|
| planeswalker loyalty lines routed to `spell-or-static` | **900** |
| lines routed to `loyalty` corpus-wide | **7** |
| …of those 7 that are actually loyalty abilities | **0** |

The 7 are **Station tier lines** (CR 702.184) — The Eternity Elevator, Kavaron,
Adagia, Uthros, Hearthhull, Susur Secundi, Evendo — printed `20+ | {T}: Add …`.
`head.strip()[:3]` sees `20+` and `^[+\-−]?\d` matches the `2`.

**Fix:** hoist the loyalty test out of the cost gate and anchor it on the
printed shape, `^([+−-][0-9X]+|0)\s*:` — a sign is mandatory, which excludes
`20+` by construction.

### D3 — 504 modal MODES orphaned from a delivery-bearing header

**A ratified DET standard already covers this and the shape extractor never
adopted it:** `foundry_common.expand_modal_bullets`, *"DET preprocessing
standard v1, part 2 (modal-mode splitting, ratified 2026-07-31)"*. Grammar §1
agrees — *"Modal modes each earn their axis."*

`ability_lines` splits on newlines only, so every `• …` bullet is a detached
line and its header's delivery is lost:

| header delivery | orphaned bullets | example |
|---|--:|---|
| `etb` | **201** | Dawnbringer Cleric — *"When this creature enters, choose …"* |
| `activated` | **64** | Kargan Intimidator — *"{1}: Choose one that hasn't been chosen …"* |
| `cast-trigger` | **33** | Kykar, Zephyr Awakener |
| `begin-combat-trigger` | 26 | Henrika Domnathi |
| `etb` + `attack-trigger` | 19 | Immard, the Stormcleaver |
| `end-step-trigger` · `upkeep-trigger` · `any-attack-trigger` · … | 161 | Astarion · Demonic Pact · Breeches |
| **total, permanent-side** | **504** | |

(999 further bullets sit on instants/sorceries, where unmarked is §1's correct
default.)

### D4 — 1,974 parameterized keyword lines unrouted; **194 belong on a NON-`static` token**

`keyword_line_tokens` recognises a keyword only when its parameters are mana
symbols or bare digits (`COST_OR_PARAM`). Every keyword taking a **typed** or
**clause** parameter is invisible.

**All 217 non-`static` candidates were read by hand. 23 are false positives**
(card names — *"Storm Seeker deals…"*; ability words — *"Scavenge the Dead —"*;
and static cost-reducers — *"Equip abilities you activate cost {1} less"*,
which are **not** equip lines). The surviving **194**:

| keyword | lines | belongs on | printed |
|---|--:|---|---|
| Ward | **53** | `becomes-targeted-trigger` | `Ward—Pay 3 life.` |
| Equip | **43** | `activated` | `Equip legendary creature {1}` · `Equip—Sacrifice a creature.` |
| Craft | 24 | `activated` | `Craft with artifact {1}{U}` |
| Cumulative upkeep | 23 | `upkeep-trigger` | `Cumulative upkeep—Pay 2 life.` |
| Champion | 12 | `etb` | `Champion a Kithkin` |
| Forecast | 11 | `activated` | `Forecast — {1}{U}, Reveal this card…` |
| Devour · Firebending · Echo · Cycling · Eternalize · Reinforce · Bloodthirst · Madness · Crew · Unearth · Exalted · Recover · Mobilize · Prowess · Modular | 28 | various | |

A further **1,757** parameterized keyword lines route to `static` — right answer,
wrong mechanism (Enchant, Protection, Affinity, Prototype, Morph, Suspend …).

### D5 — the replacement matcher's 60-character window is too narrow

`\bwould\b.{0,60}\binstead\b` misses **160 lines**. Measured gap between the two
words: **min 61 · median 89 · max 173.** Doubling Season (90), Soul-Scar Mage
(105), Embermaw Hellion (100). CR 614.1a makes "instead" definitional; the
distance to it is not.

### D6 — 30 activated abilities whose cost head has no mana symbol

The head test requires `{}` or one of six verbs, so these are lost:
`Put a -1/-1 counter on this creature:` (Barrenton Medic, Wall of Roots),
`Return a Forest you control to its owner's hand:` (Quirion Ranger),
`Remove two counters from Ghost-Spider:`, `Blight X, Return this enchantment…:`.
One is a false positive — a card *named* **"Ultimate Magic: Meteor"**, where the
colon is in the name.

### D7 — the permanent-side count is **9,235**, not 9,942 or 9,178

Both the original audit and my own fix record partitioned on the **root** type
line, which sides an Adventure creature's static ability with its instant half.
Face-aware, the number is **9,235** — 57 lines hidden. Examples: Rimrock Knight's
*"This creature can't block"*, Beanstalk Giant's P/T-setting static, Porcine
Portent's *"Boars you control get +1/+1."*

**The audit's partition is a lower bound on the defect population, not a split.**

### D8 — 29 semicolon-joined keyword lines *(logged in the fix record)*

`keyword_line_tokens` splits on commas only: *"Flying; banding"*,
*"Defender; reach"*, *"Trample; rampage"*.

### D9 — 1,229 lines blocked by 49 CR 702 keywords with no §2 home — **a Captain ruling, not a fix**

§2b says *"55 remain unrouted and are reported, never approximated."* Live count
is now **49** (the 6 the router fix closed), and the corpus cost has never been
measured before:

| keyword | lines | | keyword | lines |
|---|--:|---|---|--:|
| Flashback | **209** | | Warp | 37 |
| Partner | **129** | | Evoke | 36 |
| Foretell | 54 | | Rebound | 35 |
| Start your engines! | 46 | | Mutate | 34 |
| Bestow | 43 | | Plot · Escape | 66 |
| Buyback | 40 | | 39 more | 500 |

**Nearly all are alternative or additional CASTING COSTS** — Flashback, Buyback,
Evoke, Escape, Overload, Bestow, Foretell, Plot, Warp, Blitz, Dash, Emerge,
Mutate, Replicate, Casualty, Awaken, Aftermath. §1 omits DELIVERY for spell
abilities, and CR 601.2b makes a casting modifier not an ability of the
permanent at all.

**This is the same question as the spell-or-static audit's group C** (68 *"As an
additional cost"* lines), which it already flagged as needing a Captain call.
**It is ONE ruling covering ~1,300 lines, and it is the largest single open
vocabulary question under `spell-or-static`.**

---

## 3. THE EXHAUSTIVE PARTITION — and why step 2 is unsafe

Every one of the 9,235 permanent-side lines, face-aware, with D1 corrected
locally so the numbers are real. **Each bucket has a decision rule and a CR
anchor. The residual is named, not swept.**

| bucket | lines | CR |
|---|--:|---|
| bare STATEMENT static | **3,585** | 113.3d |
| as-long-as static | 864 | 113.3d |
| attached-object static (Aura/Equipment) | 58 | 113.3d |
| "attacks/blocks each combat if able" | 77 | 508.1 |
| imperative static sentence | 371 | 113.3d |
| other statement | 692 | 113.3d |
| **↑ the REAL step-2 target** | **≈5,647** | |
| **LOYALTY ability** | **900** | 606.1 |
| **modal MODE, header carries a delivery** | **504** | §1 multi-axis |
| **CR 702 keyword line → non-`static`** | **194** | 702.Na |
| **REPLACEMENT** | **165** | 614.1a–c |
| **TRIGGER-shaped** | **90** | 113.3c |
| **ACTIVATED, unquoted colon** | **30** | 113.3b |
| **↑ WOULD BE MISROUTED BY A BLANKET SWEEP** | **1,883** | |
| CR 702 keyword line → `static` (right answer, wrong mechanism) | 431 | 702.Na |
| modal mode, header carries none | 127 | |
| additional cost | 68 | 601.2b |
| unrouted-keyword lines (D9) | ≈1,229 | — |

**Step 2 as written — *"route bare permanent statics to `static`, ~7,976
lines"* — would put 1,883 lines onto a token the CR contradicts for every one of
them.** Worse, `static` is a *ratified* token, so unlike `spell-or-static` those
1,883 would report as **resolved** and no census could ever surface them. That
is the Unearth failure the router fix just corrected, at 33× the scale.

**And 7,976 was never the right target number.** The real static population is
**≈5,647**.

---

## 4. RECOMMENDED ORDER — each its own measured pass

Cheapest and safest first, D1 mandatory before anything else because it is
upstream of every classifier.

| # | work | lines | needs Captain? |
|---|---|--:|---|
| 1 | **D1 ABILITY_WORD → em-dash only** | 556 (frees 90 triggers) | no — one regex, CR 207.2c |
| 2 | **D2 loyalty**, hoisted out of the cost gate | 900 | no — ratified token, CR 606.1 |
| 3 | **D4 parameterized keyword lines** | 194 + 1,757 | no — §2b already ratified |
| 4 | **D3 modal modes** via `expand_modal_bullets` | 504 | no — standard ratified 2026-07-31 |
| 5 | **D5 window · D6 colon head · D8 semicolons** | 160 + 30 + 29 | no |
| 6 | **THEN step 2**, against the corrected partition | ≈5,647 | no |
| 7 | **D9 casting modifiers** + group C | ≈1,300 | **YES — one ruling** |

Re-run the name-invariance test after each pass. It is corpus-wide, needs no
ground truth, and it caught in one run what four sessions of sampling did not.

---

## 5. WHAT THIS AUDIT PROVES

**The tidy check was wrong twice, and Gate 4 caught both.** Once in the router
fix (the "class always decides the slot" generalisation would have destroyed 16
ratified `replacement` routings), and once **in this audit's own harness** — the
first name-invariance run reported 195 defects and 132 were my rename's fault.
*A check disagreeing with the code is not evidence the code is wrong.*

**Recall, not precision, is where everything was hiding.** Nine defects, and not
one of them shows up as a wrong answer on a line the tooling classifies. They
are all lines the tooling never classified — and the reports are built from what
it *did* classify.

**A ratified standard sitting unimplemented is invisible to every gate.**
`expand_modal_bullets` has been ratified since 2026-07-31, is written, is
correct, and the shape extractor has never called it. Nothing checks that a
ratified standard has a caller. **That is a gap worth its own check**, because
it cost 504 lines here and there is no reason to think it is the only one.

**"Blind by construction" has a second instance, and it is worse than the
first.** `spell-or-static` at least reads as *unresolved*. Sweeping those lines
to `static` would make 1,883 wrong answers read as *resolved* — converting a
visible gap into an invisible one. **The fallback bucket is not the danger; a
ratified bucket used as a fallback is.**
