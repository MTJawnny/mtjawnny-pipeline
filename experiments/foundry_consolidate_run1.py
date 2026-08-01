#!/usr/bin/env python3
"""CONSOLIDATION-RUN1-DIRECTIVE.md -- M=1 consolidation of the full-corpus
SYNTH run 1 output into codebook.json, under the lane-aware consensus
ruling (2026-08-01). ZERO API SPEND: pure local compute over the already-
fetched/parsed run-1 results.

Distinct from foundry_consolidate.py (the per-triage-batch pipeline,
batches 1-8): this script consumes the packed-run's already-merged
per-card structure (experiments/out/foundry/corpus_pass_run1_parsed_final.json,
{oracle_id: [{"lane","label","definition","actor_scope","evidence_quote"}]})
rather than raw JSONL batch rows, and its lane handling differs from the
per-batch pipeline in one load-bearing way directed by the consolidation
directive: free-lane output NEVER becomes new codebook.json axes here (no
clustering-into-new-candidate-axis promotion) -- it is UNIONED into a
discovery artifact for Captain review only (CONSOLIDATION-RUN1-DIRECTIVE.md
sec.4, "No ratification of free-lane discovery candidates into new axes").

Run: python3 experiments/foundry_consolidate_run1.py
"""
import sys
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import validate_slug  # noqa: E402
import foundry_consolidate as fcon  # noqa: E402

CODEBOOK_PATH = fc.FOUNDRY_OUT_DIR / "codebook.json"
GRAMMARS_PATH = REPO_ROOT / "docs" / "grammars.json"
PARSED_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_parsed_final.json"
DET_SYNTH_CHECK_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_det_synth_check.json"
DISCOVERY_OUT_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_discovery.json"
DRY_RUN_REPORT_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_consolidation_dry_run.json"


def load_full_codebook():
    cb = json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))
    axes = cb["axes"]
    active = {s: e for s, e in axes.items() if e.get("status") == "active"}
    killed = {s: e for s, e in axes.items() if e.get("status") == "killed"}
    merged = {s: e for s, e in axes.items() if e.get("status") == "merged"}
    renamed = {s: e for s, e in axes.items() if e.get("status") == "renamed"}
    det_owned = {s for s, e in axes.items() if e.get("source") == "DET"}
    return cb, axes, active, killed, merged, renamed, det_owned


def full_oracle_text(card: dict) -> str:
    faces = card.get("card_faces") or [card]
    return "\n".join((f.get("oracle_text") or "") for f in faces).lower()


def classify_run1_instances():
    cb, axes, active, killed, merged, renamed, det_owned = load_full_codebook()
    cards, _, _ = fc.load_corpus_gated()
    with open(PARSED_PATH) as f:
        per_card = json.load(f)

    print(f"codebook: {len(active)} active axes, {len(killed)} killed, {len(merged)} merged, "
          f"{len(renamed)} renamed, {len(det_owned)} DET-owned")
    print(f"run-1 input: {len(per_card)} cards")

    discarded_bad_quote = 0
    codebook_lane_raw_instances = 0           # total lane=codebook instances processed past D-4/evidence gate
    codebook_all_hits = defaultdict(set)      # slug -> set(oids resolving here this run, new+already-member)
    grammar_lane_raw_instances = 0
    grammar_all_hits = defaultdict(set)       # slug -> set(oids), for grammar hits on an EXISTING active axis
    grammar_new_virtual_nodes = defaultdict(lambda: {"members": [], "definition": None, "scope_counts": Counter()})
    grammar_downgrades = 0
    d4_rejections = 0
    killed_slug_codebook_hits = []            # (oracle_id, label) codebook-lane hits naming a killed slug
    merged_slug_codebook_hits = []
    unresolved_codebook_anomalies = []        # lane=codebook, label matches nothing at all
    det_owned_leak_hits = []                  # should be 0 -- structural check

    free_pool = []  # for discovery clustering

    for oid, instances in per_card.items():
        card = cards[oid]
        full_text = full_oracle_text(card)
        for ax in instances:
            lane = ax.get("lane")
            label = (ax.get("label") or "").strip()
            definition = (ax.get("definition") or "").strip()
            actor_scope = (ax.get("actor_scope") or "").strip()
            quote = (ax.get("evidence_quote") or "").strip()

            if not (quote and label and definition and actor_scope):
                discarded_bad_quote += 1
                continue
            if quote.lower() not in full_text:
                discarded_bad_quote += 1
                continue

            bare = label[len("rule:"):] if label.startswith("rule:") else label
            prefixed = f"rule:{bare}"

            # D-4: activation-restriction family banned under ANY lane
            if bare in validate_slug.ACTIVATION_RESTRICTION_FAMILY:
                d4_rejections += 1
                continue

            if lane == "codebook":
                codebook_lane_raw_instances += 1
                if prefixed in det_owned:
                    det_owned_leak_hits.append((oid, label))
                    continue
                if prefixed in active:
                    codebook_all_hits[prefixed].add(oid)
                elif prefixed in killed:
                    killed_slug_codebook_hits.append((oid, label))
                elif prefixed in merged:
                    merged_slug_codebook_hits.append((oid, label))
                elif prefixed in renamed:
                    # renamed axes: not active under the old slug, but also not a
                    # genuine anomaly the same way killed/merged are -- report
                    # separately alongside merged (routes the same way: report row,
                    # never silently written under the stale name).
                    merged_slug_codebook_hits.append((oid, label))
                else:
                    unresolved_codebook_anomalies.append((oid, label))
                    free_pool.append({"oracle_id": oid, "name": card["name"], "lane": "free",
                                       "label": label, "definition": definition,
                                       "actor_scope": actor_scope, "quote": quote})
                continue

            if lane == "codebook-grammar":
                grammar_lane_raw_instances += 1
                result = validate_slug.validate_slug(prefixed, definition=None, all_slugs=list(active.keys()))
                if not result["ok"]:
                    grammar_downgrades += 1
                    free_pool.append({"oracle_id": oid, "name": card["name"], "lane": "free",
                                       "label": label, "definition": definition,
                                       "actor_scope": actor_scope, "quote": quote})
                    continue
                if prefixed in active:
                    grammar_all_hits[prefixed].add(oid)
                else:
                    node = grammar_new_virtual_nodes[prefixed]
                    if oid not in {m["oracle_id"] for m in node["members"]}:
                        node["members"].append({"oracle_id": oid, "quote": quote})
                    node["definition"] = node["definition"] or definition
                    node["scope_counts"][actor_scope] += 1
                continue

            # lane == "free" (or anything else -- shouldn't happen, schema-enforced)
            free_pool.append({"oracle_id": oid, "name": card["name"], "lane": "free",
                               "label": label, "definition": definition,
                               "actor_scope": actor_scope, "quote": quote})

    return {
        "cb": cb, "axes": axes, "active": active, "killed": killed, "merged": merged,
        "renamed": renamed, "det_owned": det_owned, "cards": cards,
        "discarded_bad_quote": discarded_bad_quote,
        "codebook_lane_raw_instances": codebook_lane_raw_instances,
        "codebook_all_hits": codebook_all_hits,
        "grammar_lane_raw_instances": grammar_lane_raw_instances,
        "grammar_all_hits": grammar_all_hits,
        "grammar_new_virtual_nodes": grammar_new_virtual_nodes,
        "grammar_downgrades": grammar_downgrades,
        "d4_rejections": d4_rejections,
        "killed_slug_codebook_hits": killed_slug_codebook_hits,
        "merged_slug_codebook_hits": merged_slug_codebook_hits,
        "unresolved_codebook_anomalies": unresolved_codebook_anomalies,
        "det_owned_leak_hits": det_owned_leak_hits,
        "free_pool": free_pool,
    }


def build_discovery_artifact(result: dict) -> dict:
    free_pool = result["free_pool"]
    active = result["active"]
    killed = result["killed"]

    with open(DET_SYNTH_CHECK_PATH) as f:
        det_check = json.load(f)
    det_convergent_keys = {(row[0], row[3]) for row in det_check["soft_flags"]}  # (oracle_id, label)

    active_bare_canon = {fcon.canonicalize_label(s): s for s in active}
    killed_bare_canon = {}
    for s in killed:
        killed_bare_canon.setdefault(fcon.canonicalize_label(s), []).append(s)

    active_bare_literal = {s[len("rule:"):] for s in active}
    killed_bare_literal = {s[len("rule:"):] for s in killed}

    exact_match_reinvention = []     # literal string match to an active slug
    canon_near_miss = []             # canonical match only (not literal)
    killed_reinvention = []

    clusters = defaultdict(list)
    for inst in free_pool:
        bare = inst["label"][len("rule:"):] if inst["label"].startswith("rule:") else inst["label"]
        canon = fcon.canonicalize_label(inst["label"])
        inst["canonical_label"] = canon
        inst["det_convergent"] = (inst["oracle_id"], inst["label"]) in det_convergent_keys

        if bare in active_bare_literal:
            exact_match_reinvention.append(inst)
        elif canon in active_bare_canon:
            canon_near_miss.append(inst)

        if bare in killed_bare_literal or canon in killed_bare_canon:
            killed_reinvention.append(inst)

        clusters[canon].append(inst)

    cluster_rows = []
    for canon, insts in clusters.items():
        oids = sorted({i["oracle_id"] for i in insts})
        raw_variants = sorted({i["label"] for i in insts})
        names = sorted({i["name"] for i in insts})[:10]
        cluster_rows.append({
            "canonical_label": canon,
            "raw_variants": raw_variants,
            "member_oracle_id_count": len(oids),
            "df": len(oids),
            "sample_card_names": names,
            "det_convergent": any(i["det_convergent"] for i in insts),
            "killed_slug_reinvention": canon in killed_bare_canon or any(
                (i["label"][len("rule:"):] if i["label"].startswith("rule:") else i["label"]) in killed_bare_literal
                for i in insts),
        })
    cluster_rows.sort(key=lambda r: -r["df"])

    discovery = {
        "schema": "foundry-corpus-pass-run1-discovery/1",
        "n_free_lane_instances": len(free_pool),
        "n_clusters": len(cluster_rows),
        "clusters": cluster_rows,
        "exact_match_reinvention_count": len(exact_match_reinvention),
        "canon_near_miss_count": len(canon_near_miss),
        "killed_slug_reinvention_count": len({(i["oracle_id"], i["label"]) for i in killed_reinvention}),
        "det_convergent_count": sum(1 for i in free_pool if i["det_convergent"]),
    }
    return discovery, exact_match_reinvention, canon_near_miss


def main():
    result = classify_run1_instances()

    print(f"\n=== Discarded (evidence-quote-or-discard gate) ===")
    print(f"discarded (bad/missing quote or field): {result['discarded_bad_quote']}")
    print(f"D-4 (activation-restriction family) rejections: {result['d4_rejections']}")
    print(f"DET-owned slug leaked under lane=codebook (structural, should be 0): {len(result['det_owned_leak_hits'])}")
    if result["det_owned_leak_hits"]:
        print(f"  HALT-WORTHY: {result['det_owned_leak_hits'][:10]}")

    # New-vs-already-member split, computed via set difference against the
    # REAL current codebook (not inferred inside the loop -- avoids the
    # double-counting bug an in-loop check had: an in-loop "if oid already a
    # member" test doesn't dedupe against OTHER instances of the same
    # (slug, oid) pair seen earlier in this same run).
    codebook_new_by_slug = {}
    codebook_already_by_slug = {}
    for slug, oids in result["codebook_all_hits"].items():
        existing = set(result["active"][slug].get("member_oracle_ids", []))
        codebook_new_by_slug[slug] = oids - existing
        codebook_already_by_slug[slug] = oids & existing
    n_cb_axes = sum(1 for v in codebook_new_by_slug.values() if v)
    n_cb_new_instances = sum(len(v) for v in codebook_new_by_slug.values())
    n_cb_already = sum(len(v) for v in codebook_already_by_slug.values())
    n_cb_distinct_hits = sum(len(v) for v in result["codebook_all_hits"].values())

    print(f"\n=== Codebook lane ===")
    print(f"raw lane=codebook instances processed: {result['codebook_lane_raw_instances']} "
          f"(distinct card+slug pairs: {n_cb_distinct_hits} -- difference is same-card duplicate emissions)")
    print(f"axes receiving >=1 genuinely NEW member: {n_cb_axes}")
    print(f"total NEW (not already-member) card confirmations: {n_cb_new_instances}")
    print(f"card+slug pairs where the card was ALREADY a member (no-op confirmation): {n_cb_already}")
    print(f"killed-slug lane=codebook hits: {len(result['killed_slug_codebook_hits'])}")
    print(f"merged/renamed-slug lane=codebook hits: {len(result['merged_slug_codebook_hits'])}")
    print(f"unresolved lane=codebook anomalies (folded to free pool): {len(result['unresolved_codebook_anomalies'])}")

    grammar_new_by_slug = {}
    grammar_already_by_slug = {}
    for slug, oids in result["grammar_all_hits"].items():
        existing = set(result["active"][slug].get("member_oracle_ids", []))
        grammar_new_by_slug[slug] = oids - existing
        grammar_already_by_slug[slug] = oids & existing
    n_gram_new_instances = sum(len(v) for v in grammar_new_by_slug.values())
    n_gram_already = sum(len(v) for v in grammar_already_by_slug.values())

    print(f"\n=== Codebook-grammar lane ===")
    n_gram_existing_axes = len(result["grammar_all_hits"])
    n_gram_existing_instances = sum(len(v) for v in result["grammar_all_hits"].values())
    n_gram_new_nodes = len(result["grammar_new_virtual_nodes"])
    print(f"grammar hits resolving to an EXISTING active axis: {n_gram_existing_axes} axes, "
          f"{n_gram_existing_instances} distinct card+slug pairs "
          f"({n_gram_new_instances} genuinely new, {n_gram_already} already-member no-ops)")
    print(f"NEW virtual-node instantiations (grammar-valid, no existing axis): {n_gram_new_nodes}")
    for slug in sorted(result["grammar_new_virtual_nodes"]):
        n = len(result["grammar_new_virtual_nodes"][slug]["members"])
        print(f"  {slug}: {n} quote-verified member(s)")
    print(f"downgraded to free (validate_slug failed): {result['grammar_downgrades']}")

    discovery, exact_match, near_miss = build_discovery_artifact(result)
    print(f"\n=== Free lane / discovery ===")
    print(f"free-lane instances (incl. downgrades/anomalies folded in): {discovery['n_free_lane_instances']}")
    print(f"canonical clusters: {discovery['n_clusters']}")
    print(f"exact-match-to-active-slug reinvention (literal string match): {discovery['exact_match_reinvention_count']}")
    print(f"canonical-only near-miss to an active slug: {discovery['canon_near_miss_count']}")
    print(f"killed-slug reinvention: {discovery['killed_slug_reinvention_count']}")
    print(f"det-convergent flagged instances: {discovery['det_convergent_count']}")

    fc.write_json(DISCOVERY_OUT_PATH, discovery)
    print(f"\nwrote {DISCOVERY_OUT_PATH}")

    # --- Dry-run report: exactly what WOULD be written to codebook.json,
    # blocked pending the member-provenance schema ruling (no mutation here) ---
    dry_run = {
        "schema": "foundry-corpus-pass-run1-consolidation-dry-run/1",
        "BLOCKED": True,
        "block_reason": "codebook.json member_oracle_ids has no per-member provenance/tier field shape "
                         "(CONSOLIDATION-RUN1-DIRECTIVE.md sec.4: 'HALT and propose a shape -- do not "
                         "invent one silently'). This report shows what consolidation WOULD write once "
                         "Captain rules on the shape.",
        "codebook_lane_would_add": {slug: sorted(oids) for slug, oids in codebook_new_by_slug.items() if oids},
        "codebook_lane_axes_touched": n_cb_axes,
        "codebook_lane_new_member_instances": n_cb_new_instances,
        "grammar_lane_existing_axis_would_add": {slug: sorted(oids) for slug, oids in grammar_new_by_slug.items() if oids},
        "grammar_lane_new_virtual_nodes": {
            slug: {"member_count": len(v["members"]), "definition": v["definition"],
                   "scope": v["scope_counts"].most_common(1)[0][0] if v["scope_counts"] else None,
                   "members": v["members"]}
            for slug, v in result["grammar_new_virtual_nodes"].items()
        },
        "killed_slug_codebook_hits": [{"oracle_id": o, "label": l} for o, l in result["killed_slug_codebook_hits"]],
        "merged_or_renamed_slug_codebook_hits": [{"oracle_id": o, "label": l} for o, l in result["merged_slug_codebook_hits"]],
        "unresolved_codebook_anomalies": [{"oracle_id": o, "label": l} for o, l in result["unresolved_codebook_anomalies"]],
    }
    fc.write_json(DRY_RUN_REPORT_PATH, dry_run)
    print(f"wrote {DRY_RUN_REPORT_PATH} (BLOCKED -- dry-run only, no codebook.json mutation)")


if __name__ == "__main__":
    main()
