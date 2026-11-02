extends Node
## Погода волны: для каждого сезона - баннер и бой через 6 с. Пишет SEASON OK и кадры tools/_preview/season_<id>_*.png.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")

var _fails: int = 0


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _shot(n: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/season_%s.png" % n))


func _find(root: Node, script_end: String) -> Node:
	for n: Node in root.find_children("*", "", true, false):
		if n.get_script() != null and String((n.get_script() as Script).resource_path).ends_with(script_end):
			return n
	return null


func _run() -> void:
	# шанс и правила выпадения
	var got: int = 0
	var prev: StringName = &""
	for i: int in 2000:
		var s: StringName = WaveRules.roll_season(5, &"normal")
		if s != &"":
			got += 1
			if s == prev:
				_fails += 1
				print("SEASON FAIL: погода повторилась подряд")
				break
			prev = s
	if absf(got / 2000.0 - Balance.SEASON_WAVE_CHANCE) > 0.04:
		_fails += 1
		print("SEASON FAIL: шанс %.2f" % (got / 2000.0))
	if WaveRules.roll_season(1, &"normal") != &"" or WaveRules.roll_season(9, &"boss") != &"":
		_fails += 1
		print("SEASON FAIL: погода на 1-й или особой волне")
	GameState.character = &"granny"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.4).timeout
	get_tree().paused = false
	var hurt: HurtboxComponent = level.find_children("*", "HurtboxComponent", true, false).filter(func(n: Node) -> bool: return n.get_parent().is_in_group(&"player")).front()
	hurt.grant_invulnerability(999.0)
	for n: Node in level.find_children("*", "", true, false):   # волна не кончается: смотрим погоду спокойно
		if n.get_script() != null and String((n.get_script() as Script).resource_path).ends_with("wave_manager.gd"):
			n.process_mode = Node.PROCESS_MODE_DISABLED
	GameState.wave_time_left = 999.0   # бабка стоит столбом - не даём ей сдохнуть
	var hp0: float = WaveRules.hp_mult(5)
	for s: StringName in Balance.SEASON_ORDER:
		GameState.season = s
		_find(level, "ground.gd").call("_apply_season")
		_find(level, "wave_mod_badge.gd").call("_refresh")
		(level.find_children("*", "WeatherOverlay", true, false).front() as WeatherOverlay).call("_apply")
		_find(level, "wave_banner.gd").call("_on_wave_started", GameState.wave)
		await get_tree().create_timer(1.1).timeout
		await _shot(String(s) + "_1")
		await get_tree().create_timer(7.0).timeout
		await _shot(String(s) + "_2")
		var hz: WeatherHazards = level.find_children("*", "WeatherHazards", true, false).front() as WeatherHazards
		var spots: int = (hz.get("_spots") as Array).size()
		var drops: int = (hz.get("_drops") as Array).size()
		print("WEATHER ", s, " spots ", spots, " drops ", drops, " hp ", GameState.hp)
		if (s == &"autumn" or s == &"winter") and spots == 0:
			_fails += 1
			print("SEASON FAIL: нет луж/сугробов")
		if s == &"spring" and drops == 0:
			_fails += 1
			print("SEASON FAIL: нет подснежников")
		hz.call("_clear")
	if not is_equal_approx(WaveRules.hp_mult(5), hp0 * Balance.SEASONS[&"spring"].get("enemy_hp", 1.0)):
		_fails += 1
		print("SEASON FAIL: множитель HP")
	print("SEASON OK" if _fails == 0 else "SEASON FAIL %d" % _fails)
	get_tree().quit()
