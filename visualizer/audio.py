import os
import subprocess
import numpy as np
from scipy.ndimage import gaussian_filter1d
from .motion import MotionConfig, shape_bar_motion

def load_audio(audio_path, target_sr=44100):
    """
    Decodes audio to a 44.1kHz mono float32 numpy array using ffmpeg.
    Validates that audio is non-empty and has at least 0.1s duration.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Input audio file not found: {audio_path}")

    cmd = [
        "ffmpeg", "-v", "error", "-i", audio_path,
        "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "-"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_data, _ = proc.communicate()

    if proc.returncode != 0 or len(raw_data) == 0:
        raise RuntimeError(f"Failed to decode audio file or audio is empty: {audio_path}")

    samples = np.frombuffer(raw_data, dtype=np.float32)
    if len(samples) == 0:
        raise ValueError(f"Audio file contains zero samples: {audio_path}")

    duration = len(samples) / target_sr
    if duration < 0.1:
        raise ValueError(f"Audio duration ({duration:.3f}s) is too short. Minimum duration is 0.1s: {audio_path}")

    return samples, target_sr

def extract_audio_features(
    samples,
    sr,
    fps=30,
    min_freq=45.0,
    max_freq=11000.0,
    num_bands=24,
    window_size=4096
):
    """
    Extracts frame-by-frame broadband RMS energy and multi-band spectral magnitudes.
    
    Returns:
        all_rms: (total_frames,) float32 array of broadband RMS energy.
        spectrum: (total_frames, num_bands) float32 array of band spectral magnitudes.
        duration: audio duration in seconds.
    """
    duration = len(samples) / sr
    total_frames = int(duration * fps)
    if total_frames == 0:
        return np.zeros(0, dtype=np.float32), np.zeros((0, num_bands), dtype=np.float32), duration

    # Logarithmic frequency band boundaries
    band_limits = np.geomspace(min_freq, max_freq, num_bands + 1)
    hanning = np.hanning(window_size)
    freqs = np.fft.rfftfreq(window_size, 1.0 / sr)

    masks = []
    for i in range(num_bands):
        f_low, f_high = band_limits[i], band_limits[i + 1]
        mask = (freqs >= f_low) & (freqs < f_high)
        masks.append(mask)

    # Center zero-padded audio for exact frame alignment
    padded = np.pad(samples, (window_size // 2, window_size // 2))

    all_rms = np.zeros(total_frames, dtype=np.float32)
    spectrum = np.zeros((total_frames, num_bands), dtype=np.float32)

    for f in range(total_frames):
        center_sample = round(f * sr / fps)
        chunk = padded[center_sample:center_sample + window_size]

        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
        all_rms[f] = rms

        fft_vals = np.abs(np.fft.rfft(chunk * hanning))
        magnitudes = [float(np.mean(fft_vals[m])) if np.any(m) else 0.0 for m in masks]
        spectrum[f] = magnitudes

    return all_rms, spectrum, duration

def analyze_audio(
    samples,
    sr,
    fps=30,
    num_bars=64,
    min_freq=None,
    max_freq=None,
    window_size=4096,
    config=None
):
    """
    Analyzes audio and produces fluid, organic bar heights.
    
    Validates input parameters, separates feature extraction from motion shaping,
    and returns bar heights bounded in [baseline_height, max_height] with seamless
    circular motion and framerate-independent attack/decay dynamics.
    
    Returns:
        all_bar_heights: (total_frames, num_bars) float32 array of bar heights (in pixels)
        all_rms: (total_frames,) float32 array of RMS energy for ambient backlight pulsation
        duration: audio duration in seconds
    """
    # 1. Parameter Validation
    if not isinstance(fps, (int, float)) or fps < 1 or fps > 120:
        raise ValueError(f"Invalid fps: {fps}. Supported frame rate is between 1 and 120.")

    if not isinstance(num_bars, int) or num_bars < 16 or num_bars > 256:
        raise ValueError(f"Unsupported bar count: {num_bars}. Supported bar count is between 16 and 256.")

    if len(samples) == 0:
        raise ValueError("Audio samples array is empty.")

    duration = len(samples) / sr
    if duration < 0.1:
        raise ValueError(f"Audio duration ({duration:.3f}s) is too short. Minimum duration is 0.1s.")

    # 2. Configuration initialization
    if config is None:
        config = MotionConfig()
    if min_freq is not None:
        config.min_freq = min_freq
    if max_freq is not None:
        config.max_freq = max_freq

    # 3. Feature Extraction
    all_rms, spectrum, duration = extract_audio_features(
        samples=samples,
        sr=sr,
        fps=fps,
        min_freq=config.min_freq,
        max_freq=config.max_freq,
        num_bands=config.num_bands,
        window_size=window_size
    )

    # 4. Motion Shaping
    all_bar_heights = shape_bar_motion(
        broadband_rms=all_rms,
        spectrum=spectrum,
        fps=fps,
        num_bars=num_bars,
        config=config
    )

    return all_bar_heights, all_rms, duration
