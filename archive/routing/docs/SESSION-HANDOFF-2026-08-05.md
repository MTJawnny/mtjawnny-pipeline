# SESSION HANDOFF — 2026-08-05

> **⚠ SUPERSEDED by `docs/SESSION-HANDOFF-2026-08-06.md`.** Follow that file's
> READING MANIFEST and NEXT WORK ITEM. Numbers below are stale: §2 is now **53**
> tokens (not 45), unrouted is **16,273** (not 18,162), and step 2's three
> slices have landed.

Supersedes `SESSION-HANDOFF-2026-08-04-EVE.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** Ten commits, `216e480` .. `341a28b`.

**The session in one line: Captain ratified the 14 §2 rows; every remaining open
defect in the pre-step-2 audit (D3–D6, D8) was closed; step 2 was opened as
named shapes rather than a sweep — 2,128 ability lines routed onto a correct
DELIVERY token across seven passes, ten lines corrected OFF a token they should
never have held, and not one token losing ground.**

---

## 0. START HERE

`docs/SESSION-START-PROCEDURE.md` — six gates. **If no task was given, §5's NEXT
WORK ITEM is your instruction.** Only two things need Captain's explicit word:
**ratifying new vocabulary** and **mutating the codebook**.

---

## 1. READING MANIFEST — indexed by TASK

### Always

| | |
|---|---|
| `docs/SESSION-START-PROCEDURE.md` | six gates, short |
| `CLAUDE.md` | locked rules + traps |
| Gate 2 commands | live state is measured, never recalled |

### If you are touching the DELIVERY EXTRACTOR (the current work)

```
python3 experiments/foundry_prior_art.py <your topic>      # ← FIRST, always
python3 experiments/foundry_routing_regression.py snapshot experiments/out/foundry/regression/<name>.json
python3 experiments/foundry_routing_regression.py diff <before> <after> --strict
python3 experiments/foundry_routing_regression.py invariance
```

| read | why |
|---|---|
| **`docs/PRE-STEP-2-AUDIT-2026-08-04.md`** | the nine defects. **D1–D6 and D8 are all CLOSED**; D9 is a Captain ruling. What remains is **step 2** |
| **`docs/D4-KEYWORD-FORMS-2026-08-04.md`** | the CR states a printed form in FOUR sentence shapes; five defects caught by measurement |
| **`docs/D3-MODAL-MODES-2026-08-04.md`** | modal inheritance, and the 49-line gap in the ratified modal regex |
| **`docs/D5-REPLACEMENT-WINDOW-2026-08-04.md`** | why a guessed constant HIDES missing logic; the created-ability guard |
| **`docs/D6-COST-HEAD-2026-08-04.md`** | "derive from the CR" ≠ "copy the nearest CR list"; CR 113.3b is a grammar, not a list |
| **`docs/D8-KEYWORD-LIST-SPLIT-2026-08-04.md`** | a 2-line residue meant the stated defect was a symptom |
| `docs/CODEBOOK-NAMING-GRAMMAR.md` **§1, §2, §2a, §2b, §2e, §2f, §9** | the DELIVERY law. **§2 is now 45 tokens**; §2e and §2f are new |
| `docs/DELIVERY-VOCABULARY-BATCH-2026-08-03.md` **§6** | 193 keywords already classified |
| `docs/TRIGGER-VERB-DERIVATION-2026-08-04.md` | why the verb set is DERIVED |
| `docs/SPELL-OR-STATIC-AUDIT-2026-08-04.md` | the bucket that is blind by construction |

### If you are touching the CODEBOOK, an AXIS, or a SLUG

`docs/CODEBOOK-NAMING-GRAMMAR.md` **WHOLE** · `docs/PARENT-TREE-CANDIDATES.md` ·
`docs/FAMILY-TREE-EVIDENCE.md` · `docs/TRIAGE-BATCH-1.md`..`-7.md` — and
`foundry_slug_dossier.py` on **the name you are about to WRITE**.

### If you are touching KEYWORDS

`docs/KEYWORD-LEDGER-CANDIDATES.md` — bare keywords are never axes; Phase B is
their home. **This is what keeps D9's ~951 lines correctly unrouted.**

### If you are touching the PARENT layer

`docs/PARENT-LAYER-OPENING-PACKET-2026-08-04.md` · `PARENT-TREE-CANDIDATES.md`
(S1–S7, T1–T2) · grammar **§6b**.

---

## 2. LIVE STATE — measured at handoff

| | |
|---|---|
| codebook | **565 axes · 359 active · 8,740 members — UNCHANGED, no mutation this session** |
| sha256 | `5fa27b70fabdce8d40e537907358522449d4ce642d80f6680314c1b2d2e7d93e` |
| lint | clean |
| family sweep | 6 blocking (the same 6) |
| definition drift | 35 — C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3 (unchanged) |
| **§2 DELIVERY vocabulary** | **45 tokens** (was 31) |
| routed ability lines | **61,907** (was 61,868 — +39, all dual-delivery, see D3 §5a / D8 §3) |
| ruling registry | **95 docs · 127 ruling ids** |
| **lines with NO ratified token** | **18,162** (was 20,290 — **−2,128**) |
| distinct ratified tokens in use | **64** (was 47) |
| keyword homes | **148** (was 144 — 4 CR-confirmed, D6 §4) |
| baseline snapshot | `experiments/out/foundry/regression/p9-step2a.json` |
| working tree | clean |

---

## 3. WHAT CHANGED — seven commits

**`216e480` RATIFIED: the 14 §2 rows (+502 lines).** §2 31 → 45 tokens, plus
§8b's `<type>-counter-placed-trigger` grammar family and §2e (a static ability
that *generates* a replacement effect takes `replacement` — 16 keywords, 282
lines). **Ratification had a mechanical half the sheet understated:** only
main-phase was wired to `mark`; the other 11 tokens emitted `None, "<descriptor>"`
because no ratified token existed when they were written.

**`eda04be` D4 — parameterized keyword lines (+528).** Forms parsed from the CR,
which states them in **four** sentence shapes. 0 lines moved off a ratified token.

**`3c78e50` D3 — modal modes inherit their header's delivery (+515).**
Reproduces the audit's table to the line (etb 201, activated 64, cast-trigger 33,
begin-combat 26).

**`15a3d71` audit #2 + this handoff.**

**`2ffbcef` D5 — the replacement window was a guessed number (+155, 9 corrected).**
`{0,60}` had no CR behind it; CR 614.1a states no distance, so it was REMOVED,
not widened. Removing it exposed a **missing created-ability guard** the window
had been hiding by one character.

**`2d64b1f` D6 — the cost head is STRUCTURE, not a verb list (+47).** The work
order's prescription (reuse the derived CR 701 list) was measured and catches
only 11 of 27 — `return` and `put` are not keyword actions. CR 113.3b's
`[Cost]: [Effect]` is the claim.

**`9693441` D8 — keyword lists (+95).** Stated as 29 semicolon lines; the real
defect was a **seam between the two keyword paths**, and 61 comma-joined lines
had it too.

**`1b443f2` FINDING — S7's "zero-cost next step" is NOT RUNNABLE. Nothing built.**
See §4.2 and decision-sheet item 8.

**`341a28b` step 2, first slice (+294).** Two named shapes, not a sweep:
`enters? as` (the 57-card clone family, lost to a plural-only test) and the
**static grant** (237). Took **two** tightenings, both found by reading output.

---

## 4. NEXT WORK ITEM — proceeds WITHOUT asking

**`PRE-STEP-2-AUDIT-2026-08-04.md`'s D3, D4, D5, D6 and D8 are all CLOSED.**
D7 was a measurement correction, D9 is a Captain ruling (Phase B), and D1/D2
were closed on 2026-08-04. **What remains of that audit is step 2 itself.**

### 1. Step 2, continued — one named shape at a time

**The first slice is done** (`341a28b`, `docs/STEP-2A-STATIC-GRANT-2026-08-05.md`).
**17,367 lines remain in `spell-or-static`, 5,153 of them permanent-side.**

**Never as a blanket sweep** — §7 of the EVE handoff is the reason: *"a RATIFIED
bucket used as a fallback"* would turn 1,883 wrong answers into answers that read
as resolved.

**The method that worked, and the one to continue with:** name a shape, measure
it, **read its output**, tighten until leakage is zero or explained, then take
the next shape. The static grant looked obvious and needed **two** tightenings —
97 instants leaked on the first, 65 on the second — and both were visible only in
the output, never in the idea.

### 2. The S7 gate — **NOT the one-liner three handoffs promised**

**READ `docs/S7-GATE-NOT-RUNNABLE-2026-08-05.md` FIRST.**
`family_tree_evidence.py` is hardcoded to the DERIVED-TAG-LAYER-SPEC v1
patterns: no arguments, no `argparse`, zero references to `parent`/`candidate`/
`codebook`. It cannot be pointed at a candidate. And **deck co-play — the first
named component of the substitute lens — has no data source in this repo**
(`data/raw/` is oracle-cards, oracle-tags, rulings).

**2 of the 3 components ARE available** (Tagger cross-reference over 35,550
tagged cards; exemplar panels). The proposal is §4 of that document; the design
question it turns on is §5 and is **on the decision sheet**.

### 3. Reviving `experiments/foundry_review.html`

Dark since 2026-07-17. `SESSION-START-PROCEDURE.md` names **ratification
throughput** as the real bottleneck, and this session is evidence: six passes of
DET work landed while the decision sheet only grew.

## 5. BLOCKED ON CAPTAIN — one sheet

Nothing here blocks the next work item. **Present as ONE decision sheet.**

| # | item | why it needs Captain |
|---|---|---|
| 1 | **`enchanted-player` as a §6 SCOPE token** (CR 303.4, 702.5) | **new vocabulary.** Nothing else names the player an Aura is attached to. Hits `draw-step-trigger` (Curse of Obsession, Righteous Authority) and `is-dealt-damage-trigger` (Grievous Wound). Those lines carry **no** scope token rather than a guessed one |
| 2 | **`<type>-counter-threshold-trigger`** | its NAME was its own question on the 14-row sheet and only the rows got the word. Reasoning is complete and needs **zero** new vocabulary (`COUNTER-PLACED-RULING` §3a). Absent from `grammars.json` |
| 3 | `main-phase-unqualified` (n=1, Carpet of Flowers) | §6b rule 1 says per-shape axes are free; does n=1 earn a token? |
| 4 | `to-graveyard-zone-unstated` (n=11) | per-card ruling; CR 110.1 decides each one but the printed words do not |
| 5 | **Widening `_MODAL_HEADER_RE`** (49 lines / 19 cards) | it is part of the **ratified** DET preprocessing standard v1 and is shared with `det_scan_texts()` — widening changes pattern scanning for every consumer |
| 6 | Migrations **logged, not executed** | `rule:lifegain-triggered-plus1-counter` → `rule:gain-life-trigger-plus1-counter` (also closes §14 Q5, open since 2026-07-31), the §2a `other-` pair, the three `delayed` slot-order renames. **Each is a codebook mutation — needs Captain's word AND the backup law** |
| 7 | `rule:postcombat-main-phase-trigger` under-populated | 2 of 10 cards; a membership addition |
| 8 | **What replaces deck co-play in the S7 substitute lens?** | **A** — accept a 2/3 lens (Tagger + exemplars, deck co-play reported UNMEASURED), satisfiable today at zero cost; or **B** — acquire deck data, the only thing that measures actual substitution, but a new external data source that interacts with the locked rule *"no card data in git, ever."* **Recommendation: A now, B logged.** `docs/S7-GATE-NOT-RUNNABLE-2026-08-05.md` §5 |

---

## 6. WHAT THIS SESSION PROVES

**"Ratification is mechanical — add the row and the gap closes" was HALF TRUE,
and the half that was false was silent.** The grammar is parsed at run time, so
adding the 14 rows closed 102 lines instantly — and stopped there, because 11 of
the 14 tokens had no `mark()` call to reach them. **A ratified token with no
emitter looks exactly like a ratified token with no members.** Same shape as
"a ratified standard with no caller"; nothing gates it.

**A markdown table is an API.** §2's table is machine-parsed to the first `###`,
so the "shapes we deliberately do NOT route" table I wrote under it was read as
**ratified vocabulary** — silently ratifying the two shapes it documented as
open. Caught by a routing diff, not by review. It is the **second** instance:
the parser's own comment records the first. §2f now carries the standing rule.

**Suspect the check — it fired three more times, and all three times the check
was mine.** A set-difference independence test that removed the very tokens it
was testing; a `have.get("Cumulative upkeep")` lookup that missed a title-cased
key and read as a parse failure; and `\d` in a `re.sub` *replacement* string,
which is a group escape. The last one failed **loudly** on all 159 forms, which
is why it cost minutes instead of a session.

**The most dangerous change is the one that moves a line OFF a ratified token.**
Across 1,546 moved lines, exactly **one** did — Pyramids, and it was a fix. The
two that would have been regressions (`Max speed — [Ability]` swallowing a whole
ability) were caught by the routing diff *before* landing, because the diff
reports re-routes separately from gap closures. **Keep that separation.**

**Reading every moved line is affordable and it works.** All 172 of D4's
non-`static` lines were read individually before the change landed; no false
positive survived. The five known false-positive shapes are now canaries in the
probe.

---

## 7. TRAPS TO ADD TO THE STANDING LIST

- **Any table under `## 2.` that is not ratified DELIVERY vocabulary belongs in
  a `###` subsection.** Prose and bullet lists are safe; a table is not.
- **`\d` in a `re.sub` REPLACEMENT is a group escape**, not the character class.
  Use a lambda. Cousin of the recorded `re.escape` trap.
- **A keyword matcher needs `\s+`, not `\s*`, before a non-cost parameter** —
  `\s*` made "EQUIP**PED** Warriors…" match `Equip [quality]`.
- **Split on commas AFTER trying the whole line**, never before: a keyword
  parameter may contain commas (`Ward—{2}, Pay 2 life.`).
- **A keyword whose parameter is an ABILITY must not be matched by the keyword
  path** — the wrapper's class would overwrite the inner ability's correct
  delivery (CR 702.178a, `Max speed — [Ability]`).
- **`instantiated_members` in `grammars.json` asserts codebook AXES.** Delivery
  nodes are not axes (TRIAGE-BATCH-1 §1c).
- **Set subtraction is the wrong tool for "does X depend only on Y"** — it
  removes members present in both.
