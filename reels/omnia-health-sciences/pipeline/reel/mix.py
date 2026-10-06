"""Build the full soundtrack (music + SFX + processed VO) from timeline.py."""
import numpy as np, soundfile as sf, subprocess, os, sys, json, scipy.signal as ss
import pyloudnorm as pyln
from synth import *
import timeline as TL

OUT = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
WITH_VO = "--novo" not in sys.argv
N = secs(TL.DURATION + 0.01)
music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); vo = np.zeros((N, 2))
send_hall = np.zeros((N, 2)); send_plate = np.zeros((N, 2))

def add(buf, sig, t, gain_db=0.0, pan=0.0, send=None, send_db=-12):
    if sig.ndim == 1: sig = stereo(sig, pan=pan)
    i = secs(t); j = min(N, i + len(sig))
    if i >= N or j <= 0: return
    s0 = max(0, -i); i = max(0, i)
    buf[i:j] += sig[s0:s0 + (j - i)] * db(gain_db)
    if send is not None:
        send[i:j] += sig[s0:s0 + (j - i)] * db(gain_db + send_db)

def fade(sig, fin=0.0, fout=0.0):
    n = len(sig); e = np.ones(n)
    if fin: k = min(n, secs(fin)); e[:k] = np.linspace(0, 1, k)
    if fout: k = min(n, secs(fout)); e[n - k:] *= np.linspace(1, 0, k)
    return sig * (e[:, None] if sig.ndim == 2 else e)

# ---------------- VO ----------------
def process_vo(key):
    src = os.path.join(TL.VO_DIR, f"final_{key}.wav")
    a, sr = sf.read(src)
    a = ss.resample_poly(a, 2, 1)  # 24k -> 48k
    tmp_in, tmp_out = f"/tmp/_vo_{key}_in.wav", f"/tmp/_vo_{key}_out.wav"
    sf.write(tmp_in, a, SR)
    subprocess.run(["rubberband", "-q", "-3", "-F", "-p", "-1.6", tmp_in, tmp_out], check=True)
    b, _ = sf.read(tmp_out)
    b = hp(b, 75, 2)
    b = biquad(b, "lowshelf", 140, 3.0, 0.7)
    b = biquad(b, "peak", 340, -2.5, 1.0)
    b = biquad(b, "peak", 3300, 3.0, 0.8)
    b = biquad(b, "highshelf", 9500, 2.0, 0.7)
    b = b / (np.max(np.abs(b)) + 1e-9) * 0.8
    b = compress(b, thr_db=-16, ratio=3.5, attack=0.003, release=0.08, makeup_db=4)
    b = np.tanh(1.3 * b) / np.tanh(1.3)
    return b

if WITH_VO:
    for key, t in TL.VO.items():
        b = process_vo(key)
        g = -3.0
        if key == "L10": g = -1.5
        if key == "L09": g = -1.5
        add(vo, stereo(b), t, g, send=send_plate, send_db=-15)
        if key in ("L01", "L10", "L09"):
            add(send_hall, stereo(b), t, g - (6 if key == "L10" else 13))

# ---------------- MUSIC / SFX ----------------
D = NOTE
# 0.00 HOOK IMPACT
add(sfx, boom(3.0, 120, 30, 1.4), 0.0, -1.0, send=send_hall, send_db=-10)
add(music, wide(braam, [D["D1"], D["A1"], D["D2"], D["F2"]], 3.4, peak=2600), 0.0, -4.5, send=send_hall, send_db=-8)
add(sfx, metal_hit(110, 3.0), 0.0, -12, send=send_hall, send_db=-6)
# low drone bed through hook, eye & marketing
add(music, fade(stereo(drone(D["D2"], 6.0, 420)), 0.6, 0.4), 0.3, -10)
# heartbeat at 60 bpm in hook/eye
for t in [0.0, 1.0, 2.0, 3.0, 4.0]:
    add(sfx, heartbeat(1.0), t, -4.0 if t > 0 else -6.0)
# counter ticks 0.25 -> T_TRILLION (accelerating), then lock
t = 0.22; step = 0.07
while t < TL.T_TRILLION - 0.03:
    add(sfx, tick(rng.uniform(2600, 3600), 1.0), t, -15, pan=rng.uniform(-0.3, 0.3)); step = max(0.028, step * 0.93); t += step
add(sfx, lock_clunk(), TL.T_TRILLION, -7)
add(sfx, boom(1.2, 90, 40, 0.35, 1.5, 0.3), TL.T_TRILLION, -9)
add(sfx, taiko(0.9), TL.T_CELLS, -9, send=send_hall, send_db=-12)
# into EYE: whoosh + eerie high tones
add(sfx, whoosh(0.5, 300, 6000, 0.6), 2.17, -9)
add(music, fade(stereo(shimmer([D["D6"], D["A5"] * 1.004], 2.0, 3.0)), 0.3, 0.5), 2.5, -24, send=send_hall, send_db=-6)
add(sfx, taiko(0.7), TL.T_TRUST, -14)
add(sfx, reverse_swell(0.55, 2500), 4.25 - 0.55, -15)
# MARKETING: glitch bed, cheesy bright stab (ironic), tape stop
add(sfx, stereo(glitch(1.30)), 4.25, -13)
add(sfx, boom(0.8, 300, 120, 0.12, 2.0, 0.8), 4.25, -12)
add(music, stereo(pluck_bass(D["D3"] * 2, 0.4, 3500) * 0.6), 4.25, -16)
# CRT power-off zap (pairs with the visual squash-to-line)
_n = secs(0.3); _t = np.arange(_n) / SR
zap = sine(1800 * np.exp(-_t / 0.07) + 60, _n) * np.exp(-_t / 0.12) * 0.5 + hp(rng.standard_normal(_n), 3000) * np.exp(-_t / 0.03) * 0.3
add(sfx, zap, 5.42, -16)
add(sfx, tick(1200, 1.0), 5.71, -12)

# 5.75 SCIENTIST: tape stop then silence then braam
# (tape stop applied after building bus, see below)
add(sfx, boom(3.0, 110, 30, 1.6), 5.75, -2.0, send=send_hall, send_db=-9)
add(music, wide(braam, [D["D1"], D["D2"], D["A2"], D["C3"]], 3.4, peak=2000, decay=2.6), 5.75, -6.0, send=send_hall, send_db=-8)
add(music, fade(stereo(drone(D["D2"], 3.4, 600)), 0.5, 0.3), 5.9, -11)
for t in [6.25, 7.25, 8.25]:
    add(sfx, heartbeat(0.9), t, -8)
# TOP 1% slam
add(sfx, metal_hit(147, 3.0), TL.T_TOP, -8, send=send_hall, send_db=-4)
add(sfx, boom(2.0, 140, 35, 0.9), TL.T_TOP, -5)
add(sfx, whoosh(0.35, 500, 7000, 0.85, 0.15), TL.T_TOP - 0.3, -12)

# 8.6-9.0 short riser into PROOF montage
add(sfx, stereo(riser(0.5, 400, 8000, 0.2, 0.6)), 8.5, -10)
# PROOF 9.0 -> 14.75 : ostinato 120bpm 8ths + heartbeat on beats + hats on 16ths
pat = ["D2", "D2", "D2", "F2", "D2", "D2", "C2", "D2", "D2", "D2", "D2", "A1", "D2", "D2", "E2", "F2"]
k = 0; t = 9.0
while t < 14.70:
    pr = (t - 9.0) / 5.75
    n = D[pat[k % len(pat)]]
    add(music, stereo(pluck_bass(n, 0.26, 900 + 2600 * pr)), t, -9 + (3 if k % 4 == 0 else 0) - 2)
    k += 1; t += 0.25
for t in np.arange(9.0, 14.70, 0.5):
    add(sfx, heartbeat(0.8, gap=0.18), t, -11)
for i, t in enumerate(np.arange(9.0, 14.70, 0.125)):
    add(sfx, hat(1.0), t + 0.004, -27 + (4 if i % 2 else 0), pan=(0.25 if i % 2 else -0.25))
add(music, fade(stereo(pad([D["D3"], D["F3"], D["A3"]], 5.9, 1.5, 0.6, 1200)), 0, 0.3), 9.0, -17)
# hits on each proof cut + counters
for cut, land in [(9.0, TL.T_PATENTS - 0.15), (10.5, TL.T_PUBS - 0.2), (12.5, TL.T_CITES - 0.25)]:
    add(sfx, taiko(1.0), cut, -3, send=send_hall, send_db=-10)
    add(sfx, boom(1.6, 100, 34, 0.7, 2.0, 0.4), cut, -6)
    add(sfx, whoosh(0.4, 300, 6000, 0.75, 0.16), cut - 0.32, -11)
    t = cut + 0.05; step = 0.06
    while t < land - 0.02:
        add(sfx, tick(rng.uniform(2800, 3800), 1.0), t, -16, pan=rng.uniform(-0.3, 0.3)); step = max(0.026, step * 0.9); t += step
    add(sfx, lock_clunk(), land, -9)

# 14.75 NOBEL / VINTAGE: projector rattle + clock + strings, ostinato thins
add(sfx, whoosh(0.5, 200, 4000, 0.7), 14.35, -10)
add(sfx, boom(2.2, 90, 30, 1.2), 14.75, -6, send=send_hall, send_db=-10)
add(sfx, fade(stereo(projector(3.75)), 0.05, 0.4), 14.75, -16)
add(music, fade(stereo(pad([D["D3"], D["F3"], D["A3"], D["C4"]], 5.6, 1.4, 0.8, 1800)), 0, 0.2), 14.75, -11, send=send_hall, send_db=-10)
for i, t in enumerate(np.arange(14.75, 18.45, 0.5)):
    add(sfx, woodblock(1650 if i % 2 == 0 else 1250, 1.0), t, -17, pan=(-0.2 if i % 2 == 0 else 0.2))
k = 0
for t in np.arange(15.0, 18.45, 0.25):
    add(music, stereo(pluck_bass(D[pat[k % len(pat)]], 0.22, 900)), t, -15); k += 1
add(sfx, lock_clunk(), TL.T_HARAKEH_CUT, -8)
add(sfx, whoosh(0.35, 300, 5000, 0.8, 0.15), TL.T_HARAKEH_CUT - 0.3, -12)
add(sfx, taiko(0.8), TL.T_NOBEL, -9, send=send_hall, send_db=-12)
# 2x NOBEL slam
add(sfx, metal_hit(196, 3.0), TL.T_TWOTIME, -9, send=send_hall, send_db=-4)
add(sfx, taiko(1.0), TL.T_TWOTIME, -5)
# big riser 16.2 -> 20.15
_r = stereo(riser(20.15 - 16.2, 200, 11000, 0.45, 0.55))
_e = np.ones(len(_r)); _a, _b = secs(18.45 - 16.2), secs(19.95 - 16.2); _e[_a:_b] = db(-4)
_e = ss.lfilter([0.002], [1, -0.998], _e) / ss.lfilter([0.002], [1, -0.998], np.ones(len(_e)))
add(sfx, _r * _e[:, None], 16.2, -7)
# 18.5 CAPSULE: heartbeat accelerating, strings swell
add(sfx, boom(1.8, 100, 32, 0.8), 18.5, -6)
hb = []; t = 18.5; per = 0.5
while t < 20.05:
    hb.append(t); t += per; per = max(0.17, per * 0.82)
for i, t in enumerate(hb):
    add(sfx, heartbeat(0.9 + 0.1 * i / len(hb), gap=min(0.2, 0.4 * (hb[i + 1] - t) if i + 1 < len(hb) else 0.14)), t, -7)
add(music, fade(stereo(pad([D["D3"], D["A3"], D["D4"], D["F3"]], 1.75, 0.6, 0.05, 2600)), 0, 0.02), 18.4, -9)
inhale = reverse_swell(0.24, 1800)

# 20.40 LOGO SLAM (D major resolve)
add(sfx, boom(3.5, 130, 28, 1.8, 2.5, 0.9), TL.T_LOGO, 0.0, send=send_hall, send_db=-8)
add(sfx, sub_drop(3.2, 75, 24), TL.T_LOGO, -2)
add(music, wide(braam, [D["D1"], D["D2"], D["F#2"], D["A2"], D["D3"]], 4.2, peak=2800, decay=3.0), TL.T_LOGO, -5.0, send=send_hall, send_db=-6)
add(sfx, metal_hit(220, 4.0), TL.T_LOGO, -9, send=send_hall, send_db=-3)
add(music, fade(stereo(shimmer([D["D5"], D["F#5"], D["A5"], D["E5"]], 4.0, 3.2)), 0.05, 0.6), TL.T_LOGO + 0.05, -15, send=send_hall, send_db=-3)
add(music, fade(stereo(pad([D["D3"], D["F#3"], D["A3"], D["E4"]], TL.DURATION - TL.T_LOGO - 0.4, 1.2, 1.4, 2200)), 0, 0.8), TL.T_LOGO + 0.4, -12, send=send_hall, send_db=-8)
add(sfx, heartbeat(0.8), 23.55, -11)

# ---------------- bus processing ----------------
bed = music + sfx
# tape stop on the bed at the end of the marketing shot (5.40 -> 5.70), silence until 5.75
i0 = secs(5.42); bed = tape_stop(bed, i0, 0.30); bed[secs(5.72):secs(5.75)] = 0
# sidechain duck bed under VO
if WITH_VO:
    env = envelope(vo, 0.01, 0.25); env = env / (env.max() + 1e-9)
    duck = db(-5.0 * np.clip(env * 3, 0, 1))
    bed *= duck[:, None]
hall = convolve(send_hall + 0.35 * bed * db(-14), make_ir(3.2, 0.03, 7000, 1500, seed=3))[:N]
plate = convolve(send_plate, make_ir(1.1, 0.012, 10000, 3500, seed=9))[:N]
gate = np.ones(N); g0, g1 = secs(20.14), secs(TL.T_LOGO - 0.004)
gate[g0:g1] = 0.0
gate = np.minimum(gate, np.convolve(gate, np.ones(secs(0.012)) / secs(0.012), "same"))
mixd = (bed + hall * db(-3) + plate * db(-6)) * gate[:, None] + vo
ii = secs(TL.T_LOGO - 0.24); mixd[ii:ii + len(inhale)] += inhale[:len(mixd) - ii] * db(-8)
mixd = hp(mixd, 22, 2)
# glue + loudness
mixd = compress(mixd, thr_db=-14, ratio=2.0, attack=0.01, release=0.15)
meter = pyln.Meter(SR)
l = meter.integrated_loudness(mixd)
mixd = mixd * db(-14.0 - l)
mixd = limiter(mixd, -1.0, 0.08)
l2 = meter.integrated_loudness(mixd)
mixd = fade(mixd, 0.0, 0.35)
sf.write(OUT, mixd.astype(np.float32), SR, subtype="FLOAT")
print(f"wrote {OUT} {len(mixd)/SR:.2f}s LUFS in={l:.1f} out={l2:.1f} peak={20*np.log10(np.max(np.abs(mixd))):.2f} dBFS")
