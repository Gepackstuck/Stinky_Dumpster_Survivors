class_name EnemyBase
extends CharacterBody2D
## Базовый враг: идёт к игроку, наносит урон при контакте (через Hitbox).
## Создаётся через PoolManager; после add_child() нужно вызвать setup().

const BASE_RADIUS: float = 6.0
static var _textures: Dictionary[StringName, Texture2D] = {}

@export var enemy_id: StringName = &"squid_gopnik"

@onready var _sprite: Sprite2D = $Sprite2D
@onready var _health: HealthComponent = $HealthComponent
@onready var _hurtbox: HurtboxComponent = $Hurtbox
@onready var _flash: HitFlashComponent = $HitFlash
@onready var _hitbox: HitboxComponent = $Hitbox

var _target: Node2D = null
var _speed: float = 0.0
var _dead: bool = false
var _shapes_ready: bool = false
var _knockback: Vector2 = Vector2.ZERO
var _brain: BossBrain = null
var _neutral: bool = false

# Управление движением для «мозгов» боссов.
var speed_mult: float = 1.0
var extra_velocity: Vector2 = Vector2.ZERO
var forced_velocity: Vector2 = Vector2.ZERO
var forced_sec: float = 0.0


func _ready() -> void:
	_hurtbox.hurt.connect(_on_hurt)
	_health.died.connect(_on_died)
	_health.health_changed.connect(func(current: float, maximum: float) -> void: _flash.set_outline_by_health(current / maxf(maximum, 1.0)))


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
	_apply_size(stats.get("radius", BASE_RADIUS))
	_speed = stats["speed"] * WaveRules.speed_mult(GameState.wave)
	speed_mult = 1.0
	extra_velocity = Vector2.ZERO
	forced_sec = 0.0
	_health.setup(stats["hp"] * hp_mult)
	_hitbox.damage = stats["damage"] * WaveRules.damage_mult(GameState.wave)
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
	if forced_sec > 0.0:
		forced_sec -= delta
		velocity = forced_velocity
	else:
		velocity = global_position.direction_to(_target.global_position) * _speed * speed_mult + extra_velocity
	_knockback = _knockback.move_toward(Vector2.ZERO, Balance.KNOCKBACK_DECAY * delta)
	velocity += _knockback
	if velocity.x != 0.0:
		_sprite.flip_h = velocity.x < 0.0
	move_and_slide()
	_keep_distance_from_target()


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
static func spawn_enemy(parent: Node, target: Node2D, id: StringName, at: Vector2, hp_mult: float) -> void:
	if not is_instance_valid(parent) or not is_instance_valid(target):
		return
	var enemy: EnemyBase = PoolManager.acquire(load("res://scenes/enemies/enemy_base.tscn") as PackedScene) as EnemyBase
	parent.add_child(enemy)
	enemy.setup(target, at, id, hp_mult)


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
func hit_by_weapon(damage: float, push: Vector2 = Vector2.ZERO) -> void:
	if _dead:
		return
	if _hurtbox.receive_hit(damage) and push != Vector2.ZERO:
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
	HitFx.popup(get_tree(), global_position + Vector2(0.0, -10.0), str(int(damage)), Color.WHITE)
	_health.take_damage(damage)


func _on_died() -> void:
	if _dead:
		return
	_dead = true
	if _neutral:
		_bin_hit_fx(true)
	else:
		HitFx.burst(get_tree(), global_position, Color(1.0, 0.0625, 0.9412), 14, 110.0, 3.0, 0.5)
		HitFx.burst(get_tree(), global_position, Color(0.2235, 1.0, 0.0784), 8, 80.0, 2.0, 0.5)
	EventBus.enemy_died.emit(enemy_id, global_position)
	if _brain != null:
		_brain.on_death()
	PoolManager.release(self)
