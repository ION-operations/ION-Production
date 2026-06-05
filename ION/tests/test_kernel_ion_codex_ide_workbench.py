import json
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import urllib.request

from kernel.ion_codex_ide_workbench import build_codex_ide_workbench_model
from kernel.ion_dual_codex_chat import record_chat_turn
from kernel.ion_local_cockpit_app import make_handler


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-ide-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


def test_codex_ide_model_reports_no_context_binding_truthfully(tmp_path: Path):
    _seed_root(tmp_path)

    model = build_codex_ide_workbench_model(tmp_path)
    ide = model["codex_ide_workbench"]
    registry = ide["context_registry"]

    assert model["surface"] == "ide"
    assert ide["schema_id"] == "ion.codex_ide_workbench_model.v0_1"
    assert registry["schema_id"] == "ion.codex_ide_context_registry.v0_1"
    assert registry["status"] == "no_active_binding"
    assert registry["bridge_status"] == "none_mounted"
    assert registry["binding_count"] == 0
    assert registry["binding_ids_unique"] is True
    assert registry["warning_count"] >= 1
    assert registry["authority"]["production_authority"] is False
    assert registry["authority"]["live_execution_authority"] is False
    assert registry["authority"]["accepted_state_authority"] is False
    assert registry["authority"]["secrets_authority"] is False


def test_codex_ide_model_projects_chat_binding_and_latest_bridge(tmp_path: Path):
    _seed_root(tmp_path)
    result = record_chat_turn(
        tmp_path,
        lane_id="codex_general",
        message="Use the IDE bridge.",
        ide_context_bridge={
            "source": "codex_ide_workbench",
            "active_view": "diffs",
            "active_drawer": "context",
            "bottom_panel": "problems",
            "selected_path": "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx",
            "selected_tab": {
                "id": "source:CodexIdeWorkbenchPanel.tsx",
                "label": "CodexIdeWorkbenchPanel.tsx",
                "path": "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx",
                "kind": "source",
                "status": "open",
            },
            "open_tabs": [
                {
                    "id": "source:CodexIdeWorkbenchPanel.tsx",
                    "label": "CodexIdeWorkbenchPanel.tsx",
                    "path": "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx",
                    "kind": "source",
                    "status": "open",
                }
            ],
            "context_systems": [
                {
                    "id": "context-system:codex-solo",
                    "title": "Codex Solo",
                    "path": "ION/05_context/current/codex_solo/CAPSULE.md",
                    "status": "witness",
                    "kind": "capsule_floor",
                }
            ],
        },
    )

    model = build_codex_ide_workbench_model(tmp_path)
    ide = model["codex_ide_workbench"]
    registry = ide["context_registry"]
    session = ide["workspace_session"]

    assert result["ok"] is True
    assert registry["status"] == "active_binding_mounted"
    assert registry["bridge_status"] == "mounted"
    assert registry["binding_count"] == 1
    assert registry["binding_ids_unique"] is True
    assert registry["latest_bridge"]["artifact_ref"] == result["turn"]["ide_context_bridge"]["artifact_ref"]
    assert registry["latest_bridge_artifact_present"] is True
    assert session["active_chat_context_binding_id"] == registry["active_binding_id"]
    assert session["selected_path"] == "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx"
    assert session["open_tabs"][0]["path"] == "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx"
    assert any(row["context_kind"] == "chat_context_binding" for row in registry["context_systems"])
    assert any(row["context_kind"] == "ide_bridge_context_ref" for row in registry["context_systems"])
    assert registry["authority"]["production_authority"] is False
    assert registry["authority"]["live_execution_authority"] is False


def test_local_cockpit_serves_first_class_ide_model(tmp_path: Path):
    _seed_root(tmp_path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/cockpit/ide/model.json", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()

    assert payload["surface"] == "ide"
    assert payload["codex_ide_workbench"]["schema_id"] == "ion.codex_ide_workbench_model.v0_1"
    assert payload["codex_ide_workbench"]["context_registry"]["bridge_status"] == "none_mounted"
    assert payload["codex_ide_workbench"]["authority"]["production_authority"] is False
