"""Микроб (enemy_microbe): зелёный шипастый шар с пастью, медленный и жирный. Ползёт на нижних отростках.
Ряды: walk (12) - пульсирует и перебирает отростками, как на ходулях, шипы колышутся; attack (8) - сжался и раскрыл пасть на
полтела; hurt (4) - сплющился; death (10) - сдувается и оседает лужей."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bake
import rig

SRC = "tools/_hd_raw/t5/microbe_184.png"
FS = 224
PAD = 0.14
LEGS = [("leg0", (0.17, 0.72)), ("leg1", (0.32, 0.83)), ("leg2", (0.52, 0.85)), ("leg3", (0.70, 0.80)), ("leg4", (0.84, 0.62))]
SPIKES = [("sp0", (0.16, 0.30)), ("sp1", (0.24, 0.18)), ("sp2", (0.47, 0.12)), ("sp3", (0.68, 0.16)), ("sp4", (0.82, 0.33)), ("sp5", (0.13, 0.47))]


def build() -> rig.Rig:
    r = rig.Rig(rig.cutout(SRC))
    for name, at in LEGS:
        r.warp(name, at, 0.07)
    for name, at in SPIKES:
        r.warp(name, at, 0.06)
    r.warp("jaw", (0.48, 0.62), 0.14).warp("brow", (0.48, 0.33), 0.16).warp("eye_l", (0.34, 0.37), 0.05).warp("eye_r", (0.61, 0.35), 0.05)
    return r


def limbs(p: float, amp: float = 1.0) -> dict:
    pose = {}
    for i, (name, _) in enumerate(LEGS):   # отростки шагают волной слева направо
        ph = p + i * 1.25
        pose["~" + name] = (0.020 * amp * math.cos(ph), -0.035 * amp * max(math.sin(ph), 0.0), 1.0, 10 * amp * math.cos(ph))
    for i, (name, _) in enumerate(SPIKES):
        pose["~" + name] = (0.0, 0.0, 1.0, 9 * amp * math.sin(p * 2 + i * 1.7))
    return pose


def frames(r: rig.Rig) -> dict:
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}
    n = 12
    for i in range(n):
        p = i / n * math.tau
        pose = limbs(p)
        pose.update({"~jaw": (0.0, 0.010 * math.sin(2 * p), 1.0 + 0.03 * math.sin(2 * p)),
                     "~eye_l": (0.0, 0.0, 1.0 + 0.08 * math.sin(p + 1.0)), "~eye_r": (0.0, 0.0, 1.0 + 0.08 * math.sin(p + 2.5))})
        breathe = math.sin(2 * p)
        rows["walk"].append(rig.polish(r.render(pose, FS, {"sx": 1.0 + 0.03 * breathe, "sy": 1.0 - 0.03 * breathe, "dy": -0.012 * abs(math.sin(p)), "rot": 2.0 * math.sin(p), "pivot": (0.5, 0.8)}, PAD)))
    for j, k in enumerate([0.0, -0.6, -1.0, 0.5, 1.0, 0.85, 0.45, 0.1]):
        wind, hit = max(-k, 0.0), max(k, 0.0)
        pose = limbs(j * 0.8, 0.4)
        pose.update({"~jaw": (0.0, 0.055 * hit - 0.04 * wind, 1.0 + 0.20 * hit - 0.08 * wind), "~brow": (0.0, -0.03 * hit + 0.02 * wind),
                     "~eye_l": (0.0, -0.02 * hit, 1.0 + 0.25 * hit), "~eye_r": (0.0, -0.02 * hit, 1.0 + 0.25 * hit)})
        rows["attack"].append(rig.polish(r.render(pose, FS, {"sy": 1.0 - 0.12 * wind + 0.10 * hit, "sx": 1.0 + 0.08 * wind + 0.08 * hit, "pivot": (0.5, 0.8)}, PAD)))
    for k in [1.0, 0.75, 0.4, 0.1]:
        pose = limbs(2.0, 1.0 + k)
        pose.update({"~brow": (0.0, 0.02 * k), "~jaw": (0.0, 0.02 * k), "~eye_l": (0.0, 0.0, 1.0 - 0.3 * k), "~eye_r": (0.0, 0.0, 1.0 - 0.3 * k)})
        rows["hurt"].append(rig.polish(r.render(pose, FS, {"sy": 1.0 - 0.14 * k, "sx": 1.0 + 0.12 * k, "rot": -5 * k, "pivot": (0.5, 0.8)}, PAD)))
    m = 10
    for i in range(m):   # сдувается: шар оседает и расползается, пасть отваливается, отростки подкашиваются
        k = rig.ease(i / (m - 1))
        pose = limbs(i * 0.9, 1.0 - k)
        pose.update({"~jaw": (0.0, 0.05 * k, 1.0 + 0.12 * k), "~brow": (0.0, 0.07 * k, 1.0 - 0.10 * k),
                     "~eye_l": (-0.02 * k, 0.05 * k, 1.0 - 0.4 * k), "~eye_r": (0.02 * k, 0.05 * k, 1.0 - 0.4 * k)})
        wob = math.sin(k * 9.0) * (1.0 - k) * 4.0
        rows["death"].append(rig.polish(r.render(pose, FS, {"sy": 1.0 - 0.52 * k, "sx": 1.0 + 0.20 * k, "rot": wob, "pivot": (0.5, 0.86)}, PAD)))
    return rows


if __name__ == "__main__":
    r = build()
    bake.emit("sprites/enemy_microbe.png", frames(r), 32.0, 12, "микроб")
