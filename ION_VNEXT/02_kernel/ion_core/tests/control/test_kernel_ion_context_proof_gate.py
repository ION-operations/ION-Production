from kernel.ion_context_proof_gate import (
    evaluate_context_proof_return,
    required_file_paths_from_receipt,
)


def _receipt():
    return {
        "required_context_reads": [
            {"kind": "file", "required": True, "path": "ION/REPO_AUTHORITY.md"},
            {"kind": "file", "required": True, "path": "ION/02_architecture/ION_MOUNT_CONTRACT.md"},
            {"kind": "note", "required": True, "path": "not-a-file"},
            {"kind": "file", "required": False, "path": "optional.md"},
        ]
    }


def test_required_file_paths_from_receipt_keeps_required_file_reads_only():
    assert required_file_paths_from_receipt(_receipt()) == [
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
    ]


def test_context_proof_accepts_required_paths_with_evidence_tokens():
    output = """### CONTEXT PROOF
- ION/REPO_AUTHORITY.md excerpt line sha256 abc
- ION/02_architecture/ION_MOUNT_CONTRACT.md EOF heading observed

### TEMPLATE ACTION PROOF
not evaluated by this gate
"""

    result = evaluate_context_proof_return(receipt=_receipt(), task_output=output)

    assert result["accepted"] is True
    assert result["integration_decision"] == "ALLOW_STEWARD_REVIEW"
    assert result["missing_paths"] == []


def test_context_proof_rejects_missing_initial_heading():
    result = evaluate_context_proof_return(
        receipt=_receipt(),
        task_output="I read ION/REPO_AUTHORITY.md excerpt line sha256 abc",
    )

    assert result["accepted"] is False
    assert "missing_initial_context_proof_heading" in result["findings"]


def test_context_proof_rejects_required_path_without_nearby_evidence():
    receipt = {
        "required_context_reads": [
            {"kind": "file", "required": True, "path": "ION/REPO_AUTHORITY.md"},
        ]
    }
    output = """### CONTEXT PROOF
- ION/REPO_AUTHORITY.md acknowledged
"""

    result = evaluate_context_proof_return(receipt=receipt, task_output=output)

    assert result["accepted"] is False
    assert "missing_read_evidence_near_path:ION/REPO_AUTHORITY.md" in result["findings"]
