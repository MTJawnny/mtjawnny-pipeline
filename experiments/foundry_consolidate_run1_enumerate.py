#!/usr/bin/env python3
"""SESSION 2b — ENUMERATE. The arithmetic, alone.

`docs/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md`. **ZERO API SPEND. ZERO MUTATION
of `codebook.json` or `grammars.json`.** This writes exactly one artifact —
`experiments/out/foundry/corpus_pass_run1_plan.json` — and makes NO decisions.
Every judgment was made and frozen in session 2a.

THE ONE RULE (directive §1): **anything 2a did not enumerate DOES NOT HAPPEN.**
On any case 2a's artifact does not resolve, HALT and name it. Do not infer, do
not default, do not "route the obvious way". A gap in 2a is a defect in 2a and
is fixed by re-running 2a, not by exercising judgment here. This session's whole
value is that it has none.

WHY IT RE-WALKS THE PARSED FILE, AND WHY THAT IS SAFE
-----------------------------------------------------
An A1 assertion needs a QUOTE per (slug, oracle_id). `classify_run1_instances`
returns `codebook_all_hits` / `grammar_all_hits` as `{slug: set(oracle_id)}` —
the quote is dropped on the floor. So the quote has to be recovered by walking
`corpus_pass_run1_parsed_final.json` again.

Re-implementing a classifier's walk is the single most common defect class in
this repo, so the walk is **not trusted on its own**: it applies the producer's
OWN gates (`full_oracle_text`, the evidence check, D-4, the lane split) and then
its reconstructed hit-sets are asserted **equal to the producer's** — every
slug, every oracle_id, both directions. Any divergence HALTS. The re-walk is
therefore only ever a quote lookup; `classify_run1_instances` stays the
authority on WHICH rows exist.

DEDUPE (directive §2). A (slug, oracle_id) appears EXACTLY ONCE — in
`member_additions` with its assertions listed, or once in `assertion_merges` if
the member already exists. Same-run duplicates are resolved by LOOKUP into 2a's
`same_run_duplicates` (its `winning_quote`), never by re-deciding: 2a froze the
collapse rule as "lane precedence then first-in-parse-order", and CDR-04's
"keep both quotes" is a PROPOSAL, not ratified — §1 binds.

    python3 experiments/foundry_consolidate_run1_enumerate.py
    python3 experiments/foundry_consolidate_run1_enumerate.py --output <path>
"""
import argparse
import contextlib
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                        # noqa: E402
import foundry_codebook as fcb                     # noqa: E402
import validate_slug                               # noqa: E402
import foundry_consolidate_run1 as run1            # noqa: E402
import foundry_consolidate_run1_classify as clf    # noqa: E402

CLASSIFICATION_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_classification.json"
OUT_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_plan.json"
SOURCE_REF = "run1"


# --------------------------------------------------------------------------
# preconditions (directive PRECONDITIONS — verify all, else HALT)
# --------------------------------------------------------------------------

def preconditions() -> dict:
    codebook = fcb.load_codebook(fcb.CODEBOOK_PATH)
    fcb.lint_or_halt(codebook, "codebook.json (read-only precondition)")
    live_sha = fcb.sha256_of(fcb.CODEBOOK_PATH)

    if not CLASSIFICATION_PATH.exists():
        fc.halt(f"{CLASSIFICATION_PATH} not found — 2b expands 2a's frozen "
                f"decisions and cannot invent them. Run session 2a first.")
    a2a = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
    a2a_sha = fcb.sha256_of(CLASSIFICATION_PATH)

    recorded = a2a.get("codebook_sha256_at_classification")
    if recorded != live_sha:
        fc.halt(
            f"the codebook has MOVED since 2a classified against it.\n"
            f"    2a classified against {recorded}\n"
            f"    live codebook is      {live_sha}\n"
            f"  Expanding a decision set made against a different state is the "
            f"failure this precondition exists to stop. Re-run 2a and re-approve.")

    blocking = a2a.get("blocking_decisions") or []
    if blocking:
        ids = ", ".join(b.get("id", "?") for b in blocking)
        fc.halt(f"2a still carries {len(blocking)} BLOCKING decision(s): {ids}. "
                f"2b cannot compute exact expected_counts while any is open.")

    # The A12 external re-audit outcome is RECORDED (verdict NO-GO-AS-WRITTEN,
    # docs/CDR-PROPOSALS.md rev 2 provenance line; SESSION-HANDOFF-2026-08-02
    # names that file as A12's record). Its findings were folded into the
    # ratified A-series (A3/CDR-03, A4/CDR-02, A5/CDR-08, A9/CDR-09, A11/CDR-01,
    # ADD-05/CDR-05) which is the law this session is governed by. Recorded, not
    # waived — the directive requires the former.
    return {"codebook": codebook, "live_sha": live_sha,
            "a2a": a2a, "a2a_sha": a2a_sha}


# --------------------------------------------------------------------------
# quote recovery — a lookup, cross-checked against the producer
# --------------------------------------------------------------------------

def build_quote_index(result: dict) -> dict:
    """(lane, slug, oracle_id) -> [quote, …] in parse order.

    Applies the producer's own gates so the reconstruction is the same walk,
    then `assert_matches_producer` proves it. Quotes are kept as a LIST because
    one card can emit the same axis twice in one run (44 such cases); which one
    wins is 2a's `same_run_duplicates`, never this function's choice.
    """
    cards, _, _ = fc.load_corpus_gated()
    per_card = json.loads(run1.PARSED_PATH.read_text(encoding="utf-8"))
    active, killed = result["active"], result["killed"]
    merged, renamed = result["merged"], result["renamed"]
    det_owned = result["det_owned"]

    quotes = defaultdict(list)
    for oid, instances in per_card.items():
        card = cards[oid]
        full_text = run1.full_oracle_text(card)
        for ax in instances:
            lane = ax.get("lane")
            label = (ax.get("label") or "").strip()
            definition = (ax.get("definition") or "").strip()
            actor_scope = (ax.get("actor_scope") or "").strip()
            quote = (ax.get("evidence_quote") or "").strip()

            if not (quote and label and definition and actor_scope):
                continue
            if quote.lower() not in full_text:
                continue
            bare = label[len("rule:"):] if label.startswith("rule:") else label
            prefixed = f"rule:{bare}"
            if bare in validate_slug.ACTIVATION_RESTRICTION_FAMILY:
                continue

            if lane == "codebook":
                if prefixed in det_owned or prefixed in killed:
                    continue
                if prefixed in merged or prefixed in renamed:
                    continue
                if prefixed in active:
                    quotes[("codebook", prefixed, oid)].append(quote)
                continue
            if lane == "codebook-grammar":
                v = validate_slug.validate_slug(
                    prefixed, definition=None, all_slugs=list(active.keys()))
                if not v["ok"]:
                    continue
                if prefixed in active:
                    quotes[("grammar", prefixed, oid)].append(quote)
                continue
    return quotes


def assert_matches_producer(quotes: dict, result: dict) -> None:
    """GUARD — the re-walk must reconstruct the producer's hit-sets EXACTLY.

    Without this the expander is a second, unverified classifier, and a silent
    divergence would put a real quote on the wrong row or drop a row entirely.
    Checked in BOTH directions, per lane.
    """
    for lane, key in (("codebook", "codebook_all_hits"), ("grammar", "grammar_all_hits")):
        mine = defaultdict(set)
        for (ln, slug, oid) in quotes:
            if ln == lane:
                mine[slug].add(oid)
        theirs = {s: set(v) for s, v in result[key].items()}
        if set(mine) != set(theirs):
            only_mine = sorted(set(mine) - set(theirs))[:5]
            only_theirs = sorted(set(theirs) - set(mine))[:5]
            fc.halt(f"{lane} lane: the quote re-walk disagrees with "
                    f"`{key}` on which SLUGS were hit.\n"
                    f"    only in the re-walk: {only_mine}\n"
                    f"    only in the producer: {only_theirs}")
        for slug in sorted(theirs):
            if mine[slug] != theirs[slug]:
                fc.halt(f"{lane} lane, {slug}: the quote re-walk disagrees with "
                        f"`{key}` on WHICH CARDS hit it "
                        f"({len(mine[slug])} vs {len(theirs[slug])}). The "
                        f"re-walk is not the producer's walk; refusing to "
                        f"attach quotes on a different partition.")


def winning_quote_index(a2a: dict) -> dict:
    """(slug, oracle_id) -> the quote 2a's collapse chose. LOOKUP ONLY."""
    return {(d["slug"], d["oracle_id"]): d["winning_quote"]
            for d in a2a.get("same_run_duplicates", [])}


def pick_quote(quotes: list, slug: str, oid: str, winners: dict) -> str:
    """One quote for one (slug, oracle_id), per the dedupe law.

    HALTS on a multi-emission pair 2a did not resolve — directive §1: a gap in
    2a is a defect in 2a, never something to break a tie over here.
    """
    if len(quotes) == 1:
        return quotes[0]
    key = (slug, oid)
    if key in winners:
        return winners[key]
    fc.halt(f"{slug} / {oid} emitted {len(quotes)} quotes in run 1 and 2a's "
            f"`same_run_duplicates` does not resolve it. 2b has no tie-break "
            f"and must not invent one (directive §1).")


# --------------------------------------------------------------------------
# expansion
# --------------------------------------------------------------------------

def expand(ctx: dict) -> dict:
    a2a = ctx["a2a"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result, discovery, exact_match, _near = clf.resolve_run1()
    cards = result["cards"]
    active = result["active"]

    quotes = build_quote_index(result)
    assert_matches_producer(quotes, result)
    winners = winning_quote_index(a2a)
    corpus_ref = fcb.corpus_ref_current()

    nodes = clf.classify_nodes(result)
    routing = clf.route_killed_slugs(result, cards)
    r5 = clf.classify_r5(exact_match, result)
    a15 = clf.classify_a15(discovery, result)[0]

    additions, merges = {}, {}     # (slug, oid) -> row

    def emit(slug, oid, quote, original_lane, effective_lane, promotion_reason,
             axis_exists: bool):
        key = (slug, oid)
        bucket = merges if axis_exists and oid in fcb.member_id_set(active[slug]) \
            else additions
        other = merges if bucket is additions else additions
        if key in other:
            fc.halt(f"dedupe law violated: {slug}/{oid} is routed to BOTH "
                    f"member_additions and assertion_merges.")
        assertion = fcb.build_assertion(
            "llm", SOURCE_REF, quote, corpus_ref, evidence_status="quoted",
            original_lane=original_lane, effective_lane=effective_lane,
            promotion_reason=promotion_reason)
        if key in bucket:
            bucket[key]["assertions"].append(assertion)
        else:
            bucket[key] = {"slug": slug, "oracle_id": oid,
                           "card_name": cards[oid]["name"],
                           "assertions": [assertion]}

    # 1. codebook + grammar lanes, against EXISTING active axes
    for lane, hits_key in (("codebook", "codebook_all_hits"),
                           ("grammar", "grammar_all_hits")):
        for slug, oids in sorted(result[hits_key].items()):
            for oid in sorted(oids):
                q = pick_quote(quotes[(lane, slug, oid)], slug, oid, winners)
                emit(slug, oid, q,
                     original_lane="codebook" if lane == "codebook" else "codebook-grammar",
                     effective_lane="codebook" if lane == "codebook" else "codebook-grammar",
                     promotion_reason=None, axis_exists=True)

    # 2. R5 — free-lane labels literally equal to an active slug
    for row in r5:
        emit(row["slug"], row["oracle_id"], row["quote"],
             original_lane=row["original_lane"], effective_lane=row["effective_lane"],
             promotion_reason=row["promotion_reason"], axis_exists=True)

    # 3. A15 — promoted clusters. Only rows 2a marked valid; anything else would
    #    be 2b deciding, and there are none once the block is clear.
    for row in a15:
        if not row["validate_slug_ok"]:
            fc.halt(f"A15 row {row['target_slug']}/{row['oracle_id']} is not "
                    f"validate_slug_ok. 2a should have blocked or discovered it.")
        slug = row["target_slug"]
        exists = slug in active
        if exists:
            emit(slug, row["oracle_id"], row["quote"], row["original_lane"],
                 row["effective_lane"], row["promotion_reason"], axis_exists=True)
        else:
            key = (slug, row["oracle_id"])
            a = fcb.build_assertion("llm", SOURCE_REF, row["quote"], corpus_ref,
                                    original_lane=row["original_lane"],
                                    effective_lane=row["effective_lane"],
                                    promotion_reason=row["promotion_reason"])
            if key in additions:
                additions[key]["assertions"].append(a)
            else:
                additions[key] = {"slug": slug, "oracle_id": row["oracle_id"],
                                  "card_name": cards[row["oracle_id"]]["name"],
                                  "assertions": [a]}

    # 4. new axes from 2a's `instantiate` nodes, and their member rows
    new_axes, node_member_rows = [], 0
    for n in nodes:
        if n["action"] != "instantiate":
            continue
        scope = max(sorted(n["scope_counts"]), key=lambda s: n["scope_counts"][s])
        new_axes.append({
            "slug": n["slug"], "definition": n["definition"], "scope": scope,
            "source": "B-only", "parameterized": False, "status": "active",
            "history_note": n["reason"],
        })
        for m in n["members"]:
            key = (n["slug"], m["oracle_id"])
            a = fcb.build_assertion("llm", SOURCE_REF, m["quote"], corpus_ref,
                                    original_lane="codebook-grammar",
                                    effective_lane="codebook-grammar",
                                    promotion_reason="grammar-valid new virtual node")
            if key in additions:
                additions[key]["assertions"].append(a)
            else:
                additions[key] = {"slug": n["slug"], "oracle_id": m["oracle_id"],
                                  "card_name": cards[m["oracle_id"]]["name"],
                                  "assertions": [a]}
            node_member_rows += 1

    return {
        "result": result, "additions": additions, "merges": merges,
        "new_axes": new_axes, "nodes": nodes, "routing": routing,
        "r5": r5, "a15": a15, "node_member_rows": node_member_rows,
        "corpus_ref": corpus_ref,
    }


# --------------------------------------------------------------------------
# gates (directive §3)
# --------------------------------------------------------------------------

def gate_counts(ex: dict, a2a: dict) -> None:
    """Every 2a `expected_counts` entry must match the expansion EXACTLY."""
    exp = a2a["expected_counts"]
    result = ex["result"]
    active = result["active"]

    cb_add = cb_merge = g_add = g_merge = 0
    for slug, oids in result["codebook_all_hits"].items():
        existing = fcb.member_id_set(active[slug])
        cb_add += len(oids - existing)
        cb_merge += len(oids & existing)
    for slug, oids in result["grammar_all_hits"].items():
        existing = fcb.member_id_set(active[slug])
        g_add += len(oids - existing)
        g_merge += len(oids & existing)

    got = {
        "codebook_lane_member_additions": cb_add,
        "codebook_lane_assertion_merges": cb_merge,
        "grammar_lane_member_additions": g_add,
        "grammar_lane_assertion_merges": g_merge,
        "r5_member_additions": sum(1 for r in ex["r5"] if r["disposition"] == "member-addition"),
        "r5_assertion_merges": sum(1 for r in ex["r5"] if r["disposition"] != "member-addition"),
        "a15_promoted_rows": sum(1 for r in ex["a15"] if r["validate_slug_ok"]),
        "new_axes_instantiated": len(ex["new_axes"]),
        "new_axis_member_rows": ex["node_member_rows"],
        "routing_rows": len(ex["routing"]),
    }
    bad = [(k, exp.get(k), v) for k, v in sorted(got.items()) if exp.get(k) != v]
    if bad:
        lines = "\n".join(f"    {k}: 2a says {a}, expansion gives {b}" for k, a, b in bad)
        fc.halt("the expansion does not reproduce 2a's expected_counts. This is "
                "the closed loop that makes an external audit of 2a meaningful:\n"
                + lines)
    return got


def gate_merge_collisions(ex: dict) -> None:
    """No (class, source_ref) pair may collide on merge — `merge_assertion`
    halts on duplicates and session 3 must not discover that mid-apply."""
    active = ex["result"]["active"]
    clashes = []
    for (slug, oid), row in sorted(ex["merges"].items()):
        member = fcb.member_by_id(active[slug], oid)
        if member is None:
            fc.halt(f"assertion_merges holds {slug}/{oid} but it is not a member.")
        for a in member.get("assertions", []):
            if a.get("class") == "llm" and a.get("source_ref") == SOURCE_REF:
                clashes.append(f"{slug}/{oid}")
                break
    if clashes:
        fc.halt(f"{len(clashes)} planned merge(s) would collide with an existing "
                f"(llm, {SOURCE_REF}) assertion, e.g. {clashes[:5]}. "
                f"`merge_assertion` halts on that, mid-apply, in session 3.")


def gate_every_row_has_an_axis(ex: dict) -> None:
    """Every planned row must land on an axis that will EXIST when session 3
    applies it — an active one, or one this plan instantiates.

    THIS GATE EXISTS BECAUSE ITS ABSENCE SHIPPED AN UNAPPLIABLE PLAN. A15's
    `instantiate` clusters name a target slug that is not yet an axis, and
    `expand()` step 3's else-branch builds their member rows without ever
    adding the axis to `new_axes` — 189 rows on 2 axes that the plan does not
    create. Nothing else caught it:

    * `gate_counts` compares `new_axes_instantiated` against 2a's expectation,
      and BOTH sides count only `classify_nodes` instantiations. A closed loop
      closed on a quantity that both sides compute the same wrong way proves
      the two computations agree, not that either is right.
    * `gate_merge_collisions` walks `merges` only; all 189 are additions.
    * `expected_final_counts` derives `axes_active_after` from
      `len(ex["new_axes"])`, so it inherits the omission and stays
      self-consistent.

    An axis record needs a definition and a scope, and 2a's
    `a15_cluster_summary` carries neither — so this halts rather than
    inventing them. Directive §1: a gap in 2a is a defect in 2a, fixed by
    ruling on it, never by exercising judgment here.
    """
    active = ex["result"]["active"]
    planned = {a["slug"] for a in ex["new_axes"]}
    orphans = Counter()
    for bucket in (ex["additions"], ex["merges"]):
        for (slug, _oid) in bucket:
            if slug not in active and slug not in planned:
                orphans[slug] += 1
    if orphans:
        lines = "\n".join(f"    {slug}: {n} row(s)"
                          for slug, n in sorted(orphans.items()))
        fc.halt(
            f"{sum(orphans.values())} planned row(s) target {len(orphans)} axis/axes "
            f"that neither exist nor are instantiated by this plan:\n{lines}\n"
            f"  These are A15 clusters 2a classified `instantiate`. An axis "
            f"record needs a definition and a scope; 2a's a15_cluster_summary "
            f"carries neither, and 2b has no judgment to supply them. The fix "
            f"is a ruling that authors the axis record, not a change here.")


def expected_final_counts(ex: dict) -> dict:
    """The exact post-apply numbers session 3 must match. No tolerances (A14)."""
    axes = ex["result"]["axes"]
    by_status = Counter(a.get("status") for a in axes.values())
    member_rows = sum(len(a.get("members") or []) for a in axes.values())
    assertion_rows = sum(len(m.get("assertions") or [])
                         for a in axes.values() for m in (a.get("members") or []))
    new_assertions = sum(len(r["assertions"]) for r in ex["additions"].values()) \
        + sum(len(r["assertions"]) for r in ex["merges"].values())
    return {
        "axes_by_status_before": dict(sorted(by_status.items())),
        "axes_active_after": by_status["active"] + len(ex["new_axes"]),
        "axes_total_after": len(axes) + len(ex["new_axes"]),
        "member_rows_before": member_rows,
        "member_rows_after": member_rows + len(ex["additions"]),
        "assertion_rows_before": assertion_rows,
        "assertion_rows_after": assertion_rows + new_assertions,
        "member_additions": len(ex["additions"]),
        "assertion_merges": len(ex["merges"]),
        "new_axes": len(ex["new_axes"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", default=str(OUT_PATH))
    args = ap.parse_args()

    ctx = preconditions()
    print(f"precondition: codebook sha256={ctx['live_sha'][:16]}… lint clean, "
          f"matches 2a's recorded state")
    print(f"precondition: 2a artifact sha256={ctx['a2a_sha'][:16]}…, "
          f"0 blocking decisions")

    ex = expand(ctx)
    got = gate_counts(ex, ctx["a2a"])
    gate_merge_collisions(ex)
    gate_every_row_has_an_axis(ex)

    overlap = set(ex["additions"]) & set(ex["merges"])
    if overlap:
        fc.halt(f"plan is not duplicate-free: {len(overlap)} (slug, oracle_id) "
                f"pairs appear in BOTH sections, e.g. {sorted(overlap)[:3]}")

    plan = {
        "schema": "foundry-consolidation-plan/1",
        "generated_by": "experiments/foundry_consolidate_run1_enumerate.py",
        "directive": "docs/CONSOLIDATION-2B-ENUMERATE-DIRECTIVE.md",
        "classification_sha256": ctx["a2a_sha"],
        "codebook_sha256_pre_state": ctx["live_sha"],
        "corpus_ref": ex["corpus_ref"],
        "inputs": ctx["a2a"]["inputs"],
        "expected_counts_from_2a": ctx["a2a"]["expected_counts"],
        "expansion_counts": got,
        "expected_final_counts": expected_final_counts(ex),
        "new_axes": sorted(ex["new_axes"], key=lambda a: a["slug"]),
        "member_additions": [ex["additions"][k] for k in sorted(ex["additions"])],
        "assertion_merges": [ex["merges"][k] for k in sorted(ex["merges"])],
        "routing": ex["routing"],
        "taxonomy": ctx["a2a"]["taxonomy_items"],
        "promotions": ctx["a2a"]["promotions"],
        "same_run_duplicates": ctx["a2a"]["same_run_duplicates"],
        "report_rows": ctx["a2a"]["report_rows"],
    }

    out = Path(args.output)
    fc.write_json(out, plan)
    sha = fcb.sha256_of(out)
    print(f"\nwrote {out}\n  sha256={sha}  size={out.stat().st_size:,}")

    fin = plan["expected_final_counts"]
    print(f"\nmember_additions {len(plan['member_additions']):,}  "
          f"assertion_merges {len(plan['assertion_merges']):,}  "
          f"new_axes {len(plan['new_axes'])}")
    print(f"member rows  {fin['member_rows_before']:,} -> {fin['member_rows_after']:,}")
    print(f"assertions   {fin['assertion_rows_before']:,} -> {fin['assertion_rows_after']:,}")
    print(f"active axes  {fin['axes_by_status_before']['active']} -> {fin['axes_active_after']}")
    print("\nSTOP. Session 3 (APPLY) runs only on Captain's explicit go naming "
          "this plan sha256.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
