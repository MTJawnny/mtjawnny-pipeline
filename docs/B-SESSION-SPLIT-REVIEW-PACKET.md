# B-SESSION-SPLIT REVIEW PACKET — external review briefing (2026-08-01)

> **THIS IS NOT THE A12 EXTERNAL RE-AUDIT PACKET.** The A12 checkpoint
> reviews session 2a's OUTPUT — the classification artifact — which does not
> exist yet. That packet will be `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`,
> assembled after 2a runs. THIS packet is a pre-execution review of the two
> directives that will produce it, plus the state they will run against.
> Reviewing a plan before executing it is cheaper than reviewing its output;
> both are worth doing.

## Part 0 — YOUR ROLE (read before everything else)

You are an independent auditor. You have NO access to the repository —
everything you need is in this packet. Your job is to find what is wrong,
missing, or self-serving, not to validate it.

**Disclosure of a conflict you must weight:** this packet was assembled by
the same AI assistant (Claude, in Claude Code) that wrote the directives you
are reviewing, executed the migration they build on, and proposed the session
split itself. The human operator ("Captain") requested an outside check
because of that. Treat every recommendation as a claim to test.

**Second disclosure, and it matters:** a prior re-audit of this work was run
past Fable 5 — also a Claude model. It reproduced the migration
byte-for-byte and re-derived its provenance by an independent method, and it
caught a real 820-row arithmetic error in the split proposal. But it is
same-family, and its confirmations therefore carry less weight than yours
against correlated blind spots. Findings from that pass are listed in Part 4
so you do not spend effort rediscovering them — **and so you can judge
whether the fixes applied were the right ones.**

**What we want from you:**
1. Is the session split at the right joint? The claim is that everything in
   2a is a decision and everything in 2b is arithmetic. Attack that. Name
   anything in 2a that is actually mechanical, or anything left in 2b that
   requires judgment.
2. Is the closed loop between 2a and 2b sufficient? 2a declares
   `expected_counts`; 2b must reproduce them exactly or halt. Does that
   genuinely fence the failure mode where 2a under-specifies and 2b silently
   decides? What would slip through it?
3. Is the size arithmetic in Part 2 right, and does its conclusion follow?
4. What will hurt at session 3 (apply), at corroboration waves, or at the
   later schema pass, that is cheap to fix now?
5. Anything the assistant should have surfaced and didn't. The Captain has
   caught it before doing analysis-without-solutions. Assume there is more.
6. Rank by severity. Do not pad. If something is sound, say so in one line
   and move on.

**Output format:** ranked findings (severity, claim, evidence from this
packet, recommended change), then an explicit verdict on the split
(APPROVE / APPROVE-WITH-CORRECTIONS / REJECT), then a short overall
assessment.

## Part 1 — PROJECT PRIMER (cold-start context)

The project is the Magic Thesaurus (mtjawnny.com): a deterministic Magic:
The Gathering card-similarity engine over a ~38,233-card corpus (32,557
after a legality gate). Tier 0–2 similarity (same card / same ability / same
wording) is mature. Tier 3 — "same job, different words" — is the open
problem, and the "T3 axis foundry" is the machinery for mining it.

The foundry's central artifact is `codebook.json`: ~455 axis records
(`rule:enters-tapped`, `rule:create-token-treasure`, …), each with a
definition, a status (active / killed / merged / renamed / deferred), and a
membership list of card `oracle_id`s. It is local, gitignored, ~3.4 MB.

Membership arrives three ways, and the distinction is load-bearing:
- **rule-derived** — a ratified deterministic regex pattern ("DET") matched
  the card's oracle text. Full weight, zero tokens.
- **human** — the Captain ratified it during batch triage. Full weight.
- **llm** — a model proposed it ("SYNTH"). Discounted, never gate-bearing.

House discipline, stated because it explains the directives' tone: halt
loudly on any unexpected shape, never guess, never silently skip;
evidence-quote-or-discard on every per-card assignment; fixed seeds and
byte-identical determinism gates on generated artifacts; every scoring
constant is a ratified ruling, not a tuning knob.

## Part 2 — THE SITUATION

**Session 1 (done, 2026-08-01).** `codebook.json` migrated from schema
`foundry-codebook/1` to `/2`. Under /1 an axis's membership was a flat list
of oracle_id strings with no provenance. Under /2 it is a list of member
objects, each carrying a STACK of assertions — one per support event:

```json
{
  "oracle_id": "<uuid>",
  "tier": "provisional",
  "assertions": [
    {"class": "human", "source_ref": "batch-3", "quote": "...",
     "corpus_ref": "2026-07-18", "evidence_status": "quoted"},
    {"class": "llm", "source_ref": "run1", "original_lane": "free",
     "effective_lane": "codebook", "promotion_reason": "exact-active-slug-match",
     "quote": "...", "corpus_ref": "2026-08-01", "evidence_status": "quoted"}
  ]
}
```

Rules: one member record per (axis, oracle_id); assertions are append-merge,
never overwritten; duplicate (class, source_ref) halts; member-level `tier`
present IFF every assertion is llm-class (any human or rule-derived
assertion means full weight, so consensus tier is moot). All 7,699 existing
rows were backfilled with exactly one assertion each — 3,697 rule-derived,
4,002 human. Membership itself provably unchanged: 455/455 id-sets
identical. Gates: independent verifier clean, lint clean, determinism ×2
byte-identical, 19/19 negative tests.

**What remains.** A full-corpus SYNTH run ("run 1", M=1, $57.63 already
spent, 32,557 cards) produced output that has never been written into the
codebook. Consolidating it is the next work. It involves both bulk
membership writes and a set of genuinely contested judgment calls.

**The sizing measurement that drove the split.** The consolidation plan must
enumerate every affected row as a full A1 assertion, quote included:

| | rows |
|---|---|
| codebook-lane additions | 14,255 |
| codebook-lane already-member merges | 1,833 |
| grammar-lane additions | 1,127 |
| grammar-lane merges | 170 |
| R5 exact-match promotions | 141 |
| virtual-node member rows | 607 |
| A15 promotions | 213 |
| **total** | **~18,346** |

Run-1 quotes measured: n=46,999, mean 85 chars, median 77, p90 144. At
~425 B/row that is **~7.8 MB / ~1.95M tokens** — roughly 93× the first audit
packet (79.7 KB). It cannot be externally audited at any sampling rate that
would mean anything, because the bulk is mechanical and the sample would
mostly show you lane-routing arithmetic.

The DECISIONS inside it are far smaller: 95-node classification (607 member
rows), A15's 213, R5's 141, killed-slug routing (2 hits), taxonomy items —
**≈1,000 rows, ~350 KB, ~88K tokens.** That fits in one packet IN FULL, with
no sampling judgment about what to omit.

Hence: extract the judgment into session 2a, audit it whole, freeze it; let
2b expand mechanically afterwards. An adverse finding then invalidates a
small artifact instead of a 7.8 MB one, and `expected_final_counts` — session
3's exact-match gate — gets computed after the decisions are settled rather
than alongside them.

**This amends a ratified ruling.** Amendment A12 fixed a four-session arc
(MIGRATE / PLAN / APPLY / DET-RUN-2). This makes it five. That is itself
something to review: the arc's own discipline says nothing model-generated is
load-bearing without Captain ratification, and this split was model-proposed.

## Part 3 — THE TWO DIRECTIVES (verbatim)

### 3.1 `docs/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md`

<!-- BEGIN VERBATIM 2A -->
# CONSOLIDATION-2A-CLASSIFY-DIRECTIVE — the decisions, alone (session 2a of 5)

ZERO MUTATION, ZERO API SPEND. This session computes and writes ONE
artifact — every consolidation DECISION, and nothing mechanical — then
STOPS. Nothing touches codebook.json or grammars.json.

Governed by B-MIGRATION-DISCOVERY.md §10 (A1–A15) and §9 where unamended.
Supersedes, with CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md, the single-session
CONSOLIDATION-PLAN-DIRECTIVE.md.

**Why this session exists separately.** The full plan enumerates ~18,346
rows at ~425 B each — ~7.8 MB, ~1.95M tokens — because every row carries an
A1 assertion with a quote. That cannot be externally audited at all, at any
sampling rate that would mean anything. The decisions inside it are ~1,000
rows, ~350 KB, ~88K tokens, and CAN be audited whole. So the judgment is
extracted, audited, and frozen FIRST; the mechanical expansion happens once,
afterwards, against an approved decision set. An adverse audit finding then
invalidates a small artifact instead of a 7.8 MB one.

PRECONDITION (verify in the state-check, else HALT): session 1 complete —
codebook.json schema `foundry-codebook/2`, lint clean, independent verifier
clean. Record the live codebook sha256 in the artifact; 2b and session 3
both check against it.

## 1. Inputs

corpus_pass_run1_parsed_final.json · corpus_pass_run1_discovery.json ·
corpus_pass_run1_consolidation_dry_run.json (reference only — recompute,
never trust) · the det_synth check artifact · docs/grammars.json ·
validate_slug.py · the /2 codebook (READ-ONLY, via
foundry_codebook.load_codebook) · gated corpus.

## 2. Build `experiments/out/foundry/corpus_pass_run1_classification.json`

Schema `foundry-consolidation-classification/1`. Deterministic (×2
byte-identical). Records input hashes and the live codebook sha256. Every
decision is enumerated by slug and, where it is a per-card decision, by
oracle_id. No aggregates without their underlying lists.

1. **node_classification** — the 95 grammar virtual-node candidates
   (AG-COUNT-01), each classified into the closed vocabulary:
   `instantiate` / `join-existing` / `redirect` / `report-only` /
   `collision-killed` / `collision-renamed`. Category totals must sum to
   exactly 95. Expected per A14/R7: 93 instantiate; `rule:grants-haste` →
   redirect-per-D4 (Zidane, Tantalus Thief → `rule:temporary-keyword-grant`);
   `rule:draw-second-card-trigger-token` → report-only. Deviations from that
   expectation are allowed but must be stated and justified in the human
   summary — the expectation is a prior, not a gate.

2. **killed_slug_routing** — the `foundry-killed-slug-routing/1` artifact
   (A14/H-02/R10). Every killed-, merged-, or renamed-slug hit enumerated
   with a closed action — `redirect` / `split` / `report` / `discovery` /
   `reject` — and explicit targets. M8-violating combo labels list their
   per-class split targets. NO runtime predicates: no "if the quote fits",
   no similarity thresholds. Every instance is decided HERE, by name.

3. **promotions** —
   - R5: the 141 exact-match free-lane reinventions, split into the 45 new
     members and the 96 already-member merges, each row listed.
   - A15: the 213 rows, EACH re-validated through `validate_slug` exactly as
     a grammar-lane label would be. Rows that fail validation fall back to
     discovery and are listed as such with the failure reason.
     `original_lane` / `effective_lane` recorded per row. The
     `<state>`-placeholder cluster's 10 rows are report-only.

4. **taxonomy_items** — each stated as the EXACT history-entry text 2b will
   emit: revivals entering `deferred` per A2 (never active-at-n=0), the two
   kill-note corrections (R8.4, R8.5), the whole-slug alias per A6
   (`rule:grants-haste-to-token` → `rule:grants-haste-to-created-tokens`;
   NOT a global token→created-tokens synonym, which would corrupt 28 active
   slugs).

5. **same_run_duplicates** — the measured intra-run duplicate emissions
   (run 1: 35 codebook-lane + 3 grammar-lane + 6 free-lane) enumerated by
   (slug, oracle_id), each RESOLVED here per the Captain-ratified collapse
   rule: same-run emissions collapse to a single assertion; lane precedence
   `codebook` > `codebook-grammar` > free-promoted; quote tie-break = first
   in deterministic parse order. Record the winning lane and quote for each.
   This category exists so 2b performs a LOOKUP, never a policy decision —
   it is the one genuine judgment that would otherwise hide inside 2b's
   "mechanical" expansion. Also enumerate any cross-lane same-run pair
   arising from A15 canonical-form promotion (raw-label overlap measured 0;
   canonical-form overlap has never been computed — compute it).

6. **expected_counts** — the closed-loop contract with 2b. Per category:
   how many member_additions, how many assertion_merges, how many new axes,
   how many rows of each promotion type, how many report rows. 2b's
   expansion must reproduce these EXACTLY or halt. This is what makes an
   audit of 2a alone meaningful: a 2b expander bug is otherwise precisely
   the thing an external reviewer of 2a cannot see.

7. **report_rows** — everything deferred to Captain's eyes, with counts and
   the reason each is deferred.

8. **human_summary** — a Captain-readable section INSIDE the artifact:
   category totals, the full 95-node classification table, notable rows, and
   any deviation from the priors in item 1. This section plus the
   enumerations is what the external reviewer reads.

## 3. Reporting and stop

Print counts and slugs only. Quotes go to the artifact, never to console
(A14). Commit the generator script; the artifact itself is gitignored output
— record its sha256 in the report.

Then STOP. In order:

1. Captain reviews the artifact.
2. **A12 EXTERNAL RE-AUDIT CHECKPOINT.** Assemble
   `docs/B-CONSOLIDATION-REAUDIT-PACKET.md`: the amended schema
   (B-MIGRATION-DISCOVERY.md §10 A1) + this artifact's `human_summary` +
   the FULL enumeration of items 1–5 (they fit — that is the point of this
   split) + `expected_counts` + the same red-team charge and disclosure the
   first packet carried. Captain runs it past a DIFFERENT MODEL FAMILY.
   A same-family check does not discharge this.
3. Session 2b runs only on Captain's explicit go, naming the classification
   artifact's sha256 it approves.

Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 4. Standing discipline

Zero mutation of codebook.json/grammars.json under any circumstance · halt
loudly · verify-or-drop · transcript hygiene (quotes to files only) · G1 ·
G4 · determinism ×2 on the artifact · one session, this work item only.
<!-- END VERBATIM 2A -->

### 3.2 `docs/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md`

<!-- BEGIN VERBATIM 2B -->
# CONSOLIDATION-2B-ENUMERATE-DIRECTIVE — the arithmetic, alone (session 2b of 5)

ZERO API SPEND. ZERO MUTATION of codebook.json or grammars.json: this
session writes exactly one artifact, the full consolidation plan. It makes
NO decisions. Every judgment was made and frozen in session 2a.

Governed by B-MIGRATION-DISCOVERY.md §10 (A1–A15) and §9 where unamended.
Supersedes, with CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md, the single-session
CONSOLIDATION-PLAN-DIRECTIVE.md.

PRECONDITIONS (verify all in the state-check, else HALT):
- session 1 complete, codebook.json schema `foundry-codebook/2`, lint clean;
- the live codebook sha256 matches the one 2a recorded — if the codebook has
  moved since 2a classified against it, HALT and re-run 2a rather than
  expanding a decision set made against a different state;
- `corpus_pass_run1_classification.json` exists and its sha256 matches the
  one Captain's go names;
- the A12 external re-audit outcome is recorded, or explicitly waived by
  Captain in writing.

## 1. The one rule

**Anything session 2a did not enumerate DOES NOT HAPPEN.** On encountering
any case 2a's artifact does not resolve — an unclassified node, an
unrouted killed-slug hit, an unresolved same-run duplicate, a promotion row
with no recorded validation outcome — HALT and name it. Do not infer, do not
fall back to a default, do not "route the obvious way." A gap in 2a is a
defect in 2a and is fixed by re-running 2a and re-approving, not by
exercising judgment here. This session's whole value is that it has none.

## 2. Build `experiments/out/foundry/corpus_pass_run1_plan.json`

Schema `foundry-consolidation-plan/1`. Deterministic (×2 byte-identical).
Records input hashes, the 2a artifact's sha256, and the live codebook
sha256 as the plan's recorded pre-state (session 3 checks against it).

Expected scale, for sizing: **~18,346 enumerated rows** = 16,088 codebook
pairs (14,255 additions + 1,833 merges) + 1,297 grammar pairs (1,127 + 170)
+ 141 R5 + 607 virtual-node member rows + 213 A15 rows; ~7.8 MB.

1. **member_additions** — codebook lane (recomputed: expect 14,255 across
   257 axes) + grammar-lane existing axes (expect 1,127 across 20) + the
   virtual nodes' 607 member rows + R5's 45 + A15's promoted rows, each as a
   full A1 assertion: `class=llm`, `source_ref="run1"`, `original_lane` /
   `effective_lane` as 2a recorded them, `quote`, `corpus_ref`,
   `evidence_status`.
2. **assertion_merges** — run-1 confirmations of EXISTING members (expect
   1,833 codebook + 170 grammar + R5's 96): llm assertions to be merged onto
   member records that already exist.
3. **new_axes** — the axis records for 2a's `instantiate` classifications:
   definition, scope, `source="B-only"`, grammar-lane history note, each
   exactly as 2a specified.
4. **promotions / routing / taxonomy** — transcribed from 2a, expanded to
   per-row assertions where the row is a membership row.
5. **expected_final_counts** — the exact post-apply numbers session 3 must
   match: axis counts by status, member rows, assertion rows, per-category
   totals. No "~", no tolerances, no drift categories (A14). Computed HERE,
   after the decisions are frozen, which is what makes them trustworthy as
   session 3's gate.

**Dedupe law.** A (slug, oracle_id) arriving via multiple routes appears
EXACTLY ONCE — in `member_additions` with all its assertions listed, or once
in `assertion_merges` if the member already exists. The plan is internally
duplicate-free by construction and lint-checked for it. Same-run duplicates
are resolved by LOOKUP into 2a's `same_run_duplicates`; encountering one 2a
did not resolve is a halt, per §1.

## 3. Gates

- Every 2a `expected_counts` entry matches the expansion EXACTLY, or halt
  and report the divergence per category. This is the closed loop that makes
  an external audit of 2a alone meaningful.
- Plan is internally duplicate-free.
- No (class, source_ref) pair would collide on merge — dry-check every
  planned merge against the live codebook's existing assertions, since
  `merge_assertion` halts on duplicates and session 3 must not discover that
  mid-apply.
- Determinism ×2, byte-identical.

## 4. Reporting and stop

Print counts only; quotes to the artifact (A14). Commit the expander script;
the plan artifact is gitignored output — record its sha256 in the report.

Then STOP. Session 3 (APPLY, CONSOLIDATION-APPLY-DIRECTIVE.md) runs only on
Captain's explicit go naming the plan sha256 it approves.

Spend $0.00 / cumulative $90.51 / headroom $49.49.

## 5. Standing discipline

Zero judgment · zero mutation of codebook.json/grammars.json · halt loudly ·
transcript hygiene · G1 · G4 · determinism ×2 · one session, this work item
only.
<!-- END VERBATIM 2B -->

## Part 4 — THE PRIOR (SAME-FAMILY) RE-AUDIT'S FINDINGS AND WHAT WAS DONE

Listed so you do not rediscover them, and so you can judge the fixes.

| # | Finding | Fix applied |
|---|---|---|
| F1 | The migration's independent verifier downgraded EVERY quote mismatch to a report row and still printed CLEAN — a bug scrambling hundreds of quotes would have passed. | Hard halt when `corpus_ref` == the current corpus snapshot (the "quote was true then, stale now" carve-out cannot apply when no time has passed). Human rows additionally checked against the claimed batch's own review JSON, not merely the corpus. Declared per-row exemption list. |
| F2 | /2 cannot represent two same-run support events (duplicate `(class, source_ref)` halts), and run 1 contains 35 codebook + 3 grammar + 6 free-lane intra-run duplicate emissions. 2b would have had to invent policy, or session 3 would halt mid-apply. | Captain ratified a collapse rule: same-run emissions collapse to one assertion; lane precedence codebook > codebook-grammar > free-promoted; quote tie-break first-in-parse-order. 2a now RESOLVES each duplicate explicitly so 2b performs a lookup. |
| F3 | The split proposal's row count was wrong by 820 — it omitted the 607 virtual-node member rows and A15's 213. | Corrected to ~18,346 (Part 2 above). Conclusion unchanged and slightly strengthened. |
| F4 | Lint accepted `class=human` + `source_ref=det-patterns-v2:3`, unformatted `corpus_ref`, and an axis status typo (`"actve"`) that would silently remove an axis from every status-partitioned consumer. | Added class↔source_ref family map, date-format check, status vocabulary, `renamed_to`/`merged_into` iff-status + dangling-target, `legacy-captain-seed` iff empty quote. |
| F5 | The verifier pinned `corpus_ref` to today's snapshot — correct while only one snapshot has ever existed, but it would halt on all 7,699 historically-correct rows after the first corpus refresh. | Validates as a date, rejects future-dated refs, reports drift rather than halting on it. |
| F6 | The migration writer read the LIVE codebook for DET slug resolution while migrating a different `--input`. | Fixed. |
| F7 | The 11 `member_additions` rows wear the `legacy-captain-seed` evidence label though they are not captain seeds. | Documented at the vocabulary definition; `source_ref` distinguishes them. Data unchanged. |

**Its SUSPECTED finding, unfixed and worth your attention:** nothing in this
arc would catch corruption of the SOURCE ARTIFACTS themselves after
ratification. The migration manifest hashes them once; nothing re-checks that
manifest later. Both the writer and the verifier treat the DET hit lists and
the batch decisions/review files as ground truth. That is the outer boundary
of what "independent verification" means here.

**A defect found during the same pass, not by the audit:** one axis
(`rule:etb-with-negative-counters`) carried a stale `merged_into` pointer
while `status: active` — merged at batch 5, then re-kept at batches 6 and 7,
because the legacy reconciler's keep path reactivates an axis without
clearing the pointer. Nothing had followed it, but session 2a does extensive
slug routing and would have. Captain ruled to clear it; the legacy producer
was NOT changed, because its replay output is load-bearing for the
migration's byte-reproducibility. It was the only axis with that shape.

## Part 5 — RATIFIED CONSTRAINTS THE DIRECTIVES MUST RESPECT

Abbreviated; these are prior Captain rulings, not open questions. Flag it if
a directive violates one.

- **A1** — the multi-assertion member shape (Part 2). Deterministic order:
  members by oracle_id, assertions by (class, source_ref), fixed key order.
- **A2** — revived axes enter `deferred`, never active-at-n=0. They flip to
  active when their ratified DET pattern lands its first membership.
- **A5** — class = who made the PER-CARD judgment. Batch triage = human.
  Bulk transformation of model output = llm, even when the RULE was
  Captain-ratified. A later Captain confirmation ADDS a human assertion; it
  never rewrites the llm one.
- **A6** — the token→created-tokens synonym is a WHOLE-SLUG alias, not a
  global token map (a global map would corrupt 28 active slugs).
- **A8** — a DET refresh replaces only its own rule-derived assertions and
  never touches a human or llm assertion on the same member.
- **A11** — members hold DIRECT assertions only; parent rollups stay derived
  views.
- **A14** — evidence quotes are NEVER printed to console, only to report
  files. Killed-slug routing is a closed data vocabulary with every instance
  enumerated, no runtime "does the quote fit" judgment. No drift tolerances:
  exact match or halt.
- **A15** — the 213 rows are free-lane labels whose canonical forms match
  ratified closed grammar compositions. Each re-validates through
  `validate_slug` exactly like a grammar-lane label;
  `original_lane="free"` / `effective_lane="codebook-grammar"` preserved.
- **R7** — faceted keyword-grant axes (scope / delivery / context) are
  legitimate; only BARE grant axes are engine-redundant. Bare
  `rule:grants-haste` stays killed and its one member routes to
  `rule:temporary-keyword-grant`.
- **R12** — run-1's already-member confirmations were originally to stay
  no-ops. A1 SUPERSEDES this: they now merge as llm assertions. This
  reversal is deliberate and is one of the things worth checking.
- **Budget** — $140 cumulative ceiling on the arc, $90.51 spent, $49.49
  headroom. Sessions 2a and 2b are $0.00: pure local compute.
