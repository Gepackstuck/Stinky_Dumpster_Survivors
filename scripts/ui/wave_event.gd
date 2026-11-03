class_name WaveEvent
extends Control
## Событие между волнами (перед Ларьком): персонаж с предложением и два выбора. Balance.EVENT_*.
## Виды: меняла (оружие -> 2 предмета), гадалка (куча-лотерея на следующей волне), мент (взятка или риск),
## спорщик (пари на следующую волну). A/D - выбор, пробел/A - да. choose(i) - для ботов. Сигнал done.

signal done

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const KINDS: Array[StringName] = [&"trader", &"fortune", &"cop", &"bet"]
const BETS: Array[StringName] = [&"no_dash", &"kills", &"few_hits", &"half_hp"]

var _kind: StringName = &"trader"
var _bet: StringName = &"no_dash"
var _buttons: Array[Button] = []


static func roll() -> StringName:
	if GameState.wave < Balance.EVENT_FROM_WAVE or GameState.wave >= Balance.WAVE_COUNT - 1 or randf() >= Balance.EVENT_CHANCE:
		return &""
	return KINDS[randi() % KINDS.size()]


func setup(kind: StringName) -> void:
	_kind = kind
	_bet = BETS[randi() % BETS.size()]
	add_to_group(&"wave_event")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	z_index = 90
	var back: Panel = Panel.new()
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.03, 0.04, 0.97)
	box.border_color = Color(0.97, 1.0, 0.0)
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.position = Vector2(80.0, 60.0)
	back.size = Vector2(320.0, 150.0)
	add_child(back)
	var data: Dictionary = _texts()
	var face: Sprite2D = Sprite2D.new()
	face.texture = CharacterLibrary.sprite_sheet(data["face"])
	face.hframes = 4
	face.vframes = 3
	face.frame = 8
	face.scale = Vector2.ONE * 2.0
	face.position = Vector2(118.0, 112.0)
	face.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(face)
	_add_label(data["title"], Vector2(150.0, 68.0), 240.0, Color(0.97, 1.0, 0.0))
	var text: Label = _add_label(data["text"], Vector2(150.0, 84.0), 240.0, Color.WHITE)
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.size.y = 60.0
	for i: int in 2:
		var b: Button = Button.new()
		b.text = data["yes"] if i == 0 else data["no"]
		b.position = Vector2(100.0 + i * 145.0, 176.0)
		b.size = Vector2(135.0, 22.0)
		UI_BUTTONS.skin(b, i * 3)
		b.pressed.connect(choose.bind(i))
		add_child(b)
		_buttons.append(b)
	UI_BUTTONS.add_focus_arrows(_buttons)
	_buttons[0].grab_focus()


func _add_label(t: String, pos: Vector2, w: float, color: Color) -> Label:
	var l: Label = Label.new()
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART   # перенос включаем ДО текста, иначе подпись растягивается под строку
	l.custom_minimum_size = Vector2(w, 0.0)
	l.position = pos
	l.size = Vector2(w, 12.0)
	l.text = t
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	add_child(l)
	return l


func _texts() -> Dictionary:
	match _kind:
		&"trader":
			return {"face": &"hobo", "title": "БОМЖ-МЕНЯЛА", "text": "ОТДАЙ САМУЮ ХРЕНОВУЮ ПУШКУ - ДАМ ДВЕ ШТУКИ ИЗ МЕШКА. НЕ ГЛЯДЯ.", "yes": "МЕНЯЮ", "no": "ПОШЁЛ ТЫ"}
		&"fortune":
			return {"face": &"granny", "title": "ГАДАЛКА С ВОКЗАЛА", "text": "ПОЗОЛОТИ РУЧКУ (%d ГОВНА) - НАГАДАЮ КУЧУ НА СЛЕДУЮЩЕЙ ВОЛНЕ. РУЛЕТКА БУДЕТ." % _fortune_price(), "yes": "ПЛАЧУ", "no": "НЕ ВЕРЮ"}
		&"cop":
			return {"face": &"guard", "title": "МЕНТ", "text": "ДОКУМЕНТЫ! ВЗЯТКА %d ГОВНА - И Я ТЕБЯ НЕ ВИДЕЛ. РИСКНЁШЬ - ПОЛОВИНА ШАНСА, ЧТО ОТБЕРУ ТРЕТЬ ВСЕГО ГОВНА." % _bribe(), "yes": "НА, ПОДАВИСЬ", "no": "РИСКНУ"}
		_:
			return {"face": &"punk", "title": "СПОРЩИК", "text": tr("СПОРИМ НА %d ГОВНА: %s? ВЫИГРАЕШЬ - ВТРОЕ БОЛЬШЕ И ПРЕДМЕТ.") % [_stake(), _bet_text()], "yes": "СПОРИМ", "no": "СЛАБО"}


func _fortune_price() -> int:
	return Balance.EVENT_FORTUNE_PRICE + GameState.wave * 2


func _bribe() -> int:
	return maxi(roundi(GameState.coins * Balance.EVENT_BRIBE_FRACTION), 5)


func _stake() -> int:
	return Balance.EVENT_BET_STAKE + GameState.wave * 2


func _bet_text() -> String:
	match _bet:
		&"no_dash": return tr("ПРОЙДЁШЬ ВОЛНУ БЕЗ РЫВКОВ")
		&"kills": return tr("УБЬЁШЬ %d ЗА ВОЛНУ") % _bet_kills()
		&"few_hits": return tr("ПОЛУЧИШЬ НЕ БОЛЬШЕ 3 УДАРОВ")
		_: return tr("ЗАКОНЧИШЬ ВОЛНУ, И ХП БУДЕТ НЕ МЕНЬШЕ ПОЛОВИНЫ")


func _bet_kills() -> int:
	return 20 + GameState.wave * 6


func choose(i: int) -> void:
	var yes: bool = i == 0
	match _kind:
		&"trader":
			if yes and GameState.weapons.size() > 1:
				var worst: int = 0
				for k: int in GameState.weapons.size():
					if GameState.weapons[k]["tier"] < GameState.weapons[worst]["tier"]:
						worst = k
				var gone: String = PerkLibrary.title(ShopLibrary.perk_id_of(GameState.weapons[worst]["id"]))
				GameState.weapons.remove_at(worst)
				EventBus.weapons_changed.emit()
				var got: PackedStringArray = []
				for n: int in 2:
					var item: StringName = ItemLibrary.roll_free_item(GameState.wave)
					if item != &"":
						GameState.add_item(item)
						got.append(ItemLibrary.title(item))
				GameState.last_event_note = "МЕНЯЛА ЗАБРАЛ %s, ДАЛ: %s" % [gone, ", ".join(got)]
		&"fortune":
			if yes and GameState.coins >= _fortune_price():
				GameState.coins -= _fortune_price()
				GameState.forced_pile = true
				GameState.last_event_note = "ГАДАЛКА: В СЛЕДУЮЩЕЙ ВОЛНЕ БУДЕТ СВЕТЯЩАЯСЯ КУЧА"
		&"cop":
			if yes:
				GameState.coins -= _bribe()
				GameState.last_event_note = "ОТДАЛ МЕНТУ %d ГОВНА. СВОБОДЕН." % _bribe()
			elif randf() < 0.5:
				var taken: int = roundi(GameState.coins * Balance.EVENT_COP_TAKE)
				GameState.coins -= taken
				GameState.last_event_note = "МЕНТ ОТОБРАЛ %d ГОВНА. РИСКНУЛ, ЛОХ." % taken
			else:
				GameState.last_event_note = "МЕНТ ЗЕВНУЛ И УШЁЛ. ПОВЕЗЛО ТЕБЕ."
		&"bet":
			if yes and GameState.coins >= _stake():
				GameState.coins -= _stake()
				GameState.active_bet = {"kind": _bet, "stake": _stake(), "kills": _bet_kills(), "kills0": GameState.kills, "dashes": 0, "hits": 0}
				GameState.last_event_note = "ПОСПОРИЛ НА %d ГОВНА. УСЛОВИЕ - ВВЕРХУ ЭКРАНА В БОЮ." % _stake()
	AudioManager.play_sfx(&"buy" if yes else &"ui_select")
	done.emit()
	queue_free()


func _input(event: InputEvent) -> void:
	if event.is_action_pressed(&"move_left") or event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_left") or event.is_action_pressed(&"ui_right"):
		get_viewport().set_input_as_handled()
		(_buttons[1] if _buttons[0].has_focus() else _buttons[0]).grab_focus()
