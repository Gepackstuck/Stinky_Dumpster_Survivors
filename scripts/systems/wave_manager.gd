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
var _bosses_spawned: bool = false


func _ready() -> void:
	_special = WaveRules.roll_special_waves()
	GameState.special_waves = _special
	EventBus.next_wave_requested.connect(_on_next_wave_requested)
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(func() -> void: _fighting = false)
	# Первая волна стартует после выбора стартового оружия (первый perk_chosen).
	EventBus.perk_chosen.connect(func(_id: StringName) -> void: _start_wave(1), CONNECT_ONE_SHOT)


## Вид волны (normal/elite/horde/boss) — нужен экрану между волнами для превью следующей.
func wave_kind(wave: int) -> StringName:
	return _special.get(wave, &"normal")


func _process(delta: float) -> void:
	if not _fighting or not GameState.run_active:
		return
	_wave_elapsed += delta
	GameState.time += delta
	GameState.wave_time_left = maxf(WaveRules.duration_sec(GameState.wave) - _wave_elapsed, 0.0)
	_spawn_due_groups()
	_spawn_special_units()
	if GameState.wave_kind != &"boss" and GameState.wave_time_left <= 0.0:
		_end_wave()


func _start_wave(wave: int) -> void:
	GameState.wave = wave
	GameState.wave_kind = wave_kind(wave)
	GameState.wave_note = ""
	_wave_elapsed = 0.0
	GameState.wave_time_left = WaveRules.duration_sec(wave)
	_spawn_times = WaveRules.spawn_times(wave, GameState.wave_kind)
	_elite_spawned = false
	_bosses_spawned = false
	_bosses_alive = 0
	_fighting = true
	EventBus.wave_started.emit(wave)


func _spawn_due_groups() -> void:
	var wave: int = GameState.wave
	while not _spawn_times.is_empty() and _spawn_times[0] <= _wave_elapsed:
		_spawn_times.remove_at(0)
		var enemy_id: StringName = WaveRules.pick_enemy_id(wave)
		var size: int = maxi(roundi(WaveRules.group_size(wave) * float(Balance.ENEMIES[enemy_id].get("group_mult", 1.0))), 1)
		spawner.spawn_group(enemy_id, size, WaveRules.hp_mult(wave))


func _spawn_special_units() -> void:
	var wave: int = GameState.wave
	if GameState.wave_kind == &"elite" and not _elite_spawned and _wave_elapsed >= Balance.ELITE_SPAWN_SEC:
		_elite_spawned = true
		spawner.spawn_single(Balance.ELITE_ID, WaveRules.hp_mult(wave))
	elif GameState.wave_kind == &"boss" and not _bosses_spawned and _wave_elapsed >= Balance.FINAL_BOSS_SPAWN_SEC:
		_bosses_spawned = true
		var pool: Array[StringName] = Balance.FINAL_BOSS_POOL.duplicate()
		pool.shuffle()
		var count: int = randi_range(1, pool.size())
		for i: int in count:
			spawner.spawn_single(pool[i], WaveRules.hp_mult(wave))
			_bosses_alive += 1
			EventBus.boss_spawned.emit(pool[i])


func _on_enemy_died(enemy_id: StringName, _at: Vector2) -> void:
	if GameState.wave_kind == &"boss" and Balance.FINAL_BOSS_POOL.has(enemy_id):
		_bosses_alive -= 1
		if _bosses_alive <= 0 and _bosses_spawned:
			_win()


func _end_wave() -> void:
	_fighting = false
	spawner.clear_all()
	for node: Node in get_tree().get_nodes_in_group(&"pickups"):
		var pickup: XpPickup = node as XpPickup
		if pickup != null:
			pickup.attract(player)
	await get_tree().create_timer(Balance.WAVE_END_COLLECT_SEC, false).timeout
	if GameState.run_active:
		var bonus: int = Balance.WAVE_END_BONUS_XP_BASE + Balance.WAVE_END_BONUS_XP_PER_WAVE * GameState.wave
		EventBus.xp_collected.emit(bonus)
		HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -16.0), "+%d XP: ПОКОПАЛСЯ В ПОМОЙКЕ" % bonus, Color(0.968627, 1, 0, 1), 18.0, 1.4)
		if player.has_method(&"heal_full"):
			player.call(&"heal_full")
		EventBus.wave_ended.emit(GameState.wave)


func _win() -> void:
	_fighting = false
	spawner.clear_all()
	GameState.run_active = false
	EventBus.run_won.emit()


func _on_next_wave_requested() -> void:
	_start_wave(GameState.wave + 1)
