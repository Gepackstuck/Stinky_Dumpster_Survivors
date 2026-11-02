class_name EnemyBase
extends CharacterBody2D
## Базовый враг: идёт к игроку, наносит урон при контакте (через Hitbox).
## Создаётся через PoolManager; после add_child() нужно вызвать setup().

const BASE_RADIUS: float = 6.0
const PUDDLE_SCENE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
static var _textures: Dictionary[StringName, Texture2D] = {}

@export var enemy_id: StringName = &"squid_gopnik"

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox
@onready var _flash: HitFlashComponent = $HitFlash
@onready var _hitbox: HitboxComponent = $Hitbox
@onready var _anim: FrameAnimatorComponent = $FrameAnimator

var _target: Node2D = null
var _speed: float = 0.0
var _dead: bool = false
var _shapes_ready: bool = false
var _knockback: Vector2 = Vector2.ZERO
var _brain: BossBrain = null
var _neutral: bool = false
var _burn_dps: float = 0.0
var _burn_left: float = 0.0
var _burn_tick: float = 0.0
var _slow_factor: float = 1.0
var _slow_left: float = 0.0

# Управление движением для «мозгов» боссов.
var speed_mult: float = 1.0
var extra_velocity: Vector2 = Vector2.ZERO
var forced_velocity: Vector2 = Vector2.ZERO
var forced_sec: float = 0.0


func _ready() -> void:
	_hurtbox.hurt.connect(_on_hurt)
	_health.died.connect(_on_died)
	_health.health_changed.connect(func(current: float, maximum: float) -> void: _flash.set_outline_by_health(current / maxf(maximum, 1.0)))


## Текущее и максимальное здоровье (для полоски элиты/босса в HUD).
func health_pair() -> Vector2:
	return Vector2(_health.current_health, _health.max_health)


func is_alive() -> bool:
	return not _dead


## Инициализировать (или заново инициализировать при выдаче из пула).
func setup(target: Node2D, spawn_position: Vector2, id: StringName = &"squid_gopnik", hp_mult: float = 1.0) -> void:
	enemy_id = id
	var stats: Dictionary = Balance.ENEMIES[enemy_id]
	_neutral = stats.get("neutral", false)
	if _neutral:
		remove_from_group(&"enemies")
		add_to_group(&"neutrals")
	else:
		remove_from_group(&"neutrals")
		add_to_group(&"enemies")
	_sprite.scale = Vector2.ONE
	_hitbox.set_deferred(&"monitoring", stats.get("contact", true))
	if enemy_id == &"trash_bin":
		_sprite.texture = _texture_for(StringName("trash_bin_%d" % randi_range(0, Balance.BIN_VARIANTS - 1)))  # разная начинка
	else:
		_sprite.texture = _texture_for(enemy_id)
	_sprite.vframes = int(stats.get("anim_rows", 1))   # у боссов лист: ряд на каждое состояние (ходьба, замахи, ярость)
	_anim.row = 0
	var mod_size: float = WaveRules.mod_f("enemy_size", 1.0) if not _neutral and not stats.has("anim_rows") else 1.0   # боссов не трогаем
	_sprite.scale = Vector2.ONE * mod_size
	_apply_size(float(stats.get("radius", BASE_RADIUS)) * mod_size)
	_revived = false
	modulate = Color.WHITE
	_bounce_t = randf() * TAU
	# летающие проходят сквозь наземных (и наоборот): тело на своём слое, сталкивается только со стеной
	collision_layer = Balance.FLYER_BODY_LAYER if stats.get("flying", false) else Balance.GROUND_BODY_LAYER
	collision_mask = Balance.FLYER_BODY_MASK if stats.get("flying", false) else Balance.GROUND_BODY_MASK
	_speed = stats["speed"] * WaveRules.speed_mult(GameState.wave)
	speed_mult = 1.0
	_burn_left = 0.0
	_slow_left = 0.0
	extra_velocity = Vector2.ZERO
	forced_sec = 0.0
	_health.setup(stats["hp"] * hp_mult)
	_hitbox.damage = stats["damage"] * WaveRules.damage_mult(GameState.wave)
	_hitbox.source_id = id
	_target = target
	if _brain != null:
		_brain.queue_free()
		_brain = null
	if stats.has("brain"):
		_brain = (load(stats["brain"]) as GDScript).new() as BossBrain
		add_child(_brain)
		_brain.setup(self, target)
	_dead = false
	_knockback = Vector2.ZERO
	global_position = spawn_position


func _physics_process(delta: float) -> void:
	if _dead or not is_instance_valid(_target):
		return
	if _brain != null:
		_brain.physics_tick(delta)
	_tick_status(delta)
	if _dead:
		return
	if forced_sec > 0.0:
		forced_sec -= delta
		velocity = forced_velocity
	else:
		velocity = global_position.direction_to(_target.global_position) * _speed * speed_mult * (_slow_factor if _slow_left > 0.0 else 1.0) + extra_velocity
	_knockback = _knockback.move_toward(Vector2.ZERO, Balance.KNOCKBACK_DECAY * delta)
	velocity += _knockback
	if velocity.x != 0.0:
		_sprite.flip_h = velocity.x < 0.0
	move_and_slide()
	_keep_distance_from_target()
	if WaveRules.mod_fx("bounce", false):   # дискотека: враги подпрыгивают в такт
		_bounce_t += delta * 9.0
		_sprite.position.y = -absf(sin(_bounce_t)) * 4.0
	elif _sprite.position.y != 0.0:
		_sprite.position.y = 0.0


## Мягкое расталкивание: враг не заходит внутрь игрока, а отъезжает — через толпу можно проломиться.
func _keep_distance_from_target() -> void:
	if _speed <= 0.0:
		return
	var offset: Vector2 = global_position - _target.global_position
	var distance: float = offset.length()
	if distance < Balance.ENEMY_PLAYER_MIN_DISTANCE and distance > 0.001:
		global_position += offset / distance * (Balance.ENEMY_PLAYER_MIN_DISTANCE - distance)


## Убрать врага без смерти (конец волны): без дропа, без счёта убийств.
func vanish() -> void:
	if _dead:
		return
	_dead = true
	HitFx.burst(get_tree(), global_position, Color(0.2235, 1.0, 0.0784), 6, 60.0)
	PoolManager.release(self)


## Мерзость из бака: от удара летят объедки, слизь и мухи, бак трясётся; при разбитии — взрыв помоев.
func _bin_hit_fx(final: bool) -> void:
	var tree: SceneTree = get_tree()
	var at: Vector2 = global_position + Vector2(0.0, -4.0)
	var junk: Array[Color] = [Color(0.2235, 1.0, 0.0784), Color(0.58, 0.34, 0.12), Color(1.0, 1.0, 1.0),
			Color(0.968627, 1.0, 0.0), Color(0.0, 0.3, 1.0), Color(1.0, 0.0627, 0.9412), Color(1.0, 0.0, 0.2)]
	var pieces: int = 3 if not final else 6
	for i: int in pieces:
		HitFx.burst(tree, at, junk[randi() % junk.size()], 4 if not final else 8, 90.0 if not final else 150.0, 3.0, 0.7, true)
	HitFx.burst(tree, at, Color(0.0, 0.0, 0.0), 3, 60.0, 2.0, 1.0, true)  # мухи
	if not final:
		var tween: Tween = create_tween()
		_sprite.position = Vector2(randf_range(-2.0, 2.0), 0.0)
		tween.tween_property(_sprite, "position", Vector2.ZERO, 0.12)


## Поджечь: урон в секунду на несколько секунд (повторный поджог обновляет таймер).
func ignite(dps: float, sec: float) -> void:
	_burn_dps = maxf(_burn_dps if _burn_left > 0.0 else 0.0, dps)
	_burn_left = maxf(_burn_left, sec)


## Замедлить: множитель скорости на несколько секунд.
func slow(factor: float, sec: float) -> void:
	_slow_factor = factor
	_slow_left = maxf(_slow_left, sec)


func _tick_status(delta: float) -> void:
	if _slow_left > 0.0:
		_slow_left -= delta
	if _burn_left <= 0.0:
		return
	_burn_left -= delta
	_burn_tick -= delta
	if _burn_tick <= 0.0:
		_burn_tick = 0.25
		HitFx.burst(get_tree(), global_position + Vector2(0.0, -4.0), Color(1.0, 0.45, 0.0), 3, 30.0, 2.0, 0.4, true)
		HitFx.burst(get_tree(), global_position + Vector2(0.0, -6.0), Color(1.0, 0.9, 0.2), 2, 24.0, 2.0, 0.35, true)
		_health.take_damage(_burn_dps * 0.25)


## Лечение долей от максимума (знахарка, обжора).
func heal_percent(fraction: float) -> void:
	if _dead:
		return
	_health.heal(_health.max_health * fraction)
	_flash.flash(Color(0.2235, 1.0, 0.0784))


## Обжора растёт: спрайт крупнее (до предела), здоровья чуть добавляется.
func grow(step: float) -> void:
	_sprite.scale = Vector2.ONE * minf(_sprite.scale.x + step, Balance.GLUTTON_MAX_SCALE)


## Яйцо лопается: враг исчезает без дропа и убийства, на его месте вылупляется другой.
func hatch_into(id: StringName) -> void:
	if _dead:
		return
	_dead = true
	HitFx.burst(get_tree(), global_position, Color(0.968627, 1.0, 0.0), 10, 80.0, 3.0, 0.5)
	spawn_enemy.call_deferred(get_parent(), _target, id, global_position, WaveRules.hp_mult(GameState.wave))
	PoolManager.release(self)


## Создать врага вне очереди спавна (вылупление, дети мамки).
static func spawn_enemy(parent: Node, target: Node2D, id: StringName, at: Vector2, hp_mult: float) -> EnemyBase:
	if not is_instance_valid(parent) or not is_instance_valid(target):
		return null
	var enemy: EnemyBase = PoolManager.acquire(load("res://scenes/enemies/enemy_base.tscn") as PackedScene) as EnemyBase
	parent.add_child(enemy)
	enemy.setup(target, at, id, hp_mult)
	return enemy


## Ряд анимации (состояние босса); restart — начать ряд с первого кадра.
func set_anim_row(row: int, restart: bool = true) -> void:
	if _anim.row == row and not restart:
		return
	_anim.row = row
	if restart:
		_anim.restart()


func flash(color: Color) -> void:
	_flash.flash(color)


func health_fraction() -> float:
	return _health.current_health / maxf(_health.max_health, 1.0)


static func _texture_for(id: StringName) -> Texture2D:
	if not _textures.has(id):
		_textures[id] = load("res://assets/sprites/enemy_%s.png" % id) as Texture2D
	return _textures[id]


## Размер тела/хитбоксов под тип врага (общие ресурсы форм копируем один раз на экземпляр).
func _apply_size(radius: float) -> void:
	var body: CollisionShape2D = $CollisionShape2D
	var hurt_shape: CollisionShape2D = $Hurtbox/CollisionShape2D
	var hit_shape: CollisionShape2D = $Hitbox/CollisionShape2D
	if not _shapes_ready:
		body.shape = body.shape.duplicate()
		hurt_shape.shape = hurt_shape.shape.duplicate()
		hit_shape.shape = hit_shape.shape.duplicate()
		_shapes_ready = true
	var k: float = radius / BASE_RADIUS
	(body.shape as CircleShape2D).radius = radius
	(hurt_shape.shape as RectangleShape2D).size = Vector2(14.0, 14.0) * k
	(hit_shape.shape as RectangleShape2D).size = Vector2(12.0, 12.0) * k


## Удар оружием игрока: урон и (опционально) своя скорость отбрасывания.
func hit_by_weapon(damage: float, push: Vector2 = Vector2.ZERO, source: StringName = &"") -> void:
	if _dead:
		return
	if source != &"":
		GameState.hit_source = source
	if _hurtbox.receive_hit(damage) and push != Vector2.ZERO:
		_knockback = push


## Толчок без урона (вонь портков).
func shove(push: Vector2) -> void:
	if not _dead and not _neutral:
		_knockback = push


func _on_hurt(damage: float) -> void:
	if _dead:
		return
	_flash.flash(Color.WHITE)
	if _neutral:
		_bin_hit_fx(false)
	if is_instance_valid(_target) and not _neutral:
		_knockback = _target.global_position.direction_to(global_position) * Balance.ENEMY_KNOCKBACK_SPEED
	if not _neutral:
		HitFx.burst(get_tree(), global_position, Color(1.0, 0.0, 0.2), 5, 70.0)
		_item_hit_effects()
	if GameState.is_crit_damage(damage):
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -14.0), str(int(damage)) + "!", Color(1.0, 0.85, 0.0), 22.0, 0.8, true)
	else:
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -10.0), str(int(damage)), Color.WHITE)
	if not _neutral:
		GameState.record_damage(minf(damage, _health.current_health))
	_health.take_damage(damage)


## Эффекты предметов на попадание: поджог (зажигалка) и сильный отброс (лом).
func _item_hit_effects() -> void:
	if GameState.ink_percent > 0.0 and randf() * 100.0 < GameState.ink_percent:   # кальмар: чернила
		slow(0.5, 1.5)
	if GameState.steal_percent > 0.0 and randf() * 100.0 < GameState.steal_percent:   # крыс: ворюга
		GameState.coins += 1
		GameState.run_coins_earned += 1
	if GameState.burn_percent > 0.0 and randf() * 100.0 < GameState.burn_percent:
		ignite(Balance.ITEM_BURN_DPS, Balance.ITEM_BURN_SEC)
	if GameState.bash_percent > 0.0 and randf() * 100.0 < GameState.bash_percent and is_instance_valid(_target):
		_knockback = _target.global_position.direction_to(global_position) * Balance.ITEM_BASH_PUSH


var _revived: bool = false
var _bounce_t: float = 0.0


## Эффект модификатора волны при смерти врага: лужа, взрыв, «зомби» встаёт, джекпот.
func _mod_death_effect() -> void:
	var stats: Dictionary = Balance.ENEMIES[enemy_id]
	if stats.has("anim_rows"):
		return   # элиты и боссы - без фокусов
	var tree: SceneTree = get_tree()
	var at: Vector2 = global_position
	match WaveRules.mod_fx("on_death", &""):
		&"puddle":
			if randf() < Balance.DEATH_PUDDLE_CHANCE:
				var puddle: TimedHazard = PUDDLE_SCENE.instantiate() as TimedHazard
				tree.current_scene.add_child.call_deferred(puddle)
				puddle.ready.connect(func() -> void:
					puddle.source_id = enemy_id
					puddle.setup(at, 14.0, Balance.DEATH_PUDDLE_DAMAGE * WaveRules.hazard_mult(GameState.wave), 3.0), CONNECT_ONE_SHOT)
		&"explode":
			HitFx.burst(tree, at, Color(1.0, 0.6, 0.0), 16, 90.0, 3.0, 0.4, true)
			HitFx.burst(tree, at, Color(1.0, 1.0, 0.3), 8, 50.0, 4.0, 0.3, true)
			var player: Node2D = tree.get_first_node_in_group(&"player") as Node2D
			if player != null and player.global_position.distance_to(at) < Balance.EXPLODE_ON_DEATH_RADIUS:
				var hb: HurtboxComponent = player.get_node_or_null(^"Hurtbox") as HurtboxComponent
				if hb != null and hb.receive_hit(Balance.EXPLODE_ON_DEATH_DAMAGE * WaveRules.hazard_mult(GameState.wave)):
					GameState.last_damage_source = enemy_id
			for node: Node in tree.get_nodes_in_group(&"enemies"):
				var other: EnemyBase = node as EnemyBase
				if other != null and other != self and other.global_position.distance_to(at) < Balance.EXPLODE_ON_DEATH_RADIUS:
					other.hit_by_weapon.call_deferred(20.0, at.direction_to(other.global_position) * 200.0)
		&"revive":
			if not _revived and randf() < Balance.REVIVE_CHANCE:
				var parent: Node = get_parent()
				var id: StringName = enemy_id
				var target: Node2D = _target
				HitFx.popup(tree, at + Vector2(0.0, -10.0), "ВСТАЁТ!", Color(0.6, 1.0, 0.3), 12.0, 0.8)
				tree.create_timer(1.0, false).timeout.connect(func() -> void:
					if is_instance_valid(parent) and is_instance_valid(target) and GameState.wave_mod == &"zombies":
						var zombie: EnemyBase = EnemyBase.spawn_enemy(parent, target, id, at, WaveRules.hp_mult(GameState.wave) * 0.6)
						if zombie != null:
							zombie._revived = true
							zombie.modulate = Color(0.6, 1.0, 0.5))
		&"jackpot":
			if randf() < Balance.JACKPOT_CHANCE:
				HitFx.popup(tree, at + Vector2(0.0, -14.0), "ДЖЕКПОТ!", Color(1.0, 0.9, 0.0), 22.0, 1.2, true)
				for i: int in Balance.JACKPOT_DROPS:
					EventBus.xp_drop_requested.emit(at + Vector2.from_angle(randf() * TAU) * randf_range(4.0, 26.0), 3)


func _on_died() -> void:
	if _dead:
		return
	_dead = true
	if _neutral:
		_bin_hit_fx(true)
	else:
		HitFx.burst(get_tree(), global_position, Color(1.0, 0.0625, 0.9412), 14, 110.0, 3.0, 0.5)
		HitFx.burst(get_tree(), global_position, Color(0.2235, 1.0, 0.0784), 8, 80.0, 2.0, 0.5)
	if not _neutral:
		_mod_death_effect()
	EventBus.enemy_died.emit(enemy_id, global_position)
	if _brain != null:
		_brain.on_death()
	PoolManager.release(self)
