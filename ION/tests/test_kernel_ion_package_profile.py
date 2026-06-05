import json
from pathlib import Path

from kernel.ion_package_profile import evaluate_package_profile


def seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname='package-profile-test'\n", encoding="utf-8")
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)


def test_single_carrier_sandbox_treats_sibling_roots_as_optional(tmp_path):
    seed_root(tmp_path)

    result = evaluate_package_profile(tmp_path)

    assert result["status"] == "PACKAGE_PROFILE_READY"
    assert result["profile_id"] == "single_carrier_sandbox"
    assert result["status_ceiling"] == "LOCAL_SANDBOX_READY_ONLY"
    assert result["ready_verdict"] == "ION_STATUS_SINGLE_CARRIER_READY"
    assert result["full_readiness_proven"] is False
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    assert result["accepted_state_authority"] is False
    assert result["missing_required_paths"] == []
    assert result["optional_sibling_roots"]
    assert all(item["required"] is False for item in result["optional_sibling_roots"])
    assert any(item["path"] == "../mcp" and item["present"] is False for item in result["optional_sibling_roots"])
    assert any(item["path"] == "../browser_extension" and item["present"] is False for item in result["optional_sibling_roots"])


def test_missing_package_profile_blocks_readiness(tmp_path):
    seed_root(tmp_path)
    declaration = tmp_path / "ION/05_context/current/ION_PACKAGE_PROFILE.json"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    declaration.write_text(json.dumps({"profile_id": "missing_profile"}), encoding="utf-8")

    result = evaluate_package_profile(tmp_path)

    assert result["status"] == "PACKAGE_PROFILE_BLOCKED"
    assert result["accepted"] is False
    assert result["blockers"][0]["category"] == "profile_missing"
    assert result["production_authority"] is False
