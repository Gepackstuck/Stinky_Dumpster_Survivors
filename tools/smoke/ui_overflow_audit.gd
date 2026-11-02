extends Node
## АУДИТ ТЕКСТА: обходит экраны и ищет надписи, которые не влезают (шире своей рамки или вылезают за экран 480x270).
## Печатает UI OVERFLOW <экран> | <путь> | <текст>. В конце UI AUDIT DONE N.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const SCREEN: Rect2 = Rect2(0, 0, 480, 270)
var _found: int = 0
var _seen: Dictionary = {}


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	for arg: String in OS.get_cmdline_user_args():   # -- --locale=en: тот же обход на другом языке
		if arg.begins_with("--locale="):
			TranslationServer.set_locale(arg.trim_prefix("--locale="))
	print("UI AUDIT LOCALE ", TranslationServer.get_locale())
	_run.call_deferred()


func _check(where: String, root: Node) -> void:
	for node: Node in root.find_children("*", "Label", true, false):
		var l: Label = node as Label
		if l == null or not l.is_visible_in_tree() or l.text.strip_edges() == "" or l.clip_text:
			continue
		var r: Rect2 = l.get_global_rect()
		var sc: Vector2 = l.get_global_transform().get_scale()
		var need: Vector2 = l.get_minimum_size() * sc
		var bad: String = ""
		if l.autowrap_mode == TextServer.AUTOWRAP_OFF and need.x > r.size.x + 1.0:
			bad = "шире рамки (%d > %d)" % [need.x, r.size.x]
		elif need.y > r.size.y + 2.0 and l.autowrap_mode != TextServer.AUTOWRAP_OFF:
			bad = "строк больше, чем места (%d > %d)" % [need.y, r.size.y]
		var drawn: Rect2 = Rect2(r.position, Vector2(maxf(r.size.x, need.x), maxf(r.size.y, need.y)))
		if not SCREEN.encloses(drawn.grow(-1.0)):
			bad += (" + " if bad != "" else "") + "за экраном %s" % str(drawn)
		if bad != "":
			var key: String = where + "|" + l.text
			if _seen.has(key):
				continue
			_seen[key] = true
			_found += 1
			print("UI OVERFLOW %s | %s | %s | %s" % [where, str(root.get_path_to(l)), bad, l.text.replace("\n", " / ").left(70)])


func _run() -> void:
	var menu: Node = load("res://scenes/ui/main_menu.tscn").instantiate()
	get_tree().root.add_child(menu)
	await get_tree().create_timer(0.3).timeout
	_check("меню", menu)
	menu.call("_open_modes")
	await get_tree().process_frame
	var mp: Node = menu.get("_modes_panel")
	for b: Button in mp.get("_buttons"):
		b.grab_focus()
		await get_tree().process_frame
		_check("режимы", menu)
	menu.call("_close_modes")
	await get_tree().process_frame
	menu.call("_open_seed")
	await get_tree().process_frame
	_check("шизосид", menu)
	menu.get("_seed_panel").emit_signal("closed")
	await get_tree().process_frame
	menu.call("_open_settings")
	await get_tree().process_frame
	_check("настройки", menu)
	menu.get("_settings").emit_signal("closed")
	await get_tree().process_frame
	menu.call("_open_bestiary")
	await get_tree().create_timer(0.2).timeout
	var best: Node = menu.get("_bestiary")
	for i: int in 30:
		_check("бестиарий", menu)
		var ev: InputEventAction = InputEventAction.new()
		ev.action = &"move_right"
		ev.pressed = true
		best._input(ev)
		await get_tree().process_frame
	menu.queue_free()
	await get_tree().process_frame
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(0.5).timeout
	for i: int in Balance.CHARACTER_ORDER.size():
		yard.call("_select", i)
		await get_tree().process_frame
		_check("кладбище/" + String(Balance.CHARACTER_ORDER[i]), yard)
	yard.call("_toggle_book")
	await get_tree().process_frame
	_check("книга оружия", yard)
	var book: Node = yard.get("_book")
	for tab: int in range(1, 5):   # вкладки коллекции, курсор по всем клеткам
		book.call("_show_tab", tab)
		await get_tree().process_frame
		var n: int = (book.get("_grid_ids") as Array).size()
		for k: int in n:
			book.set("_cursor", k)
			book.call("_update_cursor")
			_check("книга/%d/%d" % [tab, k], book)
		await get_tree().process_frame
	yard.call("_toggle_book")
	await get_tree().process_frame
	Profile.danger_unlocked = 5
	yard.call("_open_picker")
	for d: int in 6:
		yard.set("_pick_danger", d)
		yard.call("_refresh_picker")
		await get_tree().process_frame
		_check("опасность/%d" % d, yard)
	yard.queue_free()
	await get_tree().process_frame
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(0.6).timeout
	_check("бой/HUD", level)
	var banner: Node = level.find_children("*", "", true, false).filter(func(n: Node) -> bool: return n.has_method(&"_on_wave_started") and n.get_script() != null and String(n.get_script().resource_path).ends_with("wave_banner.gd")).front()
	GameState.wave_kind = &"normal"
	GameState.wave_mod = &""
	for s: StringName in Balance.SEASON_ORDER:
		GameState.season = s
		banner.call("_on_wave_started", 3)
		await get_tree().create_timer(0.45).timeout
		_check("баннер/" + String(s), banner)
	var lu: Node = level.get_node(^"LevelUpScreen")
	GameState.coins = 999
	GameState.wave = 8
	# все товары Ларька: оружия всех тиров, предметы, перки
	var offers: Array[Dictionary] = []
	for w: StringName in Balance.WEAPONS:
		if not Balance.WEAPONS[w].get("structure", false):
			offers.append({"kind": &"weapon", "id": w, "tier": 4, "price": 999, "locked": false, "sold": false})
	for it: StringName in Balance.ITEMS:
		offers.append({"kind": &"item", "id": it, "tier": ItemLibrary.tier(it), "price": 99, "locked": true, "sold": false})
	for k: int in range(0, offers.size(), 4):
		GameState.shop_offers.assign(offers.slice(k, k + 4))
		lu.set("_queue", [])
		lu.call("_show_choices")
		await get_tree().process_frame
		_check("ларёк", lu)
	lu.set("_shop_mode", true)
	for i: int in GameState.weapons.size():
		lu.call("_update_slot_info", i)
		_check("ларёк/слот", lu)
	for kind: StringName in WaveEvent.KINDS:
		var ev: WaveEvent = WaveEvent.new()
		lu.add_child(ev)
		ev.setup(kind)
		await get_tree().process_frame
		_check("событие/" + String(kind), ev)
		ev.queue_free()
	var pause: Node = level.get_node(^"PauseMenu")
	pause.call("_open")
	await get_tree().process_frame
	_check("пауза", pause)
	for it: StringName in Balance.ITEMS:
		GameState.items[it] = 1
	pause.call("_open_inventory")
	await get_tree().process_frame
	_check("пауза/хлам", pause)
	pause.call("_close")
	var ds: Node = level.get_node(^"DeathScreen")
	GameState.damage_by_source = {&"extension_cord": 9999.0, &"rotten_cheese": 5000.0, &"pets": 300.0, &"structures": 100.0, &"ult": 50.0}
	for killer: StringName in [&"boss_trash_golem", &"garbage_truck", &"wire", &"squid_gopnik"]:
		GameState.last_damage_source = killer
		GameState.seed_word = "МОРКОВСКВАСЯШАУР"
		GameState.mode = &"endless"   # самый длинный сид - строка итогов не должна вылезти
		ds.call("_show_result", FlavorText.random_death(), true)
		await get_tree().process_frame
		_check("итоги/" + String(killer), ds)
	var rs: Node = level.get_node(^"RouletteScreen")
	for m: StringName in Balance.WAVE_MODS:
		rs.get("_title").text = "ВЫПАЛО: %s!" % Balance.WAVE_MOD_DATA[m]["title"]
		rs.get("_sub").text = Balance.WAVE_MOD_DATA[m]["line"]
		rs.get("_root").visible = true
		await get_tree().process_frame
		_check("рулетка/" + String(m), rs)
	print("UI AUDIT DONE %d" % _found)
	get_tree().quit()
