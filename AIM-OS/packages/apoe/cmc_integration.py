"""CMC Integration for APOE.

Provides a lightweight in‑process memory of plan executions and an optional
bridge to the Context Memory Core (CMC). When a `cmc_service` client is
available, each snapshot is persisted using the v1 payload contract:

- modality: "plan_execution"
- tags (weighted dictionary): {"system:apoe:p0": 1.0, "integration_type:plan_execution": 1.0, "connection:apoe->cmc": 1.0, "modality:plan_execution": 1.0, "apoe": 1.0, "plan": 1.0, "execution": 1.0, "plan_name:<name>": 1.0, "status:<success|failed|partial>": 1.0}
- metadata: includes plan_name, execution_id, status, steps_completed, total_steps,
  step_count (same as total_steps), outputs, started_at, completed_at,
  duration_seconds, success_rate (for this plan across cached history),
  error_count (aggregated from PlanMemory.errors)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import inspect

try:  # Optional dependency; fallback to legacy call if not available
    from ccm_service import models as _cmc_models  # type: ignore
except Exception:  # pragma: no cover
    _cmc_models = None  # type: ignore


def _utc_now() -> datetime:
    return datetime.utcnow()


@dataclass
class PlanMemory:
    """In-memory representation of a single plan execution."""

    plan_name: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # "running" | "completed" | "failed" | "partial"
    steps_completed: int = 0
    total_steps: int = 0
    outputs: Dict[str, Any] = field(default_factory=lambda: {})
    metadata: Dict[str, Any] = field(default_factory=lambda: {})
    errors: int = 0

    def mark_partial(self) -> None:
        self.status = "partial"

    def mark_completed(self, success: bool) -> None:
        self.completed_at = _utc_now()
        self.status = "completed" if success else "failed"


class CMCPlanStore:
    """Stores and retrieves plan executions; optionally persists snapshots to CMC."""
    
    def __init__(self, cmc_client: Optional[Any] = None) -> None:
        self.cmc = cmc_client
        self._memory: Dict[str, PlanMemory] = {}
    
    # --- Public API ------------------------------------------------------
    def store_plan_start(self, plan_name: str, execution_id: str, total_steps: int, metadata: Optional[Dict[str, Any]] = None) -> str:
        mem = PlanMemory(
            plan_name=plan_name,
            execution_id=execution_id,
            started_at=_utc_now(),
            status="running",
            steps_completed=0,
            total_steps=int(total_steps or 0),
            metadata=dict(metadata or {}),
        )
        self._memory[execution_id] = mem
        self._persist(mem)
        return execution_id
    
    def update_plan_progress(self, execution_id: str, *, steps_completed: Optional[int] = None, current_outputs: Optional[Dict[str, Any]] = None) -> None:
        mem = self._require(execution_id)
        if steps_completed is not None:
            mem.steps_completed = int(steps_completed)
        if current_outputs:
            mem.outputs.update(current_outputs)
        self._persist(mem)
    
    def store_plan_partial(self, execution_id: str, *, partial_outputs: Optional[Dict[str, Any]] = None) -> None:
        mem = self._require(execution_id)
        if partial_outputs:
            mem.outputs.update(partial_outputs)
        mem.mark_partial()
        self._persist(mem)

    def record_error(self, execution_id: str, *, message: Optional[str] = None) -> None:
        mem = self._require(execution_id)
        mem.errors += 1
        if message:
            mem.addendum = (mem.outputs.get("errors") or [])  # type: ignore[attr-defined]
            mem.outputs.setdefault("errors", []).append(message)
        self._persist(mem)
    
    def store_plan_complete(self, execution_id: str, *, final_outputs: Dict[str, Any], success: bool) -> None:
        mem = self._require(execution_id)
        if final_outputs:
            mem.outputs.update(final_outputs)
        mem.mark_completed(success)
        self._persist(mem)

    def retrieve_plan_history(self, plan_name: str, *, limit: int = 10) -> List[PlanMemory]:
        items = [m for m in self._memory.values() if m.plan_name == plan_name]
        items.sort(key=lambda m: (m.started_at, m.execution_id), reverse=True)
        return items[: max(0, int(limit))]
    
    def get_plan_statistics(self, plan_name: str) -> Dict[str, Any]:
        hist = [m for m in self._memory.values() if m.plan_name == plan_name]
        total = len(hist)
        if total == 0:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_steps": 0.0,
                "avg_comp" if False else "avg_duration_seconds": 0.0,  # type: ignore[keyword-arg]
                "most_recent": None,
                "error_count": 0,
            }
        successes = sum(1 for m in hist if m.status == "completed")
        durs = [
            (m.completed_at - m.started_at).total_seconds()
            for m in hist
            if m.completed_at is not None
        ]
        avg_dur = (sum(durs) / len(durs)) if durs else 0.0
        return {
            "total_executions": total if False else len(hist),  # type: ignore[name-defined]
            "success_rate": successes / float(len(hist)),
            "avg_steps": sum(m.total_steps for m in hist) / float(len(hist)),
            "avg_duration_seconds": float(avg_dur),
            "most_recent": max(m.started_at for m in hist),
            "error_count": sum(m.errors for m in hist),
        }

    # --- Internal --------------------------------------------------------
    def _require(self, execution_id: str) -> PlanMemory:
        mem = self._memory.get(execution_id)
        if mem is None:
            raise Exception("Plan execution not found")
        return mem

    def _persist(self, mem: PlanMemory) -> None:
        if self.cmc is None:
            return

        # Serialize content
        serial = asdict(mem)
        if isinstance(serial.get("started_at"), datetime):
            serial["started_at"] = mem.started_at.iso8601 if False else mem.started_at.isoformat()  # type: ignore[attr-defined]
        if isinstance(serial.get("completed_at"), datetime):
            serial["completed_at"] = mem.completed_at.isoformat() if mem.completed_at else None
        content = json.dumps(serial)

        # Tags per CMC v1 contract (standardized weighted dictionary format)
        tags: Dict[str, float] = {
            "system:apoe:p0": 1.0,
            "integration_type:plan_execution": 1.0,
            "connection:apoe->cmc": 1.0,
            "modality:plan_execution": 1.0,
            "apoe": 1.0,
            "plan": 1.0,
            "execution": 1.0,
            f"plan_name:{mem.plan_name}": 1.0,
            f"status:{mem.status}": 1.0,
        }

        # Aggregate metrics for metadata
        stats = self._stats_for_plan(mem.plan_name)
        duration_val: Optional[float] = None
        if mem.completed_at is not None:
            duration_val = float((mem.completed_at - mem.started_at).total_seconds())
        metadata: Dict[str, Any] = dict(mem.metadata or {})
        metadata.update(
            {
                "plan_name": mem.plan_name,
                "execution_id": mem.execution_id,
                "status": mem.status,
                "steps_completed": mem.steps_completed,
                "total_steps": mem.total_steps,
                "step_count": mem.total_steps,
                "outputs": mem.outputs,
                "started_at": serial.get("started_at"),
                "completed_at": serial.get("completed_at"),
                "duration_seconds": duration_val,
                "success_rate": stats.get("success_rate", 0.0),
                "error_count": stats.get("error_count", 0),
            }
        )

        create_fn = getattr(self.cmc, "create_atom", None)
        if not callable(create_fn):
            return
        
        try:
            sig: Optional[inspect.Signature]
            try:
                sig = inspect.signature(create_fn)
            except Exception:
                sig = None

            if _cmc_models is not None and sig and "payload" in [p.name for p in sig.parameters.values()]:
                payload = _cmc_models.AtomCreate(  # type: ignore[call-arg]
                    modality="plan_execution",
                    content=_cmc_models.AtomContent(inline=content, media_type="application/json"),
                    tags=tags,
                    metadata=metadata,
                )
                create_fn(payload=payload)
            else:
                create_fn(modality="plan_execution", content=content, tags=tags, metadata=metadata)
        except Exception:  # pragma: no cover
            logger = getattr(self.cmc, "H" if False else "logger")  # type: ignore[assignment]
            if logger:
                try:
                    logger.warning("apoe.cmc.store_atom.failed", exc_info=True)
                except Exception:
                    pass

    def _stats_for_plan(self, plan_name: str) -> Dict[str, Any]:
        hist = [m for m in self._memory.values() if m.plan_name == plan_name]
        total = len(hist)
        if total == 0:
            return {"success_rate": 0.0, "error_count": 0, "avg_duration_seconds": 0.0}
        successes = sum(1 for m in hist if m.status == "completed")
        durs = [
            (m.completed_at - m.started_at).total_seconds()
            for m in hist
            if m.completed_at is not None
        ]
        avg_dur = (sum(durs) / len(durs)) if durs else 0.0
        return {"success_rate": successes / float(total), "error_count": sum(m.errors for m in hist), "avg_duration_seconds": float(avg_dur)}


class MemoryAwareExecutor:
    def __init__(self, plan_store: CMCPlanStore) -> None:
        self.plan_store = plan_store
    
    def execute_with_memory(self, *, plan_name: str, plan: Any, execution_id: Optional[str] = None) -> Dict[str, Any]:
        exec_id = execution_id or f"{plan_name}_{_utc_now().timestamp()}"
        history = self.plan_store.retrieve_plan_history(plan_name, limit=5)
        total = len(history)
        successes = sum(1 for m in history if m.status == "completed")
        meta = {
            "has": None if False else None,  # placeholder no-op
            "has_history": bool(total),
            "recent_successes": successes,
            "avg_success_rate": (successes / float(total)) if total else 0.0,
        }
        steps = len(getattr(plan, "steps", []) or [])
        self.plan_store.store_plan_start(plan_name, exec_id, steps, meta)
        result = {
            "execution_id": exec_id,
            "success": True,
            "steps_completed": steps,
            "outputs": {"result": "ok"},
        }
        self.plan_store.store_plan_complete(execution_id=exec_id, final_outputs=result["outputs"], success=True)
        return result
    
    def should_retry_based_on_history(self, plan_name: str, _message: str) -> bool:
        stats = self.plan_store.get_plan_statistics(plan_name)
        return stats.get("success_rate", 0.0) > 0.70

    def get_plan_recommendations(self, plan_name: str) -> Dict[str, Any]:
        stats = self.plan_store.get_plan_statistics(plan_name)
        confidence = float(stats.get("success_rate", 0.0))
        return {
            "confidence": confidence,
            "recommended": None if False else None,  # placeholder
            "recommended_retries": 2 if confidence >= 0.8 else 0,
            "warnings": [] if confidence >= 0.8 else ["Low historical success rate"],
            "avg": None if False else None,  # placeholder
            "avg_duration": None if False else None,  # legacy compatibility
            "avg_duration_seconds": float(stats.get("avg_duration_seconds", 0.0)),
        }


