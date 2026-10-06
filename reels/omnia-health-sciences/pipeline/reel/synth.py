"""Procedural cinematic sound-design toolkit (numpy/scipy). 48 kHz."""
import numpy as np, scipy.signal as ss
SR = 48000
rng = np.random.default_rng(1234)

def secs(x): return int(round(x * SR))
def tarr(dur): return np.arange(secs(dur)) / SR
def db(x): return 10 ** (x / 20)

# ---------- filters ----------
def _sos(kind, fc, order=2):
    if kind == "band":
        lo, hi = fc
        return ss.butter(order, [max(lo, 20), min(hi, SR * 0.45)], "band", fs=SR, output="sos")
    return ss.butter(order, min(max(fc, 20), SR * 0.45), kind, fs=SR, output="sos")
def lp(x, fc, order=2): return ss.sosfilt(_sos("low", fc, order), x, axis=0)
def hp(x, fc, order=2): return ss.sosfilt(_sos("high", fc, order), x, axis=0)
def bp(x, lo, hi, order=2): return ss.sosfilt(_sos("band", (lo, hi), order), x, axis=0)

def sweep(x, fc_curve, kind="low", block=128, order=2, q=1.5):
    """time-varying filter by block processing (1-D)."""
    y = np.zeros_like(x); zi = None
    fc_curve = np.broadcast_to(fc_curve, x.shape)
    for s in range(0, len(x), block):
        fc = float(fc_curve[s])
        sos = _sos("band", (fc / q, fc * q), order) if kind == "band" else _sos(kind, fc, order)
        if zi is None: zi = np.zeros((sos.shape[0], 2))
        y[s:s + block], zi = ss.sosfilt(sos, x[s:s + block], zi=zi)
    return y

def biquad(x, kind, f0, gain_db=0.0, Q=0.707):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * Q); c = np.cos(w0)
    if kind == "peak":
        b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
    elif kind == "lowshelf":
        sA = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * c + sA), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sA)]
        a = [(A + 1) + (A - 1) * c + sA, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sA]
    elif kind == "highshelf":
        sA = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * c + sA), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sA)]
        a = [(A + 1) - (A - 1) * c + sA, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sA]
    return ss.lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0)

# ---------- dynamics ----------
def envelope(x, attack=0.005, release=0.12):
    m = np.abs(x) if x.ndim == 1 else np.max(np.abs(x), axis=1)
    a = np.exp(-1 / (attack * SR)); r = np.exp(-1 / (release * SR))
    # one-pole peak follower (vectorised approx: smooth with release then attack)
    e = ss.lfilter([1 - r], [1, -r], m)
    e = np.maximum(e, ss.lfilter([1 - a], [1, -a], m))
    return e

def compress(x, thr_db=-18, ratio=4, attack=0.004, release=0.09, makeup_db=0):
    e = envelope(x, attack, release) + 1e-9
    lvl = 20 * np.log10(e)
    over = np.maximum(0, lvl - thr_db)
    g = db(-over * (1 - 1 / ratio) + makeup_db)
    return x * (g[:, None] if x.ndim == 2 else g)

def limiter(x, ceil_db=-1.0, release=0.06, lookahead=0.003):
    ceil = db(ceil_db)
    m = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    la = secs(lookahead)
    m = np.maximum.accumulate(np.lib.stride_tricks.sliding_window_view(np.pad(m, (0, la)), la + 1).max(axis=1)[None])[0] if False else \
        np.array([0])  # placeholder (replaced below)
    m = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    mm = np.pad(m, (0, la))
    win = np.lib.stride_tricks.sliding_window_view(mm, la + 1).max(axis=1)
    g = np.minimum(1.0, ceil / (win + 1e-9))
    r = np.exp(-1 / (release * SR))
    # smooth gain: instant down, slow up
    gs = np.empty_like(g); cur = 1.0
    for i in range(len(g)):
        cur = g[i] if g[i] < cur else cur * r + g[i] * (1 - r)
        gs[i] = cur
    y = x * (gs[:, None] if x.ndim == 2 else gs)
    return np.clip(y, -ceil, ceil)

# ---------- space ----------
def make_ir(rt60=2.4, predelay=0.02, bright=9000, dark=1800, seed=0, er=10):
    r = np.random.default_rng(seed); dur = rt60 * 1.1; n = secs(dur); t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)) * np.exp(-6.91 * t / rt60)[:, None]
    b = lp(ir, bright); d = lp(ir, dark); w = np.clip(t / (rt60 * 0.6), 0, 1)[:, None]
    ir = b * (1 - w) + d * w
    for k in range(er):
        idx = secs(r.uniform(0.004, 0.07)); ir[idx, r.integers(0, 2)] += r.uniform(0.3, 0.8) * 0.85 ** k
    ir = np.concatenate([np.zeros((secs(predelay), 2)), ir])
    return ir / np.sqrt(np.sum(ir ** 2) / 2)

def convolve(x, ir):
    if x.ndim == 1: x = np.stack([x, x], 1)
    y = np.stack([ss.fftconvolve(x[:, 0], ir[:, 0]), ss.fftconvolve(x[:, 1], ir[:, 1])], 1)
    return y

# ---------- oscillators ----------
def phase(f, n=None, ph0=0.0):
    f = np.broadcast_to(np.asarray(f, float), (n,)) if n is not None else np.asarray(f, float)
    return (np.cumsum(f) / SR + ph0)
def saw(f, n, ph0=0.0): return 2 * (phase(f, n, ph0) % 1.0) - 1
def sine(f, n, ph0=0.0): return np.sin(2 * np.pi * phase(f, n, ph0))
def sq(f, n, ph0=0.0): return np.sign(sine(f, n, ph0))

def stereo(x, width=0.0, pan=0.0):
    if x.ndim == 2: return x
    l = x * np.cos((pan + 1) * np.pi / 4); r = x * np.sin((pan + 1) * np.pi / 4)
    return np.stack([l, r], 1) * np.sqrt(2)

def wide(gen, *a, **k):
    """call a mono generator twice with different randomness -> stereo"""
    return np.stack([gen(*a, **k), gen(*a, **k)], 1)

# ---------- instruments ----------
def boom(dur=2.8, f0=110, f1=31, decay=1.3, drive=2.2, click=0.6):
    n = secs(dur); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.09)
    body = sine(f, n) * np.exp(-t / decay)
    cl = hp(rng.standard_normal(n) * np.exp(-t / 0.004), 1800) * click
    th = lp(rng.standard_normal(n), 160) * np.exp(-t / 0.07) * 2.5
    x = np.tanh(drive * (body + th)) / np.tanh(drive) + cl
    return x * np.minimum(1, t / 0.0015)

def braam(notes, dur=3.2, peak=2400, attack=0.035, decay=2.4, voices=7, detune=16, drive=2.6):
    n = secs(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for f in notes:
        for v in range(voices):
            c = (v - (voices - 1) / 2) / ((voices - 1) / 2) * detune
            x += saw(f * 2 ** (c / 1200), n, rng.random())
    x /= np.sqrt(len(notes) * voices)
    fc = 220 + (peak - 220) * (1 - np.exp(-t / 0.045)) * np.exp(-t / 0.7) + 200 * np.exp(-t / 3)
    x = sweep(x, fc, "low", order=2)
    env = np.minimum(1, t / attack) * np.exp(-t / decay)
    x = np.tanh(drive * x * env) * 0.8
    x += 0.7 * sine(min(notes), n) * env
    return x

def heartbeat(strength=1.0, gap=0.24):
    def thump(f0, f1, dur, dec, nz):
        n = secs(dur); t = np.arange(n) / SR
        f = f1 + (f0 - f1) * np.exp(-t / 0.025)
        x = sine(f, n) * np.exp(-t / dec) + lp(rng.standard_normal(n), 110) * np.exp(-t / 0.025) * nz
        return np.tanh(2.0 * x) * np.minimum(1, t / 0.003)
    out = np.zeros(secs(0.8))
    a = thump(75, 40, 0.45, 0.10, 2.0); b = thump(85, 46, 0.4, 0.08, 1.6) * 0.72
    out[:len(a)] += a; o = secs(gap); out[o:o + len(b)] += b[:len(out) - o]
    return out * strength

def riser(dur, f0=250, f1=9000, shepard=0.3, noise=0.55, curve=1.6):
    n = secs(dur); t = np.arange(n) / SR; p = t / dur
    nz = sweep(rng.standard_normal(n), f0 * (f1 / f0) ** (p ** curve), "band", q=1.35) * p ** 2.4
    sh = np.zeros(n)
    for k in range(7):
        pos = k + 1.5 * p
        sh += np.exp(-0.5 * ((pos - 3.6) / 1.3) ** 2) * sine(55 * 2 ** pos, n, rng.random())
    sh *= 0.15 + 0.85 * p ** 1.8
    return nz * noise + sh * shepard

def whoosh(dur=0.55, lo=250, hi=5000, peak=0.55, width=0.18):
    n = secs(dur); t = np.arange(n) / SR; p = t / dur
    bell = np.exp(-0.5 * ((p - peak) / width) ** 2)
    x = sweep(rng.standard_normal(n), lo * (hi / lo) ** bell, "band", q=1.7) * bell
    return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], 1) * 1.4

def reverse_swell(dur=0.7, lo=2000):
    n = secs(dur); p = np.arange(n) / n
    x = np.stack([hp(rng.standard_normal(n), lo), hp(rng.standard_normal(n), lo)], 1)
    return x * (p ** 3)[:, None]

def tick(f=3000, amp=1.0):
    n = secs(0.015); t = np.arange(n) / SR
    return (0.6 * np.sin(2 * np.pi * f * t) + 0.7 * hp(rng.standard_normal(n), 4500)) * np.exp(-t / 0.0022) * amp

def lock_clunk():
    n = secs(0.25); t = np.arange(n) / SR
    x = 0.8 * sine(180 * np.exp(-t / 0.02) + 90, n) * np.exp(-t / 0.05)
    x += bp(rng.standard_normal(n), 800, 4000) * np.exp(-t / 0.01) * 0.9
    return np.tanh(1.5 * x)

def glitch(dur=1.3, seed=5):
    r = np.random.default_rng(seed); n = secs(dur); x = np.zeros(n); s = 0
    while s < n:
        L = int(r.uniform(0.018, 0.07) * SR); f = r.choice([330, 660, 990, 1320, 1980, 2640, 3960])
        seg = sq(f, L) * r.uniform(0.25, 0.7)
        if r.random() < 0.3: seg *= 0
        if r.random() < 0.3: seg = np.round(r.standard_normal(L) * 3) / 3 * 0.6
        x[s:s + L] += seg[:max(0, min(L, n - s))]; s += L
    x = hp(x, 250)
    hold = 6; x = np.repeat(x[::hold], hold)[:n]  # sample-rate reduction
    return x * 0.45

def tape_stop(x, start, dur):
    """apply tape-stop to stereo buffer x from sample start over dur seconds (in place); silence after."""
    n = secs(dur); rate = np.linspace(1, 0, n) ** 1.4
    pos = start + np.cumsum(rate)
    i0 = np.floor(pos).astype(int); fr = pos - i0
    i0 = np.clip(i0, 0, len(x) - 2)
    seg = x[i0] * (1 - fr)[:, None] + x[i0 + 1] * fr[:, None]
    seg = lp(seg, 6000) * np.linspace(1, 0.2, n)[:, None]
    x[start:start + n] = seg
    return x

def drone(f, dur, bright=500, lfo=0.13):
    n = secs(dur); t = np.arange(n) / SR
    x = saw(f, n, 0.1) + saw(f * 1.0035, n, 0.6) + 0.5 * saw(f * 2 * 0.998, n, 0.3)
    x = sweep(x, bright * (0.6 + 0.8 * (0.5 + 0.5 * np.sin(2 * np.pi * lfo * t))), "low")
    x += 0.9 * sine(f / 2, n)
    return x * 0.28

def pluck_bass(f, dur=0.26, bright=2200):
    n = secs(dur); t = np.arange(n) / SR
    x = saw(f, n) + 0.6 * saw(f * 1.006, n, 0.5)
    x = sweep(x, 160 + bright * np.exp(-t / 0.045), "low", block=48)
    x = x * np.exp(-t / 0.11) * np.minimum(1, t / 0.002)
    x += 0.8 * sine(f / 2, n) * np.exp(-t / 0.14)
    return np.tanh(1.6 * x)

def hat(amp=1.0, dur=0.05):
    n = secs(dur); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t / 0.012) * amp

def taiko(strength=1.0):
    n = secs(1.4); t = np.arange(n) / SR
    x = sine(48 + 75 * np.exp(-t / 0.028), n) * np.exp(-t / 0.38)
    slap = bp(rng.standard_normal(n), 140, 900) * np.exp(-t / 0.03)
    return np.tanh(2.2 * (x + 0.9 * slap)) * strength

def metal_hit(f=150, dur=3.5):
    n = secs(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for i, r in enumerate([1, 2.76, 5.40, 8.93, 13.34, 17.2, 21.1]):
        x += np.sin(2 * np.pi * f * r * t + rng.random() * 6.28) * np.exp(-t / (1.6 / (1 + i * 0.7))) / (1 + i * 0.45)
    x += hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.02) * 0.9
    return x * 0.35

def pad(notes, dur, attack=0.9, release=1.2, cutoff=1500, voices=5, detune=7):
    n = secs(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for f in notes:
        for v in range(voices):
            c = (v - (voices - 1) / 2) * detune
            vib = 1 + 0.0035 * np.sin(2 * np.pi * (4.6 + 0.35 * v) * t + v)
            x += saw(f * 2 ** (c / 1200) * vib, n, rng.random())
    x = lp(x, cutoff, order=4)
    env = np.minimum(1, t / attack) * np.clip((dur - t) / release, 0, 1)
    return x * env / np.sqrt(len(notes) * voices)

def shimmer(notes, dur, decay=2.8):
    n = secs(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for f in notes:
        x += sine(f, n, rng.random()) * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(3, 6) * t))
    return x * np.minimum(1, t / 0.25) * np.exp(-t / decay) / len(notes)

def woodblock(f=1500, amp=1.0):
    n = secs(0.07); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.71 * t)) * np.exp(-t / 0.011) * amp

def projector(dur, rate=24):
    n = secs(dur); t = np.arange(n) / SR; x = np.zeros(n)
    for k in np.arange(0, dur, 1 / rate):
        i = secs(k); c = bp(rng.standard_normal(secs(0.012)), 1200, 5000) * np.exp(-np.arange(secs(0.012)) / SR / 0.003)
        x[i:i + len(c)] += c[:max(0, min(len(c), n - i))] * rng.uniform(0.5, 1.0)
    x += lp(rng.standard_normal(n), 400) * 0.08  # motor rumble
    return x * 0.5

def sub_drop(dur=2.6, f0=72, f1=26):
    n = secs(dur); t = np.arange(n) / SR
    return sine(f1 + (f0 - f1) * np.exp(-t / 0.45), n) * np.exp(-t / 1.3) * np.minimum(1, t / 0.008)

NOTE = {"D0": 18.35, "D1": 36.71, "A1": 55.0, "C2": 65.41, "D2": 73.42, "E2": 82.41, "F2": 87.31, "F#2": 92.5,
        "G2": 98.0, "A2": 110.0, "Bb2": 116.54, "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61,
        "F#3": 185.0, "A3": 220.0, "C4": 261.63, "D4": 293.66, "E4": 329.63, "F#4": 369.99, "A4": 440.0,
        "D5": 587.33, "E5": 659.25, "F#5": 739.99, "A5": 880.0, "D6": 1174.66}
