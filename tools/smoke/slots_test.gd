extends Node
## ТЕСТ слотов оружия: бонусы наборов по классам, свойства тиров, слияние; кадры HUD, Ларька и паузы
## в tools/_preview/slots_*.png (без окна, с --headless, только проверки). В конце печатает SLOTS OK / SLOTS FAIL.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _fails: int = 0


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print("SLOTS ", "ok   " if ok else "FAIL ", what)
	if not ok:
		_fails += 1


func _shot(label: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/slots_%s.png" % label))


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	await get_tree().create_timer(0.5).timeout
	get_tree().paused = false
	GameState.weapons.clear()
	EventBus.weapons_changed.emit()
	var armor0: float = GameState.armor
	var repel0: float = GameState.repel_percent
	var hp0: float = GameState.bonus_max_hp
	# вонючее: носок, сыр, швабра, вантуз, баллончик = 5; хозяйственное: швабра, вантуз = 2; кухонное: сыр = 1
	for pair: Array in [[&"sock", 1], [&"rotten_cheese", 2], [&"mop", 3], [&"plunger", 4], [&"spray_can", 1], [&"slingshot", 2]]:
		GameState.add_weapon(pair[0], pair[1])
	var counts: Dictionary = WeaponLibrary.class_counts(GameState.weapons)
	_check(counts.get(&"stinky", 0) == 5, "вонючих 5 (есть %d)" % counts.get(&"stinky", 0))
	_check(is_equal_approx(GameState.repel_percent - repel0, 12.0), "вонючее 5 даёт +12%% отпугивания (есть %+.1f)" % (GameState.repel_percent - repel0))
	_check(is_equal_approx(GameState.armor - armor0, 1.0), "хозяйственное 2 даёт +1 броню (есть %+.1f)" % (GameState.armor - armor0))
	_check(is_equal_approx(GameState.bonus_max_hp, hp0), "кухонное 1 - без бонуса")
	_check(WeaponLibrary.stat(&"slingshot", 2, "ricochets", 0) == 3, "рогатка II: 3 отскока")
	_check(WeaponLibrary.stat(&"mop", 4, "arc_deg") == 185.0, "швабра IV: дуга 185")
	_check(WeaponLibrary.stat(&"lighter", 3, "burn_dps", 0.0) == 2.0, "свойство без прибавки не меняется")
	await get_tree().process_frame
	var nodes: int = get_tree().get_nodes_in_group(&"weapon_nodes").size()
	_check(nodes == 6, "6 узлов оружия (есть %d)" % nodes)
	await get_tree().create_timer(1.5).timeout
	await _shot("1_hud")
	# слияние: две рогатки II -> III, набор стрелялок не меняется по числу (одна рогатка)
	GameState.weapons[4] = {"id": &"slingshot", "tier": 2}
	EventBus.weapons_changed.emit()
	_check(GameState.find_merge_partner(4) == 5, "есть пара для слияния")
	GameState.merge_weapons(4)
	_check(GameState.weapons.size() == 5 and GameState.weapons[4]["tier"] == 3, "рогатка слилась в III")
	_check(is_equal_approx(GameState.repel_percent - repel0, 9.0), "после замены баллончика вонючих 4: +9%")
	# Ларёк и пауза
	GameState.coins = 300
	GameState.wave = 6
	EventBus.wave_ended.emit(6)
	await get_tree().create_timer(0.5).timeout
	await _shot("2_shop")
	var lu: Node = level.get_node("LevelUpScreen")
	lu.call("_update_slot_info", 1)
	await get_tree().process_frame
	await _shot("3_shop_slot")
	lu.call("_on_next_pressed")
	await get_tree().process_frame
	var pause: Node = level.get_node("PauseMenu")
	pause.call("_open")
	pause.call("_open_inventory")
	await get_tree().create_timer(0.3).timeout
	await _shot("4_pause")
	pause.call("_close")
	print("SLOTS OK" if _fails == 0 else "SLOTS FAIL %d" % _fails)
	get_tree().quit()
