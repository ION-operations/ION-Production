from __future__ import annotations

import time
from dataclasses import dataclass

from jarvis_injector.adapters.manager import AdapterManager
from jarvis_injector.core.enums import DispatchState
from jarvis_injector.core.errors import ActivationError, AdapterExecutionError, TargetNotFoundError, VerificationError
from jarvis_injector.core.models import (
    ActionResult,
    DispatchAccepted,
    DispatchContext,
    DispatchRequest,
    DispatchResult,
    ExecutionRecord,
)
from jarvis_injector.core.policy import resolve_policy
from jarvis_injector.registry.fingerprint_store import FingerprintStore
from jarvis_injector.registry.target_registry import TargetRegistry
from jarvis_injector.verification.engine import VerificationEngine
from jarvis_injector.windows.window_controller import Win32WindowController


@dataclass
class DispatchExecutor:
    target_registry: TargetRegistry
    window_controller: Win32WindowController
    adapter_manager: AdapterManager
    verification_engine: VerificationEngine
    fingerprint_store: FingerprintStore

    def execute(self, execution_id: str, request: DispatchRequest) -> DispatchResult:
        target = self.target_registry.get(request.target_id)
        if target is None:
            raise TargetNotFoundError(f"Unknown target '{request.target_id}'")

        ctx = DispatchContext(
            execution_id=execution_id,
            request=request,
            target=target,
            policy=resolve_policy(target),
        )

        phase_started = time.perf_counter()
        window = self.window_controller.find_window(target)
        if window is None:
            raise TargetNotFoundError(f"Target window not found for '{target.id}'")
        ctx.window = window
        ctx.timings_ms["find_window"] = int((time.perf_counter() - phase_started) * 1000)

        phase_started = time.perf_counter()
        self.window_controller.restore_if_minimized(window)
        self.window_controller.activate(window)
        self.window_controller.wait_until_ready(window, 2000)
        ctx.timings_ms["restore_activate"] = int((time.perf_counter() - phase_started) * 1000)

        fingerprint = self.window_controller.build_fingerprint(target.id, window)
        fingerprint_path = self.fingerprint_store.save(fingerprint)
        ctx.artifacts.saved_artifact_ids.append(str(fingerprint_path))

        selection = self.adapter_manager.choose(ctx)
        ctx.adapter_selection = selection.selection
        if not selection.probe.supported:
            raise AdapterExecutionError(selection.probe.reason or "No supported adapter")

        phase_started = time.perf_counter()
        locate_result = selection.adapter.locate_input(ctx)
        ctx.locate_result = locate_result
        ctx.timings_ms["locate_input"] = int((time.perf_counter() - phase_started) * 1000)

        phase_started = time.perf_counter()
        text_result = selection.adapter.set_text(ctx, locate_result)
        submit_result = selection.adapter.submit(ctx, locate_result)
        self._assert_action(text_result, "set_text")
        self._assert_action(submit_result, "submit")
        verification = self.verification_engine.verify(ctx)
        ctx.verification = verification
        ctx.timings_ms["submit_verify"] = int((time.perf_counter() - phase_started) * 1000)

        if not verification.passed:
            raise VerificationError("Verification policy did not pass")

        return DispatchResult(
            execution_id=execution_id,
            target_id=request.target_id,
            state=DispatchState.SUCCESS,
            adapter_used=selection.selection.adapter,
            verification=verification,
            timings_ms=ctx.timings_ms,
            artifacts=ctx.artifacts,
        )

    @staticmethod
    def _assert_action(result: ActionResult, phase: str) -> None:
        if not result.success:
            raise AdapterExecutionError(result.detail or f"{phase} failed")


class DispatchService:
    def __init__(self, queue: "ExecutionQueue") -> None:
        self._queue = queue

    def submit(self, request: DispatchRequest) -> DispatchAccepted:
        return self._queue.submit(request)

    def run_now(self, request: DispatchRequest) -> DispatchResult:
        return self._queue.run_now(request)

    def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        return self._queue.get_execution(execution_id)

    def list_executions(self, limit: int = 25) -> list[ExecutionRecord]:
        return self._queue.list_executions(limit=limit)

