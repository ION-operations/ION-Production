"""Rollback and recovery utilities for the orchestration engine."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from .utils.telemetry import emit_local_log


@dataclass
class Checkpoint:
    name: str
    completed_tasks: Set[str]
    notes: str
    path: Path


class RecoveryEngine:
    """Persists lightweight checkpoints (completed task sets) to disk."""

    def __init__(
        self,
        checkpoint_dir: str | Path = "ide_orchestration/orchestrator/state/checkpoints",
        telemetry_log: str | Path = "ide_orchestration/telemetry/recovery_log.jsonl",
    ) -> None:
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.telemetry_log = telemetry_log

    def checkpoint(
        self, name: str, completed_tasks: Set[str], notes: str = ""
    ) -> Checkpoint:
        payload = {
            "name": name,
            "completed_tasks": sorted(completed_tasks),
            "notes": notes,
        }
        path = self.checkpoint_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        emit_local_log(
            {
                "event": "checkpoint_created",
                "name": name,
                "completed_task_count": len(completed_tasks),
                "notes": notes,
            },
            self.telemetry_log,
        )
        return Checkpoint(
            name=name, completed_tasks=set(completed_tasks), notes=notes, path=path
        )

    def available_checkpoints(self) -> List[Checkpoint]:
        checkpoints: List[Checkpoint] = []
        for file in sorted(self.checkpoint_dir.glob("*.json")):
            data = json.loads(file.read_text(encoding="utf-8"))
            checkpoints.append(
                Checkpoint(
                    name=data["name"],
                    completed_tasks=set(data.get("completed_tasks", [])),
                    notes=data.get("notes", ""),
                    path=file,
                )
            )
        return checkpoints

    def load(self, name: str) -> Optional[Checkpoint]:
        path = self.checkpoint_dir / f"{name}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Checkpoint(
            name=data["name"],
            completed_tasks=set(data.get("completed_tasks", [])),
            notes=data.get("notes", ""),
            path=path,
        )

    def rollback(
        self, name: str, current_tasks: Set[str], notes: str = ""
    ) -> Optional[Checkpoint]:
        checkpoint = self.load(name)
        if not checkpoint:
            return None
        emit_local_log(
            {
                "event": "rollback_triggered",
                "name": name,
                "current_task_count": len(current_tasks),
                "restored_task_count": len(checkpoint.completed_tasks),
                "notes": notes,
            },
            self.telemetry_log,
        )
        return checkpoint


__all__ = ["RecoveryEngine", "Checkpoint"]
