#!/usr/bin/env python3
"""AQ4 BENCHMARK — CROSS-CARD PAIRING PROTOCOL (contract §20 B/C/E, packet 3b).

WHAT THIS IS AND IS NOT
-----------------------
§20's B1-B4, C1, DISCOVERY-1 and E1 are CROSS-CARD questions phrased over two
cards. The committed cohorts are flat lists of oracle_ids and bind no card to a
counterpart, so those questions had no instantiation. This module freezes the
Captain-ratified pairing protocol that supplies one.

It does NOT:
  · write an answer of any kind (§11 of the packet directive);
  · draw, seed or reveal the blind holdout;
  · materialize the RESERVED half of cohort 6 (see THE SOURCING RULE);
  · encode a candidate, mint vocabulary, or touch production.

THE SOURCING RULE — READ BEFORE ADDING A FUNCTION
-------------------------------------------------
Identities come from the COMMITTED PUBLIC COHORT FILES and from nowhere else.
`build_cohorts()` and `family_open_reserved()` are never called here, so no
reserved cohort-6 set is computed in this process at any point. That is a
STRUCTURAL guarantee rather than a filter applied afterwards: a filter can only
remove what it already computed, and computing the reserved half in order to
exclude it is the thing being forbidden. `PC5` rigs it.

WHY UNORDERED PAIRS
-------------------
C1 (strict replacement) is directional -- "can B replace A?" is not "can A
replace B?". Both directions derive from ONE unordered pair by recording a
per-direction verdict on the answer, so directed storage would double the pair
count for zero additional information. Captain ratified UNORDERED.

WHY NO CAP, TOP-N OR THRESHOLD
------------------------------
Every tranche emits what its partition yields. A cap would be exactly the
tuning knob this repository's engine rules forbid ("every scoring constant is a
ratified ruling, not a tuning knob"), and it would silently decide which cards
get compared. `PC4` asserts the count identity that a cap would break.

THE FOUR TRANCHES (Captain-ratified, frozen)
--------------------------------------------
  PAIR_K_CHAIN  semantics-free control. Within each published class, keyed
                order, adjacent pairs. Shares only 6 pairs with the S tranches,
                so a verdict holding on K and S together is not a
                stratification artifact.
  S0            same delivery token AND same action family -- the closest
                pairs; instantiates B1 (equal despite different wording).
  S1            same delivery token, action family DIFFERS -- B2, B3, C1.
  S2            same action family, delivery token DIFFERS -- B4, DISCOVERY-1.

Both S coordinates are pre-candidate substrate: grammar §2's ratified DELIVERY
table and the CR 701 keyword-action list parsed at run time. Neither is
expressible in OCC-FACET or MIN-IR terms, and both are already the
pre-registered cohort-4 stratification -- so the tranches decide WHICH cards are
compared, never HOW.

BLIND EXTENSIBILITY
-------------------
Both coordinates are computed from card text by frozen code, so the same
functions applied to a revealed holdout yield strata with no new decision. That
only holds if the INPUTS are pinned too: `reproducibility_pins()` records the
corpus ref, the CR edition and the parsed §2 DELIVERY vocabulary. A CR refresh
moved keyword names 193 -> 194 as recently as the last one, so an unpinned rule
is not reproducible at packet 9.
"""
import sys
import json
import glob
import hashlib
import argparse
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
sys.path.insert(0, str(EXPERIMENTS))
sys.path.insert(0, str(HERE))

import foundry_common as fc              # noqa: E402
import foundry_codebook as fcb           # noqa: E402
import foundry_cr as CR                  # noqa: E402
import foundry_shape_extractor as fx     # noqa: E402
import aq4_population as ap              # noqa: E402

COHORT_DIR = HERE / "cohorts"
PAIR_PATH = HERE / "pairs-open.json"

#: Domain-separated keying salts, FROZEN VERBATIM. Every tranche keys its own
#: ordering, so two tranches drawing from the same group cannot pair the same
#: cards by accident of a shared order.
#:
#: THE SALT STRING IS LOAD-BEARING AND MUST NOT BE TIDIED. Greedy contrast
#: matching (S1/S2) walks the keyed order and takes the first eligible partner,
#: so a different salt yields a different — equally valid — matching with a
#: different leftover count. Measured while freezing this module: normalizing
#: the null key from `None` to the empty string moved S1 from 127 to 126 pairs
#: and the K-vs-S overlap from 6 to 4. These salts are the ones the packet-3b
#: audit Captain ruled on was measured with, so they are reproduced exactly.
#: A "cleanup" of these strings silently re-draws the pair set.
K_SALT = "aq4-pair-k"
S_SALT = "aq4-pair-s"
S_TRANCHE_SALT = {
    "S0": "S0-same-stratum",
    "S1": "S1-same-delivery-diff-action",
    "S2": "S2-same-action-diff-delivery",
}

TRANCHES = ("PAIR_K_CHAIN", "S0", "S1", "S2")


def _label(tranche: str, key) -> str:
    """The frozen keying salt for one group. `key` is rendered with `str()`,
    including `None` -> "None": this is a HASH SALT for domain separation, not
    a reported stratum label, so sampling.json's "null is not vocabulary" rule
    (which governs printed stratum names) does not apply and must not be
    applied here — doing so re-draws the matching, as measured above.
    """
    if tranche == "PAIR_K_CHAIN":
        return f"{K_SALT}\x00{key}"
    return f"{S_SALT}\x00{S_TRANCHE_SALT[tranche]}\x00{key}"

#: Which §20 questions each tranche can legitimately instantiate. Recorded here
#: because a tranche whose questions are unstated becomes a pair list nobody
#: knows what to do with.
TRANCHE_QUESTIONS = {
    "PAIR_K_CHAIN": ["control — semantics-free; any question, as the "
                     "stratification-artifact check"],
    "S0": ["B1"],
    "S1": ["B2", "B3", "C1"],
    "S2": ["B4", "DISCOVERY-1"],
}


# ==========================================================================
# SOURCING — published open identities only
# ==========================================================================

def published_classes() -> dict:
    """{class_id: (cohort, [oracle_id])} from the COMMITTED cohort files.

    The only identity source in this module. Reading the files rather than
    rebuilding the cohorts is what makes reserved non-exposure structural.
    """
    out = {}
    files = sorted(glob.glob(str(COHORT_DIR / "cohort-*.json")))
    if not files:
        fc.halt(f"no committed cohort files under {COHORT_DIR} — pairing reads "
                f"published identities and never rebuilds them.")
    for f in files:
        payload = json.loads(Path(f).read_text(encoding="utf-8"))
        for cl in payload["classes"]:
            out[cl["class_id"]] = (payload["cohort"], sorted(cl["oracle_ids"]))
    return dict(sorted(out.items()))


def open_exemplars(classes: dict) -> list:
    return sorted({o for _, ids in classes.values() for o in ids})


# ==========================================================================
# THE FROZEN TRANCHE RULES
# ==========================================================================

def _pair(a: str, b: str) -> tuple:
    """An unordered pair, canonicalized so {a,b} and {b,a} are one value."""
    return (a, b) if a <= b else (b, a)


def chain_pairs(ids: list, label: str) -> list:
    """Adjacent pairs in keyed order. floor(n/2) pairs; an odd tail is left
    unpaired rather than wrapped.

    NOT a ring. A ring would wrap the last card onto the first, which emits a
    SELF-PAIR on a 1-member class and a DUPLICATE unordered pair on a 2-member
    class. Captain ratified the chain and the singleton is rescued by S
    instead -- see `PC3`.
    """
    ordered = ap.hash_order(label, sorted(ids))
    return [_pair(ordered[i], ordered[i + 1])
            for i in range(0, len(ordered) - 1, 2)]


def contrast_pairs(ids: list, label: str, coord) -> list:
    """Greedy deterministic matching of cards that DIFFER on `coord`.

    Walk the keyed order; for each still-unused card take the first still-unused
    later card whose `coord` value differs. Deterministic because the walk order
    is the keyed order and the choice is always "first eligible", with no
    scoring and no tie-break of its own.
    """
    ordered = ap.hash_order(label, sorted(ids))
    used, out = set(), []
    for a in ordered:
        if a in used:
            continue
        for b in ordered:
            if b in used or b == a or coord(b) == coord(a):
                continue
            out.append(_pair(a, b))
            used.add(a)
            used.add(b)
            break
    return out


def build_pairs(classes: dict, delivery: dict, action: dict) -> dict:
    """{tranche: [pair]} under the four frozen rules."""
    out = {}

    # -- PAIR_K_CHAIN: within each published class, semantics-free ----------
    k = []
    for cid, (_cohort, ids) in classes.items():
        k.extend(chain_pairs(ids, _label("PAIR_K_CHAIN", cid)))
    out["PAIR_K_CHAIN"] = k

    ids_all = open_exemplars(classes)

    # -- S0: same delivery AND same action ---------------------------------
    g0 = collections.defaultdict(list)
    for o in ids_all:
        g0[(delivery[o], action[o])].append(o)
    s0 = []
    for key, members in sorted(g0.items(), key=lambda kv: str(kv[0])):
        if len(members) >= 2:
            s0.extend(chain_pairs(members, _label("S0", key)))
    out["S0"] = s0

    # -- S1: delivery held, action differs ---------------------------------
    g1 = collections.defaultdict(list)
    for o in ids_all:
        g1[delivery[o]].append(o)
    s1 = []
    for key, members in sorted(g1.items(), key=lambda kv: str(kv[0])):
        s1.extend(contrast_pairs(members, _label("S1", key),
                                 lambda o: action[o]))
    out["S1"] = s1

    # -- S2: action held, delivery differs ---------------------------------
    g2 = collections.defaultdict(list)
    for o in ids_all:
        g2[action[o]].append(o)
    s2 = []
    for key, members in sorted(g2.items(), key=lambda kv: str(kv[0])):
        s2.extend(contrast_pairs(members, _label("S2", key),
                                 lambda o: delivery[o]))
    out["S2"] = s2

    return out


# ==========================================================================
# PINS — what makes the rule reproducible against a future corpus / CR
# ==========================================================================

def reproducibility_pins() -> dict:
    """The three inputs Captain ratified as pinned.

    `grammar_section_2` hashes the PARSED §2 DELIVERY vocabulary, not the raw
    markdown bytes. The parse is what pairing depends on, it is derived rather
    than transcribed, and it is stable under prose edits to a section whose
    table did not move. Hashing bytes would churn the pin on an unrelated
    sentence and teach the next session to ignore it.
    """
    tokens = fx.ratified_delivery_tokens()
    blob = json.dumps(tokens, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)
    if not tokens:
        fc.halt("grammar §2's DELIVERY vocabulary parsed EMPTY. Pinning an "
                "empty vocabulary would freeze a rule that groups every card "
                "into one stratum.")
    return {
        "corpus_ref": fcb.corpus_ref_current(),
        "cr_edition": CR.CR_PATH.name,
        "cr_sha256": hashlib.sha256(CR.CR_PATH.read_bytes()).hexdigest(),
        "grammar_section_2_delivery_tokens": len(tokens),
        "grammar_section_2_sha256": hashlib.sha256(blob.encode()).hexdigest(),
        "_what": "Both S coordinates derive from these. A CR refresh moved "
                 "keyword names 193 -> 194 last time, so an unpinned pairing "
                 "rule is not reproducible at packet 9.",
    }


# ==========================================================================
# BUILD
# ==========================================================================

def gather_substrate(ids: list, g: dict = None) -> tuple:
    """(delivery, action) per open exemplar, from the SAME facts the cohorts
    were built from. Re-deriving them here would be the recorded
    re-implementation probe defect."""
    g = g or ap.gather()
    facts = g["facts"]
    missing = [o for o in ids if o not in facts]
    if missing:
        fc.halt(f"{len(missing)} published open exemplar(s) are absent from the "
                f"gated candidate universe, e.g. {missing[:3]!r}. The pairing "
                f"substrate cannot be derived for a card the corpus gate drops.")
    return ({o: facts[o]["delivery_token"] for o in ids},
            {o: facts[o]["action_family"] for o in ids})


def build(write: bool = False, g: dict = None) -> dict:
    classes = published_classes()
    ids = open_exemplars(classes)
    delivery, action = gather_substrate(ids, g)
    tranches = build_pairs(classes, delivery, action)

    union = sorted({p for ts in tranches.values() for p in ts})
    covered = {o for p in union for o in p}

    _assert_pairing_invariants(classes, ids, tranches, union, covered)

    payload = {
        "_what": "Frozen cross-card pairing view over the PUBLISHED OPEN "
                 "benchmark exemplars (contract §20 B/C/E). Captain-ratified "
                 "packet 3b. Contains no answer of any kind.",
        "_law": "Unordered pairs. C1's direction is recorded on the ANSWER as a "
                "per-direction verdict, never by storing the pair twice.",
        "packet": "3b",
        "storage": "unordered",
        "tranches_frozen": list(TRANCHES),
        "tranche_questions": TRANCHE_QUESTIONS,
        "reproducibility_pins": reproducibility_pins(),
        "identity_source": "committed cohort-*.json only; build_cohorts and "
                           "family_open_reserved are never called, so no "
                           "reserved cohort-6 set exists in this process",
        "open_exemplars": len(ids),
        "counts": {t: len(tranches[t]) for t in TRANCHES},
        "unique_unordered_pairs": len(union),
        "exemplar_coverage": {"covered": len(covered), "total": len(ids)},
        "pairs": {t: [list(p) for p in sorted(set(tranches[t]))]
                  for t in TRANCHES},
    }
    payload["pairs_sha256"] = ap.sha256_of(payload["pairs"])

    if write:
        PAIR_PATH.write_text(ap.canonical_json(payload) + "\n", encoding="utf-8")
        print(f"wrote {PAIR_PATH}")
        print(f"pairs_sha256 {payload['pairs_sha256']}")
    return payload


def _assert_pairing_invariants(classes, ids, tranches, union, covered) -> None:
    """Every frozen property, asserted on every build. Each one HALTS."""
    # 1. no self-pairs, anywhere
    selfp = [p for ts in tranches.values() for p in ts if p[0] == p[1]]
    if selfp:
        fc.halt(f"{len(selfp)} self-pair(s) emitted, e.g. {selfp[:2]!r}. A card "
                f"compared with itself answers no §20 question and is the "
                f"ring-wrap artifact the chain rule exists to avoid.")

    # 2. every published open exemplar is reachable
    if covered != set(ids):
        missed = sorted(set(ids) - covered)
        fc.halt(f"{len(missed)} published open exemplar(s) appear in NO pair, "
                f"e.g. {missed[:3]!r}. Captain ratified coverage of every "
                f"published open exemplar at least once.")

    # 3. no pair reaches outside the published open set
    stray = sorted({o for p in union for o in p} - set(ids))
    if stray:
        fc.halt(f"{len(stray)} paired id(s) are not published open exemplars, "
                f"e.g. {stray[:3]!r}. The only identity source is the "
                f"committed cohort files.")

    # 4. THE COUNT IDENTITY — a cap, top-N or threshold would break it.
    # PAIR_K_CHAIN emits exactly floor(n/2) pairs per published class. This is
    # an identity over the partition, carrying no constant of its own, so it
    # cannot be satisfied by a rule that stopped early.
    expect_k = sum(len(members) // 2 for _cohort, members in classes.values())
    if len(tranches["PAIR_K_CHAIN"]) != expect_k:
        fc.halt(f"PAIR_K_CHAIN emitted {len(tranches['PAIR_K_CHAIN'])} pairs "
                f"but the class partition yields exactly {expect_k}. A cap, a "
                f"top-N or an early stop is the only way to break this "
                f"identity, and every one of them is a tuning knob.")


# ==========================================================================
# CONTROLS
# ==========================================================================

def selftest() -> int:
    ok = True

    def report(name, passed, detail):
        nonlocal ok
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name:<8s} {detail}")

    g = ap.gather()
    classes = published_classes()
    ids = open_exemplars(classes)
    delivery, action = gather_substrate(ids, g)
    tranches = build_pairs(classes, delivery, action)
    union = sorted({p for ts in tranches.values() for p in ts})
    covered = {o for p in union for o in p}
    counts = {t: len(tranches[t]) for t in TRANCHES}

    # -- PC1 the frozen rules reproduce the measured packet-3b numbers -----
    # The audit that Captain ruled on measured these. If the frozen rule does
    # not reproduce them, the thing ratified is not the thing implemented.
    expect = {"PAIR_K_CHAIN": 138, "S0": 105, "S1": 127, "S2": 122}
    report("PC1", counts == expect and len(union) == 486
           and len(covered) == 272 == len(ids),
           f"tranches {counts} == measured {expect}; union {len(union)} unique "
           f"pairs; coverage {len(covered)}/{len(ids)} — the audited numbers "
           f"Captain ruled on are the numbers the frozen rule emits")

    # -- PC2 tranche disjointness + K independence -------------------------
    s_union = set(tranches["S0"]) | set(tranches["S1"]) | set(tranches["S2"])
    pairwise = {f"S0∩S1": len(set(tranches["S0"]) & set(tranches["S1"])),
                f"S0∩S2": len(set(tranches["S0"]) & set(tranches["S2"])),
                f"S1∩S2": len(set(tranches["S1"]) & set(tranches["S2"]))}
    k_overlap = len(set(tranches["PAIR_K_CHAIN"]) & s_union)
    report("PC2", all(v == 0 for v in pairwise.values()) and k_overlap == 6,
           f"S tranches mutually disjoint {pairwise}; PAIR_K shares only "
           f"{k_overlap} pairs with S, so the control is near-independent and "
           f"not a subset of the stratified tranches")

    # -- PC3 no self-pairs; the singleton is rescued by S ------------------
    singles = [cid for cid, (_c, m) in classes.items() if len(m) < 2]
    single_ids = {o for cid in singles for o in classes[cid][1]}
    k_self = [p for p in tranches["PAIR_K_CHAIN"] if p[0] == p[1]]
    k_cov = {o for p in tranches["PAIR_K_CHAIN"] for o in p}
    rescued = sorted(single_ids - k_cov)
    rescued_by_s = all(any(o in p for p in s_union) for o in rescued)
    # RIG: the ring rule Captain did NOT adopt. On a 1-member class it emits a
    # self-pair, which is exactly why the chain was ratified instead.
    def ring(members, label):
        o = ap.hash_order(label, sorted(members))
        if len(o) < 2:
            return [_pair(o[0], o[0])] if o else []
        return [_pair(o[i], o[(i + 1) % len(o)]) for i in range(len(o))]
    rig_self = [p for cid, (_c, m) in classes.items()
                for p in ring(m, f"rig\x00{cid}") if p[0] == p[1]]
    report("PC3", not k_self and len(singles) == 1 and rescued and rescued_by_s
           and len(rig_self) == 1,
           f"PAIR_K emits 0 self-pairs; the {len(singles)} singleton class "
           f"({singles[0]}) is unpairable within its class and IS rescued by a "
           f"cross-class S tranche; RIG — the unratified ring rule emits "
           f"{len(rig_self)} self-pair(s) on the same input")

    # -- PC4 no cap / top-N / threshold ------------------------------------
    expect_k = sum(len(m) // 2 for _c, m in classes.values())
    # RIG, AND THE AIM MATTERS. The first version of this control capped at 4
    # and PASSED VACUOUSLY: published classes hold 1/5/6/8 members, so
    # floor(n/2) never exceeds 4 and a cap of 4 removes nothing. A rig that
    # cannot bite reads exactly like a rig that found nothing wrong. Capped at
    # 2, which is below the modal class's yield of 3, so it genuinely bites.
    CAP = 2
    capped = []
    for cid, (_c, m) in classes.items():
        capped.extend(chain_pairs(m, _label("PAIR_K_CHAIN", cid))[:CAP])
    report("PC4", counts["PAIR_K_CHAIN"] == expect_k and len(capped) < expect_k,
           f"PAIR_K count {counts['PAIR_K_CHAIN']} equals the partition "
           f"identity sum(floor(n/2))={expect_k}, which carries no constant; "
           f"RIG — a per-class cap of {CAP} drops it to {len(capped)}, so the "
           f"identity detects a cap (a cap of 4 does NOT bite here and would "
           f"have passed vacuously — the aim is the point)")

    # -- PC5 reserved cohort-6 half is never materialized -------------------
    # AIMED AT THE CODE PATH. The claim is not "we filtered the reserved half
    # out" — it is that this module never computes it. Proven by asserting the
    # only identity source is the published files, and rigged by showing the
    # reserved half is a DIFFERENT set that would change the pair count.
    published_union = set(ids)
    from_files = set()
    for f in sorted(glob.glob(str(COHORT_DIR / "cohort-*.json"))):
        payload = json.loads(Path(f).read_text(encoding="utf-8"))
        for cl in payload["classes"]:
            from_files |= set(cl["oracle_ids"])
    no_c45 = not (COHORT_DIR / "cohort-4.json").exists() and \
        not (COHORT_DIR / "cohort-5.json").exists()
    # RIG: a synthetic "reserved" id injected into a class must change the
    # output, proving the pairing genuinely consumes the id set it is handed.
    rig_classes = dict(classes)
    victim = sorted(classes)[0]
    rig_classes[victim] = (classes[victim][0],
                           sorted(classes[victim][1] + ["ffffffff-ffff-ffff-ffff-ffffffffffff"]))
    rig_k = sum(len(m) // 2 for _c, m in rig_classes.values())
    report("PC5", published_union == from_files and no_c45 and rig_k != expect_k,
           f"every paired id came from the committed cohort files "
           f"({len(from_files)} ids); build_cohorts/family_open_reserved never "
           f"called; no cohort-4.json or cohort-5.json exists; RIG — injecting "
           f"one synthetic reserved id moves the partition identity "
           f"{expect_k} -> {rig_k}, so the pair set is not blind to its input")

    # -- PC6 determinism + pins present ------------------------------------
    again = build_pairs(classes, delivery, action)
    same = ap.sha256_of({t: sorted(set(again[t])) for t in TRANCHES}) == \
        ap.sha256_of({t: sorted(set(tranches[t])) for t in TRANCHES})
    pins = reproducibility_pins()
    have = all(pins.get(k) for k in ("corpus_ref", "cr_edition", "cr_sha256",
                                     "grammar_section_2_sha256"))
    # RIG: an unkeyed (id-order) chain is a DIFFERENT pairing. Name/id order is
    # the recorded defect the sampler law forbids.
    unkeyed = []
    for cid, (_c, m) in classes.items():
        o = sorted(m)
        unkeyed.extend(_pair(o[i], o[i + 1]) for i in range(0, len(o) - 1, 2))
    moved = len(set(unkeyed) ^ set(tranches["PAIR_K_CHAIN"]))
    report("PC6", same and have and moved > 0,
           f"rebuild identical; pins present (corpus_ref={pins['corpus_ref']}, "
           f"CR={pins['cr_edition']}, §2 vocab "
           f"{pins['grammar_section_2_delivery_tokens']} tokens); RIG — an "
           f"unkeyed id-order chain moves {moved} pair assignments, so the "
           f"keying is load-bearing")

    print()
    print("  each control is aimed at the CODE PATH, not at a tool name:")
    print("    PC3 rigs the RING rule Captain declined, not a renamed chain;")
    print("    PC4 rigs a per-class CAP, the shape a tuning knob actually takes;")
    print("    PC5 rigs the ID SET handed to the partition, because the claim")
    print("        is that the reserved half is never computed — not filtered;")
    print("    PC6 rigs the ORDERING, since an unkeyed pairing is the recorded")
    print("        name-order defect wearing a different hat.")
    return 0 if ok else 1


def census() -> int:
    p = build(write=False)
    print("=" * 74)
    print("AQ4 CROSS-CARD PAIRING — CENSUS (counts only, no oracle_id printed)")
    print("=" * 74)
    print(f"  open exemplars        {p['open_exemplars']}")
    for t in TRANCHES:
        print(f"  {t:<20s} {p['counts'][t]:>5d}   -> {', '.join(TRANCHE_QUESTIONS[t])}")
    print(f"  unique unordered      {p['unique_unordered_pairs']:>5d}")
    c = p["exemplar_coverage"]
    print(f"  coverage              {c['covered']}/{c['total']}")
    print(f"  pins                  {p['reproducibility_pins']['corpus_ref']} · "
          f"{p['reproducibility_pins']['cr_edition']}")
    return 0


def main() -> int:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--build", action="store_true",
                     help="write pairs-open.json")
    ap_.add_argument("--census", action="store_true",
                     help="counts only; prints no oracle_id")
    ap_.add_argument("--selftest", action="store_true",
                     help="the PC1..PC6 controls, each rigged red")
    a = ap_.parse_args()
    if a.selftest:
        return selftest()
    if a.build:
        build(write=True)
        return 0
    if a.census:
        return census()
    ap_.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
