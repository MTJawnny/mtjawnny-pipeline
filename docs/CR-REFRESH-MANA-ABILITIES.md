# CR REFRESH — THE MANA-ABILITY RULES CHANGED

> ## ✅ RESOLVED — 2026-08-09. **→ `docs/CR-REFRESH-2026-08-09.md`**
>
> The change is in hand and it is **CR 605.1a**. A mana ability now
> additionally requires that *"its cost and effect don't move any card to or
> from a library"*, with a self-replacement caveat.
>
> **Every number in the blast radius below held, re-verified by a rule-by-rule
> edition diff rather than re-measured:** CR **106.4**, **106.6** and
> **106.12** are byte-identical across the two editions, so
> `tapped-for-mana-trigger` (58), `add-mana` (1,746) and
> `restricted-purpose-mana` (217) did not move. **0 routing lines moved
> corpus-wide.**
>
> **And 605.1a itself has no code path here.** Grammar §2 cites it to explain a
> §1 qualifier that is matched as printed card text; nothing parses the rule.
> The prediction that a restatement would move the branch's *premise* was aimed
> at the right rule — the premise just is not encoded anywhere. That is
> D-CR-2 on the decision sheet.
>
> This page is kept for its 2026-08-09 baseline, which is what made the
> re-check a comparison. Everything below it is pre-refresh.

**Opened 2026-08-09 on Captain's notice. BLOCKED: the change itself is not yet
in hand.** Undated in the filename on purpose — this stays open until the
vendored CR is refreshed and the blast radius below is re-checked.

---

## THE SITUATION

> Captain, 2026-08-09: *"There's a new CR that changes how mana abilities work.
> We'll need to incorporate this change for the final product."*

**The vendored snapshot is `effective June 19, 2026`** — measured from its own
header, not from the file mtime (which reads Jul 16 and is the copy date, not
the rules date). So a newer CR exists and this repo has not seen it.

CLAUDE.md already anticipated this exact shape:

> *"The local CR is a VENDORED SNAPSHOT and can fall behind the corpus.
> Refreshing `docs/mtg-comprehensive-rules.md` is a real maintenance item."*

**This is the first time the lag is known to affect a RULE rather than a card.**
The two standing CR-LAG entries (`chorus`, `N or less`) are both vocabulary the
snapshot lacks. A mana-ability rules change is different in kind: it can
invalidate a *derivation*, and this pipeline derives from the CR at run time by
design.

---

## WHAT IS NOT KNOWN, AND WILL NOT BE GUESSED

**I do not know what the change says.** My knowledge cutoff precedes it, and
the vendored CR predates it. Nothing in this document infers the content of the
new rule, and no branch should be written against a guess — that would be the
house's worst failure mode (a hand-list standing in for a CR the repo could
have parsed).

**What is needed to proceed:** the updated CR text, or the rules-effective date
plus the changed rule numbers.

---

## BLAST RADIUS — measured 2026-08-09, so the re-check has a baseline

### Ratified §2 DELIVERY vocabulary standing directly on mana rules

| token | lines | CR it is derived from |
|---|--:|---|
| `tapped-for-mana-trigger` | **58** | **106.12** (*"to tap a permanent FOR MANA is to activate a mana ability"*) + 106.12a |
| `ability-activated-trigger` | 34 | 602.1 / 602.2 |
| …of those, carrying the **CR 605.1a** *"isn't a mana ability"* qualifier | **16** | 605.1a |

`tapped-for-mana-trigger` is the exposed one. Its branch is written from
**CR 106.12's definition of the act**, and it is one of the three recorded
"look ONE RULE UP" sites — so if 106.12 or 605.1a is restated, that branch does
not merely lose recall, **its premise moves.**

### Ratified vocabulary landed 2026-08-09, in the path of the change

Both were ratified **hours before** this notice, and both cite mana rules:

| what | CR | population |
|---|---|--:|
| `add-mana` §4 EFFECT verb | **106.4** | 1,746 lines print `Add {…}` |
| `restricted-purpose-mana` in §3a's RESTRICTION slot | **106.6** | 217 members |

Neither is wrong today. Both must be re-verified against the new rules before
anything is built on them.

### Codebook surface

10 active axes name mana — **312 members**, dominated by
`restricted-purpose-mana` (217).

### Code sites

| file | what it does with mana rules |
|---|---|
| `foundry_shape_extractor.py` | the CR 106.12 / 106.12a branch (both voices) |
| `validate_slug.py` | carries the CR 106.12a ruling |
| `tier_engine.py` | paragraph splitting that must separate a mana ability from a *"spend this mana only…"* sentence |

---

## THE ORDER OF WORK, WHEN THE CHANGE IS IN HAND

1. **Refresh `docs/mtg-comprehensive-rules.md`** and record the new
   rules-effective date in this file.
2. **Re-run the CR-parsed enumerations first, not the classifiers.** Every
   halt-guard that asserts CONTENT will fire on its own if a list it parses
   changed shape — that is what they are for. Read those failures before
   touching a branch.
3. **Diff the routing** (`--strict --lines`) and read every moved line. A CR
   refresh is the one change that can move routing without any code edit,
   because the vocabulary is parsed at run time.
4. **Re-check the four counts above.** `foundry_recorded_numbers.py` already
   re-derives every count §2 asserts and exits 1 on drift, so it will catch a
   silently changed population without anyone remembering to look.
5. **Re-measure the two 2026-08-09 ratifications** (`add-mana`,
   `restricted-purpose-mana`) against the new 106.4 / 106.6.
6. **Clear or re-confirm the CR-LAG register** — `chorus` and `N or less` may
   simply be fixed by the refresh, in which case the register shrinks.

---

## WHY THIS IS A DOCUMENT AND NOT A TODO LINE

Because the numbers above are a **baseline**, and without one the refresh
cannot be verified. The recorded rule applies to this file too: *a
carried-forward count is not a measurement* — so every number here was measured
on 2026-08-09 and is stated with the date so the post-refresh re-run is a
comparison rather than a fresh guess.
