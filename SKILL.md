---
name: audio-visualizer
description: Automatically creates aesthetic, Instagram-ready video visualizers from an audio file or path. Analyzes track mood and genre with Gemini, generates a bespoke atmospheric background, renders an audio-reactive spinning vinyl disc with fluid waveform bars, and mixes it into a high-fidelity MP4.
---

# Audio Visualizer Skill

Use this skill when a user provides an audio file (song, vocal cover, instrumental, podcast clip, beat) and wants to transform it into an aesthetic video for Instagram Reels, Stories, or social media.

---

## Autonomous Workflow

### Step 1: Input Intake & Track Profiling
1. Identify the input audio file path (either uploaded via chat or located on disk).
2. Extract or clarify basic track metadata:
   - **Title**: Song name or project title (in uppercase wide tracking).
   - **Subtitle**: Subtitle or credit (e.g. "TITLE COVER", "ACOUSTIC COVER", or artist name).
   - **Aspect Ratio**: Default to `9:16` (1080×1920) for Instagram Reels/Stories, or `1:1` (1080×1080) if requested for feed posts.

### Step 2: Atmospheric Art Conception via Gemini
1. Analyze the song's genre, emotional mood, and lyrical themes (e.g., romantic, soulful, rainy twilight, neon lo-fi, warm acoustic, ambient indie).
2. Formulate a prompt for `generate_image`:
   - Specify aspect ratio matching the target (`9:16` or `1:1`).
   - Include visual styling keywords: *Atmospheric cinematic aesthetic background for music, vertical 9:16, moody midnight obsidian and deep tones, soft diffused warm bokeh, subtle floating dust particles, elegant fine vignette, artistic abstract minimalism, clean sophisticated mood, no text, no people, no movie logos*.
3. Execute `generate_image` to save the artwork asset.

### Step 3: Run the Visualizer Engine
Execute the modular engine CLI:

```bash
python -m visualizer.cli \
  --audio "/path/to/input.mp3" \
  --bg "/path/to/generated_bg.jpg" \
  --title "SONG TITLE" \
  --subtitle "ARTIST OR COVER" \
  --aspect "9:16" \
  --output "output_video.mp4"
```

#### Under the Hood:
- **Audio Processing**: Decodes to 44.1kHz float32 mono; computes 4096-point FFT with centered zero-padded windows; applies track-wide 98th-percentile dynamic normalization and musical attack/decay smoothing.
- **Solid Physical Vinyl**: Renders opaque micro-grooves (preventing background bleed-through) and a central rotating label with gold spoke accents.
- **Stationary Sheen**: Keeps specular lighting highlights anchored in camera space while the vinyl rotates underneath.
- **Luminous Bloom**: Adds a 30% alpha Gaussian light spill behind the 4px pill-cap bars to tie them into the background.
- **Edge-Darkening Vignette**: Continuous mathematical distance power mask focusing attention on the center disc.
- **Direct FFmpeg Stream**: Pipes frames directly to FFmpeg stdin to encode H.264 High Profile (`yuv420p`) + 320 kbps AAC audio with faststart.

### Step 4: Verification & Delivery
1. Inspect output stream properties:
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration output_video.mp4
   ```
2. Deliver the final video link with a brief markdown link and 2-3 tailored Instagram caption suggestions.
