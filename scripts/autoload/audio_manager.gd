extends Node
## Звуки и музыка. Autoload: AudioManager. Звуки - assets/sfx/<имя>.wav, музыка - assets/music/<имя>.wav (луп).
## Слушает EventBus (смерти, урон, волны, уровни...) - системы сами звук не дёргают.
## Против звуковой каши: один и тот же звук не чаще MIN_GAP, лимит одновременных голосов, лёгкий разброс высоты.
## У частых звуков есть варианты (<имя>_2.wav, <имя>_3.wav) - берётся случайный, чтобы не долбило одно и то же.
## Музыка: боевые треки сменяются от волны к волне, у элиты и боссов свой трек, в меню и на кладбище - свой.

const VOICES: int = 16
const MIN_GAP: Dictionary = {&"enemy_death": 0.05, &"hit": 0.06, &"hit_crit": 0.08, &"shoot": 0.05, &"swing": 0.07, &"pickup": 0.035, &"warn": 0.15}
const DEFAULT_GAP: float = 0.03
const VOLUME_DB: Dictionary = {&"pickup": -13.0, &"hit": -15.0, &"hit_crit": -12.0, &"shoot": -14.0, &"swing": -12.0, &"enemy_death": -9.0,
		&"ui_move": -10.0, &"ui_select": -8.0, &"warn": -8.0, &"player_hurt": -5.0, &"explosion": -6.0, &"truck_horn": -8.0, &"wave_horn": -4.0}
const MUSIC_FADE_SEC: float = 0.8
const BATTLE_TRACKS: Array[StringName] = [&"battle_a", &"battle_b", &"battle_c"]
const PICKUP_SCALE: Array[int] = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]   # подбор подряд - вверх по пентатонике, как в Brotato
const PICKUP_CHAIN_SEC: float = 0.45

var _players: Array[AudioStreamPlayer] = []
var _next: int = 0
var _last_play: Dictionary = {}
var _cache: Dictionary = {}
var _music: AudioStreamPlayer = null
var _music_name: StringName = &""
var _variants: Dictionary = {}   # имя звука -> сколько вариантов лежит в assets/sfx
var _pickup_step: int = 0
var _pickup_last: float = -10.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i: int in VOICES:
		var p: AudioStreamPlayer = AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	_music = AudioStreamPlayer.new()
	add_child(_music)
	EventBus.enemy_died.connect(func(id: StringName, _at: Vector2) -> void:
		play_sfx(&"boss_roar" if Balance.ENEMIES.get(id, {}).has("anim_rows") else &"enemy_death"))
	EventBus.player_hit.connect(func(_d: float) -> void: play_sfx(&"player_hurt"))
	EventBus.xp_collected.connect(func(_a: int) -> void: _play_pickup())
	EventBus.enemy_hurt.connect(func(crit: bool) -> void: play_sfx(&"hit_crit" if crit else &"hit", 0.08))
	EventBus.player_leveled_up.connect(func(_l: int) -> void: play_sfx(&"level_up"))
	EventBus.wave_started.connect(func(_w: int) -> void:
		play_sfx(&"wave_horn")
		play_music(battle_track()))
	EventBus.wave_ended.connect(func(_w: int) -> void: play_music(&"shop"))
	EventBus.boss_spawned.connect(func(_id: StringName) -> void: play_sfx(&"boss_roar"))
	EventBus.dash_used.connect(func(_at: Vector2) -> void: play_sfx(&"dash"))
	EventBus.player_died.connect(func() -> void:
		stop_music()
		play_sfx(&"death"))
	EventBus.run_won.connect(func() -> void:
		stop_music()
		play_sfx(&"win"))
	EventBus.item_combo.connect(func(_c: StringName) -> void: play_sfx(&"combo"))
	EventBus.perk_chosen.connect(func(_p: StringName) -> void: play_sfx(&"buy"))
	EventBus.streak_changed.connect(func(_t: int, _b: float, broken: bool) -> void:
		if broken:
			play_sfx(&"streak_break"))
	EventBus.weapon_fired.connect(func(kind: StringName) -> void: play_sfx(kind, 0.12))
	EventBus.telegraph_shown.connect(func() -> void: play_sfx(&"warn"))
	Settings.changed.connect(_apply_music_volume)
	get_viewport().gui_focus_changed.connect(func(_c: Control) -> void: play_sfx(&"ui_move"))


## Трек волны: элита и боссы - свой, остальные боевые по кругу (каждая волна - следующий).
func battle_track() -> StringName:
	if GameState.wave_kind in [&"boss", &"elite"] or GameState.wave == Balance.WAVE_COUNT:
		return &"boss"
	return BATTLE_TRACKS[maxi(GameState.wave - 1, 0) % BATTLE_TRACKS.size()]


func _play_pickup() -> void:
	var now: float = Time.get_ticks_msec() / 1000.0
	_pickup_step = mini(_pickup_step + 1, PICKUP_SCALE.size() - 1) if now - _pickup_last < PICKUP_CHAIN_SEC else 0
	_pickup_last = now
	play_sfx(&"pickup", 0.0, pow(2.0, PICKUP_SCALE[_pickup_step] / 12.0))


func _variant(sfx_name: StringName) -> StringName:
	if not _variants.has(sfx_name):
		var count: int = 1
		while ResourceLoader.exists("res://assets/sfx/%s_%d.wav" % [sfx_name, count + 1]):
			count += 1
		_variants[sfx_name] = count
	var k: int = randi() % int(_variants[sfx_name])
	return sfx_name if k == 0 else StringName("%s_%d" % [sfx_name, k + 1])


func _stream(sfx_name: StringName, folder: String) -> AudioStream:
	var key: String = folder + String(sfx_name)
	if not _cache.has(key):
		var path: String = "res://assets/%s/%s.wav" % [folder, sfx_name]
		_cache[key] = load(path) if ResourceLoader.exists(path) else null
	return _cache[key]


## Проиграть короткий звук по имени (pitch_var - разброс высоты, чтобы повторы не резали ухо).
func play_sfx(sfx_name: StringName, pitch_var: float = 0.05, pitch: float = 1.0) -> void:
	if Settings.sfx_volume <= 0.0 or Profile.sandbox:   # тесты и боты - без звука
		return
	var now: float = Time.get_ticks_msec() / 1000.0
	if now - float(_last_play.get(sfx_name, -1.0)) < float(MIN_GAP.get(sfx_name, DEFAULT_GAP)):
		return
	var stream: AudioStream = _stream(_variant(sfx_name), "sfx")
	if stream == null:
		return
	_last_play[sfx_name] = now
	var p: AudioStreamPlayer = _players[_next]
	_next = (_next + 1) % _players.size()
	p.stream = stream
	p.pitch_scale = pitch * randf_range(1.0 - pitch_var, 1.0 + pitch_var)
	p.volume_db = linear_to_db(Settings.sfx_volume) + float(VOLUME_DB.get(sfx_name, 0.0))
	p.play()


## Запустить музыкальный луп по имени (тот же - не перезапускает).
func play_music(music_name: StringName) -> void:
	if Profile.sandbox:
		return
	if music_name == _music_name and _music.playing:
		return
	var stream: AudioStreamWAV = _stream(music_name, "music") as AudioStreamWAV
	if stream == null:
		return
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_end = int(stream.get_length() * stream.mix_rate)
	_music_name = music_name
	var tw: Tween = create_tween()
	if _music.playing:
		tw.tween_property(_music, "volume_db", -40.0, MUSIC_FADE_SEC * 0.5)
	tw.tween_callback(func() -> void:
		_music.stream = stream
		_music.volume_db = -40.0
		_music.play())
	tw.tween_property(_music, "volume_db", _music_db(), MUSIC_FADE_SEC)


func stop_music() -> void:
	_music_name = &""
	var tw: Tween = create_tween()
	tw.tween_property(_music, "volume_db", -40.0, MUSIC_FADE_SEC * 0.5)
	tw.tween_callback(_music.stop)


func _music_db() -> float:
	return linear_to_db(maxf(Settings.music_volume, 0.001)) - 6.0


func _apply_music_volume() -> void:
	if _music.playing:
		_music.volume_db = _music_db()
