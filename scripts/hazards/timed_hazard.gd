class_name TimedHazard
extends HitboxComponent
## Зона урона на время (облако пердежа, лужа говна). Бьёт игрока, пока он внутри; потом тает.
## После add_child() вызвать setup().

@onready var _shape: CollisionShape2D = $CollisionShape2D
@onready var _sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	super()
	_shape.shape = _shape.shape.duplicate()


func setup(at: Vector2, radius: float, hazard_damage: float, lifetime_sec: float) -> void:
	global_position = at
	damage = hazard_damage
	(_shape.shape as CircleShape2D).radius = radius
	var tween: Tween = create_tween()
	tween.tween_interval(maxf(lifetime_sec - 0.5, 0.1))
	tween.tween_property(_sprite, "modulate:a", 0.0, 0.5)
	tween.tween_callback(queue_free)
