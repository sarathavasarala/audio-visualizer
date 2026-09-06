# 🎵 Audio Visualizer

> **Drop an audio file to your AI agent. Get a bespoke, Instagram-ready video in seconds.**

Turn your songs, acoustic covers, beats, podcast snippets, and voice memos into aesthetic, cinema-grade social videos without opening video editing software.

Just drop your MP3 or WAV to your AI agent, and it handles everything:
1. **Listens to the vibe** — Analyzes the song's genre, emotional mood, and lyrics.
2. **Conjures bespoke cover art** — Generates atmospheric, cinematic artwork tailored to your track.
3. **Spins the vinyl** — Renders an authentic physical record with audio-reactive bars that breathe with the music.
4. **Delivers the video** — Hands you a high-definition, vertical video ready to post straight to Instagram Reels, Stories, or TikTok.

---

## 🎧 The Experience

Most audio visualizers feel sterile, jittery, or locked to generic templates. This visualizer is crafted to look and feel like high-end music cinematography:

- **Organic Breathing Motion** — The whole ring pulses and breathes naturally with the rhythm and bass, with delicate ripples reflecting the melody and vocals.
- **Physical Vinyl Record** — Authentic grooved vinyl texture with a rotating center label, gold spoke accents, and stationary studio lighting that stays fixed while the record spins.
- **Atmospheric Artwork** — Bespoke visual moods (warm amber dusk, moody midnight rain, neon lo-fi, vintage film grain) generated to match your music.
- **Clean Aesthetic Typography** — Elegant serif title styling that keeps the focus entirely on your music.
- **Platform-Ready** — Formatted perfectly in vertical **9:16** for Reels/Stories or **1:1** square for feed posts, encoded in crisp 1080p with studio-quality audio.

---

## 🪄 How to Use

### Option 1: With Your AI Agent (Recommended)

If you're using Google Antigravity or any agent equipped with this skill, you don't need to run any code:

1. **Drop your audio file** into the chat (`.mp3`, `.wav`, `.m4a`).
2. Say something like:
   > *"Make an aesthetic 9:16 visualizer for this song."*
3. The agent will confirm your song title, generate matching cover art, render the spinning vinyl, and hand you the finished MP4!

---

### Option 2: Run via CLI

Prefer running it from your terminal? It’s a single command:

#### 1. Setup
```bash
# Install FFmpeg (required for video rendering)
brew install ffmpeg

# Install Python requirements
pip install -r requirements.txt
```

#### 2. Generate
```bash
# Minimal, clean title (9:16 vertical for Instagram Reels)
python -m visualizer.cli \
  --audio "my_song.mp3" \
  --bg "my_artwork.jpg" \
  --title "SONG TITLE" \
  --aspect "9:16" \
  --output "visualizer.mp4"
```

```bash
# Square format with artist credit (1:1 for Feed posts)
python -m visualizer.cli \
  --audio "my_song.wav" \
  --bg "my_artwork.jpg" \
  --title "SONG TITLE" \
  --subtitle "ARTIST NAME" \
  --aspect "1:1" \
  --output "feed_post.mp4"
```

#### CLI Options:
- `--audio`, `-a`: Path to your audio file (`.mp3`, `.wav`, `.m4a`, etc.) *(Required)*
- `--output`, `-o`: Where to save the video (default: `output.mp4`)
- `--bg`, `-b`: Path to a background image (optional, defaults to an elegant dark gradient)
- `--title`, `-t`: Song name displayed in tracked uppercase serif
- `--subtitle`, `-s`: Subtitle or artist credit (optional; leave blank for a clean title-only look)
- `--aspect`: Video format — `9:16` (Reels/Stories) or `1:1` (Feed)
- `--fps`: Frame rate (default: `30`)
- `--bars`: Number of radial waveform bars (default: `64`)

---

## 🎛️ Customizing the Motion

Want to dial in how reactive the bars are? All motion physics are centralized in [`visualizer/motion.py`](visualizer/motion.py) via `MotionConfig`:

```python
from visualizer import render_visualizer_video, MotionConfig

# Customize the feel
config = MotionConfig(
    shared_weight=0.65,    # 65% shared breathing / 35% local ripples
    attack_sec=0.060,      # Snappy rise time (60ms)
    release_sec=0.220,     # Smooth, musical decay (220ms)
    saturation_strength=1.2 # Soft saturation prevents harsh clipping on loud drops
)

render_visualizer_video(
    audio_path="song.wav",
    output_path="output.mp4",
    motion_config=config
)
```

---

## 🧪 Testing

Run the automated test suite verifying baseline silence return, dynamic headroom, and framerate consistency:

```bash
python -m unittest discover tests
```

---

## 🔒 Privacy

All personal audio recordings, temporary assets, and rendered video outputs are strictly excluded from git tracking via `.gitignore`. Your music stays on your machine.
