#!/usr/bin/env python3
"""F0 — the fixture selection freeze (M02 `selection_freeze`).

Fills the null member slots of `oracle_compiler/FIXTURES.json` from populations
the accepted C02 measurement already defines, one recorded deterministic rule
per role, BEFORE any C03 (H-REGION) code or result exists. Read-only: it calls
the frozen AQ4 probe functions and writes one ignored JSON report.

WHAT A RULE MAY LOOK AT: probe measurements (census rows, legacy effect heads,
P1 residue, P3 participants, P4 relation candidates) and printed structure.
Nothing about operation regions -- none exist yet, and M02 forbids choosing a
member "because H-REGION succeeds or fails on it". Ties break by
(oracle_id, stem, occurrence); one card serves one role.

A ROLE NO AQ4 PROBE POPULATION MEASURES goes to the second source M02 allows:
pre-existing production fixtures -- the Gate 2 ground-truth seeds and the
codebook's human-ratified assertions. There a member comes only from a ratified
axis whose DEFINITION expresses the role (a pinned, reviewable mapping), taking
human-asserted members by oracle_id. Text inside an evidence quote never selects
a member: that would be a new text classifier. A role neither source expresses
stays null, with the reason. Filling
it would need a new text classifier, which is a new measurement (V1 P0.2: do
not duplicate or extend the probes under another name).

    python3 experiments/oracle_ingest/f0_select.py            # report + write
    python3 experiments/oracle_ingest/f0_select.py --stdout   # report only
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for rel in ("experiments", "tests/guards/gate2", "tests/guards/probe",
            "benchmarks/aq4/experiments"):
    sys.path.insert(0, str(ROOT / rel))

import foundry_probe as p                    # noqa: E402
import foundry_common as fc                  # noqa: E402
import foundry_qualifier_census as fqc       # noqa: E402
import foundry_shape_extractor as fx         # noqa: E402
import foundry_aq4_probes as aq              # noqa: E402

# interface/1 I1 -- a differing identity is a STOP, never a silent re-measurement.
PINNED = {
    "benchmarks/aq4/experiments/foundry_aq4_probes.py":
        "eec9a4e2aea4c27d74dfffc6d4b82fdcd6f7292bd777aadc2c8625215c7c48f6",
    "config/cr/MTG_Comprehensive_Rules_2026-08-07_LLM.md":
        "ca904dc900ce8e06c240960f937590df431aa2d97ec1569140cc910c56202d8b",
    "data/raw/oracle-cards.jsonl.gz":
        "2be88ba86da7ecbbb541094f28439c4888c5585c9ca8155e097f1cd0b548d872",
}
# The accepted C02 numbers the re-derived population must reproduce.
C02 = {"rows": 2110, "multi": 66, "heads": {1: 2044, 2: 65, 3: 1},
       "exile_return": 53, "p3_multi": 19, "p3_qual": 1041}

OUT = ROOT / "experiments" / "out" / "oracle_ingest" / "f0" / "selection.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_identities() -> dict:
    for rel, want in PINNED.items():
        got = _sha(ROOT / rel)
        if got != want:
            fc.halt(f"pinned input {rel} is {got}, interface/1 pins {want}")
    return dict(PINNED)


def key(row: dict) -> tuple:
    return (row["oracle_id"], row["stem"], row["occurrence"])


# ---------------------------------------------------------------- the rules
# Each rule is a predicate over one census row plus its card; each is proven to
# refuse a rigged input before it is trusted (CLAUDE.md: a guard never shown to
# fail is not a guard).

def simple_one_operation(row, card, per_card_rows) -> bool:
    """One legacy head, zero P1 residue, the card's only census row, and no
    P4 relation candidate anywhere on the card."""
    return (len(aq.effect_heads(row["clause"])) == 1
            and not aq.claim(row["clause"])["residue"]
            and per_card_rows == 1
            and not aq.relation_candidates(card))


def two_sequential(row, card, per_card_rows) -> bool:
    """P2 member with exactly two distinct heads, not the exile + return form
    (that form is the delayed-return role's pressure and the C03 majority)."""
    heads = aq.effect_heads(row["clause"])
    return len(heads) == 2 and len(set(heads)) == 2 and heads != ["exile", "return"]


def _row_line(row, card):
    """The P4 line holding this census clause, or None."""
    low = row["clause"].lower()
    for i, line in enumerate(aq._card_lines(card)):
        if low in line.lower():
            return i, line
    return None


def delayed_return(row, card, per_card_rows) -> bool:
    """An exile census row whose own line carries a P4 coreference candidate,
    delay-marked and in a LATER sentence, where that sentence has a legacy
    `return` head: exile now, return the same referent later. Same-clause
    flicker ("then return") is excluded by requiring the later sentence."""
    if row["stem"] != "exile":
        return False
    found = _row_line(row, card)
    if found is None:
        return False
    li, line = found
    sentences = fx.sentence_spans(line)
    home = next((i for i, s in enumerate(sentences) if row["clause"].lower() in s.lower()),
                None)
    if home is None:
        return False
    for c in aq.relation_candidates(card):
        if (c["line"] == li and c["kind"] == "coreference" and c["delayed"]
                and c["sentence"] > home and c["sentence"] < len(sentences)
                and "return" in aq.effect_heads(sentences[c["sentence"]])):
            return True
    return False


def conditional_second(row, card, per_card_rows) -> bool:
    """P2 member whose clause carries a frozen P4 conditionality marker after
    its first head: the second operation is printed under a condition."""
    heads = aq.effect_heads(row["clause"])
    if len(heads) < 2:
        return False
    low = row["clause"].lower()
    first = aq._HEAD_RE.search(low)
    return any(rx.search(low, first.end()) for _, rx, _ in aq._CONDITION_MARKERS)


def choreography(row, card, per_card_rows) -> bool:
    """P3 member: a qualifier-bearing clause with >=2 restricted participants."""
    return bool(row["tokens"]) and sum(
        1 for x in aq.participants(row["clause"]) if x["restricted"]) >= 2


ROLES = (
    ("simple-one-operation-negative-control", simple_one_operation,
     "census rows (P1/P2 population)"),
    ("two-sequential-operations", two_sequential,
     "P2 multi-head clauses (legacy effect_heads)"),
    ("delayed-return-same-object", delayed_return,
     "census exile rows joined to P4 relation candidates"),
    ("conditional-second-operation", conditional_second,
     "P2 multi-head clauses joined to P4 conditionality markers"),
    ("participant-role-choreography", choreography,
     "P3 qualifier-bearing clauses with >=2 restricted participants"),
)

UNFILLED = {
    "split-destination-selected-set":
        "no AQ4 probe population measures a selected set divided across "
        "destinations; the census lattice, P1-P4 and their marker inventories "
        "carry no such structure (production fixtures not searched in F0)",
    "prior-set-complement-reference":
        "P4's frozen back-reference inventory has no complement form; "
        "selecting one needs a new text classifier, i.e. a new measurement "
        "(production fixtures not searched in F0)",
    "ability-borrowing-inheritance-pressure":
        "no AQ4 probe population measures ability borrowing; M01 classifies "
        "it GENUINELY_MISSING (production fixtures not searched in F0)",
}


CODEBOOK_SHA = "6aa6193f8a457ae4c7884e364f519749a9d68b96f7ecedf3fa903bfa4677426c"
GROUND_TRUTH = ROOT / "tests" / "fixtures" / "ground_truth"

# Role -> the ratified codebook axis whose definition expresses it, with that
# definition's sha256. A judgment about DEFINITIONS, made once, pinned: if the
# axis is renamed, retired or redefined, the run halts rather than follow it.
PRODUCTION_AXIS = {
    "split-destination-selected-set": (
        "rule:library-dig-to-hand",
        "9eb55e81224c9011db866caf5977e9495088d7c04e2fe2614a584c8c0bdd93f5",
        "one selected card to hand, the rest to the library bottom: a selected "
        "set divided across two destinations"),
    "prior-set-complement-reference": (
        "rule:library-dig-to-hand",
        "9eb55e81224c9011db866caf5977e9495088d7c04e2fe2614a584c8c0bdd93f5",
        "'the rest' names the complement of the selected card within the set "
        "looked at before"),
}
PRODUCTION_UNFILLED = {}

# Members the Captain NAMED (Issue #1 comment 5878405103). A naming is
# authority, not a selection rule: it is recorded, and only verified to exist in
# the pinned corpus under the recorded oracle_id and name.
CAPTAIN_NAMED = {
    "ability-borrowing-inheritance-pressure": {
        "ruling": 5878405103,
        "members": (("fcc666bc-6fea-44e0-94bc-462c742db528", "The Book of Vile Darkness",
                     "triggered-ability inheritance from exiled cards; a variant, "
                     "not V1 R2-C's activated-ability case"),
                    ("c259e16f-2a44-4552-8678-815f757a02e8", "Agatha's Soul Cauldron",
                     "activated-ability borrowing from exiled creature cards; V1 R2-C's "
                     "case")),
        "variants": ("triggered-ability-inheritance", "activated-ability-borrowing"),
    },
}


def production_pass(cards, used) -> dict:
    """Fill the roles no probe population measures from production fixtures."""
    cb_path = fc.FOUNDRY_OUT_DIR / "codebook.json"
    if _sha(cb_path) != CODEBOOK_SHA:
        fc.halt(f"codebook is {_sha(cb_path)}, F0 pinned {CODEBOOK_SHA}")
    axes = json.loads(cb_path.read_text(encoding="utf-8"))["axes"]
    p.domain(axes, "status", "active")
    gt_axes = set()
    for f in sorted(GROUND_TRUTH.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for k in ("moves", "seeds", "adds", "merges"):
            gt_axes |= {m.get("to") for m in d.get(k) or []}
        gt_axes |= set(d.get("new_axes") or {})
        gt_axes |= {v["to"] for v in (d.get("renames") or {}).values()}
    gt_axes.discard(None)
    out = {}
    for role, (slug, def_sha, why) in PRODUCTION_AXIS.items():
        axis = axes.get(slug)
        if axis is None or axis.get("status") != "active":
            fc.halt(f"{role}: {slug} is not an active codebook axis")
        got = hashlib.sha256(axis["definition"].encode("utf-8")).hexdigest()
        if got != def_sha:
            fc.halt(f"{role}: {slug} definition moved ({got}); re-review the mapping")
        human = sorted(m["oracle_id"] for m in axis["members"]
                       if any(a.get("class") == "human" for a in m.get("assertions", []))
                       and m["oracle_id"] in cards)
        hit = next((o for o in human if o not in used), None)
        if hit is None:
            out[role] = {"member": None, "reason": f"{slug} has no unused human member"}
            continue
        used.add(hit)
        out[role] = {"member": cards[hit]["name"], "oracle_id": hit,
                     "source_population": f"codebook axis {slug} (human-ratified "
                                          f"assertions; codebook sha256 {CODEBOOK_SHA})",
                     "selection_rule": f"first unused human-asserted member by oracle_id "
                                       f"of the ratified axis whose definition expresses "
                                       f"the role: {why}",
                     "axis_in_gate2_ground_truth": slug in gt_axes,
                     "qualifying_rows": len(human)}
    for role, reason in PRODUCTION_UNFILLED.items():
        out[role] = {"member": None, "reason": reason}
    for role, named in CAPTAIN_NAMED.items():
        for oid, name, _ in named["members"]:
            if oid not in cards or cards[oid]["name"] != name:
                fc.halt(f"{role}: Captain-named {name!r} is not {oid} in the pinned corpus")
        out[role] = {"members": [n for _, n, _ in named["members"]],
                     "oracle_ids": [o for o, _, _ in named["members"]],
                     "captain_ruling": named["ruling"],
                     "notes": {n: why for _, n, why in named["members"]},
                     # Fixture-local labels (Captain, Issue #1): the role holds two
                     # distinct shapes. NOT production tags -- A01's R2-C unit
                     # proposes those, for Captain ratification.
                     "fixture_variants": {n: v for (_, n, _), v in zip(
                         named["members"], named["variants"])},
                     "variants_are_production_vocabulary": False}
    return {"searched": {"gate2_ground_truth_axes": len(gt_axes),
                         "codebook_active_axes": sum(1 for a in axes.values()
                                                     if a.get("status") == "active")},
            "roles": out}


# A rule whose EVERY qualifying row was read and found spurious is recorded
# here with the exact set it covers. If the set moves, the run halts: the
# judgment was made about these rows and no others. Nothing is dropped by name.
REVIEWED_NULL = {
    "conditional-second-operation": {
        "qualifying_oracle_ids": {"16da72a3-d980-4dd8-99f2-8191cce00978",
                                  "2cb98ca9-d7bb-416b-a17e-ee5f8e4d78f2"},
        "reason": "both qualifying clauses get their second head from `cast` in "
                  "'mana spent to cast this spell', a CR 601.2 payment condition "
                  "and not an instruction; the condition governs the only real "
                  "operation. A known false-positive class of both detector paths "
                  "(the legacy boundary rule accepts `to`). No genuine member.",
    },
}


def negative_controls() -> list:
    """Every rule refuses a rigged input it must refuse. Halts otherwise."""
    card = {"name": "Rig", "oracle_text": "Destroy target creature.", "layout": "normal"}
    row = {"oracle_id": "rig", "name": "Rig", "stem": "destroy", "occurrence": 0,
           "clause": "Destroy target creature", "tokens": []}
    two = dict(row, clause="Destroy target creature, then exile target artifact")
    flicker = dict(row, stem="exile",
                   clause="Exile target creature you control, then return that card "
                          "to the battlefield")
    cases = [
        ("simple refuses two heads", simple_one_operation, two, card, 1, False),
        ("simple refuses a second census row", simple_one_operation, row, card, 2, False),
        ("two_sequential refuses one head", two_sequential, row, card, 1, False),
        ("two_sequential refuses exile + return", two_sequential, flicker, card, 1, False),
        ("delayed_return refuses same-clause flicker", delayed_return, flicker,
         {"name": "Rig", "layout": "normal",
          "oracle_text": "Exile target creature you control, then return that card "
                         "to the battlefield."}, 1, False),
        ("conditional_second refuses no marker", conditional_second, two, card, 1, False),
        ("choreography refuses no qualifier", choreography, row, card, 1, False),
    ]
    out = []
    for name, rule, r, c, n, want in cases:
        got = bool(rule(r, c, n))
        if got != want:
            fc.halt(f"negative control failed: {name} (rule returned {got})")
        out.append(name)
    return out


def select() -> dict:
    identities = check_identities()
    p.corpus()                                   # guard A: canonical state
    cards, _, _ = fc.load_corpus_gated()
    rows = fqc.population(cards)
    p.domain(rows, "stem", "destroy", "exile", "bounce")

    # Reconcile with accepted C02 before trusting the population (interface/1 I2).
    heads = {r_key: aq.effect_heads(r["clause"]) for r in rows for r_key in [key(r)]}
    dist = {}
    for h in heads.values():
        dist[min(len(h), 5)] = dist.get(min(len(h), 5), 0) + 1
    multi = [k for k, h in heads.items() if len(h) > 1]
    flick = [k for k, h in heads.items() if h[:4] == ["exile", "return"]]
    qual = [r for r in rows if r["tokens"]]
    p3m = [r for r in qual if choreography(r, None, 0)]
    measured = {"rows": len(rows), "multi": len(multi), "heads": dist,
                "exile_return": len(flick), "p3_multi": len(p3m), "p3_qual": len(qual)}
    if measured != C02:
        fc.halt(f"population does not reproduce accepted C02: {measured} != {C02}")

    per_card = {}
    for r in rows:
        per_card[r["oracle_id"]] = per_card.get(r["oracle_id"], 0) + 1
    used = set()
    selected = {}
    for role, rule, population in ROLES:
        qualifying = [r for r in sorted(rows, key=key)
                      if rule(r, cards[r["oracle_id"]], per_card[r["oracle_id"]])]
        if role in REVIEWED_NULL:
            got = {r["oracle_id"] for r in qualifying}
            if got != REVIEWED_NULL[role]["qualifying_oracle_ids"]:
                fc.halt(f"{role}: qualifying set moved to {sorted(got)}; the recorded "
                        "null judgment covered a different set -- re-review it")
            selected[role] = {"member": None, "source_population": population,
                              "selection_rule": " ".join(rule.__doc__.split()),
                              "qualifying_rows": len(qualifying),
                              "qualifying_members": sorted(r["name"] for r in qualifying),
                              "reason": REVIEWED_NULL[role]["reason"]}
            continue
        hit = next((r for r in qualifying if r["oracle_id"] not in used), None)
        if hit is None:
            selected[role] = {"member": None, "source_population": population,
                              "selection_rule": rule.__doc__.split("\n\n")[0].strip(),
                              "reason": "no row satisfies the rule"}
            continue
        used.add(hit["oracle_id"])
        selected[role] = {
            "member": hit["name"], "oracle_id": hit["oracle_id"],
            "census_key": [hit["stem"], hit["occurrence"]],
            "source_population": population,
            "selection_rule": " ".join(rule.__doc__.split()),
            "qualifying_rows": len(qualifying),
        }
    production = production_pass(cards, used)
    return {"schema": "oracle-compiler-f0-selection/0", "inputs": identities,
            "production_fixtures": production,
            "reconciled_with_c02": measured | {"heads": {str(k): v for k, v in
                                                         sorted(dist.items())}},
            "negative_controls": negative_controls(),
            "tie_break": "(oracle_id, stem, occurrence); one card per role, roles in listed order",
            "selected": selected, "unfilled": UNFILLED}


def main(argv) -> int:
    report = select()
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if "--stdout" not in argv:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
