"""Босс «Мусорный голем» (enemy_boss_trash_golem): громила из чёрных мусорных мешков и гнили, горящие глаза.
Ряды по порядку состояний босса (boss_golem_brain): walk (12) - тяжёлый шаг вразвалку; throw (8) - замах правой и бросок;
pound (8) - обе лапы вверх и удар в землю; summon (8) - лапы в стороны, рёв; enrage (12) - ярость: шаг сгорбившись, пасть открыта;
death (12) - падает на колени и валится."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bake
import rig

SRC = "tools/_hd_raw/t5/golem_203.png"
FS = 320
PAD = 0.2


def build() -> rig.Rig:
    r = rig.Rig(rig.cutout(SRC))
    r.body((0.50, 0.18), (0.50, 0.60), 0.15)
    r.body((0.36, 0.64), (0.32, 0.86), 0.10).body((0.63, 0.64), (0.67, 0.83), 0.10)
    r.chain("arm_l", [(0.33, 0.27), (0.22, 0.48), (0.25, 0.64)], 0.085, taper=1.0)
    r.chain("arm_r", [(0.70, 0.27), (0.80, 0.46), (0.75, 0.63)], 0.085, taper=1.0)
    r.warp("head", (0.58, 0.20), 0.10).warp("jaw", (0.58, 0.31), 0.05)
    r.warp("foot_l", (0.32, 0.86), 0.10).warp("foot_r", (0.67, 0.83), 0.10)
    return r


def step(p: float, amp: float = 1.0) -> tuple:
    s = math.sin(p)
    lift_l, lift_r = max(s, 0.0) ** 0.7, max(-s, 0.0) ** 0.7
    pose = {"~foot_l": (0.0, -0.05 * amp * lift_l, 1.0 + 0.06 * lift_l), "~foot_r": (0.0, -0.05 * amp * lift_r, 1.0 + 0.06 * lift_r),
            "arm_l0": 7 * s, "arm_l1": 6 * math.cos(p), "arm_r0": 7 * s, "arm_r1": 6 * math.cos(p),
            "~jaw": (0.0, 0.008 * math.sin(2 * p), 1.0, 0.0, 1.0 + 0.30 * math.sin(2 * p)), "~head": (0.006 * s, 0.004 * math.cos(2 * p), 1.0, 3 * s)}
    root = {"dx": -0.02 * amp * s, "dy": 0.016 * abs(math.cos(p)) - 0.008, "rot": -3.5 * amp * s}
    return pose, root


def frames(r: rig.Rig) -> dict:
    rows = {"walk": [], "throw": [], "pound": [], "summon": [], "enrage": [], "death": []}

    def shot(pose, root):
        return rig.polish(r.render(pose, FS, root, PAD), gamma=0.8, px=3)

    for i in range(12):
        pose, root = step(i / 12 * math.tau)
        rows["walk"].append(shot(pose, root))
    # бросок: правая лапа уходит вверх-назад, тело отклоняется, затем хлёсткий мах вперёд-вниз
    for back, fwd in [(0.3, 0.0), (0.7, 0.0), (1.0, 0.0), (1.0, 0.0), (0.3, 0.6), (0.0, 1.0), (0.0, 0.7), (0.0, 0.3)]:
        pose = {"arm_r0": -95 * back + 18 * fwd, "arm_r1": -35 * back + 25 * fwd, "arm_l0": -10 * back + 12 * fwd,
                "~head": (0.01 * back - 0.01 * fwd, 0.0), "~jaw": (0.0, 0.012 * fwd, 1.0 + 0.2 * fwd)}
        rows["throw"].append(shot(pose, {"rot": 5 * back - 7 * fwd, "sy": 1.0 + 0.02 * back - 0.04 * fwd}))
    # удар в землю: обе лапы вверх, тело вытянулось -> обрушил, присел, расплющило
    for up, slam in [(0.4, 0.0), (0.8, 0.0), (1.0, 0.0), (1.0, 0.0), (0.2, 0.7), (0.0, 1.0), (0.0, 0.8), (0.0, 0.4)]:
        pose = {"arm_l0": 110 * up - 14 * slam, "arm_l1": 25 * up, "arm_r0": -110 * up + 14 * slam, "arm_r1": -25 * up,
                "~jaw": (0.0, 0.012 * up, 1.0 + 0.25 * up), "~head": (0.0, -0.01 * up + 0.02 * slam)}
        rows["pound"].append(shot(pose, {"sy": 1.0 + 0.06 * up - 0.14 * slam, "sx": 1.0 - 0.02 * up + 0.10 * slam, "dy": -0.01 * up}))
    # призыв: лапы в стороны, голова назад, рёв, тело трясёт
    for j, k in enumerate([0.3, 0.7, 1.0, 1.0, 1.0, 1.0, 0.7, 0.3]):
        shake = (1 if j % 2 else -1) * 0.008 * k
        pose = {"arm_l0": 55 * k, "arm_l1": 20 * k, "arm_r0": -55 * k, "arm_r1": -20 * k,
                "~head": (shake, -0.02 * k, 1.0 + 0.08 * k), "~jaw": (0.0, 0.02 * k, 1.0 + 0.35 * k)}
        rows["summon"].append(shot(pose, {"dx": shake, "sy": 1.0 + 0.04 * k, "rot": -2 * k}))
    for i in range(12):   # ярость: тот же шаг, но резче, сгорблен, пасть открыта, лапы дёргаются
        p = i / 12 * math.tau
        pose, root = step(p, 1.4)
        pose.update({"~jaw": (0.0, 0.015, 1.0 + 0.3 + 0.1 * math.sin(3 * p)), "~head": (0.0, 0.015, 1.06),
                     "arm_l0": 14 * math.sin(p) + 12, "arm_r0": 14 * math.sin(p) - 12, "arm_l1": 12 * math.sin(2 * p), "arm_r1": -12 * math.sin(2 * p)})
        root.update({"sy": 0.95, "sx": 1.04})
        rows["enrage"].append(shot(pose, root))
    for i in range(12):
        t = i / 11
        kneel = rig.ease(min(t / 0.35, 1.0))
        fall = rig.ease(max(0.0, min((t - 0.3) / 0.5, 1.0)))
        bounce = math.sin(max(0.0, (t - 0.8) / 0.2) * math.pi) * 0.015
        pose = {"arm_l0": 25 * kneel + 20 * fall, "arm_l1": 20 * fall, "arm_r0": -25 * kneel + 30 * fall, "arm_r1": 20 * fall,
                "~jaw": (0.0, 0.02 * kneel, 1.0 + 0.3 * kneel), "~head": (0.0, 0.03 * kneel)}
        rows["death"].append(shot(pose, {"sy": 1.0 - 0.18 * kneel, "rot": -82 * fall, "dx": 0.12 * fall, "dy": -bounce - 0.13 * fall, "pivot": (0.5, 0.86)}))
    return rows


if __name__ == "__main__":
    r = build()
    r.debug("tools/_hd_raw/rig_golem.png")
    bake.emit("sprites/enemy_boss_trash_golem.png", frames(r), 84.0, 12, "босс_мусорный_голем")
