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
var _still_time: float = 0.0
var _still_timer: float = 0.0


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
	EventBus.weapons_changed.connect(_sync_weapons)
	EventBus.enemy_died.connect(_on_enemy_died_item_fx)
	EventBus.wave_started.connect(_on_wave_started_items)
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
	_update_still_regen(delta, direction == Vector2.ZERO)
	if GameState.regen_hp > 0.0:
		_regen_timer += delta
		if _regen_timer >= Balance.PERK_REGEN_INTERVAL_SEC:
			_regen_timer -= Balance.PERK_REGEN_INTERVAL_SEC
			_health.heal(GameState.regen_hp)


func _on_wave_started_items(_wave: int) -> void:
	GameState.block_charges = GameState.block_count


## «Грязный бинт»: пока стоишь на месте, лечит чуть сильнее.
func _update_still_regen(delta: float, standing: bool) -> void:
	if GameState.still_regen <= 0.0 or not GameState.run_active:
		return
	if not standing:
		_still_time = 0.0
		_still_timer = 0.0
		return
	_still_time += delta
	if _still_time < Balance.ITEM_STILL_WAIT_SEC:
		return
	_still_timer += delta
	if _still_timer >= Balance.ITEM_STILL_REGEN_SEC:
		_still_timer = 0.0
		_health.heal(GameState.still_regen)
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -12.0), "+%d ХП" % int(GameState.still_regen), Color(0.2235, 1.0, 0.0784), 12.0, 0.5)


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


func _on_perk_chosen(_perk_id: StringName) -> void:
	_update_magnet_radius()
	_health.set_max(maxf(Balance.PLAYER_MAX_HP + GameState.bonus_max_hp, 10.0))


## Оружие игрока: каждое — отдельный узел-автоатака, пересобираем при любом изменении набора.
func _sync_weapons() -> void:
	for node: Node in get_tree().get_nodes_in_group(&"weapon_nodes"):
		node.queue_free()
	for entry: Dictionary in GameState.weapons:
		var weapon: Node2D = null
		match entry["id"]:
			&"laser_pointer":
				var laser: LaserWeapon = LaserWeapon.new()
				laser.weapon_id = &"laser_pointer"
				laser.tier = entry["tier"]
				weapon = laser
			&"slipper":
				var slipper: SlipperWeapon = SlipperWeapon.new()
				slipper.weapon_id = &"slipper"
				slipper.tier = entry["tier"]
				weapon = slipper
			&"lighter", &"slingshot", &"condensed_milk":
				var shooter: WeaponBase = WeaponBase.new()
				shooter.weapon_id = entry["id"]
				shooter.tier = entry["tier"]
				weapon = shooter
			&"sock":
				var aura: AuraWeapon = AuraWeapon.new()
				aura.weapon_id = &"sock"
				aura.tier = entry["tier"]
				weapon = aura
			&"mop":
				var mop: MeleeWeapon = MeleeWeapon.new()
				mop.weapon_id = &"mop"
				mop.tier = entry["tier"]
				weapon = mop
		if weapon != null:
			weapon.add_to_group(&"weapon_nodes")
			add_child(weapon)


func _on_hurt(raw_damage: float) -> void:
	if randf() * 100.0 < GameState.dodge_percent:
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -12.0), "МИМО!", Color(0.0, 0.94, 1.0), 14.0, 0.7)
		return
	if GameState.block_charges > 0:
		GameState.block_charges -= 1
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -12.0), "КАСКА!", Color(1.0, 1.0, 0.0), 14.0, 0.8)
		HitFx.burst(get_tree(), global_position, Color(1.0, 1.0, 0.0), 8, 50.0, 2.0, 0.4, true)
		return
	if randf() * 100.0 < GameState.repel_percent:
		_stink_repel()
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
	if GameState.thorns_damage > 0.0:
		_thorns_hit()


## «Обосранные портки»: вонь сдувает врагов вокруг, урон по тебе не проходит.
func _stink_repel() -> void:
	HitFx.popup(get_tree(), global_position + Vector2(0.0, -12.0), "ВОНЬ!", Color(0.2235, 1.0, 0.0784), 14.0, 0.8)
	HitFx.burst(get_tree(), global_position, Color(0.2235, 1.0, 0.0784), 18, Balance.ITEM_REPEL_RADIUS * 1.6, 3.0, 0.8, true)
	var radius_sq: float = Balance.ITEM_REPEL_RADIUS * Balance.ITEM_REPEL_RADIUS
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and global_position.distance_squared_to(enemy.global_position) <= radius_sq:
			enemy.shove((enemy.global_position - global_position).normalized() * Balance.ITEM_REPEL_PUSH)


## «Колючая проволока»: враги вплотную получают урон в ответ.
func _thorns_hit() -> void:
	var radius_sq: float = Balance.ITEM_THORNS_RADIUS * Balance.ITEM_THORNS_RADIUS
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and global_position.distance_squared_to(enemy.global_position) <= radius_sq:
			enemy.hit_by_weapon(GameState.thorns_damage * GameState.damage_mult, (enemy.global_position - global_position).normalized() * 80.0)


func _on_enemy_died_item_fx(enemy_id: StringName, at: Vector2) -> void:
	if Balance.ENEMIES.get(enemy_id, {}).get("neutral", false) or not GameState.run_active:
		return
	if randf() * 100.0 < GameState.lifesteal_percent:
		_health.heal(Balance.ITEM_LIFESTEAL_HP)
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -12.0), "+1 ХП", Color(1.0, 0.0, 0.2), 12.0, 0.6)
	if randf() * 100.0 < GameState.explode_percent:
		_explode.call_deferred(at)


## «Взрывной понос»: убитый враг рвётся и задевает соседей.
func _explode(at: Vector2) -> void:
	if not is_inside_tree():
		return
	HitFx.burst(get_tree(), at, Color(0.58, 0.34, 0.12), 14, Balance.ITEM_EXPLODE_RADIUS * 2.0, 3.0, 0.6, true)
	HitFx.burst(get_tree(), at, Color(0.968627, 1.0, 0.0), 8, Balance.ITEM_EXPLODE_RADIUS * 1.5, 2.0, 0.5, true)
	var radius_sq: float = Balance.ITEM_EXPLODE_RADIUS * Balance.ITEM_EXPLODE_RADIUS
	for group: StringName in [&"enemies", &"neutrals"]:
		for node: Node in get_tree().get_nodes_in_group(group):
			var enemy: EnemyBase = node as EnemyBase
			if enemy != null and at.distance_squared_to(enemy.global_position) <= radius_sq:
				enemy.hit_by_weapon(Balance.ITEM_EXPLODE_DAMAGE * GameState.damage_mult, (enemy.global_position - at).normalized() * 140.0)


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
