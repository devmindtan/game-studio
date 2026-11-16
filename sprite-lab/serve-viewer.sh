#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8765}"
URL="http://localhost:${PORT}/viewer.html"
echo "Sprite Lab Viewer: $URL"
echo "Nhấn Ctrl+C để dừng."
# regenerate manifest so new sprites appear
python3 - <<'PY'
import json, os, glob
base = 'sprites'
sprites = []
for name in sorted(os.listdir(base)):
    d = os.path.join(base, name)
    if not os.path.isdir(d): continue
    meta_path = os.path.join(d, f'{name}.json')
    if not os.path.exists(meta_path): continue
    with open(meta_path) as f: meta = json.load(f)
    entry = {'name': name, 'meta': meta,
             'strip': f'sprites/{name}/{name}_strip.png',
             'preview': f'sprites/{name}/preview.png'}
    gifs = {}
    for g in sorted(glob.glob(os.path.join(d, '*.gif'))):
        gifs[os.path.splitext(os.path.basename(g))[0]] = f'sprites/{name}/{os.path.basename(g)}'
    entry['gifs'] = gifs
    sprites.append(entry)
with open('sprites-manifest.json','w') as f: json.dump({'sprites': sprites}, f, ensure_ascii=False, indent=2)
print('manifest:', len(sprites), 'sprites')
PY
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
