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
| controls | `… --selftest` (NC-P2-1 … NC-P2-7, RC1 … RC6) |

---

## 1. WHAT IS COMMITTED, AND WHY EACH PIECE EXISTS

| file | role |
|---|---|
| `aq4_projection.py` | **packet 4** — the ownership-neutral evaluation projection: schema validation, canonicalization, the semantic-surface regenerator, and the projection/surface controls. Never a candidate encoder |
| `evaluation-projection-schema.json` | **packet 4** — the versioned schema both candidates must later export into. The single machine-readable vocabulary source |
| `open-surface-manifest.json` | **packet 4** — the durable pin of the 782/307/364 semantic-occurrence surface: full digests plus the generation law. No oracle_id, no member list, no card text |
| `aq4_population.py` | the machinery: universe, per-card structural facts, cohort construction, the sampler, and the seven negative controls |
| `sampling.json` | **the commitment** — cohort-4 seed, the per-stratum rule, the ordering law, the K constants. Changing a value here changes the pre-registered population |
| `cohorts/cohort-N.json` | the OPEN cohort lists — `oracle_id` only (§7) |
| `population-manifest.json` | counts, hashes, stratum summary, both overlap matrices, trap-coverage map, measured-empty classes |
| `holdout-seed-commitment.json` | **packet 3A, not packet 2** — the cohort-5 seed precommitment (§22 steps 1–2). Hash-only: one PRIMARY and one RESERVE SHA-256, the canonical seed representation, and the reserve/redraw law. **No seed plaintext, here or anywhere in this repository** |

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

**Custody note, added by packet 3A.** The two sentences above are packet 2's
statement about packet 2, and they stay true of it. `holdout-seed-commitment.json`
now records §22 steps 1–2: **the SHA-256 of the primary seed and of the single
reserve seed, and nothing else.** The plaintext seeds are held externally by the
Captain and are not in this repository — no session that wrote or verified that
file has ever held them. **A hash of a seed is not a seed**, so cohort 5 stays
UNGENERATED and UNREVEALED and the sentences above still describe the machinery
here. `sampling.json` is deliberately unchanged; it says the cohort-5 seed is
not there, and it still is not.

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
| `c6.add-mana` | the CR 106.4 add-mana template, **both printed forms** (symbol and noun) | EXTRACT-2 |
| `c6.ramp-nonland-mana` | CR 106.4 add-mana, **both printed forms**, on a card with no Land type | EXTRACT-2 + CR 305.2 + EXTRACT-0 |
| `c6.ramp-land-to-battlefield` | `put … onto the battlefield` and a CR 205 `‹land type› card` in one sentence | EXTRACT-4 + ratified CR 205 parse |
| `c6.ramp-predefined-mana-token` | creates a CR 111.10 token whose CR-printed ability is itself CR 106.4 add-mana | EXTRACT-2, two CR rules meeting |

### 6a. RAMP — the gap this packet's first pass recorded, now closed

The first pass shipped `c6.add-mana` in ramp's place and **recorded the gap
rather than hiding it**: closing it needed a ruling packet 2 did not have.
Captain has since supplied exactly two, and two is enough:

- **ramp is a BENCHMARK family** — never production vocabulary. Nothing here
  mints a term, emits a token or touches the codebook.
- **an ordinary basic land is not ramp by its mana ability alone.**

**The rate argument, stated as a rule and not a taste.** CR 305.2: *"A player
can normally play one land during their turn; however, continuous effects may
increase this number."* Mana from a **nonland** source is mana that arrives
without spending the one thing the turn rations — which is both why the arm is
acceleration and why Captain's ruling is satisfied by the **type-line cut**.

**The cut is the type line, NOT the reminder strip, and RC3 exists because the
plausible story is the false one.** Ten of the twelve basic lands print their
mana ability as CR 207.2a reminder text, so `strip_reminder` appears to handle
them. It does not handle **Wastes**: it has no basic land *type*, so CR 305.6
makes nothing intrinsic and its `{T}: Add {C}.` is real printed text. Rigged,
the strip-only story lets **1,038** lands into the arm.

**`c6.add-mana` HAS NOW BEEN WIDENED — the finding is closed, 2026-08-16.**
CR 106.4 supplies the verb verbatim — *"instructs a player to **add mana**"* —
and the corpus prints the object two ways: a symbol (`Add {G}`) or the noun
(`Add one mana of any color`). The first pass matched only the symbol, so it
missed **471 cards including Birds of Paradise and Chromatic Lantern** — the
archetypal mana accelerants. The previous session measured that, recorded it as
`RAMP.ADD_MANA_SYMBOL_ONLY`, and deliberately did **not** close it, because
moving a pre-registered population is a ruling and not a fix.

**Captain ruled `CORRECT_BEFORE_PACKET3`**: the symbol-only test is an
objective **pre-holdout detector defect**, not a design choice. So:

| | before | after |
|---|---|---|
| `c6.add-mana` qualifying population | **1,718** | **2,189** |
| open half (published) | 859 | 1,095 |
| reserved for holdout draw | 859 | 1,094 |

**The correction is purely ADDITIVE and that is asserted, not assumed.** The
old population is a proven **subset** of the new one: **+471, −0**. RC7 checks
the subset relation directly rather than the totals, because a change that
added 471 and dropped 471 reads identically on a count — the recorded "a count
cannot see a substitution".

**Cohort 6 now carries ONE mana test.** `population-manifest.json` →
`ramp_family.add_mana_template_correction` records the ruling, the CR basis and
both populations. Correcting now is safe and was timed deliberately: **no
holdout has been drawn, no cohort-5 seed chosen, and no answer key exists**, so
the correction cannot have been fitted to a known key. Cohort 4 is untouched
and proven byte-identical by its selection hash.

**What moved, and nothing else did.** Only `c6.add-mana` changed: the other six
cohort-6 classes are byte-identical, and cohorts 1, 2, 3, 7 and 8 are
byte-identical files. The cohort-6 overlap rows in the manifest moved in *both*
directions (`1x6` 646→644, `2x6` 1,501→1,560) — which is the open/reserved
**re-slice**, not displacement: the open half is every other card of a keyed
ordering, so a larger pool re-slices membership both ways. Verified by
reverting only the `add_mana` predicate and reproducing every baseline overlap
number exactly.

**Search is not the arm; the zone change is.** A search-gated cut loses Settle
the Wilds (which *seeks*) and every "put a land card from your hand onto the
battlefield" — 136 of the 420 members print no search or seek at all, and all
136 were read individually. What they share is the CR zone-change instruction
with a CR 205-anchored land **card** as its object; requiring the head noun
`card` is what separates the object being moved from a land already on the
battlefield (`Sacrifice a land:`).

**No arm is a list of card names (RC4).** The land vocabulary is CR 205.2a's
`land` plus the 18 CR 205.3 subtypes only a land carries, read from the
ratified lattice parse; the coordination bridge admits CR 205.2a card types and
CR 205.4a **supertypes** (`land and/or **legendary** permanent cards` — RC1
turned red until the supertype arm existed); the token set is CR 111.10's
closed list filtered by CR 106.4, which returns four, and the fourth is one
this session did not know to look for.

**What is deliberately NOT included** lives in
`population-manifest.json` → `ramp_family.components`, every entry carrying one
of four dispositions and its measured size. Two are worth reading here:
`additional_land_play` is **EXCLUDED_OBJECTIVELY** as of Captain's 2026-08-16
ruling — see §6b, which is where its preserved identity is described;
`multi_mana_lands` is **OUTSIDE_CURRENT_DETERMINISTIC_COVERAGE**, and the
measurement that looked like it was not is why. Counting mana symbols in the
add clause returns 388 lands — **310 of those print `Add {R} or {G}`, which is
one mana with a choice of color, not two.** Only 73 print CR 107.4's adjacent
conjunctive form, and even those need the activation cost subtracted before
"accelerates" is true.

### 6b. ADDITIONAL LAND PLAY — excluded from ramp, preserved as itself

Captain ruled on this 2026-08-16, and the ruling has three parts that pull in
different directions, so all three are implemented separately:

1. **EXCLUDE from ramp membership.** An additional land play grants
   *permission*; ramp is *arrival*. A Burgeoning with no land in hand ramps
   nobody. The 34 cards contribute **zero** members to every ramp class and to
   the ramp union count.
2. **PRESERVE the mechanic separately.** It keeps its own objectively derived
   population (CR 305.2's own words, `_ADDITIONAL_LAND`) and its own row in
   `ramp_family.components`. Excluding it from ramp is not deleting it.
3. **Its relationship to broader outcome similarity is recorded**, because an
   additional land play *can* contribute to a similar gameplay result. A future
   broad outcome/discovery parent should be able to retrieve these cards
   alongside ramp; a strict ramp-membership query must not.

**Where part 3 lives, and why there.** The benchmark has **no existing
representation for a cross-family outcome relation** — a class carries
membership and nothing else. Rather than invent one, the relation is recorded
as **benchmark metadata** on the register row it belongs to:
`ramp_family.components[additional_land_play].benchmark_outcome_relation`,
carrying `relation: TANGENTIAL_OUTCOME_SIMILARITY`, `to: c6.ramp`, and an
explicit `scope: BENCHMARK_ONLY`. **It is not a production semantic parent, not
a canonical axis, not vocabulary, and no cohort membership is computed from
it.** Minting a parent to hold this note would be exactly the architecture this
packet is forbidden to decide.

**The exclusion is a guard, not a sentence in a document.**
`_assert_additional_land_play_outside_ramp` halts on every build if any
permission card reaches the ramp family, naming the ids and the arm that
admitted them. It exists because the failure it guards is silent: a later
widening of an arm's regex could pull permission into ramp while the register
still read `EXCLUDED_OBJECTIVELY` — a register that lies. Measured today the
two sets are **wholly disjoint** (34 vs 1,944, zero intersection), so the
assertion is exact rather than a tolerance. **RC8 rigs it red** by handing the
guard a union that has swallowed the 34, which is what separates a guard from a
reporter that detects and exits 0.

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
| RC1 | classic land ramp is included | printed land-ramp templates captured, self-placement and non-land objects refused; a SEARCH-gated cut turns it red |
| RC2 | nonland mana acceleration is included | both CR 106.4 printed forms captured; the symbol-only template loses 3 of the fixture's true positives |
| RC3 | ordinary basic lands are excluded | 0 lands reach the mana arm; dropping the type-line cut lets **1,038** in, so the reminder strip was never the guard |
| RC4 | no named-card hand-list | vocabulary re-derived from the CR and equal to what the module loaded; an injected card name is detected |
| RC5 | deterministic open/reserved split | rebuild byte-identical, the family split partitions its union, an unkeyed split moves 950 assignments |
| RC6 | holdout non-exposure | 972 reserved ramp cards reach 0 `c6.ramp` classes and appear in no split record |
| RC7 | `c6.add-mana` carries **both** CR 106.4 printed forms, and the correction is additive | the symbol-only predicate loses 3 of the fixture's true positives, including both worded accelerant shapes; the class must also be **−0** against the old population, checked as a subset and not as a total |
| RC8 | additional-land-play stays out of ramp, **and keeps its own identity** | handing the guard a union that has swallowed the 34 must HALT — a guard that merely reported would pass the disjointness half and fail this |

**All six were rigged red against the code path** (drill:
`_LAND_CARD` without its head noun · the symbol-only template · the nonland cut
removed · a card name injected into the vocabulary · unkeyed ordering ·
the halves swapped). **RC6's first rig was mis-aimed** and is the fourth
recorded instance of that: "make everything open" halted in `build_cohorts` on
the partition guard *before RC6 ran*, which proved the partition guard and said
nothing about RC6. Swapping the halves keeps the partition valid and reaches
the control. RC1 also earned its keep before shipping — it was **red** until
CR 205.4a supertypes entered the coordination bridge.

**Two were mis-aimed first, and both misfires are instructive.** NC-P2-4 began
as a grep of this file for a quoted `docs/` path and found **two** — its own
regex literal and its own message; a control that matches itself is the
overlapping-classes probe defect aimed at a negative control. NC-P2-5 began by
asserting that no drawn `oracle_id` appears anywhere in the manifest, which
fails for a reason that is not a leak: an open cohort draws from the same
universe, so some published members are independently also cohort-4 draws.
Twelve of 795, and the control now asserts exactly that identity.

---

## 8a. CROSS-CARD PAIRING — frozen, packet 3b

§20's B1–B4, C1, DISCOVERY-1 and E1 are **cross-card** questions phrased over
two cards, and the cohorts are flat id lists that bind no card to a counterpart.
`aq4_pairing.py` freezes the Captain-ratified protocol that instantiates them.

| tranche | rule | pairs | instantiates |
|---|---|---|---|
| `PAIR_K_CHAIN` | keyed order within each published class, adjacent | 138 | control (semantics-free) |
| `S0` | same delivery token **and** action family | 105 | B1 |
| `S1` | same delivery token, action family **differs** | 127 | B2, B3, C1 |
| `S2` | same action family, delivery token **differs** | 122 | B4, DISCOVERY-1 |

**486 unique unordered pairs covering 272/272 published open exemplars**, with
no cap, top-N or threshold anywhere. The S tranches are mutually disjoint and
`PAIR_K_CHAIN` shares only **6** pairs with them, so it stays a near-independent
control rather than a subset — a verdict holding on K *and* S is not a
stratification artifact.

**Unordered storage.** C1 is directional, but both directions derive from one
pair by recording a per-direction verdict on the *answer*; storing directed
pairs would double the count for zero information.

**The singleton is why S exists.** `c1.active-volcano-named-case` has one
member and is unpairable within its class — the chain leaves it uncovered and a
ring would emit a *self-pair*. A cross-class S tranche rescues it. That is the
concrete argument for the stratified tranches, not an aesthetic one.

**The keying salt is load-bearing and must not be tidied.** Greedy contrast
matching takes the first eligible partner in keyed order, so a different salt
gives a different, equally valid matching. Measured while freezing: normalizing
the null key from `None` to `""` moved S1 127 → 126 and the K∩S overlap 6 → 4.

**Reserved cohort-6 identities are never materialized** — not filtered out,
*never computed*. `aq4_pairing` reads only the committed `cohort-*.json` files
and never calls `build_cohorts` or `family_open_reserved`.

**Blind extensibility is pinned, not assumed.** Both S coordinates come from
frozen code, so a revealed holdout strata mechanically — but only if
`corpus_ref`, the CR edition and the parsed §2 DELIVERY vocabulary are
unchanged. All three are recorded in `pairs-open.json`. A CR refresh moved
keyword names 193 → 194 last time; an unpinned rule is not reproducible at
packet 9.

Controls `PC1`–`PC6` (`--selftest`), each with a demonstrated rigged-red path.
**PC4's rig is worth reading**: its first version capped at 4 and passed
*vacuously*, because published classes hold 1/5/6/8 members so `floor(n/2)`
never exceeds 4 and the cap removed nothing. A rig that cannot bite is
indistinguishable from a rig that found nothing.

---

## 8b. THE EVALUATION PROJECTION — frozen, packet 4

Contract §23a and supersession-register entries #27–#30. **Benchmark evaluation
law only**: no production architecture is ratified, no canonical ownership is
decided, no production vocabulary is minted, and no candidate encoder exists.

```
python3 experiments/aq4_benchmark/aq4_projection.py --census
python3 experiments/aq4_benchmark/aq4_projection.py --selftest
python3 experiments/aq4_benchmark/aq4_projection.py --validate-surface
```

### The semantic-occurrence surface is a CHAIN, not a view

The surface must **not** be called "reminder-stripped". The strip is one pass of
six, and naming the surface after one pass is what let the recorded counts
depend on a choice no document stated. The chain, by implementation name and in
order, is pinned in `open-surface-manifest.json`:

| # | implementation | role | CR |
|--:|---|---|---|
| 1 | `tier_engine.get_raw_faces` | all-faces raw oracle text | — |
| 2 | `foundry_common.canonicalize_self_reference` | optional **normalized detector view** — never evidence | 201.5c |
| 3 | `foundry_locality.units` | paragraph split + locality reconciliation; halts on a reflow | 113.2c |
| 4 | `foundry_shape_extractor.strip_reminder` | reminder strip + its separator repair | 207.2a |
| 5 | `foundry_shape_extractor.quoted_spans` | created-ability spans blanked | 113.2c |
| 6 | `foundry_shape_extractor.sentence_spans` | **owns the clause ordinal** | 113.2c |

**Reminder text** stays in the raw evidence view and stays trace-visible, but it
mints no semantic occurrence and is **never independently claim-admissible** — a
fact supported only from inside a reminder parenthetical HALTS. The **rejected**
unstripped surface is recorded with its own digests rather than quoted:
**872 / 360 / 417**.

**The raw-vs-CARDNAME-canonical question is closed as VIEW-INVARIANT**, measured
rather than argued: 782 / 307 / 364 on both views, identical occurrence
addresses, identical reached sets, 0 head-value deltas on either detector path.
**The deferred-P3 exposure is preserved, not closed** — 57 occurrences differ
textually and 32 of them across 22 cards are unreached by P1+P2. Re-audit the
text view before any future P3 adoption; P3 is not implemented and no
proper-name heuristic is adopted.

### COST is a structural marker, and it is positional

A COST region is `role: COST` plus a deterministic evidence span, owned by one
existing semantic occurrence, derived from CR-grounded boundaries: CR 113.3b /
602.1a (everything before the colon), CR 606.2 (loyalty), CR 702.6b (a keyword's
em-dash body is the keyword's own cost). Every guard is the ratified helper —
`fx.in_created_ability`, `fx.in_card_name`, `fx.LOYALTY_COST`, the CR 702
keyword-name set — never a re-implementation.

**Positional, not verb-based**, which is the whole safety property:

| printed text | COST region? |
|---|---|
| `{2}, {T}: Draw a card.` | yes — CR 113.3b/602.1a |
| `+1: ~ deals 2 damage to any target.` | yes — CR 606.2 |
| `Equip—Sacrifice a creature.` | yes — CR 702.6b |
| `Counter target spell unless that player pays {2}.` | **no** — discusses payment |
| `You may sacrifice a creature. If you do, …` | **no** — discusses sacrifice |
| `Equipped creature has "{T}: Draw a card."` | **no** — colon inside a created ability |

There is **no positive EFFECT token in v1** and no unknown-role value: material
not proven to occupy a structural cost position stays unmarked. Cost carries no
dimension, no atoms and no absence claim, so it cannot reach the ABSENT-PROVEN
machinery at all. **Uncontracted cost content stays residue, and residue is not
free** — where it differs between two units and v1 cannot prove equality, it
blocks a strict PROVEN equality rather than being ignored.

Measured over the frozen surface before the schema was written: **113** COST
regions (84 / 27 / 2 by arm), **0** crossing a clause boundary, **0**
paragraph- or face-crossing, **0** ambiguous, max span 58 characters. So a COST
marker is a sub-clause region owned by one occurrence and **no fifth identity
coordinate is required**.

The bare keyword-parameter form ("Equip {3}") is **out of v1 scope and recorded
as such** — deriving it needs keyword-parameter parsing this packet is forbidden
to build.

### Dispositions

Five, no sixth. `HUMAN-RESOLVED` is **key/adjudication-side only** and carries
its semantic payload transparently, with the adjudication method as artifact
metadata rather than as a disposition value. `ABSENT-PROVEN` is
**claimant-side only**. Key absence is `HUMAN-RESOLVED(absent)` where a
candidate would claim `ABSENT-PROVEN`, and a candidate earns that only under the
§18 obligations — the key never discharges them on its behalf.

A per-row party field was proposed and is **rejected** (written in quotes, never
in backticks, because a rejected term in backticks is ingested as ratified
vocabulary). Artifact identity already says whose rows these are.

### Controls

`--selftest`, 44 assertions, every rig demonstrated red: native-vocabulary and
candidate-branch rejection, participant-kind rejection, per-row-party rejection,
key-only and claimant-only disposition sides, method-not-a-disposition,
unknown-is-not-absent, action-head-not-a-dimension, multi-action order
preservation, the six COST cases above, cost-not-a-dimension, cost-no-absence,
same-span-same-role, trace required / trace corrupted / normalization-as-evidence
/ reminder-only support, derived verdicts and E1 prose refused, canonical
ordering determinism, and the surface digests regenerating from live machinery
with two independent rigs.

Deliberately **not** wired into Gate 2 or CI.

## 8c. THE SHARED COMPARISON ALGEBRA — frozen, packet 7

Contract §17a and supersession-register entry #31. **Benchmark evaluation law
only**: it implements §17 and register #17 as they already stand, and mints no
operator, verdict, proof kind, dimension or relation kind.

```
python3 experiments/aq4_benchmark/aq4_compare.py --census
python3 experiments/aq4_benchmark/aq4_compare.py --selftest
python3 experiments/aq4_benchmark/aq4_compare.py --validate-pins
```

| file | role |
|---|---|
| `comparison-algebra.json` | the frozen law — operation table, result domain, proof-kind vocabulary, per-operation obligations, UNKNOWN propagation and reason classes, the derived-question audit, and the dependency pins. **No pair answer, no member list, no candidate data** |
| `aq4_compare.py` | the shared comparator, its proof records and its controls. Shared evaluation machinery, **never a candidate** |

### Universal versus existential — the one law the table hangs on

> **A universal claim is contract-provable. An existential claim needs a corpus
> witness.**

Entailment, equality and disjointness are universal, so they are proved from
the §14 contracts, the §13 atom semantics and the ratified subtype→type
hierarchy (`CR_CONTRACT`). Non-entailment, non-equality and OVERLAP assert that
some object *exists*, so only a named printed card proves them
(`CORPUS_WITNESS`). That is register #17 generalized past overlap — and it is
why *"I could not prove equality"* is `UNKNOWN` and never `PROVEN_NOT`.

Four operations, and `compare()` refuses anything the frozen file does not
register: `OP_ENTAILS` (directional), `OP_EQUALITY`,
`OP_ELIGIBILITY_EQUALITY`, `OP_INTERSECTION`. **OVERLAP and DISJOINT are two
readers of ONE proposition**, so they cannot disagree and nothing can appear
between them.

### Blockers block; they never disprove

| present | consequence | never |
|---|---|---|
| a structural COST region on either side | strict equality cannot be PROVEN | PROVEN_NOT from differing cost bytes |
| a differing or missing action head | strict equality cannot be PROVEN | a missing head read as an equal action |
| a projected relation edge | strict equality cannot be PROVEN | a claim that no relation exists |
| a dimension actionable on one side, missing on the other | UNKNOWN, reason `MISSING_FACT` | any absence claim |

The cost case is demonstrated rather than asserted: a synthetic pair with
identical constraint facts and identical heads, one side carrying a cost
region, is `PROVEN` if the region is ignored and `UNKNOWN` under the real
algebra. The control prints both.

### What is derivable, and what is honestly not

`B1` · `B2` · `B4` · `C1` · `C2` · `DISCOVERY-1` · `E1` · `HONESTY-1` derive
mechanically. Two do not, and **neither gap was filled from intuition**:

- **`B3` is PARTIAL.** Its eligibility arm derives in full; its
  action-equivalence arm returns `UNKNOWN` with reason
  `NO_CONTRACTED_COMPARISON_LAW`, because §17's closed table authorizes no
  action-head comparison and a head is expressly not a §14 dimension. Head
  identity is reported as a **structural** fact — evidence for a future ruling,
  never a semantic claim.
- **`C3` is NOT derivable.** §17's ChoiceGroup derivation reads the *owning
  header's* modality; the frozen projection exports the occurrence address and
  no header modality. Reported, not fixed — proposing a projection field is
  outside this packet.
- **`HONESTY-2`** is a scoring-time property of a claiming candidate, and no
  candidate exists. The algebra implements only its consequence: an
  `ABSENT_PROVEN` row whose claimant obligations are not represented as
  satisfied degrades to `UNKNOWN`, reason `ABSENCE_NOT_EARNED`.

`C1` is directional over the **frozen unordered pair** — the direction is an
argument at answer time and no directed pair is ever stored. An empty blocker
list means *"no blocking fact is derivable under v1 law"*, **not** that the
replacement holds.

`E1`'s domain is the **354** unique unordered pairs of the semantic tranches,
one trace per pair, never multiplied by question count and never over
`PAIR_K_CHAIN`. It emits a validated §19 trace and no prose.

### Two declared readings, flagged rather than smuggled

The projection schema fixes an atom's `op` but not the payload shape of a
`CARD` or `INTERVAL` value, so the comparator declares one. And §20's `B4` says
"destination / timing / quantity" while §14's rows are named `zone`,
`timing_duration`, `quantity` and `numeric`, so the mapping is recorded as a
reading. **Neither is ratified law, neither is load-bearing, and both sit
beside the full per-dimension verdict table**, which does not depend on them.

### Controls

`--selftest`, 67 assertions, every rig demonstrated red: unregistered-operator
refusal · inability-to-prove staying UNKNOWN with its closed-world
counterfactual printed · a distinguishing witness being the *only* route to
PROVEN_NOT · missing-is-not-absent · residue and cost blocking a proof that
ignoring them would grant · action-head blocking · overlap without a witness ·
witness inadmissibility and non-satisfaction · disjointness needing a
contradiction · the forbidden controller complement beside the zone complement
that *is* taken · the context guard · wrapper transparency with the
adjudication metadata surviving into the trace · claimant-side absence
obligations · derived verdicts refused by the projection · native identifiers
refused in a proof record · proof-trace and reason-class discipline · symmetry
as **byte-identity** under operand reversal · explicit direction · determinism
×2.

Deliberately **not** wired into Gate 2 or CI.

**No verdict over any real card is produced here.** There is no answer key, no
candidate export and no scoring. Every fixture is synthetic and every
`oracle_id` in this module is a zero-padded placeholder.

## 9. WHAT THIS PACKET DELIBERATELY DID NOT DECIDE

- **Whether `this way` is a fourth relation kind.** It is in cohort 2 because
  packet 1 measured it as the largest unresolved reference form (1,088
  references). Nothing here assigns it a kind.
- ~~**Whether `c6.add-mana` should be widened to CR 106.4's worded form.**~~
  **RULED AND DONE, 2026-08-16** — Captain ruled it an objective pre-holdout
  detector defect (`CORRECT_BEFORE_PACKET3`). 1,718 → 2,189, additive, §6a.
- **Whether a card that ramps an OPPONENT is ramp.** 41 of
  `c6.ramp-land-to-battlefield`'s members name a non-`you` recipient and no
  your-zone (Show and Tell, Hypergenesis, the Ghost Quarter cycle). The arm is
  the zone change, which they genuinely print; controller scoping is a separate
  dimension and cohort 8 already carries `c8.residue-controller` for it.
- ~~**Whether permission-to-play-a-land joins the family**~~ **RULED,
  2026-08-16** — EXCLUDED from ramp, mechanic preserved separately, and its
  tangential outcome relation recorded as benchmark-only metadata (§6b, 34
  cards). What remains undecided is a *different* question, and it belongs to
  the architecture and not to this packet: **what a broad outcome/discovery
  parent actually is.** Nothing here proposes one.
- **Cohort 4's size beyond the zero-free-parameter rule** (§4). Changing
  `per_stratum` in `sampling.json` and regenerating is the whole cost, so this
  stays cheap to rule on.
- **Any semantic answer, for any card, in any cohort.** Inclusion reasons are
  structural. Answer keys are packet 3 and later, under the §22 firewall.
