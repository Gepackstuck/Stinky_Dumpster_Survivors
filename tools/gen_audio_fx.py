#!/usr/bin/env python3
"""Свои звуки у каждого оружия (w_<id>.wav), смерти каждого врага (e_<id>.wav) и рёв каждого босса (r_<id>.wav).
Всё синтезом, как в tools/gen_audio.py. Нет файла - игра берёт общий звук (shoot/swing/enemy_death/boss_roar).
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_audio_fx.py -> assets/sfx/"""
import os
import numpy as np
from gen_audio import N, T, TAU, R, filt, noise, gate, sweep, phase, plus, room, save, bell, OUT_SFX


def at(buf, x, sec, gain=1.0):
    s0 = N(sec); e = min(s0 + len(x), len(buf)); buf[s0:e] += x[:e - s0] * gain
    return buf


def ex(n, tau):
    return np.exp(-T(n) / tau)


def nz(sec, lo=None, hi=None):
    return filt(noise(N(sec)), lo=lo, hi=hi)


def whoosh(sec=0.16, lo=400, hi=2800):
    n = N(sec); t = T(n); x = noise(n); y = np.zeros(n); acc = 0.0
    fc = lo + (hi - lo) * np.sin(np.pi * t / t[-1]) ** 2; k = 1 - np.exp(-TAU * fc / SR_)
    for j in range(n): acc += k[j] * (x[j] - acc); y[j] = acc
    return filt(y, lo=200) * np.sin(np.pi * t / t[-1]) ** 1.5


def metal(f, ratios, sec=0.5, decay=0.3):
    n = N(sec); t = T(n)
    return sum(a * np.sin(TAU * f * r * t + R.uniform(0, TAU)) * np.exp(-t / (decay * d)) for r, a, d in ratios)


def clicks(sec, count, lo=2000, hi=9000, gain=1.0):
    out = np.zeros(N(sec))
    for p in np.sort(R.uniform(0, sec * 0.9, count)):
        at(out, nz(0.004, lo, hi) * ex(N(0.004), 0.0012), p, gain * R.uniform(0.5, 1.0))
    return out


def voice(f0, f1, sec, formant=700, tau=0.2, vib=0.0, rough=0.0):
    """Хрип/крик: пила с подъёмом около форманты, вибрато, шершавость."""
    n = N(sec); t = T(n); f = sweep(f0, f1, n, tau) * (1 + vib * np.sin(TAU * 7 * t)); ph = phase(f, n)
    top = int(min(30, (SR_ * 0.4) / max(f0, f1)))
    x = sum(k ** -0.9 * np.sin(k * ph) * (1 + 1.5 * np.exp(-((f0 * k - formant) / (formant * 0.35)) ** 2)) for k in range(1, top))
    if rough: x = x * (1 - rough + rough * np.abs(np.sin(TAU * 31 * t)))
    return filt(x, hi=4000) * gate(n, sec - 0.05, 0.05, 0.01)


SR_ = 32000


# ---------------- оружие ----------------
def weapons():
    W = {}
    # зажигалка: колёсико трёт кремень (трещотка), искра, «фух» пламени
    b = np.zeros(N(0.3)); n = N(0.07)
    rasp = nz(0.07, 2500, 7000) * (0.4 + 0.6 * (np.sin(TAU * 70 * T(n)) > 0.3))
    at(b, rasp, 0.0, 0.8); at(b, clicks(0.05, 4, 4000, 12000), 0.06, 0.9)
    n = N(0.22); at(b, nz(0.22, 150, 1400) * np.minimum(T(n) / 0.03, 1) * ex(n, 0.08), 0.07, 1.0)
    W["lighter"] = b
    # носок: мокрый шлепок дважды и душный выдох
    b = np.zeros(N(0.25))
    for d, g in ((0, 1.0), (0.05, 0.6)): at(b, nz(0.06, 200, 1500) * ex(N(0.06), 0.015) + 0.6 * np.sin(TAU * 120 * T(N(0.06))) * ex(N(0.06), 0.02), d, g)
    at(b, nz(0.18, 100, 600) * np.sin(np.pi * T(N(0.18)) / 0.18) * 0.4, 0.06)
    W["sock"] = b
    # рогатка: резинка дзынькает, камешек свистит
    n = N(0.18); t = T(n)
    tw = np.sin(phase(150 * (1 + 0.3 * np.sin(TAU * 28 * t) * ex(n, 0.05)), n)) * ex(n, 0.05)
    W["slingshot"] = plus(tw, 0.5 * whoosh(0.14, 1500, 4500))
    # швабра: мокрый взмах и плюх
    W["mop"] = at(plus(whoosh(0.2, 300, 1500), np.zeros(N(0.3))), nz(0.12, 300, 2000) * ex(N(0.12), 0.04), 0.14, 0.9)
    # лазерная указка: тонкий «пиу» с биениями
    n = N(0.09); t = T(n)
    W["laser_pointer"] = (np.sin(phase(sweep(2600, 1900, n, 0.05), n)) + np.sin(phase(sweep(2615, 1912, n, 0.05), n))) * ex(n, 0.04) * 0.5
    # тапок: звонкий шлепок резиной
    n = N(0.12); t = T(n)
    W["slipper"] = plus(0.4 * whoosh(0.08, 600, 2500), at(np.zeros(N(0.15)), nz(0.03, 600, 5000) * ex(N(0.03), 0.006) + 0.7 * np.sin(TAU * 260 * T(N(0.03))) * ex(N(0.03), 0.012), 0.06))
    # сгущёнка: выдавливание из банки - бульк-чвяк
    n = N(0.2); t = T(n)
    W["condensed_milk"] = nz(0.2, 400, 2500) * (0.5 + 0.5 * np.sin(TAU * 34 * t)) * ex(n, 0.08) + 0.6 * np.sin(phase(sweep(180, 420, n, 0.04), n)) * ex(n, 0.06)
    # самопал: грубый хлопок с жестяным звоном
    n = N(0.45)
    W["pipe_gun"] = np.tanh(2 * (nz(0.45, None, 3000) * ex(n, 0.04) + 0.8 * np.sin(phase(sweep(110, 50, n, 0.05), n)) * ex(n, 0.08) + 0.25 * metal(900, ((1, 1, 1), (2.4, 0.6, 0.6), (3.9, 0.4, 0.4)), 0.45, 0.2)))
    # арбалет: тетива «тунг» и деревянный стук
    n = N(0.25); t = T(n)
    W["crossbow"] = plus(sum(k ** -1.2 * np.sin(TAU * 110 * k * t) for k in range(1, 8)) * ex(n, 0.06) * 0.6, metal(700, ((1, 1, 1), (2.7, 0.5, 0.5)), 0.08, 0.05) * 0.5, 0.4 * whoosh(0.15, 1200, 4000))
    # сковородка: «бонг»
    W["frying_pan"] = plus(0.4 * whoosh(0.12, 400, 1800), at(np.zeros(N(0.7)), metal(330, ((1, 1, 1), (1.59, 0.7, 0.8), (2.31, 0.5, 0.6), (3.42, 0.35, 0.4), (4.9, 0.2, 0.25)), 0.6, 0.4) * np.minimum(T(N(0.6)) / 0.002, 1), 0.08))
    # скалка: деревянный удар
    W["rolling_pin"] = plus(0.5 * whoosh(0.12, 300, 1500), at(np.zeros(N(0.25)), metal(480, ((1, 1, 1), (2.6, 0.6, 0.5), (4.2, 0.3, 0.3)), 0.12, 0.05) + nz(0.12, 300, 2500) * ex(N(0.12), 0.01), 0.09))
    # тухлый сыр: газ «пфф» и пузыри
    b = np.zeros(N(0.35)); at(b, nz(0.3, 100, 900) * np.sin(np.pi * T(N(0.3)) / 0.3) ** 0.7, 0)
    for d in (0.08, 0.15, 0.24): n = N(0.05); at(b, np.sin(phase(sweep(250, 700, n, 0.01), n)) * ex(n, 0.015), d, 0.5)
    W["rotten_cheese"] = b
    # баллончик: шипение и шарик внутри
    W["spray_can"] = plus(nz(0.12, 3500, 10000) * np.minimum(T(N(0.12)) / 0.01, 1) * ex(N(0.12), 0.06), clicks(0.04, 2, 2500, 6000) * 0.6)
    # бутылка: свист и звон стекла
    W["bottle"] = plus(0.5 * whoosh(0.12, 800, 3000), at(np.zeros(N(0.3)), metal(2200, ((1, 1, 1), (2.6, 0.6, 0.7), (4.1, 0.4, 0.5)), 0.2, 0.08), 0.06))
    # мосинка: хлёсткий выстрел, гул, эхо, затвор
    n = N(0.9); t = T(n); b = np.zeros(N(1.0))
    crack = nz(0.9, 1200, None) * ex(n, 0.008)
    boom = nz(0.9, None, 700) * ex(n, 0.12) + 0.9 * np.sin(phase(sweep(90, 40, n, 0.06), n)) * ex(n, 0.15)
    at(b, room(np.tanh(2.5 * (crack + boom)), 1.4, 0.45), 0)
    for d in (0.55, 0.68): at(b, metal(1800, ((1, 1, 1), (2.3, 0.6, 0.6)), 0.05, 0.02) + nz(0.05, 2000, 8000) * ex(N(0.05), 0.005), d, 0.35)
    W["mosin"] = b
    # вантуз: чавкающий «чпок» и резиновый писк
    n = N(0.18); t = T(n)
    W["plunger"] = np.sin(phase(sweep(160, 900, n, 0.02), n)) * ex(n, 0.03) + 0.3 * nz(0.18, 300, 1500) * ex(n, 0.05) + 0.2 * np.sin(TAU * 1300 * t) * ex(n, 0.04)
    # заточка: короткий скрежет «вжик»
    n = N(0.09)
    W["shiv"] = nz(0.09, 3000, 9000) * np.sin(np.pi * T(n) / 0.09) + 0.3 * np.sin(TAU * 3300 * T(n)) * ex(n, 0.03)
    # лопата: тяжёлый взмах и железный «дзынь»
    W["shovel"] = plus(0.6 * whoosh(0.2, 250, 1300), at(np.zeros(N(0.6)), plus(metal(220, ((1, 1, 1), (2.1, 0.7, 0.6), (3.3, 0.5, 0.4), (4.5, 0.3, 0.25)), 0.4, 0.25), nz(0.08, 200, 2000) * ex(N(0.08), 0.02)), 0.16))
    # горелка: рёв пламени
    n = N(0.16)
    W["blowtorch"] = (nz(0.16, 80, 900) + 0.4 * nz(0.16, 2000, 6000)) * np.sin(np.pi * T(n) / 0.16) ** 0.5
    # шприц: «пшик» и стеклянный тик
    W["syringe"] = plus(nz(0.07, 2500, 9000) * ex(N(0.07), 0.02), metal(3500, ((1, 1, 1), (2.7, 0.4, 0.5)), 0.05, 0.015) * 0.4)
    # консерва-бомба: бросок, жестяной стук, шипит фитиль
    W["tin_bomb"] = plus(0.4 * whoosh(0.12, 500, 2200), at(np.zeros(N(0.4)), metal(700, ((1, 1, 1), (1.7, 0.6, 0.6), (2.9, 0.4, 0.4)), 0.12, 0.05), 0.08), nz(0.4, 4000, 9000) * 0.12)
    # удлинитель: электрический треск
    n = N(0.18); t = T(n)
    W["extension_cord"] = filt(sum(np.sin(TAU * 100 * k * t) / k for k in range(1, 30)), lo=200, hi=5000) * (np.abs(noise(n)) > 0.6) * ex(n, 0.08) + clicks(0.18, 8, 2000, 10000)
    return W


# ---------------- враги ----------------
def enemies():
    E = {}
    E["squid_gopnik"] = plus(voice(190, 120, 0.22, 800, 0.08, 0.02, 0.3) * 0.6, nz(0.2, 200, 1500) * ex(N(0.2), 0.06))   # «ыа» + хлюп щупалец
    b = np.zeros(N(0.3))
    for i in range(4): n = N(0.05); at(b, np.sin(phase(sweep(300 + 150 * i, 1100 + 200 * i, n, 0.01), n)) * ex(n, 0.015), i * 0.045, 0.7)
    E["microbe"] = b   # пузыри лопаются
    n = N(0.35); t = T(n)
    E["npc_bot"] = np.sign(np.sin(phase(sweep(900, 120, n, 0.12), n))) * ex(n, 0.12) * 0.5 + clicks(0.35, 5) * 0.5   # робот вырубился
    E["cockroach"] = plus(clicks(0.12, 9, 1500, 8000, 1.2), nz(0.06, 300, 2000) * ex(N(0.06), 0.015))   # хруст панциря
    n = N(0.6); t = T(n)
    E["wifi_ghost"] = room(np.sin(phase(sweep(700, 280, n, 0.25) * (1 + 0.03 * np.sin(TAU * 6 * t)), n)) * gate(n, 0.5, 0.1, 0.03) * 0.6 + nz(0.6, 800, 3000) * 0.15 * ex(n, 0.2), 1.0, 0.5)   # вой призрака
    n = N(0.15); E["chaser"] = plus(filt(sum(np.sin(TAU * 230 * k * T(n)) / k for k in range(1, 10)), hi=3000) * ex(n, 0.03) * 0.4, at(np.zeros(n), nz(0.08, 300, 2500) * ex(N(0.08), 0.02), 0.03))   # муха - жжж-шмяк
    E["charger"] = plus(voice(130, 80, 0.3, 600, 0.1, 0.0, 0.4) * 0.7, np.sin(TAU * 70 * T(N(0.2))) * ex(N(0.2), 0.06))   # тяжёлое «ух»
    b = np.zeros(N(0.3)); at(b, nz(0.25, 300, 2200) * (0.5 + 0.5 * np.sin(TAU * 40 * T(N(0.25)))) * ex(N(0.25), 0.08), 0)
    for d in (0.05, 0.12): n = N(0.05); at(b, np.sin(phase(sweep(200, 600, n, 0.01), n)) * ex(n, 0.02), d, 0.6)
    E["spitter"] = b   # бульк-плевок
    E["bruiser"] = plus(voice(95, 65, 0.5, 500, 0.2, 0.01, 0.5) * 0.8, 1.2 * np.sin(phase(sweep(90, 40, N(0.3), 0.05), N(0.3))) * ex(N(0.3), 0.1))   # стон и грохот
    E["looter"] = plus(voice(220, 160, 0.15, 900, 0.05) * 0.4, sum(at(np.zeros(N(0.35)), metal(2400 + 300 * i, ((1, 1, 1), (2.3, 0.5, 0.5)), 0.1, 0.04), 0.03 + i * 0.06) for i in range(4)) * 0.5)   # «ой» и звон монет
    E["healer"] = plus(voice(330, 250, 0.3, 1000, 0.15) * 0.3, sum(at(np.zeros(N(0.5)), bell(f, 0.2), i * 0.06) for i, f in enumerate((1568, 1318, 1046))) * 0.4)   # вздох и звёздочки вниз
    E["egg"] = plus(clicks(0.1, 7, 2000, 9000, 1.1), at(np.zeros(N(0.3)), nz(0.15, 200, 1200) * ex(N(0.15), 0.05), 0.06))   # скорлупа и слизь
    E["mamka"] = plus(voice(150, 90, 0.5, 650, 0.25, 0.03, 0.3) * 0.7, at(np.zeros(N(0.6)), nz(0.2, 150, 1200) * ex(N(0.2), 0.07), 0.3))   # материнский стон и шлёп
    E["glutton"] = voice(85, 70, 0.55, 450, 0.3, 0.02, 0.7) * (0.6 + 0.4 * np.sin(TAU * 18 * T(N(0.55))))   # отрыжка
    n = N(0.25); E["blinker"] = np.sin(phase(np.linspace(300, 2400, n) ** 1.0, n)) * np.linspace(0.2, 1, n) * gate(n, 0.22, 0.03) * 0.5 + nz(0.25, 2000, 8000) * np.linspace(0, 0.3, n)   # втянуло в портал
    E["shield_bearer"] = plus(metal(400, ((1, 1, 1), (1.8, 0.7, 0.6), (2.9, 0.5, 0.4), (4.4, 0.3, 0.3)), 0.6, 0.3), at(np.zeros(N(0.6)), metal(400, ((1, 0.6, 0.4), (2.2, 0.4, 0.3)), 0.3, 0.15), 0.12))   # щит грохнулся
    b = np.zeros(N(0.5))
    for i in range(12): at(b, metal(R.uniform(2500, 6000), ((1, 1, 1), (2.4, 0.5, 0.5)), 0.12, 0.04), R.uniform(0, 0.15), R.uniform(0.2, 0.5))
    E["mirror"] = plus(b, nz(0.15, 3000, None) * ex(N(0.15), 0.03))   # стекло вдребезги
    E["thief"] = plus(voice(500, 700, 0.15, 1400, 0.03) * 0.5, sum(at(np.zeros(N(0.4)), metal(2600 + 250 * i, ((1, 1, 1),), 0.1, 0.05), 0.1 + i * 0.05) for i in range(3)) * 0.5)   # «эй!» и монеты
    E["trash_bin"] = plus(metal(260, ((1, 1, 1), (1.5, 0.8, 0.7), (2.7, 0.6, 0.5), (3.8, 0.4, 0.3)), 0.6, 0.25), clicks(0.3, 10, 1000, 6000, 0.8))   # бак гремит
    return E


def bosses():
    B = {}
    B["boss_mega_hamster"] = room(voice(420, 260, 0.9, 1500, 0.3, 0.05, 0.3), 1.0, 0.3)          # визгливый рёв
    B["boss_zakhar"] = room(voice(110, 80, 1.0, 600, 0.4, 0.02, 0.4) * (0.7 + 0.3 * (np.sin(TAU * 5 * T(N(1.0))) > 0)), 1.2, 0.3)   # хохот «ха-ха»
    B["boss_rat_queen"] = room(voice(700, 520, 0.8, 2200, 0.2, 0.06, 0.5), 1.0, 0.3)            # крысиный визг
    B["boss_roach_king"] = room(plus(voice(120, 90, 0.9, 700, 0.3, 0.0, 0.6) * 0.6, clicks(0.9, 30, 1500, 7000)), 1.0, 0.3)   # треск хитина
    B["boss_trash_golem"] = room(plus(voice(60, 45, 1.2, 400, 0.5, 0.01, 0.6), metal(150, ((1, 1, 1), (2.3, 0.5, 0.5), (3.1, 0.4, 0.3)), 1.0, 0.5) * 0.5), 1.4, 0.35)   # железный рокот
    n = N(0.9); B["boss_pigeon_papa"] = room(voice(260, 200, 0.9, 900, 0.3, 0.0) * (0.5 + 0.5 * np.sin(TAU * 9 * T(n)) ** 2), 1.0, 0.3)   # голубиное «гррру»
    B["boss_mother_in_law"] = room(voice(380, 300, 1.0, 1100, 0.4, 0.04, 0.2), 1.0, 0.3)       # «ааа!» тёщи
    b = np.zeros(N(1.0)); at(b, np.sin(TAU * 90 * T(N(0.15))) * ex(N(0.15), 0.04) + nz(0.15, None, 1500) * ex(N(0.15), 0.02), 0)
    at(b, bell(1046, 0.5), 0.25, 0.6); at(b, bell(784, 0.6), 0.45, 0.6)
    B["boss_uk"] = room(b, 1.2, 0.35)   # штамп и «дзынь» окошка
    n = N(1.6); t = T(n)
    B["boss_blue_whale"] = room(np.sin(phase(80 + 60 * np.sin(np.pi * t / 1.6) ** 2, n)) * gate(n, 1.4, 0.2, 0.2) + 0.3 * np.sin(phase(160 + 120 * np.sin(np.pi * t / 1.6) ** 2, n)) * gate(n, 1.4, 0.2, 0.2), 2.0, 0.5)   # песня кита
    B["boss_minion"] = room(voice(200, 140, 0.6, 750, 0.2, 0.01, 0.3), 0.8, 0.3)               # «эх, ёлки»
    return B


if __name__ == "__main__":
    os.makedirs(OUT_SFX, exist_ok=True)
    cnt = 0
    for prefix, group in (("w_", weapons()), ("e_", enemies()), ("r_", bosses())):
        for k, v in group.items():
            v = v * gate(len(v), len(v) / SR_ - 0.01, 0.01, 0.0005)
            save(f"{OUT_SFX}/{prefix}{k}.wav", v, 0.8); cnt += 1
    print("fx:", cnt)
