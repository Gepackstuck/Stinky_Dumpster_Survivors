"""Списки id из библии (tools/hd/bible.py) для сборщиков."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bible

HEROES = list(bible.HEROES)
ENEMIES = list(bible.ENEMIES)
BOSSES = list(bible.BOSSES)
