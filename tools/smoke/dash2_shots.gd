extends Node
## Кадры: старческий пердёж вместо рывка (бабка, шанс 100% в тесте) и труба сантехника. tools/_preview/dash2_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	var img: Image = get_viewport().get_texture().get_image()
	var c: Vector2 = img.get_size() * 0.5
	var crop: Image = img.get_region(Rect2i(int(c.x) - 120, int(c.y) - 70, 240, 140))
	crop.resize(480, 280, Image.INTERPOLATE_NEAREST)
	crop.save_png(ProjectSettings.globalize_path("res://tools/_preview/dash2_%s.png" % n))


func _run() -> void:
	for hero: StringName in [&"granny", &"plumber"]:
		GameState.character = hero
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		get_tree().current_scene = level
		await get_tree().create_timer(3.2).timeout
		get_tree().paused = false
		for k: int in 2:   # рывок - обувь из Ларька: обуваем героя
			GameState.add_item(ItemLibrary.SHOES)
		var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		var dash: Node = player.get_node(^"Dash")
		if hero == &"granny":
			dash.get("_p")["fart"] = 1.0
		for k: int in 6:
			EnemyBase.spawn_enemy(level.get_node(^"Enemies"), player, &"squid_gopnik", player.global_position + Vector2.from_angle(k) * 30.0, 1.0)
		await get_tree().create_timer(0.3).timeout
		Input.action_press(&"move_right")
		Input.action_press(&"dash")
		await get_tree().physics_frame
		Input.action_release(&"dash")
		await get_tree().create_timer(0.1).timeout
		await _shot("%s_a" % hero)
		await get_tree().create_timer(0.12).timeout
		await _shot("%s_b" % hero)
		Input.action_release(&"move_right")
		level.queue_free()
		await get_tree().process_frame
	get_tree().quit()
