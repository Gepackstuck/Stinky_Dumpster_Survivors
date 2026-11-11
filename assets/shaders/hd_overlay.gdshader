shader_type canvas_item;
// Реалистичный стиль: виньетка, зерно плёнки и ползущий грязный туман поверх мира (под интерфейсом).

uniform float vignette = 0.55;
uniform float grain = 0.05;
uniform float fog = 0.10;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	vec2 uv = UV;
	float d = distance(uv, vec2(0.5)) * 1.35;
	float v = smoothstep(0.35, 1.0, d) * vignette;
	float n = noise(uv * vec2(5.0, 3.0) + vec2(TIME * 0.03, TIME * 0.011)) * 0.6 + noise(uv * vec2(11.0, 7.0) - vec2(TIME * 0.02, 0.0)) * 0.4;
	float f = smoothstep(0.45, 0.9, n) * fog * (0.4 + d);   // туман гуще по краям: центр боя чистый
	float g = (hash(uv * 900.0 + fract(TIME) * 37.0) - 0.5) * grain;
	vec3 col = mix(vec3(0.0), vec3(0.42, 0.44, 0.36), f / max(f + v, 0.001));
	COLOR = vec4(col + g, clamp(v + f + abs(g), 0.0, 0.95));
}
