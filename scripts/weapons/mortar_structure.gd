extends SlipperWeapon
## Тележка-миномёт: стоит на месте и навесом закидывает врагов банками (удар по площади, далеко).

var _sprite: Sprite2D = null
var _flash: float = 0.0


func _ready() -> void:
	weapon_id = &"cart_mortar"
	super._ready()
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/structure_mortar.png")
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_sprite.position = Vector2(0.0, -4.0)
	add_child(_sprite)


func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	_flash = maxf(_flash - delta * 4.0, 0.0)
	_sprite.frame = 1 if _flash > 0.0 else 0


func _fire(target: Node2D) -> void:
	_flash = 1.0
	super._fire(target)
