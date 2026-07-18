#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- bootstrap loop "Consolidate (DET + SUP)" step for
batch 1. Reads the Stage 1B SYNTH results (experiments/out/foundry/
stage1b_raw_results.jsonl), applies the evidence-quote-or-discard gate,
clusters raw free-form axis labels into codebook candidates (DET token-
similarity pass), and writes a consolidated-axes file in the shape
foundry_emit.py consumes. Batch 1 is free-form/open-coded (no codebook to
close-code against yet), so clustering is unsupervised.

Run: python3 experiments/foundry_consolidate.py
"""
import sys
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

RAW_RESULTS_PATH = fc.FOUNDRY_OUT_DIR / "stage1b_raw_results.jsonl"
BATCH_NUM = 1
CODEBOOK_VERSION = "0.1"

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


def load_raw_instances(cards: dict) -> tuple:
    """Returns (instances, discarded_count). Each instance carries
    oracle_id, name, label, definition, actor_scope, quote, and its
    normalized token set for clustering."""
    if not RAW_RESULTS_PATH.exists():
        fc.halt(f"{RAW_RESULTS_PATH} not found -- fetch batch results first")

    instances = []
    discarded = []
    parse_failures = 0
    for line in RAW_RESULTS_PATH.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        oracle_id = row["custom_id"]
        result = row["result"]
        if result["type"] != "succeeded":
            fc.halt(f"card {oracle_id}: batch result type {result['type']!r}, expected all rows to have "
                     f"succeeded (verified live before this script ran) -- unexpected state, investigate")
        card = cards.get(oracle_id)
        if card is None:
            fc.halt(f"card {oracle_id} from batch results not found in corpus")

        text = result["message"]["content"][0]["text"]
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
            if not (quote and label and definition and actor_scope):
                discarded.append({"oracle_id": oracle_id, "reason": "missing field", "axis": axis})
                continue
            if quote.lower() not in full_text:
                discarded.append({"oracle_id": oracle_id, "reason": "quote not verbatim in oracle text",
                                   "axis": axis})
                continue
            instances.append({
                "oracle_id": oracle_id, "name": card["name"], "label": label,
                "definition": definition, "actor_scope": actor_scope, "quote": quote,
                # Label-only tokens, not label+definition: definitions share
                # enough generic connective prose that including them pulled
                # in false merges even after stopword-filtering (measured
                # live, see the STOPWORDS comment above). Labels are short,
                # intentional slugs -- a much cleaner clustering signal.
                "tokens": normalize_tokens(label),
            })

    print(f"parsed {len(instances) + len(discarded)} raw axis instances from {RAW_RESULTS_PATH.name} "
          f"({parse_failures} card(s) had non-JSON output, excluded entirely)")
    print(f"evidence-quote-or-discard gate: kept {len(instances)}, discarded {len(discarded)} "
          f"({sum(1 for d in discarded if d['reason'] == 'quote not verbatim in oracle text')} bad quotes, "
          f"{sum(1 for d in discarded if d['reason'] == 'missing field')} missing a required field)")
    if discarded:
        sample = discarded[:5]
        for d in sample:
            print(f"  discarded example: {d['oracle_id']} -- {d['reason']} -- {json.dumps(d['axis'])[:150]}")
    return instances, discarded


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


def main():
    cards, _ = fc.load_corpus()
    instances, discarded = load_raw_instances(cards)
    clusters = cluster_instances(instances)

    multi = [c for c in clusters if len(c) >= 2]
    singles = [c for c in clusters if len(c) == 1]
    print(f"clusters with >=2 distinct cards: {len(multi)} (candidate axes)")
    print(f"singleton clusters (1 card): {len(singles)} (-> OTHER lane)")

    print(f"\nTop 40 clusters by member count:")
    for c in clusters[:40]:
        labels_preview = Counter(inst["label"] for inst in c).most_common(3)
        print(f"  {len(c):>3}  labels: {labels_preview}")

    out_path = fc.FOUNDRY_OUT_DIR / "consolidate_clusters_raw.json"
    fc.write_json(out_path, {
        "n_instances": len(instances),
        "n_discarded": len(discarded),
        "n_clusters": len(clusters),
        "clusters": [
            [{"oracle_id": i["oracle_id"], "name": i["name"], "label": i["label"],
              "definition": i["definition"], "actor_scope": i["actor_scope"], "quote": i["quote"]}
             for i in c]
            for c in clusters
        ],
    })
    print(f"\nwrote {out_path} for manual review pass")

    build_consolidated_axes(clusters)


def slugify(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"rule:{s}"


def build_consolidated_axes(clusters: list) -> Path:
    """Batch 1 is free-form/open-coded, so every candidate axis is B-only
    (Source A reconciliation is a full-corpus-pass step, not a per-batch
    one -- T3-AXIS-FOUNDRY-v3.md 'After convergence'). Clusters with >=2
    distinct cards become candidate axes; singletons go to other_lane."""
    used_slugs = set()
    axes = []
    other_lane = []
    for cluster in clusters:
        if len(cluster) < 2:
            inst = cluster[0]
            other_lane.append({
                "oracle_id": inst["oracle_id"], "label": inst["label"],
                "definition": inst["definition"], "quote": inst["quote"],
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
            "members": [{"oracle_id": i["oracle_id"], "quote": i["quote"]} for i in cluster],
        })

    consolidated = {
        "batch": BATCH_NUM,
        "codebook_version": CODEBOOK_VERSION,
        "axes": axes,
        "other_lane": other_lane,
    }
    out_path = fc.FOUNDRY_OUT_DIR / f"consolidated_batch{BATCH_NUM}.json"
    fc.write_json(out_path, consolidated)
    print(f"\nconsolidated: {len(axes)} candidate axes (all source=B-only), {len(other_lane)} other_lane rows")
    print(f"wrote {out_path}")
    return out_path


if __name__ == "__main__":
    main()
