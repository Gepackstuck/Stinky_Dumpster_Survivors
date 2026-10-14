class_name HealthComponent
extends Node
## Здоровье сущности. Не знает о владельце: общается только сигналами.

signal health_changed(current: float, maximum: float)
signal died

var max_health: float = 1.0
var current_health: float = 1.0
var _is_dead: bool = false


## Задать максимум и полностью восстановить здоровье (в т.ч. при повторном спавне из пула).
func setup(max_hp: float) -> void:
	max_health = max_hp
	current_health = max_hp
	_is_dead = false
	health_changed.emit(current_health, max_health)


func take_damage(amount: float) -> void:
	if _is_dead or amount <= 0.0:
		return
	current_health = maxf(current_health - amount, 0.0)
	health_changed.emit(current_health, max_health)
	if current_health <= 0.0:
		_is_dead = true
		died.emit()


func heal(amount: float) -> void:
	if _is_dead or amount <= 0.0:
		return
	current_health = minf(current_health + amount, max_health)
	health_changed.emit(current_health, max_health)


func is_dead() -> bool:
	return _is_dead
