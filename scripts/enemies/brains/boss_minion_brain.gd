extends BossBrain
## Миньон-псих: дёргается из стороны в сторону, кидает гаечные ключи веером и лобит говно, оставляющее лужу.
## В ярости (<50% HP) быстрее стреляет и крутит булаву вихрем: кольцо ключей во все стороны.

const WRENCH: Texture2D = preload("res://assets/sprites/proj_wrench.png")
const POOP: Texture2D = preload("res://assets/sprites/proj_poop.png")
const PUDDLE_SCENE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
const WRENCH_FAN_COUNT: int = 3
const ENRAGE_HP_FRACTION: float = 0.5
# ряды листа enemy_boss_minion.png
const ROW_WALK: int = 0
const ROW_WRENCH: int = 1
const ROW_POOP: int = 2
const ROW_RAGE: int = 3
const ROW_WHIRL: int = 4

var _wrench_cooldown: float = 1.0
var _poop_cooldown: float = 2.5
var _whirl_cooldown: float = Balance.MINION_WHIRL_INTERVAL_SEC
var _strafe_left: float = 0.0
var _strafe_sign: float = 0.0


func _enraged() -> bool:
	return boss.health_fraction() < ENRAGE_HP_FRACTION


func idle_row() -> int:
	return ROW_RAGE if _enraged() else ROW_WALK


func physics_tick(delta: float) -> void:
	_strafe_left -= delta
	if _strafe_left <= 0.0:
		_strafe_left = randf_range(0.4, 0.9)
		_strafe_sign = [-1.0, 0.0, 1.0][randi() % 3]
	boss.extra_velocity = direction_to_target().orthogonal() * _strafe_sign * Balance.MINION_STRAFE_SPEED
	if tick_cast(delta):
		return   # занят замахом: таймеры других атак ждут
	var mult: float = Balance.MINION_ENRAGE_MULT if _enraged() else 1.0
	_wrench_cooldown -= delta
	_poop_cooldown -= delta
	_whirl_cooldown -= delta
	if _enraged() and _whirl_cooldown <= 0.0:
		_whirl_cooldown = Balance.MINION_WHIRL_INTERVAL_SEC
		start_cast(ROW_WHIRL, Balance.MINION_CAST_SEC, _whirl, false)
	elif _wrench_cooldown <= 0.0:
		_wrench_cooldown = Balance.MINION_WRENCH_INTERVAL_SEC * mult
		start_cast(ROW_WRENCH, Balance.MINION_CAST_SEC, _throw_wrenches, false)
	elif _poop_cooldown <= 0.0:
		_poop_cooldown = Balance.MINION_POOP_INTERVAL_SEC * mult
		start_cast(ROW_POOP, Balance.MINION_CAST_SEC, _lob_poop, false)


func _throw_wrenches() -> void:
	var base: Vector2 = direction_to_target()
	for i: int in WRENCH_FAN_COUNT:
		var deg: float = (i - (WRENCH_FAN_COUNT - 1) * 0.5) * Balance.MINION_WRENCH_FAN_DEG
		shoot(WRENCH, base.rotated(deg_to_rad(deg)), Balance.MINION_WRENCH_DAMAGE,
				Balance.MINION_WRENCH_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, Balance.MINION_WRENCH_SPIN)


## Вихрь булавой: ключи разлетаются кольцом.
func _whirl() -> void:
	for i: int in Balance.MINION_WHIRL_WRENCHES:
		var dir: Vector2 = Vector2.RIGHT.rotated(TAU * float(i) / float(Balance.MINION_WHIRL_WRENCHES))
		shoot(WRENCH, dir, Balance.MINION_WRENCH_DAMAGE, Balance.MINION_WRENCH_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, Balance.MINION_WRENCH_SPIN)
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.968627, 1.0, 0.0), 10, 90.0)


## Говно летит к точке, где игрок стоит сейчас, и там превращается в лужу.
func _lob_poop() -> void:
	var distance: float = distance_to_target()
	shoot(POOP, direction_to_target(), 0.0, Balance.MINION_POOP_SPEED,
			distance / Balance.MINION_POOP_SPEED, 6.0, PUDDLE_SCENE)
