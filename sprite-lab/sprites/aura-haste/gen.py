#!/usr/bin/env python3
"""aura-haste: Rune tốc độ aura, redrawn 2D 2026-11-22 (bach-ai roadmap I1, user: the game is 2D, not 2.5D).

a round ring of gold speed chevrons turning round the body (lib/specialfx). The old aura lay as a flat ellipse at the feet / orbited in 3D with a back half.
Anchor at the feet (the run draws auras at player_pos); the art centres on the body. Double density.
Chạy: gamekit art run aura-haste
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

ANIM = [("loop", specialfx.haste_ring(96, 8), 12, True, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=specialfx.AURA_FEET)
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
