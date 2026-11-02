class_name WeatherOverlay
extends CanvasLayer
## Погода волны на весь экран: рисованная кромка по краям (иней, жара, листья, подтёки)
## плюс лёгкий оттенок всего мира. Центр экрана чистый - врагов видно. Плавно появляется и уходит.

const FRAMES: Dictionary = {
	&"winter": preload("res://assets/sprites/fx_weather_winter.png"),
	&"summer": preload("res://assets/sprites/fx_weather_summer.png"),
	&"autumn": preload("res://assets/sprites/fx_weather_autumn.png"),
	&"spring": preload("res://assets/sprites/fx_weather_spring.png"),
}

var _frame: TextureRect
var _world_tint: CanvasModulate
var _shown: StringName = &""


## world - узел мира: оттенок (CanvasModulate) должен жить на холсте мира, а не в слое.
func setup(world: Node) -> void:
	layer = 2   # над миром, под вспышками (3), фильтрами модификаторов (4) и HUD (5)
	_frame = TextureRect.new()
	_frame.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_frame.size = Vector2(480.0, 270.0)
	_frame.modulate.a = 0.0
	add_child(_frame)
	_world_tint = CanvasModulate.new()
	_world_tint.color = Color.WHITE
	world.add_child(_world_tint)
	EventBus.wave_started.connect(func(_w: int) -> void: _apply())
	EventBus.wave_ended.connect(func(_w: int) -> void: _apply.call_deferred())
	_apply()


func _apply() -> void:
	var season: StringName = GameState.season
	if season == _shown:
		return
	_shown = season
	var tw: Tween = create_tween().set_parallel(true)
	if season == &"":
		tw.tween_property(_frame, ^"modulate:a", 0.0, 1.2)
		tw.tween_property(_world_tint, ^"color", Color.WHITE, 1.2)
		return
	_frame.texture = FRAMES[season]
	_frame.modulate.a = 0.0
	tw.tween_property(_frame, ^"modulate:a", 1.0, 1.0)
	tw.tween_property(_world_tint, ^"color", Balance.SEASONS[season]["world"], 1.0)
