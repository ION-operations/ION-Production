from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


def _repo_root() -> Path:
    configured = os.getenv("AIMOS_REPO_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[4]


class InjectorConfig(BaseModel):
    repo_root: Path = Field(default_factory=_repo_root)
    api_host: str = Field(default_factory=lambda: os.getenv("JARVIS_INJECTOR_HOST", "127.0.0.1"))
    api_port: int = Field(default_factory=lambda: int(os.getenv("JARVIS_INJECTOR_PORT", "5013")))
    worker_count: int = Field(default_factory=lambda: int(os.getenv("JARVIS_INJECTOR_WORKERS", "1")))
    hotkey: str = Field(default_factory=lambda: os.getenv("JARVIS_INJECTOR_HOTKEY", "CTRL+ALT+J"))

    @property
    def targets_dir(self) -> Path:
        return self.repo_root / "config" / "window_targets"

    @property
    def state_root(self) -> Path:
        return self.repo_root / "state" / "window_injector"

    @property
    def locators_dir(self) -> Path:
        return self.state_root / "locators"

    @property
    def templates_dir(self) -> Path:
        return self.state_root / "templates"

    @property
    def fingerprints_dir(self) -> Path:
        return self.state_root / "fingerprints"

    @property
    def motions_dir(self) -> Path:
        return self.state_root / "motions"

    @property
    def workflows_dir(self) -> Path:
        return self.state_root / "workflows"

    @property
    def episodes_db_path(self) -> Path:
        return self.state_root / "episodes.db"

    @property
    def logs_root(self) -> Path:
        return self.repo_root / "logs" / "window_injector"

    @property
    def executions_log_path(self) -> Path:
        return self.logs_root / "executions" / "executions.jsonl"

    @property
    def screenshots_dir(self) -> Path:
        return self.logs_root / "screenshots"

    def ensure_directories(self) -> None:
        directories = [
            self.targets_dir,
            self.locators_dir,
            self.templates_dir,
            self.fingerprints_dir,
            self.motions_dir,
            self.workflows_dir,
            self.executions_log_path.parent,
            self.screenshots_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

