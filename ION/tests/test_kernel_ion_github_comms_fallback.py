import json
import subprocess
from pathlib import Path

from kernel.ion_github_comms_fallback import (
    BLOCKED_VERDICT,
    READY_VERDICT,
    build_github_comms_fallback,
    scan_github_comms_text_for_secrets,
)


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text('[project]\nname = "ion-github-comms-fallback-test"\n', encoding="utf-8")
    for rel in [
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_GITHUB_DATA_PLANE_PROTOCOL.md",
        "ION/02_architecture/ION_GITHUB_WORK_DAEMON_PROTOCOL.md",
        "ION/03_registry/ion_github_data_plane_registry.yaml",
        "ION/05_context/current/github_data_plane/PRIOR_ART_CONSOLIDATION_2026-05-04.md",
    ]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{rel}\n", encoding="utf-8")
    (root / "ION/03_registry/ion_github_data_plane_registry.yaml").write_text(
        "active_branch: work/github-comms-fallback\n"
        "active_remote: https://github.com/ION-operations/ION.git\n"
        "first_commit_pushed: false\n"
        "setup_state: test\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "checkout", "-b", "work/github-comms-fallback"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/ION-operations/ION.git"], cwd=root, check=True)


def test_github_comms_fallback_writes_issue_artifacts(tmp_path):
    _seed_root(tmp_path)

    result = build_github_comms_fallback(
        tmp_path,
        packet_id="PCKT-SEV-001-GITHUB-COMMS-FALLBACK",
        objective="Create an auditable fallback lane when MCP is unavailable.",
        message="MCP direct call is unavailable in this carrier. Please use this GitHub issue draft as the handoff envelope.",
        channel="issue",
        evidence_refs=["ION/04_packages/kernel/ion_mcp_local_bridge.py"],
        write=True,
    )

    assert result["verdict"] == READY_VERDICT
    assert result["network_access_used"] is False
    assert result["github_mutation_performed"] is False
    assert result["git_mutation_performed"] is False
    assert result["accepted_state_claimed"] is False
    paths = result["artifact_paths"]
    for rel in paths.values():
        assert (tmp_path / rel).exists(), rel
    command_plan = json.loads((tmp_path / paths["github_command_plan"]).read_text(encoding="utf-8"))
    assert command_plan["commands"][0]["argv"][:3] == ["gh", "issue", "create"]
    body = (tmp_path / paths["markdown"]).read_text(encoding="utf-8")
    assert "Candidate carrier communication artifact" in body
    assert "does not run `gh`" in body


def test_github_comms_fallback_artifact_only_has_no_gh_command(tmp_path):
    _seed_root(tmp_path)

    result = build_github_comms_fallback(
        tmp_path,
        objective="Share a Drive-synced fallback artifact without GitHub publication.",
        message="Use the synced artifact bundle as evidence until GitHub publication is approved.",
        channel="artifact_only",
        write=True,
    )

    assert result["verdict"] == READY_VERDICT
    command_plan = json.loads((tmp_path / result["artifact_paths"]["github_command_plan"]).read_text(encoding="utf-8"))
    assert command_plan["commands"] == []
    assert command_plan["manual_fallbacks"]


def test_github_comms_comment_requires_issue_number(tmp_path):
    _seed_root(tmp_path)

    result = build_github_comms_fallback(
        tmp_path,
        objective="Comment on the current fallback thread.",
        message="Attach current status to the existing thread.",
        channel="comment",
        write=True,
    )

    assert result["verdict"] == BLOCKED_VERDICT
    assert "comment_channel_requires_issue_number" in result["findings"]
    assert result["write"]["performed"] is False


def test_github_comms_secret_scan_blocks_token_text(tmp_path):
    _seed_root(tmp_path)
    secret_message = "Do not publish this: GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwx"

    result = build_github_comms_fallback(
        tmp_path,
        objective="Publish a fallback status without secrets.",
        message=secret_message,
        channel="issue",
        write=True,
    )

    assert result["verdict"] == BLOCKED_VERDICT
    assert result["message"] == "<withheld_due_to_blocking_findings>"
    assert "secret_scan_block" in result["findings"]
    assert result["secret_scan"]["secret_values_redacted"] is True
    assert result["write"]["performed"] is False


def test_secret_scan_ignores_explicit_placeholders():
    result = scan_github_comms_text_for_secrets("GITHUB_TOKEN=<redacted>", "OPENAI_API_KEY=your_key_here")

    assert result["accepted"] is True
    assert result["findings"] == []


def test_github_comms_status_projection_is_non_authorizing(tmp_path):
    _seed_root(tmp_path)
    from kernel.ion_github_comms_fallback import build_github_comms_fallback_status

    status = build_github_comms_fallback_status(tmp_path, mcp_observation="mcp_not_exposed")

    assert status["mode"] == "LOCAL_DRAFT_ONLY_NO_GITHUB_MUTATION"
    assert status["ok"] is True
    assert status["network_access_used"] is False
    assert status["github_mutation_performed"] is False
    assert status["accepted_state_authority"] is False


def test_github_comms_draft_projection_is_copy_block_only(tmp_path):
    _seed_root(tmp_path)
    from kernel.ion_github_comms_fallback import build_github_comms_fallback_draft

    result = build_github_comms_fallback_draft(
        tmp_path,
        summary="MCP fallback handoff",
        message="MCP is not exposed to this carrier; use GitHub copy block.",
        target="issue",
        related_ref="PCKT-SEV-001-GITHUB-COMMS-FALLBACK",
        source_carrier="unit_test",
        write=False,
    )

    assert result["ok"] is True
    assert result["write"]["performed"] is False
    assert result["network_access_used"] is False
    assert result["github_mutation_performed"] is False
    assert result["copy_blocks"]["github_issue_title"].startswith("ION carrier fallback")
    assert "Candidate carrier communication artifact" in result["copy_blocks"]["github_issue_body"]
