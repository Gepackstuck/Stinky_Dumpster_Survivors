extends Node
## Кадры сочности боя: стрелялки и швабра против толпы, герой неуязвим. tools/_preview/juice_N.png (кроп центра ×2).

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	_run.call_deferred()


func _run() -> void:
	GameState.character = &"guard"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.2).timeout
	get_tree().paused = false
	GameState.weapons.clear()
	for w: Array in [[&"mosin", 2], [&"pipe_gun", 2], [&"mop", 3], [&"crossbow", 1], [&"tin_bomb", 2]]:
		GameState.add_weapon(w[0], w[1])
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	var hb: HurtboxComponent = player.get_node(^"Hurtbox")
	for k: int in 14:
		EnemyBase.spawn_enemy(level.get_node(^"Enemies"), player, [&"squid_gopnik", &"chaser", &"spitter", &"bruiser"][k % 4], player.global_position + Vector2.from_angle(k * 0.45) * randf_range(50.0, 95.0), 1.0)
	for i: int in 30:
		hb.grant_invulnerability(1.0)
		GameState.xp = 0
		await get_tree().create_timer(0.12).timeout
		if i in [8, 14, 20, 26]:
			await RenderingServer.frame_post_draw
			var img: Image = get_viewport().get_texture().get_image()
			var c: Vector2 = img.get_size() * 0.5
			var crop: Image = img.get_region(Rect2i(int(c.x) - 160, int(c.y) - 90, 320, 180))
			crop.resize(640, 360, Image.INTERPOLATE_NEAREST)
			crop.save_png(ProjectSettings.globalize_path("res://tools/_preview/juice_%d.png" % i))
	print("JUICE DONE")
	get_tree().quit()
