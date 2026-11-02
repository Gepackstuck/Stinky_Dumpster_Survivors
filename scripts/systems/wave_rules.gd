class_name WaveRules
extends RefCounted
## Чистые правила волн в духе Brotato: длительность, число и размер групп, HP, тип врага.
## Числа — из Balance. См. docs/BROTATO_REFERENCE.md.


static func duration_sec(wave: int) -> float:
	if wave >= Balance.WAVE_COUNT:
		return Balance.WAVE_DURATION_FINAL_SEC
	return minf(Balance.WAVE_DURATION_FIRST_SEC + (wave - 1) * Balance.WAVE_DURATION_STEP_SEC, Balance.WAVE_DURATION_MAX_SEC)


## Сколько групп за волну: общее число врагов (BASE + PER_WAVE × (волна−1)) делим на средний размер группы.
static func group_count(wave: int, kind: StringName) -> int:
	var late: float = float(maxi(wave - Balance.WAVE_LATE_START, 0))
	var total: int = Balance.WAVE_ENEMIES_BASE + Balance.WAVE_ENEMIES_PER_WAVE * (maxi(wave, 1) - 1) + roundi(Balance.WAVE_ENEMIES_LATE * late * late)
	var avg_size: float = float(Balance.WAVE_GROUP_SIZE_BASE + floori(float(wave - 1) / float(Balance.WAVE_GROUP_SIZE_WAVES_PER_STEP)) + 1)
	var count: int = maxi(roundi(float(total) / avg_size), Balance.WAVE_MIN_GROUPS)
	count = maxi(count, ceili(duration_sec(wave) / Balance.WAVE_MAX_GAP_SEC))  # поле не должно пустеть надолго
	if kind == &"horde":
		count = int(count * Balance.HORDE_GROUP_MULT)
	return count


static func group_size(wave: int) -> int:
	var size: int = Balance.WAVE_GROUP_SIZE_BASE + floori(float(wave - 1) / float(Balance.WAVE_GROUP_SIZE_WAVES_PER_STEP))
	return maxi(size + randi_range(-1, 1) + 1, 1)


static func _late(wave: int) -> float:
	return float(maxi(wave - Balance.WAVE_LATE_START, 0))


static func hp_mult(wave: int) -> float:
	var n: float = float(maxi(wave, 1) - 1)
	return (1.0 + n * Balance.WAVE_HP_GROWTH + _late(wave) * _late(wave) * Balance.WAVE_HP_QUAD) * Balance.ENEMY_HP_MULT


static func damage_mult(wave: int) -> float:
	var n: float = float(maxi(wave, 1) - 1)
	return (1.0 + n * Balance.WAVE_DAMAGE_GROWTH + _late(wave) * _late(wave) * Balance.WAVE_DAMAGE_QUAD) * Balance.ENEMY_DAMAGE_MULT


static func speed_mult(wave: int) -> float:
	var mult: float = minf(1.0 + (maxi(wave, 1) - 1) * Balance.WAVE_SPEED_GROWTH, Balance.WAVE_SPEED_MAX_MULT)
	return mult * (Balance.PAYDAY_ENEMY_SPEED_MULT if GameState.wave_mod == &"payday" else 1.0)


## Модификатор волны: только на обычных волнах с WAVE_MOD_FROM, не тот же, что в прошлый раз.
static func roll_mod(wave: int, kind: StringName, last: StringName) -> StringName:
	if kind != &"normal" or wave < Balance.WAVE_MOD_FROM or randf() >= Balance.WAVE_MOD_CHANCE:
		return &""
	var pool: Array[StringName] = Balance.WAVE_MODS.filter(func(m: StringName) -> bool: return m != last)
	return pool[randi() % pool.size()]


## Сила урона модификаторов (лужи, мусоровоз): мягче, чем у врагов.
static func hazard_mult(wave: int) -> float:
	return pow(damage_mult(wave), 0.7)


## Времена появления групп (сек от начала волны), отсортированы.
static func spawn_times(wave: int, kind: StringName) -> Array[float]:
	var count: int = group_count(wave, kind)
	var last: float = duration_sec(wave) * Balance.WAVE_SPAWN_END_FRACTION
	var times: Array[float] = [Balance.WAVE_FIRST_GROUP_SEC]
	# равномерно по окну волны (с разбросом внутри своей доли), а не чистый рандом — иначе бывают дыры
	var step: float = (last - Balance.WAVE_FIRST_GROUP_SEC) / float(maxi(count - 1, 1))
	for i: int in range(1, count):
		var centre: float = Balance.WAVE_FIRST_GROUP_SEC + step * i
		times.append(clampf(centre + randf_range(-step, step) * 0.4, Balance.WAVE_FIRST_GROUP_SEC, last))
	times.sort()
	return times


## Взвешенный случайный тип среди открытых к этой волне.
static func pick_enemy_id(wave: int) -> StringName:
	var total: float = 0.0
	for id: StringName in Balance.WAVE_ENEMY_UNLOCK:
		if wave >= Balance.WAVE_ENEMY_UNLOCK[id]:
			total += Balance.WAVE_ENEMY_WEIGHTS[id]
	var roll: float = randf() * total
	for id: StringName in Balance.WAVE_ENEMY_UNLOCK:
		if wave >= Balance.WAVE_ENEMY_UNLOCK[id]:
			roll -= Balance.WAVE_ENEMY_WEIGHTS[id]
			if roll <= 0.0:
				return id
	return &"squid_gopnik"


## Вид каждой волны на этот забег: элиты/орды в окнах Brotato, боссы на последней.
static func roll_special_waves() -> Dictionary:
	var kinds: Dictionary = {}
	for i: int in Balance.SPECIAL_WAVE_WINDOWS.size():
		var window: Array = Balance.SPECIAL_WAVE_WINDOWS[i]
		var wave: int = window[randi() % window.size()]
		var is_last: bool = i == Balance.SPECIAL_WAVE_WINDOWS.size() - 1
		kinds[wave] = &"elite" if (is_last or randf() < Balance.ELITE_CHANCE) else &"horde"
	kinds[Balance.WAVE_COUNT] = &"boss"
	return kinds
