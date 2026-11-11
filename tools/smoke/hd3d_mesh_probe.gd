extends Node
## Проба 3D-модели существа: поворот на 4 стороны и вид на земле под 55°. tools/_preview/hd/04_3d/<имя>_*.png. Оконный режим.
## Имя модели: переменная MESH (по умолчанию frog); файл tools/_hd_raw/mesh/<имя>.glb.

var _name: String = "frog"


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var env_name: String = OS.get_environment("MESH")
	if env_name != "":
		_name = env_name
	_run.call_deferred()


func _load_mesh() -> Node3D:
	var doc: GLTFDocument = GLTFDocument.new()
	var state: GLTFState = GLTFState.new()
	var err: int = doc.append_from_file(ProjectSettings.globalize_path("res://tools/_hd_raw/mesh/%s.glb" % _name), state)
	if err != OK:
		push_error("glb load failed %d" % err)
		return Node3D.new()
	var root: Node3D = doc.generate_scene(state) as Node3D
	var mat: StandardMaterial3D = StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.roughness = 0.6
	if not _name.ends_with("_inf"):   # у «надутых» своя текстура, у остальных цвета вершин
		for n: Node in root.find_children("*", "MeshInstance3D", true, false):
			(n as MeshInstance3D).material_override = mat
	return root


func _run() -> void:
	var env: WorldEnvironment = WorldEnvironment.new()
	var e: Environment = Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.1, 0.1, 0.12)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.5, 0.52, 0.6)
	e.ambient_light_energy = 0.7
	env.environment = e
	add_child(env)
	var sun: DirectionalLight3D = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-40.0, -30.0, 0.0)
	sun.light_energy = 1.1
	sun.shadow_enabled = true
	add_child(sun)
	var holder: Node3D = Node3D.new()
	add_child(holder)
	var mesh: Node3D = _load_mesh()
	holder.add_child(mesh)
	var box: AABB = AABB()
	for n: Node in mesh.find_children("*", "MeshInstance3D", true, false):
		box = (n as MeshInstance3D).get_aabb() if box.size == Vector3.ZERO else box.merge((n as MeshInstance3D).get_aabb())
	print("AABB ", box)
	var cam: Camera3D = Camera3D.new()
	cam.fov = 35.0
	add_child(cam)
	var size: float = maxf(box.size.x, maxf(box.size.y, box.size.z))
	cam.position = box.get_center() + Vector3(0.0, 0.2 * size, 2.6 * size)
	cam.look_at(box.get_center())
	for i: int in 4:
		holder.rotation_degrees.y = i * 90.0
		await get_tree().create_timer(0.4).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/04_3d/%s_вид%d.png" % [_name, i]))
	# на земле: наклонная камера 55°, тот же свет, что в пробе угла
	holder.rotation_degrees.y = 0.0
	var ground: MeshInstance3D = MeshInstance3D.new()
	var plane: PlaneMesh = PlaneMesh.new()
	plane.size = Vector2(30.0, 30.0)
	ground.mesh = plane
	var gm: StandardMaterial3D = StandardMaterial3D.new()
	gm.albedo_texture = load("res://assets/hd/sprites/ground_tile.png")
	gm.normal_enabled = true
	gm.normal_texture = load("res://assets/hd/sprites/ground_tile_n.png")
	gm.uv1_scale = Vector3(6.0, 6.0, 1.0)
	gm.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	ground.material_override = gm
	add_child(ground)
	var lamp: OmniLight3D = OmniLight3D.new()
	lamp.position = Vector3(1.0, 2.5, 2.0)
	lamp.light_color = Color(1.0, 0.8, 0.55)
	lamp.light_energy = 3.0
	lamp.omni_range = 12.0
	lamp.shadow_enabled = true
	add_child(lamp)
	e.background_color = Color(0.03, 0.03, 0.04)
	holder.scale = Vector3.ONE * 2.4
	for a: float in [55.0]:
		var rad: float = deg_to_rad(a)
		cam.fov = 30.0
		cam.position = Vector3(0.0, sin(rad) * 7.0, cos(rad) * 7.0)
		cam.look_at(Vector3(0.0, 0.6, 0.0))
		for k: int in 4:
			holder.rotation_degrees.y = k * 90.0
			await get_tree().create_timer(0.4).timeout
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/04_3d/%s_на_земле%d.png" % [_name, k]))
	print("MESH PROBE DONE")
	get_tree().quit()
