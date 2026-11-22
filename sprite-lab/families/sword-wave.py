#!/usr/bin/env python3
"""Family generator for Sóng kiếm: sword-wave and its tiers -ii .. -v (one file per skill family).

Redrawn 2026-11-21 (bach-ai design/cleave-wave-redesign.md): every flight direction drawn from geometry by
lib/wavefx.py at double density (px_scale 0.5) instead of rotating one crescent; sea-green air blade with a
trail and wind specks; the tier sets core / rim / side blades. Each tier folder's gen.py is a stub that runs
this file with its own __file__.
Chạy: gamekit art run sword-wave   (and sword-wave-ii .. sword-wave-v)
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"sword-wave": [1], "sword-wave-ii": [2], "sword-wave-iii": [3], "sword-wave-iv": [4], "sword-wave-v": [5]}
import json
import sys
from pathlib import Path


def _ws():
    for p in Path(TIER_FILE).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(TIER_FILE).resolve().parent
_V = TIERS[HERE.name]
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import wavefx  # noqa: E402
from sheet import export  # noqa: E402

if __name__ == "__main__":
    export(HERE, HERE.name, wavefx.animations(_V[0]), anchor=(wavefx.C, wavefx.C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5   # drawn at double density: same size on screen, twice the pixels
    meta.write_text(json.dumps(m, indent=2))
    print("OK", HERE.name)
