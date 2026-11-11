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
	if ArtStyle.is_hd():
		color.a = 0.0 if get_parent().is_in_group(&"enemies") else Balance.HD_PLAYER_RIM_ALPHA   # у врагов своя тёмная обводка; герою - тёплый ободок, чтобы не терялся
	_material.set_shader_parameter(&"outline_color", color)


## Обводка по доле здоровья: мало — моча, много — красный, полупрозрачная.
func set_outline_by_health(fraction: float) -> void:
	var c: Color = Balance.OUTLINE_LOW_HP_COLOR.lerp(Balance.OUTLINE_FULL_HP_COLOR, pow(clampf(fraction, 0.0, 1.0), Balance.OUTLINE_HP_CURVE))
	c.a = Balance.OUTLINE_ALPHA
	set_outline(c)


func flash(color: Color) -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_material.set_shader_parameter(&"flash_color", color)
	_material.set_shader_parameter(&"amount", Balance.HD_FLASH_AMOUNT if ArtStyle.is_hd() else 1.0)   # новый стиль: вспышка тонирует, а не заливает силуэт
	_tween = create_tween()
	_tween.tween_property(_material, "shader_parameter/amount", 0.0, FLASH_SEC)
