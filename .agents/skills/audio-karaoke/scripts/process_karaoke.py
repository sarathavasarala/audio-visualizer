#!/usr/bin/env python3
"""
YouTube Karaoke & Pitch-Adapted Vocal Pipeline
Autonomous script for:
1. Downloading YouTube audio or processing local audio files
2. Trimming to specified time ranges
3. Isolating clean instrumental (karaoke) and vocal stems using UVR models via audio-separator
4. Pitch-shifting the karaoke track across user-tailored keys using FFmpeg librubberband
"""

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_time_to_seconds(time_str: str) -> float:
    """Convert string like '58', '58s', '1:22', '01:22', or '00:01:22' to seconds."""
    if not time_str:
        return 0.0
    clean = time_str.strip().rstrip("sS")
    parts = clean.split(":")
    if len(parts) == 1:
        return float(parts[0])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ValueError(f"Unrecognized time format: {time_str}")


def format_seconds_to_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:06.3f}"


def run_cmd(cmd, error_msg="Command failed"):
    """Run a subprocess command and check for errors."""
    print(f"--> Running: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error output: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"{error_msg}: {result.stderr.strip()}")
    return result.stdout


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from song titles."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")


def download_or_prepare_audio(input_source: str, start_sec: float | None, end_sec: float | None, work_dir: Path) -> tuple[Path, str]:
    """Download audio from YouTube or copy/trim from local file."""
    is_url = input_source.startswith("http://") or input_source.startswith("https://")
    track_title = "Karaoke_Track"

    if is_url:
        print(f"[*] Fetching metadata and downloading from: {input_source}")
        # Get title
        try:
            raw_title = run_cmd([
                "yt-dlp", "--print", "title",
                "--extractor-args", "youtube:player_client=android",
                "--no-playlist", input_source
            ], "Failed to fetch title").strip()
            if raw_title:
                track_title = sanitize_filename(raw_title)
        except Exception:
            track_title = "youtube_track"

        raw_download_path = work_dir / "downloaded_raw.mp4"
        
        # Download format 18 (progressive audio+video) or best audio
        dl_cmd = [
            "yt-dlp",
            "-f", "18/ba/b",
            "--extractor-args", "youtube:player_client=android",
            "--no-playlist",
            "-o", str(raw_download_path),
            input_source
        ]
        run_cmd(dl_cmd, "Failed to download audio via yt-dlp")
        source_audio = raw_download_path
    else:
        local_path = Path(input_source).expanduser().resolve()
        if not local_path.exists():
            raise FileNotFoundError(f"Input file not found: {local_path}")
        track_title = sanitize_filename(local_path.stem)
        source_audio = local_path

    # Now trim if requested
    prepared_wav = work_dir / f"{track_title}_source.wav"
    ffmpeg_cmd = ["ffmpeg", "-y"]

    if start_sec is not None:
        ffmpeg_cmd.extend(["-ss", format_seconds_to_timestamp(start_sec)])
    if end_sec is not None:
        ffmpeg_cmd.extend(["-to", format_seconds_to_timestamp(end_sec)])

    ffmpeg_cmd.extend([
        "-i", str(source_audio),
        "-vn",
        "-ar", "44100",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        str(prepared_wav)
    ])

    print("[*] Trimming and converting source audio to 44.1kHz WAV...")
    run_cmd(ffmpeg_cmd, "FFmpeg trimming failed")
    return prepared_wav, track_title


def separate_vocals(input_wav: Path, work_dir: Path, model_name: str | None = None) -> tuple[Path, Path]:
    """Separate vocals and instrumental using audio-separator."""
    print("[*] Initializing AI Vocal Separation (UVR engine)...")
    from audio_separator.separator import Separator

    output_dir = work_dir / "stems"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize separator
    # Default model if not specified: UVR-MDX-NET-Inst_HQ_3.onnx or model_bs_roformer_ep_317_sdr_12.9755.ckpt
    sep_kwargs = {
        "output_dir": str(output_dir),
        "output_format": "WAV",
        "log_level": 20,  # INFO
    }
    separator = Separator(**sep_kwargs)
    
    selected_model = model_name or "UVR-MDX-NET-Inst_HQ_3.onnx"
    print(f"[*] Loading separation model: {selected_model}...")
    separator.load_model(model_filename=selected_model)

    print(f"[*] Separating stems for: {input_wav.name}...")
    separated_files = separator.separate(str(input_wav))
    print(f"[*] Raw separated files: {separated_files}")

    instrumental_file = None
    vocal_file = None

    for fname in separated_files:
        path = output_dir / fname
        lower_name = fname.lower()
        if "(instrumental)" in lower_name or "_instrumental" in lower_name:
            instrumental_file = path
        elif "(vocals)" in lower_name or "_vocals" in lower_name or "(vocal)" in lower_name:
            vocal_file = path

    # Fallback heuristic if naming differs
    if not instrumental_file and separated_files:
        for f in separated_files:
            if "voc" not in f.lower():
                instrumental_file = output_dir / f
                break
    if not vocal_file and len(separated_files) > 1:
        for f in separated_files:
            if f != (instrumental_file.name if instrumental_file else ""):
                vocal_file = output_dir / f
                break

    if not instrumental_file or not instrumental_file.exists():
        raise RuntimeError("Failed to locate separated instrumental stem.")

    return instrumental_file, vocal_file


def pitch_shift_track(instrumental_wav: Path, semitones: int, output_mp3: Path):
    """Pitch shift an instrumental track by N semitones using rubberband."""
    if semitones == 0:
        # Just convert to high-quality MP3
        cmd = [
            "ffmpeg", "-y",
            "-i", str(instrumental_wav),
            "-c:a", "libmp3lame",
            "-q:a", "2",
            str(output_mp3)
        ]
    else:
        # Scale factor = 2^(semitones / 12)
        scale = math.pow(2.0, semitones / 12.0)
        filter_str = f"rubberband=pitch={scale:.6f}:pitchq=quality"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(instrumental_wav),
            "-af", filter_str,
            "-c:a", "libmp3lame",
            "-q:a", "2",
            str(output_mp3)
        ]

    run_cmd(cmd, f"Pitch shift failed for {semitones} semitones")


def main():
    parser = argparse.ArgumentParser(description="Autonomous YouTube Karaoke & Pitch Shift Pipeline")
    parser.add_argument("--input", "-i", required=True, help="YouTube URL or local audio/video file path")
    parser.add_argument("--start", "-s", default=None, help="Start time (e.g., '58', '00:58')")
    parser.add_argument("--end", "-e", default=None, help="End time (e.g., '2:20', '02:20')")
    parser.add_argument("--shifts", default="-2,-4", help="Comma-separated semitone shifts, e.g. '-2,-4' (2 curated versions for 110-240Hz range)")
    parser.add_argument("--model", default=None, help="UVR Model name for audio-separator")
    parser.add_argument("--output-dir", "-o", default=str(Path.home() / "Downloads"), help="Destination directory")

    args = parser.parse_args()

    start_sec = parse_time_to_seconds(args.start) if args.start else None
    end_sec = parse_time_to_seconds(args.end) if args.end else None

    # Parse shifts
    shift_list = []
    for s in args.shifts.split(","):
        s = s.strip()
        if s:
            shift_list.append(int(s))

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="karaoke_pipeline_") as temp_dir_str:
        work_dir = Path(temp_dir_str)
        print(f"[*] Working directory created: {work_dir}")

        # Step 1: Download & Trim
        prepared_wav, track_title = download_or_prepare_audio(
            args.input, start_sec, end_sec, work_dir
        )

        time_tag = ""
        if start_sec is not None or end_sec is not None:
            s_str = args.start or "0s"
            e_str = args.end or "end"
            time_tag = f"_[{s_str}-{e_str}]"

        # Step 2: Separate Stems
        instrumental_wav, vocal_wav = separate_vocals(prepared_wav, work_dir, args.model)
        print(f"[+] Instrumental stem separated: {instrumental_wav.name}")

        # Save isolated vocals to destination for user reference
        if vocal_wav and vocal_wav.exists():
            dest_vocals = out_dir / f"{track_title}{time_tag}_(Vocals).mp3"
            print(f"[*] Exporting isolated vocals to: {dest_vocals}")
            run_cmd(["ffmpeg", "-y", "-i", str(vocal_wav), "-c:a", "libmp3lame", "-q:a", "2", str(dest_vocals)])

        # Step 3: Multi-Key Pitch Shifting
        generated_files = []
        for shift in shift_list:
            if shift == 0:
                tag = "Original_Key"
            elif shift > 0:
                tag = f"+{shift}_semitones"
            else:
                tag = f"{shift}_semitones"

            dest_file = out_dir / f"{track_title}{time_tag}_(Karaoke)_{tag}.mp3"
            print(f"[*] Generating {tag} track: {dest_file.name}...")
            pitch_shift_track(instrumental_wav, shift, dest_file)
            generated_files.append((shift, dest_file))

        print("\n" + "=" * 60)
        print("[+] SUCCESS! All karaoke tracks generated successfully:")
        for shift, path in generated_files:
            sign = f"+{shift}" if shift > 0 else str(shift)
            print(f"  • Shift {sign:>3} st: {path}")
        print("=" * 60)


if __name__ == "__main__":
    main()
