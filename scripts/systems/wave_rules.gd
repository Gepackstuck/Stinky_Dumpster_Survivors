class_name WaveRules
extends RefCounted
## Чистые правила волн в духе Brotato: длительность, число и размер групп, HP, тип врага.
## Числа — из Balance. См. docs/BROTATO_REFERENCE.md.


static func duration_sec(wave: int) -> float:
	if wave >= Balance.WAVE_COUNT:
		return Balance.WAVE_DURATION_FINAL_SEC
	return minf(Balance.WAVE_DURATION_FIRST_SEC + (wave - 1) * Balance.WAVE_DURATION_STEP_SEC, Balance.WAVE_DURATION_MAX_SEC)


static func group_count(wave: int, kind: StringName) -> int:
	var t: float = float(wave - 1) / float(maxi(Balance.WAVE_COUNT - 1, 1))
	var interval: float = lerpf(Balance.WAVE_GROUP_INTERVAL_START_SEC, Balance.WAVE_GROUP_INTERVAL_END_SEC, t)
	var count: int = maxi(roundi(duration_sec(wave) * Balance.WAVE_SPAWN_END_FRACTION / interval), Balance.WAVE_GROUPS_BASE)
	if kind == &"horde":
		count = int(count * Balance.HORDE_GROUP_MULT)
	return count


static func group_size(wave: int) -> int:
	var size: int = Balance.WAVE_GROUP_SIZE_BASE + floori(float(wave - 1) / float(Balance.WAVE_GROUP_SIZE_WAVES_PER_STEP))
	return maxi(size + randi_range(-1, 1) + 1, 1)


static func hp_mult(wave: int) -> float:
	return 1.0 + (maxi(wave, 1) - 1) * Balance.WAVE_HP_GROWTH


static func damage_mult(wave: int) -> float:
	return 1.0 + (maxi(wave, 1) - 1) * Balance.WAVE_DAMAGE_GROWTH


static func speed_mult(wave: int) -> float:
	return minf(1.0 + (maxi(wave, 1) - 1) * Balance.WAVE_SPEED_GROWTH, Balance.WAVE_SPEED_MAX_MULT)


## Времена появления групп (сек от начала волны), отсортированы.
static func spawn_times(wave: int, kind: StringName) -> Array[float]:
	var count: int = group_count(wave, kind)
	var last: float = duration_sec(wave) * Balance.WAVE_SPAWN_END_FRACTION
	var times: Array[float] = [Balance.WAVE_FIRST_GROUP_SEC]
	for i: int in count - 1:
		times.append(randf_range(Balance.WAVE_FIRST_GROUP_SEC, last))
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
