#!/usr/bin/env python3
"""Опасность: черепа-уровни 16×16 для выбора (danger_0..5.png) и медали-отметки 8×8 на могилы (mark_0..5.png + mark_empty.png).
Медали: какашка, бронза, серебро, золото, платина с мухами, радужная корона из говна. python3 tools/gen_danger.py"""
from PIL import Image
K = (10, 10, 10, 255)
SK = [((200, 200, 190), (120, 110, 90)), ((150, 220, 90), (70, 140, 40)), ((240, 200, 60), (160, 110, 20)),
      ((255, 120, 40), (170, 50, 10)), ((255, 30, 60), (130, 0, 30)), ((200, 40, 255), (90, 0, 140))]
skull = ["....XXXXXX....", "...XAAAAAAX...", "..XAAAAAAAAX..", ".XAAAAAAAAAAX.", ".XAKKAAAAKKAX.", ".XAKKKAAKKKAX.",
         ".XAAAAKKAAAAX.", "..XAAAAAAAAX..", "...XAKAKAKX...", "...XAAAAAAX...", "....XXXXXX...."]
for lvl, (a, d) in enumerate(SK):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); p = im.load()
    for y, row in enumerate(skull):
        for x, ch in enumerate(row):
            if ch == "X": p[x + 1, y + 2] = K
            elif ch == "A": p[x + 1, y + 2] = (a if (x + y) % 3 else d) + (255,)
            elif ch == "K": p[x + 1, y + 2] = K
    for h in range(lvl):   # рога/шипы растут с уровнем
        x = 2 + h * 2 + (1 if h >= 3 else 0)
        p[min(x, 14), 1] = d + (255,); p[min(x, 14), 0 if h % 2 else 1] = a + (255,)
    im.save("assets/ui/danger_%d.png" % lvl)
MED = [((140, 80, 30), (100, 55, 20)), ((205, 127, 50), (140, 80, 30)), ((210, 215, 225), (130, 135, 150)),
       ((255, 215, 0), (190, 140, 0)), ((150, 240, 255), (60, 160, 200)), (None, None)]
poop = ["...XX...", "..XAAX..", ".XAAAAX.", ".XADAAX.", "XAAAADAX", "XAADAAAX", ".XXXXXX."]
RAIN = [(255, 0, 51), (255, 130, 0), (247, 255, 0), (57, 255, 20), (0, 240, 255), (255, 16, 240)]
for lvl, (a, d) in enumerate(MED):
    im = Image.new("RGBA", (8, 8), (0, 0, 0, 0)); p = im.load()
    for y, row in enumerate(poop):
        for x, ch in enumerate(row):
            if ch == "X": p[x, y + 1] = K
            elif ch in "AD":
                if a is None: p[x, y + 1] = RAIN[(x + y) % 6] + (255,)
                else: p[x, y + 1] = (d if ch == "D" else a) + (255,)
    if lvl == 4: p[0, 0] = K; p[7, 1] = K
    if lvl == 5: p[2, 0] = (247, 255, 0, 255); p[5, 0] = (247, 255, 0, 255); p[3, 0] = (255, 16, 240, 255)
    im.save("assets/ui/mark_%d.png" % lvl)
em = Image.new("RGBA", (8, 8), (0, 0, 0, 0)); q = em.load()
for y, row in enumerate(poop):
    for x, ch in enumerate(row):
        if ch != ".": q[x, y + 1] = (45, 40, 50, 255) if ch == "X" else (28, 25, 32, 200)
em.save("assets/ui/mark_empty.png")
prev = Image.new("RGBA", (6 * 40, 80), (50, 35, 25, 255))
for i in range(6):
    s = Image.open("assets/ui/danger_%d.png" % i).resize((32, 32), Image.NEAREST); prev.paste(s, (i * 40 + 4, 4), s)
    m = Image.open("assets/ui/mark_%d.png" % i).resize((24, 24), Image.NEAREST); prev.paste(m, (i * 40 + 8, 44), m)
prev.save("tools/_preview/danger.png"); print("ok")
