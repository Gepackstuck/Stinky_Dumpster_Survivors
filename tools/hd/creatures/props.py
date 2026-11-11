"""Предметы арены в реалистичном стиле: кристалл опыта (сгусток зелёной дряни) и мусорный бак.
Кристалл - один кадр (покачивание и «поворот» делает игра). Бак: walk (1) - стоит, hurt (4) - его мнёт и трясёт от удара."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bake
import rig


def xp() -> None:
    r = rig.Rig(rig.cutout("tools/_hd_raw/t5/xp_212.png"))
    frame = rig.polish(r.render({}, 96, {}, 0.04), gamma=0.6, sat=1.3, rim=0.7)
    bake.emit("sprites/xp_pixel.png", {"idle": [frame]}, 9.0, 8, "кристалл_опыта")


def trash_bin() -> None:
    r = rig.Rig(rig.cutout("tools/_hd_raw/t5/bin_221.png"))
    r.warp("lid", (0.50, 0.22), 0.20).warp("side", (0.45, 0.55), 0.22)
    rows = {"walk": [rig.polish(r.render({}, 224, {}, 0.10))], "hurt": []}
    for k in [1.0, 0.7, 0.4, 0.12]:
        pose = {"~lid": (0.02 * k, -0.03 * k, 1.0, 6 * k), "~side": (0.0, 0.0, 1.0 - 0.06 * k)}
        rows["hurt"].append(rig.polish(r.render(pose, 224, {"rot": -5 * k * math.cos(k * 6.0), "sx": 1.0 + 0.05 * k, "sy": 1.0 - 0.05 * k}, 0.10)))
    bake.emit("sprites/enemy_trash_bin.png", rows, 30.0, 12, "мусорный_бак")


if __name__ == "__main__":
    xp()
    trash_bin()
