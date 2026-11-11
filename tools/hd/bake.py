"""Запекание анимаций реалистичного стиля: лист кадров в assets/hd/, запись в manifest.json, GIF для просмотра."""
import json
import os

import numpy as np

import rig

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
MANIFEST = os.path.join(ROOT, "assets", "hd", "manifest.json")
PREVIEW = os.path.join(ROOT, "tools", "_preview", "hd", "02_анимации")


def emit(rel: str, rows: dict, world_w: float, fps: int = 12, title: str = "") -> None:
    """rel - путь пиксельного оригинала внутри assets/ (sprites/enemy_x.png). rows - {имя_ряда: [кадры]} (порядок = ряды листа).
    world_w - ширина фигуры в мировых единицах (как у пиксельного спрайта)."""
    names = list(rows.keys())
    frames = [rows[n] for n in names]
    fs = frames[0][0].shape[0]
    alpha = np.max(np.stack([f[..., 3] for f in frames[0]]), axis=0)   # ширина фигуры по ряду ходьбы
    xs = np.where(alpha.max(0) > 40)[0]
    fig_px = float(xs.max() - xs.min() + 1)
    rig.save_sheet(frames, os.path.join(ROOT, "assets", "hd", rel))
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    man[rel] = {"h": max(len(r) for r in frames), "v": len(frames), "scale": round(world_w / fig_px, 5), "fps": fps,
                "body_w": world_w, "rows": {n: [i, len(rows[n])] for i, n in enumerate(names)}}
    json.dump(man, open(MANIFEST, "w"), indent=1, sort_keys=True)
    base = title or os.path.splitext(os.path.basename(rel))[0]
    for n in names:
        rig.save_gif(rows[n], os.path.join(PREVIEW, "%s_%s.gif" % (base, n)), fps, scale=max(1, 384 // fs))
    print("baked", rel, "rows", {n: len(rows[n]) for n in names}, "scale", man[rel]["scale"])
