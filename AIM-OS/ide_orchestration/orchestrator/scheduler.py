"""Task scheduler that performs basic capability matching.

The scheduler consumes the flattened task graph exposed by ``GraphManager`` and
attempts to pair each ready task with the most appropriate agent profile found
in ``ide_orchestration/agents/registry.json`` (or a user-provided registry
path).  The matching logic is intentionally lightweight so it can run locally
without external dependencies while still surfacing useful rationale for human
review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .graph_manager import GraphManager, TaskNode


@dataclass
class AgentProfile:
    """Representation of a single agent entry in the registry."""

    id: str
    ai_modes: List[str] = field(default_factory=list)
    domain_strengths: List[str] = field(default_factory=list)
    api_contracts: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    availability: str = "available"  # e.g. available, busy, offline
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_available(self) -> bool:
        return self.availability.lower() not in {"busy", "offline", "blocked"}


@dataclass
class TaskAssignment:
    """Suggested pairing between a task and an agent."""

    task_id: str
    agent_id: Optional[str]
    score: float
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class Scheduler:
    """Computes ready tasks then proposes agent assignments."""

    def __init__(
        self,
        graph_manager: GraphManager,
        agent_registry: str | Path = "ide_orchestration/agents/registry.json",
    ) -> None:
        self.graph_manager = graph_manager
        self.registry_path = Path(agent_registry)
        self.agents = self._load_agents()

    # ------------------------------------------------------------------ #
    # Registry helpers
    # ------------------------------------------------------------------ #
    def _load_agents(self) -> List[AgentProfile]:
        if not self.registry_path.exists():
            return []

        with self.registry_path.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)

        items = payload.get("agents", payload)
        agents: List[AgentProfile] = []
        for item in items:
            try:
                agents.append(
                    AgentProfile(
                        id=item["id"],
                        ai_modes=item.get("ai_modes", []),
                        domain_strengths=item.get("domain_strengths", []),
                        api_contracts=item.get("api_contracts", []),
                        quality_score=float(item.get("quality_score", 0)),
                        availability=item.get("availability", "available"),
                        metadata=item.get("metadata", {}),
                    )
                )
            except KeyError:
                # Malformed entries are skipped but we still surface a stub so
                # the caller knows no agents were loaded.
                continue
        return agents

    # ------------------------------------------------------------------ #
    # Scheduling
    # ------------------------------------------------------------------ #
    def build_schedule(
        self,
        completed_tasks: Set[str],
        completed_phases: Optional[Set[str]] = None,
        blocked_tasks: Optional[Set[str]] = None,
        max_assignments: Optional[int] = None,
    ) -> List[TaskAssignment]:
        """Compute ready tasks and match each to the best-fit agent."""
        ready = self.graph_manager.compute_ready_tasks(
            completed_tasks=completed_tasks,
            completed_phases=completed_phases or set(),
            blocked_tasks=blocked_tasks or set(),
        )

        assignments: List[TaskAssignment] = []
        for task in ready:
            agent_id, score, rationale = self._select_agent(task)
            assignments.append(
                TaskAssignment(
                    task_id=task.id,
                    agent_id=agent_id,
                    score=score,
                    rationale=rationale,
                    metadata={
                        "phase": task.phase_id,
                        "workstream": task.workstream_id,
                        "dependencies": task.dependencies,
                        "gate_refs": task.gate_refs,
                    },
                )
            )
            if max_assignments and len(assignments) >= max_assignments:
                break
        return assignments

    def _select_agent(self, task: TaskNode) -> Tuple[Optional[str], float, str]:
        if not self.agents:
            return (None, 0.0, "No agent registry loaded; manual assignment required")

        best_agent: Optional[AgentProfile] = None
        best_score = -1.0
        best_reason = ""

        workstream_owner = self._workstream_owner(task.workstream_id)

        for agent in self.agents:
            score, reason = self._score_agent(agent, task, workstream_owner)
            if score > best_score:
                best_agent = agent
                best_score = score
                best_reason = reason

        if not best_agent:
            return (
                None,
                0.0,
                "All agents unavailable or incompatible; escalate to coordinator",
            )

        return (best_agent.id, round(best_score, 3), best_reason)

    def _score_agent(
        self, agent: AgentProfile, task: TaskNode, workstream_owner: Optional[str]
    ) -> Tuple[float, str]:
        if not agent.is_available:
            return (-1.0, f"{agent.id} unavailable ({agent.availability})")

        score = 0.0
        rationale: List[str] = []

        mode_overlap = _overlap(agent.ai_modes, task.ai_modes)
        if mode_overlap:
            score += 1.5 * mode_overlap
            rationale.append(f"ai_modes:{mode_overlap}")

        api_overlap = _overlap(agent.api_contracts, task.api_contracts)
        if api_overlap:
            score += 1.0 * api_overlap
            rationale.append(f"api:{api_overlap}")

        # Bonus when the agent owns the workstream in the ChainSpec
        if workstream_owner and workstream_owner == agent.id:
            score += 0.75
            rationale.append("workstream_owner")

        # Quality score is treated as a soft multiplier
        score += 0.5 * agent.quality_score
        rationale.append(f"quality:{agent.quality_score:.2f}")

        # If the task references gate refs requiring evidence logging, prefer
        # agents with documented metadata support.
        if "task.evidence_logged" in task.gate_refs and agent.metadata.get(
            "evidence_logging"
        ):
            score += 0.5
            rationale.append("evidence_logging")

        return (score, ", ".join(rationale))

    def _workstream_owner(self, workstream_id: str) -> Optional[str]:
        try:
            workstream = self.graph_manager.get_workstream(workstream_id)
        except KeyError:
            return None
        return workstream.get("owner")


def _overlap(candidate: Sequence[str], required: Sequence[str]) -> float:
    if not candidate or not required:
        return 0.0
    a = set(map(str.lower, candidate))
    b = set(map(str.lower, required))
    return len(a & b) / len(b or {1})


__all__ = ["Scheduler", "AgentProfile", "TaskAssignment"]
