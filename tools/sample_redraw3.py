#!/usr/bin/env python3
"""Пример v3: B + бешенство. Глитч-двойник (розовый/голубой сдвиг), рваный контур, линии ярости, налитые глаза, пена."""
import random
import numpy as np
from PIL import Image
import importlib.util, sys

spec = importlib.util.spec_from_file_location("s2", "tools/sample_redraw2.py")
s2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s2)
W = H = 26
PAD = 3
BLACK, WHITE, GREEN, PINK, YELLOW, RED, BLUE, CYAN = s2.BLACK, s2.WHITE, s2.GREEN, s2.PINK, s2.YELLOW, s2.RED, s2.BLUE, s2.CYAN


def pad(a):
    out = np.zeros((H + 2 * PAD, W + 2 * PAD, 4), np.uint8)
    out[PAD:PAD + H, PAD:PAD + W] = a
    return out


def px(a, pts, c):
    for x, y in pts:
        x += PAD; y += PAD
        if 0 <= x < a.shape[1] and 0 <= y < a.shape[0]:
            a[y, x] = (*c, 255)


def rage(a, seed, glitch=((PINK, -1, 0), (CYAN, 1, 0))):
    """Глитч-двойники за спрайтом + рваные шипы на контуре."""
    rng = random.Random(seed)
    a = a.copy()
    op = a[:, :, 3] > 0
    h, w = op.shape
    # двойники: сдвинутая копия силуэта цветом глитча там, где пусто
    for col, dx, dy in glitch:
        sh = np.roll(np.roll(op, dx * 2, 1), dy, 0)
        mask = sh & ~op
        # рвём двойника полосами
        for y in range(h):
            if rng.random() < 0.4:
                mask[y] = False
        a[mask] = (*col, 255)
    # шипы контура: чёрные пиксели наружу от силуэта
    outline = (a[:, :, 3] > 0) & (a[:, :, :3] == np.array(BLACK)).all(axis=2)
    ys, xs = np.nonzero(outline)
    for y, x in zip(ys, xs):
        if rng.random() < 0.16:
            dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, -1)])
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and a[ny, nx, 3] == 0:
                a[ny, nx] = (*BLACK, 255)
    return a


def anger_marks(a, color=RED):
    px(a, [(-2, 1), (-1, 0), (0, -1), (-2, 0)], color)      # левая «молния» ярости над головой
    px(a, [(27, 1), (26, 0), (25, -1), (27, 0)], color)
    px(a, [(-2, 12), (-3, 11), (-3, 13)], YELLOW)           # линии скорости по бокам
    px(a, [(28, 12), (29, 11), (29, 13)], YELLOW)
    return a


def hobo_p():
    b = s2.hobo_b()
    a = pad(b)
    a = rage(a, 3)
    # пена изо рта и бешеные зрачки-спирали
    px(a, [(9, 16), (10, 17), (10, 18), (15, 17), (16, 18), (16, 19)], WHITE)
    px(a, [(11, 18), (12, 19), (14, 18)], PINK)
    px(a, [(9, 11), (10, 11), (17, 11), (18, 11)], BLACK)
    px(a, [(9, 12), (18, 12)], RED)
    px(a, [(7, 7), (8, 6), (9, 7), (17, 6), (18, 5), (19, 6)], BLACK)     # торчащие дыбом брови
    px(a, [(13, 2), (12, 1), (14, 1), (13, 0)], YELLOW)                  # искры из вихра
    return anger_marks(a, GREEN)


def granny_p():
    b = s2.granny_b()
    a = pad(b)
    a = rage(a, 5, ((CYAN, -1, 0), (PINK, 1, 0)))
    px(a, [(10, 10), (11, 10), (14, 10), (15, 10)], WHITE)
    px(a, [(10, 10), (15, 10)], RED)
    px(a, [(9, 7), (10, 7), (14, 7), (15, 7)], BLACK)
    px(a, [(8, 12), (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 12)], BLACK)  # безумный оскал
    px(a, [(10, 12), (12, 12), (14, 12)], WHITE)
    px(a, [(7, 3), (8, 2), (9, 3), (16, 3), (17, 2), (18, 3)], PINK)     # бигуди торчат
    px(a, [(21, 22), (22, 22), (23, 22)], YELLOW)                        # клюка искрит
    return anger_marks(a, PINK)


def janitor_p():
    b = s2.janitor_b()
    a = pad(b)
    a = rage(a, 8, ((RED, -1, 0), (YELLOW, 1, 0)))
    px(a, [(9, 10), (10, 10), (15, 10), (16, 10)], WHITE)
    px(a, [(10, 10), (15, 10)], RED)
    px(a, [(8, 8), (9, 8), (10, 9), (15, 9), (16, 8), (17, 8)], BLACK)
    px(a, [(9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13)], BLACK)   # рот щёткой
    px(a, [(10, 13), (12, 13), (14, 13), (16, 13)], YELLOW)
    px(a, [(11, 14), (14, 14)], WHITE)
    px(a, [(12, 1), (13, 0), (14, 1), (13, -1)], WHITE)                 # налобный фонарь слепит
    px(a, [(5, 20), (6, 21), (19, 19), (20, 20)], BROWN := s2.BROWN)
    return anger_marks(a, RED)


def up(a, k=7):
    return Image.fromarray(a, "RGBA").resize((a.shape[1] * k, a.shape[0] * k), Image.NEAREST)


if __name__ == "__main__":
    k = 7
    names = ["hobo", "granny", "janitor"]
    bs = [s2.hobo_b(), s2.granny_b(), s2.janitor_b()]
    ps = [hobo_p(), granny_p(), janitor_p()]
    cell = (W + 2 * PAD) * k + 6
    sheet = Image.new("RGBA", (cell * 6 + 20, (H + 2 * PAD) * k + 12), (60, 40, 25, 255))
    x = 6
    for n, b, p in zip(names, bs, ps):
        for arr in (pad(b), p):
            im = up(arr, k)
            sheet.paste(im, (x, 6), im)
            x += cell
    sheet.save("tools/_preview/redraw_sample3.png")
