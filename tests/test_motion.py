import unittest
import numpy as np
from visualizer.motion import MotionConfig, build_circular_distribution_matrix, shape_bar_motion
from visualizer.audio import analyze_audio, extract_audio_features

class TestBarMotion(unittest.TestCase):
    def setUp(self):
        self.sr = 44100
        self.duration = 2.0
        self.t = np.linspace(0, self.duration, int(self.sr * self.duration), endpoint=False)

    def test_silence_returns_resting_baseline(self):
        """Verify that pure silence returns exactly the resting baseline height (6.0 px)."""
        silence = np.zeros_like(self.t, dtype=np.float32)
        bars, rms, dur = analyze_audio(silence, self.sr, fps=30, num_bars=64)
        
        self.assertEqual(bars.shape, (int(self.duration * 30), 64))
        # All bars must be finite and equal to resting baseline (6.0 px)
        self.assertTrue(np.all(np.isfinite(bars)))
        self.assertTrue(np.allclose(bars, 6.0, atol=1e-3), f"Expected 6.0 baseline, got max {bars.max()}")

    def test_bounded_finite_heights(self):
        """Verify that heights are strictly finite and bounded within [6.0, 78.0] under extreme signal."""
        extreme = np.random.uniform(-10.0, 10.0, len(self.t)).astype(np.float32)
        bars, rms, dur = analyze_audio(extreme, self.sr, fps=30, num_bars=64)
        
        self.assertTrue(np.all(np.isfinite(bars)))
        self.assertTrue(np.all(bars >= 6.0), f"Found bar height < 6.0: {bars.min()}")
        self.assertTrue(np.all(bars <= 78.0), f"Found bar height > 78.0: {bars.max()}")

    def test_low_and_high_tones_and_balanced_motion(self):
        """
        Verify that both low tones (60Hz) and high tones (3500Hz) cause breathing motion across the ring,
        and that no region exclusively represents bass or treble.
        """
        low_tone = (0.5 * np.sin(2 * np.pi * 60 * self.t)).astype(np.float32)
        high_tone = (0.5 * np.sin(2 * np.pi * 3500 * self.t)).astype(np.float32)

        bars_low, _, _ = analyze_audio(low_tone, self.sr, fps=30, num_bars=64)
        bars_high, _, _ = analyze_audio(high_tone, self.sr, fps=30, num_bars=64)

        # Steady-state frame near 1.0 second
        f_mid = int(1.0 * 30)
        h_low = bars_low[f_mid]
        h_high = bars_high[f_mid]

        # In both cases, every single bar must be well above baseline (> 15 px) due to 65% shared breathing
        self.assertTrue(np.all(h_low > 15.0), f"Low tone has frozen bars: min is {h_low.min()}")
        self.assertTrue(np.all(h_high > 15.0), f"High tone has frozen bars: min is {h_high.min()}")

        # Check ratio of max to min bar height in the ring:
        # Should show clear organic variation, but neither side should be completely flat or 10x dominant
        ratio_low = h_low.max() / h_low.min()
        ratio_high = h_high.max() / h_high.min()
        self.assertLess(ratio_low, 2.5, f"Low tone ratio too extreme: {ratio_low}")
        self.assertLess(ratio_high, 2.5, f"High tone ratio too extreme: {ratio_high}")

    def test_circular_seamlessness(self):
        """Verify seamless wrap between bar 0 and bar num_bars-1."""
        W = build_circular_distribution_matrix(num_bars=64, num_bands=24)
        diff_wrap = np.max(np.abs(W[0] - W[-1]))
        diff_neighbor = np.max(np.abs(W[1] - W[0]))
        # The wrap difference should be smooth, of comparable size to adjacent bars
        self.assertLess(diff_wrap, diff_neighbor * 2.0)

    def test_no_rigid_mirrored_halves(self):
        """Verify that the circular distribution is not a rigid bilateral mirror."""
        W = build_circular_distribution_matrix(num_bars=64, num_bands=24)
        mirror_diff = np.max(np.abs(W - W[::-1]))
        self.assertGreater(mirror_diff, 0.01, "Circular matrix is a rigid mirror")

    def test_amplitude_pulse_smooth_decay(self):
        """Verify smooth decay without sudden drops or oscillation after an amplitude pulse."""
        pulse = np.zeros_like(self.t, dtype=np.float32)
        # 300ms burst of 220Hz tone
        pulse[int(0.2 * self.sr):int(0.5 * self.sr)] = 0.6 * np.sin(2 * np.pi * 220 * self.t[:int(0.3 * self.sr)])
        
        bars, _, _ = analyze_audio(pulse, self.sr, fps=30, num_bars=64)
        
        # During pulse (t=0.35s, frame ~10), height should be elevated
        f_pulse = int(0.35 * 30)
        self.assertGreater(bars[f_pulse].mean(), 30.0)

        # Decay frames after pulse shuts off (t=0.55s onwards)
        f_start_decay = int(0.55 * 30)
        decay_means = [bars[f].mean() for f in range(f_start_decay, len(bars))]
        
        # Monotonically decreasing decay (smooth release)
        for i in range(len(decay_means) - 1):
            self.assertLessEqual(decay_means[i + 1], decay_means[i] + 1e-4)

        # By the end of 2 seconds (1.5s after pulse shutoff), should be back at baseline 6.0 px
        self.assertAlmostEqual(bars[-1].mean(), 6.0, delta=0.05)

    def test_framerate_timing_consistency_30_vs_60_fps(self):
        """Verify comparable motion timing at 30 fps and 60 fps."""
        pulse = np.zeros_like(self.t, dtype=np.float32)
        pulse[int(0.2 * self.sr):int(0.4 * self.sr)] = 0.5 * np.sin(2 * np.pi * 300 * self.t[:int(0.2 * self.sr)])

        bars_30, _, _ = analyze_audio(pulse, self.sr, fps=30, num_bars=64)
        bars_60, _, _ = analyze_audio(pulse, self.sr, fps=60, num_bars=64)

        # Check decay at real-world time points t = 0.6s, 0.8s, 1.0s
        for t_check in [0.6, 0.8, 1.0]:
            f30 = int(t_check * 30)
            f60 = int(t_check * 60)
            mean30 = bars_30[f30].mean()
            mean60 = bars_60[f60].mean()
            diff = abs(mean30 - mean60)
            self.assertLess(diff, 2.5, f"Timing discrepancy at t={t_check}s: 30fps={mean30:.2f}, 60fps={mean60:.2f}")

    def test_validation_errors(self):
        """Verify proper validation errors for empty audio, short duration, invalid fps, unsupported bar counts."""
        # Empty audio
        with self.assertRaises(ValueError):
            analyze_audio(np.array([], dtype=np.float32), self.sr, fps=30, num_bars=64)

        # Very short audio (< 0.1s)
        with self.assertRaises(ValueError):
            short = np.ones(int(0.05 * self.sr), dtype=np.float32)
            analyze_audio(short, self.sr, fps=30, num_bars=64)

        # Invalid fps
        with self.assertRaises(ValueError):
            analyze_audio(self.t[:self.sr], self.sr, fps=0, num_bars=64)
        with self.assertRaises(ValueError):
            analyze_audio(self.t[:self.sr], self.sr, fps=-10, num_bars=64)
        with self.assertRaises(ValueError):
            analyze_audio(self.t[:self.sr], self.sr, fps=200, num_bars=64)

        # Unsupported bar count
        with self.assertRaises(ValueError):
            analyze_audio(self.t[:self.sr], self.sr, fps=30, num_bars=8)
        with self.assertRaises(ValueError):
            analyze_audio(self.t[:self.sr], self.sr, fps=30, num_bars=512)

    def test_mixed_frequencies(self):
        """Verify that mixed audio containing bass, mids, and treble creates a balanced, organic response."""
        mixed = (
            0.4 * np.sin(2 * np.pi * 80 * self.t) +
            0.3 * np.sin(2 * np.pi * 800 * self.t) +
            0.2 * np.sin(2 * np.pi * 5000 * self.t)
        ).astype(np.float32)

        bars, rms, dur = analyze_audio(mixed, self.sr, fps=30, num_bars=64)
        f_mid = int(1.0 * 30)
        h = bars[f_mid]

        self.assertTrue(np.all(h >= 20.0), f"All bars should be active, min was {h.min()}")
        self.assertTrue(np.all(h <= 78.0), f"No bar should exceed 78, max was {h.max()}")
        # Check standard deviation around the circle: should have subtle organic ripple (between 1 and 8 px)
        self.assertGreater(float(np.std(h)), 0.5)
        self.assertLess(float(np.std(h)), 10.0)

    def test_soft_saturation_no_hard_clipping(self):
        """Verify soft saturation preserves headroom without flattening peaks into a flat ceiling."""
        config = MotionConfig()
        t_dyn = np.linspace(0, 3.0, int(3.0 * self.sr), endpoint=False)
        signal = np.zeros_like(t_dyn, dtype=np.float32)
        # Normal section (0 - 1.5s)
        signal[:int(1.5 * self.sr)] = 0.3 * np.sin(2 * np.pi * 150 * t_dyn[:int(1.5 * self.sr)])
        # Loud peak section (1.5 - 2.5s)
        signal[int(1.5 * self.sr):int(2.5 * self.sr)] = 1.0 * np.sin(2 * np.pi * 150 * t_dyn[int(1.5 * self.sr):int(2.5 * self.sr)])
        # Massive peak section (2.5 - 3.0s)
        signal[int(2.5 * self.sr):] = 2.5 * np.sin(2 * np.pi * 150 * t_dyn[int(2.5 * self.sr):])

        bars, _, _ = analyze_audio(signal, self.sr, fps=30, num_bars=64, config=config)

        max_normal = bars[int(0.8 * 30)].max()
        max_loud = bars[int(2.0 * 30)].max()
        max_massive = bars[int(2.8 * 30)].max()

        # Louder peaks must strictly produce higher bar heights (smooth saturation, not flat clipping)
        self.assertGreater(max_loud, max_normal + 5.0)
        self.assertGreater(max_massive, max_loud + 2.0)
        # But must still stay strictly bounded within max_height
        self.assertLessEqual(max_massive, 78.0)

    def test_top_and_bottom_balance(self):
        """Verify top does not disproportionately dominate bottom."""
        # Multi-tone acoustic simulation
        music = (
            0.4 * np.sin(2 * np.pi * 100 * self.t) +
            0.3 * np.sin(2 * np.pi * 1200 * self.t) +
            0.2 * np.sin(2 * np.pi * 4000 * self.t)
        ).astype(np.float32)

        bars, _, _ = analyze_audio(music, self.sr, fps=30, num_bars=64)
        f_mid = int(1.0 * 30)
        h = bars[f_mid]

        # Top sector (around bar 0: bars -2, -1, 0, 1, 2)
        top_indices = [62, 63, 0, 1, 2]
        # Bottom sector (around bar 32: bars 30, 31, 32, 33, 34)
        bottom_indices = [30, 31, 32, 33, 34]

        top_mean = h[top_indices].mean()
        bottom_mean = h[bottom_indices].mean()

        ratio = top_mean / bottom_mean
        # In old visualizer, top reacted wildly while bottom was quiet; now they should be well-balanced (0.6 to 1.6)
        self.assertGreater(ratio, 0.6, f"Top under-reacts relative to bottom: ratio {ratio:.2f}")
        self.assertLess(ratio, 1.6, f"Top over-reacts relative to bottom: ratio {ratio:.2f}")

    def test_end_to_end_render(self):
        """Verify that render_visualizer_video produces a valid MP4 with video and audio streams."""
        import os
        import tempfile
        import subprocess
        from scipy.io import wavfile
        from visualizer.engine import render_visualizer_video

        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, "test_input.wav")
            out_path = os.path.join(tmpdir, "test_output.mp4")

            # 1.0s synthetic audio
            audio_data = (0.4 * np.sin(2 * np.pi * 220 * self.t[:self.sr])).astype(np.float32)
            wavfile.write(wav_path, self.sr, (audio_data * 32767).astype(np.int16))

            render_visualizer_video(
                audio_path=wav_path,
                output_path=out_path,
                aspect="1:1",
                fps=30,
                num_bars=32
            )

            self.assertTrue(os.path.exists(out_path))
            self.assertGreater(os.path.getsize(out_path), 1000)

            # ffprobe validation
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,codec_name",
                "-of", "csv=p=0",
                out_path
            ]
            res = subprocess.check_output(cmd, text=True).strip()
            self.assertIn("1080", res)
            self.assertIn("h264", res)

if __name__ == "__main__":
    unittest.main()
