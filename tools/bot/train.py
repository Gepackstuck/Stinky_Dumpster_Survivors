#!/usr/bin/env python3
"""ОБУЧЕНИЕ БОТА: эволюционный подбор «мозга» (весов манёвров) по результатам забегов.
Каждое поколение: несколько кандидатов-мозгов, каждый играет N забегов скиллом pro на одинаковых сидах;
лучшие выживают, от них рождаются мутанты. Лучший мозг пишется в tools/bot/brain.json (его берут все боты).
Без окна, с пониженным приоритетом. Пример: python3 tools/bot/train.py --gens 8 --pop 8 --runs 10 --jobs 6
Оценка (fitness): средняя достигнутая волна + 4 за победу + доля пройденной последней волны + запас ХП."""
import argparse, json, os, random, subprocess, sys, time, glob, statistics
sys.path.insert(0, os.path.dirname(__file__))
from pool import Pool, godot_cmd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GODOT = os.environ.get("GODOT", os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/Godot Engine/Godot.app/Contents/MacOS/Godot"))
BRAIN = os.path.join(ROOT, "tools", "bot", "brain.json")
# границы параметров (мин, макс) — совпадают по смыслу с BRAIN_DEFAULT в bot_runner.gd
RANGES = {
    "danger_w": (30, 250), "danger_pad": (10, 70), "proj_w": (2, 40), "hazard_w": (0, 120), "edge_w": (10, 200), "wall_w": (50, 500),
    "space_w": (0.0, 0.5), "pickup_w": (0.0, 0.8), "range_w": (0.0, 0.4), "inertia_w": (0, 15), "goal_w": (0, 25),
    "orbit_w": (0, 25), "orbit_flip_sec": (0.8, 6.0), "gap_w": (0, 120), "surround_at": (0.25, 0.8),
    "surround_r": (50, 140), "hp_caution": (0, 3), "melee_bold": (0.1, 1.0),
    "dash_surround": (0.3, 0.9), "dash_proj_dist": (10, 60), "dash_melee_dist": (8, 40),
}
DEFAULT = {"danger_w": 90, "danger_pad": 32, "proj_w": 10, "hazard_w": 30, "edge_w": 60, "wall_w": 200, "space_w": 0.12, "pickup_w": 0.25,
           "range_w": 0.08, "inertia_w": 4, "goal_w": 9, "orbit_w": 6, "orbit_flip_sec": 2.5, "gap_w": 40,
           "surround_at": 0.45, "surround_r": 90, "hp_caution": 1.0, "melee_bold": 0.3,
           "dash_surround": 0.6, "dash_proj_dist": 28, "dash_melee_dist": 16}


def mutate(b, rate, rng):
    c = dict(b)
    for k, (lo, hi) in RANGES.items():
        if rng.random() < 0.4:
            c[k] = min(hi, max(lo, c[k] + rng.gauss(0, (hi - lo) * rate)))
    return c


def cross(a, b, rng):
    return {k: (a[k] if rng.random() < 0.5 else b[k]) for k in RANGES}


def fitness(out):
    rs = [json.load(open(p)) for p in glob.glob(os.path.join(out, "pro_*.json"))]
    if not rs:
        return -1.0, 0, 0
    sc = []
    for r in rs:
        last = r["waves"][-1] if r["waves"] else {"sec": 0, "min_hp_ratio": 0}
        progress = 1.0 if r["result"] == "win" else min(1.0, last.get("sec", 0) / 90.0)
        sc.append(r["wave"] - 1 + progress + (4 if r["result"] == "win" else 0) + 0.5 * r.get("hp_end_ratio", 0))
    wins = sum(r["result"] == "win" for r in rs)
    return statistics.mean(sc), wins, len(rs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=8); ap.add_argument("--pop", type=int, default=8)
    ap.add_argument("--runs", type=int, default=18); ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    base = DEFAULT
    if os.path.exists(BRAIN):
        base = {**DEFAULT, **json.load(open(BRAIN))}
    run_dir = os.path.join(ROOT, "tools", "_bot_runs", "train_" + time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(run_dir)
    pop = [base] + [mutate(base, 0.25, rng) for _ in range(a.pop - 1)]
    key = lambda b: json.dumps({k: round(v, 4) for k, v in sorted(b.items())})
    evals = {}   # мозг -> все оценки: лидеров переигрываем каждое поколение, отбор по среднему (меньше везения)
    best, best_fit = base, None
    history = []
    per_proc = max(1, a.runs // 3)
    for g in range(a.gens):
        jobs, dirs = [], []
        for i, brain in enumerate(pop):
            d = os.path.join(run_dir, f"g{g:02d}_c{i}")
            os.makedirs(d)
            bp = os.path.join(d, "brain.json"); json.dump(brain, open(bp, "w"), indent=1)
            dirs.append(d)
            for k in range(0, a.runs, per_proc):   # одинаковые сиды у всех кандидатов поколения: честное сравнение
                seed = 1000 * g + k + 1
                jobs.append((godot_cmd("pro", seed, min(per_proc, a.runs - k), d, "all", bp), os.path.join(d, f"log_{seed}.txt"), f"c{i}"))
        status = lambda: "Обучение мозга (оценка = средняя волна + бонусы, по всем переигровкам):\n" + "\n".join("- " + h for h in history[-8:])
        Pool(f"Обучение: поколение {g + 1}/{a.gens}", a.jobs, status).run(jobs)
        for i, d in enumerate(dirs):
            f, w, n = fitness(d)
            evals.setdefault(key(pop[i]), {"brain": pop[i], "fits": [], "wins": 0, "runs": 0})
            e = evals[key(pop[i])]; e["fits"].append(f); e["wins"] += w; e["runs"] += n
        ranked = sorted((evals[key(b)] for b in pop), key=lambda e: -statistics.mean(e["fits"]))
        top = ranked[0]
        line = (f"поколение {g + 1}: лидер {statistics.mean(top['fits']):.2f} (проверок {len(top['fits'])}, побед {top['wins']}/{top['runs']}), "
                f"медиана {statistics.median(statistics.mean(e['fits']) for e in ranked):.2f}")
        print(line, flush=True); history.append(line)
        proven = [e for e in evals.values() if len(e["fits"]) >= 2] or [top]
        champ = max(proven, key=lambda e: statistics.mean(e["fits"]))
        best, best_fit = champ["brain"], statistics.mean(champ["fits"])
        json.dump({k: round(v, 3) for k, v in best.items()}, open(BRAIN, "w"), indent=1)
        elite = [e["brain"] for e in ranked[: max(2, a.pop // 4)]]
        rate = 0.25 * (1 - g / max(1, a.gens)) + 0.05
        pop = elite + [mutate(cross(rng.choice(elite), rng.choice(elite), rng), rate, rng) for _ in range(a.pop - len(elite))]
    open(os.path.join(run_dir, "TRAIN.md"), "w").write("\n".join(history) + f"\n\nлучший мозг: {json.dumps(best, ensure_ascii=False)}\n")
    print("готово, мозг в", BRAIN)


if __name__ == "__main__":
    main()
