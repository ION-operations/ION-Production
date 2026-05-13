from __future__ import annotations

import ctypes
import hashlib
import re
import sys
import time
from ctypes import wintypes

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

from jarvis_injector.core.errors import ActivationError
from jarvis_injector.core.models import Rect, ResolvedWindow, TargetProfile, WindowFingerprint

if sys.platform == "win32":
    user32 = ctypes.windll.user32
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    SW_RESTORE = 9
    SW_SHOW = 5

    class WinRect(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]


class Win32WindowController:
    def enumerate_windows(self) -> list[ResolvedWindow]:
        if sys.platform != "win32":
            return []

        windows: list[ResolvedWindow] = []

        @EnumWindowsProc
        def callback(hwnd, _lparam):
            title = self._window_text(hwnd)
            class_name = self._class_name(hwnd)
            if not title and not class_name:
                return True

            pid = self._window_pid(hwnd)
            windows.append(
                ResolvedWindow(
                    hwnd=int(hwnd),
                    title=title,
                    process_name=self._process_name(pid),
                    pid=pid,
                    class_name=class_name,
                    is_minimized=bool(user32.IsIconic(hwnd)),
                    is_visible=bool(user32.IsWindowVisible(hwnd)),
                    bounds=self._window_rect(hwnd),
                )
            )
            return True

        user32.EnumWindows(callback, 0)
        return windows

    def find_window(self, target: TargetProfile) -> ResolvedWindow | None:
        candidates = []
        for window in self.enumerate_windows():
            score = self._score_window(target, window)
            if score > 0:
                candidates.append((score, window))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def restore_if_minimized(self, window: ResolvedWindow) -> None:
        if sys.platform == "win32" and window.is_minimized:
            user32.ShowWindow(window.hwnd, SW_RESTORE)

    def activate(self, window: ResolvedWindow) -> None:
        if sys.platform != "win32":
            return
        user32.ShowWindow(window.hwnd, SW_SHOW)
        if not user32.SetForegroundWindow(window.hwnd):
            raise ActivationError(f"SetForegroundWindow failed for hwnd={window.hwnd}")

    def wait_until_ready(self, window: ResolvedWindow, timeout_ms: int) -> None:
        if sys.platform != "win32":
            return
        deadline = time.monotonic() + (timeout_ms / 1000)
        while time.monotonic() < deadline:
            if user32.IsWindow(window.hwnd) and user32.IsWindowVisible(window.hwnd):
                return
            time.sleep(0.05)
        raise ActivationError(f"Window hwnd={window.hwnd} did not become ready within {timeout_ms}ms")

    def is_foreground(self, hwnd: int) -> bool:
        if sys.platform != "win32":
            return False
        return int(user32.GetForegroundWindow()) == int(hwnd)

    def build_fingerprint(self, target_id: str, window: ResolvedWindow) -> WindowFingerprint:
        title_hash = hashlib.sha1(window.title.encode("utf-8", errors="ignore")).hexdigest()[:16]
        return WindowFingerprint(
            target_id=target_id,
            process_name=window.process_name,
            class_name=window.class_name,
            title_hash=title_hash,
        )

    @staticmethod
    def _window_text(hwnd: int) -> str:
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value.strip()

    @staticmethod
    def _class_name(hwnd: int) -> str:
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, 256)
        return buffer.value.strip()

    @staticmethod
    def _window_rect(hwnd: int) -> Rect:
        rect = WinRect()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        return Rect(
            x=int(rect.left),
            y=int(rect.top),
            width=int(rect.right - rect.left),
            height=int(rect.bottom - rect.top),
        )

    @staticmethod
    def _window_pid(hwnd: int) -> int:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return int(pid.value)

    @staticmethod
    def _process_name(pid: int) -> str:
        if pid <= 0 or psutil is None:
            return ""
        try:
            return psutil.Process(pid).name()
        except Exception:
            return ""

    @staticmethod
    def _score_window(target: TargetProfile, window: ResolvedWindow) -> int:
        score = 0
        process_name = window.process_name.lower()
        title = window.title
        class_name = window.class_name.lower()

        if target.process_hints and process_name in {hint.lower() for hint in target.process_hints}:
            score += 50

        if target.title_regex:
            try:
                if re.search(target.title_regex, title, flags=re.IGNORECASE):
                    score += 35
            except re.error:
                pass

        class_hints = {hint.lower() for hint in target.class_hints}
        if class_hints and class_name in class_hints:
            score += 20

        if score > 0 and window.is_visible:
            score += 10

        return score
