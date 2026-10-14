class_name PlayerController
extends CharacterBody2D
## Игрок: движение WASD/стрелками, здоровье, смерть.

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _camera: Camera2D = $Camera2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox

var _arena_max: Vector2 = Vector2.ZERO


func _ready() -> void:
	_sprite.texture = PlaceholderSprites.player()
	_arena_max = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	# Камера не показывает пространство за ареной.
	_camera.limit_left = 0
	_camera.limit_top = 0
	_camera.limit_right = int(Balance.ARENA_SIZE)
	_camera.limit_bottom = int(Balance.ARENA_SIZE)
	_hurtbox.invulnerability_sec = Balance.PLAYER_HURT_COOLDOWN_SEC
	_hurtbox.hurt.connect(_on_hurt)
	_health.health_changed.connect(_on_health_changed)
	_health.died.connect(_on_died)
	_health.setup(Balance.PLAYER_MAX_HP)


func _physics_process(_delta: float) -> void:
	var direction: Vector2 = Input.get_vector(&"move_left", &"move_right", &"move_up", &"move_down")
	velocity = direction * Balance.PLAYER_MOVE_SPEED
	move_and_slide()
	global_position = global_position.clamp(Vector2.ZERO, _arena_max)


func _on_hurt(damage: float) -> void:
	EventBus.player_hit.emit(damage)
	_health.take_damage(damage)


func _on_health_changed(current: float, maximum: float) -> void:
	GameState.hp = current
	GameState.max_hp = maximum


func _on_died() -> void:
	set_physics_process(false)
	hide()
	_hurtbox.set_deferred(&"monitorable", false)
	EventBus.player_died.emit()
