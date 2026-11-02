class_name BuildAdvisor
extends RefCounted
## Советчик: ищет в билде главную дурость и говорит о ней грубо (без мата). Пороги - в Balance.ADVISOR_*.
## issues() - список по важности; top() - самая важная или пусто.


static func issues() -> Array[String]:
	var out: Array[String] = []
	var wave: int = GameState.wave
	var weapons: Array[Dictionary] = GameState.weapons
	if weapons.is_empty():
		out.append("ТЫ БЕЗ ОРУЖИЯ. ТЫ ЧЕМ БИТЬСЯ СОБРАЛСЯ, ВЗГЛЯДОМ?")
	for i: int in weapons.size():
		if GameState.find_merge_partner(i) >= 0:
			out.append("ДВЕ ОДИНАКОВЫЕ ПУШКИ ОДНОГО ТИРА. ОБЪЕДИНИ, ТУПИЦА")
			break
	if wave >= Balance.ADVISOR_SLOTS_WAVE and weapons.size() <= Balance.WEAPON_SLOTS - 3:
		out.append("ПОЛОВИНА РУК ПУСТАЯ. КУПИ ПУШЕК, ЖМОТ")
	if GameState.max_hp < Balance.ADVISOR_LOW_HP and wave >= Balance.ADVISOR_HP_WAVE:
		out.append("ХП КАК У ТАРАКАНА. БЕРИ ЖИВУЧЕСТЬ, ПОКА НЕ РАЗДАВИЛИ")
	var melee: int = 0
	for w: Dictionary in weapons:
		if Balance.WEAPONS[w["id"]].has("reach"):
			melee += 1
	if weapons.size() >= 3 and melee == weapons.size() and GameState.armor <= 0.0 and wave >= 4:
		out.append("ВСЁ В БЛИЖНЕМ БОЮ И БРОНЯ НОЛЬ. ТЕБЯ СОЖРУТ ВПРИКУСКУ")
	if weapons.size() >= 4 and WeaponLibrary.active_sets_lines().is_empty():
		out.append("НИ ОДНОГО НАБОРА. ОРУЖИЕ ИЗ РАЗНЫХ ПОМОЕК")
	if GameState.damage_mult < 1.0 and wave >= 5:
		out.append("УРОН В МИНУСЕ. ТЫ ЛЕЧИШЬ ВРАГОВ СВОИМ ВИДОМ")
	if GameState.coins >= Balance.ADVISOR_HOARD_COINS:
		out.append("СИДИШЬ НА КУЧЕ ГОВНА. ПОМРЁШЬ БОГАТЫМ И ТУПЫМ")
	return out


static func top() -> String:
	var list: Array[String] = issues()
	return list[0] if not list.is_empty() else ""
