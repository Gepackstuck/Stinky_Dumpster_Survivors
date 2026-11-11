"""Интерфейс новой пиксельной рисовки: ржавое грязное железо, заклёпки, трещины, потёки крови, кости. Размеры и раскладка листов те же,
что у классики (подмена один в один): рамки карточек 112x150 (лист 8x2), панели 360x160 (лист 4), кнопки 200x28 (6 вариантов + нажатая),
полоски 72x10 и 68x6, сердце 14x14, слот оружия 20x20, значок уровня 32x14. Всё рисуется кодом, цвета грязные, без неона."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image
from scipy import ndimage

import bake

OUT = os.path.join(bake.ROOT, "assets", "hd", "ui")
os.makedirs(OUT, exist_ok=True)
INK = np.array([14, 8, 10])
ACCENTS = [  # (металл светлый, металл тёмный, ржавчина, потёк)
    ((92, 74, 66), (46, 36, 34), (150, 70, 30), (150, 14, 20)),     # ржавое железо, кровь
    ((84, 88, 76), (38, 42, 36), (110, 96, 40), (96, 120, 20)),     # гнилая зелень, желчь
    ((98, 92, 82), (50, 46, 42), (120, 100, 60), (130, 20, 24)),    # кость
    ((80, 64, 86), (36, 28, 42), (110, 50, 70), (120, 20, 60)),     # синяк
    ((100, 70, 56), (52, 30, 26), (170, 80, 30), (170, 20, 14)),    # медь
    ((70, 80, 90), (30, 36, 44), (90, 90, 80), (110, 24, 28)),      # холодная сталь
    ((86, 78, 60), (44, 38, 28), (140, 110, 40), (140, 100, 20)),   # гной
    ((60, 56, 56), (24, 22, 22), (100, 60, 50), (130, 10, 16)),     # сажа
]


def noise(h, w, rng, s=1.2):
    n = ndimage.gaussian_filter(rng.random((h, w)), s)
    return (n - n.mean()) / (n.std() + 1e-6)


def plate(w, h, t, acc, seed, interior=(10, 8, 10, 255), drips=True, rivets=True, cracks=True, radius=3):
    """Железная рамка w x h толщиной t с внутренним полем."""
    rng = np.random.default_rng(seed)
    light, dark, rust, blood = [np.array(c, np.float32) for c in acc]
    img = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    dx = np.minimum(xx, w - 1 - xx)
    dy = np.minimum(yy, h - 1 - yy)
    d = np.minimum(dx, dy)
    # скруглённые срезанные углы
    cut = (dx < radius) & (dy < radius) & ((radius - dx) + (radius - dy) > radius + 0)
    frame = (d < t) & ~cut
    n1 = noise(h, w, rng, 1.0)
    n2 = noise(h, w, rng, 3.0)
    metal = dark[None, None, :] + (light - dark)[None, None, :] * np.clip(0.75 + 0.30 * n1 + 0.2 * n2, 0, 1)[..., None] * 1.25
    bevel = np.where(d == 0, 0.5, np.where(d == t - 1, 0.7, 1.0))                    # тёмный внешний контур, внутренняя кромка
    edge_hi = ((yy < 2) | (xx < 2)) & frame & (d >= 1)
    metal = metal * bevel[..., None]
    metal[edge_hi] = np.clip(metal[edge_hi] * 1.25, 0, 255)
    rustm = np.clip(n2 * 0.9 + noise(h, w, rng, 0.8) * 0.5 - 0.35, 0, 1) * (rng.random((h, w)) < 0.85)
    metal = metal * (1 - rustm[..., None] * 0.8) + rust[None, None, :] * rustm[..., None] * 0.8
    img[..., :3] = metal
    img[..., 3] = np.where(frame, 255, 0)
    inner = (d >= t) & ~cut
    img[inner] = np.array(interior, np.float32)
    # грязь по внутренней кромке
    shade = np.clip(1.0 - (d - t) / 6.0, 0, 1) * inner
    img[..., :3] = img[..., :3] * (1 - 0.5 * shade[..., None])
    if rivets and min(w, h) > 14:
        for cx, cy in [(t // 2, t // 2), (w - 1 - t // 2, t // 2), (t // 2, h - 1 - t // 2), (w - 1 - t // 2, h - 1 - t // 2)]:
            if 0 <= cx < w and 0 <= cy < h:
                img[cy, cx, :3] = light * 1.35
                img[min(cy + 1, h - 1), cx, :3] = dark * 0.6
    if cracks and min(w, h) > 24:
        for _ in range(max(1, (w + h) // 90)):
            x, y = rng.integers(2, w - 2), rng.integers(0, t)
            if rng.random() < 0.5:
                y = h - 1 - y
            for k in range(int(rng.integers(4, 12))):
                if 0 <= y < h and 0 <= x < w and frame[y, x]:
                    img[y, x, :3] = INK
                x += int(rng.integers(-1, 2)); y += 1 if y < h // 2 else -1
    if drips:
        for _ in range(max(3, w // 14)):
            x = int(rng.integers(t, w - t))
            ln = int(rng.integers(4, max(6, min(40, h // 2))))
            wide = 2 if min(w, h) > 40 and rng.random() < 0.6 else 1
            for k in range(ln):
                y = k
                if y < h:
                    f = 1.0 - k / (ln + 1.0) * 0.4
                    for ddx in range(wide):
                        img[y, min(x + ddx, w - 1), :3] = blood * f
                        img[y, min(x + ddx, w - 1), 3] = 255
            if rng.random() < 0.7 and ln < h:                                    # капля на конце
                img[min(ln, h - 1), x, :3] = blood * 0.8
                img[min(ln, h - 1), x, 3] = 255
        # блики крови на кромке
        for x in range(t, w - t):
            if rng.random() < 0.06:
                img[t - 1, x, :3] = blood * 0.9
    return np.clip(img, 0, 255).astype(np.uint8)


def paste(sheet, cell, x, y):
    sheet[y:y + cell.shape[0], x:x + cell.shape[1]] = cell


def card_frames():
    W, H = 112, 150
    sheet = np.zeros((H * 2, W * 8, 4), np.uint8)
    for i in range(16):
        acc = ACCENTS[i % 8]
        cell = plate(W, H, 6 if i < 8 else 7, acc, 100 + i, radius=5)
        paste(sheet, cell, (i % 8) * W, (i // 8) * H)
    Image.fromarray(sheet).save(os.path.join(OUT, "card_frames.png"))


def death_panels():
    W, H = 360, 160
    sheet = np.zeros((H, W * 4, 4), np.uint8)
    for i in range(4):
        paste(sheet, plate(W, H, 8, ACCENTS[(i * 2) % 8], 200 + i, interior=(8, 6, 8, 245), radius=6), i * W, 0)
    Image.fromarray(sheet).save(os.path.join(OUT, "death_panels.png"))


def buttons():
    for v in range(6):
        for hover in (0, 1):
            acc = ACCENTS[v % 8]
            if hover:
                acc = tuple(tuple(min(255, int(c * 1.25)) for c in col) for col in acc)
            img = plate(200, 28, 4, acc, 300 + v + 10 * hover, interior=(18, 12, 14, 255) if not hover else (46, 14, 16, 255), cracks=False)
            Image.fromarray(img).save(os.path.join(OUT, "button_v%d%s.png" % (v, "_hover" if hover else "")))
    for name in ("button", "button_wide"):
        for hover in (0, 1):
            img = plate(200, 28, 4, ACCENTS[0], 330 + hover, interior=(18, 12, 14, 255) if not hover else (46, 14, 16, 255), cracks=False)
            Image.fromarray(img).save(os.path.join(OUT, "%s%s.png" % (name, "_hover" if hover else "")))


def bars():
    rng = np.random.default_rng(7)
    for name, fill_cols, under_acc in (("hp", ((70, 6, 12), (170, 12, 22), (230, 70, 70)), ACCENTS[0]), ("xp", ((26, 44, 6), (96, 150, 16), (190, 230, 90)), ACCENTS[1])):
        under = plate(72, 10, 2, under_acc, 400 if name == "hp" else 401, interior=(6, 4, 6, 255), drips=False, rivets=False, cracks=False, radius=2)
        Image.fromarray(under).save(os.path.join(OUT, "%s_bar_under.png" % name))
        fill = np.zeros((6, 68, 4), np.uint8)
        d0, d1, hi = [np.array(c, np.float32) for c in fill_cols]
        for y in range(6):
            t = y / 5.0
            col = d1 * (1 - t) + d0 * t if y else hi
            fill[y, :, :3] = col
        n = noise(6, 68, rng, 0.7)
        fill[..., :3] = np.clip(fill[..., :3] * (1 + 0.15 * n[..., None]), 0, 255)
        fill[..., 3] = 255
        fill[5, ::7, :3] = (fill[5, ::7, :3] * 0.6)
        Image.fromarray(fill).save(os.path.join(OUT, "%s_bar_fill.png" % name))


def heart():
    img = np.zeros((14, 14, 4), np.uint8)
    pat = ["..............", "..KKK....KKK..", ".KrrrK..KrrrK.", "KrRRrrKKrRRrrK", "KrRwRrrrrrRrrK", "KrRRrrrrrrrrrK", "KrrrrrrrrrrrrK", ".KrrrrdrrrrrK.",
           "..KrrrrdrrrK..", "...KrrrrrrK...", "....KrrdrK....", ".....KrrK.....", "......KK......", ".............."]
    pal = {"K": (14, 4, 8), "r": (140, 10, 24), "R": (200, 30, 40), "w": (250, 150, 150), "d": (80, 4, 14)}
    for y, row in enumerate(pat):
        for x, ch in enumerate(row):
            if ch in pal:
                img[y, x, :3] = pal[ch]; img[y, x, 3] = 255
    img[11:13, 6, :3] = (150, 14, 20); img[11:13, 6, 3] = 255           # капля
    Image.fromarray(img).save(os.path.join(OUT, "hud_heart.png"))


def small():
    Image.fromarray(plate(20, 20, 2, ACCENTS[0], 500, interior=(14, 10, 12, 255), drips=False, cracks=False, radius=2)).save(os.path.join(OUT, "hud_weapon_slot.png"))
    Image.fromarray(plate(32, 14, 2, ACCENTS[7], 501, interior=(24, 6, 8, 255), drips=True, cracks=False, radius=2)).save(os.path.join(OUT, "level_badge.png"))


if __name__ == "__main__":
    card_frames(); death_panels(); buttons(); bars(); heart(); small()
    man = json.load(open(bake.MANIFEST))
    for n in os.listdir(OUT):
        if n.endswith(".png") and not n.endswith("_n.png"):
            man["ui/" + n] = {"h": 1, "v": 1, "scale": 1.0, "pixel": True}
    json.dump(man, open(bake.MANIFEST, "w"), indent=1, sort_keys=True)
    # просмотр глазами
    prev = Image.new("RGBA", (900, 500), (50, 44, 44, 255))
    sheet = Image.open(os.path.join(OUT, "card_frames.png"))
    prev.alpha_composite(sheet.crop((0, 0, 448, 150)), (0, 0)); prev.alpha_composite(sheet.crop((448, 150, 896, 300)), (450, 0))
    for i in range(3):
        prev.alpha_composite(Image.open(os.path.join(OUT, "button_v%d%s.png" % (i, "_hover" if i == 2 else ""))), (10, 170 + i * 34))
    prev.alpha_composite(Image.open(os.path.join(OUT, "hp_bar_under.png")), (230, 170)); prev.alpha_composite(Image.open(os.path.join(OUT, "hp_bar_fill.png")), (232, 172))
    prev.alpha_composite(Image.open(os.path.join(OUT, "xp_bar_under.png")), (230, 190)); prev.alpha_composite(Image.open(os.path.join(OUT, "xp_bar_fill.png")), (232, 192))
    prev.alpha_composite(Image.open(os.path.join(OUT, "hud_heart.png")), (320, 170)); prev.alpha_composite(Image.open(os.path.join(OUT, "hud_weapon_slot.png")), (350, 170)); prev.alpha_composite(Image.open(os.path.join(OUT, "level_badge.png")), (380, 170))
    prev.alpha_composite(Image.open(os.path.join(OUT, "death_panels.png")).crop((0, 0, 360, 160)), (10, 280))
    prev = prev.resize((1800, 1000), Image.NEAREST)
    prev.convert("RGB").save("tools/_preview/hd/05_пиксели/интерфейс_жуть.png")
    print("ui ok")
