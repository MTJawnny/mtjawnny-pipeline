# RATIFIED DIRECTIVES — batches 4 and 6 (extracted verbatim)

Captain's parsed-directive sections, lifted UNCHANGED from
`TRIAGE-BATCH-4.md` and `TRIAGE-BATCH-6.md` before those documents were
archived. Per the ratified rule (`MASTER-HANDOFF-ADDENDUM-2.md`:123)
*"parsed-directives section is authoritative over prose annotations"* —
so this file carries the whole of those batches' live law. The archived
originals keep the working record (findings, per-axis verdicts,
spot-checks) and are NOT authoritative.

Batches 1 and 3 are deliberately absent: they predate the §10 convention
and are prose-annotated, with no safe extraction boundary. Both remain
live in `docs/` in full.

---

## Source: `TRIAGE-BATCH-4.md` lines 536–672 (verbatim)

## 10. CAPTAIN RATIFICATION — PARSED DIRECTIVES

Per SUP-TRIAGE-PROTOCOL.md's §10 convention: this section is the
authoritative, parseable record of Captain's ratification. Sections 0/1's
prose annotations above remain the audit trail explaining *why*; this
section is what `/triage-emit 4` actually parses. Where this section and
the prose above could be read differently, this section governs.

**D1 — `rule:activated-tap-target-creature` (n=16): KEEP, member removals
ratified as proposed, no split.**
Remove 9 members: Arena, Crossbow Infantry, Eddymurk Crab, Glaring Aegis,
Hammers of Moradin, Relic Barrier, Rishadan Port, Summon: Valefor, Tamiyo,
Field Researcher. Surviving 7: Blinding Mage, Blinding Souleater, Gavony
Trapper, Loxodon Mystic, Sigardian Priest, Solstice Zealot, Stormscape
Apprentice. The axis concept stands as originally defined ("an activated
ability that taps a target creature") — Captain declined section 5's
implicit invitation to fork it into sibling ETB/attack-trigger tap axes
this batch; those siblings are schema-pass material, tracked in
PARENT-TREE-CANDIDATES.md's "taps a target creature" trigger-context gap
entry, not built now.

**D2 — Member removals ratified (single-card, no axis-level action).**
- `rule:mass-damage-opponent-creatures-only` (n=3): remove Klothys, God of
  Destiny — deals damage to opponents directly, not their creatures. No
  reassignment target; the axis for "mass damage to opponents, no target"
  does not exist this batch and none is being built for it now.
- `rule:targeted-creature-damage` (n=13): remove Item Crate — "deals 2
  damage to any target" is any-target, not creature-specific. REASSIGN:
  add Item Crate to `rule:direct-damage-any-target` at reconcile (its
  quote is a verbatim fit for that axis's existing definition).

**D3 — `rule:targeted-planeswalker-damage`: add Breya, Etherium Shaper at
reconcile, per the ratified M8 per-object-class mixed-target rule.**
Breya's quote ("deals 3 damage to target player or planeswalker") already
qualifies her for `rule:targeted-player-damage` (in this batch's own
member list); M8 requires the second tag on the planeswalker-damage axis
too, since mixed-target cards get multiple tags rather than one combo tag.
This is a reconcile-time addition to an axis Breya isn't otherwise a
batch-4 member of — not a member-removal, not a new axis.

**D4 — Merges ratified.**
- `rule:grants-temporary-hexproof` (n=2: Mizzium Skin, Plumecreed Escort)
  → MERGE INTO `rule:temporary-keyword-grant`.
- `rule:etb-grants-energy-counters` (n=3: Hightide Hermit, Decoction
  Module, Inventor's Axe) → MERGE INTO `rule:gives-energy-counters-immediately`.
- `rule:replacement-exile-instead-of-graveyard` (n=2: Mission Briefing,
  Covetous Castaway // Ghostly Castigator) → MERGE INTO
  `rule:graveyard-to-exile-replacement`.
- Q1 resolved: `rule:replaces-death-with-exile` (n=2: Bouncer's Beatdown,
  Incendiary Flow) → MERGE INTO `rule:graveyard-to-exile-replacement`
  (Captain: "Merge"). The self-protection-vs-removal-upgrade distinction
  section 2 raised is noted but does not block the merge — same
  continuous-replacement-effect text pattern governs.
- **STANDING RULE (going forward, all future batches):** any
  `grants-temporary-<keyword>` candidate (any keyword, not just hexproof)
  folds into `rule:temporary-keyword-grant` on sight — beta does not need
  to raise it as a question or a fresh merge proposal. The keyword-identity
  facet (which keyword was granted) is deferred to the schema-pass facet
  scheme (§10 STEP 2a below / PARENT-TREE-CANDIDATES.md), not rebuilt as a
  one-off axis per keyword.

**D5 — HELD, not parsed into this emit's codebook build as KEEP/KILL/MERGE.**
`rule:activated-pump-with-self-damage-cost` (n=2: Stormcloud Djinn,
Electric Eel) and `rule:activated-self-toughness-pump` (n=2: Abbey Matron,
Pearl Dragon) do NOT execute section 1b's proposed MERGE INTO
`rule:mana-activated-pump-self` this batch. Verdict for both: **DEFER**.
Both carry into codebook v0.4 as `status: "deferred"` (recorded, inactive,
not offered to SYNTH as an active codebook slug, not merged) pending
Captain's review of their full member lists + evidence quotes, written to
`experiments/out/foundry/review/batch-4-deferred-examples.md` (file only —
transcript hygiene, no oracle text to console).

**D6 — PRECEDENT REVERSAL: cost-shape riders are legitimate wide-net axes.**
The b2/b3 "cost-shape riders are not axes" precedent (which killed
`rule:sacrifice-creature-as-additional-cost`,
`rule:sacrifice-as-additional-cost`, `rule:self-sacrifice-divided-damage`,
etc.) is OVERTURNED. `rule:additional-cost-sacrifice-permanent` (n=4:
Shard Volley, Lethal Throwdown, Bankrupt in Blood, Momentous Fall) and
`rule:additional-cost-discard-a-card` (n=2: Laughing Mad, Sazacap's Brew)
flip **KILL → KEEP**, both entering codebook v0.4 as new active axes with
their batch-4 members. Downstream actions (not executed this emit, logged
as punch list): (a) MASTER-HANDOFF-ADDENDUM-2.md §4 rulings registry
updated with the reversal (STEP 4/6 of this session); (b)
docs/SUP-TRIAGE-PROTOCOL.md's and `.claude/commands/triage-beta.md`'s
standing verdict precedents updated so batch-5 beta does not auto-KILL
cost-shape candidates; (c) punch-list item: evaluate resurrecting the
b2/b3-killed cost-shape axes (`rule:sacrifice-creature-as-additional-cost`,
`rule:sacrifice-as-additional-cost`, `rule:self-sacrifice-divided-damage`)
at reconcile or schema pass — NOT executed now, Captain must explicitly
call it.

**D7 — All other section-1 verdicts stand as written.**
Every axis in sections 1a/1b not named in D1–D6 above ratifies exactly as
SUP proposed (overwhelmingly KEEP, including all 27 new-candidate KEEPs).
No further changes.

### STEP 2 — Parent-tree ledger additions (attributed to Captain, batch-4
ratification; written to `mtjawnny.github.io/docs/PARENT-TREE-CANDIDATES.md`
per the established durable-location precedent, not this repo's `docs/`):

a. **Keyword-grant facet scheme.** Wide-net `rule:temporary-keyword-grant`
   stays the catch-all; granular facet dimensions on top: which keyword
   (e.g. `gives-hexproof`), duration (EOT / next turn / static-anthem /
   keyword counter), scope (target / up-to-N / all-you-control / all),
   delivery trigger (etb / activated / cast). Interacts with the b1-Q1
   keyword-grant engine-redundancy kill — open tension T1, schema pass
   reconciles. Do not author these as axes now.
b. **Cost-shape facet scheme**, per D6: wide-net cost axes
   (`rule:additional-cost-sacrifice-permanent`,
   `rule:additional-cost-discard-a-card`, and the punch-listed b2/b3
   revival candidates) stay wide-net; granular children on top: object
   class sacrificed, one-shot vs. repeatable outlet.
c. **Delivery-facet note**, from the energy merge (D4): merged members of
   `rule:gives-energy-counters-immediately` should be distinguishable by
   delivery trigger (etb vs. other) at schema pass.

### STEP 3 — Punch list additions (logged only, not executed this emit):

- DET fix for `experiments/foundry_common.py`'s `build_review_card_record()`:
  when root `oracle_text` is empty, concatenate `card_faces[*].oracle_text`
  per the repo's all-faces rules (21 multi-face cards affected in batch 4).
  **Correction at emit time:** found already implemented, correctly, but
  uncommitted in the working tree — not written by the emit session, but
  committed as part of it since it directly benefits batch-5's Stage 1B
  prompts. Does not retroactively fix `review/batch-4.json` itself (already
  generated before the fix existed). Captain note carried forward: consider
  a sanctioned oracle-text injection path for multi-face cards — surfacing
  back-face cards quickly is a product requirement for every tool built on
  this engine.
- Batch-5 beta spec change: add a MEMBER ROSTER section to the TRIAGE doc —
  every axis, full member card names (names only, no oracle text) — so
  Captain can audit membership, not just logic.
- Batch-5 SYNTH prompt fix from section 5 (activated-vs-triggered /
  ability-type check) stands — apply it.

**RATIFIED.** §10 supersedes sections 1–2's prefilled verdicts wherever
they conflict. Proceeding to `/triage-emit 4`.

---

## Source: `TRIAGE-BATCH-6.md` lines 424–1008 (verbatim)

## 10. CAPTAIN RATIFICATION — PARSED DIRECTIVES (2026-07-30)

**AUTHORITATIVE FOR PARSING.** Translated from the 2026-07-30 chat review session
(independent card-by-card audit of this document + Captain's direct rulings). Where this
section conflicts with anything above, THIS SECTION GOVERNS. All card-text claims were
verified against live oracle text in the review session; emit re-verifies against the
corpus (verify-or-drop) as always. Several directives below instruct Claude Code to
FIND-AND-CONFIRM before acting — those are marked; halt loudly if confirmation fails.

### D1 — LEGALITY GATE (new standing ruling, brand-wide; EXPLICIT PARTIAL REVERSAL)
**A card must be legal in at least one format to be a valid target for the engine, the
scan, and every MTJawnny tool.** Stated as brand fact: the corpus may retain non-legal
rows for reference, but no non-legal card is ever tagged, offered to SYNTH, counted in
an axis, surfaced by a tool, or spent tokens on. Un-sets, joke sets, playtest cards
(CMB1/CMB2/MB2 test cards), Unknown Event promos, prototype/event cards — out.
- Implementation: gate on the Scryfall `legalities` object. PASS iff any format value is
  `legal` or `restricted`. Everything else (all `not_legal`/`banned`) FAILS the gate.
  This is GATE #0 — it runs at dataset level before every downstream stage (DET pass,
  batch assembly, SYNTH, tools).
- REVERSAL LOG (rulings registry): this partially overturns the earlier
  "legality is display-layer only; joke/playtest cards stay in corpus; rank buries,
  never excludes" posture. New form of the ruling: Alchemy-only and format-narrow cards
  still pass (they are legal somewhere; paper-over-Alchemy display rules unchanged);
  nowhere-legal cards are excluded outright — the corroboration gate is no longer the
  sole exclusion. Logged Captain-explicit, D6-style.
- **Retroactive membership scrub (Code task):** rescan every member of every codebook
  axis (all versions ≥ current) against Gate #0; emit a scrub report and remove gated
  members. Known hits from this session's audit: Potatoes and Joraga Peach (Unknown
  Event), Heart of a Duelist and Taiga Stadium (playtest — note Taiga Stadium was
  ratified into rule:enters-tapped-conditional in batch 5 §10; the gate removes it
  retroactively, that is intended), and "Wizard" in rule:restricted-purpose-mana
  (unverifiable via web this session — confirm via corpus name index; if playtest/
  Unknown Event, gate it). Pick-a-Beeble: apply the gate mechanically (Attraction
  Commander legality is disputed across sources); its member_removal in D3 stands on
  independent grounds regardless.
- **Batch assembly + full-corpus pass now draw only from gate-passing cards.** Report
  the gated-out count so the full-corpus card total and cost estimate get restated.
- **Precedent rescan (Code task, FIND-AND-CONFIRM):** walk every ratified
  ruling/precedent in the registry, decisions/*.json rationales, and SUP standards;
  identify any derived from now-gated cards; trash those unless independently useful on
  legal-card evidence, and log each disposition. Named suspect: the "Peel Out/Banana
  precedent" cited in this document's Stone Retrieval Unit verdict — it appears in no
  handoff or registry visible to the review session; locate its origin, and strike the
  citation if it cannot be sourced or derives from gated cards (Stone Retrieval Unit's
  membership stands on its Powerstone quote alone either way).

### D2 — Q1 ruled: (b), expand — with the lattice grammar noted in §11
rule:activated-tap-or-untap-any-creature KEEPS its creature scope; sole member Puppet
Strings. NEW captain-authored sibling rule:activated-tap-or-untap-any-permanent; member
Fatestitcher ("{T}: You may tap or untap another target permanent."). The ledgered
rule:activated-tap-target parent unifies them for browsing. Per "don't absorb, expand"
and "small n — kill for fake, never for rare."

### D3 — Q2 ruled: (a), plus member surgery from the independent audit
- rule:etb-pump-target-creature: drop the "not restricted to the controller's own
  creatures" definition clause; keep Herald of the Fair and Yeva's Forcemage; scope
  field reads any-creature (widest member); ownership-scope logged as a facet dimension
  for the schema pass.
- **rule:activated-ability-costs-self-sacrifice: member_removal(Pick-a-Beeble).**
  Verified: it is an Attraction; Visit and Prize are TRIGGERED abilities and "sacrifice
  Pick-a-Beeble" sits inside the Prize EFFECT — fails the axis on both the activated
  requirement and the cost requirement (batch-4 D1 conflation class). Note for the
  record: the section-5 override sample marked this row OK; the true sample result is at
  best 28/30. Roster-based membership audit (D6) exists precisely for this.
- **member_removal(Otawara, Soaring City) is REVERSED — Otawara STAYS in
  rule:targeted-bounce-creature.** Ruled: **M8 GENERALIZES from damage to every
  targeted-<action> family** (registry update): a card targeting multiple object
  classes (AND or OR shape) receives every applicable per-class tag; never a combo tag;
  removal for multi-type text is wrong when the class in question is among the targets.
  The missing per-class bounce siblings (targeted-bounce-artifact / -enchantment /
  -planeswalker) go to the parent-tree ledger as a lattice family, instantiated when
  members arrive (§11 rules; do not author empty).
- rule:leaves-battlefield-trigger-create-token-creature: member_removal(Zoo Escapees)
  stands, but Zoo Escapees is NOT homeless — NEW captain-authored
  rule:leaves-battlefield-trigger-create-token-mutagen (n=1: Zoo Escapees), per the D10
  (batch 5) sibling convention. Withdraw the "no home exists" ledger flag.
- NEW captain-authored rule:activated-untap-target-creature; members High Alert and
  Staff of Domination (both verified "Untap target creature"), rehomed from their
  rule:untaps-target-land removals. Ledger: flag the tap/untap activated family for
  consolidation review at schema pass (it now spans tap-target-creature,
  untap-target-creature, untap-another-permanent, tap-or-untap-any-creature,
  tap-or-untap-any-permanent, untaps-target-land, plus mass variants).
- rule:charge-counter-accumulation: member_addition(Culling Dais) — "{1}, {T}: Put a
  charge counter on Culling Dais" (rehome from its removal above). Joraga Peach's
  candidate rehomes are MOOT — gated by D1.
- All other SUP corrections stand as written: Village Ironsmith // Ironfang removal,
  Forth Eorlingas! move to rule:token-count-scales-with-x, Insult // Injury (Injury)
  addition to targeted-planeswalker-damage, Stone Retrieval Unit addition to
  create-token-mana-producing-artifact (citation caveat per D1).

### D4 — All remaining verdicts stand
All 165 confirmations and 27 new-candidate KEEPs stand as proposed except as modified by
D1–D3. Zero KILLs, zero MERGEs remains true at axis level. New captain-authored axes
this batch: activated-tap-or-untap-any-permanent, activated-untap-target-creature,
leaves-battlefield-trigger-create-token-mutagen (3).

### D5 — STANDING PROTOCOL RULE: remove-and-rehome
Every member_removal must answer "where does this card actually belong?" — an existing
axis (member_addition), a convention-consistent new sibling (captain-author candidate),
or an explicit "no home; ledger-flagged." Silent stranding is a protocol violation.
Batch-5 set the pattern; batch 6 missed it three times (High Alert/Staff, Culling Dais,
Zoo Escapees). Bake into SUP-TRIAGE-PROTOCOL.md and triage-beta.

### D6 — MEMBER ROSTER regression (Code task, FIND-AND-CONFIRM)
This document omitted the MEMBER ROSTER section required since batch 4's punch list and
delivered in batch 5. Regenerate the roster for all 192 axes (names only, no oracle
text) and append it to this file BEFORE reconcile; Captain audits it before batch 7
assembly. Fix triage-beta so the roster is structurally mandatory. While regenerating,
if the roster surfaces additional members that obviously belong in different existing
buckets (per the D5 rule and this session's patterns), Code may reorganize —
member-level moves only, quote-verified, every move listed in the emit report for
Captain's post-hoc review; anything judgment-ambiguous halts loudly instead.

### D7 — Recently-killed appendix (Code task, FIND-AND-CONFIRM)
Equipment-static-buff was re-invented by SYNTH for the third consecutive batch. Confirm
whether the recently-killed appendix (escalated at batch 5) was actually built into the
batch-6 SYNTH prompt. If unbuilt: BUILD IT NOW; it blocks batch-7 submission. If built:
it failed — diagnose and fix before batch 7.

### D8 — Batch-7 feedback additions (beyond section 7)
1. Effect-POSITION check joins the ability-type check: a cost-axis member must show the
   named action on the cost side of the colon; an effect inside resolution text never
   satisfies a cost axis (Pick-a-Beeble class).
2. M8-generalized: multi-class targeted-<action> cards get every applicable per-class
   tag; never removed for breadth.
3. n=2 OTHER-lane tier: the assembly script's no_other_lane_reinforcement_reason must
   state "spot-checked, not exhaustively cleared" per this document's own methodology
   note — carry that honesty forward.
4. All section-7 items stand.

---

## 11. CORPUS-WIDE PROCESSING PLAN (ratified direction — record in docs/, execute per sequencing)

Captain has ratified the three-lane design for the full-corpus pass, plus a lattice
grammar layer. Claude Code: persist this section into the protocol docs (new
docs/CORPUS-PASS-PLAN.md or equivalent), wire the sequencing, and treat the lattice
grammar as a naming-discipline change effective immediately.

### 11.1 Three lanes
- **Lane 1 — DET pre-tag pass (runs first, token-free, re-runs on every Scryfall
  refresh).** Every codebook axis gets classified DET-able or SYNTH-only. DET-able =
  membership decidable by an anchored oracle-text pattern with polarity
  canonicalization and no judgment (enters-tapped, the three activation-restriction
  strings, "can't be regenerated", no-maximum-hand-size, stun counters, energy, the
  Ring, landfall—, kicker, etc.). Each pattern is proposed with a measured corpus
  hit-list, sampled and RATIFIED by Captain like a scoring constant, versioned, never
  silently tuned. Provenance: rule-derived (full weight). Gate #0 applies.
- **Lane 2 — SYNTH judgment pass.** DET-owned axes are STRIPPED from the embedded
  codebook (this is the codebook condensation's biggest lever). SYNTH hunts judgment
  territory: jobs, rhystic shapes, cheat-into-play, Tier-3 same-job-different-words.
  Runs only on gate-passing cards; restate the card count and cost estimate after the
  gate + strip land.
- **Lane 3 — Reconcile with halt-loudly.** SYNTH never sees DET pre-tags (no
  anchoring). At reconcile: SYNTH free-lane output matching a DET-owned axis =
  corroboration; contradiction of a DET pattern = halt-loudly review row.

### 11.2 Lattice grammars ("prebuilt buckets," done safely)
Captain's intent: game concepts derive families — once
activated-tap-or-untap-any-permanent exists, the whole
`activated-tap-or-untap-<scope>` family is enumerable a priori (any/own/opponent ×
creature/artifact/permanent, etc.). Ratified mechanism:
- For a family, Captain ratifies a GRAMMAR: an action stem plus ordered facet slots
  with closed vocabularies (e.g. `activated-tap-or-untap-<ownership?><class>`;
  `targeted-bounce-<class>`; `<trigger>-create-token-<type>`). The grammar, not a list
  of empty axes, is the prebuilt bucket.
- **Virtual nodes:** unpopulated lattice slugs are NOT authored into the codebook (an
  axis with zero members is a hypothesis, not a ruling, and empty axes bloat the
  embedded codebook — the cost driver). A node INSTANTIATES the moment a
  quote-verified member arrives, no fresh ratification needed because the grammar was
  ratified.
- **Labeling discipline upgrade (fixes section-7 item 3 for good):** SYNTH may compose
  a slug from a ratified grammar and have it count as lane=codebook-grammar (new lane
  value) rather than lane=free — eliminating the near-miss invented-slug problem
  (etb-prefix confusion, synonymous equipment slugs) by making the composition rule
  deterministic. Anything not exact-codebook and not grammar-composable stays
  lane=free.
- Emit derives parents from grammar structure for free (stem = parent, facets =
  children), feeding the ratified derived-parents scheme. Existing seeded grammars:
  create-token-<type> (batch-5 D14), etb-create-token-<type> and
  leaves-battlefield-trigger-create-token-<type> (batch-5 D10 + this batch),
  targeted-<action>-<class> (M8 generalized, D3), activated-tap-or-untap-<scope> (D2),
  draw-second/cast-second prefix scheme (batch-5 D12). Code drafts the formal grammar
  file; Captain ratifies before the full pass.
- If lattice grammars prove not to help agent efficiency in practice, they get scraped
  per Captain — measure: rate of lane=free near-miss slugs per batch, before vs after.

### 11.3 Sequencing (amends batch-5 D17; registry update)
1. GATE #0 — legality gate implemented + retroactive scrub + precedent rescan (D1).
2. Keyword-bucket extraction (already ratified, unchanged).
3. COMBINED per-axis walk: naming audit + agent-legible definition rewrite +
   DET-ability classification + grammar drafting (one walk, four columns).
4. DET rule authoring + ratification + full-corpus DET pass (gate-passing cards).
5. Codebook condensation (largely automatic via DET strip).
6. SYNTH full-corpus pass (~$100 budget re-estimated post-gate/strip; explicit Captain
   trigger still required).
7. SCHEMA PASS (unchanged agenda + tap/untap consolidation + ownership facet + lattice
   formalization).
8. Display build per READY-TO-SHIP contract.

### 11.4 Language standard (Captain's stated goal)
Every rule name and definition must be understandable and reproducible by an agent with
no session context: grammar-composed slugs, closed facet vocabularies, glossary for
shorthand (scroll, regrowth), definitions that state trigger/cost/effect position
explicitly. This is the same standard as batch-5 D17's agent-legibility directive, now
extended: the naming audit is load-bearing for lattice derivation, DET patterns, and
parent derivation alike.

---

**STOP.** Sections 10–11 are the authoritative record for batch 6. Claude Code: execute
the FIND-AND-CONFIRM tasks (D1 scrub + precedent rescan, D6 roster, D7 appendix) and the
D1 gate BEFORE running `/triage-emit 6`; reorganization latitude per D6; halt loudly on
any ambiguity, failed gate, or unspecified decision. Then emit: parse §10, verify
every quote and member against the gate-passing corpus, write decisions/batch-6.json,
reconcile to codebook v0.6, restate the full-corpus count/cost post-gate, assemble
batch 7 from gate-passing cards only, and STOP for go-ahead.

---

## 12. Gate #0 execution report (D1, run 2026-07-30, before this document's emit)

**Implementation.** `foundry_common.gate_passes(card)` / `load_corpus_gated()` added to
`experiments/foundry_common.py`: a card passes iff any Scryfall `legalities` value is
`legal` or `restricted`. Scoped to the T3 Axis Foundry pipeline only (`foundry_common.py`'s
consumers) — `tier_engine.py`'s own `load_cards()`/`CARDS_PATH` path, used by production
tier scoring outside the foundry, is untouched. This is a scope decision I made rather than
silently guessed broad; flagging it explicitly so Captain can correct it if D1's "every
MTJawnny tool" was meant to reach the live tier engine too.

**Retroactive scrub** (`experiments/foundry_gate0_scrub.py`, run against codebook v0.5):
checked 3,085 member rows across all 362 axes (every status, not just active); removed
173 gated-out rows spanning 92 axes. Zero missing-from-corpus rows (no data-drift halt).
Determinism verified x2 byte-identical on the resulting member sets. Full report:
`experiments/out/foundry/gate0_scrub_report.json`. Named suspects from D1 confirmed:
Taiga Stadium (removed from rule:enters-tapped-conditional, as D1 anticipated) plus 91
other axes' gated members surfaced by the same mechanical rule (Cyclopean Titan, Gnome-Made
Engine, Item Crate, and 170 others — none previously flagged, all caught by the same
single mechanical check). Batch-6's own new candidates (Potatoes, Joraga Peach, Heart of a
Duelist, "Wizard") are handled separately at decisions/batch-6.json build time, per below —
they were never in codebook.json to begin with, since batch 6 hasn't been reconciled yet.

**"Wizard" resolved** (D1's specific ask): the corpus has exactly one card named "Wizard"
with the quoted restricted-purpose-mana ability — oracle_id `e2402676-...`, a Commander
Masters token (`set=tcmm`, `layout=token`), not_legal in every format. Gated. This is a
genuine token-card corpus row (not a data error) that will be dropped from
rule:restricted-purpose-mana's batch-6 confirmation when decisions/batch-6.json is built.

**Precedent rescan** (D1's second ask): walked every string value in `decisions/batch-1.json`
through `batch-5.json` and grepped `MASTER-HANDOFF.md`, `MASTER-HANDOFF-ADDENDUM-3.md`,
`SUP-TRIAGE-PROTOCOL.md`, `KEYWORD-LEDGER-CANDIDATES.md` for exact card-name matches,
checking every hit against Gate #0. Found 6 real card citations that fail the gate
(Exit Through the Grift Shop, Buzzing Whack-a-Doodle, Cyclopean Titan, Gnome-Made Engine,
Item Crate, Taiga Stadium) — all were already either historical member_removals (no live
effect) or live codebook members already caught and fixed by the retroactive scrub above.
**No dangling ratified rule turned out to rest solely on a now-gated card's evidence** —
the scrub and the rescan agree, which is the result I'd want to see, not one I'm assuming.
One real citation problem found and fixed: this document's own "Peel Out/Banana precedent"
line (struck above) — Peel Out was never a ratified precedent and is itself gated.

---

## 13. Batch-6 decisions/emit-time exclusions from Gate #0 [SUPERSEDED — see below]

The paragraph originally here (identifying 4 gated cards: Potatoes, Joraga Peach, Heart of
a Duelist, "Wizard") was **incomplete**. It was written before `decisions/batch-6.json` was
actually built. When `foundry_adapt_batch6_decisions.py` ran its belt-and-suspenders Gate
#0 re-check (checking every one of this batch's 756 confirmed member rows directly against
`foundry_common.gate_passes()`, not just the 4 named suspects), it HALTED on the very first
mismatch (**Everythingamajig**, an Unstable/`ust` card nobody had flagged). That halt was
correct behavior, not a bug — it caught that the manual 4-card list was a undercount.

**Full mechanical recheck result: 53 gated member-rows across 39 axes, 29 unique cards.**
The gated cards break cleanly into Scryfall `set_type` categories — all mechanically
nowhere-legal per Gate #0's literal rule, including categories D1's illustrative examples
didn't name explicitly (emblem, planar, memorabilia) but which are definitionally never
legal in any constructed format for the same underlying reason as the named categories:

- **funny** (Un-sets/joke sets — D1-named): Everythingamajig, Faerie Aerie, Fifth Stage of
  Magic Design, Heroes of Kamigawa, Joraga Peach, Peel Out, Photo Op, Potatoes, Save Point,
  Side to Side, Surprise Party, The Joiner of Cats, The Strixhaven-Lorwyn Rover, Timmy
  Power Gamer, Trivia Contest, Drive to Work, Voracious Vacuum
- **token** (bare token printings — D1-named): Bushy Bodyguard, Event: Rat King's
  Revolution, Map, "Wizard"
- **masters** (Mystery Booster playtest — D1-named): Heart of a Duelist, Lich's Duel Mastery
- **emblem** (not named by D1, but never deck-includable, same non-legal status): Mordenkainen
  Emblem, Rowan, Scholar of Sparks Emblem
- **planar** (Planechase plane cards, not named by D1, same non-legal status): Game
  Knights Live, The Lux Foundation Library
- **memorabilia** (not named by D1, promotional/non-tournament): Phoberos Reaver, The
  Vanquisher
- **alchemy** (Viconia, Disciple of Violence — this specific `hbg` printing's own
  legalities show it not_legal in every format including alchemy itself; does not
  contradict D1's "Alchemy-only cards still pass" clause, since that clause requires the
  card to actually BE alchemy-legal, which this printing isn't)

I flagged this scope question (does Gate #0's mechanical rule reach categories D1 didn't
explicitly name?) rather than silently deciding either way — concluded yes, apply the rule
literally as stated ("PASS iff any format value is legal or restricted... Everything else
FAILS"), since D1's named examples are illustrative, not an exhaustive closed list, and
narrowing the mechanical check to only the named categories would require inventing a
distinction D1's own text doesn't draw. Full list and per-axis breakdown in
`decisions/batch-6.json`'s `note_to_reconcile` field and each affected axis's `notes`.

Pick-a-Beeble (set=unf, Unfinity) passes Gate #0 mechanically, exactly as D1 anticipated;
it's removed from rule:activated-ability-costs-self-sacrifice on the independent D3 grounds
instead (Attraction Visit/Prize are triggered, not activated; the sacrifice sits inside the
Prize effect, not the cost).


---

## 14. MEMBER ROSTER — batch-6 contribution, post-corrections (D6, regenerated 2026-07-30)

Names only, no oracle text, per D6. Covers all 192 batch-6 axes plus the 3 new
captain-authored axes from D2/D3 (activated-tap-or-untap-any-permanent,
activated-untap-target-creature, leaves-battlefield-trigger-create-token-mutagen) = 195
rows. This is batch 6's OWN confirmation/new-candidate contribution after applying every
correction in sections 1-3, 12-13 (member_removals, member_additions, Gate #0 exclusions,
D2/D3 rehomes) — not each axis's total cumulative codebook membership (existing axes carry
additional members from batches 1-5 already in codebook.json; a "(n=0)" row below means
this batch's own example got fully excluded, not that the axis is empty in the codebook).

Generated by re-parsing the digest mechanically and applying every correction as code,
rather than re-typing 195 lists by hand — this caught two real bugs the prose sections
above didn't (both fixed before this roster was finalized, not left for Captain to catch):

1. **`rule:charge-counter-accumulation` double-count.** D3 said "member_addition(Culling
   Dais) — rehome from its removal above," but Culling Dais was already an independent
   batch-6-confirmed member of this axis on its own distinct quote ("Put a charge counter
   on this artifact," separate from the "draw a card for each charge counter" quote that
   got it removed from rule:draw-scaled-by-creature-count). No rehome was needed — D3's
   instruction and the pre-existing confirmation were about the SAME fact stated two ways.
   Fixed to avoid a duplicate member row; net effect on the axis is unchanged (Culling
   Dais was always going to end up here either way).
2. **`rule:death-trigger-counter-transfer` empties to n=0 this batch.** Joraga Peach was
   this axis's only batch-6 confirmation hit, and Joraga Peach is fully gated (Gate #0).
   Checked codebook.json directly: the axis already has 3 real members from batch 3, so
   this is not an orphaned/dying axis — it simply gets zero reinforcement from batch 6.
   Noted inline rather than silently dropped from the roster.

No other reorganization-worthy misfiles surfaced during roster generation beyond what
sections 1-3 already found and fixed; this list is mechanical, so anything already
corrected upstream propagates through cleanly.

- `rule:activated-ability-costs-self-sacrifice` (n=33): A-Skemfar Elderhall, Ark of Blight, Bad River, Booby Trap, Brittle Effigy, Burnished Hart, Cathar Commando, Culling Dais, Emberwilde Augur, Everythingamajig, Expert-Level Safe, Fanatical Firebrand, From Beyond, Kithkin Armor, Lawbringer, Lord of Tresserhorn, Map, Misty Palms Oasis, Moonsilver Key, Navigation Orb, Papalymo Totolymo, Pictures of Spider-Man, Racers' Ring, Relic of Progenitus, Save Point, Seal of Primordium, The Book of Vile Darkness, The Surgical Bay, Torch Fiend, Trivia Contest, Unyaro Griffin, Vexing Bauble, Witching Well
- `rule:activated-destroy-target-land` (n=2): Ark of Blight, Keldon Arsonist
- `rule:activated-draw-a-card` (n=9): A-Spell Satchel, Fungal Plots, Greed, Misty Palms Oasis, Racers' Ring, Relic of Progenitus, Staff of Domination, The Surgical Bay, Vexing Bauble
- `rule:activated-exile-graveyard-creature-card` (n=7): Abyssal Harvester, Conversion Chamber, Rag Dealer, Sibsig's Artisan, The Ooze, The Scarab God, Viconia, Disciple of Violence
- `rule:activated-exile-graveyard-creature-for-token` (n=2): Fungal Plots, Havengul Runebinder
- `rule:activated-loot` (n=2): Furtive Analyst, Strix Lookout
- `rule:activated-sacrifice-any-permanent-for-self-counter` (n=2): Dreadmobile, Sawblade Skinripper
- `rule:activated-tap-or-untap-any-creature` (n=1): Puppet Strings
- `rule:activated-tap-or-untap-any-permanent` (n=1): Fatestitcher
- `rule:activated-tap-target-creature` (n=9): Akroan Jailer, Burden of Guilt, Pacification Array, Silkbind Faerie, Staff of Domination, Steam Catapult, Thornscape Apprentice, Vengeful Villagers, Weakstone's Subjugation
- `rule:activated-untap-another-permanent` (n=2): Kelpie Guide, Vizier of Tumbling Sands
- `rule:activated-untap-target-creature` (n=2): High Alert, Staff of Domination
- `rule:activation-restricted-only-during-your-turn` (n=3): Circle of Elders, Gutterbones, Rag Man
- `rule:activation-restricted-to-own-upkeep` (n=1): Emberwilde Augur
- `rule:activation-restricted-to-sorcery-speed` (n=13): A-Skemfar Elderhall, Beetle, Legacy Criminal, Birthing Pod, Champion of the Weird, Endbringer's Revel, Gollum's Bite, Inside Source, Map, Najeela, the Blade-Blossom, Predation Steward, Scavenged Brawler, Sibsig's Artisan, Sultai Monument
- `rule:additional-cost-discard-a-card` (n=2): Big Score, Unexpected Windfall
- `rule:additional-cost-sacrifice-permanent` (n=1): Final Vengeance
- `rule:alt-cost-sacrifice-lands` (n=1): Dwarven Landslide
- `rule:animates-land-into-creature` (n=1): Creeping Tar Pit
- `rule:attack-trigger-create-token` (n=3): Sentinel of the Nameless City, Silverwing Squadron, The Spear of Leonidas
- `rule:attack-trigger-loot` (n=1): Vaultbreaker
- `rule:attack-trigger-mass-pump-attackers` (n=1): Ultra Magnus, Tactician // Ultra Magnus, Armored Carrier
- `rule:attack-trigger-pump-any-creature` (n=1): Yotian Frontliner
- `rule:attack-trigger-untap-attacker` (n=1): Tadeas, Juniper Ascendant
- `rule:aura-locks-enchanted-creature-tapped` (n=2): Frozen in Ice, Unquenchable Thirst
- `rule:buff-scales-with-land-type-count` (n=1): Lashwrithe
- `rule:burst-draw` (n=13): Aetherflux Conduit, Big Score, Birthday Escape, Blood Pact, Brokers Charm, Distant Memories, Dream Cache, Scatter Arc, Tragic Lesson, Unexpected Conversion, Unexpected Windfall, Weight of Memory, Witching Well
- `rule:cannot-block-restriction` (n=4): Dirty Wererat, Razorlash Transmogrant, Skrelv, Defector Mite, Visions of Brutality
- `rule:cant-be-blocked-by-color` (n=2): Lightning Mare, Vine Mare
- `rule:cant-be-countered` (n=3): Kavu Chameleon, Lightning Mare, Tyrranax Rex
- `rule:cantrip` (n=2): Provoke, Uncomfortable Chill
- `rule:cast-from-exile-trigger` (n=1): Fire Lord Zuko
- `rule:cast-from-top-of-library` (n=1): Into the Pit
- `rule:cast-trigger-transforms-into-creature` (n=1): Veiled Serpent
- `rule:changes-color-creature` (n=3): Distorting Lens, Possessed Nomad, Prismwake Merrow
- `rule:changes-creature-type-text` (n=2): Artificial Evolution, New Blood
- `rule:charge-counter-accumulation` (n=4): Conversion Chamber, Culling Dais, Private Research, Tidal Influence
- `rule:cheat-creature-into-play` (n=3): Cryptic Gateway, Ghalta, Stampede Tyrant, Timmy, Power Gamer
- `rule:choose-creature-type-on-etb` (n=2): Cover of Darkness, Lifecraft Engine
- `rule:combat-damage-to-player-draws-card` (n=2): Tadeas, Juniper Ascendant, The Lux Foundation Library
- `rule:combat-damage-triggers-discard` (n=2): Rakdos Ringleader, Zhang Liao, Hero of Hefei
- `rule:combat-damage-triggers-loot` (n=1): Prowler, Misguided Mentor
- `rule:combat-trick-pump-own-creature` (n=16): Aspirant's Ascent, Brokers Charm, Burrog Barrage, Enshrouding Mist, Fists of the Anvil, Gift of the Viper, Heroic Teamwork, Karametra's Blessing, Magic Damper, Predation Steward, Predator's Strike, Simic Charm, Staggering Size, Stonewood Invocation, Strength in Numbers, Temur Charm
- `rule:combat-trigger-auto-attach-equipment` (n=1): Ria Ivor, Bane of Bladehold
- `rule:compensates-controller-with-token` (n=2): Buy Your Silence, Hunted Bonebrute
- `rule:conditional-attack-restriction-by-opponent-land-type` (n=2): Red Cliffs Armada, Serpent of the Endless Sea
- `rule:conditional-creature-status` (n=1): Athreos, Shroud-Veiled
- `rule:copies-cast-spell` (n=4): Curse of Echoes, Mica, Reader of Ruins, Rowan, Scholar of Sparks Emblem, The Strixhaven-Lorwyn Rover
- `rule:copy-creature-token` (n=2): Aggressive Biomancy, Gigantoplasm
- `rule:cost-reduction` (n=10): Artist's Talent, Gargos, Vicious Watcher, Heroes of Kamigawa, Mana Matrix, Rhonas's Monument, The Destined Warrior, The Wind Crystal, Undead Warchief, Voyager Quickwelder, Zirda, the Dawnwaker
- `rule:counter-removal-as-activation-cost` (n=8): A-Spell Satchel, Academy Elite, Conversion Chamber, Fertilid, Glistener Seer, Grasping Shadows // Shadows' Lair, Noble's Purse, Predation Steward
- `rule:counters-noncreature-spell` (n=1): Scatter Arc
- `rule:counters-target-spell` (n=6): Glorious Gale, Horribly Awry, Sinister Sabotage, Statute of Denial, Thought Collapse, Unravel
- `rule:create-token-creature` (n=14): A-Skemfar Elderhall, Chatterstorm, Conversion Chamber, Depose // Deploy, Elemental Eruption, Fertile Imagination, Goblin Rally, Havengul Runebinder, Huatli, Warrior Poet, Side to Side, Sorin, Lord of Innistrad, Spirit Summoning, Wild Hypothesis, Wrangler of the Damned
- `rule:create-token-mana-producing-artifact` (n=2): Peel Out, Stone Retrieval Unit
- `rule:create-token-treasure` (n=10): Big Score, Bill Ferny, Bree Swindler, Buy Your Silence, Cindercone Smite, Depths of Desire, Guild Artisan, Noble's Purse, Pick-a-Beeble, Pictures of Spider-Man, Unexpected Windfall
- `rule:created-token-enters-tapped` (n=2): Illustrious Historian, The Final Days
- `rule:creates-token-with-x-scaled-counters` (n=1): Wild Hypothesis
- `rule:damage-divided-among-multiple-targets` (n=4): Huatli, Warrior Poet, Jaya's Immolating Inferno, Meteor Shower, Ureni, the Song Unending
- `rule:death-of-your-permanents-grows-this-creature` (n=1): Haruspex
- `rule:death-trigger-counter-transfer` (n=0): (none)  [Gate #0 emptied this batch's contribution; axis retains prior-batch members in codebook.json]
- `rule:death-trigger-scroll-regrowth` (n=1): Living Lightning
- `rule:death-trigger-token-creation` (n=2): Chasm Skulker, Hallowed Spiritkeeper
- `rule:delayed-draw-next-upkeep` (n=2): Gravebind, Heal
- `rule:direct-damage-any-target` (n=12): Banefire, Boilerbilges Ripper, Chandra, Heart of Fire, Fanatical Firebrand, Goblin Bangchuckers, Irencrag Pyromancer, Jaya's Immolating Inferno, Mudbutton Torchrunner, Prophetic Bolt, Seismic Wave, Spider-Man 2099, Staggershock
- `rule:doubles-counter-placement` (n=1): Michelangelo, Weirdness to 11
- `rule:drain-life` (n=4): Acolyte of Aclazotz, Dakmor Ghoul, Mind Drain, Triumphant Getaway
- `rule:drain-on-creature-death` (n=1): Bastion of Remembrance
- `rule:draw-cards-with-life-loss-cost` (n=4): Bitter Revelation, Blood Pact, Grasping Shadows // Shadows' Lair, Sanguimancy
- `rule:draw-scaled-by-creature-count` (n=3): Biomantic Mastery, Camaraderie, Winged Portent
- `rule:draw-second-card-trigger-plus1-counter` (n=1): Codespell Cleric
- `rule:draw-trigger-self-counter-growth` (n=2): Agent Maria Hill, Chasm Skulker
- `rule:enters-tapped` (n=26): A-Skemfar Elderhall, Alirios, Enraptured, Bad River, Caldera Lake, Carrion Crow, Creeping Tar Pit, Elvish Rejuvenator, Forgotten Sentinel, Gutterbones, Highland Weald, Memorial to War, Mistvault Bridge, Misty Palms Oasis, Mountain Valley, Noble's Purse, Nomad Outpost, Path to the Festival, Racers' Ring, Retrofitted Transmogrant, Revenge of the Rats, Swiftwater Cliffs, The Falcon, Airship Restored, The Surgical Bay, Thornglint Bridge, Woodland Stream, Xander's Lounge
- `rule:enters-tapped-conditional` (n=5): Arena of Glory, Frostboil Snarl, Minas Tirith, Shattered Sanctum, Wild Roads
- `rule:etb-and-attack-trigger` (n=6): Borborygmos and Fblthp, Kami of Transmutation, Omo, Queen of Vesuva, Sentinel of the Nameless City, Sidisi, Brood Tyrant, Vengeful Ancestor
- `rule:etb-auto-attach-to-own-creature` (n=4): Maul of the Skyclaves, Piston Sledge, Rosethorn Halberd, Thunder Lasso
- `rule:etb-bounce-other-creature` (n=2): Monk Class, Separatist Voidmage
- `rule:etb-counter-on-other-creature` (n=9): Aerie Auxiliary, Ascendant Dustspeaker, Clay Champion, Grafted Growth, Inspired Inventor, Restorative Technique, Sandskitter Outrider, Trufflesnout, Voracious Vacuum
- `rule:etb-create-token` (n=6): Gilded Goose, Glacier Godmaw, Niko, Light of Hope, Overencumbered, Sentinel of the Nameless City, Welcome to . . . // Jurassic Park
- `rule:etb-create-token-creature` (n=23): Alirios, Enraptured, Bastion of Remembrance, Brood Butcher, Charforger, Clarion Cathars, Edgewall Pack, Faerie Aerie, Falcon Abomination, Farmer Cotton, Firebender Ascension, Ghired, Conclave Exile, Hero of the Nyxborn, Huatli, Poet of Unity // Roar of the Fifth People, Illustrious Historian, Inside Source, Inspired Inventor, Okoye, Dora Milaje Leader, Scion Summoner, Scurry of Gremlins, Secure Detention, Spiked Corridor // Torture Pit, Tempt with Bunnies, Whirler Rogue
- `rule:etb-create-token-creature-conditional` (n=3): Nightsquad Commando, Venser, Corpse Puppet, Verix Bladewing
- `rule:etb-create-token-food` (n=2): Farmer Cotton, Samwise Gamgee
- `rule:etb-create-token-mutagen` (n=5): Genghis Frog, Michelangelo, Weirdness to 11, Raphael, the Muscle, The Ooze, Zoo Escapees
- `rule:etb-destroy-target-enchantment` (n=3): Brokers Charm, War Priest of Thune, Wispmare
- `rule:etb-draw-card` (n=6): Elvish Visionary, Rune of Flight, Save Point, Spirited Companion, Stupefying Touch, Woodland Acolyte // Mend the Wilds
- `rule:etb-exile-graveyard-card` (n=2): Lich's Duel Mastery, Mastermind Plum
- `rule:etb-gain-life` (n=7): Arborback Stomper, Dawning Angel, Shu Grain Caravan, Swiftwater Cliffs, Thragtusk, Trufflesnout, Windgrace Acolyte
- `rule:etb-loot` (n=3): Quicksilver Fisher, Statute of Denial, Viashino Racketeer
- `rule:etb-mass-pump-your-creatures` (n=1): Moonshaker Cavalry
- `rule:etb-modal-choice` (n=6): Coliseum Behemoth, Inspired Inventor, Primaris Eliminator, Sandskitter Outrider, Trufflesnout, Wingbane Vantasaur
- `rule:etb-pump-target-creature` (n=2): Herald of the Fair, Yeva's Forcemage
- `rule:etb-scry` (n=2): Lazav, the Multifarious, Witching Well
- `rule:etb-tutor-to-hand` (n=5): Farfinder, Fierce Empath, Huatli, Poet of Unity // Roar of the Fifth People, Spellseeker, Sphinx Summoner
- `rule:etb-with-counters` (n=13): Aether Figment, Bushy Bodyguard, Fertilid, Fifth Stage of Magic Design, Frontier Mastodon, Molly Hayes, Runaway, Morlun, Devourer of Spiders, Noble's Purse, Phantom Flock, Razorlash Transmogrant, Retrofitted Transmogrant, Tidal Influence, Zoanthrope
- `rule:etb-with-negative-counters` (n=2): Bristlebane Battler, Morselhoarder
- `rule:etb-with-oil-counters` (n=2): Glistener Seer, Predation Steward
- `rule:evasion-vs-high-power-blockers` (n=2): Kithkin Armor, Tadeas, Juniper Ascendant
- `rule:evasion-vs-low-power-blockers` (n=2): Hierophant Bio-Titan, Prowler, Misguided Mentor
- `rule:exile-until-source-leaves` (n=4): Chained to the Rocks, Constricting Sliver, Drive to Work, Lumbering Battlement
- `rule:fixed-lifegain` (n=9): Ivory Crane Netsuke, Last Kiss, Path of Peace, Ray of Dissolution, Recumbent Bliss, Soul Shred, Staff of the Sun Magus, Swallowing Plague, Vengeant Vampire
- `rule:forced-attack-each-combat` (n=5): Berserkers of Blood Ridge, Curse of the Nightly Hunt, Guise of Fire, Phoberos Reaver, Sprinting Warbrute
- `rule:forced-hand-reveal` (n=1): Struggle for Sanity
- `rule:forces-creature-to-attack` (n=1): Heckling Fiends
- `rule:forces-creature-to-be-blocked` (n=2): Irresistible Prey, Provoke
- `rule:forces-opponent-sacrifice` (n=1): Vindictive Lich
- `rule:free-cast` (n=4): Aetherflux Conduit, Extract Brain, Guff Rewrites History, Spelltwine
- `rule:free-sacrifice-outlet` (n=1): Acolyte of Aclazotz
- `rule:gives-energy-counters-immediately` (n=3): Consulate Surveillance, Inspired Inventor, Servant of the Conduit
- `rule:grants-ability-at-threshold-board` (n=1): Zegana, Utopian Speaker
- `rule:grants-ability-at-threshold-self` (n=3): Dirty Wererat, Possessed Nomad, Swarmborn Giant
- `rule:grants-additional-combat-phase` (n=4): Lightning Runner, Najeela, the Blade-Blossom, Save Point, Scourge of the Throne
- `rule:grants-creature-type` (n=3): Avatar Destiny, Captain's Hook, Samurai's Katana
- `rule:grants-extra-turn` (n=1): Ultimecia, Time Sorceress // Ultimecia, Omnipotent
- `rule:grants-haste-to-created-tokens` (n=2): Lightning Coils, Welcome to . . . // Jurassic Park
- `rule:grants-haste-to-your-creatures` (n=2): Gimli's Reckless Might, Push the Limit
- `rule:grants-trample-to-other-creatures` (n=2): Aggressive Mammoth, Brawn
- `rule:grants-unblockable-target` (n=1): Jailbreak Scheme
- `rule:graveyard-to-hand-recursion` (n=4): Endbringer's Revel, Jared Carthalion, Myr Reservoir, Restock
- `rule:graveyard-to-library-shuffle-in` (n=2): Memory's Journey, Stroke of Luck
- `rule:graveyard-to-library-top-recursion` (n=3): False Mourning, Treason of Isengard, Woodland Acolyte // Mend the Wilds
- `rule:individual-cost-reduction` (n=4): Hollow Marauder, Khalni Hydra, Melek, Reforged Researcher, Writhing Necromass
- `rule:innate-unblockable` (n=3): Aether Figment, Creeping Tar Pit, Vedalken Infiltrator
- `rule:kicker-conditional-bonus-effect` (n=8): Aether Figment, Bog Badger, Dauntless Unity, Dwarven Landslide, Heroic Teamwork, Orim's Chant, Temporal Firestorm, Verix Bladewing
- `rule:land-fetch-to-battlefield` (n=4): Bad River, Cartographer's Survey, Elvish Rejuvenator, Navigation Orb
- `rule:landfall-gain-life` (n=1): Grazing Gladehart
- `rule:landfall-self-pump` (n=1): Glacier Godmaw
- `rule:leaves-battlefield-returns-exiled-card` (n=3): Aurelia's Vindicator, Champion of the Weird, Wormfang Turtle
- `rule:leaves-battlefield-trigger-create-token-creature` (n=1): Thragtusk
- `rule:leaves-battlefield-trigger-create-token-mutagen` (n=1): Zoo Escapees
- `rule:level-up-scaling-stats-abilities` (n=2): Monk Class, Skywatcher Adept
- `rule:library-dig-put-onto-battlefield` (n=1): The Joiner of Cats
- `rule:library-dig-to-hand` (n=3): Anticipate, Militia Bugler, Prophetic Bolt
- `rule:library-top-visibility` (n=1): Into the Pit
- `rule:life-total-reset` (n=1): Form of the Dragon
- `rule:lifegain-scaled-by-creature-count` (n=2): Camaraderie, Depose // Deploy
- `rule:lifegain-scaled-by-permanent-color-count` (n=2): Breathe Your Last, Treva, the Renewer
- `rule:lifegain-triggered-counter` (n=1): Gideon's Company
- `rule:mana-activated-pump-self` (n=8): A-Kargan Intimidator, Cursed Ronin, Freejam Regent, Igneous Cur, Jetmir's Fixer, Lightning Mare, Minotaur Sureshot, Vengeful Firebrand
- `rule:mass-counter-distribution` (n=5): Fire Lord Zuko, Havengul Runebinder, Nykthos Paragon, Silkguard, Vault 12: The Necropolis
- `rule:mass-creature-destruction` (n=3): No Witnesses, Sublime Exhalation, The Nipton Lottery
- `rule:mass-damage-creatures-and-players` (n=1): Temporal Firestorm
- `rule:mass-damage-opponent-creatures-only` (n=2): Cosmotronic Wave, Seismic Wave
- `rule:mass-debuff-opponent-creatures` (n=3): A-Skemfar Elderhall, Primaris Eliminator, Uncomfortable Chill
- `rule:mass-graveyard-exile` (n=3): Erebos's Intervention, Identity Crisis, Relic of Progenitus
- `rule:mass-pump-your-creatures` (n=5): Camaraderie, Dauntless Unity, Esquire of the King, Morale, Rush of Battle
- `rule:mass-untap-and-haste-stolen-creatures` (n=2): Smelt-Ward Gatekeepers, Twisted Fealty
- `rule:mass-untap-your-creatures` (n=5): Lightning Runner, Najeela, the Blade-Blossom, Save Point, Scourge of the Throne, The Nipton Lottery
- `rule:mill-self-cards` (n=4): Avatar Destiny, Founding the Third Path, Grizzled Angler // Grisly Anglerfish, Windgrace Acolyte
- `rule:modal` (n=9): Brokers Charm, Epic Fight, Erebos's Intervention, Heliod's Intervention, Mastermind's Acquisition, Plunge into Darkness, Simic Charm, Temur Charm, Vindictive Lich
- `rule:no-maximum-hand-size` (n=3): Mordenkainen Emblem, The Lux Foundation Library, The Vanquisher
- `rule:partner-with-tutor` (n=2): Khorvath Brightflame, Regna, the Redeemer
- `rule:pay-life-cost-for-effect` (n=4): Everythingamajig, Greed, Living Airship, Shessra, Death's Whisper
- `rule:plus1-counters-matter` (n=4): Craig Boone, Novac Guard, Herald of Secret Streams, Lux Artillery, Sapphire Drake
- `rule:populate-copy-creature-token` (n=2): Ghired, Conclave Exile, Mirror-Sigil Sergeant
- `rule:postcombat-main-phase-trigger` (n=2): Belbe, Corrupted Observer, Florian, Voldaren Scion
- `rule:power-scales-with-creature-count` (n=1): Silverwing Squadron
- `rule:prevent-all-combat-damage-this-turn` (n=2): Peel Out, Respite
- `rule:prevent-fixed-damage-any-target` (n=4): Acolyte's Reward, Heal, Kithkin Armor, Rakalite
- `rule:prevents-damage-prevention` (n=1): Insult // Injury
- `rule:prevents-damage-to-self` (n=2): Inviolability, Solitary Confinement
- `rule:prevents-regeneration` (n=5): Gravebind, Murderous Betrayal, Necrite, Nekrataal, Rage of Purphoros
- `rule:prevents-target-blocking` (n=1): Untimely Malfunction
- `rule:reanimate-from-graveyard` (n=4): Aerith, Last Ancient, Corpse Dance, Heroes of Kamigawa, Timely Hordemate
- `rule:redirect-targets-of-spell-or-ability` (n=3): Rebound, Ricochet Trap, Untimely Malfunction
- `rule:restricted-purpose-mana` (n=4): Herd Heirloom, Myr Reservoir, Nardole, Resourceful Cyborg, Stone Retrieval Unit
- `rule:restricts-blocking-to-flying-only` (n=1): Rishadan Brigand
- `rule:rhystic-tax` (n=3): Crush Dissent, Logic Knot, Stench of Evil
- `rule:sacrifice-for-creature-token` (n=1): Sultai Monument
- `rule:scales-mana-by-count` (n=1): Welcome to . . . // Jurassic Park
- `rule:scales-token-count-with-x` (n=1): Aggressive Biomancy
- `rule:self-bounce-activated` (n=1): Sliptide Serpent
- `rule:self-exile-after-resolution` (n=4): Divergent Equation, Reap the Past, Restock, Spelltwine
- `rule:self-recursion-from-graveyard` (n=4): Gutterbones, Razorlash Transmogrant, Retrofitted Transmogrant, The Falcon, Airship Restored
- `rule:sets-base-power-or-toughness` (n=5): Ascendant Spirit, Oko's Hospitality, Suit Up, Tezzeret the Schemer, Veiled Sentry
- `rule:skips-controller-draw-step` (n=1): Solitary Confinement
- `rule:stun-counter` (n=3): Event: Rat King's Revolution, Twisted Riddlekeeper, Vengeful Villagers
- `rule:targeted-bounce-creature` (n=5): Champion's Victory, Consuming Vortex, Depths of Desire, Otawara, Soaring City, Simic Charm
- `rule:targeted-creature-damage` (n=16): Arrows of Justice, Cindercone Smite, Command the Storm, Corrupt Eunuchs, Devour in Flames, Feed the Flames, Flame Slash, Hamato Ninpō, Helicarrier Strike, Insult // Injury, Last Kiss, Legolas, Master Archer, Puncture Bolt, Rage of Purphoros, Soul Shred, Swallowing Plague
- `rule:targeted-destruction` (n=27): Breathe Your Last, Cathar Commando, Dark Betrayal, Deadly Alliance, Destructive Revelry, Disenchant, Dwarven Landslide, Feed the Cycle, Heliod's Intervention, Icequake, Murderous Betrayal, Neck Snap, Nekrataal, Nissa's Defeat, Path of Peace, Primaris Eliminator, Puncturing Light, Sagittars' Volley, Seal of Primordium, Shoot the Sheriff, Sorin, Lord of Innistrad, Torch Fiend, Untimely Malfunction, Vengeance, Vengeant Vampire, Verdigris, Wild Swing
- `rule:targeted-discard` (n=3): Hollow Marauder, Mind Drain, Vindictive Lich
- `rule:targeted-exile` (n=5): Angel of Deliverance, Brittle Effigy, Buy Your Silence, Final Vengeance, Grip of Desolation
- `rule:targeted-planeswalker-damage` (n=5): Burning Fields, Chandra's Outburst, Devour in Flames, Emberwilde Augur, Insult // Injury (Injury face)
- `rule:targeted-player-damage` (n=6): Burning Fields, Chandra's Outburst, Concert Kaboomist, Emberwilde Augur, Insult // Injury, Morlun, Devourer of Spiders
- `rule:taxes-opponent-spell-cost` (n=1): Chill
- `rule:temporary-control-theft` (n=4): New Blood, Smelt-Ward Gatekeepers, The Nipton Lottery, Twisted Fealty
- `rule:temporary-keyword-grant` (n=5): Beetle, Legacy Criminal, Graviton, Fundamental Force, Rush of Vitality, Staggering Size, Venser, Corpse Puppet
- `rule:the-ring-tempts-you` (n=6): Birthday Escape, Glorious Gale, Gollum's Bite, Horses of the Bruinen, Ravenloft Adventurer, Took Reaper
- `rule:token-count-scales-with-graveyard-creature-count` (n=3): Hallowed Spiritkeeper, Revenge of the Rats, The Final Days
- `rule:token-count-scales-with-x` (n=3): Farmer Cotton, Path of the Ghosthunter, Forth Eorlingas!
- `rule:token-sacrifice-for-mana` (n=3): Brood Butcher, Glimpse the Impossible, Skittering Precursor
- `rule:tribal-anthem-buff` (n=10): Angel of Invention, Banner of Kinship, Chief of the Scale, Game Knights Live, Kargan Warleader, Lifecraft Engine, Quintorius, Field Historian, Stormscale Scion, Surprise Party, Undead Warchief
- `rule:triggers-on-cast-instant-sorcery` (n=3): Glacierwood Siege, Mica, Reader of Ruins, Rowan, Scholar of Sparks Emblem
- `rule:tutor-from-outside-game-to-hand` (n=2): Mastermind's Acquisition, Photo Op
- `rule:untaps-target-land` (n=1): Ley Weaver
- `rule:x-scales-with-permanent-count` (n=1): Khalni Hydra

---

## 15. D7 diagnosis: recently-killed appendix (2026-07-30)

**The appendix mechanism is built and correctly wired** — verified directly against the
actual API request payload sent for batch 6
(`experiments/out/foundry/stage1b_requests_batch6.json`): the system prompt's
`RECENTLY KILLED` block contains all 75 killed slugs verbatim, including both
`rule:equipment-grants-stat-buff` and `rule:equipment-static-pt-buff` — the exact two
strings SYNTH then re-proposed as lane=codebook matches for Rosethorn Halberd and Maul of
the Skyclaves. This is not a missing-plumbing bug; `load_recently_killed_reference()` ran
and its output reached the model.

**Root cause: model compliance, not wiring.** The batch-6 SYNTH call runs with
`"thinking": {"type": "disabled"}` — single-pass generation, no deliberation step. The
killed-slug list is a bare 75-item comma-separated string with no definitions or examples
attached (by design, to control prompt-growth cost — see the docstring in
`foundry_stage1b.py`). Cross-referencing a candidate label against a 75-item list is
exactly the kind of "read the whole list, then check" step that degrades without a
reasoning pass; the model appears to independently reconstruct the same natural vocabulary
for "equipment gives a static P/T buff" (a very obvious slug name) without reliably
checking it against the list before emitting it. This is now 3 batches running (killed
batch 3, resurrected batch 5 — which is why the appendix was built — resurrected again
batch 6 despite the appendix being present and correct).

**Fix implemented now (deterministic, not another prompt tweak):** added a third anomaly
category to `foundry_digest.py`'s `find_anomalies()` — any OTHER-lane row whose label
starts with `"rule:"` is flagged in the digest's Anomalies section (new
"OTHER-lane rows with an invalid 'rule:' prefix" subsection), since a genuine lane=free
label should never carry that prefix. This catches BOTH failure modes (killed-slug
resurrection and near-miss invented slugs like the Stone Retrieval Unit case) mechanically,
every batch, without depending on SYNTH prompt compliance or a reviewer noticing it by
manual grep — which is how all 3 of this batch's instances were actually found. Regenerated
digest-batch-6.md confirms it catches exactly the 3 known instances (Maul of the Skyclaves,
Rosethorn Halberd, Stone Retrieval Unit) and nothing else.

**Recommendation for batch 7+ (not implemented — a prompt/cost tradeoff for Captain, not a
unilateral call):** if this keeps recurring, consider enabling thinking for the SYNTH call
specifically when the killed-list check matters, or restructuring the prompt to require an
explicit "does this candidate label match anything in RECENTLY KILLED — yes/no" line before
the final answer. Both cost more tokens per card; given the digest-side catch now makes
this a zero-cost review-time flag rather than a silent miss, I'd defer that tradeoff to
Captain rather than spend batch-7 budget on it preemptively.


