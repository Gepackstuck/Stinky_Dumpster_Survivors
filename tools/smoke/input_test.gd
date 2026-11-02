extends Node
## ТЕСТ подписей кнопок: Xbox/PlayStation по имени геймпада и замена A/B/X/Y на значки. INPUT OK / FAIL.

func _ready() -> void:
	Profile.sandbox = true
	var fails: int = 0
	for pair: Array in [["PS5 Controller", true], ["DualSense Wireless Controller", true], ["Xbox Series Controller", false], ["Wireless Controller", true]]:
		if InputMode.is_sony(pair[0]) != pair[1]:
			fails += 1
			print("INPUT FAIL ", pair[0])
	var s: String = InputMode.to_sony("A - КУПИТЬ   X - ЗАМОРОЗИТЬ   Y - РЕРОЛЛ   RB - РЫВОК   СТРЕЛКИ - ВЫБОР")
	if s != "✕ - КУПИТЬ   □ - ЗАМОРОЗИТЬ   △ - РЕРОЛЛ   R1 - РЫВОК   СТРЕЛКИ - ВЫБОР":
		fails += 1
		print("INPUT FAIL замена: ", s)
	print("INPUT OK" if fails == 0 else "INPUT FAIL %d" % fails)
	get_tree().quit()
