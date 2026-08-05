# PICK UP HERE

**Deliberately undated and deliberately named without a date.** Handoffs got
picked by filename sort and by `ls -t`, and both orderings selected the wrong
file (`SESSION-START-PROCEDURE.md` Gate 1 records it). This file is the stable
entry point. **Keep the name. Update the contents.**

---

## 0. THE ONE-LINE STATE

W1, W2 and W3's DET half are DONE. Captain ratified the W3 decision sheet;
**five of nine landed (D1, D4, D5, D6, D7)**, **D2/D3 was built, measured and
WITHDRAWN**, **D8 was split into D8a (unblocked) and D8b (blocked)**. Codebook
never mutated. Last pushed commit: `4387dec`.

**Canonical current handoff: `docs/SESSION-HANDOFF-2026-08-08.md`.**
This file does not replace it — it tells you what to do FIRST and why.

---

## 1. DO THIS FIRST — the audit, and it is not optional

**Six §2 DELIVERY tokens were ratified in one session and NOT ONE OF THEM HAS
A POSITIVE-CORRECTNESS CHECK.** This is the exact hole the project already
named:

> *"Every mechanism in this repo asked 'did it CHANGE' or 'did it get LOST'.
> Not one asked 'is it RIGHT'. A token wrong since before the first snapshot
> was permanently invisible, and `diff --strict` scores `None → ratified` as
> pure profit."*

`foundry_ground_truth.py` is the one check that closes it — and it replays
**534 `class: human` seeds from `experiments/moves/*.json`**, which are
*pre-existing codebook memberships*. The six new tokens have **no members**
(the codebook was deliberately not mutated), so **ground truth almost certainly
covers none of them.** They were snapshotted into the regression baseline the
moment they were created, so every future `diff --strict` will score them
correct forever, whether they are or not.

**The six, with the line counts to check against:**

| token | CR | lines |
|---|---|--:|
| `state-trigger` | 603.8 | 50 |
| `draw-trigger` | 121.1 | 71 |
| `draw-second-card-trigger` | 121.1 + D3f | 62 |
| `leaves-graveyard-trigger` (`any-` form) | 400.1 / 700.4 | 43 |
| `lose-life-trigger` | 119.3 | 20 |
| `ability-activated-trigger` | 602.1 / 602.2 | 34 |

**VERIFY, do not assume, that ground truth covers none of them** — that claim
was reasoned, not measured, and Gate 4 says suspect the check.

---

## 2. THEN — D8a, in this order

**Ordered by DECK-BUILDING RELEVANCE, not line count** (Captain's ratified
criterion; the first draft of the queue got this wrong):

1. **Room doors unlocking** — CR 709.5 / 116.2m — 43 lines / 41 cards.
   A build-around set mechanic whose cards currently cannot join ANY
   delivery-bearing axis.
2. **day–night** — CR 728.1 — 10. The werewolf archetype.
3. **coin flip** — CR 705.1 — 7. The Krark archetype.
4. **exile from the battlefield** — CR 400.1 / 700.4 — 12. An LTB variant §2
   named for the graveyard and not for exile.
5. **player loses the game** — CR 603.9 — 7. Its own CR rule, but marginal for
   deck-building. Say so rather than padding the case.

**The recipe, proven five times this session:** Gate 3 the name →
add a §2 table row with the CR quoted → wire the emitter → routing diff
`--strict --lines` and READ EVERY MOVED LINE → the four audits → re-pin the
baseline only onto improvement, and only with the reason stated.

---

## 3. DO NOT DO — and why, so it is not rediscovered

**D8b — monstrosity (19) · level-up (13) · attach (12) · phasing (7) ·
dungeon (4).** These five **are CR 701/702 keyword terms**, so they belong to
the WITHDRAWN D2/D3 question. Minting them one at a time is design goal #1's
duplication or a back-door ratification of a decision that went back to
Captain. §5a of the handoff has the full reasoning.

**D2/D3 as a blanket grammar family.** It was built exactly as ratified and
**admitted 251 tokens** — `flying-trigger`, `deathtouch-trigger`,
`hexproof-trigger`, `defender-trigger` (a word §6 bans) and `kicker-trigger`
(retired by §2g). "Every CR 702 keyword" is parsed from the CR at run time and
is *still* a hand-list in disguise, because most CR 702 keywords are STATIC
abilities that never happen. **The recommended replacement is an EXPLICIT
member list of the ~41 attested terms — a ratification, needing Captain.**

**Blanket-sweeping `spell-or-static` into `static`.** Still forbidden, but
re-measure before quoting the warning: the 1,883 that gates W4 is now **4**
(`experiments/foundry_blanket_risk.py`), and the 4 are correct.

---

## 4. CARRIED FORWARD FROM EARLIER SESSIONS — still open

- **W8, Captain's sheet — now ten items.** Reminder-text conformance (167
  memberships) · refresh the vendored CR · `main-phase-unqualified` (n=1) ·
  `to-graveyard-zone-unstated` (**now 12, not 11**) · five logged migrations ·
  `rule:postcombat-main-phase-trigger` · §2a prefix anchor · `start your
  engines!` / 43 homeless keywords · tier A · **item 10 = W3's D2/D3 + D8b.**
- **117 single-faced instants/sorceries routing to `replacement`** — the
  branch has no spell-face gate (W2 addendum §3). Needs a per-FACE cut, which
  is real design.
- **W4** — 4,375 decidably-static lines. Named shapes, one at a time.
- **W6** family sweep (the standing 6) · **W7** definition drift (the standing
  35) · **W5** `escapes with` (12).
- **W9 parent layer** is blocked on W8; **W10 display** on W9.

---

## 5. THE THREE THINGS MOST LIKELY TO BITE

1. **A row-level loss on a ROUTED line is invisible to `diff --strict`.** The
   line keeps a ratified token, so the diff scores a re-route and
   `unrouted_lines` never moves. Watch `deliveries` and
   `descriptor_unrouted.*`. Three splitter defects had exactly this shape, and
   one of them had INVENTED a trigger rather than lost one — **a census scores
   a lost token and an invented gap identically.**
2. **A probe defect is the default outcome, not the exception.** Eighteen
   across four sessions. Write the probe, then run the system map's question
   on the probe.
3. **Look ONE CR RULE UP.** A branch written from the sub-rule describing the
   *trigger* inherits its voice; the CR states the same event actively one rule
   above (106.12 above 106.12a, 506.3 above 508, 708.7 above 708.8). VOICE and
   WORD ORDER are named sweep classes now, beside W1's INFLECTION.

---

## 6. THE PROMPT — paste this to restart

```
Follow docs/SESSION-START-PROCEDURE.md, then read docs/PICK-UP-HERE.md and
docs/SESSION-HANDOFF-2026-08-08.md.

Do §1 of PICK-UP-HERE first: the six §2 DELIVERY tokens ratified last session
(state-trigger, draw-trigger, draw-second-card-trigger, leaves-graveyard-trigger,
lose-life-trigger, ability-activated-trigger) have no positive-correctness
check, because foundry_ground_truth.py replays existing codebook memberships
and these tokens have none. MEASURE whether that is true rather than assuming
it. If it is, audit all six against their CR rules by reading a real sample of
each token's lines, and report anything mis-routed before any new work.

Then work D8a in the order given in §2, one class at a time, using the recipe
that landed the five ratifications last session. Do NOT touch D8b or D2/D3 —
§3 says why.

Standing rules apply: read every moved line in every routing diff, run all
four audits after each step, re-pin a baseline only onto improvement and only
with the reason stated, and do not mutate the codebook. Commit as you go.
```
