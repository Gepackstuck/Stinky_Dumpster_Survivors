extends Node
## Дымовой тест: каждый персонаж + все предметы, игра на ускорении. Запуск: сцена tools/smoke/smoke_test.tscn.
## Ошибки смотреть в консоли Godot. В конце печатает SMOKE DONE.

# Слотов 6: лишние оружия просто не добавятся.
const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Engine.time_scale = 4.0
	_run.call_deferred()


func _run() -> void:
	var offset: int = 0
	for id: StringName in Balance.CHARACTER_ORDER:
		print("SMOKE character ", id)
		GameState.character = id
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		await get_tree().create_timer(0.6).timeout
		if GameState.weapons.is_empty():
			GameState.apply_perk(&"w_mop")
		get_tree().paused = false
		var pool: Array = Balance.WEAPONS.keys().filter(func(w: StringName) -> bool: return w != &"turret")
		GameState.weapons.clear()
		for k: int in Balance.WEAPON_SLOTS:
			GameState.add_weapon(pool[(offset + k) % pool.size()], 1 + randi() % 4)   # каждому герою своя шестёрка оружий
		offset += Balance.WEAPON_SLOTS
		for item_id: StringName in Balance.ITEMS:
			GameState.add_item(item_id)
		await get_tree().create_timer(6.0).timeout
		print("SMOKE wave ", GameState.wave, " hp ", GameState.hp, " kills ", GameState.kills)
		EventBus.wave_ended.emit(GameState.wave)
		await get_tree().create_timer(1.0).timeout
		get_tree().paused = false
		level.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	print("SMOKE DONE")
	get_tree().quit()
