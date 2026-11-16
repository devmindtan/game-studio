#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8765}"
URL="http://localhost:${PORT}/viewer.html"
echo "Sprite Lab Viewer: $URL"
echo "Nhấn Ctrl+C để dừng."
# regenerate both manifests so new sprites and game skills appear
python3 build_manifest.py
python3 build_games_manifest.py
# open browser if possible
if command -v xdg-open >/dev/null 2>&1; then (sleep 0.5; xdg-open "$URL" >/dev/null 2>&1 || true) &
elif command -v open >/dev/null 2>&1; then (sleep 0.5; open "$URL" >/dev/null 2>&1 || true) & fi
# Serve with "no-store": sprites are re-rendered all the time and a cached PNG/GIF
# would show the previous art (lesson 2026-11-16: the redrawn mage did not appear).
exec python3 -c '
import http.server, sys
class NoStore(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()
http.server.ThreadingHTTPServer(("", int(sys.argv[1])), NoStore).serve_forever()
' "$PORT"
