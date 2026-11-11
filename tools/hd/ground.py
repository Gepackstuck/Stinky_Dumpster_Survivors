"""Пол арены реалистичного стиля: из картинки модели делает бесшовную плитку, приглушает и затемняет (враги должны читаться)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image

import bake

SRC = "tools/_hd_raw/t3/ground_51.png"
WORLD = 150.0
RELIEF = 60.0   # сила рельефа пола   # мировых единиц на одну плитку


def seamless(a: np.ndarray) -> np.ndarray:
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.minimum(np.minimum(xx, w - 1 - xx) / (w * 0.22), np.minimum(yy, h - 1 - yy) / (h * 0.22))
    m = np.clip(d, 0.0, 1.0)
    m = (m * m * (3 - 2 * m))[..., None]
    return a * m + np.roll(a, (h // 2, w // 2), (0, 1)) * (1 - m)


if __name__ == "__main__":
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32) / 255.0
    a = seamless(a)
    grey = a.mean(-1, keepdims=True)
    a = grey + (a - grey) * 0.8
    a = 0.24 + (a - a.mean()) * 0.5          # низкий контраст, тёмный: пол - фон, а не герой кадра
    a = a * np.array([1.0, 0.93, 0.90], np.float32)   # чуть в ржаво-красное
    out = os.path.join(bake.ROOT, "assets", "hd", "sprites", "ground_tile.png")
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(out)
    # рельеф для света: высота по яркости (трещины и ямы темнее - значит ниже)
    from scipy import ndimage
    h = ndimage.gaussian_filter(grey[..., 0], 1.2) * RELIEF
    gy, gx = np.gradient(h)
    n = np.stack([-gx, gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(out.replace(".png", "_n.png"))
    man = json.load(open(bake.MANIFEST))
    man["sprites/ground_tile.png"] = {"h": 1, "v": 1, "scale": WORLD / a.shape[0], "n": True, "repeat": True}
    json.dump(man, open(bake.MANIFEST, "w"), indent=1, sort_keys=True)
    print("ground ok")
