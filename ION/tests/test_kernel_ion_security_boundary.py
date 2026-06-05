import json
from pathlib import Path

from kernel.ion_security_boundary import scan_security_boundary


def seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname='security-boundary-test'\n", encoding="utf-8")
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)


def test_security_boundary_detects_dotenv_without_emitting_secret_values(tmp_path):
    seed_root(tmp_path)
    secret_value = "dummy-value-that-must-not-appear"
    (tmp_path / ".env.supabase.local").write_text(f"SUPABASE_SERVICE_ROLE_KEY={secret_value}\n", encoding="utf-8")

    result = scan_security_boundary(tmp_path)
    rendered = json.dumps(result, sort_keys=True)

    assert result["status"] == "SECURITY_BLOCKED"
    assert result["accepted"] is False
    assert result["blocker_count"] == 1
    assert result["findings"][0]["path"] == ".env.supabase.local"
    assert result["findings"][0]["rule_id"] == "DOTENV_SECRET_FILE"
    assert result["findings"][0]["secret_values_emitted"] is False
    assert secret_value not in rendered


def test_security_boundary_allows_template_env_variable_names_only(tmp_path):
    seed_root(tmp_path)
    template_value = "replace-me"
    (tmp_path / ".env.supabase.local.example").write_text(f"SUPABASE_URL={template_value}\n", encoding="utf-8")

    result = scan_security_boundary(tmp_path)
    rendered = json.dumps(result, sort_keys=True)

    assert result["status"] == "SECURITY_BOUNDARY_READY"
    assert result["accepted"] is True
    assert result["findings"][0]["category"] == "dotenv_template"
    assert result["findings"][0]["safe_variable_names"] == ["SUPABASE_URL"]
    assert template_value not in rendered


def test_security_boundary_does_not_block_worker_shift_receipt_named_for_secret_containment(tmp_path):
    seed_root(tmp_path)
    receipt = tmp_path / "ION/05_context/current/worker_shift/leases/lease_secret_containment_claim.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({"receipt_type": "lease_claim", "secret_values_emitted": False}), encoding="utf-8")

    result = scan_security_boundary(tmp_path)

    assert result["status"] == "SECURITY_BOUNDARY_READY"
    assert result["blocker_count"] == 0
