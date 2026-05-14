from __future__ import annotations

import json
import zipfile
from pathlib import Path

from kernel.ion_custom_gpt_sandbox_package import build_package


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_custom_gpt_sandbox_package_uses_current_paths_and_redacts_workspace(tmp_path: Path) -> None:
    _write(tmp_path / "README.md", "# repo\n")
    _write(tmp_path / "AGENTS.md", "instructions\n")
    _write(
        tmp_path
        / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md",
        "carrier instructions\n",
    )
    _write(tmp_path / "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md", "builder instructions\n")
    _write(
        tmp_path / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml",
        "openapi: 3.1.0\n",
    )
    _write(tmp_path / "Needs_Routed/custom_gpt_mount/ion_boot_result.json", '{"ok": true}\n')

    result = build_package(tmp_path, tmp_path / "out")

    assert result["ok"] is True
    with zipfile.ZipFile(result["zip_path"]) as zf:
        start_here = zf.read("START_HERE_FOR_CUSTOM_GPT.md").decode("utf-8")
        manifest = json.loads(zf.read("PACKAGE_MANIFEST.json"))
        names = set(zf.namelist())

    assert "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md" in start_here
    assert "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml" in start_here
    assert "ION_GPT/custom_gpt_action_gateway/openapi.yaml" not in start_here
    assert manifest["workspace_root"] == "redacted_local_workspace_root"
    assert manifest["workspace_root_redacted"] is True
    assert manifest["accepted_state_claim"] is False
    assert manifest["production_authority"] is False
    assert manifest["live_execution_authority"] is False
    assert (
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml"
        in manifest["canonical_action_schema_reference"]
    )
    assert "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md" in names
