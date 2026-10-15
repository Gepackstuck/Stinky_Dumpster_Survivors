#!/usr/bin/env python3
"""ПРИМЕР перерисовки: тот же кислотный стиль, но с объёмом (свет/тень дизерингом), чистым контуром и читаемыми деталями.
Пишет tools/_preview/redraw_sample.png (старое слева, новое справа, x8)."""
import numpy as np
from PIL import Image

W = H = 26
BLACK = (10, 10, 10); WHITE = (240, 240, 240); GREEN = (57, 255, 20); PINK = (255, 16, 240)
YELLOW = (247, 255, 0); RED = (255, 0, 51); BLUE = (30, 30, 255); CYAN = (0, 240, 255)
BROWN = (107, 62, 31); SKIN = (240, 190, 150); ORANGE = (255, 130, 0); GREY = (140, 140, 150)
yy, xx = np.mgrid[0:H, 0:W]


def ell(cx, cy, rx, ry):
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0


def box(x0, y0, x1, y1):
    return (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)


def tone(c, k):
    """k<0 — темнее и холоднее (в сторону фиолетового), k>0 — светлее и ближе к белому."""
    c = np.array(c, float)
    if k < 0:
        return tuple(int(v) for v in (c * (1 + k) + np.array([40, 0, 70]) * (-k) * 0.6))
    return tuple(int(v) for v in (c + (np.array([255, 255, 255]) - c) * k))


class Canvas:
    def __init__(self):
        self.px = np.zeros((H, W, 4), np.uint8)
        self.layers = []

    def part(self, mask, color, shade=True):
        self.layers.append((mask, color, shade))

    def render(self):
        union = np.zeros((H, W), bool)
        for m, _, _ in self.layers:
            union |= m
        out = np.zeros((H, W, 4), np.uint8)
        # контур: 1 px чёрный вокруг всего силуэта
        d = union.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d |= np.roll(np.roll(union, dy, 0), dx, 1)
        out[d] = (*BLACK, 255)
        for m, color, shade in self.layers:
            ys, xs = np.nonzero(m)
            if len(ys) == 0:
                continue
            x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            span = max((x1 - x0) + (y1 - y0), 1)
            for y, x in zip(ys, xs):
                col = color
                if shade:
                    u = ((x - x0) + (y - y0)) / span
                    if u > 0.72:
                        col = tone(color, -0.5)
                    elif u > 0.58 and (x + y) % 2 == 0:
                        col = tone(color, -0.5)
                    elif u < 0.2:
                        col = tone(color, 0.5)
                    elif u < 0.3 and (x + y) % 2 == 0:
                        col = tone(color, 0.5)
                out[y, x] = (*col, 255)
        return out

    def dot(self, out, x, y, c):
        out[y, x] = (*c, 255)


def put(out, pts, c):
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H:
            out[y, x] = (*c, 255)


def hobo():
    c = Canvas()
    c.part(box(8, 21, 11, 24), BROWN); c.part(box(15, 21, 18, 24), BROWN)           # ботинки
    c.part(ell(13, 15, 9.5, 8), GREEN)                                               # тело
    c.part(ell(5, 15, 2.6, 3), GREEN); c.part(ell(21, 15, 2.6, 3), GREEN)            # лапы
    c.part(box(12, 3, 13, 7), GREEN); c.part(box(14, 4, 15, 6), GREEN)               # вихор
    out = c.render()
    # заплатка-рвань на пузе
    for y in range(17, 21):
        for x in range(10, 16):
            out[y, x] = (*BROWN, 255)
    put(out, [(11, 17), (13, 17), (15, 17), (11, 20), (13, 20), (15, 20)], BLACK)    # стежки
    put(out, [(12, 18), (13, 18), (12, 19), (13, 19)], tone(BROWN, 0.35))
    # глаза: большие, злые
    for ex in (9, 16):
        for y in range(9, 14):
            for x in range(ex, ex + 4):
                if (x - ex - 1.5) ** 2 / 2.6 + (y - 11) ** 2 / 6.5 <= 1.0:
                    out[y, x] = (*WHITE, 255)
        put(out, [(ex + 1, 11), (ex + 2, 11), (ex + 1, 12), (ex + 2, 12)], BLACK)
        put(out, [(ex + 1, 11)], PINK)
    put(out, [(8, 9), (9, 9), (10, 8), (17, 8), (18, 9), (19, 9)], BLACK)             # злые брови
    # пасть с зубами
    for x in range(9, 18):
        out[15, x] = (*BLACK, 255)
        out[16, x] = (*BLACK, 255)
    put(out, [(10, 16), (12, 16), (14, 16), (16, 16)], WHITE)
    put(out, [(11, 15), (13, 15), (15, 15)], WHITE)
    put(out, [(13, 17), (14, 17)], PINK)                                              # язык
    # вонь
    put(out, [(2, 6), (3, 5), (22, 7), (23, 6), (4, 3), (21, 4)], GREEN)
    return out


def granny():
    c = Canvas()
    c.part(box(8, 22, 11, 24), GREY); c.part(box(15, 22, 18, 24), GREY)              # тапки
    c.part(ell(13, 17, 8.5, 6.5), BLUE)                                              # пальто
    c.part(ell(13, 9, 5, 5), SKIN)                                                   # лицо
    c.part(ell(13, 6, 6.5, 4.5), RED)                                                # платок
    c.part(box(21, 11, 22, 23), BROWN, shade=False)                                  # палка
    c.part(box(20, 10, 23, 11), BROWN, shade=False)
    out = c.render()
    put(out, [(9, 17), (14, 15), (17, 19), (11, 20), (16, 22 - 3)], WHITE)           # горох на пальто
    put(out, [(9, 5), (13, 4), (17, 5), (11, 7), (15, 7)], YELLOW)                   # горох на платке
    # очки
    for ex in (9, 14):
        for y in range(8, 11):
            for x in range(ex, ex + 3):
                out[y, x] = (*CYAN, 255)
        put(out, [(ex, 8), (ex + 2, 8), (ex, 10), (ex + 2, 10)], BLACK)
        put(out, [(ex + 1, 9)], BLACK)
    put(out, [(12, 9), (12, 8)], BLACK)
    put(out, [(11, 12), (12, 12), (13, 12), (14, 12)], BLACK)                         # поджатые губы
    put(out, [(13, 11)], tone(SKIN, -0.4))
    return out


def janitor():
    c = Canvas()
    c.part(box(8, 22, 11, 24), BLACK, shade=False); c.part(box(15, 22, 18, 24), BLACK, shade=False)
    c.part(box(9, 19, 17, 22), BLUE)                                                 # штаны
    c.part(ell(13, 15, 9.5, 5.5), ORANGE)                                            # жилет
    c.part(ell(13, 10, 5, 4.5), SKIN, shade=False)                                    # лицо
    c.part(ell(13, 5, 6.5, 3.5), YELLOW); c.part(box(5, 6, 21, 7), YELLOW)           # каска
    out = c.render()
    for y in (14, 17):
        for x in range(5, 22):
            if out[y, x, 3] and tuple(out[y, x, :3]) != BLACK:
                out[y, x] = (*YELLOW, 255)                                            # световозвращающие полосы
    put(out, [(12, 2), (13, 2), (14, 2)], WHITE)                                      # фонарь на каске
    put(out, [(10, 10), (16, 10), (11, 10), (15, 10)], WHITE); put(out, [(11, 10), (15, 10)], BLACK)   # глаза
    put(out, [(9, 9), (10, 9), (16, 9), (17, 9)], BLACK)                              # брови
    put(out, [(10, 12), (11, 12), (12, 12), (14, 12), (15, 12), (16, 12), (11, 13), (15, 13)], BROWN)  # усы
    put(out, [(13, 13), (13, 14)], RED)
    return out


def up(a, k=8):
    return Image.fromarray(a, "RGBA").resize((W * k, H * k), Image.NEAREST)


if __name__ == "__main__":
    names = ["hobo", "granny", "janitor"]
    fns = [hobo, granny, janitor]
    sheet = Image.new("RGBA", (W * 8 * 6 + 70, H * 8 + 20), (60, 40, 25, 255))
    x = 10
    for n, fn in zip(names, fns):
        old = Image.open(f"assets/sprites/player_{n}.png").convert("RGBA").crop((0, 0, 26, 26)).resize((W * 8, H * 8), Image.NEAREST)
        sheet.paste(old, (x, 10), old); x += W * 8 + 5
        new = up(fn()); sheet.paste(new, (x, 10), new); x += W * 8 + 12
    sheet.save("tools/_preview/redraw_sample.png")
