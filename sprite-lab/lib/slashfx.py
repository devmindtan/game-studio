"""slashfx: redesign options for Chém kiếm (bach-ai design/blade-arc-redesign.md step 2, 2026-11-23).

Each option is one swing to the right in a 96 px frame at double density (px_scale 0.5), pivot (40, 52) as the
current sword-slash, 5 frames: wind-up, swing opening, peak, trail, dust. Fan of about 140 deg, outer radius
~34 px (~70 px in game at sprite scale 2). Solid pixels, dark rim, no dither, no area overlay.
"""

from __future__ import annotations

import math

from spritekit import Canvas
from icefx import _p

PIV = (40.0, 52.0)
R_OUT = 34.0
HALF = math.radians(70)

W = "#ffffff"
S1 = "#e8f2ff"
S2 = "#a9c8f0"
S3 = "#6f93c8"
S4 = "#40608f"
X = "#1a2236"


def _rim(c, col=X):
    w, h = c.width, c.height
    px = c.img.load()
    solid = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0}
    for x, y in solid:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in solid:
                _p(c, q[0], q[1], col)


def _fan(c, a0, a1, r_in, r_out, colour_at):
    """Fill the ring sector a0..a1 (radians, 0 = right, + = down) between r_in and r_out; colour_at(u, v) with
    u = 0..1 along the swing (0 = start), v = 0..1 from inner to outer edge, returning a colour or None."""
    cx, cy = PIV
    for y in range(c.height):
        for x in range(c.width):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            if r < r_in or r > r_out:
                continue
            a = math.atan2(dy, dx)
            if a < a0 or a > a1:
                continue
            col = colour_at((a - a0) / max(1e-6, a1 - a0), (r - r_in) / max(1e-6, r_out - r_in))
            if col:
                _p(c, x, y, col)


# swing goes from -70 deg (up-front) to +70 deg (down-front); frame k reveals up to `lead`
_LEAD = [0.15, 0.6, 1.0, 1.0, 1.0]
_TAIL = [0.0, 0.0, 0.25, 0.7, 1.0]


def slash_fan(frames=5):
    """A: a thick filled fan: white leading edge, steel body, tail thinning and fading to the inside."""
    out = []
    for f in range(frames):
        c = Canvas(96, 96)
        lead, tail = _LEAD[f], _TAIL[f]
        a0 = -HALF + 2 * HALF * tail
        a1 = -HALF + 2 * HALF * lead
        if f < 4:
            def col(u, v, f=f):
                thick = 0.35 + 0.65 * u              # thin at the tail, full at the lead
                if v < 1 - thick:
                    return None
                if u > 0.9 and v > 0.5:
                    return W
                if v > 0.85:
                    return S1
                return S2 if v > 0.6 else (S3 if f < 3 else S4)
            _fan(c, a0, a1, R_OUT * 0.45, R_OUT, col)
        else:
            for k in range(7):                       # dust
                a = -HALF + k * 2 * HALF / 6
                _p(c, PIV[0] + math.cos(a) * (R_OUT - 2), PIV[1] + math.sin(a) * (R_OUT - 2), S2)
        _rim(c)
        out.append(c)
    return out


def slash_twin(frames=5):
    """B: twin crescents, a thick outer moon and a thin inner one, speed lines behind, a glint at the tip."""
    out = []
    for f in range(frames):
        c = Canvas(96, 96)
        lead, tail = _LEAD[f], _TAIL[f]
        a0 = -HALF + 2 * HALF * tail
        a1 = -HALF + 2 * HALF * lead
        if f < 4:
            def outer(u, v):
                w = math.sin(u * math.pi) * 0.9 + 0.1      # crescent: thick in the middle
                return (W if v > 0.8 else S1 if v > 0.55 else S2) if v > 1 - w else None
            def inner(u, v):
                w = math.sin(u * math.pi) * 0.7 + 0.1
                return (S2 if v > 0.5 else S3) if v > 1 - w else None
            _fan(c, a0, a1, R_OUT * 0.72, R_OUT, outer)
            _fan(c, a0, a1, R_OUT * 0.42, R_OUT * 0.62, inner)
            if f <= 2:
                tx, ty = PIV[0] + math.cos(a1) * R_OUT, PIV[1] + math.sin(a1) * R_OUT
                for k in range(1, 4):
                    for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                        _p(c, tx + dx, ty + dy, W)
            for k in range(3):                       # speed lines along the swing
                a = a0 + (a1 - a0) * (0.2 + 0.3 * k)
                r = R_OUT + 3
                c.line(int(PIV[0] + math.cos(a) * r), int(PIV[1] + math.sin(a) * r),
                       int(PIV[0] + math.cos(a - 0.25) * r), int(PIV[1] + math.sin(a - 0.25) * r), S2, 1)
        else:
            for k in range(5):
                a = -HALF + k * 2 * HALF / 4
                _p(c, PIV[0] + math.cos(a) * R_OUT, PIV[1] + math.sin(a) * R_OUT, S1)
        _rim(c)
        out.append(c)
    return out


def _blade(c, a, length, cols, w_max=2):
    """A sword silhouette from the pivot along angle a: grip, guard, blade with a bright edge."""
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    for t in range(int(length)):
        x, y = PIV[0] + ux * t, PIV[1] + uy * t
        if t < 5:
            _p(c, x, y, "#6b4a2a")
        elif t < 7:
            for s in range(-3, 4):
                _p(c, x + nx * s, y + ny * s, "#c9a13a")
        else:
            w = w_max if t < length - 4 else max(0, w_max - 1)
            for s in range(-w, w + 1):
                _p(c, x + nx * s, y + ny * s, cols[0] if s == -w else cols[1])


def slash_blade(frames=5):
    """C: the sword itself sweeps through the arc; thin ghost blades spaced along the path and a bright edge
    smear at the tip trail it."""
    out = []
    for f in range(frames):
        c = Canvas(96, 96)
        lead = _LEAD[f]
        a1 = -HALF + 2 * HALF * lead
        if f < 4:
            if f >= 1:
                _fan(c, max(-HALF, a1 - 1.5), a1, R_OUT - 4, R_OUT + 1,
                     lambda u, v: S1 if u > 0.7 else (S2 if u > 0.35 else S3))
                for back, cols in ((1.2, (S4, S4)), (0.8, (S3, S3)), (0.4, (S2, S2))):
                    if a1 - back >= -HALF - 0.05:
                        _blade(c, a1 - back, R_OUT - 2, cols, 0)
            if f < 4:
                _blade(c, a1, R_OUT, (W, "#d8e2f0") if f < 3 else (S2, S3))
        else:
            for k in range(5):
                a = -HALF + k * 2 * HALF / 4
                _p(c, PIV[0] + math.cos(a) * (R_OUT - 3), PIV[1] + math.sin(a) * (R_OUT - 3), S2)
        _rim(c)
        out.append(c)
    return out
