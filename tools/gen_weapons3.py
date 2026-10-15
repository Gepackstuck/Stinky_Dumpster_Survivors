"""Оружие пачки 3: в руках (12x12), иконки (16x16), снаряды. Запуск из корня: python3 tools/gen_weapons3.py"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, BLUE, BROWN, CYAN, GREEN, GREY, PINK, RED, UI, WHITE, YELLOW, blob, finish, line, new_img, new_mask, paint, poly, px, rect, union
from PIL import Image

ORANGE = (255, 120, 0)


def _build(size, layers, dots):
    sil = union(*[m for m, _ in layers])
    img = new_img(size, size)
    for m, c in layers:
        paint(img, m, c)
    out = finish(img, sil)
    for x, y, c in dots:
        px(out, x, y, c)
    return out


def held(layers, dots=()):
    return _build(12, layers, dots)


def icon(layers, dots=()):
    return _build(16, layers, dots)


def hm():
    return new_mask(12, 12)


def im():
    return new_mask(16, 16)


# ---------------------------------------------------------------- в руках (смотрят вправо)
def held_plunger():
    stick = hm(); rect(stick, 0, 5, 7, 6)
    cup = hm(); poly(cup, [(7, 5), (9, 2), (11, 2), (11, 9), (9, 9), (7, 6)])
    return held([(stick, BROWN), (cup, RED)], [(9, 4, WHITE), (10, 3, ORANGE), (10, 8, BLACK), (3, 5, YELLOW)])


def held_shiv():
    blade = hm(); line(blade, [(4, 6), (11, 6)], 1)
    grip = hm(); rect(grip, 0, 5, 4, 7)
    return held([(blade, GREY), (grip, BLUE)], [(10, 6, WHITE), (8, 6, WHITE), (2, 6, WHITE), (6, 7, RED), (1, 5, BLACK)])


def held_shovel():
    shaft = hm(); rect(shaft, 0, 5, 7, 6)
    blade = hm(); poly(blade, [(7, 3), (10, 3), (11, 5), (11, 7), (10, 9), (7, 9)])
    return held([(shaft, BROWN), (blade, GREY)], [(10, 5, WHITE), (9, 4, WHITE), (8, 8, BROWN), (10, 8, BROWN), (0, 5, BLACK), (1, 4, BROWN)])


def held_blowtorch():
    tank = hm(); rect(tank, 0, 3, 4, 8)
    pipe = hm(); rect(pipe, 4, 5, 8, 6)
    nozzle = hm(); rect(nozzle, 8, 4, 9, 7)
    return held([(tank, RED), (pipe, GREY), (nozzle, GREY)], [(1, 4, WHITE), (1, 5, WHITE), (2, 7, BLACK), (10, 5, YELLOW), (10, 6, ORANGE), (11, 5, ORANGE), (11, 6, YELLOW)])


def held_syringe():
    barrel = hm(); rect(barrel, 3, 4, 8, 7)
    plunger = hm(); rect(plunger, 0, 5, 3, 6)
    thumb = hm(); rect(thumb, 0, 3, 1, 8)
    needle = hm(); rect(needle, 8, 5, 11, 6)
    return held([(barrel, WHITE), (plunger, GREY), (thumb, GREY), (needle, GREY)], [(4, 5, GREEN), (5, 5, GREEN), (6, 5, GREEN), (7, 5, GREEN), (4, 6, GREEN), (5, 6, GREEN), (6, 6, GREEN), (11, 5, WHITE), (6, 4, BLACK)])


def held_tin_bomb():
    can = hm(); rect(can, 2, 4, 9, 10)
    lid = hm(); rect(lid, 2, 3, 9, 4)
    fuse = hm(); line(fuse, [(6, 3), (7, 1), (9, 0)], 0)
    return held([(can, GREY), (lid, WHITE), (fuse, BROWN)], [(4, 6, RED), (5, 6, RED), (6, 6, RED), (4, 8, BLACK), (7, 8, BLACK), (10, 0, YELLOW), (11, 0, ORANGE), (9, 9, BLACK)])


def held_extension_cord():
    box = hm(); rect(box, 0, 3, 5, 9)
    rod = hm(); rect(rod, 5, 5, 9, 6)
    return held([(box, WHITE), (rod, GREY)], [(1, 5, BLACK), (3, 5, BLACK), (1, 7, BLACK), (3, 7, BLACK), (2, 3, ORANGE), (10, 4, CYAN), (11, 6, CYAN), (10, 7, WHITE), (9, 5, CYAN), (2, 9, ORANGE)])


HELD = {"plunger": held_plunger, "shiv": held_shiv, "shovel": held_shovel, "blowtorch": held_blowtorch,
        "syringe": held_syringe, "tin_bomb": held_tin_bomb, "extension_cord": held_extension_cord}


# ---------------------------------------------------------------- иконки 16x16
def icon_plunger():
    stick = im(); line(stick, [(2, 14), (9, 6)], 1)
    cup = im(); poly(cup, [(8, 7), (10, 2), (14, 4), (14, 9), (10, 10)])
    return icon([(stick, BROWN), (cup, RED)], [(11, 4, WHITE), (12, 5, ORANGE), (12, 8, BLACK), (5, 11, YELLOW)])


def icon_shiv():
    blade = im(); line(blade, [(6, 9), (14, 1)], 1)
    grip = im(); line(grip, [(2, 13), (6, 9)], 2)
    return icon([(blade, GREY), (grip, BLUE)], [(13, 2, WHITE), (11, 4, WHITE), (9, 6, RED), (3, 12, WHITE), (1, 14, BLACK)])


def icon_shovel():
    shaft = im(); line(shaft, [(1, 14), (9, 6)], 1)
    handle = im(); rect(handle, 0, 13, 3, 15)
    blade = im(); poly(blade, [(8, 5), (11, 2), (15, 6), (12, 9)])
    return icon([(shaft, BROWN), (handle, BROWN), (blade, GREY)], [(12, 4, WHITE), (11, 5, WHITE), (13, 7, BROWN), (11, 8, BROWN), (3, 12, YELLOW)])


def icon_blowtorch():
    tank = im(); rect(tank, 1, 6, 6, 13)
    pipe = im(); rect(pipe, 6, 8, 10, 10)
    nozzle = im(); rect(nozzle, 10, 7, 11, 11)
    return icon([(tank, RED), (pipe, GREY), (nozzle, GREY)], [(2, 7, WHITE), (2, 9, WHITE), (4, 11, BLACK), (12, 8, YELLOW), (12, 9, ORANGE), (13, 8, ORANGE), (14, 9, YELLOW), (13, 10, RED)])


def icon_syringe():
    barrel = im(); rect(barrel, 5, 6, 12, 9)
    plunger = im(); rect(plunger, 1, 7, 5, 8)
    thumb = im(); rect(thumb, 0, 5, 1, 10)
    needle = im(); rect(needle, 12, 7, 15, 8)
    return icon([(barrel, WHITE), (plunger, GREY), (thumb, GREY), (needle, GREY)], [(6, 7, GREEN), (7, 7, GREEN), (8, 7, GREEN), (9, 7, GREEN), (10, 7, GREEN), (6, 8, GREEN), (7, 8, GREEN), (8, 8, GREEN), (9, 8, GREEN), (15, 7, WHITE), (8, 5, BLACK), (10, 5, BLACK)])


def icon_tin_bomb():
    can = im(); rect(can, 3, 6, 12, 14)
    lid = im(); rect(lid, 3, 4, 12, 6)
    fuse = im(); line(fuse, [(8, 4), (9, 2), (12, 1)], 0)
    return icon([(can, GREY), (lid, WHITE), (fuse, BROWN)], [(5, 9, RED), (6, 9, RED), (7, 9, RED), (8, 9, RED), (5, 12, BLACK), (9, 12, BLACK), (13, 0, YELLOW), (14, 1, ORANGE), (14, 0, RED), (11, 10, BLACK)])


def icon_extension_cord():
    box = im(); rect(box, 1, 4, 8, 12)
    rod = im(); rect(rod, 8, 7, 13, 9)
    return icon([(box, WHITE), (rod, GREY)], [(2, 7, BLACK), (5, 7, BLACK), (2, 10, BLACK), (5, 10, BLACK), (3, 4, ORANGE), (14, 5, CYAN), (14, 8, CYAN), (15, 10, CYAN), (13, 3, WHITE), (12, 6, CYAN), (6, 12, ORANGE)])


ICONS = {"plunger": icon_plunger, "shiv": icon_shiv, "shovel": icon_shovel, "blowtorch": icon_blowtorch,
         "syringe": icon_syringe, "tin_bomb": icon_tin_bomb, "extension_cord": icon_extension_cord}


# ---------------------------------------------------------------- снаряды
def proj_flame():
    img = new_img(8, 8)
    m = new_mask(8, 8); blob(m, 4, 4, 3, 3, random.Random(41), 0.5, 10)
    inner = new_mask(8, 8); blob(inner, 4, 4, 1.6, 1.6, random.Random(42), 0.3, 8)
    paint(img, m, ORANGE); paint(img, inner, YELLOW)
    px(img, 6, 2, RED); px(img, 1, 5, RED)
    return img


def proj_poison():
    img = new_img(8, 8)
    m = new_mask(8, 8); blob(m, 4, 4, 3, 3, random.Random(43), 0.4, 10)
    paint(img, m, GREEN)
    px(img, 3, 3, WHITE); px(img, 5, 5, BLACK); px(img, 2, 5, BLACK)
    return img


def proj_tin_bomb():
    sheet = new_img(32, 10)
    for f in range(2):
        img = new_img(16, 10)
        can = new_mask(16, 10); rect(can, 3, 2, 11, 8)
        paint(img, can, GREY)
        lid = new_mask(16, 10); rect(lid, 3, 2, 11, 3)
        paint(img, lid, WHITE)
        for x in (5, 6, 7, 8):
            px(img, x, 5, RED)
        px(img, 4, 7, BLACK); px(img, 9, 7, BLACK)
        px(img, 7, 1, BROWN); px(img, 8, 0, BROWN)
        px(img, 9 if f == 0 else 10, 0, YELLOW); px(img, 10 if f == 0 else 9, 1, ORANGE)
        sheet.alpha_composite(img, (f * 16, 0))
    return sheet


PROJECTILES = {"proj_flame": proj_flame, "proj_poison": proj_poison, "proj_tin_bomb": proj_tin_bomb}

if __name__ == "__main__":
    sheet = Image.new("RGBA", (len(HELD) * 20 + 80, 40), (60, 40, 20, 255))
    for i, (name, fn) in enumerate(HELD.items()):
        img = fn()
        img.save("assets/sprites/held_%s.png" % name)
        sheet.alpha_composite(img, (i * 20 + 4, 2))
    for i, (name, fn) in enumerate(ICONS.items()):
        img = fn()
        img.save(UI + "perk_w_" + name + ".png")
        sheet.alpha_composite(img, (i * 20 + 2, 20))
    for i, (name, fn) in enumerate(PROJECTILES.items()):
        img = fn()
        img.save("assets/sprites/%s.png" % name)
        sheet.alpha_composite(img, (len(HELD) * 20 + i * 24 + (0 if i < 2 else 0), 2 if i < 2 else 20))
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save("tools/_preview/weapons3.png")
    print("ok")
