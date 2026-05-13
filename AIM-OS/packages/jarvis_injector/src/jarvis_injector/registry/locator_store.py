from __future__ import annotations

from pathlib import Path
from typing import Any

from jarvis_injector.memory.vaults import ArtifactVaults


class LocatorStore:
    def __init__(self, root: Path, vaults: ArtifactVaults) -> None:
        self._root = root
        self._vaults = vaults
        self._root.mkdir(parents=True, exist_ok=True)

    def load(self, target_id: str) -> dict[str, Any] | None:
        return self._vaults.load_json(self._root / f"{target_id}.json")

    def save(self, target_id: str, payload: dict[str, Any]) -> Path:
        return self._vaults.save_json(self._root / f"{target_id}.json", payload)

