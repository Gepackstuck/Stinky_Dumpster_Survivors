extends Node
## ТЕСТ кучи-лотереи и рулетки: куча далеко (стрелка), вступили, Ларёк -> рулетка -> модификатор на волне.
## Кадры (в окне): tools/_preview/pile_*.png. В конце PILE OK / FAIL.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _fails: int = 0


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print("PILE ", "ok   " if ok else "FAIL ", what)
	if not ok:
		_fails += 1


func _shot(n: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/pile_%s.png" % n))


func _run() -> void:
	GameState.character = &"skater"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.2).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	var pile: ModPile = ModPile.new()
	level.add_child(pile)
	pile.global_position = player.global_position + Vector2(260.0, 40.0)
	await get_tree().create_timer(0.6).timeout
	await _shot("1_pointer")
	pile.global_position = player.global_position + Vector2(40.0, 0.0)
	await get_tree().create_timer(0.5).timeout
	await _shot("2_pile")
	player.global_position = pile.global_position
	await get_tree().create_timer(0.3).timeout
	_check(GameState.roulette_pending, "вступил - рулетка ждёт")
	await _shot("3_stepped")
	EventBus.next_wave_requested.emit()
	await get_tree().create_timer(1.2, true).timeout
	await _shot("4_spin")
	await get_tree().create_timer(3.4, true).timeout
	await _shot("5_result")
	await get_tree().create_timer(2.0, true).timeout
	_check(GameState.wave_mod != &"", "модификатор волны с рулетки: %s" % GameState.wave_mod)
	print("PILE OK" if _fails == 0 else "PILE FAIL %d" % _fails)
	get_tree().quit()
