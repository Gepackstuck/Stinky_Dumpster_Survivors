class_name PerkLibrary
extends RefCounted
## Каталог перков: id, название, описание, иконка. Числа берутся из Balance.

const SPEED: StringName = &"speed"
const REGEN: StringName = &"regen"
const DOUBLE_SHOT: StringName = &"double_shot"
const LOOT_GOBLIN: StringName = &"loot_goblin"
const W_LIGHTER: StringName = &"w_lighter"
const W_SOCK: StringName = &"w_sock"
const W_SLINGSHOT: StringName = &"w_slingshot"
const W_MOP: StringName = &"w_mop"
const W_LASER: StringName = &"w_laser_pointer"
const W_SLIPPER: StringName = &"w_slipper"
const W_MILK: StringName = &"w_condensed_milk"
const W_PIPE_GUN: StringName = &"w_pipe_gun"
const W_CROSSBOW: StringName = &"w_crossbow"
const W_FRYING_PAN: StringName = &"w_frying_pan"
const W_ROLLING_PIN: StringName = &"w_rolling_pin"
const W_ROTTEN_CHEESE: StringName = &"w_rotten_cheese"
const W_SPRAY_CAN: StringName = &"w_spray_can"
const W_BOTTLE: StringName = &"w_bottle"
const W_MOSIN: StringName = &"w_mosin"
const START_WEAPONS: Array[StringName] = [W_LIGHTER, W_SOCK, W_SLINGSHOT, W_MOP]  # на выбор в начале забега
const WEAPON_PERKS: Array[StringName] = [W_LIGHTER, W_SOCK, W_SLINGSHOT, W_MOP, W_LASER, W_SLIPPER, W_MILK, W_PIPE_GUN, W_CROSSBOW, W_FRYING_PAN, W_ROLLING_PIN, W_ROTTEN_CHEESE, W_SPRAY_CAN, W_BOTTLE, W_MOSIN]  # всё оружие (Ларёк)
const ALL: Array[StringName] = [SPEED, REGEN, DOUBLE_SHOT, LOOT_GOBLIN, W_LIGHTER, W_SOCK, W_SLINGSHOT, W_MOP, W_LASER, W_SLIPPER, W_MILK, W_PIPE_GUN, W_CROSSBOW, W_FRYING_PAN, W_ROLLING_PIN, W_ROTTEN_CHEESE, W_SPRAY_CAN, W_BOTTLE, W_MOSIN]

const _TITLES: Dictionary[StringName, String] = {
	SPEED: "Скорость",
	REGEN: "Регенерация",
	DOUBLE_SHOT: "Двойной выстрел",
	LOOT_GOBLIN: "Лут-Гоблин",
	W_LIGHTER: "Зажигалка",
	W_SOCK: "Вонючий носок",
	W_SLINGSHOT: "Рогатка",
	W_MOP: "Швабра",
	W_LASER: "Лазерная указка",
	W_SLIPPER: "Тапок",
	W_MILK: "Сгущёнка",
	W_PIPE_GUN: "Самопал",
	W_CROSSBOW: "Арбалет",
	W_FRYING_PAN: "Сковородка",
	W_ROLLING_PIN: "Скалка",
	W_ROTTEN_CHEESE: "Тухлый сыр",
	W_SPRAY_CAN: "Баллончик",
	W_BOTTLE: "Бутылка",
	W_MOSIN: "Мосинка",
}
const _ICONS: Dictionary[StringName, String] = {
	SPEED: "res://assets/ui/perk_speed.png",
	REGEN: "res://assets/ui/perk_regen.png",
	DOUBLE_SHOT: "res://assets/ui/perk_double_shot.png",
	LOOT_GOBLIN: "res://assets/ui/perk_loot_goblin.png",
	W_LIGHTER: "res://assets/ui/perk_w_lighter.png",
	W_SOCK: "res://assets/ui/perk_w_sock.png",
	W_SLINGSHOT: "res://assets/ui/perk_w_slingshot.png",
	W_MOP: "res://assets/ui/perk_w_mop.png",
	W_LASER: "res://assets/ui/perk_w_laser_pointer.png",
	W_SLIPPER: "res://assets/ui/perk_w_slipper.png",
	W_MILK: "res://assets/ui/perk_w_condensed_milk.png",
	W_PIPE_GUN: "res://assets/ui/perk_w_pipe_gun.png",
	W_CROSSBOW: "res://assets/ui/perk_w_crossbow.png",
	W_FRYING_PAN: "res://assets/ui/perk_w_frying_pan.png",
	W_ROLLING_PIN: "res://assets/ui/perk_w_rolling_pin.png",
	W_ROTTEN_CHEESE: "res://assets/ui/perk_w_rotten_cheese.png",
	W_SPRAY_CAN: "res://assets/ui/perk_w_spray_can.png",
	W_BOTTLE: "res://assets/ui/perk_w_bottle.png",
	W_MOSIN: "res://assets/ui/perk_w_mosin.png",
}


static func title(perk_id: StringName) -> String:
	return _TITLES[perk_id]


static func icon(perk_id: StringName) -> Texture2D:
	return load(_ICONS[perk_id]) as Texture2D


static func description(perk_id: StringName) -> String:
	match perk_id:
		SPEED:
			return "+%d%% скорости. Пердишь - летишь." % roundi(Balance.PERK_SPEED_BONUS * 100.0)
		REGEN:
			return "+%d хп раз в %d сек. Кишки сами заживают." % [roundi(Balance.PERK_REGEN_HP), roundi(Balance.PERK_REGEN_INTERVAL_SEC)]
		DOUBLE_SHOT:
			return "+%d снаряд, -%d%% урона с каждого." % [Balance.PERK_DOUBLE_SHOT_EXTRA_PROJECTILES, roundi((1.0 - Balance.PERK_DOUBLE_SHOT_DAMAGE_MULT) * 100.0)]
		LOOT_GOBLIN:
			return "Подбор +%d%%, скорость -%d%%. Жадность тяжела." % [roundi((Balance.PERK_LOOT_GOBLIN_PICKUP_RADIUS_MULT - 1.0) * 100.0), roundi((1.0 - Balance.PERK_LOOT_GOBLIN_MOVE_SPEED_MULT) * 100.0)]
		W_LIGHTER:
			return "ОРУЖИЕ. Быстрые искры, враг горит. %d урона, %.2f с. Классика." % [roundi(Balance.WEAPONS[&"lighter"]["damage"]), Balance.WEAPONS[&"lighter"]["cooldown"]]
		W_LASER:
			return "ОРУЖИЕ. Красный луч пробивает всех на линии. Бесит кота и врагов."
		W_SLIPPER:
			return "ОРУЖИЕ. Бросок тапка: %d урона по площади. Мать так же делала." % roundi(Balance.WEAPONS[&"slipper"]["damage"])
		W_MILK:
			return "ОРУЖИЕ. Липкая капля замедляет врага вдвое. Сладко и мерзко."
		W_SOCK:
			return "ОРУЖИЕ. Вонь вокруг тебя: %d урона всем в радиусе раз в %.1f с." % [roundi(Balance.WEAPONS[&"sock"]["damage"]), Balance.WEAPONS[&"sock"]["cooldown"]]
		W_SLINGSHOT:
			return "ОРУЖИЕ. Камень с %d отскоками от врага к врагу." % int(Balance.WEAPONS[&"slingshot"]["ricochets"])
		W_MOP:
			return "ОРУЖИЕ. Взмах дугой: %d урона и отброс. Бей и отпихивай." % roundi(Balance.WEAPONS[&"mop"]["damage"])
	if perk_id in WEAPON_PERKS:
		var stats: Dictionary = Balance.WEAPONS[StringName(String(perk_id).trim_prefix("w_"))]
		return "ОРУЖИЕ. %s. %d урона, %.2f с." % [String(stats.get("tag", "")).capitalize(), roundi(stats["damage"]), stats["cooldown"]]
	return ""


## Максимум стаков перка (0 - без ограничения).
static func max_stacks(perk_id: StringName) -> int:
	if perk_id == SPEED:
		return Balance.PERK_SPEED_MAX_STACKS
	if perk_id in WEAPON_PERKS:
		return 1
	return 0


## До `count` случайных разных перков, которые ещё можно взять.
static func pick_choices(count: int) -> Array[StringName]:
	var pool: Array[StringName] = []
	for perk_id: StringName in ALL:
		var cap: int = max_stacks(perk_id)
		if cap == 0 or GameState.get_perk_stacks(perk_id) < cap:
			pool.append(perk_id)
	pool.shuffle()
	var result: Array[StringName] = []
	for i: int in mini(count, pool.size()):
		result.append(pool[i])
	return result
