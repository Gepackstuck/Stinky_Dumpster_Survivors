extends BossBrain
## Таракан-качок (элита): тройной рывок (каждый с дорожкой-предупреждением), кладка яиц (вылупляются тараканы),
## топот (круг вокруг). В ярости (<50% HP) чаще.

const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const ROW_WALK: int = 0
const ROW_DASH: int = 1
const ROW_EGGS: int = 2
const ROW_STOMP: int = 3
const ROW_ENRAGE: int = 4

var _cooldown: float = 1.8
var _dashes_left: int = 0


func _enraged() -> bool:
	return boss.health_fraction() < ENRAGE_HP_FRACTION


func idle_row() -> int:
	return ROW_ENRAGE if _enraged() else ROW_WALK


func physics_tick(delta: float) -> void:
	if tick_cast(delta) or boss.forced_sec > 0.0:
		return
	if _dashes_left > 0:   # серия рывков: следующий сразу
		_dashes_left -= 1
		_queue_dash()
		return
	boss.speed_mult = 1.0
	_cooldown -= delta
	if _cooldown > 0.0:
		return
	_cooldown = Balance.ROACH_KING_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if _enraged() else 1.0)
	var roll: float = randf()
	if roll < 0.45:
		_dashes_left = Balance.ROACH_KING_DASHES - 1
		_queue_dash()
	elif roll < 0.7:
		start_cast(ROW_EGGS, Balance.ROACH_KING_CAST_SEC, _lay_eggs)
	else:
		Telegraph.circle(boss.get_tree(), boss.global_position, Balance.ROACH_KING_STOMP_RADIUS, Balance.ROACH_KING_CAST_SEC, boss)
		start_cast(ROW_STOMP, Balance.ROACH_KING_CAST_SEC, _stomp)


func _queue_dash() -> void:
	var aim: Vector2 = direction_to_target()
	Telegraph.line(boss.get_tree(), boss.global_position, aim, Balance.ROACH_KING_DASH_SPEED * Balance.ROACH_KING_DASH_SEC, 16.0, Balance.ROACH_KING_DASH_WINDUP, boss)
	start_cast(ROW_DASH, Balance.ROACH_KING_DASH_WINDUP, func() -> void:
		boss.forced_velocity = aim * Balance.ROACH_KING_DASH_SPEED
		boss.forced_sec = Balance.ROACH_KING_DASH_SEC, true, Balance.ROACH_KING_DASH_SEC)


func _lay_eggs() -> void:
	for i: int in Balance.ROACH_KING_EGGS:
		var at: Vector2 = boss.global_position + Vector2.from_angle(TAU * i / Balance.ROACH_KING_EGGS) * 24.0
		EnemyBase.spawn_enemy.call_deferred(boss.get_parent(), target, &"egg", at, WaveRules.hp_mult(GameState.wave) * 0.5)


func _stomp() -> void:
	EventBus.shake_requested.emit(Balance.SHAKE_BOSS_SLAM)
	if target.global_position.distance_to(boss.global_position) <= Balance.ROACH_KING_STOMP_RADIUS:
		var hb: HurtboxComponent = target.get_node_or_null(^"Hurtbox") as HurtboxComponent
		if hb != null and hb.receive_hit(Balance.ROACH_KING_STOMP_DAMAGE * WaveRules.damage_mult(GameState.wave)):
			GameState.last_damage_source = boss.enemy_id
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.75, 0.6, 0.4), 18, 100.0, 3.0, 0.4)
