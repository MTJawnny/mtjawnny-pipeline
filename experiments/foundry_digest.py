#!/usr/bin/env python3
"""SUP-TRIAGE-PROTOCOL.md -- DIGEST artifact generator. Reads a batch's
enriched review JSON (foundry_enrich.py's output) and writes
experiments/out/foundry/review/digest-batch-<N>.md: per-axis header line
(slug | scope | n | quote-DF min/med/max | reminder-count) + definition +
one line per member (name, quote-DF, reminder flag, quote truncated to
<=80 chars); OTHER-lane token groups sorted by size (member labels AND
card names); a stats block; an Alchemy-row / non-normal-layout anomaly
list.

Deterministic by construction: every list is explicitly sorted (never
relies on incidental dict/set iteration order), no wall-clock timestamp is
embedded (that alone would break the x2 byte-identical determinism gate).

Completeness over the ~60KB size target where they conflict: this NEVER
drops an axis or a token group with 2+ distinct cards (per the protocol's
own artifact contract and this run's instructions) -- if that makes a
batch's digest land over ~60KB, the actual size is reported honestly
rather than silently violated to hit the target.

Usage: python3 experiments/foundry_digest.py --batch 2
"""
import sys
import json
import argparse
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "experiments"))
import foundry_common as fc  # noqa: E402

ALCHEMY_PREFIX = "A-"
QUOTE_TRUNC = 80


def truncate_quote(q: str) -> str:
    q = q.replace("\n", " ")
    if len(q) <= QUOTE_TRUNC:
        return q
    return q[: QUOTE_TRUNC - 1] + "…"


def axis_block(axis: dict) -> list:
    members = axis["members"]
    dfs = [m["quote_df"] for m in members]
    reminder_n = sum(1 for m in members if m.get("reminder_restatement"))
    lines = [
        f"### `{axis['slug']}` | scope={axis['scope']} | n={len(members)} | "
        f"quote-DF min/med/max={min(dfs)}/{statistics.median(dfs):.0f}/{max(dfs)} | reminder={reminder_n}",
        axis["definition"],
        "",
    ]
    for m in sorted(members, key=lambda m: (m["card"]["name"], m["oracle_id"])):
        flag = "Y" if m.get("reminder_restatement") else "N"
        lines.append(f"- {m['card']['name']} | qDF={m['quote_df']} | reminder={flag} | \"{truncate_quote(m['quote'])}\"")
    lines.append("")
    return lines


def token_group_line(group: dict, other_by_oid: dict) -> str:
    members = sorted(group["members"], key=lambda m: (m["label"], m["oracle_id"]))
    parts = []
    for m in members:
        card = other_by_oid.get(m["oracle_id"])
        name = card["card"]["name"] if card else "?"
        parts.append(f"{m['label']}({name})")
    tokens = "/".join(group["tokens"])
    return f"- [{tokens}] (n={group['size']}): " + ", ".join(parts)


def find_anomalies(batch: dict) -> tuple:
    alchemy = []
    nonnormal = []
    bad_prefix = []
    for axis in batch["axes"]:
        for m in axis["members"]:
            name = m["card"]["name"]
            layout = m["card"]["layout"]
            if name.startswith(ALCHEMY_PREFIX):
                alchemy.append((name, axis["slug"]))
            if layout != "normal":
                nonnormal.append((name, layout, axis["slug"]))
    for row in batch["other_lane"]:
        name = row["card"]["name"]
        layout = row["card"]["layout"]
        if name.startswith(ALCHEMY_PREFIX):
            alchemy.append((name, "other_lane"))
        if layout != "normal":
            nonnormal.append((name, layout, "other_lane"))
        # batch-6 D7: SYNTH occasionally free-labels a card with a "rule:"-prefixed
        # slug that does NOT exist in the active codebook (either a near-miss
        # invented name, or -- 3 batches running now -- the exact string of a
        # KILLED axis despite the RECENTLY KILLED prompt block listing it
        # verbatim). A genuine lane=free label never carries "rule:"; if one
        # shows up in other_lane, the two-lane check silently failed upstream.
        # This can't be fixed by prompt compliance alone (thinking is disabled
        # on the SYNTH call), so it's caught here, deterministically, every batch.
        if row["label"].startswith("rule:"):
            bad_prefix.append((name, row["label"]))
    alchemy = sorted(set(alchemy))
    nonnormal = sorted(set(nonnormal))
    bad_prefix = sorted(set(bad_prefix))
    return alchemy, nonnormal, bad_prefix


def build_digest(batch_num: int) -> Path:
    paths = fc.batch_paths(batch_num)
    batch = json.loads(paths["enriched"].read_text(encoding="utf-8"))
    stats = batch["enrichment_stats"]

    other_by_oid = {row["oracle_id"]: row for row in batch["other_lane"]}
    alchemy, nonnormal, bad_prefix = find_anomalies(batch)

    n_grouped_other = len({m["oracle_id"] for g in batch["token_groups"] for m in g["members"]})

    existing = sorted(
        (a for a in batch["axes"] if a.get("status") == "existing_codebook_axis"),
        key=lambda a: a["slug"],
    )
    new_candidates = sorted(
        (a for a in batch["axes"] if a.get("status") != "existing_codebook_axis"),
        key=lambda a: (-len(a["members"]), a["slug"]),
    )

    lines = [
        f"# Batch {batch_num} Review Digest — codebook v{batch.get('codebook_version', '?')}",
        "",
        f"Generated deterministically from `review/batch-{batch_num}-enriched.json` "
        f"(foundry_enrich.py output). {len(batch['axes'])} axes "
        f"({len(existing)} confirming existing codebook axes, {len(new_candidates)} new candidates), "
        f"{len(batch['other_lane'])} OTHER-lane rows, {len(batch['token_groups'])} token groups "
        f"(2+ shared label tokens). See `docs/SUP-TRIAGE-PROTOCOL.md` for the review convention.",
        "",
        "## Stats block",
        f"- axes: {len(batch['axes'])} ({len(existing)} existing_codebook_axis confirmations, {len(new_candidates)} new_candidate)",
        f"- axis members: {stats['n_axis_members']}",
        f"- other_lane rows: {stats['n_other_lane']} ({n_grouped_other} appear in >=1 token group, "
        f"{stats['n_other_lane'] - n_grouped_other} ungrouped singleton{'s' if stats['n_other_lane'] - n_grouped_other != 1 else ''})",
        f"- corpus cards scanned: {stats['n_corpus_cards_scanned']:,}",
        f"- unique normalized quotes: {stats['n_unique_normalized_quotes']:,}",
        f"- reminder-text bodies (corpus-wide): {stats['n_reminder_texts_found']:,}",
        f"- reminder restatements flagged: {stats['n_reminder_restatements_flagged']} "
        f"({stats['n_reminder_restatements_exact']} exact, {stats['n_reminder_restatements_substring_only']} substring-only)",
        f"- discard audit: {stats['n_discard_audited']} discarded instance(s) audited, "
        f"{stats['n_discard_face_scanning_misses']} face-scanning miss(es) "
        f"(all-non-oracle-text-field discards: {stats['discard_audit_all_non_oracle_text_fields']})",
        f"- token groups: {stats['n_token_groups']} (2+ rows sharing 2+ label tokens)",
        f"- Alchemy-flagged member rows: {len(alchemy)}",
        f"- non-normal-layout member rows: {len(nonnormal)}",
        f"- OTHER-lane rows with an invalid 'rule:' prefix: {len(bad_prefix)}",
        "",
        "## Anomalies",
        "",
        f"### Alchemy rows (name-prefixed \"{ALCHEMY_PREFIX}\") -- {len(alchemy)}",
    ]
    if alchemy:
        for name, where in alchemy:
            lines.append(f"- {name} ({where})")
    else:
        lines.append("(none)")
    lines += ["", f"### Non-normal-layout rows -- {len(nonnormal)}"]
    if nonnormal:
        for name, layout, where in nonnormal:
            lines.append(f"- {name} ({layout}) ({where})")
    else:
        lines.append("(none)")
    lines += ["", f"### OTHER-lane rows with an invalid 'rule:' prefix -- {len(bad_prefix)}",
              "(a genuine lane=free label never starts with \"rule:\" -- this means SYNTH free-labeled "
              "with a slug it believed was a codebook match, but it isn't an active axis. Check first "
              "whether it's a KILLED axis being re-proposed (recently-killed-appendix compliance "
              "failure, batch-6 D7) vs. a near-miss invented slug (naming-discipline failure).)"]
    if bad_prefix:
        for name, label in bad_prefix:
            lines.append(f"- {name}: {label}")
    else:
        lines.append("(none)")

    lines += ["", f"## Axes -- existing codebook confirmations ({len(existing)})", ""]
    for axis in existing:
        lines += axis_block(axis)

    lines += [f"## Axes -- new candidates ({len(new_candidates)})", ""]
    for axis in new_candidates:
        lines += axis_block(axis)

    groups_sorted = sorted(batch["token_groups"], key=lambda g: (-g["size"], g["tokens"]))
    lines += [f"## OTHER-lane token groups ({len(groups_sorted)}, sorted by size desc)", ""]
    for g in groups_sorted:
        lines.append(token_group_line(g, other_by_oid))

    out_path = paths["digest"]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    size = out_path.stat().st_size
    print(f"wrote {out_path} ({size:,} bytes, target ~60KB -- "
          f"{'within target' if size <= 61440 else 'OVER target (completeness prioritized per the never-omit rule)'})")
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", type=int, required=True)
    args = parser.parse_args()
    build_digest(args.batch)


if __name__ == "__main__":
    main()
