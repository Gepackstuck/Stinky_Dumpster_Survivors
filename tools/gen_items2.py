"""Иконки предметов, пачка 2 (16x16). Запуск из корня проекта: python3 tools/gen_items2.py [preview]"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import (BLACK, BLUE, BROWN, CYAN, GREEN, GREY, PINK, RED, WHITE, YELLOW, UI,
                     blob, line, minus, new_img, poly, px, rect, union, _item, _m)
from PIL import Image


def bottle_cap():
    cap = _m(); blob(cap, 8, 8, 6, 6, random.Random(101), 0.4, 14)
    mid = _m(); blob(mid, 8, 8, 4, 4, random.Random(102), 0.3, 10)
    return _item([(cap, GREY), (mid, RED)], [(6, 7, WHITE), (7, 7, WHITE), (9, 9, YELLOW), (10, 9, YELLOW), (3, 3, GREY), (12, 12, GREY)], (0, WHITE, "dots_off"))


def gum():
    g = _m(); blob(g, 8, 9, 5, 4, random.Random(103), 0.8, 12)
    s = _m(); rect(s, 3, 3, 6, 5)
    return _item([(g, PINK), (s, PINK)], [(7, 8, WHITE), (9, 10, BLACK), (4, 3, BROWN), (5, 4, BROWN), (11, 8, GREY)], (0, WHITE, "dots_off"))


def ushanka():
    hat = _m(); blob(hat, 8, 6, 6, 4, random.Random(104), 0.5, 12)
    fl = _m(); rect(fl, 1, 6, 3, 13); rect(fl, 12, 6, 14, 13)
    band = _m(); rect(band, 3, 8, 12, 10)
    return _item([(hat, BROWN), (fl, BROWN), (band, GREY)], [(7, 3, YELLOW), (8, 3, YELLOW), (2, 12, GREY), (13, 12, GREY), (5, 5, GREY), (10, 6, GREY)], (0, GREY, "dots_off"))


def lighter():
    body = _m(); rect(body, 4, 6, 11, 14)
    top = _m(); rect(top, 4, 3, 11, 6)
    flame = _m(); poly(flame, [(6, 3), (7, 0), (8, 2), (9, 0), (10, 3)])
    return _item([(body, BLUE), (top, GREY), (flame, RED)], [(8, 1, YELLOW), (6, 9, WHITE), (6, 10, WHITE), (9, 12, CYAN), (7, 4, WHITE)])


def plastic_bag():
    bag = _m(); poly(bag, [(3, 5), (12, 5), (14, 14), (2, 14)])
    h1 = _m(); line(h1, [(4, 5), (5, 1), (7, 1), (7, 5)], 1)
    h2 = _m(); line(h2, [(9, 5), (9, 1), (11, 1), (12, 5)], 1)
    return _item([(bag, WHITE), (h1, WHITE), (h2, WHITE)], [(6, 8, RED), (7, 8, RED), (8, 8, RED), (6, 9, RED), (8, 9, RED), (9, 11, GREEN), (4, 12, GREY), (11, 7, GREY), (7, 12, YELLOW)], (0, CYAN, "dots_off"))


def rubber_boot():
    shaft = _m(); rect(shaft, 4, 1, 9, 10)
    foot = _m(); poly(foot, [(4, 8), (9, 8), (14, 11), (14, 14), (3, 14), (3, 11)])
    return _item([(shaft, GREEN), (foot, GREEN)], [(4, 1, BLACK), (9, 1, BLACK), (6, 4, WHITE), (6, 5, WHITE), (10, 12, BROWN), (11, 12, BROWN), (5, 12, BROWN), (4, 13, YELLOW)])


def vodka():
    body = _m(); poly(body, [(5, 6), (10, 6), (11, 14), (4, 14)])
    neck = _m(); rect(neck, 6, 1, 9, 6)
    cap = _m(); rect(cap, 6, 0, 9, 1)
    label = _m(); rect(label, 5, 8, 10, 11)
    return _item([(body, CYAN), (neck, CYAN), (cap, RED), (label, WHITE)], [(6, 9, RED), (8, 9, RED), (7, 10, RED), (5, 7, WHITE), (5, 12, WHITE)])


def hot_dog():
    bun = _m(); blob(bun, 8, 8, 7, 4, random.Random(105), 0.4, 14)
    sau = _m(); rect(sau, 2, 6, 13, 9)
    return _item([(bun, YELLOW), (sau, RED)], [(4, 7, YELLOW), (7, 7, YELLOW), (10, 8, YELLOW), (12, 7, YELLOW), (5, 11, GREEN), (9, 12, GREEN), (3, 5, BROWN), (11, 5, BROWN)])


def binoculars():
    l = _m(); blob(l, 4, 8, 3, 5, random.Random(106), 0.2, 10)
    r = _m(); blob(r, 12, 8, 3, 5, random.Random(107), 0.2, 10)
    br = _m(); rect(br, 5, 6, 10, 9)
    return _item([(l, GREY), (r, GREY), (br, BROWN)], [(4, 11, CYAN), (12, 11, CYAN), (3, 12, WHITE), (11, 12, WHITE), (4, 4, BLACK), (12, 4, BLACK), (8, 7, YELLOW)])


def scarf():
    loop = _m(); rect(loop, 1, 3, 14, 7)
    tail = _m(); rect(tail, 9, 7, 13, 14)
    return _item([(loop, RED), (tail, RED)], [(3, 4, WHITE), (6, 4, WHITE), (9, 4, WHITE), (12, 4, WHITE), (10, 9, WHITE), (12, 11, WHITE), (10, 13, WHITE), (4, 6, BROWN), (7, 6, BROWN)])


def skateboard():
    deck = _m(); rect(deck, 1, 6, 14, 9)
    n1 = _m(); poly(n1, [(1, 6), (0, 4), (2, 5)])
    w1 = _m(); blob(w1, 4, 12, 2, 2, random.Random(108), 0.2, 8)
    w2 = _m(); blob(w2, 11, 12, 2, 2, random.Random(109), 0.2, 8)
    return _item([(deck, YELLOW), (n1, YELLOW), (w1, GREY), (w2, GREY)], [(4, 7, BLACK), (7, 7, RED), (8, 8, RED), (11, 7, BLACK), (4, 12, WHITE), (11, 12, WHITE)])


def dried_fish():
    body = _m(); blob(body, 7, 8, 6, 3, random.Random(110), 0.4, 12)
    tail = _m(); poly(tail, [(12, 8), (15, 4), (15, 12)])
    return _item([(body, YELLOW), (tail, BROWN)], [(3, 7, BLACK), (4, 7, WHITE), (6, 6, BROWN), (7, 9, BROWN), (9, 6, BROWN), (10, 9, BROWN), (5, 10, GREY)])


def helmet():
    dome = _m(); blob(dome, 8, 8, 7, 6, random.Random(111), 0.4, 14)
    brim = _m(); rect(brim, 0, 11, 15, 13)
    ridge = _m(); rect(ridge, 7, 2, 9, 6)
    return _item([(dome, YELLOW), (brim, YELLOW), (ridge, GREY)], [(4, 7, WHITE), (5, 6, WHITE), (11, 9, BROWN), (3, 12, BLACK), (12, 12, BLACK), (8, 9, RED)])


def bandage():
    roll = _m(); blob(roll, 8, 8, 6, 6, random.Random(112), 0.3, 12)
    hole = _m(); blob(hole, 8, 8, 2, 2, random.Random(113), 0.2, 8)
    return _item([(minus(roll, hole), WHITE)], [(5, 5, RED), (6, 6, RED), (10, 7, RED), (5, 11, GREY), (11, 11, GREY), (8, 8, BROWN), (3, 8, GREY), (13, 8, GREY), (12, 4, GREEN)], (0, GREY, "dots_off"))


def crowbar():
    shaft = _m(); line(shaft, [(3, 14), (11, 3)], 2)
    hook = _m(); line(hook, [(11, 3), (14, 2), (14, 5)], 2)
    return _item([(shaft, RED), (hook, RED)], [(4, 12, GREY), (5, 10, GREY), (7, 8, GREY), (9, 5, GREY), (3, 14, BLACK), (13, 3, GREY)])


def gold_tooth():
    t = _m(); blob(t, 8, 6, 5, 4, random.Random(114), 0.4, 12)
    r1 = _m(); poly(r1, [(4, 8), (7, 8), (6, 15), (4, 15)])
    r2 = _m(); poly(r2, [(9, 8), (12, 8), (12, 15), (10, 15)])
    return _item([(t, YELLOW), (r1, YELLOW), (r2, YELLOW)], [(5, 4, WHITE), (6, 4, WHITE), (11, 6, BROWN), (5, 11, BROWN), (11, 11, BROWN), (8, 7, BROWN)])


def battery():
    body = _m(); rect(body, 4, 3, 11, 14)
    cap = _m(); rect(cap, 6, 1, 9, 3)
    stripe = _m(); rect(stripe, 4, 6, 11, 9)
    return _item([(body, GREEN), (cap, GREY), (stripe, YELLOW)], [(7, 7, BLACK), (8, 7, BLACK), (7, 8, BLACK), (8, 12, WHITE), (5, 12, WHITE), (10, 4, WHITE)])


def crown():
    band = _m(); rect(band, 1, 9, 14, 13)
    spikes = _m(); poly(spikes, [(1, 9), (1, 3), (4, 7), (7, 2), (8, 2), (11, 7), (14, 3), (14, 9)])
    return _item([(band, GREY), (spikes, GREY)], [(1, 2, YELLOW), (14, 2, YELLOW), (7, 1, RED), (8, 1, RED), (4, 11, RED), (8, 11, GREEN), (12, 11, CYAN), (3, 7, BROWN), (12, 7, BROWN), (6, 5, BROWN)], (0, YELLOW, "dots_off"))


def junk_backpack():
    body = _m(); blob(body, 8, 9, 6, 6, random.Random(115), 0.7, 14)
    pocket = _m(); rect(pocket, 4, 10, 11, 14)
    flap = _m(); rect(flap, 4, 4, 11, 6)
    return _item([(body, BROWN), (pocket, GREEN), (flap, GREY)], [(7, 0, GREY), (9, 1, BROWN), (11, 2, PINK), (5, 8, YELLOW), (9, 8, YELLOW), (7, 12, BLACK), (8, 12, BLACK)], (0, YELLOW, "dots_off"))


def bone_club():
    shaft = _m(); line(shaft, [(3, 13), (11, 4)], 3)
    k1 = _m(); blob(k1, 12, 3, 3, 3, random.Random(116), 0.3, 8)
    k2 = _m(); blob(k2, 2, 14, 2, 2, random.Random(117), 0.3, 8)
    return _item([(shaft, WHITE), (k1, WHITE), (k2, WHITE)], [(11, 5, GREY), (9, 7, GREY), (7, 9, GREY), (5, 11, GREY), (13, 2, BLACK), (12, 1, RED), (14, 4, RED)])


ITEMS2 = [
    ("bottle_cap", bottle_cap), ("gum", gum), ("ushanka", ushanka), ("lighter", lighter), ("plastic_bag", plastic_bag),
    ("rubber_boot", rubber_boot), ("vodka", vodka), ("hot_dog", hot_dog), ("binoculars", binoculars), ("scarf", scarf),
    ("skateboard", skateboard), ("dried_fish", dried_fish), ("helmet", helmet), ("bandage", bandage), ("crowbar", crowbar),
    ("gold_tooth", gold_tooth), ("battery", battery), ("crown", crown), ("junk_backpack", junk_backpack), ("bone_club", bone_club),
]

if __name__ == "__main__":
    sheet = Image.new("RGBA", (5 * 20, 4 * 20), (60, 40, 20, 255))
    for i, (name, fn) in enumerate(ITEMS2):
        img = fn()
        img.save(UI + "item_" + name + ".png")
        sheet.alpha_composite(img, ((i % 5) * 20 + 2, (i // 5) * 20 + 2))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save("tools/_preview/items2.png")
    print("ok", len(ITEMS2))
