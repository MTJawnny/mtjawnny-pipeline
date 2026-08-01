# Output-trim proposal — PROPOSED, NOT RATIFIED

Status: **PROPOSAL ONLY.** Nothing in this document is implemented.
`foundry_stage1b.py`'s `OUTPUT_SCHEMA` still requires the full
`{lane, label, definition, actor_scope, evidence_quote}` shape for every
lane, exactly as before. This document is input for Captain's ratify/reject
call, per Captain's 2026-07-31 directive (point 2): "Propose (don't
implement yet) the output-trim ruling... Present it with the reconcile-side
verification design for my ratification."

---

## 1. The trim

**lane=codebook confirmations emit bare slugs**: `{"lane": "codebook",
"label": "rule:some-slug"}` — no `definition`, no `actor_scope`, no
`evidence_quote`.

**lane=free and lane=codebook-grammar keep the full mandatory shape**,
unchanged, evidence-quote-or-discard exactly as it is today.

### Why the line is drawn here

- lane=free and lane=codebook-grammar are each asserting something NEW:
  either a brand-new candidate axis, or a new grammar-composed slug
  instantiating a virtual node. Both mutate codebook structure (a new axis,
  or a new member of a family that didn't exist before). The
  evidence-quote-or-discard law exists precisely to gate structural changes
  — it stays in full force here.
- lane=codebook is asserting something narrower and lower-stakes: "this
  ALREADY-RATIFIED axis, whose definition and existing membership are
  already established, is ALSO present on this card." Worst case on a bad
  confirmation: one axis's member list gets one wrong entry. It doesn't
  corrupt the axis's definition, doesn't create a phantom axis, and doesn't
  propagate into the grammar layer. That is a materially smaller blast
  radius than a bad free/grammar-lane claim.

### Measured savings (real data, not estimated)

Computed directly from `stage1b_raw_results_batch{6,7}.jsonl` (2,400 cards,
4,158 real axis instances — not a sample, the actual historical output):

| | codebook-lane axes | free/grammar-lane axes |
|---|---:|---:|
| Mean full-JSON size | 286.2 chars (~72 tok) | 356.1 chars (~89 tok) |
| Mean trimmed-JSON size | 61.6 chars (~15 tok) | unchanged |
| Reduction | **78.5%** | 0% (not trimmed) |

Lane mix, same two batches: **34.2% codebook-lane, 65.8% free-lane**
(2,001 and 2,157 total axes; batch 6 = 35.0%/65.0%, batch 7 = 33.4%/66.6%).
Average total axes/card = **1.7325** (2,400 cards → 4,158 axes) — this
replaces the old, never-measured "2.5 axes/card assumed" placeholder
`foundry_stage1b.py` has carried since batch 1; §3's re-pricing uses the
real 1.7325 figure throughout, trim or no trim.

Blending: output tokens/card without trim ≈ 144 tok; with trim ≈ 111 tok —
a **23.1% reduction in total output tokens** (smaller than the 78.5%
per-axis figure because free-lane axes, which aren't trimmed, are the
majority of axis volume).

---

## 2. Reconcile-side verification design (what replaces the quote)

The honest premise: most codebook axes are SYNTH-judgment territory
precisely because they are NOT mechanically decidable (if they were, DET
would own them, per CORPUS-PASS-PLAN.md's own Lane 1/Lane 2 split). Losing
the quote means reconcile cannot deterministically re-derive "is this
specific card really a match" the way it could re-run a DET pattern.
**This proposal does not pretend otherwise.** It substitutes two cheaper,
weaker, but real checks for the one expensive, strong check — not a
like-for-like replacement, a different risk/cost tradeoff.

### Layer 1 — anchor-term plausibility gate (per-instance, ~free)

For every active axis, reconcile maintains an **anchor-term set**: the
union of significant (non-stopword) tokens appearing across that axis's
existing quote-verified members' evidence quotes (this data already exists
in the `decisions/batch-N.json` history — no new collection needed, just an
index built once and refreshed as new quote-verified members arrive via
free/grammar lane or SUP triage).

For every bare-slug codebook-lane confirmation, reconcile checks: does the
card's own oracle text contain **at least one** of the axis's anchor terms?
If not, auto-reject — folded into the anomaly report exactly like today's
`lane=codebook, label didn't resolve` case (not silently trusted, not
silently discarded either — surfaced).

- Cost: zero API calls, pure string matching against text reconcile
  already has on hand.
- Catches: gross mismatches — wrong-slug confirmations, hallucinated
  matches with no textual basis at all.
- Does NOT catch: a card that genuinely shares vocabulary with an axis but
  fails a specific qualifier the axis's definition requires (the exact
  batch-5 `rule:counters-noncreature-spell` shape: "Counter target spell."
  shares "counter"/"spell" with real members but has no noncreature
  restriction). Vocabulary overlap is necessary, not sufficient.

### Layer 2 — fixed-seed sample audit per axis per batch (bounded cost)

Reuses the EXACT mechanism already ratified for DET patterns (walk-
ratification sec.2.5: "each pattern emits a fixed-seed 20-hit sample
sheet... seed 20260731 + pattern index"). Applied here to SYNTH instead of
DET: every batch, for every axis that received new bare-slug codebook-lane
confirmations, reconcile draws a fixed-seed sample of up to 20 of them (all
of them if fewer than 20) and does a REAL check — oracle text against axis
definition, same rigor as today's quote verification, just applied to a
bounded sample instead of every instance.

**Proposed threshold**: if a sampled batch's precision for an axis falls
below 90%, that axis's bare-slug trim privilege is SUSPENDED — falls back
to requiring full quotes for that axis in all future batches until Captain
explicitly re-enables it (the threshold and the auto-suspend action are
both Captain's call to set differently; 90% is a starting recommendation,
not asserted as correct).

- Cost: bounded at ≤20 real oracle-text checks per axis per batch, not
  per-card — the same order of magnitude as the review workload SUP triage
  already does per batch today.
- Catches: systematic axis-level drift (an axis the model starts
  over-applying).
- Does NOT catch: an individual bad confirmation outside the sampled 20 —
  probabilistic, not exhaustive. **This is the real tradeoff being
  ratified, stated plainly**: some fraction of bad codebook-lane
  confirmations will enter member lists undetected, at whatever the
  model's true per-axis error rate turns out to be. Free/grammar-lane's
  quote gate is deterministic and complete; this is not, by design, in
  exchange for the token savings in §1.

### Layer 3 (optional refinement — Captain's call whether to also ratify)

**Trust-tier gating**: only axes with an established track record (proposed
starting bar: ≥10 prior quote-verified members, and no history of a Layer-2
suspension) are eligible for the trim at all. Newly-created or low-volume
axes always require full quotes regardless of lane, until they earn
trust. This bounds the trim's blast radius to axes where SYNTH's historical
accuracy on that specific axis is already known, rather than extending the
"your word is trusted" privilege to every axis from day one.

Layer 3 is presented as optional because it adds real bookkeeping
(reconcile needs to track a trust flag per axis, not just an anchor-term
index and a sample-precision history) for a benefit that Layers 1+2 may
already mostly capture — Captain may reasonably decide the added complexity
isn't worth it, or may want it precisely because it bounds risk on new
axes where Layer 2's history is thin (a brand-new axis with 3 prior members
doesn't have enough of a track record for a 20-sample audit to mean much
yet).

---

## 3. What this proposal does NOT change

- The evidence-quote-or-discard law itself (CLAUDE.md, MASTER-HANDOFF.md) —
  it stays universal for free/grammar-lane and for every axis not yet
  trim-eligible.
- `OUTPUT_SCHEMA`/`build_packed_output_schema()` — unchanged until
  ratified; this document proposes, it does not implement.
- Nothing about DET pattern verification (the sec.2.5 20-hit sample-sheet
  standing condition) — Layer 2 above borrows its SHAPE, not its
  instance data.

## 4. If ratified

Implementation would touch: `foundry_stage1b.py`'s `OUTPUT_SCHEMA` (a
conditional per-lane schema, or two schema variants selected by a
discriminator), `foundry_consolidate.py`'s `load_raw_instances()` (accept
bare-slug codebook-lane rows without a quote field), and a new reconcile-
side module for the anchor-term index + fixed-seed sample-audit bookkeeping
(Layers 1–2) plus, if Layer 3 is ratified, a per-axis trust-tier field in
`codebook.json`. None of this is built yet — scoped here only so the size
of the follow-on work is visible alongside the ratification ask.
