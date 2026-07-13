#!/usr/bin/env python3
"""On-demand dev server for the Tier Engine Viewer -- stdlib only.

Sibling script to emit_viewer.py, same "no second scoring implementation"
discipline: this imports emit_viewer as a library and calls its unmodified
load_export_context()/export_anchor()/resolve_anchor_sqlite() -- the exact
same functions the batch exporter uses -- so an on-demand lookup can never
drift from a batch export of the same card.

Routes:
  GET /                  -> experiments/viewer.html (tracked source; this
                            script serves it as the root page even though
                            it no longer lives under experiments/out/).
  GET /data/<file>       -> experiments/out/viewer/data/<file> (the same
                            directory emit_viewer.py writes to -- pre-baked
                            anchors.txt exports AND anything this server
                            computes on demand land in the same place).
  GET /api/search?q=...  -> up to 25 {name, oracle_id} matches from
                            cards.sqlite, substring/case-insensitive, for
                            an autocomplete box. A results LIST for a human
                            to pick from is not the resolver's exact-match
                            guarantee (CLAUDE.md) -- that guarantee applies
                            to /api/anchor below, which never guesses.
  GET /api/anchor?name=. -> exact-match resolve (0 or >1 sqlite matches is
                            a 404 with the candidate count, never a guess),
                            then serve the cached experiments/out/viewer/
                            data/<slug>.json if present, else compute it
                            via emit_viewer.export_anchor() -- which writes
                            the SAME JSON shape a batch export would -- and
                            refresh index.json from every cached file.

Context (corpus + indexes) is loaded ONCE at startup, exactly like
emit_viewer.py's own main() -- a cold anchor lookup is a few hundred ms to
~1s (see emit_viewer.py's own per-anchor timings), not a full corpus
reload.

Per-face lookup (2026-07-13): `name=` also resolves an INDIVIDUAL face
name of a multi-faced card (e.g. "Delver of Secrets" alone, not just the
combined "Delver of Secrets // Insectile Aberration"), scoping the whole
lookup to just that face's own text -- see emit_viewer.py's own "Per-face
lookup" section for the full design. `mode=weighboth` forces today's
existing whole-card behavior for a name that would otherwise resolve to a
face; `mode=face&face=N` forces face N (0-based) for a name that would
otherwise resolve to the whole card -- both used by the viewer's flip/
weigh-both buttons, which always know the combined name already (from a
prior response's `face_context`) rather than needing to guess face-name
spelling. Resolution ALWAYS tries the existing combined-name sqlite path
first, unchanged -- the face_name_index fallback below only ever fires
for a name that path found NOTHING for, so no existing single-faced or
combined-name lookup can change behavior.
"""
import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import emit_viewer as ev  # noqa: E402
import tier_engine as te  # noqa: E402

VIEWER_HTML = Path("experiments/viewer.html")
VIEWER_DATA_DIR = Path("experiments/out/viewer/data")
DEFAULT_PORT = 8765
SEARCH_LIMIT = 25

ctx = None  # set in main(), read by the request handler
face_ctx = None  # set in main() (2026-07-13, per-face lookup), read by the request handler


def build_index_from_cache(out_dir: Path) -> None:
    """Regenerates index.json by scanning every cached <slug>.json in
    out_dir -- keeps the index consistent whether an anchor got there via
    emit_viewer.py's batch export or this server's on-demand computation,
    without tracking export order separately."""
    entries = []
    for path in sorted(out_dir.glob("*.json")):
        if path.name == "index.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        entries.append({
            "name": data["anchor"]["name"],
            "slug": path.stem,
            "file": path.name,
            "tier_counts": {t: data["tiers"][t]["count"] for t in data["tiers"]},
            "runtime_seconds": data["runtime_seconds"],
        })
    index_path = out_dir / "index.json"
    index_path.write_text(
        json.dumps({"generated_at": ev.dt.datetime.now(ev.dt.timezone.utc).isoformat(timespec="seconds"),
                    "anchors": entries}, indent=2),
        encoding="utf-8",
    )


def search_cards(query: str) -> list:
    rows = ctx.conn.execute(
        "SELECT name, oracle_id FROM cards WHERE name LIKE ? COLLATE NOCASE ORDER BY name LIMIT ?",
        (f"%{query}%", SEARCH_LIMIT),
    ).fetchall()
    return [{"name": name, "oracle_id": oracle_id} for name, oracle_id in rows]


def resolve_combined_name(name: str):
    """Returns (oracle_id, None) on a unique cards.sqlite match, or
    (None, error_dict) -- same exact-match discipline as the pre-existing
    single-path resolver this replaces the first half of."""
    rows = ctx.conn.execute("SELECT oracle_id FROM cards WHERE name = ? COLLATE NOCASE", (name,)).fetchall()
    if len(rows) == 0:
        return None, {"error": f"{name!r}: no match in cards.sqlite"}
    if len(rows) > 1:
        return None, {"error": f"{name!r}: ambiguous, {len(rows)} matches"}
    oracle_id = rows[0][0]
    if oracle_id not in ctx.card_docs:
        return None, {"error": f"{name!r}: resolved in cards.sqlite but absent from the jsonl corpus"}
    return oracle_id, None


def _face_split(oracle_id: str) -> bool:
    """True iff this card was actually split into per-face pseudo-docs in
    face_ctx (i.e. its layout is in ev.FACE_SPLIT_LAYOUTS) -- NOT just "has
    more than one face." Bug found in review (Fable 5, N2): a first draft
    checked only `n_faces > 1`, which is also true for card_faces-bearing
    layouts that were NEVER split (art_series, double_faced_token -- see
    ev.FACE_SPLIT_LAYOUTS's own comment) -- requesting mode=face for one of
    those (e.g. a double_faced_token) looked up a face key that was never
    built, raising an uncaught KeyError deep in export_face_anchor() with
    no HTTP response at all (confirmed live: connection dropped, not even
    a clean 500). Checking membership in face_ctx.face_meta directly (the
    actual data, not a re-derived proxy for it) can't drift out of sync
    with what build_face_scoped_context() really built."""
    return f"{oracle_id}::0" in face_ctx.face_card_docs


def resolve_query(name: str, mode: str, face_param: str):
    """Per-face lookup (2026-07-13). Returns (kind, oracle_id, face_index,
    error) where kind is "combined" or "face"; error is a dict on failure
    (kind/oracle_id/face_index are then meaningless). Resolution order:
    1. Try the existing combined-name path FIRST, unchanged -- an
       ordinary single-faced card, or a multi-faced card looked up by its
       own full slash-name, always wins here and is completely unaffected
       by anything below.
    2. Only if that finds NOTHING does a bare individual face name (e.g.
       "Delver of Secrets" alone) get tried against face_ctx.face_name_
       index -- 0 or 2+ matches (a rare cross-card face-name collision)
       is a 404 with the count, never a guess, same halt-loudly
       convention as every other resolver in this file.

    Three bugs fixed here in review (Fable 5, Findings D/N2/N3), all the
    same underlying mistake -- an explicit mode/face request that doesn't
    apply was silently ignored/downgraded instead of erroring, the one
    convention this whole file otherwise never breaks:
    - mode=face on a card that isn't actually face-split (single-faced, OR
      multi-faced but outside FACE_SPLIT_LAYOUTS) now 404s instead of
      silently falling back to "combined" with no indication the request
      was ignored (Finding D, and N2's crash is really the same mistake
      one level worse -- see _face_split() above).
    - mode=face&face=N reaching this function via the face_name_index
      fallback (i.e. a bare face name was typed) now VERIFIES N against
      what that name actually resolves to, instead of silently discarding
      N and using the name's own resolution unconditionally (N3 -- was
      live: "?name=Insectile+Aberration&mode=face&face=0" returned face 1,
      the name's own index, with the face=0 request simply dropped)."""
    combined_oracle_id, err = resolve_combined_name(name)
    if combined_oracle_id is not None:
        doc = ctx.card_docs[combined_oracle_id]
        n_faces = len(doc["faces"])
        face_split = n_faces > 1 and _face_split(combined_oracle_id)
        if mode == "face":
            if not face_split:
                return None, None, None, {
                    "error": f"{name!r}: mode=face requested but this card has no separately-indexed faces "
                             f"({n_faces} face(s), layout not in FACE_SPLIT_LAYOUTS)"
                }
            try:
                face_index = int(face_param) if face_param is not None else 0
            except ValueError:
                return None, None, None, {"error": f"invalid face param {face_param!r}: must be an integer"}
            if not (0 <= face_index < n_faces):
                return None, None, None, {"error": f"face {face_index} out of range for {name!r} ({n_faces} faces)"}
            return "face", combined_oracle_id, face_index, None
        return "combined", combined_oracle_id, None, None

    matches = face_ctx.face_name_index.get(te.normalize_name(name), [])
    if len(matches) == 0:
        return None, None, None, {"error": f"{name!r}: no match in cards.sqlite or as an individual DFC face name"}
    if len(matches) > 1:
        combined_names = sorted({ctx.card_docs[oid]["name"] for oid, _ in matches})
        return None, None, None, {
            "error": f"{name!r}: ambiguous face name, matches {len(matches)} different cards: {combined_names}"
        }
    face_oracle_id, resolved_face_index = matches[0]
    if mode == "weighboth":
        return "combined", face_oracle_id, None, None
    if face_param is not None:
        try:
            requested_face_index = int(face_param)
        except ValueError:
            return None, None, None, {"error": f"invalid face param {face_param!r}: must be an integer"}
        if requested_face_index != resolved_face_index:
            return None, None, None, {
                "error": f"{name!r} resolves to face {resolved_face_index}, which conflicts with the "
                         f"explicitly requested face={requested_face_index} -- query by the combined "
                         f"name instead to pick a face explicitly"
            }
    return "face", face_oracle_id, resolved_face_index, None


def _cached_bytes_if_fresh(cache_path: Path, expected_corpus_cards: int) -> bytes:
    """Returns the cached JSON bytes if the file exists AND its own
    `corpus_cards` matches the LIVE context's, else None. Bug found in
    review (Fable 5, N4): a face-mode cache entry has no invalidation of
    its own -- emit_viewer.py's batch export wipes experiments/out/viewer/
    data/ wholesale, but an on-demand entry written by THIS server just
    sits there indefinitely. Confirmed live during this session: fixing
    the `prepare`-layout gap changed face_ctx's own corpus size (1,647->
    1,747 faces), but pre-existing on-demand cache files from before that
    fix kept being served unchanged, silently missing every `prepare`-face
    candidate a fresh computation would now find. `corpus_cards` is
    already recorded in every export's own JSON for exactly this kind of
    check -- comparing it against the live context's real size before
    trusting a cache hit is cheap and catches ANY future context change,
    not just this one instance."""
    if not cache_path.exists():
        return None
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    if data.get("corpus_cards") != expected_corpus_cards:
        return None
    return cache_path.read_bytes()


def get_or_compute_anchor(name: str, mode: str, face_param: str) -> tuple:
    """Returns (status_code, json_bytes). See resolve_query()'s docstring
    for the combined-vs-face resolution order; this just dispatches to the
    right cache path + export function for whichever kind won."""
    kind, oracle_id, face_index, err = resolve_query(name, mode, face_param)
    if err is not None:
        return 404, json.dumps(err).encode()

    VIEWER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if kind == "combined":
        combined_name = ctx.card_docs[oracle_id]["name"]
        slug = te.filename_slug(combined_name)
        cache_path = VIEWER_DATA_DIR / f"{slug}.json"
        cached = _cached_bytes_if_fresh(cache_path, ctx.n_total_cards)
        if cached is not None:
            return 200, cached
        ev.export_anchor(combined_name, oracle_id, ctx, VIEWER_DATA_DIR)
        build_index_from_cache(VIEWER_DATA_DIR)
        return 200, cache_path.read_bytes()

    combined_name = ctx.card_docs[oracle_id]["name"]
    slug = f"{te.filename_slug(combined_name)}--face{face_index}"
    cache_path = VIEWER_DATA_DIR / f"{slug}.json"
    cached = _cached_bytes_if_fresh(cache_path, len(face_ctx.face_card_docs))
    if cached is not None:
        return 200, cached
    ev.export_face_anchor(combined_name, oracle_id, face_index, ctx, face_ctx, VIEWER_DATA_DIR)
    build_index_from_cache(VIEWER_DATA_DIR)
    return 200, cache_path.read_bytes()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, obj) -> None:
        self._send(status, json.dumps(obj).encode(), "application/json")

    def do_GET(self):
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self._send(200, VIEWER_HTML.read_bytes(), "text/html; charset=utf-8")
            return

        if path.startswith("/data/"):
            rel = path[len("/data/"):]
            candidate = (VIEWER_DATA_DIR / rel).resolve()
            if VIEWER_DATA_DIR.resolve() not in candidate.parents or not candidate.is_file():
                self._send_json(404, {"error": f"no such data file: {rel}"})
                return
            self._send(200, candidate.read_bytes(), "application/json")
            return

        if path == "/api/search":
            q = (query.get("q") or [""])[0].strip()
            if not q:
                self._send_json(400, {"error": "missing q param"})
                return
            self._send_json(200, {"results": search_cards(q)})
            return

        if path == "/api/anchor":
            name = (query.get("name") or [""])[0].strip()
            if not name:
                self._send_json(400, {"error": "missing name param"})
                return
            mode = (query.get("mode") or [""])[0].strip()
            face_param = (query.get("face") or [None])[0]
            status, body = get_or_compute_anchor(name, mode, face_param)
            self._send(status, body, "application/json")
            return

        self._send_json(404, {"error": f"no such route: {path}"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--cards-path", default=str(te.CARDS_PATH))
    parser.add_argument("--card-tags-path", default=str(te.CARD_TAGS_PATH))
    parser.add_argument("--cards-sqlite-path", default=str(te.CARDS_SQLITE_PATH))
    cli_args = parser.parse_args()

    if not VIEWER_HTML.exists():
        te.halt(f"{VIEWER_HTML} not found -- run this from the repo root")

    global ctx, face_ctx
    ctx = ev.load_export_context(
        Path(cli_args.cards_path), Path(cli_args.card_tags_path), Path(cli_args.cards_sqlite_path),
    )

    print("\nbuilding face-scoped corpus view (per-face DFC lookup)...")
    face_start = time.perf_counter()
    face_ctx = ev.build_face_scoped_context(ctx)
    print(
        f"  {len(face_ctx.face_meta):,} individual face(s) indexed "
        f"({len(face_ctx.face_card_docs):,} total pool entries) in {time.perf_counter() - face_start:.1f}s"
    )

    server = HTTPServer(("127.0.0.1", cli_args.port), Handler)
    print(f"\nserving {VIEWER_HTML} on http://127.0.0.1:{cli_args.port}/ (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
