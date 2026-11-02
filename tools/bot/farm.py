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
a = ap.parse_args()
out = os.path.join(ROOT, "tools", "_bot_runs", time.strftime("%Y%m%d_%H%M%S") + (("_" + a.tag) if a.tag else ""))
os.makedirs(os.path.join(out, "logs"))
jobs, seed = [], 1
for part in a.plan.split(","):
    skill, n = part.split("="); n = int(n)
    while n > 0:
        k = min(n, a.chunk)
        jobs.append((godot_cmd(skill, seed, k, out, a.heroes), os.path.join(out, "logs", f"{skill}_{seed}.log"), skill))
        seed += 1; n -= k


def live():
    rs = [json.load(open(p)) for p in glob.glob(os.path.join(out, "*_s*_r*.json"))]
    lines = ["Промежуточно (побед / забегов):"]
    for s in ("noob", "mid", "pro"):
        sr = [r for r in rs if r["skill"] == s]
        if sr:
            w = sum(r["result"] == "win" for r in sr)
            lines.append(f"- {s}: {w}/{len(sr)} ({100 * w // len(sr)}%), средняя волна {sum(r['wave'] for r in sr) / len(sr):.1f}")
    return "\n".join(lines)


print(f"ферма: {out}, план {a.plan}, {len(jobs)} пачек", flush=True)
Pool(f"Ферма {a.plan}", a.jobs, live).run(jobs)
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "bot", "report.py"), out])
