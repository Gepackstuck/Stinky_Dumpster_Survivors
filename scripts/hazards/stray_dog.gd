class_name StrayDog
extends Node2D
## Н16: бездомный пёс сидит на арене с «?» над головой. Постой рядом STRAY_ADOPT_SEC - пойдёт за тобой (BuddyDog).
## Пока пса у героя нет, редко появляется в волне (BuddyKeeper.maybe_spawn_stray).

const TEX: GDScript = preload("res://scripts/systems/tex.gd")

var _sprite: Sprite2D
var _mark: Label
var _held: float = 0.0
var _anim: float = 0.0


func _ready() -> void:
	z_index = 1
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/buddy_dog.png")
	_sprite.hframes = 6
	_sprite.frame = 4
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_mark = Label.new()
	_mark.text = "?"
	_mark.position = Vector2(-4.0, -24.0)
	_mark.add_theme_color_override(&"font_color", Color(0.97, 1.0, 0.0))
	_mark.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	add_child(_mark)
	EventBus.wave_ended.connect(func(_w: int) -> void: queue_free())


func _process(delta: float) -> void:
	_anim += delta
	_sprite.frame = 4 + int(_anim * 2.0) % 2
	_mark.position.y = -24.0 - absf(sin(_anim * 4.0)) * 3.0
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null:
		return
	if player.global_position.distance_to(global_position) <= 22.0:
		_held += delta
		_mark.text = "%d%%" % roundi(100.0 * _held / Balance.STRAY_ADOPT_SEC)
		if _held >= Balance.STRAY_ADOPT_SEC:
			_adopt(player)
	else:
		_held = maxf(_held - delta, 0.0)
		_mark.text = "?"


func _adopt(player: Node2D) -> void:
	GameState.dog_found_run = true
	var dog: BuddyDog = BuddyDog.new()
	dog.player = player
	dog.stray = true
	get_parent().add_child(dog)
	dog.global_position = global_position
	HitFx.popup(get_tree(), global_position + Vector2(0.0, -20.0), tr("ПЁС ПОШЁЛ ЗА ТОБОЙ!"), Color(1.0, 0.75, 0.35), 16.0, 1.6, true)
	queue_free()
