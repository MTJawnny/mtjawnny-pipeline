# §8 Validation Poke — Running Punch List

Running log of findings from the READY-TO-SHIP display-layer contract's
§8 gate (~30-card poke through the local viewer/server, before any batch
precompute work is authorized). Entries are investigation + documentation
only unless marked otherwise. Nothing in this file authorizes an engine
change by itself — see each entry's "Ruling" line.

**Standing practice (added 2026-07-10, applies to Entries #3 and #4 and
any future structural-fact work): check `data/raw/oracle-tags.jsonl.gz`
(Scryfall's human-curated Tagger dataset, 4,492 tags) for an existing tag
BEFORE deriving any new `rule:`-tag or regex parser.** It's already fully
loaded into the engine, unfiltered, via `invert_tags.py` ->
`experiments/out/card-tags.json.gz` -> `tier_engine.py` (35,550 tagged
cards) — a matching tag costs zero new engineering, no derivation ritual,
no eyeball sample, it's already live in Tier 3 scoring today. Checked
`data/raw/rulings.jsonl.gz` (WotC rulings, also sitting unwired in
`data/raw/`) as a possible shortcut first — it's a dead end for this
purpose: only 51% card coverage (19,623/38,233 oracle_ids), none of the
specific cards discussed this session have any rulings at all, and its
content is dominated by generic rules-education boilerplate (X-cost
templates, "triggered abilities use when/whenever/at" reminders) rather
than per-card distinguishing facts — rulings clarify edge-case
interactions assuming you already know the oracle text, they don't
restate it.

---

## Entry #1 — Kinship both-params display

**Ruling (Captain, 2026-07-07): HOLD** — superseded 2026-07-10:
**RESOLVED, no action needed.** Re-verified directly against current code
and live output while auditing Entries #4/#5 this session (asked to
implement this entry; found there was nothing left to build). The
`assign_tier()` code has a `Phase 2c (ratified): both sides' params, not
the anchor's alone` block — `fragment = f"{kw} {param_a} vs {kw}
{param_c}"` when they differ — that already ships exactly the fix this
entry's own DRAFT change-order proposed, independently of this entry ever
being authorized. Confirmed live: `experiments/out/reports/full/`
`zurgo-thunder-s-decree-tier2.md` shows `mobilize 2 vs mobilize x` for
Devoted Mardu/Avenger of the Fallen, `mobilize 2 vs mobilize 3` for
Dalkovan Packbeasts, `mobilize 2 vs mobilize 1` for the rest — every
candidate's own param, never a copy of the anchor's. The Tier 1 rows that
show only `mobilize 2 (DF=16)` (no "vs") are the genuinely SAME-param
case (Dalkovan Outrider, Voice of Victory, Bone-Cairn Butcher, all truly
"Mobilize 2") — collapsed by design ("X vs X" would be redundant), not a
recurrence of the bug. `emit_viewer.py` already exports both
`anchor_param`/`candidate_param` as separate JSON fields, and
`viewer.html` already renders `anchor param: X · candidate param: Y` in
the detail row. Same pattern as Entry #2: a real finding when written,
independently fixed by later ratified work before it was ever its own
authorized change order. Don't re-investigate.

### What's wrong

The v2.9 Mechanism 1 (keyword kinship) evidence shown to a human — in
report tables, the exported viewer JSON, and therefore `viewer.html` — only
ever displays the **anchor's** keyword param, never the candidate's. For a
different-param Tier 2 match (the whole point of Mechanism 1's Tier 2
path), this means every candidate row under one anchor prints an
*identical* evidence string regardless of what that candidate's card
actually says.

Confirmed directly in the shipped reports: every one of Zurgo, Thunder's
Decree's 15 keyword-kinship rows (3 Tier 1, 12 Tier 2) shows exactly
`keyword kinship: mobilize 2 (DF=16)` — including Devoted Mardu, whose
card literally says "Mobilize X", and Avenger of the Fallen, also
"Mobilize X" — never "mobilize X" or the candidate's real number.

### Where it's computed vs. where it's dropped

`keyword_kinship_match()` (`experiments/tier_engine.py:1296`, confirmed at
that line) computes, per qualifying keyword, a full structured dict:
`{"keyword", "tier", "anchor_param", "candidate_param", "df"}` — for
**every** keyword the anchor/candidate pair shares that clears the DF
floor, as a list.

`assign_tier()` (`experiments/tier_engine.py:1327`) then:
- picks exactly ONE match — `best_kinship = min(matches, key=(tier, df))`
  (line 1350) — discarding any other qualifying keyword shared by the
  same pair (theoretically possible per the code; not observed in the
  current 15-row sample, see below).
- composes `fragment` from `keyword` + `anchor_param` ONLY (line 1402:
  `fragment = f"{kw} {param_a}".strip()`), confirmed at that line.
- composes `evidence` as `f"keyword kinship: {fragment} (DF={df})"` (line
  1405, confirmed at that line) — same anchor-only string.
- returns a dict (line 1424) with only `tier, fragment, fragment_df,
  fragment_df_exact, evidence, mechanism` — `keyword`, `anchor_param`, and
  `candidate_param` do NOT survive as separate fields past this function;
  `candidate_param` does not survive AT ALL, in any form, past this point.

### Full drop scope (part 2 of the task)

Traced `keyword_kinship_match()`'s 5 computed fields through every
downstream consumer:

| Field | Report row (.md) | Viewer JSON (emit_viewer.py) | serve_viewer.py on-demand JSON |
|---|---|---|---|
| `keyword` (bare name) | **dropped** as a field (only embedded, unlabeled, inside `evidence`/`fragment` strings) | same — dropped | same — dropped |
| `tier` | kept (used as the row's tier bucket itself, i.e. which table it's in) | kept (implicit: which of `tiers["1"]`/`tiers["2"]`) | same |
| `anchor_param` | **dropped** as a field (only embedded inside `evidence`/`fragment`) | same — dropped | same — dropped |
| `candidate_param` | **fully dropped, in every form, at every layer** | same — fully dropped | same — fully dropped |
| `df` | kept, as `fragment_df` (generic field, not kinship-labeled) | kept, same field name | same |

`compute_candidate_rows()` (`experiments/tier_engine.py:3214`) builds the
report/export row straight from `assign_tier()`'s already-reduced return
dict (line 3247: `row = {"name":..., "evidence": result["evidence"],
"fragment": result["fragment"], ...}`) — it never had `keyword`/
`anchor_param`/`candidate_param` available to keep, because `assign_tier()`
already discarded them one layer up.

`emit_viewer.py`'s `build_row_export()` (`experiments/emit_viewer.py:160`)
carries the row through as-is and additionally computes its OWN
`keyword_overlap` field — but that calls the separate, pre-existing
`te.keyword_overlap()` (`tier_engine.py:1855`), which returns the sorted
list of ALL keyword NAMES both cards share (no params, no DF-floor
filtering, no kinship qualification logic at all — it's the generic
"Keywords shared" report column, unrelated to Mechanism 1's qualification
path). It is not a source of the missing params either.

`serve_viewer.py` has no row-building logic of its own — it calls
`ev.export_anchor()` directly, so its on-demand JSON is byte-identical in
shape to the batch export. **No difference between (b) and (c).** The
report `.md` tables (a) show strictly less than the JSON (no
`fragment_df`/`mechanism`/etc. as separate columns, just the composed
`evidence` string and the generic `keyword_overlap` column) but suffer the
identical drop for the same reason: both are downstream of the same
`assign_tier()` reduction.

**Multiple qualifying keywords per pair:** the code path exists
(`matches` is a list; only the best is kept), but a live re-scan of all 15
current kinship rows found zero pairs where `keyword_kinship_match()`
returns more than one match — so this part of the drop is a latent
possibility in the current 7+2 anchor set, not yet an observed case.

### Report history confirmation (part 3 of the task)

**Yes — confirmed directly.** Every existing kinship row in every current
report and export shows only the anchor's param. Grep of
`experiments/out/reports/full/zurgo-thunder-s-decree-tier2.md` and the
summary report: all 15 rows read `keyword kinship: mobilize 2 (DF=16)`,
verbatim identical, regardless of whether the candidate's own card says
"Mobilize 1", "Mobilize 2", "Mobilize 3", or "Mobilize X".

**Implication, stated plainly:** standing gate 6 ("Zurgo: T1 = Mobilize-2
kinship trio... Hero of Bladehold in T2 via the 6-token trigger run") was
verified by CARD IDENTITY (checking which named cards appear in which
tier) and by re-deriving params from raw oracle text out-of-band (this
entry's own hand-verification table, below) — **not** by reading
candidate-param evidence off the shipped report, because the shipped
report never displays it. A human reading only the report/viewer, with no
independent check, cannot currently distinguish Zurgo's Tier 1 trio
(genuinely "Mobilize 2", same as Zurgo) from a hypothetical wrongly-tiered
Tier 1 row, by eye — they'd have to trust the tier bucket placement alone.

### Hand-verification table (part 4 of the task)

Read-only recomputation via `keyword_kinship_match()` (called directly,
unmodified — no engine files edited) for all 15 kinship-qualified rows
across all 9 exported viewer anchors. **All 15 belong to Zurgo, Thunder's
Decree** — the other 8 anchors (Grand Abolisher, Myrel, Marisi, Preordain,
Sol Ring, Sakura-Tribe Elder, Delney, Goldnight Commander) have zero
keyword-kinship rows (confirmed by scanning every row's `mechanism` field
in their exported JSON).

`candidate_actual_line` is the verbatim oracle-text line pulled directly
from the candidate's raw card data (searched across all faces, DFC-safe) —
independent of the engine's parser, for eyeball cross-check.

| Anchor | Candidate | Tier | Keyword | Anchor param | Candidate param (recomputed) | Candidate's actual card line |
|---|---|---|---|---|---|---|
| Zurgo, Thunder's Decree | Dalkovan Outrider | 1 | mobilize | 2 | 2 | Mobilize 2 |
| Zurgo, Thunder's Decree | Bone-Cairn Butcher | 1 | mobilize | 2 | 2 | Mobilize 2 (Whenever this creature attacks, create two tapped and attacking 1/1 red Warrior creature tokens. Sacrifice them at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Voice of Victory | 1 | mobilize | 2 | 2 | Mobilize 2 (Whenever this creature attacks, create two tapped and attacking 1/1 red Warrior creature tokens. Sacrifice them at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Zurgo Stormrender | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Mardu Thunderkite | 2 | mobilize | 2 | 1 | Mobilize 1 |
| Zurgo, Thunder's Decree | Avenger of the Fallen | 2 | mobilize | 2 | x | Mobilize X, where X is the number of creature cards in your graveyard. (Whenever this creature attacks, create X tapped and attacking 1/1 red Warrior creature tokens...) |
| Zurgo, Thunder's Decree | Dalkovan Packbeasts | 2 | mobilize | 2 | 3 | Mobilize 3 (Whenever this creature attacks, create three tapped and attacking 1/1 red Warrior creature tokens. Sacrifice them at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Nightblade Brigade | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Zurgo's Vanguard | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Venerated Stormsinger | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Dragonback Lancer | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Shock Brigade | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Reigning Victor | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Stadium Headliner | 2 | mobilize | 2 | 1 | Mobilize 1 (Whenever this creature attacks, create a tapped and attacking 1/1 red Warrior creature token. Sacrifice it at the beginning of the next end step.) |
| Zurgo, Thunder's Decree | Devoted Mardu | 2 | mobilize | 2 | x | Mobilize X, where X is your devotion to Mardu. (Whenever you attack, create X tapped and attacking Mardudes (tapped and attacking 1/1 red Warrior creature tokens)...) |

**Disagreement check: zero.** Every recomputed `candidate_param` is
verbatim present, in the right position, in that candidate's own raw
oracle-text keyword line — including both "X"-param cards (Avenger of the
Fallen, Devoted Mardu), which is exactly the erratum-2 case. This stays a
**display nit**, not a correctness question: the parser is computing the
right values; the display layer just never receives them.

### DRAFT change-order text — NOT AUTHORIZED

*(Drafted per Captain's ruling shape. Not implemented. Requires explicit
authorization as its own change order before any code is touched.)*

**Proposed fix shape:** the engine should stop composing an English
sentence and start exporting facts. Concretely:

- `keyword_kinship_match()`'s already-computed `keyword`, `anchor_param`,
  `candidate_param`, `df` (and `tier`, already used) should survive as
  their OWN structured fields on the row — e.g. a `kinship` sub-object
  (`{"keyword", "anchor_param", "candidate_param", "df"}`) alongside the
  existing `fragment`/`evidence`/`mechanism` fields, for `mechanism ==
  "keyword"` rows only (text/reminder-mechanism rows are unaffected).
- The engine's own `evidence` string MAY continue to exist for the
  report's human-readable line (and MAY be upgraded to show both params,
  e.g. `"keyword kinship: mobilize 2 (anchor) vs mobilize X (candidate),
  DF=16"`, for reading convenience directly in the .md report) — but it
  must never be the ONLY place the params live. The site's display layer
  (per the READY-TO-SHIP contract, §3: "BOTH params, always") must compose
  its own presentation string from the structured fields, not parse or
  reuse the engine's English sentence. Engine states facts; display
  arranges them.
- If a pair shares multiple qualifying keywords (the latent,
  currently-unobserved case above), decide whether to keep exporting only
  the single best match or to export the full `matches` list — a real
  design question for the change order, not decided here.

**Gates this would obligate**, per standing protocol:
- Full v2.5–v2.9 gate suite green (all 7 calibration anchors).
- Determinism confirmed twice.
- Regeneration of all deliverables: reports (7 anchors, full lists,
  Tagger crosscheck), viewer cache re-export (all 9 viewer anchors,
  `experiments/out/viewer/data/` wiped and rebuilt).
- Report header note flagging the change (per house style: never silent).
- Since this only ADDS fields and does not change any tier assignment,
  score, or ranking, DF-drift / explained-drift gates should show zero
  movement — any row reordering would be an unrelated regression, not an
  expected consequence of this fix, and should halt loudly if seen.

---

## Entry #2 — Sentence-final punctuation breaks fragment matching (Arcane Signet audit)

**RESOLVED (confirmed 2026-07-10, discovered incidentally while
investigating an unrelated Delney/Roaming Throne question) — but not the
way this entry's own draft proposed, and not the whole story.** Two
separate things happened, worth untangling for anyone reading this cold:

1. **The tokenizer bug itself IS fixed.** `strip_sentence_final_token_period()`
   (`tier_engine.py:529`, doc comment: "CO-C (Phase 2a, ratified)... Fixes
   the Arcane Signet/Manalith clause-truncation bug (Batch-1 Lane 1a)")
   already does exactly what this entry's draft proposed — strips a bare
   trailing period per-token, everywhere a sentence ends. Verified directly:
   `longest_common_run()` between Arcane Signet and Manalith now finds the
   full 7-token fragment `{t}: add one mana of any color` (previously
   truncated to 6 tokens, losing "color", per this entry's original
   finding). This landed as part of the same Phase 0-5 work already baked
   into commit `190e8fa` — predates both this session and the prior one;
   this entry was simply never closed out to reflect it.
2. **But the tokenizer fix alone would NOT have solved this entry's actual
   complaint** (that the 9 named candidates should reach Tier 2). The
   CORRECTLY-measured corpus DF of that full 7-token fragment is 308 (not
   the ~26 an earlier triage pass recorded off the buggy truncated
   version) — deep "DEAD" band under Phase 3's rescue ceiling (172), so it
   never qualifies via text matching regardless of tokenization. This is
   already documented in Arcane Signet's own report header (Phase 4
   change-order commentary, "FINDING (not engineered around)").
   **All 9 candidates now correctly reach Tier 2 anyway** (confirmed
   directly, all 9 checked) — but via `mechanism=mana` (Phase 4's mana-pip
   kinship, a later, unrelated addition), never via `mechanism=text`. The
   outcome this entry wanted is achieved; the mechanism that achieves it is
   not the one this entry's own draft proposed.

No further action needed on this entry — recorded for the historical
record and so a future session doesn't reopen a case that already has a
real, verified answer. Original write-up preserved below unedited.

### What's wrong

Auditing Arcane Signet (`{t}: add one mana of any color in your
commander's color identity.`), 9 named candidates were expected in Tier 2
(same "add one mana of any color" ability) but don't land there:

| Candidate | Expected | Actual |
|---|---|---|
| Manalith | T2 | T3 |
| Opaline Unicorn | T2 | absent (no tier) |
| Utopia Tree | T2 | absent |
| Alloy Myr | T2 | absent |
| Lifespring Druid | T2 | absent |
| Great Forest Druid | T2 | absent |
| Three Tree Rootweaver | T2 | absent |
| Ornithopter of Paradise | T2 | absent |
| Birds of Paradise | T2 | absent |

All 9 have the identical matchable paragraph `"{t}: add one mana of any
color."` — a plain, unqualified version of Signet's ability. All 9 fail
for the exact same reason.

### Root cause (confirmed by direct call, not inferred)

Paragraph tokenization (`tier_engine.py:915`,
`"paragraph_tokens": [p.split() for p in matchable_paragraphs]`) is a bare
whitespace `.split()` — no punctuation stripping, ever, on any token.
Sentence-final punctuation stays glued to the last word of whichever
sentence it ends.

- Arcane Signet's tokens: `..., "any", "color", "in", "your", ...` —
  `"color"` is bare, because its sentence keeps going.
- Manalith's tokens: `..., "any", "color."` — its sentence ENDS there, so
  the period is glued on: the actual token is `"color."`, a different
  string from `"color"`.

`longest_common_run()` (`tier_engine.py:1097`) does exact token-string
comparison, so `"color" != "color."` stops the match one token early.
Confirmed by calling it directly:

```
Manalith vs Arcane Signet:
  longest_common_run length=6, frag=['{t}:','add','one','mana','of','any']
  ngram_df_estimate = 308  (floor=50)  -> REJECTED, too generic

Fellwar Stone vs Arcane Signet (control -- text continues past "color"):
  longest_common_run length=7, frag=[...,'any','color']
  ngram_df_estimate = 26  (floor=50)   -> qualifies, correctly lands T2
```

Fellwar Stone's own ability text also continues past "color" (`"...color
that a land..."`), so its `"color"` token is bare too — it string-matches
Signet's, the run extends one token further, and lands on a far rarer
7-token fragment (DF=26). Manalith's sentence-final period costs it
exactly that one token, and the resulting shorter 6-token fragment
(`"...of any"`, no "color") is a near-universal prefix shared by every
"add one mana of any TYPE/COLOR" card in the corpus (DF=308) — correctly
rejected as too generic, but only because the genuinely rare, matching
fragment was never even attempted.

With no qualifying fragment on either side, `assign_tier()` returns `None`
for the pair — not a demotion, not a corroboration-gate exclusion, just
never found.

**This is a general tokenizer property, not an Arcane-Signet-specific
one**: any anchor/candidate pair where the shared wording ends the
candidate's sentence exactly at the point where the anchor's sentence
keeps going will lose exactly one token off the match, every time, by
construction of `.split()` + exact-string comparison. This follows
directly from the code (no corpus-wide re-scan needed to establish the
mechanism is general) — but **how many corpus-wide pairs it actually
affects has NOT been measured** (no loose-substring-scan-then-recount
mistake repeated here, per the erratum-2 lesson: don't guess a count,
measure it, if this proceeds to a change order).

### Independent, second finding: Tier 3 tag-taxonomy split

Separately explains why Manalith (T3) and the other 8 (absent even from
T3) diverge from each other, unrelated to the tokenization bug:

| Card | Relevant Tagger tags | tier3_score | Threshold |
|---|---|---|---|
| Arcane Signet (anchor) | `mana-rock`, `mana-producer`, `ramp`, `commander-identity-matters`, ... | — | — |
| Manalith | `mana-rock`, `mana-producer`, `ramp`, `mini-refund`, `refund` | **0.288** | 0.15 |
| other 8 (all creatures) | `mana-dork` (not `mana-rock`), `mana-producer`, `ramp` | **0.076** | 0.15 |

The Tagger layer tags artifact mana rocks `mana-rock` and creature mana
dorks `mana-dork` as two distinct tags. Manalith (an artifact) shares
`mana-rock` directly with Signet and clears the 0.15 Tier 3 coverage
threshold comfortably; the 8 creatures only share the generic
`activated-ability`/`mana-producer`/`ramp` tags, landing at 0.076 — below
threshold, so they don't surface even as a Tier 3 proposal. This is a
Tagger-taxonomy question (should `mana-dork` inherit toward `mana-rock`,
or should the two be tag-siblings for overlap purposes?), not an engine
logic bug — recorded here because it's the reason the 8 land differently
from Manalith even before the tokenization bug is considered.

### DRAFT change-order text — NOT AUTHORIZED

*(Sketched for the record. Not implemented. Requires its own explicit
authorization — and, given this is a FROZEN-core scoring change, almost
certainly its own dedicated gate/regression pass, not a bundle-in with
display-only fixes like Entry #1.)*

**Proposed fix shape:** strip a trailing sentence-ending `.` from the LAST
token of each paragraph (or more precisely: normalize a token's trailing
period away wherever it is purely sentence-final punctuation, not an
abbreviation or part of the text like `{t}:`) before building
`paragraph_tokens`/n-grams — so `"color."` and `"color"` become the same
token regardless of sentence position. Needs explicit care: must NOT
strip apostrophes or other in-word punctuation (`"commander's"` must stay
one token), and must NOT touch mana/tap symbols (`"{t}:"`) or other
intentional non-word tokens.

**Why this is bigger than Entry #1:** this touches token identity used by
`longest_common_run`/`ngram_df_estimate`/the corpus-wide `ngram_df` index
itself — i.e., it changes the DF of every n-gram window whose boundary
touches a sentence-final word, corpus-wide, for every anchor, not just
Arcane Signet. That is a real re-tokenization of the corpus index, not an
additive field.

**Gates this would obligate**, per standing protocol:
- Full v2.5–v2.9 gate suite green, all 7 calibration anchors.
- Determinism confirmed twice.
- Explicit corpus-wide count of how many (anchor, candidate) pairs change
  tier as a result (measured, not estimated) — expect this to be
  materially larger than Entry #1's zero-score-impact change, since
  `ngram_df` values themselves shift.
- DF-drift review under the tightened explained-drift definition (every
  moved row must trace to a named fragment DF delta); this fix is
  explicitly expected to cause real, non-trivial movement — that is the
  point of the fix, not a regression, but every movement still must be
  individually traced, not hand-waved as "expected."
- Regeneration of all deliverables: reports, full lists, Tagger
  crosscheck, viewer cache re-export.
- Report header note (never silent).

---

## Entry #3 — Structural `rule:`-tag injection backlog (missing template-block tags)

**Ruling (Captain, 2026-07-09): PARKED.** No code changes this session. Not
an isolated one-off — Captain wants this treated as a standing backlog
practice: whenever a future session touches `tier_engine.py` for any other
reason, check this entry and bundle in a `rule:`-tag addition if one's
ready, rather than waiting for a dedicated session.

### The idea

`rule:turn-scoped` (v2.6 amendment 2) is a proven, one-instance pattern:
an engine-derived structural fact (not sourced from the human Tagger
index) — regex over composed full text, corpus-wide DF/idf computed,
printed with a fixed-seed eyeball sample, then injected into the extended
tag pool that feeds `tier3_score()`. Known Limitations already flags it as
"the pilot for this pattern... no second instance has been built yet."

`tier3_score()` is a coverage FRACTION (matched idf-weighted tag mass ÷
anchor's total idf-weighted tag mass, qualifies at >=0.15) — additive
across however many tags match, no per-tag special-casing. So every new
`rule:`-tag added to the pool automatically strengthens Tier 3 corroboration
for any pair that shares it, with zero new qualification mechanism or
threshold constant needed. The backlog item is purely "which structural
facts are missing from both the Tagger vocabulary and the `rule:` pool,"
not new engine architecture.

### Motivating case (parked, not itself authorizing anything)

Craterhoof Behemoth vs. End-Raze Forerunners: both are "ETB, pump
creatures you control by an amount, grant a keyword set including
trample, until end of turn." Confirmed a reorder-tolerant text matcher
would NOT bridge this pair — every literal token-window overlap between
the two is deep boilerplate (`trample until end of turn` DF=268, `+2/+2
until end of turn` DF=308, `until end of turn, where` DF=292, all "dead"
band) — so this is a `rule:`-tag question, not a `find_shared_fragment()`
question. Checked which of the 5 informal "blocks" (ETB trigger /
creatures-you-control scope / +N/+N pump / gain KEYWORD / until-end-of-turn
duration) are already covered:

- Pump-magnitude and keyword-grant: **already covered** by existing
  Tagger tags (`overrun`, `toughness-boost-to-all`, `gives-trample`,
  `virtual-french-vanilla` — this pair already shares 7 tags, 0.55
  coverage, already Tier 3's #4 row for this anchor out of 1710).
- ETB trigger, EOT duration, and controlled-creatures scope: **not
  currently a tag anywhere** — syntactic template markers, not "what this
  card does" semantics, so the human Tagger never encoded them. Candidates
  so far, unvalidated:
  - `rule:etb-trigger` — broadly reusable, worth deriving.
  - `rule:eot-duration` — broadly reusable, worth deriving.
  - `rule:controlled-creatures-scope` ("creatures you control" / "other
    creatures you control") — likely too boilerplate-everywhere to carry
    useful idf; probably not worth its own tag, needs DF check before
    deciding.
- Also flagged in this conversation as a second candidate independent of
  the Craterhoof case: **upkeep-trigger** presence ("at the beginning of
  your upkeep" family) — no existing tag found for it; worth checking
  when this entry is picked up.

**Checked against the existing Tagger vocabulary (2026-07-10, see standing
practice note at top of file) before any of the above get derived:**
`upkeep-cost` exists (230 taggings) but is a DIFFERENT concept — "cards
that ask you to pay some kind of cost on your upkeep step," not "has an
upkeep trigger" — no direct hit for `rule:upkeep-trigger`'s concept, it's
still a real gap. No existing tag found for ETB-trigger or EOT-duration
either. All three candidates above stand as genuinely missing — this audit
didn't eliminate this entry, just confirms it's not duplicating existing
Tagger work.

### DRAFT next actions — NOT AUTHORIZED

*(Sketched for the record. Requires explicit authorization before any
code is touched, same as Entries #1/#2.)*

1. Audit: which structural template facts are both (a) NOT in the
   current Tagger vocabulary and (b) NOT already an existing `rule:`-tag
   — build the "most impactful missing tags" list before writing any
   regex, don't guess which ones matter.
2. For each candidate tag: derive with the exact `rule:turn-scoped`
   ritual — regex, corpus-wide DF/idf, fixed-seed eyeball sample, printed
   BEFORE it touches scoring. Never silently pick a pattern or skip the
   eyeball step, per house rule.
3. Inject into the same extended Tier-3 tag pool `rule:turn-scoped`
   already uses — no new mechanism, no new threshold constant.
4. Since this changes Tier 3 coverage scores (unlike Entry #1's pure
   display addition), it needs the same weight as a scoring change: full
   gate suite green, determinism confirmed twice, corpus-wide count of
   which pairs newly qualify or reorder (measured, not estimated), viewer
   cache regen, report header note.

---

## Entry #4 — Granted-keyword-SET kinship (Equipment/Aura/anthem "confers
keywords to something else" idiom)

**Ruling (Captain, 2026-07-10): PARKED, then IMPLEMENTED later the same
session** ("implement code for entry 4") — see the IMPLEMENTED section
below for what shipped, the real bug it surfaced, and full verification.

### What's wrong

Swiftfoot Boots (`Equipped creature has hexproof and haste.`) vs. Lightning
Greaves (`Equipped creature has haste and shroud.`) — same sentence shape,
share the keyword "haste" — sits at Tier 3 (score 0.72, 2nd-highest of
Boots' 1456 Tier 3 candidates), never Tier 2. Confirmed by direct call:
`longest_common_run()` finds only `equipped creature has` (3 tokens,
below the 5-token floor) because the keyword order flips between the two
cards (hexproof-then-haste vs. haste-then-shroud), so the contiguous run
breaks immediately after `has`. It also never reaches the existing
keyword-kinship mechanism (Mechanism 1): `is_keyword_only_paragraph()`
requires every comma-separated fragment to start with a keyword name, and
`hexproof and haste` has no comma — Mechanism 1's parser never sees this
clause at all, "and"-joined keyword-grant idioms are outside its scope by
construction.

**Checked whether Scryfall's own `keywords` field could shortcut this
(skip building our own parser): it can't.** Confirmed directly —
`Swiftfoot Boots -> ['Equip']`, `Lightning Greaves -> ['Equip']` — Scryfall
only lists a card's OWN keyword abilities, never keywords it grants to
something else. Own extraction is required.

### Measured corpus shape (not guessed)

Equipment: 658 cards. Aura: 1295 cards. Grant-idiom regex
(`^(equipped|enchanted) creature (?:gets? [^.]*? and )?has (.+)`) matches
252 Equipment / 79 Aura sentences. After extracting the actual keyword
list from the matched clause (against the standard keyword-ability
vocabulary, filtering non-keyword quoted text):

| keywords granted | count | example |
|---|---|---|
| 0 (false-positive idiom match, e.g. quoted non-keyword ability text) | 84 | Compulsory Rest |
| 1 | 203 | Mask of Avacyn |
| 2 | 33 | Behemoth Sledge (`trample and lifelink`) |
| 3 | 5 | Helm of Kaldra |
| 4 (often *conditional* — Multiclass Baldric grants a different keyword per creature type controlled, not an unconditional set) | 2 | Multiclass Baldric |

### Design (improved during discussion — record the reasoning, not just the shape)

Original framing was two separate mechanisms: a type-gated (`Equipment`/
`Aura`) keyword-set kinship mechanism, plus a separate corpus-wide
"keyword soup" tag. Sharper on inspection:

- **Type-gating is redundant, not wrong.** The subject phrases themselves
  (`Equipped creature`, `Enchanted creature`, `creatures you control`) are
  already exclusive to Equipment/Aura/anthem-granting cards by Magic's own
  rules — only an Equipment card can ever say "Equipped creature." A
  phrase-anchored regex gets the type restriction for free; a separate
  `type_bucket()` check buys nothing extra and doesn't generalize to
  anthem-style grants the way a subject-phrase parser does.
- **One extraction, two consumers, not two mechanisms.** A single parser
  produces one fact per card — `granted_keyword_set: frozenset[str]` —
  regardless of subject phrase or type. What happens with that fact
  branches on its SIZE, matching the measured distribution above:
  - size 1-2 (203 + 33 = 236 cards, the overwhelming majority and the
    range where exact-set overlap is actually meaningful): new Tier 2
    kinship mechanism, same "shared-slot precedent" shape as mana kinship
    (R6) — qualifies on ANY shared keyword, cascade-ranked by overlap
    fraction/count. This is what fixes Boots<->Greaves.
  - size >=3: too rare and too combinatorially loose for precise Tier 2
    set-matching to mean anything at this count, which was Captain's own
    read ("it starts finding other cards that have keywords"). **No new
    tag needed here — `keyword-soup` already exists in the Tagger
    vocabulary** (`data/raw/oracle-tags.jsonl.gz`, description "cards that
    list out all or almost all the keyword abilities found in their set,"
    27 cards including Eater of Virtue), already loaded and already live
    in Tier 3 scoring today (confirmed directly: Eater of Virtue's entry
    in `experiments/out/card-tags.json.gz` already carries
    `keyword-soup`). Corpus-wide already, not gear-only, matching this
    entry's own instinct that the term applies more naturally to stacked
    creatures than equipment. Nothing to derive — verify it's surfacing
    correctly for the relevant pairs when this entry is picked up, don't
    rebuild it.
  - Also checked `keyword-anthem` (473 cards, "give your entire team a
    keyword") for size 1-2 — it's a coarser, complementary signal (marks
    "this is a team-wide keyword granter" but not which keyword or how
    many), doesn't replace the precise set-kinship mechanism above, but
    worth having both live at once — no conflict.
  - conditional grants (Champion's Helm's "as long as legendary,"
    Multiclass Baldric's per-creature-type set) — still undecided: exclude
    from the fact entirely, or extract but let the existing `condition
    penalty` (already in the rank formula) discount them. Not resolved in
    this discussion, flag explicitly when picked up.

### DRAFT next actions — NOT AUTHORIZED

*(Sketched for the record. Requires explicit authorization before any
code is touched, same as Entries #1-#3.)*

1. Finalize the grant-clause regex (subject phrase + verb variants
   `has`/`have`/`gets...and has`/`gains`) against the standard keyword
   vocabulary, print the corpus-wide match sample for eyeball review
   before it touches scoring — same ritual as every prior mechanism.
2. Resolve the conditional-grant question above before implementing, not
   during.
3. Implement `granted_keyword_set` extraction; wire size 1-2 into the new
   Tier 2 kinship mechanism (mana-kinship shape: qualify on any shared
   keyword, cascade-rank by overlap). Size >=3 needs NO new tag — the
   existing `keyword-soup` Tagger tag already covers it and is already
   live; this step is just confirming it surfaces where expected, not
   building anything.
4. This touches the FROZEN tier-assignment core (new Tier 2 path) — full
   v2.5-v2.9 gate suite green, determinism confirmed twice, corpus-wide
   count of newly-qualifying/reordering pairs (measured, not estimated),
   viewer cache regen, report header note.

### IMPLEMENTED, 2026-07-10 (same session as Entry #5, Captain's ruling: "implement Entry #4")

Built per the design above, unchanged from the parked scope: `granted_keyword_set`
extraction (`extract_granted_keyword_clause()`), a new `keyword_grant`
Tier 2 mechanism (`granted_keyword_kinship_match()`, mana-kinship shape —
any shared keyword qualifies, ranked by stray-keyword count via
`GRANT_KEYWORD_MISMATCH_PENALTY`), scoped to size 1-2 grants
(`GRANT_SIZE_CEILING=2`). Verb variants `has`/`have`/`gains` per step 1.
Conditional grants excluded entirely (the open question, resolved):
confirmed directly against Champion's Helm and Multiclass Baldric's real
oracle text that both are correctly excluded by construction (regex
anchor / keyword-exact-match respectively), not by the
`CONDITIONAL_GRANT_MARKERS` backstop, which exists as defense-in-depth
only. Anthem phrasing ("creatures you control have...") deliberately left
out — never corpus-measured this session, not guessed at.

**Real bug found and fixed auditing this entry, required for its own
motivating case to work at all:** `is_keyword_only_paragraph()`'s keyword
prefix check was a raw substring match, not word-boundary safe —
"equipped"/"enchanted" silently prefix-matched an Equipment/Aura card's
OWN `Equip`/`Enchant` keyword, wrongly excluding the entire grant-clause
paragraph from `matchable_paragraphs` before ANY mechanism could see it.
Confirmed directly: Swiftfoot Boots and Lightning Greaves both returned
**zero** `matchable_paragraphs` containing their grant clause before the
fix — this entry's own headline example was completely invisible, not
just under-ranked. Fixed to match the sibling function
`parse_keyword_instances()`'s already-correct convention
(`frag == kw or frag.startswith(kw + " ")`). One gate collision found and
resolved: Discreet Retreat (own keyword `Enchant`, same bug) was
previously invisible to Grand Abolisher's Tier 2 corroboration gate; now
correctly surfaces (shares Abolisher's own defining fragment) and
correctly self-disqualifies via the existing v2.6 amendment 1 mechanism —
added to `MANA_ONLY_FAMILY`, same precedent as the Angel of
Jubilation/Yasharn entries already documented at that gate. Confirmed
purely additive elsewhere (Tier 2 counts: Myrel +1, Sol Ring +2,
Delney +6, Grand Abolisher unchanged at 54) — no other regressions.

**Verification, all confirmed green:**
- Full gate suite: 73/73 PASS, 0 STOP/FAIL (after the `MANA_ONLY_FAMILY`
  fix — first run surfaced exactly the one Discreet Retreat collision,
  nothing else).
- Determinism: byte-identical across 2 runs.
- Corpus-wide: 372 cards carry a qualifying size-1/2 granted-keyword fact,
  producing 9,059 pairwise Tier 2 kinship links — real, shared-slot-scale
  impact (same category as mana kinship's own reach). Invisible in the
  9-card calibration panel (none are Equipment/Aura anchors) — verified
  live instead via Swiftfoot Boots: 34 new `keyword_grant` Tier 2 rows,
  Lightning Greaves confirmed among them (was Tier 3, score 0.72; now
  Tier 2, `granted-keyword kinship: haste (mismatch penalty=0.60)`),
  fetched through the actual running `/api/anchor` endpoint, not just the
  pre-exported 9-anchor batch.
- Viewer cache regenerated (9 anchors), `serve_viewer.py` restarted and
  reconfirmed live after every subsequent change this session.

**Files touched**: `experiments/tier_engine.py` (new constants block,
`build_keyword_vocabulary()`, `extract_granted_keyword_clause()`,
`build_granted_keyword_facts()`, `granted_keyword_kinship_match()`,
`assign_tier()`'s new mechanism branch, main loop's `keyword_grant` rank
branch, `check_stability_gate`'s mechanism carve-out, the
`is_keyword_only_paragraph()` bug fix, `MANA_ONLY_FAMILY` addition, report
header notes), `experiments/emit_viewer.py` (mirrors `tier_engine.py`'s
`card_docs` setup for the granted-keyword facts).

---

## Entry #5 — `find_shared_fragment()` credits only one run per pair, drops a second genuine one

**Ruling: RULED and IMPLEMENTED, 2026-07-10** (diminishing returns, floor at
0.25, unbounded run count) — see the IMPLEMENTED section below for what
shipped and full verification. Originally flagged live from a direct
Captain question about Delney/Roaming Throne's Tier 2 evidence.

### What's wrong

Delney, Streetwise Lookout: `If a triggered ability of a creature you
control with power 2 or less triggers, that ability triggers an
additional time.` vs. Roaming Throne: `If a triggered ability of another
creature you control of the chosen type triggers, it triggers an
additional time.` — Roaming Throne currently qualifies Tier 2 on the
fragment `if a triggered ability of` (DF=12) alone. Captain's question:
is the engine only counting that shown fragment, or the whole string —
and shouldn't the later shared words ("triggers... an additional time")
count too?

### Traced directly (not inferred from the report)

Exact tokens, per the engine's own `paragraph_tokens`:

```
Delney:  if a triggered ability of a creature you control with power 2
         or less triggers, that ability triggers an additional time
Throne:  if a triggered ability of another creature you control of the
         chosen type triggers, it triggers an additional time
```

`longest_common_run()` correctly finds the single GLOBAL longest run —
`if a triggered ability of` (5 tokens) — then diverges (`a` vs `another`).
But there is a SECOND, separate, genuinely shared run later in the same
pair: `triggers an additional time` (4 tokens, confirmed by direct
substring comparison — both sides have this run verbatim, just at
different token positions since `that ability` (2 tokens) vs `it`
(1 token) shifts the alignment). `find_shared_fragment()` never surfaces
this second run: `longest_common_run()` returns only ONE run per
paragraph pair (the longest), by construction — the 4-token suffix run
is simply outcompeted by the 5-token prefix run and silently discarded.

**Would it have qualified even if found separately? No** — 4 tokens is
below `NGRAM_MIN_LEN=5`, so this specific suffix run would never
independently qualify regardless of this limitation. The concrete case
in front of Captain doesn't change tier as a result of this gap. The
finding is about the GENERAL pattern: whenever two paragraphs share a
prefix run AND a suffix run around a differing middle clause, only the
longer of the two is ever counted, and the discarded one could
legitimately be >=5 tokens on a different pair — this hasn't been
measured corpus-wide.

**Different in kind from the Craterhoof/End-Raze case (same session,
earlier)**: that one was genuinely reordered/interleaved text where even
an order-invariant window search would fail (confirmed: every literal
overlap there was deep-boilerplate DF). This one is the SAME linear
order, same word sequence on both sides, just with a differing middle
clause sandwiched between two real, position-consistent shared runs — a
more tractable, narrower problem than scrambled-text matching.

### Cumulative scoring (Captain's follow-up question, 2026-07-10): is it philosophically sound?

**Yes, no principled objection** — checked against the codebase's own
standing philosophy, not just intuition. Ruling 6 is literally
"qualification stays maximal, rank buries, never excludes" (confirmed via
grep, cited in multiple deviation headers) — the whole design ethos here
is use-all-available-evidence-and-let-rank-sort-it-out. Silently
discarding a second genuine shared run instead of burying it low is
arguably the anomaly relative to that principle, not the other way
around. So this is the RIGHT direction, not a rejected idea — it's sized
wrong to be a quick fix, which is a different objection. Three concrete,
verified reasons:

1. **Architecture, not data.** `compute_rank()` (`tier_engine.py:2400`)
   takes exactly one `fragment` + one `fragment_idf` — the formula itself
   is `fragment_idf * sqrt(length/5) + tag_score...`, a single term, not a
   sum over a list. `find_shared_fragment()` returns one `(text, df,
   length)` tuple. The report/viewer evidence column is one string.
   Cumulative scoring means qualification, rank, report generation, viewer
   JSON, AND `viewer.html` rendering all change shape from "one fragment"
   to "a list of fragments" — not a bigger number plugged into the same
   slot.
2. **The specific Delney/Throne suffix run still couldn't be included
   even with this change.** DF is only ever indexed at 5-token windows —
   `ngram_df_estimate()` hard-requires `len(tokens) >= ngram_min_len`
   (confirmed at `tier_engine.py:1392`). A 4-token run has no way to be
   measured as rare-or-common in the current system at all. That's a
   separate, deeper limitation (`NGRAM_MIN_LEN` itself) that cumulative
   scoring alone doesn't solve.
3. **This is REBALANCE-class work, not an additive fix.** Today's
   mana-kinship pool-widening fix (same session) was safely additive — it
   can only ever discover new pairs, never reorder existing ones.
   Cumulative fragment scoring is the opposite: it would systematically
   raise the rank of every pair that already has 2+ qualifying runs,
   which means real corpus-wide reordering, not just new discoveries. Same
   category as Phase 3's rebalance (RULING-MANIFEST-2026-07-09.md,
   R1-R3) — that one measured "~13.6% of within-tier pairs reorder" and
   needed its own dedicated impact memo and ratification cycle before
   shipping. This needs the same treatment, not a quick patch.

### DRAFT next actions — NOT AUTHORIZED

*(Sketched for the record. Requires explicit authorization before any
code is touched, same as Entries #1/#3/#4.)*

1. Measure first, per house discipline: corpus-wide, for anchor/candidate
   pairs that already share a qualifying Tier 2 text fragment, how often
   does a SECOND qualifying (>=5 token, DF-banded) run also exist in the
   same paragraph pair but go uncredited? If this is rare, the fix may not
   be worth the complexity; if common, it's a real gap. This number also
   roughly bounds the rebalance's blast radius (point 3 above) before
   committing to it.
2. If pursued: `find_shared_fragment()` needs to return multiple
   non-overlapping runs per pair (not just the single longest), each
   independently DF-banded, with a decision on how multiple qualifying
   runs combine into rank (sum idf terms? sum with diminishing returns on
   the 2nd+ run, the way idf-weighting already naturally discounts common
   tags in Tier 3's coverage formula? take the best and treat the rest as
   corroboration only, never additive?) — a real design question, not a
   mechanical change.
3. This touches the FROZEN tier-assignment core and the rank formula both
   — full gate suite green, determinism confirmed twice, corpus-wide
   before/after count of affected pairs (measured), viewer cache regen,
   report header note.

### IMPLEMENTED, 2026-07-10 (Captain's ruling, same session as the audit above)

**Ruling:**
1. **Scope constrained to the single best-matching paragraph pair**, exactly
   as the audit's own methodology assumed — `compute_fact_penalties()`
   needed zero changes, confirmed.
2. **Rank combination: diminishing returns with a FLOOR, unbounded run
   count.** Run weight by position: 1st (primary) = 1.0 (unchanged
   formula), 2nd = 0.5, 3rd = 0.25, 4th+ = 0.25 (does NOT keep decaying —
   floors at 0.25 so a candidate with many qualifying runs doesn't have its
   tail contribution vanish to near-zero). Captain's phrasing: "full, half,
   quarter, then back up to half, then continue half for any additional" —
   implemented as floor-at-0.25 first (matches runs 1-3 exactly; differs
   from the literal ask only in NOT bouncing back up for run 4, staying at
   the quarter floor instead of a half floor), by Captain's own choice
   ("let's try Floor at 0.25 first, I'll adjust if it needs to be 0.5") —
   flip `fragment_run_weight()`'s `return 0.25` to `return 0.5` for
   run_index >= 2 if this needs revisiting. Run count is unbounded (no cap)
   per Captain's ruling ("there will be a natural cap to these cards").
3. **Sub-`NGRAM_MIN_LEN` (5-token) runs: explicitly OUT OF SCOPE, deferred
   to backlog, not this build.** `NGRAM_MIN_LEN=5` is an arbitrary
   threshold, not a principled one — lowering it needs real safeguards
   first (short/common phrases risk becoming noisy, misleading-similarity
   signal rather than genuine kinship) before it's touched. Confirmed this
   build's own motivating case (Delney/Roaming Throne's 4-token suffix run)
   is UNAFFECTED by this build for exactly this reason — verified live: the
   pair still surfaces only the single 5-token prefix fragment today, same
   as before, correctly.
4. **Evidence display format**: primary fragment first, each extra run
   appended with ` + `, each with its own DF marker, e.g. `if a triggered
   ability of (DF=12) + triggers, that ability triggers an additional time
   (DF≈10)`. Same format in reports, viewer JSON export (`extra_fragments`
   list, structured), and `viewer.html`'s detail-row rendering.

**Re-audit before implementation found the original measurement (44/574,
7.7%) was WRONG on the details** (not the conclusion) — corrected via a
second script that called the live `assign_tier()` directly instead of a
standalone re-derivation, and specifically respected the engine's own
no-double-count paragraph suppression (`exclude_paragraphs`, the mechanism
that stops a keyword-kinship-claimed reminder paragraph from ALSO being
searched for text credit):
- True population (pairs where `assign_tier()` live-resolves to
  `mechanism in ("text", "reminder")`, tier 2): **1,259**, not 574 — the
  original script's DF ceiling (50) was the wrong constant; the real Tier 2
  qualification ceiling is `T2_RESCUE_CEILING=172`.
- True qualifying-second-run count: **41**, not 44 — Delney=33 (80%),
  Sakura-Tribe Elder=5 (12%), Zurgo=3 (7%). True rate against the corrected
  population: 41/1259 = **3.3%**, not the originally-reported 7.7% — rarer
  than believed, though still real and still concentrated in the same
  three anchors.
- **Zurgo's risk was overstated in the original doc.** The three
  Avenger of the Fallen/Dalkovan Packbeasts/Devoted Mardu candidates the
  original doc flagged as "HIGH RISK, overlaps `check_zurgo_keyword_gate`'s
  hand-verified cards" are `mechanism="keyword"` in the live engine (the
  Mobilize reminder paragraph is excluded from text search once keyword
  kinship claims it) — this build's scope (the text/reminder `find_shared_fragments`
  path only) never touches them at all. The three candidates actually
  affected (Dalkovan Encampment, Pugnacious Pugilist, Salt Road Skirmish,
  all `mechanism="reminder"`) appear in NO hand-verification table and NO
  hard-coded gate assertion anywhere in the codebase — confirmed via grep.
  `check_zurgo_keyword_gate()` itself was also re-read directly: it's a
  print-and-eyeball gate (row count > 0, full rank-order printout for
  review), not a hard-coded per-candidate assertion — it cannot fail from
  this change by construction.
- One more edge case surfaced and confirmed correctly out-of-scope by
  construction: a small set of pairs (8 in the Sol Ring pool, e.g. Arid
  Archway, City of Traitors) show `tier=2, mechanism="text", fragment_df=None`
  — these are Tier-1-whole-paragraph matches DEMOTED to Tier 2 by
  `types_disjoint_for_demotion()` (disjoint Artifact/Land type), keeping
  the FULL paragraph as `fragment`, never routed through
  `find_shared_fragment(s)` at all. Multi-run search correctly never runs
  on these (they're in `assign_tier()`'s `elif t1_eligible_match` branch,
  not the `else: find_shared_fragments(...)` branch this build touches).

**Corpus-wide reorder impact, measured directly** (live `assign_tier()` +
`compute_rank()`, old formula vs new, same code path both ways, full Tier 2
list per anchor, not just the displayed top-`REPORT_CAP`(10) window):
- Sakura-Tribe Elder: 42/204 Tier 2 rows reordered (20.6%), max shift 21
  positions.
- Zurgo, Thunder's Decree: 35/88 reordered (39.8%), max shift 28.
- Delney, Streetwise Lookout: 214/282 reordered (75.9%), max shift 74.
- **No candidate crosses into or out of the displayed top-10 window in any
  of the three anchors** — real, substantial internal Tier 2 reordering,
  but invisible in today's report tables/viewer default view for this
  calibration panel. Confirms why `check_stability_gate()` (blocking)
  showed zero entered/exited/moved rows on the first post-change run for
  Sakura-Tribe Elder (the only one of the three in the default
  `ANCHOR_PANEL`) — reordering happened entirely below the display cutoff.
- No Tier changes anywhere (all reordering is within Tier 2; nothing moved
  to/from Tier 1/3).

**`check_stability_gate()` extended** (the touchpoint flagged in the build
handoff doc, point 5): a row with a non-empty `_extra_fragments` list is
now a NAMED, explained cause of movement (`cumulative_scoring_fired`),
same status as the pre-existing `mechanism in ("keyword", "reminder")`
carve-out — plus a sibling-explanation variant (`sibling_cumulative_names`)
for rows that shift position because ANOTHER row in the tier gained extra
credit, mirroring the existing `sibling_mv_names` pattern. Verified this
was actually load-bearing, not defensive-only: without it, Delney/Sakura's
`mechanism="text"` reordered rows (Zurgo's are all `mechanism="reminder"`,
already auto-exempted by the pre-existing carve-out) would have shown
`UNEXPLAINED` and failed the blocking gate.

**Verification, all confirmed green:**
- Full gate suite: 73/73 PASS (default 6-anchor panel), 0 STOP/FAIL.
- Zurgo and Delney (not in default `ANCHOR_PANEL`, only in `anchors.txt`)
  independently run via `--anchor`: clean, all applicable gates PASS.
- Determinism: byte-identical across 2 runs (`snapshot.py
  verify-determinism`).
- Viewer cache regenerated (`emit_viewer.py`, 9 anchors); spot-checked
  Delney's export directly — 33 rows carry a populated `extra_fragments`
  field, matching the corrected audit count exactly.
- Two motivating live cases re-verified directly against `assign_tier()`:
  Delney vs Katara/Puppet's Verdict now show combined multi-run evidence;
  Delney vs Roaming Throne (the ORIGINAL case that started this whole
  investigation) is correctly UNCHANGED — its second run is 4 tokens,
  below `NGRAM_MIN_LEN`, out of scope per point 3 above, exactly as
  predicted.

**Files touched**: `experiments/tier_engine.py` (`find_shared_fragment` →
`find_shared_fragments`, `fragment_run_weight`, `assign_tier`'s Tier 2
branch, `compute_rank`'s new `extra_fragment_terms` param, the main
scoring loop's per-extra-run idf/weight computation, `check_stability_gate`'s
explained-movement logic), `experiments/emit_viewer.py` (`extra_fragments`
export field), `experiments/viewer.html` (detail-row rendering).

**Not yet done** (standard ritual, remaining): snapshot creation, report
header note on the record (never silent about a scoring change) —
in progress, see session log.

---

## Entry #6 — Reminder-injected fragment vs. raw paragraph text comparison bug (found live-querying Swiftfoot Boots)

**Found and fixed, 2026-07-10** (Captain live-reviewing Swiftfoot Boots'
viewer output, noticed equip-cost boilerplate cluttering its Tier 2 list;
asked whether to disable the rescue band for Equipment/Aura/anthem types).

### What's wrong

`text_injected_on_side()` and `find_reminder_attribution()` both compared a
`find_shared_fragment(s)`-reconstructed fragment (every token's trailing
period already stripped, CO-C convention) against the RAW injected-
reminder paragraph text (periods intact). Across an internal sentence
boundary within a multi-sentence paragraph (e.g. Swiftfoot Boots' Equip
reminder: `"{1}: Attach to target creature you control. Equip only as a
sorcery."` — two sentences, one paragraph), the reconstructed fragment can
never equal or substring-match the raw text, since the internal period is
a literal character the reconstruction never carries. This silently
disabled `fragment_both_sides_injected()`'s hard discount
(`PROVENANCE_DISCOUNT_WEIGHT`) for exactly the case it exists to catch.

Same bug, third location: two NAMED gate constants (`SWIFTFOOT_EQUIP_TEXT`,
`FAITHLESS_FLASHBACK_TEXT`) used raw, period-bearing text for exact-
equality checks against `row["fragment"]` — which also never carries
periods — so both checks were structurally unable to ever fire, regardless
of real state.

### Fix

Shared normalization helper (`normalize_paragraph_for_fragment_comparison()`)
applied in both functions; both gate constants redefined in already-
normalized form.

### Two gates this unmasked (were trivial always-PASS, not verified)

- **check_gb_swiftfoot_boots_gate**: even with the discount now correctly
  firing, 1 equip-reminder-boilerplate row (Ring of Evos Isle) still sits
  in Swiftfoot Boots' displayed Tier 2 top 10 — a confirmed, measured hard
  floor from Phase 3's frame-affinity restoration (any same-type match
  restores `effective_weight` toward 1.0 independent of the provenance
  discount: at `PROVENANCE_DISCOUNT_WEIGHT=0.0`, `effective_weight` still
  floors at `restored_fraction=0.375` for an Equipment-vs-Equipment pair).
  **Ruling (Captain): lower the constant as far as it actually helps, update
  the gate to reflect measured reality.** `PROVENANCE_DISCOUNT_WEIGHT`
  lowered `0.05 -> 0.01` (real benefit for different-type both-sides-
  injected matches, negligible further benefit for same-type ones — the
  floor dominates); gate's expected count updated `0 -> 1`.
- **check_gc_faithless_looting_gate**: the flashback reminder's corpus DF
  has drifted `173 -> 172` since the gate was written (ordinary corpus
  growth, unrelated to this session) — exactly at `T2_RESCUE_CEILING`'s
  inclusive boundary, so 171 rows now legitimately rescue-band-qualify
  under the already-ratified DF-banding rule. **Ruling (Captain): let it
  through, update the gate** — same "corpus reality moved, the gate's stale
  expectation gets updated, not the scoring" precedent as Discreet Retreat
  (Entry #4's `MANA_ONLY_FAMILY` addition). Gate's expected count updated
  `0 -> 171`.

### Verification

Full gate suite 73/73 green, Zurgo/Delney (not in default panel) verified
separately, determinism confirmed twice, viewer cache regenerated and
confirmed live — Swiftfoot Boots' Tier 2 top 10 now shows 9 genuine
matches (mostly the new `keyword_grant` mechanism from Entry #4) and 1
residual boilerplate row, down from the original clutter.

### Files touched

`experiments/tier_engine.py` only: `normalize_paragraph_for_fragment_comparison()`
(new, shared), `text_injected_on_side()`, `find_reminder_attribution()`,
`SWIFTFOOT_EQUIP_TEXT`/`FAITHLESS_FLASHBACK_TEXT` constants,
`PROVENANCE_DISCOUNT_WEIGHT`, `check_gb_swiftfoot_boots_gate()`,
`check_gc_faithless_looting_gate()`, report header note.

---

## Entry #7 — keyword mechanism must outrank reminder mechanism; Equipment/Aura P/T modifier ignored

**Ruled and implemented, 2026-07-10** (Captain live-reviewing Zurgo's Tier
2 table).

### Part 1: mechanism sort priority

Confirmed live: Zurgo's Tier 2 had Hanweir Garrison (`mechanism=reminder`)
ranked #1, above Zurgo Stormrender (`mechanism=keyword`) at #2 — an exact
NAMED keyword match losing to a reminder-text match purely on numeric
score. **Ruling: keyword > reminder only** (not keyword > everything —
text/mana/keyword_grant rows keep competing purely on score, unaffected),
implemented as a **guaranteed categorical sort key** (`(mechanism-priority,
-rank, ...)`, not a scalar bonus) so the ordering can never be undone by
future DF/corpus drift the way a bonus sized for today's data silently
could. See `keyword_over_reminder_priority()` in `compute_anchor_full_tiers()`.

Noted for the record, not currently observed: a strict 2-bucket priority
(keyword=0, everything-else=1) is the only internally-consistent way to
implement a HARD "always above" guarantee — a 3-way scheme where text
"stays exactly unaffected" relative to BOTH keyword and reminder
simultaneously isn't achievable in a transitive sort if text's score ever
falls between the two. In practice this is moot today: keyword-kinship
rows exist only for Zurgo among the 9-anchor panel, and Zurgo has zero
`text`-mechanism Tier 2 rows, so keyword and text never actually compete
for a slot anywhere in the current corpus. Flagged here in case a future
anchor makes this theoretical edge real.

### Part 2: Equipment/Aura P/T modifier

Entry #4's `granted_keyword_set` extraction discarded the "gets +N/+N"
stat-bonus prefix entirely (a non-capturing throwaway group) — two
equipment granting the identical keyword set but very different power/
toughness bonuses (Behemoth Sledge +2/+2 trample+lifelink vs a
hypothetical +0/+0 version) ranked as equally close kin. `GRANT_CLAUSE_RE`
now captures the P/T modifier as its own group; `parse_pt_modifier()`
parses `"+2/+2"` → `(2, 2)`; carried as `pt_mod` on each granted-keyword
fact (`None` if no "gets" clause — a missing clause means a definitive
+0/+0, not unparsed uncertainty). `granted_keyword_kinship_match()`'s
cascade gets a new flat per-point term, `GRANT_PT_MISMATCH_PENALTY_PER_POINT
= 0.15` (first-pass default, same "comparable scale, open to
recalibration" reasoning as `GRANT_KEYWORD_MISMATCH_PENALTY`, not
corpus-tuned). Confirmed live: Behemoth Sledge (+2/+2) vs Bronzeplate Boar
(+3/+2), shared `trample` — evidence now reads `trample, +2/+2 vs +3/+2
(mismatch penalty=0.45)` (0.30 keyword-mismatch for the unshared
`lifelink` + 0.15 for the 1-point P/T distance), where before it silently
ignored the stat difference entirely.

### Verification

Full gate suite 73/73 green (after updating `check_gb_swiftfoot_boots_gate`'s
measured floor `1 -> 2` — the P/T penalty made some `keyword_grant`
matches less competitive, letting a second equip-reminder-boilerplate row
back into the fixed top-10 window by relative displacement, not a new
bug), Zurgo/Delney verified separately, determinism confirmed twice,
viewer cache regenerated and confirmed live (Zurgo's keyword rows now
sort 1-12 before any reminder row; Behemoth Sledge/Bronzeplate Boar's
evidence shows both P/T values).

### Files touched

`experiments/tier_engine.py` only: `compute_anchor_full_tiers()`'s sort
keys, `GRANT_CLAUSE_RE`, `PT_MODIFIER_RE`, `parse_pt_modifier()`,
`extract_granted_keyword_clause()`, `build_granted_keyword_facts()`,
`granted_keyword_kinship_match()`, `assign_tier()`'s keyword_grant
evidence string, `GRANT_PT_MISMATCH_PENALTY_PER_POINT`,
`GB_SWIFTFOOT_MAX_DISPLAYED_EQUIP_REMINDER_ROWS`.

### Follow-up, same session: P/T mismatch corrected from penalty to guaranteed graduated priority

**Ruled, 2026-07-10.** Captain's feedback on the P/T work above: a scalar
penalty blended into the same score as tag_score/affinity/CI isn't
"priority" — it can be swamped by unrelated terms. Wanted: "exact buff get
priority, then near buffs" as a hard rule, same guarantee-not-nudge
principle as Part 1's keyword-vs-reminder fix. **Ruling: fully graduated
by distance** (not just a 2-tier exact/non-exact split).

Implemented as `pt_exactness_priority()`, a second categorical sort-key
dimension alongside `keyword_over_reminder_priority()`. Noted directly, not
glossed over: a single global total-order sort CANNOT make "exact P/T
beats near beats far" absolute among `keyword_grant` rows while ALSO
leaving every other mechanism's ordering completely untouched — if a
text-mechanism row's rank legitimately falls between two keyword_grant
rows of different P/T distance, something has to give. Pragmatic
resolution, mirroring Part 1's own 2-bucket shape: an EXACT-match (distance
0, including "neither side has a P/T mod") keyword_grant row stays in the
shared pool, competing on rank normally, unaffected. Only a NON-exact match
gets pushed into a graduated lower tier (1 per point of distance) below
that shared pool — guarantees exact > near > far among keyword_grant rows,
at the documented cost that a near/far match also sorts below every other
mechanism's rows, not just below closer keyword_grant matches specifically.
The fact-selection logic (`best_grant = min(...)` when a pair has multiple
qualifying combinations) was also reordered to prefer P/T-closeness first,
keyword-mismatch only as a tie-break.

**Verified**: monotonically non-decreasing P/T distance confirmed directly
across Behemoth Sledge's full `keyword_grant` row list (64 rows, live via
`/api/anchor`) — no exact match exists in its pool today, so distance-1
rows correctly lead, distance-2 correctly follows, etc. Full gate suite
73/73 green after updating `check_gb_swiftfoot_boots_gate`'s measured floor
a THIRD time (`2 -> 4`) — the graduated priority pushes every non-exact
keyword_grant match below the shared pool by design, letting more
equip-reminder rows into Swiftfoot Boots' fixed top-10 window purely by
relative displacement. Flagged explicitly in that constant's own comment:
this floor has moved 3 times this session from unrelated precision
improvements elsewhere, expected to keep moving as ranking gets sharper — a
future redesign (ratio/percentage check instead of an exact count) might be
more stable long-term, not built here. Zurgo/Delney and determinism
reverified, viewer regenerated and confirmed live.

---

## Entry #8 — Qualification-cascade shadowing: reminder-text boilerplate blocking real keyword_grant matches

**Investigated, ratified (per Fable 5's recommendation), and implemented,
2026-07-10.** Full investigation doc:
`~/Projects/mtjawnny.github.io/docs/REMINDER-TEXT-QUALIFICATION-CASCADE-ISSUE.md`
(includes the full session history, exact code citations, corpus
measurements, four sketched options, and Fable 5's full written
recommendation — not fully reproduced here).

### What's wrong

`assign_tier()`'s qualification cascade is "first mechanism to find
anything wins": text/reminder matching (step 3) runs before keyword_grant
(step 5, Entry #4), gated `if base is None:` — meaning if text/reminder
finds ANYTHING at Tier 2, however weak, keyword_grant never even runs for
that pair. Confirmed with real cards: Crystal Slipper, Ring of Valkas,
Skateboard, Boots of Speed, and Strider Harness all genuinely share
"haste" with Swiftfoot Boots via a clean `Equipped creature has haste`
clause — but all five also happen to have Equip cost `{1}` (same as
Boots), so their generic Equip-reminder boilerplate text-matches first and
claims the pair before keyword_grant is checked. Not a viewer bug — the
viewer renders exactly what `assign_tier()` computes; verified directly by
calling it standalone, matching the live server byte-for-byte.

Traced and ruled OUT as the same issue: mana kinship's identical `if base
is None:` gating is a DELIBERATE, already-ratified design (R6, Phase 4 —
mana kinship is meant to be the broadest, weakest, last-resort net,
losing to anything more specific is correct). keyword_grant inherited the
same code SHAPE from mana's precedent, but nobody ever explicitly ruled
that gating was right for keyword_grant specifically — it was copied, not
decided. Also checked and clean: Mechanism 1 (keyword_kinship) shows zero
shadowing anywhere in the calibration panel today.

### Corpus measurement (before ratifying, not guessed)

Of 9,059 pairs corpus-wide that qualify via `granted_keyword_kinship_match()`:
- **587 pairs** are correctly claimed today by genuinely strong, specific
  text matches (e.g. Behemoth Sledge vs Unflinching Courage, DF≈2, a
  near-verbatim "gets +2/+2 and has trample and lifelink" match) — these
  MUST keep winning; a blanket cascade-reorder (Option A) would have
  wrongly preempted every one of them.
- **71 pairs** are shadowed by PURE both-sides-injected boilerplate with
  nothing else backing the text/reminder win — these are the real bug.

This measurement is what separated the four sketched options and is why
Fable 5's Option C (narrow, categorical, boilerplate-specific) was
recommended over Option A (blanket reorder) or Option B (run everything,
pick the best by a new cross-mechanism metric).

### Fix (Option C, as recommended)

New check after the existing keyword_grant/mana blocks: if the text/
reminder path already claimed the pair (`base == 2`, `mechanism in
("text", "reminder")`) AND its entire winning evidence — the primary
fragment AND every cumulative-scoring extra run (Entry #5) — is both-
sides-M2-injected boilerplate (`fragment_both_sides_injected()`, already
built for Entry #6's discount logic) AND a genuine `granted_keyword_
kinship_match()` also qualifies, keyword_grant wins outright.
**Categorical, not a scalar comparison** — the engine has already ruled
`PROVENANCE_DISCOUNT_WEIGHT=0.01`-weighted boilerplate near-worthless;
inventing a DF-vs-grant-penalty cross-mechanism metric to reconfirm that
would be pointless. If even ONE run in the winning match is genuine
non-boilerplate text, this does not fire — the 587-pair population is
untouched by construction. Folds in Option D's evidence idea: the
displaced boilerplate match is kept, not erased, appended to the
evidence string as `[also matched: ...]`.

### A real bug caught during verification (not shipped)

The new check's first draft used `elif mechanism in ("text", "reminder"):`
chained off the wrong `if` — it fired even for Tier 0 matches (which never
set `fragment` at all, leaving it at its `None` initial value), crashing
on `fragment_both_sides_injected(None, ...)` during the corpus-wide
re-measurement pass. Fixed by requiring `base == 2` explicitly, not just
"whatever elif branch this happens to be." Caught by the verification
ritual doing its job, not by luck.

### Verification

Full gate suite 73/73 green. Corpus-wide re-measurement after the fix: 0
pairs still shadowed by pure boilerplate (was 71), all 587 genuine-text
matches confirmed byte-for-byte unchanged. `check_gb_swiftfoot_boots_gate`'s
measured floor moved a FOURTH time this session but DOWNWARD for the
first time (`4 → 3`) — a genuine reduction in clutter, not relative
displacement (Ring of Valkas correctly relabeled to `keyword_grant`).
Zurgo/Delney (not in default panel) verified separately, determinism
confirmed twice, viewer cache regenerated and confirmed live via the
actual `/api/anchor` endpoint (all five motivating cards — Crystal
Slipper, Ring of Valkas, Boots of Speed, Skateboard, Strider Harness —
now show `mechanism=keyword_grant` with the boilerplate preserved as a
note).

### Files touched

`experiments/tier_engine.py` only: `assign_tier()` (new post-cascade
check, `format_grant_evidence()` extracted as a shared helper to avoid
duplicating the evidence-building code), `GB_SWIFTFOOT_MAX_DISPLAYED_
EQUIP_REMINDER_ROWS` (4 → 3), report header note. Companion doc (separate
repo, not committed by this session): `REMINDER-TEXT-QUALIFICATION-
CASCADE-ISSUE.md`.

---

## Entry #9 — Fable 5's engine-wide weighting review: four changes (locate_fragment_context bug, sentence-boundary trim, short-whole-sentence Tier 2 path, equip-cost delta term)

**Investigated, ratified (per Fable 5's recommendation), and implemented,
2026-07-10 (new session, on top of `4759b99`).** Full investigation doc:
`~/Projects/mtjawnny.github.io/docs/EQUIPMENT-REMINDER-AND-WEIGHTING-
DELIBERATION.md` (Captain's request: take a step back from the Swiftfoot
Boots reminder-text fight across multiple prior sessions, collect
comprehensive engine context, hand it to Fable 5 to think about the whole
engine and determine whether a real lever was missing before reaching for
a blunt kill-switch — "turn off reminder text for Equipment specifically."
Three other card clusters Captain named directly (Craterhoof vs. End-Raze
Forerunners; Anguished Unmaking/Inevitable Defeat/Utter End/Vanish into
Eternity; Nahiri's Lithoforming/Lessons from Life under a Growth Spiral
anchor) were investigated alongside Equipment as part of the same
"check how other cards are weighted too" ask.

### Fable 5's core finding

"The engine has no concept of the sentence." Its only matching units are
the whole paragraph (Tier 1, no length floor) and the ≥5-token verbatim
run (Tier 2, `NGRAM_MIN_LEN`). Three of four case studies in the
deliberation doc trace to that one gap; the fourth (Equipment) turned out
to be *already correctly working* except for one real, narrow, additive
omission. Recommended sequence, each measured before the next: (1) fix a
live bug the review's own verification turned up, (2) a sentence-boundary
trim rule + (3) a short-whole-sentence Tier 2 path together (one removes
accident-admitted pairs, the other readmits the legitimate ones on honest
evidence), (4) an equip-cost delta term. Explicitly rejected: coverage/
length-normalized scoring (would punish cards for having more text,
crushing already-correct matches) and the Equipment kill-switch (the
residual "clutter" is honest, defensible weak-match burial, not a bug).

### Change 1 — `locate_fragment_context()` boundary-crossing bug (found by Fable 5, not asked for)

Same bug class Entry #6 already fixed for `fragment_both_sides_injected()`
— compared a period-stripped fragment against RAW paragraph text, which
can't match across an internal sentence boundary. Any Tier 2 row whose
fragment crossed a boundary silently got `(None, None)` here, which
`compute_fact_penalties()` reads as "unknown" — disabling ALL FIVE fact
penalties (scope/duration/exception/polarity/condition), not just one.
Measured: 87/484 (18%) of Tier 2 text/reminder rows across the doc's own
6 anchors affected; concrete case, Growth Spiral vs. Gretchen Titchwillow
(a creature) showed zero duration penalty despite being exactly the
one_shot-vs-ongoing mismatch `DURATION_PENALTY` exists to catch.

**Fix:** normalize BOTH sides of the comparison (not just the paragraph)
via the existing `normalize_paragraph_for_fragment_comparison()`. An
earlier draft normalized only the paragraph and broke 8 Sol-Ring-pool
rows whose `fragment` is itself RAW, period-intact whole-paragraph text
(Entry #5's already-documented Tier-1-demoted-to-Tier-2 case) — caught by
this fix's own corpus measurement (86/904 fixed, 0 regressions) before it
shipped, not by luck.

**Verification:** full gate suite 73/73 (default panel) + 36/36 (Zurgo/
Delney), determinism ×2, viewer regenerated and reconfirmed live (Growth
Spiral vs. Gretchen Titchwillow now correctly pays `dur=1.0`).

### Change 2 — sentence-boundary trim rule

A matched token run that happens to straddle two UNRELATED sentences
(e.g. Growth Spiral's "Draw a card." + "You may put a land..." colliding
with Nahiri's Lithoforming's unrelated "...draw a card." + "You may play
X additional lands...") reads as rare (low DF) purely because that exact
seam-crossing sequence is uncommon, not because the underlying abilities
are similar. New `trim_run_for_sentence_boundary()`: a run crossing a
sentence boundary (on either side) survives whole only if its
continuation past that boundary is itself ≥`NGRAM_MIN_LEN` tokens (real
corroboration); otherwise truncated to the leading segment, discarded if
that's also sub-floor. New per-paragraph `paragraph_sentence_ends` field
(via `sentence_boundary_indices()`) marks which token positions are
sentence-final in the RAW (pre-CO-C-stripped) text.

**Exempts reminder-injected paragraphs entirely** — caught measuring this
fix's own impact: Faithless Looting's flashback reminder ("...for its
flashback cost. Then exile it.") is Scryfall's own fixed, single-author,
always-co-occurring two-sentence explanation of ONE keyword, not two
independently-written clauses that happen to collide; trimming it dropped
`check_gc_faithless_looting_gate`'s population from 171 to 0 (the
shortened prefix's DF rose 172→178, rescue band → DEAD) — backwards from
the rule's intent. Fixed by treating any paragraph in
`reminder_keyword_by_paragraph` as having zero internal boundaries.

**Corpus-measured** (17-anchor sample: default panel + Zurgo/Delney +
this review's case-study anchors): 803 pairs had a qualifying run either
before or after; 778 unaffected, 25 lost their qualification entirely
(all verified as the exact false-positive class this fix targets — 7
Growth Spiral "draw a card you may"-class, 18 Anguished
Unmaking/Inevitable Defeat "exile target nonland permanent
[you/its]"-class), 0 trimmed-but-still-qualifying in this sample.

**Verification:** full gate suite 73/73 + 36/36, determinism ×2, viewer
regenerated and reconfirmed live.

### Change 3 — short whole-sentence identity Tier 2 path

`find_shared_fragments()` can never qualify a clause shorter than
`NGRAM_MIN_LEN` (5) tokens, by construction. "Exile target nonland
permanent" is a complete, defining 4-word ability — one word short.
Confirmed directly: Utter End and Vanish into Eternity reach Tier 1 on
this exact clause ONLY because it happens to sit alone in its own
paragraph on both cards; Anguished Unmaking and Inevitable Defeat have
the identical clause with a life-total rider glued onto the SAME
paragraph (no line break), losing the whole-paragraph shortcut and
leaving them stuck at Tier 3 — a Scryfall text-formatting accident, not a
real functional difference.

**New mechanism** (`find_shared_sentence()`, `mechanism="sentence"`): an
exact, byte-identical SENTENCE shared by both cards, scoped to sentences
under `NGRAM_MIN_LEN` only (longer ones stay on the n-gram path, never
duplicated). Reuses `clause_index`/`clause_df` — already built
corpus-wide by `build_indexes()`, previously only a fast candidate-pool
pre-filter — as an EXACT sentence-level DF count, same `para_exact_df`
convention Tier 1 already uses for short paragraphs. Same full/
discounted/rescue/dead banding as text/reminder, same `T2_RESCUE_CEILING`.
Measured: "exile target nonland permanent" has sentence-DF=17 (discounted
band).

**Placed LAST in the cascade** (after keyword_grant and mana kinship,
same "only fires if nothing else found anything" gating) — a real
implementation bug caught during this fix's own corpus measurement, not
shipped: an earlier draft placed it right where text/reminder leaves
`base` at None, which let it claim Sol Ring vs. Ancient Tomb's pair (both
share the exact short sentence "{t}: add {c}{c}") BEFORE mana kinship's
own specialized amount/color/shape cascade (R5/R6) ever ran, failing
`check_gg_sol_ring_cascade_gate` (expected `mechanism=mana`, got
`mechanism=sentence`). Fixed by moving it to the true end of the cascade
— it has no domain-specific richness of its own the way mana/keyword_grant
do, so it shouldn't compete with them for position.

**Threading note:** `clause_df` had to be threaded as a new parameter
through `assign_tier()` and ~9 calling functions (`run_self_check`,
`check_symmetry`, `check_scope_duration_spotchecks`,
`check_godsend_gate`, `check_polarity_family_gate`,
`check_basandra_gate`, `compute_candidate_rows`, plus the `ctx`-based
gate functions and `emit_viewer.py`'s own `compute_candidate_rows` call)
— `ctx["clause_df"]`/`ctx.clause_df` were already populated (clause_df
was already corpus-wide-computed for the pre-existing candidate-pool
pre-filter), so no new corpus-wide computation, just wiring.

**Corpus-measured** (same 17-anchor sample): 66 new `mechanism="sentence"`
rows, entirely concentrated in the motivating cluster (Anguished Unmaking
22, Inevitable Defeat 16, Utter End 14, Vanish into Eternity 14) plus a
handful of genuine "you lose 3 life" (DF=7) matches on unrelated
life-loss cards — zero rows fired anywhere else in the sample, including
all 6 default-panel anchors.

**Verification:** full gate suite 73/73 + 36/36, determinism ×2, viewer
regenerated and reconfirmed live (Anguished Unmaking's Tier 2 list now
shows all three siblings at `mechanism=sentence`).

### Change 4 — equip-cost delta term for `keyword_grant`

`granted_keyword_kinship_match()` had no signal for Equip-ACTIVATION-cost
closeness — only the card's own CASTING cost (`mv_delta`, a different
axis) entered the shared rank formula, so two Equipment granting the
identical keyword set for `{1}` and `{5}` Equip costs scored equally
close kin. **Rejected the flagged fallback** (disable reminder-text Tier
2 qualification for Equipment): verified directly that Swiftfoot Boots'
3 residual displayed boilerplate rows (Ring of Xathrid, Cobbled Wings,
Ring of Evos Isle) share no real keyword grant with Boots at all — honest,
defensible weak matches, "rank buries, never excludes" working as
intended, not a bug to chase.

**Doc erratum caught during implementation:** the deliberation doc cited
Cloak of the Bat/Fleetfeather Sandals (tied at 6.267) as proof of
equip-cost blindness — both are actually `Equip {2}` granting the
identical keyword set, functionally identical cards, correctly tied.
Caught by Fable 5's own independent verification before implementation.

**Fix:** `EQUIP_COST_RE`/`parse_equip_cost_value()` extract each
Equipment's Equip cost as a numeric value (relative-distance heuristic
via `mana_symbols_numeric_value()`, not rules-accurate mana value) from
RAW oracle text, carried on each `granted_keyword_facts` entry alongside
the existing P/T-modifier field. A missing/unparseable cost (an Aura, or
a non-mana cost like "Equip—Sacrifice a creature") is genuinely UNKNOWN,
contributes zero penalty — the opposite convention from the P/T-modifier
field (there, a missing clause IS a definitive +0/+0). New flat per-point
term `GRANT_EQUIP_COST_PENALTY_PER_POINT=0.15`, same scale as the
existing P/T-mismatch term.

**Corpus-measured:** 372 qualifying grant facts, 151 with a parsed
numeric equip cost (221 Auras/non-mana-cost Equipment correctly
None/unpenalized), values ranging 0-7, clustering 1-4 — comparable scale
to the P/T term, no re-tuning signal from the distribution.

**Verification:** live, Lightning Greaves (`Equip {0}`) vs. Swiftfoot
Boots (`Equip {1}`) now shows `equip 1 vs equip 0` with penalty raised
0.60→0.75; Boots' displayed Tier 2 top 10 unaffected (still 3 boilerplate
rows, unchanged). Full gate suite 73/73 + 36/36, determinism ×2, viewer
regenerated and reconfirmed live.

### Files touched

`experiments/tier_engine.py`: `locate_fragment_context()` (both-sides
normalization), `sentence_boundary_indices()` (new), `paragraph_
sentence_ends` (new face field), `longest_common_run()` (now also returns
`end_b`), `trim_run_for_sentence_boundary()` (new),
`find_shared_fragments()` (trim integration), `find_shared_sentence()`
(new), `assign_tier()` (new last-cascade-step sentence path, `clause_df`
threaded through), `EQUIP_COST_RE`, `GRANT_EQUIP_COST_PENALTY_PER_POINT`,
`mana_symbols_numeric_value()`, `parse_equip_cost_value()` (new),
`equip_cost_value` (new face field), `build_granted_keyword_facts()`
(equip cost carried per-fact), `granted_keyword_kinship_match()` (equip
term), `format_grant_evidence()` (equip note in evidence string),
`run_self_check`/`check_symmetry`/`check_scope_duration_spotchecks`/
`check_godsend_gate`/`check_polarity_family_gate`/`check_basandra_gate`/
`compute_candidate_rows` (all threaded `clause_df`), four report header
notes (one per change). `experiments/emit_viewer.py`: `compute_candidate_
rows()` call updated for the new `clause_df` parameter. Companion doc
(separate repo, not committed by this session):
`EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md`.

**Committed and pushed** (Captain's explicit ask, same session): commit
`f50d6ec` (the four changes above) and `c65f04d` (wiring `keyword_grant`/
`sentence` into `viewer.html`'s mechanism filter + badge colors, a
display-only follow-up, no engine/scoring change). Both on `main` ==
`origin/main` as of this note.

---

## Entry #10 — Second-class phrase bucket (superseding a same-session obliteration draft) + a keyword_grant pool-seeding bug it uncovered

**Ruled and implemented, 2026-07-10, new session on top of `c65f04d`.**
Captain's own words, after reviewing Entry #9's equip-cost delta term
live: "equip reminder text still overwhelmingly survived. obliterate
it." First draft did exactly that (excluded the Equip reminder from
Mechanism 2 injection entirely, see the superseded write-up below).
Captain then stepped back from it: **"rather than completely exclude...
let's create a second class bucket for sentences and word groups I want
to personally demote... don't remove. bucket kneecap it hard enough
where it assuredly appears near the bottom."** Explicitly framed as
staying in the spirit of ruling 6 ("qualification stays maximal, rank
buries, never excludes") rather than adding a second, narrower exclusion
mechanism alongside the DEAD DF band.

### The final design

`SECOND_CLASS_PHRASE_PATTERNS`: a short, explicit, Captain-curated tuple
of compiled regexes (same style/precedent as `SCOPE_PATTERNS`/
`EXCEPTION_PATTERNS`/`CONDITION_MARKERS`) — currently the Equip-cost
reminder boilerplate and `"you lose \d+ life"` (Captain's own named
example — a minor rider clause, e.g. Anguished Unmaking's second
sentence, real evidence but shouldn't outrank a card's actual defining
ability). `is_second_class_phrase(text)` checks a fragment against the
list via `.fullmatch()` (matched against the fragment as `compute_rank()`
already sees it — CO-C period-stripped, lowercased).

`second_class_priority(row)`, a new function in
`compute_anchor_full_tiers()`: a row's ENTIRE winning evidence — the
primary fragment AND every cumulative-scoring extra run (Entry #5) —
must match the list for the demotion to fire; if even ONE run is genuine
non-listed text, the row stays in the normal competitive pool (same
"all runs must agree" discipline as Entry #8's boilerplate-override
check). Scoped to `mechanism in ("text", "reminder", "sentence")` — the
only mechanisms whose evidence is a literal matchable string.
Categorical, not a scalar penalty (same guarantee-not-nudge shape as
`keyword_over_reminder_priority()`/`pt_exactness_priority()`), placed
FIRST in both Tier 1 and Tier 2's sort tuples so it dominates every
other consideration, per Captain's own "assuredly near the bottom"
framing.

Mechanism 2 injection is restored to its pre-obliteration behavior
(unconditional) — the Equip reminder is matchable again, everywhere.

`check_gb_swiftfoot_boots_gate` rewritten a third time this session: no
longer tracks an exact display-window count (which moved 0→1→2→4→3
across five earlier precision fixes, then briefly "retired" to a hard 0
under the obliteration draft) — now verifies the demotion GUARANTEE
structurally: (a) zero equip-reminder rows in the displayed top 10, (b)
equip-reminder rows still PRESENT (not excluded) in the full Tier 2
list, (c) every one of their positions is strictly after every
non-second-class row's position. All three must hold.

### A real bug caught verifying the obliteration draft, still true and still fixed here

`gather_candidate_pool()` had **no seeding path of its own for
`keyword_grant`** — the same class of gap already found and fixed this
session for mana kinship (`build_mana_pip_index()`, the Priest of
Gix/Dark Ritual case), just never noticed for `keyword_grant` because
Equipment's own Equip-reminder boilerplate text overlap was
ACCIDENTALLY doing double duty as its pool-seeding path this entire
time, since Entry #4. Confirmed directly while testing the obliteration
draft: excluding the Equip reminder collapsed Swiftfoot Boots' candidate
pool from dozens of cards to **2** — Lightning Greaves, Entry #4's own
motivating case, vanished from the pool entirely even though
`assign_tier()` still correctly resolves it to `keyword_grant` when
called directly on the pair. It was never being DISCOVERED via any
seeding path of its own. This bug is independent of which demotion
strategy the boilerplate itself gets, so the fix stands regardless of
the pivot: `build_granted_keyword_index()` (granted keyword name ->
`set(oracle_id)`, scoped to `GRANT_SIZE_CEILING`, no DF-floor gate —
same "any shared keyword qualifies, no evergreen-style prune case"
reasoning as mana kinship's own index), wired into
`gather_candidate_pool()` as a new seeding block.

### Verification

Swiftfoot Boots' full Tier 2 list is back to 99 rows (57 second-class,
demoted; 42 genuine). Displayed Tier 2 top 10, confirmed live via
`/api/anchor`: Bilbo's Ring / Lightning Greaves / Cloak of the Bat /
Fleetfeather Sandals / My Precious / Ring of Valkas / Unicycle /
Brilliant Wings / A-Cori-Steel Cutter / Dragon Breath — 100% genuine,
zero second-class rows visible. Anguished Unmaking's real siblings
(Utter End, Inevitable Defeat, Vanish into Eternity) rank at the top of
its own list; its five "you lose 3 life" coincidences (Ulcerate, Black
Market Connections, Grim Servant, Hostile Negotiations, The Cruelty of
Gix) sort to the very bottom, present but never excluded. Confirmed the
pool-seeding fix is purely additive elsewhere (Mask of Avacyn, an Aura,
unaffected at 17 Tier 2 rows). Full gate suite 73/73 → 74/74 (one
additional assertion line inside `check_gb_swiftfoot_boots_gate`, not a
new gate) green (default panel) plus 37/37 (Zurgo/Delney), determinism
confirmed twice, viewer cache regenerated and reconfirmed live.

### Files touched

`experiments/tier_engine.py`: `SECOND_CLASS_PHRASE_PATTERNS` +
`is_second_class_phrase()` (new), `second_class_priority()` (new, inside
`compute_anchor_full_tiers()`), both Tier 1/2 sort keys (new leading
priority dimension), `check_gb_swiftfoot_boots_gate()` (rewritten to a
structural check), `build_granted_keyword_index()` (new),
`gather_candidate_pool()` (new `granted_keyword_index` param + seeding
block), `build_gate_ctx()` (new `granted_keyword_index` key), `main()`
(builds and threads the new index), report header note (rewritten to
describe the final design, superseding the obliteration draft's note).
`experiments/emit_viewer.py`: `gather_candidate_pool()` call + context
`SimpleNamespace` updated for the new `granted_keyword_index` parameter.

**Not yet committed** — Captain's explicit ask required first, per house
rule.
