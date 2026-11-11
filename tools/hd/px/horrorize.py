"""Запасной «ужастик» для всех картинок, которые ещё не перерисованы вручную: тот же размер и раскладка кадров, но цвета грязные и приглушённые,
неон уходит (розовый -> кровь, лайм -> гниль, голубой -> холодная сталь, жёлтый -> охра), по краям тёмная кайма, зерно, редкие тёмные брызги.
Результат: assets/hd/<тот же путь>; игра подхватывает его в новом стиле (ArtStyle). Уже нарисованные вручную файлы не трогаются.
Запуск: PYTHONPATH=tools/hd tools/_venv/ml/bin/python tools/hd/px/horrorize.py"""
import colorsys
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image
from scipy import ndimage

import bake

ROOT = bake.ROOT
SKIP_DIRS = {"fonts", "hd", "music", "sfx", "shaders"}
rng = np.random.default_rng(5)


def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.where(m, d, 1), 0); gc = np.where(m, (mx - g) / np.where(m, d, 1), 0); bc = np.where(m, (mx - b) / np.where(m, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = np.where(m, h, 0.0)
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx


def hsv2rgb(h, s, v):
    i = np.floor(h * 6.0).astype(int) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    out = np.zeros(h.shape + (3,))
    for k, (r, g, b) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        sel = i == k
        out[..., 0] = np.where(sel, r, out[..., 0]); out[..., 1] = np.where(sel, g, out[..., 1]); out[..., 2] = np.where(sel, b, out[..., 2])
    return out


def horrorize(img, blood=0.02):
    a = np.asarray(img.convert("RGBA")).astype(np.float64) / 255.0
    al = a[..., 3]
    h, s, v = rgb2hsv(a[..., :3])
    nh, ns = h.copy(), s.copy()
    zones = [((h >= 0.80) | (h < 0.04), 0.985, 0.85), ((h >= 0.04) & (h < 0.17), 0.09, 0.62), ((h >= 0.17) & (h < 0.45), 0.19, 0.55),
             ((h >= 0.45) & (h < 0.72), 0.57, 0.33), ((h >= 0.72) & (h < 0.80), 0.82, 0.55)]
    for sel, hue, k in zones:
        nh = np.where(sel, hue, nh); ns = np.where(sel, s * k, ns)
    nv = np.power(v, 1.18) * 0.88
    solid = al > 0.5
    edge = solid & ~ndimage.binary_erosion(solid)
    nv = np.where(edge, nv * 0.6, nv)
    grain = (rng.random(v.shape) - 0.5) * 0.07
    nv = np.clip(nv + grain * solid, 0, 1)
    rgb = hsv2rgb(nh, np.clip(ns, 0, 1), nv)
    spl = solid & (rng.random(v.shape) < blood) & ~edge
    rgb[spl] = np.array([0.38, 0.03, 0.05]) * (0.6 + 0.6 * rng.random(spl.sum()))[:, None]
    out = np.zeros(a.shape)
    out[..., :3] = rgb
    out[..., 3] = al
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")


def boss_rows():
    s = open(os.path.join(ROOT, "scripts/autoload/balance.gd"), encoding="utf-8").read()
    return {k: int(v) for k, v in re.findall(r'&"(boss_\w+)": \{[^\n]*?"anim_rows": (\d+)', s)}


if __name__ == "__main__":
    man = json.load(open(bake.MANIFEST)) if os.path.exists(bake.MANIFEST) else {}
    rows = boss_rows()
    done = 0
    for sub in ("sprites", "ui"):
        base = os.path.join(ROOT, "assets", sub)
        for fn in sorted(os.listdir(base)):
            if not fn.endswith(".png"):
                continue
            rel = "%s/%s" % (sub, fn)
            if rel in man:
                continue     # нарисовано вручную
            src = Image.open(os.path.join(base, fn))
            out = horrorize(src, 0.02 if "item_" not in fn else 0.008)
            dst = os.path.join(ROOT, "assets", "hd", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            out.save(dst)
            e = {"h": 1, "v": 1, "scale": 1.0, "pixel": True, "generic": True}
            w, h = src.size
            if sub == "sprites" and fn.startswith("enemy_"):
                eid = fn[len("enemy_"):-4]
                v = rows.get(eid, 1)
                e.update({"h": 4, "v": v, "body_w": w / 4.0, "foot": h / v / 2.0 - 1.0, "fps": 8})
            elif sub == "sprites" and fn.startswith("player_"):
                e.update({"h": 4, "v": 3, "body_w": w / 4.0, "foot": h / 3 / 2.0 - 1.0, "fps": 8})
            man[rel] = e
            done += 1
    json.dump(man, open(bake.MANIFEST, "w"), indent=1, sort_keys=True)
    print("horrorized", done)
