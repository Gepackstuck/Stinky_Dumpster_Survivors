extends Node
## Прогон цикла экранов (живёт в корне, переживает смену сцен). Кадры кладёт в tools/_preview/flow_*.png.


func _ready() -> void:
	_run.call_deferred()


func _shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/flow_%s.png" % label))


func _run() -> void:
	await get_tree().create_timer(1.0).timeout
	_shot("menu")
	SceneFlow.go("res://scenes/ui/graveyard.tscn", Vector2.DOWN)
	await get_tree().create_timer(1.0).timeout
	print("FLOW graveyard: ", get_tree().current_scene.name)
	_shot("graveyard")
	var book: Control = preload("res://scripts/ui/weapon_book.gd").new()
	get_tree().current_scene.add_child(book)
	await get_tree().create_timer(0.4).timeout
	_shot("book")
	book.queue_free()
	GameState.character = &"hobo"
	SceneFlow.go("res://scenes/levels/main.tscn", Vector2.UP)
	await get_tree().create_timer(0.3).timeout
	_shot("transition")
	await get_tree().create_timer(2.5).timeout
	print("FLOW arena: ", get_tree().current_scene.name)
	get_tree().paused = false
	await get_tree().create_timer(1.2).timeout
	var pause: Node = get_tree().current_scene.find_child("PauseMenu", true, false)
	if pause != null:
		pause.call("_open")
		await get_tree().create_timer(0.2).timeout
		_shot("pause")
		await get_tree().create_timer(0.2).timeout
		pause.call("_close")
	EventBus.run_won.emit()
	get_tree().paused = false
	await get_tree().create_timer(0.5).timeout
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	player.global_position = Vector2(260.0, 300.0)
	_shot("gate_arena")
	player.global_position = Vector2(260.0, 516.0)
	await get_tree().create_timer(0.3).timeout
	_shot("to_graveyard")
	await get_tree().create_timer(0.9).timeout
	print("FLOW back: ", get_tree().current_scene.name)
	_shot("arrival")
	await get_tree().create_timer(1.6).timeout
	_shot("arrived")
	SceneFlow.go("res://scenes/ui/main_menu.tscn", Vector2.UP)
	await get_tree().create_timer(1.0).timeout
	print("FLOW DONE ", get_tree().current_scene.name)
	get_tree().quit()
