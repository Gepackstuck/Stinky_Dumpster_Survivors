extends Node
## Текущее состояние забега. Autoload: GameState.

var hp: float = 0.0
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
var items: Dictionary[StringName, int] = {}   # рюкзак: id предмета -> штук
var coin_bonus: float = 0.0        # +доля к говну с дропа
var repel_percent: float = 0.0
var thorns_damage: float = 0.0
var explode_percent: float = 0.0
var lifesteal_percent: float = 0.0
var discount_percent: float = 0.0
var pet_count: int = 0
var turret_count: int = 0
var ghost_drunk_count: int = 0
var ghost_granny_count: int = 0
var _item_stats: Dictionary[StringName, float] = {}
var _coin_remainder: float = 0.0
var shop_offers: Array[Dictionary] = []  # витрина Ларька (замороженные переходят на след. волну)


func _ready() -> void:
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(_on_player_died)
	EventBus.xp_collected.connect(_on_xp_collected)


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
	_coin_remainder = 0.0
	weapons.clear()
	shop_offers.clear()
	reroll_count = 0
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
	coin_bonus = fx.get(&"coin_bonus", 0.0) / 100.0
	repel_percent = minf(fx.get(&"repel", 0.0), Balance.ITEM_REPEL_MAX_PERCENT)
	thorns_damage = fx.get(&"thorns", 0.0)
	explode_percent = minf(fx.get(&"explode", 0.0), 75.0)
	lifesteal_percent = minf(fx.get(&"lifesteal", 0.0), 60.0)
	discount_percent = minf(fx.get(&"discount", 0.0), 60.0)
	pet_count = roundi(fx.get(&"pets", 0.0))
	turret_count = roundi(fx.get(&"turrets", 0.0))
	ghost_drunk_count = roundi(fx.get(&"ghost_drunk", 0.0))
	ghost_granny_count = roundi(fx.get(&"ghost_granny", 0.0))


## Урон выстрела с учётом статов, перков и крита.
func roll_damage(base: float) -> float:
	var result: float = base * projectile_damage_mult * damage_mult
	if randf() * 100.0 < crit_percent:
		result *= Balance.CRIT_DAMAGE_MULT
	return result


func cooldown_for(base_sec: float) -> float:
	return base_sec / attack_speed_mult


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
	regen_hp = Balance.PERK_REGEN_HP * regen + Balance.REGEN_HP_PER_POINT * stat_total(&"regen")


func _on_enemy_died(enemy_id: StringName, _position: Vector2) -> void:
	if not Balance.ENEMIES.get(enemy_id, {}).get("neutral", false):
		kills += 1


## Сколько XP нужно, чтобы выйти с уровня `at_level` на следующий.
static func xp_needed(at_level: int) -> int:
	return ceili(Balance.XP_LEVEL_FACTOR * pow(at_level + 3, 2))


func _on_xp_collected(amount: int) -> void:
	if not run_active:
		return
	xp += amount
	_coin_remainder += float(amount) * Balance.COIN_PER_XP * (1.0 + coin_bonus)  # деньги — доля от опыта, копить придётся
	var whole: int = floori(_coin_remainder)
	coins += whole
	_coin_remainder -= float(whole)
	while xp >= xp_to_next:
		xp -= xp_to_next
		level += 1
		xp_to_next = xp_needed(level)
		EventBus.player_leveled_up.emit(level)


func _on_player_died() -> void:
	run_active = false
	EventBus.run_ended.emit()
