class_name TurretStructure
extends WeaponBase
## Турель из ведра: стоит на месте, поворачивается к врагу (8 направлений), перед выстрелом ствол набухает,
## снаряд вылетает из дула.

const TEXTURE: Texture2D = preload("res://assets/sprites/structure_turret.png")

var _sprite: Sprite2D = null
var _aim: int = 1            # 0=E, по часовой: SE, S, SW, W, NW, N, NE
var _charging: bool = false
var _kick: float = 0.0       # отдача после выстрела (0..1)
var _anim: float = 0.0


func _ready() -> void:
	super._ready()
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURE
	_sprite.hframes = 8
	_sprite.vframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_apply_frame()


func _physics_process(delta: float) -> void:
	_anim += delta
	var target: Node2D = _find_nearest_enemy()
	if target == null:
		_charging = false
	else:
		_aim = posmod(roundi(global_position.direction_to(target.global_position).angle() / (PI / 4.0)), 8)
		if not _charging and _cooldown_left <= 0.0:
			_charging = true
			_cooldown_left = Balance.TURRET_WINDUP_SEC   # замах: ствол набухает, потом выстрел
	_kick = maxf(_kick - delta * 6.0, 0.0)
	_apply_frame()
	super._physics_process(delta)


func _muzzle_offset() -> Vector2:
	return Vector2.from_angle(float(_aim) * PI / 4.0) * Balance.TURRET_MUZZLE_DIST


func _apply_frame() -> void:
	_sprite.frame_coords = Vector2i(_aim, 1 if _charging else 0)
	var swell: float = 1.0 + (0.06 * sin(_anim * 40.0) if _charging else 0.0)
	_sprite.scale = Vector2.ONE * swell
	_sprite.position = -_muzzle_offset().normalized() * 2.0 * _kick   # отдача назад


func _fire(target: Node2D) -> void:
	var saved: Vector2 = global_position
	var muzzle: Vector2 = saved + _muzzle_offset()
	global_position = muzzle   # снаряд стартует из дула
	super._fire(target)
	global_position = saved
	_charging = false
	_kick = 1.0
	HitFx.burst(get_tree(), muzzle, Color(0.968627, 1.0, 0.0), 4, 40.0, 2.0, 0.25, true)
