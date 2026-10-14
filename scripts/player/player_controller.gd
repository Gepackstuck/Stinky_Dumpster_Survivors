class_name PlayerController
extends CharacterBody2D
## Игрок: движение WASD/стрелками, здоровье, магнит для XP, перки, смерть.

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _camera: Camera2D = $Camera2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox
@onready var _magnet: Area2D = $Magnet
@onready var _magnet_collision: CollisionShape2D = $Magnet/CollisionShape2D

var _arena_max: Vector2 = Vector2.ZERO
var _regen_timer: float = 0.0


func _ready() -> void:
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
	_magnet.area_entered.connect(_on_magnet_area_entered)
	EventBus.perk_chosen.connect(_on_perk_chosen)
	_update_magnet_radius()
	_health.setup(Balance.PLAYER_MAX_HP)


func _physics_process(delta: float) -> void:
	var direction: Vector2 = Input.get_vector(&"move_left", &"move_right", &"move_up", &"move_down")
	velocity = direction * Balance.PLAYER_MOVE_SPEED * GameState.move_speed_mult
	if direction.x != 0.0:
		_sprite.flip_h = direction.x < 0.0
	move_and_slide()
	global_position = global_position.clamp(Vector2.ZERO, _arena_max)
	if GameState.regen_hp > 0.0:
		_regen_timer += delta
		if _regen_timer >= Balance.PERK_REGEN_INTERVAL_SEC:
			_regen_timer -= Balance.PERK_REGEN_INTERVAL_SEC
			_health.heal(GameState.regen_hp)


func _update_magnet_radius() -> void:
	var shape: CircleShape2D = _magnet_collision.shape as CircleShape2D
	shape.radius = Balance.PICKUP_RADIUS_BASE * GameState.pickup_radius_mult


func _on_magnet_area_entered(area: Area2D) -> void:
	if area is XpPickup:
		(area as XpPickup).attract(self)


func _on_perk_chosen(_perk_id: StringName) -> void:
	_update_magnet_radius()


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
