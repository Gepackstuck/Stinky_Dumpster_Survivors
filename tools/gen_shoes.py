#!/usr/bin/env python3
"""Обувь героев = индикатор рывка. У каждого героя своя пара: готовая - яркая, на перезарядке - серая
(в игре наливается цветом снизу вверх). Лист на героя: 4 клетки 8x6 -
[бок цветной, анфас цветной, бок серый, анфас серый]; носок смотрит вправо.
Ещё пишет scripts/systems/hero_feet.gd - где у героя ступни (низ спрайта), найдено по листу героя.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_shoes.py -> assets/sprites/shoes_<id>.png, превью tools/_preview/shoes.png"""
import os
import numpy as np
from PIL import Image
from pix import *

CW, CH = 8, 6
HEROES = ["hobo", "squid", "clerk", "janitor", "uncle_vitya", "blogger", "granny", "courier", "pigeon", "punk",
          "shawarma", "guard", "student", "plumber", "dacha", "skater", "slime", "gopnik_jock", "cat"]
SILVER = (200, 205, 215); LIME = (150, 255, 40); NAVY = (30, 40, 110); FELT = (150, 150, 150)
SOCK = (235, 235, 225); TOE = (240, 160, 150); ARMY = (60, 80, 40); RUBBER = (40, 90, 200)

# тип, верх, подошва, акцент
SPEC = {
    "hobo": ("torn", BROWN, BLACK, TOE),            # рваные ботинки, палец наружу
    "squid": ("galosh", PINK, (150, 0, 120), WHITE),  # розовые калоши на щупальцах
    "clerk": ("dress", (25, 25, 30), BLACK, WHITE),  # лакированные туфли
    "janitor": ("boot", ORANGE, BLACK, YELLOW),      # рабочие резиновые сапоги
    "uncle_vitya": ("flip", (40, 90, 230), (20, 50, 160), SOCK),   # шлёпки с носками
    "blogger": ("sneaker", WHITE, PINK, CYAN),       # белые кроссы с неоновой подошвой
    "granny": ("valenok", FELT, BLACK, WHITE),       # валенки с калошами
    "courier": ("sneaker", YELLOW, (60, 60, 60), GREEN),
    "pigeon": ("sneaker", RED, WHITE, WHITE),        # мелкие красные кеды на лапках
    "punk": ("boot", BLACK, (60, 60, 60), RED),      # берцы, красные шнурки
    "shawarma": ("slipper", SILVER, GREY, YELLOW),   # тапки из фольги
    "guard": ("boot", ARMY, BLACK, (120, 140, 80)),  # кирзачи
    "student": ("sneaker", RED, WHITE, WHITE),       # конверсы
    "plumber": ("boot", RUBBER, NAVY, CYAN),         # синие резиновые сапоги
    "dacha": ("galosh", DGREEN, BLACK, GREEN),       # калоши
    "skater": ("sneaker", CYAN, WHITE, BLUE),        # скейтерские кеды
    "slime": ("croc", LIME, (40, 140, 20), BLACK),   # кроксы
    "gopnik_jock": ("sneaker", WHITE, BLACK, BLUE),  # кроссы с рынка, три полоски
    "cat": ("boot", (120, 60, 25), BLACK, YELLOW),   # кот в сапогах
}


def side(kind, up, sole, acc):
    c = Canvas(CW, CH)
    if kind == "sneaker":
        c.rect(1, 2, 5, 3, up); c.rect(5, 3, 7, 3, up); c.rect(1, 4, 7, 4, sole); c.pts([(3, 2), (4, 2)], acc)
    elif kind == "boot":
        c.rect(1, 0, 4, 3, up); c.rect(4, 2, 7, 3, up); c.rect(1, 4, 7, 4, sole); c.pts([(2, 1), (3, 1), (2, 2)], acc)
    elif kind == "torn":
        c.rect(1, 1, 5, 3, up); c.rect(5, 2, 6, 3, up); c.rect(1, 4, 5, 4, sole); c.pts([(7, 3), (7, 4), (6, 4)], acc); c.px(3, 2, BLACK)
    elif kind == "galosh":
        c.rect(1, 2, 6, 4, up); c.px(7, 4, up); c.px(2, 2, acc); c.rect(1, 4, 7, 4, sole)
    elif kind == "dress":
        c.rect(1, 2, 4, 3, up); c.rect(4, 3, 7, 3, up); c.rect(1, 4, 7, 4, sole); c.px(5, 3, acc); c.px(2, 2, acc)
    elif kind == "flip":
        c.rect(2, 0, 5, 3, acc); c.px(6, 3, acc); c.line(3, 2, 5, 3, up); c.rect(1, 4, 7, 4, sole)
    elif kind == "valenok":
        c.rect(1, 0, 4, 3, up, dither=WHITE); c.rect(4, 2, 6, 3, up); c.rect(1, 4, 7, 4, sole); c.px(7, 3, sole)
    elif kind == "slipper":
        c.rect(1, 3, 7, 3, up, dither=WHITE); c.rect(3, 2, 6, 2, up); c.rect(1, 4, 7, 4, sole); c.px(5, 2, acc)
    elif kind == "croc":
        c.rect(1, 2, 6, 3, up); c.rect(6, 3, 7, 3, up); c.rect(1, 4, 7, 4, sole); c.pts([(3, 2), (5, 2), (4, 3)], acc); c.line(1, 1, 2, 2, up)
    return c


def front(kind, up, sole, acc):
    c = Canvas(CW, CH)
    tall = kind in ("boot", "valenok", "flip")
    top = 0 if tall else 2
    if kind == "flip":
        c.rect(2, 0, 5, 3, acc); c.line(2, 3, 5, 3, up); c.rect(2, 4, 5, 4, sole); c.px(3, 2, up); c.px(4, 2, up)
    else:
        c.rect(2, top, 5, 3, up, dither=WHITE if kind == "valenok" else None)
        c.rect(2, 4, 5, 4, sole)
        if kind in ("sneaker", "boot"): c.pts([(3, top + (1 if tall else 0)), (4, top + (1 if tall else 0))], acc)
        if kind == "torn": c.px(5, 3, acc)
        if kind == "croc": c.pts([(3, 2), (4, 3)], acc)
        if kind in ("dress", "galosh"): c.px(3, top, acc)
    return c


def grey(a):
    g = a.copy().astype(float)
    lum = (0.3 * g[:, :, 0] + 0.59 * g[:, :, 1] + 0.11 * g[:, :, 2]) * 0.55 + 30
    for k in range(3): g[:, :, k] = lum
    g[:, :, 3] = a[:, :, 3]
    return g.clip(0, 255).astype(np.uint8)


def feet_y(h):
    im = np.array(Image.open(f"assets/sprites/player_{h}.png").convert("RGBA"))
    fw, fh = im.shape[1] // 4, im.shape[0] // 3
    bots = []
    for r in range(3):
        fr = im[r * fh:(r + 1) * fh, 0:fw, 3] > 0
        bots.append(int(np.nonzero(fr.any(1))[0].max()) - fh // 2)
    return fh, bots


if __name__ == "__main__":
    os.makedirs("tools/_preview", exist_ok=True)
    sheets = []
    feet = {}
    for h in HEROES:
        kind, up, sole, acc = SPEC[h]
        s = side(kind, up, sole, acc).finish(BLACK, WHITE)
        f = front(kind, up, sole, acc).finish(BLACK, WHITE)
        out = Image.new("RGBA", (CW * 4, CH), (0, 0, 0, 0))
        for i, a in enumerate((s, f, grey(s), grey(f))):
            im = Image.fromarray(a); out.paste(im, (i * CW + (CW - im.width) // 2, CH - im.height), im)
        out.save(f"assets/sprites/shoes_{h}.png"); sheets.append(out)
        # значки товара в Ларьке: пара обуви крупно (32) и мелко (16)
        pair = Image.fromarray(s)
        for size, k, p1, p2 in ((32, 2, (1, 5), (15, 14)), (16, 1, (0, 3), (8, 8))):
            icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            big = pair.resize((pair.width * k, pair.height * k), Image.NEAREST)
            icon.paste(big, p1, big)       # пара вразбежку, не налезая
            icon.paste(big, p2, big)
            icon.save(f"assets/ui/item_shoes_{h}{'' if size == 32 else '_s'}.png")
        feet[h] = feet_y(h)
    lines = ["class_name HeroFeet", "extends RefCounted",
             "## СГЕНЕРИРОВАНО tools/gen_shoes.py - не править руками.",
             "## Низ ступней героя (px от центра кадра) по рядам листа: бок, спина, лицо.", "",
             "const BOTTOM: Dictionary = {"]
    for h in HEROES:
        lines.append(f'\t&"{h}": [{", ".join(str(b) for b in feet[h][1])}],')
    lines += ["}", "", "", "static func bottom(hero: StringName, row: int) -> float:",
              "\treturn float((BOTTOM.get(hero, [15, 15, 15]) as Array)[clampi(row, 0, 2)])", ""]
    open("scripts/systems/hero_feet.gd", "w").write("\n".join(lines))
    k = 6; prev = Image.new("RGBA", (CW * 4 * k + 16, len(sheets) * (CH * k + 4) + 8), (70, 45, 25, 255))
    for i, s in enumerate(sheets):
        big = s.resize((s.width * k, s.height * k), Image.NEAREST); prev.paste(big, (8, 4 + i * (CH * k + 4)), big)
    prev.save("tools/_preview/shoes.png"); print(prev.size, feet["hobo"], feet["slime"])
