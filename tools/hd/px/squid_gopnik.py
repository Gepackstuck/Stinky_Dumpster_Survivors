"""Кальмар-гопник (enemy_squid_gopnik), ЖУТКАЯ НОВАЯ ПИКСЕЛЬНАЯ: распухшая багровая тварь в окровавленной кепке, выпученные налитые глаза,
пасть с рядами кривых зубов, 10 мокрых щупалец с язвами, с них капает.
Ряды: walk (12) - волочится на нижних щупальцах, верхние извиваются волной, зубы чавкают, глаза дёргаются; attack (8) - присел, подобрал
щупальца и кинулся с распахнутой пастью; hurt (4) - отшатнулся, щупальца веером; death (10) - щупальца обмякают, оседает в лужу, кепка слетает."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig as rig1
import rig2

SRC = "tools/_hd_raw/px3/squid_102.png"
F = 96
WORLD_W = 40.0
PAD = (0.92 * F / (2.0 * WORLD_W) - 1.0) / 2.0
CH = [  # имя, точки (корень -> кончик), радиус, знак
    ("UL", [(0.26, 0.44), (0.17, 0.38), (0.19, 0.26), (0.23, 0.14)], 0.045, 1),
    ("UR", [(0.74, 0.43), (0.82, 0.36), (0.80, 0.24), (0.78, 0.15)], 0.045, -1),
    ("ML", [(0.27, 0.52), (0.17, 0.55), (0.11, 0.58)], 0.04, 1),
    ("MR", [(0.72, 0.52), (0.82, 0.55), (0.89, 0.58)], 0.04, -1),
    ("LL", [(0.32, 0.64), (0.24, 0.73), (0.18, 0.84), (0.27, 0.88)], 0.045, 1),
    ("LC", [(0.40, 0.70), (0.36, 0.80), (0.38, 0.89)], 0.04, 1),
    ("RC", [(0.58, 0.70), (0.60, 0.80), (0.64, 0.88)], 0.04, -1),
    ("RR", [(0.64, 0.66), (0.72, 0.75), (0.77, 0.85), (0.69, 0.88)], 0.045, -1),
]


def build():
    cut = rig1.cutout(SRC, 768, 0.04)
    h = cut.shape[0]
    rgb = cut[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    shadow = np.zeros(cut.shape[:2], bool)
    shadow[int(0.70 * h):] = True
    cut[..., 3] = np.where(shadow & (lum < 0.16) & (sat < 0.22), 0.0, cut[..., 3])     # лужа тени под тварью - не тело
    cap = np.zeros(cut.shape[:2], bool)
    cap[:int(0.31 * h)] = True
    greyish = cap & (sat < 0.2)
    cut[..., :3] = np.where(greyish[..., None], np.clip(lum[..., None] * np.array([1.9, 0.42, 0.40], np.float32), 0, 1), cut[..., :3])   # кепка тёмно-красная
    r = rig2.Rig2(cut)
    for name, pts, rad, _ in CH:
        r.chain(name, pts, rad)
    r.warp("jaw", (0.50, 0.58), 0.12).warp("cap", (0.50, 0.20), 0.14).warp("head", (0.50, 0.36), 0.2)
    r.warp("eye_l", (0.40, 0.385), 0.05).warp("eye_r", (0.62, 0.385), 0.05)
    r.lid("lid_l", (0.40, 0.385), 0.045, 0.045).lid("lid_r", (0.62, 0.385), 0.045, 0.045)
    return r


def tent(p, amp=1.0, walk=0.0, up=0.0):
    pose = {}
    for k, (name, _, _, sg) in enumerate(CH):
        ph = p + k * 0.85
        base = 6.5 * amp * (1.0 if name[0] in "UML" and name[1] != "C" else 0.8)
        n = len([1 for _ in range(4)])
        for i in range(3):
            pose["%s%d" % (name, i)] = base * math.sin(ph - i * 0.9) * (0.6 + 0.4 * i) * sg + sg * up * (8 + 5 * i)
    if walk:
        for name, ph in (("LL", 0.0), ("RR", math.pi), ("LC", math.pi * 0.5), ("RC", math.pi * 1.5)):
            sg = 1 if name[0] == "L" else -1
            lift = max(math.sin(p + ph), 0.0)
            pose[name + "0"] = pose.get(name + "0", 0.0) + sg * (-10.0 * lift) * walk
            pose[name + "1"] = pose.get(name + "1", 0.0) + sg * (-15.0 * lift) * walk
    return pose


def frames(r, pal):
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}

    def shot(pose, root):
        return rig2.pixelize(r.render(pose, root, F, PAD), F, pal)

    n = 12
    for i in range(n):
        p = i / n * math.tau
        s, c = math.sin(p), math.cos(p)
        pose = tent(p, 1.0, 1.0)
        pose.update({"~jaw": (0.0, 0.012 * math.sin(2 * p), 1.0, 0.0, 1.0 + 0.2 * math.sin(2 * p)), "~cap": (0.0, -0.008 * abs(s)),
                     "~eye_l": (0.010 * math.sin(p * 2), 0.006 * math.cos(p * 3)), "~eye_r": (-0.010 * math.sin(p * 2 + 1.0), 0.006 * math.cos(p * 3 + 2.0)),
                     "^lid_l": rig1.blink(i, n, 0.5), "^lid_r": rig1.blink(i, n, 0.64)})
        rows["walk"].append(shot(pose, {"dx": -0.012 * s, "dy": -0.016 * abs(c), "rot": -2.0 * s, "pivot": (0.5, 0.8)}))
    for wind, hit in [(0.0, 0.0), (0.6, 0.0), (1.0, 0.0), (0.4, 0.5), (0.0, 1.0), (0.0, 0.8), (0.0, 0.4), (0.0, 0.1)]:
        pose = tent(1.7, 0.5, 0.0, up=0.9 * wind - 1.1 * hit)
        pose.update({"~jaw": (0.0, 0.04 * hit - 0.03 * wind, 1.0 + 0.1 * hit, 0.0, 1.0 + 0.45 * hit - 0.18 * wind), "^lid_l": 0.6 * wind, "^lid_r": 0.6 * wind,
                     "~eye_l": (0.0, -0.01 * hit), "~eye_r": (0.0, -0.01 * hit), "~cap": (0.0, 0.012 * wind - 0.015 * hit), "~head": (0.0, 0.0, 1.0 - 0.04 * wind + 0.05 * hit)})
        rows["attack"].append(shot(pose, {"sy": 1.0 - 0.10 * wind + 0.10 * hit, "sx": 1.0 + 0.06 * wind + 0.05 * hit, "dy": 0.02 * wind - 0.025 * hit, "pivot": (0.5, 0.8)}))
    for k in (1.0, 0.75, 0.4, 0.1):
        pose = tent(2.4, 1.0 + 1.4 * k, 0.0, up=-0.6 * k)
        pose.update({"^lid_l": k, "^lid_r": k, "~jaw": (0.0, 0.02 * k, 1.0, 0.0, 1.0 + 0.25 * k), "~cap": (0.012 * k, -0.01 * k, 1.0, 8 * k), "~head": (-0.015 * k, 0.0, 1.0 - 0.04 * k)})
        rows["hurt"].append(shot(pose, {"rot": -7 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k, "pivot": (0.5, 0.8)}))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        k = rig1.ease(t)
        pose = tent(t * 4.0, 1.0 - k, 0.0, up=0.8 * k)
        pose.update({"^lid_l": rig1.ease(min(t / 0.4, 1.0)), "^lid_r": rig1.ease(min(t / 0.55, 1.0)), "~jaw": (0.0, 0.04 * k, 1.0, 0.0, 1.0 + 0.35 * k),
                     "~cap": (0.07 * k, 0.04 * k, 1.0, 38 * k), "~head": (0.0, 0.03 * k, 1.0 + 0.05 * k, 0.0, 1.0 - 0.22 * k)})
        rows["death"].append(shot(pose, {"sy": 1.0 - 0.45 * k, "sx": 1.0 + 0.22 * k, "dy": 0.01 * k, "rot": 5 * math.sin(k * 5.0) * (1 - k), "pivot": (0.5, 0.88)}))
    return rows


if __name__ == "__main__":
    r = build()
    pal = rig2.make_palette(r.render({}, {}, F, PAD), F, 30)
    pal = rig2.grade_palette(pal, 1.0, 0.85)
    bake.emit("sprites/enemy_squid_gopnik.png", frames(r, pal), WORLD_W, 10, "кальмар_гопник_жуть", texel=0.5)
