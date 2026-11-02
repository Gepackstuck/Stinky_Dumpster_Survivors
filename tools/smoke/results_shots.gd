extends Node
## Кадры экрана итога: смерть и победа с подставными данными. tools/_preview/results_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	_run.call_deferred()


func _fake() -> void:
	GameState.kills = 412
	GameState.level = 14
	GameState.wave = 11
	GameState.danger = 2
	GameState.damage_by_source = {&"mop": 5400.0, &"slingshot": 3100.0, &"pets": 900.0, &"thorns": 300.0, &"dash": 120.0, &"other": 40.0}
	GameState.hp_history.clear()
	GameState.hp_wave_marks.clear()
	for i: int in 400:
		if i % 40 == 0:
			GameState.hp_wave_marks.append(i)
		GameState.hp_history.append(clampf(0.75 + 0.25 * sin(i * 0.05) - i * 0.0015, 0.05, 1.0))
	GameState.last_damage_source = &"spitter"
	GameState.seed_word = "ВАСЯ"   # строка режима и сида внизу панели


func _run() -> void:
	for mode: String in ["death", "win"]:
		GameState.character = &"janitor"
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		get_tree().current_scene = level
		await get_tree().create_timer(0.8).timeout
		_fake()
		if mode == "death":
			level.get_node(^"DeathScreen").call("_show_result", "СДОХ КАК ЛОХ. ОПЯТЬ", true)
		else:
			level.get_node(^"DeathScreen").call("_on_run_won")
		await get_tree().create_timer(0.4).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/results_%s.png" % mode))
		get_tree().paused = false
		level.queue_free()
		await get_tree().process_frame
	print("RESULTS DONE")
	get_tree().quit()
