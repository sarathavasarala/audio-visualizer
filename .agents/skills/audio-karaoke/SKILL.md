---
name: audio-karaoke
description: >-
  Extracts karaoke (instrumental) tracks from YouTube videos or local audio files with optional time-range trimming,
  and generates pitch-shifted versions tailored to the singer's vocal range using UVR (Ultimate Vocal Remover) models and FFmpeg.
  Organizes all project assets (source audio, isolated vocals, original key instrumental, pitch-shifted variations) in a dedicated folder in ~/Downloads/.
---

# Audio Karaoke & Pitch Pipeline Skill

Use this skill when a user:
1. Wants to turn a YouTube song or local audio file into a clean karaoke / instrumental backing track.
2. Needs to trim a specific section of a song (e.g. `00:58` to `02:20`) for singing or karaoke practice.
3. Finds the original song too high or low for their vocal range and needs pitch-shifted versions (e.g. `-2`, `-3`, `-4` semitones) without changing tempo.

---

## Autonomous Workflow

### Step 1: Parse Inputs & Common Destination Folder
1. **Dedicated Common Project Folder**:
   - All assets generated or used by the pipeline automatically flow into a dedicated folder inside `~/Downloads/`:
     ```bash
     mkdir -p "$HOME/Downloads/<Song_Title>_Karaoke"
     ```
   - Assets collected in this folder:
     - **Source Audio**: `<Song_Title>_source.mp3` (downloaded from YouTube or copied from local source).
     - **Trimmed Audio**: `<Song_Title>_[start-end]_trimmed.mp3` (if a time-range cut was specified).
     - **Clean Instrumental**: `<Song_Title>_(Karaoke)_Original_Key.mp3` (original unshifted backing track).
     - **Isolated Vocals**: `<Song_Title>_(Vocals).mp3` (isolated vocal stem for practice or reference).
     - **Pitch-Shifted Variations**: `<Song_Title>_(Karaoke)_[-2_semitones].mp3`, `<Song_Title>_(Karaoke)_[-4_semitones].mp3`, etc.

2. **Inputs**:
   - **Source**: YouTube URL or local audio file path.
   - **Time Range**:
     - Start time (e.g. `58`, `00:58`, `00:00:58`)
     - End time (e.g. `2:20`, `00:02:20`, `140`)
     - (Omit if user wants the full song).
   - **Vocal Profile & Semitone Shifts**:
     - Default: Generates **2 curated versions** tailored to the user's vocal range (e.g. for the 110 Hz – 240 Hz baritone range):
       - **`-2` semitones**: Moderate drop (1 whole step down) preserving bright energy while shaving off peak strain.
       - **`-4` semitones**: Comfort drop (2 whole steps down) fitting comfortably within the singer's natural chest voice.
     - Custom shifts can be provided if requested (e.g. `-3`, `+2`).

---

### Step 2: Execute Pipeline Runner Script

Run the dedicated pipeline script (it will automatically create the dedicated `<Track_Title>_Karaoke/` directory inside `--output-dir`):

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

Verify that all assets exist in the common project folder:
```bash
ls -lh "$HOME/Downloads/<Song_Title>_Karaoke"
```
Expected assets:
- `[Song Title]_source.mp3`
- `[Song Title]_[start-end]_trimmed.mp3` *(if trimmed)*
- `[Song Title]_(Karaoke)_Original_Key.mp3`
- `[Song Title]_(Vocals).mp3`
- `[Song Title]_(Karaoke)_[-2_semitones].mp3`
- `[Song Title]_(Karaoke)_[-4_semitones].mp3`

---

### Step 4: Deliver to User

Provide clickable file paths to all generated versions in markdown format and explain the musical transposition:
* State what the original key was.
* Explain which shift corresponds to which musical key and why it fits their vocal range.
