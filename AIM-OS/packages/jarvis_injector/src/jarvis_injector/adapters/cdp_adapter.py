from __future__ import annotations

from jarvis_injector.adapters.base import BaseAdapter
from jarvis_injector.core.enums import AdapterKind
from jarvis_injector.core.models import ActionResult, AdapterProbe, DispatchContext, LocateResult


class CdpAdapter(BaseAdapter):
    name = AdapterKind.CDP.value

    def probe(self, ctx: DispatchContext) -> AdapterProbe:
        return AdapterProbe(adapter=AdapterKind.CDP, supported=False, reason="CDP adapter not implemented in Phase A")

    def locate_input(self, ctx: DispatchContext) -> LocateResult:
        return LocateResult(adapter=AdapterKind.CDP, locator_id=None)

    def set_text(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        return ActionResult(success=False, detail="CDP adapter not implemented in Phase A")

    def submit(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        return ActionResult(success=False, detail="CDP adapter not implemented in Phase A")

