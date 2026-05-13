"""
Test confidence_gated_controls VIF/APOE Integration

Verifies that confidence_gated_controls correctly:
- Validates confidence via VIF
- Checks APOE orchestration gates
- Creates VIF witnesses
- Works without VIF/APOE (fail-soft)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MockVIFClient:
    """Mock VIF client for testing"""
    def validate_confidence(self, confidence_score: float, change_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock confidence validation"""
        if confidence_score >= 0.70:
            return {
                "kappa_gate_passed": True,
                "reason": "Confidence sufficient"
            }
        else:
            return {
                "kappa_gate_passed": False,
                "reason": "Confidence below threshold"
            }
    
    def create_witness(self, change_id: str, context: Dict[str, Any]) -> str:
        """Mock witness creation"""
        return f"witness_{change_id}"


@dataclass
class MockAPOEClient:
    """Mock APOE client for testing"""
    def check_gate_status(self, plan_id: str, change_id: str) -> Dict[str, Any]:
        """Mock gate status check"""
        # Simulate gate check
        if plan_id and change_id:
            return {
                "passed": True,
                "reason": "Gate passed"
            }
        return {
            "passed": False,
            "reason": "No active plan"
        }


class TestConfidenceGatedVIFAPOEIntegration:
    """Test suite for confidence_gated_controls VIF/APOE integration"""
    
    @pytest.fixture
    def mock_vif_client(self):
        """Create mock VIF client"""
        return MockVIFClient()
    
    @pytest.fixture
    def mock_apoe_client(self):
        """Create mock APOE client"""
        return MockAPOEClient()
    
    @pytest.fixture
    def confidence_gated_controls(self, mock_vif_client, mock_apoe_client):
        """Create confidence_gated_controls instance with mocked clients"""
        # Import the actual class
        from daemon_rag_system.ah_protocol.confidence_gated_controls import ConfidenceGatedControls
        
        # Create instance with mocked clients
        controls = ConfidenceGatedControls(
            config_path="test_config.json",
            vif_client=mock_vif_client,
            apoe_client=mock_apoe_client
        )
        return controls
    
    def test_vif_confidence_validation_high_confidence(self, confidence_gated_controls, mock_vif_client):
        """Test VIF confidence validation with high confidence"""
        confidence_score = 0.85
        change_id = "test_change_1"
        context = {"task": "test_task"}
        
        # Call validation method
        result, message = confidence_gated_controls._validate_confidence_via_vif(
            confidence_score, change_id, context
        )
        
        # Verify result
        assert result is True
        assert "validated" in message.lower() or "passed" in message.lower()
    
    def test_vif_confidence_validation_low_confidence(self, confidence_gated_controls, mock_vif_client):
        """Test VIF confidence validation with low confidence"""
        confidence_score = 0.60  # Below threshold
        change_id = "test_change_2"
        context = {"task": "test_task"}
        
        # Call validation method
        result, message = confidence_gated_controls._validate_confidence_via_vif(
            confidence_score, change_id, context
        )
        
        # Verify result (should fail)
        assert result is False
        assert "failed" in message.lower() or "threshold" in message.lower()
    
    def test_vif_confidence_validation_no_client(self):
        """Test VIF confidence validation without VIF client (fail-soft)"""
        from daemon_rag_system.ah_protocol.confidence_gated_controls import ConfidenceGatedControls
        
        controls = ConfidenceGatedControls(
            config_path="test_config.json",
            vif_client=None,  # No VIF client
            apoe_client=None
        )
        
        confidence_score = 0.85
        change_id = "test_change_3"
        context = {"task": "test_task"}
        
        # Should not raise exception (fail-soft)
        result, message = controls._validate_confidence_via_vif(
            confidence_score, change_id, context
        )
        
        # Should return True with skip message
        assert result is True
        assert "not available" in message.lower() or "skipping" in message.lower()
    
    def test_apoe_orchestration_gate_check(self, confidence_gated_controls, mock_apoe_client):
        """Test APOE orchestration gate check"""
        # Import ChangeRequest from the module
        import sys
        import importlib
        module = importlib.import_module('daemon_rag_system.ah_protocol.confidence_gated_controls')
        ChangeRequest = getattr(module, 'ChangeRequest', None)
        
        if ChangeRequest is None:
            # If ChangeRequest doesn't exist, create a simple mock
            from dataclasses import dataclass
            @dataclass
            class ChangeRequest:
                id: str
                description: str
                confidence: float
        
        change_request = ChangeRequest(
            id="test_change_4",
            description="Test change",
            confidence=0.80
        )
        context = {
            "active_apoe_plan_id": "test_plan_1"
        }
        
        # Call gate check method
        result, message = confidence_gated_controls._check_apoe_orchestration_gate(
            change_request, context
        )
        
        # Verify result
        assert result is True
        assert "passed" in message.lower() or "gate" in message.lower()
    
    def test_apoe_orchestration_gate_no_plan(self, confidence_gated_controls, mock_apoe_client):
        """Test APOE orchestration gate check without active plan"""
        # Use same ChangeRequest import pattern
        from dataclasses import dataclass
        @dataclass
        class ChangeRequest:
            id: str
            description: str
            confidence: float
        
        change_request = ChangeRequest(
            id="test_change_5",
            description="Test change",
            confidence=0.80
        )
        context = {}  # No active plan
        
        # Call gate check method
        result, message = confidence_gated_controls._check_apoe_orchestration_gate(
            change_request, context
        )
        
        # Should pass (no plan to check against)
        assert result is True
        assert "no active" in message.lower() or "no plan" in message.lower()
    
    def test_apoe_orchestration_gate_no_client(self):
        """Test APOE orchestration gate check without APOE client (fail-soft)"""
        from daemon_rag_system.ah_protocol.confidence_gated_controls import ConfidenceGatedControls
        from dataclasses import dataclass
        @dataclass
        class ChangeRequest:
            id: str
            description: str
            confidence: float
        
        controls = ConfidenceGatedControls(
            config_path="test_config.json",
            vif_client=None,
            apoe_client=None  # No APOE client
        )
        
        change_request = ChangeRequest(
            id="test_change_6",
            description="Test change",
            confidence=0.80
        )
        context = {"active_apoe_plan_id": "test_plan_1"}
        
        # Should not raise exception (fail-soft)
        result, message = controls._check_apoe_orchestration_gate(
            change_request, context
        )
        
        # Should return True with skip message
        assert result is True
        assert "not available" in message.lower() or "skipping" in message.lower()
    
    def test_vif_witness_creation(self, confidence_gated_controls, mock_vif_client):
        """Test VIF witness creation"""
        change_id = "test_change_7"
        context = {"task": "test_task", "details": "test_details"}
        
        # Call witness creation method
        witness = confidence_gated_controls._create_vif_witness(change_id, context)
        
        # Verify witness created
        assert witness is not None
        assert isinstance(witness, str)
        assert len(witness) > 0
    
    def test_integrated_validation_flow(self, confidence_gated_controls, mock_vif_client, mock_apoe_client):
        """Test complete validation flow with VIF and APOE"""
        from dataclasses import dataclass
        @dataclass
        class ChangeRequest:
            id: str
            description: str
            confidence: float
        
        change_request = ChangeRequest(
            id="test_change_8",
            description="Test change",
            confidence=0.85  # High confidence
        )
        context = {
            "active_apoe_plan_id": "test_plan_1",
            "task": "test_task"
        }
        
        # Call validate_change (which uses both VIF and APOE)
        # This would call the actual validate_change method
        # For now, we test the individual components
        
        # Test VIF validation
        vif_result, vif_message = confidence_gated_controls._validate_confidence_via_vif(
            change_request.confidence, change_request.id, context
        )
        assert vif_result is True
        
        # Test APOE gate check
        apoe_result, apoe_message = confidence_gated_controls._check_apoe_orchestration_gate(
            change_request, context
        )
        assert apoe_result is True


class TestConfidenceGatedVIFAPOEIntegrationManual:
    """Manual test cases for confidence_gated_controls VIF/APOE integration"""
    
    def test_manual_vif_validation(self):
        """Manual test: Verify VIF validation works with real VIF client"""
        # Steps:
        # 1. Create confidence_gated_controls with real VIF client
        # 2. Validate change with confidence 0.85
        # 3. Verify VIF validates correctly
        # 4. Validate change with confidence 0.60
        # 5. Verify VIF rejects (below threshold)
        pass
    
    def test_manual_apoe_gate_check(self):
        """Manual test: Verify APOE gate check works with real APOE client"""
        # Steps:
        # 1. Create confidence_gated_controls with real APOE client
        # 2. Create change request with active plan
        # 3. Verify gate check works
        # 4. Test with no active plan
        # 5. Verify graceful handling
        pass
    
    def test_manual_fail_soft_behavior(self):
        """Manual test: Verify system works without VIF/APOE"""
        # Steps:
        # 1. Create confidence_gated_controls without VIF/APOE clients
        # 2. Validate changes
        # 3. Verify no errors (fail-soft)
        # 4. Verify validation still works (using config-based gates)
        pass

