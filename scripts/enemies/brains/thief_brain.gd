extends BossBrain
## Н21: щипач. Не дерётся - бегает по полю и тырит упавшую слизь-опыт (то есть твоё говно), пока мешок не полон
## или не вышло время; потом удирает к краю арены. Убил - мешок лопается, всё сворованное ×2. Ушёл - пропало.

var _stolen: int = 0
var _left: float = 0.0
var _fleeing: bool = false
var _goal: Node2D = null


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	super.setup(owner_enemy, player)
	_stolen = 0
	_left = Balance.THIEF_STEAL_SEC
	_fleeing = false
	_goal = null


func physics_tick(delta: float) -> void:
	_left -= delta
	if not _fleeing and (_left <= 0.0 or _stolen >= Balance.THIEF_MAX_STEAL):
		_fleeing = true
		HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -18.0), TranslationServer.translate("СВАЛИВАЮ!"), Color(1.0, 0.6, 0.1))
	var speed: float = float(Balance.ENEMIES[&"thief"]["speed"]) * WaveRules.speed_mult(GameState.wave)
	if _fleeing:
		var exit: Vector2 = _nearest_edge()
		boss.forced_velocity = boss.global_position.direction_to(exit) * speed * 1.3
		boss.forced_sec = 0.12
		if boss.global_position.distance_to(exit) < 8.0:
			HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -18.0), TranslationServer.translate("УНЁС %d!") % _stolen, Color(1.0, 0.2, 0.2), 16.0, 1.2)
			boss.vanish()
		return
	if not is_instance_valid(_goal) or not _goal.is_inside_tree() or not _goal.visible:
		_goal = _nearest_pickup()
	if _goal == null:
		boss.forced_velocity = -direction_to_target() * speed * 0.6   # добра нет - держится подальше от героя
		boss.forced_sec = 0.12
		return
	boss.forced_velocity = boss.global_position.direction_to(_goal.global_position) * speed
	boss.forced_sec = 0.12
	if boss.global_position.distance_to(_goal.global_position) < 8.0 and (_goal as XpPickup) != null:
		var p: XpPickup = _goal as XpPickup
		_stolen += p.amount()
		p.set_physics_process(false)
		PoolManager.release(p)
		_goal = null
		HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -14.0), TranslationServer.translate("СТЫРИЛ!"), Color(0.6, 1.0, 0.3), 10.0, 0.5)


func _nearest_pickup() -> Node2D:
	var best: Node2D = null
	var best_d: float = Balance.THIEF_SEE_RADIUS
	for n: Node in boss.get_tree().get_nodes_in_group(&"pickups"):
		var p: XpPickup = n as XpPickup
		if p == null or not p.is_inside_tree() or p.is_physics_processing():
			continue   # уже летит к герою - не успеет
		var d: float = p.global_position.distance_to(boss.global_position)
		if d < best_d:
			best_d = d
			best = p
	return best


func _nearest_edge() -> Vector2:
	var pos: Vector2 = boss.global_position
	var a: float = Balance.ARENA_SIZE
	var options: Array[Vector2] = [Vector2(0.0, pos.y), Vector2(a, pos.y), Vector2(pos.x, 0.0), Vector2(pos.x, a)]
	var best: Vector2 = options[0]
	for o: Vector2 in options:
		if o.distance_to(pos) < best.distance_to(pos):
			best = o
	return best


func on_death() -> void:
	if _stolen <= 0:
		return
	var total: int = _stolen * 2
	var tree: SceneTree = boss.get_tree()
	HitFx.popup(tree, boss.global_position + Vector2(0.0, -18.0), TranslationServer.translate("МЕШОК ЛОПНУЛ! x2"), Color(0.97, 1.0, 0.0), 16.0, 1.0, true)
	var parts: int = mini(total, 8)
	for i: int in parts:
		EventBus.xp_drop_requested.emit(boss.global_position, total / parts + (1 if i < total % parts else 0))
	if total >= 20:
		Achievements.unlock(&"thief_caught")
