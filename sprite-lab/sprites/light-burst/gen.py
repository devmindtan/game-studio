#!/usr/bin/env python3
"""light-burst: Ánh sáng: nổ sáng khi Thánh ấn hết (bach-ai design/species.md E5/E6, 2026-11-23).

Option A chosen (user 2026-11-23) of three drawn (lib/elementfx.light_burst_a/b/c).
Double density (px_scale 0.5). 
Chạy: gamekit art run light-burst
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

S = 96
C = S / 2
ANIM = [("burst", elementfx.light_burst_a(S), 12, False, {})]   # option A chosen by the user 2026-11-23

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
