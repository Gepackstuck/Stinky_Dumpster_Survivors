"""Листы героев кладбища: у каждого свой цвет, комплекция и «причёска». assets/sprites/player_<id>.png
Берёт рисовалки героя из gen_art и подменяет в их исходнике размеры тела и выросты на голове. Запуск из корня: python3 tools/gen_heroes.py"""
import inspect
import re
import sys

sys.path.insert(0, "tools")
import gen_art as ga
from PIL import Image

# id: (цвет, rx, ry, выросты на голове, код выростов)
HEROES = {
    "hobo": (ga.GREEN, 9, 8, None),
    "squid": (ga.BLUE, 8, 9,
              "line(tent, [(8, 5 + bob), (6 + sway, 2 + bob)], 1); line(tent, [(12, 4 + bob), (12 - sway, 0 + bob)], 1); line(tent, [(16, 5 + bob), (18 - sway, 2 + bob)], 1)"),
    "clerk": (ga.GREY, 7, 9, "rect(tent, 8, 2 + bob, 15, 5 + bob)"),
    "janitor": (ga.YELLOW, 10, 7, "rect(tent, 6, 2 + bob, 17, 5 + bob); rect(tent, 17, 4 + bob, 21, 5 + bob)"),
    "uncle_vitya": (ga.RED, 9, 8,
                    "line(tent, [(9, 4 + bob), (8, 2 + bob)], 0); line(tent, [(12, 4 + bob), (12, 1 + bob)], 0); line(tent, [(15, 4 + bob), (16, 2 + bob)], 0)"),
    "blogger": (ga.PINK, 7, 7, "line(tent, [(12, 5 + bob), (12, 3 + bob)], 1); blob(tent, 12, 2 + bob, 3, 2, rng, 0.2, 8)"),
}

_cache = {}


def variant_fn(name, rx, ry, tent_code):
    key = (name, rx, ry, tent_code)
    if key in _cache:
        return _cache[key]
    src = inspect.getsource(getattr(ga, name))
    src = re.sub(r"def %s\(" % name, "def %s_v(" % name, src, count=1)
    src = re.sub(r"blob\(body, 12, 12 \+ bob, 9, 8,", "blob(body, 12, 12 + bob, %d, %d," % (rx, ry), src, count=1)
    if tent_code:
        src = re.sub(r"line\(tent, \[.*?\], 2\)", tent_code, src, count=1)
    exec(src, ga.__dict__)
    _cache[key] = ga.__dict__[name + "_v"]
    return _cache[key]


def build(hero_id):
    color, rx, ry, tent_code = HEROES[hero_id]
    old = ga.GREEN
    ga.GREEN = color
    try:
        side = variant_fn("draw_player", rx, ry, tent_code)
        up = variant_fn("draw_player_up", rx, ry, tent_code)
        down = variant_fn("draw_player_down", rx, ry, tent_code)
        rows = [ga.sheet([side(0), side(1), side(0), side(1)]),
                ga.sheet([up(0), up(1), up(0), up(1)]),
                ga.sheet([down(0, 0), down(1, 1), down(0, 2), down(1, 3)])]
    finally:
        ga.GREEN = old
    out = ga.new_img(rows[0].size[0], rows[0].size[1] * 3)
    for i, r in enumerate(rows):
        out.paste(r, (0, i * rows[0].size[1]))
    return out


if __name__ == "__main__":
    preview = Image.new("RGBA", (len(HEROES) * 30, 3 * 30), (60, 40, 20, 255))
    for i, hero_id in enumerate(HEROES):
        sheet = build(hero_id)
        sheet.save("assets/sprites/player_%s.png" % hero_id)
        for r in range(3):
            cell = sheet.crop((0, r * 26, 26, r * 26 + 26))
            preview.alpha_composite(cell, (i * 30 + 2, r * 30 + 2))
    preview.resize((preview.width * 6, preview.height * 6), Image.NEAREST).save("tools/_preview/heroes.png")
    print("ok")
