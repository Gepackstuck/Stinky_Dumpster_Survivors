class_name HitFlashComponent
extends Node
## Мигание спрайта цветом при попадании (шейдер hit_flash). Создаёт материал сам.

const FLASH_SHADER: Shader = preload("res://assets/shaders/hit_flash.gdshader")
const FLASH_SEC: float = 0.09

@export var sprite: Sprite2D

var _material: ShaderMaterial = ShaderMaterial.new()
var _tween: Tween = null


func _ready() -> void:
	_material.shader = FLASH_SHADER
	sprite.material = _material


## Цвет внешней обводки (игрок и враги разные, чтобы читались на земле).
func set_outline(color: Color) -> void:
	_material.set_shader_parameter(&"outline_color", color)


func flash(color: Color) -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_material.set_shader_parameter(&"flash_color", color)
	_material.set_shader_parameter(&"amount", 1.0)
	_tween = create_tween()
	_tween.tween_property(_material, "shader_parameter/amount", 0.0, FLASH_SEC)
