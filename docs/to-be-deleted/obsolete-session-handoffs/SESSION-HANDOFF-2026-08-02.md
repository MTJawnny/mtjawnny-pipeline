# SESSION HANDOFF — 2026-08-02

> ⚠ **SUPERSEDED — this is NOT current state.**
> The current handoff is **`docs/SESSION-HANDOFF-2026-08-02-EVE.md`**.
> Start at **`docs/SESSION-START-PROCEDURE.md`**.
> (Filename sort is misleading: `-EVE` and `-PM` sort BEFORE the
> bare-date file, so "newest by name" picks the wrong one. Follow
> this pointer, not the sort.)

Written to be read COLD. This file supersedes `SESSION-HANDOFF-2026-08-01.md`
for current state; that file remains accurate as the record of the B-migration
arc and is still worth reading for §3's mirror-drift analysis.

**Session spend: $0.00. Cumulative arc: $90.51. Headroom vs the $140 ceiling:
$49.49.** Zero API calls. One Fable 5 subagent was launched and died on
usage credits without producing a deliverable — Captain has ruled out further
Fable 5 spend, so analysis is done in-house from here.

**codebook.json was NOT mutated this session.** sha256 still
`61af1a1d7f81504f422feb4d…`, identical to session start.

---

## 1. Where the system is, in one paragraph

The failure surface moved again, and this time it moved *off* the codebook
entirely. `codebook.json` is untouched and healthy. What was broken was the
**documentation layer**: twelve load-bearing documents — including the foundry
spec that eight scripts cite as their authority — lived in a gitignored
directory in the *other* repo with no version history in either. One of them,
the triage protocol the `/triage-*` skills actually load, had silently lost
five ratified standing rules for six weeks. All of that is now fixed, tracked,
and gated. Four of five Tier-0 code bugs are fixed; the fifth is measured and
correctly blocked. **The next work item is the §12a rename walk — the first
codebook mutation in days.**

**Live state, all measured at session end:**

| | |
|---|---|
| codebook | `foundry-codebook/2` v0.7 · 455 records · **307 active** · 7,699 members · lint clean |
| sha256 | `61af1a1d7f81504f422feb4d…` (unchanged this session) |
| family sweep | 196 findings, **6 blocking** · `--strict` exits 1 |
| ruling registry | 123 distinct rulings · 49 sole-homed · 14 docs deletion-blocked |
| docs | 36 live · 16 archived |
| spend | $90.51 / $140 |

---

## 2. The next work item: the §12a rename walk

**Ratified and ready. Nothing blocks it.** Full specification in
`docs/CODEBOOK-NAMING-GRAMMAR.md` §12a; the rule it enforces is §8a.

16 renames, name-only — members and definitions unchanged:

- **3 verb-side** — singular `counter` in verb sense, banned by §8a rule 1
- **10 noun-side** — each gains `plus1-`; every one of their definitions
  already says +1/+1, verified against the definition text
- **3 `any-`** — the type-agnostic axes Captain ruled on

Arithmetic check that must still hold: **16 renames + 17 already-conforming =
33 counter-bearing active axes.**

### Preconditions — derive these fresh, do not trust this file

This is the session's first codebook mutation. Before touching anything:

1. `python3 experiments/foundry_codebook.py lint` → clean
2. `python3 experiments/foundry_family_sweep.py --strict` → record the
   blocking count *before*
3. **Backup law**: write a timestamped backup to
   `experiments/out/foundry/backups/` and **verify it by readback**.
   `codebook.json` is gitignored — that directory is the only rollback path.
4. Re-derive the 16 renames from live state rather than pasting §12a's list.
   If the live set disagrees with §12a, **halt** — do not reconcile silently.

### After

Determinism ×2 byte-identical · lint clean · sweep re-run · exact-count
report · `git` the grammar and any doc changes (the codebook itself is
gitignored).

### What the walk unblocks

- **ADD-08 / Tier-0 bug 4** — measured this session: the adjacency rule
  misfiles **17 of 33** counter axes on current names, **4** after the walk.
  See §3 below; the rule itself needs two corrections *as well*.
- **CDR-13's Homograph Form Ledger** — its "zero new churn" claim rests
  entirely on these renames existing.

---

## 3. Decisions still waiting on Captain

**Newly surfaced this session, never previously put in front of you:**

- **6 family rulings** — `docs/FAMILY-TREE-EVIDENCE.md`. Five proposed
  families (cast-interference, resolution-protection,
  activation-interference, combat-prohibition, tax-effects), each with
  measured corpus co-occurrence, a mandatory counter-argument, exemplar and
  near-miss panels, and one yes/no question. This document was written to
  solicit exactly these rulings and has been sitting unread in the other
  repo.
- **S1–S7 structural rulings + T1/T2 open tensions** —
  `docs/PARENT-TREE-CANDIDATES.md`. These gate CDR-02, CDR-05 and CDR-06,
  all three of which Captain parked pending them.

**Carried forward from `CDR-PROPOSALS.md`:** CDR-01, 03, 05, 07, 08, 10, 11,
12, 13 are RULED. **CDR-09 is RULED and recorded** (grammar §8a + §12a).
CDR-02, CDR-04, CDR-06 remain parked for discussion.

**Two corrections to the ADD-08 rule** (measured, recorded in grammar §8a) —
the adjacency rule as specified in `CR-VOCABULARY-AUDIT.md` §4 is incomplete:

1. it must look **past SCOPE tokens** when hunting the object — in
   `counters-target-spell` the next token is `target`, not `spell`
2. **left type-binding must outrank right object-adjacency** —
   `cast-trigger-self-plus1-counter-noncreature-spell` is noun sense but has
   a type word left and an object right

---

## 4. What shipped this session (13 commits)

| commit | what |
|---|---|
| `c45ebee` | 12 load-bearing docs brought under version control (3,935 lines) |
| `25613c6` | **restored 5 ratified standing rules** lost from the live triage protocol |
| `427f3e5` | **CDR-09 ratified** — grammar §8a + the §12a walk, logged not executed |
| `601f330` | ruling registry — a provable deletion gate |
| `f62a2e5` `1d1c84b` `019df5f` `f617f15` | 16 docs archived; site repo cleaned and restored |
| `4d37841` | Tier-0 bug 1 — `load_axis_patterns()` halts on orphans |
| `f09fe73` | Tier-0 bug 2 — 2a existence test uses canonical form |
| `89548bf` | Tier-0 bug 3 — guard against CARDNAME-token-blind patterns |
| `d9ef6e8` | Tier-0 bug 5 — renamed the lying count, added a shrink alarm |
| `7a688ef` | ADD-08's dependency measured; bug 4 confirmed blocked |

### New standing gates

- **`experiments/foundry_ruling_registry.py`** — harvests every ratified-ruling
  reference in `docs/`. **No document may be deleted while it is the sole home
  of any ruling.** `--check <doc>` exits 0/1 on exactly that.
- **`foundry_family_sweep`** gained `pattern-misses-cardname-token`
  (BLOCKING) and `membership-shrank-since-probe` (BLOCKING).
- **`foundry_common`** now owns the single definition of
  `is_prefilter_pattern` / `pattern_slug` / `pattern_misses_cardname_token`.
  Two of this session's bugs were *duplicated definitions*, not logic errors.

---

## 5. The pattern that explains this session

Last session's finding was "a hand-maintained mirror gets trusted as the
record." This session found the same disease one layer down, three times:

| duplicated thing | consequence |
|---|---|
| `SUP-TRIAGE-PROTOCOL.md` copied instead of moved (commit `abf9c2b`, 2026-07-19) | the live copy lost **"Don't absorb, expand"** and 4 other ratified rules for six weeks — through batches 4–7 **and** corpus-pass run 1 |
| "is this pattern a pre-filter?" derived in two places | 3 ratified DET patterns sat unapplied while reading as handled |
| "does this axis exist?" tested on the slug string | 2a would have instantiated 3 duplicate axes |

**A copy is not a migration.** `CLAUDE.md` now carries this as a standing
rule, and the site repo holds no pipeline documentation at all.

Worth internalising: the sweep's blocking count went 11 → 6 this session, and
**none of that was a gate being loosened.** Bug 2's fix removed 3
name-collision + 3 name-reorder findings because those collisions were the
*symptom* of the string-identity bug. The remaining 6 are all real work
awaiting rulings.

---

## 6. Known-open technical debt

- **Tier-0 bug 4 (ADD-08)** — blocked on the walk, measured, rule corrections
  recorded.
- **`docs/B-CONSOLIDATION-REAUDIT-LLM-HANDOFF.md` is a PHANTOM.** Cited by
  both `CDR-PROPOSALS.md` and the 2026-08-01 handoff as the record of the A12
  external re-audit (verdict NO-GO-AS-WRITTEN, blockers B-01/B-02/B-03). It
  has never existed in git and is nowhere on disk. The findings survive only
  as summaries in those two documents.
- **`experiments/foundry_review.html` has been dark since 2026-07-17** while
  every review since went out as markdown — against the ratified rule that
  *"Captain's review surface is a tool, not a document."* Captain's CDR-07
  ruling (oracle text + card attributes + top-5 near homes) is a description
  of this tool's card inspector. Reviving it is probably the highest-leverage
  unstarted work, because ratification throughput is the bottleneck.
- **The convergence gate was never instrumented.** `T3-AXIS-FOUNDRY-v3.md`
  makes it the precondition for the full-corpus pass — codebook freezes at
  v1.0 first. The codebook is v0.7 and no record of the gate being evaluated
  exists anywhere in `docs/`. Run 1 launched anyway.
- 2a's artifact is `72d090d2…` (regenerated post-bug-2). Stale the moment any
  further CDR is ruled.
- 27 docs pass the ruling gate but were deliberately kept; 14 are blocked with
  the specific rulings named. See `docs/RATIFIED-RULINGS-REGISTRY.md`.

---

## 7. Standing discipline

- **Halt loudly.** Never guess, never silently skip.
- **Measure, never recall.** Every hand-written number checked this session
  was wrong: rev 2 said 34 counter axes (33) and ~15 renames (16); the
  previous handoff said 5 blocking findings (11 at the time). Paste from
  generator output (ADD-06).
- **Verify claims about missing files with an absolute path.** Two "phantom
  document" findings this session were my own grep errors — the files existed
  in the sibling repo.
- **Nothing model-generated is load-bearing without Captain ratification.**
- **`codebook.json` is gitignored.** `experiments/out/foundry/backups/` is the
  ONLY rollback path; the backup law and its readback are not optional.
- **One session, one work item.** Next session: the walk, nothing else.
- **Run both gates before and after any consolidation work:**
  `foundry_family_sweep.py --strict` and `foundry_ruling_registry.py`.
- **Never create, move or delete anything in `mtjawnny.github.io` without
  Captain approving that specific action.**
