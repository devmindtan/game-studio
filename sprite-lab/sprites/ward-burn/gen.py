#!/usr/bin/env python3
"""ward-burn: Hoả y (special card), redrawn 2026-11-22 (bach-ai design/special-fx-redesign.md H4).

A low ring of solid flames round the hero, flickering out of step, embers rising (lib/specialfx.flame_ring).
The old one was dotted dashes in a 48 px frame drawn at scale 1 (about 24 px on a 100 px burn). Double density
(px_scale 0.5); the hitbox circle (from the ring mask) lets the run scale it to the card's radius (_ring_fx).
Chạy: gamekit art run ward-burn
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

S = 128
C = S / 2
ANIM = [("cast", specialfx.flame_ring(S, 52, 10), 13, False,
         {"hitbox": {"shape": "circle", "center": [C, C + 8], "active": [0, 9], "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
