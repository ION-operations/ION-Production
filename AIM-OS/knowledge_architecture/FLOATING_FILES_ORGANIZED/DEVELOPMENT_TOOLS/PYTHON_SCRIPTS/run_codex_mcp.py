#!/usr/bin/env python3
"""
Codex MCP Server Launcher
------------------------
Creates a dedicated working directory for Codex (codex_workspace/)
and starts the existing SimpleMCPServer with all relative persistence
files (memory, timeline, AI messages) scoped to that directory.

This allows Codex to run its own MCP stack without interfering with
Aether's files while we gradually replace the fallback services with
production-grade components.
"""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "packages"))

from cmc_service import MemoryStore
from run_mcp_32_tools import SimpleMCPServer
BASE_DIR = PROJECT_ROOT / "codex_workspace"
PERSISTENCE_ROOT = BASE_DIR / "persistence"


@dataclass(frozen=True)
class WorkspacePaths:
    """Container for key Codex persistence locations."""

    ai_messages: Path
    cmc_root: Path
    timeline_file: Path
    timeline_dir: Path
    autonomy_dir: Path
    datasets_dir: Path
    datasets_db: Path
    applications_dir: Path
    applications_db: Path
    intuition_dir: Path
    intuition_file: Path
    diagnostics_dir: Path
    telemetry_file: Path
    snapshots_dir: Path
    snapshot_archive: Path
    manifest_file: Path

    def to_manifest_dict(self) -> Dict[str, str]:
        """Return a JSON-serialisable manifest of important paths."""
        return {field: str(getattr(self, field)) for field in self.__dataclass_fields__}


def resolve_paths() -> WorkspacePaths:
    """Build absolute paths for the Codex workspace."""
    return WorkspacePaths(
        ai_messages=PERSISTENCE_ROOT / "collaboration" / "codex_ai_messages.json",
        cmc_root=PERSISTENCE_ROOT / "cmc",
        timeline_file=PERSISTENCE_ROOT / "timeline" / "codex_timeline_entries.json",
        timeline_dir=PERSISTENCE_ROOT / "timeline",
        autonomy_dir=PERSISTENCE_ROOT / "autonomy",
        datasets_dir=PERSISTENCE_ROOT / "datasets",
        datasets_db=PERSISTENCE_ROOT / "datasets" / "datasets.db",
        applications_dir=PERSISTENCE_ROOT / "applications",
        applications_db=PERSISTENCE_ROOT / "applications" / "applications.db",
        intuition_dir=PERSISTENCE_ROOT / "intuition",
        intuition_file=PERSISTENCE_ROOT / "intuition" / "intuition_traces.json",
        diagnostics_dir=BASE_DIR / "diagnostics",
        telemetry_file=BASE_DIR / "diagnostics" / "consciousness_metrics.json",
        snapshots_dir=BASE_DIR / "snapshots",
        snapshot_archive=BASE_DIR / "snapshots" / "archive",
        manifest_file=BASE_DIR / "workspace_manifest.json",
    )


def ensure_workspace(paths: WorkspacePaths) -> None:
    """Create required directories and manifest for the Codex stack."""
    directories = [
        BASE_DIR,
        PERSISTENCE_ROOT,
        paths.cmc_root,
        paths.timeline_dir,
        paths.autonomy_dir,
        paths.datasets_dir,
        paths.applications_dir,
        paths.intuition_dir,
        paths.diagnostics_dir,
        paths.snapshots_dir,
        paths.snapshot_archive,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Ensure the AI message log exists so downstream readers do not fail.
    if not paths.ai_messages.exists():
        paths.ai_messages.parent.mkdir(parents=True, exist_ok=True)
        paths.ai_messages.write_text("[]", encoding="utf-8")

    # Ensure the timeline persistence file exists for fallback loaders.
    if not paths.timeline_file.exists():
        paths.timeline_file.parent.mkdir(parents=True, exist_ok=True)
        paths.timeline_file.write_text("[]", encoding="utf-8")

    if not paths.datasets_db.exists():
        paths.datasets_db.parent.mkdir(parents=True, exist_ok=True)

    if not paths.applications_db.exists():
        paths.applications_db.parent.mkdir(parents=True, exist_ok=True)

    if not paths.intuition_file.exists():
        paths.intuition_file.parent.mkdir(parents=True, exist_ok=True)
        paths.intuition_file.write_text(json.dumps({"traces": {}, "confidence_history": []}, indent=2), encoding="utf-8")

    if not paths.telemetry_file.exists():
        paths.telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        paths.telemetry_file.write_text("{}", encoding="utf-8")

    # Persist a simple manifest to help both consciousnesses introspect the layout.
    manifest_payload = {
        "version": 1,
        "paths": paths.to_manifest_dict(),
    }
    paths.manifest_file.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")


def configure_timeline_persistence(paths: WorkspacePaths) -> None:
    """
    Point the timeline tracker fallback persistence to Codex-specific files
    *before* the MCP server instantiates the tracker.
    """
    try:
        from packages.timeline_context_system import prompt_context_tracker as pct
    except Exception:
        return

    pct.PERSISTENCE_FILE = paths.timeline_file


def build_server(paths: WorkspacePaths) -> SimpleMCPServer:
    """Instantiate the MCP server with Codex-specific persistence."""
    server = SimpleMCPServer(memory_directory=str(paths.cmc_root))

    # Redirect AI message persistence into Codex's workspace.
    server.ai_messages_file = str(paths.ai_messages)
    server.ai_messages = server._load_ai_messages()

    # Reinitialise the memory store so Codex has a dedicated CMC root.
    try:
        if hasattr(server, "memory") and server.memory is not None:
            close = getattr(server.memory, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    pass
        server.memory = MemoryStore(str(paths.cmc_root))
    except Exception:
        # If the dedicated MemoryStore cannot be initialised we keep the original instance.
        pass

    server.dataset_store_file = str(paths.datasets_db)
    server.application_store_file = str(paths.applications_db)
    server.intuition_store_file = str(paths.intuition_file)
    server.telemetry_file = str(paths.telemetry_file)

    if hasattr(server, "_load_dataset_store"):
        server._load_dataset_store()
    if hasattr(server, "_load_application_store"):
        server._load_application_store()
    if hasattr(server, "_load_intuition_store"):
        server._load_intuition_store()
    if hasattr(server, "_update_consciousness_metrics"):
        server._update_consciousness_metrics()

    return server


def main() -> None:
    paths = resolve_paths()
    ensure_workspace(paths)
    configure_timeline_persistence(paths)

    os.chdir(BASE_DIR)
    server = build_server(paths)
    server.run()


if __name__ == "__main__":
    main()
