class_name PerkCard
extends TextureButton
## Карточка перка на экране повышения уровня.

signal chosen(perk_id: StringName)

@onready var _arrow: TextureRect = $Arrow
@onready var _icon: TextureRect = $Icon
@onready var _hotkey: Label = $Hotkey
@onready var _title: Label = $Title
@onready var _description: Label = $Description
@onready var _price: Label = $Price

const FRAMES: Texture2D = preload("res://assets/ui/card_frames.png")
const FRAME_SIZE: Vector2 = Vector2(112.0, 150.0)
const ARROW_BASE_Y: float = 156.0
const FRAME_VARIANTS: int = 8  # столько рамок в листе card_frames.png
const TITLE_TOP: float = 56.0
const PRICE_TOP: float = 126.0

var _perk_id: StringName = &""
var _lock: TextureRect  # значок замка справа сверху: предмет заморожен


func _ready() -> void:
	_lock = TextureRect.new()
	_lock.texture = preload("res://assets/ui/lock_icon.png")
	_lock.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_lock.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lock.position = Vector2(FRAME_SIZE.x - 20.0, 8.0)
	_lock.hide()
	add_child(_lock)
	pressed.connect(func() -> void: chosen.emit(_perk_id))
	focus_entered.connect(_refresh_highlight)
	focus_exited.connect(_refresh_highlight)
	_refresh_highlight()


func setup(perk_id: StringName, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = perk_id
	_price.hide()
	_lock.hide()
	_icon.texture = PerkLibrary.icon(perk_id)
	_hotkey.text = str(hotkey_index)
	_title.text = PerkLibrary.title(perk_id)
	_title.add_theme_color_override(&"font_color", Color(0.968627, 1, 0, 1))
	var stacks: int = GameState.get_perk_stacks(perk_id)
	_description.text = PerkLibrary.description(perk_id)
	if stacks > 0:
		_description.text += "\n(х%d)" % (stacks + 1)
	_fit_text(false)


## Карточка товара Ларька: цена, тир (цветом), заморозка.
func setup_offer(offer: Dictionary, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = offer["id"]
	_icon.texture = ShopLibrary.icon(offer)
	_hotkey.text = str(hotkey_index)
	_title.text = ShopLibrary.title(offer) + "\nТИР " + StatLibrary.TIER_NAMES[offer["tier"] - 1]
	_title.add_theme_color_override(&"font_color", StatLibrary.tier_color(offer["tier"]))
	if offer["kind"] == &"item" and ItemLibrary.is_cursed(offer["id"]):
		_title.add_theme_color_override(&"font_color", Color(0.75, 0.2, 1.0))   # проклятое - фиолетовое
	_description.text = ShopLibrary.description(offer)
	var affordable: bool = GameState.coins >= offer["price"]
	_price.text = "%d ГОВНА" % offer["price"]
	_price.add_theme_color_override(&"font_color", Color(0.968627, 1, 0, 1) if affordable else Color(1.0, 0.1, 0.2))
	_price.show()
	_lock.visible = offer.get("locked", false)
	_fit_text(true)


## Карточка стата: иконка, название цветом тира, «ТИР I..IV» и описание.
func setup_stat(stat_id: StringName, tier: int, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = stat_id
	_price.hide()
	_lock.hide()
	_icon.texture = StatLibrary.icon(stat_id)
	_hotkey.text = str(hotkey_index)
	_title.text = StatLibrary.title(stat_id) + "\nТИР " + StatLibrary.TIER_NAMES[tier - 1]
	_title.add_theme_color_override(&"font_color", StatLibrary.tier_color(tier))
	_description.text = StatLibrary.description(stat_id, tier)
	_fit_text(false)


## Текст не налезает друг на друга: описание стоит сразу под названием и не заходит на цену.
## Не влезает - сначала убираем строку «ТИР» (тир и так виден цветом названия), потом обрезаем с «...» (в пиксельном шрифте нет «…»).
func _fit_text(has_price: bool) -> void:
	var bottom: float = (PRICE_TOP - 1.0) if has_price else (FRAME_SIZE.y - 8.0)
	var lh: float = _line_h(_title)
	_description.max_lines_visible = -1
	var avail: int = 1
	for attempt: int in 2:
		var title_h: float = _title.get_line_count() * lh
		_title.position.y = TITLE_TOP
		_title.size.y = title_h
		_description.position.y = TITLE_TOP + title_h + 3.0
		avail = maxi(int((bottom - _description.position.y) / lh), 1)
		if _description.get_line_count() <= avail or not _title.text.contains("\n"):
			break
		_title.text = _title.text.get_slice("\n", 0)   # без «ТИР ...» - тир и так виден цветом названия
	var text: String = _description.text.replace("\n\n", "\n")   # пустые строки - роскошь
	_description.text = text
	if _description.get_line_count() > avail:
		var words: PackedStringArray = text.replace("\n", " \n ").split(" ", false)
		while words.size() > 1 and _description.get_line_count() > avail:
			words.remove_at(words.size() - 1)
			_description.text = " ".join(words).replace(" \n ", "\n").strip_edges() + "..."
	_description.max_lines_visible = avail
	_description.size.y = avail * lh


func _line_h(l: Label) -> float:
	return l.get_line_height() + l.get_theme_constant(&"line_spacing")


func _frame_texture(variant: int, row: int) -> AtlasTexture:
	var atlas: AtlasTexture = AtlasTexture.new()
	atlas.atlas = ArtStyle.tex("res://assets/ui/card_frames.png")   # новый стиль: ржавые рамки
	atlas.region = Rect2(Vector2(variant * FRAME_SIZE.x, row * FRAME_SIZE.y), FRAME_SIZE)
	return atlas


func _process(_delta: float) -> void:
	if has_focus():
		_arrow.position.y = ARROW_BASE_Y + roundf(2.0 * sin(Time.get_ticks_msec() * 0.01))  # стрелка покачивается
		# выбранная карточка пульсирует тёплым жёлтым
		var pulse: float = 0.5 + 0.5 * sin(Time.get_ticks_msec() * 0.012)
		modulate = Color(1.0, 1.0, 1.0).lerp(Color(1.0, 1.0, 0.45), pulse * 0.6)


## Невыбранные карточки затемнены, выбранная яркая и мигает — сразу видно, на какой стоишь.
func _refresh_highlight() -> void:
	modulate = Color.WHITE if has_focus() else Color(0.8, 0.8, 0.85)
	_arrow.visible = has_focus()
