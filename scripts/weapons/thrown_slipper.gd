class_name ThrownSlipper
extends Node2D
## Летящий тапок: по дуге в точку, на падении — удар по площади, кольцо и брызги.

const TEXTURE: Texture2D = preload("res://assets/sprites/proj_slipper.png")
const ARC_HEIGHT: float = 28.0
const RING_SEC: float = 0.3

var _from: Vector2 = Vector2.ZERO
var _to: Vector2 = Vector2.ZERO
var _damage: float = 0.0
var _radius: float = 40.0
var _flight: float = 0.5
var _t: float = 0.0
var _landed: bool = false
var _ring: float = 0.0
var _sprite: Sprite2D = null


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURE
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	z_index = 5


func launch(from: Vector2, to: Vector2, damage: float, radius: float, flight_sec: float) -> void:
	_from = from
	_to = to
	_damage = damage
	_radius = radius
	_flight = flight_sec
	global_position = from


func _physics_process(delta: float) -> void:
	if _landed:
		_ring += delta / RING_SEC
		queue_redraw()
		if _ring >= 1.0:
			queue_free()
		return
	_t += delta / _flight
	var k: float = minf(_t, 1.0)
	global_position = _from.lerp(_to, k)
	_sprite.position.y = -sin(k * PI) * ARC_HEIGHT
	_sprite.rotation = k * TAU * 2.0
	_sprite.frame = int(_t * 12.0) % 2
	if _t >= 1.0:
		_land()


func _land() -> void:
	_landed = true
	_sprite.position = Vector2.ZERO
	_sprite.hide()
	var radius_sq: float = _radius * _radius
	for group: StringName in [&"enemies", &"neutrals"]:
		for node: Node in get_tree().get_nodes_in_group(group):
			var enemy: EnemyBase = node as EnemyBase
			if enemy != null and global_position.distance_squared_to(enemy.global_position) <= radius_sq:
				enemy.hit_by_weapon(_damage, (enemy.global_position - global_position).normalized() * 120.0)
	HitFx.burst(get_tree(), global_position, Color(0.58, 0.34, 0.12), 12, _radius * 2.0, 3.0, 0.5, true)
	HitFx.burst(get_tree(), global_position, Color(0.2235, 1.0, 0.0784), 8, _radius * 1.5, 2.0, 0.5, true)
	queue_redraw()


func _draw() -> void:
	if not _landed:
		return
	var a: float = 1.0 - _ring
	draw_arc(Vector2.ZERO, _radius * minf(_ring * 1.5, 1.0), 0.0, TAU, 28, Color(0.58, 0.34, 0.12, a), 2.0)
	draw_arc(Vector2.ZERO, _radius * minf(_ring * 1.2, 1.0), 0.0, TAU, 28, Color(1.0, 0.0627, 0.94, a * 0.7), 1.0)
