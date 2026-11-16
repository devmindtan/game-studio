#!/usr/bin/env bash
# Studio web: Sprite Lab viewer (viewer.html) + game dashboard (games.html).
# The server is rooted at the workspace so the dashboard can show each game's own
# sprites and screenshots (games/<g>/...); pages live in sprite-lab/.
#   GET  /sprite-lab/games-manifest.json   rebuilt on every request (always current)
#   POST /api/review?game=<slug>           saves the user's verdicts to
#                                          games/<slug>/design/review.json (only there)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8765}"
URL="http://localhost:${PORT}/sprite-lab/viewer.html"
echo "Studio: $URL"
echo "Game dashboard: http://localhost:${PORT}/sprite-lab/games.html"
echo "Nhấn Ctrl+C để dừng."
python3 build_manifest.py
python3 build_games_manifest.py
if [[ -n "${NO_OPEN:-}" ]]; then :   # tests / agents: do not open a browser
elif command -v xdg-open >/dev/null 2>&1; then (sleep 0.5; xdg-open "$URL" >/dev/null 2>&1 || true) &
elif command -v open >/dev/null 2>&1; then (sleep 0.5; open "$URL" >/dev/null 2>&1 || true) & fi
# Serve with "no-store": sprites are re-rendered all the time and a cached PNG/GIF
# would show the previous art (lesson 2026-11-16: the redrawn mage did not appear).
exec python3 -c '
import http.server, json, os, re, sys, urllib.parse
LAB = os.getcwd()
ROOT = os.path.dirname(LAB)
sys.path.insert(0, LAB)
import build_games_manifest

class Studio(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(302); self.send_header("Location", "/sprite-lab/viewer.html"); self.end_headers(); return
        if urllib.parse.urlparse(self.path).path == "/sprite-lab/games-manifest.json":
            try:
                build_games_manifest.build()
            except Exception as e:  # serve the last good manifest, report why
                sys.stderr.write("games manifest: %s\n" % e)
        super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        if url.path != "/api/review":
            self.send_error(404); return
        slug = urllib.parse.parse_qs(url.query).get("game", [""])[0]
        game = os.path.join(ROOT, "games", slug)
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or not os.path.isfile(os.path.join(game, "project.godot")):
            self.send_error(400, "unknown game"); return
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > 512 * 1024:
            self.send_error(413); return
        try:
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            assert isinstance(data, dict)
        except Exception:
            self.send_error(400, "bad json"); return
        os.makedirs(os.path.join(game, "design"), exist_ok=True)
        path = os.path.join(game, "design", "review.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        body = b"{\"ok\": true}"
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), Studio).serve_forever()
' "$PORT"
