#!/usr/bin/env python3
"""Предметы, партия 3: проклятые (фиолетовая аура, тёмная гамма) и комбо (два предмета слились, золотые искры).
python3 tools/gen_items3.py --apply  -> assets/ui/item_<id>.png и _s.png; превью tools/_preview/items3.png"""
import sys
sys.path.insert(0, "tools")
from icon_kit import *
VIOL = (150, 40, 220); DVIOL = (70, 10, 110); GOLD = (255, 210, 40)
I = {}
def ic(sh=DVIOL, hi=VIOL, lim=0.45):
    def d(f): I[f.__name__] = (f, sh, hi, lim); return f
    return d

def aura(c):   # фиолетовые искры проклятия по углам
    for (x, y) in [(1, 2), (26, 1), (0, 25), (27, 26), (14, 0)]: c.px(x, y, VIOL)
def sparks(c):   # золотые искры комбо
    for (x, y) in [(2, 2), (25, 3), (3, 25), (24, 24)]:
        c.px(x, y, GOLD); c.px(x + 1, y, YELLOW); c.px(x, y + 1, YELLOW)

@ic()
def cursed_cigcase(c):
    c.rect(4, 6, 23, 22, (90, 90, 100), dither=DGREY); c.rect(4, 13, 23, 14, BLACK); c.ell(13, 18, 4, 3, WHITE); c.ell(12, 17, 1, 1, BLACK); c.ell(15, 17, 1, 1, BLACK)
    c.rect(7, 2, 9, 6, WHITE); c.rect(7, 1, 9, 1, ORANGE); c.pts([(8, 0), (10, 0)], LG); aura(c)
@ic()
def cursed_teeth(c):
    c.ell(14, 14, 11, 8, (150, 30, 60), dither=DRED); c.teeth(5, 23, 10, (255, 250, 200), BLACK, 4); c.teeth(6, 22, 17, (230, 220, 160), BLACK, 3)
    c.px(9, 11, GOLD); aura(c)
@ic()
def cursed_chain(c):
    for k in range(5):
        x = 3 + k * 5; y = 6 + (k % 2) * 4
        c.ell(x + 2, y + 2, 3, 2, GREY, dither=DGREY); c.ell(x + 2, y + 2, 1.5, 0.8, BLACK)
    c.rect(8, 16, 20, 25, (180, 220, 255), dither=CYAN); c.rect(12, 13, 16, 16, (180, 220, 255)); aura(c)
@ic()
def cursed_wallet(c):
    c.rect(3, 8, 24, 22, (60, 40, 30), dither=(40, 25, 20)); c.rect(3, 8, 24, 10, (90, 60, 40)); c.ell(13, 15, 4, 4, WHITE)
    c.rect(12, 18, 14, 22, WHITE); c.ell(11, 14, 1, 1, BLACK); c.ell(15, 14, 1, 1, BLACK); c.ell(22, 6, 2, 2, GOLD); aura(c)
@ic()
def cursed_voodoo(c):
    c.ell(14, 7, 5, 5, (190, 150, 90), dither=(160, 120, 70)); c.rect(10, 11, 18, 22, (190, 150, 90), dither=(160, 120, 70))
    c.rect(6, 13, 22, 15, (190, 150, 90)); c.rect(10, 22, 12, 26, (190, 150, 90)); c.rect(16, 22, 18, 26, (190, 150, 90))
    c.line(12, 5, 13, 6, BLACK); c.line(15, 5, 16, 6, BLACK); c.line(16, 8, 23, 3, LG); c.line(9, 17, 3, 22, LG); c.px(23, 3, RED); c.px(3, 22, RED); aura(c)
@ic()
def cursed_shawarma(c):
    poly(c, [(8, 3), (20, 3), (22, 24), (6, 24)], (230, 200, 140), dither=(200, 160, 100)); c.rect(9, 7, 19, 9, (120, 160, 40)); c.rect(9, 13, 19, 15, (150, 90, 60))
    c.eye(14, 19, 2.5, (0, 0)); c.pts([(4, 8), (24, 10), (5, 18)], GREEN); aura(c)
@ic()
def cursed_mirror(c):
    poly(c, [(6, 3), (20, 2), (24, 14), (13, 26), (4, 15)], (190, 230, 255), dither=(150, 200, 240)); c.line(9, 5, 18, 22, WHITE); c.line(18, 6, 8, 18, (120, 160, 200))
    c.eye(14, 13, 3, (1, 0), iris=VIOL); aura(c)
@ic()
def cursed_rat_crown(c):
    poly(c, [(3, 14), (6, 4), (10, 10), (14, 2), (18, 10), (22, 4), (25, 14)], GOLD); c.rect(3, 14, 25, 18, (200, 160, 20))
    c.ell(14, 23, 6, 4, GREY, dither=DGREY); c.px(11, 22, RED); c.px(17, 22, RED); c.ell(8, 21, 1.5, 1.5, PINK); c.ell(20, 21, 1.5, 1.5, PINK); aura(c)

@ic(DBROWN, GOLD, 0.5)
def combo_smoke(c):
    c.rect(2, 16, 17, 19, WHITE); c.rect(14, 16, 17, 19, ORANGE); c.rect(19, 12, 25, 23, RED); c.rect(20, 9, 24, 12, GREY)
    c.ell(22, 6, 2, 3, ORANGE); c.px(22, 5, YELLOW); c.ell(9, 9, 4, 3, LG, dither=GREY); c.ell(5, 5, 3, 2, LG); sparks(c)
@ic(DBROWN, GOLD, 0.5)
def combo_rotten_lunch(c):
    c.ell(10, 16, 8, 5, (210, 170, 100), dither=(180, 140, 70)); c.rect(3, 14, 17, 16, (120, 200, 60)); c.ell(10, 12, 7, 3, (220, 180, 110))
    c.rect(18, 6, 25, 22, (200, 220, 230), dither=WHITE); c.rect(18, 6, 25, 9, BLUE); c.pts([(12, 22), (14, 24), (7, 23)], GREEN); sparks(c)
@ic(DGREEN, GOLD, 0.5)
def combo_stink_set(c):
    poly(c, [(3, 6), (12, 6), (12, 20), (8, 24), (3, 22)], (225, 215, 170), dither=(190, 175, 120))
    c.rect(14, 6, 25, 20, (50, 90, 170), dither=(40, 70, 135)); c.ell(19, 14, 3, 3, BROWN)
    for (x, y) in [(6, 2), (18, 2), (13, 25)]: c.ell(x, y, 2, 1.5, GREEN); sparks(c)
@ic(DGREY, GOLD, 0.5)
def combo_double_head(c):
    c.ell(14, 18, 11, 7, YELLOW, dither=ORANGE); c.rect(3, 18, 25, 20, (200, 160, 20))
    c.ell(14, 9, 8, 5, GREY, dither=DGREY); c.rect(4, 8, 6, 10, DGREY); c.rect(22, 8, 24, 10, DGREY); c.rect(12, 3, 16, 4, BLACK); sparks(c)
@ic(DBROWN, GOLD, 0.6)
def combo_golden_poop(c):
    c.ell(14, 21, 10, 5, GOLD, dither=(220, 170, 20)); c.ell(14, 15, 7, 4, GOLD, dither=(220, 170, 20)); c.ell(14, 10, 4, 3, GOLD); c.ell(14, 6, 2, 2, YELLOW)
    c.px(10, 19, WHITE); c.px(12, 13, WHITE); c.rect(17, 17, 19, 19, WHITE); sparks(c)
@ic(BLUE, GOLD, 0.5)
def combo_russian_winter(c):
    c.ell(14, 10, 10, 7, (160, 130, 90), dither=BROWN); c.rect(3, 10, 8, 20, BROWN, dither=DBROWN); c.rect(20, 10, 25, 20, BROWN, dither=DBROWN)
    poly(c, [(11, 14), (17, 14), (18, 26), (10, 26)], (220, 245, 255), dither=WHITE); c.rect(12, 18, 16, 21, RED)
    for (x, y) in [(2, 3), (25, 2), (24, 24)]: c.px(x, y, WHITE); sparks(c)
@ic(DGREEN, GOLD, 0.5)
def combo_dacha_defense(c):
    c.rect(3, 8, 13, 20, GREY, dither=DGREY); c.rect(11, 11, 20, 13, DGREY); c.eye(8, 13, 2, (1, 0))
    c.ell(20, 22, 5, 3, (120, 90, 40)); c.ell(20, 21, 3, 1.5, RED); c.pts([(18, 18), (22, 18)], YELLOW); c.rect(1, 24, 26, 26, GREEN); sparks(c)
@ic(DBROWN, GOLD, 0.5)
def combo_friendship(c):
    c.ell(8, 16, 6, 6, (170, 120, 70), dither=BROWN); c.ell(6, 14, 1, 1, BLACK); c.ell(10, 14, 1, 1, BLACK); c.ell(8, 18, 2, 1, BLACK)
    c.ell(20, 17, 5, 4, GREY, dither=DGREY); c.px(18, 15, RED); c.px(22, 15, RED); c.ell(14, 9, 3, 2.5, RED); c.ell(12, 8, 1.5, 1.5, RED); c.ell(16, 8, 1.5, 1.5, RED); sparks(c)

def render(n):
    f, sh, hi, lim = I[n]; c = new(); f(c); return fin(c, sh, hi, lim)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    k = 4; cols = 8
    prev = Image.new("RGBA", (cols * 34 * k, 2 * (34 * k + 30)), (45, 30, 20, 255))
    for i, n in enumerate(I):
        a = render(n); im = Image.fromarray(a); sm = Image.fromarray(small(a))
        if apply: im.save("assets/ui/item_%s.png" % n); sm.save("assets/ui/item_%s_s.png" % n)
        x = (i % cols) * 34 * k; y = (i // cols) * (34 * k + 30)
        b = im.resize((32 * k, 32 * k), Image.NEAREST); prev.paste(b, (x, y), b)
        s2 = sm.resize((32, 32), Image.NEAREST); prev.paste(s2, (x + 40, y + 32 * k), s2)
    prev.save("tools/_preview/items3.png"); print("ok", len(I))
