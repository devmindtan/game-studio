#!/usr/bin/env python3
"""root-snare: Rễ trói (bach-ai design/region-events-plan.md §4B, 2026-11-23):
option A (thorny hooked roots) chosen by the user 2026-11-23. One root cluster each (crack telegraph,
soil bulge, burst, hold, sink). Chạy: gamekit art run root-snare
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
import rootfx  # noqa: E402
from sheet import export  # noqa: E402

ANIM = [("snare", rootfx.root_hooks(), 10, False, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(rootfx.GX, rootfx.GY))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
