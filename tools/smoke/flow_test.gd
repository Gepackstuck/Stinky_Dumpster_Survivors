extends Node
## Проверка цикла экранов: меню -> кладбище -> книга оружия -> арена -> кладбище -> меню. Ошибки смотреть в консоли.


func _ready() -> void:
	var runner: Node = Node.new()
	runner.set_script(load("res://tools/smoke/flow_runner.gd"))
	get_tree().root.add_child.call_deferred(runner)
	get_tree().change_scene_to_file.call_deferred("res://scenes/ui/main_menu.tscn")
