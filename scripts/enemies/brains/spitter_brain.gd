extends BossBrain
## Плюющийся: держит дистанцию и плюёт слюной (как Spitter в Brotato).

const SPIT: Texture2D = preload("res://assets/sprites/proj_spit.png")
const NEAR: float = 70.0
const FAR: float = 110.0
const SPIT_INTERVAL_SEC: float = 2.0
const SPIT_SPEED: float = 90.0
const SPIT_DAMAGE: float = 2.0

var _spit_left: float = 1.0


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	super.setup(owner_enemy, player)
	_spit_left = randf_range(0.5, SPIT_INTERVAL_SEC)


func physics_tick(delta: float) -> void:
	var dist: float = distance_to_target()
	if dist > FAR:
		boss.speed_mult = 1.0
		boss.extra_velocity = Vector2.ZERO
	elif dist < NEAR:
		boss.speed_mult = 0.0
		boss.extra_velocity = -direction_to_target() * 55.0
	else:
		boss.speed_mult = 0.0
		boss.extra_velocity = Vector2.ZERO
	_spit_left -= delta
	if _spit_left <= 0.0 and dist < FAR * 1.6:
		_spit_left = SPIT_INTERVAL_SEC
		shoot(SPIT, direction_to_target(), SPIT_DAMAGE * WaveRules.damage_mult(GameState.wave), SPIT_SPEED, 3.0, 4.0)
