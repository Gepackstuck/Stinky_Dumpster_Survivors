class_name MainMenu
extends Control
## Главное меню: «Погнали» ведёт на кладбище, «Я ливаю» закрывает игру.

const GRAVEYARD_SCENE: String = "res://scenes/ui/graveyard.tscn"
const BESTIARY: GDScript = preload("res://scripts/ui/bestiary.gd")
const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const SCREEN: Vector2 = Vector2(480.0, 270.0)
const GROUND: Texture2D = preload("res://assets/sprites/ground_tile.png")
const PLAYER_TEX: Texture2D = preload("res://assets/sprites/player.png")
const YELLOW: Color = Color(0.968627, 1.0, 0.0)
const PINK: Color = Color(1.0, 0.0627451, 0.941176)
const GREEN: Color = Color(0.2235, 1.0, 0.0784)
const GREY: Color = Color(0.55, 0.55, 0.6)

var _time: float = 0.0
var _hero: Sprite2D
var _start: Button
var _quit: Button
var _bestiary_button: Button
var _bestiary: Control = null


var _settings_button: Button = null
var _daily_button: Button = null
var _settings: SettingsPanel = null


func _ready() -> void:
	AudioManager.play_music(&"shop")
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.05, 0.07, 0.05)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(back)
	var ground: TextureRect = TextureRect.new()
	ground.texture = GROUND
	ground.stretch_mode = TextureRect.STRETCH_TILE
	ground.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	ground.modulate = Color(0.32, 0.4, 0.3)
	ground.size = SCREEN
	ground.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(ground)
	_title("ПОМОЙКА", 26.0, YELLOW, PINK)
	_title("SURVIVORS", 44.0, GREEN, Color.BLACK)
	_title(tr("MENU_TAGLINE"), 66.0, GREY, Color.BLACK)
	_hero = Sprite2D.new()
	_hero.texture = PLAYER_TEX
	_hero.hframes = 4
	_hero.vframes = 3
	_hero.frame = 8
	_hero.scale = Vector2(2.0, 2.0)
	_hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_hero.position = Vector2(SCREEN.x * 0.5, 112.0)
	add_child(_hero)
	_start = _button(tr("MENU_PLAY"), 126.0)
	_daily_button = _button(tr("MENU_DAILY"), 150.0)
	_bestiary_button = _button(tr("MENU_BESTIARY"), 174.0)
	_settings_button = _button(tr("MENU_SETTINGS"), 198.0)
	_quit = _button(tr("MENU_QUIT"), 222.0)
	for b: Button in [_start, _daily_button, _bestiary_button, _settings_button, _quit]:
		b.size.y = 22.0
	UI_BUTTONS.skin(_daily_button, 1)
	_daily_button.pressed.connect(_start_daily)
	var best: int = int(Profile.daily_best.get(str(GameState.today_seed()), 0))
	_daily_button.text = tr("MENU_DAILY") + (" (%d)" % best if best > 0 else "")
	UI_BUTTONS.skin(_start, 0)
	UI_BUTTONS.skin(_bestiary_button, 2)
	UI_BUTTONS.skin(_settings_button, 3)
	UI_BUTTONS.skin(_quit, 4)
	_settings_button.pressed.connect(_open_settings)
	_bestiary_button.pressed.connect(_open_bestiary)
	_start.pressed.connect(func() -> void:
		GameState.daily = false
		SceneFlow.go(GRAVEYARD_SCENE, Vector2.DOWN))
	_quit.pressed.connect(func() -> void: get_tree().quit())
	UI_BUTTONS.add_focus_arrows([_start, _daily_button, _bestiary_button, _settings_button, _quit])
	_start.grab_focus()
	_title(tr("MENU_HINT"), 246.0, GREY, Color.BLACK)


func _title(text: String, y: float, color: Color, shadow: Color) -> Label:
	var label: Label = Label.new()
	label.text = text
	label.position = Vector2(0.0, y)
	label.size = Vector2(SCREEN.x, 12.0)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", shadow)
	label.add_theme_constant_override(&"shadow_offset_x", 1)
	label.add_theme_constant_override(&"shadow_offset_y", 1)
	add_child(label)
	return label


func _button(text: String, y: float) -> Button:
	var button: Button = Button.new()
	button.text = text
	button.position = Vector2((SCREEN.x - 180.0) * 0.5, y)
	button.size = Vector2(180.0, 28.0)
	add_child(button)
	return button


## Ежедневка: герой дня, опасность ГНИЛЬ, один сид на всех - сразу на арену.
func _start_daily() -> void:
	GameState.daily = true
	GameState.daily_seed = GameState.today_seed()
	GameState.character = Balance.CHARACTER_ORDER[GameState.daily_seed % Balance.CHARACTER_ORDER.size()]
	GameState.danger = Balance.DAILY_DANGER
	SceneFlow.go("res://scenes/levels/main.tscn", Vector2.DOWN)


func _open_settings() -> void:
	_settings = SettingsPanel.new()
	_settings.closed.connect(func() -> void:
		_settings.queue_free()
		_settings = null
		_settings_button.grab_focus())
	add_child(_settings)


func _open_bestiary() -> void:
	_bestiary = BESTIARY.new()
	_bestiary.closed.connect(func() -> void:
		_bestiary.queue_free()
		_bestiary = null
		_bestiary_button.grab_focus())
	add_child(_bestiary)


func _input(event: InputEvent) -> void:
	if _bestiary != null or _settings != null:
		return
	var step: int = 0
	if event.is_action_pressed(&"move_up") or event.is_action_pressed(&"ui_up"):
		step = -1
	elif event.is_action_pressed(&"move_down") or event.is_action_pressed(&"ui_down"):
		step = 1
	if step != 0:
		get_viewport().set_input_as_handled()
		var order: Array[Button] = [_start, _daily_button, _bestiary_button, _settings_button, _quit]
		var at: int = 0
		for i: int in order.size():
			if order[i].has_focus():
				at = i
		order[posmod(at + step, order.size())].grab_focus()


func _process(delta: float) -> void:
	_time += delta
	_hero.position.y = 112.0 + roundf(sin(_time * 5.0))
	_hero.frame = 8 + int(_time * 4.0) % 4
