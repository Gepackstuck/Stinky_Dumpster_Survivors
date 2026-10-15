extends Node2D
## Ворота на нижней границе арены: появляются после победы над боссом. Войдёшь - бесшовно выходишь на кладбище.

const GRAVEYARD: String = "res://scenes/ui/graveyard.tscn"
const HALF_WIDTH: float = 16.0

var _player: Node2D = null
var _done: bool = false
var _time: float = 0.0
var _hint: Label = null
var _leaves: Array[Sprite2D] = []


func _ready() -> void:
	z_index = 4
	var tex: Texture2D = CharacterLibrary.load_texture("res://assets/sprites/gate.png")
	var half: float = tex.get_width() * 0.5
	for side: int in 2:
		var leaf: Sprite2D = Sprite2D.new()   # створка: начало координат на внешнем крае, чтобы распахиваться наружу
		leaf.texture = tex
		leaf.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		leaf.centered = false
		leaf.region_enabled = true
		leaf.region_rect = Rect2(Vector2(half * side, 0.0), Vector2(half, tex.get_height()))
		leaf.offset = Vector2(0.0 if side == 0 else -half, 0.0)
		leaf.position = Vector2(-half if side == 0 else half, -tex.get_height())
		add_child(leaf)
		_leaves.append(leaf)
	_hint = Label.new()
	_hint.text = "ВЫХОД"
	_hint.position = Vector2(-20.0, -44.0)
	_hint.size = Vector2(40.0, 10.0)
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
	_hint.add_theme_color_override(&"font_shadow_color", Color(1.0, 0.0627451, 0.941176))
	_hint.add_theme_constant_override(&"shadow_offset_x", 1)
	_hint.add_theme_constant_override(&"shadow_offset_y", 1)
	add_child(_hint)
	_player = get_tree().get_first_node_in_group(&"player") as Node2D


func _process(delta: float) -> void:
	_time += delta
	_hint.modulate.a = 0.6 + 0.4 * sin(_time * 6.0)
	if _done or _player == null:
		return
	var local: Vector2 = _player.global_position - global_position
	var near: float = clampf(1.0 - (local.distance_to(Vector2(0.0, -8.0)) - 24.0) / 50.0, 0.0, 1.0)   # ближе - шире створки
	for leaf: Sprite2D in _leaves:
		leaf.scale.x = lerpf(1.0, 0.18, near)
	if local.y > -14.0 and absf(local.x) < HALF_WIDTH:
		_done = true
		SceneFlow.from_arena = true
		SceneFlow.go(GRAVEYARD, Vector2.DOWN)
