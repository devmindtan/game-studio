#!/usr/bin/env python3
"""sword-slash-opts: three redesign options for Chém kiếm (bach-ai design/blade-arc-redesign.md step 2,
2026-11-23): opt_a thick fan smear, opt_b twin crescents, opt_c sweeping blade with afterimages. One swing to
the right each; the chosen one gets all directions and tiers II-V in sword-slash*.
Chạy: gamekit art run sword-slash-opts
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
import slashfx  # noqa: E402
from sheet import export  # noqa: E402

ANIM = [("opt_a", slashfx.slash_fan(), 14, False, {}), ("opt_b", slashfx.slash_twin(), 14, False, {}),
        ("opt_c", slashfx.slash_blade(), 14, False, {})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=slashfx.PIV)
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
