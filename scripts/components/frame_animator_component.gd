class_name FrameAnimatorComponent
extends Node
## Дёрганая покадровая анимация листа спрайтов: 8 fps, без интерполяции (ART_STYLE.md).

const FRAME_TIME_SEC: float = 1.0 / 8.0

@export var sprite: Sprite2D

## false — стоим на кадре 0 (игрок в простое не дёргается).
var active: bool = true
## Ряд листа (направление): кадр = row * hframes + столбец. 0 для листов из одного ряда.
var row: int = 0
var _col: int = 0
var _time: float = 0.0


func _ready() -> void:
	_time = randf() * FRAME_TIME_SEC  # чтобы экземпляры не дёргались в унисон


func _process(delta: float) -> void:
	if not active:
		_col = 0
		sprite.frame = row * sprite.hframes
		return
	_time += delta
	if _time >= FRAME_TIME_SEC:
		_time = fmod(_time, FRAME_TIME_SEC)
		_col = (_col + 1) % sprite.hframes
	sprite.frame = row * sprite.hframes + _col
