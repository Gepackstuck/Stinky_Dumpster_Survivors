#!/usr/bin/env python3
"""Сводка фермы ботов: python3 tools/bot/report.py <папка с *.json> -> печать + REPORT.md в той же папке.
Смотрим на скиллозависимость (победы по уровням), волны смерти, длину забега, «еле выжил», окружения, наборы и героев."""
import json, sys, glob, os, statistics
from collections import Counter, defaultdict

TARGET = {"god": (45, 55), "pro": (25, 35), "mid": (5, 10), "noob": (0, 2)}
SHOP_SEC = 25  # сколько живой игрок в среднем сидит в Ларьке и на карточках за волну


def load(d):
    out = []
    for p in glob.glob(os.path.join(d, "*.json")):
        try:
            out.append(json.load(open(p)))
        except Exception:
            pass
    return out


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def main(d):
    runs = load(d)
    if not runs:
        print("нет прогонов в", d); return
    L = []
    by_skill = defaultdict(list)
    for r in runs:
        by_skill[r["skill"]].append(r)
    L.append(f"# Ферма ботов: {len(runs)} забегов\n")
    L.append("## Скиллозависимость\n")
    L.append("| Скилл | Забегов | Побед | Цель | Медиана волны смерти | Еле выжил (победы с ХП<25%) | Окружён при смерти | Длина победы, мин |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in ["noob", "mid", "pro", "god"]:
        rs = by_skill.get(s, [])
        if not rs:
            continue
        wins = [r for r in rs if r["result"] == "win"]
        deaths = [r for r in rs if r["result"] == "death"]
        med = statistics.median([r["wave"] for r in deaths]) if deaths else "-"
        close = sum(1 for r in wins if r["waves"] and r["waves"][-1]["min_hp_ratio"] < 0.25)
        surr = sum(1 for r in deaths if r.get("surrounded_at_end", 0) >= 0.6)
        dur = statistics.median([(r["game_sec"] + SHOP_SEC * r["wave"]) / 60 for r in wins]) if wins else 0
        lo, hi = TARGET.get(s, (0, 100))
        wr = pct(len(wins), len(rs))
        mark = "ок" if lo <= wr <= hi else ("мало" if wr < lo else "много")
        L.append(f"| {s} | {len(rs)} | {wr:.0f}% | {lo}-{hi}% ({mark}) | {med} | {pct(close, len(wins)):.0f}% | {pct(surr, len(deaths)):.0f}% | {dur:.1f} |")
    L.append("\n## Где умирают (волна: смертей по скиллам)\n")
    waves = sorted({r["wave"] for r in runs if r["result"] == "death"})
    SK = [s for s in ["noob", "mid", "pro", "god"] if s in by_skill]
    L.append("| Волна | " + " | ".join(SK) + " |")
    L.append("|---|" + "---|" * len(SK))
    for w in waves:
        row = [str(sum(1 for r in by_skill[s] if r["result"] == "death" and r["wave"] == w)) for s in SK]
        L.append(f"| {w} | " + " | ".join(row) + " |")
    L.append("\n## Кто убивает (последний удар)\n")
    for k, v in Counter(r["killer"] for r in runs if r["result"] == "death").most_common(10):
        L.append(f"- {k or '?'}: {v}")
    L.append("\n## Герои (pro и mid): победы / забеги\n")
    hero = defaultdict(lambda: [0, 0])
    for r in runs:
        if r["skill"] in ("pro", "mid"):
            hero[r["hero"]][1] += 1
            hero[r["hero"]][0] += r["result"] == "win"
    for h, (w, n) in sorted(hero.items(), key=lambda x: -pct(*x[1])):
        L.append(f"- {h}: {w}/{n} ({pct(w, n):.0f}%)")
    L.append("\n## Наборы оружия у победителей (класс с 3+ оружиями)\n")
    sets = Counter()
    wins_all = [r for r in runs if r["result"] == "win"]
    for r in wins_all:
        for c, n in r.get("sets", {}).items():
            if n >= 3:
                sets[c] += 1
    for c, n in sets.most_common():
        L.append(f"- {c}: {n} из {len(wins_all)} побед")
    if not sets:
        L.append("- побед с наборами 3+ нет")
    L.append("\n## Оружие в финальных билдах (все забеги)\n")
    wc = Counter(w["id"] for r in runs for w in r.get("weapons", []))
    L.append(", ".join(f"{k} {v}" for k, v in wc.most_common()))
    timeouts = sum(1 for r in runs if r["result"] == "timeout")
    if timeouts:
        L.append(f"\n**Таймаутов: {timeouts}** (бот завис - смотреть логи)")
    text = "\n".join(L)
    open(os.path.join(d, "REPORT.md"), "w").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("tools/_bot_runs/*/"))[-1])
