extends Node
## Сам прогон цикла экранов (живёт в корне, переживает смену сцен).


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	await get_tree().create_timer(1.5).timeout
	print("FLOW menu: ", get_tree().current_scene.name)
	SceneFlow.go("res://scenes/ui/graveyard.tscn", Vector2.DOWN)
	await get_tree().create_timer(1.2).timeout
	print("FLOW graveyard: ", get_tree().current_scene.name)
	var book: Control = preload("res://scripts/ui/weapon_book.gd").new()
	get_tree().current_scene.add_child(book)
	await get_tree().create_timer(0.5).timeout
	book.queue_free()
	GameState.character = &"hobo"
	SceneFlow.go("res://scenes/levels/main.tscn", Vector2.DOWN)
	await get_tree().create_timer(3.0).timeout
	print("FLOW arena: ", get_tree().current_scene.name)
	SceneFlow.go("res://scenes/ui/graveyard.tscn", Vector2.UP)
	await get_tree().create_timer(1.2).timeout
	print("FLOW back: ", get_tree().current_scene.name)
	SceneFlow.go("res://scenes/ui/main_menu.tscn", Vector2.UP)
	await get_tree().create_timer(1.2).timeout
	print("FLOW DONE ", get_tree().current_scene.name)
	get_tree().quit()
