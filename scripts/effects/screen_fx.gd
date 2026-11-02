class_name ScreenFx
extends CanvasLayer
## Экранные эффекты под HUD: тёмные углы всегда и красная пульсация краёв при уроне по герою.

const SHADER: Shader = preload("res://shaders/screen_fx.gdshader")

var _rect: ColorRect
var _hurt: float = 0.0


func _ready() -> void:
	layer = 3   # над миром, под фильтрами модификаторов (4) и HUD (5)
	_rect = ColorRect.new()   # холст под шейдер (сам не виден)
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat: ShaderMaterial = ShaderMaterial.new()
	mat.shader = SHADER
	_rect.material = mat
	add_child(_rect)
	EventBus.player_hit.connect(func(_d: float) -> void: _hurt = 1.0)


func _process(delta: float) -> void:
	_hurt = move_toward(_hurt, 0.0, delta * 3.0)
	var mat: ShaderMaterial = _rect.material as ShaderMaterial
	mat.set_shader_parameter(&"hurt", _hurt)
	mat.set_shader_parameter(&"screen_px", get_viewport().get_visible_rect().size)
