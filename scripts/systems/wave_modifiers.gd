class_name WaveModifiers
extends Node2D
## Эффекты модификатора волны (Balance.WAVE_MOD_DATA[GameState.wave_mod]["fx"]): спавнеры (капли кислоты, мусоровоз,
## молнии, тапки, голуби, ящики, тараканы, дым), фильтры экрана (тьма, диско, канализация, похмелье), ветер, время.
## Множители врагов/игрока/говна читаются прямо в WaveRules / GameState / EnemyBase через WaveRules.mod_fx().
## Какой модификатор - решает WaveManager; этот узел только играет его.

const PUDDLE_SCENE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
const CLOUD_SCENE: PackedScene = preload("res://scenes/hazards/stink_cloud.tscn")
const TRUCK_SCENE: PackedScene = preload("res://scenes/hazards/garbage_truck.tscn")
const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/enemy_projectile.tscn")
const DARKNESS_SHADER: Shader = preload("res://shaders/darkness.gdshader")
const OVERLAY_SHADER: Shader = preload("res://shaders/mod_overlay.gdshader")
const SLIPPER_TEX: Texture2D = preload("res://assets/sprites/proj_slipper_flat.png")
const PIGEON_TEX: Texture2D = preload("res://assets/sprites/pet_pigeon.png")
const CRATE_TEX: Texture2D = preload("res://assets/sprites/airdrop_crate.png")
const WIND_BITS: Array[Texture2D] = [preload("res://assets/sprites/proj_dung.png"), preload("res://assets/sprites/proj_seed.png")]
const ACID: Color = Color(0.45, 1.0, 0.2)
const OVERLAY_MODE: Dictionary = {&"disco": 1, &"sewer": 2, &"hangover": 3}

var _timer: float = 0.0
var _dark_rect: ColorRect = null
var _fx_rect: ColorRect = null
var _dark: float = 0.0
var _fx: float = 0.0
var _fx_mode: int = 0
var _time: float = 0.0
var _base_time_scale: float = 1.0
var _scaled: bool = false
var _wind_dir: Vector2 = Vector2.RIGHT
var _wind_left: float = 0.0
var _wind_bit_left: float = 0.0


func _ready() -> void:
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.wave_ended.connect(func(_w: int) -> void: _reset_wave_state())
	EventBus.player_died.connect(_reset_wave_state)
	EventBus.run_won.connect(_reset_wave_state)
	var layer: CanvasLayer = CanvasLayer.new()
	layer.layer = 4   # под HUD (5), над миром
	add_child(layer)
	_dark_rect = _overlay_rect(DARKNESS_SHADER, layer)
	_fx_rect = _overlay_rect(OVERLAY_SHADER, layer)


func _exit_tree() -> void:
	_reset_wave_state()


## Холст под шейдер фильтра (сам по себе не виден, рисует только шейдер).
func _overlay_rect(shader: Shader, layer: CanvasLayer) -> ColorRect:
	var rect: ColorRect = ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = shader
	rect.material = mat
	rect.visible = false
	layer.add_child(rect)
	return rect


func _on_wave_started(_wave: int) -> void:
	_timer = 1.5
	var ts: float = WaveRules.mod_f("time_scale", 1.0)
	if ts != 1.0 and not _scaled:
		_base_time_scale = Engine.time_scale
		Engine.time_scale = _base_time_scale * ts
		_scaled = true
	_wind_left = 0.0


func _reset_wave_state() -> void:
	if _scaled:
		Engine.time_scale = _base_time_scale
		_scaled = false
	GameState.wind = Vector2.ZERO


func _physics_process(delta: float) -> void:
	var fighting: bool = GameState.run_active and GameState.wave_time_left > 0.0
	_time += delta
	var overlay: StringName = WaveRules.mod_fx("overlay", &"") if fighting else &""
	_update_darkness(delta, overlay == &"darkness")
	_update_fx_overlay(delta, OVERLAY_MODE.get(overlay, 0))
	if not fighting or GameState.wave_mod == &"":
		GameState.wind = Vector2.ZERO
		return
	if WaveRules.mod_fx("wind", false):
		_update_wind(delta)
	var spawner_kind: StringName = WaveRules.mod_fx("spawner", &"")
	if spawner_kind == &"":
		return
	_timer -= delta
	if _timer > 0.0:
		return
	match spawner_kind:
		&"acid":
			_timer = Balance.ACID_DROP_INTERVAL_SEC * randf_range(0.7, 1.3)
			_acid_drop()
		&"truck":
			_timer = Balance.TRUCK_INTERVAL_SEC * randf_range(0.8, 1.2)
			_truck()
		&"lightning":
			_timer = Balance.LIGHTNING_INTERVAL_SEC * randf_range(0.7, 1.3)
			_lightning()
		&"slippers":
			_timer = Balance.SLIPPER_INTERVAL_SEC * randf_range(0.6, 1.4)
			_slipper()
		&"pigeons":
			_timer = Balance.PIGEON_RAID_INTERVAL_SEC * randf_range(0.8, 1.2)
			_pigeons()
		&"crates":
			_timer = Balance.CRATE_INTERVAL_SEC * randf_range(0.8, 1.2)
			_crate()
		&"roaches":
			_timer = Balance.ROACH_INTERVAL_SEC * randf_range(0.8, 1.2)
			_roaches()
		&"smoke":
			_timer = Balance.SMOKE_INTERVAL_SEC * randf_range(0.7, 1.3)
			_smoke()


func _player() -> Node2D:
	return get_tree().get_first_node_in_group(&"player") as Node2D


func _arena_clamp(at: Vector2, margin: float = 20.0) -> Vector2:
	return at.clamp(Vector2(margin, margin), Vector2(Balance.ARENA_SIZE - margin, Balance.ARENA_SIZE - margin))


## Точка удара: чаще рядом с игроком (иначе модификатор не чувствуется), иногда где угодно.
func _strike_point(near_chance: float, near_radius: float = 90.0) -> Vector2:
	var player: Node2D = _player()
	if player != null and randf() < near_chance:
		return _arena_clamp(player.global_position + Vector2.from_angle(randf() * TAU) * randf_range(0.0, near_radius))
	return Vector2(randf_range(30.0, Balance.ARENA_SIZE - 30.0), randf_range(30.0, Balance.ARENA_SIZE - 30.0))


func _hurt_player_at(at: Vector2, radius: float, damage: float, source: StringName) -> void:
	var player: Node2D = _player()
	if player == null or player.global_position.distance_to(at) > radius:
		return
	var hb: HurtboxComponent = player.get_node_or_null(^"Hurtbox") as HurtboxComponent
	if hb != null and hb.receive_hit(damage):
		GameState.last_damage_source = source


func _still_on(kind: StringName) -> bool:
	return is_inside_tree() and WaveRules.mod_fx("spawner", &"") == kind and GameState.wave_time_left > 0.0


func _spawn_puddle(at: Vector2, radius: float, damage: float, sec: float, source: StringName, tint: Color) -> void:
	var puddle: TimedHazard = PUDDLE_SCENE.instantiate() as TimedHazard
	get_tree().current_scene.add_child(puddle)
	puddle.source_id = source
	puddle.setup(at, radius, damage, sec)
	puddle.get_node(^"Sprite2D").self_modulate = tint


# ---------------------------------------------------------------- спавнеры

func _acid_drop() -> void:
	var at: Vector2 = _strike_point(Balance.ACID_DROP_NEAR_PLAYER)
	Telegraph.circle(get_tree(), at, Balance.ACID_DROP_RADIUS, Balance.ACID_DROP_WARN_SEC)
	await get_tree().create_timer(Balance.ACID_DROP_WARN_SEC, false).timeout
	if not _still_on(&"acid"):
		return
	_spawn_puddle(at, Balance.ACID_DROP_RADIUS, Balance.ACID_PUDDLE_DAMAGE * WaveRules.hazard_mult(GameState.wave), Balance.ACID_PUDDLE_SEC, &"acid_rain", ACID)
	HitFx.burst(get_tree(), at, ACID, 10, 50.0, 2.0, 0.4, true)


## Мусоровоз: полоса через всю арену рядом с игроком, сначала телеграф, потом проезд.
func _truck() -> void:
	var player: Node2D = _player()
	if player == null:
		return
	var arena: float = Balance.ARENA_SIZE
	var horizontal: bool = randf() < 0.5
	var lane: float = clampf((player.global_position.y if horizontal else player.global_position.x) + randf_range(-30.0, 30.0), 30.0, arena - 30.0)
	var from: Vector2 = Vector2(-60.0, lane) if horizontal else Vector2(lane, -60.0)
	var to: Vector2 = Vector2(arena + 60.0, lane) if horizontal else Vector2(lane, arena + 60.0)
	if randf() < 0.5:
		var tmp: Vector2 = from
		from = to
		to = tmp
	Telegraph.line(get_tree(), from, from.direction_to(to), from.distance_to(to), Balance.TRUCK_HALF_WIDTH, Balance.TRUCK_WARN_SEC)
	await get_tree().create_timer(Balance.TRUCK_WARN_SEC, false).timeout
	if not _still_on(&"truck"):
		return
	var truck: GarbageTruck = TRUCK_SCENE.instantiate() as GarbageTruck
	get_tree().current_scene.add_child(truck)
	truck.launch(from, to)


## Молния: круг-метка, потом удар (бьёт героя и, втрое сильнее, врагов в круге).
func _lightning() -> void:
	var at: Vector2 = _strike_point(0.5, 110.0)
	Telegraph.circle(get_tree(), at, Balance.LIGHTNING_RADIUS, Balance.LIGHTNING_WARN_SEC)
	await get_tree().create_timer(Balance.LIGHTNING_WARN_SEC, false).timeout
	if not _still_on(&"lightning"):
		return
	var damage: float = Balance.LIGHTNING_DAMAGE * WaveRules.hazard_mult(GameState.wave)
	_hurt_player_at(at, Balance.LIGHTNING_RADIUS, damage, &"thunder")
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and enemy.global_position.distance_to(at) <= Balance.LIGHTNING_RADIUS + 4.0:
			enemy.hit_by_weapon(damage * 3.0)
	_bolt(at)


## Зигзаг молнии сверху в точку: белый с жёлтой каймой, гаснет за 0.15 с.
func _bolt(at: Vector2) -> void:
	var line: Line2D = Line2D.new()
	var y: float = at.y - 140.0
	var x: float = at.x + randf_range(-20.0, 20.0)
	while y < at.y:
		line.add_point(Vector2(x, y))
		y += randf_range(10.0, 18.0)
		x += randf_range(-8.0, 8.0)
	line.add_point(at)
	line.width = 3.0
	line.default_color = Color(1.0, 1.0, 0.85)
	line.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	line.z_index = 15
	get_tree().current_scene.add_child(line)
	var glow: Line2D = line.duplicate() as Line2D
	glow.width = 6.0
	glow.default_color = Color(1.0, 0.95, 0.2, 0.5)
	glow.z_index = 14
	get_tree().current_scene.add_child(glow)
	HitFx.burst(get_tree(), at, Color(1.0, 1.0, 0.4), 12, 80.0, 3.0, 0.3, true)
	for node: Line2D in [line, glow]:
		var tw: Tween = node.create_tween()
		tw.tween_property(node, "modulate:a", 0.0, 0.15)
		tw.tween_callback(node.queue_free)


## Тапок летит из-за края арены через игрока (вражеский снаряд - бот и игрок видят его как снаряд).
func _slipper() -> void:
	var player: Node2D = _player()
	if player == null:
		return
	var arena: float = Balance.ARENA_SIZE
	var side: int = randi() % 4
	var from: Vector2 = [Vector2(-10.0, randf() * arena), Vector2(arena + 10.0, randf() * arena), Vector2(randf() * arena, -10.0), Vector2(randf() * arena, arena + 10.0)][side]
	var aim: Vector2 = player.global_position + Vector2.from_angle(randf() * TAU) * randf_range(0.0, 40.0)
	var shot: EnemyProjectile = PoolManager.acquire(PROJECTILE_SCENE) as EnemyProjectile
	get_tree().current_scene.add_child(shot)
	shot.source_id = &"slipper_storm"
	shot.launch(from, from.direction_to(aim), Balance.SLIPPER_DAMAGE * WaveRules.hazard_mult(GameState.wave), Balance.SLIPPER_SPEED, arena * 1.6 / Balance.SLIPPER_SPEED, SLIPPER_TEX, 9.0)


## Стая из трёх голубей пролетает над полосой у игрока и бомбит её: метки, потом лужи помёта.
func _pigeons() -> void:
	var player: Node2D = _player()
	if player == null:
		return
	var arena: float = Balance.ARENA_SIZE
	var lane: float = clampf(player.global_position.y + randf_range(-25.0, 25.0), 30.0, arena - 30.0)
	var left_to_right: bool = randf() < 0.5
	var x0: float = -30.0 if left_to_right else arena + 30.0
	var x1: float = arena + 30.0 if left_to_right else -30.0
	var flight: float = absf(x1 - x0) / Balance.PIGEON_RAID_SPEED
	for k: int in 3:
		var bird: Sprite2D = Sprite2D.new()
		bird.texture = PIGEON_TEX
		bird.hframes = 4
		bird.flip_h = not left_to_right
		bird.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		bird.z_index = 12
		get_tree().current_scene.add_child(bird)
		bird.global_position = Vector2(x0 - k * 18.0, lane - 26.0 + k * 6.0)
		var tw: Tween = bird.create_tween().set_parallel(true)
		tw.tween_property(bird, "global_position:x", x1 - k * 18.0, flight)
		tw.tween_method(func(t: float) -> void: bird.frame = int(t * 24.0) % 4, 0.0, flight, flight)
		tw.chain().tween_callback(bird.queue_free)
	var drops: int = int(arena / Balance.PIGEON_RAID_DROP_EVERY_PX)
	for i: int in drops:
		var x: float = lerpf(x0, x1, (float(i) + 0.5) / float(drops))
		var at: Vector2 = Vector2(x, lane + randf_range(-6.0, 6.0))
		var when: float = absf(x - x0) / Balance.PIGEON_RAID_SPEED
		get_tree().create_timer(when, false).timeout.connect(func() -> void:
			if _still_on(&"pigeons"):
				Telegraph.circle(get_tree(), at, 11.0, 0.6)
				get_tree().create_timer(0.6, false).timeout.connect(func() -> void:
					if _still_on(&"pigeons"):
						_spawn_puddle(at, 11.0, Balance.DEATH_PUDDLE_DAMAGE * WaveRules.hazard_mult(GameState.wave), 3.0, &"pigeon_raid", Color.WHITE)))


## Ящик гуманитарки: метка, ящик падает с неба (придавит, если стоишь под ним), разлетается говном.
func _crate() -> void:
	var at: Vector2 = _strike_point(0.6, 120.0)
	Telegraph.circle(get_tree(), at, 14.0, Balance.CRATE_WARN_SEC)
	var crate: Sprite2D = Sprite2D.new()
	crate.texture = CRATE_TEX
	crate.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	crate.z_index = 12
	get_tree().current_scene.add_child(crate)
	crate.global_position = at + Vector2(0.0, -150.0)
	var tw: Tween = crate.create_tween()
	tw.tween_property(crate, "global_position", at, Balance.CRATE_WARN_SEC).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	await tw.finished
	if not is_instance_valid(crate):
		return
	crate.queue_free()
	if not _still_on(&"crates"):
		return
	_hurt_player_at(at, 14.0, Balance.CRATE_DAMAGE * WaveRules.hazard_mult(GameState.wave), &"airdrop")
	HitFx.burst(get_tree(), at, Color(0.7, 0.45, 0.2), 14, 80.0, 3.0, 0.5, true)
	HitFx.popup(get_tree(), at + Vector2(0.0, -12.0), "ГУМАНИТАРКА!", Color(0.968627, 1.0, 0.0), 14.0, 0.9)
	for i: int in Balance.CRATE_XP_DROPS:
		EventBus.xp_drop_requested.emit(at + Vector2.from_angle(randf() * TAU) * randf_range(6.0, 22.0), 2)


## Тараканий исход: пачка хилых тараканов (за них больше говна - множитель coin у модификатора).
func _roaches() -> void:
	var spawner: Node = get_parent().get_node_or_null(^"Spawner")
	if spawner != null and spawner.has_method(&"spawn_group"):
		spawner.call(&"spawn_group", &"cockroach", Balance.ROACH_GROUP, WaveRules.hp_mult(GameState.wave) * 0.4)


## Перекур: облако дыма - не бьёт, но закрывает обзор и плывёт.
func _smoke() -> void:
	var cloud: TimedHazard = CLOUD_SCENE.instantiate() as TimedHazard
	get_tree().current_scene.add_child(cloud)
	cloud.source_id = &"smoke_break"
	cloud.setup(_strike_point(0.4, 140.0), Balance.SMOKE_RADIUS, 0.0, Balance.SMOKE_SEC)
	cloud.set_deferred(&"monitoring", false)   # дым не жжётся
	cloud.get_node(^"Sprite2D").self_modulate = Color(0.75, 0.75, 0.8)
	cloud.z_index = 11   # поверх голов: именно закрывает обзор
	var drift: Vector2 = Vector2.from_angle(randf() * TAU) * 40.0
	cloud.create_tween().tween_property(cloud, "global_position", cloud.global_position + drift, Balance.SMOKE_SEC)


# ---------------------------------------------------------------- ветер и фильтры

func _update_wind(delta: float) -> void:
	_wind_left -= delta
	if _wind_left <= 0.0:
		_wind_left = Balance.WIND_CHANGE_SEC
		_wind_dir = Vector2.from_angle(randi_range(0, 7) * TAU / 8.0)
		var player: Node2D = _player()
		if player != null:
			HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -20.0), "ВЕТЕР МЕНЯЕТСЯ!", Color(0.8, 0.9, 1.0), 12.0, 0.8)
	GameState.wind = _wind_dir * Balance.WIND_FORCE
	_wind_bit_left -= delta
	if _wind_bit_left <= 0.0:
		_wind_bit_left = 0.12
		_wind_bit()


## Летящий мусор по ветру: показывает, куда дует (мелкий, полупрозрачный - не мешает видеть врагов).
func _wind_bit() -> void:
	var player: Node2D = _player()
	if player == null:
		return
	var bit: Sprite2D = Sprite2D.new()
	bit.texture = WIND_BITS[randi() % WIND_BITS.size()]
	bit.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	bit.modulate = Color(1, 1, 1, 0.55)
	bit.z_index = 9
	get_tree().current_scene.add_child(bit)
	var start: Vector2 = player.global_position - _wind_dir * 160.0 + _wind_dir.orthogonal() * randf_range(-110.0, 110.0)
	bit.global_position = start
	var tw: Tween = bit.create_tween().set_parallel(true)
	tw.tween_property(bit, "global_position", start + _wind_dir * 320.0, 1.6)
	tw.tween_property(bit, "rotation", randf_range(-6.0, 6.0), 1.6)
	tw.chain().tween_callback(bit.queue_free)


func _update_darkness(delta: float, on: bool) -> void:
	_dark = move_toward(_dark, 1.0 if on else 0.0, delta * 1.5)
	_dark_rect.visible = _dark > 0.0
	if not _dark_rect.visible:
		return
	var player: Node2D = _player()
	if player == null:
		return
	var mat: ShaderMaterial = _dark_rect.material as ShaderMaterial
	var screen: Vector2 = get_viewport().get_visible_rect().size
	var at: Vector2 = get_viewport().get_canvas_transform() * player.global_position
	var zoom: float = get_viewport().get_canvas_transform().get_scale().x
	mat.set_shader_parameter(&"center", at / screen)
	mat.set_shader_parameter(&"screen_px", screen)
	mat.set_shader_parameter(&"radius_px", Balance.DARKNESS_RADIUS * zoom)
	mat.set_shader_parameter(&"strength", _dark)


func _update_fx_overlay(delta: float, mode: int) -> void:
	if mode != 0:
		_fx_mode = mode
	_fx = move_toward(_fx, 1.0 if mode != 0 else 0.0, delta * 1.5)
	_fx_rect.visible = _fx > 0.0 and _fx_mode != 0
	if not _fx_rect.visible:
		return
	var mat: ShaderMaterial = _fx_rect.material as ShaderMaterial
	mat.set_shader_parameter(&"mode", _fx_mode)
	mat.set_shader_parameter(&"strength", _fx)
	mat.set_shader_parameter(&"time", _time)
	mat.set_shader_parameter(&"screen_px", get_viewport().get_visible_rect().size)
