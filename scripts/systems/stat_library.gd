class_name StatLibrary
extends RefCounted
## Каталог статов для карточек повышения уровня (как в Brotato): название, иконка, описание, тиры I-IV.

const IDS: Array[StringName] = [&"max_hp", &"regen", &"damage", &"attack_speed", &"speed", &"armor", &"dodge", &"pickup", &"crit"]
const TIER_NAMES: Array[String] = ["I", "II", "III", "IV"]
const TIER_COLORS: Array[Color] = [
	Color(0.91, 0.91, 0.91), Color(0.0, 0.94, 1.0), Color(1.0, 0.063, 0.94), Color(1.0, 0.2, 0.15)]

const _TITLES: Dictionary[StringName, String] = {
	&"max_hp": "ЖИВУЧЕСТЬ",
	&"regen": "ЗАЖИВЛЕНИЕ",
	&"damage": "ЗЛОБА",
	&"attack_speed": "СКОРОСТРЕЛЬНОСТЬ",
	&"speed": "ПРЫТКОСТЬ",
	&"armor": "ТОЛСТАЯ ШКУРА",
	&"dodge": "УВЁРТЛИВОСТЬ",
	&"pickup": "ЦЕПКИЕ РУКИ",
	&"crit": "ПОДЛЫЙ УДАР",
}


static func title(stat_id: StringName) -> String:
	return _TITLES[stat_id]


static func icon(stat_id: StringName) -> Texture2D:
	return load("res://assets/ui/stat_%s.png" % stat_id) as Texture2D


static func tier_color(tier: int) -> Color:
	return TIER_COLORS[tier - 1]


static func description(stat_id: StringName, tier: int) -> String:
	var v: int = roundi(Balance.STAT_VALUES[stat_id][tier - 1])
	match stat_id:
		&"max_hp":
			return "+%d макс. ХП. Больше мяса - дольше мучаешься." % v
		&"regen":
			return "+%d к регену. Раны затягиваются сами, чёрт." % v
		&"damage":
			return "+%d%% урона. Бьёшь злее." % v
		&"attack_speed":
			return "+%d%% скорости атаки. Руки чешутся." % v
		&"speed":
			return "+%d%% скорости бега. Пердишь - летишь." % v
		&"armor":
			return "+%d брони. Сало спасает." % v
		&"dodge":
			return "+%d%% уклонения. Скользкий, как мыло." % v
		&"pickup":
			return "+%d%% радиус подбора. Всё тащишь к себе." % v
		&"crit":
			return "+%d%% крита (x2). Бьёшь в больное." % v
	return ""


## Тир одной карточки на уровне `level`: гарантированный минимум + случайное повышение.
static func roll_tier(level: int) -> int:
	var tier: int = _guaranteed_tier(level)
	var chance2: float = minf(maxf(level - 1, 0) * Balance.STAT_TIER2_CHANCE_PER_LEVEL, 0.5)
	var chance3: float = minf(maxf(level - 5, 0) * Balance.STAT_TIER3_CHANCE_PER_LEVEL, 0.3)
	var chance4: float = minf(maxf(level - 15, 0) * Balance.STAT_TIER4_CHANCE_PER_LEVEL, 0.1)
	var roll: float = randf()
	if roll < chance4:
		tier = maxi(tier, 4)
	elif roll < chance3 + chance4:
		tier = maxi(tier, 3)
	elif roll < chance2 + chance3 + chance4:
		tier = maxi(tier, 2)
	return tier


static func _guaranteed_tier(level: int) -> int:
	if level >= 25 and level % 5 == 0:
		return 4
	return Balance.STAT_GUARANTEED_TIER.get(level, 1)


## `count` разных статов с тирами для уровня: массив {id, tier}.
static func pick_offers(count: int, level: int) -> Array[Dictionary]:
	var pool: Array[StringName] = IDS.duplicate()
	pool.shuffle()
	var offers: Array[Dictionary] = []
	for i: int in mini(count, pool.size()):
		offers.append({"id": pool[i], "tier": roll_tier(level)})
	return offers
