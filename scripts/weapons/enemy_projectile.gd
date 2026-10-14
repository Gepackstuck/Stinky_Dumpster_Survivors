class_name EnemyProjectile
extends Area2D
## Снаряд врага/босса: бьёт игрока (HurtboxComponent) или, если задан landing_hazard,
## долетает до точки и оставляет там зону урона. Берётся из PoolManager.

@onready var _sprite: Sprite2D = $Sprite2D

var _direction: Vector2 = Vector2.ZERO
var _speed: float = 0.0
var _damage: float = 0.0
var _life_left: float = 0.0
var _spin: float = 0.0
var _landing_hazard: PackedScene = null
var _active: bool = false
var source_id: StringName = &""


func _ready() -> void:
	area_entered.connect(_on_area_entered)


func launch(from: Vector2, direction: Vector2, damage: float, speed: float, lifetime_sec: float,
		texture: Texture2D, spin_rad: float = 0.0, landing_hazard: PackedScene = null) -> void:
	global_position = from
	_direction = direction
	_damage = damage
	_speed = speed
	_life_left = lifetime_sec
	_spin = spin_rad
	_landing_hazard = landing_hazard
	_sprite.texture = texture
	rotation = 0.0
	_active = true
	set_physics_process(true)


func _physics_process(delta: float) -> void:
	if not _active:
		return
	global_position += _direction * _speed * delta
	rotation += _spin * delta
	_life_left -= delta
	if _life_left <= 0.0:
		_finish(true)


func _on_area_entered(area: Area2D) -> void:
	if not _active or _damage <= 0.0:
		return
	if area is HurtboxComponent:
		if (area as HurtboxComponent).receive_hit(_damage):
			GameState.last_damage_source = source_id
		_finish(false)


func _finish(landed: bool) -> void:
	_active = false
	set_physics_process(false)
	if landed and _landing_hazard != null:
		_spawn_hazard.call_deferred(_landing_hazard, global_position, source_id)
	PoolManager.release(self)


static func _spawn_hazard(scene: PackedScene, at: Vector2, source: StringName = &"") -> void:
	var tree: SceneTree = Engine.get_main_loop() as SceneTree
	if tree == null or tree.current_scene == null:
		return
	var hazard: TimedHazard = scene.instantiate() as TimedHazard
	tree.current_scene.add_child(hazard)
	hazard.source_id = source
	hazard.setup(at, Balance.MINION_PUDDLE_RADIUS, Balance.MINION_PUDDLE_DAMAGE, Balance.MINION_PUDDLE_LIFETIME_SEC)
