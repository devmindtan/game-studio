"""roguefx: burst effects for the Cung thủ and Sát thủ skills that need their own picture (2026-11-26):
arrow_rain, thorn_trap, hawk_dive (archer); smoke_bomb, blade_ring, shadow_strike (assassin).

Each returns 12 Canvas frames of S x S at double density (px_scale 0.5), centre = where it hits. Flat colours,
1 px dark outline where the shape is solid, phases: wind-up, hit, linger, fade.
"""
from __future__ import annotations

import math

from spritekit import Canvas

OUT = "#14111c"
WOOD = ("#5a3618", "#8a5a2a")
STEEL = ("#6a7590", "#b8c4d8", "#f4f8ff")
FEATHER = ("#d8e8f0", "#ffffff")
EARTH = ("#3e2414", "#6a4020", "#a8703a")
THORN = ("#1e4a1e", "#2a6a28", "#5ab83a", "#c8f07a")
HAWK = ("#3a2414", "#6a4020", "#a8703a", "#f2c14e")
SMOKE = ("#3a3448", "#5a5468", "#8a8498", "#c8c2d0")
VOID = ("#14081e", "#3a1660", "#7a3ab8", "#e0b8ff")
N = 12


def _arrow_down(c, x, y, length=14):
    """An arrow falling down-right with its head at (x, y)."""
    c.line(x - length, y - length * 2, x, y, WOOD[1], 2)
    c.polygon([(x + 1, y + 3), (x - 3, y - 1), (x + 2, y - 2)], STEEL[1])
    c.pixel(x - length, y - length * 2, FEATHER[1])
    c.pixel(x - length + 1, y - length * 2, FEATHER[0])


def arrow_rain(S, R):
    """Mưa tên: a volley falls on a circle of radius R, stabs the ground and fades."""
    C = S // 2
    spots = [(math.cos(k * 2.399) * R * math.sqrt((k + 0.5) / 9), math.sin(k * 2.399) * R * 0.6 * math.sqrt((k + 0.5) / 9))
             for k in range(9)]
    out = []
    for f in range(N):
        c = Canvas(S, S)
        if f >= 3:   # the target circle on the ground
            c.ellipse(C - R, C - int(R * 0.6), C + R, C + int(R * 0.6), EARTH[1] if f < 9 else EARTH[0], fill=False)
        for k, (dx, dy) in enumerate(spots):
            land = 3 + k % 4                    # frame it lands
            x, y = int(C + dx), int(C + dy)
            if f < land:
                fall = (land - f) * 10
                if fall < S:
                    _arrow_down(c, x - fall // 2, y - fall)
            elif f < 10:                        # stuck in the ground: a short shaft
                c.line(x - 4, y - 8, x, y, WOOD[1], 2)
                c.pixel(x - 4, y - 8, FEATHER[1])
                if f == land:
                    c.ellipse(x - 4, y - 2, x + 4, y + 2, EARTH[2], fill=False)
        c.outline(OUT)
        out.append(c)
    return out


def thorn_trap(S, R):
    """Bẫy gai: cracks open in a ring, green thorns burst up, hold, then sink."""
    C = S // 2
    out = []
    heights = [0, 0, 0, 4, 10, 16, 18, 16, 14, 10, 5, 0]
    for f in range(N):
        c = Canvas(S, S)
        c.ellipse(C - R, C - R // 2, C + R, C + R // 2, EARTH[0] if f < 11 else EARTH[1], fill=f >= 1)
        if f >= 1:
            c.ellipse(C - R + 3, C - R // 2 + 2, C + R - 3, C + R // 2 - 2, EARTH[1])
        h = heights[f]
        for k in range(9):
            a = k * 0.7
            x = int(C + math.cos(a) * R * 0.75 * ((k % 3) + 1) / 3)
            y = int(C + math.sin(a) * R * 0.35 * ((k % 3) + 1) / 3)
            if h:
                hh = h - (k % 3) * 2
                c.polygon([(x - 3, y), (x + 3, y), (x, y - hh)], THORN[1])
                c.line(x, y - 1, x, y - hh + 1, THORN[2], 1)
                c.pixel(x, y - hh, THORN[3])
        c.outline(OUT)
        out.append(c)
    return out


def _hawk(c, x, y, wing):
    """A hawk seen from above-side, diving down-right, centre (x, y); wing 0..2 = wing beat."""
    span = (10, 7, 4)[wing]
    c.polygon([(x - 6, y - 3), (x + 6, y + 3), (x + 2, y + 5), (x - 7, y)], HAWK[1])            # body
    c.polygon([(x - 2, y), (x - 2 - span, y - span), (x + 3, y - 2)], HAWK[0])                 # far wing
    c.polygon([(x - 1, y + 1), (x - span, y + span + 2), (x + 4, y + 3)], HAWK[2])             # near wing
    c.polygon([(x + 6, y + 3), (x + 9, y + 5), (x + 5, y + 6)], HAWK[3])                       # beak
    c.pixel(x + 4, y + 2, OUT)


def hawk_dive(S, R):
    """Chim ưng: a hawk dives from the upper left onto the target, talons hit, feathers scatter."""
    C = S // 2
    out = []
    for f in range(N):
        c = Canvas(S, S)
        if f < 4:   # a fast dive: the talons hit on frame 4 (gameplay rule snappy: first hit before 0.4 s)
            t = f / 3.0
            x = int(C - (1 - t) * S * 0.42)
            y = int(C - (1 - t) * S * 0.42)
            for k in range(1, 3):   # speed streaks behind
                c.line(x - 8 - k * 6, y - 8 - k * 6, x - 4 - k * 6, y - 4 - k * 6, FEATHER[0], 1)
            _hawk(c, x, y, f % 3)
        else:
            g = f - 4
            for k in range(8):   # talon slash marks then feathers flying out
                a = k * math.tau / 8
                r = R * 0.3 + g * 4
                fx, fy = int(C + math.cos(a) * r), int(C + math.sin(a) * r * 0.7)
                if g < 4:
                    c.line(fx, fy, fx + 2, fy - 3, FEATHER[1] if k % 2 else HAWK[2], 2)
            if g < 2:
                for d in (-5, 0, 5):
                    c.line(C - 6 + d, C - 6, C + 6 + d, C + 6, STEEL[2], 1)
            if g < 5:   # it flies back up and away
                _hawk(c, C + g * 6, C - g * 8, g % 3)
        c.outline(OUT)
        out.append(c)
    return out


def smoke_bomb(S, R):
    """Bom khói: a small bomb bursts into grey puffs that roll out to R, hang and thin away."""
    C = S // 2
    out = []
    for f in range(N):
        c = Canvas(S, S)
        if f == 0:
            c.ellipse(C - 5, C - 5, C + 5, C + 5, SMOKE[0])
            c.line(C + 3, C - 5, C + 6, C - 9, EARTH[2], 1)
            c.pixel(C + 6, C - 10, "#fff27a")
        else:
            grow = min(1.0, f / 5.0)
            for k in range(10):
                a = k * math.tau / 10 + f * 0.05
                r = R * 0.7 * grow * (0.5 + (k % 3) * 0.25)
                x, y = int(C + math.cos(a) * r), int(C + math.sin(a) * r * 0.75)
                pr = int(6 + 8 * grow) - max(0, f - 8) * 3
                if pr <= 1:
                    continue
                shade = SMOKE[1 + (k % 3)] if f < 9 else SMOKE[k % 2]
                c.ellipse(x - pr, y - pr, x + pr, y + pr, shade)
            if f < 9:
                c.ellipse(C - 7, C - 6, C + 7, C + 6, SMOKE[3])
        c.outline(OUT)
        out.append(c)
    return out


def _dagger(c, x, y, ang, L=12):
    """A dagger centred at (x, y) pointing at angle ang (radians)."""
    dx, dy = math.cos(ang), math.sin(ang)
    tx, ty = int(x + dx * L / 2), int(y + dy * L / 2)
    hx, hy = int(x - dx * L / 2), int(y - dy * L / 2)
    mx, my = int(x - dx * L / 6), int(y - dy * L / 6)
    c.line(mx, my, tx, ty, STEEL[1], 2)
    c.line(mx, my, tx, ty, STEEL[2], 1)
    c.line(hx, hy, mx, my, EARTH[0], 2)
    c.line(int(mx - dy * 3), int(my + dx * 3), int(mx + dy * 3), int(my - dx * 3), HAWK[3], 1)


def blade_ring(S, R):
    """Vòng dao: six daggers spin out around the hero to radius R, sweep a full turn and fly off."""
    C = S // 2
    out = []
    for f in range(N):
        c = Canvas(S, S)
        r = R * min(1.0, 0.35 + f * 0.13) if f < 10 else R + (f - 9) * 8
        turn = f * 0.55
        if 2 <= f <= 9:
            c.ellipse(C - int(r), C - int(r * 0.8), C + int(r), C + int(r * 0.8), VOID[2], fill=False)
        for k in range(6):
            a = turn + k * math.tau / 6
            x, y = C + math.cos(a) * r, C + math.sin(a) * r * 0.8
            _dagger(c, x, y, a + math.pi / 2)
        c.outline(OUT)
        out.append(c)
    return out


def shadow_strike(S, R):
    """Ám kích: a violet shadow flickers in, two crossing slashes cut, the cut glows and fades."""
    C = S // 2
    out = []
    for f in range(N):
        c = Canvas(S, S)
        if f < 2:   # the shadow gathering
            rr = 4 + f * 4
            c.ellipse(C - rr, C - rr, C + rr, C + rr, VOID[1])
        if 2 <= f <= 7:
            g = min(1.0, (f - 1) / 2.0)
            L = int(R * g)
            col = VOID[3] if f < 5 else VOID[2]
            c.line(C - L, C - L, C + L, C + L, VOID[2], 4)
            c.line(C - L, C - L, C + L, C + L, col, 2)
            if f >= 3:
                c.line(C - L, C + L, C + L, C - L, VOID[2], 4)
                c.line(C - L, C + L, C + L, C - L, col, 2)
        if 5 <= f <= 10:
            for k in range(6):
                a = k * math.tau / 6 + 0.4
                d = R * 0.4 + (f - 5) * 4
                c.pixel(int(C + math.cos(a) * d), int(C + math.sin(a) * d), VOID[3] if f < 9 else VOID[2])
        c.outline(OUT)
        out.append(c)
    return out
