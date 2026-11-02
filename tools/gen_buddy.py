#!/usr/bin/env python3
"""Н16: пёс-спутник (дворняга с помойки) + его шмотки поверх (те же 6 кадров: 4 бег, 2 сидит) + кость.
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_buddy.py
-> assets/sprites/buddy_dog.png, buddy_wear_<id>.png, bone.png, assets/ui/kennel.png; превью tools/_preview/buddy.png"""
import numpy as np
from PIL import Image
from pix import *

FW, FH = 26, 20
FUR = (190, 140, 80); FUR2 = (150, 100, 55); PATCH = (90, 60, 35); TONGUE = (255, 110, 140)
WEAR = ["collar", "bandana", "cap", "cloak", "glasses", "bow"]


def pose(t):
    """Параметры кадра: b - подпрыгивание, run - бег (0-3) или сидит (4-5)."""
    if t < 4:
        return {"b": [0, 1, 0, 1][t], "leg": [-2, 0, 2, 0][t], "sit": False, "tail": [0, 1, 0, -1][t]}
    return {"b": 0, "leg": 0, "sit": True, "tail": [1, -1][t - 4]}


def dog(t):
    c = Canvas(FW, FH); p = pose(t); b = p["b"]
    hx, hy = 19, 7 - b                                            # голова
    if p["sit"]:
        c.ell(11, 12, 7, 5, FUR, dither=FUR2); c.rect(14, 13, 16, 18, FUR); c.rect(6, 15, 9, 18, FUR2)
    else:
        c.ell(11, 11 - b, 8, 4, FUR, dither=FUR2)
        for x, d in ((5, p["leg"]), (8, -p["leg"]), (14, -p["leg"]), (17, p["leg"])):
            c.line(x, 13 - b, x + d, 18, FUR2, 2)
    c.ell(9, 10 - b, 3, 2, PATCH)                                 # пятно на боку
    c.line(3, 9 - b, 0, 5 - b + p["tail"], FUR2, 2)               # хвост
    c.ell(hx, hy, 5, 4, FUR); c.ell(hx + 4, hy + 2, 3, 2, FUR2)    # морда
    c.px(hx + 7, hy + 1, BLACK)                                   # нос
    c.line(hx - 3, hy - 3, hx - 4, hy - 7, FUR2, 2)               # ухо торчком
    c.line(hx + 1, hy - 3, hx + 3, hy, PATCH, 2)                  # ухо висит
    c.eye(hx + 1, hy - 1, 1, (1, 0), blood=False)
    if t % 2 == 0 and not p["sit"]: c.rect(hx + 4, hy + 4, hx + 5, hy + 5, TONGUE)   # язык на бегу
    return c


def wear(kind, t):
    c = Canvas(FW, FH); p = pose(t); b = p["b"]; hx, hy = 19, 7 - b
    if kind == "collar":
        c.line(hx - 4, hy + 2, hx - 1, hy + 4, RED, 2); c.pts([(hx - 3, hy + 5), (hx - 1, hy + 6)], WHITE)
    elif kind == "bandana":
        c.line(hx - 5, hy + 3, hx, hy + 5, BLUE, 2); c.pts([(hx - 4, hy + 6), (hx - 3, hy + 7)], BLUE); c.px(hx - 2, hy + 4, WHITE)
    elif kind == "cap":
        c.rect(hx - 3, hy - 5, hx + 2, hy - 3, RED); c.rect(hx - 6, hy - 3, hx - 3, hy - 3, RED)   # козырьком назад
    elif kind == "cloak":
        top = 7 - b
        c.line(hx - 4, hy + 2, 4, top + (2 if p["sit"] else 0), PURPLE, 3)
        c.pts([(3, top + 3), (2, top + 5), (5, top + 4)], PURPLE)
    elif kind == "glasses":
        c.rect(hx - 1, hy - 2, hx + 4, hy - 1, BLACK); c.px(hx + 1, hy - 2, (60, 60, 200))
    elif kind == "bow":
        c.pts([(hx - 4, hy - 7), (hx - 6, hy - 8), (hx - 6, hy - 6), (hx - 2, hy - 8), (hx - 2, hy - 6), (hx - 4, hy - 6)], PINK)
    return c


def to_sheet(canvases, outline=True):
    frames = [cv.finish(BLACK, WHITE) if outline else cv.a for cv in canvases]
    return sheet(frames)


def bone():
    c = Canvas(12, 7)
    c.rect(3, 2, 8, 4, (240, 235, 215)); c.ell(2, 2, 2, 1, (240, 235, 215)); c.ell(2, 4, 2, 1, (240, 235, 215))
    c.ell(9, 2, 2, 1, (240, 235, 215)); c.ell(9, 4, 2, 1, (240, 235, 215))
    return c.finish(BROWN, WHITE)


def kennel():
    """Будка для экрана пса: 64x48, на крыше табличка под кличку."""
    c = Canvas(64, 48)
    c.poly = None
    c.rect(8, 18, 56, 46, (150, 90, 45), dither=(120, 70, 35))
    for y in range(20, 46, 5): c.line(8, y, 56, y, (100, 60, 30))
    for k in range(0, 26):                                           # крыша
        c.line(32 - k, 4 + k // 1 * 0 + k * 0 + (k * 14) // 26, 32 + k, 4 + (k * 14) // 26, (170, 40, 40))
    c.rect(22, 28, 42, 46, (30, 20, 15))                             # вход
    c.rect(18, 12, 46, 18, (220, 210, 170))                          # табличка
    c.pts([(6, 46), (58, 46), (40, 44)], GREEN)
    return c.finish(BROWN, WHITE)


if __name__ == "__main__":
    to_sheet([dog(t) for t in range(6)]).save("assets/sprites/buddy_dog.png")
    for k in WEAR:
        to_sheet([wear(k, t) for t in range(6)], outline=False).save(f"assets/sprites/buddy_wear_{k}.png")
    Image.fromarray(bone()).save("assets/sprites/bone.png")
    Image.fromarray(kennel()).save("assets/ui/kennel.png")
    base = Image.open("assets/sprites/buddy_dog.png")
    rows = [base] + [Image.alpha_composite(base, Image.open(f"assets/sprites/buddy_wear_{k}.png").resize(base.size)) for k in WEAR]
    prev = Image.new("RGBA", (base.width + 80, base.height * len(rows)), (60, 40, 30, 255))
    for i, r in enumerate(rows): prev.paste(r, (0, i * base.height), r)
    k = Image.open("assets/ui/kennel.png"); prev.paste(k, (base.width + 8, 4), k)
    b = Image.open("assets/sprites/bone.png"); prev.paste(b, (base.width + 20, 60), b)
    prev.resize((prev.width * 4, prev.height * 4), Image.NEAREST).save("tools/_preview/buddy.png"); print(prev.size)
