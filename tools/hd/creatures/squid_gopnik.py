"""Кальмар-гопник (enemy_squid_gopnik): розовая тварь в красной кепке, пасть до ушей. Базовый ближник.
Ряды: walk (12) - семенит, руки болтаются; attack (8) - бросок с раскрытой пастью; hurt (4); death (10) - оседает в лужу."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image

import bake
import rig

SRC = "tools/_hd_raw/t3/squid_24.png"
FS = 224
PAD = 0.18


def build() -> rig.Rig:
    a = rig.cutout(SRC)
    h = a.shape[0]
    a[int(0.865 * h):, :, 3] = 0.0            # лужа под ногами не должна ездить вместе со ступнями
    a[int(0.83 * h):, int(0.74 * h):, 3] = 0.0
    a[int(0.84 * h):, :int(0.17 * h), 3] = 0.0
    r = rig.Rig(a)
    r.body((0.47, 0.30), (0.47, 0.50), 0.20)
    r.body((0.45, 0.62), (0.47, 0.80), 0.16)   # ноги - часть туловища: их двигают мягкие деформации, без швов
    r.chain("arm_l", [(0.27, 0.40), (0.20, 0.52), (0.19, 0.66)], 0.055, taper=0.9)
    r.chain("arm_r", [(0.70, 0.42), (0.77, 0.52), (0.82, 0.64)], 0.05, taper=0.9)
    r.warp("foot_l", (0.26, 0.82), 0.085).warp("foot_r", (0.67, 0.81), 0.085)
    r.warp("jaw", (0.52, 0.52), 0.10).warp("head", (0.50, 0.30), 0.22).warp("cap", (0.50, 0.17), 0.12)
    return r


def frames(r: rig.Rig) -> dict:
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}
    n = 12
    for i in range(n):
        p = i / n * math.tau
        s, c = math.sin(p), math.cos(p)
        lift_l, lift_r = max(s, 0.0) ** 0.7, max(-s, 0.0) ** 0.7
        pose = {
            # поднятая ступня идёт вверх и чуть на зрителя (крупнее); опорная стоит
            "~foot_l": (0.012 * lift_l, -0.055 * lift_l, 1.0 + 0.10 * lift_l, -8 * lift_l),
            "~foot_r": (-0.012 * lift_r, -0.055 * lift_r, 1.0 + 0.10 * lift_r, 8 * lift_r),
            "arm_l0": 8 * s + 2, "arm_l1": 7 * c,
            "arm_r0": 8 * s - 2, "arm_r1": 7 * c,
            "~cap": (0.0, -0.006 * math.cos(2 * p)),
            "~jaw": (0.0, 0.008 * math.sin(2 * p + 1.0)),
        }
        # вес переносится на опорную ногу: тело качается в её сторону и чуть оседает на шаге
        root = {"dx": -0.014 * s, "dy": 0.012 * abs(c) - 0.006, "rot": -2.5 * s}
        rows["walk"].append(rig.polish(r.render(pose, FS, root, PAD)))
    # бросок: присел, руки назад (замах) -> рывок на зрителя, пасть настежь, руки хватают -> возврат
    for k in [0.0, -0.6, -1.0, 0.5, 1.0, 0.8, 0.4, 0.1]:
        wind, hit = max(-k, 0.0), max(k, 0.0)
        pose = {
            "~jaw": (0.0, 0.055 * hit - 0.012 * wind, 1.0 + 0.16 * hit),
            "~head": (0.0, -0.01 * hit + 0.015 * wind, 1.0 + 0.07 * hit - 0.03 * wind),
            "arm_l0": 16 * wind - 20 * hit, "arm_l1": 10 * wind - 16 * hit,
            "arm_r0": -16 * wind + 20 * hit, "arm_r1": -10 * wind + 16 * hit,
        }
        root = {"sy": 1.0 - 0.09 * wind + 0.09 * hit, "sx": 1.0 + 0.05 * wind + 0.06 * hit}
        rows["attack"].append(rig.polish(r.render(pose, FS, root, PAD)))
    for k in [1.0, 0.75, 0.4, 0.1]:
        pose = {"arm_l0": 14 * k, "arm_r0": -14 * k, "~head": (-0.02 * k, -0.012 * k, 1.0 - 0.04 * k), "~jaw": (0.0, 0.03 * k)}
        rows["hurt"].append(rig.polish(r.render(pose, FS, {"rot": -6 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k}, PAD)))
    # смерть: колени подгибаются, тело валится на бок и шлёпается, руки обвисают, пасть отваливается
    m = 10
    for i in range(m):
        t = i / (m - 1)
        buckle = rig.ease(min(t / 0.3, 1.0))
        fall = rig.ease(max(0.0, min((t - 0.2) / 0.55, 1.0)))
        bounce = math.sin(max(0.0, (t - 0.75) / 0.25) * math.pi) * 0.02
        pose = {"arm_l0": 26 * fall, "arm_l1": 18 * fall, "arm_r0": 30 * fall, "arm_r1": 22 * fall,
                "~jaw": (0.0, 0.04 * fall, 1.0 + 0.10 * fall), "~cap": (0.02 * fall, -0.02 * fall, 1.0, 10 * fall)}
        root = {"rot": -84 * fall, "sy": 1.0 - 0.12 * buckle, "dy": -bounce - 0.03 * fall, "dx": 0.12 * fall, "pivot": (0.45, 0.84)}
        rows["death"].append(rig.polish(r.render(pose, FS, root, PAD)))
    return rows


if __name__ == "__main__":
    r = build()
    r.debug("tools/_hd_raw/rig_squid_gopnik.png")
    bake.emit("sprites/enemy_squid_gopnik.png", frames(r), 31.0, 12, "кальмар_гопник")
