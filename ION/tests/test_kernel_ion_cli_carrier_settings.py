from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from kernel import ion_cli_carrier_settings as settings
from kernel.ion_cli_model_selection import resolve_execution_selection
from kernel.ion_prompt_spawn_carrier_routing import resolve_carrier_for_domain

_SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def ion_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion_carrier_settings_repo"
    (root / "ION/03_registry").mkdir(parents=True)
    (root / "ION/05_context/current/domain_weaver").mkdir(parents=True)
    (root / "ION/05_context/current/cursor_connector/prompt_spawn_runs").mkdir(parents=True)
    (root / "ION/05_context/current/claude_connector/claude_prompt_spawn_runs").mkdir(
        parents=True
    )
    (root / "pyproject.toml").write_text("[project]\nname='carrier-settings-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# test\n", encoding="utf-8")
    for relative in (
        Path("ION/05_context/current/domain_weaver/DOMAIN_LEADER_CARRIER_ROUTING.candidate.yaml"),
        Path("ION/05_context/current/domain_weaver/DOMAIN_LEADER_CARRIER_ROUTING.candidate.json"),
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_SOURCE_REPO_ROOT / relative, target)
    return root


def _write_settings(root: Path, carriers: dict) -> None:
    payload = settings.default_settings_payload()
    payload["carriers"] = carriers
    path = root / settings.SETTINGS_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_disabled_carrier_skipped_with_fallback(ion_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_settings(
        ion_root,
        {
            "cursor_cli": {
                "enabled": False,
                "daily_run_limit": 100,
                "operation_mode": "full",
                "notes": "",
            },
            "claude_cli": settings._default_carrier_row(),
            "codex_cli": settings._default_carrier_row(),
        },
    )

    def fake_probe(shell_root: Path, carrier_id: str, *, routing=None):
        if carrier_id == "claude_cli":
            return True, "ok"
        return False, "skipped"

    monkeypatch.setattr(
        "kernel.ion_cli_model_selection.probe_carrier_available",
        fake_probe,
    )
    selection = resolve_execution_selection(
        ion_root,
        domain_id="domain.cli_carrier_selection_and_usage_fallback",
        carrier="cursor_cli",
        work_class="code_implementation",
        execution_surface="prompt_spawn",
    )
    assert selection.get("carrier_id") == "claude_cli"
    blocked, finding = settings.carrier_settings_gate(ion_root, "cursor_cli")
    assert blocked is True
    assert finding == "carrier_settings_disabled"


def test_daily_limit_triggers_fallback(ion_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runs = ion_root / "ION/05_context/current/cursor_connector/prompt_spawn_runs"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "prompt_spawn_2026-08-08T120000+0000_test").mkdir()
    _write_settings(
        ion_root,
        {
            "cursor_cli": {
                "enabled": True,
                "daily_run_limit": 1,
                "operation_mode": "full",
                "notes": "",
            },
            "claude_cli": settings._default_carrier_row(),
            "codex_cli": settings._default_carrier_row(),
        },
    )

    def fake_probe(shell_root: Path, carrier_id: str, *, routing=None):
        blocked, finding = settings.carrier_settings_gate(shell_root, carrier_id)
        if blocked:
            return False, str(finding)
        if carrier_id == "claude_cli":
            return True, "ok"
        return False, "probe_failed"

    monkeypatch.setattr(
        "kernel.ion_cli_model_selection.probe_carrier_available",
        fake_probe,
    )
    selection = resolve_execution_selection(
        ion_root,
        domain_id="domain.cli_carrier_selection_and_usage_fallback",
        carrier="cursor_cli",
        work_class="code_implementation",
        execution_surface="prompt_spawn",
    )
    assert selection.get("carrier_id") == "claude_cli"


def test_all_disabled_leaves_pause_finding(ion_root: Path) -> None:
    _write_settings(
        ion_root,
        {
            "cursor_cli": {**settings._default_carrier_row(), "enabled": False},
            "claude_cli": {**settings._default_carrier_row(), "enabled": False},
            "codex_cli": {**settings._default_carrier_row(), "enabled": False},
        },
    )
    resolution = resolve_carrier_for_domain(
        ion_root,
        domain_id="domain.cli_carrier_selection_and_usage_fallback",
        carrier="auto",
        work_class="code_implementation",
    )
    assert resolution.get("carrier_settings_pause") is True
    assert (
        resolution.get("carrier_settings_finding")
        == "all_carriers_disabled_by_operator_settings"
    )


def test_write_setting_atomic_and_receipted(ion_root: Path) -> None:
    settings.ensure_default_settings_file(ion_root)
    result = settings.write_setting(
        ion_root,
        carrier_id="cursor_cli",
        field="daily_run_limit",
        value=42,
    )
    assert result["ok"] is True
    receipt_rel = result.get("receipt_path")
    assert receipt_rel
    receipt_path = ion_root / receipt_rel
    assert receipt_path.is_file()
    on_disk = json.loads((ion_root / settings.SETTINGS_RELATIVE).read_text(encoding="utf-8"))
    assert on_disk["carriers"]["cursor_cli"]["daily_run_limit"] == 42
    tmp_glob = list((ion_root / settings.SETTINGS_RELATIVE.parent).glob(".*.tmp"))
    assert not tmp_glob


def test_absence_detector_stale_counters(ion_root: Path) -> None:
    payload = settings.default_settings_payload()
    payload["usage_counters_refreshed_at"] = "2020-01-01T00:00:00+00:00"
    path = ion_root / settings.SETTINGS_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    check = settings.probe_carrier_settings_absence(ion_root, write=True)
    assert check["status"] == "finding"
    finding_path = (
        ion_root / settings.FINDINGS_RELATIVE / settings.FINDING_STALE_COUNTERS
    )
    assert finding_path.is_file()
