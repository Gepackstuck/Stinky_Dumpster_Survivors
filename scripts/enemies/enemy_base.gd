class_name EnemyBase
extends CharacterBody2D
## Базовый враг: идёт к игроку, наносит урон при контакте (через Hitbox).
## Создаётся через PoolManager; после add_child() нужно вызвать setup().

@export var enemy_id: StringName = &"squid_gopnik"

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox
@onready var _hitbox: HitboxComponent = $Hitbox

var _target: Node2D = null
var _speed: float = 0.0
var _dead: bool = false


func _ready() -> void:
	_hurtbox.hurt.connect(_health.take_damage)
	_health.died.connect(_on_died)


## Инициализировать (или заново инициализировать при выдаче из пула).
func setup(target: Node2D, spawn_position: Vector2) -> void:
	var stats: Dictionary = Balance.ENEMIES[enemy_id]
	_speed = stats["speed"]
	_health.setup(stats["hp"])
	_hitbox.damage = stats["damage"]
	_target = target
	_dead = false
	global_position = spawn_position


func _physics_process(_delta: float) -> void:
	if _dead or not is_instance_valid(_target):
		return
	velocity = global_position.direction_to(_target.global_position) * _speed
	if velocity.x != 0.0:
		_sprite.flip_h = velocity.x < 0.0
	move_and_slide()
	_keep_distance_from_target()


## Мягкое расталкивание: враг не заходит внутрь игрока, а отъезжает — через толпу можно проломиться.
func _keep_distance_from_target() -> void:
	var offset: Vector2 = global_position - _target.global_position
	var distance: float = offset.length()
	if distance < Balance.ENEMY_PLAYER_MIN_DISTANCE and distance > 0.001:
		global_position += offset / distance * (Balance.ENEMY_PLAYER_MIN_DISTANCE - distance)


func _on_died() -> void:
	if _dead:
		return
	_dead = true
	EventBus.enemy_died.emit(enemy_id, global_position)
	PoolManager.release(self)
