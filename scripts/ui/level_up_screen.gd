class_name LevelUpScreen
extends CanvasLayer
## Экран выбора перка: ставит игру на паузу, показывает 3 карточки. Уровни копятся в очередь.

@onready var _cards: Array[PerkCard] = [$Root/Cards/Card1, $Root/Cards/Card2, $Root/Cards/Card3]
@onready var _root: Control = $Root

var _pending: int = 0


func _ready() -> void:
	_root.hide()
	for card: PerkCard in _cards:
		card.chosen.connect(_on_card_chosen)
	EventBus.player_leveled_up.connect(_on_leveled_up)
	EventBus.player_died.connect(_on_player_died)


func _unhandled_input(event: InputEvent) -> void:
	if not _root.visible:
		return
	for i: int in _cards.size():
		if event.is_action_pressed(StringName("pick_card_%d" % (i + 1))) and _cards[i].visible:
			get_viewport().set_input_as_handled()
			_on_card_chosen(_cards[i].get_meta(&"perk_id"))
			return


func _on_leveled_up(_new_level: int) -> void:
	_pending += 1
	if not _root.visible:
		_show_choices()


func _show_choices() -> void:
	var choices: Array[StringName] = PerkLibrary.pick_choices(Balance.LEVEL_UP_CHOICES)
	if choices.is_empty():
		_pending = 0
		return
	for i: int in _cards.size():
		var has_choice: bool = i < choices.size()
		_cards[i].visible = has_choice
		if has_choice:
			_cards[i].setup(choices[i], i + 1)
			_cards[i].set_meta(&"perk_id", choices[i])
	_root.show()
	get_tree().paused = true


func _on_card_chosen(perk_id: StringName) -> void:
	GameState.apply_perk(perk_id)
	_pending -= 1
	if _pending > 0:
		_show_choices()
	else:
		_root.hide()
		get_tree().paused = false


func _on_player_died() -> void:
	_pending = 0
	_root.hide()
