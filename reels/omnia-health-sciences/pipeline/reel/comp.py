#!/usr/bin/env python
"""Omnia reel compositor. Usage: comp.py render <f0> <f1> <out.mp4>  |  comp.py still <t1,t2,...> <out.png>"""
import sys, os, math, numpy as np, cv2
cv2.setNumThreads(1)
import timeline as TL
from fx import *
from fx import _gx, _gy

PL = {}
FA = {}
def plate(key, *fallbacks):
    for k in (key,) + fallbacks:
        if k in PL: return PL[k]
        if os.path.exists(os.path.join(PLATES, f"{k}.png")):
            PL[k] = Plate(k); return PL[k]
    raise FileNotFoundError(key)

LOGO = None
def logo_layers():
    global LOGO
    if LOGO is None:
        Lw, Ld, Lc = np.load(os.path.join(SCR, "logo", "logo_layers.npy")).astype(np.float32)
        LOGO = (Lw, Ld, Lc)
    return LOGO

# ---------------- impacts: flash / shake / chroma / punch ----------------
IMPACTS = [(0.0, 1.0), (TL.T_TRILLION, 0.55), (TL.T_CELLS, 0.25), (2.5, 0.3), (TL.T_TRUST, 0.35), (4.25, 0.55),
           (5.75, 0.9), (TL.T_TOP, 1.0), (9.0, 0.7), (10.5, 0.7), (12.5, 0.7),
           (TL.LAND["patents"], 0.35), (TL.LAND["pubs"], 0.35), (TL.LAND["cites"], 0.35),
           (14.75, 0.5), (TL.T_HARAKEH_CUT, 0.4), (TL.T_TWOTIME, 0.9), (TL.T_NOBEL, 0.45), (18.5, 0.45), (TL.T_LOGO, 1.25)]
HB = TL.capsule_heartbeats()

FLASH_SCALE = {0.0: 0.0, TL.T_LOGO: 1.0}
def impact_state(t, fi):
    fl = sh = ca = pu = 0.0
    for t0, a in IMPACTS:
        if t >= t0 and t - t0 < 0.8:
            fl += a * FLASH_SCALE.get(t0, 0.8) * decay(t, t0, 0.055); sh += a * decay(t, t0, 0.13); ca += a * decay(t, t0, 0.10); pu += a * decay(t, t0, 0.09)
    r = np.random.default_rng(fi + 7)
    return fl, sh * 16 * r.normal(0, 1), sh * 16 * r.normal(0, 1), sh * 0.5 * r.normal(0, 1), ca, pu

def shot_at(t):
    for a, b, k in TL.SHOTS:
        if a <= t < b: return a, b, k
    return TL.SHOTS[-1]

# ---------------- shots ----------------
def s_cells(t, lt, fi):
    p = plate("cells_1", "cells_2")
    e = in_out_sine(lt / 2.6)
    fa = FA.get("cells") or FA.setdefault("cells", FlowAnim(p, "cells"))
    if fa.ok:   # AI video motion (LTX) drives the camera; keep only a gentle drift of our own
        src = fa.src(in_out_sine(lt / 2.5) * 0.85)
        img = p.render(zoom=lerp(1.05, 1.09, e), rot=lerp(0, 0.8, e), src=src)
    else:
        src = p.animate(t, amp=9.0, speed=0.8, weight="near")
        img = p.render(zoom=lerp(1.06, 1.24, e), cx=lerp(0, -18, e), cy=lerp(0, 30, e), rot=lerp(0, 1.2, e), dolly=0.16, px=lerp(-25, 25, e), focus=0.55, src=src)
    img = grade(img, exposure=-0.15, contrast=1.18, sat=1.05, high_tint=(0.03, -0.01, -0.02), shadow_tint=(0.0, 0.0, 0.01))
    img += P_RED.render(t, 0.35)
    scrim = np.exp(-((_gx / 520) ** 2 + ((_gy + 960 - 930) / 330) ** 2))
    img *= (1 - 0.55 * scrim)[..., None]
    # --- text ---
    if t < TL.T_TRILLION:
        final = "37,000,000,000,000"
        r = np.random.default_rng(fi)
        s = []
        for i, ch in enumerate(final):
            settle = 0.30 + 0.62 * (i / len(final)) ** 0.8
            s.append(ch if (ch == "," or t >= settle) else str(r.integers(0, 10)))
        tx = T("".join(s), MO(700, 78))
        draw(img, tx, W / 2, 900, alpha=ramp(t, 0.0, 0.08), glow=0.5, glow_color=RED, ca=2.0)
        lab = T("HUMAN CELLS / ESTIMATED COUNT", MO(400, 24), 0.12)
        draw(img, lab, W / 2, 990, alpha=0.65 * ramp(t, 0.05, 0.2))
    else:
        k = t - TL.T_TRILLION
        sc = lerp(1.22, 1.0, out_expo(k / 0.28))
        big = T("37", FR(600, 400))
        draw(img, big, W / 2, 760, scale=sc, glow=lerp(1.2, 0.35, out_cubic(k / 0.6)), glow_color=RED, ca=lerp(10, 0, out_cubic(k / 0.25)), mblur=lerp(14, 0, out_cubic(k / 0.12)))
        tr = T("TRILLION", OU(800, 118), 0.14)
        draw(img, tr, W / 2, 1010, scale=lerp(1.12, 1.0, out_expo(k / 0.3)), alpha=ramp(k, 0.0, 0.06), glow=0.25, glow_color=RED)
        if t >= TL.T_CELLS:
            c = t - TL.T_CELLS
            ce = T("cells.", FR(400, 150, True))
            n = len(ce.s)
            draw(img, ce, W / 2, 1185, reveal=lambda i: (out_cubic((c - i * 0.045) / 0.22), int(26 * (1 - out_cubic((c - i * 0.045) / 0.22)))), glow=0.6, glow_color=RED)
    return img, dict(bloom=0.45, streak=0.25)

def s_eye(t, lt, fi):
    p = plate("eye_1", "hand_1", "cells_2")
    e = in_out_sine(lt / 1.75)
    dil = 0.05 + 0.32 * out_cubic(ramp(t, TL.T_TRUST - 0.05, TL.T_TRUST + 0.35)) - 0.12 * out_cubic(ramp(t, TL.T_THEM, TL.T_THEM + 0.4))
    src = p.animate(t, amp=2.0, speed=0.5, weight="near", pupil=(p.w * 400 / 768, p.h * 545 / 1344, p.w * 120 / 768, dil))
    img = p.render(zoom=lerp(1.14, 1.26, e), cy=-150, rot=lerp(-0.6, 0.4, e), dolly=0.08, px=lerp(15, -15, e), focus=0.6, src=src)
    img = grade(img, exposure=-0.3, contrast=1.28, sat=0.9, high_tint=(0.012, 0.0, -0.01), shadow_tint=(0.0, 0.0, 0.008))
    spot = np.exp(-(((_gx) / 520) ** 2 + ((_gy + 330) / 420) ** 2))
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    img *= (0.35 + 0.65 * spot)[..., None] * (1 - 0.6 * np.clip((yy - 0.5) / 0.3, 0, 1))[..., None]
    y0 = 1060
    words = [("WHO", TL.word_time("L02", 0)), ("DO", TL.word_time("L02", 1)), ("YOU", TL.word_time("L02", 2))]
    f = OU(700, 84); gap = 0.42 * f.size
    tot_w = sum(T(w_, f, 0.16).ink_w for w_, _ in words) + gap * (len(words) - 1)
    x = W / 2 - tot_w / 2
    for w_, tw in words:        # words rise in on their VO timestamps
        tx = T(w_, f, 0.16)
        k = ramp(t, tw - 0.03, tw + 0.14)
        draw(img, tx, x, y0 + 18 * (1 - out_cubic(k)), alpha=out_cubic(k), anchor="left")
        x += tx.ink_w + gap
    if t >= TL.T_TRUST:
        k = t - TL.T_TRUST
        tr = T("TRUST", FR(600, 250, True))
        draw(img, tr, W / 2, y0 + 205, scale=lerp(1.3, 1.0, out_expo(k / 0.25)), glow=lerp(1.0, 0.3, out_cubic(k / 0.5)), glow_color=RED, ca=lerp(9, 0, out_cubic(k / 0.2)), mblur=lerp(12, 0, out_cubic(k / 0.1)))
    if t >= TL.T_THEM - 0.2:
        k = t - (TL.T_THEM - 0.2)
        wt = T("WITH THEM?", OU(500, 70), 0.28)
        draw(img, wt, W / 2, y0 + 390, alpha=out_cubic(k / 0.25), blur=lerp(8, 0, out_cubic(k / 0.25)))
    return img, dict(bloom=0.35, streak=0.2)

def s_marketing(t, lt, fi):
    p = plate("marketing_1", "journals_1")
    e = out_cubic(lt / 1.5)
    img = p.render(zoom=lerp(1.08, 1.22, e) + 0.004 * math.sin(fi * 2.1), rot=1.5 * math.sin(fi * 0.7) * 0.3, dolly=0.05)
    img = grade(img, exposure=-0.15, contrast=1.25, sat=1.45, gamma=0.95)
    g = 0.0
    if lt < 0.16: g = 1.0 - lt / 0.16
    for s in (4.62, 4.9, 5.18):
        if s <= t < s + 0.07: g = max(g, 0.7)
    img = glitch(img, fi, max(0.12, g), seed=3)
    # dark band behind the type
    yy = np.linspace(0, H, H, dtype=np.float32)[:, None, None]
    img *= 1 - 0.72 * np.exp(-((yy - 945) / 190) ** 2)
    k = t - TL.VO["L03"]
    f = OU(900, 128)
    a1, a2 = T("A MARKETING", f, 0.01), T("TEAM?", f, 0.01)
    r = np.random.default_rng(fi)
    jit = (r.normal(0, 2.5), r.normal(0, 2.5)) if g > 0.3 else (0.0, 0.0)
    for tx, y, delay in ((a1, 880, 0.0), (a2, 1012, 0.10)):
        kk = ramp(k, delay, delay + 0.10)
        draw(img, tx, W / 2 + jit[0], y + jit[1], alpha=kk, ca=(9 if g > 0.3 else 3), scale=lerp(1.12, 1.0, out_expo(kk)), shadow=0.6)
    st = ramp(t, 5.0, 5.18)
    if st > 0:
        for y, tx in ((880, a1), (1012, a2)):
            x0 = W / 2 - tx.ink_w / 2 - 24; x1 = x0 + (tx.ink_w + 48) * out_cubic(st)
            cv2.rectangle(img, (int(x0), int(y - 6)), (int(x1), int(y + 6)), tuple(float(v) for v in RED * 1.25), -1)
    return img, dict(bloom=0.15, streak=0.0, post_crt=True)

def s_founder(key, t, lt, dur, credit_name, credit_sub, top_lines):
    p = plate(key)
    e = in_out_sine(lt / dur)
    img = p.render(zoom=lerp(1.03, 1.11, e), cy=lerp(10, -10, e), dolly=0.10, px=lerp(-14, 14, e), focus=0.5)
    img = grade(img, exposure=0.0, contrast=1.1, sat=0.92)
    img += light_leak(t, seed=11, color=(0.9, 0.16, 0.08), strength=0.10)
    # bottom gradient for credit legibility
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img *= 1 - 0.9 * np.clip((yy - 0.66) / 0.12, 0, 1) ** 1.1
    for txt, f, trk, y, tt in top_lines:
        tx = T(txt, f, trk); k = ramp(t, tt - 0.04, tt + 0.2)
        draw(img, tx, W / 2, y + 16 * (1 - out_cubic(k)), alpha=out_cubic(k), blur=lerp(6, 0, out_cubic(k)))
    ct = TL.VO["L04"] + 1.9 if key == "mousa" else TL.T_COFOUNDER + 0.35
    k = ramp(t, ct, ct + 0.35)
    if k > 0:
        x0 = 82; y = 1430
        cv2.rectangle(img, (x0, y - 2), (int(x0 + 150 * out_cubic(k)), y + 2), tuple(float(c) for c in RED), -1)
        n = T(credit_name, OU(600, 38), 0.22); s = T(credit_sub, OU(400, 29), 0.04)
        draw(img, n, x0, y + 46, alpha=out_cubic(k), anchor="left", shadow=0.8)
        draw(img, s, x0, y + 94, alpha=0.92 * ramp(t, ct + 0.12, ct + 0.45), anchor="left", shadow=0.9)
    return img

def s_mousa(t, lt, fi):
    lines = [("OR A SCIENTIST", OU(600, 62), 0.22, 300, TL.VO["L04"] + 0.05),
             ("IN THE WORLD'S", OU(600, 62), 0.22, 378, TL.word_time("L04", 3))]
    img = s_founder("mousa", t, lt, 3.25, "PROF. SHAKER A. MOUSA", "Founder & CSO  ·  Top 1% scientist (Stanford ranking)", lines)
    if t >= TL.T_TOP:
        k = t - TL.T_TOP
        tp = T("TOP 1%", FR(700, 250))
        draw(img, tp, W / 2, 560, scale=lerp(1.35, 1.0, out_expo(k / 0.3)), glow=lerp(1.4, 0.4, out_cubic(k / 0.7)), glow_color=RED,
             ca=lerp(12, 0, out_cubic(k / 0.25)), mblur=lerp(16, 0, out_cubic(k / 0.12)))
        img, ring = shockwave(img, TL.T_TOP, t, center=(W / 2, 560), speed=2400, width=70, amp=22)
        if isinstance(ring, np.ndarray): img += ring[..., None] * RED * 0.35
    return img, dict(bloom=0.3, streak=0.15)

PROOF = {
    "patents":   dict(plate=("blueprint_1", "molecules_1", "cells_2"), n=400, fmt="{:,}", label="PATENTS", sub="U.S. & INTERNATIONAL", hud="EVIDENCE 01/03"),
    "pubs":      dict(plate=("journals_1", "microscope_1", "cells_2"), n=1000, fmt="{:,}", label="PUBLICATIONS", sub="PEER-REVIEWED", hud="EVIDENCE 02/03"),
    "citations": dict(plate=("network_1", "dna_1", "cells_2"), n=33000, fmt="{:,}", label="CITATIONS", sub="ACROSS GLOBAL SCIENCE", hud="EVIDENCE 03/03"),
}
def s_proof(key, t, lt, fi, a, b):
    cfg = PROOF[key]; p = plate(*cfg["plate"])
    dur = b - a; e = lt / dur
    img = p.render(zoom=lerp(1.1, 1.32, out_cubic(e)), rot=lerp(-2.0, 0.8, e), dolly=0.18, px=lerp(30, -30, e), focus=0.5)
    img = grade(img, exposure=-0.35, contrast=1.15, sat=0.9, high_tint=(0.03, -0.01, -0.02))
    if lt < 0.12: img = radial_blur(img, 0.12 * (1 - lt / 0.12), 6)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img *= 1 - 0.45 * np.exp(-((yy - 0.5) / 0.16) ** 2)   # darken behind numbers
    land = TL.LAND["patents" if key == "patents" else ("pubs" if key == "pubs" else "cites")]
    k = ramp(t, a + 0.04, land)
    val = int(round(cfg["n"] * out_expo(k) if k < 1 else cfg["n"]))
    s = cfg["fmt"].format(val) + ("+" if t >= land else "")
    f = fit_font(cfg["fmt"].format(cfg["n"]) + "+", lambda z: FR(600, z), 900, 330)
    num = T(s, f)
    pop = lerp(1.14, 1.0, out_expo((t - land) / 0.25)) if t >= land else 1.0
    draw(img, num, W / 2, 830, scale=pop, glow=(0.9 if t >= land else 0.35) * (1 - 0.6 * c01((t - land) / 0.6) if t >= land else 1), glow_color=RED,
         ca=(lerp(8, 0, out_cubic((t - land) / 0.2)) if t >= land else 2), mblur=(0 if t >= land else 6))
    lab = T(cfg["label"], fit_font(cfg["label"], lambda z: OU(800, z), 860, 104, 0.14), 0.14)
    kl = ramp(t, a + 0.05, a + 0.3)
    draw(img, lab, W / 2, 1050, alpha=out_cubic(kl), wipe=out_cubic(kl), glow=0.2, glow_color=RED)
    sub = T(cfg["sub"], OU(400, 30), 0.34)
    draw(img, sub, W / 2, 1125, alpha=0.7 * ramp(t, land - 0.05, land + 0.25))
    return img, dict(bloom=0.4, streak=0.3)

def s_harakeh(t, lt, fi):
    if t < TL.T_HARAKEH_CUT:
        lines = [("HIS CO-FOUNDER", OU(600, 66), 0.22, 330, TL.T_COFOUNDER)]
        img = s_founder("harakeh", t, lt, TL.T_HARAKEH_CUT - 14.75, "PROF. STEVE HARAKEH", "Co-Founder & CPO  ·  Former Stanford Medicine researcher", lines)
        return img, dict(bloom=0.3, streak=0.12)
    # vintage lineage
    lt2 = t - TL.T_HARAKEH_CUT; dur = 18.5 - TL.T_HARAKEH_CUT
    p = plate("vintage_1", "labsil_1", "journals_1")
    r = np.random.default_rng(fi * 3 + 1)
    e = in_out_sine(lt2 / dur)
    img = p.render(zoom=lerp(1.08, 1.18, e) + 0.002 * r.normal(), cx=r.normal(0, 1.5), cy=r.normal(0, 2.0), rot=lerp(0.5, -0.5, e), dolly=0.10, px=lerp(-20, 20, e))
    L = (img @ LUMA)[..., None]
    sep = np.concatenate([L * 1.08, L * 0.86, L * 0.62], axis=2)
    img = 0.75 * sep + 0.25 * img
    img = grade(img, exposure=-0.25 + 0.06 * r.normal(), contrast=1.25, sat=1.0, lift=0.02)
    # dust & scratches
    for _ in range(int(r.integers(1, 4))):
        x = int(r.uniform(60, W - 60)); cv2.line(img, (x, 0), (x + int(r.normal(0, 8)), H), (0.75, 0.68, 0.55), 1, cv2.LINE_AA)
    for _ in range(int(r.integers(4, 14))):
        cv2.circle(img, (int(r.uniform(0, W)), int(r.uniform(0, H))), int(r.uniform(1, 4)), (0.05, 0.04, 0.03) if r.random() < 0.6 else (0.9, 0.85, 0.75), -1, cv2.LINE_AA)
    k = ramp(t, TL.T_HARAKEH_CUT, TL.T_HARAKEH_CUT + 0.2)
    wa = T("WORKED ALONGSIDE A", OU(600, 58), 0.22)
    draw(img, wa, W / 2, 470, alpha=out_cubic(k), blur=lerp(6, 0, out_cubic(k)))
    if t >= TL.T_TWOTIME:
        k2 = t - TL.T_TWOTIME
        tw = T("2×", FR(700, 300))
        draw(img, tw, W / 2, 700, scale=lerp(1.35, 1.0, out_expo(k2 / 0.28)), glow=lerp(1.3, 0.45, out_cubic(k2 / 0.6)), glow_color=(1.0, 0.7, 0.35),
             ca=lerp(10, 0, out_cubic(k2 / 0.2)), mblur=lerp(14, 0, out_cubic(k2 / 0.12)))
    if t >= TL.T_NOBEL - 0.05:
        k3 = t - (TL.T_NOBEL - 0.05)
        nl = T("NOBEL LAUREATE", fit_font("NOBEL LAUREATE", lambda z: OU(800, z), 900, 104, 0.12), 0.12)
        draw(img, nl, W / 2, 930, scale=lerp(1.12, 1.0, out_expo(k3 / 0.25)), alpha=ramp(k3, 0, 0.06), glow=0.4, glow_color=(1.0, 0.7, 0.35))
        sm = T("Linus Pauling  ·  Chemistry 1954  ·  Peace 1962", OU(400, 30), 0.06)
        draw(img, sm, W / 2, 1010, alpha=0.75 * ramp(t, TL.T_NOBEL + 0.35, TL.T_NOBEL + 0.7))
    return img, dict(bloom=0.25, streak=0.0, vintage=True)

def s_capsule(t, lt, fi):
    p = plate("capsule_2", "capsule_1")
    dur = 20.15 - 18.5; e = lt / dur
    zoom = lerp(1.06, 1.22, in_out_sine(e)) + 0.9 * in_cubic(ramp(t, 19.7, 20.15)) ** 1.5
    lf = FA.get("capsule_v") or FA.setdefault("capsule_v", LtxFrames(p, "capsule"))
    src = lf.src(e) if lf.ok else None
    img = p.render(zoom=zoom, cy=lerp(230, 160, e) * (1 - in_cubic(ramp(t, 19.7, 20.15))), rot=lerp(0, -2.5, e), dolly=0.12, px=lerp(-20, 20, e), focus=0.6, src=src)
    pulse = 0.0
    for hb in HB:
        pulse += decay(t, hb, 0.12) + 0.6 * decay(t, hb + 0.2, 0.1)
    img = grade(img, exposure=-0.05 + 0.18 * pulse, contrast=1.15, sat=1.05, high_tint=(0.03, -0.01, -0.02))
    img += P_GOLD.render(t, 0.35, converge=(W / 2, H / 2), conv_amt=0.7 * in_cubic(e))
    # light sweep
    sw = ramp(t, 18.9, 19.6)
    if 0 < sw < 1:
        band = np.exp(-(((_gx + W / 2) * 0.6 + (_gy + H / 2) * 0.35 - lerp(-300, 1500, sw)) / 90) ** 2)
        img += band[..., None] * np.array([1.0, 0.85, 0.8], np.float32) * 0.18 * (img @ LUMA)[..., None] * 3
    k1 = ramp(t, TL.T_TOGETHER - 0.03, TL.T_TOGETHER + 0.2)
    draw(img, T("TOGETHER,", OU(600, 66), 0.3), W / 2, 330, alpha=out_cubic(k1), blur=lerp(6, 0, out_cubic(k1)))
    tb = TL.word_time("L09", 2)
    k2 = ramp(t, tb - 0.25, tb)
    draw(img, T("THEY BUILT", OU(800, 112), 0.08), W / 2, 450, alpha=out_cubic(k2), scale=lerp(1.08, 1.0, out_expo(k2)))
    if t >= TL.T_THIS:
        k3 = t - TL.T_THIS
        draw(img, T("this.", FR(600, 210, True)), W / 2, 620, scale=lerp(1.3, 1.0, out_expo(k3 / 0.25)), glow=lerp(1.4, 0.6, out_cubic(k3 / 0.4)), glow_color=RED,
             ca=lerp(10, 0, out_cubic(k3 / 0.2)))
    rb = in_cubic(ramp(t, 19.75, 20.15))
    if rb > 0: img = radial_blur(img, 0.35 * rb, 8)
    img = img + rb ** 2 * 0.6
    return img, dict(bloom=0.5, streak=0.35)

def s_black(t, lt, fi):
    img = np.zeros((H, W, 3), np.float32)
    return img, dict(bloom=0, streak=0, nograin=False)

def s_logo(t, lt, fi):
    e = lt / (TL.DURATION - TL.T_LOGO)
    try:
        p = plate("endbg_1", "cells_1")
        img = p.render(zoom=lerp(1.12, 1.2, e), rot=lerp(0, 0.8, e), dolly=0.05)
        if not os.path.exists(os.path.join(PLATES, "endbg_1.png")):   # bookend: the opening cells, defocused
            sm = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
            img = cv2.resize(cv2.GaussianBlur(sm, (0, 0), 10), (W, H), interpolation=cv2.INTER_LINEAR)
        img = grade(img, exposure=-1.25, contrast=1.1, sat=0.9) * (0.55 + 0.45 * out_cubic(ramp(lt, 0.3, 1.5)))
    except FileNotFoundError:
        img = np.zeros((H, W, 3), np.float32) + np.exp(-((_gy / 900) ** 2 + (_gx / 700) ** 2))[..., None] * RED * 0.12
    img += P_RED.render(t, 0.18)
    Lw, Ld, Lc = logo_layers()
    lw = 800; s = lw / Lw.shape[1]
    k = out_expo(ramp(lt, 0.0, 0.55))
    sc = s * lerp(1.18, 1.0, k)
    def lay(m, scale):
        return cv2.resize(m, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    word = lay(Lw, sc); dia = lay(Ld, sc); crs = lay(Lc, sc)
    h, w = word.shape; cx, cy = W / 2, 860
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    # god rays / glow behind
    glow_amt = lerp(2.2, 0.45, out_cubic(ramp(lt, 0.0, 1.2)))
    canvas = np.zeros((H, W), np.float32); canvas[y0:y0 + h, x0:x0 + w] = np.clip(word + dia, 0, 1)
    gl = cv2.GaussianBlur(cv2.resize(canvas, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 10)
    gl = cv2.resize(gl, (W, H))
    img += gl[..., None] * (0.5 * WHITE + 0.5 * RED) * glow_amt
    rays = radial_blur(np.dstack([canvas] * 3) * 0.6, 0.25, 10, cx, cy)
    img += rays * np.array([1.0, 0.5, 0.45], np.float32) * lerp(1.2, 0.15, out_cubic(ramp(lt, 0, 1.4)))
    # composite wordmark (white), diamond (red, pops in), cross (white)
    alpha_w = ramp(lt, 0.0, 0.05)
    reg = img[y0:y0 + h, x0:x0 + w]
    A = word[..., None] * alpha_w
    reg[:] = reg * (1 - A) + WHITE * A
    dk = out_back(ramp(lt, 0.12, 0.5), 2.2)
    if dk > 0:
        ys_, xs_ = np.where(dia > 0.5)
        dcy, dcx = ys_.mean(), xs_.mean()
        M = cv2.getRotationMatrix2D((dcx, dcy), lerp(-90, 0, out_cubic(ramp(lt, 0.12, 0.5))), max(0.01, dk))
        d2 = cv2.warpAffine(dia, M, (w, h)); c2 = cv2.warpAffine(crs, M, (w, h))
        A = d2[..., None]; reg[:] = reg * (1 - A) + RED * 1.05 * A
        A = c2[..., None]; reg[:] = reg * (1 - A) + WHITE * A
    # light sweep over wordmark
    sw = ramp(lt, 0.55, 1.25)
    if 0 < sw < 1:
        xx = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * 0.4
        band = np.exp(-((xx - lerp(-200, w + 300, sw)) / 45) ** 2)
        reg += (band * word)[..., None] * 0.9
    if lt < 0.6:
        img, ring = shockwave(img, TL.T_LOGO, t, center=(cx, cy), speed=3000, width=110, amp=34)
        if isinstance(ring, np.ndarray): img += ring[..., None] * np.array([1.0, 0.4, 0.35], np.float32) * 0.45
    # tagline
    k1 = t - TL.T_TAGLINE
    if k1 > -0.05:
        tg = T("Beyond Wellness.", FR(400, 66, True))
        draw(img, tg, W / 2, 1110, reveal=lambda i: (out_cubic((k1 - i * 0.025) / 0.3), 0), blur=0)
    k2 = t - (TL.T_WITHIN - 0.05)
    if k2 > 0:
        tg2 = T("Within Biology.", FR(600, 66, True))
        draw(img, tg2, W / 2, 1195, reveal=lambda i: (out_cubic((k2 - i * 0.025) / 0.3), 0), color=np.array([0.95, 0.22, 0.16], np.float32), glow=0.5, glow_color=RED)
    k3 = ramp(t, 23.25, 23.65)
    if k3 > 0:
        url = T("omniahealthsciences.com", OU(500, 34), 0.12)
        draw(img, url, W / 2, 1330, alpha=0.85 * out_cubic(k3))
        lw2 = int(90 * out_cubic(k3))
        for sx in (-1, 1):
            xa = int(W / 2 + sx * (url.ink_w / 2 + 30)); cv2.line(img, (xa, 1330), (xa + sx * lw2, 1330), tuple(float(c) for c in RED), 2, cv2.LINE_AA)
    img *= 1 - 0.5 * ramp(t, TL.DURATION - 0.25, TL.DURATION)
    return img, dict(bloom=0.25, streak=0.15, nohud=True)

P_RED = Particles(70, seed=1, color=(1.0, 0.42, 0.36), speed=(4, -26), size=(1.5, 10))
P_GOLD = Particles(90, seed=2, color=(1.0, 0.75, 0.45), speed=(0, -12), size=(1.2, 7))

HUD = {"cells": "01 — CELLULAR", "eye": "02 — TRUST", "marketing": "02 — TRUST", "mousa": "03 — THE SCIENTIST",
       "patents": "04 — EVIDENCE LEDGER", "pubs": "04 — EVIDENCE LEDGER", "citations": "04 — EVIDENCE LEDGER",
       "harakeh": "05 — LINEAGE", "capsule": "06 — FORMULATION"}

def render_frame(fi):
    t = fi / FPS
    a, b, key = shot_at(t); lt = t - a
    if key == "cells": img, o = s_cells(t, lt, fi)
    elif key == "eye": img, o = s_eye(t, lt, fi)
    elif key == "marketing": img, o = s_marketing(t, lt, fi)
    elif key == "mousa": img, o = s_mousa(t, lt, fi)
    elif key in PROOF: img, o = s_proof(key, t, lt, fi, a, b)
    elif key == "harakeh": img, o = s_harakeh(t, lt, fi)
    elif key == "capsule": img, o = s_capsule(t, lt, fi)
    elif key == "black": img, o = s_black(t, lt, fi)
    else: img, o = s_logo(t, lt, fi)
    fl, dx, dy, rot, ca, pu = impact_state(t, fi)
    if o.get("bloom", 0) or o.get("streak", 0):
        img = bloom(img, 0.62, o.get("bloom", 0), 18, o.get("streak", 0))
    img = chroma(img, 1.2 + 9 * ca)
    img = shake(img, dx, dy, rot, 1 + 0.035 * pu)
    if fl > 0.01: img = img + (1 - np.clip(img, 0, 1)) * min(1.0, fl * 0.75)
    if o.get("post_crt") and t >= 5.42:
        img = crt_off(img, ramp(t, 5.42, 5.72))
    img = vignette(img, 0.5 if o.get("vintage") else 0.38)
    img = grain(img, fi, 0.085 if o.get("vintage") else 0.042)
    if not o.get("nohud") and key != "black":
        hud = HUD.get(key, "")
        draw(img, T(hud, MO(400, 22), 0.08), 70, 212, alpha=0.55, anchor="left")
        tc = "TC 00:00:{:02d}:{:02d}".format(int(t), fi % FPS)
        draw(img, T(tc, MO(400, 22), 0.08), W - 70, 212, alpha=0.45, anchor="right")
        if (fi // 15) % 2 == 0: cv2.circle(img, (W - 70 - T(tc, MO(400, 22), 0.08).ink_w - 22, 212), 6, tuple(float(c) for c in RED * 1.1), -1, cv2.LINE_AA)
    return to8(img)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        ts = [float(x) for x in sys.argv[2].split(",")]
        frames = [render_frame(int(round(x * FPS))) for x in ts]
        thumbs = [cv2.resize(f, (W // 3, H // 3), interpolation=cv2.INTER_AREA) for f in frames]
        cols = 6 if len(thumbs) > 6 else len(thumbs)
        rows = [np.hstack(thumbs[i:i + cols] + [np.zeros_like(thumbs[0])] * (cols - len(thumbs[i:i + cols]))) for i in range(0, len(thumbs), cols)]
        cv2.imwrite(sys.argv[3], np.vstack(rows)[:, :, ::-1])
    elif mode == "full":
        for x in sys.argv[2].split(","):
            cv2.imwrite(sys.argv[3].replace(".png", f"_{x}.png"), render_frame(int(round(float(x) * FPS)))[:, :, ::-1])
    elif mode == "render":
        import subprocess, time
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        t0 = time.time()
        for fi in range(f0, f1):
            pr.stdin.write(render_frame(fi).tobytes())
            if (fi - f0) % 30 == 0: print(f"{out}: frame {fi} ({(time.time()-t0)/(fi-f0+1):.2f}s/f)", flush=True)
        pr.stdin.close(); pr.wait()
        print("done", out, flush=True)
