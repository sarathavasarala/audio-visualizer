---
name: audio-karaoke
description: >-
  Extracts karaoke (instrumental) tracks from YouTube videos or local audio files with optional time-range trimming,
  and generates pitch-shifted versions tailored to the singer's vocal range using UVR (Ultimate Vocal Remover) models and FFmpeg.
---

# Audio Karaoke & Pitch Pipeline Skill

Use this skill when a user:
1. Wants to turn a YouTube song or local audio file into a clean karaoke / instrumental backing track.
2. Needs to trim a specific section of a song (e.g. `00:58` to `02:20`) for singing or karaoke practice.
3. Finds the original song too high or low for their vocal range and needs pitch-shifted versions (e.g. `-2`, `-3`, `-4` semitones) without changing tempo.

---

## Autonomous Workflow

### Step 1: Parse Inputs & Requirements
Identify:
* **Source**: YouTube URL or local audio file path.
* **Time Range**:
  - Start time (e.g. `58`, `00:58`, `00:00:58`)
  - End time (e.g. `2:20`, `00:02:20`, `140`)
  - (Omit if user wants the full song).
* **Vocal Profile & Semitone Shifts**:
  - Default: Generates **2 curated versions** tailored to the user's vocal range (e.g. for the 110 Hz – 240 Hz baritone range):
    - **`-2` semitones**: Moderate drop (1 whole step down) preserving bright energy while shaving off peak strain.
    - **`-4` semitones**: Comfort drop (2 whole steps down) fitting comfortably within the singer's natural chest voice.
  - Custom shifts can be provided if requested (e.g. `-3`, `+2`).
* **Output Destination**:
  - Defaults to `~/Downloads/<Song_Title>_Karaoke/` or `/Users/sarathavasarala/Downloads`.

---

### Step 2: Execute Pipeline Runner Script

Run the dedicated pipeline script:

```bash
/opt/anaconda3/bin/python .agents/skills/audio-karaoke/scripts/process_karaoke.py \
  --input "<YOUTUBE_URL_OR_FILE_PATH>" \
  --start "<START_TIME>" \
  --end "<END_TIME>" \
  --shifts "-2,-4" \
  --output-dir "$HOME/Downloads"
```

*Example for full song:*
```bash
/opt/anaconda3/bin/python .agents/skills/audio-karaoke/scripts/process_karaoke.py \
  --input "https://www.youtube.com/watch?v=..." \
  --shifts "-2,-4" \
  --output-dir "$HOME/Downloads"
```

---

### Step 3: Verify Output Files

Check that the generated files exist in the output directory:
- Clean Instrumental: `[Song Title]_(Instrumental)_[Original_Key].mp3`
- Pitch Variations: `[Song Title]_(Instrumental)_[-2_semitones].mp3`, etc.
- Isolated Vocals: `[Song Title]_(Vocals).mp3` (retained for reference).

---

### Step 4: Deliver to User

Provide clickable file paths to all generated versions in markdown format and explain the musical transposition:
* State what the original key was.
* Explain which shift corresponds to which musical key and why it fits their vocal range.
