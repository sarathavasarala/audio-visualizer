import unittest
import os
import tempfile
import json
from PIL import Image
from visualizer.lyrics import LyricCue, load_lyrics, parse_lrc_file, LyricRenderer

class TestLyrics(unittest.TestCase):
    def test_load_lyrics_from_list(self):
        data = [
            {"start": 1.0, "end": 4.0, "text": "Line 1", "subtext": "Sub 1"},
            {"start": 5.0, "end": 8.0, "text": "Line 2"}
        ]
        cues = load_lyrics(data)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0].text, "Line 1")
        self.assertEqual(cues[0].subtext, "Sub 1")
        self.assertEqual(cues[1].text, "Line 2")
        self.assertEqual(cues[1].subtext, "")

    def test_load_lyrics_from_json_file(self):
        data = [{"start": 0.0, "end": 3.0, "text": "Hello World"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_name = f.name

        try:
            cues = load_lyrics(temp_name)
            self.assertEqual(len(cues), 1)
            self.assertEqual(cues[0].text, "Hello World")
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    def test_load_lyrics_from_lrc_file(self):
        lrc_content = """[00:01.50]First line
[00:05.00]Second line
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".lrc", delete=False) as f:
            f.write(lrc_content)
            temp_name = f.name

        try:
            cues = load_lyrics(temp_name)
            self.assertEqual(len(cues), 2)
            self.assertAlmostEqual(cues[0].start_sec, 1.5, places=2)
            self.assertEqual(cues[0].text, "First line")
            self.assertAlmostEqual(cues[0].end_sec, 5.0, places=2)
            self.assertEqual(cues[1].text, "Second line")
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    def test_lyric_renderer_timings(self):
        cues = [
            LyricCue(start_sec=2.0, end_sec=6.0, text="Test Lyric", subtext="Translation")
        ]
        renderer = LyricRenderer(cues, canvas_width=1080, y_pos=1500, fade_sec=0.4)

        # Before cue (far away)
        res_before = renderer.get_overlay_for_time(0.5)
        self.assertIsNone(res_before)

        # During lead-in fade (e.g. 1.8s)
        res_fadein = renderer.get_overlay_for_time(1.8)
        self.assertIsNotNone(res_fadein)
        stamp, pos, alpha = res_fadein
        self.assertTrue(0.0 < alpha < 1.0)
        self.assertIsInstance(stamp, Image.Image)

        # In the middle of cue (e.g. 4.0s)
        res_mid = renderer.get_overlay_for_time(4.0)
        self.assertIsNotNone(res_mid)
        stamp, pos, alpha = res_mid
        self.assertAlmostEqual(alpha, 1.0, places=2)

        # During fade-out (e.g. 6.2s)
        res_fadeout = renderer.get_overlay_for_time(6.2)
        self.assertIsNotNone(res_fadeout)
        stamp, pos, alpha = res_fadeout
        self.assertTrue(0.0 < alpha < 1.0)

        # After cue
        res_after = renderer.get_overlay_for_time(8.0)
        self.assertIsNone(res_after)

    def test_alpha_compositing(self):
        cues = [LyricCue(start_sec=1.0, end_sec=3.0, text="Composite Test")]
        renderer = LyricRenderer(cues, canvas_width=1080, y_pos=1500)
        overlay = renderer.get_overlay_for_time(2.0)
        self.assertIsNotNone(overlay)

        stamp, dest_pos, alpha = overlay
        base = Image.new("RGBA", (1080, 1920), (10, 10, 10, 255))
        
        # Test applying alpha
        stamp_alpha = stamp.copy()
        if alpha < 1.0:
            a_chan = stamp_alpha.getchannel("A").point(lambda a: int(a * alpha))
            stamp_alpha.putalpha(a_chan)

        base.alpha_composite(stamp_alpha, dest=dest_pos)
        self.assertEqual(base.size, (1080, 1920))

if __name__ == "__main__":
    unittest.main()
