"""
Tests for PLIx VIF Integration

Validates PLIx witness creation using VIF metadata field.
"""

import pytest
from datetime import datetime, timezone
from packages.apoe.vif_integration_plix import (
    PLIxVIFIntegration,
    create_constraint_replay_witness,
    create_purity_proof_witness,
    create_subdistribution_witness
)
from packages.vif.witness import VIF, ConfidenceBand, TaskCriticality


def test_create_constraint_replay_witness():
    """Test constraint replay witness creation"""
    
    witness = create_constraint_replay_witness(
        constraint_id="con_123",
        constraint_text="available == True",
        variables={"available": True},
        result=True,
        evidence_hash="abc123...",
        purity_proof={
            "ast_hash": "def456...",
            "allowed_operations": ["==", "field_access"],
            "validation_result": True
        },
        snapshot_id="snap_789"
    )
    
    assert isinstance(witness, VIF)
    assert witness.operation_type == "plix_constraint_replay"
    assert "plix_specific" in witness.metadata
    assert witness.metadata["witness_type"] == "constraint_replay"
    
    plix_data = witness.metadata["plix_specific"]
    assert plix_data["constraint_id"] == "con_123"
    assert plix_data["constraint_text"] == "available == True"
    assert plix_data["evaluation_result"] is True


def test_create_purity_proof_witness():
    """Test purity proof witness creation"""
    
    witness = create_purity_proof_witness(
        constraint_id="con_456",
        ast_hash="ast123...",
        allowed_ops=["abs", "max", "=="],
        is_pure=True,
        signature="sig789...",
        snapshot_id="snap_101"
    )
    
    assert isinstance(witness, VIF)
    assert witness.operation_type == "plix_purity_proof"
    assert witness.task_criticality == TaskCriticality.CRITICAL
    assert witness.confidence_band == ConfidenceBand.A
    
    plix_data = witness.metadata["plix_specific"]
    assert plix_data["constraint_id"] == "con_456"
    assert plix_data["validation_result"] is True
    assert "abs" in plix_data["allowed_operations"]


def test_create_subdistribution_witness():
    """Test subdistribution witness creation"""
    
    attempts = [
        {"attempt": 1, "result": None, "error": "Timeout", "probability": 0.3},
        {"attempt": 2, "result": None, "error": "Failed", "probability": 0.2},
        {"attempt": 3, "result": {"success": True}, "error": None, "probability": 0.4}
    ]
    
    witness = create_subdistribution_witness(
        step_id="step_789",
        attempts=attempts,
        result={"success": True},
        probability=0.9,
        monad_valid=True,
        snapshot_id="snap_202"
    )
    
    assert isinstance(witness, VIF)
    assert witness.operation_type == "plix_subdistribution"
    assert witness.confidence_score == 0.9
    assert witness.confidence_band == ConfidenceBand.A
    
    plix_data = witness.metadata["plix_specific"]
    assert plix_data["step_id"] == "step_789"
    assert len(plix_data["attempts"]) == 3
    assert plix_data["total_probability_mass"] == 0.9
    assert plix_data["failure_probability"] == 0.1


def test_extract_plix_metadata():
    """Test extracting PLIx metadata from VIF"""
    
    integration = PLIxVIFIntegration()
    
    witness = create_constraint_replay_witness(
        constraint_id="test",
        constraint_text="x > 0",
        variables={"x": 10},
        result=True,
        evidence_hash="hash",
        purity_proof={},
        snapshot_id="snap"
    )
    
    plix_data = integration.extract_plix_metadata(witness)
    
    assert plix_data is not None
    assert plix_data["constraint_id"] == "test"
    assert plix_data["variables"]["x"] == 10


def test_is_plix_witness():
    """Test PLIx witness detection"""
    
    integration = PLIxVIFIntegration()
    
    # PLIx witness
    plix_witness = create_purity_proof_witness(
        constraint_id="test",
        ast_hash="hash",
        allowed_ops=[],
        is_pure=True,
        signature="sig",
        snapshot_id="snap"
    )
    
    assert integration.is_plix_witness(plix_witness)
    
    # Non-PLIx witness
    regular_witness = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=100,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="out_hash",
        output_tokens=50,
        total_tokens=150,
        task_criticality=TaskCriticality.ROUTINE,
        kappa_threshold=0.70,
        kappa_gate_passed=True,
        created_at=datetime.now(timezone.utc),
        execution_time_ms=100.0,
        operation_type="standard_operation"
    )
    
    assert not integration.is_plix_witness(regular_witness)


def test_get_witness_type():
    """Test getting PLIx witness type"""
    
    integration = PLIxVIFIntegration()
    
    constraint_witness = create_constraint_replay_witness(
        constraint_id="test", constraint_text="x", variables={},
        result=True, evidence_hash="h", purity_proof={}, snapshot_id="s"
    )
    
    assert integration.get_witness_type(constraint_witness) == "constraint_replay"
    
    purity_witness = create_purity_proof_witness(
        constraint_id="test", ast_hash="h", allowed_ops=[],
        is_pure=True, signature="s", snapshot_id="snap"
    )
    
    assert integration.get_witness_type(purity_witness) == "purity_proof"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

