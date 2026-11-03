extends Node
## Журнал забегов игрока для разработчика: каждая волна, покупки, рерроллы, смерть/победа.
## Пишет JSON-строки в user://playlog/<дата>.jsonl (на маке: ~/Library/Application Support/Godot/app_userdata/StinkyDumpsterSurvivors/playlog/).
## Боты и тесты (Profile.sandbox) не пишутся. Autoload: RunLog. Только слушает EventBus.

const DIR: String = "user://playlog"

var dir: String = DIR   # тесты пишут в свою папку, чтобы не портить журнал игрока

var _run_id: String = ""
var _kills_at_wave: int = 0
var _earned_at_wave: int = 0
var _shop: Array[Dictionary] = []   # действия в Ларьке после текущей волны
var _dmg_at_wave: Dictionary = {}    # урон по источникам на начало волны (для урона за волну)
var _taken: Dictionary = {}          # кто сколько снял с героя за волну
var _hits: int = 0
var _hp_min: float = 0.0
var _wave_t0: int = 0


func _ready() -> void:
	EventBus.run_started.connect(_on_run_started)
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.shop_action.connect(func(kind: StringName, id: StringName, price: int) -> void:
		_shop.append({"do": kind, "id": id, "price": price, "coins_after": GameState.coins}))
	EventBus.perk_chosen.connect(func(p: StringName) -> void: _shop.append({"do": "card", "id": p}))
	EventBus.player_hit.connect(func(dmg: float) -> void:
		var src: String = String(GameState.last_damage_source)
		_taken[src] = snappedf(float(_taken.get(src, 0.0)) + dmg, 0.1)
		_hits += 1
		_hp_min = minf(_hp_min, GameState.hp))
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
	_dmg_at_wave = GameState.damage_by_source.duplicate()
	_taken.clear()
	_hits = 0
	_hp_min = GameState.hp
	_wave_t0 = Time.get_ticks_msec()


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
	var dealt: Dictionary = {}
	for src: Variant in GameState.damage_by_source:
		var d: float = float(GameState.damage_by_source[src]) - float(_dmg_at_wave.get(src, 0.0))
		if d > 0.5:
			dealt[String(src)] = roundi(d)
	return {"ev": ev, "wave": wave, "dealt": dealt, "taken_by": _taken.duplicate(), "hits": _hits, "hp_min": snappedf(_hp_min, 0.1),
		"sec": snappedf((Time.get_ticks_msec() - _wave_t0) / 1000.0, 0.1), "fps": Engine.get_frames_per_second(),
		"enemy_hp_x": snappedf(WaveRules.hp_mult(wave), 0.01), "enemy_dmg_x": snappedf(WaveRules.damage_mult(wave), 0.01),
		"companions": {"rats": GameState.pet_count, "turrets": GameState.turret_count, "ghost_drunk": GameState.ghost_drunk_count, "other": GameState.comp_counts.duplicate()},
		"extra_projectiles": GameState.extra_projectiles, "perks": GameState.perk_stacks.duplicate(), "kind": GameState.wave_kind, "mod": GameState.wave_mod, "season": GameState.season,
		"kills": GameState.kills - _kills_at_wave, "kills_total": GameState.kills, "earned": GameState.run_coins_earned - _earned_at_wave,
		"coins": GameState.coins, "level": GameState.level, "hp": snappedf(GameState.hp, 0.1), "max_hp": snappedf(GameState.max_hp, 0.1),
		"dmg_taken": snappedf(GameState.wave_damage_taken, 0.1), "weapons": ws, "items": GameState.items.duplicate(),
		"stats": {"dmg": snappedf(GameState.damage_mult, 0.01), "atk": snappedf(GameState.attack_speed_mult, 0.01), "crit": GameState.crit_percent,
			"armor": GameState.armor, "dodge": GameState.dodge_percent, "speed": snappedf(GameState.move_speed_mult, 0.01),
			"regen": snappedf(GameState.regen_hp, 0.1), "lifesteal": GameState.lifesteal_percent, "coin_bonus": snappedf(GameState.coin_bonus, 0.01)}}


func _write(d: Dictionary) -> void:
	if Profile.sandbox or _run_id == "":
		return
	d["run"] = _run_id
	DirAccess.make_dir_recursive_absolute(dir)
	var path: String = "%s/%s.jsonl" % [dir, Time.get_date_string_from_system()]
	var f: FileAccess = FileAccess.open(path, FileAccess.READ_WRITE if FileAccess.file_exists(path) else FileAccess.WRITE)
	if f == null:
		return
	f.seek_end()
	f.store_line(JSON.stringify(d))
