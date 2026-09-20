# 🎵 Audio Skills Suite

> **AI agent skills for musicians and creators — drop an audio file, get social-ready visualizers and pitch-adapted karaoke stems.**

This repository provides two standardized Antigravity AI agent skills and modular engines designed for music workflows:
1. **`/audio-visualizer`** — Generates cinema-grade, Instagram-ready 9:16 or 1:1 vinyl visualizer videos with bespoke artwork, audio-reactive wave bars, synchronized lyrics, and story splitting.
2. **`/audio-karaoke`** — Extracts clean instrumental backing tracks from YouTube videos or local audio files, with pitch-shifted variants tailored to your vocal range.

All project assets are organized automatically into dedicated folders in your `~/Downloads/` directory.

---

## ⚡ Skills Overview

### 1. `/audio-visualizer`
*Location: [`.agents/skills/audio-visualizer/`](.agents/skills/audio-visualizer/)*

Turn your songs, acoustic covers, beats, podcast snippets, and voice memos into aesthetic social videos:

- **Bespoke Atmospheric Art** — Analyzes track mood, genre, and cultural roots with Gemini to create tailored artwork (warm dusk sandstone archways, misty pine forests, rainy lo-fi neon, etc.).
- **Physical Vinyl Record** — Solid grooved vinyl texture with rotating center label, gold spoke accents, and stationary specular studio lighting that remains fixed while the record spins.
- **Organic Breathing Motion** — 65% broadband loudness breathing combined with 35% local spectral ripples, circular Gaussian spatial smoothing (`mode='wrap'`), and physical attack/release dynamics.
- **Synchronized Lyrics Overlay** — Smooth sinusoidal alpha cross-fades and LUT-accelerated alpha blending from `.json` or `.lrc` cue files.
- **Instagram Story Splitting** — Automatically splits long tracks into 59-second frame-accurate clips for Instagram Stories (under the 60s platform limit).
- **Automated Asset Bundling** — Exports source audio, trimmed audio, cover art, master video, and story clips into `~/Downloads/<Song_Title>_Visualizer/`.

#### Quick Agent Prompt:
> *"Make an aesthetic 9:16 visualizer for this song: `~/Music/my_song.mp3`"*

---

### 2. `/audio-karaoke`
*Location: [`.agents/skills/audio-karaoke/`](.agents/skills/audio-karaoke/)*

Extract studio-quality karaoke backing tracks and pitch-shift them to match your vocal range:

- **YouTube & Local Audio Intake** — Accepts any YouTube link or local audio file (`.mp3`, `.wav`, `.m4a`, etc.).
- **UVR AI Stem Separation** — Separates clean instrumental backing and isolated vocals using Ultimate Vocal Remover models via `audio-separator`.
- **Pitch Adaptation** — Shifts keys (e.g. `-2`, `-4` semitones) with pristine quality using FFmpeg `librubberband` without altering tempo.
- **Time-Range Trimming** — Isolates specific song sections (e.g. verse + chorus) for vocal practice.
- **Automated Asset Bundling** — Automatically exports source audio, trimmed audio, isolated vocals, original key instrumental, and all pitch-shifted variations into `~/Downloads/<Song_Title>_Karaoke/`.

#### Quick Agent Prompt:
> *"Turn this song into a karaoke track with -2 and -4 semitone versions for my range: `https://www.youtube.com/watch?v=...`"*

---

## 💻 CLI Usage (`visualizer.cli`)

Prefer running the visualizer engine directly from the command line?

### Setup
```bash
# Install FFmpeg
brew install ffmpeg

# Install Python requirements
pip install -r requirements.txt
```

### Commands

```bash
# 9:16 Vertical for Instagram Reels / Stories with asset export
python -m visualizer.cli \
  --audio "my_song.mp3" \
  --bg "my_artwork.jpg" \
  --title "SONG TITLE" \
  --aspect "9:16" \
  --export-dir "$HOME/Downloads/My_Song_Visualizer" \
  --output "output.mp4"
```

```bash
# Square format with artist credit and synchronized lyrics
python -m visualizer.cli \
  --audio "my_song.wav" \
  --bg "my_artwork.jpg" \
  --title "SONG TITLE" \
  --subtitle "ARTIST NAME" \
  --aspect "1:1" \
  --lyrics "lyrics.json" \
  --output "feed_post.mp4"
```

#### CLI Options:
- `--audio`, `-a`: Path to input audio file (`.mp3`, `.wav`, `.m4a`, etc.) *(Required)*
- `--output`, `-o`: Where to save the master video (default: `output.mp4`)
- `--bg`, `-b`: Path to background image (optional, defaults to an elegant dark gradient)
- `--title`, `-t`: Song name displayed in tracked uppercase serif
- `--subtitle`, `-s`: Subtitle or artist credit (optional; leave blank for clean title-only)
- `--aspect`: Video aspect ratio — `9:16` (Reels/Stories) or `1:1` (Feed)
- `--fps`: Frame rate (default: `30`)
- `--bars`: Number of radial waveform bars (default: `64`, range: 16–256)
- `--lyrics`, `-l`: Path to synchronized lyrics cue file (`.json` or `.lrc`)
- `--export-dir`: Directory to copy and bundle all project assets together

---

## 🎛️ Motion Physics & Customization

The motion dynamics are centralized in [`visualizer/motion.py`](visualizer/motion.py) via `MotionConfig`:

```python
from visualizer import render_visualizer_video, MotionConfig

config = MotionConfig(
    shared_weight=0.65,      # 65% shared breathing / 35% local ripples
    attack_sec=0.060,        # Snappy rise time (60ms)
    release_sec=0.220,       # Smooth, musical decay (220ms)
    saturation_strength=1.2  # Soft saturation prevents peak flattening on loud hits
)

render_visualizer_video(
    audio_path="song.mp3",
    output_path="output.mp4",
    motion_config=config
)
```

---

## 🧪 Testing

Run the automated test suite verifying motion headroom, silent decay, framerate invariance, and lyric rendering:

```bash
python -m unittest discover tests
```

---

## 🔒 Privacy

All personal audio files, temporary media, and rendered videos are strictly ignored by version control via `.gitignore`. Your music remains private on your machine.
