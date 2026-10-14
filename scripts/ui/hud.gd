class_name Hud
extends CanvasLayer
## HUD: полоски HP/XP, уровень, убийства. Обновляется только при изменении значений.

@onready var _hp_bar: TextureProgressBar = $Root/HpBar
@onready var _xp_bar: TextureProgressBar = $Root/XpBar
@onready var _level_label: Label = $Root/LevelLabel
@onready var _kills_label: Label = $Root/KillsLabel

var _last_hp: float = -1.0
var _last_level: int = -1
var _last_kills: int = -1
var _last_xp: int = -1


func _process(_delta: float) -> void:
	if GameState.hp != _last_hp or GameState.max_hp != _hp_bar.max_value:
		_last_hp = GameState.hp
		_hp_bar.max_value = maxf(GameState.max_hp, 1.0)
		_hp_bar.value = GameState.hp
	if GameState.xp != _last_xp or GameState.xp_to_next != int(_xp_bar.max_value):
		_last_xp = GameState.xp
		_xp_bar.max_value = maxf(GameState.xp_to_next, 1)
		_xp_bar.value = GameState.xp
	if GameState.level != _last_level:
		_last_level = GameState.level
		_level_label.text = "УР. %d" % GameState.level
	if GameState.kills != _last_kills:
		_last_kills = GameState.kills
		_kills_label.text = "УБИТО %d" % GameState.kills
