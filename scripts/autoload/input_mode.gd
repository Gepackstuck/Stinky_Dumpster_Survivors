extends Node
## Какое устройство сейчас в руках: клавиатура, геймпад Xbox или PlayStation (DualSense/DualShock) - для подсказок кнопок.
## Autoload: InputMode. hint("ПРОБЕЛ", "A - ОК") - подпись под устройство; для PlayStation A/B/X/Y -> ✕/○/□/△.
## Кнопки физически те же (Godot считает по позиции: низ/право/лево/верх), меняются только подписи.

signal changed(pad: bool)

const SONY_WORDS: Array[String] = ["ps5", "ps4", "ps3", "dualsense", "dualshock", "sony", "playstation", "wireless controller"]
const SONY_MAP: Dictionary = {"A": "✕", "B": "○", "X": "□", "Y": "△", "RB": "R1", "LB": "L1", "START": "OPTIONS"}

var pad: bool = false
var sony: bool = false


func _input(event: InputEvent) -> void:
	var now_pad: bool = pad
	var now_sony: bool = sony
	if event is InputEventJoypadButton or (event is InputEventJoypadMotion and absf((event as InputEventJoypadMotion).axis_value) > 0.5):
		now_pad = true
		now_sony = is_sony(Input.get_joy_name(event.device))
	elif event is InputEventKey or event is InputEventMouseButton:
		now_pad = false
	if now_pad != pad or now_sony != sony:
		pad = now_pad
		sony = now_sony
		changed.emit(pad)


static func is_sony(joy_name: String) -> bool:
	var low: String = joy_name.to_lower()
	for w: String in SONY_WORDS:
		if low.contains(w):
			return true
	return false


## Подпись под устройство: клавиатурный текст или геймпадный (буквы Xbox, для PlayStation - значки).
func hint(keyboard: String, gamepad: String) -> String:
	if not pad:
		return keyboard
	return to_sony(gamepad) if sony else gamepad


## A/B/X/Y/RB/LB/START как отдельные слова -> значки PlayStation.
static func to_sony(text: String) -> String:
	var re: RegEx = RegEx.create_from_string("(?<![A-Za-zА-Яа-я])(START|RB|LB|A|B|X|Y)(?![A-Za-zА-Яа-я])")
	var out: String = text
	var shift: int = 0
	for m: RegExMatch in re.search_all(text):
		var rep: String = SONY_MAP[m.get_string(1)]
		out = out.substr(0, m.get_start(1) + shift) + rep + out.substr(m.get_end(1) + shift)
		shift += rep.length() - m.get_string(1).length()
	return out
