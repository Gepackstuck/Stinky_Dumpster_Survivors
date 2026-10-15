extends Node
## БОТ-ИГРОК для проверки баланса: сам двигается (уворот + сбор говна), выбирает карточки уровней и закупается в Ларьке.
## Игра идёт на ускорении. Лог по волнам: tools/_preview/bot_log.txt. Профиль игрока после теста возвращается как был.
## Сцена tools/smoke/bot.tscn. Какие герои - в RUNS.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const RUNS: Array[StringName] = [&"hobo", &"janitor", &"clerk", &"squid", &"blogger", &"pigeon", &"uncle_vitya", &"granny", &"courier", &"punk", &"guard", &"plumber"]
const TIME_SCALE: float = 8.0
const FLEE_RADIUS: float = 95.0
const STAT_WEIGHT: Dictionary = {&"damage": 3.0, &"attack_speed": 2.6, &"max_hp": 2.0, &"armor": 2.2, &"crit": 1.4,
		&"speed": 1.4, &"dodge": 1.5, &"regen": 1.3, &"pickup": 0.8}

var _file: FileAccess
var _level: Node = null
var _ui: Node = null
var _player: Node2D = null
var _run_index: int = -1
var _running: bool = false
var _finished: bool = false
var _real_start: int = 0
var _backup: Dictionary = {}
# статистика текущей волны
var _w_kills: int = 0
var _w_dmg: float = 0.0
var _w_min_hp: float = 999.0
var _w_peak: int = 0
var _last_hp: float = 0.0
var _rerolls: int = 0
var _projectiles: Array[Node] = []
var _frame: int = 0
var _src: Dictionary = {}   # урон по источникам за волну


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_backup = {"k": Profile.total_kills, "c": Profile.total_coins, "d": Profile.deaths, "w": Profile.wins}
	_file = FileAccess.open(ProjectSettings.globalize_path("res://tools/_preview/bot_log.txt"), FileAccess.WRITE)
	Engine.time_scale = TIME_SCALE
	EventBus.player_died.connect(_on_died)
	EventBus.run_won.connect(_on_won)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.player_hit.connect(_on_hit)
	_next_run.call_deferred()


func _out(text: String) -> void:
	print(text)
	_file.store_line(text)
	_file.flush()


func _next_run() -> void:
	if _level != null:
		_level.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	_run_index += 1
	if _run_index >= RUNS.size():
		_finish()
		return
	get_tree().paused = false
	GameState.character = RUNS[_run_index]
	_level = MAIN.instantiate()
	get_tree().root.add_child(_level)
	_running = true
	_finished = false
	_real_start = Time.get_ticks_msec()
	await get_tree().create_timer(0.5).timeout
	_ui = _level.find_children("*", "LevelUpScreen", true, false)[0]
	_player = get_tree().get_first_node_in_group(&"player") as Node2D
	_last_hp = GameState.hp
	_out("=== ЗАБЕГ %d: %s ===" % [_run_index + 1, RUNS[_run_index]])


func _finish() -> void:
	Profile.total_kills = _backup["k"]
	Profile.total_coins = _backup["c"]
	Profile.deaths = _backup["d"]
	Profile.wins = _backup["w"]
	Profile.save()
	_out("BOT DONE")
	_release_keys()
	get_tree().quit()


func _on_hit(damage: float) -> void:
	var key: StringName = GameState.last_damage_source if GameState.last_damage_source != &"" else &"?"
	_src[key] = _src.get(key, 0.0) + damage


func _src_text() -> String:
	var parts: Array[String] = []
	var keys: Array = _src.keys()
	keys.sort_custom(func(a: StringName, b: StringName) -> bool: return _src[a] > _src[b])
	for k: StringName in keys.slice(0, 4):
		parts.append("%s %.0f" % [k, _src[k]])
	return ", ".join(parts)


func _on_wave_started(_wave: int) -> void:
	_src.clear()
	_w_kills = GameState.kills
	_w_dmg = 0.0
	_w_min_hp = GameState.hp
	_w_peak = 0
	_rerolls = 0


func _stats_line() -> String:
	var weapons: Array[String] = []
	for w: Dictionary in GameState.weapons:
		weapons.append("%s%d" % [w["id"], w["tier"]])
	return "урон+%d%% скор+%d%% хп+%d бр%d уворот%d крит%d | оружие %s | предметов %d" % [roundi(GameState.stat_total(&"damage")), roundi(GameState.stat_total(&"attack_speed")),
			roundi(GameState.bonus_max_hp), roundi(GameState.armor), roundi(GameState.dodge_percent), roundi(GameState.crit_percent),
			",".join(weapons), _item_total()]


func _item_total() -> int:
	var total: int = 0
	for id: StringName in GameState.items:
		total += GameState.items[id]
	return total


func _on_wave_ended(wave: int) -> void:
	if not _running:
		return
	_out("В%02d %s мин.хп %.0f урона получено %.0f (%s) убито %d пик.врагов %d | ур %d говна %d | %s" % [wave, GameState.wave_kind, _w_min_hp, _w_dmg, _src_text(), GameState.kills - _w_kills, _w_peak, GameState.level, GameState.coins, _stats_line()])


func _end_run(result: String) -> void:
	if _finished:
		return
	_finished = true
	_running = false
	_release_keys()
	_out("ИТОГ %s: %s на волне %d (осталось %.0fс), последний удар от %s, урон за волну: %s, убито %d, реальное время %.0fс. %s" % [RUNS[_run_index], result, GameState.wave, GameState.wave_time_left, GameState.last_damage_source, _src_text(), GameState.kills, (Time.get_ticks_msec() - _real_start) / 1000.0, _stats_line()])
	await get_tree().create_timer(1.0).timeout
	_next_run()


func _on_died() -> void:
	_end_run("СМЕРТЬ")


func _on_won() -> void:
	_end_run("ПОБЕДА")


func _release_keys() -> void:
	for action: StringName in [&"move_left", &"move_right", &"move_up", &"move_down"]:
		Input.action_release(action)


func _physics_process(_delta: float) -> void:
	if not _running or _player == null or not is_instance_valid(_player):
		return
	if GameState.hp < _last_hp:
		_w_dmg += _last_hp - GameState.hp
	_last_hp = GameState.hp
	_w_min_hp = minf(_w_min_hp, GameState.hp)
	if get_tree().paused:
		_release_keys()
		return
	if Time.get_ticks_msec() - _real_start > 900000:
		_end_run("ТАЙМАУТ")
		return
	_steer()


func _steer() -> void:
	var pos: Vector2 = _player.global_position
	var flee: Vector2 = Vector2.ZERO
	var nearest: float = 9999.0
	var enemies: Array[Node] = get_tree().get_nodes_in_group(&"enemies")
	_w_peak = maxi(_w_peak, enemies.size())
	var nearest_enemy: Node2D = null
	for node: Node in enemies:
		var enemy: Node2D = node as Node2D
		var offset: Vector2 = enemy.global_position - pos
		var dist: float = offset.length()
		if dist < nearest:
			nearest = dist
			nearest_enemy = enemy
		if dist < FLEE_RADIUS and dist > 0.1:
			flee -= offset / dist * pow((FLEE_RADIUS - dist) / FLEE_RADIUS, 1.5) * 2.0
	var want: Vector2 = flee
	if nearest > 50.0:
		var best: Node2D = null
		var best_d: float = 220.0
		for node: Node in get_tree().get_nodes_in_group(&"pickups"):
			var pickup: Node2D = node as Node2D
			var d: float = pos.distance_to(pickup.global_position)
			if d < best_d:
				best_d = d
				best = pickup
		if best != null:
			want += (best.global_position - pos).normalized() * 0.9
		elif nearest_enemy != null and nearest > 130.0:
			want += (nearest_enemy.global_position - pos).normalized() * 0.5   # подойти, чтобы оружие доставало
	if nearest_enemy != null and flee.length() > 0.05:
		var side: Vector2 = (nearest_enemy.global_position - pos).orthogonal().normalized()   # обходить по кругу, а не упираться в стену
		want += side * 0.35
	# уворот от снарядов врагов: шаг в сторону от траектории
	_frame += 1
	if _frame % 3 == 0:
		_projectiles = _level.find_children("*", "EnemyProjectile", true, false)
	for node: Node in _projectiles:
		if not is_instance_valid(node):
			continue
		var proj: Node2D = node as Node2D
		var to_me: Vector2 = pos - proj.global_position
		var dist_p: float = to_me.length()
		var heading: Vector2 = proj.get("_direction")
		if dist_p < 120.0 and dist_p > 1.0 and heading.dot(to_me / dist_p) > 0.75:
			var perp: Vector2 = heading.orthogonal()
			if perp.dot(to_me) < 0.0:
				perp = -perp
			want += perp * 2.2 * (1.0 - dist_p / 120.0)
	var arena: float = Balance.ARENA_SIZE
	var margin: float = 70.0
	if pos.x < margin:
		want.x += (margin - pos.x) / margin * 3.2
	if pos.x > arena - margin:
		want.x -= (pos.x - (arena - margin)) / margin * 3.2
	if pos.y < margin:
		want.y += (margin - pos.y) / margin * 3.2
	if pos.y > arena - margin:
		want.y -= (pos.y - (arena - margin)) / margin * 3.2
	var hard: float = 34.0   # у самой проволоки внутрь стены не идём совсем
	if pos.x < hard:
		want.x = maxf(want.x, 0.0)
	if pos.x > arena - hard:
		want.x = minf(want.x, 0.0)
	if pos.y < hard:
		want.y = maxf(want.y, 0.0)
	if pos.y > arena - hard:
		want.y = minf(want.y, 0.0)
	if want.length() > 1.0:
		want = want.normalized()
	_press(&"move_left", maxf(-want.x, 0.0))
	_press(&"move_right", maxf(want.x, 0.0))
	_press(&"move_up", maxf(-want.y, 0.0))
	_press(&"move_down", maxf(want.y, 0.0))


func _press(action: StringName, strength: float) -> void:
	if strength > 0.05:
		Input.action_press(action, strength)
	else:
		Input.action_release(action)


# ---- интерфейс между волнами ----

func _process(_delta: float) -> void:
	if not _running or _ui == null or not is_instance_valid(_ui):
		return
	var root: Control = _ui.get("_root")
	if not root.visible:
		return
	if _ui.get("_start_mode"):
		_ui.call("_on_card_pressed", 0)
	elif _ui.get("_shop_mode"):
		_shop()
	else:
		_level_up()


func _level_up() -> void:
	var offers: Array = _ui.get("_stat_offers")
	var best: int = 0
	var best_score: float = -1.0
	for i: int in offers.size():
		var score: float = STAT_WEIGHT.get(offers[i]["id"], 1.0) * (0.6 + 0.4 * offers[i]["tier"])
		if score > best_score:
			best_score = score
			best = i
	_ui.call("_on_card_pressed", best)


func _offer_score(offer: Dictionary) -> float:
	var tier: int = offer["tier"]
	if offer["kind"] == &"weapon":
		var merge: float = 6.0 if GameState.find_weapon(offer["id"], tier) >= 0 else 0.0
		var free: float = 8.0 if GameState.weapons.size() < Balance.WEAPON_SLOTS else 0.0
		return 6.0 + tier * 3.0 + merge + free
	if offer["kind"] == &"item":
		var data: Dictionary = Balance.ITEMS[offer["id"]]
		var score: float = 3.0 + tier * 2.5
		for stat: StringName in data.get("mods", {}):
			var v: float = data["mods"][stat]
			score += STAT_WEIGHT.get(stat, 1.0) * v * (0.25 if v > 0.0 else 0.18)
		if data.get("fx", {}).has(&"pets") or data.get("fx", {}).has(&"turrets"):
			score += 4.0
		return score
	return 2.0


func _shop() -> void:
	var offers: Array[Dictionary] = GameState.shop_offers
	var best: int = -1
	var best_score: float = 0.0
	for i: int in offers.size():
		if ShopLibrary.why_not(offers[i]) != "":
			continue
		var score: float = _offer_score(offers[i])
		if score > best_score:
			best_score = score
			best = i
	if best >= 0:
		_ui.call("_on_card_pressed", best)
		return
	var cost: int = Balance.REROLL_BASE_COST + int(GameState.wave * Balance.REROLL_WAVE_FACTOR) + GameState.reroll_count * Balance.REROLL_STEP_COST
	if _rerolls < 3 and GameState.coins >= cost + 25:
		_rerolls += 1
		_ui.call("_on_reroll_pressed")
		return
	for slot: int in GameState.weapons.size():
		if GameState.find_merge_partner(slot) >= 0:
			GameState.merge_weapons(slot)
			_ui.call("_refresh_shop")
			return
	_ui.call("_on_next_pressed")
