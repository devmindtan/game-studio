extends SceneTree
## Minimal headless test runner (no gdUnit4 needed).
## Usage: gamekit test <game>   (or: godot --headless --path <game> -s res://addons/gamekit/test/run_tests.gd)
## Loads every script under res://src (a parse error fails the run), then
## runs every `test_*` method in every `*_test.gd` under res://tests (unit + integration),
## prints PASS/FAIL per test and exits with code 1 on any failure.
## A test stopped by a script error (bad call, out-of-range index) fails too: before, it returned early with no
## failures recorded and printed PASS (lesson 2026-11-23).


class _ScriptErrors extends Logger:
	var count := 0
	var last := ""

	func _log_error(function: String, file: String, line: int, code: String, rationale: String,
			_editor_notify: bool, error_type: int, _backtraces: Array[ScriptBacktrace]) -> void:
		if error_type == Logger.ERROR_TYPE_SCRIPT:
			count += 1
			last = "%s (%s:%d %s)" % [rationale if rationale != "" else code, file.get_file(), line, function]


func _init() -> void:
	var files: Array[String] = []
	_collect("res://tests", files)
	var passed := 0
	var failed := 0
	var script_errors := _ScriptErrors.new()
	OS.add_logger(script_errors)
	# Every game script must at least parse, even when no test touches it
	# (lesson 2026-11-16: tests passed while the run scene had a parse error).
	var sources: Array[String] = []
	_collect_ext("res://src", ".gd", sources)
	for path in sources:
		var src: GDScript = load(path)
		if src == null or not src.can_instantiate():
			failed += 1
			print("FAIL  %s — game script does not load (parse error?)" % path)
		else:
			passed += 1
	for path in files:
		var script: GDScript = load(path)
		if script == null or not script.can_instantiate():
			failed += 1
			print("FAIL  %s — script does not load (parse error?)" % path.get_file())
			continue
		for method in script.get_script_method_list():
			var name: String = method["name"]
			if not name.begins_with("test_"):
				continue
			var suite: Object = script.new()
			var before := script_errors.count
			suite.call(name)
			var errs: Array = (suite.get("failures") as Array).duplicate()
			if script_errors.count > before:
				errs.append("script error: " + script_errors.last)
			if errs.is_empty():
				passed += 1
				print("PASS  %s::%s" % [path.get_file(), name])
			else:
				failed += 1
				print("FAIL  %s::%s — %s" % [path.get_file(), name, "; ".join(errs)])
	print("\n%d passed, %d failed" % [passed, failed])
	quit(1 if failed > 0 else 0)


func _collect(dir_path: String, out: Array[String]) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	for sub in dir.get_directories():
		_collect(dir_path.path_join(sub), out)
	for f in dir.get_files():
		if f.ends_with("_test.gd"):
			out.append(dir_path.path_join(f))


func _collect_ext(dir_path: String, ext: String, out: Array[String]) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	for sub in dir.get_directories():
		_collect_ext(dir_path.path_join(sub), ext, out)
	for f in dir.get_files():
		if f.ends_with(ext):
			out.append(dir_path.path_join(f))
