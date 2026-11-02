extends BossBrain
## Королева крыс (элита): визжит и зовёт стаю тараканов, таранит по прямой (дорожка-предупреждение),
## бьёт хвостом по кругу (круг-предупреждение). В ярости (<50% HP) чаще и стая больше.

const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const FIRST_ATTACK_DELAY_SEC: float = 1.8
# ряды листа enemy_boss_rat_queen.png
const ROW_WALK: int = 0
const ROW_SUMMON: int = 1
const ROW_CHARGE: int = 2
const ROW_TAIL: int = 3
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
	_cooldown = Balance.RAT_QUEEN_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if _enraged() else 1.0)
	var roll: float = randf()
	var tree: SceneTree = boss.get_tree()
	if roll < 0.35:
		start_cast(ROW_SUMMON, Balance.RAT_QUEEN_CAST_SEC, _summon)
	elif roll < 0.7:
		var aim: Vector2 = direction_to_target()
		boss.flash(Color(1.0, 0.0, 0.2))
		Telegraph.line(tree, boss.global_position, aim, Balance.RAT_QUEEN_CHARGE_SPEED * Balance.RAT_QUEEN_CHARGE_SEC, float(Balance.ENEMIES[boss.enemy_id]["radius"]) * 0.8, Balance.RAT_QUEEN_CAST_SEC + 0.2, boss)
		start_cast(ROW_CHARGE, Balance.RAT_QUEEN_CAST_SEC + 0.2, _charge.bind(aim), true, Balance.RAT_QUEEN_CHARGE_SEC)
	else:
		Telegraph.circle(tree, boss.global_position, Balance.RAT_QUEEN_TAIL_RADIUS, Balance.RAT_QUEEN_CAST_SEC, boss)
		start_cast(ROW_TAIL, Balance.RAT_QUEEN_CAST_SEC, _tail)


func _summon() -> void:
	var count: int = Balance.RAT_QUEEN_SUMMON + (2 if _enraged() else 0)
	for i: int in count:
		var at: Vector2 = boss.global_position + Vector2.from_angle(TAU * i / count) * 26.0
		EnemyBase.spawn_enemy.call_deferred(boss.get_parent(), target, &"cockroach", at, WaveRules.hp_mult(GameState.wave) * 0.5)
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.6, 0.6, 0.7), 14, 70.0, 3.0, 0.5)


func _charge(aim: Vector2) -> void:
	boss.forced_velocity = aim * Balance.RAT_QUEEN_CHARGE_SPEED
	boss.forced_sec = Balance.RAT_QUEEN_CHARGE_SEC


func _tail() -> void:
	var at: Vector2 = boss.global_position
	if target.global_position.distance_to(at) <= Balance.RAT_QUEEN_TAIL_RADIUS:
		var hb: HurtboxComponent = target.get_node_or_null(^"Hurtbox") as HurtboxComponent
		if hb != null and hb.receive_hit(Balance.RAT_QUEEN_TAIL_DAMAGE * WaveRules.damage_mult(GameState.wave)):
			GameState.last_damage_source = boss.enemy_id
	HitFx.burst(boss.get_tree(), at, Color(1.0, 0.3, 0.8), 18, Balance.RAT_QUEEN_TAIL_RADIUS * 2.0, 3.0, 0.4)
