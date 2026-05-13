from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from jarvis_injector.core.enums import DispatchState
from jarvis_injector.core.models import DispatchAccepted, DispatchRequest, DispatchResult, ExecutionRecord
from jarvis_injector.core.telemetry import ExecutionTelemetry


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionQueue:
    def __init__(self, handler, telemetry: ExecutionTelemetry, worker_count: int = 1) -> None:
        self._handler = handler
        self._telemetry = telemetry
        self._executor = ThreadPoolExecutor(max_workers=worker_count)
        self._records: dict[str, ExecutionRecord] = {}
        self._lock = Lock()

    def submit(self, request: DispatchRequest) -> DispatchAccepted:
        execution_id = self._new_execution_id()
        record = ExecutionRecord(
            execution_id=execution_id,
            request=request,
            state=DispatchState.QUEUED,
        )
        with self._lock:
            self._records[execution_id] = record

        self._executor.submit(self._run, execution_id, request)
        return DispatchAccepted(execution_id=execution_id, state=DispatchState.QUEUED)

    def run_now(self, request: DispatchRequest) -> DispatchResult:
        execution_id = self._new_execution_id()
        return self._run(execution_id, request)

    def _run(self, execution_id: str, request: DispatchRequest) -> DispatchResult:
        with self._lock:
            record = self._records.get(execution_id)
            if record is None:
                record = ExecutionRecord(
                    execution_id=execution_id,
                    request=request,
                    state=DispatchState.RUNNING,
                )
                self._records[execution_id] = record
            else:
                record.state = DispatchState.RUNNING
                record.updated_at = utc_now()

        try:
            result = self._handler(execution_id, request)
        except Exception as exc:
            result = DispatchResult(
                execution_id=execution_id,
                target_id=request.target_id,
                state=DispatchState.FAILED,
                verification={"passed": False, "signals": [], "manual_review_required": False},
                error=str(exc),
            )

        with self._lock:
            record = self._records[execution_id]
            record.state = result.state
            record.result = result
            record.updated_at = utc_now()
            self._telemetry.record_execution(record)

        return result

    def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        with self._lock:
            return self._records.get(execution_id)

    def list_executions(self, limit: int = 25) -> list[ExecutionRecord]:
        with self._lock:
            records = sorted(
                self._records.values(),
                key=lambda record: record.updated_at,
                reverse=True,
            )
        return records[:limit]

    def queue_depth(self) -> int:
        with self._lock:
            return sum(1 for record in self._records.values() if record.state == DispatchState.QUEUED)

    @staticmethod
    def _new_execution_id() -> str:
        return f"inj_{uuid4().hex[:12]}"

