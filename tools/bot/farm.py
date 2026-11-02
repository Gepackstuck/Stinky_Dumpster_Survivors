#!/usr/bin/env python3
"""Ферма прогонов (без окна, бережёт ЦП, см. pool.py). Сколько забегов на каждый скилл - отдельно:
  python3 tools/bot/farm.py --plan noob=15,mid=40,pro=120 --jobs 4
Результаты: tools/_bot_runs/<дата>/*.json, сводка REPORT.md; прогресс: tools/_bot_runs/STATUS.md."""
import argparse, os, subprocess, sys, time, glob, json
sys.path.insert(0, os.path.dirname(__file__))
from pool import Pool, godot_cmd, ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--plan", default="noob=15,mid=40,pro=120")
ap.add_argument("--jobs", type=int, default=6)
ap.add_argument("--chunk", type=int, default=5)
ap.add_argument("--heroes", default="all")
ap.add_argument("--tag", default="")
ap.add_argument("--danger", type=int, default=0)
ap.add_argument("--per_hero", action="store_true", help="план - на КАЖДОГО героя отдельно (ровно поровну)")
a = ap.parse_args()
out = os.path.join(ROOT, "tools", "_bot_runs", time.strftime("%Y%m%d_%H%M%S") + (("_" + a.tag) if a.tag else ""))
os.makedirs(os.path.join(out, "logs"))
jobs, seed = [], 1
HEROES = ["hobo", "squid", "clerk", "janitor", "uncle_vitya", "blogger", "granny", "courier", "pigeon", "punk", "shawarma",
          "guard", "student", "plumber", "dacha", "skater", "slime", "gopnik_jock", "cat"]
hero_sets = HEROES if a.per_hero else [a.heroes]
for part in a.plan.split(","):
    skill, total = part.split("="); total = int(total)
    for hs in hero_sets:
        n = total
        while n > 0:
            k = min(n, a.chunk)
            jobs.append((godot_cmd(skill, seed, k, out, hs, None, a.danger), os.path.join(out, "logs", f"{skill}_{seed}.log"), f"{skill}:{hs}"))
            seed += 1; n -= k
import random
random.Random(1).shuffle(jobs)   # вперемешку: промежуточный статус сразу по всем героям и скиллам


def live():
    rs = [json.load(open(p)) for p in glob.glob(os.path.join(out, "*_s*_r*.json"))]
    lines = ["Промежуточно (побед / забегов):"]
    for s in ("noob", "mid", "pro", "god"):
        sr = [r for r in rs if r["skill"] == s]
        if sr:
            w = sum(r["result"] == "win" for r in sr)
            lines.append(f"- {s}: {w}/{len(sr)} ({100 * w // len(sr)}%), средняя волна {sum(r['wave'] for r in sr) / len(sr):.1f}")
    return "\n".join(lines)


print(f"ферма: {out}, план {a.plan}, {len(jobs)} пачек", flush=True)
Pool(f"Ферма {a.plan}", a.jobs, live).run(jobs)
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "bot", "report.py"), out])
