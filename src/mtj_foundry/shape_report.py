"""Ability-shape censuses — the `--gaps`, `--action` and `--rank` operator reports.

## What this is

The operator censuses S7 left in the legacy `foundry_shape_extractor` shell:
which delivery shapes have no ratified token (and what hides inside the
`spell-or-static` bucket), every card printing one CR keyword action grouped by
delivery, and every CR 701 action ranked by how much is buildable today. S13
moved the aggregation and every printed line here. Output is the shell's,
character for character.

## What this is NOT

* **Not the shape parse.** `scan`, `deliveries_for_lines`, `find_action`,
  `_has_spell_face` and the delivery vocabulary are
  `mtj_foundry.mtg.shapes.delivery`; they reach this module as callables from
  the composition boundary, which wraps them in its historic `STOP — …`.
* **Not a reader, writer or CLI.** The corpus, the grammar and CR-check reads,
  the codebook-coverage read and its handler, argument parsing, the `--json`
  writes and printing all stay at the boundary, where committed guards pin them.
"""

from __future__ import annotations

import collections
import re

__all__ = ["action_lines", "gaps", "rank_lines", "unknown_action_message"]


def gaps(rows: list, cards: dict, ratified: dict, limit: int, has_spell_face) -> tuple:
    """(printed lines, `--json` document) for the unratified-delivery census."""
    gap = collections.Counter()
    cardset = collections.defaultdict(set)
    inside = collections.defaultdict(collections.Counter)
    inside_cards = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        if r["delivery"] is not None:
            continue
        if r["descriptor"] not in ("spell-or-static",):
            gap[r["descriptor"]] += 1
            cardset[r["descriptor"]].add(r["name"])
        else:
            # THE CENSUS WAS BLIND HERE BY CONSTRUCTION, and this is where
            # almost all of the unrouted mass lives: 14,898 of 15,902 lines,
            # 93.7%. The exclusion is right -- these are not missing
            # VOCABULARY, which is what the table above ranks -- but "excluded
            # from this table" turned into "unreportable", and 236 CR 614.1c
            # replacement effects hid in here indefinitely.
            #
            # CR 113.3a decides the split and needs no new vocabulary to do it:
            # *"a spell ability ... is an ability that functions only while the
            # spell is on the stack"*, and a spell is an instant or a sorcery.
            # So a card with NO instant/sorcery face leaves CR 113.3's
            # four-category enumeration closed on `static` -- the line is
            # decidably a static ability that simply has no branch yet. A card
            # WITH such a face is genuinely undecidable from its faces alone,
            # and grammar §1 makes the unmarked default correct for it anyway.
            key = ("CR 113.3a closes: decidably STATIC"
                   if not has_spell_face(cards[r["oracle_id"]])
                   else "undecidable — has an instant/sorcery face (§1 default)")
            shape = " ".join(re.sub(r"[^\w\s'’—•|+{}/-]", "", r["line"].strip())
                             .split()[:3]).lower()
            inside[key][shape] += 1
            inside_cards[key][shape].add(r["name"])
    out = [f"ratified DELIVERY tokens parsed from grammar §2: {len(ratified)}",
           f"  {', '.join(sorted(ratified))}\n",
           f"ability lines scanned: {len(rows)}   gate-passing cards: {len(cards)}\n",
           f"{'unratified delivery shape':38s} {'lines':>7} {'cards':>7}",
           "-" * 56]
    for desc, n in gap.most_common():
        out.append(f"{desc:38s} {n:7d} {len(cardset[desc]):7d}")

    total_inside = sum(sum(c.values()) for c in inside.values())
    out += [f"\n{'=' * 68}",
            f"INSIDE `spell-or-static` — {total_inside} lines the table above CANNOT see",
            f"{'=' * 68}",
            "This bucket is excluded from the census because it is not missing",
            "VOCABULARY. But excluded became unreportable, and 236 CR 614.1c",
            "replacement effects once hid here indefinitely. CR 113.3a splits it",
            "with no new vocabulary at all:\n"]
    for key in sorted(inside, key=lambda k: -sum(inside[k].values())):
        n = sum(inside[key].values())
        out.append(f"  {key:52}{n:>7}  ({n / total_inside:.1%})")
    out += ["\nSo the headline 'unrouted' number is not a gap count. Most of it is",
            "grammar §1's UNMARKED DEFAULT for a spell ability, which is correct",
            "and needs nothing. The decidably-static half is the real queue.\n"]
    for key in sorted(inside, key=lambda k: -sum(inside[k].values())):
        out.append(f"--- {key} — top opening shapes ---")
        out.append(f"  {'shape':34}{'lines':>7}{'cards':>7}")
        for shape, n in inside[key].most_common(limit):
            out.append(f"  {shape:34}{n:>7}{len(inside_cards[key][shape]):>7}")
        out.append("")
    document = {d: {"lines": n, "cards": sorted(cardset[d])} for d, n in gap.most_common()}
    return out, document


def unknown_action_message(action: str, actions: dict):
    """The refusal for a term that is not in the CR check registry, or None."""
    if action in actions:
        return None
    near = [t for t in actions if action in t]
    return (f"{action!r} is not a CR term in cr-checks.json. "
            f"Did you mean: {', '.join(near[:8]) or '(no near matches)'}")


def action_lines(action: str, meta: dict, rows: list, limit: int) -> list:
    """Every card printing one CR keyword action, grouped by delivery shape."""
    groups = collections.defaultdict(list)
    for r in rows:
        key = r["delivery"] or f"UNRATIFIED:{r['descriptor']}"
        if r["created_ability"] and r["delivery"] is None:
            key = "UNRATIFIED:created-ability(§2)"
        groups[key].append(r)
    cards_hit = {r["oracle_id"] for r in rows}
    out = [f"CR {meta['cr']}  {action}  ({meta['kind']})",
           f"forms: {', '.join(meta['forms'])}",
           f"cards: {len(cards_hit)}   ability lines: {len(rows)}\n"]
    ready = sum(len(v) for k, v in groups.items() if not k.startswith("UNRATIFIED"))
    out.append(f"  buildable now (ratified delivery): {ready} lines")
    out.append(f"  need a ruling:                     {len(rows) - ready} lines\n")
    for key in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        rs = groups[key]
        out.append(f"## {key}   n={len(rs)}")
        for r in sorted(rs, key=lambda r: r["name"])[:limit]:
            out.append(f"   {r['name'][:36]:38s} {r['line'][:88]}")
        if len(rs) > limit:
            out.append(f"   … and {len(rs) - limit} more")
        out.append("")
    return out


def rank_lines(cards: dict, ratified: dict, actions: dict, covered: set, limit: int,
               deliveries_for_lines, find_action):
    """Rank every CR 701 keyword action by how much of it is buildable today.

    Single corpus pass -- one delivery parse per ability line, matched against
    every action at once. Scanning per-action instead would be 262 full passes.
    The lines are returned after the whole pass, so a refusal inside the parse
    still stops before anything is printed.
    """
    # CR 701 is the keyword-ACTION section. 702 keywords (flying, trample) are
    # static/evasion abilities, not actions, and they are the keyword-bucket
    # job -- including them buries the population this ranking is about.
    actions = {t: m for t, m in actions.items() if str(m["cr"]).startswith("701.")}
    stat = collections.defaultdict(lambda: {"cards": set(), "ready": 0, "blocked": 0})
    for oid, card in cards.items():
        for line, line_parsed in deliveries_for_lines(card, ratified):
            parsed = None
            for term, meta in actions.items():
                form, _ = find_action(line, meta["forms"])
                if form is None:
                    continue
                if parsed is None:
                    parsed = line_parsed
                s = stat[term]
                s["cards"].add(oid)
                for tok, _d in parsed:
                    if tok:
                        s["ready"] += 1
                    else:
                        s["blocked"] += 1
    out = [f"{'CR action':24s} {'CR':>8} {'cards':>6} {'ready':>6} {'blocked':>7} {'%':>6}  axis?",
           "-" * 72]
    rows = sorted(stat.items(), key=lambda kv: -len(kv[1]["cards"]))
    for term, s in rows[:limit]:
        n = s["ready"] + s["blocked"]
        pct = 100.0 * s["ready"] / n if n else 0.0
        out.append(f"{term:24s} {actions[term]['cr']:>8} {len(s['cards']):6d} "
                   f"{s['ready']:6d} {s['blocked']:7d} {pct:5.1f}%  "
                   f"{'yes' if term in covered else 'NO AXIS'}")
    return out
