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
        # In 9:16 vertical, place title above disc
        title_y = cy - 650 if height > width else cy - 420
        sub_y = title_y + 60

        # Auto-fit title to stay within safe margins (at least 80px on each side)
        max_title_w = width - 160
        title_size = 44
        title_spacing = 18
        while title_size > 22:
            f_test = get_system_font(title_size, bold=True)
            chars = list(title.upper())
            char_widths = [draw.textbbox((0, 0), ch, font=f_test)[2] for ch in chars]
            curr_w = sum(char_widths) + (len(chars) - 1) * title_spacing
            if curr_w <= max_title_w:
                break
            title_size -= 2
            title_spacing = max(6, int(18 * (title_size / 44)))

        font_title = get_system_font(title_size, bold=True)
        draw_tracked_text(draw, title.upper(), cx, title_y, font_title, (248, 242, 234, 245), spacing=title_spacing)

        if subtitle:
            max_sub_w = width - 200
            sub_size = 18
            sub_spacing = 10
            while sub_size > 14:
                f_test = get_system_font(sub_size, bold=False)
                chars = list(subtitle.upper())
                char_widths = [draw.textbbox((0, 0), ch, font=f_test)[2] for ch in chars]
                curr_w = sum(char_widths) + (len(chars) - 1) * sub_spacing
                if curr_w <= max_sub_w:
                    break
                sub_size -= 1
                sub_spacing = max(4, int(10 * (sub_size / 18)))

            font_sub = get_system_font(sub_size, bold=False)
            draw_tracked_text(draw, subtitle.upper(), cx, sub_y, font_sub, (212, 175, 125, 180), spacing=sub_spacing)
            # Accent hairline
            line_w = 42
            draw.line([(cx - line_w, sub_y + 40), (cx + line_w, sub_y + 40)], fill=(212, 175, 125, 75), width=1)

    return canvas
