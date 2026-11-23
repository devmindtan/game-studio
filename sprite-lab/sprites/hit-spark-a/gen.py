#!/usr/bin/env python3
"""hit-spark-a: tia lửa trúng đòn vật lý cận chiến, phương án A: sao trắng bốn cánh (bach-ai roadmap cảm giác đánh, 2026-11-23).

One of three options (lib/hitfx), for the user to choose.
Double density (px_scale 0.5). 
Chạy: gamekit art run hit-spark-a
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
import hitfx  # noqa: E402
from sheet import export  # noqa: E402

S = hitfx.S
C = S / 2
ANIM = [("spark", hitfx.spark_star(), 20, False, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
