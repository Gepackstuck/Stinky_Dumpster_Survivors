class_name FrameAnimatorComponent
extends Node
## Дёрганая покадровая анимация листа спрайтов: 8 fps, без интерполяции (ART_STYLE.md).

const FRAME_TIME_SEC: float = 1.0 / 8.0

@export var sprite: Sprite2D

var _time: float = 0.0


func _ready() -> void:
	_time = randf() * FRAME_TIME_SEC  # чтобы экземпляры не дёргались в унисон


func _process(delta: float) -> void:
	_time += delta
	if _time >= FRAME_TIME_SEC:
		_time = fmod(_time, FRAME_TIME_SEC)
		sprite.frame = (sprite.frame + 1) % sprite.hframes
