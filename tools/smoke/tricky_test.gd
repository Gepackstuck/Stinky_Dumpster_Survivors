extends Node
## Хитрые враги: щит режет урон спереди, зеркало отражает, бомж прыгает к игроку.
## Пишет TRICKY OK / TRICKY FAIL и кадры tools/_preview/tricky_*.png (если есть окно).

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")

var _fails: int = 0


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	if not ok:
		_fails += 1
		print("TRICKY FAIL: ", what)


func _shot(n: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/tricky_%s.png" % n))


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.2).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	player.process_mode = Node.PROCESS_MODE_DISABLED   # герой не стреляет и не ходит - мерим чисто
	var p: Vector2 = player.global_position
	var shield: EnemyBase = EnemyBase.spawn_enemy(level, player, &"shield_bearer", p + Vector2(40.0, 0.0), 1.0)
	var mirror: EnemyBase = EnemyBase.spawn_enemy(level, player, &"mirror", p + Vector2(-40.0, 10.0), 1.0)
	var blinker: EnemyBase = EnemyBase.spawn_enemy(level, player, &"blinker", p + Vector2(0.0, -120.0), 1.0)
	await get_tree().create_timer(0.3).timeout
	var hp0: float = shield.health_pair().x
	shield.hit_by_weapon(10.0)
	_check(is_equal_approx(shield.health_pair().x, hp0 - 10.0 * Balance.SHIELD_BLOCK), "щит спереди режет урон %s -> %s" % [hp0, shield.health_pair().x])
	var mb: BossBrain = null
	for c: Node in mirror.get_children():
		if c is BossBrain:
			mb = c
	mb.set(&"_phase", 2)
	mb.set(&"_timer", 5.0)
	var mhp: float = mirror.health_pair().x
	mirror.hit_by_weapon(10.0)
	_check(is_equal_approx(mirror.health_pair().x, mhp), "блестящее зеркало не получает урон")
	await _shot("1")
	var start: Vector2 = blinker.global_position
	await get_tree().create_timer(Balance.BLINKER_INTERVAL_SEC + Balance.BLINKER_WARN_SEC + 0.5).timeout
	await _shot("2")
	_check(blinker.global_position.distance_to(p) < 70.0 and blinker.global_position.distance_to(start) > 40.0, "бомж телепортнулся к игроку")
	# Н21 щипач: тырит лежащую слизь, после смерти роняет вдвое
	for k: int in 3:
		EventBus.xp_drop_requested.emit(p + Vector2(-80.0, 60.0 + k * 4.0), 3)
	await get_tree().process_frame
	var thief: EnemyBase = EnemyBase.spawn_enemy(level, player, &"thief", p + Vector2(-110.0, 60.0), 1.0)
	await get_tree().create_timer(2.5).timeout
	var tb: Node = null
	for c: Node in thief.get_children():
		if c is BossBrain:
			tb = c
	_check(int(tb.get(&"_stolen")) > 0, "щипач стырил слизь")
	await _shot("3")
	var before: int = get_tree().get_nodes_in_group(&"pickups").filter(func(n: Node) -> bool: return n.is_inside_tree()).size()
	thief.hit_by_weapon(9999.0)
	await get_tree().create_timer(0.3).timeout
	var after: int = get_tree().get_nodes_in_group(&"pickups").filter(func(n: Node) -> bool: return n.is_inside_tree()).size()
	_check(after > before, "мешок щипача лопнул")
	print("TRICKY OK" if _fails == 0 else "TRICKY FAIL %d" % _fails)
	get_tree().quit()
