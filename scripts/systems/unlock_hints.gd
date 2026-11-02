class_name UnlockHints
extends RefCounted
## Подсказки открытия: что ещё закрыто (оружие и герои), сколько осталось и что открылось только что.


static func _left_text(kind: StringName, left: int) -> String:
	match kind:
		&"kills":
			return "УБЕЙ ЕЩЁ %d ВРАГОВ" % left
		&"coins":
			return "СОБЕРИ ЕЩЁ %d ГОВНА" % left
		&"deaths":
			return "СДОХНИ ЕЩЁ %d РАЗ" % left if left > 1 else "СДОХНИ ЕЩЁ РАЗ"
		&"wins":
			return "ПРОЙДИ ИГРУ ЕЩЁ %d РАЗ" % left if left > 1 else "ПРОЙДИ ИГРУ ЕЩЁ РАЗ"
	return ""


## Закрытое оружие и герои: {title, text, fraction, weapon}. Отсортировано: ближе к открытию - раньше.
static func locked() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for weapon_id: StringName in Balance.WEAPON_UNLOCK:
		if Profile.is_weapon_unlocked(weapon_id):
			continue
		var rule: Dictionary = Balance.WEAPON_UNLOCK[weapon_id]
		var have: int = Profile.counter(rule["kind"])
		result.append({
			"title": PerkLibrary.title(StringName("w_" + String(weapon_id))),
			"text": _left_text(rule["kind"], rule["need"] - have),
			"fraction": float(have) / float(rule["need"]),
			"weapon": true,
		})
	for hero_id: StringName in Balance.CHARACTER_ORDER:
		if Profile.is_unlocked(hero_id):
			continue
		var data: Dictionary = Balance.CHARACTERS[hero_id]
		if data["unlock"] == &"ach":
			result.append({"title": CharacterLibrary.title(hero_id), "text": CharacterLibrary.unlock_text(hero_id), "fraction": 0.0, "weapon": false})
			continue
		var have_h: int = Profile.counter(data["unlock"])
		result.append({
			"title": CharacterLibrary.title(hero_id),
			"text": _left_text(data["unlock"], data["need"] - have_h),
			"fraction": float(have_h) / float(data["need"]),
			"weapon": false,
		})
	result.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["fraction"] > b["fraction"])
	return result


## Две строки для экрана смерти: что открылось в этом забеге и что ближе всего к открытию.
static func death_lines() -> Array[String]:
	var lines: Array[String] = []
	var fresh: Array[StringName] = Profile.fresh_weapon_unlocks()
	if not fresh.is_empty():
		var names: Array[String] = []
		for id: StringName in fresh:
			names.append(PerkLibrary.title(StringName("w_" + String(id))))
		lines.append("ОТКРЫТО В ЛАРЬКЕ: %s" % ", ".join(names))
		Profile.announce_weapons(fresh)
	var fresh_heroes: Array[StringName] = Profile.fresh_unlocks()
	if not fresh_heroes.is_empty():
		lines.append("ОТКОПАН НОВЫЙ ГЕРОЙ: ЗАГЛЯНИ НА КЛАДБИЩЕ")
	var all: Array[Dictionary] = locked()
	if not all.is_empty():
		var first: Dictionary = all[0]
		lines.append("СКОРО: %s. %s" % [first["title"], first["text"]])
	return lines
