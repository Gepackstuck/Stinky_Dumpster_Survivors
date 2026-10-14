extends BossBrain
## Миньон-ебанат: дёргается из стороны в сторону, кидает гаечные ключи веером и лобит говно, оставляющее лужу.

const WRENCH: Texture2D = preload("res://assets/sprites/proj_wrench.png")
const POOP: Texture2D = preload("res://assets/sprites/proj_poop.png")
const PUDDLE_SCENE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
const WRENCH_FAN_COUNT: int = 3

var _wrench_cooldown: float = 1.0
var _poop_cooldown: float = 2.5
var _strafe_left: float = 0.0
var _strafe_sign: float = 0.0


func physics_tick(delta: float) -> void:
	_strafe_left -= delta
	if _strafe_left <= 0.0:
		_strafe_left = randf_range(0.4, 0.9)
		_strafe_sign = [-1.0, 0.0, 1.0][randi() % 3]
	boss.extra_velocity = direction_to_target().orthogonal() * _strafe_sign * Balance.MINION_STRAFE_SPEED
	_wrench_cooldown -= delta
	if _wrench_cooldown <= 0.0:
		_wrench_cooldown = Balance.MINION_WRENCH_INTERVAL_SEC
		_throw_wrenches()
	_poop_cooldown -= delta
	if _poop_cooldown <= 0.0:
		_poop_cooldown = Balance.MINION_POOP_INTERVAL_SEC
		_lob_poop()


func _throw_wrenches() -> void:
	var base: Vector2 = direction_to_target()
	for i: int in WRENCH_FAN_COUNT:
		var deg: float = (i - (WRENCH_FAN_COUNT - 1) * 0.5) * Balance.MINION_WRENCH_FAN_DEG
		shoot(WRENCH, base.rotated(deg_to_rad(deg)), Balance.MINION_WRENCH_DAMAGE,
				Balance.MINION_WRENCH_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, Balance.MINION_WRENCH_SPIN)


## Говно летит к точке, где игрок стоит сейчас, и там превращается в лужу.
func _lob_poop() -> void:
	var distance: float = distance_to_target()
	shoot(POOP, direction_to_target(), 0.0, Balance.MINION_POOP_SPEED,
			distance / Balance.MINION_POOP_SPEED, 6.0, PUDDLE_SCENE)
