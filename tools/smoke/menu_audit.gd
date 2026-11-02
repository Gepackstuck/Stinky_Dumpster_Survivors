extends Node
## АУДИТ МЕНЮ: снимает кадры всех экранов в tools/_preview/audit_*.png (счётчики профиля восстанавливаются).

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const ALL_ITEMS: Array[StringName] = [&"cigarette", &"sandwich", &"holey_sock", &"pot", &"energy_can", &"poop_wallet", &"old_milk", &"nail_knuckles", &"dirty_glasses", &"junk_magnet", &"stinky_pants", &"foil_hat", &"shawarma", &"coupon", &"barbed_wire", &"diarrhea", &"bloody_rag", &"dead_rat", &"bucket_turret", &"ghost_drunk", &"golden_toilet", &"bottle_cap", &"gum"]


func _ready() -> void:
	Profile.sandbox = true   # тесты не пишут в живой профиль
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/audit_%s.png" % label))


func _press(action: StringName) -> void:
	var ev: InputEventAction = InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	await get_tree().process_frame
	ev = InputEventAction.new()
	ev.action = action
	ev.pressed = false
	Input.parse_input_event(ev)
	await get_tree().process_frame


func _run() -> void:
	var saved: Dictionary = Profile.enemy_kills.duplicate()
	for id: StringName in Balance.ENEMIES:
		if randf() < 0.6:
			Profile.enemy_kills[id] = randi_range(1, 400)
	# 1) главное меню + бестиарий + навигация
	var menu: Node = load("res://scenes/ui/main_menu.tscn").instantiate()
	get_tree().root.add_child(menu)
	await get_tree().create_timer(0.6).timeout
	await _shot("1_main_menu")
	await _press(&"move_down")
	await _shot("1b_main_menu_focus2")
	menu.call("_open_settings")
	await get_tree().create_timer(0.3).timeout
	await _shot("1c_settings")
	menu.get("_settings").emit_signal("closed")
	await get_tree().process_frame
	menu.call("_open_bestiary")
	await get_tree().create_timer(0.4).timeout
	await _shot("2_bestiary")
	for i: int in 9:
		await _press(&"move_right")
	await _press(&"move_down")
	await _shot("2b_bestiary_nav")
	await _press(&"ui_accept")
	await get_tree().create_timer(0.3).timeout
	await _shot("2c_after_close")
	menu.queue_free()
	await get_tree().process_frame
	# 2) кладбище и книга оружия
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(1.0).timeout
	await _shot("3_graveyard")
	var book: Control = load("res://scripts/ui/weapon_book.gd").new()
	yard.add_child(book)
	await get_tree().create_timer(0.3).timeout
	await _shot("4_weapon_book")
	book.queue_free()
	yard.queue_free()
	await get_tree().process_frame
	# 3) арена: ХУД, выбор стартового оружия, пауза, инвентарь, подтверждения
	GameState.character = &"hobo"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	await get_tree().create_timer(1.0).timeout
	await _shot("5_start_choice")
	level.get_node("LevelUpScreen").call("_on_card_pressed", 0)
	get_tree().paused = false
	await get_tree().create_timer(1.5).timeout
	await _shot("6_hud")
	var pause: Node = level.get_node("PauseMenu")
	pause.call("_open")
	await get_tree().create_timer(0.3).timeout
	await _shot("7_pause")
	await _press(&"move_down")
	await _press(&"move_down")
	await _shot("7b_pause_focus_bestiary")
	await _press(&"ui_accept")
	await get_tree().create_timer(0.3).timeout
	await _shot("7c_pause_bestiary")
	await _press(&"ui_cancel")
	await get_tree().create_timer(0.2).timeout
	await _shot("7d_pause_after_bestiary")
	pause.call("_open_inventory")
	await get_tree().create_timer(0.2).timeout
	await _shot("8_inventory_empty")
	pause.call("_close")
	for id: StringName in ALL_ITEMS:
		GameState.add_item(id)
	for w: StringName in [&"mop", &"sock", &"slingshot", &"plunger", &"blowtorch"]:
		GameState.add_weapon(w, 2)
	GameState.coins = 123
	pause.call("_open")
	pause.call("_open_inventory")
	await get_tree().create_timer(0.2).timeout
	await _shot("8b_inventory_full")
	pause.call("_close")
	pause.call("_open")
	pause.call("_ask", "ТОЧНО В МЕНЮ?\nВЕСЬ ПРОГРЕСС ЗАБЕГА\nПРОПАДЁТ.", "ДА, ПРОПАДАЙ", func() -> void: pass)
	await get_tree().create_timer(0.2).timeout
	await _shot("9_confirm")
	pause.call("_close")
	# 4) уровень: карточки статов и Ларёк
	var lu: Node = level.get_node("LevelUpScreen")
	GameState.wave = 6
	EventBus.player_leveled_up.emit(7)
	EventBus.player_leveled_up.emit(8)
	EventBus.wave_ended.emit(6)
	await get_tree().create_timer(0.4).timeout
	await _shot("10_levelup_cards")
	lu.call("_on_card_pressed", 0)
	await get_tree().create_timer(0.2).timeout
	lu.call("_on_card_pressed", 0)
	await get_tree().create_timer(0.4).timeout
	await _shot("11_shop_full")
	lu.call("_open_menu", 1)
	await get_tree().create_timer(0.2).timeout
	await _shot("12_shop_slot_menu")
	lu.call("_close_menu")
	GameState.coins = 0
	await _press(&"move_right")
	await _press(&"ui_accept")
	await get_tree().create_timer(0.2).timeout
	await _shot("13_shop_cant_afford")
	# 5) смерть
	GameState.last_damage_source = &"spitter"
	lu.call("_on_next_pressed")
	GameState.kills = 77
	EventBus.player_died.emit()
	await get_tree().create_timer(0.5).timeout
	await _shot("14_death")
	Profile.enemy_kills = saved
	print("AUDIT DONE")
	get_tree().quit()
