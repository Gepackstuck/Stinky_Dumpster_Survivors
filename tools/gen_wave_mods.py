#!/usr/bin/env python3
"""Модификаторы волн: значки 32×32 (+_s 16×16) и мусоровоз 48×28 (2 кадра колёс).
python3 tools/gen_wave_mods.py --apply  (превью tools/_preview/wave_mods.png)"""
import sys
sys.path.insert(0, "tools")
from icon_kit import *

I = {}
def ic(sh=PURPLE, hi=WHITE, lim=0.4):
    def d(f): I[f.__name__] = (f, sh, hi, lim); return f
    return d

@ic(DGREEN, YELLOW, 0.5)
def mod_acid_rain(c):   # грязная туча с глазами, кислотные капли и дымящаяся лужа
    for (x, y, r) in [(8, 7, 6), (15, 5, 7), (21, 8, 5)]:
        c.ell(x, y, r, r * 0.8, GREY, dither=DGREY)
    c.eye(11, 7, 2, (0, 1)); c.eye(18, 6, 1.5, (0, 1))
    for (x, y) in [(6, 15), (13, 18), (20, 14), (9, 22), (17, 23)]:
        poly(c, [(x, y - 3), (x + 2, y + 1), (x, y + 2), (x - 2, y + 1)], GREEN)
    c.ell(14, 26, 10, 1.6, LGREEN, dither=GREEN); c.pts([(5, 25), (23, 24)], YELLOW)

@ic(DGREY, YELLOW, 0.4)
def mod_darkness(c):   # разбитая лампочка, из темноты пялятся глаза
    c.rect(0, 0, 27, 27, (20, 18, 28), dither=(30, 26, 40))
    c.ell(14, 10, 6, 7, (220, 220, 160), dither=(180, 180, 120)); c.rect(11, 16, 17, 21, GREY, dither=DGREY)
    c.line(11, 6, 15, 12, BLACK); c.line(15, 12, 13, 15, BLACK); c.px(17, 8, BLACK)
    c.eye(4, 22, 1.5, (1, 0), iris=RED); c.eye(23, 21, 2, (-1, 0), iris=RED); c.eye(24, 4, 1, (-1, 1), iris=RED)

@ic(DBROWN, YELLOW, 0.4)
def mod_garbage_truck(c):   # морда мусоровоза с клыками
    c.rect(2, 6, 25, 21, GREEN, dither=DGREEN); c.rect(4, 8, 23, 12, (150, 220, 255), dither=CYAN)
    c.eye(9, 10, 2, (1, 1)); c.eye(18, 10, 3, (-1, 1))
    c.rect(4, 15, 23, 19, BLACK); c.teeth(5, 22, 15, WHITE, BLACK, 3)
    c.ell(6, 23, 3, 3, BLACK); c.ell(21, 23, 3, 3, BLACK); c.px(6, 23, GREY); c.px(21, 23, GREY)
    c.pts([(1, 3), (4, 2), (25, 2), (27, 4)], BROWN); c.pts([(13, 1), (14, 0)], GREEN)

@ic(BLUE, WHITE, 0.4)
def mod_ice(c):   # жирная лужа, на ней скользит ботинок
    c.ell(14, 20, 13, 6, (120, 200, 255), dither=(200, 240, 255)); c.ell(10, 19, 4, 1.5, WHITE)
    poly(c, [(7, 6), (16, 6), (19, 11), (21, 13), (21, 16), (8, 16)], BROWN, dither=DBROWN)
    c.rect(8, 15, 21, 16, BLACK); c.pts([(2, 9), (4, 9), (1, 12), (3, 12)], CYAN); c.pts([(24, 22), (26, 21)], YELLOW)

@ic(DBROWN, YELLOW, 0.5)
def mod_payday(c):   # мешок с говном и знаком денег, мухи
    c.ell(14, 17, 10, 9, (190, 150, 90), dither=(160, 120, 70)); c.rect(11, 5, 17, 9, (190, 150, 90)); c.rect(10, 8, 18, 9, RED)
    c.ell(14, 17, 4, 4.5, BROWN); c.rect(13, 11, 15, 23, YELLOW); c.rect(11, 13, 17, 14, YELLOW); c.rect(11, 20, 17, 21, YELLOW)
    for (x, y) in [(4, 4), (24, 6), (25, 25)]:
        c.px(x, y, BLACK); c.px(x - 1, y - 1, LG); c.px(x + 1, y - 1, LG)

def truck_frame(k):
    """Мусоровоз сбоку, едет вправо: кузов-контейнер, кабина с глазами, колёса крутятся (k = 0/1)."""
    c = Canvas(46, 26)
    c.rect(1, 3, 28, 18, GREEN, dither=DGREEN); c.rect(1, 3, 28, 4, LGREEN)
    for x in range(4, 27, 6): c.rect(x, 6, x + 1, 16, DGREEN)
    c.ell(10, 2, 4, 2, BROWN); c.ell(20, 1, 3, 2, (150, 90, 40)); c.pts([(14, 0), (8, 0)], GREEN)   # мусор торчит
    c.rect(29, 7, 43, 18, YELLOW, dither=ORANGE); c.rect(33, 9, 42, 13, (150, 220, 255), dither=CYAN)
    c.eye(36, 11, 1.5, (1, 0)); c.eye(40, 11, 2, (1, 0))
    c.rect(41, 15, 44, 18, BLACK); c.teeth(36, 44, 16, WHITE, BLACK, 2)
    for wx in (8, 22, 38):
        c.ell(wx, 21, 3.5, 3.5, BLACK); c.ell(wx, 21, 1.5, 1.5, GREY)
        c.px(wx + (1 if k else -1), 21 - 1, WHITE)
    c.pts([(0, 10), (0, 14)], BROWN)   # капает жижа
    return c.finish(DGREEN, YELLOW, lim=0.35)

def render(n):
    f, sh, hi, lim = I[n]; c = new(); f(c); return fin(c, sh, hi, lim)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    k = 5; prev = Image.new("RGBA", (len(I) * 34 * k, 34 * k + 170), (45, 30, 20, 255))
    for i, n in enumerate(I):
        a = render(n); im = Image.fromarray(a); sm = Image.fromarray(small(a))
        if apply: im.save("assets/ui/%s.png" % n); sm.save("assets/ui/%s_s.png" % n)
        b = im.resize((32 * k, 32 * k), Image.NEAREST); prev.paste(b, (i * 34 * k, 0), b)
    frames = [Image.fromarray(truck_frame(j)) for j in (0, 1)]
    w, h = frames[0].size; sheet = Image.new("RGBA", (w * 2, h))
    for j, fr in enumerate(frames): sheet.paste(fr, (j * w, 0))
    if apply: sheet.save("assets/sprites/garbage_truck.png")
    big = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST); prev.paste(big, (10, 34 * k + 6), big)
    prev.save("tools/_preview/wave_mods.png"); print("ok", sheet.size)
