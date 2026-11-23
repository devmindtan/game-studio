#!/usr/bin/env python3
"""shadow-burst: Bóng tối: nổ bóng khi quái mang Ăn mòn chết (bach-ai design/species.md E5/E6, 2026-11-23).

Three options to choose from (user rule: 2-3 different designs): opt_a, opt_b, opt_c (lib/elementfx.dark_burst_a/b/c).
Double density (px_scale 0.5). Once one is chosen the others are removed.
Chạy: gamekit art run shadow-burst
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
ANIM = [(f"opt_{k}", getattr(elementfx, f"dark_burst_{k}")(S), 12, False, {}) for k in "abc"]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(C, C))
    meta = HERE / f"{HERE.name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", HERE.name)
