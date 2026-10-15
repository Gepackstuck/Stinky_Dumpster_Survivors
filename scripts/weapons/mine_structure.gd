extends Node2D
## Мина из крышек: лежит на земле и мигает; враг наступил - бабах по площади.

const TEX: GDScript = preload("res://scripts/systems/tex.gd")
const THROWN: GDScript = preload("res://scripts/weapons/thrown_slipper.gd")

var _sprite: Sprite2D = null
var _anim: float = 0.0
var _armed: bool = true


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/structure_mine.png")
	_sprite.hframes = 4
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_anim = randf()


func _physics_process(delta: float) -> void:
	if not _armed:
		return
	_anim += delta
	_sprite.frame = int(_anim * 4.0) % 4
	var trigger_sq: float = Balance.MINE_TRIGGER_DIST * Balance.MINE_TRIGGER_DIST
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		if enemy != null and global_position.distance_squared_to(enemy.global_position) <= trigger_sq:
			_explode()
			return


func _explode() -> void:
	_armed = false
	var boom: Node2D = THROWN.new()
	get_tree().current_scene.add_child(boom)
	boom.call(&"launch", global_position, global_position, Balance.MINE_DAMAGE * GameState.damage_mult, Balance.MINE_RADIUS, 0.02)
	HitFx.burst(get_tree(), global_position, Color(1.0, 0.47, 0.0), 14, 100.0, 3.0, 0.4, true)
	queue_free()
