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
"""
import argparse
import json
import sys
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


def get_or_compute_anchor(name: str) -> tuple:
    """Returns (status_code, json_bytes). Exact-match resolve against
    cards.sqlite (same convention as emit_viewer's batch path); ambiguous
    or missing is a 404 with the reason, never a guess."""
    rows = ctx.conn.execute("SELECT oracle_id FROM cards WHERE name = ? COLLATE NOCASE", (name,)).fetchall()
    if len(rows) == 0:
        return 404, json.dumps({"error": f"{name!r}: no match in cards.sqlite"}).encode()
    if len(rows) > 1:
        return 404, json.dumps({"error": f"{name!r}: ambiguous, {len(rows)} matches"}).encode()
    oracle_id = rows[0][0]
    if oracle_id not in ctx.card_docs:
        return 404, json.dumps({"error": f"{name!r}: resolved in cards.sqlite but absent from the jsonl corpus"}).encode()

    slug = te.filename_slug(name)
    cache_path = VIEWER_DATA_DIR / f"{slug}.json"
    if cache_path.exists():
        return 200, cache_path.read_bytes()

    VIEWER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ev.export_anchor(name, oracle_id, ctx, VIEWER_DATA_DIR)
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
            status, body = get_or_compute_anchor(name)
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

    global ctx
    ctx = ev.load_export_context(
        Path(cli_args.cards_path), Path(cli_args.card_tags_path), Path(cli_args.cards_sqlite_path),
    )

    server = HTTPServer(("127.0.0.1", cli_args.port), Handler)
    print(f"\nserving {VIEWER_HTML} on http://127.0.0.1:{cli_args.port}/ (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
