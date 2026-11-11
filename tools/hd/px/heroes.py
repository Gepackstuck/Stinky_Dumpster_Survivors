"""18 героев в тоне «В с абсурдом»: заготовки tools/_hd_raw/pf/hero_<id>_<вид>_<сид>.png, три вида (side смотрит ВЛЕВО, back, front) по 8 кадров, скелет по силуэту."""
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

P = "tools/_hd_raw/pf/"
N = 8
# id: (размер в мировых единицах по высоте/ширине, {вид: (номер заготовки 0/1, отразить)})
H = {
    "blogger": (44, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "cat": (30, {"side": (1, True), "back": (1, False), "front": (1, False)}),
    "clerk": (44, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "courier": (44, {"side": (0, True), "back": (1, False), "front": (1, False)}),
    "dacha": (44, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "gopnik_jock": (44, {"side": (1, False), "back": (1, False), "front": (1, False)}),
    "granny": (42, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "guard": (46, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "hobo": (44, {"side": (1, False), "back": (1, False), "front": (1, False)}),
    "janitor": (44, {"side": (0, True), "back": (1, False), "front": (1, False)}),
    "pigeon": (32, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "plumber": (44, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "punk": (36, {"side": (0, True), "back": (1, False), "front": (1, False)}),
    "shawarma": (44, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "skater": (44, {"side": (0, True), "back": (1, False), "front": (1, False)}),
    "slime": (44, {"side": (0, False), "back": (1, False), "front": (1, False)}),
    "squid": (44, {"side": (1, False), "back": (1, False), "front": (1, False)}),
    "student": (44, {"side": (1, False), "back": (1, False), "front": (1, False)}),
    "uncle_vitya": (46, {"side": (1, True), "back": (1, False), "front": (1, False)}),
}
SEED0 = {}
for f in os.listdir(P):
    if f.startswith("hero_") and f.endswith(".png"):
        key = f[5:].rsplit("_", 1)
        SEED0.setdefault(key[0], []).append(f)


def src(hero, view, idx):
    fs = sorted(SEED0["%s_%s" % (hero, view)])
    return P + fs[min(idx, len(fs) - 1)]


def build(hero, view, idx, flip):
    cut = rig1.cutout(src(hero, view, idx), 768, 0.04)
    if flip:
        cut = cut[:, ::-1].copy()
    img, _ = ph.recrop(cut)
    spec = {"auto": True}
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
            pose["~footL"] = (0.05 * sn, -0.05 * ll, 1.0, 0.0)
            pose["~footR"] = (-0.05 * sn, -0.05 * lr, 1.0, 0.0)
        if "armL" in warps:
            pose["~armL"] = (-0.03 * sn, 0.0, 1.0, 10 * sn)
            pose["~armR"] = (0.03 * sn, 0.0, 1.0, -10 * sn)
    else:
        k = 1.0
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
        pose["~head"] = (0.005 * sn, 0.003 * abs(cs), 1.0, 2.5 * sn)
    root = {"dx": -0.008 * sn, "dy": -0.016 * abs(cs), "rot": -2.0 * sn if view != "side" else -2.5, "pivot": (0.5, 0.9)}
    return pose, root


def run(hero):
    size, picks = H[hero]
    pad = ((1 + 2 * ph.PAD) * 44.0 / size - 1.0) / 2.0
    rigs = {v: build(hero, v, *picks[v]) for v in ("side", "back", "front")}
    big = np.concatenate([rigs[v][0].render({}, {}, ph.F, pad) for v in rigs], 0)
    pal = rig2.grade_palette(rig2.make_palette(big, ph.F * 3, 30), 1.15, 1.0)
    rows = {}
    for v, (r, warps) in rigs.items():
        rows[v] = []
        for i in range(N):
            pose, root = pose_for(v, warps, i)
            rows[v].append(rig2.pixelize(r.render(pose, root, ph.F, pad), ph.F, pal))
    bake.emit("sprites/player_%s.png" % hero, rows, size, 12, "герой_" + hero, texel=0.5)


if __name__ == "__main__":
    only = sys.argv[1:]
    for h in H:
        if not only or h in only:
            run(h)
