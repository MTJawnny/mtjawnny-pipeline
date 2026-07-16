#!/usr/bin/env python3
"""Fetch Scryfall bulk data as JSONL, streamed line-by-line, never loaded whole into memory.

Default mode hits the live Scryfall bulk-data API. --from-snapshot skips the
network fetch and pulls the archived files out of R2 instead (used for
tonight's proof run against the 2026-07-03 backfill snapshot). Both modes
leave the same artifact paths under data/raw/ so downstream code (trim_merge.py)
has one input contract regardless of which mode produced it.

JSONL is mandatory: no code path in this repo may consume Scryfall's legacy
bulk-data format, even temporarily. All bulk data is followed via
jsonl_download_uri only.
"""
import argparse
import gzip
import os
import subprocess
import sys
from pathlib import Path

import requests

USER_AGENT = "MTJawnnyPipeline/1.0 (mtjawnny.com)"
BULK_DATA_URL = "https://api.scryfall.com/bulk-data"
RCLONE_REMOTE = os.environ.get("RCLONE_REMOTE", "r2:")
SNAPSHOT_BUCKET_PREFIX = f"{RCLONE_REMOTE}mtjawnny/data/snapshots"
OUT_DIR = Path("data/raw")

ORACLE_CARDS_FILENAME = "oracle-cards.jsonl.gz"
RULINGS_FILENAME = "rulings.jsonl.gz"


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def api_headers() -> dict:
    return {"User-Agent": USER_AGENT, "Accept": "application/json"}


def fetch_bulk_data_entries() -> list:
    resp = requests.get(BULK_DATA_URL, headers=api_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()["data"]


def pick_entry(entries: list, bulk_type: str) -> dict:
    matches = [e for e in entries if e.get("type") == bulk_type]
    if not matches:
        halt(f"no bulk-data entry of type '{bulk_type}' found in {BULK_DATA_URL} response")
    if len(matches) > 1:
        halt(f"multiple bulk-data entries of type '{bulk_type}' — expected exactly one")
    entry = matches[0]
    if "jsonl_download_uri" not in entry:
        halt(
            f"bulk-data entry '{bulk_type}' has no jsonl_download_uri — "
            f"the JSONL format is mandatory, refusing to fall back to the legacy download_uri"
        )
    return entry


def stream_download(url: str, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    total = 0
    with requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    total += len(chunk)
    tmp.rename(dest)
    return total


def count_gzip_lines(path: Path) -> int:
    count = 0
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count


def report(label: str, path: Path) -> None:
    if not path.exists():
        halt(f"expected artifact missing after fetch: {path}")
    size = path.stat().st_size
    lines = count_gzip_lines(path)
    print(f"{label}: {path} — {size:,} bytes, {lines:,} lines")


def fetch_live() -> None:
    entries = fetch_bulk_data_entries()

    oracle_entry = pick_entry(entries, "oracle_cards")
    oracle_dest = OUT_DIR / ORACLE_CARDS_FILENAME
    stream_download(oracle_entry["jsonl_download_uri"], oracle_dest)

    rulings_entry = pick_entry(entries, "rulings")
    rulings_dest = OUT_DIR / RULINGS_FILENAME
    stream_download(rulings_entry["jsonl_download_uri"], rulings_dest)

    report("oracle-cards", oracle_dest)
    report("rulings", rulings_dest)


def rclone_ls(remote_path: str) -> list:
    result = subprocess.run(
        ["rclone", "lsf", remote_path], capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def rclone_copy(remote_file: str, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["rclone", "copy", remote_file, str(dest_dir)], capture_output=True, text=True
    )
    if result.returncode != 0:
        halt(f"rclone copy failed for {remote_file}: {result.stderr.strip()}")


def fetch_from_snapshot(snapshot_date: str) -> None:
    snapshot_path = f"{SNAPSHOT_BUCKET_PREFIX}/{snapshot_date}"

    oracle_remote = f"{snapshot_path}/{ORACLE_CARDS_FILENAME}"
    rclone_copy(oracle_remote, OUT_DIR)
    oracle_dest = OUT_DIR / ORACLE_CARDS_FILENAME
    if not oracle_dest.exists():
        halt(f"{oracle_remote} did not land at {oracle_dest} after rclone copy")

    snapshot_files = rclone_ls(snapshot_path)
    archived_rulings = next(
        (f for f in snapshot_files if "rulings" in f and f.endswith(".jsonl.gz")), None
    )
    rulings_dest = OUT_DIR / RULINGS_FILENAME
    if archived_rulings:
        rclone_copy(f"{snapshot_path}/{archived_rulings}", OUT_DIR)
        landed = OUT_DIR / archived_rulings
        if landed != rulings_dest:
            landed.rename(rulings_dest)
    else:
        print(
            f"no rulings bulk file archived in {snapshot_path} — "
            f"falling back to live rulings download",
            file=sys.stderr,
        )
        entries = fetch_bulk_data_entries()
        rulings_entry = pick_entry(entries, "rulings")
        stream_download(rulings_entry["jsonl_download_uri"], rulings_dest)

    report("oracle-cards", oracle_dest)
    report("rulings", rulings_dest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-snapshot",
        action="store_true",
        help="pull from the archived R2 snapshot instead of live Scryfall bulk-data",
    )
    parser.add_argument(
        "--snapshot-date",
        default="2026-07-03",
        help="snapshot date folder under data/snapshots/ in R2 (default: 2026-07-03)",
    )
    args = parser.parse_args()

    if args.from_snapshot:
        fetch_from_snapshot(args.snapshot_date)
    else:
        fetch_live()


if __name__ == "__main__":
    main()
