import sys, os, time, torch, gc
from PIL import Image
from sdxl_lib import encode_prompts, Gen
from jobs import JOBS
only = sys.argv[1:]  # optional subset keys
jobs = [j for j in JOBS if not only or j[0] in only]
jobs = [j for j in jobs if not os.path.exists(f"out/{j[0]}.png")]
print("jobs:", [j[0] for j in jobs], flush=True)
st = encode_prompts([(k, p, n) for k, p, n, s, steps in jobs], "emb.pt")
gc.collect()
g = Gen()
for k, p, n, seed, steps in jobs:
    t = time.time()
    img = g.run(st[k], steps=steps, cfg=1.0, seed=seed)
    Image.fromarray(img).save(f"out/{k}.png")
    print(f"DONE {k} {time.time()-t:.0f}s", flush=True)
print("ALL DONE", flush=True)
