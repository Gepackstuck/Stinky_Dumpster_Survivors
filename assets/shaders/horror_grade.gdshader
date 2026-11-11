shader_type canvas_item;
// Цветокоррекция ужаса для ВСЕГО кадра (игра + интерфейс): приглушённые цвета, ржавый оттенок, плотные тени, лёгкое дрожание
// и хроматическая «дрожь» по краям, редкие всплески помех. Неоновые рамки интерфейса становятся грязными, а не мультяшными.

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float saturation = 0.5;
uniform float darken = 1.12;        // >1 - плотнее тени
uniform vec3 tint = vec3(1.06, 0.94, 0.90);
uniform float aberration = 0.0016;
uniform float glitch = 0.5;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453);
}

void fragment() {
	vec2 uv = SCREEN_UV;
	float edge = pow(distance(uv, vec2(0.5)) * 1.4, 2.0);
	float spike = step(0.985, hash(vec2(floor(TIME * 6.0), 3.0))) * glitch;       // редкий всплеск помех
	float band = step(0.96, hash(vec2(floor(uv.y * 40.0), floor(TIME * 8.0)))) * spike;
	vec2 off = vec2(aberration * (0.4 + edge * 2.0) + band * 0.01, 0.0);
	float r = texture(screen_tex, uv + off).r;
	float g = texture(screen_tex, uv).g;
	float b = texture(screen_tex, uv - off).b;
	vec3 c = vec3(r, g, b);
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(vec3(l), c, saturation);
	c = pow(c, vec3(darken)) * tint;
	c += (hash(uv * vec2(1280.0, 720.0) + TIME) - 0.5) * 0.025;                    // зерно
	COLOR = vec4(c, 1.0);
}
