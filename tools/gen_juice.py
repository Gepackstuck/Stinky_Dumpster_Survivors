#!/usr/bin/env python3
"""Сочность: вспышка у дула (3 кадра 12×12), гильза 4×2, пятна на полу после смерти врага (4 вида 18×12), муха (2 кадра 5×4).
python3 tools/gen_juice.py -> assets/sprites/fx_*.png; превью tools/_preview/juice.png"""
import random
from PIL import Image
Y = (247, 255, 0, 255); O = (255, 130, 0, 255); W = (255, 255, 230, 255); R = (255, 0, 51, 255)
rng = random.Random(3)
# вспышка: звезда, кадры от большой к маленькой
flash = Image.new("RGBA", (36, 12), (0, 0, 0, 0)); p = flash.load()
for f, r in enumerate((5, 4, 2)):
    cx, cy = f * 12 + 6, 6
    for k in range(-r, r + 1):
        for (dx, dy) in ((k, 0), (0, k), (k // 2, k // 2), (k // 2, -k // 2)):
            x, y = cx + dx, cy + dy
            if 0 <= x - f * 12 < 12 and 0 <= y < 12:
                d = abs(dx) + abs(dy)
                p[x, y] = W if d <= 1 else (Y if d <= r - 1 else O)
flash.save("assets/sprites/fx_muzzle.png")
casing = Image.new("RGBA", (4, 2), (0, 0, 0, 0)); c = casing.load()
for x in range(4): c[x, 0] = (230, 190, 60, 255); c[x, 1] = (170, 120, 30, 255)
c[3, 0] = (120, 80, 20, 255); casing.save("assets/sprites/fx_casing.png")
# пятна: кровь, кишки, говно, слизь (на полу медленно тают)
cols = [((160, 0, 30), (110, 0, 20)), ((200, 60, 110), (150, 30, 70)), ((107, 62, 31), (80, 45, 20)), ((120, 200, 40), (80, 150, 20))]
splat = Image.new("RGBA", (18 * 4, 12), (0, 0, 0, 0)); s = splat.load()
for v, (a, d) in enumerate(cols):
    for _ in range(5):
        cx, cy, rx, ry = rng.randint(4, 13), rng.randint(3, 8), rng.uniform(2, 5), rng.uniform(1.5, 3)
        for y in range(12):
            for x in range(18):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    s[v * 18 + x, y] = (a if (x + y) % 3 else d) + (220,)
    for _ in range(6):   # брызги
        x, y = rng.randint(0, 17), rng.randint(0, 11); s[v * 18 + x, y] = d + (220,)
    if v == 1:   # кишка-червяк
        for k in range(8): s[v * 18 + 4 + k, 6 + (k % 3) - 1] = (255, 120, 170, 230)
splat.save("assets/sprites/fx_splat.png")
fly = Image.new("RGBA", (10, 4), (0, 0, 0, 0)); fl = fly.load()
for f in range(2):
    fl[f * 5 + 2, 2] = (10, 10, 10, 255); fl[f * 5 + 2, 3] = (40, 40, 40, 255)
    wing = (200, 200, 230, 200)
    if f == 0: fl[f * 5 + 1, 1] = wing; fl[f * 5 + 3, 1] = wing
    else: fl[f * 5 + 1, 2] = wing; fl[f * 5 + 3, 2] = wing
fly.save("assets/sprites/fx_fly.png")
prev = Image.new("RGBA", (200, 60), (60, 40, 25, 255))
for i, im in enumerate([flash, casing, splat, fly]):
    b = im.resize((im.width * 3, im.height * 3), Image.NEAREST); prev.paste(b, (2, 2 + i * 14 if i < 3 else 46), b) if False else None
x = 2
for im in [flash, casing, splat, fly]:
    b = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    if x + b.width > 200: x = 2
    prev.paste(b, (x, 4 if im is flash else (30 if im is splat else 46)), b); x += b.width + 4
prev.save("tools/_preview/juice.png"); print("ok")
