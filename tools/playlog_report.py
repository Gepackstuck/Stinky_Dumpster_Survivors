#!/usr/bin/env python3
"""Сводка журнала забегов игрока (scripts/autoload/run_log.gd).
python3 tools/playlog_report.py [дата YYYY-MM-DD | all]  -> таблица по волнам: убийства, заработано, говно, ХП, оружие, покупки."""
import json, os, sys, glob

DIR = os.path.expanduser("~/Library/Application Support/Godot/app_userdata/StinkyDumpsterSurvivors/playlog")
arg = sys.argv[1] if len(sys.argv) > 1 else "all"
files = sorted(glob.glob(f"{DIR}/*.jsonl")) if arg == "all" else [f"{DIR}/{arg}.jsonl"]
runs = {}
for f in files:
    for line in open(f, encoding="utf-8"):
        d = json.loads(line); runs.setdefault(d["run"], []).append(d)
for rid, evs in runs.items():
    head = next((e for e in evs if e["ev"] == "run"), {})
    print(f"\n=== {rid}  герой {head.get('hero')}  опасность {head.get('danger')}  режим {head.get('mode') or 'обычный'}  (говно/XP {head.get('coin_per_xp')}, ХП врагов x{head.get('enemy_hp_mult')})")
    print("волна  тип     убито  зараб  говно  ХП        урон_по_тебе  ур  оружие")
    for e in evs:
        if e["ev"] in ("wave", "end"):
            tag = "КОНЕЦ " + e.get("result", "") if e["ev"] == "end" else ""
            print(f"{e['wave']:>5}  {e['kind']:<7} {e['kills']:>5}  {e['earned']:>5}  {e['coins']:>5}  {e['hp']:>4}/{e['max_hp']:<4}  {e['dmg_taken']:>12}  {e['level']:>2}  {' '.join(e['weapons'])} {tag}")
            if e.get("dealt"):
                top = sorted(e["dealt"].items(), key=lambda kv: -kv[1])[:4]
                print(f"       урон за волну: {', '.join(f'{k} {v}' for k, v in top)}   по тебе: {e.get('taken_by')} ({e.get('hits')} ударов, мин ХП {e.get('hp_min')})   враги ХПx{e.get('enemy_hp_x')} уронx{e.get('enemy_dmg_x')}  fps {e.get('fps')}")
            if e["ev"] == "end":
                print(f"       убийца: {e.get('killer')}  время {e.get('time')}с  урон: " + ", ".join(f"{k} {int(v)}" for k, v in sorted(e.get('damage_by_source', {}).items(), key=lambda kv: -kv[1])[:5]))
        elif e["ev"] == "shop":
            acts = [f"{a['do']} {a.get('id', '')} {a.get('price', '')}".strip() for a in e["actions"]]
            print(f"       ларёк после {e['after_wave']}: {'; '.join(acts)}  (осталось {e['coins_left']})")
