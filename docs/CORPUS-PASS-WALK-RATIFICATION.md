# CORPUS-PASS-PLAN steps 2–3 — combined walk ratification document

> ## RESOLUTION (2026-07-31)
> Every open question and proposal in this document has been ruled on and
> applied. The complete ruling set and execution record live in
> `docs/WALK-RATIFICATION-EXECUTION-HANDOFF.md` (Captain's rulings, section 2)
> and its own execution — codebook.json is now v0.7 with 305 active axes (23
> renames + 1 kill applied), `docs/grammars.json` and
> `docs/CODEBOOK-NAMING-GRAMMAR.md` were updated (Q2/Q3/F3/Q5/F4/Q6/Q8/Q9),
> and `docs/det-patterns-v1.json` holds the final 42 ratified DET patterns.
> **Everything below this line is now HISTORICAL** — the proposal state as it
> stood before ratification, kept for audit trail. Do not treat it as current
> codebook/grammar/pattern state; read the execution handoff doc instead.

Status (as of the original 2026-07-30 run): **PROPOSALS ONLY. Nothing in this document has been executed.**
`codebook.json` is untouched by this session — no rename, merge, status
change, or DET pattern has been applied to it. Everything below is input
for Captain to ratify or reject, the same discipline as every prior
SUP-triage batch (`docs/SUP-TRIAGE-PROTOCOL.md`) and the naming grammar
itself (`docs/CODEBOOK-NAMING-GRAMMAR.md` §13).

Run: 2026-07-30, against codebook v0.7 (306 active axes, `batches_reconciled
[1..7]`) and the CR effective June 19, 2026.

Inputs read: `docs/MASTER-HANDOFF.md`, `docs/MASTER-HANDOFF-ADDENDUM-2.md`,
`docs/MASTER-HANDOFF-ADDENDUM-3.md`, `docs/CORPUS-PASS-PLAN.md`,
`docs/CODEBOOK-NAMING-GRAMMAR.md`.

Artifacts produced this session (file manifest, §6 has the full list):
`experiments/foundry_keyword_buckets.py`, `experiments/out/foundry/keyword-buckets.json`,
`experiments/out/foundry/keyword-buckets_report.md`, `experiments/validate_slug.py`,
`docs/grammars.json`, `experiments/out/foundry/validate_slug_report.json`,
`experiments/foundry_axis_walk.py`, `experiments/out/foundry/axis_walk_scaffold.json`,
`experiments/foundry_det_patterns_probe.py`, `experiments/out/foundry/det_patterns_probe.json`,
this document.

---

## 1. Step 2 — keyword-bucket extraction (DET job)

Mechanical extraction over CR 702 (Keyword Abilities), 193 keyword entries
(194 after splitting Daybound-and-Nightbound into two independently-cited
slugs). Every classification cites its CR sub-rule; verify-or-drop applied
throughout — no bucket was force-fit.

### 1.1 Bucket counts

| Bucket | Count | Notes |
|---|---:|---|
| static | 77 | |
| triggered | 46 | |
| activated | 24 | |
| hybrid | 23 | genuinely mixed classes (e.g. Modular = static+triggered) |
| evasion | 8 | Flying, Menace, Skulk, Fear, Intimidate, Shadow, Horsemanship, Landwalk |
| special-action | 3 | Plot, and 2 others whose CR text literally says "is a special action" |
| characteristic-defining | 2 | Changeling, Devoid |
| spell | 1 | Ascend (also Epic/Paradigm, folded into "spell" via the typed-multi rule) |
| rules-modifying | 1 | Partner (deck-construction rule, not a game ability) |
| ambiguous-card-dependent | 1 | Solved (Case cards — genuinely varies by printed text, can't be fixed to one class) |
| **unclassified (verify-or-drop)** | **8** | CR states no fixed class at all — see 1.2 |

### 1.2 Verify-or-drop residual (8 keywords, correctly NOT force-fit)

| Keyword | CR | Why it can't be classified |
|---|---|---|
| Fading | 702.32 | "represents two abilities" with no type word stated |
| Vanishing | 702.63 | same shape as Fading |
| Offspring | 702.175 | "represents two abilities," no type word |
| Disturb | 702.146 | no class statement at all |
| Read Ahead | 702.155 | no class statement at all |
| Space Sculptor | 702.158 | no class statement at all |
| Visit | 702.159 | no class statement (structurally reads as triggered — "Whenever you roll..." — but CR never says so explicitly; left unclassified rather than inferred) |
| Living Metal | 702.161 | no class statement at all |

These are genuinely open — resolving them would require inferring from
the quoted reminder-text structure rather than an explicit CR statement,
which this job deliberately declines to do (verify-or-drop, not recall).

### 1.3 Taxonomy corrections vs. addendum-3's original assumption

Addendum-3 §4 assumed a flat 5-bucket taxonomy (static / triggered /
activated / hybrid / casting-modifier). Verification against the real CR
text found this wrong on two counts, both worth ratifying explicitly:

1. **"casting-modifier" is not a CR ability class.** CR classifies Flash,
   Convoke, Kicker, Delve, etc. as ordinary classes (mostly `static`) whose
   *text* happens to modify casting. This job keeps the CR-cited base class
   and adds a **separate, orthogonal, non-CR-anchored heuristic flag**
   `casting_modifier_heuristic` (55 keywords hit it — Equip, Flash, Morph,
   Affinity, Cascade, Emerge, Escape, Level Up, Mutate, Foretell, Plot, and
   more). **Proposal: retire "casting-modifier" as a peer bucket; keep it as
   a facet.**
2. **Real CR ability classes the original 5-bucket list missed:** `evasion`,
   `characteristic-defining`, `spell` (as in "spell ability," CR 113.3a),
   `replacement` (614.1, zero hits this pass but a real class), and
   `special-action` (116). **Proposal: adopt the 9-bucket taxonomy in §1.1
   as the ratified closed vocabulary**, superseding addendum-3 §4.

### 1.4 Trigger-family gaps (DELIVERY closed vocabulary)

Three triggered keywords don't match any closed-vocabulary trigger family
from `CODEBOOK-NAMING-GRAMMAR.md` §2: **Ward** (702.21a, "becomes the target
of a spell or ability" — a *becomes-targeted* trigger), **Recover** (702.59a,
"a creature is put into your graveyard" — a *graveyard-event* trigger, not
self-referential), **Training** (702.149a, an *attack-trigger* variant with
an attacker-count condition baked in). **Proposal:** add
`becomes-targeted-trigger` to the closed DELIVERY vocabulary (Ward's family;
also covers any future `rule:` axis about "becomes the target of"). Recover
and Training are thin (1 keyword each) and are better left as per-keyword
exceptions than new vocabulary — logged, not resolved here.

Separately, **`blocks-or-becomes-blocked-trigger`** (Bushido, Flanking,
Rampage, Afflict) is a real, recurring CR trigger shape entirely absent
from the closed DELIVERY vocabulary. **Proposal: add it** — it will be
needed the moment any `rule:` axis about blocking triggers is authored.

### 1.5 Internal inconsistency found in CODEBOOK-NAMING-GRAMMAR.md itself

§2's DELIVERY table lists the slot value for the graveyard-from-battlefield
family as literally `dies`. §13 D-1 ratifies **`death-trigger`** as the
family word ("No `dies-` slugs"), in the same document. This job followed
D-1 (the explicit, later ratification) throughout — every `death-trigger-*`
codebook axis and this job's own DELIVERY classification use
`death-trigger`, never `dies`. **Flagging for a one-line editorial fix to
§2's table** (change the printed slot value from `dies` to `death-trigger`)
so the document stops contradicting itself.

### 1.6 Mobilize — resolved

Addendum-3 flagged Mobilize as "not yet verified." It is present at CR
702.181 (triggered, attack-trigger family, verified this session — not a
gap after all).

---

## 2. Step 3 — combined per-axis walk (306 active codebook axes)

### 2.1 Method

`experiments/foundry_axis_walk.py` produces a per-axis scaffold (delivery/
cost/effect decomposition, first-pass DET/SYNTH signal detection, grammar-
family match) for all 306 active axes, cross-referencing
`validate_slug.py`'s grammar-conformance result for each. The DET/SYNTH
signal pass and every proposed rename below were then reviewed and refined
by hand — the scaffold accelerates the walk, it doesn't replace the
judgment call. Full per-axis output (all 306 rows) lives in
`experiments/out/foundry/axis_walk_scaffold.json`; this document surfaces
the load-bearing subset (real renames, DET candidates, grammar drafts, open
questions) rather than reprinting all 306 rows.

### 2.2 Grammar validation — full rename set

`validate_slug.py --batch`: **87/306 clean**, 219 flagged. Of the 219,
**198 fail *only* on `unknown_vocabulary`** (structurally valid slugs using
English descriptive words — `creatures`, `other`, `library`, `targets`,
`ability`, `prevents`... — that aren't in the grammar's closed vocabulary).
The remaining **21 have a genuine structural finding**. This is the load-
bearing distinction: 21 slugs need an actual rename decision; 198 need a
*policy* decision (§2.2.3), not 198 individual rulings.

#### 2.2.1 Genuine structural renames (19 slugs, all mechanical, tied to already-ratified rules)

**D-3 (`-scaled-by-` → `-scales-with-`), 15 slugs — the connective is
already ratified, this is pure mechanical migration:**

| Current | Proposed |
|---|---|
| `rule:attack-trigger-pump-scaled-by-creature-count` | `rule:attack-trigger-pump-scales-with-creature-count` |
| `rule:cost-reduction-scaled-by-attackers` | `rule:cost-reduction-scales-with-attacker-count` |
| `rule:cost-reduction-scaled-by-legendary-creature-count` | `rule:cost-reduction-scales-with-legendary-creature-count` |
| `rule:cost-reduction-scaled-by-lifegain` | `rule:cost-reduction-scales-with-life-gained` |
| `rule:damage-scaled-by-hand-size` | `rule:damage-scales-with-hand-size` |
| `rule:death-trigger-token-scaled-by-power` | `rule:death-trigger-token-scales-with-power` |
| `rule:draw-scaled-by-creature-count` | `rule:draw-scales-with-creature-count` |
| `rule:draw-scaled-by-opponent-tapped-creatures` | `rule:draw-scales-with-opponent-tapped-creature-count` |
| `rule:life-loss-scaled-by-card-mana-value` | `rule:life-loss-scales-with-mana-value` |
| `rule:lifegain-scaled-by-creature-count` | `rule:lifegain-scales-with-creature-count` |
| `rule:lifegain-scaled-by-mana-value` | `rule:lifegain-scales-with-mana-value` |
| `rule:lifegain-scaled-by-permanent-color-count` | `rule:lifegain-scales-with-color-count` |
| `rule:lifegain-scaled-by-sacrificed-creature-toughness` | `rule:lifegain-scales-with-sacrificed-creature-toughness` |
| `rule:mass-damage-flying-creatures-scaled-by-x` | `rule:mass-damage-flying-creatures-scales-with-x` |
| `rule:pump-scaled-by-own-creature-count` | `rule:pump-scales-with-own-creature-count` |

Note: `rule:cost-reduction-scales-with-own-counters` already uses the
correct connective and needs no rename (it was flagged only for the
separate `bare_counter_noun` question, resolved as a pass — "own-counters"
is explicitly in the §7 closed stat vocabulary).

**D-2 (bare verb stem), 1 slug:**

| Current | Proposed |
|---|---|
| `rule:equipment-etb-creates-and-attaches-token` | `rule:equipment-etb-create-and-attach-token` |

**Counter-law §8.1 (typed counter, not bare noun), 2 slugs — both verified
against their own definitions to be +1/+1 counters specifically:**

| Current | Proposed |
|---|---|
| `rule:activated-sacrifice-any-permanent-for-self-counter` | `rule:activated-sacrifice-any-permanent-for-self-plus1-counter` |
| `rule:combat-damage-to-player-triggers-self-counter` | `rule:combat-damage-to-player-triggers-self-plus1-counter` |

**Banned-token (participle "countered"), 1 slug — needs a Captain naming
call, not auto-fixed (no clean single-token replacement exists in the
current vocabulary):**

| Current | Options (pick one) |
|---|---|
| `rule:cant-be-countered` | `rule:spell-uncounterable` (new vocab token "uncounterable," parallels "unblockable") — **recommended**, or `rule:immune-to-counterspells` (reuses "counterspells" as a new compound token) |

(`rule:free-cast` and `rule:free-sacrifice-outlet` were also flagged by an
earlier, over-strict version of the `free_must_be_free` check during this
session — both definitions do quote a genuine zero-cost ("without paying
its mana cost," "at no mana cost"), so on inspection **neither needs a
rename**; the checker was corrected mid-walk, see `validate_slug.py` git
history in this session.)

#### 2.2.2 Vocabulary-question backlog (198 slugs) — policy proposal, not 198 renames

The 198 `unknown_vocabulary`-only slugs are not naming violations in the
usual sense — codebook v0.1–v0.7 was built almost entirely *before*
`CODEBOOK-NAMING-GRAMMAR.md` existed (ratified today, 2026-07-30), using
natural descriptive English rather than the grammar's closed slot
vocabulary. Forcing 198 renames now would contradict the already-ratified
**"No midflight renames"** rule (addendum-2 §4: "naming standardization is
a FINAL AUDIT punch item; renames logged, not executed"). **Proposal:**

1. **Extend the closed vocabulary** with the ~40 most common legitimate
   structural/descriptive tokens surfacing across these 198 slugs —
   `creatures`, `other`, `on`, `from`, `library`, `triggers`, `ability`,
   `and`, `by`, `prevents`, `unblockable`, `buff`, `tapped`, `restriction`,
   `top`, `targets`, `doubles`, `energy`, `forces`, `controller`, `prevent`,
   `into`, `growth`, `tribal`, `effect`, `choose`, `enters`, `cards`,
   `threshold`, `recursion`, and similar (full 179-token frequency list in
   `experiments/out/foundry/validate_slug_report.json`). These are exactly
   the kind of "new vocabulary is a Captain ratification, not a typo"
   additions §10.3 anticipates — a one-time ratification, not per-slug.
2. **Log the remainder as the final-naming-audit backlog** (per the
   already-ratified rule) rather than renaming now.
3. A short list clearly reads as idiomatic job names in the same spirit as
   the 4 already-exempt leaves (`rhystic-tax`, `cheat-creature-into-play`,
   `compensates-controller-with-token`, `the-ring-tempts-you`) —
   **candidates for the §12 exemption list**: `burst-draw`, `cantrip`,
   `modal`, `drain-life`, `combat-trick-pump-own-creature`,
   `tribal-anthem-buff`, `alternate-win-condition`. Proposed, not applied.

### 2.3 Agent-legible definition rewrites

Every active axis got a DELIVERY/COST/EFFECT decomposition (full 306 rows
in `axis_walk_scaffold.json`, field `definition_rewrite`). Representative
sample:

| Slug | Rewrite |
|---|---|
| `rule:enters-tapped` | TRIGGER/DELIVERY: static (unmarked, default). COST: none. EFFECT: the permanent enters the battlefield tapped, delaying its immediate usability as a cost/drawback. |
| `rule:activated-tap-target-creature` | TRIGGER/DELIVERY: activated. COST: activation cost per printed ability (mana/tap/sacrifice as stated). EFFECT: taps a target creature, acting as pseudo-removal or combat disruption. |
| `rule:etb-with-counters` | TRIGGER/DELIVERY: etb. COST: none. EFFECT: the permanent enters already carrying a set number of +1/+1 counters, establishing an immediate stat baseline. |
| `rule:activation-restricted-to-sorcery-speed` | TRIGGER/DELIVERY: activated (restriction facet). COST: activation cost per printed ability. EFFECT: can only be activated at times the controller could cast a sorcery. |
| `rule:cast-trigger-card-draw` | TRIGGER/DELIVERY: cast-trigger. COST: none. EFFECT: triggers a card draw whenever the controller casts a spell matching a condition. |
| `rule:rhystic-tax` | TRIGGER/DELIVERY: static (unmarked). COST: none. EFFECT: pay-or-I-benefit / pay-or-you-can't tax: unless a player pays a cost, the controller gains a benefit. |

Two structural findings from this pass, both flagged rather than resolved:

- **173/306 active axes (57%) have no marked DELIVERY prefix** and default
  to "static/spell, unmarked." Grammar §1 says this default is correct for
  spell-resolution effects (CR 113.3a), but a chunk of these are actually
  **static abilities on permanents**, not spells — the grammar's "omitted
  for spell abilities" rule doesn't currently distinguish "omitted because
  it's a spell" from "omitted because DELIVERY wasn't marked for a
  permanent's static ability." Not resolved here; flagged for the naming
  audit.
- `combat-damage-triggers-*` (4 live axes: discard, loot, proliferate,
  treasure) remain un-normalized to `combat-damage-to-player-*` /
  `-to-creature-*` per the grammar's own §2 migration note. All 4 are
  `to-player` on inspection of their definitions (no `to-creature` variant
  exists yet) — **proposed renames**: `rule:combat-damage-to-player-discard`,
  `-loot`, `-proliferate`, `-treasure`.

### 2.4 DET-able vs. SYNTH-only classification

**265/306 (87%) are SYNTH-only** — they require reading a free-form filter,
condition, or job-pattern that no anchored regex can safely decide (matches
CORPUS-PASS-PLAN's own framing: DET is the minority lane). Breakdown by
delivery: 173 unmarked/static, 29 etb, 19 activated, 12 attack-trigger, the
rest split across the remaining trigger families. Full list in the scaffold
JSON; not reprinted here since "SYNTH-only, no anchored pattern" is a
uniform verdict without axis-specific content to add.

**41/306 (13%) are DET-able**, all with a proposed pattern and a measured
corpus hit-count against the Gate #0-filtered corpus (32,557 cards).
> **B2 annotation (2026-07-31):** this "41" is wrong — the table below it
> and the committed `foundry_det_patterns_probe.py` (verified against a
> pre-ratification backup) only ever had 39 rows. **39 is authoritative.**
> Not corrected in place (historical section, see this document's
> RESOLUTION header); `docs/det-patterns-v1.json`'s arithmetic is computed
> from the correct 39.
**These are proposals — "sampled and RATIFIED by Captain like a scoring
constant" per CORPUS-PASS-PLAN §1, not yet binding.**

| Slug | Proposed pattern (informal) | Corpus hits | Current n_members |
|---|---|---:|---:|
| `rule:activation-restricted-during-combat` | "Activate only during combat" | 7 | 1 |
| `rule:activation-restricted-only-during-your-turn` | "Activate only during your turn" | 77 | 7 |
| `rule:activation-restricted-to-own-upkeep` | "Activate only during your upkeep" | 51 | 4 |
| `rule:activation-restricted-to-sorcery-speed` | "Activate only as a sorcery" | 565 | 38 |
| `rule:created-token-enters-tapped` | "create a tapped ... token" (adjective form, verified against live members) | 195 | 11 |
| `rule:enters-tapped` (unconditional) | "enters tapped," NOT followed by unless/if | 709 | 171 |
| `rule:enters-tapped-conditional` | "enters tapped unless/if" + the reversed "unless X, ~ enters tapped" polarity (Lesson 1) | 168 | 13 |
| `rule:etb-tap-and-stun-target` | ETB clause with both "tap" and "stun counter" | 28 | 2 |
| `rule:forced-attack-each-combat` | "this creature attacks each combat if able" (CR 508.1a) | 59 | 9 |
| `rule:forces-all-creatures-attack` | "all/each creatures ... attack each combat if able" | 5 | 2 |
| `rule:grants-additional-combat-phase` | "an additional/extra/another combat phase" | 44 | 13 |
| `rule:grants-cascade-to-own-spells` | "spells you cast have cascade" | 2 | 2 |
| `rule:grants-controller-hexproof` | "you have/gain hexproof" | 13 | 3 |
| `rule:grants-creature-type` | "in addition to its/their other (creature) types" | 305 | 11 |
| `rule:grants-double-strike-target` | "target creature gains double strike" | 69 | 4 |
| `rule:grants-extra-land-drop` | "an additional land" / "play N lands" | 36 | 10 |
| `rule:grants-extra-turn` | "takes an extra/additional turn" | 55 | 8 |
| `rule:grants-flashback-to-graveyard-card` | "gains flashback" (granted, not printed) | 14 | 2 |
| `rule:grants-flying-and-pump-to-creature` | "+N/+N and gains flying" (either order) | 53 | 4 |
| `rule:grants-haste-to-created-tokens` | haste grant scoped to the just-created token(s) | 102 | 5 |
| `rule:grants-haste-to-your-creatures` | "creatures you control have haste" | 34 | 6 |
| `rule:grants-trample-to-creatures-with-counters` | trample conditioned on having a +1/+1 counter | 31 | 3 |
| `rule:grants-trample-to-other-creatures` | "other creatures you control have trample" | 9 | 7 |
| `rule:grants-unblockable` | "can't be blocked this turn / as long as" | 407 | 5 |
| `rule:grants-unblockable-target` | "target creature can't be blocked" | 38 | 11 |
| `rule:grants-ward-to-other-creatures` | "other creatures you control have ward" | 2 | 2 |
| `rule:innate-unblockable` | "this creature can't be blocked" (excl. "...except by") | 373 | 11 |
| `rule:activated-grants-self-unblockable` | activation cost followed by "this creature/permanent can't be blocked" | 25 | 2 |
| `rule:kicker-conditional-bonus-effect` | CR keyword "kicker"/"was kicked" | 260 | 24 |
| `rule:landfall-gain-life` | "landfall" + "gain ... life" co-occurring | 12 | 3 |
| `rule:landfall-produces-mana` | "landfall" + a mana symbol co-occurring | 0 | 1 |
| `rule:landfall-self-pump` | "landfall" + "+N/+N" co-occurring | 39 | 5 |
| `rule:no-maximum-hand-size` | "no maximum hand size" | 43 | 5 |
| `rule:prevents-regeneration` | "can't be regenerated" (CR 701.15) | 152 | 28 |
| `rule:restricted-purpose-mana` | "spend this mana only to" / "can be spent only to" | 217 | 24 |
| `rule:stun-counter` | "stun counter(s)" | 87 | 17 |
| `rule:the-ring-tempts-you` | "the Ring tempts you" | 54 | 19 |
| `rule:energy-<family> pre-filter` | activated cost spends `{E}` | 117 | n/a (pre-filter) |
| `rule:gives-energy-counters pre-filter` | grants `{E}` counters | 141 | n/a (pre-filter) |

Full pattern source strings, sample hit names, and methodology notes:
`experiments/out/foundry/det_patterns_probe.json`.

**Flags on this list requiring a Captain call before ratification (not
resolved here):**

- **Unblockable family overlap.** `grants-unblockable` (407 hits) and
  `innate-unblockable` (373 hits) overlap substantially on the shared
  "can't be blocked" phrase family; the 4 live unblockable axes are not yet
  disambiguated by delivery shape in a way the regex alone can guarantee.
  §2.5 proposes a `<delivery>-unblockable-<scope>` lattice grammar
  (`docs/grammars.json`, status `proposed`) as the fix — Captain must rule
  whether the 4 existing axes collapse 1:1 onto its 4 cells before this
  pattern set is usable as-is.
- **`rule:kicker-conditional-bonus-effect` may duplicate a killed keyword-
  ledger entry.** `docs/KEYWORD-LEDGER-CANDIDATES.md` batch 2 already killed
  "Kicker" as an engine-redundant keyword mechanic (same logic as b1-Q1).
  This axis (n=24, still active) describes what reads as the same
  underlying mechanism from a different angle ("optional additional cost →
  bonus effect"). **Flagging for Captain to confirm this is a distinct,
  legitimate job-axis (the *bonus effect being unlocked*, not the keyword
  itself) rather than a resurrection of the killed axis** before its DET
  pattern is ratified.
- **The 4 energy-family axes** (`energy-outlet-condition`,
  `energy-outlet-infinite`, `gives-energy-counters-condition`,
  `gives-energy-counters-immediately`) are proposed as a **two-stage**
  design: DET pre-filters "does this card spend/grant `{E}`" (Lane 1), and
  the condition/infinite/immediate 4-way split stays SYNTH judgment
  (Lane 2) — consistent with CORPUS-PASS-PLAN §1's Lane 1→2 handoff, not a
  full DET classification of these 4 axes individually.

### 2.5 Grammar family drafts

`docs/grammars.json` now holds all 8 already-ratified seeded families
(§11 of the naming grammar) populated with their real live members and
virtual-node examples, plus **one newly-drafted, `status: "proposed"`**
family surfaced by this walk:

- **`<delivery>-unblockable-<scope>`** — stem `unblockable`, facets
  `delivery` (static/activated/targeted) × `scope` (self/target). Not
  ratified; see the flag in §2.4. Full spec in `docs/grammars.json`.

Two more candidates were considered and **deliberately not drafted** (would
need Captain input on real semantic differences, not just naming):

- `activated-(un)tap-<scope>-<class>` consolidation — already flagged in
  CORPUS-PASS-PLAN §3 and the naming grammar §12 migration ledger; this
  walk confirms the 5 live members (`activated-tap-or-untap-any-creature`,
  `-any-permanent`, `activated-tap-target-creature`,
  `activated-untap-another-permanent`, `activated-untap-target-creature`)
  are not yet lattice-conformant but does not propose new names beyond what
  §12 already logged — no new information to add.
- `targeted-destruction-<class>` / `targeted-exile-<class>` /
  `targeted-discard-<class>` — the existing `targeted-<action>-<class>`
  grammar (already ratified) doesn't yet cover these 3 axes' class facet.
  Not drafted as a rename because their current membership (171, 72, 33
  cards respectively) likely spans multiple object classes and needs a
  membership check before any class-suffix split, not a blind rename — see
  `docs/grammars.json`'s notes field on that family.

---

## 3. Open questions for Captain (nothing below was resolved by this walk)

1. **Ratify the 9-bucket keyword-ability taxonomy** (§1.1/§1.3), superseding
   addendum-3 §4's original 5-bucket assumption; demote "casting-modifier"
   to a facet flag.
2. **Add `becomes-targeted-trigger` and `blocks-or-becomes-blocked-trigger`**
   to the closed DELIVERY vocabulary (§1.4).
3. **Fix the `dies`/`death-trigger` self-contradiction** in
   `CODEBOOK-NAMING-GRAMMAR.md` §2's table (§1.5) — editorial only, D-1
   already settled which name wins.
4. **Rule on `rule:cant-be-countered`'s replacement name** (§2.2.1) — no
   clean auto-fix exists.
5. **Ratify the vocabulary-extension list** (§2.2.2) so the 198-slug
   vocabulary-question backlog resolves to "extend + defer the rest to the
   final naming audit" rather than sitting open.
6. **Confirm or reject the 4 idiomatic-leaf exemption candidates**
   (§2.2.2.3): `burst-draw`, `cantrip`, `modal`,
   `combat-trick-pump-own-creature`, `tribal-anthem-buff`,
   `alternate-win-condition`, `drain-life`.
7. **Sample and ratify (or reject/adjust) the 41 DET patterns** in §2.4 —
   this is the actual Lane-1 gate before any full-corpus DET pass can run.
8. **Rule on the unblockable-family lattice** (§2.4/§2.5) before its DET
   patterns are usable.
9. **Confirm `rule:kicker-conditional-bonus-effect` is not a keyword-ledger
   duplicate** (§2.4) before ratifying its DET pattern.
10. **Decide the `combat-damage-triggers-*` → `combat-damage-to-player-*`
    renames** (§2.3, 4 slugs) — mechanical once confirmed, not yet applied.

---

## 4. Explicit non-actions

- `codebook.json` was not modified — no status changes, no member changes,
  no renames applied.
- No DET pattern was wired into `foundry_stage1b.py`'s SYNTH prompt or
  `foundry_consolidate.py`'s labeling logic. `validate_slug.py` is built
  and tested but **not yet wired into emit/SUP** — batch-7 §12 D7 flagged
  this wiring as landing "in the walk session," but the user's task scope
  for this session was building the artifacts, not modifying the live
  SUP-triage pipeline; wiring `lane=codebook-grammar` into
  `foundry_stage1b.py`/`foundry_consolidate.py` is flagged as the
  next actionable step, not done here.
- No full-corpus DET pass ran (CORPUS-PASS-PLAN step 4) — that requires the
  patterns in §2.4 to be ratified first.
- Keyword buckets were not integrated into the SYNTH prompt or the tag-tree
  parent scheme (CORPUS-PASS-PLAN §2 step 3, addendum-3 §4's "two
  integrations, both schema pass") — extraction only, per the ratified
  sequencing.

---

## 5. Artifacts produced (file manifest)

| File | Contents |
|---|---|
| `experiments/foundry_keyword_buckets.py` | Step-2 DET job (CR 702 → keyword-buckets.json) |
| `experiments/out/foundry/keyword-buckets.json` | 194 keyword classifications, CR-cited |
| `experiments/out/foundry/keyword-buckets_report.md` | Verify-or-drop residuals, trigger-family gaps, casting-modifier hits |
| `experiments/validate_slug.py` | Grammar §10 validator (charset/banned-tokens/closed-vocab/restriction-family/counter-law/cost-law/collision) |
| `experiments/out/foundry/validate_slug_report.json` | Per-slug validation result, all 306 active axes |
| `docs/grammars.json` | 8 ratified + 1 proposed grammar family, real member data |
| `experiments/foundry_axis_walk.py` | Step-3 scaffold generator (delivery/cost/effect + DET/SYNTH signal + grammar match) |
| `experiments/out/foundry/axis_walk_scaffold.json` | Full 306-row walk output |
| `experiments/foundry_det_patterns_probe.py` | Corpus hit-count measurement for the 41 DET-able proposals |
| `experiments/out/foundry/det_patterns_probe.json` | Measured hit counts, patterns, sample names |
| `docs/CORPUS-PASS-WALK-RATIFICATION.md` | This document |
