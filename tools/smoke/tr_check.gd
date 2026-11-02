extends SceneTree
## Быстрая проверка перевода: печатает пару строк на en. godot --headless -s res://tools/smoke/tr_check.gd


func _init() -> void:
	TranslationServer.set_locale("en")
	for s: String in ["ЗИМА: ДУБАК", "ГЛЮЧНЫЙ БОМЖ", "КРОКСЫ", "ЭВОЛЮЦИЯ: %s!", "MENU_PLAY"]:
		print("TR ", s, " -> ", TranslationServer.translate(s))
	quit()
