import os
import json
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from .canvas import get_system_font

@dataclass
class LyricCue:
    start_sec: float
    end_sec: float
    text: str
    subtext: str = ""

def load_lyrics(lyrics_source) -> List[LyricCue]:
    """
    Loads lyric cues from a JSON file path, list of dicts, or LRC file path.
    """
    if isinstance(lyrics_source, list):
        cues = []
        for item in lyrics_source:
            cues.append(LyricCue(
                start_sec=float(item.get("start", item.get("start_sec", 0.0))),
                end_sec=float(item.get("end", item.get("end_sec", 0.0))),
                text=item.get("text", "").strip(),
                subtext=item.get("subtext", "").strip()
            ))
        return sorted(cues, key=lambda c: c.start_sec)

    if isinstance(lyrics_source, str):
        if not os.path.exists(lyrics_source):
            raise FileNotFoundError(f"Lyrics file not found: {lyrics_source}")
        
        if lyrics_source.endswith(".json"):
            with open(lyrics_source, "r", encoding="utf-8") as f:
                data = json.load(f)
            return load_lyrics(data)
        
        elif lyrics_source.endswith(".lrc"):
            return parse_lrc_file(lyrics_source)
        
        else:
            # Attempt to parse as JSON first
            try:
                with open(lyrics_source, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return load_lyrics(data)
            except json.JSONDecodeError:
                return parse_lrc_file(lyrics_source)

    raise ValueError(f"Unsupported lyrics source type: {type(lyrics_source)}")

def parse_lrc_file(file_path: str) -> List[LyricCue]:
    """
    Parses a standard .lrc file into LyricCue objects.
    """
    cues = []
    lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("["):
                continue
            # Format: [mm:ss.xx] Lyric text
            try:
                tag_end = line.find("]")
                if tag_end == -1:
                    continue
                time_str = line[1:tag_end]
                text = line[tag_end + 1:].strip()
                parts = time_str.split(":")
                if len(parts) == 2:
                    minutes = float(parts[0])
                    seconds = float(parts[1])
                    t_sec = minutes * 60.0 + seconds
                    lines.append((t_sec, text))
            except Exception:
                continue

    lines.sort(key=lambda x: x[0])
    for i, (t_sec, text) in enumerate(lines):
        if i + 1 < len(lines):
            end_sec = lines[i + 1][0]
        else:
            end_sec = t_sec + 4.0
        cues.append(LyricCue(start_sec=t_sec, end_sec=end_sec, text=text))

    return cues

class LyricRenderer:
    """
    Manages pre-rendered cached lyric cue images with smooth alpha transitions.
    """
    def __init__(
        self,
        cues: List[LyricCue],
        canvas_width: int = 1080,
        y_pos: int = 1530,
        fade_sec: float = 0.35,
        font_size_main: int = 36,
        font_size_sub: int = 21
    ):
        self.cues = cues
        self.canvas_width = canvas_width
        self.y_pos = y_pos
        self.fade_sec = fade_sec
        self.font_main = get_system_font(font_size_main, bold=True)
        self.font_sub = get_system_font(font_size_sub, bold=False)
        self._cached_stamps = {}
        self._pre_render_cues()

    def _pre_render_cues(self):
        """
        Pre-renders each lyric cue into an RGBA stamp with drop shadow.
        """
        for idx, cue in enumerate(self.cues):
            stamp, dest_xy = self._create_cue_stamp(cue)
            self._cached_stamps[idx] = (stamp, dest_xy)

    def _create_cue_stamp(self, cue: LyricCue) -> Tuple[Image.Image, Tuple[int, int]]:
        dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(dummy_img)

        # Spacing / tracking
        spacing_main = 5
        main_chars = list(cue.text)
        main_widths = [draw.textbbox((0, 0), ch, font=self.font_main)[2] for ch in main_chars]
        main_w = sum(main_widths) + max(0, len(main_chars) - 1) * spacing_main
        main_bbox = draw.textbbox((0, 0), cue.text or "A", font=self.font_main)
        main_h = main_bbox[3] - main_bbox[1]

        sub_w, sub_h = 0, 0
        spacing_sub = 3
        if cue.subtext:
            sub_chars = list(cue.subtext)
            sub_widths = [draw.textbbox((0, 0), ch, font=self.font_sub)[2] for ch in sub_chars]
            sub_w = sum(sub_widths) + max(0, len(sub_chars) - 1) * spacing_sub
            sub_bbox = draw.textbbox((0, 0), cue.subtext, font=self.font_sub)
            sub_h = sub_bbox[3] - sub_bbox[1]

        pad_x = 40
        pad_y = 25
        gap = 14 if cue.subtext else 0

        stamp_w = max(main_w, sub_w) + pad_x * 2
        stamp_h = main_h + (gap + sub_h if cue.subtext else 0) + pad_y * 2

        stamp = Image.new("RGBA", (stamp_w, stamp_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(stamp)

        # Draw soft shadow layer for legibility
        shadow_stamp = Image.new("RGBA", (stamp_w, stamp_h), (0, 0, 0, 0))
        sh_draw = ImageDraw.Draw(shadow_stamp)

        # Draw main text shadow
        cx = stamp_w / 2.0
        curr_x = cx - main_w / 2.0
        y_text = pad_y
        for ch, w in zip(main_chars, main_widths):
            sh_draw.text((curr_x, y_text + 2), ch, font=self.font_main, fill=(0, 0, 0, 200))
            curr_x += w + spacing_main

        # Draw subtext shadow
        if cue.subtext:
            y_sub = y_text + main_h + gap
            curr_x_sub = cx - sub_w / 2.0
            for ch, w in zip(sub_chars, sub_widths):
                sh_draw.text((curr_x_sub, y_sub + 2), ch, font=self.font_sub, fill=(0, 0, 0, 180))
                curr_x_sub += w + spacing_sub

        shadow_stamp = shadow_stamp.filter(ImageFilter.GaussianBlur(4))
        stamp = Image.alpha_composite(stamp, shadow_stamp)
        s_draw = ImageDraw.Draw(stamp)

        # Draw crisp main text (Warm candlelight ivory)
        curr_x = cx - main_w / 2.0
        for ch, w in zip(main_chars, main_widths):
            s_draw.text((curr_x, y_text), ch, font=self.font_main, fill=(252, 248, 240, 255))
            curr_x += w + spacing_main

        # Draw crisp subtext (Muted warm gold)
        if cue.subtext:
            y_sub = y_text + main_h + gap
            curr_x_sub = cx - sub_w / 2.0
            for ch, w in zip(sub_chars, sub_widths):
                s_draw.text((curr_x_sub, y_sub), ch, font=self.font_sub, fill=(220, 192, 145, 230))
                curr_x_sub += w + spacing_sub

        dest_x = int((self.canvas_width - stamp_w) / 2)
        dest_y = int(self.y_pos - stamp_h / 2)

        return stamp, (dest_x, dest_y)

    def get_overlay_for_time(self, t: float) -> Optional[Tuple[Image.Image, Tuple[int, int], float]]:
        """
        Finds active cue for time t and computes eased alpha [0.0, 1.0].
        Returns (stamp_img, dest_pos, alpha) or None if silence.
        """
        for idx, cue in enumerate(self.cues):
            # Check within cue interval with fade margins
            if cue.start_sec - self.fade_sec <= t <= cue.end_sec + self.fade_sec:
                dur = cue.end_sec - cue.start_sec
                fade = min(self.fade_sec, dur / 2.0) if dur > 0 else 0.1

                if t < cue.start_sec:
                    # Lead-in fade
                    linear_a = max(0.0, (t - (cue.start_sec - fade)) / fade)
                elif t > cue.end_sec:
                    # Lead-out fade
                    linear_a = max(0.0, ((cue.end_sec + fade) - t) / fade)
                elif t < cue.start_sec + fade:
                    # In-boundary fade-in
                    linear_a = (t - cue.start_sec) / fade
                elif t > cue.end_sec - fade:
                    # Out-boundary fade-out
                    linear_a = (cue.end_sec - t) / fade
                else:
                    linear_a = 1.0

                # Sinusoidal easing
                eased_a = 0.5 * (1.0 - math.cos(math.pi * max(0.0, min(1.0, linear_a))))
                if eased_a > 0.005:
                    stamp, dest_pos = self._cached_stamps[idx]
                    return stamp, dest_pos, eased_a

        return None
