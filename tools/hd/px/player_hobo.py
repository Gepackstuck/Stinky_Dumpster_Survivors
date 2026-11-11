"""Герой «Бомж Вася» (player_hobo), ЖУТКАЯ НОВАЯ ПИКСЕЛЬНАЯ. Досье: бородач в ушанке и драном пальто с заплатками, красный нос, в руке бутылка.
Здесь: серый от грязи доходяга в ушанке и рваном зелёном пальто с кровавыми потёками, красные глаза, борода слиплась.
Ряды как в игре: side (смотрит ВЛЕВО, игра зеркалит) - 8 кадров шага, ноги ходят ножницами; back (идёт вверх) - 8; front (идёт вниз) - 8.
Рост героя около 44 мировых единиц (88 px), один пиксель = 0.5 единицы."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig as rig1
import rig2

F = 112
PAD = 0.085
N = 8


def recrop(cut, tf_in=None):
    """Обрезать по телу и вернуть (картинка, функция пересчёта координат старой картинки -> новой)."""
    h, w = cut.shape[:2]
    ys, xs = np.where(cut[..., 3] > 0.3)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    side = max(x1 - x0, y1 - y0)
    pad = int(side * 0.04)
    S = side + 2 * pad
    out = np.zeros((S, S, 4), np.float32)
    ox = (S - (x1 - x0)) // 2
    oy = S - pad - (y1 - y0)
    out[oy:oy + (y1 - y0), ox:ox + (x1 - x0)] = cut[y0:y1, x0:x1]
    k = 768.0 / S
    import PIL.Image as I
    big = np.asarray(I.fromarray((out * 255).astype(np.uint8)).resize((768, 768), I.NEAREST)).astype(np.float32) / 255.0
    return big, (lambda x, y: ((x * w - x0 + ox) / S, (y * h - y0 + oy) / S))


def front():
    cut = rig1.cutout("tools/_hd_raw/px3/hobo_122.png", 768, 0.04)
    h, w = cut.shape[:2]
    rgb = cut[..., :3]
    red = (rgb[..., 0] - np.maximum(rgb[..., 1], rgb[..., 2])) > 0.10
    low = np.zeros(cut.shape[:2], bool); low[int(0.78 * h):] = True
    cut[..., 3] = np.where(low & red, 0.0, cut[..., 3])                  # лужа крови под ногами
    bottle = np.zeros(cut.shape[:2], bool); bottle[int(0.62 * h):, :int(0.40 * w)] = True
    cut[..., 3] = np.where(bottle, 0.0, cut[..., 3])                       # бутылка на земле
    img, tf = recrop(cut)
    r = rig2.Rig2(img)
    fl, fr = tf(0.50, 0.80), tf(0.65, 0.80)
    r.warp("foot_l", fl, 0.075).warp("foot_r", fr, 0.075)
    r.warp("head", tf(0.56, 0.17), 0.12).warp("hem", tf(0.57, 0.68), 0.16)
    r.chain("arm_l", [tf(0.42, 0.34), tf(0.38, 0.47), tf(0.37, 0.58)], 0.06).chain("arm_r", [tf(0.70, 0.34), tf(0.73, 0.47), tf(0.71, 0.58)], 0.06)
    r.lid("lid_l", tf(0.545, 0.205), 0.02, 0.02).lid("lid_r", tf(0.585, 0.205), 0.02, 0.02)
    return r


def back():
    cut = rig1.cutout("tools/_hd_raw/px5/back_303.png", 768, 0.04)
    cut = cut.copy()
    img, tf = recrop(cut)
    r = rig2.Rig2(img)
    r.warp("foot_l", tf(0.44, 0.84), 0.075).warp("foot_r", tf(0.58, 0.84), 0.075).warp("head", tf(0.50, 0.14), 0.1).warp("hem", tf(0.50, 0.66), 0.16)
    r.chain("arm_l", [tf(0.38, 0.35), tf(0.34, 0.47), tf(0.33, 0.58)], 0.06).chain("arm_r", [tf(0.63, 0.35), tf(0.66, 0.47), tf(0.65, 0.57)], 0.06)
    return r


def side():
    cut = rig1.cutout("tools/_hd_raw/px5/side_314.png", 768, 0.04)
    img, tf = recrop(cut)
    r = rig2.Rig2(img)
    r.chain("leg_f", [tf(0.50, 0.70), tf(0.46, 0.77), tf(0.46, 0.85)], 0.055).chain("leg_b", [tf(0.55, 0.70), tf(0.56, 0.78), tf(0.57, 0.87)], 0.055)
    r.chain("arm", [tf(0.50, 0.38), tf(0.52, 0.47), tf(0.52, 0.55)], 0.05)
    r.warp("head", tf(0.47, 0.15), 0.1).warp("hem", tf(0.50, 0.66), 0.14)
    return r


def walk_pose(kind, i, n=N):
    p = i / n * math.tau
    s, c = math.sin(p), math.cos(p)
    ll, lr = max(s, 0.0) ** 0.7, max(-s, 0.0) ** 0.7
    if kind == "side":
        pose = {"leg_f0": 30 * s, "leg_f1": -26 * max(-s, 0.0) + 8 * max(s, 0.0), "leg_b0": -30 * s, "leg_b1": -26 * max(s, 0.0) + 8 * max(-s, 0.0),
                "arm0": -16 * s, "arm1": -8 * s, "~head": (0.004 * s, 0.003 * abs(c)), "~hem": (0.02 * s, 0.0, 1.0, -4 * s)}
        root = {"dy": -0.014 * abs(c), "rot": -2.5, "pivot": (0.5, 0.9)}
    else:
        k = -1.0 if kind == "back" else 1.0
        pose = {"~foot_l": (0.0, -0.05 * ll, 1.0 + 0.06 * k * ll), "~foot_r": (0.0, -0.05 * lr, 1.0 + 0.06 * k * lr),
                "arm_l0": 8 * s, "arm_l1": 6 * s, "arm_r0": 8 * s, "arm_r1": 6 * s, "~head": (0.005 * s, 0.003 * abs(c), 1.0, 2 * s),
                "~hem": (0.012 * s, 0.0, 1.0, -3 * s)}
        if kind == "front":
            pose["^lid_l"] = rig1.blink(i, n, 0.7)
            pose["^lid_r"] = rig1.blink(i, n, 0.74)
        root = {"dx": -0.008 * s, "dy": -0.012 * abs(c), "rot": -1.6 * s, "pivot": (0.5, 0.9)}
    return pose, root


if __name__ == "__main__":
    rigs = {"side": side(), "back": back(), "front": front()}
    pal_src = np.concatenate([rig2.pixelize(rigs[k].render({}, {}, F, PAD), F, np.zeros((1, 3))) for k in rigs], 0)
    big = np.concatenate([rigs[k].render({}, {}, F, PAD) for k in rigs], 0)
    pal = rig2.grade_palette(rig2.make_palette(big, F * 3, 30), 1.1, 0.58)
    rows = {}
    for k, r in rigs.items():
        rows[k] = []
        for i in range(N):
            pose, root = walk_pose(k, i)
            rows[k].append(rig2.pixelize(r.render(pose, root, F, PAD), F, pal))
    bake.emit("sprites/player_hobo.png", rows, 44.0, 12, "герой_бомж_жуть", texel=0.5)
