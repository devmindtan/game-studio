#!/usr/bin/env python3
"""aura-aegis — Thần hộ, near half of a horizontal 3D orbit.

Three golden bucklers circle the hero's waist on a flattened ellipse (16x5).
This sprite holds the near (lower) half and is drawn in front of the hero;
aura-aegis-back holds the far (upper) half drawn behind him. Same 48x48 frame,
feet anchor (24,44), 4 form + 8 loop frames, "loop" name as the game expects.
"""
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
import orbit_shields  # noqa: E402
from sheet import export  # noqa: E402

if __name__ == "__main__":
    orbit_shields.build(HERE, HERE.name, "front", export)
    print("OK", HERE.name)
