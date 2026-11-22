#!/usr/bin/env python3
"""ward-freeze: Băng ấn (special card), redrawn 2026-11-22 (bach-ai design/special-fx-redesign.md H5).

Frost swirls in, a ring of solid faceted ice spikes bursts up at the freeze's reach, then shatters into shards
(lib/specialfx.ice_nova). The old one was a dotted ring with spikes and no hitbox, so _ring_fx scaled it from a
25 px guess. Double density (px_scale 0.5); hitbox from the ring mask. Chạy: gamekit art run ward-freeze
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

S = 144
C = S / 2
ANIM = [("cast", specialfx.ice_nova(S, 50, 13), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [3, 7], "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
