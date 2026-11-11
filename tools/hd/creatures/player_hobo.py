"""Герой «Бомж» (player_hobo): бородатый мужик в зелёном ватнике с меховым воротом, руки в крови.
Ряды как у пиксельного листа: 0 - бок (смотрит влево, игра зеркалит), 1 - спиной (идёт вверх), 2 - лицом (идёт вниз).
В каждом ряду 8 кадров шага; кадр 0 - стойка. Пропорции сделаны коренастыми и голова крупнее: в игре он мелкий."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig

FS = 192
PAD = 0.04
N = 8
STOCKY = {"sx": 1.32, "sy": 0.92}   # шире и чуть ниже: читаемый силуэт


def front_like(src: str, back: bool) -> list:
    r = rig.Rig(rig.cutout("tools/_hd_raw/t5/hero_%s.png" % src))
    r.warp("head", (0.49, 0.15), 0.085).warp("leg_l", (0.45, 0.84), 0.065).warp("leg_r", (0.56, 0.84), 0.065)
    r.warp("arm_l", (0.35, 0.56), 0.07).warp("arm_r", (0.65, 0.56), 0.07).warp("hem", (0.50, 0.68), 0.12)
    out = []
    for i in range(N):
        p = i / N * math.tau
        s = math.sin(p)
        lift_l, lift_r = max(s, 0.0) ** 0.7, max(-s, 0.0) ** 0.7
        k = -1.0 if back else 1.0   # спиной: поднятая нога уходит от зрителя (мельче), а не на него
        pose = {"~head": (0.004 * s, 0.0, 1.28, 2.0 * s),
                "~leg_l": (0.0, -0.07 * lift_l, 1.0 + 0.07 * k * lift_l), "~leg_r": (0.0, -0.07 * lift_r, 1.0 + 0.07 * k * lift_r),
                # руки в противофазе с ногами
                "~arm_l": (0.0, -0.022 * lift_r + 0.012 * lift_l, 1.0, 5 * s), "~arm_r": (0.0, -0.022 * lift_l + 0.012 * lift_r, 1.0, 5 * s),
                "~hem": (0.012 * s, 0.0, 1.0, -3 * s)}
        root = dict(STOCKY, dy=0.012 * abs(math.cos(p)) - 0.012, rot=-1.6 * s, dx=-0.008 * s)
        out.append(rig.polish(r.render(pose, FS, root, PAD)))
    return out


def side() -> list:
    a = rig.cutout("tools/_hd_raw/t5/hero_side.png")[:, ::-1].copy()   # в пиксельном листе бок смотрит влево
    r = rig.Rig(a)
    r.warp("head", (0.47, 0.14), 0.085).warp("feet", (0.50, 0.85), 0.075).warp("knee", (0.50, 0.74), 0.07)
    r.warp("arm", (0.48, 0.56), 0.07).warp("hem", (0.50, 0.66), 0.10)
    out = []
    for i in range(N):
        p = i / N * math.tau
        s, c = math.sin(p), math.cos(p)
        pose = {"~head": (0.0, 0.0, 1.28, 0.0),
                "~feet": (-0.06 * s, -0.045 * max(c, 0.0)),      # ступня выносится вперёд по дуге и ставится
                "~knee": (-0.03 * s, -0.012 * max(c, 0.0)),
                "~arm": (0.045 * s, -0.008 * abs(s), 1.0, -9 * s),  # рука навстречу ноге
                "~hem": (0.014 * s, 0.0)}
        root = dict(STOCKY, dy=0.012 * abs(c) - 0.012, rot=-3.0)   # лёгкий наклон вперёд по ходу
        out.append(rig.polish(r.render(pose, FS, root, PAD)))
    return out


if __name__ == "__main__":
    rows = {"side": side(), "back": front_like("back", True), "front": front_like("front", False)}
    bake.emit("sprites/player_hobo.png", rows, 17.0, 12, "герой_бомж")
