from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

from jarvis_injector.core.models import ActionResult

if sys.platform == "win32":
    user32 = ctypes.windll.user32
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    ULONG_PTR = ctypes.c_size_t

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class InputUnion(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("union", InputUnion)]


class WindowsInputDriver:
    def type_text(self, text: str) -> ActionResult:
        if sys.platform != "win32":
            return ActionResult(success=False, detail="Keyboard injection is Windows-only")

        inputs: list[INPUT] = []
        for char in text:
            scan_code = ord(char)
            inputs.extend(
                [
                    INPUT(type=INPUT_KEYBOARD, union=InputUnion(ki=KEYBDINPUT(0, scan_code, KEYEVENTF_UNICODE, 0, 0))),
                    INPUT(type=INPUT_KEYBOARD, union=InputUnion(ki=KEYBDINPUT(0, scan_code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0))),
                ]
            )
        return self._send(inputs, detail="text typed")

    def press_enter(self) -> ActionResult:
        return self.press_virtual_key(0x0D, detail="enter pressed")

    def press_virtual_key(self, vk_code: int, detail: str | None = None) -> ActionResult:
        if sys.platform != "win32":
            return ActionResult(success=False, detail="Keyboard injection is Windows-only")
        inputs = [
            INPUT(type=INPUT_KEYBOARD, union=InputUnion(ki=KEYBDINPUT(vk_code, 0, 0, 0, 0))),
            INPUT(type=INPUT_KEYBOARD, union=InputUnion(ki=KEYBDINPUT(vk_code, 0, KEYEVENTF_KEYUP, 0, 0))),
        ]
        return self._send(inputs, detail=detail or f"vk={vk_code} pressed")

    @staticmethod
    def _send(inputs: list["INPUT"], detail: str) -> ActionResult:
        if not inputs:
            return ActionResult(success=True, detail=detail)
        sent = user32.SendInput(len(inputs), (INPUT * len(inputs))(*inputs), ctypes.sizeof(INPUT))
        if sent != len(inputs):
            return ActionResult(success=False, detail=f"SendInput sent {sent}/{len(inputs)} events")
        return ActionResult(success=True, detail=detail)
