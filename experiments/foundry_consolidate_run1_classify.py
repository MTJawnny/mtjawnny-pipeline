#!/usr/bin/env python3
"""CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md -- session 2a: every consolidation
DECISION, and nothing mechanical. ZERO MUTATION, ZERO API SPEND.

Writes experiments/out/foundry/corpus_pass_run1_classification.json
(foundry-consolidation-classification/1) and stops. codebook.json and
grammars.json are opened READ-ONLY and never written.

Why this session exists apart from 2b: the full consolidation plan enumerates
~18,346 rows carrying quoted assertions (~7.8 MB / ~1.95M tokens) and cannot
be externally audited at any meaningful sampling rate. The decisions inside it
are ~1,000 rows and fit in one packet whole. So the judgment is extracted,
audited and frozen here; 2b expands it mechanically afterwards against
`expected_counts`, which is the closed loop that makes auditing this artifact
alone worth something.

Everything is recomputed from run-1 output through the committed producer
(foundry_consolidate_run1.classify_run1_instances) -- the dry-run report is
reference only and is never trusted. Deterministic: sorted iteration
throughout, fixed key order, no set-iteration-order dependence.

Run: python3 experiments/foundry_consolidate_run1_classify.py [--output PATH]
"""
import io
import sys
import json
import argparse
import contextlib
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402
import foundry_consolidate as fcon  # noqa: E402
import foundry_consolidate_run1 as run1  # noqa: E402
import validate_slug  # noqa: E402

OUT_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_classification.json"
PARSED_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_parsed_final.json"
GRAMMARS_PATH = REPO_ROOT / "docs" / "grammars.json"

EXPECTED_NODE_TOTAL = 92
# RE-DERIVED 2026-08-09 (was 95). The guard HALTED rather than letting a moved
# premise through, which is it working -- the number is stale, not wrong, and
# every one of the three is accounted for. Same discipline as a ratchet
# re-pin: movement is accepted only with the reason recorded.
#
# FOUR nodes left the set, all for the same correct reason: they are now REAL
# ACTIVE AXES, instantiated by the 44-axis re-home earlier on 2026-08-09, so
# they are no longer "new virtual nodes":
#   rule:create-token-clue                 active, 34 members
#   rule:etb-create-token-clue             active, 35 members
#   rule:death-trigger-create-token-clue   active,  5 members
#   rule:activated-create-token-creature   active,  1 member
# ONE node joined: rule:cant-be-blocked-except-by-count, which now VALIDATES
# because grammar §13 Q8.5's closed restriction vocabulary is parsed rather
# than transcribed (A15-VOCAB-01 half 1). 95 - 4 + 1 = 92.
#
# ISOLATED, not assumed. Against the verified pre-rename backup the count is
# also 92, so the rename is not the cause; against the pre-fix validator it is
# 91, so the +1 is exactly the vocabulary fix. The -4 predates this session
# entirely.
#
# A14 measured 95 - 2 collisions = 93. That count was computed with a
# STRING existence test, which cannot see that a proposed node is an
# existing axis spelled differently. Testing on canonical form (F-D fix,
# 2026-08-02) removes three more:
#   rule:targeted-damage-creature      -> live rule:targeted-creature-damage
#   rule:targeted-damage-player        -> live rule:targeted-player-damage
#   rule:grants-flying-target-static   -> sibling node -static-target
# So 93 -> 90 clean instantiations, 3 reclassified as join-existing /
# collision-node-duplicate. No node is lost; membership routes to the axis
# that already exists.
# RE-DERIVED 2026-08-09 (was 90), by the SAME four-out/one-in accounting as
# EXPECTED_NODE_TOTAL above: 90 - 4 + 1 = 87. Every other node category is
# unchanged -- join-existing 2, collision-killed 1, collision-renamed 1,
# collision-node-duplicate 1 -- so the whole movement is in this bucket and
# 87 + 2 + 1 + 1 + 1 = 92 closes against the total.
EXPECTED_CLEAN_NODES = 87          # was A14's 93, minus 3 canonical duplicates, minus the 4 now-live axes, plus the except node
# RE-DERIVED 2026-08-09 (was 213) — and this one is NOT a drift. 213 NEVER
# REPRODUCED, from its own recorded inputs, by its own producer.
#
# The classification artifact records the sha256 of all four inputs. Two are
# byte-identical today (`corpus_pass_run1_parsed_final.json`,
# `..._det_synth_check.json`), and the other two are recoverable —
# codebook `61af1a1d` is a kept backup, grammars `9214e67b` is commit 0f6fbdf.
# Replayed at that EXACT state, with the producer checked out at BOTH cfc26fa
# (which wrote the artifact) and f09fe73 (whose message asserts "A15 (213)
# unchanged"):
#
#     A15 = 194        every time, on every combination
#     R5  = 141        every time — the recorded value, EXACTLY
#
# **R5 reproducing to the row is what makes this trustworthy**: the replay
# harness is provably faithful, so A15's 19-row gap is a property of the
# artifact, not of the replay. `foundry_consolidate_run1` reads exactly those
# four paths and no others, so there is no fifth input to blame.
#
# The whole gap is ONE cluster: `cant-be-blocked-except-by-count` is recorded
# at **21 rows** and reproduces at **2**. 188 + 2 + 2 + 1 + 1 = 194.
#
# CONSEQUENCES, because other documents reason from the unreproducible number:
#   * A15-VOCAB-01's headline "209 rows blocked" reproduces as **190** (188+2).
#   * CDR-02 reasons at length about "the A15 21-row cluster … DET captures
#     only 5 of its 21 rows — the cluster is a grab bag". That analysis rests
#     on 21 rows that do not reproduce.
# Neither changes this session's ruling — the `destruction`/`except` questions
# are decided by the GRAMMAR, not by cluster size — but both are recorded in
# docs/A15-VOCAB-01-RULING-2026-08-09.md §9 rather than silently overwritten.
EXPECTED_A15_ROWS = 194            # A15 / R6 — reproducible value; see above
# RE-DERIVED 2026-08-09 (was 141). ATTRIBUTED ROW BY ROW, not accepted --
# `experiments/foundry_r5_attribution.py` replays classify_r5 against every
# codebook backup in tz-normalized chronological order and names the rows that
# enter and leave at each step. The whole 141 -> 163 is eight ratified codebook
# mutations, and every delta closes:
#
#   08-02 01:51  141   CDR-03's measured value reproduces exactly
#   08-02 17:29  140   -1  cdr09 rename walk drops draw-trigger-self-counter-growth
#   08-02 18:40  141   +1  lifegain-scales-with-target-color-count instantiated
#   08-02 19:46  157  +16  THE TIER-3 PACKET -- rule:etb-surveil (15) + one more
#   08-02 23:14  158   +1  prevents-damage-to-controller
#   08-03 15:19  159   +1  rule:cycling
#   08-09 13:49  156   -3  etb-bounce-own-land, grants-cascade-to-own-spells RENAMED
#   08-09 14:48  166  +10  the 44-axis --wide re-home (attack-trigger-scry etc.)
#   LIVE         163   -3  this session's targeted-destruction -> -destroy rename
#
# EVERY ENTERING ROW IS A CORRECT PROMOTION, verified rather than assumed: a
# row enters R5 when a run-1 FREE-LANE label comes to equal an ACTIVE slug,
# i.e. the codebook grew an axis under a name run-1 had already proposed.
# `rule:etb-surveil` was ABSENT on 2026-08-02 and is active now; all 15 of its
# cards print "When this ... enters, surveil N". Every LEAVING row left because
# its axis was renamed, so the label no longer names an active slug.
#
# THE REAL DEFECT IS THE GUARD, NOT THE DATA. This number is a pure function of
# WHICH SLUGS ARE ACTIVE -- a thing the project mutates deliberately and often.
# CDR-03 measured 141 at ~13:23 on 2026-08-02 and the tier-3 packet added 16 at
# ~19:45 THE SAME DAY, so the constant was stale within six hours and eight
# mutations have landed since. Pinned as a literal it is a guaranteed false
# alarm after every ratified mutation. See the ruling doc §9 for the durable
# fix (pin it against the codebook sha the classification already records, so a
# mismatch reads "the codebook moved, re-ratify" rather than "STOP, unknown").
EXPECTED_R5_ROWS = 163             # R5

NODE_CATEGORIES = ("instantiate", "join-existing", "redirect", "report-only",
                   "collision-killed", "collision-renamed",
                   "collision-node-duplicate")
ROUTING_ACTIONS = ("redirect", "split", "report", "discovery", "reject")


def build_canonical_axis_index(axes: dict) -> dict:
    """canonical form -> the slug that owns it, preferring the ACTIVE axis.

    Existence must be tested on CANONICAL form, not on the slug string.
    `rule:targeted-damage-creature` and `rule:targeted-creature-damage` are
    one axis spelled two ways; a string test says "no such axis" and
    instantiates a twin. That is finding F-D, and it would have created two
    duplicate axes out of the 93 proposed nodes.

    A rename or merge leaves a shell whose old slug canonicalises the same
    as its target — 16 such pairs live today — so a bare canonical lookup is
    ambiguous. Resolution: the ACTIVE member of a canonical group owns it.
    Two ACTIVE axes sharing a canonical form is a genuine ambiguity that 2a
    is not entitled to resolve, so it halts (currently zero such cases).
    """
    groups = defaultdict(list)
    for slug, entry in sorted(axes.items()):
        groups[fcon.canonicalize_label(slug)].append((slug, entry.get("status")))

    index = {}
    for canon, members in sorted(groups.items()):
        live = sorted(s for s, st in members if st == "active")
        if len(live) > 1:
            fc.halt(
                f"two ACTIVE axes share the canonical form {canon!r}: "
                f"{live!r}. They are the same axis spelled two ways; 2a "
                f"cannot pick a winner. Resolve by ruling (merge or rename), "
                f"then re-run."
            )
        index[canon] = live[0] if live else sorted(s for s, _ in members)[0]
    return index

# The five free-lane clusters A15 promotes, named as the ratification prose
# names them. They are resolved to canonical form through the SAME
# canonicalizer the discovery artifact used rather than by matching the prose
# strings literally -- the canonicalizer sorts and stems tokens, so
# "targeted-destruction-creature" is stored as "creature-targeted-destruc".
# Looking them up any other way would be guesswork.
A15_CLUSTER_NAMES = (
    "targeted-destruction-creature",
    "cant-be-blocked-except-by-count",
    "etb-create-token-blood",
    "etb-create-token-clue",
    "activated-tap-opponent-artifact",
)

# A15-VOCAB-01 option B (Captain-ratified 2026-08-09,
# docs/A15-VOCAB-01-RULING-2026-08-09.md): "rename the target slugs to
# compositions using existing ratified vocabulary, then re-validate."
#
# THE CLUSTER NAME AND THE TARGET SLUG ARE TWO DIFFERENT THINGS, and conflating
# them is what makes this look like a one-word edit. The cluster name is an
# IDENTITY in run-1's free pool -- `canonicalize_label` turns it into the key
# the rows are looked up under, and those rows carry the model's own 2026-08-01
# spelling. Renaming the tuple entry would change the LOOKUP as well as the
# target, find no rows, and trip the halt-guard below. That guard is correct;
# the fix is to leave identity alone and redirect only what gets created.
#
# Only clusters whose ratified name violates the grammar appear here. Everything
# else keeps `rule:<cluster>` as before.
A15_TARGET_SLUG_OVERRIDE = {
    # grammar §4 ratifies `destroy`; `destruction` appears nowhere in §4 and
    # CR 701.8 files the keyword action as Destroy. Completes the
    # `destruction` -> `destroy` retirement executed 2026-08-02 on
    # `mass-creature-destruction` (grammar §6c line 838) and finished on
    # `rule:targeted-destruction` -> `rule:targeted-destroy` on 2026-08-09.
    "targeted-destruction-creature": "rule:targeted-destroy-creature",
}

# R8 revivals. A2: a revived axis enters `deferred`, never active-at-n=0; it
# flips to active when its ratified DET pattern lands its first membership
# (session 4).
R8_REVIVALS = {
    "rule:grants-team-trample":
        "R8.1: scope-faceted keyword grant, legitimate per R7/A7 (the analogue "
        "rule:grants-haste-to-your-creatures is active and DET-owned). Revival law applies; "
        "enters deferred per A2 pending its DET pattern (session 4).",
    "rule:grants-haste-to-reanimated-creature":
        "R8.2: delivery-context grant, legitimate per R7/A7 (the analogue "
        "rule:grants-haste-to-created-tokens is active and DET-owned at n=102). Enters "
        "deferred per A2 pending its DET pattern (session 4).",
}

# R8.4 / R8.5: kill notes that state the wrong reason. The axes STAY killed;
# only the recorded reason changes.
R8_KILL_NOTE_CORRECTIONS = {
    "rule:sacrifice-self-as-activation-cost":
        "duplicate-of-live-axis (rule:activated-ability-costs-self-sacrifice)",
    "rule:sacrifice-as-additional-cost":
        "duplicate-of-live-axis (rule:additional-cost-sacrifice-permanent)",
    "rule:grants-haste-to-token":
        "duplicate of rule:grants-haste-to-created-tokens",
}

# A6: a WHOLE-SLUG alias in the routing artifact. Explicitly NOT a global
# token -> created-tokens synonym, which would corrupt the 28 active slugs
# carrying the bare token `token`.
A6_WHOLE_SLUG_ALIAS = {
    "rule:grants-haste-to-token": "rule:grants-haste-to-created-tokens",
}

# Lane precedence for the Captain-ratified same-run collapse rule.
LANE_PRECEDENCE = {"codebook": 0, "codebook-grammar": 1, "free": 2}

# Killed/merged/renamed-slug routing, decided PER SLUG by name (A14/H-02).
# An earlier draft of this file inferred the route by substring-matching the
# recorded kill note for "mechanism"/"ledger" -- which is exactly the runtime
# "does this fit" predicate A14 forbids, and it misfired immediately:
# rule:activated-regenerate-self's kill note contains the phrase "broad
# mechanism shape" in an unrelated clause and was routed to discovery on that
# accident. Every route is now written down.
KILLED_SLUG_ROUTES = {
    "rule:venture-into-dungeon": {
        "action": "discovery",
        "target": None,
        "reason": ("R10 mechanism/keyword kill -> discovery + ledger flag. Killed at batch 2 as "
                   "'Venture into the Dungeon keyword mechanism, ledger candidate'; the mechanism "
                   "has no axis home and the ledger is where it is tracked."),
    },
    "rule:activated-regenerate-self": {
        "action": "report",
        "target": None,
        "reason": ("R8.3 ratified that this axis is being AUTHORED properly via the DET path, with "
                   "a drafted pattern and a fixed-seed sample sheet, going live only on Captain's "
                   "pattern ratification in session 4. Routing this hit now would pre-empt that "
                   "ratification; regeneration currently has no active home, so it is a report row "
                   "until session 4 gives it one."),
    },
}


def resolve_run1() -> tuple:
    """Recompute run-1 classification through the committed producer."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = run1.classify_run1_instances()
        discovery, exact_match, near_miss = run1.build_discovery_artifact(result)
    return result, discovery, exact_match, near_miss


# --------------------------------------------------------------------------
# 1. node classification (AG-COUNT-01)
# --------------------------------------------------------------------------

def classify_nodes(result: dict) -> list:
    axes = result["axes"]
    nodes = result["grammar_new_virtual_nodes"]
    rows = []
    canon_index = build_canonical_axis_index(axes)
    # Canonical collisions WITHIN this run's own node set (the
    # grants-flying-static-target / -target-static pair). CDR-05 requires the
    # winner be named deterministically rather than by whichever the loop
    # reaches first: lowest slug string wins, the rest alias into it.
    node_canon = defaultdict(list)
    for s in sorted(nodes):
        node_canon[fcon.canonicalize_label(s)].append(s)

    for slug in sorted(nodes):
        node = nodes[slug]
        members = sorted(node["members"], key=lambda m: m["oracle_id"])
        canon = fcon.canonicalize_label(slug)

        # Existence by canonical form, not by string (F-D).
        existing = axes.get(slug)
        matched_slug = slug if existing is not None else None
        if existing is None:
            twin = canon_index.get(canon)
            if twin is not None:
                existing, matched_slug = axes[twin], twin
        status = existing.get("status") if existing else None
        canonical_twin = matched_slug is not None and matched_slug != slug

        siblings = node_canon[canon]
        if existing is None and len(siblings) > 1 and slug != siblings[0]:
            category, action, target = "collision-node-duplicate", "join-existing", siblings[0]
            reason = (f"canonically identical to sibling node {siblings[0]!r} proposed in the "
                      f"same run ({canon!r}); one axis spelled two ways. The lowest slug "
                      f"instantiates and this one aliases into it (CDR-05, deterministic "
                      f"tie-break). Instantiating both would create duplicate axes.")
        elif existing is None:
            category, action, target = "instantiate", "instantiate", None
            reason = ("grammar-valid composition with no existing axis of any status; "
                      "instantiates as a new axis (source=B-only, grammar lane).")
        elif status == "active" and canonical_twin:
            category, action, target = "join-existing", "join-existing", matched_slug
            reason = (f"canonically identical to the live active axis {matched_slug!r} "
                      f"({canon!r}) — the same axis spelled two ways. Members route there; "
                      f"instantiating would create a duplicate (F-D).")
        elif status == "active":
            category, action, target = "join-existing", "join-existing", matched_slug
            reason = "slug already exists as an active axis; members route to it."
        elif status == "killed":
            # R7: bare, unscoped keyword grants stay killed (b1-Q1 says "PURE
            # keyword-grant axes"); the member routes per the b4-D4 standing
            # rule rather than reviving the slug.
            category, action = "collision-killed", "redirect"
            target = "rule:temporary-keyword-grant"
            reason = ("collides with a KILLED axis. R7/A7: bare unscoped grants are "
                      "engine-redundant and stay killed; the member routes to "
                      "rule:temporary-keyword-grant per the ratified b4-D4 standing rule (A10).")
        elif status == "renamed":
            category, action, target = "collision-renamed", "report-only", None
            reason = (f"collides with a RENAMED shell (renamed_to="
                      f"{existing.get('renamed_to')!r}) that still holds "
                      f"{len(existing.get('members', []))} legacy audit row(s). R7 makes this a "
                      f"REPORT ROW for Captain: the node's payoff sense and the rename target's "
                      f"sense differ, and instantiating would overwrite retained audit rows.")
        else:
            fc.halt(f"virtual node {slug!r} collides with an axis of status {status!r} — that case "
                    f"is not in the ratified closed vocabulary {NODE_CATEGORIES}; 2a must not "
                    f"invent a category. Resolve by ruling, then re-run")

        rows.append({
            "slug": slug, "canonical_label": canon,
            "matched_slug": matched_slug, "matched_by_canonical_form": canonical_twin,
            "category": category, "action": action, "target": target,
            "n_members": len(members), "reason": reason,
            "definition": node["definition"],
            "scope_counts": dict(sorted(node["scope_counts"].items())),
            "members": [{"oracle_id": m["oracle_id"], "quote": m["quote"]} for m in members],
        })
    return rows


# --------------------------------------------------------------------------
# 2. killed / merged / renamed slug routing (A14 / H-02 / R10)
# --------------------------------------------------------------------------

def route_killed_slugs(result: dict, cards: dict) -> list:
    """Every killed/merged/renamed-slug hit, each with a CLOSED action decided
    here by name. No runtime predicates -- A14 forbids a "does the quote fit"
    judgment at apply time, so anything not determined by a ratified rule
    becomes a report row for Captain rather than a guess."""
    axes = result["axes"]
    rows = []
    seen = set()

    for oid, label in sorted(result["killed_slug_codebook_hits"]) + \
                      sorted(result["merged_slug_codebook_hits"]):
        slug = label if label.startswith("rule:") else f"rule:{label}"
        if (oid, slug) in seen:
            continue
        seen.add((oid, slug))
        entry = axes.get(slug, {})
        status = entry.get("status")
        kill_note = " ".join(h.get("note", "") for h in entry.get("history", [])
                             if h.get("action") in ("killed", "merged"))

        if status == "renamed":
            action, target = "redirect", entry.get("renamed_to")
            reason = "renamed shell; the live axis is the rename target."
        elif status == "merged":
            action, target = "redirect", entry.get("merged_into")
            reason = "merged axis; the live axis is the merge target."
        elif slug in A6_WHOLE_SLUG_ALIAS:
            action, target = "redirect", A6_WHOLE_SLUG_ALIAS[slug]
            reason = "A6 whole-slug alias (NOT a global token synonym)."
        elif slug in KILLED_SLUG_ROUTES:
            route = KILLED_SLUG_ROUTES[slug]
            action, target, reason = route["action"], route["target"], route["reason"]
        else:
            fc.halt(f"killed-slug hit on {slug!r} ({oid}) has no route in KILLED_SLUG_ROUTES. "
                    f"A14 requires every instance to be decided in the plan by name — 2a must not "
                    f"infer one from the kill note. Add the ruling, then re-run")

        rows.append({
            "oracle_id": oid, "card_name": cards.get(oid, {}).get("name", ""),
            "slug": slug, "slug_status": status, "lane": "codebook",
            "action": action, "target": target, "reason": reason,
        })
    return rows


# --------------------------------------------------------------------------
# 3. promotions (R5 + A15)
# --------------------------------------------------------------------------

def classify_r5(exact_match: list, result: dict) -> list:
    """R5: free-lane labels literally equal to an active slug. They promote as
    codebook-lane confirmations -- new member, or an assertion merge if the
    card is already a member."""
    active = result["active"]
    rows = []
    seen = set()
    for inst in sorted(exact_match, key=lambda i: (i["label"], i["oracle_id"])):
        slug = inst["label"] if inst["label"].startswith("rule:") else f"rule:{inst['label']}"
        key = (slug, inst["oracle_id"])
        if key in seen:
            continue
        seen.add(key)
        entry = active.get(slug)
        if entry is None:
            fc.halt(f"R5 row {slug}/{inst['oracle_id']} is not an active axis after recomputation")
        already = inst["oracle_id"] in fcb.member_id_set(entry)
        rows.append({
            "slug": slug, "oracle_id": inst["oracle_id"], "card_name": inst["name"],
            "disposition": "assertion-merge" if already else "member-addition",
            "original_lane": "free", "effective_lane": "codebook",
            "promotion_reason": "exact-active-slug-match",
            "quote": inst["quote"],
        })
    return rows


def classify_a15(discovery: dict, result: dict) -> tuple:
    """A15: free-lane clusters whose CANONICAL form equals a ratified closed
    grammar composition. Each row re-validates through validate_slug exactly
    as a grammar-lane label would; failures fall back to discovery."""
    active = result["active"]
    nodes = result["grammar_new_virtual_nodes"]
    by_canon = defaultdict(list)
    for inst in result["free_pool"]:
        by_canon[inst.get("canonical_label")].append(inst)

    active_slugs = sorted(active.keys())
    rows, cluster_summary = [], []
    for name in A15_CLUSTER_NAMES:
        canon = fcon.canonicalize_label(f"rule:{name}")
        insts = by_canon.get(canon, [])
        if not insts:
            fc.halt(f"A15 cluster {name!r} (canonical {canon!r}) has no rows after recomputation — "
                    f"the ratified promotion set and the measured data disagree")
        # Same F-D fix as classify_nodes: existence is a CANONICAL question.
        # `active` here is already active-only, so no rename-shell ambiguity.
        target = A15_TARGET_SLUG_OVERRIDE.get(name, f"rule:{name}")
        active_canon = build_canonical_axis_index(active)
        node_canon_index = {fcon.canonicalize_label(s): s for s in sorted(nodes)}
        canon_target = fcon.canonicalize_label(target)
        if canon_target in active_canon:
            disposition = "join-existing-active"
            target = active_canon[canon_target]
        elif canon_target in node_canon_index:
            disposition = "join-existing-node"
            target = node_canon_index[canon_target]
        else:
            disposition = "instantiate"

        v = validate_slug.validate_slug(target, definition=None, all_slugs=active_slugs)
        ok = bool(v.get("ok"))
        failures = [f["check"] for f in v.get("failures", [])]
        details = [str(f.get("detail", "")) for f in v.get("failures", [])]

        # A15 says a row failing validation falls back to discovery. R6 says
        # these specific clusters PROMOTE. When validation fails purely on
        # closed-VOCABULARY grounds those two ratified statements contradict
        # each other, and 2a is not entitled to pick a side: R9 puts vocabulary
        # additions on the Captain-ratification path, proposed with evidence in
        # the consolidation session. So these rows are BLOCKED, not silently
        # demoted -- dropping 209 Captain-ratified promotions into discovery on
        # a technicality would be exactly the silent invention the house style
        # forbids.
        if ok:
            row_disposition, blocked = disposition, False
        elif failures == ["unknown_vocabulary"]:
            row_disposition, blocked = "blocked-pending-vocabulary-ratification", True
        else:
            row_disposition, blocked = "discovery", False

        for inst in sorted(insts, key=lambda i: i["oracle_id"]):
            rows.append({
                "cluster": name, "canonical_label": canon, "target_slug": target,
                "oracle_id": inst["oracle_id"], "card_name": inst["name"],
                "raw_label": inst["label"], "disposition": row_disposition,
                "validate_slug_ok": ok, "validate_slug_failures": failures,
                "original_lane": "free", "effective_lane": "codebook-grammar",
                "promotion_reason": "canonical-form-matches-ratified-grammar",
                "quote": inst["quote"],
            })
        cluster_summary.append({
            "cluster": name, "canonical_label": canon, "target_slug": target,
            "disposition": row_disposition, "rows": len(insts),
            "validate_slug_ok": ok, "validate_slug_failures": failures,
            "validate_slug_detail": details, "blocked": blocked,
        })

    placeholder = sorted(
        (c for c in discovery["clusters"] if "<" in c["canonical_label"]),
        key=lambda c: (-c["df"], c["canonical_label"]))
    return rows, cluster_summary, placeholder


# --------------------------------------------------------------------------
# 4. same-run duplicate collapse (Captain-ratified 2026-08-01)
# --------------------------------------------------------------------------

def resolve_same_run_duplicates(cards: dict) -> list:
    """Run 1 emitted the same (card, label) more than once in places. Under /1
    set() absorbed that silently; under /2 merge_assertion HALTS on a duplicate
    (class, source_ref). Each duplicate is resolved HERE so 2b performs a
    lookup and never a policy decision.

    Ratified rule: collapse to ONE assertion; lane precedence
    codebook > codebook-grammar > free-promoted; quote tie-break = first in
    deterministic parse order."""
    per_card = json.loads(PARSED_PATH.read_text(encoding="utf-8"))
    rows = []
    for oid in sorted(per_card):
        groups = defaultdict(list)
        for order, inst in enumerate(per_card[oid]):
            label = (inst.get("label") or "").strip()
            quote = (inst.get("evidence_quote") or "").strip()
            lane = inst.get("lane")
            if not (label and quote and lane):
                continue
            slug = label if label.startswith("rule:") else f"rule:{label}"
            groups[slug].append({"order": order, "lane": lane, "quote": quote,
                                 "raw_label": label})
        for slug in sorted(groups):
            emissions = groups[slug]
            if len(emissions) < 2:
                continue
            ranked = sorted(emissions,
                            key=lambda e: (LANE_PRECEDENCE.get(e["lane"], 9), e["order"]))
            winner = ranked[0]
            rows.append({
                "oracle_id": oid, "card_name": cards.get(oid, {}).get("name", ""),
                "slug": slug, "n_emissions": len(emissions),
                "lanes": sorted({e["lane"] for e in emissions}),
                "winning_lane": winner["lane"], "winning_quote": winner["quote"],
                "quotes_differ": len({e["quote"] for e in emissions}) > 1,
                "discarded": [{"lane": e["lane"], "quote": e["quote"]} for e in ranked[1:]],
                "rule": "same-run collapse: lane precedence then first-in-parse-order",
            })
    return rows


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def build(output_path: Path) -> dict:
    live_sha = fcb.sha256_of(fcb.CODEBOOK_PATH)
    codebook = fcb.load_codebook(fcb.CODEBOOK_PATH)
    fcb.lint_or_halt(codebook, "codebook.json (read-only precondition)")
    print(f"precondition: codebook {codebook['schema']} sha256={live_sha[:16]}… lint clean")

    print("recomputing run-1 classification through the committed producer...")
    result, discovery, exact_match, _near_miss = resolve_run1()
    cards = result["cards"]

    nodes = classify_nodes(result)
    node_counts = Counter(r["category"] for r in nodes)
    if sum(node_counts.values()) != EXPECTED_NODE_TOTAL:
        fc.halt(f"node classification totals {sum(node_counts.values())}, expected "
                f"{EXPECTED_NODE_TOTAL} (AG-COUNT-01)")
    if node_counts["instantiate"] != EXPECTED_CLEAN_NODES:
        fc.halt(f"clean instantiations = {node_counts['instantiate']}, expected "
                f"{EXPECTED_CLEAN_NODES} (A14 measured 93 with a string existence test; the F-D canonical fix removes 3 duplicates)")

    routing = route_killed_slugs(result, cards)
    r5 = classify_r5(exact_match, result)
    a15, a15_clusters, placeholder = classify_a15(discovery, result)
    duplicates = resolve_same_run_duplicates(cards)

    if len(r5) != EXPECTED_R5_ROWS:
        fc.halt(f"R5 rows = {len(r5)}, expected {EXPECTED_R5_ROWS}")
    if len(a15) != EXPECTED_A15_ROWS:
        fc.halt(f"A15 rows = {len(a15)}, expected {EXPECTED_A15_ROWS}")

    # --- expected_counts: the closed-loop contract 2b must reproduce exactly
    cb_new = sum(len(v) for v in result["codebook_all_hits"].values()
                 if v) and None  # placeholder, computed below explicitly
    codebook_new = codebook_already = 0
    for slug, oids in sorted(result["codebook_all_hits"].items()):
        existing = fcb.member_id_set(result["active"][slug])
        codebook_new += len(oids - existing)
        codebook_already += len(oids & existing)
    grammar_new = grammar_already = 0
    for slug, oids in sorted(result["grammar_all_hits"].items()):
        existing = fcb.member_id_set(result["active"][slug])
        grammar_new += len(oids - existing)
        grammar_already += len(oids & existing)

    r5_add = sum(1 for r in r5 if r["disposition"] == "member-addition")
    r5_merge = len(r5) - r5_add
    a15_promoted = sum(1 for r in a15 if r["validate_slug_ok"])
    a15_blocked = sum(1 for r in a15
                      if r["disposition"] == "blocked-pending-vocabulary-ratification")
    a15_discovery = len(a15) - a15_promoted - a15_blocked
    node_member_rows = sum(r["n_members"] for r in nodes if r["action"] == "instantiate")

    # BLOCKING decisions: 2b cannot compute exact expected_counts, and session
    # 3 cannot have an exact-match gate, while any of these are open.
    blocking = []
    if a15_blocked:
        blocked_clusters = [c for c in a15_clusters if c.get("blocked")]
        blocking.append({
            "id": "A15-VOCAB-01",
            "rows_affected": a15_blocked,
            "summary": ("Two ratified A15 promotion clusters fail validate_slug purely on "
                        "closed-vocabulary grounds, so R6 (these clusters PROMOTE) and A15 "
                        "(rows failing validation fall back to discovery) contradict."),
            "clusters": [{"cluster": c["cluster"], "target_slug": c["target_slug"],
                          "rows": c["rows"], "unknown_tokens_detail": c["validate_slug_detail"]}
                         for c in blocked_clusters],
            "options": [
                {"option": "A", "action": "Ratify the missing vocabulary tokens per R9",
                 "consequence": "All rows promote as R6 intended; the closed vocabulary grows."},
                {"option": "B", "action": "Rename the target slugs to compositions using existing "
                                          "ratified vocabulary, then re-validate",
                 "consequence": "Rows promote under a different slug; no vocabulary change. The "
                                "new names need Captain approval like any authored slug."},
                {"option": "C", "action": "Let A15's fallback stand",
                 "consequence": "All affected rows go to discovery; R6's promotion of these two "
                                "clusters is effectively reversed. Stated explicitly because it "
                                "is a reversal, not a technicality."},
            ],
            "recommendation": ("Option B or A, not C. The clusters are large and Captain-reviewed; "
                               "letting a vocabulary gap silently reverse a ratified promotion is "
                               "the failure mode the halt-loudly rule exists to prevent. B is "
                               "narrower than A: it needs no vocabulary expansion."),
        })

    expected_counts = {
        "codebook_lane_member_additions": codebook_new,
        "codebook_lane_assertion_merges": codebook_already,
        "grammar_lane_member_additions": grammar_new,
        "grammar_lane_assertion_merges": grammar_already,
        "r5_member_additions": r5_add,
        "r5_assertion_merges": r5_merge,
        "a15_promoted_rows": a15_promoted,
        "a15_blocked_pending_vocabulary": a15_blocked,
        "a15_fell_back_to_discovery": a15_discovery,
        "new_axes_instantiated": node_counts["instantiate"],
        "new_axis_member_rows": node_member_rows,
        "revivals_to_deferred": len(R8_REVIVALS),
        "kill_note_corrections": len(R8_KILL_NOTE_CORRECTIONS),
        "whole_slug_aliases": len(A6_WHOLE_SLUG_ALIAS),
        "routing_rows": len(routing),
        "same_run_duplicates_collapsed": len(duplicates),
    }
    expected_counts["total_enumerated_rows"] = (
        codebook_new + codebook_already + grammar_new + grammar_already
        + len(r5) + a15_promoted + node_member_rows)

    taxonomy = {
        "revivals_to_deferred": [
            {"slug": s, "from_status": result["axes"][s]["status"], "to_status": "deferred",
             "reason": reason,
             "history_note": (f"Revived to deferred per A2 (revived axes never enter active at "
                              f"n=0). {reason}")}
            for s, reason in sorted(R8_REVIVALS.items())],
        "kill_note_corrections": [
            {"slug": s, "stays": "killed", "corrected_reason": reason,
             "history_note": f"Kill-note correction (R8): recorded reason is now {reason!r}."}
            for s, reason in sorted(R8_KILL_NOTE_CORRECTIONS.items())],
        "whole_slug_aliases": [
            {"from_slug": a, "to_slug": b,
             "note": ("A6: WHOLE-SLUG alias in the routing artifact. Explicitly NOT a global "
                      "token->created-tokens synonym, which would corrupt the 28 active slugs "
                      "carrying the bare token `token`.")}
            for a, b in sorted(A6_WHOLE_SLUG_ALIAS.items())],
    }

    report_rows = []
    for r in nodes:
        if r["action"] in ("report-only", "redirect"):
            report_rows.append({"kind": f"node-{r['action']}", "slug": r["slug"],
                                "reason": r["reason"]})
    for r in routing:
        if r["action"] in ("report", "discovery"):
            report_rows.append({"kind": f"routing-{r['action']}", "slug": r["slug"],
                                "oracle_id": r["oracle_id"], "reason": r["reason"]})
    report_rows.append({
        "kind": "placeholder-clusters",
        "reason": (f"A15 names ONE `<state>`-placeholder cluster (10 rows) as report-only. "
                   f"Measurement finds {len(placeholder)} placeholder-bearing clusters totalling "
                   f"{sum(c['df'] for c in placeholder)} rows — SYNTH emitted grammar facet "
                   f"placeholders verbatim more widely than the ratification recorded. All are "
                   f"report-only; none are promoted. Flagged because the ratified text and the "
                   f"measured data differ in scope."),
        "clusters": [{"canonical_label": c["canonical_label"], "rows": c["df"]}
                     for c in placeholder],
    })
    report_rows.append({
        "kind": "det-synth-convergence",
        "reason": (f"{discovery['det_convergent_count']} free-lane instances flagged as "
                   f"DET-convergent; discovery-lane only, no action in this plan."),
    })

    human_summary = {
        "headline": (f"{node_counts['instantiate']} new axes instantiate; "
                     f"{expected_counts['total_enumerated_rows']} rows will be enumerated by 2b; "
                     f"{len(report_rows)} report rows for Captain."),
        "node_classification_table": {k: node_counts.get(k, 0) for k in NODE_CATEGORIES},
        "node_collisions": [{"slug": r["slug"], "category": r["category"],
                             "action": r["action"], "target": r["target"]}
                            for r in nodes if r["category"].startswith("collision")],
        "a15_clusters": a15_clusters,
        "r5_split": {"member_additions": r5_add, "assertion_merges": r5_merge},
        "blocking_decisions": [{"id": b["id"], "rows_affected": b["rows_affected"],
                                "summary": b["summary"]} for b in blocking],
        "routing_actions": dict(sorted(Counter(r["action"] for r in routing).items())),
        "same_run_duplicates": {
            "total": len(duplicates),
            "with_differing_quotes": sum(1 for d in duplicates if d["quotes_differ"]),
            "by_lane_set": dict(sorted(Counter(
                "+".join(d["lanes"]) for d in duplicates).items())),
        },
        "deviations_from_priors": [],
    }
    if node_counts["instantiate"] != EXPECTED_CLEAN_NODES:
        human_summary["deviations_from_priors"].append("clean node count differs from the post-F-D expectation of 90")

    artifact = {
        "schema": "foundry-consolidation-classification/1",
        "STOPPED_FOR_CAPTAIN": True,
        "blocking_decisions": blocking,
        "generated_by": "experiments/foundry_consolidate_run1_classify.py",
        "directive": "docs/CONSOLIDATION-2A-CLASSIFY-DIRECTIVE.md",
        "codebook_sha256_at_classification": live_sha,
        "inputs": {
            str(p.relative_to(REPO_ROOT)): fcb.sha256_of(p)
            for p in sorted([PARSED_PATH, GRAMMARS_PATH, fcb.CODEBOOK_PATH,
                             fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_det_synth_check.json"])
        },
        "human_summary": human_summary,
        "expected_counts": expected_counts,
        "node_classification": nodes,
        "killed_slug_routing": {
            "schema": "foundry-killed-slug-routing/1",
            "closed_action_vocabulary": list(ROUTING_ACTIONS),
            "rows": routing,
        },
        "promotions": {"r5_exact_match": r5, "a15_grammar_canonical": a15,
                       "a15_cluster_summary": a15_clusters},
        "taxonomy_items": taxonomy,
        "same_run_duplicates": duplicates,
        "report_rows": report_rows,
    }

    fc.write_json(output_path, artifact)
    digest = fcb.sha256_of(output_path)

    if fcb.sha256_of(fcb.CODEBOOK_PATH) != live_sha:
        fc.halt("codebook.json changed during this session — 2a must not mutate it")

    print(f"\nwrote {output_path}")
    print(f"  sha256={digest}  size={output_path.stat().st_size}")
    print(f"\nnode classification: {dict(sorted(node_counts.items()))}")
    print(f"routing rows: {len(routing)} {dict(sorted(Counter(r['action'] for r in routing).items()))}")
    print(f"R5: {r5_add} additions + {r5_merge} merges = {len(r5)}")
    print(f"A15: {a15_promoted} promoted, {a15_blocked} BLOCKED pending vocabulary, "
          f"{a15_discovery} to discovery = {len(a15)}")
    for b in blocking:
        print(f"\nBLOCKING DECISION {b['id']}: {b['rows_affected']} rows — {b['summary']}")
    print(f"same-run duplicates collapsed: {len(duplicates)}")
    print(f"report rows: {len(report_rows)}")
    print(f"expected total enumerated rows for 2b: {expected_counts['total_enumerated_rows']}")
    return artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", default=str(OUT_PATH))
    args = parser.parse_args()
    build(Path(args.output))


if __name__ == "__main__":
    main()
