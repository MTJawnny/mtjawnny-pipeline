# REFOUNDATION ROADMAP

Status: **BOOTSTRAP ROADMAP — TARGET ARCHITECTURE NOT YET RATIFIED**

This roadmap records sequence, not final implementation detail.

## P0 — Repository / Engine Refoundation

The purpose of P0 is to make the MTG Thesaurus / Foundry system able to stand itself up deterministically, expose one obvious current authority path, support disposable Manager/Worker sessions, and preserve semantic truth while replacing accidental architecture.

AQ4 feature work remains paused during P0 unless Captain explicitly changes that priority.

---

## P0.0 — Establish durable bridge and forensic baseline

Status: **COMPLETE**

Completed:
- measured local vs GitHub relationship;
- proved local history was 62 commits ahead / 0 behind and linear;
- published `refoundation-baseline-2026-08-28` at `11d6363...`;
- kept remote `main` untouched at `3a2db84...`;
- verified ChatGPT can read/write GitHub;
- verified Claude can receive a GitHub Issue and post a durable result;
- removed Captain from routine technical result transport.

---

## P0.1 — Clean-slate architecture study

Status: **COMPLETE / PENDING REVIEW**

GitHub Issue: **#1**

Claude performed a read-only clean-slate architecture analysis under:

> PRESERVE TRUTH, NOT PLUMBING.

It proposed, among other things:
- real Python packaging;
- explicit import layering;
- one path owner;
- separation of library modules and CLI entry points;
- pure validation (`check` vs `emit`);
- tracked ratchet baselines;
- machine-readable knowledge status/frontmatter;
- generated routing/state indexes;
- structured ruling data;
- AQ4 one-way isolation;
- aggressive legacy dispositions;
- a multi-phase migration.

These are **proposals, not accepted architecture** until reviewed.

---

## P0.2 — Manager architecture review

Status: **NEXT**

Owner: fresh GitHub-enabled ChatGPT Manager session.

Objective:
- read Issue #1 result completely;
- inspect exact repository evidence needed to challenge/confirm it;
- separate measurements from design choices;
- identify where Claude's proposal conflicts with Captain direction, accepted Foundry law, or practical system requirements;
- reduce Claude's D1–D9 into the smallest real Captain decision set;
- recommend an accepted target architecture or request bounded additional evidence.

Mutation: **NONE by default.**

Deliverable:
- durable architecture review / Captain decision sheet in GitHub.

---

## P0.3 — Captain architecture decisions

Status: **BLOCKED ON P0.2**

Captain should be asked only questions that cannot be mechanically derived from already-stated direction.

Likely classes:
- permanent package/project naming;
- whether rulings become structured data with generated views;
- final knowledge-authority model;
- handoff retirement policy;
- research/archive extraction boundary;
- generated-but-tracked exceptions if any;
- timing/order constraints against paused AQ4.

The fresh Manager may reduce or alter this list after reviewing Issue #1.

---

## P0.4 — Ratify refoundation target + conservation contract

Status: **BLOCKED**

Before migration:
- write/record accepted target architecture;
- record which prior architecture documents are evidence vs superseded;
- define exact conservation quantities;
- define the migration state machine;
- define rollback/STOP rules;
- define branch/PR strategy;
- ensure the known local-only files are classified before depending on GitHub as complete state.

---

## P0.5+ — Incremental implementation

Status: **NOT AUTHORIZED**

Implementation should proceed at durable verification boundaries, not as one giant refactor.

The actual phases will be selected only after P0.2/P0.3/P0.4.

Candidate classes from Issue #1 include:
- canonical path ownership;
- pure gate architecture;
- tracked ratchet baseline;
- link integrity;
- knowledge metadata/index/state;
- Python package skeleton;
- layer-by-layer module migration;
- cycle removal;
- CLI separation;
- generated-output relocation;
- knowledge migration/disposition;
- AQ4 isolation;
- extract/delete pass.

Do not treat this list as authorization or final ordering.

---

# Parallel concern — session independence

Session drift is a first-class refoundation requirement, not a later convenience.

Success means:
- a new ChatGPT Manager can recover current state from GitHub/repository resources;
- a new Claude Worker can recover its task from GitHub/repository resources;
- neither needs the previous session transcript;
- task base/state mismatches are detectable and cause STOP;
- accepted decisions/results are durable before a session ends.

Bootstrap implementation lives in this `refoundation/` directory and should itself be replaced by the final state/routing architecture once that architecture is accepted.

---

# Return to AQ4

AQ4 remains paused at the Adjudicator-A incident checkpoint.

Do not resume unit-binding adjudication, Adjudicator B, or C1–C6 merely because infrastructure phases become green.

The return-to-AQ4 condition should be explicit in durable state after the refoundation has a trustworthy authority/routing/validation foundation.
