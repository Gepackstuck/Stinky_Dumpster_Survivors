#!/usr/bin/env python3
"""Телеграфы атак: полосатая заливка (тайл 8×8, повторяется) и череп в точке удара 9×9.
python3 tools/gen_telegraph.py  -> assets/sprites/tele_stripe.png, tele_skull.png; превью tools/_preview/telegraph.png"""
from PIL import Image
RED = (255, 0, 51, 255); DRED = (150, 0, 30, 255); YEL = (247, 255, 0, 255); BLK = (10, 10, 10, 0)

stripe = Image.new("RGBA", (8, 8), (0, 0, 0, 0)); p = stripe.load()
for y in range(8):
    for x in range(8):
        band = ((x + y) // 2) % 2   # диагональные полосы шириной 2
        if band == 0:
            p[x, y] = RED if (x * 3 + y) % 5 else DRED
        else:
            p[x, y] = (255, 0, 51, 90) if (x + y) % 2 else (0, 0, 0, 0)   # дизеринг между полосами
skull_rows = [
    "..XXXXX..",
    ".XYYYYYX.",
    "XYYYYYYYX",
    "XY.YYY.YX",
    "XY..Y..YX",
    "XYYY.YYYX",
    ".XYYYYYX.",
    "..XY.YX..",
    "..XXXXX..",
]
skull = Image.new("RGBA", (9, 9), (0, 0, 0, 0)); q = skull.load()
for y, row in enumerate(skull_rows):
    for x, ch in enumerate(row):
        if ch == "X": q[x, y] = (10, 10, 10, 255)
        elif ch == "Y": q[x, y] = YEL
        elif ch == "." and 0 < x < 8 and 2 < y < 8 and row[x - 1] != "." : q[x, y] = (10, 10, 10, 255)
stripe.save("assets/sprites/tele_stripe.png"); skull.save("assets/sprites/tele_skull.png")
prev = Image.new("RGBA", (200, 90), (60, 40, 25, 255))
big = stripe.resize((32, 32), Image.NEAREST)
for i in range(5): prev.paste(big, (4 + i * 32, 4), big)
sk = skull.resize((54, 54), Image.NEAREST); prev.paste(sk, (60, 34), sk)
prev.save("tools/_preview/telegraph.png"); print("ok")
