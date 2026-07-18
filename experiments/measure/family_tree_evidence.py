#!/usr/bin/env python3
"""MEASUREMENT-ONLY, read-only. T3-BUILDOUT-PLAYBOOK.md Step 4 (family-tree
evidence audit). Implements DERIVED-TAG-LAYER-SPEC.md's v1 derivation
patterns as a THROWAWAY script -- never imported by tier_engine.py, never
wired into scoring. Follows the v2.6 amendment 2 (rule:turn-scoped) ritual:
print each pattern, its corpus DF/idf, and a fixed-seed sample, BEFORE any
downstream analysis uses it.

Produces the evidence docs/FAMILY-TREE-EVIDENCE.md cites:
  1. corpus DF/idf per derived tag (both polarities canonicalized into one
     slug per Lesson 1, scope-split into two slugs for cast per the spec).
  2. pairwise co-occurrence + conditional probability between derived tags.
  3. cross-reference against the Scryfall Tagger taxonomy (which Tagger
     tags blanket which derived populations) -- a redundancy signal, not a
     laundering path (the anti-laundering guard: corpus behavior and
     exemplar cards outrank tag co-occurrence wherever they disagree).
  4. named match lists per tag, for picking real exemplar/near-miss panels.
  5. spot-checks against cards named in prior gate/punch-list history
     (Grand Abolisher, MANA_ONLY_FAMILY, PARTIAL_LOCK_CARDS, Basandra,
     Silence, Godsend, Myr Reservoir, Vexing Shusher...).

Run: python3 experiments/measure/family_tree_evidence.py
(run twice to confirm determinism -- no randomness beyond the fixed seed)
"""
import sys
import json
import math
import random
import re
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402

OUT_DIR = REPO_ROOT / "experiments" / "out" / "measurement"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_SIZE = 20
SAMPLE_SEED = 20260717  # today's date, same fixed-seed-for-determinism convention as TURN_SCOPED_SAMPLE_SEED


# ---------------------------------------------------------------------------
# v1 derivation patterns (DERIVED-TAG-LAYER-SPEC.md's "V1 derivation set").
# Each pattern is searched against a card's composed_full_text (already
# lowercased, reminder-stripped, self-name-substituted -- same text
# TURN_SCOPED_RE itself searches, so Split Second's reminder-only "can't
# cast spells or activate abilities..." explanation is excluded exactly the
# way it is for the shipped derivation, not by a separate carve-out here).
# Regex windows calibrated against the live corpus this session (raw
# oracle_text scan, not recalled) -- see the session's calibration dump for
# the phrase-frequency scan each pattern below is grounded in.
# ---------------------------------------------------------------------------

RESTRICTS_CAST_NEG_RE = re.compile(r"can'?t cast\b")
RESTRICTS_CAST_POS_RE = re.compile(
    r"can cast (?:spells?|noncreature spells|creature spells|instant or sorcery spells|"
    r"sorcery spells|instant spells)(?: and activate abilities)? only\b"
)

RESTRICTS_ACTIVATION_NEG_RE = re.compile(
    r"activated abilities?(?:[^.]{0,60})?can'?t be activated"
    r"|can'?t activate\b"
    r"|activate abilities that aren'?t mana abilities\b"
)
RESTRICTS_ACTIVATION_POS_RE = re.compile(r"can activate [a-z ]*only\b|activate abilities only\b")

COST_INCREASE_RE = re.compile(r"costs? \{\d+\} more to cast")
COST_REDUCTION_RE = re.compile(r"costs? \{\d+\} less to cast")

PAY_TAX_RE = re.compile(r"unless [a-z' ]{0,30}\bpays?\b")

UNCOUNTERABLE_RE = re.compile(r"can'?t be countered")

PROHIBITS_ATTACK_RE = re.compile(r"can'?t attack\b")
PROHIBITS_BLOCK_RE = re.compile(r"can'?t block\b")

# rule:turn-scoped is NOT redefined here -- reused verbatim from tier_engine.py
# (te.TURN_SCOPED_RE / te.find_turn_scoped_matches), the already-shipped v2.6
# amendment 2 pilot this whole layer generalizes.


def find_matches(card_docs: dict, pattern: re.Pattern) -> dict:
    """oracle_id -> matched paragraph text (first face/paragraph hit), over
    composed_full_text for the DF count, then re-located to the specific
    paragraph for scope classification. Mirrors find_turn_scoped_matches's
    shape/convention exactly. NOTE: returns only the FIRST matching
    paragraph per card -- fine for a single DF count, but see
    find_all_paragraph_matches() for callers (uncounterable self/granted
    split) that need every qualifying paragraph on a card, since a card can
    carry both forms at once (Vexing Shusher: "This spell can't be
    countered." AND "{R/G}: Target spell can't be countered." -- the first-
    match-only version silently drops the second sentence)."""
    matches = {}
    for oracle_id in sorted(card_docs):
        doc = card_docs[oracle_id]
        if not pattern.search(doc["composed_full_text"]):
            continue
        matched_paragraph = None
        for face in doc["faces"]:
            for p in face["matchable_paragraphs"]:
                if pattern.search(p):
                    matched_paragraph = p
                    break
            if matched_paragraph:
                break
        matches[oracle_id] = matched_paragraph or doc["composed_full_text"]
    return matches


def find_all_paragraph_matches(card_docs: dict, pattern: re.Pattern) -> dict:
    """oracle_id -> list of ALL matching paragraphs across all faces (not
    just the first) -- needed wherever a card can carry more than one
    qualifying sentence with DIFFERENT classifications (e.g. Vexing
    Shusher's self AND granted uncounterable lines)."""
    matches = {}
    for oracle_id in sorted(card_docs):
        doc = card_docs[oracle_id]
        if not pattern.search(doc["composed_full_text"]):
            continue
        hits = []
        for face in doc["faces"]:
            for p in face["matchable_paragraphs"]:
                if pattern.search(p):
                    hits.append(p)
        matches[oracle_id] = hits or [doc["composed_full_text"]]
    return matches


def print_derivation(label, pattern, matches, card_docs, n_total_cards, log):
    df = len(matches)
    idf = math.log(n_total_cards / df) if df > 0 else 0.0
    log(f"\n-- {label} --")
    log(f"  regex: {pattern.pattern}")
    log(f"  corpus DF = {df:,} / {n_total_cards:,} cards, idf = {idf:.2f}")
    sample_ids = random.Random(SAMPLE_SEED).sample(sorted(matches), min(SAMPLE_SIZE, len(matches)))
    log(f"  {len(sample_ids)}-card random sample (seed={SAMPLE_SEED}):")
    for oid in sorted(sample_ids, key=lambda o: card_docs[o]["name"]):
        log(f"    {card_docs[oid]['name']}: {matches[oid][:100]!r}")
    return df, idf


def classify_scope_split(matches: dict, card_docs: dict) -> tuple:
    """Splits a matches dict into (opponent_scoped, other_scoped) oracle_id
    sets via te.extract_scope() on the matched paragraph -- reuses the
    EXISTING SCOPE_PATTERNS machinery per the playbook's instruction, no new
    scope vocabulary invented here. opponent_scoped = scope in {all_opp,
    single}; other_scoped = everything else (symmetric/self/unknown)."""
    opp, other = {}, {}
    for oid, paragraph in matches.items():
        scope = te.extract_scope(paragraph)
        if scope in ("all_opp", "single"):
            opp[oid] = paragraph
        else:
            other[oid] = paragraph
    return opp, other


def main():
    log_lines = []

    def log(s=""):
        print(s)
        log_lines.append(s)

    log("=" * 100)
    log("FAMILY-TREE EVIDENCE MEASUREMENT -- T3-BUILDOUT-PLAYBOOK.md Step 4")
    log("Reproduce with: python3 experiments/measure/family_tree_evidence.py")
    log("=" * 100)

    cards = te.load_cards(te.CARDS_PATH)
    log(f"loaded {len(cards):,} cards from {te.CARDS_PATH}")
    name_index = te.build_name_index(cards)
    n_total_cards = len(cards)

    raw_keyword_df = te.compute_keyword_df_from_cards(cards)
    log("normalizing corpus (self-name substitution, reminder strip, paragraph/clause split)...")
    card_docs = {
        oracle_id: te.build_card_doc(card, keyword_df=raw_keyword_df)
        for oracle_id, card in cards.items()
    }

    keyword_vocabulary = te.build_keyword_vocabulary(cards)
    for doc in card_docs.values():
        doc["granted_keyword_facts"] = te.build_granted_keyword_facts(doc, keyword_vocabulary)

    card_tags = te.load_card_tags(te.CARD_TAGS_PATH)
    log(f"loaded Tagger tags for {len(card_tags):,} cards")
    tag_index = te.build_tag_index(card_tags)
    tagger_idf, tagger_card_count, n_tagged_cards = te.compute_tag_stats(card_tags)

    # =========================================================================
    # PART 1 -- each v1 derivation: pattern, corpus DF/idf, fixed-seed sample
    # =========================================================================
    log("\n" + "#" * 100)
    log("# PART 1 -- v1 derivation patterns: corpus DF/idf + eyeball sample")
    log("#" * 100)

    derived_tags = {}  # slug -> {oid: matched_paragraph}
    derived_df = {}
    derived_idf = {}

    def register(slug, matches):
        derived_tags[slug] = matches
        derived_df[slug] = len(matches)
        derived_idf[slug] = math.log(n_total_cards / len(matches)) if matches else 0.0

    # --- 1. restricts-cast / restricts-opponent-cast (both polarities) ---
    cast_neg = find_matches(card_docs, RESTRICTS_CAST_NEG_RE)
    cast_pos = find_matches(card_docs, RESTRICTS_CAST_POS_RE)
    print_derivation("restricts-cast, NEGATIVE polarity (\"can't cast...\")", RESTRICTS_CAST_NEG_RE, cast_neg, card_docs, n_total_cards, log)
    print_derivation("restricts-cast, POSITIVE polarity (\"can cast ... only...\")", RESTRICTS_CAST_POS_RE, cast_pos, card_docs, n_total_cards, log)
    cast_all = {**cast_neg, **cast_pos}
    cast_opp, cast_other = classify_scope_split(cast_all, card_docs)
    log(f"\n  Lesson-1 canonicalization: {len(cast_all):,} total cards ({len(cast_neg):,} negative + {len(cast_pos):,} positive, overlap={len(set(cast_neg) & set(cast_pos))})")
    log(f"  scope split (te.extract_scope on matched paragraph): opponent-scoped (all_opp/single)={len(cast_opp):,}, other (symmetric/self/unknown)={len(cast_other):,}")
    register("rule:restricts-opponent-cast", cast_opp)
    register("rule:restricts-cast", cast_other)

    # --- 2. restricts-activation (both polarities, scope recorded not split) ---
    act_neg = find_matches(card_docs, RESTRICTS_ACTIVATION_NEG_RE)
    act_pos = find_matches(card_docs, RESTRICTS_ACTIVATION_POS_RE)
    print_derivation("restricts-activation, NEGATIVE polarity", RESTRICTS_ACTIVATION_NEG_RE, act_neg, card_docs, n_total_cards, log)
    print_derivation("restricts-activation, POSITIVE polarity", RESTRICTS_ACTIVATION_POS_RE, act_pos, card_docs, n_total_cards, log)
    act_all = {**act_neg, **act_pos}
    act_scopes = Counter(te.extract_scope(p) for p in act_all.values())
    log(f"\n  combined: {len(act_all):,} cards. scope distribution: {dict(act_scopes)}")
    register("rule:restricts-activation", act_all)

    # --- 3. cost-increase / cost-reduction ---
    cost_inc = find_matches(card_docs, COST_INCREASE_RE)
    cost_red = find_matches(card_docs, COST_REDUCTION_RE)
    print_derivation("cost-increase", COST_INCREASE_RE, cost_inc, card_docs, n_total_cards, log)
    print_derivation("cost-reduction", COST_REDUCTION_RE, cost_red, card_docs, n_total_cards, log)
    inc_scopes = Counter(te.extract_scope(p) for p in cost_inc.values())
    log(f"  cost-increase scope distribution: {dict(inc_scopes)}")
    register("rule:cost-increase", cost_inc)
    register("rule:cost-reduction", cost_red)

    # --- 4. pay-tax ---
    tax = find_matches(card_docs, PAY_TAX_RE)
    print_derivation("pay-tax", PAY_TAX_RE, tax, card_docs, n_total_cards, log)
    register("rule:pay-tax", tax)

    # --- 5. uncounterable (self vs granted split) ---
    uncounter_all = find_matches(card_docs, UNCOUNTERABLE_RE)
    # Per-SENTENCE scan (not first-paragraph-only): a card can carry BOTH
    # forms at once -- Vexing Shusher has "This spell can't be countered."
    # (self) AND "{R/G}: Target spell can't be countered." (granted) as two
    # separate matchable_paragraphs. find_matches()'s first-hit-only shape
    # would silently drop the second sentence and misclassify the card as
    # self-only; caught verifying this exact named example before shipping
    # the split.
    uncounter_all_paragraphs = find_all_paragraph_matches(card_docs, UNCOUNTERABLE_RE)
    uncounter_self, uncounter_granted = {}, {}
    for oid, paragraphs in uncounter_all_paragraphs.items():
        for paragraph in paragraphs:
            sentence = None
            for s in te.split_clauses(paragraph):
                if UNCOUNTERABLE_RE.search(s):
                    sentence = s
                    break
            sentence = sentence or paragraph
            if "target spell" in sentence:
                uncounter_granted[oid] = paragraph
            else:
                uncounter_self[oid] = paragraph
    print_derivation("uncounterable, ALL (pre-split)", UNCOUNTERABLE_RE, uncounter_all, card_docs, n_total_cards, log)
    both_forms = sorted(set(uncounter_self) & set(uncounter_granted))
    log(f"  self/granted split: self={len(uncounter_self):,} (this spell / spells you cast or control), granted={len(uncounter_granted):,} (\"target spell can't be countered\")")
    log(f"  cards carrying BOTH forms ({len(both_forms)}): {[card_docs[o]['name'] for o in both_forms]}")
    register("rule:uncounterable-self", uncounter_self)
    register("rule:grants-uncounterable", uncounter_granted)

    # --- 6. turn-scoped (shipped, reused verbatim) ---
    turn_scoped_matches, turn_scoped_idf = te.run_turn_scoped_derivation(card_docs, n_total_cards)
    log("")
    register("rule:turn-scoped", turn_scoped_matches)

    # --- 7. grants-<keyword> (zero new parsing, from granted_keyword_facts) ---
    grant_cards = {}
    grant_keyword_counter = Counter()
    for oid, doc in card_docs.items():
        facts = doc["granted_keyword_facts"]
        if not facts:
            continue
        kws = set()
        for f in facts:
            if f["keywords"]:
                kws.update(f["keywords"])
        if kws:
            grant_cards[oid] = ", ".join(sorted(kws))
            for k in kws:
                grant_keyword_counter[k] += 1
    log(f"\n-- grants-<keyword> (from existing granted_keyword_facts, GRANT_SIZE_CEILING={te.GRANT_SIZE_CEILING}) --")
    log(f"  corpus DF (any qualifying grant) = {len(grant_cards):,} / {n_total_cards:,} cards")
    top_grant_kws = sorted(grant_keyword_counter.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
    log(f"  top 20 granted keywords by DF: {top_grant_kws}")
    register("rule:grants-keyword", grant_cards)

    # --- 8. prohibits-attack / prohibits-block ---
    atk = find_matches(card_docs, PROHIBITS_ATTACK_RE)
    blk = find_matches(card_docs, PROHIBITS_BLOCK_RE)
    print_derivation("prohibits-attack", PROHIBITS_ATTACK_RE, atk, card_docs, n_total_cards, log)
    print_derivation("prohibits-block", PROHIBITS_BLOCK_RE, blk, card_docs, n_total_cards, log)
    both = set(atk) & set(blk)
    log(f"  cards firing BOTH (e.g. \"can't attack or block\" templating): {len(both):,}")
    register("rule:prohibits-attack", atk)
    register("rule:prohibits-block", blk)

    log("\n" + "=" * 60)
    log("Derived tag corpus DF/idf summary (all tags this session measured):")
    log("=" * 60)
    for slug in sorted(derived_df, key=lambda s: -derived_df[s]):
        ceiling_note = "<= DERIVED_QUALIFY_DF_CEILING(172)" if derived_df[slug] <= 172 else "> 172 (cannot solo-qualify Tier 3 per Lesson 3)"
        log(f"  {slug}: DF={derived_df[slug]:,}  idf={derived_idf[slug]:.2f}  [{ceiling_note}]")

    # =========================================================================
    # PART 2 -- pairwise co-occurrence + conditional probability between
    # derived tags (evidence source 1, "strongest -- compute it, don't recall it")
    # =========================================================================
    log("\n" + "#" * 100)
    log("# PART 2 -- pairwise derived-tag co-occurrence / conditional probability")
    log("#" * 100)
    slugs = sorted(derived_tags)
    log(f"\n{'pair':<70} {'|A|':>6} {'|B|':>6} {'|A&B|':>7} {'P(B|A)':>8} {'P(A|B)':>8} {'jaccard':>8}")
    pair_stats = {}
    for i, a in enumerate(slugs):
        set_a = set(derived_tags[a])
        for b in slugs[i + 1:]:
            set_b = set(derived_tags[b])
            inter = len(set_a & set_b)
            union = len(set_a | set_b)
            p_b_given_a = inter / len(set_a) if set_a else 0.0
            p_a_given_b = inter / len(set_b) if set_b else 0.0
            jaccard = inter / union if union else 0.0
            pair_stats[(a, b)] = (inter, p_b_given_a, p_a_given_b, jaccard)
            if inter > 0:
                log(f"{a + ' / ' + b:<70} {len(set_a):>6} {len(set_b):>6} {inter:>7} {p_b_given_a:>8.2f} {p_a_given_b:>8.2f} {jaccard:>8.3f}")

    # =========================================================================
    # PART 3 -- Tagger taxonomy cross-reference
    # =========================================================================
    log("\n" + "#" * 100)
    log("# PART 3 -- Scryfall Tagger cross-reference (which Tagger tags blanket which derived populations)")
    log("#" * 100)
    for slug in slugs:
        card_set = set(derived_tags[slug])
        if not card_set:
            continue
        tagger_counter = Counter()
        for oid in sorted(card_set):
            for entry in card_tags.get(oid, []):
                tagger_counter[entry["slug"]] += 1
        # Deterministic tie-break: Counter.most_common() ties preserve
        # first-insertion order, which here depends on iterating a set of
        # oracle_id strings -- Python randomizes str hash per process by
        # default, so set iteration order (and therefore tie-break winners)
        # silently differed between runs with identical counts. Caught by
        # the project's own "determinism x2" ritual before shipping this
        # script: two back-to-back runs produced different top-8 orderings
        # among tied counts (e.g. cost-increase's "symmetrical" vs "cycle"
        # both at 16/71 swapped position). Explicit (-count, slug) sort
        # fixes it independent of set iteration order.
        top = sorted(tagger_counter.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
        log(f"\n  {slug} (DF={len(card_set):,}) -- top Tagger tags among its members:")
        for tslug, cnt in top:
            coverage = cnt / len(card_set)
            blanket_flag = " <-- BLANKETS >=50% of this derived population" if coverage >= 0.5 else ""
            log(f"    {tslug}: {cnt:,}/{len(card_set):,} ({coverage:.0%}){blanket_flag}")
        if not top:
            log("    (no Tagger overlap at all -- zero of this derived population's members are Tagger-tagged with anything in common)")

    # =========================================================================
    # PART 4 -- Tagger <-> rule: redundancy table (Step 3's appended requirement)
    # =========================================================================
    log("\n" + "#" * 100)
    log("# PART 4 -- Tagger <-> rule: redundancy table (pairwise co-fire rates)")
    log("#" * 100)
    WATCH_TAGGER_SLUGS = [
        "hate-flash", "silence", "pacifism", "hate-attacker", "hate-counterspell",
        "hate-flashback", "cost-increaser", "tax", "cast-tax", "tax-attack", "tax-block",
        "counterspell", "counterspell-soft",
    ]
    log(f"\n{'tagger tag':<20} {'|tagger|':>9}  " + "  ".join(f"{s.replace('rule:', ''):<12}" for s in slugs))
    for tslug in WATCH_TAGGER_SLUGS:
        tagger_set = tag_index.get(tslug, set())
        if not tagger_set:
            log(f"{tslug:<20} {'(0, not in Tagger dump)':>9}")
            continue
        row = [f"{tslug:<20} {len(tagger_set):>9}  "]
        for slug in slugs:
            rule_set = set(derived_tags[slug])
            inter = len(tagger_set & rule_set)
            rate = inter / len(tagger_set) if tagger_set else 0.0
            row.append(f"{inter:>4}({rate:.0%})".ljust(14))
        log("".join(row))

    # =========================================================================
    # PART 5 -- named spot-checks against prior gate/punch-list history
    # =========================================================================
    log("\n" + "#" * 100)
    log("# PART 5 -- spot-checks against cards named in prior gates/punch-list entries")
    log("#" * 100)
    SPOT_CHECK_NAMES = sorted(
        {"Grand Abolisher", "Myrel, Shield of Argive", "Marisi, Breaker of the Coil",
         "Sol Ring", "Preordain", "Sakura-Tribe Elder"}
        | te.ABOLISHER_BURIAL_TARGETS
        | te.MANA_ONLY_FAMILY
        | te.PARTIAL_LOCK_CARDS
        | {"Basandra, Battle Seraph", "Kutzil, Malamet Exemplar", "Godsend", "Voice of Victory",
           "Silence", "Mandate of Peace", "Conqueror's Flail", "Vexing Shusher", "Defense Grid",
           "Sphere of Resistance", "Rhystic Study", "Mystic Remora", "Dosan the Falling Leaf",
           "City of Solitude", "Teferi, Time Raveler", "Drannith Magistrate", "Aven Mindcensor",
           "Lavinia, Azorius Renegade", "Thalia, Guardian of Thraben", "Stony Silence",
           "Cursed Totem", "Collector Ouphe", "Ghostly Prison", "Propaganda", "Ensnaring Bridge",
           "Pacifism", "Arrest", "Encrust", "Faith's Fetters", "Trinisphere", "Thorn of Amethyst",
           "Aura of Silence", "Void Winnower", "Sphinx's Decree", "Damping Engine", "Abeyance",
           "Interdict", "Zurgo, Thunder's Decree"}
    )
    for name in SPOT_CHECK_NAMES:
        resolved = te.resolve_anchor(name, cards, name_index)
        if resolved is None:
            log(f"  {name}: NOT FOUND in corpus -- skipped")
            continue
        oid = resolved["oracle_id"]
        carried = [slug for slug, matches in derived_tags.items() if oid in matches]
        tagger_carried = sorted(e["slug"] for e in card_tags.get(oid, []))
        log(f"  {name}: derived={carried or '(none)'}")

    # write outputs
    out_path = OUT_DIR / "family_tree_evidence_report.txt"
    out_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path}")

    raw = {
        "derived_df": derived_df,
        "derived_idf": derived_idf,
        "derived_members": {slug: sorted(card_docs[oid]["name"] for oid in matches) for slug, matches in derived_tags.items()},
    }
    raw_path = OUT_DIR / "family_tree_evidence_raw.json"
    raw_path.write_text(json.dumps(raw, indent=0), encoding="utf-8")
    print(f"wrote {raw_path}")


if __name__ == "__main__":
    main()
