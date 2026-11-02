class_name AmbientFx
extends Node2D
## Живой фон арены: редкие мухи кружат над полом рядом с героем. Мелкие и полупрозрачные - не мешают видеть врагов.

const FLY: Texture2D = preload("res://assets/sprites/fx_fly.png")
const MAX_FLIES: int = 7
const SPAWN_SEC: float = 0.7

var _timer: float = 0.0
var _flies: Array[Sprite2D] = []


func _process(delta: float) -> void:
	_timer -= delta
	_flies.assign(_flies.filter(func(f: Sprite2D) -> bool: return is_instance_valid(f)))
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
