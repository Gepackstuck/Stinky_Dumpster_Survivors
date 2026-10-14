class_name Hud
extends CanvasLayer
## HUD: HP и XP полоски с цифрами и «грязным» цветом, значок уровня, таймер, волна.
## Обновляется только при изменении значений.

const URINE: Color = Color(1.0, 0.93, 0.0)       # мало HP — ярко-жёлтый, как моча
const HP_CURVE: float = 2.0                      # >1: жёлтый держится дольше, красный только у почти полного HP
const HP_FULL: Color = Color(1.0, 0.0, 0.2)      # много HP — красный
const POOP: Color = Color(0.58, 0.34, 0.12)      # мало опыта — цвет дерьма
const XP_FULL: Color = Color(0.2235, 1.0, 0.0784)  # много опыта — кислотно-зелёный
const XP_CURVE: float = 2.2                      # >1: дерьмовый цвет XP держится дольше

@onready var _hp_bar: TextureProgressBar = $Root/HpBar
@onready var _hp_label: Label = $Root/HpLabel
@onready var _xp_bar: TextureProgressBar = $Root/XpBar
@onready var _xp_label: Label = $Root/XpLabel
@onready var _level_label: Label = $Root/LevelBadge/LevelLabel
@onready var _timer_label: Label = $Root/TimerLabel
@onready var _wave_label: Label = $Root/WaveLabel

var _last_hp: float = -1.0
var _last_max_hp: float = -1.0
var _last_level: int = -1
var _last_xp: int = -1
var _last_xp_max: int = -1
var _last_second: int = -1
var _last_wave: int = -1


func _process(_delta: float) -> void:
	if GameState.hp != _last_hp or GameState.max_hp != _last_max_hp:
		_last_hp = GameState.hp
		_last_max_hp = GameState.max_hp
		_hp_bar.max_value = maxf(GameState.max_hp, 1.0)
		_hp_bar.value = GameState.hp
		_hp_bar.tint_progress = URINE.lerp(HP_FULL, pow(clampf(GameState.hp / maxf(GameState.max_hp, 1.0), 0.0, 1.0), HP_CURVE))
		_hp_label.text = "%d/%d" % [ceili(GameState.hp), int(GameState.max_hp)]
	if GameState.xp != _last_xp or GameState.xp_to_next != _last_xp_max:
		_last_xp = GameState.xp
		_last_xp_max = GameState.xp_to_next
		_xp_bar.max_value = maxf(GameState.xp_to_next, 1)
		_xp_bar.value = GameState.xp
		_xp_bar.tint_progress = POOP.lerp(XP_FULL, pow(clampf(float(GameState.xp) / maxf(GameState.xp_to_next, 1), 0.0, 1.0), XP_CURVE))
		_xp_label.text = "%d/%d" % [GameState.xp, GameState.xp_to_next]
	if GameState.level != _last_level:
		_last_level = GameState.level
		_level_label.text = "УР.%d" % GameState.level
	var second: int = ceili(GameState.wave_time_left)
	if second != _last_second:
		_last_second = second
		_timer_label.text = str(second)
	if GameState.wave != _last_wave:
		_last_wave = GameState.wave
		_wave_label.text = "ВОЛНА %d/%d" % [GameState.wave, Balance.WAVE_COUNT]
