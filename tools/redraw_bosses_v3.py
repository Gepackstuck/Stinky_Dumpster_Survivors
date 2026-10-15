#!/usr/bin/env python3
"""Боссы v3: лист 4 кадра × ряд на состояние. python3 tools/redraw_bosses_v3.py [--apply]"""
import sys
sys.path.insert(0, "tools")
import boss_hamster, boss_zakhar, boss_minion
BOSSES = {"boss_mega_hamster": boss_hamster, "boss_zakhar": boss_zakhar, "boss_minion": boss_minion}
if __name__ == "__main__":
    for n, m in BOSSES.items():
        im = m.build(); im.save(f"tools/_preview/enemies_v2/enemy_{n}.png"); print(n, im.size, len(m.ROWS), "rows")
        if "--apply" in sys.argv: im.save(f"assets/sprites/enemy_{n}.png")
