#!/usr/bin/env python3
"""Gate the build: card-count sanity, known-card spot checks, neighbor sanity,
artifact sizes, FTS smoke test (plan 3.9).

Halt-loudly house style: ANY failure exits nonzero with a plain-English
reason, and leaves /data/latest.json untouched (upload.py never runs).

On success, writes data/artifacts/.validated.json — a sha256 fingerprint of
every gated artifact plus a timestamp. upload.py recomputes the same hashes
and refuses to upload unless they match, so a stale marker from a previous
run (or artifacts rebuilt after validate ran) can't slip past the gate.
"""
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

RCLONE_REMOTE = os.environ.get("RCLONE_REMOTE", "r2:")
LATEST_JSON_REMOTE = f"{RCLONE_REMOTE}mtjawnny/data/latest.json"

SQLITE_PATH = Path("data/artifacts/cards.sqlite")
VECTORS_PATH = Path("data/artifacts/finisher/vectors.bin")
INDEX_PATH = Path("data/artifacts/finisher/index.json.gz")
EXPECTED_PATH = Path("tests/expected.json")
MARKER_PATH = Path("data/artifacts/.validated.json")

# (min_bytes, max_bytes) per plan 3.9
SIZE_BOUNDS = {
    SQLITE_PATH: (150 * 1024 * 1024, 260 * 1024 * 1024),
    VECTORS_PATH: (9 * 1024 * 1024, 14 * 1024 * 1024),
    INDEX_PATH: (int(0.8 * 1024 * 1024), 4 * 1024 * 1024),
}

CARD_COUNT_DELTA_TOLERANCE = 0.10
ANCHOR_NAME = "Counterspell"
ANCHOR_TOP_K = 5
ANCHOR_MIN_SCORE = 0.85
ANCHOR_SHARED_WORD = "counter"
FTS_QUERY = "landfall"
FTS_MIN_RESULTS = 10


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def ok(message: str) -> None:
    print(f"  OK — {message}")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_artifacts_exist() -> None:
    for path in (SQLITE_PATH, VECTORS_PATH, INDEX_PATH):
        if not path.exists():
            halt(f"required artifact missing: {path} — run the earlier pipeline stages first")


def fetch_previous_latest_json() -> dict | None:
    result = subprocess.run(
        ["rclone", "cat", LATEST_JSON_REMOTE], capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        halt(f"{LATEST_JSON_REMOTE} exists but is not valid JSON: {e}")


def check_card_count_delta(conn: sqlite3.Connection) -> int:
    print("card count delta check:")
    current_count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]

    previous = fetch_previous_latest_json()
    if previous is None:
        print(f"  FIRST RUN — no previous {LATEST_JSON_REMOTE} found, skipping delta check")
        ok(f"current card count: {current_count:,}")
        return current_count

    previous_count = (previous.get("counts") or {}).get("cards")
    if previous_count is None:
        halt(f"{LATEST_JSON_REMOTE} exists but has no counts.cards field — can't compute delta")

    lo = previous_count * (1 - CARD_COUNT_DELTA_TOLERANCE)
    hi = previous_count * (1 + CARD_COUNT_DELTA_TOLERANCE)
    if not (lo <= current_count <= hi):
        halt(
            f"card count {current_count:,} is outside ±{int(CARD_COUNT_DELTA_TOLERANCE * 100)}% "
            f"of the previous version's {previous_count:,} (expected {lo:,.0f}-{hi:,.0f}) — "
            f"this looks like a bad Scryfall fetch or a broken trim step, not a normal week's churn"
        )
    ok(f"current {current_count:,} vs previous {previous_count:,} (within ±{int(CARD_COUNT_DELTA_TOLERANCE * 100)}%)")
    return current_count


def check_known_card_panel(conn: sqlite3.Connection) -> None:
    print("known-card panel check:")
    if not EXPECTED_PATH.exists():
        halt(f"{EXPECTED_PATH} not found — can't run the known-card panel")
    with open(EXPECTED_PATH) as f:
        expected = json.load(f)
    expected = {k: v for k, v in expected.items() if not k.startswith("_")}

    for name, expected_text in expected.items():
        row = conn.execute(
            "SELECT oracle_text FROM cards WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            halt(f"known-card panel: {name!r} not found in cards.sqlite at all")
        actual_text = row[0]
        if actual_text != expected_text:
            halt(
                f"known-card panel: {name!r} oracle_text mismatch\n"
                f"  expected: {expected_text!r}\n"
                f"  actual:   {actual_text!r}"
            )
        ok(f"{name!r} oracle_text matches")


def check_neighbor_sanity(conn: sqlite3.Connection) -> None:
    print("neighbor sanity check:")
    anchor_row = conn.execute(
        "SELECT oracle_id FROM cards WHERE name = ?", (ANCHOR_NAME,)
    ).fetchall()
    if len(anchor_row) == 0:
        halt(f"neighbor sanity: anchor card {ANCHOR_NAME!r} not found in cards.sqlite")
    if len(anchor_row) > 1:
        halt(f"neighbor sanity: anchor card {ANCHOR_NAME!r} matched {len(anchor_row)} rows — ambiguous")
    anchor_oracle_id = anchor_row[0][0]

    neighbors = conn.execute(
        """
        SELECT c.name, c.oracle_text, n.score
        FROM neighbors n JOIN cards c ON c.oracle_id = n.neighbor_id
        WHERE n.oracle_id = ?
        ORDER BY n.rank
        LIMIT ?
        """,
        (anchor_oracle_id, ANCHOR_TOP_K),
    ).fetchall()

    if len(neighbors) < ANCHOR_TOP_K:
        halt(f"neighbor sanity: {ANCHOR_NAME!r} has only {len(neighbors)} neighbor rows, expected {ANCHOR_TOP_K}")

    word_pattern = re.compile(r"\b" + re.escape(ANCHOR_SHARED_WORD) + r"\b", re.IGNORECASE)
    for name, oracle_text, score in neighbors:
        if score <= ANCHOR_MIN_SCORE:
            halt(
                f"neighbor sanity: {ANCHOR_NAME!r} neighbor {name!r} scores {score:.4f}, "
                f"expected > {ANCHOR_MIN_SCORE}"
            )
        if not word_pattern.search(oracle_text or ""):
            halt(
                f"neighbor sanity: {ANCHOR_NAME!r} neighbor {name!r} shares zero words with "
                f"{ANCHOR_SHARED_WORD!r} (oracle_text: {oracle_text!r}) — embeddings may be broken"
            )
    ok(f"{ANCHOR_NAME!r} top-{ANCHOR_TOP_K} all score > {ANCHOR_MIN_SCORE} and mention {ANCHOR_SHARED_WORD!r}")


def check_artifact_sizes() -> None:
    print("artifact size bounds check:")
    for path, (lo, hi) in SIZE_BOUNDS.items():
        size = path.stat().st_size
        if not (lo <= size <= hi):
            halt(
                f"{path} is {size:,} bytes ({size / 1024 / 1024:.2f} MB), outside expected "
                f"bounds {lo:,}-{hi:,} bytes ({lo / 1024 / 1024:.1f}-{hi / 1024 / 1024:.1f} MB)"
            )
        ok(f"{path}: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")


def check_fts_smoke_test(conn: sqlite3.Connection) -> None:
    print("FTS smoke test:")
    count = conn.execute(
        "SELECT COUNT(*) FROM cards_fts WHERE cards_fts MATCH ?", (FTS_QUERY,)
    ).fetchone()[0]
    if count <= FTS_MIN_RESULTS:
        halt(f"FTS query {FTS_QUERY!r} returned {count} results, expected > {FTS_MIN_RESULTS}")
    ok(f"FTS query {FTS_QUERY!r} returned {count} results")


def write_marker(current_count: int) -> None:
    fingerprint = {
        "validated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "card_count": current_count,
        "artifact_hashes": {
            str(path): sha256_of(path)
            for path in (SQLITE_PATH, VECTORS_PATH, INDEX_PATH)
        },
    }
    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MARKER_PATH, "w") as f:
        json.dump(fingerprint, f, indent=2)
    print(f"wrote {MARKER_PATH}")


def main() -> None:
    require_artifacts_exist()

    conn = sqlite3.connect(SQLITE_PATH)
    try:
        current_count = check_card_count_delta(conn)
        check_known_card_panel(conn)
        check_neighbor_sanity(conn)
        check_artifact_sizes()
        check_fts_smoke_test(conn)
    finally:
        conn.close()

    write_marker(current_count)
    print("\nVALIDATE PASSED — all gates clear, upload.py may proceed")


if __name__ == "__main__":
    main()
