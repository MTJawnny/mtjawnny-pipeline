#!/usr/bin/env python3
"""Assembles docs/B-CONSOLIDATION-REAUDIT-PACKET.md -- the A12 external
re-audit checkpoint packet (CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md sec.3
step 2).

Generated, not hand-written (G4): it embeds session 2a's classification
artifact, so it must be reproducible from that artifact and regenerated
whenever 2a re-runs. Deterministic.

Run: python3 experiments/foundry_build_reaudit_packet.py
"""
import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

ARTIFACT_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_classification.json"
OUT_PATH = REPO_ROOT / "docs" / "B-CONSOLIDATION-REAUDIT-PACKET.md"
DIRECTIVE_2A = REPO_ROOT / "docs" / "CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md"
DIRECTIVE_2B = REPO_ROOT / "docs" / "CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md"


def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def build(artifact_path: Path, out_path: Path) -> str:
    art = json.loads(artifact_path.read_text(encoding="utf-8"))
    hs = art["human_summary"]
    ec = art["expected_counts"]
    L = []
    w = L.append

    w("# B-CONSOLIDATION RE-AUDIT PACKET — A12 external checkpoint (2026-08-01)")
    w("")
    w("## Part 0 — YOUR ROLE (read before everything else)")
    w("")
    w("You are an independent auditor. You have NO access to the repository —")
    w("everything you need is in this packet. Your job is to find what is wrong,")
    w("missing, or self-serving, not to validate it.")
    w("")
    w("**This is the ratified A12 checkpoint.** A multi-session arc is rewriting a")
    w("Magic: The Gathering card-tagging codebook. The session under review made")
    w("every consolidation DECISION and wrote them to one artifact; the next")
    w("session mechanically expands them into ~18,000 database rows, and the one")
    w("after that applies those rows. This is the last point at which a wrong")
    w("decision is cheap to fix.")
    w("")
    w("**Disclosure of a conflict you must weight:** every artifact here was")
    w("produced by an AI assistant (Claude, in Claude Code) — the classification,")
    w("the directives governing it, and this packet. The human operator")
    w("(\"Captain\") requires an outside check for exactly that reason. Treat every")
    w("decision below as a claim to test.")
    w("")
    w("**Second disclosure:** an earlier re-audit was run past Fable 5 — also a")
    w("Claude model, therefore same-family and weak against correlated blind")
    w("spots. It found a real 820-row arithmetic error and several gate weaknesses,")
    w("all since fixed. You are the different-family check that ruling A12 actually")
    w("requires.")
    w("")
    w("**What we want from you:**")
    w("1. **Rule on the blocking decision in Part 2.** It is a genuine")
    w("   contradiction between two ratified rules and it gates everything")
    w("   downstream.")
    w("2. Attack the 95-node classification (Part 4). Each node becomes a new")
    w("   permanent axis or does not. Are the two collision calls right?")
    w("3. Attack the promotions (Part 6). Free-lane model output is being promoted")
    w("   into curated membership. Is that sound, or lane-discipline laundering?")
    w("4. Attack the same-run collapse (Part 7): 44 cases where the model emitted")
    w("   the same tag twice for one card, collapsed by a ratified precedence rule.")
    w("   Is the rule right, and is discarding the loser's quote a loss of evidence?")
    w("5. What will hurt later — at apply time, at corroboration waves, at the")
    w("   future schema pass — that is cheap to fix now?")
    w("6. Anything the assistant should have surfaced and did not.")
    w("7. Rank by severity. Do not pad. If something is sound, one line and move on.")
    w("")
    w("**Output:** ranked findings (severity, claim, evidence from this packet,")
    w("recommended change), then a verdict: GO / GO-WITH-FIXES / NO-GO-AS-WRITTEN.")
    w("")

    w("## Part 1 — PRIMER (cold-start context)")
    w("")
    w("The Magic Thesaurus (mtjawnny.com) is a deterministic MTG card-similarity")
    w("engine over ~38,233 cards (32,557 after a legality gate). Tier 0–2")
    w("similarity is mature; Tier 3 — \"same job, different words\" — is the open")
    w("problem. The \"T3 axis foundry\" mines it.")
    w("")
    w("`codebook.json` holds ~455 axis records (`rule:enters-tapped`,")
    w("`rule:create-token-treasure`, …), each with a definition, a status")
    w("(active / killed / merged / renamed / deferred), and card membership.")
    w("Membership provenance is load-bearing and has three classes:")
    w("**rule-derived** (a ratified regex matched the oracle text; full weight),")
    w("**human** (Captain ratified it in batch triage; full weight), and **llm**")
    w("(a model proposed it; discounted, never gate-bearing).")
    w("")
    w("A full-corpus model pass (\"run 1\", M=1, 32,557 cards, $57.63 spent)")
    w("produced output in three lanes: `codebook` (matches an existing axis),")
    w("`codebook-grammar` (a valid composition under a ratified naming grammar),")
    w("and `free` (anything else — discovery only). None of it has been written")
    w("into the codebook yet. Doing so is the work being planned.")
    w("")
    w("House discipline: halt loudly on any unexpected shape, never guess, never")
    w("silently skip; evidence-quote-or-discard on every per-card assignment;")
    w("deterministic byte-identical regeneration; every constant is a ratified")
    w("ruling, not a tuning knob.")
    w("")

    w("## Part 2 — THE BLOCKING DECISION (rule on this first)")
    w("")
    if art.get("blocking_decisions"):
        for b in art["blocking_decisions"]:
            w(f"### {b['id']} — {b['rows_affected']} rows affected")
            w("")
            w(b["summary"])
            w("")
            w("Clusters affected:")
            w("")
            w("| cluster | target slug | rows | validator objection |")
            w("|---|---|---|---|")
            for c in b["clusters"]:
                detail = esc(" ".join(c["unknown_tokens_detail"]))[:160]
                w(f"| `{c['cluster']}` | `{c['target_slug']}` | {c['rows']} | {detail} |")
            w("")
            w("The contradiction, precisely: ruling **R6/A15** names these clusters")
            w("as PROMOTING into codebook membership. The same amendment says each")
            w("row must re-validate through the slug validator \"exactly like a")
            w("grammar-lane label\", and that rows failing validation fall back to")
            w("discovery. These two clusters fail — but only because their slug")
            w("contains a word outside the closed naming vocabulary. So the ratified")
            w("outcome and the ratified mechanism disagree.")
            w("")
            w("Options as the session recorded them:")
            w("")
            for o in b["options"]:
                w(f"- **Option {o['option']} — {o['action']}.** {o['consequence']}")
            w("")
            w(f"**The session's recommendation:** {b['recommendation']}")
            w("")
            w("Scrutinise this specifically. The assistant chose to BLOCK rather than")
            w("follow the fallback rule to the letter, on the grounds that silently")
            w("demoting 209 Captain-ratified promotions on a vocabulary technicality")
            w("is the failure mode the halt-loudly rule exists to prevent. That")
            w("reasoning is itself a judgment call, and it is the one most worth")
            w("challenging in this packet.")
            w("")
    else:
        w("None — the session reported no blocking decisions.")
        w("")

    w("## Part 3 — THE SCHEMA THE PLAN WRITES INTO (ratified amendment A1)")
    w("")
    w("Each axis's membership is a list of member objects; each member carries a")
    w("STACK of assertions, one per support event:")
    w("")
    w("```json")
    w(json.dumps({
        "oracle_id": "<uuid>", "tier": "provisional",
        "assertions": [
            {"class": "human", "source_ref": "batch-3", "quote": "...",
             "corpus_ref": "2026-07-18", "evidence_status": "quoted"},
            {"class": "llm", "source_ref": "run1", "original_lane": "free",
             "effective_lane": "codebook-grammar",
             "promotion_reason": "canonical-form-matches-ratified-grammar",
             "quote": "...", "corpus_ref": "2026-07-04", "evidence_status": "quoted"},
        ]}, indent=2))
    w("```")
    w("")
    w("Rules: one member record per (axis, oracle_id); assertions append-merge and")
    w("are never overwritten; a duplicate `(class, source_ref)` HALTS; member-level")
    w("`tier` is present **iff** every assertion is llm-class (any human or")
    w("rule-derived assertion means full weight, so a consensus tier is moot).")
    w("Deterministic order: members by oracle_id, assertions by (class, source_ref).")
    w("")
    w("The codebook was migrated to this shape in a prior session: 7,699 existing")
    w("rows backfilled with one assertion each (3,697 rule-derived, 4,002 human),")
    w("membership provably unchanged, independently verified.")
    w("")

    w("## Part 4 — THE 95-NODE CLASSIFICATION (AG-COUNT-01)")
    w("")
    w("Each of these is a grammar-valid composition the model proposed that has no")
    w("existing axis. Classifying one `instantiate` creates a new permanent axis.")
    w("")
    w("| category | count |")
    w("|---|---|")
    for k, v in hs["node_classification_table"].items():
        w(f"| {k} | {v} |")
    w("")
    w("The two collisions — the cases where a proposed node hits an axis that")
    w("already exists under a non-active status:")
    w("")
    for r in art["node_classification"]:
        if not r["category"].startswith("collision"):
            continue
        w(f"**`{r['slug']}`** — {r['category']}, action `{r['action']}`"
          + (f", target `{r['target']}`" if r["target"] else "") + f", {r['n_members']} member(s)")
        w("")
        w(f"> {r['reason']}")
        w("")
        for m in r["members"]:
            w(f"> - `{m['oracle_id']}` — evidence: {m['quote']!r}")
        w("")
    w("### All 93 instantiations — summary")
    w("")
    w("| slug | members | definition |")
    w("|---|---|---|")
    for r in art["node_classification"]:
        if r["action"] != "instantiate":
            continue
        w(f"| `{r['slug']}` | {r['n_members']} | {esc(r['definition'])[:150]} |")
    w("")
    w("### All 93 instantiations — full member evidence")
    w("")
    w("Every card that would join each new axis, with the oracle-text clause the")
    w("model cited. This is the evidence for whether the axis deserves to exist at")
    w("all: a node whose members do not share a mechanism is a bad axis regardless")
    w("of how well-formed its name is.")
    w("")
    for r in art["node_classification"]:
        if r["action"] != "instantiate":
            continue
        w(f"**`{r['slug']}`** ({r['n_members']} members) — {esc(r['definition'])[:220]}")
        w("")
        for m in r["members"]:
            w(f"- {m['quote']!r}")
        w("")

    w("## Part 5 — WHAT THE NEXT SESSION MUST REPRODUCE EXACTLY")
    w("")
    w("These counts are the closed loop: session 2b expands the decisions above")
    w("into full rows and must reproduce every number here or halt. This is what")
    w("makes auditing this artifact alone meaningful — a bug in the mechanical")
    w("expander is otherwise precisely what you cannot see from here.")
    w("")
    w("| count | value |")
    w("|---|---|")
    for k, v in ec.items():
        w(f"| {k} | {v} |")
    w("")

    w("## Part 6 — PROMOTIONS")
    w("")
    w("Free-lane model output being promoted into curated membership. This is the")
    w("judgment most worth attacking: the lane system exists to keep unreviewed")
    w("model output out of the codebook, and these rulings carve exceptions.")
    w("")
    w("### R5 — free-lane labels literally equal to an existing active axis")
    w("")
    w(f"{hs['r5_split']['member_additions']} become new members; "
      f"{hs['r5_split']['assertion_merges']} are cards already on the axis, so they")
    w("merge as an additional llm assertion onto an existing member.")
    w("")
    w("| slug | card | disposition | evidence quote |")
    w("|---|---|---|---|")
    for r in art["promotions"]["r5_exact_match"]:
        w(f"| `{r['slug']}` | {esc(r['card_name'])} | {r['disposition']} | {esc(r['quote'])[:110]} |")
    w("")
    w("### A15 — free-lane clusters whose canonical form matches a ratified grammar")
    w("")
    w("| cluster | target slug | rows | disposition | validator |")
    w("|---|---|---|---|---|")
    for c in art["promotions"]["a15_cluster_summary"]:
        w(f"| `{c['cluster']}` | `{c['target_slug']}` | {c['rows']} | {c['disposition']} | "
          f"{'ok' if c['validate_slug_ok'] else ', '.join(c['validate_slug_failures'])} |")
    w("")
    w("Per-row detail for the clusters that PASSED validation:")
    w("")
    w("| target slug | card | raw model label | evidence quote |")
    w("|---|---|---|---|")
    for r in art["promotions"]["a15_grammar_canonical"]:
        if r["validate_slug_ok"]:
            w(f"| `{r['target_slug']}` | {esc(r['card_name'])} | `{esc(r['raw_label'])}` | "
              f"{esc(r['quote'])[:110]} |")
    w("")
    w("Per-row detail for the BLOCKED clusters (the Part 2 decision). Included in")
    w("full rather than sampled, so the ruling is not made on a curated excerpt:")
    w("")
    w("| target slug | card | raw model label | evidence quote |")
    w("|---|---|---|---|")
    for r in art["promotions"]["a15_grammar_canonical"]:
        if r["disposition"] == "blocked-pending-vocabulary-ratification":
            w(f"| `{r['target_slug']}` | {esc(r['card_name'])} | `{esc(r['raw_label'])}` | "
              f"{esc(r['quote'])[:110]} |")
    w("")

    w("## Part 7 — SAME-RUN DUPLICATE COLLAPSE")
    w("")
    w(f"The model emitted the same (card, label) more than once in "
      f"{hs['same_run_duplicates']['total']} cases; "
      f"{hs['same_run_duplicates']['with_differing_quotes']} of those carry DIFFERENT")
    w("evidence quotes across the emissions. The schema cannot hold two assertions")
    w("with the same (class, source_ref) — it halts — so a collapse rule was")
    w("ratified: collapse to one assertion, lane precedence")
    w("`codebook` > `codebook-grammar` > free-promoted, quote tie-break = first in")
    w("deterministic parse order.")
    w("")
    w("| card | slug | emissions | lanes | winning lane | quotes differ |")
    w("|---|---|---|---|---|---|")
    for d in art["same_run_duplicates"]:
        w(f"| {esc(d['card_name'])} | `{d['slug']}` | {d['n_emissions']} | "
          f"{'+'.join(d['lanes'])} | {d['winning_lane']} | {d['quotes_differ']} |")
    w("")

    w("## Part 8 — ROUTING, TAXONOMY, AND REPORT ROWS")
    w("")
    w("### Killed/merged/renamed-slug routing (closed action vocabulary)")
    w("")
    w("| card | slug | status | action | reason |")
    w("|---|---|---|---|---|")
    for r in art["killed_slug_routing"]["rows"]:
        w(f"| {esc(r['card_name'])} | `{r['slug']}` | {r['slug_status']} | {r['action']} | "
          f"{esc(r['reason'])[:170]} |")
    w("")
    w("### Taxonomy items")
    w("")
    for kind, rows in art["taxonomy_items"].items():
        w(f"**{kind}**")
        w("")
        for r in rows:
            head = r.get("slug") or f"{r.get('from_slug')} → {r.get('to_slug')}"
            w(f"- `{head}` — {esc(r.get('reason') or r.get('corrected_reason') or r.get('note'))[:220]}")
        w("")
    w("### Report rows (deferred to Captain, no action planned)")
    w("")
    for r in art["report_rows"]:
        w(f"- **{r['kind']}** — {esc(r['reason'])[:400]}")
    w("")

    w("## Part 9 — RATIFIED CONSTRAINTS (prior rulings, not open questions)")
    w("")
    w("Flag it if a decision above violates one of these.")
    w("")
    w("- **A2** — a revived axis enters `deferred`, never active-at-n=0.")
    w("- **A5** — class = who made the PER-CARD judgment. Bulk transformation of")
    w("  model output is `llm` even when the RULE was Captain-ratified.")
    w("- **A6** — the token→created-tokens synonym is a WHOLE-SLUG alias, not a")
    w("  global token map (a global map would corrupt 28 active slugs).")
    w("- **A8** — a rule-derived refresh replaces only its own assertions and")
    w("  never touches a human or llm assertion on the same member.")
    w("- **A11** — members hold DIRECT assertions only; parent rollups stay")
    w("  derived views.")
    w("- **A14** — killed-slug routing is a closed data vocabulary with every")
    w("  instance enumerated; no runtime \"does the quote fit\" judgment. No drift")
    w("  tolerances: exact match or halt. Evidence quotes never printed to console.")
    w("- **R7** — faceted keyword-grant axes (scope / delivery / context) are")
    w("  legitimate; only BARE grant axes are engine-redundant.")
    w("- **R9** — vocabulary additions are ratified like any other constant:")
    w("  proposed with evidence in the consolidation session, applied on approval.")
    w("- **R12 superseded by A1** — run-1 confirmations of cards already on an")
    w("  axis were originally to be discarded as no-ops; they now merge as llm")
    w("  assertions instead. This reversal is deliberate and worth checking.")
    w("")

    w("## Part 10 — THE GOVERNING DIRECTIVE (verbatim)")
    w("")
    w("<!-- BEGIN VERBATIM 2A -->")
    w(DIRECTIVE_2A.read_text(encoding="utf-8").rstrip())
    w("<!-- END VERBATIM 2A -->")
    w("")
    w("---")
    w("")
    w(f"Artifact under review: `corpus_pass_run1_classification.json`, sha256")
    w(f"`{fcb.sha256_of(ARTIFACT_PATH)}`.")
    w(f"Codebook state at classification: sha256")
    w(f"`{art['codebook_sha256_at_classification']}`.")

    text = "\n".join(L) + "\n"
    out_path.write_text(text, encoding="utf-8")
    return text


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artifact", default=str(ARTIFACT_PATH))
    p.add_argument("--output", default=str(OUT_PATH))
    a = p.parse_args()
    text = build(Path(a.artifact), Path(a.output))
    print(f"wrote {a.output}")
    print(f"  {len(text):,} B  (~{len(text)//4:,} tokens)")


if __name__ == "__main__":
    main()
