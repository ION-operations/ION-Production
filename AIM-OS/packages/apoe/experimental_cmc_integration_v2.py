"""Experimental CMC Integration for APOE (v2, isolated sandbox).

This module is intentionally *not* wired into the production APOE package.
It exists as a clean‑room design space for APOE→CMC v1+ integrations:

- modality: "plan_execution"
- tags: ["apoe","plan","execution","plan_name:<name>","status:<success|failed|partial>"]
- metadata: plan_name, execution_id, status, steps_completed, total_steps,
  step_count, outputs, started_at, completed_at, duration_seconds,
  success_rate, error_count, avg_duration_seconds (for this plan).

Key differences vs the main implementation (owned by the APOE specialist):
- Pure, well‑typed API with explicit models and no legacy artifacts.
- Support for partial executions and error accounting as first‑class concepts.
- Deterministic ordering for history queries by (started_at DESC, execution_id DESC).
- Rich aggregation helpers (per‑plan and global stats) designed for HHNI/SEG.

NOTE: This file is sandbox‑only; do NOT import it from the main APOE package
without an explicit design review and agreement with the team.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Iterable, Tuple
import json
import inspect

try:  # Optional dependency; v2 prefers modern payload API when available
    from cmc_service.models import (  # type: ignore
        AtomCreate,
        AtomContent,
    )
except Exception:  # pragma: no cover
    AtomCreate = None  # type: ignore
    AtomContent = None  # type: ignore


def _utc_now() -> datetime:
    """Return current UTC time as a naive datetime."""
    return datetime.utcnow()


@dataclass
class PlanMemoryV2:
    """In‑memory representation of a single plan execution (v2 sandbox).

    This is deliberately richer than the minimal production model: it includes
    an error counter and can represent partial executions explicitly.
    """

    plan_name: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # "running" | "completed" | "failed" | "partial"
    steps_completed: int = 0
    total_steps: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: int = 0

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.completed_at is None:
            return None
        return float((self.completed_at - self.started_at).total_seconds())

    def mark_partial(self) -> None:
        self.status = "partial"

    def mark_completed(self, success: bool) -> None:
        self.completed_at = _utc_now()
        self.status = "completed" if success else "failed"


@dataclass
class PlanStatsV2:
    """Aggregated statistics for a given plan name."""

    plan_name: str
    total_executions: int
    success_rate: float
    avg_steps: float
    avg_duration_seconds: float
    error_count: int
    most_recent_started_at: Optional[datetime]


class CMCPlanStoreV2:
    """Isolated sandbox plan store for APOE→CMC v1/v2 integrations.

    Responsibilities:
    - Maintain an in‑memory history of executions (PlanMemoryV2).
    - Provide deterministic history queries.
    - Persist snapshots to CMC using the v1 payload spec when a client is present.
    """

    def __init__(self, cmc_client: Optional[Any] = None) -> None:
        self.cmc = cmc_client
        self._memory: Dict[str, PlanMemoryV2] = {}

    # ------------------------------------------------------------------ #
    # Public mutation API                                                #
    # ------------------------------------------------------------------ #
    def store_plan_start(
        self,
        plan_name: str,
        execution_id: str,
        total_steps: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        mem = PlanMemoryV2(
            plan_name=plan_name,
            execution_id=execution_id,
            started_at=_utc_now(),
            status="running",
            steps_completed=0,
            total_steps=int(total_steps or 0),
            outputs={},
            metadata=dict(metadata or {}),
        )
        self._memory[execution_id] = mem
        self._persist_snapshot(mem)
        return execution_id

    def update_plan_progress(
        self,
        execution_id: str,
        *,
        steps_completed: Optional[int] = None,
        current_outputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        mem = self._require(execution_id)
        if steps_completed is not None:
            mem.steps_completed = int(steps_completed)
        if current_outputs:
            mem.outputs.update(current_outputs)
        self._persist_snapshot(mem)

    def store_plan_partial(
        self,
        execution_id: str,
        *,
        partial_outputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        mem = self._require(execution_id)
        if partial_outputs:
            mem.outputs.update(partial_outputs)
        mem.mark_partial()
        self._persist_snapshot(mem)

    def record_error(self, execution_id: str, *, message: Optional[str] = None) -> None:
        mem = self._require(execution_id)
        mem.errors += 1
        if message:
            mem.outputs.setdefault("errors", []).append(message)
        self._persist_snapshot(mem)

    def store_plan_complete(
        self,
        execution_id: str,
        *,
        final_outputs: Optional[Dict[str, Any]] = None,
        success: bool,
    ) -> None:
        mem = self._require(execution_id)
        if final_outputs:
            mem.outputs.update(final_outputs)
        mem.mark_completed(success)
        self._persist_snapshot(mem)

    # ------------------------------------------------------------------ #
    # History / statistics                                               #
    # ------------------------------------------------------------------ #
    def retrieve_plan_history(
        self,
        plan_name: str,
        *,
        limit: int = 10,
    ) -> List[PlanMemoryV2]:
        """Return executions for a plan, newest first (deterministic)."""
        items = [m for m in self._memory.values() if m.plan_name == plan_name]
        items.sort(key=lambda m: (m.started_at, m.execution_id), reverse=True)
        return items[: max(0, int(limit))]

    def iter_all(self) -> Iterable[PlanMemoryV2]:
        return self._memory.values()

    def get_plan_statistics(self, plan_name: str) -> PlanStatsV2:
        hist = self.retrieve_plan_history(plan_name, limit=1_000)
        total = len(hist)
        if total == 0:
            return PlanStatsV2(
                plan_name=plan_name,
                total_executions=0,
                success_rate=0.0,
                avg_steps=0.0,
                avg_duration_seconds=0.0,
                error_count=0,
                most_recent_started_at=None,
            )
        successes = sum(1 for m in hist if m.status == "completed")
        durations = [m.duration_seconds or 0.0 for m in hist if m.duration_seconds is not None]
        avg_duration = (sum(durations) / len(durations)) if durations else 0.0
        avg_steps = sum(m.total_steps for m in hist) / float(total)
        most_recent = max(m.started_at for m in hist)
        return PlanStatsV2(
            plan_name=plan_name,
            total_executions=total,
            success_rate=successes / float(total),
            avg_steps=avg_steps,
            avg_duration_seconds=avg_duration,
            error_count=sum(m.errors for m in hist),
            most_recent_started_at=most_recent,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _require(self, execution_id: str) -> PlanMemoryV2:
        mem = self._memory.get(execution_id)
        if mem is None:
            raise ValueError(f"Plan execution not found: {execution_id}")
        return mem

    def _build_tags(self, mem: PlanMemoryV2) -> List[str]:
        """Build v1 tag list for this snapshot."""
        return [
            "apoe",
            "plan",
            "execution",
            f"plan_name:{mem.plan_name}",
            f"status:{mem.status}",
        ]

    def _build_metadata(self, mem: PlanMemoryV2) -> Dict[str, Any]:
        """Build v1 metadata dict enriched with aggregate metrics."""
        stats = self.get_plan_statistics(mem.plan_name)
        duration = mem.duration_seconds
        meta: Dict[str, Any] = dict(mem.metadata or {})
        meta.update(
            {
                "plan_name": mem.plan_name,
                "execution_id": mem.execution_id,
                "status": mem.status,
                "steps_completed": mem.steps_completed,
                "total_steps": mem.total_steps,
                "step_count": mem.total_steps,
                "outputs": mem.outputs,
                "started_at": mem.started_at.isoformat(),
                "completed_at": mem.completed_at.isoformat() if mem.completed_at else None,
                "duration_seconds": duration,
                "success_rate": stats.success_rate,
                "error_count": stats.error_count,
                "avg_duration_seconds": stats.avg_duration_seconds,
            }
        )
        return meta

    def _persist_snapshot(self, mem: PlanMemoryV2) -> None:
        """Persist a snapshot to CMC if a client is configured."""
        if self.cmc is None:
            return

        serial = asdict(mem)
        # Replace datetime objects with ISO strings for JSON content
        if isinstance(serial.get("started_at"), datetime):
            serial["started_at"] = mem.started_at.isoformat()
        if isinstance(serial.get("completed_at"), datetime):
            serial["completed_at"] = mem.completed_at.isoformat() if mem.completed_at else None
        content = json.dumps(serial)

        tags = self._build_tags(mem)
        metadata = self._build_metadata(mem)

        create_fn = getattr(self.cmc, "create_atom", None)
        if not callable(create_fn):
            return

        try:
            sig: Optional[inspect.Signature]
            try:
                sig = inspect.signature(create_fn)
            except Exception:
                sig = None

            # Prefer modern payload API if available
            if (
                AtomCreate is not None
                and AtomContent is not None
                and sig is not None
                and "payload" in sig.parameters
            ):
                payload = AtomCreate(  # type: ignore[call-arg]
                    modality="plan_execution",
                    content=AtomContent(inline=content, media_type="application/json"),
                    tags=tags,
                    metadata=metadata,
                )
                create_fn(payload=payload)
            else:
                # Legacy kwargs path, used by tests/mocks
                create_fn(
                    modality="plan_execution",
                    content=content,
                    tags=tags,
                    metadata=metadata,
                )
        except Exception:  # pragma: no cover
            logger = getattr(self.cmc, "logger", None)
            if logger is not None:
                try:
                    logger.warning("apoe.experimental_cmc_v2.store_atom.failed", exc_info=True)
                except Exception:
                    pass


class MemoryAwareExecutorV2:
    """Experimental executor that records plan execution snapshots via CMCPlanStoreV2."""

    def __init__(self, plan_store: CMCPlanStoreV2) -> None:
        self.plan_store = plan_store

    def execute_with_memory(
        self,
        *,
        plan_name: str,
        plan: Any,
        execution_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Simulate execution and persist start/progress/finish snapshots."""
        exec_id = execution_id or f"{plan_name}_{_utc_now().timestamp()}"

        history = self.plan_store.retrieve_plan_history(plan_name, limit=5)
        recent_success = sum(1 for m in history if m.status == "completed")
        total = len(history)
        metadata = {
            "has_history": bool(total),
            "recent_successes": recent_success,
            "avg_success_rate": (recent_success / float(total)) if total else 0.0,
        }

        steps = len(getattr(plan, "steps", []) or [])
        self.plan_store.store_plan_start(plan_name, exec_id, steps, metadata)

        # Simulated work path
        result = {
            "execution_id": exec_id,
            "success": True,
            "steps_completed": steps,
            "outputs": {"result": "ok"},
        }
        self.plan_store.store_plan_complete(
            execution_id=exec_id,
            final_outputs=result["outputs"],
            success=True,
        )
        return result

    def should_retry_based_on_history(self, plan_name: str, _message: str) -> bool:
        """Simple retry policy: retry if historical success rate > 0.70."""
        stats = self.plan_store.get_plan_statistics(plan_name)
        return stats.success_rate > 0.70

    def get_plan_recommendations(self, plan_name: str) -> Dict[str, Any]:
        """Return recommendations based on historical success rate and duration."""
        stats = self.plan_store.get_plan_statistics(plan_name)
        confidence = stats.success_rate
        recommended_retries = 2 if confidence >= 0.80 else 0
        warnings: List[str] = []
        if confidence < 0.50:
            warnings.append("Low historical success rate")
        return {
            "confidence": confidence,
            "recommended_retries": recommended_retries,
            "warnings": warnings,
            "avg_duration_seconds": stats.avg_duration_seconds,
        }


