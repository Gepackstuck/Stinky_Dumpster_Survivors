class_name HeldWeapon
extends Node2D
## Оружие в руках героя: значок крутится вокруг тела (у каждого слота своё место), смотрит в сторону цели
## и показывает атаку: ствол отдаёт назад, швабра машет, носок трясётся. Висит ребёнком узла оружия.

const RING_X: float = 19.0
const RING_Y: float = 13.0
const BIG_COUNT: int = 3            # до стольких оружий значки в натуральную величину, дальше вдвое меньше
const FIRST_ANGLE: float = 0.6      # первое оружие у правой руки, остальные по кругу
const KICK_DECAY: float = 6.0
const RECOIL_PX: float = 3.0
const SWING_RAD: float = 1.3

var slot_index: int = 0
var slot_count: int = 1

var _sprite: Sprite2D
var _weapon_id: StringName = &""
var _aim: Vector2 = Vector2.RIGHT
var _kick: float = 0.0


func _ready() -> void:
	_weapon_id = get_parent().weapon_id
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/ui/perk_w_%s.png" % _weapon_id) as Texture2D
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	if get_parent().has_signal(&"fired"):
		get_parent().connect(&"fired", _on_fired)
	_place(0.0)


func _on_fired(direction: Vector2) -> void:
	if direction != Vector2.ZERO:
		_aim = direction
	_kick = 1.0


func _process(delta: float) -> void:
	_kick = maxf(_kick - delta * KICK_DECAY, 0.0)
	_place(delta)


func _place(_delta: float) -> void:
	var angle: float = FIRST_ANGLE + TAU * float(slot_index) / float(maxi(slot_count, 1))
	var home: Vector2 = Vector2(cos(angle) * RING_X, sin(angle) * RING_Y)
	var side: float = -1.0 if _aim.x < 0.0 else 1.0
	_sprite.flip_h = _aim.x < 0.0
	var offset: Vector2 = Vector2.ZERO
	var base_scale: float = 1.0 if slot_count <= BIG_COUNT else 0.5
	_sprite.rotation = 0.0
	_sprite.scale = Vector2.ONE * base_scale
	match _weapon_id:
		&"mop":
			_sprite.rotation = side * (-0.6 + SWING_RAD * sin(_kick * PI))   # взмах
			offset = _aim * 3.0 * _kick
		&"sock":
			_sprite.scale = Vector2.ONE * base_scale * (1.0 + 0.4 * _kick)                  # раздувается при вони
			offset = Vector2(roundf(sin(_kick * 40.0)) * 1.0, 0.0)
		_:
			offset = -_aim * RECOIL_PX * _kick                                  # отдача
	_sprite.position = (home + offset).round()
