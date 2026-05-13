from __future__ import annotations

from jarvis_injector.adapters.base import BaseAdapter
from jarvis_injector.core.enums import AdapterKind
from jarvis_injector.core.models import ActionResult, AdapterProbe, DispatchContext, LocateResult
from jarvis_injector.windows.input_driver import WindowsInputDriver


class KeyboardAdapter(BaseAdapter):
    name = AdapterKind.KEYBOARD.value

    def __init__(self, input_driver: WindowsInputDriver) -> None:
        self._input_driver = input_driver

    def probe(self, ctx: DispatchContext) -> AdapterProbe:
        if not ctx.window:
            return AdapterProbe(adapter=AdapterKind.KEYBOARD, supported=False, reason="No resolved window")
        if not ctx.policy.allow_keyboard_injection:
            return AdapterProbe(adapter=AdapterKind.KEYBOARD, supported=False, reason="Policy forbids keyboard injection")
        return AdapterProbe(
            adapter=AdapterKind.KEYBOARD,
            supported=True,
            confidence=0.55,
            reason="Foreground keyboard fallback available",
        )

    def locate_input(self, ctx: DispatchContext) -> LocateResult:
        return LocateResult(adapter=AdapterKind.KEYBOARD, locator_id="foreground-window")

    def set_text(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        return self._input_driver.type_text(ctx.request.command_text)

    def submit(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        if "press_enter" in ctx.target.submit_policy or not ctx.target.submit_policy:
            return self._input_driver.press_enter()
        return ActionResult(success=False, detail=f"Unsupported keyboard submit policy: {ctx.target.submit_policy}")

