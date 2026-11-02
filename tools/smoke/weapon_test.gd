extends Node
## ТЕСТ: каждое оружие пачки 3 в одиночку на волне 3 (8 с на x4): печатает убийства и уроны. Лог: tools/_preview/weapon_test.txt


const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const IDS: Array[StringName] = [&"plunger", &"shiv", &"shovel", &"blowtorch", &"syringe", &"tin_bomb", &"extension_cord"]


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	Engine.time_scale = 4.0
	_run.call_deferred()


func _run() -> void:
	var f: FileAccess = FileAccess.open(ProjectSettings.globalize_path("res://tools/_preview/weapon_test.txt"), FileAccess.WRITE)
	for id: StringName in IDS:
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		await get_tree().create_timer(0.6).timeout
		get_tree().paused = false
		GameState.weapons.clear()
		GameState.add_weapon(id, 1)
		GameState.hp = GameState.max_hp
		var kills0: int = GameState.kills
		await get_tree().create_timer(8.0).timeout
		f.store_line("%s: волна %d убито %d хп %d/%d" % [id, GameState.wave, GameState.kills - kills0, roundi(GameState.hp), roundi(GameState.max_hp)])
		f.flush()
		level.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	f.store_line("DONE")
	f.close()
	get_tree().quit()
