class_name HeroFeet
extends RefCounted
## СГЕНЕРИРОВАНО tools/gen_shoes.py - не править руками.
## Низ ступней героя (px от центра кадра) по рядам листа: бок, спина, лицо.

const BOTTOM: Dictionary = {
	&"hobo": [14, 14, 14],
	&"squid": [14, 14, 14],
	&"clerk": [14, 14, 14],
	&"janitor": [14, 14, 14],
	&"uncle_vitya": [14, 14, 14],
	&"blogger": [14, 14, 14],
	&"granny": [14, 14, 14],
	&"courier": [14, 14, 14],
	&"pigeon": [14, 14, 14],
	&"punk": [14, 14, 14],
	&"shawarma": [14, 14, 14],
	&"guard": [14, 14, 14],
	&"student": [14, 14, 14],
	&"plumber": [14, 14, 14],
	&"dacha": [14, 14, 14],
	&"skater": [14, 14, 14],
	&"slime": [11, 11, 11],
}


static func bottom(hero: StringName, row: int) -> float:
	return float((BOTTOM.get(hero, [15, 15, 15]) as Array)[clampi(row, 0, 2)])
