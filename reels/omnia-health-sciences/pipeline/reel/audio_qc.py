import numpy as np, soundfile as sf, scipy.signal as ss, sys, re, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
torch.set_num_threads(2)
f = sys.argv[1]
a, sr = sf.read(f); m = a.mean(1)
fig, ax = plt.subplots(2, 1, figsize=(16, 7), sharex=True)
t = np.arange(len(m)) / sr
win = 1024
rms = np.sqrt(np.convolve(m**2, np.ones(win)/win, 'same'))
ax[0].plot(t, 20*np.log10(rms+1e-6), lw=0.6); ax[0].set_ylim(-60, 0); ax[0].set_ylabel("RMS dB"); ax[0].grid(alpha=.3)
for x in [2.5,4.25,5.75,9,10.5,12.5,14.75,18.5,20.15,20.4]: ax[0].axvline(x, color='r', lw=0.5)
fq, tt, Sx = ss.spectrogram(m, sr, nperseg=2048, noverlap=1536)
ax[1].pcolormesh(tt, fq, 10*np.log10(Sx+1e-12), vmin=-120, vmax=-30, shading='auto'); ax[1].set_yscale('symlog', linthresh=200); ax[1].set_ylim(20, 20000)
plt.tight_layout(); plt.savefig(f.replace('.wav','_qc.png'), dpi=70)
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small.en", device="cpu")
a16 = ss.resample_poly(m, 1, 3).astype(np.float32)
out = asr({"raw": a16, "sampling_rate": 16000}, return_timestamps=True)
print("TRANSCRIPT:", out["text"])
for c in out.get("chunks", []): print("  ", c["timestamp"], c["text"])
