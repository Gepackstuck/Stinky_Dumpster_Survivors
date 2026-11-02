extends BossBrain
## Синий кит (финальный босс): рыдает веером слёз (конус), прыгает и плюхается туда, где стоял герой
## (круг на земле, потом кольцо брызг), выпускает фонтаны из-под земли рядом с героем (три круга).
## В ярости (<50% HP) чаще, слёз больше.

const TEAR: Texture2D = preload("res://assets/sprites/proj_milk.png")
const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const FIRST_ATTACK_DELAY_SEC: float = 2.0
# ряды листа enemy_boss_blue_whale.png
const ROW_WALK: int = 0
const ROW_TEARS: int = 1
const ROW_FLOP: int = 2
const ROW_SPOUT: int = 3
const ROW_ENRAGE: int = 4

var _cooldown: float = FIRST_ATTACK_DELAY_SEC


func _enraged() -> bool:
	return boss.health_fraction() < ENRAGE_HP_FRACTION


func idle_row() -> int:
	return ROW_ENRAGE if _enraged() else ROW_WALK


func physics_tick(delta: float) -> void:
	if tick_cast(delta):
		return
	boss.speed_mult = 1.0
	_cooldown -= delta
	if _cooldown > 0.0:
		return
	_cooldown = Balance.WHALE_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if _enraged() else 1.0)
	var roll: float = randf()
	var tree: SceneTree = boss.get_tree()
	if roll < 0.4:
		var aim: Vector2 = direction_to_target()
		Telegraph.cone(tree, boss.global_position, aim, Balance.WHALE_TEAR_FAN_DEG + 4.0, Balance.TELEGRAPH_SHOT_LENGTH, Balance.WHALE_CAST_SEC, boss)
		start_cast(ROW_TEARS, Balance.WHALE_CAST_SEC, _tears.bind(aim))
	elif roll < 0.7:
		var spot: Vector2 = target.global_position
		Telegraph.circle(tree, spot, Balance.WHALE_FLOP_RADIUS, Balance.WHALE_CAST_SEC + Balance.WHALE_FLOP_SEC)
		start_cast(ROW_FLOP, Balance.WHALE_CAST_SEC, _flop.bind(spot), true, Balance.WHALE_FLOP_SEC)
	else:
		var spots: Array[Vector2] = []
		for i: int in Balance.WHALE_SPOUTS:
			spots.append(target.global_position + Vector2.from_angle(randf() * TAU) * randf_range(0.0, 50.0))
		for s: Vector2 in spots:
			Telegraph.circle(tree, s, Balance.WHALE_SPOUT_RADIUS, Balance.WHALE_CAST_SEC + 0.3)
		start_cast(ROW_SPOUT, Balance.WHALE_CAST_SEC + 0.3, _spouts.bind(spots))


func _tears(base: Vector2) -> void:
	var count: int = Balance.WHALE_TEAR_COUNT + (2 if _enraged() else 0)
	for i: int in count:
		var deg: float = (i - (count - 1) * 0.5) * (Balance.WHALE_TEAR_FAN_DEG * 2.0 / float(maxi(count - 1, 1)))
		shoot(TEAR, base.rotated(deg_to_rad(deg)), Balance.WHALE_TEAR_DAMAGE, Balance.WHALE_TEAR_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 0.0)


func _flop(spot: Vector2) -> void:
	boss.forced_velocity = (spot - boss.global_position) / Balance.WHALE_FLOP_SEC
	boss.forced_sec = Balance.WHALE_FLOP_SEC
	boss.get_tree().create_timer(Balance.WHALE_FLOP_SEC, false).timeout.connect(func() -> void:
		if not is_instance_valid(boss) or not boss.is_alive():
			return
		_hit_player_at(spot, Balance.WHALE_FLOP_RADIUS, Balance.WHALE_FLOP_DAMAGE)
		EventBus.shake_requested.emit(Balance.SHAKE_BOSS_SLAM)
		for i: int in Balance.WHALE_FLOP_RING:
			var dir: Vector2 = Vector2.RIGHT.rotated(TAU * float(i) / float(Balance.WHALE_FLOP_RING))
			shoot(TEAR, dir, Balance.WHALE_TEAR_DAMAGE, Balance.WHALE_TEAR_SPEED * 0.8, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 0.0)
		HitFx.burst(boss.get_tree(), spot, Color(0.0, 0.94, 1.0), 20, 100.0, 3.0, 0.5))


func _spouts(spots: Array[Vector2]) -> void:
	for s: Vector2 in spots:
		_hit_player_at(s, Balance.WHALE_SPOUT_RADIUS, Balance.WHALE_SPOUT_DAMAGE)
		HitFx.burst(boss.get_tree(), s, Color(0.0, 0.94, 1.0), 14, 60.0, 3.0, 0.6, true)
		HitFx.burst(boss.get_tree(), s + Vector2(0.0, -10.0), Color(1.0, 1.0, 1.0), 6, 40.0, 2.0, 0.4, true)


func _hit_player_at(at: Vector2, radius: float, damage: float) -> void:
	if target.global_position.distance_to(at) > radius:
		return
	var hb: HurtboxComponent = target.get_node_or_null(^"Hurtbox") as HurtboxComponent
	if hb != null and hb.receive_hit(damage):
		GameState.last_damage_source = boss.enemy_id
