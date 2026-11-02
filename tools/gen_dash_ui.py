#!/usr/bin/env python3
"""Значок рывка для HUD: кеда с полосами скорости 14×12 (заряжено) и тёмный силуэт (перезарядка).
python3 tools/gen_dash_ui.py -> assets/ui/hud_dash_full.png, hud_dash_empty.png; превью tools/_preview/dash_ui.png"""
from PIL import Image
K = (10, 10, 10, 255); W = (240, 240, 240, 255); G = (57, 255, 20, 255); P = (255, 16, 240, 255); Y = (247, 255, 0, 255); R = (255, 0, 51, 255); B = (107, 62, 31, 255)
rows = [
    "..............",
    "........KKK...",
    ".......KWWWK..",
    "GG....KWPWWK..",
    "......KWWPWK..",
    ".GGG.KWWWWWKK.",
    ".....KWWWWWWWK",
    "GG..KWRWWWWWWK",
    "...KWWRRWWWBWK",
    "..KKKKKKKKKKKK",
    "..KYKYKYKYKYK.",
    "...KKKKKKKKK..",
]
cmap = {"K": K, "W": W, "G": G, "P": P, "Y": Y, "R": R, "B": B}
full = Image.new("RGBA", (14, 12), (0, 0, 0, 0)); f = full.load()
empty = Image.new("RGBA", (14, 12), (0, 0, 0, 0)); e = empty.load()
for y, row in enumerate(rows):
    for x, ch in enumerate(row):
        if ch in cmap:
            f[x, y] = cmap[ch]
            if ch != "G":
                e[x, y] = K if ch == "K" else ((55, 50, 60, 255) if (x + y) % 2 else (40, 36, 45, 255))
full.save("assets/ui/hud_dash_full.png"); empty.save("assets/ui/hud_dash_empty.png")
prev = Image.new("RGBA", (130, 60), (60, 40, 25, 255))
for i, im in enumerate([full, empty]):
    b = im.resize((56, 48), Image.NEAREST); prev.paste(b, (4 + i * 64, 6), b)
prev.save("tools/_preview/dash_ui.png"); print("ok")
