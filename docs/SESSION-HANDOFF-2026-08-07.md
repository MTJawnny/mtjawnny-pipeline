# SESSION HANDOFF — 2026-08-07

Supersedes `SESSION-HANDOFF-2026-08-06.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** Nine commits, `98af57a` .. `3ff3afd`.

**The session in one line: stage 2's ability-word strip turned out to be a CR
enumeration (CR 207.2c), and pulling that thread opened the whole IN-CARD
SEPARATION class Captain named — modes, striations, levelers, stations, die
tables — 191 gap lines closed, 0 regressions, and two new standing mechanisms
that report failures nothing in this repo could see before.**

**NEXT SESSION'S JOB IS THE TRAP SWEEP. It is §4. Start there.**

---

## 0. START HERE

`docs/SESSION-START-PROCEDURE.md` — five gates. **If no task was given, §4's
NEXT WORK ITEM is your instruction.** Only two things need Captain's explicit
word: **ratifying new vocabulary** and **mutating the codebook**.

---

## 1. READING MANIFEST — indexed by TASK

### Always

| | |
|---|---|
| **`python3 experiments/foundry_system_map.py`** | **RUN FIRST.** Five stages, and which of each stage's lists is CR-parsed vs heuristic. Generated, so it cannot go stale. Ends with the one question that finds defects here |
| **`docs/OUT-OF-SCOPE.md`** | **NEW — a DECLINE register, not a backlog.** Attractions/`Visit`, art tags, Prototype. If it is there, report it *declined*, never *open* |
| `docs/SESSION-START-PROCEDURE.md` | five gates, short |
| `CLAUDE.md` | locked rules + traps (**12 new traps this session**) |
| Gate 2 commands | live state is measured, never recalled |

### Gate 2 has TWO new members — run all six

```
python3 experiments/foundry_codebook.py lint
python3 experiments/foundry_family_sweep.py --strict
python3 experiments/foundry_definition_drift.py
python3 experiments/foundry_ruling_registry.py
python3 experiments/foundry_punctuation_audit.py      # NEW — conservation
python3 experiments/foundry_visibility_audit.py       # NEW — option visibility
```

Both new ones exit 1 on failure and are safe to gate on.

### If you are touching the DELIVERY EXTRACTOR (the current work)

```
python3 experiments/foundry_prior_art.py <your topic>      # ← FIRST, always
python3 experiments/foundry_routing_regression.py snapshot experiments/out/foundry/regression/<name>.json
python3 experiments/foundry_routing_regression.py diff <before> <after> --strict
python3 experiments/foundry_routing_regression.py invariance --strict
```

| read | why |
|---|---|
| **`docs/AUDIT-5-2026-08-05.md`** | findings 3 and 5 are **still open** and are §4's job |
| **`docs/ABILITY-WORD-CR207-2026-08-06.md`** | CR 207.2c is a closed list; CR 207.2d licenses the one honest heuristic |
| **`docs/IN-CARD-SEPARATION-CENSUS-2026-08-06.md`** | **all eleven separation constructs, each against its own CR rule.** §9 is the visibility mechanism |
| **`docs/MODE-NAMES-CR700-2026-08-06.md`** | a mode is not an ability; improving recall can hand out a WRONG token |
| **`docs/PUNCTUATION-RESCAN-2026-08-06.md`** | conservation ≠ census; the two pre-existing recall gaps |
| `docs/CODEBOOK-NAMING-GRAMMAR.md` **§1, §2, §2a, §2b, §2e, §2f, §2g, §6, §9** | the DELIVERY law. **§2 is now 52 tokens**; **§2g is new** (kicker retired) |
| `docs/STEP-2A-…` · `-2B-` · `-2C-` | the three step-2 slices; the method that works |
| `docs/LINKED-ABILITIES-CR607-2026-08-05.md` · `docs/VOCABULARY-COMPLETION-2026-08-05.md` · `docs/CR-LAW-AUDIT-2026-08-05.md` | prior passes |

### Other tasks

- **CODEBOOK / AXIS / SLUG** — `CODEBOOK-NAMING-GRAMMAR.md` **WHOLE** ·
  `PARENT-TREE-CANDIDATES.md` · `FAMILY-TREE-EVIDENCE.md` ·
  `TRIAGE-BATCH-1.md`..`-7.md` — and `foundry_slug_dossier.py` on **the name you
  are about to WRITE**.
- **KEYWORDS** — `KEYWORD-LEDGER-CANDIDATES.md`; bare keywords are never axes.
- **PARENT layer** — `PARENT-LAYER-OPENING-PACKET-2026-08-04.md` · §6b ·
  `S7-GATE-NOT-RUNNABLE-2026-08-05.md`.

---

## 2. LIVE STATE — measured at handoff, not recalled

| | |
|---|---|
| codebook | **565 axes · 359 active · 8,740 members — UNCHANGED, no mutation this session** |
| lint | clean |
| family sweep | **6 blocking** (the same 6) |
| definition drift | **35** (was 35; dipped to 34 mid-session, see §3 note) |
| **§2 DELIVERY vocabulary** | **52 tokens** (was 53 — `kicker` retired, §2g) |
| **deliveries emitted** | **61,952** (was 61,945) |
| **unrouted** | **16,082** (was 16,273) |
| `spell-or-static` | **15,151** |
| keyword homes | **150** (unchanged all session) |
| **DET modal/table expansions** | **1,930** (was 1,755) |
| conservation audit | **0 violations** / 61,383 lines |
| visibility audit | **0 dropped · 0 unscanned · 33 uncontexted** |
| baseline snapshot | `experiments/out/foundry/regression/p24-join-after.json` |
| working tree | clean |

---

## 3. WHAT CHANGED — nine commits

**`98af57a` stage 2: the ability-word strip is a CR enumeration.** CR 207.2c
publishes all 61 ability words; `descend 4`/`descend 8` carry digits and
`council's dilemma` a curly apostrophe — the two things a shape could never
express were the two that were failing. CR 207.2d licenses the residual shape
because it says outright that flavor words are *not listed*. **29 lines.**

**`79bb334` conservation audit.** A census cannot answer *"did anything get
lost."* Text / sentence / ability conservation, all 0.

**`47083a6` mode names are flavor words.** The bullet is CR 700.2 list
punctuation. **22 lines** — and the 23rd was **wrong**, so the CR 113.3a closure
now refuses a bulleted line.

**`c2bd5d9` modal: CR 700.2 defines modality by the LIST.** **58 lines.** The
harness caught 2 regressions pre-commit; the refusal is now structural.

**`8cf0c3d` striations (CR 711.2 / 721.2 / 700.2i).** **82 lines.** Strip the
marker, do not claim the line — 7 re-routes said so.

**`24b369f` visibility audit.** Three layers; two had no reporter.

**`7b259af` decline register.** `docs/OUT-OF-SCOPE.md`.

**`3ff3afd` kicker retired (§2g) + join extended to CR 706.3b / 700.2h.**
0 lines moved on both, which is the proof each was correct.

> **Drift note, stated not smoothed:** definition drift read 35 → 34 → 35 across
> the session. The DET expansions change which patterns hit. It is not a routing
> regression, and the routing diff is 0 for those passes. Re-measure, don't
> carry this number forward.

---

## 4. NEXT WORK ITEM — the TRAP SWEEP. Proceeds WITHOUT asking.

**Do this first and do it as a SWEEP, not as two point fixes.** The handoff it
came from was explicit, and this session produced fresh proof: the
`Max speed — [Ability]` trap resurfaced in the station branch **within an hour**
of my writing it into CLAUDE.md.

Two AUDIT-5 findings remain open:

| # | fix | lines |
|---|---|--:|
| 3 | drop the `\b` after `as ` in the CR 614.1c branch — **`~` is not a word character** | 25 |
| 5 | `\benters?\b` in the etb trigger test — plural *"one or more … enter"* | 43 |

**The sweep is the job, not those two lines.** Grep every branch in
`foundry_shape_extractor.py` for both patterns:

1. **`\b` adjacent to `~`** — `~` is not a word character, so `\b~` and `~\b`
   can never match. Fixed at two sites, live at a third; find the rest.
2. **A singular/plural or inflected verb test** — `enters` vs `enter`,
   `dies` vs `die`, `attacks` vs `attack`. Fourth instance this arc, and the
   newest one was **punctuation, not a verb ending**: the die-row range
   separator prints as em-dash (75), hyphen (5) and not-at-all (26). **Widen
   the sweep to separators and symbol variants, not just verbs.**

After each: `diff --strict`, **read every moved line**, determinism ×2,
invariance, conservation, visibility.

### Then, in order

1. **CR 706.3b die rows — the ROUTING half.** The DET join is done (`3ff3afd`);
   the rows still parse alone and 99 are unrouted. CR 706.3b makes the table
   *"all part of one ability"*, so a row should inherit the roll ability's
   delivery exactly as a mode inherits its header's. **No vocabulary.** The
   mechanism is D3 inheritance in `deliveries_for_lines`.
2. **The anthem group** — step 2's real next slice, and the big one.
   `creatures you control` (179) · `other creatures you control` (78) ·
   `each creature you control` (61), against **15,151** lines still in
   `spell-or-static`. `rule:tribal-anthem-buff` has a KEEP ruling reconfirmed in
   batches 4, 6 and 7 — **nothing rules its DELIVERY**, so this is routing, not
   vocabulary.
3. `escapes with` (12) — CR 113.6h chains to 614.12; reasoning is in `STEP-2C`
   §2b, needs its own pass.

---

## 5. BLOCKED ON CAPTAIN — one sheet

Nothing here blocks §4. **Two items were CLOSED this session** (kicker retired,
`_MODAL_HEADER_RE` widened) and **one was DECLINED** (Attractions → `OUT-OF-SCOPE.md`).

| # | item | why it needs Captain |
|---|---|---|
| 1 | **Refresh `docs/mtg-comprehensive-rules.md`** | the local CR is a vendored snapshot **behind the corpus**: `Chorus` is a printed spell type absent from CR 205.3k's five. Held in a dated CR-LAG register meanwhile |
| 2 | `main-phase-unqualified` (n=1, Carpet of Flowers) | §6b rule 1 says per-shape axes are free; does n=1 earn a token? |
| 3 | `to-graveyard-zone-unstated` (n=11) | per-card ruling; CR 110.1 decides each, the printed words do not |
| 4 | Migrations **logged, not executed** | `rule:lifegain-triggered-plus1-counter` → `rule:gain-life-trigger-plus1-counter` (closes §14 Q5), the §2a `other-` pair, three `delayed` slot-order renames. **Each is a codebook mutation — Captain's word AND the backup law** |
| 5 | `rule:postcombat-main-phase-trigger` under-populated | 2 of 10 cards; a membership addition |
| 6 | **What replaces deck co-play in the S7 substitute lens?** | **A** — a 2/3 lens, free today; or **B** — acquire deck data, interacting with *"no card data in git, ever."* **Recommendation: A now, B logged.** `S7-GATE-NOT-RUNNABLE-2026-08-05.md` §5 |
| 7 | **§2a prefix-stripping must be anchored to the token list** | `AUDIT-5` §1 finding 2. `any-` means two different things; a blind stripper corrupts four token names. A convention change |
| 8 | **`start your engines!` / the 43 homeless CR 702 keywords** | 46 lines. CR 702.179a names its class outright, but the fix touches `effective_classes` and **moves the pinned `keyword_homes = 150` guard**. Most of the other 42 are alternative costs where "no home" may be correct — needs a ruling on the class, not 43 fixes |

---

## 6. WHAT THIS SESSION PROVES

**The list was never a shape.** Every defect closed today was a hand-written
shape standing where the CR publishes an enumeration or states a class
outright — 207.2c, 700.2, 706.3b, 711.2, 716.2, 721.2, 702.33a. The system
map's question found all of them: *"where does this list come from, and can that
source contain every member the CR names?"*

**"Unrouted" is not "stopped," and a census cannot tell you which.** Pawprint
modes read 100% unrouted *after* being correctly fixed. Three constructs would
have been called broken by an unrouted rate alone.

**Improving recall can hand out a WRONG ratified token.** A gap-closing diff
scores `None → ratified` as pure profit and cannot see it. Read every closed
gap.

**A probe is code and gets audited like code.** **Four probe defects in one
session**, each of which would have shipped as a finding: a `non-ASCII` class
that re-measured the em-dash; `{TK}` read as a station symbol when it is
Unfinity's ticket; a visibility audit that called 165 options unscannable
because it compared un-canonicalized text; and 49 station striations reported as
needing a join when their context is inline. **Run the system map's question on
your own probe first.**

**The harness earns its keep.** It halted the modal pass on *"2 lines LOST a
ratified delivery token"* and refused to proceed. Both were real.
