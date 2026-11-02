extends SceneTree
## Пересобрать docs/ACHIEVEMENTS.md из кода (Achievements.all_ids). godot --headless -s res://tools/gen_achievements_doc.gd


func _init() -> void:
	_run.call_deferred()


func _run() -> void:
	var ach: GDScript = load("res://scripts/autoload/achievements.gd")
	var ids: Array = ach.call(&"all_ids")
	var lines: PackedStringArray = ["# Достижения", "", "Собирается из кода скриптом `tools/gen_achievements_doc.gd` - не править руками.",
		"id = API name в Steamworks. Всего: **%d**." % ids.size(), "", "| id | Название | Условие |", "|---|---|---|"]
	for id: StringName in ids:
		var cond: String = ""
		var list: Dictionary = ach.get(&"LIST")
		if list.has(id):
			cond = list[id][1]
		elif String(id).begins_with("nohit_"): cond = "Убей босса, не получив от него урона"
		elif String(id).begins_with("kill500_"): cond = "Убей 500 таких врагов за всё время"
		elif String(id).begins_with("tier4_"): cond = "Доведи это оружие до IV тира"
		elif String(id).begins_with("set_win_"): cond = "Победи с набором из 6 оружий этого класса"
		elif String(id).begins_with("mod_clean_"): cond = "Переживи этот модификатор волны без урона"
		else: cond = "Победи этим героем на этой опасности"
		lines.append("| `%s` | %s | %s |" % [id, ach.call(&"title_of", id), cond])
	var f: FileAccess = FileAccess.open("res://docs/ACHIEVEMENTS.md", FileAccess.WRITE)
	f.store_string("\n".join(lines) + "\n")
	f.close()
	print("ACHIEVEMENTS DOC ", ids.size())
	quit()
