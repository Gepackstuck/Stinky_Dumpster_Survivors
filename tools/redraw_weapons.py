#!/usr/bin/env python3
"""Оружие в руках 12×12 (смотрит вправо, дуло у правого края): контур, кислотная контр-тень, блики, детали."""
import sys, os
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
LGREY = (200, 200, 210)


def fin(c, shade, hi=WHITE):
    a = c.finish(shade, hi, lim=-0.25)
    return a


def lighter():
    c = Canvas(10, 10)
    c.rect(0, 3, 5, 8, RED, dither=(150, 0, 30)); c.rect(1, 4, 1, 7, WHITE)          # корпус и блик
    c.rect(5, 2, 7, 5, GREY); c.rect(5, 6, 7, 8, GREY); c.px(6, 2, WHITE); c.px(3, 2, DGREY); c.px(4, 2, DGREY)   # колёсико, крышка
    c.pts([(8, 4), (9, 3), (9, 4), (9, 5)], ORANGE); c.pts([(8, 3), (8, 5)], YELLOW); c.px(9, 4, RED); c.px(9, 2, YELLOW)  # язычок пламени
    return fin(c, PURPLE, YELLOW)


def slingshot():
    c = Canvas(10, 10)
    c.rect(0, 4, 4, 5, BROWN); c.line(4, 5, 6, 2, BROWN, 2); c.line(4, 5, 6, 8, BROWN, 2)        # рукоять-вилка
    c.px(0, 4, (150, 90, 40)); c.px(1, 4, (150, 90, 40))
    c.line(6, 2, 8, 5, PINK); c.line(6, 8, 8, 5, PINK)                                              # жгут
    c.ell(8, 5, 1, 1, GREY); c.px(8, 4, WHITE)                                                       # камень
    c.pts([(7, 1), (7, 9)], YELLOW)
    return fin(c, PURPLE, YELLOW)


def mop():
    c = Canvas(10, 10)
    c.line(0, 5, 6, 5, BROWN, 2); c.px(1, 4, (150, 90, 40)); c.px(2, 4, (150, 90, 40))
    c.rect(6, 2, 7, 8, GREY, dither=WHITE)                                                          # зажим
    for y in range(1, 10): c.px(8 + (y % 2), y, WHITE if y % 3 else PINK)                           # мокрые пряди
    c.pts([(9, 2), (9, 5), (9, 8)], CYAN); c.pts([(8, 9)], GREEN)                                    # капли
    return fin(c, CYAN, WHITE)


def spray_can():
    c = Canvas(10, 10)
    c.rect(0, 2, 5, 8, PINK, dither=(200, 0, 190)); c.rect(1, 3, 1, 7, WHITE); c.rect(2, 4, 4, 6, YELLOW); c.px(3, 5, BLACK)   # баллон с этикеткой
    c.rect(5, 3, 6, 7, GREY); c.rect(6, 4, 7, 6, DGREY); c.px(7, 5, RED)                           # колпачок и кнопка
    c.pts([(8, 3), (9, 2), (8, 7), (9, 8), (9, 5), (8, 5)], GREEN)                                  # облако краски
    return fin(c, CYAN, WHITE)


def bottle():
    c = Canvas(10, 10)
    c.ell(3, 5, 3, 3, GREEN, dither=(20, 180, 20)); c.rect(0, 3, 4, 7, GREEN, dither=(20, 180, 20))
    c.rect(5, 4, 8, 6, GREEN); c.rect(8, 4, 9, 6, GREY)                                             # горлышко и пробка
    c.rect(1, 4, 3, 6, WHITE); c.px(2, 5, RED)                                                       # этикетка
    c.px(0, 3, WHITE); c.px(0, 4, WHITE); c.pts([(5, 4)], WHITE)
    c.pts([(7, 7), (8, 8)], YELLOW)                                                                  # капля
    return fin(c, PURPLE, YELLOW)


def mosin():
    c = Canvas(10, 10)
    c.rect(0, 4, 3, 7, BROWN, dither=(150, 90, 40)); c.rect(3, 5, 8, 6, DGREY); c.rect(8, 5, 9, 5, GREY)    # приклад, ствол
    c.rect(3, 4, 6, 4, GREY); c.px(4, 3, WHITE)                                                      # затвор
    c.line(2, 4, 2, 2, BLACK); c.px(9, 4, WHITE)                                                     # мушка / штык
    c.pts([(5, 7), (6, 7)], BROWN); c.px(1, 5, YELLOW)
    return fin(c, GREEN, WHITE)


SAMPLE = {"lighter": lighter, "slingshot": slingshot, "mop": mop, "spray_can": spray_can, "bottle": bottle, "mosin": mosin}

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(SAMPLE)
    k = 12
    prev = Image.new("RGBA", (len(names) * 14 * k + 10, 2 * 14 * k + 10), (45, 30, 20, 255))
    os.makedirs("tools/_preview/weapons_new", exist_ok=True)
    for i, n in enumerate(names):
        a = SAMPLE[n](); im = Image.fromarray(a, "RGBA")
        canvas = Image.new("RGBA", (12, 12), (0, 0, 0, 0)); canvas.paste(im, ((12 - im.width) // 2, (12 - im.height) // 2))
        canvas.save(f"tools/_preview/weapons_new/held_{n}.png")
        if apply: canvas.save(f"assets/sprites/held_{n}.png")
        old = Image.open(f"tools/_orig_art/held_{n}.png" if os.path.exists(f"tools/_orig_art/held_{n}.png") else f"assets/sprites/held_{n}.png").convert("RGBA")
        for r, src in enumerate((old, canvas)):
            big = src.resize((12 * k, 12 * k), Image.NEAREST); prev.paste(big, (5 + i * 14 * k, 5 + r * 14 * k), big)
    prev.save("tools/_preview/weapons_sample.png")
