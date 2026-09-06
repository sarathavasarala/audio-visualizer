# 🎵 Audio Visualizer

An intelligent, audio-reactive video generator that transforms audio tracks, vocal covers, podcasts, and beats into high-craft, cinematic videos ready for **Instagram Reels (9:16)**, **Stories**, and **Feed Posts (1:1)**.

Renders an authentic, spinning vinyl record surrounded by fluid waveform bars that organically breathe with the music, set against bespoke atmospheric backgrounds with studio specular lighting and luminous bloom.

---

## ✨ Key Features

- **Organic Breathing Bar Motion**: Blends a 65% broadband loudness envelope with 35% local spectral ripple detail. The entire ring breathes unified with the beat while local frequency variations dance across it.
- **Multi-Harmonic Circular Distribution**: Overlapping frequency mixtures distribute bass, midrange, and treble across the circle so no quadrant exclusively locks to bass or treble, eliminating top over-reactivity and bottom dormancy.
- **Continuous Circular Smoothing**: Gaussian spatial filtering across adjacent bars with periodic boundary wrapping (`mode='wrap'`) ensures zero visible seams and no rigid mirrored halves.
- **Framerate-Independent Dynamics**: Physical exponential attack ($\tau_{\text{attack}} = 60\text{ ms}$) and release ($\tau_{\text{release}} = 220\text{ ms}$) time constants ensure identical motion curves at 30 fps, 60 fps, or 120 fps.
- **Capped Frequency Balancing & Soft Saturation**: Per-band reference tracking with a noise floor gate ($-55\text{ dBFS}$) and smooth $\tanh$ compression preserves dynamic headroom during loud peaks without flat ceilings or hiss amplification.
- **Physical Vinyl Disc**: Opaque micro-grooved record body with rotating obsidian/amber center label and delicate gold spoke accents.
- **Stationary Specular Sheen**: Studio lighting highlights remain fixed in world-space while the physical vinyl rotates underneath.
- **Luminous Bloom & Distance Vignette**: 30% alpha Gaussian bloom behind 4px pill-cap bars and a mathematical distance power vignette focusing attention on the center disc.
- **Direct FFmpeg Stream**: Pipes raw frames directly to FFmpeg stdin to encode H.264 High Profile (`yuv420p`) + 320 kbps AAC with `faststart` (zero intermediate frame files on disk).

---

## 🚀 Quickstart

### 1. Prerequisites

Ensure [FFmpeg](https://ffmpeg.org) is installed on your system:

```bash
# macOS (via Homebrew)
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get install ffmpeg
```

### 2. Installation

Clone the repository and install the Python dependencies:

```bash
git clone https://github.com/sarathavasarala/audio-visualizer.git
cd audio-visualizer
pip install -r requirements.txt
```

### 3. Generate a Video

Run via the CLI:

```bash
# Clean minimal title (9:16 Instagram Reel)
python -m visualizer.cli \
  --audio "path/to/song.wav" \
  --bg "path/to/background.jpg" \
  --title "SONG TITLE" \
  --aspect "9:16" \
  --output "output.mp4"
```

```bash
# With artist/cover subtitle (1:1 Feed Post)
python -m visualizer.cli \
  --audio "path/to/song.mp3" \
  --bg "path/to/background.jpg" \
  --title "SONG TITLE" \
  --subtitle "ARTIST OR COVER" \
  --aspect "1:1" \
  --fps 30 \
  --bars 64 \
  --output "output_square.mp4"
```

---

## ⚙️ CLI Options

| Flag | Description | Default |
| :--- | :--- | :--- |
| `--audio`, `-a` | Path to input audio file (`.mp3`, `.wav`, `.m4a`, `.flac`, etc.) | *Required* |
| `--output`, `-o` | Destination MP4 path | `output.mp4` |
| `--bg`, `-b` | Path to background image | `None` (dark gradient) |
| `--title`, `-t` | Song or project title (uppercase tracked serif) | `""` |
| `--subtitle`, `-s` | Subtitle / artist / credit line (optional, omit for clean look) | `""` |
| `--aspect` | Aspect ratio (`9:16` for vertical, `1:1` for square) | `9:16` |
| `--fps` | Video framerate ($1 \le \text{fps} \le 120$) | `30` |
| `--bars` | Number of radial wave bars ($16 \le \text{bars} \le 256$) | `64` |

---

## 🎛️ Tunable Motion Parameters

Motion shaping is modularized in [`visualizer/motion.py`](visualizer/motion.py) and centralized in `MotionConfig`:

```python
from visualizer import render_visualizer_video, MotionConfig

config = MotionConfig(
    shared_weight=0.65,          # 65% broadband breathing / 35% local ripple
    detail_weight=0.35,
    attack_sec=0.060,            # 60ms rise time constant (snappy & reactive)
    release_sec=0.220,           # 220ms decay time constant (smooth release)
    min_freq=45.0,               # Lower analysis frequency (Hz)
    max_freq=11000.0,            # Upper analysis frequency (Hz)
    baseline_height=6.0,         # Resting bar height in pixels (silence)
    max_height=78.0,             # Maximum bar height in pixels
    spatial_smoothing_sigma=1.2, # Circular smoothing across neighbor bars
    saturation_strength=1.2,     # Soft tanh compression curvature
    noise_floor_db=-55.0         # Noise gate floor (dBFS)
)

render_visualizer_video(
    audio_path="song.wav",
    output_path="output.mp4",
    motion_config=config
)
```

---

## 🧪 Testing

The repository includes a comprehensive unit test suite covering silence baseline return, bounded heights, low/high tone circular breathing, seamless wrapping, 30 vs 60 fps timing consistency, dynamic headroom, and end-to-end video synthesis:

```bash
python -m unittest discover tests
```

---

## 🤖 Antigravity AI Skill Integration

This project includes a native `SKILL.md` for Google Antigravity. When invoked within an AI-assisted environment, the agent can:
1. Intake audio and clarify title, optional subtitle, and aspect ratio.
2. Analyze the song's musical mood, genre, and lyrical themes.
3. Automatically generate bespoke, atmospheric 9:16 artwork via Gemini.
4. Execute the visualizer engine and deliver the finished, Instagram-ready MP4.

---

## 📄 License & Privacy

- Audio and generated video outputs are strictly excluded from version control via `.gitignore`.
- Built for musicians, podcasters, creators, and audio engineers.
