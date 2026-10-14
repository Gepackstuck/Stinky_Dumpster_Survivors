shader_type canvas_item;
// Заливка спрайта цветом на время попадания (amount 0..1) + тонкая светлая обводка вокруг силуэта,
// чтобы персонажи и враги выделялись на земле. Кадры листа имеют 1 px прозрачного поля — обводка не обрезается.

uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 outline_color : source_color = vec4(1.0, 1.0, 1.0, 0.8);

void fragment() {
	vec4 base = texture(TEXTURE, UV) * COLOR;
	vec2 px = TEXTURE_PIXEL_SIZE;
	float around = max(max(texture(TEXTURE, UV + vec2(px.x, 0.0)).a, texture(TEXTURE, UV - vec2(px.x, 0.0)).a),
			max(texture(TEXTURE, UV + vec2(0.0, px.y)).a, texture(TEXTURE, UV - vec2(0.0, px.y)).a));
	if (base.a < 0.1 && around > 0.1) {
		COLOR = outline_color;
	} else {
		COLOR = vec4(mix(base.rgb, flash_color.rgb, amount), base.a);
	}
}
