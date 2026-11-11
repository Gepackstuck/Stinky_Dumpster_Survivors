"""Пол новой пиксельной рисовки: мёртвая свалка (чёрная грязь, кровь, кости, банки). Из картинки модели: бесшовная плитка 256 px,
общая палитра, затемнение (пол - тёмный фон, враги и свет должны читаться), карта нормалей для света."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image
from scipy import ndimage

import bake
import rig2
from ground import seamless

SRC = "tools/_hd_raw/px4/ground_201.png"
T = 256
a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32) / 255.0
a = seamless(a)
im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((T, T), Image.BOX)
a = np.asarray(im).astype(np.float32) / 255.0
grey = a.mean(-1, keepdims=True)
a = np.clip(grey + (a - grey) * 1.1, 0, 1)
a = np.clip(0.04 + (a - a.mean()) * 0.8 + a.mean() * 0.62, 0, 1)    # темнее, контраст ниже
pal = rig2.make_palette(np.concatenate([a, np.ones((T, T, 1), np.float32)], -1), T, 22)
d = ((a[..., None, :] - pal[None, None]) ** 2).sum(-1)
q = pal[d.argmin(-1)]
out = os.path.join(bake.ROOT, "assets", "hd", "sprites", "ground_tile.png")
Image.fromarray((q * 255).astype(np.uint8)).save(out)
h = ndimage.gaussian_filter(q.mean(-1), 0.8) * 22.0
gy, gx = np.gradient(h)
n = np.stack([-gx, gy, np.ones_like(gx)], -1)
n /= np.linalg.norm(n, axis=-1, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(out.replace(".png", "_n.png"))
man = json.load(open(bake.MANIFEST))
man["sprites/ground_tile.png"] = {"h": 1, "v": 1, "scale": 0.5, "n": True, "pixel": True, "repeat": True}
json.dump(man, open(bake.MANIFEST, "w"), indent=1, sort_keys=True)
print("ground ok")
