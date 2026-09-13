# T3-BUILDOUT-PLAYBOOK — Claude Code Session Guide (Steps 1–9)

How to use this file: run ONE step per Claude Code session in
`~/Projects/mtjawnny-pipeline`, `/clear` between steps. Open each session
with: "Read docs/T3-BUILDOUT-PLAYBOOK.md and execute Step N. Continue
through all phases — only stop on genuine ambiguity, a failed gate, or an
unspecified decision." Reference documents live in `docs/`:
DISCOVERY-RECALL-AUDIT.md, TIER-ENGINE-V3-PROPOSAL.md,
DERIVED-TAG-LAYER-SPEC.md. Read the ones each step names BEFORE writing
anything.

## Standing rules — every session, no exceptions

- Discuss before build; halt loudly on ambiguity, naming the exact problem
  in plain English. Never best-guess, never skip silently.
- Verify before write: claims about engine behavior are checked against
  the live code/corpus, not recalled.
- Nothing is committed without Captain's explicit ask. Ever.
- Every engine change runs the full gate suite plus determinism ×2, and
  ends with a snapshot (constants.json, gates.log, manifest, outputs)
  under `experiments/out/snapshots/<change-name>-v1/`.
- New scoring constants are ratified rulings: proposed value + rationale
  presented to Captain BEFORE implementation, printed in report headers
  after.
- Deviations from this playbook are flagged at the top of the session
  summary, never buried.
- End every step by writing a short completion note the next session can
  read cold: what landed, what's pending, exact flag log.

---

## Step 1 — Commit the sitting punch-list work

Goal: clean base. The granted-keyword pool-seeding fix +
SECOND_CLASS_PHRASE demotion (punch list, final entry) are implemented but
uncommitted.

Tasks: run the full gate suite on the working tree as-is (74/74 default
panel + 37/37 Zurgo/Delney expected), determinism ×2, then present Captain
the diff summary and WAIT for the explicit commit go-ahead. Commit message
cites the punch-list entry.

Stop conditions: any gate not green; any working-tree change beyond the
punch-list entry's own "Files touched" list.

---

## Step 2 — Phase A change order (discovery correctness)

Read first: docs/DISCOVERY-RECALL-AUDIT.md, TIER-ENGINE-V3-PROPOSAL.md
(items D1, D2, N1, N2 only), the punch-list standing-practice header.

Land, in this order, as ONE change order:

1. **D2 — seeding floor alignment.** In `gather_candidate_pool()`, the
   n-gram seeding comparison changes from `args.ngram_df_floor` to
   `T2_RESCUE_CEILING` (the named constant — never a second 172 literal).
   Keyword kinship's floor does NOT change.
2. **N1 — verb-collision fix.** `is_keyword_only_paragraph()` must not
   classify keyword-ACTION instance lines ("Regenerate target creature.")
   as bare boilerplate: a keyword-leading paragraph that continues with a
   real object/clause keeps its full text in matchable_paragraphs.
   Verify Death Ward's matchable_paragraphs is non-empty after.
3. **N2 — self-name/keyword collision.** Self-name substitution skips a
   token when the card's name equals a keyword-action name AND the token
   is in verb position (sentence-initial, followed by a target phrase).
   Verify the card Regenerate's paragraph reads "regenerate target
   creature." not "~ target creature."
4. **D1 — superset gate.** Port docs' audit harness into the gate suite as
   `check_discovery_superset_gate`: fixed panel (Swiftfoot Boots, Dark
   Ritual, Grizzly Bears, Grand Abolisher, Helm of Kaldra, Sol Ring) +
   3 seeded-random rotating anchors; exhaustive assign_tier + tier3
   qualification vs pool diff; zero-miss required; also runs face-scoped
   for 2 fixed face anchors (Stomp face1, Delver face0). The
   granted_keyword_facts post-processing pass is REQUIRED in the harness
   context — see the audit doc's harness-correction section for the trap.
5. Regenerate ALL face exports (emit_viewer) after gates go green.

Verification anchors (present results to Captain): Stomp face1 pool covers
all ~177 qualifiable (was 56); Delver face0 likewise; Bonecrusher
whole-card gains Equal Treatment; Death Ward ↔ Heal the Scars / Refresh /
Regenerate land Tier 1 via the ordinary paragraph path; Swiftfoot Boots ↔
Lightning Greaves unchanged (T2/keyword_grant, byte-identical evidence).

Stop conditions: any pre-existing gate regresses; N1/N2 changes any card
OUTSIDE the keyword-verb collision class (run a corpus-wide
matchable_paragraphs diff and show Captain the full changed-card list —
if it's more than a few dozen cards, halt and present before proceeding).

---

## Step 3 — T3 additive scoring term (ratify BEFORE any tags exist)

Read first: docs/DERIVED-TAG-LAYER-SPEC.md, "Lesson 2" and the
architecture section.

Task: implement `score = tagger_coverage + DERIVED_WEIGHT *
derived_agreement`, where derived_agreement is the anchor-directional
normalized shared idf over the `rule:` namespace only. DERIVED_WEIGHT is a
new ratified constant — present the proposed 0.5 to Captain for
ratification before writing code. `rule:turn-scoped` migrates from the
injected-tag mechanism into the derived term (it is the namespace's first
member); verify Zurgo's T3 spot-check targets are unaffected or improved.

Hard requirement: with no other derivations present, every anchor's T3
list must be byte-identical OR differ only where turn-scoped migration
explains it — print the full diff for Captain. Snapshot a BEFORE panel
(Grand Abolisher, Zurgo, Sol Ring, Preordain, Sakura-Tribe Elder) for
Step 5's gates.

---

## Step 4 — Family-tree evidence audit (Claude Code derives ARGUMENTS; Captain writes rulings against them)

This step produces a document, not code:
`docs/FAMILY-TREE-EVIDENCE.md`. Captain will argue with it and write the
ratified family tree himself. Do NOT propose a final tree — propose
candidate families WITH evidence and counter-arguments.

Read first: docs/DERIVED-TAG-LAYER-SPEC.md (family section, v1 derivation
set), experiments/POKE-PUNCH-LIST.md, tier_engine.py's SELF_CHECK_PAIRS /
gate-card constants, tags/cards.yaml.

Evidence sources — use ALL of them, and label which supports each claim:

1. **Corpus co-occurrence (strongest — compute it, don't recall it).**
   Implement the spec's v1 derivation patterns as a THROWAWAY measurement
   script (experiments/measure/, never wired into scoring): tag the full
   corpus, then compute pairwise co-occurrence and conditional
   probabilities between derived tags, and between derived tags and the
   top-IDF Tagger tags. High mutual co-occurrence between two derived
   tags = evidence they share a family; near-zero = evidence against.
2. **Tagger taxonomy cross-reference.** Which Tagger tags (hate-flash,
   silence, cost-increaser, taxing...) blanket which derived-tag
   populations. Flag explicitly wherever a candidate family merely
   reproduces a Tagger tag — that's an argument the family adds nothing.
3. **Repo history.** Punch-list entries, gate cards, and change-order
   rationales that already argued function-similarity questions (the
   MANA_ONLY_FAMILY retirement, Drannith/Avatar's Wrath, Silence-family
   discussions). Cite entry and date.
4. **Exemplar panels.** For each candidate family: 8–12 canonical member
   cards spanning DIFFERENT templating (both polarities, tax vs
   prohibition, self vs granted), plus 3–5 near-miss cards that look like
   members but Captain may want excluded — these near-misses are what he
   writes rulings against.

Required output structure per candidate family: name; proposed members
(derived tags); the affirmative argument with evidence citations; the
strongest COUNTER-argument (mandatory — no family ships without one);
exemplar panel; near-miss panel; open question phrased as a single ruling
for Captain ("Does rule:uncounterable belong beside
rule:restricts-opponent-cast in resolution-protection — i.e., is Vexing
Shusher kin to Grand Abolisher?").

Candidate families to evaluate at minimum: cast-interference,
resolution-protection, activation-interference, combat-prohibition,
tax-effects (as distinct from hard restriction). Also propose any family
the co-occurrence data surfaces that the spec didn't anticipate.

Guard (important): do not let the Tagger's taxonomy launder itself back
in as "evidence" — corpus behavior and exemplar cards outrank tag
co-occurrence wherever they disagree, and every family needs at least one
argument grounded in card behavior alone.

---

## Step 5 — Land v1 derivations (2–3 per session, repeat until the set is in)

Read first: docs/DERIVED-TAG-LAYER-SPEC.md (v1 set + ritual),
Captain's ratified family tree (from Step 4's aftermath), Step 3's BEFORE
panel snapshot.

Per derivation, the v2.6 ritual verbatim: implement pattern + BOTH
polarities (Lesson 1 — "can't X during Y" ≡ "can X only during Z");
print regex, corpus DF, computed idf, fixed-seed 20-card sample; run the
before/after gate panel; present sample + panel diff; WAIT for Captain's
yes before the next derivation. Family umbrellas emit per the ratified
tree at the inherited discount.

Gate panel (blocking): Grand Abolisher's T3 must contain Defense Grid,
Dosan the Falling Leaf, City of Solitude, and Teferi Time Raveler at or
above their Step 3 BEFORE positions — the additive term makes demotion
impossible by construction, so any demotion is a bug, halt. Determinism
×2. Superset gate (derived tags flow through tag_index seeding
automatically — verify, don't assume).

Suggested landing order (rarest/highest-precision first):
restricts-opponent-cast(+restricts-cast), cost-increase/cost-reduction,
uncounterable(self/granted split), pay-tax, restricts-activation,
prohibits-attack/block, grants-<keyword> (zero new parsing — emitted from
granted_keyword_facts).

---

## Step 6 — Role-2 audit harness (Batch API; model proposes, never writes data)

Read first: docs/DERIVED-TAG-LAYER-SPEC.md (Role 2 + Role 3 mechanics).

Build `experiments/audit_derivations.py`: for each landed derivation,
shard the corpus, submit oracle texts to the Anthropic **Message Batches
API** with the derivation's INTENT as a closed yes/no question, small
model, two-pass self-agreement (disagreement = "uncertain" bucket, never a
verdict), then reconcile model verdicts against the deterministic tags
into exactly three per-derivation reports: MISSED (model yes, regex no),
OVERCAUGHT (model no, regex yes), UNCERTAIN. Include card name, oracle
text, and the model's one-line reason in each row.

Constraints: API key from an env var, key file gitignored (same discipline
as the rclone remote); verify current Batch API pricing/limits from
Anthropic's docs before the first run and print the cost estimate for
Captain's go-ahead; model output NEVER enters any artifact or index — the
only path forward is Captain ratifying a pattern amendment, which goes
back through Step 5's ritual; resumable sharding so a failed batch resumes
rather than restarts.

Captain's loop per derivation: read MISSED and OVERCAUGHT (typically
dozens of rows), ratify amendments or dismiss with a note. Amendments
re-run their ritual; the audit re-runs on amended patterns until both
lists are empty or every remaining row carries a dismissal note.

---

## Step 7 — Derived-layer poke + viewer refresh

Regenerate all viewer exports. Extend anchors.txt with a derived-layer
poke panel: Grand Abolisher, Defense Grid, Vexing Shusher, Silence, Dosan
the Falling Leaf, Rhystic Study, Sphere of Resistance, Drannith
Magistrate, plus one clean granter (Swiftfoot Boots — this also closes the
audit's Finding 3, keyword_grant finally exercised in the viewer). Present
Captain each anchor's new T3 band for eyeball, punch-list style: findings
logged with rulings requested, nothing auto-fixed.

---

## Step 8 — Phase B ratifications (independent track — run whenever)

Read first: docs/TIER-ENGINE-V3-PROPOSAL.md Phase B. One change order:
keyword ledger (`experiments/keyword-ledger.yaml`, loader halts loudly on
unknown fields/names, active entries printed in report headers) with its
six initial entries; F1 shared-subset grant qualification
(Boots↔Greaves must remain byte-identical; Helm of Kaldra ↔ Haunted
Cloak qualifies buried); Q1 instant/sorcery affinity bucket; R1 CI
attenuation (Captain must pick table vs flat CI_PENALTY raise BEFORE
implementation — present both with the Agadeem Fell-the-Profane/
Shatterskull numbers); N3 level-cost second-class pattern. Named
supersessions from the proposal's final section restated in the change
order verbatim.

---

## Step 9 — Phase C + batch precompute (parked until 1–8 are green)

Phase C mechanisms (keyword-set kinship, variable mana parse, numeric
discount, vanilla rank terms, activation-cost facts LAST) one change order
each, per the proposal. Batch precompute remains blocked behind the §8
poke gate as already ruled — Steps 7's derived-layer poke findings fold
into that same gate. Do not start Step 9 sessions until Captain explicitly
reopens it.
