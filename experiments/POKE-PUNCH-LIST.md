# §8 Validation Poke — Running Punch List

Running log of findings from the READY-TO-SHIP display-layer contract's
§8 gate (~30-card poke through the local viewer/server, before any batch
precompute work is authorized). Entries are investigation + documentation
only unless marked otherwise. Nothing in this file authorizes an engine
change by itself — see each entry's "Ruling" line.

---

## Entry #1 — Kinship both-params display

**Ruling (Captain, 2026-07-07): HOLD.** No code changes this session.
Batched with other poke findings into a single future change order.

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

**Ruling: PENDING.** Not yet ruled by Captain. Logged from the top-100
audit; no code touched. Unlike Entry #1, this is a **scoring-affecting**
correctness bug (it changes which candidates qualify for Tier 1/2), not a
pure display gap — flagging that distinction explicitly since a fix here
would touch the FROZEN tier-assignment core (`tier_engine.py:1215`), not
just export/display formatting.

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
