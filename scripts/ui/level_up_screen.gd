class_name LevelUpScreen
extends CanvasLayer
## Экран выбора перка: ставит игру на паузу, показывает 3 карточки. Уровни копятся в очередь.

@onready var _cards: Array[PerkCard] = [$Root/Cards/Card1, $Root/Cards/Card2, $Root/Cards/Card3]
@onready var _root: Control = $Root
@onready var _title: Label = $Root/Title
@onready var _counter: Label = $Root/Counter
@onready var _empty: Label = $Root/Empty
@onready var _next_button: Button = $Root/NextButton

var _pending: int = 0
var _selected: int = 0


func _ready() -> void:
	_root.hide()
	for i: int in _cards.size():
		_cards[i].chosen.connect(_on_card_chosen)
		_cards[i].mouse_entered.connect(_select.bind(i))  # наведение мыши = выбор карточки для A/D
	_next_button.pressed.connect(_on_next_pressed)
	EventBus.player_leveled_up.connect(_on_leveled_up)
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.run_won.connect(func() -> void: _root.hide())
	EventBus.player_died.connect(_on_player_died)


func _unhandled_input(event: InputEvent) -> void:
	if not _root.visible or _pending <= 0:
		return
	if event.is_action_pressed(&"move_left"):
		get_viewport().set_input_as_handled()
		_select(_selected - 1)
		return
	if event.is_action_pressed(&"move_right"):
		get_viewport().set_input_as_handled()
		_select(_selected + 1)
		return
	for i: int in _cards.size():
		if event.is_action_pressed(StringName("pick_card_%d" % (i + 1))) and _cards[i].visible:
			get_viewport().set_input_as_handled()
			_on_card_chosen(_cards[i].get_meta(&"perk_id"))
			return


## Как в Brotato: уровни копятся во время волны, выбор — после её конца.
func _on_leveled_up(_new_level: int) -> void:
	_pending += 1


func _on_wave_ended(_wave: int) -> void:
	_show_choices()


func _show_choices() -> void:
	var choices: Array[StringName] = PerkLibrary.pick_choices(Balance.LEVEL_UP_CHOICES)
	if _pending <= 0:
		choices.clear()
	var frames: Array[int] = []
	for v: int in PerkCard.FRAME_VARIANTS:
		frames.append(v)
	frames.shuffle()  # у каждой карточки своя случайная рамка
	for i: int in _cards.size():
		var has_choice: bool = i < choices.size()
		_cards[i].visible = has_choice
		if has_choice:
			_cards[i].setup(choices[i], i + 1, frames[i])
			_cards[i].set_meta(&"perk_id", choices[i])
	_refresh_shop()
	_root.show()
	get_tree().paused = true
	_select(0)
	if _pending <= 0:
		_next_button.grab_focus()


## Счётчик «осталось купить», текст кнопки следующей волны и блокировка кнопки до конца выбора.
func _refresh_shop() -> void:
	_title.text = "ЛАРЁК"
	_counter.text = "ОСТАЛОСЬ ВЗЯТЬ: %d" % _pending
	_empty.visible = _pending <= 0
	var next_wave: int = GameState.wave + 1
	var kind: StringName = GameState.special_waves.get(next_wave, &"normal")
	var label: String = {&"elite": ": ЭЛИТА!", &"horde": ": ОРДА!", &"boss": ": БОССЫ!"}.get(kind, "")
	_next_button.text = "ВОЛНА %d%s" % [next_wave, label]
	_next_button.disabled = _pending > 0


func _on_next_pressed() -> void:
	_root.hide()
	get_tree().paused = false
	EventBus.next_wave_requested.emit()


func _on_card_chosen(perk_id: StringName) -> void:
	GameState.apply_perk(perk_id)
	_pending -= 1
	_show_choices()


func _on_player_died() -> void:
	_pending = 0
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
