extends Node
## Витрина: рендерит героя с каждым носимым предметом и с 1-6 оружиями в PNG (tools/_preview/showcase_*.png).
## Запуск: сцена tools/smoke/showcase.tscn. Печатает SHOWCASE DONE.

const PLAYER: PackedScene = preload("res://scenes/player/player.tscn")
const CELL: Vector2i = Vector2i(80, 64)
const SCALE: int = 3
const WEAPON_ORDER: Array[StringName] = [&"lighter", &"sock", &"slingshot", &"mop", &"laser_pointer", &"slipper"]


func _ready() -> void:
	_run.call_deferred()


func _snap(label_text: String, items: Array[StringName], weapons: Array[StringName], row: int, kick: bool) -> Image:
	GameState.reset_run()
	GameState.items.clear()
	for id: StringName in items:
		GameState.add_item(id)
	GameState.weapons.clear()
	for id: StringName in weapons:
		GameState.weapons.append({"id": id, "tier": 1})
	var vp: SubViewport = SubViewport.new()
	vp.size = CELL
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var center: Vector2 = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE) * 0.5
	var bg: ColorRect = ColorRect.new()
	bg.color = Color(0.4, 0.26, 0.14)
	bg.position = center - Vector2(CELL) * 0.5
	bg.size = Vector2(CELL)
	vp.add_child(bg)
	var player: Node2D = PLAYER.instantiate()
	player.position = center
	vp.add_child(player)
	var layer: CanvasLayer = CanvasLayer.new()
	vp.add_child(layer)
	var label: Label = Label.new()
	label.text = label_text
	label.position = Vector2(2.0, 54.0)
	label.add_theme_color_override(&"font_color", Color(1.0, 1.0, 1.0))
	label.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0))
	layer.add_child(label)
	var anim: FrameAnimatorComponent = player.get_node("FrameAnimator") as FrameAnimatorComponent
	anim.active = false
	anim.row = row
	EventBus.weapons_changed.emit()
	await get_tree().process_frame
	await get_tree().process_frame
	if kick:
		for node: Node in get_tree().get_nodes_in_group(&"weapon_nodes"):
			node.emit_signal(&"fired", Vector2(1.0, -0.4).normalized())
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var image: Image = vp.get_texture().get_image()
	vp.queue_free()
	await get_tree().process_frame
	return image


func _sheet(cells: Array[Image], columns: int, path: String) -> void:
	var rows: int = ceili(float(cells.size()) / float(columns))
	var sheet: Image = Image.create(columns * CELL.x, rows * CELL.y, false, Image.FORMAT_RGBA8)
	for i: int in cells.size():
		cells[i].convert(Image.FORMAT_RGBA8)
		sheet.blit_rect(cells[i], Rect2i(Vector2i.ZERO, CELL), Vector2i((i % columns) * CELL.x, (i / columns) * CELL.y))
	sheet.resize(sheet.get_width() * SCALE, sheet.get_height() * SCALE, Image.INTERPOLATE_NEAREST)
	sheet.save_png(ProjectSettings.globalize_path(path))
	print("SHOWCASE saved ", path)


func _run() -> void:
	# 1) каждый носимый предмет по отдельности, герой лицом к камере
	var cells: Array[Image] = []
	for id: StringName in Balance.ITEMS:
		if ItemLibrary.slot(id) == &"":
			continue
		var one: Array[StringName] = [id]
		cells.append(await _snap(ItemLibrary.title(id).left(14), one, [], 2, false))
	_sheet(cells, 6, "res://tools/_preview/showcase_items.png")
	# 2) оружие: 1..6 штук, в покое / в момент выстрела, лицом и боком
	cells = []
	for kick: bool in [false, true]:
		for row: int in [2, 0]:
			for n: int in range(1, 7):
				var ws: Array[StringName] = []
				for i: int in n:
					ws.append(WEAPON_ORDER[i])
				cells.append(await _snap("%d ОРУЖ." % n, [], ws, row, kick))
	_sheet(cells, 6, "res://tools/_preview/showcase_weapons.png")
	# 3) одетый герой: по предмету на каждую точку + 3 оружия
	var dressed: Array[StringName] = [&"pot", &"dirty_glasses", &"scarf", &"vodka", &"crowbar", &"rubber_boot", &"junk_backpack"]
	cells = []
	for row: int in [2, 0, 1]:
		cells.append(await _snap("ОДЕТ", dressed, [&"lighter", &"mop", &"sock"], row, false))
	_sheet(cells, 3, "res://tools/_preview/showcase_dressed.png")
	print("SHOWCASE DONE")
	get_tree().quit()
