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

    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Error: Input audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    if args.bg and not os.path.exists(args.bg):
        print(f"Warning: Background file not found: {args.bg}. Falling back to default canvas.", file=sys.stderr)
        args.bg = None

    print(f"Rendering visualizer for: {args.audio}")
    print(f"Aspect Ratio: {args.aspect} | Framerate: {args.fps} fps | Bars: {args.bars}")
    if args.title:
        print(f"Title: {args.title} | Subtitle: {args.subtitle}")

    def on_progress(curr, total):
        if curr % 300 == 0 or curr == total:
            pct = (curr / total) * 100.0
            print(f"Progress: {curr}/{total} frames ({pct:.1f}%)", flush=True)

    out = render_visualizer_video(
        audio_path=args.audio,
        output_path=args.output,
        bg_path=args.bg,
        title=args.title,
        subtitle=args.subtitle,
        aspect=args.aspect,
        fps=args.fps,
        num_bars=args.bars,
        progress_callback=on_progress
    )

    print(f"\nSuccess! Video generated at: {out}")

if __name__ == "__main__":
    main()
