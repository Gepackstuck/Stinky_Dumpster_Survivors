extends Node
## Кадры: медали опасности на могилах и окно выбора опасности. tools/_preview/danger_*.png (профиль не сохраняется).

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	Profile.danger_unlocked = 3
	Profile.hero_wins = {&"hobo": [0, 1, 2], &"squid": [0], &"clerk": [0, 1, 2, 3, 4, 5], &"janitor": [0, 1]}
	_run.call_deferred()


func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/danger_%s.png" % n))


func _run() -> void:
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(2.5).timeout
	await _shot("graves")
	for hero: int in [3, 16, 8]:
		yard.call("_select", hero)
		await get_tree().create_timer(0.2).timeout
		await _shot("dossier_%d" % hero)
	yard.call("_choose")
	await get_tree().create_timer(0.3).timeout
	yard.set("_pick_danger", 2)
	yard.call("_refresh_picker")
	await get_tree().create_timer(0.2).timeout
	await _shot("picker")
	print("DANGER SHOTS DONE")
	get_tree().quit()
