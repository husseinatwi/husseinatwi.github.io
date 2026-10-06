"""Cinematic treatment of the founders' real portraits: dark low-key background, graded subject,
crimson rim light, feathered edges, laid out for a 9:16 frame (working res 1317x2304)."""
import numpy as np, cv2, sys
from PIL import Image
import prep
WW, WH = 1317, 2304
RED = np.array([0xDA, 0x29, 0x1C], np.float32) / 255.

def treat(photo, mask_path, key, face_y_frac, rim_side=1, scale_w=1.12, bottom_pad=0):
    img = np.asarray(Image.open(photo).convert("RGB"))
    import os
    cache = f"_{key}_up.npy"
    if os.path.exists(cache): up = np.load(cache).astype(np.float32)
    else:
        up = prep.upscale(img); np.save(cache, up.astype(np.float16))
    m = np.asarray(Image.open(mask_path).convert("L"), np.float32) / 255.
    tw = int(WW * scale_w); s = tw / up.shape[1]; th = int(up.shape[0] * s)
    ph = cv2.resize(up, (tw, th), interpolation=cv2.INTER_AREA)
    lz = cv2.resize(img.astype(np.float32) / 255., (tw, th), interpolation=cv2.INTER_LANCZOS4)
    ph = 0.75 * ph + 0.25 * lz
    mk = cv2.resize(m, (tw, th), interpolation=cv2.INTER_CUBIC).clip(0, 1)
    # grade subject: contrast, slight desat, cool shadows / warm highs
    lum = (ph @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    subj = lum + (ph - lum) * 0.78
    subj = np.clip((subj - 0.04) * 1.12, 0, 1) ** 1.08
    subj = subj * np.array([1.0, 0.97, 0.95]) + (1 - subj) * np.array([0.0, 0.004, 0.012])
    # background: crushed to near-black, blurred, faint red haze
    bg = cv2.GaussianBlur(ph, (0, 0), 6) * 0.10
    bgl = (bg @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    bg = bgl * 0.6 + bg * 0.4
    # light falloff on subject: brighter towards face
    yy = np.linspace(0, 1, th)[:, None, None]
    fall = np.clip(1.15 - 0.55 * np.abs(yy - face_y_frac) ** 1.2, 0.45, 1.1)
    subj = subj * fall
    subj = np.where(subj > 0.62, 0.62 + (1 - np.exp(-(subj - 0.62) * 2.2)) * 0.30, subj)   # shoulder: keep coats from clipping
    out = bg * (1 - mk[..., None]) + subj * mk[..., None]
    # rim light from the side: edge band of the mask, weighted by horizontal gradient direction
    er = cv2.erode(mk, np.ones((9, 9), np.uint8), iterations=2)
    band = np.clip(mk - er, 0, 1)
    gx = cv2.Sobel(cv2.GaussianBlur(mk, (0, 0), 6), cv2.CV_32F, 1, 0, ksize=5)
    side = np.clip(-gx * rim_side * 4, 0, 1)
    side = side ** 0.7
    rim = cv2.GaussianBlur(band * (0.06 + 0.94 * side), (0, 0), 3.0)
    rim_top = rim * np.clip(1.25 - yy[..., 0] * 1.1, 0.35, 1.0)       # rim fades down the body
    glow = cv2.GaussianBlur(cv2.dilate(mk, np.ones((5, 5), np.uint8), iterations=6), (0, 0), 55) * (1 - mk)
    glow_side = cv2.GaussianBlur(np.clip(-gx * rim_side * 6, 0, 1), (0, 0), 50)
    out = out + rim_top[..., None] * np.array([1.0, 0.32, 0.25]) * 1.35 + (glow * (0.25 + 0.75 * glow_side))[..., None] * RED * 0.28
    # canvas: photo anchored to bottom, feathered top edge into black
    canvas = np.zeros((WH, WW, 3), np.float32); dcan = np.zeros((WH, WW), np.float32)
    x0 = (WW - tw) // 2; y0 = WH - th + bottom_pad
    feather = np.clip(np.arange(th) / (0.22 * th), 0, 1)[:, None, None] ** 1.5
    side_f = np.clip(np.minimum(np.arange(tw), tw - 1 - np.arange(tw)) / (0.06 * tw), 0, 1)[None, :, None]
    out = out * feather * side_f
    ys, ye = max(0, y0), min(WH, y0 + th); xs, xe = max(0, x0), min(WW, x0 + tw)
    canvas[ys:ye, xs:xe] = out[ys - y0:ye - y0, xs - x0:xe - x0]
    # depth: depth-anything inside subject + mask for crisp separation
    d = prep.depth((np.clip(ph, 0, 1) * 255).astype(np.uint8))
    d = 0.25 + 0.75 * (0.6 * mk + 0.4 * d * mk)
    dcan[:] = 0.2; dcan[ys:ye, xs:xe] = d[ys - y0:ye - y0, xs - x0:xe - x0]
    Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8)).save(f"{key}.png")
    np.save(f"{key}_depth.npy", dcan.astype(np.float16))
    Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8)).resize((WW // 3, WH // 3)).save(f"{key}_prev.png")
    print("done", key, "photo top y", y0, "height", th, flush=True)

if __name__ == "__main__":
    treat("../founders/mousa.jpeg", "../founders/mousa_mask.png", "mousa", face_y_frac=0.25, rim_side=-1, scale_w=1.10)
    treat("../founders/harakeh.png", "../founders/harakeh_mask.png", "harakeh", face_y_frac=0.22, rim_side=1, scale_w=1.10)
