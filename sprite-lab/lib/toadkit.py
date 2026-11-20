"""toadkit: a side-view toad drawn from parts (games/bach-ai/design/art/toads.md).

User 2026-11-18: the first toads were flat ovals with orange dots and no legs. A toad reads through its
folded hind thigh, propped front arm, browed eye with a horizontal pupil, the poison gland behind the eye,
a wide mouth line, and raised warts (lit top, dark underside).

  draw_toad(c, pose, s=1.0, ox=0, oy=0, pal=PAL, king=False)
pose: a dict of part placements in unit coordinates (scale 1 = the 32x24 Cóc Độc, floor at y=22):
  body: (cx, cy, rx, ry, angle_deg)   angle < 0 tips the head (right) up
  thigh: (cx, cy, rx, ry, angle_deg)  the near hind thigh
  shin: [(x, y), ...]                 knee -> heel -> toes (polyline, on or off the ground)
  arm: [(x, y), ...]                  shoulder -> elbow -> hand
  far: (dx, dy)                       offset of the far legs (drawn darker, behind)
  eyes: "open" | "shut"; puff: throat sac size (0..3)
POSES holds the named poses used by both sprites.
"""

from __future__ import annotations

import math

PAL = {
    "lit": "#8a8a3a", "back": "#5e6a2a", "side": "#38401c",
    "belly": "#d8c47a", "throat": "#efe2a8", "belly_d": "#b09a58",
    "wart_l": "#ffb04a", "wart": "#e0702a", "wart_d": "#8a3a1a",
    "eye": "#f0c040", "pupil": "#14160c", "brow": "#2a2a14",
    "gland": "#a0a048", "mouth": "#2a2a14",
}


def _ellipse_pts(cx, cy, rx, ry, ang, n=28):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for k in range(n):
        t = k * math.tau / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((round(cx + x * ca - y * sa), round(cy + x * sa + y * ca)))
    return out


def _on_body(body, u, v):
    """Point at body-local (u, v) in [-1, 1] (u along the body to the head, v down)."""
    cx, cy, rx, ry, ang = body
    a = math.radians(ang)
    x, y = u * rx, v * ry
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


def _sc(p, s, ox, oy):
    return (round(p[0] * s + ox), round(p[1] * s + oy))


def _limb(c, pts, w, col, s, ox, oy, rim=None):
    q = [_sc(p, s, ox, oy) for p in pts]
    if rim:   # a dark rim first: the limb reads apart from the body behind it
        for a, b in zip(q, q[1:]):
            c.line(a[0], a[1], b[0], b[1], rim, max(1, round(w * s)) + 2)
    for a, b in zip(q, q[1:]):
        c.line(a[0], a[1], b[0], b[1], col, max(1, round(w * s)))
    return q


def _wart(c, x, y, size, pal):
    """A raised wart: lit top-left, dark underside; round from size 3 up."""
    r = max(1, size)
    if r >= 3:
        c.ellipse(x, y + 1, x + r, y + r + 1, pal["wart_d"], fill=True)   # shadow under it
        c.ellipse(x, y, x + r, y + r, pal["wart"], fill=True)
        c.pixel(x + 1, y + 1, pal["wart_l"])
        if r >= 4:
            c.pixel(x + 2, y + 1, pal["wart_l"])
        return
    c.rect(x, y, x + r, y + r, pal["wart"], fill=True)
    c.pixel(x, y, pal["wart_l"])
    c.line(x, y + r, x + r, y + r, pal["wart_d"])


WARTS = [(-0.6, -0.8), (-0.1, -0.95), (-0.85, -0.25), (-0.3, -0.35)]
# (u, v, size multiplier): uneven warts on the king
KING_WARTS = [(-0.6, -0.75, 1.0), (-0.85, -0.2, 0.8), (-0.3, -0.35, 1.2), (-0.55, 0.15, 0.7), (0.05, -0.45, 0.6)]
MOTTLE = [(-0.7, -0.55), (-0.45, -0.1), (-0.15, -0.65), (0.05, -0.25), (-0.85, 0.05), (0.35, -0.2), (-0.35, 0.15)]


def draw_toad(c, pose, s=1.0, ox=0, oy=0, pal=PAL, king=False):
    body = pose["body"]
    fdx, fdy = pose.get("far", (2, -1))
    # far legs, darker, behind the body
    far_shin = [(x + fdx, y + fdy) for x, y in pose["shin"]]
    _limb(c, far_shin, 1.5, pal["side"], s, ox, oy)
    far_arm = [(x + fdx * 0.6, y + fdy) for x, y in pose["arm"]]
    _limb(c, far_arm, 1.5, pal["side"], s, ox, oy)
    # near hind leg: shin under the thigh, then the thigh over it
    sh = _limb(c, pose["shin"], 2, pal["lit"], s, ox, oy, rim=pal["side"])
    toe = sh[-1]
    c.line(toe[0], toe[1], toe[0] + round(2 * s), toe[1], pal["side"])   # long toes
    # body
    cx, cy, rx, ry, ang = body
    c.polygon(_ellipse_pts(cx * s + ox, cy * s + oy, rx * s, ry * s, ang), pal["back"])
    # belly: the lower front half
    belly = [_sc(_on_body(body, u, v), s, ox, oy) for u, v in ((-0.6, 0.55), (0.1, 0.95), (0.75, 0.7), (0.95, 0.15), (0.5, 0.3), (-0.2, 0.35))]
    c.polygon(belly, pal["belly"])
    # throat sac
    puff = pose.get("puff", 0)
    tx, ty = _sc(_on_body(body, 0.72, 0.45), s, ox, oy)
    tr = round((2 + puff) * s * 0.8)
    c.ellipse(tx - tr, ty - tr, tx + tr, ty + tr, pal["throat"], fill=True)
    # lit back band
    lit = [_sc(_on_body(body, u, v), s, ox, oy) for u, v in ((-0.85, -0.35), (-0.4, -0.9), (0.3, -0.92), (0.55, -0.6), (0.1, -0.6), (-0.5, -0.5))]
    c.polygon(lit, pal["lit"])
    # side shade under the back, belly shadow line
    for u in (-0.8, -0.5, -0.2):
        x, y = _sc(_on_body(body, u, 0.5), s, ox, oy)
        c.pixel(x, y, pal["belly_d"])
    # thigh (drumstick) on the flank
    tcx, tcy, trx, tr_y, tang = pose["thigh"]
    c.polygon(_ellipse_pts(tcx * s + ox, tcy * s + oy, trx * s + 1, tr_y * s + 1, tang), pal["side"])   # rim
    c.polygon(_ellipse_pts(tcx * s + ox, tcy * s + oy, trx * s, tr_y * s, tang), pal["back"])
    tl = _ellipse_pts(tcx * s + ox - s * 0.8, tcy * s + oy - s * 0.9, trx * s * 0.6, tr_y * s * 0.5, tang)
    c.polygon(tl, pal["lit"])
    # front arm, over the body
    am = _limb(c, pose["arm"], 2, pal["lit"], s, ox, oy, rim=pal["side"])
    hx, hy = am[-1]
    for d in (-1, 1, 2):   # three splayed fingers
        c.pixel(hx + round(d * s), hy, pal["side"])
    # poison gland behind the eye, then the eye with brow and horizontal pupil
    gx, gy = _sc(_on_body(body, 0.25, -0.75), s, ox, oy)
    gr = max(1, round(1.6 * s))
    c.ellipse(gx - gr - 1, gy - gr, gx + gr, gy + gr // 2 + 1, pal["gland"], fill=True)
    ex, ey = _sc(_on_body(body, 0.6, -1.0), s, ox, oy)   # bulges above the head line
    er = max(2, round(2.2 * s))
    c.ellipse(ex - er, ey - er, ex + er, ey + er, pal["back"], fill=True)
    if pose.get("eyes", "open") == "open" and GRIM:   # burning eye, a red pinprick pupil
        c.ellipse(ex - er + 1, ey - er + 1, ex + er - 1, ey + er - 1, "#ffd040", fill=True)
        c.ellipse(ex - er + 2, ey - er + 2, ex + er - 2, ey + er - 2, "#fff4a0", fill=True)
        c.rect(ex, ey, ex + 1, ey, "#e01810", fill=True)
    elif pose.get("eyes", "open") == "open":
        c.ellipse(ex - er + 1, ey - er + 1, ex + er - 1, ey + er - 1, pal["eye"], fill=True)
        c.line(ex - er + 1, ey, ex + er - 1, ey, pal["pupil"])          # horizontal pupil
        c.pixel(ex - er + 2, ey - er + 1, "#fff6c8")                     # glint
    else:
        c.line(ex - er + 1, ey, ex + er - 1, ey, pal["pupil"])
    c.line(ex - er, ey - er, ex + er - 1, ey - er - 1, pal["brow"])     # brow ridge
    if GRIM:   # a heavy brow slanting down to the snout: a scowl
        c.line(ex - er - 1, ey - er - 2, ex + er, ey - er + 1, pal["brow"])
        c.line(ex - er, ey - er - 1, ex + er, ey - er + 2, pal["brow"])
    # wide mouth from the snout back under the eye; "mouth" > 0 opens it (spitting)
    m0 = _sc(_on_body(body, 0.98, 0.05), s, ox, oy)
    m1 = _sc(_on_body(body, 0.45, 0.15), s, ox, oy)
    mo = pose.get("mouth", 0)
    if GRIM:
        mo = max(mo, 0.3)   # the jaw always hangs open
    if mo > 0.2:
        m2 = _sc(_on_body(body, 0.95, 0.05 + 0.5 * mo), s, ox, oy)
        c.polygon([m1, m0, m2], "#5a1a20")
        c.line(m1[0], m1[1], m2[0], m2[1], "#c85060")      # tongue / pink inside
        if mo > 0.7 and not NO_GLOB:   # poison glob leaving the mouth (Cóc Độc Bào Tử shoots its tongue instead)
            gx, gy = m0[0] + round(2 * s), (m0[1] + m2[1]) // 2
            c.ellipse(gx, gy - round(s), gx + round(2 * s), gy + round(s), "#8ad040", fill=True)
            c.pixel(gx + 1, gy - 1, "#c8ff7a")
    else:
        c.line(m0[0], m0[1], m1[0], m1[1], pal["mouth"])
    # raised poison warts along the spine
    if king:
        for u, v in MOTTLE:   # darker mottling so the back is not flat
            x, y = _sc(_on_body(body, u, v), s, ox, oy)
            c.rect(x, y, x + 1, y, pal["side"], fill=True)
        for u, v, m in KING_WARTS:
            x, y = _sc(_on_body(body, u, v), s, ox, oy)
            _wart(c, x, y, max(2, round(1.6 * s * m)), pal)
        _crown(c, body, s, ox, oy, pose)
        if GRIM:
            for path in (((-0.7, -0.55), (-0.4, -0.7), (-0.1, -0.6), (0.15, -0.75)), ((-0.6, -0.2), (-0.3, -0.35), (0.0, -0.25)),
                         ((-0.85, 0.05), (-0.6, -0.05), (-0.45, 0.15))):   # glowing purple veins over the back
                pts = [_sc(_on_body(body, u, v), s, ox, oy) for u, v in path]
                for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                    c.line(ax, ay, bx, by, VEIN)
                c.pixel(pts[1][0], pts[1][1], VEIN_L)
            for n, (u, v) in enumerate(((-0.5, 0.1), (-0.15, 0.2), (0.2, 0.1))):   # warts ooze purple down the flank
                x, y = _sc(_on_body(body, u, v), s, ox, oy)
                drip = 1 + (SPORE_PHASE + n) % 3
                c.line(x, y + 1, x, y + drip, OOZE)
                c.pixel(x, y + drip + 1, VEIN_L)
            mx, my = _sc(_on_body(body, 0.9, 0.2), s, ox, oy)   # poison drool strings from the hanging jaw
            for k, dx in enumerate((0, -2)):
                ln = 2 + (SPORE_PHASE + k) % 4
                c.line(mx + dx, my, mx + dx, my + ln, OOZE)
                c.pixel(mx + dx, my + ln + 1, VEIN_L)
        if pose.get("drool"):   # poison drips from the mouth corner while it winds up
            dx, dy = _sc(_on_body(body, 0.9, 0.2), s, ox, oy)
            c.line(dx, dy, dx, dy + round(3 * s), OOZE if GRIM else "#8ad040")
            c.pixel(dx, dy + round(3 * s) + 1, VEIN_L if GRIM else "#c8ff7a")
    else:
        for u, v in WARTS:
            x, y = _sc(_on_body(body, u, v), s, ox, oy)
            _wart(c, x, y, max(2, round(1.6 * s)), pal)


CAP, CAP_L, CAP_D, STEM = "#7a3aa8", "#b070e0", "#4a2070", "#e0d8c0"
# Cóc Độc Bào Tử (Cóc Chúa phase 2, bach-ai design/bosses.md): the crown swells (CROWN_GROW) and glows,
# puffing spores (CROWN_GLOW; SPORE_PHASE moves the puffs frame to frame). Defaults leave Cóc Chúa as it was.
CROWN_GROW = 1.0
CROWN_GLOW = False
SPORE_PHASE = 0
NO_GLOB = False
# Cóc Độc Bào Tử looks ferocious and ghastly (user 2026-11-20): GRIM gives burning eyes with a red pinprick
# pupil under a heavy scowling brow, a mouth hanging open and drooling purple poison, glowing purple veins
# over the back and warts oozing purple. Refs: Dragon Quest toxic toad (oozes poison from every pore), Dark
# Souls basilisk (bulging eyes, beady pinprick pupils).
GRIM = False
VEIN, VEIN_L, OOZE = "#7a2aa8", "#d070ff", "#b050e8"
GLOW, GLOW_L = "#c060ff", "#f0c8ff"


def _crown(c, body, s, ox, oy, pose):
    """A crown of toxic mushrooms on the head behind the eye (Cóc Chúa)."""
    for u, h, r in ((-0.05, 3.0, 2.2), (-0.32, 2.2, 1.7), (0.18, 1.6, 1.3)):   # behind the eye
        bx, by = _sc(_on_body(body, u, -0.98), s, ox, oy)
        hh = round(h * s * CROWN_GROW)
        rr = round(r * s * CROWN_GROW)
        c.line(bx, by, bx, by - hh, STEM, max(1, round(0.8 * s)))
        c.ellipse(bx - rr, by - hh - rr, bx + rr, by - hh + rr // 2, CAP_D, fill=True)
        c.ellipse(bx - rr, by - hh - rr, bx + rr, by - hh, GLOW if CROWN_GLOW else CAP, fill=True)
        c.pixel(bx - rr // 2, by - hh - rr + 1, GLOW_L if CROWN_GLOW else CAP_L)
        c.pixel(bx + rr // 2, by - hh - rr // 2, GLOW_L if CROWN_GLOW else CAP_L)
        if CROWN_GLOW:   # spots on the swollen cap and spore puffs rising off it
            c.pixel(bx, by - hh - rr // 2, CAP_L)
            for k in range(3):
                t = (SPORE_PHASE + k * 3) % 8
                c.pixel(bx - rr + (k * 5 + SPORE_PHASE) % (2 * rr + 1), by - hh - rr - 1 - t, GLOW_L if t < 5 else GLOW)


def lerp_pose(a, b, t):
    """In-between of poses a and b (t 0..1): numbers, tuples and point lists blend; other keys come
    from the nearer pose. Gives the extra frames a smooth motion needs (creature-v1)."""
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k, b.get(k)), b.get(k, a.get(k))
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            out[k] = va + (vb - va) * t
        elif isinstance(va, tuple) and isinstance(vb, tuple) and len(va) == len(vb):
            out[k] = tuple(x + (y - x) * t for x, y in zip(va, vb))
        elif isinstance(va, list) and isinstance(vb, list) and len(va) == len(vb):
            out[k] = [tuple(x + (y - x) * t for x, y in zip(p, q)) for p, q in zip(va, vb)]
        else:
            out[k] = va if t < 0.5 else vb
    return out


# Poses at scale 1 (32x24 frame, floor y = 22). Toes and hands on y = 22 when grounded.
SIT = {"body": (16, 15.5, 9.5, 5.6, -8), "thigh": (8, 18.5, 4.5, 3.2, 25),
       "shin": [(7, 20), (10, 22), (13, 22)], "arm": [(20, 18), (22, 20), (23, 22)], "far": (2, -1)}
POSES = {
    "sit": SIT,
    "sit_puff": {**SIT, "puff": 2},
    "sit_low": {**SIT, "body": (15, 16, 10, 5.6, -6), "puff": 1},
    "crouch": {"body": (15, 17, 11, 5, -4), "thigh": (9, 18.5, 5, 3, 15),
               "shin": [(7, 21), (11, 22), (14, 22)], "arm": [(21, 19), (24, 21), (24, 22)], "far": (2, -1)},
    "crouch_deep": {"body": (15, 17.8, 11.5, 4.5, -2), "thigh": (8.5, 19, 5, 2.8, 10),
                    "shin": [(6, 21), (11, 22), (14, 22)], "arm": [(21, 19.5), (24, 21), (25, 22)], "far": (2, -1)},
    "takeoff": {"body": (16, 13, 10, 5.5, -30), "thigh": (10, 16, 4.5, 3, 50),
                "shin": [(8, 19), (5, 21), (2, 22)], "arm": [(21, 12), (24, 14), (26, 15)], "far": (2, -1)},
    "apex": {"body": (16, 12, 11, 5, -6), "thigh": (8, 13.5, 4.5, 2.8, 10),
             "shin": [(5, 14), (2, 16), (0, 17)], "arm": [(22, 13), (26, 13), (29, 12)], "far": (1, -1)},
    "fall": {"body": (16, 12, 10.5, 5.5, 15), "thigh": (9, 13, 4.5, 3, 35),
             "shin": [(8, 16), (11, 18), (14, 18)], "arm": [(22, 16), (24, 19), (25, 21)], "far": (2, -1)},
    "land": {"body": (16, 17.5, 12, 4.5, 0), "thigh": (9, 19, 5, 3, 10),
             "shin": [(7, 21), (11, 22), (15, 22)], "arm": [(22, 19.5), (25, 21), (27, 22)], "far": (2, -1)},
    "flat": {"body": (16, 19, 12, 3.5, 0), "thigh": (8, 20, 5, 2.2, 5),
             "shin": [(5, 21), (9, 22), (13, 22)], "arm": [(22, 20.5), (26, 22), (28, 22)], "far": (2, 0), "eyes": "shut"},
}
