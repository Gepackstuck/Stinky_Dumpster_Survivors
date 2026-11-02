extends Node2D
## Витрина обуви героев (= заряд рывка): все герои в три ряда - готов, наполовину, пусто; боком и анфас; один шагает.
## Кадры tools/_preview/shoes_shot_*.png. Пишет SHOES OK.

const ORDER: Array[StringName] = [&"hobo", &"squid", &"clerk", &"janitor", &"uncle_vitya", &"blogger", &"granny", &"courier", &"pigeon", &"punk", &"shawarma", &"guard", &"student", &"plumber", &"dacha", &"skater", &"slime"]

var _shoes: Array[HeroShoes] = []


func _ready() -> void:
	Profile.sandbox = true
	RenderingServer.set_default_clear_color(Color(0.42, 0.27, 0.15))
	var cam: Camera2D = Camera2D.new()
	cam.zoom = Vector2(1.0, 1.0)
	cam.position = Vector2(240.0, 135.0)
	add_child(cam)
	for r: int in 3:   # ряд: заряд 1.0 / 0.5 / 0.0
		for i: int in ORDER.size():
			var hero: Node2D = Node2D.new()
			hero.position = Vector2(16.0 + i * 27.0, 40.0 + r * 80.0)
			add_child(hero)
			var sprite: Sprite2D = Sprite2D.new()
			sprite.name = &"Sprite2D"
			sprite.texture = CharacterLibrary.sprite_sheet(ORDER[i])
			sprite.hframes = 4
			sprite.vframes = 3
			sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			hero.add_child(sprite)
			var anim: FrameAnimatorComponent = FrameAnimatorComponent.new()
			anim.name = &"FrameAnimator"
			anim.sprite = sprite
			anim.row = 2 if i % 2 == 0 else 0
			anim.active = r == 0 and i % 3 == 0
			hero.add_child(anim)
			var shoes: HeroShoes = HeroShoes.new()
			hero.add_child(shoes)
			shoes.set_hero(ORDER[i])
			(shoes.get(&"_part") as Array).assign([1.0, 1.0] if r == 0 else ([0.5, 1.0] if r == 1 else [0.0, 0.0]))
			_shoes.append(shoes)
	_run.call_deferred()


func _run() -> void:
	for k: int in 3:
		await get_tree().create_timer(0.19).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/shoes_shot_%d.png" % k))
	print("SHOES OK" if _shoes.size() == ORDER.size() * 3 else "SHOES FAIL")
	get_tree().quit()
