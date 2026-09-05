import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .audio import load_audio, analyze_audio
from .disc import create_vinyl_disc
from .canvas import create_canvas

def render_visualizer_video(
    audio_path,
    output_path,
    bg_path=None,
    title="",
    subtitle="",
    aspect="9:16",
    fps=30,
    num_bars=64,
    disc_radius=260,
    progress_callback=None
):
    """
    Renders an audio-reactive visualizer video streamed directly into FFmpeg.
    """
    # 1. Dimensions
    if aspect == "1:1":
        width, height = 1080, 1080
        cx, cy = 540, 540
    else:  # default 9:16 vertical (Reels / Stories)
        width, height = 1080, 1920
        cx, cy = 540, 1030

    # 2. Audio Processing
    samples, sr = load_audio(audio_path)
    bar_heights, rms_levels, duration = analyze_audio(samples, sr, fps=fps, num_bars=num_bars)
    total_frames = int(duration * fps)

    # 3. Canvas & Vinyl Preparation
    base_canvas = create_canvas(width, height, cx, cy, bg_path=bg_path, title=title, subtitle=subtitle)
    vinyl_disc, vinyl_sheen = create_vinyl_disc(disc_r=disc_radius)

    wave_inner_r = disc_radius + 8

    # Precalculate trigonometric tables
    thetas = [(i / num_bars) * 2 * math.pi - math.pi / 2 for i in range(num_bars)]
    cos_thetas = np.array([math.cos(th) for th in thetas], dtype=np.float32)
    sin_thetas = np.array([math.sin(th) for th in thetas], dtype=np.float32)

    # Pre-position layers for fast compositing
    dest_pos = (cx - disc_radius, cy - disc_radius)

    # 4. Setup FFmpeg streaming pipe
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-",               # Stream from Python stdin
        "-i", audio_path,        # Input audio
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "faster",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        output_path
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # 5. Render Loop
        for f in range(total_frames):
            t = f / fps
            bars = bar_heights[f]
            rms = rms_levels[f]

            frame = base_canvas.copy()

            # Dynamic ambient backlight breathing
            halo_alpha = int(np.clip(rms * 420, 15, 85))
            backlight = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bl_draw = ImageDraw.Draw(backlight)
            for r in range(disc_radius + 110, disc_radius, -15):
                a = int(halo_alpha * (1.0 - (r - disc_radius) / 110.0)**1.5)
                bl_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 160, 60, a))
            backlight = backlight.filter(ImageFilter.GaussianBlur(20))
            frame = Image.alpha_composite(frame, backlight)

            # Draw wave bars
            wave_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            wg_draw = ImageDraw.Draw(wave_layer)

            for i in range(num_bars):
                h = bars[i]
                r1 = wave_inner_r
                r2 = wave_inner_r + h
                c_th = cos_thetas[i]
                s_th = sin_thetas[i]

                x1 = cx + r1 * c_th
                y1 = cy + r1 * s_th
                x2 = cx + r2 * c_th
                y2 = cy + r2 * s_th

                ratio = min(1.0, (h - 6.0) / 60.0)
                r_col = int(222 + 33 * ratio)
                g_col = int(170 + 48 * ratio)
                b_col = int(90 + 60 * ratio)
                alpha = int(180 + 75 * ratio)

                # 4px width bar with rounded 2px pill cap
                wg_draw.line([(x1, y1), (x2, y2)], fill=(r_col, g_col, b_col, alpha), width=4)
                wg_draw.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=(r_col, g_col, b_col, alpha))

            # Restrained Bloom to Bars (30% alpha Gaussian spill)
            bloom = wave_layer.filter(ImageFilter.GaussianBlur(8))
            bloom.putalpha(bloom.getchannel("A").point(lambda a: int(a * 0.30)))
            frame = Image.alpha_composite(frame, bloom)
            frame = Image.alpha_composite(frame, wave_layer)

            # Rotate solid disc underneath stationary sheen
            rotation_deg = (t * 24.0) % 360.0
            rotated_disc = vinyl_disc.rotate(rotation_deg, resample=Image.Resampling.BICUBIC)

            try:
                frame.alpha_composite(rotated_disc, dest=dest_pos)
            except (TypeError, AttributeError):
                disc_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                disc_layer.paste(rotated_disc, dest_pos)
                frame = Image.alpha_composite(frame, disc_layer)

            # Composite stationary sheen highlight
            try:
                frame.alpha_composite(vinyl_sheen, dest=dest_pos)
            except (TypeError, AttributeError):
                sheen_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                sheen_layer.paste(vinyl_sheen, dest_pos)
                frame = Image.alpha_composite(frame, sheen_layer)

            proc.stdin.write(frame.tobytes())

            if progress_callback:
                progress_callback(f + 1, total_frames)

    finally:
        proc.stdin.close()
        proc.wait()

    return output_path
