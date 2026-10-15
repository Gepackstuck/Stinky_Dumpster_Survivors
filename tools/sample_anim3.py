#!/usr/bin/env python3
"""Анимация B+: 3 героя × 4 стороны × 4 кадра ходьбы, глитч каждый тик (полосы, двойники, шум, мерцание)."""
import random
import numpy as np
from PIL import Image
import importlib.util
spec = importlib.util.spec_from_file_location("s2", "tools/sample_redraw2.py")
s2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s2)
B = s2
PAD = 5; S = 26 + 2 * PAD
HEROES = {"hobo": (s2.PURPLE, s2.YELLOW, s2.GREEN, [s2.PINK, s2.CYAN]),
          "granny": (s2.CYAN, s2.WHITE, s2.PINK, [s2.CYAN, s2.PINK]),
          "janitor": (s2.RED, s2.YELLOW, s2.RED, [s2.RED, s2.YELLOW])}
EYE = {"hobo": [(9, 11), (10, 11), (17, 11), (18, 11)], "granny": [(10, 10), (15, 10)], "janitor": [(10, 10), (15, 10)]}

def frame(hero, row, col):
    sh = Image.open(f"assets/sprites/player_{hero}.png").convert("RGBA")
    return np.array(sh.crop((col * 26, row * 26, col * 26 + 26, row * 26 + 26)))

def padded(a):
    o = np.zeros((S, S, 4), np.uint8); o[PAD:PAD + 26, PAD:PAD + 26] = a; return o

def glitch(a, hero, front, rng, t):
    shade, hi, mark, gl = HEROES[hero]
    a = a.copy()
    op0 = a[:, :, 3] > 0
    # двойники с рандомным сдвигом, каждый тик другой
    for c in gl:
        dx = rng.choice([-3, -2, 2, 3]); dy = rng.choice([0, 0, 1])
        m = np.roll(np.roll(op0, dx, 1), dy, 0) & ~op0
        for y in range(S):
            if rng.random() < 0.5: m[y] = False
        a[m] = (*c, 255)
    # горизонтальные рваные полосы: сдвиг строк
    for _ in range(rng.randint(2, 4)):
        y0 = rng.choice([rng.randint(PAD + 15, PAD + 24), rng.randint(PAD, PAD + 6)]); h = rng.randint(1, 3); d = rng.choice([-3, -2, 2, 3])
        a[y0:y0 + h] = np.roll(a[y0:y0 + h], d, 1)
    # цветовые блоки-шум на теле
    ys, xs = np.nonzero(a[:, :, 3] > 0)
    for _ in range(rng.randint(4, 9)):
        i = rng.randrange(len(ys)); c = rng.choice([s2.PINK, s2.CYAN, s2.YELLOW, s2.GREEN, s2.WHITE])
        a[ys[i], xs[i]] = (*c, 255)
    # шипы
    for _ in range(10):
        i = rng.randrange(len(ys)); dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        x, y = xs[i] + dx, ys[i] + dy
        if 0 <= x < S and 0 <= y < S and a[y, x, 3] == 0: a[y, x] = (*s2.BLACK, 255)
    # линии ярости вокруг
    for _ in range(3):
        x = rng.choice([rng.randint(0, 3), rng.randint(S - 4, S - 1)]); y = rng.randint(2, S - 4)
        for k in range(rng.randint(2, 4)):
            if 0 <= y + k < S: a[y + k, x] = (*mark, 255)
    if front:  # налитые глаза бешено дёргаются
        for x, y in EYE[hero]:
            a[y + PAD + rng.choice([0, 0, 1]), x + PAD] = (*(s2.RED if rng.random() < .6 else s2.WHITE), 255)
    return a

def render(k=5, ticks=16):
    rng = random.Random(7)
    cols = 4; rows = 3
    imgs = []
    for t in range(ticks):
        sheet = Image.new("RGBA", (cols * S * k, rows * S * k), (45, 30, 20, 255))
        for ri, hero in enumerate(HEROES):
            shade, hi, *_ = HEROES[hero]
            for ci, (row, flip, front) in enumerate([(2, False, True), (0, False, False), (1, False, False), (0, True, False)]):
                f = frame(hero, row, (t // 2) % 4)
                if flip: f = f[:, ::-1].copy()
                f = s2.enhance(f, shade, hi)
                a = glitch(padded(f), hero, front, rng, t)
                im = Image.fromarray(a, "RGBA").resize((S * k, S * k), Image.NEAREST)
                sheet.paste(im, (ci * S * k, ri * S * k), im)
        imgs.append(sheet.convert("P", palette=Image.ADAPTIVE))
    imgs[0].save("tools/_preview/anim_b_plus3.gif", save_all=True, append_images=imgs[1:], duration=90, loop=0, disposal=2)

render()
