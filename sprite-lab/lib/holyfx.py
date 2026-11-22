"""Cột thánh quang (holy-column) redrawn (bach-ai design/holy-column-redesign.md, user 2026-11-21: "ugly, weak").

The old column was a soft wobbly white tube wrapped in a dithered speck cloud (the same mistake as the old
burn). Here, at double density (px_scale 0.5), 12 frames:
  0-2  lead-in: a holy sigil (flat ring, 4 cross ticks, inner ring) draws itself on the ground, a thin guide
       ray reaches down from the sky;
  3    the beam slams down: full-width flash, ground burst;
  4-6  the beam holds: straight edges, white core, gold bands, a pale rim, light streaks running down it;
       ground rays and a widening burst ring;
  7-11 outro: the beam narrows to a line and lifts away, the sigil fades, 4-point sparkles rise.
Masks (hit area): the sigil's flat disc on the ground, frames 3..6. No veil, no speck cloud (pixel-sprite rule).
Tiers: II wider beam, III a second inner sigil ring, IV gold flecks in the beam, V a crown of rays at the top.
"""
import math

from spritekit import Canvas
from fxkit import FxFrames

WHITE = (255, 255, 250)
CORE = (255, 246, 196)
GOLD = (255, 214, 92)
AMBER = (232, 160, 48)
RIM = (255, 236, 170)
SIGIL = (255, 226, 120)
SIGIL_D = (196, 132, 36)
OUTLINE = (92, 52, 14)

MS = [80, 70, 60, 40, 50, 55, 65, 80, 95, 110, 125, 140]


def _put(c, x, y, col, a=255):
    x, y = int(round(x)), int(round(y))
    w, h = c.img.size
    if 0 <= x < w and 0 <= y < h:
        old = c.img.getpixel((x, y))
        if old[3] < a:
            c.img.putpixel((x, y), (col[0], col[1], col[2], a))


def _ring(c, cx, cy, r, squash, col, a=255, frac=1.0, rot=0.0, width=1):
    steps = max(24, int(r * 6))
    for i in range(int(steps * frac)):
        t = rot + i / steps * math.tau
        for w in range(width):
            _put(c, cx + math.cos(t) * (r - w), cy + math.sin(t) * (r - w) * squash, col, a)


def _sigil(c, cx, cy, r, tier, draw, a=255, rot=0.0):
    """Holy sigil flat on the ground; draw 0..1 = how much of it is drawn (lead-in)."""
    _ring(c, cx, cy, r, 0.42, SIGIL, a, frac=draw, rot=rot, width=2)
    _ring(c, cx, cy, r - 3, 0.42, SIGIL_D, a, frac=draw, rot=rot)
    if tier >= 3:
        _ring(c, cx, cy, r * 0.62, 0.42, SIGIL, a, frac=draw, rot=-rot)
    if draw > 0.5:   # four cross ticks at the quarters
        for q in range(4):
            t = rot + q * math.pi / 2
            x, y = cx + math.cos(t) * r, cy + math.sin(t) * r * 0.42
            for d in range(-3, 4):
                _put(c, x + d, y, WHITE, a)
                _put(c, x, y + d * 0.5, WHITE, a)


def _beam(c, cx, top, bottom, half, tier, k, a=255):
    """Straight-edged beam: white core, gold bands, pale rim; streaks run down it frame to frame."""
    core = max(1.0, half * 0.38)
    for y in range(int(top), int(bottom)):
        for x in range(int(cx - half), int(cx + half) + 1):
            d = abs(x - cx)
            if d <= core:
                col = WHITE if a >= 230 else CORE   # the outro beam stays warm, not grey
            elif d <= half * 0.66:
                col = CORE
            elif d <= half - 1.5:
                col = GOLD
            else:
                col = RIM
            if col in (CORE, GOLD) and (y + k * 9 + int(d) * 3) % 23 < 2:   # streaks running down
                col = WHITE
            if tier >= 4 and col == GOLD and (x * 7 + y * 3 + k * 5) % 41 == 0:
                col = WHITE
            _put(c, x, y, col, a)
        _put(c, cx - half - 1, y, AMBER, a // 2)
        _put(c, cx + half + 1, y, AMBER, a // 2)


def _rays(c, cx, cy, r0, r1, n, rot, a=255):
    for i in range(n):
        t = rot + i * math.tau / n
        for s in range(int(r0), int(r1)):
            _put(c, cx + math.cos(t) * s, cy + math.sin(t) * s * 0.42, GOLD if s < (r0 + r1) / 2 else AMBER, a)


def _sparkle(c, x, y, r, a=255):
    for d in range(-r, r + 1):
        col = WHITE if abs(d) < 2 else CORE
        _put(c, x + d, y, col, a)
        _put(c, x, y + d, col, a)


def holy_column(tier, w, h, ground, radius, seed=41):
    cx = w / 2
    half = 14 + tier * 1.5 + (3 if tier >= 2 else 0)
    out, masks = [], []
    for f in range(12):
        c = Canvas(w, h)
        rot = f * 0.18
        if f < 3:                                                    # lead-in: sigil draws in, guide ray
            _sigil(c, cx, ground, radius, tier, (f + 1) / 3, rot=rot)
            for y in range(0, int(ground - radius * 0.4), 2):
                _put(c, cx, y, CORE, 120 + f * 40)
        elif f < 7:                                                  # strike and hold
            k = f - 3
            wid = half * (1.35 if k == 0 else 1.0 - 0.04 * k)
            _sigil(c, cx, ground, radius, tier, 1.0, rot=rot)
            _rays(c, cx, ground, radius * 0.5, radius * (1.3 + 0.15 * k), 10 + tier * 2, rot, 230)
            _ring(c, cx, ground, radius * (0.9 + 0.25 * k), 0.42, WHITE if k < 2 else CORE, 255 - k * 40, width=2)
            _beam(c, cx, 0, ground, wid, tier, f)
            for yy in range(int(ground - wid * 0.5), int(ground + wid * 0.5) + 1):   # bright splash at the foot
                for xx in range(int(cx - wid * 1.5), int(cx + wid * 1.5) + 1):
                    e = ((xx - cx) / (wid * 1.5)) ** 2 + ((yy - ground) / (wid * 0.5)) ** 2
                    if e <= 1.0:
                        _put(c, xx, yy, WHITE if e < 0.35 else (CORE if e < 0.7 else GOLD))
            if tier >= 5:                                            # a crown of rays at the top
                for i in range(7):
                    t = math.pi * (0.15 + 0.7 * i / 6)
                    for s in range(6, 18):
                        _put(c, cx + math.cos(t) * s * 1.6, 10 - math.sin(t) * s * 0.5 + s * 0.2, GOLD)
            for i in range(2 + tier):                               # sparkles at the foot
                a = (i * 2.1 + f) % math.tau
                _sparkle(c, cx + math.cos(a) * radius * 0.8, ground + math.sin(a) * radius * 0.35, 2 + (i + f) % 2)
        else:                                                        # outro: the beam narrows and lifts
            k = f - 7
            wid = max(1.0, half * (0.7 - 0.14 * k))
            lift = k * (ground / 6)
            fade = int(255 * (1 - k / 6))
            _sigil(c, cx, ground, radius, tier, 1.0, a=fade, rot=rot)
            if wid > 1:   # gold as it lifts away (white faded to grey on the dark floor)
                _beam(c, cx, 0, max(0, ground - lift), wid, min(tier, 3), f, fade)
            for i in range(3 + tier):                               # sparkles rising
                x = cx + ((i * 37) % int(radius * 2) - radius) * 0.9
                y = ground - 12 - k * 14 - (i * 23) % 40
                _sparkle(c, x, y, 2 + (i % 2), fade)
        out.append(c.outline(OUTLINE) if 3 <= f < 7 else c)
        m = Canvas(w, h)
        if 3 <= f < 7:
            m.ellipse(int(cx - radius), int(ground - radius * 0.42), int(cx + radius), int(ground + radius * 0.42), "#ffffff", fill=True)
        masks.append(m)
    return FxFrames(out, masks)
