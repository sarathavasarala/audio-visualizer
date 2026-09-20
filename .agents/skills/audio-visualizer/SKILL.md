---
name: audio-visualizer
description: Automatically creates aesthetic, Instagram-ready video visualizers from an audio file or path. Analyzes track mood and genre with Gemini, generates a bespoke atmospheric background, renders an audio-reactive spinning vinyl disc with fluid waveform bars, and mixes it into a high-fidelity MP4. Organizes all project assets (cover art, source audio, final output, story clips) in a dedicated folder in ~/Downloads/.
---

# Audio Visualizer Skill

Use this skill when a user provides an audio file (song, vocal cover, instrumental, podcast clip, beat) and wants to transform it into an aesthetic video for Instagram Reels, Stories, or social media.

---

## Autonomous Workflow

### Step 1: Destination Asset Folder & Track Profiling
1. **Dedicated Asset Directory in Downloads**:
   - **Immediately** create a dedicated folder inside the user's `~/Downloads/` directory named after the track or song title:
     ```bash
     mkdir -p "$HOME/Downloads/<Song_Title>_Visualizer"
     ```
   - All project assets generated or used during the workflow **must** be stored or copied into this folder:
     - **Source Audio**: Original audio file (e.g. `source_audio.mp3`), plus any trimmed version if a time cut is specified (`trimmed_audio.mp3`).
     - **Cover Artwork**: Bespoke atmospheric artwork generated via Gemini (`cover_art.jpg`).
     - **Lyrics File**: Timed lyrics `.json` or `.lrc` (if synchronized lyrics overlay was generated).
     - **Full Video Output**: Master 1080p visualizer MP4 (`<song_title>_visualizer_full.mp4`).
     - **Story Clips**: 59-second clips (`<song_title>_story_part1_59s.mp4`, `<song_title>_story_part2.mp4`) if the video exceeds 60s or if story cuts are requested.
2. **Audio File Intake & Trimming**:
   - Verify that an audio file path has been provided or uploaded.
   - If a specific time range or cut is requested (e.g. "till 1:22 mark"), trim the audio file using FFmpeg with a clean 1.0–1.5s audio fade-out:
     ```bash
     ffmpeg -y -i "input.mp3" -to <seconds> -af "afade=t=out:st=<start>:d=1.5" -b:a 320k "trimmed_audio.mp3"
     ```
3. **Metadata & Styling Preferences**:
   - Clarify or confirm the following with the user before generating:
     - **Title**: Song name or project title (formatted in uppercase with elegant wide tracking).
     - **Subtitle**: **Strictly optional**. Explicitly confirm if the user wants an artist name or cover credit, or prefers a **clean title-only** visual (often preferred for minimal/cinematic aesthetic). Never invent or guess an unrequested subtitle.
     - **Lyrics**: Check if the user wants synchronized lyrics overlay (e.g. Romanized lyrics only, or Romanized with translations). Provide or generate a timed `.json` or `.lrc` cue file.
     - **Aspect Ratio**: Default to `9:16` (1080×1920) for Instagram Reels/Stories, or `1:1` (1080×1080) if requested for feed posts.
     - **Story Splitting**: If the video is longer than 60 seconds (Instagram Stories limit is 60s), offer or generate split 59-second clips.

### Step 2: Atmospheric Art Conception via Gemini
1. **Genre & Cultural Symbolism Analysis**:
   Analyze the song's musical genre, cultural roots, emotional mood, and lyrical themes. Never use generic or cliché tropes (e.g. avoid candles unless explicitly requested). Instead, select authentic cultural, architectural, and environmental symbolism:

   | Genre / Style | Authentic Visual Symbolism & Aesthetics | Palette & Mood |
   | :--- | :--- | :--- |
   | **Sufi / Qawwali / Devotional** | Grand Mughal/Islamic arabesque archways, sacred geometric jali tracery, luminous celestial crescent moon, starry midnight sky, empty stone/marble sanctuary washed in divine moonlight, floating golden stardust particles. *(No people, no dervishes in center, no candles).* | Midnight sapphire, royal indigo, antique gold, celestial moonlight. |
   | **Ghazal / Urdu Poetry** | Heritage stone jharokhas, moonlit palace terrace, night desert breeze, jasmine vines, serene marble pavilion, poetic melancholic dusk. | Warm obsidian, antique ivory, dusty rose, twilight amber. |
   | **Lo-Fi / Chillhop** | Rainy midnight window overlooking blurred city lights, warm desk lamp reflection, soft neon reflections, cozy interior room twilight. | Deep teal, soft amber, muted neon magenta, rainy blue. |
   | **R&B / Neo-Soul** | Rich velvet textures, minimalist modernist architecture, bronze and honey spotlighting, moody atmospheric shadows, sleek contours. | Deep burgundy, espresso obsidian, warm honey bronze. |
   | **Synthwave / Cyberpunk** | Distant retro-futuristic skyline, wireframe grid horizons, misty megacity towers, celestial neon aurora bloom. | Electric cyan, deep violet, midnight magenta, neon glow. |
   | **Classical / Orchestral** | Historic concert hall architraves, rich mahogany and brass acoustics, dramatic volumetric shaft of light with floating dust motes. | Deep mahogany, gold trim, warm charcoal, dramatic chiaroscuro. |
   | **Indie Folk / Ambient** | Foggy pine forest ridge, Nordic mountain peaks at twilight, calm glassy lake reflection, ethereal mist and northern lights. | Moss green, slate grey, misty cyan, soft twilight gold. |

2. **Compositional Clearance Rules**:
   - **Disc Clearance (`cx=540, cy=1030`, radius ~340px)**: The central area of the image must remain visually uncluttered (e.g. open sky, distant architecture, gentle mist, or atmospheric depth) so the spinning vinyl record and glowing waveform bars do not collide with or obscure key subjects.
   - **Lyrics Clearance (`y=1450–1650`)**: The lower third must provide clean, dark, or textured contrast for floating synchronized lyrics.
   - **No Foreground Figures**: Never generate humans, faces, or characters centered in the frame, as the vinyl record will directly block them.

3. **Formulate Prompt & Generate Artwork**:
   Execute `generate_image` with aspect ratio matching target (`9:16` or `1:1`) incorporating the specific genre symbolism and clearance rules. Copy the generated image to `$HOME/Downloads/<Song_Title>_Visualizer/cover_art.jpg`.

### Step 3: Run the Visualizer Engine
Execute the modular engine CLI with the target assets and optional `--export-dir`:

```bash
python -m visualizer.cli \
  --audio "/path/to/input.mp3" \
  --bg "/path/to/generated_bg.jpg" \
  --title "SONG TITLE" \
  --subtitle "" \
  --aspect "9:16" \
  --lyrics "lyrics.json" \
  --export-dir "$HOME/Downloads/<Song_Title>_Visualizer" \
  --output "$HOME/Downloads/<Song_Title>_Visualizer/<song_title>_visualizer_full.mp4"
```
*(Omit `--subtitle` if title-only is preferred. Omit `--lyrics` if no lyrics overlay is needed).*

#### Under the Hood:
- **Synchronized Lyrics Subsystem (`visualizer.lyrics`)**: Pre-renders text cues as RGBA stamps with drop-shadows, sinusoidal alpha easing, and LUT-accelerated alpha blending.
- **Organic Bar Motion Engine**: Blends 65% broadband loudness breathing with 35% local spectral ripple detail, circular frequency distribution, circular spatial smoothing (`mode='wrap'`), framerate-independent dynamics (60ms attack, 220ms release), and tanh soft saturation.
- **Solid Physical Vinyl**: Renders opaque micro-grooves, rotating center label with gold spoke accents, and stationary specular sheen anchored in camera space.
- **Luminous Bloom & Vignette**: 30% alpha Gaussian bloom spill behind 4px pill-cap bars; continuous mathematical edge-darkening vignette.
- **Direct FFmpeg Stream**: Pipes frames directly to FFmpeg stdin to encode H.264 High Profile (`yuv420p`) + 320 kbps AAC audio with faststart.

### Step 4: Story Splitting (for Instagram Stories)
If the video duration exceeds 60 seconds (or if the user requested story clips):
Split the full video into 59-second clips with frame accuracy:

```bash
# Part 1: First 59 seconds
ffmpeg -y -i "<song_title>_visualizer_full.mp4" -t 59.0 -c:v libx264 -crf 18 -preset faster -c:a aac -b:a 320k "$HOME/Downloads/<Song_Title>_Visualizer/<song_title>_story_part1_59s.mp4"

# Part 2: Remaining segment
ffmpeg -y -ss 59.0 -i "<song_title>_visualizer_full.mp4" -c:v libx264 -crf 18 -preset faster -c:a aac -b:a 320k "$HOME/Downloads/<Song_Title>_Visualizer/<song_title>_story_part2.mp4"
```

### Step 5: Verification & Delivery
1. Inspect output stream properties:
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration output_video.mp4
   ```
2. Verify that all project assets are present in the Downloads folder:
   ```bash
   ls -lh "$HOME/Downloads/<Song_Title>_Visualizer"
   ```
3. Deliver clickable markdown file links to all assets directly in the Downloads folder.
4. Provide 2-3 tailored Instagram caption suggestions with hashtags.
