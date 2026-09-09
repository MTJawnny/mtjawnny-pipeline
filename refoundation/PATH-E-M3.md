# The static diagnostic pilot — operator page

One installed command, `mtj-foundry-pilot`. It takes two already-emitted
milestone-2 artifacts and writes a self-contained static bundle that any plain
file server can host. `mtj-foundry-report` and `mtj-foundry-evidence` are
unchanged.

**Task authority is not here.** It is GitHub Issue #1: latest `K` -> active `T`.
Current phase state is `refoundation/ACTIVE-PHASE.yaml`. This page says how to
run the thing and what its output means.

## What this milestone is, in one paragraph

M2 was accepted as a **trustworthy substrate**, explicitly not as a
product-quality result. M3 closes the artifact -> browser loop over that
substrate and nothing else. It adds no evidence, repairs no membership, tunes no
ranking, and ships no model, embedding or text similarity. **Its job is to make
the current evidence — including how thin and how tied it is — visible in a
browser rather than only in a JSON file.**

## Run

```
# 1. emit the two accepted milestone-2 artifacts
mtj-foundry-evidence index --root /path/to/mtjawnny-pipeline \
    --input-lock /path/to/mtjawnny-pipeline/refoundation/path-e/input-lock.json \
    > index.json

mtj-foundry-evidence evaluate --index index.json \
    --panel /path/to/mtjawnny-pipeline/refoundation/path-e/m2-evaluation.json \
    --source-document /path/to/mtjawnny-pipeline/docs/WIRE-PREDICTIONS-2026-08-09.md \
    > evaluation.json

# 2. build the bundle from those FILES. No repository is read.
mtj-foundry-pilot --index index.json --evaluation evaluation.json \
    --output /tmp/pilot-bundle --verify

# 3. serve it
python3 -m http.server --directory /tmp/pilot-bundle 8000
```

`--verify` re-reads the written bundle and checks it against the source
artifact: manifest digests, the full corpus population, and **every** assigned
anchor's candidate order and tie blocks against `mtj_foundry.retrieval.query`.

Exit contract is milestone 1's: **0** with a summary on stdout, **1** with one
`STOP — …` line on stderr and nothing on stdout, **2** for argparse usage.

### Why a third console script rather than a fourth subcommand

`mtj-foundry-evidence`'s accepted contract states that *the command writes no
file and creates no directory*. A bundle builder writes several hundred files.
Folding it in would have falsified an accepted contract line and required
editing accepted prose for tidiness — which is what `evidence_cli` itself
declined to do to `mtj-foundry-report`. M2's surface is untouched.

## What the builder reads and writes

Reads exactly two artifact files, plus its own package-owned template
(`src/mtj_foundry/pilot_assets/`). **No codebook, corpus, repository root,
authority selector, input lock or network.**

Writes only under the explicit `--output` directory, under one stated rule:
create a new path, use an empty one, replace one whose `manifest.json` this
builder wrote (removing exactly the files that manifest lists), and **refuse
everything else**. There is no `shutil.rmtree` in the module and a test asserts
its absence from the import closure, not from the prose.

**A recognised prior manifest is fully validated before anything is deleted**
(M3.R1). Matching the schema proves only that the document *claims* to be ours;
`files` must also be a list, every entry an object with a non-empty string
`path`, and every path must pass the output-root containment check. All of that
runs in one pass that unlinks nothing, so a manifest whose last entry is
malformed does not leave its first nine files deleted. A malformed
schema-correct manifest raises `PilotOutputError` and reaches the operator as
the usual exit 1 with one `STOP — …` line. Only the fields the replacement
actually consumes are checked — refusing a bundle over a missing `sha256` would
reject bundles that are fine.

## The bundle

`mtj-foundry-static-pilot/1`, status `DIAGNOSTIC_NOT_PRODUCT_QUALIFIED`.

```
index.html                  assets/pilot.css   assets/pilot.js
data/meta.json              identities, population, frozen metrics, disclosure
data/cards.json             columnar directory of EVERY card in the corpus
data/names.json             the artifact's own name index, ids -> card indices
data/normalization.json     python's strip set + full case-fold map, derived
data/axes.json              the active-axis catalogue
data/evidence.json          every active membership, member objects verbatim
data/text/<xx>.json         faces, sharded by oracle_id[:2]
data/retrieval/<xx>.json    precomputed tie blocks per assigned anchor
manifest.json               every emitted file's path, sha256 and byte size
```

`manifest.json` covers every emitted file **except itself** — a file cannot
carry its own digest — and names that exclusion in `self_excluded`. Two builds
from the same artifacts into unrelated output roots are byte-identical, manifest
included; the source PATH is deliberately not recorded, only the digest, so the
same bytes fed from two directories produce the same bundle.

### The browser boundary — the design's load-bearing choice

**Python precomputes every candidate list by calling the accepted milestone-2
`retrieval.query`, once per assigned anchor.** The JavaScript contains no
comparator, no sort key, no candidate rule, no feature arithmetic and no
threshold; it renders tie blocks in the order it was given. A defect in the page
can misdraw a block — it cannot invent a different ranking, because there is no
ranking code there to be wrong.

That is checked, not asserted: `pilot.verify_retrieval_equivalence` re-runs the
accepted retrieval and compares the **emitted bytes** — candidate sequence,
shared axis ids, tie-block boundaries and block features — for **every** assigned
anchor. It is exhaustive because the whole sweep is one pass of the same queries
the build already made.

**The tie block is the transport unit**, not a compression trick: two candidates
are in one block exactly when they are equal under ordering keys 1 and 2, so
those features belong to the block. **Individual ranks are not written at all** —
key 3 is `oracle_id` ascending and carries no semantics, so a per-member ordinal
would be a number the artifact does not mean.

## What the page shows

Every card of the selected corpus is findable, by name or by `oracle_id`.

**Query normalization is the accepted Python semantic, run in the browser**
(M3.R1). The artifact's name index is keyed by `str.strip().casefold()`, so the
bundle carries `data/normalization.json` — Python's own strip set and full
case-fold map, derived at build time by asking this Python about every Unicode
code point, and proven against `str.strip().casefold()` before a byte is written.
`toLowerCase()` is not full case folding (U+017F folds to `s`, U+00DF to `ss`)
and `trim()` is not `str.strip()` (Python strips U+001C–001F and U+0085, which
`trim` keeps; `trim` removes U+FEFF, which Python keeps — neither set contains
the other). **This is a lookup boundary, not a search feature**: it turns typed
text into a key, and every lookup after it is still exact, prefix or substring
against the artifact's own key list. An `oracle_id` is matched after the strip
only — case-folding an identity would invent a rule the artifact does not have.
Gate #0 eligibility and evidence coverage are **badges**, never filters the
bundle applied; the two checkboxes in the finder are the reader's own view
state and say so. An ambiguous normalized name is announced as ambiguous and
every identity is listed — nothing is collapsed, because `oracle_id` is the only
card key. Multi-face cards show every face with its own text.

An **assigned** anchor shows its faces, its active memberships with the codebook
assertion copied whole (class, source_ref, quote, corpus_ref, evidence_status,
locality — rendered without a fixed field list, so a field a later schema adds
still appears), the total candidate count, and the candidates as **tie blocks**,
each labelled with its size, its position range, its shared-axis count and
cardinalities, and an explicit note that the order inside it is arbitrary.
Expanding a candidate shows **both sides'** stored assertions on each shared
axis — the whole of the recorded reason the two cards are connected.

An **unassigned** anchor shows `UNASSIGNED_NO_ACTIVE_EVIDENCE`, zero candidates,
and a prominent statement that this is an absence of evidence and **not** a
finding that the card has no similar cards.

A persistent disclosure panel carries the milestone's limits. **Every number in
it is interpolated from the two source artifacts, and so is every quantifier** —
"a majority" is as much a population claim as "31,958" is, and fixing the digits
while leaving the adjective would move the same defect one word to the right.

## What the bundle does NOT prove

* Not that the selected evidence is sufficient for a product.
* Not that the declared ordering is the right one, or a ratified one.
* Not that a card with no candidates is unlike anything.
* Not that the connections shown are complete.
* **Not that any later milestone is authorised.**

The accepted M2 measurement stands unchanged and is shown on the page: candidate
discovery 12 of 28, 3 of 12 discoverable in the top ten, 7 of 12 in the top
twenty-five, and 12 of 12 in a tie block larger than one. The pilot makes that
result *more* visible, not less — on the selected inputs Rampant Growth's 22
candidates, Reanimate's 61 and Reliquary Tower's 42 each render as **one** tie
block, and Beast Within, the only multi-axis panel anchor, splits its 180 into
three blocks of which the largest holds 164.

## Deferred — not started, not promised here

Publication or deployment of any kind, codebook repair, coverage work,
embeddings, lexical similarity, quote entailment validation, a ratified ordering,
AQ4, Bridge v0, Step6 and any merge to main. AQ4 is PAUSED, Bridge v0
PARKED_UNUSED, Step6 NOT_STARTED, Merge NO.
