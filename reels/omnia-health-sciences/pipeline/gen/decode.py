import glob, os, torch, time
from PIL import Image
from diffusers import AutoencoderKL
from sdxl_lib import REPO
torch.set_num_threads(int(os.environ.get("THREADS", "4")))
vae = AutoencoderKL.from_pretrained(REPO, subfolder="vae", variant="fp16", torch_dtype=torch.float32).eval()
for f in sorted(glob.glob("out/*.lat.pt")):
    k = os.path.basename(f)[:-7]
    if os.path.exists(f"out/{k}.png"): continue
    t = time.time(); lat = torch.load(f)
    with torch.no_grad():
        img = vae.decode(lat / vae.config.scaling_factor).sample
    img = ((img[0].permute(1, 2, 0).clamp(-1, 1) + 1) * 127.5).round().byte().numpy()
    Image.fromarray(img).save(f"out/{k}.png"); print(f"DECODED {k} {time.time()-t:.0f}s", flush=True)
