"""ГОТОВАЯ рисовка (тон «В с абсурдом»): все 19 врагов из заготовок tools/_hd_raw/pf (лучшая из двух), скелет находится по силуэту (auto), у каждого своя смерть."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import auto

BLOOD = (0.80, 0.04, 0.08)
VOMIT = (0.55, 0.92, 0.12)
GREY = (0.45, 0.45, 0.5)
P = "tools/_hd_raw/pf/"
# id, файл, ширина (мир. ед.), смерть, цвет брызг, летун
E = [
    ("squid_gopnik", "squid_gopnik_2001", 40, "burst", BLOOD, False), ("spitter", "spitter_2003", 40, "burst", VOMIT, False),
    ("chaser", "chaser_2005", 38, "burst", BLOOD, True), ("microbe", "microbe_2007", 38, "melt", VOMIT, False),
    ("cockroach", "cockroach_2009", 40, "burst", (0.42, 0.26, 0.06), False), ("charger", "charger_2011", 46, "headpop", BLOOD, False),
    ("npc_bot", "npc_bot_2013", 32, "burst", GREY, False), ("bruiser", "bruiser_2015", 44, "headpop", BLOOD, False),
    ("glutton", "glutton_2017", 44, "burst", VOMIT, False), ("healer", "healer_2020", 28, "headpop", BLOOD, False),
    ("looter", "looter_2022", 32, "headpop", BLOOD, False), ("egg", "egg_2023", 36, "burst", VOMIT, False),
    ("wifi_ghost", "wifi_ghost_2026", 34, "dissolve", VOMIT, True), ("mamka", "mamka_2028", 28, "headpop", BLOOD, False),
    ("thief", "thief_2029", 30, "headpop", BLOOD, False), ("shield_bearer", "shield_bearer_2031", 38, "headpop", BLOOD, False),
    ("mirror", "mirror_2034", 32, "burst", GREY, False), ("blinker", "blinker_2035", 32, "dissolve", BLOOD, False),
    ("trash_bin", "trash_bin_2037", 36, "melt", VOMIT, False),
]


def spec(e):
    id_, f, w, death, goo, fly = e
    return {"id": "enemy_" + id_, "src": P + f + ".png", "title": id_ + "_финал", "world_w": float(w), "death": death, "goo": goo, "fly": fly,
            "lift": 8.0 if fly else 0.0, "auto": True, "seed": (sum(map(ord, id_)) % 5) + 1, "head_y": 0.3}


if __name__ == "__main__":
    only = sys.argv[1:]
    for e in E:
        if only and e[0] not in only:
            continue
        auto.run(spec(e))
