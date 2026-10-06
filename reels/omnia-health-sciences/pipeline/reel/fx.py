"""Compositing toolkit: easing, 2.5D depth-parallax plates, text layers, light/lens FX, grain, glitch."""
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import timeline as TL
SCR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PLATES = os.path.join(SCR, "plates"); FONTS = os.path.join(SCR, "fonts")
W, H, FPS = TL.W, TL.H, TL.FPS
RED = np.array([0xDA, 0x29, 0x1C], np.float32) / 255.
WHITE = np.ones(3, np.float32)
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)

# ---------------- easing ----------------
def c01(x): return float(min(1.0, max(0.0, x)))
def ramp(t, a, b): return c01((t - a) / (b - a)) if b > a else float(t >= a)
def smooth(x): x = c01(x); return x * x * (3 - 2 * x)
def out_cubic(x): x = c01(x); return 1 - (1 - x) ** 3
def in_cubic(x): x = c01(x); return x ** 3
def out_expo(x): x = c01(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def in_out_sine(x): x = c01(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def out_back(x, s=1.6): x = c01(x) - 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x
def decay(t, t0, tau):  # impulse response after t0
    return math.exp(-(t - t0) / tau) if t >= t0 else 0.0

# ---------------- fonts / text ----------------
_fonts = {}
def font(name, size):
    k = (name, size)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _fonts[k]
def FR(w, s, it=False): return font(f"Fraunces-{w}-{'italic' if it else 'normal'}.ttf", s)
def OU(w, s): return font(f"Outfit-{w}-normal.ttf", s)
def MO(w, s): return font(f"JetBrainsMono-{w}-normal.ttf", s)

_tcache = {}
class Text:
    """Rasterised text (alpha mask) with per-character boxes for animated reveals."""
    def __init__(self, s, f, tracking=0.0):
        self.s = s; self.f = f
        size = f.size; trk = tracking * size
        asc, desc = f.getmetrics(); pad = int(size * 0.35) + 8
        if tracking == 0:
            l, t, r, b = f.getbbox(s); tw = r
        widths = [f.getlength(c) for c in s]
        tw = sum(widths) + trk * max(0, len(s) - 1) if tracking else f.getlength(s)
        w = int(math.ceil(tw)) + 2 * pad; h = asc + desc + 2 * pad
        img = Image.new("L", (w, h), 0); d = ImageDraw.Draw(img)
        self.boxes = []
        if tracking:
            x = pad
            for c, cw in zip(s, widths):
                d.text((x, pad), c, font=f, fill=255); self.boxes.append((x, x + cw)); x += cw + trk
        else:
            d.text((pad, pad), s, font=f, fill=255)
            x = pad
            for c, cw in zip(s, widths): self.boxes.append((x, x + cw)); x += cw
        self.a = np.asarray(img, np.float32) / 255.
        # tight ink bbox for centering
        ys, xs = np.where(self.a > 0.02)
        self.ink = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else (0, 0, w, h)
        self.pad = pad; self.w, self.h = w, h
    @property
    def ink_w(self): return self.ink[2] - self.ink[0]
    @property
    def ink_h(self): return self.ink[3] - self.ink[1]

def T(s, f, tracking=0.0):
    k = (s, f.path, f.size, tracking)
    if k not in _tcache: _tcache[k] = Text(s, f, tracking)
    return _tcache[k]

def fit_font(s, maker, max_w, start, tracking=0.0, min_size=20):
    size = start
    while size > min_size:
        if T(s, maker(size), tracking).ink_w <= max_w: return maker(size)
        size = int(size * 0.95)
    return maker(size)

def _shift(a, dx, dy=0):
    if dx == 0 and dy == 0: return a
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)

def draw(frame, tx, cx, cy, scale=1.0, alpha=1.0, color=WHITE, blur=0.0, glow=0.0, glow_color=None,
         glow_sigma=None, ca=0.0, reveal=None, wipe=None, mblur=0.0, shadow=0.0, anchor="center"):
    """Composite text layer onto float32 RGB frame. (cx,cy): ink-box center (or left-center for anchor='left')."""
    if alpha <= 0.002: return
    a = tx.a
    if reveal is not None:          # per-char reveal: reveal(i) -> (alpha, dy)
        a = np.zeros_like(tx.a)
        for i, (x0, x1) in enumerate(tx.boxes):
            ra, dy = reveal(i)
            if ra <= 0: continue
            xa, xb = int(x0) - 2, int(math.ceil(x1)) + 2
            seg = tx.a[:, xa:xb] * ra
            if dy: seg = _shift(seg, 0, dy)
            a[:, xa:xb] = np.maximum(a[:, xa:xb], seg)
    if wipe is not None:            # left->right wipe 0..1 over ink box (soft edge)
        x = np.arange(tx.w, dtype=np.float32)
        edge = tx.ink[0] + wipe * (tx.ink_w + 40) - 20
        a = a * np.clip((edge - x) / 20 + 0.5, 0, 1)[None, :]
    if scale != 1.0:
        a = cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR if scale > 1 else cv2.INTER_AREA)
    if mblur > 0.5:
        k = int(mblur) * 2 + 1; a = cv2.blur(a, (1, k))
    if blur > 0.3: a = cv2.GaussianBlur(a, (0, 0), blur)
    h, w = a.shape
    ix0, iy0, ix1, iy1 = [v * scale for v in tx.ink]
    if anchor == "left": ox = cx - ix0
    elif anchor == "right": ox = cx - ix1
    else: ox = cx - (ix0 + ix1) / 2
    oy = cy - (iy0 + iy1) / 2
    x0, y0 = int(round(ox)), int(round(oy))
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe <= xs or ye <= ys: return
    A = a[ys - y0:ye - y0, xs - x0:xe - x0] * alpha
    reg = frame[ys:ye, xs:xe]
    if shadow > 0:
        sh = cv2.GaussianBlur(A, (0, 0), 10) * shadow
        reg *= (1 - sh[..., None])
    if glow > 0:
        gs = glow_sigma or max(4, 0.06 * tx.f.size * scale)
        g = cv2.GaussianBlur(A, (0, 0), gs)
        reg += g[..., None] * (glow_color if glow_color is not None else color) * glow
    if ca > 0.3:
        d = ca
        for c, sh_ in ((0, d), (1, 0), (2, -d)):
            Ac = _shift(A, sh_) if sh_ else A
            reg[..., c] = reg[..., c] * (1 - Ac) + color[c] * Ac
    else:
        reg[:] = reg * (1 - A[..., None]) + color * A[..., None]

def draw_rgba(frame, rgba, cx, cy, scale=1.0, alpha=1.0, add_glow=0.0, glow_sigma=20):
    """composite a straight-alpha RGBA float image centered at (cx, cy)."""
    img = rgba
    if scale != 1.0:
        img = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
    h, w = img.shape[:2]; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe <= xs or ye <= ys: return
    sub = img[ys - y0:ye - y0, xs - x0:xe - x0]
    A = sub[..., 3:4] * alpha; reg = frame[ys:ye, xs:xe]
    if add_glow > 0:
        g = cv2.GaussianBlur(sub[..., :3] * A, (0, 0), glow_sigma)
        reg += g * add_glow
    reg[:] = reg * (1 - A) + sub[..., :3] * A

# ---------------- plates (2.5D parallax) ----------------
_gy, _gx = np.mgrid[0:H, 0:W].astype(np.float32)
_gx -= W / 2; _gy -= H / 2
class Plate:
    def __init__(self, key):
        bgr = cv2.imread(os.path.join(PLATES, f"{key}.png"), cv2.IMREAD_COLOR)
        self.img = bgr[:, :, ::-1].astype(np.float32) / 255.
        dp = os.path.join(PLATES, f"{key}_depth.npy")
        d = np.load(dp).astype(np.float32) if os.path.exists(dp) else np.full(self.img.shape[:2], 0.5, np.float32)
        self.depth = cv2.GaussianBlur(d, (0, 0), 3)
        self.h, self.w = self.img.shape[:2]
        self.base = H / self.h if self.w * (H / self.h) >= W else W / self.w
    def flow_fields(self, seed=0, scale=0.012):
        """two smooth random vector fields at plate res (for organic fluid drift)"""
        if not hasattr(self, "_flow"):
            r = np.random.default_rng(seed); sh = (max(8, int(self.h * scale)), max(8, int(self.w * scale)))
            f = []
            for _ in range(4):
                n = cv2.GaussianBlur(r.standard_normal(sh).astype(np.float32), (0, 0), 1.6)
                n = cv2.resize(n, (self.w, self.h), interpolation=cv2.INTER_CUBIC); f.append(n / (np.abs(n).max() + 1e-6))
            self._flow = f
        return self._flow
    def animate(self, t, amp=8.0, speed=0.6, weight="near", pupil=None):
        """returns an animated source image: fluid drift weighted by depth (+ optional pupil dilation)"""
        f1, f2, f3, f4 = self.flow_fields()
        w = self.depth if weight == "near" else (1 - self.depth)
        a, b = math.cos(t * speed * 2 * math.pi * 0.35), math.sin(t * speed * 2 * math.pi * 0.35)
        dx = (f1 * a + f3 * b) * amp * (0.3 + 0.7 * w); dy = (f2 * a + f4 * b) * amp * (0.3 + 0.7 * w) - amp * 0.4 * t * w
        if not hasattr(self, "_ggrid"):
            gy, gx = np.mgrid[0:self.h, 0:self.w].astype(np.float32); self._ggrid = (gx, gy)
        gx, gy = self._ggrid
        mx, my = gx + dx, gy + dy
        if pupil is not None:
            (pcx, pcy, R, k) = pupil
            ddx, ddy = gx - pcx, gy - pcy; r = np.sqrt(ddx ** 2 + ddy ** 2) + 1e-3
            fall = np.clip(1 - r / R, 0, 1) ** 2
            s = 1 / (1 + k * fall)
            mx = mx + ddx * (s - 1); my = my + ddy * (s - 1)
        return cv2.remap(self.img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    def render(self, zoom=1.08, cx=0.0, cy=0.0, rot=0.0, dolly=0.0, px=0.0, py=0.0, focus=0.5, src=None):
        """zoom: >1 crops in. cx,cy: pan in output px. dolly: extra relative magnification of near layers.
        px,py: lateral parallax (output px) applied as (depth-focus)."""
        s = self.base * zoom
        c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        ux = (c * _gx + si * _gy - cx) / s; uy = (-si * _gx + c * _gy - cy) / s
        mx = ux + self.w / 2; my = uy + self.h / 2
        if dolly or px or py:
            d = cv2.remap(self.depth, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101) - focus
            k = 1.0 / (1.0 + dolly * d)
            mx = ux * k + self.w / 2 - px * d / s; my = uy * k + self.h / 2 - py * d / s
        return cv2.remap(self.img if src is None else src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

# ---------------- grading & lens ----------------
def grade(img, exposure=0.0, contrast=1.0, pivot=0.35, sat=1.0, lift=0.0, gamma=1.0, gain=1.0,
          shadow_tint=(0, 0, 0), high_tint=(0, 0, 0), black=0.0):
    x = img * (2 ** exposure)
    x = (x - pivot) * contrast + pivot
    x = np.clip(x, 0, None)
    L = (x @ LUMA)[..., None]
    x = L + (x - L) * sat
    x = np.clip((x - black) / (1 - black), 0, None)
    x = lift + (gain - lift) * np.power(np.clip(x, 0, None), gamma)
    if any(shadow_tint) or any(high_tint):
        L = np.clip((x @ LUMA)[..., None], 0, 1)
        x = x + (1 - L) * np.array(shadow_tint, np.float32) + L * np.array(high_tint, np.float32)
    return x

def bloom(img, thr=0.6, strength=0.5, sigma=18, streak=0.0, streak_color=(1.0, 0.35, 0.3)):
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    br = np.clip((small - thr) / (1 - thr), 0, None)
    out = img
    if strength > 0:
        g = cv2.GaussianBlur(br, (0, 0), sigma / 4) * 0.6 + cv2.GaussianBlur(br, (0, 0), sigma) * 0.4
        out = out + cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR) * strength
    if streak > 0:
        s = cv2.GaussianBlur(br, (0, 0), sigmaX=60, sigmaY=0.8)
        s = s.mean(axis=2, keepdims=True) * np.array(streak_color, np.float32)
        out = out + cv2.resize(s, (W, H), interpolation=cv2.INTER_LINEAR) * streak
    return out

_vig = None
def vignette(img, amount=0.45, power=2.2):
    global _vig
    if _vig is None:
        r = np.sqrt((_gx / (W * 0.62)) ** 2 + (_gy / (H * 0.62)) ** 2)
        _vig = np.clip(r, 0, 1.4) ** power
    return img * (1 - amount * _vig)[..., None]

def chroma(img, amount):
    """radial chromatic aberration (amount in px at the edge)"""
    if amount < 0.3: return img
    out = img.copy()
    for ch, k in ((0, 1.0), (2, -1.0)):
        s = 1 + k * amount / (H / 2)
        M = np.float32([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]])
        out[..., ch] = cv2.warpAffine(img[..., ch], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return out

def shake(img, dx, dy, rot=0.0, zoom=1.0):
    if abs(dx) < 0.2 and abs(dy) < 0.2 and abs(rot) < 0.01 and zoom == 1.0: return img
    M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, zoom); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

def radial_blur(img, amount, steps=8, cx=W / 2, cy=H / 2):
    if amount < 0.002: return img
    acc = img.copy()
    for i in range(1, steps):
        s = 1 + amount * i / steps
        M = np.float32([[s, 0, (1 - s) * cx], [0, s, (1 - s) * cy]])
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return acc / steps

_grain = None
def grain(img, frame_idx, amount=0.045, size=1.0):
    global _grain
    if _grain is None:
        r = np.random.default_rng(99)
        _grain = [cv2.resize(r.standard_normal((H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR) for _ in range(12)]
    g = _grain[frame_idx % 12]
    L = np.clip(img @ LUMA, 0, 1)
    wgt = (0.35 + 1.3 * L * (1 - L) * 2.2)[..., None]
    return img + g[..., None] * amount * wgt

# ---------------- particles ----------------
class Particles:
    def __init__(self, n=70, seed=0, color=(1.0, 0.45, 0.38), speed=(0, -40), size=(1.5, 9)):
        r = np.random.default_rng(seed)
        self.p = r.uniform(0, 1, (n, 2)) * [W, H]; self.z = r.uniform(0, 1, n)
        self.size = size; self.color = np.array(color, np.float32); self.speed = np.array(speed, np.float32)
        self.ph = r.uniform(0, 6.28, n); self.b = r.uniform(0.3, 1.0, n)
    def render(self, t, intensity=1.0, converge=None, conv_amt=0.0):
        hw, hh = W // 2, H // 2
        layers = [np.zeros((hh, hw), np.float32) for _ in range(3)]
        for i in range(len(self.z)):
            z = self.z[i]
            pos = self.p[i] + self.speed * t * (0.4 + 1.2 * z) + np.array([math.sin(t * 0.9 + self.ph[i]) * 12 * z, 0])
            pos = np.mod(pos, [W, H])
            if converge is not None and conv_amt > 0:
                pos = pos + (np.array(converge) - pos) * conv_amt
            rad = self.size[0] + (self.size[1] - self.size[0]) * z ** 2
            tw = 0.6 + 0.4 * math.sin(t * 3 + self.ph[i] * 3)
            li = 0 if z < 0.33 else (1 if z < 0.66 else 2)
            cv2.circle(layers[li], (int(pos[0] / 2), int(pos[1] / 2)), max(1, int(rad / 2)), float(self.b[i] * tw), -1, cv2.LINE_AA)
        acc = cv2.GaussianBlur(layers[0], (0, 0), 0.8) + cv2.GaussianBlur(layers[1], (0, 0), 2.0) * 0.8 + cv2.GaussianBlur(layers[2], (0, 0), 5.0) * 0.6
        acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)
        return acc[..., None] * self.color * intensity

# ---------------- glitch / transitions ----------------
def glitch(img, fi, amount=1.0, seed=0):
    if amount <= 0.01: return img
    r = np.random.default_rng(seed * 1000 + fi)
    out = img.copy()
    nb = int(6 + 10 * amount)
    for _ in range(nb):
        y = r.integers(0, H - 10); hgt = int(r.integers(6, 90) * amount) + 4
        dx = int(r.normal(0, 60 * amount))
        out[y:y + hgt] = np.roll(out[y:y + hgt], dx, axis=1)
        if r.random() < 0.25 * amount:
            out[y:y + hgt] = 1 - out[y:y + hgt] * np.array([0.2, 1.0, 1.0])
    d = int(8 + 20 * amount)
    out[..., 0] = np.roll(out[..., 0], d, axis=1); out[..., 2] = np.roll(out[..., 2], -d, axis=1)
    out[::3] *= (1 - 0.25 * amount)  # scanlines
    return out

def crt_off(img, p):
    """p 0..1: squash to a line then a dot (old TV power-off)"""
    out = np.zeros_like(img)
    if p >= 1: return out
    if p < 0.7:
        q = out_cubic(p / 0.7); hh = max(2, int(H * (1 - q) ** 2.2)); ww = W
    else:
        q = (p - 0.7) / 0.3; hh = 2; ww = max(2, int(W * (1 - q) ** 2))
    small = cv2.resize(img, (ww, hh), interpolation=cv2.INTER_AREA)
    boost = 1 + 3 * c01(p / 0.7)
    y0, x0 = (H - hh) // 2, (W - ww) // 2
    out[y0:y0 + hh, x0:x0 + ww] = np.clip(small * boost + 0.25 * c01(p / 0.5), 0, 4)
    glowl = cv2.GaussianBlur(out, (0, 0), 12)
    return out + glowl * 1.5

def shockwave(img, t0, t, center=(W / 2, H / 2), speed=2600, width=90, amp=26):
    dt = t - t0
    if dt < 0 or dt > 0.6: return img, 0
    rr = speed * dt
    dx, dy = _gx + W / 2 - center[0], _gy + H / 2 - center[1]
    r = np.sqrt(dx * dx + dy * dy) + 1e-3
    ring = np.exp(-((r - rr) / width) ** 2) * amp * (1 - dt / 0.6)
    mx = (_gx + W / 2) - dx / r * ring; my = (_gy + H / 2) - dy / r * ring
    out = cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return out, ring / amp

def light_leak(t, seed=0, color=(1.0, 0.25, 0.12), strength=0.6):
    r = np.random.default_rng(seed)
    cx = W * (r.uniform(-0.2, 1.2) + 0.6 * math.sin(t * 1.3 + r.uniform(0, 6)))
    cy = H * (r.uniform(0, 1) + 0.25 * math.cos(t * 0.9))
    sx, sy = W * r.uniform(0.35, 0.6), H * r.uniform(0.25, 0.45)
    g = np.exp(-(((_gx + W / 2 - cx) / sx) ** 2 + ((_gy + H / 2 - cy) / sy) ** 2))
    return g[..., None] * np.array(color, np.float32) * strength

def to8(img):
    return (np.clip(img, 0, 1) ** (1 / 1.0) * 255 + 0.5).astype(np.uint8)


class FlowAnim:
    """AI-generated motion (LTX-Video optical flow, low-res) applied to a sharp high-res plate."""
    def __init__(self, plate, key):
        path = os.path.join(SCR, "ltx", f"{key}_flow.npy")
        self.ok = os.path.exists(path)
        if not self.ok: return
        self.fl = np.load(path).astype(np.float32); self.N = len(self.fl)
        self.p = plate; self.sx = plate.w / self.fl.shape[2]; self.sy = plate.h / self.fl.shape[1]
        gy, gx = np.mgrid[0:plate.h, 0:plate.w].astype(np.float32); self.g = (gx, gy)
    def src(self, u, strength=1.0):
        """u in [0,1]: position along the generated clip"""
        pos = c01(u) * (self.N - 1); i0 = int(math.floor(pos)); i1 = min(self.N - 1, i0 + 1); fr = pos - i0
        f = self.fl[i0] * (1 - fr) + self.fl[i1] * fr
        fu = cv2.resize(f, (self.p.w, self.p.h), interpolation=cv2.INTER_LINEAR)
        mx = self.g[0] + fu[..., 0] * self.sx * strength; my = self.g[1] + fu[..., 1] * self.sy * strength
        return cv2.remap(self.p.img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
