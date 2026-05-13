import subprocess
from pathlib import Path

from kernel.ion_codex_local_pc_readiness import (
    BLOCKED_VERDICT,
    PARTIAL_VERDICT,
    READY_VERDICT,
    audit_codex_local_pc_readiness,
    write_codex_local_pc_readiness,
)


def _run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _write_required_surfaces(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    for rel in [
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        "ION/docs/setup/ION_CURRENT_OPERATING_PACKET_V119.md",
        "ION/docs/setup/CODEX_CLI_ION_DOGFOOD_SETUP_V125.md",
        "ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md",
        "ION/02_architecture/CODEX_CARRIER_DOMAIN_PROTOCOL.md",
        "ION/04_packages/kernel/ion_codex_carrier_domain.py",
        "ION/04_packages/kernel/ion_codex_cli_carrier_audit.py",
        "ION/04_packages/kernel/ion_codex_solo_context.py",
        "ION/04_packages/kernel/ion_mcp_local_bridge.py",
        ".codex/config.toml",
        ".codex/hooks/ion_session_start_context.py",
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "ION/05_context/current/codex_solo/STATUS.json",
        "ION/05_context/current/codex_solo/ROUTE.json",
        "ION/02_architecture/ION_GITHUB_DATA_PLANE_PROTOCOL.md",
    ]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# surface\n", encoding="utf-8")


def _init_git(root: Path, branch: str = "work/test-codex-local-pc") -> None:
    _run_git(root, "init")
    _run_git(root, "checkout", "-b", branch)
    _run_git(root, "remote", "add", "origin", "https://github.com/ION-operations/ion-codex.git")


def test_codex_local_pc_readiness_blocks_without_codex(monkeypatch, tmp_path):
    _write_required_surfaces(tmp_path)
    _init_git(tmp_path)
    monkeypatch.setattr("kernel.ion_codex_local_pc_readiness.shutil.which", lambda name: None)

    result = audit_codex_local_pc_readiness(tmp_path)

    assert result["verdict"] == BLOCKED_VERDICT
    assert "codex_cli_not_found_on_path" in result["blockers"]
    assert result["capability_boundaries"]["github_mutation_performed"] is False
    assert result["capability_boundaries"]["hidden_codex_memory_read"] is False


def test_codex_local_pc_readiness_partial_when_codex_exists_but_services_off(monkeypatch, tmp_path):
    _write_required_surfaces(tmp_path)
    _init_git(tmp_path)

    def fake_which(name: str):
        return "/usr/bin/fake-codex" if name == "codex" else None

    def fake_run(command, *, cwd=None, timeout=8, max_output_chars=4000):
        if command[0] == "git":
            from kernel import ion_codex_local_pc_readiness as mod
            return mod.subprocess.run(
                list(command), cwd=cwd, check=False, capture_output=True, text=True, timeout=timeout
            ).__dict__  # unreachable shape guard; monkeypatched below by explicit branch
        return {"command": list(command), "available": True, "returncode": 0, "stdout": "codex 0.0.test\n", "stderr": ""}

    # Patch only command discovery and Codex subprocess execution; leave git real.
    monkeypatch.setattr("kernel.ion_codex_local_pc_readiness.shutil.which", fake_which)
    monkeypatch.setattr(
        "kernel.ion_codex_local_pc_readiness._codex_probe",
        lambda include_help=False: {
            "codex_on_path": True,
            "codex_path": "/usr/bin/fake-codex",
            "version": {"returncode": 0, "stdout": "codex 0.0.test\n"},
            "help_probe": None,
            "resume_help_probe": None,
            "feature_help_probes": {},
            "not_claimed": [],
        },
    )
    monkeypatch.setattr(
        "kernel.ion_codex_local_pc_readiness._probe_local_port",
        lambda port, host="127.0.0.1", timeout=0.25: {"host": host, "port": port, "listening": False, "error": "ConnectionRefusedError"},
    )

    result = audit_codex_local_pc_readiness(tmp_path)

    assert result["verdict"] == PARTIAL_VERDICT
    assert result["codex_cli"]["codex_on_path"] is True
    assert "ion_mcp_preview_not_listening_8765" in result["warnings"]
    assert result["capability_boundaries"]["network_access_used"] is False


def test_codex_local_pc_readiness_can_write_candidate_status(monkeypatch, tmp_path):
    _write_required_surfaces(tmp_path)
    _init_git(tmp_path)
    monkeypatch.setattr("kernel.ion_codex_local_pc_readiness.shutil.which", lambda name: None)

    out = tmp_path / "ION/05_context/current/codex_local_pc/CODEX_LOCAL_PC_READINESS.json"
    result = write_codex_local_pc_readiness(tmp_path)

    assert out.exists()
    assert result["verdict"] == BLOCKED_VERDICT


def test_codex_local_pc_readiness_current_tree_shape():
    result = audit_codex_local_pc_readiness(Path.cwd())

    assert result["schema_id"] == "ion.codex_local_pc_readiness.v1"
    assert result["verdict"] in {READY_VERDICT, PARTIAL_VERDICT, BLOCKED_VERDICT}
    assert result["core_surfaces"]["repo_authority"]["exists"] is True
    assert result["capability_boundaries"]["git_mutation_performed"] is False
