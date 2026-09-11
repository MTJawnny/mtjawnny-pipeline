#!/usr/bin/env python3
"""SEMANTIC LOCALITY — which structured part of a card owns a fact.

RATIFIED 2026-08-13, resolving FL-2.

CANONICAL RULING: `docs/B-MIGRATION-DISCOVERY.md` sec.11 -- tracked, and it
sits with sec.10's A1, the section that defines the assertion object this
amends. Cite THAT for the law.

**AMENDMENTS A1-A4 ARE RESTATED IN FULL AT sec.11.2 OF THAT SAME TRACKED
DOCUMENT, AND THAT IS THE CITATION TO USE.** Every `A1`/`A2`/`A3`/`A4` below
means sec.11.2. This was repointed 2026-08-14: the amendments were previously
cited to the architecture-review packet, which is UNTRACKED, so on a fresh
clone a Gate 2 module cited a path that does not exist -- the same fail-open
shape as `SESSION-START-PROCEDURE.md` Gate 3b's missing-manifest corollary,
and as a ratified standard with no caller.

Working packets, historical records rather than authority -- and they differ in
whether a fresh clone even has them:
  * `docs/SEMANTIC-ADDRESS-PREIMPLEMENTATION-CHECK-2026-08-13.md` (PASS) --
    TRACKED, committed in 35f77b7. Safe to cite for detail.
  * `docs/SEMANTIC-ADDRESS-ARCHITECTURE-REVIEW-2026-08-13.md` (RATIFY WITH
    AMENDMENTS A1-A4) -- **UNTRACKED**. Do not cite it as authority; its
    binding content is sec.11.2.

THE PROBLEM THIS SOLVES, IN ONE CARD
------------------------------------
Active Volcano prints `Choose one — • Destroy target blue permanent. • Return
target Island to its owner's hand.` The codebook knows the card destroys a
permanent AND bounces a land. Both true. It does not know they are two options
you choose BETWEEN. Measured 2026-08-13: **41 cards** carry two object-lattice
facts proven by mutually exclusive modes.

An assertion already carries the quote that proves it. It never carried WHICH
PART of the card that quote came from. This module derives that.

WHAT AN ADDRESS IS, AND WHAT IT DELIBERATELY IS NOT
---------------------------------------------------
* **Semantic OWNER** — the one structured location that owns the fact.
* **Evidence SPAN** — the wider contiguous range some quotes cover.

They are different, and A2 exists because 39 quoted assertions legitimately
cover a whole modal block. **The span is DERIVED, never stored** (§13 of the
pre-implementation check): it is a pure function of quote + corpus snapshot,
and storing it would duplicate something that can go stale on its own.

**NO MODE IDENTIFIER IS DERIVED (amendment A1).** Measured over the whole
corpus: **1,791 paragraphs hold exactly one modal bullet and ZERO hold two or
more.** Scryfall puts every mode on its own line, so the paragraph coordinate
IS the mode path. A separate mode field would be a second source of truth for
a fact the paragraph index already carries.

**EXCLUSIVITY IS DERIVED, NEVER STORED (amendment A4).** `owning_header()`
walks back to the nearest preceding non-bullet paragraph on the same face:
**1,783 of 1,791 bullets** resolve deterministically. The 8 exceptions are
Celebr-8000's CR 706.3b die-roll table, which the repository already rules is
not modal.

THE RESOLUTION LAW (amendment A3) — RECONCILED, NEVER RACED
------------------------------------------------------------
A quote is resolved against EVERY supported text representation, and the owner
is accepted only when the union of matched COORDINATES holds exactly one
element. This is not first-match-wins and it privileges no producer class.

Why both representations are required, measured 2026-08-13 over 7,891 quoted
assertions: human evidence is verbatim, DET evidence is CARDNAME-canonicalized.

    raw only        98.6%          canonical only  93.7%          either  99.44%

Canonical-only would orphan **423 human assertions**; raw-only orphans 26 DET
ones. And the tie the law never has to break: **Case F — the two
representations resolving to DIFFERENT single units — is 0**, as are the cases
where one narrows the other. The union is safe because the corpus contains no
disagreement, and it returns AMBIGUOUS by construction if one ever appears.

**The union is over COORDINATES, not over strings.** That is what makes a
canonicalization collision safe: `Rahilda, Wanted Cutthroat // Rahilda, Feral
Outlaw` has two faces whose distinct raw text collapses to identical
canonical text, and two paragraphs collapsing to the same STRING still hold
different COORDINATES, so the union has 2 elements and the law returns
AMBIGUOUS rather than silently merging them.

WHAT THIS MODULE DOES NOT DO
----------------------------
* It writes nothing. No assertion is modified; the backfill migration is a
  separate, Captain-authorised codebook mutation under the backup law.
* **Locality does not certify CORRECTNESS.** A perfectly addressed assertion
  can still sit on the wrong axis -- `foundry_definition_drift` C4 measured 93
  such memberships. Where locality analysis finds a membership contradicting
  its axis, it is routed there, never forced into an address.
* No child-effect decomposition, no qualifier vocabulary, no roles.

    python3 experiments/foundry_locality.py --census
    python3 experiments/foundry_locality.py --report

The GATE is no longer here. S9 moved the fixtures, the schema and
write-boundary controls, the ratchet and `--selftest` to their test owner:

    python3 tests/guards/gate2/test_locality.py --gate
"""
import argparse
import functools
import inspect
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import foundry_common as fc                    # noqa: E402

# S9: `foundry_codebook`, the C8.5J ratchet import and the `ProjectPaths` view it
# bound left WITH the guard they existed for. The schema and write-boundary
# fixtures were this shell's only `foundry_codebook` callers, and the ratchet
# baseline was read only by the gate. Keeping either here would leave a binding
# with no reader -- the "ratified token with no emitter" shape this repository
# has paid for three times -- so they live at the guard's owner,
# `tests/guards/gate2/test_locality.py`, and nowhere else.


# ---------------------------------------------------------------------------
# S7 — THE RATIFIED ADDRESS LAW NOW LIVES IN THE PERMANENT SUBSTRATE
# ---------------------------------------------------------------------------
# Migration slice 7 moved the six pure definitions into
# `mtj_foundry.mtg.shapes.locality`: the four statuses, `_norm`, `units`,
# `resolve`, `owning_header`, `mutually_exclusive` and `_by_name`. NO SECOND
# IMPLEMENTATION REMAINS HERE.
#
# What stayed was everything the permanent MTG layer may not own: the
# codebook-facing census and binding, the assertion-schema fixtures, the
# boundary-fixture writer, the ratchet directions and their baseline, the
# unaddressed report, and the CLI.
#
# S9 split that list in two rather than leaving it standing. The GUARD half --
# every fixture, the ratchet directions with their baseline read and direction
# assertion, `--gate` and `--selftest` -- is now owned by
# `tests/guards/gate2/test_locality.py`, and NO COPY OF IT REMAINS HERE. What is
# still this shell's is the codebook-facing `census()` and the unaddressed
# reporter with its `--census`/`--report` doors; those are later slices.
#
# The halt boundary is re-established here: the permanent module raises
# `LocalityError`, and the wrappers below convert it to `fc.halt`, preserving
# the historic `STOP — …` process contract for every legacy caller.
from mtj_foundry.mtg.shapes import locality as _locality  # noqa: E402

LocalityError = _locality.LocalityError

# THE CARD-TEXT PRIMITIVES, INJECTED. The shared face reader and the ratified
# CARDNAME collapse are `foundry_common`'s today and a later slice's tomorrow.
# The substrate receives them from here; it never imports them and never infers
# them.
_locality.use_card_face_rules(_locality.CardFaceRules(fc, {
    "raw_faces": "raw_faces",
    "canonicalize_self_reference": "canonicalize_self_reference",
}))


def _halting(fn):
    """Re-establish the historic `STOP — …` process contract at this boundary.

    A library may not exit a process it does not own, so the permanent module
    raises and this converts.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except LocalityError as exc:
            fc.halt(str(exc))
    return wrapper


# Re-export by REFERENCE, mechanically, so a name cannot be silently dropped on
# its way through the shell. Doing it BY HAND lost `_BULLET` -- the census and
# the fixtures still read it as a module global, and only the full Gate-2 run
# saw the `NameError`. The address law has no derived state, so every name is
# safe to bind at import; the list is the permanent module's, not a guess.
_NOT_REEXPORTED = {"annotations", "Any", "Callable"}
for _name, _obj in sorted(vars(_locality).items()):
    if _name.startswith("__") or _name in _NOT_REEXPORTED:
        continue
    if _name in globals() or inspect.ismodule(_obj):
        continue
    globals()[_name] = _halting(_obj) if inspect.isfunction(_obj) else _obj
del _name, _obj


def census(cards, codebook_path=None) -> dict:
    """Coverage over every live assertion, with EXACT denominators.

    Reports owner coverage and evidence-location coverage SEPARATELY. They are
    different questions and the pre-implementation check exists because
    substituting one for the other is how a broad quote comes to look owned.
    """
    import json
    path = codebook_path or (fc.FOUNDRY_OUT_DIR / "codebook.json")
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    m = {"assertions": 0, "quoted": 0, "quoteless": 0,
         "owned": 0, "span": 0, "ambiguous": 0, "unresolved": 0,
         # STORED coverage, added with the step-4 backfill. Everything above
         # measures what the resolver CAN address; these two measure what the
         # codebook actually CARRIES, and the difference is not academic:
         # measured 2026-08-13, deleting all 7,808 stored addresses left every
         # one of Gate 2's 15 rows green, because a census computed from quotes
         # reproduces itself perfectly on a file with the field stripped out.
         # The migration's entire product was unguarded by the gate that
         # exists to guard it.
         #
         # Marker choice is deliberate and collision-checked against every
         # pinned section, per the trap the handoff records: `stored_owned`
         # resolves WORSE_IF_DOWN through the pre-existing "owned" marker and
         # `stored_mismatch` resolves WORSE_IF_UP through "mismatch", so
         # neither needs a new marker and neither changes another consumer's
         # semantics as a side effect.
         "stored_owned": 0, "stored_mismatch": 0,
         # THE THIRD QUESTION, AND THE ONE NEITHER OTHER METRIC CAN ANSWER.
         # An assertion the resolver addresses to exactly one OWNER, whose
         # stored `locality` is ABSENT. Correct value: 0.
         #
         # The regression it exists for: someone removes or fails to write
         # locality on an assertion that is still perfectly deterministically
         # addressable. `stored_owned` can stay FLAT through that, because
         # corpus growth adds addressed rows at the same time it loses one --
         # a ratchet on a total cannot see a compensated loss, which is the
         # object lattice's own open -7/+7 gap in a different field.
         # `stored_mismatch` stays 0 because no INCORRECT coordinate was
         # stored; absence is not disagreement. Only a per-assertion join of
         # "is addressable" against "is addressed" catches it.
         #
         # EXCLUSIONS, all four by ratification rather than convenience:
         # AMBIGUOUS, SPAN, UNRESOLVED and quoteless assertions are NOT
         # missing. The resolver declines to address them, so an absent
         # address is the correct and required state -- counting them here
         # would make the ratified unaddressed rule read as 122 permanent
         # defects. Tombstone (non-active) axes stay outside the active-axis
         # locality contract, unchanged.
         "addressable_missing": 0}
    for slug, axis in cb["axes"].items():
        if axis.get("status") != "active":
            continue
        for member in axis.get("members") or []:
            card = cards.get(member["oracle_id"])
            for a in member["assertions"]:
                m["assertions"] += 1
                q = a.get("quote")
                stored = a.get("locality")
                if stored is not None:
                    m["stored_owned"] += 1
                if not q:
                    m["quoteless"] += 1
                    # A stored address with no quote is unfalsifiable; lint
                    # already rejects it, so reaching here is a mismatch.
                    if stored is not None:
                        m["stored_mismatch"] += 1
                    continue
                m["quoted"] += 1
                if card is None:
                    m["unresolved"] += 1
                    if stored is not None:
                        m["stored_mismatch"] += 1
                    continue
                r = resolve(card, q)
                m[{OWNER: "owned", SPAN: "span", AMBIGUOUS: "ambiguous",
                   UNRESOLVED: "unresolved"}[r["status"]] ] += 1
                # An address is SNAPSHOT-RELATIVE. When the corpus moves under
                # stored evidence, the ratified rule is that the change is
                # REPORTED, never silently reattached -- so this counts rather
                # than repairs.
                if stored is not None and (
                        r["status"] != OWNER or list(r["owner"]) != list(stored)):
                    m["stored_mismatch"] += 1
                # Addressable but unaddressed. Deliberately keyed on OWNER
                # only, so the four unaddressed-by-rule statuses can never
                # reach it.
                if r["status"] == OWNER and stored is None:
                    m["addressable_missing"] += 1
    return m


# --------------------------------------------------------------------------
# STEP 5 — the unaddressed-assertion reporter
#
# `census()` returns COUNTS. What a human needs in order to work the ambiguous
# rows down over time is the LIST, grouped by reason. Written to
# `experiments/out/foundry/` (gitignored: local, never committed), for the same
# reason the object-lattice sample sheet is.
#
# **The remainder is 122, not 83.** The implementation handoff sec.6 enumerates
# "the other 83 (40 ambiguous + 4 unresolved + 39 quoteless)" and omits the
# **39 SPAN** rows, which are equally unaddressed -- `resolve()` returns no
# owner for them, so the backfill skips them exactly as it skips the rest.
# Almost certainly because span and quoteless are BOTH 39 and read as the same
# number twice. The backfill rule itself ("address only where resolve()
# returns OWNER") is unaffected and correct; only the count of its complement
# was wrong. Re-derived here so the reporter can never inherit it.
# --------------------------------------------------------------------------

UNADDRESSED_JSON = fc.FOUNDRY_OUT_DIR / "locality-unaddressed.json"
UNADDRESSED_MD = fc.FOUNDRY_OUT_DIR / "locality-unaddressed.md"

# Why each reason is unaddressed, and what a human would have to do about it.
# Prose, not vocabulary: none of these strings is a ratified token.
_REASON_NOTES = {
    "AMBIGUOUS": ("the quote appears in more than one paragraph, so no "
                  "deterministic rule picks one. Dominated by short repeated "
                  "riders. FIX: narrow the evidence quote to the paragraph "
                  "that actually proves the axis."),
    "SPAN": ("the quote legitimately covers a contiguous run of paragraphs "
             "(A2). The evidence is LOCATED but the fact has no single owner. "
             "FIX: usually none needed -- a modal block quote is honest "
             "evidence; narrow it only if the axis is about one mode."),
    "UNRESOLVED": ("the quote matches no text in the current corpus snapshot. "
                   "Near-noise today. FIX: re-check the quote against the "
                   "card; addresses are snapshot-relative and re-derived."),
    "QUOTELESS": ("the assertion carries no quote at all (the A3 "
                  "legacy-captain-seed exemption). An address is DERIVED from "
                  "a quote, so there is nothing to resolve. FIX: record the "
                  "evidence quote; this is a provenance gap, not a locality "
                  "one."),
}


def unaddressed_rows(cards, codebook_path=None) -> list:
    """Every live assertion the backfill will NOT address, with its reason.

    Deterministically ordered: (reason, slug, oracle_id, class, source_ref).
    Nothing here reads a card name as a code path -- names are carried for the
    human reading the sheet.
    """
    import json
    path = codebook_path or (fc.FOUNDRY_OUT_DIR / "codebook.json")
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for slug, axis in cb["axes"].items():
        if axis.get("status") != "active":
            continue
        for member in axis.get("members") or []:
            oid = member["oracle_id"]
            card = cards.get(oid)
            for a in member["assertions"]:
                q = a.get("quote")
                if not q:
                    reason, detail, cands = "QUOTELESS", (
                        "assertion carries no evidence quote"), []
                elif card is None:
                    reason, detail, cands = "UNRESOLVED", (
                        "oracle_id is not in the gated corpus"), []
                else:
                    r = resolve(card, q)
                    if r["status"] == OWNER:
                        continue
                    reason = r["status"]
                    detail = r["reason"]
                    cands = [list(c) for c in r["candidates"]]
                rows.append({
                    "reason": reason,
                    "axis": slug,
                    "oracle_id": oid,
                    "card": (card or {}).get("name", "(not in corpus)"),
                    "class": a.get("class"),
                    "source_ref": a.get("source_ref"),
                    "quote": q or "",
                    "candidates": cands,
                    "detail": detail,
                })
    rows.sort(key=lambda r: (r["reason"], r["axis"], r["oracle_id"],
                             r["class"] or "", r["source_ref"] or ""))
    return rows


def render_unaddressed_md(rows: list, totals: dict) -> str:
    """The human-readable sheet. Pure function of `rows` -- determinism ×2."""
    from collections import Counter
    by_reason = Counter(r["reason"] for r in rows)
    out = [
        "# SEMANTIC LOCALITY — the unaddressed assertions",
        "",
        "Generated by `python3 experiments/foundry_locality.py --report`.",
        "**Regenerate rather than edit**; this file is gitignored and local.",
        "",
        "An unaddressed assertion is **fully valid card-level evidence** "
        "(ratified 2026-08-13).",
        "It simply cannot prove that its fact co-occurs in the same semantic "
        "unit with another.",
        "Nothing here is a defect by default — read the FIX note per reason.",
        "",
        f"- assertions on active axes: **{totals['assertions']:,}**",
        f"- addressed (semantic OWNER): **{totals['owned']:,}**",
        f"- **unaddressed: {len(rows):,}**",
        "",
        "| reason | n | what it means |",
        "|---|--:|---|",
    ]
    for reason in sorted(by_reason):
        out.append(f"| `{reason}` | {by_reason[reason]} | "
                   f"{_REASON_NOTES.get(reason, '')} |")
    out.append("")
    for reason in sorted(by_reason):
        out += [f"## {reason} — {by_reason[reason]}", "",
                "| axis | card | class | source_ref | quote |",
                "|---|---|---|---|---|"]
        for r in (x for x in rows if x["reason"] == reason):
            q = r["quote"].replace("\n", " ⏎ ").replace("|", "\\|")
            if len(q) > 160:
                q = q[:157] + "…"
            out.append(f"| `{r['axis']}` | {r['card'].replace('|', '')} | "
                       f"{r['class']} | `{r['source_ref']}` | {q} |")
        out.append("")
    return "\n".join(out) + "\n"


def cmd_report(cards) -> int:
    """Writes the two artifacts, with determinism ×2 byte-identical."""
    import json
    from collections import Counter

    totals = census(cards)
    rows = unaddressed_rows(cards)

    # The reporter's own conservation check. `census` and `unaddressed_rows`
    # walk the codebook independently, so a disagreement means one of them is
    # wrong -- exactly the "second measurement path" rule, wired in rather than
    # done once by hand.
    expected = (totals["assertions"] - totals["owned"])
    if len(rows) != expected:
        fc.halt(f"reporter disagreement: census says {expected} assertions are "
                f"unaddressed ({totals['assertions']} total - "
                f"{totals['owned']} owned) but the row walk found "
                f"{len(rows)}. Two independent walks of the same codebook must "
                f"agree; refusing to write a sheet that contradicts the gate.")
    by_reason = Counter(r["reason"] for r in rows)
    if by_reason["SPAN"] != totals["span"] or by_reason["AMBIGUOUS"] != totals["ambiguous"]:
        fc.halt(f"reporter disagreement per reason: rows {dict(by_reason)} vs "
                f"census {totals}")

    payload = {"generated_by": "experiments/foundry_locality.py --report",
               "totals": totals, "unaddressed": len(rows),
               "by_reason": dict(sorted(by_reason.items())), "rows": rows}
    md = render_unaddressed_md(rows, totals)

    # Determinism ×2 on both artifacts, from a second independent build.
    rows2 = unaddressed_rows(cards)
    payload2 = {"generated_by": payload["generated_by"], "totals": census(cards),
                "unaddressed": len(rows2),
                "by_reason": dict(sorted(Counter(r["reason"] for r in rows2).items())),
                "rows": rows2}
    if json.dumps(payload, sort_keys=False) != json.dumps(payload2, sort_keys=False):
        fc.halt("determinism gate FAILED — two builds of the unaddressed "
                "report differ")
    if render_unaddressed_md(rows2, payload2["totals"]) != md:
        fc.halt("determinism gate FAILED — two renders of the unaddressed "
                "sheet differ")

    fc.write_json(UNADDRESSED_JSON, payload)
    UNADDRESSED_MD.write_text(md, encoding="utf-8")
    print(f"determinism ×2 byte-identical on both artifacts")
    print(f"wrote {UNADDRESSED_JSON}")
    print(f"wrote {UNADDRESSED_MD}")
    print(f"\n{totals['assertions']:,} assertions on active axes · "
          f"{totals['owned']:,} addressed · {len(rows):,} UNADDRESSED")
    for reason in sorted(by_reason):
        print(f"    {reason:12}: {by_reason[reason]:>4}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--report", action="store_true",
                    help="write the unaddressed-assertion sheet to "
                         "experiments/out/foundry/ (gitignored)")
    args = ap.parse_args()

    cards, _, _ = fc.load_corpus_gated()

    if args.report:
        return cmd_report(cards)

    if args.census:
        m = census(cards)
        q = max(m["quoted"], 1)
        located = m["owned"] + m["span"]
        print(f"\nlocality census — {m['assertions']:,} assertions, "
              f"{m['quoted']:,} quoted, {m['quoteless']:,} quoteless")
        print(f"    semantic OWNER      : {m['owned']:,}  "
              f"({100 * m['owned'] / q:.2f}% of quoted)")
        print(f"    evidence LOCATED    : {located:,}  "
              f"({100 * located / q:.2f}% of quoted)   <- a different question")
        print(f"    span                : {m['span']:,}")
        print(f"    ambiguous           : {m['ambiguous']:,}")
        print(f"    unresolved          : {m['unresolved']:,}")
        print(f"  STORED in the codebook (a different question again)")
        print(f"    addressed           : {m['stored_owned']:,}")
        print(f"    stored_mismatch     : {m['stored_mismatch']:,}   "
              f"<- stored address disagrees with the resolver today")
        print(f"    addressable_missing : {m['addressable_missing']:,}   "
              f"<- resolver says OWNER but nothing is stored (must be 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
