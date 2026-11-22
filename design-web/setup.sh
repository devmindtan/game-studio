#!/usr/bin/env bash
# Tải font + clone tool/asset tham khảo cho Design Lab. Chạy lại được nhiều lần.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VENDOR="$HERE/vendor"
mkdir -p "$VENDOR" "$HERE/fonts"

clone() {  # clone <tên> <url>
  local name="$1" url="$2"
  if [[ -d "$VENDOR/$name/.git" ]]; then
    git -C "$VENDOR/$name" pull --ff-only --quiet
  else
    git clone --depth 1 --quiet "$url" "$VENDOR/$name"
  fi
  printf '  %-18s %s\n' "$name" "$(du -sh "$VENDOR/$name" | cut -f1)"
}

echo "== tool/asset tham khảo (vendor/, không commit)"
clone icons            https://github.com/game-icons/icons.git
clone kenney-uipack    https://github.com/lpfd/kenney-uipack.git
clone kenney-ui-audio  https://github.com/Calinou/kenney-ui-audio.git

echo "== font VT323 (OFL, có tiếng Việt)"
if [[ ! -f "$HERE/fonts/VT323-Regular.ttf" ]]; then
  curl -fsSL -o "$HERE/fonts/VT323-Regular.ttf" \
    https://raw.githubusercontent.com/google/fonts/main/ofl/vt323/VT323-Regular.ttf
fi
if [[ ! -f "$HERE/fonts/OFL.txt" ]]; then
  curl -fsSL -o "$HERE/fonts/OFL.txt" \
    https://raw.githubusercontent.com/google/fonts/main/ofl/vt323/OFL.txt
fi
ls -lh "$HERE/fonts/VT323-Regular.ttf" | awk '{print "  VT323 " $5}'

echo "ok: design-web/serve.sh"
