# PICK UP HERE

**Deliberately undated and deliberately named without a date.** Handoffs got
picked by filename sort and by `ls -t`, and both orderings selected the wrong
file (`SESSION-START-PROCEDURE.md` Gate 1 records it). This file is the stable
entry point. **Keep the name. Update the contents.**

---

## 0AC. P3 ARCHITECTURE IS APPROVED WITH AMENDMENTS — IMPLEMENTATION/CUTOVER IS NEXT

**Captain ruled P3-1 … P3-5 on 2026-08-14. P3-6 is DONE and reviewed.** This
section is no longer a question. **Do not reopen the architecture and do not
re-run the option comparison** — the packet
(`docs/P3-CODEBOOK-DURABILITY-PACKET-2026-08-14.md`) is the history; the
rulings below are the law.

| | ruling |
|---|---|
| **P3-1** | **C6.** The authoritative codebook is the **EXACT IMMUTABLE R2 SNAPSHOT SELECTED BY THE TRACKED MANIFEST IN THE CURRENT GIT REVISION.** |
| **P3-2** | A tracked hash/metadata manifest: **YES.** |
| **P3-3** | **Every ratified codebook mutation receives a durable snapshot.** |
| **P3-4** | Architecture is approved **BEFORE the first snapshot exists.** The restore drill is a precondition to **AUTHORITY CUTOVER / P3 CLOSURE**, not to architecture approval. |
| **P3-5** | **Foundry CI is READ-ONLY.** |
| **P3-6** | **DONE** — the structured, reason-bound W6 waiver (this phase). |

**P3-1 IS NOT "THE NEWEST R2 SNAPSHOT", AND THE DIFFERENCE IS THE WHOLE
RULING.** Git selects; R2 stores. An uploaded R2 object that no committed
manifest selects is **orphan and non-authoritative** — uploading does not
confer authority. **There is no authoritative `latest.json` for the codebook**;
do not create one and do not read one. (The `/data/v/<date>/` + `latest.json`
discipline governs *shipped product artifacts*; it is deliberately NOT the
model here, because a mutable pointer would move authority without a commit.)

**P3-4, stated so it is not misread as a green light:** the architecture is
authorized, but **until the restore drill succeeds, the current LOCAL codebook
remains the operational source.** A snapshot that exists is not yet an
authority.

**P3-5, and do not shortcut this:** the existing production Actions
credentials (`R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY`) are **known to be
write-capable** — `pipeline/upload.py` and `pipeline/embed.py` both write with
them. **Their existence is NOT proof that a read-only path exists.** Provision
separate read-only Foundry credentials; prefer that over reusing the
production pair.

### ✅ THE PRIVACY BLOCKER IS CLOSED — PRIVATE FOUNDRY STORE PROVEN (2026-08-14)

**Captain ruled `PRIVATE FOUNDRY STORE PROVEN`.** Do not re-run the privacy
investigation and do not re-open the storage choice. Evidence:
`docs/P3-CODEBOOK-DURABILITY-PACKET-2026-08-14.md` **PART ELEVEN**.

**⛔ `mtjawnny` IS PUBLIC AND IS PERMANENTLY DISQUALIFIED as the Foundry
authority store.** Anonymous HTTPS through the product's custom domain returns
byte-exact objects across three `data/` prefixes — including
`data/cache/embeddings.parquet`, an internal build artifact no shipped page
references. **Delivery is bucket-level**, so `r2:mtjawnny/data/foundry/…`
**MUST NOT be used.** *A PREFIX IS NOT PRIVACY* — that sentence stood here as a
caution; it is now a measurement.

**✅ The authority store is the separate private bucket `mtjawnny-foundry`:**

- **r2.dev:** disabled · **Custom Domains:** none · **Bucket Lock:** none
- **Lifecycle:** *no rule expires or transitions completed Foundry objects; the
  default incomplete-multipart abort rule (7 days) remains enabled.* **Never
  shorten this to "no lifecycle rules"** — the short form is false, and a later
  session checking the Dashboard against it would read a normal Cloudflare
  default as undeclared drift.
- Those four are **Captain-verified in the Dashboard**, not machine-proven: the
  Foundry tokens are object-scoped, so even `GetBucketVersioning` returns 403 —
  which is itself evidence they are correctly narrow.

**The capability boundary is proven behaviourally, not by label:**

| remote | capability | measured |
|---|---|---|
| `r2foundry-rw:` | Object Read & Write, scoped to `mtjawnny-foundry` | GET ✅ · PUT ✅ · DELETE ✅ |
| `r2foundry-ro:` | Object Read, scoped to `mtjawnny-foundry` | GET ✅ · LIST ✅ · PUT **403 `PutObject`** · DELETE **403 `DeleteObject`** · overwrite **403 `PutObject`** |
| `r2:` | production, `mtjawnny` only | **separate — never reuse for Foundry authority** |

Bucket existence was proven by a **byte-identical object round-trip, never by
`rclone mkdir`**; an unsigned GET of the sentinel's real S3 endpoint returned
**no bytes**; and no probe was ever written to `mtjawnny`.

**First-snapshot procedure, per the ruling:** the first snapshot is a
**CANDIDATE**, never an authority, until all five succeed — ~~privacy proof~~
**(DONE)**, remote readback + hash match, fresh restore, Gate-equivalence on
the restored copy, and a corrupt-byte negative control that must HALT.
**Four remain.**

### THREE TRANSPORT LAWS — read these before writing any C6 code

**LAW A — EXIT STATUS IS NOT OBJECT INTEGRITY.** `rclone mkdir` returned
**exit 0** while `CreateBucket` was denied and no bucket existed; `rclone
copyto` of a **missing** object returns **exit 0 and creates no file**;
`lsjson` of a missing key returns **`[]` at exit 0**. So **no restore, publish
or bootstrap decision may rest on an exit code** — success means bytes verified
against the tracked manifest, **exact SHA-256 and exact byte size** at minimum,
and a restore yielding zero/wrong bytes **must HALT even at exit 0.**

**LAW B — THE BUCKET PRECHECK MUST NOT MASK THE REAL OPERATION.** Without
`--s3-no-check-bucket`, rclone's precheck returns **403 `CreateBucket`** before
the intended GET/PUT/DELETE — which reads exactly like "this credential cannot
write" and is not that. **All Foundry transport must bypass it**, and every
write-denial control must be aimed past it or it proves nothing.

**LAW C — THE PUBLISHER DOES NOT GUARANTEE IMMUTABILITY.** Object Read & Write
includes `DeleteObject` and R2 offers nothing narrower. **C6 immutability is
application discipline** — new immutable key per snapshot, refuse overwrite,
never prune authority history, verify remote bytes after upload, Git manifest
selects. **Do not claim storage-layer WORM.** Bucket Lock is unratified and
disabled.

### NEXT PHASE — C6 IMPLEMENTATION

Not privacy investigation, not provisioning, not an architecture decision:
those are all closed. The outstanding build is the tracked selector manifest,
immutable candidate publication, remote readback, the bootstrap/restore
verifier, and candidate-vs-authority status.

**P3 IS NOT CLOSED.** C6 architecture approved · P3-6 done · private storage
proven · credential separation proven — **and implementation, candidate,
restore and cutover all outstanding.** The **local codebook remains the
operational source**, no R2 snapshot is authoritative, and **no tracked
authority manifest exists yet.**

---

### The measured state the rulings rest on

`codebook.json` — **403 active axes, 7,930 assertions, 4,233 of them
Captain-ratified `human`** — lives in `experiments/out/`, which
`.gitignore` covers wholesale. So it **has no git history**, and the 88 MB of
timestamped backups protecting it sit in *the same gitignored directory on the
same disk*. `B-MIGRATION-DISCOVERY.md` §5.1 item 6 recorded this on 2026-08-01
(*"codebook.json has no git history — backup discipline is the entire rollback
story"*) and nothing has changed since.

**Why it blocks CI, measured.** Gate 2 is 16 rows and ~142 s — runtime is not
the obstacle. But **7 of the 16 rows read the codebook** — `lint`,
`family_sweep`, `definition_drift`, `ground_truth`, `ground_truth_wide`,
`recorded_numbers`, `locality` — and CI has no copy of it. The corpus half is
fine: `data/` is gitignored too, but `pipeline/fetch.py` re-fetches it from
Scryfall, which is what `build.yml` already does. **The codebook has no such
path: it cannot be re-fetched or regenerated, only restored.** A CI job that
ran the other 9 rows and silently skipped these would be a gate that fails
open — the shape `SESSION-START-PROCEDURE.md` Gate 3b exists to stop.

**That list is MEASURED, not grepped** — codebook moved aside, Gate 2 run, file
restored and verified byte-identical. An import-grep first predicted 8 and
named `probe_guards`, `reachability` and `object_lattice`; all three pass
without the codebook (the lattice gate's floor comes from tracked
`det-patterns-v2.json`), and `recorded_numbers` — which the grep missed —
fails. **Do not restore the 8-row statement.**

**The tension that P3-1 resolves.** *"No card data in git, ever"* is a locked
rule and assertions carry oracle-text quotes, so tracking the codebook
directly would have meant amending a first-commit rule and publishing card
text from a **public** repo. **C6 keeps that rule intact** — git carries only
hashes and metadata, never card text — which is why it was preferred over the
otherwise-more-ergonomic "just track it".

**Do not smuggle the remaining decisions through plumbing.** The architecture
is ruled and the storage foundation is proven; the *cutover* is not finished.
The four remaining candidate criteria above — readback, restore,
Gate-equivalence, corrupt-byte HALT — are preconditions, not formalities.

---

## 0AB. SEMANTIC LOCALITY IS DONE — ALL ELEVEN STEPS, INCLUDING THE BACKFILL

**→ CANONICAL RULING: `docs/B-MIGRATION-DISCOVERY.md` §11.** Tracked, and it
sits with §10's A1 — the section that defines the assertion object FL-2 amends,
and the one `experiments/foundry_codebook.py` already names as its schema
authority. §11 carries the ratification text verbatim, amendments A1–A4, the
as-built field names, and why AQ4/AQ5 stay open. **Resolves FL-2. Do NOT re-run
any of it.**

*Historical working packets, NOT the authority. **They differ in whether a
fresh clone has them at all**, which this list got wrong until 2026-08-14 —
it called all three "untracked by choice" and one of them is tracked:*

| packet | tracked? | holds |
|---|---|---|
| `SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md` | **TRACKED**, committed in `35f77b7` | measurement tables, resolution matrix, the eleven pass criteria |
| `SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md` | **untracked** | why A1–A4 |
| `THESAURUS-FACT-LAYER-ARCHITECTURE-2026-08-13.md` §8 | **untracked** | where FL-2 was raised; its recommendation was **not** what was ratified |

**Amendments A1–A4 are restated in full at §11.2 of the canonical tracked
ruling — cite that, never the review packet.** `experiments/foundry_locality.py`
cited the untracked review for them until 2026-08-14, so a Gate 2 module named
a path a fresh clone does not have; repointed there too.

*(The implementation handoff `SEMANTIC-LOCALITY-IMPLEMENTATION-HANDOFF.md` was
deleted 2026-08-13 once all eleven steps landed, per its own §9 item 4. Every
durable ruling, correction and trap it carried was moved into this section,
`CLAUDE.md`'s traps list, `docs/SESSION-START-PROCEDURE.md`, §11 above, and the
implementation files' own docstrings before it went.)*

An assertion already carried the quote that proves it. It never carried **which
part of the card** that quote came from — so the codebook knew Active Volcano
destroys a permanent **and** bounces a land, and could not know they are two
options you choose **between**. Locality is that address: one optional
`locality: [face, paragraph]` key, derived from the quote.

| | |
|---|--:|
| assertions on active axes | **7,930** |
| **addressed** by the backfill | **7,808** |
| left unaddressed, by rule | **122** |
| new DET output born addressed | `foundry_det_pass.cmd_apply` |

**THE REMAINDER IS 122, NOT 83.** The implementation handoff §6 enumerates
*"the other 83 (40 ambiguous + 4 unresolved + 39 quoteless)"* and **omits the
39 SPAN rows**, which `resolve()` equally declines to address. Span and
quoteless are both 39, which is how one got read for both. The backfill RULE
in that section — *address only where `resolve()` returns OWNER* — is correct
and unchanged; only its arithmetic complement was wrong. Re-derive with
`--report`, never quote the 83.

**What is stored and what is deliberately not:** the semantic **OWNER** only.
The evidence **span** is derived (§13), **no mode identifier** is stored
(A1 — 1,791 paragraphs hold exactly one bullet, zero hold two), and
**exclusivity is derived** from the owning header (A4).

**Unaddressed is not a defect.** An unaddressed assertion is fully valid
card-level evidence; it simply cannot prove same-unit co-occurrence. The
working sheet is `python3 experiments/foundry_locality.py --report`
(gitignored, local).

**ROLLBACK POINT for the backfill mutation**, recorded here because
`experiments/out/` is gitignored and this is the only durable place for it:
codebook `b4197e94…` → **`6aa6193f…`**, backed up under the backup law to
`experiments/out/foundry/backups/codebook.v0.7.pre-locality-backfill.20260814-015858.json`
(readback-verified at the pre-mutation sha). To revert, copy that file over
`experiments/out/foundry/codebook.json`. **The backup is per-machine** — on a
fresh clone it does not exist, and the rebuild path is
`foundry_locality_backfill.py --plan` then `--dry-run`, not a restore.

**Three things a session must not undo:**

* **Do NOT gate the write path on locality.** `foundry_det_pass` writes
  unaddressed rows on purpose — blocking a write on address coverage would
  make an unaddressable-but-valid membership unwritable, directly against the
  ratification. `write_boundary_fixtures` WB3 goes red if anyone adds that
  gate, and `--selftest` proves WB3 can fail.
* **Do NOT quote the census as storage.** They are different questions and the
  gap was measured: deleting all 7,808 stored addresses left every one of Gate
  2's 15 rows **green**, because a census computed from quotes reproduces
  itself perfectly on a file with the field stripped. `locality.stored_owned`
  and `locality.stored_mismatch` now ride the ratchet and close it.
* **Do NOT re-address.** The backfill ADDS and refuses to rewrite. Re-addressing
  after a corpus change is a different operation with a different conservation
  rule, and it is unbuilt.

**Still Captain's, untouched here:** AQ4 (the predicate row), AQ5 (`level`),
qualifier vocabulary, child effects.

**THE NEXT ARC IS THE QUALIFIER PACKET, AND ITS EVIDENCE BASE IS NOW A
COMMAND, NOT A NUMBER IN A DOCUMENT.**

```
python3 experiments/foundry_qualifier_census.py          # the report
python3 experiments/foundry_qualifier_census.py --json   # for the packet
```

**Do NOT quote 48.0%, 2,106 or ×9.2 from either census document.** Both are
superseded as sources: the census
(`FACT-GRANULARITY-CORPUS-CENSUS-2026-08-13.md`) and its verification
(`...-INDEPENDENT-VERIFICATION-2026-08-13.md`) are **untracked working
packets**, and the verification's own §V records that its code *"was run from
the session scratchpad and is not added to the repository."* A committed page
pointing at numbers nothing could re-derive is the carried-forward-count trap
aimed at the document that governs the next arc — which is why the tool exists.

**The verification's counting key was wrong, and only re-deriving it showed
that.** It deduped `(card, stem, clause)` **case-folded**, which merges
**Seize the Soul**'s spell effect (paragraph 0) with the identical clause in
its Haunt trigger (paragraph 2) — two units `foundry_locality.resolve` itself
calls AMBIGUOUS. Counting **occurrences** gives **2,110**; the three rows above
2,107 are Ugin, Eye of the Storms, Act of Authority, and Outland Liberator's
two DFC faces — every one a second real ability.

Reproduced exactly by an independently-built detector: raw yields **2,389**,
base object axes **23**, upper bound **48.6%**, `targeted-exile-creature`
**68.3%**, `targeted-destroy-artifact` **24.3%**. Live headline: **49.3% of
2,110**, expansion **×9.7**, and **54 clauses carry a CR 702 keyword
restriction** — the category the original census lacked entirely, now derived
from `load_702` rather than hand-listed. The rate is **detector-sensitive and
deliberately unpinned**; Gate 2's `qualifier_census` row protects the
REPRODUCIBILITY, not the number.

**Two false negatives the tool found in its own first draft**, both of which
the residual method makes visible and a category-regex cannot: a **CR 205.3
subtype is not a base class** (`destroy target Wall` lands on
`targeted-destroy-creature`, which does not encode Wall — 60 clauses), and
**`another target creature`** sits in the lattice's `_TARGET_HEAD`, outside the
tail a residual method reads (58 clauses, 26 otherwise unqualified). `up to N`
is cardinality, not eligibility, and is deliberately not counted.

---

## 0AA. THE OBJECT LATTICE IS BUILT AND WAITING ON ONE RATIFICATION

**→ `docs/OBJECT-LATTICE-2026-08-09.md`. Read it before §0Z.**

Captain, 2026-08-09: *"it was weeks ago I said that cards that destroy multiple
things need a one rule instance of each object it destroys. Like the card
Putrefy."* **Correct, ratified in batch 6, and never applied to a single card.**

`MASTER-HANDOFF-ADDENDUM-4.md` §4: *"**M8 generalized (b6 D3)** | Multi-class
`targeted-<action>` cards get every applicable per-class tag, all action verbs,
**never combo tags**."* Measured before this work: **0 cards** in the codebook
carried two class siblings of one action family. Putrefy carried only
`rule:prevents-regeneration` — the rider, not the spell.

**The class axes need NO ratification.** `b6 §11.2`: *"Captain ratifies
GRAMMARS (stem + closed facet slots); **virtual nodes instantiate on first
quote-verified member, no fresh ratification**."* The decision sheet brought on
`targeted-destroy-creature` was asking Captain to re-ratify one node of a
grammar already ratified whole.

**Built: `experiments/foundry_object_lattice.py`.** All vocabulary derived at
run time — CR 701.8a (only permanents are destroyed), CR 110.4 (the six
permanent types), CR 205.3g–q subtype→type consumed from
`foundry_cr702_classes`, CR 110.1 (`<type> card` is not a permanent), every
emitted class asserted against grammar §5's `OBJECT_VOCAB`.

| | |
|---|--:|
| memberships across destroy · exile · bounce | **2,653** |
| the same three families in the codebook today | **267** |
| multi-class cards — the population M8 is about | **440** (was 0) |
| **cards carrying no derived tag today that gain one** | **1,637** |
| **coverage** | 19.3% → **24.3%** |

Cost **$0.00**, re-runnable, `rule-derived` rather than `llm`. For scale the
whole 15,371-row consolidation plan (a $57.63 LLM pass) reaches 48.0%.

**✅ RATIFIED 2026-08-13 — and the first ratification was on a DEFECTIVE
sheet. → `docs/OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md`.**
Captain's card-by-card review found **7 correct memberships missing** from the
2026-08-12 output. They were regressions from that same commit, which removed
**170** memberships, verified **83**, and shipped the other **87** unread.
Repaired at the grammar level (CR 608.2c · CR 601.2c · CR 110.1 at arm level),
corpus-wide diff **+7 / −0**, re-ratified against the repaired sheet.
`det-patterns-v2.json`'s lattice row now reads `corpus_hits: 2499`.

**A 12-ROW SAMPLE OF WHAT WAS PRODUCED CANNOT SEE A MEMBERSHIP THAT IS
MISSING**, which is why three protections ship with the ratification:
`foundry_object_lattice.py --gate` (Gate 2 row 14) runs the grammar-shape
fixtures, the **independent** residual invariant, the **tracked membership
floor**, and a per-class ratchet. Both the invariant and the floor are
preconditions of the write, asserted by
`foundry_det_pass.assert_lattice_invariant` on both phases.

**THE FLOOR IS THE TRACKED NUMBER, NOT THE PINNED ONE — audited 2026-08-13.**
`experiments/out/` is gitignored, so `audit-baseline.json` is per-machine and
`report()` returns 0 on an unpinned section: a fresh clone printed
`object lattice gate GREEN` having compared nothing, and `det_pass apply` never
consulted it. The floor is therefore re-derived from
`det-patterns-v2.json`'s ratified `corpus_hits` (2,499), the way
`foundry_recorded_numbers.py` re-derives grammar §2's counts. **It is
DIRECTIONAL, not an equality invariant** — `corpus_hits` is a measurement at
probe time (3 ratified patterns have already drifted from theirs with Gate 2
green; the sibling field is named `codebook_n_members_at_probe`), so a FALL is
fatal and a RISE is reported, and normal corpus growth does not turn the gate
red. The per-class ratchet is kept as a **local diagnostic**.
**Known open gap:** a compensating −7/+7 redistribution nets zero, so on a
fresh unpinned environment nothing fires. Detail and why it was not closed:
`OBJECT-LATTICE-RESIDUAL-RULING-2026-08-13.md` §8a–§8c. **Still Captain's, and NOT decided here:** controller/ownership
scope, and any `targeted-destroy-token` family.

The sheet is written:
`experiments/out/foundry/object_lattice_samples.{json,md}`
(regenerate: `python3 experiments/foundry_object_lattice.py --report 12`).
**That sheet caught a real defect on its first run** — Auriok Salvagers,
*"Return target artifact card from your graveyard"*, claimed for bounce; CR
110.1 fixed it and `destroy` did not move by one row, which is what confirmed
the rule.

Then one structural change: `det-patterns-v2.json` is `slug` + one regex → one
axis, and a lattice pattern is one matcher → **N axes at match time**. Schema +
`foundry_det_pass.py`, not a new JSON row.

**Findings that fall out, in `OBJECT-LATTICE-2026-08-09.md` §4 and §6:**

* **3 of the consolidation plan's 87 new axes are combo tags M8 forbids by
  name** — `targeted-exile-artifact-or-creature`, `-artifact-or-enchantment`,
  `targeted-bounce-artifact-or-enchantment`. Dossiered: no ruling anywhere. The
  nine `activated-tap-or-untap-*` are **not** this (b6 D2 ratified that grammar;
  the OR is between verbs, not object classes).
* **2,923 redirect rows in the plan create no membership.** The lattice
  re-derives the destroy ones from the corpus, but
  `combat-trick-pump-creature-you-control` (375) and
  `replacement-enters-with-counters` (318) are not lattice cases and still tag
  nothing. Whether a rename redirect should mint a membership is a real ruling.
* **Grammar §5 line 651 still spells the lattice `targeted-destruction-<class>`**
  and `grammars.json`'s action facet still carries `"destruction"` with
  `"destroy"` absent. Now load-bearing — G4 generator fix.
* Unruled, reported not decided: CR 300.2 conjunctive targets (*"artifact
  creature"*, one object, two types) and *"destroy target token"* (CR 111, no
  ratified OBJECT token).

---

## 0Z. READ THIS BEFORE §2 — THE WORK QUEUE CHANGED

**→ `docs/PRODUCT-REALITY-AUDIT-2026-08-09.md`.** Captain asked whether the
work actually serves the tool. Measured answer: **the T3 foundry is not
connected to the product.** `tier_engine.py` reads no foundry output at all and
emits one self-derived `rule:` tag; all 13 importers of the delivery classifier
are audits. **19.3% of the corpus carries any derived tag.** 204 commits since
2026-08-01 touched `pipeline/` zero times.

**W4 is PAUSED — do not take §2A.** The ordered queue is now:

1. ~~**Wire the codebook into `tier_engine`**~~ — **MEASURED 2026-08-09, DO NOT
   RE-RUN. → `docs/WIRE-RESULT-2026-08-09.md`.** The join was built offline and
   graded against predictions committed before it existed. **It does not land:
   1 of 3 criteria passed.** The join is a re-rank by codebook MEMBERSHIP —
   across 33 hand-named correct neighbours, **every one on its axis was
   promoted and every one not on it was demoted, no exceptions**. Axis recall
   against those families is **13/33 = 39%**, and the one axis at 100% recall
   produced **zero** movement because its members already share verbatim text
   and the engine reaches them at Tier 2 for free. Re-run it after coverage
   moves: `python3 experiments/foundry_wire_experiment.py --json`.
2. ~~**Unblock `A15-VOCAB-01`**~~ — **BOTH HALVES LANDED 2026-08-09. →
   `docs/A15-VOCAB-01-RULING-2026-08-09.md`.** It was never ONE decision and
   never a vocabulary question. The **21-row `except` half was a transcription
   bug** in `validate_slug` against grammar §13 Q8.5 (ratified 2026-07-31),
   fixed by PARSING the ratified line; four guards negative-controlled. The
   **188-row `destruction` half completed a rename Captain ratified and the
   project executed on a sibling 2026-08-02** (§6c line 838) and stopped
   halfway: `rule:targeted-destruction` → **`rule:targeted-destroy`**, 172
   members, Captain-ratified and executed under the backup law.
   **`STOPPED_FOR_CAPTAIN` is cleared — the 18,059-row pass is ratified to
   proceed and has NOT been run yet.** That is the next action.

   **The rename ended a CHECK-EVASION, and this is the transferable lesson:**
   `definition_drift`'s C3 keys on grammar §4 EFFECT verbs, so an axis spelled
   with a non-§4 word is invisible to it **by construction**. Renaming put 172
   members into C3's scope for the first time — 171 pass, and **Audacious Swap
   is a genuine defect** (*"shuffles it into their library"* — a tuck, not a
   destroy). Gate 2 going RED after a mutation is the drill working.

   **R5 IS ATTRIBUTED AND 2a NOW COMPLETES — → ruling doc §9.**
   `experiments/foundry_r5_attribution.py` replays `classify_r5` over every
   codebook backup. R5 141 → 163 is **eight ratified mutations**, every delta
   closing, every entering row a correct promotion. The harness is provably
   faithful: at the classification's own recorded inputs it reproduces
   **R5 = 141 exactly**.

   **But `EXPECTED_A15_ROWS = 213` NEVER REPRODUCED.** Same replay, producer
   checked out at both `cfc26fa` and `f09fe73`, gives **194** every time while
   R5 gives 141 in the same run. One cluster carries it all —
   `cant-be-blocked-except-by-count`, recorded 21 rows, reproducible 2. So
   A15-VOCAB-01's "209 blocked" reproduces as **190**, and CDR-02's "21-row
   grab bag" analysis rests on rows that do not reproduce. **Cause is not among
   the four recorded inputs** — unresolved, and stated as such.

   **`STOPPED_FOR_CAPTAIN` is a HARDCODED literal**, not a computed flag. The
   audit page and CLAUDE.md §0 read it as proof the pass is blocked; it is
   `true` with zero blockers. The real signal is `blocking_decisions` — **now
   empty**.

   **2a completed**, determinism ×2, old artifact preserved as
   `...PRE-A15-RULING-20260809.json`. New contract: **0 blocked, 194 promoted,
   15,371 rows for 2b** (was 18,059); routing 2 → 2,925, attributed to
   `merged_slug_codebook_hits` 0 → 2,926 as renamed axes went 45 → 108.

   **2b IS RUN — the plan exists. → ruling doc §10.** The expander did not
   exist (the directive says "commit the expander script"; nothing did);
   `experiments/foundry_consolidate_run1_enumerate.py` is it. Zero mutation,
   one artifact, determinism ×2.

   **plan sha256 `b545d2bf2fbd9245950c9038c911d7f2ba01355d67c3c8c3736bf8a6f9e90188`**
   — 13,565 member additions + 1,806 assertion merges = **15,371**, exactly
   2a's `total_enumerated_rows`; 87 new axes. Every gate passed, including 2a's
   `expected_counts` reproducing exactly in all ten categories.

   **Applying it would take coverage 19.3% → 48.0% (+9,351 cards) and the
   median axis size 4 → 10** — the direct answer to `WIRE-RESULT`'s "39% axis
   recall, median axis 4". Re-run `foundry_wire_experiment.py` after an apply;
   the predictions are already committed.

   **⛔ SESSION 3 RAN AND HALTED — THE PLAN IS UNAPPLIABLE. →
   `docs/CONSOLIDATION-APPLY-HALT-2026-08-09.md`.** The applier
   (`experiments/foundry_consolidate_run1_apply.py`) was built and stopped the
   plan on its own pre-mutation verifier. **Nothing was written** — codebook
   still `b4197e94…`, plan still `b545d2bf…`, no backup consumed.

   **189 of the 13,565 member additions target 2 axes the plan never
   creates**: `rule:targeted-destroy-creature` (188) and
   `rule:activated-tap-opponent-artifact` (1). Both are A15 clusters 2a
   classified `instantiate`; 2b's `expand()` step 3 builds their member rows
   and never adds the axis, because `new_axes` is fed only by
   `classify_nodes()`. **All five 2b gates passed** — `gate_counts` compares
   `new_axes_instantiated` against 2a's expectation and **both sides count
   only the node route**, so the closed loop closed on a quantity computed the
   same wrong way twice. 403+87=490 and 8,982+13,565=22,547 are each correct
   and jointly impossible.

   **Fixed in the producer:** `gate_every_row_has_an_axis()` now halts a
   regeneration rather than emitting an unappliable plan. It halts instead of
   instantiating because an axis record needs a definition and a scope, and
   2a's `a15_cluster_summary` carries neither.

   **The rest of the plan is clean, and that was measured** — the whole
   verifier re-run against a patched copy: 15,371/15,371 rows correct,
   15,371/15,371 quotes verbatim, R5 163 + A15 194 promotions folded with lane
   fields intact. **One defect, not the first of a queue.**

   **NEXT IS CAPTAIN'S, not a work item:** two axis records to ratify
   (decision sheet, halt doc §3, with proposed definitions and the measured
   35-card overlap with `rule:targeted-destroy`). Then regenerate — **the plan
   sha changes, which voids the current go** — then `--dry-run`, then
   `--go-sha256 <new hash>`. Note `grammars.json` names
   `targeted-destruction-creature` a lattice candidate *"once member evidence
   is checked … do not auto-rename"*, which is exactly the auto-route 2b took.

   **← SUPERSEDED PREFLIGHT (ruling doc §11), kept for what it still gets
   right.** Two things a session must not rediscover: the governing
   directive is at **`docs/archive/CONSOLIDATION-APPLY-DIRECTIVE.md`** (the 2b
   directive cites a path that does not exist) and it carries a **stale count —
   "the 93 instantiations", live number 87**; and **the applier does not
   exist**, so session 3 is build + run, with a restore drill, a 500-row
   fixed-seed spot verifier, determinism ×2 by applying twice from backup, and
   four companion artifacts. The codebook grows **2.5× in one mutation**
   (8,982 → 22,547 member rows, 403 → 490 axes). Both directives end "one
   session, this work item only."

3. **Revive `foundry_review.html`** — dark since 2026-07-17.
4. **A green pipeline build** — last one 2026-07-05.

**Three findings the wire experiment produced that no foundry session could
have** (all in `WIRE-RESULT-2026-08-09.md`):

* **A codebook membership defect**: `rule:reanimate-from-graveyard` holds
  **Animate Dead** and **not Dance of the Dead**, its Aura-template twin. The
  wire promoted one to #2 and buried the other at #56. No Gate 2 check can see
  this.
* **A live `tier_engine` bug, unrelated to the codebook**: Rampant Growth's
  displayed top-10 is **an alphabetical slice of a 44-row score tie**. Tier 3
  sorts `(-score, name)`, so with one distinct score in the head the product
  ships the alphabet. A tie-break is a ratified-constant question for Captain.
* **88 Alchemy (`A-`) memberships across 51 active axes, 48 of them duplicate
  pairs with their own paper twin.** They inflate every axis DF — which feeds
  `idf` *and* the 172 `DERIVED_QUALIFY_DF_CEILING` — and duplicate displayed
  rows, against the ratified *"paper rows preferred over A- variants"*.

**Audit §10 is BUILT: `experiments/foundry_reachability.py`, Gate 2 row 13.**
It parses the shipped entry points out of `.github/workflows/`, walks their
import closure, and reports how many foundry artifacts reach a shipped card.
**0 of 5**, every session, until that changes.

Everything below this section is still ACCURATE; it is the queue's PRIORITY
that changed, not its facts.

---

## 0. THE ONE-LINE STATE

W1, W2 and W3's DET half are DONE. D1/D4/D5/D6/D7 landed 2026-08-08; **all five
D8a items landed 2026-08-09**. D2/D3 was WITHDRAWN; D8b stays blocked behind it.
§2 is **64 tokens**; `unclassified-trigger` is **481**.

**2026-08-09 also rebuilt the safety net and then used it.** Gate 2 is **one
command, 12 rows, every one negative-controlled** (`foundry_gate2.py`).
Positive correctness went **488 → 1,248 graded assertions**. Two gates that
could not fail now can.

**THE CODEBOOK WAS MUTATED — 403 active axes / 8,810 members** (was 565/8,740),
across three Captain-authorised specs under the backup law: one quote repair,
44 new axes re-homing the `--wide` residual, and the 5-axis `etb` → `replacement-
enters-…` rename. Every one backed up, dry-run, determinism ×2, conservation
checked.

**Canonical current handoff: `docs/SESSION-HANDOFF-2026-08-09.md`.**
This file does not replace it — it tells you what to do FIRST and why.

---

## 0a. THE CR REFRESH IS DONE — **→ `docs/CR-REFRESH-2026-08-09.md`**

Landed 2026-08-09 (`2733326`, `675a58b`). The pipeline reads the **2026-08-07**
edition through one normalizing loader (`experiments/foundry_cr.py`); the file
itself is untouched, and it is **tracked in this repo now** rather than reached
across into the site's gitignored `docs/`.

**0 of 61,383 ability lines moved.** Two numbers did, both real WotC changes:
CR 702 keyword names **193 → 194** and keyword homes **150 → 151**, from the new
CR 702.195 **Storied**. Everything else on the acceptance test reproduced
exactly.

**Do not re-derive any of this.** Three things worth carrying:

* **The mana rule is CR 605.1a** and it has **no code path here**. CR 106.4 /
  106.6 / 106.12 are byte-identical across editions, so nothing mana-related
  moved. `CR-REFRESH-MANA-ABILITIES.md` is resolved.
* **The CR-LAG register did NOT shrink.** `chorus` and `N or less` both said
  "the real fix is to refresh the snapshot"; the refresh happened and fixed
  neither. Both comments are corrected in place — the CR is behind the printed
  cards, not the snapshot behind the CR.
* **`MTJ_CR_PATH=<file>` runs the whole pipeline against another edition.** That
  is how the loader was proven a no-op on the June CR before the diff was
  believed, and it is how the next refresh should be verified.

**Two items are on Captain's sheet** (§4): the new file's encoding damage in
CR 206.3a, and whether CR 605.1a needs modelling. Neither blocks anything.

---

## 1. DO THIS FIRST — read the audit's result, do NOT re-run it

**The audit the previous version of this file demanded HAS BEEN RUN.**
2026-08-09, commit `2bcaeb6`. Do not re-derive it; the result is in
`SESSION-HANDOFF-2026-08-09.md` §2 and here in one line:

> All 280 lines of the six 2026-08-08 tokens were read against their CR rules.
> **Five of six are clean.** `draw-trigger` was 69/71, and the two bad ones —
> plus **two more the token-scoped audit could not see** — were fixed.

**What it left behind, and this is the part that matters:**

`foundry_ground_truth.py` asserts **0 of 6**, and the reason is structural,
not specific to those six. **13 of 16 move specs carry ZERO seeds**, so the
whole codebook — 8,740 members — is graded through a fixture of 534 drawn
from three specs / 15 axes. **Every token ratified since 2026-08-04 sits
outside the only positive-correctness check in the repo.**

Widening the fixture is cheap, unstarted, and is §6C of the handoff.

**Do not read "5 of 6 clean" as "the tokens are verified."** It means they
were read once by a session. That is strictly better than the diff, which
scores `None → ratified` as pure profit, and strictly worse than a fixture.

---

## 2. THEN — the next work item

> **⛔ SUPERSEDED BY §0Z.** Both items below are shape/vocabulary work inside
> the foundry, and the foundry does not reach a shipped card. They are kept
> because they are correctly scoped and will matter **after** the codebook is
> wired into `tier_engine` — not before. Do not start either without saying out
> loud which shipped artifact changes.

**The CR refresh is done (§0a). Both items below are ready and unblocked —
and both are PAUSED pending §0Z.**

**A. W4 — the static queue · 3,358 lines · the big slice. TWO SHAPES DONE.**
The **anthem** (`<subject> get ±N/±N`, **524**) and the **keyword grant**
(`<subject> have <CR 702 keywords>`, **488**) both landed 2026-08-09 with
**0 re-routes** — `docs/W4-ANTHEM-2026-08-09.md` and
`docs/W4-KEYWORD-GRANT-2026-08-09.md`. **Read the second one's §9 first**; it
ranks what is left, and **CR 601.2f cost reduction (~498) is next**.
`python3 experiments/foundry_shape_extractor.py --gaps`, section headed
`INSIDE spell-or-static`. Named shapes, one at a time,
never a blanket sweep — the warning was re-measured 2026-08-09 and the 1,883 is
still **4** (`experiments/foundry_blanket_risk.py`), all four the Siege cycle
behaving correctly.

**B. The 481-line residual.** `python3 experiments/foundry_w3_census.py`
partitions it by the CR rule that decides it and mints nothing. Ranked by
DECK-BUILDING RELEVANCE (Captain's ratified criterion — a queue sorted by line
count applies the one the rule names as wrong):

1. **`fully unlock a Room`** — CR 709.5i — 17. The case is already written
   (handoff §5d); it needs Captain, not analysis.
2. **plays-a-card** — CR 601.1a / 305.1 — 16.
3. **ring-tempts** — CR 701.54 — 8.
4. counter-placed / -removed — 122.6 / §8b — 38. **Check §8b first**, it may
   already govern these.

**The recipe, proven ten times now:** Gate 3 the name you are about to WRITE →
§2 table row with the CR quoted → wire the emitter → routing diff
`--strict --lines` and READ EVERY MOVED LINE → the four audits → re-pin the
baseline only onto improvement, and only with the reason stated.

---

## 3. DO NOT DO — and why, so it is not rediscovered

**D8b — monstrosity (19) · level-up (13) · attach (12) · phasing (7) ·
dungeon (4).** These five **are CR 701/702 keyword terms**, so they belong to
the WITHDRAWN D2/D3 question. Minting them one at a time is design goal #1's
duplication or a back-door ratification.

**D2/D3 as a blanket grammar family.** Built exactly as ratified and it
**admitted 251 tokens** — including `defender-trigger` (a word §6 bans) and
`kicker-trigger` (retired by §2g). "Every CR 702 keyword" is parsed from the
CR at run time and is *still* a hand-list in disguise, because most CR 702
keywords are STATIC abilities that never happen. **The replacement is an
EXPLICIT member list of the ~41 attested terms — a ratification.**

**Widening `door-unlocked-trigger` to cover `fully unlock`.** CR 709.5i is a
different event — the SECOND door, on ANY Room. §6b rule 1 forbids the fold by
name. It is a ratification, not a regex change.

**Adding `lose` to the compound splitter's `PREDICATE` list.** Measured: it
makes the `gain or lose life` defect WORSE, not better. Handoff §5b has the
diagnosis; it needs a shared-object re-join, not a list entry.

---

## 4. CARRIED FORWARD — still open

- **13 memberships on `rule:grants-trample-to-creatures-with-counters`
  contradict the axis's own definition.** The axis claims the card *grants*
  trample to counter-bearing creatures; Avatar of the Resolute prints
  `Reach, trample` and simply **has** it, as does Bioessence Hydra. Found by
  locality analysis 2026-08-13 and **routed, not fixed** — locality does not
  certify semantic correctness (§11 of `B-MIGRATION-DISCOVERY.md`), so this
  belongs to `foundry_definition_drift` / a membership ruling.
  **No live gate reports it:** `definition_drift` returns zero matches on this
  axis today, so the only thing keeping it visible is this line. Surfaced here
  2026-08-13 because it previously existed **only** in two untracked packets.
- **W8, Captain's sheet — now fourteen items.** The ten standing ones, plus
  CR 709.5i, the shared-object splitter, and the two from the CR refresh
  (`docs/CR-REFRESH-2026-08-09.md` §DECISION SHEET): **D-CR-1 is RULED and
  LANDED** — Captain 2026-08-09, repair the 7 mojibake characters in CR 206.3a
  at read time; CR 206.3a is now byte-identical to the 2026-06-19 edition and
  0 lines moved. **D-CR-2** whether "is a mana ability" (CR 605.1a) needs
  modelling at all is open — recommendation is no.
- **117 single-faced instants/sorceries routing to `replacement`** — the
  branch has no spell-face gate. Needs a per-FACE cut; real design.
- **10 `it becomes day AS THIS CREATURE ENTERS` lines** — CR 614.1c
  replacements, found while landing D8a item 2, unrouted, logged not started.
- **W5** `escapes with` (12) · **W6** family sweep (the standing 6, now a
  machine record: `docs/family-sweep-known-debt.json`; **retire a row there in
  the same commit that fixes it**, or the gate goes red on the stale waiver) ·
  **W7** definition drift (the standing 35).
- **W9 parent layer** is blocked on W8; **W10 display** on W9.

---

## 5. THE FOUR THINGS MOST LIKELY TO BITE

1. **A TOKEN-SCOPED AUDIT IS BLIND TO ITS OWN NEIGHBOURS.** Reading all 280
   lines of the six tokens found 2 defects; the routing diff on the fix found
   **4**. The other two had the identical cause and a token outside the audit's
   scope. Read the population, then run the diff and read that too.
2. **A SPECIFICATION IS A CARRIED-FORWARD COUNT WITH A CR NUMBER ATTACHED.**
   All five D8a items had a defective spec — three wrong counts, one wrong CR
   rule (728 is Rad Counters; day–night is 731), one hidden second CR rule.
   Re-measure the anchor and the partition, not just the number.
3. **A row-level loss on a ROUTED line is invisible to `diff --strict`.**
   Watch `deliveries` and `descriptor_unrouted.*`, never `unrouted_lines`.
4. **A probe defect is the default outcome.** Nineteen across five sessions,
   including one this session that under-counted by requiring a line to start
   with `when` — and so lost an ability-word prefix and a compound.

---

## 6. THE PROMPT — paste this to restart

```
Follow docs/SESSION-START-PROCEDURE.md, then read docs/PICK-UP-HERE.md and
docs/SESSION-HANDOFF-2026-08-09.md.

Do NOT re-run the six-token audit — §1 says it is done and what it left.
Do NOT re-do the CR refresh — §0a says it is done and what it moved.

Take a work item from §2: W4 (the anthem group) or the 481-line residual.

Standing rules apply: Gate 2 is `python3 experiments/foundry_gate2.py`, read
every moved line in every routing diff, re-pin a baseline only onto improvement
and only with the reason stated, back up before any codebook mutation, and use
`import foundry_probe as p` for anything that measures. Commit as you go.
```
