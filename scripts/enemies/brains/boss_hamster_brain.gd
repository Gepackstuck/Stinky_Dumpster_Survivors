extends BossBrain
## Мега-хомяк: плюётся семечками веером, прыгает и давит пузом (кольцо семечек-ударная волна), катится шаром.
## В ярости (<50% HP) атакует чаще; ряд ярости — красные глаза, пар из ушей.

const SEED: Texture2D = preload("res://assets/sprites/proj_seed.png")
const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const FIRST_ATTACK_DELAY_SEC: float = 1.8
const SEED_FAN_COUNT: int = 5
# ряды листа enemy_boss_mega_hamster.png
const ROW_WALK: int = 0
const ROW_SPIT: int = 1
const ROW_SLAM: int = 2
const ROW_ROLL: int = 3
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
	_cooldown = Balance.HAMSTER_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if _enraged() else 1.0)
	var roll: float = randf()
	if roll < 0.4:
		start_cast(ROW_SPIT, Balance.HAMSTER_CAST_SEC, _spit)
	elif roll < 0.7:
		start_cast(ROW_SLAM, Balance.HAMSTER_CAST_SEC, _slam)
	else:
		boss.flash(Color(0.968627, 1.0, 0.0))
		start_cast(ROW_ROLL, Balance.HAMSTER_CAST_SEC, _roll, true, Balance.HAMSTER_ROLL_SEC)


func _spit() -> void:
	var base: Vector2 = direction_to_target()
	for i: int in SEED_FAN_COUNT:
		var deg: float = (i - (SEED_FAN_COUNT - 1) * 0.5) * Balance.HAMSTER_SEED_FAN_DEG * 0.5
		shoot(SEED, base.rotated(deg_to_rad(deg)), Balance.HAMSTER_SEED_DAMAGE, Balance.HAMSTER_SEED_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 8.0)


## Прыжок-раздавливание: ударная волна — кольцо семечек во все стороны.
func _slam() -> void:
	for i: int in Balance.HAMSTER_SLAM_SEEDS:
		var dir: Vector2 = Vector2.RIGHT.rotated(TAU * float(i) / float(Balance.HAMSTER_SLAM_SEEDS))
		shoot(SEED, dir, Balance.HAMSTER_SEED_DAMAGE, Balance.HAMSTER_SLAM_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 6.0)
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.7, 0.7, 0.75), 14, 90.0, 3.0, 0.5)


func _roll() -> void:
	boss.forced_velocity = direction_to_target() * Balance.HAMSTER_ROLL_SPEED
	boss.forced_sec = Balance.HAMSTER_ROLL_SEC
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.968627, 1.0, 0.0), 8, 80.0)
