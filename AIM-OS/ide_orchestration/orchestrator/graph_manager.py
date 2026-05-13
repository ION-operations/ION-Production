"""Graph Manager for IDE orchestration ChainSpec.

Loads the epic ChainSpec YAML file, indexes phases/workstreams/tasks, and
provides helper methods to compute ready queues based on dependency state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


@dataclass
class TaskNode:
    """Flattened view of a task pulled from the ChainSpec."""

    id: str
    description: str
    phase_id: str
    workstream_id: str
    dependencies: List[str] = field(default_factory=list)
    gate_refs: List[str] = field(default_factory=list)
    ai_modes: List[str] = field(default_factory=list)
    api_contracts: List[str] = field(default_factory=list)
    evidence_targets: List[str] = field(default_factory=list)
    outputs: List[dict] = field(default_factory=list)


class GraphManager:
    """Loads ChainSpec.yaml and exposes dependency-aware helpers."""

    def __init__(self, spec_path: str | Path):
        self.spec_path = Path(spec_path)
        if not self.spec_path.exists():
            raise FileNotFoundError(f"ChainSpec file not found: {self.spec_path}")

        self.spec: Dict = {}
        self.phases: Dict[str, Dict] = {}
        self.workstreams: Dict[str, Dict] = {}
        self.tasks: Dict[str, TaskNode] = {}
        self._load_spec()

    # ------------------------------------------------------------------ #
    # Spec loading / indexing
    # ------------------------------------------------------------------ #
    def _load_spec(self) -> None:
        """Load YAML spec and build indexes."""
        with self.spec_path.open("r", encoding="utf-8") as fp:
            self.spec = yaml.safe_load(fp)

        epic = self.spec.get("epic", {})
        raw_phases = epic.get("phases", [])
        raw_workstreams = self.spec.get("workstreams", [])

        self.phases = {phase["id"]: phase for phase in raw_phases}
        self.workstreams = {ws["id"]: ws for ws in raw_workstreams}
        self.tasks = {}

        for ws in raw_workstreams:
            phase_id = ws["phase"]
            for task in ws.get("tasks", []):
                task_id = task["id"]
                node = TaskNode(
                    id=task_id,
                    description=task.get("description", ""),
                    phase_id=phase_id,
                    workstream_id=ws["id"],
                    dependencies=task.get("dependencies", []),
                    gate_refs=task.get("gate_refs", []),
                    ai_modes=task.get("ai_modes", []),
                    api_contracts=task.get("api_contracts", []),
                    evidence_targets=task.get("evidence_targets", []),
                    outputs=task.get("outputs", []),
                )
                self.tasks[task_id] = node

    def refresh(self) -> None:
        """Reload spec from disk (useful when ChainSpec changes)."""
        self._load_spec()

    # ------------------------------------------------------------------ #
    # Query helpers
    # ------------------------------------------------------------------ #
    def list_phases(self) -> List[str]:
        return list(self.phases.keys())

    def list_workstreams(self) -> List[str]:
        return list(self.workstreams.keys())

    def list_tasks(self) -> List[str]:
        return list(self.tasks.keys())

    def get_phase_dependencies(self, phase_id: str) -> List[str]:
        return self.phases.get(phase_id, {}).get("dependencies", [])

    def get_workstream(self, workstream_id: str) -> Dict:
        return self.workstreams[workstream_id]

    def get_task(self, task_id: str) -> TaskNode:
        return self.tasks[task_id]

    # ------------------------------------------------------------------ #
    # Dependency resolution
    # ------------------------------------------------------------------ #
    def compute_ready_tasks(
        self,
        completed_tasks: Set[str],
        completed_phases: Optional[Set[str]] = None,
        blocked_tasks: Optional[Set[str]] = None,
    ) -> List[TaskNode]:
        """Return tasks whose dependencies (task + phase) are satisfied."""
        completed_phases = completed_phases or set()
        blocked_tasks = blocked_tasks or set()
        ready: List[TaskNode] = []

        for task_id, task in self.tasks.items():
            if task_id in completed_tasks or task_id in blocked_tasks:
                continue

            # Phase dependency check
            phase_deps = set(self.get_phase_dependencies(task.phase_id))
            if not phase_deps.issubset(completed_phases):
                continue

            # Task dependency check
            if not set(task.dependencies).issubset(completed_tasks):
                continue

            ready.append(task)

        return ready

    def compute_phase_status(
        self, completed_tasks: Set[str]
    ) -> Dict[str, Tuple[int, int]]:
        """Return mapping phase_id -> (completed_task_count, total_tasks)."""
        status: Dict[str, Tuple[int, int]] = {}
        for phase_id in self.phases:
            total = sum(
                1 for task in self.tasks.values() if task.phase_id == phase_id
            )
            done = sum(
                1
                for task in self.tasks.values()
                if task.phase_id == phase_id and task.id in completed_tasks
            )
            status[phase_id] = (done, total)
        return status


__all__ = ["GraphManager", "TaskNode"]
