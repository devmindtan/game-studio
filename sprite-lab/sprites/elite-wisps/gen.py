#!/usr/bin/env python3
"""elite-wisps: option C: energy wisps rising round an elite (bach-ai roadmap F, 2026-11-23). Drawn white: the game tints it with the affix / aura colour.
Chạy: gamekit art run elite-wisps
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
import elementfx  # noqa: E402
from sheet import export  # noqa: E402

S = 64
ANIM = [("loop", elementfx.elite_wisps(S), 10, True, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(S / 2, S - 6))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
