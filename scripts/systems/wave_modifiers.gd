class_name WaveModifiers
extends Node2D
## Модификаторы волн: кислотный дождь, тьма, мусоровоз, жирный пол (в игроке), день зарплаты (в GameState/WaveRules).
## Какой модификатор - решает WaveManager (GameState.wave_mod); этот узел только играет его эффекты.

const PUDDLE_SCENE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
const TRUCK_SCENE: PackedScene = preload("res://scenes/hazards/garbage_truck.tscn")
const DARKNESS_SHADER: Shader = preload("res://shaders/darkness.gdshader")
const ACID: Color = Color(0.45, 1.0, 0.2)

var _timer: float = 0.0
var _dark_layer: CanvasLayer = null
var _dark_rect: ColorRect = null
var _dark: float = 0.0


func _ready() -> void:
	EventBus.wave_started.connect(func(_w: int) -> void: _timer = 1.5)
	_build_darkness()


func _build_darkness() -> void:
	_dark_layer = CanvasLayer.new()
	_dark_layer.layer = 4   # под HUD (5), над миром
	add_child(_dark_layer)
	_dark_rect = ColorRect.new()   # холст для шейдера тьмы (сам по себе не виден)
	_dark_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_dark_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = DARKNESS_SHADER
	_dark_rect.material = mat
	_dark_layer.add_child(_dark_rect)
	_dark_rect.visible = false


func _physics_process(delta: float) -> void:
	var mod: StringName = GameState.wave_mod
	var fighting: bool = GameState.run_active and GameState.wave_time_left > 0.0
	_update_darkness(delta, mod == &"darkness" and fighting)
	if not fighting or mod == &"":
		return
	_timer -= delta
	if _timer > 0.0:
		return
	match mod:
		&"acid_rain":
			_timer = Balance.ACID_DROP_INTERVAL_SEC * randf_range(0.7, 1.3)
			_acid_drop()
		&"garbage_truck":
			_timer = Balance.TRUCK_INTERVAL_SEC * randf_range(0.8, 1.2)
			_truck()
		_:
			_timer = 999.0


func _player() -> Node2D:
	return get_tree().get_first_node_in_group(&"player") as Node2D


func _acid_drop() -> void:
	var player: Node2D = _player()
	if player == null:
		return
	var arena: float = Balance.ARENA_SIZE
	var at: Vector2 = Vector2(randf_range(30.0, arena - 30.0), randf_range(30.0, arena - 30.0))
	if randf() < Balance.ACID_DROP_NEAR_PLAYER:
		at = (player.global_position + Vector2.from_angle(randf() * TAU) * randf_range(0.0, 90.0)).clamp(Vector2(20, 20), Vector2(arena - 20, arena - 20))
	Telegraph.circle(get_tree(), at, Balance.ACID_DROP_RADIUS, Balance.ACID_DROP_WARN_SEC)
	await get_tree().create_timer(Balance.ACID_DROP_WARN_SEC, false).timeout
	if GameState.wave_mod != &"acid_rain" or not is_inside_tree():
		return
	var puddle: TimedHazard = PUDDLE_SCENE.instantiate() as TimedHazard
	get_tree().current_scene.add_child(puddle)
	puddle.source_id = &"acid_rain"
	puddle.setup(at, Balance.ACID_DROP_RADIUS, Balance.ACID_PUDDLE_DAMAGE * WaveRules.hazard_mult(GameState.wave), Balance.ACID_PUDDLE_SEC)
	puddle.self_modulate = ACID
	puddle.get_node(^"Sprite2D").self_modulate = ACID
	HitFx.burst(get_tree(), at, ACID, 10, 50.0, 2.0, 0.4, true)


## Мусоровоз: полоса через всю арену рядом с игроком, сначала телеграф, потом проезд.
func _truck() -> void:
	var player: Node2D = _player()
	if player == null:
		return
	var arena: float = Balance.ARENA_SIZE
	var horizontal: bool = randf() < 0.5
	var lane: float = (player.global_position.y if horizontal else player.global_position.x) + randf_range(-30.0, 30.0)
	lane = clampf(lane, 30.0, arena - 30.0)
	var from: Vector2 = Vector2(-40.0, lane) if horizontal else Vector2(lane, -40.0)
	var to: Vector2 = Vector2(arena + 40.0, lane) if horizontal else Vector2(lane, arena + 40.0)
	if randf() < 0.5:
		var tmp: Vector2 = from
		from = to
		to = tmp
	Telegraph.line(get_tree(), from, from.direction_to(to), from.distance_to(to), Balance.TRUCK_HALF_WIDTH, Balance.TRUCK_WARN_SEC)
	await get_tree().create_timer(Balance.TRUCK_WARN_SEC, false).timeout
	if GameState.wave_mod != &"garbage_truck" or not is_inside_tree():
		return
	var truck: GarbageTruck = TRUCK_SCENE.instantiate() as GarbageTruck
	get_tree().current_scene.add_child(truck)
	truck.launch(from, to)


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
