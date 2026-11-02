#!/usr/bin/env python3
"""ОБУЧЕНИЕ БОТА: эволюционный подбор «мозга» (весов манёвров) по результатам забегов.
Каждое поколение: несколько кандидатов-мозгов, каждый играет N забегов скиллом pro на одинаковых сидах;
лучшие выживают, от них рождаются мутанты. Лучший мозг пишется в tools/bot/brain.json (его берут все боты).
Без окна, с пониженным приоритетом. Пример: python3 tools/bot/train.py --gens 8 --pop 8 --runs 10 --jobs 6
Оценка (fitness): средняя достигнутая волна + 4 за победу + доля пройденной последней волны + запас ХП."""
import argparse, json, os, random, subprocess, sys, time, glob, statistics
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GODOT = os.environ.get("GODOT", os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/Godot Engine/Godot.app/Contents/MacOS/Godot"))
BRAIN = os.path.join(ROOT, "tools", "bot", "brain.json")
# границы параметров (мин, макс) — совпадают по смыслу с BRAIN_DEFAULT в bot_runner.gd
RANGES = {
    "danger_w": (30, 250), "danger_pad": (10, 70), "proj_w": (1, 20), "edge_w": (10, 200), "wall_w": (50, 500),
    "space_w": (0.0, 0.5), "pickup_w": (0.0, 0.8), "range_w": (0.0, 0.4), "inertia_w": (0, 15), "goal_w": (0, 25),
    "orbit_w": (0, 25), "orbit_flip_sec": (0.8, 6.0), "gap_w": (0, 120), "surround_at": (0.25, 0.8),
    "surround_r": (50, 140), "hp_caution": (0, 3), "melee_bold": (0.1, 1.0),
}
DEFAULT = {"danger_w": 90, "danger_pad": 32, "proj_w": 6, "edge_w": 60, "wall_w": 200, "space_w": 0.12, "pickup_w": 0.25,
           "range_w": 0.08, "inertia_w": 4, "goal_w": 9, "orbit_w": 6, "orbit_flip_sec": 2.5, "gap_w": 40,
           "surround_at": 0.45, "surround_r": 90, "hp_caution": 1.0, "melee_bold": 0.3}


def mutate(b, rate, rng):
    c = dict(b)
    for k, (lo, hi) in RANGES.items():
        if rng.random() < 0.4:
            c[k] = min(hi, max(lo, c[k] + rng.gauss(0, (hi - lo) * rate)))
    return c


def cross(a, b, rng):
    return {k: (a[k] if rng.random() < 0.5 else b[k]) for k in RANGES}


def play(brain_path, out, seed, runs):
    cmd = ["nice", "-n", "15", GODOT, "--headless", "--fixed-fps", "60", "--path", ROOT, "res://tools/bot/bot_runner.tscn", "--",
           "--skill=pro", f"--seed={seed}", f"--runs={runs}", f"--out={out}", f"--brain={brain_path}"]
    with open(os.path.join(out, f"log_{seed}.txt"), "w") as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=3600)


def fitness(out):
    rs = [json.load(open(p)) for p in glob.glob(os.path.join(out, "*.json"))]
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
    ap.add_argument("--runs", type=int, default=10); ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    base = DEFAULT
    if os.path.exists(BRAIN):
        base = {**DEFAULT, **json.load(open(BRAIN))}
    run_dir = os.path.join(ROOT, "tools", "_bot_runs", "train_" + time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(run_dir)
    pop = [base] + [mutate(base, 0.25, rng) for _ in range(a.pop - 1)]
    best, best_fit = base, None
    history = []
    per_proc = max(1, a.runs // 2)
    for g in range(a.gens):
        jobs = []
        dirs = []
        for i, brain in enumerate(pop):
            d = os.path.join(run_dir, f"g{g:02d}_c{i}")
            os.makedirs(d)
            bp = os.path.join(d, "brain.json"); json.dump(brain, open(bp, "w"), indent=1)
            dirs.append(d)
            for k in range(0, a.runs, per_proc):   # одинаковые сиды у всех кандидатов поколения: честное сравнение
                jobs.append((bp, d, 1000 * g + k + 1, min(per_proc, a.runs - k)))
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(lambda j: play(*j), jobs))
        scored = sorted(((fitness(d), i) for i, d in enumerate(dirs)), key=lambda x: -x[0][0])
        (top_fit, top_w, top_n), top_i = scored[0]
        line = f"поколение {g}: лучший {top_fit:.2f} (побед {top_w}/{top_n}), медиана {statistics.median(s[0][0] for s in scored):.2f}"
        print(line, flush=True); history.append(line)
        if best_fit is None or top_fit > best_fit:
            best, best_fit = pop[top_i], top_fit
            json.dump({k: round(v, 3) for k, v in best.items()}, open(BRAIN, "w"), indent=1)
        elite = [pop[i] for _, i in scored[: max(2, a.pop // 4)]]
        rate = 0.25 * (1 - g / max(1, a.gens)) + 0.05
        pop = [best] + elite[1:] + [mutate(cross(rng.choice(elite), rng.choice(elite), rng), rate, rng) for _ in range(a.pop - len(elite))]
    open(os.path.join(run_dir, "TRAIN.md"), "w").write("\n".join(history) + f"\n\nлучший мозг: {json.dumps(best, ensure_ascii=False)}\n")
    print("готово, мозг в", BRAIN)


if __name__ == "__main__":
    main()
