"""drawnicons: item icons drawn properly where the user's piece is too small to read as an icon (user 2026-11-25:
"vẽ icon bao tên đàng hoàng; tay, chân quá nhỏ thì cứ vẽ bình thường, khi mặc vào chỉ cần có chút màu giống").
24 x 24, the user's style: a 1 px dark outline, 3-4 flat shades per material, no anti-alias. Each takes a tier
palette with metal/cloth ramp d, m, l, h and an accent / trim (t) so the icon matches the colours worn.

    quiver(pal)  boots(pal)  gloves(pal)  -> PIL RGBA image 24 x 24
"""

from __future__ import annotations

from spritekit import Canvas

S = 24
OUTLINE = "#08080c"
FEATHER = "#f4f4f4"
FEATHER_D = "#bdbdbd"
SHAFT = "#8a5a2e"


def _done(c):
    c.outline(OUTLINE)
    return c.img


def quiver(pal):
    """A leather quiver leaning right, a strap band, three arrows spread out of it with white fletching."""
    c = Canvas(S, S)
    for (x0, y0, x1, y1) in ((8, 11, 4, 3), (11, 10, 11, 1), (14, 9, 19, 2)):   # shafts, fanned out
        c.line(x0, y0, x1, y1, SHAFT)
    for (fx, fy) in ((4, 3), (11, 1), (19, 2)):                                   # fletching: a small V each
        c.pixel(fx - 1, fy, FEATHER)
        c.pixel(fx + 1, fy, FEATHER)
        c.pixel(fx - 1, fy + 1, FEATHER_D)
        c.pixel(fx + 1, fy + 1, FEATHER_D)
        c.pixel(fx, fy - 1, FEATHER)
    c.polygon([(6, 11), (16, 8), (19, 21), (9, 23)], pal["m"])          # the tube
    c.polygon([(6, 11), (9, 10), (12, 22), (9, 23)], pal["d"])          # its shaded side
    c.line(15, 9, 18, 20, pal["l"])                                     # light edge
    c.polygon([(5, 10), (16, 7), (17, 9), (6, 12)], pal["h"])           # the rim
    c.line(7, 16, 18, 13, pal.get("t", pal["h"]), 2)                    # the strap band
    return _done(c)


def boots(pal):
    """A pair of tall boots, the near one in front: shaft, cuff band, toe."""
    c = Canvas(S, S)
    for dx, dy, shade in ((5, -1, "d"), (0, 1, "m")):
        x, y = 4 + dx, 4 + dy
        c.rect(x, y + 2, x + 6, y + 13, pal[shade])                     # shaft
        c.polygon([(x, y + 13), (x + 6, y + 13), (x + 12, y + 16), (x + 12, y + 18), (x, y + 18)], pal[shade])
        c.rect(x, y + 1, x + 6, y + 3, pal["h"] if shade == "m" else pal["l"])   # cuff band
        c.line(x + 1, y + 5, x + 1, y + 12, pal["l"])                   # light edge
        c.rect(x, y + 17, x + 12, y + 18, pal.get("t", pal["d"]))       # sole
    return _done(c)


def gloves(pal):
    """A glove seen from the back: four separate fingers, the thumb out to the side, a flared cuff."""
    c = Canvas(S, S)
    c.polygon([(6, 16), (16, 16), (18, 22), (4, 22)], pal["d"])         # flared cuff
    c.line(5, 17, 17, 17, pal.get("t", pal["h"]))                       # cuff trim
    c.rect(6, 9, 15, 16, pal["m"])                                      # back of the hand
    for k in range(4):                                                  # four fingers, a dark gap between them
        x = 6 + k * 3 - (1 if k == 3 else 0)
        top = (5, 3, 4, 6)[k]
        c.rect(x, top, x + 1, 9, pal["l"] if k < 3 else pal["m"])
    c.polygon([(15, 10), (19, 8), (20, 10), (16, 14)], pal["m"])        # thumb
    c.line(7, 10, 7, 15, pal["h"])                                      # light edge
    return _done(c)
