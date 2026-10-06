# Final VO lines: per-line speed control, trimmed, saved at 24k for further processing
import numpy as np, soundfile as sf, torch, json
torch.set_num_threads(1)
from kokoro import KPipeline
pipe = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
VOICE = "am_michael"
LINES = [
 ("L01", "Thirty-seven trillion cells.", 0.90),
 ("L02", "Who do you trust with them?", 0.92),
 ("L03", "A marketing team?", 0.95),
 ("L04", "Or a scientist in the world's top one percent?", 0.95),
 ("L05", "Four hundred patents.", 0.97),
 ("L06", "A thousand publications.", 0.97),
 ("L07", "Thirty-three thousand citations.", 0.97),
 ("L08", "His co-founder worked alongside a two-time Nobel laureate.", 0.97),
 ("L09", "Together, they built this.", 0.90),
 ("L10", "[Omnia](/ˈɑmniə/).", 0.85),
 ("L11", "Beyond wellness. Within biology.", 0.90),
]
meta = {}
for key, text, spd in LINES:
    rs = list(pipe(text, voice=VOICE, speed=spd))
    a = np.concatenate([r.audio.numpy() for r in rs]).astype(np.float32)
    words = []
    for r in rs:
        for t in (r.tokens or []):
            if getattr(t, "start_ts", None) is not None:
                words.append((t.text, float(t.start_ts), float(t.end_ts)))
    idx = np.where(np.abs(a) > 0.01)[0]
    s = max(0, idx[0] - int(0.03*24000)); e = min(len(a), idx[-1] + int(0.15*24000))
    off = s/24000
    words = [(w, round(st-off,3), round(en-off,3)) for w, st, en in words]
    sf.write(f"final_{key}.wav", a[s:e], 24000)
    meta[key] = dict(text=text, dur=(e-s)/24000, words=words)
    print(key, f"{(e-s)/24000:.2f}s", words, flush=True)
json.dump(meta, open("final_meta.json","w"), indent=1)
