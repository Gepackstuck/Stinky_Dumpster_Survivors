class_name WeaponLibrary
extends RefCounted
## Оружие: свойства с учётом тира, классы и бонусы наборов (как в Brotato).
## Числа - в Balance.WEAPONS / WEAPON_TIER_PROPS / WEAPON_CLASSES / WEAPON_CLASS_BONUS.

const CLASS_TITLES: Dictionary[StringName, String] = {
	&"kitchen": "КУХОННОЕ", &"household": "ХОЗЯЙСТВЕННОЕ", &"guns": "СТРЕЛЯЛКИ",
	&"fire": "ОГНЕОПАСНОЕ", &"stinky": "ВОНЮЧЕЕ", &"prison": "ЗОНОВСКОЕ",
}
const CLASS_SHORT: Dictionary[StringName, String] = {   # для тесных мест (карточка Ларька, строка наборов)
	&"kitchen": "КУХНЯ", &"household": "ХОЗ", &"guns": "СТВОЛЫ", &"fire": "ОГОНЬ", &"stinky": "ВОНЬ", &"prison": "ЗОНА",
}
const CLASS_COLORS: Dictionary[StringName, Color] = {
	&"kitchen": Color(1.0, 0.75, 0.3), &"household": Color(0.55, 0.75, 1.0), &"guns": Color(0.85, 0.85, 0.9),
	&"fire": Color(1.0, 0.45, 0.05), &"stinky": Color(0.2235, 1.0, 0.0784), &"prison": Color(0.75, 0.45, 1.0),
}
const TEX: GDScript = preload("res://scripts/systems/tex.gd")
const MIN_SET: int = 2   # бонус набора начинается с двух оружий класса
## Подписи свойств, которые растут с тиром (для карточки в Ларьке).
const _PROP_LABELS: Dictionary[String, String] = {
	"ricochets": "ОТСКОКОВ", "pierce": "ПРОБИВАЕТ", "pellets": "ДРОБИН", "chain_jumps": "ПРЫЖКОВ МОЛНИИ",
	"radius": "РАДИУС", "aoe_radius": "РАДИУС ВЗРЫВА", "reach": "ДЛИНА", "arc_deg": "ДУГА",
	"knockback": "ОТБРОС", "beam_half_width": "ШИРИНА ЛУЧА", "burn_duration": "ГОРИТ СЕК",
	"slow_duration": "ТОРМОЗИТ СЕК", "proj_life": "ДАЛЬНОСТЬ",
}


## Свойство оружия на тире: значение из WEAPONS (или default) + прибавка тира.
static func stat(weapon_id: StringName, tier: int, key: String, default: Variant = 0.0) -> Variant:
	var base: Variant = Balance.WEAPONS[weapon_id].get(key, default)
	var bonus: Array = Balance.WEAPON_TIER_PROPS.get(weapon_id, {}).get(key, [])
	if bonus.is_empty() or tier < 1:
		return base
	return base + bonus[clampi(tier, 1, 4) - 1]


static func classes(weapon_id: StringName) -> Array:
	return Balance.WEAPON_CLASSES.get(weapon_id, [])


static func class_title(class_id: StringName) -> String:
	return CLASS_TITLES.get(class_id, String(class_id).to_upper())


static func class_icon(class_id: StringName) -> Texture2D:
	return TEX.load_tex("res://assets/ui/class_%s_s.png" % class_id)


## Сколько оружий каждого класса в слотах: {class_id: count}.
static func class_counts(weapons: Array[Dictionary]) -> Dictionary:
	var counts: Dictionary = {}
	for entry: Dictionary in weapons:
		for class_id: StringName in classes(entry["id"]):
			counts[class_id] = counts.get(class_id, 0) + 1
	return counts


## Величина бонуса набора при count оружиях класса (0 — набора нет).
static func set_value(class_id: StringName, count: int) -> float:
	if count < MIN_SET:
		return 0.0
	var values: Array = Balance.WEAPON_CLASS_BONUS[class_id]["values"]
	return values[mini(count, MIN_SET + values.size() - 1) - MIN_SET]


## Бонус набора как запись {mods, fx} — для GameState и текста (ItemLibrary.describe).
static func set_bonus(class_id: StringName, count: int) -> Dictionary:
	var value: float = set_value(class_id, count)
	var data: Dictionary = Balance.WEAPON_CLASS_BONUS[class_id]
	if value == 0.0:
		return {}
	if data.has("mod"):
		return {"mods": {data["mod"]: value}}
	return {"fx": {data["fx"]: value}}


static func set_bonus_text(class_id: StringName, count: int) -> String:
	var bonus: Dictionary = set_bonus(class_id, count)
	return ItemLibrary.describe(bonus) if not bonus.is_empty() else ""


## Строка про классы для карточки оружия: что даст покупка этого оружия к твоим наборам.
static func classes_line(weapon_id: StringName) -> String:
	var counts: Dictionary = class_counts(GameState.weapons)
	var parts: Array[String] = []
	for class_id: StringName in classes(weapon_id):
		parts.append("%s %d" % [CLASS_SHORT[class_id], counts.get(class_id, 0) + 1])
	return "  ".join(parts)


## Свойства, выросшие от тира (для карточки): «ОТСКОКОВ: 3».
static func tier_props_lines(weapon_id: StringName, tier: int) -> Array[String]:
	var lines: Array[String] = []
	for key: String in Balance.WEAPON_TIER_PROPS.get(weapon_id, {}):
		var value: Variant = stat(weapon_id, tier, key)
		var label: String = _PROP_LABELS.get(key, key.to_upper())
		if key == "proj_life":
			lines.append("%s: %d" % [label, roundi(value * float(Balance.WEAPONS[weapon_id].get("proj_speed", Balance.PROJECTILE_SPEED)))])
		elif value is float and not is_equal_approx(value, roundf(value)):
			lines.append("%s: %.1f" % [label, value])
		else:
			lines.append("%s: %d" % [label, roundi(value)])
	return lines


## Активные наборы для экранов: «ВОНЮЧЕЕ 3: 6% ВРАГ ОТВАЛИВАЕТ ОТ ВОНИ».
static func active_sets_lines(short: bool = false) -> Array[String]:
	var counts: Dictionary = class_counts(GameState.weapons)
	var lines: Array[String] = []
	for class_id: StringName in CLASS_TITLES:
		var count: int = counts.get(class_id, 0)
		if count >= MIN_SET:
			lines.append("%s %d: %s" % [CLASS_SHORT[class_id] if short else class_title(class_id), count, set_bonus_text(class_id, count)])
	return lines
