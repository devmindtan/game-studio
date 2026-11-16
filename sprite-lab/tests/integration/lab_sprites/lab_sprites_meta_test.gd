extends RefCounted
## Integration: every sprite in the lab loads as a SpriteSheet whose json matches
## its strip, whose animations are contiguous and cover the strip, and whose
## anchor lies inside the frame. Runs on every sprite, so a new one is covered
## the moment `gamekit art run` writes it.

const DIR := "res://sprites"

var failures: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func _names() -> PackedStringArray:
	var out := PackedStringArray()
	var d := DirAccess.open(DIR)
	if d:
		for n in d.get_directories():
			if FileAccess.file_exists(DIR.path_join("%s/%s.json" % [n, n])):
				out.append(n)
	return out


func test_lab_has_sprites() -> void:
	_check(not _names().is_empty(), "no sprite in sprite-lab/sprites (gamekit art new <name>)")


func test_every_sprite_matches_its_strip() -> void:
	for n in _names():
		var s := SpriteSheet.load_dir(DIR.path_join(n), n)
		_check(s != null and s.texture != null, "%s: does not load" % n)
		if s == null or s.texture == null:
			continue
		var total := int(s.meta.get("frames", 0))
		_check(s.texture.get_width() == int(s.frame_size.x) * total
			and s.texture.get_height() == int(s.frame_size.y),
			"%s: strip %dx%d vs %d x %s" % [n, s.texture.get_width(), s.texture.get_height(), total, s.frame_size])


func test_animations_are_contiguous_and_cover_the_strip() -> void:
	for n in _names():
		var s := SpriteSheet.load_dir(DIR.path_join(n), n)
		if s == null:
			continue
		var next := 0
		for a in s.animation_names():
			var e := s.animation(a)
			_check(int(e.get("start", -1)) == next, "%s/%s starts at %s, expected %d" % [n, a, e.get("start"), next])
			_check(float(e.get("fps", 0)) > 0.0, "%s/%s: fps must be > 0" % [n, a])
			next = int(e.get("start", 0)) + int(e.get("frames", 0))
		_check(next == int(s.meta.get("frames", 0)), "%s: animations cover %d of %s frames" % [n, next, s.meta.get("frames")])


func test_every_anchor_is_inside_its_frame() -> void:
	for n in _names():
		var s := SpriteSheet.load_dir(DIR.path_join(n), n)
		if s:
			_check(Rect2(Vector2.ZERO, s.frame_size).grow(0.01).has_point(s.anchor),
				"%s: anchor %s outside %s" % [n, s.anchor, s.frame_size])
