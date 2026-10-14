extends BossBrain
## Тележка-убийца: бежит как все, потом замирает, краснеет и рвётся рывком по прямой (как Charger в Brotato).

const WINDUP_SEC: float = 0.45
const DASH_SEC: float = 0.55
const DASH_SPEED: float = 260.0

var _cooldown: float = 0.0
var _windup_left: float = 0.0
var _dash_dir: Vector2 = Vector2.ZERO


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	super.setup(owner_enemy, player)
	_cooldown = randf_range(1.2, 3.0)


func physics_tick(delta: float) -> void:
	if _windup_left > 0.0:
		_windup_left -= delta
		boss.speed_mult = 0.0
		boss.flash(Color(1.0, 0.0, 0.2))
		if _windup_left <= 0.0:
			boss.forced_velocity = _dash_dir * DASH_SPEED
			boss.forced_sec = DASH_SEC
			boss.speed_mult = 1.0
			_cooldown = randf_range(2.5, 3.5)
		return
	if boss.forced_sec > 0.0:
		return
	_cooldown -= delta
	if _cooldown <= 0.0:
		_dash_dir = direction_to_target()
		_windup_left = WINDUP_SEC
