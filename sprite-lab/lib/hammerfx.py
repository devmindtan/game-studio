"""hammerfx: Búa thần (god hammer) — a gold war hammer called down out of the sky.

DNA (pixel-sprite skill, light family): the same gold ramp as the holy column, a
heavy gold head with a steel collar and a white rune, a swung handle, and at the
impact a white flash, a shock ring, gold rays, dust and stun stars. Tiers keep
the motif and each adds one idea:
  I   gold hammer, flash, one ring, sparks
  II  + a second, slower ring
  III + rays of light out of the impact
  IV  + a halo around the head, heavier dust
  V   + a white-hot core and a crown of sparkles

Each strike animation has 12 frames: 3 falling (accelerating), impact at 3, the
damage frames 3-5, then the hammer sinks and fades while the dust, debris and the
stun stars settle. The hit area is cut from the art around the impact
(fxkit.mask_art), never typed.
"""
from __future__ import annotations

import json
import math
import random

from spritekit import Canvas
import fxkit as fk
from burstfx import GOLD, _h01
from icefx import _p

W, H = 96, 160
IMPACT = (48.0, 110.0)

OUT = "#2e1d0b"
SCORCH = "#3a2a18"
WOOD, WOOD_L, WOOD_D = "#7a5530", "#a4763f", "#3f2a14"
STEEL, STEEL_D = "#e2ebf7", "#9aa9bd"
DUST, DUST_D = "#cbb086", "#8a7250"
DIRT = "#5c4630"

MS = [70, 55, 45, 45, 50, 55, 70, 80, 95, 110, 125, 140]   # ~0.94 s
FALL = [62, 27, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0]              # head height above the impact
SINK = [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2]                # the head settles into the ground
FADE = [255, 255, 255, 255, 255, 240, 215, 185, 150, 110, 60, 0]
LEVEL = [0.00, 0.00, 0.22, 1.00, 0.94, 0.84, 0.70, 0.56, 0.42, 0.30, 0.18, 0.08]
RING = [0.00, 0.00, 0.45, 1.00, 1.00, 0.92, 0.78, 0.58, 0.34, 0.14, 0.00, 0.00]
DUSTL = [0.00, 0.00, 0.35, 0.90, 1.00, 0.95, 0.88, 0.78, 0.64, 0.48, 0.30, 0.14]
FLASH = [0.00, 0.10, 0.26, 1.00, 0.62, 0.34, 0.18, 0.10, 0.05, 0.00, 0.00, 0.00]
# the handle points back towards the hero (screen degrees, y down), so the blow
# leans in from the side it came from
HANDLE = {"right": 195.0, "left": -15.0, "up": 105.0, "down": -75.0}


def _hammer_px(u, v):
    """Colour at (u, v) in the hammer's own frame: u runs from the head centre
    towards the pommel, v across the head. None = empty."""
    # head: a heavy crossbar, its polished striking face at the far end
    if -10.5 <= u <= 2.0 and abs(v) <= 12.5:
        if u <= -9.5 or u >= 1.0 or abs(v) >= 11.5:
            return OUT
        du, dv = u + 4.2, v                               # rune: outlined white gem
        ad = abs(du) + abs(dv)
        if ad <= 4.4:
            if ad <= 1.2:
                return GOLD[5]
            if ad <= 2.4:
                return GOLD[4]
            return GOLD[1] if ad <= 3.4 else OUT
        if u <= -8.5:
            col = GOLD[4]
        elif u <= -4.0:
            col = GOLD[3]
        elif u <= -0.5:
            col = GOLD[2]
        else:
            col = GOLD[1]
        if v <= -8.5:
            col = GOLD[min(4, GOLD.index(col) + 1)]       # lit top edge
        elif v >= 9.0:
            col = GOLD[max(0, GOLD.index(col) - 1)]       # shaded underside
        return col
    # short blunt back of the head
    if 2.0 < u <= 5.5 and abs(v) <= 7.5:
        if u >= 4.9 or abs(v) >= 6.7:
            return OUT
        return GOLD[2] if v <= 0 else GOLD[1]
    # steel collar where the handle enters the head
    if 5.0 < u <= 8.0 and abs(v) <= 5.5:
        if u >= 7.4 or abs(v) >= 4.9:
            return OUT
        return STEEL if v < 0 else STEEL_D
    # handle
    if 8.0 < u <= 36.0 and abs(v) <= 2.6:
        if abs(v) >= 2.0:
            return OUT
        for band in (14.0, 22.0, 30.0):
            if abs(u - band) < 1.0:
                return GOLD[2]
        return WOOD_L if v <= -0.8 else (WOOD if v < 1.0 else WOOD_D)
    # pommel
    if 35.6 < u <= 39.4 and abs(v) <= 3.2:
        if u >= 38.8 or abs(v) >= 2.6:
            return OUT
        return GOLD[3] if v < -0.8 else GOLD[1]
    return None


def _hammer(c, cx, cy, ang, alpha, grow=0, flat=None):
    """The hammer itself, rotated so its handle leaves at [ang]. grow/flat draw a
    hot silhouette just outside the shape (the flash of the hit)."""
    if alpha <= 0:
        return
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tmp = Canvas(c.width, c.height)
    for y in range(max(0, int(cy - 28)), min(tmp.height, int(cy + 54))):
        for x in range(max(0, int(cx - 54)), min(tmp.width, int(cx + 54))):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u = ca * dx + sa * dy
            v = -sa * dx + ca * dy
            col = _hammer_px(u, v)
            if col is None and grow > 0 and flat is not None:
                for du, dv in ((grow, 0), (-grow, 0), (0, grow), (0, -grow)):
                    if _hammer_px(u + du, v + dv):
                        col = flat
                        break
            if col is not None:
                tmp.pixel(x, y, col)
    if alpha < 255:
        tmp.img.putalpha(tmp.img.getchannel("A").point(lambda a: a * alpha // 255))
    c.paste(tmp)


def _shock(c, cx, cy, rx, level, cols, salt=61, rot=0.0, thick=3):
    """A shockwave running out over the ground: a bright leading edge with two
    bands behind it, a shadow underneath, thickening on the near (front) arc."""
    if level <= 0.05 or rx < 2:
        return
    ry = rx * 0.52
    n = max(64, int(math.tau * rx * 2.6))
    for i in range(n):
        if _h01(i // 6, salt, 5) < 0.12 + 0.78 * (1.0 - level):
            continue
        a = rot + i * math.tau / n
        wob = 0.95 + 0.10 * _h01(i, salt, 7)
        ca, sa = math.cos(a), math.sin(a)
        t = thick + (1 if sa > 0.25 and thick > 1 else 0)
        for k in range(t):
            rrx, rry = rx * wob - k, ry * wob - k * 0.52
            if rrx <= 0:
                continue
            _p(c, cx + ca * rrx, cy + sa * rry, cols[min(len(cols) - 1, k)])
        _p(c, cx + ca * (rx * wob + 0.9), cy + sa * (ry * wob + 1.5), OUT)
        if _h01(i, salt, 11) < 0.10 * level:
            _p(c, cx + ca * (rx * wob + 2.3), cy + sa * (ry * wob + 1.7), cols[1])


def _scorch(c, cx, cy, lv, tier):
    """The ground under the blow: a scorched ellipse with a rim of thrown dirt."""
    r = 12.0 + tier
    for y in range(int(cy - r * 0.5) - 1, int(cy + r * 0.5) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            dx, dy = (x - cx) / r, (y - cy) / (r * 0.5)
            d = dx * dx + dy * dy
            if d > 1.0:
                continue
            if d > 0.72:
                if _h01(x, y, 17) < 0.55 * lv:
                    _p(c, x, y, DIRT)
            elif _h01(x, y, 19) < 0.28 + 0.55 * lv:
                _p(c, x, y, SCORCH)


def _crack_lines(cx, cy, tier):
    rng = random.Random(500 + tier)
    out = []
    for _ in range(4 + tier):
        a = rng.uniform(0, math.tau)
        x, y = cx + math.cos(a) * 6.0, cy + math.sin(a) * 3.0
        pts = [(x, y)]
        for _ in range(3 + tier // 2):
            a += rng.uniform(-0.5, 0.5)
            step = rng.uniform(2.0, 3.6)
            x += math.cos(a) * step
            y += math.sin(a) * step * 0.55
            pts.append((x, y))
        out.append(pts)
    return out


def _cracks(c, lv, lines):
    if lv <= 0.05:
        return
    for pts in lines:
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            steps = max(1, int(max(abs(x1 - x0), abs(y1 - y0))))
            for s in range(steps + 1):
                x = x0 + (x1 - x0) * s / steps
                y = y0 + (y1 - y0) * s / steps
                _p(c, x, y, OUT)
                if i >= 1 and _h01(int(x), int(y), 23) < 0.55 * lv:
                    _p(c, x, y - 1, DIRT)


def _dust(c, cx, cy, lv, tier):
    """Grit and dust thrown up around the foot of the blow: round puffs, lit
    on top and shaded underneath."""
    if lv <= 0.05:
        return
    n = 3 + tier // 2
    for i in range(n):
        a = i * math.tau / n + 0.45
        d = 16 + 14 * (1.0 - lv) + 3 * _h01(i, 31, 1)
        rr = 2 + int(2 * lv)
        x = cx + math.cos(a) * d
        y = cy + math.sin(a) * d * 0.45 - 3 - 4 * (1.0 - lv)
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                if dx * dx + dy * dy > rr * rr:
                    continue
                if _h01(int(x) + dx, int(y) + dy, 37 + i) > 0.30 + 0.45 * lv:
                    continue
                if dx * dx + dy * dy > (rr - 1) * (rr - 1) and _h01(int(x), int(y), 43) < 0.5:
                    continue
                _p(c, x + dx, y + dy, DUST if dy < 0 else DUST_D)


def _flash(c, cx, cy, fl, tier):
    """The burst of the hit: a white-hot diamond with long thin rays. Drawn
    behind the hammer so the head stays readable against its own light."""
    if fl <= 0.04:
        return
    r = 4 + int(12 * fl)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            dd = abs(dx) + abs(dy)
            if dd > r:
                continue
            if dd <= max(2, r * 0.45):
                _p(c, cx + dx, cy + dy, GOLD[5])
            elif dd <= r * 0.8:
                _p(c, cx + dx, cy + dy, GOLD[4])
            elif _h01(cx + dx, cy + dy, 41) < 0.65:
                _p(c, cx + dx, cy + dy, GOLD[3])
    if tier >= 3:
        n = 8 if tier < 5 else 12
        fk.rays(c, cx, cy, r, r + 4 + int(11 * fl), n, GOLD[3], GOLD[5],
                rot=0.2 + 0.15 * tier)
    if tier >= 5 and fl > 0.25:
        # crown of sparkles around the burst (tier V's one new idea)
        for i in range(10):
            a = i * math.tau / 10 + 0.3
            d = r + 8 + (i % 2) * 5
            fk.sparkle(c, int(cx + math.cos(a) * d),
                       int(cy + math.sin(a) * d * 0.7), 1, GOLD[5], GOLD[3])


def _chips(c, cx, cy, f, chips):
    """Rock chips knocked out of the ground: fly out, then lie where they land."""
    age = f - 3
    if age < 0 or age > 10:
        return
    for a, sp, land in chips:
        d_end = 10 + sp * 20
        if age < land:
            t = age / land
            d = 8 + (d_end - 8) * t
            h = 7 * sp * t * (1.0 - t) * 3.0
            x = cx + math.cos(a) * d
            y = cy + math.sin(a) * d * 0.5 - h
            _p(c, x, y, OUT)
            _p(c, x + 0.6, y - 0.7, DUST)
        elif age <= land + 5:
            x = cx + math.cos(a) * d_end
            y = cy + math.sin(a) * d_end * 0.5
            _p(c, x, y, OUT if age == land else DIRT)


def _stars(c, cx, cy, f, lv, tier):
    """Stun stars circling over the blow (the skill stuns for 1 s)."""
    if not 4 <= f <= 10:
        return
    n = 2 if tier < 3 else 3
    for k in range(n):
        a = (f - 4) * 0.5 + k * math.tau / n
        x = cx + math.cos(a) * 14
        y = cy - 18 + math.sin(a) * 4
        tw = 0.55 + 0.45 * math.sin(f * 1.6 + k * 2.0)
        if _h01(int(x), int(y), 91 + k) < tw * max(0.35, lv):
            fk.sparkle(c, int(x), int(y), 2 if tier >= 4 else 1, GOLD[5], GOLD[3])


def _motes(c, cx, cy, f, lv, tier):
    """A few motes left hanging, then the last of the light."""
    if f < 7:
        return
    for i in range(3 + tier):
        a = i * 2.399 + f * 0.55
        r = 8 + (i * 3 + f) % 18
        x = cx + math.cos(a) * r
        y = cy - 22 - math.sin(a) * r * 0.5 + (f - 7) * 1.5
        if _h01(int(x), int(y), 97 + i) < 0.45 * lv:
            fk.sparkle(c, int(x), int(y), 1, GOLD[4], GOLD[2])


def _beam(c, cx, y1, lv):
    """A thread of light above the falling hammer: it is called down, not thrown."""
    if y1 <= 1 or lv <= 0.05:
        return
    for y in range(0, int(y1) + 1):
        t = y / float(y1)
        half = 1.8 + 1.8 * t
        for x in range(int(cx - half), int(cx + half) + 1):
            edge = abs(x - cx) / half
            if edge > 1.0:
                continue
            if edge < 0.5:
                col, dens = GOLD[4], 0.80 + 0.15 * lv
            else:
                col, dens = GOLD[2], 0.22 + 0.25 * lv
            if _h01(x, y, 33) < dens:
                _p(c, x, y, col)


def strike(tier, w, h, impact, direction="right", seed=13):
    cx, gy = impact
    ang = HANDLE[direction]
    rng = random.Random(seed)
    sparks = [(rng.uniform(0, math.tau), rng.uniform(0.55, 1.2)) for _ in range(10 + 2 * tier)]
    chips = [(rng.uniform(0, math.tau), rng.uniform(0.55, 1.25), 2 + int(rng.random() * 3))
             for _ in range(4 + tier)]
    cracks = _crack_lines(cx, gy, tier)
    frames, masks = [], []
    for f in range(12):
        c = Canvas(w, h)
        lv = LEVEL[f]
        rl = RING[f]
        dl = DUSTL[f]
        fl = FLASH[f]
        top = gy - FALL[f] + SINK[f]
        if f <= 2:
            _beam(c, cx, top - 10, 0.35 + 0.30 * f)
        if lv > 0:
            if tier >= 4:
                k = 1.0 - min(1.0, max(0.0, (f - 3) / 4.0))
                fk.glow(c, cx, gy, 15 + 6 * k, [GOLD[2] + "50", GOLD[1] + "40"], density=0.7)
            _scorch(c, cx, gy, min(1.0, lv * 2.0), tier)
            _cracks(c, min(1.0, lv * 2.0), cracks)
            k = min(1.0, max(0.0, (f - 2) / 7.0))
            _shock(c, cx, gy, 8 + 24 * k, rl, (GOLD[4], GOLD[2], GOLD[1]),
                   salt=61, rot=0.13 * f)
            if tier >= 2:
                k2 = min(1.0, max(0.0, (f - 3) / 8.0))
                _shock(c, cx, gy, 5 + 25 * k2, rl * 0.72, (GOLD[3], GOLD[1], GOLD[0]),
                       salt=63, rot=-0.11 * f)
            if tier >= 4:
                k3 = min(1.0, max(0.0, (f - 4) / 8.0))
                _shock(c, cx, gy, 9 + 26 * k3, rl * 0.50, (GOLD[2], GOLD[1], GOLD[0]),
                       salt=67, rot=0.07 * f)
        if lv > 0:
            _dust(c, cx, gy, dl, tier)
            _flash(c, cx, gy, fl, tier)
        if 3 <= f <= 5:
            _hammer(c, cx, top, ang, FADE[f], grow=1, flat=GOLD[4])
        _hammer(c, cx, top, ang, FADE[f])
        if lv > 0:
            _chips(c, cx, gy, f, chips)
            # sparks fly out and up, thinning as they cool
            for i, (a, sp) in enumerate(sparks):
                age = (f - 3) + i * 0.11
                if age <= 0 or age > 7:
                    continue
                d = 8 + sp * 26 * age ** 0.7
                x = cx + math.cos(a) * d
                y = gy + math.sin(a) * d * 0.45 - 20 * age + 5 * age * age
                if not (3 <= x <= w - 4 and 3 <= y <= h - 4):
                    continue
                fk.streak(c, x, y, math.cos(a) * 0.6, -1.2, 2 + (i % 2), GOLD[4], GOLD[2])
            _stars(c, cx, gy, f, lv, tier)
            _motes(c, cx, gy, f, lv, tier)
        frames.append(c)
        masks.append(fk.mask_art(c, cx, gy, 26.0))
    return fk.FxFrames(frames, masks)


def build(here, name, tier, export):
    """Export the four strike directions of one tier (gen.py calls this)."""
    anims = []
    for d in ("right", "left", "up", "down"):
        anims.append((f"strike_{d}", strike(tier, W, H, IMPACT, d), 13, False,
                      {"durations_ms": MS,
                       "hitbox": {"shape": "rect", "center": list(IMPACT), "active": [3, 5]}}))
    export(here, name, anims, anchor=IMPACT, preview_scale=1, gif_scale=1)
    meta = here / f"{name}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
