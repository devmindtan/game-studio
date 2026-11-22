#!/usr/bin/env python3
"""ward-shock-strike: Lôi ấn's bolt on each struck monster (bach-ai design/special-fx-redesign.md H3, 2026-11-22).

A jagged bolt falls from above onto the monster's feet (anchor = bottom centre), flashes and throws sparks,
then thins away (lib/specialfx.shock_strike). Double density (px_scale 0.5).
Chạy: gamekit art run ward-shock-strike
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

W, H = 48, 112
ANIM = [("strike", specialfx.shock_strike(W, H, 9), 16, False,
         {"hitbox": {"shape": "circle", "center": [W / 2, H - 6], "active": [1, 3]}})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(W / 2, H - 6))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
