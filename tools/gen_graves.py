"""Могилы кладбища: закрытая (надгробие на холмике, 48x52) и раскопанная (яма с кучей земли, 48x40). Запуск из корня: python3 tools/gen_graves.py"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, BROWN, GREEN, GREY, UI, WHITE, YELLOW, RED, blob, dither, finish, line, new_img, new_mask, paint, poly, px, rect, union
from PIL import Image


def closed():
    w, h = 48, 52
    mound = new_mask(w, h); blob(mound, 24, 46, 22, 6, random.Random(7), 0.8, 14)
    stone = new_mask(w, h); poly(stone, [(12, 46), (12, 16), (15, 10), (20, 7), (28, 7), (33, 10), (36, 16), (36, 46)])
    sil = union(mound, stone)
    img = new_img(w, h)
    paint(img, mound, BROWN); dither(img, mound, YELLOW, "dots_off")
    paint(img, stone, GREY); dither(img, stone, WHITE, "dots_off")
    out = finish(img, sil)
    for y in range(13, 26): px(out, 24, y, BLACK)          # крест на плите
    for x in range(20, 29): px(out, x, 17, BLACK)
    for x, y in ((16, 30), (17, 31), (17, 32), (18, 33), (30, 35), (31, 36), (14, 40), (15, 40), (33, 28)): px(out, x, y, GREEN)   # мох
    for x, y in ((20, 31), (21, 32), (22, 31), (26, 33), (27, 34), (28, 34)): px(out, x, y, BLACK)   # трещины
    for x in (8, 11, 38, 41, 5, 43):
        px(out, x, 44, GREEN); px(out, x, 43, GREEN)
    return out


def opened():
    w, h = 48, 40
    rim = new_mask(w, h); blob(rim, 24, 24, 22, 9, random.Random(11), 0.6, 16)
    pit = new_mask(w, h); blob(pit, 24, 25, 17, 6, random.Random(12), 0.5, 14)
    pile = new_mask(w, h); blob(pile, 8, 28, 7, 5, random.Random(13), 0.8, 10)
    cross = new_mask(w, h); line(cross, [(41, 8), (41, 24)], 2); line(cross, [(36, 12), (46, 12)], 2)
    sil = union(rim, pile, cross)
    img = new_img(w, h)
    paint(img, rim, BROWN); dither(img, rim, YELLOW, "dots_off")
    paint(img, pile, BROWN); dither(img, pile, YELLOW, "checker")
    paint(img, cross, BROWN)
    paint(img, pit, BLACK)
    out = finish(img, sil)
    for x, y in ((14, 24), (18, 27), (30, 28), (34, 24), (22, 29)): px(out, x, y, GREY)   # камешки на дне
    for x in (4, 7, 44, 46):
        px(out, x, 34, GREEN); px(out, x, 33, GREEN)
    return out


if __name__ == "__main__":
    c, o = closed(), opened()
    c.save(UI + "grave_closed.png"); o.save(UI + "grave_open.png")
    sheet = Image.new("RGBA", (110, 60), (30, 40, 25, 255))
    sheet.alpha_composite(c, (2, 4)); sheet.alpha_composite(o, (58, 12))
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save("tools/_preview/graves.png")
    print("ok")
