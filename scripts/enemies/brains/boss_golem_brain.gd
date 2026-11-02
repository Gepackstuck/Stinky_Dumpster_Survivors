extends BossBrain
## Мусорный голем (финал): швыряет мешок туда, где герой (круг, потом жгучая лужа), бьёт кулаками в землю
## (круг + кольцо обломков), зовёт гопников из мусора. В ярости чаще.

const DEBRIS: Texture2D = preload("res://assets/sprites/proj_bottle.png")
const BAG: Texture2D = preload("res://assets/sprites/proj_tin_bomb.png")
const PUDDLE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const ROW_WALK: int = 0
const ROW_THROW: int = 1
const ROW_POUND: int = 2
const ROW_SUMMON: int = 3
const ROW_ENRAGE: int = 4

var _cooldown: float = 2.0


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
	_cooldown = Balance.GOLEM_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if _enraged() else 1.0)
	var roll: float = randf()
	var tree: SceneTree = boss.get_tree()
	if roll < 0.45:
		var spot: Vector2 = target.global_position
		var flight: float = boss.global_position.distance_to(spot) / Balance.GOLEM_BAG_SPEED
		Telegraph.circle(tree, spot, Balance.GOLEM_BAG_RADIUS, Balance.GOLEM_CAST_SEC + flight)
		start_cast(ROW_THROW, Balance.GOLEM_CAST_SEC, _throw.bind(spot))
	elif roll < 0.8:
		Telegraph.circle(tree, boss.global_position, Balance.GOLEM_POUND_RADIUS, Balance.GOLEM_CAST_SEC + 0.2, boss)
		start_cast(ROW_POUND, Balance.GOLEM_CAST_SEC + 0.2, _pound)
	else:
		start_cast(ROW_SUMMON, Balance.GOLEM_CAST_SEC, _summon)


func _throw(spot: Vector2) -> void:
	var distance: float = boss.global_position.distance_to(spot)
	shoot(BAG, boss.global_position.direction_to(spot), 0.0, Balance.GOLEM_BAG_SPEED, distance / Balance.GOLEM_BAG_SPEED, 5.0, PUDDLE)


func _pound() -> void:
	EventBus.shake_requested.emit(Balance.SHAKE_BOSS_SLAM)
	var at: Vector2 = boss.global_position
	if target.global_position.distance_to(at) <= Balance.GOLEM_POUND_RADIUS:
		var hb: HurtboxComponent = target.get_node_or_null(^"Hurtbox") as HurtboxComponent
		if hb != null and hb.receive_hit(Balance.GOLEM_POUND_DAMAGE * WaveRules.damage_mult(GameState.wave)):
			GameState.last_damage_source = boss.enemy_id
	for i: int in Balance.GOLEM_DEBRIS:
		var dir: Vector2 = Vector2.RIGHT.rotated(TAU * float(i) / float(Balance.GOLEM_DEBRIS))
		shoot(DEBRIS, dir, Balance.GOLEM_DEBRIS_DAMAGE, Balance.GOLEM_DEBRIS_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 8.0)
	HitFx.burst(boss.get_tree(), at, Color(0.4, 0.4, 0.45), 20, 110.0, 3.0, 0.5)


func _summon() -> void:
	for i: int in Balance.GOLEM_SUMMON:
		var at: Vector2 = boss.global_position + Vector2.from_angle(TAU * i / Balance.GOLEM_SUMMON) * 34.0
		EnemyBase.spawn_enemy.call_deferred(boss.get_parent(), target, &"squid_gopnik", at, WaveRules.hp_mult(GameState.wave) * 0.6)
