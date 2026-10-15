#!/usr/bin/env python3
"""Проволока (10 ячеек 48×16), сердечко HP (14×14), XP-кристалл (2 кадра 12×14). --apply пишет в assets."""
import sys, math, random
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
STEEL = (170, 175, 185); LSTEEL = (225, 228, 235); DSTEEL = (95, 98, 110); RUSTC = (150, 75, 35); LRUST = (205, 120, 55)
CW, CH = 48, 16

def barbed(metal, light, dark, barb, sag=1, tint=None, glitch=False, rng=None):
    c = Canvas(CW, CH)
    period = 16.0
    for x in range(CW):                                   # две скрученные проволоки
        s = math.sin(x / period * 2 * math.pi)
        y1 = 8 + s * 1.6; y2 = 8 - s * 1.6
        top, bot = (y1, y2) if s >= 0 else (y2, y1)
        c.px(x, round(bot), dark); c.px(x, round(bot) - 0, dark)
        c.px(x, round(top), light if (x // 2) % 2 else metal)
        c.px(x, round(top) + 1, metal)
    for bx in (8, 24, 40):                                # колючка: узел и 4 шипа
        c.rect(bx - 1, 7, bx + 1, 9, metal); c.px(bx, 7, light)
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            c.line(bx + dx, 8 + dy, bx + dx * 4, 8 + dy * 5, barb if barb != metal else light)
            c.px(bx + dx * 4, 8 + dy * 5, WHITE if dy < 0 else light)
    if tint:
        for bx in (16, 32): c.px(bx, 8, tint)
    return c.finish(DSTEEL, WHITE, lim=0.5, glitch=2 if glitch else 0, rng=rng)[1:-1, 1:-1]

def build_wire():
    r = random.Random(7)
    cells = []
    kinds = [  # (металл, свет, тень, шип)
        (STEEL, LSTEEL, DSTEEL, (120, 125, 135)), (RUSTC, LRUST, (95, 45, 20), (110, 50, 25)),
        ((60, 64, 72), (130, 135, 150), BLACK, (40, 42, 50)), ((90, 200, 80), (190, 255, 150), (20, 90, 30), GREEN),
        ((200, 60, 170), (255, 150, 235), (90, 10, 80), PINK), (STEEL, LSTEEL, DSTEEL, YELLOW)]
    for i, (m, l, d, b) in enumerate(kinds):
        cells.append(barbed(m, l, d, b, tint=(YELLOW if i == 5 else None), glitch=(i % 2 == 1), rng=r))
    for frame in range(2):   # ток: сталь + синие разряды
        a = barbed(STEEL, LSTEEL, DSTEEL, (120, 125, 135)).copy()
        for k in range(5):
            x = r.randint(2, 44); y = r.randint(1, 13)
            for j in range(4):
                xx, yy = x + j * 2, y + (j % 2) * 2 * (1 if (frame + k) % 2 else -1)
                if 0 <= xx < CW and 0 <= yy < CH: a[yy, xx] = (*(CYAN if j % 2 else WHITE), 255)
        cells.append(a)
    for frame in range(2):   # огонь: язычки над проволокой
        a = barbed((90, 60, 40), (150, 110, 80), BLACK, (70, 40, 30)).copy()
        for x in range(3, CW, 5):
            h = 4 + ((x + frame * 3) % 3) * 2
            for dy in range(h):
                col = YELLOW if dy < h // 3 else (ORANGE if dy < 2 * h // 3 else RED)
                for dx in ((0,) if dy > h // 2 else (-1, 0, 1)):
                    xx, yy = x + dx, 8 - dy
                    if 0 <= xx < CW and 0 <= yy < CH and a[yy, xx, 3] == 0: a[yy, xx] = (*col, 255)
        cells.append(a)
    return np.concatenate(cells, axis=1)

def from_mask(rows, cmap):
    h = len(rows); w = len(rows[0]); c = Canvas(w, h)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in cmap: c.px(x, y, cmap[ch])
    return c

def heart():
    rows = ["..RRR..RRR..",
            ".RWWRRRRRRR.",
            "RWWPRRRRRRRR",
            "RWPRRRRRRRDR",
            "RPRRRRRRRRDR",
            "RRRRRRRRRRDR",
            ".RRRRRRRRDD.",
            "..RRRRRRDD..",
            "...RRRRDD...",
            "....RRDD....",
            ".....RD.....",
            "............"]
    c = from_mask(rows, {"R": RED, "W": WHITE, "P": PINK, "D": (140, 0, 30)})
    c.pts([(5, 3), (6, 4), (5, 5), (6, 6)], BLACK)       # шов-трещина
    c.pts([(8, 11), (8, 10)], GREEN)                        # кислотная капля
    return c.finish((140, 0, 30), PINK, lim=2)

def xp(frame):
    rows = ["....GG....",
            "...GWWG...",
            "..GWLLGG..",
            ".GWLLLGGG.",
            ".GLLLLGGG.",
            ".GLLLLGGG.",
            ".GLLLDGGG.",
            ".GLLDDGGG.",
            "..GLDDGG..",
            "...GDDG...",
            "....GG...."]
    cm = {"G": GREEN, "W": WHITE, "L": (150, 255, 100), "D": (10, 150, 10)}
    c = from_mask(rows, cm)
    if frame: c.pts([(8, 1), (9, 0), (1, 9)], YELLOW); c.px(7, 3, WHITE)
    else: c.pts([(0, 8), (1, 9)], CYAN)
    return c.finish((10, 120, 10), WHITE, lim=2)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    w = build_wire(); Image.fromarray(w, "RGBA").save("tools/_preview/wire_new.png")
    h = heart(); x0 = xp(0); x1 = xp(1)
    Image.fromarray(h, "RGBA").save("tools/_preview/heart_new.png"); print(h.shape, x0.shape)
    def pad(a):
        o = np.zeros((14, 12, 4), np.uint8); h, w = a.shape[:2]; o[14 - h:, :w] = a; return o
    x0, x1 = pad(x0), pad(x1)
    xs = np.concatenate([x0, x1], axis=1); Image.fromarray(xs, "RGBA").save("tools/_preview/xp_new.png")
    k = 6
    prev = Image.new("RGBA", (480 * 2 + 20, 16 * 2 * k // 2 + 400), (60, 90, 40, 255))
    ww = Image.fromarray(w, "RGBA"); ww2 = ww.resize((ww.width * 2, ww.height * 2), Image.NEAREST); prev.paste(ww2, (10, 5), ww2)
    for i, im in enumerate([Image.fromarray(h, "RGBA"), Image.fromarray(x0, "RGBA"), Image.fromarray(x1, "RGBA")]):
        b = im.resize((im.width * 10, im.height * 10), Image.NEAREST); prev.paste(b, (10 + i * 200, 60), b)
    prev.save("tools/_preview/ui_new.png")
    if apply:
        Image.fromarray(w, "RGBA").save("assets/sprites/arena_wire.png")
        Image.fromarray(h, "RGBA").save("assets/ui/hud_heart.png")
        Image.fromarray(xs, "RGBA").save("assets/sprites/xp_pixel.png")
