class_name WaveManager
extends Node
## Ведёт забег как в Brotato: 15 волн по таймеру, группы врагов с красными крестами,
## элиты/орды в окнах 11–12 / 14–15 / 17–18, боссы на 20-й. Между волнами — уровни, затем «Дальше».
## См. docs/BROTATO_REFERENCE.md.

@export var spawner: Spawner
@export var player: Node2D

var _fighting: bool = false
var _spawn_times: Array[float] = []
var _wave_elapsed: float = 0.0
var _special: Dictionary = {}
var _bosses_alive: int = 0
var _elite_spawned: bool = false
var _thief_at: float = -1.0   # Н21: секунда волны, когда придёт щипач (-1 - не придёт)
var _bosses_spawned: bool = false


var _camp_timer: float = 0.0
var _camp_warned: bool = false


var _last_mod: StringName = &""


func _ready() -> void:
	EventBus.endless_requested.connect(_on_endless_requested)
	_special = WaveRules.roll_special_waves()
	GameState.special_waves = _special
	EventBus.next_wave_requested.connect(_on_next_wave_requested)
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(func() -> void: _fighting = false)
	# Первая волна стартует после выбора стартового оружия (первый perk_chosen).
	EventBus.perk_chosen.connect(func(_id: StringName) -> void: _start_wave(1), CONNECT_ONE_SHOT)


## Вид волны (normal/elite/horde/boss) — нужен экрану между волнами для превью следующей.
func wave_kind(wave: int) -> StringName:
	if GameState.mode == &"endless":   # Н32: босс-рандом каждые 5 волн, элита каждую 3-ю
		if wave % Balance.ENDLESS_BOSS_EVERY == 0:
			return &"boss"
		return &"elite" if wave >= Balance.MODE_ENDLESS_ELITE_FROM and wave % Balance.ENDLESS_ELITE_EVERY == 0 else &"normal"
	if wave > Balance.WAVE_COUNT:
		if wave % Balance.ENDLESS_BOSS_EVERY == 0:
			return &"boss"
		return &"elite" if wave % Balance.ENDLESS_ELITE_EVERY == 0 else &"normal"
	if int(WaveRules.danger_v("early_elite")) == wave:
		return &"elite"
	return _special.get(wave, &"normal")


func _process(delta: float) -> void:
	if not _fighting or not GameState.run_active:
		return
	_wave_elapsed += delta
	GameState.time += delta
	GameState.wave_time_left = maxf(WaveRules.duration_sec(GameState.wave) - _wave_elapsed, 0.0)
	_spawn_due_groups()
	if _thief_at >= 0.0 and _wave_elapsed >= _thief_at:
		_thief_at = -1.0
		spawner.spawn_single(&"thief", WaveRules.hp_mult(GameState.wave))
	_spawn_special_units()
	_camp_raid(delta)
	if GameState.wave_kind != &"boss" and GameState.wave_time_left <= 0.0:
		_end_wave()


## Анти-кемпинг: пока игрок стоит, вокруг него появляются новые группы — стоять нельзя, надо маневрировать.
func _camp_raid(delta: float) -> void:
	if GameState.wave < 2 or GameState.still_sec < Balance.CAMP_WAIT_SEC:
		_camp_timer = 0.0
		return
	if _camp_timer == 0.0 and not _camp_warned:
		_camp_warned = true
		var camper: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		if camper != null:
			HitFx.popup(get_tree(), camper.global_position + Vector2(0.0, -22.0), "НЕ СТОЙ, БОМЖ! ОБЛАВА!", Color(1.0, 0.1, 0.2), 14.0, 1.2)
	_camp_timer += delta
	if _camp_timer >= Balance.CAMP_RAID_PERIOD_SEC:
		_camp_timer = 0.0001
		var player2: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		if player2 == null:
			return
		var wave: int = GameState.wave
		var enemy_id: StringName = WaveRules.pick_enemy_id(wave)
		var size: int = maxi(roundi(WaveRules.group_size(wave) * float(Balance.ENEMIES[enemy_id].get("group_mult", 1.0))), 2)
		spawner.spawn_group_near(enemy_id, size, WaveRules.hp_mult(wave), player2.global_position)


func _start_wave(wave: int) -> void:
	GameState.wave = wave
	GameState.wave_kind = wave_kind(wave)
	GameState.wave_mod = GameState.pending_mod   # модификатор - только с рулетки (куча-лотерея)
	GameState.pending_mod = &""
	GameState.season = WaveRules.roll_season(wave, GameState.wave_kind)
	GameState.wave_note = ""
	_wave_elapsed = 0.0
	_camp_warned = false
	GameState.wave_time_left = WaveRules.duration_sec(wave)
	_spawn_times = WaveRules.spawn_times(wave, GameState.wave_kind)
	_elite_spawned = false
	_thief_at = randf_range(Balance.THIEF_SPAWN_AT.x, Balance.THIEF_SPAWN_AT.y) if GameState.wave_kind == &"normal" and wave >= Balance.THIEF_FROM_WAVE and randf() < Balance.THIEF_CHANCE else -1.0
	_bosses_spawned = false
	_bosses_alive = 0
	_fighting = true
	@warning_ignore("integer_division")
	var bins: int = Balance.BIN_COUNT_BASE + (wave - 1) / Balance.BIN_COUNT_WAVES_PER_EXTRA
	for i: int in bins:
		spawner.spawn_single(&"trash_bin", 1.0)
	EventBus.wave_started.emit(wave)


func _spawn_due_groups() -> void:
	var wave: int = GameState.wave
	while not _spawn_times.is_empty() and _spawn_times[0] <= _wave_elapsed:
		_spawn_times.remove_at(0)
		var enemy_id: StringName = _pick_limited(wave)
		var size: int = maxi(roundi(WaveRules.group_size(wave) * float(Balance.ENEMIES[enemy_id].get("group_mult", 1.0))), 1)
		spawner.spawn_group(enemy_id, size, WaveRules.hp_mult(wave))


## Выбор типа врага с лимитом лекарей: не больше 4 живых одновременно.
func _pick_limited(wave: int) -> StringName:
	var id: StringName = WaveRules.pick_enemy_id(wave)
	for attempt: int in 6:
		if id != &"healer":
			return id
		var alive: int = 0
		for node: Node in get_tree().get_nodes_in_group(&"enemies"):
			if (node as EnemyBase) != null and (node as EnemyBase).enemy_id == &"healer":
				alive += 1
		if alive < 4:
			return id
		id = WaveRules.pick_enemy_id(wave)
	return &"squid_gopnik"


func _spawn_special_units() -> void:
	var wave: int = GameState.wave
	if GameState.wave_kind == &"elite" and not _elite_spawned and _wave_elapsed >= Balance.ELITE_SPAWN_SEC:
		_elite_spawned = true
		var elite: StringName = Balance.ELITE_POOL[randi() % Balance.ELITE_POOL.size()]
		spawner.spawn_single(elite, WaveRules.hp_mult(wave) * Balance.ELITE_HP_MULT)
		EventBus.boss_spawned.emit(elite)
	elif GameState.wave_kind == &"boss" and not _bosses_spawned and _wave_elapsed >= Balance.FINAL_BOSS_SPAWN_SEC:
		_bosses_spawned = true
		var pool: Array[StringName] = Balance.FINAL_BOSS_POOL.duplicate()
		pool.shuffle()
		var count: int = Balance.FINAL_BOSS_MAX if WaveRules.danger_v("both_bosses") else randi_range(1, Balance.FINAL_BOSS_MAX)
		for i: int in count:
			spawner.spawn_single(pool[i], WaveRules.hp_mult(wave) * Balance.BOSS_HP_MULT)
			_bosses_alive += 1
			EventBus.boss_spawned.emit(pool[i])


func _on_enemy_died(enemy_id: StringName, at: Vector2) -> void:
	if Balance.ELITE_POOL.has(enemy_id) and GameState.wave_kind == &"elite":
		_elite_reward(at)
	if GameState.wave_kind == &"boss" and Balance.FINAL_BOSS_POOL.has(enemy_id):
		_bosses_alive -= 1
		if _bosses_alive <= 0 and _bosses_spawned:
			if GameState.endless:
				_end_wave()   # в бесконечности боссы - просто веха, идём дальше
			else:
				_win()


## Награда за убитую элиту: куча говна и бесплатный предмет (тир растёт с волной).
func _elite_reward(at: Vector2) -> void:
	for i: int in Balance.ELITE_REWARD_XP_DROPS:
		EventBus.xp_drop_requested.emit(at + Vector2.from_angle(randf() * TAU) * randf_range(4.0, 20.0), Balance.ELITE_REWARD_XP_VALUE)
	var item_id: StringName = ItemLibrary.roll_free_item(GameState.wave + 4)
	if item_id == &"":
		return
	GameState.add_item(item_id)
	HitFx.popup(get_tree(), at + Vector2(0.0, -18.0), "ЭЛИТА ВЫРОНИЛА: %s" % ItemLibrary.title(item_id), Color(0.968627, 1.0, 0.0), 14.0, 1.8)


func _end_wave() -> void:
	if GameState.wave_mod != &"":
		_last_mod = GameState.wave_mod
	GameState.wave_mod = &""
	GameState.season = &""
	_fighting = false
	spawner.clear_all()
	for node: Node in get_tree().get_nodes_in_group(&"pickups"):
		var pickup: XpPickup = node as XpPickup
		if pickup != null:
			pickup.attract(player)
	await get_tree().create_timer(Balance.WAVE_END_COLLECT_SEC, false).timeout
	if GameState.run_active and GameState.mode == &"duel" and GameState.wave >= Balance.DUEL_WAVES:
		EventBus.duel_round_over.emit()   # Н31: раунд пройден
		return
	if GameState.run_active:
		var bonus: int = Balance.WAVE_END_BONUS_XP_BASE + Balance.WAVE_END_BONUS_XP_PER_WAVE * GameState.wave
		EventBus.xp_collected.emit(bonus)
		HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -16.0), "+%d XP: ПОКОПАЛСЯ В ПОМОЙКЕ" % bonus, Color(0.968627, 1, 0, 1), 18.0, 1.4)
		if player.has_method(&"heal_full"):
			player.call(&"heal_full")
		var gift: String = GameState.closed_gift()   # Н33: без Ларька - находка после волны
		if gift != "":
			HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -30.0), gift, Color(0.22, 1.0, 0.08), 18.0, 2.2, true)
		EventBus.wave_ended.emit(GameState.wave)


func _win() -> void:
	_fighting = false
	spawner.clear_all()
	GameState.run_active = false
	EventBus.run_won.emit()


## Бесконечный режим: после победы продолжаем - сначала Ларёк, потом 16-я волна и дальше.
func _on_endless_requested() -> void:
	GameState.endless = true
	GameState.run_active = true
	get_tree().paused = false
	EventBus.wave_ended.emit(GameState.wave)


func _on_next_wave_requested() -> void:
	if GameState.roulette_pending:   # вступил в кучу: сначала рулетка
		GameState.roulette_pending = false
		EventBus.roulette_requested.emit()
		GameState.pending_mod = await EventBus.roulette_done
	_start_wave(GameState.wave + 1)
