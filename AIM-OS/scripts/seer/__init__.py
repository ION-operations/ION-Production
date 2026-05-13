"""
AIM-OS SEER — Desktop Engine & Automation Platform
Spatially Environment-Encoded Ranger

Provides full desktop control and visual automation:
- Screenshot capture & micro-cropping (mss + Pillow)
- Biomechanical mouse kinematics (Bezier curves via pyautogui)
- Window management & app switching (pygetwindow)
- Keyboard input (pyautogui)
- Visual recognition (OpenCV template matching, HSV masking)
- Reflex loop (async event loop for continuous visual monitoring)
- Element Library (store/search UI elements by app/page)
- Capture System (screen capture, DOM import, verification)
- Automation Engine (compose & run workflows from elements)
- AI Discovery (Gemini Vision identifies UI elements automatically)
- Gemini Integration (API + CLI, Nano Banana image generation)
- MCP Tools (32 tools exposing SEER + Gemini to all agents)
- Generative path execution (AI-drawn kinematic paths — R&D)
"""

from .desktop import ScreenCapture, WindowManager, KeyboardController
from .kinematics import MouseKinematics
from .vision import VisionEngine, VisualAnchor
from .reflex import ReflexEngine
from .element_library import ElementLibrary, Element
from .capture import CaptureEngine
from .automation import AutomationEngine, Automation, Action, ActionType
from .discovery import DiscoveryEngine, GeminiVision
from .gemini_integration import GeminiInterface, GeminiCLI
from .generative_path import GenerativePathExecutor

__all__ = [
    'ScreenCapture', 'WindowManager', 'KeyboardController',
    'MouseKinematics',
    'VisionEngine', 'VisualAnchor',
    'ReflexEngine',
    'ElementLibrary', 'Element',
    'CaptureEngine',
    'AutomationEngine', 'Automation', 'Action', 'ActionType',
    'DiscoveryEngine', 'GeminiVision',
    'GeminiInterface', 'GeminiCLI',
    'GenerativePathExecutor',
]




