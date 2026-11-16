#!/usr/bin/env bash
# Serve <game>/builds/web over HTTP, load it in headless Chrome, print the page
# console, press Space, and save <game>/builds/web-smoke.png. Exit 1 on a JS exception.
#   gamekit smoke-web <game> [wait-ms]   (default 30000: the wasm is slow in software GL)
set -euo pipefail
kit="$(cd "$(dirname "$0")" && pwd)"
game="${1:?usage: smoke_web.sh <game-dir> [wait-ms]}"
wait_ms="${2:-30000}"
cd "$game"
[[ -f builds/web/index.html ]] || { echo "No web build. Run: gamekit export $game Web" >&2; exit 1; }
chrome="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
[[ -n "$chrome" ]] || { echo "No Chrome/Chromium found - web build NOT verified." >&2; exit 1; }
RUN=(); command -v limited >/dev/null 2>&1 && RUN=(limited)
profile="$(mktemp -d)"; log="$(mktemp)"
(cd builds/web && exec python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1) & http=$!
"${RUN[@]}" "$chrome" --headless=new --no-sandbox --user-data-dir="$profile" --use-angle=swiftshader \
  --enable-unsafe-swiftshader --window-size=1280,720 --remote-debugging-port=9333 about:blank >/dev/null 2>&1 & browser=$!
trap 'kill $browser $http 2>/dev/null; sleep 1; rm -rf "$profile" "$log"' EXIT
sleep 2
timeout $(( wait_ms / 1000 + 60 )) node "$kit/web_smoke_cdp.mjs" 9333 http://127.0.0.1:8765/index.html "$wait_ms" builds/web-smoke.png | tee "$log"
! grep -q '^EXCEPTION' "$log"
