class_name HeldWeapon
extends Node2D
## Оружие в руках героя, как в Brotato: маленький спрайт стоит на кольце вокруг тела (у каждого слота свое место),
## разворачивается на ближайшего врага (8 направлений) и показывает атаку: ствол отдаёт назад, швабра машет,
## носок раздувается. Верхние оружия рисуются за телом, нижние перед ним, чтобы не закрывать героя.
## Висит ребёнком узла оружия (там же сигнал `fired`).

const OUTLINE: GDScript = preload("res://scripts/systems/outline_fx.gd")
const RING_X: float = 23.0
const RING_Y: float = 16.0
const FIRST_ANGLE: float = 0.5      # первое оружие у правой руки, остальные по кругу
const TRACK_SEC: float = 0.12       # как часто искать цель для поворота
const KICK_DECAY: float = 5.0
const RECOIL_PX: float = 3.0
const SWING_RAD: float = 1.3
const SNAP_RAD: float = PI / 4.0    # поворот шагом 45 градусов (дёрганый пиксель-арт)
const HELD_SCALE: float = 0.62      # спрайты 26x26, в руках делаем компактнее
const FLASH: Texture2D = preload("res://assets/sprites/fx_muzzle.png")
const CASING: Texture2D = preload("res://assets/sprites/fx_casing.png")
const CASING_WEAPONS: Array[StringName] = [&"pipe_gun", &"mosin", &"crossbow", &"slingshot", &"syringe"]
const KICK_LIFT: float = 0.35       # ствол задирается при выстреле (рад)
const ANIM_STEP_SEC: float = 0.14   # смена кадров анимации (лист из 4 кадров)

var _held_scale: float = HELD_SCALE   # у картинки нового стиля другой размер: мировой размер оружия остаётся прежним
var slot_index: int = 0
var slot_count: int = 1

var _sprite: Sprite2D
var _weapon_id: StringName = &""
var _home: Vector2 = Vector2.ZERO
var _aim: Vector2 = Vector2.RIGHT
var _kick: float = 0.0
var _track_left: float = 0.0
var _range_sq: float = 0.0
var _frames: Array[Texture2D] = []
var _anim_clock: float = 0.0
var _frame_idx: int = 0


func _ready() -> void:
	_weapon_id = get_parent().weapon_id
	_range_sq = Balance.WEAPON_TARGET_RANGE * Balance.WEAPON_TARGET_RANGE
	var angle: float = FIRST_ANGLE + TAU * float(slot_index) / float(maxi(slot_count, 1))
	_home = Vector2(cos(angle) * RING_X, sin(angle) * RING_Y)
	_aim = _home.normalized()
	_sprite = Sprite2D.new()
	var held_path: String = "res://assets/sprites/held_%s.png" % _weapon_id
	var held_tex: Texture2D = _load_texture(held_path)
	_held_scale = HELD_SCALE
	if ArtStyle.is_hd() and ArtStyle.has_hd(held_path) and held_tex != null:
		var hd_tex: Texture2D = ArtStyle.tex(held_path)
		_held_scale = HELD_SCALE * float(held_tex.get_height()) / float(hd_tex.get_height())
		held_tex = hd_tex
	_build_frames(held_tex, get_parent().tier)
	_sprite.texture = _frames[0] if not _frames.is_empty() else null
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var back_layer: Node = get_parent().get_parent().get_node_or_null("HeldBack")
	if back_layer != null and _home.y < -1.0:
		back_layer.add_child(_sprite)   # верхние оружия за телом
		tree_exiting.connect(_sprite.queue_free)
	else:
		add_child(_sprite)
	if get_parent().has_signal(&"fired"):
		get_parent().connect(&"fired", _on_fired)
	_place()


## Где сейчас оружие в руках (мировые координаты): отсюда вылетают снаряды.
func sprite_global() -> Vector2:
	return _sprite.global_position if _sprite != null else get_parent().global_position


func _on_fired(direction: Vector2) -> void:
	if direction != Vector2.ZERO:
		_aim = direction
	_kick = 1.0
	if _weapon_id in [&"mop", &"frying_pan", &"rolling_pin", &"plunger", &"shiv", &"shovel", &"sock", &"rotten_cheese"]:
		return
	_muzzle_flash()
	if _weapon_id in CASING_WEAPONS:
		_eject_casing()


## Вспышка-звезда у дула: 3 кадра за 0.07 с.
func _muzzle_flash() -> void:
	var flash: Sprite2D = Sprite2D.new()
	flash.texture = FLASH
	flash.hframes = 3
	flash.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	flash.z_index = 6
	get_tree().current_scene.add_child(flash)
	flash.global_position = (sprite_global() + _aim * 7.0).round()
	var tw: Tween = flash.create_tween()
	tw.tween_property(flash, "frame", 2, 0.07)
	tw.tween_callback(flash.queue_free)


## Гильза: вылетает вбок-вверх, падает, подпрыгивает и тает на полу.
func _eject_casing() -> void:
	var casing: Sprite2D = Sprite2D.new()
	casing.texture = CASING
	casing.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	casing.z_index = -1
	get_tree().current_scene.add_child(casing)
	var start: Vector2 = sprite_global()
	casing.global_position = start
	var side: Vector2 = _aim.orthogonal() * (1.0 if randf() < 0.5 else -1.0)
	var land: Vector2 = start + side * randf_range(6.0, 10.0) - _aim * 4.0 + Vector2(0.0, 6.0)
	var tw: Tween = casing.create_tween()
	tw.tween_property(casing, "global_position", start + side * 4.0 + Vector2(0.0, -6.0), 0.08)
	tw.parallel().tween_property(casing, "rotation", randf_range(4.0, 8.0), 0.25)
	tw.tween_property(casing, "global_position", land, 0.14).set_ease(Tween.EASE_IN)
	tw.tween_property(casing, "global_position", land + side * 2.0 + Vector2(0.0, -2.0), 0.05)
	tw.tween_property(casing, "global_position", land + side * 3.0, 0.05)
	tw.tween_interval(0.8)
	tw.tween_property(casing, "modulate:a", 0.0, 0.4)
	tw.tween_callback(casing.queue_free)


func _process(delta: float) -> void:
	if _frames.size() > 1:
		_anim_clock += delta
		var idx: int = int(_anim_clock / ANIM_STEP_SEC) % _frames.size()
		if idx != _frame_idx:
			_frame_idx = idx
			_sprite.texture = _frames[idx]
	_kick = maxf(_kick - delta * KICK_DECAY, 0.0)
	_track_left -= delta
	if _track_left <= 0.0:
		_track_left = TRACK_SEC
		_track_target()
	_place()


## Смотрим на ближайшего врага в радиусе атаки (без врагов остаёмся как были).
func _track_target() -> void:
	var best_sq: float = _range_sq
	var found: Vector2 = Vector2.ZERO
	var origin: Vector2 = get_parent().global_position
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		if enemy == null:
			continue
		var d: float = origin.distance_squared_to(enemy.global_position)
		if d < best_sq:
			best_sq = d
			found = enemy.global_position - origin
	if found != Vector2.ZERO:
		_aim = found.normalized()


func _place() -> void:
	var angle: float = snappedf(_aim.angle(), SNAP_RAD)
	var offset: Vector2 = Vector2.ZERO
	_sprite.scale = Vector2.ONE * _held_scale
	_sprite.rotation = angle
	_sprite.flip_v = absf(angle) > PI * 0.5 + 0.01    # чтобы смотря влево, не быть вверх ногами
	match _weapon_id:
		&"mop", &"frying_pan", &"rolling_pin", &"plunger", &"shiv", &"shovel":
			var side: float = -1.0 if _sprite.flip_v else 1.0
			_sprite.rotation = angle + side * (-0.5 + SWING_RAD * sin(_kick * PI))   # взмах
			offset = _aim * 3.0 * _kick
		&"sock", &"rotten_cheese":
			_sprite.scale = Vector2.ONE * _held_scale * (1.0 + 0.4 * _kick)                          # раздувается при вони
			offset = Vector2(roundf(sin(_kick * 40.0)), 0.0)
		_:   # отдача: резкий толчок назад вдоль выстрела, ствол задирается, плавный возврат
			var k: float = _kick * _kick
			offset = -_aim * RECOIL_PX * 1.6 * k
			var lift: float = -1.0 if not _sprite.flip_v else 1.0
			_sprite.rotation = angle + lift * KICK_LIFT * k
			_sprite.scale = Vector2(_held_scale * (1.0 - 0.12 * k), _held_scale * (1.0 + 0.12 * k))
	var base: Vector2 = Vector2(roundf(_home.x), roundf(_home.y))
	var shifted: Vector2 = base + offset
	_sprite.position = Vector2(roundf(shifted.x), roundf(shifted.y))


## Лист из кадров (квадраты шириной = высоте) режем на текстуры, каждая получает обводку тира.
func _build_frames(sheet: Texture2D, tier: int) -> void:
	_frames.clear()
	if sheet == null:
		return
	var img: Image = sheet.get_image()
	var h: int = img.get_height()
	var count: int = maxi(img.get_width() / h, 1)
	for i: int in count:
		var part: Image = img.get_region(Rect2i(i * h, 0, h, h)) if count > 1 else img
		_frames.append(OUTLINE.outlined(ImageTexture.create_from_image(part), tier))


## Обычная загрузка; если редактор ещё не импортировал новый PNG - читаем файл напрямую (удобно для тестов).
static func _load_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	var image: Image = Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image != null else null
