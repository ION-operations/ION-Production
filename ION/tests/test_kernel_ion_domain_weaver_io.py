from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path

from kernel import ion_domain_weaver_io as io_helpers


def test_stable_json_text_sorts_indents_and_appends_newline() -> None:
    payload = {"z": 1, "a": {"b": 2}}

    assert io_helpers._stable_json_text(payload) == json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_stable_json_sha256_matches_stable_text() -> None:
    payload = {"b": 2, "a": 1}
    expected = hashlib.sha256(io_helpers._stable_json_text(payload).encode("utf-8")).hexdigest()

    assert io_helpers._stable_json_sha256(payload) == expected


def test_write_stable_json_and_hash_writes_parent_and_returns_hash(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "payload.json"
    payload = {"b": 2, "a": 1}

    digest = io_helpers._write_stable_json_and_hash(target, payload)

    assert target.read_text(encoding="utf-8") == io_helpers._stable_json_text(payload)
    assert digest == hashlib.sha256(target.read_bytes()).hexdigest()


def test_resolve_root_finds_shell_root_from_child(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    child = root / "ION" / "04_packages"
    child.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    (root / "ION" / "REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")

    assert io_helpers._resolve_root(child) == root


def test_rel_returns_repo_relative_or_absolute_fallback(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    in_root = root / "ION" / "file.json"
    outside = tmp_path / "outside.json"

    assert io_helpers._rel(root, in_root) == "ION/file.json"
    assert io_helpers._rel(root, outside) == outside.as_posix()


def test_safe_rel_path_blocks_parent_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    assert io_helpers._safe_rel_path(root, "ION/file.json") == (root / "ION/file.json").resolve()
    try:
        io_helpers._safe_rel_path(root, "../outside.json")
    except ValueError as exc:
        assert "path escapes root" in str(exc)
    else:
        raise AssertionError("_safe_rel_path accepted a parent traversal escape")


def test_sha256_file_and_file_ref_existing_and_missing(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    target = root / "data" / "payload.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"payload")

    assert io_helpers._sha256_file(target) == hashlib.sha256(b"payload").hexdigest()
    existing = io_helpers._file_ref(root, Path("data/payload.json"), "test reason")
    missing = io_helpers._file_ref(root, Path("data/missing.json"), "missing reason", required=False)

    assert existing == {
        "path": "data/payload.json",
        "exists": True,
        "required": True,
        "reason": "test reason",
        "sha256": hashlib.sha256(b"payload").hexdigest(),
    }
    assert missing == {
        "path": "data/missing.json",
        "exists": False,
        "required": False,
        "reason": "missing reason",
    }


def test_read_json_file_returns_mapping_only(tmp_path: Path) -> None:
    object_path = tmp_path / "object.json"
    list_path = tmp_path / "list.json"
    invalid_path = tmp_path / "invalid.json"
    object_path.write_text('{"ok": true}', encoding="utf-8")
    list_path.write_text("[1, 2]", encoding="utf-8")
    invalid_path.write_text("{", encoding="utf-8")

    assert io_helpers._read_json_file(object_path) == {"ok": True}
    assert io_helpers._read_json_file(list_path) == {}
    assert io_helpers._read_json_file(invalid_path) == {}
    assert io_helpers._read_json_file(tmp_path / "missing.json") == {}


def test_latest_json_refs_orders_newest_and_hashes(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    data_dir = root / "refs"
    data_dir.mkdir(parents=True)
    older = data_dir / "older.json"
    newer = data_dir / "newer.json"
    ignored = data_dir / "ignored.txt"
    older.write_text('{"older": true}', encoding="utf-8")
    newer.write_text('{"newer": true}', encoding="utf-8")
    ignored.write_text("ignored", encoding="utf-8")
    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))

    refs = io_helpers._latest_json_refs(root, Path("refs"), reason="latest refs", limit=2)

    assert [ref["path"] for ref in refs] == ["refs/newer.json", "refs/older.json"]
    assert refs[0]["sha256"] == hashlib.sha256(newer.read_bytes()).hexdigest()
    assert refs[0]["reason"] == "latest refs"


def test_latest_queue_run_refs_uses_helper_constant_and_orders_runs(tmp_path: Path) -> None:
    sys.modules.pop("kernel.ion_domain_weaver", None)
    module = importlib.import_module("kernel.ion_domain_weaver_io")
    assert "kernel.ion_domain_weaver" not in sys.modules

    root = tmp_path / "repo"
    run_root = root / module.DEFAULT_CODEX_QUEUE_RUNS_DIR
    older = run_root / "codex_run_older" / "run.json"
    newer = run_root / "codex_run_newer" / "run.json"
    older.parent.mkdir(parents=True)
    newer.parent.mkdir(parents=True)
    older.write_text('{"run": "older"}', encoding="utf-8")
    newer.write_text('{"run": "newer"}', encoding="utf-8")
    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))

    refs = module._latest_queue_run_refs(root, limit=2)

    assert [ref["path"] for ref in refs] == [
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/codex_run_newer/run.json",
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/codex_run_older/run.json",
    ]
    assert refs[0]["sha256"] == hashlib.sha256(newer.read_bytes()).hexdigest()
    assert module._latest_queue_run_refs(tmp_path / "missing-root") == []


def test_task_return_body_path_prefers_reverse_touched_body_paths(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    first = root / "run" / "task_return_body.md"
    second = root / "run" / "latest_return.md"
    first.parent.mkdir(parents=True)
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")
    latest_return = {
        "template_action_proof_result": {
            "touched_paths": ["run/task_return_body.md", "run/latest_return.md"],
        }
    }

    assert io_helpers._task_return_body_path_from_return(root, latest_return, []) == "run/latest_return.md"


def test_task_return_body_path_uses_packet_fields_and_run_fallbacks(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    direct = root / "direct" / "task_return_body.md"
    direct.parent.mkdir(parents=True)
    direct.write_text("direct", encoding="utf-8")
    run_body = root / "runs" / "codex_run_x" / "task_return_body.md"
    run_json = run_body.parent / "run.json"
    run_body.parent.mkdir(parents=True)
    run_body.write_text("body", encoding="utf-8")
    run_json.write_text("{}", encoding="utf-8")

    assert io_helpers._task_return_body_path_from_return(root, {"task_return_body_path": "direct/task_return_body.md"}, []) == "direct/task_return_body.md"
    assert io_helpers._task_return_body_path_from_return(root, {}, [{"run_packet_path": "runs/codex_run_x/run.json"}]) == "runs/codex_run_x/task_return_body.md"


def test_context_receipt_path_prefers_touched_body_sibling_and_run_fallback(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    touched = {"template_action_proof_result": {"touched_paths": ["run/context_receipt.json"]}}
    body = root / "body-run" / "task_return_body.md"
    body_receipt = body.parent / "context_receipt.json"
    fallback_receipt = root / "fallback-run" / "context_receipt.json"
    fallback_run = fallback_receipt.parent / "run.json"
    body.parent.mkdir(parents=True)
    fallback_receipt.parent.mkdir(parents=True)
    body.write_text("body", encoding="utf-8")
    body_receipt.write_text("{}", encoding="utf-8")
    fallback_receipt.write_text("{}", encoding="utf-8")
    fallback_run.write_text("{}", encoding="utf-8")

    assert io_helpers._context_receipt_path_from_return(root, touched, "", []) == "run/context_receipt.json"
    assert io_helpers._context_receipt_path_from_return(root, {}, "body-run/task_return_body.md", []) == "body-run/context_receipt.json"
    assert io_helpers._context_receipt_path_from_return(root, {}, "", [{"run_packet_path": "fallback-run/run.json"}]) == "fallback-run/context_receipt.json"


def test_result_paths_collects_path_fields_and_lists() -> None:
    result = {
        "one_path": "one",
        "two_paths": ["two", "three"],
        "blank_path": "",
        "ignored": "no",
    }

    assert io_helpers._result_paths(result) == ["one", "two", "three"]


def test_unique_paths_preserves_order() -> None:
    assert io_helpers._unique_paths(["a", "b", "a", "", "c", "b"]) == ["a", "b", "c"]


def test_as_mapping_and_clean_list_normalize_inputs() -> None:
    mapping = {"a": 1}

    assert io_helpers._as_mapping(mapping) is mapping
    assert io_helpers._as_mapping(["not", "mapping"]) == {}
    assert io_helpers._clean_list([" a ", "", "a", None, "b"]) == ["a", "b"]
    assert io_helpers._clean_list("not-list") == []
