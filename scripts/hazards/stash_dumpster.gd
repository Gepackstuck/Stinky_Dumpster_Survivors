class_name StashDumpster
extends Node2D
## Заначка: мусорный контейнер посреди волны. Постой рядом Balance.STASH_OPEN_SEC (кольцо заполняется) -
## откроется: бесплатный предмет (тир по волне) или говно. Отошёл - прогресс тает. Жадность против жизни.

const SHEET: Texture2D = preload("res://assets/sprites/stash_dumpster.png")

var _sprite: Sprite2D
var _progress: float = 0.0
var _opened: bool = false


func _ready() -> void:
	add_to_group(&"stash")
	z_index = 1
	_sprite = Sprite2D.new()
	_sprite.texture = SHEET
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_sprite.offset = Vector2(0.0, -10.0)
	add_child(_sprite)
	EventBus.wave_ended.connect(func(_w: int) -> void: queue_free())
	EventBus.player_died.connect(queue_free)


func _process(delta: float) -> void:
	if _opened:
		return
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	var near: bool = player != null and player.global_position.distance_to(global_position) <= Balance.STASH_RADIUS
	_progress = clampf(_progress + (delta if near else -delta * 0.6), 0.0, Balance.STASH_OPEN_SEC)
	queue_redraw()
	if _progress >= Balance.STASH_OPEN_SEC:
		_open()


func _draw() -> void:
	if _opened or _progress <= 0.0:
		return
	var t: float = _progress / Balance.STASH_OPEN_SEC
	draw_arc(Vector2(0.0, -10.0), 16.0, -PI * 0.5, -PI * 0.5 + TAU * t, 24, Color(0.97, 1.0, 0.0), 2.0)


func _open() -> void:
	_opened = true
	_sprite.frame = 1
	queue_redraw()
	var item: StringName = ItemLibrary.roll_free_item(GameState.wave)
	if item != &"" and randf() < 0.6:
		GameState.add_item(item)
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -24.0), "ЗАНАЧКА: %s!" % ItemLibrary.title(item), Color(0.97, 1.0, 0.0), 16.0, 1.6, true)
	else:
		var coins: int = Balance.STASH_COINS + GameState.wave * Balance.STASH_COINS / 3
		GameState.coins += coins
		GameState.run_coins_earned += coins
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -24.0), "ЗАНАЧКА: +%d ГОВНА" % coins, Color(0.97, 1.0, 0.0), 16.0, 1.6, true)
	AudioManager.play_sfx(&"combo")
	HitFx.burst(get_tree(), global_position + Vector2(0.0, -10.0), Color(1.0, 0.85, 0.2), 16, 90.0, 3.0, 0.5, true)
	var tw: Tween = create_tween()
	tw.tween_interval(1.5)
	tw.tween_property(self, "modulate:a", 0.0, 0.6)
	tw.tween_callback(queue_free)
