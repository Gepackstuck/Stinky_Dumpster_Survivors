extends Node
## ТЕСТ: строки подсказок открытия (пишет tools/_preview/hints.txt).


func _ready() -> void:
	var f: FileAccess = FileAccess.open(ProjectSettings.globalize_path("res://tools/_preview/hints.txt"), FileAccess.WRITE)
	for entry: Dictionary in load("res://scripts/systems/unlock_hints.gd").call("locked"):
		f.store_line("%s | %s | %.2f" % [entry["title"], entry["text"], entry["fraction"]])
	f.close()
	get_tree().quit()
