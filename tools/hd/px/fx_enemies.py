"""Враги из заготовок FLUX (tools/_hd_raw/fx/enemy_<id>_<n>.png, описания - tools/hd/bible.py). Скелет по силуэту, у каждого своя смерть.
PICK: id -> номер заготовки (после просмотра глазами и сверки с лором)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import auto

BLOOD = (0.80, 0.04, 0.08)
VOMIT = (0.55, 0.92, 0.12)
BROWN = (0.42, 0.26, 0.06)
GREY = (0.45, 0.45, 0.5)
P = "tools/_hd_raw/fx/"
TEXEL = 1.0 / 3.0
# id: (размер фигуры в мировых единицах, смерть, цвет брызг, летун)
E = {
    "squid_gopnik": (40, "burst", BLOOD, False), "microbe": (38, "melt", VOMIT, False), "npc_bot": (34, "burst", GREY, False),
    "cockroach": (30, "burst", BROWN, False), "wifi_ghost": (36, "dissolve", VOMIT, True), "chaser": (30, "burst", BLOOD, True),
    "charger": (46, "burst", BLOOD, False), "spitter": (38, "burst", VOMIT, False), "bruiser": (48, "headpop", BLOOD, False),
    "looter": (34, "headpop", BLOOD, False), "healer": (36, "headpop", BLOOD, False), "blinker": (36, "dissolve", BLOOD, False),
    "thief": (32, "headpop", BLOOD, False), "shield_bearer": (40, "headpop", BLOOD, False), "mirror": (40, "burst", GREY, False),
    "egg": (34, "burst", VOMIT, False), "mamka": (46, "burst", BLOOD, False), "glutton": (46, "burst", VOMIT, False),
    "trash_bin": (36, "burst", BROWN, False),
}
PICK = {}


def spec(id_):
    w, death, goo, fly = E[id_]
    F = int(round(w * 1.5 / TEXEL / 8.0)) * 8                      # кадр с запасом на замахи и разлёт кусков
    return {"id": "enemy_" + id_, "src": "%senemy_%s_%d.png" % (P, id_, PICK.get(id_, 1)), "title": "враг_" + id_, "world_w": float(w), "F": F, "texel": TEXEL, "fit": 0.66,
            "death": death, "goo": goo, "fly": fly, "lift": 8.0 if fly else 0.0, "auto": True, "seed": (sum(map(ord, id_)) % 5) + 1, "head_y": 0.3}


if __name__ == "__main__":
    for id_ in (sys.argv[1:] or list(E)):
        auto.run(spec(id_))
