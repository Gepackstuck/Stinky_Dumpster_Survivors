#!/usr/bin/env python3
"""Шапки-трофеи (идея 12): за победу на уровне опасности 0..5 - шапка из того же хлама, что и медали.
0 газетная пилотка, 1 кепка из пивных крышек, 2 шлем из мятой банки, 3 медный кран-рог, 4 серебряный дуршлаг, 5 корона-унитаз.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_trophy_hats.py -> assets/sprites/trophy_hat_<n>.png (16x12)"""
from PIL import Image
from pix import *

PAPER = (225, 220, 200); COPPER = (200, 110, 50); SILVER = (205, 210, 220); GOLD = (255, 200, 40); RUSTY = (170, 90, 40)


def hat(n):
    c = Canvas(16, 12)
    if n == 0:   # пилотка из газеты
        c.rect(2, 8, 13, 10, PAPER); c.line(2, 8, 7, 2, PAPER, 2); c.line(13, 8, 8, 2, PAPER, 2)
        c.pts([(4, 9), (6, 9), (9, 9), (11, 9), (6, 6), (9, 5)], DGREY)
    elif n == 1:  # кепка из пивных крышек
        c.ell(7, 8, 6, 4, RUSTY); c.rect(10, 9, 15, 10, RUSTY)
        for x in (4, 7, 10): c.ell(x, 7, 1, 1, YELLOW)
        c.pts([(5, 9), (9, 9)], DGREY)
    elif n == 2:  # шлем из мятой банки
        c.rect(3, 4, 12, 10, RED); c.rect(3, 4, 12, 5, GREY); c.pts([(5, 7), (6, 8), (10, 6)], WHITE); c.line(8, 6, 9, 9, (150, 0, 30))
    elif n == 3:  # медный кран-рог
        c.rect(3, 7, 12, 10, COPPER); c.rect(6, 3, 9, 7, COPPER); c.rect(9, 3, 13, 4, COPPER); c.px(13, 5, CYAN); c.px(13, 6, CYAN)
        c.rect(5, 1, 10, 2, COPPER); c.pts([(4, 8), (7, 4)], YELLOW)
    elif n == 4:  # серебряный дуршлаг
        c.ell(7, 8, 6, 4, SILVER, dither=WHITE)
        for (x, y) in ((4, 7), (7, 6), (10, 7), (6, 9), (9, 9)): c.px(x, y, DGREY)
        c.rect(0, 9, 1, 10, SILVER); c.rect(14, 9, 15, 10, SILVER)
    else:        # корона-унитаз
        c.rect(3, 6, 12, 10, GOLD, dither=YELLOW); c.ell(7, 6, 5, 2, WHITE); c.ell(7, 6, 3, 1, CYAN)
        for x in (3, 7, 11): c.pts([(x, 3), (x + 1, 2), (x + 1, 4)], GOLD)
        c.pts([(5, 9), (10, 8)], WHITE)
    return c.finish(BLACK if n < 5 else BROWN, WHITE)


for n in range(6):
    Image.fromarray(hat(n)).save(f"assets/sprites/trophy_hat_{n}.png")
p = Image.new("RGBA", (6 * 20, 16), (40, 30, 30, 255))
for n in range(6):
    im = Image.open(f"assets/sprites/trophy_hat_{n}.png"); p.paste(im, (n * 20 + 2, 2), im)
p.resize((960, 128), Image.NEAREST).save("tools/_preview/trophy_hats.png")
