extends Node
## БОТ-ИГРОК для фермы прогонов баланса. Играет забеги сам: движение (уворот, сбор говна), карточки уровней, Ларёк.
## Три уровня скилла (SKILLS): noob - рукожоп, mid - средний, pro - задрот. Профиль игрока не трогает (Profile.sandbox).
## Запуск без окна (не мешает работать):
##   Godot --headless --fixed-fps 60 --path . res://tools/bot/bot_runner.tscn -- --skill=pro --runs=5 --seed=1 --out=/abs/dir
## --fixed-fps 60: игровое время идёт ровно по 1/60 с за кадр, но так быстро, как тянет процессор.
## Каждый забег - JSON в --out. Сводка: python3 tools/bot/report.py <dir>. Ферма целиком: tools/bot/farm.sh.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
const GAME_TIMEOUT_SEC: float = 3600.0
const SHOP_ACTIONS_MAX: int = 40          # защита от зацикливания в Ларьке
const SKILLS: Dictionary = {
	# react - как часто бот пересматривает направление (с); noise - ошибка оценки позиции врагов (px);
	# mistake - шанс дёрнуться не туда при решении; look - насколько вперёд предсказывает (с);
	# see_proj - видит ли вражеские снаряды; shop/cards - как закупается и выбирает карточки.
	&"noob": {"dash": &"random", "react": 0.30, "dirs": 8, "noise": 22.0, "mistake": 0.12, "look": [0.3], "see_proj": false, "shop": &"random", "cards": &"random"},
	&"mid": {"dash": &"smart", "react": 0.12, "dirs": 12, "noise": 7.0, "mistake": 0.03, "look": [0.2, 0.5], "see_proj": true, "shop": &"greedy", "cards": &"weighted"},
	&"god": {"dash": &"smart", "react": 0.0, "dirs": 32, "noise": 0.0, "mistake": 0.0, "look": [0.1, 0.25, 0.45, 0.8], "see_proj": true, "shop": &"sets", "cards": &"weighted", "god": true},
	&"pro": {"dash": &"smart", "react": 0.0, "dirs": 24, "noise": 0.0, "mistake": 0.0, "look": [0.15, 0.4, 0.8], "see_proj": true, "shop": &"sets", "cards": &"weighted"},
}
# «Мозг» бота: веса манёвров. Подбираются обучением (tools/bot/train.py) и лежат в tools/bot/brain.json.
# Скилл (SKILLS) - это помехи поверх мозга: реакция, шум, ошибки, закупка. Мозг у всех уровней общий.
const BRAIN_DEFAULT: Dictionary = {
	"danger_w": 90.0, "danger_pad": 32.0, "proj_w": 10.0, "hazard_w": 30.0, "edge_w": 60.0, "wall_w": 200.0, "space_w": 0.12,
	"pickup_w": 0.25, "range_w": 0.08, "inertia_w": 4.0, "goal_w": 9.0, "orbit_w": 6.0, "orbit_flip_sec": 2.5,
	"gap_w": 40.0, "surround_at": 0.45, "surround_r": 90.0, "hp_caution": 1.0, "melee_bold": 0.3,
	"dash_surround": 0.6, "dash_proj_dist": 28.0, "dash_melee_dist": 16.0,
}
const BRAIN_PATH: String = "res://tools/bot/brain.json"
const SECTORS: int = 24   # круг вокруг героя для поиска дыр в окружении
const STAT_WEIGHT: Dictionary = {&"damage": 4.2, &"attack_speed": 3.6, &"max_hp": 3.4, &"armor": 3.0, &"crit": 1.6,
		&"speed": 2.0, &"dodge": 2.2, &"regen": 2.2, &"pickup": 0.8}
const DANGEROUS: Array[StringName] = [&"charger", &"bruiser", &"boss_zakhar", &"boss_minion", &"boss_mega_hamster", &"boss_rat_queen", &"boss_blue_whale"]

var _skill_id: StringName = &"mid"
var _skill: Dictionary = {}
var _brain: Dictionary = {}
var _orbit_sign: float = 1.0
var _orbit_left: float = 0.0
var _surround_max: float = 0.0   # макс. окружённость за волну (0..1), для отчёта
var _heroes: Array[StringName] = []
var _runs_total: int = 1
var _seed: int = 1
var _out_dir: String = ""
var _run_index: int = -1
var _hero: StringName = &"hobo"
var _level: Node = null
var _ui: Node = null
var _player: Node2D = null
var _running: bool = false
var _finished: bool = false
var _game_time: float = 0.0
var _shop_visits: int = 0
var _shop_actions: int = 0
var _waves: Array[Dictionary] = []
var _wave: Dictionary = {}
var _last_hp: float = 0.0
var _rerolls: int = 0
var _real_start: int = 0
# управление
var _projectiles: Array[Node] = []
var _hazards: Array[Node] = []
var _telegraphs: Array[Node] = []   # зоны будущих ударов (видит и обходит)   # лужи говна, облака вони: [узел], радиус берём из формы
var _frame: int = 0
var _last_dir: Vector2 = Vector2.ZERO
var _decide_left: float = 0.0
var _pos_hist: Array[Vector2] = []
var _escape_dir: Vector2 = Vector2.ZERO
var _escape_left: float = 0.0
var _goal: Vector2 = Vector2.ZERO
var _goal_left: float = 0.0
var _last_coverage: float = 0.0
var _dash_release: bool = false
var _dashes: int = 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	_parse_args()
	seed(_seed)
	DirAccess.make_dir_recursive_absolute(_out_dir)
	EventBus.player_died.connect(func() -> void: _end_run("death"))
	EventBus.run_won.connect(func() -> void: _end_run("win"))
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.player_hit.connect(_on_hit)
	_next_run.call_deferred()


func _parse_args() -> void:
	var args: Dictionary = {}
	for arg: String in OS.get_cmdline_user_args():
		var parts: PackedStringArray = arg.trim_prefix("--").split("=", true, 1)
		args[parts[0]] = parts[1] if parts.size() > 1 else "1"
	_skill_id = StringName(args.get("skill", "mid"))
	_skill = SKILLS.get(_skill_id, SKILLS[&"mid"])
	_runs_total = int(args.get("runs", "1"))
	GameState.danger = int(args.get("danger", "0"))
	_seed = int(args.get("seed", "1"))
	_out_dir = args.get("out", ProjectSettings.globalize_path("res://tools/_bot_runs/manual"))
	_brain = BRAIN_DEFAULT.duplicate()
	var brain_path: String = args.get("brain", ProjectSettings.globalize_path(BRAIN_PATH))
	if FileAccess.file_exists(brain_path):
		var loaded: Variant = JSON.parse_string(FileAccess.get_file_as_string(brain_path))
		if loaded is Dictionary:
			for key: String in loaded:
				if _brain.has(key):
					_brain[key] = float(loaded[key])
	var heroes: String = args.get("heroes", "all")
	if heroes == "all":
		_heroes.assign(Balance.CHARACTER_ORDER)
	else:
		for h: String in heroes.split(","):
			_heroes.append(StringName(h))


func _next_run() -> void:
	if _level != null:
		_level.queue_free()
		_level = null
		await get_tree().process_frame
		await get_tree().process_frame
	_run_index += 1
	if _run_index >= _runs_total:
		print("BOT DONE skill=%s seed=%d runs=%d" % [_skill_id, _seed, _runs_total])
		get_tree().quit()
		return
	get_tree().paused = false
	_hero = _heroes[randi() % _heroes.size()]
	GameState.character = _hero
	_level = MAIN.instantiate()
	get_tree().root.add_child(_level)
	_running = true
	_finished = false
	_game_time = 0.0
	_dashes = 0
	_shop_visits = 0
	_waves.clear()
	_wave = {}
	_real_start = Time.get_ticks_msec()
	await get_tree().process_frame
	await get_tree().process_frame
	var found: Array[Node] = _level.find_children("*", "LevelUpScreen", true, false)
	_ui = found[0] if not found.is_empty() else null
	_player = get_tree().get_first_node_in_group(&"player") as Node2D
	_last_hp = GameState.hp


func _on_hit(damage: float) -> void:
	if _wave.is_empty():
		return
	var key: String = String(GameState.last_damage_source) if GameState.last_damage_source != &"" else "?"
	var src: Dictionary = _wave["src"]
	src[key] = src.get(key, 0.0) + damage


func _on_wave_started(wave: int) -> void:
	_wave = {"w": wave, "kind": String(GameState.wave_kind), "min_hp": GameState.hp, "max_hp": GameState.max_hp,
			"dmg": 0.0, "kills0": GameState.kills, "src": {}, "t0": _game_time}
	_rerolls = 0
	_surround_max = 0.0


func _close_wave() -> void:
	if _wave.is_empty():
		return
	_wave["kills"] = GameState.kills - int(_wave["kills0"])
	_wave.erase("kills0")
	_wave["sec"] = snappedf(_game_time - float(_wave["t0"]), 0.1)
	_wave.erase("t0")
	_wave["min_hp_ratio"] = snappedf(float(_wave["min_hp"]) / maxf(float(_wave["max_hp"]), 1.0), 0.01)
	_wave["surround_max"] = snappedf(_surround_max, 0.01)
	_wave["coins"] = GameState.coins
	_wave["level"] = GameState.level
	_waves.append(_wave)
	_wave = {}


func _on_wave_ended(_wave_number: int) -> void:
	if _running:
		_close_wave()


func _end_run(result: String) -> void:
	if _finished or not _running:
		return
	_finished = true
	_running = false
	_close_wave()
	_release_keys()
	var weapons: Array = []
	for w: Dictionary in GameState.weapons:
		weapons.append({"id": String(w["id"]), "tier": w["tier"]})
	var sets: Dictionary = {}
	var counts: Dictionary = WeaponLibrary.class_counts(GameState.weapons)
	for c: StringName in counts:
		sets[String(c)] = counts[c]
	var items: Dictionary = {}
	for id: StringName in GameState.items:
		items[String(id)] = GameState.items[id]
	var record: Dictionary = {
		"hero": String(_hero), "skill": String(_skill_id), "danger": GameState.danger, "seed": _seed, "run": _run_index, "result": result,
		"wave": GameState.wave, "waves_total": Balance.WAVE_COUNT, "game_sec": snappedf(_game_time, 0.1),
		"shop_visits": _shop_visits, "dashes": _dashes, "clean_waves": GameState.clean_waves, "best_streak": snappedf(GameState.best_streak_sec, 0.1), "killer": String(GameState.last_damage_source) if result == "death" else "",
		"surrounded_at_end": snappedf(_last_coverage, 0.01), "hp_end_ratio": snappedf(GameState.hp / maxf(GameState.max_hp, 1.0), 0.01), "level": GameState.level,
		"kills": GameState.kills, "weapons": weapons, "sets": sets, "items": items, "waves": _waves.duplicate(true),
		"real_sec": snappedf((Time.get_ticks_msec() - _real_start) / 1000.0, 0.1),
	}
	var path: String = _out_dir.path_join("%s_s%d_r%d.json" % [_skill_id, _seed, _run_index])
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(record))
		file.close()
	print("RUN %s %s %s wave %d game %.0fs real %.0fs" % [_skill_id, _hero, result, GameState.wave, _game_time, record["real_sec"]])
	await get_tree().create_timer(0.5).timeout
	_next_run()


func _release_keys() -> void:
	for action: StringName in [&"move_left", &"move_right", &"move_up", &"move_down"]:
		Input.action_release(action)


func _physics_process(delta: float) -> void:
	_frame += 1
	if not _running or _player == null or not is_instance_valid(_player):
		return
	if get_tree().paused:
		_release_keys()
		return
	_game_time += delta
	if _dash_release:
		_dash_release = false
		Input.action_release(&"dash")
	if not _wave.is_empty():
		if GameState.hp < _last_hp:
			_wave["dmg"] = float(_wave["dmg"]) + _last_hp - GameState.hp
		_wave["min_hp"] = minf(float(_wave["min_hp"]), GameState.hp)
	_last_hp = GameState.hp
	if _game_time > GAME_TIMEOUT_SEC:
		_end_run("timeout")
		return
	_steer(delta)


# ---------------------------------------------------------------- движение

func _steer(delta: float) -> void:
	var pos: Vector2 = _player.global_position
	var arena: float = Balance.ARENA_SIZE
	_pos_hist.append(pos)
	if _pos_hist.size() > 36:
		_pos_hist.pop_front()
	if _escape_left > 0.0:
		_escape_left -= delta
		_drive(_escape_dir)
		return
	_decide_left -= delta
	if _decide_left > 0.0:   # медленная реакция: держим прежнее направление
		_drive(_last_dir)
		return
	_decide_left = float(_skill["react"])
	var enemies: Array[Node] = get_tree().get_nodes_in_group(&"enemies")
	if _skill["see_proj"]:
		_scan_threats()
	else:
		_projectiles = []
		_hazards = []
	var noise: float = float(_skill["noise"])
	var speed: float = Balance.PLAYER_MOVE_SPEED * GameState.move_speed_mult
	var near: Array = []   # [pos, vel, danger]
	for node: Node in enemies:
		var enemy: Node2D = node as Node2D
		var sight: float = Balance.DARKNESS_RADIUS + 12.0 if GameState.wave_mod == &"darkness" else 200.0   # в темноте не видно
		if enemy.global_position.distance_squared_to(pos) < sight * sight:
			var vel: Vector2 = (enemy as CharacterBody2D).velocity if enemy is CharacterBody2D else Vector2.ZERO
			var id: Variant = enemy.get("enemy_id")
			var danger: float = 1.8 if id != null and DANGEROUS.has(id) else 1.0
			var seen: Vector2 = enemy.global_position + Vector2(randf_range(-noise, noise), randf_range(-noise, noise))
			near.append([seen, vel, danger])
	var pickups: Array = []
	for node: Node in get_tree().get_nodes_in_group(&"pickups"):
		var pk: Node2D = node as Node2D
		if pk.global_position.distance_squared_to(pos) < 220.0 * 220.0:
			pickups.append(pk.global_position)
	var crowd: int = 0
	for e: Array in near:
		if pos.distance_to(e[0]) < 38.0:
			crowd += 1
	# зажали толпой: пробиваемся в сторону самого пустого просвета
	if _pos_hist.size() >= 36 and crowd >= 1 and _pos_hist[0].distance_to(pos) < 14.0:
		_escape_dir = _escape_direction(pos, near)
		_escape_left = 0.7
		_pos_hist.clear()
		return
	_goal_left -= maxf(float(_skill["react"]), delta)
	if _goal_left <= 0.0 or pos.distance_to(_goal) < 30.0:
		_pick_goal(pos, near)
	var b: Dictionary = _brain
	var want: float = _want_range()
	var danger_r: float = clampf(want + float(b["danger_pad"]), 55.0, 110.0)
	var bold: float = float(b["melee_bold"]) if want < 70.0 and GameState.hp > GameState.max_hp * 0.5 else 1.0   # ближнему бою надо подходить
	var hp_ratio: float = clampf(GameState.hp / maxf(GameState.max_hp, 1.0), 0.0, 1.0)
	var caution: float = 1.0 + float(b["hp_caution"]) * (1.0 - hp_ratio)   # мало ХП - осторожнее
	var dirs: int = int(_skill["dirs"])
	var looks: Array = _skill["look"]
	var calm: bool = true
	for e: Array in near:
		if pos.distance_to(e[0]) < danger_r:
			calm = false
			break
	var centroid: Vector2 = Vector2.ZERO
	for e: Array in near:
		centroid += e[0]
	if not near.is_empty():
		centroid /= near.size()
	# окружение: какая доля круга вокруг занята врагами и где самая широкая дыра
	var ring: Array = _ring_gap(pos, near, float(b["surround_r"]))
	var coverage: float = ring[0]
	var gap_dir: Vector2 = ring[1]
	_last_coverage = coverage
	_surround_max = maxf(_surround_max, coverage)
	var surrounded: bool = coverage >= float(b["surround_at"])
	# стрейф: обходим толпу по кругу, направление обхода иногда меняем (и у стены)
	_orbit_left -= maxf(float(_skill["react"]), delta)
	if _orbit_left <= 0.0:
		_orbit_left = float(b["orbit_flip_sec"]) * randf_range(0.6, 1.4)
		_orbit_sign = -_orbit_sign if randf() < 0.5 else _orbit_sign
	var tangent: Vector2 = Vector2.ZERO
	if not near.is_empty() and pos.distance_to(centroid) > 1.0:
		tangent = (pos - centroid).normalized().orthogonal() * _orbit_sign
		var ahead: Vector2 = pos + tangent * 60.0
		if ahead.x < 50.0 or ahead.y < 50.0 or ahead.x > arena - 50.0 or ahead.y > arena - 50.0:
			_orbit_sign = -_orbit_sign
			tangent = -tangent
	var best_dir: Vector2 = Vector2.ZERO
	var best_score: float = -INF
	for i: int in dirs + 1:
		var dir: Vector2 = Vector2.ZERO if i == dirs else Vector2.from_angle(TAU * i / dirs)
		var score: float = 0.0
		for t: float in looks:
			var me: Vector2 = pos + dir * speed * t
			var w: float = 1.0 if t < 0.6 else 0.7
			for e: Array in near:
				var d: float = me.distance_to((e[0] as Vector2) + (e[1] as Vector2) * t)
				if d < danger_r:
					score -= w * float(e[2]) * pow((danger_r - d) / danger_r, 2.0) * float(b["danger_w"]) * bold * caution
			for node: Node in _projectiles:
				if not is_instance_valid(node):
					continue
				var proj: Node2D = node as Node2D
				var heading: Vector2 = proj.get("_direction")
				var pp: Vector2 = proj.global_position + heading * float(proj.get("_speed")) * t
				var dd: float = me.distance_to(pp)
				if dd < 22.0:
					score -= w * (22.0 - dd) * float(b["proj_w"])
			for node: Node in _telegraphs:
				if is_instance_valid(node) and (node as Telegraph).contains(me):
					score -= w * float(b["hazard_w"]) * 1.5
			for node: Node in _hazards:
				if not is_instance_valid(node):
					continue
				var hz: Node2D = node as Node2D
				var hr: float = _hazard_radius(hz) + 6.0
				var hd: float = me.distance_to(hz.global_position)
				if hd < hr:
					score -= w * (hr - hd) / hr * float(b["hazard_w"])
			var edge: float = minf(minf(me.x, arena - me.x), minf(me.y, arena - me.y))
			if edge < 70.0:
				score -= w * pow((70.0 - edge) / 70.0, 2.0) * float(b["edge_w"])
			if edge < 44.0:
				score -= w * float(b["wall_w"])
		if not near.is_empty():
			score += (pos + dir * speed * 0.8).distance_to(centroid) * float(b["space_w"])
		if calm and not pickups.is_empty():
			var closest: float = 9999.0
			for pk: Vector2 in pickups:
				closest = minf(closest, (pos + dir * speed * 0.5).distance_to(pk))
			score -= closest * float(b["pickup_w"])
		elif calm and not near.is_empty():
			score -= absf((pos + dir * speed * 0.5).distance_to(_nearest(near, pos)) - want) * float(b["range_w"])
		if dir != Vector2.ZERO:
			score += dir.dot(_last_dir) * float(b["inertia_w"])
			score += dir.dot((_goal - pos).normalized()) * float(b["goal_w"]) * (0.3 if surrounded else 1.0)
			score += dir.dot(tangent) * float(b["orbit_w"])
			if surrounded:
				score += dir.dot(gap_dir) * float(b["gap_w"]) * coverage   # кольцо смыкается - рвёмся в дыру
		else:
			score -= 1000.0 if not near.is_empty() else 6.0   # стоять среди врагов нельзя
		if score > best_score:
			best_score = score
			best_dir = dir
	if randf() < float(_skill["mistake"]):
		best_dir = Vector2.from_angle(randf() * TAU)   # дёрнулся не туда
	_maybe_dash(pos, near, coverage, gap_dir, best_dir, hp_ratio)
	_last_dir = best_dir
	_drive(best_dir)


## Вражеские снаряды и лужи/облака: игра кладёт их в корень текущей сцены (у бота это сам бот), не в уровень.
func _scan_threats() -> void:
	if _frame % 2 != 0:
		return
	_projectiles = []
	_hazards = []
	_telegraphs = []
	var ground: Node = _level.get_node_or_null(^"Ground") if _level != null else null
	if ground != null:
		for child: Node in ground.get_children():
			if child is Telegraph:
				_telegraphs.append(child)
	for holder: Node in [get_tree().current_scene, _level]:
		if holder == null:
			continue
		for child: Node in holder.get_children():
			if child is EnemyProjectile and child.get("_active"):
				_projectiles.append(child)
			elif child is TimedHazard:
				_hazards.append(child)


func _hazard_radius(hz: Node2D) -> float:
	var shape_node: Variant = hz.get("_shape")
	if shape_node is CollisionShape2D and (shape_node as CollisionShape2D).shape is CircleShape2D:
		return ((shape_node as CollisionShape2D).shape as CircleShape2D).radius
	return 16.0


## Рывок: задрот рвётся в дыру, когда кольцо смыкается, и уходит из-под снаряда/удара; рукожоп жмёт наугад.
func _maybe_dash(pos: Vector2, near: Array, coverage: float, gap_dir: Vector2, best_dir: Vector2, hp_ratio: float) -> void:
	var mode: StringName = _skill["dash"]
	var dir: Vector2 = Vector2.ZERO
	if mode == &"random":
		if randf() < 0.02:
			dir = best_dir if best_dir != Vector2.ZERO else Vector2.from_angle(randf() * TAU)
	else:
		var b: Dictionary = _brain
		if coverage >= float(b["dash_surround"]) and gap_dir != Vector2.ZERO:
			dir = gap_dir
		else:
			for node: Node in _projectiles:
				if not is_instance_valid(node):
					continue
				var proj: Node2D = node as Node2D
				var heading: Vector2 = proj.get("_direction")
				var to_me: Vector2 = pos - proj.global_position
				if to_me.length() < float(b["dash_proj_dist"]) and heading.dot(to_me.normalized()) > 0.8:
					dir = heading.orthogonal() if heading.orthogonal().dot(best_dir) >= 0.0 else -heading.orthogonal()
					break
			if dir == Vector2.ZERO and hp_ratio < 0.4:
				for e: Array in near:
					if pos.distance_to(e[0]) < float(b["dash_melee_dist"]):
						dir = best_dir
						break
	if dir == Vector2.ZERO:
		return
	_drive(dir)
	Input.action_press(&"dash")
	_dash_release = true
	_dashes += 1


## Окружённость: [доля секторов круга радиуса r, занятых врагами; направление в центр самой широкой дыры].
func _ring_gap(pos: Vector2, near: Array, r: float) -> Array:
	var busy: Array[bool] = []
	busy.resize(SECTORS)
	busy.fill(false)
	var count: int = 0
	for e: Array in near:
		var off: Vector2 = (e[0] as Vector2) - pos
		var dist: float = off.length()
		if dist > r or dist < 0.01:
			continue
		var spread: int = 1 if dist > r * 0.5 else 2   # близкий враг перекрывает больше круга
		var sector: int = int(floor(posmod(off.angle(), TAU) / TAU * SECTORS))
		for k: int in range(-spread + 1, spread):
			busy[posmod(sector + k, SECTORS)] = true
	for v: bool in busy:
		if v:
			count += 1
	if count == 0:
		return [0.0, Vector2.ZERO]
	if count == SECTORS:
		return [1.0, _escape_direction(pos, near)]
	var best_len: int = 0
	var best_mid: float = 0.0
	for start: int in SECTORS:
		if busy[start] or not busy[posmod(start - 1, SECTORS)]:
			continue
		var length: int = 0
		while length < SECTORS and not busy[posmod(start + length, SECTORS)]:
			length += 1
		if length > best_len:
			best_len = length
			best_mid = (start + length * 0.5) / float(SECTORS) * TAU
	var arena: float = Balance.ARENA_SIZE
	var dir: Vector2 = Vector2.from_angle(best_mid)
	var after: Vector2 = pos + dir * 50.0
	if after.x < 30.0 or after.y < 30.0 or after.x > arena - 30.0 or after.y > arena - 30.0:
		dir = _escape_direction(pos, near)   # дыра в стену - не дыра
	return [float(count) / SECTORS, dir]


func _escape_direction(pos: Vector2, near: Array) -> Vector2:
	var arena: float = Balance.ARENA_SIZE
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
	return pick


## Цель манёвра: точка простора подальше от толпы и стен.
func _pick_goal(pos: Vector2, near: Array) -> void:
	var arena: float = Balance.ARENA_SIZE
	var best: Vector2 = Vector2(arena, arena) * 0.5
	var best_score: float = -INF
	for i: int in 14:
		var cand: Vector2 = Vector2(randf_range(80.0, arena - 80.0), randf_range(80.0, arena - 80.0))
		var sc: float = -cand.distance_to(pos) * 0.15
		var heading: Vector2 = (cand - pos).normalized()
		for e: Array in near:
			var d: float = cand.distance_to(e[0])
			if d < 110.0:
				sc -= (110.0 - d) * 0.6
			var off: Vector2 = (e[0] as Vector2) - pos
			var along: float = off.dot(heading)
			if along > 0.0 and absf(off.dot(heading.orthogonal())) < 26.0 and along < pos.distance_to(cand):
				sc -= 14.0
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


func _press(action: StringName, strength: float) -> void:
	if strength > 0.05:
		Input.action_press(action, strength)
	else:
		Input.action_release(action)


func _nearest(near: Array, pos: Vector2) -> Vector2:
	var best: Vector2 = near[0][0]
	for e: Array in near:
		if pos.distance_squared_to(e[0]) < pos.distance_squared_to(best):
			best = e[0]
	return best


## Желаемая дистанция до врагов: ближний бой - вплотную, стрелки - подальше.
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


# ---------------------------------------------------------------- экраны между волнами

func _process(_delta: float) -> void:
	if not _running or _ui == null or not is_instance_valid(_ui):
		return
	var root: Control = _ui.get("_root")
	if not root.visible:
		_shop_actions = 0
		return
	if _ui.get("_start_mode"):
		_ui.call("_on_card_pressed", randi() % 4)
	elif _ui.get("_shop_mode"):
		if _shop_actions == 0:
			_shop_visits += 1
		_shop_actions += 1
		if _shop_actions > SHOP_ACTIONS_MAX:
			_ui.call("_on_next_pressed")
			return
		_shop()
	else:
		_level_up()


func _level_up() -> void:
	var offers: Array = _ui.get("_stat_offers")
	if offers.is_empty():
		return
	if _skill["cards"] == &"random":
		_ui.call("_on_card_pressed", randi() % offers.size())
		return
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
	var dmg: float = float(data.get("damage", 5.0)) * float(WeaponLibrary.stat(id, tier, "pellets", 1)) * Balance.WEAPON_TIER_DAMAGE[tier - 1]
	return dmg / maxf(float(data.get("cooldown", 1.0)) * Balance.WEAPON_TIER_COOLDOWN[tier - 1], 0.05) * (1.15 if data.has("burn_dps") else 1.0)


func _avg_power() -> float:
	var total: float = 0.0
	for w: Dictionary in GameState.weapons:
		total += _weapon_power(w["id"], w["tier"])
	return total / maxf(float(GameState.weapons.size()), 1.0)


func _worst_weapon() -> int:
	var worst: int = -1
	var worst_power: float = INF
	for i: int in GameState.weapons.size():
		var pw: float = _weapon_power(GameState.weapons[i]["id"], GameState.weapons[i]["tier"])
		if pw < worst_power:
			worst_power = pw
			worst = i
	return worst


## Синергия с наборами (только у задрота): чем больше уже оружий этого класса, тем ценнее.
func _set_bonus_score(weapon_id: StringName) -> float:
	if _skill["shop"] != &"sets":
		return 0.0
	var counts: Dictionary = WeaponLibrary.class_counts(GameState.weapons)
	var score: float = 0.0
	for c: StringName in WeaponLibrary.classes(weapon_id):
		score += minf(float(counts.get(c, 0)), 4.0) * 3.0
	return score


func _offer_score(offer: Dictionary) -> float:
	var tier: int = offer["tier"]
	if offer["kind"] == &"weapon":
		var merge: float = 10.0 if GameState.find_weapon(offer["id"], tier) >= 0 else 0.0
		var power: float = _weapon_power(offer["id"], tier)
		var synergy: float = _set_bonus_score(offer["id"])
		if GameState.weapons.size() < Balance.WEAPON_SLOTS:
			if merge == 0.0 and GameState.weapons.size() >= 3 and power < _avg_power() * 0.9 and synergy < 6.0:
				return -50.0
			return 8.0 + power * 0.5 + merge + synergy
		if merge > 0.0:
			return 8.0 + merge + synergy
		var worst: int = _worst_weapon()
		var worst_power: float = _weapon_power(GameState.weapons[worst]["id"], GameState.weapons[worst]["tier"])
		if power > worst_power * 1.4 and GameState.weapons.size() > 1:
			return 6.0 + (power - worst_power) * 0.4 + synergy
		return -50.0
	if offer["kind"] == &"item":
		var data: Dictionary = Balance.ITEMS[offer["id"]]
		var score: float = 3.0 + tier * 2.5
		for stat: StringName in data.get("mods", {}):
			var v: float = data["mods"][stat]
			score += STAT_WEIGHT.get(stat, 1.0) * v * (0.3 if v > 0.0 else 0.2)
		for key: StringName in [&"pets", &"turrets", &"dogs", &"pigeons", &"mines", &"lamps", &"mortars", &"ghost_granny", &"ghost_drunk"]:
			if data.get("fx", {}).has(key):
				score += 4.0
		return score
	return 4.0 + STAT_WEIGHT.get(offer["id"], 1.0) * 0.5


func _shop() -> void:
	var offers: Array[Dictionary] = GameState.shop_offers
	if _skill["shop"] == &"random":
		# рукожоп: берёт что попало, пока хватает, без слияний и рерроллов
		var can: Array[int] = []
		for i: int in offers.size():
			if not offers[i]["sold"] and ShopLibrary.why_not(offers[i]) == "":
				can.append(i)
		if not can.is_empty() and randf() < 0.75:
			_ui.call("_on_card_pressed", can[randi() % can.size()])
		else:
			_ui.call("_on_next_pressed")
		return
	for slot: int in GameState.weapons.size():   # слить одинаковые
		if GameState.find_merge_partner(slot) >= 0:
			GameState.merge_weapons(slot)
			_ui.call("_refresh_shop")
			return
	var best: int = -1
	var best_score: float = -30.0
	for i: int in offers.size():
		if offers[i]["sold"]:
			continue
		var score: float = _offer_score(offers[i])
		if score <= best_score:
			continue
		var full_swap: bool = offers[i]["kind"] == &"weapon" and GameState.weapons.size() >= Balance.WEAPON_SLOTS and GameState.find_weapon(offers[i]["id"], offers[i]["tier"]) < 0
		if full_swap:
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
	var locked_any: bool = false   # заморозить дорогое, но нужное
	for offer: Dictionary in offers:
		if not offer["sold"] and not offer["locked"] and offer["price"] > GameState.coins and _offer_score(offer) >= 9.0:
			offer["locked"] = true
			locked_any = true
	if locked_any:
		_ui.call("_show_choices")
		return
	var cost: int = _ui.call("_reroll_cost")
	var reroll_cap: int = 25 if _skill["shop"] == &"sets" else 6
	if _rerolls < reroll_cap and GameState.coins >= cost + 8:
		_rerolls += 1
		_ui.call("_on_reroll_pressed")
		return
	_ui.call("_on_next_pressed")
