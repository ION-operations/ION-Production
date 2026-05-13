"""Progress tracker utilities for the IDE orchestration program."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .graph_manager import GraphManager, TaskNode


@dataclass
class PhaseProgress:
    phase_id: str
    completed: int
    total: int

    @property
    def percentage(self) -> float:
        return (self.completed / self.total) * 100 if self.total else 0.0


class ProgressTracker:
    """Aggregates task completion signals and produces simple predictions."""

    def __init__(self, manager: GraphManager) -> None:
        self.manager = manager

    def phase_progress(self, completed_tasks: Set[str]) -> List[PhaseProgress]:
        results: List[PhaseProgress] = []
        for phase_id, phase in self.manager.phases.items():
            tasks = [
                task
                for task in self.manager.tasks.values()
                if task.phase_id == phase_id
            ]
            total = len(tasks)
            done = sum(1 for task in tasks if task.id in completed_tasks)
            results.append(PhaseProgress(phase_id=phase_id, completed=done, total=total))
        return results

    def workstream_progress(self, completed_tasks: Set[str]) -> Dict[str, Dict[str, int]]:
        progress: Dict[str, Dict[str, int]] = {}
        for ws_id, ws in self.manager.workstreams.items():
            tasks = ws.get("tasks", [])
            total = len(tasks)
            done = sum(1 for task in tasks if task["id"] in completed_tasks)
            progress[ws_id] = {"completed": done, "total": total}
        return progress

    def predictive_metrics(
        self,
        completed_tasks: Set[str],
        historical_velocity: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """Estimate completion time using simple velocity heuristics."""
        historical_velocity = historical_velocity or {}
        metrics: Dict[str, Dict[str, float]] = {}
        for phase in self.phase_progress(completed_tasks):
            remaining = max(phase.total - phase.completed, 0)
            velocity = historical_velocity.get(phase.phase_id, 1.0)
            eta = remaining / velocity if velocity else float("inf")
            metrics[phase.phase_id] = {
                "percent_complete": round(phase.percentage, 2),
                "remaining_tasks": remaining,
                "velocity_tasks_per_day": velocity,
                "eta_days": round(eta, 2) if eta != float("inf") else -1,
            }
        return metrics

    def summarize(
        self,
        completed_tasks: Set[str],
        historical_velocity: Optional[Dict[str, float]] = None,
    ) -> Dict[str, any]:
        return {
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "completed": phase.completed,
                    "total": phase.total,
                    "percent_complete": round(phase.percentage, 2),
                }
                for phase in self.phase_progress(completed_tasks)
            ],
            "workstreams": self.workstream_progress(completed_tasks),
            "predictive_metrics": self.predictive_metrics(
                completed_tasks, historical_velocity
            ),
        }


__all__ = ["ProgressTracker", "PhaseProgress"]
