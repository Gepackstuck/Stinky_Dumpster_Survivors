#!/bin/zsh
# Ночной прогон: 1) обучение мозга бота на свежей версии, 2) ферма по каждому герою (бог, задрот, средний, рукожоп).
# Запускать из копии tools/_wt/snap (она не меняется, пока днём правим основной проект). ЦП бережёт pool.py (ночью 30-35% свободно).
# Пример: cd tools/_wt/snap && zsh tools/bot/night.sh
set -e
echo "[$(date +%H:%M)] НОЧЬ: обучение мозга"
/usr/bin/python3 -u tools/bot/train.py --gens ${GENS:-3} --pop 6 --runs 8 --jobs 6
echo "[$(date +%H:%M)] НОЧЬ: ферма по героям"
/usr/bin/python3 -u tools/bot/farm.py --per_hero --plan ${PLAN:-god=8,pro=12,mid=3,noob=1} --jobs 6 --tag night
echo "[$(date +%H:%M)] НОЧЬ: готово"
