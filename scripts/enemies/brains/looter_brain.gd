extends BossBrain
## Крыса-ворюга: удирает от игрока (отрицательная скорость), с неё падает куча добра.


func physics_tick(_delta: float) -> void:
	boss.speed_mult = -1.0
