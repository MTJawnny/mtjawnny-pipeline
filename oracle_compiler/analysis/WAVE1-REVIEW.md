# Oracle Compiler — Wave-1 Review (C01–C02 against V1)

**Task:** W1.ORACLE-COMPILER-WAVE1-REVIEW (Issue #1 comment 5877803036).
**Base:** `50c97856f387a5dfd9b900049282df23b8417051` (accepted head, K 5877803287).
This file is analysis, not a selector: work runs only when the latest `K` on
Issue #1 selects its `T`.
**Status:** Worker proposal; becomes the reviewed Wave-1 result only on Codex
cross-review acceptance (Captain decision E).

## 1. What was reviewed

| package | task | accepted result | verdict |
|---|---|---|---|
| C01 AQ4 Packet-0 preflight | 5876922694 | 5877076654 | ACCEPT 5877105479 |
| C02 AQ4 §27 probes P1–P4 | 5877105724 | 5877172814 | ACCEPT 5877200277 |

Read with them: `oracle_compiler/V1.md`, `PLAN.md`, `PROGRAM.md`, `OWNERSHIP.md`,
`INTERFACES.md`; the M02 fixture contract and M03 crosswalk at commit
`1efd2e00284964061f4a8e69ac35d22e7c6adde9` (branch compiler/manager-m02-m03-2026-09-26,
not merged into the program branch); the AQ4 implementation contract §§11, 18,
25–27a and register #27.

Input identities, re-measured for this review at the accepted head and equal to
C02's record:

| input | identity |
|---|---|
| probe code | `benchmarks/aq4/experiments/foundry_aq4_probes.py` sha256 `eec9a4e2aea4c27d74dfffc6d4b82fdcd6f7292bd777aadc2c8625215c7c48f6` (= FREEZE-MANIFEST) |
| corpus | operator `data/raw/oracle-cards.jsonl.gz` sha256 `2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872` (32,557 cards) |
| CR | `config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md` sha256 `ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b` |
| C02 output | `--all --json` sha256 `74e3559d785dc3ac47d14823ac1fec96dd446ae446d82a3ee45b03ef3f818dfd` (41,541 bytes, ×2 byte-identical) |

No file under `benchmarks/`, `experiments/`, `tests/guards/`, `config/` or `src/`
differs between C02's base `3798ccf` and the accepted head `50c9785`.

## 2. V1 §14 P0 obligations — discharged or not

| P0 item | status after C01–C02 | evidence / gap |
|---|---|---|
| P0.0 AQ4 governance boundary | **DISCHARGED for measurement** | C01: freeze intact, Gate 2 green, no law conflict; C02 ran under Captain authorization 5764505048 with frozen bytes. Nothing ratified AQ4 production; it stays PAUSED. |
| P0.1 existing-substrate ownership audit | **DISCHARGED before this program** (M01, result 5844518936; M03 crosswalk) | Not re-opened. Five rows are GENUINELY_MISSING or CANDIDATE_NOT_RATIFIED and stay so: replacement lineage, decision authority, ability borrowing (GENUINELY_MISSING); operation structure (H-REGION is a falsification target only) and keyword consequences (a future registry interface may be defined; unratified consequence law may not be frozen or populated) (CANDIDATE_NOT_RATIFIED). |
| P0.2 consume §27 probes | **DISCHARGED** | All four probes measured once, deterministically, under the frozen contract. Readings are feasibility/pricing evidence only (C02 corrected readings). |
| P0.3 H-REGION falsification | **NOT STARTED — two preconditions open** (§4) | Needs the fixture selection freeze and a re-derivable population. |
| P0.4 reference resolution | NOT STARTED | Pressure set measured (§3, P4). |
| P0.5 coverage ledger | NOT STARTED | P1 residue evidence is its input. |
| P0.6 Round-2 seam audits | NOT PLACED until this review | Placed in `PROGRAM.md` (decision H4). |
| P0.7 verbalizer | NOT STARTED | Needs stable experimental output. |
| P0.8 parser bake-off | NOT STARTED | Last; parser selection is Captain's. |

## 3. What C03 and C04 inherit

**C03 (H-REGION, V1 P0.3) — population.** P2 found 66/2,110 clause occurrences
with more than one candidate effect head on the frozen legacy path: 53
"exile + return", 13 other combinations (exile family 60, destroy 6, bounce 0).
Candidate heads establish neither a delayed return nor same-object identity (C02
correction). The COST-region precedent (register #27) is the positive control:
113 derivable COST regions on the frozen 782-occurrence open surface, 0 crossing
any clause, paragraph or face boundary, 0 ambiguous.

**C04 (reference resolution, V1 P0.4) — pressure set.** P4: 32,603 candidate
references on 16,245 cards; 1,548 kind-unclear (4.75%), dominated by "this way"
(1,088), "the same" (225) and "the copy" (208); 3,774 delayed-marked references;
741 CR 607 linkage candidates; 607 references excluded inside created abilities.
These are candidate classifications, not established edges.

**C05 (coverage ledger, V1 P0.5) — input.** P1: 1,304/2,110 (61.8%) zero residue
primary, 960/2,110 (45.5%) strict; residue dominated by controller relations
(910) and numeric comparison (500). Feasibility evidence only; §18 obligations
remain the claiming candidate's.

## 4. Findings

**F1 — C03's population is narrow, and V1's frontier is wider.** §27 defines
P2's population as "all classified clause occurrences"; the frozen probe reads
that as `foundry_qualifier_census.population()`, three object-lattice actions
(destroy, exile, bounce). V1 §7's frontier is multiple operations within any
paragraph/clause surface. So an H-REGION that survives C03 has survived only a
flicker-dominated slice: 53 of 66 clauses are one form. **Consequence:** C03's
report must state that its population is P2's census slice, and a surviving
H-REGION is "not killed on the P2 population", never "confirmed". The COST
precedent and the fixture family (F2) are the only other evidence C03 may use.
Widening the population is a re-measurement, which V1 P0.2 forbids duplicating;
it is not proposed here.

**F2 — the fixture selection freeze has not happened, and it is a C03
precondition.** M02's `selection_freeze` requires, "after C01 PASS … and before
any C03 candidate result exists", every null fixture member to be filled "only
from already-authorized pre-existing production fixtures or the existing AQ4
probe populations named by the role", by a recorded deterministic rule, "not because
H-REGION succeeds or fails on them". Eight of ten roles have null members (only
the V1-named replacement-lineage set and Knight of Autumn are filled). Also,
`FIXTURES.json` and the M03 crosswalk live only on the M02/M03 branch; the
program branch has neither. **Proposed next task (Manager surface):** bring both
files onto the program branch byte-identical to `1efd2e0`, then fill the eight
null members under M02's own source rule: the probe populations each role names
(re-derived with the frozen functions, since C02's accepted output holds
aggregates and examples, not complete populations) or authorized pre-existing
production fixtures, with no C03 code or result in existence. C03 must not start before that task is
accepted.

**F3 — the C02 artifact holds only examples, so C03 must re-derive its
population.** The accepted JSON lists 25 of the 66 multi-head clauses. C03
therefore re-derives the population with the frozen functions (census
population, legacy `effect_heads`) and must reconcile to C02's accepted numbers
before using it: 66 clauses, head-count distribution {1: 2044, 2: 65, 3: 1}, 53
"exile + return", and the 25 C02 examples as a subset. Any mismatch is a STOP.
This is plumbing (the same measurement read at a finer grain), not a new probe.

**F4 — the C02 output survives only in a temporary scratch clone.** Its hashes
match the record, and the measurement is ×2 deterministic, so loss is
recoverable by re-running C02's vehicle. It is recorded, not repaired: copying
it anywhere is outside this task. C03 must pin the sha256 values above, never a
path.

**F5 — the P2 count uses the frozen legacy detector.** §27a keeps
`effect_heads` frozen for P2 and routes new ground-truth work to
`semantic_action_heads`, whose authorized classes (CR 700.2 mode bullet;
instruction prefix) move heads on bulleted and prefixed clauses. C03 is
experimental, not ground truth, so it takes P2's population as measured, and
reports separately which of its clauses the corrected path would read
differently. It must not substitute one detector for the other silently.

**F6 — V1's kill conditions need pre-committed operational tests.** V1 §5 says
H-REGION is killed "if a precommitted fixture/population demonstrates" any of
seven conditions, and AQ4 §26's rung adoption gate is consumer-question based.
Neither says how a measurement decides each condition. Without a pre-commitment,
C03 would decide what counts as a kill after seeing its own output. That is the
reason for interface/1 (§5).

**F7 — no conflict found** between C01/C02 evidence and V1, M01/M03, or AQ4 law.
C01's A3 naming hazard stands: "§27 probe P3" (multi-participant) is not "§27a
detector class P3" (deferred finite-subject), and C03/C04 texts must keep the
two apart.

## 5. Decision: propose `oracle-compiler-interface/1`

**Proposed.** Under Captain decision H3 it is ratified when this review is
accepted by cross-review, because it mints no production vocabulary or schema
and promotes no AQ4 benchmark law. It is a **measurement interface**: it pins
what C03 and C04 read and how C03's result is decided, before either exists. It
defines no record shape, no occurrence coordinate, no region identity and no
reference type; C03's outputs stay ignored experimental output under
`experiments/out/`.

The interface text is in `oracle_compiler/INTERFACES.md`. Its content, in
summary: the four input identities of §1; the C03 population rule of F3 with its
reconciliation STOP; the fixture precondition of F2; and one pre-committed test
per V1 kill condition, each evaluated per population clause and per fixture,
each reported as a count with its clause list, and each a STOP-to-Captain when
it fires on any fixture or on any clause whose consumer question needs the
distinction.

**What interface/1 does not do:** it does not ratify H-REGION, the four-coordinate
occurrence as production identity, the COST region beyond benchmark law, any
region vocabulary, or any reference model. A fired kill condition returns to the
Captain and the AQ4 reserved finer-effect path (V1 §5), never to an ad hoc
identifier.

## 6. Decision H4: placement of V1 P0.6

The three Round-2 seam audits (R2-A replacement-event lineage, R2-B decision
authority, R2-C ability borrowing/inheritance) are placed as package **A01**,
one audit per unit, **after M04 and before C04**:

- they are read-only and independent of H-REGION, so C03 does not wait for them;
- C04 must test "replacement lineage endpoints" (V1 P0.4), which R2-A audits
  first, so A01 precedes C04;
- every later package that could approach schema (C05's ledger extension,
  interface/2, the Wave-4 contract) comes after A01, which satisfies "before any
  schema expansion";
- each unit first proves whether an existing structure suffices (M03 rows:
  all three GENUINELY_MISSING, so each audit must show that classification still
  holds or name the existing structure that overturns it), and each STOPs before
  vocabulary or schema minting.

Recorded in `oracle_compiler/PROGRAM.md`.

## 7. Next packages, in order

1. **F0 fixture selection freeze** (F2), Manager surface.
2. **C03** H-REGION falsification under interface/1.
3. C03b, M04, **A01** (P0.6), C04, M05, C05, C06, M06, Wave 4, per `PROGRAM.md`.

## 8. Batched Captain items raised by this review

None new. Standing: H1 watcher install and H2 `main` workflow deploy await the
operator (Issue #1 comment 5877802778).
