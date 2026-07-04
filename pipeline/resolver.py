#!/usr/bin/env python3
"""The card-authoring resolver (plan 3.11) — Captain's two-field handoff.

Input: a plain text file, one card per line, "name | slug". Output: an
enriched manifest — name, slug, oracle_id, R2 image URL(s), Scryfall
fallback URL(s), is_dfc, face_urls — in the same shape as
docs/cutover-manifest.md, built by hand before this tool existed.

Deterministic, no fuzzy matching, ever:
  1. Layouts token/emblem/art_series/vanguard/scheme/planar are excluded
     from the match space entirely before any name lookup happens (Evening
     3 found 216 name collisions with real cards, mostly tokens).
  2. Exact-match against the Oracle bulk name index, case-normalized. A
     double-faced card is indexed both under its full "Front // Back" name
     AND under each individual face name — so Captain can write the plain
     front-face name a human would actually say, without it counting as
     fuzzy matching (both strings come straight from the bulk record).
  3. DFC rule (locked, PHASE-2-COMPLETION.md correction #1): is_dfc is true
     if and only if card_faces[0].image_uris exists — never judged by
     card_faces presence alone.

Halts LOUDLY, per line, on: zero matches, multiple surviving matches, the
slug already naming a root-level .html in the site repo, or a missing R2
image (HEAD check). A bad line does not abort the run — it prints a
plain-English STOP naming the exact problem card and is left out of the
output manifest; every other clean line still resolves. Exit code is
nonzero if any line halted, so a caller (or Captain) knows to look.
"""
import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import requests

DEFAULT_BULK_PATH = Path("data/raw/oracle-cards.jsonl.gz")
DEFAULT_SITE_REPO = Path("~/Projects/mtjawnny.github.io").expanduser()
CDN_BASE = "https://cdn.mtjawnny.com"

# Name-resolution exclusion set — deliberately broader than the image-corpus
# layout filter (which keeps tokens/emblems since they get images too): a
# card-authoring resolver should never resolve a Captain-typed name to a
# token or emblem instead of the real card.
RESOLVER_EXCLUDE_LAYOUTS = {"token", "emblem", "art_series", "vanguard", "scheme", "planar"}

HEAD_TIMEOUT = 15


def normalize(name: str) -> str:
    return name.strip().casefold()


def parse_input_lines(path: Path) -> list:
    if not path.exists():
        print(f"STOP — input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(path, encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 2 or not parts[0] or not parts[1]:
                print(
                    f"STOP — line {line_no}: expected exactly 'name | slug', got {raw_line!r}",
                    file=sys.stderr,
                )
                sys.exit(1)
            rows.append({"line_no": line_no, "name": parts[0], "slug": parts[1]})
    return rows


def load_name_index(bulk_path: Path) -> dict:
    """normalized name -> {oracle_id: card}. Indexes both the full card name
    and, for multi-face cards, each individual face name."""
    if not bulk_path.exists():
        print(f"STOP — {bulk_path} not found — run pipeline/fetch.py first", file=sys.stderr)
        sys.exit(1)

    index = {}
    with gzip.open(bulk_path, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"STOP — {bulk_path} line {line_no}: JSON parse failure: {e}", file=sys.stderr)
                sys.exit(1)

            layout = card.get("layout") or "unknown"
            if layout in RESOLVER_EXCLUDE_LAYOUTS:
                continue
            oracle_id = card.get("oracle_id")
            if not oracle_id:
                continue

            keys = {normalize(card["name"])}
            for face in card.get("card_faces") or []:
                if face.get("name"):
                    keys.add(normalize(face["name"]))

            for key in keys:
                index.setdefault(key, {})[oracle_id] = card
    return index


def is_dfc(card: dict) -> bool:
    faces = card.get("card_faces")
    if not faces:
        return False
    return "image_uris" in faces[0]


def build_image_urls(card: dict) -> dict:
    """Returns {"is_dfc", "image_url", "scryfall_fallback_url", "face_urls"}."""
    oracle_id = card["oracle_id"]
    dfc = is_dfc(card)

    if dfc:
        faces = card["card_faces"]
        front_r2 = f"{CDN_BASE}/cards/png/{oracle_id}-front.png"
        back_r2 = f"{CDN_BASE}/cards/png/{oracle_id}-back.png"
        front_scryfall = faces[0]["image_uris"]["png"]
        back_scryfall = (faces[1].get("image_uris") or {}).get("png") if len(faces) > 1 else None
        return {
            "is_dfc": True,
            "image_url": front_r2,
            "scryfall_fallback_url": front_scryfall,
            "face_urls": {
                "front": {"r2": front_r2, "scryfall": front_scryfall},
                "back": {"r2": back_r2, "scryfall": back_scryfall},
            },
        }

    root_png = (card.get("image_uris") or {}).get("png")
    r2_url = f"{CDN_BASE}/cards/png/{oracle_id}.png"
    return {
        "is_dfc": False,
        "image_url": r2_url,
        "scryfall_fallback_url": root_png,
        "face_urls": None,
    }


def r2_urls_to_check(resolved: dict) -> list:
    if resolved["is_dfc"]:
        return [resolved["face_urls"]["front"]["r2"], resolved["face_urls"]["back"]["r2"]]
    return [resolved["image_url"]]


def head_check(url: str) -> bool:
    try:
        resp = requests.head(url, timeout=HEAD_TIMEOUT, allow_redirects=True)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def slug_taken(slug: str, site_repo: Path) -> bool:
    return (site_repo / f"{slug}.html").exists()


def resolve_row(row: dict, name_index: dict, site_repo: Path) -> tuple:
    """Returns (resolved_dict_or_None, halt_message_or_None)."""
    name, slug, line_no = row["name"], row["slug"], row["line_no"]
    matches = list(name_index.get(normalize(name), {}).values())

    if len(matches) == 0:
        return None, f"line {line_no}: {name!r} matched 0 cards — check spelling, no fuzzy fallback"
    if len(matches) > 1:
        oracle_ids = ", ".join(c["oracle_id"] for c in matches)
        return None, (
            f"line {line_no}: {name!r} matched {len(matches)} cards ({oracle_ids}) — ambiguous, "
            f"disambiguate with a more specific name or wait for a future set/collector-number field"
        )

    card = matches[0]

    if slug_taken(slug, site_repo):
        return None, f"line {line_no}: slug {slug!r} is already a root-level .html in {site_repo}"

    image_fields = build_image_urls(card)
    for url in r2_urls_to_check(image_fields):
        if not head_check(url):
            return None, f"line {line_no}: {name!r} resolved to {card['oracle_id']} but R2 image missing: {url}"

    resolved = {
        "name": name,
        "slug": slug,
        "oracle_id": card["oracle_id"],
        **image_fields,
    }
    return resolved, None


def render_markdown(resolved_rows: list) -> str:
    lines = [
        "| name | slug | oracle_id | image_url | scryfall_fallback_url | is_dfc | face_urls |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in resolved_rows:
        face_urls = json.dumps(r["face_urls"]) if r["face_urls"] else "-"
        lines.append(
            f"| {r['name']} | {r['slug']} | `{r['oracle_id']}` | {r['image_url']} | "
            f"{r['scryfall_fallback_url']} | {'yes' if r['is_dfc'] else 'no'} | {face_urls} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="text file of 'name | slug' lines")
    parser.add_argument("--output", help="path for the resolved markdown manifest (default: stdout)")
    parser.add_argument("--bulk-path", default=str(DEFAULT_BULK_PATH))
    parser.add_argument("--site-repo", default=str(DEFAULT_SITE_REPO))
    args = parser.parse_args()

    rows = parse_input_lines(Path(args.input))
    print(f"loaded {len(rows)} input line(s) from {args.input}")

    name_index = load_name_index(Path(args.bulk_path))
    print(f"name index: {len(name_index):,} distinct keys")

    site_repo = Path(args.site_repo).expanduser()

    resolved_rows = []
    halts = []
    for row in rows:
        resolved, halt_message = resolve_row(row, name_index, site_repo)
        if resolved is not None:
            resolved_rows.append(resolved)
            print(f"  OK — line {row['line_no']}: {row['name']!r} -> {resolved['oracle_id']}")
        else:
            halts.append(halt_message)
            print(f"STOP — {halt_message}", file=sys.stderr)

    manifest_md = render_markdown(resolved_rows)
    if args.output:
        Path(args.output).write_text(manifest_md)
        print(f"\nwrote resolved manifest: {args.output}")
    else:
        print("\n" + manifest_md)

    print(f"\n{len(resolved_rows)} resolved, {len(halts)} halted (of {len(rows)} input line(s))")
    if halts:
        sys.exit(1)


if __name__ == "__main__":
    main()
