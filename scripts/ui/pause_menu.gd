class_name PauseMenu
extends CanvasLayer
## Простейшее меню паузы по Esc: продолжить / заново / выйти.

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const PANELS: Texture2D = preload("res://assets/ui/death_panels.png")
const PANEL_SIZE: Vector2 = Vector2(360.0, 160.0)
const PANEL_VARIANTS: int = 4

@onready var _root: Control = $Root
@onready var _panel: TextureRect = $Root/Panel
@onready var _resume: Button = $Root/Resume
@onready var _inventory_button: Button = $Root/Inventory
@onready var _restart: Button = $Root/Restart
@onready var _quit: Button = $Root/Quit

var _menu_button: Button = null
var _confirm: Control = null
var _confirm_yes: Button = null
var _confirm_no: Button = null
var _confirm_text: Label = null
var _confirm_action: Callable = Callable()
var _confirm_return: Button = null
var _inventory: Control = null
var _inventory_text: Label = null
var _inventory_items: GridContainer = null
var _inventory_weapons: HBoxContainer = null


func _ready() -> void:
	_root.hide()
	_resume.pressed.connect(_close)
	_restart.pressed.connect(_on_restart)
	_inventory_button.pressed.connect(_open_inventory)
	_build_inventory()
	_quit.pressed.connect(func() -> void: _ask("ТОЧНО ВЫЙТИ ИЗ ИГРЫ?\nВСЁ ЗАКРОЕТСЯ, ПРОГРЕСС ЗАБЕГА\nПОХЕРИТСЯ.", "ДА, ВАЛЮ ОТСЮДА", func() -> void: get_tree().quit()))
	_build_menu_button()
	_build_confirm()


## Пятая кнопка «В главное меню» (с подтверждением) - кнопки сдвигаются теснее.
func _build_menu_button() -> void:
	var ys: Array[float] = [92.0, 111.0, 130.0, 149.0, 190.0]   # перед «валить» большой отступ: кнопка опасная
	var order: Array[Button] = [_resume, _inventory_button, _restart, null, _quit]
	_menu_button = Button.new()
	_menu_button.text = "В ГЛАВНОЕ МЕНЮ"
	_menu_button.size = _quit.size
	var skinned: Array[Button] = [_resume, _inventory_button, _restart, _menu_button, _quit]
	for i: int in skinned.size():
		UI_BUTTONS.skin(skinned[i], i)
	_root.add_child(_menu_button)
	order[3] = _menu_button
	for i: int in order.size():
		order[i].position = Vector2(order[i].position.x if i != 3 else _quit.position.x, ys[i])
		order[i].size.y = 18.0
	_menu_button.pressed.connect(func() -> void: _ask("ТОЧНО В МЕНЮ?\nВЕСЬ ПРОГРЕСС ЗАБЕГА\nПОХЕРИТСЯ.", "ДА, ПОХЕРИТЬ", func() -> void: SceneFlow.go("res://scenes/ui/main_menu.tscn", Vector2.UP)))
	_quit.text = "! ВАЛИТЬ ОТСЮДА !"
	_quit.add_theme_color_override(&"font_color", Color(1.0, 0.1, 0.2))
	_quit.add_theme_color_override(&"font_hover_color", Color(1.0, 0.1, 0.2))
	_quit.add_theme_color_override(&"font_focus_color", Color(1.0, 1.0, 1.0))
	UI_BUTTONS.skin_danger(_quit)


## Спросить подтверждение: текст, подпись «да» и действие.
func _ask(question: String, yes_text: String, action: Callable) -> void:
	_confirm_text.text = question
	_confirm_yes.text = yes_text
	_confirm_action = action
	_confirm_return = _menu_button if _menu_button.has_focus() else _quit
	_confirm.show()
	_confirm_no.grab_focus()


func _build_confirm() -> void:
	_confirm = Control.new()
	_confirm.set_anchors_preset(Control.PRESET_FULL_RECT)
	_confirm.hide()
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.03, 0.02, 0.04, 0.96)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	_confirm.add_child(back)
	var text: Label = Label.new()
	_confirm_text = text
	text.position = Vector2(0.0, 80.0)
	text.size = Vector2(480.0, 50.0)
	text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	text.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
	_confirm.add_child(text)
	_confirm_yes = Button.new()
	_confirm_yes.text = "ДА, ПОХЕРИТЬ"
	_confirm_yes.position = Vector2(100.0, 150.0)
	_confirm_yes.size = Vector2(130.0, 22.0)
	UI_BUTTONS.skin(_confirm_yes, 4)
	_confirm.add_child(_confirm_yes)
	_confirm_no = Button.new()
	_confirm_no.text = "НЕТ, ЕЩЁ ПОЖИВУ"
	_confirm_no.position = Vector2(250.0, 150.0)
	_confirm_no.size = Vector2(130.0, 22.0)
	UI_BUTTONS.skin(_confirm_no, 0)
	_confirm.add_child(_confirm_no)
	_root.add_child(_confirm)
	_confirm_yes.pressed.connect(func() -> void: _confirm_action.call())
	_confirm_no.pressed.connect(func() -> void:
		_confirm.hide()
		_confirm_return.grab_focus())


func _input(event: InputEvent) -> void:
	if not _root.visible:
		return
	if _confirm.visible:
		if event.is_action_pressed(&"move_left") or event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_left") or event.is_action_pressed(&"ui_right"):
			get_viewport().set_input_as_handled()
			(_confirm_no if _confirm_yes.has_focus() else _confirm_yes).grab_focus()
		return
	if _inventory.visible:
		if event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"move_left") or event.is_action_pressed(&"move_right"):
			get_viewport().set_input_as_handled()
			_inventory.hide()
			_inventory_button.grab_focus()
		return
	var step: int = 0
	if event.is_action_pressed(&"move_up"):
		step = -1
	elif event.is_action_pressed(&"move_down"):
		step = 1
	if step == 0:
		return
	get_viewport().set_input_as_handled()  # W/S и стрелки — между кнопками
	var buttons: Array[Button] = [_resume, _inventory_button, _restart, _menu_button, _quit]
	var current: int = 0
	for i: int in buttons.size():
		if buttons[i].has_focus():
			current = i
	buttons[posmod(current + step, buttons.size())].grab_focus()


func _unhandled_input(event: InputEvent) -> void:
	var key: InputEventKey = event as InputEventKey
	if key == null or not key.pressed or key.echo or key.keycode != KEY_ESCAPE:
		return
	get_viewport().set_input_as_handled()
	if _confirm.visible:
		_confirm.hide()
		_confirm_return.grab_focus()
	elif _inventory.visible:
		_inventory.hide()
		_inventory_button.grab_focus()
	elif _root.visible:
		_close()
	elif not get_tree().paused and GameState.run_active and GameState.wave > 0:
		_open()


func _open() -> void:
	var panel: AtlasTexture = AtlasTexture.new()
	panel.atlas = PANELS
	panel.region = Rect2(Vector2(randi_range(0, PANEL_VARIANTS - 1) * PANEL_SIZE.x, 0.0), PANEL_SIZE)
	_panel.texture = panel
	_root.show()
	get_tree().paused = true
	_resume.grab_focus()


func _close() -> void:
	_inventory.hide()
	_root.hide()
	get_tree().paused = false


func _on_restart() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()


## Экран «хлам и статы»: статы забега слева, оружие под ними, предметы столбиком справа.
func _build_inventory() -> void:
	_inventory = Control.new()
	_inventory.set_anchors_preset(Control.PRESET_FULL_RECT)
	_inventory.hide()
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.03, 0.02, 0.04, 0.96)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	_inventory.add_child(back)
	var title: Label = Label.new()
	title.text = "ХЛАМ И СТАТЫ"
	title.position = Vector2(0.0, 6.0)
	title.size = Vector2(480.0, 14.0)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
	_inventory.add_child(title)
	_inventory_text = Label.new()
	_inventory_text.position = Vector2(12.0, 26.0)
	_inventory_text.size = Vector2(150.0, 140.0)
	_inventory_text.add_theme_color_override(&"font_color", Color(0.91, 0.91, 0.91))
	_inventory.add_child(_inventory_text)
	_inventory_weapons = HBoxContainer.new()
	_inventory_weapons.position = Vector2(12.0, 226.0)
	_inventory.add_child(_inventory_weapons)
	_inventory_items = GridContainer.new()
	_inventory_items.columns = 2
	_inventory_items.position = Vector2(170.0, 26.0)
	_inventory_items.add_theme_constant_override(&"h_separation", 6)
	_inventory_items.add_theme_constant_override(&"v_separation", 1)
	_inventory.add_child(_inventory_items)
	var hint: Label = Label.new()
	hint.text = "ESC / ПРОБЕЛ - НАЗАД"
	hint.position = Vector2(0.0, 254.0)
	hint.size = Vector2(480.0, 10.0)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.add_theme_color_override(&"font_color", Color(0.6, 0.6, 0.65))
	_inventory.add_child(hint)
	_root.add_child(_inventory)


func _open_inventory() -> void:
	var lines: Array[String] = []
	lines.append("ХП: %d/%d" % [roundi(GameState.hp), roundi(GameState.max_hp)])
	lines.append("УРОН: %+d%%" % roundi((GameState.damage_mult - 1.0) * 100.0))
	lines.append("СКОР. АТАКИ: %+d%%" % roundi((GameState.attack_speed_mult - 1.0) * 100.0))
	lines.append("КРИТ: %d%%" % roundi(GameState.crit_percent))
	lines.append("БРОНЯ: %d" % roundi(GameState.armor))
	lines.append("УВОРОТ: %d%%" % roundi(GameState.dodge_percent))
	lines.append("СКОРОСТЬ: %+d%%" % roundi((GameState.move_speed_mult - 1.0) * 100.0))
	lines.append("РЕГЕН: %.1f" % GameState.regen_hp)
	lines.append("ПОДБОР: %+d%%" % roundi((GameState.pickup_radius_mult - 1.0) * 100.0))
	lines.append("")
	lines.append("УРОВЕНЬ: %d" % GameState.level)
	lines.append("ВОЛНА: %d/%d" % [GameState.wave, Balance.WAVE_COUNT])
	lines.append("УБИТО: %d" % GameState.kills)
	lines.append("ГОВНА: %d" % GameState.coins)
	_inventory_text.text = "\n".join(lines)
	for child: Node in _inventory_items.get_children():
		child.queue_free()
	for item_id: StringName in GameState.items:
		var row: HBoxContainer = HBoxContainer.new()
		row.custom_minimum_size = Vector2(148.0, 14.0)
		var icon: TextureRect = TextureRect.new()
		icon.texture = ItemLibrary.icon(item_id)
		icon.custom_minimum_size = Vector2(14.0, 14.0)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		row.add_child(icon)
		var label: Label = Label.new()
		var count: int = GameState.items[item_id]
		label.text = ItemLibrary.title(item_id) + (" (%d)" % count if count > 1 else "")
		label.add_theme_color_override(&"font_color", StatLibrary.tier_color(ItemLibrary.tier(item_id)))
		row.add_child(label)
		_inventory_items.add_child(row)
	for child: Node in _inventory_weapons.get_children():
		child.queue_free()
	for entry: Dictionary in GameState.weapons:
		var weapon_icon: TextureRect = TextureRect.new()
		weapon_icon.texture = PerkLibrary.icon(ShopLibrary.perk_id_of(entry["id"]))
		weapon_icon.custom_minimum_size = Vector2(20.0, 20.0)
		weapon_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		weapon_icon.modulate = Color.WHITE.lerp(StatLibrary.tier_color(entry["tier"]), 0.4)
		_inventory_weapons.add_child(weapon_icon)
	_inventory.show()
