"""AI upscale (Real-ESRGAN general x4v3) + depth (Depth-Anything-V2-Base) for each still."""
import sys, os, time, numpy as np, cv2, torch, torch.nn as nn, torch.nn.functional as F
from PIL import Image
from huggingface_hub import hf_hub_download
torch.set_num_threads(int(os.environ.get("THREADS", "2")))
WR_H = 2304  # working height (1.2x of 1920)

class SRVGGNetCompact(nn.Module):
    def __init__(s, nf=64, nc=32, up=4):
        super().__init__(); s.up = up
        L = [nn.Conv2d(3, nf, 3, 1, 1), nn.PReLU(nf)]
        for _ in range(nc): L += [nn.Conv2d(nf, nf, 3, 1, 1), nn.PReLU(nf)]
        L += [nn.Conv2d(nf, 3 * up * up, 3, 1, 1)]
        s.body = nn.ModuleList(L); s.ps = nn.PixelShuffle(up)
    def forward(s, x):
        o = x
        for l in s.body: o = l(o)
        return s.ps(o) + F.interpolate(x, scale_factor=s.up, mode="nearest")

_sr = None
def upscale(img):  # img uint8 RGB
    global _sr
    if _sr is None:
        _sr = SRVGGNetCompact().eval()
        sd = torch.load(hf_hub_download("jhj0517/realesr-general-x4v3", "realesr-general-x4v3.pth"), map_location="cpu")["params"]
        _sr.load_state_dict(sd)
    x = torch.from_numpy(img.astype(np.float32) / 255.).permute(2, 0, 1)[None]
    H, W = img.shape[:2]; out = np.zeros((H * 4, W * 4, 3), np.float32)
    T = 384; P = 16  # tiles with padding to bound memory
    with torch.no_grad():
        for y in range(0, H, T):
            for x0 in range(0, W, T):
                ya, yb = max(0, y - P), min(H, y + T + P); xa, xb = max(0, x0 - P), min(W, x0 + T + P)
                o = _sr(x[:, :, ya:yb, xa:xb])[0].permute(1, 2, 0).numpy()
                oy, ox = (y - ya) * 4, (x0 - xa) * 4
                hh, ww = min(T, H - y) * 4, min(T, W - x0) * 4
                out[y * 4:y * 4 + hh, x0 * 4:x0 * 4 + ww] = o[oy:oy + hh, ox:ox + ww]
    return np.clip(out, 0, 1)

_depth = None
def depth(img):
    global _depth
    from transformers import pipeline
    if _depth is None:
        _depth = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Base-hf", device="cpu")
    d = np.asarray(_depth(Image.fromarray(img))["predicted_depth"], dtype=np.float32)
    d = cv2.resize(d.squeeze(), (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
    d = (d - np.percentile(d, 1)) / (np.percentile(d, 99.5) - np.percentile(d, 1) + 1e-6)
    return np.clip(d, 0, 1)

def process(src, key, target_h=WR_H):
    t = time.time()
    img = np.asarray(Image.open(src).convert("RGB"))
    up = upscale(img)
    h, w = up.shape[:2]; s = target_h / h
    wr = cv2.resize(up, (int(round(w * s)), target_h), interpolation=cv2.INTER_AREA)
    lz = cv2.resize(img.astype(np.float32) / 255., (wr.shape[1], wr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    wr = 0.7 * wr + 0.3 * lz
    wr8 = (np.clip(wr, 0, 1) * 255).round().astype(np.uint8)
    Image.fromarray(wr8).save(f"{key}.png")
    d = depth(img)
    d = cv2.resize(d, (wr8.shape[1], wr8.shape[0]), interpolation=cv2.INTER_CUBIC)
    np.save(f"{key}_depth.npy", d.astype(np.float16))
    Image.fromarray((d * 255).astype(np.uint8)).resize((wr8.shape[1] // 4, wr8.shape[0] // 4)).save(f"{key}_depth_prev.png")
    print(f"{key}: {img.shape[1]}x{img.shape[0]} -> {wr8.shape[1]}x{wr8.shape[0]} in {time.time()-t:.0f}s", flush=True)

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        src, key = arg.split(":")
        if os.path.exists(f"{key}.png") and os.path.exists(f"{key}_depth.npy"): print("skip", key); continue
        process(src, key)
