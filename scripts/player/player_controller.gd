class_name PlayerController
extends CharacterBody2D
## Игрок: движение WASD/стрелками, здоровье, магнит для XP, перки, смерть.

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _animator: FrameAnimatorComponent = $FrameAnimator
@onready var _flash: HitFlashComponent = $HitFlash
@onready var _camera: Camera2D = $Camera2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox
@onready var _magnet: Area2D = $Magnet
@onready var _magnet_collision: CollisionShape2D = $Magnet/CollisionShape2D

var _arena_max: Vector2 = Vector2.ZERO
var _regen_timer: float = 0.0
var _shake: float = 0.0


func _ready() -> void:
	_arena_max = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	# Камера не показывает пространство за ареной.
	var border: int = int(Balance.ARENA_BORDER_THICKNESS)
	_camera.zoom = Vector2.ONE * Balance.CAMERA_ZOOM
	_camera.limit_left = -border
	_camera.limit_top = -border
	_camera.limit_right = int(Balance.ARENA_SIZE) + border
	_camera.limit_bottom = int(Balance.ARENA_SIZE) + border
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
		_sprite.flip_h = direction.x > 0.0
	_animator.active = direction != Vector2.ZERO
	if direction != Vector2.ZERO:
		# ряды листа: 0 — бок, 1 — вверх (спиной), 2 — вниз (лицом)
		if absf(direction.y) > absf(direction.x) + 0.01:
			_animator.row = 1 if direction.y < 0.0 else 2
			_sprite.flip_h = false
		else:
			_animator.row = 0
	move_and_slide()
	global_position = global_position.clamp(Vector2.ZERO, _arena_max)
	_update_shake(delta)
	if GameState.regen_hp > 0.0:
		_regen_timer += delta
		if _regen_timer >= Balance.PERK_REGEN_INTERVAL_SEC:
			_regen_timer -= Balance.PERK_REGEN_INTERVAL_SEC
			_health.heal(GameState.regen_hp)


func _update_shake(delta: float) -> void:
	if _shake <= 0.0:
		_camera.offset = Vector2.ZERO
		return
	_shake = maxf(_shake - Balance.SHAKE_DECAY * delta, 0.0)
	_camera.offset = Vector2(randf_range(-_shake, _shake), randf_range(-_shake, _shake)).round()


func _update_magnet_radius() -> void:
	var shape: CircleShape2D = _magnet_collision.shape as CircleShape2D
	shape.radius = Balance.PICKUP_RADIUS_BASE * GameState.pickup_radius_mult


func _on_magnet_area_entered(area: Area2D) -> void:
	if area is XpPickup:
		(area as XpPickup).attract(self)


func _on_perk_chosen(perk_id: StringName) -> void:
	_update_magnet_radius()
	_health.set_max(Balance.PLAYER_MAX_HP + GameState.bonus_max_hp)
	_add_weapon(perk_id)


## Оружия-перки: каждое — отдельный узел-автоатака на игроке.
func _add_weapon(perk_id: StringName) -> void:
	var weapon: Node2D = null
	match perk_id:
		PerkLibrary.W_LIGHTER:
			var lighter: WeaponBase = WeaponBase.new()
			lighter.weapon_id = &"lighter"
			weapon = lighter
		PerkLibrary.W_SOCK:
			var aura: AuraWeapon = AuraWeapon.new()
			aura.weapon_id = &"sock"
			weapon = aura
		PerkLibrary.W_SLINGSHOT:
			var sling: WeaponBase = WeaponBase.new()
			sling.weapon_id = &"slingshot"
			weapon = sling
		PerkLibrary.W_MOP:
			var mop: MeleeWeapon = MeleeWeapon.new()
			mop.weapon_id = &"mop"
			weapon = mop
	if weapon != null:
		add_child(weapon)


func _on_hurt(raw_damage: float) -> void:
	if randf() * 100.0 < GameState.dodge_percent:
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -12.0), "МИМО!", Color(0.0, 0.94, 1.0), 14.0, 0.7)
		return
	var reduced: float = raw_damage * Balance.ARMOR_K / (Balance.ARMOR_K + GameState.armor)
	var damage: float = maxf(minf(roundf(reduced), _health.max_health * Balance.PLAYER_MAX_HIT_FRACTION), 1.0)
	EventBus.player_hit.emit(damage)
	_flash.flash(Color(1.0, 0.0, 0.2))
	_shake = Balance.PLAYER_HIT_SHAKE
	# «пердим»: зелёное облако вонючих пикселей (без надписей)
	HitFx.burst(get_tree(), global_position + Vector2(0.0, 4.0), Color(0.2235, 1.0, 0.0784), 12, 60.0, 3.0, 0.7, true)
	HitFx.burst(get_tree(), global_position + Vector2(0.0, 4.0), Color(0.9686, 1.0, 0.0), 5, 45.0, 2.0, 0.7, true)
	_health.take_damage(damage)


func heal(amount: float) -> void:
	_health.heal(amount)


## Полное лечение между волнами (как в Brotato).
func heal_full() -> void:
	_health.heal(_health.max_health)


func _on_health_changed(current: float, maximum: float) -> void:
	GameState.hp = current
	_flash.set_outline_by_health(current / maxf(maximum, 1.0))
	GameState.max_hp = maximum


func _on_died() -> void:
	set_physics_process(false)
	hide()
	_hurtbox.set_deferred(&"monitorable", false)
	EventBus.player_died.emit()
