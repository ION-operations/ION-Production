"""
AIM-OS SEER — Desktop Control Module

Provides OS-level screen capture and window management.
This is SEER's primary interface for seeing and interacting with
the full desktop environment — not limited to browser tabs.
"""

import base64
import io
import json
import time
from typing import Optional, List, Dict, Tuple

import mss
import mss.tools
from PIL import Image

try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

import pyautogui


class ScreenCapture:
    """
    High-performance screen capture with micro-cropping.
    Uses mss for speed (~20ms full capture) and Pillow for processing.
    """

    def __init__(self):
        self._sct = mss.mss()

    def screenshot(self, monitor: int = 0,
                   region: Optional[Dict] = None,
                   max_dimension: int = 1920) -> dict:
        """
        Capture a screenshot.

        Args:
            monitor: Monitor index (0 = all monitors, 1 = primary, 2+ = secondary)
            region: Optional {x, y, width, height} for targeted capture
            max_dimension: Max width/height before downscaling (for token efficiency)

        Returns:
            dict with base64 image, dimensions, and metadata
        """
        t_start = time.perf_counter()

        if region:
            # Targeted micro-crop — the SEER paradigm
            capture_area = {
                'left': region['x'],
                'top': region['y'],
                'width': region['width'],
                'height': region['height']
            }
        else:
            # Full monitor capture
            monitors = self._sct.monitors
            if monitor >= len(monitors):
                monitor = 0
            capture_area = monitors[monitor]

        # Capture
        raw = self._sct.grab(capture_area)
        img = Image.frombytes('RGB', (raw.width, raw.height), raw.rgb)

        # Downscale if needed (keeps aspect ratio)
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Convert to base64 PNG
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        capture_time = (time.perf_counter() - t_start) * 1000

        return {
            'success': True,
            'image_base64': b64,
            'width': img.width,
            'height': img.height,
            'format': 'png',
            'capture_ms': round(capture_time, 1),
            'region': region,
            'size_bytes': len(buffer.getvalue())
        }

    def micro_crop(self, x: int, y: int,
                   width: int = 200, height: int = 200) -> dict:
        """
        SEER's signature move: capture a tiny, context-dense region.
        100x100 to 300x300 pixel crops instead of full 4K screenshots.

        ~200 tokens instead of ~100,000 tokens per image.
        """
        return self.screenshot(region={
            'x': x, 'y': y,
            'width': width, 'height': height
        })

    def get_monitors(self) -> List[Dict]:
        """List all monitors with their geometry."""
        monitors = []
        for i, mon in enumerate(self._sct.monitors):
            if i == 0:
                # Index 0 is the combined virtual monitor
                monitors.append({
                    'index': 0,
                    'name': 'All Monitors (combined)',
                    'left': mon['left'],
                    'top': mon['top'],
                    'width': mon['width'],
                    'height': mon['height']
                })
            else:
                monitors.append({
                    'index': i,
                    'name': f'Monitor {i}',
                    'left': mon['left'],
                    'top': mon['top'],
                    'width': mon['width'],
                    'height': mon['height'],
                    'primary': i == 1
                })
        return monitors

    def get_screen_size(self) -> Tuple[int, int]:
        """Get primary screen dimensions."""
        return pyautogui.size()


class WindowManager:
    """
    OS-level window enumeration, focusing, and management.
    Enables SEER to switch between IDEs, browsers, and applications.
    """

    def list_windows(self, visible_only: bool = True) -> List[Dict]:
        """
        List all windows with their geometry and state.

        Returns list of dicts with: title, position, size, active, minimized, etc.
        """
        if not HAS_PYGETWINDOW:
            return self._fallback_list_windows()

        windows = []
        for win in gw.getAllWindows():
            if visible_only and (not win.title or win.title.strip() == ''):
                continue

            try:
                windows.append({
                    'title': win.title,
                    'rect': {
                        'x': win.left,
                        'y': win.top,
                        'w': win.width,
                        'h': win.height
                    },
                    'active': win.isActive,
                    'minimized': win.isMinimized,
                    'maximized': win.isMaximized,
                    'visible': win.visible if hasattr(win, 'visible') else True
                })
            except Exception:
                continue

        return windows

    def focus_window(self, title_substring: str) -> dict:
        """
        Focus a window by title substring match.
        Case-insensitive partial match.

        Args:
            title_substring: Part of the window title to match

        Returns:
            dict with success status and matched window info
        """
        if not HAS_PYGETWINDOW:
            return {'success': False, 'error': 'pygetwindow not available'}

        search = title_substring.lower()
        for win in gw.getAllWindows():
            if search in win.title.lower():
                try:
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    time.sleep(0.3)  # Wait for focus transition
                    return {
                        'success': True,
                        'title': win.title,
                        'rect': {
                            'x': win.left, 'y': win.top,
                            'w': win.width, 'h': win.height
                        }
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e), 'title': win.title}

        return {
            'success': False,
            'error': f'No window found matching "{title_substring}"',
            'available': [w.title for w in gw.getAllWindows() if w.title.strip()][:20]
        }

    def get_active_window(self) -> dict:
        """Get info about the currently focused window."""
        if not HAS_PYGETWINDOW:
            return {'success': False, 'error': 'pygetwindow not available'}

        try:
            win = gw.getActiveWindow()
            if not win:
                return {'success': False, 'error': 'No active window'}
            return {
                'success': True,
                'title': win.title,
                'rect': {
                    'x': win.left, 'y': win.top,
                    'w': win.width, 'h': win.height
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _fallback_list_windows(self) -> List[Dict]:
        """Fallback when pygetwindow is not available."""
        return [{'error': 'pygetwindow not installed — install with: pip install pygetwindow'}]


class KeyboardController:
    """
    OS-level keyboard input.
    Wraps pyautogui with natural typing speed variation.
    """

    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> dict:
        """
        Type text with natural speed variation.

        Args:
            text: Text to type
            interval: Base interval between keystrokes (seconds)
        """
        import random

        for char in text:
            pyautogui.press(char) if len(char) > 1 else pyautogui.write(char, _pause=False)
            # Variable typing speed
            time.sleep(interval * random.uniform(0.5, 1.5))

        return {'success': True, 'typed': text, 'length': len(text)}

    @staticmethod
    def hotkey(*keys: str) -> dict:
        """
        Press a hotkey combination (e.g., 'ctrl', 'c' for Ctrl+C).
        """
        pyautogui.hotkey(*keys, _pause=False)
        return {'success': True, 'keys': list(keys)}

    @staticmethod
    def press(key: str, presses: int = 1) -> dict:
        """Press a single key."""
        pyautogui.press(key, presses=presses, _pause=False)
        return {'success': True, 'key': key, 'presses': presses}
