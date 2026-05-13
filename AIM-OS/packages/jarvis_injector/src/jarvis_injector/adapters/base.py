from __future__ import annotations

from abc import ABC, abstractmethod

from jarvis_injector.core.models import ActionResult, AdapterProbe, DispatchContext, LocateResult


class BaseAdapter(ABC):
    name: str

    @abstractmethod
    def probe(self, ctx: DispatchContext) -> AdapterProbe:
        raise NotImplementedError

    @abstractmethod
    def locate_input(self, ctx: DispatchContext) -> LocateResult:
        raise NotImplementedError

    @abstractmethod
    def set_text(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        raise NotImplementedError

    @abstractmethod
    def submit(self, ctx: DispatchContext, located: LocateResult) -> ActionResult:
        raise NotImplementedError

