"""Кальмар-гопник (enemy_squid_gopnik): розовый кальмар в красной кепке, пасть до ушей, ходит на щупальцах. Базовый ближник.
Ряды: walk (12) - переваливается на нижних щупальцах, верхние извиваются, язык болтается; attack (8) - присел и бросился пастью,
язык наружу; hurt (4) - дёрнулся назад; death (10) - подогнулся и завалился на бок."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig

SRC = "tools/_hd_raw/t4/squid_72.png"
FS = 224
PAD = 0.18


def build() -> rig.Rig:
    a = rig.cutout(SRC)
    h = a.shape[0]
    # кепка у гопника красная (модель нарисовала серую): серые пиксели верха перекрашиваем по яркости
    top = a[:int(0.27 * h)]
    rgb = top[..., :3]
    lum = rgb.mean(-1, keepdims=True)
    grey = (rgb.max(-1, keepdims=True) - rgb.min(-1, keepdims=True)) < 0.12
    top[..., :3] = np.where(grey, np.clip(lum * np.array([1.9, 0.22, 0.2], np.float32), 0, 1), rgb)
    r = rig.Rig(a)
    r.warp("head", (0.50, 0.30), 0.20).warp("cap", (0.50, 0.16), 0.13)
    r.warp("jaw", (0.50, 0.64), 0.15).warp("tongue", (0.50, 0.55), 0.07)
    r.warp("up_l", (0.19, 0.30), 0.07).warp("up_r", (0.85, 0.37), 0.07).warp("mid_l", (0.13, 0.50), 0.06)
    r.warp("arm_l", (0.20, 0.72), 0.11).warp("arm_r", (0.83, 0.68), 0.11)
    r.warp("foot_l", (0.36, 0.83), 0.085).warp("foot_r", (0.68, 0.83), 0.085)
    r.lid("eye_l", (0.405, 0.285), 0.052, 0.052).lid("eye_r", (0.59, 0.285), 0.052, 0.052)
    r.warp("pup_l", (0.405, 0.285), 0.03).warp("pup_r", (0.59, 0.285), 0.03)
    return r


def tentacles(p: float, amp: float = 1.0) -> dict:
    """Верхние щупальца всё время извиваются, каждое в своей фазе."""
    return {"~up_l": (0.010 * amp * math.sin(p), 0.008 * amp * math.cos(p), 1.0, 16 * amp * math.sin(p + 0.4)),
            "~up_r": (0.010 * amp * math.sin(p + 2.1), 0.008 * amp * math.cos(p + 2.1), 1.0, -16 * amp * math.sin(p + 2.5)),
            "~mid_l": (0.012 * amp * math.sin(p + 1.2), 0.0, 1.0, 14 * amp * math.sin(p + 1.6))}


def frames(r: rig.Rig) -> dict:
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}
    n = 12
    for i in range(n):
        p = i / n * math.tau
        s, c = math.sin(p), math.cos(p)
        lift_l, lift_r = max(s, 0.0) ** 0.7, max(-s, 0.0) ** 0.7
        pose = tentacles(p)
        pose.update({
            "~foot_l": (0.010 * lift_l, -0.050 * lift_l, 1.0 + 0.08 * lift_l), "~foot_r": (-0.010 * lift_r, -0.050 * lift_r, 1.0 + 0.08 * lift_r),
            # боковые щупальца загребают в противофазе с ногами - как руки при ходьбе
            "~arm_l": (0.0, -0.030 * lift_r, 1.0, 9 * s), "~arm_r": (0.0, -0.030 * lift_l, 1.0, 9 * s),
            # пасть жуёт: то распахнётся, то прикроется; язык мотается; глаза моргают вразнобой и косят по сторонам
            "~tongue": (0.022 * math.sin(p), 0.012 * math.cos(2 * p), 1.0 + 0.10 * math.sin(2 * p)),
            "~jaw": (0.0, 0.018 * math.sin(2 * p + 1.0), 1.0, 0.0, 1.0 + 0.16 * math.sin(2 * p + 1.0)),
            "^eye_l": rig.blink(i, n, 0.55), "^eye_r": rig.blink(i, n, 0.70),
            "~pup_l": (0.012 * math.sin(p), 0.004 * math.cos(p)), "~pup_r": (0.012 * math.sin(p + 0.6), 0.004 * math.cos(p)),
            "~cap": (0.0, -0.006 * math.cos(2 * p)),
        })
        rows["walk"].append(rig.polish(r.render(pose, FS, {"dx": -0.014 * s, "dy": 0.012 * abs(c) - 0.006, "rot": -2.5 * s}, PAD)))
    for j, k in enumerate([0.0, -0.6, -1.0, 0.5, 1.0, 0.85, 0.45, 0.1]):
        wind, hit = max(-k, 0.0), max(k, 0.0)
        pose = tentacles(j * 0.9, 0.5)
        pose.update({
            "~jaw": (0.0, 0.050 * hit - 0.050 * wind, 1.0 + 0.10 * hit, 0.0, 1.0 + 0.24 * hit - 0.30 * wind),
            "^eye_l": 0.75 * wind, "^eye_r": 0.75 * wind,
            "~tongue": (0.0, 0.070 * hit - 0.02 * wind, 1.0 + 0.30 * hit),
            "~head": (0.0, -0.012 * hit + 0.015 * wind, 1.0 + 0.06 * hit - 0.03 * wind),
            "~arm_l": (0.035 * hit - 0.02 * wind, -0.05 * hit, 1.0 + 0.1 * hit, -14 * hit + 8 * wind),
            "~arm_r": (-0.035 * hit + 0.02 * wind, -0.05 * hit, 1.0 + 0.1 * hit, 14 * hit - 8 * wind),
        })
        rows["attack"].append(rig.polish(r.render(pose, FS, {"sy": 1.0 - 0.10 * wind + 0.09 * hit, "sx": 1.0 + 0.05 * wind + 0.07 * hit}, PAD)))
    for k in [1.0, 0.75, 0.4, 0.1]:
        pose = tentacles(1.0, 1.0 + k)
        pose.update({"~head": (-0.02 * k, -0.012 * k, 1.0 - 0.04 * k), "~jaw": (0.0, 0.03 * k), "~tongue": (-0.02 * k, 0.02 * k), "^eye_l": k, "^eye_r": k,
                     "~arm_l": (-0.03 * k, -0.03 * k), "~arm_r": (0.03 * k, -0.03 * k)})
        rows["hurt"].append(rig.polish(r.render(pose, FS, {"rot": -6 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k}, PAD)))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        buckle = rig.ease(min(t / 0.3, 1.0))
        fall = rig.ease(max(0.0, min((t - 0.2) / 0.55, 1.0)))
        bounce = math.sin(max(0.0, (t - 0.75) / 0.25) * math.pi) * 0.02
        pose = tentacles(t * 5.0, 1.0 - fall)
        pose.update({"^eye_l": rig.ease(min(t / 0.5, 1.0)), "^eye_r": rig.ease(min(t / 0.7, 1.0)) * 0.8, "~jaw": (0.0, 0.04 * fall, 1.0 + 0.08 * fall), "~tongue": (0.03 * fall, 0.05 * fall, 1.0 + 0.2 * fall),
                     "~cap": (0.02 * fall, -0.02 * fall, 1.0, 10 * fall), "~arm_l": (0.0, 0.03 * fall), "~arm_r": (0.0, 0.03 * fall)})
        root = {"rot": -84 * fall, "sy": 1.0 - 0.12 * buckle, "dy": -bounce - 0.03 * fall, "dx": 0.12 * fall, "pivot": (0.5, 0.84)}
        rows["death"].append(rig.polish(r.render(pose, FS, root, PAD)))
    return rows


if __name__ == "__main__":
    r = build()
    r.debug("tools/_hd_raw/rig_squid_gopnik.png")
    bake.emit("sprites/enemy_squid_gopnik.png", frames(r), 32.0, 12, "кальмар_гопник")
