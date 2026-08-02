# DERIVED-TAG-LAYER SPEC (v1) — Engine-Derived Semantics for Tier 3

Status: DESIGN FOR DISCUSSION, grounded in a measured prototype run against
the full 38,233-card corpus this session. Nothing here authorizes a build.
Extends TIER-ENGINE-V3-PROPOSAL.md; supersedes nothing — `rule:turn-scoped`
(v2.6 amendment 2) is the ratified prototype this generalizes.

## Purpose

Tier 3 is the product's headline promise ("same job, different words") and
currently rests entirely on Scryfall Tagger overlap: volunteer-curated,
2,683 cards uncovered, ranking by curation density. This layer adds a
second, independent semantic signal the engine derives deterministically
from oracle text it already normalizes — no Tagger dependence, no
embeddings (empirically ruled out this session: the Deck Finisher vector
stack returns surface-form creature noise for Grand Abolisher and misses
Defense Grid in both directions), no per-card human labor.

## Prototype: what was measured, verbatim

Seven v1 regexes + one family umbrella were run over every card's
matchable paragraphs, and Grand Abolisher's Tier 3 was recomputed with the
extended tag layer.

Corpus DF (deterministic, reproducible):

| tag | DF | idf |
|---|---:|---:|
| rule:turn-scoped (shipped) | 731 | 3.96 |
| rule:cost-reduction | 645 | 4.08 |
| rule:cast-interference (family) | 482 | 4.37 |
| rule:pay-tax | 243 | 5.06 |
| rule:uncounterable | 117 | 5.79 |
| rule:restricts-activation | 105 | 5.90 |
| rule:cost-increase | 102 | 5.93 |
| rule:restricts-cast | 97 | 5.98 |
| rule:restricts-opponent-cast | 42 | 6.81 |

Grand Abolisher derived: restricts-opponent-cast, restricts-activation,
turn-scoped, cast-interference. Defense Grid derived: cost-increase,
turn-scoped, cast-interference. The bridge exists and is machine-derived.

Naive integration result (derived tags appended into the existing
anchor-coverage score): T3 grew 68 → 117 with a genuinely strong new top
band (Abeyance, Interdict, Damping Engine, Sphinx's Decree, Lavinia,
Collector Ouphe — real interference kin, previously invisible) — BUT
Defense Grid only moved #31 → #29, Dosan the Falling Leaf fell #7 → #25,
City of Solitude fell #6 → #24, and Teferi Time Raveler dropped out
entirely. Two root causes, and they define this spec's two hard
requirements:

**Lesson 1 — polarity canonicalization is mandatory.** Dosan and City of
Solitude phrase the SAME restriction positively ("players can cast spells
only during their own turns") while Abolisher phrases it negatively
("opponents can't cast spells... during your turn"). A derivation that
only matches one polarity splits a functional family down the middle —
the exact failure the whole layer exists to fix. Every restriction-class
derivation MUST canonicalize both forms ("can't X during Y" ≡ "can X only
during Z") into one tag. This is also precisely the class of miss the
Fable-5 audit role (below) exists to catch at scale.

**Lesson 2 — derived tags need their own additive score term.**
tier3_score is anchor-directional COVERAGE: adding derived tags to the
anchor grows the denominator and dilutes every existing Tagger-only match
(that is what demoted Dosan). Ruling proposal: Tier 3 score becomes

    score = tagger_coverage + DERIVED_WEIGHT * derived_agreement

where derived_agreement = sum of shared rule:-tag idf, normalized by the
anchor's own rule:-tag idf sum (anchor-directional, same convention), and
DERIVED_WEIGHT is a ratified constant (proposed 0.5 to start). Property:
adding a derivation can never demote an existing Tagger match — the two
signals corroborate, never dilute. Qualification threshold unchanged;
untagged cards become T3-reachable through the derived term alone.

## Architecture

Three parts, three different owners:

**1. Derivations — deterministic engine code (machine-owned).** Each
derivation is a normalized-text pattern + polarity canonicalization,
shipped inside the engine, run at build time, following the v2.6 ritual
verbatim: print the pattern, corpus DF, computed idf, and a fixed-seed
20-card sample for eyeball review before it ever feeds scoring. Ratified
individually, like every other constant. Derivations read oracle text, so
Tagger coverage gaps don't propagate.

**2. Family tree — one ratified YAML page (Captain-owned).** Cross-
mechanism jumps live here: a family umbrella tag is emitted (at the
existing inherited-tag 0.5 discount) whenever any member fires. The
prototype proved this is where the interesting bridges happen — and also
where the judgment calls live: is rule:uncounterable in the
"protect-your-turn" family with restricts-opponent-cast (Vexing Shusher's
route into Abolisher's list — currently absent because the prototype's
family tree didn't include it)? That is a rules-philosophy call, and the
whole surface is a few dozen lines, not 35k cards. Proposed v1 families:
- rule:cast-interference = {restricts-cast, restricts-opponent-cast,
  cost-increase, pay-tax}
- rule:resolution-protection = {restricts-opponent-cast, uncounterable,
  turn-scoped-restriction} (the Abolisher/Shusher/Silence axis — draft,
  needs Captain's tree)
- rule:activation-interference = {restricts-activation, activation
  cost-increase}

**3. Provenance classes — the governance frame.** The determinism ruling
governs the ENGINE, not its data inputs — Tagger data is already
external-judgment data consumed as a versioned artifact. This table makes
that explicit and creates the slot the LLM question lands in:

| class | source | weight | example |
|---|---|---|---|
| tagger | Scryfall Tagger dump | 1.0 (0.5 inherited) | hate-flash |
| rule-derived | engine derivation | via derived_agreement term | rule:cost-increase |
| human | tags/cards.yaml, TX | 1.0 | Captain's own calls |
| llm | batch-generated artifact | discounted, proposed 0.5 | (future, below) |

## V1 derivation set (proposal for ratification)

The prototype seven, amended per Lesson 1, plus two:

1. rule:restricts-cast / rule:restricts-opponent-cast — BOTH polarities
   ("can't cast" AND "can cast ... only ..."), scope-classified via the
   existing SCOPE_PATTERNS machinery.
2. rule:restricts-activation — both polarities, same scope treatment.
3. rule:cost-increase / rule:cost-reduction — scope-classified
   (opponents'/your/all); reduction is NOT in any interference family.
4. rule:pay-tax — "unless ... pays" (Rhystic/Mystic Remora/Smothering axis).
5. rule:uncounterable — self and granted forms distinguished
   (rule:uncounterable-self vs rule:grants-uncounterable).
6. rule:turn-scoped — shipped, unchanged.
7. rule:grants-<keyword> — emitted from granted_keyword_facts, zero new
   parsing (the facts already exist).
8. rule:prohibits-attack / rule:prohibits-block — the Encrust/Pacifism
   axis the prototype accidentally surfaced via restricts-activation;
   splitting it keeps the activation family clean.

Deliberately NOT in v1: trigger-condition tags (Tagger covers ETB well),
mana-production tags (T2 mana kinship already owns that axis), anything
requiring cross-sentence reasoning. Grow the set only when a poke shows a
concrete miss — same discipline as everything else.

## Can Fable 5 build out the tags? — Yes, in three roles, in this order

**Role 1 (core, recommended): I write the derivations, the corpus writes
the tags.** For everything above, no model touches any card at runtime —
I author the patterns and canonicalization rules, the engine applies them
deterministically to all 38,233 cards on every weekly build. This is most
of the value, it is reproducible forever, and it is what this spec is.

**Role 2 (recommended alongside): I audit and mine at corpus scale, as a
harness, not a data path.** The prototype's Dosan miss is the exact shape
of error this catches: batch-run the corpus against each derivation's
INTENT ("does this card restrict when players may cast spells?"), diff
model judgment against regex output, and hand Captain two short lists —
cards the pattern missed (candidate rule amendments) and cards it wrongly
caught (candidate tightenings). Model output never enters an artifact;
only the amended deterministic rules do, each through the normal ritual.
This is how one person governs 35k cards without touching 35k cards:
you ratify RULES and review DIFFS, the machine does the enumeration.

**Role 3 (optional, later): direct LLM tags as their own provenance-class
artifact — for the residue structure can't reach.** Some function is
genuinely semantic ("this is graveyard hate" phrased seventeen ways).
Mechanics if/when wanted: closed vocabulary only (the model assigns from
a ratified tag list, never invents slugs), batch API over oracle text,
two-pass self-agreement (a tag ships only if both passes emit it),
structured output, the artifact version-pinned in the manifest (model id +
prompt hash + date), consumed exactly like the Tagger dump, scored at the
llm-class discount, stratified 200-card fixed-seed samples for Captain's
eyeball per refresh, and NEVER gate-bearing — llm tags add rank signal,
they never qualify or disqualify anything on their own. Honest limit
stated up front: at 35k scale I will make low-single-digit-percent errors
on rules-nuanced cards; the discount, the closed vocabulary, the audit
samples, and TX quarantine are the containment, same as they are for
Tagger's own errors. Cost is modest at batch rates with a small model —
verify current pricing before scheduling. Recommendation: build Roles 1–2
first; they shrink the residue Role 3 would cover, and the poke will show
whether it is still needed.

## Sequencing and gates

1. Ratify Lesson 2's scoring change (the additive derived term) FIRST —
   without it, every derivation added demotes existing good matches, as
   measured.
2. Land v1 derivations one at a time through the v2.6 ritual; family tree
   ratified as one page.
3. Gates: (a) fixed before/after panel — Abolisher's list must contain
   Defense Grid, Dosan, City of Solitude, Silence-family, all at or above
   their pre-derivation positions, plus the new interference band;
   (b) determinism ×2; (c) the discovery superset gate extended — derived
   tags seed the pool exactly as Tagger tags do (same tag_index path), so
   this is automatic once they share the index.
4. Role-2 audit pass over the v1 set; amendments ratified; batch
   precompute proceeds only after the §8-style poke over the derived layer
   clears — same bar as everything else.
