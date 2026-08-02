#!/usr/bin/env python3
"""Standing family-completeness and name-differentiation sweep. READ-ONLY.

WHY THIS EXISTS. Three Captain-ratified DET patterns
(rule:cant-be-blocked-by-power / -except-by-count / -as-long-as-state) sat
unapplied from ratification until 2026-08-01 because no check ever compared
the ratified stores against each other. The gap was WRITTEN DOWN the whole
time -- docs/grammars.json's cant-be-blocked family records
`instantiated_members: 2` beside `virtual_nodes_example: 3` -- and nobody
cross-read it against the codebook and the pattern file at the same time.
Session 2a then proposed re-creating one of those axes from discounted llm
evidence, and the naming validator rejected the very restriction tokens
Q8.5 had ratified.

Every one of those is the same failure: a hand-maintained MIRROR of a
ratified record is trusted as the record. This sweep is the standing check
for that class, plus the name-differentiation pass Captain ordered
2026-08-01 ("rules challenge each other by name; if two names are too close
we may need additional taxonomy simply for differential reason").

SELF-CALIBRATION (the point Captain raised). A sweep that hardcodes what it
knows becomes one more mirror and drifts like the others. So nothing here
hardcodes a family, a vocabulary, or a slug template: composition templates
are INFERRED from each family's own ratified `instantiated_members`, and
every vocabulary is read from its ratified source at run time. When Captain
ratifies a new family, this sweep covers it without being edited. If a
family's template cannot be inferred, the sweep says so rather than
guessing -- an uninferable family is a finding, not a silent skip.

The four ratified stores it cross-reads:
  docs/grammars.json               -- ratified families, closed vocabularies
  docs/det-patterns-v2.json        -- ratified deterministic patterns
  experiments/out/foundry/codebook.json -- the axes that actually exist
  experiments/validate_slug.py     -- the naming validator's vocabularies

Run:  python3 experiments/foundry_family_sweep.py
      python3 experiments/foundry_family_sweep.py --strict   # exit 1 on BLOCKING
"""
import re
import sys
import json
import argparse
import itertools
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402
import foundry_codebook as fcb  # noqa: E402
import foundry_consolidate as fcon  # noqa: E402
import validate_slug  # noqa: E402

GRAMMARS_PATH = REPO_ROOT / "docs" / "grammars.json"
DET_PATTERNS_PATH = REPO_ROOT / "docs" / "det-patterns-v2.json"
REPORT_PATH = fc.FOUNDRY_OUT_DIR / "family_sweep_report.json"

# The Comprehensive Rules live in the SITE repo, not this one. They are the
# only store in this system that is NOT a hand-maintained mirror -- every
# other vocabulary here is copied by hand from somewhere and has been found
# drifted at least once. Optional by design: this is a public repo whose CI
# has no reason to hold the CR, so pass E reports itself unavailable rather
# than failing when the file is absent. An unavailable pass is stated in the
# report, never silently skipped.
CR_PATH = REPO_ROOT.parent / "mtjawnny.github.io" / "docs" / "mtg-comprehensive-rules.md"

# Severities. BLOCKING = a ratified thing is not where the record says it is,
# or two axes cannot be told apart. ADVISORY = worth a human's eye, not a stop.
BLOCKING, ADVISORY = "BLOCKING", "ADVISORY"


def finding(sev, kind, subject, detail, **extra):
    return dict(severity=sev, kind=kind, subject=subject, detail=detail, **extra)


# --------------------------------------------------------------------------
# store loaders
# --------------------------------------------------------------------------

def load_stores():
    grammars = json.loads(GRAMMARS_PATH.read_text(encoding="utf-8"))["grammars"]
    det_raw = json.loads(DET_PATTERNS_PATH.read_text(encoding="utf-8"))["patterns"]
    codebook = fcb.load_codebook(fcb.CODEBOOK_PATH)["axes"]

    det = {}
    for p in det_raw:
        if p.get("status") != "ratified":
            continue
        slug = p["slug"].split(" (")[0].split(" ")[0]
        # A pattern whose slug text is marked "(pre-filter)" is Lane-1
        # machinery with no axis of its own; anything else is an axis pattern.
        det[slug] = dict(p, is_prefilter=fc.is_prefilter_pattern(p))
    return grammars, det, codebook


# --------------------------------------------------------------------------
# A. mirror drift -- the class of defect that motivated this file
# --------------------------------------------------------------------------

def sweep_mirror_drift(grammars, det, codebook):
    out = []

    # A1. A ratified axis pattern with no codebook record at all. This is the
    # orphan check. foundry_det_pass.load_axis_patterns() silently demotes
    # such a pattern to the prefilter list, so it never runs and never reports.
    for slug, p in sorted(det.items()):
        if p["is_prefilter"] or slug in codebook:
            continue
        out.append(finding(
            BLOCKING, "ratified-pattern-has-no-axis", slug,
            f"det-patterns-v2.json ratifies this pattern (index {p['pattern_index']}, "
            f"{p['corpus_hits']} corpus hits at ratification) but no codebook record exists "
            f"under any status. foundry_det_pass.load_axis_patterns() demotes it to the "
            f"prefilter list without a halt, so it has never been applied.",
            pattern_index=p["pattern_index"], corpus_hits=p["corpus_hits"]))

    # A2. grammars.json claims a member the codebook does not have, or has
    # under a non-live status. The family record is the mirror; the codebook
    # is the record.
    for fam_name, fam in sorted(grammars.items()):
        if fam.get("status") != "ratified":
            continue
        for slug in fam.get("instantiated_members", []):
            entry = codebook.get(slug)
            if entry is None:
                out.append(finding(
                    BLOCKING, "grammar-claims-missing-axis", slug,
                    f"grammars.json lists this as an instantiated member of "
                    f"{fam_name!r}, but no codebook record exists.", family=fam_name))
            elif entry.get("status") not in ("active", "deferred"):
                out.append(finding(
                    ADVISORY, "grammar-claims-non-live-axis", slug,
                    f"listed as instantiated in {fam_name!r} but its codebook status is "
                    f"{entry.get('status')!r}.", family=fam_name))

    # A3. The DET roster and the codebook's own source=DET marking disagree.
    # These are two independent claims about the same fact, and consumers
    # split on which they trust: the SYNTH prompt strips by the roster
    # (foundry_stage1b.load_det_owned_slugs), the consolidation guard checks
    # the codebook marking. An axis in the gap is invisible to both.
    roster = {s for s, p in det.items() if not p["is_prefilter"]}
    marked = {s for s, e in codebook.items() if e.get("source") == "DET"}
    for slug in sorted(roster - marked):
        if slug not in codebook:
            continue  # already reported by A1
        out.append(finding(
            BLOCKING, "det-ownership-disagreement", slug,
            "a ratified DET pattern owns this slug, but its codebook record is not "
            "marked source=DET. The SYNTH prompt strips it (roster) while the "
            "consolidation guard does not protect it (marking) — so SYNTH cannot see it "
            "and nothing stops a lane from writing llm members onto it."))
    for slug in sorted(marked - roster):
        out.append(finding(
            ADVISORY, "det-marked-without-pattern", slug,
            "codebook marks this source=DET but no ratified pattern claims the slug."))

    # A4. Stale denormalised counts inside the pattern file. Harmless to read,
    # actively misleading to a future session that treats them as current.
    for slug, p in sorted(det.items()):
        recorded = p.get("current_codebook_n_members")
        if recorded is None or slug not in codebook:
            continue
        live = len(codebook[slug].get("members", []))
        if recorded != live:
            out.append(finding(
                ADVISORY, "stale-denormalised-count", slug,
                f"det-patterns-v2.json records current_codebook_n_members={recorded}; "
                f"the codebook holds {live}. A snapshot presented as a current value.",
                recorded=recorded, live=live))

    # A5. Vocabulary ratified in a family but absent from the validator. This
    # is what blocked A15: Q8.5 ratified the cant-be-blocked restriction vocab
    # and validate_slug only ever encoded the stem tokens.
    validator_vocab = set(validate_slug.CLOSED_VOCAB)
    for fam_name, fam in sorted(grammars.items()):
        if fam.get("status") != "ratified":
            continue
        for facet in fam.get("facets", []):
            vocab = facet.get("closed_vocab")
            if not isinstance(vocab, list):
                continue
            for value in vocab:
                # A facet value may be a multi-token phrase or carry a
                # <placeholder>; check its literal tokens.
                tokens = [t for t in value.replace("<", "").replace(">", "").split("-") if t]
                missing = [t for t in tokens if t not in validator_vocab]
                if missing:
                    out.append(finding(
                        ADVISORY, "ratified-vocab-missing-from-validator",
                        f"{fam_name}:{facet['slot']}={value}",
                        f"token(s) {missing} are ratified as closed vocabulary for this facet "
                        f"but are not in validate_slug's CLOSED_VOCAB, so a correctly-composed "
                        f"sibling of this family fails validation.",
                        family=fam_name, slot=facet["slot"], missing_tokens=missing))
    return out


# --------------------------------------------------------------------------
# B. family completeness -- Captain's sibling-derivation insight, mechanised
# --------------------------------------------------------------------------

def infer_template(fam_name, fam):
    """Infer a family's composition template from its OWN ratified members
    rather than from its `stem` string.

    The stem field is prose (e.g. "activated-(un)tap[-or-untap]") and cannot
    be joined onto facet values; naive concatenation invents slugs that were
    never proposed. Instead: take each instantiated member, strip the facet
    values its tokens match, and whatever prefix survives across ALL members
    is the real fixed prefix. Returns (prefix_tokens, slots) or None when the
    family's members do not agree on one -- an uninferable family is reported,
    never guessed at.
    """
    members = [m[len("rule:"):] if m.startswith("rule:") else m
               for m in fam.get("instantiated_members", [])]
    slots = [f["closed_vocab"] for f in fam.get("facets", [])
             if isinstance(f.get("closed_vocab"), list)]
    if not members or not slots or len(slots) != len(fam.get("facets", [])):
        return None

    prefixes = defaultdict(list)
    nonconforming = []
    for m in members:
        remaining = m.split("-")
        unmatched = []
        # Greedily strip any trailing run of tokens that spells a facet value.
        for vocab in reversed(slots):
            matched = False
            for value in sorted(vocab, key=len, reverse=True):
                vt = value.replace("<", "").replace(">", "").split("-")
                if len(vt) <= len(remaining) and remaining[-len(vt):] == vt:
                    remaining = remaining[:-len(vt)]
                    matched = True
                    break
            if not matched:
                unmatched.append("<unfilled>")
        if unmatched:
            nonconforming.append({"member": f"rule:{m}", "unfilled_slots": len(unmatched)})
        prefixes["-".join(remaining)].append(f"rule:{m}")
    # One agreed prefix across every member, or we do not claim to know it.
    if len(prefixes) != 1:
        return {"ok": False, "prefixes": {k: v for k, v in prefixes.items()},
                "nonconforming": nonconforming}
    return {"ok": True, "prefix": next(iter(prefixes)), "slots": slots,
            "nonconforming": nonconforming}


def sweep_family_completeness(grammars, det, codebook, extra_known):
    """extra_known: {canonical_form: label} for things that exist outside the
    codebook (e.g. proposed consolidation nodes) so a sibling already queued
    for creation is not reported as missing."""
    out, coverage = [], []
    canon_cb = {fcon.canonicalize_label(s): s for s in codebook}
    canon_det = {fcon.canonicalize_label(s): s for s in det}

    for fam_name, fam in sorted(grammars.items()):
        if fam.get("status") != "ratified":
            continue
        open_facets = [f["slot"] for f in fam.get("facets", [])
                       if not isinstance(f.get("closed_vocab"), list)]
        if open_facets:
            coverage.append({"family": fam_name, "closed": False,
                             "open_facets": open_facets,
                             "note": "open facet vocabulary — siblings are not enumerable"})
            continue

        inferred = infer_template(fam_name, fam)
        if inferred is None or not inferred["ok"]:
            groups = inferred["prefixes"] if inferred else {}
            out.append(finding(
                BLOCKING, "family-members-contradict-template", fam_name,
                "this family's own ratified instantiated_members do not compose to one "
                "template, so its siblings cannot be enumerated and its coverage is "
                "unknowable. The members disagree with the family record that lists them "
                f"— they strip to {len(groups)} different prefixes: "
                + "; ".join(f"{k!r} <- {v}" for k, v in sorted(groups.items())),
                prefix_groups={k: v for k, v in sorted(groups.items())},
                nonconforming=(inferred or {}).get("nonconforming", [])))
            coverage.append({"family": fam_name, "closed": True, "inferable": False})
            continue

        prefix, slots = inferred["prefix"], inferred["slots"]
        for nc in inferred["nonconforming"]:
            out.append(finding(
                ADVISORY, "family-member-has-unfilled-slot", nc["member"],
                f"listed as an instantiated member of {fam_name!r} but {nc['unfilled_slots']} "
                f"facet slot(s) are not filled by any ratified vocabulary value — the name "
                f"does not express every facet the family declares.", family=fam_name))
        product, missing = [], []
        for combo in itertools.product(*slots):
            parts = [prefix] if prefix else []
            for value in combo:
                parts.append(value.replace("<", "").replace(">", ""))
            slug = "rule:" + "-".join(p for p in parts if p)
            product.append(slug)
            key = fcon.canonicalize_label(slug)
            if key in canon_cb or key in canon_det or key in extra_known:
                continue
            missing.append(slug)

        coverage.append({
            "family": fam_name, "closed": True, "inferable": True,
            "inferred_prefix": prefix,
            "slots": [len(s) for s in slots],
            "product": len(product), "covered": len(product) - len(missing),
            "uncovered": missing,
        })
        for slug in missing:
            out.append(finding(
                ADVISORY, "family-sibling-uninstantiated", slug,
                f"a valid composition of ratified family {fam_name!r} with no axis, no "
                f"ratified pattern, and nothing queued to create it. Not necessarily a "
                f"defect — the shape may have no corpus support, or may be semantically "
                f"void — but it is unexamined. Measure its corpus hits before ruling.",
                family=fam_name))
    return out, coverage


# --------------------------------------------------------------------------
# E. CR vocabulary completeness -- the check against the one non-mirror
# --------------------------------------------------------------------------

# The CR enumerates a closed set in exactly two shapes. Both are parsed
# generically; neither is a per-family hardcoding.
#
#   TERM-HEADING     "701.2. Activate"      -- rule number, then a bare term,
#                                              no sentence. Used for keyword
#                                              actions (701) and keyword
#                                              abilities (702).
#   DEFINED-INSTANCE "111.10a A Treasure token is a colorless ..."
#                                           -- lettered subrule defining one
#                                              named instance of a category.
_CR_TERM_HEADING = re.compile(r"^(\d{3}\.\d+)\.\s+([A-Z][A-Za-z'’\- ]{2,40})\s*$", re.M)
_CR_DEFINED_INSTANCE = re.compile(
    r"^(\d{3}\.\d+[a-z])\s+An?\s+([A-Z][\w'’]*(?:\s+[A-Z][\w'’]*)*)\s+(\w+)\s+is\b", re.M)


def load_cr():
    if not CR_PATH.exists():
        return None
    return CR_PATH.read_text(encoding="utf-8")


def cr_enumeration(cr_text, anchor):
    """Every term the CR enumerates under `anchor` (e.g. "111.10", "701").
    Returns (shape, [terms]) or (None, []) when nothing parses -- the caller
    reports that rather than treating an unparsed anchor as agreement."""
    if not cr_text:
        return None, []
    terms = [m.group(2).strip() for m in _CR_DEFINED_INSTANCE.finditer(cr_text)
             if m.group(1).startswith(anchor)]
    if terms:
        return "defined-instance", sorted(set(terms))
    prefix = anchor if "." in anchor else anchor + "."
    terms = [m.group(2).strip() for m in _CR_TERM_HEADING.finditer(cr_text)
             if m.group(1).startswith(prefix)]
    if terms:
        return "term-heading", sorted(set(terms))
    return None, []


def _norm(s):
    return s.lower().replace("’", "'").replace(" ", "-")


def sweep_cr_vocabulary(grammars, cr_text):
    """Compare each ratified closed vocabulary against what the CR actually
    enumerates under that family's own cr_anchor.

    A gap is reported, never auto-judged: the project may legitimately scope
    NARROWER than the CR, and this pass cannot tell a deliberate exclusion
    from a forgotten one. What it can prove is that a value the CR defines has
    no home in the ratified vocabulary -- and a card carrying that value must
    then land somewhere wrong, because the model has nowhere right to put it.
    That is exactly how Map and Vibranium tokens ended up inside
    rule:create-token-clue and rule:etb-create-token-mana-producing-artifact
    (2026-08-01), which an external audit read as model incoherence.
    """
    out, coverage = [], []
    if cr_text is None:
        out.append(finding(
            ADVISORY, "cr-unavailable", str(CR_PATH),
            "the Comprehensive Rules were not found, so ratified vocabularies were NOT "
            "checked against their CR anchors. This pass did not run — its silence is "
            "absence of evidence, not evidence of agreement."))
        return out, coverage

    for fam_name, fam in sorted(grammars.items()):
        if fam.get("status") != "ratified":
            continue
        anchors = re.findall(r"\b(\d{3}(?:\.\d+)?)\b", fam.get("cr_anchor") or "")
        for facet in fam.get("facets", []):
            vocab = facet.get("closed_vocab")
            if not isinstance(vocab, list):
                continue
            # Pick the anchor whose enumeration this facet's vocabulary is
            # actually DRAWN FROM, not the one with the most terms. A family's
            # cr_anchor prose often cites several rules, and only one of them
            # (if any) enumerates the domain a given facet ranges over: the
            # grants-<keyword> family anchors on CR 702 for its `keyword`
            # facet, but its `duration` facet (eot / next-turn / ...) ranges
            # over nothing CR 702 lists. Scoring by overlap keeps the check
            # from indicting every facet whose anchor merely mentions a big
            # enumeration -- an alarm that is wrong most of the time trains
            # people to ignore the times it is right.
            ratified_norm = {_norm(v) for v in vocab}
            best = (None, [], None, 0.0)
            any_parsed = None
            for a in anchors:
                shape, terms = cr_enumeration(cr_text, a)
                if not terms:
                    continue
                any_parsed = any_parsed or a
                overlap = len({_norm(t) for t in terms} & ratified_norm)
                score = overlap / len(ratified_norm) if ratified_norm else 0.0
                if score > best[3]:
                    best = (shape, terms, a, score)
            shape, terms, anchor, score = best
            if not terms and any_parsed:
                # An enumeration parsed fine; this facet simply does not range
                # over it. Distinct from "nothing parsed" -- saying otherwise
                # would misreport a working check as a broken one.
                anchor, score, terms = any_parsed, 0.0, []

            # Below this bar the vocabulary is not drawn from the enumeration,
            # so "what the CR lists and we lack" is not a gap in our coverage
            # -- it is a comparison against the wrong list.
            if (terms or any_parsed) and score < 0.5:
                coverage.append({
                    "family": fam_name, "slot": facet["slot"], "cr_anchor": anchor,
                    "applicable": False, "overlap_fraction": round(score, 3),
                    "note": "facet vocabulary is not drawn from this CR enumeration; "
                            "no completeness claim is made either way",
                })
                continue
            if not terms:
                out.append(finding(
                    ADVISORY, "cr-enumeration-not-extractable",
                    f"{fam_name}:{facet['slot']}",
                    f"no enumerable term list could be parsed from CR anchor(s) {anchors} in "
                    f"either known shape, so this vocabulary was NOT checked against the CR. "
                    f"Reported rather than passed."))
                continue

            ratified = {_norm(v) for v in vocab}
            cr_terms = {_norm(t): t for t in terms}
            missing = sorted(cr_terms[k] for k in set(cr_terms) - ratified)
            extra = sorted(v for v in vocab if _norm(v) not in cr_terms)
            coverage.append({
                "family": fam_name, "slot": facet["slot"], "cr_anchor": anchor,
                "applicable": True, "overlap_fraction": round(score, 3),
                "cr_shape": shape, "cr_enumerated": len(terms),
                "ratified": len(vocab), "missing_from_ratified": missing,
                "ratified_beyond_cr": extra,
            })
            if missing:
                out.append(finding(
                    ADVISORY, "cr-vocabulary-incomplete", f"{fam_name}:{facet['slot']}",
                    f"CR {anchor} enumerates {len(terms)} terms; this ratified vocabulary "
                    f"covers {len(terms) - len(missing)}. A card carrying one of the "
                    f"{len(missing)} uncovered values has no valid slug in this family and "
                    f"will be absorbed by the nearest sibling. Confirm each is a deliberate "
                    f"exclusion or ratify it: {missing}",
                    family=fam_name, slot=facet["slot"], cr_anchor=anchor,
                    missing=missing))
    return out, coverage


# --------------------------------------------------------------------------
# C. name differentiation -- "rules challenge each other by name"
# --------------------------------------------------------------------------

def sweep_name_differentiation(codebook, extra_labels):
    """Every live axis (plus anything queued for creation) is challenged
    against every other. Three outcomes matter, in descending severity:

      COLLISION      two names canonicalize identically — the system cannot
                     tell them apart at all
      SUBSUMPTION    one name's tokens are a strict subset of another's, so
                     the shorter name does not say what excludes the longer;
                     a card matching the longer also reads as matching the
                     shorter
      THIN-DIFFERENCE  the names differ by exactly one token and that token
                     is NOT drawn from any ratified facet vocabulary, so the
                     distinction is real but unnamed — this is precisely the
                     case Captain ordered additional taxonomy for

    A one-token difference drawn FROM a ratified facet vocabulary is the
    grammar working as intended and is not reported.
    """
    out = []
    labels = dict(extra_labels)
    for slug, e in codebook.items():
        if e.get("status") in ("active", "deferred"):
            labels[slug] = e.get("status")

    canon = defaultdict(list)
    for slug in labels:
        canon[fcon.canonicalize_label(slug)].append(slug)
    for key, group in sorted(canon.items()):
        if len(group) > 1:
            out.append(finding(
                BLOCKING, "name-collision", " ~ ".join(sorted(group)),
                f"these names canonicalize to the same form ({key!r}). They are the same "
                f"axis under two spellings; one must merge, alias, or be renamed.",
                members=sorted(group)))

    facet_vocab = set(validate_slug.CLOSED_VOCAB)
    tokens = {s: [t for t in (s[len("rule:"):] if s.startswith("rule:") else s).split("-") if t]
              for s in labels}
    slugs = sorted(labels)
    for i, a in enumerate(slugs):
        ta, sa = tokens[a], set(tokens[a])
        for b in slugs[i + 1:]:
            tb, sb = tokens[b], set(tokens[b])
            if sa == sb and ta != tb:
                out.append(finding(
                    BLOCKING, "name-reorder-collision", f"{a} ~ {b}",
                    "identical token sets in different order — the same name written two "
                    "ways.", members=[a, b]))
                continue
            if sa < sb or sb < sa:
                shorter, longer = (a, b) if sa < sb else (b, a)
                extra = sorted(set(tokens[longer]) - set(tokens[shorter]))
                out.append(finding(
                    ADVISORY, "name-subsumption", f"{shorter} < {longer}",
                    f"{longer!r} is {shorter!r} plus {extra}. A card matching the longer "
                    f"axis also reads as matching the shorter one, so the shorter name does "
                    f"not state what excludes the longer. Needs an explicit parent/child "
                    f"relation, or a differentiating token on the shorter name.",
                    shorter=shorter, longer=longer, extra_tokens=extra))
                continue
            only_a, only_b = sa - sb, sb - sa
            if len(only_a) == 1 and len(only_b) == 1:
                ua, ub = only_a.pop(), only_b.pop()
                if ua in facet_vocab and ub in facet_vocab:
                    continue  # a ratified facet distinction: the grammar working
                # "Too close" presupposes shared context. Two one-token slugs
                # (rule:cantrip vs rule:modal) trivially satisfy the
                # one-differing-token test while sharing nothing and naming
                # unrelated concepts — that is maximally FAR apart, not close.
                # Require the names to agree on more than they differ on.
                if len(sa & sb) < 2 or len(sa & sb) <= 1:
                    continue
                out.append(finding(
                    ADVISORY, "name-thin-difference", f"{a} ~ {b}",
                    f"these differ only by {ua!r} vs {ub!r}, and that distinction is not "
                    f"drawn from any ratified facet vocabulary. The difference may be real, "
                    f"but nothing in the naming system names it — a reader (or a model) "
                    f"cannot tell which to choose. Candidate for additional taxonomy.",
                    members=[a, b], differing_tokens=[ua, ub]))
    return out


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def run(include_proposed: bool):
    grammars, det, codebook = load_stores()

    extra_known, extra_labels = {}, {}
    proposed_path = fc.FOUNDRY_OUT_DIR / "corpus_pass_run1_classification.json"
    if include_proposed and proposed_path.exists():
        art = json.loads(proposed_path.read_text(encoding="utf-8"))
        for n in art.get("node_classification", []):
            if n.get("action") == "instantiate":
                extra_known[fcon.canonicalize_label(n["slug"])] = n["slug"]
                extra_labels[n["slug"]] = "proposed-2a-node"

    cr_text = load_cr()
    findings = []
    findings += sweep_mirror_drift(grammars, det, codebook)
    fam_findings, coverage = sweep_family_completeness(grammars, det, codebook, extra_known)
    findings += fam_findings
    cr_findings, cr_coverage = sweep_cr_vocabulary(grammars, cr_text)
    findings += cr_findings
    findings += sweep_name_differentiation(codebook, extra_labels)

    findings.sort(key=lambda f: (f["severity"] != BLOCKING, f["kind"], f["subject"]))
    by_kind = Counter(f["kind"] for f in findings)
    by_sev = Counter(f["severity"] for f in findings)

    report = {
        "schema": "foundry-family-sweep/1",
        "generated_by": "experiments/foundry_family_sweep.py",
        "codebook_sha256": fcb.sha256_of(fcb.CODEBOOK_PATH),
        "included_proposed_nodes": bool(extra_labels),
        "totals": {"findings": len(findings), **dict(sorted(by_sev.items()))},
        "by_kind": dict(sorted(by_kind.items())),
        "cr_available": cr_text is not None,
        "cr_path": str(CR_PATH),
        "family_coverage": coverage,
        "cr_vocabulary_coverage": cr_coverage,
        "findings": findings,
    }
    fc.write_json(REPORT_PATH, report)

    print(f"family sweep — codebook {report['codebook_sha256'][:16]}…"
          + (" (+ proposed 2a nodes)" if extra_labels else ""))
    print(f"\n{'family':<52} {'closed':>7} {'product':>8} {'covered':>8} {'gaps':>6}")
    print("-" * 86)
    for c in coverage:
        if not c.get("closed"):
            print(f"{c['family'][:50]:<52} {'open':>7} {'-':>8} {'-':>8} {'-':>6}")
        elif not c.get("inferable"):
            print(f"{c['family'][:50]:<52} {'yes':>7} {'?':>8} {'?':>8} {'?':>6}")
        else:
            print(f"{c['family'][:50]:<52} {'yes':>7} {c['product']:>8} "
                  f"{c['covered']:>8} {len(c['uncovered']):>6}")

    if cr_coverage:
        print(f"\n{'family:slot':<44} {'CR anchor':>10} {'CR':>5} {'ours':>5} {'gap':>5}")
        print("-" * 76)
        for c in cr_coverage:
            if not c.get("applicable"):
                print(f"{(c['family'][:30] + ':' + c['slot'])[:42]:<44} {c['cr_anchor']:>10} "
                      f"{'n/a':>5} {'-':>5} {'-':>5}   (not this facet's domain)")
            else:
                print(f"{(c['family'][:30] + ':' + c['slot'])[:42]:<44} {c['cr_anchor']:>10} "
                      f"{c['cr_enumerated']:>5} {c['ratified']:>5} {len(c['missing_from_ratified']):>5}")
    elif cr_text is None:
        print("\nCR pass: NOT RUN (comprehensive rules not found)")

    print(f"\nfindings: {len(findings)}  ({by_sev.get(BLOCKING, 0)} blocking, "
          f"{by_sev.get(ADVISORY, 0)} advisory)")
    for kind, n in sorted(by_kind.items()):
        print(f"   {kind:<42} {n}")
    if by_sev.get(BLOCKING):
        print("\nBLOCKING:")
        for f in findings:
            if f["severity"] == BLOCKING:
                print(f"   [{f['kind']}] {f['subject']}")
    print(f"\nwrote {REPORT_PATH}")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--strict", action="store_true",
                   help="exit 1 if any BLOCKING finding is present (for use as a gate)")
    p.add_argument("--no-proposed", action="store_true",
                   help="sweep the codebook alone, ignoring proposed consolidation nodes")
    a = p.parse_args()
    report = run(include_proposed=not a.no_proposed)
    if a.strict and report["totals"].get(BLOCKING):
        fc.halt(f"{report['totals'][BLOCKING]} blocking finding(s) — see {REPORT_PATH}")


if __name__ == "__main__":
    main()
