from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jarvis_injector.config import InjectorConfig


class ArtifactVaults:
    def __init__(self, config: InjectorConfig) -> None:
        self.config = config
        self.config.ensure_directories()

    def save_json(self, path: Path, payload: dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
        return path

    def load_json(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def target_template_dir(self, target_id: str) -> Path:
        path = self.config.templates_dir / target_id
        path.mkdir(parents=True, exist_ok=True)
        return path

