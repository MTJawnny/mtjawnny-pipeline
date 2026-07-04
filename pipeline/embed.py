#!/usr/bin/env python3
"""Generate/cache bge-small-en-v1.5 embeddings per recipes/embedding.yaml (Evening 2, plan 3.4).

Incremental by design: on startup, pulls the existing embeddings.parquet cache
from R2 (absent on first run only — not an error), then re-embeds only cards
whose oracle_id is new or whose composed input text hash changed. Everything
else is carried forward from the cache untouched.

For multi-face cards (split/transform/adventure/modal_dfc/flip), Scryfall
leaves the root oracle_text/type_line null and stores real text per face in
card_faces (see trim_merge.py). The oracle_text/type_line slots for those
cards are the face values joined with " // " in face order.
"""
import gzip
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sentence_transformers import SentenceTransformer

RECIPE_PATH = Path("recipes/embedding.yaml")
TRIMMED_PATH = Path("data/trimmed/cards.jsonl.gz")
CACHE_LOCAL = Path("data/cache/embeddings.parquet")
CACHE_REMOTE_FILE = "r2:mtjawnny/data/cache/embeddings.parquet"
CACHE_REMOTE_DIR = "r2:mtjawnny/data/cache/"

EXPECTED_MODEL = "BAAI/bge-small-en-v1.5"
EXPECTED_DIM = 384
EXPECTED_RECIPE = "name. type_line. oracle_text (keywords)"
EXPECTED_SELF_TOKEN = "~"

ENCODE_BATCH_SIZE = 64
PROGRESS_CHUNK = 2000


def halt(message: str) -> None:
    print(f"STOP — {message}", file=sys.stderr)
    sys.exit(1)


def load_recipe() -> dict:
    if not RECIPE_PATH.exists():
        halt(f"{RECIPE_PATH} not found")
    with open(RECIPE_PATH) as f:
        recipe = yaml.safe_load(f) or {}

    for key in ("model", "input_recipe", "self_name_token"):
        if key not in recipe:
            halt(f"{RECIPE_PATH} missing required key {key!r}")

    if recipe["model"] != EXPECTED_MODEL:
        halt(
            f"{RECIPE_PATH} model={recipe['model']!r} does not match the model "
            f"embed.py is written for ({EXPECTED_MODEL!r}) — switching models "
            f"invalidates the cache and must be a deliberate, versioned change "
            f"to both the recipe and this script together"
        )
    if recipe["input_recipe"] != EXPECTED_RECIPE:
        halt(
            f"{RECIPE_PATH} input_recipe={recipe['input_recipe']!r} does not match "
            f"what compose_text() implements ({EXPECTED_RECIPE!r})"
        )
    if recipe["self_name_token"] != EXPECTED_SELF_TOKEN:
        halt(
            f"{RECIPE_PATH} self_name_token={recipe['self_name_token']!r} does not "
            f"match embed.py's hardcoded token ({EXPECTED_SELF_TOKEN!r})"
        )
    return recipe


def load_cards() -> list:
    if not TRIMMED_PATH.exists():
        halt(f"{TRIMMED_PATH} not found — run pipeline/trim_merge.py first")
    cards = []
    with gzip.open(TRIMMED_PATH, "rt", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as e:
                halt(f"{TRIMMED_PATH} line {line_no}: JSON parse failure: {e}")
            if "oracle_id" not in card or not card["oracle_id"]:
                halt(f"{TRIMMED_PATH} line {line_no}: missing oracle_id")
            cards.append(card)
    return cards


def _face_text(card: dict) -> tuple:
    """Return (type_line, oracle_text) accounting for multi-face cards."""
    faces = card.get("card_faces")
    type_line = card.get("type_line")
    oracle_text = card.get("oracle_text")

    if faces:
        if not type_line:
            type_line = " // ".join(face.get("type_line") or "" for face in faces)
        if not oracle_text:
            oracle_text = " // ".join(face.get("oracle_text") or "" for face in faces)

    return type_line or "", oracle_text or ""


def normalize_self_references(oracle_text: str, name: str, self_token: str) -> str:
    if not oracle_text:
        return ""
    candidates = {name}
    if " // " in name:
        for face_name in name.split(" // "):
            face_name = face_name.strip()
            if face_name:
                candidates.add(face_name)

    for candidate in sorted(candidates, key=len, reverse=True):
        pattern = r"\b" + re.escape(candidate) + r"\b"
        oracle_text = re.sub(pattern, self_token, oracle_text)
    return oracle_text


def compose_text(card: dict, self_token: str) -> str:
    name = card["name"]
    type_line, oracle_text = _face_text(card)
    keywords = card.get("keywords") or []

    normalized_oracle_text = normalize_self_references(oracle_text, name, self_token)
    keyword_str = ", ".join(keywords)
    return f"{name}. {type_line}. {normalized_oracle_text} ({keyword_str})"


def download_cache() -> None:
    CACHE_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["rclone", "copy", CACHE_REMOTE_FILE, str(CACHE_LOCAL.parent)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and CACHE_LOCAL.exists():
        print(f"downloaded existing cache from R2: {CACHE_REMOTE_FILE}")
    else:
        print("no cache found in R2 (first run) — starting from an empty cache")


def load_cache_map() -> dict:
    if not CACHE_LOCAL.exists():
        return {}
    df = pd.read_parquet(CACHE_LOCAL)
    cache_map = {}
    for row in df.itertuples(index=False):
        cache_map[row.oracle_id] = (row.text_sha256, np.asarray(row.vector, dtype=np.float32))
    return cache_map


def upload_cache() -> None:
    result = subprocess.run(
        [
            "rclone", "copy", str(CACHE_LOCAL), CACHE_REMOTE_DIR,
            "-M", "--metadata-set", "cache-control=public, max-age=300",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        halt(f"rclone upload of {CACHE_LOCAL} to {CACHE_REMOTE_DIR} failed: {result.stderr.strip()}")
    print(f"uploaded {CACHE_LOCAL} to {CACHE_REMOTE_DIR}")


def main() -> None:
    t0 = time.time()

    recipe = load_recipe()
    cards = load_cards()
    print(f"loaded {len(cards):,} trimmed cards")

    download_cache()
    cache_map = load_cache_map()
    print(f"cache entries loaded: {len(cache_map):,}")

    self_token = recipe["self_name_token"]
    texts = [compose_text(c, self_token) for c in cards]
    shas = [hashlib.sha256(t.encode("utf-8")).hexdigest() for t in texts]

    final_vectors = [None] * len(cards)
    to_embed_indices = []
    to_embed_texts = []
    reused = 0
    for i, c in enumerate(cards):
        cached = cache_map.get(c["oracle_id"])
        if cached is not None and cached[0] == shas[i]:
            final_vectors[i] = cached[1]
            reused += 1
        else:
            to_embed_indices.append(i)
            to_embed_texts.append(texts[i])

    embed_count = len(to_embed_texts)
    print(f"reused from cache: {reused:,}  |  to embed: {embed_count:,}")

    if embed_count:
        model = SentenceTransformer(recipe["model"])
        dim = model.get_embedding_dimension()
        if dim != EXPECTED_DIM:
            halt(
                f"model {recipe['model']!r} produced dim={dim}, expected "
                f"{EXPECTED_DIM} — the cache/parquet contract assumes {EXPECTED_DIM}-dim vectors"
            )

        done = 0
        for start in range(0, embed_count, PROGRESS_CHUNK):
            chunk_texts = to_embed_texts[start:start + PROGRESS_CHUNK]
            chunk_vecs = model.encode(
                chunk_texts,
                batch_size=ENCODE_BATCH_SIZE,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            for j, vec in enumerate(chunk_vecs):
                final_vectors[to_embed_indices[start + j]] = np.asarray(vec, dtype=np.float32)
            done += len(chunk_texts)
            print(f"  embedded {done:,}/{embed_count:,}")
    else:
        print("cache fully up to date — nothing to embed")

    if any(v is None for v in final_vectors):
        halt("internal error: some card ended up with no vector assigned")

    vectors_arr = np.stack(final_vectors).astype(np.float32)
    if vectors_arr.shape[0] != len(cards):
        halt(f"vector count {vectors_arr.shape[0]:,} != input card count {len(cards):,}")
    if vectors_arr.shape[1] != EXPECTED_DIM:
        halt(f"vector dim {vectors_arr.shape[1]} != expected {EXPECTED_DIM}")
    if np.isnan(vectors_arr).any():
        halt("NaNs found in computed embedding vectors")

    df = pd.DataFrame({
        "oracle_id": [c["oracle_id"] for c in cards],
        "text_sha256": shas,
        "vector": list(vectors_arr),
    })

    CACHE_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE_LOCAL, engine="pyarrow", index=False)

    try:
        df_check = pd.read_parquet(CACHE_LOCAL)
    except Exception as e:
        halt(f"wrote {CACHE_LOCAL} but it failed to read back: {e}")
    if len(df_check) != len(df):
        halt(f"{CACHE_LOCAL} round-trip row count {len(df_check):,} != written {len(df):,}")
    sample_vec = np.asarray(df_check.iloc[0]["vector"], dtype=np.float32)
    if sample_vec.shape[0] != EXPECTED_DIM:
        halt(f"{CACHE_LOCAL} round-trip vector dim {sample_vec.shape[0]} != {EXPECTED_DIM}")

    upload_cache()

    elapsed = time.time() - t0
    print(
        f"done in {elapsed:.1f}s — {len(cards):,} total vectors "
        f"({embed_count:,} newly embedded, {reused:,} reused from cache)"
    )


if __name__ == "__main__":
    main()
