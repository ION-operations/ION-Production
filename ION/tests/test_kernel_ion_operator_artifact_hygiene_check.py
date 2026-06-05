from pathlib import Path
import zipfile

from kernel.ion_operator_artifact_hygiene_check import (
    check_general_operator_artifact,
    check_gpt_upload_kit,
)


def _write(path: Path, text: str = "content") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _valid_readme() -> str:
    return "\n".join(
        [
            "# Do This Only",
            "1. Paste the instructions file.",
            "2. Upload every file inside 02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE.",
            "3. Upload nothing else.",
            "4. Run the smoke prompt after save.",
        ]
    )


def _build_valid_gpt_kit(root: Path, count: int = 20) -> None:
    _write(root / "00_READ_ME_FIRST_DO_THIS_ONLY.md", _valid_readme())
    _write(root / "01_PASTE_THIS_IN_GPT_BUILDER_INSTRUCTIONS.md", "instructions")
    knowledge = root / "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE"
    _write(knowledge / "00_ROOT_MANIFEST.json", "{}")
    for index in range(1, count):
        suffix = ".zip" if index >= 10 else ".md"
        path = knowledge / f"{index:02d}_FILE{suffix}"
        if suffix == ".zip":
            path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("START_HERE.md", "content")
        else:
            _write(path, "content")


def test_gpt_upload_kit_accepts_exact_collapsed_shape(tmp_path):
    root = tmp_path / "ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_20260516T000000Z"
    _build_valid_gpt_kit(root)

    report = check_gpt_upload_kit(root)

    assert report.passed is True
    assert report.root_entries == [
        "00_READ_ME_FIRST_DO_THIS_ONLY.md",
        "01_PASTE_THIS_IN_GPT_BUILDER_INSTRUCTIONS.md",
        "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE",
    ]
    assert report.knowledge_file_count == 20


def test_gpt_upload_kit_rejects_mixed_upload_workspace(tmp_path):
    root = tmp_path / "ION_GPT_UPLOAD_SET_chaos"
    _write(root / "FILES_TO_UPLOAD_TO_FRESH_GPT" / "README.md", "primary")
    _write(root / "UPLOAD_THESE_MARKDOWN" / "01.md", "old")
    _write(root / "UPLOAD_THESE_ZIPS" / "context.zip", "old")
    _write(root / "VALIDATION_LOGS" / "check.txt", "log")
    _write(root / "ION_CODEX_TASK_RETURN.md", "task return")

    report = check_gpt_upload_kit(root)
    codes = {issue.code for issue in report.issues}

    assert report.passed is False
    assert "gpt_kit_root_entries_not_exact" in codes
    assert "mixed_upload_folder_names_same_level" in codes
    assert "reference_material_in_operator_root" in codes
    assert "loose_reference_file_in_operator_root" in codes


def test_gpt_upload_kit_rejects_visible_fallback_beside_primary(tmp_path):
    root = tmp_path / "ION_GPT_UPLOAD_SET_chaos"
    _write(root / "FILES_TO_UPLOAD_TO_FRESH_GPT" / "README.md", "primary")
    _write(root / "FILES_TO_UPLOAD_TO_FRESH_GPT_10_FILE_FALLBACK" / "README.md", "fallback")

    report = check_gpt_upload_kit(root)

    assert report.passed is False
    assert "fallback_visible_beside_primary" in {issue.code for issue in report.issues}


def test_gpt_upload_kit_rejects_forbidden_paths(tmp_path):
    root = tmp_path / "ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_20260516T000000Z"
    _build_valid_gpt_kit(root)
    _write(root / "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE" / "ION_VAULT_LOCAL" / "placeholder.txt")

    report = check_gpt_upload_kit(root)

    assert report.passed is False
    assert "forbidden_path" in {issue.code for issue in report.issues}


def test_general_operator_artifact_requires_one_outcome_folder(tmp_path):
    root = tmp_path / "result"
    (root / "OPERATOR_FINAL").mkdir(parents=True)

    assert check_general_operator_artifact(root).passed is True

    (root / "INTERNAL_REFERENCE_DO_NOT_TOUCH").mkdir()
    report = check_general_operator_artifact(root)

    assert report.passed is False
    assert "general_outcome_root_not_single" in {issue.code for issue in report.issues}
