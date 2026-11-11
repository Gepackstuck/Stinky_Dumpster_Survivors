"""Плевун (enemy_spitter), ЖУТКАЯ НОВАЯ ПИКСЕЛЬНАЯ: распухшая серая тварь-жаба, глаза-пузыри с красными зрачками, пасть до пола с рядами игл, чёрное мясистое брюхо.
Ряды: walk (10) - переступает лапами с растопыренными пальцами, глаза дёргаются, зубы чавкают, моргает; attack (8) - раздула горло, запрокинула голову, харкнула
кислотой; hurt (4) - отшатнулась; death (10) - подкосилась, завалилась на бок, лапы обмякли."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig as rig1
import rig2

SRC = "tools/_hd_raw/px3/frog_114.png"
F = 96
WORLD_W = 40.0
PAD = (0.92 * F / (2.0 * WORLD_W) - 1.0) / 2.0


def build():
    cut = rig1.cutout(SRC, 768, 0.04)
    h = cut.shape[0]
    lum = cut[..., :3].mean(-1)
    sat = cut[..., :3].max(-1) - cut[..., :3].min(-1)
    low = np.zeros(cut.shape[:2], bool)
    low[int(0.70 * h):] = True
    cut[..., 3] = np.where(low & (lum < 0.18) & (sat < 0.10), 0.0, cut[..., 3])       # тень под лапами - не тело
    r = rig2.Rig2(cut)
    r.chain("al", [(0.25, 0.50), (0.22, 0.65), (0.26, 0.82)], 0.075).chain("ar", [(0.76, 0.50), (0.80, 0.65), (0.74, 0.82)], 0.075)
    r.warp("jaw", (0.50, 0.40), 0.13).warp("throat", (0.50, 0.55), 0.14).warp("head", (0.50, 0.28), 0.2)
    r.warp("eye_l", (0.35, 0.26), 0.07).warp("eye_r", (0.68, 0.26), 0.07)
    r.lid("lid_l", (0.35, 0.26), 0.07, 0.07).lid("lid_r", (0.68, 0.26), 0.07, 0.07)
    return r


def frames(r, pal):
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}

    def shot(pose, root):
        return rig2.pixelize(r.render(pose, root, F, PAD), F, pal)

    n = 10
    for i in range(n):
        p = i / n * math.tau
        s = math.sin(p)
        ll, lr = max(s, 0.0), max(-s, 0.0)
        pose = {"al0": 18 * s, "al1": -26 * ll + 6 * lr, "ar0": -18 * s, "ar1": -26 * lr + 6 * ll,
                "~jaw": (0.0, 0.012 * math.sin(2 * p), 1.0, 0.0, 1.0 + 0.3 * math.sin(2 * p)), "~throat": (0.0, 0.0, 1.0 + 0.05 * math.sin(2 * p + 1.0)),
                "~eye_l": (0.012 * math.sin(p * 2), 0.008 * math.cos(p * 3)), "~eye_r": (-0.012 * math.sin(p * 2 + 1.0), 0.008 * math.cos(p * 3 + 2.0)),
                "^lid_l": rig1.blink(i, n, 0.55), "^lid_r": rig1.blink(i, n, 0.66)}
        rows["walk"].append(shot(pose, {"dy": -0.018 * abs(s), "rot": 2.0 * s, "sy": 1.0 - 0.025 * math.cos(2 * p), "sx": 1.0 + 0.02 * math.cos(2 * p)}))
    for sw, sp in [(0.3, 0.0), (0.7, 0.0), (1.0, 0.0), (1.0, 0.3), (0.3, 1.0), (0.0, 0.9), (0.0, 0.5), (0.0, 0.15)]:
        pose = {"~throat": (0.0, 0.01 * sw, 1.0 + 0.25 * sw - 0.08 * sp), "~head": (-0.012 * sw + 0.015 * sp, -0.02 * sw + 0.012 * sp, 1.0 + 0.04 * sp),
                "~jaw": (0.0, -0.02 * sw + 0.05 * sp, 1.0 + 0.1 * sp, 0.0, 1.0 + 0.6 * sp - 0.3 * sw), "^lid_l": 0.6 * sw, "^lid_r": 0.6 * sw, "al0": -8 * sw, "ar0": 8 * sw}
        rows["attack"].append(shot(pose, {"rot": -4 * sw + 5 * sp, "sx": 1.0 + 0.03 * sw + 0.05 * sp, "sy": 1.0 + 0.03 * sw - 0.03 * sp}))
    for k in [1.0, 0.75, 0.4, 0.1]:
        pose = {"^lid_l": k, "^lid_r": k, "~head": (-0.015 * k, -0.01 * k, 1.0 - 0.03 * k), "~jaw": (0.0, 0.02 * k), "al0": 12 * k, "ar0": -12 * k}
        rows["hurt"].append(shot(pose, {"rot": -6 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k}))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        fall = rig1.ease(max(0.0, min((t - 0.1) / 0.6, 1.0)))
        bounce = math.sin(max(0.0, (t - 0.7) / 0.3) * math.pi) * 0.02
        pose = {"^lid_l": rig1.ease(min(t / 0.5, 1.0)), "^lid_r": rig1.ease(min(t / 0.6, 1.0)), "~jaw": (0.0, 0.04 * fall, 1.0, 0.0, 1.0 + 0.45 * fall),
                "al0": 30 * fall, "al1": 25 * fall, "ar0": 30 * fall, "ar1": 25 * fall}
        rows["death"].append(shot(pose, {"rot": 72 * fall, "sy": 1.0 - 0.1 * rig1.ease(min(t / 0.3, 1.0)), "dy": -bounce + 0.16 * fall, "dx": -0.03 * fall, "pivot": (0.5, 0.58)}))
    return rows


if __name__ == "__main__":
    r = build()
    pal = rig2.grade_palette(rig2.make_palette(r.render({}, {}, F, PAD), F, 28), 1.1, 0.78)
    bake.emit("sprites/enemy_spitter.png", frames(r, pal), WORLD_W, 10, "плевун_жуть", texel=0.5)
