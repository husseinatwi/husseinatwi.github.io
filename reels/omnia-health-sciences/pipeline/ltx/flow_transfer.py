"""Carry AI-generated motion (LTX frames, low-res) onto the sharp high-res plate via dense optical flow."""
import sys, numpy as np, cv2
def flows_to_first(frames):
    """frames: N x h x w x 3 uint8 -> list of flow (h,w,2) mapping frame_t pixel -> frame_0 location offset"""
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    g0 = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)
    out = [np.zeros(g0.shape + (2,), np.float32)]
    prev = out[0]
    for i in range(1, len(frames)):
        gi = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
        f = dis.calc(gi, g0, prev.copy())      # warm start from previous (motion is smooth)
        f = cv2.GaussianBlur(f, (0, 0), 4.0)    # keep it smooth (no tearing on the sharp plate)
        out.append(f); prev = f
    return np.stack(out)

if __name__ == "__main__":
    key = sys.argv[1]
    fr = np.load(f"{key}_frames.npy")
    fl = flows_to_first(fr)
    np.save(f"{key}_flow.npy", fl.astype(np.float16))
    mag = np.sqrt((fl ** 2).sum(-1))
    print(key, "frames", fr.shape, "max flow px", float(mag.max()), "mean last", float(mag[-1].mean()))
