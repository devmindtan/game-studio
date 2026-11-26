#!/usr/bin/env bash
# Design Lab server. Rooted at the workspace so screens can use the game's own sprites.
set -euo pipefail

WS="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8770}"

echo "Design Lab:      http://localhost:$PORT/design-web/index.html"
echo "Link một màn:    http://localhost:$PORT/design-web/#<game>/<màn>/<số hướng>"
echo "Ctrl+C để dừng."
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$WS"
