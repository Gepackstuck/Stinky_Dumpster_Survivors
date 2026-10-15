extends Node
## БОТ-ИГРОК для проверки баланса: сам двигается (уворот + сбор говна), выбирает карточки уровней и закупается в Ларьке.
## Игра идёт на ускорении. Лог по волнам: tools/_preview/bot_log.txt. Профиль игрока после теста возвращается как был.
## Сцена tools/smoke/bot.tscn. Какие герои - в RUNS.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const RUNS: Array[StringName] = [&"hobo", &"janitor", &"clerk", &"squid", &"blogger", &"pigeon", &"uncle_vitya", &"granny", &"courier", &"punk", &"guard", &"plumber"]
const TIME_SCALE: float = 8.0
const STAND_STILL: bool = false   # true: бот не двигается — проверка, что кемперить нельзя
const FLEE_RADIUS: float = 95.0
const STAT_WEIGHT: Dictionary = {&"damage": 4.2, &"attack_speed": 3.6, &"max_hp": 3.4, &"armor": 3.0, &"crit": 1.6,
		&"speed": 2.0, &"dodge": 2.2, &"regen": 2.2, &"pickup": 0.8}

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
var _last_dir: Vector2 = Vector2.ZERO
var _pos_hist: Array[Vector2] = []
var _escape_dir: Vector2 = Vector2.ZERO
var _escape_left: float = 0.0
var _goal: Vector2 = Vector2.ZERO
var _goal_left: float = 0.0
var _results: Array = []
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
	var killers: Dictionary = {}
	var waves: Array = []
	for r: Dictionary in _results:
		killers[r["killer"]] = killers.get(r["killer"], 0) + 1
		waves.append(r["wave"])
	waves.sort()
	_out("СВОДКА: волны смерти %s, медиана %s; убийцы %s" % [str(waves), str(waves[waves.size() / 2]) if not waves.is_empty() else "-", str(killers)])
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
	_results.append({"hero": RUNS[_run_index], "wave": GameState.wave, "killer": GameState.last_damage_source if result == "СМЕРТЬ" else &"win"})
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
	if not STAND_STILL:
		_steer()


func _steer() -> void:
	var pos: Vector2 = _player.global_position
	var enemies: Array[Node] = get_tree().get_nodes_in_group(&"enemies")
	_w_peak = maxi(_w_peak, enemies.size())
	_frame += 1
	if _frame % 3 == 0:
		_projectiles = _level.find_children("*", "EnemyProjectile", true, false)
	var speed: float = Balance.PLAYER_MOVE_SPEED * GameState.move_speed_mult
	var near: Array = []   # [pos, vel, danger]
	for node: Node in enemies:
		var enemy: Node2D = node as Node2D
		if enemy.global_position.distance_squared_to(pos) < 200.0 * 200.0:
			var vel: Vector2 = Vector2.ZERO
			if enemy is CharacterBody2D:
				vel = (enemy as CharacterBody2D).velocity
			var danger: float = 1.0
			var id: StringName = enemy.get("enemy_id") if enemy.get("enemy_id") != null else &""
			if id == &"charger" or id == &"boss_zakhar" or id == &"boss_minion" or id == &"boss_mega_hamster" or id == &"bruiser":
				danger = 1.8
			near.append([enemy.global_position, vel, danger])
	var pickups: Array = []
	for node: Node in get_tree().get_nodes_in_group(&"pickups"):
		var pk: Node2D = node as Node2D
		if pk.global_position.distance_squared_to(pos) < 220.0 * 220.0:
			pickups.append(pk.global_position)
	var arena: float = Balance.ARENA_SIZE
	# зажали в угол/толпой: пробиваемся — игрок расталкивает врагов, надо давить в сторону с самым пустым просветом
	_pos_hist.append(pos)
	if _pos_hist.size() > 36:
		_pos_hist.pop_front()
	var crowd: int = 0
	for e: Array in near:
		if pos.distance_to(e[0]) < 38.0:
			crowd += 1
	if _escape_left > 0.0:
		_escape_left -= get_physics_process_delta_time()
		_drive(_escape_dir)
		return
	if _pos_hist.size() >= 36 and crowd >= 1 and _pos_hist[0].distance_to(pos) < 14.0:
		var center: Vector2 = Vector2(arena, arena) * 0.5
		var pick: Vector2 = Vector2.ZERO
		var pick_score: float = -INF
		for k: int in 16:
			var d2: Vector2 = Vector2.from_angle(TAU * k / 16.0)
			var sc: float = d2.dot((center - pos).normalized()) * 2.0
			for e: Array in near:
				var off: Vector2 = (e[0] as Vector2) - pos
				if off.length() < 90.0 and off.normalized().dot(d2) > 0.6:
					sc -= 1.5
			var after: Vector2 = pos + d2 * 40.0
			if after.x < 30.0 or after.y < 30.0 or after.x > arena - 30.0 or after.y > arena - 30.0:
				sc -= 4.0
			if sc > pick_score:
				pick_score = sc
				pick = d2
		_escape_dir = pick
		_escape_left = 0.7
		_pos_hist.clear()
		return
	_goal_left -= get_physics_process_delta_time()
	if _goal_left <= 0.0 or pos.distance_to(_goal) < 30.0:
		_pick_goal(pos, near)
	var danger_r: float = clampf(_want_range() + 32.0, 55.0, 95.0)
	var bold: float = 1.0
	if _want_range() < 70.0 and GameState.hp > GameState.max_hp * 0.5:
		bold = 0.3   # ближнему бою надо подходить вплотную, иначе оружие не работает
	var best_dir: Vector2 = Vector2.ZERO
	var best_score: float = -INF
	var dirs: int = 16
	for i: int in dirs + 1:
		var dir: Vector2 = Vector2.ZERO if i == dirs else Vector2.from_angle(TAU * i / dirs)
		var score: float = 0.0
		# смотрим три момента вперёд: через 0.25, 0.5 и 0.8 сек
		for t: float in [0.15, 0.4, 0.8]:
			var me: Vector2 = pos + dir * speed * t
			var w: float = 1.0 if t < 0.6 else 0.7
			for e: Array in near:
				var ep: Vector2 = (e[0] as Vector2) + (e[1] as Vector2) * t
				var d: float = me.distance_to(ep)
				var danger: float = e[2]
				if d < danger_r:
					score -= w * danger * pow((danger_r - d) / danger_r, 2.0) * 90.0 * bold
			for node: Node in _projectiles:
				if not is_instance_valid(node):
					continue
				var proj: Node2D = node as Node2D
				var heading: Vector2 = proj.get("_direction")
				var pv: float = float(proj.get("_speed"))
				var pp: Vector2 = proj.global_position + heading * pv * t
				var dd: float = me.distance_to(pp)
				if dd < 22.0:
					score -= w * (22.0 - dd) * 6.0
			# стены и углы
			var edge: float = minf(minf(me.x, arena - me.x), minf(me.y, arena - me.y))
			if edge < 70.0:
				score -= w * pow((70.0 - edge) / 70.0, 2.0) * 60.0
			if edge < 44.0:
				score -= w * 200.0
		# простор: чем дальше от центра масс врагов, тем лучше, но не уходим в угол
		if not near.is_empty():
			var centroid: Vector2 = Vector2.ZERO
			for e: Array in near:
				centroid += e[0]
			centroid /= near.size()
			score += (pos + dir * speed * 0.8).distance_to(centroid) * 0.12
		# собираем говно, когда рядом тихо
		var calm: bool = true
		for e: Array in near:
			if pos.distance_to(e[0]) < danger_r:
				calm = false
				break
		if calm and not pickups.is_empty():
			var closest: float = 9999.0
			for pk: Vector2 in pickups:
				closest = minf(closest, (pos + dir * speed * 0.5).distance_to(pk))
			score -= closest * 0.25
		elif calm and not near.is_empty():
			# подойти к врагам на дистанцию стрельбы, чтобы оружие доставало
			score -= absf((pos + dir * speed * 0.5).distance_to(_nearest(near, pos)) - _want_range()) * 0.08
		if dir != Vector2.ZERO:
			score += dir.dot(_last_dir) * 4.0   # без дёрганья
			score += dir.dot((_goal - pos).normalized()) * 9.0   # идём к цели по прямой, а не кружим
		else:
			score -= 6.0   # стоять на месте — плохо
		if score > best_score:
			best_score = score
			best_dir = dir
	_last_dir = best_dir
	_drive(best_dir)


## Цель манёвра: точка простора подальше от толпы и стен — бежим к ней прямо, а не кружим вокруг врагов.
func _pick_goal(pos: Vector2, near: Array) -> void:
	var arena: float = Balance.ARENA_SIZE
	var best: Vector2 = Vector2(arena, arena) * 0.5
	var best_score: float = -INF
	for i: int in 14:
		var cand: Vector2 = Vector2(randf_range(80.0, arena - 80.0), randf_range(80.0, arena - 80.0))
		var sc: float = -cand.distance_to(pos) * 0.15
		for e: Array in near:
			var d: float = cand.distance_to(e[0])
			if d < 110.0:
				sc -= (110.0 - d) * 0.6
		var line_blocked: float = 0.0
		var heading: Vector2 = (cand - pos).normalized()
		for e: Array in near:
			var off: Vector2 = (e[0] as Vector2) - pos
			var along: float = off.dot(heading)
			if along > 0.0 and absf(off.dot(heading.orthogonal())) < 26.0 and along < pos.distance_to(cand):
				line_blocked += 1.0
		sc -= line_blocked * 14.0
		if sc > best_score:
			best_score = sc
			best = cand
	_goal = best
	_goal_left = 2.5


func _drive(dir: Vector2) -> void:
	_press(&"move_left", maxf(-dir.x, 0.0))
	_press(&"move_right", maxf(dir.x, 0.0))
	_press(&"move_up", maxf(-dir.y, 0.0))
	_press(&"move_down", maxf(dir.y, 0.0))


func _nearest(near: Array, pos: Vector2) -> Vector2:
	var best: Vector2 = near[0][0]
	for e: Array in near:
		if pos.distance_squared_to(e[0]) < pos.distance_squared_to(best):
			best = e[0]
	return best


## Желаемая дистанция до врагов: ближний бой — вплотную, стрелки — подальше.
func _want_range() -> float:
	var shortest: float = 110.0
	for w: Dictionary in GameState.weapons:
		var data: Dictionary = Balance.WEAPONS.get(w["id"], {})
		if data.has("reach"):
			shortest = minf(shortest, float(data["reach"]) * 0.6)
		elif data.has("radius"):
			shortest = minf(shortest, float(data["radius"]) * 0.6)
		elif data.has("range"):
			shortest = minf(shortest, float(data["range"]) * 0.7)
		elif data.has("proj_life"):
			shortest = minf(shortest, float(data["proj_life"]) * Balance.PROJECTILE_SPEED * 0.7)
	return shortest


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


func _weapon_power(id: StringName, tier: int) -> float:
	var data: Dictionary = Balance.WEAPONS.get(id, {})
	var dmg: float = float(data.get("damage", 5.0)) * float(data.get("pellets", 1)) * (1.0 + 0.8 * float(tier - 1))
	return dmg / maxf(float(data.get("cooldown", 1.0)), 0.05) * (1.15 if data.has("burn_dps") else 1.0)


func _avg_power() -> float:
	var total: float = 0.0
	for w: Dictionary in GameState.weapons:
		total += _weapon_power(w["id"], w["tier"])
	return total / maxf(float(GameState.weapons.size()), 1.0)


func _worst_weapon() -> int:
	var worst: int = -1
	var worst_power: float = INF
	for i: int in GameState.weapons.size():
		var w: Dictionary = GameState.weapons[i]
		var pw: float = _weapon_power(w["id"], w["tier"])
		if pw < worst_power:
			worst_power = pw
			worst = i
	return worst


func _offer_score(offer: Dictionary) -> float:
	var tier: int = offer["tier"]
	if offer["kind"] == &"weapon":
		var merge: float = 10.0 if GameState.find_weapon(offer["id"], tier) >= 0 else 0.0
		var power: float = _weapon_power(offer["id"], tier)
		if GameState.weapons.size() < Balance.WEAPON_SLOTS:
			if merge == 0.0 and GameState.weapons.size() >= 3 and power < _avg_power() * 0.9:
				return -50.0   # слабый хлам в слот не берём
			return 8.0 + power * 0.5 + merge
		if merge > 0.0:
			return 8.0 + merge
		var worst: int = _worst_weapon()
		var worst_power: float = _weapon_power(GameState.weapons[worst]["id"], GameState.weapons[worst]["tier"])
		if power > worst_power * 1.4 and GameState.weapons.size() > 1:
			return 6.0 + (power - worst_power) * 0.4   # замена слабого оружия
		return -50.0
	if offer["kind"] == &"item":
		var data: Dictionary = Balance.ITEMS[offer["id"]]
		var score: float = 3.0 + tier * 2.5
		for stat: StringName in data.get("mods", {}):
			var v: float = data["mods"][stat]
			score += STAT_WEIGHT.get(stat, 1.0) * v * (0.3 if v > 0.0 else 0.2)
		var fx: Dictionary = data.get("fx", {})
		for key: StringName in [&"pets", &"turrets", &"dogs", &"pigeons", &"mines", &"lamps", &"mortars", &"ghost_granny", &"ghost_drunk"]:
			if fx.has(key):
				score += 4.0
		return score
	return 4.0 + STAT_WEIGHT.get(offer["id"], 1.0) * 0.5


func _shop() -> void:
	# 1. слить одинаковые оружия
	for slot: int in GameState.weapons.size():
		if GameState.find_merge_partner(slot) >= 0:
			GameState.merge_weapons(slot)
			_ui.call("_refresh_shop")
			return
	var offers: Array[Dictionary] = GameState.shop_offers
	# 2. купить лучшее из доступного; если слоты забиты, а предложение сильнее худшего оружия — сначала сдать худшее
	var best: int = -1
	var best_score: float = -30.0
	for i: int in offers.size():
		if offers[i]["sold"]:
			continue
		var score: float = _offer_score(offers[i])
		if score <= best_score:
			continue
		if offers[i]["kind"] == &"weapon" and GameState.weapons.size() >= Balance.WEAPON_SLOTS and GameState.find_weapon(offers[i]["id"], offers[i]["tier"]) < 0:
			if GameState.coins < offers[i]["price"]:
				continue
		elif ShopLibrary.why_not(offers[i]) != "":
			continue
		best_score = score
		best = i
	if best >= 0:
		var offer: Dictionary = offers[best]
		if offer["kind"] == &"weapon" and GameState.weapons.size() >= Balance.WEAPON_SLOTS and GameState.find_weapon(offer["id"], offer["tier"]) < 0:
			GameState.recycle_weapon(_worst_weapon())
		_ui.call("_on_card_pressed", best)
		return
	# 3. заморозить дорогое, но нужное (оно переживёт реролл и волну)
	var locked_any: bool = false
	for offer: Dictionary in offers:
		if not offer["sold"] and not offer["locked"] and offer["price"] > GameState.coins and _offer_score(offer) >= 9.0:
			offer["locked"] = true
			locked_any = true
	if locked_any:
		_ui.call("_show_choices")
		return
	# 4. реролл, пока есть на что
	var cost: int = Balance.REROLL_BASE_COST + int(GameState.wave * Balance.REROLL_WAVE_FACTOR) + GameState.reroll_count * Balance.REROLL_STEP_COST
	if _rerolls < 25 and GameState.coins >= cost + 8:
		_rerolls += 1
		_ui.call("_on_reroll_pressed")
		return
	_ui.call("_on_next_pressed")
