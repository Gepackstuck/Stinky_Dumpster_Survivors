extends RefCounted
## Болтовня компаньонов: раз в 7-16 секунд над головой всплывает короткая реплика.


static func next_delay() -> float:
	return randf_range(7.0, 16.0)


static func say(node: Node2D, lines: Array, color: Color) -> void:
	HitFx.popup(node.get_tree(), node.global_position + Vector2(0.0, -16.0), String(lines[randi() % lines.size()]), color, 10.0, 0.9)
