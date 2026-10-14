shader_type canvas_item;
// Заливка спрайта цветом на время попадания (amount 0..1). Прозрачность спрайта сохраняется.

uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float amount : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	vec4 base = texture(TEXTURE, UV) * COLOR;
	COLOR = vec4(mix(base.rgb, flash_color.rgb, amount), base.a);
}
