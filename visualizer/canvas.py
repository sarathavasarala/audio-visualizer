import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_system_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Optima.ttc",
        "/System/Library/Fonts/Supplemental/Bodoni 72 OS.ttc",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_tracked_text(draw, text, center_x, y, font, fill, spacing=14):
    chars = list(text)
    char_widths = [draw.textbbox((0, 0), ch, font=font)[2] for ch in chars]
    total_w = sum(char_widths) + (len(chars) - 1) * spacing
    curr_x = center_x - total_w / 2
    for ch, w in zip(chars, char_widths):
        draw.text((curr_x, y), ch, font=font, fill=fill)
        curr_x += w + spacing

def create_canvas(width=1080, height=1920, cx=540, cy=1030, bg_path=None, title="", subtitle=""):
    """
    Creates the base visual canvas with resized background, mathematical edge vignette,
    and elegant typography.
    """
    if bg_path and os.path.exists(bg_path):
        bg_raw = Image.open(bg_path).convert("RGBA")
        scale = max(width / bg_raw.width, height / bg_raw.height)
        new_w = int(bg_raw.width * scale)
        new_h = int(bg_raw.height * scale)
        bg_resized = bg_raw.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        canvas = bg_resized.crop((left, top, left + width, top + height))
    else:
        # Generate elegant dark gradient canvas if no background image is supplied
        canvas = Image.new("RGBA", (width, height), (10, 12, 18, 255))

    # Continuous Mathematical Edge-Darkening Vignette
    yy, xx = np.mgrid[:height, :width]
    distance = np.sqrt(
        ((xx - cx) / (width * 0.70)) ** 2
        + ((yy - cy) / (height * 0.70)) ** 2
    )
    alpha = (145 * np.clip(distance, 0, 1) ** 1.8).astype(np.uint8)
    vignette = Image.new("RGBA", (width, height), (4, 6, 12, 0))
    vignette.putalpha(Image.fromarray(alpha))
    canvas = Image.alpha_composite(canvas, vignette)

    draw = ImageDraw.Draw(canvas)

    # Typography (only if title is provided)
    if title:
        font_title = get_system_font(48, bold=True)
        font_sub = get_system_font(19, bold=False)

        # In 9:16 vertical, place title above disc
        title_y = cy - 650 if height > width else cy - 420
        sub_y = title_y + 65

        draw_tracked_text(draw, title.upper(), cx, title_y, font_title, (248, 242, 234, 245), spacing=22)
        if subtitle:
            draw_tracked_text(draw, subtitle.upper(), cx, sub_y, font_sub, (212, 175, 125, 180), spacing=12)
            # Accent hairline
            line_w = 42
            draw.line([(cx - line_w, sub_y + 45), (cx + line_w, sub_y + 45)], fill=(212, 175, 125, 75), width=1)

    return canvas
