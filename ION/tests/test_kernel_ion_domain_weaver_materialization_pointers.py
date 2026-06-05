from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

from kernel import ion_domain_weaver_materialization_pointers as pointers


def test_path_row_is_pure_no_write_shape_without_filesystem_claims() -> None:
    row = pointers.shape_domain_weaver_materialization_path_row(
        path="ION/05_context/current/domain_weaver/materialization/PTR.candidate.json",
        path_kind="target_path",
        source_field="target_path",
        reason="candidate pointer target only",
    )

    assert row["schema_id"] == pointers.MATERIALIZATION_POINTER_PATH_ROW_SCHEMA_ID
    assert row["row_kind"] == "domain_weaver_materialization_pointer_path_row"
    assert row["path_kind"] == "target_path"
    assert row["path_probe_performed"] is False
    assert row["exists"] is None
    assert row["sha256"] is None
    assert row["would_create_path"] is False
    assert row["would_write_path"] is False
    assert row["authority"]["materialization_write_authority"] is False
    assert row["authority"]["registry_mutation_authority"] is False
    assert row["authority"]["projection_refresh_authority"] is False


def test_status_row_rejects_ready_status_and_materialization_ready_true_claim() -> None:
    row = pointers.shape_domain_weaver_materialization_status_row(
        pointer_id="dw_mat_ptr_example",
        status="ready",
        summary="caller tried to claim readiness",
        blockers=[],
        materialization_ready=True,
    )

    assert row["schema_id"] == pointers.MATERIALIZATION_POINTER_STATUS_ROW_SCHEMA_ID
    assert row["requested_status"] == "ready"
    assert row["status"] == "blocked_ready_claim_rejected"
    assert row["materialization_ready"] is False
    assert row["materialization_ready_claim_rejected"] is True
    assert row["would_materialize"] is False
    assert row["would_write"] is False
    assert "materialization_ready_true_claim_forbidden" in row["blockers"]
    assert row["authority"]["materialization_ready_claim_authority"] is False
    assert row["authority"]["accepted_state_authority"] is False


def test_pointer_record_is_deterministic_and_dedupes_path_rows() -> None:
    kwargs = {
        "pointer_kind": "promotion materialization",
        "subject_id": "PCKT-DOMAIN-WEAVER-001",
        "source_path": "ION/05_context/current/domain_weaver/source.json",
        "target_path": "ION/05_context/current/domain_weaver/target.candidate.json",
        "evidence_paths": [
            "ION/05_context/current/domain_weaver/evidence.json",
            "ION/05_context/current/domain_weaver/evidence.json",
        ],
        "summary": "candidate pointer only",
    }

    first = pointers.shape_domain_weaver_materialization_pointer(**kwargs)
    second = pointers.shape_domain_weaver_materialization_pointer(**kwargs)

    assert first == second
    assert first["schema_id"] == pointers.MATERIALIZATION_POINTER_SCHEMA_ID
    assert first["row_kind"] == "domain_weaver_materialization_pointer_candidate"
    assert first["pointer_id"].startswith("dw_mat_ptr_")
    assert first["pointer_kind"] == "promotion_materialization"
    assert first["status"] == "candidate"
    assert first["materialization_ready"] is False
    assert first["would_materialize"] is False
    assert first["would_write"] is False
    assert [row["path_kind"] for row in first["path_rows"]] == [
        "target_path",
        "source_path",
        "evidence_path",
    ]
    assert first["path_row_count"] == 3


def test_supplied_path_rows_are_normalized_to_no_write_shape() -> None:
    pointer = pointers.shape_domain_weaver_materialization_pointer(
        pointer_kind="gate",
        target_path="ION/05_context/current/domain_weaver/target.candidate.json",
        path_rows=[
            {
                "path": "ION/05_context/current/domain_weaver/supplied.candidate.json",
                "path_kind": "claimed write proof",
                "source_field": "hostile_path_rows",
                "required": False,
                "reason": "caller tried to smuggle proof",
                "path_probe_performed": True,
                "exists": True,
                "sha256": "not-real",
                "would_create_path": True,
                "would_write_path": True,
                "authority": {
                    "materialization_write_authority": True,
                    "accepted_state_authority": True,
                },
            }
        ],
    )

    supplied = pointer["path_rows"][0]
    assert supplied["path"] == "ION/05_context/current/domain_weaver/supplied.candidate.json"
    assert supplied["path_kind"] == "claimed_write_proof"
    assert supplied["source_field"] == "hostile_path_rows"
    assert supplied["required"] is False
    assert supplied["path_probe_performed"] is False
    assert supplied["exists"] is None
    assert supplied["sha256"] is None
    assert supplied["would_create_path"] is False
    assert supplied["would_write_path"] is False
    assert supplied["authority"]["materialization_write_authority"] is False
    assert supplied["authority"]["accepted_state_authority"] is False


def test_summary_counts_candidate_records_without_moving_state() -> None:
    ready_rejected = pointers.shape_domain_weaver_materialization_pointer(
        pointer_kind="gate",
        target_path="ION/05_context/current/domain_weaver/gate.candidate.json",
        status="materialization_ready",
        materialization_ready=True,
    )
    blocked = pointers.shape_domain_weaver_materialization_pointer(
        pointer_kind="packet",
        target_path="ION/05_context/current/domain_weaver/packet.candidate.json",
        status="candidate",
        blockers=["missing nemesis review"],
    )

    summary = pointers.shape_domain_weaver_materialization_pointer_summary([ready_rejected, blocked])

    assert summary["schema_id"] == pointers.MATERIALIZATION_POINTER_SUMMARY_SCHEMA_ID
    assert summary["pointer_count"] == 2
    assert summary["path_row_count"] == 2
    assert summary["blocked_pointer_count"] == 2
    assert summary["ready_claim_rejected_count"] == 1
    assert summary["status_counts"] == {
        "blocked": 1,
        "blocked_ready_claim_rejected": 1,
    }
    assert summary["materialization_ready"] is False
    assert summary["would_materialize"] is False
    assert summary["would_write"] is False
    assert summary["would_refresh_projection"] is False
    assert summary["authority"]["topology_movement_authority"] is False
    assert summary["authority"]["ui_projection_movement_authority"] is False
    assert summary["authority"]["live_execution_authority"] is False


def test_materialization_pointer_helper_has_no_reverse_or_stateful_imports() -> None:
    sys.modules.pop("kernel.ion_domain_weaver_materialization_pointers", None)
    sys.modules.pop("kernel.ion_domain_weaver", None)

    module = importlib.import_module("kernel.ion_domain_weaver_materialization_pointers")

    assert module.MATERIALIZATION_POINTER_SCHEMA_ID == pointers.MATERIALIZATION_POINTER_SCHEMA_ID
    assert "kernel.ion_domain_weaver" not in sys.modules

    source_path = Path(module.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    observed_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            observed_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            observed_imports.append(node.module or "")

    assert observed_imports == ["__future__", "hashlib", "typing"]
    forbidden_import_fragments = (
        "ion_domain_weaver",
        "queue_runner",
        "dispatcher",
        "operator_action",
        "projection_refresh",
        "registry",
        "topology",
        "cockpit",
        "secret",
        "pathlib",
        "os",
        "subprocess",
    )
    assert not any(
        fragment in imported
        for imported in observed_imports
        for fragment in forbidden_import_fragments
    )
