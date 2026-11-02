#!/usr/bin/env python3
"""Живое кладбище (идея 11): грибы на могилах (3 вида), памятник из говна самому дохлому герою.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_grave_life.py -> assets/ui/grave_mushroom.png (3 кадра 8x8), grave_monument.png (2 кадра 18x24)"""
from PIL import Image
from pix import *

PALE = (230, 220, 190); TOXIC = (150, 255, 40); MUD = (110, 70, 30); GOLD = (255, 200, 40)


def mushroom(k):
    c = Canvas(8, 8)
    if k == 0:   # поганка: красная шляпка в белую точку
        c.rect(3, 4, 4, 7, PALE); c.ell(3, 3, 3, 2, RED); c.pts([(2, 2), (4, 3)], WHITE)
    elif k == 1:  # кислотный светящийся гриб
        c.rect(3, 4, 4, 7, PALE); c.ell(3, 3, 3, 2, TOXIC, dither=GREEN); c.px(5, 1, YELLOW)
    else:        # кучка опят
        c.rect(1, 4, 1, 7, PALE); c.rect(5, 3, 5, 7, PALE); c.ell(1, 3, 1, 1, ORANGE); c.ell(5, 2, 2, 1, ORANGE); c.px(3, 6, PALE); c.px(3, 5, ORANGE)
    return c.finish(BROWN, WHITE)


def monument(t):
    c = Canvas(18, 24)
    c.rect(1, 19, 16, 23, GREY, dither=DGREY)                         # постамент
    c.rect(3, 20, 14, 21, GOLD); c.pts([(5, 20), (8, 21), (11, 20)], BROWN)   # табличка
    c.ell(9, 16, 7, 3, BROWN, dither=MUD)                             # куча ярусами
    c.ell(9, 12, 5, 3, BROWN, dither=MUD)
    c.ell(9, 8, 3, 2, BROWN, dither=MUD)
    c.pts([(9, 5), (10, 4)], BROWN)
    c.eye(7, 12, 1, (1, 0), blood=False); c.eye(11, 12, 1, (0, 0), blood=False)
    c.line(7, 15, 11, 15, BLACK)
    for k, x in enumerate((5, 9, 13)):                                 # вонь
        y = 3 - (t + k) % 2
        c.pts([(x, y), (x + 1, y - 1)], GREEN)
    c.pts([(4, 9), (14, 11)], GOLD if t else YELLOW)                   # блестит «бронза»
    return c.finish(BROWN, YELLOW)


sheet([mushroom(k) for k in range(3)]).save("assets/ui/grave_mushroom.png")
sheet([monument(t) for t in range(2)]).save("assets/ui/grave_monument.png")
a = Image.open("assets/ui/grave_mushroom.png"); b = Image.open("assets/ui/grave_monument.png")
p = Image.new("RGBA", (70, 26), (40, 30, 30, 255)); p.paste(a, (2, 16), a); p.paste(b, (30, 1), b)
p.resize((560, 208), Image.NEAREST).save("tools/_preview/grave_life.png")
