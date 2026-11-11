extends Node
## Показ ограниченного поворота: тело существа качается от -40° до +40° вокруг вертикали, камера 55° над землёй.
## Кадры: tools/_hd_raw/yaw/<имя>_NN.png. Имя модели: переменная MESH. Оконный режим.

const FRAMES: int = 24
var _name: String = "frog_inf"


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if OS.get_environment("MESH") != "":
		_name = OS.get_environment("MESH")
	_run.call_deferred()


func _run() -> void:
	var env: WorldEnvironment = WorldEnvironment.new()
	var e: Environment = Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.03, 0.03, 0.04)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.42, 0.43, 0.5)
	e.ambient_light_energy = 0.7
	env.environment = e
	add_child(env)
	var sun: DirectionalLight3D = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48.0, -35.0, 0.0)
	sun.light_color = Color(0.7, 0.78, 1.0)
	sun.light_energy = 0.9
	sun.shadow_enabled = true
	add_child(sun)
	var lamp: OmniLight3D = OmniLight3D.new()
	lamp.position = Vector3(1.5, 2.8, 2.5)
	lamp.light_color = Color(1.0, 0.8, 0.55)
	lamp.light_energy = 3.0
	lamp.omni_range = 12.0
	lamp.shadow_enabled = true
	add_child(lamp)
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
	var doc: GLTFDocument = GLTFDocument.new()
	var state: GLTFState = GLTFState.new()
	doc.append_from_file(ProjectSettings.globalize_path("res://tools/_hd_raw/mesh/%s.glb" % _name), state)
	var holder: Node3D = Node3D.new()
	add_child(holder)
	holder.add_child(doc.generate_scene(state))
	holder.scale = Vector3.ONE * 1.9
	var cam: Camera3D = Camera3D.new()
	cam.fov = 30.0
	add_child(cam)
	var rad: float = deg_to_rad(55.0)
	cam.position = Vector3(0.0, sin(rad) * 7.0, cos(rad) * 7.0)
	cam.look_at(Vector3(0.0, 0.7, 0.0))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tools/_hd_raw/yaw"))
	for i: int in FRAMES:
		holder.rotation_degrees.y = sin(float(i) / FRAMES * TAU) * 40.0
		await get_tree().create_timer(0.15).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_hd_raw/yaw/%s_%02d.png" % [_name, i]))
	print("YAW DONE")
	get_tree().quit()
