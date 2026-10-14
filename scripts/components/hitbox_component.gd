class_name HitboxComponent
extends Area2D
## Область, которой наносим урон при контакте. Пока пересекается с HurtboxComponent —
## каждый физический кадр пытается ударить; частоту ограничивает неуязвимость у Hurtbox.

@export var damage: float = 0.0

var _targets: Array[HurtboxComponent] = []


func _ready() -> void:
	area_entered.connect(_on_area_entered)
	area_exited.connect(_on_area_exited)
	set_physics_process(false)


func _exit_tree() -> void:
	_targets.clear()
	set_physics_process(false)


func _physics_process(_delta: float) -> void:
	for target: HurtboxComponent in _targets:
		if is_instance_valid(target):
			target.receive_hit(damage)


func _on_area_entered(area: Area2D) -> void:
	if area is HurtboxComponent:
		_targets.append(area)
		set_physics_process(true)


func _on_area_exited(area: Area2D) -> void:
	if area is HurtboxComponent:
		_targets.erase(area)
		if _targets.is_empty():
			set_physics_process(false)
