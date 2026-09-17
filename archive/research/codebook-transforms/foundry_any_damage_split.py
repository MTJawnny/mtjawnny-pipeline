#!/usr/bin/env python3
"""Any-damage / combat-damage split -- EXECUTOR (Captain-ratified 2026-08-02).

Ruling: "Any damage deserves its own axis rather than combat damage."
`any-damage-` ratified as DELIVERY vocabulary by Captain, same session.
Record: docs/DAMAGE-DELIVERY-RULING-2026-08-02.md

Unlike the CDR-09 walk this is NOT name-only -- members MOVE between axes,
carrying their assertions (and therefore their evidence quotes) verbatim. No
assertion is rewritten; nothing is re-evidenced; a member that moves arrives
with exactly the proof it had.

The source axis's DEFINITION is also corrected: it currently reads "deals
damage to an opponent", which is the any-damage wording the ruling says must
not live under a `combat-damage-` prefix.

Usage:
  python3 experiments/foundry_any_damage_split.py --dry-run
  python3 experiments/foundry_any_damage_split.py --execute
"""
import sys
import copy
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402

RULING = "Captain-ratified 2026-08-02 (docs/DAMAGE-DELIVERY-RULING-2026-08-02.md)"
BATCH = "any-damage-split-2026-08-02"
SOURCE = "rule:combat-damage-to-player-discard"

# The source definition is any-damage wording sitting under a combat- prefix.
SOURCE_DEFINITION_NEW = (
    "Whenever this creature deals COMBAT damage to a player, that player discards a card. "
    "Combat-restricted by delivery: a trigger that fires on damage of any kind belongs on "
    "the any-damage- family instead."
)

# oracle_id -> destination. Every id is verified present on SOURCE before use.
MOVES = {
    "rule:any-damage-to-player-discard": {
        "members": [
            "244541f6-cbfc-4e89-9156-64e412f745a7",  # Zhang Liao, Hero of Hefei
            "759af941-f6a3-4726-91f2-9b1e4e55ea71",  # Hypnotic Specter
        ],
        "definition": (
            "Whenever a creature deals damage of any kind -- combat or noncombat -- to an "
            "opponent, that player discards a card. Distinct from the combat-damage- family: "
            "this trigger also fires off pingers, direct damage and fight effects."
        ),
        # Matches SOURCE: the discard lands on the opponent.
        "scope": "opponent-stuff",
    },
    "rule:any-damage-to-player-draw": {
        "members": [
            "8d47b78b-11cc-4351-91d6-c891eb63dd98",  # Keen Sense
        ],
        "definition": (
            "Whenever a creature deals damage of any kind -- combat or noncombat -- to an "
            "opponent, its controller may draw a card."
        ),
        # Matches the rule:combat-damage-to-player-loot precedent: the payoff is
        # the controller's, so the scope is `self`, not `opponent-stuff`.
        "scope": "self",
    },
}


def apply_split(codebook: dict) -> dict:
    cb = copy.deepcopy(codebook)
    axes = cb["axes"]
    src = axes.get(SOURCE)
    if src is None:
        fc.halt(f"{SOURCE}: not in the codebook")
    if src.get("status") != "active":
        fc.halt(f"{SOURCE}: status is {src.get('status')!r}, expected 'active'")

    by_id = {m["oracle_id"]: m for m in src.get("members", [])}
    moving = [oid for spec in MOVES.values() for oid in spec["members"]]
    if len(moving) != len(set(moving)):
        fc.halt("an oracle_id is routed to two destinations")
    for oid in moving:
        if oid not in by_id:
            fc.halt(f"{oid}: not a member of {SOURCE} — the ruling and live state disagree")

    for new_slug, spec in sorted(MOVES.items()):
        if new_slug in axes:
            fc.halt(f"{new_slug}: already exists — collision")
        members = [copy.deepcopy(by_id[oid]) for oid in sorted(spec["members"])]
        axes[new_slug] = {
            "definition": spec["definition"],
            "scope": spec["scope"],
            "source": "CAPTAIN",
            "parameterized": False,
            "members": members,
            "status": "active",
            "merged_into": None,
            "history": [{"batch": BATCH, "action": "created",
                         "note": f"split from {SOURCE}: any damage is a distinct delivery "
                                 f"from combat damage. {RULING}"}],
        }

    src["members"] = [m for m in src["members"] if m["oracle_id"] not in set(moving)]
    src["definition"] = SOURCE_DEFINITION_NEW
    src.setdefault("history", []).append(
        {"batch": BATCH, "action": "split",
         "note": f"moved {len(moving)} any-damage member(s) to "
                 f"{', '.join(sorted(MOVES))}; definition corrected from any-damage wording "
                 f"to combat-restricted. {RULING}"})
    return cb


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    cb = fcb.load_codebook()
    fcb.lint_or_halt(cb, "codebook (pre-split)")

    once = fcb._serialize(apply_split(cb))
    twice = fcb._serialize(apply_split(cb))
    if once != twice:
        fc.halt("determinism gate FAILED — two applications differ")
    print(f"determinism x2 byte-identical ({len(once)} bytes)")

    result = apply_split(cb)
    fcb.lint_or_halt(result, "codebook (post-split, in memory)")

    src_before = len(cb["axes"][SOURCE]["members"])
    src_after = len(result["axes"][SOURCE]["members"])
    print(f"\n{SOURCE}: {src_before} -> {src_after} members")
    for slug in sorted(MOVES):
        print(f"  + {slug}: {len(result['axes'][slug]['members'])} members "
              f"(scope={result['axes'][slug]['scope']})")
    a_b = sum(1 for e in cb["axes"].values() if e.get("status") == "active")
    a_a = sum(1 for e in result["axes"].values() if e.get("status") == "active")
    print(f"\nactive axes : {a_b} -> {a_a}")
    print(f"members(all): {sum(len(e.get('members', [])) for e in cb['axes'].values())} -> "
          f"{sum(len(e.get('members', [])) for e in result['axes'].values())}  (must be equal — "
          f"members move, none are created or lost)")

    if args.dry_run:
        print("\nDRY RUN — nothing written.")
        return

    path = fcb.CODEBOOK_PATH
    before = fcb.sha256_of(path)
    digest = fcb.write_codebook_atomic(path, result, "codebook")
    print(f"\nwrote {path}\n  sha256 before: {before}\n  sha256 after : {digest}")


if __name__ == "__main__":
    main()
