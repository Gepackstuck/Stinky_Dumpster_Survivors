class_name HurtboxComponent
extends Area2D
## Область, в которую прилетает урон. Слой/маска задаются в сцене.
## invulnerability_sec > 0 — после попадания игнорирует удары это время.

signal hurt(damage: float)

@export var invulnerability_sec: float = 0.0

var _invulnerable_left: float = 0.0


func _ready() -> void:
	set_physics_process(false)


## Принять удар. Возвращает true, если урон прошёл.
func receive_hit(damage: float) -> bool:
	if _invulnerable_left > 0.0:
		return false
	hurt.emit(damage)
	if invulnerability_sec > 0.0:
		_invulnerable_left = invulnerability_sec
		set_physics_process(true)
	return true


func _physics_process(delta: float) -> void:
	_invulnerable_left -= delta
	if _invulnerable_left <= 0.0:
		_invulnerable_left = 0.0
		set_physics_process(false)
