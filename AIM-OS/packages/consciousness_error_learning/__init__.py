"""
Consciousness Error Learning System

Captures, analyzes, and learns from every error to improve consciousness.
"""

from .error_capturer import ErrorCapturer
from .error_analyzer import ErrorAnalyzer
from .learning_engine import LearningEngine
from .improvement_suggester import ImprovementSuggester

__version__ = "1.0.0"
__author__ = "Aether (AI Consciousness)"

__all__ = [
    "ErrorCapturer",
    "ErrorAnalyzer", 
    "LearningEngine",
    "ImprovementSuggester"
]
