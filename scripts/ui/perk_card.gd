class_name PerkCard
extends TextureButton
## Карточка перка на экране повышения уровня.

signal chosen(perk_id: StringName)

@onready var _arrow: TextureRect = $Arrow
@onready var _icon: TextureRect = $Icon
@onready var _hotkey: Label = $Hotkey
@onready var _title: Label = $Title
@onready var _description: Label = $Description

const FRAMES: Texture2D = preload("res://assets/ui/card_frames.png")
const FRAME_SIZE: Vector2 = Vector2(112.0, 150.0)
const ARROW_BASE_Y: float = 156.0
const FRAME_VARIANTS: int = 8  # столько рамок в листе card_frames.png

var _perk_id: StringName = &""


func _ready() -> void:
	pressed.connect(func() -> void: chosen.emit(_perk_id))
	focus_entered.connect(_refresh_highlight)
	focus_exited.connect(_refresh_highlight)
	_refresh_highlight()


func setup(perk_id: StringName, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = perk_id
	_icon.texture = PerkLibrary.icon(perk_id)
	_hotkey.text = str(hotkey_index)
	_title.text = PerkLibrary.title(perk_id)
	_title.add_theme_color_override(&"font_color", Color(0.968627, 1, 0, 1))
	var stacks: int = GameState.get_perk_stacks(perk_id)
	_description.text = PerkLibrary.description(perk_id)
	if stacks > 0:
		_description.text += "\n(х%d)" % (stacks + 1)


## Карточка товара Ларька: цена, тир (цветом), заморозка.
func setup_offer(offer: Dictionary, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = offer["id"]
	_icon.texture = ShopLibrary.icon(offer)
	_hotkey.text = str(hotkey_index)
	_title.text = ShopLibrary.title(offer) + "\nТИР " + StatLibrary.TIER_NAMES[offer["tier"] - 1]
	_title.add_theme_color_override(&"font_color", StatLibrary.tier_color(offer["tier"]))
	_description.text = ShopLibrary.description(offer)


## Карточка стата: иконка, название цветом тира, «ТИР I..IV» и описание.
func setup_stat(stat_id: StringName, tier: int, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = stat_id
	_icon.texture = StatLibrary.icon(stat_id)
	_hotkey.text = str(hotkey_index)
	_title.text = StatLibrary.title(stat_id) + "\nТИР " + StatLibrary.TIER_NAMES[tier - 1]
	_title.add_theme_color_override(&"font_color", StatLibrary.tier_color(tier))
	_description.text = StatLibrary.description(stat_id, tier)


func _frame_texture(variant: int, row: int) -> AtlasTexture:
	var atlas: AtlasTexture = AtlasTexture.new()
	atlas.atlas = FRAMES
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
	modulate = Color.WHITE if has_focus() else Color(0.45, 0.45, 0.5)
	_arrow.visible = has_focus()
