#!/bin/bash
# Ферма прогонов: боты играют забеги без окна, параллельно и с пониженным приоритетом (мак не тормозит, мышь/клава не трогаются).
# Использование: tools/bot/farm.sh [забегов_на_скилл=60] [процессов=6] ["noob mid pro"] [герои=all]
# Результаты: tools/_bot_runs/<дата>/*.json и REPORT.md (сводка). Остановить: kill по PID из вывода или pkill -f bot_runner.
set -e
cd "$(dirname "$0")/../.."
RUNS=${1:-60}; JOBS=${2:-6}; SKILLS=${3:-"noob mid pro"}; HEROES=${4:-all}
GODOT=${GODOT:-"$HOME/Library/Application Support/Steam/steamapps/common/Godot Engine/Godot.app/Contents/MacOS/Godot"}
OUT="$PWD/tools/_bot_runs/$(date +%Y%m%d_%H%M%S)"
CHUNK=5
mkdir -p "$OUT/logs"
TASKS="$OUT/tasks.txt"; : > "$TASKS"
SEED=1
for S in $SKILLS; do
  LEFT=$RUNS
  while [ "$LEFT" -gt 0 ]; do
    N=$(( LEFT < CHUNK ? LEFT : CHUNK ))
    echo "$S $SEED $N" >> "$TASKS"
    SEED=$((SEED + 1)); LEFT=$((LEFT - N))
  done
done
echo "ферма: $OUT ($(wc -l < "$TASKS" | tr -d ' ') пачек по $CHUNK, $JOBS процессов)"
export GODOT OUT HEROES
xargs -P "$JOBS" -L 1 bash -c 'nice -n 15 "$GODOT" --headless --fixed-fps 60 --path "$PWD" res://tools/bot/bot_runner.tscn -- --skill=$0 --seed=$1 --runs=$2 --heroes=$HEROES --out="$OUT" > "$OUT/logs/$0_$1.log" 2>&1 || true' < "$TASKS"
/usr/bin/python3 tools/bot/report.py "$OUT"
