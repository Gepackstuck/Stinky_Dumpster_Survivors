class_name HdAtmosphere
extends Node2D
## Свет и воздух реалистичного стиля: ночная помойка. Тьма вокруг (CanvasModulate), тёплый свет от героя,
## вспышки от выстрелов и взрывов, поверх - виньетка, зерно и ползущий туман. Интерфейс не затрагивается.
## Добавляется в уровень только при ArtStyle.is_hd(). Все числа - Balance.HD_*.

const OVERLAY: Shader = preload("res://assets/shaders/hd_overlay.gdshader")

var _player: Node2D
var _light: PointLight2D
var _flash: PointLight2D
var _flash_left: float = 0.0
var _t: float = 0.0


func setup(player: Node2D) -> void:
	_player = player
	var dark: CanvasModulate = CanvasModulate.new()
	dark.color = Balance.HD_AMBIENT
	add_child(dark)
	var moon: DirectionalLight2D = DirectionalLight2D.new()
	moon.color = Balance.HD_MOON_COLOR
	moon.energy = Balance.HD_MOON_ENERGY
	moon.height = Balance.HD_MOON_HEIGHT
	moon.rotation_degrees = Balance.HD_MOON_ANGLE_DEG
	add_child(moon)
	_light = _make_light(Balance.HD_PLAYER_LIGHT_RADIUS, Balance.HD_PLAYER_LIGHT_COLOR, Balance.HD_PLAYER_LIGHT_ENERGY)
	_flash = _make_light(Balance.HD_FLASH_RADIUS, Balance.HD_FLASH_COLOR, 0.0)
	var layer: CanvasLayer = CanvasLayer.new()
	layer.layer = 0   # над миром, под HUD (у HUD слой выше)
	add_child(layer)
	var rect: ColorRect = ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = OVERLAY
	mat.set_shader_parameter(&"vignette", Balance.HD_VIGNETTE)
	mat.set_shader_parameter(&"grain", Balance.HD_GRAIN)
	mat.set_shader_parameter(&"fog", Balance.HD_FOG)
	rect.material = mat
	layer.add_child(rect)
	EventBus.weapon_fired.connect(func(_k: StringName, _w: StringName) -> void: _flash_left = Balance.HD_FLASH_SEC)


func _make_light(radius: float, color: Color, energy: float) -> PointLight2D:
	var grad: Gradient = Gradient.new()
	grad.offsets = PackedFloat32Array([0.0, 0.35, 0.7, 1.0])
	grad.colors = PackedColorArray([Color(1, 1, 1, 1), Color(0.75, 0.75, 0.75, 1), Color(0.25, 0.25, 0.25, 1), Color(0, 0, 0, 1)])
	var tex: GradientTexture2D = GradientTexture2D.new()
	tex.gradient = grad
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 256
	tex.height = 256
	var light: PointLight2D = PointLight2D.new()
	light.texture = tex
	light.texture_scale = radius * 2.0 / 256.0
	light.color = color
	light.energy = energy
	light.height = Balance.HD_PLAYER_LIGHT_HEIGHT
	add_child(light)
	return light


func _process(delta: float) -> void:
	if not is_instance_valid(_player):
		return
	_t += delta
	_light.global_position = _player.global_position
	_flash.global_position = _player.global_position
	# свет героя чуть дрожит, как фонарь на севших батарейках
	_light.energy = Balance.HD_PLAYER_LIGHT_ENERGY * (1.0 + 0.04 * sin(_t * 9.0) + 0.03 * sin(_t * 23.0))
	_flash_left = maxf(_flash_left - delta, 0.0)
	_flash.energy = Balance.HD_FLASH_ENERGY * _flash_left / Balance.HD_FLASH_SEC
