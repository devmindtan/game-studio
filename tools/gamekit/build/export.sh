#!/usr/bin/env bash
# Export a game and package each platform as a zip in <game>/builds/dist/.
#
#   gamekit export <game>                 # Linux, Windows, Web
#   gamekit export <game> Web             # one preset (names from export_presets.cfg)
#   SKIP_TESTS=1 gamekit export <game>    # skip the test gate
#   DEBUG=1 gamekit export <game>         # debug build instead of release
#
# Heavy steps run through `limited` when it exists (machine rule: keep 10% free).
set -euo pipefail

game="${1:?usage: export.sh <game-dir> [preset...]}"; shift
cd "$game"
[[ -f project.godot && -f export_presets.cfg ]] || { echo "$game: needs project.godot and export_presets.cfg (gamekit install $game)" >&2; exit 2; }

GODOT="${GODOT:-godot}"
RUN=()
command -v limited >/dev/null 2>&1 && RUN=(limited)
presets=("$@")
[[ ${#presets[@]} -gt 0 ]] || presets=(Linux Windows Web)

version="$(sed -n 's/^config\/version="\(.*\)"/\1/p' project.godot)"
version="${version:-0.0.0}"
slug="$(basename "$PWD")"
mode="--export-release"; [[ "${DEBUG:-0}" == 1 ]] && mode="--export-debug"

ver="$("$GODOT" --version 2>/dev/null | tail -n1 | cut -d. -f1-4)"
tdir="${XDG_DATA_HOME:-$HOME/.local/share}/godot/export_templates/$ver"
[[ -d "$tdir" ]] || { echo "No export templates for $ver. Run: gamekit templates" >&2; exit 1; }

echo "== import"
"${RUN[@]}" "$GODOT" --headless --path . --import >/dev/null 2>&1 || true

if [[ "${SKIP_TESTS:-0}" != 1 ]]; then
  echo "== tests"
  tlog="$(mktemp)"
  if ! "${RUN[@]}" "$GODOT" --headless --path . -s res://addons/gamekit/test/run_tests.gd >"$tlog" 2>&1; then
    grep -E "^FAIL|SCRIPT ERROR" "$tlog" >&2 || true
    echo "Tests failed - not exporting." >&2; rm -f "$tlog"; exit 1
  fi
  grep -E "^[0-9]+ passed" "$tlog" || true
  rm -f "$tlog"
fi

mkdir -p builds/dist
status=0
for preset in "${presets[@]}"; do
  out="$(awk -v p="$preset" '
    /^\[preset\.[0-9]+\]$/ {inpreset=1; name=""; next}
    /^\[/ {inpreset=0}
    inpreset && /^name=/ {name=$0; sub(/^name="/,"",name); sub(/"$/,"",name)}
    inpreset && /^export_path=/ && name==p {v=$0; sub(/^export_path="/,"",v); sub(/"$/,"",v); print v; exit}
  ' export_presets.cfg)"
  [[ -n "$out" ]] || { echo "Unknown preset: $preset" >&2; status=1; continue; }
  dir="$(dirname "$out")"
  rm -rf "$dir"; mkdir -p "$dir"
  echo "== export $preset -> $out"
  log="$(mktemp)"
  if ! "${RUN[@]}" "$GODOT" --headless --path . "$mode" "$preset" "$out" >"$log" 2>&1 || [[ ! -s "$out" ]]; then
    grep -E "ERROR|error" "$log" | head -20 >&2
    echo "Export $preset failed (full log: $log)" >&2
    status=1; continue
  fi
  rm -f "$log"
  cp assets/credits/CREDITS.md "$dir/" 2>/dev/null || true
  lower="$(tr '[:upper:]' '[:lower:]' <<<"$preset")"
  zipfile="$PWD/builds/dist/${slug}-${version}-${lower}.zip"
  rm -f "$zipfile"
  (cd "$dir" && zip -qr "$zipfile" .)
  echo "   packaged $(du -h "$zipfile" | cut -f1)  builds/dist/$(basename "$zipfile")"
done
exit $status
