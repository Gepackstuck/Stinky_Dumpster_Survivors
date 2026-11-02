extends Node
## ТЕСТ: структуры пачки 3 против манекена-врага рядом. Лог: tools/_preview/struct_test.txt

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const ENEMY: PackedScene = preload("res://scenes/enemies/enemy_base.tscn")


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	var f: FileAccess = FileAccess.open(ProjectSettings.globalize_path("res://tools/_preview/struct_test.txt"), FileAccess.WRITE)
	for id: StringName in [&"stink_lamp", &"bottle_mine", &"cart_mortar", &"bomber_pigeon", &"stray_dog"]:
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		await get_tree().create_timer(0.5).timeout
		get_tree().paused = false
		GameState.weapons.clear()
		GameState.items.clear()
		GameState.add_item(id)
		EventBus.wave_started.emit(GameState.wave)
		await get_tree().create_timer(0.3).timeout
		var comp: Node2D = get_tree().get_nodes_in_group(&"companions")[0] as Node2D
		var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		var enemy: EnemyBase = ENEMY.instantiate() as EnemyBase
		level.get_node("Enemies").add_child(enemy)
		enemy.setup(player, comp.global_position + Vector2(18.0, 0.0), &"bruiser", 1.0)
		var health: HealthComponent = enemy.get_node("HealthComponent") as HealthComponent
		var hp0: float = health.current_health
		var start_dist: float = comp.global_position.distance_to(player.global_position)
		await get_tree().create_timer(3.0).timeout
		f.store_line("%s: враг hp %.0f -> %.0f (жив=%s) дист до героя при старте %.0f, компаньон жив=%s" % [id, hp0, health.current_health, is_instance_valid(enemy) and enemy.is_inside_tree(), start_dist, is_instance_valid(comp)])
		if id == &"bomber_pigeon":
			f.store_line("  pigeon: bomb_left=%s anim=%s orbit=%s pos=%s player=%s enemy=%s" % [comp.get("_bomb_left"), comp.get("_anim"), comp.get("_orbit"), comp.global_position, player.global_position, enemy.global_position])
		f.flush()
		level.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	f.store_line("DONE")
	f.close()
	get_tree().quit()
