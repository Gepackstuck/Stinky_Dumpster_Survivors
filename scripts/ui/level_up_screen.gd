class_name LevelUpScreen
extends CanvasLayer
## Экран между волнами. Сначала карточки статов за каждый новый уровень (4 карточки, тиры I-IV, реролл),
## потом Ларёк: 4 товара за говно (оружие и перки), заморозка, реролл, шесть слотов оружия со скрещиванием и переработкой.
## В начале забега — выбор стартового оружия. Управление: A/D, W/S, пробел/E, цифры 1-4, F (заморозить), R (реролл).

@onready var _cards: Array[PerkCard] = [$Root/Cards/Card1, $Root/Cards/Card2, $Root/Cards/Card3, $Root/Cards/Card4]
@onready var _root: Control = $Root
@onready var _title: Label = $Root/Title
@onready var _counter: Label = $Root/Counter
@onready var _toast_label: Label = $Root/Empty
@onready var _next_button: Button = $Root/NextButton
@onready var _reroll_button: Button = $Root/RerollButton
@onready var _coins: Label = $Root/Coins
@onready var _hint: Label = $Root/Hint
@onready var _slots_box: HBoxContainer = $Root/Slots
@onready var _slot_info: Label = $Root/SlotInfo
@onready var _backdrop: TextureRect = $Root/Backdrop

const HINT_CARDS: String = "A/D - ВЫБОР   ПРОБЕЛ/E - ВЗЯТЬ   1-4 - БЫСТРО   W - РЕРОЛЛ"
const HINT_START: String = "A/D - ВЫБОР   ПРОБЕЛ/E - ВЗЯТЬ   1-4 - БЫСТРО"
const HINT_SHOP: String = "A/D - ВЫБОР   ПРОБЕЛ/E - КУПИТЬ   F - ЗАМОРОЗИТЬ   W - РЕРОЛЛ   S - В БОЙ"

var _queue: Array[int] = []            # уровни, за которые ещё не выбран стат
var _stat_offers: Array[Dictionary] = []
var _selected: int = 0                 # позиция среди видимых карточек
var _zone: int = 0                     # 0 — карточки, 1 — нижний ряд (реролл, «в бой», слоты оружия)
var _bottom_index: int = 0
var _start_mode: bool = false
var _shop_mode: bool = false
var _slot_buttons: Array[Button] = []
var _toast_id: int = 0
var _menu: PanelContainer = null        # контекстное меню слота оружия
var _menu_buttons: Array[Button] = []   # [объединить, переработать, назад]
var _menu_slot: int = -1
const COUNTER_COLOR: Color = Color(1.0, 0.78, 0.98)  # подпись под заголовком (после remove override она становилась тёмной)
const BACKDROP_SHOP: Color = Color(0.32, 0.28, 0.3)
const BACKDROP_LEVEL: Color = Color(0.3, 0.1, 0.34)
var _counter_base: String = ""
var _item_grid: GridContainer = null     # рюкзак предметов (слева внизу в Ларьке)
const ITEM_GRID_COLUMNS: int = 7
const ITEM_GRID_MAX: int = 14


func _ready() -> void:
	_root.hide()
	for i: int in _cards.size():
		_cards[i].pressed.connect(_on_card_pressed.bind(i))
		_cards[i].mouse_entered.connect(_select_card.bind(i))  # мышь — запасной вариант
	_build_slot_buttons()
	_build_item_grid()
	_build_slot_menu()
	_next_button.pressed.connect(_on_next_pressed)
	_reroll_button.pressed.connect(_on_reroll_pressed)
	EventBus.player_leveled_up.connect(_on_leveled_up)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.run_won.connect(func() -> void: _root.hide())
	EventBus.player_died.connect(_on_player_died)
	_show_start_choice.call_deferred()


func _build_slot_menu() -> void:
	_menu = PanelContainer.new()
	var panel_box: StyleBoxFlat = StyleBoxFlat.new()
	panel_box.bg_color = Color(0.03, 0.02, 0.04)
	panel_box.border_color = Color(1.0, 0.0627, 0.94)
	panel_box.set_border_width_all(2)
	panel_box.set_content_margin_all(4.0)
	_menu.add_theme_stylebox_override(&"panel", panel_box)
	_menu.z_index = 20
	_menu.hide()
	var column: VBoxContainer = VBoxContainer.new()
	column.add_theme_constant_override(&"separation", 2)
	_menu.add_child(column)
	for index: int in 3:
		var button: Button = Button.new()
		button.custom_minimum_size = Vector2(130.0, 14.0)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
		button.add_theme_color_override(&"font_hover_color", Color(0.968627, 1.0, 0.0))
		button.add_theme_color_override(&"font_focus_color", Color(0.968627, 1.0, 0.0))
		button.add_theme_color_override(&"font_pressed_color", Color(0.968627, 1.0, 0.0))
		button.add_theme_color_override(&"font_disabled_color", Color(0.28, 0.28, 0.3))  # недоступно — тёмная надпись
		for state: StringName in [&"normal", &"hover", &"pressed", &"disabled", &"focus"]:
			var box: StyleBoxFlat = StyleBoxFlat.new()
			box.bg_color = Color(0.13, 0.1, 0.0) if state == &"focus" else Color(0.03, 0.02, 0.04)
			box.border_color = Color(0.968627, 1.0, 0.0) if state == &"focus" else Color(0.03, 0.02, 0.04)
			box.set_border_width_all(1)
			box.set_content_margin_all(2.0)
			button.add_theme_stylebox_override(state, box)
		button.pressed.connect(_on_menu_pressed.bind(index))
		column.add_child(button)
		_menu_buttons.append(button)
	_root.add_child(_menu)


func _build_item_grid() -> void:
	_item_grid = GridContainer.new()
	_item_grid.columns = ITEM_GRID_COLUMNS
	_item_grid.position = Vector2(8.0, 224.0)
	_item_grid.add_theme_constant_override(&"h_separation", 0)
	_item_grid.add_theme_constant_override(&"v_separation", 0)
	_item_grid.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(_item_grid)


## Рюкзак: иконка каждого предмета, число штук справа внизу, рамка цветом тира.
func _refresh_items() -> void:
	for child: Node in _item_grid.get_children():
		child.queue_free()
	_item_grid.visible = _shop_mode
	var shown: int = 0
	for item_id: StringName in GameState.items:
		if shown >= ITEM_GRID_MAX:
			break
		shown += 1
		var cell: Control = Control.new()
		cell.custom_minimum_size = Vector2(16.0, 16.0)
		cell.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var icon: TextureRect = TextureRect.new()
		icon.texture = ItemLibrary.icon(item_id)
		icon.size = Vector2(16.0, 16.0)
		icon.modulate = Color.WHITE.lerp(StatLibrary.tier_color(ItemLibrary.tier(item_id)), 0.25)
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		cell.add_child(icon)
		var count: int = GameState.items[item_id]
		if count > 1:
			var label: Label = Label.new()
			label.text = str(count)
			label.position = Vector2(8.0, 6.0)
			label.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
			label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
			label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			cell.add_child(label)
		_item_grid.add_child(cell)


func _build_slot_buttons() -> void:
	for i: int in Balance.WEAPON_SLOTS:
		var button: Button = Button.new()
		button.custom_minimum_size = Vector2(19.0, 19.0)
		button.expand_icon = true
		button.focus_entered.connect(_update_slot_info.bind(i))
		button.pressed.connect(_on_slot_pressed.bind(i))
		_slots_box.add_child(button)
		_slot_buttons.append(button)


func _input(event: InputEvent) -> void:
	if not _root.visible:
		return
	if _menu.visible:
		_menu_input(event)
		return
	if event.is_action_pressed(&"move_left"):
		get_viewport().set_input_as_handled()
		_move_sideways(-1)
	elif event.is_action_pressed(&"move_right"):
		get_viewport().set_input_as_handled()
		_move_sideways(1)
	elif event.is_action_pressed(&"move_down") and not _start_mode:
		get_viewport().set_input_as_handled()
		if _zone == 0:
			_focus_bottom(0)
		elif _zone == 2:
			_zone = 0
			_select(_selected)
	elif event.is_action_pressed(&"move_up") and not _start_mode:
		get_viewport().set_input_as_handled()
		if _zone == 1:
			_zone = 0
			_select(_selected)
		elif _zone == 0:
			_focus_top()
	elif event is InputEventKey and event.pressed and not event.echo:
		var code: Key = (event as InputEventKey).physical_keycode
		if code == KEY_R and not _start_mode:
			get_viewport().set_input_as_handled()
			_on_reroll_pressed()
		elif code == KEY_F and _shop_mode and _zone == 0:
			get_viewport().set_input_as_handled()
			_toggle_lock()
	for i: int in _cards.size():
		if event.is_action_pressed(StringName("pick_card_%d" % (i + 1))) and _cards[i].visible:
			get_viewport().set_input_as_handled()
			_on_card_pressed(i)
			return


## Меню слота: W/S между доступными пунктами, Esc или «Назад» — закрыть. Остальное не пускаем.
func _menu_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		_close_menu()
	elif event.is_action_pressed(&"move_up") or event.is_action_pressed(&"move_down"):
		get_viewport().set_input_as_handled()
		var enabled: Array[Button] = []
		for button: Button in _menu_buttons:
			if not button.disabled:
				enabled.append(button)
		var current: int = 0
		for i: int in enabled.size():
			if enabled[i].has_focus():
				current = i
		var step: int = -1 if event.is_action_pressed(&"move_up") else 1
		enabled[posmod(current + step, enabled.size())].grab_focus()
	elif event.is_action_pressed(&"move_left") or event.is_action_pressed(&"move_right") or event is InputEventKey and event.pressed and not event.echo:
		if not event.is_action_pressed(&"ui_accept") and not event.is_action_pressed(&"ui_cancel"):
			get_viewport().set_input_as_handled()


func _open_menu(slot: int) -> void:
	_menu_slot = slot
	var entry: Dictionary = GameState.weapons[slot]
	var can_merge: bool = GameState.find_merge_partner(slot) >= 0
	var can_recycle: bool = GameState.weapons.size() > 1
	_menu_buttons[0].text = "ОБЪЕДИНИТЬ: ТИР %s" % StatLibrary.TIER_NAMES[mini(entry["tier"], 3)] if can_merge else "ОБЪЕДИНИТЬ"
	_menu_buttons[0].disabled = not can_merge
	_menu_buttons[1].text = "ПЕРЕРАБОТАТЬ: +%d" % GameState.weapon_recycle_value(slot)
	_menu_buttons[1].disabled = not can_recycle
	_menu_buttons[2].text = "НАЗАД"
	_menu.show()
	var slot_rect: Rect2 = _slot_buttons[slot].get_global_rect()
	_menu.reset_size()
	_menu.position = Vector2(clampf(slot_rect.position.x - 100.0, 6.0, 480.0 - _menu.size.x - 6.0), slot_rect.position.y - _menu.size.y - 4.0)
	for button: Button in _menu_buttons:
		if not button.disabled:
			button.grab_focus()
			break


func _close_menu() -> void:
	_menu.hide()
	_menu_slot = -1
	_refresh_shop()
	_focus_bottom(_bottom_index)


func _on_menu_pressed(index: int) -> void:
	var slot: int = _menu_slot
	if index == 0 and slot >= 0:
		GameState.merge_weapons(slot)
		_toast("ОБЪЕДИНИЛ. ПОЛУЧИЛОСЬ ЗЛЕЕ.")
	elif index == 1 and slot >= 0:
		_toast("ПЕРЕРАБОТАЛ: +%d ГОВНА." % GameState.recycle_weapon(slot))
	_menu.hide()
	_menu_slot = -1
	_refresh_shop()
	_focus_bottom(_bottom_index)


func _move_sideways(step: int) -> void:
	if _zone == 0:
		_select(_selected + step)
	elif _zone == 1:
		_focus_bottom(_bottom_index + step)


## Как в Brotato: уровни копятся во время волны, выбор — после её конца.
func _on_leveled_up(new_level: int) -> void:
	_queue.append(new_level)


func _on_wave_ended(_wave: int) -> void:
	GameState.reroll_count = 0
	GameState.shop_offers = ShopLibrary.fill_offers(GameState.shop_offers, GameState.wave + 1)
	_show_choices()


## В начале забега: выбор стартового оружия из 4.
func _show_start_choice() -> void:
	_start_mode = true
	_show_choices()


func _show_choices() -> void:
	_zone = 0
	_stat_offers.clear()
	_shop_mode = not _start_mode and _queue.is_empty()
	var frames: Array[int] = []
	for v: int in PerkCard.FRAME_VARIANTS:
		frames.append(v)
	frames.shuffle()  # у каждой карточки своя случайная рамка
	for i: int in _cards.size():
		_cards[i].visible = false
	if _start_mode:
		for i: int in PerkLibrary.START_WEAPONS.size():
			_cards[i].visible = true
			_cards[i].setup(PerkLibrary.START_WEAPONS[i], i + 1, frames[i])
	elif not _shop_mode:
		_stat_offers = StatLibrary.pick_offers(Balance.LEVEL_UP_CHOICES, _queue[0])
		for i: int in _stat_offers.size():
			_cards[i].visible = true
			_cards[i].setup_stat(_stat_offers[i]["id"], _stat_offers[i]["tier"], i + 1, frames[i])
	else:
		for i: int in mini(GameState.shop_offers.size(), _cards.size()):
			var offer: Dictionary = GameState.shop_offers[i]
			if offer["sold"]:
				continue
			_cards[i].visible = true
			_cards[i].setup_offer(offer, i + 1, frames[i])
	_refresh_shop()
	_root.show()
	get_tree().paused = true
	if _visible_cards().is_empty():
		_focus_bottom(0)
	else:
		_select(0)


func _visible_cards() -> Array[int]:
	var result: Array[int] = []
	for i: int in _cards.size():
		if _cards[i].visible:
			result.append(i)
	return result


func _reroll_cost() -> int:
	return Balance.REROLL_BASE_COST + int(GameState.wave * Balance.REROLL_WAVE_FACTOR) + GameState.reroll_count * Balance.REROLL_STEP_COST


## Заголовок, счётчики, кнопки и слоты оружия под текущий режим.
func _refresh_shop() -> void:
	_coins.text = "ГОВНА: %d" % GameState.coins
	_coins.visible = not _start_mode
	_toast_label.text = ""
	_counter.add_theme_color_override(&"font_color", COUNTER_COLOR)
	_refresh_slots()
	_refresh_items()
	if _start_mode:
		_title.text = "ВЫБЕРИ СВОЮ ХУЙНЮ"
		_title.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
		_backdrop.modulate = BACKDROP_SHOP
		_counter_base = "ЭТИМ ТЫ БУДЕШЬ УБИВАТЬ"
		_counter.text = _counter_base
		_hint.text = HINT_START
		_next_button.hide()
		_reroll_button.hide()
		_slots_box.hide()
		_slot_info.text = ""
		return
	_next_button.visible = _shop_mode
	_reroll_button.show()
	_reroll_button.text = "РЕРОЛЛ %d" % _reroll_cost()
	_reroll_button.disabled = GameState.coins < _reroll_cost()
	_slots_box.visible = _shop_mode
	var next_wave: int = GameState.wave + 1
	var kind: StringName = GameState.special_waves.get(next_wave, &"normal")
	var label: String = {&"elite": ": ЭЛИТА!", &"horde": ": ОРДА!", &"boss": ": БОССЫ!"}.get(kind, "")
	if _shop_mode:
		_title.text = "ЛАРЁК"
		_title.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
		_backdrop.modulate = BACKDROP_SHOP
		_counter_base = "ВОЛНА %d ПРОЙДЕНА. ТРАТЬ ГОВНО, ПОКА ЖИВОЙ" % GameState.wave
		_hint.text = HINT_SHOP
		_next_button.text = "В БОЙ: ВОЛНА %d%s" % [next_wave, label]
		_next_button.disabled = false
	else:
		_title.text = "УРОВЕНЬ %d!" % _queue[0]
		_title.add_theme_color_override(&"font_color", Color(1.0, 0.0627, 0.94))
		_backdrop.modulate = BACKDROP_LEVEL
		_counter_base = "ВЫБЕРИ УЛУЧШЕНИЕ. ВСЕГО ВЫБОРОВ: %d" % _queue.size()
		_hint.text = HINT_CARDS
		_next_button.text = "ВОЛНА %d%s" % [next_wave, label]
		_next_button.disabled = true
	_counter.text = _counter_base


func _refresh_slots() -> void:
	for i: int in _slot_buttons.size():
		var button: Button = _slot_buttons[i]
		var filled: bool = i < GameState.weapons.size()
		button.disabled = not filled
		button.focus_mode = Control.FOCUS_ALL if filled else Control.FOCUS_NONE
		var border: Color = Color(0.25, 0.25, 0.3)
		if filled:
			var entry: Dictionary = GameState.weapons[i]
			button.icon = PerkLibrary.icon(ShopLibrary.perk_id_of(entry["id"]))
			border = StatLibrary.tier_color(entry["tier"])
		else:
			button.icon = null
		for state: StringName in [&"normal", &"hover", &"pressed", &"disabled", &"focus"]:
			var box: StyleBoxFlat = StyleBoxFlat.new()
			box.bg_color = Color(0.04, 0.03, 0.05)
			box.border_color = Color(0.97, 1.0, 0.0) if state == &"focus" else border
			box.set_border_width_all(2 if state == &"focus" else 1)
			button.add_theme_stylebox_override(state, box)


func _bottom_items() -> Array[Control]:
	var items: Array[Control] = []
	if _next_button.visible and not _next_button.disabled:
		items.append(_next_button)
	if _slots_box.visible:
		for i: int in GameState.weapons.size():
			items.append(_slot_buttons[i])
	return items


## Реролл вынесен наверх (W с карточек), чтобы не перепутать его с «В бой».
func _focus_top() -> void:
	if _reroll_button.visible and not _reroll_button.disabled:
		_zone = 2
		_reroll_button.grab_focus()
		_slot_info.text = ""
	elif _reroll_button.visible:
		_on_reroll_pressed()  # не хватает говна: тряска и сообщение


func _focus_bottom(index: int) -> void:
	var items: Array[Control] = _bottom_items()
	if items.is_empty():
		return
	_zone = 1
	_bottom_index = posmod(index, items.size())
	items[_bottom_index].grab_focus()
	if not (items[_bottom_index] in _slot_buttons):
		_slot_info.text = ""


func _update_slot_info(i: int) -> void:
	if i >= GameState.weapons.size():
		_slot_info.text = ""
		return
	var entry: Dictionary = GameState.weapons[i]
	_slot_info.text = "%s ТИР %s. E: МЕНЮ" % [PerkLibrary.title(ShopLibrary.perk_id_of(entry["id"])), StatLibrary.TIER_NAMES[entry["tier"] - 1]]


func _on_next_pressed() -> void:
	_shop_mode = false
	_root.hide()
	get_tree().paused = false
	EventBus.next_wave_requested.emit()


func _on_reroll_pressed() -> void:
	if _start_mode or not _reroll_button.visible:
		return
	if _reroll_button.disabled:
		_toast("НА РЕРОЛЛ НЕ ХВАТАЕТ ГОВНА, БОМЖ.")
		_shake_node(_reroll_button, 4.0)
		_flash_coins()
		return
	GameState.coins -= _reroll_cost()
	GameState.reroll_count += 1
	if _shop_mode:
		GameState.shop_offers = ShopLibrary.fill_offers(GameState.shop_offers, GameState.wave + 1)
	var keep_focus: bool = _zone == 2
	_show_choices()
	if keep_focus and not _reroll_button.disabled:
		_focus_top()  # можно крутить реролл подряд


func _on_card_pressed(index: int) -> void:
	if _start_mode:
		GameState.apply_perk(PerkLibrary.START_WEAPONS[index])
		_start_mode = false
		_root.hide()
		get_tree().paused = false
		return
	if _shop_mode:
		var offer: Dictionary = GameState.shop_offers[index]
		var reason: String = ShopLibrary.why_not(offer)
		if reason != "":
			_toast(reason)
			_shake_node(_cards[index], 5.0)
			if GameState.coins < offer["price"]:
				_flash_coins()
			return
		ShopLibrary.buy(offer)
		var kept: int = _selected
		_show_choices()
		_select(mini(kept, maxi(_visible_cards().size() - 1, 0)))
		_toast("КУПИЛ: %s. ГОРДИСЬ." % ShopLibrary.title(offer))
		return
	var stat: Dictionary = _stat_offers[index]
	GameState.apply_stat(stat["id"], stat["tier"])
	_queue.pop_front()
	_show_choices()


func _toggle_lock() -> void:
	var visible_cards: Array[int] = _visible_cards()
	if visible_cards.is_empty():
		return
	var index: int = visible_cards[_selected]
	var offer: Dictionary = GameState.shop_offers[index]
	offer["locked"] = not offer["locked"]
	_cards[index].setup_offer(offer, index + 1, randi() % PerkCard.FRAME_VARIANTS)
	_toast("ЗАМОРОЖЕНО. ПЕРЕЖИВЁТ ВОЛНУ." if offer["locked"] else "РАЗМОРОЗИЛ.")


func _on_slot_pressed(i: int) -> void:
	if i < GameState.weapons.size():
		_open_menu(i)


func _on_player_died() -> void:
	_queue.clear()
	_root.hide()


## Короткое сообщение под заголовком (жёсткая фраза); само гаснет.
func _toast(text: String) -> void:
	_toast_id += 1
	var my_id: int = _toast_id
	_counter.text = text
	_counter.add_theme_color_override(&"font_color", Color(1.0, 0.1, 0.2))
	_coins.text = "ГОВНА: %d" % GameState.coins
	await get_tree().create_timer(1.8, true).timeout
	if my_id == _toast_id:
		_counter.text = _counter_base
		_counter.add_theme_color_override(&"font_color", COUNTER_COLOR)


## Подсветить карточку по позиции среди видимых (A/D). Пробел/E берёт её — это делает сама кнопка в фокусе.
func _select(position: int) -> void:
	var visible_cards: Array[int] = _visible_cards()
	if visible_cards.is_empty():
		return
	_selected = posmod(position, visible_cards.size())
	_cards[visible_cards[_selected]].grab_focus()


func _select_card(card_index: int) -> void:
	var position: int = _visible_cards().find(card_index)
	if position >= 0 and _zone == 0:
		_select(position)


## Тряска ноды по горизонтали (отказ покупки). Исходную позицию помним, чтобы повторные тряски не уводили её.
func _shake_node(node: Control, amplitude: float = 4.0) -> void:
	if not node.has_meta(&"shake_x"):
		node.set_meta(&"shake_x", node.position.x)
	var origin: float = node.get_meta(&"shake_x")
	var tween: Tween = create_tween()
	for i: int in 8:
		tween.tween_property(node, "position:x", origin + (amplitude if i % 2 == 0 else -amplitude), 0.045)
	tween.tween_property(node, "position:x", origin, 0.045)
	tween.tween_callback(node.remove_meta.bind(&"shake_x"))


## Говно мигает красным и трясётся секунду: «тебе не хватает».
func _flash_coins() -> void:
	_shake_node(_coins, 3.0)
	var tween: Tween = create_tween()
	for i: int in 4:
		tween.tween_callback(_coins.add_theme_color_override.bind(&"font_color", Color(1.0, 0.1, 0.2)))
		tween.tween_interval(0.13)
		tween.tween_callback(_coins.add_theme_color_override.bind(&"font_color", Color(0.85, 0.55, 0.2)))
		tween.tween_interval(0.12)
