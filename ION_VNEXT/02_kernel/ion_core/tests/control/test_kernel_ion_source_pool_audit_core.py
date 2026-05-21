from kernel.ion_source_pool_audit_core import (
    attach_source_pool_hash,
    build_source_pool_record,
    classify_source_pool_record,
    normalize_decision,
    stable_source_pool_hash,
    source_pool_to_dict,
    validate_source_pool_record,
)


DIGEST = "a" * 64


def test_curated_kernel_source_pool_record_is_hashable_and_ready():
    record = build_source_pool_record(
        source_pool_id="kernel_controls",
        family="kernel",
        source_pool_class="ACTIVE_KERNEL_SOURCE_POOL",
        canonical_target="02_kernel/ion_core",
        source_paths=["ION_Developement/ION/04_packages/kernel/ion_path_authority.py"],
        evidence_hashes={"ION_Developement/ION/04_packages/kernel/ion_path_authority.py": DIGEST},
        observed_counts={"files": 1, "tests": 1},
        created_at="2026-05-21T00:00:00Z",
    )

    as_dict = source_pool_to_dict(record)
    assert as_dict["default_decision"] == "PROMOTE_ACTIVE"
    assert as_dict["authority"]["accepted_state_claim"] is False
    assert validate_source_pool_record(record) == ()
    assert stable_source_pool_hash(record) == stable_source_pool_hash(as_dict)

    attached = attach_source_pool_hash(record)
    assert attached["source_pool_hash"] == stable_source_pool_hash(record)
    assert classify_source_pool_record(record)["verdict"] == "ION_SOURCE_POOL_AUDIT_CORE_READY"


def test_needs_routed_source_pool_routes_work_without_source_promotion():
    record = build_source_pool_record(
        source_pool_id="needs_routed",
        family="work",
        source_pool_class="WORK_INBOX_SOURCE_POOL",
        canonical_target="07_work/inbox",
        source_paths=["Needs_Routed/workpackets"],
        created_at="2026-05-21T00:00:00Z",
    )

    classification = classify_source_pool_record(record)

    assert classification["ok"] is True
    assert classification["recommended_decision"] == "ROUTE_WORK_ITEM"
    assert classification["direct_bulk_copy_allowed"] is False


def test_private_source_pool_is_presence_only_private_exclude():
    record = build_source_pool_record(
        source_pool_id="vault_presence",
        family="private",
        source_pool_class="PRIVATE_EXCLUDED_POOL",
        canonical_target="99_private/vault_local",
        source_paths=["ION_VAULT_LOCAL"],
        default_decision="PRIVATE_EXCLUDE",
        created_at="2026-05-21T00:00:00Z",
    )

    classification = classify_source_pool_record(record)

    assert validate_source_pool_record(record) == ()
    assert classification["recommended_decision"] == "PRIVATE_EXCLUDE"
    assert "private_path_present" in classification["risk_flags"]


def test_runtime_current_state_blocks_direct_promotion():
    record = build_source_pool_record(
        source_pool_id="active_runtime",
        family="runtime",
        source_pool_class="UNKNOWN_SOURCE_POOL",
        canonical_target="05_runtime",
        source_paths=["ION_Developement/ION/05_context/current/ACTIVE_WORK_PACKET.json"],
        default_decision="PROMOTE_ACTIVE",
        created_at="2026-05-21T00:00:00Z",
    )

    classification = classify_source_pool_record(record)

    assert classification["ok"] is False
    assert classification["recommended_decision"] == "BLOCKED_NEEDS_HUMAN"
    assert "direct_promotion_requires_risk_closure" in classification["errors"]
    assert "runtime_current_state_present" in classification["risk_flags"]


def test_queue_or_ledger_paths_are_forbidden():
    record = build_source_pool_record(
        source_pool_id="queue_source",
        family="runtime",
        source_pool_class="UNKNOWN_SOURCE_POOL",
        canonical_target="05_runtime",
        source_paths=["ION_Developement/ION/05_context/current/queues/pending.json"],
        default_decision="BLOCKED_NEEDS_HUMAN",
        created_at="2026-05-21T00:00:00Z",
    )

    errors = validate_source_pool_record(record)

    assert "active_queue_or_ledger_forbidden" in errors


def test_bad_path_shapes_and_authority_claims_block():
    record = build_source_pool_record(
        source_pool_id="bad",
        family="kernel",
        source_pool_class="ACTIVE_KERNEL_SOURCE_POOL",
        canonical_target="02_kernel/ion_core",
        source_paths=["../outside.py"],
        authority={"production_authority": True},
        created_at="2026-05-21T00:00:00Z",
    )

    errors = validate_source_pool_record(record)

    assert "source_paths_include_forbidden_shape" in errors
    assert "production_authority_must_be_false" in errors


def test_m26_decision_aliases_normalize_to_vnext_canonical_decisions():
    assert normalize_decision("MERGE") == "MERGE_INTO_CANON"
    assert normalize_decision("REGENERATE") == "REGENERATE_FROM_SOURCE"
    assert normalize_decision("ROUTE_NOT_PROMOTE_AS_SOURCE") == "ROUTE_WORK_ITEM"
    assert normalize_decision("DO_NOT_UNPACK_INTO_VNEXT") == "ARCHIVE_EVIDENCE"


def test_candidate_module_does_not_perform_filesystem_scans():
    source = __import__("kernel.ion_source_pool_audit_core", fromlist=["__file__"]).__loader__.get_source(
        "kernel.ion_source_pool_audit_core"
    )

    forbidden = ("Path(", "open(", "read_text(", "write_text(", "rglob(", "iterdir(", "os.")
    assert source is not None
    assert not any(token in source for token in forbidden)
