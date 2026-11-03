class_name PlayerController
extends CharacterBody2D
## Игрок: движение WASD/стрелками, здоровье, магнит для XP, перки, смерть.

const CHAIN_WEAPON: GDScript = preload("res://scripts/weapons/chain_weapon.gd")
const HELD_WEAPON: GDScript = preload("res://scripts/weapons/held_weapon.gd")

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _animator: FrameAnimatorComponent = $FrameAnimator
@onready var _flash: HitFlashComponent = $HitFlash
@onready var _camera: Camera2D = $Camera2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox
@onready var _magnet: Area2D = $Magnet
@onready var _magnet_collision: CollisionShape2D = $Magnet/CollisionShape2D
@onready var _dash: DashComponent = $Dash
var _facing: Vector2 = Vector2.RIGHT
var _drain_timer: float = 0.0
var _slime_tick: float = 0.0
var _hp_sample: float = 0.0
var _pickups_for_heal: int = 0

var _arena_max: Vector2 = Vector2.ZERO
var _regen_timer: float = 0.0
var _shake: float = 0.0
var _still_time: float = 0.0
var _still_timer: float = 0.0
var _drunk_left: float = 0.0
var _combo_stacks: int = 0
var _combo_left: float = 0.0
var _slow_tick: float = 0.0
var _shoes: HeroShoes = null
var terrain_mult: float = 1.0   # лужи, сугробы (погода волны) - ставит WeatherHazards каждый тик


func _ready() -> void:
	_arena_max = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	# Камера не показывает пространство за ареной.
	var border: int = int(Balance.ARENA_BORDER_THICKNESS)
	_camera.zoom = Vector2.ONE * Balance.CAMERA_ZOOM
	_camera.limit_left = -border
	_camera.limit_top = -border
	_camera.limit_right = int(Balance.ARENA_SIZE) + border
	_camera.limit_bottom = int(Balance.ARENA_SIZE) + border
	_shoes = HeroShoes.new()   # обувь героя = заряд рывка
	add_child(_shoes)
	_hurtbox.invulnerability_sec = Balance.PLAYER_HURT_COOLDOWN_SEC
	_hurtbox.hurt.connect(_on_hurt)
	_health.health_changed.connect(_on_health_changed)
	_health.died.connect(_on_died)
	_magnet.area_entered.connect(_on_magnet_area_entered)
	EventBus.perk_chosen.connect(_on_perk_chosen)
	var look: Texture2D = CharacterLibrary.sprite_sheet(GameState.character)   # у каждого героя свой внешний вид
	if look != null:
		_sprite.texture = look
	EventBus.weapons_changed.connect(_sync_weapons)
	EventBus.enemy_died.connect(_on_enemy_died_item_fx)
	EventBus.wave_started.connect(_on_wave_started_items)
	EventBus.wave_ended.connect(_on_wave_ended_items)
	EventBus.streak_changed.connect(_on_streak_changed)
	EventBus.weapon_evolved.connect(func(id: StringName) -> void:
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -26.0), tr("ЭВОЛЮЦИЯ: %s!") % WeaponLibrary.display_name(id, 5), Color(1.0, 0.84, 0.0), 26.0, 2.0, true)
		HitFx.burst(get_tree(), global_position, Color(1.0, 0.84, 0.0), 30, 140.0, 3.0, 0.8, true)
		AudioManager.play_sfx(&"combo"))
	EventBus.shake_requested.connect(func(amount: float) -> void:
		if Settings.screen_shake:
			_shake = maxf(_shake, amount))
	EventBus.dash_used.connect(func(_at: Vector2) -> void: GameState.trick_left = Balance.HERO_TRICK_SEC if GameState.trick_bonus > 0.0 else 0.0)
	EventBus.xp_collected.connect(_on_xp_for_heal)
	EventBus.wave_started.connect(func(_w: int) -> void:
		if GameState.pies > 0.0:
			heal(GameState.pies)
			HitFx.chatter(get_tree(), global_position + Vector2(0.0, -16.0), "ПИРОЖОК! +%d" % roundi(GameState.pies), Color(1.0, 0.75, 0.3), 12.0, 0.8))
	EventBus.wave_started.connect(func(_w: int) -> void: _update_magnet_radius())
	EventBus.wave_ended.connect(func(_w: int) -> void: _update_magnet_radius.call_deferred())
	_update_magnet_radius()
	_health.setup(Balance.PLAYER_MAX_HP)


func _physics_process(delta: float) -> void:
	var direction: Vector2 = Input.get_vector(&"move_left", &"move_right", &"move_up", &"move_down")
	if direction != Vector2.ZERO:
		_facing = direction
	if Input.is_action_just_pressed(&"dash"):
		if not _dash.try_dash(direction, _facing) and not _dash.is_dashing():
			_shoes.deny()   # сил нет - ботинки краснеют
	var speed_mult: float = GameState.move_speed_mult * WaveRules.mod_f("player_speed", 1.0) * _rush_mult() * terrain_mult
	if not GameState.run_active:   # забег окончен: к воротам идём ровным шагом, статы и погода больше не важны
		speed_mult = Balance.AFTER_RUN_SPEED_MULT
	var wanted: Vector2 = direction * Balance.PLAYER_MOVE_SPEED * speed_mult
	if _dash.is_dashing():
		velocity = _dash.dash_velocity()
	elif WaveRules.mod_fx("ice", false) and GameState.run_active:   # жирный пол: разгон и торможение с инерцией
		velocity = velocity.lerp(wanted, clampf(Balance.ICE_ACCEL * delta, 0.0, 1.0))
	else:
		velocity = wanted
	if not _dash.is_dashing() and GameState.run_active:
		velocity += GameState.wind   # ветер с помойки (модификатор волны)
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
	if GameState.run_active and GameState.wave_time_left > 0.0:
		GameState.tick_streak(delta)
	GameState.still_sec = GameState.still_sec + delta if direction == Vector2.ZERO else 0.0
	_update_still_regen(delta, direction == Vector2.ZERO)
	_update_item_timers(delta)
	_update_slow_field(delta, direction != Vector2.ZERO)
	if GameState.run_active and GameState.wave_time_left > 0.0:   # график ХП для экрана итога
		_hp_sample += delta
		if _hp_sample >= 1.0:
			_hp_sample = 0.0
			GameState.hp_history.append(clampf(GameState.hp / maxf(GameState.max_hp, 1.0), 0.0, 1.0))
	if GameState.trick_left > 0.0:
		GameState.trick_left -= delta
	if GameState.slime_touch > 0.0:
		_slime_tick -= delta
		if _slime_tick <= 0.0:
			_slime_tick = 0.25
			for node: Node in get_tree().get_nodes_in_group(&"enemies"):
				var enemy: EnemyBase = node as EnemyBase
				if enemy != null and enemy.global_position.distance_to(global_position) < Balance.HERO_SLIME_RADIUS:
					enemy.slow(1.0 - GameState.slime_touch / 100.0, Balance.HERO_SLIME_SEC)
	if GameState.hp_drain > 0.0 and GameState.run_active and GameState.wave_time_left > 0.0:
		_drain_timer += delta
		if _drain_timer >= Balance.CURSED_HP_DRAIN_SEC:
			_drain_timer = 0.0
			pay_hp(GameState.hp_drain)
	if GameState.regen_hp > 0.0:
		_regen_timer += delta
		if _regen_timer >= Balance.PERK_REGEN_INTERVAL_SEC:
			_regen_timer -= Balance.PERK_REGEN_INTERVAL_SEC
			_health.heal(GameState.regen_hp)


func _on_wave_started_items(_wave: int) -> void:
	GameState.block_charges = GameState.block_count
	_drunk_left = 0.0
	_combo_stacks = 0
	_combo_left = 0.0


## «Рюкзак с хламом»: после волны шанс найти бесплатный предмет.
func _on_wave_ended_items(wave_number: int) -> void:
	if GameState.stash_percent <= 0.0 or not GameState.run_active:
		return
	if randf() * 100.0 >= GameState.stash_percent:
		return
	var item_id: StringName = ItemLibrary.roll_free_item(wave_number + 2)
	if item_id == &"":
		return
	GameState.add_item(item_id)
	HitFx.popup(get_tree(), global_position + Vector2(0.0, -20.0), "В РЮКЗАКЕ НАШЁЛ: %s" % ItemLibrary.title(item_id), Color(0.968627, 1.0, 0.0), 14.0, 1.8)


## Палёнка (пьянка) и батарейка (серия) дают временную скорость атаки.
func _update_item_timers(delta: float) -> void:
	if _drunk_left > 0.0:
		_drunk_left -= delta
	if _combo_left > 0.0:
		_combo_left -= delta
		if _combo_left <= 0.0:
			_combo_stacks = 0
	var bonus: float = Balance.ITEM_DRUNK_ATTACK_BONUS if _drunk_left > 0.0 else 0.0
	bonus += float(_combo_stacks) * GameState.combo_percent / 100.0
	GameState.temp_attack_bonus = bonus


## «Доска с колёсами»: враги рядом с бегущим героем замедляются.
func _update_slow_field(delta: float, moving: bool) -> void:
	if GameState.slow_field_count <= 0 or not moving or not GameState.run_active:
		return
	_slow_tick -= delta
	if _slow_tick > 0.0:
		return
	_slow_tick = Balance.ITEM_SLOW_TICK_SEC
	var factor: float = 1.0 / (1.0 + 0.5 * float(GameState.slow_field_count))
	var radius_sq: float = Balance.ITEM_SLOW_RADIUS * Balance.ITEM_SLOW_RADIUS
	HitFx.burst(get_tree(), global_position + Vector2(0.0, 8.0), Color(0.6, 0.5, 0.35), 2, 24.0, 2.0, 0.4, true)
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and global_position.distance_squared_to(enemy.global_position) <= radius_sq:
			enemy.slow(factor, Balance.ITEM_SLOW_SEC)


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
		HitFx.chatter(get_tree(), global_position + Vector2(0.0, -12.0), "+%d ХП" % int(GameState.still_regen), Color(0.2235, 1.0, 0.0784), 12.0, 0.5)


func _update_shake(delta: float) -> void:
	if _shake <= 0.0:
		_camera.offset = Vector2.ZERO
		return
	_shake = maxf(_shake - Balance.SHAKE_DECAY * delta, 0.0)
	_camera.offset = Vector2(randf_range(-_shake, _shake), randf_range(-_shake, _shake)).round()


func _update_magnet_radius() -> void:
	var shape: CircleShape2D = _magnet_collision.shape as CircleShape2D
	shape.radius = Balance.PICKUP_RADIUS_BASE * GameState.pickup_radius_mult * WaveRules.mod_f("pickup", 1.0)


func _on_magnet_area_entered(area: Area2D) -> void:
	if area is XpPickup:
		(area as XpPickup).attract(self)


func _on_perk_chosen(_perk_id: StringName) -> void:
	_update_magnet_radius()
	_health.set_max(9.0 if GameState.nine_lives else maxf(Balance.PLAYER_MAX_HP + GameState.bonus_max_hp, 10.0))


## Оружие игрока: каждое — отдельный узел-автоатака, пересобираем при любом изменении набора.
func _sync_weapons() -> void:
	for node: Node in get_tree().get_nodes_in_group(&"weapon_nodes"):
		node.queue_free()
	var slot: int = 0
	for entry: Dictionary in GameState.weapons:
		var weapon: Node2D = null
		match entry["id"]:
			&"laser_pointer":
				var laser: LaserWeapon = LaserWeapon.new()
				laser.weapon_id = &"laser_pointer"
				laser.tier = entry["tier"]
				weapon = laser
			&"extension_cord":
				var chain: Node2D = CHAIN_WEAPON.new()
				chain.set(&"weapon_id", &"extension_cord")
				chain.set(&"tier", entry["tier"])
				weapon = chain
			&"slipper", &"tin_bomb":
				var slipper: SlipperWeapon = SlipperWeapon.new()
				slipper.weapon_id = entry["id"]
				slipper.tier = entry["tier"]
				weapon = slipper
			&"lighter", &"slingshot", &"condensed_milk", &"pipe_gun", &"crossbow", &"spray_can", &"bottle", &"mosin", &"blowtorch", &"syringe":
				var shooter: WeaponBase = WeaponBase.new()
				shooter.weapon_id = entry["id"]
				shooter.tier = entry["tier"]
				weapon = shooter
			&"sock", &"rotten_cheese":
				var aura: AuraWeapon = AuraWeapon.new()
				aura.weapon_id = entry["id"]
				aura.tier = entry["tier"]
				weapon = aura
			&"mop", &"frying_pan", &"rolling_pin", &"plunger", &"shiv", &"shovel":
				var mop: MeleeWeapon = MeleeWeapon.new()
				mop.weapon_id = entry["id"]
				mop.tier = entry["tier"]
				weapon = mop
		if weapon != null:
			weapon.add_to_group(&"weapon_nodes")
			weapon.set_meta(&"slot", slot)   # панель оружия в HUD сопоставляет узел со слотом
			add_child(weapon)
			var held: Node2D = HELD_WEAPON.new()   # оружие видно в руках героя
			held.set(&"slot_index", slot)
			held.set(&"slot_count", GameState.weapons.size())
			weapon.add_child(held)
			slot += 1
	_on_perk_chosen(&"")   # бонус набора мог поменять макс. ХП


func _on_streak_changed(tier: int, bonus: float, broken: bool) -> void:
	var at: Vector2 = global_position + Vector2(0.0, -18.0)
	if broken:
		HitFx.popup(get_tree(), at, FlavorText.random_streak_break(), Color(1.0, 0.1, 0.2), 16.0, 1.0)
	elif tier > 0:
		HitFx.popup(get_tree(), at, "СЕРИЯ +%d%% ГОВНА! %s" % [roundi(bonus * 100.0), FlavorText.random_streak_up()], Color(0.968627, 1.0, 0.0), 18.0, 1.2)


func _on_hurt(raw_damage: float) -> void:
	if not GameState.run_active and GameState.hp > 0.0:   # забег окончен (победа): мины и снаряды уже не бьют
		return
	if randf() * 100.0 < GameState.dodge_percent:
		HitFx.chatter(get_tree(), global_position + Vector2(0.0, -12.0), "МИМО!", Color(0.0, 0.94, 1.0), 14.0, 0.7)
		return
	if GameState.block_charges > 0:
		GameState.block_charges -= 1
		HitFx.chatter(get_tree(), global_position + Vector2(0.0, -12.0), "КАСКА!", Color(1.0, 1.0, 0.0), 14.0, 0.8)
		HitFx.burst(get_tree(), global_position, Color(1.0, 1.0, 0.0), 8, 50.0, 2.0, 0.4, true)
		return
	if randf() * 100.0 < GameState.repel_percent:
		_stink_repel()
		return
	var reduced: float = raw_damage * maxf(Balance.ARMOR_K / (Balance.ARMOR_K + GameState.armor), Balance.ARMOR_MIN_FACTOR)
	var damage: float = maxf(minf(roundf(reduced), _health.max_health * Balance.PLAYER_MAX_HIT_FRACTION), 1.0)
	if GameState.nine_lives:   # кот: удар - минус одна жизнь, сколько бы ни било
		damage = 1.0
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -22.0), tr("МЯУ! ОСТАЛОСЬ %d") % maxi(int(_health.current_health) - 1, 0), Color(1.0, 0.8, 0.3), 14.0, 0.9)
	EventBus.player_hit.emit(damage)
	_flash.flash(Color(1.0, 0.0, 0.2))
	if Settings.screen_shake:
		_shake = Balance.PLAYER_HIT_SHAKE
	# «пердим»: зелёное облако вонючих пикселей (без надписей)
	HitFx.burst(get_tree(), global_position + Vector2(0.0, 4.0), Color(0.2235, 1.0, 0.0784), 12, 60.0, 3.0, 0.7, true)
	HitFx.burst(get_tree(), global_position + Vector2(0.0, 4.0), Color(0.9686, 1.0, 0.0), 5, 45.0, 2.0, 0.7, true)
	_health.take_damage(damage)
	if GameState.thorns_damage > 0.0:
		_thorns_hit()


## «Обосранные портки»: вонь сдувает врагов вокруг, урон по тебе не проходит.
func _stink_repel() -> void:
	HitFx.chatter(get_tree(), global_position + Vector2(0.0, -12.0), "ВОНЬ!", Color(0.2235, 1.0, 0.0784), 14.0, 0.8)
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
			GameState.hit_source = &"thorns"
			enemy.hit_by_weapon(GameState.thorns_damage * GameState.damage_mult, (enemy.global_position - global_position).normalized() * 80.0)


func _on_enemy_died_item_fx(enemy_id: StringName, at: Vector2) -> void:
	if Balance.ENEMIES.get(enemy_id, {}).get("neutral", false) or not GameState.run_active:
		return
	if GameState.combo_percent > 0.0:
		_combo_stacks = mini(_combo_stacks + 1, Balance.ITEM_COMBO_MAX_STACKS)
		_combo_left = Balance.ITEM_COMBO_SEC
	if GameState.drunk_percent > 0.0 and _drunk_left <= 0.0 and randf() * 100.0 < GameState.drunk_percent:
		_drunk_left = Balance.ITEM_DRUNK_SEC
		HitFx.chatter(get_tree(), global_position + Vector2(0.0, -14.0), "ПЬЯНКА!", Color(0.0, 0.94, 1.0), 14.0, 0.8)
	if randf() * 100.0 < GameState.lifesteal_percent:
		_health.heal(Balance.ITEM_LIFESTEAL_HP)
		HitFx.chatter(get_tree(), global_position + Vector2(0.0, -12.0), "+1 ХП", Color(1.0, 0.0, 0.2), 12.0, 0.6)
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
				GameState.hit_source = &"items"
				enemy.hit_by_weapon(Balance.ITEM_EXPLODE_DAMAGE * GameState.damage_mult, (enemy.global_position - at).normalized() * 140.0)


## Курьер: в первые секунды волны бегает быстрее.
func _rush_mult() -> float:
	if GameState.rush <= 0.0 or GameState.wave <= 0:
		return 1.0
	var elapsed: float = WaveRules.duration_sec(GameState.wave) - GameState.wave_time_left
	return 1.0 + GameState.rush / 100.0 if elapsed < Balance.HERO_RUSH_SEC else 1.0


## Палыч: каждые N подобранных говнин +1 ХП.
func _on_xp_for_heal(_amount: int) -> void:
	if GameState.clean_heal_every <= 0:
		return
	_pickups_for_heal += 1
	if _pickups_for_heal >= GameState.clean_heal_every:
		_pickups_for_heal = 0
		heal(1.0)


## Плата здоровьем за проклятье: без неуязвимости и без смерти от неё (минимум 1 ХП).
func pay_hp(amount: float) -> void:
	var take: float = minf(amount, _health.current_health - 1.0)
	if take > 0.0:
		_health.take_damage(take)
		HitFx.chatter(get_tree(), global_position + Vector2(0.0, -14.0), "-%d" % roundi(take), Color(0.6, 0.0, 0.8), 12.0, 0.6)


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
	GameState.death_position = global_position   # Н30: тут в следующий раз будет граффити
	EventBus.player_died.emit()
