# SESSION HANDOFF — 2026-08-08

Supersedes `SESSION-HANDOFF-2026-08-07-EVE.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** 8 commits, `1bc8025` .. `HEAD`.

**The session in one line: W1 and W2 were reviewed, then W3 was worked — and
W3 turned out not to need the Batch API it was scoped for. Deriving it from
the CR instead cost $0, routed 119 lines, found twelve defects including one
wrong ratified token and one INVENTED trigger, and left a nine-item decision
sheet where a 935-line batch job used to be.**

**NEXT SESSION'S JOB: §6. Either W8 (Captain's sheet, now 10 items) or W4 —
and W4 is the biggest remaining slice at 4,375.**

---

## 0. START HERE

`docs/SESSION-START-PROCEDURE.md` — five gates, Gate 2 is EIGHT commands.
If no task was given, §6's NEXT WORK ITEM is your instruction. Only two things
need Captain's explicit word: **ratifying new vocabulary** and **mutating the
codebook**.

---

## 1. READING MANIFEST — indexed by TASK

### Always

| | |
|---|---|
| **`python3 experiments/foundry_system_map.py`** | **RUN FIRST.** Five stages; which list is CR-parsed vs heuristic. Generated, cannot go stale |
| **`docs/OUT-OF-SCOPE.md`** | a DECLINE register, not a backlog. Attractions/`Visit` appears in W3's population — report it *declined* |
| `docs/SESSION-START-PROCEDURE.md` | five gates |
| `CLAUDE.md` | locked rules + traps — **6 new this session** |
| Gate 2, all eight | live state is measured, never recalled — §3 |

### If you are touching the DELIVERY EXTRACTOR

```
python3 experiments/foundry_prior_art.py <your topic>      # ← FIRST, always
python3 experiments/foundry_routing_regression.py snapshot experiments/out/foundry/regression/<name>.json
python3 experiments/foundry_routing_regression.py diff <before> <after> --strict --lines
python3 experiments/foundry_routing_regression.py invariance --strict
python3 experiments/foundry_ground_truth.py                # after EVERY step
```

| read | why |
|---|---|
| **`docs/W3-TRIGGER-VOCABULARY-2026-08-07.md`** | **NEW.** The CR partition, the twelve defects, and the D1–D9 decision sheet |
| **`docs/W1-W2-RECORD.md`** | the sweep classes this session extended |
| `docs/WORK-PACKETS-2026-08-07.md` | W3's row and section are updated; **its original numbers are superseded twice over** |
| `docs/AUDIT-5-2026-08-05.md` | findings 3 and 5 are CLOSED (W1) |
| `docs/CODEBOOK-NAMING-GRAMMAR.md` **§1, §2, §2a, §2b, §2c, §2f, §6a, §8a, §8b, §11** | the DELIVERY law. **§2b + §8b + §11 are what D2/D3's one-family recommendation rests on**; §8a is what fixed the census's homograph defect |
| `docs/DELIVERY-GAP-CENSUS-2026-08-03.md` | the census; `--gaps` reports inside `spell-or-static` too |

### Other tasks

- **CODEBOOK / AXIS / SLUG** — grammar **WHOLE** · `PARENT-TREE-CANDIDATES.md` ·
  `FAMILY-TREE-EVIDENCE.md` · `TRIAGE-BATCH-1.md`..`-7.md`, and
  `foundry_slug_dossier.py` on **the name you are about to WRITE**.
- **KEYWORDS** — `KEYWORD-LEDGER-CANDIDATES.md`. Membership tests use
  `CR_KEYWORD_NAMES`, never `KEYWORD_HOME`.
- **PARENT layer** — `PARENT-LAYER-OPENING-PACKET-2026-08-04.md` · §6b ·
  `S7-GATE-NOT-RUNNABLE-2026-08-05.md`.

### New mechanism

| | |
|---|---|
| **`experiments/foundry_w3_census.py`** | partitions every unrouted trigger line by the CR rule that decides it. Mints nothing, judges nothing, reports RESIDUAL rather than forcing a fit. `--residual`, `--class <name>` |

---

## 2. WHAT PROMPTED THIS

Captain asked for a review of W1/W2 and then an attempt at W3. W3's packet
scoped it as a Batch API job. **Its own justifying sentence is the argument
against it:**

> *"This is a **CR-LOOKUP JOB**, not a judgement job — which is why it
> batches."*

A CR-lookup job is what a DET tool does, and CLAUDE.md's central rule is
*"NEVER TRANSCRIBE THE CR — DERIVE FROM IT AT RUN TIME."*

---

## 3. GATE 2 — eight commands, all green

```
lint                clean — 565 axes · 8,740 members · NO MUTATION this session
family sweep        the standing 6 blocking
definition drift    the standing 35
ruling registry     clean (regenerated)
conservation        0 violations · baseline re-pinned 4× ON PURPOSE, see §5
visibility          0 dropped · 0 unscanned · 31 uncontexted · 0 face spans
ground truth        488 / 488 — UNCHANGED THROUGH ALL TWELVE FIXES
gate audit          5,676 out · 114 CR members attested only outside · 0 crashes
invariance          0
```

---

## 4. LIVE STATE — measured at handoff

| | |
|---|--:|
| ability lines | 61,383 |
| deliveries | **61,960** (was 61,961 — one FABRICATED row removed, §5) |
| **`unclassified-trigger`** | **816** (was 935 at W1/W2, 988 at packet) |
| …CR-classified by `foundry_w3_census.py` | **719 · 88.1%** |
| …residual | 97 lines / 93 cards / ~85 distinct clauses |
| `linked:unclassified-trigger` | 38 (unchanged) |
| unrouted lines | **15,678** (was 15,744) |
| `spell-or-static` | 14,747 → undecidable 10,372 (70.3%) · **decidably STATIC 4,375** |
| keyword homes | 150 — never moved |
| codebook | **565 axes / 8,740 members — UNTOUCHED** |

---

## 5. THE TWELVE DEFECTS, and the two that only one number could see

Full record: `docs/W3-TRIGGER-VOCABULARY-2026-08-07.md`.

**Six were branches that could not see a printed form of a token they ALREADY
HAD** — CR 400.7 determiner hand-list (15) · CR 106.12 active voice (32) ·
contracted copula (8) · CR 506.3 passive (6) · CR 120.1 noun-first (3) ·
CR 708.7 active voice (1). Plus CR 106.12a's typed second clause (2).

**VOICE and WORD ORDER are now named sweep classes** beside W1's INFLECTION,
with a rule for finding the next one: **the CR states the same event in the
active voice ONE RULE ABOVE the trigger rule.** 106.12 above 106.12a, 506.3
above 508, 708.7 above 708.8. The class was then **swept and came back
clean** — ten of fifteen probes measure zero.

**Three were the compound splitter**, and they point opposite ways: an `or`
inside an OBJECT phrase or a CR QUANTITY phrase LOSES a real token (5 lines);
an `or` inside a `while` condition (CR 603.4) **INVENTS a trigger that does
not exist** (1 line).

> **THE THING TO CARRY FORWARD.** Every one of those emitted
> `[etb, unclassified-trigger]` — the line kept a ratified token, so
> `diff --strict` scored it a **re-route** and `unrouted_lines` never moved.
> Only `deliveries` and `descriptor_unrouted.*` can see a row-level loss on a
> routed line. **A census scores a lost token and an invented gap
> identically.**

**One wrong ratified token was removed** — Lich read `any-sacrifice-trigger`,
taken off its *effect* text (CR 113.3c).

**One fix was measured and REJECTED**, recorded in the code so it is not tried
a third time: reusing `trigger_condition`'s enumeration rule inside
`trigger_clause` scores 1 gain / **3 regressions** and the diff halted on it.
`_ENUM_CONT` cannot tell "A, B, or C" from "when X, or when Y". Keeper of
Progenitus stays an honest gap.

**Baseline re-pinned four times, every one deliberate and stated:**
`to-graveyard-zone-unstated` 11→12 (Patron of the Nezumi joins §2f's pending
list) · the two new `*-damage-recipient-unstated` metrics · `deliveries`
61,961→61,960 (a **fabricated** row deleted; conservation's own law passes
unchanged).

---

## 6. NEXT WORK ITEM

**Take one of these two. Both are ready; neither is blocked.**

### A. W4 — the anthem group · TIER B · the biggest remaining slice

**4,375 lines** that CR 113.3a decides are statics with no branch yet.
`python3 experiments/foundry_shape_extractor.py --gaps`, read the section
headed `INSIDE spell-or-static`. Prior art is short and is the method that
works: `STEP-2A-STATIC-GRANT-2026-08-05.md`, `-2B-`, `-2C-`.

**The standing warning, from `PRE-STEP-2-AUDIT`:** routing `spell-or-static`
wholesale into `static` *"would turn 1,883 wrong answers into answers that
READ as resolved."* **Named shapes, one at a time. Never a blanket sweep.**

### B. W8 — Captain's decision sheet, now **10 items**

Item 10 is W3's D1–D9. **Recommend D4 first** — CR 603.8 state triggers, a
closed CR category with a CR-supplied term of art, 50 lines, and ratifying it
also shrinks W3's residual. **D2/D3 recommend ONE grammar family, not 41
tokens** (§2b + §8b + §11). D9 is ruled-not-ratified and needs no action.

### Then, in order

W5 `escapes with` (12 lines) · W6 family sweep (the standing 6) · W7
definition drift (the standing 35).

**Also still open, logged not started:** the **117 single-faced instants and
sorceries routing to `replacement`** — the `replacement` branch has no
spell-face gate (W2 addendum §3). It needs a per-FACE cut, which is real
design, not a one-line gate.

---

## 7. BLOCKED ON CAPTAIN

**W8, now ten items.** The nine standing ones are unchanged (reminder-text
conformance 167 memberships · CR refresh · `main-phase-unqualified` ·
`to-graveyard-zone-unstated`, **now 12 not 11** · five logged migrations ·
`rule:postcombat-main-phase-trigger` · §2a prefix anchor · `start your
engines!` · tier A). Item 10 is W3's sheet.

**No new CR-LAG entry.** `commit a crime` was one step from being filed as a
third, on a grep returning zero — the CR states it as a **gerund**
(*"committing a crime"*, CR 700.13). The register still stands at two:
`chorus`, `N or less`.

---

## 8. WHAT THIS SESSION PROVES

**A `llm` PROPOSAL SET IS STRUCTURALLY BLIND TO A CLASSIFIER DEFECT.** It is
shown *shapes* and asked to name them, so it can only ever report gaps. Six of
this session's twelve defects were branches failing to see a printed form of a
token they already had; one was a *wrong* token; one was an *invented* gap.
**A proposal set names gaps; only reading the classifier finds the ones that
are not gaps.**

**THE PACKET'S OWN JUSTIFICATION WAS THE COUNTER-ARGUMENT.** "A CR-lookup job,
not a judgement job" is the definition of DET work. Read a scoping decision's
reasoning before accepting its instrument.

**A PROBE DEFECT IS STILL THE DEFAULT OUTCOME — three more, all in the census
script**, all caught before their numbers were used: bare `-ed`/noun matches
scoring `enchanted player` and `has flying` as keyword events; `counters`
(noun plural) read as CR 701.6's verb, fixed by encoding **§8a's ratified
test** rather than inventing one; and the keyword classes tested first,
stealing from the specific CR rules. Sixteen across four sessions.

**"FOUND NOTHING" IS A RESULT, AND SO IS "REJECTED".** Ten of fifteen voice
probes measure zero, and the enumeration fix was measured, halted on, reverted
and written into the code as a rejection with its numbers. Both are stated
rather than omitted.
