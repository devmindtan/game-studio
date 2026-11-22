#!/usr/bin/env python3
"""ward-pulse: Thánh kiếm (special card), redrawn 2026-11-22 (bach-ai design/special-fx-redesign.md H2).

Six bright swords point outward and sweep one turn round the hero with gold arc trails, then flare into rays
(lib/specialfx.holy_blades). Double density (px_scale 0.5), anchor at the centre; the hitbox circle is measured
from the swept-ring mask so the run's _ring_fx scales it to the card's reach.
Chạy: gamekit art run ward-pulse
"""
import json
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import specialfx  # noqa: E402
from sheet import export  # noqa: E402

S = 144
C = S / 2
ANIM = [("cast", specialfx.holy_blades(S, 60, 14), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [3, 9], "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
