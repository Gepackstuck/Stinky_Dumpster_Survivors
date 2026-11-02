class_name WeaponPanel
extends Control
## Панель оружия в HUD (правый верх): 6 слотов, рамка цвета тира, иконка и полоска перезарядки под каждым.
## Набор слотов - из GameState.weapons (сигнал weapons_changed), перезарядка - у узлов группы weapon_nodes (meta "slot").

const FRAME: Texture2D = preload("res://assets/ui/hud_weapon_slot.png")
const CD_UNDER: Texture2D = preload("res://assets/ui/hud_cd_under.png")
const CD_FILL: Texture2D = preload("res://assets/ui/hud_cd_fill.png")
const SLOT_SIZE: Vector2 = Vector2(20.0, 20.0)
const STEP: float = 21.0
const READY_FLASH: Color = Color(1.0, 1.0, 0.6)

var _frames: Array[TextureRect] = []
var _icons: Array[TextureRect] = []
var _bars: Array[TextureProgressBar] = []


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for i: int in Balance.WEAPON_SLOTS:
		var frame: TextureRect = TextureRect.new()
		frame.texture = FRAME
		frame.position = Vector2(i * STEP, 0.0)
		frame.size = SLOT_SIZE
		frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(frame)
		_frames.append(frame)
		var icon: TextureRect = TextureRect.new()
		icon.position = Vector2(i * STEP + 2.0, 2.0)
		icon.size = Vector2(16.0, 16.0)
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(icon)
		_icons.append(icon)
		var bar: TextureProgressBar = TextureProgressBar.new()
		bar.texture_under = CD_UNDER
		bar.texture_progress = CD_FILL
		bar.max_value = 1.0
		bar.step = 0.0
		bar.position = Vector2(i * STEP + 1.0, SLOT_SIZE.y + 1.0)
		bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(bar)
		_bars.append(bar)
	EventBus.weapons_changed.connect(_rebuild)
	EventBus.run_started.connect(_rebuild)
	_rebuild()


func _rebuild() -> void:
	for i: int in _frames.size():
		var filled: bool = i < GameState.weapons.size()
		_frames[i].visible = filled
		_icons[i].visible = filled
		_bars[i].visible = filled
		if not filled:
			continue
		var entry: Dictionary = GameState.weapons[i]
		var tint: Color = StatLibrary.tier_color(entry["tier"])
		_frames[i].modulate = tint
		_icons[i].texture = PerkLibrary.icon_small(ShopLibrary.perk_id_of(entry["id"]))
		_bars[i].tint_progress = tint


func _process(_delta: float) -> void:
	for node: Node in get_tree().get_nodes_in_group(&"weapon_nodes"):
		if not node.has_method(&"cooldown_ratio") or not node.has_meta(&"slot"):
			continue
		var slot: int = node.get_meta(&"slot")
		if slot < 0 or slot >= _bars.size():
			continue
		var ratio: float = node.call(&"cooldown_ratio")
		_bars[slot].value = ratio
		_icons[slot].modulate = READY_FLASH if ratio >= 1.0 else Color.WHITE
