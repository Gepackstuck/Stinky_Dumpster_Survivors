class_name FlavorText
extends RefCounted
## Случайные подписи для экранов. Каждый раз — другая фраза.

const DEATH_LINES: Array[String] = [
	"Ты умер, как лох",
	"Помойка победила",
	"Тебя съели. Невкусно, но съели",
	"Скончался от кринжа",
	"Кишки наружу, мораль внутри",
	"Ну и чё ты ждал?",
	"Ты теперь удобрение",
	"Мухи оценили твой труд",
	"Тебя сожрал кальмар в кепке",
	"RIP. Никто не заметил",
	"Позор. Зато красиво",
	"Минус один. Помойка не заметила",
]

const WIN_LINES: Array[String] = [
	"Ты выиграл и нахуя?",
	"Ты выжил. Но зачем?",
	"Победа! Пахнет всё так же",
	"Ты выиграл. Помойке пофиг",
	"Поздравляю, герой говна",
	"Ура. И что дальше?",
]

static var _last_death: int = -1
static var _last_win: int = -1


static func random_death() -> String:
	_last_death = _pick(DEATH_LINES, _last_death)
	return DEATH_LINES[_last_death]


## Пока не используется: экран победы появится в Шаге 7.
static func random_win() -> String:
	_last_win = _pick(WIN_LINES, _last_win)
	return WIN_LINES[_last_win]


# Не повторяет предыдущую фразу два раза подряд.
static func _pick(lines: Array[String], last: int) -> int:
	var index: int = randi() % lines.size()
	if index == last:
		index = (index + 1) % lines.size()
	return index
