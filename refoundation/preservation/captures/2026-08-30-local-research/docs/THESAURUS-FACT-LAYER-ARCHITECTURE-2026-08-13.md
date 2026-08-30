# THE FACT LAYER FOR SEARCHER B — architecture report

**2026-08-13.** Written from the live repository. Zero codebook mutation, zero
API calls, no DET pass run. Gate 2 green at start and end (14 gates, 13 pass,
1 known-excused `family_sweep`, 0 unexpected).

**Shipped artifact that changes because of this work: NONE.**
`foundry_reachability.py` still reports **0 of 5** foundry artifacts reaching a
shipped card, and no `pipeline/` file was touched. This is Foundry safety
infrastructure. Saying so out loud before starting is CLAUDE.md §0.

---

## 0. THE FINDING THAT GOVERNS THE REST — THIS DECISION IS ALREADY OPEN

**Gate 3b, prior art.** The brief asks whether Foundry needs a reusable typed
fact mechanism or whether each family should invent its own guards. **That
question is already written down, already measured, and already sitting with
Captain** as `docs/ARCHITECTURE-AUDIT.md` §13:

> **AQ4. Is the axis the right primary object, or is the predicate row?**
> *Tradeoff:* the axis is ratified law, S1–S7 and the naming grammar are built
> on it, and 4,233 human assertions are filed under it. The predicate row fixes
> magnitude, deck role and level in one change instead of three… Migrating is
> the largest risk in this document.

> **AQ5. Add a `level` field, and if so, derived from `source` or assigned per
> axis?** *Tradeoff:* deriving from `source` is free and correct by provenance
> but only splits DET-owned from human-owned, 39 against 364… Assigning per
> axis gives consumers the subset they need but the rubric this audit built
> agreed with hand-scoring on roughly 16 of 30, so per-axis means 403 hand
> rulings.

The audit's §6 also already enumerates six options (A–F), including the brief's
Option D as its §6.4 (`level` field) and the brief's Option E as its §6.6
(*"the predicate table, with axes as saved queries"*).

**So this report does not re-derive that decision.** Re-running it would be the
recorded failure of a session rediscovering what the project already decided.
What follows adds the three things the audit did **not** cover — assertion
shape, effect locality, and the guard-coverage matrix — and answers the one
narrow question §20 of the brief actually leaves open.

---

## 1. PRODUCT CONTRACT

| | job | status |
|---|---|---|
| **Searcher A** | *"what cards read like this card?"* — rules-language / verbatim similarity | **built; not being rebuilt, not touched here** |
| **Searcher B** | *"what cards do the same gameplay job, in different words?"* — Grand Abolisher ↔ Defense Grid | **the current target** |
| **Budget Swapper** | same job, compatible action/object/scope/magnitude/timing, cheaper | lowest tolerance for false equivalence |
| **Deck Completion** | what function is missing + what fits this deck's mechanical texture | needs coarse role + synergy |

`ARCHITECTURE-AUDIT.md` §4 already derived these backward and measured the
result: **the tag layer exposes what a similarity tool needs and is missing the
two a Budget Swapper needs — magnitude and role — where magnitude is absent
from every one of the 403 active axes.**

---

## 2. WHAT ONE ASSERTION ACTUALLY IS (not in the prior audit)

`foundry-codebook/2`, read live. 615 axes, 403 active.

```json
{ "oracle_id": "01c729d7-…",
  "assertions": [ { "class": "human", "source_ref": "batch-2",
                    "quote": "Create a 5/4 green Snake creature token.",
                    "corpus_ref": "2026-07-04",
                    "evidence_status": "quoted" } ] }
```

A membership is a **stack of support assertions**, each carrying provenance
class, source reference, corpus reference and a verbatim evidence quote. Live
provenance: **4,233 `human`, 3,697 `rule-derived`, 0 `llm`.**

**This is a genuinely good substrate** and it is the strongest argument against
the brief's Option E. It already has: per-fact provenance, per-fact evidence,
corpus versioning, multiple independent supports for one fact, and a ratified
mutation path (`foundry_membership_move.py`). A new fact artifact would have to
re-earn all five.

**What it lacks is one field, and it is the same field AQ5 names:** the
assertion records *what* is claimed and *who* claimed it, and **nowhere records
what KIND of claim it is** — closed rules fact, effect tuple, deck role, or
editorial judgment.

---

## 3. EFFECT LOCALITY — the verdict, with the live example

**Question: can facts belonging to one ability be told apart?**
**Answer: yes in practice, no by construction. The quote is the only
coordinate, and there is no `face` / `ability` / `mode` field.**

The live worked case — Nicol Bolas, Planeswalker, the card on the most axes:

| axis | evidence quote |
|---|---|
| `rule:burst-draw` | `+2: Draw two cards.` |
| `rule:direct-damage-any-target` | `−3: Nicol Bolas deals 10 damage to target creature or planeswalker.` |
| `rule:reanimate-from-graveyard` | `−4: Put target creature or planeswalker card from a graveyard…` |
| `rule:exile-each-graveyard` | `−12: Exile all but the bottom card of target player's library.` |
| `rule:activation-restricted-to-sorcery-speed` | `Activate only as a sorcery` |

**The first four are cleanly local** — each quote carries its own loyalty cost,
so a consumer can tell `+2` from `−3` and will never form the false
cross-product *"draws two cards AND deals 10 damage"* as one effect.

**The fifth is the failure in miniature.** `Activate only as a sorcery` binds to
no ability. A restriction with no effect-identity cannot be attached to the
effect it restricts, which is exactly what Budget Swapper needs
(`action ↔ object ↔ scope ↔ magnitude ↔ timing ↔ condition`).

So: **locality is *recoverable* by string-matching a quote back to an ability
line, and it is not *represented*.** The repository already depends on that
recovery and already guards it — `foundry_ground_truth.py` treats an
**unanchored seed** (quote no longer matching any ability line) as fatal. That
is an existing, tested mechanism for exactly this, which means adding real
coordinates later is an extension, not a rewrite.

**A flat bag is insufficient, and the modal case proves it:** Dawnbringer
Cleric prints `• Dispel Magic — Destroy target enchantment.` and
`• Gentle Repose — Exile target…` as separate CR 700.2 modes. Flattened, the
card reads as doing both; it does one.

---

## 4. GUARD COVERAGE MATRIX (honest, measured this session)

`FC` = fresh clone. ✓ detects · ✗ blind · ~ partial.

| guard | net loss | net gain | class redistribution | same-count substitution | corpus growth | FC durable | blocks write |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| grammar fixtures (20) | ✗ | ✗ | ~ | ~ | tolerant | ✓ | via gate |
| **class anchors (20, new)** | ~ | ✗ | **✓** | **✓** (seeded) | tolerant | ✓ | via gate |
| residual invariant | ~ | ✗ | ✗ | ✗ | tolerant | ✓ | **✓ direct** |
| tracked family floor | ✓ | reported | ✗ | ✗ | tolerant | ✓ | **✓ direct** |
| local per-class ratchet | ✓ | reported | ✓ | ✗ | needs re-pin | **✗** | ✗ |
| ground-truth seeds | ✗ | ✗ | ✗ | ✓ (delivery only) | tolerant | ✓ | ✗ |
| sample-sheet review | ✗ | ✓ | ~ | ~ | manual | ✓ | ✓ |
| DET cache reconciliation | ✓ | ✓ | ✓ | ✓ | n/a | ✓ | **✓ direct** |

**The row that was missing is the class anchor**, and the matrix shows why: it
is the only tracked, fresh-clone-durable row with a ✓ in *both* redistribution
and substitution. Every count-based guard is structurally ✗ in both, because a
count cannot see a substitution.

---

## 5. GROUND TRUTH — why it cannot simply absorb this

`experiments/moves/*.json` (20 files, **tracked**) → `foundry_ground_truth.py`
→ Gate 2 row 7. 534 Captain-ratified `class: human` seeds with verbatim quotes.

**It is scoped to DELIVERY by construction, not by accident.** `expected_delivery(axis, tokens)`
derives the expected value from **the axis slug's own §2 DELIVERY head**. The
lattice's class slugs are spell-ability slugs — grammar §1 omits DELIVERY for
those because CR 113.3a already fixes it — so `targeted-exile-creature` has no
DELIVERY head to grade. **Ground truth would be reading a slot the lattice does
not have.**

Widening it to mean "all facts" would redefine what `moves/*.json` asserts,
which the brief itself lists under STOP. **Recommendation: keep moves
delivery-only.** Its *pattern* — tracked, per-card, evidence-quoted,
growth-tolerant — is the right one and is what the class anchors copy, at the
layer that owns the fact.

---

## 6. OPTIONS, STRONGEST CASE EACH

| option | strongest case | why not now |
|---|---|---|
| **A. directional per-class floors** | natural extension of ratchet semantics; catches redistribution when a class falls | needs a tracked home; `det-patterns-v2.json` is not obviously it; **and a count still cannot see substitution** |
| **B. typed evidence-backed fact assertions** | per-member correctness, fresh-clone durable, reusable across future families | this is AQ4's predicate row wearing a smaller hat — new fact schema, Captain's |
| **C. population guard + semantic seeds** | genuinely complementary, not redundant: §4's matrix shows counts and seeds have disjoint blind spots | **this is what the stack now is** |
| **D. membership snapshot / digest** | strongest detection | duplicates card data toward git, and a hash cannot say whether growth was *correct* |
| **E. generalized fact artifact, axes as derived views** | one substrate for all four consumers | highest burden of proof; **= AQ4**; would discard a working assertion model with 4,233 human assertions |

---

## 7. RECOMMENDATION

**Now (done, and inside the brief's implementation allowance): Option C.** The
guard stack already had counts; it lacked per-member semantic anchors. One
anchor per ratified class, in the existing fixture mechanism shipped with the
2026-08-13 ratification. No new vocabulary, no new schema, no new semantic
category, no codebook mutation, no redefinition of `moves`.

**Enabled for later, not built:** the assertion model is the right substrate for
Searcher B. It needs the AQ5 `level` field to let a consumer select its
semantic layer, and effect coordinates to let Budget Swapper reconstruct a
tuple. Both are extensions of `foundry-codebook/2`, not replacements — which is
the measured argument **against** the brief's Option E.

**The Grand Abolisher ↔ Defense Grid test, answered honestly:** today the fact
layer can say neither card is a `targeted-*` anything, and nothing more. To
relate them a later functional layer needs *who is restricted*, *when*, *what
action class*, and *prohibited vs taxed* — none of which exists as a dimension
today. That is L2 role work, it is judgment, and per §17 of the brief and §5.4
of the audit it belongs to a model adjudicating under human ratification, not
to a regex. **It is blocked on AQ4/AQ5, not on the object lattice.**

---

## 8. DECISION SHEET — Captain

Only items **not** already open as AQ1–AQ9. Everything about the predicate row,
the `level` field, magnitude and role remains AQ4/AQ5 and is not re-asked here.

### FL-1. Anchor coverage for the 3 unanchored classes

**Question.** `bounce-planeswalker`, `destroy-battle` and `exile-planeswalker`
have live members but no single-class card to anchor them. Seed them with a
multi-class card (expectation becomes a subset assertion), or leave them
reported-uncovered?

**Why now.** They are the residual blind spot for zero-sum movement, and the
gate names them on every run rather than hiding them.

**Measured.** 20 of 23 live classes anchored. `destroy-battle` has 1 member.

- **A.** Leave uncovered, keep reporting. *No new semantics; 3 classes stay blind.*
- **B.** Seed with multi-class cards using subset expectations. *Full coverage; introduces a second fixture semantic ("contains" vs "equals").*

**Recommendation: A.** B invents a fixture semantic to cover 3 classes, one of
which has a single member. Zero members is a hypothesis; near-zero is not worth
a new assertion shape.

**Unchanged either way:** parser, memberships, ratification.

### FL-2. Does the lattice's evidence quote need an effect coordinate?

> ## ✅ RESOLVED 2026-08-13 — RATIFIED AND IMPLEMENTED
>
> **The recommendation below (C, fold into AQ4) was NOT what was ratified.**
> Kept verbatim, per the repo's preserve-history convention; read this banner
> for what actually happened.
>
> **Ruling text:**
> `docs/SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md` §12, with
> amendments A1–A4 from
> `docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md`.
>
> **Outcome: essentially B, generalised past `rule-derived` and stripped of
> the coordinate this section proposed.** An assertion of ANY provenance class
> may carry an optional `locality` field holding **one** coordinate,
> `[face, paragraph]`.
>
> **`ability` and `mode` are NOT stored, and that is the substantive
> correction to the question as posed here.** Measured over the whole corpus:
> **1,791 paragraphs hold exactly one modal bullet and ZERO hold two or more**,
> so the paragraph coordinate already separates modes and a `mode` field would
> be a second source of truth (amendment A1). Modal grouping and selection
> cardinality are **derived** from the owning header (A4); the evidence
> **span** is derived, never stored (§13).
>
> **AQ4 is NOT pre-committed.** The predicate row remains open and out of
> scope; locality addresses *where a fact lives*, not *what it asserts*.
>
> **Implemented and live.** `experiments/foundry_locality.py` (resolver +
> 40 fixtures), the optional field in `foundry_codebook.py`,
> `foundry_det_pass.cmd_apply` emitting on new DET output, and
> `experiments/foundry_locality_backfill.py`, which addressed **7,808 of
> 7,930** assertions on active axes under the backup law. The remaining
> **122** stay unaddressed by rule and are enumerated by
> `foundry_locality.py --report`. Gate 2 row `locality`; stored coverage rides
> the ratchet.
>
> **"Retrofitting across 7,930 assertions is not [cheap]"** — the concern
> stated below — **is the one prediction here that did not hold.** The
> retrofit was one deterministic pass costing $0, because the address is a
> pure function of a quote the assertion already carried.

**Question.** Should a `rule-derived` assertion carry a deterministic
`face` / `ability` / `mode` coordinate alongside its quote?

**Why now.** Cheap while one family writes them; retrofitting across 7,930
assertions is not. Budget Swapper needs effect-local tuples.

**Measured.** Nicol Bolas's 5 assertions are separable by quote alone; his
`Activate only as a sorcery` assertion binds to no ability. Quotes are already
guarded for anchoring by `foundry_ground_truth.py`.

- **A.** Nothing now; recover locality by quote matching.
- **B.** Add derived coordinates for `rule-derived` assertions only.
- **C.** Fold into AQ4 and decide with the predicate row.

**Recommendation: C.** This is the same question AQ4 asks, one field down, and
deciding it separately would pre-commit AQ4's answer.

**If approved (C):** nothing changes today; FL-2 is recorded as a sub-item of
AQ4 so the predicate-row ruling has to answer it.

---

## 9. OUT OF SCOPE, RECORDED

**Gate 2 runs in no CI.** `.github/workflows/` holds only `build.yml`; nothing
references `foundry_gate2.py` or any foundry script. All 14 rows — including
every guard in §4's matrix — execute only when a session remembers. That is
directly against the house rule *"a control that depends on someone remembering
is not a control,"* which is why the single-runner exists. **Relevance to the
fact layer:** every guard this report recommends inherits that gap, so its
durability claims are conditional on a session running Gate 2. **Not fixed
here, per instruction.**

Also unchanged and unresolved on purpose: controller/ownership scope,
`targeted-destroy-token`, and any flicker/removal taxonomy.
