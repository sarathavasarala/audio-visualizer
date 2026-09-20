import argparse
import os
import sys
from .engine import render_visualizer_video

def main():
    parser = argparse.ArgumentParser(
        description="Audio Visualizer - Generate aesthetic audio-reactive Instagram videos from an audio file."
    )
    parser.add_argument("--audio", "-a", required=True, help="Path to input audio file (.mp3, .wav, .m4a, etc.)")
    parser.add_argument("--output", "-o", default="output.mp4", help="Path to destination MP4 file (default: output.mp4)")
    parser.add_argument("--bg", "-b", default=None, help="Optional path to background image")
    parser.add_argument("--title", "-t", default="", help="Song or piece title")
    parser.add_argument("--subtitle", "-s", default="", help="Subtitle, artist, or cover credit")
    parser.add_argument("--aspect", choices=["9:16", "1:1"], default="9:16", help="Video aspect ratio (default: 9:16)")
    parser.add_argument("--fps", type=int, default=30, help="Video frame rate (default: 30)")
    parser.add_argument("--bars", type=int, default=64, help="Number of radial wave bars (default: 64)")
    parser.add_argument("--lyrics", "-l", default=None, help="Optional path to lyrics file (.json or .lrc)")
    parser.add_argument("--export-dir", default=None, help="Directory to export all project assets (cover art, audio, output video, lyrics)")

    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Error: Input audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    if args.lyrics and not os.path.exists(args.lyrics):
        print(f"Error: Lyrics file not found: {args.lyrics}", file=sys.stderr)
        sys.exit(1)

    if args.fps < 1 or args.fps > 120:
        print(f"Error: Invalid FPS: {args.fps}. Supported frame rate is between 1 and 120.", file=sys.stderr)
        sys.exit(1)

    if args.bars < 16 or args.bars > 256:
        print(f"Error: Unsupported bar count: {args.bars}. Supported bar count is between 16 and 256.", file=sys.stderr)
        sys.exit(1)

    if args.bg and not os.path.exists(args.bg):
        print(f"Warning: Background file not found: {args.bg}. Falling back to default canvas.", file=sys.stderr)
        args.bg = None

    print(f"Rendering visualizer for: {args.audio}")
    print(f"Aspect Ratio: {args.aspect} | Framerate: {args.fps} fps | Bars: {args.bars}")
    if args.title:
        print(f"Title: {args.title} | Subtitle: {args.subtitle}")
    if args.lyrics:
        print(f"Lyrics: {args.lyrics}")

    def on_progress(curr, total):
        if curr % 300 == 0 or curr == total:
            pct = (curr / total) * 100.0
            print(f"Progress: {curr}/{total} frames ({pct:.1f}%)", flush=True)

    try:
        out = render_visualizer_video(
            audio_path=args.audio,
            output_path=args.output,
            bg_path=args.bg,
            title=args.title,
            subtitle=args.subtitle,
            aspect=args.aspect,
            fps=args.fps,
            num_bars=args.bars,
            progress_callback=on_progress,
            lyrics=args.lyrics
        )
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nSuccess! Video generated at: {out}")

    if args.export_dir:
        import shutil
        exp_dir = os.path.expanduser(args.export_dir)
        os.makedirs(exp_dir, exist_ok=True)
        dest_audio = os.path.join(exp_dir, os.path.basename(args.audio))
        if os.path.abspath(args.audio) != os.path.abspath(dest_audio):
            shutil.copy2(args.audio, dest_audio)
        if args.bg and os.path.exists(args.bg):
            dest_bg = os.path.join(exp_dir, "cover_art" + os.path.splitext(args.bg)[1])
            if os.path.abspath(args.bg) != os.path.abspath(dest_bg):
                shutil.copy2(args.bg, dest_bg)
        if args.lyrics and os.path.exists(args.lyrics):
            dest_lyrics = os.path.join(exp_dir, os.path.basename(args.lyrics))
            if os.path.abspath(args.lyrics) != os.path.abspath(dest_lyrics):
                shutil.copy2(args.lyrics, dest_lyrics)
        dest_out = os.path.join(exp_dir, os.path.basename(out))
        if os.path.abspath(out) != os.path.abspath(dest_out):
            shutil.copy2(out, dest_out)
        print(f"All assets successfully exported to: {exp_dir}")

if __name__ == "__main__":
    main()
