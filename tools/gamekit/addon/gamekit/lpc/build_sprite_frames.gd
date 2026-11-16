extends SceneTree
## Builds a SpriteFrames resource for every ingested LPC character.
##
## Usage (after `godot --headless --path . --import`, so the PNGs are imported):
##   gamekit sprites <game>   (or: godot --headless --path <game> -s res://addons/gamekit/lpc/build_sprite_frames.gd)
##
## Reads   res://assets/sprites/characters/<name>/standard/<file>.png
## Writes  res://assets/sprites/characters/<name>/<name>_frames.tres
## Animation names are "<anim>_<direction>" (walk_down, slash_left, ...) or just
## "<anim>" for one-direction animations (hurt, climb). See lpc_layout.json.

const LAYOUT_PATH := "res://addons/gamekit/lpc/lpc_layout.json"
const CHARACTERS_DIR := "res://assets/sprites/characters"


func _init() -> void:
	var layout: Variant = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT_PATH))
	if not layout is Dictionary:
		push_error("Cannot read %s" % LAYOUT_PATH)
		quit(1)
		return
	var dir := DirAccess.open(CHARACTERS_DIR)
	if dir == null:
		print("No %s - nothing to build." % CHARACTERS_DIR)
		quit(0)
		return
	var failed := 0
	for name in dir.get_directories():
		if not _build(name, layout):
			failed += 1
	quit(1 if failed > 0 else 0)


func _build(name: String, layout: Dictionary) -> bool:
	var base := CHARACTERS_DIR.path_join(name)
	var size := int(layout["frame_size"])
	var dirs: Array = layout["direction_order"]
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	var built: Array[String] = []
	for anim: Dictionary in layout["animations"]:
		var png := base.path_join("standard/%s.png" % anim["file"])
		if not ResourceLoader.exists(png):
			continue
		var tex: Texture2D = load(png)
		var rows := int(anim["directions"])
		for r in rows:
			var anim_name := String(anim["name"]) if rows == 1 else "%s_%s" % [anim["name"], dirs[r]]
			frames.add_animation(anim_name)
			frames.set_animation_speed(anim_name, float(anim["fps"]))
			frames.set_animation_loop(anim_name, bool(anim["loop"]))
			for col in anim["cycle"]:
				var region := Rect2(int(col) * size, r * size, size, size)
				if region.end.x > tex.get_width() or region.end.y > tex.get_height():
					continue
				var atlas := AtlasTexture.new()
				atlas.atlas = tex
				atlas.region = region
				frames.add_frame(anim_name, atlas)
		built.append(String(anim["name"]))
	if built.is_empty():
		push_error("%s: no standard/*.png found" % name)
		return false
	var out := base.path_join("%s_frames.tres" % name)
	var err := ResourceSaver.save(frames, out)
	if err != OK:
		push_error("%s: save failed (%s)" % [out, error_string(err)])
		return false
	print("OK    %s  (%s)" % [out, ", ".join(built)])
	return true
