"""elementfx: options for the two special elements (bach-ai design/species.md E5/E6, user 2026-11-22).

Ánh sáng (Light): the Thánh ấn mark over a monster's head and the light burst when it ends.
Bóng tối (Dark): the Ăn mòn mark (smoke / cracks / drips) and the shadow burst when a marked monster dies.
Three options of each, different in shape and motion (not just colour), for the user to pick.
Flat 2D (no squash), solid pixels, dark rim, no dither (design/special-fx-redesign.md §2).
"""

from __future__ import annotations

import math

from spritekit import Canvas
from icefx import _p

# Light
L_W = "#fffbea"
L_1 = "#fff6d8"
L_2 = "#f6e7b0"
L_3 = "#e7c35a"
L_4 = "#b8862f"
L_X = "#5a3c14"
# Dark
D_W = "#e9c8ff"
D_1 = "#b27ae0"
D_2 = "#7a3fa8"
D_3 = "#4a2370"
D_4 = "#2a1240"
D_X = "#120818"


def _disk(c, cx, cy, r, col):
    ri = int(math.ceil(r))
    for y in range(-ri, ri + 1):
        for x in range(-ri, ri + 1):
            if x * x + y * y <= r * r:
                _p(c, cx + x, cy + y, col)


def _ring(c, cx, cy, r, col, w=1.0):
    ri = int(math.ceil(r + w))
    for y in range(-ri, ri + 1):
        for x in range(-ri, ri + 1):
            d = math.hypot(x, y)
            if r - w / 2 <= d <= r + w / 2:
                _p(c, cx + x, cy + y, col)


def _rim(c, col):
    """1 px dark outline round every drawn pixel (shapes stay readable over a busy fight)."""
    w, h = c.width, c.height
    px = c.img.load()
    solid = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0}
    for x, y in solid:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in solid:
                _p(c, q[0], q[1], col)


def _star4(c, cx, cy, r, core, arm, edge):
    for k in range(1, int(r) + 1):
        wid = max(0, int((r - k) / r * 2.5))
        for s in range(-wid, wid + 1):
            col = arm if abs(s) < wid else edge
            for dx, dy, sx, sy in ((k, 0, 0, 1), (-k, 0, 0, 1), (0, k, 1, 0), (0, -k, 1, 0)):
                _p(c, cx + dx + s * sx, cy + dy + s * sy, col)
    _disk(c, cx, cy, 1.6, core)


# ---------- Light: Thánh ấn mark (48 px canvas, px_scale 0.5 -> 24 px in game) ----------

def light_mark_a(size=48, frames=8):
    """A: a 4-point holy star that breathes (grows, glints) over the head."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        s = 0.5 + 0.5 * math.sin(f / frames * math.tau)
        _star4(c, c0, c0, 9 + 3 * s, L_W, L_2, L_3)
        if f % 4 == 1:
            _p(c, c0 + 7, c0 - 7, L_W)
        _rim(c, L_X)
        out.append(c)
    return out


def light_mark_b(size=48, frames=8):
    """B: a flat halo ring with a small cross inside, the ring's glint running round it."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        _ring(c, c0, c0, 11, L_3, 3.0)
        _ring(c, c0, c0, 11, L_2, 1.2)
        a = f / frames * math.tau
        _disk(c, c0 + math.cos(a) * 11, c0 + math.sin(a) * 11, 2.0, L_W)
        for k in range(-5, 6):
            _p(c, c0 + k, c0, L_1)
            _p(c, c0, c0 + k, L_1)
        _p(c, c0, c0, L_W)
        _rim(c, L_X)
        out.append(c)
    return out


def light_mark_c(size=48, frames=8):
    """C: a gold diamond rune (an eye of light) with two motes orbiting it."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        for y in range(-10, 11):
            wd = 7 - abs(y) * 7 // 10
            for x in range(-wd, wd + 1):
                _p(c, c0 + x, c0 + y, L_3 if abs(x) == wd or abs(y) == 10 else L_2)
        open_ = 1 if f % 8 in (3, 4) else 2
        for x in range(-4, 5):
            _p(c, c0 + x, c0, L_X)
        _disk(c, c0, c0, open_, L_W)
        for k in range(2):
            a = f / frames * math.tau + k * math.pi
            _disk(c, c0 + math.cos(a) * 15, c0 + math.sin(a) * 6, 1.5, L_W)
        _rim(c, L_X)
        out.append(c)
    return out


# ---------- Light: burst when Thánh ấn ends (96 px canvas) ----------

def light_burst_a(size=96, frames=8):
    """A: a solid sun flash with long and short rays, shrinking to a sparkle."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        r = 18 * (1 - u) + 4
        for k in range(8):
            a = k * math.tau / 8
            ln = (34 if k % 2 == 0 else 24) * (0.5 + u * 0.6)
            c.line(int(c0 + math.cos(a) * r), int(c0 + math.sin(a) * r),
                   int(c0 + math.cos(a) * ln), int(c0 + math.sin(a) * ln), L_2 if u < 0.7 else L_3, 2)
        _disk(c, c0, c0, r, L_2)
        _disk(c, c0, c0, r * 0.65, L_1)
        _disk(c, c0, c0, r * 0.35, L_W)
        _rim(c, L_X)
        out.append(c)
    return out


def light_burst_b(size=96, frames=8):
    """B: eight light feathers fanning out from the centre and fading."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        d = 8 + u * 30
        for k in range(8):
            a = k * math.tau / 8 + 0.2
            x, y = c0 + math.cos(a) * d, c0 + math.sin(a) * d
            ln = 16 * (1 - u * 0.4)
            for t in range(int(ln)):
                w = max(0, int((1 - t / ln) * 4.0))
                for s in range(-w, w + 1):
                    _p(c, x - math.cos(a) * t - math.sin(a) * s, y - math.sin(a) * t + math.cos(a) * s,
                       L_1 if s == 0 else L_2)
        if u < 0.4:
            _disk(c, c0, c0, 8 * (1 - u * 2), L_W)
        _rim(c, L_X)
        out.append(c)
    return out


def light_burst_c(size=96, frames=8):
    """C: a holy cross: a vertical and a horizontal beam flare, then thin out."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        ln = 40 * min(1.0, u * 3 + 0.3)
        w = 6 * (1 - u) + 1
        for t in range(-int(ln), int(ln) + 1):
            tw = w * (1 - abs(t) / (ln + 1) * 0.7)
            for s in range(-int(tw), int(tw) + 1):
                col = L_W if abs(s) < tw * 0.4 else L_2
                _p(c, c0 + s, c0 + t, col)
                if abs(t) < ln * 0.7:
                    _p(c, c0 + t, c0 + s, col)
        _disk(c, c0, c0, 6 * (1 - u) + 2, L_W)
        _rim(c, L_X)
        out.append(c)
    return out


# ---------- Dark: Ăn mòn mark (48 px canvas) ----------

def dark_mark_a(size=48, frames=8):
    """A: three wisps of purple smoke curling up from the body (one per stack)."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        for k in range(3):
            for t in range(10):
                life = ((f + k * 3 + t) % frames) / frames
                x = c0 - 9 + k * 9 + math.sin(t * 0.9 + f * 0.8 + k) * 3
                y = c0 + 14 - t * 2.6
                r = 3.2 - t * 0.22
                if r > 0.6:
                    _disk(c, x, y, r, D_2 if t < 4 else (D_3 if life < 0.5 else D_1))
        _rim(c, D_X)
        out.append(c)
    return out


def dark_mark_b(size=48, frames=8):
    """B: a dark sigil of cracks under the feet, glowing purple along the cracks, pulsing."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        glow = D_1 if f % 4 < 2 else D_2
        for k in range(5):
            a = k * math.tau / 5 - math.pi / 2
            x, y = c0, c0
            for t in range(4):
                nx = x + math.cos(a + (0.5 if t % 2 else -0.4)) * 4.5
                ny = y + math.sin(a + (0.5 if t % 2 else -0.4)) * 4.5
                c.line(int(x), int(y), int(nx), int(ny), D_4, 3)
                c.line(int(x), int(y), int(nx), int(ny), glow, 1)
                x, y = nx, ny
        _disk(c, c0, c0, 3, D_4)
        _disk(c, c0, c0, 1.5, D_W)
        _rim(c, D_X)
        out.append(c)
    return out


def dark_mark_c(size=48, frames=8):
    """C: black tar dripping from the body, drops falling and splashing."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        for x in range(-10, 11):
            for dy in range(3):
                _p(c, c0 + x, c0 - 12 + abs(x) // 4 + dy, D_1 if dy == 0 else D_2)
        for k in range(3):
            life = ((f + k * 3) % frames) / frames
            x = c0 - 7 + k * 7
            y = c0 - 10 + life * 22
            _disk(c, x, y, 3.0 - life * 0.8, D_2)
            _disk(c, x - 1, y - 1, 1.0, D_1)
            if life > 0.8:
                for dx in (-3, 3):
                    _p(c, x + dx, y + 1, D_2)
        _rim(c, D_X)
        out.append(c)
    return out


# ---------- Dark: burst when a marked monster dies (96 px canvas) ----------

def dark_burst_a(size=96, frames=10):
    """A: a dark sphere pulls in, then bursts into curling tendrils."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        if u < 0.35:
            r = 16 - u / 0.35 * 8
            _disk(c, c0, c0, r, D_3)
            _disk(c, c0, c0, r * 0.6, D_4)
            _ring(c, c0, c0, r, D_1, 1.2)
        else:
            v = (u - 0.35) / 0.65
            for k in range(7):
                a0 = k * math.tau / 7
                for t in range(int(6 + v * 26)):
                    a = a0 + t * 0.06
                    d = t * 1.3
                    w = max(0.6, 2.8 - t * 0.09)
                    _disk(c, c0 + math.cos(a) * d, c0 + math.sin(a) * d, w, D_2 if t % 5 else D_1)
            if v < 0.3:
                _disk(c, c0, c0, 6, D_W)
        _rim(c, D_X)
        out.append(c)
    return out


def dark_burst_b(size=96, frames=10):
    """B: an implosion: a purple ring closes in, a black flash, then a thin ring snaps outward."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        if u < 0.5:
            r = 40 * (1 - u * 1.8)
            _ring(c, c0, c0, r, D_3, 7.0)
            _ring(c, c0, c0, r, D_2, 4.0)
            _ring(c, c0, c0, r, D_W, 1.2)
        elif u < 0.65:
            _disk(c, c0, c0, 10, D_X)
            _ring(c, c0, c0, 10, D_W, 1.2)
        else:
            r = 12 + (u - 0.65) / 0.35 * 32
            _ring(c, c0, c0, r, D_3, 5.0 * (1.2 - (u - 0.65) / 0.35))
            _ring(c, c0, c0, r, D_1, 2.0)
        _rim(c, D_X)
        out.append(c)
    return out


def dark_burst_c(size=96, frames=10):
    """C: shards of shadow fly out like broken glass, spinning, then fade."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        for k in range(9):
            a = k * math.tau / 9 + 0.3
            d = 6 + u * 34
            x, y = c0 + math.cos(a) * d, c0 + math.sin(a) * d
            sp = a + f * 0.7
            ln = 7 * (1 - u * 0.4)
            for t in range(-int(ln), int(ln) + 1):
                w = max(0, int((1 - abs(t) / (ln + 1)) * 2.2))
                for s in range(-w, w + 1):
                    _p(c, x + math.cos(sp) * t - math.sin(sp) * s, y + math.sin(sp) * t + math.cos(sp) * s,
                       D_1 if s == 0 else D_3)
        if u < 0.25:
            _disk(c, c0, c0, 9, D_4)
            _disk(c, c0, c0, 4, D_W)
        _rim(c, D_X)
        out.append(c)
    return out


# ---------- elite / boss-buff marks (bach-ai roadmap F, 2026-11-23), drawn white so the game tints them ----------
E_W = "#ffffff"
E_1 = "#e6e6ee"
E_2 = "#b4b4c4"
E_X = "#2a2a36"


def elite_crest(size=32, frames=8):
    """Option B: a small faceted gem crest floating over the head, bobbing, a glint crossing it."""
    out = []
    c0 = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        bob = round(math.sin(f / frames * math.tau) * 1.5)
        cy = c0 + bob
        for y in range(-8, 9):
            wd = 6 - abs(y) * 6 // 8
            for x in range(-wd, wd + 1):
                col = E_1 if x < 0 else E_2
                if y < -3:
                    col = E_W
                _p(c, c0 + x, cy + y, col)
        g = f % frames - 3
        for k in range(-2, 3):
            if 0 <= g <= 4:
                _p(c, c0 - 4 + g + k, cy - 2 - k, E_W)
        _rim(c, E_X)
        out.append(c)
    return out


def elite_wisps(size=64, frames=10):
    """Option C: tongues of energy rising round the body from the feet (Diablo IV-like champion aura), behind
    the monster; solid tongues that sway and grow in turn; drawn white, see-through in game."""
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        base = size - 6
        for k in range(6):
            x0 = size / 2 - 16 + k * 6.4
            grow = 0.55 + 0.45 * abs(math.sin(f / frames * math.pi * 2 + k * 1.3))
            h = (22 + (k % 3) * 6) * grow
            for t in range(int(h)):
                u = t / h
                x = x0 + math.sin(u * 4 + f * 0.8 + k) * 2.5 * u
                w = 3.2 * (1 - u) ** 0.6
                col = E_2 if u > 0.7 else (E_1 if u > 0.35 else E_W)
                for sx in range(-int(round(w)), int(round(w)) + 1):
                    _p(c, x + sx, base - t, col)
        out.append(c)
    return out
