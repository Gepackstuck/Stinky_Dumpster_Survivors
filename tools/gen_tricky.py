#!/usr/bin/env python3
"""Хитрые враги (идея 5): глючный бомж-телепорт, трюмо-мутант (отражает), гопник с крышкой (щит).
Запуск из корня: PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_tricky.py
Листы по 4 кадра -> assets/sprites/enemy_<id>.png, эффекты -> assets/sprites/fx_*.png, превью -> tools/_preview/tricky.png."""
import math, os
from PIL import Image
from pix import *

LGREY = (190, 190, 200); GLASS = (170, 230, 255); TRACK = (40, 60, 200); SLIME = (150, 255, 60)


def blinker(t):
    """Глючный бомж: мерцает полосами, полтела «съехало», капает фиолетовая слизь."""
    c = Canvas(30, 34)
    b = [0, 1, 0, 1][t]; sh = [0, 2, -1, 3][t]
    c.rect(9, 28, 12, 33, BROWN); c.rect(17, 28, 20, 33, BROWN); c.pts([(8, 33), (21, 33)], BLACK)
    c.ell(15, 20 + b, 9, 10, PURPLE, dither=PINK)                      # балахон
    c.rect(6, 16 + b, 24, 17 + b, BLACK) if t == 2 else None
    for y in (14, 19, 24):                                              # глитч-полосы со сдвигом
        c.rect(5 + sh, y + b, 25 + sh, y + b, CYAN if (y + t) % 2 else PINK)
    c.ell(15, 9 + b, 7, 7, SKIN, dither=(200, 150, 255))
    c.rect(8, 2 + b, 22, 5 + b, PURPLE); c.rect(10, 0 + b, 20, 2 + b, PURPLE)   # капюшон
    c.eye(12, 9 + b, 3, (1, 0)); c.eye(19, 10 + b, 1, (0, 0), blood=False)
    c.rect(11, 14 + b, 19, 15 + b, BLACK); c.pts([(12, 14 + b), (14, 15 + b), (17, 14 + b)], YELLOW)
    c.line(5, 18 + b, 1, 22 - b, SKIN, 2); c.line(25, 18 + b, 29, 15 + b, SKIN, 2)
    c.rect(26, 11 + b, 29, 15 + b, GREEN); c.px(27, 10 + b, WHITE)          # бутылка «телепортина»
    for k, x in enumerate((9, 15, 21)):                                  # слизь капает
        yy = 29 + (t + k) % 4
        c.pts([(x, yy), (x, yy + 1)], PINK)
    if t % 2:
        c.pts([(2 + sh, 6), (27 - sh, 4), (3, 28), (26, 26)], CYAN)       # искры глюка
    return c.finish(PINK, CYAN, lim=0.1)


def mirror(t):
    """Трюмо-мутант: треснутое зеркало на щупальцах, внутри отражается злая рожа."""
    c = Canvas(30, 38)
    w = [0, 1, 0, -1][t]
    for i, x in enumerate((8, 15, 22)):                                   # щупальца-ножки
        d = w if i % 2 == 0 else -w
        c.line(x, 30, x + d, 34, PINK, 2); c.line(x + d, 34, x + d * 2 + 1, 37, PINK, 2)
    c.rect(4, 2, 26, 31, BROWN, dither=(150, 90, 40))                     # рама
    c.rect(4, 2, 26, 3, (200, 140, 60)); c.pts([(4, 2), (26, 2), (4, 31), (26, 31)], GOLD if 'GOLD' in globals() else YELLOW)
    c.rect(7, 5, 23, 28, GLASS, dither=WHITE)                            # стекло
    sh = t % 4
    c.line(8 + sh * 3, 5, 7 + sh * 3, 9, WHITE, 2)                        # блик бегает
    c.line(12, 5, 16, 14, DGREY); c.line(16, 14, 22, 12, DGREY); c.line(16, 14, 14, 22, DGREY)   # трещины
    c.eye(11, 15, 2, (1, 0)); c.eye(19, 17, 3, (-1, 0))                  # отражение-рожа
    c.rect(10, 22, 20, 23, RED); c.pts([(11, 22), (13, 23), (15, 22), (17, 23), (19, 22)], WHITE)
    c.line(4, 14, 0, 18 + w, PINK, 2); c.line(26, 14, 30, 10 - w, PINK, 2)   # щупальца-руки
    c.pts([(0, 19 + w), (30, 9 - w)], RED)
    return c.finish(CYAN, WHITE, lim=0.05)


def shield_bearer(t):
    """Гопник в трениках: корпус без щита (крышка - отдельный спрайт, крутится к игроку)."""
    c = Canvas(26, 34)
    lg = [-1, 0, 1, 0][t]; b = [0, 1, 0, 1][t]
    c.rect(8 + lg, 24, 11 + lg, 32, TRACK); c.rect(15 - lg, 24, 18 - lg, 32, TRACK)
    c.line(9 + lg, 24, 9 + lg, 32, WHITE); c.line(16 - lg, 24, 16 - lg, 32, WHITE)   # лампасы
    c.rect(6 + lg, 32, 12 + lg, 33, BLACK); c.rect(14 - lg, 32, 20 - lg, 33, BLACK)
    c.rect(6, 13 + b, 20, 25, TRACK, dither=BLUE); c.line(13, 13 + b, 13, 25, LGREY)
    c.line(7, 13 + b, 7, 25, WHITE); c.line(19, 13 + b, 19, 25, WHITE)
    c.ell(13, 7 + b, 6, 6, SKIN); c.rect(8, 1 + b, 18, 3 + b, BLACK); c.rect(17, 3 + b, 21, 4 + b, BLACK)   # кепка
    c.eye(11, 7 + b, 1, (1, 0), blood=False); c.eye(15, 8 + b, 2, (1, 0))
    c.rect(10, 11 + b, 16, 11 + b, (90, 30, 30)); c.px(16, 10 + b, WHITE)    # ухмылка, фикса
    c.line(5, 15 + b, 2, 21, TRACK, 3); c.line(21, 15 + b, 24, 20, TRACK, 3)
    c.pts([(2, 22), (24, 21)], SKIN)
    c.pts([(14, 18 + b), (15, 19 + b), (16, 18 + b)], YELLOW)               # семки
    return c.finish(BLUE, WHITE, lim=0.05)


def thief(t):
    """Н21: щипач в капюшоне с огромным мешком краденого говна, крадётся на цыпочках."""
    c = Canvas(30, 32)
    lg = [-1, 1, -1, 1][t]; b = [0, 1, 0, 1][t]
    c.line(11, 24, 10 + lg, 31, BLACK, 2); c.line(17, 24, 18 - lg, 31, BLACK, 2)
    c.ell(14, 18 + b, 6, 7, (60, 60, 70), dither=DGREY)                 # худи
    c.ell(14, 9 + b, 5, 5, (60, 60, 70)); c.ell(15, 10 + b, 3, 3, SKIN)  # капюшон, лицо
    c.eye(14, 10 + b, 1, (1, 0), blood=False); c.eye(17, 10 + b, 1, (1, 0), blood=False)
    c.line(14, 13 + b, 17, 12 + b, BLACK)                                # ухмылка
    c.ell(5, 13 + b, 6, 7, BROWN, dither=(130, 90, 40))                  # мешок за спиной
    c.rect(3, 5 + b, 7, 7 + b, BROWN); c.pts([(4, 13 + b), (5, 12 + b), (6, 13 + b)], YELLOW)   # «$»
    c.line(9, 15 + b, 4, 8 + b, (60, 60, 70), 2)                          # рука держит мешок
    c.line(19, 16 + b, 24, 14 - b, (60, 60, 70), 2); c.px(25, 13 - b, SKIN)   # тянет лапу к добру
    if t % 2: c.pts([(26, 9), (27, 11)], GREEN)                          # капля слизи-опыта в руке
    return c.finish(PURPLE, WHITE, lim=0.05)


def lid():
    """Крышка от мусорного бака: щит, выпуклая сторона вправо (к игроку)."""
    c = Canvas(10, 22)
    c.ell(4, 11, 4, 10, GREY, dither=DGREY)
    c.ell(5, 11, 3, 8, LGREY)
    for y in (5, 11, 17): c.line(3, y, 7, y, DGREY)
    c.rect(1, 9, 2, 13, DGREY)                                            # ручка с изнанки
    c.pts([(6, 6), (5, 14), (7, 16)], (170, 80, 30))                       # ржавчина
    c.pts([(7, 3), (7, 19)], SLIME)                                       # налипшая слизь
    return c.finish(DGREY, WHITE)


def blink_mark(t):
    """Метка, куда прыгнет глючный бомж: фиолетовая воронка."""
    c = Canvas(20, 12)
    r = [9, 7, 5, 8][t]
    c.ell(10, 6, r, max(r // 2, 2), PURPLE, dither=PINK)
    c.ell(10, 6, max(r - 3, 1), max(r // 2 - 2, 1), BLACK)
    for k in range(4):
        a = math.radians(t * 45 + k * 90)
        c.px(int(10 + 9 * math.cos(a)), int(6 + 5 * math.sin(a)), CYAN)
    return c.finish(PINK, CYAN, outline=False)


def mirror_glow(t):
    """Блеск активного зеркала: лучи вокруг."""
    c = Canvas(40, 44)
    for k in range(8):
        a = math.radians(k * 45 + t * 11)
        r0, r1 = 15, 19 + (k + t) % 3
        c.line(int(20 + r0 * math.cos(a)), int(22 + r0 * math.sin(a)), int(20 + r1 * math.cos(a)), int(22 + r1 * math.sin(a)), WHITE if k % 2 else CYAN)
    return c.finish(CYAN, WHITE, outline=False)


def glass(t):
    """Отражённый осколок зеркала."""
    c = Canvas(8, 8)
    pts = [(1, 4), (4, 1), (7, 3), (5, 7)] if t % 2 == 0 else [(1, 2), (6, 1), (6, 6), (2, 7)]
    for i in range(4):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % 4]; c.line(x0, y0, x1, y1, CYAN)
    c.rect(3, 3, 4, 4, WHITE)
    return c.finish(CYAN, WHITE)


if __name__ == "__main__":
    out = {}
    out["proj_glass"] = Image.fromarray(glass(0))
    for name, fn in (("blinker", blinker), ("mirror", mirror), ("shield_bearer", shield_bearer), ("thief", thief)):
        out[f"enemy_{name}"] = sheet([fn(t) for t in range(4)])
    out["fx_blink_mark"] = sheet([blink_mark(t) for t in range(4)])
    out["fx_mirror_glow"] = sheet([mirror_glow(t) for t in range(4)])
    out["fx_shield_lid"] = Image.fromarray(lid(), "RGBA")
    for k, im in out.items():
        im.save(f"assets/sprites/{k}.png")
    k = 4; pad = 8
    W = max(im.width for im in out.values()) * k + pad * 2; H = sum(im.height * k + pad for im in out.values()) + pad
    prev = Image.new("RGBA", (W, H), (45, 30, 20, 255)); y = pad
    for im in out.values():
        big = im.resize((im.width * k, im.height * k), Image.NEAREST); prev.paste(big, (pad, y), big); y += big.height + pad
    os.makedirs("tools/_preview", exist_ok=True); prev.save("tools/_preview/tricky.png"); print(prev.size)
