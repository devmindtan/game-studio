"""boltfx: projectiles in flight and lightning, drawn to the fx_craft density.

User 2026-11-18: projectiles blurred when drawn big; lightning should be thinner, taller
and start from a small dark cloud.
  projectile(kind, tier, size, deg, n): one flight animation drawn straight at angle deg
      (0 = right, clockwise on screen) on a double-density frame: no rotated pixels.
      Kinds: arcane (bright orb, tapered tail), fire (flame head, three-layer flame),
      solar (long golden ray), thunder (thin jagged spear), void (dark orb, purple swirl).
      Hit masks: the head only (the tail never makes the hit area longer).
  dark_cloud(c, x, y, s): a small outlined thundercloud.
  thin_bolt(c, ...): a lightning line, 1 px core + 1 px glow, forks from tier 3.
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
import fxkit as fk
from icefx import _disk, _p

PAL = {
    "arcane": ("#4a2a9a", "#7a5af0", "#7ef0ff", "#ffffff"),
    "fire": ("#8a1f1f", "#e0402a", "#ff8a2a", "#ffd84a"),
    "solar": ("#a8601a", "#ffb43a", "#ffe88a", "#fffbe0"),
    "thunder": ("#2a6ab0", "#9ad0ff", "#fff8c0", "#ffffff"),
    "void": ("#0a0418", "#3a0a6a", "#8a2ad8", "#e05aff"),
}
CLOUD = ("#22223a", "#3a3a5a", "#5a5a80")


def _tail(c, x, y, ux, uy, length, width, cols):
    px, py = -uy, ux
    for k, col in enumerate(cols):
        f = 1 - k / (len(cols) + 0.4)
        L, W = length * f, width * f
        c.polygon([(int(round(x + px * W)), int(round(y + py * W))), (int(round(x - px * W)), int(round(y - py * W))),
                   (int(round(x - ux * L)), int(round(y - uy * L)))], col)


def projectile(kind, tier, size, deg, n=6, seed=1):
    rim, mid, light, core = PAL[kind]
    cx = cy = size / 2
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    rng = random.Random(seed + int(deg))
    hr = 3.5 + tier * 0.7                     # head radius (double-density px)
    out, masks = [], []
    for f in range(n):
        c = Canvas(size, size)
        fl = 0.85 + 0.15 * math.sin(f * math.tau / n)
        hx, hy = cx + ux * hr * 0.6, cy + uy * hr * 0.6   # head slightly ahead of the anchor
        if kind == "arcane":
            _tail(c, hx, hy, ux, uy, (10 + tier * 2) * fl, hr * 0.9, [rim, mid, light])
            fk.glow(c, hx, hy, hr * fl + 1, [rim, mid, light, core])
            for k in range(2 + tier // 2):
                b = (f * 3 + k * 5) % 9 + 4
                fk.sparkle(c, int(hx - ux * b * 1.6 + px * ((k % 3) - 1) * 3), int(hy - uy * b * 1.6 + py * ((k % 3) - 1) * 3), 1, core, light)
        elif kind == "fire":
            _tail(c, hx, hy, ux, uy, (12 + tier * 3) * fl, hr * 1.1, [rim, mid, light, core])
            lay = Canvas(size, size)
            fk.glow(lay, hx, hy, hr * 1.05 * fl, [rim, mid, light, core])
            fk.stack(c, lay, "#3a0e0e")
            for k in range(3 + tier):
                b = (f * 2 + k * 3) % 8 + 3
                fk.streak(c, hx - ux * b * 2 + px * (k % 3 - 1) * 2, hy - uy * b * 2 + py * (k % 3 - 1) * 2, ux, uy, 2, light, mid)
        elif kind == "solar":
            L = 14 + tier * 3
            for k, (col, w) in enumerate(((rim, 3), (mid, 2), (light, 1))):
                c.line(int(round(hx - ux * L * fl)), int(round(hy - uy * L * fl)), int(round(hx + ux * 2)), int(round(hy + uy * 2)), col, w + 1 - k // 2)
            c.line(int(round(hx - ux * L * 0.7)), int(round(hy - uy * L * 0.7)), int(round(hx + ux * 2)), int(round(hy + uy * 2)), core)
            fk.sparkle(c, int(hx + ux * 2), int(hy + uy * 2), 2 + tier // 2, core, light)
        elif kind == "thunder":
            L = 16 + tier * 3
            pts = [(hx + ux * 3, hy + uy * 3)]
            segs = 6
            for k in range(1, segs + 1):
                t = k / segs
                j = ((k + f) % 3 - 1) * 2.2 * (1 if k < segs else 0)
                pts.append((hx - ux * L * t + px * j, hy - uy * L * t + py * j))
            lay = Canvas(size, size)
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                lay.line(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), mid, 3)
            fk.stack(c, lay, None)
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                c.line(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), core)
            fk.sparkle(c, int(pts[0][0]), int(pts[0][1]), 2, core, light)
            if f % 2 == 0:   # crackle off the shaft
                k = 2 + f % 3
                x0, y0 = pts[k]
                c.line(int(x0), int(y0), int(x0 + px * 4 * (1 if f % 4 else -1)), int(y0 + py * 4 * (1 if f % 4 else -1)), light)
        elif kind == "void":
            for k in range(4 + tier):   # dark motes drift behind
                b = (f * 2 + k * 3) % 10 + 4
                _disk(c, hx - ux * b * 1.5 + px * (k % 3 - 1) * 2, hy - uy * b * 1.5 + py * (k % 3 - 1) * 2, 1.2, mid)
            lay = Canvas(size, size)
            fk.glow(lay, hx, hy, hr * 1.1, [light, mid, rim, rim])
            fk.stack(c, lay, "#000000")
            for k in range(3):   # the swirl round the rim turns
                aa = f * 0.9 + k * math.tau / 3
                _p(c, hx + math.cos(aa) * hr, hy + math.sin(aa) * hr, core)
                _p(c, hx + math.cos(aa + 0.3) * hr, hy + math.sin(aa + 0.3) * hr, light)
        out.append(c)
        masks.append(fk.mask_art(c, hx, hy, hr * 1.2 + 1))
    return fk.FxFrames(out, masks)


def dark_cloud(c, x, y, s, flash=False):
    """A small dark thundercloud (outlined puffs, lit tops); flash lights its belly."""
    lay = Canvas(c.width, c.height)
    for dx, dy, r in ((-1.0, 0.2, 0.55), (0.0, -0.25, 0.7), (1.0, 0.15, 0.55), (-0.45, 0.35, 0.5), (0.5, 0.35, 0.5)):
        _disk(lay, x + dx * s, y + dy * s, r * s, CLOUD[1])
        _disk(lay, x + dx * s - r * s * 0.25, y + dy * s - r * s * 0.3, r * s * 0.5, CLOUD[2])
    _disk(lay, x, y + s * 0.45, s * 0.9, CLOUD[0])
    if flash:
        _disk(lay, x, y + s * 0.35, s * 0.4, "#9ad0ff")
    fk.stack(c, lay, "#0a0a18")


def thin_bolt(c, x0, y0, x1, y1, rng, tier, core="#fff8c0", glow="#9ad0ff", segs=10):
    """A thin lightning line: 1 px core over a 3 px glow, jagged, forks from tier 3."""
    pts = [(x0, y0)]
    for k in range(1, segs):
        t = k / segs
        pts.append((x0 + (x1 - x0) * t + rng.uniform(-5, 5) * (1 - t * 0.5), y0 + (y1 - y0) * t))
    pts.append((x1, y1))
    for (a, b), (cx_, cy_) in zip(pts, pts[1:]):
        c.line(int(a), int(b), int(cx_), int(cy_), glow, 3)
    for (a, b), (cx_, cy_) in zip(pts, pts[1:]):
        c.line(int(a), int(b), int(cx_), int(cy_), core)
    if tier >= 3:
        for k in (segs // 3, segs // 2 + 1):
            a, b = pts[k]
            ex, ey = a + rng.choice((-1, 1)) * (8 + tier), b + 10 + tier
            c.line(int(a), int(b), int(ex), int(ey), glow, 2)
            c.line(int(a), int(b), int(ex), int(ey), core)
    return pts


BOLT_MS = [70, 70, 50, 50, 55, 60, 80, 90, 100, 110, 120, 130]


def lightning_strike(tier, w, h, ground, radius, seed=51):
    """12 frames: a small dark cloud gathers above, a thin tall bolt hits the ground with
    a flash, crackle, fade. Hit mask: the flash at the landing point, frames 2-3."""
    cx = w / 2
    rng = random.Random(seed)
    cloud_y = 12 + tier
    cs = 6 + tier
    out, masks = [], []
    for f in range(12):
        c = Canvas(w, h)
        if f < 2:
            dark_cloud(c, cx, cloud_y, cs * (0.7 + 0.15 * f))
            fk.ring_band(c, cx, ground, radius * (0.4 + 0.2 * f), ["#2a6ab0", "#9ad0ff"])
            if f == 1:
                fk.sparkle(c, int(cx), int(cloud_y + cs), 2, "#fff8c0", "#9ad0ff")
        elif f < 6:
            dark_cloud(c, cx, cloud_y, cs, flash=f in (2, 4))
            r2 = random.Random(seed + f)
            thin_bolt(c, cx + r2.uniform(-2, 2), cloud_y + cs * 0.8, cx, ground, r2, tier)
            # the hit at the ground grows with the tier: a small spark at I, a burst with rays from III
            # (user 2026-11-18: early levels need no explosion)
            gk = (0.22 + 0.11 * tier) * (1.0 if f == 2 else 0.75)
            fk.glow(c, cx, ground, radius * gk, ["#2a6ab0", "#9ad0ff", "#fff8c0", "#ffffff"][-(2 + min(2, tier // 2)):], density=0.85)
            if tier >= 3:
                fk.rays(c, cx, ground, radius * 0.25, radius * (0.4 + 0.12 * tier), 4 + 2 * tier, "#fff8c0", "#ffffff", rot=f * 0.4)
            else:
                fk.sparkle(c, int(cx), int(ground), 2 + tier, "#ffffff", "#9ad0ff")
        else:
            k = f - 6
            if k < 3:
                dark_cloud(c, cx, cloud_y - k, cs * (1 - 0.15 * k))
            for s in range(6 + tier):
                a = s * 1.3 + k * 0.8
                r = radius * (0.3 + 0.12 * k) * (0.6 + (s % 3) * 0.2)
                fk.streak(c, cx + math.cos(a) * r, ground + math.sin(a) * r * 0.6, math.cos(a), math.sin(a), 3, "#c8f0ff", "#2a6ab0")
            if k < 3:
                fk.sparkle(c, int(cx), int(ground), 3 - k, "#ffffff", "#9ad0ff")
            if k >= 1:
                from icefx import _fade
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
        masks.append(fk.mask_art(c, cx, ground, radius * 0.75 if 2 <= f <= 3 else 0))
    return fk.FxFrames(out, masks)
