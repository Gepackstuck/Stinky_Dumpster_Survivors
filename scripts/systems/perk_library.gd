class_name PerkLibrary
extends RefCounted
## Каталог перков: id, название, описание, иконка. Числа берутся из Balance.

const SPEED: StringName = &"speed"
const REGEN: StringName = &"regen"
const DOUBLE_SHOT: StringName = &"double_shot"
const LOOT_GOBLIN: StringName = &"loot_goblin"
const W_SOCK: StringName = &"w_sock"
const W_SLINGSHOT: StringName = &"w_slingshot"
const W_MOP: StringName = &"w_mop"
const WEAPON_PERKS: Array[StringName] = [W_SOCK, W_SLINGSHOT, W_MOP]
const ALL: Array[StringName] = [SPEED, REGEN, DOUBLE_SHOT, LOOT_GOBLIN, W_SOCK, W_SLINGSHOT, W_MOP]

const _TITLES: Dictionary[StringName, String] = {
	SPEED: "Скорость",
	REGEN: "Регенерация",
	DOUBLE_SHOT: "Двойной выстрел",
	LOOT_GOBLIN: "Лут-Гоблин",
	W_SOCK: "Вонючий носок",
	W_SLINGSHOT: "Рогатка",
	W_MOP: "Швабра",
}
const _ICONS: Dictionary[StringName, String] = {
	SPEED: "res://assets/ui/perk_speed.png",
	REGEN: "res://assets/ui/perk_regen.png",
	DOUBLE_SHOT: "res://assets/ui/perk_double_shot.png",
	LOOT_GOBLIN: "res://assets/ui/perk_loot_goblin.png",
	W_SOCK: "res://assets/ui/perk_w_sock.png",
	W_SLINGSHOT: "res://assets/ui/perk_w_slingshot.png",
	W_MOP: "res://assets/ui/perk_w_mop.png",
}


static func title(perk_id: StringName) -> String:
	return _TITLES[perk_id]


static func icon(perk_id: StringName) -> Texture2D:
	return load(_ICONS[perk_id]) as Texture2D


static func description(perk_id: StringName) -> String:
	match perk_id:
		SPEED:
			return "+%d%% скорости. Пердишь — летишь." % roundi(Balance.PERK_SPEED_BONUS * 100.0)
		REGEN:
			return "+%d хп раз в %d сек. Кишки сами заживают." % [roundi(Balance.PERK_REGEN_HP), roundi(Balance.PERK_REGEN_INTERVAL_SEC)]
		DOUBLE_SHOT:
			return "+%d снаряд, -%d%% урона с каждого." % [Balance.PERK_DOUBLE_SHOT_EXTRA_PROJECTILES, roundi((1.0 - Balance.PERK_DOUBLE_SHOT_DAMAGE_MULT) * 100.0)]
		LOOT_GOBLIN:
			return "Подбор +%d%%, скорость -%d%%. Жадность тяжела." % [roundi((Balance.PERK_LOOT_GOBLIN_PICKUP_RADIUS_MULT - 1.0) * 100.0), roundi((1.0 - Balance.PERK_LOOT_GOBLIN_MOVE_SPEED_MULT) * 100.0)]
		W_SOCK:
			return "ОРУЖИЕ. Вонь вокруг тебя: %d урона всем в радиусе раз в %.1f с." % [roundi(Balance.WEAPONS[&"sock"]["damage"]), Balance.WEAPONS[&"sock"]["cooldown"]]
		W_SLINGSHOT:
			return "ОРУЖИЕ. Камень с %d отскоками от врага к врагу." % int(Balance.WEAPONS[&"slingshot"]["ricochets"])
		W_MOP:
			return "ОРУЖИЕ. Взмах дугой: %d урона и отброс. Бей и отпихивай." % roundi(Balance.WEAPONS[&"mop"]["damage"])
	return ""


## Максимум стаков перка (0 — без ограничения).
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
