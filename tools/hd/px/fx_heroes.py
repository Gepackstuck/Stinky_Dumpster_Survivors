"""Герои из листов FLUX (tools/_hd_raw/fx/hero_<id>_<n>.png: один персонаж с трёх сторон). Лист режется на фигуры (sheet.split),
из каждой собирается ряд ходьбы: side (смотрит ВЛЕВО, игра зеркалит), back, front - по 8 кадров, скелет по силуэту.
PICK: id -> (номер листа, порядок видов слева направо буквами s/f/b, рост в мировых единицах, отразить бок)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

import auto
import bake
import player_hobo as ph
import rig as rig1
import rig2
import sheet

P = "tools/_hd_raw/fx/"
TMP = P + "_cells/"
N = 8
DEFAULT = (1, "sfb", 46, False)
TEXEL = float(os.environ.get("HD_TEXEL", "0.3333"))     # мировых единиц на пиксель спрайта: меньше - детальнее
F = int(round(56.0 / TEXEL / 8.0)) * 8                 # кадр героя 56 мировых единиц
PICK = {"hobo": (9, "sfb", 46, False)}   # 9 - пробный лист
SMALL = {"cat": 34, "pigeon": 34, "punk": 38, "slime": 40}


def cells(hero):
    n, order, size, flip = PICK.get(hero, DEFAULT)
    os.makedirs(TMP, exist_ok=True)
    out = {}
    for img, v in zip(sheet.split("%shero_%s_%d.png" % (P, hero, n)), order):
        name = {"s": "side", "f": "front", "b": "back"}[v]
        if name == "side" and flip:
            img = img.transpose(0)          # FLIP_LEFT_RIGHT
        path = "%s%s_%s.png" % (TMP, hero, name)
        img.save(path)
        out[name] = path
    return out, SMALL.get(hero, size)


def build(path):
    cut = rig1.cutout(path, 768, 0.04)
    img, _ = ph.recrop(cut)
    warps = auto.detect_warps(img)
    r = rig2.Rig2(img)
    for name, (x, y, rad) in warps.items():
        r.warp(name, (x, y), rad)
    return r, warps


def pose_for(view, warps, i):
    p = i / N * math.tau
    sn, cs = math.sin(p), math.cos(p)
    ll, lr = max(sn, 0.0) ** 0.7, max(-sn, 0.0) ** 0.7
    pose = {}
    if view == "side":                                         # шаг ножницами вдоль экрана
        if "footL" in warps:
            pose["~footL"] = (0.045 * sn, -0.05 * ll, 1.0, 6 * sn)
            pose["~footR"] = (-0.045 * sn, -0.05 * lr, 1.0, -6 * sn)
        if "armL" in warps:
            pose["~armL"] = (-0.03 * sn, 0.0, 1.0, 10 * sn)
            pose["~armR"] = (0.03 * sn, 0.0, 1.0, -10 * sn)
    else:
        if "footL" in warps:
            pose["~footL"] = (0.0, -0.07 * ll, 1.0 + 0.08 * ll)
            pose["~footR"] = (0.0, -0.07 * lr, 1.0 + 0.08 * lr)
        if "armL" in warps:
            pose["~armL"] = (0.0, -0.02 * lr, 1.0, 10 * sn)
            pose["~armR"] = (0.0, -0.02 * ll, 1.0, 10 * sn)
    for kk in range(3):
        if "wave%d" % kk in warps:
            pose["~wave%d" % kk] = (0.012 * math.sin(p + kk * 1.4), 0.004 * math.cos(2 * p + kk), 1.0, 5 * math.sin(p + kk * 1.4 + 0.8))
    if "torso" in warps:
        pose["~torso"] = (0.006 * sn, 0.0, 1.0 + 0.025 * math.sin(2 * p))
    if "head" in warps:
        pose["~head"] = (0.005 * sn, 0.004 * abs(cs), 1.0, 2.5 * sn)
    root = {"dx": -0.008 * sn if view != "side" else 0.0, "dy": -0.018 * abs(cs), "rot": -2.0 * sn if view != "side" else -2.5, "pivot": (0.5, 0.9)}
    return pose, root


def run(hero):
    paths, size = cells(hero)
    pad = ((1 + 2 * ph.PAD) * 44.0 / size - 1.0) / 2.0
    rigs = {v: build(paths[v]) for v in ("side", "back", "front")}
    big = np.concatenate([rigs[v][0].render({}, {}, F, pad) for v in rigs], 0)
    pal = rig2.grade_palette(rig2.make_palette(big, F * 3, 34), 1.12, 1.0)
    rows = {}
    for v, (r, warps) in rigs.items():
        rows[v] = [rig2.pixelize(r.render(*pose_for(v, warps, i), F, pad), F, pal) for i in range(N)]
    bake.emit("sprites/player_%s.png" % hero, rows, size, 12, "герой_" + hero, texel=TEXEL)


if __name__ == "__main__":
    import bible_names
    for h in (sys.argv[1:] or bible_names.HEROES):
        run(h)
