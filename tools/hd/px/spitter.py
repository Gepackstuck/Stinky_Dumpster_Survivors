"""Плевун (enemy_spitter), НОВАЯ ПИКСЕЛЬНАЯ: жирная зубастая жаба, плюётся кислотой.
Ряды: walk (10) - переступает передними лапами, жуёт, моргает; attack (8) - раздула горло, запрокинула голову, харкнула;
hurt (4) - отшатнулась, зажмурилась; death (10) - подкосилась, завалилась на бок, лапы обмякли."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig as rig1
import rig2

SRC = "tools/_hd_raw/px1/frog_13.png"
F = 88
WORLD_W = 34.0
PAD = (0.92 * F / (2.0 * WORLD_W) - 1.0) / 2.0


def build():
    cut = rig1.cutout(SRC, 768, 0.04)
    h = cut.shape[0]
    sat = cut[..., :3].max(-1) - cut[..., :3].min(-1)
    low = np.zeros(cut.shape[:2], bool)
    low[int(0.66 * h):] = True
    cut[..., 3] = np.where(low & (sat < 0.12), 0.0, cut[..., 3])    # серая тень под жабой - не тело
    r = rig2.Rig2(cut)
    r.chain("al", [(0.26, 0.55), (0.23, 0.66), (0.27, 0.77)], 0.07).chain("ar", [(0.74, 0.55), (0.77, 0.66), (0.73, 0.77)], 0.07)
    r.warp("jaw", (0.50, 0.47), 0.09).warp("throat", (0.50, 0.60), 0.12).warp("head", (0.50, 0.32), 0.18)
    r.lid("eye_l", (0.352, 0.305), 0.05, 0.05).lid("eye_r", (0.668, 0.305), 0.05, 0.05)
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
                "~jaw": (0.0, 0.012 * math.sin(2 * p), 1.0, 0.0, 1.0 + 0.22 * math.sin(2 * p)), "~throat": (0.0, 0.0, 1.0 + 0.05 * math.sin(2 * p + 1.0)),
                "^eye_l": rig1.blink(i, n, 0.55), "^eye_r": rig1.blink(i, n, 0.62)}
        rows["walk"].append(shot(pose, {"dy": -0.018 * abs(s), "rot": 2.0 * s, "sy": 1.0 - 0.025 * math.cos(2 * p), "sx": 1.0 + 0.02 * math.cos(2 * p)}))
    for sw, sp in [(0.3, 0.0), (0.7, 0.0), (1.0, 0.0), (1.0, 0.3), (0.3, 1.0), (0.0, 0.9), (0.0, 0.5), (0.0, 0.15)]:
        pose = {"~throat": (0.0, 0.01 * sw, 1.0 + 0.22 * sw - 0.08 * sp), "~head": (-0.012 * sw + 0.015 * sp, -0.02 * sw + 0.012 * sp, 1.0 + 0.04 * sp),
                "~jaw": (0.0, -0.02 * sw + 0.05 * sp, 1.0 + 0.1 * sp, 0.0, 1.0 + 0.5 * sp - 0.3 * sw), "^eye_l": 0.7 * sw, "^eye_r": 0.7 * sw,
                "al0": -8 * sw, "ar0": 8 * sw}
        rows["attack"].append(shot(pose, {"rot": -4 * sw + 5 * sp, "sx": 1.0 + 0.03 * sw + 0.05 * sp, "sy": 1.0 + 0.03 * sw - 0.03 * sp}))
    for k in [1.0, 0.75, 0.4, 0.1]:
        pose = {"^eye_l": k, "^eye_r": k, "~head": (-0.015 * k, -0.01 * k, 1.0 - 0.03 * k), "~jaw": (0.0, 0.02 * k), "al0": 12 * k, "ar0": -12 * k}
        rows["hurt"].append(shot(pose, {"rot": -6 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k}))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        fall = rig1.ease(max(0.0, min((t - 0.1) / 0.6, 1.0)))
        bounce = math.sin(max(0.0, (t - 0.7) / 0.3) * math.pi) * 0.02
        pose = {"^eye_l": rig1.ease(min(t / 0.5, 1.0)), "^eye_r": rig1.ease(min(t / 0.6, 1.0)), "~jaw": (0.0, 0.04 * fall, 1.0, 0.0, 1.0 + 0.4 * fall),
                "al0": 30 * fall, "al1": 25 * fall, "ar0": 30 * fall, "ar1": 25 * fall}
        rows["death"].append(shot(pose, {"rot": 80 * fall, "sy": 1.0 - 0.1 * rig1.ease(min(t / 0.3, 1.0)), "dy": -bounce - 0.02 * fall, "dx": -0.10 * fall, "pivot": (0.5, 0.82)}))
    return rows


if __name__ == "__main__":
    r = build()
    pal = rig2.make_palette(r.render({}, {}, F, PAD), F, 24)
    bake.emit("sprites/enemy_spitter.png", frames(r, pal), WORLD_W, 10, "плевун_новый", lift=0.0, texel=0.5)
