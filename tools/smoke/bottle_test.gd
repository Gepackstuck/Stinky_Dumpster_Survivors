extends Node
## Н7: бутылка на поле, герой на ходу пинает - бахает по врагу. BOTTLE OK / FAIL, кадр tools/_preview/bottle_*.png

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
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/bottle_%s.png" % n))


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.4).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	(player.get(&"_health") as HealthComponent).setup(99999.0)
	var bg: BottleGrenades = level.find_children("*", "BottleGrenades", true, false).front() as BottleGrenades
	GameState.wave = 3
	bg.call("_spawn", player)
	var bottle: Sprite2D = (bg.get("_lying") as Array).front()
	bottle.global_position = player.global_position + Vector2(14.0, 0.0)
	var enemy: EnemyBase = EnemyBase.spawn_enemy(level, player, &"bruiser", player.global_position + Vector2(90.0, 0.0), 1.0)
	var hp0: float = enemy.health_pair().x
	await _shot("1")
	bottle.global_position = player.global_position + Vector2(4.0, 0.0)
	player.set(&"velocity", Vector2(80.0, 0.0))   # будто герой бежит вправо
	bg.call("_try_kick", player)
	await get_tree().create_timer(0.1).timeout
	await _shot("2")
	await get_tree().create_timer(0.6).timeout
	_check(not (bg.get("_lying") as Array).has(bottle), "бутылку пнули")
	_check(not is_instance_valid(enemy) or enemy.health_pair().x < hp0 or not enemy.is_alive(), "взрыв задел врага")
	print("BOTTLE OK" if _fails == 0 else "BOTTLE FAIL %d" % _fails)
	get_tree().quit()


func _check(ok: bool, what: String) -> void:
	if not ok:
		_fails += 1
		print("BOTTLE FAIL: ", what)
