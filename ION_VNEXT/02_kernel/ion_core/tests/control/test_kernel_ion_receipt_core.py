import inspect

from kernel.ion_receipt_core import (
    BLOCKED_VERDICT,
    READY_VERDICT,
    attach_receipt_hash,
    build_receipt_record,
    classify_receipt_record,
    stable_receipt_hash,
    validate_receipt_record,
)
import kernel.ion_receipt_core as receipt_core


VALID_HASH = "a" * 64


def _record(**overrides):
    params = {
        "receipt_type": "control_promotion",
        "producer": "codex_cli",
        "subject": "M41 receipt core candidate",
        "claim": "candidate receipt core was selected by M40",
        "source_paths": ["ION_Developement/ION/05_context/current/reports/M40/example.json"],
        "evidence_hashes": {"source": VALID_HASH},
        "created_at": "2026-05-20T14:24:52Z",
    }
    params.update(overrides)
    return build_receipt_record(**params)


def test_receipt_core_builds_valid_candidate_record():
    record = _record()

    errors = validate_receipt_record(record)
    classification = classify_receipt_record(record)

    assert errors == ()
    assert classification["ok"] is True
    assert classification["verdict"] == READY_VERDICT
    assert classification["accepted_state_claim"] is False
    assert classification["production_authority"] is False
    assert classification["live_execution_authority"] is False


def test_receipt_core_hash_is_stable_and_ignores_attached_hash_field():
    record = _record()

    first = stable_receipt_hash(record)
    with_hash = attach_receipt_hash(record)
    second = stable_receipt_hash(with_hash)

    assert len(first) == 64
    assert first == second
    assert with_hash["receipt_hash"] == first


def test_receipt_core_rejects_authority_overclaim():
    record = _record(authority={"production_authority": True})

    classification = classify_receipt_record(record)

    assert classification["ok"] is False
    assert classification["verdict"] == BLOCKED_VERDICT
    assert "production_authority_must_be_false" in classification["errors"]


def test_receipt_core_requires_source_binding():
    record = _record(source_paths=[])

    assert "source_paths_required" in validate_receipt_record(record)


def test_receipt_core_blocks_runtime_or_private_paths():
    runtime_record = _record(source_paths=["ION/05_context/current/ACTIVE_WORK_PACKET.json"])
    private_record = _record(source_paths=["ION_VAULT_LOCAL/token.txt"])
    escape_record = _record(source_paths=["../ION_EXPORTS_LOCAL/out.json"])

    assert "source_paths_include_forbidden_or_runtime_path" in validate_receipt_record(runtime_record)
    assert "source_paths_include_forbidden_or_runtime_path" in validate_receipt_record(private_record)
    assert "source_paths_include_forbidden_or_runtime_path" in validate_receipt_record(escape_record)


def test_receipt_core_has_no_current_state_defaults_or_file_io():
    source = inspect.getsource(receipt_core)

    assert "DEFAULT_REPORT_DIR" not in source
    assert "DEFAULT_RECEIPT_DIR" not in source
    assert ".write_text(" not in source
    assert ".read_text(" not in source
