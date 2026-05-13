from __future__ import annotations

from pathlib import Path

from jarvis_injector.memory.vaults import ArtifactVaults


class TemplateStore:
    def __init__(self, vaults: ArtifactVaults) -> None:
        self._vaults = vaults

    def template_dir(self, target_id: str) -> Path:
        return self._vaults.target_template_dir(target_id)

    def list_family(self, target_id: str, family: str) -> list[Path]:
        root = self.template_dir(target_id)
        return sorted(root.glob(f"{family}*"))

