#!/usr/bin/env python3
"""Write games-manifest.json for the web viewer's Games / skill-demo view.

The HTTP server for viewer.html is rooted at sprite-lab/, so it cannot reach
../games/*.json. This builder copies the small pieces the demo needs (class,
skill, cast_range, hitbox, monster) into a manifest next to the sprite manifest.
It only READS game data - game repos are never modified here.

Everything the demo animates comes from these real files:
  games/<slug>/project.godot                 name / version
  games/<slug>/assets/data/classes.json      class sprite, base damage
  games/<slug>/assets/data/upgrades_<c>.json skills + level scaling
  games/<slug>/assets/data/monsters.json     targets for the demo scene
  sprite-lab/sprites/<sprite>/<sprite>.json  hitbox + frame timing

Run by serve-viewer.sh at start and by hand after changing game data.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAMES = os.path.join(ROOT, "games")
LAB_SPRITES = os.path.join(HERE, "sprites")
OUT = os.path.join(HERE, "games-manifest.json")


def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {} if default is None else default


def project_info(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = ""
    def grab(key):
        m = re.search(r'^' + re.escape(key) + r'\s*=\s*"([^"]*)"', text, re.M)
        return m.group(1) if m else ""
    return {"name": grab("config/name"), "version": grab("config/version")}


def lab_meta(sprite):
    path = os.path.join(LAB_SPRITES, sprite, sprite + ".json")
    return load(path)


def pick_anim(meta):
    names = [a.get("name", "") for a in meta.get("animations", [])]
    for want in ("fly", "spin", "burst", "spell", "attack"):
        for n in names:
            if n == want:
                return n
    for n in names:
        if n.startswith("slash_"):
            return n
    return names[0] if names else "default"


def cast_kind(defn, anim):
    if "cast_range" in defn:
        return "cast-out"
    if anim == "spin":
        return "orbit"
    if anim.startswith("slash_"):
        return "melee"
    if anim == "fly":
        return "projectile"
    return "cast-out"


def hitbox_of(meta, anim):
    for a in meta.get("animations", []):
        if a.get("name") == anim and isinstance(a.get("hitbox"), dict):
            hb = dict(a["hitbox"])
            # frame timing is needed to show WHEN the hitbox is live
            for key in ("fps", "frames", "durations_ms"):
                if key in a:
                    hb[key] = a[key]
            return hb
    return {}


def skill_entry(skill_id, defn, upgrade, class_id, base_damage):
    sprite = str(defn.get("sprite", skill_id))
    tiers = [str(t) for t in defn.get("tier_sprites", [])] or [sprite]
    meta = lab_meta(tiers[0]) or lab_meta(sprite) or {}
    anim = pick_anim(meta)
    return {
        "id": skill_id,
        "name": upgrade.get("name", skill_id),
        "desc": upgrade.get("desc", ""),
        "class": class_id,
        "sprite": sprite,
        "tiers": tiers,
        "anim": anim,
        "cast": cast_kind(defn, anim),
        "cast_range": float(defn.get("cast_range", 0.0)),
        "cooldown": float(defn.get("cooldown", 0.0)),
        "duration": float(defn.get("duration", 0.0)),
        "ticks": int(defn.get("ticks", 1)),
        "size_mul": float(defn.get("size_mul", 1.0)),
        "damage": round(base_damage * float(defn.get("damage_mul", 1.0)), 1),
        "hitbox": hitbox_of(meta, anim),
        "tier_hitboxes": [hitbox_of(lab_meta(t) or {}, anim) for t in tiers],
        "frame_size": meta.get("frame_size", []),
        "max_level": upgrade.get("max_level", 1),
    }


def build_game(slug):
    root = os.path.join(GAMES, slug)
    info = project_info(os.path.join(root, "project.godot"))
    data_dir = os.path.join(root, "assets", "data")
    classes = load(os.path.join(data_dir, "classes.json"))
    monsters = load(os.path.join(data_dir, "monsters.json"))
    classes = {k: v for k, v in classes.items() if isinstance(v, dict) and not k.startswith("_")}
    monsters = {k: v for k, v in monsters.items() if isinstance(v, dict) and not k.startswith("_")}

    hero_list, skills = [], []
    for class_id, cls in classes.items():
        hero_list.append({
            "id": class_id,
            "name": cls.get("name", class_id),
            "sprite": cls.get("sprite", class_id),
            "base_damage": float(cls.get("stats", {}).get("damage", 10.0)),
        })
        pool = load(os.path.join(data_dir, str(cls.get("upgrades", ""))))
        upgrades = [u for u in pool.get("upgrades", []) if isinstance(u, dict)]
        defs = pool.get("skills", {})
        for u in upgrades:
            sid = str(u.get("id", ""))
            if u.get("kind") == "skill" and sid in defs and isinstance(defs[sid], dict):
                skills.append(skill_entry(sid, defs[sid], u, class_id, hero_list[-1]["base_damage"]))

    targets = []
    for mid, m in list(monsters.items())[:4]:
        targets.append({"id": mid, "sprite": str(m.get("sprite", mid)),
                        "hp": float(m.get("hp", 10.0)), "scale": float(m.get("scale", 2))})

    return {
        "slug": slug,
        "name": info.get("name") or slug,
        "version": info.get("version", ""),
        "heroes": hero_list,
        "skills": skills,
        "targets": targets,
    }


def build():
    games = []
    if os.path.isdir(GAMES):
        for slug in sorted(os.listdir(GAMES)):
            if os.path.isfile(os.path.join(GAMES, slug, "project.godot")):
                games.append(build_game(slug))
    payload = {"games": games}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return len(games), sum(len(g["skills"]) for g in games)


if __name__ == "__main__":
    g, s = build()
    if "--quiet" not in sys.argv:
        print(f"games manifest: {g} games, {s} skills")
