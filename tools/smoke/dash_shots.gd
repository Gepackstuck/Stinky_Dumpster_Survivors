extends Node
## Кадры рывка: герой со скейтом бежит и рвётся (послеобразы, шкала в HUD), потом упирается во врага. tools/_preview/dash_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _shot(n: int) -> void:
	await RenderingServer.frame_post_draw
	var img: Image = get_viewport().get_texture().get_image()
	var c: Vector2 = img.get_size() * 0.5
	var crop: Image = img.get_region(Rect2i(int(c.x) - 120, int(c.y) - 70, 240, 140))
	crop.resize(480, 280, Image.INTERPOLATE_NEAREST)
	crop.save_png(ProjectSettings.globalize_path("res://tools/_preview/dash_%d.png" % n))
	img.get_region(Rect2i(0, 0, img.get_width() / 2, img.get_height() / 6)).save_png(ProjectSettings.globalize_path("res://tools/_preview/dash_hud_%d.png" % n))


func _run() -> void:
	GameState.character = &"skater"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.5).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	Input.action_press(&"move_right")
	await get_tree().create_timer(0.3).timeout
	Input.action_press(&"dash")
	await get_tree().physics_frame
	Input.action_release(&"dash")
	await get_tree().create_timer(0.08).timeout
	await _shot(1)
	await get_tree().create_timer(0.15).timeout
	await _shot(2)
	Input.action_release(&"move_right")
	EnemyBase.spawn_enemy(level, player, &"bruiser", player.global_position + Vector2(30.0, 0.0), 1.0)
	await get_tree().create_timer(1.3).timeout
	Input.action_press(&"move_right")
	Input.action_press(&"dash")
	await get_tree().physics_frame
	Input.action_release(&"dash")
	await get_tree().create_timer(0.12).timeout
	await _shot(3)
	Input.action_release(&"move_right")
	print("DASH SHOTS DONE")
	get_tree().quit()
