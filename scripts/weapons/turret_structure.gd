class_name TurretStructure
extends WeaponBase
## Турель из ведра: стоит на месте и стреляет по ближайшему врагу (стрельба — из WeaponBase).

const TEXTURE: Texture2D = preload("res://assets/sprites/structure_turret.png")

var _sprite: Sprite2D = null
var _anim: float = 0.0


func _ready() -> void:
	super._ready()
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURE
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)


func _physics_process(delta: float) -> void:
	_anim += delta
	_sprite.frame = int(_anim * 3.0) % 2
	super._physics_process(delta)
