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


def pipe_gun():
    tube = _m(); rect(tube, 3, 4, 10, 6)
    stock = _m(); rect(stock, 0, 5, 3, 8)
    tape = _m(); rect(tape, 5, 4, 6, 6)
    return _held([(tube, GREY), (stock, BROWN), (tape, YELLOW)], [(11, 5, BLACK), (4, 7, BROWN), (8, 5, WHITE)])


def crossbow():
    stock = _m(); rect(stock, 0, 5, 9, 7)
    bow = _m(); line(bow, [(7, 0), (9, 5), (9, 7), (7, 11)], 1)
    string = _m(); line(string, [(7, 0), (5, 6), (7, 11)], 0)
    return _held([(stock, BROWN), (bow, GREY), (string, WHITE)], [(10, 6, RED), (11, 6, WHITE), (2, 6, BLACK)])


def frying_pan():
    pan = _m(); blob(pan, 8, 6, 3, 4, random.Random(21), 0.2, 10)
    handle = _m(); rect(handle, 0, 5, 5, 7)
    return _held([(pan, BLACK), (handle, BROWN)], [(8, 4, GREY), (9, 5, GREY), (7, 7, YELLOW), (8, 6, WHITE)])


def rolling_pin():
    body = _m(); rect(body, 2, 4, 9, 8)
    h1 = _m(); rect(h1, 0, 5, 2, 7)
    h2 = _m(); rect(h2, 9, 5, 11, 7)
    return _held([(body, YELLOW), (h1, BROWN), (h2, BROWN)], [(4, 5, WHITE), (6, 7, BROWN), (8, 5, BROWN)])


def cheese():
    wedge = _m(); poly(wedge, [(1, 8), (10, 4), (10, 9), (1, 9)])
    return _held([(wedge, YELLOW)], [(4, 7, BROWN), (7, 6, BROWN), (6, 8, BROWN), (9, 2, GREEN), (7, 1, GREEN), (11, 3, GREEN), (2, 5, GREEN)])


def spray_can():
    can = _m(); rect(can, 1, 3, 8, 8)
    nozzle = _m(); rect(nozzle, 8, 5, 10, 6)
    cap = _m(); rect(cap, 7, 3, 8, 8)
    return _held([(can, RED), (nozzle, GREY), (cap, GREY)], [(3, 4, WHITE), (3, 6, WHITE), (5, 5, YELLOW), (11, 5, YELLOW), (11, 6, RED)])


def bottle():
    body = _m(); rect(body, 1, 4, 7, 8)
    neck = _m(); rect(neck, 7, 5, 11, 7)
    return _held([(body, GREEN), (neck, GREEN)], [(3, 5, WHITE), (4, 5, WHITE), (11, 6, BROWN), (5, 7, WHITE), (2, 6, YELLOW)])


def mosin():
    barrel = _m(); rect(barrel, 4, 5, 11, 6)
    stock = _m(); poly(stock, [(0, 4), (5, 5), (5, 8), (0, 8)])
    return _held([(barrel, GREY), (stock, BROWN)], [(11, 5, BLACK), (7, 4, GREY), (2, 6, YELLOW), (8, 6, BLACK)])


HELD = {"lighter": lighter, "sock": sock, "slingshot": slingshot, "mop": mop, "laser_pointer": laser, "slipper": slipper, "condensed_milk": milk,
        "pipe_gun": pipe_gun, "crossbow": crossbow, "frying_pan": frying_pan, "rolling_pin": rolling_pin,
        "rotten_cheese": cheese, "spray_can": spray_can, "bottle": bottle, "mosin": mosin}

if __name__ == "__main__":
    sheet = Image.new("RGBA", (8 * 16, ((len(HELD) + 7) // 8) * 16), (60, 40, 20, 255))
    for i, (name, fn) in enumerate(HELD.items()):
        img = fn()
        img.save("assets/sprites/held_%s.png" % name)
        sheet.alpha_composite(img, ((i % 8) * 16 + 2, (i // 8) * 16 + 2))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save("tools/_preview/held.png")
    print("ok")
