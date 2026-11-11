extends Node
## Реалистичный стиль: кадр всего экрана в толпе (40 врагов, 5 стволов, крысы): проверка читаемости. tools/_preview/crowd_N.png. Оконный режим.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	Settings.art_style = "real"   # только на этот запуск, в настройки не пишется
	ArtStyle.apply_ui()
	_run.call_deferred()


func _run() -> void:
	GameState.character = &"hobo"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(1.5).timeout
	level.get_node(^"LevelUpScreen").call(&"_on_card_pressed", 0)   # у бомжа нет стартового оружия: берём первое
	await get_tree().create_timer(1.7).timeout
	get_tree().paused = false
	GameState.weapons.clear()
	for w: Array in [[&"mosin", 2], [&"pipe_gun", 2], [&"mop", 3], [&"crossbow", 2], [&"lighter", 2]]:
		GameState.add_weapon(w[0], w[1])
	GameState.items[&"dead_rat"] = 3
	EventBus.items_changed.emit()
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	var hb: HurtboxComponent = player.get_node(^"Hurtbox")
	var ids: Array[StringName] = [&"squid_gopnik", &"chaser", &"microbe", &"spitter"]   # пока только перерисованные
	for k: int in 40:
		EnemyBase.spawn_enemy(level.get_node(^"Enemies"), player, ids[k % ids.size()], player.global_position + Vector2.from_angle(k * 0.37) * randf_range(60.0, 170.0), 12.0)
	for i: int in 24:
		hb.grant_invulnerability(1.0)
		GameState.xp = 0
		await get_tree().create_timer(0.15).timeout
		if i in [6, 14, 22]:
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/crowd_%d.png" % i))
	print("HD CROWD DONE")
	get_tree().quit()
