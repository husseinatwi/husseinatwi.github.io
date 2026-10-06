"""Denoise only (UNet), save latents. Keeps memory flat (~9 GB): no VAE decode spike."""
import sys, os, time, torch, gc
from sdxl_lib import encode_prompts, Gen, REPO
from diffusers import DPMSolverMultistepScheduler
from jobs import JOBS
keys = sys.argv[1:]
jobs = [j for j in JOBS if (not keys or j[0] in keys) and not os.path.exists(f"out/{j[0]}.png") and not os.path.exists(f"out/{j[0]}.lat.pt")]
jobs.sort(key=lambda j: keys.index(j[0]) if j[0] in keys else 99)
print("jobs:", [j[0] for j in jobs], flush=True)
st = encode_prompts([(k, p, n) for k, p, n, s, steps in jobs], "emb.pt"); gc.collect()
g = Gen(); del g.vae; gc.collect()
for k, p, n, seed, steps in jobs:
    t = time.time(); emb = st[k]
    sch = DPMSolverMultistepScheduler.from_pretrained(REPO, subfolder="scheduler", algorithm_type="sde-dpmsolver++", use_karras_sigmas=True)
    sch.set_timesteps(steps); gen = torch.Generator().manual_seed(seed)
    lat = torch.randn((1, 4, 1344 // 8, 768 // 8), generator=gen) * sch.init_noise_sigma
    tid = torch.tensor([[1344, 768, 0, 0, 1344, 768]], dtype=torch.float32)
    with torch.no_grad():
        for t_ in sch.timesteps:
            x = sch.scale_model_input(lat, t_)
            nz = g.unet(x.contiguous(memory_format=torch.channels_last), t_, encoder_hidden_states=emb["pe"], added_cond_kwargs={"text_embeds": emb["pp"], "time_ids": tid}).sample
            lat = sch.step(nz, t_, lat, generator=gen).prev_sample
    torch.save(lat, f"out/{k}.lat.pt")
    print(f"LATENT {k} {time.time()-t:.0f}s", flush=True)
print("ALL LATENTS DONE", flush=True)
