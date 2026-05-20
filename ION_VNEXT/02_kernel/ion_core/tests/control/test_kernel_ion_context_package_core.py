import inspect

from kernel.ion_context_package_core import (
    BLOCKED_VERDICT,
    READY_VERDICT,
    attach_context_package_hash,
    build_context_package_record,
    classify_context_package_record,
    stable_context_package_hash,
    validate_context_package_record,
)
import kernel.ion_context_package_core as context_package_core


VALID_HASH = "b" * 64


def _record(**overrides):
    params = {
        "package_id": "governance.system_cartography",
        "context_kind": "domain_context_package",
        "domain": "governance.system_cartography",
        "summary": "Candidate context package for bounded governance cartography.",
        "read_order": [
            "ION_VNEXT/00_front_door/AI_START_HERE.md",
            "ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml",
        ],
        "source_receipts": [
            "ION_Developement/ION/05_context/current/reports/ION_ORGANIZATION_MILESTONE_041_VNEXT_RECEIPT_CORE_LANDING_20260520T205023Z/ION_VNEXT_M41_RECEIPT_CORE_RECEIPT.json"
        ],
        "source_hashes": {"m41_receipt": VALID_HASH},
        "created_at": "2026-05-20T22:50:00Z",
    }
    params.update(overrides)
    return build_context_package_record(**params)


def test_context_package_core_builds_valid_source_bound_record():
    record = _record()

    errors = validate_context_package_record(record)
    classification = classify_context_package_record(record)

    assert errors == ()
    assert classification["ok"] is True
    assert classification["verdict"] == READY_VERDICT
    assert classification["accepted_state_claim"] is False
    assert classification["production_authority"] is False
    assert classification["live_execution_authority"] is False


def test_context_package_core_hash_is_stable_and_ignores_attached_hash_field():
    record = _record()

    first = stable_context_package_hash(record)
    with_hash = attach_context_package_hash(record)
    second = stable_context_package_hash(with_hash)

    assert len(first) == 64
    assert first == second
    assert with_hash["context_package_hash"] == first


def test_context_package_core_requires_source_receipts_and_hashes():
    no_receipts = _record(source_receipts=[])
    no_hashes = _record(source_hashes={})

    assert "source_receipts_required" in validate_context_package_record(no_receipts)
    assert "source_hashes_required" in validate_context_package_record(no_hashes)


def test_context_package_core_rejects_authority_overclaim():
    record = _record(authority={"accepted_state_claim": True})

    classification = classify_context_package_record(record)

    assert classification["ok"] is False
    assert classification["verdict"] == BLOCKED_VERDICT
    assert "accepted_state_claim_must_be_false" in classification["errors"]


def test_context_package_core_blocks_runtime_private_queue_and_escape_paths():
    runtime_record = _record(read_order=["ION/05_context/current/ACTIVE_WORK_PACKET.json"])
    private_record = _record(source_receipts=["ION_VAULT_LOCAL/token.txt"])
    queue_record = _record(read_order=["ION_VNEXT/05_runtime/queues/inbox.json"])
    escape_record = _record(read_order=["../ION_EXPORTS_LOCAL/out.json"])

    assert "read_order_include_forbidden_or_runtime_path" in validate_context_package_record(runtime_record)
    assert "source_receipts_include_forbidden_or_runtime_path" in validate_context_package_record(private_record)
    assert "read_order_include_forbidden_or_runtime_path" in validate_context_package_record(queue_record)
    assert "read_order_include_forbidden_or_runtime_path" in validate_context_package_record(escape_record)


def test_context_package_core_has_no_file_io_or_active_defaults():
    source = inspect.getsource(context_package_core)

    assert "DEFAULT_REPORT_DIR" not in source
    assert "DEFAULT_CONTEXT_PACKAGE_DIR" not in source
    assert ".write_text(" not in source
    assert ".read_text(" not in source
    assert "rglob(" not in source
