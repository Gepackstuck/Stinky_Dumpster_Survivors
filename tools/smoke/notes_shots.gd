extends Node
## Н17: записки от бомжей на кладбище. Кадр tools/_preview/notes_1.png, печатает NOTES OK (прогресс и награда работают).

func _ready() -> void:
	Profile.sandbox = true
	_run.call_deferred()


func _run() -> void:
	Profile.quests = [{"kind": "kill", "enemy": "cockroach", "hero": "granny", "got": 120, "need": 200, "reward": 5},
			{"kind": "kill_hero", "enemy": "spitter", "hero": "granny", "got": 30, "need": 50, "reward": 8},
			{"kind": "wave_hero", "enemy": "chaser", "hero": "uncle_vitya", "got": 6, "need": 12, "reward": 10}]
	GameState.character = &"granny"
	for i: int in 80:
		Quests.on_kill(&"cockroach")
	var bones0: int = Profile.bones
	var text: String = Quests.on_run_end(false)
	var ok: bool = Profile.bones == bones0 + 5 and text != "" and Profile.quests.size() == 3
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(0.6).timeout
	yard.call("_toggle_notes")
	await get_tree().create_timer(0.3).timeout
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/notes_1.png"))
	print("NOTES OK" if ok else "NOTES FAIL")
	get_tree().quit()
