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
  effects     the effect sprites skill data really plays (no lab library here)
  review      design/review.json (the user's verdicts saved by the dashboard)

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
        })
    return {
        "id": skill_id, "name": upgrade.get("name", skill_id), "desc": upgrade.get("desc", ""),
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
        if t[-1] > lim["oneshot_max"]:
            slow.append("%s dài %.2fs" % (a["name"], t[-1]))
        hb = a.get("hitbox") or {}
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
    out["small"] = ["pass", "%dx%d" % tuple(fs)] if max(fs) <= lim["frame_max"] else ["fail", "khung %dx%d > %d" % (fs[0], fs[1], lim["frame_max"])]
    reach = max([reach_of(a.get("hitbox")) for a in play] or [0.0]) * scale * size_max
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


def used_effects(skills, sprites):
    """Effect sprites the game's data really plays (skill sprites and tiers)."""
    by_name = {s["name"]: s for s in sprites}
    out = []
    for sk in skills:
        for lv, t in enumerate(sk["tiers"], 1):
            if t in by_name:
                out.append({"sprite": by_name[t], "skill": sk["id"], "skill_name": sk["name"],
                            "tier": lv if len(sk["tiers"]) > 1 else 0, "check": sk.get("check")})
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
                       "pool_size": len(ups)})
        for u in ups:
            sid = str(u.get("id", ""))
            if u.get("kind") == "skill" and isinstance(defs.get(sid), dict):
                e = skill_entry(sid, defs[sid], u, cls, root)
                e["class"] = cid
                skills.append(e)
            else:
                stat_ups.append({"id": sid, "class": cid, "name": u.get("name", sid), "desc": u.get("desc", ""),
                                 "max_level": int(u.get("max_level", 1)), "weight": u.get("weight", 1),
                                 "levels": [level_values(u, lv) for lv in range(1, int(u.get("max_level", 1)) + 1)]})

    mons = []
    for mid, m in monsters.items():
        appears = []
        for st in stages:
            ts = [float(w.get("t_from", 0)) for w in st["waves"] if w.get("monster") == mid]
            if ts:
                appears.append({"stage": st["number"], "from": min(ts), "expected": st["expected_spawns"].get(mid, 0)})
        mons.append({"id": mid, "stats": m, "sprite": sprite_info(root, str(m.get("sprite", mid))), "appears": appears})

    rules_doc = load(os.path.join(data, "gameplay_rules.json"))
    scale = float(cfg.get("world", {}).get("sprite_scale", 2))

    def meta_of(name):
        return load(os.path.join(root, "assets", "sprites", "custom", name, name + ".json")) or \
            load(os.path.join(LAB, name, name + ".json")) or None

    if rules_doc.get("rules"):
        for sk in skills:
            sk["check"] = check_skill(sk, classes.get(sk["class"], {}), rules_doc, meta_of, scale)

    custom = os.path.join(root, "assets", "sprites", "custom")
    sprites = [s for s in (sprite_info(root, n) for n in sorted(os.listdir(custom)) if os.path.isdir(custom)) if s] \
        if os.path.isdir(custom) else []

    info = project_info(os.path.join(root, "project.godot"))
    return {
        "slug": slug, "name": info.get("name") or slug, "version": info.get("version", ""),
        "brief": brief_pitch(root), "decisions": decisions(root), "ui": ui_set(root),
        "world": cfg.get("world", {}), "xp": cfg.get("xp", {}), "pickups": cfg.get("pickups", {}),
        "stages": stages, "heroes": heroes, "monsters": mons, "skills": skills, "stat_ups": stat_ups,
        "sprites": sprites, "review": load(os.path.join(root, "design", "review.json")),
        "rules": rules_doc, "rule_doc": rel(os.path.join(root, "design", "gameplay-rules.md")),
        "effects": used_effects(skills, sprites), "statuses": [],
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
