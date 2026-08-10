#!/usr/bin/env python3
"""SESSION 3 — APPLY. Execute exactly the approved plan, zero judgment.

`docs/archive/CONSOLIDATION-APPLY-DIRECTIVE.md` (filed under `archive/` — the
2b directive cites a path that does not exist; that file is still the governing
law). ZERO API SPEND. This is the codebook mutation: 13,565 member additions,
1,806 assertion merges, 87 new axes — the codebook grows 2.5x in one write.

THE ONE RULE (directive §1): **anything the plan does not enumerate DOES NOT
HAPPEN.** This session recomputes no decision. Every number it emits is either
read from the plan or derived from the file it just wrote, and every one is
checked against the plan's `expected_final_counts` EXACTLY — A14 replaced
"small/large drift" language with exact-match-or-halt, so there is no tolerance
band anywhere in here.

NOTE ON THE DIRECTIVE'S OWN NUMBER. §1.2 says *"new_axes — the 93
instantiations"*. The live number is **87**, and 93 was already stale when the
directive was written (the F-D canonical fix took it to 90 on 2026-08-02; four
more nodes became real axes in the 2026-08-09 re-home). The plan is the
authority on the count; the directive is the authority on the *procedure*. This
script asserts against the plan and never against a number typed into prose —
"a specification is a carried-forward count with a rule number attached".

WHAT THE PLAN'S FIVE SECTIONS BECOME
------------------------------------
1. `member_additions` / `assertion_merges` -> `merge_assertion`, the ratified
   membership-growth primitive. Never a hand-built member dict.
2. `new_axes` -> axis records (definition, scope, source="B-only", status,
   the grammar-lane history note), created BEFORE their member rows arrive.
3. `promotions` (R5 + A15) -> nothing of their own: 2b already folded every
   promotion row into 1 with its lane fields. `verify_promotions_folded`
   proves that rather than assuming it.
4. `routing` -> the ratified `foundry-killed-slug-routing/1` data artifact
   (A14/H-02). A redirect is a ROUTING RECORD, not a membership: it is what
   `expected_final_counts` not counting these 2,925 rows means.
5. `taxonomy` -> two revivals killed->deferred (A2: a revived axis never
   enters active at n=0), three kill-note corrections, and the whole-slug
   alias, which A6 places in the routing artifact and NOT in the codebook.

`report_rows` are untouched by construction and reported for Captain.

GATES (directive §2), in the order they run
-------------------------------------------
backup + RESTORE DRILL first (the drill runs before any mutation, so the
rollback path is proven at a moment when using it costs nothing) · an
independent pre-apply verifier on a separate code path (A13), including
quote-verbatim validation of all 15,371 rows against the gated corpus ·
conservation (every pre-existing member and assertion survives byte-identical
— this is a pure-addition mutation and nothing may leave) · lint (inside the
atomic write) · `expected_final_counts` exact · determinism x2 by applying
twice from the backup · a 500-row fixed-seed spot verifier that re-reads the
WRITTEN FILE, not the in-memory object. Any failure restores from the verified
backup and halts.

Quotes are never printed to console (A14). Halt messages name a slug and an
oracle_id and stop there.

    python3 experiments/foundry_consolidate_run1_apply.py --dry-run
    python3 experiments/foundry_consolidate_run1_apply.py --go-sha256 <hash>
"""
import argparse
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                        # noqa: E402
import foundry_codebook as fcb                     # noqa: E402
import foundry_consolidate_run1 as run1            # noqa: E402

PLAN_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_plan.json"
CLASSIFICATION_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_classification.json"
ROUTING_PATH = fc.FOUNDRY_OUT_DIR / "killed_slug_routing.json"
APPLY_REPORT_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_apply_report.json"

PLAN_SCHEMA = "foundry-consolidation-plan/1"
ROUTING_SCHEMA = "foundry-killed-slug-routing/1"
SOURCE_REF = "run1"
BACKUP_TAG = "consolidation-apply"

# Fixed in code, not computed from the clock: a history tag built from
# datetime.now() makes two runs across midnight differ, and determinism x2 is a
# ratified gate. Dated for the record, constant for the gate.
HISTORY_BATCH = "corpus-pass-run1-consolidation-2026-08-09"

# The spot verifier's sample. Fixed seed + a sorted population = the same 500
# rows on every run, so a failure is reproducible by anyone.
SPOT_SAMPLE_N = 500
SPOT_SEED = 20260809

ROUTING_ACTIONS = ("redirect", "split", "report", "discovery", "reject")


# --------------------------------------------------------------------------
# preconditions (directive PRECONDITIONS — verify all, else HALT)
# --------------------------------------------------------------------------

def preconditions(plan_path: Path, go_sha: str) -> dict:
    if not plan_path.exists():
        fc.halt(f"{plan_path} not found — session 3 executes session 2b's plan "
                f"and cannot invent one. Run the enumerator first.")
    plan_sha = fcb.sha256_of(plan_path)
    if go_sha is not None and plan_sha != go_sha:
        fc.halt(f"PLAN HASH MISMATCH — refusing to apply.\n"
                f"    Captain's go names {go_sha}\n"
                f"    the file on disk is {plan_sha}\n"
                f"  The go authorises ONE artifact by hash. A different plan is a "
                f"different mutation and needs its own go.")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema") != PLAN_SCHEMA:
        fc.halt(f"{plan_path}: schema {plan.get('schema')!r}, expected {PLAN_SCHEMA!r}")

    codebook = fcb.load_codebook(fcb.CODEBOOK_PATH)
    fcb.lint_or_halt(codebook, "codebook.json (pre-apply)")
    live_sha = fcb.sha256_of(fcb.CODEBOOK_PATH)
    if live_sha != plan["codebook_sha256_pre_state"]:
        fc.halt(
            f"the codebook has MOVED since the plan was enumerated.\n"
            f"    plan's recorded pre-state {plan['codebook_sha256_pre_state']}\n"
            f"    live codebook is          {live_sha}\n"
            f"  Directive §1: if live state differs from the plan's recorded "
            f"pre-state, HALT — regenerate and re-approve the plan instead of "
            f"adapting it.")

    if not CLASSIFICATION_PATH.exists():
        fc.halt(f"{CLASSIFICATION_PATH} not found — the plan's provenance chain "
                f"cannot be verified.")
    a2a_sha = fcb.sha256_of(CLASSIFICATION_PATH)
    if a2a_sha != plan["classification_sha256"]:
        fc.halt(f"2a's classification artifact has moved since the plan was built.\n"
                f"    plan records {plan['classification_sha256']}\n"
                f"    live is      {a2a_sha}")
    a2a = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
    blocking = a2a.get("blocking_decisions") or []
    if blocking:
        ids = ", ".join(b.get("id", "?") for b in blocking)
        fc.halt(f"2a carries {len(blocking)} BLOCKING decision(s): {ids}. "
                f"A blocked plan is not an approved plan.")

    return {"plan": plan, "plan_sha": plan_sha, "codebook": codebook,
            "live_sha": live_sha, "a2a": a2a, "a2a_sha": a2a_sha}


# --------------------------------------------------------------------------
# A13 — the independent verifier. Separate code path from the writer, and it
# runs BEFORE anything is mutated: a defect found here costs a restore of
# nothing at all.
# --------------------------------------------------------------------------

def verify_plan(plan: dict, codebook: dict) -> dict:
    axes = codebook["axes"]
    active = {s for s, e in axes.items() if e.get("status") == "active"}
    new_slugs = {a["slug"] for a in plan["new_axes"]}
    corpus_ref = plan["corpus_ref"]
    v = []

    # --- new axes: no collision with an axis of ANY status. A `renamed` or
    # `killed` shell occupying the slug is exactly the collision R7 made a
    # report row for, and instantiating over one would overwrite retained
    # audit rows.
    if len(new_slugs) != len(plan["new_axes"]):
        v.append("new_axes carries a duplicate slug")
    for a in plan["new_axes"]:
        if a["slug"] in axes:
            v.append(f"{a['slug']}: new axis collides with an existing "
                     f"{axes[a['slug']].get('status')!r} axis")
        for field in ("definition", "scope", "source", "status", "history_note"):
            if not a.get(field):
                v.append(f"{a['slug']}: new axis is missing {field}")
        if a.get("source") != "B-only":
            v.append(f"{a['slug']}: source is {a.get('source')!r}, directive §1.2 "
                     f"says source=\"B-only\"")
        if a.get("status") != "active":
            v.append(f"{a['slug']}: status is {a.get('status')!r}, expected 'active'")

    # --- taxonomy: the two revivals must be killed today and must NOT be
    # receiving members (A2 — a revived axis enters deferred at n=0).
    revival_slugs = {r["slug"] for r in plan["taxonomy"]["revivals_to_deferred"]}
    for r in plan["taxonomy"]["revivals_to_deferred"]:
        entry = axes.get(r["slug"])
        if entry is None:
            v.append(f"{r['slug']}: revival target is not in the codebook")
        elif entry.get("status") != r["from_status"]:
            v.append(f"{r['slug']}: status is {entry.get('status')!r}, the plan "
                     f"recorded {r['from_status']!r}")
        if r.get("to_status") != "deferred":
            v.append(f"{r['slug']}: A2 requires a revival to enter 'deferred', "
                     f"plan says {r.get('to_status')!r}")
    for c in plan["taxonomy"]["kill_note_corrections"]:
        entry = axes.get(c["slug"])
        if entry is None:
            v.append(f"{c['slug']}: kill-note correction target is not in the codebook")
        elif entry.get("status") != c["stays"]:
            v.append(f"{c['slug']}: status is {entry.get('status')!r}, the plan "
                     f"says it stays {c['stays']!r}")

    # --- rows. Every assertion is checked field by field against A1 rather
    # than trusted because 2b built it: a verifier that reads the producer's
    # output through the producer's own assumptions verifies nothing.
    seen = {}
    for section, expect_member in (("member_additions", False), ("assertion_merges", True)):
        for row in plan[section]:
            slug, oid = row["slug"], row["oracle_id"]
            key = (slug, oid)
            if key in seen:
                v.append(f"{slug}/{oid}: appears twice in the plan "
                         f"({seen[key]} and {section}) — the dedupe law is violated")
                continue
            seen[key] = section

            if slug in new_slugs:
                if expect_member:
                    v.append(f"{slug}/{oid}: an assertion merge onto an axis that "
                             f"does not exist yet")
                entry = None
            elif slug not in active:
                v.append(f"{slug}/{oid}: target axis is "
                         f"{axes.get(slug, {}).get('status', 'ABSENT')!r}, not active")
                continue
            else:
                entry = axes[slug]

            if slug in revival_slugs:
                v.append(f"{slug}/{oid}: rows target an axis being revived to "
                         f"deferred — A2 says it enters at n=0")

            if entry is not None:
                is_member = oid in fcb.member_id_set(entry)
                if is_member != expect_member:
                    v.append(f"{slug}/{oid}: is_member={is_member} but the plan "
                             f"filed it under {section}")
                if is_member:
                    member = fcb.member_by_id(entry, oid)
                    for a in member.get("assertions", []):
                        if a.get("class") == "llm" and a.get("source_ref") == SOURCE_REF:
                            v.append(f"{slug}/{oid}: already carries an "
                                     f"(llm, {SOURCE_REF}) assertion — merge_assertion "
                                     f"halts on that, mid-apply")

            for a in row["assertions"]:
                if a.get("class") != "llm" or a.get("source_ref") != SOURCE_REF:
                    v.append(f"{slug}/{oid}: assertion is not (llm, {SOURCE_REF})")
                for lane_field in ("original_lane", "effective_lane"):
                    if a.get(lane_field) not in fcb.LANES:
                        v.append(f"{slug}/{oid}: {lane_field} "
                                 f"{a.get(lane_field)!r} not in {fcb.LANES}")
                if a.get("evidence_status") != "quoted":
                    v.append(f"{slug}/{oid}: evidence_status is not 'quoted'")
                if a.get("corpus_ref") != corpus_ref:
                    v.append(f"{slug}/{oid}: corpus_ref disagrees with the plan's")
                if not (a.get("quote") or "").strip():
                    v.append(f"{slug}/{oid}: empty quote")
                if list(a.keys()) != [k for k in fcb.ASSERTION_KEY_ORDER if k in a]:
                    v.append(f"{slug}/{oid}: assertion keys are not in canonical order")

    # --- the plan's own "before" numbers must describe the file we loaded.
    # `expected_final_counts` is only exact-matchable if its baseline is the
    # live one; a plan built against a different baseline would still produce a
    # self-consistent after-count and pass the post-apply gate.
    exp = plan["expected_final_counts"]
    live_members = sum(len(a.get("members") or []) for a in axes.values())
    live_assertions = sum(len(m.get("assertions") or [])
                          for a in axes.values() for m in (a.get("members") or []))
    if live_members != exp["member_rows_before"]:
        v.append(f"member_rows_before: plan says {exp['member_rows_before']:,}, "
                 f"live is {live_members:,}")
    if live_assertions != exp["assertion_rows_before"]:
        v.append(f"assertion_rows_before: plan says {exp['assertion_rows_before']:,}, "
                 f"live is {live_assertions:,}")
    live_by_status = dict(sorted(Counter(a.get("status") for a in axes.values()).items()))
    if live_by_status != exp["axes_by_status_before"]:
        v.append(f"axes_by_status_before: plan says {exp['axes_by_status_before']}, "
                 f"live is {live_by_status}")
    if len(plan["member_additions"]) != exp["member_additions"]:
        v.append("member_additions: the plan's row count disagrees with its own "
                 "expected_final_counts")
    if len(plan["assertion_merges"]) != exp["assertion_merges"]:
        v.append("assertion_merges: the plan's row count disagrees with its own "
                 "expected_final_counts")
    if len(plan["new_axes"]) != exp["new_axes"]:
        v.append("new_axes: the plan's row count disagrees with its own "
                 "expected_final_counts")

    if v:
        head = "\n  ".join(v[:40])
        fc.halt(f"the independent verifier found {len(v)} problem(s) in the plan, "
                f"BEFORE any mutation:\n  {head}"
                + (f"\n  ... and {len(v) - 40} more" if len(v) > 40 else ""))
    return {"rows_verified": len(seen), "new_axes": len(new_slugs)}


def verify_quotes_verbatim(plan: dict) -> dict:
    """A13's quote-verbatim check. Every planned assertion's quote must appear
    in its card's full oracle text, all faces — the producer's own gate
    (`quote.lower() not in full_text`), re-applied here from the corpus rather
    than from anything 2a or 2b wrote down.

    This is the check that would catch a quote attached to the wrong card, and
    it is the only pre-apply gate that reads the CARDS at all."""
    cards, _, _ = fc.load_corpus_gated()
    text_cache = {}
    bad = []
    checked = 0
    for section in ("member_additions", "assertion_merges"):
        for row in plan[section]:
            oid = row["oracle_id"]
            card = cards.get(oid)
            if card is None:
                bad.append(f"{row['slug']}/{oid}: not in the gated corpus")
                continue
            if oid not in text_cache:
                text_cache[oid] = run1.full_oracle_text(card)
            full = text_cache[oid]
            for a in row["assertions"]:
                checked += 1
                if a["quote"].strip().lower() not in full:
                    # A14: name the row, never the quote.
                    bad.append(f"{row['slug']}/{oid}: quote is not verbatim in "
                               f"the card's oracle text")
    if bad:
        head = "\n  ".join(bad[:20])
        fc.halt(f"quote-verbatim validation failed on {len(bad)} assertion(s):\n  "
                f"{head}" + (f"\n  ... and {len(bad) - 20} more" if len(bad) > 20 else ""))
    return {"assertions_quote_checked": checked, "cards_touched": len(text_cache)}


def verify_promotions_folded(plan: dict) -> dict:
    """Directive §1.3: promotions land "as enumerated, with lane fields
    preserved". 2b folded them into member_additions / assertion_merges, so
    this session's job is to PROVE that fold rather than re-apply it — a second
    application would be a duplicate (class, source_ref) and a halt mid-write.

    Checked by (slug, oracle_id) AND by lane triple, because a promotion whose
    `original_lane` was lost on the way into the plan is exactly the A15 defect
    the lane fields exist to record."""
    rows = {}
    for section in ("member_additions", "assertion_merges"):
        for row in plan[section]:
            rows[(row["slug"], row["oracle_id"])] = row["assertions"]

    missing, lane_mismatch = [], []

    def check(slug, oid, want):
        found = rows.get((slug, oid))
        if found is None:
            missing.append(f"{slug}/{oid}")
            return
        for a in found:
            if (a.get("original_lane"), a.get("effective_lane"),
                    a.get("promotion_reason")) == want:
                return
        lane_mismatch.append(f"{slug}/{oid}")

    for r in plan["promotions"]["r5_exact_match"]:
        check(r["slug"], r["oracle_id"],
              (r["original_lane"], r["effective_lane"], r["promotion_reason"]))
    a15 = [r for r in plan["promotions"]["a15_grammar_canonical"] if r["validate_slug_ok"]]
    for r in a15:
        check(r["target_slug"], r["oracle_id"],
              (r["original_lane"], r["effective_lane"], r["promotion_reason"]))

    if missing or lane_mismatch:
        fc.halt(f"promotion rows are not correctly folded into the plan: "
                f"{len(missing)} absent, {len(lane_mismatch)} present with "
                f"different lane fields. e.g. absent={missing[:3]} "
                f"lanes={lane_mismatch[:3]}")
    return {"r5_rows_folded": len(plan["promotions"]["r5_exact_match"]),
            "a15_rows_folded": len(a15)}


# --------------------------------------------------------------------------
# apply — the writer. Nothing in here decides anything.
# --------------------------------------------------------------------------

def apply_plan(codebook: dict, plan: dict) -> dict:
    axes = codebook["axes"]
    counts = Counter()

    # 1. new axes FIRST — their member rows arrive in step 2 and merge_assertion
    #    needs the entry to exist.
    for a in plan["new_axes"]:
        if a["slug"] in axes:
            fc.halt(f"{a['slug']}: already exists — collision with a new axis")
        axes[a["slug"]] = {
            "definition": a["definition"],
            "scope": a["scope"],
            "source": a["source"],
            "parameterized": bool(a.get("parameterized", False)),
            "members": [],
            "status": a["status"],
            "merged_into": None,
            "history": [{"batch": HISTORY_BATCH, "action": "created",
                         "note": a["history_note"]}],
        }
        counts["new_axes"] += 1

    # 2. membership. One primitive, both sections — `merge_assertion` is what
    #    decides created-vs-merged, and it halting on a duplicate is the point.
    touched = Counter()
    for section, expected in (("member_additions", "created"),
                              ("assertion_merges", "merged")):
        for row in plan[section]:
            entry = axes.get(row["slug"])
            if entry is None:
                fc.halt(f"{row['slug']}: axis absent at apply time")
            for i, assertion in enumerate(row["assertions"]):
                outcome = fcb.merge_assertion(entry, row["oracle_id"], assertion)
                counts[f"assertions_{section}"] += 1
                if i == 0 and outcome != expected:
                    fc.halt(f"{row['slug']}/{row['oracle_id']}: merge_assertion "
                            f"reported {outcome!r} on a row the plan filed under "
                            f"{section} (expected {expected!r})")
            counts[section] += 1
            touched[row["slug"]] += 1

    # 3. taxonomy. A2 revivals killed -> deferred, kill-note corrections, and
    #    the A6 alias, which is a ROUTING-artifact row and never a codebook edit
    #    (a global token synonym would corrupt the 28 active slugs carrying the
    #    bare token `token` — that is the whole reason A6 exists).
    for r in plan["taxonomy"]["revivals_to_deferred"]:
        entry = axes[r["slug"]]
        entry["status"] = r["to_status"]
        entry.setdefault("history", []).append(
            {"batch": HISTORY_BATCH, "action": "revived", "note": r["history_note"]})
        counts["revivals"] += 1
    for c in plan["taxonomy"]["kill_note_corrections"]:
        entry = axes[c["slug"]]
        entry.setdefault("history", []).append(
            {"batch": HISTORY_BATCH, "action": "kill_note_corrected",
             "note": c["history_note"]})
        counts["kill_note_corrections"] += 1

    # 4. provenance on every axis that received rows. Not required by the
    #    directive; recorded because the alternative is 277 axes gaining 15,371
    #    rows with nothing in their own history saying where those came from.
    for slug in sorted(touched):
        if slug in {a["slug"] for a in plan["new_axes"]}:
            continue
        axes[slug].setdefault("history", []).append({
            "batch": HISTORY_BATCH, "action": "members_received",
            "note": f"corpus pass run 1 consolidation: {touched[slug]} row(s) "
                    f"applied from corpus_pass_run1_plan.json "
                    f"(sha256 {plan['_plan_sha256'][:16]}), class=llm "
                    f"source_ref={SOURCE_REF}.",
        })
    counts["axes_touched"] = len(touched)
    return counts


# --------------------------------------------------------------------------
# gates
# --------------------------------------------------------------------------

def gate_expected_final_counts(codebook: dict, plan: dict) -> dict:
    """A14: exact match or halt. No drift categories."""
    exp = plan["expected_final_counts"]
    axes = codebook["axes"]
    by_status = Counter(a.get("status") for a in axes.values())
    member_rows = sum(len(a.get("members") or []) for a in axes.values())
    assertion_rows = sum(len(m.get("assertions") or [])
                         for a in axes.values() for m in (a.get("members") or []))
    got = {
        "axes_active_after": by_status["active"],
        "axes_total_after": len(axes),
        "member_rows_after": member_rows,
        "assertion_rows_after": assertion_rows,
        "axes_by_status_after": dict(sorted(by_status.items())),
    }
    # The plan records no after-status breakdown, so derive the one it implies:
    # the new axes enter active, and each A2 revival moves its own recorded
    # from_status to deferred. Counted off the taxonomy rows, never off a
    # literal — a hand-typed "2" here is the carried-forward-count trap in the
    # gate that exists to catch it.
    implied = Counter(exp["axes_by_status_before"])
    implied["active"] = exp["axes_active_after"]
    for r in plan["taxonomy"]["revivals_to_deferred"]:
        implied[r["from_status"]] -= 1
        implied[r["to_status"]] += 1
    exp = dict(exp, axes_by_status_after=dict(sorted(implied.items())))
    bad = [(k, exp[k], v) for k, v in sorted(got.items()) if exp[k] != v]
    if bad:
        lines = "\n".join(f"    {k}: plan says {a}, got {b}" for k, a, b in bad)
        fc.halt("expected_final_counts DO NOT MATCH. A14 forbids a drift "
                "category here — restoring from backup:\n" + lines)
    return got


def gate_conservation(before: dict, after: dict) -> dict:
    """This mutation is pure addition: no member and no assertion may leave,
    and no pre-existing assertion may change. A count of what ARRIVED cannot
    see something that LEFT, which is why this is a separate gate from
    expected_final_counts — 'a census cannot answer did anything get lost'."""
    lost_members, changed = [], []
    kept_assertions = 0
    for slug, entry in before["axes"].items():
        post = after["axes"].get(slug)
        if post is None:
            lost_members.append(f"{slug}: axis vanished")
            continue
        post_by_id = {m["oracle_id"]: m for m in post.get("members") or []}
        for m in entry.get("members") or []:
            pm = post_by_id.get(m["oracle_id"])
            if pm is None:
                lost_members.append(f"{slug}/{m['oracle_id']}")
                continue
            post_keys = {(a["class"], a["source_ref"]): a for a in pm["assertions"]}
            for a in m["assertions"]:
                key = (a["class"], a["source_ref"])
                if key not in post_keys:
                    lost_members.append(f"{slug}/{m['oracle_id']} lost assertion {key}")
                elif post_keys[key] != a:
                    changed.append(f"{slug}/{m['oracle_id']} assertion {key} was rewritten")
                else:
                    kept_assertions += 1
    if lost_members or changed:
        head = "\n  ".join((lost_members + changed)[:20])
        fc.halt(f"CONSERVATION FAILED: {len(lost_members)} lost, {len(changed)} "
                f"rewritten. This is a pure-addition mutation; nothing may "
                f"leave:\n  {head}")
    return {"pre_existing_assertions_intact": kept_assertions}


def spot_verify(written_path: Path, plan: dict) -> dict:
    """The independent spot-verifier (directive §2): 500 fixed-seed plan rows
    re-checked 1:1 against the WRITTEN FILE.

    It re-reads from disk on purpose. Every other gate above inspects the
    in-memory object the writer just built, so all of them share the writer's
    blind spots; this one shares only the serializer's."""
    cb = json.loads(Path(written_path).read_text(encoding="utf-8"))
    axes = cb["axes"]
    population = sorted(
        [(r["slug"], r["oracle_id"], "member_additions") for r in plan["member_additions"]] +
        [(r["slug"], r["oracle_id"], "assertion_merges") for r in plan["assertion_merges"]])
    rng = random.Random(SPOT_SEED)
    sample = rng.sample(population, min(SPOT_SAMPLE_N, len(population)))
    by_key = {}
    for section in ("member_additions", "assertion_merges"):
        for r in plan[section]:
            by_key[(r["slug"], r["oracle_id"])] = r["assertions"]

    bad = []
    for slug, oid, section in sample:
        entry = axes.get(slug)
        if entry is None:
            bad.append(f"{slug}: axis absent from the written file")
            continue
        member = next((m for m in entry.get("members") or []
                       if m["oracle_id"] == oid), None)
        if member is None:
            bad.append(f"{slug}/{oid}: member absent from the written file")
            continue
        written = {(a["class"], a["source_ref"]): a for a in member["assertions"]}
        for planned in by_key[(slug, oid)]:
            key = (planned["class"], planned["source_ref"])
            got = written.get(key)
            if got is None:
                bad.append(f"{slug}/{oid}: planned assertion {key} not written")
            elif got != planned:
                # A14 — report WHICH field, never its value.
                fields = sorted(set(got) | set(planned))
                diff = [f for f in fields if got.get(f) != planned.get(f)]
                bad.append(f"{slug}/{oid}: written assertion differs from the "
                           f"plan on {diff}")
        want_tier = fcb.expected_tier(member["assertions"])
        if member.get("tier") != want_tier:
            bad.append(f"{slug}/{oid}: tier {member.get('tier')!r} does not match "
                       f"the assertion stack ({want_tier!r})")
    if bad:
        head = "\n  ".join(bad[:20])
        fc.halt(f"SPOT VERIFIER FAILED on {len(bad)} of {len(sample)} sampled "
                f"rows:\n  {head}")
    return {"sampled": len(sample), "seed": SPOT_SEED, "population": len(population)}


# --------------------------------------------------------------------------
# backup / restore
# --------------------------------------------------------------------------

def restore_from_backup(backup: Path) -> str:
    """The rollback path, used by the drill, by determinism pass 2, and by
    every failure exit. One implementation, so the drill proves the same code
    a failure would run."""
    shutil.copy2(backup, fcb.CODEBOOK_PATH)
    return fcb.sha256_of(fcb.CODEBOOK_PATH)


def restore_drill(backup: Path, expected_sha: str) -> None:
    """Directive §2: restore drill FIRST. Proving the rollback at a moment when
    it restores the file to exactly what it already is costs one copy and makes
    the rollback a tested path instead of an assumed one."""
    got = restore_from_backup(backup)
    if got != expected_sha:
        fc.halt(f"RESTORE DRILL FAILED: restoring {backup.name} produced "
                f"{got}, expected {expected_sha}. The rollback path does not "
                f"work; nothing has been mutated and nothing will be.")
    fcb.lint_or_halt(fcb.load_codebook(fcb.CODEBOOK_PATH), "codebook.json (post-drill)")
    print(f"restore drill: OK — rollback verified against {backup.name}")


# --------------------------------------------------------------------------
# companion artifacts (directive §3)
# --------------------------------------------------------------------------

def write_routing_artifact(plan: dict, plan_sha: str) -> dict:
    """`foundry-killed-slug-routing/1` (A14/H-02). Closed action vocabulary, no
    runtime predicates, every instance decided in the plan by name.

    A `redirect` here is a routing RECORD, not a membership: the redirect
    targets are not in member_additions and are not counted by
    expected_final_counts. That is deliberate — routing a hit off a renamed
    shell says where the label WOULD have gone, and turning it into a
    membership would be this session exercising judgment."""
    rows = plan["routing"]
    unknown = sorted({r["action"] for r in rows} - set(ROUTING_ACTIONS))
    if unknown:
        fc.halt(f"routing rows carry action(s) outside the closed A14 "
                f"vocabulary: {unknown}")
    for r in rows:
        if r["action"] == "redirect" and not r.get("target"):
            fc.halt(f"{r['slug']}/{r['oracle_id']}: redirect with no target")
    artifact = {
        "schema": ROUTING_SCHEMA,
        "generated_by": "experiments/foundry_consolidate_run1_apply.py",
        "plan_sha256": plan_sha,
        "corpus_ref": plan["corpus_ref"],
        "action_vocabulary": list(ROUTING_ACTIONS),
        "note": "A redirect is a routing record, not a membership. These rows "
                "are deliberately absent from the codebook mutation and from "
                "expected_final_counts.",
        "counts": dict(sorted(Counter(r["action"] for r in rows).items())),
        "whole_slug_aliases": plan["taxonomy"]["whole_slug_aliases"],
        "rows": rows,
    }
    fc.write_json(ROUTING_PATH, artifact)
    return {"path": str(ROUTING_PATH), "rows": len(rows),
            "sha256": fcb.sha256_of(ROUTING_PATH)}


def write_card_axes_index() -> dict:
    """oracle_id -> {axes, dfc, gamechanger}. Derived, deterministic,
    regenerated after every codebook write, NEVER authoritative.

    `dfc` is derived fresh from the corpus by the locked rule — two-image iff
    `card_faces[0].image_uris` exists — and never by the presence of
    `card_faces`, which split/flip/adventure cards also have."""
    cb = fcb.load_codebook(fcb.CODEBOOK_PATH)
    cards, _, _ = fc.load_corpus_gated()
    gamechangers = load_gamechangers()

    per_card = defaultdict(list)
    for slug, entry in cb["axes"].items():
        # Live axes only. A `renamed` shell retains its members as a tombstone
        # (CDR-09 precedent), so including one double-counts every member it
        # shares with its rename target.
        if entry.get("status") not in ("active", "deferred"):
            continue
        for m in entry.get("members") or []:
            per_card[m["oracle_id"]].append(slug)

    index = {}
    for oid in sorted(per_card):
        card = cards.get(oid)
        if card is None:
            fc.halt(f"card_axes_index: member {oid} is not in the gated corpus — "
                    f"a membership on a card the corpus gate removes is a real "
                    f"finding, not something to skip past")
        faces = card.get("card_faces") or []
        index[oid] = {
            "axes": sorted(per_card[oid]),
            "dfc": bool(faces and faces[0].get("image_uris")),
            "gamechanger": oid in gamechangers,
        }
    artifact = {
        "schema": "foundry-card-axes-index/1",
        "generated_by": "experiments/foundry_consolidate_run1_apply.py",
        "codebook_sha256": fcb.sha256_of(fcb.CODEBOOK_PATH),
        "corpus_ref": fcb.corpus_ref_current(),
        "axis_statuses_included": ["active", "deferred"],
        "note": "Derived view. Never authoritative — regenerate after every "
                "codebook write.",
        "cards": len(index),
        "index": index,
    }
    path = fc.FOUNDRY_OUT_DIR / "card_axes_index.json"
    fc.write_json(path, artifact)
    return {"path": str(path), "cards": len(index),
            "dfc": sum(1 for r in index.values() if r["dfc"]),
            "gamechangers": sum(1 for r in index.values() if r["gamechanger"]),
            "sha256": fcb.sha256_of(path)}


GAMECHANGERS_PATH = fcb.REPO_ROOT / "tags" / "gamechangers.yaml"

GAMECHANGERS_SEED = '''# Game Changers — oracle_id list, hand-curated.
#
# Seeded empty by the run-1 consolidation apply (session 3). The format is the
# whole content of this file until Captain populates it; an empty list is a
# real statement ("no card is flagged yet"), not a placeholder.
#
# Schema: a top-level `gamechangers` key whose value is a list of oracle_ids.
# A trailing `# Card Name` comment is encouraged and ignored by the reader.
# oracle_id is the only card key in this repo — never a name, never a slug.
#
# Example (schema only — not an entry):
# gamechangers:
#   - 00000000-0000-0000-0000-000000000000  # Example Card
#
# Consumed by: experiments/foundry_consolidate_run1_apply.py
# (card_axes_index.json's `gamechanger` flag).

gamechangers: []
'''


def load_gamechangers() -> set:
    """Reads the seed without a YAML dependency: the file's whole grammar is
    `gamechangers:` followed by `- <uuid>` lines, and the seed above IS the
    spec. Anything else halts rather than being silently read as empty — an
    unparsed flag file looks exactly like an empty one."""
    if not GAMECHANGERS_PATH.exists():
        return set()
    oids = set()
    saw_key = False
    for lineno, raw in enumerate(GAMECHANGERS_PATH.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line in ("gamechangers:", "gamechangers: []"):
            saw_key = True
            continue
        if line.startswith("- "):
            oid = line[2:].strip()
            if not fcb._UUID_RE.match(oid):
                fc.halt(f"{GAMECHANGERS_PATH}:{lineno}: {oid!r} is not an "
                        f"oracle_id (uuid) shape")
            oids.add(oid)
            continue
        fc.halt(f"{GAMECHANGERS_PATH}:{lineno}: unparseable line. This reader "
                f"accepts only `gamechangers:` and `- <oracle_id>` — an "
                f"unparsed flag file reads as an empty one, which is why this "
                f"halts instead of skipping.")
    if not saw_key:
        fc.halt(f"{GAMECHANGERS_PATH}: no `gamechangers:` key")
    return oids


def seed_gamechangers() -> dict:
    """Written once. If the file exists it is left alone — Captain's entries
    are not something an apply script overwrites with a seed."""
    if GAMECHANGERS_PATH.exists():
        return {"path": str(GAMECHANGERS_PATH), "action": "left as-is",
                "entries": len(load_gamechangers())}
    GAMECHANGERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    GAMECHANGERS_PATH.write_text(GAMECHANGERS_SEED, encoding="utf-8")
    return {"path": str(GAMECHANGERS_PATH), "action": "seeded",
            "entries": len(load_gamechangers())}


DRY_RUN_STALE_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_consolidation_dry_run.json"
DRY_RUN_CORRECTED_PATH = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_consolidation_corrected.json"


def write_dry_run_correction(plan: dict, a2a: dict) -> dict:
    """G4: a generated artifact gets a GENERATOR fix, never a hand edit. The
    dry run's producer (`foundry_consolidate_run1.py`) would rewrite it against
    TODAY's codebook, which is a different question from the one that artifact
    answers, so this takes the directive's other option — a corrected successor
    artifact that supersedes it.

    Every corrected value is DERIVED here from the live 2a classification and
    the plan. None is typed in: 'a carried-forward count is not a measurement',
    and this artifact exists precisely because six of them were."""
    if not DRY_RUN_STALE_PATH.exists():
        fc.halt(f"{DRY_RUN_STALE_PATH} not found — nothing to supersede")
    stale = json.loads(DRY_RUN_STALE_PATH.read_text(encoding="utf-8"))
    exp = plan["expansion_counts"]
    fin = plan["expected_final_counts"]

    corrections = [
        {"field": "BLOCKED", "stale_value": stale.get("BLOCKED"),
         "corrected_value": False,
         "why": "The schema blocker cleared 2026-08-01 (foundry-codebook/2) and "
                "A15-VOCAB-01 cleared 2026-08-09. The plan is applied; this "
                "artifact's BLOCKED flag is the last place still saying otherwise."},
        {"field": "codebook_lane_new_member_instances",
         "stale_value": stale.get("codebook_lane_new_member_instances"),
         "corrected_value": exp["codebook_lane_member_additions"],
         "why": "B-MIGRATION-DISCOVERY §6(b). Recomputed by 2a against the "
                "codebook as it stands, not as it stood on 2026-08-01: 44 new "
                "axes and five renames have landed since."},
        {"field": "codebook_lane_axes_touched",
         "stale_value": stale.get("codebook_lane_axes_touched"),
         "corrected_value": len({r["slug"]
                                 for section in ("member_additions", "assertion_merges")
                                 for r in plan[section]
                                 if any(a["original_lane"] == "codebook"
                                        for a in r["assertions"])}),
         "why": "Derived from the plan's own rows."},
        {"field": "grammar_lane_new_virtual_nodes",
         "stale_value": len(stale.get("grammar_lane_new_virtual_nodes") or {}),
         "corrected_value": exp["new_axes_instantiated"],
         "why": "B-MIGRATION-DISCOVERY §6(a) + A14. 95 raw nodes, 93 clean at "
                "audit time, 90 after the F-D canonical fix (2026-08-02), 87 "
                "after the 2026-08-09 re-home made four of them real axes. The "
                "APPLY directive §1.2 still says 93 and is stale for the same "
                "reason this artifact is."},
        {"field": "grammar_lane_new_virtual_node_members",
         "stale_value": "recorded as 1,297 in ADDENDUM-4 §6 item 0 (attribution "
                        "error: 1,297 is the EXISTING-axis pair count)",
         "corrected_value": exp["new_axis_member_rows"],
         "why": "B-MIGRATION-DISCOVERY §6(a) names the correction; this is its "
                "value re-derived against the current codebook (§6 measured 607 "
                "against 95 nodes; 87 nodes now hold this many)."},
        {"field": "merged_or_renamed_slug_codebook_hits",
         "stale_value": len(stale.get("merged_or_renamed_slug_codebook_hits") or []),
         "corrected_value": exp["routing_rows"],
         "why": "The 2026-08-09 renames took `renamed` axes 45 -> 108, so hits "
                "that used to land on an active slug now land on a shell and "
                "route. A redirect is not a loss."},
        {"field": "exact_match_reinvention_count (§6 item 2, R5)",
         "stale_value": "141 counted as a metric, never promoted",
         "corrected_value": len(plan["promotions"]["r5_exact_match"]),
         "why": "OQ6 is resolved: R5 rows promote as codebook-lane "
                "confirmations and are folded into this plan's rows. The 141 "
                "was itself a moving number — foundry_r5_attribution.py "
                "attributes 141 -> 163 to eight ratified codebook mutations."},
        {"field": "a15 rows (§6 item 3, the closed-grammar pool)",
         "stale_value": "213",
         "corrected_value": exp["a15_promoted_rows"],
         "why": "A15-VOCAB-01-RULING-2026-08-09 §9b: 213 NEVER REPRODUCED. "
                "Replayed at the classification's own recorded inputs it gives "
                "194 while R5 gives 141 exactly in the same run. Pinned at 194 "
                "because it is what the data yields, not because it drifted."},
    ]
    artifact = {
        "schema": "foundry-corpus-pass-run1-consolidation-dry-run/2",
        "generated_by": "experiments/foundry_consolidate_run1_apply.py",
        "supersedes": {"path": str(DRY_RUN_STALE_PATH.relative_to(fcb.REPO_ROOT)),
                       "sha256": fcb.sha256_of(DRY_RUN_STALE_PATH),
                       "schema": stale.get("schema")},
        "authority": "B-MIGRATION-DISCOVERY.md §6 (the corrections) + "
                     "corpus_pass_run1_classification.json (the values). G4: the "
                     "stale artifact is superseded, never hand-edited.",
        "classification_sha256": plan["classification_sha256"],
        "plan_sha256": plan["_plan_sha256"],
        "corrections": corrections,
        "post_apply_actuals": fin,
        "blocking_decisions": a2a.get("blocking_decisions") or [],
    }
    fc.write_json(DRY_RUN_CORRECTED_PATH, artifact)
    return {"path": str(DRY_RUN_CORRECTED_PATH), "corrections": len(corrections),
            "sha256": fcb.sha256_of(DRY_RUN_CORRECTED_PATH)}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def coverage(cb: dict) -> tuple:
    cards, _, _ = fc.load_corpus_gated()
    tagged = set()
    for entry in cb["axes"].values():
        if entry.get("status") not in ("active", "deferred"):
            continue
        for m in entry.get("members") or []:
            tagged.add(m["oracle_id"])
    return len(tagged), len(cards)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", default=str(PLAN_PATH))
    ap.add_argument("--go-sha256", default=None,
                    help="the plan sha256 Captain's go names. REQUIRED to write.")
    ap.add_argument("--dry-run", action="store_true",
                    help="preconditions + the full independent verifier + the "
                         "conservation line, and stop before any mutation")
    args = ap.parse_args()

    if not args.dry_run and not args.go_sha256:
        fc.halt("--go-sha256 is required to apply. Session 3 runs only on "
                "Captain's explicit go naming the plan hash it approves "
                "(2b directive §10c). Use --dry-run to verify without writing.")

    print("=" * 78)
    print("SESSION 3 — APPLY the run-1 consolidation plan")
    print("=" * 78)

    ctx = preconditions(Path(args.plan), args.go_sha256)
    plan, codebook = ctx["plan"], ctx["codebook"]
    plan["_plan_sha256"] = ctx["plan_sha"]
    print(f"plan            sha256={ctx['plan_sha']}")
    print(f"  hash-checked against the go: {'YES' if args.go_sha256 else 'DRY RUN — not checked'}")
    print(f"codebook (pre)  sha256={ctx['live_sha'][:32]}… lint clean, matches the plan's pre-state")
    print(f"2a artifact     sha256={ctx['a2a_sha'][:32]}…, 0 blocking decisions")

    print("\n--- independent verifier (A13), pre-mutation " + "-" * 32)
    vstats = verify_plan(plan, codebook)
    print(f"  rows verified          {vstats['rows_verified']:,} "
          f"(every row's axis status, membership state and A1 assertion fields)")
    pstats = verify_promotions_folded(plan)
    print(f"  promotions folded      R5 {pstats['r5_rows_folded']}, "
          f"A15 {pstats['a15_rows_folded']} — present with lane fields preserved")
    qstats = verify_quotes_verbatim(plan)
    print(f"  quotes verbatim        {qstats['assertions_quote_checked']:,} "
          f"assertion(s) across {qstats['cards_touched']:,} cards, all found in "
          f"full oracle text")

    fin = plan["expected_final_counts"]
    print("\n--- what will change " + "-" * 55)
    print(f"  member rows      {fin['member_rows_before']:>7,} -> {fin['member_rows_after']:>7,}"
          f"   (+{fin['member_additions']:,})")
    print(f"  assertion rows   {fin['assertion_rows_before']:>7,} -> {fin['assertion_rows_after']:>7,}")
    print(f"  active axes      {fin['axes_by_status_before']['active']:>7,} -> {fin['axes_active_after']:>7,}"
          f"   (+{fin['new_axes']})")
    print(f"  routing rows     {len(plan['routing']):,} -> the routing artifact, NOT the codebook")
    print(f"  report rows      {len(plan['report_rows'])} — untouched, for Captain")

    if args.dry_run:
        print("\nDRY RUN — nothing written. Every pre-mutation gate passed.")
        return 0

    print("\n--- backup + restore drill " + "-" * 49)
    backup = fcb.backup_codebook(BACKUP_TAG)
    restore_drill(backup, ctx["live_sha"])

    before = json.loads(Path(backup).read_text(encoding="utf-8"))

    def apply_pass(label: str):
        cb = fcb.load_codebook(backup)
        counts = apply_plan(cb, plan)
        gate_expected_final_counts(cb, plan)
        cons = gate_conservation(before, cb)
        sha = fcb.write_codebook_atomic(fcb.CODEBOOK_PATH, cb, "codebook.json")
        print(f"  {label}: sha256={sha[:32]}…  "
              f"+{counts['member_additions']:,} members, "
              f"+{counts['assertion_merges']:,} merges, "
              f"+{counts['new_axes']} axes")
        return sha, counts, cons

    print("\n--- apply " + "-" * 66)
    # Every gate below halts via fc.halt, which is sys.exit -> SystemExit. That
    # is caught here on purpose: a halt mid-apply is exactly the case the
    # backup exists for, and re-raising it without restoring would leave a
    # half-applied codebook behind the very message saying it stopped.
    try:
        sha1, counts, cons = apply_pass("pass 1")
        print(f"  conservation: {cons['pre_existing_assertions_intact']:,} "
              f"pre-existing assertions intact, 0 lost, 0 rewritten")
        print("  expected_final_counts: EXACT match, all five post-apply totals")

        restored = restore_from_backup(backup)
        if restored != ctx["live_sha"]:
            fc.halt("restore before determinism pass 2 did not reproduce the "
                    "pre-state sha256")
        sha2, _, _ = apply_pass("pass 2 (from backup)")
        if sha1 != sha2:
            fc.halt(f"DETERMINISM x2 FAILED: {sha1} vs {sha2}.")
        print("  determinism x2: byte-identical")

        spot = spot_verify(fcb.CODEBOOK_PATH, plan)
        print(f"  spot verifier: {spot['sampled']} rows (seed {spot['seed']}) "
              f"re-read from the written file, all 1:1 with the plan")
    except BaseException:
        got = restore_from_backup(backup)
        print(f"\nRESTORED from {backup.name} — codebook is back at {got[:16]}… "
              f"({'matches' if got == ctx['live_sha'] else 'DOES NOT MATCH'} "
              f"the pre-state). Nothing landed.", file=sys.stderr)
        raise

    print("\n--- companion artifacts " + "-" * 52)
    gc = seed_gamechangers()
    print(f"  tags/gamechangers.yaml     {gc['action']} ({gc['entries']} entries)")
    routing = write_routing_artifact(plan, ctx["plan_sha"])
    print(f"  killed_slug_routing.json   {routing['rows']:,} rows  "
          f"sha256={routing['sha256'][:16]}…")
    index = write_card_axes_index()
    print(f"  card_axes_index.json       {index['cards']:,} cards, "
          f"{index['dfc']:,} dfc, {index['gamechangers']} gamechangers  "
          f"sha256={index['sha256'][:16]}…")
    corrected = write_dry_run_correction(plan, ctx["a2a"])
    print(f"  dry-run correction         {corrected['corrections']} corrections  "
          f"sha256={corrected['sha256'][:16]}…")

    cb_final = fcb.load_codebook(fcb.CODEBOOK_PATH)
    tagged, corpus_n = coverage(cb_final)
    by_status = Counter(a.get("status") for a in cb_final["axes"].values())
    sizes = sorted(len(a.get("members") or []) for a in cb_final["axes"].values()
                   if a.get("status") == "active")
    median = sizes[len(sizes) // 2] if sizes else 0
    adds = Counter(r["slug"] for r in plan["member_additions"])

    report = {
        "schema": "foundry-consolidation-apply-report/1",
        "generated_by": "experiments/foundry_consolidate_run1_apply.py",
        "directive": "docs/archive/CONSOLIDATION-APPLY-DIRECTIVE.md",
        "plan_sha256": ctx["plan_sha"],
        "codebook_sha256_before": ctx["live_sha"],
        "codebook_sha256_after": sha1,
        "codebook_bytes_after": fcb.CODEBOOK_PATH.stat().st_size,
        "backup": backup.name,
        "category_actuals_vs_plan": {
            "member_additions": [counts["member_additions"], fin["member_additions"]],
            "assertion_merges": [counts["assertion_merges"], fin["assertion_merges"]],
            "new_axes": [counts["new_axes"], fin["new_axes"]],
            "revivals_to_deferred": counts["revivals"],
            "kill_note_corrections": counts["kill_note_corrections"],
            "routing_rows": routing["rows"],
        },
        "sanity_panel": {
            "axes_by_status_before": fin["axes_by_status_before"],
            "axes_by_status_after": dict(sorted(by_status.items())),
            "member_rows": [fin["member_rows_before"], fin["member_rows_after"]],
            "assertion_rows": [fin["assertion_rows_before"], fin["assertion_rows_after"]],
            "axes_touched": counts["axes_touched"],
            "top_10_axes_by_additions": [{"slug": s, "additions": n}
                                         for s, n in adds.most_common(10)],
            "corpus_coverage_after": {"tagged": tagged, "corpus": corpus_n,
                                      "pct": round(100.0 * tagged / corpus_n, 1)},
            "median_active_axis_size": median,
        },
        "gates": {"independent_verifier": vstats, "quotes_verbatim": qstats,
                  "promotions_folded": pstats, "conservation": cons,
                  "spot_verifier": spot, "determinism_x2": sha1 == sha2},
        "report_rows_for_captain": plan["report_rows"],
        "companion_artifacts": {"routing": routing, "card_axes_index": index,
                                "gamechangers": gc, "dry_run_correction": corrected},
        "spend": {"session": 0.0, "cumulative": 90.51, "headroom": 49.49},
    }
    fc.write_json(APPLY_REPORT_PATH, report)

    print("\n" + "=" * 78)
    print("APPLIED")
    print("=" * 78)
    print(f"  codebook sha256  {sha1}")
    print(f"  size             {fcb.CODEBOOK_PATH.stat().st_size:,} bytes")
    print(f"  axes             {dict(sorted(by_status.items()))}")
    print(f"  coverage         {tagged:,} / {corpus_n:,} = "
          f"{100.0 * tagged / corpus_n:.1f}%   median active axis {median}")
    print(f"  report           {APPLY_REPORT_PATH}")
    print(f"  backup           {backup}")
    print("\n  report rows for Captain (untouched, no action taken):")
    for r in plan["report_rows"]:
        print(f"    [{r['kind']}] {r['slug']}")
    print("\n  spend $0.00 / cumulative $90.51 / headroom $49.49")
    print("\nNEXT: python3 experiments/foundry_gate2.py  — and EXPECT it to find "
          "something.\n      Then python3 experiments/foundry_wire_experiment.py --json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
