class_name WeatherHazards
extends Node2D
## Погода волны на поле: осенью копятся лужи, зимой растут сугробы (оба тормозят всех),
## летом жара понемногу ест ХП у всех (героя не ниже порога), весной вытаивают подснежники-бонусы.
## В конце волны всё тает за секунду.

const PUDDLE: Texture2D = preload("res://assets/sprites/weather_puddle.png")
const DRIFT: Texture2D = preload("res://assets/sprites/weather_drift.png")
const SNOWDROP: Texture2D = preload("res://assets/sprites/weather_snowdrop.png")
const TICK_SEC: float = 0.1

var _spots: Array[Sprite2D] = []      # лужи и сугробы: meta "r" радиус, "slow" множитель
var _drops: Array[Sprite2D] = []
var _spawn_left: float = 1.0
var _heat_left: float = Balance.HEAT_TICK_SEC
var _tick_left: float = 0.0
var _anim_t: float = 0.0


func _ready() -> void:
	z_index = -1   # на полу, под всеми
	EventBus.wave_ended.connect(func(_w: int) -> void: _clear())


func _physics_process(delta: float) -> void:
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null:
		return
	var season: StringName = GameState.season
	if season == &"" or GameState.wave_time_left <= 0.0:
		player.set(&"terrain_mult", 1.0)
		return
	_anim_t += delta
	_spawn_left -= delta
	if _spawn_left <= 0.0:
		_spawn(season, player)
	if season == &"summer":
		_heat_left -= delta
		if _heat_left <= 0.0:
			_heat_left = Balance.HEAT_TICK_SEC
			_heat(player)
	_tick_left -= delta
	if _tick_left <= 0.0:
		_tick_left = TICK_SEC
		_apply_slow(player)
		_pick_drops(player)
	for d: Sprite2D in _drops:
		d.frame = int(_anim_t * 4.0) % 4


func _spawn(season: StringName, player: Node2D) -> void:
	match season:
		&"autumn":
			_spawn_left = Balance.PUDDLE_EVERY_SEC
			if _spots.size() < Balance.PUDDLE_MAX:
				var s: Sprite2D = _add_sprite(PUDDLE, _spot_near(player), 4)
				s.set_meta(&"r", Balance.PUDDLE_RADIUS)
				s.set_meta(&"slow", Balance.PUDDLE_SLOW)
				s.scale = Vector2(0.2, 0.2)
				s.create_tween().tween_property(s, ^"scale", Vector2.ONE, 1.5)   # лужа натекает
				_spots.append(s)
		&"winter":
			_spawn_left = Balance.DRIFT_EVERY_SEC
			if _spots.size() < Balance.DRIFT_MAX:
				var s: Sprite2D = _add_sprite(DRIFT, _spot_near(player), 4)
				s.set_meta(&"r", Balance.DRIFT_RADIUS)
				s.set_meta(&"slow", Balance.DRIFT_SLOW)
				s.frame = 0
				s.create_tween().tween_property(s, ^"frame", 3, Balance.DRIFT_GROW_SEC)   # сугроб наметает
				_spots.append(s)
		&"spring":
			_spawn_left = Balance.SNOWDROP_EVERY_SEC
			if _drops.size() < Balance.SNOWDROP_MAX:
				var d: Sprite2D = _add_sprite(SNOWDROP, _spot_near(player), 4)
				d.z_index = 2
				HitFx.burst(get_tree(), d.global_position, Color(0.55, 0.35, 0.15), 8, 40.0, 2.0, 0.4, true)
				_drops.append(d)
		_:
			_spawn_left = 1.0


## Точка на арене недалеко от героя, но не под ним (чтобы не подставлять сразу).
func _spot_near(player: Node2D) -> Vector2:
	var margin: float = 20.0
	var p: Vector2 = player.global_position + Vector2.from_angle(randf() * TAU) * randf_range(40.0, 170.0)
	return p.clamp(Vector2(margin, margin), Vector2(Balance.ARENA_SIZE - margin, Balance.ARENA_SIZE - margin)).round()


func _add_sprite(tex: Texture2D, at: Vector2, frames: int) -> Sprite2D:
	var s: Sprite2D = Sprite2D.new()
	s.texture = tex
	s.hframes = frames
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.global_position = at
	add_child(s)
	return s


func _slow_at(at: Vector2) -> float:
	var mult: float = 1.0
	for s: Sprite2D in _spots:
		var r: float = float(s.get_meta(&"r")) * s.scale.x * (0.4 + 0.2 * s.frame if s.texture == DRIFT else 1.0)
		if at.distance_squared_to(s.global_position) <= r * r:
			mult = minf(mult, float(s.get_meta(&"slow")))
	return mult


func _apply_slow(player: Node2D) -> void:
	if _spots.is_empty():
		player.set(&"terrain_mult", 1.0)
		return
	player.set(&"terrain_mult", _slow_at(player.global_position))
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null or Balance.ENEMIES[enemy.enemy_id].get("flying", false):
			continue
		var m: float = _slow_at(enemy.global_position)
		if m < 1.0:
			enemy.slow(m, TICK_SEC * 1.5)


func _heat(player: Node2D) -> void:
	if GameState.hp > Balance.HEAT_PLAYER_MIN_HP and player.has_method(&"pay_hp"):
		player.call(&"pay_hp", Balance.HEAT_PLAYER_DAMAGE)
		HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -24.0), "ЖАРКО", Color(1.0, 0.55, 0.1))
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null:
			enemy.weather_damage(Balance.HEAT_ENEMY_FRACTION)


func _pick_drops(player: Node2D) -> void:
	var r_sq: float = Balance.SNOWDROP_PICK_RADIUS * Balance.SNOWDROP_PICK_RADIUS
	for d: Sprite2D in _drops.duplicate():
		if d.global_position.distance_squared_to(player.global_position) > r_sq:
			continue
		_drops.erase(d)
		if randf() < 0.5:
			GameState.coins += Balance.SNOWDROP_COINS
			HitFx.popup(get_tree(), d.global_position + Vector2(0.0, -12.0), "+%d ГОВНА" % Balance.SNOWDROP_COINS, Color(0.97, 1.0, 0.0))
		else:
			player.call(&"heal", Balance.SNOWDROP_HEAL)
			HitFx.popup(get_tree(), d.global_position + Vector2(0.0, -12.0), "+%d ХП" % int(Balance.SNOWDROP_HEAL), Color(0.22, 1.0, 0.08))
		AudioManager.play_sfx(&"pickup")
		d.queue_free()


func _clear() -> void:
	for s: Sprite2D in _spots + _drops:
		var tw: Tween = s.create_tween()
		tw.tween_property(s, ^"modulate:a", 0.0, 1.0)
		tw.tween_callback(s.queue_free)
	_spots.clear()
	_drops.clear()
	_spawn_left = 1.0
	_heat_left = Balance.HEAT_TICK_SEC
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player != null:
		player.set(&"terrain_mult", 1.0)
