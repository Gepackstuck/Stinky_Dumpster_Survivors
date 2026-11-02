extends Node
## Н31: экраны битвы героев после 1-го и 2-го раунда. tools/_preview/duel_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	GameState.mode = &"duel"
	GameState.duel_scores = []
	GameState.seed_word = "ВАСЯ42"
	GameState.character = &"granny"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(1.0).timeout
	for r: int in 2:
		GameState.character = [&"granny", &"skater"][r]
		GameState.kills = [312, 280][r]
		GameState.wave = 5
		var ds: DuelScreen = level.find_children("*", "DuelScreen", true, false).front() as DuelScreen
		if r == 1:
			ds = DuelScreen.new()
			level.add_child(ds)
		EventBus.duel_round_over.emit()
		await get_tree().create_timer(0.3).timeout
		if DisplayServer.get_name() != "headless":
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/duel_%d.png" % (r + 1)))
	print("DUEL ", "OK" if GameState.duel_scores.size() >= 2 else "FAIL")
	get_tree().quit()
