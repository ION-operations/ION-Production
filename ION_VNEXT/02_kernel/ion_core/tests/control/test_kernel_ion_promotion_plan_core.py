from kernel.ion_promotion_plan_core import (
    attach_promotion_plan_hash,
    build_promotion_item_from_source_pool_classification,
    build_promotion_plan_item,
    build_promotion_plan_record,
    classify_promotion_plan_record,
    stable_promotion_plan_hash,
    validate_promotion_plan_item,
    validate_promotion_plan_record,
)
from kernel.ion_source_pool_audit_core import build_source_pool_record, classify_source_pool_record


DIGEST = "a" * 64
POOL_DIGEST = "b" * 64
RECEIPT = "ION_Developement/ION/05_context/current/reports/source_pool_review_receipt.json"


def _valid_promote_item():
    return build_promotion_plan_item(
        item_id="path_authority",
        source_pool_id="kernel_controls",
        source_path="ION_Developement/ION/04_packages/kernel/ion_path_authority.py",
        target_path="ION_VNEXT/02_kernel/ion_core/src/kernel/ion_path_authority.py",
        decision="PROMOTE_ACTIVE",
        required_receipts=[RECEIPT],
        validation_obligations=[
            "source_hash_verified",
            "target_path_authorized",
            "tests_or_validation_defined",
        ],
        rollback_obligations=["remove_target_file_before_commit_if_validation_fails"],
        approval_gates=["operator_approval"],
        source_hashes={"ION_Developement/ION/04_packages/kernel/ion_path_authority.py": DIGEST},
        source_pool_hash=POOL_DIGEST,
    )


def test_promotion_plan_record_is_hashable_and_ready():
    item = _valid_promote_item()
    plan = build_promotion_plan_record(
        plan_id="m47_kernel_promote",
        planner="codex",
        source_pool_id="kernel_controls",
        target_family="kernel",
        summary="Promote one audited kernel control.",
        items=[item],
        required_receipts=[RECEIPT],
        created_at="2026-05-21T00:00:00Z",
    )

    assert validate_promotion_plan_item(item) == ()
    assert validate_promotion_plan_record(plan) == ()
    assert stable_promotion_plan_hash(plan) == stable_promotion_plan_hash(attach_promotion_plan_hash(plan))

    classification = classify_promotion_plan_record(plan)
    assert classification["verdict"] == "ION_PROMOTION_PLAN_CORE_READY"
    assert classification["direct_file_operations_performed"] is False
    assert classification["source_pool_bulk_copy_allowed"] is False


def test_plan_item_can_be_built_from_source_pool_classification():
    source_pool = build_source_pool_record(
        source_pool_id="kernel_controls",
        family="kernel",
        source_pool_class="ACTIVE_KERNEL_SOURCE_POOL",
        canonical_target="02_kernel/ion_core",
        source_paths=["ION_Developement/ION/04_packages/kernel/ion_path_authority.py"],
        evidence_hashes={"ION_Developement/ION/04_packages/kernel/ion_path_authority.py": DIGEST},
        created_at="2026-05-21T00:00:00Z",
    )
    classification = classify_source_pool_record(source_pool)

    item = build_promotion_item_from_source_pool_classification(
        item_id="path_authority",
        source_pool_id="kernel_controls",
        source_path="ION_Developement/ION/04_packages/kernel/ion_path_authority.py",
        target_path="ION_VNEXT/02_kernel/ion_core/src/kernel/ion_path_authority.py",
        classification=classification,
        required_receipts=[RECEIPT],
        validation_obligations=[
            "source_hash_verified",
            "target_path_authorized",
            "tests_or_validation_defined",
        ],
        rollback_obligations=["remove_target_file_before_commit_if_validation_fails"],
        approval_gates=["operator_approval"],
        source_hashes={"ION_Developement/ION/04_packages/kernel/ion_path_authority.py": DIGEST},
    )

    assert item.decision == "PROMOTE_ACTIVE"
    assert item.source_pool_hash == classification["source_pool_hash"]
    assert validate_promotion_plan_item(item) == ()


def test_direct_promotion_requires_validation_receipt_rollback_approval_and_hash():
    item = build_promotion_plan_item(
        item_id="incomplete",
        source_pool_id="kernel_controls",
        source_path="ION_Developement/ION/04_packages/kernel/ion_path_authority.py",
        target_path="ION_VNEXT/02_kernel/ion_core/src/kernel/ion_path_authority.py",
        decision="PROMOTE_ACTIVE",
        required_receipts=[],
        validation_obligations=["source_hash_verified"],
        rollback_obligations=[],
        approval_gates=[],
    )

    errors = validate_promotion_plan_item(item)

    assert "direct_promotion_missing_required_validations" in errors
    assert "direct_promotion_missing_approval_gate" in errors
    assert "direct_promotion_missing_rollback_obligations" in errors
    assert "direct_promotion_missing_required_receipts" in errors
    assert "direct_promotion_missing_source_hashes" in errors


def test_risky_source_pool_decision_cannot_be_direct_promotion_plan():
    item = build_promotion_plan_item(
        item_id="runtime_file",
        source_pool_id="runtime",
        source_path="ION_Developement/ION/05_context/current/ACTIVE_WORK_PACKET.json",
        target_path="ION_VNEXT/05_runtime/ACTIVE_WORK_PACKET.json",
        decision="PROMOTE_ACTIVE",
        required_receipts=[RECEIPT],
        validation_obligations=[
            "source_hash_verified",
            "target_path_authorized",
            "tests_or_validation_defined",
        ],
        rollback_obligations=["remove_target_file_before_commit_if_validation_fails"],
        approval_gates=["operator_approval"],
        risk_flags=["runtime_current_state_present"],
        source_hashes={"ION_Developement/ION/05_context/current/ACTIVE_WORK_PACKET.json": DIGEST},
    )

    errors = validate_promotion_plan_item(item)

    assert "source_path_invalid_or_forbidden" in errors
    assert "target_path_required_or_invalid" in errors
    assert "direct_promotion_requires_risk_closure" in errors


def test_private_exclude_is_presence_only_not_promotion():
    item = build_promotion_plan_item(
        item_id="vault_presence",
        source_pool_id="private",
        source_path="ION_VAULT_LOCAL",
        decision="PRIVATE_EXCLUDE",
        required_receipts=[RECEIPT],
        validation_obligations=["presence_only_no_value_inspection"],
        rollback_obligations=[],
        approval_gates=[],
        risk_flags=["private_path_present"],
        notes=["Presence-only private boundary exclusion."],
    )

    assert validate_promotion_plan_item(item) == ()


def test_plan_blocks_duplicate_item_ids_and_authority_claims():
    item = _valid_promote_item()
    plan = build_promotion_plan_record(
        plan_id="bad",
        planner="codex",
        source_pool_id="kernel_controls",
        target_family="kernel",
        summary="Bad duplicate.",
        items=[item, item],
        authority={"accepted_state_claim": True},
        created_at="2026-05-21T00:00:00Z",
    )

    errors = validate_promotion_plan_record(plan)

    assert "item_ids_must_be_unique" in errors
    assert "accepted_state_claim_must_be_false" in errors


def test_candidate_module_has_no_file_copy_move_delete_behavior():
    source = __import__("kernel.ion_promotion_plan_core", fromlist=["__file__"]).__loader__.get_source(
        "kernel.ion_promotion_plan_core"
    )

    forbidden = (
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "rglob(",
        "iterdir(",
        "shutil",
        "subprocess",
        "os.",
        ".unlink(",
        ".rename(",
        "remove(",
        "rmdir(",
    )
    assert source is not None
    assert not any(token in source for token in forbidden)
