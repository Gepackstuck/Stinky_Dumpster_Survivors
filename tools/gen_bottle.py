#!/usr/bin/env python3
"""Н7: бутылка-граната на полу (тлеющий фитиль-тряпка), 2 кадра 12x8, носиком вправо.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_bottle.py -> assets/sprites/bottle_grenade.png"""
from PIL import Image
from pix import *

GLASS = (60, 170, 60); RAG = (230, 210, 170)


def bottle(t):
    c = Canvas(14, 9)
    c.ell(5, 4, 4, 3, GLASS, dither=(40, 120, 40)); c.rect(8, 3, 10, 5, GLASS)   # пузо и горлышко
    c.pts([(3, 3), (4, 2)], WHITE)                                               # блик
    c.rect(4, 4, 6, 5, YELLOW); c.px(5, 4, RED)                                  # этикетка «ВОДКА»
    c.rect(11, 3, 12, 5, RAG); c.px(13, 2 if t else 3, ORANGE)                   # тряпка-фитиль тлеет
    if t: c.px(13, 1, YELLOW)
    return c.finish(BLACK, WHITE)


sheet([bottle(t) for t in range(2)]).save("assets/sprites/bottle_grenade.png")
im = Image.open("assets/sprites/bottle_grenade.png"); im.resize((im.width * 10, im.height * 10), Image.NEAREST).save("tools/_preview/bottle.png")
