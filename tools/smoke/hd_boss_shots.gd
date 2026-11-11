extends Node
## Реалистичный стиль: кадры с боссом (мусорный голем), баками и опытом. tools/_preview/hd/boss_N.png. Оконный режим.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	Settings.art_style = "new"   # только на этот запуск, в настройки не пишется
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
	var hb: HurtboxComponent = player.get_node(^"Hurtbox")
	EnemyBase.spawn_enemy(level.get_node(^"Enemies"), player, &"boss_trash_golem", player.global_position + Vector2(110.0, -20.0), 3.0)
	for k: int in 6:
		EnemyBase.spawn_enemy(level.get_node(^"Enemies"), player, &"squid_gopnik", player.global_position + Vector2.from_angle(k * 1.1 + 2.0) * 120.0, 3.0)
	for i: int in 40:
		hb.grant_invulnerability(1.0)
		await get_tree().create_timer(0.2).timeout
		if i in [6, 14, 22, 30, 38]:
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/03_в_игре/boss_%d.png" % i))
	print("HD BOSS DONE")
	get_tree().quit()
