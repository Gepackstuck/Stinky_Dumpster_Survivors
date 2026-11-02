extends BossBrain
## Глючный бомж: идёт к игроку, а время от времени прыгает к нему через фиолетовую дыру.
## Сначала на земле появляется метка (успей отойти), потом бомж исчезает и вылезает из неё.

const MARK: Texture2D = preload("res://assets/sprites/fx_blink_mark.png")

var _timer: float = 1.5
var _warn_left: float = 0.0
var _dest: Vector2 = Vector2.ZERO
var _mark: Sprite2D = null


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	super.setup(owner_enemy, player)
	_timer = randf_range(1.0, Balance.BLINKER_INTERVAL_SEC)


func physics_tick(delta: float) -> void:
	if _warn_left > 0.0:
		_warn_left -= delta
		boss.speed_mult = 0.0
		boss.modulate.a = clampf(_warn_left / Balance.BLINKER_WARN_SEC, 0.2, 1.0)
		if _warn_left <= 0.0:
			_jump()
		return
	boss.speed_mult = 1.0
	_timer -= delta
	if _timer <= 0.0 and distance_to_target() < Balance.BLINKER_RANGE:
		_timer = Balance.BLINKER_INTERVAL_SEC
		_dest = _pick_dest()
		_warn_left = Balance.BLINKER_WARN_SEC
		_show_mark()


func _pick_dest() -> Vector2:
	var angle: float = randf() * TAU
	var dist: float = randf_range(Balance.BLINKER_LAND_DIST.x, Balance.BLINKER_LAND_DIST.y)
	var margin: float = 16.0
	var p: Vector2 = target.global_position + Vector2.from_angle(angle) * dist
	return p.clamp(Vector2(margin, margin), Vector2(Balance.ARENA_SIZE - margin, Balance.ARENA_SIZE - margin))


func _show_mark() -> void:
	if _mark == null:
		_mark = Sprite2D.new()
		_mark.texture = MARK
		_mark.hframes = 4
		_mark.top_level = true
		_mark.z_index = -1
		boss.add_child(_mark)
	_mark.global_position = _dest
	_mark.visible = true
	var tween: Tween = _mark.create_tween().set_loops(3)
	for f: int in 4:
		tween.tween_property(_mark, ^"frame", f, Balance.BLINKER_WARN_SEC / 12.0)


func _jump() -> void:
	var tree: SceneTree = boss.get_tree()
	HitFx.burst(tree, boss.global_position, Color(0.47, 0.0, 0.63), 10, 50.0, 2.0, 0.4, true)
	boss.global_position = _dest
	boss.modulate.a = 1.0
	HitFx.burst(tree, _dest, Color(1.0, 0.0627, 0.94), 12, 60.0, 2.0, 0.4, true)
	if _mark != null:
		_mark.visible = false


func on_death() -> void:
	boss.modulate.a = 1.0
	if _mark != null:
		_mark.visible = false


func _exit_tree() -> void:
	if is_instance_valid(_mark):
		_mark.queue_free()
	if is_instance_valid(boss):
		boss.modulate.a = 1.0
