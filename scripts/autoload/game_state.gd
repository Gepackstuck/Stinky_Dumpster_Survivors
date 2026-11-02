extends Node
## Текущее состояние забега. Autoload: GameState.

var hp: float = 0.0
var still_sec: float = 0.0   # сколько секунд игрок стоит на месте (анти-кемпинг: облава)
var max_hp: float = 0.0
var xp: int = 0
var xp_to_next: int = 0
var level: int = 1
var coins: int = 0
var kills: int = 0
var wave: int = 0
var wave_time_left: float = 0.0   # обратный отсчёт текущей волны (как в Brotato)
var wave_kind: StringName = &"normal"  # normal / elite / horde / boss
var wave_note: String = ""       # подпись для баннера (имена боссов и т.п.)
var special_waves: Dictionary = {}  # номер волны -> elite/horde/boss (бросается в начале забега)
var time: float = 0.0
var run_active: bool = false
var last_damage_source: StringName = &""   # кто нанёс последний удар по игроку (экран смерти)

# Перки и производные статы (пересчитываются в _recompute_perk_stats()).
var perk_stacks: Dictionary[StringName, int] = {}
var move_speed_mult: float = 1.0
var pickup_radius_mult: float = 1.0
var extra_projectiles: int = 0
var projectile_damage_mult: float = 1.0
var regen_hp: float = 0.0
# Статы с карточек уровня (суммы значений по тирам).
var stat_totals: Dictionary[StringName, float] = {}
var damage_mult: float = 1.0
var attack_speed_mult: float = 1.0
var armor: float = 0.0
var dodge_percent: float = 0.0
var crit_percent: float = 0.0
var bonus_max_hp: float = 0.0
var reroll_count: int = 0
var weapons: Array[Dictionary] = []    # оружие игрока: {id, tier}, до WEAPON_SLOTS штук
var danger: int = 0                  # уровень опасности забега (Balance.DANGER_LEVELS)
var character: StringName = &"hobo"   # выбранный на кладбище персонаж (живёт между забегами)
var run_coins_earned: int = 0
var items: Dictionary[StringName, int] = {}   # рюкзак: id предмета -> штук
var coin_bonus: float = 0.0        # +доля к говну с дропа
var repel_percent: float = 0.0
var thorns_damage: float = 0.0
var explode_percent: float = 0.0
var lifesteal_percent: float = 0.0
var discount_percent: float = 0.0
var pet_count: int = 0
var burn_percent: float = 0.0       # зажигалка: шанс поджечь при попадании
var bash_percent: float = 0.0       # лом: шанс сильно отбросить
var crit_coin_percent: float = 0.0  # золотой зуб: шанс монеты с крита
var block_count: int = 0            # каска: сколько ударов гасит за волну
var still_regen: float = 0.0        # бинт: ХП за тик на месте
var drunk_percent: float = 0.0     # палёнка: шанс пьянки с убийства
var combo_percent: float = 0.0     # батарейка: % скорости атаки за звено серии
var slow_field_count: int = 0      # доска: сколько досок (сила замедления)
var stash_percent: float = 0.0     # рюкзак: шанс найти предмет после волны
var temp_attack_bonus: float = 0.0 # временная прибавка к скорости атаки (пьянка, серия)
var block_charges: int = 0          # осталось гашений в этой волне
var turret_count: int = 0
var comp_counts: Dictionary = {}   # пёс, голуби, мины, лампы, миномёты: ключ fx -> штук
var ghost_drunk_count: int = 0
var ghost_granny_count: int = 0
var _item_stats: Dictionary[StringName, float] = {}
var _coin_remainder: float = 0.0
var ink_percent: float = 0.0          # фишки героев (Balance.CHARACTERS fx)
var steal_percent: float = 0.0
var salary: float = 0.0
var clean_heal_every: int = 0
var hype_per: float = 0.0
var pies: float = 0.0
var rush: float = 0.0
var regen_bonus: float = 0.0
var post_bonus: float = 0.0
var xp_bonus: float = 0.0
var trick_bonus: float = 0.0
var trick_left: float = 0.0
var slime_touch: float = 0.0
var class_extra: Dictionary = {}     # +оружий класса в наборах от предметов (set_<класс>)
var hp_drain: float = 0.0            # проклятье: ХП утекает (раз в Balance.CURSED_HP_DRAIN_SEC)
var enemy_haste: float = 0.0         # проклятье: враги быстрее, %
var dash_hp_cost: float = 0.0        # проклятье: рывок стоит ХП
var no_regen: bool = false           # проклятье: реген не работает
var wind: Vector2 = Vector2.ZERO     # снос героя ветром (модификатор волны)
var wave_mod: StringName = &""      # модификатор текущей волны (Balance.WAVE_MODS) или пусто
var wave_damage_taken: float = 0.0   # урон за текущую волну (чистая волна = 0)
var last_clean_bonus: int = 0        # бонус за чистую прошлую волну (для Ларька)
var clean_waves: int = 0             # чистых волн за забег (статистика, ачивки)
var nohit_sec: float = 0.0           # серия без урона
var streak_tier: int = 0
var best_streak_sec: float = 0.0
var shop_offers: Array[Dictionary] = []  # витрина Ларька (замороженные переходят на след. волну)


func _ready() -> void:
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(_on_player_died)
	EventBus.xp_collected.connect(_on_xp_collected)
	EventBus.weapons_changed.connect(_recompute_perk_stats)
	EventBus.player_hit.connect(_on_player_hit)
	EventBus.wave_started.connect(func(_w: int) -> void: wave_damage_taken = 0.0)
	EventBus.wave_ended.connect(_on_wave_ended_clean)   # бонусы наборов зависят от оружия в слотах


## Сбросить состояние перед новым забегом.
func reset_run() -> void:
	max_hp = Balance.PLAYER_MAX_HP
	hp = max_hp
	xp = 0
	xp_to_next = xp_needed(1)
	level = 1
	coins = 0
	kills = 0
	wave = 0
	wave_time_left = 0.0
	wave_kind = &"normal"
	wave_note = ""
	special_waves = {}
	time = 0.0
	run_active = true
	last_damage_source = &""
	perk_stacks.clear()
	stat_totals.clear()
	items.clear()
	block_charges = 0
	temp_attack_bonus = 0.0
	run_coins_earned = 0
	_coin_remainder = 0.0
	wave_damage_taken = 0.0
	wave_mod = &""
	last_clean_bonus = 0
	clean_waves = 0
	nohit_sec = 0.0
	streak_tier = 0
	best_streak_sec = 0.0
	weapons.clear()
	shop_offers.clear()
	reroll_count = 0
	var start_weapon: StringName = Balance.CHARACTERS[character]["weapon"]
	if start_weapon != &"":
		weapons.append({"id": start_weapon, "tier": 1})
	_recompute_perk_stats()
	EventBus.run_started.emit()


func get_perk_stacks(perk_id: StringName) -> int:
	return perk_stacks.get(perk_id, 0)


## Применить выбранный перк (+1 стак) и пересчитать статы.
func apply_perk(perk_id: StringName) -> void:
	if perk_id in PerkLibrary.WEAPON_PERKS:
		add_weapon(StringName(String(perk_id).trim_prefix("w_")))
		return
	perk_stacks[perk_id] = get_perk_stacks(perk_id) + 1
	_recompute_perk_stats()
	EventBus.perk_chosen.emit(perk_id)


## Добавить оружие в свободный слот. false — слоты заняты.
func add_weapon(weapon_id: StringName, tier: int = 1) -> bool:
	if weapons.size() >= Balance.WEAPON_SLOTS:
		return false
	weapons.append({"id": weapon_id, "tier": tier})
	EventBus.weapons_changed.emit()
	EventBus.perk_chosen.emit(StringName("w_" + String(weapon_id)))
	return true


## Слот с таким же оружием и тиром (для скрещивания при полных слотах), -1 если нет.
func find_weapon(weapon_id: StringName, tier: int) -> int:
	if tier >= 4:
		return -1
	for i: int in weapons.size():
		if weapons[i]["id"] == weapon_id and weapons[i]["tier"] == tier:
			return i
	return -1


## Другой слот с тем же оружием и тиром, чтобы скрестить со слотом `index`; -1 если нет.
func find_merge_partner(index: int) -> int:
	var w: Dictionary = weapons[index]
	if w["tier"] >= 4:
		return -1
	for i: int in weapons.size():
		if i != index and weapons[i]["id"] == w["id"] and weapons[i]["tier"] == w["tier"]:
			return i
	return -1


## Скрестить слот `index` с парой: остаётся одно оружие тиром выше.
func merge_weapons(index: int) -> bool:
	var partner: int = find_merge_partner(index)
	if partner < 0:
		return false
	weapons[index]["tier"] += 1
	weapons.remove_at(partner)
	EventBus.weapons_changed.emit()
	return true


func weapon_recycle_value(index: int) -> int:
	var w: Dictionary = weapons[index]
	var base: float = Balance.WEAPON_PRICE.get(w["id"], 10)
	return maxi(roundi(base * Balance.SHOP_PRICE_TIER_MULT[w["tier"] - 1] * Balance.RECYCLE_FRACTION), 1)


## Сдать оружие: вернуть часть говна. Последнее оружие сдать нельзя.
func recycle_weapon(index: int) -> int:
	if weapons.size() <= 1:
		return 0
	var value: int = weapon_recycle_value(index)
	coins += value
	weapons.remove_at(index)
	EventBus.weapons_changed.emit()
	return value


## Два куска комбо у героя: забираем по одному и выдаём комбо-предмет. Пусто - комбо нет.
func _try_combo(item_id: StringName) -> StringName:
	for combo_id: StringName in Balance.ITEM_COMBOS:
		var parts: Array = Balance.ITEM_COMBOS[combo_id]
		if item_id in parts and item_count(combo_id) == 0 and item_count(parts[0]) > 0 and item_count(parts[1]) > 0:
			for part: StringName in parts:
				items[part] = item_count(part) - 1
				if items[part] <= 0:
					items.erase(part)
			items[combo_id] = 1
			Profile.found_combo(combo_id)
			return combo_id
	return &""


## Применить карточку стата нужного тира.
func apply_stat(stat_id: StringName, tier: int) -> void:
	var value: float = Balance.STAT_VALUES[stat_id][tier - 1]
	stat_totals[stat_id] = stat_totals.get(stat_id, 0.0) + value
	_recompute_perk_stats()
	EventBus.perk_chosen.emit(StringName("stat_" + String(stat_id)))


func stat_total(stat_id: StringName) -> float:
	return stat_totals.get(stat_id, 0.0) + _item_stats.get(stat_id, 0.0)


func item_count(item_id: StringName) -> int:
	return items.get(item_id, 0)


## Положить предмет в рюкзак (+1 штука) и пересчитать статы.
func add_item(item_id: StringName) -> void:
	items[item_id] = item_count(item_id) + 1
	var combo: StringName = _try_combo(item_id)
	if combo != &"":
		EventBus.item_combo.emit(combo)
	_recompute_perk_stats()
	EventBus.perk_chosen.emit(StringName("item_" + String(item_id)))
	EventBus.items_changed.emit()


func _recompute_items() -> void:
	_item_stats.clear()
	var fx: Dictionary[StringName, float] = {}
	for item_id: StringName in items:
		var count: int = items[item_id]
		var data: Dictionary = Balance.ITEMS[item_id]
		for stat_id: StringName in data.get("mods", {}):
			_item_stats[stat_id] = _item_stats.get(stat_id, 0.0) + data["mods"][stat_id] * count
		for key: StringName in data.get("fx", {}):
			fx[key] = fx.get(key, 0.0) + data["fx"][key] * count
	var hero: Dictionary = Balance.CHARACTERS[character]
	for stat_id: StringName in hero.get("mods", {}):
		_item_stats[stat_id] = _item_stats.get(stat_id, 0.0) + hero["mods"][stat_id]
	for key: StringName in hero.get("fx", {}):
		fx[key] = fx.get(key, 0.0) + hero["fx"][key]
	var counts: Dictionary = WeaponLibrary.class_counts(weapons)   # бонусы наборов оружия по классам
	class_extra = {}
	for key: StringName in fx:   # предметы-синергии: «+1 к набору»
		if String(key).begins_with("set_"):
			var cls: StringName = StringName(String(key).trim_prefix("set_"))
			class_extra[cls] = roundi(fx[key])
			if counts.has(cls) or fx[key] > 0.0:
				counts[cls] = counts.get(cls, 0) + roundi(fx[key])
	for class_id: StringName in counts:
		var bonus: Dictionary = WeaponLibrary.set_bonus(class_id, counts[class_id])
		for stat_id: StringName in bonus.get("mods", {}):
			_item_stats[stat_id] = _item_stats.get(stat_id, 0.0) + bonus["mods"][stat_id]
		for key: StringName in bonus.get("fx", {}):
			fx[key] = fx.get(key, 0.0) + bonus["fx"][key]
	var crown: float = minf(fx.get(&"crown", 0.0), 60.0)
	if crown > 0.0:
		for stat_id: StringName in _item_stats.keys():
			if _item_stats[stat_id] > 0.0:
				_item_stats[stat_id] *= 1.0 + crown / 100.0
	coin_bonus = fx.get(&"coin_bonus", 0.0) / 100.0
	repel_percent = minf(fx.get(&"repel", 0.0), Balance.ITEM_REPEL_MAX_PERCENT)
	thorns_damage = fx.get(&"thorns", 0.0)
	explode_percent = minf(fx.get(&"explode", 0.0), 75.0)
	lifesteal_percent = minf(fx.get(&"lifesteal", 0.0), 60.0)
	discount_percent = minf(fx.get(&"discount", 0.0), 60.0)
	pet_count = roundi(fx.get(&"pets", 0.0))
	burn_percent = minf(fx.get(&"burn", 0.0), 75.0)
	bash_percent = minf(fx.get(&"bash", 0.0), 60.0)
	crit_coin_percent = minf(fx.get(&"crit_coin", 0.0), 100.0)
	block_count = roundi(fx.get(&"block", 0.0))
	still_regen = fx.get(&"still_regen", 0.0)
	drunk_percent = minf(fx.get(&"drunk", 0.0), 40.0)
	combo_percent = fx.get(&"combo", 0.0)
	slow_field_count = roundi(fx.get(&"slow_field", 0.0))
	stash_percent = minf(fx.get(&"stash", 0.0), 80.0)
	turret_count = roundi(fx.get(&"turrets", 0.0))
	comp_counts = {}
	for comp_key: StringName in [&"dogs", &"pigeons", &"mines", &"lamps", &"mortars"]:
		comp_counts[comp_key] = roundi(fx.get(comp_key, 0.0))
	ghost_drunk_count = roundi(fx.get(&"ghost_drunk", 0.0))
	hp_drain = fx.get(&"hp_drain", 0.0)
	ink_percent = fx.get(&"ink", 0.0)
	steal_percent = fx.get(&"steal", 0.0)
	salary = fx.get(&"salary", 0.0)
	clean_heal_every = roundi(fx.get(&"clean_heal", 0.0))
	hype_per = fx.get(&"hype", 0.0)
	pies = fx.get(&"pies", 0.0)
	rush = fx.get(&"rush", 0.0)
	regen_bonus = fx.get(&"regen_mult", 0.0)
	post_bonus = fx.get(&"post", 0.0)
	xp_bonus = fx.get(&"xp_bonus", 0.0)
	trick_bonus = fx.get(&"trick", 0.0)
	slime_touch = fx.get(&"slime_touch", 0.0)
	enemy_haste = fx.get(&"enemy_haste", 0.0)
	dash_hp_cost = fx.get(&"dash_cost", 0.0)
	no_regen = fx.get(&"no_regen", 0.0) > 0.0
	ghost_granny_count = roundi(fx.get(&"ghost_granny", 0.0))


## Урон выстрела с учётом статов, перков и крита.
func roll_damage(base: float) -> float:
	var result: float = floorf(base * projectile_damage_mult * damage_mult * WaveRules.mod_f("player_damage", 1.0) * hero_damage_mult() * 100.0) / 100.0
	if randf() * 100.0 < crit_percent:
		result = floorf(result * Balance.CRIT_DAMAGE_MULT * 100.0) / 100.0 + CRIT_MARK
		if randf() * 100.0 < crit_coin_percent:
			coins += 1
	return result


## Крит помечается микроскопической добавкой к урону — по ней враг красит цифру.
const CRIT_MARK: float = 0.00037


static func is_crit_damage(damage: float) -> bool:
	var rest: float = fposmod(damage, 0.01)
	return rest > 0.0003 and rest < 0.00044


## Фишки героев на урон: хайп блогера, пост Саныча, трюк скейтера.
func hero_damage_mult() -> float:
	var mult: float = 1.0
	if hype_per > 0.0:
		mult += minf(floorf(kills / hype_per), Balance.HERO_HYPE_MAX) / 100.0
	if post_bonus > 0.0 and still_sec >= Balance.HERO_POST_SEC:
		mult += post_bonus / 100.0
	if trick_bonus > 0.0 and trick_left > 0.0:
		mult += trick_bonus / 100.0
	return mult


func cooldown_for(base_sec: float) -> float:
	return base_sec / ((attack_speed_mult + temp_attack_bonus) * WaveRules.mod_f("attack_speed", 1.0))


func _recompute_perk_stats() -> void:
	_recompute_items()
	var speed: int = get_perk_stacks(PerkLibrary.SPEED)
	var goblin: int = get_perk_stacks(PerkLibrary.LOOT_GOBLIN)
	var shots: int = get_perk_stacks(PerkLibrary.DOUBLE_SHOT)
	var regen: int = get_perk_stacks(PerkLibrary.REGEN)
	move_speed_mult = (1.0 + Balance.PERK_SPEED_BONUS * speed + stat_total(&"speed") / 100.0) * pow(Balance.PERK_LOOT_GOBLIN_MOVE_SPEED_MULT, goblin)
	pickup_radius_mult = 1.0 + (Balance.PERK_LOOT_GOBLIN_PICKUP_RADIUS_MULT - 1.0) * goblin + stat_total(&"pickup") / 100.0
	damage_mult = 1.0 + stat_total(&"damage") / 100.0
	attack_speed_mult = 1.0 + stat_total(&"attack_speed") / 100.0
	armor = stat_total(&"armor")
	dodge_percent = minf(stat_total(&"dodge"), Balance.DODGE_MAX_PERCENT)
	crit_percent = stat_total(&"crit")
	bonus_max_hp = stat_total(&"max_hp")
	extra_projectiles = Balance.PERK_DOUBLE_SHOT_EXTRA_PROJECTILES * shots
	projectile_damage_mult = pow(Balance.PERK_DOUBLE_SHOT_DAMAGE_MULT, shots)
	regen_hp = 0.0 if no_regen else (Balance.PERK_REGEN_HP * regen + Balance.REGEN_HP_PER_POINT * stat_total(&"regen")) * (1.0 + regen_bonus / 100.0)


func _on_enemy_died(enemy_id: StringName, _position: Vector2) -> void:
	if not Balance.ENEMIES.get(enemy_id, {}).get("neutral", false):
		kills += 1


## Серия без урона: тикает из игрока (только в бою), ступени из Balance.NOHIT_STREAK_TIERS.
func tick_streak(delta: float) -> void:
	nohit_sec += delta
	best_streak_sec = maxf(best_streak_sec, nohit_sec)
	var tier: int = 0
	for t: Array in Balance.NOHIT_STREAK_TIERS:
		if nohit_sec >= float(t[0]):
			tier += 1
	if tier != streak_tier:
		streak_tier = tier
		EventBus.streak_changed.emit(tier, streak_bonus(), false)


func streak_bonus() -> float:
	return 0.0 if streak_tier == 0 else float(Balance.NOHIT_STREAK_TIERS[streak_tier - 1][1])


func _on_player_hit(damage: float) -> void:
	wave_damage_taken += damage
	var had: int = streak_tier
	nohit_sec = 0.0
	streak_tier = 0
	if had > 0:
		EventBus.streak_changed.emit(0, 0.0, true)


## Чистая волна: ни одного попадания - бонус говна (растёт с номером волны).
func _on_wave_ended_clean(wave_number: int) -> void:
	last_clean_bonus = 0
	if run_active and salary > 0.0:   # планктон: зарплата
		var pay: int = roundi(salary * wave_number)
		coins += pay
		run_coins_earned += pay
	if not run_active or wave_damage_taken > 0.0:
		return
	last_clean_bonus = Balance.CLEAN_WAVE_BONUS_BASE + Balance.CLEAN_WAVE_BONUS_PER_WAVE * wave_number
	coins += last_clean_bonus
	run_coins_earned += last_clean_bonus
	clean_waves += 1


## Сколько XP нужно, чтобы выйти с уровня `at_level` на следующий.
static func xp_needed(at_level: int) -> int:
	return ceili(Balance.XP_LEVEL_FACTOR * pow(at_level + 3, 2))


func _on_xp_collected(amount: int) -> void:
	if not run_active:
		return
	amount = roundi(amount * (1.0 + xp_bonus / 100.0)) if xp_bonus > 0.0 else amount
	xp += amount
	_coin_remainder += float(amount) * Balance.COIN_PER_XP * (1.0 + coin_bonus + streak_bonus()) * WaveRules.mod_f("coin", 1.0)  # деньги — доля от опыта, копить придётся
	var whole: int = floori(_coin_remainder)
	coins += whole
	run_coins_earned += whole
	_coin_remainder -= float(whole)
	while xp >= xp_to_next:
		xp -= xp_to_next
		level += 1
		xp_to_next = xp_needed(level)
		EventBus.player_leveled_up.emit(level)


func _on_player_died() -> void:
	run_active = false
	EventBus.run_ended.emit()
