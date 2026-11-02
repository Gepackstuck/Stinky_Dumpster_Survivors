extends Node
## ТЕСТ режимов: бесконечность после победы (16-я волна, 18-я элита, 20-я боссы), очки ежедневки. MODES OK / FAIL.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _fails: int = 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print("MODES ", "ok   " if ok else "FAIL ", what)
	if not ok:
		_fails += 1


func _run() -> void:
	# «Шизосид»: одно слово - одинаковый рандом, разные слова - разный
	GameState.daily = false
	GameState.seed_word = "ВАСЯ"
	GameState.reset_run()
	var a: Array = [randi(), randi(), ShopLibrary.fill_offers([], 3).map(func(o: Dictionary) -> StringName: return o["id"])]
	GameState.reset_run()
	var b: Array = [randi(), randi(), ShopLibrary.fill_offers([], 3).map(func(o: Dictionary) -> StringName: return o["id"])]
	GameState.seed_word = "ПЕТЯ"
	GameState.reset_run()
	var c: Array = [randi(), randi()]
	_check(a == b, "одно слово - один и тот же забег")
	_check(a[0] != c[0], "другое слово - другой забег")
	GameState.seed_word = ""
	# Н33 ларёк закрыт: обувь сразу, находки после волны
	GameState.mode = &"closed"
	GameState.character = &"skater"
	GameState.reset_run()
	_check(GameState.item_count(ItemLibrary.SHOES) == 2, "без Ларька обувь выдана сразу")
	GameState.wave = 4
	_check(GameState.closed_gift() != "", "находка после обычной волны")
	GameState.wave = 6
	var w0: int = GameState.weapons.size()
	_check(GameState.closed_gift() != "" and (GameState.weapons.size() > w0 or w0 >= Balance.WEAPON_SLOTS), "каждая 3-я волна - оружие")
	GameState.mode = &""
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(0.6).timeout
	var wm: Node = level.get_node(^"WaveManager")
	GameState.wave = Balance.WAVE_COUNT
	wm.call("_win")
	await get_tree().process_frame
	_check(not GameState.run_active, "победа завершила забег")
	EventBus.endless_requested.emit()
	await get_tree().process_frame
	_check(GameState.endless and GameState.run_active, "бесконечность включилась")
	EventBus.next_wave_requested.emit()
	await get_tree().process_frame
	_check(GameState.wave == Balance.WAVE_COUNT + 1 and GameState.wave_kind == &"normal", "16-я волна обычная (есть %d %s)" % [GameState.wave, GameState.wave_kind])
	_check(wm.call("wave_kind", 18) == &"elite" and wm.call("wave_kind", 20) == &"boss", "18-я элита, 20-я боссы")
	GameState.mode = &"endless"
	_check(wm.call("wave_kind", 5) == &"boss" and wm.call("wave_kind", 6) == &"elite" and wm.call("wave_kind", 7) == &"normal", "Н32: босс каждые 5, элита каждая 3-я")
	GameState.mode = &""
	GameState.kills = 100
	GameState.clean_waves = 2
	_check(GameState.run_score(false) == 100 + 16 * Balance.SCORE_PER_WAVE + 2 * Balance.SCORE_PER_CLEAN_WAVE + Balance.SCORE_WIN, "очки бесконечности")
	_check(GameState.today_seed() > 20200101, "сид дня")
	print("MODES OK" if _fails == 0 else "MODES FAIL %d" % _fails)
	get_tree().quit()
