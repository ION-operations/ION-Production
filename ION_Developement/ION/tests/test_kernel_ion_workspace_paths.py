from pathlib import Path

from kernel.ion_workspace_paths import classify_ion_path, resolve_ion_path


def test_resolve_promoted_custom_gpt_action_openapi(tmp_path):
    repo = tmp_path / "ION_Developement"
    promoted = tmp_path / "ION_GPT" / "custom_gpt_action_gateway"
    promoted.mkdir(parents=True)
    (repo / "ION" / "REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (repo / "ION" / "REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='ion'\n", encoding="utf-8")
    (promoted / "openapi.yaml").write_text("openapi: 3.1.0\n", encoding="utf-8")

    resolved = resolve_ion_path(repo, "ION/09_integrations/custom_gpt_action_gateway/openapi.yaml")

    assert resolved == promoted / "openapi.yaml"


def test_classify_promoted_path_reports_workspace_resolution(tmp_path):
    repo = tmp_path / "ION_Developement"
    promoted = tmp_path / "systemd" / "user"
    promoted.mkdir(parents=True)
    (promoted / "ion-action-gateway.service.template").write_text("[Service]\n", encoding="utf-8")

    result = classify_ion_path(repo, "ION/09_integrations/systemd/user/ion-action-gateway.service.template")

    assert result["exists"] is True
    assert result["promoted_workspace_path"] is True
    assert result["resolved_path"] == "../systemd/user/ion-action-gateway.service.template"
