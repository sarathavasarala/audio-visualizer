import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.ndimage import gaussian_filter1d

def load_audio(audio_path, target_sr=44100):
    """
    Decodes audio to a 44.1kHz mono float32 numpy array using ffmpeg.
    """
    cmd = [
        "ffmpeg", "-v", "error", "-i", audio_path,
        "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "-"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_data, _ = proc.communicate()
    
    if proc.returncode != 0 or len(raw_data) == 0:
        raise RuntimeError(f"Failed to decode audio file: {audio_path}")
        
    samples = np.frombuffer(raw_data, dtype=np.float32)
    return samples, target_sr

def analyze_audio(samples, sr, fps=30, num_bars=64, min_freq=130, max_freq=3600, window_size=4096):
    """
    Analyzes audio using a 4096-point FFT with centered zero-padded windows,
    track-wide 98th-percentile normalization, and attack/decay temporal smoothing.
    
    Returns:
        all_bar_heights: (total_frames, num_bars) float32 array of bar heights (in pixels)
        all_rms: (total_frames,) float32 array of RMS energy for ambient backlight pulsation
        duration: audio duration in seconds
    """
    half_bars = num_bars // 2
    duration = len(samples) / sr
    total_frames = int(duration * fps)

    # Logarithmic frequency boundaries
    band_limits = np.geomspace(min_freq, max_freq, half_bars + 1)
    hanning = np.hanning(window_size)
    freqs = np.fft.rfftfreq(window_size, 1.0 / sr)

    masks = []
    for i in range(half_bars):
        f_low, f_high = band_limits[i], band_limits[i+1]
        masks.append((freqs >= f_low) & (freqs < f_high))

    # Center zero-padded audio
    padded = np.pad(samples, (window_size // 2, window_size // 2))

    all_rms = np.zeros(total_frames, dtype=np.float32)
    spectrum = np.zeros((total_frames, half_bars), dtype=np.float32)

    # Pass 1: High-resolution spectral analysis across the track
    for f in range(total_frames):
        center_sample = round(f * sr / fps)
        chunk = padded[center_sample:center_sample + window_size]

        rms = np.sqrt(np.mean(chunk**2)) if len(chunk) > 0 else 0.0
        all_rms[f] = rms

        fft_vals = np.abs(np.fft.rfft(chunk * hanning))
        magnitudes = [np.mean(fft_vals[m]) if np.any(m) else 0.0 for m in masks]
        magnitudes = gaussian_filter1d(magnitudes, sigma=1.0)
        spectrum[f] = magnitudes

    # Pass 2: Track-wide 98th-percentile normalization
    reference = max(float(np.percentile(spectrum, 98)), 1e-8)
    prev_smoothed = np.zeros(num_bars, dtype=np.float32)
    all_bar_heights = np.zeros((total_frames, num_bars), dtype=np.float32)

    attack_alpha = 0.60
    decay_alpha = 0.82

    for f in range(total_frames):
        level = np.clip(spectrum[f] / reference, 0.0, 1.0)
        m_scaled = 72.0 * np.log1p(8.0 * level) / np.log1p(8.0)

        # Mirrored symmetrical spectrum
        raw_bars = np.concatenate([m_scaled[::-1], m_scaled])

        for b in range(num_bars):
            if raw_bars[b] > prev_smoothed[b]:
                prev_smoothed[b] = attack_alpha * raw_bars[b] + (1 - attack_alpha) * prev_smoothed[b]
            else:
                prev_smoothed[b] = (1 - decay_alpha) * raw_bars[b] + decay_alpha * prev_smoothed[b]

        # 6px resting baseline, max height 78px
        all_bar_heights[f] = np.clip(prev_smoothed + 6.0, 6.0, 78.0)

    return all_bar_heights, all_rms, duration
