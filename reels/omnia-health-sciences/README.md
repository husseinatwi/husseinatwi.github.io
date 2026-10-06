# Omnia Health Sciences: "37 Trillion" (dramatic reel)

A 24.6-second vertical reel for [omniahealthsciences.com](https://omniahealthsciences.com), built entirely with local, open-weight AI models on a CPU-only machine. No Higgsfield, Runway, or other cloud video tools were used.

| File | What it is |
|---|---|
| `omnia_reel.mp4` | Master with voiceover. 1080×1920, 30 fps, H.264 High, AAC 48 kHz, about −14 LUFS. |
| `omnia_reel_no_vo.mp4` | Same cut with music and SFX only, so you can post it with trending audio or your own VO. |
| `cover.jpg` | 1080×1920 cover frame for the Reels grid. |
| `pipeline/` | The scripts that generated everything, so the reel can be rebuilt or versioned. |

## Script (VO cue sheet)

| Time | Voiceover | On screen |
|---|---|---|
| 0.25s | Thirty-seven trillion cells. | Counter decodes to **37 TRILLION** *cells.* |
| 2.50s | Who do you trust with them? | WHO DO YOU **TRUST** WITH THEM? (pupil dilates on "trust") |
| 4.30s | A marketing team? | A MARKETING TEAM? (struck through, then a CRT power-off) |
| 5.85s | Or a scientist in the world's top one percent? | **TOP 1%** over Prof. Shaker A. Mousa |
| 9.00s | Four hundred patents. | **400+** PATENTS |
| 10.50s | A thousand publications. | **1,000+** PUBLICATIONS |
| 12.50s | Thirty-three thousand citations. | **33,000+** CITATIONS |
| 14.75s | His co-founder worked alongside a two-time Nobel laureate. | Prof. Steve Harakeh, then a vintage lab with **2× NOBEL LAUREATE** |
| 18.50s | Together, they built this. | Capsule hero shot, then a dive into the capsule |
| 20.40s | Omnia. | Logo slam with a shockwave, right after a beat of total silence |
| 21.55s | Beyond wellness. Within biology. | Tagline and URL |

## Sound design

The score is synthesized in code and timed to the cut, which sits on a 120 BPM grid:

- **Heartbeat backbone.** It plays at 60 BPM through the hook, doubles in the proof section, and speeds up under the capsule shot until it cuts dead.
- **Hits.** Braams and sub booms land on every cut and every number lock.
- **Glitch beat.** A glitch bed and a tape-stop sit under "A marketing team?".
- **Vintage section.** A film-projector rattle and clock ticks play under the lineage shot.
- **Build and release.** A Shepard-tone riser leads into a true silence gap. The logo then lands on a D-major resolve, a sub drop, and a shimmer.

Whisper (small.en) transcribes the final mix word for word, which confirms every line cuts through the music.

## How it was made (all local)

| Step | Model or tool |
|---|---|
| Stills (cells, eye, marketing, patents, journals, citations, vintage lab, capsule) | RealVisXL V5.0 Lightning (SDXL), 768×1344, 5–6 steps |
| AI video (hook and capsule) | LTX-Video 2B 0.9.8 distilled, image-to-video, 41 frames, about 5 min per clip on CPU. On the hook, its camera push and cell parallax are carried onto the sharp upscaled still with optical flow. On the capsule, its generated smoke burst plays behind the sharp capsule. |
| Upscaling | Real-ESRGAN general x4v3 |
| 3D camera moves | Depth Anything V2 depth maps, then a 2.5D parallax renderer |
| Founder portraits | BiRefNet segmentation, then a low-key relight with a crimson rim light (real photos from the website) |
| Voice | Kokoro-82M (`am_michael`), pitched down 1.6 st with formants preserved, then EQ, compression and reverb |
| Logo | Vectorized from the site's 379 px PNG with potrace, so it stays crisp at full size |
| Type | Brand fonts: Fraunces (serif) and Outfit (sans) |
| Compositing | Custom Python/OpenCV pipeline: kinetic type, bloom and anamorphic streaks, chromatic aberration, grain, glitch, CRT-off, shockwave |

## Before you post

- **Claims.** Every number and credential is taken from omniahealthsciences.com: 400+ patents, 1,000+ publications, 33,000+ citations, "Top 1%, Stanford ranking", and Prof. Harakeh's work with Linus Pauling. Confirm the exact wording of the Stanford claim with the client before running it as a paid ad. The well-known Stanford/Elsevier list is a "top 2%" list.
- **Founder photos.** They come from the client's own website. Get sign-off before publishing.
- **Platform labeling.** The AI voice and AI imagery may need an AI-content label depending on platform policy.
