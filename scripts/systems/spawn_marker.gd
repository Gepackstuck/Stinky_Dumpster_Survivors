class_name SpawnMarker
extends Sprite2D
## Красный крест на месте будущего появления врага. Через SPAWN_MARKER_SEC испускает expired и исчезает.

signal expired(marker: SpawnMarker)

const TEXTURE: Texture2D = preload("res://assets/sprites/spawn_marker.png")
const BLINK_SEC: float = 0.12

var enemy_id: StringName = &""
var hp_mult: float = 1.0
var _time_left: float = Balance.SPAWN_MARKER_SEC
var _blink_left: float = BLINK_SEC


func _init() -> void:
	texture = TEXTURE
	hframes = 2
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	z_index = -1


func _process(delta: float) -> void:
	_blink_left -= delta
	if _blink_left <= 0.0:
		_blink_left = BLINK_SEC
		frame = (frame + 1) % hframes
	_time_left -= delta
	if _time_left <= 0.0:
		set_process(false)
		expired.emit(self)
		queue_free()
