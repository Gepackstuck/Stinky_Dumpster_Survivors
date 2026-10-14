extends Node
## Профиль игрока между забегами: счётчики (убито, говна собрано, смертей, побед) и выбранный персонаж.
## Персонажи кладбища открываются по этим счётчикам. Сохраняется в user://profile.cfg.

const PATH: String = "user://profile.cfg"

var total_kills: int = 0
var total_coins: int = 0
var deaths: int = 0
var wins: int = 0
var selected: StringName = &"hobo"
var announced: Array[StringName] = []   # персонажи, про которых кладбище уже объявило «откопан»


func _ready() -> void:
	var fresh: bool = not _load()
	if fresh:
		for id: StringName in Balance.CHARACTER_ORDER:
			if is_unlocked(id):
				announced.append(id)   # стартовые не считаем «новыми»
		save()
	EventBus.player_died.connect(_record_run.bind(false))
	EventBus.run_won.connect(_record_run.bind(true))


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
	var data: Dictionary = Balance.CHARACTERS[character_id]
	return data["unlock"] == &"open" or counter(data["unlock"]) >= data["need"]


## Оружие в ларьке доступно? Записи нет в WEAPON_UNLOCK - открыто сразу.
func is_weapon_unlocked(weapon_id: StringName) -> bool:
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


func save() -> void:
	var cfg: ConfigFile = ConfigFile.new()
	cfg.set_value("stats", "total_kills", total_kills)
	cfg.set_value("stats", "total_coins", total_coins)
	cfg.set_value("stats", "deaths", deaths)
	cfg.set_value("stats", "wins", wins)
	cfg.set_value("hero", "selected", String(selected))
	var names: PackedStringArray = PackedStringArray()
	for id: StringName in announced:
		names.append(String(id))
	cfg.set_value("hero", "announced", names)
	cfg.save(PATH)


func _load() -> bool:
	var cfg: ConfigFile = ConfigFile.new()
	if cfg.load(PATH) != OK:
		return false
	total_kills = int(cfg.get_value("stats", "total_kills", 0))
	total_coins = int(cfg.get_value("stats", "total_coins", 0))
	deaths = int(cfg.get_value("stats", "deaths", 0))
	wins = int(cfg.get_value("stats", "wins", 0))
	var saved: StringName = StringName(str(cfg.get_value("hero", "selected", "hobo")))
	selected = saved if Balance.CHARACTERS.has(saved) else &"hobo"
	for entry: String in cfg.get_value("hero", "announced", PackedStringArray()):
		if Balance.CHARACTERS.has(StringName(entry)):
			announced.append(StringName(entry))
	return true
