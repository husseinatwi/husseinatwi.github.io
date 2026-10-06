# Pipeline

These are the scripts that produced the reel. They expect this layout in a scratch folder, with models downloading from Hugging Face on first run:

```
gen/     SDXL (RealVisXL V5 Lightning) stills -> gen/out/*.png   (jobs.py = prompts)
plates/  Real-ESRGAN upscale + Depth Anything V2 depth (prep.py), founder relight (founders.py)
vo/      Kokoro TTS lines (vo_final.py) -> final_*.wav + final_meta.json (word timings)
ltx/     LTX-Video 2B image-to-video (ltx_gen.py) + optical-flow motion transfer (flow_transfer.py)
logo/    potrace vectorization of the site logo (vectorize.py)
reel/    timeline.py (single source of truth), comp.py (compositor), fx.py, synth.py + mix.py (score/SFX/VO mix)
```

To rebuild: `reel/render_all.sh omnia_reel 4` renders the frames in 4 workers, mixes the audio, and muxes both the VO and no-VO masters.
