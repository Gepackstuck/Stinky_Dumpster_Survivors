class_name Quests
extends Node
## Н17: записки от бомжей - 3 задания на кладбище. Награда - кости для пса. Выполнил - записка меняется на новую.
## Autoload нет: живёт ребёнком уровня/кладбища не нужно - прогресс копится через EventBus из Achievements-подобного узла.
## Данные в Profile.quests: [{kind, enemy, hero, need, got, reward}].

const KINDS: Array[String] = ["kill", "kill_hero", "wave_hero", "win_hero", "boss"]


static func ensure() -> void:
	while Profile.quests.size() < Balance.QUEST_COUNT:
		Profile.quests.append(make())


static func make() -> Dictionary:
	var kind: String = KINDS[randi() % KINDS.size()]
	var heroes: Array[StringName] = []
	for h: StringName in Balance.CHARACTER_ORDER:
		if Profile.is_unlocked(h):
			heroes.append(h)
	var hero: StringName = heroes[randi() % heroes.size()] if not heroes.is_empty() else &"hobo"
	var common: Array[StringName] = []
	for e: StringName in Balance.WAVE_ENEMY_UNLOCK:
		common.append(e)
	var enemy: StringName = common[randi() % common.size()]
	var q: Dictionary = {"kind": kind, "enemy": String(enemy), "hero": String(hero), "got": 0}
	match kind:
		"kill":
			q["need"] = randi_range(10, 30) * 10
			q["reward"] = 5
		"kill_hero":
			q["need"] = randi_range(5, 15) * 10
			q["reward"] = 8
		"wave_hero":
			q["need"] = randi_range(8, 15)
			q["reward"] = 10
		"win_hero":
			q["need"] = 1
			q["reward"] = 15
		_:
			var bosses: Array[StringName] = Balance.ELITE_POOL + Balance.FINAL_BOSS_POOL
			q["enemy"] = String(bosses[randi() % bosses.size()])
			q["need"] = 1
			q["reward"] = 12
	return q


static func text(q: Dictionary) -> String:
	var hero: String = CharacterLibrary.short_title(StringName(q["hero"]))
	var enemy: String = EnemyNames.title(StringName(q["enemy"]))
	match String(q["kind"]):
		"kill": return TranslationServer.translate("УБЕЙ %d: %s") % [q["need"], enemy]
		"kill_hero": return TranslationServer.translate("УБЕЙ %d: %s ЗА %s") % [q["need"], enemy, hero]
		"wave_hero": return TranslationServer.translate("ДОЖИВИ ДО %d ВОЛНЫ ЗА %s") % [q["need"], hero]
		"win_hero": return TranslationServer.translate("ПОБЕДИ ЗА %s") % hero
	return TranslationServer.translate("ЗАВАЛИ: %s") % enemy


## Прогресс: убит враг.
static func on_kill(enemy_id: StringName) -> void:
	for q: Dictionary in Profile.quests:
		var kind: String = q["kind"]
		if StringName(q["enemy"]) != enemy_id:
			continue
		if kind == "kill" or kind == "boss" or (kind == "kill_hero" and StringName(q["hero"]) == GameState.character):
			q["got"] = int(q["got"]) + 1


## Прогресс: конец забега. Возвращает строку наград ("" - ничего не выполнено).
static func on_run_end(won: bool) -> String:
	var done: Array[String] = []
	for i: int in Profile.quests.size():
		var q: Dictionary = Profile.quests[i]
		var hero_ok: bool = StringName(q["hero"]) == GameState.character
		match String(q["kind"]):
			"wave_hero":
				if hero_ok:
					q["got"] = maxi(int(q["got"]), GameState.wave)
			"win_hero":
				if hero_ok and won:
					q["got"] = 1
		if int(q["got"]) >= int(q["need"]):
			Profile.bones += int(q["reward"])
			Profile.stat_add(&"quests_done", 1)
			done.append(TranslationServer.translate("ЗАПИСКА ВЫПОЛНЕНА: +%d КОСТЕЙ") % int(q["reward"]))
			Profile.quests[i] = make()
	if Profile.stat(&"quests_done") >= 10:
		Achievements.unlock(&"quests_10")
	if Profile.stat(&"quests_done") >= 1:
		Achievements.unlock(&"quests_1")
	return "\n".join(done)
