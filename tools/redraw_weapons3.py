#!/usr/bin/env python3
"""Оружие в руках: лист 4 кадров 26×26 (96... 104×26). База рисуется один раз (тень/блики/контур), анимированные детали поверх.
python3 tools/redraw_weapons3.py [--apply] [имена]"""
import sys, os, math, random
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
S = 24
LG = (205, 205, 215); MG = (150, 150, 160); TIN = (190, 200, 210); WOOD = (170, 100, 50); RUST = (160, 70, 30)
CREAM = (255, 240, 170)
W = {}
def weapon(sh, hi=WHITE):
    def d(f): W[f.__name__] = (f, sh, hi); return f
    return d
def ring(c, cx, cy, r, col, th=1):
    for i in range(48):
        a = i / 48 * 2 * math.pi
        for dx in range(th):
            for dy in range(th): c.px(round(cx + math.cos(a) * r) + dx, round(cy + math.sin(a) * r) + dy, col)

# --- каждое оружие: f(c, t=None). t=None → статичная база, иначе анимированные детали кадра t (0..3)
@weapon(PURPLE, YELLOW)
def lighter(c, t=None):
    if t is None:
        c.rect(0, 9, 11, 17, MG, dither=LG); c.rect(1, 10, 10, 11, WHITE); c.rect(11, 9, 14, 17, LG); c.line(11, 9, 11, 17, DGREY)
        c.rect(12, 6, 14, 8, GREY); c.px(13, 6, WHITE); c.rect(3, 13, 8, 15, RED); c.px(4, 14, YELLOW); c.px(6, 14, YELLOW); c.rect(14, 10, 15, 12, DGREY)
    else:
        h = [4, 5, 4, 3][t]; w = [3, 2, 3, 3][t]
        c.ell(18, 11 - h // 2, w, h, ORANGE); c.ell(18, 12 - h // 2, max(w - 1, 1), h - 1, YELLOW); c.px(18 + (t % 2) - 1, 11 - h - 1, ORANGE); c.px(18, 12, WHITE)

@weapon(PURPLE, YELLOW)
def slipper(c, t=None):
    if t is None:
        c.ell(11, 15, 10, 4, BROWN, dither=(150, 90, 40)); c.ell(11, 12, 9, 4, PINK, dither=(255, 120, 245))
        c.rect(2, 9, 8, 12, PINK); c.rect(14, 8, 20, 13, PINK); c.ell(16, 10, 4, 3, (255, 90, 245)); c.line(14, 8, 18, 8, WHITE)
        c.rect(4, 6, 10, 9, BLACK); c.rect(5, 7, 9, 9, (40, 40, 40)); c.line(1, 18, 21, 18, BROWN, 2)
        c.rect(8, 4, 12, 8, DGREY); c.rect(9, 5, 11, 7, RED)
    else:
        c.px(10, 6, [YELLOW, WHITE, YELLOW, RED][t]); c.line(10, 4, 12 + (t % 2), 1, YELLOW); c.pts([(13 + t % 2, 0), (12, 0 + (t > 1))], ORANGE); c.px(13, 1 + (t % 2), WHITE)

@weapon(CYAN, WHITE)
def mop(c, t=None):
    if t is None:
        c.line(1, 20, 14, 8, BROWN, 2); c.line(1, 19, 13, 8, WOOD); c.rect(13, 3, 17, 12, GREY, dither=LG); c.line(13, 3, 17, 3, WHITE)
        c.rect(17, 6, 20, 19, (200, 200, 180), dither=(150, 150, 130))
    else:
        for i, y in enumerate(range(8, 23)):
            c.px(18 + ((i + t) % 3), y, WHITE if (i + t) % 2 else (190, 190, 170)); c.px(21 + (i + t) % 2 - 1, y, (170, 170, 140))
        c.pts([(19 + t, 21), (17 - t % 2, 22)], CYAN); c.px(15 + t, 23, GREEN)

@weapon(PURPLE, YELLOW)
def bottle(c, t=None):
    if t is None:
        c.rect(2, 8, 13, 17, GREEN, dither=(20, 170, 20)); c.ell(3, 12, 3, 5, GREEN); c.rect(13, 10, 20, 15, GREEN); c.rect(20, 9, 22, 16, GREY); c.line(20, 9, 22, 9, WHITE)
        c.rect(5, 10, 11, 15, WHITE); c.rect(6, 11, 10, 13, RED); c.px(8, 12, YELLOW); c.px(7, 14, BLACK); c.line(3, 8, 12, 8, (180, 255, 180))
    else:
        c.pts([(23, 10 + t), (23, 13 - t % 2)], YELLOW); c.px(6 + t * 2, 9, WHITE); c.px(2, 17 + t % 2, YELLOW); c.px(4 + t, 19, (200, 255, 120))

@weapon(GREEN)
def mosin(c, t=None):
    if t is None:
        c.rect(0, 13, 7, 19, BROWN, dither=(150, 90, 40)); c.rect(0, 12, 2, 13, BROWN); c.rect(7, 12, 12, 15, BROWN); c.rect(8, 10, 12, 12, DGREY)
        c.rect(8, 9, 10, 10, LG); c.px(11, 8, LG); c.rect(12, 11, 21, 13, DGREY, dither=GREY); c.line(12, 11, 21, 11, WHITE); c.rect(17, 13, 20, 14, BROWN)
        c.pts([(20, 9), (20, 10)], BLACK); c.line(21, 12, 23, 12, LG); c.rect(8, 15, 10, 16, GREY); c.px(9, 15, BLACK)
    else:
        c.px(9, 8 - (t == 1), [LG, WHITE, LG, LG][t]); c.px(11 + t % 2, 8, LG)
        if t == 1: c.pts([(22, 12), (22, 11)], YELLOW)

@weapon(GREEN)
def frying_pan(c, t=None):
    if t is None:
        c.line(0, 21, 9, 13, BROWN, 3); c.line(0, 20, 8, 13, WOOD); c.ell(16, 9, 7, 7, DGREY, dither=GREY); c.ell(16, 9, 5, 5, BLACK)
        c.ell(15, 8, 3, 3, YELLOW); c.ell(15, 8, 1, 1, ORANGE)
    else:
        c.pts([(12 + t, 3 - t % 2), (17 - t, 2)], WHITE); c.pts([(20, 3 + t), (21, 1 + t)], GREY); c.px(14 + t % 2, 7, WHITE)

@weapon(PURPLE, YELLOW)
def syringe(c, t=None):
    if t is None:
        c.rect(2, 10, 5, 13, PINK); c.rect(0, 9, 1, 14, GREY); c.rect(5, 9, 16, 14, (220, 240, 255), dither=WHITE)
        for x in (8, 10, 12, 14): c.px(x, 9, BLACK)
        c.rect(16, 10, 18, 13, GREY); c.line(18, 11, 23, 11, LG); c.pts([(3, 8), (3, 15)], BLACK)
    else:
        c.rect(7, 11, 15, 13, GREEN); c.px(7 + t * 2, 12, (180, 255, 120)); c.pts([(23, 13 + t % 2), (22, 15 + t % 2)], GREEN)

@weapon(CYAN, WHITE)
def condensed_milk(c, t=None):
    if t is None:
        c.rect(4, 6, 17, 20, TIN, dither=WHITE); c.rect(4, 6, 17, 8, GREY); c.rect(4, 18, 17, 20, GREY); c.rect(4, 9, 17, 17, BLUE); c.rect(5, 10, 8, 16, (80, 80, 255))
        c.ell(12, 13, 3, 3, WHITE); c.px(11, 12, BLACK); c.px(13, 12, BLACK); c.px(12, 14, PINK); c.rect(18, 7, 18, 11, GREY); c.rect(18, 8, 21, 10, WHITE)
    else:
        c.rect(21, 11, 21, 11 + t + 1, WHITE); c.px(21, 14 + t * 2, WHITE); c.px(20, 13 + t, WHITE)

@weapon(ORANGE, YELLOW)
def blowtorch(c, t=None):
    if t is None:
        c.ell(7, 13, 6, 6, RED, dither=(160, 0, 30)); c.rect(1, 8, 12, 18, RED, dither=(160, 0, 30)); c.rect(1, 11, 12, 14, YELLOW); c.rect(2, 8, 4, 9, WHITE)
        c.rect(5, 5, 9, 7, GREY); c.px(6, 4, WHITE); c.rect(12, 11, 18, 13, GREY, dither=LG); c.rect(18, 10, 19, 14, DGREY); c.line(7, 19, 9, 22, BROWN, 2)
    else:
        L = [4, 3, 4, 3][t]; c.rect(20, 10, 20 + L, 14, CYAN); c.rect(20, 11, 21 + L, 13, WHITE); c.px(21 + L, 12, BLUE); c.px(20 + (t % 2), 9, BLUE)

@weapon(PURPLE, YELLOW)
def crossbow(c, t=None):
    if t is None:
        c.rect(0, 11, 14, 13, BROWN, dither=WOOD); c.rect(2, 13, 6, 16, BROWN); c.line(14, 2, 18, 12, GREY, 2); c.line(14, 22, 18, 12, GREY, 2); c.px(14, 12, DGREY)
        c.line(7, 9, 14, 11, BLACK)
    else:
        sx = [10, 9, 10, 11][t]; c.line(14, 3, sx, 12, WHITE); c.line(14, 21, sx, 12, WHITE)
        c.line(sx, 12, 23, 12, BROWN); c.pts([(22, 11), (22, 13), (23, 12)], LG)

@weapon(ORANGE, YELLOW)
def extension_cord(c, t=None):
    if t is None:
        ring(c, 8, 12, 7, ORANGE, 2); ring(c, 8, 12, 4, YELLOW); ring(c, 8, 12, 9, RUST)
        c.line(14, 15, 17, 12, ORANGE, 2); c.rect(17, 9, 21, 15, WHITE, dither=LG); c.rect(21, 10, 23, 11, GREY); c.rect(21, 13, 23, 14, GREY)
    else:
        c.pts([(23 + t % 2 - 1, 9 + t % 3), (22, 15 - t % 2)], YELLOW); c.pts([(2 + t * 3, 6)], YELLOW); c.px(21 - t, 7, CYAN)
        if t % 2: c.line(22, 12, 23, 8, CYAN)

@weapon(RED, WHITE)
def laser_pointer(c, t=None):
    if t is None:
        c.rect(0, 10, 14, 14, DGREY, dither=GREY); c.rect(1, 11, 4, 12, WHITE); c.rect(14, 11, 17, 13, GREY); c.rect(5, 8, 9, 9, RED); c.px(9, 12, RED)
    else:
        c.rect(18, 12, 23 - t % 2, 12, RED); c.px(23, 12, [WHITE, PINK, WHITE, RED][t]); c.px(18, 11, WHITE if t % 2 else RED)

@weapon(GREEN)
def pipe_gun(c, t=None):
    if t is None:
        c.rect(6, 8, 21, 13, GREY, dither=RUST); c.rect(5, 7, 7, 14, DGREY); c.rect(19, 7, 22, 14, DGREY); c.line(6, 9, 21, 9, LG)
        c.rect(5, 13, 9, 19, RUST); c.rect(1, 14, 5, 17, BROWN); c.line(11, 8, 11, 13, YELLOW); c.line(14, 8, 14, 13, YELLOW)
    else:
        c.ell(23, 10 - t, [1, 2, 2, 1][t], [1, 2, 3, 2][t], (120, 120, 120)); c.px(22, 12, [DGREY, ORANGE, YELLOW, DGREY][t])

@weapon(PURPLE, YELLOW)
def plunger(c, t=None):
    if t is None:
        c.line(0, 18, 14, 11, BROWN, 2); c.line(0, 17, 13, 11, WOOD); c.rect(0, 16, 2, 20, BROWN)
    else:
        w = [5, 5, 4, 5][t]; x = 15 + (t == 2)
        c.ell(x + 3, 12, w - 2, w + 1, RED); c.rect(x - 1, 8 + (t == 2), x + 2, 15 - (t == 2), RED); c.ell(x + 5, 12, 2, w - 1, (255, 90, 90)); c.px(x + 4, 7, WHITE); c.pts([(x + 4, 12), (x + 5, 11)], BLACK)

@weapon(GREEN)
def rolling_pin(c, t=None):
    if t is None:
        c.rect(5, 8, 18, 15, (230, 190, 120), dither=(200, 150, 90)); c.rect(5, 8, 18, 9, WHITE); c.rect(0, 10, 5, 13, BROWN); c.rect(18, 10, 23, 13, BROWN); c.line(0, 10, 0, 13, WOOD)
        c.pts([(8, 11), (12, 12), (15, 10)], WOOD)
    else:
        c.pts([(6 + t * 4, 5 + t % 2), (10 + t * 2, 4), (3 + t, 7)], WHITE); c.px(20 - t, 16 + t % 2, WHITE)

@weapon(GREEN)
def rotten_cheese(c, t=None):
    if t is None:
        c.rect(3, 9, 20, 18, YELLOW, dither=(220, 220, 0)); c.line(3, 9, 20, 5, YELLOW, 1); c.rect(3, 9, 5, 18, (200, 200, 0)); c.line(20, 5, 20, 18, YELLOW)
        c.ell(9, 13, 2, 2, BLACK); c.ell(15, 15, 2, 2, BLACK); c.ell(17, 10, 1, 1, BLACK); c.ell(8, 17, 1, 1, BLACK); c.line(3, 9, 17, 6, WHITE)
        c.pts([(6, 11), (13, 16), (10, 10)], GREEN)
    else:
        for i in range(3):
            c.px(6 + i * 6 + (t + i) % 2, 3 - (t + i) % 3, GREEN); c.px(6 + i * 6, 1 + (t + i) % 2, (120, 255, 60))
        c.px(2 + t * 5, 21 - t, BLACK); c.px(3 + t * 5, 21 - t, DGREY)

@weapon(PURPLE, YELLOW)
def shiv(c, t=None):
    if t is None:
        c.line(8, 14, 22, 10, LG, 2); c.line(8, 13, 22, 9, WHITE); c.rect(0, 13, 6, 17, DGREY); c.rect(1, 14, 5, 15, BLUE); c.rect(7, 11, 8, 18, GREY)
        c.line(0, 16, 6, 16, BLACK)
    else:
        gx = 10 + t * 3; c.px(gx, 12 - t // 2 * 1, YELLOW); c.px(gx, 11 - t // 2, WHITE); c.px(gx - 1, 12, WHITE)

@weapon(GREEN)
def shovel(c, t=None):
    if t is None:
        c.line(0, 18, 14, 11, BROWN, 2); c.line(0, 17, 13, 11, WOOD); c.rect(0, 15, 3, 19, BROWN); c.rect(0, 15, 3, 15, WOOD)
        c.rect(15, 7, 22, 16, GREY, dither=LG); c.line(15, 7, 22, 7, WHITE); c.rect(14, 10, 15, 13, DGREY); c.pts([(18, 12), (19, 11)], RUST)
    else:
        c.pts([(16 + t, 17 + t % 2), (19 - t % 2, 18), (21, 17 + t)], BROWN); c.px(17 + t * 2, 6, BROWN)

@weapon(PURPLE, YELLOW)
def slingshot(c, t=None):
    if t is None:
        c.line(2, 20, 8, 11, BROWN, 3); c.line(8, 11, 14, 3, BROWN, 3); c.line(8, 11, 14, 20, BROWN, 3); c.px(2, 19, WOOD); c.px(7, 11, WOOD)
    else:
        sx = [19, 18, 19, 20][t]; c.line(15, 3, sx, 12, PINK); c.line(15, 20, sx, 12, PINK); c.ell(sx + 1, 12, 2, 2, GREY); c.px(sx, 11, WHITE)

@weapon(CYAN, WHITE)
def sock(c, t=None):
    if t is None:
        c.rect(2, 5, 9, 12, WHITE, dither=LG); c.rect(2, 12, 18, 19, WHITE, dither=LG); c.rect(2, 5, 9, 6, RED); c.rect(2, 8, 9, 9, RED); c.rect(2, 14, 18, 15, PINK)
        c.rect(14, 12, 19, 19, (220, 220, 200)); c.pts([(8, 17), (9, 17), (8, 18)], BROWN); c.rect(2, 17, 5, 18, (220, 220, 200))
    else:
        for i in range(3):
            y = 2 + (i * 2 + t) % 4; c.px(5 + i * 5, y, GREEN); c.px(6 + i * 5, y - 1, (120, 255, 60))
        c.pts([(10 + t % 2, 20), (14 - t % 2, 22)], GREEN)

@weapon(CYAN, WHITE)
def spray_can(c, t=None):
    if t is None:
        c.rect(2, 7, 13, 17, PINK, dither=(200, 0, 190)); c.rect(3, 8, 4, 16, WHITE); c.rect(6, 10, 11, 14, YELLOW); c.px(8, 12, BLACK); c.px(9, 12, BLACK)
        c.rect(13, 8, 16, 16, GREY); c.rect(16, 10, 18, 14, DGREY); c.px(18, 12, RED)
    else:
        for i in range(5):
            c.px(19 + (i * 3 + t * 2) % 5, 8 + (i * 5 + t) % 9, GREEN if i % 2 else (120, 255, 60))
        c.ell(21, 12, [1, 2, 3, 2][t], [2, 3, 3, 2][t], (80, 255, 40)); c.px(19, 12, WHITE)

@weapon(ORANGE, YELLOW)
def tin_bomb(c, t=None):
    if t is None:
        c.rect(3, 8, 16, 21, TIN, dither=WHITE); c.rect(3, 8, 16, 9, GREY); c.rect(3, 20, 16, 21, GREY); c.rect(3, 12, 16, 17, RED); c.px(9, 14, BLACK); c.pts([(8, 13), (10, 13), (8, 15), (10, 15)], BLACK)
        c.line(9, 8, 9, 4, BROWN)
    else:
        c.px(9 + (t % 2), 3, [YELLOW, ORANGE, WHITE, YELLOW][t]); c.pts([(8 + t, 2), (11 - t % 2, 1)], ORANGE); c.px(9, 1 + t % 2, YELLOW)

def render(name, t, seed=0):
    f, sh, hi = W[name]
    c = Canvas(S, S); f(c); base = c.finish(sh, hi, lim=0.14)          # 26×26
    out = base.copy()
    ca = Canvas(S, S); f(ca, t)
    if (ca.a[:, :, 3] > 0).any():
        an = ca.finish(sh, hi, outline=False, lim=9)
        pad = np.zeros_like(out); pad[1:-1, 1:-1] = an
        m = pad[:, :, 3] > 0; out[m] = pad[m]
        o = out[:, :, 3] > 0; n = np.zeros_like(o)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]: n |= np.roll(np.roll(o, dx, 1), dy, 0)
        out[n & ~o] = (*BLACK, 255)
    if t == 3:                                                           # глитч-кадр: съехавшие строки и цветные призраки
        r = random.Random(hash(name) & 0xffff)
        for y in r.sample(range(4, 22), 3): out[y] = np.roll(out[y], r.choice([-1, 1]), 0)
        op = out[:, :, 3] > 0
        for col, dx in ((PINK, -1), (CYAN, 1)):
            g = np.roll(op, dx, 1) & ~op
            for y in range(26):
                if r.random() < 0.7: g[y] = False
            out[g] = (*col, 255)
    return out

def sheet_of(name): return np.concatenate([render(name, t) for t in range(4)], axis=1)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(W)
    k = 4; cols = 6; rows = (len(names) + cols - 1) // cols
    cw, ch = 4 * 26 * k + 24, 26 * k + 18
    prev = Image.new("RGBA", (cols * cw, rows * ch), (45, 30, 20, 255))
    for i, n in enumerate(names):
        im = Image.fromarray(sheet_of(n), "RGBA")
        if apply: im.save(f"assets/sprites/held_{n}.png")
        big = im.resize((im.width * k, im.height * k), Image.NEAREST)
        prev.paste(big, ((i % cols) * cw + 8, (i // cols) * ch + 6), big)
    prev.save("tools/_preview/weapons_all.png"); print(len(names), prev.size)
