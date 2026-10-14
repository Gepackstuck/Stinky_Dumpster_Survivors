extends BossBrain
## Крыса-ворюга: удирает от игрока, с неё падает куча добра. У стены не застревает: скользит вдоль неё,
## а из угла уходит к центру арены.

const WALL_MARGIN: float = 34.0


func physics_tick(_delta: float) -> void:
	var pos: Vector2 = boss.global_position
	var away: Vector2 = -direction_to_target()
	var edge: float = Balance.ARENA_SIZE
	var blocked_x: bool = (pos.x < WALL_MARGIN and away.x < 0.0) or (pos.x > edge - WALL_MARGIN and away.x > 0.0)
	var blocked_y: bool = (pos.y < WALL_MARGIN and away.y < 0.0) or (pos.y > edge - WALL_MARGIN and away.y > 0.0)
	var center: Vector2 = Vector2(edge, edge) * 0.5
	var dir: Vector2 = away
	if blocked_x and blocked_y:
		dir = pos.direction_to(center)  # угол: наружу некуда, уходим через середину
	elif blocked_x:
		dir = Vector2(0.0, signf(away.y) if absf(away.y) > 0.2 else signf(center.y - pos.y))
	elif blocked_y:
		dir = Vector2(signf(away.x) if absf(away.x) > 0.2 else signf(center.x - pos.x), 0.0)
	boss.forced_velocity = dir.normalized() * float(Balance.ENEMIES[&"looter"]["speed"]) * WaveRules.speed_mult(GameState.wave)
	boss.forced_sec = 0.12
