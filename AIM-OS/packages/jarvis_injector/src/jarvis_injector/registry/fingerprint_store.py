from __future__ import annotations

from pathlib import Path

from jarvis_injector.core.models import WindowFingerprint
from jarvis_injector.memory.vaults import ArtifactVaults


class FingerprintStore:
    def __init__(self, root: Path, vaults: ArtifactVaults) -> None:
        self._root = root
        self._vaults = vaults
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, fingerprint: WindowFingerprint) -> Path:
        filename = f"{fingerprint.target_id}-{fingerprint.title_hash}.json"
        return self._vaults.save_json(
            self._root / filename,
            fingerprint.model_dump(mode="json"),
        )

