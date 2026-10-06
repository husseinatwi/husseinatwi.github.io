import torch, time, gc, os, json
from diffusers import UNet2DConditionModel, AutoencoderKL, DPMSolverMultistepScheduler, EulerAncestralDiscreteScheduler
from transformers import CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer
REPO = "SG161222/RealVisXL_V5.0_Lightning"
torch.set_num_threads(4)

def encode_prompts(pairs, out_path):
    """pairs: list of (key, prompt, negative). Saves dict of embeddings."""
    tok1 = CLIPTokenizer.from_pretrained(REPO, subfolder="tokenizer")
    tok2 = CLIPTokenizer.from_pretrained(REPO, subfolder="tokenizer_2")
    te1 = CLIPTextModel.from_pretrained(REPO, subfolder="text_encoder", variant="fp16", torch_dtype=torch.float32).eval()
    te2 = CLIPTextModelWithProjection.from_pretrained(REPO, subfolder="text_encoder_2", variant="fp16", torch_dtype=torch.float32).eval()
    def enc(text):
        embs = []; pooled = None
        for tok, te in ((tok1, te1), (tok2, te2)):
            ids = tok(text, padding="max_length", max_length=77, truncation=True, return_tensors="pt").input_ids
            with torch.no_grad():
                o = te(ids, output_hidden_states=True)
            embs.append(o.hidden_states[-2])
            if te is te2: pooled = o.text_embeds
        return torch.cat(embs, dim=-1), pooled
    store = {}
    if os.path.exists(out_path): store = torch.load(out_path)
    for key, p, n in pairs:
        pe, pp = enc(p); ne, npool = enc(n or "")
        store[key] = dict(pe=pe, pp=pp, ne=ne, np=npool, prompt=p, neg=n)
    torch.save(store, out_path)
    del te1, te2; gc.collect()
    return store

class Gen:
    def __init__(self):
        t = time.time()
        self.unet = UNet2DConditionModel.from_pretrained(REPO, subfolder="unet", variant="fp16", torch_dtype=torch.float32).eval()
        self.vae = AutoencoderKL.from_pretrained(REPO, subfolder="vae", variant="fp16", torch_dtype=torch.float32).eval()
        self.unet = self.unet.to(memory_format=torch.channels_last)
        self.unet.enable_layerwise_casting(storage_dtype=torch.bfloat16, compute_dtype=torch.float32)
        print(f"loaded unet+vae in {time.time()-t:.1f}s", flush=True)

    @torch.no_grad()
    def run(self, emb, width=768, height=1344, steps=6, cfg=1.0, seed=0, sampler="dpm2msde"):
        if sampler == "eulera":
            sch = EulerAncestralDiscreteScheduler.from_pretrained(REPO, subfolder="scheduler", timestep_spacing="trailing")
        else:
            sch = DPMSolverMultistepScheduler.from_pretrained(REPO, subfolder="scheduler", algorithm_type="sde-dpmsolver++", use_karras_sigmas=True)
        sch.set_timesteps(steps)
        g = torch.Generator().manual_seed(seed)
        lat = torch.randn((1, 4, height // 8, width // 8), generator=g) * sch.init_noise_sigma
        add_time_ids = torch.tensor([[height, width, 0, 0, height, width]], dtype=torch.float32)
        if cfg > 1.0:
            pe = torch.cat([emb["ne"], emb["pe"]]); pp = torch.cat([emb["np"], emb["pp"]]); tid = torch.cat([add_time_ids, add_time_ids])
        else:
            pe, pp, tid = emb["pe"], emb["pp"], add_time_ids
        t0 = time.time()
        for i, t in enumerate(sch.timesteps):
            x = torch.cat([lat] * 2) if cfg > 1.0 else lat
            x = sch.scale_model_input(x, t)
            n = self.unet(x.contiguous(memory_format=torch.channels_last), t, encoder_hidden_states=pe, added_cond_kwargs={"text_embeds": pp, "time_ids": tid}).sample
            if cfg > 1.0:
                nu, nc = n.chunk(2); n = nu + cfg * (nc - nu)
            lat = sch.step(n, t, lat, generator=g).prev_sample
        t1 = time.time()
        img = self.vae.decode(lat / self.vae.config.scaling_factor).sample
        img = ((img[0].permute(1, 2, 0).clamp(-1, 1) + 1) * 127.5).round().byte().numpy()
        print(f"  denoise {t1-t0:.1f}s ({(t1-t0)/steps:.1f}s/step) decode {time.time()-t1:.1f}s", flush=True)
        return img
