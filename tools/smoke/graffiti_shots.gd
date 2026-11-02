extends Node
## Н30: граффити на краю арены. Кадр у верхнего края: tools/_preview/graffiti_1.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	Profile.graffiti = [{"hero": "granny", "wave": 12, "x": 400.0, "y": 400.0}, {"hero": "uncle_vitya", "wave": 7, "x": 230.0, "y": 300.0}]
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.4).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	(player.get(&"_health") as HealthComponent).setup(99999.0)
	player.global_position = Vector2(260.0, 280.0)
	await get_tree().create_timer(0.6).timeout
	var n: int = level.find_children("*", "Graffiti", true, false).front().get_child_count()
	print("GRAFFITI ", "OK" if n == 2 else "FAIL %d" % n)
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/graffiti_1.png"))
	get_tree().quit()
