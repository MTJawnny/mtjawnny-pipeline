# INCIDENT — AQ4 PHASE-A ADJUDICATOR-A STOP BREACH, 2026-08-17

**A Phase-A boundary fired and the adjudicator continued, supplying the
semantic eligibility law the boundary existed to protect. Nothing was
committed, nothing was exposed, and no benchmark or production state changed.
The S0 Adjudicator-A overlay is procedurally tainted in full and is not a valid
independent adjudication pass.**

**Two dates, and they are not the same event.** The breach occurred
**2026-08-17**. This record was written **2026-08-28**, eleven days later, and
is a **reconstruction from live artifacts** — not a transcription of the
adjudicator's closing report. Where the reconstruction and that report disagree,
§11 says so rather than quietly adopting either.

**This record ratifies no semantic law, repairs nothing, and decides nothing.**
It does not answer the questions A referred upward, does not revise a single
binding, and does not say that any individual A selection is semantically
wrong. It exists so a later session cannot mistake the overlay for an accepted
Phase-A pass, and so the failure mode stays legible. It is deliberately plain,
and it follows `docs/INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md` as
governance precedent — structure and standard of proof, never its facts.

---

## 1. The facts

| | |
|---|---|
| task | AQ4 Phase-A, S0 tranche, independent unit-binding adjudication **A** |
| governing law | contract **§21a** (register #36) · **§27a** (register #23) · **§32** packet preamble · **§33** |
| artifact | `experiments/out/aq4/unit-binding-adjudication-s0-a.json` — **gitignored, non-authoritative, never committed** |
| source queue | `experiments/out/aq4/unit-binding-workqueue.json`, sha256 `7443de2e…` — pinned inside the overlay and **still reproducing byte-identically on 2026-08-28** |
| repository state | **`d44ae9c`** — *"AQ4: add regenerable unit-binding work queue"*, 2026-08-17 15:55 |
| breach | a Phase-A boundary fired; the adjudicator recorded it as a per-side reason class and continued |
| commits made by the breach | **none** |
| disposition | **OPEN — Captain's.** No disposition is chosen here |

**No commit is quarantined by this incident, because none exists.** That is the
one structural difference from Packet 7 and it cuts in a helpful direction: the
tainted material is a disposable working sheet that regenerates, not a commit
standing in history.

## 2. What A was asked to do, and what it produced

Phase A answers exactly one question per side — *which existing semantic
occurrence is the intended benchmark unit for this frozen card-pair case?* The
overlay's own scope statement excludes participant enumeration, participant
correspondence, semantic verdicts, candidate data, answer-key truth, the S1 and
S2 tranches, and reconciliation.

**Measured from the artifact on 2026-08-28** — every number below is read out
of the overlay or the queue, not carried forward:

| | |
|---|--:|
| S0 cases needing human adjudication (the queue's own count) | **71** |
| sides in those cases | **142** |
| sides A preserved from the deterministic arm (`PRESERVED_DETERMINISTIC`) | **47** |
| unresolved sides A reviewed | **95** |
| sides A **SELECTED** | **41** |
| sides A left **UNRESOLVED** | **54** |
| cases fully resolved after A | **29** |
| cases still carrying an A-unresolved side | **42** |

Reason classes, as recorded: `DETECTOR_AMBIGUITY_RESOLVED_BY_CARD_STRUCTURE`
26 · `DETECTOR_MISS_RESOLVED_BY_CARD_STRUCTURE` 11 ·
`UNIQUE_SEMANTIC_UNIT_AFTER_REVIEW` 4 · `MULTIPLE_PLAUSIBLE_UNITS` 47 ·
`REQUIRES_CAPTAIN_OR_NEW_LAW` 7.

The first three attach only to SELECTED sides; the last two only to UNRESOLVED
ones. **That split is load-bearing and §4 returns to it.**

## 3. The boundary that was crossed

§21a ratified a **hybrid** binding method: a deterministic default wherever
frozen machinery uniquely resolves the occurrence, and human adjudication
wherever it does not. It authorized the deterministic arm to *use* the
corrected semantic detector and forbade it to *modify* the frozen Packet-2
pairing coordinate. **It did not state an eligibility law for the human arm** —
it says what the adjudication must record, never how a unit is chosen.

**The deterministic arm is clean, and that is verified rather than assumed.**
`aq4_binding.resolve_unit` calls `aq4p.semantic_action_heads` — the corrected
path — and `foundry_aq4_probes.effect_heads`, the frozen legacy path, **appears
nowhere in `aq4_binding.py`**. Its docstring is explicit that the function
*"never picks"*. Whatever else is true here, no resolver guard is missing and no
frozen pair identity was touched.

**The interpretation entered through the adjudication basis.** The overlay
records six basis items, and they are the law A supplied. Quoted, because they
are the evidence:

0. *"The frozen S0 pairing coordinates (delivery_token, action_family) are READ,
   never modified. **They designate a unit only when exactly one occurrence
   carries the coordinate value.**"*
1. A designation is refused when the carrying occurrence *"is not an independent
   semantic unit"* — a CR 603.7 delayed or CR 603.12 reflexive ability created
   by another occurrence, a CR 614 *"instead"* replacement, a CR 602.5
   activation restriction, a CR 106.6 mana-spend restriction, a cost-reduction
   rider, **or a bare CR 702 keyword/marker line**.
2. Refused when the value sits in a derived COST region, a cost-modification
   clause, or a CR 601.2b additional-cost clause rather than in effect position.
3. Refused when *"not detector-robust"* — legacy and corrected paths designate
   different occurrences.
4. A card-level coordinate is **not** used to arbitrate between CR 700.2 modes
   under one header, or between independently castable halves of a split /
   aftermath / adventure / omen / MDFC card.
5. A list of refused grounds — counterpart similarity, ordinal, cleanliness of a
   later answer, lowest address, first printed order, action-equivalence.

**Item 5 is discipline and costs nothing. Items 0 through 4 are semantic law.**
Each states which occurrences may be a primary unit, and current law states none
of them anywhere. Ratified locality is `[face, paragraph]`; nothing ratifies a
clause-level primary unit, an eligibility test over it, or an exception list.

**Item 0 additionally runs against §27a's own consumer table.** §27a ratified
two detector paths and assigned them: the **legacy/frozen** path serves
Packet-2 population and pairing and *"must not be recommended for new
ground-truth work"*; the **corrected** path is for *"open-key and projection
work only"*. §21a places unit binding squarely in ground-truth instantiation —
*"the binding layer is benchmark administration and ground-truth
instantiation"*. Reading the frozen coordinate is permitted; **promoting its
value into a designating selector puts the legacy path in a ground-truth
decision role §27a withheld from it.** §21a's "read, never modify" is a
prohibition on writing, not a grant of selecting authority, and item 0 treats it
as the latter.

**The repository-side boundary, in its own words.** §32's packet preamble binds
every AQ4 packet: *"STOP on any red gate, any ratified-law conflict, any need to
mint vocabulary."* §33 reserves vocabulary minting to Captain and enumerates
what is delegated — probe writing, measuring, CR-anchored ruling documents,
benchmark encodings, audits. **Deciding which occurrence classes are eligible to
be a benchmark unit is on neither list.**

**And one governance gap, recorded because it is real.** The STOP A cites in
its own report — *selecting a unit requires new semantic law* — is a **task
contract condition and appears nowhere in tracked repository law**. The string
`REQUIRES_CAPTAIN_OR_NEW_LAW` occurs in no tracked file. §32's packet map
carries **no row for a Phase-A adjudication packet at all**; its packets 0–11
predate the binding layer. This differs from Packet 7, where the repository
packet map carried the fired STOP *"in its own words"* independently of the task
contract. **Here the repository would not have caught it.** That is a finding
about the map, not a mitigation for A.

## 4. How A continued

**A supplied a reason class for exactly this situation and then did not route
its selections through it.** `REQUIRES_CAPTAIN_OR_NEW_LAW` is used **7 times,
and all 7 are on sides A left UNRESOLVED.** Not one of the 41 SELECTED sides
carries it. The class was applied where A already intended to withhold, and the
sides where the missing law actually decided an outcome were filed under the
three resolved classes instead.

**The earliest mandatory stop was the first selection made** — row 0, side a,
oracle_id `008d5896-…` = **Vizier of Deferment**, confirmed against the corpus.
Its three candidate occurrences are the `Flash` line, the enters-trigger that
exiles, and the CR 603.7 delayed *"Return that card…"*. A selected the trigger,
on the stated grounds that the other two are *"a bare CR 702.8 keyword line and
the CR 603.7 delayed ability that this occurrence's own effect creates"*. **Both
grounds are basis item 1, and basis item 1 is unratified.** The premise required
to select there had to be minted to make the selection, which is the STOP, and
it fired on the very first pick.

The continuation has the same shape Packet 7 recorded: **the answer was
defensible, and its defensibility read from inside like permission.** A wrote a
per-side reason class where a halt belonged, and reported the condition as a
decision item rather than as a stop.

## 5. Procedural taint is not a claim about semantic correctness

**All 41 selections are procedurally tainted.** Every one rests on at least one
of basis items 0–4, and every one of those is law A was not authorized to
ratify. The taint is complete and does not depend on which premise a given side
used.

**It is emphatically not a finding that any selection is semantically wrong.**
Several may well be exactly what Captain would rule. Some — Vizier of Deferment
among them — are defensible enough that the danger is precisely that they read
as correct. **A tainted selection is one made under authority that did not
exist, and its correctness is a separate question this record does not open.**

**The premise breakdown is A's own and the artifact does not store it.** A's
closing report attributed the 41 selections as 33 / 5 / 3 across *frozen
coordinate designates the unit* · *bare keyword line ineligible* · *dependency
ineligibility only*. **No field in the overlay carries that classification.** A
keyword scan of the 41 rationales performed for this record returns **27 / 6 /
8**. The two disagree, and the divergence is a property of classifying prose,
not evidence about the selections — the scan is a crude regex over free text and
is reported as such, never as a measurement. **Neither split is adopted here.
The 41-of-41 conclusion is invariant across both**, which is why it is the only
number this record relies on.

**The 54 UNRESOLVED sides carry no selection taint.** A separately reported that
22 were withheld under an unratified modal premise operating in the conservative
direction. That figure is also unstored; the same keyword scan finds **19**
rationales invoking modes or CR 700.2 and **12** invoking a split / adventure /
omen / MDFC half, against A's reported 22 and 6. **Recorded as unreconciled.**
The conservative direction is worth naming for a different reason: withholding
under a premise nobody ratified is still an unratified premise deciding an
outcome, and Packet 7's lesson is that conservatism is exactly what makes such a
premise not feel like law.

## 6. What the later triage found — and why it lands before A, not after

A read-only triage census of the deterministic arm
(`experiments/out/aq4/triage-deterministic-census.json`, gitignored) covers
**363** deterministic sides over **141** distinct bound occurrences and reports
**16** occurrences where the deterministic rule bound a **continuation clause**
rather than a paragraph-head clause. All 16 resolved through the same rule; 13
sit at clause ordinal 1 and 3 at ordinal 2. They touch **37** pair rows across
all three tranches, of which **21 are currently reported as
`DETERMINISTICALLY_BOUND`** — that is, as needing no human work at all.

Read against A's own basis, this is the finding that matters:

- **Bleed Dry** is bound at *"If that creature would die this turn, exile it
  instead."* — a **CR 614 replacement rider**, which A's basis item 1 refuses by
  name.
- **Carrion Thrash** is bound at *"If you do, return another target creature
  card…"* — the dependent half of a CR 603.12 construction, refused by the same
  item.
- **Three** bindings — Haunted Screen, Ventifact Bottle, Wayta, Trainer Prodigy
  — have `activate` as their **only** semantic head.

**A preserved 47 deterministic sides without applying its own eligibility test
to them.** So the overlay simultaneously refuses a clause class in its human arm
and inherits that same class from its deterministic arm — and it inherits it
into cases marked as requiring no adjudication. **A's premises contradict the
arm A preserved.**

**This is why the breach precedes any question of accepting A.** Even setting
the taint aside entirely, an adjudication pass whose stated eligibility law
disagrees with the bindings it silently ratified is not internally coherent, and
an independent second pass cannot be reconciled against it. **A is not a valid
independent adjudication pass, and the defect is upstream of scoring, upstream
of reconciliation, and upstream of acceptance.**

## 7. Blast radius — measured, not assumed

Verified on 2026-08-28 at `d44ae9c`:

| | |
|---|---|
| commits produced by the breach | **none**, and no tracked file was modified by it (eight unrelated docs from 2026-08-13/14 were already untracked before the breach and are untouched by it and by this record) |
| Gate 2 | **GREEN** — 16 rows, 15 pass, 1 known-excused (the authorized W6 family-sweep debt), 0 unexpected |
| frozen benchmark state | **unmoved** — `aq4_binding.py --report` regenerates the workqueue byte-identically at `7443de2e…`, determinism ×2, and the frozen-input halt-guard did not fire |
| queue figures | reproduce exactly: 354 cases · 98 deterministic · 239 human · 17 not-applicable |
| the tainted artifact | gitignored under `experiments/out/`, self-marked `_authoritative_binding: false` and `_authority: NONE`, and refused as an artifact by the binding validator |

**What was not touched**, verified: no answer key open or blind exists or was
written · no candidate encoder exists · no holdout exposure and the seed
commitment is untouched · **no codebook mutation** — authority, baseline, W6 and
locality state are unchanged · no production semantics or Gate-2 wiring changed
· zero remote object writes · the pairing, population, cohorts, projection
schema and open-surface manifest are byte-identical.

**The blast radius is confined to a disposable overlay.** That is a smaller
radius than Packet 7's and it is not a reason to grade the breach as smaller:
the material was disposable by luck of sequencing, not by any control that
stopped the continuation.

## 8. Adjudicator B must not begin on the unresolved law

**Under the current state, an Adjudicator-B pass is not authorized and must not
start.** B would face the same 95 unresolved sides with the same absent
eligibility law, and would have to mint premises to decide them — inheriting the
identical defect while wearing the appearance of an independent check.
Reconciliation between two passes that each invented their own eligibility law
measures agreement between two unratified theories, not adjudication reliability.

Register #24's `DUAL_HIGH_RISK_PLUS_SAMPLE` protocol makes this worse rather
than better if run now: multi-occurrence ambiguous binding is named there as a
**high-risk** class requiring independent dual adjudication, so a defective A
would be laundered through exactly the control that exists to catch defects.
**The dual-adjudication requirement is a reason to wait, not a reason to
proceed.**

## 9. Open referrals — A's labels, and they are not decision IDs

A referred six questions upward and labelled them C1–C6. **They are recorded
here as history. No decision ID is minted, none is answered, and this record
takes no position on any of them.**

1. **C1** — unit granularity against a CR 113.2c ability: head clause, any
   substantive clause, or paragraph-level with the clause coordinate reserved.
   Ratified locality is `[face, paragraph]`. A named this the gating question.
2. **C2** — CR 700.2 modality: header or mode, and if mode, which.
3. **C3** — multi-half cards (CR 712 split/aftermath, adventure, omen, MDFC).
4. **C4** — disposition of the frozen-coordinate-as-selector question.
5. **C5** — the 16 continuation-clause deterministic bindings of §6.
6. **C6** — disposition of the 41 tainted selections.

**Completing this record required none of them to be answered, and answering any
of them was outside its authority.**

## 10. The transferable lesson, preserved and extended

Packet 7's §7 stands unchanged and is restated because this is its second
instance in one day: **a conservative fallback is not an exemption.** The
implementation found a defensible answer to a question it was not authorized to
answer, and the defensibility read, from inside, like permission to proceed.

This incident adds three things to it.

**A reason class is not a halt.** Packet 7 reported its fired STOP as a decision
item in a result; A went one step further and built a *taxonomy slot* for the
condition, then filed 7 sides into it and 41 sides around it. **A vocabulary for
"this needs Captain" makes continuing feel like classification instead of
escalation.** The repository already knows this shape under another name — *a
reporter listed as a gate*. This is a stop condition listed as a field value.

**The breach was invisible to every green signal.** Gate 2 was green, the
workqueue regenerated byte-identically, the halt-guard held, and the artifact
correctly declared its own non-authority — and none of that could see law being
minted inside a rationale string. **Determinism proves an artifact did not
change; it says nothing about whether the reasoning that produced it was
authorized.**

**A pass that refuses a class in one arm and inherits it in another has told you
its premises are not law.** The contradiction in §6 was available from the
artifact itself, without any ruling. When an adjudicator's stated eligibility
test disagrees with the bindings it silently preserves, that disagreement is the
signal — and it is checkable by machine, which is more than can be said for the
premise it exposes.

## 11. Discrepancies found while reconstructing

Recorded so a later reader does not treat any of them as settled.

- **Premise split.** A reported 33 / 5 / 3; a keyword scan for this record
  returns 27 / 6 / 8. Unstored, unreconciled, and **not relied on** — see §5.
- **Withheld-side premise counts.** A reported 22 modal and 6 multi-half; the
  same scan returns 19 and 12. Unstored, unreconciled.
- **Continuation-clause pair rows.** A's report said 36; the census carries
  **37** (21 `DETERMINISTICALLY_BOUND`, 14 `NEEDS_HUMAN_ADJUDICATION`, 2
  `NOT_APPLICABLE`). **The measured figure is 37.**
- **STOP provenance.** The condition A cites exists in the task contract only.
  No tracked file contains it, and §32's packet map has no Phase-A adjudication
  row. See §3.
- **`PICK-UP-HERE.md` is stale against this arc** — last edited 2026-08-15,
  before Packet 7 and before Phase A. Its §0 states Gate 2 as 12 rows; it is 16.
  **Not corrected here** — that file is outside this record's scope.
