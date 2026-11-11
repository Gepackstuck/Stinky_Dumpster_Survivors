class_name FrameAnimatorComponent
extends Node
## Покадровая анимация листа спрайтов. Пиксельный стиль: 8 fps, дёргано (ART_STYLE.md). Детальный стиль: больше кадров,
## своя частота, у рядов разная длина, есть разовые ряды (удар, получение урона), после которых возвращается основной.

const PIXEL_FPS: float = 8.0

@export var sprite: Sprite2D

## Кадров в секунду (у детального стиля больше кадров и выше частота).
var fps: float = PIXEL_FPS
## false — стоим на кадре 0 (игрок в простое не дёргается).
var active: bool = true
## Ряд листа (направление): кадр = row * hframes + столбец. 0 для листов из одного ряда.
var row: int = 0
## Сколько кадров в текущем ряду (0 - весь ряд листа).
var row_frames: int = 0
var _col: int = 0
var _time: float = 0.0
var _once: bool = false
var _back_row: int = 0
var _back_frames: int = 0


func _ready() -> void:
	_time = randf() / fps  # чтобы экземпляры не дёргались в унисон


func _process(delta: float) -> void:
	if not active and not _once:
		_col = 0
		sprite.frame = row * sprite.hframes
		return
	var count: int = row_frames if row_frames > 0 else sprite.hframes
	_time += delta
	if _time >= 1.0 / fps:
		_time = fmod(_time, 1.0 / fps)
		_col += 1
		if _col >= count:
			_col = 0
			if _once:   # разовый ряд доигран - обратно к основному
				_once = false
				row = _back_row
				row_frames = _back_frames
	sprite.frame = row * sprite.hframes + _col


## Начать текущий ряд с первого кадра (замах атаки босса должен начинаться с начала анимации).
func restart() -> void:
	_col = 0
	_time = 0.0
	sprite.frame = row * sprite.hframes


## Сыграть ряд один раз и вернуться к текущему (удар, получение урона). Повторный вызов во время разового ряда того же
## вида не перезапускает его с нуля чаще, чем он доигрывает.
func play_once(once_row: int, frames: int) -> void:
	if _once and row == once_row:
		return
	if not _once:
		_back_row = row
		_back_frames = row_frames
	_once = true
	row = once_row
	row_frames = frames
	restart()


## Сбросить разовые ряды (враг из пула).
func reset() -> void:
	_once = false
	row = 0
	row_frames = 0
	_col = 0
