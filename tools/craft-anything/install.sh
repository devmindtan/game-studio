#!/usr/bin/env bash
# Install Craft Anything into tools/craft-anything/app (no sudo, no system files).
#
# Downloads the pinned release .deb from GitHub and extracts it here. Run it
# again to reinstall or to switch VERSION.
set -euo pipefail

VERSION="${CRAFT_ANYTHING_VERSION:-0.6.1}"
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64) DEB_ARCH="x86_64" ;;
  aarch64|arm64) DEB_ARCH="aarch64" ;;
  *) echo "Kiến trúc chưa hỗ trợ: $ARCH" >&2; exit 1 ;;
esac

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEB="craft-anything-${VERSION}-linux-${DEB_ARCH}.deb"
URL="https://github.com/storytold/craft-anything/releases/download/v${VERSION}/${DEB}"

for cmd in curl dpkg; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Thiếu $cmd" >&2; exit 1; }
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Tải $DEB (~68 MB)…"
curl -fsSL --max-time 600 -o "$TMP/$DEB" "$URL"
file -b "$TMP/$DEB" | grep -q "Debian binary package" || { echo "Tệp tải về không phải .deb" >&2; exit 1; }

echo "Giải nén vào $HERE/app …"
rm -rf "$HERE/app"
mkdir -p "$HERE/app"
dpkg -x "$TMP/$DEB" "$HERE/app"

CLI="$HERE/app/usr/bin/craft-anything-cli"
[[ -x "$CLI" ]] || { echo "Không thấy craft-anything-cli sau khi giải nén" >&2; exit 1; }

# Register the coding agent once (Craft Anything has no model of its own).
export XDG_CONFIG_HOME="$HERE/state/config"
export XDG_DATA_HOME="$HERE/state/data"
export XDG_CACHE_HOME="$HERE/state/cache"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME"
backends="$("$CLI" ai list --output-format text 2>/dev/null || true)"
if ! printf '%s' "$backends" | grep -q "name: Claude Code"; then
  if command -v claude >/dev/null 2>&1; then
    echo "Đăng ký backend Claude Code…"
    "$CLI" ai add "Claude Code" --kind agent_cli --model claude-code --output-format text >/dev/null
  else
    echo "Không thấy lệnh 'claude'; cài Claude Code rồi chạy: ./ca ai detect" >&2
  fi
fi

echo
"$HERE/ca" doctor --output-format text 2>&1 | head -5 || true
echo
echo "Xong. Ví dụ:"
echo "  tools/craft-anything/ca rebuild - \"Một màn survivor 2D bằng Godot 4, WASD, quái theo sóng, tự bắn, thẻ nâng cấp\" \\"
echo "      --rounds 1 --unattended --allow-run --backend \"Claude Code\" --build-with godot"
