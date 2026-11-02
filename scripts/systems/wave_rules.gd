class_name WaveRules
extends RefCounted
## Чистые правила волн в духе Brotato: длительность, число и размер групп, HP, тип врага.
## Числа — из Balance. См. docs/BROTATO_REFERENCE.md.


static func duration_sec(wave: int) -> float:
	if wave > Balance.WAVE_COUNT:   # бесконечность
		return Balance.WAVE_DURATION_FINAL_SEC if wave % Balance.ENDLESS_BOSS_EVERY == 0 else Balance.WAVE_DURATION_MAX_SEC
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
	count = maxi(roundi(count * mod_f("enemy_count", 1.0)), 1)
	return count


static func group_size(wave: int) -> int:
	var size: int = Balance.WAVE_GROUP_SIZE_BASE + floori(float(wave - 1) / float(Balance.WAVE_GROUP_SIZE_WAVES_PER_STEP))
	return maxi(size + randi_range(-1, 1) + 1, 1)


static func _late(wave: int) -> float:
	return float(maxi(wave - Balance.WAVE_LATE_START, 0))


static func hp_mult(wave: int) -> float:
	var n: float = float(maxi(wave, 1) - 1)
	return (1.0 + n * Balance.WAVE_HP_GROWTH + _late(wave) * _late(wave) * Balance.WAVE_HP_QUAD) * Balance.ENEMY_HP_MULT * mod_f("enemy_hp", 1.0) * danger_f("hp")


static func damage_mult(wave: int) -> float:
	var n: float = float(maxi(wave, 1) - 1)
	return (1.0 + n * Balance.WAVE_DAMAGE_GROWTH + _late(wave) * _late(wave) * Balance.WAVE_DAMAGE_QUAD) * Balance.ENEMY_DAMAGE_MULT * mod_f("enemy_damage", 1.0) * danger_f("dmg")


static func speed_mult(wave: int) -> float:
	var mult: float = minf(1.0 + (maxi(wave, 1) - 1) * Balance.WAVE_SPEED_GROWTH, Balance.WAVE_SPEED_MAX_MULT)
	return mult * mod_f("enemy_speed", 1.0) * (1.0 + GameState.enemy_haste / 100.0) * danger_f("speed")


## Модификатор волны: только на обычных волнах с WAVE_MOD_FROM. Берётся из «мешка» (Profile.mod_bag):
## пока не выпали все, ни один не повторяется; мешок живёт между забегами.
static func roll_mod(wave: int, kind: StringName, _last: StringName) -> StringName:
	if kind != &"normal" or wave < Balance.WAVE_MOD_FROM or randf() >= Balance.WAVE_MOD_CHANCE + danger_f("mod_add"):
		return &""
	return Profile.next_mod()


## Эффект текущего модификатора волны (Balance.WAVE_MOD_DATA[mod]["fx"][key]) или default.
static func mod_fx(key: String, default: Variant = null) -> Variant:
	if GameState.wave_mod == &"":
		return default
	return Balance.WAVE_MOD_DATA[GameState.wave_mod]["fx"].get(key, default)


## Параметр текущего уровня опасности.
static func danger_f(key: String) -> float:
	return float(Balance.DANGER_LEVELS[clampi(GameState.danger, 0, Balance.DANGER_LEVELS.size() - 1)][key])


static func danger_v(key: String) -> Variant:
	return Balance.DANGER_LEVELS[clampi(GameState.danger, 0, Balance.DANGER_LEVELS.size() - 1)][key]


static func mod_f(key: String, default: float) -> float:
	return float(mod_fx(key, default))


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
static func _weight(id: StringName, wave: int) -> float:
	var w: float = Balance.WAVE_ENEMY_WEIGHTS[id]
	if id == &"spitter" and wave > 5:   # к концу плевунов больше: уворот решает
		w *= 1.0 + (wave - 5) * Balance.SPITTER_LATE_WEIGHT_PER_WAVE
	return w


static func pick_enemy_id(wave: int) -> StringName:
	var total: float = 0.0
	for id: StringName in Balance.WAVE_ENEMY_UNLOCK:
		if wave >= Balance.WAVE_ENEMY_UNLOCK[id]:
			total += _weight(id, wave)
	var roll: float = randf() * total
	for id: StringName in Balance.WAVE_ENEMY_UNLOCK:
		if wave >= Balance.WAVE_ENEMY_UNLOCK[id]:
			roll -= _weight(id, wave)
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
