#!/usr/bin/env python3
"""CDR-09 §12a counter-homograph rename walk -- EXECUTOR.

Name-only. Members, definitions, scope, source and parameterization are
untouched by every row; only the slug changes. Old slugs become `renamed`
tombstones pointing at their target (the batch-5/7 precedent in
foundry_reconcile.py: the tombstone RETAINS its members, the new entry carries
them forward).

Preconditions enforced here, on top of the ones run by hand:
  * the live non-conforming set must be SET-IDENTICAL to §12a's 16 -- the walk
    refuses to run against a codebook that has drifted from the ratified list
  * every rename target must itself pass the §8a conformance test
  * no target may collide with an existing slug
  * determinism: the whole transform is applied twice from the same input and
    the two serializations must be byte-identical before anything is installed

Usage:
  python3 experiments/foundry_cdr09_walk.py --dry-run
  python3 experiments/foundry_cdr09_walk.py --execute
"""
import sys
import copy
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402
import foundry_cdr09_derive as derive  # noqa: E402

WALK_REF = "CDR-09 §12a walk (Captain-ratified 2026-08-02, grammar §8a)"

# --- §12a verb-side (3). Targets stated verbatim in the ratified table. -------
VERB_RENAMES = {
    "rule:activated-counter-target-spell": "rule:activated-counters-target-spell",
    "rule:activated-tax-counter-unless-pays": "rule:activated-counters-target-spell-unless-pays",
    "rule:tax-or-counter-spell": "rule:counters-spell-unless-pays",
}

# --- §12a noun-side (10). §12a names the axes and the transform ("gain
# `plus1-`") but not the target strings, so targets are DERIVED by inserting
# `plus1-` immediately before the counter token. That insertion point is
# confirmed by grammar §8a correction 2, which cites the post-walk name
# `cast-trigger-self-plus1-counter-noncreature-spell` verbatim.
NOUN_PLUS1 = [
    "rule:activated-counter-transfer-from-other-creature",
    "rule:attack-trigger-buff-other-attacker-counters",
    "rule:attack-trigger-self-counter-growth",
    "rule:cast-trigger-self-counter-noncreature-spell",
    "rule:death-trigger-counter-transfer",
    "rule:draw-trigger-self-counter-growth",
    "rule:etb-counter-on-other-creature",
    "rule:lifegain-triggered-counter",
    "rule:mass-counter-distribution",
    "rule:self-counter-growth",
]

# --- §12a type-agnostic (3). Targets stated verbatim in the ratified table. ---
ANY_RENAMES = {
    "rule:doubles-counter-placement": "rule:doubles-any-counter-placement",
    "rule:cleanup-counters-on-leaving-battlefield": "rule:cleanup-any-counters-on-leaving-battlefield",
    "rule:counter-removal-as-activation-cost": "rule:any-counter-removal-as-activation-cost",
}


def insert_type_word(slug: str, type_word: str) -> str:
    """Insert a counter TYPE word immediately left of the counter token."""
    ns, rest = slug.split(":", 1)
    tk = rest.split("-")
    idx = [i for i, t in enumerate(tk) if t in derive.COUNTER_TOKENS]
    if len(idx) != 1:
        fc.halt(f"{slug}: expected exactly one counter token to bind, found {len(idx)} — "
                f"the insertion point is ambiguous and this is a ruling, not a guess.")
    tk.insert(idx[0], type_word)
    return f"{ns}:" + "-".join(tk)


def build_rename_table() -> dict:
    table = dict(VERB_RENAMES)
    for slug in NOUN_PLUS1:
        table[slug] = insert_type_word(slug, "plus1")
    table.update(ANY_RENAMES)
    if len(table) != 16:
        fc.halt(f"rename table has {len(table)} rows, expected 16 (§12a: 3 verb + 10 noun + 3 any)")
    if len(set(table.values())) != 16:
        fc.halt("rename table has duplicate targets — two axes cannot rename onto one slug")
    return table


def apply_walk(codebook: dict, table: dict) -> dict:
    """Pure transform: returns a new codebook. Never mutates its argument."""
    cb = copy.deepcopy(codebook)
    axes = cb["axes"]
    for old, new in sorted(table.items()):
        entry = axes.get(old)
        if entry is None:
            fc.halt(f"{old}: not in the codebook — the ratified list and live state disagree")
        if entry.get("status") != "active":
            fc.halt(f"{old}: status is {entry.get('status')!r}, expected 'active'")
        if new in axes:
            fc.halt(f"{old} -> {new}: target slug already exists — collision")

        # New entry: a full copy, name-only change. Members and definition are
        # carried across untouched; that is what makes this walk name-only.
        new_entry = copy.deepcopy(entry)
        new_entry["status"] = "active"
        new_entry["merged_into"] = None
        new_entry.pop("renamed_to", None)
        new_entry["history"] = list(entry.get("history", [])) + [
            {"batch": "cdr09-walk-2026-08-02", "action": "created_via_rename",
             "note": f"renamed from {old}: {WALK_REF}"}]
        axes[new] = new_entry

        # Old entry: tombstone, members retained (foundry_reconcile.py precedent).
        entry["status"] = "renamed"
        entry["renamed_to"] = new
        entry["merged_into"] = None
        entry.setdefault("history", []).append(
            {"batch": "cdr09-walk-2026-08-02", "action": "renamed",
             "note": f"renamed to {new}: {WALK_REF}"})
    return cb


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook (pre-walk)")
    table = build_rename_table()

    # Gate 1: live non-conforming set must equal §12a's 16, exactly.
    live_non = set()
    for slug, entry in cb["axes"].items():
        if entry.get("status") != "active" or not derive.carries_counter_token(slug):
            continue
        rs = derive.RATIFIED_SENSE.get(slug)
        sense = rs[0] if rs else derive.definition_sense(entry)
        if sense.startswith("ambiguous"):
            fc.halt(f"{slug}: sense undecidable — walk cannot proceed (see foundry_cdr09_derive.py)")
        if slug in derive.RATIFIED_NAMES:
            continue
        ok, _ = (derive.verb_conforms(slug) if sense == "verb" else derive.noun_conforms(slug))
        if not ok:
            live_non.add(slug)
    if live_non != set(table):
        fc.halt("live non-conforming set does not match §12a's ratified 16.\n"
                f"  only live : {sorted(live_non - set(table))}\n"
                f"  only §12a : {sorted(set(table) - live_non)}")
    print(f"gate 1 OK — live non-conforming set is set-identical to §12a's 16")

    # Gate 2: every target must itself conform under §8a.
    for old, new in sorted(table.items()):
        entry = cb["axes"][old]
        rs = derive.RATIFIED_SENSE.get(old)
        sense = rs[0] if rs else derive.definition_sense(entry)
        ok, why = (derive.verb_conforms(new) if sense == "verb" else derive.noun_conforms(new))
        if not ok:
            fc.halt(f"rename target {new!r} does not itself satisfy §8a ({sense} sense): {why}")
    print(f"gate 2 OK — all 16 targets satisfy §8a")

    # Gate 3: determinism x2, byte-identical, before anything is installed.
    once = fcb._serialize(apply_walk(cb, table))
    twice = fcb._serialize(apply_walk(cb, table))
    if once != twice:
        fc.halt("determinism gate FAILED — two applications of the walk differ")
    print(f"gate 3 OK — determinism x2 byte-identical ({len(once)} bytes)")

    result = apply_walk(cb, table)
    fcb.lint_or_halt(result, "codebook (post-walk, in memory)")

    print()
    print(f"{'FROM':<58} {'TO':<62} MEM")
    for old, new in sorted(table.items()):
        print(f"{old:<58} {new:<62} {len(cb['axes'][old].get('members', []))}")

    a_before = sum(1 for e in cb["axes"].values() if e.get("status") == "active")
    a_after = sum(1 for e in result["axes"].values() if e.get("status") == "active")
    print()
    print(f"axes        : {len(cb['axes'])} -> {len(result['axes'])}")
    print(f"active      : {a_before} -> {a_after}")
    print(f"members(all): {sum(len(e.get('members', [])) for e in cb['axes'].values())} -> "
          f"{sum(len(e.get('members', [])) for e in result['axes'].values())}")

    if args.dry_run:
        print("\nDRY RUN — nothing written.")
        return

    path = fcb.CODEBOOK_PATH
    before = fcb.sha256_of(path)
    digest = fcb.write_codebook_atomic(path, result, "codebook")
    print(f"\nwrote {path}\n  sha256 before: {before}\n  sha256 after : {digest}")


if __name__ == "__main__":
    main()
