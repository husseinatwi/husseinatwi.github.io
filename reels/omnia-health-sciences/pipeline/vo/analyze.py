import glob, numpy as np, soundfile as sf, torch, re
torch.set_num_threads(4)
from transformers import pipeline
import scipy.signal as ss
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small.en", device="cpu")
ref = "thirty seven trillion cells who do you trust with them"
def norm(s): return re.sub(r"[^a-z ]","",s.lower().replace("-"," ").replace("37","thirty seven")).split()
def wer(r,h):
    d=np.zeros((len(r)+1,len(h)+1),int); d[:,0]=range(len(r)+1); d[0,:]=range(len(h)+1)
    for i in range(1,len(r)+1):
        for j in range(1,len(h)+1):
            d[i,j]=min(d[i-1,j]+1,d[i,j-1]+1,d[i-1,j-1]+(r[i-1]!=h[j-1]))
    return d[-1,-1]/len(r)
def f0(a, sr):
    # simple autocorrelation pitch on voiced frames
    fr=int(0.04*sr); hop=int(0.01*sr); out=[]
    for s in range(0,len(a)-fr,hop):
        x=a[s:s+fr]*np.hanning(fr)
        if np.sqrt(np.mean(x**2))<0.02: continue
        c=np.correlate(x,x,'full')[fr-1:]
        lo,hi=int(sr/300),int(sr/60)
        k=lo+np.argmax(c[lo:hi])
        if c[k]>0.5*c[0]: out.append(sr/k)
    return np.array(out)
for f in sorted(glob.glob("test_*.wav")):
    a,sr=sf.read(f)
    a16=ss.resample_poly(a,2,3).astype(np.float32); hyp=asr({"raw":a16,"sampling_rate":16000})["text"]
    p=f0(a,sr)
    print(f"{f:22s} WER={wer(norm(ref),norm(hyp)):.2f} f0_med={np.median(p):6.1f}Hz f0_iqr={np.percentile(p,75)-np.percentile(p,25):5.1f} dur={len(a)/sr:.2f}s | {hyp.strip()}")
