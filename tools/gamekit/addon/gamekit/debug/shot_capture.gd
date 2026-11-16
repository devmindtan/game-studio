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
	# A decorated window on a small screen is shrunk by the window manager (a 1280x720
	# request came out 1237x696, scaling the whole game): borderless at (0, 0), exact size.
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
	DisplayServer.window_set_position(Vector2i.ZERO)
	DisplayServer.window_set_size(_size)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	change_scene_to_file(scene)
	RenderingServer.frame_post_draw.connect(_on_frame_drawn)


func _on_frame_drawn() -> void:
	_count += 1
	if _frames.has(_count):
		var img := root.get_texture().get_image()
		if img.get_size() != _size:   # never hand over a scaled screenshot
			printerr("ERROR shot_capture: frame is %s, expected %s (window could not be sized)" % [img.get_size(), _size])
			quit(1)
			return
		var path := _out.path_join("%06d.png" % _count)
		img.save_png(path)
		print("GK_SHOT ", path)
	if _count >= _frames[-1]:
		quit()
