class_name ModPile
extends Node2D
## Куча-лотерея: светится лучами, воняет, жужжит мухами (громче, когда ближе). Вступил - EventBus.pile_stepped,
## после Ларька рулетка модификатора. Исчезает в конце волны, если не вступил.

const SHEET: Texture2D = preload("res://assets/sprites/mod_pile.png")
const FLIES: AudioStream = preload("res://assets/sfx/flies_loop.wav")

var _sprite: Sprite2D
var _sound: AudioStreamPlayer2D
var _t: float = 0.0
var _done: bool = false


func _ready() -> void:
	add_to_group(&"mod_pile")
	z_index = 2
	_sprite = Sprite2D.new()
	_sprite.texture = SHEET
	_sprite.hframes = 4
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_sprite.offset = Vector2(0.0, -12.0)
	add_child(_sprite)
	if not Profile.sandbox:
		_sound = AudioStreamPlayer2D.new()
		var stream: AudioStreamWAV = FLIES.duplicate() as AudioStreamWAV
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_end = int(stream.get_length() * stream.mix_rate)
		_sound.stream = stream
		_sound.max_distance = Balance.PILE_SOUND_DIST
		_sound.volume_db = linear_to_db(maxf(Settings.sfx_volume, 0.01)) - 4.0
		add_child(_sound)
		_sound.play()
	EventBus.wave_ended.connect(func(_w: int) -> void: _vanish())
	EventBus.player_died.connect(_vanish)
	var tw: Tween = create_tween()   # плюхается с неба
	scale = Vector2(1.4, 0.4)
	tw.tween_property(self, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)


func _process(delta: float) -> void:
	_t += delta
	_sprite.frame = int(_t * 8.0) % 4
	_sprite.scale = Vector2.ONE * (1.0 + 0.06 * sin(_t * 5.0))
	if _done:
		return
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player != null and player.global_position.distance_to(global_position) < Balance.PILE_RADIUS:
		_step()


func _step() -> void:
	_done = true
	GameState.roulette_pending = true
	EventBus.pile_stepped.emit()
	AudioManager.play_sfx(&"splat_pile", 0.0)
	AudioManager.play_sfx(&"fart", 0.1)
	HitFx.burst(get_tree(), global_position, Color(0.42, 0.24, 0.12), 26, 110.0, 4.0, 0.7, true)
	HitFx.burst(get_tree(), global_position, Color(1.0, 0.86, 0.24), 14, 80.0, 3.0, 0.6, true)
	HitFx.popup(get_tree(), global_position + Vector2(0.0, -26.0), "НОГА В ГОВНЕ! РУЛЕТКА ПОСЛЕ ЛАРЬКА", Color(1.0, 0.86, 0.24), 22.0, 2.2, true)
	queue_free()


func _vanish() -> void:
	if not _done:
		_done = true
		queue_free()
