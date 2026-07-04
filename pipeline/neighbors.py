#!/usr/bin/env python3
"""Compute top-25 cosine neighbors per card from cached embeddings (plan 3.5).

Brute-force cosine over all 38K cards, but never materializes the full
N x N similarity matrix (~5.8GB at float32) — the matmul runs in row chunks
of ~2K against the full vector set instead.

Local artifact only tonight — not uploaded to R2. It gets packaged into the
versioned artifact set in Evenings 3-4.
"""
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_LOCAL = Path("data/cache/embeddings.parquet")
TRIMMED_PATH = Path("data/trimmed/cards.jsonl.gz")
OUT_PATH = Path("data/neighbors/neighbors.parquet")

TOP_K = 25
CHUNK = 2000
ANCHOR_NAMES = ["Counterspell", "Sol Ring", "Rampant Growth"]


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def load_embeddings() -> tuple:
    if not CACHE_LOCAL.exists():
        halt(f"{CACHE_LOCAL} not found — run pipeline/embed.py first")
    df = pd.read_parquet(CACHE_LOCAL)
    oracle_ids = df["oracle_id"].to_numpy()
    vectors = np.stack(df["vector"].to_numpy()).astype(np.float32)
    return oracle_ids, vectors


def verify_normalized(vectors: np.ndarray) -> None:
    norms = np.linalg.norm(vectors, axis=1)
    bad = np.sum(np.abs(norms - 1.0) > 1e-3)
    if bad:
        halt(
            f"{bad:,} of {len(norms):,} vectors in {CACHE_LOCAL} are not "
            f"L2-normalized (embed.py encodes with normalize_embeddings=True, "
            f"so they should already be unit vectors) — refusing to silently "
            f"re-normalize a cache that should already be correct"
        )


def compute_neighbors(oracle_ids: np.ndarray, vectors: np.ndarray) -> pd.DataFrame:
    n = len(oracle_ids)
    out_oracle_id, out_rank, out_neighbor_id, out_score = [], [], [], []

    for start in range(0, n, CHUNK):
        end = min(start + CHUNK, n)
        sims = vectors[start:end] @ vectors.T  # (chunk, n)
        for local_i in range(end - start):
            global_i = start + local_i
            row = sims[local_i]
            row[global_i] = -np.inf  # exclude self
            top_idx = np.argpartition(row, -TOP_K)[-TOP_K:]
            top_idx = top_idx[np.argsort(row[top_idx])[::-1]]
            out_oracle_id.extend([oracle_ids[global_i]] * TOP_K)
            out_rank.extend(range(1, TOP_K + 1))
            out_neighbor_id.extend(oracle_ids[top_idx])
            out_score.extend(row[top_idx].astype(float))
        print(f"  neighbors computed for {end:,}/{n:,} cards")

    return pd.DataFrame({
        "oracle_id": out_oracle_id,
        "rank": out_rank,
        "neighbor_id": out_neighbor_id,
        "score": out_score,
    })


def load_name_lookup() -> dict:
    if not TRIMMED_PATH.exists():
        halt(f"{TRIMMED_PATH} not found — run pipeline/trim_merge.py first")
    lookup = {}
    with gzip.open(TRIMMED_PATH, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            card = json.loads(line)
            lookup[card["oracle_id"]] = card["name"]
    return lookup


def anchor_check(df: pd.DataFrame, name_by_oracle_id: dict) -> None:
    name_to_oracle_ids = {}
    for oid, name in name_by_oracle_id.items():
        name_to_oracle_ids.setdefault(name, []).append(oid)

    for anchor_name in ANCHOR_NAMES:
        matches = name_to_oracle_ids.get(anchor_name, [])
        if len(matches) == 0:
            halt(f"anchor check: {anchor_name!r} matched 0 cards in {TRIMMED_PATH}")
        if len(matches) > 1:
            halt(f"anchor check: {anchor_name!r} matched {len(matches)} cards — ambiguous")

        oid = matches[0]
        sub = df[df["oracle_id"] == oid].sort_values("rank").head(10)
        print(f"\ntop-10 neighbors of {anchor_name!r}:")
        for _, r in sub.iterrows():
            nname = name_by_oracle_id.get(r["neighbor_id"], "?")
            print(f"  {int(r['rank']):>2}. {nname:<40} score={r['score']:.4f}")


def main() -> None:
    t0 = time.time()

    oracle_ids, vectors = load_embeddings()
    print(f"loaded {len(oracle_ids):,} vectors, dim={vectors.shape[1]}")
    verify_normalized(vectors)

    df = compute_neighbors(oracle_ids, vectors)

    expected_rows = TOP_K * len(oracle_ids)
    if len(df) != expected_rows:
        halt(f"neighbor row count {len(df):,} != expected {expected_rows:,} ({TOP_K} * card count)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, engine="pyarrow", index=False)
    print(f"wrote {OUT_PATH} — {len(df):,} rows")

    name_by_oracle_id = load_name_lookup()
    anchor_check(df, name_by_oracle_id)

    elapsed = time.time() - t0
    print(f"\ndone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
