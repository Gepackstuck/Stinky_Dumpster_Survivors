#!/usr/bin/env python3
"""Куча-лотерея и рулетка модификаторов: светящаяся куча говна 48×40 (4 кадра лучей), стрелка-вонь 30×20 (4 кадра),
покрышка-колесо 120×120 (обод; сегменты рисует игра), подставка-бак 64×40, гвоздь-указатель 12×20.
python3 tools/gen_roulette.py -> assets/sprites/mod_pile.png, assets/ui/pile_pointer.png, roulette_*.png"""
import sys, math
sys.path.insert(0, "tools")
from pix import *
from PIL import Image
import numpy as np
BR = (107, 62, 31); BR2 = (140, 85, 40); BR3 = (80, 45, 20); GOLD = (255, 220, 60)

def pile(frame):
    c = Canvas(44, 36)
    cx, by = 22, 30
    for k in range(8):   # лучи - вращаются по кадрам
        a = math.radians(k * 45 + frame * 11)
        for r in range(14, 21):
            x, y = cx + math.cos(a) * r, 18 + math.sin(a) * r * 0.75
            if 0 <= x < 44 and 0 <= y < 36 and (r + frame) % 3 != 0: c.px(int(x), int(y), YELLOW if k % 2 else GOLD)
    c.ell(cx, by - 2, 15, 6, BR, dither=BR3); c.ell(cx, by - 9, 11, 5, BR2, dither=BR); c.ell(cx, by - 15, 7, 4, BR, dither=BR2); c.ell(cx, by - 19, 3, 2.5, BR2)
    c.ell(cx - 1, by - 23, 1.5, 1.5, BR); c.px(cx - 5, by - 10, WHITE); c.px(cx + 3, by - 16, WHITE)
    c.eye(cx - 4, by - 6, 2, (1, 0)); c.eye(cx + 5, by - 7, 1.5, (-1, 0))
    for k, (x, y) in enumerate([(6, 8), (36, 6), (40, 22), (4, 24)]):   # мухи
        fx = x + (1 if (frame + k) % 2 else -1)
        c.px(fx, y, BLACK); c.px(fx - 1, y - 1, (200, 200, 230)); c.px(fx + 1, y - 1, (200, 200, 230))
    for k in range(3):   # вонь вверх
        x = cx - 6 + k * 6; y0 = 6 - (frame + k) % 4
        c.px(x, y0, GREEN); c.px(x + 1, y0 - 1, GREEN); c.px(x, y0 - 2, (120, 255, 80))
    return c.finish(BR3, YELLOW, lim=0.2)

def pointer(frame):
    c = Canvas(28, 18)
    for x in range(2, 20):   # волнистое древко-вонь
        y = 9 + int(round(2 * math.sin((x + frame * 2) * 0.7)))
        c.px(x, y, GREEN); c.px(x, y + 1, (40, 180, 20))
    c.ell(23, 9, 4, 4, BR, dither=BR2); c.ell(23, 7, 2.5, 2, BR2); c.px(22, 8, WHITE)
    for (x, y) in [(6, 4), (12, 14), (16, 3)]: c.px(x + frame % 2, y, (120, 255, 80))
    return c.finish(BR3, YELLOW, lim=0.2)

def tire():
    n = 120; im = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - 59.5, y - 59.5)
            if 50 <= d <= 59:   # резина с протектором
                tread = (int(math.degrees(math.atan2(y - 59.5, x - 59.5)) // 9) % 2)
                v = 28 + tread * 18 + (6 if d > 56 else 0)
                im[y, x] = (v, v, v + 4, 255)
            elif 47 <= d < 50:   # ржавый обод
                im[y, x] = (170, 90, 40, 255) if (x + y) % 3 else (120, 60, 25, 255)
            elif d < 6:   # ступица с болтом
                im[y, x] = (180, 180, 190, 255) if d < 4 else (60, 60, 70, 255)
    for k in range(12):   # гвозди в покрышке
        a = math.radians(k * 30 + 7); x = int(59.5 + math.cos(a) * 54); y = int(59.5 + math.sin(a) * 54)
        im[y, x] = (230, 230, 240, 255)
    return Image.fromarray(im)

def stand():
    c = Canvas(64, 40)
    c.rect(18, 4, 46, 38, GREEN, dither=DGREEN); c.rect(16, 2, 48, 6, (40, 160, 40))
    for x in range(22, 44, 6): c.rect(x, 9, x + 1, 34, DGREEN)
    c.ell(26, 20, 3, 2, (170, 90, 40)); c.ell(38, 28, 2, 2, (170, 90, 40)); c.pts([(30, 0), (34, 1)], BR)
    return c.finish(DGREEN, YELLOW, lim=0.2)

def nail():
    c = Canvas(10, 18)
    c.rect(1, 0, 8, 2, GREY); c.rect(4, 3, 5, 14, (190, 190, 200)); c.px(4, 15, (190, 190, 200)); c.px(4, 16, WHITE)
    c.pts([(5, 6), (5, 10)], (170, 90, 40))
    return c.finish(DGREY, WHITE, lim=0.1)

def sheet(frames):
    ims = [Image.fromarray(f) for f in frames]; w, h = ims[0].size
    out = Image.new("RGBA", (w * len(ims), h))
    for i, im in enumerate(ims): out.paste(im, (i * w, 0))
    return out

if __name__ == "__main__":
    sheet([pile(i) for i in range(4)]).save("assets/sprites/mod_pile.png")
    sheet([pointer(i) for i in range(4)]).save("assets/ui/pile_pointer.png")
    tire().save("assets/ui/roulette_tire.png"); Image.fromarray(stand()).save("assets/ui/roulette_stand.png"); Image.fromarray(nail()).save("assets/ui/roulette_nail.png")
    prev = Image.new("RGBA", (420, 300), (45, 30, 20, 255))
    p = Image.open("assets/sprites/mod_pile.png"); p2 = p.resize((p.width * 2, p.height * 2), Image.NEAREST); prev.paste(p2, (4, 4), p2)
    q = Image.open("assets/ui/pile_pointer.png"); q2 = q.resize((q.width * 2, q.height * 2), Image.NEAREST); prev.paste(q2, (4, 90), q2)
    t = Image.open("assets/ui/roulette_tire.png"); prev.paste(t, (4, 140), t)
    s = Image.open("assets/ui/roulette_stand.png"); prev.paste(s, (140, 220), s)
    n = Image.open("assets/ui/roulette_nail.png"); n2 = n.resize((20, 36), Image.NEAREST); prev.paste(n2, (220, 140), n2)
    prev.save("tools/_preview/roulette_art.png"); print("ok")
