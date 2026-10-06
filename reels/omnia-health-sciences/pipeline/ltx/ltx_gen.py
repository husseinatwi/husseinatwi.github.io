"""Local AI video: LTX-Video 2B (0.9.8 distilled) image-to-video on CPU.
Stage A (encode): T5-XXL bf16 -> prompt embeddings.  Stage B (gen): transformer + VAE -> frames."""
import sys, os, time, gc, json, numpy as np, torch
from PIL import Image
torch.set_num_threads(4)
from huggingface_hub import hf_hub_download
CKPT = lambda: hf_hub_download("Lightricks/LTX-Video", "ltxv-2b-0.9.8-distilled.safetensors")
CFG = "Lightricks/LTX-Video-0.9.5"
CLIPS = {
  "cells": dict(image="../gen/out/cells_1.png", prompt="Microscopic macro footage inside the human body: smooth translucent red blood cells slowly drifting and gently tumbling through dark plasma, soft bioluminescent crimson glow, floating particles, very slow camera push in, cinematic, shallow depth of field, realistic, smooth natural motion."),
  "capsule": dict(image="../gen/out/capsule_1.png", prompt="Cinematic product shot: a translucent crimson red softgel capsule floating in darkness, slowly rotating, liquid inside gently swirling, tiny golden particles drifting, wisps of smoke curling around it, dramatic rim light, smooth slow motion, realistic."),
}
NEG = "worst quality, inconsistent motion, blurry, jittery, distorted, morphing, text, watermark"
W_, H_, NF = 448, 768, 41

def stage_encode():
    from transformers import T5EncoderModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("city96/t5-v1_1-xxl-encoder-bf16")
    te = T5EncoderModel.from_pretrained("city96/t5-v1_1-xxl-encoder-bf16", torch_dtype=torch.bfloat16).eval()
    out = {}
    for k, c in CLIPS.items():
        for name, text in (("pos", c["prompt"]), ("neg", NEG)):
            ids = tok(text, padding="max_length", max_length=128, truncation=True, add_special_tokens=True, return_tensors="pt")
            t = time.time()
            with torch.no_grad():
                e = te(ids.input_ids, attention_mask=ids.attention_mask)[0].float()
            out[f"{k}_{name}"] = (e, ids.attention_mask)
            print("encoded", k, name, f"{time.time()-t:.1f}s", flush=True)
    torch.save(out, "embeds.pt")

def stage_gen(keys):
    from diffusers import LTXConditionPipeline, LTXVideoTransformer3DModel, AutoencoderKLLTXVideo
    from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
    emb = torch.load("embeds.pt")
    t = time.time()
    tr = LTXVideoTransformer3DModel.from_single_file(CKPT(), config=CFG, subfolder="transformer", torch_dtype=torch.float32)
    tr.enable_layerwise_casting(storage_dtype=torch.bfloat16, compute_dtype=torch.float32)
    vae = AutoencoderKLLTXVideo.from_single_file(CKPT(), config=CFG, subfolder="vae", torch_dtype=torch.float32)
    pipe = LTXConditionPipeline.from_pretrained(CFG, transformer=tr, vae=vae, text_encoder=None, tokenizer=None, torch_dtype=torch.float32)
    print("loaded", f"{time.time()-t:.0f}s", flush=True)
    for k in keys:
        c = CLIPS[k]
        img = Image.open(c["image"]).convert("RGB").resize((W_, H_), Image.LANCZOS)
        cond = LTXVideoCondition(image=img, frame_index=0)
        pe, pm = emb[f"{k}_pos"]
        t = time.time()
        frames = pipe(conditions=[cond], prompt_embeds=pe, prompt_attention_mask=pm,
                      width=W_, height=H_, num_frames=NF, frame_rate=24,
                      timesteps=[1000, 993, 987, 981, 975, 909, 725, 0.03], guidance_scale=1.0,
                      decode_timestep=0.05, decode_noise_scale=0.025, image_cond_noise_scale=0.0,
                      generator=torch.Generator().manual_seed(42), output_type="np").frames[0]
        print("generated", k, frames.shape, f"{time.time()-t:.0f}s", flush=True)
        np.save(f"{k}_frames.npy", (np.clip(frames, 0, 1) * 255).astype(np.uint8))
        os.makedirs(f"{k}_png", exist_ok=True)
        for i, f in enumerate(frames):
            Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).save(f"{k}_png/{i:03d}.png")

if __name__ == "__main__":
    if sys.argv[1] == "encode": stage_encode()
    else: stage_gen(sys.argv[2:])
