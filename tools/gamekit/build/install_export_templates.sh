#!/usr/bin/env bash
# Install the Godot export templates matching the installed editor.
# Only the Linux, Windows and Web (no-threads) templates are kept (~200 MB of
# the 1.2 GB archive). The archive is checksum-verified, then deleted.
#
#   gamekit templates
set -euo pipefail

GODOT="${GODOT:-godot}"
full="$("$GODOT" --version 2>/dev/null | tail -n1)"          # 4.7.2.stable.official.ed1daf0bf
ver="$(cut -d. -f1-4 <<<"$full")"                             # 4.7.2.stable
tag="${ver%.stable}-stable"                                   # 4.7.2-stable
[[ "$ver" == *.stable ]] || { echo "Only stable editors are supported (got $full)" >&2; exit 1; }

dest="${XDG_DATA_HOME:-$HOME/.local/share}/godot/export_templates/$ver"
if [[ -f "$dest/linux_release.x86_64" && -f "$dest/windows_release_x86_64.exe" && -f "$dest/web_nothreads_release.zip" ]]; then
  echo "Export templates already installed in $dest"
  exit 0
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
base="https://github.com/godotengine/godot/releases/download/$tag"
tpz="Godot_v${tag}_export_templates.tpz"

echo "Downloading $tpz (about 1.2 GB)..."
curl -fL --progress-bar -o "$work/$tpz" "$base/$tpz"
curl -fsL -o "$work/SHA512-SUMS.txt" "$base/SHA512-SUMS.txt"
expected="$(grep " $tpz\$" "$work/SHA512-SUMS.txt" | cut -d' ' -f1)"
[[ -n "$expected" ]] || { echo "No checksum for $tpz" >&2; exit 1; }
echo "$expected  $work/$tpz" | sha512sum -c -

mkdir -p "$dest"
unzip -q -j -o "$work/$tpz" \
  templates/version.txt \
  'templates/linux_*.x86_64' \
  'templates/windows_*_x86_64.exe' \
  'templates/windows_*_x86_64_console.exe' \
  'templates/web_nothreads_*.zip' \
  -d "$dest"
echo "Installed to $dest:"
ls -1 "$dest"
