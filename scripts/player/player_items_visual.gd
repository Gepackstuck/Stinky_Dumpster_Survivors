class_name PlayerItemsVisual
extends Node2D
## Купленные шмотки видны на герое, как в Brotato: каждая крепится к своей точке (голова, лицо, грудь, руки, ноги, спина).
## Компаньонов (крыса, турель, духи) тут нет: их видно и так.

const ICON_SCALE: float = 0.5
## Шапки крупнее остального: их должно быть видно (целый масштаб, без каши из пикселей).
const SLOT_SCALE: Dictionary[StringName, float] = {&"head": 1.0}
## Точки крепления; несколько предметов в одной точке занимают следующие смещения.
const SLOT_OFFSETS: Dictionary[StringName, Array] = {
	&"head": [Vector2(0, -12), Vector2(0, -19), Vector2(-7, -15), Vector2(7, -15)],
	&"face": [Vector2(0, -3), Vector2(0, -1), Vector2(-3, -2), Vector2(3, -2)],
	&"chest": [Vector2(0, 4), Vector2(0, 7), Vector2(-4, 5), Vector2(4, 5)],
	&"hand_l": [Vector2(-9, 3), Vector2(-10, -1), Vector2(-9, 7)],
	&"hand_r": [Vector2(9, 3), Vector2(10, -1), Vector2(9, 7)],
	&"feet": [Vector2(0, 10), Vector2(-6, 10), Vector2(6, 10)],
	&"back": [Vector2(-7, -3), Vector2(7, -3), Vector2(0, -6)],
}

var _sprite: Sprite2D
var _animator: FrameAnimatorComponent
var _icons: Array[Sprite2D] = []
var _slots: Array[StringName] = []
var _bases: Array[Vector2] = []
var _time: float = 0.0


func _ready() -> void:
	_sprite = get_parent().get_node("Sprite2D") as Sprite2D
	_animator = get_parent().get_node("FrameAnimator") as FrameAnimatorComponent
	EventBus.items_changed.connect(_rebuild)
	EventBus.run_started.connect(_rebuild)
	_rebuild()


func _rebuild() -> void:
	for icon: Sprite2D in _icons:
		icon.queue_free()
	_icons.clear()
	_slots.clear()
	_bases.clear()
	var used: Dictionary[StringName, int] = {}
	for item_id: StringName in GameState.items:
		var slot: StringName = ItemLibrary.slot(item_id)
		if slot == &"" or GameState.items[item_id] <= 0:
			continue
		var index: int = used.get(slot, 0)
		var offsets: Array = SLOT_OFFSETS[slot]
		if index >= offsets.size():
			continue
		used[slot] = index + 1
		var icon: Sprite2D = Sprite2D.new()
		icon.texture = ItemLibrary.icon(item_id)
		icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		icon.scale = Vector2.ONE * SLOT_SCALE.get(slot, ICON_SCALE)
		add_child(icon)
		_icons.append(icon)
		_slots.append(slot)
		_bases.append(offsets[index])
	_layout()


func _process(delta: float) -> void:
	_time += delta
	_layout()


func _layout() -> void:
	if _sprite == null:
		return
	var row: int = _animator.row
	var mirror: float = -1.0 if _sprite.flip_h else 1.0
	var bob: float = 0.0
	if _animator.active:
		bob = roundf(sin(_time * 14.0))
	for i: int in _icons.size():
		var slot: StringName = _slots[i]
		var icon: Sprite2D = _icons[i]
		icon.position = Vector2(_bases[i].x * mirror, _bases[i].y + bob)
		icon.flip_h = _sprite.flip_h
		if slot == &"face":
			icon.visible = row != 1               # спиной лица не видно
		elif slot == &"back":
			icon.visible = row != 2               # лицом к камере спина не видна
		else:
			icon.visible = true
