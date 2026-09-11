# NEXT SESSION — CR REFRESH BY NORMALIZATION

> ## ✅ DONE — 2026-08-09. **→ `docs/CR-REFRESH-2026-08-09.md`**
>
> Executed exactly as written, by normalization, with the file left pristine.
> **0 of 61,383 ability lines moved.** Gate 2 green. 7 of 9 acceptance numbers
> reproduced exactly; the 2 that moved are the new CR 702.195 **Storied**
> (keyword names 193 → 194, keyword homes 150 → 151), which is a real WotC
> change, not a loader defect.
>
> The mana rule is **CR 605.1a** and it has **no code path in this repo** —
> read the record before assuming otherwise. Two items went to Captain: the new
> file's **encoding damage in CR 206.3a** (7 characters, declared and guarded)
> and whether 605.1a needs modelling at all.
>
> **This page is kept as the SPEC.** One correction: FACT 2's "vendored 2,167
> rule-numbered lines" is wrong — measured 3,153. It changed nothing, because
> the acceptance test is content-based rather than a count.

**Written 2026-08-09 with full context loaded, so the next session does not
have to pay that cost.** Everything needed is on this page.

---

## THE PROMPT — paste this

```
Follow docs/SESSION-START-PROCEDURE.md (Gate 2 is ONE command now:
python3 experiments/foundry_gate2.py). Read docs/PICK-UP-HERE.md and
docs/CR-REFRESH-MANA-ABILITIES.md.

Your job: refresh the vendored Comprehensive Rules to the 2026-08-07 edition
at docs/MTG_Comprehensive_Rules_2026-08-07_LLM.md.

DO NOT TRANSLATE OR REWRITE THE NEW FILE. Ratified 2026-08-09: the new file
stays pristine and a single normalizing loader strips its formatting AT READ
TIME, handing the existing parsers the shape they already expect. Translating
the CR is transcribing it, which CLAUDE.md forbids, and it would need its own
conservation audit to be trustworthy.

Work it in this order, one step at a time, committing as you go:

1. Build the normalizing loader. ONE place knows about CR formatting.
2. Run the acceptance test below. Every number must reproduce EXACTLY.
3. Point the parsers at the new file. Re-run the acceptance test.
4. Routing diff --strict --lines and READ EVERY MOVED LINE. A CR refresh can
   move routing with NO code edit, because the vocabulary is parsed at run
   time — this is the one change where that happens.
5. foundry_gate2.py. Expect it to find something; that is the point.
6. Only then look at what the mana-ability rules actually changed.

Standing rules apply: read every moved line, re-pin a baseline only onto
improvement and only with the reason stated, back up before any codebook
mutation, and use `import foundry_probe as p` for anything that measures.
```

---

## FACT 1 — the new file is a DIFFERENT FORMAT, not a drop-in

```
new:       **605.1a.**  An activated ability is a mana ability if…
vendored:  605.1a An activated ability is a mana ability if…
```

Bold rule markers, `### 605.` section headings, and a table of contents.
**Every CR parser in this repo keys on the vendored plain format.** Copying the
file over `docs/mtg-comprehensive-rules.md` makes `load_702`,
`type_vocabulary` and the CR 205/207/702 enumerations return empty or partial.

The halt-guards will fire — that is them working — but it means this is a
**parser job, not a file copy**.

## FACT 2 — the new file is COMPLETE and fidelity-preserving

Checked 2026-08-09 before recommending it:

| | new | vendored |
|---|--:|--:|
| rule-numbered lines | 3,161 | 2,167 |
| size | 990 KB | 971 KB |
| **curly apostrophes (U+2019)** | **1,710 present** | — |
| CR 205.2a card types | intact | intact |
| CR 207.2c ability words | intact | intact |

The curly-apostrophe count is the one that matters most — CLAUDE.md records
that trap (`Urza's` ≠ `Urza’s`, and `C’tan`, `Shi’ar`). **The bold markers are
ADDITIVE STRUCTURE, not loss.**

## FACT 3 — bold is BETTER source, which is why it is kept

`**605.1a.**` at line start is an **unambiguous** rule marker. The plain format
forces every parser to guess whether `605.1a` is a heading or a cross-reference
mid-sentence. Keep the ambiguity out of the file and put the stripping in one
loader.

---

## THE ACCEPTANCE TEST — pinned 2026-08-09, must reproduce EXACTLY

After normalization, the CR-derived enumerations must return these. **A number
that moves is either a loader defect or a real rules change, and you must say
which before proceeding.**

| enumeration | CR | expected |
|---|---|--:|
| card types | 205.2a | **15** |
| subtypes | 205.3g–q | **550** |
| supertypes | 205.4a | **5** |
| ability words | 207.2c | **61** |
| CR 702 keyword names | 702.Na | **193** |
| keyword homes | derived | **150** |
| zones | 400.1 | **7** |
| damage recipients | 120.1 | **4** |
| self-reference nouns | CR 205 all lists | **568** |

Quick check:

```
python3 experiments/foundry_system_map.py     # prints most of the above
python3 experiments/foundry_gate2.py          # 12 rows, all must stay green
```

## THE ROUTING BASELINE — what must not move silently

| | |
|---|--:|
| ability lines | 61,383 |
| deliveries | 61,960 |
| §2 DELIVERY tokens | 64 |
| `unclassified-trigger` | 481 |
| keyword homes | 150 |
| active axes | 403 |
| codebook members | 8,810 |

`--wide` fixture, pinned: **graded 1,248 · passing 1,238 · mismatch 10 ·
unanchored 0 · head-ambiguous 3.**

---

## THE MANA BLAST RADIUS — measured, so the refresh is a COMPARISON

Captain: *"there's a new CR that changes how mana abilities work."* What
depends on it:

| | lines | CR |
|---|--:|---|
| `tapped-for-mana-trigger` | **58** | **106.12** + 106.12a |
| `ability-activated-trigger`'s mana qualifier | 16 | **605.1a** |
| `add-mana` §4 EFFECT verb | 1,746 `Add {…}` lines | **106.4** |
| `restricted-purpose-mana` §3a | 217 members | **106.6** |
| active axes naming mana | 312 members | — |

**`tapped-for-mana-trigger` is the exposed one.** Its branch is written from
CR 106.12's definition of the *act* and is one of the three recorded "look ONE
RULE UP" sites — a restatement moves its **premise**, not just its recall.

**Note the timing:** `add-mana` (CR 106.4) and `restricted-purpose-mana`
(CR 106.6) were ratified on 2026-08-09, *hours before* the CR notice. Neither
is wrong today; both must be re-verified against the new rules.

Code sites: `foundry_shape_extractor.py` (the 106.12 branch, both voices) ·
`validate_slug.py` · `tier_engine.py`.

---

## ONE THING TO CONFIRM FIRST

The filename says `_LLM.md`, which suggests a version prepared for LLM
consumption — possibly a derivative rather than WotC's official text. The
content spot-checks clean, but for a document this repo treats as ground truth,
**confirm with Captain whether this is the official release reformatted by them
or a third-party reformatting.** If third-party, diff it against the official
text before it becomes the source of every derived vocabulary.

## WHY THIS IS SAFER NOW THAN IT WOULD HAVE BEEN YESTERDAY

- Gate 2 is **one command, 12 rows, every one negative-controlled**.
- Positive correctness went **488 → 1,248** graded assertions, so CR-induced
  breakage outside the old 488 is now visible instead of silent.
- `definition_drift` and `ruling_registry` **can fail** as of 2026-08-09; the
  day before they exited 0 on any defect.
- `foundry_recorded_numbers.py --strict` re-derives every count §2 asserts, so
  a silently changed population cannot pass.
