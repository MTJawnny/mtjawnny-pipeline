#!/usr/bin/env python3
"""Machine-assigns thesaurus tiers 0-3 for a panel of anchor cards and emits
eyeball markdown reports. THESAURUS-TIER-PROTOTYPE-HANDOFF.md, script 2,
amended by TIER-ENGINE-V2-CHANGE-ORDER.md (frame gate, disjoint-type
demotion, n-gram fragment matching for Tier 2),
TIER-ENGINE-V2.1-CHANGE-ORDER.md (within-tier rank score, report
visibility, new validation gates), TIER-ENGINE-V2.2-CHANGE-ORDER.md
(fact-distance penalties in Tier 1/2 rank: CI relation and MV delta), and
TIER-ENGINE-V2.3-CHANGE-ORDER.md (per-ability effect scope, per-face
effect duration, per-ability exception/carve-out marker; revised CI-step
table; MV_PENALTY 0.25->0.5), TIER-ENGINE-V2.4-CHANGE-ORDER.md
(per-fragment polarity/prohibition marker, per-ability condition-narrowing
marker, scope pattern-table bug fix for bare-plural "players" subjects),
and the v2.5 change order in TIER-ENGINE-STATE-AND-V2.5-HANDOFF.md (the
first POSITIVE fact term: frame-affinity bonus -- type-bucket match and
shared creature subtypes -- ruled in to fix Drannith Magistrate losing to
Avatar's Wrath in Grand Abolisher's Tier 2 on a phrase-boundary DF
coincidence rather than on any real functional difference).
Tier ASSIGNMENT is frozen as of v2 -- v2.1/v2.2/v2.3/v2.4/v2.5 touch only
within-tier ORDER and how much of it a report shows.

SESSION AMENDMENT (2026-07-06, supersedes standing ruling 5 and v2.5
change-order gate 3): approved-anchor rank stability is NO LONGER a
blocking gate. The affinity bonus is expected to reshuffle any anchor's
tier lists considerably (Myrel, Preordain, Sakura-Tribe Elder, Sol Ring,
Marisi) -- that is accepted in advance, not a regression. Six-anchor
before/after diffs are still computed and printed every run for Captain's
review, but they are informational only and never halt the run. Grand
Abolisher's Drannith-vs-Wrath ruling (v2.5 gate 1) and the frozen tier-
ASSIGNMENT/determinism/MVΔ-audit gates remain fully blocking.

SESSION AMENDMENT 2 (2026-07-06, graded superset CI): the v2.5 affinity
bonus correctly gave Sen Triplets +0.25 (a real shared "Human" subtype with
Grand Abolisher), which then resurfaced it in Abolisher's Tier 2 displayed
top 10 -- not an affinity-bonus bug, but the flat superset CI step (2,
regardless of width) undercharging Sen Triplets' true CI distance (mono-W
anchor vs WUB, +2 colors). Ruling: grade the superset step instead --
`min(1 + colors_added, SUPERSET_STEP_CAP)` -- leaving SUBTYPE_BONUS and
MV_PENALTY untouched and same/subset/overlapping/disjoint flat. See
ci_relation_step_value() and graded_superset_step(). This is the cheap
intermediate step toward the backlogged per-color pip-vector comparator,
not that comparator itself.

v2.6 CHANGE ORDER -- two amendments. Amendment 1: a Tier 2 corroboration
gate amends standing ruling 6 ("qualification stays maximal, rank buries,
never excludes") -- a fragment-qualified Tier 2 candidate is now DISQUALIFIED
outright when its polarity is a functional inversion of the anchor's AND it
shares zero weighted tag DNA (tier2_corroboration_disqualified()). This
retires Grand Abolisher's 16-card "spend this mana only" family
(MANA_ONLY_FAMILY) from Tier 2 entirely (44 -> 28 rows) rather than merely
burying them. Amendment 2: a new engine-derived, rule:-provenance tag,
rule:turn-scoped, detects turn-window-asymmetry phrasing ("during your
turn", "on your turn", "during its controller's turn", etc. -- excluding
pure duration phrases) and is injected into Tier 3's anchor-directional
tag-overlap computation ONLY (see run_turn_scoped_derivation(),
build_turn_scoped_tag_index()) -- deliberately NOT fed into Tier 1/2's rank
tag_score term this round (deferred, see KNOWN_LIMITATIONS).

Standalone experiment: reads data/raw/oracle-cards.jsonl.gz and
experiments/out/card-tags.json.gz (run invert_tags.py first). No R2 reads
or writes, nothing wired into trim_merge/CI.

Normalization recipe (unchanged from v1, locked):
  - Self-name -> "~", both full name and any face names, same trick as
    embed.py's normalize_self_references (word-boundary, case-sensitive,
    longest-candidate-first) -- applied PER FACE, since matching below is
    any-face for tiers 1/2.
  - Strip reminder text (parenthesized spans).
  - Lowercase, collapse whitespace, normalize curly quotes/apostrophes.
  - Ability split = oracle_text paragraph breaks ("\\n").

Tier ladder (frozen as of v2, TIER-ENGINE-V2-CHANGE-ORDER.md Amendment 1),
strictest first, one tier per pair:
  Step 1 -- base tier from text level:
    base 0: full normalized oracle text equal, KEYWORDS INCLUDED, composed
            across all faces (Amendment 2 bug fix -- v1 compared
            keyword-stripped, any-face text, which let a DFC's one matching
            face stand in for the whole card and let Suspend-style keyword
            lines silently drop out of "reprint" detection).
    base 1: >=1 whole normalized ability paragraph shared verbatim
            (keyword-only lines still excluded here, per v1 -- a bare
            shared "Flying" must never mint a Tier 1).
    base 2: shared verbatim token fragment, min length NGRAM_MIN_LEN,
            below the n-gram DF floor (Amendment 3 -- replaces v1's
            sentence-level clause equality, which couldn't see a shared
            sub-sentence fragment like Marisi's "your opponents can't
            cast spells" buried inside a longer clause).
  Step 2 -- Tier 0 frame gate: base 0 additionally requires mana_cost
            (raw, exact), type_line (normalized whitespace/case), power,
            and toughness (null==null) equal, per face. Any mismatch
            demotes base 0 -> base 1.
  Step 3 -- disjoint-type demotion: if the candidate's card-type set
            shares NO member with the anchor's (per-face union) -> demote
            one step, capped at Tier 2. Only demotion path -- MV/pip/P-T
            deltas are ranking facts, never tier movers.
  Tier 3: zero verbatim overlap (base is None), tag-overlap coverage >=
          threshold (unchanged: anchor-directional, idf weighted, 0.5
          inherited discount, 0.15 coverage threshold).
  Tier X: never machine-assigned.

Within-tier RANK (v2.1 introduced it, v2.2 added fact-distance penalties,
v2.5 added the first positive fact term (frame affinity); qualification
above is untouched throughout -- this only orders what's already in a tier
and decides what a capped report shows):
  Tier 1/2:  raw   = ngram_idf(fragment) * sqrt(len(fragment)/NGRAM_MIN_LEN)
                     + TAG_SCORE_WEIGHT * tag_overlap_score
             final = raw - CI_PENALTY*ci_relation_step - MV_PENALTY*abs(mv_delta)
                     - SCOPE_PENALTY*scope_mismatch - DURATION_PENALTY*duration_mismatch
                     - EXCEPTION_PENALTY*exception_mismatch - POLARITY_PENALTY*polarity_mismatch
                     - CONDITION_PENALTY*condition_mismatch + affinity_term
             where ngram_idf(f) = log(N_total_cards / DF(f)) via the same
             min-DF-chaining convention as Tier 2 evidence; tag_overlap_score
             is the Tier 3 coverage score computed for EVERY candidate
             regardless of which tier it qualified into; ci_relation_step
             maps same=0/subset=1/superset=2/overlapping=3/disjoint=4 (CI
             reads Commander-legality color identity, not mana-cost colors
             -- subset beats superset since fewer colors fits every deck
             the anchor fits); sqrt (not linear) length-dampening is a v2.1
             deviation from the original linear spec (see
             NGRAM_LENGTH_DAMPENING); affinity_term (v2.5) =
             TYPE_MATCH_BONUS (candidate type-bucket == anchor's, i.e.
             type_line_bucket_match == "same") + SUBTYPE_BONUS per shared
             creature subtype (post-dash type-line tokens, only counted
             when the face is itself a Creature), capped at
             SUBTYPE_BONUS_CAP -- the only positive term, ruled in because
             same-frame, same-family candidates were losing to rarer-
             fragment candidates purely on a DF coincidence, not on any
             real functional gap. Tie-break: fragment token length
             desc, |MV Delta| asc, name asc. Report rank column shows the
             full breakdown: "final (raw - ci_term - mv_term - scope_term -
             duration_term - exception_term - polarity_term -
             condition_term + affinity_term)".
  Tier 3:    unchanged (tag score desc, name asc) -- v2.2 explicitly does
             NOT fact-penalize Tier 3; it's a human-curation proposal
             queue and polluting its pure tag signal before Captain has
             authored against it would muddy the promote/demote workflow.
  Tier 0:    sorts by name (rarely non-empty; no rank needed).
  This buries generic template fragments ("combat damage to a player,")
  below thematically real matches without excluding them from the tier --
  qualification stays maximal, rank does the burying (explicitly rejected:
  tightening the floor further to exclude boilerplate).

Design decisions carried from v1/v2 (unchanged):
  - Keyword-only paragraph detection: prefix match, case-insensitive,
    against the card's own `keywords` array.
  - Tier 3 direct/inherited discount multiplies both sides; score is
    normalized coverage (matched weight / anchor's total tag weight).
  - idf baseline computed from the inverted (tagged-card) index.
  - n-gram DF pre-pass indexes only fixed-length NGRAM_MIN_LEN windows; a
    longer shared fragment's DF is approximated as the min DF among its
    constituent windows (a safe upper bound) -- marked "DF≈" vs exact "DF=".
"""
import argparse
import gzip
import json
import math
import random
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

CARDS_PATH = Path("data/raw/oracle-cards.jsonl.gz")
CARD_TAGS_PATH = Path("experiments/out/card-tags.json.gz")
# v2.5 MVΔ audit rider only -- read-only, verification-only use; the engine's
# actual scoring still reads cmc/mana_cost from CARDS_PATH exclusively.
CARDS_SQLITE_PATH = Path("data/artifacts/cards.sqlite")
CLAUSE_DF_PATH = Path("experiments/out/clause-df.json.gz")
NGRAM_DF_PATH = Path("experiments/out/ngram-df.json.gz")
REPORTS_DIR = Path("experiments/out/reports")
FULL_REPORTS_DIR = REPORTS_DIR / "full"

SELF_TOKEN = "~"

# Tunable constants (documented here per the handoff doc's "start permissive,
# tighten after eyeballing" instruction) -- override via CLI flags below.
# Process rule (TIER-ENGINE-V2.1-CHANGE-ORDER.md Amendment 3): any deviation
# from a change-order constant must be flagged here as a deviation, not
# silently substituted.
CLAUSE_DF_FLOOR = 1000          # kept as a fast pre-filter only (Amendment 3, v2); no longer the Tier 2 qualifier
NGRAM_MIN_LEN = 5               # Amendment 3 (v2), tunable
NGRAM_DF_FLOOR = 50  # spec said 1000 for sentence-clauses; ratified at 50 for n-grams, v2.1
# 5-token windows are a much higher-frequency regime than whole sentences
# (95% of all distinct 5-grams in the corpus have DF<=7; a floor of 1000
# excluded just 2 of 213,367). At 1000, Marisi's Tier 2 flooded with generic
# trigger-template debris ("combat damage to a player," DF=829, shared by
# hundreds of unrelated triggers). Recalibrated to 50 in the v2 session by
# eyeballing the corpus DF distribution; RATIFIED at 50 in v2.1 (Amendment 3)
# rather than reverted, since it's defensible (n-gram space is far sparser
# than sentence space) -- this line is the required flag for that deviation.
# Phase 3 (ratified, RULING-MANIFEST-2026-07-09.md R1/R2/R3) -- commonality
# bands, "confirmed against native-only distributions" per the Phase 1
# clean-data re-cut (experiments/measure/PHASE-1-CLEAN-RECUT-MEMO.md). Closes
# F1 (Tier 1 had no DF gate at all -- Boros Charm minted 221 false Tier 1
# rows off a bare "choose one --" header) and extends Tier 2's old flat
# NGRAM_DF_FLOOR=50 hard ceiling into a graduated band, admitting a "rescue
# zone" up to 172 (this is what readmits the Lane 1c six -- Growth Spiral,
# Garruk's Uprising, Cultivate, Rhystic Study, Rampant Growth, Deadly
# Dispute -- as qualified-but-buried instead of rejected outright).
#
# T1 and T2 get SEPARATE declared constants (Captain ruling) even though the
# long-paragraph/fragment values are numerically identical -- never share
# one constant, so a future divergence never requires touching both.
#
# R2: paragraphs of >=NGRAM_MIN_LEN tokens use ngram_scale_df (T2's existing
# min-window scale); paragraphs shorter than that use para_exact_df (exact
# corpus-wide count of that literal paragraph text) with their OWN
# thresholds -- ngram_scale_df is undefined below the window length, and
# Phase 1 found the four worst T1 offenders in the entire corpus are all
# short paragraphs it could never even see.
T1_LONG_FULL_WEIGHT_CEILING = 10
T1_LONG_DISCOUNT_CEILING = 50
T1_LONG_RESCUE_CEILING = 172        # DEAD (does not qualify at all) above this
T1_SHORT_FULL_WEIGHT_CEILING = 5
T1_SHORT_DISCOUNT_CEILING = 39      # DEAD above this -- no rescue zone for short paragraphs (R3)

T2_FULL_WEIGHT_CEILING = 10
T2_DISCOUNT_CEILING = 50            # matches the pre-Phase-3 NGRAM_DF_FLOOR value, continuity by design
T2_RESCUE_CEILING = 172             # replaces NGRAM_DF_FLOOR as T2's hard qualification ceiling

# DEAD is ratified qualification LAW (Captain: "kill them, for now") -- a
# SECOND lawful exception to "rank buries, never excludes," alongside the
# v2.6 amendment 1 corroboration gate. Every other band still qualifies;
# only the WEIGHT differs. The exact multiplier values below are NOT part
# of the Phase 1 DF-edge measurement (that pass only ratified the edges) --
# they are this phase's own numeric ruling, printed in report headers.
# Applied to the fragment_idf term only (never tag_score): full weight is
# unchanged; the discount band roughly halves standing; the rescue zone
# buries hard (still ranks, but never competitively) without excluding.
BAND_WEIGHTS = {"full": 1.0, "discounted": 0.5, "rescue": 0.15}

# SECONDARY CORROBORATION (Captain's ruling, 2026-07-11) -- a narrow,
# explicit carve-out from "a mechanism either wins the pair's ONE tier
# slot or is fully discarded," not a repeal of any qualification law:
# once a pair has ALREADY qualified Tier 1/2 on >=NGRAM_MIN_LEN words of
# genuinely distinguishing PRIMARY evidence (via any mechanism), any
# OTHER shared signal that mechanism cascade would otherwise silently
# throw away -- a second short clause below NGRAM_MIN_LEN (regardless of
# its own DF band: a rare bulleted "• draw a card" variant that would
# have qualified on its own if it hadn't been shadowed by a better match,
# and a genuinely-too-common bare "draw a card" that can NEVER
# independently qualify, are equally valid corroboration once real
# kinship is already established some other way), or a second shared
# keyword beyond the one keyword_kinship_match already used as the
# pair's primary evidence -- is surfaced as pure DISPLAY corroboration
# instead. Captain's own framing: "keywords on their own metric do not
# contribute [to rank]. but after enough similarity they do contribute"
# [to the DISPLAYED evidence, never the score]. Motivating case: Black
# Market Connections' "Draw a card." bullet and Zuko, Conflicted's own
# "Draw a card." bullet -- both already connect at Tier 2 via a rarer,
# more specific shared header (DF≈2), and "draw a card" should ALSO be
# visible once that more-specific match already carries the pair. See
# find_clause_corroboration() and assign_tier()'s own call site --
# corroboration entries are threaded through a SEPARATE field (never
# extra_fragments/compute_rank/kinship_keyword) specifically so they can
# never accidentally pick up frame-affinity restoration or any other
# rank credit the way a real extra_fragments/kinship-winner entry can.
CORROBORATION_MIN_OTHER_WORDS = NGRAM_MIN_LEN
CORROBORATION_MAX_SHOWN_PER_KIND = 3

# R1 -- both-sides-M2-injected provenance discount (Phase 3 numeric ruling).
# Fires "regardless of DF," so it OVERRIDES the band weight above rather
# than stacking with it -- a rare/low-DF both-sides-injected match (the
# Hero-of-Bladehold-class one-side-native overlap keeps full standing; only
# BOTH sides being reminder-injected triggers this) must not escape via the
# full-weight band. Deliberately harsher than the rescue-zone weight.
#
# LOWERED 0.05 -> 0.01 (found investigating Swiftfoot Boots equip-reminder
# clutter, 2026-07-10, Captain's ruling: "lower as far as it helps"). This
# constant was NEVER actually validated against G-B (check_gb_swiftfoot_
# boots_gate) until today -- a separate bug (SWIFTFOOT_EQUIP_TEXT's exact-
# equality comparison, fixed alongside this) made that gate's check trivially
# always-pass regardless of real state. CONFIRMED, not guessed: for a same-
# type match (e.g. Equipment vs Equipment), Phase 3's OWN frame-affinity
# restoration (restoration_fraction(), below) puts a HARD FLOOR under
# effective_weight = discount + (1-discount)*restored_fraction, independent
# of this constant -- measured directly (Cobbled Wings vs Swiftfoot Boots,
# restored_fraction=0.375): at discount=0.05, effective_weight=0.406; at
# discount=0.0 (the theoretical minimum), effective_weight=0.375. Lowering
# this constant below ~0.02 buys negligible further burial for TYPE-MATCHED
# pairs (the floor dominates) but still meaningfully helps DIFFERENT-type
# both-sides-injected matches, where restored_fraction=0 and this constant
# IS the whole effective_weight. 0.01 chosen as a real, measured improvement
# (not a token gesture) while acknowledging it cannot alone fully bury every
# same-type case -- see check_gb_swiftfoot_boots_gate()'s updated expected
# count, which reflects the residual floor rather than assuming a false 0.
PROVENANCE_DISCOUNT_WEIGHT = 0.01

# Second-class phrase bucket (Captain's ruling, 2026-07-10, stepping back
# from a same-session first draft that fully excluded the Equip-cost
# reminder from matchability -- "rather than completely exclude... don't
# remove, bucket-kneecap it hard enough where it assuredly appears near
# the bottom"). Ruling 6 ("qualification stays maximal, rank buries,
# never excludes") already governs everything else in this file; this
# extends it with a HOUSE-CURATED phrase list for evidence Captain judges
# to be real-but-uninteresting -- generic cost/rules mechanics or minor
# side-effect riders that shouldn't compete on equal footing with a
# genuinely distinguishing shared fragment, but that a human should still
# be able to find if they go looking (unlike the DEAD DF band, which
# excludes outright). A row whose ENTIRE winning evidence matches this
# list is a HARD categorical demotion -- see second_class_priority() in
# compute_anchor_full_tiers(), same guarantee-not-nudge shape as
# keyword_over_reminder_priority()/pt_exactness_priority(), sorted
# strictly below every non-second-class row in its tier regardless of
# score. Deliberately a short, explicit, house-curated list (like
# SCOPE_PATTERNS/EXCEPTION_PATTERNS/CONDITION_MARKERS above), not an
# automatically-derived one -- Captain decides what counts as
# "uninteresting," the engine doesn't infer it. Matched against the
# fragment as compute_rank() already sees it (CO-C period-stripped,
# lowercased) via .fullmatch(), so no anchors/trailing periods needed in
# the patterns themselves. Add more phrases here as Captain flags them --
# this file's own comment is the changelog, not a separate doc.
SECOND_CLASS_PHRASE_PATTERNS = (
    # Equip-cost mechanics boilerplate (the Swiftfoot Boots motivating
    # case) -- "{N}: attach to target creature you control equip only as
    # a sorcery", any equip cost. Real, shared, genuinely uninteresting.
    re.compile(r"\{[^}]+\}: attach to target creature you control equip only as a sorcery"),
    # "You lose N life" -- a minor rider clause (e.g. Anguished Unmaking's
    # second sentence) that's real evidence but shouldn't outrank a card's
    # actual defining ability. Reaches Tier 2 only via the short-sentence
    # path (Entry #9) -- 4 tokens, below NGRAM_MIN_LEN.
    re.compile(r"you lose \d+ life"),
)

# Reminder-KEYWORD second-class bucket (Captain's ruling, 2026-07-12,
# revised same day from an initial text-pattern draft): a keyword whose
# ENTIRE reminder body Captain judges to be generic Comprehensive-Rules
# boilerplate, not a genuine textual signal, gets its every reminder-
# sourced match demoted -- keyed on the KEYWORD NAME itself, not on
# hand-derived fragment text. This is deliberately NOT a text-pattern
# list like SECOND_CLASS_PHRASE_PATTERNS above: reminder text for a given
# keyword is fixed and known (it's engine-injected, see build_card_doc's
# v2.9 Mechanism 2), so "demote this keyword's reminder" is a one-line
# addition here, not a corpus-measurement exercise to find and quote the
# exact substring that happens to win against some particular anchor.
#
# Split Second motivating case: its reminder ("As long as this spell is
# on the stack, players can't cast spells or activate abilities that
# aren't mana abilities.") shares generic "can't cast spells or activate
# abilities" phrasing with Grand Abolisher's own, UNRELATED "during your
# turn" hatebear lock -- a coincidental wording overlap between two
# functionally distant mechanics (stack-timing vs turn-scoped), not a
# real signal.
#
# Checked ONLY when mechanism == "reminder" -- i.e. the row's own
# `reminder_keyword` field must equal one of these names (see assign_
# tier()'s `reminder_keyword_source`) -- which is a PROVENANCE check, not
# a text-pattern one, so it can never fire for a card's own NATIVE
# printed text. This is exactly the collision a first-draft text-pattern
# version of this same fix hit and had to correct: Sen Triplets and
# Myrel, Shield of Argive both independently produce the IDENTICAL
# fragment text ("can't cast spells or activate abilities") against
# Grand Abolisher via mechanism="text" (genuine, on-topic hatebear
# restrictions, not reminder boilerplate) -- text alone cannot tell those
# apart from Split Second's coincidence, only provenance can, and
# provenance is exactly what this bucket checks.
#
# Deliberately does NOT catch every mechanism="reminder" match
# categorically (Captain's own correction, same session): the Hero of
# Bladehold <-> Zurgo, Thunder's Decree match is ALSO mechanism=
# "reminder" (via Zurgo's own injected Mobilize reminder) but was
# explicitly ratified in an earlier session as a genuine, wanted overlap
# -- "a real verbatim overlap, not word-order-chasing." Only keywords
# named here are affected; Mobilize (and every other keyword) is
# unaffected unless explicitly added.
SECOND_CLASS_REMINDER_KEYWORDS = frozenset({
    "split second",
})


def is_second_class_phrase(text: str) -> bool:
    if not text:
        return False
    return any(p.fullmatch(text) for p in SECOND_CLASS_PHRASE_PATTERNS)


# First-class phrase bucket (Captain's ruling, 2026-07-11, REVISED same
# day -- first draft was a categorical "sort to the top" guarantee, the
# exact mirror of the second-class bucket's demotion; Captain corrected
# course: "rather than just surface all with the phrase to the top... just
# add more weight to the phrase, maybe just a bit more weight" -- a SCALAR
# rank bonus, not a categorical override). A HOUSE-CURATED phrase list for
# text Captain judges to be a real, deck-relevant SIGNAL worth a modest
# nudge, competing on the same rank scale as every other term instead of
# guaranteeing a position regardless of it. Matched via .search() against
# each side's FULL composed text (any ability, not just the one that won
# the pair's tier), NOT the fullmatch-against-winning-evidence convention
# second-class uses -- "power 2 or less" is typically a floating sub-
# clause embedded differently inside many different surrounding sentences
# card to card ("target creature with power 2 or less", "each creature
# with power 2 or less can't block", ...), so it essentially never becomes
# the literal winning fragment text under the existing n-gram/clause-exact
# matching (measured: 122 cards contain this phrase somewhere corpus-wide,
# rarely as a consistently-templated run) -- checking only already-won
# evidence would make this bucket a near-no-op for its own motivating
# case. Still never touches qualification (ruling 6): PROMOTED_PHRASE_
# BONUS is added as a positive term in compute_rank(), the same additive
# slot affinity_term already occupies -- a promoted-phrase match can move
# a row up or down WITHIN its tier by a modest, fixed amount, same as
# every other rank term, never guarantees a position. See
# promoted_phrase_shared() below and PROMOTED_PHRASE_BONUS's own use in
# compute_rank()/compute_candidate_rows(). Add more phrases here as
# Captain flags them -- this file's own comment is the changelog, not a
# separate doc.
PROMOTED_PHRASE_PATTERNS = (
    re.compile(r"power 2 or less"),
)
# First-pass default, not corpus-tuned, same "small, deliberately modest"
# framing as Captain's own "just a bit more weight" -- comparable to (in
# fact identical to) DURATION_PENALTY/2, roughly half a single mismatch
# penalty's worth of movement, open to recalibration like every other
# rank-term constant in this file.
PROMOTED_PHRASE_BONUS = 0.5


def promoted_phrase_shared(anchor_doc: dict, candidate_doc: dict) -> bool:
    """True if the SAME PROMOTED_PHRASE_PATTERNS entry appears anywhere in
    BOTH anchor's and candidate's full composed text -- deliberately NOT
    scoped to the pair's winning fragment (see PROMOTED_PHRASE_PATTERNS'
    own comment for why); "both sides genuinely care about this axis" is
    the bar, not "this is why they matched." Never called for qualification
    -- only as a rank-priority input for a pair that already qualified."""
    anchor_text = anchor_doc.get("composed_full_text") or ""
    candidate_text = candidate_doc.get("composed_full_text") or ""
    return any(p.search(anchor_text) and p.search(candidate_text) for p in PROMOTED_PHRASE_PATTERNS)


# Phase 4 (ratified, RULING-MANIFEST-2026-07-09.md R5/R6) -- mana-pip
# kinship cascade. R6: ANY two mana-producing abilities sharing >=1
# produced pip (or, for the pure-colorless family, ANY comparable
# production) qualify Tier 2 -- zero overlap falls through to T3 tags
# (Option B). Captain ruling widened this: mana-ability SHAPE
# (source_class + repeatable) is NOT a qualification gate -- "open the
# gate, allow other weights to surface the best matches" -- it is one of
# these RANK-ONLY cascade terms below, same as everything else here; none
# of them ever gate qualification.
#
# R5's original cascade order was "amount first, then type" (amount
# weighted heaviest, shape a lighter secondary tiebreaker). Captain's
# ruling, 2026-07-12, PARTIALLY reverses this: "the way it gives the mana
# is also important... Thran Dynamo should beat a card that gives {C}{C}
# if that card ISN'T an activated ability, even though Thran is one mana
# further off." See MANA_SHAPE_MISMATCH_PENALTY below -- now heavier than
# ONE unit of amount difference (so a same-shape match one mana off beats
# an exact-amount cross-shape match), but still lighter than TWO (so
# amount still dominates once the gap widens past that). Corpus-measured
# before shipping (Sol Ring's own colorless-family cascade): only 4 real
# cards sit in the "exact amount, mismatched shape" bucket this reorders
# below the far larger (491-card) "one mana off, same shape" bucket --
# Ashnod's Altar/Krark-Clan Ironworks (activated_other), Conduit of Storms
# (triggered_etb), Everythingamajig (activated_other) -- a contained,
# well-targeted change, not a wholesale reordering.
MANA_AMOUNT_PENALTY_WEIGHT = 0.3
# Shape (source_class/repeatable) mismatch -- R5's "type" axis. Captain's
# ruling, 2026-07-12 (see the block comment above): now deliberately
# LARGER than one unit of amount penalty (0.3) but smaller than two
# (0.6) -- delivery mechanism (activated tap vs ETB trigger vs upkeep
# trigger vs one-shot spell effect, etc.) now outweighs a one-mana amount
# gap, but amount still wins once the gap reaches two or more. Was 0.2
# (amount-dominant-always) before this ruling.
MANA_SHAPE_MISMATCH_PENALTY = 0.4
# EXTRA colors (candidate makes colors the anchor doesn't need) cost less
# than MISSING colors (candidate can't cover something the anchor makes) --
# R5: "entirely WRONG colors cost more than extra."
MANA_EXTRA_COLOR_PENALTY = 0.3
MANA_MISSING_COLOR_PENALTY = 0.6
# The candidate's OWN production breadth, applied only when the color set
# isn't an exact match (R5: "exact color set first, then widening (mono,
# then hybrid, then multi-pip)").
MANA_WIDENING_PENALTY = {"mono": 0.0, "hybrid": 0.2, "multi": 0.4}
# R5: "drawback/rider text NEVER blocks qualification, only rank."
MANA_RIDER_PENALTY = 0.15
# Mana kinship has no natural corpus-DF/idf analog the way keyword kinship
# does (keyword_df counts real named keywords; there's no equivalently
# cheap "how common is this shape" corpus dictionary here without a whole
# new global index). A flat baseline instead -- comparable in magnitude to
# a typical Tier 2 text-fragment idf term -- with the cascade penalty
# above as the sole rank differentiator among mana-kinship matches.
MANA_KINSHIP_BASE_RANK = 5.0

# Entry #4 (Captain's ruling, 2026-07-10) -- Equipment/Aura granted-keyword-
# SET kinship. Subject-phrase-anchored, deliberately scoped to what was
# actually corpus-measured (equip/enchant idiom only -- "creatures you
# control have..." anthem phrasing was discussed but never measured this
# session, left for a future pass rather than guessed at). Verb variants
# (has/have/gains, optional "gets ... and" stat-buff prefix) per the
# entry's own step 1 instruction.
GRANT_CLAUSE_RE = re.compile(
    r"^(?:equipped|enchanted) creature "
    r"(?:gets? ([+-]\d+/[+-]\d+)[^.]*? and )?"
    r"(?:has|have|gains) (.+?)\.?$"
)
# Captain's ruling, 2026-07-10: the P/T modifier ("gets +2/+2") sits right
# next to the granted-keyword clause this mechanism already parses and was
# previously discarded entirely (the whole "gets ... and" prefix was a
# non-capturing throwaway group) -- two equipment granting the SAME
# keyword but very different stat bonuses (Behemoth Sledge +2/+2 trample/
# lifelink vs a hypothetical +0/+0 trample/lifelink granter) aren't
# equally close kin. Captured as its own group now, fed into
# granted_keyword_kinship_match()'s cascade as an additional penalty term
# -- see GRANT_PT_MISMATCH_PENALTY_PER_POINT below.
PT_MODIFIER_RE = re.compile(r"^([+-]\d+)/([+-]\d+)$")
# Conditional grants (Champion's Helm's "as long as ... legendary", a
# per-creature-type set) are EXCLUDED from the fact entirely, not extracted
# and discounted -- the entry's own open question, resolved here: reusing
# the existing condition_penalty machinery would be a no-op for this
# mechanism (it fires off compute_fact_penalties/locate_fragment_context
# against a real paragraph substring, which this mechanism's synthetic
# fragment text never is, same as mana kinship) -- building a bespoke
# discount wasn't asked for and isn't cheap, so simple exclusion. In
# practice this marker rarely fires directly: Champion's Helm's actual
# phrasing ("As long as equipped creature is legendary, it has hexproof.")
# already fails GRANT_CLAUSE_RE's leading anchor, and Multiclass Baldric's
# per-creature-type "lifelink if you control a Cleric, ..." shape already
# fails the keyword-vocabulary exact-match check below -- both verified
# directly against real oracle text. Kept as an explicit, documented
# backstop for a differently-phrased conditional that might otherwise slip
# through.
CONDITIONAL_GRANT_MARKERS = ("as long as", "so long as", "for each")
# Design (measured corpus shape, POKE-PUNCH-LIST.md Entry #4): size 1-2
# granted-keyword sets (236 of 658+1295 Equipment/Aura cards) are precise
# enough for exact-set-overlap kinship to mean something; size >=3 is
# already covered by the existing `keyword-soup` Tagger tag (27 cards,
# live in Tier 3 today) -- no new mechanism needed there.
GRANT_SIZE_CEILING = 2
# Mirrors MANA_EXTRA_COLOR_PENALTY's shape -- a flat per-stray-keyword cost
# (keywords present on one side of the match but not the other), no
# missing/extra asymmetry the way mana amount has a natural "more/less"
# direction (a granted keyword set has no such directionality).
GRANT_KEYWORD_MISMATCH_PENALTY = 0.3
# Captain's ruling, 2026-07-10: P/T modifier mismatch, a secondary/refining
# cascade term alongside the keyword-mismatch penalty above -- a missing
# "gets X/Y" clause is treated as a definitive +0/+0 (the oracle text
# genuinely says nothing about a stat bonus, a KNOWN fact, not an unparsed
# uncertainty -- unlike e.g. duration's "unknown means don't penalize"
# convention). Flat per-point cost, no direction asymmetry (unlike mana's
# amount-heavier-penalized-than-lighter or MV's pricier-vs-cheaper split --
# a stat swing in either direction is an equally real difference here).
# First-pass default, same "comparable scale to the keyword-mismatch term,
# open to recalibration" reasoning as that constant -- not corpus-tuned.
GRANT_PT_MISMATCH_PENALTY_PER_POINT = 0.15
# Independent tuning knob from mana kinship's base rank, even though the
# initial value matches it -- same "flat baseline, no natural corpus-DF
# analog" reasoning as MANA_KINSHIP_BASE_RANK's own comment, deliberately
# NOT coupled to that constant so the two mechanisms can be recalibrated
# separately later.
GRANT_KINSHIP_BASE_RANK = 5.0

# Vanilla-creature frame-mismatch kinship (Captain's ruling, 2026-07-12):
# a blank creature IS its frame, so a blank Grizzly Bears IS to a blank
# Scaled Wurm what two IDENTICAL (empty) texts would be to each other --
# they still qualify as kin, just a weaker one once the frame itself
# differs (same shape as tier0_ok's own "text matches, frame doesn't"
# Tier 1 fallback a few lines above assign_tier's cascade). No natural
# corpus-DF analog either (there's no text at all to measure), so this is
# a third independent flat-baseline constant in the same lineage as
# MANA_KINSHIP_BASE_RANK/GRANT_KINSHIP_BASE_RANK above -- mv_delta/
# color-identity/type-affinity (already-generic rank terms, unconditional
# for every mechanism) are what actually separate a same-frame-cost sibling
# from a wildly-off one; this constant only sets the shared starting point
# they all get pulled up/down from.
VANILLA_CREATURE_BASE_RANK = 5.0

# Equip-cost delta term (Fable 5's recommendation, EQUIPMENT-REMINDER-AND-
# WEIGHTING-DELIBERATION.md Section 4a/Q1, 2026-07-10, ratified): Entry #4's
# granted_keyword_kinship_match() had no signal at all for Equip-activation-
# cost closeness -- two Equipment granting the identical keyword set (e.g.
# both "haste, +0/+0") for a {1} Equip cost and a {5} Equip cost scored
# equally close kin. Only the card's own CASTING cost (mv_delta, a
# completely different number) entered the shared rank formula. Rejected
# alternative (a type-gated kill-switch disabling reminder-text Tier 2
# qualification for Equipment): the residual boilerplate rows in Swiftfoot
# Boots' own Tier 2 list are honest, defensible weak matches with nothing
# better available (verified: Ring of Xathrid/Cobbled Wings/Ring of Evos
# Isle share no real keyword grant with Boots at all) -- "rank buries,
# never excludes" is working as intended there; this is a targeted
# additive fix for the actual gap, not a broad mechanism change.
EQUIP_COST_RE = re.compile(r"\bEquip(?:\s+[A-Za-z]+)?\s+((?:\{[^}]+\})+)(?=[\s.(]|$)")
# Flat per-point cost, same shape as GRANT_PT_MISMATCH_PENALTY_PER_POINT --
# an equip-cost swing in either direction is an equally real difference,
# no missing/extra asymmetry the way mana amount has one. First-pass
# default, not corpus-tuned, open to recalibration like every other
# GRANT_*_PENALTY constant in this block.
GRANT_EQUIP_COST_PENALTY_PER_POINT = 0.15

# Granted-keyword-set kinship, GENERALIZED to a second subject phrase
# (Captain's ruling, 2026-07-12) -- this session shipped a standalone
# "team_pump" mechanism for mass-pump effects (Craterhoof Behemoth <->
# End-Raze Forerunners), structurally a near-duplicate of Entry #4's own
# mechanism above with its own parallel cascade/constants. Captain reversed
# course: "remove the team pump mechanism and figure out a way to do it
# within the system naturally... conceptually I don't even like it [as a
# separate mechanism]." Entry #4's OWN comment had already anticipated
# exactly this: "'creatures you control have...' anthem phrasing was
# discussed but never measured this session, left for a future pass" --
# this IS that pass, folded into the SAME mechanism rather than a sibling
# one. extract_granted_keyword_clause() now recognizes TWO subject
# templates: "equipped/enchanted creature" (unchanged regex/logic, GRANT_
# CLAUSE_RE below, ALWAYS produces scope="single", duration_eot=False --
# so two Equipment/Aura facts matching against each other pay zero cost on
# either of the two new terms below, preserving the exact pre-existing
# rank formula for every already-gated Equipment case) and "[other]
# creatures you control get(s)/gain(s)/has/have ..." (the constants
# immediately below, both clause orders, optional "until end of turn"
# duration and variable "+X/+X, where X is <clause>" magnitude). One fact
# shape, one cascade, one pool-seeding index -- a mass-pump match is now a
# real granted_keyword_kinship_match() result, which means it automatically
# inherits everything Entry #4 already earned for Equipment: the Option C
# boilerplate-shadowing rescue, the categorical "exact P/T beats near"
# sort priority, and build_granted_keyword_index()'s pool seeding (closing
# a real gap the standalone team_pump mechanism never got: 16 Furnace-
# Oriflamme-anchored pairs were invisible to gather_candidate_pool()
# before this unification, found only by luck via unrelated tags).
# Corpus-measured (2026-07-11, unchanged by the unification): 426 distinct
# cards carry the mass-pump idiom in either verb order; requiring >=1
# shared granted keyword (GRANT_SIZE_CEILING, reused directly -- same
# "3+-keyword grants are keyword-soup, already Tagger-covered" reasoning)
# connects 60 cards to Craterhoof alone.
#
# Two axes Equipment/Aura never needed (a static "has X" grant has no
# "other" vs "all" scope choice and no duration axis -- always ongoing):
# scope ("other creatures you control" vs "creatures you control" vs the
# Equipment-only "single") and duration ("until end of turn" vs
# permanent). Flat mismatch terms, rank-only per ruling 6 -- Craterhoof
# (scope=all) vs End-Raze (scope=other) pays this once and still qualifies
# comfortably. Reused GRANT_KEYWORD_MISMATCH_PENALTY/GRANT_PT_MISMATCH_
# PENALTY_PER_POINT directly for the keyword/PT terms (one rate, not a
# parallel bespoke one per mechanism) -- only the two genuinely NEW axes
# get their own constants.
GRANT_SCOPE_MISMATCH_PENALTY = 0.2
GRANT_DURATION_MISMATCH_PENALTY = 0.2
# Magnitude comparison has THREE shapes, not two: literal-vs-literal (a
# real point distance, uses GRANT_PT_MISMATCH_PENALTY_PER_POINT directly,
# unchanged from Entry #4), variable-vs-variable (Craterhoof-class
# "+X/+X, where X is <clause>" -- same clause text is essentially the same
# effect (treated as an exact 0-point match), different clause text is
# still "scales with board state" kinship, a LIGHTER point-equivalent than
# a real numeric gap), and literal-vs-variable (genuinely not comparable --
# a flat point-equivalent distinct from both, since treating an unbounded
# X as "very far" from a fixed number would be guessing at a distance that
# doesn't exist). Both expressed in the SAME "points" unit
# GRANT_PT_MISMATCH_PENALTY_PER_POINT already scales, not a separate rate.
GRANT_VARIABLE_MISMATCH_POINTS = 1.0
GRANT_MIXED_PT_MISMATCH_POINTS = 2.0

# A bulleted modal-choice line ("• Other creatures you control get...") or
# a planeswalker loyalty-cost line ("+1: Creatures you control get...")
# puts real characters before the subject phrase that GRANT_MASS_SUBJECT_
# RE's own left-boundary anchor (start of string, or right after ", "/
# ". ") does not cover -- stripped first so the subject search always
# starts clean.
GRANT_MASS_LEADING_JUNK_RE = re.compile(r"^(?:•\s*|[+\-−]?\d+:\s*)+")
# Subject-phrase anchor for the mass-pump idiom: matches at the very start
# of the (already junk-stripped) paragraph, or right after a clause
# boundary (", "/". ") so a trigger-clause prefix like "when this creature
# enters, " doesn't block the match -- re.search, not re.match, since the
# subject phrase is rarely the first word. Deliberately narrow to exactly
# "[other] creatures you control" (the two forms Craterhoof/End-Raze
# actually use, both corpus-measured above) -- broader subject phrasing
# ("creatures you control and planeswalkers you control", "each creature
# you control") left unhandled rather than guessed at. The equipped/
# enchanted-creature subject (GRANT_CLAUSE_RE) is tried FIRST and is
# unaffected by any of this -- see extract_granted_keyword_clause().
GRANT_MASS_SUBJECT_RE = re.compile(r"(?:^|(?<=, )|(?<=\. ))(other )?creatures you control (.+)$")
# Two verb orders, both real (Craterhoof: keyword-then-PT; End-Raze:
# PT-then-keyword) -- tried in sequence rather than one combined regex,
# same "small, explicit, sequential pattern attempts" style as
# where_x_is_param()/is_keyword_only_paragraph() elsewhere in this file.
# The PT group accepts digits OR a single x/y variable letter (either
# case) so both "+2/+2" and "+x/+x" reach the same capture; parse_pt_
# modifier()/the variable-shape check below do the actual classification.
GRANT_MASS_PT_FIRST_RE = re.compile(
    r"^gets? ([+\-]?[xXyY0-9]+/[+\-]?[xXyY0-9]+) and (?:has|have|gains?|gain) (.+)$"
)
GRANT_MASS_KW_FIRST_RE = re.compile(
    r"^(?:has|have|gains?|gain) (.+?) and gets? ([+\-]?[xXyY0-9]+/[+\-]?[xXyY0-9]+)$"
)
GRANT_MASS_PT_ONLY_RE = re.compile(r"^gets? ([+\-]?[xXyY0-9]+/[+\-]?[xXyY0-9]+)$")
GRANT_MASS_KW_ONLY_RE = re.compile(r"^(?:has|have|gains?|gain) (.+)$")
GRANT_MASS_VARIABLE_PT_RE = re.compile(r"^[+-]?[xy]/[+-]?[xy]$")
GRANT_MASS_WHERE_RE = re.compile(r",\s*where [a-zA-Z] is (.+)$")

INHERITED_TAG_DISCOUNT = 0.5
TIER3_COVERAGE_THRESHOLD = 0.15
TAG_SCORE_WEIGHT = 3.0          # Amendment 1 (v2.1), tunable -- starting value per the change order
REPORT_CAP = 10                 # Amendment 3 (v2.2): down from 40 -- matches the intended site UI default

# Amendment 1 (v2.2) -- fact-distance penalties, applied only to Tier 1/2
# rank (Tier 3 stays tag-only, a human-curation proposal queue). These are
# the first genuinely SOFT constants in the engine and are EXPECTED to move
# after Captain eyeballs the effect across all six anchors -- do not tune
# them further within this session; print the breakdowns and let Captain rule.
CI_PENALTY = 0.6                # per ci_relation_step (0-4), unchanged since v2.2
MV_PENALTY = 0.5                # v2.3 ruling 7: was 0.25 in v2.2 -- MV closeness carries decent weight,
                                 # this was Captain's original objection to Avatar's Wrath pre-carve-out
# Locked ruling (Captain, v2.2/v2.3): subset beats superset -- a candidate
# with FEWER colors fits every deck the anchor fits; a superset demands
# colors the deck may lack. v2.3 ruling 3: splashability is a virtue, not a
# defect -- subset drops from a full step (1) to a half step (0.5) so an
# exact CI match still edges a splashable one, but subset candidates stop
# bleeding rank for having fewer colors.
#
# SUPERSEDED (Captain ruling, Phase 3 rebalance, RULING-MANIFEST-2026-07-09.md):
# MV distance is no longer symmetric. Same MV is still the strongest
# (MVΔ=0 -> zero penalty, unchanged); the penalty still decays with |MVΔ|
# (distance dominant); but a CHEAPER candidate (MVΔ<0) decays slower --
# i.e. is penalized LESS per unit of distance -- than a PRICIER one
# (MVΔ>0), reflecting that a strictly cheaper functional match is a
# stronger recommendation than a pricier one at the same distance. This is
# a tiebreaker on TOP of distance, not a strict cheaper-always-above-pricier
# bucket sort (a hard bucket would bury a known-good pricier neighbor --
# e.g. End-Raze Forerunners under a Craterhoof anchor -- below EVERY
# cheaper candidate regardless of similarity). Realized as a multiplier on
# the SAME mv_penalty*abs(mv_delta) product -- one term, not two, so mana
# value is never counted twice. Cost asymmetry only: produced-mana amounts
# (Phase 4's mana-fact system) remain symmetric, an unrelated axis.
MV_PRICIER_MULT = 2.5           # RATIFIED (Captain, Phase 3 rebalance): first sweep point tested
                                 # against the live engine, passed cleanly -- applied when a candidate
                                 # costs MORE than the anchor (mv_delta > 0). Spot-checked against the
                                 # "cliff" failure mode: at this multiplier a distance-1 pricier
                                 # candidate penalizes the same as a distance-2.5 cheaper one (still
                                 # distance-dominant, not a bucket sort) -- verified via Grand
                                 # Abolisher's own Tier 2 (Failure // Comply, MVΔ=+1, ranks #6/54, not
                                 # buried). Craterhoof Behemoth / End-Raze Forerunners (the named spot-
                                 # check pair) share zero text -- see CO-D evidence, RULING-MANIFEST-
                                 # 2026-07-09.md, for the scrambled-clause finding that surfaced.
MV_CHEAPER_MULT = 1.0           # applied when a candidate costs LESS than the anchor (mv_delta < 0) --
                                 # unchanged from the old symmetric formula this round.
CI_RELATION_STEP = {"same": 0, "subset": 0.5, "superset": 2, "overlapping": 3, "disjoint": 4}

# v2.5 amendment 2 (Captain's ruling, session): graded superset CI. The flat
# superset step of 2 undercharged WIDE supersets -- Sen Triplets (Grand
# Abolisher's mono-W -> WUB, +2 colors beyond the anchor's CI) was ranking
# above its true functional distance from a mono-color anchor, only
# resurfacing into the displayed Tier 2 top-10 because the new (correct,
# untouched) SUBTYPE_BONUS shared-"Human" fact gave it +0.25. Ruling: fix
# the CI axis, not the subtype bonus, and not MV_PENALTY. same/subset/
# overlapping/disjoint stay FLAT (untouched, per "do not touch"); only
# "superset" is graded:
#   superset_step = min(1 + colors_added, SUPERSET_STEP_CAP)
# where colors_added = size of (candidate CI - anchor CI). A +1-color
# superset (e.g. Kutzil, mono-W -> WU) stays at step 2 -- the OLD flat
# value, so single-splash candidates are unaffected; this widens the TOP of
# the superset range, not a general re-tuning. Explicitly the cheap
# intermediate step toward the backlogged per-color pip-vector comparator
# (THESAURUS-TIER-PROTOTYPE-HANDOFF.md deferred/backlog list) -- a real
# graded comparator remains future work, this is not it.
SUPERSET_STEP_CAP = 4  # matches the disjoint ceiling; also the pre-existing CI_RELATION_STEP max


def graded_superset_step(colors_added: int) -> int:
    return min(1 + colors_added, SUPERSET_STEP_CAP)


def ci_relation_step_value(anchor_ci: set, candidate_ci: set, relation: str) -> tuple:
    """Returns (step, colors_added). colors_added is None except for
    "superset" (the only graded relation, v2.5 amendment 2); all other
    relations read the flat CI_RELATION_STEP table unchanged."""
    if relation != "superset":
        return CI_RELATION_STEP.get(relation, 0), None
    colors_added = len(candidate_ci - anchor_ci)
    return graded_superset_step(colors_added), colors_added


# v2.3 Amendments 1-3 -- new per-ability/per-face facts and their penalties.
# All are absolute, rule: provenance facts (detecting is fact; weighing which
# ones matter belongs to Captain's Tier X authoring -- the penalties below
# are deliberately flat, not judgment-weighted).
SCOPE_PENALTY = 2.0      # single vs all-opponents is the largest functional gap in Commander
DURATION_PENALTY = 1.0   # one-shot spell window vs a permanent's standing effect
EXCEPTION_PENALTY = 1.0  # partial lock (carve-out) vs total lock, "sizable" per ruling 6
POLARITY_PENALTY = 2.0   # v2.4 Amendment 1 -- functional inversion (same grammar, opposite
                         # effect) is at least as bad as wrong target, hence same magnitude as scope
CONDITION_PENALTY = 1.5  # v2.4 Amendment 2 -- "big penalty" per ruling 1 (condition-narrowed
                         # restriction masquerading as broad text)

# v2.5 change order -- frame-affinity bonus, the first genuinely POSITIVE
# fact term. Ruling: Drannith Magistrate must beat Avatar's Wrath in Grand
# Abolisher's Tier 2 -- same MV, same type bucket, shared subtype(s),
# permanent vs Wrath's one-shot sorcery -- Wrath's prior edge came purely
# from a rarer matched fragment (DF≈4 vs DF=29) whose extra token "turn,"
# is a phrase-boundary coincidence, not a real functional difference.
# Constants match the change order exactly (no deviation to flag).
TYPE_MATCH_BONUS = 0.3     # candidate's type bucket == anchor's ("same", per type_line_bucket_match)
SUBTYPE_BONUS = 0.25       # per shared creature subtype (post-dash type-line token)
SUBTYPE_BONUS_CAP = 0.5    # SUBTYPE_BONUS accumulates up to this, then caps

# v2.9 change order -- two new Tier-ASSIGNMENT qualification paths, run in
# PARALLEL with the original verbatim-text path (Amendment 1, v2, FROZEN
# until now). Both reuse the EXISTING ngram_df-floor discipline -- no new
# floor constant, per the change order's own "the same DF floor logic that
# governs fragments" instruction.
#
# MECHANISM 1 -- keyword kinship: a shared keyword (Scryfall keywords array
# + a parsed param from its own oracle-text line, e.g. "Mobilize 2" ->
# keyword=mobilize, param="2") qualifies as a pseudo-fragment IF its corpus
# DF clears the SAME floor as text fragments (args.ngram_df_floor) --
# evergreens (flying, trample, haste...) have DF in the thousands and never
# qualify, by construction, not by a separate check. Same param -> Tier 1
# (an identical compressed ability line); different param -> Tier 2. This
# is a PARALLEL qualification path, not a repeal of the keyword-only-
# paragraph exclusion for VERBATIM text matching (Tiers 0-2 still never
# mint a match from a bare shared "Flying" via TEXT comparison).
#
# MECHANISM 2 -- reminder-text injection: for a SINGLE-keyword line that
# carries reminder text in the raw oracle text, the reminder body
# (extracted, not stripped) becomes an ordinary matchable paragraph on
# BOTH sides, attributed to that keyword -- this DOES supersede the
# keyword-only exclusion, but only for that specific line (bare keywords
# with no reminder, and multi-keyword comma lines, stay excluded exactly
# as before -- the latter a documented simplification, see
# KNOWN_LIMITATIONS). The injected paragraph flows through the EXISTING
# find_shared_paragraph/find_shared_fragment machinery and EXISTING
# ngram_df indexing unchanged -- "runs through the existing DF discipline"
# is satisfied by construction (no separate reminder-DF table).
#
# NO-DOUBLE-COUNT: for a given (anchor, candidate) pair, any keyword that
# qualifies via Mechanism 1 has its Mechanism-2 reminder paragraph EXCLUDED
# from that pair's text search (keyword identity wins) -- see
# assign_tier()'s exclude_paragraphs construction.
#
# HONEST EXPECTATION (the change order's own words): this catches
# identical-templating longhand cards only. Cards with the same effect in
# different words/color/type (Hero-of-Bladehold-class) are out of verbatim
# reach by design -- their absence from Tier 1/2 is a PASS, not a gap to
# chase by widening normalization. Keyword kinship reuses NGRAM_DF_FLOOR
# directly -- no separate floor constant.

# Amendment 1 -- effect scope, extracted from normalized ability text (the
# SPECIFIC paragraph containing the matched fragment, not the whole card --
# per-ability is mandatory: Myrel's hate line is all_opp, her token line is
# self). Checked in this order; first match wins. "unknown" never penalizes.
SCOPE_PATTERNS = [
    ("all_opp", (r"\byour opponents\b", r"\beach opponent\b", r"\ball opponents\b")),
    ("single", (r"\btarget opponent\b", r"\ban opponent\b", r"\bchosen player\b", r"\btarget player\b")),
    ("symmetric", (
        r"\beach player\b", r"\ball players\b", r"\beveryone\b",
        # v2.4 Amendment 3 (bug fix, not a new fact): bare-plural-subject
        # patterns -- "Players can't cast spells during combat." (Basandra)
        # was falling through to all_opp-equivalent (no symmetric pattern
        # matched, so it scored a 0.00 scope penalty against Marisi's
        # all_opp instead of the correct symmetric mismatch).
        r"\bplayers can't\b", r"\bplayers don't\b", r"\bplayers skip\b",
    )),
]

# Amendment 3 -- exception/carve-out marker vocabulary (closed, per the change order).
EXCEPTION_PATTERNS = (r"\bother than\b", r"\bexcept\b", r"\bunless\b")

# v2.4 Amendment 1 -- polarity (prohibition marker), detected on the specific
# SENTENCE containing the matched fragment, not the whole ability paragraph
# (a paragraph can mix a mana ability with a "spend this mana only..."
# restriction sentence that has no bearing on the matched clause's polarity).
POLARITY_MARKERS = ("can't", "cannot")

# v2.4 Amendment 2 -- condition-narrowing marker vocabulary (closed, tight,
# `~`-anchored per the change order, to avoid eating category modifiers like
# "of artifacts, creatures, or enchantments"). Checked on the matched ability
# paragraph (same granularity as scope/duration/exception).
CONDITION_MARKERS = ("with the same name", "named", "the chosen")

# v2.3 Amendment 5 gate + calibration truths (Grand Abolisher's Tier 2).
VOICE_OF_VICTORY = "Voice of Victory"
SEN_TRIPLETS = "Sen Triplets"
VOV_PLACEMENT_STOP_POSITION = 3   # position > this (1-indexed) = gate failure
VOV_PLACEMENT_EXPECTED_POSITION = 2  # informational target, not a hard requirement
PARTIAL_LOCK_CARDS = {"Avatar's Wrath", "Drannith Magistrate"}
TOTAL_LOCK_SAME_CI_MV_FLOOR = 1  # partial-lock cards must rank below every total-lock, same-CI, |MVΔ|<=this row
# v2.2 baseline positions (Grand Abolisher Tier 2, before v2.3's scope/duration/
# exception terms and the MV_PENALTY/CI-step changes) -- reference points for
# the v2.3 movement gate (Amendment 5's "movement checks").
V22_BASELINE_ABOLISHER_POSITIONS = {
    "Silence": 9, "Mandate of Peace": 6, "Conqueror's Flail": 8, "Failure // Comply": 5,
}

# v2.4 gate 4 named these four anchors (Captain approved with NO notes in the
# v2.3 eyeball session) as the ones whose displayed top-10s had to stay
# stable. SUPERSEDED by the v2.5 session amendment: stability is no longer
# blocking for ANY anchor, so check_stability_gate is now called over the
# full ANCHOR_PANEL (all six) as an informational diff, not just these four.

# FORMULA DEVIATION from TIER-ENGINE-V2.1-CHANGE-ORDER.md Amendment 1, ratified
# by Captain, flagged per Amendment 3's process rule ("any deviation from a
# change-order constant/formula must be flagged, not silently substituted"):
#
#   Spec (Amendment 1):  rank = ngram_idf(f) * (len(f) / NGRAM_MIN_LEN) + TAG_SCORE_WEIGHT * tag_score
#   Ratified (v2.1+):     rank = ngram_idf(f) * sqrt(len(f) / NGRAM_MIN_LEN) + TAG_SCORE_WEIGHT * tag_score
#
# Reason: raising the display cap (25->40) and switching to rank-sorted order
# surfaced 23 previously-invisible candidates sharing an 8-token generic
# trigger-template fragment with Myrel ("creature tokens, where x is the
# number of", DF~47/idf~6.70). Under the LINEAR term this fragment
# out-ranked Myrel's actual token description ("1/1 colorless soldier
# artifact creature", 5 tokens, DF=12, idf~8.07) -- length compensated for
# lower rarity, burying the specific match under the generic one. Tested
# TAG_SCORE_WEIGHT at 3/5/8/10/15/20: none fixed it, because the boilerplate
# candidates are themselves legitimate token-producers that share Myrel's
# token tags, so the tag term rises for both sides together. The formula's
# LENGTH term was the actual lever, not the tag weight -- rarity must
# dominate, length only nudges. sqrt() keeps the reward for genuinely
# long+rare fragments (Darksteel Splicer's 9-token DF=3 match still tops
# the list) while much more sharply discounting long-but-common ones.
NGRAM_LENGTH_DAMPENING = "sqrt"  # was linear (len/NGRAM_MIN_LEN) per Amendment 1; see note above

ANCHOR_PANEL = [
    "Grand Abolisher",
    "Myrel, Shield of Argive",
    "Preordain",
    "Sol Ring",
    "Marisi, Breaker of the Coil",
    "Sakura-Tribe Elder",
]

# Amendment 4.1 (v2.1) -- symmetry gate pairs: every anchor-vs-anchor pair in
# the panel where both cards are themselves anchors.
SYMMETRY_PAIRS = [
    ("Grand Abolisher", "Myrel, Shield of Argive"),
    ("Grand Abolisher", "Marisi, Breaker of the Coil"),
    ("Myrel, Shield of Argive", "Marisi, Breaker of the Coil"),
]

# Amendment 1 Step 3 -- disjoint-type demotion reads this set (per-face union).
MAJOR_TYPES = {
    "Artifact", "Battle", "Conspiracy", "Creature", "Dungeon", "Enchantment",
    "Instant", "Kindred", "Tribal", "Land", "Phenomenon", "Plane",
    "Planeswalker", "Scheme", "Sorcery", "Vanguard",
}

WS_RE = re.compile(r"\s+")
CURLY_QUOTES = {"’": "'", "‘": "'", "“": '"', "”": '"'}


def strip_sentence_final_token_period(token: str) -> str:
    """CO-C (Phase 2a, ratified): applied per-token, after whitespace split.
    A token ending in a literal period is pure sentence-final punctuation
    (Magic oracle text has no abbreviations or decimals that would make an
    internal period ambiguous) -- strip exactly one trailing period,
    wherever the sentence ends within the paragraph, not only at the
    paragraph's own final token. A paragraph-final-only version was tried
    first and regressed Start the TARDIS vs Preordain: its multi-sentence
    paragraph ("...draw a card. You may planeswalk.") has "card." at a
    mid-paragraph sentence boundary, which stayed period-glued while
    Preordain's own paragraph-final "card." got stripped -- a NEW mismatch
    neither side had before. Per-token stripping treats every sentence
    ending the same way, closing that gap. Never touches apostrophes or
    symbol tokens ({t}: is colon-terminated, never affected). Fixes the
    Arcane Signet/Manalith clause-truncation bug (Batch-1 Lane 1a): a bare
    mid-sentence word (e.g. 'color') never matched the period-glued
    sentence-final twin ('color.') on the other side."""
    if token.endswith(".") and len(token) > 1:
        return token[:-1]
    return token


def sentence_boundary_indices(paragraph_text: str) -> frozenset:
    """Sentence-boundary trim rule (Fable 5's recommendation, EQUIPMENT-
    REMINDER-AND-WEIGHTING-DELIBERATION.md, 2026-07-10): 0-based token
    indices i (into `paragraph_text.split()`, the SAME raw split
    `paragraph_tokens` is built from before CO-C's per-token period strip)
    where the raw token at i ends with a literal sentence-final period --
    i.e. a sentence ends immediately after token i. Same "no abbreviations,
    no ambiguous internal periods" assumption strip_sentence_final_token_period
    already relies on. Used by find_shared_fragments() to detect when a
    matched run spans two of a paragraph's own sentences by coincidence
    (see that function's docstring) rather than reflecting one fluent
    clause."""
    return frozenset(
        i for i, tok in enumerate(paragraph_text.split())
        if tok.endswith(".") and len(tok) > 1
    )


KNOWN_LIMITATIONS = [
    "Keyword-only detection is prefix-match against the card's own keywords "
    "array; generic keyword names that don't literally prefix their "
    "templated text (e.g. 'Landwalk' vs. 'Swampwalk') are not recognized "
    "and fall through to normal clause/paragraph matching.",
    "n-gram DF is indexed only at the minimum window length; a shared "
    "fragment longer than that window has its DF approximated as the "
    "minimum DF among its constituent windows (a safe upper bound, not "
    "an exact count) -- marked 'DF≈' in evidence when this applies. The "
    "same convention is reused for Tier 1's rank-score idf, since a whole "
    "shared ability paragraph is usually longer than the indexed window.",
    "Duration (v2.3 Amendment 2) is decided purely by face type: Instant/"
    "Sorcery = one_shot, any permanent-type face = ongoing. \"Until end of "
    "turn\" effects on permanent faces still count as ongoing by this rule -- "
    "a known v1 simplification, flagged here rather than refined, per the "
    "change order's instruction to only refine it if the eyeball trips on a "
    "real case.",
    "DEFERRED (v2.6 amendment 2): rule:turn-scoped is not fed into Tier 2's "
    "tag_score rank term this round, blocked pending a Drannith/Wrath impact "
    "analysis (Wrath's own turn-window phrasing is duration-shaped and "
    "excluded by this fact's own definition, but the restriction to Tier 3 "
    "was ruled as a precaution regardless, not re-litigated here).",
    "DEFERRED (v2.6 amendment 2): additional rule:-provenance fact-tags as a "
    "general mechanism -- rule:turn-scoped is the pilot for this pattern "
    "(an engine-derived, corpus-scanned tag injected into Tier 3 scoring "
    "without touching the Tagger index); no second instance has been built "
    "yet.",
    "DEFERRED (post-v2.6 ruling): a format-legality filter -- carry Scryfall "
    "legalities per row now or at the next convenient touch (fact-based, "
    "rule: clean); a UI-side format toggle is the eventual consumer. Kills "
    "Alchemy (A-) cards from Commander-mode results.",
    "DEFERRED (post-v2.6 ruling): an LLM-assisted corpus tag pass "
    "(\"stax_coded\"-class judgments) is feasible post-prototype, but "
    "REQUIRES a new provenance namespace (llm: or assist:) -- never rule:, "
    "never manual: -- plus a spot-check sampling protocol before any "
    "scoring use.",
    "DEFERRED (post-v2.6 ruling): a Tagger data-gap check for Defense Grid "
    "-- does a tax/stax-adjacent tag exist (or belong) on Defense Grid "
    "and/or Grand Abolisher in oracle-tags? A five-minute grep, "
    "non-blocking, informational only, not yet run.",
    "DEFERRED (post-v2.6 ruling): Tier 3 plateau resolution -- Grand "
    "Abolisher's Tier 3 has a 21-way tie at score~0.24 (a "
    "\"hate-enchantment\"/\"hate-artifact\" cluster) that Defense Grid sits "
    "just behind. Known resolution limit of the current anchor-directional "
    "coverage formula; revisit only if a curation pass makes it painful.",
    "v2.9 Mechanism 2 (reminder-text injection) only attributes a reminder "
    "to its keyword for SINGLE-keyword oracle-text lines. Multi-keyword "
    "comma lines (e.g. \"flying, trample\") are not split for per-keyword "
    "reminder attribution -- a documented simplification, not engineered "
    "around, since true multi-keyword-with-reminder same-line templating "
    "is rare (evergreens sharing a line typically carry no reminder text "
    "at all on modern cards).",
    "DEFERRED (post-v2.9 ruling, Split Second finding): a rule:stack-window "
    "duration fact (\"while on the stack\"-class restrictions, e.g. Split "
    "Second, as their own duration category distinct from one_shot/"
    "ongoing) is NOT built. Rejected on principle for now -- no keyword-"
    "level good/bad curation, since that would insert subjective judgment "
    "into qualification; the existing scope/duration penalties already "
    "bury these correctly (verified: all 24 Split-Second-driven rows in "
    "Grand Abolisher's Tier 2 land below the displayed top 10). Build only "
    "if a future eyeball trip shows reminder-injected rows actually "
    "cracking a displayed top 10.",
    "v2.9 Mechanism 2's shared corpus-wide ngram_df index means an "
    "injected reminder paragraph can shift the DF (and therefore rank) of "
    "an UNRELATED pre-existing text fragment anywhere in the corpus, "
    "whenever they happen to share a common rules-text phrase -- even for "
    "anchors/candidates with no keywords involved at all (verified: "
    "Absorb Vis/Infernal Rebirth's basic-landcycling reminder shifted a "
    "Sakura-Tribe Elder ramp-fetcher fragment's DF by +1, swapping two "
    "adjacent Tier 2 rows). This is accepted as a structural property of "
    "sharing one DF index, not a defect -- reminder text is real rules "
    "text printed on real cards, so it legitimately counts toward corpus-"
    "wide phrase rarity. A separate DF table for injected paragraphs was "
    "considered and REJECTED: forking the index would make \"how rare is "
    "this wording\" depend on which mechanism asked, which is incoherent. "
    "The stability gate traces (not assumes) any such drift to a named "
    "culprit card -- see trace_df_drift().",
    "FIXED (v2.9 erratum 2, was OPEN after erratum 1): "
    "is_keyword_only_paragraph() now also accepts \"<Keyword> <param>, "
    "where <param> is <clause>.\" lines (where_x_is_param()), validated "
    "against the card's own keywords array with the SAME literal param "
    "token required on both sides -- not a general \"contains where...is\" "
    "heuristic (deliberately narrow: an unrelated em-dash ability-word "
    "construction like \"Domain -- Look at the top X cards..., where X "
    "is...\" does NOT match, since the param-bearing fragment isn't "
    "immediately after the keyword name). PRECISELY re-verified corpus-"
    "wide (old-classifier=False, new-classifier=True): 14 cards, not the "
    "147 originally estimated by a loose substring scan (that scan's "
    "'where'/'is' check false-matched things like \"anywhere\" containing "
    "\"where\", and over-counted em-dash ability-word templates that don't "
    "share this construction). Known minor over-sweep, not further "
    "engineered per the narrow-fix discipline: when a where-clause is "
    "followed by ADDITIONAL comma- or period-joined content in the SAME "
    "paragraph (e.g. Graven Lore's \"...spent to cast this spell, then "
    "draw three cards.\", Sunbringer's Touch's trailing \"Each creature "
    "you control...gains trample...\" sentence), that trailing content is "
    "swept into the keyword-only classification too, since paragraphs are "
    "matched as atomic units and this fix doesn't sub-parse sentence "
    "boundaries within the where-clause. Affects a small minority of the "
    "14; verified to trip no blocking gate. RATIFIED AS-IS (Captain's "
    "ruling, post-erratum-2): the COST is that an affected card loses "
    "Tier 1/2 TEXT-MATCH RECALL on any rules sentence following the "
    "where-clause in the same paragraph -- that trailing sentence can no "
    "longer independently qualify a verbatim Tier 1/2 match against "
    "another card sharing ONLY that sentence, since it's bundled into the "
    "excluded keyword-only paragraph rather than left as its own "
    "matchable text. DEFERRED (backlog, build only if a real eyeball trip "
    "shows an actual missed match on one of these 14 cards): a sentence-"
    "boundary sub-parse of keyword-only paragraphs, splitting a "
    "\"<Keyword> <param>, where <param> is <clause>. <trailing sentence>\" "
    "line into a keyword-only part and a separately-matchable trailing "
    "part, instead of treating the whole paragraph as one atomic unit.",
]

# v2 self-check calibration truth. Any mismatch here means the rules don't
# reproduce Captain's ruled v1 eyeball verdicts; reports must not be written
# until this passes. Tier assignment is frozen, so these must still pass
# unchanged in v2.1 (TIER-ENGINE-V2.1-CHANGE-ORDER.md Amendment 4 preamble).
SELF_CHECK_PAIRS = [
    ("Sol Ring", "Kozilek's Channeler", 2),
    ("Sol Ring", "Ur-Golem's Eye", 1),
    ("Sol Ring", "Sisay's Ring", 1),
    ("Sol Ring", "Palladium Myr", 1),
    ("Grand Abolisher", "Myrel, Shield of Argive", 1),
    ("Marisi, Breaker of the Coil", "Megatron, Tyrant // Megatron, Destructive Force", 1),
    # RULED (Captain): Instant/Sorcery no longer count as disjoint for the
    # tier-assignment demotion (types_disjoint_for_demotion()) -- this exact
    # pair was the standing "flagged for Captain's ruling" open question
    # since v2.3 ("a possible future carve-out... not implemented, pending
    # Captain's ruling"). Byte-identical text, Sorcery vs Instant -- was 2,
    # now 1. Tier 0 still correctly excluded (frame_signature requires
    # matching type_line, which Instant vs Sorcery always fails).
    ("Preordain", "Deliberate", 1),
]
# No fixed expected tier -- the v2 change order asks to print the rules'
# verdict with evidence, not assert one.
SELF_CHECK_INFO_ONLY = [
    ("Sol Ring", "Sol Talisman"),
    ("Sol Ring", "Ulvenwald Captive // Ulvenwald Abomination"),
]

# Amendment 4.3 (v2.1) -- boilerplate burial gate targets.
#
# GATE FIX (ratified by Captain, post-v2.1 eyeball; see BURIAL_GATE_TAG_EXEMPT_THRESHOLD
# below for the second half): "boilerplate cluster" membership is decided by
# FRAGMENT IDENTITY (exact string equality with the phrase below), not
# substring containment. The original substring test flagged Darksteel
# Splicer / Wickersmith's Tools as "boilerplate" merely because their real
# evidence -- a distinct, much rarer 9-token fragment ("artifact creature
# tokens, where x is the number of", DF~3) -- happens to CONTAIN this
# 8-token phrase as a substring. Their actual match is legitimate and rare;
# they were never boilerplate. Ruling: the engine's output was correct: the
# gate's classifier was wrong. MYREL_WORSE_FRAGMENT is the exact phrase
# shared verbatim (fragment == this string) by the real generic-template
# cluster (Krenko/Aang and Katara/Horn of Gondor/etc.) -- longer than the
# 6-token phrase TIER-ENGINE-V2.1-CHANGE-ORDER.md illustrated, because the
# real longest-common-run for this cluster runs 8 tokens, not 6.
ABOLISHER_BURIAL_TARGETS = {"Sen Triplets", "Avatar's Wrath", "Drannith Magistrate", "A-Teferi, Time Raveler"}
ABOLISHER_BOILERPLATE_FRAGMENT = "spells or activate abilities of"
MYREL_BETTER_FRAGMENT = "1/1 colorless soldier artifact creature"
MYREL_WORSE_FRAGMENT = "creature tokens, where x is the number of"

# GATE FIX, part 2 (ratified by Captain): a row whose fragment matches the
# boilerplate phrase exactly is still NOT counted as burial-worthy junk if
# its weighted tag-score contribution (TAG_SCORE_WEIGHT * tag_score) is
# already >= this threshold -- i.e. its rank is legitimately tag-driven,
# not an artifact of the generic fragment. Real numbers (Myrel, tag_score_
# weight=3.0): The Unbeatable Squirrel Girl (weighted=0.77), Horn of Gondor
# (0.59), Aang and Katara (0.59), Krenko Mob Boss (0.58), Marrow-Gnawer
# (0.58) all clear this bar and are exempted; Cloudspire Coordinator (0.36)
# and everything below it don't, and remain the actual burial target.
# Rationale (Captain): "a boilerplate-fragment candidate that also carries
# strong shared tags is not junk, and the gate should not punish the tag
# system for working."
BURIAL_GATE_TAG_EXEMPT_THRESHOLD = 0.5

# Amendment (v2.2) -- mono-color proximity gate target (Grand Abolisher).
# Voice of Victory (mono-white, same CI as Abolisher) must rank above every
# superset-CI candidate with |MV Delta| >= 2, EXCEPT ones whose raw
# fragment score already exceeds Voice of Victory's raw score by more than
# that candidate's own actual total penalty -- those are legitimately
# closer on text and the gate must not punish rarity for them (per the
# change order: if Sen Triplets survives above Voice of Victory at the
# starting constants, that is NOT a gate failure).
ABOLISHER_PROXIMITY_TARGET = "Voice of Victory"
ABOLISHER_PROXIMITY_MV_FLOOR = 2

# Amendment (v2.2) -- sanity ordering gate target (Sol Ring): same-CI,
# small-|MV-Delta| mana rocks that must all rank ahead of any high-|MV
# Delta| row in Sol Ring's Tier 1.
SOL_RING_SANITY_TRIO = ["Mana Crypt", "Sol Talisman", "Worn Powerstone"]


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_cards(path: Path) -> dict:
    if not path.exists():
        halt(f"{path} not found — run pipeline/fetch.py or rclone copy the snapshot first")
    cards = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"{path} line {line_no}: JSON parse failure: {e}")
            if "oracle_id" not in card or not card["oracle_id"]:
                halt(f"{path} line {line_no}: missing oracle_id")
            cards[card["oracle_id"]] = card
    return cards


def load_card_tags(path: Path) -> dict:
    if not path.exists():
        halt(f"{path} not found — run experiments/invert_tags.py first")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Normalization (unchanged from v2)
# ---------------------------------------------------------------------------

def self_name_candidates(name: str) -> set:
    candidates = {name}
    if " // " in name:
        for face_name in name.split(" // "):
            face_name = face_name.strip()
            if face_name:
                candidates.add(face_name)
    return candidates


def normalize_self_references(text: str, candidates: set, keywords: list = None) -> str:
    """N2 (2026-07-16, TIER-ENGINE-V3-PROPOSAL.md): when the card's own name
    equals one of its keyword-action names (Regenerate, Suspect, Mill,
    Manifest...), a blanket substitution eats the keyword verb itself --
    the card Regenerate's "Regenerate target creature." became "~ target
    creature.", unmatchable against every other card's genuine "regenerate
    target creature." text (N1's own fix). Skip substitution for a specific
    occurrence only when it's BOTH (a) one of the card's own keywords and
    (b) in verb position -- sentence-initial, immediately followed by
    "target" -- the same corpus-verified signal N1 uses to tell a keyword
    ACTION sentence apart from a bare keyword-name mention. Narrow by
    construction: a self-name mention used as a noun/subject elsewhere in
    the text (e.g. "Whenever ~ deals combat damage...") is untouched by
    this carve-out and still substitutes normally."""
    lowered_keywords = {k.lower() for k in (keywords or ())}
    for candidate in sorted(candidates, key=len, reverse=True):
        pattern = r"\b" + re.escape(candidate) + r"\b"
        is_keyword_action_name = candidate.lower() in lowered_keywords

        def _sub(m, _text=text, _is_action=is_keyword_action_name):
            if _is_action:
                start = m.start()
                sentence_initial = start == 0 or bool(re.search(r"[.\n]\s*$", _text[:start]))
                if sentence_initial and re.match(r"target\b", _text[m.end():].lstrip()):
                    return m.group(0)
            return SELF_TOKEN

        text = re.sub(pattern, _sub, text)
    return text


def find_paren_spans(text: str) -> list:
    """v2.9 ERRATUM (root-caused, not a v2.9 regression -- see strip_reminder/
    extract_reminder_spans): balanced-parenthesis scanner, a depth counter,
    replacing the old REMINDER_RE = re.compile(r"\\([^)]*\\)") flat regex.
    A flat regex CANNOT express nesting -- it was silently corrupting any
    card whose reminder text itself contains a parenthetical (verified:
    exactly one card in the 38,233-card corpus, Devoted Mardu: "...create X
    tapped and attacking Mardudes (tapped and attacking 1/1 red Warrior
    creature tokens). Sacrifice them..."). REMINDER_RE would match from the
    OUTER "(" through the FIRST ")" it found -- the INNER close -- leaving a
    dangling ")" and truncated reminder body. This walks the string
    tracking depth and returns each OUTERMOST span's (start, end) indices
    (end exclusive), nested parens kept intact inside the span, never
    split. Unbalanced trailing/leading parens are ignored (best-effort,
    same silent-skip the old regex exhibited for malformed text -- not
    observed in the corpus)."""
    spans = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    spans.append((start, i + 1))
                    start = None
    return spans


def strip_reminder(text: str) -> str:
    spans = find_paren_spans(text)
    if not spans:
        return text
    parts = []
    last = 0
    for start, end in spans:
        parts.append(text[last:start])
        last = end
    parts.append(text[last:])
    return "".join(parts)


def normalize_clause_text(text: str) -> str:
    text = strip_reminder(text)
    for curly, straight in CURLY_QUOTES.items():
        text = text.replace(curly, straight)
    text = text.lower()
    text = WS_RE.sub(" ", text).strip()
    return text


def normalize_type_line_for_frame(type_line: str) -> str:
    return WS_RE.sub(" ", (type_line or "").strip().lower())


def split_clauses(paragraph: str) -> list:
    """Sentence-level split within a normalized paragraph. Originally kept
    only to feed clause-df.json.gz (a fast candidate-pool pre-filter); now
    ALSO the direct source for find_shared_sentence()'s short-clause Tier 2
    path and find_clause_corroboration()'s secondary-evidence scan.

    BUG FIX (Fable 5's engine-wide audit, 2026-07-12 -- New Finding N1): a
    naive split on "." breaks INSIDE quoted granted-ability text (e.g.
    `...has "{t}: add {g}."` -- the period before the closing quote ends
    the split, leaving a trailing "clause" of just a bare `"` character).
    1,264 cards corpus-wide carry that exact artifact (plus a handful of
    other punctuation-only splits -- stray `]`/`*`/checkbox glyphs).
    Every OTHER consumer was accidentally protected from this (DF for a
    punctuation-only "clause" is in the hundreds-to-thousands, past every
    existing qualification ceiling), but find_clause_corroboration() has
    no DF ceiling at all (deliberately, see its own docstring), so a bare
    `"` was surfacing as live "also seen" evidence in shipped reports
    (e.g. Zurgo, Thunder's Decree's Tier 2 list). Filtering here, not just
    at the corroboration call site, fixes it for every current and future
    consumer of this function at once -- a punctuation-only fragment was
    never a legitimate matchable unit for ANYONE, not a corroboration-
    specific concern."""
    return [c.strip() for c in paragraph.split(".") if c.strip() and re.search(r"[a-z0-9]", c)]


def where_x_is_param(normalized_paragraph: str, keywords: list):
    """v2.9 erratum 2: recognizes the closed pattern "<Keyword> <param>,
    where <param> is <clause>." -- the where-clause CLARIFIES the keyword's
    own variable, so it's part of the keyword line, not ordinary rules
    text. <Keyword> is validated against the card's own Scryfall keywords
    array (same prefix-match discipline as the base check -- never
    freetext keyword guessing); <param> must be the literal SAME token in
    both places (e.g. both "x"), so an unrelated "where Y is..." elsewhere
    in a longer, differently-templated line (ability-word em-dash
    constructions like "Domain — ...") does NOT match -- deliberately
    narrow, per the change order's exact pattern, not a general "contains
    where...is" heuristic. Returns the matched keyword's lowercased name
    if the pattern fires, else None."""
    fragments = [f.strip() for f in normalized_paragraph.split(",") if f.strip()]
    if len(fragments) < 2:
        return None
    first = fragments[0]
    matched_kw = None
    for kw in sorted({k.lower() for k in keywords}, key=len, reverse=True):
        if first.startswith(kw + " "):
            matched_kw = kw
            break
    if matched_kw is None:
        return None
    param = first[len(matched_kw):].strip()
    if not param:
        return None  # bare keyword, no variable -- not this pattern
    param_token = param.split()[0]
    rest = ", ".join(fragments[1:]).strip()
    if re.match(r"^where\s+" + re.escape(param_token) + r"\s+is\b", rest):
        return matched_kw
    return None


def is_keyword_only_paragraph(normalized_paragraph: str, keywords: list) -> bool:
    """Prefix match: every comma-separated fragment must start with one of the
    card's own keywords (case-insensitive) -- OR (v2.9 erratum 2) the whole
    line is a "<Keyword> <param>, where <param> is <clause>." construction
    (where_x_is_param). See KNOWN_LIMITATIONS for what's still unhandled.

    BUG FIX (found auditing Entry #4, 2026-07-10): the prefix check must be
    WORD-BOUNDARY safe (frag == kw or frag.startswith(kw + " ")), not a raw
    substring prefix -- `parse_keyword_instances()` already gets this right
    (same convention, same docstring's "prefix-match" language) but this
    sibling function didn't, and the gap was silent because it only ever
    ADDED false qualifications rather than crashing. Confirmed directly:
    Swiftfoot Boots's own keyword is "Equip"; a raw `frag.startswith("equip")`
    check matches "equipped creature has hexproof and haste." (its OWN
    grant-clause paragraph, unrelated to the "Equip {1}" cost line) because
    "equipped" starts with "equip" as a bare substring -- wrongly excluding
    the ENTIRE grant clause from matchable_paragraphs, before Mechanism 1,
    ordinary text matching, OR Entry #4's new granted-keyword mechanism
    could ever see it. This is exactly why Entry #4's own motivating case
    (Swiftfoot Boots vs Lightning Greaves) surfaced the bug: both grant
    clauses are single-fragment (no comma, "X and Y" only), so both were
    silently eaten; a comma-bearing multi-keyword grant (Helm of Kaldra:
    "first strike, trample, and haste") accidentally survived because not
    every comma-fragment starts with "equip". Purely corrective -- can only
    ever ADD paragraphs back into matchable_paragraphs that a real keyword
    ability never actually claimed, never remove one a genuine keyword line
    legitimately excluded.

    BUG FIX (Fable 5's engine-wide audit, 2026-07-12 -- Finding 2, the
    "em dash" sub-class): the SAME word-boundary-safe prefix check above
    still wrongly qualifies a multi-word ABILITY WORD introducing its own
    unique effect sentence via em dash -- "domain — enchanted creature
    gets +1/+1 for each basic land type among lands you control." starts
    with "domain " (the em dash satisfies the trailing-space boundary),
    so the ENTIRE effect sentence was being excluded from matchable_
    paragraphs, not just the label. Corpus-measured before shipping: 474
    fragments across 471 cards (Threshold, Delirium, Domain, Morbid,
    Boast, Celebration, Converge, and dozens of Universes Beyond flavor
    words too common to be caught by strip_bespoke_ability_label()'s own
    DF floor). A genuine keyword-only fragment (bare "Flying", "Mobilize
    2", "Ward {2}", "Protection from white") NEVER has an em dash
    immediately after the keyword name by construction -- an em dash
    specifically marks "ability word introducing unique printed text,"
    which is definitionally not a bare keyword+param line -- so this
    exclusion cannot remove a legitimate classification, only correct a
    wrong one. A SECOND sub-class Fable 5 found (action-verb keyword
    names -- Suspect, Mill, Regenerate, Manifest -- coinciding with their
    OWN ability's first word, e.g. "suspect up to one target creature.")
    is a REAL but NOT cleanly fixable gap: re-measured directly before
    deciding not to touch it here -- of 793 fragments whose remainder
    looks superficially similar, the overwhelming majority (protection
    from X: 208, enchant TYPE: 164, affinity for X: 77, splice: 32,
    kicker COST: 19, hexproof from X: 9, and more) are genuinely
    legitimate multi-word keyword params, not sentence leakage -- no
    structural signal (word count, trailing period, comma count) cleanly
    separates the ~15-20 real verb-collision bugs from the ~770 correct
    classifications in that set. Left as a documented, deferred
    limitation rather than a hand-curated keyword exception list (which
    this file avoids elsewhere for exactly this kind of ambiguity) --
    revisit only with a real per-keyword grammatical signal, not a guess."""
    if not normalized_paragraph or not keywords:
        return False
    lowered_keywords = [k.lower() for k in keywords]
    fragments = [frag.strip() for frag in normalized_paragraph.split(",") if frag.strip()]
    if not fragments:
        return False

    def _fragment_matches_bare_keyword(frag: str, kw: str) -> bool:
        if frag == kw:
            return True
        if not frag.startswith(kw + " "):
            return False
        rest = frag[len(kw):].lstrip()
        # An em dash right after the keyword name means this is an
        # ability-word idiom introducing its own unique sentence, not a
        # bare "<keyword> <param>" line -- see this function's own
        # docstring (Fable 5's audit, Finding 2).
        if rest.startswith("—"):
            return False
        # N1 (2026-07-16, TIER-ENGINE-V3-PROPOSAL.md): a keyword-name-
        # leading fragment continuing with a literal "target" is a keyword
        # ACTION used as a verb with an object (Regenerate target
        # creature., Suspect target creature., Goad/Detain/Heist/Double
        # target ...), not a bare "<keyword> <param>" ability line -- no
        # legitimate keyword-ability parameter is ever spelled "target"
        # (params are costs/types/qualities: Enchant creature, Ward {2},
        # Protection from white, Kicker {1}{U}), so this is corpus-safe: a
        # full corpus scan found 48 such fragments across 7 keywords
        # (goad, regenerate, double, detain, heist, suspect, airbend),
        # every one a genuine action sentence, zero false positives.
        # Corrective only, like the em-dash check above: can only keep a
        # paragraph that a real keyword-only line never actually claimed.
        return re.match(r"target\b", rest) is None

    if all(
        any(_fragment_matches_bare_keyword(frag, kw) for kw in lowered_keywords)
        for frag in fragments
    ):
        return True
    return where_x_is_param(normalized_paragraph, keywords) is not None


def strip_bespoke_ability_label(normalized_paragraph: str, keywords: list, keyword_df: dict,
                                 floor: int) -> str:
    """Strips a leading "<Label> — " prefix from an otherwise-ordinary
    (non-keyword-only) paragraph when <Label> is BOTH (a) literally one of
    the card's own Scryfall `keywords` array entries (never freetext/regex
    guessing -- same discipline as parse_keyword_instances/
    is_keyword_only_paragraph) and (b) rare enough corpus-wide to clear the
    SAME floor Mechanism 1 already uses to decide a keyword is meaningful
    kinship signal rather than evergreen noise (keyword_df, floor=
    NGRAM_DF_FLOOR). This is the "Black Market Connections" case: modal
    choice bullets like "Sell Contraband — Create a Treasure token. You
    lose 1 life." carry a real, Scryfall-registered ability-word label
    (DF=1, unique to this one card) glued onto the effect text with no
    separating period -- the label survives into split_clauses()'s output
    as part of the FIRST clause ("sell contraband — create a treasure
    token"), which can never equal a differently-labeled or unlabeled
    card's matching clause (e.g. Zuko, Conflicted's bare "Draw a card."
    bullet, glued as "buy information — draw a card" on Black Market
    Connections' side before this fix). Stripping the label lets the
    underlying effect text stand on its own for BOTH ordinary fragment
    matching and the short-whole-sentence Tier 2 path.

    Corpus-measured (2026-07-11) before shipping: ~440 distinct labels
    match the "own keyword, immediately followed by em dash, at paragraph
    start" shape corpus-wide (Universes Beyond sets overwhelmingly --
    Final Fantasy, Fallout, Doctor Who, Marvel, Warhammer 40K -- each
    label almost always DF=1..2, unique per card). Real, reused evergreen/
    mechanic ability words (Landfall DF=180, Domain DF=65, Threshold
    DF=102, Delirium DF=74) sit far above the floor and are deliberately
    LEFT UNSTRIPPED -- their label is genuine shared vocabulary, already
    served by Mechanism 1 independent of this text-normalization step,
    and stripping it would only reduce text-match specificity for no
    corresponding gain. Only fires at the very START of a paragraph
    (after an optional bullet marker) -- a mid-sentence em dash elsewhere
    (e.g. the modal header's own trailing "choose one or more —") is
    never touched, since it isn't followed here by a card-owned keyword
    name at all.
    """
    if not normalized_paragraph or not keywords:
        return normalized_paragraph
    bullet = ""
    rest = normalized_paragraph
    if rest.startswith("•"):
        bullet = "•"
        rest = rest[1:].lstrip()
    marker = " — "
    idx = rest.find(marker)
    if idx == -1:
        return normalized_paragraph
    label = rest[:idx].strip()
    if not label:
        return normalized_paragraph
    lowered_keywords = {k.lower() for k in keywords}
    if label not in lowered_keywords:
        return normalized_paragraph
    if keyword_df.get(label, 0) > floor:
        return normalized_paragraph
    remainder = rest[idx + len(marker):]
    return f"{bullet} {remainder}" if bullet else remainder


def extract_reminder_spans(text: str) -> list:
    """v2.9 Mechanism 2: parenthesized spans with the outer parens stripped
    (nested parens inside kept intact) -- the complementary extraction to
    strip_reminder() (which discards this same text). Uses the same
    balanced-paren scanner (find_paren_spans) as strip_reminder, so the two
    can never disagree about where a reminder span starts/ends."""
    return [text[start + 1:end - 1] for start, end in find_paren_spans(text)]


def normalize_reminder_body(text: str) -> str:
    """v2.9 Mechanism 2: normalizes an EXTRACTED reminder span for use as an
    injected matchable paragraph -- the same curly-quote/lowercase/
    whitespace steps as normalize_clause_text, but does NOT re-strip
    reminder text (there's nothing left to strip; this text IS the
    reminder body)."""
    for curly, straight in CURLY_QUOTES.items():
        text = text.replace(curly, straight)
    text = text.lower()
    text = WS_RE.sub(" ", text).strip()
    return text


def parse_keyword_instances(normalized_paragraph: str, keywords: list) -> list:
    """v2.9 Mechanism 1: for a normalized (reminder-stripped) paragraph,
    returns [{"keyword": lowered_name, "param": str|None}, ...] for every
    comma-separated fragment that matches one of the card's own keywords --
    the SAME prefix-match convention as is_keyword_only_paragraph (the two
    must never disagree about what counts as a keyword fragment). param is
    whatever follows the keyword name on that fragment (trailing period
    stripped); None for a bare keyword (e.g. "flying"). Keywords are tried
    longest-name-first so a short keyword name can't wrongly prefix-match
    inside a longer one's fragment."""
    if not normalized_paragraph or not keywords:
        return []
    lowered_keywords = sorted({k.lower() for k in keywords}, key=len, reverse=True)
    instances = []
    for frag in normalized_paragraph.split(","):
        frag = frag.strip().rstrip(".").strip()
        if not frag:
            continue
        for kw in lowered_keywords:
            if frag == kw:
                instances.append({"keyword": kw, "param": None})
                break
            if frag.startswith(kw + " "):
                param = frag[len(kw):].strip()
                instances.append({"keyword": kw, "param": param or None})
                break
    return instances


# ---------------------------------------------------------------------------
# Phase 4 (ratified, RULING-MANIFEST-2026-07-09.md R5/R6) -- mana-fact
# extraction. Parallel to v2.9 Mechanism 1 (keyword kinship): a NEW
# qualification path, never a replacement for literal text matching (R4).
# ---------------------------------------------------------------------------

MANA_COLOR_LETTERS = frozenset("wubrg")  # lowercase -- matchable_paragraphs are lowercased (normalize_clause_text)
MANA_NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
MANA_ADD_RE = re.compile(r"\badd\b(.*?)(?:\.|$)")
MANA_SYMBOL_RE = re.compile(r"\{([^}]+)\}")


def parse_mana_fact(paragraph: str):
    """R5 -- extracts one mana-producing ability's facts from a single
    (already-normalized, lowercase) matchable_paragraph, or None if no
    recognizable "add ... mana" clause is present. A card with multiple
    mana-producing lines gets one fact per line (caller iterates).

    Facts: colors (frozenset of lowercase WUBRG letters -- a SET, order
    never matters, R5), colorless_amount, amount (total mana this ability
    produces per activation -- a comma/or-separated symbol list is a
    CHOICE, amount=1, not sum(symbols); a concatenated run like "{c}{c}" is
    cumulative, amount=len(symbols) -- these are genuinely different
    shapes and conflating them would misstate amount entirely), any_color
    (bool), ci_restricted (any_color AND explicitly scoped to "commander's
    color identity" -- a rider, never blocks qualification per R5, only
    affects rank), is_hybrid (a single {w/u}-style symbol carries BOTH
    colors as ONE pip, R5's hybrid equivalence), mixed (both colored and
    colorless production in the SAME ability), source_class/repeatable
    (how the ability fires -- the R6 "shape" candidates must share to
    qualify), widening ("mono"|"hybrid"|"multi" -- the ability's OWN
    production breadth, used only for cascade rank, never qualification).

    KNOWN LIMITATION (documented, not engineered around): variable-amount
    abilities ("add X mana, where X is...") are not parsed -- amount
    defaults from the any-color word list only ("one"/"two"/...); an
    unrecognized/absent number defaults to 1. This under-covers a real but
    rare corpus slice; halting loudly would block Phase 4 entirely for a
    handful of variable-mana cards, so it is logged here instead."""
    m = MANA_ADD_RE.search(paragraph)
    if not m:
        return None
    clause = m.group(1)

    any_color = "any color" in clause
    ci_restricted = any_color and "commander" in clause and "color identity" in clause
    is_choice = bool(re.search(r"\bor\b", clause)) or ("," in clause and not any_color)

    colors = set()
    colorless_amount = 0
    colored_pip_count = 0
    is_hybrid = False

    if any_color:
        colors = set(MANA_COLOR_LETTERS)
        amount = 1
        for word, n in MANA_NUMBER_WORDS.items():
            if re.search(rf"\b{word}\b", clause):
                amount = n
                break
    else:
        symbols = MANA_SYMBOL_RE.findall(clause)
        for sym in symbols:
            if sym == "c":
                colorless_amount += 1
            elif sym in MANA_COLOR_LETTERS:
                colors.add(sym)
                colored_pip_count += 1
            elif "/" in sym:
                parts = [p for p in sym.split("/") if p in MANA_COLOR_LETTERS]
                if parts:
                    colors.update(parts)
                    colored_pip_count += 1
                    is_hybrid = True
        if colored_pip_count == 0 and colorless_amount == 0:
            return None  # "add" found but nothing recognizable followed -- not parseable, not a mana ability we track
        amount = 1 if is_choice else (colored_pip_count + colorless_amount)

    prefix = paragraph[:m.start()]
    if "{t}" in prefix:
        source_class, repeatable = "activated_tap", True
    elif re.match(r"^\s*(at the beginning of)", paragraph):
        source_class, repeatable = "triggered_recurring", True
    elif re.match(r"^\s*(when|whenever)\b", paragraph):
        source_class, repeatable = "triggered_etb", False
    elif ":" in prefix:
        source_class, repeatable = "activated_other", True
    else:
        source_class, repeatable = "spell_effect", False

    if any_color or (is_choice and len(colors) > 1):
        widening = "multi"
    elif is_hybrid:
        widening = "hybrid"
    else:
        widening = "mono"

    # R5 "drawback/rider text NEVER blocks qualification, only rank" -- a
    # coarse, general (non-card-specific) detector for common restriction
    # phrasing anywhere in the ability, used only as a cascade rank
    # tiebreaker below, never for qualification.
    has_rider = bool(re.search(r"\b(only|unless|where|that a|to cast)\b", paragraph))

    return {
        "colors": frozenset(colors),
        "colorless_amount": colorless_amount,
        "colored_pip_count": colored_pip_count,
        "amount": amount,
        "any_color": any_color,
        "ci_restricted": ci_restricted,
        "is_hybrid": is_hybrid,
        "mixed": colored_pip_count > 0 and colorless_amount > 0,
        "has_rider": has_rider,
        "source_class": source_class,
        "repeatable": repeatable,
        "widening": widening,
        "raw": paragraph,
    }


def get_raw_faces(card: dict) -> list:
    """List of per-face dicts (name, oracle_text, mana_cost, type_line, power,
    toughness) -- real per-face split, never joined."""
    faces = card.get("card_faces")
    if faces:
        return [
            {
                "name": f.get("name") or card["name"],
                "oracle_text": f.get("oracle_text") or "",
                "mana_cost": f.get("mana_cost"),
                "type_line": f.get("type_line") or "",
                "power": f.get("power"),
                "toughness": f.get("toughness"),
            }
            for f in faces
        ]
    return [{
        "name": card["name"],
        "oracle_text": card.get("oracle_text") or "",
        "mana_cost": card.get("mana_cost"),
        "type_line": card.get("type_line") or "",
        "power": card.get("power"),
        "toughness": card.get("toughness"),
    }]


def build_card_doc(card: dict, enable_v29_mechanisms: bool = True, keyword_df: dict = None,
                    keyword_label_df_floor: int = NGRAM_DF_FLOOR) -> dict:
    """enable_v29_mechanisms=False reproduces the EXACT pre-v2.9 doc shape
    (no keyword_instances, no reminder injection) -- used ONLY to rebuild a
    "legacy" ngram index for the stability gate's DF-drift tracing
    (trace_df_drift()), never for actual scoring. `keyword_df` (2026-07-11,
    strip_bespoke_ability_label()) is None in that same legacy-reproduction
    call, which also disables the strip (it postdates v2.9, same gating
    convention as every other enable_v29_mechanisms-gated step below)."""
    candidates = self_name_candidates(card["name"])
    keywords = card.get("keywords") or []

    faces = []
    keyword_instances = []  # v2.9 Mechanism 1 -- flat across faces, card-level for kinship
    for raw_face in get_raw_faces(card):
        substituted = normalize_self_references(raw_face["oracle_text"], candidates, keywords)
        raw_paragraphs = [p for p in substituted.split("\n") if p.strip()]

        all_paragraphs = []        # keyword lines INCLUDED -- Tier 0 only
        matchable_paragraphs = []  # keyword-only lines EXCLUDED, unless reminder-injected (v2.9 M2) -- Tier 1/2
        reminder_keyword_by_paragraph = {}  # v2.9 M2: injected paragraph text -> keyword name
        for p in raw_paragraphs:
            norm = normalize_clause_text(p)
            if not norm:
                continue
            if enable_v29_mechanisms and keyword_df is not None:
                norm = strip_bespoke_ability_label(norm, keywords, keyword_df, keyword_label_df_floor)
            all_paragraphs.append(norm)
            if not is_keyword_only_paragraph(norm, keywords):
                matchable_paragraphs.append(norm)
                continue

            if not enable_v29_mechanisms:
                continue  # pre-v2.9 behavior: keyword-only lines simply excluded

            # v2.9 Mechanism 1: record keyword instance(s) carried by this line,
            # regardless of whether Mechanism 2 also fires below.
            frag_instances = parse_keyword_instances(norm, keywords)
            keyword_instances.extend(frag_instances)

            # v2.9 Mechanism 2: a line attributable to exactly ONE keyword
            # instance injects its reminder body as an ordinary matchable
            # paragraph, superseding the keyword-only exclusion FOR THAT LINE
            # ONLY. len(frag_instances) == 1 (not a raw fragment count) is the
            # right test -- v2.9 erratum 2's "<Keyword> <param>, where <param>
            # is <clause>." lines have 2+ comma fragments (the where-clause)
            # but still exactly one keyword instance, and must inject just
            # like a plain single-fragment keyword line. Multi-KEYWORD comma
            # lines (e.g. "flying, trample" -- 2 instances) remain a
            # documented simplification, not split for per-keyword reminder
            # attribution; bare keywords with no reminder stay excluded
            # exactly as pre-v2.9.
            if len(frag_instances) == 1:
                reminder_spans = extract_reminder_spans(p)
                if reminder_spans:
                    reminder_text = normalize_reminder_body(" ".join(reminder_spans))
                    if reminder_text:
                        matchable_paragraphs.append(reminder_text)
                        reminder_keyword_by_paragraph[reminder_text] = frag_instances[0]["keyword"]

        clauses = []
        for p in matchable_paragraphs:
            clauses.extend(split_clauses(p))

        # Phase 4 (ratified, R5): mana-fact extraction, one per recognizable
        # "add ... mana" paragraph on this face -- parallel data, never
        # replacing matchable_paragraphs/paragraph_tokens (R4).
        mana_facts = [f for f in (parse_mana_fact(p) for p in matchable_paragraphs) if f is not None]

        # Equip-cost delta term (Fable 5's recommendation, 2026-07-10):
        # parsed from `substituted` (RAW case, pre-lowercasing) since
        # EQUIP_COST_RE's "Equip" match is case-sensitive -- see that
        # function's own docstring for why. None if this face has no Equip
        # line at all, or a non-mana-symbol cost (e.g. a sacrifice cost).
        equip_cost_value = parse_equip_cost_value(substituted)

        faces.append({
            "name": raw_face["name"],
            "mana_cost": raw_face["mana_cost"],
            "type_line": raw_face["type_line"],
            "power": raw_face["power"],
            "toughness": raw_face["toughness"],
            "matchable_paragraphs": matchable_paragraphs,
            "paragraph_tokens": [
                [strip_sentence_final_token_period(tok) for tok in p.split()]
                for p in matchable_paragraphs
            ],
            # Reminder-injected paragraphs (v2.9 Mechanism 2) are exempt from
            # boundary detection -- caught measuring this fix's own corpus
            # impact (Faithless Looting's flashback gate: 171 -> 0 rows).
            # A keyword's reminder text (e.g. Flashback's "...for its
            # flashback cost. Then exile it.") is Scryfall's own fixed,
            # single-author explanation of ONE ability, always printed as
            # this same two-sentence pair on every card with that keyword --
            # not two independently-written native clauses that happen to
            # collide. Trimming it discarded "then exile it" and pushed the
            # remaining prefix's DF from 172 (rescue band) to 178 (DEAD),
            # converting a correctly-buried match into an incorrectly-excluded
            # one -- the opposite of what the trim rule exists to do. Native
            # paragraphs (not in reminder_keyword_by_paragraph) still get
            # full boundary detection; this exemption is reminder-scoped only.
            "paragraph_sentence_ends": [
                frozenset() if p in reminder_keyword_by_paragraph else sentence_boundary_indices(p)
                for p in matchable_paragraphs
            ],
            "full_text_all": "\n".join(all_paragraphs),
            "clauses": clauses,
            "reminder_keyword_by_paragraph": reminder_keyword_by_paragraph,
            "mana_facts": mana_facts,
            "equip_cost_value": equip_cost_value,
        })

    doc_reminder_keyword_by_paragraph = {}
    for f in faces:
        doc_reminder_keyword_by_paragraph.update(f["reminder_keyword_by_paragraph"])

    mana_facts = [fact for f in faces for fact in f["mana_facts"]]

    return {
        "oracle_id": card["oracle_id"],
        "name": card["name"],
        "type_line": card.get("type_line") or "",
        "cmc": card.get("cmc"),
        "color_identity": card.get("color_identity") or [],
        "keywords": keywords,
        "keyword_instances": keyword_instances,
        "reminder_keyword_by_paragraph": doc_reminder_keyword_by_paragraph,
        "faces": faces,
        "composed_full_text": "\n".join(f["full_text_all"] for f in faces),
        "mana_facts": mana_facts,
    }


def frame_signature(doc: dict) -> tuple:
    """Per-face (mana_cost, normalized type_line, power, toughness) tuple."""
    return tuple(
        (f["mana_cost"], normalize_type_line_for_frame(f["type_line"]), f["power"], f["toughness"])
        for f in doc["faces"]
    )


def frame_mismatch_fields(anchor_doc: dict, candidate_doc: dict) -> list:
    a_sig, c_sig = frame_signature(anchor_doc), frame_signature(candidate_doc)
    if len(a_sig) != len(c_sig):
        return ["face count"]
    names = ["mana_cost", "type_line", "power", "toughness"]
    mismatches = []
    for idx, (a_face, c_face) in enumerate(zip(a_sig, c_sig)):
        for name, a_val, c_val in zip(names, a_face, c_face):
            if a_val != c_val:
                mismatches.append(name if len(a_sig) == 1 else f"{name} (face {idx + 1})")
    return mismatches


def mana_cost_to_cmc(mana_cost: str) -> float:
    """Viewer-only (2026-07-13, per-face lookup feature): lightweight per-
    FACE mana-VALUE parse. Scryfall's own per-card `cmc` field is a whole-
    card number, ambiguous for a face-scoped pseudo-doc (a split/adventure
    face can have a wholly different cost from its sibling -- Fire // Ice,
    Bonecrusher Giant // Stomp) -- reuses MANA_SYMBOL_RE (already used to
    tokenize "add" ability clauses elsewhere in this file) to tokenize the
    FACE's own mana_cost string directly instead. Generic numbers add their
    value; X/Y/Z add 0 (Scryfall's own convention for an unresolved
    variable); any other symbol (a color, hybrid, Phyrexian, or {C}) adds
    1 -- matches Scryfall's own cmc computation for the common shapes
    relevant to mv_delta ranking here. Not used by build_card_doc() or any
    batch-pipeline path -- card-level cmc there still comes from Scryfall's
    own field, unchanged."""
    if not mana_cost:
        return 0.0
    total = 0.0
    for sym in MANA_SYMBOL_RE.findall(mana_cost):
        if sym.isdigit():
            total += int(sym)
        elif sym.upper() in ("X", "Y", "Z"):
            total += 0.0
        else:
            total += 1.0
    return total


def build_face_scoped_doc(doc: dict, face_index: int, keyword_vocabulary: frozenset) -> dict:
    """Viewer-only (2026-07-13, per-face lookup feature): a per-FACE
    pseudo-doc for a multi-faced card (transform/modal_dfc/split/
    adventure/flip), scoped to exactly ONE of build_card_doc()'s own
    already-built `faces` entries instead of joining all of them --
    everything face-scoped text/mana-fact matching needs (mana_facts,
    matchable_paragraphs, clauses, frame_signature) already lives on that
    one face dict untouched, so no scoring logic is duplicated here (same
    "no second scoring implementation" discipline emit_viewer.py's own
    docstring names). NOT called by build_card_doc() or the batch
    pipeline -- purely additive, invoked on demand by the viewer's own
    face-scoped corpus view (see emit_viewer.build_face_scoped_context()).

    `oracle_id` on the returned doc is a SYNTHETIC face key
    ("<real-oracle-id>::<face-index>"), not the real Scryfall oracle_id --
    required so gather_candidate_pool()'s `pool.discard(anchor_doc[
    "oracle_id"])` (unmodified, a generic function reused as-is here)
    correctly excludes THIS FACE's own key from its own candidate pool.
    CORRECTION (Fable 5's review, 2026-07-13): this does NOT, by itself,
    exclude a card's OTHER face(s) -- those are separate pool entries
    under their OWN synthetic keys, invisible to this one `.discard()`
    call (confirmed live: Adanto, the First Fort -- Legion's Landing's own
    back face -- appeared at position 2/42 in Legion's Landing's own
    Tier 2 before this was caught). That exclusion is handled one level up,
    in emit_viewer.export_face_anchor(), via face_meta's own
    "all_sibling_keys" list. `real_oracle_id` carries the true Scryfall id
    for legality/display lookups; `combined_name` carries the parent
    card's own slash-form name for the viewer's flip/weigh-both UI.

    keyword_instances (Mechanism 1, keyword kinship) is the one field
    build_card_doc() doesn't keep in a face-scoped-friendly shape -- it's
    derived from EVERY raw paragraph on a face (including keyword-only
    ones later excluded from matchable_paragraphs), which the face dict
    only keeps joined as `full_text_all`. Splitting that back on "\\n"
    recovers the exact same per-paragraph strings (full_text_all IS
    "\\n".join(all_paragraphs) in build_card_doc()), so this replays
    build_card_doc()'s own keyword-instance derivation exactly -- via the
    same is_keyword_only_paragraph()/parse_keyword_instances() calls,
    scoped to this one face -- rather than a second implementation.

    The returned doc's OWN `keywords` field is narrowed to just the
    keyword names this face's own keyword_instances actually carry (still
    original Scryfall casing, just filtered) -- NOT the same as the full
    `keywords` local variable below, which stays the whole card's list
    because is_keyword_only_paragraph()/parse_keyword_instances() need the
    full vocabulary to correctly classify THIS face's own lines (a keyword
    named in the card's vocabulary but never printed on this face simply
    never matches any of this face's own paragraphs, so passing the full
    list here causes no false positives). Bug found in review (Fable 5):
    an EARLIER draft copied the whole card's `keywords` onto both face
    docs unfiltered, which (1) inflated compute_keyword_df() (fixed at its
    own call site, see build_face_scoped_context()'s comment -- that
    fix alone would have been sufficient for qualification correctness)
    and (2) leaked a sibling face's keywords into keyword_overlap()'s
    DISPLAY column (e.g. Delver of Secrets' own front face showing
    "Flying" as a shared keyword, which is only ever printed on its OWN
    back face, Insectile Aberration) -- fixed here since keyword_overlap()
    reads directly off each doc's own `keywords` field."""
    face = doc["faces"][face_index]
    keywords = doc["keywords"]

    keyword_instances = []
    for norm in face["full_text_all"].split("\n"):
        if norm and is_keyword_only_paragraph(norm, keywords):
            keyword_instances.extend(parse_keyword_instances(norm, keywords))
    face_keyword_names = {inst["keyword"] for inst in keyword_instances}
    face_own_keywords = [kw for kw in keywords if kw.lower() in face_keyword_names]

    face_key = f'{doc["oracle_id"]}::{face_index}'
    face_doc = {
        "oracle_id": face_key,
        "real_oracle_id": doc["oracle_id"],
        "face_index": face_index,
        "combined_name": doc["name"],
        "name": face["name"],
        "type_line": face["type_line"],
        "cmc": mana_cost_to_cmc(face["mana_cost"]),
        # Color identity is a WHOLE-CARD concept in real Magic rules (fixed
        # for the card as printed, from symbols/color indicators on EITHER
        # face) -- not split per face, so this stays the parent doc's own
        # value on both of a card's face-scoped pseudo-docs, unchanged.
        "color_identity": doc["color_identity"],
        "keywords": face_own_keywords,
        "keyword_instances": keyword_instances,
        "reminder_keyword_by_paragraph": face["reminder_keyword_by_paragraph"],
        "faces": [face],
        "composed_full_text": face["full_text_all"],
        "mana_facts": face["mana_facts"],
    }
    # Entry #4's granted-keyword-SET facts (mirrors build_granted_keyword_
    # facts()'s own "post-processing pass over an already-built doc" shape,
    # unmodified) -- correctly scoped to just this face since face_doc
    # above only ever has ONE entry in its own "faces" list.
    face_doc["granted_keyword_facts"] = build_granted_keyword_facts(face_doc, keyword_vocabulary)
    return face_doc


# ---------------------------------------------------------------------------
# Corpus-wide indexes (the flood killer + candidate-pool efficiency)
# ---------------------------------------------------------------------------

def ngrams_for_tokens(tokens: list, min_len: int) -> list:
    if len(tokens) < min_len:
        return []
    return [" ".join(tokens[i:i + min_len]) for i in range(len(tokens) - min_len + 1)]


def build_indexes(card_docs: dict, ngram_min_len: int) -> tuple:
    """paragraph_index, clause_index, ngram_index: text -> set(oracle_id).
    clause_df, ngram_df: text -> distinct oracle_id count."""
    paragraph_index = defaultdict(set)
    clause_index = defaultdict(set)
    clause_df = defaultdict(int)
    ngram_index = defaultdict(set)
    ngram_df = defaultdict(int)

    for oracle_id in sorted(card_docs):
        doc = card_docs[oracle_id]
        card_paragraphs = set()
        card_clauses = set()
        card_ngrams = set()
        for face in doc["faces"]:
            card_paragraphs.update(face["matchable_paragraphs"])
            card_clauses.update(face["clauses"])
            for tokens in face["paragraph_tokens"]:
                card_ngrams.update(ngrams_for_tokens(tokens, ngram_min_len))
        for p in card_paragraphs:
            paragraph_index[p].add(oracle_id)
        for c in card_clauses:
            clause_index[c].add(oracle_id)
            clause_df[c] += 1
        for ng in card_ngrams:
            ngram_index[ng].add(oracle_id)
            ngram_df[ng] += 1

    return (
        dict(paragraph_index), dict(clause_index), dict(clause_df),
        dict(ngram_index), dict(ngram_df),
    )


def build_tag_index(card_tags: dict) -> dict:
    tag_index = defaultdict(set)
    for oracle_id in sorted(card_tags):
        for entry in card_tags[oracle_id]:
            tag_index[entry["slug"]].add(oracle_id)
    return dict(tag_index)


def compute_tag_stats(card_tags: dict) -> tuple:
    n_cards = len(card_tags)
    tag_card_count = defaultdict(int)
    for entries in card_tags.values():
        for e in entries:
            tag_card_count[e["slug"]] += 1
    idf = {
        slug: math.log(n_cards / count) if count > 0 else 0.0
        for slug, count in tag_card_count.items()
    }
    return idf, dict(tag_card_count), n_cards


def compute_keyword_df(card_docs: dict) -> dict:
    """v2.9 Mechanism 1: corpus DF per keyword name (count of DISTINCT cards
    carrying it), sourced from each card's own Scryfall `keywords` array --
    authoritative regardless of whether every instance parsed cleanly into
    a {keyword, param} pair."""
    df = defaultdict(int)
    for doc in card_docs.values():
        for kw in {k.lower() for k in doc["keywords"]}:
            df[kw] += 1
    return dict(df)


def compute_keyword_df_from_cards(cards: dict) -> dict:
    """Same shape/result as compute_keyword_df(), sourced directly from raw
    Scryfall records instead of already-built card_docs -- computable
    BEFORE build_card_doc runs, breaking what would otherwise be a circular
    dependency: build_card_doc's strip_bespoke_ability_label() step needs
    keyword_df to decide whether a leading "<Label> — " prefix is a rare,
    strippable bespoke ability word, but build_indexes()/compute_keyword_df
    normally only run AFTER every card_doc already exists. Mathematically
    identical to compute_keyword_df(card_docs) by construction -- doc[
    "keywords"] is always exactly card.get("keywords"), untouched by any
    paragraph-text normalization -- kept as a separate function (not a
    dict/kwarg reorder of the existing one) since the two operate on
    different input shapes (raw cards vs already-built docs)."""
    df = defaultdict(int)
    for card in cards.values():
        for kw in {k.lower() for k in (card.get("keywords") or [])}:
            df[kw] += 1
    return dict(df)


def print_keyword_stats(keyword_df: dict, floor: int, n: int = 30) -> None:
    print(f"\nv2.9 Mechanism 1 -- keyword corpus DF ({len(keyword_df):,} distinct keywords, floor={floor}):")
    ordered = sorted(keyword_df.items(), key=lambda kv: (-kv[1], kv[0]))
    print(f"  {n} most common:")
    for kw, df in ordered[:n]:
        print(f"    {kw}: DF={df}")
    print(f"  {n} least common:")
    for kw, df in ordered[-n:]:
        print(f"    {kw}: DF={df}")
    cleared = sorted(kw for kw, df in keyword_df.items() if df <= floor)
    print(f"  keywords clearing the DF floor (<= {floor}, {len(cleared)} of {len(keyword_df)}): {cleared}")


def build_keyword_index(card_docs: dict) -> dict:
    """v2.9 Mechanism 1: keyword_name -> set(oracle_id), sourced from each
    card's PARSED keyword_instances (not the raw Scryfall array) -- kept
    consistent with what keyword_kinship_match() actually compares, so the
    pool never carries a candidate that couldn't possibly qualify."""
    index = defaultdict(set)
    for oracle_id, doc in card_docs.items():
        for inst in doc["keyword_instances"]:
            index[inst["keyword"]].add(oracle_id)
    return dict(index)


def build_mana_pip_index(card_docs: dict) -> dict:
    """Pool-widening fix (Captain's ruling, 2026-07-10): mana pip letter
    (lowercase 'w'/'u'/'b'/'r'/'g', or the sentinel 'colorless') ->
    set(oracle_id), sourced from each card's own parsed mana_facts.

    Confirmed corpus bug this closes: gather_candidate_pool() had NO
    seeding path of its own for mana kinship -- a candidate was only ever
    found if it ALSO happened to share text/tag/keyword overlap with the
    anchor, which is unrelated to whether its mana production actually
    matches. Direct case: Priest of Gix ("When this creature enters, add
    {B}{B}{B}.", source_class=triggered_etb) shares ZERO Tagger tags, zero
    text, zero keywords with Dark Ritual ("Add {B}{B}{B}.",
    source_class=spell_effect) -- an EXACT amount+color match -- and was
    therefore invisible to mana_pip_kinship_match() despite qualifying by
    every rule R6 already ratified. Bog Witch was only ever discovered for
    the same anchor by ACCIDENT, via unrelated shared tags
    (adds-multiple-mana, cycle, ramp) -- not because of its mana fact.

    No DF-floor gate here, unlike build_keyword_index(): R6 already rules
    "ANY shared pip qualifies Tier 2... no natural corpus-DF analog exists
    for a mana shape" -- there is no "evergreen, can never qualify" case to
    prune the way there is for keywords, so every mana-producing card is a
    legitimate pool candidate by construction."""
    index = defaultdict(set)
    for oracle_id, doc in card_docs.items():
        for fact in doc.get("mana_facts", ()):
            for color in fact["colors"]:
                index[color].add(oracle_id)
            if fact["colorless_amount"] > 0:
                index["colorless"].add(oracle_id)
    return dict(index)


def build_granted_keyword_index(card_docs: dict) -> dict:
    """Pool-widening fix, same shape as build_mana_pip_index() above (found
    and fixed 2026-07-10, same session as the Equip-reminder obliteration):
    granted keyword name -> set(oracle_id), sourced from each card's own
    parsed granted_keyword_facts (size 1-2 only, GRANT_SIZE_CEILING --
    matches granted_keyword_kinship_match()'s own qualification scope, so
    the pool never carries a candidate that couldn't possibly qualify).

    Confirmed corpus bug this closes: gather_candidate_pool() had NO
    seeding path of its own for keyword_grant, discovered while verifying
    the Equip-reminder-injection removal above -- Swiftfoot Boots' pool
    collapsed from dozens of candidates to 2 once its Equip-reminder text
    (previously the DOMINANT, if accidental, seed for every cheap
    Equipment sharing that boilerplate) was excluded from
    matchable_paragraphs. Lightning Greaves -- Entry #4's own motivating
    case -- vanished from the pool entirely even though assign_tier()
    still correctly resolves it to keyword_grant when called directly:
    it was only ever being DISCOVERED via the boilerplate text overlap
    this session set out to kill, never via a seeding path of its own.
    Same class of gap as the mana-kinship one Captain already ruled on
    this session ("Priest of Gix / Dark Ritual") -- inherited, not
    decided, same fix shape. Since the 2026-07-12 generalization (see
    extract_granted_keyword_clause()), `granted_keyword_facts` now also
    holds mass-pump-shaped facts (formerly the standalone team_pump
    mechanism, which never had a pool-seeding index of its own) -- this
    index closes that gap too, for free, since it's keyed purely on
    `keywords`, unaware of which subject-phrase shape a fact came from."""
    index = defaultdict(set)
    for oracle_id, doc in card_docs.items():
        for fact in doc.get("granted_keyword_facts", ()):
            kw_set = fact["keywords"] or frozenset()
            if not (1 <= len(kw_set) <= GRANT_SIZE_CEILING):
                continue
            for kw in kw_set:
                index[kw].add(oracle_id)
    return dict(index)


def build_vanilla_creature_index(card_docs: dict) -> dict:
    """Pool-widening fix (Captain's ruling, 2026-07-12), same shape and same
    RECURRING gap as build_mana_pip_index()/build_granted_keyword_index()
    above: vanilla_creature_match (assign_tier(), see its own comment) has
    no seeding path of its own either. A blank creature has NO matchable
    text, keywords, mana facts, or granted-keyword facts -- the only thing
    that could ever put it in another blank creature's candidate pool is a
    SHARED TAGGER TAG, which is incidental (Balduvian Bears reached Grizzly
    Bears' pool this way; Runeclaw Bear, Forest Bear, Bear Cub, and others
    sharing the identical {1}{G} 2/2 blank frame did not, despite
    assign_tier() correctly resolving every one of them to Tier 0 when
    called directly). frame_signature() tuple -> set(oracle_id), keyed only
    for cards that are BOTH textless (empty composed_full_text) AND
    creatures -- the same two conditions vanilla_creature_match checks, so
    the index can never seed a candidate that couldn't actually qualify.

    Same-day extension (frame-MISMATCH kinship, assign_tier's new
    vanilla_creature elif): a blank creature's candidate pool now needs
    EVERY OTHER blank creature, not just its own frame bucket -- Scaled
    Wurm ({7}{G} 7/6) is a legitimate (if distant) Tier 1 kin of Grizzly
    Bears now, same as Runeclaw Bear is, and would never surface without
    also widening the pool, not just assign_tier() itself (the same class
    of gap this index was built to close in the first place). Callers
    union every value in this dict when the anchor itself is a blank
    creature -- see gather_candidate_pool()."""
    index = defaultdict(set)
    for oracle_id, doc in card_docs.items():
        if doc["composed_full_text"] or "Creature" not in type_bucket(doc["type_line"]):
            continue
        index[frame_signature(doc)].add(oracle_id)
    return dict(index)


def gather_candidate_pool(anchor_doc: dict, anchor_tags: list, paragraph_index: dict,
                           clause_index: dict, clause_df: dict, ngram_index: dict,
                           ngram_df: dict, tag_index: dict, keyword_index: dict, keyword_df: dict,
                           mana_index: dict, granted_keyword_index: dict, args: argparse.Namespace,
                           vanilla_creature_index: dict = None) -> set:
    pool = set()
    for face in anchor_doc["faces"]:
        for p in face["matchable_paragraphs"]:
            pool.update(paragraph_index.get(p, ()))
        for c in face["clauses"]:
            if clause_df.get(c, 0) <= args.clause_df_floor:
                pool.update(clause_index.get(c, ()))
        for tokens in face["paragraph_tokens"]:
            for ng in ngrams_for_tokens(tokens, args.ngram_min_len):
                # D2 (2026-07-16): seeded at T2_RESCUE_CEILING, not
                # args.ngram_df_floor -- Phase 3 raised T2's qualification
                # ceiling to T2_RESCUE_CEILING but this seeding comparison
                # was never updated to match, so any pair whose only shared
                # evidence sits in (ngram_df_floor, T2_RESCUE_CEILING] was
                # never discovered (DISCOVERY-RECALL-AUDIT.md Finding 1).
                # Keyword kinship's own floor below is intentionally
                # unchanged -- its qualification gate is still
                # args.ngram_df_floor, so its seed must match that, not this.
                if ngram_df.get(ng, 0) <= T2_RESCUE_CEILING:
                    pool.update(ngram_index.get(ng, ()))
    for entry in anchor_tags:
        pool.update(tag_index.get(entry["slug"], ()))
    # v2.9 Mechanism 1: keyword kinship doesn't rely on shared TEXT at all, so
    # a candidate sharing ONLY a qualifying keyword (no paragraph/clause/
    # ngram/tag overlap) would never be discovered by the lookups above.
    # Only pull from keywords that could actually qualify (DF<=floor) --
    # pulling in every evergreen-sharing card (e.g. every flyer) would be
    # wasteful and pointless, since evergreens never qualify by construction.
    for inst in anchor_doc.get("keyword_instances", ()):
        kw = inst["keyword"]
        if 0 < keyword_df.get(kw, 0) <= args.ngram_df_floor:
            pool.update(keyword_index.get(kw, ()))
    # Pool-widening fix (Captain's ruling, 2026-07-10): mana kinship has no
    # seeding path of its own otherwise -- see build_mana_pip_index()'s
    # docstring for the confirmed Priest-of-Gix/Dark-Ritual case this
    # closes. Unlike the keyword block above, no DF-floor gate: R6 already
    # rules any shared pip qualifies, so every mana-producing card sharing
    # a pip with the anchor is a legitimate candidate.
    for fact in anchor_doc.get("mana_facts", ()):
        for color in fact["colors"]:
            pool.update(mana_index.get(color, ()))
        if fact["colorless_amount"] > 0:
            pool.update(mana_index.get("colorless", ()))
    # Pool-widening fix (found + fixed 2026-07-10, same session as the
    # Equip-reminder obliteration): keyword_grant had no seeding path of
    # its own either -- see build_granted_keyword_index()'s docstring for
    # the confirmed Lightning-Greaves-vanishes-from-Boots'-pool case this
    # closes. Same "no DF-floor gate" reasoning as mana kinship just above:
    # granted_keyword_kinship_match() already rules ANY shared keyword
    # (within GRANT_SIZE_CEILING) qualifies, no evergreen-style "can never
    # qualify" case to prune.
    for fact in anchor_doc.get("granted_keyword_facts", ()):
        kw_set = fact["keywords"] or frozenset()
        if not (1 <= len(kw_set) <= GRANT_SIZE_CEILING):
            continue
        for kw in kw_set:
            pool.update(granted_keyword_index.get(kw, ()))
    # Pool-widening fix (Captain's ruling, 2026-07-12): vanilla_creature_
    # match has no seeding path of its own either -- see
    # build_vanilla_creature_index()'s docstring for the confirmed
    # Grizzly-Bears-only-finds-Balduvian-Bears-by-accident case this
    # closes. Only fires when the anchor is ITSELF a blank creature (a
    # textful anchor's frame_signature would never match a blank card's
    # anyway, since frame_signature says nothing about text -- this is
    # purely a lookup key, not a new qualification path).
    #
    # Same-day extension: pull EVERY blank creature in the corpus, not just
    # the anchor's own frame bucket -- assign_tier's new vanilla_creature
    # elif (frame MISMATCH kinship, Tier 1) means a blank creature is a
    # legitimate candidate for ANY other blank creature now, not only ones
    # sharing its exact frame. Restricting this seed to frame_signature(
    # anchor_doc) would silently reproduce the exact "assign_tier resolves
    # it correctly, gather_candidate_pool never offers it the chance" gap
    # this index was built to close in the first place, just one mismatch
    # level up. The corpus-wide vanilla-creature population is small (low
    # hundreds), so unioning every bucket here is cheap.
    if vanilla_creature_index and not anchor_doc["composed_full_text"] and "Creature" in type_bucket(anchor_doc["type_line"]):
        for oracle_ids in vanilla_creature_index.values():
            pool.update(oracle_ids)
    pool.discard(anchor_doc["oracle_id"])
    return pool


# ---------------------------------------------------------------------------
# Tier 2 fragment matching (Amendment 3, v2)
# ---------------------------------------------------------------------------

def longest_common_run(tokens_a: list, tokens_b: list) -> tuple:
    """Longest common contiguous run of tokens. Returns
    (length, end_index_a, end_index_b) where the run is
    tokens_a[end_index_a - length : end_index_a] ==
    tokens_b[end_index_b - length : end_index_b]. `end_index_b` (added for
    the sentence-boundary trim rule, 2026-07-10 -- see
    find_shared_fragments) was previously re-derived downstream via a
    separate substring scan; the DP already has it for free."""
    n, m = len(tokens_a), len(tokens_b)
    if n == 0 or m == 0:
        return 0, 0, 0
    prev_row = [0] * (m + 1)
    best_len = 0
    best_end_a = 0
    best_end_b = 0
    for i in range(1, n + 1):
        curr_row = [0] * (m + 1)
        token_a = tokens_a[i - 1]
        for j in range(1, m + 1):
            if token_a == tokens_b[j - 1]:
                curr_row[j] = prev_row[j - 1] + 1
                if curr_row[j] > best_len:
                    best_len = curr_row[j]
                    best_end_a = i
                    best_end_b = j
        prev_row = curr_row
    return best_len, best_end_a, best_end_b


def ngram_df_estimate(tokens: list, ngram_df: dict, ngram_min_len: int):
    """Min DF among the fragment's constituent minimum-length windows -- a
    safe upper bound on the fragment's true DF."""
    if len(tokens) < ngram_min_len:
        return None
    windows = ngrams_for_tokens(tokens, ngram_min_len)
    return min(ngram_df.get(w, 0) for w in windows)


def format_culprit_list(culprits: list, cap: int = 5) -> str:
    """Display-only truncation for trace_df_drift() culprit lists -- a
    generic template phrase (e.g. "search your library for a") can be
    shared by dozens of cycling-family keywords; the full list is real and
    traceable, but unwieldy in a terminal gate line."""
    if len(culprits) <= cap:
        return ", ".join(culprits)
    return ", ".join(culprits[:cap]) + f", +{len(culprits) - cap} more"


def trace_df_drift(fragment: str, ngram_min_len: int, legacy_ngram_index: dict, legacy_ngram_df: dict,
                    ngram_index: dict, ngram_df: dict, card_docs: dict) -> dict:
    """v2.9 stability-gate tracing (Captain's ruling): does NOT accept a
    within-tier reorder as "DF drift, therefore explained" on the mere
    ABSENCE of entries/exits -- it traces the actual delta. A fragment's
    RANK-RELEVANT DF is the MINIMUM across its constituent ngram_min_len
    windows (ngram_df_estimate's own convention) -- so this compares that
    MINIMUM, old vs new, not any individual window in isolation (a
    fragment can contain windows that drifted while the overall estimate
    -- and therefore its actual rank contribution -- stays put, e.g. "One
    with Nature": some of its windows DO gain new contributors, but its
    MINIMUM window is a different, unaffected one, so its own DF estimate
    and rank are byte-identical). Only once the minimum itself moves does
    this identify the window achieving the NEW minimum and the newly-
    contributing oracle_id(s), confirming (not assuming) that window
    landed inside one of THEIR injected reminder paragraphs specifically
    -- returning named "<card> (<keyword>)" culprits, never a bare "DF
    drifted" claim. Returns {"own_df_changed": bool, "culprits": [...]}."""
    if not fragment:
        return {"own_df_changed": False, "culprits": []}
    # Same fix as find_shared_paragraph (Phase 5, G-C): a Tier 1 whole-
    # paragraph fragment is the RAW matchable_paragraph text (periods
    # intact), not pre-stripped like a Tier 2 fragment already is -- must
    # match ngram_df's own per-token stripping convention (CO-C) or every
    # window touching a punctuated token silently misses (DF=0).
    tokens = [strip_sentence_final_token_period(tok) for tok in fragment.split()]
    if len(tokens) < ngram_min_len:
        return {"own_df_changed": False, "culprits": []}
    windows = ngrams_for_tokens(tokens, ngram_min_len)
    old_estimate = min(legacy_ngram_df.get(w, 0) for w in windows)
    new_estimate = min(ngram_df.get(w, 0) for w in windows)
    if new_estimate == old_estimate:
        return {"own_df_changed": False, "culprits": []}

    culprits = set()
    for w in windows:
        if ngram_df.get(w, 0) != new_estimate:
            continue  # only the window(s) actually driving the NEW rank-relevant estimate
        new_ids = ngram_index.get(w, set())
        old_ids = legacy_ngram_index.get(w, set())
        for oracle_id in (new_ids - old_ids):
            doc = card_docs.get(oracle_id)
            if not doc:
                continue
            for paragraph_text, kw in doc["reminder_keyword_by_paragraph"].items():
                if w in paragraph_text:
                    culprits.add(f"{doc['name']} ({kw})")
    return {"own_df_changed": True, "culprits": sorted(culprits)}


def find_shared_sentence(anchor_doc: dict, candidate_doc: dict, clause_df: dict,
                          ngram_min_len: int, rescue_ceiling: int, exclude: frozenset = frozenset()):
    """Short whole-sentence identity Tier 2 path (Fable 5's recommendation,
    EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md Section 4c, 2026-07-10,
    ratified by Captain): find_shared_fragments() can never qualify a
    matched clause shorter than ngram_min_len tokens, by construction --
    e.g. "Exile target nonland permanent" is a complete, defining 4-word
    ability, one word short of the 5-token floor, and structurally
    invisible to that path no matter how rare it is corpus-wide. This is
    the same KIND of evidence as Tier 1's whole-paragraph exact match
    (find_shared_paragraph), one structural level down: an exact, byte-
    identical SENTENCE (not a whole paragraph, not an arbitrary token
    run) shared by both cards. Deliberately scoped to sentences UNDER
    ngram_min_len only -- a sentence that long or longer is already
    reachable via find_shared_fragments (as a >=5-token run, possibly with
    cumulative multi-run credit), so this path only adds coverage for
    clauses the n-gram path can never see, never duplicates it.

    Reuses clause_index/clause_df (already built corpus-wide by
    build_indexes() from every face's `clauses` field, via split_clauses()
    -- previously only a fast candidate-pool pre-filter, per that
    function's own docstring) rather than a new index; this is an EXACT
    corpus-wide count of the literal sentence text, the same "para_exact_df"
    convention Tier 1 already uses for short paragraphs (R2, Phase 3), not
    a windowed approximation. Same full/discounted/rescue/dead banding as
    the text/reminder path, same rescue_ceiling (T2_RESCUE_CEILING).
    `exclude` (mirrors find_shared_paragraph/find_shared_fragments): normalized
    paragraph texts to skip entirely on either side -- the no-double-count
    suppression for a keyword already claimed by Mechanism 1.

    Returns None or (text, df) for the best (lowest-DF, then longest, then
    alphabetical for determinism) qualifying shared sentence -- single best
    only, no cumulative multi-sentence credit (a v1 scope choice, not
    corpus-measured to be worth the added complexity yet)."""
    anchor_sentences = set()
    for af in anchor_doc["faces"]:
        for p in af["matchable_paragraphs"]:
            if p in exclude:
                continue
            for c in split_clauses(p):
                if len(c.split()) < ngram_min_len:
                    anchor_sentences.add(c)
    if not anchor_sentences:
        return None
    candidate_sentences = set()
    for cf in candidate_doc["faces"]:
        for p in cf["matchable_paragraphs"]:
            if p in exclude:
                continue
            candidate_sentences.update(split_clauses(p))
    shared = anchor_sentences & candidate_sentences
    if not shared:
        return None
    best_text, best_df, best_key = None, None, None
    for text in shared:
        df = clause_df.get(text, 1)
        if df > rescue_ceiling:
            continue
        key = (df, -len(text.split()), text)
        if best_key is None or key < best_key:
            best_key, best_text, best_df = key, text, df
    if best_text is None:
        return None
    return best_text, best_df


def find_clause_corroboration(anchor_doc: dict, candidate_doc: dict, clause_df: dict,
                               ngram_min_len: int, exclude_paragraphs: frozenset = frozenset(),
                               exclude_texts: frozenset = frozenset()) -> list:
    """Secondary corroboration (Captain's ruling, 2026-07-11) -- the sibling
    of find_shared_sentence() that answers a different question: not "what's
    the single BEST qualifying short clause" but "what OTHER short clauses
    (< ngram_min_len tokens) do these two cards share at all," regardless of
    DF band. Deliberately UNBANDED, unlike find_shared_sentence(): a clause
    that would have independently qualified (DF <= rescue_ceiling) but got
    shadowed by a better-tier match elsewhere in the cascade, and a clause
    that's genuinely too common to EVER independently qualify (DF in the
    hundreds, e.g. a bare "draw a card"), are equally valid corroboration
    once real kinship is already established some other way -- the banding
    distinction only matters for what can be the SOLE basis of
    qualification, not for what's worth showing once qualification already
    happened. `exclude_texts` excludes whatever's already claimed as this
    pair's primary fragment/extra_fragments, so a clause already show as
    the winning evidence is never redundantly repeated as its own
    corroboration. Called ONLY after a pair has already qualified Tier 1/2
    by other means -- see the CORROBORATION_MIN_OTHER_WORDS gate at
    assign_tier()'s call site, which this function itself does not enforce.
    Sorted by DF ascending (rarest first), then alphabetically for
    determinism; capping is the caller's job (CORROBORATION_MAX_SHOWN_PER_
    KIND). Returns a list of (text, df) tuples, empty if nothing shared.

    Provenance-filtered (Fable 5's engine-wide audit, 2026-07-12 -- New
    Finding N4): a clause that's v2.9 Mechanism-2-injected reminder text
    on BOTH sides is excluded from corroboration entirely, same
    "near-worthless" judgment R1/PROVENANCE_DISCOUNT_WEIGHT/Option C
    already make everywhere else a match's provenance is checked in this
    file -- corroboration is meant to surface a REAL secondary connection,
    not a coincidental collision of two unrelated keywords' identical,
    engine-injected reminder boilerplate. No live instance of this was
    found in the default panel (short reminder clauses under
    ngram_min_len tokens are rare), but the gap is real and cheap to
    close -- left unfiltered would have been an inconsistency, not a
    deliberate design choice."""
    anchor_sentences = set()
    for af in anchor_doc["faces"]:
        for p in af["matchable_paragraphs"]:
            if p in exclude_paragraphs:
                continue
            for c in split_clauses(p):
                if len(c.split()) < ngram_min_len and c not in exclude_texts:
                    anchor_sentences.add(c)
    if not anchor_sentences:
        return []
    candidate_sentences = set()
    for cf in candidate_doc["faces"]:
        for p in cf["matchable_paragraphs"]:
            if p in exclude_paragraphs:
                continue
            candidate_sentences.update(split_clauses(p))
    shared = anchor_sentences & candidate_sentences
    if not shared:
        return []
    shared = {text for text in shared if not fragment_both_sides_injected(text, anchor_doc, candidate_doc)}
    if not shared:
        return []
    result = [(text, clause_df.get(text, 1)) for text in shared]
    result.sort(key=lambda t: (t[1], t[0]))
    return result


def fragment_run_weight(run_index: int) -> float:
    """Cumulative fragment scoring rank weight by run position (Captain's
    ruling, 2026-07-10, CUMULATIVE-FRAGMENT-SCORING-BUILD-HANDOFF.md):
    diminishing returns for the 2nd/3rd run, then a FLOOR at 0.25 (not a
    continued decay to near-zero) so a candidate with many qualifying runs
    doesn't have its 4th+ run's contribution vanish. run_index is 0-based
    (0 = the primary/longest run, which this function is never actually
    called for -- its weight is always 1.0, baked into compute_rank's
    existing raw term unchanged). Explicitly floored, not monotonically
    decaying forever -- flagged as provisional, may move to a 0.5 floor if
    corpus impact says so (same session note)."""
    if run_index == 1:
        return 0.5
    return 0.25


def trim_run_for_sentence_boundary(a_start: int, c_start: int, length: int,
                                    anchor_ends: frozenset, candidate_ends: frozenset,
                                    ngram_min_len: int) -> int:
    """Sentence-boundary trim rule (Fable 5's recommendation, EQUIPMENT-
    REMINDER-AND-WEIGHTING-DELIBERATION.md, 2026-07-10, ratified by
    Captain): a matched run that spans a sentence boundary -- on EITHER
    side, the anchor's own paragraph structure or the candidate's -- is a
    coincidence (two unrelated sentences that happen to abut with matching
    words at the seam, e.g. Growth Spiral's "...draw a card." + "You may
    put a land..." colliding with Nahiri's Lithoforming's "...draw a
    card." + "You may play X additional lands...") UNLESS what follows the
    boundary is itself a substantial (>=ngram_min_len token) continuation,
    which is real corroborating evidence a bare 1-2 token overlap isn't.
    Finds the LEFTMOST boundary within the run's interior (relative
    offsets 0..length-2 -- the run's own final token can never "cross"
    anything, nothing follows it within the run) at either side's own
    original token positions (a_start+k / c_start+k -- the run is the same
    literal words on both sides, so a relative offset means the same word
    either way, but each side's OWN sentence structure is checked
    independently, since identical words can sit in different sentence
    positions on each card). Returns the resulting length: unchanged if no
    boundary forces a trim (the overwhelming majority of runs -- most
    shared text doesn't cross a sentence at all), else the leftmost
    qualifying boundary's prefix length (which may itself fall below
    ngram_min_len -- callers must re-check the floor, same as any other
    qualification path)."""
    for k in range(length - 1):
        if (a_start + k) in anchor_ends or (c_start + k) in candidate_ends:
            tail_length = length - (k + 1)
            if tail_length >= ngram_min_len:
                return length  # long continuation past the seam -- corroborated, not a coincidence
            return k + 1  # short/no continuation -- only the leading segment survives
    return length


def find_shared_fragments(anchor_doc: dict, candidate_doc: dict, ngram_df: dict,
                           ngram_min_len: int, ngram_floor: int, exclude: frozenset = frozenset()):
    """Cumulative fragment scoring (2026-07-10 ruling): returns ALL
    qualifying (>=ngram_min_len tokens, DF<=floor) non-overlapping shared
    runs within the SINGLE best-matching anchor/candidate paragraph pair
    (never across different paragraph pairs -- keeps compute_fact_penalties
    correct without change, since every run shares the same paragraph
    context). Returns a list of (fragment_text, df, length) tuples, longest
    first, empty list if nothing qualifies. Unbounded (Captain's ruling) --
    stops only when no further run clears ngram_min_len/floor.

    Mechanics: find the global-best pair exactly as the old single-run
    find_shared_fragment() did, then mask that run's token span on both
    sides with unique per-position sentinel tokens (so a masked span can
    never accidentally re-match) and repeat longest_common_run() on the
    SAME pair only. `exclude` (v2.9, unchanged): normalized paragraph texts
    to skip entirely on either side -- the no-double-count suppression for
    a keyword that already qualified this pair via Mechanism 1.

    Sentence-boundary trim rule (2026-07-10, Fable 5's recommendation,
    ratified): every candidate run -- both the initial best-pair selection
    and every subsequent masked-and-repeated run -- is passed through
    trim_run_for_sentence_boundary() before its length/DF are evaluated
    against the floor. A run's ORIGINAL (untrimmed) span is still what
    gets masked out before searching for the next run -- the discarded
    tail was never going to qualify as evidence on its own (that's WHY it
    was discarded), no information is lost by removing it from further
    consideration too, and this avoids the next iteration wastefully
    rediscovering the identical sub-floor tail."""
    candidates = []
    for af in anchor_doc["faces"]:
        for a_idx, a_tokens in enumerate(af["paragraph_tokens"]):
            if af["matchable_paragraphs"][a_idx] in exclude:
                continue
            anchor_ends = af["paragraph_sentence_ends"][a_idx]
            for cf in candidate_doc["faces"]:
                for c_idx, c_tokens in enumerate(cf["paragraph_tokens"]):
                    if cf["matchable_paragraphs"][c_idx] in exclude:
                        continue
                    candidate_ends = cf["paragraph_sentence_ends"][c_idx]
                    length, end_a, end_b = longest_common_run(a_tokens, c_tokens)
                    if length < ngram_min_len:
                        continue
                    a_start, c_start = end_a - length, end_b - length
                    trimmed_length = trim_run_for_sentence_boundary(
                        a_start, c_start, length, anchor_ends, candidate_ends, ngram_min_len,
                    )
                    if trimmed_length < ngram_min_len:
                        continue
                    frag_tokens = a_tokens[a_start:a_start + trimmed_length]
                    df = ngram_df_estimate(frag_tokens, ngram_df, ngram_min_len)
                    if df is None or df > ngram_floor:
                        continue
                    candidates.append((
                        trimmed_length, df, " ".join(frag_tokens),
                        a_tokens, c_tokens, end_a, length, anchor_ends, candidate_ends,
                    ))
    if not candidates:
        return []
    (length, df, text, a_tokens, c_tokens, end_a,
     orig_length, anchor_ends, candidate_ends) = max(candidates, key=lambda c: (c[0], -c[1], c[2]))
    runs = [(text, df, length)]

    # Masking uses the ORIGINAL (pre-trim) span -- orig_length, not the
    # trimmed `length` just reported as evidence -- per this function's
    # own docstring on why the discarded tail is masked too.
    cur_a, cur_c, cur_end_a, cur_length = a_tokens, c_tokens, end_a, orig_length
    while True:
        matched = cur_a[cur_end_a - cur_length:cur_end_a]
        start_c = None
        for i in range(len(cur_c) - cur_length + 1):
            if cur_c[i:i + cur_length] == matched:
                start_c = i
                break
        run_tag = len(runs)
        cur_a = (
            cur_a[:cur_end_a - cur_length]
            + [f"__MASK_A_{run_tag}_{j}__" for j in range(cur_length)]
            + cur_a[cur_end_a:]
        )
        if start_c is not None:
            cur_c = (
                cur_c[:start_c]
                + [f"__MASK_B_{run_tag}_{j}__" for j in range(cur_length)]
                + cur_c[start_c + cur_length:]
            )
        next_length, next_end_a, next_end_b = longest_common_run(cur_a, cur_c)
        if next_length < ngram_min_len:
            break
        next_a_start, next_c_start = next_end_a - next_length, next_end_b - next_length
        next_trimmed_length = trim_run_for_sentence_boundary(
            next_a_start, next_c_start, next_length, anchor_ends, candidate_ends, ngram_min_len,
        )
        if next_trimmed_length < ngram_min_len:
            break
        next_frag_tokens = cur_a[next_a_start:next_a_start + next_trimmed_length]
        next_df = ngram_df_estimate(next_frag_tokens, ngram_df, ngram_min_len)
        if next_df is None or next_df > ngram_floor:
            break
        runs.append((" ".join(next_frag_tokens), next_df, next_trimmed_length))
        cur_end_a, cur_length = next_end_a, next_length
    return runs


# ---------------------------------------------------------------------------
# Tier assignment (Amendment 1, v2 -- FROZEN, do not touch qualification logic)
# ---------------------------------------------------------------------------

def type_bucket(type_line: str) -> frozenset:
    types = set()
    for face_part in type_line.split(" // "):
        left = face_part.split("—")[0]
        for word in left.split():
            if word in MAJOR_TYPES:
                types.add(word)
    return frozenset(types)


# Captain ruling: Instant and Sorcery do not count as disjoint for the
# TIER-ASSIGNMENT demotion below -- both are one-shot, nonpermanent spell
# types, unlike e.g. Artifact vs Creature. Scoped to assign_tier()'s
# demotion check ONLY: compute_affinity()'s type_match bonus and the
# report's "type bucket" fact column (type_line_bucket_match()) still use
# plain type_bucket() unchanged, since those are separate questions (rank
# affinity, display) this ruling was never asked to touch. Tier 0 already
# requires an exact frame_signature match (mana_cost + type_line + power/
# toughness), which Instant vs Sorcery always fails regardless of this
# exemption -- so it can only ever move a match between Tier 1 and Tier 2,
# never grant Tier 0.
INSTANT_SORCERY_EXEMPT = frozenset({"Instant", "Sorcery"})


def types_disjoint_for_demotion(anchor_types: frozenset, candidate_types: frozenset) -> bool:
    if not anchor_types or not candidate_types:
        return False
    if anchor_types <= INSTANT_SORCERY_EXEMPT and candidate_types <= INSTANT_SORCERY_EXEMPT:
        return False
    return not (anchor_types & candidate_types)


def creature_subtypes(type_line: str) -> frozenset:
    """v2.5 -- post-dash type-line tokens, per face, but ONLY for faces that
    are themselves Creature (a shared "Equipment" or "Human" subtype on a
    non-creature face isn't the affinity the change order is after). Reuses
    type_bucket's own "—" / " // " splitting convention. Derived, never
    hand-recalled -- see the v2.5 spot-check block, which prints these for
    Grand Abolisher, Drannith Magistrate, and Avatar's Wrath."""
    subtypes = set()
    for face_part in (type_line or "").split(" // "):
        if "—" not in face_part:
            continue
        left, right = face_part.split("—", 1)
        if "Creature" not in left.split():
            continue
        subtypes.update(right.split())
    return frozenset(subtypes)


def compute_affinity(anchor_doc: dict, candidate_doc: dict, type_match_bonus: float,
                      subtype_bonus: float, subtype_bonus_cap: float) -> dict:
    """v2.5 -- the frame-affinity bonus. type_match reuses the same "same"
    definition as the type_bucket fact column (both non-empty and equal,
    per-face union); shared creature subtypes are counted via
    creature_subtypes() and multiplied by subtype_bonus, capped. Returns the
    full breakdown so gates/reports can explain movement, not just the
    total."""
    a_types = type_bucket(anchor_doc["type_line"])
    c_types = type_bucket(candidate_doc["type_line"])
    type_match = bool(a_types and c_types and a_types == c_types)
    shared_subtypes = sorted(
        creature_subtypes(anchor_doc["type_line"]) & creature_subtypes(candidate_doc["type_line"])
    )
    type_term = type_match_bonus if type_match else 0.0
    subtype_term = min(len(shared_subtypes) * subtype_bonus, subtype_bonus_cap)
    return {
        "type_match": type_match,
        "shared_subtypes": shared_subtypes,
        "type_term": type_term,
        "subtype_term": subtype_term,
        "affinity_term": type_term + subtype_term,
    }


def restoration_fraction(affinity_term: float, type_match_bonus: float, subtype_bonus_cap: float) -> float:
    """Phase 3 rebalance (Captain ruling): how much of a band-discounted
    fragment's weight gets restored toward 1.0, on [0, 1]. Frame affinity
    only (type match + shared subtype) -- MV moved OUT of this restoration
    and into mv_asymmetric_distance()/compute_rank's own mv_term instead
    (Captain: don't add a second MV term, realize it inside the existing
    one). General by construction -- no card identity enters this
    function."""
    max_affinity = type_match_bonus + subtype_bonus_cap
    if max_affinity <= 0:
        return 0.0
    return min(1.0, affinity_term / max_affinity)

def band_for_df(df, full_ceiling: float, discount_ceiling: float, rescue_ceiling=None) -> str:
    """R3 (Phase 3, ratified): 'full'|'discounted'|'rescue'|'dead'. `df` of
    None (should not occur for any real corpus paragraph/fragment; a defensive
    guard, not an expected path) is treated as 'dead' -- never silently admit
    something the engine couldn't measure. `rescue_ceiling=None` means no
    rescue zone exists for this population (R3: short paragraphs have none)."""
    if df is None:
        return "dead"
    if df <= full_ceiling:
        return "full"
    if df <= discount_ceiling:
        return "discounted"
    if rescue_ceiling is not None and df <= rescue_ceiling:
        return "rescue"
    return "dead"


def normalize_paragraph_for_fragment_comparison(paragraph_text: str) -> str:
    """BUG FIX (found investigating Equip-reminder rescue-band clutter,
    2026-07-10): a `find_shared_fragment(s)`-reconstructed fragment has
    each token's trailing period already stripped (`strip_sentence_final_
    token_period`, the CO-C convention) -- comparing it against RAW
    paragraph text (periods intact) breaks substring containment at every
    internal sentence boundary WITHIN a multi-sentence paragraph. Concrete
    case: Swiftfoot Boots' injected Equip reminder is stored as `"{1}:
    attach to target creature you control. equip only as a sorcery."` (one
    paragraph, two sentences); the matched fragment reconstructs as
    `"{1}: attach to target creature you control equip only as a
    sorcery"` (no period after "control") -- neither `==` nor `in`
    matches the raw text, so `fragment_both_sides_injected()` silently
    returned False for 62 Swiftfoot Boots pairs that should have gotten
    the hard PROVENANCE_DISCOUNT_WEIGHT, landing them at the generic
    rescue-band weight (0.15) instead of the intended 0.05 -- exactly the
    already-ratified mechanism this discount exists for (R1, Phase 3),
    just not firing. Normalizing the paragraph text the same way the
    fragment was tokenized fixes the comparison for both
    `text_injected_on_side` and `find_reminder_attribution` (identical
    flawed pattern in both, same root cause -- fixed once, shared here)."""
    return " ".join(strip_sentence_final_token_period(tok) for tok in paragraph_text.split())


def text_injected_on_side(text: str, doc: dict) -> bool:
    """Is `text` (or is it contained within) a v2.9 Mechanism-2-injected
    reminder paragraph on this side? Substring check (not just exact-match)
    so a Tier 2 fragment carved out of an injected paragraph is recognized
    too, the same convention find_reminder_attribution already uses."""
    for paragraph_text in doc["reminder_keyword_by_paragraph"]:
        normalized = normalize_paragraph_for_fragment_comparison(paragraph_text)
        if text == normalized or text in normalized:
            return True
    return False


def fragment_both_sides_injected(text: str, anchor_doc: dict, candidate_doc: dict) -> bool:
    """R1 (Phase 3, ratified): provenance is engine-known, never a named
    keyword/phrase list -- both sides' occurrence of the matched
    paragraph/fragment must themselves be Mechanism-2-injected reminder
    text for the discount to fire. A one-side-native match (the
    Hero-of-Bladehold class) is explicitly NOT discounted -- ratified
    by-design overlap."""
    return text_injected_on_side(text, anchor_doc) and text_injected_on_side(text, candidate_doc)


def find_shared_paragraph(anchor_doc: dict, candidate_doc: dict, ngram_df: dict, ngram_min_len: int,
                           paragraph_index: dict, exclude: frozenset = frozenset()):
    """R3/F1 fix (Phase 3, ratified): closes the missing-DF-gate bug --
    previously ANY exact-string paragraph match qualified Tier 1 regardless
    of how common it was corpus-wide (Boros Charm's "choose one --" header:
    221 false Tier 1 rows; Swiftfoot Boots equip reminder: 62 more). Now
    applies the same commonality-band discipline Tier 2 already had, per
    paragraph (R2): >=ngram_min_len tokens use ngram_scale_df; shorter use
    para_exact_df, each against its OWN band edges. DEAD-band matches do
    NOT qualify at all (falls through to Tier 2/3) -- the second lawful
    exception to rank-buries-never-excludes, alongside the v2.6
    corroboration gate. Among surviving candidate paragraphs, the best band
    wins (full > discounted > rescue), ties broken by lowest DF then
    longest text, for determinism. `exclude` (v2.9): see find_shared_fragment
    -- same no-double-count suppression. Returns None, or
    {"text":, "band":, "weight":, "df":, "both_sides_injected":}."""
    candidates = []
    seen_texts = set()
    for af in anchor_doc["faces"]:
        for ap in af["matchable_paragraphs"]:
            if ap in exclude or ap in seen_texts:
                continue
            matched = any(ap in cf["matchable_paragraphs"] for cf in candidate_doc["faces"])
            if not matched:
                continue
            seen_texts.add(ap)

            # BUG FIX (Phase 5, caught by G-C): must use the SAME per-token
            # sentence-final-period stripping (CO-C) that built ngram_df
            # itself (via face["paragraph_tokens"]) -- a bare .split() here
            # silently missed every ngram_df lookup whose window included a
            # punctuated token, defaulting to DF=0 (band "full") for
            # anything with an internal period, e.g. Faithless Looting's
            # flashback reminder ("...flashback cost. then exile it.")
            # measured DF=0 instead of its true 173 and wrongly qualified
            # Tier 1 at full weight for 171 candidates.
            tokens = [strip_sentence_final_token_period(tok) for tok in ap.split()]
            if len(tokens) >= ngram_min_len:
                df = ngram_df_estimate(tokens, ngram_df, ngram_min_len)
                band = band_for_df(df, T1_LONG_FULL_WEIGHT_CEILING, T1_LONG_DISCOUNT_CEILING, T1_LONG_RESCUE_CEILING)
            else:
                df = len(paragraph_index.get(ap, ()))
                band = band_for_df(df, T1_SHORT_FULL_WEIGHT_CEILING, T1_SHORT_DISCOUNT_CEILING, None)
            if band == "dead":
                continue

            both_injected = fragment_both_sides_injected(ap, anchor_doc, candidate_doc)
            weight = PROVENANCE_DISCOUNT_WEIGHT if both_injected else BAND_WEIGHTS[band]
            candidates.append({"text": ap, "band": band, "weight": weight, "df": df,
                                "both_sides_injected": both_injected})

    if not candidates:
        return None
    band_rank = {"full": 0, "discounted": 1, "rescue": 2}
    return min(candidates, key=lambda c: (band_rank[c["band"]], c["df"], -len(c["text"])))


def find_reminder_attribution(fragment: str, anchor_doc: dict, candidate_doc: dict):
    """v2.9 Mechanism 2: which keyword (if any) the winning text-path
    fragment/paragraph is attributed to -- exact match covers Tier 1 (whole
    injected paragraph); substring covers Tier 2 (an n-gram fragment carved
    out of an injected paragraph)."""
    for doc in (anchor_doc, candidate_doc):
        for paragraph_text, kw in doc["reminder_keyword_by_paragraph"].items():
            normalized = normalize_paragraph_for_fragment_comparison(paragraph_text)
            if fragment == normalized or fragment in normalized:
                return kw
    return None


def keyword_kinship_match(anchor_doc: dict, candidate_doc: dict, keyword_df: dict, floor: int) -> list:
    """v2.9 Mechanism 1. Returns ALL qualifying (DF<=floor) shared-keyword
    matches between anchor and candidate:
    [{"keyword":, "tier": 1|2, "anchor_param":, "candidate_param":, "df":}, ...].
    tier=1 when some anchor/candidate param pair for that keyword is EQUAL
    (an identical compressed line, e.g. both "mobilize 2"); tier=2
    otherwise (shared keyword, different param). Evergreen keywords
    (DF > floor) are never returned -- qualification is by construction,
    not a separate check layered on top."""
    anchor_by_kw = defaultdict(list)
    for inst in anchor_doc["keyword_instances"]:
        anchor_by_kw[inst["keyword"]].append(inst["param"])
    candidate_by_kw = defaultdict(list)
    for inst in candidate_doc["keyword_instances"]:
        candidate_by_kw[inst["keyword"]].append(inst["param"])

    matches = []
    for kw in sorted(set(anchor_by_kw) & set(candidate_by_kw)):
        df = keyword_df.get(kw, 0)
        if df <= 0 or df > floor:
            continue
        a_params = anchor_by_kw[kw]
        c_params = candidate_by_kw[kw]
        same_param = any(ap == cp for ap in a_params for cp in c_params)
        matches.append({
            "keyword": kw, "tier": 1 if same_param else 2,
            "anchor_param": a_params[0], "candidate_param": c_params[0], "df": df,
        })
    return matches


def mana_cascade_penalty(a_fact: dict, c_fact: dict) -> float:
    """R5 cascade, rank ONLY (never qualification -- Captain ruling: "open
    the gate, allow other weights to surface the best matches"). Amount
    closeness and shape (source_class/repeatable -- HOW the mana is
    delivered: activated tap vs ETB/upkeep trigger vs one-shot spell
    effect, etc.) trade off within a SMALL amount gap (Captain's ruling,
    2026-07-12, partially reversing R5's original "amount always leads"):
    a same-shape match one mana off now outranks an exact-amount
    cross-shape match (e.g. Thran Dynamo's activated-tap {C}{C}{C} beats a
    hypothetical ETB-triggered {C}{C} effect against Sol Ring's activated-
    tap {C}{C}), but amount still dominates once the gap reaches two or
    more (MANA_SHAPE_MISMATCH_PENALTY sits strictly between one and two
    units of MANA_AMOUNT_PENALTY_WEIGHT -- see that constant's own
    comment). Source-class/repeatable is still not a QUALIFICATION
    requirement -- same shared-slot precedent as a different keyword
    param, e.g. Dark Ritual's one-shot {B}{B}{B} and Bog Witch's
    repeatable {B}{B}{B} still qualify each other at Tier 2 either way,
    this only changes which of several qualifying candidates ranks
    higher. Then color-set exactness; then the candidate's own production
    breadth (widening) for non-exact matches; then a flat rider penalty.
    Mixed (color+colorless) outputs: the LARGER component leads (whichever
    of colored_pip_count/colorless_amount is bigger drives the color-set/
    amount comparison); a true 50/50 mixed ability gets no special rule
    here -- the other terms (amount, shape, widening, rider) still
    differentiate it, per R5."""
    penalty = MANA_AMOUNT_PENALTY_WEIGHT * abs(a_fact["amount"] - c_fact["amount"])

    if a_fact["source_class"] != c_fact["source_class"] or a_fact["repeatable"] != c_fact["repeatable"]:
        penalty += MANA_SHAPE_MISMATCH_PENALTY

    a_colors, c_colors = a_fact["colors"], c_fact["colors"]
    if a_colors or c_colors:
        if a_colors == c_colors:
            pass  # exact color-set match -- no color or widening penalty at all
        else:
            extra = c_colors - a_colors
            missing = a_colors - c_colors
            penalty += MANA_EXTRA_COLOR_PENALTY * len(extra) + MANA_MISSING_COLOR_PENALTY * len(missing)
            penalty += MANA_WIDENING_PENALTY.get(c_fact["widening"], 0.0)
    # else: both purely colorless -- amount term above already carries the comparison

    if c_fact["has_rider"]:
        penalty += MANA_RIDER_PENALTY
    return penalty


# ---------------------------------------------------------------------------
# Entry #4 (Captain's ruling, 2026-07-10) -- Equipment/Aura granted-keyword-
# SET kinship, PARALLEL to text/keyword/mana matching, same shared-slot
# precedent as mana kinship (R6): ANY shared granted keyword qualifies
# Tier 2, ranked by how many stray (non-shared) keywords sit on either
# side. Fixes Swiftfoot Boots ("hexproof and haste") <-> Lightning Greaves
# ("haste and shroud") -- same sentence shape, real shared "haste", but
# longest_common_run() only finds the 3-token "equipped creature has"
# prefix (keyword order flips), below the 5-token floor, and Mechanism 1
# (keyword kinship) never sees the clause at all (no comma, "and"-joined).
# ---------------------------------------------------------------------------

KEYWORD_NAME_SHAPE_RE = re.compile(r"^[a-z][a-z '-]{1,25}$")


def build_keyword_vocabulary(cards: dict) -> frozenset:
    """Canonical set of every keyword-ability NAME that appears anywhere in
    the corpus' own Scryfall `keywords` field (lowercased) -- reused to
    validate a granted-keyword-clause extraction, same one-corpus-one-truth
    rationale as the rest of this engine (no hand-curated keyword list).
    Scryfall's `keywords` field is broader than static grantable keyword
    abilities (flying, trample, hexproof...) -- it also carries ability
    words (grandeur, boast) and Universes Beyond flavor/joke strings
    ("for auld lang syne", "10,000 needles") that could never legitimately
    appear in an "Equipped/Enchanted creature has X" idiom. A light,
    STRUCTURAL filter (letters/spaces/hyphens only, <=3 words) drops the
    obvious non-keyword-shaped noise -- confirmed directly: 72 of 845 raw
    entries fail this shape check, all genuinely non-keyword flavor text.
    Does not attempt to also separate real ability words (cascade, storm)
    from static grantable keywords by MEANING, only by shape -- low
    practical risk (no real card phrases a grant clause as "has cascade"),
    not worth a hand-curated allowlist the rest of this codebase avoids."""
    names = set()
    for card in cards.values():
        for kw in (card.get("keywords") or []):
            lowered = kw.lower()
            if KEYWORD_NAME_SHAPE_RE.match(lowered) and len(lowered.split()) <= 3:
                names.add(lowered)
    return frozenset(names)


def parse_pt_modifier(text):
    """"+2/+2" / "-1/-1" / "+0/+1" -> (power_delta, toughness_delta) ints,
    or None if text is None or doesn't match the closed +N/+N shape (e.g. a
    variable "+X/+X" grant -- left unparsed, not guessed at)."""
    if text is None:
        return None
    m = PT_MODIFIER_RE.match(text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def mana_symbols_numeric_value(cost_str: str) -> float:
    """Sums a bracketed mana-symbol cost string ("{2}{W}" -> 3.0) for
    RELATIVE-distance comparison purposes only, not rules-accurate mana
    value -- a purely-numeric symbol ("{2}") adds its number; any symbol
    containing a digit (hybrid, e.g. "{2/W}") adds the largest digit found
    (its minimum-payable numeric weight); any other symbol (a plain color
    or hybrid color-color pip) adds 1. Equip costs in the corpus are
    overwhelmingly plain generic numbers; this simple heuristic is not
    exercised on anything more exotic today, per EQUIP_COST_RE's own scope
    (see its comment)."""
    total = 0.0
    for sym in re.findall(r"\{([^}]+)\}", cost_str):
        if sym.isdigit():
            total += int(sym)
            continue
        digits = re.findall(r"\d+", sym)
        total += max(int(d) for d in digits) if digits else 1.0
    return total


def parse_equip_cost_value(face_text: str):
    """Extracts this face's Equip cost as a numeric value for relative-
    distance comparison (see mana_symbols_numeric_value), or None if this
    face has no Equip keyword line, or its cost isn't a plain mana-symbol
    cost EQUIP_COST_RE recognizes (e.g. "Equip—Sacrifice a creature", a
    non-mana cost -- left unparsed, not guessed at, same "uncertainty is
    not evidence of difference" convention as duration's own unknown
    case). Case-sensitive match against the RAW (pre-lowercasing) face
    text -- "Equip" only ever appears capitalized as a real keyword line,
    never inside ordinary sentence prose."""
    m = EQUIP_COST_RE.search(face_text)
    if not m:
        return None
    return mana_symbols_numeric_value(m.group(1))


def extract_granted_keyword_clause(paragraph: str, keyword_vocabulary: frozenset):
    """Parses an already-normalized (lowercased, reminder-stripped)
    matchable paragraph for the "grants a keyword set (and optionally a
    P/T buff) to some scope of creature(s)" idiom -- GENERALIZED
    (Captain's ruling, 2026-07-12) to two real subject-phrase templates,
    tried in sequence:

    1. Equipment/Aura: "Equipped/Enchanted creature gets +N/+N and
       has/have/gains KEYWORDS." (GRANT_CLAUSE_RE, unchanged since Entry
       #4) -- ALWAYS scope="single", duration_eot=False, PT-then-keyword
       order only (the only order this idiom is ever printed in). Tried
       FIRST; if it matches, the mass-pump branch below never runs.
    2. Mass-pump/anthem: "[other] creatures you control get(s)/gain(s)/
       has/have KEYWORDS[, where <letter> is <clause>][, until end of
       turn]." (GRANT_MASS_* constants) -- scope="all"|"other", either
       clause order, optional variable magnitude and "until end of turn"
       duration. Formerly a separate team_pump mechanism; folded in here
       (Entry #4's own comment already anticipated this exact extension:
       "'creatures you control have...' anthem phrasing was discussed but
       never measured this session, left for a future pass").

    Both branches converge on ONE fact shape, so a single cascade
    (granted_keyword_kinship_match()) and a single pool-seeding index
    (build_granted_keyword_index()) serve both -- a mass-pump match is now
    a real keyword_grant result, automatically inheriting Option C's
    boilerplate-shadowing rescue and pt_exactness_priority's categorical
    "exact beats near" sort guarantee, neither of which the standalone
    team_pump mechanism ever had.

    Conditional grants (CONDITIONAL_GRANT_MARKERS) are excluded from
    either shape, same reasoning both times -- see that constant's own
    comment. All-or-nothing keyword validation against keyword_vocabulary,
    same convention both shapes (the corpus-measured "false-positive idiom
    match" category from Entry #4's own audit, e.g. Compulsory Rest's
    `Enchanted creature has "{2}, Sacrifice this creature: ..."`, a
    granted ACTIVATED ABILITY in quotes, not a keyword list -- no partial
    credit for a clause that's part real keywords, part noise).

    Returns a fact dict or None: {"keywords": frozenset|None, "pt_mod":
    (power,toughness)|"variable"|None, "variable_definition": str|None,
    "scope": "single"|"all"|"other", "duration_eot": bool, "paragraph":
    str}. None if neither shape matches, or matches but has nothing to key
    kinship off of (no PT clause AND no valid keyword clause)."""
    if not paragraph:
        return None
    if any(marker in paragraph for marker in CONDITIONAL_GRANT_MARKERS):
        return None

    m = GRANT_CLAUSE_RE.match(paragraph)
    if m:
        pt_text, kw_text = m.group(1), m.group(2).rstrip(".")
        scope, duration_eot, variable_definition = "single", False, None
    else:
        stripped = GRANT_MASS_LEADING_JUNK_RE.sub("", paragraph)
        sm = GRANT_MASS_SUBJECT_RE.search(stripped)
        if not sm:
            return None
        if any(marker in stripped[:sm.start()] for marker in CONDITIONAL_GRANT_MARKERS):
            return None
        scope = "other" if sm.group(1) else "all"
        rest = sm.group(2).rstrip(".")
        duration_eot = " until end of turn" in rest
        rest = rest.replace(" until end of turn", "")
        variable_definition = None
        wm = GRANT_MASS_WHERE_RE.search(rest)
        if wm:
            variable_definition = wm.group(1).strip()
            rest = rest[:wm.start()]
        rest = rest.strip()

        pt_text = kw_text = None
        for regex, order in (
            (GRANT_MASS_PT_FIRST_RE, "pt_kw"),
            (GRANT_MASS_KW_FIRST_RE, "kw_pt"),
            (GRANT_MASS_PT_ONLY_RE, "pt"),
            (GRANT_MASS_KW_ONLY_RE, "kw"),
        ):
            mm = regex.match(rest)
            if not mm:
                continue
            if order == "pt_kw":
                pt_text, kw_text = mm.group(1), mm.group(2)
            elif order == "kw_pt":
                kw_text, pt_text = mm.group(1), mm.group(2)
            elif order == "pt":
                pt_text = mm.group(1)
            else:
                kw_text = mm.group(1)
            break
        else:
            return None

    keywords = None
    if kw_text:
        pieces = [p.strip() for p in re.split(r",\s*(?:and\s+)?|\s+and\s+", kw_text) if p.strip()]
        if not pieces:
            return None
        keywords = frozenset(pieces)
        if not keywords <= keyword_vocabulary:
            return None

    pt_mod = None
    if pt_text:
        literal = parse_pt_modifier(pt_text)
        if literal is not None:
            pt_mod = literal
        elif GRANT_MASS_VARIABLE_PT_RE.match(pt_text.lower()):
            pt_mod = "variable"
        # else: unparseable shape (e.g. a mismatched "+x/+y") -- left
        # unparsed, not guessed at.

    if pt_mod is None and keywords is None:
        return None

    return {
        "keywords": keywords, "pt_mod": pt_mod, "variable_definition": variable_definition,
        "scope": scope, "duration_eot": duration_eot, "paragraph": paragraph,
    }


def build_granted_keyword_facts(doc: dict, keyword_vocabulary: frozenset) -> list:
    """Per-card granted-keyword facts, one per qualifying paragraph across
    all faces -- mirrors mana_facts' shape (a list, even though in practice
    a single card rarely carries more than one or two). Called as a post-
    processing pass over already-built card_docs (mirrors build_mana_pip_index's
    call-after-card_docs pattern), not baked into build_card_doc itself,
    since it needs the corpus-wide keyword vocabulary which can only be
    known once every card's own `keywords` field has been seen."""
    facts = []
    for face in doc["faces"]:
        for paragraph in face["matchable_paragraphs"]:
            fact = extract_granted_keyword_clause(paragraph, keyword_vocabulary)
            if fact is not None:
                # Equip-cost delta term (Fable 5's recommendation,
                # 2026-07-10): carried from the SAME face the grant
                # clause itself came from -- an Equipment's own Equip
                # cost, not its casting cost (mv_delta, a different axis
                # already covered elsewhere in the rank formula). Always
                # None for a mass-pump fact (no card has both an Equip
                # line and a "creatures you control" grant on the same
                # face), no special-casing needed.
                fact["equip_cost_value"] = face["equip_cost_value"]
                facts.append(fact)
    return facts


def granted_keyword_kinship_match(anchor_doc: dict, candidate_doc: dict) -> list:
    """Scoped to GRANT_SIZE_CEILING (2) on both sides -- 3+-keyword grants
    are the corpus-measured 'keyword-soup' territory (Captain's own read:
    "it starts finding other cards that have keywords"), already covered
    by the existing Tagger tag, not this mechanism. ZERO shared keywords =
    NOT Tier 2 via this path (falls through to Tier 3 tags, same Option B
    precedent as mana kinship). `keywords` can be None (a PT-only fact,
    e.g. a plain anthem with no keyword grant) -- treated as empty, so
    such a fact can never actually produce a match here (nothing to share),
    but doesn't crash; it's a valid fact, just not a kinship signal this
    mechanism can use.

    Scope/duration mismatch (Captain's ruling, 2026-07-12, folding the
    former team_pump mechanism in here): flat terms, ZERO cost when both
    facts are the Equipment/Aura shape (scope always "single", duration_
    eot always False there) -- the pre-existing Equipment-vs-Equipment
    rank formula is therefore byte-identical to before this generalization.
    PT distance now has three shapes: literal/literal (unchanged, real
    point distance), variable/variable (0 if same defining clause, else
    GRANT_VARIABLE_MISMATCH_POINTS), or mixed (GRANT_MIXED_PT_MISMATCH_
    POINTS, not directly comparable) -- Equipment facts are never
    "variable" (GRANT_CLAUSE_RE's PT capture only matches literal digits),
    so this three-way branch also collapses to the original literal-only
    behavior for the Equipment case."""
    matches = []
    for a_fact in anchor_doc.get("granted_keyword_facts", []):
        a_kw = a_fact["keywords"] or frozenset()
        if not (1 <= len(a_kw) <= GRANT_SIZE_CEILING):
            continue
        for c_fact in candidate_doc.get("granted_keyword_facts", []):
            c_kw = c_fact["keywords"] or frozenset()
            if not (1 <= len(c_kw) <= GRANT_SIZE_CEILING):
                continue
            shared = a_kw & c_kw
            if not shared:
                continue
            extras = len((a_kw | c_kw) - shared)

            # Captain's ruling, 2026-07-10: P/T modifier mismatch, a
            # secondary cascade term -- a missing "gets X/Y" clause on
            # either side is a definitive +0/+0 (the oracle text
            # genuinely says nothing about a stat bonus, a known fact),
            # not treated as neutral/unknown. Extended 2026-07-12 for the
            # variable-magnitude case (see docstring above).
            a_pt, c_pt = a_fact["pt_mod"], c_fact["pt_mod"]
            if a_pt == "variable" and c_pt == "variable":
                pt_distance = (
                    0.0 if a_fact["variable_definition"] == c_fact["variable_definition"]
                    else GRANT_VARIABLE_MISMATCH_POINTS
                )
            elif a_pt == "variable" or c_pt == "variable":
                pt_distance = GRANT_MIXED_PT_MISMATCH_POINTS
            else:
                a_power, a_toughness = a_pt or (0, 0)
                c_power, c_toughness = c_pt or (0, 0)
                pt_distance = abs(a_power - c_power) + abs(a_toughness - c_toughness)

            # Equip-cost delta term (Fable 5's recommendation, 2026-07-10):
            # unlike the P/T-mod convention above, a MISSING/unparseable
            # equip cost on either side (None -- no Equip line at all, or a
            # non-mana-symbol cost like "Sacrifice a creature," or simply
            # not the Equipment shape at all) is genuinely UNKNOWN, not a
            # definitive value -- contributes zero penalty, same
            # "uncertainty is not evidence of difference" convention
            # duration/scope/exception already use elsewhere in this file.
            a_equip = a_fact["equip_cost_value"]
            c_equip = c_fact["equip_cost_value"]
            equip_cost_distance = abs(a_equip - c_equip) if a_equip is not None and c_equip is not None else 0.0

            scope_penalty_term = GRANT_SCOPE_MISMATCH_PENALTY if a_fact["scope"] != c_fact["scope"] else 0.0
            duration_penalty_term = (
                GRANT_DURATION_MISMATCH_PENALTY if a_fact["duration_eot"] != c_fact["duration_eot"] else 0.0
            )

            matches.append({
                "anchor_fact": a_fact, "candidate_fact": c_fact, "shared_keywords": shared,
                "pt_distance": pt_distance, "equip_cost_distance": equip_cost_distance,
                "penalty": (
                    GRANT_KEYWORD_MISMATCH_PENALTY * extras
                    + GRANT_PT_MISMATCH_PENALTY_PER_POINT * pt_distance
                    + GRANT_EQUIP_COST_PENALTY_PER_POINT * equip_cost_distance
                    + scope_penalty_term
                    + duration_penalty_term
                ),
            })
    return matches


def mana_pip_kinship_match(anchor_doc: dict, candidate_doc: dict) -> list:
    """R6 (Phase 4, ratified; gate widened by Captain ruling): ANY two
    mana-producing abilities sharing >=1 produced pip qualify Tier 2 --
    shape (source_class/repeatable) is NOT a qualification requirement,
    only a cascade-rank term (mana_cascade_penalty() -- see its own
    docstring for the 2026-07-12 amount/shape reweighting). This closes a
    real gap the original shape-gated version had:
    Dark Ritual (one-shot spell_effect, {B}{B}{B}) and Bog Witch
    (repeatable activated_tap, {B}{B}{B}) produce EXACTLY the same mana
    and share no viable text fragment (the core is 2-3 tokens, below the
    5-token floor) -- under the old shape gate neither mana kinship nor
    text matching could ever connect them. Purely colorless abilities on
    both sides qualify too (R6's "comparable amounts" path -- there's no
    color to share, ranked by amount closeness via the cascade). ZERO
    overlap = NOT T2 via this path (falls through to T3 tags, Option B).
    Returns ALL qualifying (anchor_fact, candidate_fact) pairs with each
    one's cascade penalty; assign_tier picks the best (lowest-penalty)
    match. Runs in PARALLEL with literal-text matching (R4) -- never
    called unless the text path already failed to find a better tier, so
    the measured guild-pair regression (same-pair literal-text sources
    collapsing under a hypothetical pip-normalization REPLACEMENT gate)
    cannot occur here by construction: this path only ever ADDS a
    candidate that text matching missed entirely."""
    matches = []
    for a_fact in anchor_doc.get("mana_facts", []):
        for c_fact in candidate_doc.get("mana_facts", []):
            a_colors, c_colors = a_fact["colors"], c_fact["colors"]
            if not a_colors and not c_colors:
                if a_fact["colorless_amount"] <= 0 or c_fact["colorless_amount"] <= 0:
                    continue
                shared_colors = frozenset()
            else:
                shared_colors = a_colors & c_colors
                if not shared_colors:
                    continue
            matches.append({
                "anchor_fact": a_fact, "candidate_fact": c_fact, "shared_colors": shared_colors,
                "penalty": mana_cascade_penalty(a_fact, c_fact),
            })
    return matches


def assign_tier(anchor_doc: dict, candidate_doc: dict, ngram_df: dict, clause_df: dict, keyword_df: dict,
                 paragraph_index: dict, args: argparse.Namespace):
    """Returns None if there's no verbatim overlap AND no keyword/mana/
    granted-keyword kinship (a Tier 3 candidate), else a dict:
    {"tier": int,
    "fragment": str|None, "fragment_df": int|None, "fragment_df_exact": bool,
    "evidence": str (display-formatted, notes included), "mechanism":
    "text"|"reminder"|"sentence"|"keyword"|"mana"|"keyword_grant"|
    "vanilla_creature",
    "keyword": str|None,
    "anchor_param": str|None, "candidate_param": str|None,
    "commonality_weight": float, "commonality_band": str|None,
    "anchor_mana_fact": dict|None, "candidate_mana_fact": dict|None,
    "mana_cascade_penalty": float|None, "anchor_granted_keyword_fact":
    dict|None, "candidate_granted_keyword_fact": dict|None,
    "granted_keyword_penalty": float|None, "extra_fragments": list[dict],
    "corroboration": list[dict]}. `corroboration` (2026-07-11, see the
    CORROBORATION_MIN_OTHER_WORDS constant) is populated for ANY Tier 1/2
    mechanism once the pair's own primary evidence already clears the
    word/specificity threshold -- display-only secondary evidence
    (short clauses below the n-gram floor in any DF band, or additional
    shared keywords beyond kinship_keyword), never fed into rank.
    The keyword_grant trio is populated ONLY for mechanism == "keyword_grant"
    (Entry #4, Captain's ruling 2026-07-10) -- same both-sides-carry shape
    as Phase 4's mana facts. `extra_fragments` (cumulative fragment
    scoring, 2026-07-10 ruling) is populated ONLY for a Tier 2 text/reminder
    match that has a second+ qualifying run in the same paragraph pair as
    the primary `fragment` -- each entry is {"text", "df", "df_exact",
    "length", "commonality_weight", "commonality_band", "run_weight"}, else
    []. `fragment`/`fragment_df` keep their original single-primary-run
    meaning unchanged; every downstream consumer that compares `fragment`
    against an exact string (gate checks) is unaffected by this field.
    `fragment`/`fragment_df` are populated for tiers 1/2 (used for v2.1
    rank scoring); Tier 0 leaves them None (sorts by
    name). The keyword/anchor_param/candidate_param trio is populated ONLY
    when mechanism == "keyword" (Phase 2c, ratified) -- both sides' kinship
    facts, not the anchor's alone. commonality_weight/commonality_band
    (Phase 3, ratified, R1/R2/R3) apply ONLY to the text/reminder mechanisms
    (Mechanism 1 keyword kinship has its own, separate DF floor and is
    unaffected) -- weight is 1.0 and band is None when they don't apply.

    v2.9: TWO qualification paths now run in PARALLEL with the original
    verbatim-text path, and the better (lower-numbered) tier wins, ties
    going to the text/reminder path:
      - Mechanism 1 (keyword kinship, keyword_kinship_match()): shared
        keyword, DF<=floor, same param -> Tier 1, different param -> Tier 2.
      - Mechanism 2 (reminder-text injection): a single-keyword line's
        reminder body is injected as an ordinary matchable paragraph on
        BOTH sides (see build_card_doc), so it flows through the SAME
        find_shared_paragraph/find_shared_fragment call below unchanged --
        no separate code path, just more paragraphs to search.
    NO-DOUBLE-COUNT: any keyword that qualifies via Mechanism 1 for this
    pair has its Mechanism-2 reminder paragraph excluded from THIS pair's
    text search (keyword identity wins) -- exclude_paragraphs below."""
    kinship_matches = keyword_kinship_match(anchor_doc, candidate_doc, keyword_df, args.ngram_df_floor)
    best_kinship = min(kinship_matches, key=lambda m: (m["tier"], m["df"])) if kinship_matches else None
    suppressed_keywords = {m["keyword"] for m in kinship_matches}
    exclude_paragraphs = (
        frozenset(p for p, kw in anchor_doc["reminder_keyword_by_paragraph"].items() if kw in suppressed_keywords)
        | frozenset(p for p, kw in candidate_doc["reminder_keyword_by_paragraph"].items() if kw in suppressed_keywords)
    )

    tier0_ok = (
        anchor_doc["composed_full_text"] and candidate_doc["composed_full_text"]
        and anchor_doc["composed_full_text"] == candidate_doc["composed_full_text"]
    )
    # Vanilla-creature Tier 0 (Captain's ruling, 2026-07-12): tier0_ok above
    # requires BOTH sides' composed_full_text to be truthy, so two creatures
    # with NO oracle text at all (a blank "2/2 for {1}{G}" bear) can never
    # satisfy it, however identical their frame -- "no text" was being read
    # as "nothing to compare," not as "the same nothing." A blank creature
    # IS its frame in its entirety; two that share one ARE functional
    # reprints of each other, the truest form of Tier 0. Deliberately a
    # SEPARATE flag, not a relaxation of tier0_ok itself: tier0_ok also
    # feeds the `elif tier0_ok: base = 1` fallback below for a text match
    # whose FRAME differs -- if two-blank-sides alone satisfied that flag,
    # every vanilla creature in the corpus would mint a false Tier 1 match
    # against every other one regardless of cost/stats (blank == blank is
    # trivially true for ANY two blank cards). vanilla_creature_match is
    # therefore ONLY ever checked alongside frame_signature equality (the
    # `if` immediately below), never on its own -- a frame MISMATCH between
    # two blank creatures falls through to no text-mechanism match at all,
    # same as today. Scoped to "Creature" per Captain's own wording, not
    # generalized to every blank permanent type -- frame_signature's own
    # type_line equality already means BOTH sides are creatures once this
    # AND that agree, so checking only the anchor side is sufficient.
    vanilla_creature_match = (
        not anchor_doc["composed_full_text"]
        and not candidate_doc["composed_full_text"]
        and "Creature" in type_bucket(anchor_doc["type_line"])
    )
    tier1_match = find_shared_paragraph(
        anchor_doc, candidate_doc, ngram_df, args.ngram_min_len, paragraph_index, exclude=exclude_paragraphs,
    )

    base = None
    fragment = None
    fragment_df = None
    fragment_df_exact = False
    note = ""
    evidence_core = None
    mechanism = "text"
    commonality_weight = 1.0
    commonality_band = None
    extra_fragments = []
    # Reminder-keyword provenance (Captain's ruling, 2026-07-12): which
    # keyword's injected reminder body the winning evidence came from,
    # None unless mechanism == "reminder" -- exposed as its own field
    # (not just embedded in the "[reminder: ...]" note string) so a
    # SECOND_CLASS_REMINDER_KEYWORDS-style demotion can key off the
    # keyword NAME directly, without deriving/hand-writing the exact
    # matched fragment text for each keyword Captain wants demoted.
    reminder_keyword_source = None

    # Phase 5 fix (CO-A's original design, corrected from Phase 3's first
    # pass): a T1 paragraph match in the RESCUE band (the explicitly
    # low-confidence "qualifies but buried" zone, long paragraphs only --
    # short paragraphs never have a rescue band, R3) does NOT stay Tier 1
    # -- it DEMOTES to the Tier 2 fragment path below, which independently
    # re-evaluates at the (shorter, possibly rarer) fragment level. Caught
    # by G-B: Swiftfoot Boots' equip reminder (rescue band, DF=64) was
    # wrongly minting 62 Tier 1 rows under the first Phase 3 pass. "full"
    # and "discounted" bands still stay Tier 1 (weight reduced, not
    # excluded) -- demoting "discounted" too broke the standing v2.2 Sol
    # Ring sanity gate: Sol Ring's own short "{t}: add {c}{c}." paragraph
    # (para_exact_df=19, discounted band) has no >=5-token fragment to
    # fall back to at all, so a blanket demotion would have dropped Mana
    # Crypt/Sol Talisman/Worn Powerstone out of Tier 1 entirely instead of
    # just de-weighting them.
    t1_eligible_match = tier1_match if tier1_match and tier1_match["band"] != "rescue" else None

    if (tier0_ok or vanilla_creature_match) and frame_signature(anchor_doc) == frame_signature(candidate_doc):
        base = 0
        evidence_core = (
            format_evidence_text(anchor_doc["composed_full_text"]) if tier0_ok
            else "(vanilla creature — no oracle text, frame match only)"
        )
    elif tier0_ok:
        base = 1
        fragment = (t1_eligible_match["text"] if t1_eligible_match else None) or anchor_doc["composed_full_text"]
        evidence_core = format_evidence_text(fragment)
        note = f" [frame gate failed: {', '.join(frame_mismatch_fields(anchor_doc, candidate_doc))}]"
        if t1_eligible_match:
            commonality_weight = t1_eligible_match["weight"]
            commonality_band = t1_eligible_match["band"]
    elif vanilla_creature_match and "Creature" in type_bucket(candidate_doc["type_line"]):
        # Vanilla-creature frame MISMATCH (Captain's ruling, 2026-07-12,
        # generalizing Entry #12): the same "identical text, different
        # frame -> Tier 1, buried by rank" shape as the tier0_ok elif just
        # above, for the empty-text case tier0_ok itself can never satisfy
        # (composed_full_text is falsy on both sides here, so tier0_ok is
        # False by construction). A blank creature IS its frame in its
        # entirety -- two that DON'T share one are still both "no text
        # at all," the truest possible verbatim match, just a weaker kin
        # once cost/type/P-T diverge. Deliberately never demoted further
        # than Tier 1 regardless of how far the frame drifts (Scaled Wurm
        # vs Grizzly Bears included) -- same precedent as tier0_ok's own
        # fallback, which doesn't scale its tier by mismatch severity
        # either; mv_term/ci_step/affinity (all unconditional, generic
        # rank terms already) are what separate a near-frame sibling from
        # a distant one, not the tier itself. Candidate-side "Creature"
        # check is required here (vanilla_creature_match only checks the
        # ANCHOR side, since the Tier 0 `if` above relies on frame_signature
        # equality to guarantee both sides agree -- that guarantee doesn't
        # hold once frames are allowed to differ).
        base = 1
        mechanism = "vanilla_creature"
        fragment = "vanilla creature — no oracle text"
        evidence_core = (
            f"{fragment} (frame mismatch: "
            f"{', '.join(frame_mismatch_fields(anchor_doc, candidate_doc))})"
        )
    elif t1_eligible_match:
        base = 1
        fragment = t1_eligible_match["text"]
        evidence_core = format_evidence_text(fragment)
        commonality_weight = t1_eligible_match["weight"]
        commonality_band = t1_eligible_match["band"]
    else:
        # Phase 3 (ratified, R3): the hard NGRAM_DF_FLOOR ceiling is replaced
        # by T2_RESCUE_CEILING (172) so the Lane 1c six can qualify, buried --
        # banding (full/discounted/rescue) happens below, same as Tier 1.
        # Cumulative fragment scoring (2026-07-10 ruling): find_shared_fragments
        # returns ALL qualifying non-overlapping runs within this same best
        # pair, not just the longest. runs[0] (the primary/longest) keeps
        # `fragment`/`fragment_df`/`fragment_df_exact` meaning EXACTLY what
        # they meant before this change -- every exact-string-equality gate
        # check (BOROS_CHARM_HEADER_TEXT, SWIFTFOOT_EQUIP_TEXT,
        # FAITHLESS_FLASHBACK_TEXT, MYREL_BETTER_FRAGMENT, etc.) keeps
        # comparing against the same single primary string, unaffected by
        # whether extra runs exist. runs[1:] are new: each gets its own
        # DF/band/weight (a common 2nd run can't cheaply inflate rank) and
        # is surfaced ONLY via the new `extra_fragments` list + evidence
        # text -- nothing else about the primary run's shape changes.
        runs = find_shared_fragments(
            anchor_doc, candidate_doc, ngram_df, args.ngram_min_len, T2_RESCUE_CEILING,
            exclude=exclude_paragraphs,
        )
        if runs:
            text, df, length = runs[0]
            base = 2
            fragment = text
            fragment_df = df
            fragment_df_exact = (length == args.ngram_min_len)
            marker = "=" if fragment_df_exact else "≈"
            evidence_core = f"{format_evidence_text(text)} (DF{marker}{df})"
            band = band_for_df(df, T2_FULL_WEIGHT_CEILING, T2_DISCOUNT_CEILING, T2_RESCUE_CEILING)
            both_injected = fragment_both_sides_injected(text, anchor_doc, candidate_doc)
            commonality_weight = PROVENANCE_DISCOUNT_WEIGHT if both_injected else BAND_WEIGHTS[band]
            commonality_band = band

            for r_index, (r_text, r_df, r_length) in enumerate(runs[1:], start=1):
                r_df_exact = (r_length == args.ngram_min_len)
                r_marker = "=" if r_df_exact else "≈"
                r_band = band_for_df(r_df, T2_FULL_WEIGHT_CEILING, T2_DISCOUNT_CEILING, T2_RESCUE_CEILING)
                r_both_injected = fragment_both_sides_injected(r_text, anchor_doc, candidate_doc)
                r_weight = PROVENANCE_DISCOUNT_WEIGHT if r_both_injected else BAND_WEIGHTS[r_band]
                extra_fragments.append({
                    "text": r_text, "df": r_df, "df_exact": r_df_exact, "length": r_length,
                    "commonality_weight": r_weight, "commonality_band": r_band,
                    "run_weight": fragment_run_weight(r_index),
                })
                evidence_core += f" + {format_evidence_text(r_text)} (DF{r_marker}{r_df})"

    kinship_keyword = None
    kinship_anchor_param = None
    kinship_candidate_param = None
    if best_kinship is not None and (base is None or best_kinship["tier"] < base):
        base = best_kinship["tier"]
        mechanism = "keyword"
        kw = best_kinship["keyword"]
        param_a = best_kinship["anchor_param"]
        param_c = best_kinship["candidate_param"]
        kinship_keyword = kw
        kinship_anchor_param = param_a
        kinship_candidate_param = param_c
        # Phase 2c (ratified): both sides' params, not the anchor's alone --
        # the same "mobilize 2 vs mobilize 1" precedent as the READY-TO-SHIP
        # display note. Equal params (the Tier 1 same-param case) collapse to
        # one mention since "X vs X" would be redundant.
        if param_a and param_c and param_a != param_c:
            fragment = f"{kw} {param_a} vs {kw} {param_c}"
        else:
            fragment = f"{kw} {param_a}".strip() if param_a else kw
        fragment_df = best_kinship["df"]
        fragment_df_exact = True
        evidence_core = f"keyword kinship: {fragment} (DF={best_kinship['df']})"
        note = ""
        # Mechanism 1 has its own, separate DF-floor discipline (keyword_df,
        # unaffected by R1/R3) -- band weighting is text/reminder-mechanism
        # scope only, never applied to a keyword-kinship win.
        commonality_weight = 1.0
        commonality_band = None
    elif fragment is not None:
        # The short whole-sentence path (last in the cascade, after
        # keyword_grant/mana) runs AFTER this block and sets its own
        # "sentence" mechanism label directly -- never relabeled to
        # "reminder" here, since it hasn't fired yet at this point.
        reminder_kw = find_reminder_attribution(fragment, anchor_doc, candidate_doc)
        if reminder_kw is not None:
            mechanism = "reminder"
            reminder_keyword_source = reminder_kw
            note += f" [reminder: {reminder_kw}]"

    def format_grant_evidence(best_grant: dict) -> tuple:
        """Shared by both call sites below -- builds (fragment, evidence)
        for a keyword_grant win. Not a method; a closure is fine here since
        neither call site needs it past this function."""
        anchor_fact = best_grant["anchor_fact"]
        candidate_fact = best_grant["candidate_fact"]
        shared_desc = "/".join(sorted(best_grant["shared_keywords"]))
        grant_fragment = f"granted-keyword kinship: {shared_desc}"

        def pt_display(pt_mod):
            # 2026-07-12: pt_mod can now be the sentinel "variable" (a
            # mass-pump "+X/+X" grant) in addition to a literal tuple or
            # None -- unpacking "variable" as if it were a 2-tuple would
            # raise (it's an 8-character string), so it needs its own case.
            if pt_mod == "variable":
                return "+x/+x"
            power, toughness = pt_mod or (0, 0)
            return f"{power:+d}/{toughness:+d}"

        a_pt = anchor_fact["pt_mod"]
        c_pt = candidate_fact["pt_mod"]
        pt_note = ""
        if a_pt is not None or c_pt is not None:
            pt_note = f", {pt_display(a_pt)} vs {pt_display(c_pt)}"
        # Equip-cost delta term (Fable 5's recommendation, 2026-07-10):
        # shown only when BOTH sides parsed a numeric equip cost -- same
        # "don't display what wasn't compared" convention as the P/T note
        # above, which only appears when at least one side HAS a pt_mod.
        equip_note = ""
        a_equip = anchor_fact["equip_cost_value"]
        c_equip = candidate_fact["equip_cost_value"]
        if a_equip is not None and c_equip is not None:
            equip_note = f", equip {a_equip:g} vs equip {c_equip:g}"
        # Scope/duration (2026-07-12, the mass-pump generalization): only
        # shown when at least one side isn't the plain single-target-
        # permanent Equipment/Aura shape -- keeps existing Equipment
        # evidence strings byte-identical to before this change, only the
        # mass-pump (or a cross-shape) case gets the extra context.
        scope_note = ""
        if anchor_fact["scope"] != "single" or candidate_fact["scope"] != "single":
            scope_note = f", scope {anchor_fact['scope']} vs {candidate_fact['scope']}"
        duration_note = ""
        if anchor_fact["duration_eot"] or candidate_fact["duration_eot"]:
            a_dur = "eot" if anchor_fact["duration_eot"] else "permanent"
            c_dur = "eot" if candidate_fact["duration_eot"] else "permanent"
            duration_note = f", duration {a_dur} vs {c_dur}"
        grant_evidence = (
            f"granted-keyword kinship: {shared_desc}{pt_note}{equip_note}{scope_note}{duration_note} "
            f"(mismatch penalty={best_grant['penalty']:.2f})"
        )
        return grant_fragment, grant_evidence

    # Entry #4 (Captain's ruling, 2026-07-10): granted-keyword-SET kinship,
    # PARALLEL to text/keyword matching -- same "only fires when nothing
    # else qualified this pair" gating as mana kinship below, checked FIRST
    # (deterministic tie-break: a shared functional grant is a closer,
    # more specific similarity signal than incidental mana overlap, in the
    # rare case both could apply to the same pair).
    granted_kw_anchor_fact = None
    granted_kw_candidate_fact = None
    granted_kw_penalty_value = None
    granted_kw_pt_distance = None
    if base is None:
        grant_matches = granted_keyword_kinship_match(anchor_doc, candidate_doc)
        # Captain's ruling, 2026-07-10: "exact buff gets priority, then near
        # buffs" -- when a pair has multiple qualifying fact combinations,
        # prefer the one with the closest P/T match FIRST, keyword-mismatch
        # penalty only as a tie-break among equally-close P/T candidates.
        best_grant = (
            min(grant_matches, key=lambda m: (m["pt_distance"], m["penalty"])) if grant_matches else None
        )
        if best_grant is not None:
            base = 2
            mechanism = "keyword_grant"
            granted_kw_anchor_fact = best_grant["anchor_fact"]
            granted_kw_candidate_fact = best_grant["candidate_fact"]
            granted_kw_penalty_value = best_grant["penalty"]
            granted_kw_pt_distance = best_grant["pt_distance"]
            fragment, evidence_core = format_grant_evidence(best_grant)
            note = ""
    elif base == 2 and mechanism in ("text", "reminder"):
        # mechanism can only be "text"/"reminder" here, never "sentence" --
        # the short-sentence path (below, gated `if base is None`) runs
        # AFTER this block in the cascade (last-resort, after keyword_grant
        # and mana both), so it cannot have set `mechanism` yet at this point.
        # base == 2 specifically (not just "not None"): Tier 0/1 matches
        # (base 0/1) must never be reconsidered by a Tier 2 mechanism, and
        # a Tier 0 match in particular never sets `fragment` at all (stays
        # at its None initial value) -- checking `base is None`'s negation
        # alone let this branch wrongly fire for Tier 0 rows and crash on
        # fragment_both_sides_injected(None, ...) (caught by the corpus-
        # wide re-measurement below, fixed before shipping).
        #
        # Fable 5's Option C (ratified, 2026-07-10, REMINDER-TEXT-
        # QUALIFICATION-CASCADE-ISSUE.md): the text/reminder path already
        # claimed this pair (base is not None) -- but if its ENTIRE winning
        # evidence (the primary fragment AND every cumulative-scoring extra
        # run, Entry #5) is both-sides-M2-injected boilerplate (the SAME
        # PROVENANCE_DISCOUNT_WEIGHT=0.01-near-worthless category Entry #6
        # already discounts hard), a genuinely qualifying keyword_grant
        # match is categorically stronger evidence and should win outright
        # -- not a scalar comparison (the engine has already ruled
        # boilerplate is near-worthless; inventing a DF-vs-grant-penalty
        # metric to reconfirm that would be pointless). If even ONE run is
        # genuine non-boilerplate text, this does NOT fire -- confirmed by
        # corpus measurement that genuine text matches (e.g. Behemoth
        # Sledge vs Unflinching Courage, DF~2) vastly outnumber pure-
        # boilerplate shadowing (587 vs 71 pairs) and must keep winning.
        all_runs_boilerplate = fragment_both_sides_injected(fragment, anchor_doc, candidate_doc) and all(
            fragment_both_sides_injected(extra["text"], anchor_doc, candidate_doc)
            for extra in extra_fragments
        )
        if all_runs_boilerplate:
            grant_matches = granted_keyword_kinship_match(anchor_doc, candidate_doc)
            best_grant = (
                min(grant_matches, key=lambda m: (m["pt_distance"], m["penalty"])) if grant_matches else None
            )
            if best_grant is not None:
                displaced_evidence = evidence_core
                mechanism = "keyword_grant"
                granted_kw_anchor_fact = best_grant["anchor_fact"]
                granted_kw_candidate_fact = best_grant["candidate_fact"]
                granted_kw_penalty_value = best_grant["penalty"]
                granted_kw_pt_distance = best_grant["pt_distance"]
                fragment, grant_evidence = format_grant_evidence(best_grant)
                # Fold in Option D's evidence idea (Fable 5): don't just
                # silently swap the winner -- show what was displaced, so
                # the report/viewer stays maximally informative rather than
                # erasing the boilerplate match's own DF entirely.
                evidence_core = f"{grant_evidence} [also matched: {displaced_evidence}]"
                note = ""
                commonality_weight = 1.0
                commonality_band = None
                fragment_df = None
                fragment_df_exact = False
                extra_fragments = []

    # Phase 4 (ratified, R4/R6): mana-pip kinship, PARALLEL to text/keyword
    # matching -- only ever fires when nothing else qualified this pair at
    # all (base is still None). R6: mana kinship is Tier 2 only, never
    # Tier 0/1, so it can never override an already-better tier; ties
    # never arise since it only runs in the None case.
    mana_anchor_fact = None
    mana_candidate_fact = None
    mana_cascade_penalty_value = None
    if base is None:
        mana_matches = mana_pip_kinship_match(anchor_doc, candidate_doc)
        best_mana = min(mana_matches, key=lambda m: m["penalty"]) if mana_matches else None
        if best_mana is not None:
            base = 2
            mechanism = "mana"
            mana_anchor_fact = best_mana["anchor_fact"]
            mana_candidate_fact = best_mana["candidate_fact"]
            mana_cascade_penalty_value = best_mana["penalty"]
            shared_desc = (
                "/".join(sorted(c.upper() for c in best_mana["shared_colors"]))
                if best_mana["shared_colors"] else "colorless"
            )
            fragment = f"mana kinship: {shared_desc}"
            evidence_core = f"mana kinship: {shared_desc} (cascade penalty={best_mana['penalty']:.2f})"
            note = ""

    # Short whole-sentence identity path (Fable 5's recommendation,
    # EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md Section 4c,
    # 2026-07-10, ratified): find_shared_fragments() can never qualify a
    # matched clause shorter than NGRAM_MIN_LEN tokens -- see
    # find_shared_sentence()'s own docstring. Placed LAST in the cascade,
    # after keyword_grant and mana kinship both -- caught corpus-measuring
    # this path's own impact before shipping: an earlier draft placed it
    # right where the text/reminder path leaves `base` at None, which let
    # it claim Sol Ring vs Ancient Tomb's pair (both share the exact short
    # sentence "{t}: add {c}{c}") BEFORE mana kinship's own specialized,
    # richer cascade (amount/color/shape comparison, R5/R6) ever got a
    # chance -- failing check_gg_sol_ring_cascade_gate (expected
    # mechanism=mana, got mechanism=sentence). Mana kinship and
    # keyword_grant are purpose-built, richer mechanisms for their own
    # domains (mana abilities; Equipment/Aura keyword grants); the
    # sentence path is a generic catch-all with no domain-specific
    # cascade of its own, so it belongs at the END of the "only fires if
    # nothing else found anything" chain, not competing with them for
    # position. Its own motivating cases (Anguished Unmaking, Inevitable
    # Defeat vs Utter End/Vanish into Eternity) have no mana facts and no
    # granted-keyword facts at all, so this reordering costs them nothing.
    if base is None:
        sentence_match = find_shared_sentence(
            anchor_doc, candidate_doc, clause_df, args.ngram_min_len, T2_RESCUE_CEILING,
            exclude=exclude_paragraphs,
        )
        if sentence_match is not None:
            text, df = sentence_match
            base = 2
            fragment = text
            fragment_df = df
            fragment_df_exact = True  # clause_df is an EXACT corpus-wide count, never a windowed approximation
            mechanism = "sentence"
            evidence_core = f"{format_evidence_text(text)} (DF={df})"
            band = band_for_df(df, T2_FULL_WEIGHT_CEILING, T2_DISCOUNT_CEILING, T2_RESCUE_CEILING)
            both_injected = fragment_both_sides_injected(text, anchor_doc, candidate_doc)
            commonality_weight = PROVENANCE_DISCOUNT_WEIGHT if both_injected else BAND_WEIGHTS[band]
            commonality_band = band
            note = ""

    if base is None:
        return None

    anchor_types = type_bucket(anchor_doc["type_line"])
    candidate_types = type_bucket(candidate_doc["type_line"])
    if types_disjoint_for_demotion(anchor_types, candidate_types):
        demoted_from = base
        base = min(base + 1, 2)
        if base != demoted_from:
            note += f" [demoted: disjoint type — {sorted(anchor_types)} vs {sorted(candidate_types)}]"

    # Secondary corroboration (Captain's ruling, 2026-07-11): only for Tier
    # 1/2 (Tier 0 is already the strongest possible match -- full-text+
    # frame equality -- corroboration adds nothing there and fragment is
    # always None for it anyway). "Enough OTHER evidence" (CORROBORATION_
    # MIN_OTHER_WORDS words) is measured from the WINNING fragment for the
    # text-shaped mechanisms (text/reminder/sentence) -- text/reminder
    # always already clear it (NGRAM_MIN_LEN is itself the same number),
    # but the sentence mechanism's own primary win can be as short as the
    # fragment itself, so a pair whose ONLY connection is already a
    # sub-floor clause does not additionally unlock corroboration on top
    # of it. Structured kinship mechanisms (keyword/mana/keyword_grant)
    # have no natural word count -- each already carries its own
    # independent DF/rarity discipline, so they're treated as
    # unconditionally "specific enough."
    corroboration = []
    if base in (1, 2):
        if mechanism in ("text", "reminder", "sentence"):
            other_words = (len(fragment.split()) if fragment else 0) + sum(
                len(ef["text"].split()) for ef in extra_fragments
            )
        else:
            other_words = CORROBORATION_MIN_OTHER_WORDS
        if other_words >= CORROBORATION_MIN_OTHER_WORDS:
            exclude_texts = frozenset({fragment} | {ef["text"] for ef in extra_fragments}) if fragment else frozenset()
            clause_matches = find_clause_corroboration(
                anchor_doc, candidate_doc, clause_df, args.ngram_min_len,
                exclude_paragraphs=exclude_paragraphs, exclude_texts=exclude_texts,
            )[:CORROBORATION_MAX_SHOWN_PER_KIND]
            for text, df in clause_matches:
                corroboration.append({"kind": "clause", "text": text, "df": df})

            # Every keyword_kinship_match() hit OTHER than the one already
            # used as this pair's primary evidence (kinship_keyword is None
            # unless mechanism == "keyword", so when some other mechanism
            # won, EVERY entry in kinship_matches is corroboration-eligible
            # -- Captain's own framing: "keywords on their own metric do
            # not contribute [to rank]. but after enough similarity they
            # do contribute" -- to the displayed evidence, never the score.
            kw_matches = sorted(
                (m for m in kinship_matches if m["keyword"] != kinship_keyword),
                key=lambda m: (m["tier"], m["df"]),
            )[:CORROBORATION_MAX_SHOWN_PER_KIND]
            for m in kw_matches:
                corroboration.append({
                    "kind": "keyword", "keyword": m["keyword"],
                    "anchor_param": m["anchor_param"], "candidate_param": m["candidate_param"], "df": m["df"],
                })

            if corroboration:
                def _corroboration_label(c):
                    if c["kind"] == "clause":
                        return f"{format_evidence_text(c['text'])} (DF={c['df']})"
                    kw_text = f"{c['keyword']} {c['anchor_param']}" if c["anchor_param"] else c["keyword"]
                    return f"{kw_text} (DF={c['df']})"
                shown = "; ".join(
                    _corroboration_label(c)
                    for c in corroboration
                )
                note += f" [also: {shown}]"

    return {
        "tier": base,
        "fragment": fragment,
        "fragment_df": fragment_df,
        "fragment_df_exact": fragment_df_exact,
        "evidence": evidence_core + note,
        "mechanism": mechanism,
        # Phase 2c (ratified): both-sides kinship facts, None for the
        # text/reminder mechanisms -- Phase 4's mana-kinship rows reuse this
        # same shape.
        "keyword": kinship_keyword,
        "anchor_param": kinship_anchor_param,
        "candidate_param": kinship_candidate_param,
        "commonality_weight": commonality_weight,
        "commonality_band": commonality_band,
        # Phase 4 (ratified, R6): both sides' mana facts, None unless
        # mechanism == "mana" -- same both-sides-carry precedent as Phase 2c.
        "anchor_mana_fact": mana_anchor_fact,
        "candidate_mana_fact": mana_candidate_fact,
        "mana_cascade_penalty": mana_cascade_penalty_value,
        "extra_fragments": extra_fragments,
        # Secondary corroboration (2026-07-11): display-only, NEVER fed
        # into compute_rank/extra_fragment_terms/kinship_keyword -- see the
        # CORROBORATION_MIN_OTHER_WORDS constant's own comment for why this
        # is a separate field rather than more extra_fragments entries
        # (frame-affinity restoration must never partially revive a DEAD
        # clause's rank credit, and a corroborating keyword must never be
        # mistaken for the pair's own kinship_keyword winner downstream).
        # Each entry is {"kind": "clause", "text", "df"} or {"kind":
        # "keyword", "keyword", "anchor_param", "candidate_param", "df"}.
        "corroboration": corroboration,
        # Entry #4 (Captain's ruling, 2026-07-10): both sides' granted-
        # keyword facts, None unless mechanism == "keyword_grant" -- same
        # both-sides-carry precedent as Phase 2c/Phase 4.
        "anchor_granted_keyword_fact": granted_kw_anchor_fact,
        "candidate_granted_keyword_fact": granted_kw_candidate_fact,
        "granted_keyword_penalty": granted_kw_penalty_value,
        "granted_keyword_pt_distance": granted_kw_pt_distance,
        # Reminder-keyword provenance (2026-07-12): None unless mechanism
        # == "reminder" -- see reminder_keyword_source's own comment above.
        "reminder_keyword": reminder_keyword_source,
    }


def tier3_score(anchor_tags: list, candidate_tags: list, idf: dict, inherited_discount: float):
    anchor_by_slug = {t["slug"]: t for t in anchor_tags}
    candidate_by_slug = {t["slug"]: t for t in candidate_tags}

    def factor(direct: bool) -> float:
        return 1.0 if direct else inherited_discount

    total_anchor_weight = sum(
        idf.get(slug, 0.0) * factor(t["direct"]) for slug, t in anchor_by_slug.items()
    )
    if total_anchor_weight <= 0:
        return 0.0, []

    matched = []
    matched_weight = 0.0
    for slug, at in anchor_by_slug.items():
        ct = candidate_by_slug.get(slug)
        if ct is None:
            continue
        w = idf.get(slug, 0.0) * factor(at["direct"]) * factor(ct["direct"])
        matched_weight += w
        matched.append({
            "slug": slug,
            "idf": idf.get(slug, 0.0),
            "anchor_direct": at["direct"],
            "candidate_direct": ct["direct"],
            "weight": w,
        })

    matched.sort(key=lambda m: (-m["weight"], m["slug"]))
    return matched_weight / total_anchor_weight, matched


def format_evidence_text(text: str, max_len: int = 180) -> str:
    text = text.replace("\n", " / ").replace("|", "\\|")
    if len(text) > max_len:
        text = text[: max_len].rstrip() + "…"
    return text


def format_tier3_evidence(matched: list, top_n: int = 3) -> str:
    parts = []
    for m in matched[:top_n]:
        directness = "direct" if m["anchor_direct"] and m["candidate_direct"] else "inherited"
        parts.append(f"{m['slug']} (idf={m['idf']:.2f}, {directness})")
    extra = f" +{len(matched) - top_n} more" if len(matched) > top_n else ""
    return ", ".join(parts) + extra


# ---------------------------------------------------------------------------
# v2.6 amendment 1 -- Tier 2 corroboration gate
# ---------------------------------------------------------------------------
#
# AMENDS standing ruling 6 ("qualification stays maximal, rank buries, never
# excludes"). Exclusion is now permitted under exactly ONE condition: a
# fragment-qualified Tier 2 candidate whose polarity is a functional
# INVERSION of the anchor's (the existing polarity extractor's own output --
# not re-derived) AND which shares literally ZERO tag DNA with the anchor
# (the same computation feeding the 3.0*tag_score rank term) is disqualified
# outright, not merely buried. Rationale (Captain): verbatim grammar across
# a functional inversion with zero tag corroboration is phrase coincidence,
# not kinship -- rank-burial assumed some residual signal was worth keeping
# visible; corroboration_gate says there's nothing there to bury, only
# noise. Tier 1 is untouched (same MV/frame proximity as Tier 0 makes a
# Tier 1 polarity flip a much rarer, more deliberate signal already).

def tier2_corroboration_disqualified(fact_penalties: dict, tag_score: float) -> bool:
    return bool(fact_penalties["polarity_mismatch"]) and tag_score == 0.0


# ---------------------------------------------------------------------------
# v2.6 amendment 2 -- rule:turn-scoped tag (Tier 3 scoring ONLY)
# ---------------------------------------------------------------------------
#
# New engine-derived (rule:-provenance) tag detecting turn-window asymmetry:
# an ability that behaves differently depending on WHOSE turn it currently
# is ("during your turn", "on your turn", "only during their turn(s)",
# "during its controller's turn", etc.) as an ONGOING condition -- distinct
# from pure DURATION phrases ("until end of turn", "until your next turn"),
# which are already a separate fact (face_duration) and must not be
# double-counted here. "next turn"/"last turn" variants are deliberately
# excluded too: they name a SPECIFIC adjacent turn (a scheduling/duration-
# adjacent reference), not the recurring per-turn asymmetry this tag
# targets -- the same reasoning that excludes "until your next turn".
#
# The change order's own example family ("during your turn", "during their
# controllers' turn(s)", "during their own turns", "only during your/their
# turn(s)", "on your turn") reads as illustrative of the CONCEPT, not a
# literal regex -- e.g. Defense Grid's actual oracle text is "except during
# its controller's turn" (third person "its", not "their"), which the
# family's literal wording wouldn't catch. The pattern below was derived by
# scanning data/raw/oracle-cards.jsonl.gz for every "(only )?(during|on) ...
# turns?" window, eyeballing the real corpus distribution (a 60-phrase
# frequency dump), and generalizing to the person-reference forms actually
# used in templating: your/their(own), an/each/any opponent's, each/any/that
# player's, and its/their/that player's controller('s). Generic non-person
# mentions ("during a turn", "during any turn", "during that turn", "on this
# turn") are excluded on purpose -- they don't encode an asymmetry between
# whose turn it is, so they're not this fact. Verified zero false hits on
# "until"-prefixed duration phrasing (checked programmatically, not just by
# construction) -- see run_turn_scoped_derivation's printed diagnostics for
# the corpus DF and a random sample, per the change order's "eyeball before
# scoring" instruction.
TURN_SCOPED_TAG_SLUG = "rule:turn-scoped"
TURN_SCOPED_RE = re.compile(
    r"\b(?:only\s+)?(?:during|on)\s+"
    r"(?:"
    r"(?:each\s+of\s+)?(?:your|their)(?:\s+own)?"
    r"|(?:an?\s+|each\s+|any\s+)?opponent'?s"
    r"|(?:each\s+|any\s+|that\s+)?player'?s"
    r"|(?:its|their|that\s+player'?s)\s+controller(?:'s|s')?"
    r")\s+turns?\b"
)
TURN_SCOPED_SAMPLE_SIZE = 20
TURN_SCOPED_SAMPLE_SEED = 20260706  # fixed (today's date) -- determinism gate requires a stable "random" sample


def find_turn_scoped_matches(card_docs: dict) -> dict:
    """oracle_id -> matched phrase, for every card whose composed (self-name-
    substituted, reminder-stripped, lowercased) full text contains a
    turn-window-asymmetry phrase. Runs against ALL cards, tagged or not --
    this is an engine-derived fact, not sourced from the Tagger index."""
    matches = {}
    for oracle_id in sorted(card_docs):
        m = TURN_SCOPED_RE.search(card_docs[oracle_id]["composed_full_text"])
        if m:
            matches[oracle_id] = m.group(0)
    return matches


def run_turn_scoped_derivation(card_docs: dict, n_total_cards: int) -> tuple:
    """Prints the regex, corpus DF, computed idf, and a fixed-seed 20-card
    random sample for eyeball review -- BEFORE any Tier 3 scoring uses it,
    per the change order. Returns (matches dict, idf value) for injection
    into the Tier-3-only extended tag index."""
    print("\nv2.6 amendment 2 -- rule:turn-scoped derivation (Tier 3 scoring ONLY):")
    print(f"  regex: {TURN_SCOPED_RE.pattern}")
    matches = find_turn_scoped_matches(card_docs)
    df = len(matches)
    idf = math.log(n_total_cards / df) if df > 0 else 0.0
    print(f"  corpus DF = {df:,} / {n_total_cards:,} cards, idf = log({n_total_cards}/{df}) = {idf:.2f}")
    sample_ids = random.Random(TURN_SCOPED_SAMPLE_SEED).sample(
        sorted(matches), min(TURN_SCOPED_SAMPLE_SIZE, len(matches))
    )
    print(f"  {len(sample_ids)}-card random sample (seed={TURN_SCOPED_SAMPLE_SEED}, for eyeball review):")
    for oracle_id in sorted(sample_ids, key=lambda oid: card_docs[oid]["name"]):
        print(f"    {card_docs[oracle_id]['name']}: {matches[oracle_id]!r}")
    return matches, idf


def build_turn_scoped_tag_index(card_docs: dict, card_tags: dict, base_idf: dict,
                                 turn_scoped_matches: dict, turn_scoped_idf: float) -> tuple:
    """Tier-3-ONLY extended tag index: base card_tags/idf plus a synthetic
    rule:turn-scoped entry on every matching card (including cards the
    Tagger never tagged at all). base_idf's existing slugs are copied
    UNCHANGED -- only the new slug's idf is added -- so this never perturbs
    any other tag's weight or drifts Tier 3 scores for anchors that don't
    touch turn-window text at all. Deliberately NOT merged into the base
    card_tags/idf used for Tier 1/2 rank or the v2.6 amendment 1
    corroboration check (see TIER-ENGINE-V2.6-CHANGE-ORDER.md amendment 2:
    "Do NOT feed it into Tier 2's tag_score term this round")."""
    card_tags_t3 = {}
    for oracle_id in card_docs:
        entries = list(card_tags.get(oracle_id, []))
        if oracle_id in turn_scoped_matches:
            entries = entries + [{"slug": TURN_SCOPED_TAG_SLUG, "direct": True, "weight": "engine"}]
        if entries:
            card_tags_t3[oracle_id] = entries
    idf_t3 = dict(base_idf)
    idf_t3[TURN_SCOPED_TAG_SLUG] = turn_scoped_idf
    return card_tags_t3, idf_t3


# ---------------------------------------------------------------------------
# v2.3 per-ability/per-face facts: scope, duration, exception
# ---------------------------------------------------------------------------

def locate_fragment_context(doc: dict, fragment: str) -> tuple:
    """Returns (paragraph, face_type_line) for the first face/paragraph
    containing `fragment` as an exact match (Tier 1) or substring (Tier 2).

    BUG FIX (found by Fable 5 reviewing EQUIPMENT-REMINDER-AND-WEIGHTING-
    DELIBERATION.md, 2026-07-10): comparison is now against a period-
    normalized reconstruction of each paragraph
    (normalize_paragraph_for_fragment_comparison -- the same CO-C
    per-token period-stripping convention `fragment` itself was already
    built under), not the raw paragraph. The old raw comparison broke
    across any internal sentence boundary within a multi-sentence
    paragraph -- same bug class Entry #6 already fixed for
    fragment_both_sides_injected()/text_injected_on_side(), just a missed
    call site here. Measured impact: 87/484 (18%) of Tier 2 text/reminder
    rows across the 6 default calibration anchors previously returned
    (None, None) here, silently disabling ALL FIVE downstream fact
    penalties (scope/duration/exception/polarity/condition) for those
    rows -- not a partial miss, a total one, since every caller
    (compute_fact_penalties) treats "unknown" as "never penalize."
    The RAW paragraph (periods intact) is still what's returned -- every
    downstream consumer (extract_scope, has_exception_marker,
    locate_fragment_sentence, has_condition_marker) needs real punctuation
    for its own regexes; only the MATCH comparison changes.

    `fragment` itself is normalized too, not just `p` -- caught measuring
    this fix's own corpus impact before shipping it (8 Sol-Ring-pool
    regressions in the first draft): a Tier-1-whole-paragraph match
    DEMOTED to Tier 2 (types_disjoint_for_demotion, e.g. Sol Ring vs
    Arid Archway/City of Traitors) sets `fragment` to the RAW paragraph
    text, period intact (see assign_tier's t1_eligible_match branch) --
    NOT the token-reconstructed, always-period-stripped form ordinary
    n-gram-run fragments have. Normalizing only `p` broke that case
    (`"{t}: add {c}{c}."` vs the normalized `"{t}: add {c}{c}"` no longer
    matched). Normalizing both sides is idempotent for the ordinary
    already-stripped case and fixes the demoted-paragraph case too."""
    normalized_fragment = normalize_paragraph_for_fragment_comparison(fragment)
    for face in doc["faces"]:
        for p in face["matchable_paragraphs"]:
            normalized = normalize_paragraph_for_fragment_comparison(p)
            if normalized_fragment == normalized or normalized_fragment in normalized:
                return p, face["type_line"]
    return None, None


def extract_scope(paragraph: str) -> str:
    """Amendment 1 (v2.3): per-ability effect scope from normalized ability
    text. Checked in table order; first match wins. Falls back to "self" if
    "you" appears with no opponent/player reference at all, else "unknown"
    (uncertainty is not evidence of difference -- never penalized).
    v2.4 Amendment 3 (bug fix): also catches a bare "players" subject at a
    sentence's start (beyond the three literal phrases already in
    SCOPE_PATTERNS) -- the general case the change order asks for, not just
    the specific verbs enumerated there."""
    if not paragraph:
        return "unknown"
    for scope, patterns in SCOPE_PATTERNS:
        if any(re.search(p, paragraph) for p in patterns):
            return scope
    for sentence in split_clauses(paragraph):
        if sentence.strip().startswith("players "):
            return "symmetric"
    if re.search(r"\byou\b", paragraph) and "opponent" not in paragraph and "player" not in paragraph:
        return "self"
    return "unknown"


def has_exception_marker(paragraph: str) -> bool:
    """Amendment 3: closed-vocabulary carve-out marker ("other than",
    "except", "unless") in the matched ability."""
    if not paragraph:
        return False
    return any(re.search(p, paragraph) for p in EXCEPTION_PATTERNS)


def locate_fragment_sentence(paragraph: str, fragment: str) -> str:
    """v2.4 Amendment 1: the specific sentence (period-delimited, reusing
    split_clauses) within `paragraph` that contains `fragment` -- a
    paragraph can mix an unrelated sentence (e.g. a plain mana ability)
    with the one actually carrying the matched restriction, and polarity
    must be read off the right one. Falls back to the whole paragraph if
    the fragment spans a period boundary (Tier 1 whole-paragraph matches)
    or isn't found in any single sentence."""
    if not paragraph:
        return paragraph
    if fragment == paragraph:
        return paragraph
    for sentence in split_clauses(paragraph):
        if fragment in sentence:
            return sentence
    return paragraph


def has_polarity_marker(sentence: str) -> bool:
    """v2.4 Amendment 1: prohibition marker ("can't", "cannot") on the
    specific sentence containing the matched fragment. Plain substring
    check (not regex) -- the apostrophe in "can't" makes \\b-anchored
    regex unreliable, and the marker vocabulary is closed and short."""
    if not sentence:
        return False
    return any(marker in sentence for marker in POLARITY_MARKERS)


def has_condition_marker(paragraph: str) -> bool:
    """v2.4 Amendment 2: condition-narrowing marker on the matched ability
    paragraph -- a self-reference ("~", from the self-name substitution
    already applied during normalization) or a marker from the tight,
    `~`-anchored family ("with the same name", "named", "the chosen").
    Deliberately narrow to avoid eating category modifiers like "of
    artifacts, creatures, or enchantments"."""
    if not paragraph:
        return False
    if "~" in paragraph:
        return True
    return any(marker in paragraph for marker in CONDITION_MARKERS)


def face_duration(type_line: str) -> str:
    """Amendment 2: Instant/Sorcery face -> one_shot, any permanent-type
    face -> ongoing. Known v1 simplification: "until end of turn" effects on
    permanent faces still count ongoing (see KNOWN_LIMITATIONS)."""
    tl = (type_line or "").lower()
    if "instant" in tl or "sorcery" in tl:
        return "one_shot"
    return "ongoing"


def compute_fact_penalties(anchor_doc: dict, candidate_doc: dict, fragment: str) -> dict:
    """Locates the matched ability/face on each side and derives scope,
    duration, exception, polarity, and condition mismatches (Amendments 1-3
    v2.3; Amendments 1-2 v2.4). Returns a dict with each fact's per-side
    value plus its _mismatch bool."""
    anchor_p, anchor_face_type = locate_fragment_context(anchor_doc, fragment)
    candidate_p, candidate_face_type = locate_fragment_context(candidate_doc, fragment)

    anchor_scope = extract_scope(anchor_p)
    candidate_scope = extract_scope(candidate_p)
    scope_mismatch = (
        anchor_scope != "unknown" and candidate_scope != "unknown" and anchor_scope != candidate_scope
    )

    anchor_duration = face_duration(anchor_face_type)
    candidate_duration = face_duration(candidate_face_type)
    duration_mismatch = anchor_duration != candidate_duration

    anchor_exception = has_exception_marker(anchor_p)
    candidate_exception = has_exception_marker(candidate_p)
    exception_mismatch = anchor_exception != candidate_exception  # symmetric: distance, not direction

    anchor_sentence = locate_fragment_sentence(anchor_p, fragment)
    candidate_sentence = locate_fragment_sentence(candidate_p, fragment)
    anchor_polarity = has_polarity_marker(anchor_sentence)
    candidate_polarity = has_polarity_marker(candidate_sentence)
    polarity_mismatch = anchor_polarity != candidate_polarity  # symmetric

    anchor_condition = has_condition_marker(anchor_p)
    candidate_condition = has_condition_marker(candidate_p)
    condition_mismatch = anchor_condition != candidate_condition  # symmetric

    return {
        "anchor_scope": anchor_scope, "candidate_scope": candidate_scope, "scope_mismatch": scope_mismatch,
        "anchor_duration": anchor_duration, "candidate_duration": candidate_duration,
        "duration_mismatch": duration_mismatch,
        "anchor_exception": anchor_exception, "candidate_exception": candidate_exception,
        "exception_mismatch": exception_mismatch,
        "anchor_polarity": anchor_polarity, "candidate_polarity": candidate_polarity,
        "polarity_mismatch": polarity_mismatch,
        "anchor_condition": anchor_condition, "candidate_condition": candidate_condition,
        "condition_mismatch": condition_mismatch,
    }


# ---------------------------------------------------------------------------
# Within-tier rank score (Amendment 1, v2.1; extended v2.2/v2.3)
# ---------------------------------------------------------------------------

def compute_fragment_idf(fragment: str, fragment_df, fragment_df_exact: bool, ngram_df: dict,
                          ngram_min_len: int, paragraph_index: dict, n_total_cards: int) -> tuple:
    """Returns (idf, df) for a Tier 1/2 fragment's rank contribution. Tier 2's
    df is already known (computed during assign_tier); Tier 1 fragments
    (whole ability paragraphs) get theirs computed here via the same
    min-DF-chaining convention over constituent n-gram windows, per the
    change order's instruction to reuse "the same DF≈ convention already in
    the reports." Fragments shorter than the indexed window (essentially
    never, for real ability text) fall back to the exact whole-paragraph DF
    via paragraph_index."""
    if fragment_df is not None:
        df = fragment_df
    else:
        # BUG FIX (Phase 5, same class as G-C's find_shared_paragraph fix):
        # a Tier 1 whole-paragraph fragment carries its RAW punctuation
        # (periods intact) -- must strip per-token (CO-C) before looking up
        # ngram_df, or every window touching a punctuated token silently
        # misses (df=0, clamped to 1 below), WRONGLY inflating idf to
        # log(N/1) for any long Tier 1 paragraph -- an every-Tier-1-row-
        # since-CO-C bug, not new to Phase 3.
        tokens = [strip_sentence_final_token_period(tok) for tok in fragment.split()]
        if len(tokens) >= ngram_min_len:
            df = ngram_df_estimate(tokens, ngram_df, ngram_min_len)
        else:
            df = len(paragraph_index.get(fragment, ())) or 1
    df = max(df, 1)
    return math.log(n_total_cards / df), df


def compute_rank(fragment: str, fragment_idf: float, tag_score: float, ci_step: float,
                  mv_delta_val, fact_penalties: dict, affinity: dict, ngram_min_len: int,
                  tag_score_weight: float, ci_penalty: float, mv_penalty: float, scope_penalty: float,
                  duration_penalty: float, exception_penalty: float, polarity_penalty: float,
                  condition_penalty: float, extra_fragment_terms: tuple = (), promoted: bool = False) -> dict:
    """v2.5 (rank formula): rank = idf(fragment) * sqrt(len(fragment)/NGRAM_MIN_LEN)
    + weight*tag_score - ci_penalty*ci_step - mv_penalty*abs(mv_delta)
    - scope_penalty*scope_mismatch - duration_penalty*duration_mismatch
    - exception_penalty*exception_mismatch - polarity_penalty*polarity_mismatch
    - condition_penalty*condition_mismatch + affinity_term + promoted_term.
    promoted_term (2026-07-11, first-class phrase bucket) is PROMOTED_
    PHRASE_BONUS if `promoted` else 0.0 -- a second, independent positive
    term alongside affinity_term, never blended into it (affinity_term
    measures type/subtype closeness; promoted_term measures a Captain-
    curated phrase match -- unrelated axes that both happen to add).
    sqrt (not linear) is a v2.1 deviation, unchanged here -- see
    NGRAM_LENGTH_DAMPENING. ci_step (v2.5 amendment 2) is precomputed by
    ci_relation_step_value() -- flat for same/subset/overlapping/disjoint,
    graded for superset (see graded_superset_step). affinity_term (v2.5) is
    precomputed by compute_affinity() -- the only positive term, and the
    only one not scaled by a penalty constant here (its own constants are
    baked in upstream). Returns the full breakdown dict; "raw" is the
    pre-penalty, pre-affinity score (idf+tag terms only), used to display
    the breakdown and to evaluate the mono-color proximity / sanity-
    ordering gates.

    Cumulative fragment scoring (2026-07-10 ruling): `extra_fragment_terms`
    is an already-fully-weighted list of additional runs' idf*sqrt(len)
    contributions (position-based diminishing weight * that run's own
    commonality-band weight, computed by the caller the same way the
    primary run's weighting already happens upstream of this function) --
    summed flatly into `raw`. Empty tuple (the default, and every row
    unaffected by this feature) makes this byte-identical to the pre-
    cumulative-scoring formula."""
    length = len(fragment.split())
    raw = (
        fragment_idf * math.sqrt(length / ngram_min_len)
        + sum(extra_fragment_terms)
        + tag_score_weight * tag_score
    )
    ci_term = ci_penalty * ci_step
    mv_term = mv_penalty * mv_asymmetric_distance(mv_delta_val)
    scope_term = scope_penalty if fact_penalties["scope_mismatch"] else 0.0
    duration_term = duration_penalty if fact_penalties["duration_mismatch"] else 0.0
    exception_term = exception_penalty if fact_penalties["exception_mismatch"] else 0.0
    polarity_term = polarity_penalty if fact_penalties["polarity_mismatch"] else 0.0
    condition_term = condition_penalty if fact_penalties["condition_mismatch"] else 0.0
    affinity_term = affinity["affinity_term"]
    promoted_term = PROMOTED_PHRASE_BONUS if promoted else 0.0
    final = (
        raw - ci_term - mv_term - scope_term - duration_term - exception_term
        - polarity_term - condition_term + affinity_term + promoted_term
    )
    return {
        "raw": raw, "ci_term": ci_term, "mv_term": mv_term,
        "scope_term": scope_term, "duration_term": duration_term, "exception_term": exception_term,
        "polarity_term": polarity_term, "condition_term": condition_term,
        "affinity_term": affinity_term, "promoted_term": promoted_term,
        "final": final,
    }


# ---------------------------------------------------------------------------
# v0 fact comparators (sign convention: candidate minus anchor)
# ---------------------------------------------------------------------------

def mv_delta(anchor_doc: dict, candidate_doc: dict):
    a_cmc, c_cmc = anchor_doc["cmc"], candidate_doc["cmc"]
    if a_cmc is None or c_cmc is None:
        return None
    return c_cmc - a_cmc


def mv_asymmetric_distance(mv_delta_val) -> float:
    """Phase 3 rebalance (Captain ruling): distance-dominant, direction as
    tiebreaker. abs(MVΔ) still governs magnitude (a distance of 4 always
    penalizes more than a distance of 1, regardless of direction); MV_
    PRICIER_MULT/MV_CHEAPER_MULT only scale within that, never invert it."""
    if mv_delta_val is None:
        return 0.0
    if mv_delta_val > 0:
        return mv_delta_val * MV_PRICIER_MULT
    if mv_delta_val < 0:
        return abs(mv_delta_val) * MV_CHEAPER_MULT
    return 0.0


def color_identity_relation(anchor_doc: dict, candidate_doc: dict) -> str:
    a = set(anchor_doc["color_identity"])
    c = set(candidate_doc["color_identity"])
    if a == c:
        return "same"
    if c < a:
        return "subset"
    if a < c:
        return "superset"
    if a & c:
        return "overlapping"
    return "disjoint"


def type_line_bucket_match(anchor_doc: dict, candidate_doc: dict) -> str:
    a = type_bucket(anchor_doc["type_line"])
    c = type_bucket(candidate_doc["type_line"])
    if not a or not c:
        return "unknown"
    if a == c:
        return "same"
    if a & c:
        return "overlap"
    return "different"


def keyword_overlap(anchor_doc: dict, candidate_doc: dict) -> list:
    a = set(anchor_doc["keywords"])
    c = set(candidate_doc["keywords"])
    return sorted(a & c)


def fact_columns(anchor_doc: dict, candidate_doc: dict) -> dict:
    delta = mv_delta(anchor_doc, candidate_doc)
    return {
        "mv_delta": "n/a" if delta is None else f"{delta:+g}",
        "ci_relation": color_identity_relation(anchor_doc, candidate_doc),
        "type_bucket": type_line_bucket_match(anchor_doc, candidate_doc),
        "keyword_overlap": ", ".join(keyword_overlap(anchor_doc, candidate_doc)) or "-",
    }


# ---------------------------------------------------------------------------
# Anchor/name resolution (exact-match, halt loudly -- house style, per CLAUDE.md)
# ---------------------------------------------------------------------------

def normalize_name(name: str) -> str:
    return name.strip().casefold()


def build_name_index(cards: dict) -> dict:
    index = defaultdict(list)
    for oracle_id, card in cards.items():
        index[normalize_name(card["name"])].append(oracle_id)
    return dict(index)


def resolve_anchor(name: str, cards: dict, name_index: dict) -> dict:
    matches = name_index.get(normalize_name(name), [])
    if len(matches) == 0:
        halt(f"anchor {name!r} matched 0 cards in the corpus — check spelling, no fuzzy fallback")
    if len(matches) > 1:
        halt(f"anchor {name!r} matched {len(matches)} cards ({', '.join(sorted(matches))}) — ambiguous")
    return cards[matches[0]]


# ---------------------------------------------------------------------------
# Self-check (v2 calibration gate, re-verified unchanged in v2.1)
# ---------------------------------------------------------------------------

def run_self_check(cards: dict, card_docs: dict, name_index: dict, ngram_df: dict, clause_df: dict, keyword_df: dict,
                    paragraph_index: dict, args: argparse.Namespace) -> tuple:
    print("\nSelf-check against Captain's ruled v1 eyeball verdicts (frozen since v2):")
    all_pass = True
    for anchor_name, candidate_name, expected in SELF_CHECK_PAIRS:
        anchor_doc = card_docs[resolve_anchor(anchor_name, cards, name_index)["oracle_id"]]
        candidate_doc = card_docs[resolve_anchor(candidate_name, cards, name_index)["oracle_id"]]
        result = assign_tier(anchor_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        tier = result["tier"] if result else None
        evidence = result["evidence"] if result else None
        ok = tier == expected
        all_pass = all_pass and ok
        status = "PASS" if ok else "STOP"
        print(f"  [{status}] {anchor_name} -> {candidate_name}: expected {expected}, got {tier} ({evidence})")

    print("\nInfo-only (no fixed expectation):")
    info = {}
    for anchor_name, candidate_name in SELF_CHECK_INFO_ONLY:
        anchor_doc = card_docs[resolve_anchor(anchor_name, cards, name_index)["oracle_id"]]
        candidate_doc = card_docs[resolve_anchor(candidate_name, cards, name_index)["oracle_id"]]
        result = assign_tier(anchor_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        tier = result["tier"] if result else None
        evidence = result["evidence"] if result else None
        info[candidate_name] = (tier, evidence)
        print(f"  {anchor_name} -> {candidate_name}: tier={tier} ({evidence})")

    return all_pass, info


def check_tier0_exclusion_gate(self_check_info: dict) -> bool:
    """v2.5 session amendment, gate 2 (tier ASSIGNMENT gates stay green):
    Sol Talisman and Ulvenwald Captive // Ulvenwald Abomination must remain
    excluded from Sol Ring's Tier 0 (standing ruling 2 / the v2 Amendment 2
    bug-fix verifications). Previously these were reported info-only
    (SELF_CHECK_INFO_ONLY has no fixed expected tier); this run makes the
    "not Tier 0" half of that a hard, blocking assertion, since the affinity
    bonus is rank-only and any tier-membership change here would mean it
    leaked into tier ASSIGNMENT logic -- a real bug, not a ruling to make."""
    print("\nTier 0 exclusion gate (Sol Ring, standing ruling 2 -- blocking per v2.5 session amendment):")
    all_ok = True
    for name in ("Sol Talisman", "Ulvenwald Captive // Ulvenwald Abomination"):
        tier, evidence = self_check_info.get(name, (None, None))
        ok = tier != 0
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'STOP'}] {name}: tier={tier} (must not be 0) ({evidence})")
    return all_ok


# ---------------------------------------------------------------------------
# Amendment 4 (v2.1) -- new validation gates
# ---------------------------------------------------------------------------

def check_symmetry(cards: dict, card_docs: dict, name_index: dict, ngram_df: dict, clause_df: dict, keyword_df: dict,
                    paragraph_index: dict, args: argparse.Namespace) -> bool:
    print("\nSymmetry gate (Amendment 4.1): tier assignment must not depend on direction")
    all_ok = True
    for name_a, name_b in SYMMETRY_PAIRS:
        doc_a = card_docs[resolve_anchor(name_a, cards, name_index)["oracle_id"]]
        doc_b = card_docs[resolve_anchor(name_b, cards, name_index)["oracle_id"]]
        result_ab = assign_tier(doc_a, doc_b, ngram_df, clause_df, keyword_df, paragraph_index, args)
        result_ba = assign_tier(doc_b, doc_a, ngram_df, clause_df, keyword_df, paragraph_index, args)
        tier_ab = result_ab["tier"] if result_ab else None
        tier_ba = result_ba["tier"] if result_ba else None
        ok = tier_ab == tier_ba
        all_ok = all_ok and ok
        status = "PASS" if ok else "STOP"
        print(f"  [{status}] {name_a} <-> {name_b}: {name_a}->{name_b}=tier{tier_ab}, {name_b}->{name_a}=tier{tier_ba}")
    return all_ok


def check_marisi_visibility(displayed_tier2: list, full_tier2: list, report_cap: int) -> bool:
    """v2.3 (Amendment/gate 6): reported, NON-BLOCKING. Ratified by Captain
    after the v2.2 eyeball: the mono-color-proximity ruling structurally
    penalizes Marisi (the only superset-CI, MV+2 card in Abolisher's
    same-fragment silence cluster) -- her falling out of the displayed
    top-N is the formula working as specified, not a regression to gate on.
    Position is always printed for visibility; this never fails the run."""
    print("\nMarisi visibility (Amendment 4.2, v2.3: reported, non-blocking):")
    target = "Marisi, Breaker of the Coil"
    displayed_names = [r["name"] for r in displayed_tier2]
    if target in displayed_names:
        idx = displayed_names.index(target)
        print(f"  [INFO] Marisi appears in Abolisher's displayed Tier 2 at position {idx + 1}")
        return True

    full_names = [r["name"] for r in full_tier2]
    if target in full_names:
        idx = full_names.index(target)
        row = full_tier2[idx]
        print(
            f"  [INFO] Marisi qualifies for Abolisher's Tier 2 (full-list position {idx + 1}/"
            f"{len(full_names)}, rank={row['_rank']:.2f}, evidence={row['evidence']}) but falls "
            f"outside the displayed top-{report_cap} -- not a gate failure, ratified in v2.3"
        )
    else:
        print("  [INFO] Marisi does not qualify for Abolisher's Tier 2 at all")
    return True


def total_penalty(row: dict) -> float:
    """NET penalty applied to a Tier 1/2 row: sum of all v2.2/v2.3/v2.4
    penalty terms MINUS the v2.5 affinity_term (a positive term, so it
    reduces the net penalty -- final == raw - total_penalty(row) always
    holds, which is what the "raw_gap vs penalty_gap" gate comparisons
    below rely on)."""
    return (
        row.get("_ci_term", 0.0) + row.get("_mv_term", 0.0) + row.get("_scope_term", 0.0)
        + row.get("_duration_term", 0.0) + row.get("_exception_term", 0.0)
        + row.get("_polarity_term", 0.0) + row.get("_condition_term", 0.0)
        - row.get("_affinity_term", 0.0)
    )


def best_position(rows: list, matcher) -> int:
    positions = [i for i, r in enumerate(rows) if matcher(r)]
    return min(positions) if positions else None


def is_unexempted_boilerplate(fragment_target: str, tag_exempt_threshold: float):
    """Matcher factory for burial gates (post-ruling fix): a row counts as
    burial-worthy boilerplate only if its fragment is EXACTLY the target
    phrase (identity, not substring -- a longer/rarer superstring match is a
    different, legitimate fragment) AND its weighted tag-score contribution
    is below the exemption threshold (a fragment-identical row with strong
    tag support is tag-driven, not generic-fragment noise)."""
    def matcher(row: dict) -> bool:
        return (
            row.get("fragment") == fragment_target
            and row.get("_weighted_tag_score", 0.0) < tag_exempt_threshold
        )
    return matcher


def check_rank_precedence(label: str, rows: list, better_matcher, worse_matcher,
                           better_desc: str, worse_desc: str) -> bool:
    better_pos = best_position(rows, better_matcher)
    worse_pos = best_position(rows, worse_matcher)
    print(f"\n{label}:")
    if worse_pos is None:
        print(f"  [PASS] no displayed rows match {worse_desc!r} — nothing to bury")
        return True
    if better_pos is None:
        print(f"  [STOP] no displayed rows match {better_desc!r} to test against {worse_desc!r}")
        return False
    ok = better_pos < worse_pos
    print(
        f"  [{'PASS' if ok else 'STOP'}] best {better_desc!r} at displayed position "
        f"{better_pos + 1}, best {worse_desc!r} at position {worse_pos + 1}"
    )
    return ok


def print_rank_breakdown(label: str, row: dict) -> None:
    if row is None:
        print(f"  {label}: not present in this displayed list")
        return
    fp = row.get("_fact_penalties", {})
    ci_colors_added = row.get("_ci_colors_added")
    ci_note = row["facts"]["ci_relation"] + (f", +{ci_colors_added} colors" if ci_colors_added is not None else "")
    print(
        f"  {label} ({row['name']}): raw={row['_raw_score']:.2f}, "
        f"ci_term={row['_ci_term']:.2f} ({ci_note}, step={row.get('_ci_step')}), "
        f"mv_term={row['_mv_term']:.2f} (MVΔ={row['facts']['mv_delta']}), "
        f"scope_term={row['_scope_term']:.2f} ({fp.get('anchor_scope')}/{fp.get('candidate_scope')}), "
        f"duration_term={row['_duration_term']:.2f} ({fp.get('anchor_duration')}/{fp.get('candidate_duration')}), "
        f"exception_term={row['_exception_term']:.2f} ({fp.get('anchor_exception')}/{fp.get('candidate_exception')}), "
        f"polarity_term={row['_polarity_term']:.2f} ({fp.get('anchor_polarity')}/{fp.get('candidate_polarity')}), "
        f"condition_term={row['_condition_term']:.2f} ({fp.get('anchor_condition')}/{fp.get('candidate_condition')}), "
        f"affinity_term={row.get('_affinity_term', 0.0):.2f} (type_match={row.get('_type_match')}, "
        f"shared_subtypes={row.get('_shared_subtypes')}), "
        f"final={row['_rank']:.2f}"
    )


def check_mono_color_proximity(displayed_tier2: list, target_name: str, mv_floor: int) -> bool:
    """Amendment (v2.2): Voice of Victory must rank above every superset-CI,
    |MVDelta|>=mv_floor candidate in Abolisher's displayed Tier 2 -- UNLESS
    that candidate's raw fragment score exceeds Voice of Victory's raw score
    by more than the candidate's own actual total penalty (ci_term+mv_term),
    in which case it's legitimately closer on text and the gate must not
    punish rarity for it (explicitly not a failure, per the change order)."""
    print(f"\nMono-color proximity gate (Grand Abolisher, target={target_name!r}):")
    by_name = {r["name"]: r for r in displayed_tier2}
    target_row = by_name.get(target_name)
    if target_row is None:
        print(f"  [STOP] {target_name!r} not found in displayed Tier 2")
        return False
    target_pos = displayed_tier2.index(target_row)

    all_ok = True
    for i, row in enumerate(displayed_tier2):
        if row["name"] == target_name or i >= target_pos:
            continue
        if row["facts"]["ci_relation"] != "superset":
            continue
        mv_val = row.get("_mv_delta")
        if mv_val is None or abs(mv_val) < mv_floor:
            continue

        raw_gap = row["_raw_score"] - target_row["_raw_score"]
        own_penalty = total_penalty(row)
        if raw_gap > own_penalty:
            print(
                f"  [INFO] {row['name']!r} ranks above {target_name} but raw_gap={raw_gap:.2f} > "
                f"its own penalty={own_penalty:.2f} -- legitimately closer on text, NOT a gate "
                f"failure. Flagged for Captain's constant ruling (Amendment 1)."
            )
            continue

        print(
            f"  [STOP] {row['name']!r} ranks above {target_name} with raw_gap={raw_gap:.2f} <= "
            f"its own penalty={own_penalty:.2f} -- the penalty should have caught this; check for a bug"
        )
        all_ok = False

    if all_ok:
        print(f"  [PASS] every superset/|MVΔ|>={mv_floor} row above {target_name} is an explained exception")
    return all_ok


def check_sol_ring_sanity_ordering(displayed_tier1: list, trio: list) -> bool:
    """Amendment (v2.2). Two real checks, since the list is sorted by final
    rank descending, ANY ordering among rows is trivially self-consistent
    (raw_gap vs penalty_gap always explains a flip) -- that's not a
    meaningful bug signal on its own. What IS meaningful:
      1. The trio itself must be present.
      2. Among rows tied (or near-tied) on raw score, ordering must follow
         the MV penalty -- i.e. within the trio, smaller |MV Delta| must not
         rank BELOW larger |MV Delta| (that WOULD indicate a penalty/sort bug).
    Any other same-CI, higher-|MV Delta| row that narrowly outranks a trio
    member on raw-score strength is reported for transparency, not failed --
    per the same principle as the mono-color proximity gate, rarity/tag
    strength legitimately overriding MV distance is the formula working,
    not breaking."""
    print("\nSanity ordering gate (Sol Ring Tier 1):")
    by_name = {r["name"]: r for r in displayed_tier1}
    missing = [name for name in trio if name not in by_name]
    if missing:
        print(f"  [STOP] missing from displayed Tier 1: {missing}")
        return False

    trio_rows = [by_name[name] for name in trio]
    for name, row in zip(trio, trio_rows):
        print(f"  {name}: rank={row['rank_display']} MVΔ={row['facts']['mv_delta']}")

    all_ok = True
    for a in trio_rows:
        for b in trio_rows:
            if a is b:
                continue
            a_mv, b_mv = abs(a.get("_mv_delta") or 0), abs(b.get("_mv_delta") or 0)
            if a["_raw_score"] == b["_raw_score"] and a_mv < b_mv and a["_rank"] < b["_rank"]:
                print(
                    f"  [STOP] {a['name']!r} (MVΔ={a['facts']['mv_delta']}) has equal raw score to "
                    f"{b['name']!r} (MVΔ={b['facts']['mv_delta']}) but ranks below it despite a "
                    f"SMALLER MV distance -- penalty/sort bug"
                )
                all_ok = False

    trio_max_abs_mv = max(abs(r.get("_mv_delta") or 0) for r in trio_rows)
    trio_worst_pos = max(displayed_tier1.index(r) for r in trio_rows)
    for i, row in enumerate(displayed_tier1):
        if row["name"] in trio or i >= trio_worst_pos:
            continue
        if row["facts"]["ci_relation"] != "same" or abs(row.get("_mv_delta") or 0) <= trio_max_abs_mv:
            continue
        closest_trio = min(trio_rows, key=lambda t: abs(t["_rank"] - row["_rank"]))
        raw_gap = row["_raw_score"] - closest_trio["_raw_score"]
        penalty_gap = total_penalty(row) - total_penalty(closest_trio)
        print(
            f"  [INFO] {row['name']!r} (MVΔ={row['facts']['mv_delta']}) narrowly outranks "
            f"{closest_trio['name']!r}: raw_gap={raw_gap:.2f} vs penalty_gap={penalty_gap:.2f} -- "
            f"rarity/tag strength legitimately outweighing the larger MV distance, not a gate failure."
        )

    if all_ok:
        print("  [PASS] trio present, internally ordered correctly by MV penalty")
    return all_ok


# ---------------------------------------------------------------------------
# v2.3 new gates
# ---------------------------------------------------------------------------

def check_vov_placement(displayed_tier2: list) -> bool:
    """v2.3 gate 1: Voice of Victory must appear at displayed position <=
    VOV_PLACEMENT_STOP_POSITION (expected <= VOV_PLACEMENT_EXPECTED_POSITION,
    informational only). Position 4+ = STOP with full breakdowns of every
    row above her."""
    print(f"\nVoice of Victory placement gate (Amendment 5.1):")
    names = [r["name"] for r in displayed_tier2]
    if VOICE_OF_VICTORY not in names:
        print(f"  [STOP] {VOICE_OF_VICTORY!r} not found in displayed Tier 2")
        return False
    pos = names.index(VOICE_OF_VICTORY) + 1
    if pos > VOV_PLACEMENT_STOP_POSITION:
        print(f"  [STOP] {VOICE_OF_VICTORY!r} at position {pos} (must be <= {VOV_PLACEMENT_STOP_POSITION}):")
        for row in displayed_tier2[: pos - 1]:
            print_rank_breakdown(f"  above VoV", row)
        return False
    note = "" if pos <= VOV_PLACEMENT_EXPECTED_POSITION else f" (expected <= {VOV_PLACEMENT_EXPECTED_POSITION})"
    print(f"  [PASS] {VOICE_OF_VICTORY!r} at position {pos}{note}")
    return True


SEN_TRIPLETS_EXILE_MARGIN_TARGET = 0.3  # v2.5 amendment 2 -- "robust exile" comfort target, informational
SEN_TRIPLETS_EXILE_MARGIN_FLOOR = 0.1   # below this = STOP; Captain: "I want a robust exile, not a coin flip"


def check_sen_triplets_exile(displayed_tier2: list, full_tier2: list) -> bool:
    """v2.3 gate 2, extended by v2.5 amendment 2: Sen Triplets must be
    ABSENT from the displayed top 10 (outcome-form gate; constants are the
    means -- prints positions 8-14 on failure per the v2.3 change order),
    AND the margin between it and the #10 cutoff must not be razor-thin.
    margin = cutoff row's final rank - Sen Triplets' final rank (read from
    the FULL tier-2 list, since by definition it's excluded from the
    displayed one). margin < SEN_TRIPLETS_EXILE_MARGIN_FLOOR is the hard
    STOP the ruling asks for; margin between the floor and
    SEN_TRIPLETS_EXILE_MARGIN_TARGET is noted but not a failure -- only the
    floor is an enforced boundary, per the ruling's own wording."""
    print("\nSen Triplets exile gate (Amendment 5.2, v2.5 amendment 2 margin check):")
    names = [r["name"] for r in displayed_tier2]
    if SEN_TRIPLETS in names:
        pos = names.index(SEN_TRIPLETS) + 1
        print(f"  [STOP] {SEN_TRIPLETS!r} still displayed at position {pos}. Breakdown, positions 8-14:")
        for i, row in enumerate(displayed_tier2[7:14], start=8):
            print_rank_breakdown(f"    #{i}", row)
        return False

    print(f"  [PASS] {SEN_TRIPLETS!r} absent from the displayed top {len(displayed_tier2)}")

    full_by_name = {r["name"]: r for r in full_tier2}
    sen_row = full_by_name.get(SEN_TRIPLETS)
    if sen_row is None or not displayed_tier2:
        print(f"  [INFO] {SEN_TRIPLETS!r} does not qualify for Tier 2 at all -- margin check not applicable")
        return True

    cutoff_row = displayed_tier2[-1]
    margin = cutoff_row["_rank"] - sen_row["_rank"]
    print(
        f"  Margin below #{len(displayed_tier2)} cutoff ({cutoff_row['name']}, {cutoff_row['_rank']:.2f}) vs "
        f"{SEN_TRIPLETS} ({sen_row['_rank']:.2f}): {margin:.2f}"
    )
    if margin < SEN_TRIPLETS_EXILE_MARGIN_FLOOR:
        print(
            f"  [STOP] margin {margin:.2f} < {SEN_TRIPLETS_EXILE_MARGIN_FLOOR} -- razor-thin, not a robust "
            f"exile. Boundary rows:"
        )
        print_rank_breakdown(f"    #{len(displayed_tier2)} (cutoff)", cutoff_row)
        print_rank_breakdown(f"    {SEN_TRIPLETS} (excluded)", sen_row)
        return False
    if margin < SEN_TRIPLETS_EXILE_MARGIN_TARGET:
        print(
            f"  [INFO] margin {margin:.2f} is below the ~{SEN_TRIPLETS_EXILE_MARGIN_TARGET} comfort target "
            f"but >= the {SEN_TRIPLETS_EXILE_MARGIN_FLOOR} hard floor -- not a gate failure"
        )
    else:
        print(f"  [PASS] margin {margin:.2f} >= ~{SEN_TRIPLETS_EXILE_MARGIN_TARGET} -- robust exile")
    return True


def check_partial_lock_movement(displayed_tier2: list, mv_floor: int) -> bool:
    """v2.3 gate 2b. Hard requirement (the doc's explicit floor): Avatar's
    Wrath and Drannith Magistrate must rank below Voice of Victory (the
    zero-penalty, total-lock, same-CI row) -- this is the enforced gate.
    The broader aim ("below every total-lock, same-CI, |MVDelta|<=mv_floor
    row") is checked too, but per the same "explained exception" principle
    used elsewhere in this file: if a partial-lock card's raw-score lead
    over a specific total-lock row exceeds the ADDITIONAL penalty it carries
    relative to that row, it's legitimately closer on text/tags despite the
    exception hit -- informational, not a failure (the doc's own "at
    minimum" phrasing is exactly this hedge)."""
    print("\nPartial-lock movement gate (Amendment 5.2b):")
    by_name = {r["name"]: r for r in displayed_tier2}
    names = [r["name"] for r in displayed_tier2]
    all_ok = True
    vov_row = by_name.get(VOICE_OF_VICTORY)
    for name in sorted(PARTIAL_LOCK_CARDS):
        row = by_name.get(name)
        exc = row["_fact_penalties"]["candidate_exception"] if row else None
        print(f"  {name}: {'present' if row else 'ABSENT'}, exception_marker={exc}")
        if row is None:
            continue
        pos = names.index(name)

        if vov_row is not None and pos < names.index(VOICE_OF_VICTORY):
            print(f"  [STOP] {name!r} ranks ABOVE {VOICE_OF_VICTORY} -- the enforced floor")
            all_ok = False

        violations = [
            other["name"] for other in displayed_tier2
            if other["name"] != name
            and other["facts"]["ci_relation"] == "same"
            and abs(other.get("_mv_delta") or 0) <= mv_floor
            and not other["_fact_penalties"]["candidate_exception"]
            and names.index(other["name"]) > pos  # ranks WORSE (later) than the partial-lock card
        ]
        for other_name in violations:
            other = by_name[other_name]
            raw_gap = row["_raw_score"] - other["_raw_score"]
            penalty_gap = total_penalty(row) - total_penalty(other)
            if raw_gap > penalty_gap:
                print(
                    f"  [INFO] {name!r} outranks total-lock row {other_name!r}: raw_gap={raw_gap:.2f} "
                    f"> penalty_gap={penalty_gap:.2f} -- legitimately closer on text/tags despite the "
                    f"exception hit, not a gate failure (still below {VOICE_OF_VICTORY}, the enforced floor)."
                )
            else:
                print(
                    f"  [STOP] {name!r} outranks total-lock row {other_name!r} with raw_gap={raw_gap:.2f} "
                    f"<= penalty_gap={penalty_gap:.2f} -- unexplained, check for a bug"
                )
                all_ok = False

    print("  Exception spot-checks:")
    for name in (VOICE_OF_VICTORY, "Silence", "Mandate of Peace", SEN_TRIPLETS):
        row = by_name.get(name)
        exc = row["_fact_penalties"]["candidate_exception"] if row else "not in displayed list"
        print(f"    {name}: exception_marker={exc} (expected False)")
        if row is not None and row["_fact_penalties"]["candidate_exception"]:
            all_ok = False

    if all_ok:
        print("  [PASS] partial-lock cards rank below total-lock same-CI/low-MV rows; spot-checks correct")
    return all_ok


def check_scope_duration_spotchecks(cards: dict, card_docs: dict, name_index: dict, ngram_df: dict,
                                     clause_df: dict, keyword_df: dict, paragraph_index: dict,
                                     args: argparse.Namespace) -> bool:
    """v2.3 gates 3-4: scope and duration spot-checks against Grand
    Abolisher, printed and asserted since these have definite expected
    values per the change order."""
    print("\nScope + duration spot-checks (Amendments 1, 2 / gates 3-4):")
    abolisher_doc = card_docs[resolve_anchor("Grand Abolisher", cards, name_index)["oracle_id"]]
    all_ok = True

    scope_checks = [
        (SEN_TRIPLETS, "single"),
        ("Failure // Comply", "single"),
        ("Drannith Magistrate", "all_opp"),
        (VOICE_OF_VICTORY, "all_opp"),
        ("Silence", "all_opp"),
        ("Avatar's Wrath", "all_opp"),
    ]
    # Known doc-vs-reality mismatch, verified against live oracle text before
    # implementing: Failure // Comply's Comply half currently reads "...your
    # opponents can't cast spells with the chosen name" -- literally all_opp
    # per Amendment 1's own pattern table, not "single" as the change order's
    # worked example assumed (likely written against different/older oracle
    # text). The extractor is faithful to the documented rules and to the
    # CURRENT card; this is downgraded to informational rather than forced
    # to match a stale assumption.
    KNOWN_SCOPE_MISMATCHES = {"Failure // Comply"}
    for name, expected in scope_checks:
        candidate_doc = card_docs[resolve_anchor(name, cards, name_index)["oracle_id"]]
        result = assign_tier(abolisher_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        if result is None:
            print(f"  [STOP] {name!r}: no verbatim overlap with Grand Abolisher -- cannot spot-check scope")
            all_ok = False
            continue
        fp = compute_fact_penalties(abolisher_doc, candidate_doc, result["fragment"])
        scope = fp["candidate_scope"]
        ok = scope == expected
        if not ok and name in KNOWN_SCOPE_MISMATCHES:
            print(
                f"  [INFO] {name}: scope={scope} (change order assumed {expected}, but current oracle "
                f"text is 'your opponents can't cast spells with the chosen name' -- genuinely all_opp "
                f"per the documented pattern table; not a bug, documented mismatch)"
            )
            continue
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'STOP'}] {name}: scope={scope} (expected {expected})")

    myrel_doc = card_docs[resolve_anchor("Myrel, Shield of Argive", cards, name_index)["oracle_id"]]
    myrel_scopes = []
    for face in myrel_doc["faces"]:
        for p in face["matchable_paragraphs"]:
            myrel_scopes.append((p, extract_scope(p)))
    print(f"  Myrel's abilities (expected all_opp, self):")
    for p, scope in myrel_scopes:
        print(f"    {scope}: {p!r}")
    expected_myrel = {"all_opp", "self"}
    actual_myrel = {s for _, s in myrel_scopes}
    if not expected_myrel.issubset(actual_myrel):
        print(f"  [STOP] Myrel's abilities didn't produce both expected scopes (got {actual_myrel})")
        all_ok = False
    else:
        print(f"  [PASS] Myrel's abilities include both all_opp and self")

    duration_checks = [
        ("Flamescroll Celebrant // Revel in Silence", "one_shot"),
        ("Silence", "one_shot"),
        ("Mandate of Peace", "one_shot"),
        ("Avatar's Wrath", "one_shot"),
        ("Grand Abolisher", "ongoing"),
        (VOICE_OF_VICTORY, "ongoing"),
        ("Drannith Magistrate", "ongoing"),
        ("Conqueror's Flail", "ongoing"),
    ]
    print("  Duration spot-checks:")
    for name, expected in duration_checks:
        candidate_doc = card_docs[resolve_anchor(name, cards, name_index)["oracle_id"]]
        if name == "Grand Abolisher":
            # Abolisher's own single face carries its only ability -- no
            # pairwise match needed, just read its face type directly.
            duration = face_duration(abolisher_doc["faces"][0]["type_line"])
        else:
            result = assign_tier(abolisher_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
            if result is None:
                print(f"    [STOP] {name!r}: no verbatim overlap with Grand Abolisher -- cannot spot-check duration")
                all_ok = False
                continue
            _, face_type = locate_fragment_context(candidate_doc, result["fragment"])
            duration = face_duration(face_type)
        ok = duration == expected
        all_ok = all_ok and ok
        print(f"    [{'PASS' if ok else 'STOP'}] {name}: duration={duration} (expected {expected})")

    return all_ok


def check_movement_gate(displayed_tier2: list) -> bool:
    """v2.3 gate 5: relative movement vs the v2.2 baseline. Silence and
    Mandate of Peace should drop; Conqueror's Flail should rise; Failure //
    Comply should drop below all zero-penalty rows."""
    print("\nMovement gate vs v2.2 baseline (Amendment 5.5):")
    names = [r["name"] for r in displayed_tier2]

    def current_pos(name):
        return names.index(name) + 1 if name in names else None

    all_ok = True
    for name, expect_direction in (("Silence", "drop"), ("Mandate of Peace", "drop"), ("Conqueror's Flail", "rise")):
        baseline = V22_BASELINE_ABOLISHER_POSITIONS[name]
        current = current_pos(name)
        current_display = current if current is not None else f">{len(displayed_tier2)} (fell out of top {len(displayed_tier2)})"
        if expect_direction == "drop":
            ok = current is None or current > baseline
        else:
            ok = current is not None and current < baseline
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'STOP'}] {name}: v2.2 pos={baseline}, v2.3 pos={current_display} (expected {expect_direction})")

    zero_penalty_rows = [r for r in displayed_tier2 if total_penalty(r) == 0]
    fc_pos = current_pos("Failure // Comply")
    worst_zero_penalty_pos = max((names.index(r["name"]) + 1 for r in zero_penalty_rows), default=0)
    ok = fc_pos is None or fc_pos > worst_zero_penalty_pos
    all_ok = all_ok and ok
    print(
        f"  [{'PASS' if ok else 'STOP'}] Failure // Comply: v2.3 pos="
        f"{fc_pos if fc_pos is not None else 'not displayed'}, worst zero-penalty row at "
        f"{worst_zero_penalty_pos} (expected Failure // Comply below all zero-penalty rows)"
    )
    return all_ok


# ---------------------------------------------------------------------------
# v2.4 new gates
# ---------------------------------------------------------------------------

MANA_ONLY_FAMILY = {
    "Myr Reservoir", "Flamebraider", "Smokebraider", "Vedalken Engineer", "Grand Architect",
    "Orb of Dragonkind", "Renowned Weaponsmith", "Dalakos, Crafter of Wonders",
    "Gwenna, Eyes of Gaea", "Slobad, Iron Goblin", "Castle Garenbrig",
    "Crucible of the Spirit Dragon", "Eldrazi Temple", "Hargilde, Kindly Runechanter",
    "Power Depot", "Lukka, Bound to Ruin",
    # Added auditing Entry #4 (Captain's ruling, 2026-07-10): a real
    # pre-existing bug in is_keyword_only_paragraph() (raw substring prefix
    # match, not word-boundary safe -- "enchanted" starts with the card's
    # own "Enchant" keyword as a bare substring) was wrongly excluding
    # Discreet Retreat's ENTIRE ability paragraph from matchable_paragraphs.
    # Fixed as part of Entry #4's implementation (needed for its own
    # motivating case, Swiftfoot Boots/Lightning Greaves, same bug class).
    # Discreet Retreat's newly-visible text ("spend this mana only to cast
    # outlaw spells or activate abilities of outlaw sources") shares Grand
    # Abolisher's own defining fragment and is thematically identical to
    # this family -- same "previously hidden by a tokenizer/parser bug, now
    # correctly surfaced and correctly disqualified" pattern already
    # documented above for Angel of Jubilation/Yasharn, Implacable Earth.
    # Tier 2 count unaffected (54, unchanged) -- corroboration removes it
    # outright, same as the other 16.
    "Discreet Retreat",
}


def check_godsend_gate(displayed_tier2: list, cards: dict, card_docs: dict, name_index: dict,
                        ngram_df: dict, clause_df: dict, keyword_df: dict, paragraph_index: dict, args: argparse.Namespace) -> bool:
    """v2.4 gate 1: Godsend absent from Abolisher's displayed top 10 (its
    condition-narrowed lock should sink it); condition spot-check printed."""
    print("\nGodsend gate (v2.4 gate 1):")
    names = [r["name"] for r in displayed_tier2]
    all_ok = True
    if "Godsend" in names:
        print(f"  [STOP] Godsend still displayed at position {names.index('Godsend') + 1}")
        all_ok = False
    else:
        print(f"  [PASS] Godsend absent from displayed top {len(displayed_tier2)}")

    abolisher_doc = card_docs[resolve_anchor("Grand Abolisher", cards, name_index)["oracle_id"]]
    godsend_doc = card_docs[resolve_anchor("Godsend", cards, name_index)["oracle_id"]]
    result = assign_tier(abolisher_doc, godsend_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
    if result is None:
        print("  [STOP] Godsend: no verbatim overlap with Grand Abolisher -- cannot spot-check condition")
        return False
    fp = compute_fact_penalties(abolisher_doc, godsend_doc, result["fragment"])
    ok = fp["candidate_condition"] and not fp["anchor_condition"]
    all_ok = all_ok and ok
    print(
        f"  [{'PASS' if ok else 'STOP'}] condition spot-check: Godsend={fp['candidate_condition']} "
        f"(expected True), Grand Abolisher={fp['anchor_condition']} (expected False)"
    )
    return all_ok


def check_polarity_family_gate(displayed_tier2: list, cards: dict, card_docs: dict, name_index: dict,
                                ngram_df: dict, clause_df: dict, keyword_df: dict, paragraph_index: dict, args: argparse.Namespace) -> bool:
    """v2.4 gate 2: no "spend this mana only" family member in Abolisher's
    displayed top 10 (identical grammar, inverted function -- polarity
    mismatch should sink the whole family); polarity spot-checks printed."""
    print("\nPolarity family gate (v2.4 gate 2):")
    names = [r["name"] for r in displayed_tier2]
    present = [n for n in names if n in MANA_ONLY_FAMILY]
    all_ok = True
    if present:
        print(f"  [STOP] 'spend this mana only' family still displayed: {present}")
        all_ok = False
    else:
        print(f"  [PASS] no 'spend this mana only' family member in displayed top {len(displayed_tier2)}")

    abolisher_doc = card_docs[resolve_anchor("Grand Abolisher", cards, name_index)["oracle_id"]]
    for name, expected_trip in (("Myr Reservoir", True), (VOICE_OF_VICTORY, False)):
        candidate_doc = card_docs[resolve_anchor(name, cards, name_index)["oracle_id"]]
        result = assign_tier(abolisher_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        if result is None:
            print(f"  [STOP] {name}: no verbatim overlap with Grand Abolisher -- cannot spot-check polarity")
            all_ok = False
            continue
        fp = compute_fact_penalties(abolisher_doc, candidate_doc, result["fragment"])
        ok = fp["polarity_mismatch"] == expected_trip
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'STOP'}] {name}: polarity_mismatch={fp['polarity_mismatch']} (expected {expected_trip})")
    return all_ok


def check_basandra_gate(marisi_full_tier2: list, cards: dict, card_docs: dict, name_index: dict,
                         ngram_df: dict, clause_df: dict, keyword_df: dict, paragraph_index: dict, args: argparse.Namespace) -> bool:
    """v2.4 gate 3, UNGATED by Captain ruling (RULING-MANIFEST-2026-07-09.md,
    Phase 3 rebalance). History, so nothing evaporates: original v2.4
    expectation was "Basandra ranks below Myrel," assuming neither side's
    text evidence was discounted. Phase 3's band discount then applied to
    Myrel's own matched fragment against Marisi ("your opponents can't cast
    spells", DF=29, discounted band) while Basandra's ("can't cast spells
    during combat", DF=3) stayed full-weight; this briefly flipped the
    expectation to "Basandra ranks ABOVE Myrel" (fact basis: closer color
    identity to Marisi + a near-exact rarer phrase). Captain then RETIRED
    this as a gate entirely: neither ordering is an expectation any longer
    -- both are defensible, and the symmetric-vs-not distinction is a rank
    fact to report, never a disqualifier. Reported informationally only,
    never blocking. See experiments/measure/PHASE-3-REBALANCE-SHAPES-MEMO.md
    for the full history. Scope spot-checks printed (Basandra symmetric,
    Kutzil all_opp) are unaffected and remain blocking."""
    print("\nBasandra gate (v2.4 gate 3, UNGATED by Captain ruling -- informational only, see docstring):")
    names = [r["name"] for r in marisi_full_tier2]
    all_ok = True
    if "Basandra, Battle Seraph" in names and "Myrel, Shield of Argive" in names:
        basandra_pos = names.index("Basandra, Battle Seraph")
        myrel_pos = names.index("Myrel, Shield of Argive")
        relation = "ABOVE" if basandra_pos < myrel_pos else "below"
        print(
            f"  [INFO] Basandra at full-list position {basandra_pos + 1}, Myrel at {myrel_pos + 1} "
            f"(Basandra ranks {relation} Myrel -- ungated, both orderings are defensible, not a gate failure)"
        )
    else:
        print("  [INFO] Basandra and/or Myrel not both present in Marisi's Tier 2 -- nothing to order")

    marisi_doc = card_docs[resolve_anchor("Marisi, Breaker of the Coil", cards, name_index)["oracle_id"]]
    for name, expected in (("Basandra, Battle Seraph", "symmetric"), ("Kutzil, Malamet Exemplar", "all_opp")):
        candidate_doc = card_docs[resolve_anchor(name, cards, name_index)["oracle_id"]]
        result = assign_tier(marisi_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        if result is None:
            print(f"  [STOP] {name}: no verbatim overlap with Marisi -- cannot spot-check scope")
            all_ok = False
            continue
        fp = compute_fact_penalties(marisi_doc, candidate_doc, result["fragment"])
        ok = fp["candidate_scope"] == expected
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'STOP'}] {name}: scope={fp['candidate_scope']} (expected {expected})")
    return all_ok


# ---------------------------------------------------------------------------
# v2.5 new gate + spot-check
# ---------------------------------------------------------------------------

DRANNITH_MAGISTRATE = "Drannith Magistrate"
AVATARS_WRATH = "Avatar's Wrath"
DRANNITH_WRATH_MARGIN_CEILING = 1.0  # "~1.0" per the change order -- win, not rout


def check_drannith_wrath_gate(abolisher_full_tier2: list, margin_ceiling: float) -> bool:
    """v2.5 gate 1 (the ruling itself): Drannith Magistrate must beat Avatar's
    Wrath in Grand Abolisher's Tier 2 -- margin (Drannith final - Wrath
    final) must be > 0 (an actual win) and <= ~margin_ceiling (not a rout --
    the affinity bonus overshooting would be as wrong as it undershooting).
    Uses the FULL tier-2 list, not the displayed/capped one, so the gate
    can't silently pass by one side falling out of the top-N. Constants are
    a ruling, not a tuning knob -- overshoot/undershoot STOPS with both full
    breakdowns rather than re-tuning TYPE_MATCH_BONUS/SUBTYPE_BONUS here."""
    print("\nDrannith vs Avatar's Wrath affinity gate (v2.5 ruling, Grand Abolisher Tier 2):")
    by_name = {r["name"]: r for r in abolisher_full_tier2}
    drannith = by_name.get(DRANNITH_MAGISTRATE)
    wrath = by_name.get(AVATARS_WRATH)
    if drannith is None or wrath is None:
        print(
            f"  [STOP] missing from Abolisher's Tier 2: {DRANNITH_MAGISTRATE}="
            f"{'present' if drannith else 'ABSENT'}, {AVATARS_WRATH}={'present' if wrath else 'ABSENT'}"
        )
        return False
    margin = drannith["_rank"] - wrath["_rank"]
    ok = 0 < margin <= margin_ceiling
    print(
        f"  [{'PASS' if ok else 'STOP'}] margin = Drannith({drannith['_rank']:.2f}) - "
        f"Wrath({wrath['_rank']:.2f}) = {margin:.2f} (must be > 0 and <= ~{margin_ceiling})"
    )
    print("  Full breakdowns:")
    print_rank_breakdown("  Drannith Magistrate", drannith)
    print_rank_breakdown("  Avatar's Wrath", wrath)
    return ok


def run_v25_spotcheck(cards: dict, card_docs: dict, name_index: dict, ngram_df: dict,
                       args: argparse.Namespace, abolisher_full_tier2: list) -> None:
    """v2.5 deliverable: print Grand Abolisher's, Drannith Magistrate's, and
    Avatar's Wrath's ENGINE-DERIVED subtypes (never hand-recalled), the
    affinity breakdown for each pairing, the Sen Triplets graded-superset-CI
    audit (amendment 2), and the MVΔ audit rider -- Avatar's Wrath's stored
    mana_cost/mv straight from cards.sqlite (authoritative), settling the
    report-vs-chat-side discrepancy on paper."""
    print("\nv2.5 spot-check block:")
    abolisher_doc = card_docs[resolve_anchor("Grand Abolisher", cards, name_index)["oracle_id"]]
    drannith_doc = card_docs[resolve_anchor(DRANNITH_MAGISTRATE, cards, name_index)["oracle_id"]]
    wrath_doc = card_docs[resolve_anchor(AVATARS_WRATH, cards, name_index)["oracle_id"]]

    print("  Parsed creature subtypes (post-dash type-line tokens, Creature faces only):")
    for doc in (abolisher_doc, drannith_doc, wrath_doc):
        subtypes = sorted(creature_subtypes(doc["type_line"]))
        print(f"    {doc['name']} ({doc['type_line']!r}): {subtypes or '(none)'}")

    print("  Affinity breakdown vs Grand Abolisher:")
    for doc in (drannith_doc, wrath_doc):
        affinity = compute_affinity(
            abolisher_doc, doc, args.type_match_bonus, args.subtype_bonus, args.subtype_bonus_cap,
        )
        print(
            f"    {doc['name']}: type_match={affinity['type_match']} (+{affinity['type_term']:.2f}), "
            f"shared_subtypes={affinity['shared_subtypes']} (+{affinity['subtype_term']:.2f}), "
            f"affinity_term={affinity['affinity_term']:.2f}"
        )

    print("  Sen Triplets graded-superset-CI audit (v2.5 amendment 2, Captain's ruling):")
    sen_triplets_doc = card_docs[resolve_anchor(SEN_TRIPLETS, cards, name_index)["oracle_id"]]
    by_name = {r["name"]: r for r in abolisher_full_tier2}
    sen_row = by_name.get(SEN_TRIPLETS)
    if sen_row is None:
        print(f"    [STOP] {SEN_TRIPLETS!r} not found in Grand Abolisher's Tier 2 -- cannot audit")
    else:
        anchor_ci = sorted(abolisher_doc["color_identity"]) or ["(colorless)"]
        candidate_ci = sorted(sen_triplets_doc["color_identity"])
        colors_added = sen_row["_ci_colors_added"]
        old_ci_step = CI_RELATION_STEP["superset"]
        old_ci_term = args.ci_penalty * old_ci_step
        new_ci_term = sen_row["_ci_term"]
        new_final = sen_row["_rank"]
        old_final = new_final + (new_ci_term - old_ci_term)
        print(
            f"    Grand Abolisher CI={anchor_ci}, Sen Triplets CI={candidate_ci}, colors_added={colors_added}"
        )
        print(
            f"    old (flat) superset step={old_ci_step}, ci_term={old_ci_term:.2f}, final={old_final:.2f}"
        )
        print(
            f"    new (graded) superset step={sen_row['_ci_step']}, ci_term={new_ci_term:.2f}, "
            f"final={new_final:.2f}"
        )

    print("  MVΔ audit rider (cards.sqlite is authoritative, per the session amendment):")
    con = sqlite3.connect(f"file:{CARDS_SQLITE_PATH}?mode=ro", uri=True)
    try:
        for name in ("Grand Abolisher", AVATARS_WRATH):
            rows = con.execute(
                "SELECT mana_cost, cmc FROM cards WHERE name = ?", (name,)
            ).fetchall()
            if len(rows) != 1:
                halt(f"{CARDS_SQLITE_PATH}: {name!r} matched {len(rows)} rows -- expected exactly 1")
            mana_cost, cmc = rows[0]
            print(f"    {name}: mana_cost={mana_cost!r}, cmc(mv)={cmc}")
    finally:
        con.close()
    abolisher_mv = abolisher_doc["cmc"]
    wrath_mv = wrath_doc["cmc"]
    settled_delta = wrath_mv - abolisher_mv
    print(
        f"    Settled MVΔ (Wrath - Abolisher) = {wrath_mv} - {abolisher_mv} = {settled_delta:+g}: "
        f"the report's MVΔ +2 claim is CORRECT per cards.sqlite. The chat-side 'Δ +1' suggestion for "
        f"{{2}}{{W}}{{W}} was an arithmetic slip -- {{2}}{{W}}{{W}} totals mana value 4 (2 generic + "
        f"W + W), not 3, against Grand Abolisher's {{W}}{{W}} (mv 2). No engine change required; this "
        f"settles the audit rider on paper as instructed."
    )


# ---------------------------------------------------------------------------
# v2.6 amendment 1 gate: Grand Abolisher's exact 16-card corroboration exile
# ---------------------------------------------------------------------------

# v2.9 baseline (Captain's ruling): 28 -> 52. Mechanism 2 (reminder-text
# injection) correctly added 24 new rows sharing "can't cast spells or
# activate abilities" with cards carrying the Split Second keyword
# (DF≈27, under the floor) -- verified all 24 land at full-list position
# 15+, none crack the displayed top 10; the existing scope/duration
# penalties correctly bury them (Split Second's symmetric, stack-
# triggered restriction is functionally distant from Abolisher's static
# one-sided lock). This is a gate tripwire, not a floor to loosen: updated
# by explicit ruling, not silently widened.
# CO-C (Phase 2a, ratified) sentence-final punctuation fix added exactly 2
# more rows: Angel of Jubilation, Yasharn, Implacable Earth. Both share
# Grand Abolisher's own defining fragment, "cast spells or activate
# abilities" (DF=29, under the floor) -- previously hidden because the
# bare tokenizer glued Abolisher's "abilities of" to these two cards'
# sentence-final "abilities." at the exact boundary the run needed to
# extend through. Verified as a genuine, wanted fix (both are on-topic
# "can't pay life/sacrifice to cast spells or activate abilities"
# restriction effects), not noise -- traced via find_shared_fragment
# before/after, not assumed. Corroboration gate's 16 disqualified names
# are unchanged.
#
# strip_bespoke_ability_label() (2026-07-11) dropped exactly 2 rows: Shadow
# the Hedgehog, Lake Silencio -- traced (not assumed) via a before/after
# matchable_paragraphs diff, root cause is a THIRD instance of the same bug
# CLASS as Entry #4's "equipped"/"equip" substring fix and v2.9 erratum 2's
# where-clause fix: is_keyword_only_paragraph()'s comma-fragment prefix
# check has no comma to split on in "chaos control — each spell you cast
# has split second..." (one fragment, no comma), and that single fragment
# LITERALLY starts with "chaos control " (the ability-word name + a
# trailing space, satisfied by the em dash that follows) -- so the entire
# ability-word paragraph was wrongly classified keyword-only, pre-existing,
# untouched by this session's actual fix. Under that misclassification,
# v2.9 Mechanism 2 injected only the line's PARENTHESIZED REMINDER body
# (the standard Split Second reminder text, "...players can't cast spells
# or activate abilities that aren't mana abilities") as this card's sole
# matchable content for that ability -- coincidentally sharing Grand
# Abolisher's own defining fragment through pure Comprehensity-Rules
# boilerplate, not real kinship (Split Second's symmetric stack-timing
# restriction has nothing to do with Abolisher's one-sided during-your-
# turn lock). strip_bespoke_ability_label() strips the "chaos control — "/
# "still point in time — " label BEFORE is_keyword_only_paragraph() runs,
# so the classifier now correctly sees these as ordinary text -- verified
# directly: their REAL ability text ("each spell you cast has split second
# if mana from an artifact was spent to cast it" / "all spells have split
# second") is now matchable (a genuine recall improvement for any other
# split-second-granting card), and the coincidental reminder-boilerplate
# link to Grand Abolisher is what's lost. Ratified as a quality
# improvement, not a regression, same "reminder-injected text is near-
# worthless evidence" judgment R1/PROVENANCE_DISCOUNT_WEIGHT already make
# everywhere else in this file -- not re-litigated here, just newly
# EXPOSED by a correct classification fix. 54 -> 52 is the SAME NUMBER as
# the pre-CO-C count above by coincidence only; the row set is entirely
# different (CO-C's fix predates and is independent of this one).
ABOLISHER_T2_COUNT_AFTER_CORROBORATION = 52  # was 54 (CO-C) / 52 (v2.9 erratum 2, different row set) / 28 (v2.6) / 44 (pre-amendment-1)


def check_abolisher_corroboration_gate(disqualified: list, full_tier2: list) -> bool:
    """v2.6 amendment 1, gate 1: Grand Abolisher's Tier 2 must lose EXACTLY
    the 16-card "spend this mana only" family (MANA_ONLY_FAMILY, already a
    named constant from the v2.4 polarity-family gate) and nothing else --
    44 -> 28 rows. Any of the 16 surviving, or any unlisted row dying,
    prints that row's polarity + tag values and STOPs."""
    print("\nTier 2 corroboration gate (v2.6 amendment 1, Grand Abolisher):")
    disq_names = {d["name"] for d in disqualified}
    all_ok = True

    missing = MANA_ONLY_FAMILY - disq_names
    if missing:
        print(f"  [STOP] expected disqualifications still surviving in Tier 2: {sorted(missing)}")
        by_name = {r["name"]: r for r in full_tier2}
        for name in sorted(missing):
            row = by_name.get(name)
            if row is None:
                print(f"    {name}: not present in Tier 2 at all (different tier or excluded elsewhere)")
            else:
                fp = row["_fact_penalties"]
                print(
                    f"    {name}: polarity(anchor/candidate)={fp['anchor_polarity']}/{fp['candidate_polarity']} "
                    f"(mismatch={fp['polarity_mismatch']}), tag_score={row['_tag_score']:.2f}"
                )
        all_ok = False

    extra = disq_names - MANA_ONLY_FAMILY
    if extra:
        print(f"  [STOP] unexpected disqualifications outside the 16-card list: {sorted(extra)}")
        by_disq = {d["name"]: d for d in disqualified}
        for name in sorted(extra):
            d = by_disq[name]
            print(
                f"    {name}: polarity(anchor/candidate)={d['anchor_polarity']}/{d['candidate_polarity']}, "
                f"tag_score={d['tag_score']:.2f}"
            )
        all_ok = False

    if not missing and not extra:
        print(f"  [PASS] exactly the expected 16 disqualified: {sorted(disq_names)}")

    ok_count = len(full_tier2) == ABOLISHER_T2_COUNT_AFTER_CORROBORATION
    print(
        f"  [{'PASS' if ok_count else 'STOP'}] Tier 2 count: {len(full_tier2)} "
        f"(expected {ABOLISHER_T2_COUNT_AFTER_CORROBORATION}: 44 pre-v2.6, 28 post-corroboration, "
        f"52 post-v2.9 Mechanism 2, 54 post-CO-C punctuation fix)"
    )
    all_ok = all_ok and ok_count
    return all_ok


# ---------------------------------------------------------------------------
# v2.6 amendment 2 gates: Defense Grid entry + Tier 3 turn-scoped visibility
# ---------------------------------------------------------------------------

DEFENSE_GRID = "Defense Grid"


def check_defense_grid_gate(displayed_tier3: list, full_tier3: list) -> dict:
    """v2.6 amendment 2, gate 4 -- DOWNGRADED TO INFORMATIONAL per Captain's
    ruling (session amendment, post-v2.6): Defense Grid landed at full-list
    position 31, not the anticipated "close but outside (11-15)" case. The
    turn-scoped mechanism is verified correct (score rose 0.17 -> ~0.24,
    exactly matching the tag's idf weight); the remaining distance is
    genuine tag-overlap distance from an unrelated "hate-enchantment"/
    "hate-artifact" plateau Defense Grid doesn't structurally belong to.
    Ruling: the designed remedy is the Tier 3 human promote lane, not a
    wider regex or a retuned constant -- do not tune anything here. Always
    returns a diagnostic dict (never blocks the run); the caller threads it
    into the Grand Abolisher report footer via append_footer()."""
    print("\nDefense Grid gate (v2.6 amendment 2, gate 4 -- INFORMATIONAL per Captain's ruling):")
    names = [r["name"] for r in displayed_tier3]
    if DEFENSE_GRID in names:
        pos = names.index(DEFENSE_GRID) + 1
        row = displayed_tier3[pos - 1]
        print(
            f"  [INFO] {DEFENSE_GRID!r} already in displayed Tier 3 top {len(displayed_tier3)} at position {pos} "
            f"(score={row['_score']:.4f}, evidence={row['evidence']})"
        )
        return {"present": True, "position": pos, "score": row["_score"]}

    full_names = [r["name"] for r in full_tier3]
    if DEFENSE_GRID not in full_names:
        print(f"  [INFO] {DEFENSE_GRID!r} does not qualify for Tier 3 at all (tag_score below threshold)")
        return {"present": False, "position": None}

    pos = full_names.index(DEFENSE_GRID) + 1
    dg_row = full_tier3[pos - 1]
    cutoff_row = full_tier3[len(displayed_tier3) - 1]
    score_gap = cutoff_row["_score"] - dg_row["_score"]
    # The plateau Defense Grid actually sits behind is the score band immediately
    # below the cutoff (often a large tie cluster), not the cutoff row's own score.
    plateau_score = full_tier3[len(displayed_tier3)]["_score"] if len(full_tier3) > len(displayed_tier3) else cutoff_row["_score"]
    tie_cluster_size = sum(1 for r in full_tier3 if abs(r["_score"] - plateau_score) < 1e-9)
    boundary_rows = full_tier3[len(displayed_tier3) - 1:min(pos, len(displayed_tier3) + 20)]
    print(
        f"  [INFO] {DEFENSE_GRID!r} at full-list position {pos}. score={dg_row['_score']:.4f} vs "
        f"#{len(displayed_tier3)} cutoff score={cutoff_row['_score']:.4f} (gap={score_gap:.4f}); "
        f"{tie_cluster_size} row(s) tied at score={plateau_score:.4f} just below the cutoff, a plateau "
        f"Defense Grid sits behind. Turn-scoped mechanism verified working (score rose from 0.17 "
        f"pre-amendment 2); remaining gap is genuine tag-overlap distance from an unrelated cluster, "
        f"not tuned further per ruling."
    )
    print(f"  Boundary rows (#{len(displayed_tier3)}-{min(pos, len(displayed_tier3) + 20)}):")
    for i, row in enumerate(boundary_rows, start=len(displayed_tier3)):
        print(f"    #{i} {row['name']}: score={row['_score']:.4f}, evidence={row['evidence']}")
    if pos > len(displayed_tier3) + 20:
        print(f"    ... ({pos - len(displayed_tier3) - 20} more rows omitted ...)")
        print(f"    #{pos} {dg_row['name']}: score={dg_row['_score']:.4f}, evidence={dg_row['evidence']}")
    print(f"  {DEFENSE_GRID} full tag breakdown (anchor Grand Abolisher's own weight includes rule:turn-scoped):")
    for m in dg_row["_matched_t3"]:
        print(
            f"    {m['slug']}: idf={m['idf']:.2f}, anchor_direct={m['anchor_direct']}, "
            f"candidate_direct={m['candidate_direct']}, weight={m['weight']:.2f}"
        )
    return {
        "present": False, "position": pos, "score": dg_row["_score"],
        "cutoff_score": cutoff_row["_score"], "score_gap": score_gap,
        "tie_cluster_size": tie_cluster_size, "boundary_rows": boundary_rows,
    }


def check_t3_turn_scoped_movement(anchor_names: list, built: dict) -> bool:
    """v2.6 amendment 2, gate 5: every Tier 3 row that entered/exited/moved
    in the displayed top-N (vs the report as it stood on disk before this
    run) must be traceable to rule:turn-scoped -- either the row carries the
    tag itself (shown in its own evidence/shared-tag column), or at least
    one OTHER row in this anchor's Tier 3 does (the anchor-directional
    coverage formula's denominator grows when the anchor itself gains a new
    tag, uniformly diluting every candidate's score -- see
    build_turn_scoped_tag_index -- so a non-carrier's position can still
    shift purely from a carrier's promotion). Unexplained movement, with
    neither condition true, STOPs."""
    print("\nTier 3 turn-scoped movement gate (v2.6 amendment 2, gate 5):")
    all_ok = True
    for anchor_name in anchor_names:
        report_path = REPORTS_DIR / f"{filename_slug(anchor_name)}.md"
        baseline_names = parse_report_tier_names(report_path, 3)
        if not baseline_names:
            print(f"  [INFO] {anchor_name}: no baseline Tier 3 rows found on disk -- nothing to diff")
            continue

        current_rows = built[anchor_name]["displayed_tiers"][3]
        full_rows_by_name = {r["name"]: r for r in built[anchor_name]["full_tiers"][3]}
        current_names = [r["name"] for r in current_rows]

        if baseline_names == current_names:
            print(f"  [PASS] {anchor_name} Tier 3: unchanged ({len(current_names)} rows)")
            continue

        entered = [n for n in current_names if n not in baseline_names]
        exited = [n for n in baseline_names if n not in current_names]
        moved = [
            n for n in current_names
            if n in baseline_names and current_names.index(n) != baseline_names.index(n)
        ]
        print(f"  {anchor_name} Tier 3: entered={entered} exited={exited} moved={moved}")

        tag_carriers = sorted(
            r["name"] for r in built[anchor_name]["full_tiers"][3]
            if any(m["slug"] == TURN_SCOPED_TAG_SLUG for m in r.get("_matched_t3", []))
        )
        # Phase 3 (ratified, R3): a candidate the rescue-zone band newly
        # qualifies for Tier 1/2 vanishes from Tier 3's pool entirely
        # ("qualifies at its best tier only," unchanged v1-era rule) --
        # a legitimate, mechanically-checkable explanation for T3 pool
        # reshuffling distinct from rule:turn-scoped, so it gets its own
        # category rather than being folded into the tag-carrier dilution
        # note above.
        promoted_this_run = sorted(
            r["name"] for t in (0, 1, 2) for r in built[anchor_name]["full_tiers"][t]
        )
        promoted_set = set(promoted_this_run)
        promoted_exits = sorted(set(exited) & promoted_set)
        unexplained = []
        for name in set(entered) | set(moved) | set(exited):
            row = full_rows_by_name.get(name)
            own_tag = bool(row) and TURN_SCOPED_TAG_SLUG in row["evidence"]
            own_promoted = name in promoted_exits
            explained = own_tag or bool(tag_carriers) or bool(promoted_exits)
            if own_promoted:
                note = f", promoted OUT of Tier 3 to a better tier this run (Phase 3 rescue-zone band)"
            elif not own_tag and tag_carriers:
                note = (
                    f", explained by anchor-wide dilution from {len(tag_carriers)} turn-scoped carrier(s) "
                    f"({tag_carriers[:3]}{'...' if len(tag_carriers) > 3 else ''})"
                )
            elif not own_tag and promoted_exits:
                note = (
                    f", explained by {len(promoted_exits)} pool-mate(s) promoted out of Tier 3 this run "
                    f"({promoted_exits[:3]}{'...' if len(promoted_exits) > 3 else ''}) reshuffling the display window"
                )
            else:
                note = ""
            print(f"    {name}: own_turn_scoped_shown={own_tag}{note} ({'explained' if explained else 'UNEXPLAINED'})")
            if not explained:
                unexplained.append(name)

        if unexplained:
            print(f"    [STOP] unexplained Tier 3 movement for {anchor_name}: {unexplained}")
            all_ok = False
        else:
            print(f"    [PASS] all Tier 3 movement for {anchor_name} explained by rule:turn-scoped")
    return all_ok


# ---------------------------------------------------------------------------
# v2.9 new gates: Zurgo keyword-kinship gain + evergreen-floor verification
# ---------------------------------------------------------------------------

ZURGO = "Zurgo, Thunder's Decree"


def check_zurgo_keyword_gate(full_tier1: list, full_tier2: list, report_cap: int) -> bool:
    """v2.9 gate 2 (blocking): Zurgo, Thunder's Decree -- verified in the
    v2.7 viewer session to have zero Tier 1/2 rows (its only matchable
    ability text, "warrior tokens ... can't be sacrificed", is unique in
    the corpus; "Mobilize 2" was pure keyword-only, excluded entirely) --
    must GAIN at least one row now, via Mobilize (Mechanism 1 keyword
    kinship and/or Mechanism 2 reminder injection). Prints every T1/T2 row
    with its full breakdown, grouped by which mechanism produced it, plus
    (Captain's post-run ruling deliverable) Zurgo's DISPLAYED Tier 2 top-N
    in actual rank order -- to eyeball whether the generic DF≈41
    raid-boilerplate rows already sort below the closer, rarer kin (e.g.
    Hero of Bladehold's DF≈6 shared trigger) via the existing fact
    penalties, or whether that's a future fact-term ruling."""
    print(f"\nZurgo keyword-kinship gate (v2.9 gate 2, {ZURGO}):")
    rows = [(1, r) for r in full_tier1] + [(2, r) for r in full_tier2]
    if not rows:
        print(f"  [STOP] {ZURGO} still has zero Tier 1/2 rows -- Mechanism 1/2 did not fire")
        return False

    by_mechanism = defaultdict(list)
    for tier, row in rows:
        by_mechanism[row.get("_mechanism", "text")].append((tier, row))

    print(f"  [PASS] {ZURGO} gained {len(rows)} Tier 1/2 row(s):")
    for mechanism in ("keyword", "reminder", "sentence", "text"):
        mrows = by_mechanism.get(mechanism, [])
        if not mrows:
            continue
        print(f"  -- Mechanism: {mechanism} ({len(mrows)} row(s)) --")
        for tier, row in sorted(mrows, key=lambda tr: (tr[0], -tr[1]["_rank"])):
            print_rank_breakdown(f"    T{tier} {row['name']}", row)

    print(f"\n  {ZURGO} displayed Tier 2 top {report_cap} (actual rank order, for eyeball):")
    for i, row in enumerate(full_tier2[:report_cap], 1):
        print_rank_breakdown(f"    #{i}", row)
    return True


def check_evergreen_floor_gate(built: dict, floor: int) -> bool:
    """v2.9 gate 4 (blocking): no anchor may gain a row whose ONLY kinship
    is an at/above-floor (evergreen) keyword. keyword_kinship_match()
    already floors DF before returning a match, so this should hold by
    construction -- this gate is the actual VERIFICATION, checking every
    keyword-mechanism row across every anchor really did clear the floor,
    rather than trusting the construction blindly. The floor is a ruling,
    not a knob -- any failure prints the offending keyword's DF, not a
    silent re-tune."""
    print(f"\nEvergreen floor gate (v2.9 gate 4, floor={floor}):")
    all_ok = True
    found_any = False
    for anchor_name, b in built.items():
        for tier in (1, 2):
            for row in b["full_tiers"][tier]:
                if row.get("_mechanism") != "keyword":
                    continue
                found_any = True
                df = row.get("_fragment_df")
                ok = df is not None and df <= floor
                all_ok = all_ok and ok
                status = "PASS" if ok else "STOP"
                print(f"  [{status}] {anchor_name} T{tier} {row['name']}: keyword={row['fragment']!r} DF={df}")
    if all_ok:
        note = "no keyword-kinship rows exist yet" if not found_any else "all keyword-kinship rows verified <= floor"
        print(f"  [PASS] {note}")
    return all_ok


def parse_report_tier_names(report_path: Path, tier: int) -> list:
    """Extracts the ordered candidate-name list from a tier's displayed
    table in an already-written report file -- used as the 'before'
    baseline for the stability gate. [] if the file/tier isn't found."""
    if not report_path.exists():
        return []
    header_re = re.compile(rf"^## Tier {tier} —")
    names = []
    in_section = False
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if header_re.match(line):
            in_section = True
            continue
        if not in_section:
            continue
        if line.startswith("## "):
            break
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] != "Name":
                names.append(cells[0])
    return names


def check_stability_gate(anchor_names: list, built: dict, ngram_min_len: int, legacy_ngram_index: dict,
                          legacy_ngram_df: dict, ngram_index: dict, ngram_df: dict, card_docs: dict,
                          blocking: bool = True) -> bool:
    """v2.4 gate 4. Downgraded to informational for v2.5 (session amendment,
    superseded standing ruling 5 and v2.5 change-order gate 3), then
    REINSTATED BLOCKING by v2.9 gate 3 ("any movement NOT explained by a
    keyword or reminder term = STOP") -- v2.9's own new-fact terms
    (Mechanism 1/2's "keyword"/"reminder" _mechanism tag) are added to the
    "explained" criteria alongside v2.4's polarity/condition terms and
    v2.5's affinity_term; a row that moved/exited for any of those reasons
    still passes.

    Captain's ruling (v2.9, post-run ruling on the Sakura finding): a
    within-tier REORDER (no entries/exits) is NOT accepted as "explained"
    merely because the anchor has zero keyword rows of its own. It must be
    TRACED: either the moved row's own fragment DF grew (trace_df_drift on
    itself) or some OTHER row in the tier's DF grew and is named as the
    cause -- in both cases the culprit reminder-injecting card(s) are
    printed by name. A reorder that can't be traced to a named DF delta
    still STOPs, even with no entries/exits and no anchor keyword rows.

    Baseline is read from the report files as they stood before this run's
    writes (still on disk at gate-check time, since main() only writes
    after all gates pass). Newly ENTERED rows are never individually
    checked -- v2.9 gate 3 explicitly calls new keyword/reminder-driven
    rows "expected and non-blocking", the same principle v2.5 established
    for affinity-driven entries."""
    print(f"\nStability gate ({'blocking (v2.9 gate 3)' if blocking else 'informational only, not blocking'}):")
    all_ok = True
    for anchor_name in anchor_names:
        report_path = REPORTS_DIR / f"{filename_slug(anchor_name)}.md"
        checked_any_tier = False
        for tier in (1, 2):
            baseline_names = parse_report_tier_names(report_path, tier)
            if not baseline_names:
                continue
            checked_any_tier = True
            current_rows = built[anchor_name]["displayed_tiers"][tier]
            full_rows = built[anchor_name]["full_tiers"][tier]
            full_rows_by_name = {r["name"]: r for r in full_rows}
            current_names = [r["name"] for r in current_rows]

            if baseline_names == current_names:
                print(f"  [PASS] {anchor_name} Tier {tier}: unchanged ({len(current_names)} rows)")
                continue

            entered = [n for n in current_names if n not in baseline_names]
            exited = [n for n in baseline_names if n not in current_names]
            moved = [
                n for n in current_names
                if n in baseline_names and current_names.index(n) != baseline_names.index(n)
            ]
            print(f"  {anchor_name} Tier {tier}: entered={entered} exited={exited} moved={moved}")

            # Pre-trace every "text"-mechanism row in the tier ONCE, so a moved
            # row that's stable itself can cite a NAMED sibling culprit instead
            # of a bare "something else moved" claim.
            drift_by_name = {}
            for row in full_rows:
                if row.get("_mechanism") == "text" and row.get("fragment"):
                    drift_by_name[row["name"]] = trace_df_drift(
                        row["fragment"], ngram_min_len, legacy_ngram_index, legacy_ngram_df,
                        ngram_index, ngram_df, card_docs,
                    )
            sibling_culprits = sorted({
                f"{name}: {format_culprit_list(d['culprits'])}"
                for name, d in drift_by_name.items() if d["own_df_changed"] and d["culprits"]
            })
            # Phase 3 rebalance: a row whose OWN mv_delta is unaffected (0, or
            # on the unchanged side) can still legitimately shift RANK
            # POSITION because some OTHER row in the same tier got a
            # different score from the asymmetric MV ladder -- named here so
            # that's a traced cause, not a bare "something else moved" claim.
            sibling_mv_names = sorted({
                r["name"] for r in full_rows
                if r.get("_mv_delta") not in (None, 0) and (
                    (r["_mv_delta"] > 0 and MV_PRICIER_MULT != 1.0)
                    or (r["_mv_delta"] < 0 and MV_CHEAPER_MULT != 1.0)
                )
            })
            # Cumulative fragment scoring (2026-07-10 ruling): same sibling
            # principle -- a row that itself gained no extra run can still
            # shift position because ANOTHER row in the tier got boosted by
            # one, named here so that's traced, not a bare mystery.
            sibling_cumulative_names = sorted({
                r["name"] for r in full_rows if r.get("_extra_fragments")
            })

            unexplained = []
            for name in set(exited) | set(moved):
                row = full_rows_by_name.get(name)
                mechanism = row.get("_mechanism") if row else None
                # Phase 3 rebalance (Captain ruling): the asymmetric MV ladder
                # is a NEW source of score movement distinct from the v2.9
                # keyword/reminder/DF-drift categories above -- a row whose
                # own MVΔ sign actually falls on the side the current
                # MV_PRICIER_MULT/MV_CHEAPER_MULT ratio changed is explained
                # by that, not a mystery.
                row_mv_delta = row.get("_mv_delta") if row else None
                mv_asymmetry_fired = bool(row) and row_mv_delta is not None and (
                    (row_mv_delta > 0 and MV_PRICIER_MULT != 1.0)
                    or (row_mv_delta < 0 and MV_CHEAPER_MULT != 1.0)
                )
                # Cumulative fragment scoring (2026-07-10 ruling): a row with
                # a non-empty _extra_fragments list gets rank contribution
                # from a second+ shared run -- a NAMED, ruling-driven cause
                # of movement, same status as the keyword/reminder mechanism
                # carve-out above, not a DF-drift mystery to trace.
                cumulative_scoring_fired = bool(row) and bool(row.get("_extra_fragments"))
                term_fired = bool(row) and (
                    row.get("_polarity_term", 0) > 0 or row.get("_condition_term", 0) > 0
                    or row.get("_affinity_term", 0) > 0
                    or mechanism in ("keyword", "reminder", "keyword_grant", "sentence")
                    or mv_asymmetry_fired or cumulative_scoring_fired
                )
                own_drift = drift_by_name.get(name, {"own_df_changed": False, "culprits": []})
                own_traced = own_drift["own_df_changed"] and bool(own_drift["culprits"])
                sibling_traced = (not term_fired) and (not own_traced) and bool(sibling_culprits)
                sibling_mv_traced = (
                    not term_fired and not own_traced and not sibling_traced and bool(sibling_mv_names)
                )
                sibling_cumulative_traced = (
                    not term_fired and not own_traced and not sibling_traced and not sibling_mv_traced
                    and bool(sibling_cumulative_names)
                )
                fired = term_fired or own_traced or sibling_traced or sibling_mv_traced or sibling_cumulative_traced
                detail = f"mechanism={mechanism}"
                if cumulative_scoring_fired:
                    n_extra = len(row.get("_extra_fragments") or [])
                    detail += f", cumulative fragment scoring ({n_extra} extra run(s))"
                if mv_asymmetry_fired:
                    detail += f", MV asymmetry (MVΔ={row_mv_delta:+g})"
                if own_traced:
                    detail += f", own DF drift: {format_culprit_list(own_drift['culprits'])}"
                elif sibling_traced:
                    detail += f", sibling DF drift: {'; '.join(sibling_culprits)}"
                elif sibling_mv_traced:
                    detail += f", sibling MV asymmetry: {', '.join(sibling_mv_names[:5])}{'...' if len(sibling_mv_names) > 5 else ''}"
                elif sibling_cumulative_traced:
                    detail += (
                        f", sibling cumulative fragment scoring: "
                        f"{', '.join(sibling_cumulative_names[:5])}{'...' if len(sibling_cumulative_names) > 5 else ''}"
                    )
                print(
                    f"    {name}: polarity_term={row.get('_polarity_term', 0) if row else 'n/a'}, "
                    f"condition_term={row.get('_condition_term', 0) if row else 'n/a'}, "
                    f"affinity_term={row.get('_affinity_term', 0) if row else 'n/a'}, {detail} "
                    f"({'explained' if fired else 'UNEXPLAINED'})"
                )
                if not fired:
                    unexplained.append(name)
            for name in entered:
                print(f"    {name}: entered (new row; no baseline penalty to compare)")

            if unexplained:
                label = "STOP" if blocking else "INFO"
                tail = "" if blocking else " (informational only -- not a gate failure)"
                print(f"    [{label}] unexplained movement for {anchor_name} Tier {tier}: {unexplained}{tail}")
                if blocking:
                    all_ok = False
            else:
                print(f"    [PASS] all movement for {anchor_name} Tier {tier} explained (polarity/condition/affinity/keyword/reminder/traced DF drift)")

        if not checked_any_tier:
            print(f"  [INFO] {anchor_name}: no baseline Tier 1/2 rows found on disk -- nothing to diff")
    return all_ok if blocking else True


# ---------------------------------------------------------------------------
# Tagger cross-check appendix (report appendix, non-blocking, validation source only)
# ---------------------------------------------------------------------------

SCOPE_TAG_SLUG_PATTERN = re.compile(r"opponent|symmetr|target", re.IGNORECASE)


def find_scope_adjacent_tags(tag_index: dict) -> list:
    return sorted(slug for slug in tag_index if SCOPE_TAG_SLUG_PATTERN.search(slug))


def infer_tag_scope(slugs: list) -> str:
    """Best-effort heuristic mapping a card's scope-adjacent tag slugs to a
    scope bucket, for this cross-check ONLY -- not used anywhere in ranking.
    The regex extractor is primary (scope is per-ability; tags are per-card)."""
    joined = " ".join(slugs).lower()
    if "symmetr" in joined:
        return "symmetric"
    if "opponent" in joined:
        return "all_opp"
    if "target" in joined:
        return "single"
    return "unknown"


def build_tagger_scope_crosscheck(built: dict, card_tags: dict, tag_index: dict) -> str:
    scope_tags = find_scope_adjacent_tags(tag_index)
    lines = [
        "# Tagger cross-check: regex scope vs tag-implied scope",
        "",
        "Report appendix, non-blocking. Validation source only -- the regex "
        "extractor is primary (scope is derived per-ability; tags are per-card, "
        "a coarser signal). Rows below are cards where the two disagree.",
        "",
    ]
    if not scope_tags:
        lines.append("No scope-adjacent tag slugs (opponent/symmetr/target family) found in the tag corpus.")
        return "\n".join(lines) + "\n"

    lines.append(f"Scope-adjacent tag slugs found ({len(scope_tags)}): {', '.join(scope_tags)}")
    lines.append("")
    lines.append("| Anchor | Candidate | Regex scope | Tag-implied scope | Matching tag slugs |")
    lines.append("|---|---|---|---|---|")

    scope_tag_set = set(scope_tags)
    seen_pairs = set()
    count = 0
    for anchor_name, b in built.items():
        if count >= 50:
            break
        for tier in (1, 2):
            if count >= 50:
                break
            for row in b["full_tiers"][tier]:
                if count >= 50:
                    break
                fp = row.get("_fact_penalties")
                oracle_id = row.get("oracle_id")
                if not fp or not oracle_id:
                    continue
                key = (anchor_name, oracle_id)
                if key in seen_pairs:
                    continue
                regex_scope = fp["candidate_scope"]
                if regex_scope == "unknown":
                    continue
                candidate_slugs = [e["slug"] for e in card_tags.get(oracle_id, []) if e["slug"] in scope_tag_set]
                if not candidate_slugs:
                    continue
                tag_scope = infer_tag_scope(candidate_slugs)
                if tag_scope == "unknown" or tag_scope == regex_scope:
                    continue
                seen_pairs.add(key)
                count += 1
                lines.append(
                    f"| {anchor_name} | {row['name']} | {regex_scope} | {tag_scope} | "
                    f"{', '.join(candidate_slugs)} |"
                )

    if count == 0:
        lines.append("")
        lines.append("_No disagreements found among candidates carrying a scope-adjacent tag._")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def filename_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-+", "-", slug)


TIER_TITLES = {
    0: "Tier 0 — Functional reprint (full text + frame gate: mana cost, type line, P/T all equal)",
    1: "Tier 1 — Whole ability shared verbatim",
    2: "Tier 2 — Shared verbatim fragment below the n-gram DF floor",
    3: "Tier 3 — Tag-overlap proposal (rule-proposed, not human-confirmed)",
}
# Which evidence header + extra ranking column (name, row key) each tier uses.
TIER_TABLE_SPEC = {
    0: ("Full normalized text (keywords included)", None, None),
    1: ("Shared ability paragraph", "Rank", "rank_display"),
    2: ("Shared fragment (DF)", "Rank", "rank_display"),
    3: ("Shared tags (idf, directness)", "Score", "extra"),
}


def render_table(rows: list, evidence_header: str, extra_column: str = None, extra_key: str = "extra") -> str:
    header = ["Name", evidence_header, "MV Δ", "CI relation", "Type bucket", "Keywords shared"]
    if extra_column:
        header.insert(1, extra_column)
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for row in rows:
        cells = [row["name"], row["evidence"], row["facts"]["mv_delta"],
                 row["facts"]["ci_relation"], row["facts"]["type_bucket"],
                 row["facts"]["keyword_overlap"]]
        if extra_column:
            cells.insert(1, row[extra_key])
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def compute_candidate_rows(anchor_doc: dict, anchor_tags: list, anchor_tags_t3: list, card_docs: dict,
                            card_tags: dict, card_tags_t3: dict, pool: set, ngram_df: dict, clause_df: dict, keyword_df: dict,
                            paragraph_index: dict, idf: dict, idf_t3: dict, n_total_cards: int,
                            args: argparse.Namespace) -> tuple:
    """Builds tiers[0..3], each a list of rows, SORTED (rank/score/name) but
    NOT yet capped -- callers decide capping and file-splitting. Also
    returns `disqualified`: Tier-2 rows excluded outright by the v2.6
    amendment 1 corroboration gate (never appended to tiers[2], and -- since
    they have verbatim overlap by definition -- never eligible for Tier 3
    either, so they simply vanish from this anchor's report)."""
    tiers = {0: [], 1: [], 2: [], 3: []}
    disqualified = []
    for oracle_id in pool:
        candidate_doc = card_docs[oracle_id]
        result = assign_tier(anchor_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        facts = fact_columns(anchor_doc, candidate_doc)

        # Tag overlap score computed for EVERY candidate regardless of tier
        # (Amendment 1, v2.1): it both ranks Tier 1/2 and qualifies Tier 3.
        # v2.6 amendment 2: a SEPARATE, extended computation (tag_score_t3,
        # via card_tags_t3/idf_t3 which add rule:turn-scoped) feeds ONLY
        # Tier 3 qualification/scoring below -- the base tag_score here
        # (Tagger tags only) still feeds Tier 1/2 rank AND the amendment 1
        # corroboration check, unchanged, per the change order's explicit
        # "do NOT feed it into Tier 2's tag_score term this round."
        candidate_tags = card_tags.get(oracle_id, [])
        tag_score, matched = tier3_score(anchor_tags, candidate_tags, idf, args.inherited_discount)
        candidate_tags_t3 = card_tags_t3.get(oracle_id, [])
        tag_score_t3, matched_t3 = tier3_score(anchor_tags_t3, candidate_tags_t3, idf_t3, args.inherited_discount)

        if result is not None:
            tier = result["tier"]
            candidate_mv_delta = mv_delta(anchor_doc, candidate_doc)
            row = {"name": candidate_doc["name"], "oracle_id": oracle_id, "evidence": result["evidence"],
                   "facts": facts, "fragment": result["fragment"], "_mv_delta": candidate_mv_delta,
                   "_mechanism": result["mechanism"], "_keyword": result["keyword"],
                   "_anchor_param": result["anchor_param"], "_candidate_param": result["candidate_param"],
                   "_anchor_mana_fact": result["anchor_mana_fact"],
                   "_candidate_mana_fact": result["candidate_mana_fact"],
                   "_granted_keyword_pt_distance": result["granted_keyword_pt_distance"],
                   "_reminder_keyword": result["reminder_keyword"],
                   "_corroboration": result["corroboration"],
                   # First-class phrase bucket (2026-07-11): checked against
                   # full card text, not the winning fragment -- see
                   # promoted_phrase_shared()'s own docstring for why.
                   "_promoted": promoted_phrase_shared(anchor_doc, candidate_doc)}
            if tier in (1, 2):
                fact_penalties = compute_fact_penalties(anchor_doc, candidate_doc, result["fragment"])

                if tier == 2 and tier2_corroboration_disqualified(fact_penalties, tag_score):
                    disqualified.append({
                        "name": candidate_doc["name"], "oracle_id": oracle_id,
                        "anchor_polarity": fact_penalties["anchor_polarity"],
                        "candidate_polarity": fact_penalties["candidate_polarity"],
                        "tag_score": tag_score,
                    })
                    continue  # excluded outright -- v2.6 amendment 1, the one exception to ruling 6

                # v2.7 viewer export: capture the DF this already computes (previously
                # discarded via `_`) so a row's fragment DF is available as a plain
                # number, not just baked into the "evidence" display string. Pure data
                # capture -- frag_idf (the only value that feeds the rank formula below)
                # is unchanged, so this cannot alter any score, tier, or report output.
                if result["mechanism"] == "mana":
                    # Phase 4 (ratified, R5): mana kinship has no text
                    # fragment to scale by length -- a flat baseline minus
                    # the cascade penalty (mana_cascade_penalty()) is the
                    # entire rank signal. rank_fragment is a length-neutral
                    # dummy (exactly ngram_min_len words) so compute_rank's
                    # sqrt(length/ngram_min_len) term becomes 1.0 and never
                    # rescales this baseline by accident.
                    frag_idf = MANA_KINSHIP_BASE_RANK - result["mana_cascade_penalty"]
                    frag_df = None
                    rank_fragment = " ".join(["x"] * args.ngram_min_len)
                elif result["mechanism"] == "keyword_grant":
                    # Entry #4 (Captain's ruling, 2026-07-10), extended
                    # 2026-07-12 to also cover the former team_pump's
                    # mass-pump-shaped facts (same mechanism now): same
                    # length-neutral-dummy shape as mana kinship above -- a
                    # flat baseline minus the mismatch penalty is the
                    # entire rank signal, no natural corpus-DF analog for a
                    # granted-keyword SET.
                    frag_idf = GRANT_KINSHIP_BASE_RANK - result["granted_keyword_penalty"]
                    frag_df = None
                    rank_fragment = " ".join(["x"] * args.ngram_min_len)
                elif result["mechanism"] == "vanilla_creature":
                    # Vanilla-creature frame mismatch (Captain's ruling,
                    # 2026-07-12): same length-neutral-dummy shape as mana/
                    # keyword_grant above -- no text at all to derive an idf
                    # from, and no mismatch-specific penalty term either (the
                    # generic, unconditional rank terms below -- mv_term,
                    # ci_step, affinity -- already carry mana-cost/color/type
                    # distance for every mechanism; inventing a redundant
                    # frame-distance penalty on top wasn't corpus-measured,
                    # so this stays a flat baseline like the other two until
                    # a real ranking gap is found).
                    frag_idf = VANILLA_CREATURE_BASE_RANK
                    frag_df = None
                    rank_fragment = " ".join(["x"] * args.ngram_min_len)
                else:
                    frag_idf, frag_df = compute_fragment_idf(
                        result["fragment"], result["fragment_df"], result["fragment_df_exact"],
                        ngram_df, args.ngram_min_len, paragraph_index, n_total_cards,
                    )
                    rank_fragment = result["fragment"]
                affinity = compute_affinity(
                    anchor_doc, candidate_doc, args.type_match_bonus, args.subtype_bonus,
                    args.subtype_bonus_cap,
                )
                # Phase 3 (ratified, R1/R3): the commonality-band weight (and
                # R1's harder both-sides-injected override) scales ONLY the
                # text-evidence idf term, never tag_score -- "qualification
                # surfaces; weight buries" (DRAFT RULING 1), applied here so
                # every downstream term (raw, final, rank_display) reflects it.
                # Phase 3 rebalance (Captain ruling): frame affinity (type +
                # subtype only -- MV lives in mv_term now) partially restores
                # a discounted weight toward 1.0.
                restored_fraction = restoration_fraction(
                    affinity["affinity_term"], args.type_match_bonus, args.subtype_bonus_cap,
                )
                effective_weight = result["commonality_weight"] + (
                    1.0 - result["commonality_weight"]
                ) * restored_fraction
                frag_idf *= effective_weight
                ci_step, ci_colors_added = ci_relation_step_value(
                    set(anchor_doc["color_identity"]), set(candidate_doc["color_identity"]), facts["ci_relation"],
                )
                # Cumulative fragment scoring (2026-07-10 ruling): each extra
                # run gets its OWN idf/band-weight (same blend as the primary
                # run's frag_idf *= effective_weight above -- restored_fraction
                # is fragment-independent, reused as-is), then a position-based
                # diminishing run_weight (fragment_run_weight: 1.0 primary,
                # 0.5 2nd run, 0.25 3rd+ -- a floor, not continued decay) so
                # several weak extra runs can never outweigh one strong primary
                # run. Empty for every row unaffected by this feature (the
                # overwhelming majority), leaving compute_rank byte-identical.
                extra_fragment_terms = []
                extra_fragments_export = []
                for extra in result["extra_fragments"]:
                    extra_idf, extra_df = compute_fragment_idf(
                        extra["text"], extra["df"], extra["df_exact"],
                        ngram_df, args.ngram_min_len, paragraph_index, n_total_cards,
                    )
                    extra_effective_weight = extra["commonality_weight"] + (
                        1.0 - extra["commonality_weight"]
                    ) * restored_fraction
                    extra_idf *= extra_effective_weight
                    extra_term = extra["run_weight"] * extra_idf * math.sqrt(extra["length"] / args.ngram_min_len)
                    extra_fragment_terms.append(extra_term)
                    extra_fragments_export.append({
                        "text": extra["text"], "df": extra_df, "df_exact": extra["df_exact"],
                        "length": extra["length"], "run_weight": extra["run_weight"],
                    })
                breakdown = compute_rank(
                    rank_fragment, frag_idf, tag_score, ci_step, candidate_mv_delta,
                    fact_penalties, affinity, args.ngram_min_len, args.tag_score_weight, args.ci_penalty,
                    args.mv_penalty, args.scope_penalty, args.duration_penalty, args.exception_penalty,
                    args.polarity_penalty, args.condition_penalty, tuple(extra_fragment_terms),
                    promoted=row["_promoted"],
                )
                row["_rank"] = breakdown["final"]
                row["_raw_score"] = breakdown["raw"]
                row["_ci_step"] = ci_step
                row["_ci_colors_added"] = ci_colors_added
                row["_ci_term"] = breakdown["ci_term"]
                row["_mv_term"] = breakdown["mv_term"]
                row["_scope_term"] = breakdown["scope_term"]
                row["_duration_term"] = breakdown["duration_term"]
                row["_exception_term"] = breakdown["exception_term"]
                row["_polarity_term"] = breakdown["polarity_term"]
                row["_condition_term"] = breakdown["condition_term"]
                row["_affinity_term"] = breakdown["affinity_term"]
                row["_promoted_term"] = breakdown["promoted_term"]
                row["_type_match"] = affinity["type_match"]
                row["_shared_subtypes"] = affinity["shared_subtypes"]
                row["_fact_penalties"] = fact_penalties
                row["_fragment_len"] = len(result["fragment"].split())
                row["_fragment_df"] = frag_df
                row["_fragment_df_exact"] = result["fragment_df_exact"]
                row["_commonality_band"] = result["commonality_band"]
                row["_commonality_weight"] = result["commonality_weight"]
                row["_effective_weight"] = effective_weight
                row["_extra_fragments"] = extra_fragments_export
                row["rank_display"] = (
                    f"{breakdown['final']:.2f} ({breakdown['raw']:.2f} - "
                    f"{breakdown['ci_term']:.2f} - {breakdown['mv_term']:.2f} - "
                    f"{breakdown['scope_term']:.2f} - {breakdown['duration_term']:.2f} - "
                    f"{breakdown['exception_term']:.2f} - {breakdown['polarity_term']:.2f} - "
                    f"{breakdown['condition_term']:.2f} + {breakdown['affinity_term']:.2f} + "
                    f"{breakdown['promoted_term']:.2f})"
                )
                row["_tag_score"] = tag_score
                row["_weighted_tag_score"] = args.tag_score_weight * tag_score
            tiers[tier].append(row)
            continue

        if tag_score_t3 >= args.tier3_threshold:
            tiers[3].append({
                "name": candidate_doc["name"],
                "oracle_id": oracle_id,
                "evidence": format_tier3_evidence(matched_t3),
                "extra": f"{tag_score_t3:.2f}",
                "facts": facts,
                "_score": tag_score_t3,
                "_matched_t3": matched_t3,
            })

    def mv_abs_key(row):
        d = row.get("_mv_delta")
        return abs(d) if d is not None else float("inf")

    # Captain's ruling, 2026-07-10: mechanism="keyword" (Mechanism 1, an
    # exact NAMED keyword match) must ALWAYS sort above mechanism="reminder"
    # (Mechanism 2, reminder-injected text) -- a guaranteed categorical
    # sort key, not a scalar rank bonus, so the ordering can never be
    # undone by future DF/corpus drift the way a bonus-sized-for-today's-
    # data silently could. Scoped narrowly to keyword-vs-reminder only, per
    # ruling -- "text"/"mana"/"keyword_grant" rows are UNCHANGED, still
    # competing purely on rank score among themselves and against reminder
    # rows exactly as before (confirmed live: Hanweir Garrison, reminder,
    # was outranking Zurgo Stormrender, keyword, in Zurgo's Tier 2).
    # Second-class phrase bucket (Captain's ruling, 2026-07-10) -- see
    # SECOND_CLASS_PHRASE_PATTERNS's own comment for the full rationale.
    # A row's entire winning evidence -- the primary fragment AND every
    # cumulative-scoring extra run (Entry #5) -- must match the house-
    # curated phrase list for the demotion to fire; if even ONE run is
    # genuine non-listed text, the row stays in the normal competitive
    # pool (same "all runs must agree" discipline as Entry #8's boilerplate
    # override check). Scoped to the mechanisms whose evidence is a
    # literal matchable string (text/reminder/sentence) -- keyword_grant's
    # synthetic "granted-keyword kinship: ..." string and mana's "mana
    # kinship: ..." string can never match a phrase pattern by
    # construction, so scoping is a clarity choice, not a correctness one.
    # Placed FIRST in the sort tuple, ahead of keyword_over_reminder_
    # priority/pt_exactness_priority below -- Captain's own framing
    # ("assuredly appears near the bottom") means this demotion must
    # dominate every other consideration, not just compete within its own
    # mechanism the way pt_exactness_priority scopes itself.
    #
    # Reminder-KEYWORD bucket (Captain's ruling, 2026-07-12) -- see
    # SECOND_CLASS_REMINDER_KEYWORDS' own comment for the full rationale
    # and the measured Sen Triplets/Myrel collision a first-draft text-
    # pattern version of this same fix had to correct. Checked via
    # row-level PROVENANCE (`_reminder_keyword`, set only when mechanism
    # == "reminder" -- see assign_tier()'s `reminder_keyword_source`),
    # never via text matching, so it can never fire against a card's own
    # native printed text. Scoped to the PRIMARY fragment only -- a
    # cumulative-scoring extra run (Entry #5) has no per-run reminder-
    # keyword attribution of its own, so it still falls back to the plain
    # text-pattern check below, same "all runs must agree" discipline as
    # before.
    def second_class_priority(row):
        mechanism = row.get("_mechanism")
        if mechanism not in ("text", "reminder", "sentence"):
            return 0
        fragment = row.get("fragment")
        if not fragment:
            return 0
        primary_is_second_class = is_second_class_phrase(fragment) or (
            mechanism == "reminder" and row.get("_reminder_keyword") in SECOND_CLASS_REMINDER_KEYWORDS
        )
        if not primary_is_second_class:
            return 0
        for extra in row.get("_extra_fragments") or []:
            if not is_second_class_phrase(extra.get("text", "")):
                return 0
        return 1

    def keyword_over_reminder_priority(row):
        return 0 if row.get("_mechanism") == "keyword" else 1

    # Captain's ruling, 2026-07-10 (Entry #7 follow-up): "exact buff gets
    # priority, then near buffs" for granted-keyword-SET (Equipment/Aura)
    # matches, FULLY graduated by P/T distance, guaranteed regardless of
    # tag_score/affinity/other unrelated rank terms -- not just a scalar
    # penalty blended into the same score, which those other terms could
    # swamp. A single global sort can't make "exact beats near" absolute
    # for keyword_grant rows while ALSO leaving every other mechanism's
    # ordering completely untouched (a text-mechanism row's rank could
    # legitimately fall between two keyword_grant rows of different P/T
    # distance -- a real contradiction in a strict total order, not an
    # oversight). Pragmatic resolution, same shape as keyword_over_
    # reminder_priority above: an EXACT-match (distance 0, including "no
    # P/T mod on either side") keyword_grant row stays in the normal pool,
    # competing on rank exactly as before, unaffected. Only a NON-exact
    # match gets pushed into a lower, graduated priority tier (1 per point
    # of distance) below that pool -- guarantees exact > near > far AMONG
    # keyword_grant rows, at the cost of a near/far-match keyword_grant row
    # also sorting below every other mechanism's rows, not just above
    # closer keyword_grant matches. Not scoped to any other mechanism.
    def pt_exactness_priority(row):
        if row.get("_mechanism") != "keyword_grant":
            return 0
        return row.get("_granted_keyword_pt_distance") or 0

    tiers[0].sort(key=lambda r: r["name"])
    tiers[1].sort(key=lambda r: (
        second_class_priority(r), keyword_over_reminder_priority(r), pt_exactness_priority(r),
        -r["_rank"], -r["_fragment_len"], mv_abs_key(r), r["name"],
    ))
    tiers[2].sort(key=lambda r: (
        second_class_priority(r), keyword_over_reminder_priority(r), pt_exactness_priority(r),
        -r["_rank"], -r["_fragment_len"], mv_abs_key(r), r["name"],
    ))
    tiers[3].sort(key=lambda r: (-r["_score"], r["name"]))

    return tiers, disqualified


def render_anchor_report(anchor_name: str, card_docs: dict, card_tags: dict, pool_size: int,
                          full_tiers: dict, report_cap: int, args: argparse.Namespace) -> tuple:
    """Renders the main report body (capped) and, for any tier that
    truncates, a companion full-list table. Returns (report_md_body,
    counts_before_cap, displayed_tiers, full_list_paths)."""
    counts_before_cap = {t: len(rows) for t, rows in full_tiers.items()}
    displayed_tiers = {t: rows[:report_cap] for t, rows in full_tiers.items()}
    full_list_files = {}  # tier -> {"filename": str, "content": str}, only for tiers that truncate

    lines = [f"# Tier report — {anchor_name}", ""]
    lines.append(
        f"**DEVIATION from TIER-ENGINE-V2.1-CHANGE-ORDER.md Amendment 1, ratified by Captain:** "
        f"the rank formula's length term uses `sqrt(len(fragment)/NGRAM_MIN_LEN)`, not the "
        f"spec'd linear `len(fragment)/NGRAM_MIN_LEN`. Spec formula: "
        f"`rank = ngram_idf(f) * (len(f)/NGRAM_MIN_LEN) + TAG_SCORE_WEIGHT*tag_score`. "
        f"Ratified formula: `rank = ngram_idf(f) * sqrt(len(f)/NGRAM_MIN_LEN) + TAG_SCORE_WEIGHT*tag_score`. "
        f"Reason: the linear term let an 8-token generic trigger-template fragment outrank Myrel's "
        f"5-token, rarer, thematically-precise token description; no TAG_SCORE_WEIGHT value (tested "
        f"3-20) fixed it. See NGRAM_LENGTH_DAMPENING in tier_engine.py's constants block."
    )
    lines.append("")
    lines.append(
        f"**DEVIATION from TIER-ENGINE-V2.1-CHANGE-ORDER.md Amendment 4.3, ratified by Captain:** "
        f"after the sqrt fix above, the boilerplate-burial validation gates were themselves found "
        f"miscalibrated, not the engine output. Two fixes, both to the GATE (no further engine/rank "
        f"changes): (1) \"boilerplate cluster\" membership requires exact fragment IDENTITY, not "
        f"substring containment -- a longer, rarer superstring match (e.g. Darksteel Splicer's "
        f"9-token DF~3 fragment) is a distinct, legitimate match, not boilerplate, even though it "
        f"contains the boilerplate phrase as a substring. (2) A fragment-identical row is still "
        f"exempted from \"junk\" classification if its weighted tag-score contribution "
        f"(TAG_SCORE_WEIGHT * tag_score) is >= {BURIAL_GATE_TAG_EXEMPT_THRESHOLD} -- a "
        f"boilerplate-fragment candidate that also carries strong shared tags is a legitimate "
        f"functional cousin, not noise the tag system should be punished for surfacing."
    )
    lines.append("")
    lines.append(
        f"**DEVIATION from the v2.3 CI-step table (TIER-ENGINE-V2.3-CHANGE-ORDER.md), ratified by "
        f"Captain as v2.5 amendment 2:** the \"superset\" CI relation is now GRADED, not flat. Old: "
        f"`CI_RELATION_STEP[\"superset\"] = 2` for every superset regardless of width. New: "
        f"`superset_step = min(1 + colors_added, {SUPERSET_STEP_CAP})`, where colors_added is the "
        f"count of colors the candidate's color identity adds beyond the anchor's (a +1-color "
        f"superset stays at step 2, the old flat value -- only WIDE supersets move). same/subset/"
        f"overlapping/disjoint are unchanged flat steps. Reason: the v2.5 frame-affinity bonus "
        f"correctly gave Sen Triplets +0.25 for a real shared \"Human\" subtype with Grand Abolisher, "
        f"which then resurfaced it in Abolisher's displayed Tier 2 top 10 -- not because the affinity "
        f"bonus was wrong, but because the flat superset step was undercharging Sen Triplets' actual "
        f"CI distance (mono-W anchor vs WUB, +2 colors). Ratified as the cheap intermediate step "
        f"toward the backlogged per-color pip-vector comparator (see "
        f"THESAURUS-TIER-PROTOTYPE-HANDOFF.md's deferred/backlog list) -- not itself that comparator."
    )
    lines.append("")
    lines.append(
        f"**DEVIATION from standing ruling 6 (\"qualification stays maximal, rank buries, never "
        f"excludes\"), ratified by Captain as v2.6 amendment 1:** a fragment-qualified Tier 2 "
        f"candidate is now DISQUALIFIED outright (removed from the report entirely, not merely "
        f"buried in rank) when BOTH (a) its polarity is a functional inversion of the anchor's "
        f"(polarity_mismatch=True, the existing extractor's own output) AND (b) it shares literally "
        f"zero weighted tag DNA with the anchor (tag_score=0.0, the same computation feeding the "
        f"{TAG_SCORE_WEIGHT}*tag_score rank term). Reason: verbatim grammar across a functional "
        f"inversion with zero tag corroboration is phrase coincidence, not kinship -- there's nothing "
        f"left to bury, only noise. Tier 1 is untouched. See "
        f"tier2_corroboration_disqualified() in tier_engine.py."
    )
    lines.append("")
    lines.append(
        f"**DEVIATION (new fact source), v2.6 amendment 2:** Tier 3 scoring for this report uses an "
        f"EXTENDED, engine-derived tag not sourced from the Tagger index: `rule:turn-scoped`, "
        f"detecting turn-window-asymmetry phrasing (\"during your turn\", \"on your turn\", \"during "
        f"its controller's turn\", etc. -- excluding pure duration phrases like \"until end of turn\"). "
        f"This tag is injected into the anchor-directional tag-overlap computation for TIER 3 "
        f"QUALIFICATION AND SCORING ONLY -- it deliberately does NOT feed Tier 1/2's rank tag_score "
        f"term or the amendment 1 corroboration check this round (deferred pending a Drannith/Wrath "
        f"impact analysis, since Avatar's Wrath's own turn-window phrasing is duration-shaped -- "
        f"\"until your next turn\" -- and excluded by this fact's own definition anyway, but the "
        f"restriction to Tier 3 stands regardless). See the amendment 2 derivation block in this "
        f"run's terminal output for the regex, corpus DF, computed idf, and eyeball sample."
    )
    lines.append("")
    lines.append(
        f"**DEVIATION from Amendment 1, v2 (FROZEN tier-assignment core), ratified as v2.9 Mechanism "
        f"1 -- keyword kinship:** a shared keyword (Scryfall `keywords` array + a parsed param from "
        f"its own oracle-text line, e.g. \"Mobilize 2\" -> keyword=mobilize, param=\"2\") now "
        f"qualifies as a pseudo-fragment through the SAME DF-floor discipline that governs text "
        f"fragments (no new floor constant) -- same param -> Tier 1, different param -> Tier 2. "
        f"Evergreen keywords (flying, trample, haste...) never qualify, by construction: their corpus "
        f"DF is in the thousands, always above the floor. This is a PARALLEL qualification path, not "
        f"a repeal of the keyword-only-paragraph exclusion for VERBATIM text matching -- a bare "
        f"shared \"Flying\" still never mints a Tier 1/2 via TEXT comparison. See "
        f"keyword_kinship_match() in tier_engine.py."
    )
    lines.append("")
    lines.append(
        f"**DEVIATION from Amendment 1, v2 (FROZEN tier-assignment core), ratified as v2.9 Mechanism "
        f"2 -- reminder-text injection:** for a SINGLE-keyword oracle-text line carrying reminder "
        f"text, the reminder body (extracted, not stripped) is now injected as an ordinary matchable "
        f"paragraph on BOTH anchor and candidate sides, attributed to that keyword -- this SUPERSEDES "
        f"the keyword-only-paragraph exclusion for that specific line (bare keywords with no reminder, "
        f"and multi-keyword comma lines, stay excluded exactly as before). The injected paragraph "
        f"runs through the EXISTING find_shared_paragraph/find_shared_fragment machinery and the "
        f"EXISTING ngram_df indexing, unchanged -- ubiquitous reminder text buries itself under the "
        f"same DF floor as any other fragment. NO-DOUBLE-COUNT: a keyword that already qualifies via "
        f"Mechanism 1 for a given pair has its Mechanism-2 reminder paragraph excluded from that "
        f"pair's text search (keyword identity wins). "
        f"AMENDED per Captain's post-run ruling: Mechanism 2 catches keyword-reminder <-> longhand "
        f"overlap BROADER than same-keyword templating, and that is BY DESIGN, not a defect -- once a "
        f"keyword's reminder is injected as ordinary matchable text, it is compared against EVERY "
        f"candidate's text, not just other instances of the same keyword. Grand Abolisher's original "
        f"\"HONEST EXPECTATION\" language (\"identical-templating longhand cards only\", Hero-of-"
        f"Bladehold-class cards \"out of verbatim reach by design\") was the author's PREDICTION, not a "
        f"gate: verified live, Hero of Bladehold DOES enter Zurgo, Thunder's Decree's Tier 2 (shared "
        f"6-token run \"whenever this creature attacks, create two\", DF≈6) because Zurgo's injected "
        f"Mobilize reminder and Hero's own plain ability text genuinely share that run -- a real "
        f"verbatim overlap, not word-order-chasing, and ratified as a PASS. No separate, stricter DF "
        f"floor for injected paragraphs -- same one-corpus-one-rarity-truth rationale that rejected a "
        f"forked DF table for the Sakura finding."
    )
    lines.append("")
    lines.append(
        f"**v2.9 ERRATUM (root-caused and fixed, not ratified):** verifying the no-double-count rule "
        f"on Devoted Mardu vs Zurgo, Thunder's Decree surfaced a PRE-EXISTING v1-era parser bug, not a "
        f"v2.9 regression -- REMINDER_RE = `re.compile(r\"\\([^)]*\\)\")` is a flat regex that cannot "
        f"express nested parentheses. Devoted Mardu's Mobilize reminder contains one (\"...Mardudes "
        f"(tapped and attacking 1/1 red Warrior creature tokens). Sacrifice them...\"), which the old "
        f"regex truncated at the INNER close-paren, leaving corrupted trailing text that broke keyword "
        f"classification and coincidentally string-matched Zurgo's injected reminder -- the exact "
        f"double-count the rule is supposed to prevent, caused by the keyword never being detected as "
        f"shared in the first place, not by a scoping bug in the suppression logic itself (verified: "
        f"suppression already covered both same- and different-param cases correctly). FIXED by "
        f"replacing REMINDER_RE with find_paren_spans(), a balanced-parenthesis depth-counter scanner "
        f"(a flat regex cannot express nesting; this was not attempted). Verified corpus-wide: exactly "
        f"1 of 38,233 cards was affected (Devoted Mardu); the fix's corpus-wide suspect scan (reminder-"
        f"mechanism row whose keyword is ALSO in that row's own Keywords-shared column) now returns "
        f"zero hits, down from 1. A SEPARATE, larger limitation was found during verification (NOT "
        f"fixed by erratum 1, out of its authorized scope) and is resolved below as erratum 2."
    )
    lines.append("")
    lines.append(
        f"**v2.9 ERRATUM 2 (root-caused and fixed):** is_keyword_only_paragraph()'s comma-fragment "
        f"classification required EVERY fragment to start with a keyword name, which failed on any "
        f"keyword line with a clarifying \"where X is...\" clause (e.g. \"Mobilize X, where X is your "
        f"devotion to Mardu.\") -- the \"where X is...\" fragment doesn't itself start with the keyword "
        f"name, so the whole line was misclassified as ordinary text and Mechanism 1 never saw that "
        f"card's keyword instance. Pre-existing since v1/v2, surfaced by erratum 1's fix. FIXED: "
        f"where_x_is_param() now recognizes \"<Keyword> <param>, where <param> is <clause>.\" as "
        f"keyword-only, validated against the card's own keywords array with the literal SAME param "
        f"token required in both places (never freetext keyword guessing; deliberately narrow -- an "
        f"unrelated em-dash ability-word construction like \"Domain -- Look at the top X cards..., "
        f"where X is...\" does not match). Devoted Mardu now re-enters Zurgo, Thunder's Decree's Tier "
        f"2 via keyword kinship (mobilize 2 vs mobilize X, different param -> Tier 2), its reminder "
        f"fragment correctly suppressed for the pair, and its Tier 3 row disappears (qualifies at its "
        f"best tier only). PRECISELY re-verified corpus-wide: 14 cards, not the 147 originally "
        f"estimated by a loose substring scan (that scan's bare 'where'/'is' check false-matched "
        f"things like \"anywhere\" containing \"where\", and over-counted unrelated em-dash "
        f"templates). A known minor over-sweep remains for lines where the where-clause is followed "
        f"by additional content in the same paragraph -- documented in KNOWN_LIMITATIONS, not further "
        f"engineered (verified to trip no blocking gate)."
    )
    lines.append("")
    lines.append(
        f"**Phase 3 (ratified, RULING-MANIFEST-2026-07-09.md R1/R2/R3) -- commonality bands + "
        f"provenance discount, confirmed against native-only distributions "
        f"(experiments/measure/PHASE-1-CLEAN-RECUT-MEMO.md):** closes F1 (Tier 1 had NO DF gate at "
        f"all -- Boros Charm minted 221 false Tier 1 rows off a bare \"choose one --\" header) and "
        f"extends Tier 2's old flat NGRAM_DF_FLOOR={NGRAM_DF_FLOOR} hard ceiling into a graduated "
        f"band. R2: paragraphs of >={args.ngram_min_len} tokens use ngram-scale DF (T2's existing "
        f"min-window scale); shorter paragraphs use para_exact_df with their OWN thresholds -- "
        f"ngram-scale DF is undefined below the window length. R3 band edges (T1 and T2 are "
        f"SEPARATELY declared constants, identical values by ruling): "
        f"long (>={args.ngram_min_len} tok) full-weight DF<={T1_LONG_FULL_WEIGHT_CEILING}, "
        f"discounted {T1_LONG_FULL_WEIGHT_CEILING + 1}-{T1_LONG_DISCOUNT_CEILING}, rescue zone "
        f"{T1_LONG_DISCOUNT_CEILING + 1}-{T1_LONG_RESCUE_CEILING} (qualifies, buried -- this is what "
        f"readmits the Lane 1c six: Growth Spiral, Garruk's Uprising, Cultivate, Rhystic Study, "
        f"Rampant Growth, Deadly Dispute), DEAD above {T1_LONG_RESCUE_CEILING}; short (<{args.ngram_min_len} "
        f"tok) full-weight exact_df<={T1_SHORT_FULL_WEIGHT_CEILING}, discounted "
        f"{T1_SHORT_FULL_WEIGHT_CEILING + 1}-{T1_SHORT_DISCOUNT_CEILING}, DEAD above "
        f"{T1_SHORT_DISCOUNT_CEILING} (no rescue zone for short paragraphs, R3). DEAD is ratified "
        f"qualification LAW (Captain: \"kill them, for now\") -- a SECOND lawful exception to "
        f"\"rank buries, never excludes,\" alongside the v2.6 amendment 1 corroboration gate; a "
        f"DEAD-band paragraph/fragment does not qualify at all (falls through to the next tier). "
        f"Every other band still qualifies -- only the WEIGHT differs, applied to the fragment_idf "
        f"term only (never tag_score): full={BAND_WEIGHTS['full']}, discounted="
        f"{BAND_WEIGHTS['discounted']}, rescue={BAND_WEIGHTS['rescue']} (Phase 3's own numeric "
        f"ruling, not part of the Phase 1 DF-edge measurement, which ratified edges only). R1: a "
        f"match whose evidence is v2.9 Mechanism-2-injected reminder text on BOTH sides is "
        f"discounted hard regardless of DF (weight={PROVENANCE_DISCOUNT_WEIGHT}, overriding the band "
        f"weight, not stacking with it) -- provenance is engine-known (it did the injecting), never "
        f"a named keyword/phrase list. A one-side-native match (the Hero-of-Bladehold class) keeps "
        f"full standing, ratified by-design. Mechanism 1 keyword kinship is UNAFFECTED (its own, "
        f"separate DF-floor discipline governs it, unchanged)."
    )
    lines.append("")
    lines.append(
        f"**Phase 3 REBALANCE (Captain ruling, RATIFIED, RULING-MANIFEST-2026-07-09.md):** the v2.5 "
        f"Drannith Magistrate > Avatar's Wrath gate STANDS -- the band discount above is never weakened "
        f"to preserve a pre-existing ordering. Two general mechanisms instead, both keyed only on "
        f"already-derived facts, no card identity: (1) frame-affinity restoration -- a band/provenance-"
        f"discounted fragment's effective weight is partially restored toward 1.0, proportional to type "
        f"match + shared creature subtype (affinity_term, 0-{TYPE_MATCH_BONUS + SUBTYPE_BONUS_CAP:.1f}); "
        f"see restoration_fraction(). (2) The mana-value penalty is now an ASYMMETRIC ladder replacing "
        f"the old symmetric one (one term, not two -- MV is never counted twice): same MV is still "
        f"strongest (MVΔ=0 -> zero penalty), the penalty still decays with |MVΔ| (distance dominant), "
        f"but a candidate costing MORE than the anchor gets a harsher per-distance multiplier "
        f"(MV_PRICIER_MULT={MV_PRICIER_MULT}) than one costing less (MV_CHEAPER_MULT={MV_CHEAPER_MULT}) "
        f"-- direction is a tiebreaker on distance, never a strict cheaper-always-wins bucket (verified: "
        f"a distance-1 pricier candidate penalizes the same as a distance-2.5 cheaper one). Cost "
        f"asymmetry only -- produced-mana amounts (Phase 4's mana-fact system) remain symmetric, an "
        f"unrelated axis. See mv_asymmetric_distance(). Ratified from a full-panel impact analysis "
        f"(~13.6% of within-tier pairs reorder -- expected and judged by explained-drift law + the "
        f"landmark/gate set, not a distortion ceiling; see "
        f"experiments/measure/PHASE-3-REBALANCE-SHAPES-MEMO.md). Basandra, Battle Seraph vs Myrel, "
        f"Shield of Argive (Marisi Tier 2) is UNGATED as a direct consequence -- neither ordering is an "
        f"expectation any longer, see check_basandra_gate()'s docstring for the full history."
    )
    lines.append("")
    lines.append(
        f"**Phase 4 (ratified, RULING-MANIFEST-2026-07-09.md R5/R6) -- mana-fact extraction + pip "
        f"kinship, PARALLEL to text/keyword matching (R4), never a replacement.** Mana-producing "
        f"abilities are parsed into facts (colors AS A SET, colorless amount, total amount, source "
        f"class + repeatability, any-color/CI-restricted, hybrid, mixed) -- see parse_mana_fact(). R6: "
        f"same mana-ability SHAPE (source class + repeatable) sharing >=1 produced pip (or, for the "
        f"pure-colorless family, any comparable production) qualifies Tier 2, the same shared-slot "
        f"precedent as keyword kinship -- ZERO overlap falls through to Tier 3 tags (Option B, "
        f"Captain). Fires ONLY when text/keyword matching found nothing at all for the pair (mana "
        f"kinship is Tier-2-only, so it can never override an already-better tier -- see "
        f"mana_pip_kinship_match()). Rank among mana-kinship matches uses a dedicated cascade "
        f"(mana_cascade_penalty(), amount closeness first, then color-set exactness, then the "
        f"candidate's own production breadth, then a rider penalty) rather than the idf-based text "
        f"formula, since there is no natural corpus-DF analog for a mana shape; drawback/rider text "
        f"never blocks qualification, only rank, per R5. Kinship evidence carries BOTH sides' mana "
        f"facts (Phase 2c precedent). FINDING (not engineered around): the Arcane Signet / Manalith "
        f"7-token text fragment (\"add one mana of any color\") measures DF=308 corpus-wide today -- "
        f"legitimately DEAD under Phase 3's ratified bands (T2_RESCUE_CEILING=172), not the ~26 an "
        f"earlier triage pass recorded. This cluster (Manalith + 8 creatures) still reaches Tier 2, "
        f"just via mechanism=mana instead of mechanism=text -- the qualifying OUTCOME holds, satisfying "
        f"the intent of the standing gate, through a different, equally-valid evidentiary path."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain): Instant/Sorcery are no longer disjoint for the tier-assignment demotion.** "
        f"This closes the open question flagged since v2.3 (Preordain -> Deliberate's own report section "
        f"used to ask it explicitly). Both are one-shot, nonpermanent spell types -- unlike e.g. Artifact "
        f"vs Creature -- so a byte-identical (or fragment-shared) match between an Instant and a Sorcery "
        f"now stays at its earned tier instead of being bumped down one (min tier 2). Scoped narrowly: "
        f"see types_disjoint_for_demotion() -- compute_affinity()'s type_match rank bonus and the "
        f"report's own \"type bucket\" fact column are UNCHANGED (still plain type_bucket() equality), "
        f"since neither was part of this ruling. Tier 0 is unaffected either way -- frame_signature "
        f"requires an exact type_line match, which Instant vs Sorcery always fails. Examples: Vampiric "
        f"Tutor <-> Imperial Seal <-> Cruel Tutor (byte-identical text) now land at Tier 1, not Tier 2."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain): mana-pip kinship's shape requirement (source_class + repeatable) is no "
        f"longer a qualification gate.** \"Open the gate, allow other weights to surface the best "
        f"matches.\" Closes a real gap: Dark Ritual (one-shot spell_effect, {{B}}{{B}}{{B}}) and Bog "
        f"Witch (repeatable activated_tap, {{B}}{{B}}{{B}}) produce EXACTLY the same mana but share no "
        f"viable text fragment (the core is 2-3 tokens, below the {args.ngram_min_len}-token floor) -- "
        f"under the old shape-gated version neither mana kinship nor text matching could ever connect "
        f"them. Shape mismatch is now a cascade-rank term instead (MANA_SHAPE_MISMATCH_PENALTY="
        f"{MANA_SHAPE_MISMATCH_PENALTY}) rather than a qualification requirement -- both still qualify "
        f"Tier 2 either way. See mana_pip_kinship_match()/mana_cascade_penalty(); the amount-vs-shape "
        f"RANK priority between them has changed since this ruling first shipped -- see the next entry."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain), 2026-07-12 -- delivery-mechanism weight raised above a one-mana amount "
        f"gap.** Reverses part of R5's original \"amount first, then type\" cascade order (the ruling "
        f"directly above, which set MANA_SHAPE_MISMATCH_PENALTY deliberately LIGHTER than one unit of "
        f"MANA_AMOUNT_PENALTY_WEIGHT so amount always dominated). Captain: \"the way it gives the mana "
        f"is also important... Thran Dynamo should beat a card that gives {{C}}{{C}} if that card isn't "
        f"an activated ability, even though Thran is one mana further off.\" MANA_SHAPE_MISMATCH_PENALTY "
        f"raised from 0.2 to {MANA_SHAPE_MISMATCH_PENALTY} -- now strictly between one and two units of "
        f"MANA_AMOUNT_PENALTY_WEIGHT ({MANA_AMOUNT_PENALTY_WEIGHT}), so a same-shape match one mana off "
        f"(Thran Dynamo's activated-tap {{C}}{{C}}{{C}} vs Sol Ring's activated-tap {{C}}{{C}}) now beats "
        f"an exact-amount cross-shape match, but amount still dominates once the gap reaches two or "
        f"more. Corpus-measured against Sol Ring's own colorless-family cascade before shipping: only 4 "
        f"real cards (Ashnod's Altar, Krark-Clan Ironworks, Conduit of Storms, Everythingamajig -- all "
        f"non-activated-tap, exact-amount matches) move behind the far larger same-shape-one-off bucket "
        f"(491 cards) as a result -- a contained, targeted reweighting, not a wholesale reordering."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain), 2026-07-10 -- cumulative fragment scoring:** find_shared_fragment() "
        f"(now find_shared_fragments()) no longer credits only the single globally-longest shared run "
        f"per anchor/candidate paragraph pair -- it now finds ALL qualifying non-overlapping runs "
        f"within that SAME best-matching pair (never across different pairs). Rank combination: the "
        f"primary/longest run keeps its existing weight (1.0, unchanged formula); each additional run "
        f"gets a position-based diminishing weight -- 2nd run=0.5, 3rd+=0.25 (a FLOOR, not continued "
        f"decay, so a candidate with many qualifying runs doesn't have its tail contribution vanish) -- "
        f"see fragment_run_weight(). Runs below NGRAM_MIN_LEN ({args.ngram_min_len} tokens) are "
        f"explicitly OUT OF SCOPE, deferred to backlog (a separate, deeper NGRAM_MIN_LEN question, not "
        f"resolved by this change). Motivating case: Delney, Streetwise Lookout vs Roaming Throne share "
        f"a 5-token prefix run AND a 4-token suffix run -- the 4-token run stays uncredited (below the "
        f"floor), but the general pattern (two real shared runs around a differing middle clause) is "
        f"corpus-measured: 41 of 1,259 live text/reminder-mechanism Tier 2 pairs (3.3%) have a "
        f"qualifying second run, concentrated in three anchors (Delney 80%, Sakura-Tribe Elder 12%, "
        f"Zurgo, Thunder's Decree 7%, zero elsewhere in the calibration panel). Corpus-wide reorder "
        f"impact measured directly (old vs new formula, same code path, full Tier 2 list not just the "
        f"displayed cutoff): Delney 214/282 rows reordered (75.9%, max shift 74 positions), Zurgo "
        f"35/88 (39.8%, max shift 28), Sakura-Tribe Elder 42/204 (20.6%, max shift 21) -- substantial "
        f"internal movement, but no candidate crosses into/out of the displayed top-{report_cap} window "
        f"for any of the three, and no Tier changes anywhere. compute_fact_penalties() required no "
        f"changes (same-paragraph-pair scoping keeps context identical across all runs). See "
        f"POKE-PUNCH-LIST.md Entry #5 for the full audit, including a corrected re-measurement that "
        f"found the original impact estimate had the wrong DF ceiling and didn't respect the engine's "
        f"own no-double-count paragraph exclusion."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain), 2026-07-10 -- Entry #4, granted-keyword-SET kinship "
        f"(Equipment/Aura 'confers keywords' idiom), PARALLEL to text/keyword/mana matching:** a new "
        f"`granted_keyword_set` fact (regex-extracted from 'Equipped/Enchanted creature has/have/gains "
        f"...' clauses, validated against the corpus' own Scryfall `keywords` vocabulary, all-or-nothing "
        f"-- any non-keyword clause fragment voids the whole extraction) feeds a new Tier 2 mechanism, "
        f"same shared-slot shape as mana kinship (R6): ANY shared granted keyword qualifies, ranked by "
        f"stray (non-shared) keyword count (GRANT_KEYWORD_MISMATCH_PENALTY per stray keyword). Scoped to "
        f"size 1-2 keyword grants ({GRANT_SIZE_CEILING} ceiling) -- 3+-keyword grants are the "
        f"corpus-measured 'keyword-soup' territory, already covered by that existing Tagger tag, no new "
        f"mechanism needed there. Conditional grants (Champion's Helm's 'as long as ... legendary', "
        f"Multiclass Baldric's per-creature-type set) are excluded from the fact entirely, not extracted "
        f"and discounted -- verified directly against both named cards' real oracle text that this "
        f"resolves correctly by construction (one fails the regex's leading anchor, the other fails the "
        f"keyword-exact-match check), not by the CONDITIONAL_GRANT_MARKERS backstop. Fixes the entry's "
        f"own motivating case: Swiftfoot Boots ('hexproof and haste') <-> Lightning Greaves ('haste and "
        f"shroud') -- same sentence shape, real shared 'haste', but longest_common_run() only found the "
        f"3-token 'equipped creature has' prefix (keyword order flips, below the 5-token floor) and "
        f"Mechanism 1 never saw the clause (no comma, 'and'-joined). Corpus-wide: 372 cards carry a "
        f"qualifying size-1/2 granted-keyword fact, producing 9,059 pairwise Tier 2 kinship links -- a "
        f"real, shared-slot-scale impact (same category as mana kinship's own wide reach), invisible in "
        f"this 9-card calibration panel since none of these anchors are Equipment/Aura cards; verified "
        f"directly and live instead via Swiftfoot Boots (34 new keyword_grant Tier 2 rows, Lightning "
        f"Greaves confirmed among them, live through the actual /api/anchor endpoint)."
    )
    lines.append("")
    lines.append(
        f"**BUG FIX (found auditing Entry #4, not itself part of the ruling above):** "
        f"is_keyword_only_paragraph()'s keyword-prefix check was a raw substring match, not "
        f"word-boundary safe -- 'equipped'/'enchanted' silently prefix-matched an Equipment/Aura card's "
        f"own 'Equip'/'Enchant' keyword, wrongly excluding its ENTIRE grant-clause paragraph from "
        f"matchable_paragraphs before ANY mechanism (ordinary text matching, Mechanism 1, or this "
        f"entry's own new mechanism) could see it -- this is exactly why the bug surfaced auditing this "
        f"entry: Boots/Greaves' single-fragment 'X and Y' grants (no comma) were silently eaten, while "
        f"comma-bearing multi-keyword grants (Helm of Kaldra) accidentally survived. FIXED to match the "
        f"sibling function parse_keyword_instances()'s already-correct word-boundary convention "
        f"(`frag == kw or frag.startswith(kw + \" \")`). Purely corrective -- confirmed by construction "
        f"it can only ever ADD paragraphs back, never remove a legitimate exclusion. One corpus-wide gate "
        f"collision found and resolved: Discreet Retreat's 'spend this mana only to cast outlaw spells "
        f"or activate abilities of outlaw sources' (same bug, its own 'Enchant' keyword) was previously "
        f"invisible to Grand Abolisher's Tier 2 corroboration gate; now correctly surfaces (shares "
        f"Abolisher's own defining fragment) and correctly self-disqualifies via the existing v2.6 "
        f"amendment 1 mechanism -- added to MANA_ONLY_FAMILY, same as the Angel of Jubilation/Yasharn "
        f"precedent already documented at that gate. Tier 2 counts elsewhere shifted by single digits "
        f"(Myrel +1, Sol Ring +2, Delney +6) from other previously-hidden paragraphs becoming searchable "
        f"corpus-wide -- confirmed additive only, no gate regressions, full suite green."
    )
    lines.append("")
    lines.append(
        f"**BUG FIX + 2 UPDATED GATE EXPECTATIONS (found live-querying Swiftfoot Boots' viewer output, "
        f"2026-07-10):** `text_injected_on_side()`/`find_reminder_attribution()` compared a "
        f"find_shared_fragment(s)-reconstructed string (every token's trailing period stripped, CO-C "
        f"convention) against RAW injected-reminder paragraph text (periods intact) -- exact/substring "
        f"match can never succeed across an internal sentence boundary within a multi-sentence "
        f"paragraph, silently disabling `fragment_both_sides_injected()`'s hard discount "
        f"(PROVENANCE_DISCOUNT_WEIGHT) for any such match. FIXED via a shared normalization helper "
        f"(`normalize_paragraph_for_fragment_comparison()`). Two NAMED gates (SWIFTFOOT_EQUIP_TEXT, "
        f"FAITHLESS_FLASHBACK_TEXT) used the same period-bearing constants for exact-equality checks -- "
        f"same bug, third location -- fixed by redefining both constants in already-normalized form. "
        f"This unmasked two gates that had been giving a trivial always-PASS regardless of real state: "
        f"(1) check_gb_swiftfoot_boots_gate -- even with the discount now firing correctly, 1 "
        f"equip-reminder-boilerplate row still sits in Swiftfoot Boots' displayed top 10, a confirmed, "
        f"unavoidable floor from Phase 3's OWN frame-affinity restoration (any same-type match restores "
        f"effective_weight toward 1.0 independent of the provenance discount -- measured directly, see "
        f"PROVENANCE_DISCOUNT_WEIGHT's own comment); PROVENANCE_DISCOUNT_WEIGHT lowered 0.05 -> 0.01 "
        f"(real improvement for different-type both-sides-injected matches, negligible further benefit "
        f"for same-type ones), and the gate's expected count updated 0 -> 1 to reflect measured reality "
        f"rather than an unverified assumption. (2) check_gc_faithless_looting_gate -- the flashback "
        f"reminder's corpus DF has drifted from 173 (DEAD-banded when the gate was written) to 172 "
        f"today (ordinary corpus growth, unrelated to this session), exactly at the rescue-band ceiling "
        f"-- 171 rows now legitimately qualify under the already-ratified DF-banding rule; ruling: let "
        f"the rule do what it's designed to do, update the gate's expected count 0 -> 171 rather than "
        f"add a special-case exclusion, same precedent as Discreet Retreat's MANA_ONLY_FAMILY addition "
        f"above. Both gates independently re-verified against Zurgo/Delney (not in the default panel) "
        f"and full determinism -- all green."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain), 2026-07-10 -- Entry #7, mechanism sort priority + P/T modifier "
        f"(live-reviewing Zurgo's Tier 2 table):** (1) mechanism=\"keyword\" (Mechanism 1, an exact "
        f"NAMED keyword match) now ALWAYS sorts above mechanism=\"reminder\" (Mechanism 2, "
        f"reminder-injected text) within a tier -- a guaranteed categorical sort key `(mechanism-priority, "
        f"-rank, ...)`, not a scalar rank bonus, so the ordering can never be undone by future DF/corpus "
        f"drift. Scoped narrowly to keyword-vs-reminder, per ruling -- text/mana/keyword_grant rows are "
        f"unaffected, still competing purely on rank score exactly as before. Confirmed live: Zurgo's "
        f"Hanweir Garrison (reminder) was outranking Zurgo Stormrender (keyword); all 12 keyword rows now "
        f"sort before any reminder row. (2) Entry #4's granted-keyword-SET kinship now also compares "
        f"Equipment/Aura P/T stat modifiers (\"gets +N/+N\"), previously discarded entirely -- a missing "
        f"clause is a definitive +0/+0 (the oracle text says nothing about a bonus, a known fact, not "
        f"unparsed uncertainty), flat per-point penalty (GRANT_PT_MISMATCH_PENALTY_PER_POINT=0.15, "
        f"first-pass default). Behemoth Sledge (+2/+2) vs Bronzeplate Boar (+3/+2), shared \"trample\": "
        f"evidence now reads the P/T difference explicitly, penalty correctly includes both the "
        f"unshared-keyword and P/T-distance terms. Unmasked one more relative-displacement effect: the "
        f"P/T penalty made some keyword_grant matches less competitive, letting a second equip-reminder-"
        f"boilerplate row back into Swiftfoot Boots' fixed top-10 window -- check_gb_swiftfoot_boots_gate's "
        f"measured floor updated 1 -> 2, same discipline as Entry #6's other measured-not-guessed gate "
        f"corrections."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain), 2026-07-10 -- Entry #7 follow-up: P/T mismatch corrected from a scalar "
        f"penalty to a guaranteed, fully-graduated priority.** Feedback on the P/T work above: a penalty "
        f"blended into the same score as tag_score/affinity/CI isn't \"priority\" -- unrelated terms could "
        f"swamp it. Wanted: exact buff beats near buff beats far buff, as a HARD rule, same guarantee-not-"
        f"nudge principle as the keyword-vs-reminder fix. Implemented as `pt_exactness_priority()`, a "
        f"second categorical sort-key dimension. Documented directly, not glossed over: a single global "
        f"total-order sort cannot make \"exact P/T beats near\" absolute among keyword_grant rows while "
        f"ALSO leaving every other mechanism's ordering completely untouched -- if a text-mechanism row's "
        f"rank legitimately falls between two keyword_grant rows of different P/T distance, something has "
        f"to give. Pragmatic resolution: an EXACT-match (distance 0) keyword_grant row stays in the shared "
        f"pool, competing on rank normally; only a NON-exact match gets pushed into a graduated lower tier "
        f"(1 per point of distance) below that pool. Guarantees exact > near > far among keyword_grant "
        f"rows; documented cost is a near/far match also sorting below every OTHER mechanism's rows, not "
        f"just below closer keyword_grant matches specifically. Verified directly: monotonically "
        f"non-decreasing P/T distance confirmed across Behemoth Sledge's full 64-row keyword_grant list "
        f"(live via /api/anchor). check_gb_swiftfoot_boots_gate's measured floor updated a THIRD time this "
        f"session (2 -> 4) -- flagged explicitly in that constant's own comment as an expected consequence "
        f"of unrelated precision improvements, not a regression signal on its own."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain, per Fable 5's ratification recommendation), 2026-07-10 -- the qualification-"
        f"cascade shadowing fix (Option C):** `assign_tier()`'s cascade was 'first mechanism to find "
        f"anything wins' -- text/reminder matching ran before keyword_grant and unconditionally claimed "
        f"any pair it found ANYTHING for, permanently preventing keyword_grant from even being checked, "
        f"even when the text/reminder match was purely near-universal boilerplate (e.g. every {{1}}-cost "
        f"Equipment's identical Equip reminder) and a genuine, specific shared-keyword match existed "
        f"underneath it. Full investigation and options: "
        f"REMINDER-TEXT-QUALIFICATION-CASCADE-ISSUE.md (mtjawnny.github.io/docs). Fix, exactly as Fable 5 "
        f"recommended: a NEW check after the existing keyword_grant/mana cascade -- if the text/reminder "
        f"path's ENTIRE winning evidence (primary fragment AND every cumulative-scoring extra run, Entry "
        f"#5) is both-sides-M2-injected boilerplate (the same near-worthless PROVENANCE_DISCOUNT_WEIGHT="
        f"0.01 category Entry #6 already discounts hard), a genuinely qualifying keyword_grant match wins "
        f"outright -- categorically, not by scalar comparison (the engine has already ruled boilerplate is "
        f"near-worthless; a DF-vs-grant-penalty metric would be pointless). The displaced boilerplate match "
        f"is kept, not erased -- appended to the evidence string as '[also matched: ...]'. Scoped tight: if "
        f"even ONE run in the winning match is genuine non-boilerplate text, this does NOT fire. "
        f"Corpus-measured before ratifying, not guessed: of 9,059 pairs corpus-wide that qualify via "
        f"granted_keyword_kinship_match(), 587 are correctly claimed today by genuinely strong text "
        f"matches (e.g. Behemoth Sledge vs Unflinching Courage, DF~2, a near-verbatim match) that MUST "
        f"keep winning -- confirmed unchanged, byte-for-byte, after this fix. Only 71 were pure-boilerplate "
        f"shadowed; all 71 now correctly resolve to keyword_grant. A real implementation bug was caught "
        f"during this same verification pass (not shipped): the new check's guard initially fired for "
        f"Tier 0 matches too (which never set `fragment`, crashing on the boilerplate check) -- fixed by "
        f"requiring `base == 2` explicitly, not just 'not None'. check_gb_swiftfoot_boots_gate's measured "
        f"floor moved a FOURTH time this session, but downward for the first time -- `4 -> 3`, a genuine "
        f"reduction in boilerplate clutter (Ring of Valkas correctly relabeled), not relative displacement."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain, per Fable 5's independent review), 2026-07-10 -- "
        f"locate_fragment_context() boundary-crossing bug fix.** Full investigation: "
        f"EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md (mtjawnny.github.io/docs) -- Captain asked "
        f"Fable 5 to take a step back and review the whole engine's weighting, starting from the "
        f"Swiftfoot Boots reminder-text clustering problem; Fable 5 independently verified the doc's own "
        f"numbers and found this bug live, unprompted, while doing so. `locate_fragment_context()` "
        f"compared a period-stripped fragment (the CO-C tokenization convention) against RAW, "
        f"period-intact paragraph text -- the exact same bug class Entry #6 already fixed for "
        f"`fragment_both_sides_injected()`/`text_injected_on_side()`, just a missed call site. Any Tier 2 "
        f"fragment spanning an internal sentence boundary within a multi-sentence paragraph returned "
        f"`(None, None)` here, which `compute_fact_penalties()` reads as \"unknown\" -- silently disabling "
        f"ALL FIVE fact penalties (scope/duration/exception/polarity/condition) for that row, not just one. "
        f"Measured across the 6-anchor default panel plus Zurgo/Delney/Swiftfoot Boots/Craterhoof/Growth "
        f"Spiral/the Anguished Unmaking cluster: 86 of 904 Tier 2 text/reminder rows (9.5%) affected, zero "
        f"false positives either direction. Concrete verified case: Growth Spiral vs. Gretchen Titchwillow "
        f"(a creature) previously showed zero duration penalty despite being exactly the one_shot-vs-"
        f"ongoing mismatch `DURATION_PENALTY` exists to catch; now correctly pays it (`dur=1.0`), confirmed "
        f"live via `/api/anchor`. Fix: apply `normalize_paragraph_for_fragment_comparison()` to BOTH sides "
        f"of the comparison, not just the paragraph -- an earlier draft normalized only the paragraph and "
        f"broke 8 Sol-Ring-pool rows whose `fragment` is itself the RAW, period-intact whole-paragraph text "
        f"(Entry #5's already-documented Tier-1-demoted-to-Tier-2 case, e.g. Sol Ring vs. Arid Archway) -- "
        f"caught by this fix's own corpus measurement before it shipped, not by luck. Full gate suite "
        f"73/73 green (default panel) plus 36/36 (Zurgo/Delney), determinism confirmed twice, viewer cache "
        f"regenerated and reconfirmed live. First of three changes recommended by this review -- see the "
        f"deliberation doc for the other two (a sentence-boundary trim rule and a short-whole-sentence "
        f"Tier 2 path), not yet implemented as of this note."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain, per Fable 5's recommendation), 2026-07-10 -- sentence-boundary trim rule "
        f"(second of three changes from EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md).** "
        f"`find_shared_fragments()` found the longest common TOKEN run regardless of whether it crossed an "
        f"internal sentence boundary within a paragraph -- a run that happens to straddle the seam between "
        f"two UNRELATED sentences (e.g. Growth Spiral's \"Draw a card.\" + \"You may put a land...\" "
        f"colliding with Nahiri's Lithoforming's unrelated \"...draw a card.\" + \"You may play X additional "
        f"lands...\") reads as rare (low DF) purely because that specific seam-crossing token sequence is "
        f"uncommon, not because the underlying abilities are actually similar -- the opposite of what low DF "
        f"is supposed to signal. Fix (`trim_run_for_sentence_boundary()`): a run crossing a sentence "
        f"boundary on EITHER side only survives whole if its continuation past that boundary is itself "
        f">= NGRAM_MIN_LEN(5) tokens (real corroborating evidence, not a bare 1-2 token coincidence); "
        f"otherwise it's truncated to the leading segment, discarded entirely if that's also sub-floor. "
        f"Exempts reminder-injected paragraphs (v2.9 Mechanism 2) entirely -- caught during this fix's own "
        f"corpus measurement: Faithless Looting's flashback reminder (\"...for its flashback cost. Then "
        f"exile it.\") is ONE keyword's fixed, single-author, always-co-occurring two-sentence explanation, "
        f"not two independently-written native clauses that happen to collide; trimming it dropped the "
        f"gate's measured population from 171 to 0 (the shortened prefix's DF rose from 172, rescue band, to "
        f"178, DEAD -- converting a correctly-buried match into an incorrectly-excluded one, backwards from "
        f"the rule's intent). Corpus-measured before ratifying: across a 17-anchor sample (default panel + "
        f"Zurgo/Delney + this review's own case-study anchors), 803 anchor/candidate pairs had a qualifying "
        f"run either before or after this fix -- 778 completely unaffected (no boundary in the run at all, "
        f"the overwhelming majority), 25 lost their qualification entirely, 0 were trimmed-but-still-"
        f"qualifying in this sample. All 25 losses verified as the exact false-positive class this fix "
        f"targets: Growth Spiral's \"draw a card you may\"-class collisions (7 pairs) and the Anguished "
        f"Unmaking/Inevitable Defeat \"exile target nonland permanent [you/its]\"-class collisions (18 "
        f"pairs, where the shared clause is itself only 4 tokens -- one short of NGRAM_MIN_LEN -- and only "
        f"reached 5 tokens by accidentally borrowing the next sentence's first word). These 25 pairs now "
        f"fall through to Tier 3 (or no match) unless the third change from this review (a short-whole-"
        f"sentence Tier 2 path, not yet implemented as of this note) readmits the ones with real shared "
        f"content on honest evidence instead. Full gate suite 73/73 green (default panel) plus 36/36 "
        f"(Zurgo/Delney), determinism confirmed twice, viewer cache regenerated and reconfirmed live."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain, per Fable 5's recommendation), 2026-07-10 -- short whole-sentence identity "
        f"Tier 2 path (third and final change from EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md).** "
        f"find_shared_fragments() can never qualify a matched clause shorter than NGRAM_MIN_LEN(5) tokens, "
        f"by construction -- \"Exile target nonland permanent\" is a complete, defining 4-word ability, one "
        f"word short of the floor, structurally invisible to that path no matter how rare it is corpus-wide. "
        f"Confirmed directly: Utter End and Vanish into Eternity reached Tier 1 on this exact clause only by "
        f"the LUCK of it sitting alone in its own paragraph on both cards; Anguished Unmaking and Inevitable "
        f"Defeat have the identical clause but a life-total rider glued onto the SAME paragraph (no line "
        f"break), denying them the whole-paragraph shortcut -- leaving them stuck at Tier 3, unable to reach "
        f"each other on their own defining ability, purely as a Scryfall oracle-text FORMATTING accident, "
        f"not a real functional difference. New mechanism (`find_shared_sentence()`): an exact, byte-"
        f"identical SENTENCE (not a whole paragraph, not an arbitrary token run) shared by both cards, "
        f"scoped to sentences under NGRAM_MIN_LEN only (longer ones are already reachable via the n-gram "
        f"path). Reuses `clause_index`/`clause_df` -- already built corpus-wide by `build_indexes()` from "
        f"every face's `clauses` field, previously only a fast candidate-pool pre-filter (per "
        f"`split_clauses()`'s own docstring) -- rather than a new index; this is an EXACT corpus-wide "
        f"sentence count, the same `para_exact_df` convention Tier 1 already uses for short paragraphs (R2, "
        f"Phase 3), not a windowed approximation. Same full/discounted/rescue/dead banding as the text/"
        f"reminder path, same T2_RESCUE_CEILING. Measured: \"exile target nonland permanent\" has sentence-"
        f"DF=17 (lands in the discounted band), confirmed live -- Anguished Unmaking and Inevitable Defeat "
        f"now correctly reach each other at Tier 2, `mechanism=\"sentence\"`, evidence `exile target nonland "
        f"permanent (DF=17)`. Placed LAST in the cascade (after keyword_grant and mana kinship both, same "
        f"\"only fires if nothing else found anything\" gating) -- a real implementation bug caught during "
        f"this fix's own corpus measurement, not shipped: an earlier draft placed it right where text/"
        f"reminder leaves `base` at None, which let it claim Sol Ring vs Ancient Tomb's pair (both share the "
        f"exact short sentence \"{{t}}: add {{c}}{{c}}\") BEFORE mana kinship's own specialized, richer "
        f"amount/color/shape cascade (R5/R6) ever got a chance, failing check_gg_sol_ring_cascade_gate "
        f"(expected mechanism=mana, got mechanism=sentence) -- fixed by moving the new path to the true end "
        f"of the cascade, since it has no domain-specific richness of its own the way mana/keyword_grant do "
        f"and shouldn't compete with them for position, only catch what neither of them (nor text/reminder) "
        f"found. Corpus-measured across the same 17-anchor sample as the trim rule: 66 new `mechanism="
        f"\"sentence\"` rows, entirely concentrated in the motivating cluster (Anguished Unmaking 22, "
        f"Inevitable Defeat 16, Utter End 14, Vanish into Eternity 14) plus a handful of genuine \"you lose "
        f"3 life\" (DF=7) matches on unrelated life-loss cards -- zero rows fired anywhere else in the "
        f"sample, including all 6 default-panel anchors, Zurgo, Delney, Swiftfoot Boots, Craterhoof, Growth "
        f"Spiral, and Faithless Looting. Full gate suite 73/73 green (default panel) plus 36/36 (Zurgo/"
        f"Delney), determinism confirmed twice, viewer cache regenerated and reconfirmed live via `/api/"
        f"anchor` (Anguished Unmaking's own Tier 2 list now shows all three siblings). This completes all "
        f"three changes recommended by Fable 5's review of the equipment-reminder-text and broader-"
        f"weighting question; the review's fourth item (an equip-cost-delta rank term for `keyword_grant`) "
        f"is implemented next, same session -- see the following note."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain, per Fable 5's recommendation), 2026-07-10 -- equip-cost delta term for "
        f"`keyword_grant` (fourth and final change from EQUIPMENT-REMINDER-AND-WEIGHTING-DELIBERATION.md, "
        f"the direct fix for Section 4/Q1's Equipment-clustering question).** "
        f"`granted_keyword_kinship_match()` had no signal at all for Equip-ACTIVATION-cost closeness -- "
        f"only the card's own CASTING cost (`mv_delta`, a completely different number) entered the shared "
        f"rank formula, so two Equipment granting the identical keyword set for a `{{1}}` Equip cost and a "
        f"`{{5}}` Equip cost scored equally close kin. Rejected the flagged fallback (disable reminder-text "
        f"Tier 2 qualification for Equipment specifically, add Equip cost as a new bucketing signal): "
        f"verified directly that Swiftfoot Boots' 3 residual displayed boilerplate rows (Ring of Xathrid, "
        f"Cobbled Wings, Ring of Evos Isle) share no real keyword grant with Boots at all -- Xathrid grants "
        f"neither hexproof nor haste, Cobbled Wings grants flying not haste/hexproof, Ring of Evos Isle "
        f"grants hexproof via a differently-shaped ACTIVATED (not static) ability -- honest, defensible weak "
        f"matches with nothing better available, \"rank buries, never excludes\" working as intended, not a "
        f"bug to chase. Also found a real error in this session's own briefing doc while implementing: "
        f"Cloak of the Bat and Fleetfeather Sandals (tied at score 6.267) were cited as proof of equip-cost "
        f"blindness, but both are actually `Equip {{2}}` granting the identical keyword set -- functionally "
        f"identical cards, correctly tied; caught by Fable 5's own independent verification before "
        f"implementation. Fix: `EQUIP_COST_RE`/`parse_equip_cost_value()` extract each Equipment's Equip "
        f"cost as a numeric value (a relative-distance heuristic, not rules-accurate mana value -- see "
        f"`mana_symbols_numeric_value()`'s own comment) from the RAW oracle text, carried on each "
        f"`granted_keyword_facts` entry alongside its existing P/T-modifier field; a missing/unparseable "
        f"cost (an Aura with no Equip line, or a non-mana cost like \"Equip—Sacrifice a creature\") is "
        f"genuinely UNKNOWN, not a definitive value, and contributes zero penalty -- same convention as "
        f"duration/scope/exception's own \"uncertainty is not evidence of difference\" rule, deliberately "
        f"NOT the P/T-modifier convention (there, a missing clause IS a known, definitive +0/+0). New flat "
        f"per-point term `GRANT_EQUIP_COST_PENALTY_PER_POINT=0.15`, same scale and same first-pass-default "
        f"reasoning as the existing P/T-mismatch term. Corpus-measured before ratifying: 372 qualifying "
        f"grant facts corpus-wide, 151 with a parsed numeric equip cost (the remaining 221 are Auras or "
        f"non-mana-cost Equipment, correctly None/unpenalized), values ranging 0-7 and clustering at 1-4 -- "
        f"comparable in scale to the existing P/T term, no re-tuning signal from the distribution. Verified "
        f"live: Lightning Greaves (`Equip {{0}}`) vs Swiftfoot Boots (`Equip {{1}}`) now shows `equip 1 vs "
        f"equip 0` in its evidence string with penalty correctly raised 0.60 -> 0.75; Swiftfoot Boots' "
        f"displayed Tier 2 top 10 unaffected (still 3 boilerplate rows, unchanged, per "
        f"check_gb_swiftfoot_boots_gate). Full gate suite 73/73 green (default panel) plus 36/36 (Zurgo/"
        f"Delney), determinism confirmed twice, viewer cache regenerated and reconfirmed live. This "
        f"completes all four changes recommended by Fable 5's review, same session."
    )
    lines.append("")
    lines.append(
        f"**RULED (Captain), 2026-07-10, new session -- second-class phrase bucket (superseding a "
        f"same-session first draft), plus a pool-seeding bug it uncovered.** After the equip-cost delta "
        f"term above, the Equip-cost reminder boilerplate still \"overwhelmingly survived\" in Swiftfoot "
        f"Boots' displayed Tier 2 top 10. First draft: exclude the Equip reminder from Mechanism 2 "
        f"injection entirely (obliterate it, never matchable again). Captain's follow-up ruling stepped "
        f"back from that: \"rather than completely exclude... don't remove, bucket-kneecap it hard enough "
        f"where it assuredly appears near the bottom\" -- explicitly in the spirit of ruling 6 "
        f"(\"qualification stays maximal, rank buries, never excludes\"), extended with a house-curated "
        f"phrase list rather than a DF-band or exclusion mechanism. Mechanism 2 injection is restored "
        f"unchanged (the Equip reminder is matchable again, exactly as before this note); "
        f"`SECOND_CLASS_PHRASE_PATTERNS` is a short, explicit, Captain-curated regex list (same style as "
        f"`SCOPE_PATTERNS`/`EXCEPTION_PATTERNS`/`CONDITION_MARKERS`) -- currently the Equip-cost reminder "
        f"and \"you lose N life\" (a minor rider clause, e.g. Anguished Unmaking's second sentence, real "
        f"evidence but shouldn't outrank a card's actual defining ability). A row whose ENTIRE winning "
        f"evidence (primary fragment AND every cumulative-scoring extra run) matches the list gets a hard "
        f"categorical demotion via `second_class_priority()`, sorted strictly below every non-listed row "
        f"in its tier regardless of score -- same guarantee-not-nudge shape as `keyword_over_reminder_"
        f"priority()`/`pt_exactness_priority()`, placed FIRST in the sort tuple so it dominates both. "
        f"`check_gb_swiftfoot_boots_gate` rewritten to verify the demotion structurally (absent from the "
        f"display window AND present, not excluded, strictly after every non-second-class row in the full "
        f"list) rather than tracking an exact display-window count. Verified live: Swiftfoot Boots' full "
        f"Tier 2 list is back to 99 rows (57 second-class, 42 genuine), displayed top 10 is 100% genuine "
        f"(Bilbo's Ring / Lightning Greaves / Cloak of the Bat / Fleetfeather Sandals / My Precious / Ring "
        f"of Valkas / Unicycle / Brilliant Wings / A-Cori-Steel Cutter / Dragon Breath); Anguished "
        f"Unmaking's real siblings (Utter End, Inevitable Defeat, Vanish into Eternity) rank at the top of "
        f"its list, its five \"you lose 3 life\" coincidences demoted to the very bottom. "
        f"\n\n"
        f"**A real bug caught verifying the first (obliteration) draft, still true and still fixed here:** "
        f"`gather_candidate_pool()` had NO seeding path of its own for `keyword_grant` -- the same class "
        f"of gap already found and fixed this session for mana kinship (`build_mana_pip_index()`, the "
        f"Priest of Gix/Dark Ritual case), just never noticed for keyword_grant because Equipment's own "
        f"Equip-reminder boilerplate text overlap was ACCIDENTALLY doing double duty as its pool-seeding "
        f"path the whole time (Entry #4 through this note). Confirmed directly while testing the "
        f"obliteration draft: excluding the Equip reminder collapsed Swiftfoot Boots' candidate pool from "
        f"dozens of cards to 2 -- Lightning Greaves, Entry #4's own motivating case, vanished from the "
        f"pool entirely even though `assign_tier()` still correctly resolves it to `keyword_grant` when "
        f"called directly on the pair; it was never being DISCOVERED via any seeding path of its own. This "
        f"bug is independent of which demotion strategy the boilerplate itself gets, so the fix stands "
        f"regardless of the pivot above: `build_granted_keyword_index()` (granted keyword name -> "
        f"`set(oracle_id)`, scoped to `GRANT_SIZE_CEILING`, no DF-floor gate -- same \"any shared keyword "
        f"qualifies, no evergreen-style prune case\" reasoning as mana kinship's own index), wired into "
        f"`gather_candidate_pool()` as a new seeding block. Confirmed purely additive elsewhere (Mask of "
        f"Avacyn, an Aura, unaffected at 17 Tier 2 rows). Full gate suite 73/73 green (default panel) plus "
        f"37/37 (Zurgo/Delney -- one row added to check_gb_swiftfoot_boots_gate's own PASS count, not a "
        f"new gate), determinism confirmed twice, viewer cache regenerated and reconfirmed live."
    )
    lines.append("")
    lines.append(
        f"Corpus: {len(card_docs):,} cards, {len(card_tags):,} tagged. "
        f"n-gram min length={args.ngram_min_len}, n-gram DF floor={args.ngram_df_floor}, "
        f"inherited-tag discount={args.inherited_discount}, Tier 3 coverage threshold="
        f"{args.tier3_threshold}, tag score weight={args.tag_score_weight}, "
        f"CI penalty={args.ci_penalty}, MV penalty={args.mv_penalty}, "
        f"scope penalty={args.scope_penalty}, duration penalty={args.duration_penalty}, "
        f"exception penalty={args.exception_penalty}, polarity penalty={args.polarity_penalty}, "
        f"condition penalty={args.condition_penalty}, type match bonus={args.type_match_bonus}, "
        f"subtype bonus={args.subtype_bonus} (cap {args.subtype_bonus_cap}), "
        f"superset step cap={SUPERSET_STEP_CAP}. "
        f"Candidate pool for this anchor: {pool_size:,} cards."
    )
    lines.append("")

    for t in (0, 1, 2, 3):
        header, extra_column, extra_key = TIER_TABLE_SPEC[t]
        lines.append(f"## {TIER_TITLES[t]} ({counts_before_cap[t]} found, showing up to {report_cap})")
        lines.append("")
        if not displayed_tiers[t]:
            lines.append("_none_")
        else:
            lines.append(render_table(displayed_tiers[t], header, extra_column, extra_key))
            if counts_before_cap[t] > report_cap:
                full_name = f"{filename_slug(anchor_name)}-tier{t}.md"
                full_table = render_table(full_tiers[t], header, extra_column, extra_key)
                full_md = f"# {anchor_name} — Tier {t} full list ({counts_before_cap[t]} total)\n\n{full_table}\n"
                full_list_files[t] = {"filename": full_name, "content": full_md}
                lines.append("")
                lines.append(f"_Full list ({counts_before_cap[t]} total): see `full/{full_name}`_")
        lines.append("")

    return "\n".join(lines), counts_before_cap, displayed_tiers, full_list_files


def append_footer(lines: list, anchor_name: str, tiers: dict, self_check_info: dict,
                   defense_grid_info: dict = None) -> None:
    if anchor_name == "Grand Abolisher" and defense_grid_info is not None:
        lines.append("## Defense Grid gate finding (v2.6 amendment 2, gate 4 -- informational per Captain's ruling)")
        lines.append("")
        if defense_grid_info["present"]:
            lines.append(
                f"- Defense Grid is in the displayed Tier 3 top 10 at position "
                f"{defense_grid_info['position']} (score={defense_grid_info['score']:.4f})."
            )
        elif defense_grid_info["position"] is None:
            lines.append("- Defense Grid does not qualify for Tier 3 at all (tag_score below threshold).")
        else:
            lines.append(
                f"- Defense Grid landed at full-list position {defense_grid_info['position']} "
                f"(score={defense_grid_info['score']:.4f}), not the displayed top 10. Ruling: the "
                f"turn-scoped mechanism is verified correct -- Defense Grid's score rose from 0.17 "
                f"(pre-amendment 2) to {defense_grid_info['score']:.4f} exactly as the tag's weight "
                f"(idf≈3.96) predicts. The remaining gap to the #10 cutoff (score="
                f"{defense_grid_info['cutoff_score']:.4f}, gap={defense_grid_info['score_gap']:.4f}) is "
                f"genuine tag-overlap distance, not a phrase-inventory or constant problem: Defense "
                f"Grid sits just behind a {defense_grid_info['tie_cluster_size']}-way tie plateau, "
                f"scored just below the cutoff, sharing an unrelated \"hate-enchantment\"/"
                f"\"hate-artifact\" tag cluster (Aura of Silence, Dockside Extortionist, Green Slime, "
                f"several Jaheira variants, Kataki, War's Wage, etc.) that Defense Grid structurally "
                f"doesn't belong to "
                f"-- it's a general spell tax, not artifact/enchantment hate. This is a Tier 3 "
                f"resolution limit for a large tie plateau, not an engine defect; the designed remedy "
                f"is the Tier 3 human promote lane, not a wider regex or a retuned constant."
            )
            lines.append("  Boundary rows around the cutoff:")
            for row in defense_grid_info["boundary_rows"]:
                lines.append(f"    - {row['name']}: score={row['_score']:.4f}, evidence={row['evidence']}")
        lines.append("")

    if anchor_name == "Grand Abolisher":
        sen = next((r for r in tiers[2] if r["name"] == "Sen Triplets"), None)
        vov = next((r for r in tiers[2] if r["name"] == "Voice of Victory"), None)
        lines.append("## v2.2 constants question, resolved in v2.3 (ruling 1)")
        lines.append("")
        vov_note = f"rank {vov['rank_display']}" if vov else "not in the displayed top 10"
        sen_note = f"rank {sen['rank_display']}" if sen else "no longer in the displayed top 10 (exiled, per ruling 1)"
        lines.append(
            f"- v2.2 left Sen Triplets edging out Voice of Victory as an open constants question. "
            f"v2.3 resolved it directly (ruling 1: 'too far on every axis') via the new scope/"
            f"duration/exception facts plus MV_PENALTY 0.25->0.5, rather than by further CI/MV "
            f"tuning. Current state: Sen Triplets {sen_note}; Voice of Victory {vov_note}. See the "
            f"Voice of Victory placement gate and Sen Triplets exile gate output for the enforced "
            f"outcome."
        )
        lines.append("")

    if anchor_name == "Sol Ring":
        lines.append("## Amendment 2 bug-flag verification (v2)")
        lines.append("")
        for candidate_name in ("Sol Talisman", "Ulvenwald Captive // Ulvenwald Abomination"):
            tier, evidence = self_check_info.get(candidate_name, (None, None))
            lines.append(
                f"- **{candidate_name}**: v1 wrongly called this Tier 0. "
                f"v2 gives Tier {tier} ({evidence})."
            )
        lines.append("")

    if anchor_name == "Preordain":
        deliberate_hit = None
        for t in (0, 1, 2, 3):
            for row in tiers[t]:
                if row["name"] == "Deliberate":
                    deliberate_hit = (t, row)
        lines.append("## Ruled by Captain")
        lines.append("")
        if deliberate_hit:
            t, row = deliberate_hit
            rank_note = f", rank={row['rank_display']}" if "rank_display" in row else ""
            lines.append(
                f"- Preordain -> Deliberate lands at **Tier {t}** ({row['evidence']}{rank_note}). "
                f"RULED (Captain): Instant and Sorcery no longer count as disjoint for the tier-"
                f"assignment demotion (types_disjoint_for_demotion()) -- both are one-shot, "
                f"nonpermanent spell types, unlike e.g. Artifact vs Creature. Was Tier 2 under the "
                f"old flat disjoint-type rule (the v2.3-era open question this section used to flag); "
                f"the carve-out is now implemented. Tier 0 is unaffected -- frame_signature still "
                f"requires an exact type_line match, which Instant vs Sorcery always fails."
            )
        lines.append("")

    lines.append("## Known limitations")
    lines.append("")
    for limitation in KNOWN_LIMITATIONS:
        lines.append(f"- {limitation}")
    lines.append("")


def compute_anchor_full_tiers(anchor_name: str, ctx: dict) -> tuple:
    """Phase 5: the exact anchor -> (full_tiers, disqualified) sequence
    main()'s own anchor loop runs, factored out so one-off gate checks
    (Boros Charm, Swiftfoot Boots, Faithless Looting -- none in the
    default panel) don't need to be added to --anchor to be gated. `ctx`
    bundles the corpus-wide objects every gate needs (see build_gate_ctx())."""
    args = ctx["args"]
    anchor_card = resolve_anchor(anchor_name, ctx["cards"], ctx["name_index"])
    anchor_doc = ctx["card_docs"][anchor_card["oracle_id"]]
    anchor_tags = ctx["card_tags"].get(anchor_card["oracle_id"], [])
    anchor_tags_t3 = ctx["card_tags_t3"].get(anchor_card["oracle_id"], [])

    pool = gather_candidate_pool(
        anchor_doc, anchor_tags, ctx["paragraph_index"], ctx["clause_index"], ctx["clause_df"],
        ctx["ngram_index"], ctx["ngram_df"], ctx["tag_index"], ctx["keyword_index"], ctx["keyword_df"],
        ctx["mana_index"], ctx["granted_keyword_index"], args,
        vanilla_creature_index=ctx["vanilla_creature_index"],
    )
    if anchor_card["oracle_id"] in ctx["turn_scoped_matches"]:
        pool = pool | (set(ctx["turn_scoped_matches"]) - {anchor_card["oracle_id"]})
    return compute_candidate_rows(
        anchor_doc, anchor_tags, anchor_tags_t3, ctx["card_docs"], ctx["card_tags"], ctx["card_tags_t3"], pool,
        ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], ctx["idf"], ctx["idf_t3"],
        ctx["n_total_cards"], args,
    )


# ---------------------------------------------------------------------------
# Phase 5 (RULING-MANIFEST-2026-07-09.md) -- new outcome-form gates G-A..G-K.
# Each prints its own evidence; ctx is built once in main() via
# build_gate_ctx() and passed to every check below.
# ---------------------------------------------------------------------------

BOROS_CHARM_HEADER_TEXT = "choose one —"
# BUG FIX (found investigating Equip-reminder rescue-band clutter,
# 2026-07-10): these two constants are compared via exact equality against
# `row["fragment"]`, which is always a find_shared_fragment(s)-reconstructed
# string with every token's trailing period already stripped (CO-C
# convention) -- a multi-sentence source paragraph (both of these are) can
# NEVER reconstruct with its internal/trailing periods intact, so the raw
# (period-bearing) constants could never actually equal any real row's
# fragment. Confirmed for SWIFTFOOT_EQUIP_TEXT: G-B's "equip-reminder-only
# matches buried below display cutoff" check was reporting a trivial,
# always-true PASS regardless of real state -- Ring of Evos Isle (a genuine
# both-sides-injected equip-reminder match) was actually sitting at
# displayed Tier 2 position 7, unnoticed, until the discount-weight bug
# above was fixed and this comparison was re-examined. Both constants now
# defined in their already-normalized (period-stripped) form so equality
# actually fires against a real reconstructed fragment.
SWIFTFOOT_EQUIP_TEXT = "{1}: attach to target creature you control equip only as a sorcery"
FAITHLESS_FLASHBACK_TEXT = "you may cast this card from your graveyard for its flashback cost then exile it"

LANE_1C_PAIRS = [
    ("Growth Spiral", "Eureka Moment"),
    ("Garruk's Uprising", "Elemental Bond"),
    ("Cultivate", "Skyshroud Claim"),
    ("Rhystic Study", "Reparations"),
    ("Rampant Growth", "Natural Connection"),
    ("Deadly Dispute", "Village Rites"),
]

ARCANE_SIGNET_CLUSTER = [
    "Manalith", "Opaline Unicorn", "Utopia Tree", "Alloy Myr", "Lifespring Druid",
    "Great Forest Druid", "Three Tree Rootweaver", "Ornithopter of Paradise", "Birds of Paradise",
]


def check_ga_boros_charm_gate(ctx: dict) -> bool:
    print("\nG-A Boros Charm gate (Phase 5): zero T1 rows evidenced solely by 'choose one —'")
    full_tiers, _ = compute_anchor_full_tiers("Boros Charm", ctx)
    t1 = full_tiers[1]
    bad = [r for r in t1 if r["fragment"] == BOROS_CHARM_HEADER_TEXT]
    print(f"  Tier 1 count: {len(t1)}")
    for r in t1:
        print(f"    {r['name']}: {r['evidence']}")
    ok = len(bad) == 0
    print(f"  [{'PASS' if ok else 'STOP'}] {len(bad)} T1 row(s) evidenced solely by 'choose one —' (want 0)")
    return ok


# Captain's ruling, 2026-07-10: after fixing (a) the fragment/reminder-
# paragraph text-comparison bug that made this gate's checks structurally
# unable to ever fire, and (b) lowering PROVENANCE_DISCOUNT_WEIGHT as far as
# it actually helps, exactly 1 both-sides-injected equip-reminder row still
# sits in Swiftfoot Boots' displayed Tier 2 top 10 -- CONFIRMED not further
# reducible via this constant alone, a hard floor from Phase 3's OWN frame-
# affinity restoration mechanism (any same-type match restores effective_
# weight toward 1.0 independent of the provenance discount; measured
# directly, see PROVENANCE_DISCOUNT_WEIGHT's own comment). Was previously
# "0" only because the comparison could never match anything, not because
# the condition was ever verified true. Updated to reflect measured reality,
# same precedent as this session's other corpus-drift/bug-unmasking
# corrections (Discreet Retreat, the flashback DF-drift gate below).
#
# 1 -> 2 (still same session, 2026-07-10): adding the granted-keyword-set
# mechanism's P/T-modifier mismatch penalty (GRANT_PT_MISMATCH_PENALTY_PER_
# POINT) made some keyword_grant matches with large stat-bonus differences
# rank lower than before -- a real, wanted refinement -- which let a second
# equip-reminder-boilerplate row (Cobbled Wings, alongside Ring of Evos
# Isle) back into the fixed top-10 window purely by relative displacement,
# not a new bug. Same measured-not-guessed update discipline as the change
# just above.
#
# 2 -> 4 (still same session, 2026-07-10, Entry #7 follow-up): the
# graduated P/T-exactness priority (pt_exactness_priority(), guaranteed
# "exact beats near beats far") pushes EVERY non-exact-P/T-match
# keyword_grant row below the shared pool that includes reminder rows too
# -- by design (see that function's own comment: this is the documented
# cost of a hard categorical guarantee, not a bug). Swiftfoot Boots has no
# exact +0/+0-vs-+0/+0 keyword_grant candidates crowding out reminder rows
# as effectively as before. Measured directly, not guessed: 4 rows.
# NOTE: this floor has now moved 3 times in one session purely from
# unrelated precision improvements elsewhere -- if it needs to move again,
# that's expected, not a regression signal on its own; the gate's actual
# job (zero T1 rows, Tier 2 not literally dominated by boilerplate) still
# holds. A future redesign (e.g. a percentage/ratio check instead of an
# exact count) might be more stable long-term -- flagged, not built here.
#
# 4 -> 3 (still same session, 2026-07-10, Fable 5's Option C ratified):
# unlike the three moves above, this one is a genuine IMPROVEMENT, not
# relative displacement -- Ring of Valkas (previously equip-reminder-only)
# now correctly resolves to mechanism=keyword_grant instead, since its
# winning match was PURE both-sides-injected boilerplate and a genuine
# shared "haste" grant existed underneath it. See
# REMINDER-TEXT-QUALIFICATION-CASCADE-ISSUE.md for the full cascade fix.
# Tightened to match, per this session's own "keep the floor at measured
# reality" discipline.
#
# 3 -> N/A, SUPERSEDED (new session, 2026-07-10). A same-session first
# draft retired this constant entirely after excluding the Equip
# reminder from matchability outright ("obliterate it"). Captain then
# stepped back from that: "rather than completely exclude... don't
# remove, bucket-kneecap it hard enough where it assuredly appears near
# the bottom." The Equip reminder is matchable again (Mechanism 2
# injection restored, unchanged from pre-obliteration behavior) but is
# now one of SECOND_CLASS_PHRASE_PATTERNS -- see that constant's own
# comment and second_class_priority() in compute_anchor_full_tiers() for
# the categorical demotion mechanism. This exact-count constant is
# retired for good (not un-retired) -- the gate below checks the
# DEMOTION GUARANTEE structurally (absent from display AND present, but
# sorted after every non-second-class row, in the full list) rather than
# tracking a display-window count that would otherwise need to move a
# sixth time.
def check_gb_swiftfoot_boots_gate(ctx: dict) -> bool:
    print("\nG-B Swiftfoot Boots gate (Phase 5, SECOND-CLASS BUCKET 2026-07-10): equip-reminder rows "
          "stay fully qualified -- ruling 6, never excluded -- but are guaranteed to sort below every "
          "non-second-class row in Tier 2, categorically. Checks both halves: absent from the display "
          "window, present (not excluded) and demoted in the full list")
    full_tiers, _ = compute_anchor_full_tiers("Swiftfoot Boots", ctx)
    t1 = full_tiers[1]
    bad_t1 = [r for r in t1 if r["fragment"] == SWIFTFOOT_EQUIP_TEXT]
    ok1 = len(bad_t1) == 0
    print(f"  Tier 1 count: {len(t1)}, equip-reminder-only rows: {len(bad_t1)}")
    print(f"  [{'PASS' if ok1 else 'STOP'}] zero T1 equip-reminder-only rows")

    report_cap = ctx["args"].report_cap
    full_t2 = full_tiers[2]
    displayed_t2 = full_t2[:report_cap]
    equip_in_display = [r for r in displayed_t2 if r["fragment"] == SWIFTFOOT_EQUIP_TEXT]
    ok2 = len(equip_in_display) == 0
    print(f"  displayed Tier 2 top {report_cap}: {len(equip_in_display)} equip-reminder-only "
          f"row(s) ({', '.join(r['name'] for r in equip_in_display) or 'none'})")
    print(f"  [{'PASS' if ok2 else 'STOP'}] equip-reminder-only matches absent from the display window")

    equip_positions = [i for i, r in enumerate(full_t2) if r["fragment"] == SWIFTFOOT_EQUIP_TEXT]
    non_second_class_count = len(full_t2) - len(equip_positions)
    ok3 = len(equip_positions) > 0 and all(p >= non_second_class_count for p in equip_positions)
    print(f"  full Tier 2 list ({len(full_t2)} rows): {len(equip_positions)} equip-reminder row(s) "
          f"present -- qualified, never excluded -- all sorted after all {non_second_class_count} "
          f"non-second-class rows: {ok3}")
    print(f"  [{'PASS' if ok3 else 'STOP'}] second-class demotion verified structurally (present + "
          f"strictly last), not inferred from a display-window count alone")
    return ok1 and ok2 and ok3


# Captain's ruling, 2026-07-10: this gate's premise ("DF 173, DEAD-banded,
# never qualifies") was true when written but has since drifted -- the
# flashback reminder's corpus-wide DF is measured at 172 TODAY (ordinary
# corpus growth, unrelated to any change this session), exactly AT
# T2_RESCUE_CEILING's inclusive boundary, so by the letter of the already-
# ratified DF-banding rule it now legitimately rescue-band-qualifies. This
# was never actually caught by this gate -- a text-comparison bug (fixed
# alongside this) made the check structurally unable to ever fire, so "want
# 0" was never really verified, just assumed. Ruling: let the ratified rule
# do what it's designed to do (qualification surfaces, rank buries) rather
# than special-case an exclusion -- same "corpus reality moved, the gate's
# stale expectation gets updated, not the scoring" precedent as Discreet
# Retreat (MANA_ONLY_FAMILY) and G-B above. 171 rows measured directly.
FAITHLESS_FLASHBACK_EXPECTED_QUALIFYING_ROWS = 171


def check_gc_faithless_looting_gate(ctx: dict) -> bool:
    print(f"\nG-C Faithless Looting gate (Phase 5, ratified count updated 2026-07-10): "
          f"flashback-reminder-only evidence, DF=172 today (was 173 when DEAD-banded, corpus drift) "
          f"-- now legitimately rescue-band qualifies, buried not excluded")
    full_tiers, _ = compute_anchor_full_tiers("Faithless Looting", ctx)
    bad = [r for tier in (0, 1, 2) for r in full_tiers[tier] if r["fragment"] == FAITHLESS_FLASHBACK_TEXT]
    ok = len(bad) == FAITHLESS_FLASHBACK_EXPECTED_QUALIFYING_ROWS
    print(f"  [{'PASS' if ok else 'STOP'}] {len(bad)} T0/1/2 row(s) evidenced solely by the flashback "
          f"reminder (expected {FAITHLESS_FLASHBACK_EXPECTED_QUALIFYING_ROWS}, measured 2026-07-10)")
    return ok


def check_gd_lane1c_gate(ctx: dict) -> bool:
    """G-D, RELAXED (Captain ruling): the binding check is qualification in
    the rescue zone only. The original "ranked bottom half" clause is
    STRUCK -- it was drafting-layer extrapolation (an assistant prediction
    of where discounted rows would land), never a Captain ruling. The
    ratified rulings -- qualification in the rescue zone, and the text-
    evidence discount actually firing -- are both implemented and verified
    below (discount confirmed active via a zero-weight probe). Remaining
    rank position is carried by tag_score/affinity, legitimate independent
    evidence outside this gate's scope. Prints rank/median/tag_term/
    affinity as evidence rows, not a pass/fail position check."""
    print("\nG-D Lane 1c six gate (Phase 5, RELAXED): qualify T2 in the rescue zone "
          "(position requirement struck -- see docstring)")
    all_ok = True
    for anchor_name, cand_name in LANE_1C_PAIRS:
        full_tiers, _ = compute_anchor_full_tiers(anchor_name, ctx)
        t2 = full_tiers[2]
        ranks = [r["_rank"] for r in t2]
        median = ranks[len(ranks) // 2] if ranks else None
        pos = next((i for i, r in enumerate(t2) if r["name"] == cand_name), None)
        row = t2[pos] if pos is not None else None
        band = row["_commonality_band"] if row else None
        ok = row is not None and band == "rescue"
        tag_term = row["_tag_score"] * ctx["args"].tag_score_weight if row else None
        print(
            f"  {anchor_name} vs {cand_name}: position={pos + 1 if pos is not None else None}/{len(t2)} "
            f"rank={row['_rank']:.2f} median={median:.2f} tag_term={tag_term:.2f} "
            f"affinity={row['_affinity_term']:.2f} band={band} {'PASS' if ok else 'STOP'}"
            if row else f"  {anchor_name} vs {cand_name}: NOT FOUND STOP"
        )
        all_ok = all_ok and ok
    return all_ok


def check_ge_hero_of_bladehold_gate(ctx: dict) -> bool:
    print("\nG-E Hero of Bladehold gate (Phase 5): stays in Zurgo's T2 (one-side-native preserved)")
    full_tiers, _ = compute_anchor_full_tiers("Zurgo, Thunder's Decree", ctx)
    row = next((r for r in full_tiers[2] if r["name"] == "Hero of Bladehold"), None)
    ok = row is not None
    print(f"  [{'PASS' if ok else 'STOP'}] Hero of Bladehold {'in' if ok else 'MISSING FROM'} Zurgo's Tier 2"
          + (f" -- evidence={row['evidence']!r}" if row else ""))
    return ok


def check_gf_arcane_signet_gate(ctx: dict) -> bool:
    print("\nG-F Arcane Signet gate (Phase 5): Manalith + the 8 creatures qualify T2")
    print("  FINDING (Captain-ratified): the shared text fragment measures DF=308 today (not the ~26 an "
          "earlier triage pass recorded -- that was an artifact of the pre-CO-C punctuation truncation) "
          "-- legitimately DEAD under T2_RESCUE_CEILING. Evidence path is mana kinship instead; outcome unchanged.")
    args = ctx["args"]
    anchor_doc = ctx["card_docs"][resolve_anchor("Arcane Signet", ctx["cards"], ctx["name_index"])["oracle_id"]]
    all_ok = True
    for name in ARCANE_SIGNET_CLUSTER:
        cand_doc = ctx["card_docs"][resolve_anchor(name, ctx["cards"], ctx["name_index"])["oracle_id"]]
        result = assign_tier(anchor_doc, cand_doc, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
        ok = result is not None and result["tier"] == 2
        print(f"  {name}: tier={result['tier'] if result else None} mechanism={result['mechanism'] if result else None} "
              f"{'PASS' if ok else 'STOP'}")
        all_ok = all_ok and ok
    return all_ok


def check_gg_sol_ring_cascade_gate(ctx: dict) -> bool:
    print("\nG-G Sol Ring gate (Phase 5): Sol Ring<->Ancient Tomb T2 via {C}{C} pip kinship; "
          "drawback text does not block")
    args = ctx["args"]
    sol_ring = ctx["card_docs"][resolve_anchor("Sol Ring", ctx["cards"], ctx["name_index"])["oracle_id"]]
    ancient_tomb = ctx["card_docs"][resolve_anchor("Ancient Tomb", ctx["cards"], ctx["name_index"])["oracle_id"]]
    result = assign_tier(sol_ring, ancient_tomb, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
    ok = result is not None and result["tier"] == 2 and result["mechanism"] == "mana"
    print(f"  Sol Ring vs Ancient Tomb: tier={result['tier'] if result else None} "
          f"mechanism={result['mechanism'] if result else None} evidence={result['evidence'] if result else None!r} "
          f"{'PASS' if ok else 'STOP'}")
    print("  (Ancient Tomb's 'this land deals 2 damage to you' drawback did not block qualification, per R5.)")

    print("  Colorless-family cascade landing spots (Mind Stone / Mana Vault / Thran Dynamo):")
    for name in ["Mind Stone", "Mana Vault", "Thran Dynamo"]:
        cand = ctx["card_docs"][resolve_anchor(name, ctx["cards"], ctx["name_index"])["oracle_id"]]
        r = assign_tier(sol_ring, cand, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
        print(f"    {name}: tier={r['tier'] if r else None} mechanism={r['mechanism'] if r else None} "
              f"penalty={r['mana_cascade_penalty'] if r else None}")
    return ok


def check_gh_zero_overlap_gate(ctx: dict) -> bool:
    print("\nG-H Zero-overlap gate (Phase 5): Gold Myr does NOT reach Elvish Mystic's T2 via mana kinship")
    args = ctx["args"]
    gold_myr = ctx["card_docs"][resolve_anchor("Gold Myr", ctx["cards"], ctx["name_index"])["oracle_id"]]
    elvish_mystic = ctx["card_docs"][resolve_anchor("Elvish Mystic", ctx["cards"], ctx["name_index"])["oracle_id"]]
    r_ab = assign_tier(gold_myr, elvish_mystic, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
    r_ba = assign_tier(elvish_mystic, gold_myr, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
    ok = r_ab is None and r_ba is None
    print(f"  Gold Myr -> Elvish Mystic: {r_ab} (T3-via-tags acceptable)")
    print(f"  Elvish Mystic -> Gold Myr: {r_ba} (T3-via-tags acceptable)")
    print(f"  [{'PASS' if ok else 'STOP'}] zero pip overlap (W vs G) -- NOT T2 via mana kinship, either direction")
    return ok


def check_gi_guild_pair_gate(ctx: dict) -> bool:
    print("\nG-I Guild-pair regression gate (Phase 5): literal-text path untouched by mana kinship")
    args = ctx["args"]
    pair_names = []
    for oid, doc in ctx["card_docs"].items():
        for mf in doc.get("mana_facts", []):
            if mf["colors"] == frozenset({"b", "g"}) and not mf["any_color"] and mf["widening"] == "multi":
                pair_names.append(doc["name"])
                break
        if len(pair_names) >= 2:
            break
    if len(pair_names) < 2:
        print("  [INFO] fewer than 2 same-pair sources found in this corpus snapshot -- nothing to check")
        return True
    a_doc = ctx["card_docs"][resolve_anchor(pair_names[0], ctx["cards"], ctx["name_index"])["oracle_id"]]
    c_doc = ctx["card_docs"][resolve_anchor(pair_names[1], ctx["cards"], ctx["name_index"])["oracle_id"]]
    result = assign_tier(a_doc, c_doc, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
    ok = result is not None and result["mechanism"] == "text"
    print(f"  {pair_names[0]} vs {pair_names[1]}: tier={result['tier'] if result else None} "
          f"mechanism={result['mechanism'] if result else None} {'PASS' if ok else 'STOP'}")
    return ok


def check_gj_ignoble_hierarch_gate(ctx: dict) -> bool:
    """G-J, "no plateau" clarified (Captain ruling): Urborg Elf and Druid of
    the Anima are a genuine structural tie on every current cascade/rank
    term (each shares 2 of Ignoble Hierarch's 3 colors and carries exactly
    1 unrelated color -- symmetric under R5's cascade, plus identical CI
    relation, MV, and tag score). Not a bug -- two cards equidistant from
    the anchor by every measured axis. "No plateau" is satisfied as a
    DISPLAY/ORDERING guarantee, not a numeric-score requirement: full_tiers
    is already sorted by compute_candidate_rows() with a deterministic
    tiebreaker chain (-rank, -fragment_len, mv_abs, NAME) -- ties resolve
    to a stable alphabetical order, never an accident of pool-iteration
    order. This gate verifies that tiebreaker is actually active (not that
    the underlying scores differ)."""
    print("\nG-J Ignoble Hierarch gate (Phase 5): the 0.29 quartet ordered by the cascade "
          "(ties broken deterministically by name, not required to be numerically distinct)")
    full_tiers, _ = compute_anchor_full_tiers("Ignoble Hierarch", ctx)
    t2 = full_tiers[2]
    quartet = ["Delighted Halfling", "Urborg Elf", "Druid of the Anima"]
    positions = {}
    for name in quartet:
        pos = next((i for i, r in enumerate(t2) if r["name"] == name), None)
        positions[name] = pos
        rank = t2[pos]["_rank"] if pos is not None else None
        print(f"  {name}: position={pos + 1 if pos is not None else None}/{len(t2)} rank={rank}")
    found = [p for p in positions.values() if p is not None]
    distinct_positions = len(found) == len(quartet) == len(set(found))
    # confirm the name tiebreaker is actually resolving the Urborg/Druid tie, not luck
    urborg_pos, druid_pos = positions.get("Urborg Elf"), positions.get("Druid of the Anima")
    tiebreak_ok = True
    if urborg_pos is not None and druid_pos is not None:
        same_rank = t2[urborg_pos]["_rank"] == t2[druid_pos]["_rank"]
        if same_rank:
            tiebreak_ok = (urborg_pos < druid_pos) == ("Urborg Elf" < "Druid of the Anima")
            print(f"  [INFO] Urborg Elf/Druid of the Anima tie exactly on _rank ({t2[urborg_pos]['_rank']}) "
                  f"-- resolved by name tiebreaker: {'PASS' if tiebreak_ok else 'STOP'}")
    ok = distinct_positions and tiebreak_ok
    print(f"  [{'PASS' if ok else 'STOP'}] every quartet member has a distinct, deterministic position")
    print("  [INFO] Llanowar Elves is resolver-scoped (cards.sqlite, CO-G) -- verified live via serve_viewer.py "
          "in Phase 2b's smoke test, not re-checked here (tier_engine.py's own --anchor resolver is a "
          "separate, out-of-scope mechanism against the raw corpus, not cards.sqlite).")
    return ok


def check_gk_craterhoof_endraze_gate(ctx: dict) -> bool:
    """G-K, granted-keyword-set kinship's mass-pump generalization
    (Captain's ruling, 2026-07-12, folding the former standalone team_pump
    mechanism into Entry #4's own granted_keyword_kinship_match()): the
    motivating case -- Craterhoof Behemoth ("creatures you control gain
    trample and get +X/+X until end of turn, where X is the number of
    creatures you control") and End-Raze Forerunners ("other creatures you
    control get +2/+2 and gain vigilance and trample until end of turn")
    share no >=5-token verbatim run and no whole sentence, so before this
    generalization End-Raze sat at Tier 3 (tag-overlap only). Verifies
    BOTH directions qualify Tier 2 via mechanism=keyword_grant (NOT a
    separate "team_pump" mechanism string -- the whole point of the
    2026-07-12 unification) on the shared "trample" grant, and that the
    wider cluster (60 cards corpus-wide sharing >=1 granted keyword with
    Craterhoof, see extract_granted_keyword_clause()'s own comment) still
    contains genuinely on-topic siblings already flagged by Tier 3's own
    tag system before any of this shipped (Overrun, Kamahl Heart of
    Krosa) -- not just the named pair."""
    print("\nG-K Craterhoof/End-Raze granted-keyword kinship gate (2026-07-12): End-Raze Forerunners "
          "reaches Craterhoof Behemoth's Tier 2 via a shared \"trample\" grant, both directions, "
          "as a plain keyword_grant match (no separate team_pump mechanism)")
    ok = True
    full_tiers, _ = compute_anchor_full_tiers("Craterhoof Behemoth", ctx)
    t2 = full_tiers[2]
    row = next((r for r in t2 if r["name"] == "End-Raze Forerunners"), None)
    if row is None:
        print("  [STOP] End-Raze Forerunners not present in Craterhoof Behemoth's Tier 2 at all")
        ok = False
    elif row["_mechanism"] != "keyword_grant":
        print(f"  [STOP] End-Raze Forerunners qualifies Tier 2 but via mechanism={row['_mechanism']!r}, "
              f"expected keyword_grant")
        ok = False
    else:
        print(f"  [PASS] End-Raze Forerunners: Tier 2 via keyword_grant, evidence={row['evidence']!r}")

    full_tiers_rev, _ = compute_anchor_full_tiers("End-Raze Forerunners", ctx)
    t2_rev = full_tiers_rev[2]
    row_rev = next((r for r in t2_rev if r["name"] == "Craterhoof Behemoth"), None)
    if row_rev is None or row_rev["_mechanism"] != "keyword_grant":
        print(f"  [STOP] reverse direction (End-Raze -> Craterhoof) did not qualify Tier 2 via "
              f"keyword_grant: {row_rev['_mechanism'] if row_rev else None}")
        ok = False
    else:
        print("  [PASS] reverse direction (End-Raze -> Craterhoof) also qualifies Tier 2 via keyword_grant")

    # Craterhoof's own granted-keyword facts include a real Equipment/Aura-
    # style match too (if any exists in its pool) alongside the mass-pump
    # ones -- filtering to rows whose evidence names "trample" keeps this
    # check scoped to the actual motivating cluster, not every keyword_
    # grant row regardless of shared keyword.
    other_names = {
        r["name"] for r in t2
        if r["_mechanism"] == "keyword_grant" and "trample" in (r.get("evidence") or "")
    }
    expected_present = {"Overrun", "Kamahl, Heart of Krosa"}
    missing = expected_present - other_names
    if missing:
        print(f"  [STOP] expected on-topic mass-pump siblings missing from Craterhoof's Tier 2: {sorted(missing)}")
        ok = False
    else:
        print(f"  [PASS] wider cluster present: {len(other_names)} cards reach Tier 2 via a shared "
              f"\"trample\" keyword_grant (includes {sorted(expected_present)})")
    return ok


def check_gl_promoted_phrase_gate(ctx: dict) -> bool:
    """G-L, first-class phrase bucket (Captain's ruling, 2026-07-11,
    REVISED same day to a scalar bonus -- see PROMOTED_PHRASE_PATTERNS'
    own comment): the "power 2 or less" motivating case. Reveillark
    ("return up to two target creature cards with power 2 or less from
    your graveyard to the battlefield") already reaches dozens of similar
    reanimation effects at Tier 2 through ordinary text matching -- this
    gate verifies PROMOTED_PHRASE_BONUS is actually flowing through
    compute_rank into every promoted row's `_rank`, not a categorical
    override: every `_promoted` row's `_promoted_term` must equal
    PROMOTED_PHRASE_BONUS exactly, every non-promoted row's must be 0.0,
    and at least one promoted/non-promoted PAIR must exist so the bonus
    has something to modestly move (not prove -- a fixed additive term
    can legitimately leave sort order unchanged for two rows already far
    apart on every other axis, "just a bit more weight" was the explicit
    instruction, not a guarantee)."""
    print("\nG-L Promoted-phrase gate (2026-07-11): \"power 2 or less\" adds PROMOTED_PHRASE_BONUS "
          "to matching Reveillark siblings' rank -- a modest scalar term, not a categorical override")
    full_tiers, _ = compute_anchor_full_tiers("Reveillark", ctx)
    t2 = full_tiers[2]
    ok = True
    if not t2:
        print("  [STOP] Reveillark's Tier 2 is empty")
        return False
    promoted = [r for r in t2 if r.get("_promoted")]
    non_promoted = [r for r in t2 if not r.get("_promoted")]
    if not promoted or not non_promoted:
        print(f"  [STOP] expected both promoted and non-promoted rows in Tier 2 (promoted={len(promoted)}, "
              f"non_promoted={len(non_promoted)})")
        return False
    bad_promoted = [r for r in promoted if r.get("_promoted_term") != PROMOTED_PHRASE_BONUS]
    bad_non_promoted = [r for r in non_promoted if r.get("_promoted_term") != 0.0]
    if bad_promoted or bad_non_promoted:
        print(f"  [STOP] promoted_term mismatch -- {len(bad_promoted)} promoted row(s) without the full "
              f"bonus, {len(bad_non_promoted)} non-promoted row(s) with a nonzero bonus")
        for r in (bad_promoted + bad_non_promoted)[:5]:
            print(f"    {r['name']}: promoted={r.get('_promoted')} promoted_term={r.get('_promoted_term')}")
        ok = False
    else:
        print(f"  [PASS] {len(promoted)} promoted row(s) carry exactly PROMOTED_PHRASE_BONUS="
              f"{PROMOTED_PHRASE_BONUS}, {len(non_promoted)} non-promoted row(s) carry 0.0")
    return ok


def check_gm_vanilla_creature_gate(ctx: dict) -> bool:
    """G-M, vanilla-creature Tier 0/1 (Captain's ruling, 2026-07-12; frame-
    MISMATCH kinship extension same day): a blank creature IS its frame, so
    two that share one (same mana cost, type line, power, toughness) are
    functional reprints of each other even though neither has any oracle
    text to compare -- treated through the SAME engine rules as any other
    card, not a bolted-on special case: a frame match is Tier 0, exactly
    like tier0_ok's own full-text-equality path.

    Same-day extension: a frame MISMATCH between two blank creatures no
    longer falls through to "no text-mechanism match at all" -- it's the
    SAME "identical text (here, identical NO text), different frame"
    shape as tier0_ok's own elif fallback a few lines up in assign_tier's
    cascade, so it resolves the same way: Tier 1, mechanism
    "vanilla_creature", buried by rank (mv_delta/color/type affinity, all
    already-generic terms) rather than excluded. This gate now checks
    BOTH halves: Tier 0 strictness (frame_signature governs it, unrelaxed)
    and the new Tier 1 fallback (nothing that's a blank creature falls out
    of the report entirely anymore).

    Checked via the FULL anchor pipeline (compute_anchor_full_tiers, which
    exercises gather_candidate_pool), not direct assign_tier() calls --
    assign_tier() alone was never broken; build_vanilla_creature_index()
    was ADDED because gather_candidate_pool() had no seeding path for this
    case at all (the same recurring gap as mana kinship/keyword_grant
    before it, widened again same day to pool ALL blank creatures, not
    just the anchor's own frame bucket -- see that index's own
    docstring). Confirmed corpus bug this closes: Grizzly Bears' full
    Tier 0 list held exactly 1 match (Balduvian Bears, found only by
    accident via a shared Tagger tag) before the index existed, despite
    Runeclaw Bear/Forest Bear/Bear Cub sharing the IDENTICAL blank {1}{G}
    2/2 frame and assign_tier() already resolving every one of them to
    Tier 0 when called directly.

    Also verifies the strict side: Cylian Elf (blank, {1}{G} 2/2, but
    "Creature -- Elf" not "Creature -- Bear") must NOT reach Tier 0 --
    proves frame_signature's exact type_line match still governs Tier 0,
    this isn't a blanket "same cost and stats" relaxation. Cylian Elf AND
    Scaled Wurm (blank, {7}{G} 7/6, unrelated frame) must BOTH now appear
    in Tier 1 instead (the new fallback), mechanism "vanilla_creature"."""
    print("\nG-M Vanilla-creature Tier 0/1 gate (2026-07-12): blank creatures with matching frame are "
          "functional reprints (Tier 0), mismatched-frame ones are still kin, buried by rank (Tier 1), "
          "both discoverable through the full anchor pipeline, not just direct assign_tier()")
    full_tiers, _ = compute_anchor_full_tiers("Grizzly Bears", ctx)
    t0_names = {r["name"] for r in full_tiers[0]}
    t1_by_name = {r["name"]: r for r in full_tiers[1]}
    ok = True

    expected = {"Runeclaw Bear", "Forest Bear", "Bear Cub", "Balduvian Bears"}
    missing = expected - t0_names
    if missing:
        print(f"  [STOP] expected blank {{1}}{{G}} 2/2 siblings missing from Grizzly Bears' Tier 0: {sorted(missing)}")
        ok = False
    else:
        print(f"  [PASS] all {len(expected)} expected blank-frame siblings present in Tier 0: {sorted(expected)}")

    unexpected = {"Cylian Elf", "Scaled Wurm"} & t0_names
    if unexpected:
        print(f"  [STOP] frame-mismatched blank creature(s) wrongly reached Tier 0: {sorted(unexpected)}")
        ok = False
    else:
        print("  [PASS] Cylian Elf (same cost/stats, different creature type) and Scaled Wurm "
              "(unrelated frame) correctly absent from Tier 0")

    still_missing = {"Cylian Elf", "Scaled Wurm"} - set(t1_by_name)
    if still_missing:
        print(f"  [STOP] frame-mismatched blank creature(s) missing from Tier 1 entirely: {sorted(still_missing)}")
        ok = False
    else:
        wrong_mechanism = {
            name: r["_mechanism"] for name, r in t1_by_name.items()
            if name in ("Cylian Elf", "Scaled Wurm") and r["_mechanism"] != "vanilla_creature"
        }
        if wrong_mechanism:
            print(f"  [STOP] frame-mismatched blank creature(s) reached Tier 1 via the wrong mechanism: {wrong_mechanism}")
            ok = False
        else:
            print("  [PASS] Cylian Elf and Scaled Wurm both present in Tier 1, mechanism=vanilla_creature "
                  "(frame mismatch, buried by rank rather than excluded)")

    args = ctx["args"]
    grizzly = ctx["card_docs"][resolve_anchor("Grizzly Bears", ctx["cards"], ctx["name_index"])["oracle_id"]]
    runeclaw = ctx["card_docs"][resolve_anchor("Runeclaw Bear", ctx["cards"], ctx["name_index"])["oracle_id"]]
    r_ba = assign_tier(runeclaw, grizzly, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
    symmetric_ok = bool(r_ba) and r_ba["tier"] == 0
    ok = ok and symmetric_ok
    print(f"  [{'PASS' if symmetric_ok else 'STOP'}] Runeclaw Bear -> Grizzly Bears also Tier 0 (symmetric)")

    scaled_wurm = ctx["card_docs"][resolve_anchor("Scaled Wurm", ctx["cards"], ctx["name_index"])["oracle_id"]]
    r_sw = assign_tier(scaled_wurm, grizzly, ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args)
    symmetric_mismatch_ok = bool(r_sw) and r_sw["tier"] == 1 and r_sw["mechanism"] == "vanilla_creature"
    ok = ok and symmetric_mismatch_ok
    print(f"  [{'PASS' if symmetric_mismatch_ok else 'STOP'}] Scaled Wurm -> Grizzly Bears also Tier 1/"
          f"vanilla_creature (symmetric)")
    return ok


# D1 (2026-07-16, TIER-ENGINE-V3-PROPOSAL.md / DISCOVERY-RECALL-AUDIT.md):
# fixed panel for the discovery superset gate below, plus a seed for its 3
# rotating anchors -- same "reproducible but not hand-picked every time"
# discipline as check_stability_gate's own anchor sampling.
DISCOVERY_SUPERSET_FIXED_PANEL = [
    "Swiftfoot Boots", "Dark Ritual", "Grizzly Bears", "Grand Abolisher", "Helm of Kaldra", "Sol Ring",
]
DISCOVERY_SUPERSET_GATE_SEED = 20260716
DISCOVERY_SUPERSET_FACE_ANCHORS = [
    ("Bonecrusher Giant // Stomp", 1),               # Stomp, face1
    ("Delver of Secrets // Insectile Aberration", 0),  # Delver of Secrets, face0
]


def _discovery_superset_exhaustive_qualifiers(anchor_doc, anchor_tags_t3, card_docs, card_tags_t3, idf_t3,
                                               ngram_df, clause_df, keyword_df, paragraph_index, args,
                                               check_tier3=True):
    """Shared exhaustive-qualification core for check_gn_discovery_superset_
    gate below (whole-card AND face-scoped call sites): every OTHER card in
    `card_docs` is checked directly against assign_tier() (Tier 0-2) and,
    when check_tier3, tier3_score() (Tier 3, tag-overlap only -- face mode
    passes check_tier3=False since a face-scoped anchor carries no tags of
    its own, so tier3_score would always return 0, exactly the same
    Tier-0-2-only scope export_face_anchor() already gives face mode). No
    pool involved -- this IS the "exhaustive" side of the superset check,
    gather_candidate_pool()'s own pool is compared against this set by the
    caller."""
    anchor_id = anchor_doc["oracle_id"]
    qualifying = set()
    for oid, candidate_doc in card_docs.items():
        if oid == anchor_id:
            continue
        result = assign_tier(anchor_doc, candidate_doc, ngram_df, clause_df, keyword_df, paragraph_index, args)
        if result is not None:
            qualifying.add(oid)
            continue
        if check_tier3:
            candidate_tags_t3 = card_tags_t3.get(oid, [])
            tag_score_t3, _matched = tier3_score(anchor_tags_t3, candidate_tags_t3, idf_t3, args.inherited_discount)
            if tag_score_t3 >= args.tier3_threshold:
                qualifying.add(oid)
    return qualifying


def check_gn_discovery_superset_gate(ctx: dict) -> bool:
    """G-N, discovery superset invariant (D1, 2026-07-16): productizes
    DISCOVERY-RECALL-AUDIT.md's one-off harness into a permanent gate.
    Standing rule: for every qualification path, gather_candidate_pool()'s
    pool must be a provable SUPERSET of every card assign_tier()/
    tier3_score() would independently qualify against the anchor when
    checked exhaustively (no pool). This is the class-level fix for a gap
    that has now recurred four times (mana, keyword_grant, vanilla_
    creature, and D2's n-gram seeding floor) -- any future mechanism whose
    seeding index has a gap fails HERE, at merge time, instead of being
    found by a one-off audit months later.

    Fixed 6-card panel + 3 seeded-random rotating anchors (whole-card,
    Tiers 0-3), plus 2 fixed face anchors (Stomp/Bonecrusher Giant face1,
    Delver of Secrets face0 -- Tiers 0-2 only, matching export_face_anchor
    ()'s own scope: a face-scoped anchor carries no tags, so Tier 3 can
    never qualify in face mode by construction). Uses `ctx["card_docs"]`
    (and, for face mode, `ctx["cards"]`/`ctx["keyword_df"]`) exactly as
    built by this run's own main() -- the granted_keyword_facts post-
    processing pass is therefore threaded through for free, closing the
    exact trap DISCOVERY-RECALL-AUDIT.md's own harness self-caught (its
    first exhaustive run omitted that pass and silently under-reported the
    keyword_grant dimension until caught and corrected).

    Face-scoped context reuses emit_viewer.build_face_scoped_context() via
    a function-local import (Captain's ruling, 2026-07-16) rather than
    duplicating FACE_SPLIT_LAYOUTS/face-splitting logic here a second time
    -- tier_engine.py's gated report path stays unaware of viewer-export
    specifics at MODULE scope (emit_viewer.py's own stated design), this
    is the one gate-local exception, scoped to a single function body."""
    print("\nG-N Discovery superset gate (D1): gather_candidate_pool() must be a superset "
          "of exhaustive assign_tier()/tier3_score() qualification, for every anchor")
    ok = True
    args = ctx["args"]
    cards = ctx["cards"]
    card_docs = ctx["card_docs"]
    name_index = ctx["name_index"]

    all_names = sorted({c["name"] for c in cards.values()} - set(DISCOVERY_SUPERSET_FIXED_PANEL))
    rng = random.Random(DISCOVERY_SUPERSET_GATE_SEED)
    rotating = rng.sample(all_names, 3)
    panel = DISCOVERY_SUPERSET_FIXED_PANEL + rotating
    print(f"  panel: {DISCOVERY_SUPERSET_FIXED_PANEL} + rotating {rotating} (seed={DISCOVERY_SUPERSET_GATE_SEED})")

    for anchor_name in panel:
        anchor_card = resolve_anchor(anchor_name, cards, name_index)
        anchor_id = anchor_card["oracle_id"]
        anchor_doc = card_docs[anchor_id]
        anchor_tags = ctx["card_tags"].get(anchor_id, [])
        anchor_tags_t3 = ctx["card_tags_t3"].get(anchor_id, [])

        pool = gather_candidate_pool(
            anchor_doc, anchor_tags, ctx["paragraph_index"], ctx["clause_index"], ctx["clause_df"],
            ctx["ngram_index"], ctx["ngram_df"], ctx["tag_index"], ctx["keyword_index"], ctx["keyword_df"],
            ctx["mana_index"], ctx["granted_keyword_index"], args,
            vanilla_creature_index=ctx["vanilla_creature_index"],
        )
        if anchor_id in ctx["turn_scoped_matches"]:
            pool = pool | (set(ctx["turn_scoped_matches"]) - {anchor_id})

        qualifying = _discovery_superset_exhaustive_qualifiers(
            anchor_doc, anchor_tags_t3, card_docs, ctx["card_tags_t3"], ctx["idf_t3"],
            ctx["ngram_df"], ctx["clause_df"], ctx["keyword_df"], ctx["paragraph_index"], args,
            check_tier3=True,
        )

        missing = qualifying - pool
        if missing:
            sample = sorted(card_docs[m]["name"] for m in missing)[:10]
            print(f"  [STOP] {anchor_name!r}: {len(missing)} qualifying candidate(s) missing from the pool "
                  f"(sample of {min(10, len(missing))}): {sample}")
            ok = False
        else:
            print(f"  [PASS] {anchor_name!r}: pool ({len(pool):,}) is a superset of exhaustive "
                  f"qualification ({len(qualifying):,})")

    import emit_viewer as ev
    from types import SimpleNamespace
    face_scope_ctx = SimpleNamespace(cards=cards, card_docs=card_docs, args=args, keyword_df=ctx["keyword_df"])
    face_ctx = ev.build_face_scoped_context(face_scope_ctx)

    for combined_name, face_index in DISCOVERY_SUPERSET_FACE_ANCHORS:
        anchor_card = resolve_anchor(combined_name, cards, name_index)
        face_key = f'{anchor_card["oracle_id"]}::{face_index}'
        anchor_doc = face_ctx.face_card_docs[face_key]

        pool = gather_candidate_pool(
            anchor_doc, [], face_ctx.face_paragraph_index, face_ctx.face_clause_index, face_ctx.face_clause_df,
            face_ctx.face_ngram_index, face_ctx.face_ngram_df, {}, face_ctx.face_keyword_index,
            face_ctx.face_keyword_df, face_ctx.face_mana_index, face_ctx.face_granted_keyword_index, args,
            vanilla_creature_index=face_ctx.face_vanilla_creature_index,
        )
        pool -= set(face_ctx.face_meta[face_key]["all_sibling_keys"])

        qualifying = _discovery_superset_exhaustive_qualifiers(
            anchor_doc, [], face_ctx.face_card_docs, {}, {},
            face_ctx.face_ngram_df, face_ctx.face_clause_df, face_ctx.face_keyword_df,
            face_ctx.face_paragraph_index, args, check_tier3=False,
        )
        qualifying -= set(face_ctx.face_meta[face_key]["all_sibling_keys"])

        missing = qualifying - pool
        face_label = f"{combined_name} (face{face_index}, {anchor_doc['name']!r})"
        if missing:
            sample = sorted(face_ctx.face_card_docs[m]["name"] for m in missing)[:10]
            print(f"  [STOP] {face_label}: {len(missing)} qualifying candidate(s) missing from the face-"
                  f"scoped pool (sample of {min(10, len(missing))}): {sample}")
            ok = False
        else:
            print(f"  [PASS] {face_label}: face-scoped pool ({len(pool):,}) is a superset of exhaustive "
                  f"Tier 0-2 qualification ({len(qualifying):,})")

    return ok


def build_gate_ctx(cards, card_docs, name_index, card_tags, card_tags_t3, paragraph_index, clause_index,
                    clause_df, ngram_index, ngram_df, tag_index, keyword_index, keyword_df, mana_index,
                    granted_keyword_index, turn_scoped_matches, idf, idf_t3, n_total_cards, args,
                    vanilla_creature_index) -> dict:
    return dict(
        cards=cards, card_docs=card_docs, name_index=name_index, card_tags=card_tags,
        card_tags_t3=card_tags_t3, paragraph_index=paragraph_index, clause_index=clause_index,
        clause_df=clause_df, ngram_index=ngram_index, ngram_df=ngram_df, tag_index=tag_index,
        keyword_index=keyword_index, keyword_df=keyword_df, mana_index=mana_index,
        granted_keyword_index=granted_keyword_index,
        turn_scoped_matches=turn_scoped_matches,
        idf=idf, idf_t3=idf_t3, n_total_cards=n_total_cards, args=args,
        vanilla_creature_index=vanilla_creature_index,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--anchor", action="append", dest="anchors",
                        help="anchor card name (repeatable); default is the fixed 6-card panel")
    parser.add_argument("--cards-path", default=str(CARDS_PATH))
    parser.add_argument("--card-tags-path", default=str(CARD_TAGS_PATH))
    parser.add_argument("--clause-df-floor", type=int, default=CLAUSE_DF_FLOOR)
    parser.add_argument("--ngram-min-len", type=int, default=NGRAM_MIN_LEN)
    parser.add_argument("--ngram-df-floor", type=int, default=NGRAM_DF_FLOOR)
    parser.add_argument("--inherited-discount", type=float, default=INHERITED_TAG_DISCOUNT)
    parser.add_argument("--tier3-threshold", type=float, default=TIER3_COVERAGE_THRESHOLD)
    parser.add_argument("--tag-score-weight", type=float, default=TAG_SCORE_WEIGHT)
    parser.add_argument("--ci-penalty", type=float, default=CI_PENALTY)
    parser.add_argument("--mv-penalty", type=float, default=MV_PENALTY)
    parser.add_argument("--scope-penalty", type=float, default=SCOPE_PENALTY)
    parser.add_argument("--duration-penalty", type=float, default=DURATION_PENALTY)
    parser.add_argument("--exception-penalty", type=float, default=EXCEPTION_PENALTY)
    parser.add_argument("--polarity-penalty", type=float, default=POLARITY_PENALTY)
    parser.add_argument("--condition-penalty", type=float, default=CONDITION_PENALTY)
    parser.add_argument("--type-match-bonus", type=float, default=TYPE_MATCH_BONUS)
    parser.add_argument("--subtype-bonus", type=float, default=SUBTYPE_BONUS)
    parser.add_argument("--subtype-bonus-cap", type=float, default=SUBTYPE_BONUS_CAP)
    parser.add_argument("--report-cap", type=int, default=REPORT_CAP)
    args = parser.parse_args()

    anchors = args.anchors or ANCHOR_PANEL

    cards = load_cards(Path(args.cards_path))
    print(f"loaded {len(cards):,} cards")

    card_tags = load_card_tags(Path(args.card_tags_path))
    print(f"loaded tags for {len(card_tags):,} cards")

    # Bootstrap keyword DF from raw records (2026-07-11) -- build_card_doc's
    # strip_bespoke_ability_label() step needs this BEFORE any card_doc
    # exists; see compute_keyword_df_from_cards()'s own docstring for why
    # this can't just be compute_keyword_df(card_docs) reordered.
    raw_keyword_df = compute_keyword_df_from_cards(cards)

    print("normalizing corpus (self-name substitution, reminder strip, paragraph/clause split)...")
    card_docs = {
        oracle_id: build_card_doc(card, keyword_df=raw_keyword_df)
        for oracle_id, card in cards.items()
    }
    n_total_cards = len(cards)

    # ---- Entry #4 (Captain's ruling, 2026-07-10): granted-keyword-SET facts --
    # post-processing pass (needs the corpus-wide keyword vocabulary, which can
    # only be known once every card's own `keywords` field has been seen).
    # 2026-07-12: this now ALSO covers the former team_pump mechanism's
    # mass-pump facts -- see extract_granted_keyword_clause()'s own comment. ----
    keyword_vocabulary = build_keyword_vocabulary(cards)
    for doc in card_docs.values():
        doc["granted_keyword_facts"] = build_granted_keyword_facts(doc, keyword_vocabulary)

    print("building paragraph/clause/n-gram/tag indexes...")
    paragraph_index, clause_index, clause_df, ngram_index, ngram_df = build_indexes(card_docs, args.ngram_min_len)
    tag_index = build_tag_index(card_tags)
    idf, tag_card_count, n_tagged_cards = compute_tag_stats(card_tags)
    print(
        f"distinct clauses: {len(clause_df):,} | distinct {args.ngram_min_len}-grams: "
        f"{len(ngram_df):,} | distinct tags: {len(tag_index):,}"
    )

    above_floor = sum(1 for df in ngram_df.values() if df > args.ngram_df_floor)
    print(
        f"n-gram DF floor={args.ngram_df_floor}: {above_floor:,}/{len(ngram_df):,} "
        f"distinct {args.ngram_min_len}-grams excluded from Tier 2 qualification"
    )

    # ---- v2.9 Mechanism 1: keyword corpus DF -- BEFORE any tier assignment ----
    keyword_df = compute_keyword_df(card_docs)
    keyword_index = build_keyword_index(card_docs)
    print_keyword_stats(keyword_df, args.ngram_df_floor)

    # ---- Pool-widening fix (Captain's ruling, 2026-07-10): mana kinship's own
    # candidate-pool seeding -- see build_mana_pip_index()'s docstring ----
    mana_index = build_mana_pip_index(card_docs)
    # ---- Pool-widening fix (found + fixed 2026-07-10, same session): keyword_grant's
    # own candidate-pool seeding -- see build_granted_keyword_index()'s docstring ----
    granted_keyword_index = build_granted_keyword_index(card_docs)
    # ---- Pool-widening fix (Captain's ruling, 2026-07-12): vanilla-creature
    # Tier 0's own candidate-pool seeding -- see build_vanilla_creature_index()'s docstring ----
    vanilla_creature_index = build_vanilla_creature_index(card_docs)

    name_index = build_name_index(cards)

    # ---- v2.6 amendment 2: derive rule:turn-scoped BEFORE any Tier 3 scoring ----
    turn_scoped_matches, turn_scoped_idf = run_turn_scoped_derivation(card_docs, n_total_cards)
    card_tags_t3, idf_t3 = build_turn_scoped_tag_index(card_docs, card_tags, idf, turn_scoped_matches, turn_scoped_idf)

    # ---- Gate 1: v2 self-check (frozen tier-assignment calibration) ----
    self_check_passed, self_check_info = run_self_check(cards, card_docs, name_index, ngram_df, clause_df, keyword_df, paragraph_index, args)

    # ---- v2.5 session amendment gate 2 (part 2): Tier 0 exclusions stay blocking ----
    tier0_exclusion_passed = check_tier0_exclusion_gate(self_check_info)

    # ---- Gate 2: symmetry (Amendment 4.1) ----
    symmetry_passed = check_symmetry(cards, card_docs, name_index, ngram_df, clause_df, keyword_df, paragraph_index, args)

    # ---- Build all requested anchor reports IN MEMORY (nothing written yet) ----
    built = {}
    for anchor_name in anchors:
        anchor_card = resolve_anchor(anchor_name, cards, name_index)
        anchor_doc = card_docs[anchor_card["oracle_id"]]
        anchor_tags = card_tags.get(anchor_card["oracle_id"], [])
        anchor_tags_t3 = card_tags_t3.get(anchor_card["oracle_id"], [])

        pool = gather_candidate_pool(
            anchor_doc, anchor_tags, paragraph_index, clause_index, clause_df,
            ngram_index, ngram_df, tag_index, keyword_index, keyword_df, mana_index,
            granted_keyword_index, args,
            vanilla_creature_index=vanilla_creature_index,
        )
        # v2.6 amendment 2: a candidate can ONLY score >0 on rule:turn-scoped
        # if the ANCHOR itself carries the tag (anchor-directional coverage).
        # When it does, widen the pool to every turn-scoped-tagged card --
        # otherwise a card sharing ONLY this new tag (no verbatim overlap, no
        # base Tagger tag overlap) would never be discovered at all, since
        # gather_candidate_pool seeds exclusively from the base indexes.
        if anchor_card["oracle_id"] in turn_scoped_matches:
            pool = pool | (set(turn_scoped_matches) - {anchor_card["oracle_id"]})
        full_tiers, disqualified = compute_candidate_rows(
            anchor_doc, anchor_tags, anchor_tags_t3, card_docs, card_tags, card_tags_t3, pool,
            ngram_df, clause_df, keyword_df, paragraph_index, idf, idf_t3, n_total_cards, args,
        )
        report_body, counts, displayed_tiers, full_list_files = render_anchor_report(
            anchor_name, card_docs, card_tags, len(pool), full_tiers, args.report_cap, args,
        )
        built[anchor_name] = {
            "report_body": report_body, "counts": counts,
            "displayed_tiers": displayed_tiers, "full_tiers": full_tiers,
            "full_list_files": full_list_files, "disqualified": disqualified,
        }

        print(f"\nTier 2 corroboration gate disqualifications (v2.6 amendment 1) — {anchor_name}:")
        if not disqualified:
            print("  none")
        else:
            for d in sorted(disqualified, key=lambda x: x["name"]):
                print(
                    f"  {d['name']}: anchor_polarity={d['anchor_polarity']}, "
                    f"candidate_polarity={d['candidate_polarity']}, tag_score={d['tag_score']:.2f}"
                )

    # ---- Gate 3: Marisi visibility (Amendment 4.2) ----
    marisi_gate_passed = True
    if "Grand Abolisher" in built:
        marisi_gate_passed = check_marisi_visibility(
            built["Grand Abolisher"]["displayed_tiers"][2],
            built["Grand Abolisher"]["full_tiers"][2],
            args.report_cap,
        )
    else:
        print("\nMarisi visibility gate (Amendment 4.2): SKIPPED -- Grand Abolisher not in this run's anchor list")

    # ---- Gate 4: boilerplate burial (Amendment 4.3) ----
    abolisher_burial_passed = True
    if "Grand Abolisher" in built:
        abolisher_burial_passed = check_rank_precedence(
            "Boilerplate burial gate (Grand Abolisher)",
            built["Grand Abolisher"]["displayed_tiers"][2],
            lambda r: r["name"] in ABOLISHER_BURIAL_TARGETS,
            is_unexempted_boilerplate(ABOLISHER_BOILERPLATE_FRAGMENT, BURIAL_GATE_TAG_EXEMPT_THRESHOLD),
            f"target card {sorted(ABOLISHER_BURIAL_TARGETS)}",
            f"{ABOLISHER_BOILERPLATE_FRAGMENT!r} boilerplate (fragment-identical, tag-unexempted)",
        )
    else:
        print("\nBoilerplate burial gate (Grand Abolisher): SKIPPED -- not in this run's anchor list")

    myrel_burial_passed = True
    if "Myrel, Shield of Argive" in built:
        myrel_burial_passed = check_rank_precedence(
            "Boilerplate burial gate (Myrel, Shield of Argive)",
            built["Myrel, Shield of Argive"]["displayed_tiers"][2],
            lambda r: r.get("fragment") == MYREL_BETTER_FRAGMENT,
            is_unexempted_boilerplate(MYREL_WORSE_FRAGMENT, BURIAL_GATE_TAG_EXEMPT_THRESHOLD),
            f"{MYREL_BETTER_FRAGMENT!r} cluster (fragment-identical)",
            f"{MYREL_WORSE_FRAGMENT!r} cluster (fragment-identical, tag-unexempted)",
        )
    else:
        print("\nBoilerplate burial gate (Myrel): SKIPPED -- not in this run's anchor list")

    # ---- Gate 5: mono-color proximity (v2.2 Amendment, Grand Abolisher) ----
    proximity_passed = True
    if "Grand Abolisher" in built:
        abolisher_tier2 = built["Grand Abolisher"]["displayed_tiers"][2]
        proximity_passed = check_mono_color_proximity(
            abolisher_tier2, ABOLISHER_PROXIMITY_TARGET, ABOLISHER_PROXIMITY_MV_FLOOR,
        )
        by_name = {r["name"]: r for r in abolisher_tier2}
        print("\nSen Triplets vs Voice of Victory breakdown (printed prominently per the change order):")
        print_rank_breakdown("Sen Triplets", by_name.get("Sen Triplets"))
        print_rank_breakdown("Voice of Victory", by_name.get("Voice of Victory"))
    else:
        print("\nMono-color proximity gate (Grand Abolisher): SKIPPED -- not in this run's anchor list")

    # ---- Gate 6: sanity ordering (v2.2 Amendment, Sol Ring Tier 1) ----
    sanity_ordering_passed = True
    if "Sol Ring" in built:
        sanity_ordering_passed = check_sol_ring_sanity_ordering(
            built["Sol Ring"]["displayed_tiers"][1], SOL_RING_SANITY_TRIO,
        )
    else:
        print("\nSanity ordering gate (Sol Ring): SKIPPED -- not in this run's anchor list")

    # ---- v2.3 gates 1, 2, 2b, 3-4, 5 (Grand Abolisher) ----
    vov_placement_passed = True
    sen_triplets_exile_passed = True
    partial_lock_passed = True
    scope_duration_passed = True
    movement_passed = True
    if "Grand Abolisher" in built:
        abolisher_tier2 = built["Grand Abolisher"]["displayed_tiers"][2]
        vov_placement_passed = check_vov_placement(abolisher_tier2)
        sen_triplets_exile_passed = check_sen_triplets_exile(
            abolisher_tier2, built["Grand Abolisher"]["full_tiers"][2],
        )
        partial_lock_passed = check_partial_lock_movement(abolisher_tier2, TOTAL_LOCK_SAME_CI_MV_FLOOR)
        scope_duration_passed = check_scope_duration_spotchecks(cards, card_docs, name_index, ngram_df, clause_df, keyword_df, paragraph_index, args)
        movement_passed = check_movement_gate(abolisher_tier2)
    else:
        print("\nv2.3 gates (VoV placement, Sen Triplets exile, partial-lock, scope/duration, movement): "
              "SKIPPED -- Grand Abolisher not in this run's anchor list")

    # ---- v2.4 gates 1-4 ----
    godsend_passed = True
    polarity_family_passed = True
    if "Grand Abolisher" in built:
        abolisher_tier2 = built["Grand Abolisher"]["displayed_tiers"][2]
        godsend_passed = check_godsend_gate(abolisher_tier2, cards, card_docs, name_index, ngram_df, clause_df, keyword_df, paragraph_index, args)
        polarity_family_passed = check_polarity_family_gate(abolisher_tier2, cards, card_docs, name_index, ngram_df, clause_df, keyword_df, paragraph_index, args)
    else:
        print("\nGodsend / polarity family gates: SKIPPED -- Grand Abolisher not in this run's anchor list")

    basandra_passed = True
    if "Marisi, Breaker of the Coil" in built:
        basandra_passed = check_basandra_gate(
            built["Marisi, Breaker of the Coil"]["full_tiers"][2], cards, card_docs, name_index, ngram_df,
            clause_df, keyword_df, paragraph_index, args,
        )
    else:
        print("\nBasandra gate: SKIPPED -- Marisi not in this run's anchor list")

    # ---- v2.9 gate 3: six-anchor stability diffs, BLOCKING AGAIN ----
    # v2.5's session amendment downgraded this to informational (approved-anchor
    # stability no longer protected against AFFINITY-driven reshuffling). v2.9
    # gate 3 explicitly reinstates blocking for THIS round's new mechanisms:
    # "any movement NOT explained by a keyword or reminder term = STOP" --
    # affinity/polarity/condition still count as explained too (continuity with
    # v2.5/v2.4), so nothing already-approved regresses; only movement with NO
    # explanation at all now halts the run.
    stability_anchors_present = [a for a in ANCHOR_PANEL if a in built]
    if stability_anchors_present:
        print(
            "\n[v2.9 gate 3] Stability is BLOCKING again for this round: new keyword/reminder-driven "
            "rows are expected and non-blocking (entries are never individually checked), but any "
            "MOVED or EXITED row not explained by polarity/condition/affinity/keyword/reminder/traced "
            "DF drift = STOP."
        )
        print(
            "  rebuilding a legacy (pre-v2.9) ngram index for DF-drift tracing "
            "(Captain's ruling: reorders must be traced to a named culprit, not assumed)..."
        )
        legacy_card_docs = {oid: build_card_doc(c, enable_v29_mechanisms=False) for oid, c in cards.items()}
        _, _, _, legacy_ngram_index, legacy_ngram_df = build_indexes(legacy_card_docs, args.ngram_min_len)
        stability_passed = check_stability_gate(
            stability_anchors_present, built, args.ngram_min_len, legacy_ngram_index, legacy_ngram_df,
            ngram_index, ngram_df, card_docs, blocking=True,
        )
    else:
        print("\nStability diffs: SKIPPED -- no anchors from the panel in this run's anchor list")
        stability_passed = True

    # ---- v2.5 gate 1: the ruling itself (Drannith > Avatar's Wrath, Grand Abolisher Tier 2) ----
    drannith_wrath_passed = True
    if "Grand Abolisher" in built:
        drannith_wrath_passed = check_drannith_wrath_gate(
            built["Grand Abolisher"]["full_tiers"][2], DRANNITH_WRATH_MARGIN_CEILING,
        )
    else:
        print("\nDrannith vs Avatar's Wrath gate: SKIPPED -- Grand Abolisher not in this run's anchor list")

    # ---- v2.6 amendment 1, gate 1: Grand Abolisher's exact 16-card corroboration exile ----
    abolisher_corroboration_passed = True
    if "Grand Abolisher" in built:
        abolisher_corroboration_passed = check_abolisher_corroboration_gate(
            built["Grand Abolisher"]["disqualified"], built["Grand Abolisher"]["full_tiers"][2],
        )
    else:
        print("\nTier 2 corroboration gate: SKIPPED -- Grand Abolisher not in this run's anchor list")

    # ---- v2.6 amendment 2, gate 4: Defense Grid vs Abolisher's Tier 3 top 10 ----
    # DOWNGRADED TO INFORMATIONAL per Captain's post-v2.6 ruling: Defense Grid landed
    # at position 31, not the anticipated "close but outside (11-15)" case. The
    # turn-scoped mechanism is verified correct; the remaining distance is genuine
    # tag-overlap distance from an unrelated cluster, not a constant to retune.
    # check_defense_grid_gate() always returns a diagnostic dict, never blocks --
    # the finding is printed to terminal and threaded into the Abolisher report.
    defense_grid_info = None
    if "Grand Abolisher" in built:
        defense_grid_info = check_defense_grid_gate(
            built["Grand Abolisher"]["displayed_tiers"][3], built["Grand Abolisher"]["full_tiers"][3],
        )
    else:
        print("\nDefense Grid gate: SKIPPED -- Grand Abolisher not in this run's anchor list")

    # ---- v2.6 amendment 2, gate 5: Tier 3 movement must trace to rule:turn-scoped ----
    t3_anchors_present = [a for a in ANCHOR_PANEL if a in built]
    t3_turn_scoped_passed = True
    if t3_anchors_present:
        t3_turn_scoped_passed = check_t3_turn_scoped_movement(t3_anchors_present, built)
    else:
        print("\nTier 3 turn-scoped movement gate: SKIPPED -- no anchors from the panel in this run's anchor list")

    # ---- v2.9 gate 2: Zurgo, Thunder's Decree gains Tier 1/2 rows via Mobilize ----
    zurgo_keyword_passed = True
    if ZURGO in built:
        zurgo_keyword_passed = check_zurgo_keyword_gate(
            built[ZURGO]["full_tiers"][1], built[ZURGO]["full_tiers"][2], args.report_cap,
        )
    else:
        print(f"\nZurgo keyword-kinship gate: SKIPPED -- {ZURGO!r} not in this run's anchor list")

    # ---- v2.9 gate 4: evergreen-floor self-consistency verification (all anchors) ----
    evergreen_floor_passed = check_evergreen_floor_gate(built, args.ngram_df_floor)

    # ---- Phase 5 (RULING-MANIFEST-2026-07-09.md): new outcome-form gates G-A..G-J ----
    gate_ctx = build_gate_ctx(
        cards, card_docs, name_index, card_tags, card_tags_t3, paragraph_index, clause_index,
        clause_df, ngram_index, ngram_df, tag_index, keyword_index, keyword_df, mana_index,
        granted_keyword_index, turn_scoped_matches, idf, idf_t3, n_total_cards, args,
        vanilla_creature_index,
    )
    ga_passed = check_ga_boros_charm_gate(gate_ctx)
    gb_passed = check_gb_swiftfoot_boots_gate(gate_ctx)
    gc_passed = check_gc_faithless_looting_gate(gate_ctx)
    gd_passed = check_gd_lane1c_gate(gate_ctx)
    ge_passed = check_ge_hero_of_bladehold_gate(gate_ctx)
    gf_passed = check_gf_arcane_signet_gate(gate_ctx)
    gg_passed = check_gg_sol_ring_cascade_gate(gate_ctx)
    gh_passed = check_gh_zero_overlap_gate(gate_ctx)
    gi_passed = check_gi_guild_pair_gate(gate_ctx)
    gj_passed = check_gj_ignoble_hierarch_gate(gate_ctx)
    gk_passed = check_gk_craterhoof_endraze_gate(gate_ctx)
    gl_passed = check_gl_promoted_phrase_gate(gate_ctx)
    gm_passed = check_gm_vanilla_creature_gate(gate_ctx)
    gn_passed = check_gn_discovery_superset_gate(gate_ctx)

    if not (self_check_passed and tier0_exclusion_passed and symmetry_passed and marisi_gate_passed
            and abolisher_burial_passed and myrel_burial_passed
            and proximity_passed and sanity_ordering_passed
            and vov_placement_passed and sen_triplets_exile_passed and partial_lock_passed
            and scope_duration_passed and movement_passed
            and godsend_passed and polarity_family_passed and basandra_passed
            and drannith_wrath_passed and abolisher_corroboration_passed
            and t3_turn_scoped_passed and stability_passed
            and zurgo_keyword_passed and evergreen_floor_passed
            and ga_passed and gb_passed and gc_passed and gd_passed and ge_passed
            and gf_passed and gg_passed and gh_passed and gi_passed and gj_passed
            and gk_passed and gl_passed and gm_passed and gn_passed):
        halt("one or more validation gates failed — reports NOT written (see output above)")

    # ---- v2.5 spot-check block (deliverable: subtypes, affinity, MVΔ audit rider) ----
    if "Grand Abolisher" in built:
        run_v25_spotcheck(
            cards, card_docs, name_index, ngram_df, args, built["Grand Abolisher"]["full_tiers"][2],
        )
    else:
        print("\nv2.5 spot-check block: SKIPPED -- Grand Abolisher not in this run's anchor list")

    # ---- All gates passed: write everything to disk ----
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FULL_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    CLAUSE_DF_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(CLAUSE_DF_PATH, "wt", encoding="utf-8") as f:
        json.dump(dict(sorted(clause_df.items())), f, sort_keys=True)
    print(f"\nwrote {CLAUSE_DF_PATH}")

    with gzip.open(NGRAM_DF_PATH, "wt", encoding="utf-8") as f:
        json.dump(dict(sorted(ngram_df.items())), f, sort_keys=True)
    print(f"wrote {NGRAM_DF_PATH}")

    crosscheck_md = build_tagger_scope_crosscheck(built, card_tags, tag_index)
    crosscheck_path = REPORTS_DIR / "tagger-scope-crosscheck.md"
    crosscheck_path.write_text(crosscheck_md, encoding="utf-8")
    print(f"wrote {crosscheck_path}")

    for anchor_name in anchors:
        b = built[anchor_name]
        footer_lines = []
        append_footer(footer_lines, anchor_name, b["displayed_tiers"], self_check_info, defense_grid_info)
        report_md = b["report_body"] + "\n".join(footer_lines)

        out_path = REPORTS_DIR / f"{filename_slug(anchor_name)}.md"
        out_path.write_text(report_md, encoding="utf-8")

        for full_info in b["full_list_files"].values():
            (FULL_REPORTS_DIR / full_info["filename"]).write_text(full_info["content"], encoding="utf-8")

        counts = b["counts"]
        print(
            f"  {anchor_name}: tier0={counts[0]} tier1={counts[1]} "
            f"tier2={counts[2]} tier3={counts[3]} -> {out_path}"
        )

    print(f"\ndone — {len(anchors)} anchor report(s) in {REPORTS_DIR}/")


if __name__ == "__main__":
    main()
