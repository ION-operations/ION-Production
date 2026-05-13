from __future__ import annotations

import json
from pathlib import Path

from jarvis_injector.core.models import TargetProfile, TargetSummary


class TargetRegistry:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._targets: dict[str, TargetProfile] = {}
        self.reload()

    def reload(self) -> None:
        self._targets.clear()
        self._root.mkdir(parents=True, exist_ok=True)
        for path in sorted(self._root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            target = TargetProfile.model_validate(payload)
            self._targets[target.id] = target

    def list_targets(self) -> list[TargetProfile]:
        return list(self._targets.values())

    def summaries(self) -> list[TargetSummary]:
        return [
            TargetSummary(
                id=target.id,
                display_name=target.display_name,
                preferred_adapters=target.preferred_adapters,
                verification_policy=target.verification_policy,
            )
            for target in self._targets.values()
        ]

    def get(self, target_id: str) -> TargetProfile | None:
        return self._targets.get(target_id)

