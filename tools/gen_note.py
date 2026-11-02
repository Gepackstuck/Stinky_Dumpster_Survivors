#!/usr/bin/env python3
"""Н17: записка от бомжа - мятый тетрадный листок в клетку с пятном и булавкой, 120x56.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_note.py -> assets/ui/quest_note.png"""
import numpy as np
from PIL import Image
from pix import *

R = np.random.default_rng(17)
PAPER = (235, 228, 200); LINE = (170, 190, 220); STAIN = (160, 120, 60)
c = Canvas(120, 56)
for y in range(2, 54):
    off = int(2 * np.sin(y / 7.0))                                  # мятый край
    c.a[y, 3 + off:117 - off] = (*PAPER, 255)
for x in range(6, 116, 6): c.a[3:53, x][c.a[3:53, x, 3] > 0] = (*LINE, 255)
for y in range(6, 54, 6): c.a[y, 4:116][c.a[y, 4:116, 3] > 0] = (*LINE, 255)
c.ell(98, 42, 9, 6, STAIN, dither=PAPER)                             # жирное пятно
c.ell(60, 4, 3, 3, RED); c.px(60, 4, WHITE)                          # булавка
for _ in range(12): c.px(int(R.integers(6, 114)), int(R.integers(6, 50)), (200, 190, 160))
Image.fromarray(c.a).save("assets/ui/quest_note.png")   # без авто-тени: на листке пишем текст
