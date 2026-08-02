# CDR PROPOSALS — Captain decision register (rev 2, 2026-08-01)

PROPOSALS ONLY. Nothing here is ratified; nothing has been executed. One
recommendation per decision with the measurement it rests on, so rulings are
made against numbers rather than prose.

**Rev 2 supersedes rev 1 entirely.** Rev 1 was checked by an external audit
(different model family) and by a Fable 5 pass; three of its measured premises
were materially wrong, and two of its "open questions" turned out to be
already settled by the project's own ratified grammar. Both are corrected
below and marked. Rev 1 is in git history.

Provenance of every input: external re-audit
(`docs/B-CONSOLIDATION-REAUDIT-LLM-HANDOFF.md`, verdict NO-GO-AS-WRITTEN),
Fable 5 proposal check, Fable 5 CR vocabulary ingest, Fable 5 counter-homograph
analysis, and this session's own measurements. Every claim below was
independently verified against live repo state before being written here.

---

## 0. Already ruled — no further decision needed

**ADD-01 — the three orphaned DET patterns. CAPTAIN RULED: Option A
(2026-08-01).** `rule:cant-be-blocked-by-power` (57 corpus hits),
`-except-by-count` (10), `-as-long-as-state` (18) are ratified DET patterns
that were never applied, because `foundry_det_pass.load_axis_patterns()`
silently demotes any ratified pattern whose slug is not already an active axis
into the prefilter list. All three get axes via the DET path in session 4,
entering `deferred` per A2 and flipping active when membership lands. Session
2a does NOT instantiate them from llm evidence.

Consequences to carry into execution:
- The 93-node classification must NOT instantiate `rule:cant-be-blocked-by-power`
  (measured: the DET pattern captures 34 of 2a's 44 llm members and finds 23
  cards the model missed).
- The A15 21-row cluster targeting `rule:cant-be-blocked-except-by-count` routes
  to the DET path, not llm instantiation (DET captures only 5 of its 21 rows —
  the cluster is a grab bag; see CDR-02).
- The 10 `by-power` llm-only rows and the 16 A15 rows the pattern misses become
  session-4 sample-sheet input, not blind decisions.
- `load_axis_patterns()` must HALT on a ratified non-prefilter pattern with no
  active axis instead of demoting it. Bug fix, not a ruling.

---

## 1. Resolved without a ruling — the grammar already answers

Both were listed as open questions in rev 1. Fable 5's CR ingest established
that the project's own ratified grammar decides them, and I verified each.

**`destruction` vs `destroy` — PROJECT-GRAMMAR-DERIVABLE.** Grammar §4 lists
`destroy` as the standardized EFFECT verb; `destruction` appears nowhere in
§4. `grammars.json`'s action facet lists `"destruction"` while citing "EFFECT
verbs from sec.4" as its source — the facet contradicts its own stated source.
The validator already enforces the correct answer: `rule:targeted-destruction`
and `rule:mass-creature-destruction` fail it today on exactly this token.
CR 701.8 ("Destroy") corroborates but does not decide. **Answer: `destroy`.
The grammars.json entry is the drifted artifact.**

Rev 1 claimed this was a vocabulary-ratification question and that
`destruction` was "already in live use so probably moot." That was wrong in
the way that matters: it IS in live use, and those live uses are themselves
violations the validator already flags.

**`targeted-<action>-<class>` slot order — PROJECT-GRAMMAR-DERIVABLE.**
Grammar §1 fixes slot order as `[DELIVERY]-[EFFECT]-[OBJECT]`, effect before
object. The family's own declared template says the same. So action-then-class
is ratified: `rule:targeted-bounce-creature` conforms;
`rule:targeted-battle-damage`, `-creature-damage`, `-planeswalker-damage`,
`-player-damage` are the violators. **The correct order is derivable. Whether
to rename four live axes is a migration call — see CDR-08.**

Note the deeper anomaly, recorded not ruled: §6 defines `target` as SCOPE,
which §1 places *after* OBJECT, so `targeted-` as a leading stem is itself
irregular. Q5 parked the token pending a membership check. Whether this family
survives under that stem is a Captain decision, deferred.

---

## 2. Findings that reframed rev 1

**F-A (CORRECTED) — the validator rejects 45% of live axes, and the A15
blocker's premise was false.** 139 of 307 active axes fail `validate_slug`
(132 `unknown_vocabulary`, 16 `cost_law_unverified`, 2 `free_must_be_free`).

Rev 1 said `destruction` was already in live use so the vocabulary question
was moot, and that `except` was genuinely new. **Both halves were wrong.**
`CODEBOOK-NAMING-GRAMMAR.md:328` ratifies the closed restriction vocabulary
`by-color`, `by-power`, `except-by-count`, `as-long-as-<state>`,
`by-controller` — so `except-by-count` was ratified all along; the validator
only ever encoded the stem tokens `{cant, be, blocked}`. And `destruction` is
not ratified vocabulary at all (§1 above). **A15-VOCAB-01 was never a
vocabulary-expansion question. It was validator-vs-grammar-doc drift on one
token and a naming violation on the other.**

**F-B (CORRECTED) — DET-contradiction population is 29, not 6.** Free-lane
promotions bypass the DET-owned guard; so does the **grammar lane**, which rev
1 never measured. Measured: `rule:cant-be-blocked-by-color` +8 and
`rule:cant-be-blocked-by-controller` +15 — 23 member-additions to DET-owned
axes riding inside `grammar_lane_member_additions`, none matched by their
ratified patterns, none routed by any proposal. Plus the 6 free-lane rows rev 1
found. **29 across three lanes.**

**F-C — one contradiction proves a pattern bug, not a model error.**
`rule:forced-attack-each-combat` anchors on the literal `this creature` while
DET preprocessing rewrites self-references to `~` before matching. 8
gate-passing cards systematically missed against 59 members. A separate
canonicalizer gap: short names are derived only by pre-comma split, so "Zurgo
Helmsmasher" never yields "Zurgo". Sweep confirms only one other pattern
anchors this way (`rule:innate-unblockable`, 0 misses today).

**F-D — 2a's existence test used string identity where canonical equivalence
was needed.** Two of the 93 nodes are the same axis as a live active one
(`targeted-damage-creature` ≡ `targeted-creature-damage`;
`targeted-damage-player` ≡ `targeted-player-damage`), and one pair collides
within the 93 (`grants-flying-static-target` ≡ `grants-flying-target-static`).
Bug, not a judgment call. The standing sweep now catches this class.

**F-E (NEW) — vocabulary gaps forced the "semantic incoherence" the external
audit found.** `create-token-<type>` ratifies 11 values; CR 111.10 enumerates
**21** predefined token types. Missing: Map, Junk, Incubator, Shard, Walker,
Vibranium, and seven Role types. The external auditor cited
`rule:create-token-clue` "including Map-token creation" and
`etb-create-token-mana-producing-artifact` "mixing Vibranium and Map" as proof
the nodes were incoherent. Evidence verified — **but a Map token has no valid
slug under the ratified vocabulary, so it is absorbed by the nearest sibling.
The model had nowhere correct to put it.** This reframes part of blocker B-02
from "re-review these nodes" to "complete the vocabulary and re-derive."

**F-F (NEW) — CR keyword actions with heavy corpus support and no axis at
all.** Measured against the gated corpus: `fight` 152 cards, `investigate`
137, `manifest` 68, `amass` 57, `goad` 56, `explore` 54 — zero axes for any of
them in a 455-axis codebook. `investigate` compounds F-E: investigating IS
Clue-token creation, so those 137 cards have been landing in the same
`create-token-clue` node that absorbed the Map tokens. Two independent
vocabulary gaps stacking in one axis.

**F-G (NEW) — the `counter` homograph.** CR 122.1 (game-object marker) vs CR
701.6 (keyword action, "counter target spell"). Of 34 active axes containing
"counter": 8 unambiguously object, 7 unambiguously spell-interaction, **19
indeterminate from the name alone.** Grammar §8 already rules that noun sense
must be typed and verb sense must be `counters-<object>` — but the validator
enforces it only in **final-token** position, so `rule:self-counter-growth` and
`rule:etb-with-counters` pass clean today.

Demonstrated corruption in `canonicalize_label`: `counters` (plural) sits in
EFFECT_VOCAB, `counter` (singular) in the qualifier sets, so the canonicalizer
sorts by grammatical number rather than sense. `rule:counters-target-spell`
(verb) → `counters-spell-target`; `rule:plus1-counters-matter` (noun) →
`counters-plus1-matt`; `rule:activated-counter-target-spell` (verb) →
`activated-spell-target-counter`. **A +1/+1 counter axis canonicalizes with the
same leading token as a counterspell, while two counterspell axes lead with
different tokens.** Zero live collisions today; the forms are corrupted, so the
risk is latent, not absent.

**F-H (NEW) — `exile` is a second homograph.** CR 406 (zone) vs CR 701.13
(action). 11 active axes: 8 action-sense, but `graveyard-to-exile-replacement`
and `cast-from-exile-trigger` are zone-sense and the canonicalizer buckets
`exile` as EFFECT unconditionally. Corpus pressure ongoing: 650 cards use zone
phrasing vs 3,222 action.

---

## CDR-01 — Activation policy for singleton grammar nodes

**Measured.** Of the 93 proposed nodes: **46 have exactly one member (49%)**,
12 have two, 35 have three or more. Largest: 68, 57, 44, 44.

**Recommend: n=1 → `deferred`; n≥2 → `active`, both after semantic review.**
The argument is not thinness of evidence but feedback: `load_codebook_reference()`
embeds every active non-DET axis in every future SYNTH prompt, so a wrong
active singleton does not sit inert — it teaches the next run to reproduce
itself. A2 set this precedent for revived axes; this applies it to identical
evidence strength. Deferred still records the candidate, so nothing is lost and
SYNTH will not re-propose it from scratch.

---

## CDR-02 — A15 cluster disposition (rev 1's framing withdrawn)

**Measured.** The 188-row `targeted-destruction-creature` cluster contains
exile, mass destruction, enchantment destruction, countering and −X/−X. The
21-row `cant-be-blocked-except-by-count` cluster mixes count-, flying-, Wall-,
color-, artifact-, haste- and ownership-based restrictions; its ratified DET
pattern matches only 5 of its 21 rows.

**Recommend: adopt the external auditor's Option D — partition semantically
FIRST.** Rev 1 framed this as vocabulary-vs-fallback; §1 and F-A show that
framing was wrong on both tokens. The real defect is semantic incoherence, and
the vocabulary question mostly dissolves: `destruction` is a naming violation
(use `destroy`), `except-by-count` was ratified all along, and the count subset
belongs to the ratified DET pattern per ADD-01. Most surviving subsets will
route to axes that already exist rather than needing any new name.

**Sequencing correction (Fable 5, accepted):** rev 1 recommended reconciling
the validator with the grammar doc *after* consolidation. That is backwards —
A15 revalidation and grammar-lane validation both run through `validate_slug`,
so re-running 2a before reconciling at least Q8.5 and the
`targeted-destruction-<class>` family reproduces A15-VOCAB-01 verbatim. See
ADD-02.

---

## CDR-03 — R5 revalidation method

**Measured.** 141 rows over 42 distinct axes. 97 target DET-owned axes (91
no-op merges, 6 DET-contradicting additions); 44 target non-DET axes —
**39 additions + 5 merges**, corrected from rev 1's "44 rows to review". 14
rows carry a quote under 25 characters, too short to prove the axis.

**Recommend a three-way split. Human review drops from 141 rows to 39.**

1. **The 6 free-lane + 23 grammar-lane DET contradictions (29 total) →
   DET–SYNTH contradiction review rows.** Not new policy: CORPUS-PASS-PLAN
   lane 3 already ratifies this. For a DET-owned axis the ratified pattern IS
   the deterministic predicate and has already returned a verdict. At least one
   (F-C) proves the pattern wrong rather than the model — exactly the value the
   cross-check exists to produce. Route to session 4.
2. **The 91 no-op merges → proceed.** The card is already a member on
   rule-derived grounds; the llm assertion records independent agreement. Adds
   provenance, changes no membership.
3. **The 39 non-DET additions → human review**, 14 short-quote rows first.

---

## CDR-04 — Duplicate same-run quotes: one assertion or a linked artifact

**Measured.** 44 same-run duplicates; **42 carry genuinely disjoint quotes**
and **zero** are one quote containing the other — complementary evidence, not
restatement. Stone Kavu emits `{R}: ... +1/+0` and `{W}: ... +0/+1`. All 44 are
single-lane, so no mixed-lane collapse exists in run 1.

**Recommend: keep both, inside one assertion, via an additive field.** One run
must count once for consensus; discarding half the evidence is a real loss.
Both hold if the support *event* stays singular while its *evidence* becomes
plural:

```json
{"class": "llm", "source_ref": "run1",
 "original_lane": "codebook", "effective_lane": "codebook",
 "quote": "<precedence-selected — unchanged semantics>",
 "additional_evidence": [{"quote": "...", "raw_label": "...", "parse_index": 124}],
 "corpus_ref": "2026-07-04", "evidence_status": "quoted"}
```

`quote` keeps its meaning and position, so the 7,699 migrated rows are
untouched and `(class, source_ref)` uniqueness — hence tier arithmetic — is
unchanged. **Verified by Fable 5:** `expected_tier()` and `merge_assertion()`
read only class/source_ref/effective_lane, so the claim holds.

**Four integration points rev 1 understated (Fable 5, accepted):** lint has
*two* checks to amend (canonical key order and unknown-key rejection), and the
field's position in `ASSERTION_KEY_ORDER` is part of the byte-identity
guarantee so it must be ratified, not chosen ad hoc; **the A13 verifier's
quote-verbatim validation must extend to `additional_evidence[].quote` or
evidence-quote-or-discard gains an unvalidated side channel**; the sub-object
needs its own lint shape rule and fixed key order; the winner's `parse_index`
is not recorded and losers' lane is not recorded (harmless on single-lane data
— the amendment text should say so).

This is an amendment to ratified A1 and needs ratifying as one.

---

## CDR-05 — Near-duplicate axes: merge, alias, or parent/child

**Two problems; only the second needs a ruling.**

**Bug (no ruling):** `targeted-damage-creature` and `targeted-damage-player`
are canonically identical to live active axes and must not instantiate — they
route as codebook-lane confirmations. `grants-flying-static-target` /
`-target-static` are one slug reordered; one instantiates, the other aliases,
and which is which must be named deterministically in the fix.

**Ruling:** semantic near-duplicates —
`death-trigger-create-token-clue` vs `leaves-battlefield-trigger-create-token-clue`
(death is a *subset* of leaves-battlefield), and `targeted-exile-player` vs
`targeted-exile-player-graveyard` (whose sole evidence is "Exile target
opponent's graveyard", so the unqualified name is simply wrong).

**Recommend:** run the auditor's AG-EQUIV-01 five-test pass over surviving
nodes **after** the semantic repair, not before — repair will dissolve some
pairs on its own. Parent/child relations **recorded but not built**: A11 keeps
rollups derived and the schema pass owns hierarchy. Scope must also include
A15-instantiated axes (`rule:activated-tap-opponent-artifact` and node
`rule:activated-tap-or-untap-opponent-artifact` are sibling single-member axes
created by two routes in one session — neither the B-02 review nor rev 1's
pair list covers them).

---

## CDR-06 — Routing target for temporary multi-keyword grants

**Measured.** `rule:temporary-keyword-grant` is active, 39 members, ratified
definition reads "Grants a target … **a keyword ability**" — singular. Zidane,
Tantalus Thief reads "gains lifelink and haste until end of turn" — two
keywords, one clause.

**Recommend: route as-is, plus a one-line definition amendment** ("a keyword
ability" → "one or more keyword abilities"). The axis's job is duration-scoped
keyword granting; how many keywords one clause grants is a facet of the
instance, not a different job. M8 splitting exists for labels mixing target
*classes*, which this is not, and there are no per-keyword temporary-grant axes
to split into. The definition is ratified text, so the amendment needs your
word.

---

## CDR-07 — Final status of semantically repaired nodes

**Recommend: the CDR-01 rule, applied after repair.** Passes review → active
if n≥2, deferred if n=1. **Fails review → rejected, split, or routed to an
existing axis** per its AG-NODE-01 disposition — never "deferred". Deferred
must mean "real but unproven", never "unsure, parked", or the status becomes a
dumping ground.

---

## CDR-08 (NEW) — Rename the four slot-order violators?

§1 establishes action-then-class is the ratified order, so
`rule:targeted-battle-damage`, `-creature-damage`, `-planeswalker-damage`,
`-player-damage` are violations. The order is derivable; the migration is not.

**Recommend: rename, on the §12 rename ledger, in the same walk as CDR-09.**
Leaving them is what produced the canonical collisions in the first place — two
correct-looking compositions of one concept. Cost: 4 renames, members and
definitions unchanged. Deferring is defensible if you would rather not churn
the registry twice; if so, rule that explicitly so the sweep's blocking finding
can be marked accepted-debt rather than reappearing every run.

---

## CDR-09 (NEW) — The `counter` homograph (F-G)

**Recommend: no new stem and no new vocabulary — enforce the ratified §8
partition and widen it from final-token to whole-slug.** The mechanical rule:

- **Verb sense:** token is `counters` (plural), permitted only as the EFFECT
  stem. Singular `counter` in verb sense banned.
- **Noun sense:** `counter(s)` must be immediately preceded by a type word
  (`plus1`/`minus1`/`charge`/`stun`/`oil`/`energy`/`<name>`) or a §8-sanctioned
  binding shape (`-with-…-counters`, `counter-removal-`). Never bare, anywhere.

**Churn: ~15 of 34 counter axes (~5% of the active codebook).** 3 verb-side
(`activated-counter-target-spell` → `activated-counters-target-spell`, plus
`activated-tax-counter-unless-pays` and `tax-or-counter-spell` — which are also
a near-duplicate pair differing only in delivery, worth resolving together). 9
noun-side that each simply gain `plus1-` (every definition says +1/+1).
Definitions and members unchanged; rides the existing §12 ledger.

**Needs your wording ruling — 3 axes cover ANY counter type and cannot be
typed:** `doubles-counter-placement`, `cleanup-counters-on-leaving-battlefield`,
`counter-removal-as-activation-cost`. Options: ratify `placement`/`distribution`
trailing binders, or an `any-type-` prefix.

---

## CDR-10 (NEW) — The `exile` homograph (F-H)

**Recommend: the same shape as §8, by analogy — zone sense always
prepositionally bound (`from-exile`, `to-exile`, `in-exile`); action sense is
the bare EFFECT stem.** 11 axes affected, 2 clearly zone-sense, 1 straddling.
§8 does not currently cover this, so the binding rule needs ratifying even
though the pattern is derivable by analogy. Low churn, and it forecloses a
homograph that corpus pressure (650 zone-sense cards) will otherwise keep
feeding.

---

## CDR-11 (NEW) — Predestined tags: derive axes from the CR top-down

**This is Captain's own insight, measured.** For the 13 CR token types missing
from the ratified vocabulary, corpus support (gated corpus): Incubator 35,
Junk 15, Map 13, Wicked Role 11, Monster Role 8, Cursed Role 6, Vibranium 5,
Royal Role 5, Sorcerer Role 5, Young Hero Role 5, Walker 3, Shard 2, Virtuous
Role 1. **9 clear ≥5 cards; `Gold` is already ratified at 4, so on the
project's own precedent 11 of 13 qualify. 114 card-instances currently have no
valid slug.**

**Recommend: ratify the CR-enumerable vocabulary completions and derive their
axes mechanically.** Where the CR *closes* a set (token types, counter types,
keyword actions) and corpus support clears a bar, an axis needs no discovery,
no model, and no review — it is enumerable, its membership is regex-derivable,
and it costs $0.00. That inverts the current economics: `create-token-clue` was
a $57.63 SYNTH discovery of a fact sitting in CR 111.10b.

**Where it does NOT apply:** open CR sets. `grants-<keyword>` ranges over ~190
keyword abilities; predestining all yields ~190 mostly-empty axes. The rule is
**predestine where the CR closes the set AND corpus support clears a bar**;
leave the rest to discovery.

**Second-order benefit relevant to the drift problem:** a predestined axis
carries its CR anchor as provenance. Name derived, membership derived, sweep
pass E checks it forever. No hand-maintained copy in the loop, so it cannot
drift.

**Sub-decision:** CR treats the 7 Roles as 7 distinct predefined types. Ratify
7 values or one `role` umbrella?

---

## CDR-12 (NEW) — The CR keyword-action gap (F-F)

`fight` 152, `investigate` 137, `manifest` 68, `amass` 57, `goad` 56, `explore`
54 — all CR 701 keyword actions, none with an axis.

**Recommend: treat as CDR-11's first application after token types.** These are
CR-enumerable, corpus-heavy, and mechanically derivable. `investigate` should
be sequenced first because it compounds F-E: investigating is Clue creation, so
resolving it also cleans `create-token-clue`, which is currently absorbing both
Map tokens and investigate cards.

---

## CDR-13 (NEW) — Homograph Form Ledger; answers Captain's CR-audit question

Full analysis: `docs/CR-VOCABULARY-AUDIT.md`. Verdict **CR-AUDIT-PARTIAL**.

**Measured and verified:** 313 distinct tokens across the 307 active axes —
123 exact CR terms, 45 indirectly CR-anchorable, 84 structural, **61 semantic
coinages the CR can never adjudicate** (`grants`, `pump`, `tutor`, `bounce`).
131 axes carry at least one coinage. So a CR audit was never going to carry the
whole load; "CR audit OR system-unique naming" was a false either/or.

**Recommend: a Homograph Form Ledger — sense-form rules on homograph tokens
only, generalizing the ratified §8 `counter` pattern.** Rejected: mandatory
sense-prefixes (worst churn, breaks the full-word legibility standard), domain
namespaces (makes the canonicalizer harder), and an opaque unique id (the slug
already IS the unique key; a second key invites drift).

**Cost: ~15 renames — all already mandated by CDR-09. The ledger adds ZERO new
churn.** `exile` needs zero renames: verified, the corpus already obeys the
rule (the only two preposition-bound axes are exactly the two zone-sense ones),
so it needs ratifying, not applying. Also needs ~40 lines in `validate_slug.py`
to enforce forms in all positions, and one grammar section.

Two riders:
- **Coinage collision check** — a coinage must not collide with a
  current-or-obsolete CR term in a different sense. Flags exactly 5 tokens
  across 11 axes: `tribal` (CR now says Kindred), `unblockable`, `redirect(s)`,
  `removal`, `alt`. Walk-time rename rulings.
- **CDR-10 folds into this.** The `exile` ruling becomes one ledger row rather
  than a separate decision.

---

## Standing-rule proposals (not per-item decisions)

**NEW-01 — DET-owned guard at the write boundary.** No free-lane or
grammar-lane promotion may add a member to a DET-owned axis; a promotion the
axis's pattern rejects becomes a DET–SYNTH contradiction row. **Fable 5's
amendment, accepted:** implement at the single write boundary
(`merge_assertion` / the session-3 applier) rather than per-lane. Rev 1
re-patched lanes, which is how the grammar lane was missed. Requires ADD-03
first.

**NEW-02 — `rule:forced-attack-each-combat` pattern fix → session 4**, through
the sample-sheet gate. Sweep confirms the wider sweep is already done: only
`rule:innate-unblockable` shares the shape and has 0 misses today. Session-4
patterns must be authored against `det_scan_texts` output (anchor
`(?:this creature|~)`), or the bug re-enters.

**ADD-02 — reconcile `validate_slug` with the grammar doc BEFORE re-running
2a.** At minimum Q8.5's restriction vocabulary and the
`targeted-destruction-<class>` family. Sequencing this after consolidation
reproduces A15-VOCAB-01 verbatim.

**ADD-03 — define "DET-owned" once** (roster ∪ codebook `source=DET`) and move
the guard to the write boundary. Two disagreeing definitions exist today:
`foundry_stage1b.load_det_owned_slugs()` uses the pattern roster, the
consolidation guard uses the codebook marking. The three orphaned patterns
lived exactly in that gap — SYNTH could not see them (roster-stripped) so it
re-invented them in the grammar lane, where the codebook-based guard could not
protect them.

**ADD-04 — enumerate and route the 23 grammar-lane DET contradictions**
alongside CDR-03's 6.

**ADD-05 — AG-EQUIV-01 scope must include A15-instantiated axes** (CDR-05).

**ADD-06 — generated-numbers discipline.** Prose numbers must be pasted from
generator output; generators should print the exact summary block a commit
message will carry. Every audit round of this arc has caught an arithmetic
error, and the sub-mode is always a hand-written restatement drifting from a
correct generated artifact beside it — including a fabricated "0 with differing
quotes" in commit cfc26fa where the artifact says 42.

**ADD-07 (NEW) — every-row-one-disposition count contract.** Adopt the external
auditor's AG-COUNT-01 shape as a named gate. Category-sum totals drop rows that
span two categories: the `grants-haste` row is routing *and* an apply row; the
A15 instantiation is a promotion *and* a new axis. Both were dropped by
`expected_counts`. Every row must map to exactly one final write disposition.

**ADD-08 (NEW) — position-aware canonicalization.** `canonicalize_label`'s
flat-set slot bucketing cannot be position-aware, so `counters` buckets as
EFFECT even in noun slugs. CDR-09's typed prefixes make equality collision
effectively impossible, but position-aware bucketing against the ratified slot
order is the durable fix. Flagged for design, not designed here.

---

## Summary

| ID | Decision | Recommendation |
|---|---|---|
| ADD-01 | orphaned DET patterns | **RULED: Option A** — DET path, session 4 |
| — | `destruction` vs `destroy` | resolved by grammar §4: `destroy` |
| — | `targeted-*` slot order | resolved by grammar §1: action-then-class |
| CDR-01 | singleton nodes | n=1 deferred, n≥2 active, after review |
| CDR-02 | A15 clusters | Option D — partition semantically first |
| CDR-03 | R5 revalidation | 29 contradiction rows · 91 merges proceed · 39 human review |
| CDR-04 | duplicate quotes | `additional_evidence` in one assertion; A1 amendment |
| CDR-05 | near-duplicates | canonical fix is a bug; AG-EQUIV-01 after repair |
| CDR-06 | multi-keyword grants | route as-is + amend definition to "one or more" |
| CDR-07 | repaired node status | CDR-01 rule; failures rejected, never deferred |
| CDR-08 | 4 slot-order violators | rename on the §12 ledger |
| CDR-09 | `counter` homograph | enforce §8 whole-slug; ~15 renames; 3 need wording |
| CDR-10 | `exile` homograph | prepositional binding for zone sense |
| CDR-11 | predestined tags | ratify CR completions; derive mechanically; 7 Roles or 1? |
| CDR-12 | CR keyword actions | CDR-11's first application; `investigate` first |
| CDR-13 | homograph naming (CR-audit answer) | Homograph Form Ledger; zero new churn; CDR-10 folds in |
| NEW-01..02, ADD-02..08 | standing rules | as stated above |

**Nothing proceeds until CDR-01 through CDR-13 are ruled.** The largest
remaining work item is the B-02 semantic repair of the 93 nodes, gated on
CDR-01, CDR-07, and — per ADD-02 and CDR-11 — on the vocabulary being complete
first, so nodes are not reviewed twice.
