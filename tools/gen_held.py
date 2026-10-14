"""Оружие в руках героя (12x12, смотрит ВПРАВО, в игре поворачивается на цель). Запуск из корня: python3 tools/gen_held.py"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, BLUE, BROWN, CYAN, GREEN, GREY, PINK, RED, WHITE, YELLOW, blob, finish, line, new_img, new_mask, paint, poly, px, rect, union
from PIL import Image

S = 12


def _m():
    return new_mask(S, S)


def _held(layers, dots=()):
    sil = union(*[m for m, _ in layers])
    img = new_img(S, S)
    for m, c in layers:
        paint(img, m, c)
    out = finish(img, sil)
    for x, y, c in dots:
        px(out, x, y, c)
    return out


def lighter():
    body = _m(); rect(body, 1, 4, 7, 8)
    head = _m(); rect(head, 7, 4, 9, 8)
    flame = _m(); poly(flame, [(9, 5), (11, 6), (9, 7)])
    return _held([(body, YELLOW), (head, GREY), (flame, RED)], [(3, 6, BLACK), (4, 6, BLACK), (10, 6, YELLOW)])


def sock():
    tube = _m(); rect(tube, 1, 4, 8, 7)
    toe = _m(); blob(toe, 9, 6, 2, 2, random.Random(5), 0.2, 8)
    heel = _m(); rect(heel, 1, 7, 3, 9)
    return _held([(tube, WHITE), (toe, GREY), (heel, GREY)], [(3, 5, GREEN), (6, 6, GREEN), (5, 3, GREEN), (9, 2, GREEN), (10, 4, GREEN), (2, 0, GREEN)])


def slingshot():
    handle = _m(); line(handle, [(0, 6), (5, 6)], 2)
    fork = _m(); line(fork, [(5, 6), (10, 2)], 1); line(fork, [(5, 6), (10, 10)], 1)
    band = _m(); line(band, [(10, 2), (8, 6), (10, 10)], 1)
    return _held([(handle, BROWN), (fork, BROWN), (band, PINK)], [(8, 6, YELLOW)])


def mop():
    stick = _m(); line(stick, [(0, 6), (7, 6)], 1)
    head = _m(); rect(head, 7, 3, 10, 9)
    return _held([(stick, BROWN), (head, GREY)], [(8, 4, WHITE), (9, 5, WHITE), (8, 7, WHITE), (9, 8, WHITE), (10, 6, BLACK)])


def laser():
    pen = _m(); rect(pen, 1, 5, 8, 7)
    tip = _m(); rect(tip, 8, 5, 9, 7)
    return _held([(pen, PINK), (tip, GREY)], [(3, 6, WHITE), (10, 6, RED), (11, 6, RED), (11, 5, PINK), (11, 7, PINK)])


def slipper():
    sole = _m(); blob(sole, 6, 6, 5, 3, random.Random(9), 0.3, 12)
    strap = _m(); rect(strap, 5, 3, 8, 6)
    return _held([(sole, BROWN), (strap, PINK)], [(3, 6, YELLOW), (4, 6, YELLOW), (6, 4, WHITE)])


def milk():
    can = _m(); rect(can, 1, 3, 8, 8)
    nozzle = _m(); rect(nozzle, 8, 5, 11, 6)
    return _held([(can, BLUE), (nozzle, GREY)], [(3, 4, WHITE), (4, 4, WHITE), (3, 6, WHITE), (4, 6, WHITE), (6, 5, CYAN), (5, 7, CYAN)])


HELD = {"lighter": lighter, "sock": sock, "slingshot": slingshot, "mop": mop, "laser_pointer": laser, "slipper": slipper, "condensed_milk": milk}

if __name__ == "__main__":
    sheet = Image.new("RGBA", (len(HELD) * 16, 16), (60, 40, 20, 255))
    for i, (name, fn) in enumerate(HELD.items()):
        img = fn()
        img.save("assets/sprites/held_%s.png" % name)
        sheet.alpha_composite(img, (i * 16 + 2, 2))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save("tools/_preview/held.png")
    print("ok")
