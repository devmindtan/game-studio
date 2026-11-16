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
	_frames.sort()
	if _frames.is_empty() or _out == "" or scene == "":
		push_error("shot_capture: need --gk-capture=<frames>, --gk-out=<dir> and a scene")
		quit(1)
		return
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	change_scene_to_file(scene)
	RenderingServer.frame_post_draw.connect(_on_frame_drawn)


func _on_frame_drawn() -> void:
	_count += 1
	if _frames.has(_count):
		var path := _out.path_join("%06d.png" % _count)
		root.get_texture().get_image().save_png(path)
		print("GK_SHOT ", path)
	if _count >= _frames[-1]:
		quit()
