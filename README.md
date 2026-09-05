# 🎵 Audio Visualizer

An intelligent, audio-reactive video generator designed to transform audio tracks, vocal covers, podcasts, and beats into high-craft, cinematic videos ready for **Instagram Reels (9:16)** and **Feed Posts (1:1)**.

---

## ✨ Features

- **Audio-Reactive Radial Visualizer**: 64-bar circular waveform with smooth 4px pill caps and subtle luminous bloom.
- **Physical Vinyl Disc**: Realistic grooved vinyl record with opaque micro-grooves and authentic center label.
- **Stationary Studio Lighting**: Specular light sheen remains anchored in world-space while the record rotates underneath.
- **Mathematical Vignette**: Continuous distance power mask highlighting the center disc while softening outer margins.
- **Track-Wide 98th-Percentile Normalization**: Eliminates flatlining and preserves natural vocal dynamics.
- **4096-Sample FFT Resolution**: High resolution for low-end vocal fundamentals with zero-padded centered windows.
- **Direct FFmpeg Stream**: Streams raw RGB video directly into FFmpeg (zero intermediate PNG frames on disk).
- **Instagram-Ready Output**: H.264 High Profile (`yuv420p`), 30 fps, 320 kbps AAC audio, MP4 with faststart.

---

## 🚀 Quickstart

### 1. Installation

Ensure you have [FFmpeg](https://ffmpeg.org) installed on your system:

```bash
# macOS
brew install ffmpeg
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Generate a Video

Run via the CLI:

```bash
python -m visualizer.cli \
  --audio "path/to/song.mp3" \
  --bg "path/to/background.jpg" \
  --title "KALANK" \
  --subtitle "TITLE COVER" \
  --aspect "9:16" \
  --output "output.mp4"
```

#### CLI Options:
| Flag | Description | Default |
|---|---|---|
| `--audio`, `-a` | Path to audio file (`.mp3`, `.wav`, `.m4a`, etc.) | *Required* |
| `--output`, `-o` | Destination MP4 path | `output.mp4` |
| `--bg`, `-b` | Path to background image | `None` (dark gradient) |
| `--title`, `-t` | Song title | `""` |
| `--subtitle`, `-s` | Subtitle / Artist / Credit | `""` |
| `--aspect` | Aspect ratio (`9:16` or `1:1`) | `9:16` |
| `--fps` | Video framerate | `30` |
| `--bars` | Number of radial wave bars | `64` |

---

## 🤖 Antigravity AI Skill Integration

This repository includes an autonomous `SKILL.md` for Google Antigravity. When activated, the AI agent can:
1. Accept an uploaded audio file.
2. Analyze the track's genre, mood, and lyrics.
3. Automatically prompt Gemini / `generate_image` to create a bespoke, atmospheric 9:16 background.
4. Execute the visualizer engine and deliver the finished video.

---

## 🔒 Privacy & Git Guidelines

Audio files and video outputs are strictly excluded from version control via `.gitignore`.
