from __future__ import annotations

from dataclasses import dataclass

from jarvis_injector.adapters.base import BaseAdapter
from jarvis_injector.core.enums import AdapterKind
from jarvis_injector.core.models import AdapterProbe, AdapterSelection, DispatchContext


@dataclass
class SelectedAdapter:
    adapter: BaseAdapter
    selection: AdapterSelection
    probe: AdapterProbe


class AdapterManager:
    def __init__(self, adapters: dict[AdapterKind, BaseAdapter]) -> None:
        self._adapters = adapters

    @property
    def adapters(self) -> dict[AdapterKind, BaseAdapter]:
        return self._adapters

    def choose(self, ctx: DispatchContext) -> SelectedAdapter:
        preferred = list(ctx.target.preferred_adapters)
        if ctx.request.preferred_adapter:
            preferred = [ctx.request.preferred_adapter] + [kind for kind in preferred if kind != ctx.request.preferred_adapter]

        best: SelectedAdapter | None = None
        for kind in preferred:
            adapter = self._adapters.get(kind)
            if adapter is None:
                continue
            probe = adapter.probe(ctx)
            candidate = SelectedAdapter(
                adapter=adapter,
                selection=AdapterSelection(adapter=kind, confidence=probe.confidence, reason=probe.reason),
                probe=probe,
            )
            if probe.supported:
                return candidate
            if best is None:
                best = candidate

        if best is None:
            raise RuntimeError("No adapters registered")
        return best

