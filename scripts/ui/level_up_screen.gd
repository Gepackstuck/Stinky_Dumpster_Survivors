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

const HINT_CARDS: String = "A/D - ВЫБОР   ПРОБЕЛ/E - ВЗЯТЬ   1-4 - БЫСТРО   S - РЕРОЛЛ   W - НАЗАД"
const HINT_SHOP: String = "A/D - ВЫБОР   ПРОБЕЛ/E - КУПИТЬ   F - ЗАМОРОЗИТЬ   S/W - ВНИЗ/ВВЕРХ"

var _queue: Array[int] = []            # уровни, за которые ещё не выбран стат
var _stat_offers: Array[Dictionary] = []
var _selected: int = 0                 # позиция среди видимых карточек
var _zone: int = 0                     # 0 — карточки, 1 — нижний ряд (реролл, «в бой», слоты оружия)
var _bottom_index: int = 0
var _start_mode: bool = false
var _shop_mode: bool = false
var _slot_buttons: Array[Button] = []
var _toast_id: int = 0
var _counter_base: String = ""


func _ready() -> void:
	_root.hide()
	for i: int in _cards.size():
		_cards[i].pressed.connect(_on_card_pressed.bind(i))
		_cards[i].mouse_entered.connect(_select_card.bind(i))  # мышь — запасной вариант
	_build_slot_buttons()
	_next_button.pressed.connect(_on_next_pressed)
	_reroll_button.pressed.connect(_on_reroll_pressed)
	EventBus.player_leveled_up.connect(_on_leveled_up)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.run_won.connect(func() -> void: _root.hide())
	EventBus.player_died.connect(_on_player_died)
	_show_start_choice.call_deferred()


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
	if event.is_action_pressed(&"move_left"):
		get_viewport().set_input_as_handled()
		_move_sideways(-1)
	elif event.is_action_pressed(&"move_right"):
		get_viewport().set_input_as_handled()
		_move_sideways(1)
	elif event.is_action_pressed(&"move_down") and _zone == 0 and not _start_mode:
		get_viewport().set_input_as_handled()
		_focus_bottom(0)
	elif event.is_action_pressed(&"move_up") and _zone == 1:
		get_viewport().set_input_as_handled()
		_zone = 0
		_select(_selected)
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


func _move_sideways(step: int) -> void:
	if _zone == 0:
		_select(_selected + step)
	else:
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
		for i: int in PerkLibrary.WEAPON_PERKS.size():
			_cards[i].visible = true
			_cards[i].setup(PerkLibrary.WEAPON_PERKS[i], i + 1, frames[i])
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
		_focus_bottom(1)
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
	_counter.remove_theme_color_override(&"font_color")
	_refresh_slots()
	if _start_mode:
		_title.text = "ВЫБЕРИ СВОЮ ХУЙНЮ"
		_counter_base = "ЭТИМ ТЫ БУДЕШЬ УБИВАТЬ"
		_counter.text = _counter_base
		_hint.text = HINT_CARDS
		_next_button.hide()
		_reroll_button.hide()
		_slots_box.hide()
		_slot_info.text = ""
		return
	_title.text = "ВОЛНА %d ПРОЙДЕНА!" % GameState.wave
	_next_button.show()
	_reroll_button.show()
	_reroll_button.text = "РЕРОЛЛ %d" % _reroll_cost()
	_reroll_button.disabled = GameState.coins < _reroll_cost()
	_slots_box.visible = _shop_mode
	var next_wave: int = GameState.wave + 1
	var kind: StringName = GameState.special_waves.get(next_wave, &"normal")
	var label: String = {&"elite": ": ЭЛИТА!", &"horde": ": ОРДА!", &"boss": ": БОССЫ!"}.get(kind, "")
	if _shop_mode:
		_counter_base = "ЛАРЁК: ТРАТЬ ГОВНО, ПОКА ЖИВОЙ"
		_hint.text = HINT_SHOP
		_next_button.text = "В БОЙ: ВОЛНА %d%s" % [next_wave, label]
		_next_button.disabled = false
	else:
		_counter_base = "УРОВЕНЬ %d: ВЫБИРАЙ СТАТ (ОСТАЛОСЬ %d)" % [_queue[0], _queue.size()]
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
	if _reroll_button.visible and not _reroll_button.disabled:
		items.append(_reroll_button)
	if _next_button.visible and not _next_button.disabled:
		items.append(_next_button)
	if _slots_box.visible:
		for i: int in GameState.weapons.size():
			items.append(_slot_buttons[i])
	return items


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
	var weapon_name: String = PerkLibrary.title(ShopLibrary.perk_id_of(entry["id"]))
	var action: String
	if GameState.find_merge_partner(i) >= 0:
		action = "E: СКРЕСТИТЬ ДО ТИРА %s" % StatLibrary.TIER_NAMES[entry["tier"]]
	else:
		action = "E: ПЕРЕРАБОТАТЬ (+%d)" % GameState.weapon_recycle_value(i)
	_slot_info.text = "%s ТИР %s. %s" % [weapon_name, StatLibrary.TIER_NAMES[entry["tier"] - 1], action]


func _on_next_pressed() -> void:
	_shop_mode = false
	_root.hide()
	get_tree().paused = false
	EventBus.next_wave_requested.emit()


func _on_reroll_pressed() -> void:
	if _start_mode or _reroll_button.disabled or not _reroll_button.visible:
		return
	GameState.coins -= _reroll_cost()
	GameState.reroll_count += 1
	if _shop_mode:
		GameState.shop_offers = ShopLibrary.fill_offers(GameState.shop_offers, GameState.wave + 1)
	var keep_focus: bool = _zone == 1 and _reroll_button.has_focus()
	_show_choices()
	if keep_focus and not _reroll_button.disabled:
		_focus_bottom(0)  # можно крутить реролл подряд


func _on_card_pressed(index: int) -> void:
	if _start_mode:
		GameState.apply_perk(PerkLibrary.WEAPON_PERKS[index])
		_start_mode = false
		_root.hide()
		get_tree().paused = false
		return
	if _shop_mode:
		var offer: Dictionary = GameState.shop_offers[index]
		var reason: String = ShopLibrary.why_not(offer)
		if reason != "":
			_toast(reason)
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
	if i >= GameState.weapons.size():
		return
	if GameState.find_merge_partner(i) >= 0:
		GameState.merge_weapons(i)
		_toast("СКРЕСТИЛ. ПОЛУЧИЛОСЬ ЗЛЕЕ.")
	else:
		var value: int = GameState.recycle_weapon(i)
		if value == 0:
			_toast("ПОСЛЕДНЕЕ ОРУЖИЕ НЕ ТРОГАЙ, ПОКОЙНИК.")
		else:
			_toast("ПЕРЕРАБОТАЛ: +%d ГОВНА." % value)
	_refresh_shop()
	_focus_bottom(_bottom_index)
	if _zone == 1 and _bottom_items().size() > 0:
		var item: Control = _bottom_items()[_bottom_index]
		if item in _slot_buttons:
			_update_slot_info(_slot_buttons.find(item))


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
		_counter.remove_theme_color_override(&"font_color")


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
