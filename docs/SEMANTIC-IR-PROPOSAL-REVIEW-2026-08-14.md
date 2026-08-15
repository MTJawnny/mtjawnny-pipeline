# REVIEW — Foundry First-Principles Semantic IR Proposal

**2026-08-14.** Read-only review of
`~/Downloads/FOUNDRY-FIRST-PRINCIPLES-SEMANTIC-IR-REVIEW-PROPOSAL-2026-08-14.md`
against the live repository. No code changed, no codebook mutation, no
vocabulary minted. **Shipped artifact that changes because of this review:
NONE** — and per CLAUDE.md §0 that is said out loud before anything else.

**Numbers in this review were re-derived this session where a tool exists**
(`foundry_qualifier_census.py` run live; Gate 2 run this session), not quoted
from documents. Where a number comes from a dated measurement, the date is
stated.

---

# ⛔ GATE 2 IS RED, AND THE FAILURE IS ABOUT THE EXACT FIELD THIS REVIEW DISCUSSES

**Found while writing this review, 2026-08-14. Reported, not repaired —
codebook mutation needs Captain, and the reversion event needs understanding
before any re-apply.**

Gate 2 (run this session): 16 rows, 14 pass, 1 excused (`family_sweep`), and
**`locality` FAILS** — `stored_owned 7808 → 0`, `addressable_missing 0 → 7808`,
both in the worse direction.

Investigated read-only:

- The live `experiments/out/foundry/codebook.json` (mtime **2026-08-14
  15:00:54**) has sha256 `b4197e94…` and **zero** `locality` fields across all
  8,982 assertions.
- `b4197e94…` is byte-identical to
  `backups/codebook.v0.7.pre-locality-backfill.20260814-015858.json` — the
  **pre-backfill** rollback point PICK-UP-HERE §0AB records.
- **No post-backfill copy (`6aa6193f…`) exists anywhere in `backups/`.**

So at 15:00 today the working codebook was overwritten with its pre-backfill
bytes — the documented rollback was executed, or a restore/drill clobbered
the operational file. The ratified backfill's 7,808 stored addresses are gone
from disk, and only the per-machine ratchet noticed. Recovery is documented
and cheap (`foundry_locality_backfill.py --plan` → `--dry-run` → apply, a
deterministic $0 re-derivation), **but it is a codebook mutation and it is
not taken here.**

Two consequences for this review:

1. Statements below of the form "locality is implemented and live" describe
   the **ratified state** (`B-MIGRATION-DISCOVERY.md` §11); as of this
   session's Gate 2 the stored field is absent from the working copy and
   must be re-applied before anything consumes it.
2. This is a live demonstration of the review's §4/§5.G point and of P3's
   entire premise: the codebook has no git history, a silent reversion is
   indistinguishable from normal state except to a per-machine ratchet, and
   the C6 manifest-selected-authority design is what would have made this
   event loud. The proposal's §16 ("authority/durability survives the
   redesign") is hereby endorsed with evidence it did not know it had.

**External citations were verified live this session.** All of the proposal's
load-bearing references exist and match its descriptions: `i5jb/mtgish` (a
typed alternate card syntax), `deckmaste.rs` (whose `deckmaste_semantics` is
described exactly as the proposal says — "the single information-complete
representation" between English syntax tree and engine AST), `delvefall.com`
(rules-line embeddings + concept slider), `phase-rs/phase`,
`wingedsheep/argentum-engine`, plus the already-known Forge wiki, Arena
GRP/CLIPS article, CubeArtisan `magic-card-parser`, `minimaxir/mtg-embeddings`,
Scryfall Tagger, MTGJSON atomic model. **The research section is real, not
hallucinated.** That deserves saying because it is the failure mode a packet
like this usually has, and this one does not.

---

# 0. VERDICT (proposal §39.A)

## `HYBRID SEMANTIC IR DESERVES BENCHMARK` — with four binding conditions

1. **The benchmark is filed as AQ4 evidence, not a new decision track.** The
   proposal's central question is `ARCHITECTURE-AUDIT.md` §13 **AQ4** restated
   — and its "hybrid" Outcome B is the audit's own §6.6 option, *"the
   predicate table, with axes as saved queries"*, already enumerated
   2026-08-13. Gate 3b (prior art) applies to proposals too. The
   `CANONICAL-SEMANTIC-UNIT-DECISION-PACKET-2026-08-13.md` set the precedent:
   *"no new decision IDs are minted."* Run the benchmark; file its result as
   the evidence AQ4 currently lacks; put one decision sheet in front of
   Captain.

2. **Extraction feasibility moves from EXT-6 (last) to co-equal with EXT-4
   (encoding).** This is the single largest correction this review makes, and
   it is argued from the repo's own measured history in §4 below.

3. **The benchmark set is seeded from the measured failure inventory** —
   the traps list, the five negative controls, the 39 AMBIGUOUS locality
   assertions, the 41 flattened-modal cards — not from hypothetical cohorts.
   Details in §7.F.

4. **Nothing in the current queue pauses except AQ4 ratification itself** —
   which is already paused, because AQ4 is already open and already Captain's.
   The C6 cutover and the ratified consolidation arc proceed. Sequencing
   argument in §6.

---

# 1. WHAT THE PROPOSAL GETS RIGHT (verified against local evidence)

- **The timing argument is real.** AQ4 is genuinely unresolved
  (`ARCHITECTURE-AUDIT.md` §13, quoted verbatim in the decision packet's A4).
  The corpus-wide certification/backfill has genuinely not begun. Deciding the
  substrate *before* certifying tens of thousands of rows under it is the
  correct order, and the proposal is right that this is the cheap exit ramp.

- **The qualifier problem is real and is the strongest pro-IR fact in the
  repository.** Re-derived live this session: **49.3% of 2,110** classified
  clause occurrences in the object-lattice families carry at least one
  eligibility restriction beyond the base object class; encoding those as
  compound slugs multiplies **23 base axes into 222 observed combinations
  (×9.7)**; **54 clauses** carry a CR 702 keyword restriction. Compound-slug
  explosion is measured, not feared. The proposal's Forge lesson —
  restrictions compose onto base classes rather than minting top-level
  vocabulary — is independently the conclusion the local census reached.

- **The non-goals are the right non-goals.** Not a rules engine, not EDHREC,
  not an LLM truth store, not permission for a rewrite. §10's "if a feature
  exists only because a rules engine would need it, that is evidence against
  it" is a good test and is kept in §7.E below in a sharpened form.

- **Preserve-by-default (§3.1) matches repo law.** Human assertions, evidence
  quotes, provenance separation, Gate 2, the durability architecture — the
  proposal is explicit that these survive any outcome, which is the correct
  reading of what the project's capital actually is.

- **The three-outcome structure (§17) is honest.** It allows the current
  model to win, and §31 states what that would look like. This is not a
  rewrite wearing a review's clothes — the constraints in §2.4, §30, and §36
  are genuine brakes.

---

# 2. WHAT THE PROPOSAL GETS WRONG, OR IS STALE ON

These do not sink the proposal; they change how it must be executed.

## 2.1 The Active Volcano calibration case is already half solved, and the proposal argues against a ruling it does not cite

The proposal's §8 presents Active Volcano as an open failure and §13 argues
that an IR "may allow locality to become more natural" than storing paragraph
facts and "later proving those facts belong together."

**That is not the current state.** Semantic locality (FL-2) was **ratified and
implemented 2026-08-13/14** (`B-MIGRATION-DISCOVERY.md` §11, canonical):
7,808 of 7,930 assertions on active axes now carry a stored
`locality: [face, paragraph]` owner; the remaining 122 are unaddressed by
rule and enumerated by tool. Modal exclusivity is **derived from the owning
header** (amendment A4), so a consumer can already tell that Active Volcano's
destroy and bounce are two options chosen between. The retrofit cost $0 —
the packet's own prediction that retrofitting would be expensive "is the one
prediction here that did not hold."

More importantly, the proposal's illustrative IR stores what a ratified
amendment deliberately refuses to store. **Amendment A1 rejected a stored
`mode` field on measurement**: 1,791 paragraphs hold exactly one modal
bullet and **zero** hold two or more, so the paragraph coordinate already
separates modes and a stored mode identifier would be a second source of
truth. The proposal's `ModalChoice { mode 1: …, mode 2: … }` structure
re-introduces stored mode structure. Maybe a canonical IR justifies that
where an assertion field did not — but the benchmark must **engage A1's
measurement and argue past it**, not re-litigate it silently. A clean-room
that rediscovers a rejected design without meeting the rejection's evidence
is the exact drift shape `SESSION-START-PROCEDURE.md` exists to stop.

**What remains genuinely unsolved from the calibration case is exactly one
thing: qualifier attachment** — that `blue` belongs to the destroy target.
That is the qualifier packet arc, i.e., AQ4. The proposal's calibration case
should be re-scoped to say so.

## 2.2 The cited certification plan is not in the repository

`FOUNDRY-SHARDED-CORPUS-CERTIFICATION-PLAN.md` (proposal §25) exists only in
`~/Downloads`, self-labeled DESIGN ONLY. Its "Stage F laws" are not ratified,
not tracked, and referenced nowhere in `docs/`. Under this repo's own
convention (PICK-UP-HERE's tracked/untracked table; "a committed page pointing
at numbers nothing could re-derive"), an out-of-repo design packet is not
load-bearing. The proposal treats it as a standing system to remain
compatible with. It is a *sibling proposal*, and both should say so.

## 2.3 The product-reality lens is absent, and it is the strongest measured evidence about what the product actually lacks

The proposal never confronts `WIRE-RESULT-2026-08-09.md` or
`PRODUCT-REALITY-AUDIT-2026-08-09.md`, and CLAUDE.md §0 makes their question
mandatory: *which shipped artifact changes?* The measured facts:

- `foundry_reachability.py`: **0 of 5** foundry artifacts reach a shipped
  card. The tier engine reads no foundry output.
- The wire experiment: the codebook join failed **not** for representational
  reasons but because **axis recall was 39%** against hand-named correct
  neighbours — *"the blocker is coverage, not plumbing."*
- A ratified, verified consolidation plan (15,371 rows, coverage 19.3% →
  48.0%) is one Captain decision (two axis records) plus a regeneration away
  from applying.

A semantic IR raises representational *fidelity*. It does nothing for
*recall*, and it adds extractor surface. To be fair to the proposal, the wire
result cuts both ways — it also showed the derived term "partitions, not
ranks," and richer structure is one route to ranking — but the proposal tells
only the representation side of a story whose measured half is coverage. The
consequence is drawn in §6: the review must not displace the coverage arc.

## 2.4 Small factual notes

- "4,000+ human assertions" — live: **4,233** human of 7,930 total
  (measured 2026-08-14, P3 packet).
- §1's motivating item 3 ("card-level bags insufficient") is correct but now
  resolved at the storage layer (see §2.1); item 5 (P3 showed accidental
  structure) is fair; items 1, 2, 4, 6, 7 check out.
- EXT-1 (external architecture digest) is **already substantially done by this
  proposal itself** — and now verified. Timebox any remainder to days, not a
  phase.

---

# 3. STRONGEST ARGUMENT FOR THE PROPOSAL (proposal §39.C)

**Qualifier attachment at sub-paragraph granularity is a real, measured,
unsolved representational problem — and it is about to become expensive.**

The ratified locality coordinate stops at the paragraph. But a paragraph can
hold several clauses (the 39 AMBIGUOUS assertions; Seize the Soul's spell
effect vs. its Haunt trigger printing the identical clause), and the census
shows the restriction load is heavy — 49.3% of classified clauses — and
**rising with time** (mean restriction categories per card 0.85 → 1.39 across
four release eras; census §B, measured 2026-08-13). Whatever AQ4 answers —
facet rows, typed fields, relation nodes — must prove *which occurrence* a
qualifier modifies. A flat facet row re-creates the locality problem one
level down; a typed unit carries the attachment structurally. That is the one
consumer-integrity problem (Budget Swapper's
`Destroy target permanent` ≠ `Destroy target blue permanent`) that the
current model has no answer for yet and the IR answers by construction.

Honest limit on this argument: **the IR does not touch the other named hard
case.** Grand Abolisher ↔ Defense Grid needs new *dimensions* (who is
restricted, when, prohibition vs. taxation) — and dimensions can be added to
either substrate. The decision packet already said this plainly; the proposal
should inherit that honesty.

---

# 4. STRONGEST ARGUMENT AGAINST (proposal §39.B)

**Extraction is where this repository's costs and defects actually live, and
the proposal defers extraction feasibility to EXT-6 — dead last.**

Everything measured locally says the schema is the cheap part and the
extractor is the expensive part:

- The delivery classifier — far shallower than the proposed IR — required
  the entire ~70-item traps list to get right: trigger-clause boundaries,
  ability-word stripping, em-dash six-way disambiguation, reminder-text
  inversion, striations, reflexive triggers, voice/inflection/word-order
  sweep classes, coordination-splitter defects that point opposite ways.
- Probe defects are "the default outcome, not the exception" — 21+ across
  five sessions, all in the family *asking the question again instead of
  consuming what the classifier emitted*.
- The CR-derivation law exists because **every hand-list became a defect
  with a delay** — and it was predictive (D5, D6). The proposal's §11.2
  action-primitive list is exactly such a hand-list; a real IR would derive
  action vocabulary from CR 701/702 at run time the way `TRIGGER_VERB`
  already is.
- Arena's "80% of new cards parse automatically" is a *warning* here, not
  an encouragement: that is a full-time professional team, on **newly
  templated** cards only. Foundry's corpus is 30 years of templating drift,
  and the local evidence (curly apostrophes, CR-leading-corpus and
  corpus-leading-CR both measured) says the tail is long in both directions.

A typed IR multiplies the slots an extractor must fill per clause, and every
unfilled or misfilled slot is a new instance of the proposal's own §29.5
("false precision"). Second-order cost: **the guard stack is most of the
project's real capital, and it is built against the current representation.**
Conservation, visibility, ground truth, definition drift, the ratchet, the
locality gate — a canonical-substrate change resets a large fraction of that
stack, and rebuilding negative-controlled gates is exactly the slow, careful
work of the last two weeks. Any benchmark scoring must count that
(proposal §20's dimension 13 exists but underweights it).

This is why condition 2 in §0 is binding: **for every benchmark card, the
encoding must be accompanied by its extraction story** — for each filled
field, name the CR rule and derivation path it would come from, or mark it
`HAND-LIST` / `HUMAN-ONLY`. A card whose elegant IR encoding needs three
hand-lists is a red flag in week one, not a surprise in phase EXT-6.

---

# 5. ANSWERS TO THE REMAINING §39 ITEMS

## D. Minimal candidate model

**The clean-room is smaller than the proposal thinks, because the repository
already discovered the minimal semantic grammar empirically — it is the slot
grammar, currently flattened into slugs.** The census's representation
inventory (§C of `FACT-GRANULARITY-CORPUS-CENSUS-2026-08-13.md`) is
effectively the field list: action (§4 EFFECT verbs), object (§5
`OBJECT_VOCAB`), target presence (§6a / CR 601.2c), controller scope (§6),
timing/activation (§3), delivery (§2's 52 tokens), scaling (§7),
counter/token type (§8) — all *direct* today — plus the six dimensions
measured as quote-only: **colour, state, numeric threshold, negated type,
supertype, magnitude**, and zone as a first-class pair instead of a compound.

So the minimal IR is approximately:

```
unit:
  owner:      [face, paragraph]        # the ratified locality coordinate, reused
  delivery:   §2 token                 # already closed vocabulary
  action:     §4 verb (CR-derived)
  object:     §5 class
  qualifiers: [{dimension, value}]     # the census's seven categories, CR-derived values
  quantity / zones / duration / optionality / condition
  evidence:   quote (unchanged law)
  provenance: class + source_ref + corpus_ref (unchanged law)
  disposition: parsed | ambiguous | unresolved | out-of-contract
```

The genuinely new design questions are only: (a) qualifier attachment below
the paragraph, (b) whether zone/duration/condition are fields or facet rows,
(c) unit identity across corpus refreshes — for which D-4's ratified answer
(snapshot-local, re-derive, halt on unresolved) should be the default. Note
this makes the clean-room constraint in EXT-3 ("do not look at current Foundry
schema") **partially wrong for this repo**: the slot grammar is not an
accident to be avoided, it is the empirical result the clean-room is supposed
to produce. Sketch blind if useful for de-anchoring, then reconcile against
the grammar *before* any verdict — the repo's whole finding is that drift
comes from acting without context.

## E. Rules-engine boundary

Sharper than the proposal's in/out lists, and derived from existing law:

> **A field belongs in the IR if and only if its value can be proven by an
> oracle-text quote plus a CR rule number, without game state.**

That is the existing evidence-quote-or-discard law generalized to fields. It
admits everything in the proposal's "likely in scope" list and excludes every
"likely out of scope" item automatically — layers, APNAP, priority, and
resolution ordering all require state no quote can carry. Corollary: the IR
never *resolves* references ("that creature", "it") beyond marking that a
reference exists and which unit owns it — resolution is execution.

## F. Benchmark design critique

**Seed from measured failures, not hypothetical cohorts.** The proposal's
§18.2 list is reasonable but generic; this repo owns a better one. Must-add,
each anchored to a recorded defect or ruling:

- reminder-text inversion (Spree — a `choose one` search finds the opposite);
- ability-word/flavor-word prefixes incl. digits (`No One Dies!`, `Nitro-9`),
  and a mode *named* by a flavor word (Hawkeye's `• Explosive —` mode of a
  CR 603.12 reflexive trigger);
- one paragraph, several abilities (CR 603.11 static + linked triggers;
  exert per CR 701.43d);
- striation cards (CR 711/716/721 — the marker is scaffolding, the content
  classifies);
- die-roll tables (CR 706.3b — one ability);
- Room doors (CR 709.5h vs 709.5i — two events, different cards);
- `while`-condition coordination (Preacher of the Schism — a splitter that
  invents a trigger);
- quantity-phrase coordination (`mana value 3 or greater`, `one or more`);
- identical clause, two owners (Seize the Soul — the AMBIGUOUS class, all 39);
- the 41 flattened-modal cards (the population, not just Active Volcano);
- the five negative-control constructions from
  `FULL-CARD-INFORMATION-CONSERVATION-2026-08-13.md` (NC-A…E), because a
  representation should be scored on whether those mutations are *visible*
  in it;
- CR 201.5c shortened names on non-legendaries (Destroy the Evidence);
- typography (curly apostrophes; `{TK}` ticket vs. station);
- Alchemy `A-` twins (paper-preferred law);
- a CR-leads-corpus card class (Storied/Recruit: zero attested lines) to test
  the "not modeled yet vs. not present" distinction.

Trim: "triggered/activated/static abilities" as cohorts are not adversarial
alone — fold them into the cards above, which all carry one. Keep "cards that
currently parse cleanly" small (5 or fewer) as the free-baseline control.

**And one procedural requirement the proposal omits: pre-committed
expectations.** For every card, the correct answers to §19's consumer
questions are written **before** any model encodes it — the exact discipline
that made `WIRE-RESULT` trustworthy ("every one of those movements would have
read as progress against a list written after").

## G. Migration risk — hardest knowledge to conserve

Ranked, hardest first:

1. **The ruling corpus itself.** 77 of 328 active axes already have rulings
   filed under former names; the docs' law is keyed to slugs and to §2's
   machine-parsed table. An IR re-keys the vocabulary, which orphans ruling
   history the way renames already did — except corpus-wide at once.
   `foundry_slug_dossier.py`'s rename-walking approach is the mitigation
   pattern, and it would need an axis→unit-projection equivalent.
2. **Human judgment not derivable from text**: batch annotations, family
   rulings (KEEP/MERGE verdicts), the deferred-status D6-style reversals,
   OUT-OF-SCOPE decline decisions. These attach to axes as *decisions about
   vocabulary*, and a derived-index axis is no longer a decision surface.
3. **The negative-controlled guard stack** (see §4) — rebuildable but slow,
   and its history of mis-aimed controls says each rebuild ships 3-of-8
   mis-aimed on the first pass.
4. The 4,233 human assertions themselves are the *easiest* of the named
   risks, not the hardest: each is `(axis, oracle_id, quote, locality)`, and
   under Outcome B axes persist as derived indexes, so the assertions keep
   their referent. The proposal's §24 taxonomy is right; its implicit
   ranking (assertions as the headline risk) is inverted.

## H. AQ4 impact

**The proposal *is* AQ4.** It reframes it exactly as `ARCHITECTURE-AUDIT.md`
§6.6 already did (predicate/unit substrate, axes as saved queries), adds
verified external corroboration that the pattern is common, and proposes the
evidence-gathering exercise the audit's "largest risk in this document"
assessment was always going to require before Captain could rule. It resolves
nothing by itself; executed as amended here, the benchmark becomes AQ4's
evidence packet. AQ5 (`level`) is untouched. FL-2 is already closed and the
proposal should stop implying otherwise (§2.1).

## I. Go/no-go — next read-only experiment only

**GO**, scoped as:

1. **EXT-2′** — benchmark set per §5.F above: ~35 cards, each published with its
   inclusion reason *and its pre-committed consumer-question answers*.
2. **EXT-3′** — clean-room sketch, then mandatory reconciliation against grammar
   §1–§13, the locality amendments A1–A4, and the census inventory, before
   any side-by-side. The reconciliation is part of the deliverable.
3. **EXT-4′ + extraction story** — encode in (current model + locality +
   hypothetical facet rows) vs. (candidate IR); every IR field carries its
   CR-derivation path or an explicit `HAND-LIST` flag.
4. Score on §20's dimensions plus one addition: **guard-stack reset cost** as
   its own line, not folded into "migration cost."
5. Output: **one AQ4 evidence packet, one decision sheet, Captain rules.**

**NO-GO on everything else in the proposal**: no schema ratification from its
illustrative YAML (it says so itself — hold it to that), no EXT-1 phase beyond a
timeboxed license check, no pausing of the arcs named in §6, and no
implementation authority of any kind.

---

# 6. SEQUENCING — where this fits the actual queue

The proposal's §35 recommends finishing C6 first (agreed — that is already
the ruled next phase) and then "avoiding large qualifier/AQ4 production
expansion" until the review concludes. **Half right:**

- **Pause (already paused):** freezing AQ4, minting qualifier vocabulary.
  The census itself ruled that minting qualifier vocabulary inside a plumbing
  change would smuggle a ratification; nothing changes.
- **Do NOT pause: the consolidation apply and the coverage arc.** Three
  reasons. (a) It is the measured answer to the product's live blocker (39%
  axis recall; 19.3% → 48.0% coverage), and the review has no bearing on it.
  (b) Its artifacts — memberships with verbatim quotes — survive every
  outcome: under Outcome B they become derived-index members and extraction
  seeds; nothing is certified-then-regretted, because *applying* the plan is
  not *certifying* the corpus. (c) It is already Captain-ratified pending two
  axis records; unwinding a ratified arc on an unratified proposal inverts
  the authority order.
- **Defer (agreed, and it costs nothing):** the expensive human
  certification pass (the Downloads plan's Stage F). It has not started, its
  plan is not in-repo, and it is the one thing that genuinely should wait for
  AQ4's answer.

Practically: **C6 cutover → consolidation decision sheet + apply → re-run the
wire experiment (predictions already committed) → AQ4 benchmark (this
review's §5.I) → Captain rules AQ4.** The wire re-run is itself benchmark
evidence: if coverage at 48% fixes ranking, the pressure on the IR drops; if
it still partitions, the representation argument strengthens. That
measurement is free and the proposal should want it.

---

# 7. ONE-PARAGRAPH SUMMARY FOR CAPTAIN

The proposal is serious, its research is real (verified live), and its
central question is legitimate — but it is not a new question: it is AQ4,
already open on your sheet, wearing external-research clothes. Its calibration
case is half solved (locality landed; exclusivity is derivable; what remains
is qualifier attachment, which is exactly the qualifier arc), and its one
structural blind spot is that it postpones extraction feasibility to last
when everything this repository has measured says extraction is where the
cost lives. Recommendation: run the bounded read-only benchmark, amended to
seed from our measured failures, carry pre-committed answers, and price the
extraction story per card — file the result as AQ4 evidence — and change
nothing else in the queue: C6 first, consolidation apply proceeds, corpus
certification waits. The current leading hypothesis (typed units canonical,
axes derived) is plausible; the census's ×9.7 compound pressure is the best
argument for it; the guard-stack reset and extractor surface are the best
arguments against; and the benchmark, run honestly, is how the difference
stops being a matter of taste.
