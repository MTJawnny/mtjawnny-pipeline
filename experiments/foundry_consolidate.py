#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- bootstrap loop "Consolidate (DET + SUP)" step.
Reads a batch's Stage 1B SYNTH results (experiments/out/foundry/
stage1b_raw_results[_batch<N>].jsonl), applies the evidence-quote-or-discard
gate, and writes a consolidated-axes file in the shape foundry_emit.py
consumes.

Batch 1 was free-form/open-coded (no codebook to close-code against yet),
so every instance went through unsupervised DET token-similarity
clustering. Batch 2+ is TWO-LANE (foundry_stage1b.py's system prompt asks
the model to check codebook fit first): each axis instance now carries a
"lane" field.
  - lane="codebook" AND label resolves to an ACTIVE codebook slug: attaches
    directly as an additional member of that existing axis. No clustering
    needed -- the model already did the matching, this just verifies it.
  - lane="codebook" but the label does NOT resolve (wrong slug, or a
    killed/merged/renamed one) -- a model-compliance anomaly, not a data
    error. Counted and reported, then folded into the free-lane clustering
    pool rather than silently trusted or silently dropped.
  - lane="free" (or batch 1, where "lane" is simply absent): same exact-
    normalized-label-token-set clustering as batch 1, unchanged.

Run: python3 experiments/foundry_consolidate.py --batch 2
"""
import sys
import json
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import validate_slug  # noqa: E402 -- D7 wiring, walk-ratification 2026-07-31

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"

STOPWORDS = {
    "a", "an", "the", "this", "that", "its", "it", "to", "of", "for", "with",
    "on", "in", "or", "and", "your", "you", "target", "card", "cards", "each",
    "any", "if", "is", "are", "be", "as", "at", "by", "from", "into", "onto",
    "another", "other", "spell", "spells", "ability", "abilities", "player",
    "players", "creature", "creatures", "permanent", "permanents", "when",
    "whenever", "until", "than", "then", "one", "may",
    # Structural MTG filler that dominates short label/definition token sets
    # without carrying mechanic-specific meaning -- measured live: without
    # these, "etb-triggered-ability" (a generic observation, not a T3 axis)
    # swallowed landfall-trigger, doubles-etb-triggers (the Panharmonicon
    # family), and mass-*-destruction into one 34-member false-merge cluster
    # at Jaccard>=0.5 over label+definition tokens. See git history / session
    # notes for the before/after.
    "enters", "battlefield", "trigger", "triggers", "triggered", "controller",
    "controls", "effect", "effects", "automatically", "own", "owns", "allows",
    "causes", "gain", "gains", "value",
}
STEM_SUFFIXES = ("ations", "ation", "ements", "ement", "ing", "ions", "ers",
                  "tion", "sion", "ion", "es", "ed", "er", "s")


def normalize_tokens(*texts: str) -> frozenset:
    words = re.findall(r"[a-z]+", " ".join(texts).lower())
    out = set()
    for w in words:
        if w in STOPWORDS or len(w) < 3:
            continue
        stemmed = w
        for suf in STEM_SUFFIXES:
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                stemmed = w[: -len(suf)]
                break
        out.add(stemmed)
    return frozenset(out)


# ---------------------------------------------------------------------------
# Deterministic label canonicalization (Captain directive, 2026-08-01):
# permanent reconcile-side infrastructure for scoring whether two
# independently-generated labels (different SYNTH runs, or SYNTH free-lane
# vs. a human-authored candidate) describe the SAME pattern, despite
# surface wording differences the model reinvents every run (batch-8 A/B
# found this dominates raw exact-match: "activated-mass-pump-and-opponent-
# drain" vs. "activated-team-pump-and-opponent-life-loss" for the identical
# card/judgment). Reuses the SAME grammar machinery validate_slug.py
# already enforces going forward -- this does not invent a parallel
# vocabulary, it applies the one already ratified.
# ---------------------------------------------------------------------------

# Ratified EFFECT-verb synonym collapsing (CODEBOOK-NAMING-GRAMMAR.md sec.4:
# "One verb per mechanic, chosen once, used everywhere") plus D-1..D-3's
# explicit retired-token replacements. Deliberately NOT a general free-text
# thesaurus -- every entry here traces to an explicit ratified rule, not a
# guess at what SYNTH might mean. Checked both pre- and post-stem.
CANONICAL_SYNONYM_MAP = {
    "creates": "create",              # D-2: bare verb stem
    "scaled": "scales",               # D-3: -scaled-by- retired, -scales-with- is canonical
    "dies": "death",                  # D-1: death-trigger is the family word, not dies
    "return": "bounce", "returning": "bounce",  # sec.4: bounce = return to hand
    "countered": "uncounterable",     # sec.10.2 ban + Q4: the only surviving vocabulary near this concept
}

# Slot buckets in CODEBOOK-NAMING-GRAMMAR.md sec.1 order
# (DELIVERY-EFFECT-OBJECT-SCOPE-QUALIFIER) -- checked in this order, first
# vocab a (stemmed, synonym-mapped) token matches wins. Tokens matching none
# of these fall into "descriptor" (ratified but slot-agnostic vocabulary --
# Q5 batch, glossary, keyword names) or "unclassified" (genuinely novel
# free-lane vocabulary with no ratified home yet) -- both still included in
# the canonical form (never dropped), just ordered last so they don't
# spuriously break equality between two labels that agree on every
# classified slot but differ in an unclassified tail token's position.
def _slot_vocab_order():
    return [
        ("delivery", validate_slug.DELIVERY_VOCAB),
        ("effect", validate_slug.EFFECT_VOCAB),
        ("object", validate_slug.OBJECT_VOCAB),
        ("scope", validate_slug.SCOPE_VOCAB),
        ("qualifier", validate_slug.QUALIFIER_VOCAB | validate_slug.SCALING_STAT_VOCAB
                       | validate_slug.COUNTER_TOKEN_VOCAB | validate_slug.RESTRICTION_VOCAB
                       | validate_slug.CANT_BE_BLOCKED_STEM_VOCAB),
        ("descriptor", validate_slug.WALK_RATIFICATION_VOCAB_20260731
                        | validate_slug.GLOSSARY_VOCAB | validate_slug.KEYWORD_VOCAB),
    ]


def _stem(token: str) -> str:
    for suf in STEM_SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 3:
            return token[: -len(suf)]
    return token


def canonicalize_label(label: str) -> str:
    """label may or may not carry the 'rule:' prefix. Pipeline: (1) D-2/D-3
    connective normalization via validate_slug.normalize_for_collision
    (catches creates-/scaled-by- as whole-connective substitutions before
    tokenizing loses that context); (2) per-token stem + ratified-synonym
    collapse (order: synonym, then stem, then synonym again in case
    stemming exposes a mappable root -- e.g. 'returning' -> stem 'return'
    -> synonym 'bounce'); (3) slot classification against validate_slug's
    closed vocabularies + reordering into canonical slot order, so two
    labels using the same concepts in a different word order collapse to
    the same string. NOT guaranteed to produce a "correct" slug -- a
    best-effort deterministic normal form for equality comparison between
    two independently-generated labels, nothing more."""
    bare = label[len("rule:"):] if label.startswith("rule:") else label
    bare = validate_slug.normalize_for_collision(bare)
    tokens = [t for t in bare.split("-") if t]

    slot_order = _slot_vocab_order()
    all_vocab = set()
    for _, vocab in slot_order:
        all_vocab |= vocab

    buckets = {name: [] for name, _ in slot_order}
    buckets["unclassified"] = []
    for raw in tokens:
        t = CANONICAL_SYNONYM_MAP.get(raw, raw)
        # Closed vocabularies hold the CORRECT surface form (e.g. "mass",
        # "creatures", "grants") -- check the token AS-IS against them
        # before stemming, so stemming never corrupts an already-valid
        # vocabulary word (e.g. "mass" -> stem "mas" is not in
        # QUALIFIER_VOCAB and would wrongly fall to "unclassified"). Only
        # stem (and re-check the synonym map on the stemmed root) when the
        # raw token isn't already a recognized vocabulary word.
        if t not in all_vocab:
            stemmed = _stem(t)
            t = CANONICAL_SYNONYM_MAP.get(stemmed, stemmed)
        for name, vocab in slot_order:
            if t in vocab:
                buckets[name].append(t)
                break
        else:
            buckets["unclassified"].append(t)

    parts = []
    for name, _ in slot_order:
        parts.extend(sorted(set(buckets[name])))
    parts.extend(sorted(set(buckets["unclassified"])))
    return "-".join(parts)


def load_active_codebook_slugs() -> dict:
    """Returns {slug: {"definition", "scope"}} for active axes, or {} if no
    codebook exists yet (batch 1)."""
    if not CODEBOOK_PATH.exists():
        return {}
    cb = json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))
    return {
        slug: {"definition": a["definition"], "scope": a["scope"]}
        for slug, a in cb["axes"].items() if a.get("status") == "active"
    }


def resolve_codebook_label(label: str, active_slugs: dict) -> str | None:
    """Exact match only, tolerating a missing 'rule:' prefix (a benign
    formatting slip, not a real ambiguity) -- never fuzzy."""
    if label in active_slugs:
        return label
    prefixed = label if label.startswith("rule:") else f"rule:{label}"
    if prefixed in active_slugs:
        return prefixed
    return None


def is_banned_restriction_family_label(label: str) -> bool:
    """D-4 (CODEBOOK-NAMING-GRAMMAR.md sec.3, wired D7 walk-ratification
    2026-07-31): the activation-restriction family is exclusively DET-owned;
    SYNTH must never be credited with one of these slugs under ANY lane, even
    if the model complied with the system prompt's own ban and this is a
    stray compliance slip. Checked against the exact 8-member closed family
    (validate_slug.ACTIVATION_RESTRICTION_FAMILY), not a prefix guess."""
    bare = label[len("rule:"):] if label.startswith("rule:") else label
    return bare in validate_slug.ACTIVATION_RESTRICTION_FAMILY


def resolve_codebook_grammar_label(label: str, active_slugs: dict) -> tuple:
    """D7 wiring: lane="codebook-grammar" resolution. Returns
    (resolved_slug_or_None, validator_result). A grammar-composed label must
    pass validate_slug() (charset/vocab/restriction-family/counter-law/cost-
    law/collision) to be accepted; CODEBOOK-NAMING-GRAMMAR.md sec.11: "anything
    neither exact-codebook nor grammar-valid stays lane=free" -- so an invalid
    label here means the CALLER downgrades this instance to lane="free"
    (folded into ordinary DET clustering), not discarded outright, matching
    the same non-punitive handling lane=codebook anomalies already get."""
    prefixed = label if label.startswith("rule:") else f"rule:{label}"
    result = validate_slug.validate_slug(prefixed, definition=None, all_slugs=list(active_slugs.keys()))
    if not result["ok"]:
        return None, result
    # Valid grammar-composed slug. If it already exists as an active codebook
    # axis (a prior batch already instantiated this exact virtual node),
    # attach to it directly like lane=codebook. Otherwise this is a brand
    # new grammar-instantiated candidate -- the caller's cluster/candidate
    # path handles that identically to a free-lane new_candidate axis, since
    # both need >=2 corroborating cards before promotion (a single quote-
    # verified member instantiates the grammar's virtual node per sec.11,
    # but this script's own single-card-cluster guard, TRIAGE-BATCH-2.md
    # sec.0/7.1, still applies -- one card is not corroboration).
    if prefixed in active_slugs:
        return prefixed, result
    return prefixed, result


def load_raw_instances(cards: dict, raw_results_path: Path) -> tuple:
    """Returns (instances, discarded, anomalies). Each instance carries
    oracle_id, name, lane, label, definition, actor_scope, quote, and (for
    free-lane / unresolved instances) its normalized token set for
    clustering. D7 wiring (walk-ratification 2026-07-31): `anomalies` counts
    lane="codebook" instances whose label didn't resolve to an active
    codebook slug (folded into free-lane clustering, not discarded) AND
    lane="codebook-grammar" instances whose label failed validate_slug()
    (also folded into free-lane clustering per CODEBOOK-NAMING-GRAMMAR.md
    sec.11: "anything neither exact-codebook nor grammar-valid stays
    lane=free"). A separate D-4 check rejects (discards outright, does NOT
    fold into clustering) any label from the closed activation-restriction
    family under any lane -- that family is exclusively DET-owned."""
    if not raw_results_path.exists():
        fc.halt(f"{raw_results_path} not found -- fetch batch results first")

    active_slugs = load_active_codebook_slugs()
    instances = []
    discarded = []
    anomalies = []
    parse_failures = 0
    refusals = 0
    non_succeeded = {}  # result-type -> count, for errored/canceled/expired rows
    codebook_hits = 0
    grammar_hits = 0
    grammar_new_instantiations = 0
    banned_restriction_family_hits = 0

    for line in raw_results_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        oracle_id = row["custom_id"]
        result = row["result"]
        if result["type"] != "succeeded":
            # Non-succeeded rows (errored/canceled/expired) carry no message at
            # all -- the request was never answered. Batch-3 hit a live
            # "overloaded_error" (transient infra hiccup, not a content/data
            # issue) on one card out of 1,200. Treated the same way as a
            # model refusal: zero axes contributed, logged loudly, not a
            # crash -- a single dropped card is not the "unexpected state"
            # this halt exists to catch; a MASS failure still would be
            # (see the loud percentage check below).
            non_succeeded[result["type"]] = non_succeeded.get(result["type"], 0) + 1
            continue

        message = result["message"]
        content = message.get("content") or []
        if not content:
            # Model declined to respond (stop_reason == "refusal") -- known,
            # rare, non-crashing case: treat as zero axes for this card, do
            # not treat as a parse failure (the request itself succeeded).
            refusals += 1
            continue

        card = cards.get(oracle_id)
        if card is None:
            fc.halt(f"card {oracle_id} from batch results not found in corpus")

        text = content[0]["text"]
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            parse_failures += 1
            continue

        # composed oracle text across all faces, for the evidence-quote check
        faces = card.get("card_faces") or [card]
        full_text = "\n".join((f.get("oracle_text") or "") for f in faces).lower()

        for axis in data.get("axes", []):
            quote = axis.get("evidence_quote", "")
            label = axis.get("label", "").strip()
            definition = axis.get("definition", "").strip()
            actor_scope = axis.get("actor_scope", "").strip()
            lane = axis.get("lane")  # absent entirely for batch-1 (free-form only)
            if not (quote and label and definition and actor_scope):
                discarded.append({"oracle_id": oracle_id, "reason": "missing field", "axis": axis})
                continue
            if quote.lower() not in full_text:
                discarded.append({"oracle_id": oracle_id, "reason": "quote not verbatim in oracle text",
                                   "axis": axis})
                continue

            # D-4 (D7 wiring): reject an activation-restriction-family label
            # under ANY lane -- SYNTH is banned from this closed, DET-owned
            # family regardless of how it labeled itself.
            if is_banned_restriction_family_label(label):
                banned_restriction_family_hits += 1
                anomalies.append({"oracle_id": oracle_id, "name": card["name"], "claimed_label": label,
                                   "claimed_lane": lane,
                                   "reason": "D-4: activation-restriction family is DET-owned; SYNTH-emitted "
                                             "instance rejected outright, not folded into free-lane clustering"})
                discarded.append({"oracle_id": oracle_id, "reason": "D-4 banned family", "axis": axis})
                continue

            resolved_slug = None
            new_grammar_instantiation = False
            if lane == "codebook":
                resolved_slug = resolve_codebook_label(label, active_slugs)
                if resolved_slug is not None:
                    codebook_hits += 1
                else:
                    anomalies.append({"oracle_id": oracle_id, "name": card["name"], "claimed_label": label,
                                       "reason": "lane=codebook but label did not resolve to an active codebook slug"})
            elif lane == "codebook-grammar":
                resolved_slug, validation = resolve_codebook_grammar_label(label, active_slugs)
                if resolved_slug is not None:
                    grammar_hits += 1
                    if resolved_slug not in active_slugs:
                        new_grammar_instantiation = True
                        grammar_new_instantiations += 1
                else:
                    # sec.11: "anything neither exact-codebook nor grammar-
                    # valid stays lane=free" -- downgrade, don't discard.
                    lane = "free"
                    anomalies.append({"oracle_id": oracle_id, "name": card["name"], "claimed_label": label,
                                       "reason": f"lane=codebook-grammar but validate_slug failed "
                                                 f"({validation['failures']}) -- downgraded to lane=free"})

            instances.append({
                "oracle_id": oracle_id, "name": card["name"], "lane": lane,
                "label": label, "definition": definition, "actor_scope": actor_scope,
                "quote": quote, "resolved_codebook_slug": resolved_slug,
                "new_grammar_instantiation": new_grammar_instantiation,
                # Label-only tokens, not label+definition: definitions share
                # enough generic connective prose that including them pulled
                # in false merges even after stopword-filtering (measured
                # live, see the STOPWORDS comment above). Labels are short,
                # intentional slugs -- a much cleaner clustering signal.
                "tokens": normalize_tokens(label),
            })

    n_rows = len(instances) + len(discarded) + refusals  # rows that got a message back (crude proxy, undercounts
                                                           # cards contributing 0 instances with no discards either)
    n_non_succeeded = sum(non_succeeded.values())
    if n_non_succeeded:
        total_rows = len(raw_results_path.read_text(encoding="utf-8").splitlines())
        rate = n_non_succeeded / total_rows if total_rows else 0
        print(f"non-succeeded batch rows: {n_non_succeeded}/{total_rows} ({rate:.1%}) -- {non_succeeded}")
        if rate > 0.02:
            fc.halt(f"{n_non_succeeded}/{total_rows} rows ({rate:.1%}) did not succeed -- this exceeds the "
                     f"2% single-row-hiccup tolerance and looks like a systemic API/infra problem, not an "
                     f"isolated transient error; investigate before consolidating")

    n_total = len(instances) + len(discarded) + refusals
    print(f"parsed {n_total} raw axis instance(s)/response(s) from {raw_results_path.name} "
          f"({parse_failures} card(s) had non-JSON output, {refusals} card(s) had a model refusal -- both excluded entirely)")
    print(f"evidence-quote-or-discard gate: kept {len(instances)}, discarded {len(discarded)} "
          f"({sum(1 for d in discarded if d['reason'] == 'quote not verbatim in oracle text')} bad quotes, "
          f"{sum(1 for d in discarded if d['reason'] == 'missing field')} missing a required field, "
          f"{sum(1 for d in discarded if d['reason'] == 'D-4 banned family')} D-4 banned-family rejections)")
    if active_slugs:
        print(f"three-lane: {codebook_hits} instance(s) resolved to an existing codebook axis, "
              f"{grammar_hits} instance(s) resolved via a ratified grammar family "
              f"({grammar_new_instantiations} newly-instantiated virtual node(s), sec.11), "
              f"{len(anomalies)} anomal(y/ies) total (lane=codebook unresolved, lane=codebook-grammar "
              f"validation failures folded into free-lane clustering, and D-4 banned-family rejections)")
        if banned_restriction_family_hits:
            print(f"D-4 enforcement: {banned_restriction_family_hits} SYNTH instance(s) claimed an "
                  f"activation-restriction-family slug -- rejected outright (that family is DET-owned)")
    return instances, discarded, anomalies


def cluster_instances(instances: list) -> list:
    """Exact normalized-token-set matching only -- NOT fuzzy/transitive
    similarity. A single-linkage Jaccard pass (measured live, both over
    label+definition tokens and over label-only tokens at several
    thresholds) reliably chained unrelated concepts together through shared
    generic tokens: "grants-indestructible" chained via "counter"/"scale"
    tokens through several intermediate labels all the way to
    "scales-with-tribal-count" and "scaling-mana-by-permanent-count" in one
    36-member cluster. Per the spec's own rule (T3-AXIS-FOUNDRY-v3.md
    guardrails: "halt loudly on axis-boundary ambiguity... never a silent
    merge or split"), a wrong automatic merge is worse than an
    under-merged pair Captain fixes with one MERGE INTO click in the review
    tool -- so this only ever groups instances whose normalized label
    token sets are IDENTICAL. Cards with an empty token set (fully
    stopworded label) never merge with each other.

    MIN_TOKENS_TO_MERGE guards a second false-merge shape measured live:
    aggressive stopwording (needed to fix the chaining above) can strip a
    label down to a single dominant word -- "enters-with-counters" and
    "triggers-on-counter-effect" both collapse to the bare token {count},
    exact-matching "counter-target-spell" even though +1/+1 counters and
    countering a spell are unrelated. A 1-token set is never distinctive
    enough to trust for merging."""
    MIN_TOKENS_TO_MERGE = 2
    groups = defaultdict(list)
    for inst in instances:
        if len(inst["tokens"]) >= MIN_TOKENS_TO_MERGE:
            key = inst["tokens"]
        else:
            key = (None, inst["oracle_id"], inst["label"])
        groups[key].append(inst)
    clusters = sorted(groups.values(), key=lambda g: -len(g))
    print(f"\nDET clustering (exact normalized-label-token-set match): {len(instances)} instances -> {len(clusters)} clusters")
    return clusters


def slugify(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"rule:{s}"


def build_consolidated_axes(batch_num: int, codebook_attached: dict, free_clusters: list,
                             active_slugs: dict, codebook_version: str) -> Path:
    """codebook_attached: {slug: [instance, ...]} for lane=codebook hits AND
    lane=codebook-grammar hits (D7 wiring). A grammar-composed slug not yet
    in active_slugs is a brand-new virtual-node instantiation
    (CODEBOOK-NAMING-GRAMMAR.md sec.11: "A virtual node instantiates the
    moment one quote-verified member arrives -- no fresh ratification") --
    tagged status="new_grammar_instantiation" (distinct from lane=codebook's
    "existing_codebook_axis" and free-lane's "new_candidate") so Captain can
    see at a glance which axes this batch is introducing via grammar
    composition versus reconfirming.
    free_clusters: output of cluster_instances() over the free-lane pool
    (lane="free", batch-1 legacy instances with no lane, lane=codebook
    anomalies, and lane=codebook-grammar validation failures downgraded to
    free). Clusters with >=2 distinct cards become NEW candidate axes;
    singletons go to other_lane. source="B-only" throughout -- everything
    here originates from Stage 1B SYNTH, whether or not it matched the
    codebook; Source A reconciliation is a full-corpus-pass step, not a
    per-batch one (T3-AXIS-FOUNDRY-v3.md 'After convergence')."""
    used_slugs = set(active_slugs.keys())
    axes = []
    other_lane = []

    for slug, insts in sorted(codebook_attached.items()):
        if slug in active_slugs:
            definition = active_slugs[slug]["definition"]
            scope = active_slugs[slug]["scope"]
            status = "existing_codebook_axis"
        else:
            # new_grammar_instantiation=True on every instance here (D7
            # wiring only ever populates codebook_attached with an
            # out-of-active_slugs slug via the grammar path).
            scope_counts = Counter(i["actor_scope"] for i in insts)
            scope = sorted(scope_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            rep = sorted(insts, key=lambda i: i["oracle_id"])[0]
            definition = rep["definition"]
            status = "new_grammar_instantiation"
            used_slugs.add(slug)
        axes.append({
            "slug": slug,
            "definition": definition,
            "scope": scope,
            "source": "B-only",
            "parameterized": False,
            "status": status,
            "members": [{"oracle_id": i["oracle_id"], "quote": i["quote"]} for i in insts],
        })

    single_card_clusters = 0
    for cluster in free_clusters:
        if len(cluster) < 2:
            inst = cluster[0]
            other_lane.append({
                "oracle_id": inst["oracle_id"], "label": inst["label"],
                "definition": inst["definition"], "quote": inst["quote"],
            })
            continue

        distinct_cards = {inst["oracle_id"] for inst in cluster}
        if len(distinct_cards) == 1:
            # Batch-2 finding (TRIAGE-BATCH-2.md section 0/7.1): the SYNTH model
            # can find two genuinely distinct functional axes on the SAME card
            # that happen to free-label identically -- that is not multi-card
            # corroboration, just one card's two abilities. Route every
            # instance to OTHER individually rather than promoting a fake
            # "2-member" candidate axis; flagged loudly, not silently dropped.
            single_card_clusters += 1
            for inst in cluster:
                other_lane.append({
                    "oracle_id": inst["oracle_id"], "label": inst["label"],
                    "definition": inst["definition"], "quote": inst["quote"],
                    "single_card_cluster_flag": True,
                })
            continue

        label_counts = Counter(inst["label"] for inst in cluster)
        top_label = sorted(label_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        # representative definition: from an instance carrying the top label,
        # deterministic tie-break by oracle_id
        rep = sorted((i for i in cluster if i["label"] == top_label), key=lambda i: i["oracle_id"])[0]

        slug = slugify(top_label)
        if slug in used_slugs:
            n = 2
            while f"{slug}-{n}" in used_slugs:
                n += 1
            slug = f"{slug}-{n}"
        used_slugs.add(slug)

        scope_counts = Counter(inst["actor_scope"] for inst in cluster)
        top_scope = sorted(scope_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

        axes.append({
            "slug": slug,
            "definition": rep["definition"],
            "scope": top_scope,
            "source": "B-only",
            "parameterized": False,
            "status": "new_candidate",
            "members": [{"oracle_id": i["oracle_id"], "quote": i["quote"]} for i in cluster],
        })

    consolidated = {
        "batch": batch_num,
        "codebook_version": codebook_version,
        "axes": axes,
        "other_lane": other_lane,
    }
    out_path = fc.batch_paths(batch_num)["consolidated"]
    fc.write_json(out_path, consolidated)
    n_existing = sum(1 for a in axes if a["status"] == "existing_codebook_axis")
    n_grammar_new = sum(1 for a in axes if a["status"] == "new_grammar_instantiation")
    n_new = sum(1 for a in axes if a["status"] == "new_candidate")
    print(f"\nconsolidated: {n_existing} existing-codebook-axis confirmation(s), "
          f"{n_grammar_new} new grammar-instantiated axis(es) (sec.11 virtual-node self-instantiation), "
          f"{n_new} new free-lane candidate axis(es) (all source=B-only), {len(other_lane)} other_lane rows")
    if single_card_clusters:
        print(f"single-card-cluster guard: {single_card_clusters} free-lane cluster(s) had n>=2 instances but "
              f"all traced to the SAME card -- routed to other_lane individually (flagged "
              f"single_card_cluster_flag=true) instead of promoted as a fake corroborated axis")
    print(f"wrote {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", type=int, required=True)
    args = parser.parse_args()
    batch_num = args.batch

    paths = fc.batch_paths(batch_num)
    cards, _ = fc.load_corpus()
    active_slugs = load_active_codebook_slugs()
    if active_slugs:
        cb = json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))
        codebook_version = cb["version"]
    else:
        codebook_version = "0.0"
    print(f"codebook: {len(active_slugs)} active axis(es), version {codebook_version}")

    instances, discarded, anomalies = load_raw_instances(cards, paths["raw_results"])

    codebook_attached = defaultdict(list)
    free_pool = []
    for inst in instances:
        if inst["resolved_codebook_slug"] is not None:
            codebook_attached[inst["resolved_codebook_slug"]].append(inst)
        else:
            free_pool.append(inst)

    clusters = cluster_instances(free_pool)
    multi = [c for c in clusters if len(c) >= 2]
    singles = [c for c in clusters if len(c) == 1]
    print(f"free-lane clusters with >=2 distinct cards: {len(multi)} (new candidate axes)")
    print(f"free-lane singleton clusters (1 card): {len(singles)} (-> OTHER lane)")

    print(f"\nTop 40 free-lane clusters by member count:")
    for c in clusters[:40]:
        labels_preview = Counter(inst["label"] for inst in c).most_common(3)
        print(f"  {len(c):>3}  labels: {labels_preview}")

    raw_clusters_out = paths["consolidate_clusters_raw"]
    fc.write_json(raw_clusters_out, {
        "n_instances": len(instances),
        "n_discarded": len(discarded),
        "n_codebook_attached": sum(len(v) for v in codebook_attached.values()),
        "n_anomalies": len(anomalies),
        "anomalies": anomalies,
        "n_free_clusters": len(clusters),
        "free_clusters": [
            [{"oracle_id": i["oracle_id"], "name": i["name"], "label": i["label"],
              "definition": i["definition"], "actor_scope": i["actor_scope"], "quote": i["quote"]}
             for i in c]
            for c in clusters
        ],
    })
    print(f"\nwrote {raw_clusters_out} for manual review pass")

    build_consolidated_axes(batch_num, codebook_attached, clusters, active_slugs, codebook_version)


if __name__ == "__main__":
    main()
