"""Декали пола реалистичного стиля: лужи крови и кучи потрохов. Лист ячеек 256 px -> assets/hd/sprites/ground_decals.png.
Кровь вырезается по цвету (красное на сером фоне), потроха - как предмет."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
from scipy import ndimage

import bake
import rig

CELL = 256
BLOOD = ["tools/_hd_raw/t4/blood_111.png", "tools/_hd_raw/t4/blood_112.png"]
GUTS = ["tools/_hd_raw/t4/guts_121.png", "tools/_hd_raw/t4/guts_122.png"]
WORLD = 46.0   # мировых единиц на ячейку


def red_key(path: str) -> np.ndarray:
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    red = a[..., 0] - np.maximum(a[..., 1], a[..., 2])           # насколько пиксель краснее серого фона
    mask = ndimage.binary_fill_holes(red > 0.10)                 # блики и отражения внутри лужи - тоже лужа
    mask = ndimage.binary_opening(mask, iterations=1)
    alpha = np.maximum(np.clip((red - 0.04) / 0.14, 0.0, 1.0), ndimage.gaussian_filter(mask.astype(np.float32), 1.5))
    lum = a.mean(-1, keepdims=True)
    blood = np.array([0.42, 0.02, 0.03], np.float32) * (0.35 + lum * 1.3)   # серые блики красим в тёмную кровь, яркость оставляем
    k = np.clip((red - 0.02) / 0.10, 0.0, 1.0)[..., None]
    rgb = np.clip(a * k + blood * (1 - k), 0.0, 1.0)
    return np.concatenate([rgb, alpha[..., None]], -1)


def fit(a: np.ndarray) -> np.ndarray:
    ys, xs = np.where(a[..., 3] > 0.1)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    side = max(h, w)
    c = np.zeros((side, side, 4), np.float32)
    c[(side - h) // 2:(side - h) // 2 + h, (side - w) // 2:(side - w) // 2 + w] = a
    im = Image.fromarray((c * 255).astype(np.uint8)).resize((CELL - 8, CELL - 8), Image.LANCZOS)
    out = Image.new("RGBA", (CELL, CELL))
    out.paste(im, (4, 4))
    return np.asarray(out)


if __name__ == "__main__":
    cells = [fit(red_key(p)) for p in BLOOD] + [fit(rig.cutout(p, 512, 0.02)) for p in GUTS]
    sheet = np.concatenate(cells, 1).astype(np.float32)
    sheet[..., :3] *= 0.8   # темнее: пол не спорит с врагами
    out = os.path.join(bake.ROOT, "assets", "hd", "sprites", "ground_decals.png")
    Image.fromarray(sheet.astype(np.uint8)).save(out)
    man = json.load(open(bake.MANIFEST))
    man["sprites/ground_decals.png"] = {"h": len(cells), "v": 1, "scale": WORLD / CELL, "blood": len(BLOOD)}
    json.dump(man, open(bake.MANIFEST, "w"), indent=1, sort_keys=True)
    Image.fromarray(sheet.astype(np.uint8)).save("tools/_hd_raw/_decals.png")
    print("decals", len(cells))
