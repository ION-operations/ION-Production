import json
from pathlib import Path

import yaml

from kernel.ion_gdrive_context_mirror import build_gdrive_context_mirror, resolve_drive_output_path


def _seed_repo(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    files = {
        "ION/REPO_AUTHORITY.md": "# authority\n",
        "ION/02_architecture/TEST_PROTOCOL.md": "# protocol\n",
        "ION/03_registry/test_registry.yaml": "schema_id: test\n",
        "ION/docs/guide.md": "# guide\n",
        "ION/07_templates/test_template.md": "# template\n",
        "ION/05_context/current/codex_solo/CAPSULE.md": "# capsule\n",
        "ION/05_context/current/codex_solo/MINI.md": "# mini\n",
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md": "# hot\n",
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json": "{}\n",
        "ION/05_context/current/codex_solo/ROUTE.json": "{}\n",
        "workpackets/README.md": "# workpackets\n",
        "workpackets/WORKPACKET_INDEX_20260508T190626Z.json": json.dumps(
            {"schema_id": "ion.root_source_lane.workpacket_index.v1", "files": [], "file_count": 0}
        ),
        "diffs/README.md": "# diffs\n",
        "diffs/DIFF_INDEX_20260508T190626Z.json": json.dumps(
            {"schema_id": "ion.root_source_lane.diff_index.v1", "files": [], "file_count": 0}
        ),
        "ION/07_templates/gdrive_context_mirror/START_HERE_FOR_GPT.md": "# start\n",
        "ION/07_templates/gdrive_context_mirror/GPT_REPO_MOUNT_POLICY.md": "# policy\n",
    }
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (root / ".venv").mkdir()
    (root / ".venv/ignored.py").write_text("ignored\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules/ignored.js").write_text("ignored\n", encoding="utf-8")
    (root / "ION/02_architecture/__pycache__").mkdir()
    (root / "ION/02_architecture/__pycache__/ignored.pyc").write_bytes(b"bad")
    (root / "ION/docs/raw.log").write_text("log\n", encoding="utf-8")


def test_build_gdrive_context_mirror_writes_manifest_and_latest(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    output = tmp_path / "mirror"

    result = build_gdrive_context_mirror(repo, output=output, emitted_at="2026-05-12T00:00:00Z")

    assert result["ok"] is True
    latest = json.loads((output / "LATEST.json").read_text(encoding="utf-8"))
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    sha_sums = json.loads(Path(result["sha256sums_path"]).read_text(encoding="utf-8"))
    assert latest["accepted_state_claim"] is False
    assert manifest["google_drive_is_active_repo"] is False
    assert manifest["intended_drive_account"] == "crinkedart@gmail.com"
    assert manifest["intended_drive_folder_uri"] == "google-drive://crinkedart@gmail.com/0ABqIU0r0h-u2Uk9PVA"
    assert sha_sums
    assert (Path(result["export_path"]) / "00_START_HERE/START_HERE_FOR_GPT.md").exists()
    assert (Path(result["export_path"]) / "01_LATEST_CONTEXT/CURRENT_CONTEXT_SUMMARY.md").exists()


def test_gdrive_context_mirror_excludes_secret_cache_and_logs(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    output = tmp_path / "mirror"

    result = build_gdrive_context_mirror(repo, output=output, emitted_at="2026-05-12T00:00:00Z")
    export_path = Path(result["export_path"])

    exported_paths = {path.relative_to(export_path).as_posix() for path in export_path.rglob("*") if path.is_file()}
    assert not any(".env" in path for path in exported_paths)
    assert not any(".venv" in path for path in exported_paths)
    assert not any("node_modules" in path for path in exported_paths)
    assert not any("__pycache__" in path for path in exported_paths)
    assert not any(path.endswith(".log") for path in exported_paths)


def test_gdrive_context_mirror_preserves_source_posture(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    output = tmp_path / "mirror"

    result = build_gdrive_context_mirror(repo, output=output, emitted_at="2026-05-12T00:00:00Z")
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    postures = {entry["source_posture"] for entry in manifest["files"] if entry.get("included")}

    assert "runtime_evidence" in postures
    assert "stale_index" in postures
    assert all(entry["accepted_state_claim"] is False for entry in manifest["files"])


def test_gdrive_context_mirror_can_copy_to_supplied_drive_output(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    output = tmp_path / "mirror"
    drive = tmp_path / "drive" / "ION_CONTEXT"

    result = build_gdrive_context_mirror(
        repo,
        output=output,
        drive_output=drive,
        emitted_at="2026-05-12T00:00:00Z",
    )

    assert result["drive_result"]["copied"] is True
    assert (drive / "LATEST.json").exists()
    assert (drive / "exports" / Path(result["export_path"]).name / "EXPORT_MANIFEST.json").exists()


def test_gdrive_registry_yaml_shape():
    registry_path = Path("ION/03_registry/ion_gdrive_context_mirror_registry.yaml")
    payload = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    assert payload["default_output"] == "/home/sev/ION - Production/ION_GDRIVE_CONTEXT_MIRROR"
    assert payload["intended_drive_account"] == "crinkedart@gmail.com"
    assert payload["intended_drive_folder_uri"] == "google-drive://crinkedart@gmail.com/0ABqIU0r0h-u2Uk9PVA"
    assert payload["authority"]["accepted_state_authority"] is False


def test_resolve_drive_output_path_accepts_normal_local_path(tmp_path: Path):
    target = tmp_path / "ION_CONTEXT"
    target.mkdir()

    assert resolve_drive_output_path(target) == target.resolve()
