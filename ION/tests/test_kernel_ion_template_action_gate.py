from kernel.ion_template_action_gate import evaluate_template_action_proof


def test_template_action_gate_accepts_context_and_template_proof():
    output = """### CONTEXT PROOF
- ION/REPO_AUTHORITY.md excerpt line sha256 abc

### TEMPLATE ACTION PROOF
template_id: ion.template.autonomous_loop.local_worker.v1
action_id: v101.step_01
result: accepted_state_delta_candidate
touched_paths:
  - ION/05_context/current/LAST_ION_AUTONOMOUS_LOOP_RESULT.json
"""
    result = evaluate_template_action_proof(worker_output=output)
    assert result["accepted"] is True
    assert result["integration_decision"] == "ALLOW_STEWARD_INTEGRATION"


def test_template_action_gate_rejects_missing_template_proof():
    result = evaluate_template_action_proof(worker_output="### CONTEXT PROOF\nread something\n")
    assert result["accepted"] is False
    assert "missing_template_action_proof_heading" in result["findings"]


def test_template_action_gate_accepts_markdown_scalar_variants():
    output = """### CONTEXT PROOF
- path: ION/REPO_AUTHORITY.md
  sha256: abc
  line: L1
  excerpt: authority

### TEMPLATE ACTION PROOF
- **template_id:** ion.template.patch_proposal.v1
- **action_id:** cursor_queue_runner_process_once
- **result:** designed
touched_paths:
  - ION/05_context/current/example.json

### RESULT
bounded cursor-cli proof run
"""
    result = evaluate_template_action_proof(worker_output=output)
    assert result["accepted"] is True
    assert result["template_id"] == "ion.template.patch_proposal.v1"
    assert result["action_id"] == "cursor_queue_runner_process_once"
    assert result["touched_paths"] == ["ION/05_context/current/example.json"]


def test_template_action_gate_rejects_path_traversal():
    output = """### CONTEXT PROOF
- proof

### TEMPLATE ACTION PROOF
template_id: ion.template.autonomous_loop.local_worker.v1
action_id: v101.step_01
result: accepted_state_delta_candidate
touched_paths:
  - ../outside.md
"""
    result = evaluate_template_action_proof(worker_output=output)
    assert result["accepted"] is False
    assert any(finding.startswith("invalid_touched_path") for finding in result["findings"])
