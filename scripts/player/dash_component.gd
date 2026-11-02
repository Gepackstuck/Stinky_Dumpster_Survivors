class_name DashComponent
extends Node
## Рывок героя (кнопка dash): короткий бросок с неуязвимостью. У каждого героя свой (Balance.HERO_DASH):
## молодые - дальше и чаще, старые - короче и реже, зато с фишкой (отпихнуть клюкой, вымести метлой и т.п.).
## Игрок спрашивает is_dashing() и dash_velocity(); сам компонент шлёт EventBus.dash_state для HUD.

@export var body: CharacterBody2D
@export var sprite: Sprite2D
@export var hurtbox: HurtboxComponent

var _p: Dictionary = {}
var _charges: int = 1
var _recharge: float = 0.0       # секунды до следующего заряда
var _dash_left: float = 0.0
var _dir: Vector2 = Vector2.RIGHT
var _speed: float = 0.0
var _start: Vector2 = Vector2.ZERO
var _ghost_left: float = 0.0
var _last_sent: Vector3 = Vector3(-1, -1, -1)


func _ready() -> void:
	_p = Balance.DASH_BASE.duplicate()
	var hero: Dictionary = Balance.HERO_DASH.get(GameState.character, {})
	for key: String in hero:
		_p[key] = hero[key]
	_charges = int(_p["charges"])


## Параметры рывка героя (для досье на кладбище).
static func profile(hero_id: StringName) -> Dictionary:
	var p: Dictionary = Balance.DASH_BASE.duplicate()
	var hero: Dictionary = Balance.HERO_DASH.get(hero_id, {})
	for key: String in hero:
		p[key] = hero[key]
	return p


func is_dashing() -> bool:
	return _dash_left > 0.0


func dash_velocity() -> Vector2:
	return _dir * _speed


## Попытка рывка в направлении move_dir (если стоит - туда, куда смотрел).
func try_dash(move_dir: Vector2, facing: Vector2) -> bool:
	if _charges <= 0 or _dash_left > 0.0 or get_tree().paused:
		return false
	_charges -= 1
	if _recharge <= 0.0:
		_recharge = float(_p["cd"])
	_dir = (move_dir if move_dir != Vector2.ZERO else facing).normalized()
	var fx: StringName = _p["fx"]
	var iframe: float = float(_p["sec"]) + float(_p["iframe_extra"])
	if fx == &"drunk":
		_dir = _dir.rotated(deg_to_rad(randf_range(-Balance.DASH_DRUNK_DEG, Balance.DASH_DRUNK_DEG)))
		iframe *= 1.6
	elif fx == &"fly":
		iframe += 0.15
	_start = body.global_position
	if GameState.dash_hp_cost > 0.0 and body.has_method(&"pay_hp"):   # проклятье куклы вуду
		body.call(&"pay_hp", GameState.dash_hp_cost)
	hurtbox.grant_invulnerability(iframe)
	if fx == &"slow":
		_slow_around(_start, Balance.DASH_FX_RADIUS)
		HitFx.burst(get_tree(), _start, Color(0.2235, 1.0, 0.0784), 14, 70.0, 3.0, 0.5, true)
	if fx == &"blink":
		HitFx.burst(get_tree(), _start, Color(0.0, 0.94, 1.0), 12, 60.0, 2.0, 0.4, true)
		body.global_position = _blink_target()
		HitFx.burst(get_tree(), body.global_position, Color(0.0, 0.94, 1.0), 12, 60.0, 2.0, 0.4, true)
		_finish()
	else:
		_speed = float(_p["dist"]) / float(_p["sec"])
		_dash_left = float(_p["sec"])
		_ghost_left = 0.0
	HitFx.burst(get_tree(), _start + Vector2(0.0, 6.0), Color(0.7, 0.6, 0.45), 6, 40.0, 2.0, 0.35, true)   # пыль из-под ног
	EventBus.dash_used.emit(_start)
	return true


func _physics_process(delta: float) -> void:
	if _recharge > 0.0:
		_recharge -= delta
		if _recharge <= 0.0:
			_charges = mini(_charges + 1, int(_p["charges"]))
			_recharge = float(_p["cd"]) if _charges < int(_p["charges"]) else 0.0
	if _dash_left > 0.0 and StringName(_p["fx"]) != &"fly" and _blocked(body.global_position, _dir):
		_bump()
	if _dash_left > 0.0:
		_dash_left -= delta
		_ghost_left -= delta
		if _ghost_left <= 0.0:
			_ghost_left = 0.035
			_spawn_ghost()
		if _dash_left <= 0.0:
			_finish()
	var state: Vector3 = Vector3(_charges, int(_p["charges"]), snappedf(1.0 - _recharge / float(_p["cd"]) if _recharge > 0.0 else 1.0, 0.02))
	if state != _last_sent:
		_last_sent = state
		EventBus.dash_state.emit(_charges, int(_p["charges"]), state.z)


func _finish() -> void:
	_dash_left = 0.0
	var end: Vector2 = body.global_position
	match StringName(_p["fx"]):
		&"knock":
			for enemy: EnemyBase in _enemies_near(end, Balance.DASH_FX_RADIUS):
				enemy.shove(end.direction_to(enemy.global_position) * Balance.DASH_FX_KNOCK)
			HitFx.burst(get_tree(), end, Color(0.968627, 1.0, 0.0), 12, 80.0, 3.0, 0.4, true)
		&"sweep":
			for enemy: EnemyBase in _enemies_on_path(_start, end, 16.0):
				enemy.hit_by_weapon(GameState.roll_damage(Balance.DASH_FX_DAMAGE), _dir * Balance.DASH_FX_KNOCK * 0.6, &"dash")
		&"trail":
			for enemy: EnemyBase in _enemies_on_path(_start, end, 22.0):
				enemy.slow(Balance.DASH_FX_SLOW, Balance.DASH_FX_SLOW_SEC)
			HitFx.burst(get_tree(), (_start + end) * 0.5, Color(0.968627, 0.85, 0.3), 10, 50.0, 2.0, 0.6, true)
		&"heal":
			if body.has_method(&"heal"):
				body.call(&"heal", Balance.DASH_FX_HEAL)
			HitFx.burst(get_tree(), end, Color(0.2235, 1.0, 0.0784), 8, 40.0, 2.0, 0.5, true)


## Враг вплотную по курсу? (Сквозь тела рывком не пройти - зажали, значит зажали.)
func _blocked(at: Vector2, dir: Vector2) -> bool:
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null or not enemy.is_alive():
			continue
		var off: Vector2 = enemy.global_position - at
		var reach: float = float(Balance.ENEMIES.get(enemy.enemy_id, {}).get("radius", 8.0)) + Balance.DASH_BLOCK_PAD
		if off.length() <= reach and off.normalized().dot(dir) >= Balance.DASH_BLOCK_DOT:
			return true
	return false


## Упёрся: рывок обрывается, неуязвимость снимается.
func _bump() -> void:
	_dash_left = 0.0
	Profile.stat_add(&"bumps", 1)
	if Profile.stat(&"bumps") >= 100:
		Achievements.unlock(&"bump_100")
	hurtbox.cancel_invulnerability()
	HitFx.popup(get_tree(), body.global_position + Vector2(0.0, -12.0), "УПЁРСЯ!", Color(1.0, 0.3, 0.2), 12.0, 0.6)
	_finish()


## Телепорт идёт шагами по линии и встаёт перед первым врагом (через толпу не прыгнуть).
func _blink_target() -> Vector2:
	var at: Vector2 = _start
	var arena: Vector2 = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	var steps: int = int(float(_p["dist"]) / 4.0)
	for i: int in steps:
		var nxt: Vector2 = (at + _dir * 4.0).clamp(Vector2.ZERO, arena)
		if _blocked(at, _dir):
			hurtbox.cancel_invulnerability()
			break
		at = nxt
	return at


func _slow_around(at: Vector2, radius: float) -> void:
	for enemy: EnemyBase in _enemies_near(at, radius):
		enemy.slow(Balance.DASH_FX_SLOW, Balance.DASH_FX_SLOW_SEC)


func _enemies_near(at: Vector2, radius: float) -> Array[EnemyBase]:
	var out: Array[EnemyBase] = []
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and enemy.global_position.distance_to(at) <= radius:
			out.append(enemy)
	return out


func _enemies_on_path(a: Vector2, b: Vector2, half_width: float) -> Array[EnemyBase]:
	var out: Array[EnemyBase] = []
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null:
			continue
		var closest: Vector2 = Geometry2D.get_closest_point_to_segment(enemy.global_position, a, b)
		if closest.distance_to(enemy.global_position) <= half_width:
			out.append(enemy)
	return out


## Послеобраз: копия текущего кадра героя, кислотно-зелёная, тает.
func _spawn_ghost() -> void:
	if sprite == null:
		return
	var ghost: Sprite2D = Sprite2D.new()
	ghost.texture = sprite.texture
	ghost.hframes = sprite.hframes
	ghost.vframes = sprite.vframes
	ghost.frame = sprite.frame
	ghost.flip_h = sprite.flip_h
	ghost.offset = sprite.offset
	ghost.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	ghost.modulate = Color(0.2235, 1.0, 0.0784, 0.55) if StringName(_p["fx"]) != &"fly" else Color(0.7, 0.7, 1.0, 0.55)
	ghost.z_index = -1
	get_tree().current_scene.add_child(ghost)
	ghost.global_position = sprite.global_position
	var tween: Tween = ghost.create_tween()
	tween.tween_property(ghost, "modulate:a", 0.0, 0.22)
	tween.tween_callback(ghost.queue_free)
