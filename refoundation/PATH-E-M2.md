# The evidence index and evidence-only retrieval — operator page

One installed command, `mtj-foundry-evidence`, with three subcommands: `index`
emits a deterministic full-population artifact, `query` asks it a question, and
`evaluate` grades it against a frozen human panel. The milestone-1 command
`mtj-foundry-report` is unchanged.

**Task authority is not here.** It is GitHub Issue #1: latest `K` -> active `T`.
No repository phase file assigns work. This page says how to
run these things and what their numbers mean, and nothing else.

## Run

```
mtj-foundry-evidence index --root /path/to/mtjawnny-pipeline \
    --input-lock /path/to/mtjawnny-pipeline/refoundation/path-e/input-lock.json \
    > index.json

mtj-foundry-evidence query --index index.json --name "Reanimate" --top 25

mtj-foundry-evidence evaluate --index index.json \
    --panel /path/to/mtjawnny-pipeline/refoundation/path-e/m2-evaluation.json \
    --source-document /path/to/mtjawnny-pipeline/docs/WIRE-PREDICTIONS-2026-08-09.md
```

`index` reads the repository through the accepted milestone-1 boundary and takes
the same input flags as `mtj-foundry-report`, including the same
`--root`-anchored relative-path rule. **`query` and `evaluate` read only the
artifact** (and the panel fixture): copy `index.json` anywhere, delete the
repository from the picture, and a query still answers. That asymmetry is the
milestone property, and it is demonstrated rather than asserted — the acceptance
run queries a copy from outside the repository with `PYTHONPATH` unset.

Every document goes to **stdout**; a failure goes to **stderr** and exits 1 with
nothing on stdout. Redirect stdout wherever you like — that is an operator
choice, not a side effect. The command opens no file for writing.

## The artifact

`mtj-foundry-evidence-index/1`. On the selected pilot inputs it is **24,397,424
bytes**, sha256 `771f1075d4e968f6ba76a7e625253b7c82db3b434f3fe399c6733a24a5fed116`,
and two runs are byte-identical — in-tree and from the installed command with
`PYTHONPATH` unset, all four byte-identical to each other. The evaluation report
is 52,509 bytes, sha256
`1973583a999d23a128b54765acade1d4a78d9e929dafd6f063f1890986385d3c`, also
byte-identical twice.

**The artifact carries the input lock's `status` verbatim**, so it changes when
the lock's status changes. That is the M1 contract working: an earlier digest
taken before this milestone recorded the Manager selection describes a different
document, not a different corpus. Serialization is compact
(`separators=(",",":")`, `ensure_ascii=False`, one trailing newline) rather than
the report's `indent=2`: this is a 38,233-row machine artifact, and indenting it
would spend most of the file on whitespace nobody reads.

It carries, per card:

* `oracle_id`, `name`, `normalized_name`;
* `gate0_eligible` — a **boolean on the row, never a filter over rows**;
* `faces` — every face the permanent corpus capability exposes, with oracle text
  and the existing face fields. Split, flip and adventure layouts read correctly
  because faces come from `corpus.card_faces`, not from the raw `card_faces` key;
* `evidence_state`;
* `memberships` — for each ACTIVE axis the card is on, the axis id plus the
  codebook's member object **copied whole**. `class`, `source_ref`, `quote`,
  `corpus_ref`, `evidence_status`, `locality`, a member-level `tier` and any key
  a later schema adds all survive, because the copy does not enumerate them.

Plus an `axes` catalogue for active axes (definition, scope, source, and the
axis's `active_member_count`), the corpus name index with every id kept for a
shared name, the selected input identities, and the whole milestone-1
population/coverage arithmetic under `conservation`.

## `UNASSIGNED` means exactly one thing

`UNASSIGNED_NO_ACTIVE_EVIDENCE`: **the selected codebook records no membership
for this card on any axis whose status is `active`.** That is the whole claim.

It is **not** a judgement that the card is dissimilar to anything, **not** a
review that rejected it, **not** negative evidence, and **not** a claim the card
is semantically empty. 31,958 of 38,233 corpus ids carry it. Most of that is
unreviewed, not judged, and anything that reads absence as a negative signal is
converting unknown into false.

## Retrieval, and its declared ordering

A candidate is evidence-discoverable when the anchor and the candidate **share
at least one ACTIVE axis** in the selected codebook. That is the entire rule.
Non-shared axes and absent memberships contribute exactly zero in either
direction, and a card sharing nothing is simply not returned — never returned
with a low score.

Ordering, declared before the frozen panel was run and unchanged after seeing
its result:

1. `shared_axis_count` **descending**;
2. `shared_axis_cardinalities` **ascending, lexicographically** — each shared
   axis's active member count, sorted ascending;
3. `oracle_id` **ascending** — arbitrary, deterministic, carries no semantics.

**No constant appears in that rule** — no weight, no threshold, no DF ceiling.
It is still an unratified presentation policy, not a ruling about similarity.

Every candidate carries its raw features before the order is applied, plus
`tie_block_size` and `tie_block_first_rank`, so a tie is never read as a ranking.
An ambiguous name **halts**: 216 normalized names in the selected corpus are
shared by more than one id, and `oracle_id` is the only card key.

## What the frozen evaluation measured — a poor result, reported as one

Panel: `refoundation/path-e/m2-evaluation.json`, transcribed from
`docs/WIRE-PREDICTIONS-2026-08-09.md` (git blob
`cff13bb5aa78a354a48fe50e65fe6da2f699316f`, verified at run time), which a human
committed **before** the 2026-08-09 wire experiment existed. No model invented
any label.

**Candidate discovery: 12 of 28 named-correct cards, 42.9%.** Per anchor:
Rampant Growth 3/11, Beast Within 2/5, Reanimate 3/8, Reliquary Tower 4/4. Of
the 16 not discoverable, **14 carry no active membership at all** and **2 carry
active membership only on unrelated axes** — Solemn Simulacrum on
`rule:death-trigger-draw-card`, Rapid Hybridization on
`rule:prevents-regeneration`. This is the same coverage wall the 2026-08-09
result measured at 13/33; it has not moved.

**Presentation: of the 12 discoverable, 3 reach the top 10 and 7 the top 25 —
and all 12 sit in a tie block larger than one.** Three of the four anchors carry
exactly one active axis, and with one shared axis every candidate has identical
features, so the whole pool is a single tie block ordered by `oracle_id`. **The
declared ordering has no signal to rank with, and this is the milestone's
sharpest product finding**: it is the 2026-08-09 "displayed top-10 was an
alphabetical slice of a 44-row tie" defect reproduced structurally, from
different code, on different data. Rampant Growth's 22 candidates are one tie
block; Reanimate's 61 are one; Reliquary Tower's 42 are one. Only Beast Within,
the sole two-axis anchor, discriminates at all.

**Controls:** Sol Ring and Grand Abolisher both carry zero active memberships,
return `ANCHOR_UNASSIGNED_NO_ACTIVE_EVIDENCE` with zero candidates, and acquire
no fabricated evidence.

**Known historical failure probes:** all seven are present as ABSENCE rather than
disguised as a low score. Chaos Warp, Dance of the Dead, Recommission, Emergency
Eject, Excavation Technique and Stroke of Midnight are all
`UNASSIGNED_NO_ACTIVE_EVIDENCE`; Unearth carries one membership, on
`rule:cycling`, which is unrelated to any panel anchor. **The `D-W-2` membership
gap the 2026-08-09 result named — `rule:reanimate-from-graveyard` holding Animate
Dead and not Dance of the Dead — is still open, and this measurement shows it as
a visible absence rather than a buried rank.**

## What this measurement does NOT prove

* Not that the selected evidence is sufficient for a product.
* Not that the declared ordering is the right one, or a ratified one.
* Not that a not-discoverable card is dissimilar to its anchor. It means the
  codebook records nothing about the pair.
* Not that a discoverable card is similar beyond the one axis the codebook
  records.
* **Not that milestone 3 is authorised.** That is the Manager's call from this
  evidence, and nothing here confers it.

One property is worth naming rather than hiding: ordering key 2 reads an axis's
CARDINALITY, which moves when any other card joins or leaves that axis. That is a
specificity feature over positive evidence, not a penalty for absence, but it
does mean one card's membership can change another card's order —
`WIRE-RESULT-2026-08-09.md` §7 records a live instance (88 Alchemy memberships on
51 active axes, 48 of them duplicate pairs with their paper twin, inflating
exactly this number). It is reported intact rather than corrected for, because
correcting it would be a codebook mutation.

## Deferred — not started, not promised here

The static Searcher-B pilot, any viewer, any publication, embeddings, quote
entailment validation and any codebook repair are **milestone 3 or later** and
require new Manager authorization. AQ4 is PAUSED, Bridge v0 PARKED_UNUSED, Step6
NOT_STARTED, Merge NO.
