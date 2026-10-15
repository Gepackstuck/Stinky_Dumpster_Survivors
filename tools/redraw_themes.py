#!/usr/bin/env python3
"""Темы границы арены: дома, надгробия, свалки, болото, машины, земля. Листы: вид × 4 кадра."""
import sys, random, math
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
import importlib.util
spec = importlib.util.spec_from_file_location("rd", "tools/redraw_decor.py")
rd = importlib.util.module_from_spec(spec); spec.loader.exec_module(rd)
FR = 4
GOLD = (255, 200, 0)
smoke = rd.smoke; fire = rd.fire


def save_sheet(path, kinds, cw, ch, W, H, glitch_frame=3, seed=0):
    out = Image.new("RGBA", (cw * FR * len(kinds), ch), (0, 0, 0, 0))
    for ki, fn in enumerate(kinds):
        for t in range(FR):
            c, (shade, hi) = fn(t)
            a = c.finish(shade, hi, glitch=(5 if t == glitch_frame else 0), rng=random.Random(seed + ki * 17 + t), lim=0.08)
            im = Image.fromarray(a, "RGBA")
            out.paste(im, ((ki * FR + t) * cw + (cw - im.width) // 2, ch - im.height), im)
    out.save(path)
    return out


# ---------- дома 48×44 ----------
def windows(c, x0, y0, cols, rows, dx, dy, t, lit=(YELLOW, CYAN, PINK)):
    rng = random.Random(7)
    for r in range(rows):
        for k in range(cols):
            x, y = x0 + k * dx, y0 + r * dy
            on = rng.random() < 0.55
            if on and (t + r + k) % 4 == 0 and rng.random() < 0.5: on = False
            c.rect(x, y, x + 3, y + 4, lit[(r + k) % len(lit)] if on else BLACK)
            if on and rng.random() < 0.2: c.px(x + 1, y + 2, BLACK)


def h_panel(t):
    c = Canvas(46, 42)
    c.rect(6, 6, 40, 41, GREY, dither=DGREY); c.rect(4, 4, 42, 6, DGREY)
    windows(c, 9, 9, 6, 5, 6, 6, t); c.rect(21, 36, 25, 41, BLACK)
    c.line(14, 4, 14, 0, DGREY); c.line(12, 1, 17, 1 + t % 2, DGREY); c.line(34, 4, 34, 1, DGREY)
    c.line(5, 20, 12, 22 + t % 2, WHITE); c.pts([(7, 22), (10, 23)], PINK)          # бельё
    c.pts([(30, 2), (38, 3 - t % 2)], YELLOW)
    return c, (PURPLE, WHITE)


def h_brick(t):
    c = Canvas(46, 42)
    c.rect(6, 14, 40, 41, RED, dither=(150, 0, 30))
    for y in range(16, 41, 4): c.line(6, y, 40, y, (110, 0, 20))
    c.rect(2, 8, 44, 14, BROWN, dither=ORANGE); c.rect(8, 4, 38, 8, BROWN)
    c.rect(32, 0, 36, 8, DGREY); smoke(c, 34, 2, t, GREY)
    windows(c, 10, 20, 3, 2, 10, 8, t); c.rect(20, 34, 26, 41, BROWN); c.px(25, 38, YELLOW)
    c.eye(36, 24, 2, (0, 1)); c.pts([(8, 12), (40, 12)], GREEN)
    return c, (CYAN, YELLOW)


def h_shack(t):
    c = Canvas(46, 42)
    c.rect(8, 18, 38, 41, BROWN, dither=(140, 90, 40))
    for x in range(10, 38, 4): c.line(x, 18, x, 41, (60, 30, 10))
    c.line(2, 18, 23, 4, DGREY, 2); c.line(23, 4, 44, 20, DGREY, 2); c.rect(4, 17, 42, 19, DGREY)
    c.rect(14, 26, 22, 36, BLACK if t % 3 else (50, 50, 0)); c.rect(28, 28, 34, 34, CYAN, dither=WHITE)
    c.ell(18, 31, 1, 1, YELLOW) if t % 3 == 0 else None
    c.rect(35, 6, 37, 12, DGREY); smoke(c, 36, 4, t, WHITE)
    c.line(6, 41, 4, 36, GREEN); c.pts([(42, 36), (40, 38)], GREEN)
    return c, (PINK, YELLOW)


def h_garage(t):
    c = Canvas(46, 42)
    c.rect(2, 16, 44, 41, GREY, dither=DGREY); c.rect(2, 12, 44, 16, DGREY)
    for i, x in enumerate((5, 17, 29)):
        op = (i == 1) * [0, 4, 8, 4][t]
        c.rect(x, 20, x + 10, 40, ORANGE if i != 1 else BLACK, dither=BROWN if i != 1 else None)
        if i != 1:
            for y in range(22, 40, 3): c.line(x, y, x + 10, y, (150, 70, 0))
        else:
            c.rect(x, 20, x + 10, 22 + 6 - op // 2, ORANGE)
            c.eye(x + 3, 33, 2, (1, 0)); c.eye(x + 8, 33, 2, (-1, 0))
    c.pts([(10, 8), (35, 6 + t % 2)], YELLOW); c.rect(18, 8, 28, 11, YELLOW); c.pts([(20, 9), (23, 9)], BLACK)
    return c, (CYAN, YELLOW)


def h_kiosk(t):
    c = Canvas(46, 42)
    c.rect(8, 16, 38, 41, (60, 160, 255), dither=CYAN); c.rect(12, 22, 34, 34, BLACK); c.rect(14, 24, 32, 32, (30, 40, 30))
    for x in range(4, 42, 6): c.rect(x, 10, x + 2, 16, PINK); c.rect(x + 3, 10, x + 5, 16, YELLOW)
    c.rect(4, 6, 42, 10, RED)
    c.rect(14, 1, 32, 5, BLACK if t in (1, 2) else DGREY); c.pts([(16, 3), (19, 3), (22, 3), (25, 3), (28, 3), (31, 3)] if t not in (1, 2) else [], YELLOW)
    c.ell(23, 28, 5, 3, BROWN); c.line(18, 28, 28, 28, RED); c.pts([(20, 26), (26, 26)], GREEN)
    c.rect(10, 36, 16, 40, DGREY)
    return c, (PINK, WHITE)


def h_tower(t):
    c = Canvas(46, 42)
    c.rect(12, 4, 34, 41, DGREY, dither=BLACK); c.rect(10, 2, 36, 5, GREY)
    windows(c, 15, 9, 3, 4, 6, 7, t, lit=(RED, PINK))
    c.ell(23, 20, 6, 6, WHITE) if False else None
    c.eye(23, 12, 5, [(0, 0), (1, 0), (0, 1), (-1, 0)][t])
    c.line(23, 2, 23, 0, GREY); c.ell(36, 8, 6, 4, GREY, dither=WHITE); c.line(36, 8, 40, 3, DGREY)
    c.rect(20, 34, 26, 41, BLACK); c.pts([(8, 30), (38, 20 - t)], YELLOW)
    return c, (GREEN, PINK)


HOUSES = [h_panel, h_brick, h_shack, h_garage, h_kiosk, h_tower]


# ---------- надгробия и свалки 48×32 ----------
def t_cross(t):
    c = Canvas(46, 30)
    c.rect(4, 26, 42, 28, BROWN, dither=GREEN); c.rect(20, 6, 24, 26, BROWN); c.rect(12, 11, 32, 14, BROWN)
    c.pts([(22, 16)], BLACK); c.px(14, 12 + t % 2, YELLOW)
    c.line(35, 24, 35 + t % 2, 18, GREEN); c.pts([(10, 4 + t), (38, 8)], CYAN)
    return c, (PURPLE, CYAN)


def t_stone(t):
    c = Canvas(46, 30)
    c.ell(23, 12, 11, 9, GREY, dither=WHITE); c.rect(12, 12, 34, 27, GREY, dither=WHITE); c.rect(8, 27, 38, 29, BROWN)
    c.rect(20, 7, 26, 8, BLACK); c.rect(22, 5, 24, 14, BLACK)
    c.eye(18, 18, 2, (0, 1)) if t in (1, 2) else None; c.eye(28, 18, 2, (0, 1)) if t in (1, 2) else None
    c.line(14, 22, 16, 26, BLACK)
    return c, (CYAN, WHITE)


def t_angel(t):
    c = Canvas(46, 30)
    c.rect(14, 22, 32, 28, GREY, dither=WHITE); c.rect(19, 10, 27, 22, WHITE, dither=GREY); c.ell(23, 7, 4, 4, WHITE)
    w = [0, 2, 4, 2][t]
    c.line(19, 12, 8, 6 - w, WHITE, 3); c.line(27, 12, 38, 6 - w, WHITE, 3); c.px(23, 6, RED); c.ell(23, 2, 5, 1, YELLOW)
    c.pts([(10, 20), (36, 18)], PINK)
    return c, (PINK, YELLOW)


def t_fresh(t):
    c = Canvas(46, 30)
    c.ell(23, 24, 20, 6, BROWN, dither=(70, 40, 20)); c.rect(21, 8, 25, 22, WHITE); c.rect(18, 12, 28, 14, WHITE)
    h = [0, 3, 6, 3][t]
    c.line(30, 24, 31, 24 - h, GREEN, 3); c.ell(31, 22 - h, 2, 2, GREEN); c.line(12, 24, 12, 20 - h // 2, PINK, 2)
    c.pts([(8, 4), (36, 6)], YELLOW)
    return c, (GREEN, WHITE)


def t_mausoleum(t):
    c = Canvas(46, 30)
    c.rect(8, 10, 38, 28, GREY, dither=DGREY); c.rect(4, 6, 42, 10, DGREY); c.rect(14, 2, 32, 6, GREY)
    for x in (10, 34): c.rect(x, 10, x + 3, 28, WHITE, dither=GREY)
    c.rect(18, 14, 28, 28, BLACK); c.rect(19, 15, 27, 20, (0, 80, 20) if t % 2 else BLACK)
    c.eye(21, 18, 2, (0, 0)) if t % 2 else None
    c.pts([(23, 0), (22, 1), (24, 1)], BLACK)
    return c, (GREEN, WHITE)


def t_coffin(t):
    c = Canvas(46, 30)
    c.line(8, 20, 38, 12, BROWN, 8); c.line(8, 20, 38, 12, (150, 90, 40), 3)
    lid = [0, 2, 5, 2][t]
    c.line(10, 14 - lid, 36, 6 - lid, BROWN, 3); c.eye(22, 14, 2, (0, 1)) if t > 0 else None
    c.pts([(40, 22), (6, 26)], GREEN); c.rect(4, 26, 42, 28, BROWN, dither=GREEN)
    return c, (PURPLE, YELLOW)


def t_candles(t):
    c = Canvas(46, 30)
    c.rect(4, 26, 42, 28, BROWN, dither=GREEN)
    for x, h in ((10, 10), (20, 16), (30, 8), (37, 12)):
        c.rect(x, 26 - h, x + 3, 26, WHITE, dither=YELLOW); c.px(x + 1, 25 - h, BLACK)
        fire(c, x + 1, 24 - h, t, 1)
    c.ell(23, 8, 1, 1, WHITE)
    return c, (PINK, YELLOW)


def t_ghost(t):
    c = Canvas(46, 30)
    c.ell(23, 12 - t % 2, 9, 10, WHITE, dither=CYAN)
    for k in range(4): c.rect(14 + k * 5, 18, 17 + k * 5, 24 + (k + t) % 2 * 3, WHITE, dither=CYAN)
    c.eye(19, 11 - t % 2, 3, (0, 1)); c.eye(27, 11 - t % 2, 3, (0, 1)); c.ell(23, 17, 3, 2, BLACK)
    c.rect(4, 28, 42, 29, BROWN, dither=GREEN)
    return c, (BLUE, CYAN)


TOMBS = [t_cross, t_stone, t_angel, t_fresh, t_mausoleum, t_coffin, t_candles, t_ghost]


def d_heap(t):
    c = Canvas(46, 30)
    c.ell(23, 24, 22, 10, BROWN, dither=GREEN)
    for (x, y, col) in ((10, 18, PINK), (18, 12, CYAN), (28, 14, YELLOW), (36, 20, GREEN), (23, 18, WHITE), (14, 22, RED)):
        c.rect(x, y, x + 5, y + 3, col); c.px(x + 1, y, WHITE)
    c.line(30, 10, 34, 4, GREY); c.ell(34, 4, 2, 2, WHITE)
    for k in range(3): c.px(8 + (t * 7 + k * 13) % 34, 6 + (t * 3 + k * 5) % 10, YELLOW)
    return c, (PURPLE, YELLOW)


def d_fire(t):
    c = Canvas(46, 30)
    c.ell(23, 24, 20, 7, DGREY, dither=BLACK)
    for (x, y) in ((10, 24), (20, 22), (32, 24)): c.rect(x, y, x + 6, y + 3, BROWN)
    fire(c, 16, 20, t, 2); fire(c, 28, 20, (t + 1) % 4, 2); smoke(c, 22, 6, t, DGREY)
    c.pts([(6, 6 + t), (40, 4)], ORANGE)
    return c, (RED, YELLOW)


def d_tires(t):
    c = Canvas(46, 30)
    for (x, y) in ((10, 24), (22, 24), (34, 24), (16, 15), (28, 15), (22, 7)):
        c.ell(x, y, 6, 5, BLACK); c.ell(x, y, 2, 2, GREY)
    smoke(c, 22, 4, t, DGREY); c.pts([(8 + t, 4)], GREEN)
    c.eye(22, 7, 1, (0, 0))
    return c, (GREEN, YELLOW)


def d_mount(t):
    c = Canvas(46, 30)
    c.ell(23, 28, 22, 20, BROWN, dither=GREEN)
    for (x, y, col) in ((12, 14, WHITE), (24, 8, PINK), (32, 16, CYAN), (18, 20, YELLOW), (28, 22, RED), (8, 22, GREEN)):
        c.rect(x, y, x + 4, y + 5, col)
    c.line(38, 4, 38, 14, DGREY, 2); c.line(38, 4, 28, 2, DGREY, 2); c.line(28, 2, 28, 6 + t * 2, GREY)  # кран-грабли
    c.ell(28, 8 + t * 2, 2, 2, GREY)
    return c, (PINK, YELLOW)


DUMPS = [d_heap, d_fire, d_tires, d_mount]


# ---------- болото 48×32 ----------
def s_pond(t):
    c = Canvas(46, 30)
    c.ell(23, 18, 21, 11, GREEN, dither=DGREEN); c.ell(23, 17, 15, 7, YELLOW, dither=GREEN)
    for k in range(4): c.ell(10 + k * 8, 17 - (t + k) % 4, 2, 2, WHITE)
    c.ell(23, 20, 3, 2, RED) if t % 2 else None
    return c, (CYAN, WHITE)


def s_reeds(t):
    c = Canvas(46, 30)
    c.ell(23, 26, 20, 4, DGREEN, dither=GREEN)
    for x in range(6, 42, 4):
        h = 12 + (x * 7) % 10; sw = [0, 1, 0, -1][(t + x // 4) % 4]
        c.line(x, 26, x + sw, 26 - h, GREEN, 2); c.rect(x + sw - 1, 24 - h, x + sw + 1, 27 - h, BROWN)
    c.pts([(10 + t * 6, 4), (30, 8)], YELLOW)
    return c, (PURPLE, YELLOW)


def s_toxic(t):
    c = Canvas(46, 30)
    c.ell(23, 20, 22, 8, CYAN, dither=GREEN); c.rect(8, 16, 14, 19 + t % 2, YELLOW); c.rect(30, 14 + t % 2, 36, 19, BLACK)
    for k in range(3): c.px(12 + k * 11, 20 - (t * 2 + k) % 5, WHITE)
    c.pts([(23, 20)], PINK); c.line(40, 12, 42, 6, GREEN, 2)
    return c, (PINK, WHITE)


def s_mud(t):
    c = Canvas(46, 30)
    c.ell(23, 22, 21, 7, BROWN, dither=(70, 40, 20))
    e = [0, 1, 2, 1][t]
    c.ell(14, 17 - e, 4, 4, GREEN); c.eye(14, 16 - e, 2, (0, 0)); c.ell(32, 18 - e // 2, 3, 3, GREEN); c.eye(32, 17 - e // 2, 2, (0, 0))
    c.pts([(23, 24), (24, 24)], BLACK)
    return c, (GREEN, YELLOW)


SWAMP = [s_pond, s_reeds, s_toxic, s_mud]


# ---------- машины 56×26, 2 кадра ----------
def car_base(c, body, roof, t, w=44, len_off=6):
    for x in (12 + len_off // 2, 12 + w - 8):
        c.ell(x, 20, 4, 4, BLACK); c.ell(x, 20, 2, 2, GREY)
        c.px(x + [0, 2][t % 2], 20 + [-2, 0][t % 2], WHITE)


def c_sedan(t):
    c = Canvas(54, 24)
    c.rect(4, 11, 50, 19, RED, dither=(150, 0, 30)); c.rect(14, 4, 38, 11, RED); c.rect(16, 6, 25, 10, CYAN, dither=WHITE); c.rect(28, 6, 36, 10, CYAN, dither=WHITE)
    c.eye(20, 8, 1, (0, 0)); c.eye(32, 8, 1, (0, 0), blood=False)
    c.rect(46, 13, 50, 15, YELLOW if t == 0 else WHITE); car_base(c, RED, RED, t, 46, 4); c.pts([(2, 17), (0, 18 + t)], DGREY)
    return c, (PURPLE, YELLOW)


def c_truck(t):
    c = Canvas(54, 24)
    c.rect(2, 4, 34, 19, YELLOW, dither=ORANGE); c.rect(34, 9, 50, 19, PINK); c.rect(40, 11, 48, 15, CYAN)
    c.line(4, 12, 32, 12, RED, 2); c.pts([(8, 8), (20, 7)], BLACK)
    car_base(c, YELLOW, PINK, t, 46, 4); c.ell(26, 20, 4, 4, BLACK)
    c.rect(48, 15, 50, 16, YELLOW if t else WHITE)
    return c, (CYAN, WHITE)


def c_bus(t):
    c = Canvas(54, 24)
    c.rect(2, 3, 50, 19, GREEN, dither=DGREEN)
    for k in range(6):
        c.rect(5 + k * 7, 6, 10 + k * 7, 11, CYAN, dither=WHITE)
        if (k + t) % 3 == 0: c.eye(7 + k * 7, 8, 1, (0, 0))
    c.rect(4, 14, 48, 15, YELLOW)
    car_base(c, GREEN, GREEN, t, 46, 4); c.ell(24, 20, 4, 4, BLACK); c.pts([(0, 17)], DGREY)
    return c, (PINK, YELLOW)


def c_police(t):
    c = Canvas(54, 24)
    c.rect(4, 11, 50, 19, WHITE, dither=GREY); c.rect(14, 5, 38, 11, WHITE); c.rect(16, 7, 25, 10, CYAN); c.rect(28, 7, 36, 10, CYAN)
    c.rect(4, 14, 50, 15, BLUE)
    c.rect(20, 2, 24, 4, RED if t == 0 else BLUE); c.rect(28, 2, 32, 4, BLUE if t == 0 else RED)
    c.rect(46, 13, 50, 14, YELLOW); car_base(c, WHITE, WHITE, t, 46, 4)
    return c, (CYAN, RED)


def c_garbage(t):
    c = Canvas(54, 24)
    c.rect(2, 4, 34, 19, GREEN, dither=DGREEN); c.rect(34, 8, 50, 19, GREEN); c.rect(40, 10, 48, 14, CYAN)
    c.rect(6, 7, 30, 10, DGREY); c.line(8, 16, 30, 16, YELLOW)
    car_base(c, GREEN, GREEN, t, 46, 4); c.ell(26, 20, 4, 4, BLACK); c.pts([(4 + t, 2)], YELLOW)
    return c, (PURPLE, YELLOW)


def c_hearse(t):
    c = Canvas(54, 24)
    c.rect(4, 7, 50, 19, BLACK, dither=DGREY); c.rect(8, 9, 32, 15, (40, 0, 60)); c.rect(10, 10, 30, 14, (BROWN)); c.line(10, 12, 30, 12, GOLD)
    c.rect(36, 9, 46, 14, CYAN, dither=WHITE); c.pts([(18, 5), (22, 5 - t)], GREEN)
    car_base(c, BLACK, BLACK, t, 46, 4); c.rect(46, 15, 50, 16, YELLOW)
    return c, (PURPLE, GREEN)


CARS = [c_sedan, c_truck, c_bus, c_police, c_garbage, c_hearse]


def ground_tiles():
    out = Image.new("RGBA", (48 * 5, 48), (0, 0, 0, 255))
    rng = random.Random(3)
    bases = [(60, 34, 16), (52, 52, 60), (30, 44, 26), (58, 44, 34), (22, 48, 40)]
    for i, b in enumerate(bases):
        a = np.zeros((48, 48, 4), np.uint8); a[:, :] = (*b, 255)
        for _ in range(160):
            x, y = rng.randrange(48), rng.randrange(48)
            d = rng.choice([-14, -8, 8, 14]); a[y, x, :3] = np.clip(np.array(b) + d, 0, 255)
        if i == 1:   # дорога: пунктир по центру, кромки
            a[22:26, :, :3] = (52, 52, 60)
            for x in range(0, 48, 12): a[23:25, x:x + 7] = (*YELLOW, 255)
            a[0:2, :] = (110, 110, 120, 255); a[46:48, :] = (110, 110, 120, 255)
        if i == 2:   # трава
            for _ in range(40): a[rng.randrange(48), rng.randrange(48)] = (*GREEN[:1], 120, 30, 255) if False else (40, 110, 30, 255)
        if i == 4:
            for _ in range(10):
                x, y = rng.randrange(40), rng.randrange(48); a[y, x:x + 6] = (30, 90, 60, 255)
        out.paste(Image.fromarray(a, "RGBA"), (i * 48, 0))
    out.save("assets/sprites/border_ground.png")


if __name__ == "__main__":
    save_sheet("assets/sprites/border_houses.png", HOUSES, 48, 44, 46, 42)
    save_sheet("assets/sprites/border_tombs.png", TOMBS, 48, 32, 46, 30, seed=100)
    save_sheet("assets/sprites/border_dumps.png", DUMPS, 48, 32, 46, 30, seed=200)
    save_sheet("assets/sprites/border_swamp.png", SWAMP, 48, 32, 46, 30, seed=300)
    # машины: 2 кадра, без глитча
    out = Image.new("RGBA", (56 * 2 * len(CARS), 26), (0, 0, 0, 0))
    for ki, fn in enumerate(CARS):
        for t in range(2):
            c, (shade, hi) = fn(t)
            im = Image.fromarray(c.finish(shade, hi, lim=0.1), "RGBA")
            out.paste(im, ((ki * 2 + t) * 56 + (56 - im.width) // 2, 26 - im.height), im)
    out.save("assets/sprites/border_cars.png")
    ground_tiles()
    # превью
    prev = Image.new("RGBA", (1100, 560), (45, 30, 20, 255)); y = 4
    for name in ("houses", "tombs", "dumps", "swamp", "cars"):
        im = Image.open(f"assets/sprites/border_{name}.png"); cw = 56 * 2 if name == "cars" else 48 * 4
        row = im.crop((0, 0, min(im.width, 1100 // 2), im.height)).resize((min(im.width, 550) * 2, im.height * 2), Image.NEAREST)
        prev.paste(row, (4, y), row); y += row.height + 6
    g = Image.open("assets/sprites/border_ground.png"); prev.paste(g, (4, y))
    prev.save("tools/_preview/themes.png")
