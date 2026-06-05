from kernel.ion_context_proof_gate import evaluate_context_proof_return


_HASH_A = "a" * 64
_HASH_B = "b" * 64


def _receipt(*paths: str) -> dict:
    return {
        "required_context_reads": [
            {"path": path, "kind": "file", "required": True}
            for path in paths
        ]
    }


def test_context_proof_accepts_strict_labeled_block() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "- path: ION/a.md\n"
            f"  sha256: {_HASH_A}\n"
            "  line: L1\n"
            "  excerpt: alpha\n\n"
            "### TEMPLATE ACTION PROOF\n"
            "ok\n"
        ),
    )
    assert result["accepted"] is True


def test_context_proof_accepts_strict_pipe_table_evidence() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "path | sha256 | line | excerpt\n"
            f"ION/a.md | {_HASH_A} | L1 | alpha\n"
        ),
    )
    assert result["accepted"] is True


def test_context_proof_accepts_compact_pipe_table_evidence_without_line_marker() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "All required context paths were opened directly; receipt line evidence follows.\n"
            "path | hash | excerpt\n"
            f"ION/a.md | {_HASH_A} | authority row excerpt\n"
        ),
    )
    assert result["accepted"] is True


def test_context_proof_accepts_indexed_markdown_table_with_trailing_pipe() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "| # | path | sha256 | line/excerpt |\n"
            "|---|---|---|---|\n"
            f"| 1 | ION/a.md | {_HASH_A} | L1: `{{` |\n"
        ),
    )
    assert result["accepted"] is True


def test_context_proof_accepts_later_evidence_when_path_is_named_first_without_hash() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "work_request_path: ION/a.md\n"
            "Required context path evidence:\n"
            "| # | path | sha256 | line/excerpt |\n"
            "|---|---|---|---|\n"
            f"| 1 | ION/a.md | {_HASH_A} | L1: `{{` |\n"
        ),
    )
    assert result["accepted"] is True


def test_context_proof_rejects_generic_statement() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output="### CONTEXT PROOF\nI read the context files.\n",
    )
    assert result["accepted"] is False
    assert "missing_required_read_path:ION/a.md" in result["findings"]


def test_context_proof_rejects_path_only_without_evidence() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output="### CONTEXT PROOF\n- path: ION/a.md\n",
    )
    assert result["accepted"] is False
    assert "missing_read_evidence_near_path:ION/a.md" in result["findings"]


def test_context_proof_rejects_table_row_with_blank_excerpt() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "path | sha256 | line | excerpt\n"
            f"ION/a.md | {_HASH_A} | L1 | \n"
        ),
    )
    assert result["accepted"] is False
    assert "missing_read_evidence_near_path:ION/a.md" in result["findings"]


def test_context_proof_rejects_missing_required_path() -> None:
    result = evaluate_context_proof_return(
        receipt=_receipt("ION/a.md", "ION/b.md"),
        task_output=(
            "### CONTEXT PROOF\n"
            "- path: ION/a.md\n"
            f"  sha256: {_HASH_A}\n"
            "  line: L1\n"
            "  excerpt: alpha\n"
            "- path: ION/other.md\n"
            f"  sha256: {_HASH_B}\n"
            "  line: L1\n"
            "  excerpt: other\n"
        ),
    )
    assert result["accepted"] is False
    assert "missing_required_read_path:ION/b.md" in result["findings"]
