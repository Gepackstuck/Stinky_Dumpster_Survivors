extends Node
## Пулы объектов для снарядов, врагов и XP-пикселей. Autoload: PoolManager.
## TODO(MP1): реальные пулы. Пока acquire() возвращает null.


## Взять объект из пула (или создать новый, если пул пуст).
@warning_ignore("unused_parameter")
func acquire(scene: PackedScene) -> Node:
	# TODO(MP1)
	return null


## Вернуть объект в пул.
@warning_ignore("unused_parameter")
func release(node: Node) -> void:
	# TODO(MP1)
	pass
