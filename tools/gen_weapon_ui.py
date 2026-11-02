#!/usr/bin/env python3
"""Значки классов оружия (32×32 + _s 16×16) и рамка слота / полоска перезарядки для панели оружия в HUD.
python3 tools/gen_weapon_ui.py [--apply]   (превью: tools/_preview/weapon_ui.png)"""
import sys, random
sys.path.insert(0, "tools")
from icon_kit import *

I = {}
def ic(sh=PURPLE, hi=WHITE, lim=0.35):
    def d(f): I[f.__name__] = (f, sh, hi, lim); return f
    return d

@ic(DBROWN, YELLOW, 0.45)
def class_kitchen(c):   # сковородка с глазастой яичницей и жиром
    c.rect(19, 13, 27, 16, WOOD, dither=DBROWN)
    c.ell(11, 14, 10, 9, DGREY); c.ell(11, 14, 8.5, 7.5, (60, 60, 70), dither=(45, 45, 55))
    c.ell(10, 14, 6, 5, WHITE, dither=CREAM); c.ell(9, 13, 3, 3, YELLOW); c.eye(9, 13, 1.5, (1, 0), iris=BLACK, blood=True)
    c.pts([(15, 9), (4, 18), (16, 18), (13, 20)], (200, 180, 60)); c.pts([(6, 23), (6, 25), (14, 24), (14, 26)], (230, 210, 80))
    c.pts([(22, 11), (24, 10)], LG)

@ic(DGREY, CYAN, 0.45)
def class_household(c):   # вантуз и разводной ключ крест-накрест
    c.line(4, 24, 20, 6, WOOD, th=2); c.ell(21, 5, 5, 3.5, RED); c.rect(17, 5, 25, 7, DRED)
    c.line(6, 4, 22, 22, STEEL, th=2); c.ell(5, 4, 3.5, 3.5, STEEL); c.rect(4, 2, 6, 4, BLACK)
    c.ell(23, 23, 3, 3, STEEL); c.px(23, 23, BLACK); c.pts([(9, 17), (17, 13), (12, 9)], (120, 70, 30))
    c.pts([(25, 9), (26, 11), (24, 13)], (120, 230, 255))

@ic(DGREY, WHITE, 0.4)
def class_guns(c):   # самопал из трубы на изоленте, ствол дымит
    c.rect(3, 9, 23, 13, GREY, dither=DGREY); c.rect(3, 9, 23, 9, LG)
    poly(c, [(13, 13), (19, 13), (16, 25), (10, 25)], WOOD, dither=DBROWN)
    c.rect(8, 9, 10, 13, BLUE); c.rect(17, 9, 19, 13, BLUE); c.rect(12, 14, 13, 17, BLACK)
    c.ell(25, 11, 2, 2, ORANGE); c.px(26, 11, YELLOW); c.pts([(24, 6), (25, 4), (23, 2), (26, 1)], LG)

@ic(DRED, YELLOW, 0.5)
def class_fire(c):   # злой огонь с глазами разного размера
    poly(c, [(14, 1), (19, 8), (23, 5), (24, 15), (21, 25), (7, 25), (4, 15), (6, 7), (9, 11)], RED)
    poly(c, [(14, 7), (18, 13), (19, 21), (14, 25), (9, 21), (10, 13)], ORANGE)
    poly(c, [(14, 14), (17, 20), (14, 25), (11, 20)], YELLOW)
    c.eye(10, 15, 2.5, (1, 1)); c.eye(18, 14, 1.5, (-1, 1)); c.teeth(11, 17, 21, WHITE, BLACK, 2)

@ic(DGREEN, YELLOW, 0.45)
def class_stinky(c):   # вонючий носок в зелёном облаке с мухами
    for (x, y, r) in [(8, 9, 6), (17, 7, 6), (21, 15, 5), (6, 17, 5)]:
        c.ell(x, y, r, r * 0.8, GREEN, dither=DGREEN)
    poly(c, [(10, 6), (16, 6), (16, 17), (21, 19), (21, 24), (12, 24), (10, 20)], (225, 215, 170), dither=(190, 175, 120))
    c.rect(10, 6, 16, 8, RED); c.ell(18, 22, 2, 1.5, BROWN); c.ell(12, 14, 1.5, 2, BROWN)
    for (x, y) in [(3, 3), (24, 4), (25, 23)]:
        c.px(x, y, BLACK); c.px(x - 1, y - 1, (180, 180, 220)); c.px(x + 1, y - 1, (180, 180, 220))

@ic(PURPLE, PINK, 0.45)
def class_prison(c):   # решётка, сквозь неё пялится глаз, заточка
    c.rect(2, 2, 25, 25, (40, 35, 45), dither=(55, 45, 60))
    c.ell(14, 13, 9, 7, YELLOW, dither=(230, 210, 120)); c.ell(15, 13, 4, 4, PURPLE); c.ell(15, 13, 2, 2, BLACK); c.px(13, 11, WHITE)
    c.pts([(6, 10), (7, 15), (21, 9), (22, 16)], RED)
    for x in (4, 13, 22): c.rect(x, 1, x + 1, 26, STEEL)
    c.rect(2, 1, 25, 2, GREY); c.rect(2, 25, 25, 26, GREY)
    c.line(3, 25, 9, 17, LG, th=1); c.rect(1, 24, 4, 27, (60, 90, 200))

def render(n):
    f, sh, hi, lim = I[n]; c = new(); f(c); return fin(c, sh, hi, lim)

def slot_frame():
    """Рамка слота 20×20: светлая кривая (красится по тиру через modulate), внутри тёмная грязь."""
    rng = random.Random(7); im = Image.new("RGBA", (20, 20), (0, 0, 0, 0)); p = im.load()
    for y in range(20):
        for x in range(20):
            edge = min(x, y, 19 - x, 19 - y)
            if edge == 0 and (x, y) in [(0, 0), (19, 0), (0, 19), (19, 19)]: continue
            if edge <= 1: p[x, y] = (235, 235, 235, 255) if (edge == 1 or rng.random() > 0.15) else (150, 150, 150, 255)
            else:
                v = 22 + ((x + y) % 2) * 8 + rng.randint(0, 6); p[x, y] = (v, v - 6, v - 4, 235)
    for x, ln in [(4, 3), (11, 2), (16, 4)]:   # потёки с верхней кромки
        for k in range(ln): p[x, 2 + k] = (200, 200, 200, 255)
    for (x, y) in [(2, 17), (17, 2), (3, 2)]: p[x, y] = (120, 120, 120, 255)
    return im

def cd_bars():
    """Полоска перезарядки 18×3: подложка (чёрная с бурой грязью) и заливка-слизь (красится по тиру)."""
    under = Image.new("RGBA", (18, 3), (10, 8, 8, 255)); u = under.load()
    for x in range(0, 18, 3): u[x, 1] = (60, 35, 20, 255)
    fill = Image.new("RGBA", (18, 3), (0, 0, 0, 0)); f = fill.load()
    for x in range(18):
        f[x, 0] = (255, 255, 255, 255); f[x, 1] = (215, 215, 215, 255) if x % 2 else (240, 240, 240, 255)
        f[x, 2] = (170, 170, 170, 255) if x % 4 else (0, 0, 0, 0)
    return under, fill

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    k = 6; prev = Image.new("RGBA", (len(I) * 34 * k, 34 * k + 140), (45, 30, 20, 255))
    for i, n in enumerate(I):
        a = render(n); im = Image.fromarray(a, "RGBA"); sm = Image.fromarray(small(a), "RGBA")
        if apply: im.save("assets/ui/%s.png" % n); sm.save("assets/ui/%s_s.png" % n)
        b = im.resize((32 * k, 32 * k), Image.NEAREST); prev.paste(b, (i * 34 * k, 0), b)
        s2 = sm.resize((16 * 4, 16 * 4), Image.NEAREST); prev.paste(s2, (i * 34 * k + 60, 34 * k), s2)
    frame = slot_frame(); under, fill = cd_bars()
    if apply:
        frame.save("assets/ui/hud_weapon_slot.png"); under.save("assets/ui/hud_cd_under.png"); fill.save("assets/ui/hud_cd_fill.png")
    for j, tint in enumerate([(160, 160, 170), (60, 140, 255), (190, 60, 255), (255, 30, 60)]):
        fr = Image.new("RGBA", frame.size); fr.paste(frame); px_ = fr.load()
        for y in range(20):
            for x in range(20):
                r, g, b_, al = px_[x, y]; px_[x, y] = (r * tint[0] // 255, g * tint[1] // 255, b_ * tint[2] // 255, al)
        big = fr.resize((80, 80), Image.NEAREST); prev.paste(big, (40 + j * 100, 34 * k + 60 - 2), big)
    prev.save("tools/_preview/weapon_ui.png"); print("ok", prev.size)
