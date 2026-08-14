#!/usr/bin/env python3
"""SEMANTIC LOCALITY BACKFILL — the one-shot migration that addresses existing
assertions. Step 4 of the locality roadmap, resolving FL-2.

CAPTAIN-AUTHORISED CODEBOOK MUTATION. Rides the backup law.

WHY THIS IS A NEW EXECUTOR AND NOT `foundry_membership_move.py`
---------------------------------------------------------------
That script moves MEMBERS BETWEEN AXES. Its spec shape is
`new_axes / moves / definition_edits / scope_edits / adds / seeds / drops /
quote_edits`, and there is **no assertion-field edit anywhere in it**. Its one
operation that touches an assertion at all, `quote_edits`, rewrites the
evidence text — the opposite of what this migration does. Reusing it would have
meant adding a mutation verb to a tool whose every existing gate is written
around member counts, and the member count here never changes by one.

It is, however, the STANDARD this is built to: declares nothing itself, gates
everything before a byte is written, determinism ×2, atomic write with temp
re-lint, and a conservation invariant asserted rather than eyeballed.

WHAT IS BACKFILLED, AND WHAT DELIBERATELY IS NOT
------------------------------------------------
**Only where `resolve()` returns OWNER.** Everything else stays unaddressed and
is REPORTED, never guessed — the ratification rejected converting a 98.95%
automatic win into a pile of hand rulings.

Measured 2026-08-13, and re-derived on every run rather than carried forward:

    7,930 assertions on active axes
    7,808 addressed        (semantic OWNER)
      122 left unaddressed (39 SPAN · 40 AMBIGUOUS · 4 UNRESOLVED · 39 quoteless)

**The remainder is 122, not the 83 the implementation handoff sec.6 quotes.**
That sentence enumerates "40 ambiguous + 4 unresolved + 39 quoteless" and omits
the **39 SPAN** rows, which `resolve()` also declines to address. Span and
quoteless are both 39, which is almost certainly how one got read for both. The
backfill RULE in that section is correct and unchanged; only its arithmetic
complement was wrong.

**Tombstone axes are out of scope.** Only `status == "active"` axes are
addressed. A renamed axis RETAINS its members (CDR-09), so its assertions are
live copies on the new slug and get addressed there; writing addresses onto the
tombstone too would put a derived, snapshot-relative field on a historical
record nothing re-derives.

THE CONSERVATION INVARIANT
--------------------------
Asserted, not eyeballed, and it is the strong form: strip `locality` from every
assertion in the RESULT and the codebook must be **byte-identical** to the
input. That single check subsumes "assertion count unchanged", "no quote
touched", "no member moved", "no axis renamed" and "no key reordered", and it
cannot be satisfied by a mutation that got lucky on counts.

    python3 experiments/foundry_locality_backfill.py --plan
    python3 experiments/foundry_locality_backfill.py --dry-run
    python3 experiments/foundry_locality_backfill.py --execute --go-sha256 <hash>
    python3 experiments/foundry_locality_backfill.py --selftest
"""
import sys
import copy
import json
import hashlib
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc          # noqa: E402
import foundry_codebook as fcb       # noqa: E402
import foundry_locality as fl        # noqa: E402

PLAN_PATH = fc.FOUNDRY_OUT_DIR / "locality-backfill-plan.json"


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------

def build_plan(cards, codebook: dict) -> dict:
    """Derives the full backfill, deciding nothing a human has to review.

    A row is `[axis, oracle_id, class, source_ref, [face, paragraph]]`.
    `(class, source_ref)` is unique per member — `foundry_codebook.lint` and
    `merge_assertion` both enforce it — so those four fields address exactly
    one assertion, and the applier halts if they ever address zero or two.
    """
    rows, skipped = [], {"SPAN": 0, "AMBIGUOUS": 0, "UNRESOLVED": 0,
                         "QUOTELESS": 0, "NO_CARD": 0}
    per_axis = {}
    for slug in sorted(codebook["axes"]):
        axis = codebook["axes"][slug]
        if axis.get("status") != "active":
            continue
        n_ok = n_skip = 0
        for member in axis.get("members") or []:
            oid = member["oracle_id"]
            card = cards.get(oid)
            for a in member["assertions"]:
                q = a.get("quote")
                if not q:
                    skipped["QUOTELESS"] += 1
                    n_skip += 1
                    continue
                if card is None:
                    skipped["NO_CARD"] += 1
                    n_skip += 1
                    continue
                r = fl.resolve(card, q)
                if r["status"] != fl.OWNER:
                    skipped[r["status"]] += 1
                    n_skip += 1
                    continue
                rows.append([slug, oid, a["class"], a["source_ref"],
                             list(r["owner"])])
                n_ok += 1
        if n_ok or n_skip:
            per_axis[slug] = {"addressed": n_ok, "unaddressed": n_skip}

    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    plan = {
        "generated_by": "experiments/foundry_locality_backfill.py --plan",
        "ruling": "docs/B-MIGRATION-DISCOVERY.md sec.11 (canonical, tracked)",
        "corpus_ref": fcb.corpus_ref_current(),
        "scope": "assertions on status=='active' axes only",
        "addressed": len(rows),
        "unaddressed": sum(skipped.values()),
        "unaddressed_by_reason": dict(sorted(skipped.items())),
        "per_axis": per_axis,
        "rows": rows,
    }
    return plan


def plan_sha256(plan: dict) -> str:
    """Hash of the plan's DECIDING content, not of its presentation.

    Deliberately excludes nothing — the whole payload is hashed — but is
    computed from a canonical serialization so that a re-plan producing the
    same decisions produces the same hash regardless of dict insertion order.
    """
    return hashlib.sha256(
        json.dumps(plan, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


# --------------------------------------------------------------------------
# apply
# --------------------------------------------------------------------------

def apply_plan(codebook: dict, plan: dict) -> dict:
    """Returns a NEW codebook with `locality` added to the planned assertions.

    Pure: the input is never mutated, so the caller can run this twice and
    compare, and can strip-and-compare against the untouched original.
    """
    cb = copy.deepcopy(codebook)
    axes = cb["axes"]
    seen = set()
    for slug, oid, cls, sref, coord in plan["rows"]:
        key = (slug, oid, cls, sref)
        if key in seen:
            fc.halt(f"plan addresses {key} twice — a duplicate row would make "
                    f"the applied result depend on row order; nothing written")
        seen.add(key)

        entry = axes.get(slug)
        if entry is None:
            fc.halt(f"{slug}: plan names an axis that is not in the codebook")
        if entry.get("status") != "active":
            fc.halt(f"{slug}: status is {entry.get('status')!r}, but the plan's "
                    f"declared scope is active axes only")
        member = fcb.member_by_id(entry, oid)
        if member is None:
            fc.halt(f"{slug}/{oid}: plan names a non-member — the plan and the "
                    f"live codebook disagree; nothing written")
        matches = [a for a in member["assertions"]
                   if a["class"] == cls and a["source_ref"] == sref]
        if len(matches) != 1:
            fc.halt(f"{slug}/{oid}: (class={cls!r}, source_ref={sref!r}) "
                    f"addresses {len(matches)} assertions, expected exactly 1")
        a = matches[0]
        if "locality" in a:
            fc.halt(f"{slug}/{oid}: assertion already carries a locality "
                    f"address. This migration ADDS a field and never rewrites "
                    f"one; re-addressing after a corpus change is a different "
                    f"operation with a different conservation rule.")
        # Rebuild in canonical order rather than assigning in place. `locality`
        # is last in ASSERTION_KEY_ORDER so a plain assignment happens to be
        # correct today -- and would silently stop being correct the moment
        # another optional key is appended after it. lint checks key ORDER, so
        # "happens to be correct" is not a standard worth relying on.
        rebuilt = {k: a[k] for k in fcb.ASSERTION_KEY_ORDER if k in a}
        rebuilt["locality"] = fcb.normalize_locality(coord)
        a.clear()
        a.update({k: rebuilt[k] for k in fcb.ASSERTION_KEY_ORDER
                  if k in rebuilt})
    return cb


def strip_locality(codebook: dict) -> dict:
    """The codebook with every `locality` key removed. The conservation probe."""
    cb = copy.deepcopy(codebook)
    for entry in cb["axes"].values():
        for member in entry.get("members") or []:
            for a in member.get("assertions") or []:
                a.pop("locality", None)
    return cb


def count_localities(codebook: dict) -> int:
    return sum(1 for e in codebook["axes"].values()
               for m in (e.get("members") or [])
               for a in m["assertions"] if "locality" in a)


def count_assertions(codebook: dict) -> int:
    return sum(len(m["assertions"]) for e in codebook["axes"].values()
               for m in (e.get("members") or []))


def count_members(codebook: dict) -> int:
    return sum(len(e.get("members") or []) for e in codebook["axes"].values())


def verify(before: dict, after: dict, plan: dict) -> dict:
    """Every gate, before a byte is written. Halts on the first violation.

    Reports ADDED and REMOVED separately. A net delta would let a migration
    that dropped 5 addresses and added 5 elsewhere report a clean zero.
    """
    # 1. THE STRONG CONSERVATION INVARIANT. Strip the new field back off and
    #    the result must be byte-identical to the input. Subsumes the count
    #    checks below, which are kept because they NAME what went wrong.
    a_bytes = fcb._serialize(before)
    b_bytes = fcb._serialize(strip_locality(after))
    if a_bytes != b_bytes:
        fc.halt("CONSERVATION FAILED: stripping `locality` from the result does "
                "not reproduce the input byte-for-byte. Something other than "
                "the new optional key changed; nothing written.")

    # 2. Named counts, so a failure above is diagnosable rather than just fatal.
    for label, fn in (("assertions", count_assertions),
                      ("members", count_members),
                      ("axes", lambda cb: len(cb["axes"]))):
        if fn(before) != fn(after):
            fc.halt(f"CONSERVATION FAILED: {label} {fn(before)} -> {fn(after)}. "
                    f"This migration adds one optional key and changes nothing "
                    f"else; nothing written.")

    # 3. Added and removed, separately.
    def keyset(cb):
        out = {}
        for slug, e in cb["axes"].items():
            for m in (e.get("members") or []):
                for a in m["assertions"]:
                    if "locality" in a:
                        out[(slug, m["oracle_id"], a["class"],
                             a["source_ref"])] = tuple(a["locality"])
        return out

    was, now = keyset(before), keyset(after)
    added = sorted(set(now) - set(was))
    removed = sorted(set(was) - set(now))
    changed = sorted(k for k in set(was) & set(now) if was[k] != now[k])
    if removed:
        fc.halt(f"{len(removed)} address(es) REMOVED by a migration that only "
                f"adds. First: {removed[0]}; nothing written.")
    if changed:
        fc.halt(f"{len(changed)} address(es) MODIFIED by a migration that only "
                f"adds. First: {changed[0]}; nothing written.")
    if len(added) != plan["addressed"]:
        fc.halt(f"the plan declares {plan['addressed']} addresses but "
                f"{len(added)} were added; nothing written.")

    # 3b. THE RESULT MUST EQUAL THE PLAN, COORDINATE BY COORDINATE — not merely
    #     match it in cardinality.
    #
    #     `changed` above is STRUCTURALLY DEAD for this migration and its
    #     negative control is what proved it: `before` carries zero addresses,
    #     so `set(was) & set(now)` is empty and no coordinate can ever differ
    #     from a value that was never there. NC3 mutated a stored coordinate by
    #     +99 and `verify` returned clean. A count of added rows cannot see a
    #     substitution — the same shape as the `type_vocabulary` halt-guard
    #     that asserted `len() >= 15` while every list's last member was wrong.
    #     `changed` is KEPT, because a re-address migration would have a
    #     non-empty `was` and would need it.
    declared = {(slug, oid, cls, sref): tuple(coord)
                for slug, oid, cls, sref, coord in plan["rows"]}
    if now != declared:
        mismatched = sorted(k for k in set(now) & set(declared)
                            if now[k] != declared[k])
        fc.halt(f"the applied result does not match the plan: "
                f"{len(set(now) - set(declared))} unplanned, "
                f"{len(set(declared) - set(now))} missing, "
                f"{len(mismatched)} at a different coordinate"
                + (f" (first: {mismatched[0]} plan={declared[mismatched[0]]} "
                   f"got={now[mismatched[0]]})" if mismatched else "")
                + "; nothing written.")

    # 4. The result must lint. write_codebook_atomic re-lints the temp too, so
    #    this is the EARLY copy of that check -- it fails before the backup is
    #    consumed rather than after.
    stats = fcb.lint_or_halt(after, "codebook (post-backfill, in memory)")

    # 5. Every address must still RESOLVE to the assertion's own quote. The
    #    plan derived them, so this re-derivation is a second measurement path
    #    over the applied artifact rather than over the plan.
    return {"added": len(added), "removed": len(removed),
            "changed": len(changed), "lint": stats}


def reverify_against_corpus(cards, after: dict) -> dict:
    """SECOND MEASUREMENT PATH: re-resolve every stored address from the
    APPLIED codebook and confirm it matches what the resolver says today.

    The plan and the applier share `fl.resolve`, so agreeing with the plan
    proves only that the applier copied correctly. This reads the finished
    artifact and asks the resolver again, from the quote that is actually
    stored next to the address.
    """
    ok = bad = 0
    problems = []
    for slug, e in sorted(after["axes"].items()):
        if e.get("status") != "active":
            continue
        for m in (e.get("members") or []):
            card = cards.get(m["oracle_id"])
            for a in m["assertions"]:
                if "locality" not in a:
                    continue
                r = fl.resolve(card, a["quote"]) if card else {
                    "status": fl.UNRESOLVED, "owner": None}
                if r["status"] == fl.OWNER and list(r["owner"]) == a["locality"]:
                    ok += 1
                else:
                    bad += 1
                    if len(problems) < 5:
                        problems.append((slug, m["oracle_id"], a["locality"],
                                         r["status"]))
    if bad:
        fc.halt(f"{bad} stored address(es) do not re-resolve to their own "
                f"quote. First: {problems}. The artifact contradicts the "
                f"resolver that produced it.")
    return {"reresolved_ok": ok}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _load_plan():
    if not PLAN_PATH.exists():
        fc.halt(f"{PLAN_PATH} not found — run --plan first")
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def cmd_plan(cards):
    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook (pre-plan)")
    once = build_plan(cards, cb)
    twice = build_plan(cards, cb)
    if json.dumps(once, sort_keys=True) != json.dumps(twice, sort_keys=True):
        fc.halt("determinism gate FAILED — two plan builds differ")
    sha = plan_sha256(once)
    fc.write_json(PLAN_PATH, once)
    print(f"determinism ×2 byte-identical")
    print(f"wrote {PLAN_PATH}")
    print(f"\nplan sha256 {sha}")
    print(f"  addressed        : {once['addressed']:,}")
    print(f"  left unaddressed : {once['unaddressed']:,}")
    for k, n in once["unaddressed_by_reason"].items():
        if n:
            print(f"      {k:12}: {n:>4}")
    print(f"\n  axes touched     : {len(once['per_axis']):,}")
    top = sorted(once["per_axis"].items(),
                 key=lambda kv: -kv[1]["addressed"])[:6]
    print("  largest families :")
    for slug, d in top:
        print(f"      {slug:44} {d['addressed']:>4} addressed, "
              f"{d['unaddressed']} not")
    return 0


def cmd_run(cards, execute: bool, go_sha: str):
    plan = _load_plan()
    sha = plan_sha256(plan)
    print(f"plan sha256 {sha}  ({plan['addressed']:,} rows)")

    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook (pre-backfill)")
    live_sha = fcb.sha256_of(fcb.CODEBOOK_PATH)
    print(f"codebook sha256 {live_sha}")

    # THE PLAN MUST STILL DESCRIBE THIS CODEBOOK. A plan built against an older
    # file would apply addresses derived from evidence that has since moved.
    fresh = build_plan(cards, cb)
    if plan_sha256(fresh) != sha:
        fc.halt(f"the plan on disk no longer reproduces from the live codebook "
                f"and corpus (fresh sha {plan_sha256(fresh)}). Re-run --plan "
                f"and re-review; nothing written.")
    print("plan re-derives from live state: OK")

    once = apply_plan(cb, plan)
    twice = apply_plan(cb, plan)
    if fcb._serialize(once) != fcb._serialize(twice):
        fc.halt("determinism gate FAILED — two applications differ")
    print(f"determinism ×2 byte-identical ({len(fcb._serialize(once)):,} bytes)")

    stats = verify(cb, once, plan)
    print(f"CONSERVATION OK — stripping `locality` reproduces the input "
          f"byte-for-byte")
    print(f"  addresses added   : {stats['added']:,}")
    print(f"  addresses removed : {stats['removed']}")
    print(f"  addresses changed : {stats['changed']}")
    print(f"  lint              : {stats['lint']['axes']} axes, "
          f"{stats['lint']['members']} members, "
          f"{stats['lint']['assertions']} assertions")

    rr = reverify_against_corpus(cards, once)
    print(f"  re-resolved from the applied artifact: "
          f"{rr['reresolved_ok']:,}/{stats['added']:,} agree")

    before_addr, after_addr = count_localities(cb), count_localities(once)
    print(f"  addressed assertions: {before_addr:,} -> {after_addr:,}")
    print(f"  UNADDRESSED remainder: {count_assertions(once) - after_addr:,} "
          f"(includes {count_assertions(once) - plan['addressed'] - plan['unaddressed']:,} "
          f"on non-active tombstone axes, out of scope by declaration)")

    if not execute:
        print("\nDRY RUN — nothing written.")
        return 0

    if go_sha != sha:
        fc.halt(f"--go-sha256 {go_sha!r} does not match the plan's sha256 "
                f"{sha!r}. The go token names the exact plan being authorised; "
                f"nothing written.")

    backup = fcb.backup_codebook("pre-locality-backfill")
    digest = fcb.write_codebook_atomic(fcb.CODEBOOK_PATH, once, "codebook.json")
    print(f"\nwrote {fcb.CODEBOOK_PATH}")
    print(f"  sha256 before : {live_sha}")
    print(f"  sha256 after  : {digest}")
    print(f"  backup        : {backup}")
    print(f"\nREVERT: cp {backup} {fcb.CODEBOOK_PATH}")
    return 0


def cmd_selftest(cards):
    """Negative controls. Breaks each gate on purpose; nothing is written."""
    cb = fcb.load_codebook()
    # AFTER the migration has run, the live codebook is already addressed and
    # `apply_plan` correctly refuses it -- which would leave this tool's eight
    # negative controls permanently unrunnable, i.e. a set of guards nobody can
    # ever demonstrate again. The controls are about the MIGRATION's gates, so
    # they run against the pre-migration shape, reconstructed by stripping.
    # Nothing is written either way.
    already = count_localities(cb)
    if already:
        print(f"note: the live codebook already carries {already:,} addresses; "
              f"running the controls against a stripped copy of it, which is "
              f"the state the migration gates were written for.\n")
        cb = strip_locality(cb)
    plan = build_plan(cards, cb)
    good = apply_plan(cb, plan)
    caught = []

    def expect_halt(label, fn):
        try:
            fn()
        except SystemExit:
            caught.append(label)
            print(f"    caught: {label}")
            return
        print(f"    NOT CAUGHT: {label}")

    print("selftest — every gate broken on purpose:")

    # NC1 -- a mutation that also changes a QUOTE. The count checks all pass;
    # only the strong byte-identity invariant can see it. This is the control
    # that justifies the invariant being written the expensive way.
    def nc1():
        bad = copy.deepcopy(good)
        for e in bad["axes"].values():
            for m in (e.get("members") or []):
                m["assertions"][0]["quote"] = "TAMPERED"
                verify(cb, bad, plan)
                return
    expect_halt("NC1 a tampered quote fails conservation", nc1)

    # NC2 -- an address REMOVED. Added-and-removed are reported separately for
    # exactly this: a net delta would net to zero against a compensating add.
    def nc2():
        bad = copy.deepcopy(good)
        for e in bad["axes"].values():
            for m in (e.get("members") or []):
                for a in m["assertions"]:
                    if "locality" in a:
                        a.pop("locality")
                        verify(cb, bad, plan)
                        return
    expect_halt("NC2 a removed address is caught, not netted", nc2)

    # NC3 -- an address CHANGED to a different coordinate.
    def nc3():
        bad = copy.deepcopy(good)
        for e in bad["axes"].values():
            for m in (e.get("members") or []):
                for a in m["assertions"]:
                    if "locality" in a:
                        a["locality"] = [a["locality"][0], a["locality"][1] + 99]
                        verify(cb, bad, plan)
                        return
    expect_halt("NC3 a modified address is caught", nc3)

    # NC4 -- the plan names a member that is not there.
    def nc4():
        bad_plan = copy.deepcopy(plan)
        bad_plan["rows"][0][1] = "00000000-0000-0000-0000-000000000000"
        apply_plan(cb, bad_plan)
    expect_halt("NC4 a plan row naming a non-member halts the apply", nc4)

    # NC5 -- a duplicate plan row, which would make the result order-dependent.
    def nc5():
        bad_plan = copy.deepcopy(plan)
        bad_plan["rows"].append(list(bad_plan["rows"][0]))
        apply_plan(cb, bad_plan)
    expect_halt("NC5 a duplicate plan row halts the apply", nc5)

    # NC6 -- re-running over an already-addressed codebook. The migration adds
    # and never rewrites, so it must refuse rather than quietly re-address.
    def nc6():
        apply_plan(good, plan)
    expect_halt("NC6 re-applying to an addressed codebook refuses", nc6)

    # NC7 -- a stored address that no longer resolves to its own quote. The
    # second measurement path over the finished artifact.
    def nc7():
        bad = copy.deepcopy(good)
        for e in bad["axes"].values():
            if e.get("status") != "active":
                continue
            for m in (e.get("members") or []):
                for a in m["assertions"]:
                    if "locality" in a:
                        a["locality"] = [a["locality"][0] + 7, 0]
                        reverify_against_corpus(cards, bad)
                        return
    expect_halt("NC7 an address that stops re-resolving is caught", nc7)

    # NC8 -- the go token must name the exact plan.
    def nc8():
        bad_plan = copy.deepcopy(plan)
        bad_plan["rows"] = bad_plan["rows"][:-1]
        if plan_sha256(bad_plan) == plan_sha256(plan):
            fc.halt("sha did not change")
        fc.halt("(control: differing plans hash differently)")
    expect_halt("NC8 a changed plan changes its sha256", nc8)

    print(f"\n  {len(caught)}/8 gates proved they can fail")
    return 0 if len(caught) == 8 else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    g.add_argument("--selftest", action="store_true")
    ap.add_argument("--go-sha256", default=None,
                    help="required with --execute: the plan sha256 being "
                         "authorised")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()
    if args.plan:
        return cmd_plan(cards)
    if args.selftest:
        return cmd_selftest(cards)
    if args.execute and not args.go_sha256:
        fc.halt("--execute requires --go-sha256 <plan hash>. Run --dry-run "
                "first and authorise the exact plan it reports.")
    return cmd_run(cards, args.execute, args.go_sha256)


if __name__ == "__main__":
    sys.exit(main())
