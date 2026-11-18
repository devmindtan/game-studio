#!/usr/bin/env python3
"""aura-aegis-back — far half of Thần hộ's horizontal 3D shield orbit.

Companion to aura-aegis: the upper arc of the flattened ellipse, drawn behind
the hero so the bucklers visibly pass behind his torso. Same phase and timing.
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
    orbit_shields.build(HERE, HERE.name, "back", export)
    print("OK", HERE.name)
