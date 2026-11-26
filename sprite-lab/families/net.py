#!/usr/bin/env python3
"""Family generator for Lưới (net-i .. net-v ball, net-burst-i .. net-burst-v, design/rogue-kits.md, 2026-11-26).

net-<t>: a rolled net weighted at the corners, spinning as it flies (fly_* all play the same spin, 4 frames, loop).
net-burst-<t>: the net opens over the crowd (fx_craft: 12 frames, 1 lead-in frame, hits frames 2-5 measured from a
hit mask disk, a 0.5 s ending where the net settles and fades). Each tier: a wider net, more knots, hemp to gold.
Chạy: gamekit art run net-i ; gamekit art run net-burst-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [burst radius, rope (dark, mid, light), weights]
TIERS = {"i": [34, ("#4a3418", "#8a6a3a", "#c8a870"), "#6a7590"], "ii": [38, ("#4a3418", "#9a7a44", "#e0c890"), "#8a94a6"],
         "iii": [42, ("#2a4a3a", "#4a8a6a", "#a0e0c0"), "#b8c4d8"], "iv": [46, ("#3a2a5a", "#7a5ab0", "#d0b8ff"), "#e0b8ff"],
         "v": [50, ("#7a4a10", "#c08020", "#fff4b0"), "#ffffff"]}
import json
import math
import sys
from pathlib import Path


def _ws():
    for p in Path(TIER_FILE).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(TIER_FILE).resolve().parent
TIER = HERE.name.rsplit("-", 1)[1]
R, (D, M, L), W = TIERS[TIER]
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(TIER_FILE).resolve().parents[2] / "lib"))
from spritekit import Canvas  # noqa: E402
from fxkit import FxFrames, mask_disk  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
OUT = "#14111c"


def ball():
    S = 40
    C = S // 2
    out = []
    for f in range(4):
        c = Canvas(S, S)
        c.ellipse(C - 7, C - 7, C + 7, C + 7, M)
        a0 = f * math.pi / 8
        for k in range(3):                                  # rope bands crossing the ball, turning
            a = a0 + k * math.pi / 3
            c.line(int(C + math.cos(a) * 7), int(C + math.sin(a) * 7), int(C - math.cos(a) * 7), int(C - math.sin(a) * 7), D, 1)
        c.pixel(C - 2, C - 3, L)
        for k in range(4):                                  # corner weights trailing on short ropes
            a = a0 * 2 + k * math.tau / 4
            x, y = int(C + math.cos(a) * 11), int(C + math.sin(a) * 11)
            c.line(int(C + math.cos(a) * 7), int(C + math.sin(a) * 7), x, y, M, 1)
            c.rect(x - 1, y - 1, x + 1, y + 1, W)
        c.outline(OUT)
        out.append(c)
    return S, out


def burst():
    S = 2 * R + 20
    C = S // 2
    out = []
    # opening share of the full size per frame: lead-in (0), spread (1-4), hold (5-6), settle and fade (7-11)
    grow = [0.15, 0.45, 0.75, 0.95, 1.0, 1.0, 1.0, 1.0, 0.98, 0.96, 0.94, 0.92]
    for f in range(12):
        c = Canvas(S, S)
        r = R * grow[f]
        if f >= 9 and f % 2:                                 # the last frames flicker out
            out.append(c)
            continue
        rope = M if f < 7 else D
        n = 6 + ("i ii iii iv v".split().index(TIER)) * 2   # spokes: more knots each tier
        for k in range(n):                                   # spokes
            a = k * math.tau / n
            c.line(C, C, int(C + math.cos(a) * r), int(C + math.sin(a) * r * 0.8), rope, 1)
        for ring in (0.35, 0.65, 1.0):                       # rings of the mesh
            pts = [(int(C + math.cos(k * math.tau / n) * r * ring), int(C + math.sin(k * math.tau / n) * r * ring * 0.8))
                   for k in range(n)]
            for a, b in zip(pts, pts[1:] + pts[:1]):
                c.line(a[0], a[1], b[0], b[1], rope, 1)
            if f < 7:
                for p in pts:
                    c.pixel(p[0], p[1], L)                   # knots catch the light
        if f <= 6:
            for k in range(4):                               # the corner weights
                a = k * math.tau / 4 + 0.4
                x, y = int(C + math.cos(a) * r), int(C + math.sin(a) * r * 0.8)
                c.rect(x - 1, y - 1, x + 1, y + 1, W)
        c.outline(OUT)
        out.append(c)
    masks = [mask_disk(S, S, C, C, R if 2 <= k <= 5 else 0) for k in range(12)]
    return S, FxFrames(out, masks)


if HERE.name.startswith("net-burst"):
    S, FR = burst()
    C = S / 2
    ANIM = [("burst", FR, 12.0, False, {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 5]}})]
else:
    S, FR = ball()
    C = S / 2
    HB = {"shape": "circle", "center": [C, C], "active": [0, 3], "radius": 8.0, "inner": 0.0}
    DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
        [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
    ANIM = [(n, [f.copy() for f in FR], 12.0, True, {"hitbox": dict(HB)}) for n, _ in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
