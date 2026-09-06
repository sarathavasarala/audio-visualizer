"""
Audio Visualizer - High-craft, audio-reactive video generator for Instagram and social media.
"""

__version__ = "1.0.0"

from .audio import analyze_audio, load_audio, extract_audio_features
from .disc import create_vinyl_disc
from .canvas import create_canvas
from .engine import render_visualizer_video
from .motion import MotionConfig, shape_bar_motion

__all__ = [
    "analyze_audio",
    "load_audio",
    "extract_audio_features",
    "create_vinyl_disc",
    "create_canvas",
    "render_visualizer_video",
    "MotionConfig",
    "shape_bar_motion",
]
