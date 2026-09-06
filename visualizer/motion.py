import math
from dataclasses import dataclass
import numpy as np
from scipy.ndimage import gaussian_filter1d

@dataclass
class MotionConfig:
    """
    Centralized configuration for audio-reactive bar motion shaping.
    
    Tunable Parameters:
        shared_weight: Fraction of bar height driven by broadband loudness (breathing ring).
        detail_weight: Fraction of bar height driven by local frequency detail (local ripples).
        attack_sec: Attack time constant in seconds (smooth rise time, e.g. 0.060 = 60ms).
        release_sec: Release time constant in seconds (smooth decay time, e.g. 0.220 = 220ms).
        min_freq: Lower frequency boundary for spectral analysis (Hz).
        max_freq: Upper frequency boundary for spectral analysis (Hz).
        num_bands: Number of log-spaced frequency analysis bands.
        baseline_height: Resting bar height in pixels (when audio is silent).
        max_height: Maximum bar height in pixels.
        spatial_smoothing_sigma: Standard deviation for circular Gaussian smoothing across bars.
        saturation_strength: Knee curvature for soft tanh saturation.
        noise_floor_db: Energy floor in dBFS below which audio is gated to resting baseline.
        balancing_cap_ratio: Minimum reference level for quiet frequency bands relative to global peak,
                             preventing low-level hiss from being amplified.
    """
    shared_weight: float = 0.65
    detail_weight: float = 0.35
    attack_sec: float = 0.060
    release_sec: float = 0.220
    min_freq: float = 45.0
    max_freq: float = 11000.0
    num_bands: int = 24
    baseline_height: float = 6.0
    max_height: float = 78.0
    spatial_smoothing_sigma: float = 1.2
    saturation_strength: float = 1.2
    noise_floor_db: float = -55.0
    balancing_cap_ratio: float = 0.18


def build_circular_distribution_matrix(num_bars: int = 64, num_bands: int = 24) -> np.ndarray:
    """
    Constructs a smooth, periodic mapping matrix W of shape (num_bars, num_bands).
    
    Distributes overlapping frequency mixtures around the circle so that:
    - Every bar receives an overlapping mixture of frequencies (no region is purely bass or treble).
    - The frequency response varies smoothly around the circle with 2*pi periodicity (zero seam).
    - Multi-harmonic variation eliminates rigid mirrored halves.
    - Top and bottom are naturally balanced so both breathe with the rhythm.
    """
    # Angle theta for each bar, matching engine.py orientation (theta = -pi/2 at top)
    thetas = np.linspace(0, 2.0 * np.pi, num_bars, endpoint=False) - np.pi / 2.0

    # Smooth multi-harmonic preferred frequency coordinate in normalized [0, 1] range:
    # 2-theta harmonic couples opposite sides (top/bottom and left/right);
    # 3-theta harmonic breaks bilateral mirror symmetry;
    # theta - pi/4 phase shift gives each quadrant a unique, organic feel.
    u = 0.50 + 0.22 * np.cos(2.0 * thetas) + 0.10 * np.sin(3.0 * thetas) + 0.08 * np.cos(thetas - np.pi / 4.0)
    u = np.clip(u, 0.10, 0.90)

    # Normalized frequency band centers
    xm = np.linspace(0.0, 1.0, num_bands)
    sigma = 0.18
    w_base = 0.25  # Baseline sensitivity shared across all bands

    # Gaussian kernel around each bar's preferred frequency
    diff = xm[None, :] - u[:, None]
    local_weights = np.exp(-0.5 * (diff / sigma) ** 2)

    # Blend baseline mixture with local peak
    W = w_base + (1.0 - w_base) * local_weights

    # Normalize rows so each bar's total sensitivity sums to 1.0
    row_sums = W.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    W = W / row_sums
    return W.astype(np.float32)


def shape_bar_motion(
    broadband_rms: np.ndarray,
    spectrum: np.ndarray,
    fps: int,
    num_bars: int = 64,
    config: MotionConfig = None
) -> np.ndarray:
    """
    Shapes raw audio analysis features into fluid, aesthetic bar heights.
    
    Processing Steps:
    1. Noise gating & gentle capped frequency balancing across bands.
    2. Shared broadband envelope calculation (breathing ring).
    3. Circular frequency distribution with overlapping mixtures.
    4. Circular spatial smoothing to eliminate seams and jagged jumps.
    5. Blending shared motion (65%) with local spectral detail (35%).
    6. Framerate-independent attack/decay envelope follower.
    7. Soft tanh saturation mapped to [baseline_height, max_height].
    """
    if config is None:
        config = MotionConfig()

    total_frames = len(broadband_rms)
    if total_frames == 0:
        return np.zeros((0, num_bars), dtype=np.float32)

    num_bands = spectrum.shape[1] if spectrum.ndim > 1 else config.num_bands
    height_span = config.max_height - config.baseline_height

    # 1. Noise gate factor based on broadband RMS
    noise_floor = 10.0 ** (config.noise_floor_db / 20.0)
    # Smooth fade between 0.5 * noise_floor and 1.5 * noise_floor
    noise_gate = np.clip((broadband_rms - 0.5 * noise_floor) / (1.0 * noise_floor), 0.0, 1.0)

    # 2. Broadband Loudness Envelope (Shared Breathing Motion)
    active_rms = broadband_rms[broadband_rms > noise_floor]
    if len(active_rms) > 0:
        rms_ref = max(float(np.percentile(active_rms, 90)), 1e-5)
    else:
        rms_ref = max(float(np.percentile(broadband_rms, 95)), 1e-5)

    norm_broadband = np.clip(broadband_rms / rms_ref, 0.0, None)
    broadband_envelope = np.tanh(1.2 * norm_broadband) * noise_gate

    # 3. Gentle Capped Frequency Balancing
    global_ref = max(float(np.percentile(spectrum, 95)), 1e-6)
    band_refs = np.percentile(spectrum, 90, axis=0) if total_frames > 1 else spectrum[0]
    min_allowed_ref = max(config.balancing_cap_ratio * global_ref, 1e-5)
    effective_refs = np.maximum(band_refs, min_allowed_ref)

    norm_spectrum = spectrum / effective_refs[None, :]
    balanced_spectrum = np.tanh(1.2 * norm_spectrum) * noise_gate[:, None]

    # 4. Circular Frequency Distribution
    W = build_circular_distribution_matrix(num_bars=num_bars, num_bands=num_bands)
    local_detail = balanced_spectrum @ W.T  # Shape: (total_frames, num_bars)

    # 5. Circular Spatial Smoothing across adjacent bars (mode='wrap' ensures zero seam)
    if config.spatial_smoothing_sigma > 0:
        local_detail = gaussian_filter1d(local_detail, sigma=config.spatial_smoothing_sigma, axis=1, mode='wrap')

    # 6. Motion Blending: Shared breathing envelope + Local spectral detail
    target_motion = (
        config.shared_weight * broadband_envelope[:, None] +
        config.detail_weight * local_detail
    )

    # 7. Framerate-Independent Temporal Smoothing (Attack/Release time constants)
    alpha_attack = 1.0 - math.exp(-1.0 / (fps * max(config.attack_sec, 1e-4)))
    alpha_release = 1.0 - math.exp(-1.0 / (fps * max(config.release_sec, 1e-4)))

    smoothed_motion = np.zeros(num_bars, dtype=np.float32)
    all_bar_heights = np.zeros((total_frames, num_bars), dtype=np.float32)

    for f in range(total_frames):
        target_f = target_motion[f]
        diff = target_f - smoothed_motion
        alpha = np.where(diff > 0, alpha_attack, alpha_release)
        smoothed_motion += alpha * diff

        # Flush negligible sub-pixel residual (< 0.1px) to clean zero
        smoothed_motion[smoothed_motion < 1.5e-3] = 0.0

        # 8. Soft Saturation & Height Mapping (silence returns exactly to baseline_height)
        saturated = np.tanh(config.saturation_strength * np.maximum(smoothed_motion, 0.0))
        all_bar_heights[f] = config.baseline_height + height_span * saturated

    return all_bar_heights
