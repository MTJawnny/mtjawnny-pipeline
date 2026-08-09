# PICK UP HERE

**Deliberately undated and deliberately named without a date.** Handoffs got
picked by filename sort and by `ls -t`, and both orderings selected the wrong
file (`SESSION-START-PROCEDURE.md` Gate 1 records it). This file is the stable
entry point. **Keep the name. Update the contents.**

---

## 0. THE ONE-LINE STATE

W1, W2 and W3's DET half are DONE. Captain ratified the W3 sheet; **D1, D4,
D5, D6, D7 landed 2026-08-08 and ALL FIVE D8a items landed 2026-08-09.**
**D2/D3 was built, measured and WITHDRAWN; D8b stays blocked behind it.**
§2 is **64 tokens**; `unclassified-trigger` is **481**. Codebook never
mutated — 565 axes / 8,740 members.

**Canonical current handoff: `docs/SESSION-HANDOFF-2026-08-09.md`.**
This file does not replace it — it tells you what to do FIRST and why.

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

**Take one. Both are ready; neither is blocked.**

**A. W4 — the anthem group · 4,375 decidably-static lines · the big slice.**
`python3 experiments/foundry_shape_extractor.py --gaps`, section headed
`INSIDE spell-or-static`. Named shapes, one at a time, never a blanket sweep —
but re-measure the warning first, the 1,883 is now 4
(`experiments/foundry_blanket_risk.py`).

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

- **W8, Captain's sheet — now twelve items.** The ten standing ones, plus
  CR 709.5i and the shared-object splitter.
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

Take the next work item from PICK-UP-HERE §2 and work it one class at a time
using the recipe given there. Do NOT touch D8b, D2/D3, or the two items §3
names as measured-and-rejected.

Standing rules apply: read every moved line in every routing diff, run all
four audits after each step, re-pin a baseline only onto improvement and only
with the reason stated, and do not mutate the codebook. Commit as you go.
```
