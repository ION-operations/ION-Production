from __future__ import annotations

from jarvis_injector.adapters.base import BaseAdapter
from jarvis_injector.core.enums import AdapterKind
from jarvis_injector.core.models import ActionResult, AdapterProbe, DispatchContext, LocateResult


class UiaAdapter(BaseAdapter):
    name = AdapterKind.UIA.value

    def probe(self, ctx: DispatchContext) -> AdapterProbe:
        return AdapterProbe(adapter=AdapterKind.UIA, supported=False, reason="UIA adapter not implemented in Phase A")

    def locate_input(self, ctx: DispatchContext) -> LocateResult:
        return LocateResult(adapter=AdapterKind.UIA, locator_id=None)

    def set_text(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        return ActionResult(success=False, detail="UIA adapter not implemented in Phase A")

    def submit(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        return ActionResult(success=False, detail="UIA adapter not implemented in Phase A")

