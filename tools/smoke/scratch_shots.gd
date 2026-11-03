extends Node
## Кадры стирания лотерейных билетов: середина стирания и открытый приз. tools/_preview/scratch_N.png. Оконный режим.

func _ready() -> void:
	Profile.sandbox = true
	var tickets: Array[Dictionary] = [{"kind": &"item", "item": &"dead_rat"}, {"kind": &"coins", "coins": 12}, {"kind": &"empty"}, {"kind": &"jackpot", "coins": 100}]
	var sp: ScratchPanel = ScratchPanel.new()
	add_child(sp)
	sp.setup(tickets)
	var times: Array[float] = [0.5, 1.4, 2.6, 3.6, 5.0, 6.4]
	var prev: float = 0.0
	for i: int in times.size():
		await get_tree().create_timer(times[i] - prev).timeout
		prev = times[i]
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/scratch_%d.png" % i))
	print("SCRATCH DONE")
	get_tree().quit()
