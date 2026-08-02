# B-MIGRATION AUDIT PACKET — external review briefing (2026-08-01)

## Part 0 — YOUR ROLE (read before everything else)

You are an independent auditor. You have NO access to the repository —
everything you need is in this packet, and every source document is
included VERBATIM in Parts 3–6. Your job is to find what is wrong,
missing, or self-serving in the plan below, not to validate it.

**Disclosure of a conflict you must weight:** this packet was assembled by
the same AI assistant (Claude, in Claude Code) whose analysis and
recommendations you are auditing. The human operator ("Captain")
specifically requested an outside check because of that. Treat every
recommendation as a claim to test, not a fact. The assistant's measured
numbers (marked as measured, with file:line pointers) were computed
directly against the live repo; you cannot re-run them, but you CAN check
them for internal consistency — several arithmetic cross-checks are
possible entirely within this packet, and you should do them.

**What we want from you:**
1. A verdict per ratified ruling R1–R13 (Part 5): sound / unsound /
   sound-but-incomplete, with reasoning.
2. A hunt for missed risks: consumers the census could have missed given
   its method, failure modes in the migration/consolidation directives,
   schema-design mistakes that will hurt at the later "schema pass"
   (parent/child trees) or corroboration waves.
3. Specific scrutiny on the judgment calls most likely to be wrong:
   - Promoting free-lane output (the 141 exact-match and 213 reorder
     rows) into codebook membership — is this a violation of the
     lane-discipline principle it claims to respect?
   - Freezing the legacy reconciler instead of migrating it.
   - Carrying evidence quotes (incl. building DET quotes) inside the
     codebook file vs. leaving them in run artifacts.
   - Resolving the grants-haste collision via the "hexproof precedent"
     WITHOUT reversing ruling b1-Q1 — is that reading honest, or is it a
     rationalization that quietly reverses a ratified ruling?
   - The claim that backfill provenance is "100% mechanically derivable."
   - Whether the membership-identity gate + determinism ×2 is sufficient
     verification for the migration.
4. Anything the assistant should have surfaced and didn't. The Captain
   has already caught it once doing analysis-without-solutions (the DET
   quote store had to be suggested by the human). Assume there are more.
5. Rank findings by severity. Do not pad. If something is genuinely
   sound, say so in one line and move on.

**Output format:** ranked findings (severity, claim, evidence from this
packet, recommended change), then the R1–R13 verdict table, then a short
overall assessment.

## Part 1 — PROJECT PRIMER (cold-start context)

The project is the Magic Thesaurus (mtjawnny.com): a deterministic
Magic: The Gathering card-similarity engine over a ~38,233-card corpus
(32,557 after a legality gate). Tier 0–2 similarity (same card / same
ability / same wording) is mature. Tier 3 ("same job, different words",
e.g. Grand Abolisher ↔ Defense Grid) is being built via the "T3 axis
foundry": a human-ratified codebook of ~300 functional axes ("rule:"
tags, e.g. rule:rhystic-tax), each with member cards, mined by a mix of:
- DET: deterministic regex patterns over oracle text (zero AI, ratified
  like constants, re-run on every data refresh),
- SYNTH: an LLM batch pass proposing labels per card in three lanes —
  "codebook" (names an existing axis), "codebook-grammar" (composes a new
  slug from a ratified grammar family), "free" (open discovery),
- SUP/Captain: a human (the Captain) who ratifies everything; nothing
  model-generated is load-bearing without ratification.

Binding house rules (violations are audit findings):
- Halt-loudly: on unexpected data shapes, stop with a plain message;
  never skip silently, never best-guess.
- G1: ratified scoring constants are untouchable by agents.
- G4: never hand-edit generated artifacts — fix the producer, re-run.
- Determinism ×2: generated artifacts must be byte-identical across two
  runs from the same inputs.
- Backup law: timestamped pre-mutation backups of codebook.json.
- Evidence-quote-or-discard: every per-card assignment needs a verbatim
  oracle-text quote.
- Provenance classes (ratified): tagger / rule-derived / human (full
  weight) / llm (discounted, never gate-bearing).
- Lane-aware consensus (ratified 2026-08-01): multi-run intersection
  applies to codebook+grammar lanes only; free-lane output is UNIONED
  into consolidation as discovery candidates, never scored as
  disagreement. At M=1 (single run), all SYNTH memberships are tier
  "provisional" (rank-buried until corroborated by a future run).
- Rank buries, never excludes.
- Cost ceiling: $140 cumulative for this arc; $90.51 spent; every API
  spend needs live pricing + explicit Captain trigger. (All work audited
  here is zero-spend local compute.)
- One Claude Code session per distinct work item.

## Part 2 — THE SITUATION BEING AUDITED

The full-corpus SYNTH run ("run 1", M=1, 32,557 cards, $57.63) completed
2026-08-01. Consolidating its output into codebook.json HALTED because
the file's `member_oracle_ids` is a flat list of bare oracle_id strings
with no field for per-membership provenance (source, consensus tier, run
history), which the lane-aware consensus ruling requires. The Captain
ruled out an additive sidecar (Option A) and chose Option B: migrate
`member_oracle_ids` to a list of objects, everywhere.

What happened next, in order:
1. A zero-mutation DISCOVERY session produced the report in Part 3
   (consumer census, backfill trace, draft schema, migration plan, risk
   register, and answers to standing count questions). The tasking
   directive for that session is included as Part 6 so you can check the
   report against its assignment.
2. A discussion round: the Captain answered the report's 10 open
   questions; several answers triggered deeper analysis (the "hexproof
   precedent" resolving a collision with a killed axis; a "nonsense-rule
   audit" of stale kills; a decision to build stored quotes for DET
   rows). This arc is summarized in the ratification record (Part 3,
   section 9 of the discovery report) — the section 7 VERDICT lines in
   the report are the Captain's raw annotations, preserved as audit
   trail, and section 9 is the authoritative parsed version.
3. Two execution directives were drafted (Parts 4 and 5's companion
   documents): session 1 migrates the schema; session 2 writes run-1's
   consolidation onto it. NEITHER HAS RUN YET — that is why this audit
   is happening now.

Key measured numbers you can cross-check internally:
- codebook.json: 455 axis records (307 active / 75 killed / 45 renamed /
  26 merged / 2 deferred); 442 records carry member lists; 7,699
  membership rows total (3,697 on 39 DET-owned axes; 3,707 on other
  active/deferred axes; 295 audit rows on non-active shells).
- Run-1 output: 46,999 instances over 32,557 cards = 16,195 codebook +
  2,561 grammar + 28,243 free lane. Quote-gate discards 78 (46/8/24 by
  lane). Codebook lane: 16,088 distinct pairs (14,255 new members +
  1,833 already-member) + 2 killed-slug hits + 24 anomalies + 35
  intra-run duplicate emissions. Grammar lane: 1,297 distinct pairs on
  21 existing axes (1,127 new + 170 already) + 607 members across 95 new
  virtual nodes + 646 validator downgrades + 3 duplicates. Free pool:
  28,889 (= 28,219 passing + 646 downgrades + 24 anomalies).
- Post-consolidation projection: ~23,688 membership rows before the
  ratified promotions (+45 exact-match, +213 reorder), file ~0.79 MB →
  ~6.5–7 MB with quotes carried.

The remaining parts are the verbatim source documents.

---

# PART 3 — THE DISCOVERY REPORT + RATIFICATION RECORD (verbatim: docs/B-MIGRATION-DISCOVERY.md)

# B-MIGRATION-DISCOVERY — provenance schema migration, discovery report (2026-08-01)

Produced by B-MIGRATION-DISCOVERY-DIRECTIVE.md. DISCOVERY ONLY — nothing was
mutated this session: no codebook.json write, no schema change, no script
modification, no API spend. Every number below was measured this session
against the live repo state (commit 5a7340e baseline), not recalled.
Nothing in this document is self-ratifying; it is entirely input to
Captain's ruling. Open questions are collected at the end.

Target under evaluation: **Option B** — `member_oracle_ids` migrates from a
flat list of bare oracle_id strings to a list of objects carrying
per-membership provenance, everywhere. (Option A, the additive sidecar, is
already ruled OUT by Captain.)

---

## 0. Headline findings (read this first)

1. **The blast radius is far smaller than feared.** The site repo
   (mtjawnny.github.io) has ZERO codebook consumers (verified by grep over
   *.py/*.js/*.html/*.yml — no hits at all). tier_engine.py, tests/,
   .github/workflows/build.yml, pipeline/, recipes/, tags/: zero codebook
   references. snapshot.py does not pin codebook.json
   (experiments/snapshot.py:45-50 — engine inputs only), so no gate
   byte-compares codebook.json against anything. B is confined to
   `experiments/foundry_*.py` in this repo.
2. **Backfill is 100% mechanically derivable — zero unknown rows.** All
   7,699 existing membership rows trace: 3,697 to the DET pass
   (rule-derived), 3,699 to the batches-1–7 decisions paper trail via
   replay (human), and the final 8 to the committed pay-life rehome script
   (human, Captain-ratified 2026-07-30). No "human-legacy / flag for
   review" bucket is needed. The addendum-3 §10.3 replay machinery IS the
   traceability mechanism — confirmed by actually replaying batches 1–7
   through the real reconciler this session and diffing.
3. **Old tooling fails loudly by accident of Python semantics**: every
   flat-list read site that matters does `set(member_oracle_ids)` — on a
   list of dicts that raises `TypeError: unhashable type: 'dict'`
   immediately. Still recommend an explicit schema check (no consumer
   validates the `"schema"` field today — observation §5.3).
4. **One real landmine found**: 2 of the 95 grammar virtual nodes the
   dry-run would instantiate collide with existing NON-active axis
   records — `rule:grants-haste` (a **killed** axis, b1-Q1 engine-redundancy
   kill, now legally recomposable from the ratified grants-<keyword>
   grammar) and `rule:draw-second-card-trigger-token` (a renamed shell
   still holding 2 legacy audit members). The consolidation script's
   grammar lane only checks `prefixed in active` (foundry_consolidate_run1.py:139)
   — killed/renamed are never checked, unlike the codebook lane. Needs a
   ruling before the consolidation write (Open Question 5).
5. **The §6 count gaps all resolve cleanly** — no data loss anywhere; the
   discrepancies were mixed-quantity arithmetic in the chat-side audit
   plus one genuine numerical coincidence. Full accounting in §6 below.

---

## 1. Consumer census

Method: grep for `member_oracle_ids` and `codebook` across both repos
(code files, skills, CI, tests), then followed indirection (loaders,
functions receiving the loaded dict, artifacts derived from codebook.json).
Every claim below points at file:line.

### 1.1 Call-site table

Operation classes: RS=reads-as-set, IT=iterates, CT=counts(len),
MA=mutates-appends, MR=mutates-removes, SW=serializes-writes.
Adaptation: TRIV=trivial accessor swap, HELP=needs a helper,
STRUCT=structural rework, NONE=survives as-is.

| File / site | Repo | Ops | What breaks under B | Adaptation | Will it run again? |
|---|---|---|---|---|---|
| foundry_reconcile.py:113,156,175,196,225,234 (`sorted(set(entry[...]) \| {...})`), :268-270 (`in` test + `sorted(list+[oid])`), :116,178,240,282-284 (len/report), :294 write | pipeline | RS MA CT SW | `set()` of dicts → TypeError (loud). `in` test compares oid string against objects → silently False → line 270 would append a bare string into an object list (mixed shape) IF it got that far (it won't — the set sites crash first) | STRUCT — or freeze as the /1 legacy producer (see §5.2 simplification 4 / OQ3) | Only if bootstrap resumes or a from-decisions replay is rerun |
| foundry_det_pass.py:200-215 (`cmd_apply`: reads old list, REPLACES `member_oracle_ids`, embeds old list in history note, writes with own `json.dumps(indent=2)`) | pipeline | IT MA(replace) SW | Write path must emit objects; history-note embeds the old member list verbatim (becomes object noise post-B) | HELP — build member objects (class=rule-derived); trim the note format | YES — re-runs on every Scryfall refresh (wrote full-corpus membership 2026-08-01) |
| foundry_gate0_scrub.py:38-55 (iterates members, `cards_all.get(oid)`, reassigns kept list, writes) | pipeline | IT MR SW | `cards_all.get(dict)` → None → every member lands in `missing` → fc.halt (loud, safe failure) | TRIV — iterate `m["oracle_id"]`, keep objects intact | Plausibly (retroactive scrub on future corpus refresh) |
| foundry_consolidate_run1.py:260,281 (`set(result["active"][slug].get("member_oracle_ids", []))` for new/already split) | pipeline | RS | TypeError on set-of-dicts | TRIV — id-set accessor | YES — its successor performs the actual consolidation write |
| foundry_axis_walk.py:183 (`len(e.get("member_oracle_ids") or [])`) | pipeline | CT | Nothing — len() survives | NONE | Yes (walk tooling) |
| foundry_det_patterns_probe.py:224,250 (len) | pipeline | CT | Nothing | NONE | Yes |
| foundry_stage1b.py:92-111 (`load_codebook_reference` — status/definition only), :146+ (killed slugs by status) | pipeline | other (no member read) | Nothing | NONE | Yes |
| foundry_consolidate.py:182-191 (`load_active_codebook_slugs` — definition/scope/status only) | pipeline | other | Nothing | NONE | Yes |
| validate_slug.py:414-415 (axes keys/definitions for collision checks) | pipeline | other | Nothing | NONE | Yes |
| foundry_corroboration_pass.py (reads run artifacts + DET verdicts, no codebook member reads — verified by grep) | pipeline | other | Nothing today; the FUTURE wave-apply writer must be built on /2 | n/a (build new on /2) | Future |
| foundry_adapt_batch7_decisions.py:90-97 (codebook key-exists lookup for merge targets) | pipeline | other | Nothing | NONE | Historical |
| foundry_batch7_pay_life_scrub.py:79-105 (set ops, add/remove, write) | pipeline | RS MA MR SW | Would crash on set-of-dicts | none — one-off already executed; never re-run | NO (historical) |
| foundry_assemble_batch4/5.py (read member counts for thin-axis targeting) | pipeline | CT | len survives anyway | NONE | NO (historical, batches done) |
| foundry_gate0_scrub one-off aspects, adapt_batch1–6, assemble_batch2/6/7 | pipeline | various | — | none needed | NO (historical) |
| foundry_emit.py, foundry_digest.py, foundry_review.html | pipeline | other | Consume review/decisions/consolidated batch artifacts, NOT codebook.json (verified: no CODEBOOK_PATH/member reads) | NONE | Yes (loop retired, but harmless) |
| .claude/commands/triage-{alpha,beta,emit}.md | pipeline | other | Reference the codebook conceptually; emit drives reconcile → inherits OQ3's answer | follows reconcile decision | Only if bootstrap resumes |
| tests/, .github/workflows/build.yml, pipeline/, experiments/measure/ | pipeline | — | zero codebook references (grep-verified) | NONE | — |
| ../mtjawnny.github.io (entire repo) | site | — | zero codebook references (grep-verified across *.py/*.js/*.html/*.yml) | NONE | — |

Headline counts: 16 distinct consumers examined. Live-and-must-adapt: **4**
(reconcile [or freeze], det_pass, gate0_scrub, consolidate_run1/successor).
Trivial: 2 (gate0_scrub, consolidate_run1). Helper-level: 1 (det_pass).
Structural-or-freeze: 1 (reconcile). Survive untouched: everything else.
Unknown-flagged: 0.

### 1.2 Byte-comparison / determinism / backup surfaces

- Determinism ×2 for codebook writes is performed per-session (run twice
  from the backed-up pre-state, diff) — there is no standing harness that
  byte-compares codebook.json against old snapshots (snapshot.py pins only
  engine inputs, experiments/snapshot.py:45-50). So B invalidates nothing
  standing; the ×2 law simply applies to the migration script itself.
- Backups (`experiments/out/foundry/backups/`, 3 codebook + 2 grammars
  timestamped files) are NEVER machine-restored by any code path
  (grep-verified — snapshot.py's `_pre-restore-backups` is its own
  unrelated mechanism). Restore is manual. Pre-B backups therefore stay
  audit-usable as-is; see §4.4 for the identity-check convention.
- codebook.json is **gitignored** (`.gitignore:6 experiments/out/`) — there
  is no git history safety net; the backup law is the only rollback path.

### 1.3 Adjacent membership-bearing structures — scope recommendation

- `docs/grammars.json` — `instantiated_members` lists AXIS SLUGS, not
  card ids. No card membership. Do not migrate.
- `decisions/batch-N.json` + `review/batch-N.json` (both shapes) — the
  immutable historical paper trail; the spec fixes their schemas; they are
  INPUTS to the provenance backfill. Never migrate.
- `keyword-buckets.json` — keyword taxonomy, no card membership. No.
- `captain_tags_queue.json` — already carries per-entry provenance
  (oracle_id, tag, provenance, queued_at). No change needed.
- Discovery/dry-run/wave artifacts — run outputs, regenerated by their
  producers; already object-shaped where relevant. No.

**Recommendation: B applies to codebook.json only.** No other artifact
carries per-card membership that lacks provenance. Uniform-shape-everywhere
would mean rewriting immutable historical records for no consumer benefit.

---

## 2. Backfill analysis (verified counts)

Current state (measured): 455 axis records; **442 carry
`member_oracle_ids`** — 13 renamed shells have no member field at all
(status/renamed_to/history only). ADDENDUM-4 §6 item 0's "flat list on
every one of the 455 axes (confirmed, 0 exceptions)" is therefore slightly
off: correct statement is "flat list on all 442 records that have the
field; 13 renamed shells carry none." Total membership rows: **7,699**
(7,404 on the 307 active + 2 deferred axes; **295 audit rows** retained on
35 non-active shells — 32 renamed, 2 killed, 1 merged; largest:
rule:creates-creature-token 129).

Method for triage traceability: replayed batches 1→7 through the REAL
`foundry_reconcile.reconcile()` (paths monkeypatched to scratch, zero repo
mutation) from an empty codebook, recording each (slug, oracle_id) pair's
originating batch and pathway, migrating provenance across in-replay
renames, then following the current codebook's post-walk rename chains and
diffing against the live membership.

| Bucket | Rows | Proposed class | Basis |
|---|---|---|---|
| DET-owned axes (39, source="DET") | **3,697** | rule-derived | Exactly matches det_pass_full_hits.json sum (39 patterns, 3,697 hits) — det-patterns-v2, sample-sheet gated |
| Triage-era, decisions-traceable | **3,699** | human | Replay of decisions/batch-{1..7}.foundry-decisions-v1.json: 3,641 via keep/defer/merge/rename unions, 47 via captain_axes seed_members, 11 via member_additions |
| Pay-life rehome additions | **8** | human | The ONLY rows with no decisions-file trail. Exactly the batch7_pay_life_scrub_report.json additions (Captain-ratified 2026-07-30; committed script + report = paper trail). 6 axes: fixed-lifegain 3, rhystic-tax 1, mass-damage-creatures-and-players 1, graveyard-to-library-shuffle-in 1, draw-cards-with-life-loss-cost 1, activated-loot 1 |
| Non-active shells (audit rows) | 295 | human (same replay map, under original slugs) | Retained-by-design audit copies from rename/kill flows |
| **Total** | **7,699** | | 3,697 + 3,707 + 295 = 7,699 ✓ |

Findings:

- **The untraceable remainder is 8 rows, and all 8 are traceable anyway** —
  just via a committed script instead of a decisions file. There is no
  genuine "unknown provenance" row in the codebook. Proposed disposition:
  class=human, batch=7 (the scrub logged against batch-7 history by
  design). No review-flag bucket required.
- **Replay machinery = free backfill: CONFIRMED by measurement**, with two
  supplements: (a) the pay-life report supplies the 8, (b) the current
  rename chains (walk ratification) must be followed when mapping replay
  slugs to current slugs — the replay alone reproduces pre-walk naming.
- Captain-authored axes (source=CAPTAIN, 32 records): members arrived via
  captain_axes seeds (47 rows, class human) and subsequent batch unions
  (class human). Derivation-filled axes (targeted-player/planeswalker-
  damage) were populated through later ratified batch keeps — human.
  targeted-battle-damage remains n=0. Grammar virtual-node members are
  run-1 SYNTH output: class llm, tier provisional, runs [run1]; the
  grammar-lane origin is recorded at AXIS level (lane/history), not per
  member.
- Alignment with DERIVED-TAG-LAYER-SPEC's ratified classes: the backfill
  uses exactly {rule-derived, human, llm}. "tagger" is reserved and unused
  in codebook.json (tagger provenance lives in the engine's tag layer, not
  here). Consensus tier is a field WITHIN llm-class entries only — see §3.

---

## 3. Draft schema (for ratification, not implementation)

Top level: `"schema": "foundry-codebook/2"` (from `foundry-codebook/1`).
Member entry — `member_oracle_ids` becomes a list of objects:

```json
{
  "oracle_id": "<uuid>",
  "class": "rule-derived | human | llm",
  "tier": "provisional | corroborated",
  "runs": ["run1"],
  "batch": 3
}
```

| Field | Type | Required | Semantics |
|---|---|---|---|
| oracle_id | str | always | unique within the axis's member list |
| class | str enum | always | ratified provenance class (DERIVED-TAG-LAYER-SPEC): rule-derived = DET pattern (full weight); human = Captain-ratified paper trail (full weight); llm = model-assigned (discounted, never gate-bearing). "tagger" reserved, not used in this file |
| tier | str enum | iff class=llm (forbidden otherwise) | consensus tier per the lane-aware ruling: provisional (M=1 singleton, rank-buries) / corroborated (multi-run agreement). Lives INSIDE llm entries — not a parallel vocabulary |
| runs | list[str] | iff class=llm (optional otherwise) | append-only run history, e.g. ["run1"], later ["run1","wave1"]. For rule-derived optionally carries the det-pass label |
| batch | int\|str | optional | originating triage batch (human) or det-pass label (rule-derived, e.g. "det-pass-1"). Redundant with axis-level history but makes per-member audit O(1) — Captain may drop it (OQ8) |

Examples (realistic, from measured data):

```json
{"oracle_id": "9f6d6a03-...", "class": "rule-derived", "batch": "det-pass-1"}
{"oracle_id": "a49ef21a-...", "class": "human", "batch": 3}
{"oracle_id": "7bf8bb41-...", "class": "llm", "tier": "provisional", "runs": ["run1"]}
```

**Determinism.** Member list sorted by `oracle_id` (measured: all 442
current lists are already sorted — this is the standing norm, including the
DET-pass writes). Keys within each object emitted in the fixed order
(oracle_id, class, tier, runs, batch) — json.dump preserves insertion
order, so the producer constructs dicts in that order; no sort_keys change.
Serialization stays `fc.write_json` (indent=2, ensure_ascii=False, trailing
newline) — foundry_det_pass.py:215 writes with its own equivalent settings
and should be pointed at fc.write_json during adaptation. Determinism ×2
applies to the migration script run twice from the backed-up pre-state.

**Size (measured by full simulation, not estimated).** Current file:
785,747 B. Migration alone (7,699 rows → objects): 1,384,691 B (~1.4 MB,
×1.76). Post-consolidation at full scale (23,686 rows in the simulation —
see the 2-row collision note in §5.1): **4.53 MB** with standard indent=2
multi-line objects; ~2.98 MB if member objects are emitted one-per-line
(custom encoder); 1.60 MB flat-string baseline at the same row count.
Assessment: this is a local, gitignored artifact never shipped to R2 or
embedded in prompts (stage1b embeds definitions only, never members) —
4.5 MB is immaterial. Recommend full-word field names per the ratified
agent-legibility standard; enum codes / short names NOT recommended (they
save ~1.5 MB at a real readability cost). The single-line-member encoder is
available if Captain wants it, at the cost of a custom serializer (one more
determinism surface) — OQ9.

**Versioning / fail-loudly.** Schema string bumps to foundry-codebook/2.
Measured fact: NO current consumer validates the schema string (reconcile's
load_codebook doesn't check; nothing else does). Old tooling meeting /2
fails loudly anyway via `TypeError: unhashable type: 'dict'` at the first
set() call — acceptable but ugly. Recommendation: the accessor helpers
introduced with the migration (§4.1) check `schema == "foundry-codebook/2"`
and fc.halt on mismatch in BOTH directions (new tools refuse /1, giving
the clean loud failure the house style wants).

**Future-proofing check (verify-not-design).** Corroboration waves: append
"wave1" to `runs`, flip `tier` in place — no shape change ✓. Schema pass
parent/child: axis-level fields; member shape untouched ✓. Equivalence map
and resurrection punch items: axis-level operations; member objects carry
enough provenance to survive a move (class/tier/runs travel with the row) ✓.
Multi-run histories: `runs` is append-only ordered ✓. Per-member evidence
quotes were deliberately NOT included — quotes live in the run artifacts
(corpus_pass_run1_parsed_final.json is the quote record); carrying them
would roughly double file size again and put raw oracle text in the
codebook. Flagged as OQ4 rather than silently decided.

---

## 4. Migration mechanics (plan on paper — nothing executed)

### 4.1 Producer-side changes, in order

1. **New: `experiments/foundry_migrate_codebook_v2.py`** — THE migration
   is a script (G4: re-runnable, deterministic, never a hand-edit). Reads:
   codebook.json (/1), decisions/batch-{1..7}.foundry-decisions-v1.json +
   review/batch-{1..7}.json (in-memory replay for the human-class trail),
   det-source markers (source=="DET" on the axis) for rule-derived,
   batch7_pay_life_scrub_report.json for the 8. Writes /2. Contains the
   class-assignment table of §2 as code.
2. **New (same commit): id-set accessor helpers** — either a small
   `foundry_codebook.py` module or additions to foundry_common:
   `load_codebook()` (with schema check), `member_ids(entry) -> list[str]`,
   `member_id_set(entry) -> set[str]`, `add_member(entry, obj)` (sorted
   insert + dup check on oracle_id). This becomes the single load/save
   boundary that doesn't currently exist (§5.2).
3. **Adapt `foundry_consolidate_run1.py`** (2 sites, trivial) and extend it
   into the actual consolidation writer per the halted directive: new
   members as class=llm/tier=provisional/runs=[run1]; virtual-node axes
   created with axis-level lane bookkeeping; collision handling per OQ5;
   exact-match promotion per OQ6.
4. **Adapt `foundry_det_pass.py` apply path** — writes member objects
   (class=rule-derived), preserves llm/human rows? NO: current semantics
   REPLACE the whole list on DET-owned axes (rule-derived supersedes the
   sampling-era set, foundry_det_pass.py:202). Post-B the replacement
   stays total on DET-owned axes (they are DET-owned by definition);
   history-note format trimmed to counts, not the embedded old list.
5. **Adapt `foundry_gate0_scrub.py`** — iterate `m["oracle_id"]` (trivial).
6. **`foundry_reconcile.py`** — per OQ3: either (a) freeze as the /1
   legacy producer and make the migration script a permanent second step
   of the from-decisions rebuild chain (replay → /1 → migrate → /2), or
   (b) migrate its 6 union sites + revival path now. (a) is less work and
   keeps the historical replay bit-faithful; (b) is required only if the
   bootstrap loop ever runs again on /2 directly.

### 4.2 Write sequence (the follow-up session's order of operations)

backup law (timestamped codebook + grammars copies, readback-verified) →
run migration script → integrity checks (§4.3) → determinism ×2 (second
run from the backup, byte-identical) → commit tooling → THEN the run-1
consolidation write lands on /2 (its own backup + ×2 + sanity panel +
dry-run-report correction per the §6 answers below).

**One session or two:** the honest dependency is strict (consolidation
cannot write before migration lands), but migration is independently
verifiable (the §4.3 identity check makes "migration alone changed no
membership" a provable statement) and consolidation carries its own open
rulings (OQ5, OQ6). Per the one-session-per-work-item house style:
**recommend TWO sessions** — migrate+verify+commit, then consolidate on the
new shape. A single combined session is workable if Captain prefers, at
the cost of a bigger blast radius per session.

### 4.3 Post-migration verification (migration session's gates)

- **Membership-identity check:** per axis, the set of oracle_ids extracted
  from the object list is EXACTLY the pre-migration string set (455/455
  records, including shells if OQ2 says migrate them). Zero adds, zero
  drops, zero reorders beyond the already-sorted norm.
- Count checks: 7,699 rows; 455 records; 307 active / 75 killed / 45
  renamed / 26 merged / 2 deferred; class totals exactly §2's table
  (3,697 / 3,699 / 8 / 295).
- Determinism ×2 byte-identical.
- Consumer smoke: axis_walk + det_patterns_probe run clean (len paths);
  stage1b load_codebook_reference output UNCHANGED byte-for-byte (it never
  reads members — this proves the SYNTH prompt is unaffected).
- Pre-B backups stay audit-usable via the id-set convention: compare
  `{slug: sorted(ids)}` extracted from each side (a documented one-liner;
  applies to /1 vs /2 alike). Byte-diff against pre-B backups is
  meaningless post-B by construction — the identity check replaces it.

### 4.4 Rollback

Any failed gate → restore the timestamped pre-migration backup (copy back,
re-verify checksum), fix the producer, re-run. codebook.json is not in git
(.gitignore:6), so the backup IS the rollback path — the backup step must
verify its own readback (size + hash) before the mutation is allowed.

---

## 5. Roadblock hunt + simplification hunt

### 5.1 Roadblocks / risks (ranked)

1. **Virtual-node collisions with non-active slugs (NEW finding).**
   `rule:grants-haste` — dry-run would instantiate it as a grammar virtual
   node (1 member) but it EXISTS as a killed axis (b1-Q1 kill). This is T1
   (keyword-grant tension) surfacing live: a ratified grammar can now
   legally recompose a killed slug. `rule:draw-second-card-trigger-token`
   — instantiation collides with a renamed shell holding 2 audit members
   (naive dict-assign would overwrite them — measured as the 2-row loss in
   the size simulation, 23,686 vs 23,688). Root cause:
   foundry_consolidate_run1.py:139-146 checks only `in active` on the
   grammar lane; killed/merged/renamed go unchecked (the codebook lane
   checks all four, :111-124). Consolidation must add the same checks and
   route per OQ5.
2. **Mixed-shape corruption window.** reconcile's revival path
   (`sorted(set(entry.get("member_oracle_ids", [])) | set(seed_members))`,
   foundry_reconcile.py:225) unions strings into whatever is there; if any
   /1-era tool ever ran against a /2 file past the TypeError sites, a
   mixed string/object list could be written. Mitigation: the schema check
   in the §4.1 accessors (both directions), plus OQ3's freeze decision.
3. **No schema-string validation exists today** — fail-loudly currently
   depends on the TypeError accident. Mitigated by §4.1.
4. **det_pass history notes embed the full old member list** (:207-211) —
   post-B this balloons into object dumps inside notes. Trim to counts at
   adaptation time.
5. **Duplicate emissions must dedupe on (slug, oracle_id) explicitly under
   B.** The /1 shape absorbed run-1's 35 codebook-lane + 3 grammar-lane
   intra-run duplicate emissions silently via set(). Object lists don't
   self-dedupe; add_member's dup check (§4.1) is load-bearing.
6. **codebook.json has no git history** — backup discipline is the entire
   rollback story; the readback-verify step in §4.4 is not optional.
7. Minor data-quality observation: some free-lane labels contain literal
   grammar placeholders (e.g. a cluster canonicalizing to
   `...-<state>-as-long`, 10 rows) — SYNTH occasionally emitted facet
   placeholders verbatim. Discovery-lane only; no action now.

### 5.2 Simplifications (all measured, none assumed)

1. **Site repo / engine / tests / CI: zero consumers.** The migration is
   an experiments/-only event in one repo.
2. **The id-set view IS the compatibility story.** Every live read site
   consumes membership as an id-set or a count — nobody reads order or
   any per-member detail. `member_id_set()` + `len()` covers 100% of
   current read patterns.
3. **Replay = free backfill** (measured 100% coverage, §2).
4. **reconcile can be frozen instead of reworked.** The bootstrap is
   retired; reconcile's only future role is the from-decisions replay,
   which can legitimately produce /1 and hand off to the migration script
   (deterministic chain). This converts the one STRUCT adaptation into a
   no-op — Captain's call (OQ3).
5. **Only 4 scripts need touching at all**; 2 of those are one-line-class
   trivial.

### 5.3 Observations (neither roadblock nor simplification)

- 13 renamed shells carry NO member field (ADDENDUM-4's "455 axes, 0
  exceptions" corrected to "442 records with the field").
- 295 audit rows ride on 35 non-active shells (largest:
  rule:creates-creature-token, 129) — OQ2 decides whether they migrate.
- corpus_pass_run1_wave_targeting.json has no committed producer script
  (built ad-hoc in the run-1 session) — fine for a report artifact, noted
  for the record.
- `"batches_reconciled": [1..7]` and axis-level `source`
  (B-only/CAPTAIN/DET/None ×13) are unaffected by B. The 13 source=None
  records are all renamed shells.

---

## 6. §6 report items (verified numbers; the dry-run report file itself gets corrected at execution time, not now)

Baseline actuals recomputed this session by re-running the classifier
read-only: 46,999 raw instances over 32,557 cards = 16,195 codebook +
2,561 grammar + 28,243 free. Evidence-quote gate discards 78 total: 46
codebook-lane, 8 grammar-lane, 24 free-lane. D-4 rejections: 0.

**(a) The grammar-lane "1,297" — attribution error in the record.**
1,297 is the distinct card+slug pair count on the 21 EXISTING active axes
(1,127 genuinely new + 170 already-member no-ops), NOT the membership of
the 95 new virtual nodes. The 95 new nodes hold **607** distinct members —
the sanity panel's ~607 was correct all along. Full accounting:
2,561 raw − 8 quote-discards = 2,553 processed = 1,297 (existing-axis
pairs) + 607 (new-node members) + 646 (validator downgrades) + 3 (intra-run
duplicate emissions). The "618 instances" figure was an artifact of
subtracting mixed quantities (instances vs distinct pairs). ADDENDUM-4 §6
item 0's "95 new grammar virtual-node axes with 1,297 quote-verified
members" should read "…with 607 quote-verified members"; 1,297 belongs to
the existing-axis grammar confirmations line (whose "1,127" new-member
count was correct).

**(b) Codebook lane 16,149 vs 16,114 — the 35 are intra-run duplicate
emissions.** 16,195 raw − 46 quote-discards = 16,149 processed. Accounted:
16,088 distinct card+slug pairs (14,255 new + 1,833 already-member) + 2
killed-slug hits + 24 unresolved anomalies = 16,114. The remaining 35 =
the same (card, slug) pair emitted more than once within the run,
absorbed by set-dedup. Nothing is missing.

**(c) Free lane 28,889 — a genuine numerical coincidence.** 28,889 =
28,219 free-lane instances passing the quote gate (28,243 − 24 discards)
+ 646 downgrades + 24 folded anomalies. The audit's "28,243 + 646 =
28,889 exactly" happened because the free lane's quote-gate discard count
(24) exactly equals the folded anomaly count (24). The anomalies are in
the pool; 24 different rows fell out of it.

**(2) The 141 exact-match free-lane reinventions: still sitting in
discovery.** The computed dry-run state counts them as a metric
(exact_match_reinvention_count=141) but does NOT promote them — the halted
directive §4's "treat as codebook-lane confirmation on exact
post-canonicalization match" was never implemented in
foundry_consolidate_run1.py (free_pool instances never reach
codebook_all_hits). Measured detail: 141 instances = 141 distinct
(slug, oracle_id) pairs; 96 are already members; **45 would be genuinely
new memberships**; 0 overlap with existing codebook-lane would-adds (no
double-count risk). Needs implementing — or explicitly re-ruling — at
execution time (OQ6).

**(3) Token-multiset reorder measurement (report-only).** Key finding:
`canonicalize_label` ALREADY reorders classified tokens into canonical
slot order (foundry_consolidate.py:139-141), so pure reorderings collapse
at clustering time — the directive's own example pair verifies:
creature-targeted-destruction and targeted-destruction-creature both
canonicalize to the identical string. Residual pure reorderings BEYOND
canonicalization: **0 clusters / 0 rows** (measured against active slugs +
96 enumerable closed grammar compositions, token-sorted both sides).
The real recoverable pools the future ruling would govern:
- 50 clusters / 161 distinct-card rows whose canonical form equals an
  ACTIVE slug's canonical form (the cluster-side view of the 141
  exact-match + 20 canon-near-miss instance metrics).
- **6 clusters / 223 distinct-card rows whose canonical form equals a
  ratified closed grammar composition that is NOT yet an active axis** —
  dominated by targeted-destruction-creature (188 rows), plus
  cant-be-blocked-except-by-count (21), cant-be-blocked-as-long-as-<state>
  (10), etb-create-token-blood (2), activated-tap-opponent-artifact (1),
  etb-create-token-clue (1). These are free-lane emissions that are
  grammar-valid compositions in the wrong word order — a deterministic
  future promotion candidate worth ~384 rows total across both pools.

---

## 7. OPEN QUESTIONS FOR CAPTAIN

1. **Ratify the member-object shape?** Fields oracle_id / class / tier /
   runs / batch as specified in §3 (classes = ratified
   rule-derived/human/llm; tier inside llm only). Evidence: §3.
   VERDICT: Let's discuss the best shape for future forward member object shapes. we want the oracle ID of course. We want the unique tags it's associated with. maybe we have a gamechanger association section so we can easily and more clearly update the gamechanger list. Maybe even a rider that tells whether it's a double faced card or something to help with future doublefaced card discovery 
2. **Do the 295 audit rows on non-active shells migrate too?** Uniform
   shape everywhere (recommended — avoids polymorphic reads) vs leaving
   shells as strings. Evidence: §2, §5.3.
VERDICT: Uuniform shapes everywhere. We'll go with this. explain what we lose from this.
3. **reconcile: freeze as /1 legacy producer (replay chain gains a
   migrate step) or rework its member handling to /2 now?** Freeze is less
   work and keeps historical replay bit-faithful; rework is only needed if
   the bootstrap loop ever runs again. Evidence: §1.1, §4.1 step 6, §5.2.
   VERDICT: freeze as /1 legacy producer We'll go with this. explain what we lose from this.
4. **Per-member evidence quotes: stay in run artifacts (recommended) or
   carried into member objects?** Carrying ≈ doubles file size again and
   puts oracle text in codebook.json. Evidence: §3 future-proofing.
   VERDICT: would this affect the corpus size if we had them carry? sounds like carrying might be better.
5. **Virtual-node collision policy:** rule:grants-haste (killed b1-Q1,
   recomposable from the ratified grants-<keyword> grammar — T1 live) and
   rule:draw-second-card-trigger-token (renamed shell, 2 audit members):
   instantiate / reject / ledger-route? And ratify adding
   killed/merged/renamed checks to the grammar lane. Evidence: §5.1 #1.
   VERDICT: Let it make rule:grants-haste and others like rule:grants-haste-temporary.
6. **The 141 exact-match reinventions (45 genuinely new members):
   implement the halted directive §4's promotion at execution, or re-rule
   them discovery-only?** Evidence: §6 item 2.
   VERDICT: reword this what the hell are the choices?
7. **Migration and consolidation: two sessions (recommended) or one?**
   Evidence: §4.2.
   VERDICT: Two sessions.
8. **Keep the per-member `batch` field (O(1) audit) or drop it (axis-level
   history already exists)?** Evidence: §3 table.
   VERDICT: what are pro's and cons of this?
9. **Accept 4.53 MB multi-line serialization (recommended), or ratify a
   single-line-member custom encoder (~2.98 MB, one more determinism
   surface)?** Evidence: §3 size.
   VERDICT: 4.53 MB multi-line serialization
10. **Correct ADDENDUM-4 §6 item 0's two figures** ("455 axes, 0
    exceptions" → 442 records carry the field; "95 nodes with 1,297
    members" → 607) in the next handoff revision? Evidence: §2, §6(a).
VERDICT: Yes correct it.
---

## 8. PLAIN-LANGUAGE SUMMARY (same content, simpler words — nothing here adds or changes anything above)

**What this was about.** The codebook file lists which cards belong to
each rule. Right now each membership is just a card ID — nothing says WHO
put it there (a human decision, an automatic pattern, or the AI) or how
much we trust it. The new AI full-corpus run can't be merged in until each
membership can carry that "who says so" note. Before changing the file
format, this session mapped out everything that would be affected.

**The good news.**
- Almost nothing uses this file. The website doesn't touch it at all. The
  search engine doesn't touch it. Only a handful of foundry scripts do,
  and most of them only count entries — counting still works fine after
  the change. Only about 4 scripts need edits, and 2 of those are
  one-line fixes.
- Every single one of the 7,699 existing memberships can be labeled
  automatically. We re-ran the historical decision records and matched
  them up: 3,697 came from the automatic pattern matcher, 3,699 from your
  ratified batch reviews, and the last 8 from the pay-life cleanup you
  approved in July. Zero mysteries. No manual review needed.
- Old tools that meet the new format will crash immediately with a clear
  error instead of silently misreading it. That's the failure mode we
  want.

**The catches.**
- Two of the 95 "new" grammar rules the AI run wants to create already
  exist in the file as dead entries — one is a rule you explicitly killed
  back in batch 1 (grants-haste). The merge script doesn't currently
  check for this and could silently resurrect or overwrite them. You need
  to decide what happens there.
- The file will grow from about 0.8 MB to about 4.5 MB. That's fine — it
  never leaves your machine and never goes into AI prompts.
- The file isn't in git, so the timestamped backup taken right before the
  change is the only undo button. The plan double-checks that backup
  before touching anything.

**The count mysteries from the audit — all solved, nothing lost.** The
"1,297 members" figure was a mislabel (it belongs to confirmations of
existing rules; the new rules actually got 607 members). The missing 35
were the AI tagging the same card with the same rule twice in one run —
harmless duplicates. The free-lane numbers lining up "too perfectly" was a
real coincidence: 24 entries were dropped for bad quotes and, separately,
24 different entries were folded in.

**Also found:** 141 cases where the AI reinvented an existing rule's exact
name in the wrong lane are still parked in the discovery pile — the plan
said to count them as confirmations, but that step was never actually
built. 45 of them would be new memberships. And about 380 more rows are
just word-order shuffles of names we already have (like
"creature-targeted-destruction" vs "targeted-destruction-creature") that
a future ruling could recover automatically.

**What happens next (after you rule on the open questions above):** one
session converts the file format and proves nothing changed but the
format; a second session then merges the AI run's results on top. Both
have backups, double-run checks, and a clean undo path.

---

## 9. CAPTAIN RATIFICATION — PARSED DIRECTIVES (2026-08-01)

Authoritative over the §7 prose VERDICT annotations (which stay above as
audit trail), per the standing §10-directives convention. Ratified in chat
2026-08-01 after the discussion round and the nonsense-rule audit.

**R1 — Member object shape (OQ1).** Lean rows:
`{oracle_id, class, tier, runs, batch, quote}` — classes = ratified
rule-derived | human | llm; `tier` (provisional|corroborated) required iff
class=llm, forbidden otherwise; `runs` append-only, required iff class=llm;
`batch` KEPT (OQ8); `quote` present-where-known (see R2). Card-level wants
(card→axes view, DFC flag, gamechanger association) live in a DERIVED
card-index artifact regenerated after every codebook write — never in
membership rows. Gamechanger list's curated home: `tags/gamechangers.yaml`
(in git, human provenance); the card-index surfaces it.

**R2 — Quotes carried, including a BUILT DET quote store (OQ4).** llm rows:
quote from run artifacts. human rows: backfilled from the proposing batch's
review JSON where present (captain-seed rows may lack quotes — allowed).
rule-derived rows: the DET pattern's matched clause, captured at apply time
and regenerated on every DET pass; a one-time read-only backfill fills the
existing 3,697 rows at migration. Projected file ~6.5–7 MB — accepted
(multi-line serialization ratified, OQ9).

**R3 — Uniform shape everywhere (OQ2).** All 442 member-bearing records
migrate, including the 295 audit rows on non-active shells (classes from
the replay map; `status` marks them non-live).

**R4 — reconcile FROZEN as the /1 legacy producer (OQ3).** The migration
script becomes the permanent second step of the from-decisions rebuild
chain (replay → /1 → migrate → /2). A small /2-aware member-add helper is
built in the migration session so hand-ratified additions have a home.
Captain's rebuild-from-scratch alternative was discussed and declined: one
chain link (walk-ratification renames/rewrites, Black Gate move, b7
surgery) is unscripted history, so a ground-up rebuild re-derives truth
with ambiguity; migration re-shapes ratified truth with an identity proof.

**R5 — The 141 exact-match free-lane reinventions PROMOTE (OQ6=A)** as
codebook-lane confirmations: 45 new members (llm, provisional, runs=[run1],
quotes carried), 96 no-ops.

**R6 — Reorder promotion (audit proposal #1, accepted).** Of the 6
free-lane clusters whose canonical form equals a ratified closed grammar
composition: 5 clusters / 213 rows PROMOTE (targeted-destruction-creature
188 → instantiates its virtual node; cant-be-blocked-except-by-count 21 →
instantiates; etb-create-token-blood 2 and etb-create-token-clue 1 → join
their nodes; activated-tap-opponent-artifact 1 → instantiates). The
placeholder-bearing cluster (canonical contains literal `<state>`, 10 rows)
is a REPORT ROW, not promoted. The 161 active-slug near-miss rows stay in
discovery (synonym collapse is involved; the canonicalizer never guesses).

**R7 — OQ5 resolved via the hexproof precedent, ZERO reversal of b1-Q1.**
The ratified pattern: faceted grants (scope/delivery/context) are
legitimate axes; only BARE grants are engine-redundant. Therefore: the 12
faceted grant virtual nodes instantiate normally; bare `rule:grants-haste`
stays killed and its 1 member (Zidane, Tantalus Thief — "gains lifelink and
haste until end of turn") routes to `rule:temporary-keyword-grant` per the
D4 standing rule; the grammar lane gains the killed/merged/renamed checks
the codebook lane already has; `rule:draw-second-card-trigger-token`
(renamed shell, token-payoff member vs plus1-counter rename target) is a
REPORT ROW for Captain at consolidation. T1 stays parked for schema pass.

**R8 — Nonsense-rule audit ratified; Category-2 items 1–5 ALL ALLOWED,**
implementation as recommended:
1. `rule:grants-team-trample` REVIVES (scope-faceted; analogue
   grants-haste-to-your-creatures is active+DET). Revival law applies.
2. `rule:grants-haste-to-reanimated-creature` REVIVES (delivery-context
   grant; analogue grants-haste-to-created-tokens is active+DET n=102).
3. `rule:activated-regenerate-self` AUTHORED properly via the DET path —
   pattern drafted with measured hit list + fixed-seed sample sheet;
   goes live only on Captain's pattern ratification (closes the b3
   "kill, then decompose" debt; regeneration currently has no active home).
4. Cost-shape kill family: the two with live homes
   (sacrifice-self-as-activation-cost ≈ activated-ability-costs-self-
   sacrifice; sacrifice-as-additional-cost ≈ additional-cost-sacrifice-
   permanent) STAY KILLED with kill notes corrected to
   "duplicate-of-live-axis"; the facet children go to the ledger for
   schema pass (D6 follow-up sizing now informed by run-1 data).
5. `rule:grants-haste-to-token`: stays killed; kill note corrected to
   "duplicate of grants-haste-to-created-tokens"; canonicalizer synonym
   token→created-tokens added (R9).
   DET pattern proposals are also drafted for items 1–2 (both are
   template-shaped static grants) so the revived axes don't sit at n=0 —
   same sample-sheet ratification gate as item 3.

**R9 — Canonicalizer synonym additions** exposed by the audit (starting
with token→created-tokens) are ratified like other vocabulary — proposed
with evidence in the consolidation session, applied on approval.

**R10 — Killed-slug routing table** (consolidation must implement; a
killed-slug hit is no longer one thing): duplicate-of-live-axis → confirm
the live axis if the quote fits; M8-violating combo label → split to
per-class tags; temporary grant → temporary-keyword-grant per D4;
mechanism/Alchemy kill → discovery + ledger flag; stale kill (Category 2)
→ report row, never auto-revived.

**R11 — Standing codebook lint** (audit proposal #3): the accessor module
ships invariant checks (schema string, sorted members, no duplicate
oracle_ids, class/tier vocabulary, tier-only-on-llm, quote type) run at
the end of every mutating script.

**R12 — Two sessions (OQ7):** MIGRATE (docs/B-MIGRATION-DIRECTIVE.md) then
CONSOLIDATE (docs/CONSOLIDATION-RUN1-DIRECTIVE-2.md, superseding the
halted §4+ of the original). SYNTH already-member confirmations (1,833
codebook-lane + 170 grammar-lane no-ops) stay no-ops — logged as counts,
flagged as future corroboration-wave input; NOT written into `runs`
without a future ruling (no silent policy invention).

**R13 — Record corrections (OQ10) executed** in this commit set:
ADDENDUM-4 §6 item 0's "455 axes, 0 exceptions" → 442-of-455 phrasing;
"1,297 quote-verified members" on the 95 nodes → 607, with 1,297
reattributed to the existing-axis grammar confirmations.

---

*Session spend: $0.00. Cumulative arc: $90.51. Headroom vs the $140
ceiling: $49.49.*

---

# PART 4 — SESSION-1 DIRECTIVE (verbatim: docs/B-MIGRATION-DIRECTIVE.md)

# B-MIGRATION-DIRECTIVE — codebook /1 → /2 schema migration (session 1 of 2)

Captain-triggered (ratified 2026-08-01, B-MIGRATION-DISCOVERY.md §9 —
rulings cited below as R1–R13). ZERO API SPEND: everything here is local
compute. If any step appears to require spend, that is a HALT, not a
judgment call. This session does the SHAPE migration ONLY — the run-1
consolidation write is session 2 (CONSOLIDATION-RUN1-DIRECTIVE-2.md) and
must NOT run here (R12).

## 0. Orientation reads (in order)

1. docs/B-MIGRATION-DISCOVERY.md — §3 (schema), §2 (backfill classes,
   verified counts), §4 (plan this directive enacts), §9 (ratified rulings)
2. docs/MASTER-HANDOFF.md + ADDENDUM-2 + ADDENDUM-3 + ADDENDUM-4
3. docs/CONSOLIDATION-RUN1-DIRECTIVE.md (context only — do not execute)

Print a state-check first: codebook.json schema/version + record count +
membership-row count (expect foundry-codebook/1, v0.7, 455 records, 7,699
rows), git status clean y/n. Then proceed.

## 1. Build the accessor module (R1, R11)

`experiments/foundry_codebook.py`:
- `load_codebook(path)` — halts unless `schema == "foundry-codebook/2"`
  (plain-English message naming the file's actual schema string).
- `member_ids(entry) -> list[str]`, `member_id_set(entry) -> set[str]`.
- `add_member(entry, obj)` — validates the object (field order oracle_id,
  class, tier, runs, batch, quote; class vocab; tier iff llm), halts on
  duplicate oracle_id, inserts keeping the list sorted by oracle_id.
- `lint(codebook)` — invariants: schema string; every member list sorted;
  no intra-axis duplicate oracle_ids; class ∈ {rule-derived, human, llm};
  tier present iff class=llm; runs list-of-str when present; quote str when
  present. Returns violations; callers halt on any. EVERY mutating script
  ends by running lint (R11).
- A small member-add CLI (`python3 -m foundry_codebook add-member <slug>
  <oracle_id> --class human --batch N [--quote ...]`) — the post-freeze
  home for hand-ratified additions (R4).

## 2. Build the migration script (R1–R4)

`experiments/foundry_migrate_codebook_v2.py` — deterministic, re-runnable,
G4-clean (never hand-edit output). Inputs:
- `experiments/out/foundry/codebook.json` (/1, the truth being re-shaped)
- `decisions/batch-{1..7}.foundry-decisions-v1.json` +
  `review/batch-{1..7}.json` — replayed IN MEMORY through
  foundry_reconcile.reconcile() with paths monkeypatched to a temp dir
  (the discovery session's measured method) to build the (slug, oracle_id)
  → {batch, pathway} provenance map, migrating across in-replay renames,
  then following the live codebook's rename chains
- `experiments/out/foundry/batch7_pay_life_scrub_report.json` (the 8)
- `docs/det-patterns-v2.json` + the corpus via foundry_common (read-only)
  — to regenerate each DET-owned axis's matched clause per member for the
  quote backfill (R2). Reuse the det-pass matching machinery; do not
  re-implement patterns.
- review JSONs again for human-row quote backfill (quote of the proposing
  batch where present; captain-seed rows without quotes stay quoteless)

Class assignment (must reproduce B-MIGRATION-DISCOVERY.md §2 exactly):
DET-owned axes' rows → rule-derived, batch="det-pass-1", quote=matched
clause; decisions-traceable rows → human, batch=originating batch, quote
where recoverable; the pay-life 8 → human, batch=7; the 295 shell rows →
human with replay-map batches (R3). Top-level schema → "foundry-codebook/2".
Axis insertion order preserved byte-for-byte; only member lists change
shape. Output via fc.write_json.

HALT conditions: any current member pair absent from the provenance map
(other than the known 8); any DET member without a pattern match for the
quote backfill (that would contradict det_pass_full_hits.json); any count
diverging from §3's gates.

## 3. Backup law, run, gates

1. Timestamped backups of codebook.json AND grammars.json to backups/,
   readback-verified (size + sha256 printed) BEFORE any write.
2. Run the migration.
3. Gates (all must pass, else restore backup and halt):
   - Membership-identity: per record, id-set exactly equals pre-migration
     (455/455; the 13 field-less shells stay field-less only if R3 review
     says so — R3 says uniform for the 442 member-bearing records; the 13
     empty shells gain nothing).
   - Counts: 7,699 rows; statuses 307/75/45/26/2; class totals
     rule-derived 3,697 / human 4,002 (3,707 active+deferred + 295 shells).
   - Quote coverage report: counts by class; missing-quote rows LISTED
     (expected: captain-seed only), not halted.
   - lint() clean.
   - Determinism ×2: second run from the backup, byte-identical.

## 4. Consumer adaptations (same session, R4/R12)

- `foundry_det_pass.py` apply path: emit member objects (rule-derived +
  matched-clause quote); history note trimmed to counts (no embedded
  member lists); write via fc.write_json; end with lint.
- `foundry_gate0_scrub.py`: iterate `m["oracle_id"]`, preserve objects.
- `foundry_consolidate_run1.py`: the two set() reads swap to
  member_id_set. (Its write extension is SESSION 2 — do not build here.)
- `foundry_reconcile.py`: UNTOUCHED except a top-of-file comment marking
  it the frozen /1 legacy producer and pointing at the migrate script for
  the rebuild chain (R4).
- Smoke checks: axis_walk + det_patterns_probe run clean;
  stage1b.load_codebook_reference() output byte-identical pre/post
  (proves the SYNTH prompt is untouched).

## 5. Documentation + report

- CORPUS-PASS-PLAN.md status: note the schema blocker is CLEARED by this
  session (consolidation itself still pending session 2).
- RESUME-NOTE.md: one line (date + commit).
- Report: gate results, class/quote coverage tables, file size before/
  after, commit hashes, spend $0.00 / cumulative $90.51 / headroom $49.49.
- Commit code + docs (codebook.json itself is gitignored — state its new
  sha256 in the report for the record).

## 6. Standing discipline

Halt loudly · verify-or-drop · transcript hygiene (no oracle text to
console; quotes go in files only) · G1 constants untouchable · G4 no
hand-edits · determinism ×2 · pre-mutation backups · one session, this
work item only. Continue through all phases — stop only on genuine
ambiguity, a failed gate, or an unspecified decision.

---

# PART 5 — SESSION-2 DIRECTIVE (verbatim: docs/CONSOLIDATION-RUN1-DIRECTIVE-2.md)

# CONSOLIDATION-RUN1-DIRECTIVE-2 — run-1 consolidation on the /2 schema (session 2 of 2)

Supersedes docs/CONSOLIDATION-RUN1-DIRECTIVE.md §4 onward where they
differ; its §0–§3 orientation, input verification, and backup law carry
over unchanged. Ratified 2026-08-01 (B-MIGRATION-DISCOVERY.md §9, rulings
R1–R13). ZERO API SPEND. PRECONDITION: B-MIGRATION-DIRECTIVE.md completed
with all gates passed (codebook.json is foundry-codebook/2) — verify in
the state-check; if not, HALT.

## 1. Scope

Write run 1's consolidation into the /2 codebook: codebook-lane and
grammar-lane membership, the R5/R6 promotions, the R7 collision handling,
the R8 audit executions, R9 synonym additions, R10 routing, the derived
card-index artifact, and the deferred dry-run-report corrections. Same
out-of-scope list as the original directive (no corroboration run, no
schema pass, no engine changes, no naming-audit execution).

## 2. Lane writes (extends foundry_consolidate_run1.py into the writer)

All SYNTH-added members: `{oracle_id, class:"llm", tier:"provisional",
runs:["run1"], quote:<evidence quote from parsed_final>}` via
foundry_codebook.add_member. Union only — never removal, never overwrite.

- **Codebook lane:** the 14,255 new members across 257 axes (dry-run
  `codebook_lane_would_add`). The 1,833 already-member confirmations stay
  NO-OPS — counted and reported as future corroboration-wave input, NOT
  written into `runs` (R12: no silent policy invention).
- **Grammar lane, existing axes:** the 1,127 new members across 20 axes
  (170 no-ops likewise).
- **Grammar lane, virtual nodes:** add killed/merged/renamed checks to the
  grammar-lane classifier FIRST (R7) — a grammar-valid slug matching a
  non-active record is never silently instantiated or overwritten. Then:
  - 92 clean nodes instantiate (axis record: definition from the dry run,
    source="B-only", lane bookkeeping in history, status active).
  - `rule:grants-haste` (bare, killed): does NOT instantiate (b1-Q1
    stands). Its 1 member (Zidane, Tantalus Thief) routes to
    `rule:temporary-keyword-grant` per D4, with its quote (R7).
  - `rule:draw-second-card-trigger-token` (renamed shell): REPORT ROW —
    print the member's name + quote for Captain; no write.
  - The 12 faceted grants-* nodes are part of the 92 — instantiate
    normally (hexproof precedent, R7).

## 3. Ratified promotions (R5, R6)

- **R5:** the 141 exact-match free-lane reinventions become codebook-lane
  confirmations: 45 new members written (llm/provisional/runs=[run1] +
  quotes), 96 no-ops counted. Axis history notes record
  "free-lane exact-match promotion (R5)".
- **R6:** the 5 reorder clusters / 213 rows promote:
  targeted-destruction-creature (188) instantiates its grammar node;
  cant-be-blocked-except-by-count (21) instantiates;
  activated-tap-opponent-artifact (1) instantiates;
  etb-create-token-blood (2) and etb-create-token-clue (1) join their
  session-2 instantiated nodes. Recompute cluster membership fresh from
  the discovery artifact (do not trust remembered row counts; small
  drift is a report row, large drift is a HALT). The `<state>`-placeholder
  cluster (10 rows) is a REPORT ROW, stays discovery.
- Dedupe: a card arriving via multiple routes (grammar lane + R6, etc.)
  is written once; add_member's duplicate halt enforces it — catch the
  duplicate BEFORE calling (id-set check), count as no-op.

## 4. Audit executions (R8, R9)

1. REVIVE `rule:grants-team-trample` and
   `rule:grants-haste-to-reanimated-creature`: status → active, revival
   history note citing R8 and the hexproof-precedent rationale; membership
   starts at legacy union (both n=0).
2. AUTHOR `rule:activated-regenerate-self` — draft its DET pattern plus
   patterns for the two revived axes above (all three are template-shaped).
   Emit measured hit lists + fixed-seed 20-hit sample sheets to files.
   **STOP for Captain's pattern ratification before any membership from
   these patterns is written** — this session ends with the sheets
   produced, patterns pending; membership lands via a later DET pass run.
3. Kill-note corrections (append-only history entries, R8.4/R8.5):
   sacrifice-self-as-activation-cost and sacrifice-as-additional-cost →
   "duplicate-of-live-axis" (naming the live axis);
   grants-haste-to-token → "duplicate of grants-haste-to-created-tokens".
   Ledger the cost-shape facet children (PARENT-TREE-CANDIDATES.md).
4. R9 synonym additions to the canonicalizer vocabulary (starting
   token→created-tokens), each with a one-line evidence note in the
   report; applied in foundry_consolidate.py's CANONICAL_SYNONYM_MAP.
5. R10 routing table implemented in the killed-slug handler; every routed
   or report-row instance printed as counts + slugs.

## 5. Derived card-index artifact + gamechanger seed (R1)

- `experiments/out/foundry/card_axes_index.json`: oracle_id → {axes:
  [slugs], dfc: bool (card_faces[0].image_uris rule — the locked DFC
  rule, derived fresh from the corpus), gamechanger: bool}. Regenerated
  deterministically; documented as a derived view (never hand-edited,
  never authoritative).
- Seed `tags/gamechangers.yaml` (in git): format spec + empty list for
  Captain to fill; the index reads it if present.

## 6. Integrity, sanity, reporting

- Backup law before mutation; determinism ×2 on the full consolidation
  (byte-identical codebook + artifacts); lint() at the end of every
  mutating step; Gate #0 on any corpus probe.
- Sanity panel: active axis count before/after (delta = instantiated
  nodes + 2 revivals only), membership rows before/after (expect
  ~7,699 → ~23,9xx; print exact), top-10 axes by added members, no-op
  counts, routing/report-row counts.
- Correct the dry-run report file's figures per B-MIGRATION-DISCOVERY.md
  §6 (the deferred correction) and update CORPUS-PASS-PLAN.md step 6 to
  consolidated; RESUME-NOTE.md one line.
- Report per standing format incl. spend $0.00 / cumulative $90.51 /
  headroom $49.49, commit hashes, codebook sha256.

## 7. Standing discipline

Unchanged from the original directive §10: halt loudly on genuine
ambiguity · verify-or-drop · transcript hygiene (quotes in files, never
console) · G1 · G4 · pre-mutation backups · one session, this work item
only. The corroboration wave remains a FUTURE Captain trigger.

---

# PART 6 — THE ORIGINAL DISCOVERY TASKING (verbatim: docs/B-MIGRATION-DISCOVERY-DIRECTIVE.md) — audit the report against this assignment

# B-MIGRATION-DISCOVERY-DIRECTIVE — provenance schema migration, discovery pass (2026-08-01)

DISCOVERY ONLY. This session MUTATES NOTHING: no codebook.json write, no
schema change, no consolidation write, no script modification, no API spend.
The only files this session creates are its own output documents (§7). If any
step appears to require a mutation or a spend, that is a HALT, not a judgment
call.

## 0. Context (read first)

1. docs/MASTER-HANDOFF.md
2. docs/MASTER-HANDOFF-ADDENDUM-2.md
3. docs/MASTER-HANDOFF-ADDENDUM-3.md
4. docs/MASTER-HANDOFF-ADDENDUM-4.md (§4 lane-aware consensus ruling, §6
   item 0 — the schema-gap HALT this session exists to resolve)
5. docs/CORPUS-PASS-PLAN.md
6. docs/CONSOLIDATION-RUN1-DIRECTIVE.md (the halted directive)
7. The blocked dry-run report from commit 5a7340e (locate it in the repo)
8. docs/DERIVED-TAG-LAYER-SPEC.md — specifically the ratified provenance
   classes: tagger / rule-derived / human (full weight) / llm (discounted,
   never gate-bearing)

Situation in one paragraph: the run-1 consolidation HALTED because
codebook.json's `member_oracle_ids` is a flat list of bare oracle_id strings
(455 axes, 0 exceptions) with no field to carry per-membership provenance
(source, consensus tier, run history), which the lane-aware consensus ruling
requires. Captain has ruled OUT the additive-sidecar bridge (Option A) as
wasted tokens. The target is Option B: `member_oracle_ids` becomes a list of
objects (shape to be ratified) everywhere. This session's job is to make
that migration fully known before a single line changes: every consumer,
every backfill question, every hidden roadblock, every simplification the
codebase might be hiding. All questions answered BEFORE execution.

## 1. Consumer census (the core deliverable)

Find EVERY read and write of `member_oracle_ids` — and every code path that
consumes codebook.json at all, since B changes the file's shape — across
BOTH repos: this one (mtjawnny-pipeline) and ../mtjawnny.github.io. Grep is
the start, not the finish: follow indirection (functions that receive the
loaded dict, scripts that shell out, anything deserializing codebook.json or
artifacts derived from it).

For each call site, record in a table:
- File, function/line, repo
- Operation class: reads-as-set / iterates / counts (len) / mutates-appends /
  mutates-removes / serializes-writes / diffs-or-compares / other (describe)
- What breaks under B (list-of-strings → list-of-objects), precisely:
  set-union on dicts fails, `in` membership tests change semantics, len()
  survives, JSON diff tooling, etc.
- Adaptation shape: trivial accessor swap / needs a helper (e.g. a
  members_as_id_set(axis) accessor) / structural rework / unknown-flag-it

Do not forget the quiet consumers — check explicitly, each is a known or
likely reader:
- foundry_reconcile.py (set-union logic; the rename-bug fix and the b7
  revival-UNIONS-legacy-members law both live here)
- The DET pass apply path (foundry_det_pass.py) — it WROTE full-corpus
  membership on 2026-08-01; it will write again on every Scryfall refresh
- foundry_consolidate.py and the new consolidation script from 5a7340e
- Gates / validation suite / determinism-×2 harness — anything that
  byte-compares or structurally diffs codebook.json against backups or
  snapshots (B invalidates byte-comparison against pre-B backups; how do
  the gates handle that?)
- gate0 scrub tooling, foundry_axis_walk.py, validate_slug-adjacent tooling
- Any viewer/export JSON generation, the resolver, anything in the site repo
  that transitively consumes codebook-derived artifacts
- Tests, CI workflows, ad-hoc scripts in experiments/
- Backup/restore conventions (are backups ever machine-restored by code that
  assumes the old shape?)

Also census the ADJACENT membership-bearing structures so B is defined
consistently: do grammars.json, decisions/batch-N.json, keyword-buckets.json,
or any other artifact carry member lists that should (or should not) migrate
to the same shape? Recommend scope: codebook.json only vs. uniform shape
everywhere, with reasons.

## 2. Backfill analysis (what provenance do the existing 7,699 rows get)

B forces an answer for every existing member at migration time. Map what is
mechanically derivable, with verified counts:
- DET-owned axes (39, det-patterns-v2.json): members → source=rule-derived,
  full weight. Count them.
- Triage-era members: can each be traced to its originating batch via
  decisions/batch-N.json files (batches 1–7)? If yes → source=human
  (Captain-ratified), runs/batch recorded. Report the traceable count and,
  critically, the UNTRACEABLE remainder (members in codebook.json with no
  decisions-file paper trail) — list count per axis for the remainder and
  propose disposition options (e.g. source=human-legacy vs. flag for review).
  Recall the addendum-3 §10.3 full-replay: codebook.json was rebuilt by
  replaying batches 1→5 through the fixed reconciler — that replay machinery
  may BE the traceability mechanism; assess.
- Captain-authored axes' members, derivation-filled members (e.g. the
  targeted-player/planeswalker/battle-damage fills), grammar
  virtual-node members: where do they land in the class vocabulary?
- Alignment requirement: the source vocabulary must map onto
  DERIVED-TAG-LAYER-SPEC's ratified classes (tagger / rule-derived / human /
  llm), with the provisional/corroborated consensus tier as a field WITHIN
  llm-class entries — not a parallel vocabulary. Propose the exact field
  spec under this constraint.

## 3. Schema proposal (draft for ratification, not implementation)

Propose the B object shape with exact field names, types, required/optional
status, and 2–3 realistic examples (a DET member, a replayed triage member,
a run-1 provisional SYNTH member). Address explicitly:
- Determinism: canonical sort order for the member list and for keys within
  each object; serialization settings (the determinism-×2 law must keep
  producing byte-identical output post-B)
- Size: measure current codebook.json size; project post-B size with the
  proposed shape at 23,688 membership rows (post-consolidation scale). If
  bloat is material, propose mitigations (short field names, enum codes)
  WITH the readability tradeoff stated — agent-legibility is a ratified
  language standard.
- Versioning: how the file self-identifies as post-B (schema_version field?)
  so old tooling fails loudly instead of misreading.
- Future-proofing against known upcoming needs, so B is done ONCE: multi-run
  histories (runs=[run1, wave1, ...]), corroborated-tier upgrades in place,
  the schema pass's parent/child structure, and the equivalence-map and
  resurrection punch items. Do not design those features — just verify the
  shape doesn't foreclose them.

## 4. Migration mechanics (plan on paper, execute nothing)

Draft the execution plan the follow-up session would run:
- Producer-side: which scripts must be modified, in what order, so that G4
  (never hand-edit generated artifacts — fix the producer, re-run, diff) is
  satisfied end to end. The migration itself must be a script (re-runnable,
  deterministic), not an edit.
- The write sequence: backup law → migrate → integrity checks → determinism
  ×2 → then the run-1 consolidation write lands ON the new shape. Assess:
  should migration and consolidation be one session or two? (Bias per house
  style: one session per distinct work item — but state the dependency
  honestly.)
- Post-migration verification: membership-identity check (the set of
  oracle_ids per axis is EXACTLY unchanged by migration alone), count
  checks, gate-suite pass, and a defined answer for how pre-B backups remain
  usable for audit.
- Rollback story if a post-migration gate fails.

## 5. Roadblock hunt + simplification hunt (open-ended, this is the point)

Beyond the structured sections: actively look for what the machine is hiding
in both directions.
- Roadblocks: assumptions baked anywhere that membership entries are
  strings (hashing, JSON keys, set literals, sort(), string formatting into
  reports/console), snapshot fixtures with the old shape, anything that
  round-trips membership through a format that can't carry objects.
- Simplifications: is there a cleaner path than anticipated? Examples to
  evaluate honestly (adopt none without evidence): a single load/save module
  boundary that already mediates ALL codebook access (making B a one-file
  change + accessor swaps); the possibility that most consumers only ever
  need the id-set view, making a canonical `members_ids()` accessor the
  entire compatibility story; whether the replay machinery means backfill is
  free.
- Anything found that is NEITHER: report it anyway under "observations."

## 6. Also answer while in there (zero-mutation report items)

1. The dry-run report's count gaps from the chat-side audit — explain with
   verified numbers, correcting the record in THIS session's output doc
   (the dry-run report file itself gets corrected at execution time, not
   now): (a) the grammar-lane "1,297 total members across 95 new nodes"
   figure vs. the arithmetic (2,561 − 1,297 − 646 = 618 instances; sanity
   panel implies ~607 rows) — which number is real; (b) codebook lane
   16,149 vs. accounted 16,114 (35 missing — intra-run duplicates?);
   (c) free lane 28,889 = 28,243 + 646 exactly, so where are the 24 folded
   anomalies.
2. The 141 exact-match free-lane reinventions: confirm current disposition
   in the computed dry-run state (promoted to codebook-lane confirmations
   per the halted directive §4, or still sitting in discovery).
3. Token-multiset reorder measurement (report-only, no promotion): sort each
   free-lane canonical cluster's tokens and match against (active slugs +
   ratified grammar compositions) with tokens sorted likewise. Report how
   many clusters / instances are pure reorderings (the
   creature-targeted-destruction ↔ targeted-destruction-creature case).
   This sizes a future ruling; it changes nothing now.

## 7. Output

Write `docs/B-MIGRATION-DISCOVERY.md` containing: the consumer census table
(§1), backfill analysis with verified counts (§2), the draft schema spec
(§3), the migration plan draft (§4), risk register + simplification findings
(§5), the §6 answers, and — mandatory closing section — **OPEN QUESTIONS FOR
CAPTAIN**: every decision the discovery surfaced that requires a ruling,
each stated as a one-line question with the evidence pointer. Nothing in
this document is self-ratifying; it is entirely input to Captain's ruling.

Commit the document (and nothing else). Report per standing format: census
headline numbers (call sites by operation class, trivial vs. structural
adaptation counts), backfill traceability numbers, projected size delta,
top risks, top simplifications, §6 answers, spend $0.00 / cumulative $90.51
/ headroom $49.49, commit hash.

## 8. Standing discipline

Verify-or-drop (measured numbers only, no recall — every census claim points
at a file:line) · transcript hygiene (no raw oracle text to console) ·
Gate #0 irrelevant here (no corpus probes needed; if one becomes needed,
gate it) · G1 constants untouchable · halt loudly on genuine ambiguity ·
one session, this work item only. Continue through all phases — only stop on
genuine ambiguity or an unspecified decision.

---

# PART 7 — SUPPORTING RULING CONTEXT (verbatim excerpt: the halted consolidation directive's lane-handling section, docs/CONSOLIDATION-RUN1-DIRECTIVE.md sec.4, which session 2 supersedes)

## 4. Lane handling (the core of the session)

**Codebook lane (16,195 labels expected):** each label is a membership
confirmation for an existing active axis. Union the card into that axis's
membership — union only, never removal, never overwrite. Provenance on every
SYNTH-added membership: source=SYNTH, consensus tier=provisional, runs=[run1].
No corroborated tier exists at M=1 — the schema must carry this explicitly
(tier field present, value "provisional"), not omit it. If the codebook.json
membership schema has no provenance/tier field shape to carry this, HALT and
propose a shape — do not invent one silently.

- A codebook-lane label naming a killed or merged slug is a report row
  (count + list), routed per the existing reconcile conventions, never
  silently written.
- A codebook-lane label naming a DET-owned slug should be impossible (strip
  verified, 0 structural violations in the run-1 check). If any appears at
  consolidation time anyway, HALT — that contradicts the run-1 report.

**Codebook-grammar lane (2,561 labels expected):** every label passes through
validate_slug.py. Valid composition against a ratified grammar family →
treated as codebook-lane membership (instantiating the virtual node on first
quote-verified member per the lattice-grammar ruling, lane recorded as
codebook-grammar). Validation failure → downgrade to lane=free per
CODEBOOK-NAMING-GRAMMAR.md sec.11, counted and reported. Any
activation-restriction-family label under ANY lane → reject outright (D-4),
counted and reported. This is the first live full-scale exercise of the
stage1b/consolidate wiring: per ADDENDUM-4 punch item 6, treat anomalies as
HALT rows, not curiosities. Print downgrade and rejection counts.

- Virtual-node instantiation requires the quote-verified member condition:
  the SYNTH output's evidence quote must be present for the instantiating
  member. A grammar-valid slug arriving with no evidence quote does not
  instantiate a node — report row.

**Free lane (28,243 labels expected + any downgrades from above):** NEVER
written to codebook.json as membership. Per the lane-aware ruling, free-lane
output is UNIONED into consolidation as discovery candidates only. Build:

`experiments/out/foundry/corpus_pass_run1_discovery.json` — canonicalized
(canonicalize_label(), the permanent reconcile infra with the mass→mas
stemming fix) label clusters: canonical form, raw variant strings, member
oracle_id count, DF, and a sample of up to 10 member card NAMES (names only —
transcript hygiene applies to the file's console handling, and NO raw oracle
text or SYNTH evidence blobs printed to console at any point; quotes may
live in the artifact file itself).

- The 111 soft DET-convergence flags (free-lane labels matching DET-owned
  pattern names on cards already DET-members): log them in the discovery
  artifact tagged det-convergent. They are corroboration signal for the
  future wave, not membership, not contradiction.
- Free-lane labels matching an ACTIVE codebook slug's exact string (SYNTH
  reinventing a known axis in the free lane): count and report as a
  near-miss metric (this is the lattice-grammar kill-switch metric's
  denominator context), and treat as codebook-lane confirmation ONLY if the
  slug string is an exact match post-canonicalization — anything fuzzier
  stays discovery. Report the count either way.
- Free-lane labels matching a KILLED slug: report row, stays discovery,
  flagged killed-slug-reinvention.

## 5. Determinism and integrity

— END OF PACKET —
