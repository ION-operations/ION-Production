"""CMC Integration for APOE

Enables memory-aware orchestration - plans can store and retrieve from CMC.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from dataclasses import asdict
import json


@dataclass
# NL_TAG: VIF-INTEG-001 | Represents a stored plan execution in CMC. | class PlanMemory | []
class PlanMemory:
    """Represents a stored plan execution in CMC."""
    plan_name: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str  # "running", "completed", "failed"
    steps_completed: int
    total_steps: int
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]


# NL_TAG: VIF-INTEG-002 | Stores and retrieves plan executions from CMC. | class CMCPlanStore | []
class CMCPlanStore:
    """Stores and retrieves plan executions from CMC."""
    
    def __init__(self, cmc_client: Optional[Any] = None):
        """
        Initialize CMC plan store.
        
        Args:
            cmc_client: CMC client instance (optional, for testing can be None)
        """
        self.cmc = cmc_client
        self._memory_cache: Dict[str, PlanMemory] = {}
    
    def store_plan_start(
        self,
        plan_name: str,
        execution_id: str,
        total_steps: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store plan execution start in CMC."""
        memory = PlanMemory(
            plan_name=plan_name,
            execution_id=execution_id,
            started_at=datetime.utcnow(),
            completed_at=None,
            status="running",
            steps_completed=0,
            total_steps=total_steps,
            outputs={},
            metadata=metadata or {}
        )
        
        # Store in cache (in production would store to CMC)
        self._memory_cache[execution_id] = memory
        
        # If CMC client available, store atom
        if self.cmc:
            self._store_to_cmc(memory)
        
        return execution_id
    
    def update_plan_progress(
        self,
        execution_id: str,
        steps_completed: int,
        current_outputs: Dict[str, Any]
    ):
        """Update plan execution progress in CMC."""
        if execution_id not in self._memory_cache:
            raise ValueError(f"Plan execution {execution_id} not found")
        
        memory = self._memory_cache[execution_id]
        memory.steps_completed = steps_completed
        memory.outputs.update(current_outputs)
        
        # Update in CMC if available
        if self.cmc:
            self._store_to_cmc(memory)
    
    def store_plan_complete(
        self,
        execution_id: str,
        final_outputs: Dict[str, Any],
        success: bool
    ):
        """Store plan execution completion in CMC."""
        if execution_id not in self._memory_cache:
            raise ValueError(f"Plan execution {execution_id} not found")
        
        memory = self._memory_cache[execution_id]
        memory.completed_at = datetime.utcnow()
        memory.status = "completed" if success else "failed"
        memory.outputs.update(final_outputs)
        
        # Store in CMC if available
        if self.cmc:
            self._store_to_cmc(memory)
    
    def retrieve_plan_history(
        self,
        plan_name: str,
        limit: int = 10
    ) -> List[PlanMemory]:
        """Retrieve historical executions of a plan from CMC."""
        # Filter from cache
        results = [
            m for m in self._memory_cache.values()
            if m.plan_name == plan_name
        ]
        
        # Sort by most recent first
        results.sort(key=lambda m: m.started_at, reverse=True)
        
        return results[:limit]
    
    def retrieve_similar_plans(
        self,
        plan_name: str,
        min_similarity: float = 0.70
    ) -> List[PlanMemory]:
        """Retrieve similar plan executions using semantic search."""
        # In production, would use CMC + HHNI for semantic search
        # For now, simple name matching
        results = [
            m for m in self._memory_cache.values()
            if plan_name.lower() in m.plan_name.lower() or m.plan_name.lower() in plan_name.lower()
        ]
        
        return results
    
    def get_plan_statistics(self, plan_name: str) -> Dict[str, Any]:
        """Get statistics for plan executions."""
        history = self.retrieve_plan_history(plan_name, limit=100)
        
        if not history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_steps": 0.0,
                "avg_duration_seconds": 0.0
            }
        
        completed = [h for h in history if h.completed_at]
        successful = [h for h in history if h.status == "completed"]
        
        total_duration = sum(
            (h.completed_at - h.started_at).total_seconds()
            for h in completed
        )
        
        return {
            "total_executions": len(history),
            "success_rate": len(successful) / len(history) if history else 0.0,
            "avg_steps": sum(h.total_steps for h in history) / len(history),
            "avg_duration_seconds": total_duration / len(completed) if completed else 0.0,
            "most_recent": history[0].started_at if history else None
        }
    
    def _store_to_cmc(self, memory: PlanMemory):
        """Store plan memory to CMC (internal helper)."""
        if not self.cmc:
            return
        try:
            # Lazy import to avoid hard dependency when running without CMC
            from cmc_service.models import AtomCreate, AtomContent

            payload = AtomCreate(
                modality="plan_execution",
                content=AtomContent(
                    inline=json.dumps(asdict(memory), default=str),
                    media_type="application/json",
                ),
                tags={
                    "apoe": 1.0,
                    "plan": 1.0,
                    memory.plan_name: 0.9,
                    f"status:{memory.status}": 0.8,
                },
                metadata={
                    "plan_name": memory.plan_name,
                    "execution_id": memory.execution_id,
                    "started_at": memory.started_at.isoformat(),
                    "completed_at": memory.completed_at.isoformat() if memory.completed_at else None,
                    "steps_completed": memory.steps_completed,
                    "total_steps": memory.total_steps,
                    **(memory.metadata or {}),
                },
            )
            # Correlate by execution_id for traceability
            self.cmc.create_atom(payload, correlation_id=memory.execution_id)
        except Exception:
            # Best-effort; do not raise to avoid breaking orchestration
            return


# NL_TAG: VIF-INTEG-003 | Executor that stores execution history in CMC. | class MemoryAwareExecutor | []
class MemoryAwareExecutor:
    # NL_TAG: VIF-INTEG-004 | Initialize CMC plan store. | __init__(self, cmc_client) | []
    def __init__(self, cmc_client: Optional[Any] = None):
        """
        Initialize CMC plan store.
        
        Args:
            cmc_client: CMC client instance (optional, for testing can be None)
        """
        self.cmc = cmc_client
        self._memory_cache: Dict[str, PlanMemory] = {}
    
    # NL_TAG: VIF-INTEG-005 | Store plan execution start in CMC. | store_plan_start(self, plan_name, execution_id, total_steps, metadata) | []
    def store_plan_start(
        self,
        plan_name: str,
        execution_id: str,
        total_steps: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store plan execution start in CMC."""
        memory = PlanMemory(
            plan_name=plan_name,
            execution_id=execution_id,
            started_at=datetime.utcnow(),
            completed_at=None,
            status="running",
            steps_completed=0,
            total_steps=total_steps,
            outputs={},
            metadata=metadata or {}
        )
        
        # Store in cache (in production would store to CMC)
        self._memory_cache[execution_id] = memory
        
        # If CMC client available, store atom
        if self.cmc:
            self._store_to_cmc(memory)
        
        return execution_id
    
    # NL_TAG: VIF-INTEG-006 | Update plan execution progress in CMC. | update_plan_progress(self, execution_id, steps_completed, current_outputs) | []
    def update_plan_progress(
        self,
        execution_id: str,
        steps_completed: int,
        current_outputs: Dict[str, Any]
    ):
        """Update plan execution progress in CMC."""
        if execution_id not in self._memory_cache:
            raise ValueError(f"Plan execution {execution_id} not found")
        
        memory = self._memory_cache[execution_id]
        memory.steps_completed = steps_completed
        memory.outputs.update(current_outputs)
        
        # Update in CMC if available
        if self.cmc:
            self._store_to_cmc(memory)
    
    # NL_TAG: VIF-INTEG-007 | Store plan execution completion in CMC. | store_plan_complete(self, execution_id, final_outputs, success) | []
    def store_plan_complete(
        self,
        execution_id: str,
        final_outputs: Dict[str, Any],
        success: bool
    ):
        """Store plan execution completion in CMC."""
        if execution_id not in self._memory_cache:
            raise ValueError(f"Plan execution {execution_id} not found")
        
        memory = self._memory_cache[execution_id]
        memory.completed_at = datetime.utcnow()
        memory.status = "completed" if success else "failed"
        memory.outputs.update(final_outputs)
        
        # Store in CMC if available
        if self.cmc:
            self._store_to_cmc(memory)
    
    # NL_TAG: VIF-INTEG-008 | Retrieve historical executions of a plan from CMC. | retrieve_plan_history(self, plan_name, limit) | []
    def retrieve_plan_history(
        self,
        plan_name: str,
        limit: int = 10
    ) -> List[PlanMemory]:
        """Retrieve historical executions of a plan from CMC."""
        # Filter from cache
        results = [
            m for m in self._memory_cache.values()
            if m.plan_name == plan_name
        ]
        
        # Sort by most recent first
        results.sort(key=lambda m: m.started_at, reverse=True)
        
        return results[:limit]
    
    # NL_TAG: VIF-INTEG-009 | Retrieve similar plan executions using semantic search. | retrieve_similar_plans(self, plan_name, min_similarity) | []
    def retrieve_similar_plans(
        self,
        plan_name: str,
        min_similarity: float = 0.70
    ) -> List[PlanMemory]:
        """Retrieve similar plan executions using semantic search."""
        # In production, would use CMC + HHNI for semantic search
        # For now, simple name matching
        results = [
            m for m in self._memory_cache.values()
            if plan_name.lower() in m.plan_name.lower() or m.plan_name.lower() in plan_name.lower()
        ]
        
        return results
    
    # NL_TAG: VIF-INTEG-010 | Get statistics for plan executions. | get_plan_statistics(self, plan_name) | []
    def get_plan_statistics(self, plan_name: str) -> Dict[str, Any]:
        """Get statistics for plan executions."""
        history = self.retrieve_plan_history(plan_name, limit=100)
        
        if not history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_steps": 0.0,
                "avg_duration_seconds": 0.0
            }
        
        completed = [h for h in history if h.completed_at]
        successful = [h for h in history if h.status == "completed"]
        
        total_duration = sum(
            (h.completed_at - h.started_at).total_seconds()
            for h in completed
        )
        
        return {
            "total_executions": len(history),
            "success_rate": len(successful) / len(history) if history else 0.0,
            "avg_steps": sum(h.total_steps for h in history) / len(history),
            "avg_duration_seconds": total_duration / len(completed) if completed else 0.0,
            "most_recent": history[0].started_at if history else None
        }
    
    # NL_TAG: VIF-INTEG-011 | Store plan memory to CMC (internal helper). | _store_to_cmc(self, memory) | []
    def _store_to_cmc(self, memory: PlanMemory):
        """Store plan memory to CMC (internal helper)."""
        if not self.cmc:
            return
        try:
            from cmc_service.models import AtomCreate, AtomContent

            payload = AtomCreate(
                modality="plan_execution",
                content=AtomContent(
                    inline=json.dumps(asdict(memory), default=str),
                    media_type="application/json",
                ),
                tags={
                    "apoe": 1.0,
                    "plan": 1.0,
                    memory.plan_name: 0.9,
                    f"status:{memory.status}": 0.8,
                },
                metadata={
                    "plan_name": memory.plan_name,
                    "execution_id": memory.execution_id,
                    "started_at": memory.started_at.isoformat(),
                    "completed_at": memory.completed_at.isoformat() if memory.completed_at else None,
                    "steps_completed": memory.steps_completed,
                    "total_steps": memory.total_steps,
                    **(memory.metadata or {}),
                },
            )
            self.cmc.create_atom(payload, correlation_id=memory.execution_id)
        except Exception:
            return


class MemoryAwareExecutor:
    """Executor that stores execution history in CMC."""
    
    # NL_TAG: VIF-INTEG-012 |   init   | __init__(self, plan_store) | []
    def __init__(self, plan_store: CMCPlanStore):
        self.plan_store = plan_store
    
    # NL_TAG: VIF-INTEG-013 | Execute plan and store execution in CMC. | execute_with_memory(self, plan_name, plan, execution_id) | []
    def execute_with_memory(
        self,
        plan_name: str,
        plan,  # ExecutionPlan
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute plan and store execution in CMC."""
        exec_id = execution_id or f"{plan_name}_{datetime.utcnow().timestamp()}"
        
        # Check if similar plan executed recently
        history = self.plan_store.retrieve_plan_history(plan_name, limit=5)
        recent_success = [h for h in history if h.status == "completed"]
        
        metadata = {
            "has_history": len(history) > 0,
            "recent_successes": len(recent_success),
            "avg_success_rate": sum(1 for h in history if h.status == "completed") / len(history) if history else 0.0
        }
        
        # Store plan start
        self.plan_store.store_plan_start(
            plan_name=plan_name,
            execution_id=exec_id,
            total_steps=len(plan.steps) if hasattr(plan, 'steps') else 0,
            metadata=metadata
        )
        
        # Execute plan (would call actual PlanExecutor here)
        # For now, simulate
        result = {
            "execution_id": exec_id,
            "success": True,
            "steps_completed": len(plan.steps) if hasattr(plan, 'steps') else 0,
            "outputs": {"result": "simulated"}
        }
        
        # Store completion
        self.plan_store.store_plan_complete(
            execution_id=exec_id,
            final_outputs=result["outputs"],
            success=result["success"]
        )
        
        return result
    
    # NL_TAG: VIF-INTEG-014 | Determine if retry recommended based on historical success. | should_retry_based_on_history(self, plan_name, current_failure_reason) | []
    def should_retry_based_on_history(
        self,
        plan_name: str,
        current_failure_reason: str
    ) -> bool:
        """Determine if retry recommended based on historical success."""
        stats = self.plan_store.get_plan_statistics(plan_name)
        
        # If success rate > 70%, retry is worth it
        if stats["success_rate"] > 0.70:
            return True
        
        # If no history, don't retry (unknown outcome)
        if stats["total_executions"] == 0:
            return False
        
        # If success rate very low, don't retry
        return False
    
    # NL_TAG: VIF-INTEG-015 | Get recommendations for plan execution based on history. | get_plan_recommendations(self, plan_name) | []
    def get_plan_recommendations(self, plan_name: str) -> Dict[str, Any]:
        """Get recommendations for plan execution based on history."""
        stats = self.plan_store.get_plan_statistics(plan_name)
        history = self.plan_store.retrieve_plan_history(plan_name, limit=10)
        
        recommendations = {
            "confidence": stats["success_rate"],
            "expected_duration": stats["avg_duration_seconds"],
            "recommended_retries": 0,
            "warnings": []
        }
        
        # Add recommendations based on stats
        if stats["success_rate"] < 0.50:
            recommendations["warnings"].append("Low historical success rate")
            recommendations["recommended_retries"] = 0
        elif stats["success_rate"] > 0.80:
            recommendations["recommended_retries"] = 2
        
        if stats["avg_duration_seconds"] > 300:  # 5 minutes
            recommendations["warnings"].append("Plan typically takes long time")
        
        return recommendations

