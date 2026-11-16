#!/usr/bin/env bash
# Studio web: Sprite Lab viewer (viewer.html) + game dashboard (games.html).
# The server is rooted at the workspace so the dashboard can show each game's own
# sprites and screenshots (games/<g>/...); pages live in sprite-lab/.
#   GET  /sprite-lab/games-manifest.json   rebuilt on every request (always current)
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
import http.server, os, sys, urllib.parse
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

http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), Studio).serve_forever()
' "$PORT"
