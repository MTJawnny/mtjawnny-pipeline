# SESSION 3 (APPLY) — HALTED BEFORE MUTATION. The approved plan is unappliable.

**2026-08-09.** Session 3 was taken as directed: build the applier against
`docs/archive/CONSOLIDATION-APPLY-DIRECTIVE.md`, apply plan
`b545d2bf2fbd9245950c9038c911d7f2ba01355d67c3c8c3736bf8a6f9e90188`, re-run the
wire experiment.

**The applier was built and it halted the plan on its own pre-mutation
verifier. Nothing was written.** The codebook is byte-identical to its
pre-session state (`b4197e94…`), no backup was consumed, and the plan artifact
on disk is untouched.

> **189 of the plan's 13,565 member additions target 2 axes the plan never
> creates.** They are A15 clusters that session 2a classified `instantiate`,
> and session 2b's expander builds their member rows without ever adding the
> axis. Applying it would have halted mid-write inside `merge_assertion`.

---

## 1. THE DEFECT

`foundry_consolidate_run1_enumerate.py`'s `expand()` step 3 handles an A15
promotion row whose target slug is not yet an axis:

```python
slug = row["target_slug"]
exists = slug in active
if exists:
    emit(...)                      # -> additions / merges
else:
    additions[key] = {...}         # <- member row built; NO axis ever created
```

`new_axes` is populated only from `classify_nodes()` — the grammar virtual
nodes. An A15 `instantiate` cluster never reaches it.

| A15 cluster | target slug | 2a disposition | rows | axis created by the plan? |
|---|---|---|--:|---|
| targeted-destruction-creature | `rule:targeted-destroy-creature` | **instantiate** | **188** | **NO** |
| activated-tap-opponent-artifact | `rule:activated-tap-opponent-artifact` | **instantiate** | **1** | **NO** |
| cant-be-blocked-except-by-count | `rule:cant-be-blocked-except-by-count` | join-existing-node | 2 | yes (it is a node) |
| etb-create-token-blood | `rule:etb-create-token-blood` | join-existing-node | 2 | yes (it is a node) |
| etb-create-token-clue | `rule:etb-create-token-clue` | join-existing-active | 1 | already active |

The three dispositions that work are the three where something *else* already
guarantees the axis. `instantiate` is the one disposition that makes the plan
responsible for creating it, and it is the one the expander does not implement.

### 1a. WHY NO 2b GATE SAW IT — and this is the transferable part

Session 2b ran five gates and every one passed. Each is blind to this for its
own reason:

* **`gate_counts`** compares `new_axes_instantiated` against 2a's
  `expected_counts`. **Both sides count only `classify_nodes` instantiations**
  — 87 either way. A closed loop closed on a quantity that both sides compute
  the same wrong way proves the two computations *agree*; it says nothing
  about whether either is right. This is the strongest-looking gate in 2b (the
  one its docstring calls "the closed loop that makes an external audit of 2a
  meaningful") and it is the one that fails here.
* **`gate_merge_collisions`** walks `merges` only. All 189 rows are additions.
* **`expected_final_counts`** derives `axes_active_after` from
  `len(ex["new_axes"])`, so it inherits the omission and remains perfectly
  self-consistent: 403 + 87 = 490, and 8,982 + 13,565 = 22,547. **Both numbers
  are internally correct and jointly impossible.**
* **duplicate-freeness** and the **quote re-walk** are true and irrelevant.

Same family as *"a ratified token with no emitter looks exactly like one with
no members"*: the count is right, the thing it counts does not exist.

### 1b. THE FIX THAT LANDED

`gate_every_row_has_an_axis()` in `foundry_consolidate_run1_enumerate.py`:
every planned row must land on an axis that will exist at apply time — active,
or instantiated by this plan. It fires on the current inputs, naming both
slugs and both row counts, and **halts before writing the plan**. Verified: a
regeneration now stops rather than producing an unappliable artifact.

It halts rather than instantiating, because an axis record needs a
**definition** and a **scope** and 2a's `a15_cluster_summary` carries neither.
Directive §1: a gap in 2a is a defect in 2a, fixed by ruling on it, never by
2b or 3 exercising judgment.

---

## 2. THE APPLIER — built, and it is the reason this was caught

`experiments/foundry_consolidate_run1_apply.py`. Every gate the directive asks
for, plus the pre-mutation verifier that stopped this.

| gate | directive | result on plan `b545d2bf…` |
|---|---|---|
| plan hash == Captain's go | PRECONDITIONS | matches |
| live codebook == plan's recorded pre-state | §1 | matches (`b4197e94…`) |
| 2a artifact hash, 0 blocking decisions | PRECONDITIONS | matches, 0 |
| **independent verifier (A13)** | §2 | **HALT — 189 rows, 2 axes** |
| promotions folded with lane fields | §1.3 | R5 **163**, A15 **194**, all present |
| quote-verbatim, all rows | A13 | **15,371 / 15,371** across 12,454 cards |
| backup + restore drill | §2 | not reached |
| conservation, `expected_final_counts`, lint | §2 | not reached |
| determinism ×2, 500-row spot verifier | §2 | not reached |

**With the two axes patched in as placeholders, the rest of the plan verifies
completely clean** — all 15,371 rows on the right axis in the right section
with A1-conformant assertions, all 15,371 quotes verbatim in full oracle text,
every R5 and A15 promotion folded with its lane triple intact. **This is one
defect, not the first of a queue.** That was measured, not assumed: the whole
verifier was re-run against a patched copy specifically to avoid handing back
one finding, getting a new plan, and finding the next.

Design notes worth keeping:

* **The restore drill runs before any mutation**, and shares one
  `restore_from_backup()` with the failure path and with determinism pass 2 —
  so the drill proves the same code a failure would run.
* **`fc.halt` is `sys.exit`**, so the apply block catches `BaseException`, not
  just unexpected errors. Re-raising a halt without restoring would leave a
  half-applied codebook behind the message saying it stopped.
* **The spot verifier re-reads the written file from disk.** Every other gate
  inspects the in-memory object the writer just built and therefore shares the
  writer's blind spots; this one shares only the serializer's.
* **A redirect is a routing record, not a membership.** The 2,925 routing rows
  go to `foundry-killed-slug-routing/1` and are deliberately absent from
  `expected_final_counts` — turning one into a membership would be session 3
  exercising judgment.
* Quotes are never printed to console (A14); halt messages name a slug and an
  oracle_id and stop.

---

## 3. DECISION SHEET — two axis records, and one question that is not new

Both slugs pass `validate_slug`. Both are **`NOT IN CODEBOOK`** under any
status, and Gate 3 finds **no ruling** on either.

### D-APPLY-1 · `rule:targeted-destroy-creature` — 188 rows

**Evidence:** Bone Splinters, Dark Banishing, Rend Flesh, Bring Down, Dakmor
Lancer, Lich's Caress, Gallant Strike … — 188 cards.

**The lattice already names it, and gates it.** `docs/grammars.json`, the
`targeted-<action>` family note:

> *"…in the per-axis walk's rename set as candidates to bring into the lattice
> (e.g. targeted-destruction-creature) once member evidence is checked for a
> single dominant class; **do not auto-rename**…"*

So the node is contemplated **and explicitly conditioned on an evidence check**.
2b instantiating it mechanically off an A15 canonical-form match is precisely
the auto-route that sentence refuses. That is the substantive reason this needs
a ruling and not a code fix.

**Proposed record** (not load-bearing until ratified):

```
slug:       rule:targeted-destroy-creature
definition: Destroys a target creature. The creature-class facet of the
            ratified targeted-<action>-<class> lattice.
scope:      opponent-stuff        (matches the parent axis)
source:     B-only
```

**The complication, measured:** the parent `rule:targeted-destroy` is active
with **172 members** and its ratified definition already reads *"parameterized
by type (**creature** / artifact / artifact-or-enchantment / permanent /
nonland-MV<=N)"* — though its `parameterized` field is `false`.

* **35 of the 188 are already members of `rule:targeted-destroy`** and would
  sit on both.
* This plan adds **0** rows to `rule:targeted-destroy` itself.

That 35 is the **membership-exclusivity** question Captain deferred on
2026-08-09 (*"membership should probably be exclusive"*), scoped exactly as the
deferral asked — *within an effect family*, blast radius measured. **It does
not have to be answered to ratify the axis**, and answering it here would
resolve a deferred question inside a mechanical apply.

**Recommendation: instantiate.** Creature removal is the most deck-relevant
effect class in the game and 188 rows is a real archetype, which is Captain's
ratified ranking criterion. The 35 overlaps stay as they are, logged against
the deferred exclusivity item.

### D-APPLY-2 · `rule:activated-tap-opponent-artifact` — 1 row

**Evidence:** Touchstone — *"{T}: Tap target artifact you don't control."*
One card.

**Proposed record:**

```
slug:       rule:activated-tap-opponent-artifact
definition: An activated ability taps a target artifact an opponent controls.
scope:      opponent-stuff
source:     B-only
```

**Known before this session.** `CDR-PROPOSALS.md:285`, carried in
`RATIFIED-RULINGS-REGISTRY.md`:

> *"Scope must also include A15-instantiated axes (`rule:activated-tap-opponent-artifact`
> and node `rule:activated-tap-or-untap-opponent-artifact` are sibling
> single-member axes created by two routes in one session — neither the B-02
> review nor rev 1's pair list covers them)."*

The sibling **is** in this plan's `new_axes`. The two are not synonyms —
Touchstone only taps; the sibling's definition is *"choose to tap **or**
untap"* — so folding is a semantic loss, not a dedupe.

**Recommendation: instantiate, and flag the pair** for the AG-EQUIV-01
near-duplicate pass CDR-05 already recommends. A one-member axis reserved by a
closed lattice is not the one-card-token trap: same standing as
`coin-flip-lost-trigger` at one member, which stands because CR 705.2 reserves
the slot. If Captain prefers the alternative, the honest one is **route
Touchstone to the sibling and drop this slug** — not fold the two axes.

### Also open, unchanged by this session

`grammars.json`'s `instantiated_members` still lists **`rule:targeted-destruction`**,
the pre-rename spelling, and the action facet's `closed_vocab` still carries
`"destruction"` with `"destroy"` absent entirely. That is §7 item 2 of the A15
ruling doc, still open, and it is the same rename this decision sits on top of.
**Generator fix (G4), not a hand edit.**

---

## 4. THE PATH BACK TO AN APPLY

1. Captain rules D-APPLY-1 and D-APPLY-2 (or declines one, which changes the
   row counts and therefore the plan).
2. The ratified axis records go into a **declared source 2a/2b reads** — never
   typed into the expander.
3. Regenerate: `python3 experiments/foundry_consolidate_run1_enumerate.py`.
   `gate_every_row_has_an_axis` now stands between that command and another
   unappliable artifact.
4. **The plan sha256 changes, which voids the current go.** Captain's go names
   one artifact by hash; a different plan is a different mutation.
5. `foundry_consolidate_run1_apply.py --dry-run` — full verifier, zero
   mutation — then `--go-sha256 <new hash>`.
6. Then `foundry_wire_experiment.py --json`, whose predictions are already
   committed (`d48eb4a`).

**Expect the counts to move.** Two new axes make `axes_active_after` 492, not
490, and `new_axes` 89, not 87 — the directive's stale "93" and this plan's 87
were *both* counting only the node route.

---

## 5. WHAT WAS NOT DONE, STATED PLAINLY

* **The codebook was not mutated.** `b4197e94…`, unchanged, lint clean, Gate 2
  green (12 passed, 1 known-failing `family_sweep`).
* **The plan artifact was not modified.** Still `b545d2bf…`.
* **2a was not re-run** and its artifact is untouched.
* **No axis was created and no definition was ratified.** §3 is a proposal.
* **`foundry_wire_experiment.py` was not re-run** — its condition is
  post-apply coverage, and coverage did not move.
* The applier's post-mutation gates (backup, restore drill, conservation,
  determinism ×2, spot verifier, companion artifacts) are **written but never
  executed against a real mutation.** They are code that has not run. The
  pre-mutation half is what has been exercised.
