extends BossBrain
## Яйцо-личинка: стоит и пульсирует, через EGG_HATCH_SEC лопается и выпускает жиртреста (Slasher Egg в Brotato).
## Разбей раньше — получишь немного XP и спокойствие.

var _left: float = Balance.EGG_HATCH_SEC
var _blink: float = 0.0


func physics_tick(delta: float) -> void:
	boss.speed_mult = 0.0
	_left -= delta
	if _left < 1.5:
		_blink -= delta
		if _blink <= 0.0:
			_blink = 0.25
			boss.flash(Color(1.0, 0.0, 0.2))
	if _left <= 0.0:
		boss.hatch_into(&"bruiser")
