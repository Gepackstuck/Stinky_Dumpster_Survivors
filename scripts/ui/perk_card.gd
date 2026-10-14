class_name PerkCard
extends TextureButton
## Карточка перка на экране повышения уровня.

signal chosen(perk_id: StringName)

@onready var _icon: TextureRect = $Icon
@onready var _hotkey: Label = $Hotkey
@onready var _title: Label = $Title
@onready var _description: Label = $Description

var _perk_id: StringName = &""


func _ready() -> void:
	pressed.connect(func() -> void: chosen.emit(_perk_id))


func setup(perk_id: StringName, hotkey_index: int) -> void:
	_perk_id = perk_id
	_icon.texture = PerkLibrary.icon(perk_id)
	_hotkey.text = str(hotkey_index)
	_title.text = PerkLibrary.title(perk_id)
	var stacks: int = GameState.get_perk_stacks(perk_id)
	_description.text = PerkLibrary.description(perk_id)
	if stacks > 0:
		_description.text += "\n(х%d)" % (stacks + 1)
