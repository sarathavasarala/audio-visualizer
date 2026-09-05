"""
Audio Visualizer - High-craft, audio-reactive video generator for Instagram and social media.
"""

__version__ = "1.0.0"

from .audio import analyze_audio
from .disc import create_vinyl_disc
from .canvas import create_canvas
from .engine import render_visualizer_video

__all__ = [
    "analyze_audio",
    "create_vinyl_disc",
    "create_canvas",
    "render_visualizer_video",
]
