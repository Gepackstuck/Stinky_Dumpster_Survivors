extends Node
## Профиль игрока между забегами: счётчики (убито, говна собрано, смертей, побед) и выбранный персонаж.
## Персонажи кладбища открываются по этим счётчикам. Сохраняется в user://profile.cfg.

const PATH: String = "user://profile.cfg"

var total_kills: int = 0
var total_coins: int = 0
var deaths: int = 0
var wins: int = 0
var selected: StringName = &"hobo"
var enemy_kills: Dictionary = {}   # id врага -> сколько убито за всё время (бестиарий)
var weapons_announced: Array[StringName] = []   # оружие, про которое экран смерти уже объявил «открыто»
var combos_found: Array[StringName] = []
var graffiti: Array = []
# Н16: пёс-спутник. Находишь в забеге, называешь, кормишь костями, одеваешь в шмотки с побед.
var dog_owned: bool = false
var dog_pending_name: bool = false   # подобрал - на кладбище спросят кличку
var dog_name: String = ""
var dog_level: int = 1
var bones: int = 0
var dog_enabled: bool = true
var dog_wear: String = ""
var dog_wardrobe: Array = []
var quests: Array = []                 # Н17: записки от бомжей
var last_quest_note: String = ""       # что выполнено в прошлом забеге - покажет кладбище   # Н30: последние смерти [{hero, wave}] - граффити на краю арены
var achievements: Array[StringName] = []    # открытые достижения (Achievements)
var mods_seen: Array[StringName] = []       # модификаторы волн, которые уже попадались
var stats: Dictionary = {}                  # счётчики для достижений: рывки, упоры...
var daily_best: Dictionary = {}            # ГГГГММДД -> лучшие очки ежедневки
var endless_best: int = 0                    # самая дальняя волна в бесконечности
var danger_unlocked: int = 0                 # максимальный открытый уровень опасности
var last_danger: int = 0
var hero_wins: Dictionary = {}               # герой -> Array[int] уровней опасности, на которых он победил (отметки на могиле)   # открытые комбо предметов
var mod_bag: Array[StringName] = []   # мешок модификаторов волн (без повторов, пока не выпадут все)
var _last_mod: StringName = &""
var sandbox: bool = false   # бот-ферма и тесты: всё открыто, на диск ничего не пишем (не портим живой профиль)
var announced: Array[StringName] = []   # персонажи, про которых кладбище уже объявило «откопан»


func _ready() -> void:
	var fresh: bool = not _load()
	if fresh:
		for id: StringName in Balance.CHARACTER_ORDER:
			if is_unlocked(id):
				announced.append(id)   # стартовые не считаем «новыми»
		_announce_open_weapons()
		save()
	EventBus.player_died.connect(_record_run.bind(false))
	EventBus.run_won.connect(_record_run.bind(true))
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.wave_ended.connect(func(_wave: int) -> void: save())


func _announce_open_weapons() -> void:
	for id: StringName in Balance.WEAPON_UNLOCK:
		if is_weapon_unlocked(id) and id not in weapons_announced:
			weapons_announced.append(id)


## Открыты, но экран смерти ещё не объявлял.
func fresh_weapon_unlocks() -> Array[StringName]:
	var result: Array[StringName] = []
	for id: StringName in Balance.WEAPON_UNLOCK:
		if is_weapon_unlocked(id) and id not in weapons_announced:
			result.append(id)
	return result


func announce_weapons(ids: Array[StringName]) -> void:
	for id: StringName in ids:
		if id not in weapons_announced:
			weapons_announced.append(id)
	save()


func _on_enemy_died(enemy_id: StringName, _at: Vector2) -> void:
	enemy_kills[enemy_id] = int(enemy_kills.get(enemy_id, 0)) + 1
	Quests.on_kill(enemy_id)


func killed(enemy_id: StringName) -> int:
	return int(enemy_kills.get(enemy_id, 0))


func _record_run(won: bool) -> void:
	if GameState.dog_found_run and not dog_owned:   # Н16: подобрал пса - на кладбище спросят кличку
		dog_owned = true
		dog_pending_name = true
		Achievements.unlock(&"dog_found")
	if dog_owned and won and randf() < Balance.DOG_WEAR_DROP_CHANCE:   # шмотка для пса с победы
		var left: Array = Balance.DOG_WEAR.filter(func(w: String) -> bool: return w not in dog_wardrobe)
		if not left.is_empty():
			dog_wardrobe.append(left[randi() % left.size()])
			if dog_wardrobe.size() >= Balance.DOG_WEAR.size():
				Achievements.unlock(&"dog_fashion")
	if GameState.mode == &"duel":
		save()
		return   # битва героев - не в статистику
	Quests.ensure()
	last_quest_note = Quests.on_run_end(won)
	if GameState.daily:
		var key: String = str(GameState.daily_seed)
		daily_best[key] = maxi(int(daily_best.get(key, 0)), GameState.run_score(won))
	if GameState.mode == &"endless":   # Н32: своя таблица режима
		stats[&"mode_endless_best"] = maxi(stat(&"mode_endless_best"), GameState.wave)
		if GameState.wave >= 25:
			Achievements.unlock(&"mode_endless_25")
		if GameState.wave >= 40:
			Achievements.unlock(&"mode_endless_40")
	if GameState.mode == &"closed":    # Н33
		if GameState.wave >= 10:
			Achievements.unlock(&"closed_10")
		if won:
			Achievements.unlock(&"closed_win")
	if GameState.endless:
		endless_best = maxi(endless_best, GameState.wave)
		save()
		return   # победа уже засчитана, смерть в бесконечности - не смерть забега
	total_kills += GameState.kills
	total_coins += GameState.run_coins_earned
	if won:
		wins += 1
		var list: Array = hero_wins.get(GameState.character, [])
		if GameState.danger not in list:
			list.append(GameState.danger)
		hero_wins[GameState.character] = list
		danger_unlocked = clampi(maxi(danger_unlocked, GameState.danger + 1), 0, Balance.DANGER_LEVELS.size() - 1)
	else:
		deaths += 1
		stat_add(StringName("deaths_" + String(GameState.character)), 1)
		if not graffiti.is_empty() and int(graffiti.back().get("wave", -1)) == GameState.wave and StringName(graffiti.back().get("hero", "")) == GameState.character:
			Achievements.unlock(&"deja_vu")   # сдох тем же героем на той же волне, что и в прошлый раз
		var at: Vector2 = GameState.death_position
		graffiti.append({"hero": String(GameState.character), "wave": GameState.wave, "x": at.x, "y": at.y})
		if graffiti.size() > Balance.GRAFFITI_KEEP:
			graffiti = graffiti.slice(graffiti.size() - Balance.GRAFFITI_KEEP)   # живое кладбище: грибы и мухи по смертям героя
	save()


func counter(kind: StringName) -> int:
	match kind:
		&"kills":
			return total_kills
		&"coins":
			return total_coins
		&"deaths":
			return deaths
		&"wins":
			return wins
	return 0


func is_unlocked(character_id: StringName) -> bool:
	if sandbox:
		return true
	var data: Dictionary = Balance.CHARACTERS[character_id]
	return data["unlock"] == &"open" or counter(data["unlock"]) >= data["need"]


## Оружие в ларьке доступно? Записи нет в WEAPON_UNLOCK - открыто сразу.
func is_weapon_unlocked(weapon_id: StringName) -> bool:
	if sandbox:
		return true
	if not Balance.WEAPON_UNLOCK.has(weapon_id):
		return true
	var rule: Dictionary = Balance.WEAPON_UNLOCK[weapon_id]
	return counter(rule["kind"]) >= rule["need"]


## Открыты, но кладбище ещё не показывало «НОВЕНЬКИЙ».
func fresh_unlocks() -> Array[StringName]:
	var result: Array[StringName] = []
	for id: StringName in Balance.CHARACTER_ORDER:
		if is_unlocked(id) and id not in announced:
			result.append(id)
	return result


func announce(ids: Array[StringName]) -> void:
	for id: StringName in ids:
		if id not in announced:
			announced.append(id)
	save()


## Следующий модификатор волны из мешка: перемешанный набор всех модификаторов, тянем по одному,
## пустой - перемешиваем заново (первым не ставим только что выпавший). Сохраняется в профиль.
func stat(key: StringName) -> int:
	return int(stats.get(key, 0))


func stat_add(key: StringName, amount: int) -> void:
	stats[key] = stat(key) + amount


func mark_mod_seen(mod: StringName) -> void:
	if mod not in mods_seen:
		mods_seen.append(mod)


func found_combo(combo_id: StringName) -> void:
	if combo_id not in combos_found:
		combos_found.append(combo_id)
		save()


func next_mod() -> StringName:
	if mod_bag.is_empty():
		var fresh: Array = Balance.WAVE_MODS.duplicate()
		fresh.shuffle()
		if not fresh.is_empty() and fresh[0] == _last_mod:
			fresh.push_back(fresh.pop_front())
		mod_bag.assign(fresh)
	var mod: StringName = mod_bag.pop_front()
	_last_mod = mod
	save()
	return mod


func save() -> void:
	if sandbox:
		return
	var cfg: ConfigFile = ConfigFile.new()
	cfg.set_value("stats", "total_kills", total_kills)
	cfg.set_value("stats", "total_coins", total_coins)
	cfg.set_value("stats", "deaths", deaths)
	cfg.set_value("stats", "wins", wins)
	for id: StringName in enemy_kills:
		cfg.set_value("bestiary", String(id), enemy_kills[id])
	cfg.set_value("hero", "selected", String(selected))
	var names: PackedStringArray = PackedStringArray()
	for id: StringName in announced:
		names.append(String(id))
	cfg.set_value("hero", "announced", names)
	var wnames: PackedStringArray = PackedStringArray()
	for id: StringName in weapons_announced:
		wnames.append(String(id))
	cfg.set_value("hero", "weapons_announced", wnames)
	var bag: PackedStringArray = PackedStringArray()
	for id: StringName in mod_bag:
		bag.append(String(id))
	cfg.set_value("run", "mod_bag", bag)
	var combos: PackedStringArray = PackedStringArray()
	for id: StringName in combos_found:
		combos.append(String(id))
	cfg.set_value("run", "combos_found", combos)
	cfg.set_value("run", "graffiti", graffiti)
	cfg.set_value("dog", "owned", dog_owned)
	cfg.set_value("dog", "pending_name", dog_pending_name)
	cfg.set_value("dog", "name", dog_name)
	cfg.set_value("dog", "level", dog_level)
	cfg.set_value("dog", "bones", bones)
	cfg.set_value("dog", "enabled", dog_enabled)
	cfg.set_value("dog", "wear", dog_wear)
	cfg.set_value("dog", "wardrobe", dog_wardrobe)
	cfg.set_value("quests", "list", quests)
	cfg.set_value("danger", "unlocked", danger_unlocked)
	cfg.set_value("modes", "endless_best", endless_best)
	var ach: PackedStringArray = PackedStringArray()
	for id: StringName in achievements:
		ach.append(String(id))
	cfg.set_value("achievements", "unlocked", ach)
	var seen: PackedStringArray = PackedStringArray()
	for id: StringName in mods_seen:
		seen.append(String(id))
	cfg.set_value("achievements", "mods_seen", seen)
	for key: StringName in stats:
		cfg.set_value("counters", String(key), stats[key])
	for key: String in daily_best:
		cfg.set_value("daily", key, daily_best[key])
	cfg.set_value("danger", "last", last_danger)
	for hero: StringName in hero_wins:
		cfg.set_value("danger_wins", String(hero), hero_wins[hero])
	cfg.set_value("run", "last_mod", String(_last_mod))
	cfg.save(PATH)


func _load() -> bool:
	var cfg: ConfigFile = ConfigFile.new()
	if cfg.load(PATH) != OK:
		return false
	total_kills = int(cfg.get_value("stats", "total_kills", 0))
	total_coins = int(cfg.get_value("stats", "total_coins", 0))
	deaths = int(cfg.get_value("stats", "deaths", 0))
	wins = int(cfg.get_value("stats", "wins", 0))
	if cfg.has_section("bestiary"):
		for key: String in cfg.get_section_keys("bestiary"):
			enemy_kills[StringName(key)] = int(cfg.get_value("bestiary", key, 0))
	var saved: StringName = StringName(str(cfg.get_value("hero", "selected", "hobo")))
	selected = saved if Balance.CHARACTERS.has(saved) else &"hobo"
	for entry: String in cfg.get_value("hero", "announced", PackedStringArray()):
		if Balance.CHARACTERS.has(StringName(entry)):
			announced.append(StringName(entry))
	if cfg.has_section_key("hero", "weapons_announced"):
		for entry_w: String in cfg.get_value("hero", "weapons_announced", PackedStringArray()):
			weapons_announced.append(StringName(entry_w))
	else:
		_announce_open_weapons()   # старый профиль: уже открытое новым не считаем
	for entry_m: String in cfg.get_value("run", "mod_bag", PackedStringArray()):
		if Balance.WAVE_MOD_DATA.has(StringName(entry_m)):
			mod_bag.append(StringName(entry_m))
	_last_mod = StringName(str(cfg.get_value("run", "last_mod", "")))
	danger_unlocked = int(cfg.get_value("danger", "unlocked", 0))
	endless_best = int(cfg.get_value("modes", "endless_best", 0))
	for entry_a: String in cfg.get_value("achievements", "unlocked", PackedStringArray()):
		achievements.append(StringName(entry_a))
	for entry_s: String in cfg.get_value("achievements", "mods_seen", PackedStringArray()):
		mods_seen.append(StringName(entry_s))
	if cfg.has_section("counters"):
		for key: String in cfg.get_section_keys("counters"):
			stats[StringName(key)] = int(cfg.get_value("counters", key, 0))
	if cfg.has_section("daily"):
		for key: String in cfg.get_section_keys("daily"):
			daily_best[key] = int(cfg.get_value("daily", key, 0))
	last_danger = int(cfg.get_value("danger", "last", 0))
	if cfg.has_section("danger_wins"):
		for key: String in cfg.get_section_keys("danger_wins"):
			hero_wins[StringName(key)] = cfg.get_value("danger_wins", key, [])
	graffiti = cfg.get_value("run", "graffiti", [])
	dog_owned = bool(cfg.get_value("dog", "owned", false))
	dog_pending_name = bool(cfg.get_value("dog", "pending_name", false))
	dog_name = str(cfg.get_value("dog", "name", ""))
	dog_level = int(cfg.get_value("dog", "level", 1))
	bones = int(cfg.get_value("dog", "bones", 0))
	dog_enabled = bool(cfg.get_value("dog", "enabled", true))
	dog_wear = str(cfg.get_value("dog", "wear", ""))
	dog_wardrobe = cfg.get_value("dog", "wardrobe", [])
	quests = cfg.get_value("quests", "list", [])
	for entry_c: String in cfg.get_value("run", "combos_found", PackedStringArray()):
		if Balance.ITEM_COMBOS.has(StringName(entry_c)):
			combos_found.append(StringName(entry_c))
	return true


## Н16: цена следующего уровня пса в костях (0 - максимум).
func dog_feed_cost() -> int:
	if dog_level >= Balance.DOG_MAX_LEVEL:
		return 0
	return Balance.DOG_FEED_BASE + dog_level * Balance.DOG_FEED_STEP


## Покормить пса костями: +1 уровень. true - покормил.
func feed_dog() -> bool:
	var cost: int = dog_feed_cost()
	if cost == 0 or bones < cost:
		return false
	bones -= cost
	dog_level += 1
	if dog_level >= Balance.DOG_MAX_LEVEL:
		Achievements.unlock(&"dog_level_10")
	save()
	return true
