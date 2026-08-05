# WORK PACKETS — scoped for LOW-CONTEXT sessions (2026-08-07)

**Why this file exists.** Every foundry session currently pays a large
fixed cost on turn one: `CLAUDE.md` whole, the handoff whole, and
`CODEBOOK-NAMING-GRAMMAR.md` **whole**. That cure is correct and earned — but
it is charged per session, and most remaining items do not need all of it.

This file front-loads that cost ONCE. Each packet below carries the governing
rulings **quoted inline**, so a session can work the item without going to find
them. Written 2026-08-07 with full context loaded, precisely so later sessions
do not have to load it.

> **This file is a convenience, not a new law.** If a packet's inline quote
> disagrees with the source document, **the source wins and this file is
> wrong** — say so and correct it. Everything here was verified live on
> 2026-08-07; numbers drift, rulings do not.

---

## 0. THE CONTEXT TIERS — and the one thing Captain must ratify

**PROPOSED, NOT RATIFIED.** CLAUDE.md currently says the whole-grammar read is
required before *"any work on the codebook, the grammar, the tier engine or the
foundry."* The extractor is foundry, so today that is a full read every time.

The rule's own stated reason is narrower than its scope:

> *"Three separate errors on 2026-08-02 came from encoding one section's law
> while §7, §12a or a batch ruling governed the same slug — two of them would
> have destroyed Captain-ratified names."*

**That failure mode is about SLUGS AND NAMES.** A pass that mints no name,
ratifies no vocabulary and mutates no codebook cannot hit it. So:

| tier | when | turn-one read |
|---|---|---|
| **A** | extractor/DET fix that mints NO vocabulary and touches NO codebook | Gate 1 pointer + Gate 2 + this packet. **No whole-grammar read.** |
| **B** | as A, but the pass may propose a §2 token | A + the named grammar sections in the packet |
| **C** | anything naming, renaming, or mutating the codebook | **Full CLAUDE.md + grammar WHOLE, unchanged.** No exceptions |

**Captain: tier A is the only thing here needing your word.** If you decline it,
every packet below still works — sessions just pay the full read. Nothing else
in this file depends on it.

**The tier-A tripwire.** If a tier-A session finds itself wanting to *name*
anything, it has left tier A. Stop, log the proposal, do not name it.

---

## 1. PACKET INDEX

| # | packet | tier | cost | blocked? |
|---|---|---|---|---|
| **W1** | Trap sweep — AUDIT-5 findings 3 & 5, then the sweep | A | 1 session | ✅ **DONE** — `docs/W1-W2-RECORD.md` |
| **W2** | CR 706.3b die-row routing | A | small | ✅ **DONE** — `docs/W1-W2-RECORD.md` |
| **W3** | **935** `unclassified-trigger` → Batch API | — | $ not quota | no |
| **W4** | The anthem group (**4,375** decidably static — re-measured) | B | 1–2 sessions | no |
| **W5** | `escapes with` (12 lines) | B | small | no |
| **W6** | Family sweep — the standing 6 | C | 1 session | no |
| **W7** | Definition drift — the standing 35 | C or Batch | 1 session | no |
| **W8** | Decision sheet — 9 items | — | Captain only | **yes** |
| **W9** | Parent layer (schema pass, step 7) | C | arc | **yes — W8 first** |
| **W10** | Display build (step 8) | — | arc | **yes — W9 first** |

---

## W1 — TRAP SWEEP  ·  TIER A  ·  ✅ DONE

> **CLOSED. Full record: `docs/W1-W2-RECORD.md`.** Both findings
> fixed, all three sweep classes run and stated (class 1: one dead-code site,
> 0 lines; class 2: three sites, 8 lines; class 3: nothing, and the
> measurements proving it). 92 lines moved in total.
>
> **The packet missed a prerequisite, and it mattered.** Finding 3 applied on
> its own DESTROYS a ratified `any-death-trigger` on Predatory Sludge while
> `diff --strict` exits 0 — the CR 603.11 split gated on the token spelling
> `static` instead of the CR class, so it refused every `replacement` line.
> That fix (`46c7beb`) had to land first. See §2a of the record.

**(original packet text retained below for reference)**

**GOAL.** Two known defects, then sweep for their whole class. The sweep is the
job; the two lines are the worked examples.

**READ.** This packet. Nothing else.

**THE TWO KNOWN DEFECTS, verbatim from `AUDIT-5-2026-08-05.md`:**

*Finding 3 — 25 lines.* The replacement branch tests
`^as (?!an additional cost|long as)\b…`. After canonicalization the line reads
`as ~ enters`, and **`~` is not a word character**, so the `\b` after `as `
cannot match. Loses 25 CR 614.1c replacements — `Stenn, Paranoid Partisan`,
`Pramikon, Sky Rampart`. **Fix: drop the `\b`.**

*Finding 5 — 43 lines.* `\benters\b` in the etb trigger test misses the plural:
`Whenever one or more creatures you control ENTER`. `Kotis, Sibsig Champion`,
`Builder's Talent`, `Anje, Maid of Dishonor`. **Fix: `\benters?\b`.**
`etb` is the largest trigger family (5,713) — **read the whole diff.**

**THE SWEEP — this is the actual deliverable.** Grep every branch in
`foundry_shape_extractor.py` for:

1. **`\b` adjacent to `~`.** Already fixed at two sites, live at a third.
   *A trap fixed at two sites and not swept is a trap that is still live.*
2. **Any singular/plural or inflected verb test** — `enters`/`enter`,
   `dies`/`die`, `attacks`/`attack`. Fourth instance in four sessions.
3. **Separators and symbol variants, not just verbs.** The newest instance was
   punctuation: the die-row range separator prints as em-dash (75), hyphen (5)
   and not at all (26).

**DO.**
```
python3 experiments/foundry_routing_regression.py snapshot experiments/out/foundry/regression/w1-before.json
# ... make ONE fix ...
python3 experiments/foundry_routing_regression.py snapshot experiments/out/foundry/regression/w1-after.json
python3 experiments/foundry_routing_regression.py diff  experiments/out/foundry/regression/w1-before.json experiments/out/foundry/regression/w1-after.json --strict --lines
```

**VERIFY after each fix — all of it, every time:**
```
python3 experiments/foundry_routing_regression.py invariance --strict
python3 experiments/foundry_punctuation_audit.py
python3 experiments/foundry_visibility_audit.py
python3 experiments/foundry_ground_truth.py
```

**READ EVERY MOVED LINE.** `diff --strict` halts only on `ratified → None`.
A GAP CLOSED and a RE-ROUTE both print and pass, and *improving recall can hand
out a WRONG ratified token* — that is what `foundry_ground_truth.py` is for, and
it is why it runs after every step and not just at the end.

**BOUNDARY.** No new vocabulary. No codebook mutation. If a fix seems to need
either, log it and move on.

**DONE WHEN.** Both findings fixed, all three sweep classes grepped with the
result stated (including "found nothing" — that is a result), every moved line
read, all gates green, committed.

---

## W2 — CR 706.3b DIE-ROW ROUTING  ·  TIER A  ·  ✅ DONE

> **CLOSED. Full record: `docs/W1-W2-RECORD.md`.** 119 rows now inherit;
> 78 lines moved; uncontexted die rows 2 → 0.
>
> **The packet's "expect zero re-routes" was wrong, and the exceptions were
> the point.** Two rows already carried a ratified token and BOTH were wrong
> — Cone of Cold `replacement` (a sorcery's spell ability, §1 default) and
> Delina `static-grant` (read off a granted ability in quotes). Cone of Cold
> is a deliberate `ratified → None`. That is why the inheritance is
> UNCONDITIONAL, unlike the modal branch.
>
> **Three further defects, none in the packet:** a bar row must outrank the
> modal test (a bullet must not); the SAME bug was live in the ratified DET
> join; and `_DIE_ROW_RE` knew three range forms when there are five —
> `20+ |` and `9 or less |`. The old census could not have found the last one:
> it counted only rows the regex already matched.

**(original packet text retained below for reference)**

**GOAL.** ~99 die-roll result rows parse alone and are unrouted. The DET *join*
is already done (`3ff3afd`); this is the *routing* half.

**THE RULING, verbatim (CR 706.3b):**

> *"An instruction to roll one or more dice, any instructions to modify that
> roll printed in the same paragraph, any additional instructions based on the
> result of the roll, and **the associated results table** are **all part of one
> ability**."*

**So a row should INHERIT the roll ability's delivery**, exactly as a CR 700.2
mode inherits its header's. **No vocabulary needed.**

**WHERE.** The mechanism is D3 inheritance in `deliveries_for_lines`
(`foundry_shape_extractor.py`). The modal case is the worked example, sitting
right there — a bulleted mode under a modal header yields
`[(t, f"modal-mode:{d}") for t, d in header_deliveries]`.

**BOUNDARY.** Inheritance only. If a row seems to need its own token, stop.

**VERIFY.** Same block as W1. Expect ~99 lines `None → <the roll ability's
token>` and **zero** re-routes.

---

## W3 — 988 `unclassified-trigger` → BATCH API  ·  NOT a Claude Code session

**GOAL.** The largest named gap. **988 lines, 278 distinct shapes, 174 of them
singletons.** This is a CR-lookup job, not a judgement job — which is why it
batches.

> **RE-MEASURED AFTER W1 — the table below is SUPERSEDED.** The 88-line top
> shape WAS the plural-`enter` defect and **dissolved entirely**;
> `unclassified-trigger` is now **935 lines** (was 988). Current top shapes
> and the shape-key boundary are in `docs/W1-W2-RECORD.md` §6.
> Re-measure again before costing — do not batch off either table.

**THE TOP SHAPES, measured 2026-08-07 — SUPERSEDED, see above:**

| n | shape | likely CR home |
|--:|---|---|
| 88 | `whenever one or more …` | **overlaps W1 finding 5 — RUN W1 FIRST** |
| 54 | `whenever you draw your second card each turn` | — |
| 43 | `whenever you draw a card` | — |
| 31 | `whenever this creature mutates` | CR 702.140 |
| 29 | `when you unlock this door` | Rooms |
| 24 | `when you control no …` | — |
| 21 | `whenever a creature you control deals combat damage` | — |
| 20 | `whenever an opponent draws` | — |
| 19 | `whenever this creature deals damage` | — |
| 19 | `whenever you put one or more +1/+1 counters` | — |
| 19 | `when this creature exploits` | CR 702.109 |
| 18 | `whenever you commit a crime` | CR 701.x |
| 16 | `eerie — whenever an enchantment you control enters` | CR 207.2c ability word |
| 15 | `whenever you activate an ability that isn't a mana ability` | — |

**RUN W1 FIRST.** The 88-line top shape is the plural-`enter` defect; fixing it
may dissolve a chunk of this population for free. **Re-measure before batching.**

**THE BRIEF SHAPE.** Input: the 278 shapes + CR 701 and CR 702 text. Output:
**a table only** — `shape | CR rule | proposed token | one-line justification`.

**Forbid prose.** The saving is only real if what comes back is small: a
278-row table costs almost nothing to reconcile, ten pages of reasoning about
it costs more than doing it here would have.

**PROVENANCE.** Output is `llm`-class — *discounted, never gate-bearing*.
It comes back as a **proposal set** and rides the existing loop:
`/triage-alpha N → /triage-beta N → Captain annotates → /triage-emit N`.
Seven batches have gone through it. **This is batch 8; it is not a new
mechanism.**

**BUDGET.** Batch API, **$49.49 remaining of $140** — a separate wallet from
the weekly Claude Code quota. Cost estimate from CURRENT pricing docs + Captain
go-ahead before submitting. **Never remembered prices.**

---

## W4 — THE ANTHEM GROUP  ·  TIER B  ·  the big one

**GOAL.** The largest real slice: **4,481 lines that CR 113.3a decides are
statics** and that simply have no branch yet.

**HOW TO SEE THEM** (this reporter is new — `27bbf43`):
```
python3 experiments/foundry_shape_extractor.py --gaps
```
and read the section headed **`INSIDE spell-or-static`**. It splits the bucket
by CR 113.3a and ranks the shapes with card counts.

**THE CUT, and why it needs no vocabulary.** CR 113.3a: a spell ability
functions only while the spell is on the stack, and a spell is an instant or a
sorcery. **A card with no instant/sorcery face leaves CR 113.3's four-category
enumeration closed on `static`.** `_has_spell_face()` already implements it.

**TOP SHAPES:** `creatures you control` 167/165 cards · `other creatures you`
72/71 · `each creature you` 59/58 · `this spell costs` 100 · `during your turn`
92 · `as an additional` 66.

**PRIOR ART — read before starting, it is short and it is the method that
works:** `STEP-2A-STATIC-GRANT-2026-08-05.md`, `-2B-STATIC-CONDITION-`,
`-2C-SELF-STATEMENT-`.

**THE STANDING WARNING, from `PRE-STEP-2-AUDIT`:** routing `spell-or-static`
wholesale into `static` *"would turn 1,883 wrong answers into answers that READ
as resolved."* **Take named shapes, one at a time. Never a blanket sweep.**

**`rule:tribal-anthem-buff` has a KEEP ruling reconfirmed in batches 4, 6 and 7,
and nothing rules its DELIVERY — so this is routing, not vocabulary.**

---

## W5 — `escapes with`  ·  TIER B  ·  12 lines

CR 113.6h chains to CR 614.12. Reasoning is already written up in
`STEP-2C-SELF-STATEMENT-2026-08-05.md` §2b. Needs its own pass; small.

---

## W6 — FAMILY SWEEP, the standing 6  ·  TIER C

Unchanged for several sessions. `python3 experiments/foundry_family_sweep.py --strict`

```
[family-members-contradict-template]  activated-tap-or-untap-<scope>
[family-members-contradict-template]  targeted-<action>-<class>
[pattern-misses-cardname-token]       rule:forced-attack-each-combat
[ratified-pattern-has-no-axis]        rule:cant-be-blocked-as-long-as-state
[ratified-pattern-has-no-axis]        rule:cant-be-blocked-by-power
[ratified-pattern-has-no-axis]        rule:cant-be-blocked-except-by-count
```

**TIER C because three of them are naming questions.** `ratified-pattern-has-no-axis`
is the recorded *"a ratified standard with no caller"* shape — a pattern exists,
the axis it would populate does not.

**MANDATORY:** `python3 experiments/foundry_slug_dossier.py <slug>` on **the name
you are about to WRITE**, not the one you started from. 23% of active axes have
their rulings filed under a former name.

---

## W7 — DEFINITION DRIFT, the standing 35  ·  TIER C, or batchable

`python3 experiments/foundry_definition_drift.py` → 35 findings across 359 axes:
**C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3.** Report lands in
`experiments/out/foundry/definition_drift_report.json`.

C4 is the §6a check (scope / targeting / ownership). **§6a is axis identity, not
a facet** — `target` only where the card prints "target"; `any-` must mean any;
`another` excludes the source.

**This one batches well** (rewriting a definition to match its ratified scope is
a bounded language task), but the *ratification* is tier C.

**Note:** this number moved 35 → 34 → 35 across one session because DET
expansions change which patterns hit. **Re-measure; do not carry it forward.**

---

## W8 — DECISION SHEET — CAPTAIN ONLY, 9 items

Nothing below blocks W1–W7.

| # | item | the question |
|---|---|---|
| **1** | **`REMINDER-TEXT-DET-CONFORMANCE-2026-08-07.md`** — 167 memberships | **NEW.** 148 are decided by §6a already and need only authorising. **The 19 class-C are the real call**: true facts whose only evidence is reminder text. Recommend C1 (remove) |
| 2 | Refresh `docs/mtg-comprehensive-rules.md` | vendored snapshot is behind the corpus (`Chorus`) |
| 3 | `main-phase-unqualified` (n=1) | does a 1-member shape earn a token? |
| 4 | `to-graveyard-zone-unstated` (n=11) | per-card, CR 110.1 decides each |
| 5 | Five logged migrations | codebook mutation + backup law |
| 6 | `rule:postcombat-main-phase-trigger` | 2 of 10 cards — membership addition |
| 7 | §2a prefix-stripping anchor | `any-` means two things; a blind stripper corrupts four names |
| 8 | `start your engines!` / 43 homeless keywords | one ruling on the CLASS, not 43 fixes. Moves the pinned `keyword_homes = 150` guard |
| 9 | **Tier A above** | may a no-naming extractor pass skip the whole-grammar read? |

---

## W9 — PARENT LAYER (step 7)  ·  BLOCKED on W8  ·  TIER C

Scoped in conversation 2026-08-07. **The three rules that constrain it, so the
next session does not have to rediscover them:**

**S1 — parents are DERIVED.** *"Union of ratified children computed at
index-build time, plus an explicit direct-member list for cards no child
captures. Cards are never hand-tagged with both child and parent."*
→ **An LLM pass may propose parents and CHILD EDGES. It may never emit a card
list.** Membership is computed, not assigned.

**S4a — parent edges are UNRANKED AND EQUAL.** No primary parent, no confidence
weight. Worked case: **Monstrous Rage** is a combat trick *and* an
enchantment-deck card, both at full strength. Which matters is a property of the
deck being built, not the card. *"Parent TREE" is a misnomer — it is a lattice.*

**S6 — parent names are the USER-FACING vocabulary.** Lifegain, landfall,
tokens, ramp, wheels, edicts. *Ruthless naming audit on parents, lenient on
children.*

**THREE OF EIGHT LOGGED CANDIDATES CANNOT BE AUTHORED**, and no amount of rules
work changes it: `punishes-attacking-you`, `saga-payoff`, `end-step-payoff` have
**0 children and 0 members**, because their intended children are ratified
**delivery tokens, not axes**. That is Decision 1 in
`PARENT-LAYER-OPENING-PACKET-2026-08-04.md` and it is open.

**MEASURED CANDIDATES:** `lifegain-payoff` 171 · `attack-payoff` 153 ·
`sacrifice-payoff` 132 · `precombat-setup` 64 · `discard-payoff` 56.

**TWO TRAPS, both already paid for:**
- **Sort by SENSE, never by string.** A name-match on `counter` returned 11
  axes / 104 members and most was garbage — +1/+1 counters vs countering spells
  vs energy counters. Same failure as CDR-09.
- **~Zero child overlap is the RIGHT answer.** The parent exists to group cards
  that share no child. Same-card co-occurrence remains the wrong test.

**ON THE RESEARCH PASS.** Archetype *vocabulary* (lifegain, landfall, tokens) is
free and feeds S6. Per-card *deck data* is **option B of the open S7 question** —
a new external source touching *"no card data in git, ever."* Phase 3.3 already
has the landing slot: *"the merge step accepts any extra oracle_id-keyed JSON
file."* Approval, not redesign.

---

## W10 — DISPLAY BUILD (step 8)  ·  BLOCKED on W9

Not started. `CORPUS-PASS-PLAN.md`'s status table is **stale** — dated
2026-08-01, and it still says the codebook write is pending. It happened:
`codebook.json` is `foundry-codebook/2`, batches 1–7 reconciled.

---

## 2. LIVE STATE at packet time — RE-MEASURE, DO NOT CARRY FORWARD

```
ability lines 61,383 · deliveries 61,952 · keyword homes 150
routed to a ratified token   45,481   74.1%
grammar §1 unmarked default  10,413   17.0%   (correct, not a gap)
RESOLVED                     55,894   91.1%
REAL GAP                      5,489    8.9%   = 4,481 static + 1,008 named
codebook 565 axes / 359 active / 8,740 members — lint clean
```

*A carried-forward count is not a measurement.* Every number here was live on
2026-08-07; run the gates.

**AFTER W1 + W2 — re-measured, and this block supersedes the one above:**

```
ability lines scanned        61,961 · keyword homes 150 (never moved)
unclassified-trigger            935   was 988    (−53)
linked:unclassified-trigger      38   was  34    (+4, rows that came into
                                                  existence — see the record §2a)
INSIDE spell-or-static       14,864   was 14,898
  undecidable (§1 default)   10,413   70.1%      unchanged
  decidably STATIC            4,451   29.9%      was 4,485  (−34)
```

**W4's target is 4,375, not 4,481. W3's is 935, not 988.** Both were moved by
W1/W2 and neither should be read off the block above.
