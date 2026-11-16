extends Node2D
## Dev-only viewer for ingested LPC characters (excluded from exports).
##
## Top row: the character in all four facings, cycling through every action.
## Below: a playable copy - arrows/WASD walk, Shift run, J slash, K thrust,
## L spellcast, U shoot, H hurt. Tab switches character.
##
## Run: gamekit preview <game> [<character>]
##   or godot --path <game> res://addons/gamekit/debug/character_viewer.tscn -- --character=<name>

const CHARACTERS_DIR := "res://assets/sprites/characters"
const SCALE := 3.0
const WALK_SPEED := 150.0
const RUN_SPEED := 260.0
const SHOWCASE_SECONDS := 2.0

var _names: PackedStringArray = []
var _index := 0
var _showcase: Array[LpcCharacter] = []
var _actions: PackedStringArray = []
var _action_i := 0
var _action_t := 0.0
var _player: LpcCharacter
var _busy := false  # a one-shot action is playing
var _screen: Vector2


func _ready() -> void:
	_screen = get_viewport_rect().size
	var dir := DirAccess.open(CHARACTERS_DIR)
	if dir:
		for n in dir.get_directories():
			if ResourceLoader.exists(_frames_path(n)):
				_names.append(n)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--character="):
			_index = maxi(0, _names.find(arg.trim_prefix("--character=")))
	for i in 4:
		var c := LpcCharacter.new()
		c.scale = Vector2.ONE * SCALE
		c.position = Vector2(_screen.x * (0.2 + 0.2 * i), 170.0)
		c.facing = LpcCharacter.FACINGS[i]
		add_child(c)
		_showcase.append(c)
	_player = LpcCharacter.new()
	_player.scale = Vector2.ONE * SCALE
	_player.position = Vector2(_screen.x * 0.5, _screen.y * 0.68)
	_player.animation_finished.connect(func() -> void: _busy = false)
	add_child(_player)
	_load_character()


func _frames_path(n: String) -> String:
	return CHARACTERS_DIR.path_join("%s/%s_frames.tres" % [n, n])


func _load_character() -> void:
	if _names.is_empty():
		return
	var frames: SpriteFrames = load(_frames_path(_names[_index]))
	var seen := {}
	_actions.clear()
	for a in frames.get_animation_names():
		var base := String(a)
		for f in LpcCharacter.FACINGS:
			base = base.trim_suffix("_" + String(f))
		if not seen.has(base):
			seen[base] = true
			_actions.append(base)
	for c in _showcase:
		c.sprite_frames = frames
	_player.sprite_frames = frames
	_action_i = maxi(0, _actions.find("walk"))
	_action_t = 0.0
	_play_showcase()
	_player.play_action(&"idle")


func _play_showcase() -> void:
	for c in _showcase:
		c.play_action(StringName(_actions[_action_i]))
		c.frame = 0


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_TAB:
				if not _names.is_empty():
					_index = (_index + 1) % _names.size()
					_load_character()
			KEY_J: _one_shot(&"slash")
			KEY_K: _one_shot(&"thrust")
			KEY_L: _one_shot(&"spellcast")
			KEY_U: _one_shot(&"shoot")
			KEY_H: _one_shot(&"hurt")
			KEY_ESCAPE: get_tree().quit()


func _one_shot(action: StringName) -> void:
	if _player.play_action(action):
		_player.frame = 0
		_busy = true


func _process(delta: float) -> void:
	if _names.is_empty():
		queue_redraw()
		return
	_action_t += delta
	if _action_t >= SHOWCASE_SECONDS:
		_action_t = 0.0
		_action_i = (_action_i + 1) % _actions.size()
		_play_showcase()
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if Input.is_physical_key_pressed(KEY_A): dir.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D): dir.x += 1.0
	if Input.is_physical_key_pressed(KEY_W): dir.y -= 1.0
	if Input.is_physical_key_pressed(KEY_S): dir.y += 1.0
	dir = dir.limit_length(1.0)
	if not _busy:
		var running := Input.is_physical_key_pressed(KEY_SHIFT)
		if dir != Vector2.ZERO:
			_player.face(dir)
			_player.play_action(&"run" if running else &"walk")
			_player.position += dir * (RUN_SPEED if running else WALK_SPEED) * delta
			_player.position = _player.position.clamp(Vector2(40, 330), _screen - Vector2(40, 40))
		else:
			_player.play_action(&"idle")
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, _screen), Color(0.16, 0.22, 0.18))
	draw_rect(Rect2(0, 300, _screen.x, _screen.y - 300), Color(0.24, 0.36, 0.22))
	var font := ThemeDB.fallback_font
	if _names.is_empty():
		draw_string(font, Vector2(40, 80), "Chưa có nhân vật. Chạy: gamekit sprites <game>", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color.WHITE)
		return
	var title := "%s  —  %s   (%d/%d, Tab: đổi nhân vật)" % [_names[_index], _actions[_action_i], _index + 1, _names.size()]
	draw_string(font, Vector2(24, 40), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.WHITE)
	for i in 4:
		draw_string(font, Vector2(_showcase[i].position.x - 40, 290), String(LpcCharacter.FACINGS[i]),
			HORIZONTAL_ALIGNMENT_CENTER, 80, 16, Color(1, 1, 1, 0.7))
	draw_string(font, Vector2(24, _screen.y - 20),
		"Mũi tên/WASD đi · Shift chạy · J chém · K đâm · L phép · U bắn · H bị đánh · Esc thoát",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(1, 1, 1, 0.8))
