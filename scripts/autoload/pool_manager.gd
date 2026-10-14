extends Node
## Пулы объектов для снарядов, врагов и XP-пикселей. Autoload: PoolManager.
## Контракт: acquire() отдаёт узел ВНЕ дерева — вызывающий сам делает add_child()
## и инициализирует состояние. release() убирает узел из дерева и прячет в пул.

const META_POOL_KEY: StringName = &"pool_key"
const META_POOLED: StringName = &"pooled"

var _pools: Dictionary[String, Array] = {}


## Взять объект из пула (или создать новый, если пул пуст).
func acquire(scene: PackedScene) -> Node:
	var key: String = scene.resource_path
	var pool: Array = _pools.get(key, [])
	var instance: Node
	if pool.is_empty():
		instance = scene.instantiate()
		instance.set_meta(META_POOL_KEY, key)
	else:
		instance = pool.pop_back()
	instance.set_meta(META_POOLED, false)
	return instance


## Вернуть объект в пул. Безопасно вызывать из физических колбэков (отложенно).
func release(node: Node) -> void:
	_release_deferred.call_deferred(node)


func _release_deferred(node: Node) -> void:
	if not is_instance_valid(node):
		return
	if node.get_meta(META_POOLED, false):
		return
	if not node.has_meta(META_POOL_KEY):
		node.queue_free()
		return
	var parent: Node = node.get_parent()
	if parent != null:
		parent.remove_child(node)
	node.set_meta(META_POOLED, true)
	var key: String = node.get_meta(META_POOL_KEY)
	if not _pools.has(key):
		_pools[key] = []
	_pools[key].append(node)


func _exit_tree() -> void:
	for pool: Array in _pools.values():
		for node: Node in pool:
			if is_instance_valid(node):
				node.free()
	_pools.clear()
