#!/usr/bin/env python3
"""Пул процессов ботов с защитой процессора и живым статусом.
- Не даёт свободному ЦП упасть ниже MIN_IDLE: при нехватке ставит процессы на паузу (SIGSTOP), потом продолжает (SIGCONT).
- Новые процессы стартуют, только если свободно с запасом.
- Пишет прогресс в консоль и в tools/_bot_runs/STATUS.md (смотреть: cat tools/_bot_runs/STATUS.md)."""
import os, re, signal, subprocess, time, threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GODOT = os.environ.get("GODOT", os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/Godot Engine/Godot.app/Contents/MacOS/Godot"))
STATUS = os.path.join(ROOT, "tools", "_bot_runs", "STATUS.md")
MIN_IDLE = float(os.environ.get("BOT_MIN_IDLE", "10"))   # % свободного ЦП, ниже которого ставим ботов на паузу
START_IDLE = MIN_IDLE + 8                                 # стартуем новый процесс, только если свободно столько


def cpu_idle():
    """Свободный ЦП в % (по системе в целом, как в «Мониторинге системы»)."""
    try:
        out = subprocess.run(["top", "-l", "2", "-n", "0", "-s", "1"], capture_output=True, text=True, timeout=10).stdout
        m = re.findall(r"([\d.]+)% idle", out)
        return float(m[-1]) if m else 50.0
    except Exception:
        return 50.0


def godot_cmd(skill, seed, runs, out, heroes="all", brain=None, danger=0):
    cmd = ["nice", "-n", "15", GODOT, "--headless", "--fixed-fps", "60", "--path", ROOT, "res://tools/bot/bot_runner.tscn", "--",
           f"--skill={skill}", f"--seed={seed}", f"--runs={runs}", f"--heroes={heroes}", f"--out={out}", f"--danger={danger}"]
    if brain:
        cmd.append(f"--brain={brain}")
    return cmd


class Pool:
    """jobs: список (cmd, log_path, label). progress(done, total) -> строка для статуса (по желанию)."""

    def __init__(self, title, max_jobs=4, extra_status=None):
        self.title, self.max_jobs, self.extra = title, max_jobs, extra_status
        self.t0 = time.time()

    def _write_status(self, done, total, running, paused, idle, note=""):
        el = time.time() - self.t0
        eta = (el / done * (total - done)) if done else 0
        lines = [f"# {self.title}", "",
                 f"- обновлено: {time.strftime('%H:%M:%S')}",
                 f"- пачек готово: {done}/{total} ({100 * done // max(total, 1)}%)",
                 f"- идёт процессов: {running}, на паузе (бережём ЦП): {paused}",
                 f"- свободно ЦП: {idle:.0f}% (порог {MIN_IDLE:.0f}%)",
                 f"- прошло: {el / 60:.0f} мин, осталось примерно: {eta / 60:.0f} мин"]
        if self.extra:
            lines += ["", self.extra()]
        if note:
            lines += ["", note]
        os.makedirs(os.path.dirname(STATUS), exist_ok=True)
        open(STATUS, "w").write("\n".join(lines) + "\n")

    def run(self, jobs):
        queue = list(jobs)
        total = len(queue)
        running = []   # [proc, label, paused]
        done = 0
        last_print = 0
        idle = cpu_idle()
        while queue or running:
            for item in running[:]:
                if item[0].poll() is not None:
                    running.remove(item); done += 1
            idle = cpu_idle()
            active = [r for r in running if not r[2]]
            paused = [r for r in running if r[2]]
            if idle < MIN_IDLE and active:
                active[-1][2] = True; os.kill(active[-1][0].pid, signal.SIGSTOP)
            elif idle > START_IDLE and paused:
                paused[0][2] = False; os.kill(paused[0][0].pid, signal.SIGCONT)
            elif idle > START_IDLE and queue and len(active) < self.max_jobs and not paused:
                cmd, log, label = queue.pop(0)
                running.append([subprocess.Popen(cmd, stdout=open(log, "w"), stderr=subprocess.STDOUT), label, False])
            n_paused = sum(1 for r in running if r[2])
            self._write_status(done, total, len(running) - n_paused, n_paused, idle)
            if time.time() - last_print > 20:
                last_print = time.time()
                el = time.time() - self.t0
                eta = f", осталось ~{el / done * (total - done) / 60:.0f} мин" if done else ""
                print(f"[{time.strftime('%H:%M:%S')}] {self.title}: {done}/{total} пачек, процессов {len(running) - n_paused} (+{n_paused} на паузе), свободно ЦП {idle:.0f}%{eta}", flush=True)
                if self.extra:
                    print("    " + self.extra().replace("\n", "\n    "), flush=True)
            time.sleep(2)
        self._write_status(done, total, 0, 0, idle, "ГОТОВО")
