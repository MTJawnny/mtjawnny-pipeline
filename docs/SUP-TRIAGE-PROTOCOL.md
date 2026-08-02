# SUP-TRIAGE-PROTOCOL — foundry batch review loop (ratified 2026-07-18)

Target path: docs/SUP-TRIAGE-PROTOCOL.md (pipeline repo).
Supersedes row-level review in foundry_review.html for batch verdicts.
Ratified deviation from T3-AXIS-FOUNDRY-v3: SUP performs full-pass triage;
Captain ratifies at proposal level. The review tool remains available for
ad-hoc inspection. Batch-1 precedent: 0 reversals on a fixed-seed 30-row
override check.

BATCH-1 PROVENANCE NOTE: batch 1 predates the annotation convention; its
ratification happened in chat (SUP-triage session, 2026-07-18) and its
authoritative record is decisions/batch-1.json itself. TRIAGE-BATCH-1.md
carries no written annotations by design. The written convention applies
from batch 2 onward.

## The loop (per batch N)

1. `/triage-alpha N` — cheap model. Consolidate + enrich + emit DIGEST.
2. `/triage-beta N` — top model. Read digest, write TRIAGE-BATCH-N.md
   with prefilled verdicts + questions + override sample. STOP.
3. Captain edits TRIAGE-BATCH-N.md in place (see annotation convention),
   checks the override sample against card text.
4. `/triage-emit N` — cheap model. Parse annotations -> decisions ->
   reconcile -> codebook vN -> assemble batch N+1 -> cost estimate -> STOP
   for Captain's Batch API go-ahead.

Chat (Fable 5) is reserved for: protocol changes, ruling disputes,
step-back audits, and periodic spot-audits of beta's triage quality.
No data files shuttle through chat.

## Artifact contracts

**DIGEST** (`experiments/out/foundry/review/digest-batch-N.md`, target
under ~60KB): per axis one header line
`slug | scope | n | quote-DF min/med/max | reminder-count` + definition +
one line per member (card name, quote-DF, reminder flag, quote <=80ch);
token groups sorted by size with member labels AND card names; stats
block (instance distribution, discard audit, reminder-flag split
exact-vs-substring); Alchemy-row and layout anomalies listed.
Generated deterministically (x2 byte-identical).

**TRIAGE-BATCH-N.md** (`docs/`): lanes KILL / MERGE / KEEP each entry
prefilled `VERDICT: <verdict>` with a one-line reason; QUESTIONS lane,
each `Q<i>` a tight either/or ending `-> RULE: ______`, max 8;
OTHER-lane promotions with named members; override sample: 30 rows,
fixed seed = 20260718 + N, drawn from confident calls only, table of
axis | verdict | sample member | quote; batch-feedback section for the
next SYNTH prompt; **MEMBER ROSTER section (added batch-5 per batch-4
punch list; made STRUCTURALLY MANDATORY batch-6 D6 after a batch shipped
without it): every axis, full member card names only (no oracle text) —
lets Captain audit membership directly instead of trusting the verdict
logic alone. Generate it mechanically (re-derive from the digest in code,
apply every section-1-3 correction as code) rather than by hand — this
is what caught batch 6's own duplicate-member and stranded-member bugs.
The emit step's state-check treats a missing roster as an incomplete
artifact, not a skippable nicety.**

**Decisions** (`experiments/out/foundry/decisions/batch-N.json`,
schema sup-triage-decisions-v1): per-axis verdicts
KEEP/KILL/MERGE(merge_into)/RENAME(rename_to, params, member_removals,
notes), other_lane promotions, captain_authored_axes (provenance human,
corpus-validated), ledger_candidates_carry_forward, new_rulings,
punch_list, override_spotcheck record (seed, n, reversals, result).

## Captain annotation convention (inside TRIAGE-BATCH-N.md)

- Change a verdict: edit the word after `VERDICT:` (KEEP/KILL/MERGE/RENAME).
  For MERGE add `INTO: rule:<slug>`; for RENAME add `TO: rule:<slug>`.
- Answer a question: fill the `-> RULE:` blank in place.
- Anything else: add a line starting `NOTE:` under the entry.
- New axis from Captain: add a block under `## CAPTAIN-AUTHORED` with
  slug, definition, example cards (emit will corpus-validate, provenance
  human, full weight, skips model pipeline per standing ruling).
- Untouched entries = ratified as proposed.

## Standing rules (bind every session in this loop)

- Vocabulary: "tier" = card tiers only; worker classes DET/BULK/SYNTH/SUP.
- Evidence-quote-or-discard on every per-card assignment; oracle text only.
- All-paragraph / all-faces scanning everywhere.
- Determinism: fixed seeds, explicit sort keys, x2 byte-identical gates.
- Paper rows preferred over A- Alchemy variants in sampling and emit.
- Rank buries, never excludes; DERIVED_QUALIFY_DF_CEILING = 172;
  DERIVED_WEIGHT = 0.5.
- Bare keywords / reminder text / procedural riders are never axes;
  killed keyword mechanics go to docs/KEYWORD-LEDGER-CANDIDATES.md in the
  same commit set.
- Nothing model-generated is load-bearing without Captain ratification.
  HALT LOUDLY on ambiguity; never lossy-map, never guess.
- Every Batch API submission: cost estimate from CURRENT pricing docs +
  Captain go-ahead. Never remembered prices.
- **Gate #0 (batch-6 D1): a card must be legal or restricted in at least
  one Scryfall format to be a valid target anywhere in the foundry
  pipeline** (DET pass, batch assembly, SYNTH, reconcile). Nowhere-legal
  cards (playtest/CMB1/CMB2/MB2, Unknown Event promos, prototype/event
  cards, bare token printings) are excluded outright, independent of the
  corroboration gate. Use `foundry_common.gate_passes()` /
  `load_corpus_gated()`; `load_corpus()` stays raw/unfiltered for
  tier_engine.py's other, non-foundry consumers.
- **Remove-and-rehome (batch-6 D5): every member_removal must state where
  the card actually belongs** — an existing axis (member_addition), a
  proposed captain-authored sibling, or an explicit "no home;
  ledger-flagged" note in PARENT-TREE-CANDIDATES.md. Silently stranding a
  removed card is a protocol violation.
- **Naming grammar (batch-7 section 12, ratified `docs/CODEBOOK-NAMING-GRAMMAR.md`
  v1.0): every axis slug — authored, grammar-instantiated, or renamed —
  must validate against that document's slot grammar and closed
  vocabularies.** Highlights binding on every batch from here forward: the
  bare token "defender" is banned in slugs (use "defending-player," CR
  506.2); the participle "countered" is banned as a counter-noun
  (ambiguous with Counterspell); the activation-restriction family (§3) is
  fully enumerated and DET-owned — SYNTH must not assign it. Grammar-
  composable axis homes (§11) instantiate immediately on first
  quote-verified member; ledger-flagging one instead is a protocol error
  as of batch 7 (D7). `docs/CORPUS-PASS-PLAN.md`'s combined per-axis walk
  (steps 2–5) uses this document as its kickoff and is not yet run —
  until it runs, most of the codebook has not been validated against it.

## SUP standard updates (ratified batch 2, binding from batch 3 onward)

RESTORED 2026-08-02. These ratified rules were present only in the site
repo's gitignored fork of this document and absent from this — the copy the
`/triage-*` skills actually load — from the 2026-07-19 partial migration
(`abf9c2b`) until now. Batches 4–7 and corpus-pass run 1 all ran without
them in the operational protocol.

- **"Don't absorb, expand."** When candidate axes differ by object class,
  target class, or game vector, prefer sibling axes plus a logged parent
  scheme over an absorption merge. Absorption is right when ONE
  vector/mechanism (e.g. mana) would own the rule; wrong when it would
  swallow multiple distinct mechanics under one label (e.g. "any count of
  anything scales an effect" is not one axis). Example family this
  ratified: the damage-target axes are per-object-class
  (`rule:direct-damage-any-target`, `rule:targeted-creature-damage`,
  `rule:targeted-player-damage`, `rule:targeted-planeswalker-damage`,
  `rule:targeted-battle-damage`) — mixed-target cards get MULTIPLE tags,
  never a combination tag (damageable objects are a closed system in
  Magic).
- **Cost qualifiers in axis names are binding.** An axis named "free
  ___" may not absorb paid-cost members ("Free must be Free").
- **Copying a spell is never casting a spell.** Guard against this
  conflation in all cast-trigger derivation work.
- **Joke / Un-set / non-constructed-legal-only card families get no
  axis.**
- Final-audit naming standardization (consistent family-naming schemes
  across the whole codebook, e.g. `rule:animate-<type>`,
  `rule:<type>-scales-with-<type>-count`) is a standing punch-list item,
  applied in one pass once the codebook stabilizes — never mid-flight
  during a batch.

## Convergence metrics (report both, every batch)

(a) Spec metrics: OTHER-lane rate and kill/merge/rename rate — annotated
that raw OTHER rate is method-inflated under exact-match clustering and
deflated once two-lane codebook labeling starts; read trend, not level.
(b) Ratified primary: OVERRIDE RATE — Captain reversals / beta's
confident calls, plus the fixed-seed spot-check result. The bootstrap
gate question is whether the pipeline's judgment converges on Captain's.
