extends Node
## Какое устройство сейчас в руках (клавиатура или геймпад) - для подсказок кнопок.
## Autoload: InputMode. hint("ПРОБЕЛ", "A") - вернёт нужную подпись. Сигнал changed - перерисовать подсказки.

signal changed(pad: bool)

var pad: bool = false


func _input(event: InputEvent) -> void:
	var now_pad: bool = pad
	if event is InputEventJoypadButton or (event is InputEventJoypadMotion and absf((event as InputEventJoypadMotion).axis_value) > 0.5):
		now_pad = true
	elif event is InputEventKey or event is InputEventMouseButton:
		now_pad = false
	if now_pad != pad:
		pad = now_pad
		changed.emit(pad)


func hint(keyboard: String, gamepad: String) -> String:
	return gamepad if pad else keyboard
