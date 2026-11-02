#!/usr/bin/env python3
"""Книга-коллекция на кладбище: курсор-рамка 24x24 (кривая кислотная, с каплей слизи).
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_book.py -> assets/ui/book_cursor.png"""
from PIL import Image
from pix import *

c = Canvas(24, 24)
for (x0, y0, x1, y1) in ((1, 1, 22, 1), (1, 22, 22, 22), (1, 1, 1, 22), (22, 1, 22, 22)):
    c.line(x0, y0, x1, y1, YELLOW)
for (x, y) in ((0, 0), (23, 0), (0, 23), (23, 23)):          # уголки ярче
    c.rect(max(x - 1, 0), max(y - 1, 0), min(x + 1, 23), min(y + 1, 23), PINK)
c.pts([(1, 2), (2, 1), (22, 21), (21, 22), (12, 1), (1, 12)], GREEN)
c.pts([(16, 23), (16, 22)], GREEN)                           # капля слизи
Image.fromarray(c.finish(PINK, WHITE, outline=False)).save("assets/ui/book_cursor.png")
