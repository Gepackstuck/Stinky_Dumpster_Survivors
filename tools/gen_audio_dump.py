#!/usr/bin/env python3
"""ПОМОЙНЫЙ ОРКЕСТР: все мерзкие звуки новой рисовки настроены в одну тональность (ре минор, пентатоника D F G A C), поэтому пердёж,
отрыжка, рвота, хлюпанье поноса и червей звучат вместе как музыка, а не как каша. Высота у каждого звука - нота лада:
пердёж - бас (D2..D3), отрыжка - тенор, икота и капли - верх, кости - ксилофон, бутылки - колокольчики.
Отдельно: kill_note (костяная маримба с мокрой атакой) - игра играет её выше и выше за серию убийств (арпеджио бойни),
worms/amb_dump - фон помойки (гул ре-ля, мухи, черви, далёкие пьяные стоны в ладу), dump_a/b/c и dump_boss - боевая музыка из тех же «инструментов».
Запуск: PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_audio_dump.py"""
import numpy as np

import gen_audio as G
from gen_audio import SR, N, T, TAU, filt, noise, save, gate, sweep, phase, reverb, midi, Song

R = np.random.default_rng(1313)
# ре минорная пентатоника по октавам (midi): D F G A C
PENTA = [38, 41, 43, 45, 48, 50, 53, 55, 57, 60, 62, 65, 67, 69, 72, 74, 77, 79, 81, 84, 86, 89, 91, 93]


def harm(ph, k_max, roll=0.7, f0=100.0, formants=()):
    """Сумма гармоник с формантами (горло/кишка): formants = [(центр Гц, ширина, усиление)]."""
    x = 0.0
    for k in range(1, k_max + 1):
        if f0 * k > SR * 0.42:
            break
        a = k ** -roll
        for c, w, g in formants:
            a *= 1.0 + g * np.exp(-((f0 * k - c) / w) ** 2)
        x = x + a * np.sin(k * ph)
    return x


def drops(n, count, notes, r, vol=(0.2, 0.6), t0=0.05, t1=0.95):
    """Капли/хлюпы, каждая - нота лада: короткий синус с «плюхом» вверх."""
    out = np.zeros(n)
    for _ in range(count):
        j = int(r.uniform(t0, t1) * n); d = N(r.uniform(0.035, 0.07)); q = T(d)
        f = midi(notes[int(r.integers(len(notes)))])
        seg = np.sin(TAU * f * q * (1 + 0.5 * np.exp(-q / 0.008))) * np.exp(-q / 0.016) * r.uniform(*vol)
        e = min(j + d, n); out[j:e] += seg[:e - j]
    return out


def fart(note, dur, wet=0.3, seed=0):
    """Пердёж-нота: держит высоту (это бас!), дребезжит «губами», в конце сползает на полтона вниз и хлюпает."""
    r = np.random.default_rng(seed)
    n = N(dur); t = T(n); f0 = midi(note)
    bend = 1.0 + 0.35 * np.exp(-t / 0.035) - 0.06 * np.clip((t - dur * 0.7) / (dur * 0.3), 0, 1) ** 2
    f = f0 * bend * (1 + 0.012 * np.sin(TAU * r.uniform(5, 8) * t))
    ph = phase(f, n)
    x = harm(ph, 26, 0.65, f0, ((300, 160, 1.2), (900, 300, 0.6)))
    flut = 0.55 + 0.45 * (np.sin(TAU * (f0 / 2.0) * t + 0.6 * np.sin(TAU * 31 * t)) > -0.25)      # дребезг на пол-частоты: «пр-р-р» в ноту
    x = filt(x * flut, lo=55, hi=2000)
    x += wet * filt(noise(n), lo=400, hi=1800) * np.exp(-t / (dur * 0.4)) * 0.5
    x += drops(n, int(3 + 4 * wet * 3), [74, 77, 81], r, (0.05, 0.16), 0.5, 0.95) * wet * 2.0
    env = np.minimum(t / 0.008, 1.0) * np.clip((dur - t) / 0.06, 0, 1) * (1.0 - 0.25 * t / dur)
    return np.tanh(1.9 * x * env)


def burp(note, dur, seed=0):
    """Отрыжка: поёт ноту, начинается на квинту ниже и въезжает («бу-у-эээ»), горловая форманта."""
    r = np.random.default_rng(seed)
    n = N(dur); t = T(n); f0 = midi(note)
    f = f0 * (1.0 - 0.33 * np.exp(-t / 0.07)) * (1 + 0.05 * np.sin(TAU * 24 * t) * np.exp(-t / (dur * 0.7)))
    ph = phase(f, n)
    c1 = 480 + 250 * np.sin(np.pi * t / dur)                                                       # рот открывается и закрывается
    x = sum(k ** -0.8 * (1 + 2.0 * np.exp(-((f0 * k - c1) / 170) ** 2) + 0.8 * np.exp(-((f0 * k - 1250) / 260) ** 2)) * np.sin(k * ph) for k in range(1, 24))
    x = filt(x, lo=60, hi=2800) * (1 + 0.35 * filt(noise(n), hi=60) * 6)
    return np.tanh(1.7 * x * np.sin(np.pi * np.minimum(t / dur, 1)) ** 0.55)


def puke(seed):
    """Рвота: два позыва - кварта и тоника («уэ-уээ»), плюх на ре и капли по ладу."""
    r = np.random.default_rng(seed)
    n = N(1.55); out = np.zeros(n)
    for c, d, note in ((0.03, 0.26, 55), (0.36, 0.34, 50)):
        m = N(d); q = T(m); f0 = midi(note)
        f = f0 * (1 - 0.18 * q / d) * (1 + 0.07 * np.sin(TAU * 28 * q))
        v = harm(phase(f, m), 18, 0.7, f0, ((650, 200, 1.6), (1100, 260, 0.8)))
        i0 = N(c); out[i0:i0 + m] += filt(v, lo=90, hi=1700) * np.sin(np.pi * q / d) ** 0.7 * 0.8
    i0 = N(0.74); m = n - i0; q = T(m)
    splat = filt(noise(m), lo=180, hi=2200) * np.exp(-q / 0.16) + 0.9 * np.sin(phase(sweep(midi(50), midi(38), m, 0.05), m)) * np.exp(-q / 0.12)
    out[i0:] += splat + drops(m, 11, [62, 65, 69, 72, 74], r, (0.15, 0.5), 0.05, 0.9)
    return np.tanh(1.5 * out)


def squirt(note, seed):
    """Понос: серия мокрых толчков в ноту со сползанием и брызгами (в игре - poop_splat)."""
    r = np.random.default_rng(seed)
    n = N(1.0); out = np.zeros(n); f0 = midi(note)
    for k, c in enumerate((0.0, 0.14, 0.24, 0.42, 0.5)):
        d = N(r.uniform(0.09, 0.16)); q = T(d); i0 = N(c)
        f = f0 * (1.0 if k % 2 == 0 else 0.75) * (1 + 0.5 * np.exp(-q / 0.012))
        seg = np.tanh(2 * harm(phase(f, d), 14, 0.7, f0, ((350, 200, 1.0),))) * np.exp(-q / 0.05) * (0.9 - 0.12 * k)
        seg += filt(noise(d), lo=250, hi=2200) * np.exp(-q / 0.035) * 0.7
        e = min(i0 + d, n); out[i0:e] += seg[:e - i0]
    out += drops(n, 9, [62, 65, 67, 69], r, (0.12, 0.4), 0.3, 0.92)
    return np.tanh(1.5 * filt(out, lo=60, hi=3000))


def hiccup(note, seed):
    r = np.random.default_rng(seed)
    n = N(0.24); t = T(n); f0 = midi(note)
    f = f0 * (0.6 + 0.4 * np.minimum(t / 0.05, 1.0)) * (1 + 0.12 * np.exp(-((t - 0.07) / 0.02) ** 2))
    x = harm(phase(f, n), 10, 0.9, f0, ((900, 300, 1.2),))
    env = np.minimum(t / 0.01, 1) * np.exp(-np.maximum(t - 0.07, 0) / 0.025)
    return np.tanh(1.4 * x * env)


def drunk_moan(notes, seed):
    """Пьяный стон-песня: три ноты лада с завыванием и вибрато, в конце срывается."""
    r = np.random.default_rng(seed)
    dur = 1.5; n = N(dur); t = T(n)
    f = np.zeros(n); seg = n // len(notes)
    for i, m in enumerate(notes):
        f[i * seg:(i + 1) * seg if i < len(notes) - 1 else n] = midi(m)
    f = filt(np.concatenate([np.full(2000, f[0]), f]), hi=6)[2000:]                                 # портаменто между нотами
    f *= 1 + 0.03 * np.sin(TAU * 5.2 * t) * np.clip(t / 0.4, 0, 1) - 0.1 * np.clip((t - 1.25) / 0.25, 0, 1)
    ph = phase(f, n); f0 = midi(notes[0])
    x = sum(k ** -0.9 * (1 + 1.8 * np.exp(-((f0 * k - 420) / 150) ** 2) + 0.7 * np.exp(-((f0 * k - 900) / 200) ** 2)) * np.sin(k * ph) for k in range(1, 22))
    x = filt(x, lo=70, hi=2400) * np.sin(np.pi * t / dur) ** 0.5 * (1 + 0.2 * np.sin(TAU * 13 * t))
    return np.tanh(1.3 * x)


def clink(note, seed):
    """Бутылка: стеклянный колокольчик в ноту (обертоны стекла) + короткий стук."""
    r = np.random.default_rng(seed)
    n = N(0.5); t = T(n); f0 = midi(note)
    x = sum(a * np.sin(TAU * f0 * k * t + r.uniform(0, TAU)) * np.exp(-t / d) for k, a, d in ((1, 1.0, 0.16), (2.76, 0.55, 0.08), (5.4, 0.3, 0.04), (8.9, 0.15, 0.02)) if f0 * k < SR * 0.45)
    x += filt(noise(n), lo=3000) * np.exp(-t / 0.004) * 0.5
    return x * np.minimum(t / 0.001, 1)


def bone(note, dur=0.32, crack=0.5):
    """Кость-ксилофон: деревянный брусок в ноту (обертон 4 и 10) + сухой хруст."""
    n = N(dur); t = T(n); f0 = midi(note)
    x = np.sin(TAU * f0 * t) * np.exp(-t / 0.09) + 0.35 * np.sin(TAU * f0 * 3.93 * t) * np.exp(-t / 0.03) + 0.15 * np.sin(TAU * f0 * 9.2 * t) * np.exp(-t / 0.012)
    x += crack * filt(noise(n), lo=1200, hi=6000) * np.exp(-t / 0.006)
    return x * np.minimum(t / 0.0015, 1)


def kill_note(note=62):
    """Нота убийства: костяная маримба с мокрым шлепком в атаке и коротким хвостом-кварто-квинтой. Игра транспонирует её по ладу."""
    n = N(0.45); t = T(n); f0 = midi(note)
    body = np.sin(TAU * f0 * t) * np.exp(-t / 0.13) + 0.5 * np.sin(TAU * f0 * 2 * t) * np.exp(-t / 0.07) + 0.28 * np.sin(TAU * f0 * 3.93 * t) * np.exp(-t / 0.035)
    sub = 0.6 * np.sin(phase(sweep(f0 * 0.75, f0 * 0.5, n, 0.03), n)) * np.exp(-t / 0.06)
    wet = filt(noise(n), lo=300, hi=2600) * np.exp(-t / 0.02) * 0.55
    return np.tanh(1.2 * (body + sub + wet)) * np.minimum(t / 0.002, 1)


def wet_hit(note, seed):
    """Мокрый шлепок по мясу в ноту: короткий хлюп + низкий «тук»."""
    r = np.random.default_rng(seed)
    n = N(0.16); t = T(n); f0 = midi(note)
    x = filt(noise(n), lo=250, hi=2400) * np.exp(-t / 0.022) * 0.9
    x += np.sin(phase(sweep(f0 * 1.5, f0, n, 0.012), n)) * np.exp(-t / 0.035)
    x += 0.5 * np.sin(TAU * f0 * 0.5 * t) * np.exp(-t / 0.05)
    return np.tanh(1.5 * x) * np.minimum(t / 0.001, 1)


def gore(note, seed):
    """Кровавый взрыв: саб на ре, мокрый разрыв, брызги по ладу, фонтан."""
    r = np.random.default_rng(seed)
    n = N(0.95); t = T(n); f0 = midi(note)
    x = 1.1 * np.sin(phase(sweep(f0 * 2.2, f0, n, 0.035), n)) * np.exp(-t / 0.2)
    x += filt(noise(n), lo=200, hi=3200) * np.exp(-t / 0.07) * 1.0
    x += filt(noise(n), lo=500, hi=2500) * np.exp(-t / 0.4) * (0.5 + 0.5 * np.sin(TAU * 9 * t)) * 0.3      # фонтан
    x += drops(n, 12, [62, 65, 69, 74, 77], r, (0.12, 0.45), 0.12, 0.92)
    return np.tanh(1.6 * x) * np.minimum(t / 0.001, 1)


def worm_layer(n, r, dens=14.0):
    """Черви: мокрое шевеление - много тихих хлюпов-чмоков в ладу + шуршание."""
    out = filt(noise(n), lo=900, hi=2600) * 0.012 * (0.6 + 0.4 * np.sin(TAU * 0.5 * T(n)))
    sec = n / SR
    for _ in range(int(dens * sec)):
        j = int(r.uniform(0, 0.98) * n); d = N(r.uniform(0.03, 0.09)); q = T(d)
        f = midi(PENTA[int(r.integers(8, 16))])
        seg = np.sin(phase(f * (0.5 + 1.2 * q / q[-1]), d)) * np.sin(np.pi * q / q[-1]) ** 2 * r.uniform(0.02, 0.07)
        seg += filt(noise(d), lo=600, hi=2000) * np.sin(np.pi * q / q[-1]) ** 2 * 0.02
        e = min(j + d, n); out[j:e] += seg[:e - j]
    return out


def amb_dump():
    """Фон помойки, 24 с, бесшовный: тёплый гул ре-ля, мухи, черви, редкие стеклянные капли и далёкий пьяный стон в ладу."""
    sec = 24.0; n = N(sec); t = T(n); r = np.random.default_rng(77)
    L = np.zeros(n); Rr = np.zeros(n)
    for f, g in ((36.71, 0.8), (55.0, 0.55), (73.42, 0.5), (110.0, 0.3), (146.83, 0.16), (174.61, 0.1)):   # D1 A1 D2 A2 D3 F3
        ff = round(f * sec) / sec
        for det, side in ((-0.13, 0), (0.0, 2), (0.17, 1)):
            am = 0.65 + 0.35 * np.sin(TAU * round(sec * r.uniform(0.08, 0.2)) / sec * t + r.uniform(0, TAU))
            sig = np.sin(TAU * (ff + det) * t + r.uniform(0, TAU)) * am * g * 0.16
            if side == 0: L += sig
            elif side == 1: Rr += sig
            else: L += 0.6 * sig; Rr += 0.6 * sig
    fl = G.flybuzz(n, 146.83) * 1.3                                              # мухи жужжат на ре
    L += fl * (0.5 + 0.5 * np.sin(TAU * 2 / sec * t)); Rr += np.roll(fl, 9000) * (0.5 + 0.5 * np.cos(TAU * 3 / sec * t))
    L += worm_layer(n, r, 9.0); Rr += worm_layer(n, r, 9.0)
    for k in range(7):                                                           # стеклянные капли-ноты
        x = clink(PENTA[int(r.integers(12, 20))], k) * 0.07; j = int(r.uniform(0.02, 0.9) * n)
        pan = r.uniform(0.2, 0.8); L[j:j + len(x)] += x * pan; Rr[j:j + len(x)] += x * (1 - pan)
    for j0, notes in ((0.18, [57, 60, 57]), (0.62, [62, 60, 57])):               # далёкий стон
        x = filt(drunk_moan(notes, int(j0 * 100)), hi=900) * 0.05; j = int(j0 * n)
        L[j:j + len(x)] += x * 0.7; Rr[j:j + len(x)] += x * 0.4
    x = np.stack([L, Rr])
    x = x + reverb(np.concatenate([x, x[:, :N(3.0)]], 1), 3.0)[:, :n] * 0.9
    fade = N(1.5); w = np.linspace(0, 1, fade)
    x[:, :fade] = x[:, :fade] * w + x[:, -fade:] * (1 - w)
    x = x[:, :-fade]
    save(f"{G.OUT_MUS}/amb_dump.wav", x / np.max(np.abs(x)) * 0.7, stereo=True)


# ---------------- музыка из помойных инструментов ----------------
def i_fart(f, dur, vel=1.0):
    return G.fart_bass(f, dur, vel)


def i_bone(f, dur, vel=1.0):
    n = N(dur + 0.3); t = T(n)
    x = np.sin(TAU * f * t) * np.exp(-t / 0.16) + 0.3 * np.sin(TAU * f * 3.93 * t) * np.exp(-t / 0.04) + 0.25 * filt(noise(n), lo=1500) * np.exp(-t / 0.005)
    return x * vel * np.minimum(t / 0.0015, 1)


def i_burp(f, dur, vel=1.0):
    m = 69 + 12 * np.log2(f / 440.0)
    return burp(m, max(dur, 0.25)) * vel * 0.8


def dump_drums(s, bar, pattern=0, fill=False):
    kicks = ((0, 6, 8), (0, 3, 8, 11), (0, 2, 8, 10))[pattern]
    for st in kicks: s.drum(G.kick(0.95), s.t(bar, st), 0.85, is_kick=True)
    for st in (4, 12):
        s.drum(G.snare(0.8), s.t(bar, st), 0.36, 0, 0.2)
        s.drum(wet_hit(50, st + bar) * 1.2, s.t(bar, st), 0.34, 0.12, 0.15)          # мокрый шлепок в малом
    for st in range(0, 16, 2):
        s.drum(G.hat(vel=0.5 if st % 4 else 0.3), s.t(bar, st), 0.16, 0.3, 0.05)
        if st % 4 == 2: s.drum(bone(86 if st % 8 == 2 else 81, 0.12, 0.8) * 0.5, s.t(bar, st), 0.2, -0.35, 0.2)   # костяной «тик»
    if fill:
        for k, st in enumerate((12, 13, 14, 15)): s.drum(G.tom(130 - 18 * k), s.t(bar, st), 0.32, -0.4 + 0.27 * k, 0.2)


def dump_track(name, bpm, prog, bass_pat, lead, drums=0, lead_inst=None, pad_vowel="o", burps=True, rms=0.13):
    """16 тактов: A (8) без мелодии, B (8) с мелодией. Бас - пердящий, пэд - хор, мелодия - кости/терменвокс, отрыжки на слабых долях в аккорд."""
    s = Song(bpm, 16)
    r = np.random.default_rng(len(name) * 31)
    for bar in range(16):
        root, ch = prog[bar % len(prog)]; sec = bar // 8
        dump_drums(s, bar, drums if sec else 0, fill=bar % 4 == 3)
        for st, semi, ln in bass_pat:
            s.add(i_fart(midi(root - 12 + semi), ln * s.sd * 0.9, 0.9), s.t(bar, st), 0, 0.5 * G.BASS_G, 0.02, 0, True)
        s.chord(s.t(bar, 0), [m + 12 for m in ch], 16 * s.sd, 0.6, lambda f, d, v: G.choir(f, d, v, pad_vowel), 0.065, 0.6, 0.6, True)
        for st in (2, 10):                                                       # костяной аккомпанемент: арпеджио аккорда
            for k, m in enumerate(ch):
                s.add(i_bone(midi(m + 12), 0.3, 0.8), s.t(bar, st + k * 2), -0.3 + 0.3 * k, 0.09, 0.35, 0.25)
        if burps and bar % 2 == 1:
            s.add(i_burp(midi(ch[0] - 12), 0.4, 0.9), s.t(bar, 14), 0.4, 0.1, 0.3)   # отрыжка в тонику аккорда перед сильной долей
        if bar % 4 == 2:
            s.drum(squirt(50, bar)[:N(0.5)], s.t(bar, 7), 0.12, -0.45, 0.25)
        if sec == 1:
            for st, m, ln in lead[bar % len(lead)]:
                inst = lead_inst or G.theremin
                s.add(inst(midi(m), ln * s.sd * 0.95, 0.9), s.t(bar, st), 0.2, 0.15 * G.LEAD_G, 0.4, 0.3)
    extra = np.vstack([worm_layer(s.n, r, 5.0) + G.flybuzz(s.n, 146.83) * 0.5, worm_layer(s.n, r, 5.0)])
    s.render(name, sc=0.35, rev_sec=2.6, rms=rms, wow=0.0015, extra=extra)


def music():
    Dm = (38, [57, 62, 65]); Bb = (34, [58, 62, 65]); Gm = (43, [55, 58, 62]); A = (45, [57, 61, 64]); C = (36, [55, 60, 64]); F = (41, [57, 60, 65])
    walk = [(0, 0, 3), (4, 0, 1), (6, 7, 2), (8, 0, 3), (11, 3, 1), (12, 5, 2), (14, 7, 2)]
    pump = [(st, 12 if st % 8 == 6 else 0, 2) for st in range(0, 16, 2)]
    stomp = [(0, 0, 4), (6, 0, 2), (8, 7, 2), (10, 5, 2), (12, 3, 2), (14, 2, 2)]
    lead_a = [[(0, 74, 4), (4, 77, 2), (6, 76, 2), (8, 74, 4), (12, 69, 4)], [(0, 70, 6), (6, 69, 2), (8, 67, 4), (12, 65, 4)],
              [(0, 67, 4), (4, 70, 4), (8, 74, 6), (14, 72, 2)], [(0, 73, 6), (6, 76, 2), (8, 81, 8)]]
    lead_b = [[(0, 62, 2), (2, 65, 2), (4, 69, 2), (6, 74, 2), (8, 72, 4), (12, 69, 4)], [(0, 70, 2), (2, 69, 2), (4, 65, 4), (8, 62, 8)],
              [(0, 60, 2), (2, 64, 2), (4, 67, 2), (6, 72, 2), (8, 70, 4), (12, 67, 4)], [(0, 69, 4), (4, 73, 4), (8, 76, 8)]]
    lead_c = [[(0, 86, 2), (3, 84, 1), (4, 81, 4), (8, 77, 2), (10, 81, 2), (12, 74, 4)], [(0, 77, 3), (3, 74, 3), (6, 70, 2), (8, 69, 8)],
              [(0, 79, 2), (2, 82, 2), (4, 86, 4), (8, 84, 2), (10, 82, 2), (12, 79, 4)], [(0, 81, 4), (4, 85, 4), (8, 88, 8)]]
    dump_track("dump_a", 100, [Dm, Bb, Gm, A], walk, lead_a, drums=1)
    dump_track("dump_b", 108, [Dm, C, Bb, A], pump, lead_b, drums=2, lead_inst=G.musicbox and (lambda f, d, v: G.musicbox(f * 2, 0.7, v)), pad_vowel="a")
    dump_track("dump_c", 92, [Dm, F, Gm, A], stomp, lead_c, drums=1, lead_inst=lambda f, d, v: i_bone(f, d, v) * 1.6)
    dump_track("dump_boss", 124, [Dm, Bb, C, A], pump, lead_a, drums=2, pad_vowel="a", rms=0.14)


def sfx():
    S = {}
    for i, (note, dur, wet) in enumerate(((38, 0.42, 0.2), (41, 1.1, 0.5), (45, 0.36, 0.25), (48, 1.3, 0.7), (50, 0.3, 0.1))):
        S["fart" + ("" if i == 0 else "_%d" % (i + 1))] = fart(note, dur, wet, 10 + i)
    for i, (note, dur) in enumerate(((50, 0.8), (45, 1.0), (53, 0.6))):
        S["burp" + ("" if i == 0 else "_%d" % (i + 1))] = burp(note, dur, 20 + i)
    for i in range(3):
        S["puke" + ("" if i == 0 else "_%d" % (i + 1))] = puke(30 + i)
    for i, note in enumerate((50, 45, 53)):
        S["poop_splat" + ("" if i == 0 else "_%d" % (i + 1))] = squirt(note, 40 + i)
    for i, note in enumerate((69, 74, 77)):
        S["hiccup" + ("" if i == 0 else "_%d" % (i + 1))] = hiccup(note, 50 + i)
    for i, notes in enumerate(([50, 53, 50], [57, 55, 50], [53, 57, 55])):
        S["drunk_moan" + ("" if i == 0 else "_%d" % (i + 1))] = drunk_moan(notes, 60 + i)
    for i, note in enumerate((86, 93)):
        S["bottle_clink" + ("" if i == 0 else "_%d" % (i + 1))] = clink(note, 70 + i)
    for i, note in enumerate((50, 53, 57)):
        S["wet_hit" + ("" if i == 0 else "_%d" % (i + 1))] = wet_hit(note, 80 + i)
    S["bone_crack"] = bone(81, 0.3, 1.0)
    S["bone_crack_2"] = bone(86, 0.3, 1.0)
    for i, note in enumerate((38, 41)):
        S["gore_burst" + ("" if i == 0 else "_%d" % (i + 1))] = gore(note, 90 + i)
    S["kill_note"] = kill_note(62)
    for k, v in S.items():
        x = v * gate(len(v), len(v) / SR - 0.012, 0.012, 0.0005)
        save(f"{G.OUT_SFX}/{k}.wav", x, 0.85)
    print("dump sfx:", len(S))


if __name__ == "__main__":
    import sys
    what = sys.argv[1:] or ["sfx", "amb", "music"]
    if "sfx" in what: sfx()
    if "amb" in what: amb_dump()
    if "music" in what: music()
