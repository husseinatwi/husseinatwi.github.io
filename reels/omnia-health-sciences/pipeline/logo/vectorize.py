import numpy as np, cv2, subprocess
from PIL import Image
im = np.asarray(Image.open("../brand/logo.png").convert("RGBA")).astype(np.float32) / 255.
rgb, a = im[..., :3], im[..., 3]
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
lum = 0.2126*r + 0.7152*g + 0.0722*b
red = (r - np.maximum(g, b)) * a            # redness weighted by alpha
dark = (1 - lum) * a * (red < 0.15)          # black wordmark coverage
SC = 8
def up(m): return cv2.resize(m, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
red_u, dark_u, a_u = up(red), up(dark), up(a)
redm = (red_u > 0.25).astype(np.uint8)
# fill holes of diamond to get outer shape
cnts, _ = cv2.findContours(redm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
diamond = np.zeros_like(redm); cv2.drawContours(diamond, cnts, -1, 1, -1)
cross = ((diamond > 0) & (redm == 0)).astype(np.uint8)
cross = cv2.morphologyEx(cross, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
word = ((dark_u > 0.5) & (diamond == 0)).astype(np.uint8)
print("bbox diamond", cv2.boundingRect(diamond), "cross px", cross.sum(), "word px", word.sum())
def trace(mask, name, scale):
    Image.fromarray(((1 - mask) * 255).astype(np.uint8)).convert("1").save(f"{name}.pbm")
    # -g = pgm backend (antialiased raster); -x scale factor; -t turdsize; -a corner threshold; -O opt tolerance
    subprocess.run(["potrace", "-g", "-x", str(scale), "-t", "4", "-a", "1.0", "-O", "0.4", f"{name}.pbm", "-o", f"{name}.pgm"], check=True)
    m = np.asarray(Image.open(f"{name}.pgm")).astype(np.float32) / 255.
    return 1 - m  # coverage
S2 = 0.75   # 379*8*0.75 = ~2274 px wide output
W_ = trace(word, "word", S2); D_ = trace(diamond, "diamond", S2); C_ = trace(cross, "cross", S2)
h, w = W_.shape
print("traced size", w, h)
# white-on-transparent version for dark backgrounds: wordmark white, diamond brand red, cross white
RED = np.array([0xDA, 0x29, 0x1C]) / 255.
col = np.zeros((h, w, 3)); alpha = np.clip(W_ + D_, 0, 1)
col += W_[..., None] * 1.0
col = col * (1 - D_[..., None]) + D_[..., None] * RED
col = col * (1 - C_[..., None]) + C_[..., None] * 1.0
out = np.dstack([np.clip(col, 0, 1), alpha])
Image.fromarray((out * 255).round().astype(np.uint8), "RGBA").save("logo_white_hd.png")
np.save("logo_layers.npy", np.stack([W_, D_, C_]))
# preview on black
prev = out[..., :3] * out[..., 3:4]
Image.fromarray((prev * 255).astype(np.uint8)).resize((w // 3, h // 3), Image.LANCZOS).save("preview_black.png")
