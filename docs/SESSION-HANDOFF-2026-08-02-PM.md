# SESSION HANDOFF — 2026-08-02 (PM)

Supersedes `SESSION-HANDOFF-2026-08-02.md` for current state. That file remains
the accurate record of the documentation-migration arc and the Tier-0 bug fixes;
its §2 walk specification is now **executed**.

**Zero API calls. Cumulative arc spend unchanged at $90.51 / $140.** Everything
this session was DET and in-house.

---

## 0. READ THIS FIRST — the failure mode is missing context

Captain's finding, 2026-08-02, and it is the most important line in this file:

> **"Every drift has been due to a session not having enough context."**

This is not a general caution. It is the measured cause of every defect found
today, mine included:

| defect | root cause |
|---|---|
| I proposed 3 renames that would have **destroyed ratified names** | wrote a conformance checker against grammar §8a alone, having not read §7, batch-5, or D12 |
| Multi-axis `adds` landed with quotes proving the **wrong axis** | did not re-read what an evidence quote is for before reusing one |
| `source_ref` stamped outside the closed vocabulary, and 3 adds **credited a triage batch with a decision it never made** | did not read `foundry_codebook.py`'s source_ref vocabulary before writing to it |
| 3 confident "findings" that were **false** (Kytheon, The Black Gate, Corrosion) | read the first 150 characters of an oracle text instead of all of it |

Every one was caught by a gate or by Captain — none by the code that caused it.
**A fix lands unverified until something downstream reads it.**

**Therefore: read the manifest in §2 before touching anything.** Do not start
work from this handoff alone. This handoff tells you *what is true*; the
manifest tells you *what is law*, and the law is what stops you re-deciding a
settled question or breaking a ratified name.

---

## 1. Live state — all measured at session end

| | |
|---|---|
| codebook | `foundry-codebook/2` v0.7 · **489 axes** · **322 active** · 7,871 total members (7,403 on active axes) |
| sha256 | `b89487b13925742b109f4cf9c2827c631c426742c97f9465616f9166e0f9649c` |
| statuses | active 322 · killed 75 · renamed 63 · merged 27 · deferred 2 |
| lint | clean |
| family sweep | 202 findings, **6 blocking** (unchanged all session) |
| definition drift | **27 findings** (C1a 1, C1b 1, C2 17, C3 8) — down from 34 |
| docs | 46 live · 15 archived |
| spend | $90.51 / $140 |

`codebook.json` is **gitignored**. `experiments/out/foundry/backups/` is the
ONLY rollback path. Five backups were written today, each readback-verified.

---

## 2. READING MANIFEST

### 2a. Mandatory before ANY foundry work — no exceptions

| doc | why |
|---|---|
| `CLAUDE.md` (repo root) | the contract. Locked rules, traps, vocabulary |
| **`docs/CODEBOOK-NAMING-GRAMMAR.md`** | **the single most load-bearing file.** All slug law: §1 slots + multi-axis membership, §2 DELIVERY vocab + 3 new rules ratified today, §3 activation-restriction, §4 EFFECT verbs, §7 scaling stats, §8/§8a counter law, §9 cost-vs-effect, §10 validator, §12/§12a migration ledger. **Read it whole. Three of my errors today came from reading one section.** |
| `docs/RATIFIED-RULINGS-REGISTRY.md` | generated index of every ratified ruling and its sole home. **Grep this for any slug before calling it defective.** |
| this file | current state |

### 2b. Mandatory before touching the codebook

| doc | why |
|---|---|
| `docs/T3-AXIS-FOUNDRY-v3.md` + `docs/T3-BUILDOUT-PLAYBOOK.md` | the foundry spec inherits every standing rule in the playbook; read both, as CLAUDE.md says |
| `docs/DERIVED-TAG-LAYER-SPEC.md` | derivation law, Lessons 1–3 |
| `docs/CORPUS-PASS-PLAN.md` | where the corpus pass stands and what §11.2 wiring expects |

### 2c. Ratified rulings from TODAY — these are law, and they are new

| doc | ruling |
|---|---|
| `docs/CDR-09-WALK-DERIVATION-2026-08-02.md` | the §12a walk, executed. **Also the record of how encoding one law manufactures false defects.** |
| `docs/DAMAGE-DELIVERY-RULING-2026-08-02.md` | any-damage vs combat-damage; `combat-` is a restriction, not decoration |
| `docs/MEMBERSHIP-RATIFICATION-PACKET-2026-08-02.md` | 8 new axes; **multi-axis membership** standing rule |
| `docs/REAUDIT-TIER-1-FINDINGS-2026-08-02.md` | **created-ability rule** (§2a) — a card does not deliver an ability it creates |
| `docs/TIER-2-DECISION-PACKET-2026-08-02.md` | 10 tier-2 defects + **D3f: `{T}` is axis identity**, with the general when/whether-vs-how-much test |
| `docs/REAUDIT-TIER-2-FINDINGS-2026-08-02.md` | the tier-2 evidence, incl. 3 false positives that died on verification |

### 2d. Batch ratification record — Captain's annotations are AUTHORITATIVE

`docs/TRIAGE-BATCH-1.md` · `-2` · `-3` · `-5` · `-7` ·
`docs/archive/TRIAGE-BATCH-4.md` · `docs/archive/TRIAGE-BATCH-6.md` ·
`docs/RATIFIED-DIRECTIVES-BATCH-4-6.md` ·
`docs/archive/CORPUS-PASS-WALK-RATIFICATION.md`

**These contain rulings that no other file records.** Batch-5 alone holds the
counter-polarity-is-a-parameter ruling and D12; the archived walk-ratification
holds the `own-counters` pass. I broke two ratified names today by not reading
them. **`grep -rn '<slug>' docs/` including `docs/archive/` is not optional.**

### 2e. Decisions still waiting on Captain

`docs/FAMILY-TREE-EVIDENCE.md` (6 family rulings) ·
`docs/PARENT-TREE-CANDIDATES.md` (S1–S7 structural, T1/T2 tensions — gate
CDR-02/05/06) · `docs/CDR-PROPOSALS.md` (CDR-02, 04, 06 parked)

### 2f. Reference, read when relevant

`docs/BACKEND-BUILD-PLAN.md` (3.1–3.11) · `docs/SUP-TRIAGE-PROTOCOL.md` (the
`/triage-*` skills load it) · `docs/CR-VOCABULARY-AUDIT.md` (ADD-08's §4) ·
`docs/MASTER-HANDOFF.md` + addenda 2/3/4 · `docs/B-CONSOLIDATION-REAUDIT-PACKET.md` ·
`docs/KEYWORD-LEDGER-CANDIDATES.md` · `docs/SESSION-HANDOFF-2026-08-01.md`

By absolute path, deliberately site-resident:
`~/Projects/mtjawnny.github.io/docs/PHASE-2-COMPLETION.md` (correction #4) and
`~/Projects/mtjawnny.github.io/mtg-comprehensive-rules.md`.

---

## 3. What was ratified today — 6 new laws

All recorded in `CODEBOOK-NAMING-GRAMMAR.md`; cited here so a cold session sees
them without hunting.

1. **CDR-09 §12a walk EXECUTED** — 16 counter-homograph renames, name-only.
   33 counter-bearing active axes, now **0 non-conforming**.
2. **`any-damage-to-player` / `any-damage-to-creature`** enter the closed
   DELIVERY vocabulary (§2, CR 120.3). **`combat-` is a RESTRICTION, not
   decoration** — "deals damage to an opponent" makes no combat claim.
3. **Membership is not exclusive** (§1) — a card holds membership on every axis
   it genuinely satisfies: each modal mode, and each facet of one ability.
   Ratifies existing practice: **1,236 of 5,844 carded cards (21.1%) already
   sat on >1 active axis**, up to 5. **Member counts are NOT a partition of the
   corpus** — any consumer assuming one-card-one-home is wrong.
4. **A card does not deliver an ability it CREATES** (§2) — emblem, delayed
   trigger, granted ability, token text. Delivery belongs to the *creating*
   ability. Read *whose* ability it is before reading what it does.
5. **`{T}` in an activated cost is AXIS IDENTITY** (§2) — it caps at once per
   turn. General test: does the distinction change **when/whether** the effect
   happens (split), or only **how much** (parameter)?
6. **`target-color-count`** added to §7's closed stat vocabulary.

---

## 4. Tools built today — all DET, all reusable

| tool | what it does |
|---|---|
| `experiments/foundry_membership_move.py` | **the executor for all ratified codebook surgery.** Spec-driven (`experiments/moves/*.json`): `new_axes`, `renames`, `merges`, `moves`, `adds`, `drops`, `quote_edits`, `definition_edits`. Decides nothing. Gates: source exists + active, every oracle_id really is a member, no double-routing, no collisions, **member conservation derived from the declared ops**, determinism ×2, atomic write with temp re-lint. |
| `experiments/foundry_definition_drift.py` | C1 counter/token (§8 r3) · C2 delivery (§1/§2) · C3 effect (§4). Double-gated on quote AND full oracle text. |
| `experiments/foundry_reaudit.py` | re-audit worklist generator, `--min-members/--max-members`. Auto-flags NO QUOTE, QUOTE NOT VERBATIM, CREATED-ABILITY RISK. Assembles evidence, judges nothing. |
| `experiments/foundry_cdr09_derive.py` | counter-conformance derivation; **encodes §7/batch-5/D12 exemptions with citations** |
| `experiments/foundry_cdr09_walk.py` | the §12a walk executor (spent, kept as record) |

**Standing gates to run before AND after any codebook work:**
`foundry_codebook.py lint` · `foundry_family_sweep.py --strict` ·
`foundry_ruling_registry.py` · `foundry_definition_drift.py`

---

## 5. The next work item: re-audit tier 3

Captain-ordered: *"re-audit each member of each ruling, lowest member count
first."* Tiers 1 (23 axes / 19 reads) and 2 (68 axes / 136 reads) are **done**.

**Tier 3 = 22 axes / 66 member-reads.** Generate with:

```
python3 experiments/foundry_reaudit.py --min-members 3 --max-members 3
```

It now runs with the created-ability flag, the verbatim-quote check and the
repeatability test applied automatically — none of which existed at tier 1.

Defect rates so far, which justify the ordering: **tier 1 needed something on
11 of 19 member-reads; tier 2 on 10 of 68 axes.** One-member axes are where a
single unexamined assignment is the *entire* evidence base.

### Method that worked, and must be repeated

1. Generate the worklist. 2. Read **full oracle text, all faces** for every
flagged member — never a truncated read. 3. `grep -rn '<slug>' docs/` including
`docs/archive/` before calling anything defective. 4. Write a decision packet
with evidence and a recommendation per item. 5. Execute only ratified items
through a declared spec. 6. Re-run all four gates.

---

## 6. Open items

### Needs Captain ruling
- **Garruk, Caller of Beasts** on `cast-trigger-tutor-to-battlefield` and
  **Jace, Cunning Castaway** on `combat-damage-to-player-loot` — both now
  provably wrong under ruling #4, **not yet re-homed.** The 39 ETB drift
  findings are largely the same class.
- **Brandywine Farmer** needs `rule:etb-create-token-food` ratified — it reads
  "enters **or** leaves the battlefield" and holds only the LTB membership.
  Grammar §11 already names this exact card as the one that should have
  self-instantiated.
- **`rule:targets-highest-life-opponent`** — zero members, `source: B-only`,
  no placeholder note. Never evidenced by anything. Kill or seed.
- **Surrakar Spellblade** sits on `combat-damage-to-player-draw` but scales
  with charge counters; §7 wants `-scales-with-charge-counters`.
- 6 sweep blockers (unchanged): 2 family-members-contradict-template, 1
  pattern-misses-cardname-token, 3 ratified-pattern-has-no-axis.
- 6 family rulings, S1–S7, CDR-02/04/06 — see §2e.

### Known technical debt (carried, unchanged)
- **`docs/B-CONSOLIDATION-REAUDIT-LLM-HANDOFF.md` is a PHANTOM** — cited by two
  documents, never existed in git, nowhere on disk. A12's findings survive only
  as summaries.
- **`experiments/foundry_review.html` dark since 2026-07-17.** Handoff-2026-08-02
  called reviving it the highest-leverage unstarted work, because **ratification
  throughput is the bottleneck**. Today confirms that: the constraint all
  session was Captain rulings, not finding-generation.
- **The convergence gate was never instrumented.** `T3-AXIS-FOUNDRY-v3.md` makes
  it the precondition for the full-corpus pass; codebook is v0.7, no record of
  the gate ever being evaluated. Run 1 launched anyway.
- 2a's artifact is stale the moment any further CDR is ruled.

### Explicitly NOT recommended
An **external LLM audit**. Reasons unchanged and strengthened by today: the
ruling corpus is the thing that makes judgments correct here, an outside model
has less access to it than a local session does, the last external re-audit's
deliverable is the phantom above, and it aims findings at a queue whose
bottleneck is ratification.

---

## 7. Standing discipline

- **Read the manifest before working.** §0 is the reason.
- **Halt loudly.** Never guess, never silently skip.
- **Measure, never recall.** Every hand-written number checked today across two
  sessions was wrong in at least one direction.
- **Full oracle text, all faces, always.** Three false findings today came from
  truncated reads; the all-faces rule caught Kytheon.
- **`grep -rn '<slug>' docs/ docs/archive/` before calling anything defective.**
- **A conformance checker is only as good as the set of rulings it encodes.**
  When a check disagrees with a ratified list, suspect the check first.
- **Evidence must prove ITS OWN axis.** A quote that proves the ability does not
  automatically prove every axis that ability satisfies.
- **Provenance must name what actually made the assignment** —
  `captain-cli-<date>` for hand-ratified, never an inherited batch label.
- **Backup law**: timestamped backup to `experiments/out/foundry/backups/`,
  verified by readback, before every codebook mutation. Not optional.
- **Determinism ×2 byte-identical** on every generated artifact.
- **Nothing model-generated is load-bearing without Captain ratification.**
  New vocabulary is a ratification, not a typo fix.
- **Never create, move or delete anything in `mtjawnny.github.io` without
  Captain approving that specific action.**
