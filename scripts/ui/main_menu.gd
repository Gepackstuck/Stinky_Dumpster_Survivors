class_name MainMenu
extends Control
## Главное меню: «Пошла ебаторя» ведёт на кладбище, «Я ливаю» закрывает игру.

const GRAVEYARD_SCENE: String = "res://scenes/ui/graveyard.tscn"
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


func _ready() -> void:
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
	_title("ВЫЖИВАЙ. ВОНЯЙ. ПОВТОРЯЙ.", 66.0, GREY, Color.BLACK)
	_hero = Sprite2D.new()
	_hero.texture = PLAYER_TEX
	_hero.hframes = 4
	_hero.vframes = 3
	_hero.frame = 8
	_hero.scale = Vector2(2.0, 2.0)
	_hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_hero.position = Vector2(SCREEN.x * 0.5, 112.0)
	add_child(_hero)
	_start = _button("ПОШЛА ЕБАТОРИЯ", 140.0)
	_quit = _button("Я ЛИВАЮ", 176.0)
	_start.pressed.connect(func() -> void: SceneFlow.go(GRAVEYARD_SCENE, Vector2.DOWN))
	_quit.pressed.connect(func() -> void: get_tree().quit())
	_start.grab_focus()
	_title("A/D, W/S - ВЫБОР     ПРОБЕЛ - ОК", 246.0, GREY, Color.BLACK)


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
	button.position = Vector2((SCREEN.x - 160.0) * 0.5, y)
	button.size = Vector2(160.0, 26.0)
	add_child(button)
	return button


func _input(event: InputEvent) -> void:
	var step: int = 0
	if event.is_action_pressed(&"move_up") or event.is_action_pressed(&"ui_up"):
		step = -1
	elif event.is_action_pressed(&"move_down") or event.is_action_pressed(&"ui_down"):
		step = 1
	if step != 0:
		get_viewport().set_input_as_handled()
		(_quit if _start.has_focus() else _start).grab_focus()


func _process(delta: float) -> void:
	_time += delta
	_hero.position.y = 112.0 + roundf(sin(_time * 5.0))
	_hero.frame = 8 + int(_time * 4.0) % 4
