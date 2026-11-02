extends Node
## Живое кладбище: у героев разное число смертей - грибы, мухи, памятник. tools/_preview/grave_life_*.png

func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	var deaths: Array[int] = [0, 1, 3, 6, 10, 30, 12, 2, 5]
	for i: int in deaths.size():
		Profile.stats[StringName("deaths_" + String(Balance.CHARACTER_ORDER[i]))] = deaths[i]
	for d: int in 6:   # шапки-трофеи: у первых героев победы на разных опасностях
		Profile.hero_wins[Balance.CHARACTER_ORDER[d]] = range(d + 1)
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(1.0).timeout
	if DisplayServer.get_name() != "headless":   # без окна кадр не рисуется - ждать нечего
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/grave_life_1.png"))
	print("GRAVE LIFE DONE")
	get_tree().quit()
