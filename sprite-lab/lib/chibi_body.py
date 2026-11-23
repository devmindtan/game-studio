"""chibi_body: the standard 64x64 chibi skeleton (sprite-lab/BODY_PLAN.md, user 2026-11-23).

Every layer (body, head, hair, clothes, weapon) is drawn on the SAME joints per frame, so layers stack and fit like LPC
sheets. Motion learned from LPC's walk (frame 0 stand, 1-8 a cycle: legs widest at 2 and 6, body down 1 px on contact,
up on passing, arms opposite the legs), drawn by us; no LPC pixels are used. Faces right; the game flips for left.

Example:
    from chibi_body import skeleton, PROPORTIONS, draw_bare
    j = skeleton("walk", 3, PROPORTIONS["B"])     # joints of walk frame 3
    canvas = draw_bare(j, PROPORTIONS["B"], SKIN)
"""

from __future__ import annotations

import math

from spritekit import Canvas
from icefx import _p

S = 64
GROUND = 58            # feet line (anchor y); room above for big weapons
ROOT_X = 32

# Proportion options for the user to choose (pixel-sprite step 0: distinct, not just colour).
PROPORTIONS = {
    "A": {"name": "Đầu rất to (2 đầu cao)", "head_r": 11, "torso_h": 9, "torso_w": 10, "leg_h": 7, "arm_l": 7},
    "B": {"name": "Cân đối chibi (2,3 đầu)", "head_r": 9, "torso_h": 10, "torso_w": 10, "leg_h": 9, "arm_l": 8},
    "C": {"name": "Chibi cao (2,6 đầu)", "head_r": 8, "torso_h": 12, "torso_w": 9, "leg_h": 11, "arm_l": 10},
}

ANIMS = {"idle": 2, "walk": 9, "hurt": 3, "death": 6, "dash": 4, "shoot": 13}
STANDARD = "B"         # user 2026-11-23 chose B (chibi, 2.3 heads tall)

# walk: per frame (front foot dx, back foot dx, front lift, back lift, body bob)
_WALK = [(0, 0, 0, 0, 0),
         (2, -2, 0, 1, 0), (4, -3, 0, 0, 1), (2, -1, 0, 2, 0), (0, 0, 1, 0, -1),
         (-1, 2, 1, 0, 0), (-3, 4, 0, 0, 1), (-1, 2, 2, 0, 0), (0, 0, 0, 1, -1)]

# shoot (13, LPC's rhythm): 0 stand; 1-3 the bow arm rises level; 4 the back hand nocks at the bow; 5-8 draw to the
# cheek and hold; 9 release (back hand flies back); 10-12 lower. Hands relative to the shoulder (front, back).
_SHOOT = [((1, 8), (-1, 8)), ((4, 7), (-1, 8)), ((7, 5), (0, 7)), ((10, 3), (2, 5)), ((11, 3), (8, 3)),
          ((11, 3), (5, 3)), ((11, 3), (2, 2)), ((11, 3), (1, 2)), ((11, 3), (1, 2)), ((11, 3), (-4, 1)),
          ((10, 3), (-2, 4)), ((6, 5), (-1, 6)), ((2, 7), (-1, 8))]
# chibi: the big head covers the shoulders, so the drawn bow arm is held at chest height (y +3), reaching far forward


# hurt (3): flinch back, hold, recover. (lean x of the upper body, bob)
_HURT = [(-2, 1), (-2, 1), (-1, 0)]
# death (6, LPC's fall: knees give, sink, then lie): hip drop px; frames 4-5 lie (drawn upright, turned 90 deg)
_DEATH_DROP = [1, 3, 5, 6, 6, 6]
# dash (4): crouch, lunge, glide, recover. (lean, bob, front foot dx, back foot dx)
_DASH = [(1, 2, 3, -3), (3, 2, 6, -6), (3, 2, 6, -6), (1, 1, 3, -3)]


def lying(anim: str, f: int) -> bool:
    """True for frames drawn upright then turned 90 degrees onto the ground (death 4-5)."""
    return anim == "death" and f >= 4


def skeleton(anim: str, f: int, pr: dict) -> dict:
    """Joint positions (pixels) for frame f of anim with proportions pr."""
    bob = 0
    lean = 0                       # upper body x shift (head, neck, shoulders)
    feet = [(-3, 0), (3, 0)]       # (dx, lift) back, front
    hands = None                   # explicit (front, back) hand offsets from the shoulder
    if anim == "idle":
        bob = (0, 1)[f % 2]
    elif anim == "walk":
        fd, bd, fl, bl, bob = _WALK[f]
        feet = [(bd - 2, bl), (fd + 2, fl)]          # two lanes (back / front leg): they pass, never cross into an X
    elif anim == "shoot":
        feet = [(-5, 0), (4, 0)]                     # side-on stance, feet apart
        hands = _SHOOT[f]
    elif anim == "hurt":
        lean, bob = _HURT[f]
        hands = ((-1, 6), (-3, 6))
    elif anim == "death":
        bob = _DEATH_DROP[f]
        lean = -1
        feet = [(-4, 0), (4, 0)]
        hands = ((1, 7), (-2, 7))
    elif anim == "dash":
        lean, bob, fd, bd = _DASH[f]
        feet = [(bd, 1 if f in (1, 2) else 0), (fd, 0)]
        hands = ((-2, 6), (-5, 5))                   # arms trail back
    hip_y = GROUND - 2 - pr["leg_h"] + bob
    hip = (ROOT_X, hip_y)
    neck = (ROOT_X + lean, hip_y - pr["torso_h"])
    head = (ROOT_X + 1 + lean, neck[1] - pr["head_r"] + 1)
    sh = (ROOT_X + lean, neck[1] + 2)
    if hands is None:
        swing = 0 if anim == "idle" else -feet[1][0] // 2   # arms opposite the legs
        hands = ((1 + swing, pr["arm_l"] - abs(swing) // 2), (-1 - swing, pr["arm_l"] - abs(swing) // 2))
    hand_f = (sh[0] + hands[0][0], sh[1] + hands[0][1])
    hand_b = (sh[0] + hands[1][0], sh[1] + hands[1][1])
    foot_b = (ROOT_X + feet[0][0], GROUND - 2 - feet[0][1])   # sole + outline end on the ground line
    foot_f = (ROOT_X + feet[1][0], GROUND - 2 - feet[1][1])
    hips = ((ROOT_X - 2, hip_y), (ROOT_X + 2, hip_y))   # back / front hip: the legs start apart
    return {"hip": hip, "hip_back": hips[0], "hip_front": hips[1], "neck": neck, "head": head, "shoulder": sh,
            "hand_front": hand_f, "hand_back": hand_b, "foot_back": foot_b, "foot_front": foot_f}


def lay_down(c: Canvas) -> Canvas:
    """Turns an upright frame 90 degrees (pixel exact) so the body lies on the ground, head toward the back."""
    from PIL import Image
    img = c.img.rotate(90, expand=False)
    bbox = img.getbbox()
    out = Canvas(S, S)
    if bbox:
        dy = GROUND - bbox[3]                      # rest on the ground line
        out.img.alpha_composite(img, (0, dy))
    return out


def _line(c, a, b, col, w=1):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for k in range(n):
        t = k / max(1, n - 1)
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        for s in range(w):
            _p(c, x + s - w // 2, y, col)


def _disk(c, cx, cy, r, col):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r:
                _p(c, cx + x, cy + y, col)


def draw_bare(j: dict, pr: dict, pal: dict) -> Canvas:
    """The bare base body (skin, simple shorts) on joints j: the layer every outfit is drawn over."""
    c = Canvas(S, S)
    # back limbs (darker)
    _line(c, j["hip_back"], j["foot_back"], pal["skin_d"], 3)
    _line(c, j["shoulder"], j["hand_back"], pal["skin_d"], 2)
    # torso
    hx, hy = j["hip"]
    nx, ny = j["neck"]
    w = pr["torso_w"] // 2
    for y in range(ny, hy + 1):
        k = (y - ny) / max(1, hy - ny)
        half = round(w - 1 + k * 1.2)
        for x in range(-half, half + 1):
            _p(c, nx + x, y, pal["shirt"] if y < hy - 2 else pal["shorts"])
    # front limbs
    _line(c, j["hip_front"], j["foot_front"], pal["skin"], 3)
    for foot, col in ((j["foot_back"], pal["shoe_d"]), (j["foot_front"], pal["shoe"])):
        for x in range(-1, 3):
            _p(c, foot[0] + x, foot[1], col)
            _p(c, foot[0] + x, foot[1] - 1, col)
    _line(c, j["shoulder"], j["hand_front"], pal["skin"], 2)
    _disk(c, j["hand_front"][0], j["hand_front"][1], 1, pal["skin"])
    # head: big round, eyes, cheek
    hxh, hyh = j["head"]
    r = pr["head_r"]
    _disk(c, hxh, hyh, r, pal["skin"])
    for y in range(-r, -r // 3):              # simple hair cap so the head reads
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r:
                _p(c, hxh + x, hyh + y, pal["hair"])
    for x in range(-r, -r // 2):
        for y in range(-r // 3, r // 2):
            if x * x + y * y <= r * r + r:
                _p(c, hxh + x, hyh + y, pal["hair"])
    ex = hxh + r // 2                          # big cute eyes: 2x4, a white glint top-left
    ey = hyh
    for ox in (0, -5):
        for dy in range(4):
            _p(c, ex + ox, ey + dy, pal["eye"])
            _p(c, ex + ox + 1, ey + dy, pal["eye"])
        _p(c, ex + ox, ey, "#ffffff")
    _p(c, ex + 2, ey + 4, pal["cheek"])
    _p(c, ex - 6, ey + 4, pal["cheek"])
    return c.outline(pal["outline"])
