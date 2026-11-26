#!/usr/bin/env python3
"""crit-hit: Chí mạng hit flash on the struck monster (bach-ai, user 2026-11-26), three options to pick from.

a = Chém chéo, b = Vòng nổ đỏ, c = Gai nổ (sprite-lab/lib/critfx.py). Double density (px_scale 0.5).
Chạy: gamekit art run crit-hit
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
import critfx  # noqa: E402
from sheet import export  # noqa: E402

S = 64
C = S / 2
ANIM = [("a", critfx.crit_a(S), 18, False, {}), ("b", critfx.crit_b(S), 18, False, {}), ("c", critfx.crit_c(S), 18, False, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
