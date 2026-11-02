extends Node
## Боссы: по очереди спавним на игроке, 14 с, печатаем смены ряда анимации. В конце BOSS DONE.
const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	Engine.time_scale = 2.0
	_run.call_deferred()


func _run() -> void:
	for id: StringName in [&"boss_mega_hamster", &"boss_zakhar", &"boss_minion", &"boss_rat_queen", &"boss_blue_whale"]:
		print("BOSS ", id)
		GameState.character = &"hobo"
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		await get_tree().create_timer(0.6).timeout
		get_tree().paused = false
		var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		EnemyBase.spawn_enemy(level, player, id, player.global_position + Vector2(90.0, 0.0), 1.0)
		await get_tree().process_frame
		var boss: EnemyBase = null
		for n: Node in get_tree().get_nodes_in_group(&"enemies"):
			if (n as EnemyBase).enemy_id == id:
				boss = n as EnemyBase
		var last: int = -1
		for i: int in 60:
			GameState.hp = GameState.max_hp
			await get_tree().create_timer(0.25).timeout
			if boss == null or not is_instance_valid(boss):
				break
			var row: int = boss.get_node("FrameAnimator").row
			if i == 30:
				boss._health.current_health = boss._health.max_health * 0.4   # включить ярость
			if row != last:
				print("  t=", i * 0.25, " row ", row)
				last = row
		level.queue_free()
		await get_tree().process_frame
	print("BOSS DONE")
	get_tree().quit()
