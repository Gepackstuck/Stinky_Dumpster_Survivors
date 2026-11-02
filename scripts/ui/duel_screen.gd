class_name DuelScreen
extends CanvasLayer
## Н31 «Битва героев» (хотсит): двое по очереди играют DUEL_WAVES волн на одном сиде (у каждого свой герой).
## Раунд кончился (смерть или прошёл все волны) - экран счёта. После второго - кто победил, а кто лох.

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")

var _shown: bool = false


func _ready() -> void:
	layer = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	EventBus.player_died.connect(func() -> void: _on_round_over.call_deferred(false))
	EventBus.duel_round_over.connect(func() -> void: _on_round_over(true))


func _on_round_over(survived: bool) -> void:
	if GameState.mode != &"duel" or _shown:
		return
	_shown = true
	get_tree().paused = true
	GameState.run_active = false
	GameState.duel_scores.append({"hero": String(GameState.character), "kills": GameState.kills, "wave": GameState.wave, "alive": survived})
	var root: Control = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var back: Panel = Panel.new()
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.03, 0.04, 0.97)
	box.border_color = Color(1.0, 0.06, 0.94)
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.position = Vector2(90.0, 50.0)
	back.size = Vector2(300.0, 170.0)
	root.add_child(back)
	var round_no: int = GameState.duel_scores.size()
	_text(root, tr("БИТВА ГЕРОЕВ"), 58.0, Color(0.97, 1.0, 0.0))
	for i: int in GameState.duel_scores.size():
		var e: Dictionary = GameState.duel_scores[i]
		_text(root, tr("ИГРОК %d (%s): %d УБИЙСТВ, ВОЛНА %d") % [i + 1, CharacterLibrary.short_title(StringName(e["hero"])), e["kills"], e["wave"]], 84.0 + i * 16.0, Color.WHITE)
	var button: Button = Button.new()
	button.position = Vector2(150.0, 186.0)
	button.size = Vector2(180.0, 22.0)
	UI_BUTTONS.skin(button, 1)
	root.add_child(button)
	if round_no < 2:
		_text(root, tr("ИГРОК 2, ТВОЯ ОЧЕРЕДЬ. ТОТ ЖЕ СИД, ВЫБЕРИ СВОЕГО ГЕРОЯ."), 130.0, Color(0.22, 1.0, 0.08))
		button.text = tr("ИГРОК 2 - НА КЛАДБИЩЕ")
		button.pressed.connect(func() -> void: SceneFlow.go("res://scenes/ui/graveyard.tscn", Vector2.DOWN))
	else:
		var a: Dictionary = GameState.duel_scores[0]
		var b: Dictionary = GameState.duel_scores[1]
		var winner: int = 1 if _score(a) >= _score(b) else 2
		_text(root, tr("ПОБЕДИЛ ИГРОК %d. ИГРОК %d - ЛОХ.") % [winner, 3 - winner], 130.0, Color(1.0, 0.06, 0.94))
		Achievements.unlock(&"duel_played")
		button.text = tr("В МЕНЮ")
		button.pressed.connect(func() -> void:
			GameState.mode = &""
			GameState.seed_word = ""
			SceneFlow.go("res://scenes/ui/main_menu.tscn", Vector2.UP))
	button.grab_focus()


static func _score(e: Dictionary) -> int:
	return int(e["kills"]) + int(e["wave"]) * 10   # убийства, при равенстве - кто дальше прошёл


func _text(root: Control, text: String, y: float, color: Color) -> void:
	var l: Label = Label.new()
	l.text = text
	l.position = Vector2(100.0, y)
	l.size = Vector2(280.0, 10.0)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	root.add_child(l)
