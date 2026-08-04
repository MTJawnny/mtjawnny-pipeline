# ⚠ SUPERSEDED — see `docs/SESSION-HANDOFF-2026-08-07.md`

This handoff is closed. Its NEXT WORK ITEM #1 (widen `ABILITY_WORD`) was
done as a CR 207.2c parse; items #2/#3 and the trap SWEEP are carried
forward and are the 08-07 handoff's §4.

---

# SESSION HANDOFF — 2026-08-06

Supersedes `SESSION-HANDOFF-2026-08-05.md`. **Zero API calls. Arc spend
unchanged at $90.51 / $140.** Six commits, `5a6479b` .. `db32841`.

**The session in one line: step 2 continued through three named shapes (2,166
gap lines closed, zero regressions), then Captain's two audits turned the pass
inward — six of CR 205.2a's card types were unreachable, every CR 205.3 subtype
list was being harvested instead of parsed, the damage family named 2 of CR
120.1's 4 recipients while DEFAULTING the rest onto a wrong ratified token, and
one paragraph turned out to hold up to three abilities.**

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
| **`python3 experiments/foundry_system_map.py`** | **RUN THIS FIRST.** The five stages, and which of each stage's lists is CR-parsed vs still heuristic. **Generated, so it cannot go stale.** It ends with the one question that finds defects in this codebase |
| `docs/SESSION-START-PROCEDURE.md` | five gates, short |
| `CLAUDE.md` | locked rules + traps (**12 new traps this session**) |
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
| **`docs/AUDIT-5-2026-08-05.md`** | **the five open findings and their proposed fixes — this is your work list** |
| `docs/STEP-2A-STATIC-GRANT-2026-08-05.md` · `-2B-` · `-2C-` | the three step-2 slices; the method that works |
| **`docs/LINKED-ABILITIES-CR607-2026-08-05.md`** | one paragraph can hold 3 abilities; CR 603.12 is the discriminator |
| **`docs/VOCABULARY-COMPLETION-2026-08-05.md`** | CR 120.1/400.1/303.4b; **why a fallback is a wrong answer with a ratified name** |
| **`docs/CR-LAW-AUDIT-2026-08-05.md`** | the register: what is parsed from the CR, what is still heuristic |
| `docs/SELF-REFERENCE-CR205-2026-08-05.md` | a data source can be a hand-list wearing better clothes |
| `docs/CODEBOOK-NAMING-GRAMMAR.md` **§1, §2, §2a, §2b, §2e, §2f, §6, §9** | the DELIVERY law. **§2 is now 53 tokens**; §6 gained `enchanted-player` |
| `docs/PRE-STEP-2-AUDIT-2026-08-04.md` | D1–D6, D8 closed; what remains is step 2 |
| `docs/SPELL-OR-STATIC-AUDIT-2026-08-04.md` | the bucket that is blind by construction |

### If you are touching the CODEBOOK, an AXIS, or a SLUG

`docs/CODEBOOK-NAMING-GRAMMAR.md` **WHOLE** · `docs/PARENT-TREE-CANDIDATES.md` ·
`docs/FAMILY-TREE-EVIDENCE.md` · `docs/TRIAGE-BATCH-1.md`..`-7.md` — and
`foundry_slug_dossier.py` on **the name you are about to WRITE**.

### If you are touching KEYWORDS

`docs/KEYWORD-LEDGER-CANDIDATES.md` — bare keywords are never axes.

### If you are touching the PARENT layer

`docs/PARENT-LAYER-OPENING-PACKET-2026-08-04.md` · `PARENT-TREE-CANDIDATES.md`
(S1–S7, T1–T2) · grammar **§6b** · `docs/S7-GATE-NOT-RUNNABLE-2026-08-05.md`.

---

## 2. LIVE STATE — measured at handoff

| | |
|---|---|
| codebook | **565 axes · 359 active · 8,740 members — UNCHANGED, no mutation this session** |
| sha256 | `5fa27b70fabdce8d40e537907358522449d4ce642d80f6680314c1b2d2e7d93e` |
| lint | clean |
| family sweep | 6 blocking (the same 6) |
| definition drift | 35 (unchanged) |
| **§2 DELIVERY vocabulary** | **53 tokens** (was 45) |
| §6 SCOPE | **+`enchanted-player`** |
| **deliveries emitted** | **61,945** (was 61,907 — the linked-ability split adds rows) |
| ratified / unrouted | **45,672 / 16,273** (unrouted was 18,162) |
| `spell-or-static` | **15,181**, of which **4,931 permanent-side** (was 6,821 when step 2 opened) |
| distinct tokens in use | **68** |
| keyword homes | **150** (was 148) |
| self-reference noun set | **568**, all CR-parsed (was 447, corpus-harvested) |
| ruling registry | **103 docs** |
| baseline snapshot | `experiments/out/foundry/regression/p18-linked-final.json` |
| working tree | clean |

---

## 3. WHAT CHANGED — six commits

**`5a6479b` step 2b — the conditional static (+443).** `^as long as` → `static`
(CR 113.3d + 604.2). The probe measured 400 and the classifier moved 443: the
probe matched the raw line, the classifier the ability-word-stripped body.

**`4d46f3c` step 2c — CR 614.1d + the self-reference statement (+1,448).** The
"931-line `this creature …` group" was **not one shape** — 738 of those lines
are burn spells. **CR 113.3a is the cut**: a spell ability exists only on an
instant or sorcery.

**`552eee1` self-reference vocabulary from CR 205.2a.** Six card types
unreachable, including CR 109.2d's own `this scheme`. Plus the Oxford-comma
split that dropped the last member of every CR 205 list behind a guard that
counted.

**`f7be713` CR-law audit — all ten CR 205.3 subtype lists parsed.** The corpus
became a TEST, not a source. It immediately found the CR/Scryfall apostrophe
mismatch and that **the local CR snapshot is stale**.

**`df7e8db` complete all incomplete vocabulary.** CR 120.1's source side named
2 of 4 recipients and **defaulted** the rest; 62 lines moved off a wrong
ratified token.

**`db32841` read past punctuation (CR 603.11 / 607.2h).** 37 lines carry a
second ability; Keranos carries three.

---

## 4. NEXT WORK ITEM — proceeds WITHOUT asking

### 1. `AUDIT-5`'s three DET defects — in this order, one at a time

All three are **recall** failures, all **DET**, **none needs vocabulary**. Take
them one per diff, largest blast radius first.

| # | fix | lines | why this order |
|---|---|--:|---|
| **1** | **widen `ABILITY_WORD`** to accept digits and punctuation before the em-dash (`Descend 4 —`, `Prototype {1}{B} —`, `Nitro-9 —`, `No One Dies! —`) | **121** | it runs **before every branch**, so it is the highest blast radius on the list. **Do it first and ALONE**, and read the whole diff |
| **2** | **`\benters?\b`** in the etb trigger test — plural "one or more … **enter**" | **43** | `etb` is the largest trigger family (5,713); read the diff |
| **3** | **drop the `\b` after `as `** in the CR 614.1c branch so `~` can match | **25** | `~` is not a word character — the trap this project fixed at two other sites |

**After each: `diff --strict`, read every moved line, determinism ×2,
invariance, Clue ground truth.**

### 2. Then step 2 continues — the anthem group

**15,181 lines in `spell-or-static`, 4,931 permanent-side.** Next named shape:
`creatures you control` (179) · `other creatures you control` (78) ·
`each creature you control` (61). `rule:tribal-anthem-buff` has a KEEP ruling
reconfirmed in batches 4, 6 and 7 — **but nothing rules its DELIVERY**, so this
is routing, not vocabulary.

Then: `escapes with` (12) — CR 113.6h chains explicitly to 614.12's replacement
section; the reasoning is written in `STEP-2C` §2b and needs only its own pass.

### 3. The trap SWEEP — not another point fix

Two of `AUDIT-5`'s findings are traps this project **already fixed elsewhere**:
`~` is not a word character (fixed at two sites, live at a third) and an
inflection is not a shape (third instance). **Grep every branch for both
patterns rather than fixing the one the audit happened to surface.**

---

## 5. BLOCKED ON CAPTAIN — one sheet

Nothing here blocks the next work item.

| # | item | why it needs Captain |
|---|---|---|
| 1 | **Retire `kicker` from §2's DELIVERY table** | `AUDIT-5` §1. CR 702.33a makes it a **static ability**, §2b derives keyword deliveries from that class, and all 216 lines correctly route to `static`. The token has **0 members and no emitter**. Retire it as `delayed` was retired by §2d — but **retiring ratified vocabulary is Captain's word** |
| 2 | **Refresh `docs/mtg-comprehensive-rules.md`** | the local CR is a vendored snapshot and is **behind the corpus**: `Chorus` is a printed spell type absent from CR 205.3k's five. Held in a dated CR-LAG register meanwhile. The CR is this project's only non-mirror |
| 3 | `main-phase-unqualified` (n=1, Carpet of Flowers) | §6b rule 1 says per-shape axes are free; does n=1 earn a token? |
| 4 | `to-graveyard-zone-unstated` (n=11) | per-card ruling; CR 110.1 decides each one but the printed words do not |
| 5 | **Widening `_MODAL_HEADER_RE`** (49 lines / 19 cards) | part of the **ratified** DET preprocessing standard v1, shared with `det_scan_texts()` |
| 6 | Migrations **logged, not executed** | `rule:lifegain-triggered-plus1-counter` → `rule:gain-life-trigger-plus1-counter` (closes §14 Q5), the §2a `other-` pair, three `delayed` slot-order renames. **Each is a codebook mutation — Captain's word AND the backup law** |
| 7 | `rule:postcombat-main-phase-trigger` under-populated | 2 of 10 cards; a membership addition |
| 8 | **What replaces deck co-play in the S7 substitute lens?** | **A** — a 2/3 lens (Tagger + exemplars, deck co-play UNMEASURED), free today; or **B** — acquire deck data, a new external source interacting with *"no card data in git, ever."* **Recommendation: A now, B logged.** `docs/S7-GATE-NOT-RUNNABLE-2026-08-05.md` §5 |
| 9 | **§2a prefix-stripping must be anchored to the token list** | `AUDIT-5` §1 finding 2. `any-` means "no combat restriction" in four token NAMES and "source included" as a §2a prefix; any consumer that strips blindly corrupts them. A convention change, so Captain's call |

---

## 6. WHAT THIS SESSION PROVES

**A fallback is a wrong answer with a ratified name.** The damage family's bare
`deals? damage to` arm returned `any-damage-to-creature` for every recipient it
did not recognise — 53 lines. A census counts what is *missing*; these were
present and false.

**A DATA SOURCE can be a hand-list wearing better clothes.** The self-reference
set was *derived*, from live corpus data, and still missing 6 of 15 card types,
because the gate decides what the corpus can contain. **Ask what the source
cannot hold**, not whether a human typed it.

**A halt-guard must assert CONTENT, not cardinality.** `type_vocabulary`'s
Oxford-comma split produced `and vanguard` and the `len() >= 15` guard stayed
green over a three-item loss.

**Captain's two questions found more than six passes of my own work did.**
"Make sure to create self reference for rules for every card type" and "cards
can have multiple effects separated by punctuation" each opened a defect class
that no gate in this toolchain reports. **The gates verify what a pass changed;
they cannot ask whether the pass was looking at the right thing.**

---

## 7. TRAPS ADDED TO CLAUDE.md THIS SESSION

- A probe must consume the **same preprocessing** as the classifier it measures.
- A new **tail branch** can only claim lines that already reached the fallback —
  zero re-routes becomes structural, not lucky.
- `build_keyword_homes` runs `parse_delivery` over each keyword's CR text, so
  any classifier change can move `keyword_homes`.
- Name a shape by **the CR rule that decides it**, never by the words that open
  the line.
- A **carried-forward count** in a handoff is not a measurement.
- A **data source** can be a hand-list wearing better clothes.
- The CR prints a **curly apostrophe**; Scryfall prints a straight one.
- The local CR is a **vendored snapshot** and can fall behind the corpus.
- A **period is not an ability boundary; a paragraph is** (CR 113.2c) — but
  CR 603.11/607.2h put several abilities in one paragraph, and CR 603.12 is the
  discriminator.
- Strip an **ability-word prefix BEFORE splitting sentences**.
- **"Reached `spell-or-static`" is NOT "is static"** — gate on a positive test.
- When a rule names a card type, **ask the CR which other types it covers**.
