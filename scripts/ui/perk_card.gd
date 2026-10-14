class_name PerkCard
extends TextureButton
## Карточка перка на экране повышения уровня.

signal chosen(perk_id: StringName)

@onready var _icon: TextureRect = $Icon
@onready var _hotkey: Label = $Hotkey
@onready var _title: Label = $Title
@onready var _description: Label = $Description

const FRAMES: Texture2D = preload("res://assets/ui/card_frames.png")
const FRAME_SIZE: Vector2 = Vector2(112.0, 150.0)
const FRAME_VARIANTS: int = 8  # столько рамок в листе card_frames.png

var _perk_id: StringName = &""


func _ready() -> void:
	pressed.connect(func() -> void: chosen.emit(_perk_id))


func setup(perk_id: StringName, hotkey_index: int, frame_variant: int) -> void:
	texture_normal = _frame_texture(frame_variant, 0)
	texture_focused = _frame_texture(frame_variant, 1)
	_perk_id = perk_id
	_icon.texture = PerkLibrary.icon(perk_id)
	_hotkey.text = str(hotkey_index)
	_title.text = PerkLibrary.title(perk_id)
	var stacks: int = GameState.get_perk_stacks(perk_id)
	_description.text = PerkLibrary.description(perk_id)
	if stacks > 0:
		_description.text += "\n(х%d)" % (stacks + 1)


func _frame_texture(variant: int, row: int) -> AtlasTexture:
	var atlas: AtlasTexture = AtlasTexture.new()
	atlas.atlas = FRAMES
	atlas.region = Rect2(Vector2(variant * FRAME_SIZE.x, row * FRAME_SIZE.y), FRAME_SIZE)
	return atlas
