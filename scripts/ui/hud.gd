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
var _boss_bars: Array = []   # [{root, fill, label}]
var _boss_scan: float = 0.0


func _process(_delta: float) -> void:
	if GameState.hp != _last_hp or GameState.max_hp != _last_max_hp:
		_last_hp = GameState.hp
		_last_max_hp = GameState.max_hp
		_hp_bar.max_value = maxf(GameState.max_hp, 1.0)
		_hp_bar.value = GameState.hp
		_hp_bar.tint_progress = URINE.lerp(HP_FULL, pow(clampf(GameState.hp / maxf(GameState.max_hp, 1.0), 0.0, 1.0), HP_CURVE))
		_hp_label.text = "%d/%d" % [mini(ceili(GameState.hp), ceili(GameState.max_hp)), ceili(GameState.max_hp)]
	if GameState.xp != _last_xp or GameState.xp_to_next != _last_xp_max:
		_last_xp = GameState.xp
		_last_xp_max = GameState.xp_to_next
		_xp_bar.max_value = maxf(GameState.xp_to_next, 1)
		_xp_bar.value = GameState.xp
		_xp_bar.tint_progress = POOP.lerp(XP_FULL, pow(clampf(float(GameState.xp) / maxf(GameState.xp_to_next, 1), 0.0, 1.0), XP_CURVE))
		_xp_label.text = "%d/%d" % [GameState.xp, GameState.xp_to_next]
	if GameState.level != _last_level:
		_last_level = GameState.level
		_level_label.text = str(GameState.level)
	var second: int = ceili(GameState.wave_time_left)
	if second != _last_second:
		_last_second = second
		_timer_label.text = str(second)
	if GameState.wave != _last_wave:
		_last_wave = GameState.wave
		_wave_label.text = "ВОЛНА %d/%d" % [GameState.wave, Balance.WAVE_COUNT]


func _ready() -> void:
	for i: int in 2:
		var root: Control = Control.new()
		root.position = Vector2(80.0, 236.0 - 17.0 * i)
		root.size = Vector2(320.0, 14.0)
		root.mouse_filter = Control.MOUSE_FILTER_IGNORE
		root.visible = false
		var back: ColorRect = ColorRect.new()
		back.color = Color(0.0, 0.0, 0.0, 0.85)
		back.size = Vector2(320.0, 14.0)
		root.add_child(back)
		var fill: ColorRect = ColorRect.new()
		fill.color = Color(0.85, 0.1, 0.9)
		fill.position = Vector2(2.0, 2.0)
		fill.size = Vector2(316.0, 10.0)
		root.add_child(fill)
		var label: Label = Label.new()
		label.theme = preload("res://assets/ui/theme.tres")
		label.add_theme_color_override(&"font_color", Color.WHITE)
		label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
		label.add_theme_constant_override(&"outline_size", 2)
		label.add_theme_color_override(&"font_outline_color", Color.BLACK)
		label.size = Vector2(320.0, 14.0)
		label.position = Vector2(0.0, -1.0)
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		root.add_child(label)
		$Root.add_child(root)
		_boss_bars.append({"root": root, "fill": fill, "label": label})


func _physics_process(delta: float) -> void:
	_boss_scan -= delta
	if _boss_scan > 0.0:
		return
	_boss_scan = 0.1
	var found: Array = []
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null or not enemy.is_alive():
			continue
		if enemy.enemy_id == Balance.ELITE_ID or Balance.FINAL_BOSS_POOL.has(enemy.enemy_id):
			found.append(enemy)
	for i: int in _boss_bars.size():
		var bar: Dictionary = _boss_bars[i]
		var root: Control = bar["root"]
		if i >= found.size():
			root.visible = false
			continue
		var enemy: EnemyBase = found[i]
		var pair: Vector2 = enemy.health_pair()
		var ratio: float = clampf(pair.x / maxf(pair.y, 1.0), 0.0, 1.0)
		root.visible = true
		(bar["fill"] as ColorRect).size.x = 316.0 * ratio
		var title: String = EnemyNames.title(enemy.enemy_id).to_upper()
		(bar["label"] as Label).text = "%s  %d/%d" % [title, ceili(pair.x), ceili(pair.y)]
