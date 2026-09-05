import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_vinyl_disc(disc_r=260, label_r=95, spindle_r=12):
    """
    Renders an authentic, solid vinyl record and a separate stationary specular sheen.
    
    Returns:
        disc_img: RGBA image of the vinyl record (opaque grooves, label, spindle)
        sheen_img: RGBA image of the stationary reflection highlight
    """
    size = disc_r * 2
    disc_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(disc_img)
    d_cx, d_cy = disc_r, disc_r

    # 1. Solid outer vinyl body
    d_draw.ellipse([0, 0, size, size], fill=(14, 15, 18, 255), outline=(48, 48, 58, 255), width=2)

    # 2. Opaque concentric micro-grooves (opaque so background doesn't bleed through)
    for r in range(disc_r - 10, label_r, -2):
        shade = 22 + int(12 * math.sin(r * 0.4))
        d_draw.ellipse([d_cx - r, d_cy - r, d_cx + r, d_cy + r], 
                       outline=(shade, shade, shade + 4, 255), width=1)

    # 3. Stationary sheen reflection
    sheen_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sheen_draw = ImageDraw.Draw(sheen_img)
    for angle_offset in [math.pi / 4, 5 * math.pi / 4]:
        points = [d_cx, d_cy]
        for a in np.linspace(angle_offset - 0.26, angle_offset + 0.26, 24):
            points.extend([d_cx + (disc_r - 8) * math.cos(a), d_cy + (disc_r - 8) * math.sin(a)])
        sheen_draw.polygon(points, fill=(255, 242, 220, 25))
    sheen_img = sheen_img.filter(ImageFilter.GaussianBlur(12))

    # Mask sheen so it only touches the black vinyl grooves, not the center label
    sheen_mask = Image.new("L", (size, size), 0)
    sm_draw = ImageDraw.Draw(sheen_mask)
    sm_draw.ellipse([d_cx - disc_r + 2, d_cy - disc_r + 2, d_cx + disc_r - 2, d_cy + disc_r - 2], fill=255)
    sm_draw.ellipse([d_cx - label_r, d_cy - label_r, d_cx + label_r, d_cy + label_r], fill=0)
    sheen_a = np.minimum(np.array(sheen_img.getchannel("A")), np.array(sheen_mask))
    sheen_img.putalpha(Image.fromarray(sheen_a))

    # 4. Center Label (Opaque obsidian/amber with gold trim)
    d_draw.ellipse([d_cx - label_r, d_cy - label_r, d_cx + label_r, d_cy + label_r], 
                   fill=(24, 21, 19, 255), outline=(218, 168, 85, 255), width=2)
    d_draw.ellipse([d_cx - (label_r - 6), d_cy - (label_r - 6), d_cx + (label_r - 6), d_cy + (label_r - 6)], 
                   outline=(170, 130, 60, 255), width=1)
    d_draw.ellipse([d_cx - (label_r - 16), d_cy - (label_r - 16), d_cx + (label_r - 16), d_cy + (label_r - 16)], 
                   outline=(140, 110, 50, 255), width=1)

    # Delicate gold spoke accents (rotates with disc to provide visual motion)
    for spk in range(8):
        ang = spk * (2 * math.pi / 8)
        x_s1 = d_cx + 25 * math.cos(ang)
        y_s1 = d_cy + 25 * math.sin(ang)
        x_s2 = d_cx + 70 * math.cos(ang)
        y_s2 = d_cy + 70 * math.sin(ang)
        d_draw.line([(x_s1, y_s1), (x_s2, y_s2)], fill=(190, 150, 75, 255), width=1)

    # 5. Spindle hole
    d_draw.ellipse([d_cx - spindle_r, d_cy - spindle_r, d_cx + spindle_r, d_cy + spindle_r], 
                   fill=(6, 6, 8, 255), outline=(180, 180, 190, 255), width=2)

    return disc_img, sheen_img
