extends Node
## Новая пиксельная: герой крупно, идёт вправо/вверх/вниз (без врагов). tools/_preview/hd/05_пиксели/в_игре/герой_*.png. Оконный режим.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	Settings.art_style = "new"
	ArtStyle.apply_ui()
	_run.call_deferred()


func _run() -> void:
	GameState.character = &"hobo"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(1.5).timeout
	level.get_node(^"LevelUpScreen").call(&"_on_card_pressed", 0)
	await get_tree().create_timer(1.7).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	player.get_node(^"Hurtbox").grant_invulnerability(30.0)
	for act: StringName in [&"move_right", &"move_up", &"move_down"]:
		Input.action_press(act)
		await get_tree().create_timer(0.5).timeout
		await RenderingServer.frame_post_draw
		var img: Image = get_viewport().get_texture().get_image()
		var c: Vector2i = img.get_size() / 2
		img.get_region(Rect2i(c.x - 260, c.y - 200, 520, 400)).save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/05_пиксели/в_игре/герой_%s.png" % act))
		Input.action_release(act)
	print("HERO DONE")
	get_tree().quit()
