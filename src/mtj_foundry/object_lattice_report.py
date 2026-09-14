"""Object-lattice operator — measurement report, negative-control audit, samples.

## What this is

The operator half S7/S9/S11 left in the legacy `foundry_object_lattice` shell:
the CLI modes (`--invariant`, `--report`, the default measurement, `--residual`,
`--audit`, `--samples`), the NC1-NC4 audit, the mutually-exclusive-mode report,
the per-quote locality view for the review sheet, and the ratification-packet
composition. S13 moved them here. Every flag, printed line, exit code and output
byte is the shell's.

## What this is NOT

* **Not the lattice.** Target-class extraction, `measure`, the residual
  invariant and `rule:targeted-*` identity are `mtj_foundry.mtg.shapes.
  target_classes` and `mtj_foundry.codebook_lattice`; slug validation is
  `mtj_foundry.codebook_slug`; locality is `mtj_foundry.mtg.shapes.locality`.
  They arrive as callables from the composition boundary, behind its historic
  `STOP — …`, and with the injected card-text rules they depend on.
* **Not a reader or writer.** The corpus load, the protected codebook read, both
  report writes and every path are the boundary's. `sample_packet` returns the
  documents; it writes nothing.
"""

from __future__ import annotations

import argparse
import dataclasses
import random
import re
from collections import defaultdict
from typing import Any, Callable

__all__ = ["ObjectLatticeContext", "audit", "exclusivity_report", "locality_of",
           "run", "sample_packet"]


@dataclasses.dataclass(frozen=True)
class ObjectLatticeContext:
    description: str
    report_help: str
    generated_by: str
    subtype_source: str
    action_verbs: dict
    clause_res: dict
    permanent_types: set
    card_types: set
    permanent_forms: Any
    load_cards: Callable[[], dict]
    measure: Callable[..., dict]
    residual_invariant: Callable[..., dict]
    slug_for: Callable[..., str]
    clauses_for: Callable[..., Any]
    classes_for_card: Callable[..., dict]
    full_oracle_text: Callable[[dict], str]
    validate_slug: Callable[..., dict]
    resolve: Callable[[dict, str], dict]
    owning_header: Callable[[dict, Any], dict]
    mutually_exclusive: Callable[[dict, Any, Any], bool]
    owner_status: Callable[[], str]
    locality_of: Callable[[dict, str], dict]
    exclusivity: Callable[[dict], list]
    audit: Callable[[str, set], dict]
    write_report: Callable[[int, int], dict]


def audit(stem: str, domain: set, ctx: ObjectLatticeContext) -> dict:
    """The negative controls. A guard that has never been shown to fail is not
    known to be a guard, so each of these was run against the live corpus and
    its output READ, card by card, before being written down here.

    NC1  every claimed card prints the word `destroy` — CR 701.8b's first of
         exactly two routes to destruction, and the only one this reads.
    NC2  a card with no targeted clause yields nothing (the extractor cannot
         invent a membership).
    NC3  quoted grants are reported, not silently included. All 16 were read
         2026-08-09: self-grants (Harmonic Sliver IS a Sliver) and Equipment
         grants (Heartseeker). Both genuinely hand the player that removal, so
         they are TAGGED — grammar §2's quoted-grant exclusion governs
         DELIVERY, and the class slot is an EFFECT question. Captain's ratified
         criterion is deck-building relevance.
    NC4  no emitted slug may fall outside the ratified grammar — every one is
         re-validated through slug validation.
    """
    cards = ctx.load_cards()
    qspan = re.compile(r"[\"“]([^\"”]*)[\"”]")
    dest = ctx.clause_res[stem]
    no_verb, quoted_only, silent, bad_slug = [], [], 0, []
    # NC1 must test the PRINTED verb, not the slug stem. `bounce` is a ratified
    # stem that no card prints -- they print `return` -- so keying this on the
    # stem flagged every bounce card. A probe defect in the negative control
    # itself, which is the default outcome and why this note stays.
    verb_word = ctx.action_verbs[stem]["word"]
    for oid, card in cards.items():
        clauses = list(ctx.clauses_for(card, stem))
        if not clauses:
            silent += 1
            continue
        full = ctx.full_oracle_text(card)
        if verb_word not in full.lower():
            no_verb.append(card["name"])
        spans = [m.span(1) for m in qspan.finditer(full)]
        hits = [m.start() for m in dest.finditer(full)]
        if hits and all(any(a <= h < b for a, b in spans) for h in hits):
            quoted_only.append(card["name"])

    for cls in sorted(domain | {f for f, _ in ctx.permanent_forms}):
        slug = ctx.slug_for(stem, cls)
        v = ctx.validate_slug(slug, definition=None, all_slugs=[])
        if not v["ok"]:
            bad_slug.append((slug, v.get("failures") or v.get("reason")))
    return {"nc1_no_verb": no_verb, "nc2_silent": silent,
            "nc3_quoted_only": quoted_only, "nc4_bad_slug": bad_slug}


def locality_of(card: dict, quote: str, resolve, owning_header) -> dict:
    """The semantic owner of one proving quote, for the review sheet.

    Consumes the locality law rather than re-deriving coordinates -- a second
    implementation of the resolution law is exactly the re-implementation
    defect class this repository keeps paying for.
    """
    r = resolve(card, quote)
    out = {"status": r["status"], "owner": list(r["owner"]) if r["owner"] else None}
    if r["owner"]:
        h = owning_header(card, r["owner"])
        if h["modal"]:
            out["modal_header"] = list(h["header"])
    return out


def exclusivity_report(cards: dict, ctx: ObjectLatticeContext) -> list:
    """Cards whose lattice facts come from MUTUALLY EXCLUSIVE modes.

    This is the 41-card flattening population the locality ratification exists
    to fix, now reported with the owners that prove it. Reported, never
    written: what a consumer does with exclusivity is a consumer decision.
    """
    rows = []
    for oid, card in sorted(cards.items(), key=lambda kv: kv[1]["name"]):
        owned = {}
        for stem in sorted(ctx.action_verbs):
            r = ctx.classes_for_card(card, stem, ctx.permanent_types)
            for cls in sorted(r["classes"]):
                res = ctx.resolve(card, r["quotes"][cls])
                if res["status"] == ctx.owner_status():
                    owned[ctx.slug_for(stem, cls)] = res["owner"]
        pairs = []
        keys = sorted(owned)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if ctx.mutually_exclusive(card, owned[a], owned[b]):
                    pairs.append({"a": a, "b": b,
                                  "owner_a": list(owned[a]),
                                  "owner_b": list(owned[b])})
        if pairs:
            rows.append({"card": card["name"], "oracle_id": oid,
                         "exclusive_pairs": pairs})
    return rows


def sample_packet(seed: int, n: int, cards: dict, axis_status, ctx: ObjectLatticeContext) -> tuple:
    """(report document, Markdown text) for the ratification packet.

    `axis_status(slug)` is the boundary's answer from its protected codebook
    read, or None when that read failed. **Quotes go in the FILE, never to
    console (A14).**"""
    actions = {}
    proposed_patterns = []
    for idx, stem in enumerate(sorted(ctx.action_verbs)):
        m = ctx.measure(stem, ctx.permanent_types)
        rng = random.Random(seed)
        by_class = defaultdict(list)
        for oid, r in m["hits"].items():
            for c in r["classes"]:
                by_class[c].append((oid, r["quotes"][c]))
        classes = {}
        for cls in sorted(by_class):
            pool = sorted(by_class[cls])
            slug = ctx.slug_for(stem, cls)
            exists = axis_status(slug)
            classes[cls] = {
                "slug": slug,
                "members": len(pool),
                "axis_status_today": exists or "ABSENT — self-instantiates per b6 §11.2",
                # SEMANTIC LOCALITY on NEW rule-derived output (roadmap step 3,
                # ratified 2026-08-13). The lattice is the first producer to
                # emit an address, and it emits into the REPORT only -- this
                # sheet is a review artifact, not provenance. Wiring an address
                # into the assertion payload the DET apply WRITES is the
                # backfill migration, which is a codebook mutation under the
                # backup law and is deliberately not done here.
                "sample": [{"card": cards[o]["name"], "oracle_id": o,
                            "quote": q,
                            "locality": ctx.locality_of(cards[o], q)}
                           for o, q in rng.sample(pool, min(n, len(pool)))],
            }
        actions[stem] = {
            "printed_verb": ctx.action_verbs[stem]["word"],
            "cards": m["cards"], "memberships": m["memberships"],
            "multi_class_cards": sum(v for k, v in m["n_classes"].items() if k > 1),
            "residual": [{"card": c, "clause": q} for c, q in m["residual"]],
            "conjunctive_cr300_2": m["conjunctive"],
            "classes": classes,
        }
        proposed_patterns.append({
            "slug": ctx.slug_for(stem),
            "lattice": True,
            "class_domain": "CR 110.4 permanent types + permanent/nonland/noncreature forms",
            "pattern": ctx.clause_res[stem].pattern,
            "status": "PROPOSED — not ratified, not written to det-patterns-v2.json",
            "cr_anchor": {"destroy": "701.8a/701.8b", "exile": "406.1",
                          "bounce": "zone change to hand"}.get(stem),
            "note": "One matcher -> N axes. det-patterns-v2.json's schema is "
                    "slug + one regex -> one axis; this needs the lattice "
                    "extension before it can be an entry.",
        })

    report = {
        "schema": "foundry-object-lattice-samples/1",
        "generated_by": ctx.generated_by,
        "law": "M8 generalized (b6 D3), MASTER-HANDOFF-ADDENDUM-4.md §4; "
               "lattice grammars b6 §11.2 (virtual nodes self-instantiate on "
               "first quote-verified member, no fresh ratification)",
        "record": "docs/OBJECT-LATTICE-2026-08-09.md",
        "seed": seed, "sample_size": n,
        "cr_sources": {
            "permanent_types_110_4": sorted(ctx.permanent_types),
            "card_types_205_2a": len(ctx.card_types),
            "subtype_lists_205_3": ctx.subtype_source,
        },
        "actions": actions,
        "mutually_exclusive_facts": ctx.exclusivity(cards),
        "proposed_det_patterns": proposed_patterns,
    }

    lines = ["# OBJECT LATTICE — sample sheet for ratification", "",
             f"Seed `{seed}`, {n} rows per class. Record: "
             f"`docs/OBJECT-LATTICE-2026-08-09.md`.", "",
             "Standing condition (`det-patterns-v2.json`): **any sample row "
             "failing its axis definition halts the pass before provenance "
             "writes.**", ""]
    for stem, a in actions.items():
        lines += [f"## `targeted-{stem}` — printed *{a['printed_verb']}*", "",
                  f"{a['cards']:,} cards · **{a['memberships']:,} memberships** · "
                  f"{a['multi_class_cards']} multi-class · "
                  f"{len(a['residual'])} residual", ""]
        for cls, c in a["classes"].items():
            lines += [f"### `{c['slug']}` — {c['members']:,} members "
                      f"({c['axis_status_today']})", ""]
            for row in c["sample"]:
                lines.append(f"- **{row['card']}** — {row['quote']}")
            lines.append("")
        if a["residual"]:
            lines += ["**Residual (no class named):**", ""]
            lines += [f"- {r['card']} — {r['clause']}" for r in a["residual"][:20]]
            lines.append("")
    return report, "\n".join(lines)


def build_parser(ctx: ObjectLatticeContext) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=ctx.description,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--action", default="destroy", choices=sorted(ctx.action_verbs))
    ap.add_argument("--domain", default="permanent",
                    choices=["permanent", "card"],
                    help="permanent = CR 110.4 (destroy); card = CR 205.2a")
    ap.add_argument("--residual", action="store_true",
                    help="print the clauses that matched the action but named "
                         "NO class — where the defects are")
    ap.add_argument("--audit", action="store_true",
                    help="run the negative controls (NC1-NC4) and exit 1 on "
                         "any hard failure")
    ap.add_argument("--update-baseline", action="store_true",
                    help="accept the current membership/residual counts ON "
                         "PURPOSE. A membership count that FELL is a "
                         "regression until it is re-pinned here.")
    ap.add_argument("--invariant", action="store_true",
                    help="the residual invariant: HALT if any residual clause "
                         "still carries a target arm resolving to a battlefield "
                         "class. Runs over ALL actions, not just --action.")
    ap.add_argument("--selftest", action="store_true",
                    help="negative control for --invariant: drop the zone "
                         "explanation, so it must report a failure")
    ap.add_argument("--samples", type=int, default=0, metavar="N",
                    help="fixed-seed sample of N cards per class, for the DET "
                         "standing condition's per-pattern verification")
    ap.add_argument("--seed", type=int, default=20260809)
    ap.add_argument("--report", type=int, default=0, metavar="N", help=ctx.report_help)
    return ap


def run(argv, ctx: ObjectLatticeContext) -> int:
    args = build_parser(ctx).parse_args(argv)

    if args.invariant:
        bad = 0
        for stem in sorted(ctx.action_verbs):
            r = ctx.residual_invariant(stem, ctx.permanent_types, selftest=args.selftest)
            print(f"targeted-{stem}: {len(r['explained'])} explained by a "
                  f"printed CR zone origin, {len(r['unexplained'])} UNEXPLAINED")
            for name, arm, cls, quote in r["unexplained"]:
                print(f"    {name}: arm {arm!r} -> {ctx.slug_for(stem, cls)}")
                print(f"        {quote}")
            bad += len(r["unexplained"])
        if bad:
            print(f"\n  RESIDUAL INVARIANT FAILED: {bad} live arm(s) in "
                  f"residual. The pass HALTS before provenance writes.")
            return 1
        print("\n  residual invariant holds")
        return 0

    if args.report:
        r = ctx.write_report(args.seed, args.report)
        print("wrote the ratification packet (quotes are in the files, not here)")
        print(f"  {r['json']}")
        print(f"  {r['md']}")
        for stem, n in r["actions"].items():
            print(f"  targeted-{stem}: {n:,} memberships")
        return 0

    domain = ctx.permanent_types if args.domain == "permanent" else ctx.card_types
    print(f"CR 110.4 permanent types : {sorted(ctx.permanent_types)}")
    print(f"CR 205.2a card types     : {len(ctx.card_types)}")
    print(f"domain for `{args.action}` : {args.domain} ({len(domain)})\n")

    m = ctx.measure(args.action, domain)
    print(f"cards with a targeted `{args.action}` clause and >=1 class: "
          f"{m['cards']:,}")
    print(f"memberships the ratified lattice implies : {m['memberships']:,}")
    print(f"  per class      : {dict(m['per_class'].most_common())}")
    print(f"  by class count : {dict(sorted(m['n_classes'].items()))}")
    print(f"  multi-class    : {sum(v for k, v in m['n_classes'].items() if k > 1):,}"
          f"  <- the population M8 is about")
    for combo, n in m["combos"].most_common(10):
        print(f"      {n:>4}  {' + '.join(combo)}")
    print(f"\n  CR 300.2 conjunctive ('artifact creature', ONE object): "
          f"{len(m['conjunctive'])}  <- UNRULED, reported not decided")
    print(f"  qualified clauses (restriction the class slot cannot hold): "
          f"{len(m['qualified']):,}")
    print(f"  residual (action matched, no class named): {len(m['residual'])}")
    if args.residual:
        for name, clause in m["residual"][:60]:
            print(f"      {name}: {clause}")

    if args.audit:
        a = ctx.audit(args.action, domain)
        print("\n--- negative controls " + "-" * 50)
        print(f"  NC1 claimed without the printed verb "
              f"`{ctx.action_verbs[args.action]['word']}` (CR 701.8b): "
              f"{len(a['nc1_no_verb'])}   must be 0")
        print(f"  NC2 cards yielding nothing                   : "
              f"{a['nc2_silent']:,}")
        print(f"  NC3 clause only inside a quoted grant        : "
              f"{len(a['nc3_quoted_only'])}   reported, tagged on purpose")
        for name in a["nc3_quoted_only"]:
            print(f"        {name}")
        print(f"  NC4 emitted slugs failing validate_slug      : "
              f"{len(a['nc4_bad_slug'])}   must be 0")
        for slug, why in a["nc4_bad_slug"]:
            print(f"        {slug}: {why}")
        if a["nc1_no_verb"] or a["nc4_bad_slug"]:
            print("\n  AUDIT FAILED")
            return 1
        print("\n  audit clean")

    if args.samples:
        rng = random.Random(args.seed)
        by_class = defaultdict(list)
        for oid, r in m["hits"].items():
            for c in r["classes"]:
                by_class[c].append((oid, r["quotes"][c]))
        print(f"\n--- fixed-seed samples (seed {args.seed}) " + "-" * 30)
        cards = ctx.load_cards()
        for cls in sorted(by_class):
            pool = sorted(by_class[cls])
            pick = rng.sample(pool, min(args.samples, len(pool)))
            print(f"\n  {ctx.slug_for(args.action, cls)}  (n={len(pool)})")
            for oid, q in pick:
                print(f"      {cards[oid]['name']:<34} | {q[:78]}")
    return 0
