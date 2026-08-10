# PICK UP HERE

**Deliberately undated and deliberately named without a date.** Handoffs got
picked by filename sort and by `ls -t`, and both orderings selected the wrong
file (`SESSION-START-PROCEDURE.md` Gate 1 records it). This file is the stable
entry point. **Keep the name. Update the contents.**

---

## 0Z. READ THIS BEFORE §2 — THE WORK QUEUE CHANGED

**→ `docs/PRODUCT-REALITY-AUDIT-2026-08-09.md`.** Captain asked whether the
work actually serves the tool. Measured answer: **the T3 foundry is not
connected to the product.** `tier_engine.py` reads no foundry output at all and
emits one self-derived `rule:` tag; all 13 importers of the delivery classifier
are audits. **19.3% of the corpus carries any derived tag.** 204 commits since
2026-08-01 touched `pipeline/` zero times.

**W4 is PAUSED — do not take §2A.** The ordered queue is now:

1. ~~**Wire the codebook into `tier_engine`**~~ — **MEASURED 2026-08-09, DO NOT
   RE-RUN. → `docs/WIRE-RESULT-2026-08-09.md`.** The join was built offline and
   graded against predictions committed before it existed. **It does not land:
   1 of 3 criteria passed.** The join is a re-rank by codebook MEMBERSHIP —
   across 33 hand-named correct neighbours, **every one on its axis was
   promoted and every one not on it was demoted, no exceptions**. Axis recall
   against those families is **13/33 = 39%**, and the one axis at 100% recall
   produced **zero** movement because its members already share verbatim text
   and the engine reaches them at Tier 2 for free. Re-run it after coverage
   moves: `python3 experiments/foundry_wire_experiment.py --json`.
2. ~~**Unblock `A15-VOCAB-01`**~~ — **BOTH HALVES LANDED 2026-08-09. →
   `docs/A15-VOCAB-01-RULING-2026-08-09.md`.** It was never ONE decision and
   never a vocabulary question. The **21-row `except` half was a transcription
   bug** in `validate_slug` against grammar §13 Q8.5 (ratified 2026-07-31),
   fixed by PARSING the ratified line; four guards negative-controlled. The
   **188-row `destruction` half completed a rename Captain ratified and the
   project executed on a sibling 2026-08-02** (§6c line 838) and stopped
   halfway: `rule:targeted-destruction` → **`rule:targeted-destroy`**, 172
   members, Captain-ratified and executed under the backup law.
   **`STOPPED_FOR_CAPTAIN` is cleared — the 18,059-row pass is ratified to
   proceed and has NOT been run yet.** That is the next action.

   **The rename ended a CHECK-EVASION, and this is the transferable lesson:**
   `definition_drift`'s C3 keys on grammar §4 EFFECT verbs, so an axis spelled
   with a non-§4 word is invisible to it **by construction**. Renaming put 172
   members into C3's scope for the first time — 171 pass, and **Audacious Swap
   is a genuine defect** (*"shuffles it into their library"* — a tuck, not a
   destroy). Gate 2 going RED after a mutation is the drill working.

   **R5 IS ATTRIBUTED AND 2a NOW COMPLETES — → ruling doc §9.**
   `experiments/foundry_r5_attribution.py` replays `classify_r5` over every
   codebook backup. R5 141 → 163 is **eight ratified mutations**, every delta
   closing, every entering row a correct promotion. The harness is provably
   faithful: at the classification's own recorded inputs it reproduces
   **R5 = 141 exactly**.

   **But `EXPECTED_A15_ROWS = 213` NEVER REPRODUCED.** Same replay, producer
   checked out at both `cfc26fa` and `f09fe73`, gives **194** every time while
   R5 gives 141 in the same run. One cluster carries it all —
   `cant-be-blocked-except-by-count`, recorded 21 rows, reproducible 2. So
   A15-VOCAB-01's "209 blocked" reproduces as **190**, and CDR-02's "21-row
   grab bag" analysis rests on rows that do not reproduce. **Cause is not among
   the four recorded inputs** — unresolved, and stated as such.

   **`STOPPED_FOR_CAPTAIN` is a HARDCODED literal**, not a computed flag. The
   audit page and CLAUDE.md §0 read it as proof the pass is blocked; it is
   `true` with zero blockers. The real signal is `blocking_decisions` — **now
   empty**.

   **2a completed**, determinism ×2, old artifact preserved as
   `...PRE-A15-RULING-20260809.json`. New contract: **0 blocked, 194 promoted,
   15,371 rows for 2b** (was 18,059); routing 2 → 2,925, attributed to
   `merged_slug_codebook_hits` 0 → 2,926 as renamed axes went 45 → 108.

   **← NEXT: 2b / session 3 is NOT run, deliberately.** That is the codebook
   mutation — **11,660 member additions, 87 new axes** — and its contract moved
   −2,688 rows since Captain ratified the rename against an 18,059-row pass.
   That is a fresh look, not a continuation.

3. **Revive `foundry_review.html`** — dark since 2026-07-17.
4. **A green pipeline build** — last one 2026-07-05.

**Three findings the wire experiment produced that no foundry session could
have** (all in `WIRE-RESULT-2026-08-09.md`):

* **A codebook membership defect**: `rule:reanimate-from-graveyard` holds
  **Animate Dead** and **not Dance of the Dead**, its Aura-template twin. The
  wire promoted one to #2 and buried the other at #56. No Gate 2 check can see
  this.
* **A live `tier_engine` bug, unrelated to the codebook**: Rampant Growth's
  displayed top-10 is **an alphabetical slice of a 44-row score tie**. Tier 3
  sorts `(-score, name)`, so with one distinct score in the head the product
  ships the alphabet. A tie-break is a ratified-constant question for Captain.
* **88 Alchemy (`A-`) memberships across 51 active axes, 48 of them duplicate
  pairs with their own paper twin.** They inflate every axis DF — which feeds
  `idf` *and* the 172 `DERIVED_QUALIFY_DF_CEILING` — and duplicate displayed
  rows, against the ratified *"paper rows preferred over A- variants"*.

**Audit §10 is BUILT: `experiments/foundry_reachability.py`, Gate 2 row 13.**
It parses the shipped entry points out of `.github/workflows/`, walks their
import closure, and reports how many foundry artifacts reach a shipped card.
**0 of 5**, every session, until that changes.

Everything below this section is still ACCURATE; it is the queue's PRIORITY
that changed, not its facts.

---

## 0. THE ONE-LINE STATE

W1, W2 and W3's DET half are DONE. D1/D4/D5/D6/D7 landed 2026-08-08; **all five
D8a items landed 2026-08-09**. D2/D3 was WITHDRAWN; D8b stays blocked behind it.
§2 is **64 tokens**; `unclassified-trigger` is **481**.

**2026-08-09 also rebuilt the safety net and then used it.** Gate 2 is **one
command, 12 rows, every one negative-controlled** (`foundry_gate2.py`).
Positive correctness went **488 → 1,248 graded assertions**. Two gates that
could not fail now can.

**THE CODEBOOK WAS MUTATED — 403 active axes / 8,810 members** (was 565/8,740),
across three Captain-authorised specs under the backup law: one quote repair,
44 new axes re-homing the `--wide` residual, and the 5-axis `etb` → `replacement-
enters-…` rename. Every one backed up, dry-run, determinism ×2, conservation
checked.

**Canonical current handoff: `docs/SESSION-HANDOFF-2026-08-09.md`.**
This file does not replace it — it tells you what to do FIRST and why.

---

## 0a. THE CR REFRESH IS DONE — **→ `docs/CR-REFRESH-2026-08-09.md`**

Landed 2026-08-09 (`2733326`, `675a58b`). The pipeline reads the **2026-08-07**
edition through one normalizing loader (`experiments/foundry_cr.py`); the file
itself is untouched, and it is **tracked in this repo now** rather than reached
across into the site's gitignored `docs/`.

**0 of 61,383 ability lines moved.** Two numbers did, both real WotC changes:
CR 702 keyword names **193 → 194** and keyword homes **150 → 151**, from the new
CR 702.195 **Storied**. Everything else on the acceptance test reproduced
exactly.

**Do not re-derive any of this.** Three things worth carrying:

* **The mana rule is CR 605.1a** and it has **no code path here**. CR 106.4 /
  106.6 / 106.12 are byte-identical across editions, so nothing mana-related
  moved. `CR-REFRESH-MANA-ABILITIES.md` is resolved.
* **The CR-LAG register did NOT shrink.** `chorus` and `N or less` both said
  "the real fix is to refresh the snapshot"; the refresh happened and fixed
  neither. Both comments are corrected in place — the CR is behind the printed
  cards, not the snapshot behind the CR.
* **`MTJ_CR_PATH=<file>` runs the whole pipeline against another edition.** That
  is how the loader was proven a no-op on the June CR before the diff was
  believed, and it is how the next refresh should be verified.

**Two items are on Captain's sheet** (§4): the new file's encoding damage in
CR 206.3a, and whether CR 605.1a needs modelling. Neither blocks anything.

---

## 1. DO THIS FIRST — read the audit's result, do NOT re-run it

**The audit the previous version of this file demanded HAS BEEN RUN.**
2026-08-09, commit `2bcaeb6`. Do not re-derive it; the result is in
`SESSION-HANDOFF-2026-08-09.md` §2 and here in one line:

> All 280 lines of the six 2026-08-08 tokens were read against their CR rules.
> **Five of six are clean.** `draw-trigger` was 69/71, and the two bad ones —
> plus **two more the token-scoped audit could not see** — were fixed.

**What it left behind, and this is the part that matters:**

`foundry_ground_truth.py` asserts **0 of 6**, and the reason is structural,
not specific to those six. **13 of 16 move specs carry ZERO seeds**, so the
whole codebook — 8,740 members — is graded through a fixture of 534 drawn
from three specs / 15 axes. **Every token ratified since 2026-08-04 sits
outside the only positive-correctness check in the repo.**

Widening the fixture is cheap, unstarted, and is §6C of the handoff.

**Do not read "5 of 6 clean" as "the tokens are verified."** It means they
were read once by a session. That is strictly better than the diff, which
scores `None → ratified` as pure profit, and strictly worse than a fixture.

---

## 2. THEN — the next work item

> **⛔ SUPERSEDED BY §0Z.** Both items below are shape/vocabulary work inside
> the foundry, and the foundry does not reach a shipped card. They are kept
> because they are correctly scoped and will matter **after** the codebook is
> wired into `tier_engine` — not before. Do not start either without saying out
> loud which shipped artifact changes.

**The CR refresh is done (§0a). Both items below are ready and unblocked —
and both are PAUSED pending §0Z.**

**A. W4 — the static queue · 3,358 lines · the big slice. TWO SHAPES DONE.**
The **anthem** (`<subject> get ±N/±N`, **524**) and the **keyword grant**
(`<subject> have <CR 702 keywords>`, **488**) both landed 2026-08-09 with
**0 re-routes** — `docs/W4-ANTHEM-2026-08-09.md` and
`docs/W4-KEYWORD-GRANT-2026-08-09.md`. **Read the second one's §9 first**; it
ranks what is left, and **CR 601.2f cost reduction (~498) is next**.
`python3 experiments/foundry_shape_extractor.py --gaps`, section headed
`INSIDE spell-or-static`. Named shapes, one at a time,
never a blanket sweep — the warning was re-measured 2026-08-09 and the 1,883 is
still **4** (`experiments/foundry_blanket_risk.py`), all four the Siege cycle
behaving correctly.

**B. The 481-line residual.** `python3 experiments/foundry_w3_census.py`
partitions it by the CR rule that decides it and mints nothing. Ranked by
DECK-BUILDING RELEVANCE (Captain's ratified criterion — a queue sorted by line
count applies the one the rule names as wrong):

1. **`fully unlock a Room`** — CR 709.5i — 17. The case is already written
   (handoff §5d); it needs Captain, not analysis.
2. **plays-a-card** — CR 601.1a / 305.1 — 16.
3. **ring-tempts** — CR 701.54 — 8.
4. counter-placed / -removed — 122.6 / §8b — 38. **Check §8b first**, it may
   already govern these.

**The recipe, proven ten times now:** Gate 3 the name you are about to WRITE →
§2 table row with the CR quoted → wire the emitter → routing diff
`--strict --lines` and READ EVERY MOVED LINE → the four audits → re-pin the
baseline only onto improvement, and only with the reason stated.

---

## 3. DO NOT DO — and why, so it is not rediscovered

**D8b — monstrosity (19) · level-up (13) · attach (12) · phasing (7) ·
dungeon (4).** These five **are CR 701/702 keyword terms**, so they belong to
the WITHDRAWN D2/D3 question. Minting them one at a time is design goal #1's
duplication or a back-door ratification.

**D2/D3 as a blanket grammar family.** Built exactly as ratified and it
**admitted 251 tokens** — including `defender-trigger` (a word §6 bans) and
`kicker-trigger` (retired by §2g). "Every CR 702 keyword" is parsed from the
CR at run time and is *still* a hand-list in disguise, because most CR 702
keywords are STATIC abilities that never happen. **The replacement is an
EXPLICIT member list of the ~41 attested terms — a ratification.**

**Widening `door-unlocked-trigger` to cover `fully unlock`.** CR 709.5i is a
different event — the SECOND door, on ANY Room. §6b rule 1 forbids the fold by
name. It is a ratification, not a regex change.

**Adding `lose` to the compound splitter's `PREDICATE` list.** Measured: it
makes the `gain or lose life` defect WORSE, not better. Handoff §5b has the
diagnosis; it needs a shared-object re-join, not a list entry.

---

## 4. CARRIED FORWARD — still open

- **W8, Captain's sheet — now fourteen items.** The ten standing ones, plus
  CR 709.5i, the shared-object splitter, and the two from the CR refresh
  (`docs/CR-REFRESH-2026-08-09.md` §DECISION SHEET): **D-CR-1 is RULED and
  LANDED** — Captain 2026-08-09, repair the 7 mojibake characters in CR 206.3a
  at read time; CR 206.3a is now byte-identical to the 2026-06-19 edition and
  0 lines moved. **D-CR-2** whether "is a mana ability" (CR 605.1a) needs
  modelling at all is open — recommendation is no.
- **117 single-faced instants/sorceries routing to `replacement`** — the
  branch has no spell-face gate. Needs a per-FACE cut; real design.
- **10 `it becomes day AS THIS CREATURE ENTERS` lines** — CR 614.1c
  replacements, found while landing D8a item 2, unrouted, logged not started.
- **W5** `escapes with` (12) · **W6** family sweep (the standing 6) ·
  **W7** definition drift (the standing 35).
- **W9 parent layer** is blocked on W8; **W10 display** on W9.

---

## 5. THE FOUR THINGS MOST LIKELY TO BITE

1. **A TOKEN-SCOPED AUDIT IS BLIND TO ITS OWN NEIGHBOURS.** Reading all 280
   lines of the six tokens found 2 defects; the routing diff on the fix found
   **4**. The other two had the identical cause and a token outside the audit's
   scope. Read the population, then run the diff and read that too.
2. **A SPECIFICATION IS A CARRIED-FORWARD COUNT WITH A CR NUMBER ATTACHED.**
   All five D8a items had a defective spec — three wrong counts, one wrong CR
   rule (728 is Rad Counters; day–night is 731), one hidden second CR rule.
   Re-measure the anchor and the partition, not just the number.
3. **A row-level loss on a ROUTED line is invisible to `diff --strict`.**
   Watch `deliveries` and `descriptor_unrouted.*`, never `unrouted_lines`.
4. **A probe defect is the default outcome.** Nineteen across five sessions,
   including one this session that under-counted by requiring a line to start
   with `when` — and so lost an ability-word prefix and a compound.

---

## 6. THE PROMPT — paste this to restart

```
Follow docs/SESSION-START-PROCEDURE.md, then read docs/PICK-UP-HERE.md and
docs/SESSION-HANDOFF-2026-08-09.md.

Do NOT re-run the six-token audit — §1 says it is done and what it left.
Do NOT re-do the CR refresh — §0a says it is done and what it moved.

Take a work item from §2: W4 (the anthem group) or the 481-line residual.

Standing rules apply: Gate 2 is `python3 experiments/foundry_gate2.py`, read
every moved line in every routing diff, re-pin a baseline only onto improvement
and only with the reason stated, back up before any codebook mutation, and use
`import foundry_probe as p` for anything that measures. Commit as you go.
```
