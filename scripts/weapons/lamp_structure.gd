extends AuraWeapon
## Лампа-вонялка: стоит на месте, коптит зелёным в радиусе: враги рядом получают урон и еле ползут.

const TEX: GDScript = preload("res://scripts/systems/tex.gd")

var _sprite: Sprite2D = null
var _anim: float = 0.0
var _slow_left: float = 0.0


func _ready() -> void:
	weapon_id = &"stink_lamp"
	super._ready()
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/structure_lamp.png")
	_sprite.hframes = 4
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_sprite.position = Vector2(0.0, -8.0)
	add_child(_sprite)


func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	_anim += delta
	_sprite.frame = int(_anim * 6.0) % 4
	_slow_left -= delta
	if _slow_left <= 0.0:
		_slow_left = 0.3
		var r_sq: float = _radius * _radius
		for node: Node in get_tree().get_nodes_in_group(&"enemies"):
			var enemy: EnemyBase = node as EnemyBase
			if enemy != null and global_position.distance_squared_to(enemy.global_position) <= r_sq:
				enemy.slow(Balance.LAMP_SLOW_FACTOR, 0.5)
