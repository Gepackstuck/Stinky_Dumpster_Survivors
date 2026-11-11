"""Декали пола в пикселях, кодом: кровь, блевотина с кусками, говно с мухами, жидкий понос, разбитые бутылки. Ячейка 64 px, 1 px = 0.5 ед.
Первые BLOOD ячеек - кровь (их берёт кровь от убитых врагов). Яркие только мерзости (кровь, блевотина, говно), остальное тёмное."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image
from scipy import ndimage

import bake

C = 64
rng = np.random.default_rng(21)


def blob(size, scale, seed, thresh=0.0, stretch=1.0):
    r = np.random.default_rng(seed)
    n = ndimage.zoom(r.standard_normal((size // scale + 3, size // scale + 3)), scale, order=3)[:size, :size]
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.hypot((xx - size / 2) / (size * 0.42 * stretch), (yy - size / 2) / (size * 0.42 / stretch))
    return (n * 0.35 - d * 1.15 + 0.62) > thresh


def paint(mask, base, dark, light, seed, spec=0.5):
    h, w = mask.shape
    r = np.random.default_rng(seed)
    out = np.zeros((h, w, 4), np.uint8)
    dist = ndimage.distance_transform_edt(mask)
    edge = mask & (dist < 1.5)
    inner = np.clip(dist / max(dist.max(), 1), 0, 1)
    shade = ndimage.gaussian_filter(r.random((h, w)), 1.5)
    col = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        col[..., c] = dark[c] + (base[c] - dark[c]) * np.clip(inner * 1.6 + (shade - 0.5), 0, 1)
    hi = mask & (ndimage.gaussian_filter(r.random((h, w)), 1.2) > 0.78) & (inner > 0.25)
    for c in range(3):
        col[..., c] = np.where(hi, light[c], col[..., c])
    col[edge] = np.array(dark) * 0.55
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(mask, 255, 0)
    return out


def splat_drops(img, color, n, rad, seed):
    r = np.random.default_rng(seed)
    h, w = img.shape[:2]
    for _ in range(n):
        x, y = int(r.integers(2, w - 2)), int(r.integers(2, h - 2))
        d = int(r.integers(1, 3))
        img[max(y - d + 1, 0):y + 1, max(x - d + 1, 0):x + 1] = (*color, 255)


def blood(seed):
    m = blob(C, 6, seed, -0.05, 1.0)
    img = paint(m, (190, 14, 22), (84, 4, 10), (255, 90, 80), seed)
    splat_drops(img, (150, 8, 16), 14, 2, seed + 1)
    return img


def vomit(seed):
    m = blob(C, 6, seed, -0.02, 1.15)
    img = paint(m, (150, 230, 24), (58, 110, 10), (230, 255, 120), seed)
    r = np.random.default_rng(seed)
    for _ in range(9):                                                            # куски: морковка, горох, непрожёванное
        x, y = int(r.integers(14, C - 14)), int(r.integers(14, C - 14))
        if m[y, x]:
            colr = [(245, 130, 20), (230, 220, 150), (200, 60, 40)][int(r.integers(0, 3))]
            img[y:y + 2, x:x + 3] = (*colr, 255)
    return img


def shit(seed):
    img = np.zeros((C, C, 4), np.uint8)
    base, dark, light = (120, 66, 26), (54, 26, 10), (190, 120, 60)
    yy, xx = np.mgrid[0:C, 0:C].astype(np.float32)
    mask = np.zeros((C, C), bool)
    for k, (w, h, oy) in enumerate(((44, 14, 44), (32, 12, 33), (22, 11, 23), (12, 9, 15))):   # куча-завиток
        mask |= (((xx - C / 2) / (w / 2)) ** 2 + ((yy - oy) / (h / 2)) ** 2) < 1.0
    mask |= (((xx - C / 2 - 2) / 3) ** 2 + ((yy - 11) / 4) ** 2) < 1.0
    img = paint(mask, base, dark, light, seed)
    for y in (22, 33, 44):                                                          # блики-завитки
        img[y - 2:y, 20:44, :3] = np.where(img[y - 2:y, 20:44, 3:4] > 0, (150, 96, 44), img[y - 2:y, 20:44, :3])
    for x, y in ((14, 8), (50, 12), (44, 4)):                                       # мухи
        img[y:y + 2, x:x + 2] = (20, 20, 24, 255)
        img[y - 1, x:x + 1] = (180, 190, 200, 255)
    for x in (22, 40, 31):                                                          # вонь
        img[2:9, x] = np.where(np.arange(7)[:, None] % 2 == 0, np.array([110, 150, 30, 160]), np.array([0, 0, 0, 0])).astype(np.uint8)
    return img


def diarrhea(seed):
    m = blob(C, 5, seed, 0.0, 1.5)
    img = paint(m, (140, 80, 24), (60, 30, 8), (210, 140, 50), seed)
    r = np.random.default_rng(seed)
    for _ in range(5):
        x = int(r.integers(10, C - 10)); y = int(r.integers(C // 2, C - 6)); ln = int(r.integers(6, 16))
        img[y:y + ln, x, :3] = (110, 60, 18); img[y:y + ln, x, 3] = 255
    return img


def bottles(seed):
    img = np.zeros((C, C, 4), np.uint8)
    r = np.random.default_rng(seed)
    for _ in range(3):
        cx, cy = int(r.integers(14, C - 14)), int(r.integers(16, C - 16)); a = r.uniform(0, 3.14)
        for t in np.linspace(-9, 9, 40):
            x, y = int(cx + np.cos(a) * t), int(cy + np.sin(a) * t * 0.5)
            wd = 3 if abs(t) < 5 else 2
            img[y:y + wd, x:x + wd] = (70, 120, 70, 255) if r.random() > 0.15 else (190, 230, 190, 255)
        img[cy, cx] = (230, 255, 230, 255)
    splat_drops(img, (190, 240, 200), 10, 1, seed + 3)
    return img


if __name__ == "__main__":
    cells = [blood(1), blood(2), blood(3), vomit(4), vomit(5), shit(6), shit(7), diarrhea(8), bottles(9)]
    sheet = np.concatenate(cells, 1)
    out = os.path.join(bake.ROOT, "assets", "hd", "sprites", "ground_decals.png")
    Image.fromarray(sheet).save(out)
    man = json.load(open(bake.MANIFEST))
    man["sprites/ground_decals.png"] = {"h": len(cells), "v": 1, "scale": 0.5, "pixel": True, "blood": 3}
    json.dump(man, open(bake.MANIFEST, "w"), indent=1, sort_keys=True)
    prev = Image.new("RGBA", (C * len(cells) * 2, C * 2), (50, 44, 44, 255))
    prev.alpha_composite(Image.fromarray(sheet).resize((C * len(cells) * 2, C * 2), Image.NEAREST))
    prev.convert("RGB").save("tools/_preview/hd/05_пиксели/декали_пола.png")
    print("decals", len(cells))
