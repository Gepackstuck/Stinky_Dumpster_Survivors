"""Иконки оружия пачки 2 (16x16) -> assets/ui/perk_w_<id>.png. Запуск из корня: python3 tools/gen_weapons2.py"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, BLUE, BROWN, CYAN, GREEN, GREY, PINK, RED, UI, WHITE, YELLOW, blob, finish, line, new_img, new_mask, paint, poly, px, rect, union
from PIL import Image

W = 16


def _m():
    return new_mask(W, W)


def _icon(layers, dots=()):
    sil = union(*[m for m, _ in layers])
    img = new_img(W, W)
    for m, c in layers:
        paint(img, m, c)
    out = finish(img, sil)
    for x, y, c in dots:
        px(out, x, y, c)
    return out


def pipe_gun():
    tube = _m(); rect(tube, 5, 5, 14, 8)
    stock = _m(); poly(stock, [(0, 7), (5, 7), (5, 12), (2, 12)])
    tape = _m(); rect(tape, 8, 5, 9, 8)
    return _icon([(tube, GREY), (stock, BROWN), (tape, YELLOW)], [(14, 6, BLACK), (6, 10, BROWN), (11, 6, WHITE), (15, 3, YELLOW), (13, 2, YELLOW)])


def crossbow():
    stock = _m(); rect(stock, 1, 7, 12, 9)
    bow = _m(); line(bow, [(10, 1), (13, 7), (13, 9), (10, 14)], 1)
    string = _m(); line(string, [(10, 1), (7, 8), (10, 14)], 0)
    return _icon([(stock, BROWN), (bow, GREY), (string, WHITE)], [(14, 8, RED), (15, 8, WHITE), (3, 8, BLACK), (5, 9, BLACK)])


def frying_pan():
    pan = _m(); blob(pan, 10, 6, 5, 5, random.Random(31), 0.2, 12)
    handle = _m(); line(handle, [(1, 14), (7, 9)], 2)
    return _icon([(pan, BLACK), (handle, BROWN)], [(9, 4, GREY), (10, 4, GREY), (11, 8, YELLOW), (12, 7, WHITE), (13, 5, GREY), (3, 12, WHITE)])


def rolling_pin():
    body = _m(); line(body, [(4, 12), (11, 5)], 3)
    h1 = _m(); line(h1, [(1, 15), (4, 12)], 1)
    h2 = _m(); line(h2, [(11, 5), (14, 2)], 1)
    return _icon([(body, YELLOW), (h1, BROWN), (h2, BROWN)], [(6, 9, WHITE), (7, 8, WHITE), (9, 7, BROWN), (8, 10, BROWN), (13, 8, GREY)])


def cheese():
    wedge = _m(); poly(wedge, [(1, 11), (14, 4), (14, 12), (1, 12)])
    return _icon([(wedge, YELLOW)], [(5, 10, BROWN), (9, 8, BROWN), (8, 10, BROWN), (12, 8, BROWN), (11, 11, BROWN), (4, 3, GREEN), (7, 1, GREEN), (10, 2, GREEN), (13, 1, GREEN), (2, 6, GREEN)])


def spray_can():
    can = _m(); rect(can, 4, 4, 10, 14)
    cap = _m(); rect(cap, 5, 1, 9, 4)
    nozzle = _m(); rect(nozzle, 9, 1, 11, 2)
    return _icon([(can, RED), (cap, GREY), (nozzle, GREY)], [(5, 7, WHITE), (5, 9, WHITE), (8, 8, YELLOW), (8, 11, BLACK), (13, 1, YELLOW), (14, 0, RED), (14, 3, YELLOW), (15, 2, RED)])


def bottle():
    body = _m(); poly(body, [(5, 7), (10, 7), (11, 14), (4, 14)])
    neck = _m(); rect(neck, 6, 1, 9, 7)
    cap = _m(); rect(cap, 6, 0, 9, 1)
    return _icon([(body, GREEN), (neck, GREEN), (cap, YELLOW)], [(6, 9, WHITE), (6, 10, WHITE), (8, 11, WHITE), (7, 4, WHITE), (5, 13, BLACK), (9, 13, BLACK)])


def mosin():
    barrel = _m(); line(barrel, [(5, 6), (15, 2)], 1)
    stock = _m(); poly(stock, [(0, 11), (6, 6), (9, 8), (4, 14), (0, 13)])
    return _icon([(barrel, GREY), (stock, BROWN)], [(15, 2, BLACK), (9, 4, GREY), (3, 11, YELLOW), (6, 9, BLACK), (11, 3, BLACK), (1, 12, BLACK)])


ICONS = {"pipe_gun": pipe_gun, "crossbow": crossbow, "frying_pan": frying_pan, "rolling_pin": rolling_pin,
         "rotten_cheese": cheese, "spray_can": spray_can, "bottle": bottle, "mosin": mosin}

if __name__ == "__main__":
    sheet = Image.new("RGBA", (len(ICONS) * 20, 20), (60, 40, 20, 255))
    for i, (name, fn) in enumerate(ICONS.items()):
        img = fn()
        img.save(UI + "perk_w_" + name + ".png")
        sheet.alpha_composite(img, (i * 20 + 2, 2))
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save("tools/_preview/weapons2.png")
    print("ok")
