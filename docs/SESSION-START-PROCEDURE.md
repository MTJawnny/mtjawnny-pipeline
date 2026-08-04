# SESSION-START PROCEDURE

**Read this before the handoff, not after.** It is short on purpose: a long
procedure does not get followed.

## The failure this prevents

Captain's finding, 2026-08-02: *"Every drift has been due to a session not
having enough context."* Every instance has the same shape:

> A session writes a check against **one** law, unaware of a **different**
> ratified law governing the same slug — and reports a settled question as a
> defect.

Measured cost of that shape: the CDR-09 derivation knew grammar §8a alone and
returned three false defects, **two of which would have destroyed
Captain-ratified names**. The tier-3 re-audit nearly re-raised all three again.

## Why "just grep the docs" is not enough

That was the standing rule, and it is necessary but **provably insufficient**.
Measured 2026-08-02 across 328 active axes:

| | |
|---|--:|
| active axes carrying a ruling on a law-bearing document | **291 (88%)** |
| active axes whose rulings are filed under a **former name** | **77 (23%)** |

For those 77, grepping the current slug returns nothing while a KEEP/MERGE
verdict sits in a batch document under a name the axis had two renames ago.
`rule:activated-plus1-counter-transfer-to-other-creature` is the worked case:
batch-5 ruled KEEP on it under `activated-counter-transfer-from-other-creature`,
and no grep of the live name finds that.

`RATIFIED-RULINGS-REGISTRY.md` does not close the gap either — it is keyed on
ruling IDs (`D12`, `CDR-09`, `A15`), not on slugs.

---

## The procedure

### Gate 1 — load the reading manifest (always)

**Current handoff: `docs/SESSION-HANDOFF-2026-08-03-EVE.md`.** ← this line is
the pointer; update it when you write a new handoff.

**Do not pick the handoff by filename sort.** `-EVE` and `-PM` sort *before*
the bare-date file, so "newest `SESSION-HANDOFF-*.md`" selects the oldest
same-day file. Every superseded handoff now carries a banner pointing forward,
so if you landed on one of those, follow its banner. `ls -t` also works.

Read the current handoff and follow its READING MANIFEST.
Read `docs/CODEBOOK-NAMING-GRAMMAR.md` **whole** — not the section that looks
relevant. Three separate errors on 2026-08-02 came from reading one section
while §7, §12a or a batch ruling governed the same slug.

### Gate 2 — verify live state, never recall it (always)

```
python3 experiments/foundry_codebook.py lint
python3 experiments/foundry_family_sweep.py --strict
python3 experiments/foundry_definition_drift.py
python3 experiments/foundry_ruling_registry.py
```

Handoff numbers lag. Every hand-written number checked across two sessions on
2026-08-02 was wrong in at least one direction — including the tier-3 scope
("22 axes / 66 reads"; live generation returned 23 / 69). If a handoff number
and a measured number disagree, **the measurement wins and the handoff gets
corrected.**

### Gate 3 — DOSSIER BEFORE VERDICT (the new one, and the one that matters)

**Before calling any axis, slug or member defective — before writing the
finding, not after:**

```
python3 experiments/foundry_slug_dossier.py <slug>
```

It walks the codebook's own rename history, greps **every name the axis has
ever had** across `docs/` and `docs/archive/`, and separates lines that carry a
ruling from ordinary prose. It judges nothing.

If it prints **⚠ THIS SLUG IS RULED**, you are not looking at a defect until
you have read every line it listed and can say which ruling your finding
overturns and why.

For gating a script or a batch pass, `--strict` exits 1 on any ruled slug.

### Gate 4 — when your check disagrees with a ratified list, suspect the check

This is not humility, it is the measured base rate. On 2026-08-02 a
conformance checker disagreed with a ratified list **four times** and was wrong
**four times**. The same session's §S4 measurement was wrong twice in a row —
154, then 90, before landing at 44 — each time because the classifier's
boundary was wrong, not the data.

State the number you measured, the boundary you drew, and why a different
boundary gives a different number. A finding without its boundary stated is
not reportable.

### Gate 5 — read full oracle text, all faces, every time

Three confident findings on 2026-08-02 were false because only the first ~150
characters were read. The all-faces rule is what caught Kytheon (a DFC whose
*back* face made the membership correct).

---

## Standing discipline (unchanged, restated because it is cheap to restate)

- **Nothing is committed without Captain's explicit ask.**
- **Halt loudly.** Never guess, never silently skip.
- **Backup law**: timestamped backup to `experiments/out/foundry/backups/`,
  verified by readback, before every codebook mutation.
- **Determinism ×2** byte-identical on every generated artifact.
- **Evidence must prove ITS OWN axis.** A quote proving the ability does not
  automatically prove every axis that ability satisfies.
- **New vocabulary is a ratification, not a typo fix.**
- **Generated artifacts get generator fixes** (G4), never hand edits.

## What this procedure does NOT solve

Gate 3 finds rulings that exist **in `docs/`**. A ruling made in chat and never
written down is unreachable by any tool. That is the residual risk, and the
only mitigation is the existing one: rulings get written into a document in the
same session they are made.

The deeper constraint is unchanged and is not a context problem:
**ratification throughput is the bottleneck.** Two sessions on 2026-08-02
generated more findings than could be ruled on. `experiments/foundry_review.html`
has been dark since 2026-07-17 and reviving it remains the highest-leverage
unstarted work.
