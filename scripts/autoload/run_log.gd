extends Node
## Журнал забегов игрока для разработчика: каждая волна, покупки, рерроллы, смерть/победа.
## Пишет JSON-строки в user://playlog/<дата>.jsonl (на маке: ~/Library/Application Support/Godot/app_userdata/StinkyDumpsterSurvivors/playlog/).
## Боты и тесты (Profile.sandbox) не пишутся. Autoload: RunLog. Только слушает EventBus.

const DIR: String = "user://playlog"

var _run_id: String = ""
var _kills_at_wave: int = 0
var _earned_at_wave: int = 0
var _shop: Array[Dictionary] = []   # действия в Ларьке после текущей волны


func _ready() -> void:
	EventBus.run_started.connect(_on_run_started)
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.shop_action.connect(func(kind: StringName, id: StringName, price: int) -> void:
		_shop.append({"do": kind, "id": id, "price": price, "coins_after": GameState.coins}))
	EventBus.perk_chosen.connect(func(p: StringName) -> void: _shop.append({"do": "level_pick", "id": p}))
	EventBus.player_died.connect(func() -> void: _finish("dead"))
	EventBus.run_won.connect(func() -> void: _finish("won"))


func _on_run_started() -> void:
	_run_id = Time.get_datetime_string_from_system().replace(":", "-")
	_kills_at_wave = 0
	_earned_at_wave = 0
	_shop.clear()
	_write({"ev": "run", "hero": GameState.character, "danger": GameState.danger, "mode": GameState.mode, "seed": GameState.seed_word,
		"coin_per_xp": Balance.COIN_PER_XP, "enemy_hp_mult": Balance.ENEMY_HP_MULT, "hp_growth": Balance.WAVE_HP_GROWTH})


func _on_wave_started(wave: int) -> void:
	if _shop.size() > 0:
		_write({"ev": "shop", "after_wave": wave - 1, "actions": _shop.duplicate(), "coins_left": GameState.coins})
		_shop.clear()
	_kills_at_wave = GameState.kills
	_earned_at_wave = GameState.run_coins_earned


func _on_wave_ended(wave: int) -> void:
	_write(_snapshot("wave", wave))


func _finish(result: String) -> void:
	if _run_id == "":
		return
	var d: Dictionary = _snapshot("end", GameState.wave)
	d["result"] = result
	d["killer"] = GameState.last_damage_source
	d["damage_by_source"] = GameState.damage_by_source.duplicate()
	d["time"] = snappedf(GameState.time, 0.1)
	_write(d)
	_run_id = ""


func _snapshot(ev: String, wave: int) -> Dictionary:
	var ws: Array[String] = []
	for w: Dictionary in GameState.weapons:
		ws.append("%s:%d" % [w["id"], w["tier"]])
	return {"ev": ev, "wave": wave, "kind": GameState.wave_kind, "mod": GameState.wave_mod, "season": GameState.season,
		"kills": GameState.kills - _kills_at_wave, "kills_total": GameState.kills, "earned": GameState.run_coins_earned - _earned_at_wave,
		"coins": GameState.coins, "level": GameState.level, "hp": snappedf(GameState.hp, 0.1), "max_hp": snappedf(GameState.max_hp, 0.1),
		"dmg_taken": snappedf(GameState.wave_damage_taken, 0.1), "weapons": ws, "items": GameState.items.duplicate(),
		"stats": {"dmg": snappedf(GameState.damage_mult, 0.01), "atk": snappedf(GameState.attack_speed_mult, 0.01), "crit": GameState.crit_percent,
			"armor": GameState.armor, "dodge": GameState.dodge_percent, "speed": snappedf(GameState.move_speed_mult, 0.01)}}


func _write(d: Dictionary) -> void:
	if Profile.sandbox or _run_id == "":
		return
	d["run"] = _run_id
	DirAccess.make_dir_recursive_absolute(DIR)
	var path: String = "%s/%s.jsonl" % [DIR, Time.get_date_string_from_system()]
	var f: FileAccess = FileAccess.open(path, FileAccess.READ_WRITE if FileAccess.file_exists(path) else FileAccess.WRITE)
	if f == null:
		return
	f.seek_end()
	f.store_line(JSON.stringify(d))
