# REPOSITORY ARCHITECTURE AUDIT — 2026-08-28

**A read-only inventory of every tracked file in this repository, the
organizational defects found, and a plan to fix them.**

Measured 2026-08-28 at HEAD `11d6363`. **Nothing was moved, renamed, deleted or
rewritten to produce this document, and nothing has been moved since.** Every
number below was derived from the live repository in one session and re-verified
against a byte-identical hash manifest of all 3,972 files.

**This document decides nothing.** It is a proposal. The migration it describes
has not started.

---

## THE SHORT VERSION

If you read nothing else, read these five things.

1. **This repository holds two systems that share one `docs/` folder.** The
   shipped build (`pipeline/`) and the Foundry/Thesaurus (`experiments/`) have
   **zero** code references to each other. They just happen to live together.

2. **You cannot safely move any Python file yet.** 97 files work out where the
   repository root is by counting directory levels from their own location, and
   they disagree about how many levels to count. **69 of them would break
   silently** — pointing at a real but wrong directory instead of raising an
   error.

3. **Making subfolders under `docs/` would silently drop documents from the
   ruling registry**, which is a Gate 2 gate. This already happened once. Seven
   references broke in the last archiving move and are still broken today.

4. **Eight files in `docs/` are not documents.** They are configuration read by
   code at run time — including the manifest that names which codebook is
   authoritative.

5. **The root `README.md` is wrong**, and it is the first thing anyone reads. It
   says "Weekly GitHub Actions pipeline", which is the exact sentence `CLAUDE.md`
   exists to correct.

**If only one thing gets done: fix the path problem (#2).** It is a real defect
today, independent of any reorganization. Everything else on this page is about
finding things faster. That one is about being correct.

---

# PART 1 — WHAT IS ACTUALLY IN HERE

336 tracked files. 3,972 files total once generated output is counted.

| Where | Tracked | What is actually there |
|---|--:|---|
| `pipeline/` | 11 | **The only shipped code.** The nine steps `build.yml` runs. |
| `experiments/` (flat) | 88 py | The Foundry. Standing tools, finished one-off scripts, and `tier_engine.py` (484 KB), all in one directory. |
| `experiments/aq4_benchmark/` | 21 | The AQ4 benchmark. Self-contained. |
| `experiments/moves/` | 20 | Codebook mutation specs. Also the ground-truth seed corpus. |
| `experiments/measure/` | 9 | Six measurement scripts and three memos. |
| `experiments/out/` | 0 | **2.7 GB, 3,321 files, gitignored.** Holds the working codebook. |
| `docs/` (flat) | 152 | Law, rulings, handoffs, incidents, arc records, 8 JSON config files, and a 990 KB copy of the Comprehensive Rules — all at one level. |
| `docs/archive/` | 18 | A previous archiving attempt. |
| `data/` | 0 | 458 MB of pipeline build state, gitignored. |
| `tests/` | 3 | Fixtures for the resolver, **which is unbuilt**. No test runner. |
| `tags/`, `recipes/` | 2 | Pipeline inputs. |
| `.claude/commands/` | 3 | The three triage slash-commands. |
| `CLAUDE.md` | 1 | **925 lines / 62 KB**, loaded into every session automatically. |

### The two systems, proved rather than assumed

Searching `pipeline/`, `tests/`, `.github/`, `recipes/` and `tags/` for any
mention of `experiments/` or `tier_engine` returns **nothing**. The workflow runs
nine `pipeline/*.py` scripts and no others.

This is the same finding the product audit reports as *"0 of 5 foundry artifacts
reach a shipped card"* — visible here as a directory fact. **They are two
projects, which is why a project boundary is the right fix and not just tidying.**

### What `docs/` actually contains

152 files at one level, in fourteen unrelated categories:

| Category | Files | Example |
|---|--:|---|
| Per-shape rulings | 21 | `BECOMES-TAPPED-RULING-2026-08-03.md` |
| Session handoffs | 19 | `SESSION-HANDOFF-2026-08-04-EVE.md` |
| Foundry core law | 16 | `CODEBOOK-NAMING-GRAMMAR.md` |
| Product / governance | 15 | `P3-CODEBOOK-DURABILITY-PACKET-2026-08-14.md` |
| CR derivation records | 15 | `SELF-REFERENCE-CR205-2026-08-05.md` |
| W-arc work records | 14 | `W4-ANTHEM-2026-08-09.md` |
| Re-audit / tier packets | 11 | `REAUDIT-TIER-2-2-2026-08-02.md` |
| Consolidation arc | 10 | `B-MIGRATION-DISCOVERY.md` |
| **JSON configuration** | 8 | `grammars.json` — **not documentation** |
| AQ4 / semantic | 7 | `AQ4-…-IMPLEMENTATION-CONTRACT.md` |
| Batch ratifications | 6 | `TRIAGE-BATCH-5.md` |
| Routing | 5 | `PICK-UP-HERE.md` |
| Incidents | 2 | `INCIDENT-AQ4-PACKET7-STOP-BREACH-2026-08-17.md` |
| **External reference** | 1 | The Comprehensive Rules, 990 KB |

A ratified law document and a superseded session handoff are the same kind of
thing to anyone browsing this folder. **That is the core retrieval problem.**

---

# PART 2 — THE PROBLEMS

Twelve defects. Three are actively causing damage right now. Five are structural.
Four are about navigation.

## Group A — Already broken today

### A1. Python files disagree about where the repository root is

This is the biggest obstacle, and it is a live bug rather than untidiness.

Every Foundry module figures out its base directory by counting levels up from
its own file. There are **three different answers in use**, and two of them share
the same variable name:

| Code | Files | Resolves to | Breaks when |
|---|--:|---|---|
| `Path(__file__)…parent` | 69 | `experiments/` — **but the variable is named `REPO_ROOT`** | the file's own folder is renamed |
| `Path(__file__)…parents[1]` | 22 | the actual repo root | the file's depth changes |
| `Path(__file__)…parents[2]` | 6 | the actual repo root | the file's depth changes |

They then disagree again about how to reach `docs/`:

- `foundry_cr.py` writes `REPO_ROOT.parent / "docs"`
- `foundry_family_sweep.py` writes `REPO_ROOT / "docs"`

**Both are correct**, because `REPO_ROOT` means a different directory in each
file. A variable named `REPO_ROOT` holds `experiments/` in 69 files.

**Why this is dangerous:** if a file moves, the 28 depth-counting files raise a
clear error — fine, you fix them. But the **69 `.parent` files keep working and
point somewhere wrong.** No exception. No halt. Just a different directory that
happens to exist.

This is the repository's own documented failure family — *a derived map is not
the list it was derived from* — aimed at the filesystem.

### A2. Subfolders under `docs/` silently remove documents from the registry

`foundry_ruling_registry.py` is a Gate 2 gate. Line 115 runs
`git ls-files -z -- docs`, and line 129 keeps only files **directly under**
`docs/`, explicitly "never `docs/archive/`". `foundry_prior_art.py` does the same
with a flat `docs/*.json` glob.

Create one subfolder and those documents leave the registry. Gate 2 still passes.

**The repository already knows this.** `docs/archive/README.md` says so in its
own words: *"Archived docs drop out of the registry scan (it globs `docs/*.md`,
not subdirectories), so condition 1 must be checked before the move."*

Note the asymmetry that hides it: `foundry_slug_dossier.py` uses `rglob` and
**survives** any subfolder scheme. Two tools that look like they do the same job
respond to the same move in opposite directions, and only one reports it.

### A3. The last archiving move broke seven references, still broken

**19 file paths are referenced in the documentation and do not exist.** Seven of
them are sitting one folder down, in `docs/archive/`:

| Referenced as | Actually at |
|---|---|
| `docs/TRIAGE-BATCH-4.md` | `docs/archive/TRIAGE-BATCH-4.md` |
| `docs/CORPUS-PASS-WALK-RATIFICATION.md` | `docs/archive/CORPUS-PASS-WALK-RATIFICATION.md` |
| `docs/CONSOLIDATION-PLAN-DIRECTIVE.md` | `docs/archive/CONSOLIDATION-PLAN-DIRECTIVE.md` |
| `docs/CONSOLIDATION-RUN1-DIRECTIVE-2.md` | `docs/archive/CONSOLIDATION-RUN1-DIRECTIVE-2.md` |
| `docs/OUTPUT-TRIM-PROPOSAL.md` | `docs/archive/OUTPUT-TRIM-PROPOSAL.md` |
| `docs/B-MIGRATION-SESSION-1-REPORT.md` | `docs/archive/B-MIGRATION-SESSION-1-REPORT.md` |
| `docs/T3-BUILDOUT-STEP3-HANDOFF.md` | `docs/archive/T3-BUILDOUT-STEP3-HANDOFF.md` |

The other twelve point at files that never existed or have left — including
`docs/mtg-comprehensive-rules.md` (**11 mentions**, the pre-refresh CR filename)
and two dead script paths, `experiments/audit_derivations.py` and
`experiments/measure/parent_candidate_evidence.py`.

**This is the measured precedent for what a move costs without a
reference-update step.** It is not a hypothetical risk; it already happened.

## Group B — Structural

### B1. Eight configuration files are filed as documentation

These are parsed by code at run time. They are not documents:

| File | Python readers | What it is |
|---|--:|---|
| `docs/det-patterns-v2.json` | 10 | the DET pattern table |
| `docs/grammars.json` | 8 | grammar families |
| `docs/cr-checks.json` | 4 | **generated** CR-term cache |
| `docs/det-patterns-v1.json` | 3 | superseded pattern table |
| `docs/family-sweep-known-debt.json` | 2 | the authorized W6 excuse set — a Gate 2 input |
| `docs/det-patterns-cr-actions-v1.json` | 2 | CR action patterns |
| `docs/codebook-authority.json` | 1 | **the manifest naming the authoritative codebook (P3-1)** |
| `docs/cr-predefined-tokens.json` | 0 | no reader found — possibly orphaned |

The single most load-bearing configuration file in the project sits in a folder
of 152 markdown documents.

### B2. Two tracked markdown files are program output

- `docs/RATIFIED-RULINGS-REGISTRY.md` (100 KB) is written by
  `foundry_ruling_registry.py`
- `docs/DEFINITION-DRIFT-AUDIT-2026-08-02.md` is written by
  `foundry_definition_drift.py`

Both sit among 150 hand-authored documents with nothing marking them as
regenerable. `docs/cr-checks.json` is likewise generated, and `CLAUDE.md` already
records a trap caused by reading it as if it were the CR itself.

#### B2a. This defect fired during this audit, and it is worth reading

`docs/RATIFIED-RULINGS-REGISTRY.md` is **currently showing as a modified tracked
file in the working tree**, and no human edited it.

What happened, to the second:

| time | event |
|---|---|
| `19:34:19` | the Adjudicator-A incident record was committed |
| `19:34:29` | the post-commit Gate 2 run executed `foundry_ruling_registry.py`, which **rewrote the registry in place** to harvest the newly committed document |

The regeneration is correct behaviour. Two consequences are not obvious, and both
are arguments for the `generated/` directory proposed in Part 3:

**1. A gate leaves the working tree dirty as a side effect of passing.** Running
Gate 2 — a read-only verification, as far as anyone reading its name would assume
— modifies a tracked file. Any later session running `git status` sees an
unexplained modification and cannot tell it from real uncommitted work. There is
nothing in the file's name or location that says "regenerated".

**2. The harvest picked up a false positive.** The registry now records the
incident record as a source for structural ruling **`S1`**, on this line:

> `INCIDENT-…-STOP-BREACH-2026-08-17.md:48` — *"correspondence, semantic verdicts,
> candidate data, answer-key truth, the S1 and"*

That sentence is about the AQ4 **S1 tranche**. It has nothing to do with `S1`,
the parent-tree structural ruling in `PARENT-TREE-CANDIDATES.md`. The registry's
summary moved `S1` from *"12 references across 10 docs"* to *"13 across 11"* on
the strength of a collision between two unrelated uses of the same two characters.

**The identifier namespace is overloaded and the harvester cannot see it.** This
is the repository's own documented failure family — *a markdown document is an
API* — appearing in the ruling registry rather than in grammar §2. It is a small
error today. It matters because sole-home counting is what the archive entry gate
depends on: a document wrongly credited as a ruling's home is a document the gate
will refuse to archive, and a ruling wrongly believed to be corroborated is one
that could be archived when it should not be.

**Not fixed here.** It is recorded because it was found, and because it is
evidence for two separate proposals: generated output belongs in its own
directory, and the ruling harvester needs a word-boundary or context rule before
any reorganization leans on its counts as a migration check (Part 6, Phase 2).

### B3. The working codebook lives in a gitignored output folder

`experiments/out/foundry/codebook.json` — 615 axes, 8,982 members, sha
`6aa6193f…` — is the operational authority, and `git` cannot see it. The tracked
selector `docs/codebook-authority.json` names the matching R2 snapshot, so P3
already addresses the *durability* question. The **filing** is still wrong: the
most important artifact in the project sits beside 1.2 GB of engine snapshots and
124 batch-API request dumps.

### B4. Forty of eighty-eight Foundry scripts are finished work

| Group | Files | Status |
|---|--:|---|
| Batch adapters and assemblers (batches 1–7) | 13 | arc complete |
| Batch-8 A/B one-offs | 4 | arc complete |
| Consolidation run-1 | 5 | arc complete, **internally coupled** |
| One-off probes (corpus pass, corroboration, wire, r5…) | 9 | arc complete |
| Codebook migration | 3 | arc complete |
| Re-audit builders and CDR-09 walk | 4 | arc complete |
| Viewer tooling | 2 | dormant since 2026-07-17 |

They are indistinguishable by name or location from the 45 standing tools. **Six
of them are imported by siblings**, so they have to move as a group or not at all.

### B5. AQ4 is split across three places

- Contract and papers in `docs/` — 7 tracked, 6 untracked
- Implementation in `experiments/aq4_benchmark/`
- Probes in `experiments/foundry_aq4_probes.py` (91 KB, top level)
- Working artifacts in `experiments/out/aq4/`

`experiments/aq4_benchmark/README.md` is 52 KB and is the de-facto current-state
document for the whole programme — filed where no router points to it.

## Group C — Navigation

### C1. The root README is wrong

All six lines. It opens *"Weekly GitHub Actions pipeline"* — which `CLAUDE.md`
spends its first paragraph correcting: *"IT DOES NOT RUN WEEKLY. This line said
it did until 2026-08-13, and that was never true."* It mentions neither the
Foundry nor AQ4, and has not been touched since 2026-07-03.

### C2. Four documents compete to be the entry point

- `CLAUDE.md` (925 lines, auto-loaded) points to `PICK-UP-HERE.md` **and** to
  `SESSION-HANDOFF-2026-08-09.md`, while noting that second pointer goes stale
- `SESSION-START-PROCEDURE.md` Gate 1 claims authority over which handoff is current
- `PICK-UP-HERE.md` calls itself the stable entry point

Measured today: `PICK-UP-HERE.md` was last edited **2026-08-15** — before the
Packet-7 arc and all of Phase A — and says Gate 2 has 12 rows when it has 16. The
genuinely current AQ4 state lives in `experiments/aq4_benchmark/README.md`, which
no router mentions at all.

### C3. Nineteen session handoffs sit beside ratified law

All of them carry superseded banners, and they still occupy the same folder and
the same visual weight as `CODEBOOK-NAMING-GRAMMAR.md`. A fresh session browsing
`docs/` cannot tell law from a superseded note without opening files.

### C4. Eight architecture documents have been untracked for fifteen days

The 2026-08-13/14 semantic-address and fact-layer papers, plus
`INCIDENT-LOCALITY-REVERSION-2026-08-14.md`. An untracked incident record has no
version history — the precise reason twelve documents were moved into this repo
on 2026-08-02. They are also invisible to `foundry_ruling_registry.py`, which
reads the git index.

---

# PART 3 — THE PROPOSED STRUCTURE

The goal: a cold session gets from *"what is this repo"* to *"this is the
authoritative file"* in **four reads**, three of which are small by design.

```
repository README  →  project README  →  subsystem README  →  the exact file
     ~60 lines           ~80 lines           ~60 lines
```

## Top level

```
mtjawnny-pipeline/
├── README.md              ← repository router (rewrite; currently wrong)
├── CLAUDE.md              ← contract: locked rules + routing only
├── LICENSE · requirements.txt · .gitignore
├── .github/workflows/
├── pipeline/              the shipped build — UNCHANGED
├── tags/ · recipes/       pipeline inputs — UNCHANGED
├── tests/                 resolver fixtures — UNCHANGED
├── data/                  pipeline build state, ignored — UNCHANGED
└── mtg-thesaurus/         ← NEW project boundary
```

## Inside the project

```
mtg-thesaurus/
├── README.md              project router — the subsystems, and what is NOT here
├── STATE.md               the ONE current-state index
│
├── law/                   ★ CURRENT AUTHORITY
│   ├── README.md
│   ├── CODEBOOK-NAMING-GRAMMAR.md, DERIVED-TAG-LAYER-SPEC.md,
│   │   T3-AXIS-FOUNDRY-v3.md, T3-BUILDOUT-PLAYBOOK.md,
│   │   PARENT-TREE-CANDIDATES.md, OUT-OF-SCOPE.md,
│   │   SESSION-START-PROCEDURE.md, SUP-TRIAGE-PROTOCOL.md
│   ├── rulings/           the 21 per-shape rulings
│   └── ratifications/     TRIAGE-BATCH-* and RATIFIED-DIRECTIVES-*
│
├── governance/            ★ CURRENT AUTHORITY
│   ├── incidents/         the 3 incident records
│   ├── authority/         P3 packet + codebook-authority.json
│   └── decisions/         open and ruled decision packets
│
├── aq4/                   the benchmark programme
│   ├── IMPLEMENTATION-CONTRACT.md    the single entry point
│   ├── addenda/ · reviews/
│   └── benchmark/         aq4_benchmark/ moved intact
│
├── src/                   implementation — DELIBERATELY FLAT
│   ├── README.md          the role table that replaces subfolders
│   ├── paths.py           NEW — the one root resolver
│   ├── foundry_*.py       45 standing tools + core
│   ├── tier_engine.py, snapshot.py, viewer files
│   ├── measure/ · moves/  moved intact
│   └── retired/           the 40 completed-arc scripts (late phase)
│
├── config/                the 8 JSON files from docs/
├── reference/             the Comprehensive Rules
├── evidence/              design + measurement records
│   ├── cr-derivation/ · work-arcs/ · audits/
└── history/               ✗ NEVER LAW
    ├── README.md          "nothing here is current" + a retrieval index
    ├── handoffs/          all 19
    ├── arcs/              consolidation, re-audit, tier packets
    └── archive/           the existing docs/archive/, moved intact
```

## Three things deliberately NOT moved

**1. The Python namespace stays flat.** `foundry_common` is imported by **82**
modules by bare name — which works only because it inserts its own directory onto
`sys.path`. Splitting into `core/ gates/ tools/` would break that for all 82 to
buy shelf-tidiness that `src/README.md` provides for free.

> **Group by role in the index, not the filesystem, when the filesystem is a
> module namespace.**

**2. Generated output stays put.** `experiments/out/` (2.7 GB) and `data/`
(458 MB) are referenced by 69 files' base-directory assumptions and nobody
browses them. Zero retrieval benefit, real risk.

**3. `pipeline/` stays at the root.** It is the only shipped code, the workflow
names all nine scripts by path, and it has no coupling to anything being moved.
Leaving it at the top is *what makes the project boundary readable.*

---

# PART 4 — FILE MIGRATION MAP

Each group is independently landable and independently revertible.

| # | Group | Files | From → To |
|---|---|--:|---|
| A | Config JSON | 8 | `docs/*.json` → `config/` |
| B | Comprehensive Rules | 1 | `docs/MTG_Comp…md` → `reference/` |
| C | Session handoffs | 19 | `docs/SESSION-HANDOFF-*`, `*-HANDOFF.md` → `history/handoffs/` |
| D | Ratified law | 10 | the 10 named law docs → `law/` |
| E | Per-shape rulings | 21 | `docs/*-RULING-*.md` → `law/rulings/` |
| F | Batch ratifications | 6 | `TRIAGE-BATCH-*`, `RATIFIED-DIRECTIVES-*` → `law/ratifications/` |
| G | Governance | 6 | `INCIDENT-*` → `governance/incidents/`; `P3-*`, `codebook-authority.json` → `governance/authority/` |
| H | AQ4 papers | 13 | `AQ4-*`, `SEMANTIC-*`, `FACT-GRANULARITY-*`, etc. → `aq4/` |
| I | AQ4 benchmark | 21 | `experiments/aq4_benchmark/` → `aq4/benchmark/` |
| J | Evidence: CR derivation | 15 | `CR-*`, `SELF-REFERENCE-*`, etc. → `evidence/cr-derivation/` |
| K | Evidence: work arcs | 14 | `W[0-9]*`, `D[0-9]-*`, `STEP-2*` → `evidence/work-arcs/` |
| L | Evidence: audits | 9 | `PRODUCT-REALITY-*`, `SYSTEM-SELF-TEST-*`, `WIRE-*` → `evidence/audits/` |
| M | History: arcs | 21 | `B-*`, `CONSOLIDATION-*`, `REAUDIT-*`, `TIER-[0-9]-*` → `history/arcs/` |
| N | History: existing archive | 18 | `docs/archive/` → `history/archive/` |
| O | Generated docs | 2 | the 2 program-written `.md` → `generated/` |
| P | Foundry Python | 88 | `experiments/*.py` → `src/` |
| Q | measure/ + moves/ | 29 | moved intact into `src/` |
| R | Retired arc scripts | 40 | `src/*.py` → `src/retired/` |
| — | New routers | +9 | new README / STATE files |
| — | `pipeline/ tags/ recipes/ tests/ data/ .github/` | 0 | **no change** |

Groups A–O cover all 170 tracked `docs/` files plus the 8 untracked ones. P–R
cover all 99 `experiments/` Python files and both subfolders.

---

# PART 5 — WHAT WOULD BREAK, AND HOW IT FAILS

Six kinds of reference. **Two fail loudly. Four fail silently — those are the
dangerous ones.**

| Reference | Count | Fails | Fix |
|---|--:|---|---|
| Base-directory derivation | 97 | **SILENTLY** — 69 land on a wrong-but-real folder | `paths.py` (Phase 0) |
| Bare-name imports | 82 | loudly — `ImportError` | one `sys.path.insert` |
| Registry doc enumeration | 2 | **SILENTLY** — docs vanish from the registry | make the roots a list |
| Named-file constants | ~14 | loudly — halt-guards fire | re-point at `paths.*` |
| Doc → doc path mentions | **661** | **SILENTLY** — prose rots | scripted rewrite + link checker |
| Doc → script path mentions | **288** | **SILENTLY** — pasted commands fail | same rewrite pass |

### The constants that need re-pointing

| File | Constant |
|---|---|
| `foundry_cr.py` | `CR_PATH` |
| `foundry_probe.py` | `GRAMMAR` |
| `foundry_recorded_numbers.py` | `GRAMMAR` |
| `foundry_family_sweep.py` | `GRAMMARS_PATH`, `DET_PATTERNS_PATH`, `KNOWN_DEBT_PATH` |
| `foundry_authority.py` | `MANIFEST_PATH` |
| `foundry_definition_drift.py` | `REPORT_MD` |
| `foundry_ruling_registry.py` | `DOCS`, `OUT_MD`, the `git ls-files` call |
| `foundry_prior_art.py` | `DOCS` — **flat glob, does not survive subfolders** |
| `foundry_slug_dossier.py` | `DOCS` — **uses `rglob`, survives** |
| `foundry_common.py` | `FOUNDRY_OUT_DIR`, the `sys.path` insert |
| `foundry_audit_baseline.py` | `BASELINE` |
| `.claude/commands/*.md` | triage commands citing script paths |

---

# PART 6 — HOW TO DO IT SAFELY

Nine phases. **Phase 0 is not optional and nothing else may start before it.**

| Phase | What it does | Files moved | Green when |
|--:|---|--:|---|
| **0** | **Add `paths.py`** — one module that finds the repo root by walking up to `.git`. Convert all 97 derivations to use it. | **0** | Gate 2 green ×2 byte-identical; every generated hash unchanged |
| **1** | **Fix the 19 dangling references** that already exist. Add a dangling-link checker to Gate 2. | 0 | checker reports 0, negative-controlled against a planted bad link |
| **2** | **Generalize doc enumeration** — give the registry and prior-art a root *list*; keep the git-index rule. | 0 | registry output byte-identical |
| **3** | **Create the tree and routers.** Nine README/STATE files, empty folders, root README rewrite. Purely additive. | +9 | nothing to break |
| **4** | **Groups B + A** — the CR, then config JSON. Small and loud; exercises `paths.py` against a halt-guarded constant. | 9 | CR loader byte-identical |
| **5** | **Groups C, M, N** — handoffs, arc history, existing archive. Biggest retrieval win, lowest code risk: no module reads these. | 58 | registry count unchanged; link checker 0 |
| **6** | **Groups D, E, F, G, O** — law, rulings, governance, generated docs. Touches `GRAMMAR`, `MANIFEST_PATH`, both writers. | 45 | grammar §2 parse identical; authority resolves |
| **7** | **Groups H, I** — AQ4 papers and benchmark together. **Re-verify frozen hashes explicitly**, not just Gate 2. | 34 | `pairs_sha256`, surface digest, workqueue sha all unchanged |
| **8** | **Groups J, K, L** — evidence. No code reads them. | 38 | link checker 0 |
| **9** | **Groups P, Q** as one atomic `git mv`. Then **R** separately, all 40 together. | 128 | full Gate 2 + AQ4 regeneration + full hash manifest |

### The rule for every phase

**Before:** capture the hash manifest, the Gate 2 verdict, the registry ruling
count, and the AQ4 frozen-input hashes.
**After:** all four identical, or the phase reverts.

**Use `git mv`, and commit the move separately from any content edit.** A move
plus an edit in one commit defeats rename detection and loses the file's history
— which is the one thing a reorganization must not cost.

---

# PART 7 — RISKS

| Risk | Why it is real | Control |
|---|---|---|
| **Silent base-directory redirect** | 69 files call `experiments/` their `REPO_ROOT`. After a move, `.parent` still resolves to a real folder — the wrong one. No exception raised. | Phase 0 first; assert `paths.ROOT` contains `.git` at import and halt if not |
| **Documents leaving the registry** | Measured precedent: the `docs/archive/` move already did this | Phase 2 first; gate every docs phase on an unchanged ruling count |
| **Gate 2 green means nothing here** | Gate 2 checks Foundry output correctness. A document that stopped being harvested, or prose pointing at a moved file, is invisible to all 16 rows | Two new instruments — link checker and registry count — treated as first-class |
| **Losing file history** | Rename detection fails when a move and an edit share a commit. These documents' history *is* the evidence for current law | move-only commits; verify with `git log --follow` per group |
| **Breaking the flat namespace** | 82 modules import by bare name via one `sys.path.insert` | keep `src/` flat; subfolders would be a package conversion, not a move |
| **Disturbing frozen AQ4 state** | Phase 7 touches the pairing, population and seed commitment. The binding module halts under a moved state — correct behaviour that will look like a migration failure | re-derive the four frozen hashes before and after; treat any halt as a stop |
| **The 8 untracked docs** | Cannot be `git mv`'d, invisible to the registry | commit them where they are, in their own commit, before Phase 5 |
| **`CLAUDE.md` drift** | ~70 trap bullets, many naming exact paths, auto-loaded every session | rewrite in Phase 3; traps move to a referenced document under `law/` |
| **Reorganizing mid-incident** | AQ4 Phase A is open with six unanswered questions | land Phases 0–3 (which move nothing) freely; hold 4–9 for a clean checkpoint |

---

# PART 8 — WHAT NEEDS A DECISION

## Mechanical — no ruling needed

- **Phases 0, 1, 2.** All three are defect fixes that move nothing, and are worth
  doing whether or not the reorganization proceeds.
- **Rewriting the root `README.md`**, which contradicts `CLAUDE.md` today.
- **Committing the eight untracked 2026-08-13/14 documents.**
- **Groups B, C, J, K, L, M, N** — no module reads any of them.

## Captain's call

| # | Decision | Why it is yours |
|--:|---|---|
| 1 | **The project folder name.** `mtg-thesaurus/` as proposed, or `foundry/` — the name the code, the gates and 288 doc references already use | naming is vocabulary, and vocabulary is ratified. "Thesaurus" is the product; "Foundry" is the system |
| 2 | **Whether `STATE.md` replaces `PICK-UP-HERE.md` and the handoff chain**, or sits above them | retiring the handoff pattern changes how sessions end, and `SESSION-START-PROCEDURE.md` Gate 1 is ratified law |
| 3 | **Whether `tier_engine.py` belongs under the Thesaurus at all**, or is promoted beside `pipeline/` | 484 KB, 12 importers, and the one component that *would* reach a card if the codebook were wired in. Its filing encodes a position on that |
| 4 | **Whether the 40 retired scripts move to `src/retired/`** or stay flat | six are imported by siblings; separating them asserts the arcs are closed |
| 5 | **Whether generated output moves** out of `experiments/out/` — not recommended here | 2.7 GB, 69 files' assumptions, and the working codebook. Cost real, benefit aesthetic |
| 6 | **How far `CLAUDE.md` is cut** | every bullet was paid for by a real defect. Which become a referenced document rather than always-loaded context is a judgement about what a cold session must hold |
| 7 | **Timing against AQ4** — Phases 0–3 now and 4–9 later, or all of it now | sequencing infrastructure against open governance work |

---

# APPENDIX — HOW THESE NUMBERS WERE MEASURED

Every figure came from the live repository on 2026-08-28, not from any prior
document. The methods, so they can be re-run:

| Claim | Method |
|---|---|
| 336 tracked, 3,972 total | `git ls-files`; `find` excluding `.git/` and `.venv/` |
| 97 root derivations, 69/22/6 split | grep for `Path(__file__).resolve().parent[s[N]]` across tracked `.py` |
| 82 importers of `foundry_common` | grep for `import foundry_common` / `from foundry_common import` |
| 661 doc→doc, 288 doc→script mentions | regex over `docs/` and `CLAUDE.md` for path-shaped strings |
| 19 dangling references | each extracted path tested with `[ -f ]` |
| Registry flat-only behaviour | read `foundry_ruling_registry.py` lines 101–129 directly |
| Two systems, no coupling | grep `pipeline/ tests/ .github/ recipes/ tags/` for `experiments`/`tier_engine`; read `build.yml` |
| 88/45/40 script split | name-pattern census over top-level `experiments/*.py`, cross-checked against the Gate 2 roster and the import graph |
| Codebook 615 axes / 8,982 members | parsed `experiments/out/foundry/codebook.json` |
| Gate 2 is 16 rows | ran `python3 experiments/foundry_gate2.py` |

**Read-only conservation, verified.** HEAD `11d6363` at start and end; a sha256
manifest of all 3,972 files re-derived after the audit and compared
byte-for-byte — **identical**. Working-tree status, stash list, branch and index
unchanged. No commit made.

**One clarification on the working-tree state, stated precisely.** At the moment
the audit began, the tree already carried **one modified tracked file** —
`docs/RATIFIED-RULINGS-REGISTRY.md`, regenerated by Gate 2 ten seconds after the
preceding commit (see **B2a**) — alongside the eight untracked 2026-08-13/14
documents. That modification **pre-dates this audit and was not caused by it**:
the file's sha256 is byte-identical in the before and after manifests. An earlier
summary of this audit described the tree as carrying only the eight untracked
documents, which understated it by that one file.

**This document is additive**, written after the audit: it moves, renames and
deletes nothing.
