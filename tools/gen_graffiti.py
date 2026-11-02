#!/usr/bin/env python3
"""Н30: мазок баллончиком под надпись-граффити (белый, красится modulate), с подтёками. 3 варианта 72x14.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_graffiti.py -> assets/sprites/graffiti_splat.png"""
import numpy as np
from PIL import Image
from pix import *

R = np.random.default_rng(30)


def splat(k):
    c = Canvas(72, 14)
    for x in range(2, 70):
        h = 3 + int(2 * np.sin(x / (5.0 + k)) + R.integers(0, 2))
        for y in range(5 - h // 2, 5 + h // 2 + 1):
            if R.random() < 0.85: c.px(x, y, WHITE)
        if R.random() < 0.12:                                   # подтёки краски
            for y in range(5 + h // 2, min(13, 5 + h // 2 + int(R.integers(2, 7)))): c.px(x, y, WHITE)
    for _ in range(40):                                          # брызги
        c.px(int(R.integers(0, 72)), int(R.integers(0, 14)), WHITE)
    return c.a


sheet([splat(k) for k in range(3)]).save("assets/sprites/graffiti_splat.png")
