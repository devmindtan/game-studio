#!/usr/bin/env python3
"""ward-haste: Lưu tinh (special card), redrawn 2026-11-22 (bach-ai design/special-fx-redesign.md H8).

three shooting stars orbit with gold trails, then flare (lib/specialfx.shooting_stars). The old one was a dotted swirl. Drawn at the hero; double density (px_scale 0.5).
Chạy: gamekit art run ward-haste
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

S = 112
ANIM = [("cast", specialfx.shooting_stars(S, 12), 14, False,
         {"hitbox": {"shape": "circle", "center": [S / 2, S / 2], "active": [2, 8]}})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(S / 2, S / 2))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
