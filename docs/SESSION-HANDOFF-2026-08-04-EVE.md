# SESSION HANDOFF — 2026-08-04 EVE

Supersedes `SESSION-HANDOFF-2026-08-04.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** Three commits: `8a4bb31`, `fa68b4e`, `ef0559f`.

**The session in one line: 1,928 ability lines were routed onto a correct
DELIVERY token, step 2 was stopped before it misrouted 1,883 more — and the
reason none of it was found earlier turned out to be a procedure defect, not a
diligence one.**

---

## 0. START HERE — and read §1 before you touch anything

`docs/SESSION-START-PROCEDURE.md` — now **six** gates. Gate 3b is new and it
exists because of this session; run it.

**IF NO TASK WAS GIVEN, §5's NEXT WORK ITEM IS YOUR INSTRUCTION.** Work it. Do
not stop to ask. Only two things need Captain's explicit word: **ratifying new
vocabulary** and **mutating the codebook**.

**The one thing to internalise before working:** the previous handoff had
**no READING MANIFEST section**, though Gate 1 and CLAUDE.md both instruct a
session to follow it. Nothing noticed. Four settled decisions were then
rediscovered from scratch. **A gate that points at a missing artifact fails open
silently.** If something this handoff promises is missing, say so out loud
rather than proceeding past it.

---

## 1. READING MANIFEST — indexed by TASK, not a flat list

A flat list can only contain what I already knew mattered. That is exactly how
this session lost half a day. **Find your task, read its row, and run its
`prior_art` command before writing anything.**

### Always, whatever you are doing

| | |
|---|---|
| `docs/SESSION-START-PROCEDURE.md` | six gates, short |
| `CLAUDE.md` | locked rules + traps |
| Gate 2 commands | live state is measured, never recalled |

### If you are touching the DELIVERY EXTRACTOR (the current work)

```
python3 experiments/foundry_prior_art.py <your topic>       # ← FIRST, always
python3 experiments/foundry_routing_regression.py snapshot experiments/out/foundry/regression/<name>.json
```

| read | why |
|---|---|
| **`docs/PRE-STEP-2-AUDIT-2026-08-04.md`** | the nine defects, the exhaustive partition, and **why step 2 is unsafe as written** |
| **`docs/EXTRACTOR-REPAIR-LOG-2026-08-04.md`** | passes done, and the harness workflow |
| `docs/KEYWORD-ROUTER-FIX-2026-08-04.md` | §2b router, and the trap that "the class always decides the slot" would destroy 16 ratified routings |
| `docs/CODEBOOK-NAMING-GRAMMAR.md` **§1, §2, §2a, §2b, §2d, §9** | the DELIVERY law. §2b is the one being implemented |
| `docs/DELIVERY-VOCABULARY-BATCH-2026-08-03.md` **§6** | **193 keywords already classified**; Ward 206 / Cumulative Upkeep 80 / Echo 50 already counted; the 51 UNSTATED already listed |
| `docs/TRIGGER-VERB-DERIVATION-2026-08-04.md` | why the verb set is DERIVED and must not be hand-extended |
| `docs/SPELL-OR-STATIC-AUDIT-2026-08-04.md` | the bucket that is blind by construction |

### If you are touching the CODEBOOK, an AXIS, or a SLUG

`docs/CODEBOOK-NAMING-GRAMMAR.md` **WHOLE** · `docs/PARENT-TREE-CANDIDATES.md` ·
`docs/FAMILY-TREE-EVIDENCE.md` · `docs/TRIAGE-BATCH-1.md`..`-7.md`
(Captain's annotations are authoritative) — and
`python3 experiments/foundry_slug_dossier.py <slug>` on **the name you are about
to WRITE**, not the one you started from.

### If you are touching KEYWORDS

`docs/KEYWORD-LEDGER-CANDIDATES.md` — carries the standing SUP-protocol rule
**"bare keywords / reminder text / procedural riders are never axes"**, and
names Phase B as their governed home. This answers most keyword questions
outright.

### If you are touching the PARENT layer

`docs/PARENT-LAYER-OPENING-PACKET-2026-08-04.md` · `docs/PARENT-TREE-CANDIDATES.md`
(S1–S7, T1–T2) · grammar **§6b** (SHAPE vs JOB).

### If you are about to write a DET pattern or read card text

`foundry_common.det_scan_texts()` is the **ratified DET preprocessing standard
v1** (2026-07-31). Use it, or state why you cannot.
`python3 experiments/foundry_prior_art.py --orphans` lists who bypasses it.

---

## 2. LIVE STATE — measured at handoff, with boundaries stated

| | |
|---|---|
| codebook | **565 axes · 359 active · 8,740 members — UNCHANGED, no mutation this session** |
| sha256 | `5fa27b70fabdce8d40e537907358522449d4ce642d80f6680314c1b2d2e7d93e` |
| lint | clean |
| family sweep | 6 blocking (the same 6) |
| definition drift | 35 — C1b 1 · C2 16 · C3 7 · C4a 3 · C4e 5 · C4f 3 (unchanged) |
| §2 DELIVERY vocabulary | 31 tokens (unchanged — **nothing was ratified this session**) |
| routed ability lines | **61,868** |
| lines with NO ratified token | **20,290** (was 21,366) |
| `loyalty` | **909** (was 7) |
| KEYWORD_HOME entries | **144** (was 138) |
| name-dependent deliveries | **1**, a harness artifact (was 63) |
| baseline snapshot | `experiments/out/foundry/regression/p2-loyalty.json` |
| working tree | clean |

---

## 3. CORRECTIONS — numbers that are no longer true

**Handoff numbers lag; these were wrong and are now measured.**

| stated where | was | is | why |
|---|--:|--:|---|
| spell-or-static audit §2, permanent-side | 9,942 | **9,235** | the old cut used the **root** type line, which sides an Adventure creature's static with its instant half. Face-aware is the right boundary |
| audit §6 step 2, "route ~7,976 lines to static" | 7,976 | **≈5,647** | the rest is loyalty, modal modes, keywords, replacements and triggers — **not statics** |
| audit §4, Fortify CR | 702.66a | **702.67a** | 702.66 is Delve |
| audit §4, Forecast CR | 702.56a | **702.57a** | 702.56 is Replicate |
| §2b, keywords with no §2 home | 55 | **49** | six were routed this session |
| audit §6 step 1, "757 lines" | 757 | **824** | +57 Unearth (unfound), +10 landwalk variants beyond the five basics |

---

## 4. WHAT CHANGED — three commits

**`8a4bb31` extractor — 1,928 lines corrected across four measured passes.**
§2b router (824: Equip 567, Unearth 57 off a *wrong ratified* token, landwalk
128 derived from CR 702.14a's template) · ABILITY_WORD restricted to the em-dash
(186) · trigger clause may not cross a created-ability quote (2) · loyalty
hoisted out of the cost gate (916).

**`fa68b4e` audit + harness.** Step 2 stopped; `foundry_routing_regression.py`.

**`ef0559f` Gate 3b.** `foundry_prior_art.py` + the procedure change.

---

## 5. NEXT WORK ITEM — proceeds WITHOUT asking

**Work them in order. Each is its own measured pass: snapshot → change →
`diff --strict` → read every moved line → `invariance`.** A pass that moves a
family it did not claim is caught by the count pins.

### 1. D4 — parameterized keyword lines (194 non-static + 1,757 static)

**The derivation is already found, and it is the whole difficulty of this
item.** Do NOT pattern-guess: *"Equip abilities you activate cost {1} less"* is
a static cost-reducer, **not** an equip line, and 23 of 217 candidates are false
positives of exactly that kind (card names, ability words).

**The CR states each keyword's printed form verbatim, immediately before
`means` — for 146 of 193 keywords:**

```
"Equip [cost]"        "Champion an [object]"    "Affinity for [text]"
"Modular N"           "Reinforce N—[cost]"      "Cumulative upkeep [cost]"
```

So build the matcher from `702.Na`'s own quoted form. `Ward 53 →
becomes-targeted-trigger`, `Equip 43 → activated`, `Craft 24`, `Cumulative
upkeep 23 → upkeep-trigger`, `Champion 12 → etb`, `Forecast 11`.

`python3 experiments/foundry_prior_art.py "keyword parameter" ward equip`

### 2. D3 — modal modes (504 permanent-side lines)

**Do not design this.** `foundry_common.expand_modal_bullets()` is written,
correct and **ratified 2026-07-31**; the extractor simply never called it.
Headers carry `etb` 201 · `activated` 64 · `cast-trigger` 33 · `begin-combat` 26
· and more, and every bullet is a MODE of that ability (grammar §1: *"modal
modes each earn their axis"*).

### 3. D5 · D6 · D8 (160 + 30 + 29)

Replacement's `would…instead` window is 60 chars; measured gaps run to 173.
Activated cost heads with no mana symbol (`Put a -1/-1 counter on this
creature:`). Semicolon-joined keyword lines (`Flying; banding`).

### 4. THEN step 2 proper (≈5,647)

Against the corrected partition in `PRE-STEP-2-AUDIT` §3 — **never as a blanket
sweep.**

### 5. Zero-token, unstarted, still worth doing

`python3 experiments/measure/family_tree_evidence.py` against the five populated
parent candidates — the S7 gate they have never been through.

---

## 6. BLOCKED ON CAPTAIN — one sheet, and one item came OFF it

**Still blocked: ratify the 14 §2 rows** from `SESSION-HANDOFF-2026-08-04.md` §8
(MAIN-PHASE · IS-DEALT-DAMAGE · TURNED-FACE-UP · GAIN-LIFE-TRIGGER ·
TO-GRAVEYARD · COUNTER-PLACED · DRAW-STEP). DET is wired for every one. Three
carry a real question — do not assume the answers. **Nothing changed there this
session.**

**UNBLOCKED — D9, ~1,229 lines, needs no ruling.** Flashback 209, Partner 129,
Foretell 54, Bestow 43 and 45 more keywords have no §2 home. I was going to ask.
**The docs already answered it:** `KEYWORD-LEDGER-CANDIDATES.md` carries the
standing rule that bare keywords are never axes and names **Phase B** as their
home. Found by Gate 3b, not by asking.

---

## 7. WHAT THIS SESSION PROVES

**Recall, not precision, is where everything hides.** Nine defects, and not one
appears as a wrong answer on a line the tooling classifies. They are all lines
nothing ever classified — and every report is built from what it *did* classify.

**A fallback bucket is not the danger; a RATIFIED bucket used as a fallback is.**
`spell-or-static` at least reads as unresolved. Sweeping it into `static` would
have made 1,883 wrong answers read as *resolved*. Unearth was the same failure at
1/33rd the scale, and it survived because nothing reports a wrong ratified token.

**Gate 4 fired three times, and all three times it was MY CHECK that was wrong** —
the "class always decides the slot" generalisation (would have destroyed 16
ratified routings), the metamorphic harness (195 reported, 132 self-inflicted),
and the prior-art probe itself (`re.escape` on a multi-word topic made it report
"0 mentions" on the very case it was built for). **Suspect the check.**

**Metamorphic testing is the cheapest audit tool in this project.** A card's
delivery cannot depend on its NAME. That single property, run corpus-wide,
closed in one pass what four sessions of sampling had missed — and it needs no
ground truth and no judgement. Look for more properties of this shape.

**A ratified standard with no caller is invisible to every gate.** Nothing
checked that one was wired in. `expand_modal_bullets` has been correct and
unused since 2026-07-31. `--orphans` now measures it: **4 modules use the
ratified pipeline, 19 bypass it**, including both load-bearing classifiers.

---

## 8. TRAPS TO ADD TO THE STANDING LIST

- **A gate that points at a missing artifact fails open.** The previous handoff
  had no READING MANIFEST and nothing said so.
- **Dossier the TOPIC, not just the slug.** Gate 3b.
- **`re.escape` before a separator substitution welds a backslash to the
  character class** — silently matches a literal `[`.
- **A trigger clause must never cross into a quoted created ability**, and the
  fix for a missing event verb is structural, not another verb on a list.
- **The CR writes costs as `[Cost]`.** Any matcher that wants a real cost token
  will silently drop every keyword whose CR form uses the placeholder.
