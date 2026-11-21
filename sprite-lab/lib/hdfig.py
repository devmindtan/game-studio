"""hdfig: nhân vật nhìn nghiêng ~40 px trong khung 64x64 (bản chi tiết của minifig, người dùng 2026-11-21).

Cùng bộ tham số tư thế với minifig (`minifig.pose`, `minifig.run_pose`: bob, lean, feet, hands, head, tilt, phase,
speed, lie, flash, weapon, eyes), nên animation viết cho minifig dùng lại được: offset được nhân HD_SCALE.
Thêm chỗ cho chi tiết: đầu 11 px (tai, lông mày, mũi, miệng), tay/chân gập ở khuỷu/gối, áo 3 tông có vạt và
thắt lưng khoá, ủng có cổ + đế, kiếm có chuôi quấn, chắn kiếm, lưỡi 2 tông.

Lớp và ô trang bị giống hệt minifig (minifig.LAYERS / SLOTS), nên sheet.export_layered và check_layers dùng được.
Neo (ROOT_X, FLOOR) = (32, 60); hàng viền dưới đế ủng là 59.
"""
from __future__ import annotations

import math

from spritekit import Canvas, color

import minifig as mf
from minifig import LAYERS, OUTLINE, line, put, rect  # noqa: F401  (OUTLINE dùng ở gen.py)

W = H = 64
FLOOR = 60
SOLE = FLOOR - 2          # hàng màu cuối của đế ủng
ROOT_X = 32
HIP_Y = 45
TORSO = 12
S = 1.5                   # nhân offset tư thế minifig


def _r(v):
    return int(round(v))


def geometry(p):
    hx, hy = p["hip"]
    hip = (ROOT_X + _r(hx * S), HIP_Y + _r(p["bob"] * S))
    top = (hip[0] + _r(p["lean"] * S), hip[1] - TORSO)
    sh_back = (top[0] - 3, top[1] + 2)
    sh_front = (top[0] + 2, top[1] + 2)
    (bfx, bfl), (ffx, ffl) = p["feet"]
    foot_back = (ROOT_X + _r(bfx * S), SOLE - _r(bfl * S))
    foot_front = (ROOT_X + _r(ffx * S), SOLE - _r(ffl * S))
    (bhx, bhy), (fhx, fhy) = p["hands"]
    hand_back = (sh_back[0] + _r(bhx * S), sh_back[1] + _r(bhy * S))
    hand_front = (sh_front[0] + _r(fhx * S), sh_front[1] + _r(fhy * S))
    hdx, hdy = p["head"]
    head = (top[0] + _r(hdx * S), top[1] - 1 + _r(hdy * S))      # đáy-giữa của đầu
    return {"hip": hip, "top": top, "sh_back": sh_back, "sh_front": sh_front, "foot_back": foot_back,
            "foot_front": foot_front, "hand_back": hand_back, "hand_front": hand_front, "head": head}


def keep_above_floor(x, y, angle, length, margin=2):
    for _ in range(40):
        if y + math.sin(math.radians(angle)) * length <= SOLE - margin:
            return angle
        angle += -5 if math.cos(math.radians(angle)) >= 0 else 5
    return angle


# --- bộ phận ----------------------------------------------------------------------------------

def leg(c, hip, foot, pal, back, boot_c):
    pants, shade = (pal["pants_d"], pal["pants_d"]) if back else (pal["pants"], pal["pants_d"])
    ankle = (foot[0], foot[1] - 3)
    knee = ((hip[0] + ankle[0]) / 2 + 1, (hip[1] + ankle[1]) / 2)          # gối hơi nhô ra trước
    line(c, hip[0], hip[1], knee[0], knee[1], pants, 4)
    line(c, knee[0], knee[1], ankle[0], ankle[1], pants, 3)
    line(c, knee[0] - 1, knee[1], ankle[0] - 1, ankle[1], shade, 1)          # mép sau tối
    boot, boot_d = (pal["boot_d"], pal["boot_d"]) if back else (pal["boot"], pal["boot_d"])
    fx, fy = foot
    rect(boot_c, fx - 2, fy - 3, fx + 2, fy - 1, boot)                       # cổ + thân ủng
    rect(boot_c, fx - 2, fy - 1, fx + 4, fy, boot)                           # mũi ủng về trước
    rect(boot_c, fx - 2, fy, fx + 4, fy, boot_d)                             # đế
    if not back:
        rect(boot_c, fx - 2, fy - 3, fx + 2, fy - 3, pal.get("boot_l", boot))  # viền cổ ủng


def arm(c, sh, hand, pal, back, hand_c):
    sleeve = pal["sleeve_d"] if back else pal["sleeve"]
    mx, my = (sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2
    elbow = (mx - 1, my + 1)                                                 # khuỷu gập xuống/sau
    if not back:   # nét tối giáp thân để tay trước không chìm vào áo cùng màu
        line(c, sh[0] - 2, sh[1], elbow[0] - 2, elbow[1], pal["sleeve_d"], 1)
        line(c, elbow[0] - 1, elbow[1] + 1, hand[0] - 2, hand[1] + 1, pal["sleeve_d"], 1)
    line(c, sh[0], sh[1], elbow[0], elbow[1], sleeve, 3)
    line(c, elbow[0], elbow[1], hand[0], hand[1], sleeve, 2)
    if not back:
        put(c, sh[0], sh[1] - 1, pal.get("tunic_l", sleeve))                 # vệt sáng vai
        mx2, my2 = hand[0] - (hand[0] - elbow[0]) * 0.25, hand[1] - (hand[1] - elbow[1]) * 0.25
        line(c, mx2, my2, mx2, my2 + 1, pal["sleeve_d"], 2)                    # cổ tay áo
    skin, skin_d = (pal["skin_d"], pal["skin_d"]) if back else (pal["skin"], pal["skin_d"])
    rect(hand_c, hand[0] - 1, hand[1] - 1, hand[0] + 1, hand[1] + 1, skin)
    put(hand_c, hand[0] - 1, hand[1] + 1, skin_d)


def tunic(c, g, p, pal):
    hip, top = g["hip"], g["top"]
    rows = hip[1] - top[1]
    for i in range(rows + 1):
        y = top[1] + i
        x = _r(top[0] + (hip[0] - top[0]) * i / max(1, rows))
        c.rect(x - 5, y, x + 4, y, color(pal["tunic"]))
        c.pixel(x - 5, y, pal["tunic_d"])
        c.pixel(x - 4, y, pal["tunic_d"])
        c.pixel(x + 4, y, pal["tunic_l"])
        c.pixel(x + 3, y, pal["tunic_l"]) if i < 5 else None
    # cổ chữ V
    put(c, top[0], top[1], pal["tunic_d"])
    put(c, top[0] + 1, top[1] + 1, pal["tunic_d"])
    # thắt lưng 2 hàng + khoá
    bx = _r(hip[0] + (top[0] - hip[0]) * 0.1)
    rect(c, bx - 5, hip[1] - 2, bx + 4, hip[1] - 1, pal["belt"])
    rect(c, bx + 1, hip[1] - 2, bx + 2, hip[1] - 1, pal["buckle"])
    # vạt áo dưới thắt lưng, xoè theo tốc độ, có nếp gấp
    sway = _r(math.sin(p["phase"]) * p["speed"])
    for k in range(3):
        y = hip[1] + k
        half = 5 + k // 2
        rect(c, hip[0] - half - (sway if k == 2 else 0), y, hip[0] + half - 1, y, pal["tunic"])
        put(c, hip[0] - half - (sway if k == 2 else 0), y, pal["tunic_d"])
        for fx in (-2, 1):
            put(c, hip[0] + fx, y, pal["tunic_d"])
    rect(c, hip[0] - 6 - sway, hip[1] + 2, hip[0] + 5, hip[1] + 2, pal["tunic_d"])   # mép vạt


def face(c, p, g, pal):
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 10, hx + 5, hy - 1, pal["skin"])
    rect(c, hx - 4, hy - 10, hx - 4, hy - 2, pal["skin_d"])                # má sau tối
    if 0 <= hx + 5 < W and 0 <= hy - 1 < H:
        c.img.putpixel((hx + 5, hy - 1), (0, 0, 0, 0))                     # bo cằm
    rect(c, hx - 3, hy, hx + 3, hy, pal["skin_d"])                           # cằm/cổ
    put(c, hx + 6, hy - 5, pal["skin"])                                      # mũi
    put(c, hx - 2, hy - 6, pal["skin_d"])                                    # tai
    put(c, hx - 2, hy - 5, pal["skin_d"])
    rect(c, hx + 3, hy - 3, hx + 4, hy - 3, pal["skin_d"])                   # miệng
    eyes(c, hx + 3, hy - 7, p["eyes"], pal)


def eyes(c, x, y, kind, pal):
    e = pal.get("eye", OUTLINE)
    if kind == "open":
        rect(c, x, y, x + 1, y + 1, e)
        put(c, x + 1, y, pal.get("eye_l", "#ffffff"))                       # ánh mắt
        rect(c, x - 1, y - 2, x + 1, y - 2, pal["hair_d"])                   # lông mày
    elif kind == "closed":
        rect(c, x - 1, y + 1, x + 1, y + 1, e)
        rect(c, x - 1, y - 2, x + 1, y - 2, pal["hair_d"])
    elif kind == "wince":
        put(c, x - 1, y, e)
        put(c, x, y + 1, e)
        put(c, x - 1, y + 2, e)
        rect(c, x - 1, y - 2, x + 1, y - 2, pal["hair_d"])
    elif kind == "x":
        for dx, dy in ((-1, 0), (1, 0), (0, 1), (-1, 2), (1, 2)):
            put(c, x + dx, y + dy, e)


def robe(c, g, p, pal):
    """Áo khoác dài tới gối: thân 3 tông như tunic, từ hông xoè dần xuống gối, vạt trước mở (đường tối),
    gấu đung đưa theo tốc độ; đai lưng vải. Quần + ủng lộ dưới gấu (chân vẽ ở lớp legs như thường)."""
    hip, top = g["hip"], g["top"]
    hem_y = hip[1] + 7
    sway = _r(math.sin(p["phase"]) * 1.5 * (0.3 + p["speed"]))
    for y in range(top[1], hem_y + 1):
        if y <= hip[1]:
            t = (y - top[1]) / max(1, hip[1] - top[1])
            cx = _r(top[0] + (hip[0] - top[0]) * t)
            x0, x1 = cx - 5, cx + 4
        else:
            k = y - hip[1]
            cx = hip[0] - _r(sway * k / 7)
            x0, x1 = cx - 5 - k // 2 - _r(p["speed"] * k / 3), cx + 4 + k // 3
        c.rect(x0, y, x1, y, color(pal["robe"]))
        c.pixel(x0, y, pal["robe_d"])
        c.pixel(x0 + 1, y, pal["robe_d"])
        c.pixel(x1, y, pal["robe_l"])
        if y > hip[1]:
            c.pixel(cx + 1, y, pal["robe_d"])                 # vạt trước mở
        if y == hem_y:
            c.rect(x0, y, x1, y, color(pal["trim"]))
    put(c, top[0], top[1], pal["robe_d"])                     # cổ chéo
    put(c, top[0] + 1, top[1] + 1, pal["robe_d"])
    put(c, top[0] + 2, top[1] + 2, pal["robe_d"])
    bx = hip[0]
    rect(c, bx - 5, hip[1] - 2, bx + 4, hip[1] - 1, pal["belt"])          # đai
    rect(c, bx - 6, hip[1] - 1, bx - 5, hip[1] + 2, pal["belt"])          # mối đai rủ sau


def grid_sword(c, hand, angle, length, pal, floor_margin=1):
    """Kiếm bám lưới pixel: hướng làm tròn về bội số 45°, đặt pixel theo bước nguyên -> lưỡi là một đường
    sạch (góc lẻ như 35° ra bậc thang 1-2-1 px, trông cong; bài học 2026-11-21). Sau khi làm tròn vẫn giữ
    mũi kiếm trên sàn. Màu: blade, blade_d, guard, guard_d (tuỳ), grip, grip_l (tuỳ)."""
    hx, hy = hand
    ang = keep_above_floor(hx, hy, angle, length)
    q = round(ang / 45) * 45
    for _ in range(4):
        sx, sy = round(math.cos(math.radians(q))), round(math.sin(math.radians(q)))
        steps = length if (sx == 0 or sy == 0) else round(length / 1.41)
        if hy + steps * sy <= SOLE - floor_margin:
            break
        q += -45 if math.cos(math.radians(ang)) >= 0 else 45
    ex, ey = (0, 1) if sx else (1, 0)
    gx, gy = -sy, sx
    for k in (-1, -2, -3):
        put(c, hx + k * sx, hy + k * sy, pal.get("grip_l", pal["grip"]) if k == -2 else pal["grip"])
    put(c, hx - 4 * sx, hy - 4 * sy, pal["guard"])
    for j in range(-2, 3):
        put(c, hx + sx + j * gx, hy + sy + j * gy, pal.get("guard_d", pal["guard"]) if abs(j) == 2 else pal["guard"])
    for k in range(2, steps + 1):
        put(c, hx + k * sx, hy + k * sy, pal["blade"])
        if k < steps:
            put(c, hx + k * sx + ex, hy + k * sy + ey, pal["blade_d"])


# --- kiểm tra dùng chung cho gen.py (exit khác 0 khi hỏng) -------------------------------------

def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def standing_frames(animations, skip_flash=True):
    """Chỉ số frame đứng: bỏ death (nằm) và frame nháy trắng đầu tiên của hurt."""
    out, start = [], 0
    for name, frames, *_ in animations:
        for i in range(len(frames)):
            if name == "death" or (skip_flash and name == "hurt" and i == 0):
                continue
            out.append(start + i)
        start += len(frames)
    return out


def check_blade(strip_path, animations, pal, length, frame=64, angle=None):
    """Lưỡi kiếm thấy >= nửa (bài học: kiếm chĩa ra sau bị thân che) và thẳng một đường (một giá trị x-y,
    x+y, x hoặc y cho pixel sáng) trong mọi frame đứng. angle=45 còn đòi đúng hướng chéo xuống-trước (x - y
    không đổi): góc cố định không được bị xoay đi vì chạm sàn (bài học 2026-11-21, ronin-hd dash)."""
    from PIL import Image
    im = Image.open(strip_path).convert("RGBA")
    light, dark = _rgb(pal["blade"]), _rgb(pal["blade_d"])
    hidden, bent = [], []
    for f in standing_frames(animations):
        fr = im.crop((f * frame, 0, f * frame + frame, frame)).load()
        pts = [(x, y) for y in range(frame) for x in range(frame) if fr[x, y][3] and fr[x, y][:3] == light]
        n = len(pts) + sum(1 for y in range(frame) for x in range(frame) if fr[x, y][3] and fr[x, y][:3] == dark)
        if n < length:
            hidden.append((f, n))
        if pts and min(len({fn(x, y) for x, y in pts}) for fn in (lambda x, y: x - y, lambda x, y: x + y,
                                                                    lambda x, y: x, lambda x, y: y)) != 1:
            bent.append(f)
        elif pts and angle == 45 and len({x - y for x, y in pts}) != 1:
            bent.append(f)
    if hidden or bent:
        raise SystemExit(f"kiếm: bị che ở frame {hidden}; không thẳng ở frame {bent}")


# --- ghép ------------------------------------------------------------------------------------

def draw_layers(char, p):
    pal = char["pal"]
    L = {name: Canvas(W, H) for name in LAYERS}
    g = geometry(p)
    if char.get("behind"):
        char["behind"](L["chest_back"], p, g)
    leg(L["legs_back"], g["hip"], g["foot_back"], pal, True, L["feet_back"])
    arm(L["arms_back"], g["sh_back"], g["hand_back"], pal, True, L["arms_back"])
    if char.get("held_back"):
        char["held_back"](L["weapon_back"], p, g)
    if char.get("body", "tunic") == "robe":
        robe(L["chest"], g, p, pal)
    else:
        tunic(L["chest"], g, p, pal)
    leg(L["legs_front"], g["hip"], g["foot_front"], pal, False, L["feet_front"])
    if char.get("neck"):
        char["neck"](L["chest"], p, g)
    face(L["body"], p, g, pal)
    if char.get("hair"):
        char["hair"](L["head"], p, g)
    if char.get("held"):
        char["held"](L["weapon"], p, g)
    arm(L["arms_front"], g["sh_front"], g["hand_front"], pal, False, L["arms_front"])
    if char.get("front"):
        char["front"](L["front"], p, g)
    if p["lie"]:
        L = _lie_layers(L, p["lie"])
    if p["flash"]:
        for cv in L.values():
            mf._flash(cv, p["flash"])
    return L


def _lie_layers(layers, amount):
    from PIL import Image
    angle = 90 * amount
    rotated = {k: cv.img.rotate(angle, resample=Image.NEAREST, center=(ROOT_X, FLOOR - 1))
               for k, cv in layers.items()}
    whole = Canvas(W, H)
    for img in rotated.values():
        whole.img.alpha_composite(img)
    bb = whole.img.getchannel("A").getbbox()
    shift = (FLOOR - 2) - bb[3] + 1 if bb else 0       # chừa hàng viền dưới cùng
    out = {}
    for k, img in rotated.items():
        moved = Canvas(W, H)
        moved.img.alpha_composite(img, (0, shift) if shift >= 0 else (0, 0),
                                  (0, 0) if shift >= 0 else (0, -shift))
        out[k] = moved
    return out
