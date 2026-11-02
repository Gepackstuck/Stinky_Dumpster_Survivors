extends Node
## ТЕСТ: каждый питомец/структура пачки 3 (по 2 штуки) без оружия: убийства за 10 с волны 1 (x4). Лог: tools/_preview/companion_test.txt

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const IDS: Array[StringName] = [&"stink_lamp", &"bottle_mine"]


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	Engine.time_scale = 4.0
	_run.call_deferred()


func _run() -> void:
	var f: FileAccess = FileAccess.open(ProjectSettings.globalize_path("res://tools/_preview/companion_test.txt"), FileAccess.WRITE)
	for id: StringName in IDS:
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		await get_tree().create_timer(0.6).timeout
		get_tree().paused = false
		GameState.weapons.clear()
		GameState.items.clear()
		GameState.add_item(id)
		GameState.add_item(id)
		GameState.hp = 500.0
		EventBus.wave_started.emit(GameState.wave)   # питомцы появляются на старте волны
		await get_tree().create_timer(0.3).timeout
		var kills0: int = GameState.kills
		await get_tree().create_timer(5.0).timeout
		for c: Node in get_tree().get_nodes_in_group(&"companions"):
			var near: int = 0
			for e: Node in get_tree().get_nodes_in_group(&"enemies"):
				if (e as Node2D).global_position.distance_to((c as Node2D).global_position) < 70.0:
					near += 1
			f.store_line("  %s dmg=%s cd=%s radius=%s near=%d enemies=%d" % [c.get_script().resource_path.get_file(), c.get("_damage"), c.get("_cooldown_left"), c.get("_radius"), near, get_tree().get_nodes_in_group(&"enemies").size()])
		await get_tree().create_timer(5.0).timeout
		f.store_line("%s: компаньонов %d убито %d хп %d" % [id, get_tree().get_nodes_in_group(&"companions").size(), GameState.kills - kills0, roundi(GameState.hp)])
		f.flush()
		level.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	f.store_line("DONE")
	f.close()
	get_tree().quit()
