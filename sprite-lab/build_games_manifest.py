#!/usr/bin/env python3
"""Write games-manifest.json for the game dashboard (games.html).

Read-only view of every game under games/: what the game really uses, so the
user can look at it and judge what to apply. Nothing in a game is modified here.

Per game:
  info        project.godot name/version, pitch (design/game-brief.md),
              decisions table (production/roadmap.md "Đã quyết")
  ui          production/ui/screens.json + the captured images (gamekit ui-shots),
              with a staleness flag when game files are newer than the captures
  world       run_config.json (arena, spawn ring, xp curve, ui)
  stages      assets/data/waves/stage_*.json (+ per-monster spawn rate curves)
  heroes      classes.json + the class sprite (layers, body) as the game has it
  monsters    monsters.json + sprite + where/when each one spawns
  skills      upgrades_<class>.json skills, with a value table per level that
              follows PlayerStats (add per level, mul per level, floor 0.2)
  stat_ups    the stat upgrades with their per-level values
  sprites     every sprite folder the game ships (assets/sprites/custom)
  statuses    buff/debuff effects drawn on characters (the aura of each items.json buff)
  docs        design/*.md (title + group), the "Kịch bản" tab
  missions    daily missions (missions.json) and gacha (gacha.json)

Paths are relative to sprite-lab/ (the page lives there; the server is rooted
at the workspace, see serve-viewer.sh). Image URLs carry ?v=<mtime>.
Run by serve-viewer.sh, and by the server on every request for the manifest.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAMES = os.path.join(ROOT, "games")
OUT = os.path.join(HERE, "games-manifest.json")
LAB = os.path.join(HERE, "sprites")


def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {} if default is None else default


def rel(path):
    """URL of a workspace file as seen from sprite-lab/ (with a cache buster)."""
    v = int(os.path.getmtime(path)) if os.path.exists(path) else 0
    return os.path.relpath(path, HERE).replace(os.sep, "/") + f"?v={v}"


def clean(d):
    return {k: v for k, v in d.items() if not str(k).startswith("_")} if isinstance(d, dict) else {}


def project_info(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        text = ""

    def grab(key):
        m = re.search(r'^' + re.escape(key) + r'\s*=\s*"([^"]*)"', text, re.M)
        return m.group(1) if m else ""
    return {"name": grab("config/name"), "version": grab("config/version")}


def brief_pitch(root):
    try:
        text = open(os.path.join(root, "design", "game-brief.md"), encoding="utf-8").read()
    except OSError:
        return {}
    out = {}
    for key, label in (("pitch", "Pitch"), ("genre", "Genre"), ("question", "Question"), ("hooks", "Hooks")):
        m = re.search(r"\*\*" + label + r":\*\*\s*(.+)", text)
        if m:
            out[key] = m.group(1).strip()
    return out


def docs_of(root):
    """Every design/*.md the game documents itself with: title from the first "# "
    line, group from the folder. The dashboard's "Kịch bản" tab reads this, so a
    new document shows up with no page edit (lesson: a hardcoded list goes stale)."""
    docs = []
    for dirpath, _dirs, files in os.walk(os.path.join(root, "design")):
        for name in files:
            if not name.endswith(".md") or name in ("CLAUDE.md", "README.md"):
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8").read()
            except OSError:
                continue
            title = ""
            for line in text.splitlines():
                if line.strip().startswith("# "):
                    title = re.sub(r"[*`]+", "", line.strip()[2:]).strip()
                    break
            relp = os.path.relpath(path, root).replace(os.sep, "/")
            docs.append({"path": relp, "title": title or name[:-3],
                         "group": "Màn hình" if "/ux/" in relp else "Hệ thống"})
    # master first, then the system docs, then the screen (ux) docs; alphabetical within a group
    docs.sort(key=lambda d: (0 if d["path"] == "design/master.md" else 2 if "/ux/" in d["path"] else 1, d["path"]))
    return docs


def decisions(root):
    try:
        text = open(os.path.join(root, "production", "roadmap.md"), encoding="utf-8").read()
    except OSError:
        return []
    m = re.search(r"## Đã quyết.*?\n(.*?)\n## ", text, re.S)
    rows = []
    for line in (m.group(1) if m else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] not in ("Chủ đề", "---") and not set(cells[0]) <= {"-"}:
            rows.append({"topic": cells[0], "decision": cells[1]})
    return rows


def sprite_info(root, name):
    d = os.path.join(root, "assets", "sprites", "custom", name)
    meta = load(os.path.join(d, name + ".json"))
    if not meta:
        return None
    info = {"name": name, "meta": meta, "strip": rel(os.path.join(d, name + "_strip.png"))}
    if meta.get("layers"):
        info["layers"] = {n: rel(os.path.join(d, "layers", n + "_strip.png")) for n in meta["layers"]}
    return info


def ui_set(root):
    """The game's current screens: production/ui/screens.json captured by
    `gamekit ui-shots` into production/ui/<name>.png. `stale` names the newest
    game file changed after the oldest capture (the set may no longer match)."""
    ui = os.path.join(root, "production", "ui")
    spec = load(os.path.join(ui, "screens.json"))
    shots = []
    for sc in spec.get("screens", []):
        img = os.path.join(ui, sc["name"] + ".png")
        shots.append({"name": sc["name"], "title": sc.get("title", sc["name"]),
                      "url": rel(img) if os.path.exists(img) else "",
                      "mtime": int(os.path.getmtime(img)) if os.path.exists(img) else 0})
    newest, newest_file = 0, ""
    for pattern in ("src/**/*.gd", "src/**/*.tscn", "assets/data/**/*.json", "assets/sprites/**/*.png", "project.godot"):
        for f in glob.glob(os.path.join(root, pattern), recursive=True):
            m = os.path.getmtime(f)
            if m > newest:
                newest, newest_file = m, os.path.relpath(f, root)
    oldest = min([s["mtime"] for s in shots if s["mtime"]] or [0])
    stale = {"file": newest_file, "mtime": int(newest)} if shots and newest > oldest + 1 else None
    return {"shots": shots, "stale": stale, "missing": [s["name"] for s in shots if not s["url"]]}


def rate_at(w, t):
    t0, t1 = float(w.get("t_from", 0)), float(w.get("t_to", 0))
    if t < t0 or t > t1 or t1 <= t0:
        return 0.0
    r0 = float(w.get("rate", 0))
    r1 = float(w.get("rate_end", r0))
    return r0 + (r1 - r0) * (t - t0) / (t1 - t0)


def stage_entry(path):
    s = load(path)
    duration = float(s.get("duration", 0))
    waves = [w for w in s.get("waves", []) if isinstance(w, dict)]
    step = 5.0
    times = [i * step for i in range(int(duration / step) + 1)]
    curves = {}
    for w in waves:
        if "burst" in w:
            continue
        m = str(w.get("monster", ""))
        c = curves.setdefault(m, [0.0] * len(times))
        for i, t in enumerate(times):
            c[i] += rate_at(w, t)
    bursts = [{"monster": w.get("monster"), "t": float(w.get("t_from", 0)), "count": int(w["burst"])}
              for w in waves if "burst" in w]
    total = {m: round(sum(v) * step) for m, v in curves.items()}
    for b in bursts:
        total[b["monster"]] = total.get(b["monster"], 0) + b["count"]
    return {"file": os.path.basename(path), "number": s.get("number"), "name": s.get("name", ""),
            "duration": duration, "waves": waves, "times": times, "curves": curves,
            "bursts": bursts, "expected_spawns": total}


def progression_of(data, classes):
    """Stages 1..count with the difficulty multipliers (same formulas as the game's
    src/core/stages.gd), regions, which wave file each stage plays, rewards; and the
    milestone rewards (milestones.json) with names from the class card pools."""
    st = load(os.path.join(data, "stages.json"))
    if not st:
        return {}
    k = st.get("scale", {})
    rw = st.get("rewards", {})
    every = int(st.get("boss_every", 10))
    regions = [r for r in st.get("regions", []) if isinstance(r, dict)]
    curve = []
    for n in range(1, int(st.get("count", 30)) + 1):
        m = n - 1
        reg = next((r for r in regions if r.get("from", 0) <= n <= r.get("to", 0)), regions[-1] if regions else {})
        boss = every > 0 and n % every == 0
        own = os.path.join(data, "waves", "stage_%03d.json" % n)
        wfile = os.path.basename(own) if os.path.exists(own) else str(reg.get("boss_waves" if boss else "waves", "")) + ".json"
        curve.append({"n": n, "boss": boss, "region": reg.get("name", ""), "waves": wfile,
                      "hp": round(1 + k.get("hp_lin", 0) * m + k.get("hp_quad", 0) * m * m, 3),
                      "dmg": round(1 + k.get("dmg_lin", 0) * m, 3),
                      "rate": round(min(max(1.0, k.get("rate_max", 1)), 1 + k.get("rate_lin", 0) * m), 3),
                      "gold": int(rw.get("gold_base", 0)) + int(rw.get("gold_per_stage", 0)) * n,
                      "gems_first": int(rw.get("gems_boss_first" if boss else "gems_first", 0)),
                      "gems_repeat": int(rw.get("gems_repeat", 0))})
    ms = load(os.path.join(data, "milestones.json"))
    cards = {}
    for cid, cls in classes.items():
        for u in load(os.path.join(data, str(cls.get("upgrades", "")))).get("upgrades", []):
            if isinstance(u, dict):
                cards[str(u.get("id", ""))] = u
    milestones = []
    for lv, ids in sorted(clean(ms.get("levels", ms.get("stages", {}))).items(), key=lambda kv: int(kv[0])):
        out = []
        for rid in ids:
            r = ms.get("rewards", {}).get(rid, {})
            card = cards.get(str(r.get("skill", rid)), {}) if r.get("kind") == "skill" else {}
            out.append({"id": rid, "kind": r.get("kind", ""), "class": r.get("class", ""), "icon": r.get("icon", rid),
                        "name": card.get("name", r.get("name", rid)), "desc": card.get("desc", r.get("desc", ""))})
        milestones.append({"level": int(lv), "rewards": out})
    return {"count": len(curve), "boss_every": every, "scale": k, "rewards": rw, "curve": curve,
            "regions": [{"id": r.get("id"), "name": r.get("name"), "from": r.get("from"), "to": r.get("to"),
                         "waves": r.get("waves"), "boss_waves": r.get("boss_waves"), "ground": r.get("ground", {})}
                        for r in regions],
            "milestones": milestones}


def level_values(upgrade, level):
    """The upgrade's effects at `level`, as PlayerStats applies them."""
    out = {}
    for stat, e in (upgrade.get("effects") or {}).items():
        if "add" in e:
            out[stat] = {"add": round(float(e["add"]) * level, 3)}
        if "mul" in e:
            out[stat] = {"mul": round(max(0.2, 1.0 + float(e["mul"]) * level), 3)}
    return out


def skill_entry(skill_id, defn, upgrade, cls, root):
    stats = cls.get("stats", {})
    base_damage = float(stats.get("damage", 10.0))
    tiers = [str(t) for t in defn.get("tier_sprites", [])] or [str(defn.get("sprite", skill_id))]
    levels = []
    for lv in range(1, int(upgrade.get("max_level", 1)) + 1):
        eff = level_values(upgrade, lv)
        dmg_mul = eff.get(f"skill_damage.{skill_id}", {}).get("mul", 1.0)
        area_mul = eff.get(f"skill_area.{skill_id}", {}).get("mul", 1.0)
        if "cooldown" in defn:
            cooldown = float(defn["cooldown"])
        else:
            cooldown = float(stats.get("cooldown", 1.0)) * float(defn.get("cooldown_mul", 1.0))
        levels.append({
            "level": lv,
            "damage": round(base_damage * float(defn.get("damage_mul", 1.0)) * dmg_mul, 1),
            "size": round(float(stats.get("area", 1.0)) * float(defn.get("size_mul", 1.0)) * area_mul, 2),
            "cooldown": round(cooldown, 2),
            "sprite": tiers[min(lv - 1, len(tiers) - 1)],
            "effects": eff,
            # statuses the skill puts on monsters at this level (on_hit "from")
            "statuses": [e for e in defn.get("on_hit", []) if int(e.get("from", 1)) <= lv],
        })
    return {
        "id": skill_id, "name": upgrade.get("name", skill_id), "desc": upgrade.get("desc", ""),
        "icon": upgrade.get("icon", skill_id),
        "max_level": int(upgrade.get("max_level", 1)), "weight": upgrade.get("weight", 1),
        "start": skill_id in (cls.get("start_skills") or {}),
        "params": defn, "tiers": tiers, "levels": levels,
    }


# --- gameplay rules (games/<g>/assets/data/gameplay_rules.json) ------------------
# Same checks as the game's tests/integration/data/gameplay_rules_test.gd; here
# they also grade Sprite Lab effects that are not in the game yet.
PLAY_PREF = ("slash_right", "spin", "fly", "burst", "spell", "attack")
TAGS = load(os.path.join(HERE, "sprite-tags.json"))


def played_anims(meta):
    """Animations the game would play for this effect sprite."""
    names = [a.get("name", "") for a in meta.get("animations", [])]
    slashes = [n for n in names if n.startswith("slash_")]
    if slashes:
        return slashes
    for p in PLAY_PREF:
        if p in names:
            return [p]
    return names[:1]


def anim_times(a):
    n = int(a.get("frames", 1))
    ms = a.get("durations_ms") or [1000.0 / max(1.0, float(a.get("fps", 8)))] * n
    starts = [sum(ms[:i]) / 1000.0 for i in range(n + 1)]
    return starts


def reach_of(hb):
    if not hb:
        return 0.0
    if hb.get("shape") == "rect":
        return max(float(hb.get("half_w", 0)), float(hb.get("half_h", 0)))
    return float(hb.get("radius", 0))


def check_sprite(meta, lim, scale, size_max, has_duration):
    """Rule results that depend on the sprite only: hitbox, snappy, directional,
    small, and the reach part of screen. Returns ({rule: [status, why]}, reach px)."""
    out = {}
    anims = {a.get("name"): a for a in meta.get("animations", [])}
    play = [anims[n] for n in played_anims(meta) if n in anims]
    bad = [a["name"] for a in play if not isinstance(a.get("hitbox"), dict)
           or not (0 <= a["hitbox"].get("active", [-1, -1])[0] <= a["hitbox"].get("active", [-1, -1])[1] < a.get("frames", 1))]
    out["hitbox"] = ["fail", "thiếu hitbox: " + ", ".join(bad)] if bad else ["pass", "hitbox đo từ pixel"]
    slow = []
    for a in play:
        t = anim_times(a)
        if a.get("loop", True):
            if not has_duration:
                slow.append(a["name"] + " lặp nhưng data không có duration")
            continue
        hb = a.get("hitbox") or {}
        # same rule as the game's gameplay_rules_test: hits end within oneshot_max, then an
        # ending (linger / fade) of at most outro_max (user 2026-11-18)
        end = t[min(len(t) - 1, hb.get("active", [0, len(t) - 2])[1] + 1)]
        if end > lim["oneshot_max"]:
            slow.append("%s trúng tới %.2fs" % (a["name"], end))
        if t[-1] - end > lim.get("outro_max", 0.0) + 1e-6:
            slow.append("%s pha kết thúc %.2fs" % (a["name"], t[-1] - end))
        if hb.get("active") and t[hb["active"][0]] > lim["active_start_max"]:
            slow.append("%s trúng lúc %.2fs" % (a["name"], t[hb["active"][0]]))
    out["snappy"] = ["fail", "; ".join(slow)] if slow else ["pass", "ra đòn nhanh"]
    names = set(anims)
    slash = {n for n in names if n.startswith("slash_")}
    need = {"slash_right", "slash_left", "slash_up", "slash_down"}
    if slash:
        out["directional"] = ["pass", "đủ 4 hướng"] if need <= names else ["fail", "thiếu " + ", ".join(sorted(need - names))]
    else:
        out["directional"] = ["na", "không phải đòn định hướng"]
    fs = meta.get("frame_size", [0, 0])
    px = float(meta.get("px_scale", 1.0))   # double-density sprites (icefx): the logical size counts
    ok = max(fs) * px <= lim["frame_max"] and max(fs) <= lim.get("frame_max_dense", lim["frame_max"])
    # fx_craft (should; must in the game's test once a sprite is redrawn with px_scale)
    craft = []
    for a in play:
        n = a.get("name", "")
        if n.startswith("fly") or n.startswith("slash") or a.get("loop", True):
            continue
        t = anim_times(a)
        act = (a.get("hitbox") or {}).get("active", [0, 0])
        if a.get("frames", 0) < lim.get("fx_frames_min", 0):
            craft.append("%s %d frame" % (n, a.get("frames", 0)))
        if act[0] < lim.get("fx_lead_frames", 0):
            craft.append("%s không có pha mở đầu" % n)
        if t[-1] - t[min(len(t) - 1, act[1] + 1)] < lim.get("fx_outro_min", 0) - 1e-6:
            craft.append("%s thiếu pha kết thúc" % n)
    if meta.get("px_scale") != lim.get("fx_px_scale", meta.get("px_scale")):
        craft.append("chưa vẽ mật độ gấp đôi")
    out["fx_craft"] = ["fail", "; ".join(craft)] if craft else ["pass", "đủ pha, mật độ gấp đôi"]
    out["small"] = ["pass", "%dx%d" % tuple(fs) + (" (×%g)" % px if px != 1 else "")] if ok else ["fail", "khung %dx%d > %d" % (fs[0], fs[1], lim["frame_max"])]
    reach = max([reach_of(a.get("hitbox")) for a in play] or [0.0]) * scale * size_max * px
    flies = any(a.get("name") == "fly" for a in play)
    return out, reach, flies


def grade(results, rules):
    musts = {r["id"] for r in rules if r.get("severity") == "must"}
    fails = [k for k, v in results.items() if v[0] == "fail" and k in musts]
    warns = [k for k, v in results.items() if v[0] == "fail" and k not in musts]
    return {"results": results, "fail": fails, "warn": warns, "ok": not fails}


def check_skill(skill, cls, rules_doc, sprite_meta, scale):
    lim, rules = rules_doc.get("limits", {}), rules_doc.get("rules", [])
    levels = skill["levels"]
    first, last = levels[0], levels[-1]
    p = skill["params"]
    res = {}
    cd = first["cooldown"]
    res["auto"] = ["pass", "hồi %.2fs" % cd] if lim["cooldown_min"] <= cd <= lim["cooldown_max"] else ["fail", "hồi %.2fs ngoài %s–%s" % (cd, lim["cooldown_min"], lim["cooldown_max"])]
    metas = [sprite_meta(t) for t in skill["tiers"]]
    if not all(metas):
        res["hitbox"] = ["fail", "thiếu sprite: " + ", ".join(t for t, m in zip(skill["tiers"], metas) if not m)]
        return grade(res, rules)
    per = [check_sprite(m, lim, scale, last["size"], "duration" in p) for m in metas]
    flies = any(r[2] for r in per)
    for key in ("hitbox", "snappy", "directional", "small"):
        bad = [r[0][key] for r in per if r[0][key][0] == "fail"]
        res[key] = bad[0] if bad else per[0][0][key]
    reach = max(r[1] for r in per)
    cast = float(p.get("cast_range", 0))
    why = "tầm %.0f px" % reach + (" + bắn xa %.0f px" % cast if cast else "")
    ok = (flies or lim["reach_min"] <= reach) and reach <= lim["reach_max"] and cast <= lim["cast_range_max"]
    res["screen"] = ["pass" if ok else "fail", why]
    n = len(levels)
    grows = all(b["damage"] > a["damage"] or b["size"] > a["size"] for a, b in zip(levels, levels[1:]))
    tiers_ok = not p.get("tier_sprites") or len(skill["tiers"]) == n
    lv_ok = lim["levels_min"] <= n <= lim["levels_max"] and grows and tiers_ok
    res["levels"] = ["pass" if lv_ok else "fail", "%d cấp%s%s" % (n, "" if grows else ", có cấp không mạnh hơn",
                     "" if tiers_ok else ", %d bậc sprite ≠ %d cấp" % (len(skill["tiers"]), n))]
    tags = [t for m in skill["tiers"] for t in TAGS.get(m, {}).get("tags", []) if t.startswith("class-")]
    want = "class-" + skill["class"]
    res["class"] = ["na", "chưa gắn tag class"] if not tags else (["pass", want] if all(t == want for t in tags) else ["fail", "tag " + ", ".join(sorted(set(tags))) + " nhưng nằm trong pool " + skill["class"]])
    st = cls.get("stats", {})
    base = float(st.get("damage", 1)) / max(0.01, float(st.get("cooldown", 1)))
    ratio = (first["damage"] * max(1, int(p.get("ticks", 1))) / max(0.01, cd)) / max(0.01, base)
    res["dps"] = ["pass" if lim["dps_ratio_min"] <= ratio <= lim["dps_ratio_max"] else "fail", "%.2f× đòn cơ bản" % ratio]
    return grade(res, rules)


def items_of(root, data, cfg, monsters):
    """assets/data/items.json with each item's sprite and the numbers behind it."""
    items = load(os.path.join(data, "items.json"))
    pick = cfg.get("pickups", {})
    out = {"pickups": [], "buffs": [], "equipment": []}
    bcfg = cfg.get("buffs", {})
    for group in out:
        for iid, it in clean(items.get(group, {})).items():
            e = {"id": iid, "name": it.get("name", iid), "desc": it.get("desc", ""), "slot": it.get("slot", ""),
                 "sprite": sprite_info(root, str(it.get("sprite", ""))), "icon": it.get("icon", ""),
                 "rarity": it.get("rarity", ""), "class": it.get("class", "")}
            if iid == "xp_gem":
                e["facts"] = ["%s: %g kinh nghiệm" % (mid, float(m.get("xp", 1))) for mid, m in monsters.items()]
            elif iid == "gold":
                e["facts"] = ["Tỉ lệ rơi %d%% mỗi quái" % round(float(pick.get("gold_chance", 0)) * 100)]
            if group == "pickups":
                e.setdefault("facts", []).append("Tầm hút %g px × chỉ số hút" % float(pick.get("radius", 0)))
            elif group == "buffs":
                e["facts"] = buff_facts(it, bcfg)
            out[group].append(e)
    return out


STAT_VI = {"max_hp": "Máu tối đa", "damage": "Sát thương", "cooldown": "Hồi chiêu", "area": "Vùng đánh",
           "move_speed": "Tốc độ chạy", "magnet": "Tầm hút", "regen": "Hồi máu", "armor": "Giáp"}


def buff_facts(it, bcfg):
    """Numbers of one buff (items.json buffs) and how it appears (run_config.json buffs)."""
    f = ["Thời gian %g s" % float(it.get("duration", 0))]
    for stat, e in (it.get("effects") or {}).items():
        if "mul" in e:
            f.append("%s %+d%%" % (STAT_VI.get(stat, stat), round(float(e["mul"]) * 100)))
        if "add" in e:
            f.append("%s %+g" % (STAT_VI.get(stat, stat), float(e["add"])))
    if it.get("invulnerable"):
        f.append("Miễn mọi sát thương")
    if bcfg:
        ev = bcfg.get("spawn_every", [0, 0])
        f.append("Xuất hiện ngẫu nhiên: lần đầu sau %g s, rồi mỗi %g–%g s, nằm %g s" % (
            float(bcfg.get("first_after", 0)), float(ev[0]), float(ev[1]), float(bcfg.get("lifetime", 0))))
    return f


def status_numbers(sid, e):
    """One on_hit entry in words: '1,5 s, tốc độ ×0,5'."""
    out = []
    if "time" in e:
        out.append("%g s" % float(e["time"]))
    if "mul" in e:
        out.append(("tốc độ ×%g" if sid == "slow" else "×%g sát thương mỗi lần lan") % float(e["mul"]))
    if "dps_mul" in e:
        out.append("mỗi giây %g%% sát thương đòn" % (float(e["dps_mul"]) * 100))
    if "chain" in e:
        out.append("lan %d quái" % int(e["chain"]))
    return ", ".join(out)


def statuses_of(root, data):
    """Status effects drawn on characters, in plain words.

    Keep it short: the effect's own description, plus its damage when it deals
    any, expressed from the character's base damage. No skill names, level
    gates or spawn timings - those belong on the Skills / Items tabs.
    """
    items = load(os.path.join(data, "items.json"))
    out = []
    sts = clean(load(os.path.join(data, "statuses.json")).get("statuses", {}))
    classes = clean(load(os.path.join(data, "classes.json")))
    base = 0.0
    for cls in classes.values():
        base = float(cls.get("stats", {}).get("damage", 0))
        if base:
            break
    pools = {}
    for f in sorted(os.listdir(data)):
        if f.startswith("upgrades_") and f.endswith(".json"):
            pools[f] = load(os.path.join(data, f))
    for sid, st in sts.items():
        dps, chain, times, slows = [], [], [], []
        for pool in pools.values():
            for defn in clean(pool.get("skills", {})).values():
                for e in defn.get("on_hit", []):
                    if e.get("status") != sid:
                        continue
                    if "dps_mul" in e:
                        dps.append(float(e["dps_mul"]))
                    if sid == "shock" and "mul" in e:
                        chain.append(float(e["mul"]))
                    if sid == "slow" and "mul" in e:
                        slows.append(float(e["mul"]))
                    if "time" in e:
                        times.append(float(e["time"]))
        facts = []
        if times:
            lo, hi = min(times), max(times)
            span = "%g s" % lo if lo == hi else "%g–%g s" % (lo, hi)
            facts.append("Thời gian %s (tùy chiêu)" % span)
        if sid == "slow" and slows:
            lo, hi = min(slows), max(slows)
            facts.append("Tốc độ ×%s" % ("%g" % lo if lo == hi else "%g–%g" % (lo, hi)))
        if dps:
            r = max(dps)
            facts.append("Sát thương %g mỗi giây (%g%% sát thương đòn, đòn %g)" % (r * base, r * 100, base))
        elif chain:
            facts.append("Lan ×%g sát thương đòn" % max(chain))
        out.append({"id": sid, "name": st.get("name", sid), "kind": "debuff", "desc": st.get("desc", ""),
                    "at": st.get("at", "body"), "tint": st.get("tint", ""), "sprite": sprite_info(root, str(st.get("sprite", ""))),
                    "facts": facts})
    for bid, it in clean(items.get("buffs", {})).items():
        if not it.get("aura"):
            continue
        out.append({"id": bid, "name": it.get("name", bid), "kind": "buff", "desc": it.get("desc", ""),
                    "layer": it.get("aura_layer", "front"), "sprite": sprite_info(root, str(it["aura"])),
                    "facts": []})
    return out


def build_game(slug):
    root = os.path.join(GAMES, slug)
    data = os.path.join(root, "assets", "data")
    cfg = load(os.path.join(data, "run_config.json"))
    classes = clean(load(os.path.join(data, "classes.json")))
    monsters = clean(load(os.path.join(data, "monsters.json")))
    stages = [stage_entry(p) for p in sorted(glob.glob(os.path.join(data, "waves", "stage_*.json")))]

    heroes, skills, stat_ups = [], [], []
    for cid, cls in classes.items():
        pool = load(os.path.join(data, str(cls.get("upgrades", ""))))
        ups = [u for u in pool.get("upgrades", []) if isinstance(u, dict)]
        defs = pool.get("skills", {})
        heroes.append({"id": cid, "name": cls.get("name", cid), "stats": cls.get("stats", {}),
                       "start_skills": cls.get("start_skills", {}), "sprite": sprite_info(root, cls.get("sprite", cid)),
                       "pool_size": len(ups), "role": cls.get("role", ""), "color": cls.get("color", ""),
                       "passive": cls.get("passive", {})})
        for u in ups:
            sid = str(u.get("id", ""))
            if u.get("kind") == "skill" and isinstance(defs.get(sid), dict):
                e = skill_entry(sid, defs[sid], u, cls, root)
                e["class"] = cid
                skills.append(e)
            else:
                stat_ups.append({"id": sid, "class": cid, "name": u.get("name", sid), "desc": u.get("desc", ""),
                                 "icon": u.get("icon", sid),
                                 "max_level": int(u.get("max_level", 1)), "weight": u.get("weight", 1),
                                 "levels": [level_values(u, lv) for lv in range(1, int(u.get("max_level", 1)) + 1)]})

    mons = [{"id": mid, "stats": m, "sprite": sprite_info(root, str(m.get("sprite", mid)))}
            for mid, m in monsters.items()]

    rules_doc = load(os.path.join(data, "gameplay_rules.json"))
    scale = float(cfg.get("world", {}).get("sprite_scale", 2))

    def meta_of(name):
        return load(os.path.join(root, "assets", "sprites", "custom", name, name + ".json")) or \
            load(os.path.join(LAB, name, name + ".json")) or None

    if rules_doc.get("rules"):
        for sk in skills:
            if sk["params"].get("cast") == "active":
                continue   # player-triggered movement (dash): the rules grade auto attacks, like the game's test
            sk["check"] = check_skill(sk, classes.get(sk["class"], {}), rules_doc, meta_of, scale)

    custom = os.path.join(root, "assets", "sprites", "custom")
    sprites = [s for s in (sprite_info(root, n) for n in sorted(os.listdir(custom)) if os.path.isdir(custom)) if s] \
        if os.path.isdir(custom) else []

    info = project_info(os.path.join(root, "project.godot"))
    return {
        "slug": slug, "name": info.get("name") or slug, "version": info.get("version", ""),
        "brief": brief_pitch(root), "decisions": decisions(root), "ui": ui_set(root),
        "world": cfg.get("world", {}), "xp": cfg.get("xp", {}), "pickups": cfg.get("pickups", {}),
        "stages": stages, "progression": progression_of(data, classes), "heroes": heroes,
        "skill_tree": load(os.path.join(data, "skill_tree.json")), "challenges": load(os.path.join(data, "challenges.json")), "monsters": mons, "skills": skills, "stat_ups": stat_ups,
        "sprites": sprites,
        "rules": rules_doc, "rule_doc": rel(os.path.join(root, "design", "gameplay-rules.md")),
        "statuses": statuses_of(root, data),   # buff/debuff effects drawn on characters
        "items": items_of(root, data, cfg, monsters),
        "docs": docs_of(root),   # design/*.md the "Kịch bản" tab lists
        "missions": clean(load(os.path.join(data, "missions.json"))),
        "gacha": clean(load(os.path.join(data, "gacha.json"))),
    }


def build():
    games = []
    if os.path.isdir(GAMES):
        for slug in sorted(os.listdir(GAMES)):
            if os.path.isfile(os.path.join(GAMES, slug, "project.godot")):
                games.append(build_game(slug))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"games": games}, f, ensure_ascii=False, indent=1)
    return len(games), sum(len(g["skills"]) for g in games)


if __name__ == "__main__":
    g, s = build()
    if "--quiet" not in sys.argv:
        print(f"games manifest: {g} games, {s} skills")
