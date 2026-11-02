class_name AmbientFx
extends Node2D
## Живой фон арены: редкие мухи кружат над полом рядом с героем. Мелкие и полупрозрачные - не мешают видеть врагов.

const FLY: Texture2D = preload("res://assets/sprites/fx_fly.png")
const MAX_FLIES: int = 7
const SPAWN_SEC: float = 0.7

const SEASON_FX: Dictionary = {
	"snow": preload("res://assets/sprites/fx_season_snow.png"),
	"leaf": preload("res://assets/sprites/fx_season_leaf.png"),
	"rain": preload("res://assets/sprites/fx_season_rain.png"),
	"heat": preload("res://assets/sprites/fx_season_heat.png"),
	"petal": preload("res://assets/sprites/fx_season_leaf.png"),
}

var _timer: float = 0.0
var _flies: Array[Sprite2D] = []
var _weather: Array[Sprite2D] = []
var _weather_timer: float = 0.0


func _ready() -> void:
	add_child.call_deferred(WeatherHazards.new())   # лужи, сугробы, жара, подснежники
	var overlay: WeatherOverlay = WeatherOverlay.new()
	add_child(overlay)
	overlay.setup(self)


func _process(delta: float) -> void:
	_tick_weather(delta)
	_timer -= delta
	_flies.assign(_flies.filter(func(f: Variant) -> bool: return is_instance_valid(f)))
	for f: Sprite2D in _flies:
		f.frame = int(Time.get_ticks_msec() / 40) % 2
	if _timer > 0.0 or _flies.size() >= MAX_FLIES:
		return
	_timer = SPAWN_SEC
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null:
		return
	var fly: Sprite2D = Sprite2D.new()
	fly.texture = FLY
	fly.hframes = 2
	fly.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	fly.modulate = Color(1, 1, 1, 0.7)
	fly.z_index = 8
	add_child(fly)
	_flies.append(fly)
	var center: Vector2 = player.global_position + Vector2(randf_range(-200.0, 200.0), randf_range(-110.0, 110.0))
	fly.global_position = center
	var tw: Tween = fly.create_tween()
	for i: int in 6:   # дёрганый полёт восьмёрками
		tw.tween_property(fly, "global_position", center + Vector2(randf_range(-14.0, 14.0), randf_range(-10.0, 10.0)), randf_range(0.25, 0.5))
	tw.tween_property(fly, "modulate:a", 0.0, 0.3)
	tw.tween_callback(fly.queue_free)


## Погода забега: редкие снежинки, листья, капли или жаркие искры вокруг героя. Полупрозрачные, под HUD.
func _tick_weather(delta: float) -> void:
	_weather.assign(_weather.filter(func(f: Variant) -> bool: return is_instance_valid(f)))
	_weather_timer -= delta
	if _weather_timer > 0.0 or _weather.size() >= Balance.SEASON_FX_MAX:
		return
	_weather_timer = 0.05
	var kind: String = Balance.SEASONS.get(GameState.season, {}).get("fx", "")
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if kind == "" or player == null:
		return
	var tex: Texture2D = SEASON_FX[kind]
	var p: Sprite2D = Sprite2D.new()
	p.texture = tex
	var leafy: bool = kind == "leaf" or kind == "petal"
	p.hframes = 4 if leafy else 2
	p.frame = randi_range(0, p.hframes - 1) if leafy else 0
	p.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	p.modulate = Color(1.0, 0.75, 0.9, Balance.SEASON_FX_ALPHA) if kind == "petal" else Color(1, 1, 1, Balance.SEASON_FX_ALPHA)   # весной - розовые лепестки
	p.z_index = 7
	add_child(p)
	_weather.append(p)
	var top: Vector2 = player.global_position + Vector2(randf_range(-260.0, 260.0), -110.0)
	var tw: Tween = p.create_tween()
	match kind:
		"snow":
			p.global_position = top
			tw.tween_property(p, "global_position", top + Vector2(randf_range(-30.0, 30.0), 240.0), randf_range(3.5, 5.0))
		"leaf", "petal":
			p.global_position = top
			p.rotation = randf() * TAU
			tw.set_parallel(true)
			tw.tween_property(p, "global_position", top + Vector2(randf_range(40.0, 110.0), 240.0), randf_range(4.0, 6.0))
			tw.tween_property(p, "rotation", p.rotation + randf_range(-6.0, 6.0), 5.0)
			tw.set_parallel(false)
		"rain":
			p.global_position = top
			var land: Vector2 = player.global_position + Vector2(randf_range(-240.0, 240.0), randf_range(-100.0, 110.0))
			p.global_position = land + Vector2(-50.0, -150.0)
			tw.tween_property(p, "global_position", land, 0.45)
			tw.tween_callback(func() -> void: p.frame = 1)
			tw.tween_interval(0.15)
		"heat":
			var at: Vector2 = player.global_position + Vector2(randf_range(-240.0, 240.0), randf_range(-100.0, 110.0))
			p.global_position = at
			p.frame = randi() % 2
			tw.tween_property(p, "global_position", at + Vector2(randf_range(-6.0, 6.0), -26.0), 1.6)
	tw.tween_property(p, "modulate:a", 0.0, 0.3)
	tw.tween_callback(p.queue_free)
