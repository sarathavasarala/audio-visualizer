---
name: audio-visualizer
description: Automatically creates aesthetic, Instagram-ready video visualizers from an audio file or path. Analyzes track mood and genre with Gemini, generates a bespoke atmospheric background, renders an audio-reactive spinning vinyl disc with fluid waveform bars, and mixes it into a high-fidelity MP4.
---

# Audio Visualizer Skill

Use this skill when a user provides an audio file (song, vocal cover, instrumental, podcast clip, beat) and wants to transform it into an aesthetic video for Instagram Reels, Stories, or social media.

---

## Autonomous Workflow

### Step 1: Input Intake & Track Profiling
1. **Audio File Path**:
   - Verify that an audio file path has been provided or uploaded.
   - If not provided, ask the user for the audio file path or upload before proceeding.
2. **Metadata & Styling Preferences**:
   - Clarify or confirm the following with the user before generating:
     - **Title**: Song name or project title (formatted in uppercase with elegant wide tracking).
     - **Subtitle**: **Strictly optional**. Explicitly confirm if the user wants an artist name or cover credit, or prefers a **clean title-only** visual (often preferred for minimal/cinematic aesthetic). Never invent or guess an unrequested subtitle.
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
  --subtitle "" \
  --aspect "9:16" \
  --output "output_video.mp4"
```
*(Omit `--subtitle` or pass `""` if title-only is preferred).*

#### Under the Hood:
- **Organic Bar Motion Engine**:
  - **Shared Breathing & Local Detail**: Blends a 65% broadband loudness envelope with 35% local spectral ripple detail so the entire ring pulses unified with the rhythm.
  - **Circular Frequency Mixture Distribution**: Overlapping multi-harmonic distribution ensures no quadrant is exclusively locked to bass or treble.
  - **Circular Spatial Smoothing**: Gaussian filtering with `mode='wrap'` eliminates visible seams between bar 0 and bar $N-1$.
  - **Framerate-Independent Dynamics**: Physical exponential attack (60 ms) and release (220 ms) time constants ensure identical motion across 30 fps, 60 fps, etc.
  - **Gentle Capped Balancing & Soft Saturation**: Per-band reference tracking with noise gate (-55 dBFS) and smooth tanh saturation prevents noise amplification and hard peak flattening.
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
