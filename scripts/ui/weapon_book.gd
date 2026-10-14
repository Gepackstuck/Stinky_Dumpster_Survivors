class_name WeaponBook
extends Control
## Книга оружия на кладбище: всё оружие игры, закрытое тёмное с условием открытия и прогрессом.

const COLUMNS: int = 5
const CELL: Vector2 = Vector2(92.0, 70.0)
const YELLOW: Color = Color(0.968627, 1.0, 0.0)
const GREEN: Color = Color(0.2235, 1.0, 0.0784)
const GREY: Color = Color(0.55, 0.55, 0.6)
const RED: Color = Color(1.0, 0.1, 0.2)


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.03, 0.02, 0.04, 0.97)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(back)
	_text("ОРУЖИЕ. ЧТО ОТКРЫТО, ЧТО НЕТ", Vector2(0.0, 8.0), 480.0, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	var ids: Array[StringName] = []
	for perk_id: StringName in PerkLibrary.WEAPON_PERKS:
		ids.append(StringName(String(perk_id).trim_prefix("w_")))
	for i: int in ids.size():
		_cell(ids[i], Vector2(10.0 + (i % COLUMNS) * CELL.x, 26.0 + floorf(float(i) / COLUMNS) * CELL.y))
	_text("TAB / ESC - НАЗАД", Vector2(0.0, 250.0), 480.0, GREY, HORIZONTAL_ALIGNMENT_CENTER)


func _cell(id: StringName, pos: Vector2) -> void:
	var open: bool = Profile.is_weapon_unlocked(id)
	var icon: TextureRect = TextureRect.new()
	icon.texture = PerkLibrary.icon(StringName("w_" + String(id)))
	icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	icon.position = pos + Vector2((CELL.x - 16.0) * 0.5 - 4.0, 0.0)
	icon.modulate = Color.WHITE if open else Color(0.15, 0.15, 0.2)
	add_child(icon)
	var title: String = PerkLibrary.title(StringName("w_" + String(id))) if open else "???"
	_text(title, pos + Vector2(0.0, 20.0), CELL.x - 8.0, Color.WHITE if open else GREY, HORIZONTAL_ALIGNMENT_CENTER)
	if open:
		_text("ОТКРЫТО", pos + Vector2(0.0, 32.0), CELL.x - 8.0, GREEN, HORIZONTAL_ALIGNMENT_CENTER)
	else:
		var rule: Dictionary = Balance.WEAPON_UNLOCK[id]
		_text("%s\n%d/%d" % [_rule_text(rule), mini(Profile.counter(rule["kind"]), rule["need"]), rule["need"]], pos + Vector2(0.0, 32.0), CELL.x - 8.0, RED, HORIZONTAL_ALIGNMENT_CENTER)


func _rule_text(rule: Dictionary) -> String:
	match rule["kind"]:
		&"kills":
			return "УБЕЙ ВРАГОВ"
		&"coins":
			return "СОБЕРИ ГОВНА"
		&"deaths":
			return "СДОХНИ"
		&"wins":
			return "ПРОЙДИ ИГРУ"
	return ""


func _text(text: String, pos: Vector2, width: float, color: Color, align: HorizontalAlignment) -> void:
	var label: Label = Label.new()
	label.text = text
	label.position = pos
	label.size = Vector2(width, 10.0)
	label.horizontal_alignment = align
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	label.add_theme_constant_override(&"shadow_offset_x", 1)
	label.add_theme_constant_override(&"shadow_offset_y", 1)
	add_child(label)
