# T3 Buildout — pick up at Step 3

**Paste this to start the next session** (run from `mtjawnny.github.io`,
same as this session — the pipeline work happens cross-repo in
`~/Projects/mtjawnny-pipeline`):

> Read `docs/T3-BUILDOUT-PLAYBOOK.md` and execute Step 3. Read
> `docs/T3-BUILDOUT-STEP3-HANDOFF.md` first for where Steps 1-2 landed.
> Continue through all phases — only stop on genuine ambiguity, a failed
> gate, or an unspecified decision.

## Where things stand

Playbook: `docs/T3-BUILDOUT-PLAYBOOK.md` (Steps 1-9, one step per fresh
session, per its own header).

- **Step 1 — superseded, not literally executed.** Its target punch-list
  fix was already committed before that session started (stale doc, not
  a real gap). What was actually sitting uncommitted was unrelated
  viewer work (`emit_viewer.py`/`viewer.html` card-info expansion, images
  + mana cost/type line/oracle text for anchor/candidate rows) — reviewed,
  smoke-tested, committed at `c53b30d`.
- **Step 2 — done, committed `b5d5e3a`.** Phase A change order: D2
  (n-gram pool-seeding floor raised to `T2_RESCUE_CEILING`), N1
  (keyword-verb-target sentences like "Regenerate target creature." no
  longer swallowed as boilerplate), N2 (self-name substitution no longer
  corrupts a card whose name equals its own keyword-action verb), D1 (new
  permanent gate `check_gn_discovery_superset_gate` / G-N, pool-vs-
  exhaustive-qualification, whole-card + face-scoped). Full gate suite
  green x2 (determinism confirmed), all viewer exports regenerated.
  Full detail: my memory file `project_t3-buildout-progress.md` (auto-
  loaded in this project's Claude Code sessions) has the complete
  per-item verification log if you want it without re-deriving anything.

Pipeline repo (`mtjawnny-pipeline`) `main` is at `b5d5e3a`, pushed is
`26e1166` — 2 commits ahead locally, not pushed (never asked to push).

## Step 3 — what's next

**Read first:** `docs/DERIVED-TAG-LAYER-SPEC.md` ("Lesson 2" + the
architecture section) — before writing anything.

**Task:** implement `score = tagger_coverage + DERIVED_WEIGHT *
derived_agreement`, where `derived_agreement` is the anchor-directional
normalized shared idf over the `rule:` namespace only. `DERIVED_WEIGHT`
is a new ratified constant — **present the proposed 0.5 to Captain for
ratification before writing any code.** `rule:turn-scoped` migrates from
the injected-tag mechanism into the derived term (it's the namespace's
first member); verify Zurgo's T3 spot-check targets are unaffected or
improved.

**Hard requirement:** with no other derivations present, every anchor's
T3 list must be byte-identical OR differ only where the turn-scoped
migration explains it — print the full diff for Captain. Snapshot a
BEFORE panel (Grand Abolisher, Zurgo, Sol Ring, Preordain, Sakura-Tribe
Elder) for Step 5's later gates.

**One gotcha already confirmed this session, worth not re-discovering:**
the engine ALREADY prints a `rule:turn-scoped` derivation block at every
run ("v2.6 amendment 2") — this is the OLD injected-tag mechanism Step 3
is supposed to migrate, not evidence Step 3 is already done. Don't assume
otherwise without checking `tier3_score()` / the tag-injection call sites
directly.

## Standing rules (same as every step)

Halt loudly on ambiguity, verify claims against live code/corpus not
memory, nothing committed without an explicit go-ahead, full gate suite +
determinism x2 + a snapshot after any ruling-affecting change, new
scoring constants are proposed-then-ratified before implementation. See
`docs/T3-BUILDOUT-PLAYBOOK.md`'s own "Standing rules" section for the
complete list.
