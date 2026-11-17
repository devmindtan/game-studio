extends SceneTree
## Fast screenshots for `gamekit shot`: runs a scene with a fixed 60 fps step
## (deterministic, like the movie writer) but without vsync or real-time waits,
## and saves only the requested frames, several per run.
##
## Run (gamekit does this):
##   godot --path <game> --fixed-fps 60 -s res://addons/gamekit/debug/shot_capture.gd \
##     -- --gk-scene=<res://...tscn> --gk-capture=300,600,900 --gk-out=<dir> [game args]
## Prints one "GK_SHOT <path>" line per saved frame. The game reads its own
## arguments from OS.get_cmdline_user_args() as usual (the --gk-* ones are ignored).

var _frames: Array[int] = []
var _out := ""
var _count := 0
var _size := Vector2i(1280, 720)
var _view: SubViewport


func _initialize() -> void:
	var scene := String(ProjectSettings.get_setting("application/run/main_scene", ""))
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--gk-scene=") and a.get_slice("=", 1) != "":
			scene = a.get_slice("=", 1)
		elif a.begins_with("--gk-capture="):
			for f in a.get_slice("=", 1).split(",", false):
				_frames.append(maxi(1, int(f)))
		elif a.begins_with("--gk-out="):
			_out = a.get_slice("=", 1)
		elif a.begins_with("--gk-size="):
			var wh := a.get_slice("=", 1).split("x")
			_size = Vector2i(int(wh[0]), int(wh[1]))
	_frames.sort()
	if _frames.is_empty() or _out == "" or scene == "":
		push_error("shot_capture: need --gk-capture=<frames>, --gk-out=<dir> and a scene")
		quit(1)
		return
	# The scene renders into a fixed-size SubViewport and that is what we save, so the
	# OS window does not matter. (Capturing the window failed twice: the window manager
	# shrank a decorated 1280x720 window to 1237x696, and later grew it to 1280x728.)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	_view = SubViewport.new()
	_view.size = _size
	_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_view.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST \
		if int(ProjectSettings.get_setting("rendering/textures/canvas_textures/default_texture_filter", 1)) == 0 \
		else Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_LINEAR
	root.add_child(_view)
	var packed: PackedScene = load(scene)
	if packed == null:
		push_error("shot_capture: cannot load %s" % scene)
		quit(1)
		return
	_view.add_child(packed.instantiate())


# Frames are counted in _process (it always runs) and a capture forces a draw.
# Counting on RenderingServer.frame_post_draw hung at random (lesson 2026-11-17):
# when the window was covered or on another workspace Godot skipped drawing, the
# signal never came and the run spun at 100% CPU until the time limit.
func _process(_delta: float) -> bool:
	_count += 1
	if _frames.has(_count):
		RenderingServer.force_draw(false)
		var img := _view.get_texture().get_image()
		if img.get_size() != _size:   # never hand over a scaled screenshot
			printerr("ERROR shot_capture: frame is %s, expected %s" % [img.get_size(), _size])
			quit(1)
			return true
		var path := _out.path_join("%06d.png" % _count)
		img.save_png(path)
		print("GK_SHOT ", path)
	if _count >= _frames[-1]:
		quit()
	return false
