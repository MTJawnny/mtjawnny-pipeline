# AQ4 BENCHMARK — POPULATION AND SAMPLING CONTRACT

**Packet 2 of the AQ4 lower-model packet map
(`docs/AQ4-SEMANTIC-ARCHITECTURE-IMPLEMENTATION-CONTRACT.md` §32).**

**AQ4 IS NOT RATIFIED.** Nothing in this directory changes production, ratifies
a dimension, mints a term, or chooses between the candidate architectures. It
builds the pre-registered §21 population and the deterministic sampler, and
stops there.

| | |
|---|---|
| builds | cohorts 1, 2, 3, 6-open, 7, 8 (published) · cohort 4 (drawn, identities withheld) |
| does NOT build | cohort 5 (packet 3) · any answer key (packet 3+) · any candidate encoding (packets 5–6) |
| regenerate | `python3 experiments/aq4_benchmark/aq4_population.py --build` |
| sizes only | `… --census` |
| controls | `… --selftest` (NC-P2-1 … NC-P2-7) |

---

## 1. WHAT IS COMMITTED, AND WHY EACH PIECE EXISTS

| file | role |
|---|---|
| `aq4_population.py` | the machinery: universe, per-card structural facts, cohort construction, the sampler, and the seven negative controls |
| `sampling.json` | **the commitment** — cohort-4 seed, the per-stratum rule, the ordering law, the K constants. Changing a value here changes the pre-registered population |
| `cohorts/cohort-N.json` | the OPEN cohort lists — `oracle_id` only (§7) |
| `population-manifest.json` | counts, hashes, stratum summary, both overlap matrices, trap-coverage map, measured-empty classes |

Everything regenerates from the committed script plus the corpus. Nothing here
was typed by hand except the constants in `sampling.json`, and each of those
carries its rule beside it.

---

## 2. THE SAMPLING LAW

Recorded here rather than left in code, because §8 of the packet directive
requires it to be readable without reading the implementation.

**Corpus identity.** `corpus_ref` from `foundry_codebook.corpus_ref_current()`
— the snapshot date every quote in this repo is drawn from. Current value is
recorded in `population-manifest.json`, not hardcoded here, so it moves with
the corpus instead of rotting in a constant.

**Candidate universe.** `foundry_common.load_corpus_gated()` — Gate #0,
ratified batch-6 D1 — minus Alchemy (`A-`) rows whose paper twin is present.
The benchmark does **not** alter corpus membership: Gate #0's Commander arm
applies here exactly as in every other foundry stage. The Alchemy cut
implements the ratified *"paper rows preferred over A- variants in sampling,
resolution, and emit"*; it is a **preference**, so a twinless `A-` row would be
kept, and the manifest reports how many of each rather than assuming. On the
current corpus all 216 have a twin, and detecting that required stripping the
`A-` prefix from **each face** — `A-Rowan, … // A-Will, …` is not matched by a
leading-prefix strip, which reports every Alchemy row as twinless.

**Stable ordering before sampling.** Pools are sorted by `oracle_id`. Selection
order is a SHA-256 keyed order. On-disk order is `oracle_id` again. Never dict
insertion order, never filesystem order, and **never card-name order** — name
order is a recorded defect in this repository (Tier 3's shipped top-10 is an
alphabetical slice of a score tie, and `A-` rows sort first).

**PRNG.** There is no stateful PRNG. Selection is
`sorted(pool, key=lambda oid: (sha256(label + "\0" + oid).hexdigest(), oid))`.
A stateful generator reproduces only against a matching library, and cohort 4
must regenerate byte-identically at packet 9 — months and possibly a Python
version later — or §22 step 6 cannot pass. The repository precedent
(`foundry_object_lattice.write_report`'s `random` with a fixed seed) is a
single-session review sheet, so it is precedent for *seeding*, not for the
generator. Ties break on `oracle_id`, so the order is total even under a
collision.

**Domain separation.** Every draw is keyed with its own label. Two classes
drawing from the same pool therefore cannot select the same cards by
construction, rather than by luck.

**Seed representation.** A UTF-8 string, stored in `sampling.json`, hashed into
the selection key. Cohort 4's is `AQ4-C4-20260815`. **Cohort 5 has no seed
here and packet 2 does not choose one.**

**Per-stratum count.** `1`. See §4.

**Short strata.** A stratum smaller than the requested count yields everything
it has and is **reported** as short — never merged into a neighbour, never
dropped. §21 pre-registers the stratification, so silently collapsing a rare
cell would change the pre-registered population. On the current corpus there
are **0** short strata at `per_stratum = 1`.

**Duplicate prevention.** `oracle_id` is the only card key and the universe is
a dict keyed on it, so duplicates are structurally impossible. The draw reports
`duplicate_ids` anyway rather than trusting the structure.

**Cross-cohort overlap.** Open cohorts may overlap; membership is metadata and
both overlap matrices are published (§6). The one hard rule is
`holdout ∩ development = ∅`, enforced at **draw time** by
`draw_generic(exclude=…)` — a check after the fact can only report a leak it
cannot undo — and asserted by `assert_disjoint_from_development`.

**Exclusion policy.** Alchemy rows with a paper twin (above); nothing else.
No card is excluded for being hard, and no card is included for being easy.

**Output ordering.** JSON with `sort_keys=True`, `indent=2`, trailing newline.
Hashes are over the canonical form (`sort_keys`, tight separators).

---

## 3. HOW A COHORT MEMBER IS CHOSEN

Every cohort is a set of **structural classes**. A class carries a derivation
rule, a CR or ratified-primitive anchor, and its full qualifying population;
`K_PER_CLASS = 6` exemplars are then taken in keyed-hash order.

Six, not one, is the point: **a class with one member is a named exemplar with
a derivation written around it.** `_assert_classes_are_classes` HALTS on any
derived class below `MIN_CLASS_MEMBERS = 2`. Exactly one member is exempt and
labeled — `c1.active-volcano-named-case`, the §21-named historical failure,
which is included transparently as historical evidence and is *also* a member
of the reproducible `c1.modal-flattening` class. It is **not** a production
exception.

That guard has already fired once for real: `c7.no-text-noncreature` came back
with **0** members, because every no-oracle-text card in the universe is a
Creature. It is recorded in `empty_classes_measured` rather than deleted
quietly — an empty class is a fact about the corpus, and a class that vanishes
from a spec without a trace reads later as one nobody thought of.

### Text views, and why the choice is load-bearing

| view | what it is | used for |
|---|---|---|
| `base` | `det_scan_texts()[0]` — CARDNAME-canonicalized full text | anything that must agree with `foundry_qualifier_census.population` |
| `base_nr` | `base` with CR 207.2a reminder parentheticals removed | **every printed-template test** |
| `lines` | `ability_lines()` — reminder-stripped, split | CR 700.2 modality, segmentation |

Reading raw oracle text instead of `base` misses 1,478 cards on a CARDNAME
pattern and reports a clean zero (recorded as NC-E). Reading `base` where
`base_nr` is needed hits the opposite trap: `det_scan_texts` does **not** strip
reminder text, and a `choose one` search matches Spree's own reminder
("Choose one or more additional costs") and files additive modes as mutually
exclusive. Measured here too — scanning CR 701.3 `attach` against unstripped
text pulled in reminder sentences and took the class from 234 to 743.

---

## 4. COHORT 4 — THE STRATIFIED DRAW, AND THE BLINDNESS RULE

**Stratum = delivery token × action family**, exactly as §21 pre-registers.

- **delivery token** — the first in printed order from
  `deliveries_for_lines`. Grammar §2's ratified table, **including §2's
  `any-`/`other-` scope facet**. The domain guard asserts CONTENT and names
  any offending token; it consults the table **before** stripping a scope
  prefix, because `any-damage-to-creature` is itself a ratified key and
  stripping first turns it into `damage-to-creature`, which is in no table.
  The first draft stripped first and halted on three correct tokens.
- **action family** — the first CR 701 keyword action in **predicate**
  position, using packet 1's `cr701_keyword_actions` (parsed from the CR at run
  time, halt-guarded on content) and packet 1's boundary test. Without the
  boundary test, `counter` in *"with a +1/+1 counter on it"* is an action
  family and the corpus strata on object phrases.
- **null** is a JSON null rendering as `(none)`. It is the absence of a value,
  not a coined label.

Both coordinates reduce card→value by **first in printed order**. The
alternative — the card's whole token set — makes the stratum a power set and
strata nothing.

**Per-stratum count is 1: minimal complete coverage.** §21 pre-registers the
stratification and supplies no size, so one-per-cell is the only draw rule with
**zero free parameters**. A fixed total, a size floor, or proportional
allocation each introduce a number the contract does not supply, and §10 of the
packet directive forbids smuggling a population-size choice through
implementation. Current corpus: **795 non-empty strata → 795 cards, 0 short,
0 duplicates.**

### THE BLINDNESS RULE

Cohort 4 stays uninspected until extractor freeze (§21). It is **drawn** here
and its identities are never printed, never written to a tracked file, and
never returned by a default command. `--census`, `--build` and `--selftest`
report it as *stratum sizes plus a selection hash*. `cohort4_public()` is the
only route from the draw into the manifest and it strips `_identities`;
NC-P2-5 asserts that.

`--reveal-cohort4` exists and **refuses**, so the reveal is a deliberate act at
freeze time and cannot happen by running a reporting command. Packet 9
re-enables it.

**Stated plainly, because it is inherent to the pre-registered design and not
something this packet can fix:** §21 requires the sampling script *and* the
seed to be committed, so anyone holding this repository can regenerate cohort
4's identities. The commitment is cryptographic (`selection_sha256` pins what
was drawn, before anyone looks); the blindness is **procedural**. That is the
protocol §21 specifies, and the refusing flag is what makes the procedure hard
to breach by accident rather than merely discouraged.

---

## 5. COHORT 5 — MACHINERY ONLY

Packet 3 owns the holdout. Packet 2 contributes:

- `draw_generic(pool, seed, label, n, exclude=…)` — the generic sampler,
  with exclusion applied **before** the draw;
- `assert_disjoint_from_development(...)` — §22 step 8 as a halt.

**No seed is chosen. No identity is generated. No answer key exists.** There is
no code path in this directory that produces a holdout list.

---

## 6. COHORT 6 — THE OPEN/BLIND SPLIT

§21 requires the consumer-critical families half open, half in the holdout
draw. The split is keyed-hash order per family, **even index → open, odd index
→ reserved**, pre-registered in `sampling.json` and **independent of any
holdout seed** — so publishing the open half exposes nothing about the holdout,
and packet 3 can draw from the reserved half with its own seed. The reserved
half is never materialized and never printed. Open half is capped at 8.

Family derivations, all from objective existing primitives:

| family | derivation | class |
|---|---|---|
| `c6.removal` | carries an object-lattice class on destroy / exile / bounce | EXTRACT-3, ratified lattice |
| `c6.blink` | exile followed by return in one sentence | EXTRACT-4, packet-1 form test |
| `c6.counterspell` | CR 701.5 `counter` as an effect head in predicate position | EXTRACT-1 + boundary test |
| `c6.add-mana` | the CR 106.4 `add {mana}` template | EXTRACT-2 |

**`c6.add-mana` is named for the ratified primitive, not for §21's family
label, and the gap is real.** Grammar §4's `add-mana` verb is Captain-ratified
with CR 106.4 supplying the words verbatim, and it is the objective stand-in
for "ramp". The two are **not** the same set — a Cavern of Souls adds mana and
is fixing, not acceleration. Closing that gap means ruling what "ramp" is,
which is a ratification this packet may not make and a hand tag it may not
write. So the family is derived from the primitive, named after the primitive,
and the limitation is recorded here instead of being hidden by the label.

---

## 7. NO CARD DATA IN GIT — THE GOVERNANCE ARGUMENT

*"No card data in git, ever"* is a locked first-commit rule. §12 and §16 of the
packet directive make honouring it a hard check that outranks the AQ4 contract.

**Tracked cohort files carry `oracle_id` and nothing else** — no oracle text,
and no name, type line, characteristic or derived fact **attached to any
`oracle_id`**. Inclusion reasons describe the **class**, never the card.

Stated precisely, because a governance claim that is slightly false is exactly
what a later session would lean on: four card names do appear in the tracked
JSON — *Prey Upon*, *Cloudshift*, *Seize the Soul*, *Cavern of Souls* — all of
them inside class-descriptor prose ("the Prey Upon two-participant class"), and
the first three are the names §21 itself uses for those structural classes.
**A name in that position identifies a structure and binds to no `oracle_id`**,
which is the same shape as the `why` prose in tracked `experiments/moves/*.json`.
No mapping from name to id is published here, and no card's text is.

That is strictly narrower than the established, ratified precedent:

| tracked artifact | carries |
|---|---|
| `experiments/moves/*.json` (20 files, committed) | **701 distinct `oracle_id`s**, card names in `why` prose, and short **oracle-text evidence quotes** — 394 ids in one file. These are `foundry_ground_truth`'s seeds |
| `tags/cards.yaml` | `oracle_id` keys with card names in comments |

So oracle_ids in a curated, tracked spec artifact are not a new liberty; they
are how the ground-truth fixture and the tag layer already work. The rule's
actual subject is the **corpus** — `.gitignore` blocks `data/`, `*.jsonl`,
`*.parquet`, `*.sqlite`, i.e. a card *database*. `PICK-UP-HERE.md` §0AC states
the discriminator directly when it explains why C6 exists: tracking
`codebook.json` was refused because *"assertions carry oracle-text quotes"* and
that would mean *"publishing card text from a public repo"*.

**This directory publishes no card text at all**, so it does not reach the
question. **There is no conflict to return to Captain**, and none of the
narrower reading was weakened to get here.

Human review needs names; the compliant place for them is local, alongside
every other gitignored working sheet in this repository
(`foundry_locality.py --report`, `object_lattice_samples.json`). Resolve an id
with `foundry_common.load_corpus_gated()` — do not add a name column to a
tracked file.

---

## 8. NEGATIVE CONTROLS

`--selftest`. Each was **rigged red before it was believed**, and two were
re-aimed after first reading as broken — the recorded lesson is to aim a
control at the **code path**, not at the tool's name.

| control | asserts | rig |
|---|---|---|
| NC-P2-1 | determinism | same corpus + code + seed → identical selection hash |
| NC-P2-2 | seed sensitivity | a different seed moves 776 of 795 selections |
| NC-P2-3 | stratum preservation | collapsing every stratum to one cell: 795 strata → 1, 795 drawn → 1 |
| NC-P2-4 | no untracked leakage | plant an untracked `docs/` file holding real oracle_ids → cohort hashes unchanged; a doc-derived class is detectably different, so the comparison is live |
| NC-P2-5 | blind-cohort non-exposure | the `cohort_4` record carries 0 of 795 drawn ids; no cohort-5 seed |
| NC-P2-6 | development/holdout exclusion | a synthetic overlap forced into the argument HALTS |
| NC-P2-7 | no lattice-only regression | fight (149) and attach (229) exist, 366 of them **outside** the lattice population, and cohort 2 selects from both |

**Two were mis-aimed first, and both misfires are instructive.** NC-P2-4 began
as a grep of this file for a quoted `docs/` path and found **two** — its own
regex literal and its own message; a control that matches itself is the
overlapping-classes probe defect aimed at a negative control. NC-P2-5 began by
asserting that no drawn `oracle_id` appears anywhere in the manifest, which
fails for a reason that is not a leak: an open cohort draws from the same
universe, so some published members are independently also cohort-4 draws.
Twelve of 795, and the control now asserts exactly that identity.

---

## 9. WHAT THIS PACKET DELIBERATELY DID NOT DECIDE

- **Whether `this way` is a fourth relation kind.** It is in cohort 2 because
  packet 1 measured it as the largest unresolved reference form (1,088
  references). Nothing here assigns it a kind.
- **What "ramp" is** (§6).
- **Cohort 4's size beyond the zero-free-parameter rule** (§4). Changing
  `per_stratum` in `sampling.json` and regenerating is the whole cost, so this
  stays cheap to rule on.
- **Any semantic answer, for any card, in any cohort.** Inclusion reasons are
  structural. Answer keys are packet 3 and later, under the §22 firewall.
