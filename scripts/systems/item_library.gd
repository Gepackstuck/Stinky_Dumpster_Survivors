class_name ItemLibrary
extends RefCounted
## Каталог предметов Ларька: название, иконка, описание из модификаторов. Числа — в Balance.ITEMS.

const _TITLES: Dictionary[StringName, String] = {
	&"cigarette": "ОКУРОК",
	&"sandwich": "ТУХЛЫЙ СЭНДВИЧ",
	&"holey_sock": "ДЫРЯВЫЙ НОСОК",
	&"pot": "РЖАВАЯ КАСТРЮЛЯ",
	&"energy_can": "БАНКА ЭНЕРГЕТИКА",
	&"poop_wallet": "КОШЕЛЁК С ГОВНОМ",
	&"old_milk": "ТУХЛАЯ СГУЩЁНКА",
	&"nail_knuckles": "КАСТЕТ ИЗ ГВОЗДЕЙ",
	&"dirty_glasses": "ГРЯЗНЫЕ ОЧКИ",
	&"junk_magnet": "МАГНИТ С ПОМОЙКИ",
	&"stinky_pants": "ОБОСРАННЫЕ ШТАНЫ",
	&"foil_hat": "ШАПКА ИЗ ФОЛЬГИ",
	&"shawarma": "ТУХЛАЯ ШАУРМА",
	&"coupon": "ТАЛОН БОМЖА",
	&"barbed_wire": "КОЛЮЧКА",
	&"diarrhea": "ВЗРЫВНОЙ ПОНОС",
	&"bloody_rag": "КРОВАВАЯ ТРЯПКА",
	&"dead_rat": "КРЫСА-ПРИЯТЕЛЬ",
	&"bucket_turret": "ТУРЕЛЬ ИЗ ВЕДРА",
	&"golden_toilet": "ЗОЛОТОЙ УНИТАЗ",
}
const _STAT_LABELS: Dictionary[StringName, String] = {
	&"max_hp": "МАКС. ХП", &"regen": "РЕГЕН", &"damage": "% УРОНА", &"attack_speed": "% СКОР. АТАКИ",
	&"speed": "% СКОРОСТИ", &"armor": "БРОНИ", &"dodge": "% УВОРОТА", &"pickup": "% ПОДБОРА", &"crit": "% КРИТА",
}
const _PERCENT_STATS: Array[StringName] = [&"damage", &"attack_speed", &"speed", &"dodge", &"pickup", &"crit"]


static func ids() -> Array[StringName]:
	var result: Array[StringName] = []
	for id: StringName in Balance.ITEMS:
		result.append(id)
	return result


static func title(item_id: StringName) -> String:
	return _TITLES[item_id]


static func tier(item_id: StringName) -> int:
	return Balance.ITEMS[item_id]["tier"]


static func icon(item_id: StringName) -> Texture2D:
	return load("res://assets/ui/item_%s.png" % item_id) as Texture2D


static func max_count(item_id: StringName) -> int:
	return Balance.ITEMS[item_id]["limit"]


static func at_limit(item_id: StringName) -> bool:
	var cap: int = max_count(item_id)
	return cap > 0 and GameState.item_count(item_id) >= cap


## Предметы тира `tier`, которые ещё можно взять.
static func pool(tier_value: int) -> Array[StringName]:
	var result: Array[StringName] = []
	for id: StringName in Balance.ITEMS:
		if Balance.ITEMS[id]["tier"] == tier_value and not at_limit(id):
			result.append(id)
	return result


static func _sign(value: float) -> String:
	return "+" if value >= 0.0 else "-"


## Текст карточки: плюсы и минусы построчно, эффекты словами.
static func description(item_id: StringName) -> String:
	var data: Dictionary = Balance.ITEMS[item_id]
	var lines: Array[String] = []
	var mods: Dictionary = data.get("mods", {})
	for stat_id: StringName in mods:
		var value: float = mods[stat_id]
		var suffix: String = _STAT_LABELS[stat_id]
		if stat_id in _PERCENT_STATS:
			lines.append("%s%d%s" % [_sign(value), absi(roundi(value)), suffix])
		else:
			lines.append("%s%d %s" % [_sign(value), absi(roundi(value)), suffix])
	var fx: Dictionary = data.get("fx", {})
	for key: StringName in fx:
		var v: int = roundi(fx[key])
		match key:
			&"coin_bonus":
				lines.append("+%d%% ГОВНА С ДРОПА" % v)
			&"repel":
				lines.append("%d%% ВРАГ ОТВАЛИВАЕТ ОТ ВОНИ" % v)
			&"thorns":
				lines.append("ВРАГИ РЯДОМ ПОЛУЧАЮТ %d УРОНА" % v)
			&"explode":
				lines.append("%d%% ВЗРЫВ ПРИ УБИЙСТВЕ" % v)
			&"lifesteal":
				lines.append("%d%% ХП ПРИ УБИЙСТВЕ" % v)
			&"pets":
				lines.append("+%d КРЫСА КУСАЕТ ВРАГОВ" % v)
			&"turrets":
				lines.append("+%d ТУРЕЛЬ НА ВОЛНУ" % v)
			&"discount":
				lines.append("-%d%% ЦЕН В ЛАРЬКЕ" % v)
	return "\n".join(lines)
