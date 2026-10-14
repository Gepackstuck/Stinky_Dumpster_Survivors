class_name LevelUpScreen
extends CanvasLayer
## Экран выбора перка: ставит игру на паузу, показывает 3 карточки. Уровни копятся в очередь.

@onready var _cards: Array[PerkCard] = [$Root/Cards/Card1, $Root/Cards/Card2, $Root/Cards/Card3, $Root/Cards/Card4]
@onready var _root: Control = $Root
@onready var _title: Label = $Root/Title
@onready var _counter: Label = $Root/Counter
@onready var _empty: Label = $Root/Empty
@onready var _next_button: Button = $Root/NextButton
@onready var _reroll_button: Button = $Root/RerollButton
@onready var _coins: Label = $Root/Coins

const PERK_MARK: int = 0  # в очереди: 0 = бесплатный перк/оружие Ларька, >0 = уровень (карточка статов)

var _queue: Array[int] = []
var _offers: Array[Dictionary] = []
var _selected: int = 0
var _start_mode: bool = false


func _ready() -> void:
	_root.hide()
	for i: int in _cards.size():
		_cards[i].chosen.connect(_on_card_chosen)
		_cards[i].mouse_entered.connect(_select.bind(i))  # наведение мыши = выбор карточки для A/D
	_next_button.pressed.connect(_on_next_pressed)
	_reroll_button.pressed.connect(_on_reroll_pressed)
	EventBus.player_leveled_up.connect(_on_leveled_up)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.run_won.connect(func() -> void: _root.hide())
	EventBus.player_died.connect(_on_player_died)
	_show_start_choice.call_deferred()


func _unhandled_input(event: InputEvent) -> void:
	if not _root.visible or _queue.is_empty():
		return
	if event.is_action_pressed(&"move_left"):
		get_viewport().set_input_as_handled()
		_select(_selected - 1)
		return
	if event.is_action_pressed(&"move_right"):
		get_viewport().set_input_as_handled()
		_select(_selected + 1)
		return
	if event is InputEventKey and event.pressed and not event.echo and (event as InputEventKey).physical_keycode == KEY_R:
		get_viewport().set_input_as_handled()
		_on_reroll_pressed()
		return
	for i: int in _cards.size():
		if event.is_action_pressed(StringName("pick_card_%d" % (i + 1))) and _cards[i].visible:
			get_viewport().set_input_as_handled()
			_on_card_chosen(_cards[i].get_meta(&"perk_id"))
			return


## Как в Brotato: уровни копятся во время волны, выбор — после её конца.
func _on_leveled_up(new_level: int) -> void:
	_queue.append(new_level)


func _on_wave_ended(_wave: int) -> void:
	GameState.reroll_count = 0
	_queue.append(PERK_MARK)  # бесплатный перк/оружие Ларька — последним
	_show_choices()


## В начале забега: выбор стартового оружия из 4.
func _show_start_choice() -> void:
	_start_mode = true
	_queue = [PERK_MARK]
	_show_choices()


func _show_choices() -> void:
	var perks: Array[StringName] = []
	_offers.clear()
	if not _queue.is_empty():
		if _start_mode:
			perks.assign(PerkLibrary.WEAPON_PERKS)
		elif _queue[0] == PERK_MARK:
			perks = PerkLibrary.pick_choices(Balance.LEVEL_UP_CHOICES)
			if perks.is_empty():
				_queue.pop_front()  # перки кончились — бонус пропускаем
		else:
			_offers = StatLibrary.pick_offers(Balance.LEVEL_UP_CHOICES, _queue[0])
	var frames: Array[int] = []
	for v: int in PerkCard.FRAME_VARIANTS:
		frames.append(v)
	frames.shuffle()  # у каждой карточки своя случайная рамка
	var count: int = maxi(perks.size(), _offers.size())
	for i: int in _cards.size():
		var has_choice: bool = i < count
		_cards[i].visible = has_choice
		if not has_choice:
			continue
		if not _offers.is_empty():
			_cards[i].setup_stat(_offers[i]["id"], _offers[i]["tier"], i + 1, frames[i])
			_cards[i].set_meta(&"perk_id", _offers[i]["id"])
		else:
			_cards[i].setup(perks[i], i + 1, frames[i])
			_cards[i].set_meta(&"perk_id", perks[i])
	_refresh_shop()
	_root.show()
	get_tree().paused = true
	_select(0)
	if _queue.is_empty():
		_next_button.grab_focus()


func _reroll_cost() -> int:
	return Balance.REROLL_BASE_COST + int(GameState.wave * Balance.REROLL_WAVE_FACTOR) + GameState.reroll_count * Balance.REROLL_STEP_COST


## Счётчик «осталось взять», текст кнопки следующей волны и блокировка кнопки до конца выбора.
func _refresh_shop() -> void:
	_coins.text = "ГОВНА: %d" % GameState.coins
	if _start_mode:
		_title.text = "ВЫБЕРИ СВОЮ ХУЙНЮ"
		_counter.text = "ЭТИМ ТЫ БУДЕШЬ УБИВАТЬ"
		_empty.hide()
		_next_button.hide()
		_reroll_button.hide()
		_coins.hide()
		return
	_coins.show()
	_next_button.show()
	_title.text = "ЛАРЁК"
	var is_perk: bool = not _queue.is_empty() and _queue[0] == PERK_MARK
	if _queue.is_empty():
		_counter.text = ""
	elif is_perk:
		_counter.text = "ОСТАЛОСЬ ВЗЯТЬ: %d   ТВОЙ БЕСПЛАТНЫЙ ПОДАРОК: ОРУЖИЕ ИЛИ ХУЙНЯ" % _queue.size()
	else:
		_counter.text = "ОСТАЛОСЬ ВЗЯТЬ: %d   УРОВЕНЬ %d: ВЫБИРАЙ СТАТ" % [_queue.size(), _queue[0]]
	_empty.visible = _queue.is_empty()
	_reroll_button.visible = not _queue.is_empty()
	_reroll_button.text = "РЕРОЛЛ %d" % _reroll_cost()
	_reroll_button.disabled = GameState.coins < _reroll_cost()
	var next_wave: int = GameState.wave + 1
	var kind: StringName = GameState.special_waves.get(next_wave, &"normal")
	var label: String = {&"elite": ": ЭЛИТА!", &"horde": ": ОРДА!", &"boss": ": БОССЫ!"}.get(kind, "")
	_next_button.text = "ВОЛНА %d%s" % [next_wave, label]
	_next_button.disabled = not _queue.is_empty()


func _on_next_pressed() -> void:
	_root.hide()
	get_tree().paused = false
	EventBus.next_wave_requested.emit()


func _on_reroll_pressed() -> void:
	if _start_mode or _queue.is_empty() or GameState.coins < _reroll_cost():
		return
	GameState.coins -= _reroll_cost()
	GameState.reroll_count += 1
	_show_choices()


func _on_card_chosen(perk_id: StringName) -> void:
	if _start_mode:
		GameState.apply_perk(perk_id)
		_start_mode = false
		_queue.clear()
		_root.hide()
		get_tree().paused = false
		return
	if _queue.is_empty():
		return
	if _queue[0] == PERK_MARK:
		GameState.apply_perk(perk_id)
	else:
		for offer: Dictionary in _offers:
			if offer["id"] == perk_id:
				GameState.apply_stat(perk_id, offer["tier"])
				break
	_queue.pop_front()
	_show_choices()


func _on_player_died() -> void:
	_queue.clear()
	_root.hide()


## Подсветить карточку (A/D или стрелки). Enter/Пробел берёт выбранную — это делает сама кнопка в фокусе.
func _select(index: int) -> void:
	var visible_count: int = 0
	for card: PerkCard in _cards:
		if card.visible:
			visible_count += 1
	if visible_count == 0:
		return
	_selected = posmod(index, visible_count)
	_cards[_selected].grab_focus()
