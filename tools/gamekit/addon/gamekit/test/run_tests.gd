extends SceneTree
## Minimal headless test runner (no gdUnit4 needed).
## Usage: gamekit test <game>   (or: godot --headless --path <game> -s res://addons/gamekit/test/run_tests.gd)
## Runs every `test_*` method in every `*_test.gd` under res://tests (unit + integration),
## prints PASS/FAIL per test and exits with code 1 on any failure.


func _init() -> void:
	var files: Array[String] = []
	_collect("res://tests", files)
	var passed := 0
	var failed := 0
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
			suite.call(name)
			var errs: Array = suite.get("failures")
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
