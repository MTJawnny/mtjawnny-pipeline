# SESSION HANDOFF — 2026-08-05

Supersedes `SESSION-HANDOFF-2026-08-04-EVE.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** Commits: `216e480` · `eda04be` · `3c78e50`.

**The session in one line: Captain ratified the 14 §2 rows, and ratifying them
turned out to have a mechanical half nobody had counted — 1,545 ability lines
were routed onto a correct DELIVERY token across three passes, and exactly ONE
line moved off a ratified token, as a fix.**

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
| **`docs/PRE-STEP-2-AUDIT-2026-08-04.md`** | the nine defects. **D3 and D4 are now CLOSED**; D5/D6/D8 are next and its numbers for them are still good |
| **`docs/D4-KEYWORD-FORMS-2026-08-04.md`** | the CR states a printed form in FOUR sentence shapes; five defects caught by measurement |
| **`docs/D3-MODAL-MODES-2026-08-04.md`** | modal inheritance, and the 49-line gap in the ratified modal regex |
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
| ruling registry | 89 docs · 127 ruling ids |
| **§2 DELIVERY vocabulary** | **45 tokens** (was 31) |
| routed ability lines | **61,900** (was 61,868 — +32, see D3 §5a) |
| **lines with NO ratified token** | **18,745** (was 20,290) |
| distinct ratified tokens in use | **64** (was 47) |
| baseline snapshot | `experiments/out/foundry/regression/p5-d3.json` |
| working tree | clean |

---

## 3. WHAT CHANGED — three commits

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

---

## 4. NEXT WORK ITEM — proceeds WITHOUT asking

**Each is its own measured pass: snapshot → change → `diff --strict` → read
every moved line → `invariance`.**

### 1. D5 — replacement templates (160 lines)

`foundry_shape_extractor.py`, the replacement matcher.
`\bwould\b.{0,60}\binstead\b|\bskips?\b|\benters? with\b|\benters? tapped\b`
misses 160 lines (gap min 61, median 89, max 173). **Do not widen the window —
parse the CR.** CR **614.1a/b/c publishes exactly three templates verbatim**, and
this is the same site as the 236-line *invisible* defect where only one of the
three was matched. `ed252a6`'s locked rule named this defect before any audit
found it.

### 2. D6 — activated cost heads with no mana symbol (30 lines)

`[{}]|\bsacrifice\b|\bdiscard\b|\bpay\b|\btap\b|\bexile\b|\bremove\b` loses 30
activated abilities (`Put a -1/-1 counter on this creature:`, `Return a Forest
you control to its owner's hand:`). **CR 701's keyword-action list is ALREADY
DERIVED in this same file** for the trigger verbs — reuse it rather than
extending the hand-list. One false positive to expect: a card *named*
**"Ultimate Magic: Meteor"**, where the colon is in the name.

### 3. D8 — semicolon-joined keyword lines (29 lines)

`keyword_line_tokens` splits on commas only (`Flying; banding`). No CR question.
**Note:** it now falls through to `keyword_form_tokens`, so fix the split in both
or hoist it.

### 4. THEN step 2 proper (≈5,647)

Against the corrected partition in `PRE-STEP-2-AUDIT` §3 — **never as a blanket
sweep.**

### 5. Zero-token, unstarted

`python3 experiments/measure/family_tree_evidence.py` against the five populated
parent candidates — the S7 gate they have never been through.

---

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
