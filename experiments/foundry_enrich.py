#!/usr/bin/env python3
"""T3-AXIS-FOUNDRY-v3.md -- supervisor-triage enrichment pass for a review
batch. Reads experiments/out/foundry/review/batch-N.json (foundry_emit.py's
output) and writes a SUPERSET-only sibling (batch-N-enriched.json): every
existing key is preserved verbatim, only new keys are added. Never touches
lane membership (which axis/other_lane a card is in) -- this is a read-only
enrichment for a human reviewing the JSON directly, not a reconciliation
step (that's foundry_reconcile.py's job against decisions/batch-N.json).

Corpus source (Captain's ruling, this session): tier_engine's own loader
(foundry_common.load_corpus() -> te.load_cards() over oracle-cards.jsonl.gz,
38,233 cards), NOT data/artifacts/cards.sqlite. cards.sqlite is the
production-shipped artifact and pipeline/build_db.py deliberately excludes
token/emblem/art_series/vanguard/scheme/planar layouts (EXCLUDED_LAYOUTS) --
6 of batch-1's own 476 cards (5 tokens + Mojave Desert, a Plane) are exactly
those excluded layouts, so cards.sqlite cannot resolve every card already
shipped in the file this script enriches. Using the same loader that built
the batch in the first place (foundry_emit.py -> fc.load_corpus()) keeps DF
counts consistent with every other foundry/engine DF computation in this
repo and resolves all 476 cards with zero HALTs.

Reminder-text source (Captain's ruling, this session): NOT the local CR
markdown. Verified live: the CR document (10,060 lines) only ever discusses
reminder text conceptually (207.2a's definition, glossary cross-references)
-- it never prints a single literal reminder-text string, so "CR 702
keyword reminder texts" cannot be extracted from that file. The actual
printed reminder text lives in the corpus itself; this script rebuilds the
canonical set by replaying tier_engine's own v2.9 Mechanism 2 detection
(is_keyword_only_paragraph + parse_keyword_instances + extract_reminder_
spans + normalize_reminder_body) over every face of every corpus card --
the same logic build_card_doc() already uses to identify and inject
reminder text, just run standalone here to collect the set rather than
build a scoring index. This intentionally skips strip_bespoke_ability_label
(needs a keyword_df floor irrelevant to reminder-text identification) --
a documented simplification, not a re-derivation of engine logic.

Usage: python3 experiments/foundry_enrich.py --in <batch.json> --out <enriched.json>
"""
import sys
import json
import re
import argparse
import itertools
import statistics
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import tier_engine as te  # noqa: E402
import foundry_common as fc  # noqa: E402
import foundry_consolidate as fcon  # noqa: E402

MIN_TOKENS_TO_GROUP = 2  # same floor as foundry_consolidate.cluster_instances' MIN_TOKENS_TO_MERGE


# ---------------------------------------------------------------------------
# 1. CARD ATTACHMENT
# ---------------------------------------------------------------------------

def full_oracle_text(card: dict) -> str:
    """All faces, joined -- reuses te.get_raw_faces so single-face and
    multi-face cards go through the identical code path the engine itself
    uses (never re-derives the card_faces-vs-root-oracle_text branch)."""
    return "\n".join(f["oracle_text"] for f in te.get_raw_faces(card) if f["oracle_text"])


def build_card_attachment(card: dict) -> dict:
    return {
        "name": card.get("name") or "",
        "oracle_text": full_oracle_text(card),
        "type_line": card.get("type_line") or "",
        "mana_cost": card.get("mana_cost") or "",
        "color_identity": card.get("color_identity") or [],
        "layout": card.get("layout") or "normal",
    }


def attach_cards(batch: dict, cards: dict) -> int:
    """Mutates batch in place. Returns count of oracle_ids attached."""
    unresolved = []
    n = 0
    for axis in batch["axes"]:
        for member in axis["members"]:
            oid = member["oracle_id"]
            if oid not in cards:
                unresolved.append(oid)
                continue
            member["card"] = build_card_attachment(cards[oid])
            n += 1
    for row in batch["other_lane"]:
        oid = row["oracle_id"]
        if oid not in cards:
            unresolved.append(oid)
            continue
        row["card"] = build_card_attachment(cards[oid])
        n += 1
    if unresolved:
        fc.halt(f"{len(set(unresolved))} oracle_id(s) referenced by the batch are not in the corpus "
                f"(never guess/fuzzy-resolve): {sorted(set(unresolved))[:10]}")
    return n


# ---------------------------------------------------------------------------
# 2. QUOTE-DF
# ---------------------------------------------------------------------------

def normalize_full_text_for_df(card: dict) -> str:
    """Per-card DF-search text: self-name substituted (engine's own
    self_name_candidates/normalize_self_references, run over ALL faces
    joined), then lowercased and whitespace-collapsed. Deliberately does
    NOT strip reminder text (normalize_clause_text does, but reminder text
    must stay searchable here -- REMINDER-TEXT FLAG needs quotes that ARE
    reminder restatements to actually substring-match against it)."""
    candidates = te.self_name_candidates(card.get("name") or "")
    keywords = card.get("keywords") or []
    text = full_oracle_text(card)
    text = te.normalize_self_references(text, candidates, keywords)
    text = text.lower()
    return te.WS_RE.sub(" ", text).strip()


def normalize_quote_for_df(quote: str, origin_card: dict) -> str:
    """Same three steps, applied to an evidence quote using ITS OWN origin
    card's self-name candidates/keywords -- so a quote that happens to
    mention its own card's name normalizes to '~' exactly like the corpus
    text it's being searched against, keeping cross-card generic-pattern
    matching apples-to-apples (DERIVED-TAG-LAYER-SPEC Lesson 2/N2)."""
    candidates = te.self_name_candidates(origin_card.get("name") or "")
    keywords = origin_card.get("keywords") or []
    text = te.normalize_self_references(quote, candidates, keywords)
    text = text.lower()
    return te.WS_RE.sub(" ", text).strip()


def compute_quote_df(batch: dict, cards: dict) -> dict:
    """Returns normalized_quote -> df (count of corpus cards whose
    normalized full text contains normalized_quote as a substring).
    Scans the WHOLE corpus (all cards passed in), not just the 476 cards
    in this batch -- quote_df is a corpus-wide reach proxy."""
    print(f"building normalized DF-search text for {len(cards):,} corpus cards...")
    corpus_texts = [normalize_full_text_for_df(c) for c in cards.values()]

    df_cache = {}

    def df_for(norm_quote: str) -> int:
        if norm_quote not in df_cache:
            df_cache[norm_quote] = sum(1 for t in corpus_texts if norm_quote in t)
        return df_cache[norm_quote]

    return df_for, df_cache


# ---------------------------------------------------------------------------
# 3. REMINDER-TEXT FLAG
# ---------------------------------------------------------------------------

def build_reminder_text_set(cards: dict) -> set:
    """Replays tier_engine's v2.9 Mechanism 2 (build_card_doc) over every
    face of every corpus card to collect the canonical set of printed
    reminder-text bodies, normalized identically to normalize_reminder_body
    (lowercase + whitespace-collapse -- reminder bodies carry no reminder
    text of their own to strip). All-paragraph, all-face scanning
    (mandatory per standing ruling -- Vexing Shusher lesson)."""
    reminders = set()
    for card in cards.values():
        candidates = te.self_name_candidates(card.get("name") or "")
        keywords = card.get("keywords") or []
        for face in te.get_raw_faces(card):
            substituted = te.normalize_self_references(face["oracle_text"], candidates, keywords)
            for p in substituted.split("\n"):
                if not p.strip():
                    continue
                norm = te.normalize_clause_text(p)
                if not norm or not te.is_keyword_only_paragraph(norm, keywords):
                    continue
                frag_instances = te.parse_keyword_instances(norm, keywords)
                if len(frag_instances) != 1:
                    continue
                spans = te.extract_reminder_spans(p)
                if not spans:
                    continue
                reminder_text = te.normalize_reminder_body(" ".join(spans))
                if reminder_text:
                    reminders.add(reminder_text)
    return reminders


def reminder_restatement_kind(norm_quote: str, reminder_set: set) -> str | None:
    """Returns 'exact', 'substring', or None. NOTE (worth Captain's eyes,
    not silently special-cased): the spec's own substring rule means a
    short bare-keyword quote ("Haste", "Flash") flags true whenever it
    happens to occur inside some UNRELATED keyword's longer reminder text
    (e.g. Unearth's reminder literally says "...it gains haste...") --
    verified live: of 83 flagged quotes in batch 1, only 4 are exact
    matches (genuine reminder-text restatements); 79 are substring-only
    hits on short keyword-name quotes. Flagged as specified, not filtered
    by quote length -- that threshold would be a judgment call this task
    doesn't authorize."""
    if norm_quote in reminder_set:
        return "exact"
    if any(norm_quote in rt for rt in reminder_set):
        return "substring"
    return None


# ---------------------------------------------------------------------------
# 4. OTHER-LANE TOKEN GROUPING
# ---------------------------------------------------------------------------

def build_token_groups(other_lane: list) -> list:
    """foundry_consolidate.cluster_instances groups by IDENTICAL normalized
    label token set -- which is exactly why every one of these 1,040 rows
    is already HERE in other_lane: that clustering pass already pulled out
    every row whose full token set matched another's (those became axis
    candidates), leaving only rows with a unique full set. Grouping by
    full-set equality again would therefore always yield zero groups
    (verified live). "Minus the merge step" instead means: reuse the same
    tokenization (normalize_tokens: stopwording + stemming), but group on
    PARTIAL overlap -- any 2 label-tokens shared by 2+ rows' token sets --
    which is the literal "sharing 2+ label tokens" spec language. Indexed
    by exact 2-token combination (not single-linkage/Jaccard chaining,
    which foundry_consolidate's own docstring documents as unreliable:
    it chained unrelated concepts through one shared generic token). Rows
    can appear in more than one group -- expected for a viewing aid, not a
    partition; it changes nothing about lane membership."""
    pair_groups = defaultdict(list)
    for idx, row in enumerate(other_lane):
        tokens = sorted(fcon.normalize_tokens(row["label"]))
        if len(tokens) < MIN_TOKENS_TO_GROUP:
            continue
        for combo in itertools.combinations(tokens, MIN_TOKENS_TO_GROUP):
            pair_groups[combo].append(idx)

    out = []
    for tokens, idxs in pair_groups.items():
        if len(idxs) < 2:
            continue
        members = sorted(
            ({"oracle_id": other_lane[i]["oracle_id"], "label": other_lane[i]["label"],
              "quote": other_lane[i]["quote"]} for i in idxs),
            key=lambda m: (m["oracle_id"], m["label"]),
        )
        out.append({"tokens": list(tokens), "size": len(members), "members": members})

    out.sort(key=lambda g: (-g["size"], g["tokens"]))
    return out


# ---------------------------------------------------------------------------
# 5. DISCARD AUDIT
# ---------------------------------------------------------------------------

def build_discard_audit(cards: dict) -> list:
    """Re-runs the Stage-1B evidence-quote-or-discard gate (foundry_
    consolidate.load_raw_instances) to recover the discarded instances, then
    checks each discarded quote against ALL faces of that card's oracle
    text independently of the original gate's own join logic -- if the
    quote turns up on a face the gate's join should have already covered,
    that's a genuine face-scanning miss and gets reported LOUDLY. Nothing
    is re-admitted; this only reports."""
    _, discarded = fcon.load_raw_instances(cards)
    audit = []
    for d in discarded:
        if d["reason"] != "quote not verbatim in oracle text":
            continue
        oid = d["oracle_id"]
        card = cards[oid]
        quote = d["axis"]["evidence_quote"]
        quote_lower = quote.lower()
        faces = te.get_raw_faces(card)
        face_hits = [f["name"] for f in faces if quote_lower in (f["oracle_text"] or "").lower()]
        audit.append({
            "oracle_id": oid,
            "name": card.get("name"),
            "proposed_label": d["axis"]["label"],
            "quote": quote,
            "found_on_faces": face_hits,
            "face_scanning_miss": bool(face_hits),
        })
    audit.sort(key=lambda a: a["oracle_id"])
    return audit


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def enrich(in_path: Path, out_path: Path) -> dict:
    with open(in_path, "r", encoding="utf-8") as f:
        batch = json.load(f)

    print("loading corpus (tier_engine loader, oracle-cards.jsonl.gz)...")
    cards, _ = fc.load_corpus()
    print(f"loaded {len(cards):,} corpus cards")

    # --- 1. CARD ATTACHMENT ---
    n_attached = attach_cards(batch, cards)
    print(f"\n[1] card attachment: {n_attached} member/other_lane rows attached")

    # --- 2. QUOTE-DF ---
    df_for, df_cache = compute_quote_df(batch, cards)
    print("[2] computing quote_df for every axis member and other_lane row...")
    for axis in batch["axes"]:
        dfs = []
        for member in axis["members"]:
            origin = cards[member["oracle_id"]]
            norm_q = normalize_quote_for_df(member["quote"], origin)
            member["quote_df"] = df_for(norm_q)
            dfs.append(member["quote_df"])
        axis["quote_df_min"] = min(dfs)
        axis["quote_df_median"] = statistics.median(dfs)
        axis["quote_df_max"] = max(dfs)
    for row in batch["other_lane"]:
        origin = cards[row["oracle_id"]]
        norm_q = normalize_quote_for_df(row["quote"], origin)
        row["quote_df"] = df_for(norm_q)
    print(f"    unique normalized quotes scanned: {len(df_cache)}")

    # --- 3. REMINDER-TEXT FLAG ---
    print("[3] building corpus-derived CR 702 reminder-text set...")
    reminder_set = build_reminder_text_set(cards)
    print(f"    {len(reminder_set)} distinct reminder-text bodies found corpus-wide")
    flagged = 0
    exact_count = 0
    substring_count = 0
    for axis in batch["axes"]:
        for member in axis["members"]:
            origin = cards[member["oracle_id"]]
            norm_q = normalize_quote_for_df(member["quote"], origin)
            kind = reminder_restatement_kind(norm_q, reminder_set)
            member["reminder_restatement"] = kind is not None
            flagged += member["reminder_restatement"]
            exact_count += kind == "exact"
            substring_count += kind == "substring"
    for row in batch["other_lane"]:
        origin = cards[row["oracle_id"]]
        norm_q = normalize_quote_for_df(row["quote"], origin)
        kind = reminder_restatement_kind(norm_q, reminder_set)
        row["reminder_restatement"] = kind is not None
        flagged += row["reminder_restatement"]
        exact_count += kind == "exact"
        substring_count += kind == "substring"
    print(f"    flagged {flagged} evidence quote(s) as reminder-text restatements "
          f"({exact_count} exact match, {substring_count} substring-only -- see "
          f"reminder_restatement_kind()'s docstring for why substring-only dominates)")

    # --- 4. OTHER-LANE TOKEN GROUPING ---
    print("[4] grouping OTHER-lane rows by shared normalized label tokens...")
    token_groups = build_token_groups(batch["other_lane"])
    batch["token_groups"] = token_groups
    print(f"    {len(token_groups)} groups of 2+ rows sharing 2+ label tokens")

    # --- 5. DISCARD AUDIT ---
    print("[5] auditing Stage 1B evidence-gate discards...")
    discard_audit = build_discard_audit(cards)
    batch["discard_audit"] = discard_audit
    face_scanning_misses = [a for a in discard_audit if a["face_scanning_miss"]]
    print(f"    {len(discard_audit)} discarded instance(s) audited, {len(face_scanning_misses)} face-scanning miss(es)")
    if face_scanning_misses:
        print(f"    !!! LOUD: face-scanning miss(es) found: {face_scanning_misses}")

    stats = {
        "n_axes": len(batch["axes"]),
        "n_axis_members": sum(len(a["members"]) for a in batch["axes"]),
        "n_other_lane": len(batch["other_lane"]),
        "n_cards_attached": n_attached,
        "n_corpus_cards_scanned": len(cards),
        "n_unique_normalized_quotes": len(df_cache),
        "n_reminder_texts_found": len(reminder_set),
        "n_reminder_restatements_flagged": flagged,
        "n_reminder_restatements_exact": exact_count,
        "n_reminder_restatements_substring_only": substring_count,
        "n_token_groups": len(token_groups),
        "n_discard_audited": len(discard_audit),
        "n_discard_face_scanning_misses": len(face_scanning_misses),
        "discard_audit_all_non_oracle_text_fields": all(
            not a["found_on_faces"] for a in discard_audit
        ),
    }
    batch["enrichment_stats"] = stats

    fc.write_json(out_path, batch)
    print(f"\nwrote {out_path}")

    stats_path = out_path.with_name(out_path.stem + "-stats.json")
    fc.write_json(stats_path, stats)
    print(f"wrote {stats_path}")
    return stats


def print_stats(stats: dict) -> None:
    print("\n=== STATS SUMMARY ===")
    for k in sorted(stats.keys()):
        print(f"  {k}: {stats[k]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out", dest="out_path", required=True)
    args = parser.parse_args()

    stats = enrich(Path(args.in_path), Path(args.out_path))
    print_stats(stats)


if __name__ == "__main__":
    main()
