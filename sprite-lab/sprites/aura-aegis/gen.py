#!/usr/bin/env python3
"""aura-aegis: Thần hộ aura, redrawn 2D 2026-11-22 (bach-ai roadmap I1, user: the game is 2D, not 2.5D).

three small gold shields orbiting the body on one round path (lib/specialfx). The old aura lay as a flat ellipse at the feet / orbited in 3D with a back half.
Anchor at the feet (the run draws auras at player_pos); the art centres on the body. Double density.
Chạy: gamekit art run aura-aegis
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

forms, loops = specialfx.aegis_orbit(96, 4, 8)
ANIM = [("form", forms, 12, False, {}), ("loop", loops, 10, True, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=specialfx.AURA_FEET)
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
