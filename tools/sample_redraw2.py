#!/usr/bin/env python3
"""Пример перерисовки v2: два варианта «безумнее». B — доработка оригинала (силуэт и контур те же, добавлена кислотная
контр-тень, блики, лишние детали). C — новый рисунок с кривым контуром, косыми глазами и перекошенной мордой."""
import math
import random
import numpy as np
from PIL import Image

W = H = 26
BLACK = (10, 10, 10); WHITE = (240, 240, 240); GREEN = (57, 255, 20); PINK = (255, 16, 240)
YELLOW = (247, 255, 0); RED = (255, 0, 51); BLUE = (30, 30, 255); CYAN = (0, 240, 255)
BROWN = (107, 62, 31); SKIN = (240, 190, 150); ORANGE = (255, 130, 0); GREY = (140, 140, 150); PURPLE = (120, 0, 160)
yy, xx = np.mgrid[0:H, 0:W]


def put(a, pts, c):
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H:
            a[y, x] = (*c, 255)


def opaque(a):
    return a[:, :, 3] > 0


def enhance(a, shade_color, hi_color=WHITE):
    """B: контр-тень кислотным цветом дизерингом справа-снизу + блики слева-сверху + дрожь контура не трогаем."""
    a = a.copy()
    op = opaque(a)
    ys, xs = np.nonzero(op)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    span = (x1 - x0) + (y1 - y0)
    base = a.copy()
    for y, x in zip(ys, xs):
        if tuple(base[y, x, :3]) == BLACK:
            continue
        u = ((x - x0) + (y - y0)) / span
        if u > 0.74 or (u > 0.62 and (x + y) % 2 == 0):
            if tuple(base[y, x, :3]) not in (WHITE,):
                a[y, x] = (*shade_color, 255)
        # блик: пиксель, у которого сверху/слева контур или пустота
        up = base[y - 1, x] if y > 0 else np.zeros(4)
        lf = base[y, x - 1] if x > 0 else np.zeros(4)
        if (up[3] == 0 or tuple(up[:3]) == BLACK) and (lf[3] == 0 or tuple(lf[:3]) == BLACK) and u < 0.4:
            a[y, x] = (*hi_color, 255)
    return a


def hobo_b():
    a = np.array(Image.open("tools/_orig_art/player_hobo.png").convert("RGBA").crop((0, 0, 26, 26)))
    a = enhance(a, (150, 0, 200), YELLOW)
    put(a, [(13, 6), (14, 6)], PINK)                       # воспалённый вихор
    put(a, [(9, 10), (10, 10), (16, 10), (17, 10)], RED)   # налитые кровью глаза
    put(a, [(12, 21), (12, 22), (12, 23)], GREEN)          # слюна течёт
    put(a, [(11, 22), (13, 24)], WHITE)
    put(a, [(6, 8), (5, 10), (20, 8), (21, 10)], YELLOW)   # мухи
    put(a, [(6, 12), (7, 13)], BLACK)                      # шрамы
    return a


def granny_b():
    a = np.array(Image.open("assets/sprites/player_granny.png").convert("RGBA").crop((0, 0, 26, 26)))
    a = enhance(a, CYAN, WHITE)
    put(a, [(10, 9), (11, 9), (13, 9), (14, 9)], WHITE)    # безумные выпученные глаза
    put(a, [(10, 9), (14, 9)], BLACK)
    put(a, [(9, 8), (10, 8), (11, 8), (13, 8), (14, 8), (15, 8)], BLACK)
    put(a, [(10, 12), (11, 12), (12, 12), (13, 12), (14, 12)], BLACK)  # оскал
    put(a, [(11, 13), (13, 13)], WHITE)
    put(a, [(8, 5), (9, 4), (17, 4), (18, 5)], PINK)       # бигуди
    return a


def janitor_b():
    a = np.array(Image.open("assets/sprites/player_janitor.png").convert("RGBA").crop((0, 0, 26, 26)))
    a = enhance(a, RED, YELLOW)
    put(a, [(9, 9), (10, 9), (14, 9), (15, 9)], WHITE)
    put(a, [(10, 9), (14, 9)], RED)
    put(a, [(9, 12), (10, 12), (11, 12), (12, 12), (13, 12), (14, 12), (15, 12)], BLACK)  # ощеренный рот
    put(a, [(10, 12), (12, 12), (14, 12)], YELLOW)
    put(a, [(7, 17), (8, 18), (17, 16), (18, 17), (15, 20)], BROWN)  # пятна
    put(a, [(5, 19), (5, 20), (21, 20)], PINK)
    return a


# ---------------------------------------------------------------- C: новый рисунок
def jblob(mask, cx, cy, rx, ry, rng, j=1.2, n=14):
    pts = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        k = 1 + rng.uniform(-j, j) / max(rx, ry)
        pts.append((cx + rx * k * math.cos(ang), cy + ry * k * math.sin(ang)))
    from PIL import ImageDraw
    im = Image.fromarray((mask * 255).astype(np.uint8))
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.array(im) > 0


def compose(layers, outline=2):
    union = np.zeros((H, W), bool)
    for m, _ in layers:
        union |= m
    out = np.zeros((H, W, 4), np.uint8)
    d = union.copy()
    for _ in range(outline):
        n = d.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n |= np.roll(np.roll(d, dy, 0), dx, 1)
        d = n
    out[d] = (*BLACK, 255)
    for m, c in layers:
        out[m] = (*c, 255)
    return out


def checker(mask, c, phase=0):
    return mask & ((xx + yy + phase) % 2 == 0)


def eye(a, cx, cy, r, pupil=(0, 0), iris=BLACK, sclera=WHITE):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5 and 0 <= x < W and 0 <= y < H:
                a[y, x] = (*sclera, 255)
    px, py = cx + pupil[0], cy + pupil[1]
    if 0 <= px < W and 0 <= py < H:
        a[py, px] = (*iris, 255)
        if r >= 2:
            a[py, px + 1] = (*iris, 255); a[py + 1, px] = (*iris, 255); a[py + 1, px + 1] = (*iris, 255)


def hobo_c():
    rng = random.Random(7)
    z = np.zeros((H, W), bool)
    body = jblob(z, 13, 15, 10, 8.5, rng, 1.6)
    hl = jblob(z, 9, 11, 4, 3, rng, 0.8) & body
    sh = body & (xx + yy > 36)
    arms = jblob(z, 4, 16, 3, 3.5, rng) | jblob(z, 22, 14, 3, 4, rng)
    boots = (xx >= 7) & (xx <= 11) & (yy >= 21) & (yy <= 24) | (xx >= 15) & (xx <= 20) & (yy >= 22) & (yy <= 24)
    tuft = ((xx >= 11) & (xx <= 12) & (yy >= 2) & (yy <= 8)) | ((xx >= 14) & (xx <= 15) & (yy >= 4) & (yy <= 7)) | ((xx == 9) & (yy >= 5) & (yy <= 7))
    a = compose([(boots, BROWN), (body | arms | tuft, GREEN), (checker(sh, PURPLE), PURPLE), (hl & ((xx + yy) % 3 != 0), (190, 255, 120))])
    eye(a, 9, 11, 3, (1, 0), BLACK)                       # левый глаз огромный
    eye(a, 18, 9, 2, (-1, 1), BLACK)                      # правый поменьше и выше — косые
    put(a, [(9, 11), (18, 9)], RED)
    put(a, [(6, 8), (7, 8), (8, 8), (7, 9)], BLACK)       # кривая бровь
    put(a, [(16, 6), (17, 6), (18, 6), (19, 7)], BLACK)
    for x in range(7, 20):                                # рваная пасть
        a[15, x] = (*BLACK, 255)
        a[16, x] = (*BLACK, 255)
        a[17 + (x % 2), x] = (*BLACK, 255) if x % 3 == 0 else a[17 + (x % 2), x]
    put(a, [(8, 16), (10, 17), (12, 16), (14, 17), (16, 16), (18, 17)], WHITE)    # клыки разные
    put(a, [(9, 17), (11, 15), (15, 15), (17, 15)], WHITE)
    put(a, [(13, 18), (13, 19), (14, 19), (13, 20)], PINK)                        # язык вывалился
    put(a, [(13, 21), (13, 22)], PINK)
    put(a, [(10, 20), (11, 21), (17, 20)], YELLOW)                                # пятна
    put(a, [(2, 5), (3, 4), (23, 6), (24, 5), (5, 2)], GREEN)                    # вонь
    put(a, [(21, 12), (22, 12), (21, 13)], BLACK)
    return a


def granny_c():
    rng = random.Random(11)
    z = np.zeros((H, W), bool)
    coat = jblob(z, 13, 18, 9.5, 6.5, rng, 1.3)
    sh = coat & (xx + yy > 32)
    hl = coat & (xx + yy < 22)
    face = jblob(z, 13, 10, 5.5, 5, rng, 0.8)
    scarf = jblob(z, 13, 6, 7.5, 4.5, rng, 1.0) | ((xx >= 5) & (xx <= 20) & (yy >= 7) & (yy <= 8))
    shoes = ((xx >= 7) & (xx <= 11) & (yy >= 23) & (yy <= 24)) | ((xx >= 15) & (xx <= 19) & (yy >= 23) & (yy <= 24))
    cane = (xx >= 22) & (xx <= 23) & (yy >= 12) & (yy <= 24)
    hook = (xx >= 20) & (xx <= 23) & (yy >= 11) & (yy <= 12)
    a = compose([(shoes, GREY), (cane | hook, BROWN), (coat, BLUE), (checker(sh, CYAN), CYAN), (hl & ((xx + yy) % 2 == 0), (140, 140, 255)), (face, SKIN), (scarf, RED)])
    put(a, [(7, 4), (10, 3), (14, 4), (17, 3), (19, 6), (9, 7), (13, 6)], YELLOW)  # горох
    eye(a, 10, 10, 2, (0, 0), BLACK)                       # очки-блюдца: огромные, пустые
    eye(a, 16, 10, 2, (1, 1), BLACK)
    for (cx, cy) in ((10, 10), (16, 10)):
        put(a, [(cx - 3, cy), (cx + 3, cy), (cx, cy - 3), (cx, cy + 3), (cx - 2, cy - 2), (cx + 2, cy - 2), (cx - 2, cy + 2), (cx + 2, cy + 2)], CYAN)
    put(a, [(13, 10), (13, 9)], CYAN)
    put(a, [(9, 13), (10, 14), (11, 14), (12, 13), (13, 14), (14, 14), (15, 13), (16, 14), (17, 13)], BLACK)   # кривая улыбка-пила
    put(a, [(10, 13), (12, 14), (14, 13), (16, 13)], WHITE)
    put(a, [(5, 17), (9, 21), (17, 22), (19, 17), (14, 19)], WHITE)             # горох на пальто
    put(a, [(5, 20), (6, 21), (20, 21)], PINK)
    return a


def janitor_c():
    rng = random.Random(23)
    z = np.zeros((H, W), bool)
    vest = jblob(z, 13, 16, 10.5, 6.5, rng, 1.4)
    sh = vest & (xx + yy > 34)
    legs = ((xx >= 8) & (xx <= 12) & (yy >= 20) & (yy <= 24)) | ((xx >= 14) & (xx <= 18) & (yy >= 20) & (yy <= 24))
    face = jblob(z, 13, 11, 5.5, 4.5, rng, 0.8)
    hat = jblob(z, 13, 6, 7, 3.6, rng, 1.0) | ((xx >= 4) & (xx <= 22) & (yy >= 7) & (yy <= 8))
    a = compose([(legs, BLUE), (vest, ORANGE), (checker(sh, RED), RED), (face, SKIN), (hat, YELLOW), (checker(hat & (xx + yy > 22), ORANGE), ORANGE)])
    put(a, [(11, 2), (12, 2), (13, 2), (14, 2)], WHITE); put(a, [(12, 1), (13, 1)], YELLOW)   # налобный фонарь горит
    eye(a, 10, 11, 2, (1, 0), BLACK, WHITE)
    eye(a, 16, 11, 1, (0, 0), RED, WHITE)                  # один глаз огромный, другой мелкий красный
    put(a, [(8, 8), (9, 9), (10, 9), (15, 9), (16, 9), (17, 8)], BLACK)
    put(a, [(9, 14), (10, 14), (11, 14), (12, 14), (13, 14), (14, 14), (15, 14), (16, 14), (17, 14)], BROWN)  # усищи-щётка
    put(a, [(9, 15), (17, 15), (12, 15), (13, 15), (14, 15)], BLACK)
    put(a, [(12, 15), (14, 15)], YELLOW)
    for y in (17, 20):
        for x in range(5, 22):
            if a[y, x, 3] and tuple(a[y, x, :3]) in (ORANGE, RED):
                a[y, x] = (*YELLOW, 255)
    put(a, [(6, 19), (7, 20), (17, 18), (18, 19), (15, 21)], BROWN)
    put(a, [(4, 17), (22, 19)], PINK)
    return a


def up(a, k=7):
    return Image.fromarray(a, "RGBA").resize((W * k, H * k), Image.NEAREST)


if __name__ == "__main__":
    names = ["hobo", "granny", "janitor"]
    olds = [np.array(Image.open(f"assets/sprites/player_{n}.png").convert("RGBA").crop((0, 0, 26, 26))) for n in names]
    bs = [hobo_b(), granny_b(), janitor_b()]
    cs = [hobo_c(), granny_c(), janitor_c()]
    k = 7
    sheet = Image.new("RGBA", (3 * (W * k + 8) * 3 + 12, H * k + 16), (60, 40, 25, 255))
    x = 8
    for o, b, c in zip(olds, bs, cs):
        for arr in (o, b, c):
            im = up(arr, k)
            sheet.paste(im, (x, 8), im)
            x += W * k + 8
        x += 10
    sheet.save("tools/_preview/redraw_sample2.png")
