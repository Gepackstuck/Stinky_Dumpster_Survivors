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


func killed(enemy_id: StringName) -> int:
	return int(enemy_kills.get(enemy_id, 0))


func _record_run(won: bool) -> void:
	total_kills += GameState.kills
	total_coins += GameState.run_coins_earned
	if won:
		wins += 1
	else:
		deaths += 1
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
	return true
