#!/usr/bin/env python3
"""Перерисовка героев в стиле B+: кислотная контр-тень, блики, налитые глаза, мухи, запечённый глитч (свой в каждом кадре).
Запуск: python3 tools/redraw_heroes.py [--apply]  (без --apply пишет только в tools/_preview/heroes_new)."""
import os, random, sys
import numpy as np
from PIL import Image
import importlib.util
spec = importlib.util.spec_from_file_location("s2", "tools/sample_redraw2.py")
s2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s2)
BLACK, WHITE, PINK, CYAN, YELLOW, RED, GREEN, PURPLE = s2.BLACK, s2.WHITE, s2.PINK, s2.CYAN, s2.YELLOW, s2.RED, s2.GREEN, s2.PURPLE
SHADE = {"blogger": (CYAN, YELLOW), "clerk": (PINK, WHITE), "courier": (PINK, YELLOW), "dacha": (CYAN, WHITE),
         "granny": (CYAN, WHITE), "guard": (PINK, YELLOW), "hobo": (PURPLE, YELLOW), "janitor": (RED, YELLOW),
         "pigeon": (PINK, WHITE), "plumber": (YELLOW, WHITE), "punk": (GREEN, WHITE), "shawarma": (CYAN, YELLOW),
         "skater": (PURPLE, YELLOW), "squid": (PINK, WHITE), "student": (YELLOW, WHITE), "uncle_vitya": (GREEN, WHITE)}


def shift(mask, dx):
    out = np.zeros_like(mask)
    if dx > 0: out[:, dx:] = mask[:, :-dx]
    else: out[:, :dx] = mask[:, -dx:]
    return out


def shift_rows(a, y0, h, d):
    seg = a[y0:y0 + h].copy()
    new = np.zeros_like(seg)
    if d > 0: new[:, d:] = seg[:, :-d]
    else: new[:, :d] = seg[:, -d:]
    a[y0:y0 + h] = new


def frame_fx(f, hero, row, rng):
    shade, hi = SHADE[hero]
    a = s2.enhance(f, shade, hi)
    op = a[:, :, 3] > 0
    if row in (0, 2):  # налитые глаза: часть белых пикселей в районе лица краснеет
        for y in range(4, 16):
            for x in range(26):
                if tuple(a[y, x, :3]) == tuple(WHITE) or tuple(a[y, x, :3]) == (240, 240, 240) or tuple(a[y, x, :3]) == (232, 232, 232):
                    if rng.random() < 0.28: a[y, x] = (*RED, 255)
    # двойники (глитч) только в свободные пиксели
    cols = (PINK, CYAN) if shade not in (PINK, CYAN) else (YELLOW, shade)
    for c in cols:
        dx = rng.choice([-2, -2, 2, 2, -1, 1])
        m = shift(op, dx) & ~op
        for y in range(26):
            if rng.random() < 0.55: m[y] = False
        a[m] = (*c, 255)
    # рваные полосы по верху и низу тела (середина с лицом чистая)
    for _ in range(rng.randint(1, 3)):
        y0 = rng.choice([rng.randint(14, 23), rng.randint(1, 5)])
        shift_rows(a, y0, rng.randint(1, 2), rng.choice([-2, -1, 1, 2]))
    ys, xs = np.nonzero(a[:, :, 3] > 0)
    for _ in range(rng.randint(3, 6)):
        i = rng.randrange(len(ys)); c = rng.choice([PINK, CYAN, YELLOW, GREEN, WHITE])
        if tuple(a[ys[i], xs[i], :3]) != tuple(BLACK): a[ys[i], xs[i]] = (*c, 255)
    for _ in range(8):  # шипы на контуре
        i = rng.randrange(len(ys)); dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        x, y = xs[i] + dx, ys[i] + dy
        if 0 <= x < 26 and 0 <= y < 26 and a[y, x, 3] == 0: a[y, x] = (*BLACK, 255)
    # мухи
    if rng.random() < 0.7:
        x, y = rng.choice([(1, 3), (24, 4), (2, 12), (23, 10), (24, 18)]); 
        if a[y, x, 3] == 0: a[y, x] = (*YELLOW, 255)
    return a


def redraw(hero, seed=1):
    rng = random.Random(hash(hero) % 1000 + seed)
    sh = Image.open(f"tools/_orig_art/player_{hero}.png").convert("RGBA")
    out = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    for r in range(3):
        for c in range(4):
            f = np.array(sh.crop((c * 26, r * 26, c * 26 + 26, r * 26 + 26)))
            out.paste(Image.fromarray(frame_fx(f, hero, r, rng), "RGBA"), (c * 26, r * 26))
    return out


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    os.makedirs("tools/_preview/heroes_new", exist_ok=True)
    heroes = list(SHADE)
    k = 4
    sheet = Image.new("RGBA", (8 * 26 * k + 10, 2 * 26 * k + 10), (45, 30, 20, 255))
    for i, h in enumerate(heroes):
        im = redraw(h)
        im.save(f"tools/_preview/heroes_new/player_{h}.png")
        if apply: im.save(f"assets/sprites/player_{h}.png")
        fr = im.crop((0, 52, 26, 78)).resize((26 * k, 26 * k), Image.NEAREST)
        sheet.paste(fr, ((i % 8) * 26 * k + 5, (i // 8) * 26 * k + 5), fr)
    sheet.save("tools/_preview/heroes_new.png")
