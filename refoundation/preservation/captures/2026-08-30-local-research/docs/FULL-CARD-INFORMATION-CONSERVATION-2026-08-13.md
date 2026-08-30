# FULL-CARD READ AND INFORMATION CONSERVATION — audit

**2026-08-13.** Read-only. Zero codebook mutation, no DET pass, no API calls.
Gate 2 green (14 gates, 13 pass, 1 known-excused `family_sweep`).

**Shipped artifact that changes: NONE.** This is an input-substrate correctness
audit.

**The headline is not "all producers use `det_scan_texts`".** Text conservation
is measured perfect and two historical failure modes are now structurally
impossible — but **context and structure are a different question, and the
answer there is worse.** Flattening is invisible at the card level on 41
measured cards, and the object lattice's own fact survives the deletion of the
activation cost that owns it.

---

## 1. REPRESENTATION DATA-FLOW MAP

```
Scryfall JSONL  ──►  fc.load_corpus_gated()          32,557 cards (Gate #0)
                          │
                          ▼
              tier_engine.get_raw_faces(card)        ◄── THE ONE FACE READER
                          │                              (product AND foundry)
        ┌─────────────────┴──────────────────┐
        ▼                                    ▼
fc.full_oracle_text()                tier_engine.build_card_doc()
  faces joined with "\n"               per-face, per-paragraph
        │                                    └─► Searcher A (shipped)
        ▼
fc.canonicalize_self_reference()   name → "~"
        ▼
fc.det_scan_texts()  =  [canon full text, *modal-bullet expansions]
        │
        ├─► foundry_object_lattice   (object-class facts)
        ├─► foundry_shape_extractor  (delivery rows)  ─► fx.deliveries_for_lines
        ├─► foundry_det_pass         (AUTHORITATIVE WRITE)
        └─► foundry_visibility_audit / reach_census   (validators)

fc.build_review_card_record()  full_oracle_text + faces[]  ─► SYNTH/batch prompts
```

**`foundry_common.full_oracle_text` delegates to `tier_engine.get_raw_faces`.**
That single fact answers most of the face question: the shipped product and the
foundry share one face extractor, so a face cannot be dropped by one and not the
other.

---

## 2. PRODUCER COVERAGE — the live census, re-measured

`foundry_prior_art.py --orphans`, run this session:

| | count | CLAUDE.md records |
|---|--:|--:|
| USE `det_scan_texts` | **8** | 4 |
| BYPASS it while still reading card text | **22** | 19 |

**CLAUDE.md's "STILL 4 and 19" is stale** — it says the number had not moved
since 2026-08-04. Both sides have grown. That line is itself a carried-forward
count, which is the trap the same file names.

| producer | role | faces | all text | truncates | structure | context | evidence |
|---|---|---|---|---|---|---|---|
| `foundry_det_pass` | **authoritative writer** | all | all | no | rows | delivery | quote |
| `foundry_object_lattice` | producer | all | all | no | clause | **no** | quote |
| `foundry_shape_extractor` | producer | all | all | no | line/mode | delivery | line |
| `foundry_visibility_audit` | validator | all | all | no | option | joins | — |
| `foundry_reach_census` | reporter | all | all | display only | — | — | — |
| `foundry_ground_truth` | validator | all | all | display only | line | delivery | quote |
| `foundry_punctuation_audit` | validator | all | all | no | line | — | — |
| `foundry_definition_drift` | validator | all | all | no | — | — | — |
| `foundry_routing_regression` | validator | all | all | no | line | — | — |
| `foundry_assemble_batch*` (6) | model input | all (`build_review_card_record`) | all | **definition only** | faces[] | — | required |
| `foundry_consolidate*` (4) | model input | all | all | definition only | — | — | required |
| `tier_engine` | **shipped consumer** | all | all | no | per-face/para | — | — |

**No producer truncates oracle text.** Every `[:N]` found is a display slice in
a report (`[:110]`, `[:96]`, `[:80]`, `[:70]`). The one real narrowing is
`condense_definition_for_prompt(definition, max_chars=220)`, which shortens an
**axis definition** for a model prompt — not card text — and is documented as
such at its call site.

**A bypasser is not a defect.** The four validators that bypass are
line-anchored parsers needing per-line granularity the pipeline does not return;
`--orphans` says exactly this. Their contract is narrower on purpose.

---

## 3. THE THREE MEANINGS OF COMPLETE

### 3.1 COMPLETE TEXT — ✅ measured perfect

Corpus-wide: for every card, every paragraph of every face compared between
`tier_engine.get_raw_faces` and `det_scan_texts[0]`.

```
cards                                   32,557
paragraph-count MISMATCH raw -> scan         0
cards with no oracle text on any face      340   (vanilla; correct)
most paragraphs on one card                  8   (Coralhelm Commander)
```

### 3.2 COMPLETE STRUCTURE — ◐ preserved in the row layer, lost in the string

`fx.deliveries_for_lines` keeps every unit separable. Verified live:

| shape | card | result |
|---|---|---|
| planeswalker | Nicol Bolas, Planeswalker | 3 loyalty abilities, separate rows |
| Saga | History of Benalia | chapters `I, II` and `III` separate |
| Class | Barbarian Class | level bars separate, `activated` each |
| choose one | Dawnbringer Cleric | header + 3 bullets, all inherit `etb` (D3) |
| choose two | Silumgar's Command | header + 4 bullets separate |
| split | Dead // Gone | both halves |
| Adventure | Brazen Borrower // Petty Theft | both parts |
| transforming DFC | Delver of Secrets | both faces |
| ability word | Triton Cavalry | `Heroic —` stripped, `cast-trigger` found |
| restriction | Kalitas | cost and payload on one `activated` row |

**But `full_oracle_text` joins faces with `"\n"`, the same separator as a
paragraph break.** Measured: **625 of 836 multi-face cards** have at least one
face containing an internal `\n`, so in the joined string a face boundary is
indistinguishable from a paragraph boundary.

**This is currently benign and already guarded**, which is the honest reading:
house proximity scoping is `[^\n]*` and cannot cross a newline, and
`foundry_visibility_audit` asserts **0 of 45 ratified DET patterns match across
a face boundary** over 820 multi-face cards. The structure is absent from the
string and recovered by a guard, not by the representation.

### 3.3 COMPLETE CONTEXT — ✗ the real gap

`foundry_visibility_audit`, live, using its own ratified definitions:

| category | definition | measured |
|---|---|---|
| **DROPPED** | option produced no delivery row at all | **0** |
| **UNSCANNED** | no DET pattern could ever match this effect text | **0** |
| **UNCONTEXTED** | scannable, but never joined to the header that says WHEN | **31 of 3,497** |
| band content unscanned / not joined | CR 711.2 / 716.2 striations | 0 / 0 |

Those three categories are adequate; no new vocabulary is needed.

---

## 4. NEGATIVE CONTROLS — every one on an isolated copy, corpus untouched

**Three of five were mis-aimed on the first attempt** and each first read as
"the guard is broken". That is this repository's measured base rate and it is
reported rather than hidden.

| control | construction | result |
|---|---|---|
| **NC-A later ability dropped** | Vraska the Unseen cut at char 104, *before* its `−3: Destroy target nonland permanent` | `['nonland-permanent']` → `[]` — **DETECTED**, the class anchor fails |
| **NC-B face dropped** | Brazen Borrower, Adventure half removed | `['nonland-permanent']` → `[]` — **DETECTED** |
| **NC-C context dropped** | Kalitas, `{B}{B}{B}, {T}: ` deleted, payload kept | delivery `activated` → `None` (**detected**); object fact `['creature']` → `['creature']` (**NOT detected**) |
| **NC-D flattening** | Requisition Raid's exclusive modes vs two independent sentences | both → `['artifact','enchantment']` — **INVISIBLE at card level** |
| **NC-E probe drift** | `~ deals` against raw text vs `det_scan_texts` | raw **0**, pipeline **1,478** — **SURFACED** |

NC-A's first two aims failed because the fact sat *inside* the cut. NC-D's first
fused form used `and`, which the target-boundary rules correctly split. Both
were corrected by aiming at the code path, not the tool's name.

**NC-E is the strongest single number in this audit:** a probe reading raw
oracle text instead of the pipeline misses **1,478 cards** on a CARDNAME
pattern and reports a clean zero.

---

## 5. FLATTENING — measured, not argued

**41 cards** print `choose one` and carry 2+ object-lattice facts proven by
*different* quotes — mutually exclusive modes presented as a card-level bag.

```
Requisition Raid   destroy-artifact + destroy-enchantment   (choose one)
Rain of Rust       destroy-artifact + destroy-land          (choose one)
Active Volcano     bounce-land      + destroy-permanent     (choose one)
```

**Within one action family this is close to harmless** — "choose one: destroy
artifact / destroy enchantment" and "destroy target artifact or enchantment"
resolve to the same single object, and M8 already rules the OR case gets both
class tags.

**Across families it is a live hazard.** Active Volcano asserts both a bounce
fact and a destroy fact; a Budget Swapper matching "destroys permanents" would
offer a card that destroys *or* bounces, never both. NC-D proves the card-level
bag cannot tell that shape from a card that genuinely does both.

**Locality is recoverable, not represented.** Each fact carries the bullet that
proves it, so a consumer *can* reconstruct exclusivity by string-matching quotes
back to modes — the same recovery `foundry_ground_truth` already guards via its
fatal unanchored-seed check.

---

## 6. THE ELEVEN QUESTIONS, ANSWERED DIRECTLY

1. **Part of a card without halting?** No. 0/32,557 paragraph mismatches; no classifying producer truncates.
2. **Omit a face?** No. One shared reader, `tier_engine.get_raw_faces`; `full_oracle_text` delegates to it.
3. **Miss later abilities?** No — and NC-A proves the guard fails when one is removed.
4. **Effect text without its context?** **Yes.** NC-C: deleting Kalitas's activation cost changes the delivery token and leaves the object fact identical. The lattice fact carries no cost, timing or restriction.
5. **False combined effect?** **Yes, 41 cards**, and NC-D shows it is invisible at card level.
6. **Probes same preprocessing?** 8 use / 22 bypass. Validators that bypass are justified (line granularity); NC-E shows the cost when one is not.
7. **One canonical representation?** **Partly.** Canonical for faces (`get_raw_faces`) and for DET text (`det_scan_texts`). **No canonical *structured* reader** — structure lives only in `deliveries_for_lines`, which the object lattice does not consume.
8. **Defect or future risk?** Text: neither. Structure: future risk with a working guard. Context/flattening: **live**, bounded at 41 cards, consumer-layer.
9. **Historically impossible now?** The 150-char partial read (no truncation path exists in any classifying producer) and single-face reads (one shared extractor).
10. **Still possible?** Context loss, modal flattening, and probe drift — 1,478 cards on one pattern.
11. **Smallest change before expanding Searcher B?** **None to the reader.** See §7.

---

## 7. RECOMMENDATION — no change to the reader

The reading layer is sound. Text conservation is perfect, faces are canonical,
and every adversarial shape stays individually reachable. **Strengthening the
reader would fix nothing this audit found.**

The two live gaps are both *representational*, not *read* failures, and both are
already open decisions:

- **Effect locality / context** is `FL-2` in
  `THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md`, folded into **AQ4** — the
  assertion records a quote and no `face`/`ability`/`mode` coordinate.
- **Flattening** is the same field, one layer up: exclusivity cannot be
  expressed without effect identity.

**Creating a canonical structured card reader would be a new architecture
decision, so it is not implemented here.** It is also the natural home for AQ4's
answer, and pre-building it would pre-commit that ruling.

**One documentation correction is warranted and narrow:** CLAUDE.md's orphan
count is stale (4/19 → 8/22). Not corrected in this read-only pass; flagged.

---

## 8. GUARDS AND BLIND SPOTS

| failure class | guard today |
|---|---|
| text lost in a transform | `foundry_punctuation_audit` (conservation A/B/C) |
| option unreachable | `foundry_visibility_audit` DROPPED/UNSCANNED/UNCONTEXTED |
| pattern crossing a face | visibility audit, 0 of 45 over 820 cards |
| later ability lost | class anchors + grammar fixtures (NC-A) |
| face lost | class anchors (NC-B) |
| membership lost | tracked directional floor + per-class ratchet |
| wrong-since-forever token | `foundry_ground_truth` (delivery only) |

**Blind spots no guard sees:**

1. **Modal exclusivity** — nothing asserts that two facts on one card are
   mutually exclusive. 41 cards.
2. **Context stripping that leaves the payload intact** — NC-C; the object
   lattice's fact is unchanged when its cost is deleted.
3. **Probe drift** — no gate compares a probe's representation against the
   producer's. `--orphans` reports the count and ratchets nothing.

---

## 9. CAPTAIN DECISIONS

None new. Both gaps this audit found are already open as **AQ4** and its
sub-item **FL-2**. Raising them again as fresh decisions would be the
duplication CLAUDE.md's design goal #1 forbids.

The audit's contribution to those rulings is evidence, not a new question:
**41 flattened cards, 625 of 836 face-ambiguous joins, 31 uncontexted options,
and NC-C proving an object fact outlives the cost that owns it.**

Unchanged and unresolved on purpose: controller/ownership scope,
`targeted-destroy-token`, flicker/removal taxonomy, and every repaired
target-boundary behaviour.
