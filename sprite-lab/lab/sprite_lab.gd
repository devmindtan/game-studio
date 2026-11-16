extends Node2D
## Sprite Lab viewer: test every sprite in res://sprites/<name>/ before it goes
## into a game. Two modes:
##   sheet  every animation side by side, looping, with ground line, anchor dot
##          and frame box, so one look checks the whole sheet;
##   move   a stage: walk/run, jump, attack… with mirroring, to judge the sprite
##          in motion the way a game would play it.
##
## Keys: Tab next sprite · M mode · B background · +/- scale · A anchors/boxes/hitboxes
##       move mode: ←/→ walk, Shift run, ↑/↓ (top-down sprites only),
##       Space jump, J attack, K spell, H hurt, X death, R reset.
## Args (after --): --sprite=<name> --mode=sheet|move --demo --bg=dark|light|checker
##                  --scale=<n> --no-anchors
##                  --contact=<png>  (move + demo) capture CONTACT_TIMES into one grid image, then quit
## Run: gamekit art lab <name> [sheet|move]; screenshot: gamekit art shot <name> [mode]

const SPRITES_DIR := "res://sprites"
const BGS: Array[String] = ["dark", "light", "checker"]
const MOVE_NAMES := ["walk", "run", "fly", "move"]
const RUN_NAMES := ["run", "walk", "fly", "move"]
const IDLE_NAMES := ["idle", "default"]
const ACTIONS := {  # key -> animation names to try, in order
	KEY_J: ["attack", "slash", "hit"],
	KEY_K: ["spell", "cast", "magic"],
	KEY_H: ["hurt", "damage"],
	KEY_X: ["death", "die"],
}
## Demo moments worth seeing (seconds into the 9 s demo, label): see _demo_step.
const CONTACT_TIMES := [
	[1.0, "đi phải"], [2.2, "đánh"], [3.0, "đứng"], [4.0, "chạy trái (lật)"],
	[5.2, "nhảy"], [5.9, "đi trái"], [6.6, "phép"], [7.8, "trúng đòn"],
]
const GROUND_Y := 560.0
const WALK_SPEED := 40.0  # source pixels per second; runs at 2x
const COL_TEXT := Color(0.92, 0.92, 0.95)
const COL_DIM := Color(0.92, 0.92, 0.95, 0.55)
const COL_GROUND := Color(0.45, 0.85, 0.55, 0.8)
const COL_BOX := Color(1, 1, 1, 0.18)

var _names: PackedStringArray = []
var _index := 0
var _sheet: SpriteSheet
var _mode := "sheet"
var _bg := 0
var _scale := 3.0
var _anchors := true
var _demo := false
var _time := 0.0
var _screen := Vector2(1280, 720)

# move mode
var _pos := Vector2.ZERO
var _facing := 1.0
var _action := ""        # one-shot animation playing (attack, hurt…)
var _action_t := 0.0
var _jump_t := -1.0      # < 0: not jumping
var _dead := false
var _anim_now := ""
var _anim_t := 0.0
var _contact_path := ""
var _contact_shots: Array[Image] = []
var _contact_next := 0


func _ready() -> void:
	_screen = get_viewport_rect().size
	_names = _scan()
	var want := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--sprite="): want = arg.trim_prefix("--sprite=")
		elif arg.begins_with("--mode="): _mode = arg.trim_prefix("--mode=")
		elif arg.begins_with("--bg="): _bg = maxi(0, BGS.find(arg.trim_prefix("--bg=")))
		elif arg.begins_with("--scale="): _scale = maxf(1.0, float(arg.trim_prefix("--scale=")))
		elif arg == "--demo": _demo = true
		elif arg == "--no-anchors": _anchors = false
		elif arg.begins_with("--contact="):
			_contact_path = arg.trim_prefix("--contact=")
			_mode = "move"
			_demo = true
	if want != "" and not _names.has(want):
		push_error("Sprite Lab: no sprite '%s' in %s (have: %s)" % [want, SPRITES_DIR, ", ".join(_names)])
	_index = maxi(0, _names.find(want))
	var forced_scale := false
	for arg in OS.get_cmdline_user_args():
		forced_scale = forced_scale or arg.begins_with("--scale=")
	_load(not forced_scale)


func _scan() -> PackedStringArray:
	var out := PackedStringArray()
	var dir := DirAccess.open(SPRITES_DIR)
	if dir == null:
		return out
	for n in dir.get_directories():
		if FileAccess.file_exists(SPRITES_DIR.path_join("%s/%s.json" % [n, n])):
			out.append(n)
	out.sort()
	return out


func _load(auto_scale := true) -> void:
	_sheet = null
	if _names.is_empty():
		return
	var n := _names[_index]
	_sheet = SpriteSheet.load_dir(SPRITES_DIR.path_join(n), n)
	if _sheet and auto_scale:  # frame about 120-170 px tall on screen
		_scale = clampf(roundf(150.0 / maxf(1.0, _sheet.frame_size.y)), 1.0, 10.0)
	_reset_move()


func _reset_move() -> void:
	_pos = Vector2(_screen.x * 0.5, GROUND_Y)
	_facing = 1.0
	_action = ""
	_jump_t = -1.0
	_dead = false
	_anim_now = ""


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.physical_keycode:
		KEY_TAB:
			if not _names.is_empty():
				_index = (_index + 1) % _names.size()
				_load()
		KEY_M:
			_mode = "move" if _mode == "sheet" else "sheet"
			_reset_move()
		KEY_B: _bg = (_bg + 1) % BGS.size()
		KEY_EQUAL, KEY_KP_ADD: _scale = minf(_scale + 1.0, 12.0)
		KEY_MINUS, KEY_KP_SUBTRACT: _scale = maxf(_scale - 1.0, 1.0)
		KEY_A when _mode == "sheet": _anchors = not _anchors
		KEY_R: _reset_move()
		KEY_SPACE: _try_jump()
		KEY_ESCAPE: get_tree().quit()
		_:
			if ACTIONS.has(event.physical_keycode):
				_try_action(ACTIONS[event.physical_keycode])


func _try_jump() -> void:
	if _mode == "move" and _sheet and _sheet.has_animation("jump") and _jump_t < 0.0 and not _dead:
		_jump_t = 0.0


func _try_action(names: Array) -> void:
	if _mode != "move" or _sheet == null or _dead:
		return
	var a := _sheet.first_of(names)
	if a != "":
		_action = a
		_action_t = 0.0
		_dead = names.has("death")


func _process(delta: float) -> void:
	_time += delta
	if _mode == "move" and _sheet:
		_update_move(delta)
	queue_redraw()
	if _contact_path != "" and _contact_next < CONTACT_TIMES.size() \
			and _time >= float(CONTACT_TIMES[_contact_next][0]):
		_contact_next += 1
		_grab_contact()


## Captures the frame being drawn now; after the last moment writes the grid and quits.
func _grab_contact() -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.resize(int(_screen.x / 2), int(_screen.y / 2), Image.INTERPOLATE_NEAREST)
	_contact_shots.append(img)
	if _contact_shots.size() < CONTACT_TIMES.size():
		return
	var w := int(_screen.x / 2)
	var h := int(_screen.y / 2)
	var rows := int(ceil(_contact_shots.size() / 2.0))
	var sheet := Image.create(w * 2 + 8, rows * (h + 8), false, Image.FORMAT_RGB8)
	sheet.fill(Color(0.08, 0.08, 0.1))
	for i in _contact_shots.size():
		var shot := _contact_shots[i]
		shot.convert(Image.FORMAT_RGB8)
		sheet.blit_rect(shot, Rect2i(Vector2i.ZERO, shot.get_size()), Vector2i((i % 2) * (w + 8), (i / 2) * (h + 8)))
	var err := sheet.save_png(_contact_path)
	print("contact: %s (%s)" % [_contact_path, error_string(err)])
	get_tree().quit(0 if err == OK else 1)


# --- move mode ------------------------------------------------------------------

func _update_move(delta: float) -> void:
	var dir := Vector2.ZERO
	var running := false
	if _demo:
		var d := _demo_step(delta)
		dir = d[0]
		running = d[1]
	elif not _dead:
		dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		running = Input.is_physical_key_pressed(KEY_SHIFT)
	var top_down := not _sheet.has_animation("jump")
	if not top_down:
		dir.y = 0.0
	if _action != "" and not _dead:
		dir = Vector2.ZERO  # stand still while attacking / hurt
	if absf(dir.x) > 0.01:
		_facing = signf(dir.x)
	var speed := WALK_SPEED * _scale * (2.0 if running else 1.0)
	_pos += dir.normalized() * speed * delta if dir != Vector2.ZERO else Vector2.ZERO
	var half := _sheet.frame_size.x * _scale * 0.5
	_pos.x = clampf(_pos.x, half, _screen.x - half)
	_pos.y = clampf(_pos.y, 160.0, GROUND_Y) if top_down else GROUND_Y

	if _jump_t >= 0.0:
		_jump_t += delta
		if _jump_t >= _sheet.duration("jump"):
			_jump_t = -1.0
	if _action != "":
		_action_t += delta
		if not _dead and _action_t >= _sheet.duration(_action):
			_action = ""

	var want := _choose_anim(dir, running)
	if want != _anim_now:
		_anim_now = want
		_anim_t = 0.0
	else:
		_anim_t += delta


func _choose_anim(dir: Vector2, running: bool) -> String:
	if _action != "":
		return _action
	if _jump_t >= 0.0:
		return "jump"
	if dir != Vector2.ZERO:
		var m := _sheet.first_of(RUN_NAMES if running else MOVE_NAMES)
		if m != "":
			return m
	var idle := _sheet.first_of(IDLE_NAMES)
	return idle if idle != "" else _sheet.animation_names()[0]


## Deterministic demo for screenshots: walk right, attack, run left, jump, spell…
func _demo_step(_delta: float) -> Array:
	var t := fmod(_time, 9.0)
	if t < 2.0: return [Vector2.RIGHT, false]
	if t < 2.05: _try_action(ACTIONS[KEY_J])
	if t < 3.2: return [Vector2.ZERO, false]
	if t < 5.0: return [Vector2.LEFT, true]
	if t < 5.05: _try_jump()
	if t < 6.2: return [Vector2.LEFT, false]
	if t < 6.25: _try_action(ACTIONS[KEY_K])
	if t < 7.6: return [Vector2.ZERO, false]
	if t < 7.65: _try_action(ACTIONS[KEY_H])
	return [Vector2.ZERO, false]


# --- drawing --------------------------------------------------------------------

func _draw() -> void:
	_draw_bg()
	var font := ThemeDB.fallback_font
	if _sheet == null:
		draw_string(font, Vector2(40, 80), "Chưa có sprite trong sprite-lab/sprites/. Tạo: gamekit art new <tên>",
			HORIZONTAL_ALIGNMENT_LEFT, -1, 22, COL_TEXT)
		return
	if _mode == "move":
		_draw_move(font)
	else:
		_draw_sheet(font)
	_draw_header(font)


func _draw_bg() -> void:
	var r := Rect2(Vector2.ZERO, _screen)
	match BGS[_bg]:
		"light": draw_rect(r, Color(0.86, 0.87, 0.9))
		"checker":
			draw_rect(r, Color(0.55, 0.55, 0.6))
			var c := 16.0
			for y in int(_screen.y / c) + 1:
				for x in int(_screen.x / c) + 1:
					if (x + y) % 2 == 0:
						draw_rect(Rect2(x * c, y * c, c, c), Color(0.7, 0.7, 0.75))
		_: draw_rect(r, Color(0.11, 0.12, 0.17))


func _draw_header(font: Font) -> void:
	var a := _sheet.animation_names()
	var line1 := "%s   %dx%d · neo (%s, %s) · %d animation · x%d · nền %s   (%d/%d)" % [
		_sheet.name, int(_sheet.frame_size.x), int(_sheet.frame_size.y), _sheet.anchor.x, _sheet.anchor.y,
		a.size(), int(_scale), BGS[_bg], _index + 1, _names.size()]
	draw_rect(Rect2(0, 0, _screen.x, 58), Color(0, 0, 0, 0.45))
	draw_string(font, Vector2(16, 24), line1, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, COL_TEXT)
	var keys := "Tab sprite · M chế độ (%s) · B nền · +/- tỉ lệ" % _mode
	keys += " · A neo/khung/hitbox" if _mode == "sheet" else " · ←→ đi · Shift chạy · Space nhảy · J đánh · K phép · H trúng đòn · X chết · R đặt lại"
	draw_string(font, Vector2(16, 48), keys, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, COL_DIM)


func _draw_sheet(font: Font) -> void:
	var names := _sheet.animation_names()
	var cell := _sheet.frame_size * _scale + Vector2(40, 64)
	var cols := clampi(int((_screen.x - 32) / cell.x), 1, names.size())
	var origin := Vector2(16, 76)
	for i in names.size():
		var anim := names[i]
		var a := _sheet.animation(anim)
		var c := origin + Vector2((i % cols) * cell.x, (i / cols) * cell.y)
		var point := c + Vector2(20, 8) + _sheet.anchor * _scale
		# One-shot animations replay with a short pause so they stay visible.
		var period := _sheet.duration(anim) + (0.0 if bool(a.get("loop", true)) else 0.6)
		var t := fmod(_time, maxf(period, 0.001))
		var idx := _sheet.frame_index(anim, t)
		if _anchors:
			var box := SpriteAnchor.dest_rect(point, _sheet.frame_size, _sheet.anchor, _scale, false)
			draw_rect(box, COL_BOX, false, 1.0)
		draw_line(Vector2(c.x + 8, point.y), Vector2(c.x + cell.x - 16, point.y), COL_GROUND, 1.0)
		_sheet.draw_index(self, idx, point, _scale)
		if _anchors:
			draw_rect(Rect2(point - Vector2(2, 2), Vector2(4, 4)), Color.MAGENTA)
			# hit area from the json: bright on damage frames, faint otherwise
			var body := SpriteHitbox.body(_sheet, point, _scale)
			if body != null:
				body.draw(self, Color(0.3, 1.0, 0.45, 0.8), 1.0)
			var hb := SpriteHitbox.of(_sheet, anim, point, _scale)
			if hb != null:
				var on := hb.is_active(t)
				hb.draw(self, Color(1.0, 0.25, 0.2, 0.95) if on else Color(1.0, 0.6, 0.2, 0.35), 2.0 if on else 1.0)
		var label := "%s  %d/%d  %sfps %s" % [anim, idx - int(a.get("start", 0)) + 1, int(a.get("frames", 1)),
			a.get("fps", 0), "loop" if bool(a.get("loop", true)) else "1 lần"]
		draw_string(font, Vector2(c.x + 12, c.y + cell.y - 22), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, COL_TEXT)


func _draw_move(font: Font) -> void:
	var top_down := not _sheet.has_animation("jump")
	if not top_down:
		draw_line(Vector2(0, GROUND_Y), Vector2(_screen.x, GROUND_Y), COL_GROUND, 2.0)
	var lift := 0.0
	if _jump_t >= 0.0:  # parabola over the jump animation
		lift = sin(PI * _jump_t / maxf(0.001, _sheet.duration("jump"))) * _sheet.frame_size.y * 0.5 * _scale
	var shadow_w := _sheet.frame_size.x * _scale * 0.35 * (1.0 - 0.4 * lift / maxf(1.0, _sheet.frame_size.y * _scale))
	draw_set_transform(_pos, 0.0, Vector2(1.0, 0.3))
	draw_circle(Vector2.ZERO, shadow_w, Color(0, 0, 0, 0.35))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var point := _pos - Vector2(0, lift)
	var anim := _anim_now if _anim_now != "" else _sheet.animation_names()[0]
	_sheet.draw(self, anim, _anim_t, point, _scale, _facing < 0.0)
	draw_rect(Rect2(point - Vector2(2, 2), Vector2(4, 4)), Color.MAGENTA)
	var a := _sheet.animation(anim)
	var idx := _sheet.frame_index(anim, _anim_t) - int(a.get("start", 0)) + 1
	var moment := ""
	if _demo:
		for c in CONTACT_TIMES:
			if fmod(_time, 9.0) >= float(c[0]) - 0.6:
				moment = "  · " + String(c[1])
	var info := "%s  frame %d/%d  · hướng %s%s%s" % [anim, idx, int(a.get("frames", 1)),
		"phải" if _facing > 0.0 else "trái", "  · DEMO" if _demo else "", moment]
	draw_string(font, Vector2(16, _screen.y - 20), info, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, COL_TEXT)
