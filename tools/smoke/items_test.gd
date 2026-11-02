extends Node
## ТЕСТ предметов партии 3: комбо сливаются, проклятья работают. В конце ITEMS OK / ITEMS FAIL.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _fails: int = 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print("ITEMS ", "ok   " if ok else "FAIL ", what)
	if not ok:
		_fails += 1


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	await get_tree().create_timer(0.5).timeout
	get_tree().paused = false
	GameState.add_item(&"cigarette")
	_check(ItemLibrary.combo_with_owned(&"lighter") == &"combo_smoke", "зажигалка комбится с бычком")
	GameState.add_item(&"lighter")
	_check(GameState.item_count(&"combo_smoke") == 1, "комбо ЗАКУРИЛ появилось")
	_check(GameState.item_count(&"cigarette") == 0 and GameState.item_count(&"lighter") == 0, "части комбо забраны")
	_check(GameState.burn_percent >= 25.0, "комбо даёт поджог 25%")
	var regen_before: float = GameState.regen_hp
	GameState.apply_stat(&"regen", 2)
	_check(GameState.regen_hp > regen_before, "реген работает без проклятья")
	GameState.add_item(&"cursed_shawarma")
	_check(GameState.regen_hp == 0.0, "шаурма из мусорки обнуляет реген")
	GameState.add_item(&"cursed_teeth")
	_check(GameState.enemy_haste == 15.0, "чужие зубы ускоряют врагов")
	_check(ItemLibrary.pool(3).all(func(id: StringName) -> bool: return not ItemLibrary.is_cursed(id) and not ItemLibrary.is_combo(id)), "в обычном пуле нет проклятых и комбо")
	GameState.weapons.clear()
	GameState.add_weapon(&"frying_pan", 1)
	var hp0: float = GameState.bonus_max_hp
	GameState.add_item(&"chef_apron")
	_check(WeaponLibrary.class_counts(GameState.weapons, true).get(&"kitchen", 0) == 2, "фартук: +1 к набору КУХНЯ")
	_check(GameState.bonus_max_hp >= hp0 + 3.0 + 2.0, "фартук: +3 ХП и бонус набора кухни 2")
	GameState.weapons.clear()
	GameState.add_weapon(&"mop", 4)
	GameState.add_item(&"week_socks")
	await get_tree().process_frame
	_check(GameState.weapons[0]["tier"] == 5, "швабра IV + недельные носки = эволюция")
	_check(WeaponLibrary.stat(&"mop", 5, "arc_deg") >= 300.0, "тайфун машет почти по кругу")
	GameState.character = &"hobo"
	GameState.items.erase(ItemLibrary.SHOES)
	_check(ItemLibrary.shoes_max() == 1, "бомж: одна пара обуви")
	var shelf: Array[Dictionary] = ShopLibrary.fill_offers([], 2)
	_check(shelf.any(func(o: Dictionary) -> bool: return o["id"] == ItemLibrary.SHOES), "босому обувь лежит в Ларьке")
	_check(not ItemLibrary.pool(1).has(ItemLibrary.SHOES), "обуви нет в общем пуле")
	GameState.add_item(ItemLibrary.SHOES)
	_check(ItemLibrary.at_limit(ItemLibrary.SHOES), "бомжу вторая пара не положена")
	GameState.character = &"skater"
	_check(ItemLibrary.shoes_max() == 2 and not ItemLibrary.at_limit(ItemLibrary.SHOES), "скейтеру можно вторую пару")
	_check(ItemLibrary.title(ItemLibrary.SHOES) == "КЕДЫ СКЕЙТЕРА", "в Ларьке обувь своего героя")
	# Н12 лотерея: билет не в рюкзак, стирается и даёт итог
	GameState.coins = 100
	var ticket: Dictionary = {"kind": &"item", "id": ItemLibrary.TICKET, "tier": 1, "price": ShopLibrary.price(&"item", ItemLibrary.TICKET, 1, 9), "locked": false, "sold": false}
	_check(ticket["price"] == 5, "билет всегда 5 говна")
	ShopLibrary.buy(ticket)
	_check(GameState.lottery_tickets == 1 and GameState.item_count(ItemLibrary.TICKET) == 0, "билет не в рюкзаке")
	_check(GameState.scratch_tickets() != "" and GameState.lottery_tickets == 0, "билет стёрт")
	# Н13 карта: 5 штампов -> бесплатный реролл и скидка
	GameState.card_ready = false
	GameState.card_stamps = 0
	GameState.card_spend(Balance.CARD_STAMP_COINS * Balance.CARD_STAMPS)
	_check(GameState.card_ready, "карта заполнилась")
	_check(GameState.card_open_shop() and GameState.free_rerolls >= 1 and GameState.card_discount > 0.0, "полная карта даёт реролл и скидку")
	print("ITEMS OK" if _fails == 0 else "ITEMS FAIL %d" % _fails)
	get_tree().quit()
